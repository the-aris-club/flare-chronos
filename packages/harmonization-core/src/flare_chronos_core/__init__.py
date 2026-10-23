"""Flare-Chronos Core Harmonization Deep Module Interface."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime

import pandas as pd

from .calendar_engine import (
    SFAI_CRISIS_THRESHOLD_Z,
    SFAI_SEVERE_THRESHOLD_Z,
    build_burning_activity_calendar,
    classify_sfai_tier,
    day_of_year_to_pentad,
    pentad_to_doy_range,
)
from .confidence_filter import (
    build_static_source_registry,
    compute_unified_detection_probability,
    has_aqua_nrt_geolocation_risk,
    is_in_south_atlantic_anomaly,
    is_static_or_non_veg_source,
)
from .deduplication import (
    cluster_fire_episodes,
    compute_effective_observation_effort,
    haversine_km,
)
from .domain import (
    AnomalyTier,
    BurningCalendarCell,
    FireEpisode,
    HarmonizedDetection,
    InstantaneousFootprint,
    ProcessingMode,
    SatellitePlatform,
    SensorType,
    ThermalDetection,
)
from .geometry_h3 import (
    H3_RES7_AREA_KM2,
    H3_RES8_AREA_KM2,
    allocate_footprint_to_h3,
    compute_orbital_track_azimuth,
    invert_modis_scan_angle,
    invert_viirs_scan_angle,
    latlon_to_h3,
    modis_dimensions_from_scan_angle,
    reconstruct_instantaneous_footprint,
    viirs_aggregation_zone,
    viirs_dimensions_from_scan_angle,
)
from .radiometric_calibrator import (
    CrossSensorCalibrationModel,
    apply_two_stage_frp_calibration,
    compute_frp_detection_limit,
    default_calibration_model,
    fit_coincident_aqua_snpp_model,
    holdout_validation,
)
from .solar_sza import (
    DAYNIGHT_SZA_THRESHOLD_DEG,
    compute_solar_zenith_angle,
    harmonize_daynight_flag,
)


def parse_firms_dataframe(
    df: pd.DataFrame, default_source: str = ""
) -> list[ThermalDetection]:
    """Convert a raw NASA FIRMS CSV DataFrame (MODIS or VIIRS) into ThermalDetection records."""
    if df is None or df.empty:
        return []

    records: list[ThermalDetection] = []
    cols = {c.lower(): c for c in df.columns}

    for idx, row in df.iterrows():
        lat = float(row[cols["latitude"]])
        lon = float(row[cols["longitude"]])
        scan_km = float(row[cols.get("scan", "scan")]) if "scan" in cols else 1.0
        track_km = float(row[cols.get("track", "track")]) if "track" in cols else 1.0

        # Brightness temperatures: MODIS uses brightness / bright_t31; VIIRS uses bright_ti4 / bright_ti5
        if "bright_ti4" in cols:
            t4 = float(row[cols["bright_ti4"]])
            t5 = float(row[cols.get("bright_ti5", "bright_ti4")])
            sensor = SensorType.VIIRS
        else:
            t4 = float(row[cols.get("brightness", "bright_ti4")])
            t5 = float(row[cols.get("bright_t31", "brightness")])
            sensor = SensorType.MODIS

        inst_str = str(row[cols["instrument"]]).upper() if "instrument" in cols else ""
        src_str = (
            str(row[cols["source_code"]]).upper()
            if "source_code" in cols
            else default_source.upper()
        )
        if "VIIRS" in inst_str or "VIIRS" in src_str or scan_km < 0.85:
            sensor = SensorType.VIIRS
        elif "MODIS" in inst_str or "MODIS" in src_str:
            sensor = SensorType.MODIS

        sat_raw = (
            str(row[cols.get("satellite", "")]).strip().upper()
            if "satellite" in cols
            else ""
        )
        if sat_raw in ("T", "TERRA"):
            platform = SatellitePlatform.TERRA
        elif sat_raw in ("A", "AQUA"):
            platform = SatellitePlatform.AQUA
        elif sat_raw in ("N", "SNPP", "SUOMI-NPP", "NP"):
            platform = SatellitePlatform.SNPP
        elif sat_raw in ("1", "J1", "N20", "NOAA-20", "NOAA20") or "NOAA20" in src_str:
            platform = SatellitePlatform.NOAA20
        elif sat_raw in ("2", "J2", "N21", "NOAA-21", "NOAA21") or "NOAA21" in src_str:
            platform = SatellitePlatform.NOAA21
        else:
            platform = (
                SatellitePlatform.AQUA
                if sensor == SensorType.MODIS
                else SatellitePlatform.SNPP
            )

        ver_str = (
            str(row[cols["version"]]).strip().upper() if "version" in cols else "6.1"
        )
        if "URT" in ver_str:
            proc_mode = ProcessingMode.URT
        elif "NRT" in ver_str or "NRT" in src_str:
            proc_mode = ProcessingMode.NRT
        elif "RT" in ver_str:
            proc_mode = ProcessingMode.RT
        else:
            proc_mode = ProcessingMode.STANDARD

        acq_date_str = str(row[cols["acq_date"]]).strip()
        acq_time_raw = str(row[cols["acq_time"]]).strip().zfill(4)
        hh = int(acq_time_raw[:2]) if acq_time_raw[:2].isdigit() else 0
        mm = int(acq_time_raw[2:4]) if acq_time_raw[2:4].isdigit() else 0
        dt_utc = datetime.strptime(acq_date_str, "%Y-%m-%d").replace(
            hour=min(23, hh), minute=min(59, mm), tzinfo=UTC
        )

        frp_val = (
            float(row[cols["frp"]])
            if "frp" in cols and pd.notna(row[cols["frp"]])
            else 1.0
        )
        conf_val = str(row[cols.get("confidence", "nominal")]).strip()
        dn_val = str(row[cols.get("daynight", "D")]).strip().upper()
        ftype = (
            int(row[cols["type"]])
            if "type" in cols and pd.notna(row[cols["type"]])
            else None
        )

        records.append(
            ThermalDetection(
                detection_id=f"{sensor.value}-{platform.value}-{acq_date_str}-{idx}",
                latitude=lat,
                longitude=lon,
                acq_datetime_utc=dt_utc,
                sensor=sensor,
                platform=platform,
                processing_mode=proc_mode,
                scan_km=scan_km,
                track_km=track_km,
                bright_t4_k=t4,
                bright_t5_k=t5,
                frp_mw=max(0.0, frp_val),
                raw_confidence=conf_val,
                raw_daynight=dn_val,
                version_tag=ver_str,
                fire_type=ftype,
            )
        )

    return records


def harmonize_detections(
    detections: Iterable[ThermalDetection],
    calibration_model: CrossSensorCalibrationModel | None = None,
    persistent_static_h3_res8: set[str] | None = None,
) -> list[HarmonizedDetection]:
    """Execute full 5-stage physical & statistical harmonization on raw Thermal Detections."""
    static_cells = persistent_static_h3_res8 or set()
    cal_model = calibration_model or default_calibration_model()
    results: list[HarmonizedDetection] = []

    for det in detections:
        footprint = reconstruct_instantaneous_footprint(det)
        sza_deg, harm_dn, reclass = harmonize_daynight_flag(
            det.latitude, det.longitude, det.acq_datetime_utc, det.raw_daynight
        )
        prob, is_saa = compute_unified_detection_probability(det, harm_dn)
        h3_r7 = latlon_to_h3(det.latitude, det.longitude, 7)
        h3_r8 = latlon_to_h3(det.latitude, det.longitude, 8)
        is_static = is_static_or_non_veg_source(det, h3_r8, static_cells)
        aqua_warn = has_aqua_nrt_geolocation_risk(det, footprint.scan_angle_deg)

        frp_lim, scan_frp, viirs_eq_frp, viirs_eq_cnt = apply_two_stage_frp_calibration(
            det, footprint, sza_deg, harm_dn, cal_model
        )
        w_r7 = allocate_footprint_to_h3(
            det.latitude, det.longitude, footprint, resolution=7
        )
        w_r8 = allocate_footprint_to_h3(
            det.latitude, det.longitude, footprint, resolution=8
        )

        results.append(
            HarmonizedDetection(
                raw=det,
                footprint=footprint,
                sza_deg=sza_deg,
                harmonized_daynight=harm_dn,
                daynight_reclassified=reclass,
                detection_probability=prob,
                is_saa_anomaly=is_saa,
                is_static_thermal_source=is_static,
                aqua_nrt_geoloc_warning=aqua_warn,
                frp_detection_limit_mw=frp_lim,
                scan_corrected_frp_mw=scan_frp,
                calibrated_viirs_eq_frp_mw=viirs_eq_frp,
                calibrated_viirs_eq_count=viirs_eq_cnt,
                h3_res7_cell=h3_r7,
                h3_res8_cell=h3_r8,
                h3_res7_weights=w_r7,
                h3_res8_weights=w_r8,
            )
        )

    return results


__all__ = [
    "DAYNIGHT_SZA_THRESHOLD_DEG",
    "H3_RES7_AREA_KM2",
    "H3_RES8_AREA_KM2",
    "SFAI_CRISIS_THRESHOLD_Z",
    "SFAI_SEVERE_THRESHOLD_Z",
    "AnomalyTier",
    "BurningCalendarCell",
    "CrossSensorCalibrationModel",
    "FireEpisode",
    "HarmonizedDetection",
    "InstantaneousFootprint",
    "ProcessingMode",
    "SatellitePlatform",
    "SensorType",
    "ThermalDetection",
    "allocate_footprint_to_h3",
    "apply_two_stage_frp_calibration",
    "build_burning_activity_calendar",
    "build_static_source_registry",
    "classify_sfai_tier",
    "cluster_fire_episodes",
    "compute_effective_observation_effort",
    "compute_frp_detection_limit",
    "compute_orbital_track_azimuth",
    "compute_solar_zenith_angle",
    "compute_unified_detection_probability",
    "day_of_year_to_pentad",
    "default_calibration_model",
    "fit_coincident_aqua_snpp_model",
    "harmonize_daynight_flag",
    "harmonize_detections",
    "has_aqua_nrt_geolocation_risk",
    "haversine_km",
    "holdout_validation",
    "invert_modis_scan_angle",
    "invert_viirs_scan_angle",
    "is_in_south_atlantic_anomaly",
    "is_static_or_non_veg_source",
    "latlon_to_h3",
    "modis_dimensions_from_scan_angle",
    "parse_firms_dataframe",
    "pentad_to_doy_range",
    "reconstruct_instantaneous_footprint",
    "viirs_aggregation_zone",
    "viirs_dimensions_from_scan_angle",
]

__author__ = "Xiro The Dev <lethanhtrung.trungle@gmail.com>"
