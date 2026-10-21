"""Spherical Earth Scan-Angle Footprint Physics and Uber H3 Fractional Allocation.

References:
- Ichoku, C., & Kaufman, Y. J. (2005). A method to derive smoke emission rates from MODIS
  fire radiative energy measurements. IEEE TGRS, 43(11), 2636-2649.
- Giglio, L., Schroeder, W., & Justice, C. O. (2016). The collection 6 MODIS active fire
  detection algorithm and fire products. Remote Sensing of Environment, 178, 31-41.
- Wolfe, R. E., et al. (2013). Suomi NPP VIIRS prelaunch and on-orbit geometric calibration
  and characterization. JGR: Atmospheres, 118(20), 11508-11521.
- Schroeder, W., Oliva, P., Giglio, L., & Csiszar, I. A. (2014). The New VIIRS 375 m active
  fire detection data product: Algorithm description and initial assessment. RSE, 143, 85-96.
"""

from __future__ import annotations

import math

from .domain import (
    InstantaneousFootprint,
    SatellitePlatform,
    SensorType,
    ThermalDetection,
)

# WGS-84 & Sensor Orbital Constants
R_EARTH_KM = 6378.137
MODIS_ALTITUDE_KM = 705.0
MODIS_ORBIT_RADIUS_KM = R_EARTH_KM + MODIS_ALTITUDE_KM  # 7083.137 km
MODIS_SAMPLING_RAD = 0.0014184397  # s: radians per 1-km nominal sample
MODIS_MAX_SCAN_DEG = 55.0

VIIRS_ALTITUDE_KM = 829.0
VIIRS_ORBIT_RADIUS_KM = R_EARTH_KM + VIIRS_ALTITUDE_KM  # 7207.137 km
VIIRS_NATIVE_SCAN_RAD = 0.0001458  # ~121m across-track native detector IFOV (3x = 363m nadir, 795m at 56.28 deg)
VIIRS_NATIVE_TRACK_RAD = (
    0.0004340  # ~360m along-track native detector IFOV (784m at 56.28 deg)
)
VIIRS_ZONE1_MAX_DEG = 31.72  # 3:1 aggregation (0 to 31.72 deg)
VIIRS_ZONE2_MAX_DEG = 44.86  # 2:1 aggregation (31.72 to 44.86 deg)
VIIRS_ZONE3_MAX_DEG = 56.28  # 1:1 no aggregation (44.86 to 56.28 deg)

# Uber H3 Exact Geodesic Cell Areas & Circumradii
H3_RES7_AREA_KM2 = 5.16129336
H3_RES8_AREA_KM2 = 0.73732760
H3_RES7_STEP_KM = math.sqrt(
    H3_RES7_AREA_KM2 / (1.5 * math.sqrt(3.0))
)  # ~1.409 km hex radius
H3_RES8_STEP_KM = math.sqrt(
    H3_RES8_AREA_KM2 / (1.5 * math.sqrt(3.0))
)  # ~0.533 km hex radius

try:
    import h3 as _h3_lib  # type: ignore  # optional dep; resolved when installed

    HAS_NATIVE_H3 = True
except ImportError:
    _h3_lib = None
    HAS_NATIVE_H3 = False


def modis_dimensions_from_scan_angle(theta_rad: float) -> tuple[float, float]:
    """Compute exact MODIS across-track (Delta S) and along-track (Delta T) in km.

    Equations (Giglio et al., 2016):
      Delta S = R_e * s * (cos(theta) / sqrt((R_e / r)^2 - sin^2(theta)) - 1)
      Delta T = r   * s * (cos(theta) - sqrt((R_e / r)^2 - sin^2(theta)))
    """
    theta = abs(theta_rad)
    ratio_sq = (R_EARTH_KM / MODIS_ORBIT_RADIUS_KM) ** 2
    sin_t = math.sin(theta)
    cos_t = math.cos(theta)
    radicand = max(1e-9, ratio_sq - sin_t * sin_t)
    root = math.sqrt(radicand)

    delta_s = R_EARTH_KM * MODIS_SAMPLING_RAD * ((cos_t / root) - 1.0)
    delta_t = MODIS_ORBIT_RADIUS_KM * MODIS_SAMPLING_RAD * (cos_t - root)
    return delta_s, delta_t


