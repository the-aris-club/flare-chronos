"""LangGraph Dual-System Harness (`StateGraph` + `ToolNode` + `MemorySaver` + `VerifiedFactsLedger`).

Orchestrates:
- System 1 (`opencode-v2 / jev`): Reflexive Triage (`UC-S1.1`), Entity Extraction (`UC-S1.2`),
  Single-Hop Fast Lookup (`UC-S1.3`), Flash NRT Alert (`UC-S1.4`), and Multi-Stakeholder
  Synthesis (`UC-S1.5`).
- System 2 (`qwen-local / qwen3.8-flash-next`, `reasoning_effort="xhigh"`): 15 Deliberative
  Use Cases (`UC-1.1` through `UC-5.3`).
- Symbiosis:
  1. System 1 -> System 2 Context & Tool Pruning
  2. Dynamic Escalation Gate on Physical Conflict (`divergence >= 200%` or `saa_rejected_count > 0`)
  3. Deterministic `VerifiedFactsLedger` + `NumericGroundingVerifier` loopback edge
  4. System 2 -> System 1 `VerifiedPatternCache` distillation
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from ai_service.models import (
    DeterministicHarnessChatModel,
    build_live_system1_chat_model,
    build_live_system2_chat_model,
    load_harness_config,
)
from ai_service.schemas import (
    CognitivePath,
    HarnessState,
    SpatioTemporalQueryEntity,
    StakeholderTier,
    UseCaseId,
    VerifiedFactEntry,
    VerifiedFactsLedger,
)
from ai_service.tools import ALL_DETERMINISTIC_TOOLS, TOOL_MAP, USE_CASE_PRIMARY_TOOLS

SYSTEM_1_REFLEXIVE_USE_CASES = {
    UseCaseId.UC_S1_1_INTENT_TRIAGE,
    UseCaseId.UC_S1_2_ENTITY_EXTRACTION,
    UseCaseId.UC_S1_3_SINGLE_HOP_LOOKUP,
    UseCaseId.UC_S1_4_FLASH_NRT_ALERT,
    UseCaseId.UC_S1_5_STAKEHOLDER_SYNTHESIS,
}


class VerifiedPatternCache:
    """In-memory cache of System-2 verified templates distilled for System-1 fast retrieval."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    @staticmethod
    def make_key(use_case_id: str, year: int, region: str, tier: str) -> str:
        raw = f"{use_case_id}|{year}|{region}|{tier}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def get(self, key: str) -> dict[str, Any] | None:
        return self._store.get(key)

    def put(self, key: str, value: dict[str, Any]) -> None:
        self._store[key] = value

    def size(self) -> int:
        return len(self._store)


