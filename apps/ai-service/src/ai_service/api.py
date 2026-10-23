"""The web-facing analysis API (ADR-0011).

FastAPI app with bearer-token identity, identity-bound sign-off, SSE with event
ids, a per-run time budget and CORS. The Sign-off Principal comes from validated
token claims and never from the request body.

Scope note: events carry ids, but a dropped connection is not replayed; a client
that reconnects with Last-Event-ID starts a fresh read of the checkpointed
thread. Persisting per-thread events is a separate, larger change.
"""

from __future__ import annotations

import asyncio
import json
import os
import tempfile
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Any
from uuid import uuid4

import jwt
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from ai_service.events import HarnessEvent
from ai_service.harness import DEFAULT_CHECKPOINT_PATH, FlareChronosDualSystemHarness
from ai_service.schemas import UseCaseId
from ai_service.store import RunStore

DEMO_PAGE = Path(__file__).parent / "demo" / "index.html"
DEFAULT_STORE_PATH = DEFAULT_CHECKPOINT_PATH.with_name("service.sqlite")
DEFAULT_RUN_TIMEOUT_S = 120.0
APPROVER_ROLE = "approver"


@dataclass(frozen=True)
class AuthConfig:
    """How bearer tokens are validated. ``disabled`` is for the local demo only."""

    key: str | None = None
    algorithms: tuple[str, ...] = ("HS256",)
    issuer: str | None = None
    audience: str | None = None
    disabled: bool = False

    @classmethod
    def from_env(cls) -> AuthConfig:
        if os.environ.get("AI_SERVICE_AUTH") == "disabled":
            return cls(disabled=True)
        return cls(
            key=os.environ.get("AI_SERVICE_JWT_KEY"),
            algorithms=tuple(
                os.environ.get("AI_SERVICE_JWT_ALGORITHMS", "HS256").split(",")
            ),
            issuer=os.environ.get("AI_SERVICE_JWT_ISSUER"),
            audience=os.environ.get("AI_SERVICE_JWT_AUDIENCE"),
        )


@dataclass(frozen=True)
class Principal:
    """The authenticated identity behind a request."""

    sub: str
    roles: frozenset[str] = field(default_factory=frozenset)


class ResumeRequest(BaseModel):
    thread_id: str = Field(min_length=1)
    approved: bool
    reason: str = ""


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(401, detail, headers={"WWW-Authenticate": "Bearer"})


def authenticate(request: Request) -> Principal:
    cfg: AuthConfig = request.app.state.auth
    if cfg.disabled:
        return Principal("demo", frozenset({APPROVER_ROLE}))
    header = request.headers.get("Authorization", "")
    scheme, _, bearer = header.partition(" ")
    if scheme.lower() != "bearer" or not bearer or not cfg.key:
        raise _unauthorized("a bearer token is required")
    try:
        claims = jwt.decode(
            bearer,
            cfg.key,
            algorithms=list(cfg.algorithms),
            issuer=cfg.issuer,
            audience=cfg.audience,
            options={"require": ["sub"]},
        )
    except jwt.PyJWTError as exc:
        raise _unauthorized(f"invalid token: {exc}") from exc
    return Principal(str(claims["sub"]), frozenset(claims.get("roles") or ()))


def _frames(
    events: AsyncIterator[HarnessEvent], budget_s: float
) -> AsyncIterator[bytes]:
    async def run() -> AsyncIterator[bytes]:
        n = 0
        try:
            async with asyncio.timeout(budget_s):
                async for event in events:
                    n += 1
                    yield f"id: {n}\n".encode() + event.to_sse()
        except TimeoutError:
            failed = HarnessEvent(
                "run_failed",
                {"error": f"run exceeded its time budget of {budget_s:g}s"},
            )
            yield f"id: {n + 1}\n".encode() + failed.to_sse()

    return run()


