"""Derive each region's Measured Epoch plan from the raw FIRMS archive."""

from __future__ import annotations

from pathlib import Path

#: A slice file smaller than this holds only a header, i.e. no detections.
_MIN_SLICE_BYTES = 150

_ANCHOR_SOURCE = "MODIS_SP"

#: Sources that join an epoch when their slice is in the archive, in the
#: order the harmonizer reads them.
_COMPANION_SOURCES = ("VIIRS_SNPP_SP", "VIIRS_NOAA20_SP", "VIIRS_NOAA21_NRT")


def _has_data(raw_dir: Path, region: str, source: str, date: str) -> bool:
    path = raw_dir / f"{region}__{source}__{date}__5d.csv"
    return path.exists() and path.stat().st_size >= _MIN_SLICE_BYTES


def build_epoch_plan(
    region: str, raw_dir: Path, current_year: int
) -> list[tuple[str, list[str]]]:
    """Return ``(date, sources)`` for every Measured Epoch of ``region``.

    An epoch is a year whose MODIS science-quality slice holds detections.
    VIIRS slices join it when present. The current year is excluded: its
    window belongs to a year still in progress.
    """
    plan: list[tuple[str, list[str]]] = []
    for path in sorted(raw_dir.glob(f"{region}__{_ANCHOR_SOURCE}__*__5d.csv")):
        date = path.name.split("__")[2]
        if int(date[:4]) >= current_year:
            continue
        if not _has_data(raw_dir, region, _ANCHOR_SOURCE, date):
            continue
        sources = [_ANCHOR_SOURCE] + [
            s for s in _COMPANION_SOURCES if _has_data(raw_dir, region, s, date)
        ]
        plan.append((date, sources))
    if not plan:
        raise ValueError(
            f"no Measured Epoch for {region!r} in {raw_dir} (is data/raw present?)"
        )
    return plan
