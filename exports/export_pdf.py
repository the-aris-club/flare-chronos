#!/usr/bin/env python3
"""
High-Resolution Vector PDF Exporter for Flare-Chronos (English Global Judging Edition):
1. exports/PROPOSAL.md   -> exports/PROPOSAL.pdf   (Official NASA Space Apps Technical Proposal)
2. exports/REPORT.md     -> exports/REPORT.pdf     (Codebase Architecture & Empirical Validation Report)
3. exports/MODEL_FLOW.md -> exports/MODEL_FLOW.pdf (Dual-System Cognitive AI Harness Model Flow Report)

Uses Pandoc + WeasyPrint with:
- Purpose-specific Vector SVG Architecture, Sequence, and 8-Node LangGraph StateGraph Diagrams
- LaTeX-to-Typographic-HTML Mathematical Equation Renderer for static WeasyPrint rendering
- GitHub Alert Callout Box Formatter (> [!IMPORTANT], > [!NOTE], etc.)
- A4 Print Layout, Running Headers/Footers, Purpose-Specific Cover Badge, and Diagonal Author Watermark
"""

from __future__ import annotations

import argparse
import base64
import html
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def _resolve_binary(name: str) -> str:
    """Locate a CLI dependency on ``PATH``, falling back to the Homebrew prefix."""
    found = shutil.which(name)
    if found:
        return found
    homebrew = Path("/opt/homebrew/bin") / name
    if homebrew.exists():
        return str(homebrew)
    raise FileNotFoundError(
        f"Required tool {name!r} was not found on PATH or in /opt/homebrew/bin."
    )


# ==============================================================================
# 1A. CONCEPTUAL VECTOR SVG DIAGRAMS FOR PROPOSAL.PDF
# ==============================================================================

