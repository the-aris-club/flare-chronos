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
    SpatioTemporalQueryEntity,
    StakeholderTier,
    UseCaseId,
    VerifiedFactsLedger,
    collect_citable_facts,
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

        self.assertEqual(s1_cfg["protocol"], "native_chat")
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
        citations = collect_citable_facts(payload)
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

    def test_14_tool_tiers_partition_the_registry(self) -> None:
        """The Atomic and Domain Diagnostic tiers cover the registry exactly."""
        from ai_service.tools import ATOMIC_TOOLS, DOMAIN_DIAGNOSTIC_TOOLS

        atomic = {tool.name for tool in ATOMIC_TOOLS}
        diagnostic = {tool.name for tool in DOMAIN_DIAGNOSTIC_TOOLS}
        registered = {tool.name for tool in ALL_DETERMINISTIC_TOOLS}
        self.assertEqual(atomic | diagnostic, registered)
        self.assertEqual(atomic & diagnostic, set())
        self.assertEqual(len(registered), 23)

    def test_15_raw_firms_harmoniser_is_outside_the_model_registry(self) -> None:
        """The raw CSV harmoniser stays unreachable by the model."""
        from ai_service.tools import tool_harmonize_real_firms_csv_slice

        registered = {tool.name for tool in ALL_DETERMINISTIC_TOOLS}
        self.assertNotIn(tool_harmonize_real_firms_csv_slice.name, registered)

    def test_16_fast_tier_surface_excludes_domain_diagnostic_tools(self) -> None:
        """The tier that reports can never reach a derivation."""
        from ai_service.tools import ATOMIC_TOOLS, DOMAIN_DIAGNOSTIC_TOOLS

        harness = FlareChronosDualSystemHarness(
            mode="deterministic", enable_cache=False
        )
        atomic = {tool.name for tool in ATOMIC_TOOLS}
        diagnostic = {tool.name for tool in DOMAIN_DIAGNOSTIC_TOOLS}

        fast_surface = harness._fast_tier_tools("UC-S1.4")
        self.assertTrue(fast_surface)
        self.assertTrue(set(fast_surface) <= atomic)
        self.assertEqual(set(fast_surface) & diagnostic, set())

        deliberative_surface = harness._deliberative_tools("UC-1.1")
        self.assertTrue(set(deliberative_surface) & diagnostic)
        self.assertIn("ask_user_question", deliberative_surface)

    def test_17_system1_classification_drives_the_cognitive_tier(self) -> None:
        """The tier comes from the calibrated classification, not from a regex."""
        harness = FlareChronosDualSystemHarness(
            mode="deterministic", enable_cache=False
        )

        fast = harness.invoke_use_case(
            "UC-S1.3 Fast single-hop metric lookup for 2024 mekong.",
            use_case_id=UseCaseId.UC_S1_3_SINGLE_HOP_LOOKUP,
            thread_id="tier-fast",
        )
        self.assertEqual(fast.get("cognitive_tier"), "fast")
        self.assertGreater(fast.get("triage_confidence", {}).get("region", 0), 0.0)
        self.assertEqual(
            fast.get("triage_classification", {}).get("model"),
            harness.s1_profile.model_id,
        )

        deliberative = harness.invoke_use_case(
            "UC-1.1 Decompose the 2005 to 2024 fire regime shift in mekong.",
            use_case_id=UseCaseId.UC_1_1_REGIME_SHIFT_ATTRIBUTION,
            thread_id="tier-deliberative",
        )
        self.assertEqual(deliberative.get("cognitive_tier"), "deliberative")
        self.assertGreater(
            deliberative.get("triage_confidence", {}).get("is_deliberative", 0), 0.5
        )

    def test_18_sign_off_pauses_the_run_and_resumes_with_the_decision(self) -> None:
        """A use case that authorizes an action pauses for a human."""
        from langgraph.types import Command

        harness = FlareChronosDualSystemHarness(
            mode="deterministic", enable_cache=False, enable_sign_off=True
        )
        thread_id = "sign-off-approve"
        harness.invoke_use_case(
            "UC-S1.4 Generate flash NRT tactical ranger alert for amazon in 2026.",
            use_case_id=UseCaseId.UC_S1_4_FLASH_NRT_ALERT,
            thread_id=thread_id,
        )
        snapshot = harness.graph.get_state({"configurable": {"thread_id": thread_id}})
        self.assertTrue(snapshot.interrupts)
        request = snapshot.interrupts[0].value
        self.assertEqual(request["kind"], "sign_off")
        self.assertEqual(request["use_case_id"], "UC-S1.4")
        self.assertIn("final_briefing", request["evidence"])

        resumed = harness.graph.invoke(
            Command(
                resume={
                    "approved": True,
                    "reason": "verified on the ground",
                    "decided_by": "ranger-01",
                }
            ),
            {"configurable": {"thread_id": thread_id}},
        )
        decision = resumed["sign_off_decision"]
        self.assertTrue(decision["approved"])
        self.assertEqual(decision["decided_by"], "ranger-01")
        self.assertIn("TIER_1_ACTIVE_MONITORING", resumed["final_briefing"])

    def test_19_rejected_sign_off_releases_no_briefing(self) -> None:
        """A declined action publishes nothing, and the decision is still recorded."""
        from langgraph.types import Command

        harness = FlareChronosDualSystemHarness(
            mode="deterministic", enable_cache=False, enable_sign_off=True
        )
        thread_id = "sign-off-reject"
        harness.invoke_use_case(
            "UC-S1.4 Generate flash NRT tactical ranger alert for amazon in 2026.",
            use_case_id=UseCaseId.UC_S1_4_FLASH_NRT_ALERT,
            thread_id=thread_id,
        )
        resumed = harness.graph.invoke(
            Command(resume={"approved": False, "reason": "duplicate alert"}),
            {"configurable": {"thread_id": thread_id}},
        )
        decision = resumed["sign_off_decision"]
        self.assertFalse(decision["approved"])
        self.assertEqual(decision["reason"], "duplicate alert")
        self.assertEqual(resumed["final_briefing"], "")
        self.assertEqual(resumed["synthesis_mode"], "sign_off_declined")

    def test_20_event_stream_and_sse_frames(self) -> None:
        """The run is observable as typed events and encodable as SSE frames."""
        import asyncio

        from ai_service.events import HarnessEvent, to_sse_frames

        async def collect() -> list[HarnessEvent]:
            harness = FlareChronosDualSystemHarness(
                mode="deterministic", enable_cache=False
            )
            return [
                event
                async for event in harness.astream_use_case(
                    "UC-S1.3 Fast single-hop metric lookup for 2024 mekong.",
                    use_case_id=UseCaseId.UC_S1_3_SINGLE_HOP_LOOKUP,
                    thread_id="event-stream",
                )
            ]

        events = asyncio.run(collect())
        types = [event.type for event in events]
        self.assertEqual(types[0], "run_started")
        self.assertIn("node_completed", types)
        self.assertIn("verification", types)
        self.assertIn("briefing", types)
        self.assertEqual(types[-1], "run_completed")

        frame = events[0].to_sse()
        self.assertTrue(frame.startswith(b"event: run_started\ndata: {"))
        self.assertTrue(frame.endswith(b"\n\n"))

        async def frames() -> list[bytes]:
            harness = FlareChronosDualSystemHarness(
                mode="deterministic", enable_cache=False
            )
            return [
                frame
                async for frame in to_sse_frames(
                    harness.astream_use_case(
                        "UC-S1.3 Fast single-hop metric lookup for 2024 mekong.",
                        use_case_id=UseCaseId.UC_S1_3_SINGLE_HOP_LOOKUP,
                        thread_id="sse-frames",
                    )
                )
            ]

        encoded = asyncio.run(frames())
        self.assertTrue(encoded)
        self.assertTrue(all(b"event: " in frame for frame in encoded))

    def test_21_citation_placeholder_forms_and_leftovers(self) -> None:
        """One or two braces both resolve; a leftover placeholder fails the report."""
        ledger = VerifiedFactsLedger()
        ledger.ingest_tool_payload("tool_test", {"harmonized_index": 94.2})

        for draft in (
            "Index {{harmonized_index}} rose.",
            "Index {harmonized_index} rose.",
        ):
            resolved, report = verify_grounded_draft(draft, ledger)
            self.assertIn("94.2", resolved)
            self.assertTrue(report.passed)
            self.assertEqual(report.unresolved_citations, [])

        _, report = verify_grounded_draft("Index {{invented_metric}} rose.", ledger)
        self.assertFalse(report.passed)
        self.assertEqual(report.unresolved_citations, ["invented_metric"])

    def test_22_clarification_tool_is_outside_the_deterministic_registry(self) -> None:
        """The clarification tool interrupts the run; it is not a data tool."""
        from ai_service.human_input import ask_user_question

        registered = {tool.name for tool in ALL_DETERMINISTIC_TOOLS}
        self.assertNotIn(ask_user_question.name, registered)
        self.assertIn("question", ask_user_question.description)

    def test_23_identifier_digits_are_not_quantitative_claims(self) -> None:
        """A satellite name carries digits that must not be read as a claim."""
        ledger = VerifiedFactsLedger()
        ledger.ingest_tool_payload("tool_test", {"harmonized_index": 94.2})
        for draft in (
            "Retiring NOAA-20 and NOAA-21 leaves the index at 94.2.",
            "The Sentinel-2 record shows 94.2.",
        ):
            _, report = verify_grounded_draft(draft, ledger)
            self.assertTrue(report.passed, msg=report.unverified_numbers)
            self.assertEqual(report.unverified_numbers, [])

    def test_24_boolean_findings_are_citable(self) -> None:
        """A boolean finding may be cited, not only a number."""
        payload = {
            "use_case_id": "UC-1.2",
            "observed_viirs_cluster_frp_mw": 18.5,
            "explained_by_modis_offnadir_blindness": True,
            "is_saa_nighttime_false_alarm": False,
        }
        facts = collect_citable_facts(payload)
        self.assertIs(facts["explained_by_modis_offnadir_blindness"], True)
        self.assertIs(facts["is_saa_nighttime_false_alarm"], False)

        ledger = VerifiedFactsLedger()
        ledger.ingest_tool_payload("tool_test", payload)
        resolved, report = verify_grounded_draft(
            "The gap is explained by {{explained_by_modis_offnadir_blindness}} at "
            "{{observed_viirs_cluster_frp_mw}} MW, and SAA is "
            "{{is_saa_nighttime_false_alarm}}.",
            ledger,
            extra_facts=facts,
        )
        self.assertTrue(report.passed, msg=report.unverified_numbers)
        self.assertEqual(report.unresolved_citations, [])
        self.assertIn("true", resolved)
        self.assertIn("18.5", resolved)

    def test_25_a_draft_without_any_fact_is_rejected(self) -> None:
        """A briefing that cites nothing and states no quantity must not pass."""
        ledger = VerifiedFactsLedger()
        ledger.ingest_tool_payload("tool_test", {"harmonized_index": 94.2})
        _, report = verify_grounded_draft(
            "The fire situation is unclear and needs more investigation.",
            ledger,
        )
        self.assertFalse(report.passed)
        self.assertIn("cites no fact", report.feedback_message)

    def test_26_a_draft_that_cites_a_fact_passes(self) -> None:
        """A briefing that cites a fact passes even without a bare number."""
        ledger = VerifiedFactsLedger()
        ledger.ingest_tool_payload("tool_test", {"harmonized_index": 94.2})
        _, report = verify_grounded_draft(
            "The harmonized index is {{harmonized_index}}.",
            ledger,
        )
        self.assertTrue(report.passed, msg=report.feedback_message)

    def test_27_the_classification_channel_is_outside_the_data_registry(self) -> None:
        """The classification tool is a channel to the harness, not a data tool."""
        from ai_service.classification import classify_request

        registered = {tool.name for tool in ALL_DETERMINISTIC_TOOLS}
        self.assertNotIn(classify_request.name, registered)
        from langchain_core.utils.function_calling import convert_to_openai_tool

        parameters = convert_to_openai_tool(classify_request)["function"]["parameters"][
            "properties"
        ]
        self.assertEqual(
            set(parameters),
            {
                "region",
                "is_deliberative",
                "urgency",
                "use_case",
                "confidence",
                "focus_epoch",
            },
        )

    def test_29_the_analysis_menu_covers_every_use_case(self) -> None:
        """The classifier can name every analysis the registry defines."""
        from ai_service.classification import USE_CASE_MENU

        self.assertEqual(set(USE_CASE_MENU), {uc.value for uc in UseCaseId})
        for use_case, description in USE_CASE_MENU.items():
            self.assertTrue(description.strip(), msg=use_case)

    def test_30_the_classifier_assigns_the_analysis_when_none_is_named(self) -> None:
        """A request with no use case gets the analysis the classifier names."""
        from ai_service.classification import classification_answers

        payload = classification_answers(
            {
                "region": "mekong",
                "is_deliberative": True,
                "urgency": False,
                "use_case": "UC-4.1",
                "confidence": 0.9,
            },
            "model-x",
        )
        self.assertEqual(payload["answers"]["use_case"]["choice"], "UC-4.1")

        harness = FlareChronosDualSystemHarness(
            mode="deterministic", enable_cache=False, enable_sign_off=False
        )
        provisional = harness._extract_entity("audit the orbital drift in the Mekong")
        answers = payload["answers"]
        entity, _confidence, tier = harness._refine_entity(
            provisional, answers, explicit_use_case=False
        )
        self.assertEqual(entity.use_case_id.value, "UC-4.1")
        self.assertEqual(tier, "deliberative")

    def test_31_a_named_use_case_beats_the_classifier(self) -> None:
        """An explicit use case always wins over the assigned analysis."""
        from ai_service.classification import classification_answers

        harness = FlareChronosDualSystemHarness(
            mode="deterministic", enable_cache=False, enable_sign_off=False
        )
        provisional = harness._extract_entity(
            "audit the orbital drift in the Mekong",
            UseCaseId.UC_2_2_TACTICAL_DISPATCH,
        )
        answers = classification_answers(
            {
                "region": "mekong",
                "is_deliberative": True,
                "urgency": False,
                "use_case": "UC-4.1",
                "confidence": 0.9,
            },
            "model-x",
        )["answers"]
        entity, _confidence, tier = harness._refine_entity(
            provisional, answers, explicit_use_case=True
        )
        self.assertEqual(entity.use_case_id.value, "UC-2.2")
        self.assertEqual(tier, "deliberative")

    def test_28_classification_answers_match_the_typed_questions_shape(self) -> None:
        """Both protocols answer the harness in the same shape."""
        from ai_service.classification import classification_answers

        payload = classification_answers(
            {
                "region": "Amazon",
                "is_deliberative": True,
                "urgency": False,
                "focus_epoch": 2019,
                "confidence": 0.8,
            },
            "model-x",
        )
        answers = payload["answers"]
        self.assertEqual(payload["confidence_source"], "self_reported")
        self.assertEqual(answers["region"]["choice"], "amazon")
        self.assertEqual(answers["region"]["confidence"], 0.8)
        self.assertEqual(answers["is_deliberative"]["noul"], 1.0)
        self.assertEqual(answers["urgency"]["noul"], 0.0)
        self.assertEqual(answers["focus_epoch"]["choice"], "2019")

    def test_32_a_paused_run_survives_a_process_restart(self) -> None:
        """A run waiting for a human resumes from disk, not from memory."""
        from ai_service.harness import build_sqlite_checkpointer
        from langgraph.types import Command

        with tempfile.TemporaryDirectory() as tmp:
            checkpoint_path = Path(tmp) / "checkpoints.sqlite"
            thread_id = "durable-sign-off"

            first = FlareChronosDualSystemHarness(
                mode="deterministic",
                enable_cache=False,
                enable_sign_off=True,
                checkpointer=build_sqlite_checkpointer(checkpoint_path),
            )
            first.invoke_use_case(
                "UC-S1.4 Generate flash NRT tactical ranger alert for amazon in 2026.",
                use_case_id=UseCaseId.UC_S1_4_FLASH_NRT_ALERT,
                thread_id=thread_id,
            )
            snapshot = first.graph.get_state({"configurable": {"thread_id": thread_id}})
            self.assertTrue(snapshot.interrupts)

            # A new harness on the same file stands in for a restarted process.
            second = FlareChronosDualSystemHarness(
                mode="deterministic",
                enable_cache=False,
                enable_sign_off=True,
                checkpointer=build_sqlite_checkpointer(checkpoint_path),
            )
            resumed = second.graph.invoke(
                Command(resume={"approved": True, "reason": "confirmed"}),
                {"configurable": {"thread_id": thread_id}},
            )
            self.assertTrue(resumed["sign_off_decision"]["approved"])
            self.assertIn("TIER_1_ACTIVE_MONITORING", resumed["final_briefing"])

    def test_31_every_stakeholder_tier_reaches_the_narrative_guidance(self) -> None:
        """Each tier's guidance reaches the model, not only the generic fallback."""
        from ai_service.prompts import system2_system_prompt
        from ai_service.schemas import StakeholderTier

        expected = {
            StakeholderTier.FIELD_RANGER: "operational implication",
            StakeholderTier.FORESTRY_EXECUTIVE: "policy consequence",
            StakeholderTier.CLIMATE_SCIENTIST: "name every assumption",
        }
        for tier, marker in expected.items():
            prompt = system2_system_prompt(
                entity=self._entity_for_tier(tier),
                requested_use_case="UC-2.2",
                tier=tier.value,
            )
            self.assertIn(marker, prompt)
            self.assertNotIn("a technical reader", prompt)

    def _entity_for_tier(self, tier: StakeholderTier) -> SpatioTemporalQueryEntity:
        return SpatioTemporalQueryEntity(
            use_case_id=UseCaseId.UC_2_2_TACTICAL_DISPATCH,
            cognitive_path=CognitivePath.SYSTEM2_DELIBERATIVE.value,
            region="mekong",
            epoch_years=[2024],
            pentad_range=(11, 22),
            h3_resolution=7,
            stakeholder_tier=tier,
            urgency_level="nominal",
        )

    def test_29_an_unsupported_deliberation_level_does_not_lose_the_run(self) -> None:
        """A model that refuses the configured thinking level still answers."""
        from ai_service import models as models_module
        from ai_service.models import EndpointProfile, NativeChatModel, RequestOptions

        profile = EndpointProfile(
            protocol="native_chat",
            endpoint="https://example.invalid/api/chat",
            model_id="model-x",
            api_key_env="HARNESS_TEST_KEY",
            request=RequestOptions(
                timeout_ms=5000,
                thinking_level="xhigh",
                user_agent="flare-chronos/2.0.0",
            ),
        )
        model = NativeChatModel(
            role="system2_deliberative",
            model_id="model-x",
            source_label=profile.endpoint,
            reasoning_effort="low",
            profile=profile,
        )
        os.environ["HARNESS_TEST_KEY"] = "test-key"
        seen: list[dict] = []

        def fake_post(
            url: str, payload: dict, headers: dict, timeout_sec: float
        ) -> dict:
            seen.append(payload)
            if payload.get("think") == "xhigh":
                raise models_module.EndpointCallError(
                    'HTTP 400 from endpoint: {"error":"invalid think value: \\"xhigh\\""}',
                    400,
                )
            return {"message": {"role": "assistant", "content": "answer"}}

        original_post = models_module._post_json
        models_module._post_json = fake_post  # type: ignore[assignment]
        try:
            response = model._call(model._build_payload([], []))
        finally:
            models_module._post_json = original_post  # type: ignore[assignment]

        self.assertEqual(response["message"]["content"], "answer")
        self.assertEqual([p.get("think") for p in seen], ["xhigh", False])
        self.assertFalse(model.endpoint_state["thinking_level_supported"])

    def test_30_a_second_call_skips_the_level_the_endpoint_refused(self) -> None:
        """The refusal is remembered, so the next turn does not fail first."""
        from ai_service import models as models_module
        from ai_service.models import EndpointProfile, NativeChatModel, RequestOptions

        profile = EndpointProfile(
            protocol="native_chat",
            endpoint="https://example.invalid/api/chat",
            model_id="model-x",
            api_key_env="HARNESS_TEST_KEY",
            request=RequestOptions(
                timeout_ms=5000,
                thinking_level="xhigh",
                user_agent="flare-chronos/2.0.0",
            ),
        )
        model = NativeChatModel(
            role="system2_deliberative",
            model_id="model-x",
            source_label=profile.endpoint,
            reasoning_effort="low",
            profile=profile,
        )
        os.environ["HARNESS_TEST_KEY"] = "test-key"
        seen: list[dict] = []

        def fake_post(
            url: str, payload: dict, headers: dict, timeout_sec: float
        ) -> dict:
            seen.append(payload)
            if payload.get("think") == "xhigh":
                raise models_module.EndpointCallError(
                    'HTTP 400 from endpoint: {"error":"invalid think value"}', 400
                )
            return {"message": {"role": "assistant", "content": "answer"}}

        original_post = models_module._post_json
        models_module._post_json = fake_post  # type: ignore[assignment]
        try:
            model._call(model._build_payload([], []))
            model._call(model._build_payload([], []))
        finally:
            models_module._post_json = original_post  # type: ignore[assignment]

        self.assertEqual([p.get("think") for p in seen], ["xhigh", False, False])


if __name__ == "__main__":
    unittest.main()
