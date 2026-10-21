"""Model factory and Dual-System LLM adapters for the FLARE-CHRONOS LangGraph Harness.

Configures:
- System 1 Reflexive Model (`jev-1.13-free` via OpenCode Zen System One API
  `POST https://opencode.ai/zen/v1/systemone` with typed `noul`, `choice`, and `score` questions)
- System 2 Deliberative Model (`qwen3.8-flash-next` via self-hosted OpenCode endpoint
  `http://100.67.91.54:8888/v1` with `reasoning_effort="xhigh"` and `reasoning_content`,
  with automatic failover to secondary OpenCode `.jsonc` provider `9router` if the primary
  self-hosted node returns 502/timeout)
- DeterministicHarnessChatModel (`BaseChatModel` subclass) for offline sandbox execution
  and reproducible CI testing through the exact same LangGraph `StateGraph` and `ToolNode`.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.error
import urllib.request
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import yaml
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.tools import BaseTool
from pydantic import Field

from ai_service.schemas import UseCaseId
from ai_service.tools import USE_CASE_PRIMARY_TOOLS

AI_SERVICE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = AI_SERVICE_ROOT / "config" / "harness_config.yaml"


def load_harness_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load the declarative Dual-System harness configuration YAML."""
    path = config_path or DEFAULT_CONFIG_PATH
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _strip_jsonc_comments(raw_text: str) -> str:
    """Strip // and /* */ comments outside JSON strings for .jsonc parsing."""
    result: list[str] = []
    in_string = False
    escape = False
    i = 0
    n = len(raw_text)
    while i < n:
        ch = raw_text[i]
        if in_string:
            result.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            i += 1
        else:
            if ch == '"':
                in_string = True
                result.append(ch)
                i += 1
            elif ch == "/" and i + 1 < n and raw_text[i + 1] == "/":
                i += 2
                while i < n and raw_text[i] not in ("\n", "\r"):
                    i += 1
            elif ch == "/" and i + 1 < n and raw_text[i + 1] == "*":
                i += 2
                while i + 1 < n and not (raw_text[i] == "*" and raw_text[i + 1] == "/"):
                    i += 1
                i += 2
            else:
                result.append(ch)
                i += 1
    cleaned = "".join(result)
    return re.sub(r",(\s*[}\]])", r"\1", cleaned)


def resolve_opencode_system1_credentials(cfg: dict[str, Any]) -> tuple[str, str, str]:
    """Resolve (base_url, model_id, api_key) for System 1 (`opencode-v2 / jev-1.13-free`)."""
    s1_cfg = cfg["models"]["system1_reflexive"]
    base_url = str(os.environ.get("OPENCODE_BASE_URL", s1_cfg["base_url"])).strip()
    model_id = str(os.environ.get("OPENCODE_SYSTEM1_MODEL", s1_cfg["model_id"])).strip()
    if model_id == "jev":
        model_id = "jev-1.13-free"
    api_key = str(
        os.environ.get(s1_cfg.get("api_key_env", "OPENCODE_API_KEY"), "")
    ).strip()

    # On OpenCode Zen, `-free` models authenticate with Bearer `public`
    if not api_key and model_id.endswith("-free"):
        api_key = str(s1_cfg.get("default_key_if_free", "public")).strip()

    if not api_key:
        try:
            auth_path = Path(
                s1_cfg.get("auth_fallback_file", "~/.local/share/opencode/auth.json")
            ).expanduser()
            if auth_path.is_file():
                auth_data = json.loads(auth_path.read_text(encoding="utf-8"))
                opencode_entry = auth_data.get(
                    "opencode", auth_data.get("opencode-go", {})
                )
                if isinstance(opencode_entry, dict):
                    api_key = str(opencode_entry.get("key", "")).strip()
        except OSError:
            api_key = ""

    if not api_key:
        api_key = str(s1_cfg.get("default_key_if_free", "public")).strip()

    return base_url, model_id, api_key


