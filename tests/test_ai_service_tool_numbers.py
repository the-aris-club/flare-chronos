"""Tool answers come from the published artifact, never from hand-copied literals."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
for src in (
    ROOT / "apps" / "ai-service" / "src",
    ROOT / "packages" / "harmonization-core" / "src",
    ROOT / "packages" / "firms-ingestion" / "src",
):
    sys.path.insert(0, str(src))

from ai_service import tools

RESULTS = json.loads(
    (ROOT / "data" / "processed" / "empirical_results.json").read_text()
)


class TestToolNumbersComeFromTheArtifact(unittest.TestCase):
    def test_the_recalibration_audit_reports_the_published_calibration(self) -> None:
        out = tools.tool_uc3_3_autonomous_biome_recalibration.invoke({})
        cal = RESULTS["coincident_calibration"]

        self.assertEqual(out["coincident_cell_pairs_n"], cal["n_pairs"])
        self.assertEqual(out["ks_distance_before"], cal["ks_before"])
        self.assertEqual(out["ks_distance_after"], cal["ks_after"])
        self.assertEqual(out["harmonized_r2"], cal["harm_r2"])
        self.assertEqual(out["harmonized_rmse_mw"], cal["harm_rmse"])

    def test_the_source_classifier_reports_the_fitted_omission_factors(self) -> None:
        out = tools.tool_uc1_3_thermal_source_origin_classification.invoke({})

        self.assertEqual(
            out["agricultural_small_fire_subpixel_multiplier_mekong"],
            RESULTS["omission_factor_fit"]["mekong"]["k_fit"],
        )
        self.assertEqual(
            out["deforestation_front_subpixel_multiplier_amazon"],
            RESULTS["omission_factor_fit"]["amazon"]["k_fit"],
        )

    def test_a_missing_artifact_is_an_error_not_a_stale_default(self) -> None:
        with (
            mock.patch.object(tools, "_load_empirical_results", return_value={}),
            self.assertRaisesRegex(RuntimeError, "coincident_calibration"),
        ):
            tools.tool_uc3_3_autonomous_biome_recalibration.invoke({})

    def test_every_query_box_is_the_one_the_ingestion_uses(self) -> None:
        from firms_ingestion import BBOX_MEKONG

        sys.path.insert(0, str(ROOT / "apps" / "benchmark-cli" / "src"))
        from benchmark_cli import fetch_cloud_cover

        lon0, lat0, lon1, lat1 = fetch_cloud_cover.BBOX["mekong"]
        self.assertEqual(f"{lon0},{lat0},{lon1},{lat1}", BBOX_MEKONG)

        source = Path(tools.__file__).read_text()
        self.assertIn(f'"corridor_bbox": "{BBOX_MEKONG}"', source)


if __name__ == "__main__":
    unittest.main()
