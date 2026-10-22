"""Typed event stream and Server-Sent Events encoding for the FLARE-CHRONOS harness.

The harness exposes its run as a stream of typed events. A web client consumes
them over Server-Sent Events; a script consumes them as plain objects. The
encoding is a pure function of the event, so it is testable without a server.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any, Literal

EventType = Literal[
    "run_started",
    "node_completed",
    "tool_result",
    "reasoning",
    "message",
    "sign_off_required",
    "clarification_requested",
    "verification",
    "briefing",
    "run_paused",
    "run_completed",
    "run_failed",
]


@dataclass(slots=True)
class HarnessEvent:
    """One event of the harness stream."""

    type: EventType
    data: dict[str, Any] = field(default_factory=dict)

    def to_sse(self) -> bytes:
        """Encode the event as one Server-Sent Events frame."""
        payload = json.dumps({"type": self.type, **self.data}, ensure_ascii=False)
        return f"event: {self.type}\ndata: {payload}\n\n".encode()


async def to_sse_frames(events: AsyncIterator[HarnessEvent]) -> AsyncIterator[bytes]:
    """Encode a stream of harness events as Server-Sent Events frames."""
    async for event in events:
        yield event.to_sse()
