"""Observation effort is weighted by the clear-sky share of each epoch (ERA5)."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "benchmark-cli" / "src"))

from benchmark_cli.fetch_cloud_cover import overpass_cloud_fraction
from flare_chronos_core import cloud_weighted_effort

CLOUD_FILE = ROOT / "data" / "cloud" / "era5_cloud_cover.json"
RESULTS = json.loads(
    (ROOT / "data" / "processed" / "empirical_results.json").read_text()
)


class TestCloudWeightedEffort(unittest.TestCase):
    def test_a_cloudier_than_usual_epoch_lowers_the_effort(self) -> None:
        self.assertLess(cloud_weighted_effort(1.5, clear=0.3, reference_clear=0.5), 1.5)

    def test_a_clearer_than_usual_epoch_raises_the_effort(self) -> None:
        self.assertGreater(
            cloud_weighted_effort(1.5, clear=0.7, reference_clear=0.5), 1.5
        )

    def test_a_typical_epoch_keeps_the_effort(self) -> None:
        self.assertEqual(
            cloud_weighted_effort(1.5, clear=0.5, reference_clear=0.5), 1.5
        )

    def test_a_fully_overcast_epoch_is_refused_not_divided_by_zero(self) -> None:
        with self.assertRaises(ValueError):
            cloud_weighted_effort(1.5, clear=0.0, reference_clear=0.5)


class TestOverpassCloudFraction(unittest.TestCase):
    def test_only_hours_near_the_overpass_count(self) -> None:
        # lon 0: local solar time equals UTC. 13:30 +/- 2h passes, 18:00 does not.
        times = ["2024-03-15T13:00", "2024-03-15T14:00", "2024-03-15T18:00"]
        self.assertAlmostEqual(overpass_cloud_fraction(times, [20, 40, 100], 0.0), 0.30)

    def test_the_night_pass_counts_too(self) -> None:
        times = ["2024-03-15T01:00", "2024-03-15T13:00", "2024-03-15T07:00"]
        self.assertAlmostEqual(overpass_cloud_fraction(times, [0, 100, 50], 0.0), 0.50)

    def test_longitude_shifts_the_local_overpass_hour(self) -> None:
        # lon 105E: local 13:30 is 06:30 UTC, so 06:00 and 07:00 are the pass.
        times = ["2024-03-15T06:00", "2024-03-15T07:00", "2024-03-15T13:00"]
        self.assertAlmostEqual(
            overpass_cloud_fraction(times, [10, 30, 90], 105.0), 0.20
        )

    def test_no_overpass_hours_is_an_error(self) -> None:
        with self.assertRaises(ValueError):
            overpass_cloud_fraction(["2024-03-15T07:00"], [10], 0.0)


class TestPublishedCloudTable(unittest.TestCase):
    def test_every_epoch_has_a_cloud_fraction_in_the_unit_interval(self) -> None:
        table = json.loads(CLOUD_FILE.read_text())["regions"]
        for region in ("mekong", "amazon"):
            for epoch in RESULTS[f"{region}_empirical_epochs"]:
                with self.subTest(region=region, window=epoch["date_window"]):
                    value = table[region][epoch["date_window"]]
                    self.assertGreater(value, 0.0)
                    self.assertLess(value, 1.0)

    def test_each_epoch_publishes_the_weight_it_was_normalized_with(self) -> None:
        for region in ("mekong", "amazon"):
            for epoch in RESULTS[f"{region}_empirical_epochs"]:
                with self.subTest(region=region, year=epoch["year"]):
                    self.assertIn("cloud_clear_sky_fraction", epoch)
                    self.assertIn("cloud_reference_clear_sky_fraction", epoch)


if __name__ == "__main__":
    unittest.main()