PROPOSAL_ARCH_SVG = """
<div class="diagram-container">
<div class="diagram-title">ARCHITECTURE FIGURE 1: 5-TIER END-TO-END FLARE-CHRONOS CROSS-SENSOR HARMONIZATION &amp; COGNITIVE WORKBENCH ARCHITECTURE</div>
<svg viewBox="0 0 920 690" width="660" height="495" style="width:100%; height:auto;" xmlns="http://www.w3.org/2000/svg" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f8fafc"/>
      <stop offset="100%" stop-color="#f1f5f9"/>
    </linearGradient>
    <linearGradient id="nasaGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#1e3a8a"/>
      <stop offset="100%" stop-color="#1d4ed8"/>
    </linearGradient>
    <linearGradient id="coreGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#9a3412"/>
      <stop offset="100%" stop-color="#ea580c"/>
    </linearGradient>
    <linearGradient id="calGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#065f46"/>
      <stop offset="100%" stop-color="#059669"/>
    </linearGradient>
    <marker id="arrowBlue" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/>
    </marker>
    <marker id="arrowOrange" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#ea580c"/>
    </marker>
    <marker id="arrowGreen" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#059669"/>
    </marker>
  </defs>

  <rect width="920" height="690" rx="12" fill="url(#bgGrad)" stroke="#cbd5e1" stroke-width="1.5"/>

  <!-- TIER 1: NASA SATELLITE SOURCES -->
  <rect x="22" y="18" width="876" height="106" rx="10" fill="#eff6ff" stroke="#93c5fd" stroke-width="1.5"/>
  <rect x="22" y="18" width="876" height="26" rx="10" fill="url(#nasaGrad)"/>
  <text x="460" y="35" text-anchor="middle" font-size="11" font-weight="700" fill="#ffffff" letter-spacing="0.6">TIER 1: NASA EARTHDATA &amp; LANCE FIRMS SATELLITE OBSERVATION STREAMS (2000–2026+)</text>

  <rect x="38" y="54" width="265" height="58" rx="7" fill="#ffffff" stroke="#60a5fa" stroke-width="1.2"/>
  <text x="170" y="73" text-anchor="middle" font-size="11" font-weight="700" fill="#1e3a8a">MODIS Collection 6.1 (1 km)</text>
  <text x="170" y="89" text-anchor="middle" font-size="9.5" fill="#475569">Terra (2000–2026) &amp; Aqua (2002–2026)</text>
  <text x="170" y="103" text-anchor="middle" font-size="9" font-weight="600" fill="#dc2626">Nadir 1.0 km² → Scan Edge 4.83×2.01 km (9.69 km²)</text>

  <rect x="326" y="54" width="268" height="58" rx="7" fill="#ffffff" stroke="#60a5fa" stroke-width="1.2"/>
  <text x="460" y="73" text-anchor="middle" font-size="11" font-weight="700" fill="#1e3a8a">VIIRS 375m Collection 2</text>
  <text x="460" y="89" text-anchor="middle" font-size="9.5" fill="#475569">Suomi-NPP (2012+), NOAA-20 (2018+), NOAA-21</text>
  <text x="460" y="103" text-anchor="middle" font-size="9" font-weight="600" fill="#059669">3-Zone Aggregation (3:1, 2:1, 1:1) ≤ 0.62 km²</text>

  <rect x="617" y="54" width="265" height="58" rx="7" fill="#ffffff" stroke="#60a5fa" stroke-width="1.2"/>
  <text x="749" y="73" text-anchor="middle" font-size="11" font-weight="700" fill="#1e3a8a">NRT / URT &amp; Science Archives</text>
  <text x="749" y="89" text-anchor="middle" font-size="9.5" fill="#475569">134 Cached CSV Slices + ERA5 Cloud Climatology</text>
  <text x="749" y="103" text-anchor="middle" font-size="9" font-weight="600" fill="#2563eb">Validated on 1,609,182 (1.609.182) Real Detections</text>

  <line x1="170" y1="124" x2="170" y2="148" stroke="#2563eb" stroke-width="2" marker-end="url(#arrowBlue)"/>
  <line x1="460" y1="124" x2="460" y2="148" stroke="#2563eb" stroke-width="2" marker-end="url(#arrowBlue)"/>
  <line x1="749" y1="124" x2="749" y2="148" stroke="#2563eb" stroke-width="2" marker-end="url(#arrowBlue)"/>

  <!-- TIER 2: INGESTION & SCHEMA UNIFICATION -->
  <rect x="22" y="152" width="876" height="78" rx="10" fill="#f0fdf4" stroke="#86efac" stroke-width="1.5"/>
  <text x="40" y="171" font-size="10.5" font-weight="700" fill="#166534">TIER 2: MULTI-STREAM INGESTION &amp; PROVENANCE SEAM (packages/firms-ingestion)</text>

  <rect x="38" y="180" width="410" height="38" rx="6" fill="#ffffff" stroke="#4ade80" stroke-width="1.2"/>
  <text x="243" y="197" text-anchor="middle" font-size="10.5" font-weight="700" fill="#15803d">Rate-Limited NASA FIRMS Adapter &amp; SHA-256 Archive Guard</text>
  <text x="243" y="211" text-anchor="middle" font-size="9" fill="#475569">Seamlessly bridges Standard Processing (SP) &amp; Near-Real-Time (NRT) CSVs</text>

  <rect x="472" y="180" width="410" height="38" rx="6" fill="#ffffff" stroke="#4ade80" stroke-width="1.2"/>
  <text x="677" y="197" text-anchor="middle" font-size="10.5" font-weight="700" fill="#15803d">Cross-Sensor ThermalDetection Schema Unification</text>
  <text x="677" y="211" text-anchor="middle" font-size="9" fill="#475569">Normalizes T4 (4 μm), T5 (11 μm), Scan×Track dimensions, FRP &amp; UTC timestamps</text>

  <line x1="448" y1="199" x2="470" y2="199" stroke="#059669" stroke-width="2" marker-end="url(#arrowGreen)"/>
  <line x1="460" y1="230" x2="460" y2="254" stroke="#ea580c" stroke-width="2.2" marker-end="url(#arrowOrange)"/>

  <!-- TIER 3: 5-STAGE PHYSICS HARMONIZATION ENGINE -->
  <rect x="22" y="258" width="876" height="196" rx="10" fill="#fff7ed" stroke="#fdba74" stroke-width="1.8"/>
  <rect x="22" y="258" width="876" height="26" rx="10" fill="url(#coreGrad)"/>
  <text x="460" y="275" text-anchor="middle" font-size="11" font-weight="700" fill="#ffffff" letter-spacing="0.5">TIER 3: 5-STAGE PHYSICS-GUIDED HARMONIZATION ENGINE (packages/harmonization-core — Zero I/O)</text>

  <rect x="36" y="296" width="160" height="142" rx="8" fill="#ffffff" stroke="#fb923c" stroke-width="1.4"/>
  <rect x="36" y="296" width="160" height="24" rx="8" fill="#ffedd5"/>
  <text x="116" y="312" text-anchor="middle" font-size="9.8" font-weight="700" fill="#9a3412">STAGE 1: Astronomy</text>
  <text x="116" y="332" text-anchor="middle" font-size="9" font-weight="700" fill="#1e293b">SZA &amp; Day/Night Gate</text>
  <text x="116" y="350" text-anchor="middle" font-size="8.5" fill="#475569">Exact spherical solar</text>
  <text x="116" y="364" text-anchor="middle" font-size="8.5" fill="#475569">zenith angle equation</text>
  <text x="116" y="378" text-anchor="middle" font-size="8.5" font-weight="700" fill="#c2410c">SZA(φ, λ, UTC) &lt; 85.0°</text>
  <text x="116" y="396" text-anchor="middle" font-size="8.5" fill="#475569">Eliminates twilight D/N</text>
  <text x="116" y="410" text-anchor="middle" font-size="8.5" fill="#475569">drift across NRT &amp; SP</text>

  <rect x="208" y="296" width="160" height="142" rx="8" fill="#ffffff" stroke="#fb923c" stroke-width="1.4"/>
  <rect x="208" y="296" width="160" height="24" rx="8" fill="#ffedd5"/>
  <text x="288" y="312" text-anchor="middle" font-size="9.8" font-weight="700" fill="#9a3412">STAGE 2: Confidence</text>
  <text x="288" y="332" text-anchor="middle" font-size="9" font-weight="700" fill="#1e293b">P(fire) &amp; SAA Filter</text>
  <text x="288" y="350" text-anchor="middle" font-size="8.5" fill="#475569">Unifies 0–100% &amp; l/n/h</text>
  <text x="288" y="364" text-anchor="middle" font-size="8.5" font-weight="700" fill="#c2410c">→ P(fire) ∈ [0, 1]</text>
  <text x="288" y="382" text-anchor="middle" font-size="8.5" fill="#475569">Rejects 4.63% nighttime</text>
  <text x="288" y="396" text-anchor="middle" font-size="8.5" font-weight="600" fill="#dc2626">SAA proton spikes</text>
  <text x="288" y="410" text-anchor="middle" font-size="8.5" fill="#475569">&amp; static industrial flares</text>

  <rect x="380" y="296" width="160" height="142" rx="8" fill="#ffffff" stroke="#fb923c" stroke-width="1.4"/>
  <rect x="380" y="296" width="160" height="24" rx="8" fill="#ffedd5"/>
  <text x="460" y="312" text-anchor="middle" font-size="9.8" font-weight="700" fill="#9a3412">STAGE 3: Geometry</text>
  <text x="460" y="332" text-anchor="middle" font-size="9" font-weight="700" fill="#1e293b">Scan Ellipse &amp; Uber H3</text>
  <text x="460" y="350" text-anchor="middle" font-size="8.5" fill="#475569">Inverts bow-tie scan θ</text>
  <text x="460" y="364" text-anchor="middle" font-size="8.5" font-weight="700" fill="#c2410c">ΔS(θ) × ΔT(θ), azimuth α</text>
  <text x="460" y="382" text-anchor="middle" font-size="8.5" fill="#475569">13-point quadrature onto</text>
  <text x="460" y="396" text-anchor="middle" font-size="8.5" font-weight="600" fill="#0f766e">Uber H3 Res 7 (5.16 km²)</text>
  <text x="460" y="410" text-anchor="middle" font-size="8.5" font-weight="600" fill="#0f766e">&amp; H3 Res 8 (0.74 km²)</text>

  <rect x="552" y="296" width="160" height="142" rx="8" fill="#ffffff" stroke="#fb923c" stroke-width="1.4"/>
  <rect x="552" y="296" width="160" height="24" rx="8" fill="#ffedd5"/>
  <text x="632" y="312" text-anchor="middle" font-size="9.8" font-weight="700" fill="#9a3412">STAGE 4: Radiometry</text>
  <text x="632" y="332" text-anchor="middle" font-size="9" font-weight="700" fill="#1e293b">Two-Stage FRP Operator</text>
  <text x="632" y="350" text-anchor="middle" font-size="8.5" fill="#475569">Scan detection limit</text>
  <text x="632" y="364" text-anchor="middle" font-size="8.5" font-weight="700" fill="#c2410c">FRP_lim(θ) + Stratified EQM</text>
  <text x="632" y="382" text-anchor="middle" font-size="8.5" fill="#475569">N = 20,786 Aqua–SNPP pairs</text>
  <text x="632" y="396" text-anchor="middle" font-size="8.5" fill="#475569">D_KS: 0.1153 → 0.0353</text>
  <text x="632" y="410" text-anchor="middle" font-size="8.5" font-weight="700" fill="#15803d">-69.4% KS error reduction!</text>

  <rect x="724" y="296" width="160" height="142" rx="8" fill="#ffffff" stroke="#fb923c" stroke-width="1.4"/>
  <rect x="724" y="296" width="160" height="24" rx="8" fill="#ffedd5"/>
  <text x="804" y="312" text-anchor="middle" font-size="9.8" font-weight="700" fill="#9a3412">STAGE 5: Episodes</text>
  <text x="804" y="332" text-anchor="middle" font-size="9" font-weight="700" fill="#1e293b">Deduplication &amp; Effort</text>
  <text x="804" y="350" text-anchor="middle" font-size="8.5" fill="#475569">Spatio-temporal H3 graph</text>
  <text x="804" y="364" text-anchor="middle" font-size="8.5" font-weight="700" fill="#c2410c">τ = 60 min → FireEpisode</text>
  <text x="804" y="382" text-anchor="middle" font-size="8.5" fill="#475569">Observation effort factor</text>
  <text x="804" y="396" text-anchor="middle" font-size="8.5" font-weight="700" fill="#15803d">Ω(y, φ) Normalization</text>
  <text x="804" y="410" text-anchor="middle" font-size="8.5" fill="#475569">Removes +1,311.2% jump</text>

  <line x1="196" y1="367" x2="206" y2="367" stroke="#ea580c" stroke-width="1.8" marker-end="url(#arrowOrange)"/>
  <line x1="368" y1="367" x2="378" y2="367" stroke="#ea580c" stroke-width="1.8" marker-end="url(#arrowOrange)"/>
  <line x1="540" y1="367" x2="550" y2="367" stroke="#ea580c" stroke-width="1.8" marker-end="url(#arrowOrange)"/>
  <line x1="712" y1="367" x2="722" y2="367" stroke="#ea580c" stroke-width="1.8" marker-end="url(#arrowOrange)"/>

  <line x1="460" y1="454" x2="460" y2="478" stroke="#059669" stroke-width="2.2" marker-end="url(#arrowGreen)"/>

  <!-- TIER 4: COGNITIVE HARNESS & CALENDAR ENGINE -->
  <rect x="22" y="482" width="876" height="88" rx="10" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="1.5"/>
  <rect x="22" y="482" width="876" height="24" rx="10" fill="url(#calGrad)"/>
  <text x="460" y="498" text-anchor="middle" font-size="10.5" font-weight="700" fill="#ffffff" letter-spacing="0.5">TIER 4: 26-YEAR BURNING CALENDAR &amp; DUAL-SYSTEM COGNITIVE AI HARNESS (apps/ai-service :5901)</text>

  <rect x="38" y="514" width="410" height="46" rx="6" fill="#ffffff" stroke="#34d399" stroke-width="1.2"/>
  <text x="243" y="532" text-anchor="middle" font-size="10.5" font-weight="700" fill="#065f46">Harmonized Burning Activity Calendar (26 Years × 73 Pentads)</text>
  <text x="243" y="548" text-anchor="middle" font-size="9" fill="#475569">25 Measured Epochs (2001–2025) + 1 Interpolated Year (2026) • HFD, HRF, SFAI</text>

  <rect x="472" y="514" width="410" height="46" rx="6" fill="#ffffff" stroke="#34d399" stroke-width="1.2"/>
  <text x="677" y="532" text-anchor="middle" font-size="10.5" font-weight="700" fill="#065f46">Dual-System LangGraph Harness (15 Use Cases · 18 Registered @tools)</text>
  <text x="677" y="548" text-anchor="middle" font-size="9" font-weight="600" fill="#047857">VerifiedFactsLedger • NumericGroundingVerifier • JWT Human Sign-Off Gate</text>

  <line x1="448" y1="537" x2="470" y2="537" stroke="#059669" stroke-width="2" marker-end="url(#arrowGreen)"/>
  <line x1="460" y1="570" x2="460" y2="594" stroke="#2563eb" stroke-width="2.2" marker-end="url(#arrowBlue)"/>

  <!-- TIER 5: ANALYTICAL WORKBENCH -->
  <rect x="22" y="598" width="876" height="74" rx="10" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="40" y="617" font-size="10.5" font-weight="700" fill="#1e293b">TIER 5: INTERACTIVE NEXT.JS 16 WORKBENCH (apps/workbench :5900) &amp; REPRODUCIBLE EXPORTS</text>

  <rect x="38" y="625" width="265" height="36" rx="6" fill="#ffffff" stroke="#94a3b8" stroke-width="1.2"/>
  <text x="170" y="641" text-anchor="middle" font-size="9.5" font-weight="700" fill="#1e3a8a">Three.js 3D Globe + d3-geo SVG + H3</text>
  <text x="170" y="654" text-anchor="middle" font-size="8.5" fill="#475569">1–64× Pan/Zoom &amp; H3 Res 7/8 Hexagonal Binning</text>

  <rect x="326" y="625" width="268" height="36" rx="6" fill="#ffffff" stroke="#94a3b8" stroke-width="1.2"/>
  <text x="460" y="641" text-anchor="middle" font-size="9.5" font-weight="700" fill="#9a3412">26×73 Pentad Matrix &amp; Live Briefing Rail</text>
  <text x="460" y="654" text-anchor="middle" font-size="8.5" fill="#475569">SSE Streaming &amp; /review Human Sign-Off Queue</text>

  <rect x="617" y="625" width="265" height="36" rx="6" fill="#ffffff" stroke="#94a3b8" stroke-width="1.2"/>
  <text x="749" y="641" text-anchor="middle" font-size="9.5" font-weight="700" fill="#065f46">182 Offline + 6 Live Tests (22 Files)</text>
  <text x="749" y="654" text-anchor="middle" font-size="8.5" fill="#475569">5 300-DPI Figures &amp; 3 English A4 Technical PDFs</text>
</svg>
</div>
"""

