"""The Measured Epoch plan is read from the raw archive, never typed by hand."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "benchmark-cli" / "src"))

from benchmark_cli.epoch_plan import build_epoch_plan


def _slice(raw: Path, region: str, source: str, date: str) -> None:
    """Write a slice file big enough to count as real data."""
    (raw / f"{region}__{source}__{date}__5d.csv").write_text("x" * 200)


class TestEpochPlan(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raw = Path(self._tmp.name)

    def test_a_modis_only_year_is_a_measured_epoch(self) -> None:
        _slice(self.raw, "mekong", "MODIS_SP", "2005-03-15")
        _slice(self.raw, "mekong", "MODIS_SP", "2006-03-15")

        plan = build_epoch_plan("mekong", self.raw, current_year=2026)

        self.assertEqual(
            plan,
            [("2005-03-15", ["MODIS_SP"]), ("2006-03-15", ["MODIS_SP"])],
        )

    def test_the_current_year_is_never_a_measured_epoch(self) -> None:
        _slice(self.raw, "mekong", "MODIS_SP", "2025-03-15")
        _slice(self.raw, "mekong", "MODIS_SP", "2026-03-15")

        plan = build_epoch_plan("mekong", self.raw, current_year=2026)

        self.assertEqual(plan, [("2025-03-15", ["MODIS_SP"])])

    def test_viirs_slices_present_in_the_archive_join_the_epoch(self) -> None:
        for source in ("MODIS_SP", "VIIRS_SNPP_SP", "VIIRS_NOAA20_SP"):
            _slice(self.raw, "amazon", source, "2020-08-20")
        _slice(self.raw, "amazon", "VIIRS_NOAA21_NRT", "2020-08-20")
        _slice(self.raw, "amazon", "VIIRS_SNPP_SP", "2021-08-20")  # no MODIS anchor

        plan = build_epoch_plan("amazon", self.raw, current_year=2026)

        self.assertEqual(
            plan,
            [
                (
                    "2020-08-20",
                    [
                        "MODIS_SP",
                        "VIIRS_SNPP_SP",
                        "VIIRS_NOAA20_SP",
                        "VIIRS_NOAA21_NRT",
                    ],
                )
            ],
        )

    def test_an_empty_viirs_slice_is_not_a_contributing_source(self) -> None:
        _slice(self.raw, "mekong", "MODIS_SP", "2013-03-15")
        (self.raw / "mekong__VIIRS_SNPP_SP__2013-03-15__5d.csv").write_text("hdr\n")

        plan = build_epoch_plan("mekong", self.raw, current_year=2026)

        self.assertEqual(plan, [("2013-03-15", ["MODIS_SP"])])

    def test_an_archive_with_no_measured_epoch_is_an_error_not_an_empty_plan(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            build_epoch_plan("mekong", self.raw, current_year=2026)


if __name__ == "__main__":
    unittest.main()
