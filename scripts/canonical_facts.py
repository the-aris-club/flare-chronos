"""Centralized single-source-of-truth (SSOT) facts & claims registry for FLARE-CHRONOS.

Computes every headline metric directly from the committed empirical artifacts
(`data/processed/empirical_results.json`, `data/processed/burning_calendar.json`,
`data/processed/ai_harness_results.json`, `data/raw/fetch_manifest.json`) and live
code registries (`apps/ai-service/src/ai_service/schemas.py` & `tools.py`).

Used by `tests/test_documented_claims_consistency.py` and `scripts/check-docs.py`
to prevent numeric, architectural, or domain-glossary drift across all submission
deliverables (`exports/*.md`, `exports/*.pdf`, `docs/*.md`, `GLOSSARY.md`,
`DESIGN.md`, `README.md`).
"""

from __future__ import annotations

import ast
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for pkg_src in (
    ROOT / "apps" / "ai-service" / "src",
    ROOT / "packages" / "harmonization-core" / "src",
):
    if str(pkg_src) not in sys.path:
        sys.path.insert(0, str(pkg_src))


@dataclass(frozen=True)
class CanonicalFacts:
    """Single-source-of-truth quantitative & architectural facts."""

    # Archive & Benchmark Dataset
    total_firms_records: int
    cached_csv_slices: int
    benchmark_window_records: int

    # Scan-Angle & Footprint Geometry
    max_area_ratio_modis_edge_to_viirs_nadir: float
    modis_mean_area_km2: float
    modis_p95_area_km2: float
    viirs_mean_area_km2: float
    viirs_p95_area_km2: float
    empirical_mean_footprint_ratio: float

    # Co-Incident Aqua–SNPP Radiometric Calibration
    coincident_pairs: int
    alpha: float
    beta: float
    kappa: float
    ks_before: float
    ks_after: float
    ks_reduction_pct: float
    raw_r2: float
    harm_r2: float
    viirs_to_modis_count_ratio: float
    viirs_to_modis_frp_ratio: float

    # Multi-Decadal Case Studies (Mekong & Amazon)
    mekong_measured_epochs: int
    mekong_interpolated_years: int
    amazon_measured_epochs: int
    amazon_interpolated_years: int
    mekong_2001_modis_raw: int
    mekong_2024_raw_index: float
    mekong_2024_step_jump_pct: float
    mekong_2024_harm_episodes: float
    mekong_2024_harm_index: float
    mekong_2024_reduction_vs_2005_pct: float
    amazon_2024_raw_detections: int
    amazon_2024_episodes: int
    amazon_2024_compression_ratio: float
    amazon_2024_harm_episodes: float
    amazon_2024_harm_index: float

    # Burning Activity Calendar & SFAI Observed Peaks
    mekong_observed_peak_year: int
    mekong_observed_peak_sfai: float
    amazon_observed_peak_year: int
    amazon_observed_peak_sfai: float

    # Dual-System Cognitive AI Harness & Ports
    total_use_cases: int
    system1_use_cases: int
    system2_use_cases: int
    registered_model_tools: int
    atomic_tools: int
    diagnostic_tools: int
    total_tool_functions: int
    ai_service_port: int
    workbench_port: int

    # Test Suite
    test_files_count: int


# Strings that represent superseded or erroneous historical numbers/claims and
# must NEVER appear in active submission documents.
SUPERSEDED_DOCUMENT_CLAIMS: dict[str, tuple[str, ...]] = {
    "superseded FIRMS record count (775k)": ("775.531", "775,531"),
    "inflated FIRMS record count (+12 metadata rows)": ("1.609.194", "1,609,194"),
    "superseded co-incident pairs (5,769)": ("5.769", "5,769"),
    "superseded co-incident pairs (11,553)": ("11.553", "11,553"),
    "typo step-jump (+1,351.8%)": ("+1.351,8%", "+1,351.8%"),
    "stale wireframe step-jump (+1324%)": ("+1324%", "+1,324%", "+1.324%"),
    "wrong Mekong 2024 reduction (-5.8%)": ("giảm 5,8%", "5.8% below 2005"),
    "supersededUseCase ratio (20/15)": ("20/15 Use Cases", "20/15 use cases"),
    "superseded 20-use-case count": (
        "hai mươi phân tích",
        "twenty analyses",
        "20 Use Cases",
        "20 Use Case",
        "20/20 Use Cases",
        "18/20 Use Cases",
    ),
    "superseded 23/24 tool count": (
        "23 tool",
        "23 công cụ",
        "24 hàm `@tool`",
        "24 toán tử",
        "24 deterministic",
    ),
    "superseded stdlib port 8765": ("127.0.0.1:8765", "localhost:8765"),
    "false unimplemented Workbench claim": ("Specified but not yet implemented",),
    "non-existent ADR-0008 measured-epochs filename": (
        "0008-measured-epochs-and-interpolated-years.md",
    ),
}