def invert_modis_scan_angle(scan_km: float) -> float:
    """Invert Delta S(theta) = scan_km via bisection on [0, 55.5 deg] to 1e-9 rad precision."""
    nadir_s, _ = modis_dimensions_from_scan_angle(0.0)
    if scan_km <= nadir_s:
        return 0.0

    lo = 0.0
    hi = math.radians(55.5)
    for _ in range(45):
        mid = 0.5 * (lo + hi)
        s_mid, _ = modis_dimensions_from_scan_angle(mid)
        if s_mid < scan_km:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def viirs_aggregation_zone(theta_deg: float) -> tuple[int, int]:
    """Return (zone_index, aggregation_factor) for VIIRS 375m I-band scan angle."""
    abs_deg = abs(theta_deg)
    if abs_deg < VIIRS_ZONE1_MAX_DEG:
        return 1, 3
    if abs_deg < VIIRS_ZONE2_MAX_DEG:
        return 2, 2
    return 3, 1


def viirs_dimensions_from_scan_angle(theta_rad: float) -> tuple[float, float, int]:
    """Compute VIIRS 375m I-band (Delta S, Delta T, zone) accounting for 3-zone aggregation.

    In Zone 1 (0-31.72 deg), 3 native pixels are aggregated across-track;
    In Zone 2 (31.72-44.86 deg), 2 native pixels are aggregated;
    In Zone 3 (44.86-56.28 deg), 1 native pixel is used (Wolfe et al., 2013; Schroeder et al., 2014).
    """
    theta = abs(theta_rad)
    theta_deg = math.degrees(theta)
    zone, agg_factor = viirs_aggregation_zone(theta_deg)

    ratio_sq = (R_EARTH_KM / VIIRS_ORBIT_RADIUS_KM) ** 2
    sin_t = math.sin(theta)
    cos_t = math.cos(theta)
    root = math.sqrt(max(1e-9, ratio_sq - sin_t * sin_t))

    eff_s_rad = agg_factor * VIIRS_NATIVE_SCAN_RAD
    delta_s = R_EARTH_KM * eff_s_rad * ((cos_t / root) - 1.0)
    delta_t = VIIRS_ORBIT_RADIUS_KM * VIIRS_NATIVE_TRACK_RAD * (cos_t - root)
    return delta_s, delta_t, zone


def invert_viirs_scan_angle(scan_km: float, track_km: float) -> tuple[float, int]:
    """Recover VIIRS scan angle theta_rad and aggregation zone from reported (scan, track) km."""
    # Track dimension grows monotonically from 0.36 km at nadir to ~0.784 km at 56.28 deg
    lo = 0.0
    hi = math.radians(VIIRS_ZONE3_MAX_DEG)
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        _, t_mid, _ = viirs_dimensions_from_scan_angle(mid)
        if t_mid < track_km:
            lo = mid
        else:
            hi = mid
    theta_from_track = 0.5 * (lo + hi)

    # Refine using scan_km if track_km was rounded to 2 decimal places (e.g. 0.37, 0.42)
    best_theta = theta_from_track
    best_err = float("inf")
    for offset_deg in (-3.0, -1.5, -0.5, 0.0, 0.5, 1.5, 3.0):
        cand = max(
            0.0,
            min(
                math.radians(VIIRS_ZONE3_MAX_DEG),
                theta_from_track + math.radians(offset_deg),
            ),
        )
        s_c, t_c, _ = viirs_dimensions_from_scan_angle(cand)
        err = (s_c - scan_km) ** 2 + 1.5 * (t_c - track_km) ** 2
        if err < best_err:
            best_err = err
            best_theta = cand

    zone, _ = viirs_aggregation_zone(math.degrees(best_theta))
    return best_theta, zone


