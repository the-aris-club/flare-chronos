"""Progressive NASA FIRMS Data Ingestion Script.

Fetches multi-epoch historical and near-real-time Thermal Detections for:
1. Case Study 1: Mekong Subregion & Vietnam (BBOX_MEKONG)
2. Case Study 2: Southern Amazon Arc of Deforestation (BBOX_AMAZON)
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


def build_epoch_query_plan() -> list[FIRMSQuerySpec]:
    """Construct a curated, high-signal multi-epoch query plan across sensor generations."""
    specs: list[FIRMSQuerySpec] = []

    # 1. Mekong / Vietnam Peak Dry-Season Windows (March 15 - March 19, 5-day pentad)
    mekong_epochs = [
        ("2005-03-15", ["MODIS_SP"]),
        ("2010-03-15", ["MODIS_SP"]),
        ("2012-03-15", ["MODIS_SP", "VIIRS_SNPP_SP"]),
        ("2016-03-15", ["MODIS_SP", "VIIRS_SNPP_SP"]),  # Severe El Nino
        ("2020-03-15", ["MODIS_SP", "VIIRS_SNPP_SP", "VIIRS_NOAA20_SP"]),
        ("2023-03-15", ["MODIS_SP", "VIIRS_SNPP_SP", "VIIRS_NOAA20_SP"]),
        (
            "2024-03-15",
            ["MODIS_SP", "VIIRS_SNPP_SP", "VIIRS_NOAA20_SP", "VIIRS_NOAA21_NRT"],
        ),
        (
            "2025-03-15",
            ["MODIS_NRT", "VIIRS_SNPP_NRT", "VIIRS_NOAA20_NRT", "VIIRS_NOAA21_NRT"],
        ),
    ]
    for start_date, sources in mekong_epochs:
        for src in sources:
            specs.append(
                FIRMSQuerySpec(
                    region_tag="mekong",
                    source=src,
                    bbox=BBOX_MEKONG,
                    day_range=5,
                    start_date=start_date,
                )
            )

    # Latest NRT 5-day window for Mekong across all 4 sensor streams
    for src in ["MODIS_NRT", "VIIRS_SNPP_NRT", "VIIRS_NOAA20_NRT", "VIIRS_NOAA21_NRT"]:
        specs.append(
            FIRMSQuerySpec(
                region_tag="mekong",
                source=src,
                bbox=BBOX_MEKONG,
                day_range=5,
                start_date=None,
            )
        )

    # 2. Amazon Peak Burning Season Windows (August 20 - August 24, 5-day pentad)
    amazon_epochs = [
        ("2005-08-20", ["MODIS_SP"]),
        ("2010-08-20", ["MODIS_SP"]),
        ("2012-08-20", ["MODIS_SP", "VIIRS_SNPP_SP"]),
        ("2019-08-20", ["MODIS_SP", "VIIRS_SNPP_SP"]),
        ("2020-08-20", ["MODIS_SP", "VIIRS_SNPP_SP", "VIIRS_NOAA20_SP"]),
        (
            "2024-08-20",
            ["MODIS_SP", "VIIRS_SNPP_SP", "VIIRS_NOAA20_SP", "VIIRS_NOAA21_NRT"],
        ),
    ]
    for start_date, sources in amazon_epochs:
        for src in sources:
            specs.append(
                FIRMSQuerySpec(
                    region_tag="amazon",
                    source=src,
                    bbox=BBOX_AMAZON,
                    day_range=5,
                    start_date=start_date,
                )
            )

    # Latest NRT 5-day window for Amazon across all 4 sensor streams
    for src in ["MODIS_NRT", "VIIRS_SNPP_NRT", "VIIRS_NOAA20_NRT", "VIIRS_NOAA21_NRT"]:
        specs.append(
            FIRMSQuerySpec(
                region_tag="amazon",
                source=src,
                bbox=BBOX_AMAZON,
                day_range=5,
                start_date=None,
            )
        )

    return specs


def main() -> None:
    client = FIRMSClient(min_request_interval_sec=0.4)
    print("[1/3] Checking NASA FIRMS Data Availability table via MAP_KEY...")
    try:
        avail_df = client.check_data_availability()
        print(f"      Retrieved {len(avail_df)} sensor availability records:")
        for _, row in avail_df.iterrows():
            print(
                f"      - {row.get('data_id', 'unknown')}: {row.get('min_date', '')} -> {row.get('max_date', '')}"
            )
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] Could not fetch data_availability: {exc}")

    print("\n[2/3] Fetching multi-epoch historical & NRT slices for Mekong & Amazon...")
    specs = build_epoch_query_plan()
    summary = client.fetch_batch_progressively(specs, pause_between_specs_sec=0.35)

    print("\n[2.5/3] Fetching NASA FIRMS Open 7-Day Regional Multi-Sensor Feeds...")
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
