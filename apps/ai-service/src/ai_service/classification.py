"""The classification channel for the System 1 Reflexive Layer.

The Reflexive Layer answers one question about the operator's request before
any tool runs: which area of interest it concerns, whether answering it needs
multi-step deliberation, and whether it is urgent. The model answers through a
structured tool call, so the harness reads a well-typed classification instead
of parsing prose.
"""

from __future__ import annotations

from typing import Any

from langchain_core.tools import tool

CLASSIFY_TOOL_NAME = "classify_request"


@tool
def classify_request(
    region: str,
    is_deliberative: bool,
    urgency: bool,
    focus_epoch: int | None = None,
    confidence: float = 0.5,
) -> dict[str, Any]:
    """Classify the operator's request before any tool runs.

    Call this exactly once, first, and call nothing else. `region` is the
    study area: "mekong" for the Mekong basin, Mainland Southeast Asia or
    Vietnam; "amazon" for the Amazon basin or South America. `is_deliberative`
    is true when answering needs multi-step causal attribution, cross-sensor
    forensics, a counterfactual simulation or an audit, rather than one direct
    metric lookup or a flash alert. `urgency` is true for an active,
    time-critical fire situation that needs an immediate near-real-time alert.
    `focus_epoch` is the epoch the request centres on when it names none, as a
    four-digit year between 2000 and 2026. `confidence` is your confidence in
    this classification, between 0 and 1.
    """
    return {
        "region": region,
        "is_deliberative": is_deliberative,
        "urgency": urgency,
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
            "focus_epoch": {
                "type": "choice",
                "choice": str(focus_epoch) if focus_epoch else "",
            },
        },
    }
