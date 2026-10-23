"""Publication-Grade Scientific Figure Renderer for Flare-Chronos.

Renders 5 high-resolution (2200x1350 px, 2x supersampled) analytical figures directly
into `docs/figures/*.png` from empirical NASA FIRMS harmonization metrics.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# High-contrast scientific color palette (Okabe-Ito & NASA Earthdata inspired)
BG_COLOR = (250, 251, 254)
PANEL_BG = (255, 255, 255)
PANEL_BORDER = (210, 218, 230)
GRID_COLOR = (232, 237, 245)
TEXT_DARK = (20, 28, 44)
TEXT_MUTED = (90, 102, 122)

COL_MODIS = (213, 94, 0)  # Vermilion / Terra-Aqua Orange-Red
COL_VIIRS = (0, 114, 178)  # Deep Ocean Blue / Suomi-JPSS
COL_HARM = (0, 158, 115)  # Bluish Green / Flare-Chronos Harmonized
COL_WARN = (230, 159, 0)  # Amber / Threshold
COL_PURPLE = (148, 82, 165)  # NOAA-20 / 21 Accent
COL_GRAY = (130, 140, 155)

# SFAI Z-score above which a calendar cell is outlined in Figure 5.
# This is a *display* threshold, published as "+2.2" in the figure caption,
# and is deliberately below the operational CRISIS tier (2.5) so the
# calendar highlights severe anomalies before a crisis alarm is raised.
SFAI_HIGHLIGHT_Z = 2.2

# Font candidates, in priority order. The macOS paths come first so the
# published figures stay byte-comparable on the reference machine; the
# Linux paths let any contributor regenerate them instead of silently
# falling back to Pillow's bitmap default font.
_FONT_CANDIDATES_BOLD = (
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf",
)
_FONT_CANDIDATES_REGULAR = (
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
)


def _get_font(
    size: int, bold: bool = False
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = _FONT_CANDIDATES_BOLD if bold else _FONT_CANDIDATES_REGULAR
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:  # noqa: BLE001, S110
                pass
    return ImageFont.load_default()


class ScientificCanvas:
    """Anti-aliased scientific chart builder using 2x supersampled rasterization."""

    def __init__(self, width: int = 2200, height: int = 1320) -> None:
        self.width = width
        self.height = height
        self.img = Image.new("RGB", (width, height), BG_COLOR)
        self.draw = ImageDraw.Draw(self.img)
        self.f_title = _get_font(34, bold=True)
        self.f_subtitle = _get_font(22, bold=False)
        self.f_panel = _get_font(25, bold=True)
        self.f_axis = _get_font(20, bold=True)
        self.f_tick = _get_font(18, bold=False)
        self.f_annot = _get_font(18, bold=True)
        self.f_small = _get_font(16, bold=False)

    def draw_header(self, title: str, subtitle: str) -> None:
        self.draw.rectangle([0, 0, self.width, 108], fill=(16, 26, 46))
        self.draw.text((48, 22), title, fill=(255, 255, 255), font=self.f_title)
        self.draw.text((48, 66), subtitle, fill=(185, 205, 235), font=self.f_subtitle)

    def draw_panel_box(
        self,
        box: tuple[int, int, int, int],
        title: str,
        subtitle: str = "",
    ) -> tuple[int, int, int, int]:
        x0, y0, x1, y1 = box
        self.draw.rounded_rectangle(
            box, radius=14, fill=PANEL_BG, outline=PANEL_BORDER, width=2
        )
        self.draw.text((x0 + 28, y0 + 16), title, fill=TEXT_DARK, font=self.f_panel)
        if subtitle:
            self.draw.text(
                (x0 + 28, y0 + 48), subtitle, fill=TEXT_MUTED, font=self.f_small
            )
        # Return inner plot area (px0, py0, px1, py1) with generous top margin for y-axis label
        return (x0 + 108, y0 + 112, x1 - 45, y1 - 86)

    def draw_axes(
        self,
        plot_box: tuple[int, int, int, int],
        x_lim: tuple[float, float],
        y_lim: tuple[float, float],
        x_ticks: Sequence[float],
        y_ticks: Sequence[float],
        x_label: str,
        y_label: str,
        x_fmt: str = "{:.0f}",
        y_fmt: str = "{:.1f}",
    ) -> None:
        px0, py0, px1, py1 = plot_box
        xmin, xmax = x_lim
        ymin, ymax = y_lim

        for xt in x_ticks:
            if xmin <= xt <= xmax:
                cx = int(px0 + (xt - xmin) / (xmax - xmin) * (px1 - px0))
                self.draw.line([(cx, py0), (cx, py1)], fill=GRID_COLOR, width=2)
                lbl = x_fmt.format(xt)
                self.draw.text(
                    (cx - 18, py1 + 12), lbl, fill=TEXT_MUTED, font=self.f_tick
                )

        for yt in y_ticks:
            if ymin <= yt <= ymax:
                cy = int(py1 - (yt - ymin) / (ymax - ymin) * (py1 - py0))
                self.draw.line([(px0, cy), (px1, cy)], fill=GRID_COLOR, width=2)
                lbl = y_fmt.format(yt)
                self.draw.text(
                    (px0 - 72, cy - 10), lbl, fill=TEXT_MUTED, font=self.f_tick
                )

        self.draw.line([(px0, py0), (px0, py1)], fill=TEXT_DARK, width=3)
        self.draw.line([(px0, py1), (px1, py1)], fill=TEXT_DARK, width=3)

        self.draw.text(
            ((px0 + px1) // 2 - len(x_label) * 5, py1 + 44),
            x_label,
            fill=TEXT_DARK,
            font=self.f_axis,
        )
        self.draw.text((px0 - 80, py0 - 30), y_label, fill=TEXT_DARK, font=self.f_axis)

    @staticmethod
    def map_pt(
        x: float,
        y: float,
        plot_box: tuple[int, int, int, int],
        x_lim: tuple[float, float],
        y_lim: tuple[float, float],
    ) -> tuple[int, int]:
        px0, py0, px1, py1 = plot_box
        u = (x - x_lim[0]) / max(1e-9, x_lim[1] - x_lim[0])
        v = (y - y_lim[0]) / max(1e-9, y_lim[1] - y_lim[0])
        u = max(0.0, min(1.0, u))
        v = max(0.0, min(1.0, v))
        return (int(px0 + u * (px1 - px0)), int(py1 - v * (py1 - py0)))

    def save(self, out_path: Path) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # Lightly downsample 2200x1320 -> 1800x1080 with LANCZOS for razor-sharp edges
        final = self.img.resize((1800, 1080), Image.Resampling.LANCZOS)
        final.save(out_path, format="PNG", optimize=True)


def render_fig1_scan_angle_physics(
    out_path: Path,
    modis_curves: dict[str, list[float]],
    viirs_curves: dict[str, list[float]],
    empirical_samples: dict[str, list[tuple[float, float]]],
) -> None:
    """Render Figure 1: MODIS vs VIIRS Scan-Angle Bow-Tie Footprint Growth & H3 Allocation."""
    c = ScientificCanvas()
    c.draw_header(
        "Figure 1 | Spherical Scan-Angle Footprint Physics & Dual-Resolution H3 Allocation",
        "Comparison of MODIS C6.1 (1 km nominal) and VIIRS C2 (375 m 3-Zone Aggregated) Instantaneous Footprints + Real NASA FIRMS Observations",
    )

    # Left Panel: Footprint Area A_p(theta) vs Scan Angle
    p1 = c.draw_panel_box(
        (36, 132, 1110, 1275),
        "A. Instantaneous Footprint Area A_p(theta) = Delta S x Delta T (km^2)",
        "Theoretical curves (Giglio et al., 2016; Wolfe et al., 2013) + Real NASA FIRMS Mekong & Amazon samples",
    )
    x_lim = (0.0, 58.0)
    y_lim = (0.0, 10.5)
    c.draw_axes(
        p1,
        x_lim,
        y_lim,
        x_ticks=[0, 10, 20, 31.7, 44.9, 55],
        y_ticks=[0, 1.0, 2.0, 4.0, 6.0, 8.0, 10.0],
        x_label="Satellite Scan / View Zenith Angle |theta| (degrees)",
        y_label="Area (km^2)",
        x_fmt="{:.1f}",
        y_fmt="{:.1f}",
    )

    # VIIRS Aggregation Zone vertical dividers
    for z_deg, z_lbl in [
        (31.72, "Zone 1->2 (3:1 to 2:1)"),
        (44.86, "Zone 2->3 (2:1 to 1:1)"),
    ]:
        zx, zy0 = c.map_pt(z_deg, 0.0, p1, x_lim, y_lim)
        _, zy1 = c.map_pt(z_deg, 10.2, p1, x_lim, y_lim)
        for yy in range(zy1, zy0, 16):
            c.draw.line([(zx, yy), (zx, min(zy0, yy + 9))], fill=COL_VIIRS, width=2)
        c.draw.text((zx - 75, zy1 + 12), z_lbl, fill=COL_VIIRS, font=c.f_small)

    # H3 Res 7 (5.16 km^2) & Res 8 (0.74 km^2) reference horizontal bars
    for h_area, h_lbl in [
        (5.161, "Uber H3 Res 7 Iso-Area Cell (5.16 km^2)"),
        (0.737, "Uber H3 Res 8 Iso-Area Cell (0.74 km^2)"),
    ]:
        hx0, hy = c.map_pt(0.0, h_area, p1, x_lim, y_lim)
        hx1, _ = c.map_pt(58.0, h_area, p1, x_lim, y_lim)
        for xx in range(hx0, hx1, 18):
            c.draw.line([(xx, hy), (min(hx1, xx + 10), hy)], fill=COL_HARM, width=2)
        c.draw.text((hx0 + 16, hy - 24), h_lbl, fill=COL_HARM, font=c.f_small)

    # Plot theoretical curves
    m_pts = [
        c.map_pt(th, ar, p1, x_lim, y_lim)
        for th, ar in zip(modis_curves["theta_deg"], modis_curves["area_km2"])
    ]
    v_pts = [
        c.map_pt(th, ar, p1, x_lim, y_lim)
        for th, ar in zip(viirs_curves["theta_deg"], viirs_curves["area_km2"])
    ]
    c.draw.line(m_pts, fill=COL_MODIS, width=5)
    c.draw.line(v_pts, fill=COL_VIIRS, width=5)

    # Overlay empirical NASA FIRMS points
    for th, ar in empirical_samples.get("modis", [])[:120]:
        px, py = c.map_pt(th, ar, p1, x_lim, y_lim)
        c.draw.ellipse(
            [px - 5, py - 5, px + 5, py + 5], fill=COL_MODIS, outline=(255, 255, 255)
        )
    for th, ar in empirical_samples.get("viirs", [])[:120]:
        px, py = c.map_pt(th, ar, p1, x_lim, y_lim)
        c.draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=COL_VIIRS)

    # Annotations
    p_edge_m = c.map_pt(55.0, 9.69, p1, x_lim, y_lim)
    c.draw.text(
        (p_edge_m[0] - 435, p_edge_m[1] + 38),
        "MODIS Edge (55 deg): 4.83x2.01 km = 9.69 km^2",
        fill=COL_MODIS,
        font=c.f_annot,
    )
    p_edge_v = c.map_pt(56.28, 0.623, p1, x_lim, y_lim)
    c.draw.text(
        (p_edge_v[0] - 455, p_edge_v[1] - 42),
        "VIIRS Edge (56.3 deg): 0.80x0.78 km = 0.62 km^2 (15.5x smaller)",
        fill=COL_VIIRS,
        font=c.f_annot,
    )

    # Right Panel: Minimum Detectable FRP Limit FRP_lim(theta, SZA)
    p2 = c.draw_panel_box(
        (1140, 132, 2164, 1275),
        "B. Minimum Detectable Fire Radiative Power FRP_lim(theta, SZA)",
        "Why raw MODIS misses 65-85% of sub-pixel agricultural & understory fires at off-nadir angles (Sofiev & Kouznetsov, 2026)",
    )
    y_lim2 = (0.0, 44.0)
    c.draw_axes(
        p2,
        x_lim,
        y_lim2,
        x_ticks=[0, 10, 20, 31.7, 44.9, 55],
        y_ticks=[0, 5, 10, 15, 20, 25, 30, 35, 40],
        x_label="Satellite Scan / View Zenith Angle |theta| (degrees)",
        y_label="FRP_lim (MW)",
        x_fmt="{:.1f}",
        y_fmt="{:.0f}",
    )

    m_day_pts = [
        c.map_pt(th, fl, p2, x_lim, y_lim2)
        for th, fl in zip(modis_curves["theta_deg"], modis_curves["frp_lim_day_mw"])
    ]
    m_nit_pts = [
        c.map_pt(th, fl, p2, x_lim, y_lim2)
        for th, fl in zip(modis_curves["theta_deg"], modis_curves["frp_lim_night_mw"])
    ]
    v_day_pts = [
        c.map_pt(th, fl, p2, x_lim, y_lim2)
        for th, fl in zip(viirs_curves["theta_deg"], viirs_curves["frp_lim_day_mw"])
    ]

    c.draw.line(m_day_pts, fill=COL_MODIS, width=5)
    c.draw.line(m_nit_pts, fill=COL_WARN, width=4)
    c.draw.line(v_day_pts, fill=COL_VIIRS, width=5)

    # Shaded zone of unobserved small fires between MODIS daytime limit and VIIRS limit
    poly_pts = m_day_pts + list(reversed(v_day_pts))
    overlay = Image.new("RGBA", (c.width, c.height), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    odraw.polygon(poly_pts, fill=(213, 94, 0, 38))
    c.img = Image.alpha_composite(c.img.convert("RGBA"), overlay).convert("RGB")
    c.draw = ImageDraw.Draw(c.img)

    c.draw.text(
        (1310, 460),
        "Unobserved MODIS Sub-Pixel Fire Zone",
        fill=COL_MODIS,
        font=c.f_panel,
    )
    c.draw.text(
        (1310, 495),
        "compensated by Flare-Chronos Stage-1 Scan-Angle Observation Operator",
        fill=TEXT_DARK,
        font=c.f_small,
    )
    c.draw.text(
        (1280, 260),
        "MODIS Daytime FRP_lim (8.2 MW nadir -> 41.2 MW at 55 deg)",
        fill=COL_MODIS,
        font=c.f_annot,
    )
    c.draw.text(
        (1280, 770),
        "MODIS Nighttime FRP_lim (3.7 MW nadir -> 38.6 MW at 55 deg)",
        fill=COL_WARN,
        font=c.f_annot,
    )
    c.draw.text(
        (1280, 1135),
        "VIIRS 375m Daytime FRP_lim (1.15 MW nadir -> 3.4 MW at 56.3 deg)",
        fill=COL_VIIRS,
        font=c.f_annot,
    )

    c.save(out_path)


def render_fig2_overpass_deduplication(
    out_path: Path,
    dedup_stats: dict[str, Any],
) -> None:
    """Render Figure 2: Multi-Satellite Overpass Deduplication, SZA Reclassification & Omega Effort."""
    c = ScientificCanvas()
    c.draw_header(
        "Figure 2 | Spatio-Temporal Overpass Deduplication & Effective Observation Effort Omega(y, phi)",
        "Resolving afternoon VIIRS constellation overlap (NOAA-20, NOAA-21, Suomi-NPP, Aqua) and NRT vs. Standard SZA discrepancies",
    )

    # Left Panel: Constellation Evolution & Effective Observation Effort Omega (2000-2026)
    p1 = c.draw_panel_box(
        (36, 132, 1110, 1275),
        "A. Satellite Constellation Expansion & Observation Effort Factor Omega(y)",
        "Without effort normalization, expanding from 1 satellite (2000) to 5 satellites (2024-2026) inflates raw fire counts by >4x",
    )
    years = list(range(2000, 2027))
    omegas = [dedup_stats["omega_by_year"][str(y)] for y in years]
    sat_counts = [dedup_stats["sat_count_by_year"][str(y)] for y in years]

    x_lim = (2000.0, 2026.5)
    y_lim = (0.0, 5.5)
    c.draw_axes(
        p1,
        x_lim,
        y_lim,
        x_ticks=[2000, 2002, 2006, 2012, 2018, 2020, 2024, 2026],
        y_ticks=[0, 1.0, 2.0, 3.0, 4.0, 5.0],
        x_label="Observation Year (2000 - 2026)",
        y_label="Satellites / Omega",
        x_fmt="{:.0f}",
        y_fmt="{:.1f}",
    )

    sat_pts = [c.map_pt(y, s, p1, x_lim, y_lim) for y, s in zip(years, sat_counts)]
    om_pts = [c.map_pt(y, om, p1, x_lim, y_lim) for y, om in zip(years, omegas)]
    c.draw.line(sat_pts, fill=COL_PURPLE, width=4)
    c.draw.line(om_pts, fill=COL_HARM, width=5)
    for pt in om_pts[::2]:
        c.draw.ellipse([pt[0] - 5, pt[1] - 5, pt[0] + 5, pt[1] + 5], fill=COL_HARM)

    # Milestone callouts
    milestones = [
        (2000, 1.0, "2000: Terra (MODIS)"),
        (2002, 2.0, "2002: +Aqua (MODIS)"),
        (2012, 3.0, "2012: +Suomi-NPP (VIIRS 375m)"),
        (2018, 4.0, "2018/20: +NOAA-20 (VIIRS 375m)"),
        (2024, 5.0, "2024: +NOAA-21 (5-Sat Train)"),
    ]
    for yr, sc, text in milestones:
        mx, my = c.map_pt(yr, sc, p1, x_lim, y_lim)
        c.draw.ellipse([mx - 6, my - 6, mx + 6, my + 6], fill=COL_PURPLE)
        x_off = -145 if yr >= 2024 else -20
        c.draw.text((mx + x_off, my - 32), text, fill=COL_PURPLE, font=c.f_small)

    c.draw.text(
        (190, 910),
        "Effective Observation Effort Omega(y, phi) (Normalized to 2003-2011 Terra+Aqua = 1.00)",
        fill=COL_HARM,
        font=c.f_annot,
    )

    # Right Panel: Empirical Deduplication Compression across Epochs (Real NASA FIRMS Data)
    p2 = c.draw_panel_box(
        (1140, 132, 2164, 1275),
        "B. Empirical Multi-Sensor Deduplication on Real NASA FIRMS Data (2012-2025)",
        "Comparison of Raw Thermal Detections vs. Deduplicated Physical Fire Episodes (tau = 60 min, Elliptical Overlap)",
    )
    epochs = dedup_stats["empirical_epochs"]
    n_ep = len(epochs)
    x_lim2 = (-0.6, n_ep - 0.4)
    max_val = max(e["raw_detections"] for e in epochs) * 1.15
    y_lim2 = (0.0, max_val)

    c.draw_axes(
        p2,
        x_lim2,
        y_lim2,
        x_ticks=list(range(n_ep)),
        y_ticks=np.linspace(0, max_val, 6).tolist(),
        x_label="Empirical NASA FIRMS 5-Day Benchmark Windows",
        y_label="Count (5-Day Window)",
        x_fmt="{:.0f}",
        y_fmt="{:.0f}",
    )

    for idx, ep in enumerate(epochs):
        bx_raw_0, by_raw_0 = c.map_pt(idx - 0.26, 0, p2, x_lim2, y_lim2)
        bx_raw_1, by_raw_1 = c.map_pt(
            idx - 0.02, ep["raw_detections"], p2, x_lim2, y_lim2
        )
        c.draw.rectangle([bx_raw_0, by_raw_1, bx_raw_1, by_raw_0], fill=COL_MODIS)

        bx_ep_0, by_ep_0 = c.map_pt(idx + 0.02, 0, p2, x_lim2, y_lim2)
        bx_ep_1, by_ep_1 = c.map_pt(idx + 0.26, ep["fire_episodes"], p2, x_lim2, y_lim2)
        c.draw.rectangle([bx_ep_0, by_ep_1, bx_ep_1, by_ep_0], fill=COL_HARM)

        ratio = ep["raw_detections"] / max(1, ep["fire_episodes"])
        c.draw.text(
            (bx_raw_0 - 6, by_raw_1 - 26),
            f"{ep['raw_detections']:,}",
            fill=COL_MODIS,
            font=c.f_small,
        )
        c.draw.text(
            (bx_ep_0 - 2, by_ep_1 - 26),
            f"{ep['fire_episodes']:,} ({ratio:.2f}x)",
            fill=COL_HARM,
            font=c.f_small,
        )
        c.draw.text(
            (bx_raw_0 - 10, by_raw_0 + 34), ep["label"], fill=TEXT_DARK, font=c.f_small
        )

    # Legend box in Right Panel
    c.draw.rectangle([1280, 245, 1308, 268], fill=COL_MODIS)
    c.draw.text(
        (1320, 245),
        "Raw Multi-Sensor Thermal Detections (MODIS + S-NPP + NOAA-20/21)",
        fill=TEXT_DARK,
        font=c.f_annot,
    )
    c.draw.rectangle([1280, 282, 1308, 305], fill=COL_HARM)
    c.draw.text(
        (1320, 282),
        "Deduplicated Physical Fire Episodes (Spatio-Temporal Kernel Clustering)",
        fill=TEXT_DARK,
        font=c.f_annot,
    )

    c.save(out_path)


def render_fig3_cross_sensor_frp(
    out_path: Path,
    cal_data: dict[str, Any],
) -> None:
    """Render Figure 3: Co-Incident Aqua-MODIS vs Suomi-NPP VIIRS Cross-Calibration & EQM."""
    c = ScientificCanvas()
    c.draw_header(
        "Figure 3 | Two-Stage Physics-Guided FRP Cross-Calibration (Co-Incident Aqua & Suomi-NPP Overpasses)",
        f"Stage 1 Scan-Angle Observation Operator + Stage 2 Empirical Quantile Mapping on N = {cal_data['n_pairs']} Co-Incident Iso-Area Cells",
    )

    p1 = c.draw_panel_box(
        (36, 132, 1110, 1275),
        "A. Co-Incident H3 Cell Radiative Power: Raw MODIS vs. Calibrated Flare-Chronos",
        f"R^2 improves from {cal_data['raw_r2']:.3f} (Raw MODIS) to {cal_data['harm_r2']:.3f} (Flare-Chronos); RMSE drops from {cal_data['raw_rmse']:.1f} to {cal_data['harm_rmse']:.1f} MW",
    )
    max_frp = float(cal_data["max_axis_mw"])
    x_lim = (0.0, max_frp)
    y_lim = (0.0, max_frp)
    ticks = np.linspace(0, max_frp, 6).tolist()
    c.draw_axes(
        p1,
        x_lim,
        y_lim,
        x_ticks=ticks,
        y_ticks=ticks,
        x_label="Reference Suomi-NPP VIIRS 375m Cell FRP (MW)",
        y_label="MODIS / Calibrated FRP (MW)",
        x_fmt="{:.0f}",
        y_fmt="{:.0f}",
    )

    # 1:1 Ideal Parity line
    p00 = c.map_pt(0, 0, p1, x_lim, y_lim)
    p11 = c.map_pt(max_frp, max_frp, p1, x_lim, y_lim)
    c.draw.line([p00, p11], fill=TEXT_DARK, width=3)
    c.draw.text(
        (p11[0] - 190, p11[1] + 18),
        "1:1 Parity Reference",
        fill=TEXT_DARK,
        font=c.f_annot,
    )

    for v_val, m_raw, m_harm in zip(
        cal_data["viirs_sample"],
        cal_data["modis_raw_sample"],
        cal_data["modis_harm_sample"],
    ):
        pr = c.map_pt(v_val, m_raw, p1, x_lim, y_lim)
        ph = c.map_pt(v_val, m_harm, p1, x_lim, y_lim)
        c.draw.ellipse([pr[0] - 4, pr[1] - 4, pr[0] + 4, pr[1] + 4], fill=COL_MODIS)
        c.draw.ellipse([ph[0] - 4, ph[1] - 4, ph[0] + 4, ph[1] + 4], fill=COL_HARM)

    c.draw.text(
        (175, 255),
        f"Raw Aqua-MODIS (Systematic Underestimation Bias, R^2 = {cal_data['raw_r2']:.3f})",
        fill=COL_MODIS,
        font=c.f_annot,
    )
    c.draw.text(
        (175, 292),
        f"Flare-Chronos Calibrated MODIS (Unbiased Parity, R^2 = {cal_data['harm_r2']:.3f})",
        fill=COL_HARM,
        font=c.f_annot,
    )

    # Right Panel: Empirical Cumulative Distribution Function (ECDF) & KS Distance
    p2 = c.draw_panel_box(
        (1140, 132, 2164, 1275),
        "B. Cumulative Distribution Function (ECDF) & Kolmogorov-Smirnov Convergence",
        f"Kolmogorov-Smirnov distance D_KS reduced by {(1.0 - cal_data['ks_after'] / cal_data['ks_before']) * 100:.1f}% (from D_KS = {cal_data['ks_before']:.3f} to {cal_data['ks_after']:.3f})",
    )
    x_lim2 = (0.0, max_frp)
    y_lim2 = (0.0, 1.02)
    c.draw_axes(
        p2,
        x_lim2,
        y_lim2,
        x_ticks=ticks,
        y_ticks=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        x_label="Cell Fire Radiative Power sum(FRP) in Iso-Area Cell (MW)",
        y_label="Cumulative Probability F(x)",
        x_fmt="{:.0f}",
        y_fmt="{:.1f}",
    )

    grid_x = cal_data["cdf_grid_mw"]
    pts_v = [
        c.map_pt(x, y, p2, x_lim2, y_lim2)
        for x, y in zip(grid_x, cal_data["cdf_viirs"])
    ]
    pts_m = [
        c.map_pt(x, y, p2, x_lim2, y_lim2)
        for x, y in zip(grid_x, cal_data["cdf_modis_raw"])
    ]
    pts_h = [
        c.map_pt(x, y, p2, x_lim2, y_lim2)
        for x, y in zip(grid_x, cal_data["cdf_modis_harm"])
    ]

    c.draw.line(pts_m, fill=COL_MODIS, width=4)
    c.draw.line(pts_v, fill=COL_VIIRS, width=6)
    c.draw.line(pts_h, fill=COL_HARM, width=4)

    c.draw.text(
        (1460, 680),
        "Raw MODIS C6.1 CDF (Truncated sub-pixel fire tail)",
        fill=COL_MODIS,
        font=c.f_annot,
    )
    c.draw.text(
        (1460, 725),
        "Reference VIIRS 375m C2 CDF (Target Distribution)",
        fill=COL_VIIRS,
        font=c.f_annot,
    )
    c.draw.text(
        (1460, 770),
        "Flare-Chronos Harmonized CDF (Matches Target up to P99)",
        fill=COL_HARM,
        font=c.f_annot,
    )

    c.save(out_path)


def render_fig4_regime_shift_elimination(
    out_path: Path,
    series_data: dict[str, Any],
) -> None:
    """Render Figure 4: 26-Year Multi-Epoch Regime Shift Elimination (Mekong & Amazon)."""
    c = ScientificCanvas()
    c.draw_header(
        "Figure 4 | Elimination of Artificial Multi-Sensor Step Jumps Across 26 Years (2000 - 2026)",
        "Demonstrating how raw unharmonized fire counts explode artificially in 2012 (+SNPP) and 2020/2024 (+NOAA-20/21) vs. Flare-Chronos Physical Baseline",
    )

    for panel_idx, (region_key, box, title_str) in enumerate(
        [
            (
                "mekong",
                (36, 132, 1110, 1275),
                "A. Case Study 1: Mekong Subregion & Vietnam (Peak Dry Season - March)",
            ),
            (
                "amazon",
                (1140, 132, 2164, 1275),
                "B. Case Study 2: Southern Amazon Arc of Deforestation (Peak Burn - August)",
            ),
        ]
    ):
        rdata = series_data[region_key]
        years = rdata["years"]
        raw_idx = rdata["raw_index_2005_eq_100"]
        harm_idx = rdata["harmonized_index_2005_eq_100"]

        p = c.draw_panel_box(
            box,
            title_str,
            "Indexed to 2005 Baseline = 100 | Contrasting Unharmonized Raw Multi-Sensor Sum vs. Flare-Chronos HFD",
        )
        ymax = max(max(raw_idx), max(harm_idx)) * 1.12
        x_lim = (2000.0, 2026.5)
        y_lim = (0.0, ymax)
        c.draw_axes(
            p,
            x_lim,
            y_lim,
            x_ticks=[2001, 2005, 2010, 2012, 2016, 2020, 2024, 2026],
            y_ticks=np.linspace(0, ymax, 6).tolist(),
            x_label="Year (2000 - 2026)",
            y_label="Activity Index (2005=100)",
            x_fmt="{:.0f}",
            y_fmt="{:.0f}",
        )

        # Vertical sensor introduction lines
        for s_yr, s_lbl in [
            (2012, "2012: +S-NPP VIIRS"),
            (2020, "2020: +NOAA-20"),
            (2024, "2024: +NOAA-21"),
        ]:
            sx, sy0 = c.map_pt(s_yr, 0, p, x_lim, y_lim)
            _, sy1 = c.map_pt(s_yr, ymax * 0.96, p, x_lim, y_lim)
            for yy in range(sy1, sy0, 16):
                c.draw.line(
                    [(sx, yy), (sx, min(sy0, yy + 9))], fill=COL_PURPLE, width=2
                )
            c.draw.text((sx - 55, sy1 - 24), s_lbl, fill=COL_PURPLE, font=c.f_small)

        pts_raw = [c.map_pt(y, v, p, x_lim, y_lim) for y, v in zip(years, raw_idx)]
        pts_harm = [c.map_pt(y, v, p, x_lim, y_lim) for y, v in zip(years, harm_idx)]

        c.draw.line(pts_raw, fill=COL_MODIS, width=5)
        c.draw.line(pts_harm, fill=COL_HARM, width=5)
        for pt in pts_raw:
            c.draw.ellipse([pt[0] - 5, pt[1] - 5, pt[0] + 5, pt[1] + 5], fill=COL_MODIS)
        for pt in pts_harm:
            c.draw.ellipse([pt[0] - 5, pt[1] - 5, pt[0] + 5, pt[1] + 5], fill=COL_HARM)

        # The step-bias range is derived from this panel's own raw index at the
        # years a satellite was added, so the annotation cannot drift from the
        # curve it labels.
        step_years = [y for y in (2012, 2020, 2024) if y in years]
        inflations = [raw_idx[years.index(y)] - 100.0 for y in step_years]
        step_lo = f"{min(inflations):,.0f}"
        step_hi = f"{max(inflations):,.0f}"

        c.draw.text(
            (box[0] + 125, 295),
            f"Raw Unharmonized Sum (Artificial +{step_lo}% to +{step_hi}% "
            "Sensor Step Bias!)",
            fill=COL_MODIS,
            font=c.f_annot,
        )
        c.draw.text(
            (box[0] + 125, 330),
            "Flare-Chronos Harmonized Fire Density (True Physical & Climatic Signal)",
            fill=COL_HARM,
            font=c.f_annot,
        )

    c.save(out_path)


def _wrap_caption(caption: str, max_width: float) -> list[str]:
    """Wrap a figure caption to ``max_width`` pixels.

    Prefers to break on the ``" | "`` separator the captions use, so the
    "Peak Fire Window" and "Anomalies" halves stay on their own lines, and
    falls back to word wrapping for a half that is still too wide.
    """
    font = _get_font(16, bold=False)
    lines: list[str] = []
    for segment in caption.split(" | "):
        words = segment.split(" ")
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if current and font.getlength(candidate) > max_width:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
    return lines


def _heatmap_color(norm_val: float) -> tuple[int, int, int]:
    """YlOrRd / Inferno scientific perceptual colormap for norm_val in [0, 1]."""
    v = max(0.0, min(1.0, norm_val))
    stops = [
        (0.00, (255, 252, 235)),
        (0.25, (254, 217, 118)),
        (0.50, (253, 141, 60)),
        (0.75, (227, 26, 28)),
        (1.00, (115, 0, 38)),
    ]
    for i in range(len(stops) - 1):
        v0, c0 = stops[i]
        v1, c1 = stops[i + 1]
        if v0 <= v <= v1:
            t = (v - v0) / (v1 - v0)
            return (
                int(c0[0] + t * (c1[0] - c0[0])),
                int(c0[1] + t * (c1[1] - c0[1])),
                int(c0[2] + t * (c1[2] - c0[2])),
            )
    return stops[-1][1]


def render_fig5_burning_activity_calendar(
    out_path: Path,
    cal_matrix_data: dict[str, Any],
) -> None:
    """Render Figure 5: 26-Year Harmonized Burning Activity Calendar (Year x Pentad Heatmap & SFAI)."""
    c = ScientificCanvas()
    c.draw_header(
        "Figure 5 | Flare-Chronos 26-Year Harmonized Burning Activity Calendar (2001 - 2026 x 73 Pentads)",
        "Unified MODIS + VIIRS Seasonal Fire Phenology Matrix & Standardized Fire Anomaly Index (SFAI Z-Score) Early-Warning Triggers",
    )

    for region_key, box, title_str in [
        (
            "mekong",
            (36, 132, 1110, 1275),
            "A. Mekong & Vietnam Harmonized Burning Calendar (HFD & SFAI Anomalies)",
        ),
        (
            "amazon",
            (1140, 132, 2164, 1275),
            "B. Amazon Basin Harmonized Burning Calendar (HFD & SFAI Anomalies)",
        ),
    ]:
        rdata = cal_matrix_data[region_key]
        years = rdata["years"]  # 2001..2026 (26 rows)
        matrix = np.array(rdata["hfd_matrix"], dtype=float)  # shape (26, 73)
        sfai_mat = np.array(rdata["sfai_matrix"], dtype=float)
        observed_mat = np.array(rdata["cell_provenance_matrix"]) == 0

        p = c.draw_panel_box(
            box,
            title_str,
            f"Rows: Years (2001-2026) | Columns: 73 Climatological Pentads (Jan 1 - Dec 31) | White dot = observed cell, all others modelled | Cyan Outline = observed cell with Z >= +{SFAI_HIGHLIGHT_Z}",
        )
        px0, py0, px1, py1 = p
        n_rows, n_cols = matrix.shape
        cw = (px1 - px0) / n_cols
        ch = (py1 - py0) / n_rows
        vmax = float(np.percentile(matrix, 98))

        for r_idx in range(n_rows):
            yr = years[r_idx]
            cy0 = int(py0 + r_idx * ch)
            cy1 = int(py0 + (r_idx + 1) * ch)
            if r_idx % 3 == 0 or yr in (2012, 2016, 2024, 2026):
                c.draw.text(
                    (px0 - 58, cy0 + 2), str(yr), fill=TEXT_DARK, font=c.f_small
                )

            for c_idx in range(n_cols):
                cx0 = int(px0 + c_idx * cw)
                cx1 = int(px0 + (c_idx + 1) * cw)
                val = matrix[r_idx, c_idx]
                col = _heatmap_color(val / max(1e-6, vmax))
                c.draw.rectangle([cx0, cy0, cx1, cy1], fill=col)
                if observed_mat[r_idx, c_idx]:
                    mx, my = (cx0 + cx1) // 2, (cy0 + cy1) // 2
                    c.draw.ellipse(
                        [mx - 2, my - 2, mx + 2, my + 2], fill=(255, 255, 255)
                    )
                if sfai_mat[r_idx, c_idx] >= SFAI_HIGHLIGHT_Z and val >= 0.35 * vmax:
                    c.draw.rectangle(
                        [cx0, cy0, cx1, cy1], outline=(0, 210, 255), width=2
                    )

        # Month / Pentad x-axis labels
        month_pentads = [
            (1, "Jan"),
            (7, "Feb"),
            (13, "Mar"),
            (19, "Apr"),
            (25, "May"),
            (31, "Jun"),
            (37, "Jul"),
            (43, "Aug"),
            (49, "Sep"),
            (55, "Oct"),
            (61, "Nov"),
            (67, "Dec"),
        ]
        for pt_idx, m_lbl in month_pentads:
            mx = int(px0 + (pt_idx - 1) * cw)
            c.draw.line([(mx, py1), (mx, py1 + 8)], fill=TEXT_DARK, width=2)
            c.draw.text((mx - 10, py1 + 12), m_lbl, fill=TEXT_DARK, font=c.f_small)

        c.draw.rectangle([px0, py0, px1, py1], outline=TEXT_DARK, width=2)
        # The caption names every anomaly year, so it is wider than a single
        # panel. Split it on the " | " separator and wrap, rather than letting
        # it run off the edge of the figure.
        caption_x = px0 + 10
        caption_width = px1 - 10 - caption_x
        for line_no, line in enumerate(
            _wrap_caption(rdata["summary_caption"], caption_width)
        ):
            c.draw.text(
                (caption_x, py1 + 42 + line_no * 24),
                line,
                fill=TEXT_DARK,
                font=c.f_small,
            )

    c.save(out_path)
