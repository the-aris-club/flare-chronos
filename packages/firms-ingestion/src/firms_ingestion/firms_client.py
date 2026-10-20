"""NASA LANCE FIRMS REST API and Open Archive Ingestion Adapter.

Implements paced, cached querying against NASA FIRMS endpoints while respecting
the 5,000 transactions per 10-minute interval rate limit.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

# Canonical Case Study Bounding Boxes (west,south,east,north)
BBOX_MEKONG = "100.0,11.0,109.5,23.5"  # Vietnam, Laos, Cambodia, E. Thailand
BBOX_AMAZON = "-62.0,-14.0,-50.0,-4.0"  # Southern Amazon Arc of Deforestation (Mato Grosso / Para)

FIRMS_API_BASE = "https://firms.modaps.eosdis.nasa.gov/api"
FIRMS_OPEN_CSV_BASE = "https://firms.modaps.eosdis.nasa.gov/data/active_fire"


@dataclass(frozen=True)
class FIRMSQuerySpec:
    """Specification for a single historical or near-real-time FIRMS area request."""

    region_tag: str
    source: str
    bbox: str
    day_range: int
    start_date: str | None = None  # YYYY-MM-DD; None fetches latest NRT window

    @property
    def cache_filename(self) -> str:
        date_part = self.start_date if self.start_date else "latest"
        return f"{self.region_tag}__{self.source}__{date_part}__{self.day_range}d.csv"


def load_env_map_key(env_path: Path | None = None) -> str:
    """Load FIRMS_MAP_KEY from environment or workspace .env file."""
    if os.environ.get("FIRMS_MAP_KEY"):
        return os.environ["FIRMS_MAP_KEY"].strip()

    candidates = [
        env_path,
        Path.cwd() / ".env",
        Path(__file__).resolve().parents[4] / ".env",
    ]
    for path in candidates:
        if path and path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("FIRMS_MAP_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise ValueError("FIRMS_MAP_KEY not found in environment or .env")


class FIRMSClient:
    """Adapter for NASA LANCE FIRMS REST API and Open CSV endpoints with disk caching."""

    def __init__(
        self,
        map_key: str | None = None,
        cache_dir: Path | None = None,
        min_request_interval_sec: float = 0.35,
        timeout_sec: int = 30,
    ) -> None:
        self.map_key = map_key or load_env_map_key()
        self.cache_dir = cache_dir or (
            Path(__file__).resolve().parents[4] / "data" / "raw"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.min_request_interval_sec = min_request_interval_sec
        self.timeout_sec = timeout_sec
        self._last_request_ts = 0.0
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
                ),
                "Accept": "text/csv,text/plain,*/*",
            }
        )

    def _pace(self) -> None:
        elapsed = time.monotonic() - self._last_request_ts
        if elapsed < self.min_request_interval_sec:
            time.sleep(self.min_request_interval_sec - elapsed)
        self._last_request_ts = time.monotonic()

    def check_data_availability(self, force_refresh: bool = False) -> pd.DataFrame:
        """Query /api/data_availability/csv/{MAP_KEY}/all to verify sensor date ranges."""
        cache_file = self.cache_dir / "firms_data_availability.csv"
        if cache_file.exists() and not force_refresh:
            return pd.read_csv(cache_file)

        self._pace()
        url = f"{FIRMS_API_BASE}/data_availability/csv/{self.map_key}/all"
        resp = self.session.get(url, timeout=self.timeout_sec)
        resp.raise_for_status()
        text = resp.text.strip()
        cache_file.write_text(text + "\n", encoding="utf-8")
        return pd.read_csv(StringIO(text))

    def fetch_area_csv(
        self, spec: FIRMSQuerySpec, force_refresh: bool = False
    ) -> pd.DataFrame:
        """Fetch active fire Thermal Detections for a bounding box and date window."""
        cache_file = self.cache_dir / spec.cache_filename
        if cache_file.exists() and not force_refresh:
            content = cache_file.read_text(encoding="utf-8").strip()
            if not content or "Invalid" in content[:60] or "Error" in content[:60]:
                return pd.DataFrame()
            return pd.read_csv(StringIO(content))

        self._pace()
        if spec.start_date:
            url = (
                f"{FIRMS_API_BASE}/area/csv/{self.map_key}/{spec.source}/"
                f"{spec.bbox}/{spec.day_range}/{spec.start_date}"
            )
        else:
            url = (
                f"{FIRMS_API_BASE}/area/csv/{self.map_key}/{spec.source}/"
                f"{spec.bbox}/{spec.day_range}"
            )

        resp = self.session.get(url, timeout=self.timeout_sec)
        resp.raise_for_status()
        text = resp.text.strip()
        # Only cache valid CSV responses containing header 'latitude'
        if "latitude" in text[:120].lower():
            cache_file.write_text(text + "\n", encoding="utf-8")
            df = pd.read_csv(StringIO(text))
            df["region_tag"] = spec.region_tag
            df["source_code"] = spec.source
            return df
        return pd.DataFrame()

    def fetch_open_7d_feed(self, sensor_path: str, filename: str) -> pd.DataFrame:
        """Fetch direct 7-day regional CSV feed (no API transaction cost)."""
        cache_file = self.cache_dir / f"open7d__{filename}"
        if cache_file.exists():
            return pd.read_csv(cache_file)

        self._pace()
        url = f"{FIRMS_OPEN_CSV_BASE}/{sensor_path}/csv/{filename}"
        resp = self.session.get(url, timeout=self.timeout_sec)
        resp.raise_for_status()
        text = resp.text.strip()
        if "latitude" in text[:120].lower():
            cache_file.write_text(text + "\n", encoding="utf-8")
            return pd.read_csv(StringIO(text))
        return pd.DataFrame()

    def fetch_batch_progressively(
        self,
        specs: list[FIRMSQuerySpec],
        pause_between_specs_sec: float = 0.5,
    ) -> dict[str, int]:
        """Fetch a list of FIRMSQuerySpecs progressively with caching and status counts."""
        summary: dict[str, int] = {}
        for spec in specs:
            try:
                df = self.fetch_area_csv(spec)
                summary[spec.cache_filename] = len(df)
                time.sleep(pause_between_specs_sec)
            except Exception as exc:  # noqa: BLE001
                summary[spec.cache_filename] = -1
                print(f"[WARN] Failed {spec.cache_filename}: {exc}")
        return summary