class FlareChronosDualSystemHarness:
    """Compiled LangGraph Dual-System Cognitive Harness for FLARE-CHRONOS."""

    def __init__(
        self,
        mode: Literal["deterministic", "live"] = "deterministic",
        inject_unverified_number_once: bool = False,
        enable_cache: bool = True,
    ) -> None:
        self.config = load_harness_config()
        self.mode = mode
        self.enable_cache = enable_cache
        self.pattern_cache = VerifiedPatternCache()
        self.checkpointer = MemorySaver()
        self.tool_node = ToolNode(ALL_DETERMINISTIC_TOOLS)

        s1_cfg = self.config["models"]["system1_reflexive"]
        s2_cfg = self.config["models"]["system2_deliberative"]

        if mode == "live":
            self.system1_model: BaseChatModel = build_live_system1_chat_model(
                self.config
            )
            self.system2_model: BaseChatModel = build_live_system2_chat_model(
                self.config,
                variant=s2_cfg.get("reasoning_effort", "xhigh"),
                inject_unverified_number_once=inject_unverified_number_once,
            )
        else:
            self.system1_model = DeterministicHarnessChatModel(
                role="system1_reflexive",
                model_id=s1_cfg["model_id"],
                provider_id=s1_cfg["provider"],
                reasoning_effort="low",
                inject_unverified_number_once=False,
            )
            self.system2_model = DeterministicHarnessChatModel(
                role="system2_deliberative",
                model_id=s2_cfg["model_id"],
                provider_id=s2_cfg["provider"],
                reasoning_effort=s2_cfg.get("reasoning_effort", "xhigh"),
                inject_unverified_number_once=inject_unverified_number_once,
            )

        self.graph = self._compile_state_graph()

    def _extract_entity(
        self, user_query: str, requested_use_case: UseCaseId | str | None = None
    ) -> SpatioTemporalQueryEntity:
        """System 1 (`UC-S1.1` & `UC-S1.2`): Extract structured spatio-temporal entity & route."""
        uc_enum = UseCaseId.UC_1_1_REGIME_SHIFT_ATTRIBUTION
        if isinstance(requested_use_case, UseCaseId):
            uc_enum = requested_use_case
        elif isinstance(requested_use_case, str):
            uc_enum = UseCaseId(requested_use_case)
        else:
            match_uc = re.search(r"(UC-(?:S1\.\d|\d\.\d))", user_query)
            if match_uc:
                uc_enum = UseCaseId(match_uc.group(1))

        years = sorted({int(y) for y in re.findall(r"\b(20[0-2]\d)\b", user_query)})
        if not years:
            years = [2005, 2024]

        lower_q = user_query.lower()
        region = (
            "amazon" if "amazon" in lower_q or "south_america" in lower_q else "mekong"
        )

        tier = StakeholderTier.CLIMATE_SCIENTIST
        if (
            "ranger" in lower_q
            or "tactical" in lower_q
            or uc_enum == UseCaseId.UC_S1_4_FLASH_NRT_ALERT
        ):
            tier = StakeholderTier.FIELD_RANGER
        elif "executive" in lower_q or "policy" in lower_q or "asean" in lower_q:
            tier = StakeholderTier.FORESTRY_EXECUTIVE

        is_s1 = uc_enum in SYSTEM_1_REFLEXIVE_USE_CASES
        if uc_enum == UseCaseId.UC_S1_4_FLASH_NRT_ALERT:
            c_path = CognitivePath.SYSTEM1_FLASH_ALERT
        elif is_s1:
            c_path = CognitivePath.SYSTEM1_FAST_LOOKUP
        else:
            c_path = CognitivePath.SYSTEM2_DELIBERATIVE

        urgency = (
            "flash_crisis"
            if "escalate_if_conflict" in lower_q
            or uc_enum == UseCaseId.UC_S1_4_FLASH_NRT_ALERT
            else "nominal"
        )

        return SpatioTemporalQueryEntity(
            use_case_id=uc_enum,
            cognitive_path=c_path,
            region=region,
            epoch_years=years,
            pentad_range=(11, 22),
            h3_resolution=8 if tier == StakeholderTier.FIELD_RANGER else 7,
            stakeholder_tier=tier,
            urgency_level=urgency,
        )

    def _system1_triage_node(self, state: HarnessState) -> dict[str, Any]:
        """Node 1 (`UC-S1.1` & `UC-S1.2`): System 1 Triage, Entity Extraction, Cache Lookup, Tool Pruning."""
        user_query = state.get("user_query", "")
        pre_entity = state.get("extracted_entity") or {}
        requested_uc = pre_entity.get("use_case_id")
        entity = self._extract_entity(user_query, requested_uc)
        uc_enum = entity.use_case_id
        target_year = entity.epoch_years[-1] if entity.epoch_years else 2024

        cache_key = VerifiedPatternCache.make_key(
            uc_enum.value,
            target_year,
            entity.region,
            entity.stakeholder_tier.value,
        )
        if self.enable_cache and entity.urgency_level != "flash_crisis":
            cached = self.pattern_cache.get(cache_key)
            if cached is not None:
                return {
                    "extracted_entity": entity.model_dump(),
                    "cognitive_path": CognitivePath.DISTILLED_CACHE_HIT.value,
                    "pruned_tool_names": cached["pruned_tool_names"],
                    "verified_ledger_entries": cached["verified_ledger_entries"],
                    "verification_report": cached["verification_report"],
                    "distilled_cache_hit": True,
                    "final_briefing": cached["final_briefing"],
                }

        pruned_tools = list(
            USE_CASE_PRIMARY_TOOLS.get(uc_enum, ["tool_lookup_single_epoch_metrics"])
        )
        tag_msg = SystemMessage(
            content=(
                f"[USE_CASE:{uc_enum.value}] [YEAR:{target_year}] "
                f"[REGION:{entity.region}] [TIER:{entity.stakeholder_tier.value}] "
                f"System 1 (`opencode-v2/jev`) extracted entity and pruned tools to {pruned_tools}.\n"
                f"STRICT DETERMINISTIC TOOL GATE RULES (ADR-0005):\n"
                f"1. If no tool has been called yet, you MUST call the bound tool(s) {pruned_tools} first.\n"
                f"2. After receiving the ToolMessage JSON, write a concise technical summary that cites "
                f"ONLY the exact numerical values present in the ToolMessage JSON (always include key metrics "
                f"such as total_raw_detections, deduplicated_fire_episodes, and harmonized_index_2005_eq_100 "
                f"or ks_distance_after when present).\n"
                f"3. NEVER compute new numbers, percentages, differences, or ratios in your head, and NEVER "
                f"write any number (even bullet numbers like 1, 2, 3) that is not in the ToolMessage JSON. "
                f"Use '-' for bullet points instead of numbered lists."
            )
        )
        return {
            "messages": [tag_msg],
            "extracted_entity": entity.model_dump(),
            "cognitive_path": entity.cognitive_path.value,
            "pruned_tool_names": pruned_tools,
            "escalated_from_system1": False,
            "escalation_reason": "",
            "verified_ledger_entries": state.get("verified_ledger_entries", []),
            "self_correction_retries": state.get("self_correction_retries", 0),
            "distilled_cache_hit": False,
            "reasoning_trace": state.get("reasoning_trace", []),
        }

    def _route_after_triage(
        self, state: HarnessState
    ) -> Literal["system1_fast_node", "system2_planner_node", "__end__"]:
        if state.get("distilled_cache_hit"):
            return "__end__"
        c_path = state.get("cognitive_path")
        if c_path in (
            CognitivePath.SYSTEM1_FAST_LOOKUP.value,
            CognitivePath.SYSTEM1_FLASH_ALERT.value,
        ):
            return "system1_fast_node"
        return "system2_planner_node"

    def _system1_fast_node(self, state: HarnessState) -> dict[str, Any]:
        """Node 2 (`UC-S1.3` & `UC-S1.4`): System 1 (`opencode-v2/jev`) single-hop tool call or synthesis."""
        pruned_names = state.get("pruned_tool_names", [])
        bound_tools = [TOOL_MAP[name] for name in pruned_names if name in TOOL_MAP]
        bound_s1 = self.system1_model.bind_tools(bound_tools)
        response = bound_s1.invoke(state["messages"])
        updates: dict[str, Any] = {"messages": [response]}
        if isinstance(response, AIMessage) and not response.tool_calls:
            updates["final_briefing"] = str(response.content)
        return updates

    def _route_after_system1_fast(
        self, state: HarnessState
    ) -> Literal["deterministic_tool_node", "numeric_verifier_node"]:
        messages = state.get("messages", [])
        last_msg = messages[-1] if messages else None
        if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
            return "deterministic_tool_node"
        return "numeric_verifier_node"

    def _system2_planner_node(self, state: HarnessState) -> dict[str, Any]:
        """Node 3 (`UC-1.1..UC-5.3`): System 2 (`qwen-local/qwen3.8-flash-next`) deliberative node."""
        pruned_names = state.get("pruned_tool_names", [])
        bound_tools = [TOOL_MAP[name] for name in pruned_names if name in TOOL_MAP]
        bound_s2 = self.system2_model.bind_tools(bound_tools)
        response = bound_s2.invoke(state["messages"])
        updates: dict[str, Any] = {"messages": [response]}
        if isinstance(response, AIMessage):
            reasoning = response.additional_kwargs.get("reasoning_content")
            if reasoning:
                trace = list(state.get("reasoning_trace", []))
                trace.append(str(reasoning))
                updates["reasoning_trace"] = trace
            if not response.tool_calls:
                updates["final_briefing"] = str(response.content)
        return updates

    def _route_after_system2_planner(
        self, state: HarnessState
    ) -> Literal["deterministic_tool_node", "numeric_verifier_node"]:
        messages = state.get("messages", [])
        last_msg = messages[-1] if messages else None
        if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
            return "deterministic_tool_node"
        return "numeric_verifier_node"

    def _deterministic_tool_node(self, state: HarnessState) -> dict[str, Any]:
        """Node 4: Execute `ToolNode` and ingest all numeric outputs into `VerifiedFactsLedger`."""
        tool_result = self.tool_node.invoke({"messages": state["messages"]})
        new_tool_messages: list[ToolMessage] = tool_result.get("messages", [])

        existing_entries = [
            VerifiedFactEntry.model_validate(e)
            for e in state.get("verified_ledger_entries", [])
        ]
        ledger = VerifiedFactsLedger(entries=existing_entries)

        flash_payload = state.get("flash_alert_payload")
        for tm in new_tool_messages:
            if isinstance(tm, ToolMessage):
                try:
                    payload = json.loads(str(tm.content))
                    if isinstance(payload, dict):
                        ledger.ingest_tool_payload(
                            tm.name or "deterministic_tool", payload
                        )
                        if tm.name == "tool_emit_flash_nrt_alert":
                            flash_payload = payload
                except ValueError:
                    continue

        return {
            "messages": new_tool_messages,
            "verified_ledger_entries": [e.model_dump() for e in ledger.entries],
            "flash_alert_payload": flash_payload,
        }

    def _route_after_tool_node(
        self, state: HarnessState
    ) -> Literal["escalation_gate_node", "system2_planner_node"]:
        c_path = state.get("cognitive_path")
        if c_path in (
            CognitivePath.SYSTEM1_FAST_LOOKUP.value,
            CognitivePath.SYSTEM1_FLASH_ALERT.value,
        ):
            return "escalation_gate_node"
        return "system2_planner_node"

    def _escalation_gate_node(self, state: HarnessState) -> dict[str, Any]:
        """Node 5: Dynamic System 1 -> System 2 Escalation Gate on Physical Conflict."""
        user_query = state.get("user_query", "").upper()
        if "ESCALATE_IF_CONFLICT" not in user_query:
            return {}

        messages = state.get("messages", [])
        tool_messages = [m for m in messages if isinstance(m, ToolMessage)]
        should_escalate = False
        reason = ""
        for tm in tool_messages:
            try:
                payload = json.loads(str(tm.content))
                if isinstance(payload, dict):
                    div = float(
                        payload.get("raw_vs_harmonized_index_divergence_pct", 0.0)
                    )
                    saa_cnt = int(payload.get("saa_rejected_count", 0))
                    if (
                        payload.get("requires_system2_escalation")
                        or div >= 200.0
                        or saa_cnt > 0
                    ):
                        should_escalate = True
                        reason = (
                            f"Physical divergence {div:.1f}% (>= 200.0%) or SAA anomalies "
                            f"({saa_cnt}) detected in {tm.name}."
                        )
                        break
            except (ValueError, TypeError):
                continue

        if not should_escalate:
            return {}

        escalated_tools = list(
            dict.fromkeys(
                state.get("pruned_tool_names", [])
                + USE_CASE_PRIMARY_TOOLS[UseCaseId.UC_1_1_REGIME_SHIFT_ATTRIBUTION]
            )
        )
        esc_msg = SystemMessage(
            content=(
                f"[ESCALATED_S1_TO_S2] {reason} Escalating from System 1 (`jev`) to "
                f"System 2 (`qwen3.8-flash-next`) with expanded attribution tools {escalated_tools}."
            )
        )
        return {
            "messages": [esc_msg],
            "cognitive_path": CognitivePath.ESCALATED_S1_TO_S2.value,
            "escalated_from_system1": True,
            "escalation_reason": reason,
            "pruned_tool_names": escalated_tools,
        }

    def _route_after_escalation_gate(
        self, state: HarnessState
    ) -> Literal["system1_fast_node", "system2_planner_node"]:
        if state.get("cognitive_path") == CognitivePath.ESCALATED_S1_TO_S2.value:
            return "system2_planner_node"
        return "system1_fast_node"

    def _numeric_verifier_node(self, state: HarnessState) -> dict[str, Any]:
        """Node 6: Deterministic Numeric Grounding Verifier (`VerifiedFactsLedger` check)."""
        draft = state.get("final_briefing", "")
        existing_entries = [
            VerifiedFactEntry.model_validate(e)
            for e in state.get("verified_ledger_entries", [])
        ]
        ledger = VerifiedFactsLedger(entries=existing_entries)
        report = ledger.verify_draft_text(draft)
        updates: dict[str, Any] = {
            "verification_report": report.model_dump(),
        }
        if not report.passed:
            retries = int(state.get("self_correction_retries", 0)) + 1
            updates["self_correction_retries"] = retries
            updates["messages"] = [
                HumanMessage(
                    content=(f"[NUMERIC_VERIFIER_REJECTION] {report.feedback_message}")
                )
            ]
        return updates

    def _route_after_verifier(
        self, state: HarnessState
    ) -> Literal["system2_planner_node", "system1_synthesizer_node"]:
        report = state.get("verification_report", {})
        max_repairs = int(
            self.config.get("verification_gate", {}).get("max_repair_attempts", 2)
        )
        if (
            not report.get("passed", True)
            and int(state.get("self_correction_retries", 0)) <= max_repairs
        ):
            return "system2_planner_node"
        return "system1_synthesizer_node"

    def _system1_synthesizer_node(self, state: HarnessState) -> dict[str, Any]:
        """Node 7 (`UC-S1.5`): System 1 (`opencode-v2/jev`) Stakeholder Formatting & Cache Distillation."""
        entity = state.get("extracted_entity", {})
        tier = entity.get("stakeholder_tier", StakeholderTier.CLIMATE_SCIENTIST.value)
        uc_val = entity.get(
            "use_case_id", UseCaseId.UC_1_1_REGIME_SHIFT_ATTRIBUTION.value
        )
        years = entity.get("epoch_years") or [2024]
        target_year = int(years[-1])
        region = str(entity.get("region") or "mekong")
        draft = state.get("final_briefing", "")
        c_path = state.get("cognitive_path", CognitivePath.SYSTEM2_DELIBERATIVE.value)

        header = (
            f"[{tier.upper()} BRIEFING | Cognitive Path: {c_path} | "
            f"System 1: opencode-v2/jev | System 2: qwen-local/qwen3.8-flash-next]\n"
        )
        final_text = header + draft

        messages = state.get("messages", [])
        s1_calls = 0
        s1_model = "jev-1.13-free"
        s2_calls = 0
        s2_provider = "qwen-local/qwen3.8-flash-next"
        for msg in messages:
            kw = getattr(msg, "additional_kwargs", None) or {}
            if "jev_systemone" in kw:
                s1_calls += 1
                s1_model = str(kw["jev_systemone"].get("model", s1_model))
            if "live_provider_used" in kw:
                s2_calls += 1
                s2_provider = str(kw["live_provider_used"])

        live_telemetry = {
            "mode": self.mode,
            "system1_jev_calls": s1_calls,
            "system1_model": s1_model,
            "system2_reasoning_calls": s2_calls,
            "system2_provider_used": s2_provider,
        }

        if self.enable_cache:
            cache_key = VerifiedPatternCache.make_key(
                uc_val,
                target_year,
                region,
                str(tier),
            )
            self.pattern_cache.put(
                cache_key,
                {
                    "pruned_tool_names": state.get("pruned_tool_names", []),
                    "verified_ledger_entries": state.get("verified_ledger_entries", []),
                    "verification_report": state.get("verification_report", {}),
                    "final_briefing": final_text,
                    "live_telemetry": live_telemetry,
                },
            )

        return {
            "final_briefing": final_text,
            "live_telemetry": live_telemetry,
        }

    def _compile_state_graph(self):
        """Build and compile the LangGraph `StateGraph(HarnessState)`."""
        workflow = StateGraph(HarnessState)

        workflow.add_node("system1_triage_node", self._system1_triage_node)
        workflow.add_node("system1_fast_node", self._system1_fast_node)
        workflow.add_node("system2_planner_node", self._system2_planner_node)
        workflow.add_node("deterministic_tool_node", self._deterministic_tool_node)
        workflow.add_node("escalation_gate_node", self._escalation_gate_node)
        workflow.add_node("numeric_verifier_node", self._numeric_verifier_node)
        workflow.add_node("system1_synthesizer_node", self._system1_synthesizer_node)

        workflow.add_edge(START, "system1_triage_node")
        workflow.add_conditional_edges(
            "system1_triage_node",
            self._route_after_triage,
            {
                "system1_fast_node": "system1_fast_node",
                "system2_planner_node": "system2_planner_node",
                "__end__": END,
            },
        )
        workflow.add_conditional_edges(
            "system1_fast_node",
            self._route_after_system1_fast,
            {
                "deterministic_tool_node": "deterministic_tool_node",
                "numeric_verifier_node": "numeric_verifier_node",
            },
        )
        workflow.add_conditional_edges(
            "system2_planner_node",
            self._route_after_system2_planner,
            {
                "deterministic_tool_node": "deterministic_tool_node",
                "numeric_verifier_node": "numeric_verifier_node",
            },
        )
        workflow.add_conditional_edges(
            "deterministic_tool_node",
            self._route_after_tool_node,
            {
                "escalation_gate_node": "escalation_gate_node",
                "system2_planner_node": "system2_planner_node",
            },
        )
        workflow.add_conditional_edges(
            "escalation_gate_node",
            self._route_after_escalation_gate,
            {
                "system1_fast_node": "system1_fast_node",
                "system2_planner_node": "system2_planner_node",
            },
        )
        workflow.add_conditional_edges(
            "numeric_verifier_node",
            self._route_after_verifier,
            {
                "system2_planner_node": "system2_planner_node",
                "system1_synthesizer_node": "system1_synthesizer_node",
            },
        )
        workflow.add_edge("system1_synthesizer_node", END)

        return workflow.compile(checkpointer=self.checkpointer)

    def invoke_use_case(
        self,
        user_query: str,
        use_case_id: UseCaseId | str | None = None,
        thread_id: str = "default-thread",
    ) -> dict[str, Any]:
        """Execute a user query through the compiled Dual-System LangGraph StateGraph."""
        uc_str = (
            use_case_id.value if isinstance(use_case_id, UseCaseId) else use_case_id
        )
        initial_state: dict[str, Any] = {
            "messages": [HumanMessage(content=user_query)],
            "user_query": user_query,
            "extracted_entity": {"use_case_id": uc_str} if uc_str else {},
            "self_correction_retries": 0,
            "distilled_cache_hit": False,
        }
        return self.graph.invoke(
            initial_state,
            config={"configurable": {"thread_id": thread_id}},
        )


def build_dual_system_graph(mode: Literal["deterministic", "live"] = "deterministic"):
    """Entrypoint referenced by `apps/ai-service/langgraph.json`."""
    harness = FlareChronosDualSystemHarness(mode=mode)
    return harness.graph
