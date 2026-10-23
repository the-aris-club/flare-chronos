"""The hand-set effort constants are traced to the conclusions they move."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "benchmark-cli" / "src"))

from benchmark_cli.sensitivity import (
    harmonized_episode_count,
    sensitivity_table,
)

RESULTS = json.loads(
    (ROOT / "data" / "processed" / "empirical_results.json").read_text()
)


class TestConstantSensitivity(unittest.TestCase):
    def test_the_shared_formula_reproduces_every_published_epoch(self) -> None:
        for region in ("mekong", "amazon"):
            for e in RESULTS[f"{region}_empirical_epochs"]:
                with self.subTest(region=region, year=e["year"]):
                    got = harmonized_episode_count(
                        region,
                        e["sources"],
                        e["deduplicated_fire_episodes"],
                        e["effective_observation_effort_omega"],
                    )
                    self.assertAlmostEqual(
                        got, e["harmonized_viirs_eq_episodes"], delta=0.1
                    )

    def test_the_modis_only_omission_factor_moves_the_transition_step_one_for_one(
        self,
    ) -> None:
        rows = {r["constant"]: r for r in sensitivity_table(RESULTS, "mekong", 0.2)}
        self.assertAlmostEqual(
            rows["subpixel_omission_factor"]["transition_step_change_pct"],
            -16.7,
            delta=0.2,
        )

    def test_the_era_omega_moves_the_step_as_much_as_the_omission_factor(self) -> None:
        rows = {r["constant"]: r for r in sensitivity_table(RESULTS, "amazon", 0.2)}
        self.assertAlmostEqual(
            rows["omega"]["transition_step_change_pct"], -16.7, delta=0.2
        )
        self.assertGreater(
            rows["omega"]["transition_step_change_pct"],
            rows["stream_overlap_gain"]["transition_step_change_pct"] - 100,
        )
        self.assertLess(
            abs(rows["stream_overlap_gain"]["transition_step_change_pct"]),
            abs(rows["omega"]["transition_step_change_pct"]),
        )

    def test_every_constant_reports_its_effect_on_the_headline_step(self) -> None:
        names = {r["constant"] for r in sensitivity_table(RESULTS, "amazon", 0.2)}
        self.assertEqual(
            names, {"subpixel_omission_factor", "stream_overlap_gain", "omega"}
        )


if __name__ == "__main__":
    unittest.main()
