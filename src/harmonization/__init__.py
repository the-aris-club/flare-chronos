"""Compatibility package exposing Flare-Chronos harmonization modules."""

from .firms_harmonizer import (
    FIRMSHarmonizer,
    allocate_footprint_to_h3,
    build_burning_activity_calendar,
    cluster_fire_episodes,
    compute_solar_zenith_angle,
    harmonize_detections,
    parse_firms_dataframe,
    reconstruct_instantaneous_footprint,
)

__all__ = [
    "FIRMSHarmonizer",
    "allocate_footprint_to_h3",
    "build_burning_activity_calendar",
    "cluster_fire_episodes",
    "compute_solar_zenith_angle",
    "harmonize_detections",
    "parse_firms_dataframe",
    "reconstruct_instantaneous_footprint",
]
