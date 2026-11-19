---
status: accepted
---

# Workbench on Vercel, AI service on the VPS

## Context

The DNS record for `flare-chronos.resonance.io.vn` kept the old VPS address when we changed the host address. Cloudflare sent error 522 to users. Both containers ran normally. The application did not fail. The deployment had one origin address in Cloudflare DNS. It had no second frontend.

Moving both parts away from the VPS needs more than a configuration change. The AI service stores two SQLite files and a sign-off checkpoint. It uses one lock in one process. It loads the native `h3` library. It reads 151 MB of FIRMS CSV files when it handles a request. Cloudflare Workers run Python in Pyodide. They cannot load native `h3`. Vercel Hobby limits a function to 300 seconds. This equals the configured model timeout.

## Decision

Host the Next.js Workbench on Vercel. Use it as the primary frontend. Keep the FastAPI service on the VPS. Use the host `api.flare-chronos.resonance.io.vn` for that service. Do not add a Cloudflare Worker. A split host name removes the origin address that can drift.

The Vercel build sets `NEXT_PUBLIC_AI_SERVICE_URL=https://api.flare-chronos.resonance.io.vn`. The API sets `AI_SERVICE_CORS_ORIGINS=https://flare-chronos.resonance.io.vn`. We copy two processed JSON files into `apps/workbench/data/processed`. We add them to the Next.js server trace.

When the VPS API fails, the Vercel pages still show bundled data. The service connection shows `Unavailable` and retries. We accept this state.

## Consequences

- A DNS or host failure on the VPS no longer stops the whole site. It stops the API only.
- Briefing, sign-off, and the review queue still need the VPS. Full API resilience needs a separate move to a durable external store and object storage. See ADR-0011.
- The VPS Workbench container and the nginx `/` proxy stay for one release cycle. They are a rollback path. We send no traffic to them.
- Frontend releases use Vercel Git integration. API releases keep the tag-based GHCR and CD flow.
