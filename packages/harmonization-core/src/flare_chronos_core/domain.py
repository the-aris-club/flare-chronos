"""Domain types for Flare-Chronos cross-sensor active fire harmonization.

Vocabulary strictly follows root GLOSSARY.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class SensorType(str, Enum):
    MODIS = "MODIS"
    VIIRS = "VIIRS"


class SatellitePlatform(str, Enum):
    TERRA = "Terra"
    AQUA = "Aqua"
    SNPP = "Suomi-NPP"
    NOAA20 = "NOAA-20"
    NOAA21 = "NOAA-21"


class ProcessingMode(str, Enum):
    STANDARD = "Standard"
    NRT = "NRT"
    RT = "RT"
    URT = "URT"


class AnomalyTier(str, Enum):
    QUIET = "Quiet / Suppressed (SFAI < -0.5)"
    BASELINE = "Normal Seasonal Baseline (-0.5 <= SFAI < 1.0)"
    ELEVATED = "Elevated Seasonal Activity (1.0 <= SFAI < 1.75)"
    SEVERE = "Severe Fire Period (1.75 <= SFAI < 2.5)"
    CRISIS = "Extreme Out-of-Season / Crisis Anomaly (SFAI >= 2.5)"


@dataclass(frozen=True)
class ThermalDetection:
    """A single raw active-fire or thermal-anomaly observation from MODIS or VIIRS."""

    detection_id: str
    latitude: float
    longitude: float
    acq_datetime_utc: datetime
    sensor: SensorType
    platform: SatellitePlatform
    processing_mode: ProcessingMode
    scan_km: float
    track_km: float
    bright_t4_k: float          # ~3.96 um (MODIS Ch21/22) or 3.74 um (VIIRS I4)
    bright_t5_k: float          # ~11.0 um (MODIS Ch31) or 11.45 um (VIIRS I5)
    frp_mw: float               # Instantaneous Fire Radiative Power (MW)
    raw_confidence: str         # "0"-"100" for MODIS; "l"/"n"/"h" or "low"/"nominal"/"high" for VIIRS
    raw_daynight: str           # "D" or "N"
    version_tag: str = "6.1"
    fire_type: Optional[int] = None  # Standard MCD14ML/VNP14IMGML type: 0=veg, 1=volcano, 2=static, 3=offshore


@dataclass(frozen=True)
class InstantaneousFootprint:
    """Actual ground-projected elliptical area swept by a detector element."""

    scan_angle_rad: float
    scan_angle_deg: float
    delta_s_km: float
    delta_t_km: float
    area_km2: float
    track_azimuth_deg: float
    semi_major_km: float
    semi_minor_km: float
    aggregation_zone: int       # 0 for MODIS; 1, 2, or 3 for VIIRS 375m
    area_expansion_factor: float


@dataclass(frozen=True)
class HarmonizedDetection:
    """Thermal Detection enriched with physical geometry, SZA, confidence, and H3 weights."""

    raw: ThermalDetection
    footprint: InstantaneousFootprint
    sza_deg: float
    harmonized_daynight: str    # "D" iff SZA < 85.0 deg else "N"
    daynight_reclassified: bool
    detection_probability: float
    is_saa_anomaly: bool
    is_static_thermal_source: bool
    aqua_nrt_geoloc_warning: bool
    frp_detection_limit_mw: float
    scan_corrected_frp_mw: float
    calibrated_viirs_eq_frp_mw: float
    calibrated_viirs_eq_count: float
    h3_res7_cell: str
    h3_res8_cell: str
    h3_res7_weights: Dict[str, float] = field(default_factory=dict)
    h3_res8_weights: Dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class FireEpisode:
    """A unique physical burning event reconstructed across multi-satellite overpasses."""

    episode_id: str
    centroid_lat: float
    centroid_lon: float
    start_utc: datetime
    end_utc: datetime
    h3_res7_cell: str
    h3_res8_cell: str
    harmonized_daynight: str
    contributing_platforms: List[str]
    raw_detection_count: int
    combined_probability: float
    max_footprint_area_km2: float
    raw_sum_frp_mw: float
    raw_mean_frp_mw: float
    harmonized_frp_mw: float
    effective_observation_effort_omega: float
    effort_normalized_episode_count: float


@dataclass(frozen=True)
class BurningCalendarCell:
    """A single Year x Pentad cell in the Harmonized Burning Activity Calendar."""

    year: int
    pentad: int                 # 1..73 (5-day standard climatological step)
    doy_start: int
    doy_end: int
    raw_detection_count: int
    deduplicated_episode_count: int
    effective_effort_omega: float
    hfd_per_100km2_day: float   # Harmonized Fire Density (episodes / 100 km^2 / day)
    hrf_mw_per_km2: float       # Harmonized Radiative Flux (MW / km^2)
    raw_frp_mw_per_km2: float
    sfai_zscore: float          # Standardized Fire Anomaly Index
    anomaly_tier: AnomalyTier
