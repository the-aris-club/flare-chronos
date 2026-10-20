"""Unified Detection Probability Mapping, SAA Noise Rejection, and Static Source Filtering.

Solves Problem 3 & Problem 5 (partial) of the NASA MODIS-VIIRS Harmonization Challenge:
- Maps MODIS continuous confidence (0-100%) and VIIRS categorical confidence (low, nominal, high)
  onto a unified physical Detection Probability P(fire) in [0, 1].
- Rejects nighttime proton-hit false alarms inside the South Atlantic Anomaly (SAA:
  11 E to 110 W, 7 N to 55 S) that exhibit weak longwave thermal support.
- Identifies Static Thermal Sources (type in {1, 2, 3} or persistent H3 cells).
"""

from __future__ import annotations

import math

from .domain import ProcessingMode, SatellitePlatform, SensorType, ThermalDetection

# South Atlantic Anomaly Bounding Envelope (NASA Earthdata FIRMS FAQ)
SAA_LON_MIN = -110.0
SAA_LON_MAX = 11.0
SAA_LAT_MIN = -55.0
SAA_LAT_MAX = 7.0


def is_in_south_atlantic_anomaly(lat: float, lon: float) -> bool:
    """Return True if coordinates fall within the South Atlantic Anomaly envelope."""
    return (SAA_LAT_MIN <= lat <= SAA_LAT_MAX) and (SAA_LON_MIN <= lon <= SAA_LON_MAX)


def compute_unified_detection_probability(
    det: ThermalDetection,
    harmonized_daynight: str,
) -> tuple[float, bool]:
    """Map heterogeneous sensor confidence and brightness temperatures to P(fire) in [0, 1].

    Returns:
      (detection_probability, is_saa_anomaly)
    """
    delta_t45 = max(0.0, float(det.bright_t4_k) - float(det.bright_t5_k))
    in_saa = is_in_south_atlantic_anomaly(det.latitude, det.longitude)

    if det.sensor == SensorType.MODIS:
        try:
            conf_num = float(det.raw_confidence)
        except ValueError:
            conf_num = 50.0
        conf_num = max(0.0, min(100.0, conf_num))
        # Calibrated logistic mapping anchored at Giglio et al. (2003, 2016) classes:
        # 30% -> P=0.32 (low threshold), 50% -> P=0.60, 80% -> P=0.90 (high threshold)
        z = (conf_num - 38.0) / 19.0
        # Radiometric thermal contrast reinforcement
        z += 0.015 * min(40.0, max(-10.0, delta_t45 - 18.0))
        base_prob = 1.0 / (1.0 + math.exp(-z))
    else:
        raw_c = (det.raw_confidence or "n").strip().lower()
        if raw_c.startswith("h"):
            # High confidence: saturated I4 or strong daytime/nighttime anomaly
            anchor = 0.94
        elif raw_c.startswith("n"):
            # Nominal confidence: >15K anomaly free of sun glint
            anchor = 0.78 if harmonized_daynight == "D" else 0.84
        else:
            # Low confidence: daytime sun glint candidate or weak <15K anomaly
            anchor = 0.28 if harmonized_daynight == "D" else 0.38

        # Modulate within class band using 4um - 11um brightness contrast (Delta T_45)
        thermal_boost = 0.06 * math.tanh((delta_t45 - 20.0) / 15.0)
        base_prob = max(0.05, min(0.99, anchor + thermal_boost))

    # South Atlantic Anomaly (SAA) Nighttime Cosmic-Ray Spike Filter:
    # High-energy protons in the SAA trigger single-band 4um spikes at night without
    # corresponding 11um (T5) heating or sustained FRP (Schroeder et al., 2014).
    is_saa_false_alarm = False
    if (
        in_saa
        and harmonized_daynight == "N"
        and (
            (delta_t45 < 16.5 and det.frp_mw < 2.2)
            or (base_prob < 0.45 and delta_t45 < 19.5)
        )
    ):
        is_saa_false_alarm = True
        base_prob *= 0.12

    return round(base_prob, 4), is_saa_false_alarm


def is_static_or_non_veg_source(
    det: ThermalDetection,
    h3_res8_cell: str,
    persistent_static_cells: set[str],
) -> bool:
    """Identify industrial gas flares, volcanoes, offshore platforms, or persistent H3 cells."""
    if det.fire_type is not None and det.fire_type in (1, 2, 3):
        return True
    return h3_res8_cell in persistent_static_cells


def has_aqua_nrt_geolocation_risk(det: ThermalDetection, scan_angle_deg: float) -> bool:
    """Flag Aqua NRT/RT/URT detections where orbital maneuvers can induce multi-km error."""
    return bool(
        det.platform == SatellitePlatform.AQUA
        and det.processing_mode
        in (ProcessingMode.NRT, ProcessingMode.RT, ProcessingMode.URT)
        and scan_angle_deg >= 30.0
    )