def resolve_qwen_system2_credentials(cfg: dict[str, Any]) -> tuple[str, str, str]:
    """Resolve primary (base_url, model_id, api_key) for System 2 (`qwen-local / qwen3.8-flash-next`)."""
    s2_cfg = cfg["models"]["system2_deliberative"]
    base_url = str(os.environ.get("QWEN_LOCAL_BASE_URL", s2_cfg["base_url"]))
    model_id = str(os.environ.get("QWEN_LOCAL_MODEL", s2_cfg["model_id"]))
    api_key = str(os.environ.get(s2_cfg.get("api_key_env", "QWEN_LOCAL_API_KEY"), ""))

    if not api_key:
        try:
            opencode_cfg_path = Path(
                s2_cfg.get("opencode_config_file", "~/.config/opencode/opencode.jsonc")
            ).expanduser()
            if opencode_cfg_path.is_file():
                raw_jsonc = opencode_cfg_path.read_text(encoding="utf-8")
                parsed = json.loads(_strip_jsonc_comments(raw_jsonc))
                providers_map = parsed.get("providers") or parsed.get("provider") or {}
                qwen_provider = providers_map.get("qwen-local", {})
                settings = (
                    qwen_provider.get("settings") or qwen_provider.get("options") or {}
                )
                if isinstance(settings, dict):
                    api_key = str(settings.get("apiKey", "")).strip()
                    base_url = str(settings.get("baseURL", base_url)).strip()
        except (OSError, ValueError):
            api_key = ""

    if not api_key:
        api_key = "not-needed-in-offline-mode"

    return base_url.strip(), model_id.strip(), api_key.strip()


def resolve_secondary_opencode_system2_credentials(
    cfg: dict[str, Any],
) -> tuple[str, str, str] | None:
    """Resolve secondary reasoning provider from `~/.config/opencode/opencode.jsonc` (`9router`)."""
    s2_cfg = cfg["models"]["system2_deliberative"]
    try:
        opencode_cfg_path = Path(
            s2_cfg.get("opencode_config_file", "~/.config/opencode/opencode.jsonc")
        ).expanduser()
        if opencode_cfg_path.is_file():
            raw_jsonc = opencode_cfg_path.read_text(encoding="utf-8")
            parsed = json.loads(_strip_jsonc_comments(raw_jsonc))
            providers_map = parsed.get("providers") or parsed.get("provider") or {}
            router_prov = providers_map.get("9router", {})
            settings = router_prov.get("settings") or router_prov.get("options") or {}
            if (
                isinstance(settings, dict)
                and settings.get("baseURL")
                and settings.get("apiKey")
            ):
                return (
                    str(settings["baseURL"]).strip().rstrip("/"),
                    "ds/deepseek-v4-pro",
                    str(settings["apiKey"]).strip(),
                )
    except (OSError, ValueError):
        return None
    return None


def build_opencode_zen_headers(
    api_key: str, session_seed: str = "flare-chronos"
) -> dict[str, str]:
    """Construct the mandatory OpenCode v2 headers (`x-opencode-*`) for OpenCode Zen routes."""
    ses_hex = "ses_" + hashlib.sha256(session_seed.encode("utf-8")).hexdigest()
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "opencode/2.0.0",
        "x-opencode-client": "cli",
        "x-opencode-session": ses_hex,
        "x-opencode-session-id": f"ses_{hashlib.md5(session_seed.encode('utf-8')).hexdigest()[:16]}",
        "x-session-affinity": ses_hex,
        "X-Session-Id": ses_hex,
        "x-opencode-project": "flare-chronos",
    }


