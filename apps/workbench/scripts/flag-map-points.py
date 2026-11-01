"""Flag and sample the raw FIRMS detections used by the Workbench map.

The map needs the same physics filters the harmonization core applies:
night-time SZA, SAA cosmic-ray false alarms, static heat sources and the
60-minute overpass de-duplication.  Re-implementing those rules in the Bun
build script would let the two surfaces drift, so this step calls the core and
writes a compact point list that ``build-map-data.mjs`` projects to SVG.

Output: apps/workbench/.cache/map-points.json (git-ignored build input).

Run from apps/workbench:
  ../../.venv/bin/python scripts/flag-map-points.py
"""

from __future__ import annotations

import csv
import json
import math
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "packages" / "harmonization-core" / "src"
sys.path.insert(0, str(CORE))

from flare_chronos_core import (
    ProcessingMode,
    SatellitePlatform,
    SensorType,
    ThermalDetection,
    compute_solar_zenith_angle,
    compute_unified_detection_probability,
    invert_modis_scan_angle,
    invert_viirs_scan_angle,
    latlon_to_h3,
)
from flare_chronos_core.deduplication import haversine_km

RAW = ROOT / "data" / "raw"
EMPIRICAL = ROOT / "data" / "processed" / "empirical_results.json"
OUT = Path(__file__).resolve().parents[1] / ".cache" / "map-points.json"

MAX_PER_SENSOR = 520
MAX_POINTS = 2600
SZA_NIGHT = 85.0

FLAG_SZA = 1
FLAG_SAA = 2
FLAG_STATIC = 4
FLAG_DUP = 8

PLATFORMS = {
    "terra": SatellitePlatform.TERRA,
    "aqua": SatellitePlatform.AQUA,
    "suomi-npp": SatellitePlatform.SNPP,
    "npp": SatellitePlatform.SNPP,
    "noaa-20": SatellitePlatform.NOAA20,
    "noaa-21": SatellitePlatform.NOAA21,
}


def platform_of(name: str) -> SatellitePlatform:
    return PLATFORMS.get((name or "").strip().lower(), SatellitePlatform.TERRA)


def mode_of(filename: str) -> ProcessingMode:
    return ProcessingMode.NRT if "NRT" in filename else ProcessingMode.STANDARD


def read_rows(path: Path) -> list[dict]:
    """Parse one FIRMS slice into the fields the map and physics need."""
    rows: list[dict] = []
    is_viirs = "VIIRS" in path.name
    sensor = SensorType.VIIRS if is_viirs else SensorType.MODIS
    with path.open(newline="", encoding="utf-8") as handle:
        for index, raw in enumerate(csv.DictReader(handle)):
            try:
                lat = float(raw["latitude"])
                lon = float(raw["longitude"])
                stamp = raw["acq_time"].strip().zfill(4)
                when = datetime.strptime(raw["acq_date"], "%Y-%m-%d").replace(
                    hour=int(stamp[:2]), minute=int(stamp[2:])
                )
                frp = float(raw.get("frp") or 0.0)
                scan = float(raw.get("scan") or 1.0)
                track = float(raw.get("track") or 1.0)
                platform = (raw.get("satellite") or "").strip()
                daynight_raw = (raw.get("daynight") or "").strip().upper()
                if sensor == SensorType.MODIS:
                    angle = math.degrees(invert_modis_scan_angle(scan))
                else:
                    angle, _ = invert_viirs_scan_angle(scan, track)
                    angle = math.degrees(angle)
                t4 = float(raw.get("bright_ti4") or raw.get("brightness") or 0.0)
                t5 = float(raw.get("bright_ti5") or raw.get("bright_t31") or 0.0)
            except (KeyError, TypeError, ValueError):
                continue

            sza = compute_solar_zenith_angle(lat, lon, when)
            daynight = "D" if sza < SZA_NIGHT else "N"
            confidence = (raw.get("confidence") or "50").strip().lower()
            detection = ThermalDetection(
                detection_id=f"{path.stem}:{index}",
                latitude=lat,
                longitude=lon,
                acq_datetime_utc=when,
                sensor=sensor,
                platform=platform_of(raw.get("satellite", "")),
                processing_mode=mode_of(path.name),
                scan_km=scan,
                track_km=track,
                bright_t4_k=t4,
                bright_t5_k=t5,
                frp_mw=frp,
                raw_confidence=confidence,
                raw_daynight=daynight,
                fire_type=int(raw["type"]) if raw.get("type", "").isdigit() else None,
            )
            probability, is_saa = compute_unified_detection_probability(
                detection, daynight
            )
            fire_type = detection.fire_type
            flags = 0
            if is_saa:
                flags |= FLAG_SAA
            elif sza >= SZA_NIGHT:
                flags |= FLAG_SZA
            if fire_type in (1, 2, 3):
                flags |= FLAG_STATIC

            rows.append(
                {
                    "lon": lon,
                    "lat": lat,
                    "when": when,
                    "cell": latlon_to_h3(lat, lon, 8),
                    "sensor": "v" if is_viirs else "m",
                    "flags": flags,
                    "valid": not is_saa
                    and fire_type not in (1, 2, 3)
                    and probability >= 0.2,
                    "scan": scan,
                    "track": track,
                    "angle": angle,
                    "platform": platform,
                    "daynight": daynight_raw or ("N" if sza >= SZA_NIGHT else "D"),
                    "file": path.name,
                    "index": index,
                }
            )
    return rows


