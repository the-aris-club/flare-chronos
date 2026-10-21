"""Execute all 20 Dual-System Use Cases (`UC-S1.1..UC-S1.5` & `UC-1.1..UC-5.3`) through LangGraph.

Saves the complete execution trace, verified facts counts, and symbiosis benchmarks to
`data/processed/ai_harness_results.json`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# Ensure workspace packages are importable
REPO_ROOT = Path(__file__).resolve().parents[4]
for pkg_src in (
    REPO_ROOT / "apps" / "ai-service" / "src",
    REPO_ROOT / "packages" / "harmonization-core" / "src",
):
    if str(pkg_src) not in sys.path:
        sys.path.insert(0, str(pkg_src))

from ai_service.harness import FlareChronosDualSystemHarness
from ai_service.schemas import UseCaseId

USE_CASE_BENCHMARK_QUERIES: list[tuple[UseCaseId, str]] = [
    # 5 System-1 Reflexive Use Cases
    (
        UseCaseId.UC_S1_1_INTENT_TRIAGE,
        "UC-S1.1 Triage fast validation metrics overview for 2024 mekong.",
    ),
    (
        UseCaseId.UC_S1_2_ENTITY_EXTRACTION,
        "UC-S1.2 Extract spatio-temporal entities for 2005 to 2024 in amazon.",
    ),
    (
        UseCaseId.UC_S1_3_SINGLE_HOP_LOOKUP,
        "UC-S1.3 Fast single-hop metric lookup for 2024 mekong harmonized index.",
    ),
    (
        UseCaseId.UC_S1_4_FLASH_NRT_ALERT,
        "UC-S1.4 Generate flash NRT tactical ranger alert for amazon in 2026.",
    ),
    (
        UseCaseId.UC_S1_5_STAKEHOLDER_SYNTHESIS,
        "UC-S1.5 Format executive policy summary for ASEAN forestry_executive in 2024 mekong.",
    ),
    # 15 System-2 Deliberative Use Cases
    (
        UseCaseId.UC_1_1_REGIME_SHIFT_ATTRIBUTION,
        "UC-1.1 Decompose the 2005 to 2024 fire regime shift in mekong between sensor multiplicity and physical trend.",
    ),
    (
        UseCaseId.UC_1_2_CROSS_SENSOR_DISCREPANCY,
        "UC-1.2 Diagnose cross-sensor MODIS vs VIIRS discrepancy forensics in 2024.",
    ),
    (
        UseCaseId.UC_1_3_THERMAL_SOURCE_ORIGIN,
        "UC-1.3 Classify thermal source origins across agricultural residue, deforestation, and static industrial flares in mekong.",
    ),
    (
        UseCaseId.UC_2_1_PHENOLOGY_PHASE_SHIFT,
        "UC-2.1 Detect early-onset burning phenological phase-shifts in mekong.",
    ),
    (
        UseCaseId.UC_2_2_TACTICAL_DISPATCH,
        "UC-2.2 Compute uncertainty-aware tactical ranger dispatch search ellipses and VIIRS revisit intervals.",
    ),
    (
        UseCaseId.UC_2_3_VERIFIED_BRIEFING,
        "UC-2.3 Assemble cross-verified multi-stakeholder briefing data for 2024 mekong.",
    ),
    (
        UseCaseId.UC_3_1_CONSTELLATION_RETIREMENT,
        "UC-3.1 Simulate post-2026 constellation retirement of Terra, Aqua, and Suomi-NPP using JPSS-only in mekong 2024.",
    ),
    (
        UseCaseId.UC_3_2_MULTIHOP_SPATIOTEMPORAL,
        "UC-3.2 Execute multi-hop spatio-temporal cube query across the 26-year 2001 to 2026 Mekong and Amazon archives.",
    ),
    (
        UseCaseId.UC_3_3_BIOME_RECALIBRATION,
        "UC-3.3 Audit the N=11553 Aqua-SNPP co-incident calibration transfer function and KS reduction.",
    ),
    (
        UseCaseId.UC_4_1_ORBITAL_DRIFT_SZA_AUDIT,
        "UC-4.1 Audit Terra/Aqua orbital drift and MODIS reference count stability from 2001 to 2026.",
    ),
    (
        UseCaseId.UC_4_2_NRT_VS_SP_FIDELITY,
        "UC-4.2 Audit Near-Real-Time vs Standard Processing fidelity and SAA nighttime false alarm filtering.",
    ),
    (
        UseCaseId.UC_4_3_ADAPTIVE_RATE_LIMIT,
        "UC-4.3 Compute adaptive NASA FIRMS rate-limit budget across the 134 cached slices.",
    ),
    (
        UseCaseId.UC_5_1_REDD_CARBON_MRV,
        "UC-5.1 Audit sensor-invariant FRP and Harmonized Radiative Flux for REDD+ carbon MRV in amazon 2024.",
    ),
    (
        UseCaseId.UC_5_2_POLICY_COUNTERFACTUAL,
        "UC-5.2 Evaluate agricultural residue burn-ban policy counterfactual effectiveness across 2019 to 2026 in mekong.",
    ),
    (
        UseCaseId.UC_5_3_TRANSBOUNDARY_FORENSICS,
        "UC-5.3 Analyze transboundary fire episode clustering and H3 hexagonal propagation across the mekong corridor.",
    ),
]


def run_all_benchmarks(
    mode: str = "deterministic", enable_sign_off: bool = False
) -> dict[str, Any]:
    """Run all 20 use cases + 3 symbiosis stress tests through the compiled LangGraph harness."""
    harness = FlareChronosDualSystemHarness(
        mode=mode,  # type: ignore[arg-type]
        enable_cache=True,
        enable_sign_off=enable_sign_off,
    )
    use_case_runs: list[dict[str, Any]] = []

    for idx, (uc_enum, query) in enumerate(USE_CASE_BENCHMARK_QUERIES, start=1):
        try:
            state_out = harness.invoke_to_completion(
                user_query=query,
                use_case_id=uc_enum,
                thread_id=f"bench-uc-{idx:02d}",
            )
        except Exception as exc:  # noqa: BLE001 - one failure must not stop the batch
            use_case_runs.append(
                {
                    "use_case_id": uc_enum.value,
                    "error": f"{type(exc).__name__}: {exc}"[:400],
                    "verification_passed": False,
                }
            )
            continue
        ver_report = state_out.get("verification_report", {})
        ledger_entries = state_out.get("verified_ledger_entries", [])
        use_case_runs.append(
            {
                "use_case_id": uc_enum.value,
                "cognitive_path": state_out.get("cognitive_path"),
                "pruned_tool_names": state_out.get("pruned_tool_names", []),
                "verified_facts_ingested": len(ledger_entries),
                "verification_passed": bool(ver_report.get("passed", False)),
                "checked_numbers_count": int(
                    ver_report.get("checked_numbers_count", 0)
                ),
                "unverified_numbers_count": len(
                    ver_report.get("unverified_numbers", [])
                ),
                "self_correction_retries": int(
                    state_out.get("self_correction_retries", 0)
                ),
                "clarification_requests": len(
                    state_out.get("clarification_requests", [])
                ),
                "clarification_questions": [
                    c.get("question", "")
                    for c in state_out.get("clarification_requests", [])
                ],
                "tool_rounds": sum(
                    1 for m in state_out.get("messages", []) if getattr(m, "name", None)
                ),
                "verification_rejections": state_out.get("verification_rejections", []),
                "usage": (state_out.get("live_telemetry") or {}).get("usage", {}),
                "has_system2_reasoning_trace": bool(state_out.get("reasoning_trace")),
                "synthesis_mode": state_out.get("synthesis_mode", "unknown"),
                "final_briefing_preview": str(state_out.get("final_briefing", ""))[
                    :1200
                ],
            }
        )

    # Symbiosis Test 1: Dynamic System 1 -> System 2 Escalation on Physical Conflict
    escalation_out = harness.invoke_use_case(
        user_query=(
            "UC-S1.3 Fast lookup for 2024 mekong ESCALATE_IF_CONFLICT "
            "when raw vs harmonized divergence exceeds 200%."
        ),
        use_case_id=UseCaseId.UC_S1_3_SINGLE_HOP_LOOKUP,
        thread_id="symbiosis-escalation-test",
    )

    # Symbiosis Test 2: NumericGroundingVerifier Reject & Self-Correction Loop
    repair_harness = FlareChronosDualSystemHarness(
        mode=mode,  # type: ignore[arg-type]
        inject_unverified_number_once=True,
        enable_cache=False,
        enable_sign_off=False,
    )
    repair_out = repair_harness.invoke_use_case(
        user_query="UC-1.1 Decompose the 2005 to 2024 fire regime shift in mekong.",
        use_case_id=UseCaseId.UC_1_1_REGIME_SHIFT_ATTRIBUTION,
        thread_id="symbiosis-verifier-repair-test",
    )

    # Symbiosis Test 3: System 2 -> System 1 VerifiedPatternCache Hit
    cache_hit_out = harness.invoke_use_case(
        user_query=USE_CASE_BENCHMARK_QUERIES[5][1],
        use_case_id=UseCaseId.UC_1_1_REGIME_SHIFT_ATTRIBUTION,
        thread_id="symbiosis-cache-hit-test",
    )

    summary_payload: dict[str, Any] = {
        "harness_framework": "LangGraph StateGraph + ToolNode + MemorySaver + Pydantic v2",
        "models": {
            "system1_reflexive": {
                "protocol": harness.s1_profile.protocol,
                "model_id": harness.s1_profile.model_id,
                "endpoint": harness.s1_profile.endpoint,
            },
            "system2_deliberative": {
                "protocol": harness.s2_profile.protocol,
                "model_id": harness.s2_profile.model_id,
                "endpoint": harness.s2_profile.endpoint,
                "thinking_level": harness.s2_profile.request.thinking_level,
            },
        },
        "mode": harness.mode,
        "total_use_cases_executed": len(use_case_runs),
        "system1_use_cases_count": 5,
        "system2_use_cases_count": 15,
        "deterministic_tools_registered": 23,
        "all_verifications_passed": all(
            r["verification_passed"] for r in use_case_runs
        ),
        "zero_unverified_numbers_in_final_outputs": all(
            r["unverified_numbers_count"] == 0 for r in use_case_runs
        ),
        "symbiosis_benchmarks": {
            "s1_to_s2_dynamic_escalation": {
                "initial_use_case": UseCaseId.UC_S1_3_SINGLE_HOP_LOOKUP.value,
                "resulting_cognitive_path": escalation_out.get("cognitive_path"),
                "escalated_from_system1": escalation_out.get("escalated_from_system1"),
                "escalation_reason": escalation_out.get("escalation_reason"),
                "escalated_tools": escalation_out.get("pruned_tool_names"),
                "verification_passed": escalation_out.get(
                    "verification_report", {}
                ).get("passed"),
            },
            "numeric_verifier_self_correction_loop": {
                "injected_unverified_number": 98765.4321,
                "self_correction_retries_triggered": repair_out.get(
                    "self_correction_retries"
                ),
                "final_verification_passed": repair_out.get(
                    "verification_report", {}
                ).get("passed"),
                "final_unverified_numbers": repair_out.get(
                    "verification_report", {}
                ).get("unverified_numbers"),
            },
            "s2_to_s1_verified_pattern_cache": {
                "use_case_id": UseCaseId.UC_1_1_REGIME_SHIFT_ATTRIBUTION.value,
                "cognitive_path": cache_hit_out.get("cognitive_path"),
                "distilled_cache_hit": cache_hit_out.get("distilled_cache_hit"),
                "cached_patterns_total": harness.pattern_cache.size(),
            },
        },
        "use_case_runs": use_case_runs,
    }

    out_name = (
        "ai_harness_results_live.json" if mode == "live" else "ai_harness_results.json"
    )
    out_path = REPO_ROOT / "data" / "processed" / out_name
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")
    return summary_payload


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Chạy toàn bộ 20 Use Cases của Dual-System Harness."
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Gọi mô hình thật (tốn credit). Mặc định chạy ngoại tuyến.",
    )
    parser.add_argument(
        "--sign-off",
        action="store_true",
        help="Bật cổng phê duyệt của con người (run sẽ dừng chờ).",
    )
    args = parser.parse_args()
    results = run_all_benchmarks(
        mode="live" if args.live else "deterministic",
        enable_sign_off=args.sign_off,
    )
    print(
        json.dumps(
            {
                "total_use_cases_executed": results["total_use_cases_executed"],
                "all_verifications_passed": results["all_verifications_passed"],
                "zero_unverified_numbers_in_final_outputs": results[
                    "zero_unverified_numbers_in_final_outputs"
                ],
                "symbiosis_benchmarks": results["symbiosis_benchmarks"],
            },
            indent=2,
        )
    )
