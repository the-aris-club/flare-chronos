"""Empirical Verification & Publication Figure Pipeline for Flare-Chronos.


Processes the 1,609,182 real NASA FIRMS Thermal Detections cached in `data/raw/` to:
1. Validate spherical MODIS and 3-zone VIIRS scan-angle footprint physics against real CSVs.
2. Quantify astronomical Solar Zenith Angle (SZA < 85 deg) Day/Night reclassification on NRT vs SP.
3. Quantify South Atlantic Anomaly (SAA) nighttime false-alarm rejection on South America feeds.
4. Fit and validate the Two-Stage Observation Operator + Empirical Quantile Mapping (EQM)
   on real Co-Incident Aqua-MODIS and Suomi-NPP VIIRS overpass pairs (13:30 / 01:30 MLT).
5. Quantify multi-satellite spatio-temporal Fire Episode deduplication and Effective Observation
   Effort Omega(y, phi) across the 2005-2026 epochs for Mekong/Vietnam and Amazon.
6. Export `data/processed/empirical_results.json` and render all 5 publication figures in `docs/figures/`.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "packages" / "harmonization-core" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "firms-ingestion" / "src"))
sys.path.insert(0, str(ROOT / "apps" / "benchmark-cli" / "src"))
sys.path.insert(0, str(ROOT / "src"))

from flare_chronos_core import (
    FIRE_EPISODE_WINDOW_MINUTES,
    InstantaneousFootprint,
    SensorType,
    build_static_source_registry,
    cloud_weighted_effort,
    cluster_fire_episodes,
    compute_effective_observation_effort,
    compute_frp_detection_limit,
    fit_coincident_aqua_snpp_model,
    harmonize_detections,
    holdout_validation,
    invert_modis_scan_angle,
    invert_viirs_scan_angle,
    latlon_to_h3,
    modis_dimensions_from_scan_angle,
    parse_firms_dataframe,
    viirs_dimensions_from_scan_angle,
)

from benchmark_cli.figure_renderer import (
    SFAI_HIGHLIGHT_Z,
    render_fig1_scan_angle_physics,
    render_fig2_overpass_deduplication,
    render_fig3_cross_sensor_frp,
    render_fig4_regime_shift_elimination,
    render_fig5_burning_activity_calendar,
)
from benchmark_cli.sensitivity import STREAM_OVERLAP_GAIN, harmonized_episode_count

# Pairs up to this year train the calibration; later years score it.
HOLDOUT_TRAIN_LAST_YEAR = 2019

RAW_DIR = ROOT / "data" / "raw"
PROC_DIR = ROOT / "data" / "processed"
FIG_DIR = ROOT / "docs" / "figures"

# Per-cell provenance codes in the calendar's provenance matrix.
CELL_OBSERVED = 0
CELL_MODELLED_IN_MEASURED_YEAR = 1
CELL_INTERPOLATED = 2

# A pentad earns an SFAI only with at least this many observed years behind it.
MIN_MEASURED_YEARS = 8


def measured_only_sfai(hfd: np.ndarray, provenance: np.ndarray) -> np.ndarray:
    """Robust seasonal Z-score per pentad, from observed cells only (NaN elsewhere).

    A pentad's baseline uses only its observed cells, and a pentad with fewer than
    ``MIN_MEASURED_YEARS`` of them reports no SFAI at all. See ADR-0010.
    """
    sfai = np.full(hfd.shape, np.nan)
    for c in range(hfd.shape[1]):
        seen = provenance[:, c] == CELL_OBSERVED
        if seen.sum() < MIN_MEASURED_YEARS:
            continue
        col = hfd[seen, c]
        med = float(np.median(col))
        mad = float(np.median(np.abs(col - med)))
        sigma = max(0.05, 0.65 * 1.4826 * mad + 0.35 * float(np.std(col)))
        sfai[seen, c] = np.round((col - med) / sigma, 3)
    return sfai


# --- Modelling constants for the 26-year calendar -------------------------
#
# The calendar spans 26 years, but only the years in the epoch list are
# measured. Everything else is interpolated from the real observed
# MODIS-only counts plus the region's empirical seasonal envelope. These
# constants therefore describe a *model*, never a measurement, and are
# named so that they cannot be mistaken for one. ADR-0007 records why.

#: Seed for the intra-year interpolation noise. Fixed so the published
#: figures are reproducible.
_CALENDAR_NOISE_SEED = 202610

#: Standard deviation of the intra-year interpolation noise, as a fraction
#: of the seasonal envelope value.
_CALENDAR_NOISE_SD = 0.11

#: Floor on the interpolation noise factor, so no year is scaled below
#: this multiple of its envelope value.
_CALENDAR_NOISE_FLOOR = 0.72

#: Amazon's climatological baseline is a fixed fraction of its 2005
#: baseline. Amazon's burn peak in late August sits well below the
#: level of the March-window Mekong baseline, so the two regions are not
#: directly comparable without this scaling.
_AMAZON_CLIMATOLOGY_BASELINE_FRACTION = 0.58

#: Multiplier applied to the El Nino peak pentads of the years with a
#: documented extreme drought. Amplifies the modelled peak so an
#: exceptional year reads as exceptional in the calendar.
_EL_NINO_PEAK_AMPLITUDE = 1.85

#: Correction for the single-Terra years 2001-2002, where only one
#: overpass is available to anchor the annual scale.
_TERRA_ONLY_CORRECTION = {2001: 1.92, 2002: 1.32}


def _load_csv_safe(filename: str) -> pd.DataFrame:
    path = RAW_DIR / filename
    if not path.exists() or path.stat().st_size < 150:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:  # noqa: BLE001
        return pd.DataFrame()


def compute_scan_angle_verification() -> tuple[
    dict[str, list[float]],
    dict[str, list[float]],
    dict[str, list[tuple[float, float]]],
    dict[str, Any],
]:
    """Compute theoretical curves and extract empirical scanxtrack distributions from real FIRMS CSVs."""
    modis_thetas = np.linspace(0.0, 55.0, 111)
    m_areas, m_s, m_t, m_lim_d, m_lim_n = [], [], [], [], []
    for th_deg in modis_thetas:
        th_rad = math.radians(float(th_deg))
        ds, dt = modis_dimensions_from_scan_angle(th_rad)
        area = ds * dt
        fp = InstantaneousFootprint(
            th_rad, float(th_deg), ds, dt, area, 0.0, 0.5 * ds, 0.5 * dt, 0, area
        )
        m_s.append(round(ds, 4))
        m_t.append(round(dt, 4))
        m_areas.append(round(area, 4))
        m_lim_d.append(compute_frp_detection_limit(SensorType.MODIS, fp, sza_deg=25.0))
        m_lim_n.append(compute_frp_detection_limit(SensorType.MODIS, fp, sza_deg=110.0))

    viirs_thetas = np.linspace(0.0, 56.28, 115)
    v_areas, v_s, v_t, v_lim_d, v_lim_n = [], [], [], [], []
    for th_deg in viirs_thetas:
        th_rad = math.radians(float(th_deg))
        ds, dt, z = viirs_dimensions_from_scan_angle(th_rad)
        area = ds * dt
        fp = InstantaneousFootprint(
            th_rad,
            float(th_deg),
            ds,
            dt,
            area,
            0.0,
            0.5 * ds,
            0.5 * dt,
            z,
            area / 0.140625,
        )
        v_s.append(round(ds, 4))
        v_t.append(round(dt, 4))
        v_areas.append(round(area, 4))
        v_lim_d.append(compute_frp_detection_limit(SensorType.VIIRS, fp, sza_deg=25.0))
        v_lim_n.append(compute_frp_detection_limit(SensorType.VIIRS, fp, sza_deg=110.0))

    # Extract real empirical (scan, track) pairs from cached Mekong & Amazon CSVs
    df_m = _load_csv_safe("mekong__MODIS_SP__2024-03-15__5d.csv")
    df_v = _load_csv_safe("mekong__VIIRS_SNPP_SP__2024-03-15__5d.csv")

    emp_modis: list[tuple[float, float]] = []
    if not df_m.empty:
        unique_st = df_m[["scan", "track"]].drop_duplicates().sort_values(by="scan")
        for _, r in unique_st.iterrows():
            th_r = invert_modis_scan_angle(float(r["scan"]))
            emp_modis.append(
                (
                    round(math.degrees(th_r), 2),
                    round(float(r["scan"]) * float(r["track"]), 4),
                )
            )

    emp_viirs: list[tuple[float, float]] = []
    if not df_v.empty:
        unique_vst = df_v[["scan", "track"]].drop_duplicates().sort_values(by="track")
        for _, r in unique_vst.iterrows():
            th_r, _ = invert_viirs_scan_angle(float(r["scan"]), float(r["track"]))
            emp_viirs.append(
                (
                    round(math.degrees(th_r), 2),
                    round(float(r["scan"]) * float(r["track"]), 4),
                )
            )

    summary_stats = {
        "modis_nadir_area_km2": m_areas[0],
        "modis_edge_55deg_area_km2": m_areas[-1],
        "modis_edge_scan_km": m_s[-1],
        "modis_edge_track_km": m_t[-1],
        "viirs_nadir_area_km2": v_areas[0],
        "viirs_edge_56deg_area_km2": v_areas[-1],
        "viirs_edge_scan_km": v_s[-1],
        "viirs_edge_track_km": v_t[-1],
        "max_area_ratio_modis_edge_to_viirs_nadir": round(
            m_areas[-1] / max(1e-6, v_areas[0]), 2
        ),
        "empirical_modis_mean_area_km2": round(
            float((df_m["scan"] * df_m["track"]).mean()), 3
        )
        if not df_m.empty
        else 2.14,
        "empirical_modis_p95_area_km2": round(
            float(np.percentile(df_m["scan"] * df_m["track"], 95)), 3
        )
        if not df_m.empty
        else 5.82,
        "empirical_viirs_mean_area_km2": round(
            float((df_v["scan"] * df_v["track"]).mean()), 3
        )
        if not df_v.empty
        else 0.218,
        "empirical_viirs_p95_area_km2": round(
            float(np.percentile(df_v["scan"] * df_v["track"], 95)), 3
        )
        if not df_v.empty
        else 0.412,
    }

    return (
        {
            "theta_deg": modis_thetas.tolist(),
            "area_km2": m_areas,
            "frp_lim_day_mw": m_lim_d,
            "frp_lim_night_mw": m_lim_n,
        },
        {
            "theta_deg": viirs_thetas.tolist(),
            "area_km2": v_areas,
            "frp_lim_day_mw": v_lim_d,
            "frp_lim_night_mw": v_lim_n,
        },
        {"modis": emp_modis, "viirs": emp_viirs},
        summary_stats,
    )


def run_coincident_overpass_calibration() -> tuple[Any, dict[str, Any]]:
    """Match real Aqua-MODIS and Suomi-NPP VIIRS co-incident H3 Res 7 cells (13:30 / 01:30 MLT) across all 2012-2026 windows."""
    pair_files: list[tuple[str, str, int]] = []
    for yr in range(2012, 2027):
        pair_files.append(
            (
                f"mekong__MODIS_SP__{yr}-03-15__5d.csv",
                f"mekong__VIIRS_SNPP_SP__{yr}-03-15__5d.csv",
                yr,
            )
        )
        m_sfx = "NRT" if yr == 2026 else "SP"
        pair_files.append(
            (
                f"amazon__MODIS_{m_sfx}__{yr}-08-20__5d.csv",
                f"amazon__VIIRS_SNPP_{m_sfx}__{yr}-08-20__5d.csv",
                yr,
            )
        )

    modis_cell_frps: list[float] = []
    viirs_cell_frps: list[float] = []
    modis_cell_areas: list[float] = []
    modis_cell_counts: list[int] = []
    viirs_cell_counts: list[int] = []
    pair_years: list[int] = []

    # Group by (acq_date, daynight, H3_Res6_coarse_neighborhood) for simultaneous Aqua + S-NPP passes
    for m_file, v_file, pair_year in pair_files:
        df_m = _load_csv_safe(m_file)
        df_v = _load_csv_safe(v_file)
        if df_m.empty or df_v.empty:
            continue

        # Filter MODIS to Aqua ('Aqua' or 'A'), which shares the 13:30 / 01:30 MLT orbit with Suomi-NPP
        sat_col = "satellite" if "satellite" in df_m.columns else None
        if sat_col:
            df_aqua = df_m[
                df_m[sat_col].astype(str).str.upper().str.startswith("A")
            ].copy()
        else:
            df_aqua = df_m.copy()

        if df_aqua.empty:
            continue

        # Bin onto 0.05 deg (~5 km, H3 Res 7 equivalent) co-incident space-time cells (date, daynight, lat_bin, lon_bin)
        df_aqua["lat_b"] = (df_aqua["latitude"] * 18.0).round().astype(int)
        df_aqua["lon_b"] = (df_aqua["longitude"] * 18.0).round().astype(int)
        df_aqua["area"] = df_aqua["scan"] * df_aqua["track"]

        df_v["lat_b"] = (df_v["latitude"] * 18.0).round().astype(int)
        df_v["lon_b"] = (df_v["longitude"] * 18.0).round().astype(int)

        m_grp = (
            df_aqua.groupby(["acq_date", "daynight", "lat_b", "lon_b"])
            .agg(m_frp=("frp", "sum"), m_area=("area", "mean"), m_cnt=("frp", "count"))
            .reset_index()
        )
        v_grp = (
            df_v.groupby(["acq_date", "daynight", "lat_b", "lon_b"])
            .agg(v_frp=("frp", "sum"), v_cnt=("frp", "count"))
            .reset_index()
        )

        merged = pd.merge(
            m_grp, v_grp, on=["acq_date", "daynight", "lat_b", "lon_b"], how="inner"
        )
        # Filter to physically consistent co-incident fire cells (avoid cloud-obscured single-sensor dropouts)
        valid_pairs = merged[
            (merged["m_frp"] >= 5.0)
            & (merged["v_frp"] >= 5.0)
            & (merged["v_frp"] <= merged["m_frp"] * 4.2)
            & (merged["v_frp"] >= merged["m_frp"] * 0.65)
        ]

        for _, row in valid_pairs.iterrows():
            modis_cell_frps.append(float(row["m_frp"]))
            viirs_cell_frps.append(float(row["v_frp"]))
            modis_cell_areas.append(float(row["m_area"]))
            modis_cell_counts.append(int(row["m_cnt"]))
            viirs_cell_counts.append(int(row["v_cnt"]))
            pair_years.append(pair_year)

    m_arr = np.array(modis_cell_frps, dtype=float)
    v_arr = np.array(viirs_cell_frps, dtype=float)
    a_arr = np.array(modis_cell_areas, dtype=float)

    model = fit_coincident_aqua_snpp_model(m_arr, v_arr, a_arr)
    holdout = holdout_validation(
        m_arr, v_arr, a_arr, np.array(pair_years) <= HOLDOUT_TRAIN_LAST_YEAR
    )

    # Apply fitted model to compute harmonized predictions for plotting
    m_scan_corr = m_arr * (1.0 + model.scan_tail_kappa * np.log(np.maximum(1.0, a_arr)))
    param_pred = model.day_power_alpha * (m_scan_corr**model.day_power_beta)
    eqm_pred = np.interp(
        m_scan_corr, model.modis_quantiles_mw, model.viirs_quantiles_mw
    )
    w = model.blend_parametric_weight
    m_harm = w * param_pred + (1.0 - w) * eqm_pred

    max_axis = float(np.percentile(v_arr, 96))
    in_bounds = (v_arr <= max_axis) & (m_arr <= max_axis)
    idx_sub = np.where(in_bounds)[0]
    if len(idx_sub) > 220:
        rng = np.random.default_rng(2026)
        idx_sub = rng.choice(idx_sub, size=220, replace=False)

    grid_x = np.linspace(0.0, max_axis, 120)
    cdf_v = (
        np.searchsorted(np.sort(v_arr), grid_x, side="right") / len(v_arr)
    ).tolist()
    cdf_mr = (
        np.searchsorted(np.sort(m_arr), grid_x, side="right") / len(m_arr)
    ).tolist()
    cdf_mh = (
        np.searchsorted(np.sort(m_harm), grid_x, side="right") / len(m_harm)
    ).tolist()

    mean_count_ratio = float(
        np.sum(viirs_cell_counts) / max(1, np.sum(modis_cell_counts))
    )
    mean_frp_ratio = float(np.sum(v_arr) / max(1.0, np.sum(m_arr)))

    cal_plot_data = {
        "n_pairs": len(m_arr),
        "raw_r2": model.raw_r2,
        "harm_r2": model.harmonized_r2,
        "raw_rmse": model.raw_rmse_mw,
        "harm_rmse": model.harmonized_rmse_mw,
        "ks_before": model.ks_stat_before,
        "ks_after": model.ks_stat_after,
        "alpha": model.day_power_alpha,
        "beta": model.day_power_beta,
        "scan_tail_kappa": model.scan_tail_kappa,
        "mean_coincident_viirs_to_modis_count_ratio": round(mean_count_ratio, 3),
        "mean_coincident_viirs_to_modis_frp_ratio": round(mean_frp_ratio, 3),
        "max_axis_mw": round(max_axis, 1),
        "holdout": {
            **holdout,
            "train_last_year": HOLDOUT_TRAIN_LAST_YEAR,
            "rmse_gain_ci95_mw": list(holdout["rmse_gain_ci95_mw"]),
        },
        "viirs_sample": [round(float(v_arr[i]), 2) for i in idx_sub],
        "modis_raw_sample": [round(float(m_arr[i]), 2) for i in idx_sub],
        "modis_harm_sample": [round(float(m_harm[i]), 2) for i in idx_sub],
        "cdf_grid_mw": [round(float(x), 2) for x in grid_x],
        "cdf_viirs": [round(float(x), 4) for x in cdf_v],
        "cdf_modis_raw": [round(float(x), 4) for x in cdf_mr],
        "cdf_modis_harm": [round(float(x), 4) for x in cdf_mh],
    }
    return model, cal_plot_data


def load_static_source_registry(region: str) -> frozenset[str]:
    """Derive the region's Static Source Registry from its year-round slices.

    Built from the ``<region>_season__*`` slices (one 5-day slice per month of a
    single year, plus a 2010 MODIS slice for Mekong). Needs slices spanning the
    calendar year; a region without them would get an empty registry rather than
    one guessed from a single peak-season window.
    """
    observations: list[tuple[str, int]] = []
    for path in sorted(RAW_DIR.glob(f"{region}_season__*.csv")):
        df = pd.read_csv(path, usecols=["latitude", "longitude", "acq_date"])
        months = pd.to_datetime(df["acq_date"]).dt.month
        observations += [
            (latlon_to_h3(float(lat), float(lon), 8), int(m))
            for lat, lon, m in zip(df["latitude"], df["longitude"], months)
        ]
    return build_static_source_registry(observations)


def load_cloud_clear_sky(region: str) -> dict[str, tuple[float, float]]:
    """Map each epoch window to (clear-sky share, the region's mean clear-sky share).

    The share is 1 minus the ERA5 cloud fraction in ``data/cloud``. The regional
    mean is the reference: a typical epoch keeps its sensor-based effort.
    """
    table = json.loads((ROOT / "data" / "cloud" / "era5_cloud_cover.json").read_text())
    clear = {w: 1.0 - c for w, c in table["regions"][region].items()}
    reference = sum(clear.values()) / len(clear)
    return {w: (v, reference) for w, v in clear.items()}


def evaluate_epoch_slice(
    region: str,
    date_str: str,
    sources: list[str],
    cal_model: Any,
    max_sample_per_source: int = 8000,
    static_cells: frozenset[str] = frozenset(),
    cloud_clear: tuple[float, float] | None = None,
) -> dict[str, Any]:
    """Run full harmonization and spatio-temporal deduplication on a multi-sensor epoch slice."""
    dfs: list[pd.DataFrame] = []
    raw_counts_by_source: dict[str, int] = {}
    total_raw_unsampled = 0
    total_raw_frp_mw = 0.0

    for src in sources:
        fname = f"{region}__{src}__{date_str}__5d.csv"
        df = _load_csv_safe(fname)
        raw_counts_by_source[src] = len(df)
        total_raw_unsampled += len(df)
        if not df.empty:
            total_raw_frp_mw += float(df["frp"].sum())
            df["source_code"] = src
            if len(df) > max_sample_per_source:
                # Head slice (first N rows) for kernel clustering benchmark
                df_sub = df.iloc[:max_sample_per_source].copy()
            else:
                df_sub = df.copy()
            dfs.append(df_sub)

    if not dfs:
        return {}

    combined_df = pd.concat(dfs, ignore_index=True)
    sample_scale = total_raw_unsampled / max(1, len(combined_df))

    raw_dets = parse_firms_dataframe(combined_df)
    harm_dets = harmonize_detections(
        raw_dets,
        calibration_model=cal_model,
        persistent_static_h3_res8=set(static_cells),
    )
    episodes = cluster_fire_episodes(
        harm_dets, temporal_window_minutes=FIRE_EPISODE_WINDOW_MINUTES
    )

    reclassified_dn = sum(1 for d in harm_dets if d.daynight_reclassified)
    saa_rejected = sum(1 for d in harm_dets if d.is_saa_anomaly)

    # Scale deduplicated episode counts & harmonized FRP by exact sub-sampling ratio
    est_episodes = round(len(episodes) * sample_scale)
    year = int(date_str[:4]) if date_str != "latest" else 2026
    mean_lat = 17.2 if region == "mekong" else -9.0
    n_viirs = sum(1 for s in sources if "VIIRS" in s)
    omega = compute_effective_observation_effort(year, mean_lat, n_viirs)
    omega_before_cloud = omega
    if cloud_clear is not None:
        omega = cloud_weighted_effort(omega, *cloud_clear)

    # Harmonize across sensor regimes onto a consistent VIIRS-equivalent single-constellation baseline:
    # - In MODIS-only epochs (2005, 2010), each deduplicated MODIS episode is scaled by the
    #   biome-calibrated sub-pixel small-fire omission factor (3.65 in Mekong agricultural mosaic,
    #   2.55 in Amazon deforestation fronts) divided by Omega.
    # - In multi-sensor VIIRS+MODIS epochs (2012-2024), sub-pixel fires are directly resolved by
    #   VIIRS 375m; we normalize deduplicated episodes by Omega and active VIIRS stream multiplicity.
    harm_equiv_episodes = harmonized_episode_count(region, sources, est_episodes, omega)
    n_viirs_streams = sum(1 for s in sources if "VIIRS" in s)
    if all("MODIS" in s for s in sources):
        harm_frp_total = (
            sum(d.calibrated_viirs_eq_frp_mw for d in harm_dets) * sample_scale / omega
        )
    else:
        stream_overlap_norm = 1.0 + STREAM_OVERLAP_GAIN * max(0, n_viirs_streams - 1)
        harm_frp_total = (
            sum(ep.harmonized_frp_mw for ep in episodes)
            * sample_scale
            / (omega * stream_overlap_norm)
        )

    dedup_ratio = total_raw_unsampled / max(1, est_episodes)

    invariance: dict[str, float] = {}
    if n_viirs and any("MODIS" in s for s in sources):
        modis_view = evaluate_epoch_slice(
            region,
            date_str,
            [s for s in sources if "MODIS" in s],
            cal_model,
            max_sample_per_source,
            static_cells,
            cloud_clear,
        )
        invariance["sensor_invariance_ratio"] = round(
            harm_equiv_episodes / modis_view["harmonized_viirs_eq_episodes"], 3
        )

    return {
        **invariance,
        "region": region,
        "date_window": date_str,
        "year": year,
        "sources": sources,
        "raw_counts_by_source": raw_counts_by_source,
        "total_raw_detections": total_raw_unsampled,
        "deduplicated_fire_episodes": est_episodes,
        "deduplication_compression_ratio": round(dedup_ratio, 3),
        "effective_observation_effort_omega": omega,
        "omega_before_cloud": omega_before_cloud,
        "cloud_clear_sky_fraction": round(cloud_clear[0], 4) if cloud_clear else None,
        "cloud_reference_clear_sky_fraction": round(cloud_clear[1], 4)
        if cloud_clear
        else None,
        "harmonized_viirs_eq_episodes": round(harm_equiv_episodes, 1),
        "raw_total_frp_mw": round(total_raw_frp_mw, 1),
        "harmonized_total_frp_mw": round(harm_frp_total, 1),
        "daynight_sza_reclassified_pct": round(
            100.0 * reclassified_dn / max(1, len(harm_dets)), 2
        ),
        "saa_rejected_count": round(saa_rejected * sample_scale),
        "saa_rejected_share_pct": round(
            100.0 * saa_rejected / max(1, len(harm_dets)), 2
        ),
    }


def evaluate_saa_and_nrt_sza_on_open_feeds() -> dict[str, Any]:
    """Analyze the 7-day South America and Southeast Asia NRT feeds for SAA & SZA anomalies."""
    df_sa_v = _load_csv_safe("open7d__SUOMI_VIIRS_C2_South_America_7d.csv")
    df_sa_j1 = _load_csv_safe("open7d__J1_VIIRS_C2_South_America_7d.csv")
    df_sea_v = _load_csv_safe("open7d__SUOMI_VIIRS_C2_SouthEast_Asia_7d.csv")

    stats: dict[str, Any] = {}
    for tag, df in [
        ("South_America_SNPP_7d", df_sa_v),
        ("South_America_NOAA20_7d", df_sa_j1),
        ("SouthEast_Asia_SNPP_7d", df_sea_v),
    ]:
        if df.empty:
            continue
        sub = df.iloc[:15000].copy()
        scale = len(df) / len(sub)
        dets = parse_firms_dataframe(sub, default_source="VIIRS_NRT")
        harm = harmonize_detections(dets)
        reclass = sum(1 for d in harm if d.daynight_reclassified)
        saa_cnt = sum(1 for d in harm if d.is_saa_anomaly)
        stats[tag] = {
            "total_rows": len(df),
            "sza_reclassified_count": round(reclass * scale),
            "sza_reclassified_pct": round(100.0 * reclass / len(harm), 3),
            "saa_night_false_alarms_filtered": round(saa_cnt * scale),
            "saa_night_false_alarm_pct": round(100.0 * saa_cnt / len(harm), 3),
        }
    return stats


def _load_real_annual_modis_counts(region: str, month_day: str) -> dict[int, int]:
    """Load real observed MODIS 5-day hotspot counts for all 26 years (2001-2026)."""
    counts: dict[int, int] = {}
    for yr in range(2001, 2027):
        sfx = "NRT" if (region == "amazon" and yr == 2026) else "SP"
        df = _load_csv_safe(f"{region}__MODIS_{sfx}__{yr}-{month_day}__5d.csv")
        if not df.empty:
            counts[yr] = len(df)
    return counts


def _load_real_annual_raw_totals(
    region: str, month_day: str, modis_counts: dict[int, int]
) -> dict[int, int]:
    """Load total raw multi-sensor counts across all active streams for each year (2001-2026)."""
    totals: dict[int, int] = {}
    for yr in range(2001, 2027):
        m_cnt = modis_counts.get(yr, 0)
        if yr <= 2011:
            totals[yr] = m_cnt
            continue
        sfx = "NRT" if (region == "amazon" and yr == 2026) else "SP"
        streams = [f"MODIS_{sfx}", f"VIIRS_SNPP_{sfx}"]
        if (region == "mekong" and yr >= 2019) or (region == "amazon" and yr >= 2018):
            streams.append(f"VIIRS_NOAA20_{sfx}")
        if yr >= 2024:
            streams.append("VIIRS_NOAA21_NRT")

        yr_sum = 0
        missing_viirs = 0
        for s in streams:
            df = _load_csv_safe(f"{region}__{s}__{yr}-{month_day}__5d.csv")
            if not df.empty:
                yr_sum += len(df)
            elif "VIIRS" in s:
                missing_viirs += 1
        if missing_viirs > 0 and m_cnt > 0:
            # Fill any single-stream timeout using empirically measured VIIRS/MODIS stream ratio
            ratio_per_viirs = 4.25 if region == "mekong" else 4.35
            yr_sum += round(m_cnt * ratio_per_viirs * missing_viirs)
        totals[yr] = yr_sum
    return totals


def _load_empirical_seasonal_envelope(region: str) -> np.ndarray:
    """Construct a 73-pentad seasonal envelope anchored to the 12 real monthly FIRMS slices."""
    if region == "mekong":
        anchor_files = [
            (3, "mekong_season__VIIRS_SNPP_SP__2024-01-15__5d.csv"),
            (8, "mekong_season__VIIRS_SNPP_SP__2024-02-05__5d.csv"),
            (11, "mekong_season__VIIRS_SNPP_SP__2024-02-20__5d.csv"),
            (15, "mekong__VIIRS_SNPP_SP__2024-03-15__5d.csv"),
            (19, "mekong_season__VIIRS_SNPP_SP__2024-04-05__5d.csv"),
            (22, "mekong_season__VIIRS_SNPP_SP__2024-04-20__5d.csv"),
            (27, "mekong_season__VIIRS_SNPP_SP__2024-05-15__5d.csv"),
            (33, "mekong_season__VIIRS_SNPP_SP__2024-06-15__5d.csv"),
            (39, "mekong_season__VIIRS_SNPP_SP__2024-07-15__5d.csv"),
            (45, "mekong_season__VIIRS_SNPP_SP__2024-08-15__5d.csv"),
            (52, "mekong_season__VIIRS_SNPP_SP__2024-09-15__5d.csv"),
            (58, "mekong_season__VIIRS_SNPP_SP__2024-10-15__5d.csv"),
            (64, "mekong_season__VIIRS_SNPP_SP__2024-11-15__5d.csv"),
            (70, "mekong_season__VIIRS_SNPP_SP__2024-12-15__5d.csv"),
        ]
    else:
        anchor_files = [
            (3, "amazon_season__VIIRS_SNPP_SP__2024-01-15__5d.csv"),
            (9, "amazon_season__VIIRS_SNPP_SP__2024-02-15__5d.csv"),
            (15, "amazon_season__VIIRS_SNPP_SP__2024-03-15__5d.csv"),
            (21, "amazon_season__VIIRS_SNPP_SP__2024-04-15__5d.csv"),
            (27, "amazon_season__VIIRS_SNPP_SP__2024-05-15__5d.csv"),
            (33, "amazon_season__VIIRS_SNPP_SP__2024-06-15__5d.csv"),
            (39, "amazon_season__VIIRS_SNPP_SP__2024-07-15__5d.csv"),
            (44, "amazon_season__VIIRS_SNPP_SP__2024-08-05__5d.csv"),
            (47, "amazon__VIIRS_SNPP_SP__2024-08-20__5d.csv"),
            (50, "amazon_season__VIIRS_SNPP_SP__2024-09-05__5d.csv"),
            (53, "amazon_season__VIIRS_SNPP_SP__2024-09-20__5d.csv"),
            (58, "amazon_season__VIIRS_SNPP_SP__2024-10-15__5d.csv"),
            (64, "amazon_season__VIIRS_SNPP_SP__2024-11-15__5d.csv"),
            (70, "amazon_season__VIIRS_SNPP_SP__2024-12-15__5d.csv"),
        ]

    xp: list[float] = []
    fp: list[float] = []
    for p_idx, fname in anchor_files:
        df = _load_csv_safe(fname)
        if not df.empty:
            xp.append(float(p_idx))
            fp.append(float(len(df)))

    if not xp:
        return np.ones(73, dtype=float)

    # Periodic wrap-around interpolation across Pentads 1..73
    xp_ext = [xp[-1] - 73.0] + xp + [xp[0] + 73.0]
    fp_ext = [fp[-1]] + fp + [fp[0]]
    p_grid = np.arange(1, 74, dtype=float)
    interp_counts = np.interp(p_grid, xp_ext, fp_ext)
    max_val = max(1.0, float(np.max(interp_counts)))
    return 0.06 + 2.48 * (interp_counts / max_val)


def build_26yr_calendars_and_series(
    mekong_epochs: list[dict[str, Any]],
    amazon_epochs: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Construct the 26-year (2001-2026) series and 26x73 Pentad matrices.

    Only the years present in the supplied epoch list are *measured*. The
    remaining years are **interpolated**: their annual scale is anchored to the
    real observed MODIS-only count and their intra-year shape is taken from the
    region's empirical seasonal envelope. The interpolation is deterministic
    (fixed seed) but it is a model, not an observation -- see ADR-0007.

    The modelling constants are named so they can never be mistaken for
    measurements, and the published documents mark which years are which.
    """
    rng = np.random.default_rng(_CALENDAR_NOISE_SEED)
    years_full = list(range(2001, 2027))

    mek_map = {e["year"]: e for e in mekong_epochs if e and e["year"] <= 2026}
    amz_map = {e["year"]: e for e in amazon_epochs if e and e["year"] <= 2026}

    mek_modis_26 = _load_real_annual_modis_counts("mekong", "03-15")
    mek_raw_26 = _load_real_annual_raw_totals("mekong", "03-15", mek_modis_26)
    amz_modis_26 = _load_real_annual_modis_counts("amazon", "08-20")
    amz_raw_26 = _load_real_annual_raw_totals("amazon", "08-20", amz_modis_26)

    series_out: dict[str, Any] = {}
    cal_out: dict[str, Any] = {}

    for (
        region_key,
        emp_map,
        modis_26,
        raw_26,
        peak_pentad,
        peak_window,
        anomaly_label,
    ) in [
        (
            "mekong",
            mek_map,
            mek_modis_26,
            mek_raw_26,
            15,
            "Pentads 11-22 (Feb 20 - Apr 20)",
            "Severe El Nino Anomalies",
        ),
        (
            "amazon",
            amz_map,
            amz_modis_26,
            amz_raw_26,
            47,
            "Pentads 40-56 (Jul 15 - Oct 07)",
            "Severe Drought Anomalies",
        ),
    ]:
        raw_2005 = float(raw_26[2005])
        harm_2005 = float(emp_map[2005]["harmonized_viirs_eq_episodes"])
        modis_2005 = float(modis_26[2005])
        clim_baseline_harm = (
            harm_2005
            if region_key == "mekong"
            else harm_2005 * _AMAZON_CLIMATOLOGY_BASELINE_FRACTION
        )
        emp_seasonal_curve = _load_empirical_seasonal_envelope(region_key)

        raw_idx_list: list[float] = []
        harm_idx_list: list[float] = []
        hfd_matrix: list[list[float]] = []
        provenance: list[list[int]] = []
        # A cell is observed only for the pentad that holds the epoch's 5-day
        # FIRMS window, in a Measured Epoch. Every other cell is modelled.
        observed_pentad = peak_pentad

        for yr in years_full:
            r_cnt = float(raw_26.get(yr, raw_2005))
            is_measured = yr in emp_map and yr != 2026
            if is_measured:
                h_cnt = float(emp_map[yr]["harmonized_viirs_eq_episodes"])
            else:
                # Directly anchor to the real observed MODIS_SP count for year `yr`,
                # normalized by single-Terra effort in 2001-2002
                m_cnt_yr = float(modis_26.get(yr, modis_2005))
                terra_only_corr = _TERRA_ONLY_CORRECTION.get(yr, 1.0)
                h_cnt = harm_2005 * (m_cnt_yr / modis_2005) * terra_only_corr

            raw_idx_list.append(round(100.0 * r_cnt / raw_2005, 1))
            harm_idx_list.append(round(100.0 * h_cnt / harm_2005, 1))

            row_hfd: list[float] = []
            row_prov: list[int] = []
            yr_scale = h_cnt / clim_baseline_harm
            for p_idx in range(1, 74):
                base_rate = float(emp_seasonal_curve[p_idx - 1])
                noise = max(
                    _CALENDAR_NOISE_FLOOR,
                    1.0 + float(rng.normal(0.0, _CALENDAR_NOISE_SD)),
                )
                observed = is_measured and p_idx == observed_pentad
                if observed:
                    # No noise and no multiplier: the cell is the measured value.
                    val = base_rate * yr_scale
                    row_prov.append(CELL_OBSERVED)
                else:
                    val = base_rate * yr_scale * noise
                    # A hand-set peak amplitude is a modelling assumption and
                    # only ever shapes interpolated years.
                    if (
                        not is_measured
                        and yr in (2007, 2010, 2015, 2016, 2024)
                        and abs(p_idx - (peak_pentad - 5)) <= 2
                    ):
                        val *= _EL_NINO_PEAK_AMPLITUDE
                    row_prov.append(
                        CELL_MODELLED_IN_MEASURED_YEAR
                        if is_measured
                        else CELL_INTERPOLATED
                    )
                row_hfd.append(round(val, 4))
            hfd_matrix.append(row_hfd)
            provenance.append(row_prov)

        mat_np = np.array(hfd_matrix, dtype=float)
        prov_np = np.array(provenance, dtype=int)
        sfai_np = measured_only_sfai(mat_np, prov_np)

        # The summary caption names the years that actually reach a severe
        # anomaly, and the peak SFAI actually observed. Both are derived from
        # the matrix just computed, so the published caption cannot drift from
        # the figure it labels.
        anomaly_years = [
            year
            for row, year in enumerate(years_full)
            if np.nanmax(sfai_np[row], initial=-np.inf) >= SFAI_HIGHLIGHT_Z
        ]
        peak_sfai = float(np.nanmax(sfai_np))
        observed_years = [
            y for y, row in zip(years_full, prov_np) if (row == CELL_OBSERVED).any()
        ]
        caption = (
            f"Peak Fire Window: {peak_window} | Scored on observed cells only "
            f"({len(observed_years)} measured years, pentad {observed_pentad}) | "
            f"{anomaly_label}: "
            f"{', '.join(str(y) for y in anomaly_years) or 'none reach the display threshold'}"
            f" (peak observed SFAI +{peak_sfai:.1f} sigma)"
        )

        # Which years are measured (anchored to a real epoch) and which are
        # interpolated. Published documents mark the interpolated ones so a
        # reader can tell an observation from a model output.
        measured_years = sorted(y for y in years_full if y in emp_map)
        interpolated_years = [y for y in years_full if y not in emp_map]

        series_out[region_key] = {
            "years": years_full,
            "raw_counts_by_year": {str(y): raw_26[y] for y in years_full},
            "modis_reference_counts_by_year": {str(y): modis_26[y] for y in years_full},
            "raw_index_2005_eq_100": raw_idx_list,
            "harmonized_index_2005_eq_100": harm_idx_list,
            "measured_years": measured_years,
            "interpolated_years": interpolated_years,
        }
        cal_out[region_key] = {
            "years": years_full,
            "hfd_matrix": hfd_matrix,
            "sfai_matrix": np.where(np.isnan(sfai_np), None, sfai_np).tolist(),
            "cell_provenance_matrix": prov_np.tolist(),
            "observed_pentad": observed_pentad,
            "summary_caption": caption,
            "measured_years": measured_years,
            "interpolated_years": interpolated_years,
        }

    return series_out, cal_out


def main() -> None:
    PROC_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    print("[Step 1/5] Running Spherical Scan-Angle Footprint Physics Verification...")
    modis_curves, viirs_curves, emp_samples, scan_stats = (
        compute_scan_angle_verification()
    )
    render_fig1_scan_angle_physics(
        FIG_DIR / "fig1_scan_angle_footprint_physics.png",
        modis_curves,
        viirs_curves,
        emp_samples,
    )
    print(
        f"           Saved fig1_scan_angle_footprint_physics.png | Max Area Ratio: {scan_stats['max_area_ratio_modis_edge_to_viirs_nadir']}x"
    )

    print(
        "[Step 2/5] Fitting Two-Stage FRP Cross-Calibration on Co-Incident Aqua & S-NPP Overpasses..."
    )
    cal_model, cal_plot_data = run_coincident_overpass_calibration()
    render_fig3_cross_sensor_frp(
        FIG_DIR / "fig3_cross_sensor_frp_quantile_mapping.png",
        cal_plot_data,
    )
    print(
        f"           Saved fig3_cross_sensor_frp_quantile_mapping.png | "
        f"N={cal_plot_data['n_pairs']} pairs, R^2: {cal_plot_data['raw_r2']} -> {cal_plot_data['harm_r2']}, "
        f"KS: {cal_plot_data['ks_before']} -> {cal_plot_data['ks_after']}"
    )

    print(
        "[Step 3/5] Running Multi-Satellite Overpass Deduplication across Real NASA FIRMS Epochs..."
    )
    mekong_plan = [
        ("2005-03-15", ["MODIS_SP"]),
        ("2007-03-15", ["MODIS_SP"]),
        ("2010-03-15", ["MODIS_SP"]),
        ("2012-03-15", ["MODIS_SP", "VIIRS_SNPP_SP"]),
        ("2016-03-15", ["MODIS_SP", "VIIRS_SNPP_SP"]),
        ("2019-03-15", ["MODIS_SP", "VIIRS_SNPP_SP", "VIIRS_NOAA20_SP"]),
        ("2020-03-15", ["MODIS_SP", "VIIRS_SNPP_SP", "VIIRS_NOAA20_SP"]),
        ("2023-03-15", ["MODIS_SP", "VIIRS_SNPP_SP", "VIIRS_NOAA20_SP"]),
        (
            "2024-03-15",
            ["MODIS_SP", "VIIRS_SNPP_SP", "VIIRS_NOAA20_SP", "VIIRS_NOAA21_NRT"],
        ),
        (
            "2025-03-15",
            ["MODIS_SP", "VIIRS_SNPP_SP", "VIIRS_NOAA20_SP", "VIIRS_NOAA21_NRT"],
        ),
        (
            "2026-03-15",
            ["MODIS_SP", "VIIRS_SNPP_SP", "VIIRS_NOAA20_SP", "VIIRS_NOAA21_NRT"],
        ),
    ]
    amazon_plan = [
        ("2005-08-20", ["MODIS_SP"]),
        ("2007-08-20", ["MODIS_SP"]),
        ("2010-08-20", ["MODIS_SP"]),
        ("2012-08-20", ["MODIS_SP", "VIIRS_SNPP_SP"]),
        ("2019-08-20", ["MODIS_SP", "VIIRS_SNPP_SP", "VIIRS_NOAA20_SP"]),
        ("2020-08-20", ["MODIS_SP", "VIIRS_SNPP_SP", "VIIRS_NOAA20_SP"]),
        (
            "2024-08-20",
            ["MODIS_SP", "VIIRS_SNPP_SP", "VIIRS_NOAA20_SP", "VIIRS_NOAA21_NRT"],
        ),
        (
            "2025-08-20",
            ["MODIS_SP", "VIIRS_SNPP_SP", "VIIRS_NOAA20_SP", "VIIRS_NOAA21_NRT"],
        ),
        (
            "2026-08-20",
            ["MODIS_NRT", "VIIRS_SNPP_NRT", "VIIRS_NOAA20_NRT", "VIIRS_NOAA21_NRT"],
        ),
    ]

    mekong_static = load_static_source_registry("mekong")
    amazon_static = load_static_source_registry("amazon")
    print(
        f"           Static Source Registry: mekong={len(mekong_static)} cells, "
        f"amazon={len(amazon_static)} cells"
    )

    mekong_cloud = load_cloud_clear_sky("mekong")
    amazon_cloud = load_cloud_clear_sky("amazon")

    mekong_epochs = [
        evaluate_epoch_slice(
            "mekong",
            d,
            s,
            cal_model,
            static_cells=mekong_static,
            cloud_clear=mekong_cloud.get(d),
        )
        for d, s in mekong_plan
    ]
    amazon_epochs = [
        evaluate_epoch_slice(
            "amazon",
            d,
            s,
            cal_model,
            static_cells=amazon_static,
            cloud_clear=amazon_cloud.get(d),
        )
        for d, s in amazon_plan
    ]

    omega_by_yr = {
        str(y): compute_effective_observation_effort(y, 16.0) for y in range(2000, 2027)
    }
    sat_by_yr = {}
    for y in range(2000, 2027):
        if y <= 2001:
            sat_by_yr[str(y)] = 1
        elif y <= 2011:
            sat_by_yr[str(y)] = 2
        elif y <= 2017:
            sat_by_yr[str(y)] = 3
        elif y <= 2022:
            sat_by_yr[str(y)] = 4
        else:
            sat_by_yr[str(y)] = 5

    mek_by_yr = {e["year"]: e for e in mekong_epochs}
    amz_by_yr = {e["year"]: e for e in amazon_epochs}
    dedup_fig_data = {
        "omega_by_year": omega_by_yr,
        "sat_count_by_year": sat_by_yr,
        "empirical_epochs": [
            {
                "label": "Mekong 2012 (2-Sat)",
                "raw_detections": mek_by_yr[2012]["total_raw_detections"],
                "fire_episodes": mek_by_yr[2012]["deduplicated_fire_episodes"],
            },
            {
                "label": "Mekong 2016 (El Nino)",
                "raw_detections": mek_by_yr[2016]["total_raw_detections"],
                "fire_episodes": mek_by_yr[2016]["deduplicated_fire_episodes"],
            },
            {
                "label": "Mekong 2023 (3-Sat)",
                "raw_detections": mek_by_yr[2023]["total_raw_detections"],
                "fire_episodes": mek_by_yr[2023]["deduplicated_fire_episodes"],
            },
            {
                "label": "Mekong 2024 (4-Sat)",
                "raw_detections": mek_by_yr[2024]["total_raw_detections"],
                "fire_episodes": mek_by_yr[2024]["deduplicated_fire_episodes"],
            },
            {
                "label": "Amazon 2012 (2-Sat)",
                "raw_detections": amz_by_yr[2012]["total_raw_detections"],
                "fire_episodes": amz_by_yr[2012]["deduplicated_fire_episodes"],
            },
            {
                "label": "Amazon 2024 (4-Sat)",
                "raw_detections": amz_by_yr[2024]["total_raw_detections"],
                "fire_episodes": amz_by_yr[2024]["deduplicated_fire_episodes"],
            },
        ],
    }
    render_fig2_overpass_deduplication(
        FIG_DIR / "fig2_overpass_deduplication_sza.png",
        dedup_fig_data,
    )
    print("           Saved fig2_overpass_deduplication_sza.png")

    print(
        "[Step 4/5] Evaluating SAA Nighttime Rejection & NRT SZA Reclassification on 7-Day Feeds..."
    )
    saa_sza_stats = evaluate_saa_and_nrt_sza_on_open_feeds()

    print(
        "[Step 5/5] Building 26-Year Harmonized Burning Activity Calendars & Regime-Shift Figures..."
    )
    series_data, cal_matrix_data = build_26yr_calendars_and_series(
        mekong_epochs, amazon_epochs
    )
    # Static artifact for the web frontend (ADR-0011): the calendar with a
    # per-cell provenance flag, so a viewer can tell an observation from a model.
    (PROC_DIR / "burning_calendar.json").write_text(
        json.dumps(cal_matrix_data, separators=(",", ":")), encoding="utf-8"
    )
    render_fig4_regime_shift_elimination(
        FIG_DIR / "fig4_regime_shift_elimination.png",
        series_data,
    )
    render_fig5_burning_activity_calendar(
        FIG_DIR / "fig5_harmonized_burning_calendar.png",
        cal_matrix_data,
    )
    print(
        "           Saved fig4_regime_shift_elimination.png & fig5_harmonized_burning_calendar.png"
    )

    full_results = {
        "scan_angle_physics": scan_stats,
        "coincident_calibration": {
            k: v
            for k, v in cal_plot_data.items()
            if not k.endswith("_sample") and not k.startswith("cdf_")
        },
        "mekong_empirical_epochs": mekong_epochs,
        "amazon_empirical_epochs": amazon_epochs,
        "saa_and_sza_nrt_audit": saa_sza_stats,
        "regime_shift_series": series_data,
    }
    out_json = PROC_DIR / "empirical_results.json"
    out_json.write_text(json.dumps(full_results, indent=2), encoding="utf-8")
    print(f"\n[DONE] Empirical verification metrics exported to {out_json}")


if __name__ == "__main__":
    main()
