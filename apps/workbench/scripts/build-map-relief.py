"""Render a shaded-relief image per region, already in the map's Lambert projection.

Input: Natural Earth "Shaded Relief" SR_HR (grey, 1/60 degree, public domain), plus the
lon/lat grid scripts/build-map-data.mjs writes under .cache/relief-grid. Output:
public/map/relief-<region>.webp, one pixel per grid cell, so the browser draws it over the
viewBox with no reprojection.

    curl -sSL -o .cache/ne/relief/SR_HR.zip https://naturalearth.s3.amazonaws.com/10m_raster/SR_HR.zip
    (unzip SR_HR.tif and SR_HR.tfw next to it)
    ../../.venv/bin/python -I scripts/build-map-relief.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

APP = Path(__file__).resolve().parent.parent
RASTER = APP / ".cache/ne/relief/SR_HR.tif"
GRID = APP / ".cache/relief-grid"
OUT = APP / "public/map"

# SR_HR.tfw: pixel size and the centre of the top-left pixel.
STEP = 1 / 60
LON0 = -179.99166666666667
LAT0 = 89.99166666666667


def sample(raster: np.ndarray, lon: np.ndarray, lat: np.ndarray) -> np.ndarray:
    """Bilinear sample; NaN where the pixel has no lon/lat."""
    height, width = raster.shape
    x = (lon - LON0) / STEP
    y = (LAT0 - lat) / STEP
    ok = np.isfinite(x) & np.isfinite(y)
    x = np.where(ok, x, 0.0)
    y = np.where(ok, y, 0.0)
    x0 = np.clip(np.floor(x).astype(np.int64), 0, width - 2)
    y0 = np.clip(np.floor(y).astype(np.int64), 0, height - 2)
    fx = np.clip(x - x0, 0, 1)
    fy = np.clip(y - y0, 0, 1)
    a = raster[y0, x0].astype(np.float32)
    b = raster[y0, x0 + 1].astype(np.float32)
    c = raster[y0 + 1, x0].astype(np.float32)
    d = raster[y0 + 1, x0 + 1].astype(np.float32)
    out = (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy
    out[~ok] = np.nan
    return out


def main() -> None:
    Image.MAX_IMAGE_PIXELS = None
    raster = np.asarray(Image.open(RASTER))
    OUT.mkdir(parents=True, exist_ok=True)

    for meta in sorted(GRID.glob("*.json")):
        name = meta.stem
        size = json.loads(meta.read_text())
        grid = np.fromfile(GRID / f"{name}.f32", dtype=np.float32).reshape(
            size["height"], size["width"], 2
        )
        shade = sample(raster, grid[..., 0], grid[..., 1])

        # The source is a flat light grey with shading around it. Re-centre the flat level
        # on 128 and stretch the shading, so a soft-light blend leaves flat land untouched
        # and only the hills darken and brighten it, in either theme.
        flat = np.nanmedian(shade)
        low, high = np.nanpercentile(shade, [1, 99])
        centred = np.where(
            shade >= flat,
            128 + (shade - flat) / max(high - flat, 1) * 127,
            128 - (flat - shade) / max(flat - low, 1) * 127,
        )
        image = np.clip(np.nan_to_num(centred, nan=128), 0, 255).astype(np.uint8)

        target = OUT / f"relief-{name}.webp"
        Image.fromarray(image, mode="L").convert("RGB").save(
            target, quality=88, method=6
        )
        print(
            f"{name}: {size['width']}x{size['height']} flat={flat:.0f} -> {target.name} "
            f"({target.stat().st_size // 1024} KB)"
        )


if __name__ == "__main__":
    main()
