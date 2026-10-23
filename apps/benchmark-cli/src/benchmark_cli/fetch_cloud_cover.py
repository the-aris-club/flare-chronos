"""Fetch ERA5 cloud cover for each measured epoch window.

The cloud fraction comes from ERA5 total cloud cover, read through the open
Open-Meteo archive API (no key). It is a reanalysis field, not an observation at
the instant a satellite passed, so it weights *effort*; it never decides whether
a given detection was real. The result is a small pinned file.

For each epoch window the value is the mean over a 3x3 grid of points across the
region's bounding box and over the hours within two hours of the local 13:30 or
01:30 solar overpass, the plane shared by Aqua and the Suomi-NPP / NOAA VIIRS
satellites.
"""

from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RESULTS = ROOT / "data" / "processed" / "empirical_results.json"
OUT = ROOT / "data" / "cloud" / "era5_cloud_cover.json"
API = "https://archive-api.open-meteo.com/v1/archive"
# min lon, min lat, max lon, max lat; mirrors firms_ingestion.BBOX_*
BBOX = {
    "mekong": (100.0, 11.0, 109.5, 23.5),
    "amazon": (-62.0, -14.0, -50.0, -4.0),
}
OVERPASS_LOCAL_HOURS = (1.5, 13.5)
OVERPASS_HALF_WIDTH_H = 2.0


def overpass_cloud_fraction(
    times: list[str], cloud_percent: list[float], lon: float
) -> float:
    """Mean cloud fraction (0-1) of the hours near the local overpass times."""
    picked: list[float] = []
    for stamp, pct in zip(times, cloud_percent):
        utc_hour = int(stamp[11:13]) + int(stamp[14:16]) / 60.0
        local = (utc_hour + lon / 15.0) % 24.0
        near = any(
            min(abs(local - h), 24.0 - abs(local - h)) <= OVERPASS_HALF_WIDTH_H
            for h in OVERPASS_LOCAL_HOURS
        )
        if near and pct is not None:
            picked.append(pct / 100.0)
    if not picked:
        raise ValueError("no hourly value falls near the overpass time")
    return sum(picked) / len(picked)


def _grid(region: str) -> list[tuple[float, float]]:
    lon0, lat0, lon1, lat1 = BBOX[region]
    return [
        (lat0 + (i + 0.5) * (lat1 - lat0) / 3, lon0 + (j + 0.5) * (lon1 - lon0) / 3)
        for i in range(3)
        for j in range(3)
    ]


def fetch_window(region: str, start: str) -> float:
    first = date.fromisoformat(start)
    points = _grid(region)
    query = urllib.parse.urlencode(
        {
            "latitude": ",".join(f"{lat:.3f}" for lat, _ in points),
            "longitude": ",".join(f"{lon:.3f}" for _, lon in points),
            "start_date": first.isoformat(),
            "end_date": (first + timedelta(days=4)).isoformat(),
            "hourly": "cloud_cover",
            "models": "era5",
        }
    )
    with urllib.request.urlopen(f"{API}?{query}", timeout=60) as response:  # noqa: S310 - fixed https API
        payload = json.loads(response.read().decode("utf-8"))
    results = payload if isinstance(payload, list) else [payload]
    values = [
        overpass_cloud_fraction(
            r["hourly"]["time"], r["hourly"]["cloud_cover"], point[1]
        )
        for r, point in zip(results, points)
    ]
    return sum(values) / len(values)


def main() -> None:
    results = json.loads(RESULTS.read_text())
    table: dict[str, dict[str, float]] = {"mekong": {}, "amazon": {}}
    for region, windows in table.items():
        for epoch in results[f"{region}_empirical_epochs"]:
            window = epoch["date_window"]
            windows[window] = round(fetch_window(region, window), 4)
            print(region, window, windows[window], file=sys.stderr)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(
            {
                "source": "ERA5 total cloud cover via Open-Meteo archive API",
                "method": "mean over a 3x3 grid and the hours within 2h of local 13:30 / 01:30, 5-day window",
                "regions": table,
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
