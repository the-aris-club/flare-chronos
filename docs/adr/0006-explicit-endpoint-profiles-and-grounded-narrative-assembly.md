# 0006. Explicit Endpoint Profiles and Grounded Narrative Assembly

**Status:** accepted

**Supersedes:** the credential sourcing and model binding rules of [ADR-0005](./0005-dual-system-langgraph-harness-and-deterministic-tool-gate.md).

We bind each cognitive layer to a language model service through an **Endpoint Profile** — protocol, endpoint URL, model identifier, API key, and request options — resolved from declared configuration only. The System 2 Deliberative Layer then authors the analytical briefing as a **Grounded Narrative**, in which every quantity is injected by the harness from the Verified Facts Ledger rather than written by the model.

## Context & Trade-Offs

The harness originally resolved its model bindings from the host's agent tooling configuration: a per-user authentication store for the System 1 key, a per-user provider file for the System 2 key, and a secondary provider file for the failover target. Three problems followed.

1. **Ambient dependency.** A checkout behaved differently depending on whose machine ran it. The same command could reach a public free endpoint on one laptop and fail on another.
2. **Credential crossing.** The System 1 resolver looked up a provider key that the host's authentication store does not hold, so it fell through to a *different* provider's credential and transmitted that key to a different vendor's endpoint.
3. **Silent degradation.** Four request options declared in the harness configuration — the request timeout, the output token budget, the temperature, and the stream chunk timeout — were never read by the client. The code used its own hardcoded values instead, including a three-and-a-half-second timeout against a long-context reasoning model. The failover path then swallowed the resulting error and returned a fabricated answer, so a telemetry record reported a model call that never happened.

The harness also under-used the language model. The deterministic formatter produced every briefing, so the System 2 Deliberative Layer contributed a reasoning trace that never reached the deliverable. The architecture described in ADR-0005 — a Numeric Grounding Verifier with a self-correction loop — was built to make model-authored prose safe, and was unused for that purpose.

We also rejected two alternatives. **Reading the host's agent configuration explicitly** (a declared path to a declared provider block) keeps the ambient dependency and only makes the coupling intentional. **Letting the model write numbers and detecting violations afterwards** keeps the model as the author of quantities, which makes every violation cost a full extra model round trip and lets the loop exhaust.

## Decision

1. **Endpoint Profile as the only binding.** Each layer declares a protocol (`typed_questions` or `native_chat`), an endpoint URL, a model identifier, the name of an environment variable holding its API key, and its request options. Precedence for every overridable value is: process environment, then the workspace `.env` file, then the harness configuration. No credential, endpoint, or model is ever read from the host's agent tooling configuration.
2. **No provider names in the harness source.** Classes are named for the role they serve and the protocol they speak, never for a vendor. The vendor appears only in configuration, so switching provider is a configuration change.
3. **Fail fast on a missing credential.** A live call without a configured API key raises before any network request. A failed endpoint call raises. The harness never fabricates a model answer, and never reports a model call it did not make.
4. **Grounded Narrative Assembly.** The System 2 layer receives the citation table of the Verified Facts Ledger and writes the narrative citing each quantity as a `{{fact_key}}` placeholder. The harness resolves those placeholders against the ledger and substitutes the values, so the model never writes a number. A placeholder with no ledger entry is a grounding error.
5. **The Numeric Grounding Verifier as a safety net.** After resolution, the verifier still scans the text for stray numbers the model may have written and triggers the self-correction loop. When the loop is exhausted, the harness falls back to the deterministic formatter, so a briefing always exists.
6. **Synthesis Mode as a mandatory telemetry field.** Every result records whether the narrative came from the model, from the deterministic formatter, or from the fallback. A report cannot claim model authorship for a fallback briefing.
7. **Live tests never run in the default pipeline.** The default suite runs the offline harness, which exercises the same graph, tool gate, and ledger without a network call. The live suite is marked `live`, is excluded by default, and runs only from a manually triggered workflow with a concurrency group, so provider credit is spent only on request.

## Consequences

- The harness no longer depends on any host-level agent tooling and behaves identically on a laptop, in CI, and on a deployed host.
- System 2 briefings are model-authored interpretations whose quantities are still traceable to the ledger, which is what the project deliverable needs.
- A reader of a result can tell from the Synthesis Mode field whether a briefing came from the model.
- The live suite costs provider credit and therefore needs a manual trigger and a configured secret.
- The System 1 layer keeps its deterministic formatter, because the typed-questions protocol classifies rather than writes prose.