PROPOSAL_SEQ_SVG = """
<div class="diagram-container">
<div class="diagram-title">ARCHITECTURE FIGURE 2: END-TO-END SEQUENCE FLOW FOR CROSS-SENSOR HARMONIZATION &amp; 26-YEAR CALENDAR QUERY</div>
<svg viewBox="0 0 920 510" width="660" height="366" style="width:100%; height:auto;" xmlns="http://www.w3.org/2000/svg" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif">
  <defs>
    <marker id="seqArrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#1e40af"/>
    </marker>
    <marker id="seqArrowRet" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#047857"/>
    </marker>
    <marker id="seqArrowCore" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#c2410c"/>
    </marker>
  </defs>

  <rect width="920" height="510" rx="12" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>

  <g transform="translate(30, 18)">
    <rect x="0" y="0" width="135" height="40" rx="7" fill="#1e3a8a"/>
    <text x="67" y="18" text-anchor="middle" font-size="10" font-weight="700" fill="#ffffff">Analyst / Scientist</text>
    <text x="67" y="32" text-anchor="middle" font-size="8.5" fill="#bfdbfe">Workbench (:5900)</text>

    <rect x="180" y="0" width="145" height="40" rx="7" fill="#1d4ed8"/>
    <text x="252" y="18" text-anchor="middle" font-size="10" font-weight="700" fill="#ffffff">FastAPI AI Service</text>
    <text x="252" y="32" text-anchor="middle" font-size="8.5" fill="#bfdbfe">apps/ai-service (:5901)</text>

    <rect x="365" y="0" width="150" height="40" rx="7" fill="#047857"/>
    <text x="440" y="18" text-anchor="middle" font-size="10" font-weight="700" fill="#ffffff">FIRMS Ingestion</text>
    <text x="440" y="32" text-anchor="middle" font-size="8.5" fill="#a7f3d0">134 Cached CSV Slices</text>

    <rect x="555" y="0" width="160" height="40" rx="7" fill="#c2410c"/>
    <text x="635" y="18" text-anchor="middle" font-size="10" font-weight="700" fill="#ffffff">Harmonization Core</text>
    <text x="635" y="32" text-anchor="middle" font-size="8.5" fill="#fed7aa">5 Physics Stages</text>

    <rect x="750" y="0" width="115" height="40" rx="7" fill="#334155"/>
    <text x="807" y="18" text-anchor="middle" font-size="10" font-weight="700" fill="#ffffff">Calendar &amp; Ledger</text>
    <text x="807" y="32" text-anchor="middle" font-size="8.5" fill="#cbd5e1">26×73 + SQLite</text>
  </g>

  <line x1="97" y1="58" x2="97" y2="490" stroke="#94a3b8" stroke-width="1.3" stroke-dasharray="5,4"/>
  <line x1="282" y1="58" x2="282" y2="490" stroke="#94a3b8" stroke-width="1.3" stroke-dasharray="5,4"/>
  <line x1="470" y1="58" x2="470" y2="490" stroke="#94a3b8" stroke-width="1.3" stroke-dasharray="5,4"/>
  <line x1="665" y1="58" x2="665" y2="490" stroke="#94a3b8" stroke-width="1.3" stroke-dasharray="5,4"/>
  <line x1="837" y1="58" x2="837" y2="490" stroke="#94a3b8" stroke-width="1.3" stroke-dasharray="5,4"/>

  <line x1="97" y1="84" x2="278" y2="84" stroke="#1e40af" stroke-width="1.8" marker-end="url(#seqArrow)"/>
  <text x="187" y="77" text-anchor="middle" font-size="9" font-weight="600" fill="#1e3a8a">1. Select Region AOI / Epoch (2001–2026) &amp; Query</text>

  <line x1="282" y1="114" x2="466" y2="114" stroke="#1e40af" stroke-width="1.8" marker-end="url(#seqArrow)"/>
  <text x="374" y="107" text-anchor="middle" font-size="9" font-weight="600" fill="#1e3a8a">2. Load MODIS (SP/NRT) &amp; VIIRS (SNPP/NOAA20/NOAA21) Slices</text>

  <rect x="355" y="124" width="230" height="40" rx="6" fill="#ecfdf5" stroke="#34d399" stroke-width="1.2"/>
  <text x="470" y="140" text-anchor="middle" font-size="8.8" font-weight="700" fill="#065f46">3. Unify Archive &amp; NRT Streams</text>
  <text x="470" y="155" text-anchor="middle" font-size="8.2" fill="#047857">SHA-256 Verified • 1,609,182 Detections</text>

  <line x1="470" y1="176" x2="286" y2="176" stroke="#047857" stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#seqArrowRet)"/>
  <text x="378" y="170" text-anchor="middle" font-size="8.8" font-weight="600" fill="#047857">4. Return Normalized ThermalDetection Records</text>

  <line x1="282" y1="204" x2="661" y2="204" stroke="#c2410c" stroke-width="1.8" marker-end="url(#seqArrowCore)"/>
  <text x="472" y="197" text-anchor="middle" font-size="9" font-weight="700" fill="#9a3412">5. Execute 5-Stage Physics Harmonization &amp; 18 Deterministic @tools</text>

  <rect x="520" y="216" width="290" height="156" rx="8" fill="#fff7ed" stroke="#fb923c" stroke-width="1.5"/>
  <text x="665" y="235" text-anchor="middle" font-size="9.5" font-weight="700" fill="#9a3412">Five-Stage Physical-Statistical Execution:</text>
  <text x="534" y="254" font-size="8.8" fill="#1e293b">• [5a] Astronomical SZA(φ,λ,t) &lt; 85° Day/Night Unification</text>
  <text x="534" y="272" font-size="8.8" fill="#1e293b">• [5b] Unified P(fire) ∈ [0,1] &amp; SAA / Static Flare Filtering</text>
  <text x="534" y="290" font-size="8.8" fill="#1e293b">• [5c] Scan Angle θ → ΔS×ΔT Ellipse → H3 Res 7 &amp; 8 Weights</text>
  <text x="534" y="308" font-size="8.8" fill="#1e293b">• [5d] Two-Stage FRP_lim(θ) + EQM Calibration (D_KS = 0.0353)</text>
  <text x="534" y="326" font-size="8.8" fill="#1e293b">• [5e] Episode Clustering (τ = 60 min) &amp; Effort Ω(y, φ)</text>
  <text x="534" y="344" font-size="8.8" font-weight="700" fill="#c2410c">• [5f] 26 Years × 73 Pentads Matrix (HFD, HRF, SFAI Z-Score)</text>

  <line x1="665" y1="392" x2="833" y2="392" stroke="#1e40af" stroke-width="1.8" marker-end="url(#seqArrow)"/>
  <text x="750" y="385" text-anchor="middle" font-size="8.8" font-weight="600" fill="#1e3a8a">6. Populate VerifiedFactsLedger</text>

  <line x1="837" y1="426" x2="286" y2="426" stroke="#047857" stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#seqArrowRet)"/>
  <text x="560" y="419" text-anchor="middle" font-size="9" font-weight="600" fill="#047857">7. Audit Every Number via NumericGroundingVerifier &amp; JWT Sign-Off Gate</text>

  <line x1="282" y1="460" x2="101" y2="460" stroke="#047857" stroke-width="2" marker-end="url(#seqArrowRet)"/>
  <text x="190" y="453" text-anchor="middle" font-size="9" font-weight="700" fill="#065f46">8. Stream SSE Events, H3 Map &amp; Grounded Briefing</text>
</svg>
</div>
"""

