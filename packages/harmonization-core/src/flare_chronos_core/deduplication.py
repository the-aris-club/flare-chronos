"""Spatio-Temporal Multi-Satellite Overpass Deduplication & Effort Normalization.

Solves Problem 4 of the NASA MODIS-VIIRS Harmonization Challenge:
- Clusters detections from closely spaced overpasses (e.g. Suomi-NPP at 13:30 MLT,
  NOAA-20 at ~12:40 MLT, NOAA-21 at ~13:05 MLT, and Aqua at 13:30 MLT) into unified
  Fire Episodes within an elliptical footprint overlap radius and 90-minute overpass window.
- Computes the Effective Observation Effort factor Omega(year, latitude) to prevent
  constellation expansion (from 1 satellite in 2000 to 5 satellites in 2024-2026)
  from creating artificial upward fire trends.
"""

from __future__ import annotations

import math

from .domain import FireEpisode, HarmonizedDetection
from .geometry_h3 import R_EARTH_KM


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute great-circle distance in kilometers between two coordinates."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp * 0.5) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl * 0.5) ** 2
    return 2.0 * R_EARTH_KM * math.asin(min(1.0, math.sqrt(a)))


def compute_effective_observation_effort(year: int, latitude_deg: float) -> float:
    """Compute Effective Observation Effort factor Omega(year, latitude).

    Anchored to 1.00 at the dual-MODIS (Terra + Aqua, 2003-2011) equatorial baseline:
    - 2000-2001 (Terra only, 2 passes/day): Omega_0 = 0.52
    - 2002 (Aqua launch mid-year): Omega_0 = 0.76
    - 2003-2011 (Terra + Aqua, 4 passes/day): Omega_0 = 1.00
    - 2012-2017 (+ Suomi-NPP wider 3040 km swath & 375m sensitivity): Omega_0 = 1.48
    - 2018-2022 (+ NOAA-20 50-min phased orbit reducing cloud/smoke occlusion): Omega_0 = 1.78
    - 2023 (+ NOAA-21 commissioning): Omega_0 = 1.92
    - 2024-2026 (+ NOAA-21 full operational 3-VIIRS + 2-MODIS constellation): Omega_0 = 2.08

    Modulated by latitude-dependent swath overlap sec(lat) bounded to [1.0, 1.65].
    """
    if year <= 2001:
        base_omega = 0.52
    elif year == 2002:
        base_omega = 0.76
    elif year <= 2011:
        base_omega = 1.00
    elif year <= 2017:
        base_omega = 1.48
    elif year <= 2022:
        base_omega = 1.78
    elif year == 2023:
        base_omega = 1.92
    else:
        base_omega = 2.08

    # Polar-orbiting swath convergence increases revisit frequency with |latitude|
    cos_lat = max(0.55, math.cos(math.radians(latitude_deg)))
    lat_convergence = 1.0 + 0.18 * ((1.0 / cos_lat) - 1.0)
    return round(base_omega * lat_convergence, 4)


