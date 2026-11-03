"""Only observed calendar cells carry an SFAI, a tier or an outline."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "benchmark-cli" / "src"))

from flare_chronos_core import (
    CELL_INTERPOLATED,
    CELL_MODELLED_IN_MEASURED_YEAR,
    CELL_OBSERVED,
    MIN_MEASURED_YEARS,
)

CALENDAR = json.loads(
    (ROOT / "data" / "processed" / "burning_calendar.json").read_text()
)
RESULTS = json.loads(
    (ROOT / "data" / "processed" / "empirical_results.json").read_text()
)


class TestCalendarProvenance(unittest.TestCase):
    def test_every_scored_cell_is_an_observed_cell(self) -> None:
        for region, cal in CALENDAR.items():
            for r, (srow, prow) in enumerate(
                zip(cal["sfai_matrix"], cal["cell_provenance_matrix"])
            ):
                for c, (sfai, prov) in enumerate(zip(srow, prow)):
                    if sfai is not None:
                        with self.subTest(
                            region=region, year=cal["years"][r], pentad=c + 1
                        ):
                            self.assertEqual(prov, CELL_OBSERVED)

    def test_observed_cells_are_exactly_the_measured_epochs_at_the_window_pentad(
        self,
    ) -> None:
        for region, cal in CALENDAR.items():
            measured = {
                e["year"]
                for e in RESULTS[f"{region}_empirical_epochs"]
                if e["year"] != 2026
            }
            observed = {
                cal["years"][r]
                for r, prow in enumerate(cal["cell_provenance_matrix"])
                for c, prov in enumerate(prow)
                if prov == CELL_OBSERVED and c + 1 == cal["observed_pentad"]
            }
            with self.subTest(region=region):
                self.assertEqual(observed, measured)

    def test_a_scored_pentad_has_enough_observed_years(self) -> None:
        for region, cal in CALENDAR.items():
            n_cols = len(cal["sfai_matrix"][0])
            for c in range(n_cols):
                scored = sum(row[c] is not None for row in cal["sfai_matrix"])
                with self.subTest(region=region, pentad=c + 1):
                    self.assertTrue(scored == 0 or scored >= MIN_MEASURED_YEARS)

    def test_provenance_uses_the_three_declared_states(self) -> None:
        states = {
            p
            for cal in CALENDAR.values()
            for row in cal["cell_provenance_matrix"]
            for p in row
        }
        self.assertEqual(
            states, {CELL_OBSERVED, CELL_MODELLED_IN_MEASURED_YEAR, CELL_INTERPOLATED}
        )

    def test_measured_years_match_the_raw_archive_and_exclude_the_current_year(
        self,
    ) -> None:
        from benchmark_cli.epoch_plan import build_epoch_plan

        for region, series in RESULTS["regime_shift_series"].items():
            plan_years = [
                int(date[:4])
                for date, _ in build_epoch_plan(region, ROOT / "data" / "raw", 2026)
            ]
            with self.subTest(region=region):
                self.assertEqual(sorted(series["measured_years"]), plan_years)
                self.assertEqual(series["interpolated_years"], [2026])

    def test_no_cell_of_the_current_year_is_observed(self) -> None:
        for region, cal in CALENDAR.items():
            row = cal["years"].index(2026)
            with self.subTest(region=region):
                self.assertNotIn(CELL_OBSERVED, cal["cell_provenance_matrix"][row])


if __name__ == "__main__":
    unittest.main()