REPORT_ARCH_SVG = PROPOSAL_ARCH_SVG
REPORT_SEQ_SVG = PROPOSAL_SEQ_SVG

# ==============================================================================
# 1C. DEDICATED 8-NODE LANGGRAPH DUAL-SYSTEM COGNITIVE STATEGRAPH VECTOR SVG
# ==============================================================================

LANGGRAPH_FLOW_SVG = """
<div class="diagram-container">
<div class="diagram-title">COGNITIVE ARCHITECTURE FIGURE: 8-NODE LANGGRAPH DUAL-SYSTEM STATEGRAPH (SYSTEM 1 REFLEXIVE + SYSTEM 2 DELIBERATIVE HARNESS)</div>
<svg viewBox="0 0 920 560" width="660" height="402" style="width:100%; height:auto;" xmlns="http://www.w3.org/2000/svg" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif">
  <defs>
    <linearGradient id="s1Grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#1e3a8a"/>
      <stop offset="100%" stop-color="#2563eb"/>
    </linearGradient>
    <linearGradient id="s2Grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#9a3412"/>
      <stop offset="100%" stop-color="#ea580c"/>
    </linearGradient>
    <linearGradient id="gateGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#065f46"/>
      <stop offset="100%" stop-color="#059669"/>
    </linearGradient>
    <marker id="lgBlue" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/>
    </marker>
    <marker id="lgOrange" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#ea580c"/>
    </marker>
    <marker id="lgGreen" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#059669"/>
    </marker>
  </defs>

  <rect width="920" height="560" rx="12" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>

  <!-- SYSTEM 1 REFLEXIVE LAYER -->
  <rect x="22" y="18" width="876" height="128" rx="10" fill="#eff6ff" stroke="#93c5fd" stroke-width="1.5"/>
  <rect x="22" y="18" width="876" height="25" rx="10" fill="url(#s1Grad)"/>
  <text x="460" y="35" text-anchor="middle" font-size="10.5" font-weight="700" fill="#ffffff" letter-spacing="0.5">SYSTEM 1 — REFLEXIVE LAYER (CALIBRATED TRIAGE &amp; ZERO-LLM FAST EXECUTION · 5 USE CASES: UC-S1.1 .. UC-S1.5)</text>

  <rect x="38" y="54" width="415" height="78" rx="8" fill="#ffffff" stroke="#60a5fa" stroke-width="1.3"/>
  <text x="245" y="73" text-anchor="middle" font-size="10.5" font-weight="700" fill="#1e3a8a">Node 1: system1_triage (3-Step Classifier Chain)</text>
  <text x="245" y="90" text-anchor="middle" font-size="9" fill="#334155">1. Primary Decision Model (typed_questions · calibrated logprob)</text>
  <text x="245" y="104" text-anchor="middle" font-size="9" fill="#334155">2. OpenAIStructuredClassifierModel Fallback (self_reported confidence)</text>
  <text x="245" y="118" text-anchor="middle" font-size="8.8" font-weight="600" fill="#1d4ed8">3. Deterministic Regex Extractor (Zero-Network Floor)</text>

  <rect x="485" y="54" width="395" height="78" rx="8" fill="#ffffff" stroke="#60a5fa" stroke-width="1.3"/>
  <text x="682" y="73" text-anchor="middle" font-size="10.5" font-weight="700" fill="#1e3a8a">Node 2: system1_fast_executor (~1.42 ms)</text>
  <text x="682" y="90" text-anchor="middle" font-size="9" fill="#334155">Triggered when Use Case ∈ {UC-S1.1..S1.5} &amp; Confidence ≥ 0.70</text>
  <text x="682" y="104" text-anchor="middle" font-size="9" font-weight="600" fill="#059669">Directly executes 1 mapped Atomic Tool • Zero LLM Prose Generation</text>
  <text x="682" y="118" text-anchor="middle" font-size="8.8" fill="#475569">Populates VerifiedFactsLedger &amp; jumps straight to Numeric Verifier</text>

  <line x1="453" y1="93" x2="483" y2="93" stroke="#2563eb" stroke-width="2" marker-end="url(#lgBlue)"/>
  <line x1="245" y1="132" x2="245" y2="164" stroke="#ea580c" stroke-width="2.2" marker-end="url(#lgOrange)"/>
  <text x="345" y="156" text-anchor="middle" font-size="8.8" font-weight="700" fill="#9a3412">System 2 UC (UC-S2.1..S2.10) or Confidence &lt; 0.70 (Symbiosis Escalation)</text>

  <!-- SYSTEM 2 DELIBERATIVE LAYER -->
  <rect x="22" y="168" width="876" height="184" rx="10" fill="#fff7ed" stroke="#fdba74" stroke-width="1.6"/>
  <rect x="22" y="168" width="876" height="25" rx="10" fill="url(#s2Grad)"/>
  <text x="460" y="185" text-anchor="middle" font-size="10.5" font-weight="700" fill="#ffffff" letter-spacing="0.5">SYSTEM 2 — DELIBERATIVE LAYER (MULTI-STEP SCIENTIFIC REASONING · 10 USE CASES · 18 REGISTERED @TOOLS)</text>

  <rect x="38" y="204" width="265" height="134" rx="8" fill="#ffffff" stroke="#fb923c" stroke-width="1.3"/>
  <text x="170" y="224" text-anchor="middle" font-size="10" font-weight="700" fill="#9a3412">Node 3: system2_planner (ReAct)</text>
  <text x="170" y="242" text-anchor="middle" font-size="8.8" fill="#334155">Autonomous multi-step tool selection</text>
  <text x="170" y="256" text-anchor="middle" font-size="8.8" font-weight="600" fill="#c2410c">across 18 Registered @tool Functions:</text>
  <text x="170" y="272" text-anchor="middle" font-size="8.5" fill="#475569">• 9 Atomic Physics &amp; Lookup Tools</text>
  <text x="170" y="286" text-anchor="middle" font-size="8.5" fill="#475569">• 9 Domain Diagnostic Audit Tools</text>
  <text x="170" y="302" text-anchor="middle" font-size="8.5" fill="#475569">(+1 internal CSV tool off-registry)</text>
  <text x="170" y="320" text-anchor="middle" font-size="8.5" font-weight="700" fill="#dc2626">Zero LLM Math Allowed</text>

  <rect x="328" y="204" width="265" height="62" rx="8" fill="#ffffff" stroke="#fb923c" stroke-width="1.3"/>
  <text x="460" y="223" text-anchor="middle" font-size="9.8" font-weight="700" fill="#9a3412">Node 4: deterministic_tool_node</text>
  <text x="460" y="239" text-anchor="middle" font-size="8.6" fill="#334155">Executes flare_chronos_core functions</text>
  <text x="460" y="253" text-anchor="middle" font-size="8.6" font-weight="600" fill="#065f46">&amp; records every scalar in VerifiedFactsLedger</text>

  <rect x="328" y="276" width="265" height="62" rx="8" fill="#ffffff" stroke="#fb923c" stroke-width="1.3"/>
  <text x="460" y="295" text-anchor="middle" font-size="9.8" font-weight="700" fill="#9a3412">Node 5: clarification_gate</text>
  <text x="460" y="311" text-anchor="middle" font-size="8.6" fill="#334155">Pauses run &amp; emits clarification_requested</text>
  <text x="460" y="325" text-anchor="middle" font-size="8.6" fill="#475569">when region / epoch / sensor is ambiguous</text>

  <rect x="618" y="204" width="262" height="134" rx="8" fill="#ffffff" stroke="#fb923c" stroke-width="1.3"/>
  <text x="749" y="224" text-anchor="middle" font-size="10" font-weight="700" fill="#9a3412">Node 6: grounded_synthesizer</text>
  <text x="749" y="244" text-anchor="middle" font-size="8.8" fill="#334155">Authors stakeholder-tailored narrative</text>
  <text x="749" y="260" text-anchor="middle" font-size="8.8" font-weight="700" fill="#c2410c">using {{cite:FACT_ID}} placeholders</text>
  <text x="749" y="278" text-anchor="middle" font-size="8.5" fill="#475569">Harness deterministically injects exact</text>
  <text x="749" y="292" text-anchor="middle" font-size="8.5" fill="#475569">verified values &amp; units from Ledger</text>
  <text x="749" y="314" text-anchor="middle" font-size="8.5" font-weight="600" fill="#0f766e">Stakeholders: Field Ranger / Ministry /</text>
  <text x="749" y="327" text-anchor="middle" font-size="8.5" font-weight="600" fill="#0f766e">Climate Scientist</text>

  <line x1="303" y1="235" x2="326" y2="235" stroke="#ea580c" stroke-width="1.8" marker-end="url(#lgOrange)"/>
  <line x1="303" y1="307" x2="326" y2="307" stroke="#ea580c" stroke-width="1.8" marker-end="url(#lgOrange)"/>
  <line x1="593" y1="235" x2="616" y2="235" stroke="#ea580c" stroke-width="1.8" marker-end="url(#lgOrange)"/>
  <line x1="749" y1="352" x2="749" y2="378" stroke="#059669" stroke-width="2.2" marker-end="url(#lgGreen)"/>

  <!-- VERIFICATION, HUMAN SIGN-OFF & SYMBIOSIS -->
  <rect x="22" y="382" width="876" height="160" rx="10" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="1.6"/>
  <rect x="22" y="382" width="876" height="25" rx="10" fill="url(#gateGrad)"/>
  <text x="460" y="399" text-anchor="middle" font-size="10.5" font-weight="700" fill="#ffffff" letter-spacing="0.5">VERIFICATION, IDENTITY-BOUND HUMAN SIGN-OFF GATE &amp; DUAL-PROCESS SYMBIOSIS (15/15 PASS · 0 UNVERIFIED NUMBERS)</text>

  <rect x="38" y="418" width="265" height="110" rx="8" fill="#ffffff" stroke="#34d399" stroke-width="1.3"/>
  <text x="170" y="438" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">Node 7: numeric_verifier</text>
  <text x="170" y="456" text-anchor="middle" font-size="8.6" fill="#334155">Extracts every number in draft prose &amp;</text>
  <text x="170" y="470" text-anchor="middle" font-size="8.6" fill="#334155">matches against VerifiedFactsLedger.</text>
  <text x="170" y="488" text-anchor="middle" font-size="8.6" font-weight="600" fill="#dc2626">Unverified number → Up to 2 rewrites</text>
  <text x="170" y="502" text-anchor="middle" font-size="8.6" font-weight="600" fill="#047857">→ Deterministic Grounded Floor</text>

  <rect x="328" y="418" width="265" height="110" rx="8" fill="#ffffff" stroke="#34d399" stroke-width="1.3"/>
  <text x="460" y="438" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">Node 8: human_sign_off_gate</text>
  <text x="460" y="456" text-anchor="middle" font-size="8.6" fill="#334155">Pauses UC-S1.4, UC-S2.6, UC-S2.9, UC-S2.10</text>
  <text x="460" y="470" text-anchor="middle" font-size="8.6" font-weight="600" fill="#1e3a8a">Requires Bearer JWT Sign-off Principal</text>
  <text x="460" y="488" text-anchor="middle" font-size="8.6" fill="#047857">Approved → Published | Rejected → Withheld</text>
  <text x="460" y="502" text-anchor="middle" font-size="8.5" fill="#475569">Append-Only SQLite Audit Trigger Guard</text>

  <rect x="618" y="418" width="262" height="110" rx="8" fill="#ffffff" stroke="#34d399" stroke-width="1.3"/>
  <text x="749" y="438" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">Node 9: symbiosis_distiller &amp; SSE</text>
  <text x="749" y="456" text-anchor="middle" font-size="8.6" fill="#334155">Distills verified System 2 patterns into</text>
  <text x="749" y="470" text-anchor="middle" font-size="8.6" fill="#334155">System 1 Reflexive Cache (TTL 3600s)</text>
  <text x="749" y="488" text-anchor="middle" font-size="8.6" font-weight="700" fill="#059669">Streams Typed SSE to Workbench (:5900)</text>
  <text x="749" y="502" text-anchor="middle" font-size="8.5" fill="#475569">FastAPI ASGI Service (:5901)</text>

  <line x1="303" y1="473" x2="326" y2="473" stroke="#059669" stroke-width="1.8" marker-end="url(#lgGreen)"/>
  <line x1="593" y1="473" x2="616" y2="473" stroke="#059669" stroke-width="1.8" marker-end="url(#lgGreen)"/>
</svg>
</div>
"""


