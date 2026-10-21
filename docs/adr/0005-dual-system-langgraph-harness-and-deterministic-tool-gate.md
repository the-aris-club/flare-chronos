# 0005. Dual-System (System 1 ⇄ System 2) LangGraph Harness and Deterministic Tool Gate

**Status:** accepted

We orchestrate all 20 AI decision-support and scientific reasoning use cases (5 System-1 reflexive use cases and 15 System-2 deliberative use cases) in `apps/ai-service` using a cyclic **LangGraph `StateGraph`** pairing the free OpenCode v2 `jev` model (`System 1 Reflexive Layer`) with the self-hosted `qwen3.8-flash-next` reasoning model (`System 2 Deliberative Layer`, `reasoningEffort: "xhigh"`), governed by a mandatory **Deterministic Tool Gate** and a **Numeric Grounding Verifier** backed by a per-session **Verified Facts Ledger**.

## Context & Trade-Offs

 Satellite active-fire harmonization requires exact spherical scan-angle geometry ($\Delta S(\theta)\times\Delta T(\theta)$), astronomical solar zenith angle ($\text{SZA} < 85^\circ$), two-stage radiative power calibration (`EQM`), and $O(N)$ spatio-temporal episode clustering across $1,609,182$ real NASA FIRMS detections. Allowing an LLM to estimate or calculate these quantities via next-token prediction introduces arithmetic hallucinations and violates radiometric conservation ($\sum_h w_{p,h} = 1.0$). Conversely, running a deep reasoning model (`qwen3.8-flash-next` at `xhigh` effort) on every trivial single-metric lookup or flash alert introduces unnecessary latency.

## Decision

1. **Framework Choice (`LangGraph` + `LangChain Core` + `Pydantic v2`):**
   - We use `langgraph.graph.StateGraph` and `langgraph.prebuilt.ToolNode` with `MemorySaver` checkpointing rather than a custom loop or linear agent chain, enabling explicit conditional routing between `System 1` and `System 2` as well as self-correction loopback edges when unverified numbers are detected.
2. **Dual-Process Symbiosis (`System 1: jev` ⇄ `System 2: qwen3.8-flash-next`):**
   - **System 1 (`opencode-v2 / jev`):** Handles fast intent & urgency triage (`UC-S1.1`), Pydantic spatio-temporal entity extraction (`UC-S1.2`), single-hop deterministic metric lookup (`UC-S1.3`), flash NRT crisis alerting (`UC-S1.4`), and multi-stakeholder briefing synthesis (`UC-S1.5`).
   - **System 2 (`qwen-local / qwen3.8-flash-next`):** Handles all 15 multi-step causal, forensic, counterfactual, QA/QC, and policy auditing use cases (`UC-1.1` through `UC-5.3`) with `reasoningEffort="xhigh"` and `reasoning_content` extraction.
   - **Mutual Support Protocol:** System 1 prunes the tool surface and escalates dynamically to System 2 whenever raw-vs-harmonized divergence exceeds $200\%$ or South Atlantic Anomaly (`SAA`) flags trigger; System 2 distills verified causal conclusions back into System 1's `VerifiedPatternCache`.
3. **Zero-Math-By-LLM Rule (`Deterministic Tool Gate` & `VerifiedFactsLedger`):**
   - Every numerical calculation and data retrieval is exposed as a strict `@tool` (8 atomic physics/data tools + 15 domain diagnostic/simulation tools).
   - Every tool call records its exact numeric outputs into the session's `VerifiedFactsLedger`, and the `NumericGroundingVerifier` node blocks any response containing unverified numbers.
