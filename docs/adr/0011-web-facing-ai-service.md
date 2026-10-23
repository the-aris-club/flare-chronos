---
status: accepted
---

# The AI Service Is Built For a Web Frontend

**Extends** [ADR-0008](./0008-model-driven-tool-selection-sign-off-and-event-stream.md).

ADR-0008 made the run observable as an event stream "a web client can consume". The Workbench in the glossary is that client, and it is now the intended consumer. The current server is a stdlib `ThreadingHTTPServer` with one global lock, in-memory `MemorySaver` checkpoints, no authentication, and a resume endpoint that trusts `thread_id` and `decided_by` from the request body. That is adequate for the demo page and unsafe for a user-facing frontend: anyone who learns a thread id can approve a pending Sign-off Request, and a restart silently drops every pending one.

We harden `ai-service` as a backend in four ways.

1. **ASGI server (FastAPI or Starlette)**, with CORS, a per-run timeout, SSE with `Last-Event-ID` reconnect, and an exported OpenAPI schema committed to the repo and snapshot-tested so the contract cannot drift silently. The frontend generates its TypeScript types from it.
2. **Durable checkpoints** through LangGraph's SQLite checkpointer on a single instance. The checkpointer interface is swappable, so Postgres is a later change, not a rewrite.
3. **Identity-bound Sign-off.** The Sign-off Principal comes from validated JWT claims, never from the request body. A run is bound to the principal that started it, and a resume is rejected unless the caller is that principal or an assigned approver. Each Sign-off Decision is written to an append-only audit record. A single per-deployment bearer token is the stopgap until the frontend exists.
4. **Calendar data is a static artifact.** The frontend reads the Burning Activity Calendar from a versioned static file (JSON or Parquet) carrying a Measured / Interpolated flag per cell, served from a CDN. The API handles analysis and sign-off only.

## Considered Options

- **Keep the stdlib server and call it a demo**: Zero work. Rejected — the frontend is the stated next step, and the forgeable sign-off gate would ship with it.
- **Postgres checkpointer and several workers now**: Right for concurrent users. Rejected for now — the global lock only matters under concurrency we do not have, and the interface lets us move later.
- **A read API over a database for the calendar**: Flexible queries. Rejected for now — the calendar is a batch product rebuilt when the archive changes, so a static artifact is cheaper to run and exactly reproducible.
- **Per-deployment bearer token as the permanent scheme**: Simple. Rejected as the end state — a web app has real users, and one shared secret cannot say who approved an action.

## Consequences

- The sign-off gate becomes meaningful: the Sign-off Decision names an authenticated principal, and the audit record outlives a restart.
- A restart no longer drops pending sign-offs, but a single instance with one SQLite file is a single point of failure. Moving to Postgres is the documented upgrade path.
- The calendar cannot be queried ad hoc through the API. Adding a read API later is additive and does not change this decision.
- JWT validation adds an identity-provider dependency and a configuration surface (issuer, audience, key source) that the demo did not have.
