---
status: accepted
---

# The Workbench Has One Mode: Real Data and the Real API

**Builds on** [ADR-0011](./0011-web-facing-ai-service.md).

The Workbench is the web client ADR-0011 hardened the service for. We build it with a single mode. The static surfaces (calendar, phenology clock, before/after comparator, evidence) read the versioned exported artifact, and the briefing and sign-off surface calls the live `ai-service` with an authenticated principal. There is no Replay mode, no recorded runs and no placeholder briefing. When the service is unreachable, the briefing panel says so and reports the degradation tier; the static surfaces keep working.

The Demo Walkthrough follows the same rule: its data steps use the exported artifact, and its briefing and sign-off steps run a real use case against the service. The map opens on a Region Globe and hands over to a flat equal-area-faithful map for analysis, because the argument of the project is about areas in kilometres, which a globe distorts at fire-scene zoom.

We chose this because a Replay mode would show a briefing and an Approve button that no model produced and no principal decided. That is the exact failure the verification gate and the identity-bound sign-off exist to prevent, and a reviewer cannot tell a replay from a run.

## Considered Options

- **Live plus Replay, Replay by default**: Always works, even with no model node. Rejected — a replayed run presented beside real data blurs measurement and recording, and the mode banner that would separate them is exactly what a hurried reader skips.
- **Replay only for a public preview**: Cheap to host. Rejected for the same reason, and because it creates a second code path that drifts from the real contract.
- **Globe as the main surface for everything**: Striking. Rejected — the calendar, comparator and KPIs are not geographic, and a globe distorts the iso-area comparison the project rests on.

## Consequences

- A public demo needs a reachable `ai-service`, reachable model nodes for `--mode live`, CORS set for the Workbench origin, and a short-lived demo token with the approver role issued out of band. Without them the briefing panel shows the unavailable state.
- Automated end-to-end tests run against the deterministic harness, which still exercises the real API and event stream; the full flow against live models is run by hand.
- The frontend must read the event stream with `fetch`, since `EventSource` cannot send the bearer header.
- Adding a Replay mode later would have to supersede this decision, not slip in as a flag.

## Amendment 2026-11-01: demo simulator and fixture Review runs

The supplied design export has no review queue, audit or sign-off endpoint, and the user asked for the full design surface without a fixture-mode flag or prototype banner. The Workbench therefore ships a local service simulator (Up / Degraded / Down, token handshake, run stream, retry) over the RUN-0412 sample, and the Review queue/run/audit read the design fixture runs. This supersedes the "no recorded runs" clause for the demo build only.

The boundaries remain explicit: seven `TODO(api)` markers replace the run list/detail, decision, audit, briefing connect and briefing run with the real HTTP calls, and the Workbench never treats the simulated run as production evidence. The production rule in this ADR still applies to any deployment that connects a real analysis service.