# ==============================================================================
# 2. LATEX MATH & GITHUB ALERT PREPROCESSOR FOR WEASYPRINT HTML5
# ==============================================================================

GREEK_AND_SYMBOLS: list[tuple[str, str]] = [
    (r"\\left\[", "["),
    (r"\\right\]", "]"),
    (r"\\left\(", "("),
    (r"\\right\)", ")"),
    (r"\\left\\\{", "{"),
    (r"\\right\\\}", "}"),
    (r"\\left\{", "{"),
    (r"\\right\}", "}"),
    (r"\\left\|", "|"),
    (r"\\right\|", "|"),
    (r"\\\{", "{"),
    (r"\\\}", "}"),
    (r"\\Delta(?![a-zA-Z])", "Δ"),
    (r"\\theta(?![a-zA-Z])", "θ"),
    (r"\\phi(?![a-zA-Z])", "φ"),
    (r"\\lambda(?![a-zA-Z])", "λ"),
    (r"\\omega(?![a-zA-Z])", "ω"),
    (r"\\Omega(?![a-zA-Z])", "Ω"),
    (r"\\tau(?![a-zA-Z])", "τ"),
    (r"\\sigma(?![a-zA-Z])", "σ"),
    (r"\\alpha(?![a-zA-Z])", "α"),
    (r"\\beta(?![a-zA-Z])", "β"),
    (r"\\gamma(?![a-zA-Z])", "γ"),
    (r"\\kappa(?![a-zA-Z])", "κ"),
    (r"\\psi(?![a-zA-Z])", "ψ"),
    (r"\\pi(?![a-zA-Z])", "π"),
    (r"\\mu(?![a-zA-Z])", "μ"),
    (r"\\delta(?![a-zA-Z])", "δ"),
    (r"\\epsilon(?![a-zA-Z])", "ε"),
    (r"\\mathcal\{H\}", "ℋ"),
    (r"\\mathcal\{E\}", "ℰ"),
    (r"\\mathcal\{Y\}", "𝒴"),
    (r"\\times(?![a-zA-Z])", " × "),
    (r"\\cdot(?![a-zA-Z])", " · "),
    (r"\\leq?(?![a-zA-Z])", " ≤ "),
    (r"\\geq?(?![a-zA-Z])", " ≥ "),
    (r"\\neq(?![a-zA-Z])", " ≠ "),
    (r"\\equiv(?![a-zA-Z])", " ≡ "),
    (r"\\approx(?![a-zA-Z])", " ≈ "),
    (r"\\sim(?![a-zA-Z])", "∼"),
    (r"\\to(?![a-zA-Z])", " → "),
    (r"\\implies(?![a-zA-Z])", " ⇒ "),
    (r"\\iff(?![a-zA-Z])", " ⇔ "),
    (r"\\in(?![a-zA-Z])", " ∈ "),
    (r"\\pm(?![a-zA-Z])", "±"),
    (r"\\sum(?![a-zA-Z])", "∑"),
    (r"\\prod(?![a-zA-Z])", "∏"),
    (r"\\infty(?![a-zA-Z])", "∞"),
    (r"\\circ(?![a-zA-Z])", "°"),
    (r"\\,", " "),
    (r"\\!", ""),
    (r"\\quad(?![a-zA-Z])", " &nbsp;&nbsp; "),
    (r"\\qquad(?![a-zA-Z])", " &nbsp;&nbsp;&nbsp;&nbsp; "),
    (r"\\max(?![a-zA-Z])", "max"),
    (r"\\min(?![a-zA-Z])", "min"),
    (r"\\ln(?![a-zA-Z])", "ln"),
    (r"\\exp(?![a-zA-Z])", "exp"),
    (r"\\sin(?![a-zA-Z])", "sin"),
    (r"\\cos(?![a-zA-Z])", "cos"),
    (r"\\arcsin(?![a-zA-Z])", "arcsin"),
    (r"\\arccos(?![a-zA-Z])", "arccos"),
    (r"\\tanh(?![a-zA-Z])", "tanh"),
    (r"\\bmod(?![a-zA-Z])", " mod "),
]


