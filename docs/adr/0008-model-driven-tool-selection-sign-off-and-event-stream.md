# 0008. Model-Driven Tool Selection, Tiered Tool Surfaces, Human Sign-off and an Event Stream

**Status:** accepted

**Extends:** [ADR-0005](./0005-dual-system-langgraph-harness-and-deterministic-tool-gate.md) and [ADR-0006](./0006-explicit-endpoint-profiles-and-grounded-narrative-assembly.md)

The Dual-System harness gives the language model the objective and the rules, not a step-by-step plan. The System 2 Deliberative Layer chooses its own deterministic tool calls from an exposed surface. The System 1 Reflexive Layer becomes the tier that reports rather than the tier that routes by regex. A briefing that authorizes an operational action pauses for a human sign-off. The whole run is observable as a typed event stream that a web client can consume over Server-Sent Events.

## Context & Trade-Offs

After ADR-0006 the harness bound each layer to a model and grounded the narrative, but two things were still off.

**The routing was regex, not reasoning.** `_system1_triage_node` derived the region, the epochs, and the cognitive path from regular expressions over the raw query, and the System 1 model was never consulted on the fifteen deliberative use cases. The architecture in ADR-0005 says System 1 prunes the tool surface for System 2; in practice a regex did the pruning and the model stayed silent. The tier boundary was therefore asserted rather than measured.

**The tool plan was written by the harness, not the model.** The harness decided which tools a use case called and synthesised their arguments. The model contributed a reasoning trace and nothing else. That is safe, but it wastes the capability the endpoint was bought for, and it makes the System 2 Deliberative Layer a formatter rather than a reasoner. We rejected the alternative of free model choice as well: letting the model pick arguments would make the tool arguments, and therefore the recorded facts, non-reproducible.

**There was no place for a human.** A field alert and a tactical dispatch are the two outputs a human must answer for. Nothing in the harness could pause, ask, and resume.

We also rejected building the agent loop on `create_react_agent`. It is deprecated in the installed `langgraph-prebuilt` in favour of `create_agent` from the `langchain` package, which would add a dependency whose middleware system this harness would barely use, and it would fight the custom state the harness carries. `ToolNode` plus `tools_condition`, which LangGraph documents for custom workflows, is already installed, already used, and keeps full control of the state.

## Decision

1. **The model chooses the tools.** System 2 receives the deterministic tool surface and decides which tools to call and with which arguments, in a loop that ends when it stops calling tools. The harness bounds the loop with a reasoning-step budget and falls back to the deterministic formatter when the budget is exhausted.
2. **The tier is defined by the tool surface, not by a use-case list.** The System 1 Reflexive Layer reaches only the Atomic Tools, so the tier that reports can never reach a derivation. The System 2 Deliberative Layer reaches the Atomic Tools, the Domain Diagnostic Tools, and the clarification tool. The raw FIRMS slice harmoniser stays outside the registry and outside the model's reach.
3. **System 1 classifies before it routes.** The triage node asks the classifier for the region, the urgency, and whether the request is deliberative, and merges the answer into the entity. The model's answer may override the inferred cognitive tier only when the operator did not name a use case; an explicit use case always wins. The Reflexive Layer may speak either the typed-questions protocol, whose answer carries a calibrated probability, or the native chat protocol, where the model answers through a structured classification tool and its confidence is self-reported. The harness records which of the two produced the answer, so a self-reported estimate is never read as a calibrated one.
4. **The System 1 fast tier stays a single hop.** The fast tier executes one Atomic Tool and returns a grounded fact card. It never writes an analytical narrative, and it asks no model to write: a fact card is a formatted tool output, so the tier answers without a language-model turn.
5. **Guidance moves into a system prompt.** The domain brief, the tool discipline, the citation protocol, and the clarification rules live in one prompt per tier, in the spirit of a coding agent's system prompt. The harness no longer scripts a step-by-step plan into the conversation.
6. **The model is told to stop.** An early revision told it to call as many tools as the question needs, and it did: one use case burned eight tool rounds and ended on the deterministic floor. The discipline now says to start with the tool that matches the use case, to call the smallest set that answers the question, and to stop once the output answers it.
7. **A deliberating model that says nothing is asked again.** A model in a thinking mode sometimes stops without emitting a tool call or any content. The adapter detects that and repeats the call without deliberation, which always produces a turn.
8. **Sign-off suspends the run.** A use case listed in `requires_sign_off` pauses at a sign-off gate through LangGraph's `interrupt`. The run resumes with the human's answer. A rejected sign-off releases no briefing; the decision is recorded either way.
9. **Clarification is a tool, not a special case.** The model may raise a clarification request through a tool that interrupts the run. It is bounded, and it authorizes nothing. A clarification is answered automatically only by a batch run, never a sign-off.
10. **The run is an event stream.** The harness exposes typed events, and an SSE encoder turns them into frames. A paused run is one segment of the stream; the human's answer starts the next segment with the same thread identifier.
11. **The durable checkpointer is injected.** The harness accepts a checkpointer, so an offline test injects an in-memory one and a sign-off run injects the SQLite one, which lets a paused run survive a process restart.
12. **Retries are bounded and selective.** A model node retries a transport failure, a rate limit or a server error, and never a client error. The deterministic tool node caches its result, because a tool's output is a pure function of its arguments.
13. **The classifier is not a single point of failure.** A rate-limited classifier would otherwise kill every run at its first node. The classification is an enhancement over the provisional extraction, so an unavailable classifier degrades to it and records why.

## Consequences

- The routing decision and the extracted entity now carry a calibrated probability instead of a regex match, and the classification is recorded in the run state and in the telemetry.
- The narrative is authored by the model against the tool surface the tier allows, and the numbers in it are still injected by the harness.
- The two tiers are separated by something observable: the tools each of them can reach.
- A briefing that authorizes a field action cannot be released without a recorded human decision, and a declined briefing is not published.
- A web client can stream the run and answer a pending request without the harness knowing anything about HTTP.
- The live suite depends on a model that emits tool calls reliably. The offline suite cannot exercise that path, because a model cannot be simulated faithfully; the offline suite instead drives the scripted agent.
- A node timeout is not available: LangGraph supports per-node timeouts only for asynchronous nodes, and the harness nodes are synchronous. The endpoint profile's own timeout bounds the model call instead.
