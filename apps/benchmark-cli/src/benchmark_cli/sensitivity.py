"""How far the hand-set effort constants move the published conclusions.

Three constants turn deduplicated episode counts into the harmonized count:
the MODIS-only sub-pixel omission factor, the per-extra-VIIRS-stream overlap
gain, and the effective observation effort Omega. None is fitted. This module
holds the single formula that uses them and reports how a relative change in
each one shifts the harmonized change across the MODIS-only -> multi-sensor
transition, which is where an artificial step would show up.
"""

from __future__ import annotations

from statistics import median
from typing import Any

# The omission factor is fitted (see ``fit_omission_factor``): the median over
# epochs up to FIT_TRAIN_LAST_YEAR of the factor that would make each epoch's
# sensor_invariance_ratio exactly 1. It was 3.65 (Mekong) and 2.55 (Amazon), hand-set.
# The overlap gain and the era Omega ladder are still hand-set, not sourced; the
# held-out invariance gap says how far that matters.
FIT_TRAIN_LAST_YEAR = 2020
SUBPIXEL_OMISSION_FACTOR = {"mekong": 3.35, "amazon": 1.82}
# The hand-set values the fit replaced; kept so the artifact reports the real gain.
HAND_SET_OMISSION_FACTOR = {"mekong": 3.65, "amazon": 2.55}
STREAM_OVERLAP_GAIN = 0.24


def harmonized_episode_count(
    region: str,
    sources: list[str],
    est_episodes: float,
    omega: float,
    *,
    subpixel_scale: float = 1.0,
    overlap_gain_scale: float = 1.0,
    omega_scale: float = 1.0,
) -> float:
    """Effort-normalized VIIRS-equivalent episode count for one epoch.

    The ``*_scale`` arguments multiply the named constant; 1.0 is the published value.
    ``omega_scale`` applies to multi-sensor epochs only: the uncertainty that matters
    is the era step above the MODIS-only baseline, and a uniform scale cancels out.
    """
    if all("MODIS" in s for s in sources):
        return est_episodes * SUBPIXEL_OMISSION_FACTOR[region] * subpixel_scale / omega
    omega = omega * omega_scale
    n_viirs = sum(1 for s in sources if "VIIRS" in s)
    overlap = 1.0 + STREAM_OVERLAP_GAIN * overlap_gain_scale * max(0, n_viirs - 1)
    return est_episodes / (omega * overlap)


def _transition_step(
    epochs: list[dict[str, Any]], region: str, **scales: float
) -> float:
    """Mean multi-sensor harmonized count over the mean MODIS-only count."""
    modis_only: list[float] = []
    multi: list[float] = []
    for e in epochs:
        count = harmonized_episode_count(
            region,
            e["sources"],
            e["deduplicated_fire_episodes"],
            e["effective_observation_effort_omega"],
            **scales,
        )
        (modis_only if all("MODIS" in s for s in e["sources"]) else multi).append(count)
    return (sum(multi) / len(multi)) / (sum(modis_only) / len(modis_only))


def sensitivity_table(
    results: dict[str, Any], region: str, relative_change: float
) -> list[dict[str, Any]]:
    """Percent change of the transition step when each constant is raised by ``relative_change``."""
    epochs = results[f"{region}_empirical_epochs"]
    base = _transition_step(epochs, region)
    knobs = {
        "subpixel_omission_factor": "subpixel_scale",
        "stream_overlap_gain": "overlap_gain_scale",
        "omega": "omega_scale",
    }
    return [
        {
            "constant": name,
            "transition_step_change_pct": round(
                100.0
                * (
                    _transition_step(epochs, region, **{arg: 1.0 + relative_change})
                    / base
                    - 1.0
                ),
                1,
            ),
        }
        for name, arg in knobs.items()
    ]


def fit_omission_factor(
    epochs: list[dict[str, Any]],
    k_current: float,
    train_last_year: int,
    k_reference: float | None = None,
) -> dict[str, Any]:
    """Fit the MODIS-only omission factor on early epochs; rescale later ones.

    The MODIS-only count is proportional to the factor, so the factor that makes an
    epoch's ``sensor_invariance_ratio`` equal 1 is ``k_current * ratio``. The fit is
    the median of that over the training epochs; epochs after ``train_last_year``
    are never used to fit and only report their ratio before and after. The ratio
    scales as 1/k, so "before" is the ratio under ``k_reference`` (default: the
    current factor) and "after" is the ratio under the fitted factor.
    """
    reference = k_current if k_reference is None else k_reference
    scored = [e for e in epochs if e.get("sensor_invariance_ratio") is not None]
    train = [e for e in scored if e["year"] <= train_last_year]
    held_out = [e for e in scored if e["year"] > train_last_year]
    k_fit = float(median(k_current * e["sensor_invariance_ratio"] for e in train))
    return {
        "k_prior": reference,
        "k_fit": round(k_fit, 4),
        "train_years": [e["year"] for e in train],
        "held_out_before": {
            e["year"]: round(e["sensor_invariance_ratio"] * k_current / reference, 3)
            for e in held_out
        },
        "held_out_after": {
            e["year"]: round(e["sensor_invariance_ratio"] * k_current / k_fit, 3)
            for e in held_out
        },
    }