def compute_orbital_track_azimuth(
    latitude_deg: float,
    platform: SatellitePlatform,
    daynight: str,
) -> float:
    """Compute satellite sub-orbital track azimuth (degrees clockwise from North).

    Sun-synchronous polar inclination:
      i = 98.2 deg (Terra / Aqua)
      i = 98.7 deg (Suomi-NPP / NOAA-20 / NOAA-21)
    """
    inc_deg = (
        98.2 if platform in (SatellitePlatform.TERRA, SatellitePlatform.AQUA) else 98.7
    )
    cos_i = math.cos(math.radians(inc_deg))
    cos_lat = max(0.15, math.cos(math.radians(latitude_deg)))
    sin_az = max(-1.0, min(1.0, cos_i / cos_lat))
    base_az_deg = math.degrees(math.asin(sin_az))  # ~ -8.3 deg at equator

    # Ascending node vs Descending node orientation
    is_ascending = (platform != SatellitePlatform.TERRA and daynight == "D") or (
        platform == SatellitePlatform.TERRA and daynight == "N"
    )
    if is_ascending:
        return (360.0 + base_az_deg) % 360.0
    return (180.0 - base_az_deg) % 360.0


def latlon_to_h3(lat: float, lon: float, resolution: int) -> str:
    """Map (lat, lon) to canonical Uber H3 index at Resolution 7 or 8.

    Uses native h3-py when installed; otherwise computes a deterministic geodesic
    equal-area hexagonal lattice index formatted as a standard 15-character H3 hex string.
    """
    if HAS_NATIVE_H3 and _h3_lib is not None:
        if hasattr(_h3_lib, "latlng_to_cell"):
            return str(_h3_lib.latlng_to_cell(lat, lon, resolution))  # type: ignore[union-attr]
        return str(_h3_lib.geo_to_h3(lat, lon, resolution))  # type: ignore[union-attr]

    # Deterministic equal-area hexagonal lattice projection (Snyder Equal-Area Hexagonal Grid)
    step_km = H3_RES7_STEP_KM if resolution == 7 else H3_RES8_STEP_KM
    # Equal-area authalic coordinates in km
    y_km = R_EARTH_KM * math.radians(lat)
    x_km = R_EARTH_KM * math.radians(lon) * math.cos(math.radians(lat))

    # Axial hex coordinates (q, r)
    q_f = (math.sqrt(3.0) / 3.0 * x_km - 1.0 / 3.0 * y_km) / step_km
    r_f = (2.0 / 3.0 * y_km) / step_km

    # Cube rounding to exact hexagonal cell
    x_c, z_c = q_f, r_f
    y_c = -x_c - z_c
    rx, ry, rz = round(x_c), round(y_c), round(z_c)
    dx, dy, dz = abs(rx - x_c), abs(ry - y_c), abs(rz - z_c)
    if dx > dy and dx > dz:
        rx = -ry - rz
    elif dy > dz:
        ry = -rx - rz
    else:
        rz = -rx - ry

    q_int = int(rx) + 500_000
    r_int = int(rz) + 500_000
    header = 0x8700000000000000 if resolution == 7 else 0x8800000000000000
    cell_int = header | ((q_int & 0xFFFFFF) << 24) | (r_int & 0xFFFFFF)
    return f"{cell_int:015x}"


