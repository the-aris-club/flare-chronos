---
status: accepted
---

# SFAI Operational Tiers and a Separate Calendar Display Threshold

The Standardized Fire Anomaly Index carries **two kinds of threshold**, and we keep them apart on purpose. The *operational tiers* (QUIET, BASELINE, ELEVATED, SEVERE, CRISIS) are risk classifications that drive decisions: SEVERE ($1.75 \le \text{SFAI} < 2.5$) mobilises patrols, CRISIS ($\text{SFAI} \ge 2.5$) raises an out-of-season crisis alarm. The *display threshold* ($+2.2\sigma$) is a rendering convention for one figure — the cyan frame on the Burning Activity Calendar — and nothing else. It sits deliberately below the CRISIS tier so the calendar highlights severe anomalies *before* an alarm is raised, which is the entire point of an early-warning product.

The operational boundaries are named constants in `flare_chronos_core` (`SFAI_SEVERE_THRESHOLD_Z`, `SFAI_CRISIS_THRESHOLD_Z`); the display threshold belongs to `benchmark_cli.figure_renderer` (`SFAI_HIGHLIGHT_Z`). All three are single-sourced, and the guard test in `tests/test_documented_claims_consistency.py` asserts they stay ordered and stay consistent with `docs/04` and `docs/01`.

## Considered Options

- **One threshold for everything (the original intent)**: The Figure 5 caption published `+2.2`, the renderer drew `+2.15`, `docs/04` specified `+2.25`, and the operational boundaries lived at `1.75`/`2.5` — four numbers answering one question ("what SFAI marks a crisis?"), with the display drifting *below* the operational band it was supposed to visualise. Rejected.
- **Display threshold = CRISIS tier (2.5)**: One number, no drift, but the calendar would only outline cells that have already tripped the alarm — defeating the early-warning purpose. Rejected.
- **Display threshold above CRISIS (e.g. 3.0)**: Would outline fewer cells still. Rejected.
- **Separate operational tiers and a lower display threshold (chosen)**: The two questions get two answers, each named for what it is.

## Consequences

- The 2.2 outline is **not** a crisis marker. It is called the *Severe Anomaly Outline* in the glossary, deliberately not "Crisis Anomaly" — the CRISIS tier at 2.5 is the crisis, and reusing its name for a lower threshold is what caused the original confusion. The Figure 5 caption and `docs/04` follow the glossary.
- Changing the operational boundaries means changing `flare_chronos_core` and regenerating Figure 5. Changing the display threshold means changing `figure_renderer.py` and regenerating Figure 5. Both paths run through the same guard test.
- A threshold change is not a doc-only edit. Figure 5 is a build artifact; the published PNG must be regenerated on the canonical toolchain or the caption and the drawn cells disagree.