def mark_duplicates(rows: list[dict]) -> None:
    """Mark every overpass detection after the first in a 60-minute cluster."""
    valid = sorted((row for row in rows if row["valid"]), key=lambda row: row["when"])
    buckets: dict[tuple[int, int], list[list[dict]]] = {}
    clusters: list[list[dict]] = []

    for row in valid:
        bucket = (math.floor(row["lat"] * 20), math.floor(row["lon"] * 20))
        match = None
        for dlat in (-1, 0, 1):
            if match is not None:
                break
            for dlon in (-1, 0, 1):
                for cluster in buckets.get((bucket[0] + dlat, bucket[1] + dlon), []):
                    anchor = cluster[0]
                    if (row["when"] - anchor["when"]).total_seconds() / 60.0 > 60:
                        continue
                    if (
                        row["cell"] == anchor["cell"]
                        or haversine_km(
                            row["lat"], row["lon"], anchor["lat"], anchor["lon"]
                        )
                        <= 1.35
                    ):
                        match = cluster
                        break
                if match is not None:
                    break
        if match is None:
            cluster = [row]
            clusters.append(cluster)
            buckets.setdefault(bucket, []).append(cluster)
        else:
            match.append(row)
            row["flags"] |= FLAG_DUP


def sample(rows: list[dict]) -> list[dict]:
    """Keep the visible density while retaining every static source."""
    by_file: dict[str, list[dict]] = {}
    for row in rows:
        by_file.setdefault(row["file"], []).append(row)

    picked: dict[tuple[str, int], dict] = {}
    for sensor_rows in by_file.values():
        if not sensor_rows:
            continue
        step = max(1, math.ceil(len(sensor_rows) / MAX_PER_SENSOR))
        for row in sensor_rows[::step]:
            picked[(row["file"], row["index"])] = row
    for row in rows:
        if row["flags"] & FLAG_STATIC:
            picked[(row["file"], row["index"])] = row

    kept = list(picked.values())
    if len(kept) > MAX_POINTS:
        static = [row for row in kept if row["flags"] & FLAG_STATIC]
        rest = [row for row in kept if not row["flags"] & FLAG_STATIC]
        step = max(1, math.ceil(len(rest) / max(1, MAX_POINTS - len(static))))
        kept = static + rest[::step]
    kept.sort(key=lambda row: (row["sensor"], row["lon"], row["lat"]))
    return kept


def main() -> None:
    empirical = json.loads(EMPIRICAL.read_text())
    output: dict = {"regions": {}}

    for region in ("mekong", "amazon"):
        epochs = empirical[f"{region}_empirical_epochs"]
        region_out: dict[str, dict] = {}
        for epoch in epochs:
            year = epoch["year"]
            window = epoch["date_window"]
            files = sorted(
                path
                for path in RAW.glob(f"{region}__*__{window}__5d.csv")
                if "_season" not in path.name
            )
            rows: list[dict] = []
            for path in files:
                rows.extend(read_rows(path))
            if not rows:
                continue
            mark_duplicates(rows)
            points = sample(rows)
            region_out[str(year)] = {
                "counts": {
                    "total": len(rows),
                    "sza": sum(1 for row in rows if row["flags"] & FLAG_SZA),
                    "saa": sum(1 for row in rows if row["flags"] & FLAG_SAA),
                    "static": sum(1 for row in rows if row["flags"] & FLAG_STATIC),
                    "dup": sum(1 for row in rows if row["flags"] & FLAG_DUP),
                    "sampled": len(points),
                },
                "points": [
                    [
                        round(row["lon"], 4),
                        round(row["lat"], 4),
                        row["sensor"],
                        row["flags"],
                        round(row["scan"], 2),
                        round(row["track"], 2),
                        round(row["angle"], 1),
                        row["platform"],
                        row["daynight"],
                    ]
                    for row in points
                ],
            }
            print(
                f"{region} {year}: {len(rows)} rows · {len(points)} points · "
                f"{region_out[str(year)]['counts']}"
            )
        output["regions"][region] = region_out

    output["saaZone"] = {"lon": -45, "lat": -25, "rx": 40, "ry": 18}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, separators=(",", ":")))
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
