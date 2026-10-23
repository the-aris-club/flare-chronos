# Flare-Chronos AI Service Context

Dual-process cognitive decision-support and autonomous scientific reasoning context orchestrating fast situational triage (System 1) and multi-step hypothesis verification (System 2) over deterministic cross-sensor fire harmonization tools.

## Language

### Cognitive Architecture & Harness

**System 1 Reflexive Layer**:
The tier that reports. It assigns the analysis a request needs, classifies intent and extracts the spatio-temporal entity, retrieves facts through the Atomic Tools, and returns a grounded fact card or a flash alert. It never derives an analysis, never orchestrates a tool sequence, and never writes an analytical narrative.
_Avoid_: Fast chatbot, simple prompt, router-only agent

**Analysis Assignment**:
The Reflexive Layer's answer to "which of the twenty analyses does this request need". The assignment decides the cognitive tier, the tool surface, the cache key and the report title. The System 2 Deliberative Layer still chooses the tool, so a wrong assignment shows up as a wrong title rather than a wrong calculation.
_Avoid_: Routing, intent label, model selection

**Triage Confidence**:
The Reflexive Layer's estimate of how well it classified a request. A decision endpoint returns a calibrated probability; a chat endpoint returns the model's own estimate, which is recorded as self-reported and must never be presented as calibrated. The harness records which of the two produced the answer, so a self-reported estimate is never read as a calibrated one.
_Avoid_: Confidence score, certainty, probability of correctness

**System 2 Deliberative Layer**:
The tier that explains. It chooses and orchestrates the deterministic tools — atomic and domain diagnostic — until the question is answered, asks the operator when the request is ambiguous, and writes the analytical narrative whose quantities are injected from the Verified Facts Ledger.
_Avoid_: Slow model, chain-of-thought prompt, free-form reasoner

**Dual-Process Symbiosis**:
The bidirectional cooperation protocol in which the System 1 Reflexive Layer classifies and prunes the tool surface for the System 2 Deliberative Layer, while the System 2 Deliberative Layer distills verified causal patterns back into the System 1 Reflexive Layer's cache.
_Avoid_: Model fallback, simple routing, agent handoff

**Deterministic Tool Gate**:
The strict architectural boundary requiring every physical, geometric, radiometric, or statistical quantity to be computed exclusively by invoking verified domain tools rather than estimated by language model token generation.
_Avoid_: Calculator plugin, optional tool use, code interpreter

**Verified Facts Ledger**:
The immutable per-session registry recording every numerical metric, physical unit, and provenance tag returned by deterministic tool executions during a reasoning trajectory.
_Avoid_: Tool log, scratchpad memory, context history

**Numeric Grounding Verifier**:
The post-synthesis validation gate that resolves a draft's fact citations against the Verified Facts Ledger, cross-checks every numerical claim in the resolved text, and triggers self-correction whenever an unverified number or an unresolved citation is detected.
_Avoid_: Output filter, regex sanitizer, hallucination prompt

**Endpoint Profile**:
The explicit binding that connects one cognitive layer to one language model service, made of a protocol, an endpoint URL, a model identifier, an API key, and request options, resolved entirely from declared configuration.
_Avoid_: Provider config, machine config, ambient credential, agent connection

**Grounded Narrative**:
A briefing whose every quantity is injected by the harness from the Verified Facts Ledger and never written by the language model, which authors only the interpretation.
_Avoid_: LLM-written report, generated summary, AI briefing

**Briefing Assembly**:
The deterministic step that stamps a verified result with its stakeholder tier, its cognitive path, and its synthesis mode.
_Avoid_: Synthesis mode, formatting, templating

**Synthesis Mode**:
The record of which author produced a briefing: the language model, the deterministic formatter, or the deterministic formatter after the Numeric Grounding Verifier rejected the model output.
_Avoid_: Generation mode, output source

### Deterministic Tool Tiers

**Atomic Tool**:
A deterministic tool that returns one physical, geometric or radiometric quantity, or one already-computed record. Atomic Tools are the whole surface of the System 1 Reflexive Layer.
_Avoid_: Basic tool, simple tool, primitive

**Domain Diagnostic Tool**:
A deterministic tool that derives a multi-input analysis, forensic result, simulation or audit from the Atomic Tools. Domain Diagnostic Tools are reachable only by the System 2 Deliberative Layer.
_Avoid_: Complex tool, analysis tool, advanced tool

### Human In The Loop

**Sign-off Request**:
A structured request for a human to authorize one proposed operational action, carrying the grounded evidence that justifies it and the decision the answer must take.
_Avoid_: Approval prompt, confirmation dialog, human review

**Sign-off Decision**:
The recorded answer to a Sign-off Request, naming who decided, when, and on what grounds.
_Avoid_: Approval log, audit trail, sign-off record

**Sign-off Principal**:
The authenticated identity that owns a run or is assigned to approve it, established from validated token claims and never from the request body. A Sign-off Decision names a Sign-off Principal.
_Avoid_: User, approver name, decided-by string, operator

**Clarification Request**:
A request for a human to supply information the analysis cannot infer, raised without authorizing any action.
_Avoid_: Question, prompt, clarification

### Analytical & Tactical Use-Case Concepts

**Regime-Shift Attribution**:
The multi-step causal decomposition separating genuine biomass burning anomalies from artificial hotspot step-jumps caused by satellite constellation expansion and sub-pixel sensitivity shifts.
_Avoid_: Trend explanation, count comparison

**Cross-Sensor Discrepancy Forensics**:
The physical investigation of localized disagreements between co-incident MODIS and VIIRS observations by testing scan-angle detection limits, South Atlantic Anomaly proton spikes, and orbital geolocation drift.
_Avoid_: Error debugging, sensor diff

**Counterfactual Constellation Simulation**:
A controlled analytical experiment that recomputes Harmonized Fire Density and Harmonized Radiative Flux under hypothetical satellite retirements or sensor subsetting to quantify continuity resilience.
_Avoid_: What-if guess, synthetic forecast

**Phenological Phase-Shift Detection**:
The identification of early-onset or delayed-cessation burning regimes by comparing intra-annual Standardized Fire Anomaly Index trajectories against the 26-year Pentad baseline.
_Avoid_: Season shift, early fire alert

**Uncertainty-Aware Tactical Dispatch**:
The operational prioritization of field response resources that accounts for both combined episode probability and the elliptical ground footprint uncertainty ($\Delta S \times \Delta T$) of the detecting sensors.
_Avoid_: Hotspot dispatch, point targeting
