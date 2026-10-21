"""Vertical TDD Integration Suite at Confirmed Public Seams (Real Data + Live Models).

Follows the `tdd` skill (`Red -> Green` vertical slices, zero internal mocks,
independent literal expectations, domain vocabulary from `GLOSSARY.md` and `apps/ai-service/GLOSSARY.md`).

These tests call a real hosted language model, so they are marked `live` and
excluded from the default suite. Run them explicitly:

    pytest -m live

They are triggered by the manual `live-tests.yml` GitHub Actions workflow so
that model spend never happens on a push or a pull request.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
for pkg_src in (
    REPO_ROOT / "apps" / "ai-service" / "src",
    REPO_ROOT / "packages" / "harmonization-core" / "src",
):
    if str(pkg_src) not in sys.path:
        sys.path.insert(0, str(pkg_src))

from ai_service.harness import FlareChronosDualSystemHarness
from ai_service.models import load_harness_config, resolve_endpoint_profile
from ai_service.schemas import CognitivePath, UseCaseId


@pytest.mark.live
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
        self.assertEqual(out["verification_report"]["unresolved_citations"], [])
        self.assertIn("94.2", out["final_briefing"])

        # The System 1 classifier answers with a structured classification and
        # the harness records it in the run state.
        classification = out["triage_classification"]
        configured_model = resolve_endpoint_profile(
            load_harness_config(), "system1_reflexive"
        ).model_id
        self.assertEqual(classification["model"], configured_model)
        self.assertEqual(classification["answers"]["region"]["choice"], "mekong")
        # A single-hop lookup is not a deliberative request, so the classifier
        # routes it to the fast tier.
        self.assertEqual(out["cognitive_tier"], "fast")
        self.assertLessEqual(out["triage_confidence"]["is_deliberative"], 0.5)

    def test_slice_3_live_system2_deliberative_attribution_seam_with_reasoning_trace(
        self,
    ) -> None:
        """[Seam 2] Live System 2 model executes deliberative attribution with reasoning_trace and verified ledger."""
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
        self.assertGreaterEqual(out_uc11["live_telemetry"]["system2_calls"], 2)
        configured_model = resolve_endpoint_profile(
            load_harness_config(), "system2_deliberative"
        ).model_id
        self.assertEqual(out_uc11["live_telemetry"]["system2_model"], configured_model)

        # The narrative is authored by the model and every number in it is
        # traceable to the Verified Facts Ledger.
        self.assertEqual(out_uc11["synthesis_mode"], "llm")
        self.assertNotIn("{{", out_uc11["final_briefing"])

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
        # Part A: Live System 1 escalates to Live System 2 when divergence = 1330.0% >= 200%
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
        self.assertGreaterEqual(out_esc["live_telemetry"]["system1_calls"], 1)
        self.assertGreaterEqual(out_esc["live_telemetry"]["system2_calls"], 1)
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
        self.assertGreaterEqual(out_repair["self_correction_retries"], 1)
        self.assertTrue(
            out_repair["verification_report"]["passed"],
            msg=out_repair["verification_report"],
        )
        self.assertNotIn("98765.4321", out_repair["final_briefing"])
        self.assertIn("94.2", out_repair["final_briefing"])

    def test_slice_5_live_sign_off_gate_pauses_the_run_and_publishes_only_on_approval(
        self,
    ) -> None:
        """[Seam 5] A field-authorizing briefing waits for a human on a live run."""
        from langgraph.types import Command

        harness = FlareChronosDualSystemHarness(
            mode="live", enable_cache=False, enable_sign_off=True
        )

        def run_until_pause(thread_id: str) -> dict:
            harness.invoke_use_case(
                user_query=(
                    "UC-S1.4 Generate flash NRT tactical ranger alert for amazon in 2026."
                ),
                use_case_id=UseCaseId.UC_S1_4_FLASH_NRT_ALERT,
                thread_id=thread_id,
            )
            snapshot = harness.graph.get_state(
                {"configurable": {"thread_id": thread_id}}
            )
            self.assertTrue(snapshot.interrupts)
            request = snapshot.interrupts[0].value
            self.assertEqual(request["kind"], "sign_off")
            self.assertEqual(request["use_case_id"], "UC-S1.4")
            # The evidence the human decides on is the verified briefing.
            self.assertIn("final_briefing", request["evidence"])
            return request

        declined_thread = "tdd-live-slice-5-declined"
        run_until_pause(declined_thread)
        declined = harness.graph.invoke(
            Command(resume={"approved": False, "reason": "duplicate alert"}),
            {"configurable": {"thread_id": declined_thread}},
        )
        self.assertFalse(declined["sign_off_decision"]["approved"])
        self.assertEqual(declined["final_briefing"], "")
        self.assertEqual(declined["synthesis_mode"], "sign_off_declined")

        approved_thread = "tdd-live-slice-5-approved"
        run_until_pause(approved_thread)
        approved = harness.graph.invoke(
            Command(
                resume={
                    "approved": True,
                    "reason": "verified on the ground",
                    "decided_by": "ranger-01",
                }
            ),
            {"configurable": {"thread_id": approved_thread}},
        )
        decision = approved["sign_off_decision"]
        self.assertTrue(decision["approved"])
        self.assertEqual(decision["decided_by"], "ranger-01")
        self.assertIn("TIER_1_ACTIVE_MONITORING", approved["final_briefing"])
        # The released briefing carries no number that a tool did not produce.
        self.assertTrue(
            approved["verification_report"]["passed"],
            msg=approved["verification_report"],
        )

    def test_slice_6_live_classifier_assigns_the_analysis_to_a_free_form_request(
        self,
    ) -> None:
        """[Seam 6] A request that names no use case is assigned the right one."""
        harness = FlareChronosDualSystemHarness(mode="live", enable_cache=False)
        cases = [
            (
                "Audit the orbital drift of Terra and Aqua from 2001 to 2026 in the Mekong.",
                UseCaseId.UC_4_1_ORBITAL_DRIFT_SZA_AUDIT,
                "mekong",
            ),
            (
                "What is the harmonized fire index for the Amazon in 2024?",
                UseCaseId.UC_S1_3_SINGLE_HOP_LOOKUP,
                "amazon",
            ),
        ]
        for index, (query, expected_use_case, expected_region) in enumerate(cases):
            out = harness.invoke_use_case(
                user_query=query,
                thread_id=f"tdd-live-slice-6-{index}",
            )
            entity = out["extracted_entity"]
            self.assertEqual(entity["use_case_id"], expected_use_case.value)
            self.assertEqual(entity["region"], expected_region)
            # The assigned analysis decides the tier, not the other way round.
            expected_tier = (
                "fast"
                if expected_use_case.value.startswith("UC-S1")
                else "deliberative"
            )
            self.assertEqual(out["cognitive_tier"], expected_tier)
            self.assertEqual(out["triage_fallback"], "")


if __name__ == "__main__":
    unittest.main()
