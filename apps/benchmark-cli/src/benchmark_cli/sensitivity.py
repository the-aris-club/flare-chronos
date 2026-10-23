"""How far the hand-set effort constants move the published conclusions.

Three constants turn deduplicated episode counts into the harmonized count:
the MODIS-only sub-pixel omission factor, the per-extra-VIIRS-stream overlap
gain, and the effective observation effort Omega. None is fitted. This module
holds the single formula that uses them and reports how a relative change in
each one shifts the harmonized change across the MODIS-only -> multi-sensor
transition, which is where an artificial step would show up.
"""

from __future__ import annotations

from typing import Any

# ponytail: none of these three is fitted or sourced. They are tuned so the
# MODIS-only and multi-sensor eras meet, which is why sensor_invariance_ratio in
# the results artifact is the measurement that matters. Derive them from the
# archive (overpass counts per sensor-year) before leaning on any conclusion.
SUBPIXEL_OMISSION_FACTOR = {"mekong": 3.65, "amazon": 2.55}
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
