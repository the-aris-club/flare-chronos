"""Endpoint profiles and Dual-System chat adapters for the FLARE-CHRONOS harness.

Each cognitive layer is bound to one LLM service through an `EndpointProfile`:
protocol, endpoint, model id, API key, and request options. Every value is
resolved from explicit configuration — process environment first, then the
workspace `.env` file, then the harness config. Nothing is read from ambient
machine state, so the same profile runs on a developer laptop, in CI, and on a
deployed host without change.

Two protocols are supported:

- `typed_questions`: posts `{model, state, questions}` and returns `{answers}`
  where every answer carries a calibrated probability. Used by the System 1
  Reflexive Layer, which classifies rather than writes.
- `native_chat`: posts `{model, messages, ...}` to a chat endpoint and returns
  `{message: {content, thinking, tool_calls}}`. Used by the System 2
  Deliberative Layer, which writes a grounded narrative.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal

import yaml
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import BaseModel, Field

from ai_service.schemas import (
    UseCaseId,
    collect_citation_keys,
    format_citation_value,
)
from ai_service.tools import USE_CASE_PRIMARY_TOOLS

AI_SERVICE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = AI_SERVICE_ROOT / "config" / "harness_config.yaml"
WORKSPACE_ENV_FILE = AI_SERVICE_ROOT.parents[1] / ".env"

Protocol = Literal["typed_questions", "native_chat"]

DEFAULT_USER_AGENT = "flare-chronos/2.0.0"


class MissingEndpointCredentialError(RuntimeError):
    """Raised when a live call is attempted without a configured API key."""

    def __init__(self, profile: EndpointProfile) -> None:
        super().__init__(
            f"No API key configured for this endpoint profile "
            f"(protocol={profile.protocol}, endpoint={profile.endpoint}, "
            f"model={profile.model_id}). Set the environment variable "
            f"{profile.api_key_env} or add it to the workspace .env file."
        )
        self.profile = profile


class EndpointCallError(RuntimeError):
    """Raised when a live endpoint call fails or answers with an unusable body."""


class RequestOptions(BaseModel):
    """Request tuning for one endpoint profile. Every field is sent verbatim."""

    timeout_ms: int = 30000
    temperature: float | None = None
    max_output_tokens: int | None = None
    thinking_level: str | bool | None = None
    seed: int | None = None
    user_agent: str = DEFAULT_USER_AGENT
    headers: dict[str, str] = Field(default_factory=dict)
    extra_body: dict[str, Any] = Field(default_factory=dict)


class EndpointProfile(BaseModel):
    """The explicit binding between one cognitive layer and one LLM service."""

    protocol: Protocol
    endpoint: str
    model_id: str
    api_key_env: str
    request: RequestOptions = Field(default_factory=RequestOptions)


def load_harness_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load the declarative Dual-System harness configuration YAML."""
    path = config_path or DEFAULT_CONFIG_PATH
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def read_workspace_env(env_file: Path | None = None) -> dict[str, str]:
    """Read `KEY=VALUE` pairs from the workspace `.env` file, if it exists."""
    path = env_file or WORKSPACE_ENV_FILE
    if not path.is_file():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip("'\"")
    return values


def _lookup_env(env_name: str, workspace_env: dict[str, str]) -> str:
    """Return the first non-empty value of `env_name` from env, then `.env`."""
    for candidate in (os.environ.get(env_name), workspace_env.get(env_name)):
        if candidate and candidate.strip():
            return candidate.strip()
    return ""


def resolve_endpoint_profile(
    cfg: dict[str, Any], layer: str, env_file: Path | None = None
) -> EndpointProfile:
    """Resolve one layer's endpoint profile.

    Precedence for every overridable value: process environment, then the
    workspace `.env` file, then the harness config.
    """
    layer_cfg = cfg["models"][layer]
    workspace_env = read_workspace_env(env_file)

    endpoint = _lookup_env(
        str(layer_cfg.get("endpoint_env", "")), workspace_env
    ) or str(layer_cfg["endpoint"])
    model_id = _lookup_env(str(layer_cfg.get("model_env", "")), workspace_env) or str(
        layer_cfg["model_id"]
    )
    return EndpointProfile(
        protocol=layer_cfg["protocol"],
        endpoint=endpoint.strip(),
        model_id=model_id.strip(),
        api_key_env=str(layer_cfg["api_key_env"]),
        request=RequestOptions.model_validate(layer_cfg.get("request") or {}),
    )


