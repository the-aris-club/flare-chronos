---
status: accepted
---

# Workbench on Vercel, AI service on the VPS

## Context

The `flare-chronos.resonance.io.vn` DNS record kept the old VPS IP after the host was re-IP'd. Cloudflare returned 522 while both containers were healthy; the application was not down. The deployment had one origin IP in Cloudflare DNS and no second frontend.

Moving both parts off the VPS is not a config change. The AI service keeps two SQLite stores and a cross-request sign-off checkpoint, relies on a single in-process lock, loads the native `h3` library, and reads 151 MB of FIRMS CSVs at request time. Cloudflare Workers run Python in Pyodide and cannot load native `h3`. Vercel Hobby caps functions at 300 s, equal to the configured model timeout.

## Decision

Host the Next.js Workbench on Vercel as the primary frontend. Keep the FastAPI service on the VPS behind `api.flare-chronos.resonance.io.vn`. Split the host names instead of adding a Cloudflare Worker: there is no origin IP for the frontend to drift from.

The Vercel build sets `NEXT_PUBLIC_AI_SERVICE_URL=https://api.flare-chronos.resonance.io.vn`. The API sets `AI_SERVICE_CORS_ORIGINS=https://flare-chronos.resonance.io.vn`. The two processed JSON artifacts are copied into `apps/workbench/data/processed` and included in the Next.js server trace.

We accept degraded mode when the VPS API is down: the Vercel pages still render from bundled data and the service connection shows `Unavailable` with retry.

## Consequences

- A DNS or host failure on the VPS no longer takes the whole site down. It takes the API down only.
- Briefing, sign-off, and the review queue still need the VPS. Full API resilience needs a separate migration to a durable external store and object storage (ADR-0011's Postgres upgrade path).
- The VPS Workbench container and nginx `/` proxy stay for one release cycle as a rollback; no traffic is sent to them.
- Frontend releases follow Vercel Git integration. API releases keep the tag-based GHCR/CD flow.