def reconstruct_instantaneous_footprint(
    det: ThermalDetection,
) -> InstantaneousFootprint:
    """Reconstruct physical ground footprint (Delta S x Delta T) and scan geometry."""
    scan_km = max(0.30, float(det.scan_km))
    track_km = max(0.30, float(det.track_km))

    if det.sensor == SensorType.MODIS:
        theta_rad = invert_modis_scan_angle(scan_km)
        calc_s, calc_t = modis_dimensions_from_scan_angle(theta_rad)
        # Preserve empirical FIRMS scan/track if present, fallback to analytical spherical solution
        delta_s = scan_km if scan_km > 0.9 else calc_s
        delta_t = track_km if track_km > 0.9 else calc_t
        zone = 0
        nadir_area = 1.0
    else:
        theta_rad, zone = invert_viirs_scan_angle(scan_km, track_km)
        calc_s, calc_t, _ = viirs_dimensions_from_scan_angle(theta_rad)
        delta_s = scan_km if scan_km > 0.30 else calc_s
        delta_t = track_km if track_km > 0.30 else calc_t
        nadir_area = 0.375 * 0.375  # 0.140625 km^2 nominal

    area_km2 = delta_s * delta_t
    track_az = compute_orbital_track_azimuth(
        det.latitude, det.platform, det.raw_daynight
    )

    return InstantaneousFootprint(
        scan_angle_rad=theta_rad,
        scan_angle_deg=math.degrees(theta_rad),
        delta_s_km=round(delta_s, 4),
        delta_t_km=round(delta_t, 4),
        area_km2=round(area_km2, 4),
        track_azimuth_deg=round(track_az, 2),
        semi_major_km=round(0.5 * max(delta_s, delta_t), 4),
        semi_minor_km=round(0.5 * min(delta_s, delta_t), 4),
        aggregation_zone=zone,
        area_expansion_factor=round(area_km2 / nadir_area, 4),
    )


def allocate_footprint_to_h3(
    lat: float,
    lon: float,
    footprint: InstantaneousFootprint,
    resolution: int = 7,
) -> dict[str, float]:
    """Fractionally allocate an oriented elliptical footprint across Uber H3 Iso-Area Cells.

    Uses a 13-point Gaussian-like elliptical quadrature stencil rotated by the satellite
    track azimuth so that edge-of-swath MODIS pixels (~9.7 km^2) distribute energy
    proportionally across all intersected H3 cells, with sum(weights) == 1.0.
    """
    center_cell = latlon_to_h3(lat, lon, resolution)
    cell_area = H3_RES7_AREA_KM2 if resolution == 7 else H3_RES8_AREA_KM2

    # Fast path if footprint is much smaller than a single H3 cell (e.g., VIIRS nadir on Res 7)
    if footprint.area_km2 <= 0.25 * cell_area:
        return {center_cell: 1.0}

    # 13-point elliptical quadrature stencil in normalized (u_scan, v_track) coordinates in [-1, 1]
    # Center point (weight 0.28) + inner ring at r=0.45 (4 pts x 0.09) + outer ring at r=0.82 (8 pts x 0.045)
    stencil = [(0.0, 0.0, 0.28)]
    for angle_deg in (0.0, 90.0, 180.0, 270.0):
        rad = math.radians(angle_deg)
        stencil.append((0.45 * math.cos(rad), 0.45 * math.sin(rad), 0.09))
    for angle_deg in range(0, 360, 45):
        rad = math.radians(angle_deg)
        stencil.append((0.82 * math.cos(rad), 0.82 * math.sin(rad), 0.045))

    az_rad = math.radians(footprint.track_azimuth_deg)
    cos_az = math.cos(az_rad)
    sin_az = math.sin(az_rad)
    half_s = 0.5 * footprint.delta_s_km
    half_t = 0.5 * footprint.delta_t_km
    km_per_deg_lat = 111.132
    km_per_deg_lon = max(15.0, 111.320 * math.cos(math.radians(lat)))

    weights: dict[str, float] = {}
    for u_s, v_t, w in stencil:
        dx_scan = u_s * half_s
        dy_track = v_t * half_t
        # Rotate from (across-track, along-track) into (East, North) km
        east_km = dx_scan * cos_az + dy_track * sin_az
        north_km = -dx_scan * sin_az + dy_track * cos_az

        pt_lat = lat + (north_km / km_per_deg_lat)
        pt_lon = lon + (east_km / km_per_deg_lon)
        cell = latlon_to_h3(pt_lat, pt_lon, resolution)
        weights[cell] = weights.get(cell, 0.0) + w

    # Normalize to exact unity
    total_w = sum(weights.values())
    return {k: round(v / total_w, 6) for k, v in weights.items()}
