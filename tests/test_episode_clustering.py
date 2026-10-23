"""Fire Episode clustering must stay inside one diurnal window."""

from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta

from flare_chronos_core import cluster_fire_episodes, harmonize_detections
from flare_chronos_core.domain import (
    ProcessingMode,
    SatellitePlatform,
    SensorType,
    ThermalDetection,
)

WINDOW_MIN = 95.0


def viirs_detection(det_id: str, minutes_after_start: float) -> ThermalDetection:
    start = datetime(2024, 3, 18, 5, 0, tzinfo=UTC)
    return ThermalDetection(
        detection_id=det_id,
        latitude=15.25,
        longitude=107.12,
        acq_datetime_utc=start + timedelta(minutes=minutes_after_start),
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


class TestEpisodeWindow(unittest.TestCase):
    def test_a_chain_of_close_detections_does_not_become_one_long_episode(
        self,
    ) -> None:
        """Five detections 80 minutes apart span 320 minutes; no episode may exceed the window."""
        chain = [viirs_detection(f"C{i}", 80.0 * i) for i in range(5)]
        episodes = cluster_fire_episodes(
            harmonize_detections(chain), temporal_window_minutes=WINDOW_MIN
        )
        self.assertGreater(len(episodes), 1)
        for ep in episodes:
            span_min = (ep.end_utc - ep.start_utc).total_seconds() / 60.0
            self.assertLessEqual(span_min, WINDOW_MIN)

    def test_detections_inside_the_window_still_merge(self) -> None:
        pair = [viirs_detection("A", 0.0), viirs_detection("B", 60.0)]
        episodes = cluster_fire_episodes(
            harmonize_detections(pair), temporal_window_minutes=WINDOW_MIN
        )
        self.assertEqual(len(episodes), 1)


if __name__ == "__main__":
    unittest.main()