def create_app(
    *,
    harness: FlareChronosDualSystemHarness | None = None,
    store: RunStore | None = None,
    auth: AuthConfig | None = None,
    run_timeout_s: float | None = None,
    mode: str = "deterministic",
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if app.state.harness is not None:
            yield
            return
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

        DEFAULT_CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
        async with AsyncSqliteSaver.from_conn_string(
            str(DEFAULT_CHECKPOINT_PATH)
        ) as saver:
            app.state.harness = FlareChronosDualSystemHarness(
                mode=mode,  # type: ignore[arg-type]
                enable_cache=True,
                enable_sign_off=True,
                checkpointer=saver,
            )
            yield

    app = FastAPI(
        title="Flare-Chronos analysis API", version="1.0.0", lifespan=lifespan
    )
    app.state.harness = harness
    app.state.store = store or RunStore(DEFAULT_STORE_PATH)
    app.state.auth = auth or AuthConfig.from_env()
    app.state.run_timeout_s = (
        run_timeout_s
        if run_timeout_s is not None
        else float(os.environ.get("AI_SERVICE_RUN_TIMEOUT_S", DEFAULT_RUN_TIMEOUT_S))
    )
    # ponytail: one run at a time; the graph is not proven safe to interleave.
    # Per-thread locks if concurrent users become real.
    app.state.run_lock = asyncio.Lock()

    origins = [o for o in os.environ.get("AI_SERVICE_CORS_ORIGINS", "").split(",") if o]
    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_methods=["GET", "POST"],
            allow_headers=["Authorization", "Content-Type", "Last-Event-ID"],
        )

    def stream_response(
        request: Request, events: AsyncIterator[HarnessEvent]
    ) -> StreamingResponse:
        async def locked() -> AsyncIterator[bytes]:
            async with request.app.state.run_lock:
                async for frame in _frames(events, request.app.state.run_timeout_s):
                    yield frame

        return StreamingResponse(
            locked(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
        )

    @app.get("/", include_in_schema=False)
    def page() -> FileResponse:
        return FileResponse(DEMO_PAGE, media_type="text/html")

    @app.get("/api/v1/analysis/use-cases")
    def use_cases(_: Annotated[Principal, Depends(authenticate)]) -> dict[str, Any]:
        return {"use_cases": [{"id": u.value, "label": u.value} for u in UseCaseId]}

    @app.get("/api/v1/analysis/stream")
    def stream(
        request: Request,
        principal: Annotated[Principal, Depends(authenticate)],
        query: str = "",
        use_case_id: str | None = None,
        thread_id: str | None = None,
    ) -> StreamingResponse:
        query = query.strip()
        if not query:
            raise HTTPException(400, "query is required")
        thread = thread_id or f"run-{uuid4().hex}"
        if not request.app.state.store.claim(thread, principal.sub):
            raise HTTPException(403, "this thread belongs to another principal")
        return stream_response(
            request,
            request.app.state.harness.astream_use_case(
                user_query=query, use_case_id=use_case_id or None, thread_id=thread
            ),
        )

    @app.post("/api/v1/analysis/resume")
    def resume(
        request: Request,
        body: ResumeRequest,
        principal: Annotated[Principal, Depends(authenticate)],
    ) -> StreamingResponse:
        store: RunStore = request.app.state.store
        owner = store.owner_of(body.thread_id)
        if owner is None:
            raise HTTPException(404, "no such run")
        if principal.sub != owner and APPROVER_ROLE not in principal.roles:
            raise HTTPException(403, "only the run's owner or an approver may decide")
        store.record_decision(body.thread_id, principal.sub, body.approved, body.reason)
        answer = {
            "approved": body.approved,
            "reason": body.reason,
            "decided_by": principal.sub,
        }
        return stream_response(
            request, request.app.state.harness.astream_resume(body.thread_id, answer)
        )

    return app


def export_openapi(path: Path) -> None:
    """Write the OpenAPI schema the frontend generates its types from."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        app = create_app(
            harness=FlareChronosDualSystemHarness(mode="deterministic"),
            store=RunStore(Path(tmp) / "unused.sqlite"),
            auth=AuthConfig(disabled=True),
        )
        schema = app.openapi()
    path.write_text(
        json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
