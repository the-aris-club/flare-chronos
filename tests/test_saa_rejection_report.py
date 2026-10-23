"""Every epoch reports how much of its detections the SAA rule rejected."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "benchmark-cli" / "src"))

from benchmark_cli.run_experiments import (
    evaluate_epoch_slice,
    run_coincident_overpass_calibration,
)


class TestSaaRejectionReport(unittest.TestCase):
    def test_epoch_reports_the_rejected_share_as_a_percentage(self) -> None:
        model, _ = run_coincident_overpass_calibration()
        epoch = evaluate_epoch_slice(
            "amazon", "2005-08-20", ["MODIS_SP"], model, max_sample_per_source=500
        )
        share = epoch["saa_rejected_share_pct"]
        self.assertGreaterEqual(share, 0.0)
        self.assertLessEqual(share, 100.0)


if __name__ == "__main__":
    unittest.main()