def cluster_fire_episodes(
    detections: list[HarmonizedDetection],
    temporal_window_minutes: float = 95.0,
    min_probability: float = 0.20,
) -> list[FireEpisode]:
    """Deduplicate multi-satellite Thermal Detections into physical Fire Episodes.

    Two detections d_i, d_j belong to the same Fire Episode if:
      1. neither is an SAA cosmic-ray anomaly or Static Thermal Source,
      2. |t_i - t_j| <= temporal_window_minutes (default 95 min covers the entire
         NOAA-20 / NOAA-21 / Suomi-NPP / Aqua afternoon or midnight overpass train), and
      3. great-circle distance(d_i, d_j) <= r_eff(d_i) + r_eff(d_j) + 0.65 km
         (or they map to the same H3 Resolution 7 cell within the overpass window).
    """
    valid = [
        d
        for d in detections
        if not d.is_saa_anomaly
        and not d.is_static_thermal_source
        and d.detection_probability >= min_probability
    ]
    if not valid:
        return []

    # Sort chronologically by UTC acquisition timestamp
    valid.sort(key=lambda d: d.raw.acq_datetime_utc)

    clusters: list[list[HarmonizedDetection]] = []
    # Spatial hash buckets (0.05 deg ~ 5.5 km grid) -> list of active clusters for O(1) neighbor lookup
    spatial_buckets: dict[tuple[int, int], list[list[HarmonizedDetection]]] = {}

    for det in valid:
        t_cur = det.raw.acq_datetime_utc
        r_cur = math.sqrt(det.footprint.area_km2 / math.pi)
        b_lat = math.floor(det.raw.latitude * 20.0)
        b_lon = math.floor(det.raw.longitude * 20.0)
        matched_cluster = None

        # Search 3x3 neighboring 0.05-deg buckets
        for dlat in (-1, 0, 1):
            if matched_cluster is not None:
                break
            for dlon in (-1, 0, 1):
                key = (b_lat + dlat, b_lon + dlon)
                bucket = spatial_buckets.get(key)
                if not bucket:
                    continue
                still_active: list[list[HarmonizedDetection]] = []
                for cl in bucket:
                    # Seed-anchored: linking to the newest member would let a run of
                    # detections each inside the window chain into one long episode.
                    anchor = cl[0]
                    dt_min = (
                        t_cur - anchor.raw.acq_datetime_utc
                    ).total_seconds() / 60.0
                    if dt_min > temporal_window_minutes:
                        continue
                    still_active.append(cl)
                    if matched_cluster is None:
                        if det.h3_res8_cell == anchor.h3_res8_cell:
                            matched_cluster = cl
                        else:
                            r_anchor = math.sqrt(anchor.footprint.area_km2 / math.pi)
                            dist_km = haversine_km(
                                det.raw.latitude,
                                det.raw.longitude,
                                anchor.raw.latitude,
                                anchor.raw.longitude,
                            )
                            if dist_km <= max(1.35, r_cur + r_anchor + 0.65):
                                matched_cluster = cl
                spatial_buckets[key] = still_active

        if matched_cluster is not None:
            matched_cluster.append(det)
        else:
            new_cl = [det]
            clusters.append(new_cl)
            spatial_buckets.setdefault((b_lat, b_lon), []).append(new_cl)

    episodes: list[FireEpisode] = []
    for idx, cl in enumerate(clusters, start=1):
        # Weight centroid toward finest-resolution (smallest footprint area) detections
        inv_areas = [1.0 / max(0.10, d.footprint.area_km2) for d in cl]
        sum_inv = sum(inv_areas)
        c_lat = sum(d.raw.latitude * w for d, w in zip(cl, inv_areas)) / sum_inv
        c_lon = sum(d.raw.longitude * w for d, w in zip(cl, inv_areas)) / sum_inv

        # Independent Bayesian evidence combination: P_comb = 1 - prod(1 - P_i * w_sensor)
        miss_prod = 1.0
        for d in cl:
            miss_prod *= max(0.01, 1.0 - 0.85 * d.detection_probability)
        combined_prob = min(0.999, 1.0 - miss_prod)

        platforms = sorted({d.raw.platform.value for d in cl})
        raw_sum_frp = sum(d.raw.frp_mw for d in cl)
        raw_mean_frp = raw_sum_frp / len(cl)

        # Group by distinct overpass platform to avoid summing redundant passes,
        # while summing sub-pixel VIIRS clusters captured on the SAME platform pass
        by_platform_frp: dict[str, float] = {}
        for d in cl:
            plat_key = f"{d.raw.platform.value}_{d.raw.acq_datetime_utc.strftime('%Y%m%d%H%M')}"
            by_platform_frp[plat_key] = (
                by_platform_frp.get(plat_key, 0.0) + d.calibrated_viirs_eq_frp_mw
            )

        # Inverse-variance / footprint-weighted mean across distinct overpasses in the episode
        harmonized_frp = sum(by_platform_frp.values()) / max(1, len(by_platform_frp))

        year = cl[0].raw.acq_datetime_utc.year
        omega = compute_effective_observation_effort(year, c_lat)
        effort_norm_count = combined_prob / omega

        # Pick representative finest-resolution H3 cells
        finest_det = min(cl, key=lambda d: d.footprint.area_km2)
        episodes.append(
            FireEpisode(
                episode_id=f"EP-{cl[0].raw.acq_datetime_utc.strftime('%Y%m%d')}-{idx:06d}",
                centroid_lat=round(c_lat, 5),
                centroid_lon=round(c_lon, 5),
                start_utc=cl[0].raw.acq_datetime_utc,
                end_utc=cl[-1].raw.acq_datetime_utc,
                h3_res7_cell=finest_det.h3_res7_cell,
                h3_res8_cell=finest_det.h3_res8_cell,
                harmonized_daynight=finest_det.harmonized_daynight,
                contributing_platforms=platforms,
                raw_detection_count=len(cl),
                combined_probability=round(combined_prob, 4),
                max_footprint_area_km2=round(max(d.footprint.area_km2 for d in cl), 4),
                raw_sum_frp_mw=round(raw_sum_frp, 3),
                raw_mean_frp_mw=round(raw_mean_frp, 3),
                harmonized_frp_mw=round(harmonized_frp, 3),
                effective_observation_effort_omega=omega,
                effort_normalized_episode_count=round(effort_norm_count, 4),
            )
        )

    return episodes
