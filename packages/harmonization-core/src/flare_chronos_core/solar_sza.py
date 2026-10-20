"""Astronomical Solar Zenith Angle (SZA) Computation and Day/Night Unification.

Solves Problem 5 of the NASA Space Apps MODIS-VIIRS Harmonization Challenge:
Near-Real-Time (NRT) VIIRS products (1.0NRT/2.0NRT) assign the DayNight flag based on
ascending/descending orbital node rather than the physical Solar Zenith Angle threshold
(SZA < 85 deg) used in Standard Science Quality products (MCD14ML / VNP14IMGML).
"""

from __future__ import annotations

from datetime import datetime
import math
from typing import Tuple

DAYNIGHT_SZA_THRESHOLD_DEG = 85.0


def compute_solar_zenith_angle(
    latitude_deg: float,
    longitude_deg: float,
    acq_datetime_utc: datetime,
) -> float:
    """Compute exact astronomical Solar Zenith Angle (SZA, in degrees) from UTC and (lat, lon).

    Uses the Spencer (1971) / NOAA Solar Calculator Fourier series for solar declination
    and Equation of Time, accurate to ~0.01 deg across 2000-2030.
    """
    doy = acq_datetime_utc.timetuple().tm_yday
    utc_hours = (
        acq_datetime_utc.hour
        + acq_datetime_utc.minute / 60.0
        + acq_datetime_utc.second / 3600.0
    )

    # Fractional year gamma in radians
    gamma = 2.0 * math.pi / 365.25 * (doy - 1.0 + (utc_hours - 12.0) / 24.0)

    # Equation of Time (in minutes)
    eqtime_min = 229.18 * (
        0.000075
        + 0.001868 * math.cos(gamma)
        - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2.0 * gamma)
        - 0.040849 * math.sin(2.0 * gamma)
    )

    # Solar declination angle (in radians)
    decl_rad = (
        0.006918
        - 0.399912 * math.cos(gamma)
        + 0.070257 * math.sin(gamma)
        - 0.006758 * math.cos(2.0 * gamma)
        + 0.000907 * math.sin(2.0 * gamma)
        - 0.002697 * math.cos(3.0 * gamma)
        + 0.001480 * math.sin(3.0 * gamma)
    )

    # True Solar Time (in minutes) and Solar Hour Angle (degrees)
    time_offset_min = eqtime_min + 4.0 * longitude_deg
    true_solar_time_min = (utc_hours * 60.0 + time_offset_min) % 1440.0
    hour_angle_deg = (true_solar_time_min / 4.0) - 180.0
    if hour_angle_deg < -180.0:
        hour_angle_deg += 360.0

    lat_rad = math.radians(latitude_deg)
    ha_rad = math.radians(hour_angle_deg)

    cos_sza = (
        math.sin(lat_rad) * math.sin(decl_rad)
        + math.cos(lat_rad) * math.cos(decl_rad) * math.cos(ha_rad)
    )
    cos_sza = max(-1.0, min(1.0, cos_sza))
    return round(math.degrees(math.acos(cos_sza)), 4)


def harmonize_daynight_flag(
    latitude_deg: float,
    longitude_deg: float,
    acq_datetime_utc: datetime,
    raw_daynight: str,
    sza_threshold_deg: float = DAYNIGHT_SZA_THRESHOLD_DEG,
) -> Tuple[float, str, bool]:
    """Return (sza_deg, harmonized_daynight, was_reclassified).

    Enforces NASA Standard Processing convention:
      Day ('D')   <=> SZA < 85.0 deg
      Night ('N') <=> SZA >= 85.0 deg
    """
    sza_deg = compute_solar_zenith_angle(latitude_deg, longitude_deg, acq_datetime_utc)
    harmonized = "D" if sza_deg < sza_threshold_deg else "N"
    raw_clean = (raw_daynight or "D").strip().upper()[:1]
    reclassified = harmonized != raw_clean
    return sza_deg, harmonized, reclassified
