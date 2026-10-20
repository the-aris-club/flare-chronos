"""Harmonized Burning Activity Calendar & Phenological Anomaly Engine.

Constructs the 26-year (2000-2026) x 73-Pentad Harmonized Burning Activity Calendar,
computing:
- Harmonized Fire Density (HFD, episodes / 100 km^2 / day)
- Harmonized Radiative Flux (HRF, MW / km^2)
- Standardized Fire Anomaly Index (SFAI, robust seasonal Z-score per Pentad)
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np

from .deduplication import compute_effective_observation_effort
from .domain import AnomalyTier, BurningCalendarCell, FireEpisode


def day_of_year_to_pentad(doy: int) -> int:
    """Map day-of-year (1..366) to standard 5-day climatological Pentad (1..73)."""
    return min(73, max(1, ((doy - 1) // 5) + 1))


def pentad_to_doy_range(pentad: int) -> tuple[int, int]:
    """Return inclusive (doy_start, doy_end) for a Pentad in 1..73."""
    start = (pentad - 1) * 5 + 1
    end = 365 if pentad == 73 else pentad * 5
    return start, end


def classify_sfai_tier(sfai: float) -> AnomalyTier:
    """Classify Standardized Fire Anomaly Index (SFAI Z-score) into operational risk tiers."""
    if sfai < -0.5:
        return AnomalyTier.QUIET
    if sfai < 1.0:
        return AnomalyTier.BASELINE
    if sfai < 1.75:
        return AnomalyTier.ELEVATED
    if sfai < 2.5:
        return AnomalyTier.SEVERE
    return AnomalyTier.CRISIS


def build_burning_activity_calendar(
    episodes: list[FireEpisode],
    aoi_area_km2: float,
    mean_latitude_deg: float = 16.0,
) -> list[BurningCalendarCell]:
    """Aggregate deduplicated Fire Episodes into a Year x Pentad Burning Activity Calendar."""
    if not episodes:
        return []

    by_yp: dict[tuple[int, int], list[FireEpisode]] = defaultdict(list)
    years_present = sorted({ep.start_utc.year for ep in episodes})
    pentads_present = sorted(
        {day_of_year_to_pentad(ep.start_utc.timetuple().tm_yday) for ep in episodes}
    )

    for ep in episodes:
        yr = ep.start_utc.year
        pt = day_of_year_to_pentad(ep.start_utc.timetuple().tm_yday)
        by_yp[(yr, pt)].append(ep)

    # First pass: compute HFD and HRF per (year, pentad)
    prelim: dict[tuple[int, int], dict[str, float]] = {}
    by_pentad_hrf: dict[int, list[float]] = defaultdict(list)

    for yr in years_present:
        omega = compute_effective_observation_effort(yr, mean_latitude_deg)
        for pt in pentads_present:
            eps = by_yp.get((yr, pt), [])
            raw_det_count = sum(e.raw_detection_count for e in eps)
            ep_count = len(eps)
            harm_ep_sum = sum(e.effort_normalized_episode_count for e in eps)
            harm_frp_sum = sum(
                e.harmonized_frp_mw / e.effective_observation_effort_omega for e in eps
            )
            raw_frp_sum = sum(e.raw_sum_frp_mw for e in eps)

            # 5 days per Pentad; HFD is episodes per 100 km^2 per day
            hfd = (harm_ep_sum / (5.0 * max(1.0, aoi_area_km2))) * 100.0
            hrf = harm_frp_sum / max(1.0, aoi_area_km2)
            raw_frp_density = raw_frp_sum / max(1.0, aoi_area_km2)

            prelim[(yr, pt)] = {
                "raw_det_count": float(raw_det_count),
                "ep_count": float(ep_count),
                "omega": omega,
                "hfd": hfd,
                "hrf": hrf,
                "raw_frp_density": raw_frp_density,
            }
            by_pentad_hrf[pt].append(hrf)

    # Second pass: compute seasonal baseline statistics (median & robust sigma per Pentad)
    pentad_stats: dict[int, tuple[float, float]] = {}
    for pt, vals in by_pentad_hrf.items():
        arr = np.array(vals, dtype=float)
        med = float(np.median(arr))
        mad = float(np.median(np.abs(arr - med)))
        std = float(np.std(arr))
        robust_sigma = max(1e-4, 0.65 * (1.4826 * mad) + 0.35 * std)
        pentad_stats[pt] = (med, robust_sigma)

    cells: list[BurningCalendarCell] = []
    for (yr, pt), metrics in sorted(prelim.items()):
        doy_s, doy_e = pentad_to_doy_range(pt)
        med, sigma = pentad_stats[pt]
        sfai = (metrics["hrf"] - med) / sigma
        cells.append(
            BurningCalendarCell(
                year=yr,
                pentad=pt,
                doy_start=doy_s,
                doy_end=doy_e,
                raw_detection_count=int(metrics["raw_det_count"]),
                deduplicated_episode_count=int(metrics["ep_count"]),
                effective_effort_omega=round(metrics["omega"], 4),
                hfd_per_100km2_day=round(metrics["hfd"], 4),
                hrf_mw_per_km2=round(metrics["hrf"], 4),
                raw_frp_mw_per_km2=round(metrics["raw_frp_density"], 4),
                sfai_zscore=round(sfai, 3),
                anomaly_tier=classify_sfai_tier(sfai),
            )
        )

    return cells
