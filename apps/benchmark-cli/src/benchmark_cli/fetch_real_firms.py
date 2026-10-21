"""Complete 26-Year (2001-2026) NASA FIRMS Data Ingestion Script.

Fetches 100% real multi-sensor historical (SP) and near-real-time (NRT) Thermal Detections for:
1. Case Study 1: Mekong Subregion & Vietnam (BBOX_MEKONG) across all 26 years (2001-2026)
   + Intra-annual 12-month seasonal phenology slices (Pentads across Jan-Dec)
2. Case Study 2: Southern Amazon Arc of Deforestation (BBOX_AMAZON) across all 26 years (2001-2026)
   + Intra-annual 12-month seasonal phenology slices (Pentads across Jan-Dec)
3. Direct 7-Day Regional Open Feeds for South America & Southeast Asia (SAA & NRT SZA verification)

Respects the 5,000 transactions / 10-minute rate limit and caches all CSVs in data/raw/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure monorepo packages are importable
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "packages" / "firms-ingestion" / "src"))

from firms_ingestion import BBOX_AMAZON, BBOX_MEKONG, FIRMSClient, FIRMSQuerySpec


def get_mekong_march_sources(year: int) -> list[str]:
    """Return all active NASA FIRMS sensor streams for March 15-19 of `year`."""
    if year <= 2011:
        return ["MODIS_SP"]
    if year <= 2018:
        # VIIRS_NOAA20_SP starts 2018-04-01 (after March 2018)
        return ["MODIS_SP", "VIIRS_SNPP_SP"]
    if year <= 2023:
        return ["MODIS_SP", "VIIRS_SNPP_SP", "VIIRS_NOAA20_SP"]
    # 2024, 2025, 2026 (March 2026 is before 2026-06-30 SP cutoff; NOAA21_NRT starts 2024-01-17)
    return ["MODIS_SP", "VIIRS_SNPP_SP", "VIIRS_NOAA20_SP", "VIIRS_NOAA21_NRT"]


def get_amazon_august_sources(year: int) -> list[str]:
    """Return all active NASA FIRMS sensor streams for August 20-24 of `year`."""
    if year <= 2011:
        return ["MODIS_SP"]
    if year <= 2017:
        return ["MODIS_SP", "VIIRS_SNPP_SP"]
    if year <= 2023:
        # August 2018 is after 2018-04-01 when VIIRS_NOAA20_SP began
        return ["MODIS_SP", "VIIRS_SNPP_SP", "VIIRS_NOAA20_SP"]
    if year in (2024, 2025):
        return ["MODIS_SP", "VIIRS_SNPP_SP", "VIIRS_NOAA20_SP", "VIIRS_NOAA21_NRT"]
    # August 2026 is after 2026-07-01 / 2026-08-01 NRT cutover
    return ["MODIS_NRT", "VIIRS_SNPP_NRT", "VIIRS_NOAA20_NRT", "VIIRS_NOAA21_NRT"]


def build_epoch_query_plan() -> list[FIRMSQuerySpec]:
    """Construct a complete 26-year (2001-2026) + 12-month intra-annual query plan."""
    specs: list[FIRMSQuerySpec] = []

    # 1. All 26 Consecutive Years (2001-2026) for Mekong / Vietnam Peak Window (March 15-19)
    for yr in range(2001, 2027):
        start_date = f"{yr}-03-15"
        for src in get_mekong_march_sources(yr):
            specs.append(
                FIRMSQuerySpec(
                    region_tag="mekong",
                    source=src,
                    bbox=BBOX_MEKONG,
                    day_range=5,
                    start_date=start_date,
                )
            )

    # 2. All 26 Consecutive Years (2001-2026) for Amazon Peak Window (August 20-24)
    for yr in range(2001, 2027):
        start_date = f"{yr}-08-20"
        for src in get_amazon_august_sources(yr):
            specs.append(
                FIRMSQuerySpec(
                    region_tag="amazon",
                    source=src,
                    bbox=BBOX_AMAZON,
                    day_range=5,
                    start_date=start_date,
                )
            )

    # 3. Intra-Annual Seasonal Phenology Slices (12 Months across the year + early Feb El Nino onset)
    mekong_seasonal_dates = [
        "2024-01-15",
        "2024-02-05",
        "2024-02-20",
        "2024-04-05",
        "2024-04-20",
        "2024-05-15",
        "2024-06-15",
        "2024-07-15",
        "2024-08-15",
        "2024-09-15",
        "2024-10-15",
        "2024-11-15",
        "2024-12-15",
        # Early February out-of-season El Nino onset comparison (2010 & 2016 vs normal)
        "2010-02-05",
        "2016-02-05",
    ]
    for d_str in mekong_seasonal_dates:
        yr = int(d_str[:4])
        src = "MODIS_SP" if yr < 2012 else "VIIRS_SNPP_SP"
        specs.append(
            FIRMSQuerySpec(
                region_tag="mekong_season",
                source=src,
                bbox=BBOX_MEKONG,
                day_range=5,
                start_date=d_str,
            )
        )

    amazon_seasonal_dates = [
        "2024-01-15",
        "2024-02-15",
        "2024-03-15",
        "2024-04-15",
        "2024-05-15",
        "2024-06-15",
        "2024-07-15",
        "2024-08-05",
        "2024-09-05",
        "2024-09-20",
        "2024-10-15",
        "2024-11-15",
        "2024-12-15",
    ]
    for d_str in amazon_seasonal_dates:
        specs.append(
            FIRMSQuerySpec(
                region_tag="amazon_season",
                source="VIIRS_SNPP_SP",
                bbox=BBOX_AMAZON,
                day_range=5,
                start_date=d_str,
            )
        )

    # 4. Latest NRT 5-day window for Mekong & Amazon across all 4 sensor streams
    for reg, bbox in [("mekong", BBOX_MEKONG), ("amazon", BBOX_AMAZON)]:
        for src in [
            "MODIS_NRT",
            "VIIRS_SNPP_NRT",
            "VIIRS_NOAA20_NRT",
            "VIIRS_NOAA21_NRT",
        ]:
            specs.append(
                FIRMSQuerySpec(
                    region_tag=reg,
                    source=src,
                    bbox=bbox,
                    day_range=5,
                    start_date=None,
                )
            )

    return specs


def main() -> None:
    client = FIRMSClient(min_request_interval_sec=0.35, timeout_sec=75)
    print("[1/3] Checking NASA FIRMS Data Availability table via MAP_KEY...")
    try:
        avail_df = client.check_data_availability()
        print(f"      Retrieved {len(avail_df)} sensor availability records.")
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] Could not fetch data_availability: {exc}")

    specs = build_epoch_query_plan()
    print(
        f"\n[2/3] Fetching {len(specs)} complete 26-year historical, seasonal & NRT slices..."
    )
    summary = client.fetch_batch_progressively(specs, pause_between_specs_sec=0.25)

    print("\n[2.5/3] Verifying NASA FIRMS Open 7-Day Regional Multi-Sensor Feeds...")
    open_feeds = [
        ("modis-c6.1", "MODIS_C6_1_SouthEast_Asia_7d.csv"),
        ("suomi-npp-viirs-c2", "SUOMI_VIIRS_C2_SouthEast_Asia_7d.csv"),
        ("noaa-20-viirs-c2", "J1_VIIRS_C2_SouthEast_Asia_7d.csv"),
        ("modis-c6.1", "MODIS_C6_1_South_America_7d.csv"),
        ("suomi-npp-viirs-c2", "SUOMI_VIIRS_C2_South_America_7d.csv"),
        ("noaa-20-viirs-c2", "J1_VIIRS_C2_South_America_7d.csv"),
    ]
    for sensor_path, fname in open_feeds:
        try:
            df_open = client.fetch_open_7d_feed(sensor_path, fname)
            summary[f"open7d__{fname}"] = len(df_open)
            print(f"      - open7d__{fname}: {len(df_open):,} rows")
        except Exception as exc:  # noqa: BLE001
            summary[f"open7d__{fname}"] = -1
            print(f"      [WARN] open7d__{fname}: {exc}")

    total_rows = sum(v for v in summary.values() if v > 0)
    manifest_path = ROOT / "data" / "raw" / "fetch_manifest.json"
    manifest_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(
        f"\n[3/3] Completed progressive fetch: {len(summary)} slices, {total_rows:,} total real Thermal Detections cached."
    )
    print(f"      Manifest written to {manifest_path}")


if __name__ == "__main__":
    main()
