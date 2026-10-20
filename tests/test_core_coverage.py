"""Additional coverage tests for previously untested public seams in flare_chronos_core."""

from __future__ import annotations

import sys
import unittest
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "packages" / "harmonization-core" / "src"))

from flare_chronos_core import (
    AnomalyTier,
    BurningCalendarCell,
    ThermalDetection,
    build_burning_activity_calendar,
    classify_sfai_tier,
    compute_effective_observation_effort,
    haversine_km,
    is_in_south_atlantic_anomaly,
    latlon_to_h3,
)
from flare_chronos_core.domain import ProcessingMode, SatellitePlatform, SensorType


class TestCoreCoverage(unittest.TestCase):
    def test_haversine_known_distance(self) -> None:
        d = haversine_km(0.0, 0.0, 0.0, 1.0)
        self.assertAlmostEqual(d, 111.19, delta=0.5)

    def test_effective_observation_effort_baseline(self) -> None:
        omega = compute_effective_observation_effort(2005, 0.0)
        self.assertAlmostEqual(omega, 1.0, places=2)
        self.assertLess(compute_effective_observation_effort(2000, 0.0), omega)
        self.assertGreater(compute_effective_observation_effort(2025, 0.0), omega)

    def test_saa_detection(self) -> None:
        self.assertTrue(is_in_south_atlantic_anomaly(-22.5, -48.0))
        self.assertFalse(is_in_south_atlantic_anomaly(14.0, 108.0))

    def test_classify_sfai_tier(self) -> None:
        self.assertEqual(classify_sfai_tier(-1.0), AnomalyTier.QUIET)
        self.assertEqual(classify_sfai_tier(0.0), AnomalyTier.BASELINE)
        self.assertEqual(classify_sfai_tier(1.2), AnomalyTier.ELEVATED)
        self.assertEqual(classify_sfai_tier(2.0), AnomalyTier.SEVERE)
        self.assertEqual(classify_sfai_tier(3.0), AnomalyTier.CRISIS)

    def test_latlon_to_h3_returns_string(self) -> None:
        cell = latlon_to_h3(14.0, 108.0, 7)
        self.assertIsInstance(cell, str)
        self.assertGreater(len(cell), 0)

    def test_build_burning_activity_calendar_empty(self) -> None:
        cells = build_burning_activity_calendar([], aoi_area_km2=100.0)
        self.assertEqual(cells, [])

    def test_build_burning_activity_calendar_nonempty(self) -> None:
        det = ThermalDetection(
            detection_id="T1",
            latitude=14.0,
            longitude=108.0,
            acq_datetime_utc=datetime(2024, 3, 20, 5, 0, tzinfo=UTC),
            sensor=SensorType.VIIRS,
            platform=SatellitePlatform.SNPP,
            processing_mode=ProcessingMode.STANDARD,
            scan_km=0.4,
            track_km=0.4,
            bright_t4_k=340.0,
            bright_t5_k=300.0,
            frp_mw=10.0,
            raw_confidence="high",
            raw_daynight="D",
        )
        from flare_chronos_core import cluster_fire_episodes, harmonize_detections

        harm = harmonize_detections([det])
        episodes = cluster_fire_episodes(harm)
        cells = build_burning_activity_calendar(episodes, aoi_area_km2=50.0)
        self.assertGreater(len(cells), 0)
        self.assertIsInstance(cells[0], BurningCalendarCell)


if __name__ == "__main__":
    unittest.main()