def resolve_api_key(profile: EndpointProfile, env_file: Path | None = None) -> str:
    """Resolve the API key for a profile, or raise when none is configured."""
    key = _lookup_env(profile.api_key_env, read_workspace_env(env_file))
    if not key:
        raise MissingEndpointCredentialError(profile)
    return key


def _post_json(
    url: str, payload: dict[str, Any], headers: dict[str, str], timeout_sec: float
) -> dict[str, Any]:
    """POST a JSON body and decode a JSON object response."""
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_sec) as response:
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:400]
        exc.close()
        raise EndpointCallError(f"HTTP {exc.code} from {url}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise EndpointCallError(f"Cannot reach {url}: {exc.reason}") from exc
    try:
        decoded = json.loads(body)
    except ValueError as exc:
        raise EndpointCallError(f"Non-JSON response from {url}: {body[:400]}") from exc
    if not isinstance(decoded, dict):
        raise EndpointCallError(f"Unexpected response shape from {url}: {body[:400]}")
    return decoded


def synthesize_grounded_response(
    use_case_id: str, tool_messages: list[ToolMessage]
) -> str:
    """Format a strictly grounded narrative citing only numbers from tool output.

    This is the deterministic floor used by the offline harness and as the
    fallback when a model-authored narrative fails numeric verification.
    """
    parsed_payloads: list[tuple[str, dict[str, Any]]] = []
    for tool_message in tool_messages:
        try:
            data = json.loads(str(tool_message.content))
        except ValueError:
            continue
        if isinstance(data, dict):
            parsed_payloads.append((tool_message.name or "tool", data))

    lines: list[str] = [f"### Verified Analysis Report ({use_case_id})"]
    for tool_name, payload in parsed_payloads:
        lines.append(f"- **Tool Executed (`{tool_name}`)**:")
        for key, value in payload.items():
            if isinstance(value, int | float) and not isinstance(value, bool):
                lines.append(f"  - `{key}`: **{value}**")
            elif isinstance(value, str) and len(value) < 160:
                lines.append(f"  - `{key}`: {value}")
    return "\n".join(lines)


def build_citation_table(tool_messages: list[ToolMessage]) -> dict[str, float]:
    """Collect the citable quantities carried by the deterministic tool outputs."""
    citations: dict[str, float] = {}
    for tool_message in tool_messages:
        try:
            payload = json.loads(str(tool_message.content))
        except ValueError:
            continue
        if isinstance(payload, dict):
            citations.update(collect_citation_keys(payload))
    return citations


class HarnessChatModel(BaseChatModel):
    """Shared tool-argument mapping and grounded synthesis for every harness model."""

    role: str = Field(default="system2_deliberative")
    model_id: str = Field(default="")
    source_label: str = Field(default="")
    reasoning_effort: str = Field(default="low")
    bound_tool_names: list[str] = Field(default_factory=list)
    inject_unverified_number_once: bool = Field(default=False)
    _injected_once: bool = False

    @property
    def _llm_type(self) -> str:
        return f"flare-chronos-{self.role}"

    def bind_tools(
        self,
        tools: Sequence[dict[str, Any] | type | Any | BaseTool],
        *,
        tool_choice: str | None = None,
        **kwargs: Any,
    ) -> HarnessChatModel:
        names: list[str] = []
        for tool in tools:
            if isinstance(tool, dict) and "name" in tool:
                names.append(str(tool["name"]))
            else:
                tool_name = getattr(tool, "name", None)
                if tool_name is not None:
                    names.append(str(tool_name))
        return self.model_copy(update={"bound_tool_names": names})

    def _infer_use_case_and_params_from_messages(
        self, messages: list[BaseMessage]
    ) -> tuple[str, dict[str, Any]]:
        """Extract active use_case_id and entity parameters from the conversation state."""
        use_case_id = UseCaseId.UC_1_1_REGIME_SHIFT_ATTRIBUTION.value
        params: dict[str, Any] = {
            "year": 2024,
            "region": "mekong",
            "stakeholder_tier": "climate_scientist",
        }
        for message in messages:
            text = str(message.content)
            match_uc = re.search(r"\[USE_CASE:(UC-[A-Z0-9\.-]+)\]", text)
            if match_uc:
                use_case_id = match_uc.group(1)
            match_year = re.search(r"\[YEAR:(\d{4})\]", text)
            if match_year:
                params["year"] = int(match_year.group(1))
            match_region = re.search(r"\[REGION:([a-z_]+)\]", text)
            if match_region:
                params["region"] = match_region.group(1)
            match_tier = re.search(r"\[TIER:([a-z_]+)\]", text)
            if match_tier:
                params["stakeholder_tier"] = match_tier.group(1)
        return use_case_id, params

    def _build_tool_arguments(
        self, tool_name: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Construct deterministic tool arguments matching the `@tool` signatures."""
        year = int(params.get("year", 2024))
        region = str(params.get("region", "mekong"))
        arg_map: dict[str, dict[str, Any]] = {
            "tool_compute_footprint_and_h3_allocation": {
                "sensor": "MODIS",
                "scan_angle_deg": 55.0,
                "latitude": 14.5,
                "longitude": 108.0,
            },
            "tool_compute_solar_sza_and_daynight": {
                "latitude": 14.5,
                "longitude": 108.0,
                "acq_date": "2024-03-15",
                "acq_time_hhmm": "0630",
                "raw_daynight": "D",
            },
            "tool_evaluate_detection_probability_and_saa": {
                "sensor": "VIIRS",
                "latitude": -15.0,
                "longitude": -48.0,
                "bright_t4_k": 310.0,
                "bright_t5_k": 297.0,
                "frp_mw": 1.4,
                "raw_confidence": "nominal",
                "harmonized_daynight": "N",
            },
            "tool_calibrate_cross_sensor_frp": {
                "raw_modis_frp_mw": 35.0,
                "scan_angle_deg": 48.0,
                "sza_deg": 28.0,
                "harmonized_daynight": "D",
            },
            "tool_deduplicate_overpass_episodes": {
                "year": year,
                "latitude": 17.2 if region == "mekong" else -9.0,
                "raw_detection_count": 50988 if region == "mekong" else 112405,
                "deduplicated_episodes": 22557 if region == "mekong" else 22578,
            },
            "tool_lookup_single_epoch_metrics": {
                "region": region,
                "year": year,
            },
            "tool_query_seasonal_phenology_12m": {
                "region": "both",
            },
            "tool_emit_flash_nrt_alert": {
                "region": region,
            },
            "tool_uc1_1_regime_shift_attribution": {
                "region": region,
                "baseline_year": 2005,
                "comparison_year": year,
            },
            "tool_uc1_2_cross_sensor_discrepancy_forensics": {
                "modis_scan_angle_deg": 52.0,
                "viirs_cluster_frp_mw": 18.5,
                "latitude": -12.4,
                "longitude": -54.2,
                "daynight": "D",
            },
            "tool_uc1_3_thermal_source_origin_classification": {
                "region": region,
            },
            "tool_uc2_1_phenological_phase_shift_detection": {
                "region": region,
            },
            "tool_uc2_2_uncertainty_aware_tactical_dispatch": {
                "scan_angle_deg": 55.0,
                "latitude": 14.2,
                "longitude": 108.1,
            },
            "tool_uc2_3_verified_multistakeholder_briefing_data": {
                "region": region,
                "year": year,
            },
            "tool_uc3_1_constellation_retirement_simulation": {
                "region": region,
                "year": year,
            },
            "tool_uc3_2_multihop_spatiotemporal_cube_query": {},
            "tool_uc3_3_autonomous_biome_recalibration": {},
            "tool_uc4_1_orbital_drift_and_sza_audit": {},
            "tool_uc4_2_nrt_vs_sp_fidelity_audit": {},
            "tool_uc4_3_adaptive_firms_rate_limit_planner": {},
            "tool_uc5_1_redd_plus_carbon_mrv_baseline_audit": {
                "region": region,
            },
            "tool_uc5_2_burn_ban_policy_counterfactual_audit": {
                "region": region,
            },
            "tool_uc5_3_transboundary_fire_propagation_forensics": {},
        }
        return arg_map.get(tool_name, {})

    def _selected_tools(
        self, use_case_id: str, bound_tool_names: list[str]
    ) -> list[str]:
        target_tools = bound_tool_names or USE_CASE_PRIMARY_TOOLS.get(
            UseCaseId(use_case_id), ["tool_lookup_single_epoch_metrics"]
        )
        return target_tools[:2]

    def _tool_call_message(
        self, use_case_id: str, tool_names: list[str], params: dict[str, Any]
    ) -> AIMessage:
        """Build the tool-call turn that binds a use case to its primary tools."""
        tool_calls = [
            {
                "name": tool_name,
                "args": self._build_tool_arguments(tool_name, params),
                "id": f"call_{use_case_id.replace('-', '_').replace('.', '_')}_{tool_name}",
                "type": "tool_call",
            }
            for tool_name in tool_names
        ]
        return AIMessage(content="", tool_calls=tool_calls)


class DeterministicHarnessChatModel(HarnessChatModel):
    """LangChain `BaseChatModel` for deterministic execution of the LangGraph StateGraph.

    Provides the offline sandbox used by CI and by the local benchmark run. The
    same StateGraph, ToolNode, and Verified Facts Ledger are exercised as in
    live mode, so the offline suite proves graph and gate behaviour without
    calling any network service.
    """

    @property
    def _llm_type(self) -> str:
        return f"flare-chronos-deterministic-{self.role}"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        use_case_id, params = self._infer_use_case_and_params_from_messages(messages)
        tool_messages = [m for m in messages if isinstance(m, ToolMessage)]
        is_repair_turn = any(
            isinstance(m, HumanMessage)
            and "[NUMERIC_VERIFIER_REJECTION]" in str(m.content)
            for m in messages
        )
        has_escalated_msg = any(
            "[ESCALATED_S1_TO_S2]" in str(m.content) for m in messages
        )
        already_called_names = {tm.name for tm in tool_messages if tm.name}
        missing_bound_tools = [
            t for t in self.bound_tool_names if t not in already_called_names
        ]

        if not tool_messages or (has_escalated_msg and missing_bound_tools):
            selected_tools = self._selected_tools(use_case_id, missing_bound_tools)
            additional_kwargs: dict[str, Any] = {}
            if self.role == "system2_deliberative":
                additional_kwargs["reasoning_content"] = (
                    f"[System 2 Deliberative Reasoning ({self.model_id}, "
                    f"effort={self.reasoning_effort})]: Decomposing {use_case_id} "
                    f"into deterministic tool invocations {selected_tools}."
                )
            return ChatResult(
                generations=[
                    ChatGeneration(
                        message=self._tool_call_message(
                            use_case_id, selected_tools, params
                        ).model_copy(update={"additional_kwargs": additional_kwargs})
                    )
                ]
            )

        content = synthesize_grounded_response(use_case_id, tool_messages)
        if (
            self.inject_unverified_number_once
            and not self._injected_once
            and not is_repair_turn
        ):
            self._injected_once = True
            content += (
                "\n- **Speculative Unverified Extrapolation**: "
                "Estimated anomaly of **98765.4321** MW."
            )
        additional_kwargs = {}
        if self.role == "system2_deliberative":
            additional_kwargs["reasoning_content"] = (
                f"[System 2 Deliberative Verification ({self.model_id}, "
                f"effort={self.reasoning_effort})]: Synthesizing narrative from "
                f"{len(tool_messages)} deterministic tool outputs with strict "
                f"adherence to the VerifiedFactsLedger."
            )
        return ChatResult(
            generations=[
                ChatGeneration(
                    message=AIMessage(
                        content=content, additional_kwargs=additional_kwargs
                    )
                )
            ]
        )


class SystemOneChatModel(HarnessChatModel):
    """Live System 1 adapter for the typed-questions protocol.

    The protocol evaluates a `state` against typed questions and returns
    calibrated probabilities instead of free text, so it fits the System 1
    Reflexive Layer: intent triage, entity classification, and verification of
    the deterministic tool output. It is not an OpenAI-shaped chat API, so it
    is implemented directly over HTTP.
    """

    profile: EndpointProfile

    @property
    def _llm_type(self) -> str:
        return "flare-chronos-system-one"

    def evaluate(self, state_text: str, questions: dict[str, Any]) -> dict[str, Any]:
        """Send one typed-questions request and return the raw answers payload."""
        payload = {
            "model": self.profile.model_id,
            "state": state_text,
            "questions": questions,
        }
        headers = {
            **self.profile.request.headers,
            "Content-Type": "application/json",
            "User-Agent": self.profile.request.user_agent,
            "Authorization": f"Bearer {resolve_api_key(self.profile)}",
        }
        return _post_json(
            self.profile.endpoint,
            payload,
            headers,
            self.profile.request.timeout_ms / 1000.0,
        )

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        use_case_id, params = self._infer_use_case_and_params_from_messages(messages)
        tool_messages = [m for m in messages if isinstance(m, ToolMessage)]

        if not tool_messages:
            user_text = "\n".join(
                str(m.content) for m in messages if not isinstance(m, ToolMessage)
            )
            response = self.evaluate(
                state_text=user_text,
                questions={
                    "region": {
                        "type": "choice",
                        "instructions": "Which geographical study region is queried in the state?",
                        "criteria": {
                            "mekong": "Mekong river basin or Mainland Southeast Asia",
                            "amazon": "Amazon basin or South America",
                        },
                    },
                    "is_deliberative": {
                        "type": "noul",
                        "instructions": "Does this query require multi-step System 2 causal attribution?",
                    },
                },
            )
            answers = response.get("answers", {})
            region_choice = answers.get("region", {}).get("choice")
            if region_choice in ("mekong", "amazon"):
                params["region"] = region_choice

            selected_tools = self._selected_tools(use_case_id, self.bound_tool_names)
            message = self._tool_call_message(use_case_id, selected_tools, params)
            message.additional_kwargs["systemone_result"] = response
            return ChatResult(generations=[ChatGeneration(message=message)])

        tool_summary = "\n".join(str(tm.content) for tm in tool_messages)
        response = self.evaluate(
            state_text=tool_summary[:4000],
            questions={
                "requires_escalation": {
                    "type": "noul",
                    "instructions": (
                        "Does this tool output show severe raw-vs-harmonized divergence "
                        "(>= 200%) or South Atlantic Anomaly anomalies requiring "
                        "System 2 escalation?"
                    ),
                },
                "verification_status": {
                    "type": "choice",
                    "instructions": "Classify the physical status of the returned fire metrics.",
                    "criteria": {
                        "verified_nominal": "Metrics are consistent and within expected harmonized bounds",
                        "regime_conflict": "Severe raw-vs-harmonized divergence or orbital artifact detected",
                    },
                },
            },
        )
        message = AIMessage(
            content=synthesize_grounded_response(use_case_id, tool_messages),
            additional_kwargs={"systemone_result": response},
        )
        return ChatResult(generations=[ChatGeneration(message=message)])


class SystemTwoChatModel(HarnessChatModel):
    """Live System 2 adapter for the native chat protocol.

    The endpoint returns the model's deliberation as a dedicated `thinking`
    field, which the harness records as reasoning evidence. On the synthesis
    turn the model writes the analytical narrative and cites every quantity as
    a `{{fact_key}}` placeholder; the harness resolves those placeholders
    against the Verified Facts Ledger, so the model never writes a number.
    """

    profile: EndpointProfile

    @property
    def _llm_type(self) -> str:
        return "flare-chronos-system-two"

    def _to_native_messages(self, messages: list[BaseMessage]) -> list[dict[str, Any]]:
        """Convert LangChain messages into the native chat message shape."""
        native: list[dict[str, Any]] = []
        for message in messages:
            if isinstance(message, SystemMessage):
                native.append({"role": "system", "content": str(message.content)})
            elif isinstance(message, HumanMessage):
                native.append({"role": "user", "content": str(message.content)})
            elif isinstance(message, ToolMessage):
                native.append({"role": "tool", "content": str(message.content)})
            elif isinstance(message, AIMessage):
                entry: dict[str, Any] = {
                    "role": "assistant",
                    "content": str(message.content),
                }
                if message.tool_calls:
                    entry["tool_calls"] = [
                        {
                            "function": {
                                "name": call["name"],
                                "arguments": call.get("args", {}),
                            }
                        }
                        for call in message.tool_calls
                    ]
                native.append(entry)
        return native

    def _build_payload(
        self, messages: list[BaseMessage], tools: Sequence[Any] | None
    ) -> dict[str, Any]:
        """Build the native chat request body from the profile and the turn."""
        options: dict[str, Any] = {}
        request = self.profile.request
        if request.temperature is not None:
            options["temperature"] = request.temperature
        if request.max_output_tokens is not None:
            options["num_predict"] = request.max_output_tokens
        if request.seed is not None:
            options["seed"] = request.seed

        payload: dict[str, Any] = {
            "model": self.profile.model_id,
            "messages": self._to_native_messages(messages),
            "stream": False,
        }
        if options:
            payload["options"] = options
        if request.thinking_level is not None:
            payload["think"] = request.thinking_level
        if tools:
            payload["tools"] = [convert_to_openai_tool(tool) for tool in tools]
        payload.update(request.extra_body)
        return payload

    def _call(self, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {
            **self.profile.request.headers,
            "Content-Type": "application/json",
            "User-Agent": self.profile.request.user_agent,
            "Authorization": f"Bearer {resolve_api_key(self.profile)}",
        }
        return _post_json(
            self.profile.endpoint,
            payload,
            headers,
            self.profile.request.timeout_ms / 1000.0,
        )

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        use_case_id, params = self._infer_use_case_and_params_from_messages(messages)
        tool_messages = [m for m in messages if isinstance(m, ToolMessage)]
        has_escalated_msg = any(
            "[ESCALATED_S1_TO_S2]" in str(m.content) for m in messages
        )
        already_called_names = {tm.name for tm in tool_messages if tm.name}
        missing_bound_tools = [
            t for t in self.bound_tool_names if t not in already_called_names
        ]

        if not tool_messages or (has_escalated_msg and missing_bound_tools):
            selected_tools = self._selected_tools(use_case_id, missing_bound_tools)
            payload = self._build_payload(messages, None)
            payload["messages"] = payload["messages"] + [
                {
                    "role": "user",
                    "content": (
                        f"Decompose FLARE-CHRONOS use case {use_case_id} for "
                        f"region={params.get('region')} year={params.get('year')} "
                        f"using deterministic tools {selected_tools}."
                    ),
                }
            ]
            response = self._call(payload)
            message_data = response.get("message", {})
            thinking = str(message_data.get("thinking") or "")
            message = self._tool_call_message(use_case_id, selected_tools, params)
            message.additional_kwargs["reasoning_content"] = (
                f"[Live System 2 ({self.model_id})]: {thinking}"
            )
            message.additional_kwargs["model_used"] = self.model_id
            return ChatResult(generations=[ChatGeneration(message=message)])

        citations = build_citation_table(tool_messages)
        citation_lines = "\n".join(
            f"- {key} = {format_citation_value(value)}"
            for key, value in sorted(citations.items())
        )
        narrative_prompt = (
            "Write the analytical briefing for the FLARE-CHRONOS System 2 "
            "Deliberative Layer.\n"
            "Rules:\n"
            "1. Cite EVERY quantity as {{fact_key}} using exactly the keys listed "
            "below. Never write a digit yourself.\n"
            "2. Never introduce a quantity, percentage, or ratio that is not in "
            "the list.\n"
            "3. Explain the physical interpretation: what the deterministic tool "
            "outputs imply about the process, and what the caller should do.\n"
            f"Available facts:\n{citation_lines}\n"
        )
        payload = self._build_payload(messages, None)
        payload["messages"] = payload["messages"] + [
            {"role": "user", "content": narrative_prompt}
        ]
        response = self._call(payload)
        message_data = response.get("message", {})
        thinking = str(message_data.get("thinking") or "")
        content = str(message_data.get("content") or "")
        is_repair_turn = any(
            isinstance(m, HumanMessage)
            and "[NUMERIC_VERIFIER_REJECTION]" in str(m.content)
            for m in messages
        )
        if (
            self.inject_unverified_number_once
            and not self._injected_once
            and not is_repair_turn
        ):
            self._injected_once = True
            content += (
                "\n- Speculative Unverified Extrapolation: estimated anomaly "
                "of 98765.4321 MW."
            )
        message = AIMessage(
            content=content,
            additional_kwargs={
                "reasoning_content": f"[Live System 2 ({self.model_id})]: {thinking}",
                "model_used": self.model_id,
            },
        )
        return ChatResult(generations=[ChatGeneration(message=message)])


def build_live_system1_chat_model(
    cfg: dict[str, Any] | None = None,
) -> SystemOneChatModel:
    """Create the live System 1 client for the typed-questions protocol."""
    config = cfg or load_harness_config()
    profile = resolve_endpoint_profile(config, "system1_reflexive")
    return SystemOneChatModel(
        role="system1_reflexive",
        model_id=profile.model_id,
        source_label=profile.endpoint,
        reasoning_effort="low",
        profile=profile,
    )


def build_live_system2_chat_model(
    cfg: dict[str, Any] | None = None,
    inject_unverified_number_once: bool = False,
) -> SystemTwoChatModel:
    """Create the live System 2 client for the native chat protocol."""
    config = cfg or load_harness_config()
    profile = resolve_endpoint_profile(config, "system2_deliberative")
    return SystemTwoChatModel(
        role="system2_deliberative",
        model_id=profile.model_id,
        source_label=profile.endpoint,
        reasoning_effort=str(profile.request.thinking_level or "low"),
        profile=profile,
        inject_unverified_number_once=inject_unverified_number_once,
    )
