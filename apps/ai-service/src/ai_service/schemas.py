"""Domain Schemas, Verified Facts Ledger, and LangGraph State for Flare-Chronos AI Service."""

from __future__ import annotations

import json
import re
from enum import StrEnum
from typing import Annotated, Any, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

CITATION_PATTERN = re.compile(r"\{\{([A-Za-z0-9_.\[\]-]+)\}\}")


def collect_citation_keys(payload: Any, prefix: str = "") -> dict[str, float]:
    """Map every numeric leaf of a tool payload to its canonical ledger fact key.

    The key names match `VerifiedFactsLedger.ingest_tool_payload` exactly, so a
    citation table built from a payload always addresses real ledger entries.
    Numeric tokens embedded in string fields are excluded: they are ledger
    entries but not citable quantities.
    """
    citations: dict[str, float] = {}
    if isinstance(payload, str):
        try:
            decoded = json.loads(payload)
        except ValueError:
            return citations
        if isinstance(decoded, str):
            return citations
        return collect_citation_keys(decoded, prefix)
    if isinstance(payload, dict):
        for key, value in payload.items():
            sub_key = f"{prefix}.{key}" if prefix else str(key)
            citations.update(collect_citation_keys(value, sub_key))
    elif isinstance(payload, list):
        for index, item in enumerate(payload):
            citations.update(collect_citation_keys(item, f"{prefix}[{index}]"))
    elif isinstance(payload, int | float) and not isinstance(payload, bool):
        citations[prefix or "value"] = float(payload)
    return citations


def format_citation_value(value: float) -> str:
    """Render a ledger value without exponent notation or trailing zeros."""
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))
    return f"{value:.6f}".rstrip("0").rstrip(".")