def load_canonical_facts() -> CanonicalFacts:
    """Derive all canonical facts directly from committed artifacts and code."""
    manifest = json.loads(
        (ROOT / "data" / "raw" / "fetch_manifest.json").read_text(encoding="utf-8")
    )
    non_empty_slices = {k: v for k, v in manifest.items() if v > 0}

    results: dict[str, Any] = json.loads(
        (ROOT / "data" / "processed" / "empirical_results.json").read_text(
            encoding="utf-8"
        )
    )
    calendar: dict[str, Any] = json.loads(
        (ROOT / "data" / "processed" / "burning_calendar.json").read_text(
            encoding="utf-8"
        )
    )
    harness_res: dict[str, Any] = json.loads(
        (ROOT / "data" / "processed" / "ai_harness_results.json").read_text(
            encoding="utf-8"
        )
    )

    try:
        from ai_service.tools import (
            ALL_DETERMINISTIC_TOOLS,
            ATOMIC_TOOLS,
            DOMAIN_DIAGNOSTIC_TOOLS,
        )

        n_all_tools = len(ALL_DETERMINISTIC_TOOLS)
        n_atomic_tools = len(ATOMIC_TOOLS)
        n_diag_tools = len(DOMAIN_DIAGNOSTIC_TOOLS)
    except (ImportError, AttributeError):
        tools_tree = ast.parse(
            (
                ROOT / "apps" / "ai-service" / "src" / "ai_service" / "tools.py"
            ).read_text(encoding="utf-8")
        )
        list_lengths: dict[str, int] = {}
        for node in tools_tree.body:
            if (
                isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Name)
                and isinstance(node.value, ast.List)
            ):
                list_lengths[node.target.id] = len(node.value.elts)
        n_atomic_tools = list_lengths["ATOMIC_TOOLS"]
        n_diag_tools = list_lengths["DOMAIN_DIAGNOSTIC_TOOLS"]
        n_all_tools = list_lengths["ALL_DETERMINISTIC_TOOLS"]

    scan = results["scan_angle_physics"]
    calib = results["coincident_calibration"]
    mekong_series = results["regime_shift_series"]["mekong"]
    amazon_series = results["regime_shift_series"]["amazon"]

    mekong_epochs = {e["year"]: e for e in results["mekong_empirical_epochs"]}
    amazon_epochs = {e["year"]: e for e in results["amazon_empirical_epochs"]}

    m2024 = mekong_epochs[2024]
    a2024 = amazon_epochs[2024]
    mekong_2024_raw_idx = mekong_series["raw_index_2005_eq_100"][
        mekong_series["years"].index(2024)
    ]
    mekong_2024_harm_idx = mekong_series["harmonized_index_2005_eq_100"][
        mekong_series["years"].index(2024)
    ]
    amazon_2024_harm_idx = amazon_series["harmonized_index_2005_eq_100"][
        amazon_series["years"].index(2024)
    ]

    def _peak_observed_sfai(region: str) -> tuple[int, float]:
        reg = calendar[region]
        best_year = -1
        best_val = -999.0
        for y, row in zip(reg["years"], reg["sfai_matrix"], strict=True):
            vals = [v for v in row if v is not None]
            if vals and max(vals) > best_val:
                best_val = max(vals)
                best_year = int(y)
        return best_year, round(best_val, 1)

    m_peak_year, m_peak_sfai = _peak_observed_sfai("mekong")
    a_peak_year, a_peak_sfai = _peak_observed_sfai("amazon")

    test_files = sorted((ROOT / "tests").glob("test_*.py"))
    ks_red = round((1.0 - calib["ks_after"] / calib["ks_before"]) * 100.0, 1)

    return CanonicalFacts(
        total_firms_records=sum(non_empty_slices.values()),
        cached_csv_slices=len(non_empty_slices),
        benchmark_window_records=451_488,
        max_area_ratio_modis_edge_to_viirs_nadir=float(
            scan["max_area_ratio_modis_edge_to_viirs_nadir"]
        ),
        modis_mean_area_km2=float(scan["empirical_modis_mean_area_km2"]),
        modis_p95_area_km2=float(scan["empirical_modis_p95_area_km2"]),
        viirs_mean_area_km2=float(scan["empirical_viirs_mean_area_km2"]),
        viirs_p95_area_km2=float(scan["empirical_viirs_p95_area_km2"]),
        empirical_mean_footprint_ratio=round(
            float(scan["empirical_modis_mean_area_km2"])
            / float(scan["empirical_viirs_mean_area_km2"]),
            2,
        ),
        coincident_pairs=int(calib["n_pairs"]),
        alpha=float(calib["alpha"]),
        beta=float(calib["beta"]),
        kappa=float(calib["scan_tail_kappa"]),
        ks_before=float(calib["ks_before"]),
        ks_after=float(calib["ks_after"]),
        ks_reduction_pct=ks_red,
        raw_r2=float(calib["raw_r2"]),
        harm_r2=float(calib["harm_r2"]),
        viirs_to_modis_count_ratio=float(
            calib["mean_coincident_viirs_to_modis_count_ratio"]
        ),
        viirs_to_modis_frp_ratio=float(
            calib["mean_coincident_viirs_to_modis_frp_ratio"]
        ),
        mekong_measured_epochs=len(mekong_series["measured_years"]),
        mekong_interpolated_years=len(mekong_series["interpolated_years"]),
        amazon_measured_epochs=len(amazon_series["measured_years"]),
        amazon_interpolated_years=len(amazon_series["interpolated_years"]),
        mekong_2001_modis_raw=int(
            mekong_epochs[2001]["raw_counts_by_source"]["MODIS_SP"]
        ),
        mekong_2024_raw_index=float(mekong_2024_raw_idx),
        mekong_2024_step_jump_pct=round(float(mekong_2024_raw_idx) - 100.0, 1),
        mekong_2024_harm_episodes=float(m2024["harmonized_viirs_eq_episodes"]),
        mekong_2024_harm_index=float(mekong_2024_harm_idx),
        mekong_2024_reduction_vs_2005_pct=round(100.0 - float(mekong_2024_harm_idx), 1),
        amazon_2024_raw_detections=int(a2024["total_raw_detections"]),
        amazon_2024_episodes=int(a2024["deduplicated_fire_episodes"]),
        amazon_2024_compression_ratio=round(
            float(a2024["deduplication_compression_ratio"]), 2
        ),
        amazon_2024_harm_episodes=float(a2024["harmonized_viirs_eq_episodes"]),
        amazon_2024_harm_index=float(amazon_2024_harm_idx),
        mekong_observed_peak_year=m_peak_year,
        mekong_observed_peak_sfai=m_peak_sfai,
        amazon_observed_peak_year=a_peak_year,
        amazon_observed_peak_sfai=a_peak_sfai,
        total_use_cases=int(harness_res["total_use_cases_executed"]),
        system1_use_cases=int(harness_res["system1_use_cases_count"]),
        system2_use_cases=int(harness_res["system2_use_cases_count"]),
        registered_model_tools=n_all_tools,
        atomic_tools=n_atomic_tools,
        diagnostic_tools=n_diag_tools,
        total_tool_functions=n_all_tools + 1,
        ai_service_port=5901,
        workbench_port=5900,
        test_files_count=len(test_files),
    )


if __name__ == "__main__":
    facts = load_canonical_facts()
    print(json.dumps(asdict(facts), indent=2))
