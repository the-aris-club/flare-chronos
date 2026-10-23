"""Checklist Facade Seam for Flare-Chronos (src/harmonization/firms_harmonizer.py).

Delegates all domain physics, H3 fractional footprint allocation, astronomical SZA
reclassification, multi-satellite overpass deduplication, and Two-Stage FRP calibration
to the monorepo package `packages/harmonization-core` (`flare_chronos_core`).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

# Ensure monorepo core package is on sys.path when invoked directly
_ROOT = Path(__file__).resolve().parents[2]
_CORE_SRC = _ROOT / "packages" / "harmonization-core" / "src"
if str(_CORE_SRC) not in sys.path:
    sys.path.insert(0, str(_CORE_SRC))

from flare_chronos_core import *  # re-export core domain + physics API for compat facade


class FIRMSHarmonizer:
    """High-level orchestrator for MODIS C6.1 and VIIRS 375m C1/C2 harmonization."""

    def __init__(
        self,
        calibration_model: CrossSensorCalibrationModel | None = None,
        persistent_static_h3_res8: set[str] | None = None,
        overpass_window_minutes: float = FIRE_EPISODE_WINDOW_MINUTES,
    ) -> None:
        self.calibration_model = calibration_model or default_calibration_model()
        self.persistent_static_h3_res8 = persistent_static_h3_res8 or set()
        self.overpass_window_minutes = overpass_window_minutes

    def harmonize_dataframe(
        self,
        df: pd.DataFrame,
        default_source: str = "",
    ) -> list[HarmonizedDetection]:
        """Parse and harmonize a NASA FIRMS DataFrame into HarmonizedDetection objects."""
        raw_detections = parse_firms_dataframe(df, default_source=default_source)
        return harmonize_detections(
            raw_detections,
            calibration_model=self.calibration_model,
            persistent_static_h3_res8=self.persistent_static_h3_res8,
        )

    def deduplicate_to_episodes(
        self,
        harmonized: list[HarmonizedDetection],
    ) -> list[FireEpisode]:
        """Cluster multi-satellite overpasses into deduplicated physical Fire Episodes."""
        return cluster_fire_episodes(
            harmonized,
            temporal_window_minutes=self.overpass_window_minutes,
        )

    def generate_calendar(
        self,
        episodes: list[FireEpisode],
        aoi_area_km2: float,
        mean_latitude_deg: float = 16.0,
    ) -> list[BurningCalendarCell]:
        """Produce the Year x Pentad Harmonized Burning Activity Calendar."""
        return build_burning_activity_calendar(
            episodes=episodes,
            aoi_area_km2=aoi_area_km2,
            mean_latitude_deg=mean_latitude_deg,
        )

    @staticmethod
    def summarize_episodes_to_dataframe(episodes: list[FireEpisode]) -> pd.DataFrame:
        """Export deduplicated Fire Episodes to a clean tabular DataFrame."""
        rows: list[dict[str, object]] = []
        for ep in episodes:
            rows.append(
                {
                    "episode_id": ep.episode_id,
                    "centroid_lat": ep.centroid_lat,
                    "centroid_lon": ep.centroid_lon,
                    "start_utc": ep.start_utc.isoformat(),
                    "end_utc": ep.end_utc.isoformat(),
                    "h3_res7_cell": ep.h3_res7_cell,
                    "h3_res8_cell": ep.h3_res8_cell,
                    "daynight": ep.harmonized_daynight,
                    "platforms": ",".join(ep.contributing_platforms),
                    "raw_detection_count": ep.raw_detection_count,
                    "combined_probability": ep.combined_probability,
                    "max_footprint_area_km2": ep.max_footprint_area_km2,
                    "raw_sum_frp_mw": ep.raw_sum_frp_mw,
                    "harmonized_frp_mw": ep.harmonized_frp_mw,
                    "omega_effort": ep.effective_observation_effort_omega,
                    "effort_normalized_episodes": ep.effort_normalized_episode_count,
                }
            )
        return pd.DataFrame(rows)