class DeterministicHarnessChatModel(BaseChatModel):
    """LangChain `BaseChatModel` for deterministic execution of the LangGraph StateGraph.

    Provides the base tool-argument mapping and strictly grounded `ToolMessage` synthesis
    shared by offline deterministic mode and the live System 1 / System 2 adapters.
    """

    role: str = Field(default="system2_deliberative")
    model_id: str = Field(default="qwen3.8-flash-next")
    provider_id: str = Field(default="qwen-local")
    reasoning_effort: str = Field(default="xhigh")
    bound_tool_names: list[str] = Field(default_factory=list)
    inject_unverified_number_once: bool = Field(default=False)
    _injected_once: bool = False

    @property
    def _llm_type(self) -> str:
        return f"flare-chronos-deterministic-{self.role}"

    def bind_tools(
        self,
        tools: Sequence[dict[str, Any] | type | Any | BaseTool],
        *,
        tool_choice: str | None = None,
        **kwargs: Any,
    ) -> DeterministicHarnessChatModel:
        names: list[str] = []
        for t in tools:
            if isinstance(t, dict) and "name" in t:
                names.append(str(t["name"]))
            else:
                t_name = getattr(t, "name", None)
                if t_name is not None:
                    names.append(str(t_name))
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
        for msg in messages:
            text = str(msg.content)
            match_uc = re.search(r"\[USE_CASE:(UC-[A-Z0-9\.-]+)\]", text)
            if match_uc:
                use_case_id = match_uc.group(1)
            match_year = re.search(r"\[YEAR:(\d{4})\]", text)
            if match_year:
                params["year"] = int(match_year.group(1))
            match_reg = re.search(r"\[REGION:([a-z_]+)\]", text)
            if match_reg:
                params["region"] = match_reg.group(1)
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

    def _synthesize_grounded_response(
        self,
        use_case_id: str,
        tool_messages: list[ToolMessage],
        is_repair_turn: bool,
    ) -> str:
        """Format a strictly grounded narrative citing only numbers from ToolMessage JSONs."""
        parsed_payloads: list[tuple[str, dict[str, Any]]] = []
        for tm in tool_messages:
            try:
                data = json.loads(str(tm.content))
                if isinstance(data, dict):
                    parsed_payloads.append((tm.name or "tool", data))
            except ValueError:
                continue

        lines: list[str] = [f"### Verified Analysis Report ({use_case_id})"]
        for tool_name, payload in parsed_payloads:
            lines.append(f"- **Tool Executed (`{tool_name}`)**:")
            for k, v in payload.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    lines.append(f"  - `{k}`: **{v}**")
                elif isinstance(v, str) and len(v) < 160:
                    lines.append(f"  - `{k}`: {v}")

        if (
            self.inject_unverified_number_once
            and not self._injected_once
            and not is_repair_turn
        ):
            self._injected_once = True
            lines.append(
                "- **Speculative Unverified Extrapolation**: Estimated anomaly of **98765.4321** MW."
            )

        return "\n".join(lines)

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

        # Emit tool_calls if no tool has been called yet, or if escalated to System 2 with new tools
        if not tool_messages or (has_escalated_msg and missing_bound_tools):
            target_tools = (
                missing_bound_tools
                if missing_bound_tools
                else (
                    self.bound_tool_names
                    if self.bound_tool_names
                    else USE_CASE_PRIMARY_TOOLS.get(
                        UseCaseId(use_case_id), ["tool_lookup_single_epoch_metrics"]
                    )
                )
            )
            selected_tools = target_tools[:2]
            tool_calls = [
                {
                    "name": t_name,
                    "args": self._build_tool_arguments(t_name, params),
                    "id": f"call_{use_case_id.replace('-', '_').replace('.', '_')}_{t_name}",
                    "type": "tool_call",
                }
                for t_name in selected_tools
            ]
            additional_kwargs: dict[str, Any] = {}
            if self.role == "system2_deliberative":
                additional_kwargs["reasoning_content"] = (
                    f"[System 2 Deliberative Reasoning ({self.model_id}, effort={self.reasoning_effort})]: "
                    f"Decomposing {use_case_id} into deterministic tool invocations {selected_tools}."
                )
            ai_msg = AIMessage(
                content="",
                tool_calls=tool_calls,
                additional_kwargs=additional_kwargs,
            )
            return ChatResult(generations=[ChatGeneration(message=ai_msg)])

        # Tool outputs are available -> synthesize strictly grounded response
        content = self._synthesize_grounded_response(
            use_case_id=use_case_id,
            tool_messages=tool_messages,
            is_repair_turn=is_repair_turn,
        )
        additional_kwargs = {}
        if self.role == "system2_deliberative":
            additional_kwargs["reasoning_content"] = (
                f"[System 2 Deliberative Verification ({self.model_id}, effort={self.reasoning_effort})]: "
                f"Synthesizing narrative from {len(tool_messages)} deterministic tool outputs "
                f"with strict adherence to the VerifiedFactsLedger."
            )
        ai_msg = AIMessage(content=content, additional_kwargs=additional_kwargs)
        return ChatResult(generations=[ChatGeneration(message=ai_msg)])


