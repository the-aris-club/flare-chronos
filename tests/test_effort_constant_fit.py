"""The MODIS-only omission factor is fitted on early epochs and scored on later ones."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "benchmark-cli" / "src"))

from benchmark_cli.sensitivity import (
    FIT_TRAIN_LAST_YEAR,
    HAND_SET_OMISSION_FACTOR,
    SUBPIXEL_OMISSION_FACTOR,
    fit_omission_factor,
)

RESULTS = json.loads(
    (ROOT / "data" / "processed" / "empirical_results.json").read_text()
)

# Held-out epochs must hold the all-sensor and MODIS-only counts within this gap.
# Looser than the 0.10 aim of the strict xfail gate: one 5-day window per epoch.
HELD_OUT_TOLERANCE = 0.20


def epoch(year: int, ratio: float) -> dict:
    return {"year": year, "sensor_invariance_ratio": ratio}


class TestFitOmissionFactor(unittest.TestCase):
    def test_the_fit_is_the_median_of_the_factors_that_make_each_ratio_one(
        self,
    ) -> None:
        epochs = [
            epoch(2012, 0.8),
            epoch(2016, 1.0),
            epoch(2019, 0.9),
            epoch(2024, 0.7),
        ]
        fit = fit_omission_factor(epochs, k_current=2.0, train_last_year=2020)
        self.assertAlmostEqual(fit["k_fit"], 2.0 * 0.9)
        self.assertEqual(fit["train_years"], [2012, 2016, 2019])

    def test_held_out_ratios_are_rescaled_by_the_fit_and_never_used_to_fit(
        self,
    ) -> None:
        epochs = [epoch(2012, 0.5), epoch(2016, 0.5), epoch(2024, 0.9)]
        fit = fit_omission_factor(epochs, k_current=2.0, train_last_year=2020)
        self.assertAlmostEqual(fit["k_fit"], 1.0)
        self.assertEqual(fit["held_out_before"], {2024: 0.9})
        self.assertAlmostEqual(fit["held_out_after"][2024], 1.8)

    def test_the_report_compares_against_the_hand_set_reference(self) -> None:
        epochs = [epoch(2012, 1.0), epoch(2016, 1.0), epoch(2024, 1.0)]
        # current factor 2.0 fits (ratio 1.0); the old hand-set factor was 4.0
        fit = fit_omission_factor(epochs, 2.0, 2020, k_reference=4.0)
        self.assertEqual(fit["k_prior"], 4.0)
        self.assertAlmostEqual(fit["held_out_before"][2024], 0.5)
        self.assertAlmostEqual(fit["held_out_after"][2024], 1.0)

    def test_epochs_without_a_ratio_are_skipped(self) -> None:
        epochs = [
            epoch(2005, 1.0) | {"sensor_invariance_ratio": None},
            epoch(2012, 0.5),
        ]
        self.assertEqual(fit_omission_factor(epochs, 2.0, 2020)["train_years"], [2012])


class TestFittedConstantsOnTheArchive(unittest.TestCase):
    def test_the_committed_factors_are_the_fit_of_the_published_ratios(self) -> None:
        for region, k in SUBPIXEL_OMISSION_FACTOR.items():
            epochs = RESULTS[f"{region}_empirical_epochs"]
            fit = fit_omission_factor(
                epochs, k, FIT_TRAIN_LAST_YEAR, HAND_SET_OMISSION_FACTOR[region]
            )
            with self.subTest(region=region):
                self.assertAlmostEqual(fit["k_fit"], k, delta=0.01)

    def test_held_out_epochs_hold_sensor_invariance_within_tolerance(self) -> None:
        for region in SUBPIXEL_OMISSION_FACTOR:
            fit = RESULTS["omission_factor_fit"][region]
            for year, ratio in fit["held_out_after"].items():
                with self.subTest(region=region, year=year):
                    self.assertLessEqual(abs(ratio - 1.0), HELD_OUT_TOLERANCE)

    def test_the_artifact_publishes_the_fit_for_both_regions(self) -> None:
        self.assertEqual(set(RESULTS["omission_factor_fit"]), {"mekong", "amazon"})


if __name__ == "__main__":
    unittest.main()
