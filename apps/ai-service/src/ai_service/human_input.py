"""Human interaction tools for the FLARE-CHRONOS Dual-System harness.

These tools are not part of the deterministic tool registry. They exist so a
run can pause for a human: the model asks a clarifying question, or a briefing
must be signed off before it is released. Both use LangGraph's `interrupt`,
which suspends the graph at a checkpoint and resumes it with the human's
answer.
"""

from __future__ import annotations

from typing import Any

from langchain_core.tools import tool
from langgraph.types import interrupt

CLARIFICATION_TOOL_NAME = "ask_user_question"


@tool
def ask_user_question(
    question: str,
    options: list[str] | None = None,
) -> str:
    """Ask the operator for information the analysis cannot infer.

    Use this only when the request is genuinely ambiguous and no tool output
    answers the ambiguity, for example an unstated area of interest or an
    unstated epoch. State one question. Add `options` when the choice is
    finite. The operator's answer is returned as the tool result.
    """
    request: dict[str, Any] = {
        "kind": "clarification",
        "question": question,
        "options": list(options or []),
    }
    answer = interrupt(request)
    if isinstance(answer, dict):
        answer = answer.get("answer", answer)
    return str(answer)


HUMAN_INPUT_TOOLS = [ask_user_question]