def resolve_citations(text: str, citations: dict[str, float]) -> tuple[str, list[str]]:
    """Replace `{{fact_key}}` placeholders with the ledger value of that key.

    Returns the resolved text and the list of keys that had no ledger entry.
    An unresolved key is a grounding error: the model cited a quantity that no
    deterministic tool produced.
    """
    unresolved: list[str] = []

    def _substitute(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in citations:
            unresolved.append(key)
            return match.group(0)
        return format_citation_value(citations[key])

    return CITATION_PATTERN.sub(_substitute, text), unresolved


class UseCaseId(StrEnum):
    """Canonical identifiers for all 20 Dual-System Use Cases (5 System-1 + 15 System-2)."""

    # System 1 Reflexive Layer Use Cases
    UC_S1_1_INTENT_TRIAGE = "UC-S1.1"
    UC_S1_2_ENTITY_EXTRACTION = "UC-S1.2"
    UC_S1_3_SINGLE_HOP_LOOKUP = "UC-S1.3"
    UC_S1_4_FLASH_NRT_ALERT = "UC-S1.4"
    UC_S1_5_STAKEHOLDER_SYNTHESIS = "UC-S1.5"

    # System 2 Deliberative Layer Use Cases (5 Groups x 3 Use Cases = 15)
    UC_1_1_REGIME_SHIFT_ATTRIBUTION = "UC-1.1"
    UC_1_2_CROSS_SENSOR_DISCREPANCY = "UC-1.2"
    UC_1_3_THERMAL_SOURCE_ORIGIN = "UC-1.3"

    UC_2_1_PHENOLOGY_PHASE_SHIFT = "UC-2.1"
    UC_2_2_TACTICAL_DISPATCH = "UC-2.2"
    UC_2_3_VERIFIED_BRIEFING = "UC-2.3"

    UC_3_1_CONSTELLATION_RETIREMENT = "UC-3.1"
    UC_3_2_MULTIHOP_SPATIOTEMPORAL = "UC-3.2"
    UC_3_3_BIOME_RECALIBRATION = "UC-3.3"

    UC_4_1_ORBITAL_DRIFT_SZA_AUDIT = "UC-4.1"
    UC_4_2_NRT_VS_SP_FIDELITY = "UC-4.2"
    UC_4_3_ADAPTIVE_RATE_LIMIT = "UC-4.3"

    UC_5_1_REDD_CARBON_MRV = "UC-5.1"
    UC_5_2_POLICY_COUNTERFACTUAL = "UC-5.2"
    UC_5_3_TRANSBOUNDARY_FORENSICS = "UC-5.3"


class CognitivePath(StrEnum):
    """Execution path selected or escalated to within the Dual-System LangGraph."""

    SYSTEM1_FAST_LOOKUP = "system1_fast_lookup"
    SYSTEM1_FLASH_ALERT = "system1_flash_alert"
    SYSTEM2_DELIBERATIVE = "system2_deliberative"
    ESCALATED_S1_TO_S2 = "escalated_s1_to_s2"
    DISTILLED_CACHE_HIT = "distilled_cache_hit"


class StakeholderTier(StrEnum):
    """Target audience format for System 1 final synthesis (UC-S1.5)."""

    FIELD_RANGER = "field_ranger"
    FORESTRY_EXECUTIVE = "forestry_executive"
    CLIMATE_SCIENTIST = "climate_scientist"


class SpatioTemporalQueryEntity(BaseModel):
    """Structured spatio-temporal parameters extracted by System 1 (UC-S1.2)."""

    use_case_id: UseCaseId = Field(
        default=UseCaseId.UC_1_1_REGIME_SHIFT_ATTRIBUTION,
        description="Classified canonical use case ID.",
    )
    cognitive_path: CognitivePath = Field(
        default=CognitivePath.SYSTEM2_DELIBERATIVE,
        description="Selected initial cognitive execution path.",
    )
    region: str = Field(
        default="mekong",
        description="Target region tag ('mekong' or 'amazon').",
    )
    epoch_years: list[int] = Field(
        default_factory=lambda: [2005, 2024],
        description="Target epoch years in [2001, 2026].",
    )
    pentad_range: tuple[int, int] = Field(
        default=(11, 22),
        description="Climatological Pentad interval (1..73).",
    )
    h3_resolution: int = Field(
        default=7,
        description="Uber H3 resolution (7 for regional phenology, 8 for tactical field).",
    )
    stakeholder_tier: StakeholderTier = Field(
        default=StakeholderTier.CLIMATE_SCIENTIST,
        description="Target stakeholder formatting tier.",
    )
    urgency_level: str = Field(
        default="nominal",
        description="Urgency classification ('nominal', 'elevated', 'flash_crisis').",
    )


class VerifiedFactEntry(BaseModel):
    """A single immutable numerical fact produced by a deterministic @tool call."""

    fact_key: str
    numeric_value: float
    unit: str = ""
    source_tool: str
    provenance_tag: str = "flare_chronos_core"


class VerificationReport(BaseModel):
    """Result of checking a draft response against the VerifiedFactsLedger."""

    passed: bool
    checked_numbers_count: int
    verified_numbers: list[float] = Field(default_factory=list)
    unverified_numbers: list[float] = Field(default_factory=list)
    unresolved_citations: list[str] = Field(default_factory=list)
    feedback_message: str = ""


class VerifiedFactsLedger(BaseModel):
    """Per-session immutable registry of tool-computed numbers (ADR-0005)."""

    entries: list[VerifiedFactEntry] = Field(default_factory=list)
    exempt_numbers: set[float] = Field(
        default_factory=lambda: {
            0.0,
            1.0,
            2.0,
            3.0,
            4.0,
            5.0,
            6.0,
            7.0,
            8.0,
            10.0,
            11.0,
            12.0,
            13.0,
            14.0,
            15.0,
            20.0,
            22.0,
            25.0,
            26.0,
            30.0,
            45.0,
            47.0,
            50.0,
            55.0,
            73.0,
            85.0,
            95.0,
            100.0,
            375.0,
            705.0,
            829.0,
            2000.0,
            2001.0,
            2002.0,
            2003.0,
            2004.0,
            2005.0,
            2006.0,
            2007.0,
            2008.0,
            2009.0,
            2010.0,
            2011.0,
            2012.0,
            2013.0,
            2014.0,
            2015.0,
            2016.0,
            2017.0,
            2018.0,
            2019.0,
            2020.0,
            2021.0,
            2022.0,
            2023.0,
            2024.0,
            2025.0,
            2026.0,
            2027.0,
        }
    )

    def ingest_tool_payload(
        self, tool_name: str, payload: Any, prefix: str = ""
    ) -> None:
        """Recursively harvest all numeric fields from a deterministic tool output."""
        if isinstance(payload, str):
            try:
                parsed = json.loads(payload)
            except ValueError:
                parsed = None
            if parsed is not None and not isinstance(parsed, str):
                self.ingest_tool_payload(tool_name, parsed, prefix)
                return
            # Also ingest numeric tokens embedded inside tool string fields (e.g., bounding boxes)
            for idx, tok in enumerate(
                re.findall(r"(?<![A-Za-z0-9_])-?\d+(?:\.\d+)?(?![A-Za-z0-9_])", payload)
            ):
                try:
                    self.entries.append(
                        VerifiedFactEntry(
                            fact_key=f"{prefix}_str[{idx}]",
                            numeric_value=float(tok),
                            source_tool=tool_name,
                        )
                    )
                except ValueError:
                    continue
            return

        if isinstance(payload, dict):
            for k, v in payload.items():
                sub_key = f"{prefix}.{k}" if prefix else str(k)
                self.ingest_tool_payload(tool_name, v, sub_key)
        elif isinstance(payload, list):
            for idx, item in enumerate(payload):
                self.ingest_tool_payload(tool_name, item, f"{prefix}[{idx}]")
        elif isinstance(payload, int | float) and not isinstance(payload, bool):
            val = float(payload)
            self.entries.append(
                VerifiedFactEntry(
                    fact_key=prefix or "value",
                    numeric_value=val,
                    source_tool=tool_name,
                )
            )
            # Also register absolute value and 1-decimal / integer rounded variants
            # so legitimate display formatting of the exact tool output is recognized
            self.entries.append(
                VerifiedFactEntry(
                    fact_key=f"{prefix}_round1",
                    numeric_value=round(val, 1),
                    source_tool=tool_name,
                )
            )
            self.entries.append(
                VerifiedFactEntry(
                    fact_key=f"{prefix}_round2",
                    numeric_value=round(val, 2),
                    source_tool=tool_name,
                )
            )

    def verify_draft_text(
        self, draft_text: str, rel_tolerance: float = 0.008
    ) -> VerificationReport:
        """Verify that every non-structural number in `draft_text` comes from a Tool Call."""
        cleaned = re.sub(r"UC-(?:S1\.)?\d+(?:\.\d+)?", "", draft_text)
        cleaned = re.sub(r"ADR-000\d", "", cleaned)
        cleaned = re.sub(r"P\d{2}", "", cleaned)
        cleaned = re.sub(
            r"H3\s*Res(?:olution)?\s*[78]", "", cleaned, flags=re.IGNORECASE
        )
        cleaned = re.sub(
            r"\b\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)?",
            "",
            cleaned,
        )

        raw_matches = re.findall(
            r"(?<![A-Za-z0-9_])-?\d+(?:,\d{3})*(?:\.\d+)?(?![A-Za-z0-9_])", cleaned
        )
        known_values = [e.numeric_value for e in self.entries]

        verified: list[float] = []
        unverified: list[float] = []

        for token in raw_matches:
            norm = token.replace(",", "")
            try:
                num = float(norm)
            except ValueError:
                continue

            if abs(num) in self.exempt_numbers or num in self.exempt_numbers:
                verified.append(num)
                continue

            matched = False
            for kv in known_values:
                if abs(num - kv) <= max(1e-3, abs(kv) * rel_tolerance) or abs(
                    abs(num) - abs(kv)
                ) <= max(1e-3, abs(kv) * rel_tolerance):
                    matched = True
                    break
            if matched:
                verified.append(num)
            else:
                unverified.append(num)

        passed = len(unverified) == 0
        msg = (
            "All numerical claims verified against VerifiedFactsLedger."
            if passed
            else (
                f"VIOLATION OF DETERMINISTIC TOOL GATE: Unverified numbers {unverified} "
                "detected in draft. Re-synthesize strictly using numbers from Tool outputs."
            )
        )
        return VerificationReport(
            passed=passed,
            checked_numbers_count=len(verified) + len(unverified),
            verified_numbers=verified,
            unverified_numbers=unverified,
            feedback_message=msg,
        )


def verify_grounded_draft(
    draft_text: str,
    ledger: VerifiedFactsLedger,
    rel_tolerance: float = 0.008,
) -> tuple[str, VerificationReport]:
    """Resolve `{{fact_key}}` citations and verify the resolved text.

    Returns the resolved text and the verification report. A citation that no
    deterministic tool produced is a grounding error and fails the report even
    when every number in the draft is verified.
    """
    citations = {
        entry.fact_key: entry.numeric_value
        for entry in ledger.entries
        if not entry.fact_key.endswith(("_round1", "_round2"))
    }
    resolved, unresolved = resolve_citations(draft_text, citations)
    report = ledger.verify_draft_text(resolved, rel_tolerance=rel_tolerance)
    if unresolved:
        report.unresolved_citations = sorted(set(unresolved))
        report.passed = False
        report.feedback_message = (
            "VIOLATION OF DETERMINISTIC TOOL GATE: the draft cited "
            f"{report.unresolved_citations} which no deterministic tool produced. "
            "Cite only the keys listed in the available facts list."
        )
    return resolved, report


class HarnessState(TypedDict):
    """LangGraph State schema shared across System 1, System 2, ToolNode, and Verifier."""

    messages: Annotated[list[BaseMessage], add_messages]
    user_query: str
    extracted_entity: dict[str, Any]
    cognitive_path: str
    pruned_tool_names: list[str]
    escalated_from_system1: bool
    escalation_reason: str
    flash_alert_payload: dict[str, Any] | None
    verified_ledger_entries: list[dict[str, Any]]
    verification_report: dict[str, Any]
    self_correction_retries: int
    distilled_cache_hit: bool
    final_briefing: str
    reasoning_trace: list[str]
    live_telemetry: dict[str, Any]
    synthesis_mode: str
