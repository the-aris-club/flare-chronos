"""Guards the project's reason for existing: no artificial step at a sensor transition.

Naively summing detections jumps when a satellite joins the constellation
(+SNPP 2012, +NOAA-20 2018, +NOAA-21 2024). The harmonized series must not
inherit that jump. Each Measured Epoch is one 5-day window, so the gate is
deliberately coarse: it compares the harmonized change across a transition with
the change in the MODIS-only count over the same years (the control, a single
sensor family that did not change constellation), and fails only when the two
disagree by more than ``MAX_STEP_DIVERGENCE``.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS_JSON = ROOT / "data" / "processed" / "empirical_results.json"

# (before_year, after_year) pairs that straddle a constellation change and are
# both Measured Epochs. 2016->2019 spans +NOAA-20, 2023->2024 spans +NOAA-21.
TRANSITIONS = {
    "mekong": [(2010, 2012), (2016, 2019), (2023, 2024)],
    "amazon": [(2010, 2012), (2012, 2019), (2020, 2024)],
}

# The harmonized ratio may differ from the MODIS-control ratio by at most this
# factor in either direction. Coarse on purpose: one 5-day window per year.
MAX_STEP_DIVERGENCE = 2.0


def step_divergence(before: dict, after: dict) -> float:
    """Harmonized ratio divided by the MODIS-control ratio across a transition."""
    harmonized = (
        after["harmonized_viirs_eq_episodes"] / before["harmonized_viirs_eq_episodes"]
    )
    control = (
        after["raw_counts_by_source"]["MODIS_SP"]
        / before["raw_counts_by_source"]["MODIS_SP"]
    )
    return harmonized / control


class TestSensorTransitionSteps(unittest.TestCase):
    def setUp(self) -> None:
        self.results = json.loads(RESULTS_JSON.read_text())

    def test_step_divergence_is_computed_from_the_artifact(self) -> None:
        before = {
            "harmonized_viirs_eq_episodes": 100.0,
            "raw_counts_by_source": {"MODIS_SP": 50},
        }
        after = {
            "harmonized_viirs_eq_episodes": 150.0,
            "raw_counts_by_source": {"MODIS_SP": 50},
        }
        self.assertAlmostEqual(step_divergence(before, after), 1.5)

    def test_no_artificial_step_at_sensor_transitions(self) -> None:
        for region, pairs in TRANSITIONS.items():
            epochs = {e["year"]: e for e in self.results[f"{region}_empirical_epochs"]}
            for y0, y1 in pairs:
                with self.subTest(region=region, transition=f"{y0}->{y1}"):
                    ratio = step_divergence(epochs[y0], epochs[y1])
                    self.assertLess(ratio, MAX_STEP_DIVERGENCE)
                    self.assertGreater(ratio, 1.0 / MAX_STEP_DIVERGENCE)


if __name__ == "__main__":
    unittest.main()
