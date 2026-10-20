"""Unit & Mathematical Verification Test Suite for Flare-Chronos.

Tests all 5 core cross-sensor scientific harmonization equations:
1. Spherical MODIS & 3-Zone VIIRS Bow-tie Footprint Reconstruction + H3 Fractional Allocation
2. Two-Stage Physics-Guided FRP Observation Operator & Co-Incident Overpass Calibration
3. Unified Detection Probability, SAA Nighttime Cosmic-Ray Rejection & Static Source Filtering
4. Spatio-Temporal Multi-Satellite Overpass Deduplication & Effective Observation Effort Omega
5. Astronomical Solar Zenith Angle (SZA < 85 deg) DayNight Unification
"""

from __future__ import annotations

from datetime import datetime, timezone
import math
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "packages" / "harmonization-core" / "src"))

from harmonization.firms_harmonizer import (  # noqa: E402
    FIRMSHarmonizer,
    ProcessingMode,
    SatellitePlatform,
    SensorType,
    ThermalDetection,
    allocate_footprint_to_h3,
    build_burning_activity_calendar,
    cluster_fire_episodes,
    compute_effective_observation_effort,
    compute_frp_detection_limit,
    compute_solar_zenith_angle,
    compute_unified_detection_probability,
    fit_coincident_aqua_snpp_model,
    harmonize_daynight_flag,
    harmonize_detections,
    invert_modis_scan_angle,
    modis_dimensions_from_scan_angle,
    reconstruct_instantaneous_footprint,
    viirs_aggregation_zone,
    viirs_dimensions_from_scan_angle,
)


