"""LangGraph Dual-System Harness (`StateGraph` + `ToolNode` + `MemorySaver` + `VerifiedFactsLedger`).

Orchestrates:
- System 1 Reflexive Layer: Intent Triage (`UC-S1.1`), Entity Extraction
  (`UC-S1.2`), Single-Hop Fast Lookup (`UC-S1.3`), Flash NRT Alert (`UC-S1.4`),
  and Stakeholder Fact Card (`UC-S1.5`). It classifies with a calibrated
  typed-questions endpoint and never derives an analysis.
- System 2 Deliberative Layer: 15 Deliberative Use Cases (`UC-1.1` through
  `UC-5.3`). It chooses its own deterministic tool calls and writes the
  analytical narrative.
- Symbiosis:
  1. System 1 -> System 2 Context & Tool Pruning
  2. Dynamic Escalation Gate on Physical Conflict (`divergence >= 200%` or `saa_rejected_count > 0`)
  3. Deterministic `VerifiedFactsLedger` + `NumericGroundingVerifier` loopback edge
  4. System 2 -> System 1 `VerifiedPatternCache` distillation

Every language model is reached through an `EndpointProfile` resolved from
explicit configuration. The harness never reads the host's agent tooling
configuration, and it never fabricates a model answer: a missing credential or
a failed call surfaces as an error.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any, Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.cache.memory import InMemoryCache
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import CachePolicy, Command, RetryPolicy, interrupt

from ai_service.events import HarnessEvent
from ai_service.human_input import HUMAN_INPUT_TOOLS, ask_user_question
from ai_service.models import (
    AI_SERVICE_ROOT,
    DeterministicHarnessChatModel,
    EndpointCallError,
    HarnessChatModel,
    build_live_system1_chat_model,
    build_live_system2_chat_model,
    load_harness_config,
    resolve_endpoint_profile,
    synthesize_grounded_response,
)
from ai_service.prompts import system1_typed_questions, system2_system_prompt
from ai_service.schemas import (
    CognitivePath,
    HarnessState,
    SpatioTemporalQueryEntity,
    StakeholderTier,
    UseCaseId,
    VerifiedFactEntry,
    VerifiedFactsLedger,
    verify_grounded_draft,
)
from ai_service.tools import (
    ALL_DETERMINISTIC_TOOLS,
    ATOMIC_TOOLS,
    TOOL_MAP,
    USE_CASE_PRIMARY_TOOLS,
)

SYSTEM_1_REFLEXIVE_USE_CASES = {
    UseCaseId.UC_S1_1_INTENT_TRIAGE,
    UseCaseId.UC_S1_2_ENTITY_EXTRACTION,
    UseCaseId.UC_S1_3_SINGLE_HOP_LOOKUP,
    UseCaseId.UC_S1_4_FLASH_NRT_ALERT,
    UseCaseId.UC_S1_5_STAKEHOLDER_SYNTHESIS,
}

FAST_TIER = "fast"
DELIBERATIVE_TIER = "deliberative"

DEFAULT_CHECKPOINT_PATH = (
    AI_SERVICE_ROOT.parents[1] / "data" / "runtime" / "harness_checkpoints.sqlite"
)


def build_sqlite_checkpointer(path: Path | None = None) -> Any:
    """Create a durable checkpointer so a paused run survives a process restart.

    A run that waits for a human sign-off must be resumable tomorrow, so the
    checkpoint lives on disk rather than in memory.
    """
    from langgraph.checkpoint.sqlite import SqliteSaver

    target = path or DEFAULT_CHECKPOINT_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    return SqliteSaver(sqlite3.connect(target, check_same_thread=False))


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
        checkpointer: Any | None = None,
        enable_sign_off: bool = True,
    ) -> None:
        self.config = load_harness_config()
        self.mode = mode
        self.enable_cache = enable_cache
        self.enable_sign_off = enable_sign_off
        self.pattern_cache = VerifiedPatternCache()
        self.checkpointer = checkpointer if checkpointer is not None else MemorySaver()
        self.node_cache = InMemoryCache()
        self.tool_node = ToolNode(
            [*ALL_DETERMINISTIC_TOOLS, *HUMAN_INPUT_TOOLS],
            handle_tool_errors=True,
        )

        s1_profile = resolve_endpoint_profile(self.config, "system1_reflexive")
        s2_profile = resolve_endpoint_profile(self.config, "system2_deliberative")
        self.s1_profile = s1_profile
        self.s2_profile = s2_profile
        self.cognition = self.config.get("cognition", {}) or {}

        if mode == "live":
            self.system1_model: HarnessChatModel = build_live_system1_chat_model(
                self.config
            )
            self.system2_model: HarnessChatModel = build_live_system2_chat_model(
                self.config,
                inject_unverified_number_once=inject_unverified_number_once,
            )
        else:
            self.system1_model = DeterministicHarnessChatModel(
                role="system1_reflexive",
                model_id=s1_profile.model_id,
                source_label=s1_profile.endpoint,
                reasoning_effort="low",
                inject_unverified_number_once=False,
            )
            self.system2_model = DeterministicHarnessChatModel(
                role="system2_deliberative",
                model_id=s2_profile.model_id,
                source_label=s2_profile.endpoint,
                reasoning_effort=str(s2_profile.request.thinking_level or "low"),
                inject_unverified_number_once=inject_unverified_number_once,
            )

        self.graph = self._compile_state_graph()

    # ------------------------------------------------------------------
    # Entity extraction and tier routing
    # ------------------------------------------------------------------

    def _extract_entity(
        self, user_query: str, requested_use_case: UseCaseId | str | None = None
    ) -> SpatioTemporalQueryEntity:
        """System 1 (`UC-S1.1` & `UC-S1.2`): Provisional entity from the raw query."""
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

    def _refine_entity(
        self,
        provisional: SpatioTemporalQueryEntity,
        answers: dict[str, Any],
        explicit_use_case: bool,
    ) -> tuple[SpatioTemporalQueryEntity, dict[str, float], str]:
        """Merge the calibrated classification into the entity and pick the tier."""
        data = provisional.model_dump()
        confidence: dict[str, float] = {}

        region_answer = answers.get("region") or {}
        region_choice = region_answer.get("choice")
        if region_choice in ("mekong", "amazon"):
            data["region"] = region_choice
            confidence["region"] = float(region_answer.get("confidence", 0.0))

        urgency_p = float((answers.get("urgency") or {}).get("noul", 0.0))
        confidence["urgency"] = urgency_p
        if urgency_p >= float(self.cognition.get("urgency_threshold", 0.6)):
            data["urgency_level"] = "flash_crisis"

        deliberative_p = float((answers.get("is_deliberative") or {}).get("noul", 0.0))
        confidence["is_deliberative"] = deliberative_p

        if not provisional.epoch_years:
            focus_choice = (answers.get("focus_epoch") or {}).get("choice")
            if focus_choice and str(focus_choice).isdigit():
                data["epoch_years"] = [int(focus_choice)]

        threshold = float(self.cognition.get("deliberative_threshold", 0.5))
        if explicit_use_case:
            tier = (
                FAST_TIER
                if str(data["use_case_id"]).startswith("UC-S1")
                else DELIBERATIVE_TIER
            )
        else:
            tier = DELIBERATIVE_TIER if deliberative_p >= threshold else FAST_TIER
            if tier == FAST_TIER:
                data["use_case_id"] = UseCaseId.UC_S1_3_SINGLE_HOP_LOOKUP.value

        if tier == FAST_TIER:
            data["cognitive_path"] = (
                CognitivePath.SYSTEM1_FLASH_ALERT.value
                if data["urgency_level"] == "flash_crisis"
                else CognitivePath.SYSTEM1_FAST_LOOKUP.value
            )
        else:
            data["cognitive_path"] = CognitivePath.SYSTEM2_DELIBERATIVE.value

        return SpatioTemporalQueryEntity.model_validate(data), confidence, tier

    # ------------------------------------------------------------------
    # Tool surfaces
    # ------------------------------------------------------------------

    def _primary_tools(self, use_case_value: str) -> list[str]:
        try:
            return list(USE_CASE_PRIMARY_TOOLS.get(UseCaseId(use_case_value), []))
        except ValueError:
            return []

    def _fast_tier_tools(self, use_case_value: str) -> list[str]:
        """The System 1 surface: Atomic Tools only, so the fast tier cannot analyse."""
        primary = self._primary_tools(use_case_value)
        if self.cognition.get("fast_tier_tool_surface", "atomic") == "atomic":
            allowed = {tool.name for tool in ATOMIC_TOOLS}
            candidates = [name for name in primary if name in allowed]
        else:
            candidates = primary
        return candidates or ["tool_lookup_single_epoch_metrics"]

    def _deliberative_tools(self, use_case_value: str) -> list[str]:
        """The System 2 surface: every registered deterministic tool, plus clarification."""
        if self.cognition.get("deliberative_tool_surface", "all") == "use_case":
            names = self._primary_tools(use_case_value)
        else:
            names = [tool.name for tool in ALL_DETERMINISTIC_TOOLS]
        return [*names, ask_user_question.name]

    # ------------------------------------------------------------------
    # Nodes
    # ------------------------------------------------------------------

    def _system1_triage_node(self, state: HarnessState) -> dict[str, Any]:
        """Node 1: System 1 classifies intent and extracts the entity, then routes."""
        user_query = state.get("user_query", "")
        pre_entity = state.get("extracted_entity") or {}
        requested_uc = pre_entity.get("use_case_id")
        explicit_use_case = bool(requested_uc)

        provisional = self._extract_entity(user_query, requested_uc)
        classification = self.system1_model.classify(
            state_text=user_query,
            questions=system1_typed_questions(provisional),
            entity=provisional,
        )
        answers = classification.get("answers", {}) or {}
        entity, confidence, tier = self._refine_entity(
            provisional, answers, explicit_use_case
        )

        target_year = entity.epoch_years[-1] if entity.epoch_years else 2024
        cache_key = VerifiedPatternCache.make_key(
            entity.use_case_id.value,
            target_year,
            entity.region,
            entity.stakeholder_tier.value,
        )
        if self.enable_cache and entity.urgency_level != "flash_crisis":
            cached = self.pattern_cache.get(cache_key)
            if cached is not None:
                return {
                    "extracted_entity": entity.model_dump(mode="json"),
                    "cognitive_path": CognitivePath.DISTILLED_CACHE_HIT.value,
                    "cognitive_tier": cached.get("cognitive_tier", tier),
                    "triage_confidence": confidence,
                    "pruned_tool_names": cached["pruned_tool_names"],
                    "verified_ledger_entries": cached["verified_ledger_entries"],
                    "verification_report": cached["verification_report"],
                    "distilled_cache_hit": True,
                    "final_briefing": cached["final_briefing"],
                    "live_telemetry": cached["live_telemetry"],
                }

        tag_msg = SystemMessage(
            content=(
                f"[USE_CASE:{entity.use_case_id.value}] [YEAR:{target_year}] "
                f"[REGION:{entity.region}] "
                f"[TIER:{entity.stakeholder_tier.value}] "
                f"[COGNITIVE_TIER:{tier}] "
                f"System 1 classified the request with confidence {confidence}.\n"
                f"STRICT DETERMINISTIC TOOL GATE RULES (ADR-0005):\n"
                f"1. If no tool has been called yet, you MUST call the bound tool(s) first.\n"
                f"2. After receiving the ToolMessage JSON, write a concise technical summary that cites "
                f"ONLY the exact numerical values present in the ToolMessage JSON (always include key metrics "
                f"such as total_raw_detections, deduplicated_fire_episodes, and harmonized_index_2005_eq_100 "
                f"or ks_distance_after when present).\n"
                f"3. NEVER compute new numbers, percentages, differences, or ratios in your head, and NEVER "
                f"write any number (even bullet numbers like 1, 2, 3) that is not in the ToolMessage JSON. "
                f"Use '-' for bullet points instead of numbered lists."
            )
        )
        tool_surface = (
            self._fast_tier_tools(entity.use_case_id.value)
            if tier == FAST_TIER
            else self._primary_tools(entity.use_case_id.value)
        )
        return {
            "messages": [tag_msg],
            "extracted_entity": entity.model_dump(mode="json"),
            "cognitive_path": entity.cognitive_path.value,
            "cognitive_tier": tier,
            "triage_confidence": confidence,
            "triage_classification": classification,
            "tool_surface": tool_surface,
            "pruned_tool_names": tool_surface,
            "escalated_from_system1": False,
            "escalation_reason": "",
            "verified_ledger_entries": state.get("verified_ledger_entries", []),
            "self_correction_retries": state.get("self_correction_retries", 0),
            "distilled_cache_hit": False,
            "reasoning_trace": state.get("reasoning_trace", []),
            "synthesis_mode": "pending",
        }

    def _route_after_triage(
        self, state: HarnessState
    ) -> Literal["system1_fast_node", "system2_agent_node", "__end__"]:
        if state.get("distilled_cache_hit"):
            return "__end__"
        if state.get("cognitive_tier") == FAST_TIER:
            return "system1_fast_node"
        return "system2_agent_node"

    def _system1_fast_node(self, state: HarnessState) -> dict[str, Any]:
        """Node 2: System 1 executes one Atomic Tool and returns a grounded fact card."""
        surface = self._fast_tier_tools(
            str((state.get("extracted_entity") or {}).get("use_case_id", ""))
        )
        bound_tools = [TOOL_MAP[name] for name in surface if name in TOOL_MAP]
        bound_s1 = self._apply_plan(self.system1_model.bind_tools(bound_tools), surface)
        response = bound_s1.invoke(state["messages"])
        updates: dict[str, Any] = {"messages": [response]}
        if isinstance(response, AIMessage) and not response.tool_calls:
            updates["final_briefing"] = str(response.content)
            updates["synthesis_mode"] = "deterministic"
        return updates

    def _apply_plan(self, model: HarnessChatModel, plan: list[str]) -> HarnessChatModel:
        """Give the offline simulator the tool plan the harness decided on."""
        if self.mode != "deterministic":
            return model
        return model.model_copy(update={"planned_tool_names": list(plan)})

    def _route_after_system1_fast(
        self, state: HarnessState
    ) -> Literal["deterministic_tool_node", "numeric_verifier_node"]:
        messages = state.get("messages", [])
        last_msg = messages[-1] if messages else None
        if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
            return "deterministic_tool_node"
        return "numeric_verifier_node"

    def _system2_agent_node(self, state: HarnessState) -> dict[str, Any]:
        """Node 3: System 2 plans its own tool calls and writes the narrative."""
        entity_payload = state.get("extracted_entity") or {}
        entity = SpatioTemporalQueryEntity.model_validate(entity_payload)
        surface = self._deliberative_tools(entity.use_case_id.value)
        bound_tools = [TOOL_MAP[name] for name in surface if name in TOOL_MAP]
        bound_tools.extend(
            tool for tool in HUMAN_INPUT_TOOLS if tool.name not in TOOL_MAP
        )

        prompt = system2_system_prompt(
            entity=entity,
            requested_use_case=entity.use_case_id.value,
            tier=str(entity.stakeholder_tier.value),
            max_clarifications=int(self.cognition.get("max_clarifications", 2)),
        )
        bound_s2 = self.system2_model.bind_tools(bound_tools)
        bound_s2 = self._apply_plan(
            bound_s2, list(state.get("pruned_tool_names") or [])
        )

        tool_rounds = sum(
            1 for m in state.get("messages", []) if isinstance(m, ToolMessage)
        )
        max_rounds = int(
            self.config.get("deterministic_tool_gate", {}).get("max_reasoning_steps", 8)
        )
        if tool_rounds >= max_rounds:
            tool_messages = [
                m for m in state.get("messages", []) if isinstance(m, ToolMessage)
            ]
            return {
                "final_briefing": synthesize_grounded_response(
                    entity.use_case_id.value, tool_messages
                ),
                "synthesis_mode": "deterministic_fallback",
                "reasoning_trace": [
                    *state.get("reasoning_trace", []),
                    (
                        f"[System 2 stopped after {tool_rounds} tool rounds: "
                        f"the reasoning step budget was exhausted.]"
                    ),
                ],
            }

        response = bound_s2.invoke([SystemMessage(prompt), *state["messages"]])

        updates: dict[str, Any] = {"messages": [response]}
        if isinstance(response, AIMessage):
            reasoning = response.additional_kwargs.get("reasoning_content")
            if reasoning:
                trace = list(state.get("reasoning_trace", []))
                trace.append(str(reasoning))
                updates["reasoning_trace"] = trace
            if not response.tool_calls:
                updates["final_briefing"] = str(response.content)
                updates["synthesis_mode"] = (
                    "llm" if self.mode == "live" else "deterministic"
                )
        return updates

    def _route_after_system2_agent(
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
        clarifications = list(state.get("clarification_requests", []))
        for tm in new_tool_messages:
            if not isinstance(tm, ToolMessage):
                continue
            if tm.name == "ask_user_question":
                clarifications.append(
                    {"tool_call_id": tm.tool_call_id, "answer": str(tm.content)}
                )
                continue
            try:
                payload = json.loads(str(tm.content))
                if isinstance(payload, dict):
                    ledger.ingest_tool_payload(tm.name or "deterministic_tool", payload)
                    if tm.name == "tool_emit_flash_nrt_alert":
                        flash_payload = payload
            except ValueError:
                continue

        return {
            "messages": new_tool_messages,
            "verified_ledger_entries": [e.model_dump() for e in ledger.entries],
            "flash_alert_payload": flash_payload,
            "clarification_requests": clarifications,
        }

    def _route_after_tool_node(
        self, state: HarnessState
    ) -> Literal["escalation_gate_node", "system2_agent_node"]:
        c_path = state.get("cognitive_path")
        if c_path in (
            CognitivePath.SYSTEM1_FAST_LOOKUP.value,
            CognitivePath.SYSTEM1_FLASH_ALERT.value,
        ):
            return "escalation_gate_node"
        return "system2_agent_node"

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
                    divergence = float(
                        payload.get("raw_vs_harmonized_index_divergence_pct", 0.0)
                    )
                    saa_count = int(payload.get("saa_rejected_count", 0))
                    if (
                        payload.get("requires_system2_escalation")
                        or divergence >= 200.0
                        or saa_count > 0
                    ):
                        should_escalate = True
                        reason = (
                            f"Physical divergence {divergence:.1f}% (>= 200.0%) or SAA anomalies "
                            f"({saa_count}) detected in {tm.name}."
                        )
                        break
            except (ValueError, TypeError):
                continue

        if not should_escalate:
            return {}

        escalated_tools = list(
            dict.fromkeys(
                state.get("pruned_tool_names", [])
                + self._primary_tools(UseCaseId.UC_1_1_REGIME_SHIFT_ATTRIBUTION.value)
            )
        )
        esc_msg = SystemMessage(
            content=(
                f"[ESCALATED_S1_TO_S2] {reason} Escalating from System 1 to "
                f"System 2 with expanded attribution tools {escalated_tools}."
            )
        )
        escalated_entity = dict(state.get("extracted_entity") or {})
        escalated_entity["use_case_id"] = (
            UseCaseId.UC_1_1_REGIME_SHIFT_ATTRIBUTION.value
        )
        return {
            "messages": [esc_msg],
            "extracted_entity": escalated_entity,
            "cognitive_path": CognitivePath.ESCALATED_S1_TO_S2.value,
            "cognitive_tier": DELIBERATIVE_TIER,
            "escalated_from_system1": True,
            "escalation_reason": reason,
            "tool_surface": escalated_tools,
            "pruned_tool_names": escalated_tools,
        }

    def _route_after_escalation_gate(
        self, state: HarnessState
    ) -> Literal["system1_fast_node", "system2_agent_node"]:
        if state.get("cognitive_path") == CognitivePath.ESCALATED_S1_TO_S2.value:
            return "system2_agent_node"
        return "system1_fast_node"

    def _numeric_verifier_node(self, state: HarnessState) -> dict[str, Any]:
        """Node 6: Numeric Grounding Verifier (`VerifiedFactsLedger` check).

        The verifier resolves `{{fact_key}}` citations against the ledger and
        then checks every number in the resolved text. A citation with no
        ledger entry is a grounding error, not a formatting problem.
        """
        draft = state.get("final_briefing", "")
        existing_entries = [
            VerifiedFactEntry.model_validate(e)
            for e in state.get("verified_ledger_entries", [])
        ]
        ledger = VerifiedFactsLedger(entries=existing_entries)
        tolerance = float(
            self.config.get("deterministic_tool_gate", {}).get(
                "numeric_tolerance_rel", 0.005
            )
        )
        resolved, report = verify_grounded_draft(
            draft,
            ledger,
            tolerance,
            ignore_literals=[
                self.s1_profile.model_id,
                self.s2_profile.model_id,
                str((state.get("extracted_entity") or {}).get("use_case_id", "")),
            ],
        )
        if not resolved.strip():
            report.passed = False
            report.feedback_message = (
                "VIOLATION OF DETERMINISTIC TOOL GATE: the draft is empty. "
                "Write the analytical narrative and cite the available facts."
            )
        updates: dict[str, Any] = {
            "verification_report": report.model_dump(),
            "final_briefing": resolved,
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
    ) -> Literal["system2_agent_node", "sign_off_gate_node"]:
        report = state.get("verification_report", {})
        max_repairs = int(
            self.config.get("verification_gate", {}).get("max_repair_attempts", 2)
        )
        if (
            not report.get("passed", True)
            and int(state.get("self_correction_retries", 0)) <= max_repairs
        ):
            return "system2_agent_node"
        return "sign_off_gate_node"

    def _sign_off_gate_node(self, state: HarnessState) -> dict[str, Any]:
        """Node 7: Human sign-off for use cases that authorize an operational action."""
        entity = state.get("extracted_entity") or {}
        use_case_value = str(entity.get("use_case_id", ""))
        required = set(self.cognition.get("requires_sign_off", []) or [])
        if not self.enable_sign_off or use_case_value not in required:
            return {}

        request = {
            "kind": "sign_off",
            "use_case_id": use_case_value,
            "question": (
                f"Authorize the operational action proposed by {use_case_value}?"
            ),
            "options": ["approve", "reject"],
            "cognitive_tier": state.get("cognitive_tier", ""),
            "evidence": {
                "final_briefing": state.get("final_briefing", ""),
                "verification_report": state.get("verification_report", {}),
            },
        }
        answer = interrupt(request)
        payload = answer if isinstance(answer, dict) else {"approved": bool(answer)}
        approved = bool(payload.get("approved", False))
        decision = {
            "use_case_id": use_case_value,
            "approved": approved,
            "reason": str(payload.get("reason", "")),
            "decided_by": str(payload.get("decided_by", "")),
            "request": request,
        }
        updates: dict[str, Any] = {"sign_off_decision": decision}
        if not approved:
            updates["final_briefing"] = ""
            updates["synthesis_mode"] = "sign_off_declined"
        return updates

    def _route_after_sign_off(
        self, state: HarnessState
    ) -> Literal["system1_synthesizer_node", "__end__"]:
        decision = state.get("sign_off_decision") or {}
        if decision and not decision.get("approved", False):
            return "__end__"
        return "system1_synthesizer_node"

    def _system1_synthesizer_node(self, state: HarnessState) -> dict[str, Any]:
        """Node 8: Stakeholder header, synthesis mode, and cache distillation."""
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

        report = state.get("verification_report", {})
        synthesis_mode = str(state.get("synthesis_mode") or "pending")
        if not report.get("passed", True):
            tool_messages = [
                m for m in state.get("messages", []) if isinstance(m, ToolMessage)
            ]
            draft = synthesize_grounded_response(str(uc_val), tool_messages)
            synthesis_mode = "deterministic_fallback"
            ledger = VerifiedFactsLedger(
                entries=[
                    VerifiedFactEntry.model_validate(e)
                    for e in state.get("verified_ledger_entries", [])
                ]
            )
            tolerance = float(
                self.config.get("deterministic_tool_gate", {}).get(
                    "numeric_tolerance_rel", 0.005
                )
            )
            draft, fallback_report = verify_grounded_draft(draft, ledger, tolerance)
            report = fallback_report.model_dump()

        header = (
            f"[{tier.upper()} BRIEFING | Cognitive Path: {c_path} | "
            f"System 1: {self.s1_profile.model_id} | "
            f"System 2: {self.s2_profile.model_id} | "
            f"Synthesis: {synthesis_mode}]\n"
        )
        final_text = header + draft

        messages = state.get("messages", [])
        s1_calls = 1 if state.get("triage_classification") else 0
        s1_model = self.s1_profile.model_id
        s2_calls = 0
        s2_model = self.s2_profile.model_id
        for message in messages:
            kwargs = getattr(message, "additional_kwargs", None) or {}
            if "systemone_result" in kwargs:
                s1_calls += 1
            if "model_used" in kwargs:
                s2_calls += 1
                s2_model = str(kwargs["model_used"])

        live_telemetry = {
            "mode": self.mode,
            "system1_calls": s1_calls,
            "system1_model": s1_model,
            "system1_endpoint": self.s1_profile.endpoint,
            "system2_calls": s2_calls,
            "system2_model": s2_model,
            "system2_endpoint": self.s2_profile.endpoint,
            "cognitive_tier": state.get("cognitive_tier", ""),
            "tool_surface": state.get("tool_surface", []),
            "synthesis_mode": synthesis_mode,
            "triage_confidence": state.get("triage_confidence", {}),
            "triage_classification": state.get("triage_classification", {}),
            "clarification_requests": state.get("clarification_requests", []),
            "sign_off_decision": state.get("sign_off_decision", {}),
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
                    "cognitive_tier": state.get("cognitive_tier", ""),
                },
            )

        return {
            "final_briefing": final_text,
            "live_telemetry": live_telemetry,
            "synthesis_mode": synthesis_mode,
            "verification_report": report,
        }

    # ------------------------------------------------------------------
    # Graph
    # ------------------------------------------------------------------

    def _compile_state_graph(self):
        """Build and compile the LangGraph `StateGraph(HarnessState)`."""
        workflow = StateGraph(HarnessState)

        model_retry = RetryPolicy(
            max_attempts=3,
            initial_interval=0.5,
            backoff_factor=2.0,
            retry_on=lambda exc: isinstance(exc, EndpointCallError) and exc.retryable,
        )

        workflow.add_node(
            "system1_triage_node", self._system1_triage_node, retry_policy=model_retry
        )
        workflow.add_node(
            "system1_fast_node", self._system1_fast_node, retry_policy=model_retry
        )
        workflow.add_node(
            "system2_agent_node", self._system2_agent_node, retry_policy=model_retry
        )
        workflow.add_node(
            "deterministic_tool_node",
            self._deterministic_tool_node,
            cache_policy=CachePolicy(ttl=3600),
        )
        workflow.add_node("escalation_gate_node", self._escalation_gate_node)
        workflow.add_node("numeric_verifier_node", self._numeric_verifier_node)
        workflow.add_node("sign_off_gate_node", self._sign_off_gate_node)
        workflow.add_node("system1_synthesizer_node", self._system1_synthesizer_node)

        workflow.add_edge(START, "system1_triage_node")
        workflow.add_conditional_edges(
            "system1_triage_node",
            self._route_after_triage,
            {
                "system1_fast_node": "system1_fast_node",
                "system2_agent_node": "system2_agent_node",
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
            "system2_agent_node",
            self._route_after_system2_agent,
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
                "system2_agent_node": "system2_agent_node",
            },
        )
        workflow.add_conditional_edges(
            "escalation_gate_node",
            self._route_after_escalation_gate,
            {
                "system1_fast_node": "system1_fast_node",
                "system2_agent_node": "system2_agent_node",
            },
        )
        workflow.add_conditional_edges(
            "numeric_verifier_node",
            self._route_after_verifier,
            {
                "system2_agent_node": "system2_agent_node",
                "sign_off_gate_node": "sign_off_gate_node",
            },
        )
        workflow.add_conditional_edges(
            "sign_off_gate_node",
            self._route_after_sign_off,
            {
                "system1_synthesizer_node": "system1_synthesizer_node",
                "__end__": END,
            },
        )
        workflow.add_edge("system1_synthesizer_node", END)

        return workflow.compile(checkpointer=self.checkpointer, cache=self.node_cache)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

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
            config=self._run_config(thread_id),
        )

    def _run_config(self, thread_id: str) -> dict[str, Any]:
        return {
            "configurable": {"thread_id": thread_id},
            "recursion_limit": int(self.cognition.get("recursion_limit", 24)),
        }

    # ------------------------------------------------------------------
    # Event stream
    # ------------------------------------------------------------------

    @staticmethod
    def _event_from_chunk(mode: str, chunk: Any) -> list[HarnessEvent]:
        """Translate one LangGraph stream chunk into harness events."""
        events: list[HarnessEvent] = []
        if mode == "updates" and isinstance(chunk, dict) and chunk:
            interrupts = chunk.get("__interrupt__")
            if interrupts:
                payload = dict(interrupts[0].value) if interrupts else {}
                kind = payload.get("kind")
                if kind == "clarification":
                    events.append(HarnessEvent("clarification_requested", payload))
                else:
                    events.append(HarnessEvent("sign_off_required", payload))
            else:
                for node_name, update in chunk.items():
                    events.append(
                        HarnessEvent(
                            "node_completed",
                            {
                                "node": node_name,
                                "keys": sorted(update.keys())
                                if isinstance(update, dict)
                                else [],
                            },
                        )
                    )
                    if node_name == "deterministic_tool_node" and isinstance(
                        update, dict
                    ):
                        tool_names = [
                            str(getattr(message, "name", "") or "")
                            for message in update.get("messages", [])
                            if getattr(message, "name", None)
                        ]
                        if tool_names:
                            events.append(
                                HarnessEvent("tool_result", {"tools": tool_names})
                            )
        elif mode == "messages":
            payload = chunk[0] if isinstance(chunk, tuple) else chunk
            reasoning = (getattr(payload, "additional_kwargs", None) or {}).get(
                "reasoning_content"
            )
            if reasoning:
                events.append(HarnessEvent("reasoning", {"text": str(reasoning)}))
            content = getattr(payload, "content", "")
            if content:
                events.append(HarnessEvent("message", {"content": str(content)}))
        return events

    async def astream_use_case(
        self,
        user_query: str,
        use_case_id: UseCaseId | str | None = None,
        thread_id: str = "default-thread",
    ) -> AsyncIterator[HarnessEvent]:
        """Run one use case and yield typed events as the run progresses."""
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
        config = self._run_config(thread_id)
        yield HarnessEvent(
            "run_started",
            {
                "thread_id": thread_id,
                "use_case_id": uc_str,
                "mode": self.mode,
            },
        )
        async for event in self._astream(initial_state, config):
            yield event

    async def astream_resume(
        self, thread_id: str, payload: Any
    ) -> AsyncIterator[HarnessEvent]:
        """Resume a paused run with the human's answer and yield typed events."""
        config = self._run_config(thread_id)
        yield HarnessEvent(
            "run_started",
            {"thread_id": thread_id, "mode": self.mode, "resumed": True},
        )
        async for event in self._astream(Command(resume=payload), config):
            yield event

    async def _astream(
        self, graph_input: Any, config: dict[str, Any]
    ) -> AsyncIterator[HarnessEvent]:
        try:
            async for mode, chunk in self.graph.astream(
                graph_input, config, stream_mode=["updates", "messages"]
            ):
                for event in self._event_from_chunk(mode, chunk):
                    yield event
        except Exception as exc:  # noqa: BLE001 - surfaced to the client
            yield HarnessEvent(
                "run_failed", {"error": str(exc), "error_type": type(exc).__name__}
            )
            return

        snapshot = self.graph.get_state(config)
        if snapshot.interrupts:
            yield HarnessEvent(
                "run_paused",
                {
                    "thread_id": config["configurable"]["thread_id"],
                    "next": list(snapshot.next),
                },
            )
            return

        values = snapshot.values or {}
        yield HarnessEvent(
            "verification", dict(values.get("verification_report") or {})
        )
        yield HarnessEvent(
            "briefing",
            {
                "text": str(values.get("final_briefing", "")),
                "synthesis_mode": values.get("synthesis_mode", ""),
            },
        )
        yield HarnessEvent(
            "run_completed",
            {
                "thread_id": config["configurable"]["thread_id"],
                "cognitive_tier": values.get("cognitive_tier", ""),
                "synthesis_mode": values.get("synthesis_mode", ""),
                "sign_off_decision": values.get("sign_off_decision", {}),
                "clarification_requests": values.get("clarification_requests", []),
            },
        )


def build_dual_system_graph(mode: Literal["deterministic", "live"] = "deterministic"):
    """Entrypoint referenced by `apps/ai-service/langgraph.json`."""
    harness = FlareChronosDualSystemHarness(mode=mode)
    return harness.graph
