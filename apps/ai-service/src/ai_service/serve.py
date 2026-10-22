"""A small server that exposes one harness run as a live event stream.

The harness is the product; this server only puts a browser in front of it.
It exposes the two endpoints the architecture document specifies:

    GET  /api/v1/analysis/stream      run one use case, stream its events
    POST /api/v1/analysis/resume      answer a run that is waiting for a human

and serves a demo page at `/` that shows the run as it happens: the
classification, the tool calls, the reasoning, the verification and the
briefing, with the approval buttons when the run asks for a human.

The server uses the standard library only, and the default mode is the
deterministic harness, so the demo runs anywhere without a credential.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import threading
from collections.abc import AsyncIterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from ai_service.events import HarnessEvent
from ai_service.harness import FlareChronosDualSystemHarness
from ai_service.schemas import UseCaseId

DEMO_PAGE = Path(__file__).parent / "demo" / "index.html"


class ServerState:
    """The harness, plus the lock that keeps one run at a time.

    The graph is not safe to run twice at once, so the runs queue.
    """

    def __init__(self, mode: str) -> None:
        self.harness = FlareChronosDualSystemHarness(
            mode=mode,  # type: ignore[arg-type]
            enable_cache=True,
            enable_sign_off=True,
        )
        self.lock = threading.Lock()

    def use_cases(self) -> list[dict[str, str]]:
        return [
            {"id": use_case.value, "label": use_case.value.replace("UC-", "UC-")}
            for use_case in UseCaseId
        ]


class AnalysisRequestHandler(BaseHTTPRequestHandler):
    """Serves the demo page, the event stream and the resume call."""

    server_version = "flare-chronos-demo/1.0"

    # -- plumbing ---------------------------------------------------------

    @property
    def state(self) -> ServerState:
        return self.server.state  # type: ignore[attr-defined]

    def log_message(self, format: str, *args: Any) -> None:
        pass

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_page(self) -> None:
        try:
            body = DEMO_PAGE.read_bytes()
        except OSError:
            self._send_json(500, {"error": "the demo page is missing"})
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _begin_stream(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

    def _pump(self, events: AsyncIterator[HarnessEvent]) -> None:
        """Write every event of one run as a Server-Sent Events frame."""

        async def drain() -> None:
            async for event in events:
                self.wfile.write(event.to_sse())
                self.wfile.flush()

        with self.state.lock:
            try:
                asyncio.run(drain())
            except (BrokenPipeError, ConnectionResetError):
                pass

    # -- routes -----------------------------------------------------------

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self._send_page()
        elif parsed.path == "/api/v1/analysis/use-cases":
            self._send_json(200, {"use_cases": self.state.use_cases()})
        elif parsed.path == "/api/v1/analysis/stream":
            self._run_stream(parsed)
        else:
            self._send_json(404, {"error": "not found", "path": parsed.path})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/v1/analysis/resume":
            self._send_json(404, {"error": "not found", "path": parsed.path})
            return
        length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            self._send_json(400, {"error": "the request body is not JSON"})
            return
        thread_id = str(payload.get("thread_id") or "")
        if not thread_id:
            self._send_json(400, {"error": "thread_id is required"})
            return
        answer: dict[str, Any] = {
            "approved": bool(payload.get("approved")),
            "reason": str(payload.get("reason") or ""),
            "decided_by": str(payload.get("decided_by") or ""),
        }
        self._begin_stream()
        self._pump(self.state.harness.astream_resume(thread_id, answer))

    def _run_stream(self, parsed: Any) -> None:
        params = parse_qs(parsed.query)
        query = (params.get("query") or [""])[0].strip()
        if not query:
            self._send_json(400, {"error": "query is required"})
            return
        use_case_id = (params.get("use_case_id") or [""])[0].strip() or None
        thread_id = (params.get("thread_id") or [f"demo-{uuid4().hex[:8]}"])[0]
        self._begin_stream()
        self._pump(
            self.state.harness.astream_use_case(
                user_query=query,
                use_case_id=use_case_id,
                thread_id=thread_id,
            )
        )


class AnalysisServer(ThreadingHTTPServer):
    """The server, with the harness it runs and a quiet socket layer."""

    daemon_threads = True
    state: ServerState

    def handle_error(self, request: Any, client_address: Any) -> None:
        """A browser that closes the stream early is not an error."""
        return


def serve(
    host: str = "127.0.0.1", port: int = 8765, mode: str = "deterministic"
) -> None:
    """Run the server until interrupted."""
    state = ServerState(mode)
    server = AnalysisServer((host, port), AnalysisRequestHandler)
    server.state = state
    print(f"Flare-Chronos demo on http://{host}:{port} (mode={mode})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Serve the harness run as a live event stream with a demo page."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument(
        "--mode",
        default="deterministic",
        choices=["deterministic", "live"],
        help="the deterministic harness needs no credential; live calls the model",
    )
    args = parser.parse_args()
    serve(host=args.host, port=args.port, mode=args.mode)


if __name__ == "__main__":
    main()