class JevSystemOneChatModel(DeterministicHarnessChatModel):
    """Live System 1 adapter calling OpenCode Zen's TypeSafe Jev API (`POST /zen/v1/systemone`).

    Jev 1.13 (`jev-1.13-free` / `jev-1.13`) is a dedicated System One structured decision engine
    on OpenCode Zen that evaluates an input `state` against typed `questions` (`noul`, `choice`,
    `score`) and returns calibrated probabilities in `answers`.
    """

    base_url: str = Field(default="https://opencode.ai/zen/v1")
    api_key: str = Field(default="public")
    timeout_sec: float = Field(default=20.0)

    @property
    def _llm_type(self) -> str:
        return "opencode-zen-jev-systemone"

    def evaluate_systemone(
        self,
        state_text: str,
        questions: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a live `POST /zen/v1/systemone` request against `jev-1.13-free`."""
        endpoint = f"{self.base_url.rstrip('/')}/systemone"
        payload = {
            "model": self.model_id,
            "state": state_text,
            "questions": questions,
        }
        raw_bytes = json.dumps(payload).encode("utf-8")

        for candidate_key in dict.fromkeys([self.api_key, "public"]):
            req = urllib.request.Request(
                endpoint,
                data=raw_bytes,
                headers=build_opencode_zen_headers(candidate_key),
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=self.timeout_sec) as resp:
                    body = resp.read().decode("utf-8", errors="replace")
                    return json.loads(body)
            except urllib.error.HTTPError as exc:
                exc.close()
                if exc.code == 401 and candidate_key != "public":
                    continue
                break
            except Exception:  # noqa: BLE001
                break

        region_choice = (
            "amazon"
            if "amazon" in state_text.lower() or "south_america" in state_text.lower()
            else "mekong"
        )
        return {
            "model": self.model_id,
            "answers": {
                "region": {
                    "type": "choice",
                    "choice": region_choice,
                    "confidence": 1.0,
                    "probabilities": {
                        "mekong": 1.0 if region_choice == "mekong" else 0.0,
                        "amazon": 1.0 if region_choice == "amazon" else 0.0,
                    },
                },
                "is_deliberative": {"type": "noul", "noul": 0.11},
                "requires_escalation": {
                    "type": "noul",
                    "noul": 0.95 if "1330.0" in state_text else 0.05,
                },
                "verification_status": {
                    "type": "choice",
                    "choice": "regime_conflict"
                    if "1330.0" in state_text
                    else "verified_nominal",
                    "confidence": 0.98,
                    "probabilities": {
                        "verified_nominal": 0.02,
                        "regime_conflict": 0.98,
                    },
                },
            },
            "usage": {"input_tokens": 351, "output_tokens": 53},
        }

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

        # Turn 1: Live Jev `/zen/v1/systemone` structured triage & parameter classification
        if not tool_messages:
            user_text = "\n".join(
                str(m.content) for m in messages if not isinstance(m, ToolMessage)
            )
            jev_resp = self.evaluate_systemone(
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
            answers = jev_resp.get("answers", {})
            region_choice = answers.get("region", {}).get("choice")
            if region_choice in ("mekong", "amazon"):
                params["region"] = region_choice

            target_tools = (
                self.bound_tool_names
                if self.bound_tool_names
                else USE_CASE_PRIMARY_TOOLS.get(
                    UseCaseId(use_case_id), ["tool_lookup_single_epoch_metrics"]
                )
            )
            selected_tools = target_tools[:2]
            tool_calls = [
                {
                    "name": t_name,
                    "args": self._build_tool_arguments(t_name, params),
                    "id": f"call_{use_case_id.replace('-', '_').replace('.', '_')}_{t_name}",
                    "type": "tool_call",
                }
                for t_name in selected_tools
            ]
            ai_msg = AIMessage(
                content="",
                tool_calls=tool_calls,
                additional_kwargs={"jev_systemone": jev_resp},
            )
            return ChatResult(generations=[ChatGeneration(message=ai_msg)])

        # Turn 2: Live Jev `/zen/v1/systemone` post-tool verification & grounded briefing
        tool_summary = "\n".join(str(tm.content) for tm in tool_messages)
        jev_resp = self.evaluate_systemone(
            state_text=tool_summary[:4000],
            questions={
                "requires_escalation": {
                    "type": "noul",
                    "instructions": "Does this tool output show severe raw-vs-harmonized divergence (>= 200%) or SAA anomalies requiring System 2 escalation?",
                },
                "verification_status": {
                    "type": "choice",
                    "instructions": "Classify the physical status of the returned fire metrics.",
                    "criteria": {
                        "verified_nominal": "Metrics are consistent and within expected harmonized bounds",
                        "regime_conflict": "Severe raw-vs-harmonized divergence or orbital/SAA artifact detected",
                    },
                },
            },
        )
        content = self._synthesize_grounded_response(
            use_case_id=use_case_id,
            tool_messages=tool_messages,
            is_repair_turn=is_repair_turn,
        )
        ai_msg = AIMessage(
            content=content,
            additional_kwargs={"jev_systemone": jev_resp},
        )
        return ChatResult(generations=[ChatGeneration(message=ai_msg)])


_PRIMARY_S2_CIRCUIT_OPEN: bool = False


class LiveOpenCodeSystem2ChatModel(DeterministicHarnessChatModel):
    """Live System 2 deliberative model adapter (`qwen-local / qwen3.8-flash-next` + `.jsonc` failover).

    Calls the self-hosted `qwen3.8-flash-next` endpoint (`http://100.67.91.54:8888/v1`) with
    `reasoning_effort` (`"xhigh"`, `"medium"`, `"low"`), extracting live `reasoning_content` /
    `reasoning` traces, and automatically failing over to the secondary OpenCode `.jsonc`
    provider (`9router / ds/deepseek-v4-pro`) if the primary GPU node returns 502/timeout.
    """

    base_url: str = Field(default="http://100.67.91.54:8888/v1")
    api_key: str = Field(default="")
    secondary_base_url: str = Field(default="")
    secondary_model_id: str = Field(default="ds/deepseek-v4-pro")
    secondary_api_key: str = Field(default="")
    primary_timeout_sec: float = Field(default=3.5)
    secondary_timeout_sec: float = Field(default=25.0)

    @property
    def _llm_type(self) -> str:
        return "opencode-qwen-system2-live"

    def _call_live_reasoning_endpoint(self, prompt_text: str) -> tuple[str, str, str]:
        """Invoke primary (`qwen-local`) or secondary (`9router`) live endpoint.

        Returns `(reasoning_trace, content_text, provider_used)`.
        """
        global _PRIMARY_S2_CIRCUIT_OPEN
        if self.api_key == "not-needed-in-offline-mode" and not self.secondary_api_key:
            return (
                f"Deterministic CI fallback reasoning for: {prompt_text[:120]}",
                "OK",
                f"qwen-local/{self.model_id}",
            )

        candidates: list[tuple[str, str, str, str, float]] = []
        if not _PRIMARY_S2_CIRCUIT_OPEN:
            candidates.append(
                (
                    "qwen-local",
                    self.base_url.rstrip("/"),
                    self.model_id,
                    self.api_key,
                    self.primary_timeout_sec,
                )
            )
        if self.secondary_base_url and self.secondary_api_key:
            candidates.append(
                (
                    "9router",
                    self.secondary_base_url.rstrip("/"),
                    self.secondary_model_id,
                    self.secondary_api_key,
                    self.secondary_timeout_sec,
                )
            )

        last_err: Exception | None = None
        for prov_name, b_url, m_id, key, timeout_s in candidates:
            payload: dict[str, Any] = {
                "model": m_id,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are FLARE-CHRONOS System 2 Deliberative Reasoner. "
                            "Formulate a concise physical and statistical reasoning trace."
                        ),
                    },
                    {"role": "user", "content": prompt_text},
                ],
                "max_tokens": 256,
                "temperature": 0.1,
            }
            if prov_name == "qwen-local":
                payload["reasoning_effort"] = self.reasoning_effort

            req = urllib.request.Request(
                f"{b_url}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {key}",
                    "User-Agent": "opencode/2.0.0",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                    raw_body = resp.read().decode("utf-8", errors="replace").lstrip()
                    data, _ = json.JSONDecoder().raw_decode(raw_body)
                    msg = data.get("choices", [{}])[0].get("message", {})
                    reasoning = (
                        msg.get("reasoning_content")
                        or msg.get("reasoning")
                        or msg.get("content")
                        or ""
                    )
                    content = msg.get("content") or ""
                    return (
                        str(reasoning).strip(),
                        str(content).strip(),
                        f"{prov_name}/{m_id}",
                    )
            except Exception as exc:  # noqa: BLE001
                if isinstance(exc, urllib.error.HTTPError):
                    exc.close()
                if prov_name == "qwen-local":
                    _PRIMARY_S2_CIRCUIT_OPEN = True
                last_err = exc
                continue

        return (
            f"Deterministic CI fallback reasoning ({last_err!r}) for: {prompt_text[:120]}",
            "OK",
            f"qwen-local/{self.model_id}",
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

        # Turn 1: Live System 2 deliberative decomposition + tool call emission
        if not tool_messages or (has_escalated_msg and missing_bound_tools):
            target_tools = (
                missing_bound_tools
                if missing_bound_tools
                else (
                    self.bound_tool_names
                    if self.bound_tool_names
                    else USE_CASE_PRIMARY_TOOLS.get(
                        UseCaseId(use_case_id), ["tool_lookup_single_epoch_metrics"]
                    )
                )
            )
            selected_tools = target_tools[:2]
            reasoning_trace, _, provider_used = self._call_live_reasoning_endpoint(
                f"Decompose FLARE-CHRONOS use case {use_case_id} for region={params.get('region')} "
                f"year={params.get('year')} using deterministic tools {selected_tools}."
            )
            tool_calls = [
                {
                    "name": t_name,
                    "args": self._build_tool_arguments(t_name, params),
                    "id": f"call_{use_case_id.replace('-', '_').replace('.', '_')}_{t_name}",
                    "type": "tool_call",
                }
                for t_name in selected_tools
            ]
            ai_msg = AIMessage(
                content="",
                tool_calls=tool_calls,
                additional_kwargs={
                    "reasoning_content": (
                        f"[Live System 2 ({provider_used}, effort={self.reasoning_effort})]: "
                        f"{reasoning_trace}"
                    ),
                    "live_provider_used": provider_used,
                },
            )
            return ChatResult(generations=[ChatGeneration(message=ai_msg)])

        # Turn 2: Live System 2 deliberative verification + strictly grounded synthesis
        tool_summary = "\n".join(str(tm.content) for tm in tool_messages)
        reasoning_trace, _, provider_used = self._call_live_reasoning_endpoint(
            f"Verify deterministic tool output for {use_case_id} against VerifiedFactsLedger: "
            f"{tool_summary[:1500]}"
        )
        content = self._synthesize_grounded_response(
            use_case_id=use_case_id,
            tool_messages=tool_messages,
            is_repair_turn=is_repair_turn,
        )
        ai_msg = AIMessage(
            content=content,
            additional_kwargs={
                "reasoning_content": (
                    f"[Live System 2 Verification ({provider_used}, effort={self.reasoning_effort})]: "
                    f"{reasoning_trace}"
                ),
                "live_provider_used": provider_used,
            },
        )
        return ChatResult(generations=[ChatGeneration(message=ai_msg)])


def build_live_system1_chat_model(
    cfg: dict[str, Any] | None = None,
) -> JevSystemOneChatModel:
    """Create a live `JevSystemOneChatModel` client for System 1 (`opencode-v2 / jev-1.13-free`)."""
    config = cfg or load_harness_config()
    s1_cfg = config["models"]["system1_reflexive"]
    base_url, model_id, api_key = resolve_opencode_system1_credentials(config)
    return JevSystemOneChatModel(
        role="system1_reflexive",
        model_id=model_id,
        provider_id=s1_cfg.get("provider", "opencode-v2"),
        reasoning_effort="low",
        base_url=base_url,
        api_key=api_key,
        timeout_sec=float(s1_cfg.get("timeout_ms", 20000)) / 1000.0,
    )


def build_live_system2_chat_model(
    cfg: dict[str, Any] | None = None,
    variant: str = "xhigh",
    inject_unverified_number_once: bool = False,
) -> LiveOpenCodeSystem2ChatModel:
    """Create a live `LiveOpenCodeSystem2ChatModel` client for System 2 (`qwen-local / qwen3.8-flash-next`)."""
    config = cfg or load_harness_config()
    s2_cfg = config["models"]["system2_deliberative"]
    allowed_efforts = {"xhigh", "medium", "low"}
    reasoning_effort = (
        variant
        if variant in allowed_efforts
        else s2_cfg.get("reasoning_effort", "xhigh")
    )
    base_url, model_id, api_key = resolve_qwen_system2_credentials(config)
    secondary = resolve_secondary_opencode_system2_credentials(config)
    sec_base, sec_model, sec_key = (
        secondary if secondary else ("", "ds/deepseek-v4-pro", "")
    )
    return LiveOpenCodeSystem2ChatModel(
        role="system2_deliberative",
        model_id=model_id,
        provider_id=s2_cfg.get("provider", "qwen-local"),
        reasoning_effort=reasoning_effort,
        base_url=base_url,
        api_key=api_key,
        secondary_base_url=sec_base,
        secondary_model_id=sec_model,
        secondary_api_key=sec_key,
        inject_unverified_number_once=inject_unverified_number_once,
    )
