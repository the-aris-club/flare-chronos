"""FLARE-CHRONOS Dual-System Cognitive Harness (`apps/ai-service`).

Exports the LangGraph `StateGraph` builder, schemas, endpoint profiles, model
adapters, prompts, human-input tools, event stream, and the 23 deterministic
`@tool` functions.
"""

from ai_service.classification import classification_answers, classify_request
from ai_service.events import HarnessEvent, to_sse_frames
from ai_service.harness import (
    FlareChronosDualSystemHarness,
    VerifiedPatternCache,
    build_dual_system_graph,
    build_sqlite_checkpointer,
)
from ai_service.human_input import ask_user_question
from ai_service.models import (
    DeterministicHarnessChatModel,
    EndpointCallError,
    EndpointProfile,
    MissingEndpointCredentialError,
    NativeChatModel,
    RequestOptions,
    SystemOneChatModel,
    build_live_system1_chat_model,
    build_live_system2_chat_model,
    load_harness_config,
    resolve_api_key,
    resolve_endpoint_profile,
)
from ai_service.prompts import (
    system1_classification_prompt,
    system1_typed_questions,
    system2_system_prompt,
)
from ai_service.schemas import (
    CognitivePath,
    HarnessState,
    SpatioTemporalQueryEntity,
    StakeholderTier,
    UseCaseId,
    VerificationReport,
    VerifiedFactEntry,
    VerifiedFactsLedger,
    collect_citable_facts,
    resolve_citations,
    verify_grounded_draft,
)
from ai_service.tools import (
    ALL_DETERMINISTIC_TOOLS,
    ATOMIC_TOOLS,
    DOMAIN_DIAGNOSTIC_TOOLS,
    TOOL_MAP,
    USE_CASE_PRIMARY_TOOLS,
)

__all__ = [
    "ALL_DETERMINISTIC_TOOLS",
    "ATOMIC_TOOLS",
    "DOMAIN_DIAGNOSTIC_TOOLS",
    "TOOL_MAP",
    "USE_CASE_PRIMARY_TOOLS",
    "CognitivePath",
    "DeterministicHarnessChatModel",
    "EndpointCallError",
    "EndpointProfile",
    "FlareChronosDualSystemHarness",
    "HarnessEvent",
    "HarnessState",
    "MissingEndpointCredentialError",
    "NativeChatModel",
    "RequestOptions",
    "SpatioTemporalQueryEntity",
    "StakeholderTier",
    "SystemOneChatModel",
    "UseCaseId",
    "VerificationReport",
    "VerifiedFactEntry",
    "VerifiedFactsLedger",
    "VerifiedPatternCache",
    "ask_user_question",
    "build_dual_system_graph",
    "build_live_system1_chat_model",
    "build_live_system2_chat_model",
    "build_sqlite_checkpointer",
    "classification_answers",
    "classify_request",
    "collect_citable_facts",
    "load_harness_config",
    "resolve_api_key",
    "resolve_citations",
    "resolve_endpoint_profile",
    "system1_classification_prompt",
    "system1_typed_questions",
    "system2_system_prompt",
    "to_sse_frames",
    "verify_grounded_draft",
]