def _convert_latex_expr_to_html(expr: str) -> str:
    """Convert a single LaTeX mathematical expression into clean typographic HTML for WeasyPrint."""
    s = expr.strip()

    if r"\begin{cases}" in s:
        inner = s.split(r"\begin{cases}", 1)[1].split(r"\end{cases}", 1)[0]
        rows = [r.strip() for r in inner.split(r"\\") if r.strip()]
        formatted_rows = []
        for row in rows:
            parts = [p.strip() for p in row.split("&")]
            converted_parts = [_convert_latex_expr_to_html(p) for p in parts]
            formatted_rows.append(" &nbsp; ".join(converted_parts))
        cases_html = "{ " + " ; &nbsp; ".join(formatted_rows) + " }"
        prefix = _convert_latex_expr_to_html(s.split(r"\begin{cases}", 1)[0])
        return f"{prefix} {cases_html}"

    s = s.replace("<", "&lt;").replace(">", "&gt;")

    for pattern, repl in GREEK_AND_SYMBOLS:
        s = re.sub(pattern, repl, s)

    for _ in range(3):
        s = re.sub(r"\\text\{([^{}]*)\}", r"\1", s)

    for _ in range(3):
        s = re.sub(r"\\(?:widehat|widetilde)\{([^{}]+)\}", r"\1̂", s)
        s = re.sub(r"\\bar\{([^{}]+)\}", r"\1̄", s)

    for _ in range(4):
        s = re.sub(r"_\{([^{}]+)\}", r"<sub>\1</sub>", s)
        s = re.sub(r"\^\{([^{}]+)\}", r"<sup>\1</sup>", s)

    s = re.sub(r"_([a-zA-Z0-9φθλkijp0])", r"<sub>\1</sub>", s)
    s = re.sub(r"\^([a-zA-Z0-9234°\-\+])", r"<sup>\1</sup>", s)

    for _ in range(4):
        s = re.sub(r"\\sqrt\{([^{}]+)\}", r"√(\1)", s)
        s = re.sub(
            r"\\frac\{([^{}]+)\}\{([^{}]+)\}",
            r"<span class='math-frac'>(\1) / (\2)</span>",
            s,
        )

    s = s.replace(r"\%", "%").replace("{", "").replace("}", "")
    return s


def _render_svg_container_as_data_uri(container_html: str) -> str:
    """Convert inline <svg>...</svg> inside .diagram-container into a base64 SVG <img> so WeasyPrint renders full vector graphics."""
    svg_match = re.search(r"(<svg\b.*?</svg>)", container_html, flags=re.DOTALL)
    if not svg_match:
        return container_html
    raw_svg = svg_match.group(1)
    b64_svg = base64.b64encode(raw_svg.encode("utf-8")).decode("ascii")
    img_tag = (
        f'<img class="vector-diagram-img" src="data:image/svg+xml;base64,{b64_svg}" '
        f'style="width:100%; height:auto; border:none; margin:0; display:block;" />'
    )
    return container_html.replace(raw_svg, img_tag)


