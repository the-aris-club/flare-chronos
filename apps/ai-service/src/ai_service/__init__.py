"""FLARE-CHRONOS Dual-System Cognitive Harness (`apps/ai-service`).

Exports the LangGraph `StateGraph` builder, schemas, endpoint profiles, model
adapters, and 23 deterministic `@tool` functions.
"""

from ai_service.harness import (
    FlareChronosDualSystemHarness,
    VerifiedPatternCache,
    build_dual_system_graph,
)
from ai_service.models import (
    DeterministicHarnessChatModel,
    EndpointCallError,
    EndpointProfile,
    MissingEndpointCredentialError,
    RequestOptions,
    SystemOneChatModel,
    SystemTwoChatModel,
    build_live_system1_chat_model,
    build_live_system2_chat_model,
    load_harness_config,
    resolve_api_key,
    resolve_endpoint_profile,
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
    collect_citation_keys,
    resolve_citations,
    verify_grounded_draft,
)
from ai_service.tools import ALL_DETERMINISTIC_TOOLS, TOOL_MAP, USE_CASE_PRIMARY_TOOLS

__all__ = [
    "ALL_DETERMINISTIC_TOOLS",
    "TOOL_MAP",
    "USE_CASE_PRIMARY_TOOLS",
    "CognitivePath",
    "DeterministicHarnessChatModel",
    "EndpointCallError",
    "EndpointProfile",
    "FlareChronosDualSystemHarness",
    "HarnessState",
    "MissingEndpointCredentialError",
    "RequestOptions",
    "SpatioTemporalQueryEntity",
    "StakeholderTier",
    "SystemOneChatModel",
    "SystemTwoChatModel",
    "UseCaseId",
    "VerificationReport",
    "VerifiedFactEntry",
    "VerifiedFactsLedger",
    "VerifiedPatternCache",
    "build_dual_system_graph",
    "build_live_system1_chat_model",
    "build_live_system2_chat_model",
    "collect_citation_keys",
    "load_harness_config",
    "resolve_api_key",
    "resolve_citations",
    "resolve_endpoint_profile",
    "verify_grounded_draft",
]
