"""The classification channel for the System 1 Reflexive Layer.

The Reflexive Layer answers one set of questions about the operator's request
before any tool runs: which analysis the request needs, which area of interest
it concerns, whether it needs multi-step deliberation, and whether it is
urgent. The model answers through a structured tool call, so the harness reads a
well-typed classification instead of parsing prose.

Assigning the analysis is the part only this layer can do. The System 2 model
picks the tool; the Reflexive Layer says which of the twenty analyses the
request is, and that answer becomes the use case, the cognitive tier, the tool
surface and the report title.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from langchain_core.tools import tool
from pydantic import Field

CLASSIFY_TOOL_NAME = "classify_request"

# The analysis menu. Every use case in the registry has one line, so the model
# reads a catalogue of analyses rather than a catalogue of tools.
USE_CASE_MENU: dict[str, str] = {
    "UC-S1.1": "triage the intent and the urgency of a request",
    "UC-S1.2": "extract the spatio-temporal entity of a request",
    "UC-S1.3": "single-hop verified metric lookup for one region and epoch",
    "UC-S1.4": "immediate near-real-time flash alert for active fire",
    "UC-S1.5": "assemble a fact card for one stakeholder",
    "UC-1.1": "decompose a fire regime shift into sensor artifact and physical change",
    "UC-1.2": "diagnose why two sensors disagree about one detection",
    "UC-1.3": "classify the origin of thermal detections",
    "UC-2.1": "detect an early-onset burning phenological phase shift",
    "UC-2.2": "compute uncertainty-aware tactical dispatch for rangers",
    "UC-2.3": "assemble a cross-verified multi-stakeholder situation briefing",
    "UC-3.1": "simulate the effect of constellation retirement",
    "UC-3.2": "run a multi-hop spatio-temporal cube query over the archive",
    "UC-3.3": "audit the biome recalibration and its goodness of fit",
    "UC-4.1": "audit orbital drift and solar zenith angle stability",
    "UC-4.2": "audit near-real-time versus standard processing fidelity",
    "UC-4.3": "plan the provider rate-limit budget across cached slices",
    "UC-5.1": "audit the carbon baseline for REDD+ reporting",
    "UC-5.2": "evaluate a burn-ban policy counterfactual",
    "UC-5.3": "forensic analysis of transboundary fire propagation",
}

UseCaseChoice = Literal[
    "UC-S1.1",
    "UC-S1.2",
    "UC-S1.3",
    "UC-S1.4",
    "UC-S1.5",
    "UC-1.1",
    "UC-1.2",
    "UC-1.3",
    "UC-2.1",
    "UC-2.2",
    "UC-2.3",
    "UC-3.1",
    "UC-3.2",
    "UC-3.3",
    "UC-4.1",
    "UC-4.2",
    "UC-4.3",
    "UC-5.1",
    "UC-5.2",
    "UC-5.3",
]

_USE_CASE_CATALOGUE = "; ".join(
    f"{use_case} = {description}" for use_case, description in USE_CASE_MENU.items()
)


@tool
def classify_request(
    region: str,
    is_deliberative: bool,
    urgency: bool,
    use_case: Annotated[UseCaseChoice, Field(description=_USE_CASE_CATALOGUE)],
    confidence: float = 0.5,
    focus_epoch: int | None = None,
) -> dict[str, Any]:
    """Classify the operator's request before any tool runs.

    Call this exactly once, first, and call nothing else. `region` is the
    study area: "mekong" for the Mekong basin, Mainland Southeast Asia or
    Vietnam; "amazon" for the Amazon basin or South America. `is_deliberative`
    is true when answering needs multi-step causal attribution, cross-sensor
    forensics, a counterfactual simulation or an audit, rather than one direct
    metric lookup or a flash alert. `urgency` is true for an active,
    time-critical fire situation that needs an immediate near-real-time alert.
    `use_case` is the one analysis the request needs, chosen from the
    catalogue in its description. `focus_epoch` is the epoch the request
    centres on when it names none, as a four-digit year between 2000 and
    2026. `confidence` is your confidence in this classification, between 0
    and 1.
    """
    return {
        "region": region,
        "is_deliberative": is_deliberative,
        "urgency": urgency,
        "use_case": use_case,
        "focus_epoch": focus_epoch,
        "confidence": confidence,
    }


def classification_answers(args: dict[str, Any], model_id: str) -> dict[str, Any]:
    """Map the classification tool arguments onto the answers shape.

    The shape matches a typed-questions answer so the harness reads both
    protocols the same way. The confidence is the model's own estimate, which
    is recorded as self-reported.
    """
    confidence = float(args.get("confidence", 0.5) or 0.5)
    focus_epoch = args.get("focus_epoch")
    return {
        "model": model_id,
        "confidence_source": "self_reported",
        "answers": {
            "region": {
                "type": "choice",
                "choice": str(args.get("region") or "").strip().lower(),
                "confidence": confidence,
            },
            "is_deliberative": {
                "type": "noul",
                "noul": 1.0 if args.get("is_deliberative") else 0.0,
            },
            "urgency": {"type": "noul", "noul": 1.0 if args.get("urgency") else 0.0},
            "use_case": {
                "type": "choice",
                "choice": str(args.get("use_case") or "").strip(),
            },
            "focus_epoch": {
                "type": "choice",
                "choice": str(focus_epoch) if focus_epoch else "",
            },
        },
    }