def preprocess_markdown_for_weasyprint(
    md_content: str, workspace_root: Path, is_report: bool = False
) -> tuple[str, dict[str, str]]:
    """Replace Mermaid blocks with purpose-specific vector SVGs, format GitHub alerts, and convert LaTeX math."""
    html_injections: dict[str, str] = {}
    arch_svg = REPORT_ARCH_SVG if is_report else PROPOSAL_ARCH_SVG
    seq_svg = REPORT_SEQ_SVG if is_report else PROPOSAL_SEQ_SVG

    def mermaid_replacer(match: re.Match[str]) -> str:
        code = match.group(1)
        token = f"SVGDIAGRAMPLACEHOLDER{len(html_injections)}END"
        if "system1_triage" in code or "System 1" in code:
            html_injections[token] = _render_svg_container_as_data_uri(
                LANGGRAPH_FLOW_SVG
            )
            return f"\n\n{token}\n\n"
        if "flowchart" in code:
            html_injections[token] = _render_svg_container_as_data_uri(arch_svg)
            return f"\n\n{token}\n\n"
        if "sequenceDiagram" in code:
            html_injections[token] = _render_svg_container_as_data_uri(seq_svg)
            return f"\n\n{token}\n\n"
        return match.group(0)

    md_content = re.sub(
        r"```mermaid\n(.*?)\n```", mermaid_replacer, md_content, flags=re.DOTALL
    )

    def alert_replacer(match: re.Match[str]) -> str:
        alert_type = match.group(1).upper()
        body_lines = match.group(2).strip().splitlines()
        cleaned_lines = [re.sub(r"^>\s?", "", line) for line in body_lines]
        body_text = " ".join(cleaned_lines)
        badge_map = {
            "IMPORTANT": (
                "KEY SCIENTIFIC & EMPIRICAL FINDING",
                "callout-important",
            ),
            "NOTE": ("TECHNICAL & ARCHITECTURAL NOTE", "callout-note"),
            "WARNING": ("PHYSICAL & OPERATIONAL WARNING", "callout-warning"),
            "TIP": ("OPERATIONAL RECOMMENDATION", "callout-tip"),
        }
        title, css_cls = badge_map.get(alert_type, (alert_type, "callout-important"))
        return (
            f"\n<div class='callout-box {css_cls}'>"
            f"<div class='callout-header'>⚡ {title}</div>"
            f"<div class='callout-body'>\n\n{body_text}\n\n</div>"
            f"</div>\n"
        )

    md_content = re.sub(
        r"^>\s*\[!(IMPORTANT|NOTE|WARNING|TIP)\]\s*\n((?:^>.*\n?)+)",
        alert_replacer,
        md_content,
        flags=re.MULTILINE,
    )

    protected_blocks: list[str] = []

    def _stash_code(match: re.Match[str]) -> str:
        idx = len(protected_blocks)
        protected_blocks.append(match.group(0))
        return f"@@CODE_BLOCK_{idx}@@"

    md_content = re.sub(r"```.*?```", _stash_code, md_content, flags=re.DOTALL)
    md_content = re.sub(r"`[^`\n]+`", _stash_code, md_content)

    def _display_math_repl(match: re.Match[str]) -> str:
        html_math = _convert_latex_expr_to_html(match.group(1))
        return f"\n<div class='math-block'>{html_math}</div>\n"

    md_content = re.sub(
        r"\$\$(.*?)\$\$", _display_math_repl, md_content, flags=re.DOTALL
    )

    def _inline_math_repl(match: re.Match[str]) -> str:
        inner = match.group(1)
        html_math = _convert_latex_expr_to_html(inner)
        return f"<span class='math-inline'>{html_math}</span>"

    md_content = re.sub(r"(?<!\$)\$([^\$\n]+?)\$(?!\$)", _inline_math_repl, md_content)

    for idx, block in enumerate(protected_blocks):
        md_content = md_content.replace(f"@@CODE_BLOCK_{idx}@@", block)

    docs_dir = (workspace_root / "docs").resolve()
    figures_dir = (docs_dir / "figures").resolve()
    workbench_public_dir = (workspace_root / "apps" / "workbench" / "public").resolve()
    md_content = (
        md_content.replace("](docs/figures/", f"](file://{figures_dir}/")
        .replace("](../docs/figures/", f"](file://{figures_dir}/")
        .replace("](apps/workbench/public/", f"](file://{workbench_public_dir}/")
        .replace("](../apps/workbench/public/", f"](file://{workbench_public_dir}/")
        .replace('src="docs/figures/', f'src="file://{figures_dir}/')
        .replace('src="../docs/figures/', f'src="file://{figures_dir}/')
        .replace("](docs/logo.svg)", f"](file://{docs_dir}/logo.svg)")
        .replace("](../docs/logo.svg)", f"](file://{docs_dir}/logo.svg)")
    )

    return md_content, html_injections


# ==============================================================================
# 3. PROFESSIONAL A4 CSS TEMPLATE (SCIENTIFIC TYPOGRAPHY)
# ==============================================================================

CSS_CONTENT = """
@page {
    size: A4 portrait;
    margin: 18mm 14mm 18mm 14mm;
    @top-left {
        content: "FLARE-CHRONOS — 2026 NASA SPACE APPS CHALLENGE (MODIS & VIIRS HARMONIZATION)";
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-size: 7.5pt;
        font-weight: 700;
        color: #64748b;
        letter-spacing: 0.4px;
    }
    @bottom-left {
        content: "© 2026 Lê Thành Trung • Flare-Chronos Scientific Harmonization System";
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-size: 7.5pt;
        color: #94a3b8;
    }
    @bottom-right {
        content: "Page " counter(page) " / " counter(pages);
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-size: 7.5pt;
        font-weight: 600;
        color: #64748b;
    }
}

@page :first {
    @top-left { content: none; }
}

body {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 9.4pt;
    line-height: 1.54;
    color: #1e293b;
    margin: 0;
    padding: 0;
}

.cover-badge {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #c2410c 100%);
    color: #ffffff;
    padding: 7px 14px;
    border-radius: 6px;
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 0.9px;
    text-transform: uppercase;
    display: inline-block;
    margin-bottom: 8px;
}

.brand-logo-container {
    text-align: center;
    margin: 4px 0 8px 0;
    page-break-inside: avoid;
    page-break-after: avoid;
}

img.brand-logo-img {
    width: 175px;
    max-width: 175px;
    height: auto;
    display: block;
    margin: 0 auto;
    border: none;
    border-radius: 10px;
}

h1 {
    font-size: 16.5pt;
    font-weight: 800;
    color: #0f172a;
    margin-top: 6px;
    margin-bottom: 10px;
    line-height: 1.25;
    border-bottom: 2.5px solid #ea580c;
    padding-bottom: 8px;
    page-break-after: avoid;
}

h2 {
    font-size: 12.2pt;
    font-weight: 700;
    color: #1e3a8a;
    margin-top: 18px;
    margin-bottom: 8px;
    padding: 5px 10px;
    background: linear-gradient(90deg, #eff6ff 0%, #f8fafc 100%);
    border-left: 4px solid #2563eb;
    border-radius: 0 6px 6px 0;
    page-break-after: avoid;
}

h3 {
    font-size: 10.5pt;
    font-weight: 700;
    color: #0f172a;
    margin-top: 13px;
    margin-bottom: 5px;
    page-break-after: avoid;
}

h4 {
    font-size: 9.6pt;
    font-weight: 600;
    color: #334155;
    margin-top: 9px;
    margin-bottom: 4px;
    page-break-after: avoid;
}

p {
    margin-top: 0;
    margin-bottom: 7px;
    text-align: justify;
}

a {
    color: #1d4ed8;
    text-decoration: none;
}

blockquote {
    margin: 8px 0 12px 0;
    padding: 10px 14px;
    background-color: #f8fafc;
    border-left: 4px solid #0284c7;
    border-radius: 0 8px 8px 0;
    color: #334155;
    font-size: 9pt;
}

blockquote p {
    margin-bottom: 3px;
    text-align: left;
}

.callout-box {
    margin: 10px 0 12px 0;
    padding: 10px 14px;
    border-radius: 8px;
    page-break-inside: avoid;
}

.callout-important {
    background-color: #fff7ed;
    border: 1.2px solid #fdba74;
    border-left: 5px solid #ea580c;
}

.callout-note {
    background-color: #eff6ff;
    border: 1.2px solid #93c5fd;
    border-left: 5px solid #2563eb;
}

.callout-header {
    font-size: 8.8pt;
    font-weight: 800;
    color: #9a3412;
    letter-spacing: 0.4px;
    margin-bottom: 4px;
}

.callout-body p {
    margin: 0;
    font-size: 9pt;
    color: #1e293b;
}

.math-block {
    margin: 8px 0 10px 0;
    padding: 8px 14px;
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 3.5px solid #1e3a8a;
    border-radius: 6px;
    font-family: "Helvetica Neue", Georgia, serif;
    font-size: 9.6pt;
    font-weight: 600;
    color: #0f172a;
    text-align: center;
    page-break-inside: avoid;
}

.math-inline {
    font-family: "Helvetica Neue", Georgia, serif;
    font-weight: 600;
    color: #0f172a;
    white-space: nowrap;
}

.math-rom {
    font-style: normal;
    font-weight: 600;
}

.math-frac {
    display: inline-block;
    padding: 0 2px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 9px 0 13px 0;
    font-size: 8.1pt;
    line-height: 1.38;
    table-layout: auto;
    page-break-inside: auto;
}

tr {
    page-break-inside: avoid;
    page-break-after: auto;
}

thead {
    display: table-header-group;
}

th {
    background-color: #0f172a;
    color: #ffffff;
    font-weight: 700;
    text-align: left;
    padding: 6px 7px;
    border: 1px solid #0f172a;
}

td {
    padding: 5.5px 7px;
    border: 1px solid #cbd5e1;
    vertical-align: top;
    overflow-wrap: break-word;
    word-wrap: break-word;
}

tbody tr:nth-child(even) {
    background-color: #f8fafc;
}

code {
    font-family: "Courier New", "Helvetica Neue", monospace;
    font-size: 8.2pt;
    font-weight: 600;
    background-color: #f1f5f9;
    color: #0f172a;
    padding: 1.5px 4px;
    border-radius: 3px;
    border: 1px solid #e2e8f0;
}

pre {
    background-color: #0f172a;
    color: #f8fafc;
    padding: 9px 11px;
    border-radius: 7px;
    font-family: "Courier New", "Helvetica Neue", monospace;
    font-size: 7.5pt;
    font-weight: 600;
    line-height: 1.38;
    white-space: pre-wrap;
    word-wrap: break-word;
    margin: 7px 0 11px 0;
    page-break-inside: avoid;
    border: 1px solid #1e293b;
}

pre code {
    background-color: transparent;
    color: inherit;
    padding: 0;
    border: none;
    font-size: inherit;
}

ul, ol {
    margin-top: 3px;
    margin-bottom: 8px;
    padding-left: 18px;
}

li {
    margin-bottom: 3.5px;
}

hr {
    border: none;
    border-top: 1px solid #cbd5e1;
    margin: 14px 0;
}

.diagram-container {
    margin: 12px 0 15px 0;
    padding: 9px;
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 9px;
    page-break-inside: avoid;
    text-align: center;
}

.diagram-title {
    font-size: 8.3pt;
    font-weight: 700;
    color: #1e3a8a;
    margin-bottom: 7px;
    letter-spacing: 0.4px;
    text-transform: uppercase;
}

img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 10px auto;
    border: 1px solid #cbd5e1;
    border-radius: 7px;
    page-break-inside: avoid;
}

figure {
    margin: 10px 0 14px 0;
    text-align: center;
    page-break-inside: avoid;
}

figcaption {
    font-size: 8pt;
    font-weight: 600;
    color: #475569;
    margin-top: 4px;
}

.watermark-overlay {
    position: fixed;
    top: 46%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-33deg);
    z-index: 9999;
    pointer-events: none;
    text-align: center;
    white-space: nowrap;
    opacity: 0.055;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    color: #0f172a;
    border: 2.5px solid #0f172a;
    padding: 12px 28px;
    border-radius: 10px;
}

.watermark-overlay .wm-name {
    font-size: 26pt;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    display: block;
}

.watermark-overlay .wm-email {
    font-size: 13pt;
    font-weight: 600;
    letter-spacing: 0.8px;
    display: block;
    margin-top: 4px;
}
"""


