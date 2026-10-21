"""Vertical TDD Integration Suite at Confirmed Public Seams (Real Data + Live Models).

Follows the `tdd` skill (`Red -> Green` vertical slices, zero internal mocks,
independent literal expectations, domain vocabulary from `GLOSSARY.md` and `apps/ai-service/GLOSSARY.md`).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
for pkg_src in (
    REPO_ROOT / "apps" / "ai-service" / "src",
    REPO_ROOT / "packages" / "harmonization-core" / "src",
):
    if str(pkg_src) not in sys.path:
        sys.path.insert(0, str(pkg_src))


class TestLiveDualSystemSeamsTDD(unittest.TestCase):
    """Vertical TDD tests across the 4 confirmed public seams."""

    def test_slice_1_real_firms_csv_harmonization_seam_preserves_physical_invariants(
        self,
    ) -> None:
        """[Seam 4] Harmonizing a real NASA FIRMS CSV slice from data/raw/ produces verified episodes."""
        from ai_service.tools import tool_harmonize_real_firms_csv_slice

        result = tool_harmonize_real_firms_csv_slice.invoke(
            {
                "slice_filename": "mekong__MODIS_SP__2024-03-15__5d.csv",
                "sample_limit": 500,
            }
        )

        # Independent known-good literals from NASA FIRMS 2024-03-15 Mekong MODIS_SP slice
        self.assertEqual(
            result["slice_filename"], "mekong__MODIS_SP__2024-03-15__5d.csv"
        )
        self.assertEqual(result["total_csv_rows"], 3446)
        self.assertEqual(result["evaluated_detections_count"], 500)
        self.assertGreater(result["reconstructed_fire_episodes_count"], 0)
        self.assertLess(result["reconstructed_fire_episodes_count"], 500)
        self.assertTrue(result["all_daytime_sza_below_85_deg"])
        self.assertTrue(result["all_probabilities_in_unit_interval"])
        self.assertEqual(result["h3_energy_conservation_weight_sum"], 1.0)

    def test_slice_2_live_system1_single_hop_lookup_seam_returns_verified_metrics(
        self,
    ) -> None:
        """[Seam 1] Live System 1 model invokes deterministic lookup tool and passes VerifiedFactsLedger."""
        from ai_service.harness import FlareChronosDualSystemHarness
        from ai_service.schemas import CognitivePath, UseCaseId

        harness = FlareChronosDualSystemHarness(mode="live", enable_cache=False)
        out = harness.invoke_use_case(
            user_query="UC-S1.3 Retrieve verified single-epoch metrics for 2024 in mekong.",
            use_case_id=UseCaseId.UC_S1_3_SINGLE_HOP_LOOKUP,
            thread_id="tdd-live-slice-2",
        )

        self.assertEqual(out["cognitive_path"], CognitivePath.SYSTEM1_FAST_LOOKUP.value)
        ledger_values = {
            round(float(e["numeric_value"]), 1) for e in out["verified_ledger_entries"]
        }
        # Independent known-good literals for Mekong 2024 from empirical_results.json
        self.assertIn(50988.0, ledger_values)
        self.assertIn(22557.0, ledger_values)
        self.assertIn(94.2, ledger_values)
        self.assertTrue(
            out["verification_report"]["passed"], msg=out["verification_report"]
        )
        self.assertEqual(out["verification_report"]["unverified_numbers"], [])
        self.assertIn("94.2", out["final_briefing"])

        # Verify live Jev 1.13 SystemOne structured decision telemetry on AIMessage
        jev_payloads = [
            m.additional_kwargs["jev_systemone"]
            for m in out["messages"]
            if getattr(m, "additional_kwargs", None)
            and "jev_systemone" in m.additional_kwargs
        ]
        self.assertGreaterEqual(len(jev_payloads), 2)
        self.assertEqual(jev_payloads[0]["model"], "jev-1.13-free")
        self.assertEqual(jev_payloads[0]["answers"]["region"]["choice"], "mekong")

    def test_slice_3_live_system2_deliberative_attribution_seam_with_reasoning_trace(
        self,
    ) -> None:
        """[Seam 2] Live System 2 model executes deliberative attribution with reasoning_trace and verified ledger."""
        from ai_service.harness import FlareChronosDualSystemHarness
        from ai_service.schemas import CognitivePath, UseCaseId

        harness = FlareChronosDualSystemHarness(mode="live", enable_cache=False)
        out_uc11 = harness.invoke_use_case(
            user_query="UC-1.1 Why did raw detections in mekong 2024 jump to 1424.2 while harmonized is 94.2?",
            use_case_id=UseCaseId.UC_1_1_REGIME_SHIFT_ATTRIBUTION,
            thread_id="tdd-live-slice-3-uc11",
        )

        self.assertEqual(
            out_uc11["cognitive_path"], CognitivePath.SYSTEM2_DELIBERATIVE.value
        )
        ledger_vals = {
            round(float(e["numeric_value"]), 3)
            for e in out_uc11["verified_ledger_entries"]
        }
        # Independent known-good literals for UC-1.1 (Mekong 2005 vs 2024 from empirical_results.json)
        self.assertIn(1424.2, ledger_vals)
        self.assertIn(1324.2, ledger_vals)
        self.assertIn(94.2, ledger_vals)
        self.assertIn(-5.8, ledger_vals)
        self.assertGreaterEqual(len(out_uc11["reasoning_trace"]), 2)
        self.assertIn("[Live System 2", out_uc11["reasoning_trace"][0])
        self.assertTrue(
            out_uc11["verification_report"]["passed"],
            msg=out_uc11["verification_report"],
        )
        self.assertGreaterEqual(
            out_uc11["live_telemetry"]["system2_reasoning_calls"], 2
        )
        self.assertIn(
            out_uc11["live_telemetry"]["system2_provider_used"],
            ("qwen-local/qwen3.8-flash-next", "9router/ds/deepseek-v4-pro"),
        )

        out_uc33 = harness.invoke_use_case(
            user_query="UC-3.3 Verify cross-sensor KS distance before and after harmonization.",
            use_case_id=UseCaseId.UC_3_3_BIOME_RECALIBRATION,
            thread_id="tdd-live-slice-3-uc33",
        )
        ledger_uc33 = {
            round(float(e["numeric_value"]), 3)
            for e in out_uc33["verified_ledger_entries"]
        }
        # Independent known-good KS distance literals from empirical_results.json (0.117 -> 0.024, 79.7% reduction)
        self.assertIn(0.117, ledger_uc33)
        self.assertIn(0.024, ledger_uc33)
        self.assertIn(79.7, ledger_uc33)
        self.assertIn(11553.0, ledger_uc33)
        self.assertTrue(
            out_uc33["verification_report"]["passed"],
            msg=out_uc33["verification_report"],
        )

    def test_slice_4_live_symbiosis_escalation_and_verifier_self_correction_seam(
        self,
    ) -> None:
        """[Seam 3] Live System 1 -> System 2 dynamic escalation on >=200% divergence & self-correction loop."""
        from ai_service.harness import FlareChronosDualSystemHarness
        from ai_service.schemas import CognitivePath, UseCaseId

        # Part A: Live System 1 (jev-1.13-free) escalates to Live System 2 when divergence = 1330.0% >= 200%
        harness_esc = FlareChronosDualSystemHarness(mode="live", enable_cache=False)
        out_esc = harness_esc.invoke_use_case(
            user_query=(
                "UC-S1.3 Quick lookup for 2024 mekong fire index; "
                "ESCALATE_IF_CONFLICT if raw vs harmonized divergence exceeds threshold."
            ),
            use_case_id=UseCaseId.UC_S1_3_SINGLE_HOP_LOOKUP,
            thread_id="tdd-live-slice-4-esc",
        )
        self.assertTrue(out_esc["escalated_from_system1"])
        self.assertEqual(
            out_esc["cognitive_path"], CognitivePath.ESCALATED_S1_TO_S2.value
        )
        self.assertIn("1330.0%", out_esc["escalation_reason"])
        self.assertGreaterEqual(out_esc["live_telemetry"]["system1_jev_calls"], 1)
        self.assertGreaterEqual(out_esc["live_telemetry"]["system2_reasoning_calls"], 2)
        self.assertTrue(
            out_esc["verification_report"]["passed"], msg=out_esc["verification_report"]
        )

        # Part B: Live System 2 NumericGroundingVerifier self-correction loop rejects unverified 98765.4321
        harness_repair = FlareChronosDualSystemHarness(
            mode="live",
            inject_unverified_number_once=True,
            enable_cache=False,
        )
        out_repair = harness_repair.invoke_use_case(
            user_query="UC-1.1 Attribute 2024 mekong regime shift with strict numeric verification.",
            use_case_id=UseCaseId.UC_1_1_REGIME_SHIFT_ATTRIBUTION,
            thread_id="tdd-live-slice-4-repair",
        )
        self.assertEqual(out_repair["self_correction_retries"], 1)
        self.assertTrue(
            out_repair["verification_report"]["passed"],
            msg=out_repair["verification_report"],
        )
        self.assertNotIn("98765.4321", out_repair["final_briefing"])
        self.assertIn("94.2", out_repair["final_briefing"])


if __name__ == "__main__":
    unittest.main()
