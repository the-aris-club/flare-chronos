"""Review Runs: runs that raised a Sign-off Request, derived from the Run Event Log.

A Review Run is a pure projection of what the run emitted and what the audit
record holds, so Review shows exactly what the reviewer saw live (ADR-0016).
"""

from __future__ import annotations

import re
from typing import Any, Literal

# The ledger also holds rounded copies (`x_round1`) and fragments of string values
# (`x_str[0]`) so the verifier can match prose; a reviewer needs each fact once.
_DERIVED_KEY = re.compile(r"(_round\d+|_str\[\d+\])$")

ReviewStatus = Literal["needs", "published", "withheld", "failed"]


def project_run(
    thread_id: str,
    owner: str,
    events: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Return the Review Run for a thread, or None if it never raised a Sign-off Request."""
    request = next((e for e in events if e["type"] == "sign_off_required"), None)
    if request is None:
        return None
    started = next((e for e in events if e["type"] == "run_started"), {})
    if decisions:
        status: ReviewStatus = "published" if decisions[-1]["approved"] else "withheld"
    elif any(e["type"] == "run_failed" for e in events):
        status = "failed"
    else:
        status = "needs"
    evidence = request.get("evidence") or {}
    tools: list[str] = []
    for event in events:
        if event["type"] == "tool_result":
            tools.extend(t for t in event.get("tools", []) if t not in tools)
    return {
        "id": thread_id,
        "owner": owner,
        "use_case_id": request.get("use_case_id") or started.get("use_case_id"),
        "status": status,
        "started_at": events[0]["at"],
        "updated_at": events[-1]["at"],
        "mode": started.get("mode", ""),
        "question": request.get("question", ""),
        "briefing": evidence.get("final_briefing", ""),
        "verification": evidence.get("verification_report") or {},
        "self_corrections": evidence.get("self_corrections", 0),
        "entity": evidence.get("entity") or {},
        "facts": [
            {
                "fact_key": f["fact_key"],
                "value": f["numeric_value"],
                "unit": f.get("unit", ""),
                "source_tool": f["source_tool"],
                "provenance": f.get("provenance_tag", ""),
            }
            for f in evidence.get("verified_ledger_entries", [])
            if not _DERIVED_KEY.search(f["fact_key"])
        ],
        "tools": tools,
    }


SUMMARY_FIELDS = (
    "id",
    "owner",
    "use_case_id",
    "status",
    "started_at",
    "updated_at",
)


def summarize(run: dict[str, Any]) -> dict[str, Any]:
    """The queue row: the run without its evidence."""
    return {key: run[key] for key in SUMMARY_FIELDS}