def build_pdf(
    md_path: Path,
    pdf_path: Path,
    watermark_name: str = "Lê Thành Trung",
    watermark_email: str = "lethanhtrung.trungle@gmail.com",
) -> None:
    """Convert a Markdown proposal, report, or model-flow file into a high-resolution A4 PDF."""
    workspace_root = Path(__file__).resolve().parents[1]
    stem_upper = md_path.stem.upper()
    is_report = "REPORT" in stem_upper
    is_model_flow = "MODEL_FLOW" in stem_upper

    print(f"[1/4] Preprocessing Markdown document: {md_path.name}...")
    raw_md = md_path.read_text(encoding="utf-8")
    processed_md, html_injections = preprocess_markdown_for_weasyprint(
        raw_md, workspace_root, is_report=is_report
    )

    tmp_dir = Path(tempfile.gettempdir())
    temp_md = tmp_dir / f".temp_{md_path.stem}.md"
    temp_html = tmp_dir / f".temp_{md_path.stem}.html"
    temp_css = tmp_dir / ".temp_pdf_style.css"

    temp_md.write_text(processed_md, encoding="utf-8")
    temp_css.write_text(CSS_CONTENT, encoding="utf-8")

    print("[2/4] Compiling Markdown to HTML5 via Pandoc...")
    pandoc_cmd = [
        _resolve_binary("pandoc"),
        str(temp_md),
        "-f",
        "markdown+gfm_auto_identifiers+fenced_divs+pipe_tables+backtick_code_blocks-tex_math_dollars",
        "-t",
        "html5",
        "--syntax-highlighting=pygments",
        "-o",
        str(temp_html),
    ]
    res = subprocess.run(pandoc_cmd, capture_output=True, text=True, check=False)  # noqa: S603
    if res.returncode != 0:
        pandoc_cmd = [
            _resolve_binary("pandoc"),
            str(temp_md),
            "-f",
            "markdown-tex_math_dollars",
            "-t",
            "html5",
            "--highlight-style=pygments",
            "-o",
            str(temp_html),
        ]
        subprocess.run(pandoc_cmd, check=True)  # noqa: S603

    body_html = temp_html.read_text(encoding="utf-8")
    for token, svg_html in html_injections.items():
        body_html = body_html.replace(f"<p>{token}</p>", svg_html).replace(
            token, svg_html
        )

    safe_name = html.escape(watermark_name.strip())
    safe_email = html.escape(watermark_email.strip())
    if is_model_flow:
        doc_role = "Dual-System Cognitive Model Flow"
        badge_text = "2026 NASA SPACE APPS CHALLENGE • DUAL-SYSTEM COGNITIVE MODEL FLOW — FLARE-CHRONOS"
    elif is_report:
        doc_role = "Codebase & Empirical Report"
        badge_text = "2026 NASA SPACE APPS CHALLENGE • CODEBASE ARCHITECTURE & EMPIRICAL REPORT — FLARE-CHRONOS"
    else:
        doc_role = "Official Technical Proposal"
        badge_text = "2026 NASA SPACE APPS CHALLENGE • OFFICIAL TECHNICAL PROPOSAL — FLARE-CHRONOS"

    watermark_block = ""
    if safe_name or safe_email:
        watermark_block = f"""
  <div class="watermark-overlay">
    <span class="wm-name">{safe_name} • FLARE-CHRONOS</span>
    <span class="wm-email">{safe_email} • {doc_role}</span>
  </div>"""

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Flare-Chronos — {html.escape(md_path.stem)}</title>
  <link rel="stylesheet" href="{temp_css.resolve().as_uri()}"/>
</head>
<body>{watermark_block}
  <div class="cover-badge">{badge_text}</div>
  {body_html}
</body>
</html>
"""
    temp_html.write_text(full_html, encoding="utf-8")

    print(
        f"[3/4] Rendering high-resolution vector A4 PDF via WeasyPrint -> {pdf_path.name}..."
    )
    weasy_cmd = [
        _resolve_binary("weasyprint"),
        "--base-url",
        str(workspace_root.resolve()),
        str(temp_html),
        str(pdf_path),
    ]
    subprocess.run(weasy_cmd, check=True)  # noqa: S603

    for tmp in (temp_md, temp_html, temp_css):
        if tmp.exists():
            os.remove(tmp)

    size_kb = pdf_path.stat().st_size / 1024.0
    print(f"[4/4] Successfully exported PDF: {pdf_path} ({size_kb:.1f} KB)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export PROPOSAL.md, REPORT.md, and MODEL_FLOW.md to A4 PDFs with vector SVG diagrams."
    )
    parser.add_argument(
        "-i",
        "--input",
        default=None,
        help="Input Markdown file path (default: exports PROPOSAL.md, REPORT.md, and MODEL_FLOW.md).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output PDF file path.",
    )
    parser.add_argument(
        "--watermark-name",
        default="Lê Thành Trung",
        help="Author name displayed on the diagonal watermark.",
    )
    parser.add_argument(
        "--watermark-email",
        default="lethanhtrung.trungle@gmail.com",
        help="Author email displayed on the diagonal watermark.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    exports_dir = Path(__file__).resolve().parent

    if args.input:
        in_path = Path(args.input).resolve()
        out_path = (
            Path(args.output).resolve() if args.output else in_path.with_suffix(".pdf")
        )
        build_pdf(
            md_path=in_path,
            pdf_path=out_path,
            watermark_name=args.watermark_name,
            watermark_email=args.watermark_email,
        )
    else:
        for fname in ("PROPOSAL.md", "REPORT.md", "MODEL_FLOW.md"):
            md_file = exports_dir / fname
            if md_file.exists():
                pdf_file = md_file.with_suffix(".pdf")
                build_pdf(
                    md_path=md_file,
                    pdf_path=pdf_file,
                    watermark_name=args.watermark_name,
                    watermark_email=args.watermark_email,
                )
