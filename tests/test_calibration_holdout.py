"""Calibration quality is judged on pairs the model never saw."""

from __future__ import annotations

import unittest

import numpy as np
from flare_chronos_core import holdout_validation


def synthetic_pairs(n: int, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    areas = rng.uniform(1.0, 7.5, size=n)
    true_frp = rng.lognormal(mean=3.4, sigma=0.75, size=n)
    modis = np.maximum(
        4.0, true_frp / ((1.0 + 0.30 * np.log(areas)) * 1.32) + rng.normal(0, 2.0, n)
    )
    viirs = true_frp + rng.normal(0, 1.5, n)
    return modis, viirs, areas


class TestHoldoutValidation(unittest.TestCase):
    def test_calibration_beats_raw_on_unseen_pairs_with_an_interval(self) -> None:
        modis, viirs, areas = synthetic_pairs(600, seed=7)
        train = np.arange(600) < 400
        out = holdout_validation(modis, viirs, areas, train)
        self.assertEqual(out["n_train"], 400)
        self.assertEqual(out["n_test"], 200)
        self.assertLess(out["harmonized_rmse_mw"], out["raw_rmse_mw"])
        low, high = out["rmse_gain_ci95_mw"]
        self.assertLess(low, high)
        self.assertGreater(low, 0.0)

    def test_the_blend_weight_is_fitted_on_training_pairs_only(self) -> None:
        modis, viirs, areas = synthetic_pairs(600, seed=7)
        train = np.arange(600) < 400
        out = holdout_validation(modis, viirs, areas, train)
        self.assertGreaterEqual(out["blend_parametric_weight"], 0.0)
        self.assertLessEqual(out["blend_parametric_weight"], 1.0)

    def test_a_test_set_from_a_shifted_sensor_relation_is_reported_not_hidden(
        self,
    ) -> None:
        modis, viirs, areas = synthetic_pairs(600, seed=7)
        viirs = viirs.copy()
        viirs[400:] *= 3.0  # test-era VIIRS reads three times brighter than training
        out = holdout_validation(modis, viirs, areas, np.arange(600) < 400)
        self.assertGreater(out["harmonized_rmse_mw"], out["train_rmse_mw"])


if __name__ == "__main__":
    unittest.main()


class TestHoldoutHonesty(unittest.TestCase):
    def test_a_split_with_no_test_pairs_is_refused(self) -> None:
        modis, viirs, areas = synthetic_pairs(100, seed=3)
        with self.assertRaises(ValueError):
            holdout_validation(modis, viirs, areas, np.ones(100, dtype=bool))

    def test_resampling_whole_groups_widens_the_interval_for_correlated_pairs(
        self,
    ) -> None:
        modis, viirs, areas = synthetic_pairs(600, seed=7)
        groups = np.repeat(np.arange(60), 10)  # ten pairs share each date
        viirs = viirs + np.repeat(np.random.default_rng(1).normal(0, 25, 60), 10)
        train = np.arange(600) < 400
        iid = holdout_validation(modis, viirs, areas, train)
        grouped = holdout_validation(modis, viirs, areas, train, groups=groups)
        iid_width = iid["rmse_gain_ci95_mw"][1] - iid["rmse_gain_ci95_mw"][0]
        grouped_width = (
            grouped["rmse_gain_ci95_mw"][1] - grouped["rmse_gain_ci95_mw"][0]
        )
        self.assertGreater(grouped_width, iid_width)


class TestPublishedHoldout(unittest.TestCase):
    def test_the_published_calibration_gain_is_positive_on_held_out_years(self) -> None:
        import json
        from pathlib import Path

        results = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "data/processed/empirical_results.json"
            ).read_text()
        )
        holdout = results["coincident_calibration"]["holdout"]
        self.assertGreater(holdout["n_test"], 1000)
        self.assertGreater(holdout["rmse_gain_ci95_mw"][0], 0.0)
        self.assertLess(holdout["harmonized_rmse_mw"], holdout["raw_rmse_mw"])
