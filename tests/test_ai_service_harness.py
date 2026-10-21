"""Integration & unit tests for the FLARE-CHRONOS Dual-System LangGraph Harness (`apps/ai-service`)."""

from __future__ import annotations

import json
import os
import sys
import tempfile
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
    MissingEndpointCredentialError,
    load_harness_config,
    resolve_api_key,
    resolve_endpoint_profile,
)
from ai_service.run_all_usecases import USE_CASE_BENCHMARK_QUERIES
from ai_service.schemas import (
    CognitivePath,
    UseCaseId,
    VerifiedFactsLedger,
    collect_citation_keys,
    resolve_citations,
    verify_grounded_draft,
)
from ai_service.tools import ALL_DETERMINISTIC_TOOLS, TOOL_MAP, USE_CASE_PRIMARY_TOOLS


class TestFlareChronosDualSystemHarness(unittest.TestCase):
    """Verify the LangGraph Dual-System Harness, 23 Tools, 20 Use Cases, and Symbiosis."""

    def test_01_harness_config_declares_explicit_endpoint_profiles(self) -> None:
        cfg = load_harness_config()
        s1_cfg = cfg["models"]["system1_reflexive"]
        s2_cfg = cfg["models"]["system2_deliberative"]

        self.assertEqual(s1_cfg["protocol"], "typed_questions")
        self.assertEqual(s1_cfg["api_key_env"], "SYSTEM1_API_KEY")
        self.assertTrue(s1_cfg["endpoint"].startswith("https://"))
        self.assertTrue(s1_cfg["model_id"])

        self.assertEqual(s2_cfg["protocol"], "native_chat")
        self.assertEqual(s2_cfg["api_key_env"], "SYSTEM2_API_KEY")
        self.assertTrue(s2_cfg["endpoint"].startswith("https://"))
        self.assertTrue(s2_cfg["model_id"])

        # Every request option must be a real field on the profile, and the
        # configured timeout must reach the client instead of a hardcoded value.
        s2_profile = resolve_endpoint_profile(cfg, "system2_deliberative")
        self.assertEqual(s2_profile.protocol, "native_chat")
        self.assertEqual(s2_profile.request.timeout_ms, 300000)
        self.assertEqual(s2_profile.request.temperature, 0.0)
        self.assertEqual(s2_profile.request.max_output_tokens, 65536)
        self.assertIsNotNone(s2_profile.request.thinking_level)

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
                self.assertEqual(ver.get("unresolved_citations"), [])
                self.assertGreater(len(out.get("verified_ledger_entries", [])), 0)
                if not uc_enum.value.startswith("UC-S1."):
                    self.assertEqual(
                        out.get("cognitive_path"),
                        CognitivePath.SYSTEM2_DELIBERATIVE.value,
                    )
                    self.assertGreaterEqual(len(out.get("reasoning_trace", [])), 1)
                    self.assertEqual(out.get("synthesis_mode"), "deterministic")

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

        langgraph_json = json.loads(
            (REPO_ROOT / "apps" / "ai-service" / "langgraph.json").read_text(
                encoding="utf-8"
            )
        )
        entrypoint = langgraph_json["graphs"]["flare_chronos_dual_system"]
        self.assertTrue(entrypoint.endswith(":build_dual_system_graph"))

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

    def test_09_endpoint_profile_precedence_is_environment_then_dotenv_then_config(
        self,
    ) -> None:
        cfg = load_harness_config()
        with tempfile.TemporaryDirectory() as tmp:
            env_file = Path(tmp) / ".env"
            env_file.write_text(
                "SYSTEM2_ENDPOINT=https://from-dotenv.example/v1\n"
                "SYSTEM2_MODEL=model-from-dotenv\n",
                encoding="utf-8",
            )

            # 1. Config is the fallback when nothing is exported.
            os.environ.pop("SYSTEM2_ENDPOINT", None)
            os.environ.pop("SYSTEM2_MODEL", None)
            profile = resolve_endpoint_profile(
                cfg, "system2_deliberative", env_file=env_file
            )
            self.assertEqual(profile.endpoint, "https://from-dotenv.example/v1")
            self.assertEqual(profile.model_id, "model-from-dotenv")

            # 2. The process environment wins over the workspace .env file.
            os.environ["SYSTEM2_ENDPOINT"] = "https://from-environment.example/v1"
            os.environ["SYSTEM2_MODEL"] = "model-from-environment"
            try:
                profile = resolve_endpoint_profile(
                    cfg, "system2_deliberative", env_file=env_file
                )
                self.assertEqual(
                    profile.endpoint, "https://from-environment.example/v1"
                )
                self.assertEqual(profile.model_id, "model-from-environment")
            finally:
                os.environ.pop("SYSTEM2_ENDPOINT", None)
                os.environ.pop("SYSTEM2_MODEL", None)

    def test_10_missing_api_key_fails_before_any_network_call(self) -> None:
        cfg = load_harness_config()
        profile = resolve_endpoint_profile(cfg, "system2_deliberative")
        os.environ.pop(profile.api_key_env, None)
        with (
            tempfile.TemporaryDirectory() as tmp,
            self.assertRaises(MissingEndpointCredentialError) as ctx,
        ):
            resolve_api_key(profile, env_file=Path(tmp) / "absent.env")
        self.assertIn(profile.api_key_env, str(ctx.exception))

    def test_11_citation_placeholder_resolution_and_grounding_error(self) -> None:
        payload = {
            "harmonized_index_2005_eq_100": 94.2,
            "total_raw_detections": 50988,
            "nested": {"divergence_pct": 1330.0},
        }
        citations = collect_citation_keys(payload)
        self.assertEqual(citations["harmonized_index_2005_eq_100"], 94.2)
        self.assertEqual(citations["total_raw_detections"], 50988.0)
        self.assertEqual(citations["nested.divergence_pct"], 1330.0)

        resolved, unresolved = resolve_citations(
            "Index {{harmonized_index_2005_eq_100}} from {{total_raw_detections}}.",
            citations,
        )
        self.assertEqual(unresolved, [])
        self.assertIn("94.2", resolved)
        self.assertIn("50988", resolved)

        ledger = VerifiedFactsLedger()
        ledger.ingest_tool_payload("tool_test", payload)
        _, report = verify_grounded_draft(
            "Index {{harmonized_index_2005_eq_100}} rose by {{invented_metric}}.",
            ledger,
        )
        self.assertFalse(report.passed)
        self.assertEqual(report.unresolved_citations, ["invented_metric"])

    def test_12_no_ambient_agent_tooling_configuration_is_read(self) -> None:
        """Guard against reintroducing reads of the host's agent tooling config."""
        forbidden = (
            "opencode.jsonc",
            "auth.json",
            ".config/opencode",
            ".local/share/opencode",
        )
        source_root = REPO_ROOT / "apps" / "ai-service" / "src" / "ai_service"
        offenders: list[str] = []
        for path in sorted(source_root.glob("*.py")):
            text = path.read_text(encoding="utf-8")
            for needle in forbidden:
                if needle in text:
                    offenders.append(f"{path.name}: {needle}")
        self.assertEqual(offenders, [], msg=f"ambient config reads found: {offenders}")

    def test_13_provider_names_are_absent_from_the_harness_source(self) -> None:
        """The harness must stay switchable: no vendor name in code or config."""
        forbidden = ("opencode", "ollama", "jev-", "qwen", "deepseek", "beam")
        source_root = REPO_ROOT / "apps" / "ai-service" / "src" / "ai_service"
        offenders: list[str] = []
        for path in sorted(source_root.glob("*.py")):
            text = path.read_text(encoding="utf-8").lower()
            for needle in forbidden:
                if needle in text:
                    offenders.append(f"{path.name}: {needle}")
        self.assertEqual(offenders, [], msg=f"provider names found: {offenders}")


if __name__ == "__main__":
    unittest.main()