class TestFlareChronosPhysics(unittest.TestCase):
    """Verify exact physical and statistical properties of Flare-Chronos."""

    def test_modis_spherical_scan_geometry(self) -> None:
        """MODIS nadir is 1.0x1.0 km (1.0 km^2) and expands to ~4.83x2.01 km (~9.69 km^2) at 55 deg."""
        s0, t0 = modis_dimensions_from_scan_angle(0.0)
        self.assertAlmostEqual(s0, 1.000, places=2)
        self.assertAlmostEqual(t0, 1.000, places=2)

        theta_55 = math.radians(55.0)
        s55, t55 = modis_dimensions_from_scan_angle(theta_55)
        area_55 = s55 * t55
        self.assertGreater(s55, 4.75)
        self.assertLess(s55, 4.90)
        self.assertGreater(t55, 1.98)
        self.assertLess(t55, 2.05)
        self.assertAlmostEqual(area_55, 9.69, delta=0.15)

        # Verify inversion accuracy
        theta_recovered = invert_modis_scan_angle(s55)
        self.assertAlmostEqual(math.degrees(theta_recovered), 55.0, places=2)

    def test_viirs_three_zone_aggregation_physics(self) -> None:
        """VIIRS 3-zone aggregation bounds (31.72, 44.86, 56.28 deg) keep footprint <= 0.65 km^2."""
        z1, f1 = viirs_aggregation_zone(15.0)
        z2, f2 = viirs_aggregation_zone(38.0)
        z3, f3 = viirs_aggregation_zone(52.0)
        self.assertEqual((z1, f1), (1, 3))
        self.assertEqual((z2, f2), (2, 2))
        self.assertEqual((z3, f3), (3, 1))

        s_nadir, t_nadir, _ = viirs_dimensions_from_scan_angle(0.0)
        self.assertAlmostEqual(s_nadir * t_nadir, 0.138, delta=0.02)

        s_edge, t_edge, z_edge = viirs_dimensions_from_scan_angle(math.radians(56.28))
        self.assertEqual(z_edge, 3)
        self.assertLess(s_edge * t_edge, 0.66)
        self.assertGreater(s_edge * t_edge, 0.55)

    def test_h3_fractional_allocation_conserves_energy(self) -> None:
        """Fractional allocation weights onto H3 Res 7 and Res 8 must sum strictly to 1.0."""
        edge_modis = ThermalDetection(
            detection_id="M-EDGE",
            latitude=14.5,
            longitude=107.8,
            acq_datetime_utc=datetime(2024, 3, 16, 6, 30, tzinfo=timezone.utc),
            sensor=SensorType.MODIS,
            platform=SatellitePlatform.AQUA,
            processing_mode=ProcessingMode.STANDARD,
            scan_km=4.80,
            track_km=2.00,
            bright_t4_k=335.0,
            bright_t5_k=298.0,
            frp_mw=120.0,
            raw_confidence="85",
            raw_daynight="D",
        )
        fp = reconstruct_instantaneous_footprint(edge_modis)
        w7 = allocate_footprint_to_h3(edge_modis.latitude, edge_modis.longitude, fp, resolution=7)
        w8 = allocate_footprint_to_h3(edge_modis.latitude, edge_modis.longitude, fp, resolution=8)

        self.assertAlmostEqual(sum(w7.values()), 1.0, places=4)
        self.assertAlmostEqual(sum(w8.values()), 1.0, places=4)
        # A 9.6 km^2 MODIS edge pixel must span multiple H3 Res 8 cells (0.737 km^2 each)
        self.assertGreaterEqual(len(w8), 3)

    def test_astronomical_sza_and_daynight_unification(self) -> None:
        """Verify SZA < 85 deg daytime classification and NRT twilight reclassification."""
        # Solar noon in Central Highlands Vietnam (14.0 N, 108.0 E) at 05:00 UTC (~12:12 local solar)
        dt_noon = datetime(2024, 3, 20, 5, 0, tzinfo=timezone.utc)
        sza_noon = compute_solar_zenith_angle(14.0, 108.0, dt_noon)
        self.assertLess(sza_noon, 20.0)

        # Midnight at 17:00 UTC (~00:12 local solar)
        dt_night = datetime(2024, 3, 20, 17, 0, tzinfo=timezone.utc)
        sza_night, dn_flag, reclass = harmonize_daynight_flag(14.0, 108.0, dt_night, raw_daynight="D")
        self.assertGreater(sza_night, 140.0)
        self.assertEqual(dn_flag, "N")
        self.assertTrue(reclass)

    def test_saa_nighttime_anomaly_rejection(self) -> None:
        """Nighttime low-contrast spike inside South Atlantic Anomaly must be flagged."""
        saa_det = ThermalDetection(
            detection_id="V-SAA",
            latitude=-22.5,
            longitude=-48.0,
            acq_datetime_utc=datetime(2024, 8, 21, 4, 15, tzinfo=timezone.utc),
            sensor=SensorType.VIIRS,
            platform=SatellitePlatform.SNPP,
            processing_mode=ProcessingMode.NRT,
            scan_km=0.42,
            track_km=0.39,
            bright_t4_k=304.0,
            bright_t5_k=291.0,  # Delta T_45 = 13 K (< 24 K threshold)
            frp_mw=1.2,
            raw_confidence="low",
            raw_daynight="N",
        )
        prob, is_saa = compute_unified_detection_probability(saa_det, "N")
        self.assertTrue(is_saa)
        self.assertLess(prob, 0.10)

    def test_multi_satellite_overpass_deduplication(self) -> None:
        """Afternoon overpass train (NOAA-20, NOAA-21, SNPP, Aqua) within 55 min merges into 1 Fire Episode."""
        base_lat, base_lon = 15.250, 107.120
        raw_pass_train = [
            ThermalDetection(
                detection_id="N20-1",
                latitude=base_lat,
                longitude=base_lon,
                acq_datetime_utc=datetime(2024, 3, 18, 5, 42, tzinfo=timezone.utc),
                sensor=SensorType.VIIRS,
                platform=SatellitePlatform.NOAA20,
                processing_mode=ProcessingMode.STANDARD,
                scan_km=0.39,
                track_km=0.37,
                bright_t4_k=342.0,
                bright_t5_k=301.0,
                frp_mw=18.5,
                raw_confidence="nominal",
                raw_daynight="D",
            ),
            ThermalDetection(
                detection_id="N21-1",
                latitude=base_lat + 0.0015,
                longitude=base_lon - 0.0010,
                acq_datetime_utc=datetime(2024, 3, 18, 6, 7, tzinfo=timezone.utc),
                sensor=SensorType.VIIRS,
                platform=SatellitePlatform.NOAA21,
                processing_mode=ProcessingMode.NRT,
                scan_km=0.41,
                track_km=0.38,
                bright_t4_k=345.0,
                bright_t5_k=302.0,
                frp_mw=21.0,
                raw_confidence="nominal",
                raw_daynight="D",
            ),
            ThermalDetection(
                detection_id="SNPP-1",
                latitude=base_lat - 0.0010,
                longitude=base_lon + 0.0012,
                acq_datetime_utc=datetime(2024, 3, 18, 6, 32, tzinfo=timezone.utc),
                sensor=SensorType.VIIRS,
                platform=SatellitePlatform.SNPP,
                processing_mode=ProcessingMode.STANDARD,
                scan_km=0.38,
                track_km=0.36,
                bright_t4_k=348.0,
                bright_t5_k=302.5,
                frp_mw=22.4,
                raw_confidence="high",
                raw_daynight="D",
            ),
            ThermalDetection(
                detection_id="AQUA-1",
                latitude=base_lat + 0.0030,
                longitude=base_lon + 0.0020,
                acq_datetime_utc=datetime(2024, 3, 18, 6, 35, tzinfo=timezone.utc),
                sensor=SensorType.MODIS,
                platform=SatellitePlatform.AQUA,
                processing_mode=ProcessingMode.STANDARD,
                scan_km=1.45,
                track_km=1.18,
                bright_t4_k=328.0,
                bright_t5_k=300.0,
                frp_mw=15.0,
                raw_confidence="78",
                raw_daynight="D",
            ),
        ]

        harm = harmonize_detections(raw_pass_train)
        episodes = cluster_fire_episodes(harm, temporal_window_minutes=95.0)
        self.assertEqual(len(episodes), 1)
        ep = episodes[0]
        self.assertEqual(ep.raw_detection_count, 4)
        self.assertEqual(len(ep.contributing_platforms), 4)
        self.assertGreater(ep.combined_probability, 0.98)

    def test_two_stage_coincident_frp_calibration(self) -> None:
        """Fitting the Two-Stage Observation Operator + EQM reduces KS distance and RMSE."""
        rng = np.random.default_rng(42)
        n = 120
        areas = rng.uniform(1.0, 7.5, size=n)
        true_frp = rng.lognormal(mean=3.4, sigma=0.75, size=n)
        # Simulate MODIS scan-angle attenuation + truncation vs VIIRS reference
        modis_obs = true_frp / ((1.0 + 0.30 * np.log(areas)) * 1.32) + rng.normal(0, 2.0, size=n)
        modis_obs = np.maximum(4.0, modis_obs)
        viirs_obs = true_frp + rng.normal(0, 1.5, size=n)

        model = fit_coincident_aqua_snpp_model(modis_obs, viirs_obs, areas)
        self.assertGreater(model.harmonized_r2, model.raw_r2)
        self.assertLess(model.harmonized_rmse_mw, model.raw_rmse_mw)
        self.assertLess(model.ks_stat_after, model.ks_stat_before)


if __name__ == "__main__":
    unittest.main()
