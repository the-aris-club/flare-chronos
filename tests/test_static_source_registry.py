"""The Static Source Registry is derived from the archive, not typed in."""

from __future__ import annotations

import unittest
from datetime import UTC, datetime

from flare_chronos_core import (
    build_static_source_registry,
    harmonize_detections,
    latlon_to_h3,
)
from flare_chronos_core.domain import (
    ProcessingMode,
    SatellitePlatform,
    SensorType,
    ThermalDetection,
)

FLARE = (15.25, 107.12)


def detection_at(lat: float, lon: float) -> ThermalDetection:
    return ThermalDetection(
        detection_id="D1",
        latitude=lat,
        longitude=lon,
        acq_datetime_utc=datetime(2024, 3, 18, 5, 0, tzinfo=UTC),
        sensor=SensorType.VIIRS,
        platform=SatellitePlatform.SNPP,
        processing_mode=ProcessingMode.STANDARD,
        scan_km=0.39,
        track_km=0.37,
        bright_t4_k=345.0,
        bright_t5_k=302.0,
        frp_mw=20.0,
        raw_confidence="high",
        raw_daynight="D",
    )


class TestStaticSourceRegistry(unittest.TestCase):
    def test_a_cell_hot_all_year_is_static_and_a_seasonal_cell_is_not(self) -> None:
        flare_cell = latlon_to_h3(*FLARE, 8)
        farm_cell = latlon_to_h3(14.0, 106.0, 8)
        observations = [(flare_cell, m) for m in range(1, 13)]
        observations += [(farm_cell, m) for m in (2, 3, 4)]
        registry = build_static_source_registry(observations)
        self.assertIn(flare_cell, registry)
        self.assertNotIn(farm_cell, registry)

    def test_repeat_detections_in_one_month_do_not_make_a_cell_static(self) -> None:
        cell = latlon_to_h3(*FLARE, 8)
        registry = build_static_source_registry([(cell, 3)] * 500)
        self.assertNotIn(cell, registry)

    def test_harmonization_rejects_a_detection_in_a_registered_cell(self) -> None:
        cell = latlon_to_h3(*FLARE, 8)
        registry = build_static_source_registry([(cell, m) for m in range(1, 13)])
        det = detection_at(*FLARE)
        self.assertFalse(harmonize_detections([det])[0].is_static_thermal_source)
        flagged = harmonize_detections([det], persistent_static_h3_res8=set(registry))
        self.assertTrue(flagged[0].is_static_thermal_source)


if __name__ == "__main__":
    unittest.main()
