"""Integration & unit tests for the FLARE-CHRONOS Dual-System LangGraph Harness (`apps/ai-service`)."""

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

from ai_service.harness import FlareChronosDualSystemHarness, build_dual_system_graph
from ai_service.models import (
    load_harness_config,
    resolve_opencode_system1_credentials,
    resolve_qwen_system2_credentials,
)
from ai_service.run_all_usecases import USE_CASE_BENCHMARK_QUERIES
from ai_service.schemas import (
    CognitivePath,
    UseCaseId,
    VerifiedFactsLedger,
)
from ai_service.tools import ALL_DETERMINISTIC_TOOLS, TOOL_MAP, USE_CASE_PRIMARY_TOOLS


class TestFlareChronosDualSystemHarness(unittest.TestCase):
    """Verify the LangGraph Dual-System Harness, 23 Tools, 20 Use Cases, and Symbiosis."""

    def test_01_harness_config_and_model_endpoints(self) -> None:
        cfg = load_harness_config()
        s1_cfg = cfg["models"]["system1_reflexive"]
        s2_cfg = cfg["models"]["system2_deliberative"]

        self.assertEqual(s1_cfg["provider"], "opencode-v2")
        self.assertEqual(s1_cfg["model_id"], "jev-1.13-free")
        self.assertEqual(s1_cfg["model_alias"], "jev")
        self.assertEqual(s1_cfg["base_url"], "https://opencode.ai/zen/v1")
        self.assertEqual(
            s1_cfg["systemone_endpoint"], "https://opencode.ai/zen/v1/systemone"
        )

        self.assertEqual(s2_cfg["provider"], "qwen-local")
        self.assertEqual(s2_cfg["model_id"], "qwen3.8-flash-next")
        self.assertEqual(s2_cfg["base_url"], "http://100.67.91.54:8888/v1")
        self.assertEqual(s2_cfg["reasoning_effort"], "xhigh")
        self.assertEqual(
            s2_cfg["compatibility"]["reasoning_field"], "reasoning_content"
        )

        s1_url, s1_model, s1_key = resolve_opencode_system1_credentials(cfg)
        self.assertEqual(s1_url, "https://opencode.ai/zen/v1")
        self.assertEqual(s1_model, "jev-1.13-free")
        self.assertTrue(len(s1_key) > 0)

        s2_url, s2_model, s2_key = resolve_qwen_system2_credentials(cfg)
        self.assertEqual(s2_url, "http://100.67.91.54:8888/v1")
        self.assertEqual(s2_model, "qwen3.8-flash-next")
        self.assertTrue(len(s2_key) > 0)

    def test_02_tool_registry_completeness(self) -> None:
        self.assertEqual(len(ALL_DETERMINISTIC_TOOLS), 23)
        self.assertEqual(len(USE_CASE_PRIMARY_TOOLS), 20)
        for uc_id, tool_names in USE_CASE_PRIMARY_TOOLS.items():
            self.assertIsInstance(uc_id, UseCaseId)
            self.assertGreaterEqual(len(tool_names), 1)
            for t_name in tool_names:
                self.assertIn(t_name, TOOL_MAP)

    def test_03_all_20_use_cases_execute_and_pass_verification(self) -> None:
        harness = FlareChronosDualSystemHarness(
            mode="deterministic", enable_cache=False
        )
        self.assertEqual(len(USE_CASE_BENCHMARK_QUERIES), 20)

        for idx, (uc_enum, query) in enumerate(USE_CASE_BENCHMARK_QUERIES, start=1):
            with self.subTest(use_case=uc_enum.value):
                out = harness.invoke_use_case(
                    user_query=query,
                    use_case_id=uc_enum,
                    thread_id=f"test-uc-{idx:02d}",
                )
                ver = out.get("verification_report", {})
                self.assertTrue(
                    ver.get("passed"),
                    msg=f"{uc_enum.value} failed verification: {ver}",
                )
                self.assertEqual(ver.get("unverified_numbers"), [])
                self.assertGreater(len(out.get("verified_ledger_entries", [])), 0)
                if not uc_enum.value.startswith("UC-S1."):
                    self.assertEqual(
                        out.get("cognitive_path"),
                        CognitivePath.SYSTEM2_DELIBERATIVE.value,
                    )
                    self.assertGreaterEqual(len(out.get("reasoning_trace", [])), 1)

    def test_04_dynamic_s1_to_s2_escalation_on_physical_divergence(self) -> None:
        harness = FlareChronosDualSystemHarness(mode="deterministic", enable_cache=True)
        out = harness.invoke_use_case(
            user_query=(
                "UC-S1.3 Fast lookup for 2024 mekong ESCALATE_IF_CONFLICT "
                "when raw vs harmonized divergence exceeds 200%."
            ),
            use_case_id=UseCaseId.UC_S1_3_SINGLE_HOP_LOOKUP,
            thread_id="test-s1-s2-escalation",
        )
        self.assertEqual(
            out.get("cognitive_path"),
            CognitivePath.ESCALATED_S1_TO_S2.value,
        )
        self.assertTrue(out.get("escalated_from_system1"))
        self.assertIn(
            "tool_uc1_1_regime_shift_attribution", out.get("pruned_tool_names", [])
        )
        self.assertTrue(out.get("verification_report", {}).get("passed"))

    def test_05_numeric_grounding_verifier_rejects_and_self_corrects(self) -> None:
        harness = FlareChronosDualSystemHarness(
            mode="deterministic",
            inject_unverified_number_once=True,
            enable_cache=False,
        )
        out = harness.invoke_use_case(
            user_query="UC-1.1 Decompose the 2005 to 2024 fire regime shift in mekong.",
            use_case_id=UseCaseId.UC_1_1_REGIME_SHIFT_ATTRIBUTION,
            thread_id="test-verifier-loopback",
        )
        self.assertEqual(out.get("self_correction_retries"), 1)
        self.assertTrue(out.get("verification_report", {}).get("passed"))
        self.assertEqual(
            out.get("verification_report", {}).get("unverified_numbers"), []
        )
        self.assertNotIn("98765.4321", out.get("final_briefing", ""))

    def test_06_s2_to_s1_verified_pattern_cache_distillation(self) -> None:
        harness = FlareChronosDualSystemHarness(mode="deterministic", enable_cache=True)
        q = "UC-3.3 Audit the N=11553 Aqua-SNPP co-incident calibration transfer function."
        out1 = harness.invoke_use_case(
            user_query=q,
            use_case_id=UseCaseId.UC_3_3_BIOME_RECALIBRATION,
            thread_id="test-cache-1",
        )
        self.assertFalse(out1.get("distilled_cache_hit"))
        self.assertEqual(
            out1.get("cognitive_path"), CognitivePath.SYSTEM2_DELIBERATIVE.value
        )

        out2 = harness.invoke_use_case(
            user_query=q,
            use_case_id=UseCaseId.UC_3_3_BIOME_RECALIBRATION,
            thread_id="test-cache-2",
        )
        self.assertTrue(out2.get("distilled_cache_hit"))
        self.assertEqual(
            out2.get("cognitive_path"), CognitivePath.DISTILLED_CACHE_HIT.value
        )
        self.assertEqual(out1.get("final_briefing"), out2.get("final_briefing"))

    def test_07_langgraph_json_entrypoint(self) -> None:
        compiled_graph = build_dual_system_graph(mode="deterministic")
        self.assertIsNotNone(compiled_graph)

    def test_08_direct_ledger_rejection_unit_check(self) -> None:
        ledger = VerifiedFactsLedger()
        ledger.ingest_tool_payload(
            "tool_test", {"harmonized_index": 94.2, "omega": 2.0975}
        )
        good_report = ledger.verify_draft_text(
            "In 2024, the harmonized_index was 94.2 with effort omega 2.0975."
        )
        self.assertTrue(good_report.passed)
        bad_report = ledger.verify_draft_text(
            "In 2024, the harmonized_index was 94.2, which is a 412.9% increase."
        )
        self.assertFalse(bad_report.passed)
        self.assertIn(412.9, bad_report.unverified_numbers)


if __name__ == "__main__":
    unittest.main()
