#!/usr/bin/env python3
"""
A4 PDF exporter for the Flare-Chronos submission:
1. exports/PROPOSAL.md -> exports/PROPOSAL.pdf (technical proposal)
2. exports/REPORT.md   -> exports/REPORT.pdf   (engineering and model report)

Uses Pandoc and WeasyPrint with one simple typographic style, a vector 8-node
LangGraph figure, a LaTeX-to-HTML math renderer, and GitHub alert formatting.
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
import unicodedata
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
# 1. 8-NODE LANGGRAPH DUAL-SYSTEM COGNITIVE STATEGRAPH VECTOR SVG
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
  <rect x="22" y="18" width="876" height="132" rx="10" fill="#eff6ff" stroke="#93c5fd" stroke-width="1.5"/>
  <rect x="22" y="18" width="876" height="25" rx="10" fill="url(#s1Grad)"/>
  <text x="460" y="35" text-anchor="middle" font-size="10.5" font-weight="700" fill="#ffffff" letter-spacing="0.5">SYSTEM 1 — REFLEXIVE LAYER (5 USE CASES: UC-S1.1 .. UC-S1.5)</text>

  <rect x="38" y="54" width="410" height="86" rx="8" fill="#ffffff" stroke="#60a5fa" stroke-width="1.3"/>
  <text x="243" y="74" text-anchor="middle" font-size="10.5" font-weight="700" fill="#1e3a8a">Node 1: system1_triage_node</text>
  <text x="243" y="92" text-anchor="middle" font-size="8.8" fill="#334155">1. Decision model (typed_questions, calibrated logprob)</text>
  <text x="243" y="107" text-anchor="middle" font-size="8.8" fill="#334155">2. Structured chat fallback (self_reported confidence)</text>
  <text x="243" y="122" text-anchor="middle" font-size="8.8" font-weight="600" fill="#1d4ed8">3. Deterministic regex floor (zero network)</text>

  <rect x="472" y="54" width="410" height="86" rx="8" fill="#ffffff" stroke="#60a5fa" stroke-width="1.3"/>
  <text x="677" y="74" text-anchor="middle" font-size="10.5" font-weight="700" fill="#1e3a8a">Node 2: system1_fast_node</text>
  <text x="677" y="92" text-anchor="middle" font-size="8.8" fill="#334155">One Atomic Tool · zero LLM prose generation</text>
  <text x="677" y="107" text-anchor="middle" font-size="8.8" font-weight="600" fill="#059669">Runs in ~1–5 ms across UC-S1.1 .. UC-S1.5</text>
  <text x="677" y="122" text-anchor="middle" font-size="8.8" fill="#475569">Routes to the tool node or the numeric verifier</text>

  <line x1="450" y1="97" x2="470" y2="97" stroke="#2563eb" stroke-width="2" marker-end="url(#lgBlue)"/>

  <!-- SYSTEM 1 TO SYSTEM 2 ESCALATION -->
  <line x1="170" y1="140" x2="170" y2="172" stroke="#ea580c" stroke-width="2.2" marker-end="url(#lgOrange)"/>
  <text x="182" y="164" text-anchor="start" font-size="8.8" font-weight="700" fill="#9a3412">System 2 use case, or confidence &lt; 0.70</text>

  <!-- SYSTEM 2 DELIBERATIVE LAYER -->
  <rect x="22" y="176" width="876" height="180" rx="10" fill="#fff7ed" stroke="#fdba74" stroke-width="1.6"/>
  <rect x="22" y="176" width="876" height="25" rx="10" fill="url(#s2Grad)"/>
  <text x="460" y="193" text-anchor="middle" font-size="10.5" font-weight="700" fill="#ffffff" letter-spacing="0.5">SYSTEM 2 — DELIBERATIVE LAYER (10 USE CASES · 18 REGISTERED @TOOLS)</text>

  <rect x="38" y="212" width="410" height="132" rx="8" fill="#ffffff" stroke="#fb923c" stroke-width="1.3"/>
  <text x="243" y="232" text-anchor="middle" font-size="10.2" font-weight="700" fill="#9a3412">Node 3: system2_agent_node</text>
  <text x="243" y="250" text-anchor="middle" font-size="8.6" fill="#334155">ReAct planner across 18 @tools (9 atomic + 9 diagnostic)</text>
  <text x="243" y="266" text-anchor="middle" font-size="8.6" fill="#334155">Clarification is handled inside this node (max 2 questions)</text>
  <text x="243" y="282" text-anchor="middle" font-size="8.6" font-weight="600" fill="#c2410c">Grounded synthesis with {{cite:FACT_ID}} placeholders</text>
  <text x="243" y="300" text-anchor="middle" font-size="8.6" fill="#475569">Routes to the tool node or the numeric verifier</text>
  <text x="243" y="320" text-anchor="middle" font-size="8.6" font-weight="700" fill="#dc2626">No free-form LLM arithmetic</text>

  <rect x="472" y="212" width="410" height="132" rx="8" fill="#ffffff" stroke="#fb923c" stroke-width="1.3"/>
  <text x="677" y="232" text-anchor="middle" font-size="10.2" font-weight="700" fill="#9a3412">Node 4: deterministic_tool_node</text>
  <text x="677" y="250" text-anchor="middle" font-size="8.6" fill="#334155">Executes flare_chronos_core physics and lookup functions</text>
  <text x="677" y="266" text-anchor="middle" font-size="8.6" font-weight="600" fill="#065f46">Records every scalar in the VerifiedFactsLedger</text>
  <text x="677" y="282" text-anchor="middle" font-size="8.6" fill="#475569">Result cache TTL 3600 s</text>
  <text x="677" y="300" text-anchor="middle" font-size="8.6" fill="#475569">Routes to the escalation gate or back to the agent</text>

  <line x1="450" y1="252" x2="470" y2="252" stroke="#ea580c" stroke-width="1.8" marker-end="url(#lgOrange)"/>
  <line x1="470" y1="326" x2="450" y2="326" stroke="#ea580c" stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#lgOrange)"/>

  <!-- VERIFICATION, SIGN-OFF AND FINAL SYNTHESIS -->
  <line x1="359" y1="356" x2="359" y2="380" stroke="#059669" stroke-width="2.2" marker-end="url(#lgGreen)"/>
  <text x="369" y="373" text-anchor="start" font-size="8.8" font-weight="700" fill="#065f46">verify</text>

  <rect x="22" y="382" width="876" height="160" rx="10" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="1.6"/>
  <rect x="22" y="382" width="876" height="25" rx="10" fill="url(#gateGrad)"/>
  <text x="460" y="399" text-anchor="middle" font-size="10.5" font-weight="700" fill="#ffffff" letter-spacing="0.5">VERIFICATION, HUMAN SIGN-OFF &amp; FINAL SYNTHESIS</text>

  <rect x="38" y="418" width="205" height="110" rx="8" fill="#ffffff" stroke="#34d399" stroke-width="1.3"/>
  <text x="140" y="438" text-anchor="middle" font-size="9.8" font-weight="700" fill="#065f46">Node 5: escalation_gate</text>
  <text x="140" y="458" text-anchor="middle" font-size="8.3" fill="#334155">Escalates S1 → S2 when</text>
  <text x="140" y="473" text-anchor="middle" font-size="8.3" font-weight="600" fill="#dc2626">raw-vs-harmonized ≥ 200%</text>
  <text x="140" y="488" text-anchor="middle" font-size="8.3" fill="#334155">or SAA anomalies appear</text>
  <text x="140" y="507" text-anchor="middle" font-size="8.3" fill="#475569">Otherwise returns to S1</text>

  <rect x="257" y="418" width="205" height="110" rx="8" fill="#ffffff" stroke="#34d399" stroke-width="1.3"/>
  <text x="359" y="438" text-anchor="middle" font-size="9.8" font-weight="700" fill="#065f46">Node 6: numeric_verifier</text>
  <text x="359" y="458" text-anchor="middle" font-size="8.3" fill="#334155">Audits every draft number</text>
  <text x="359" y="473" text-anchor="middle" font-size="8.3" fill="#334155">against VerifiedFactsLedger</text>
  <text x="359" y="488" text-anchor="middle" font-size="8.3" font-weight="600" fill="#dc2626">Unverified → S2 retry</text>
  <text x="359" y="507" text-anchor="middle" font-size="8.3" fill="#475569">≤ 2 corrections, then floor</text>

  <rect x="476" y="418" width="205" height="110" rx="8" fill="#ffffff" stroke="#34d399" stroke-width="1.3"/>
  <text x="578" y="438" text-anchor="middle" font-size="9.8" font-weight="700" fill="#065f46">Node 7: sign_off_gate</text>
  <text x="578" y="458" text-anchor="middle" font-size="8.3" fill="#334155">Pauses UC-S1.4 and UC-2.2</text>
  <text x="578" y="473" text-anchor="middle" font-size="8.3" font-weight="600" fill="#1e3a8a">Requires a Bearer JWT</text>
  <text x="578" y="488" text-anchor="middle" font-size="8.3" fill="#047857">Approve → publish</text>
  <text x="578" y="507" text-anchor="middle" font-size="8.3" fill="#dc2626">Reject → withhold</text>

  <rect x="695" y="418" width="205" height="110" rx="8" fill="#ffffff" stroke="#34d399" stroke-width="1.3"/>
  <text x="797" y="438" text-anchor="middle" font-size="9.8" font-weight="700" fill="#065f46">Node 8: system1_synthesizer</text>
  <text x="797" y="458" text-anchor="middle" font-size="8.3" fill="#334155">Builds the final briefing</text>
  <text x="797" y="473" text-anchor="middle" font-size="8.3" fill="#334155">Streams SSE to the Workbench</text>
  <text x="797" y="488" text-anchor="middle" font-size="8.3" fill="#475569">FastAPI ASGI :5901</text>
  <text x="797" y="507" text-anchor="middle" font-size="8.3" font-weight="700" fill="#059669">END</text>

  <line x1="462" y1="470" x2="474" y2="470" stroke="#059669" stroke-width="1.8" marker-end="url(#lgGreen)"/>
  <line x1="681" y1="470" x2="693" y2="470" stroke="#059669" stroke-width="1.8" marker-end="url(#lgGreen)"/>
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
    (r"\\ln(?![a-zA-Z])", "ln "),
    (r"\\exp(?![a-zA-Z])", "exp "),
    (r"\\sin(?![a-zA-Z])", "sin "),
    (r"\\cos(?![a-zA-Z])", "cos "),
    (r"\\arcsin(?![a-zA-Z])", "arcsin "),
    (r"\\arccos(?![a-zA-Z])", "arccos "),
    (r"\\tanh(?![a-zA-Z])", "tanh "),
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
            r"<span class='frac'><span class='num'>\1</span><span class='den'>\2</span></span>",
            s,
        )

    s = s.replace(r"\%", "%").replace("{", "").replace("}", "")
    s = re.sub(r"Δ\s+([A-Z])", r"Δ\1", s)
    s = re.sub(r"\b(cos|sin|ln|exp|tanh|arcsin|arccos)\s+<sup>", r"\1<sup>", s)
    s = re.sub(r"\(\s+", "(", s)
    s = re.sub(r"\s+\)", ")", s)
    # Italicize single Latin variables; function names and acronyms stay upright.
    s = re.sub(r"(?<![A-Za-z<])([A-Za-z])(?![A-Za-z>])", r"<i>\1</i>", s)
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


# ==============================================================================
# 1D. CONTENT-AWARE TABLE COLUMN BALANCER
# ==============================================================================

# Helvetica AFM advance widths (per mille of the font size). WeasyPrint's
# automatic table layout squeezes narrow columns and overflows wide ones, so the
# exporter measures each column and injects an explicit <colgroup> instead.
_HELVETICA_ADVANCE: dict[str, int] = {
    " ": 278,
    "!": 278,
    '"': 355,
    "#": 556,
    "$": 556,
    "%": 889,
    "&": 667,
    "'": 191,
    "(": 333,
    ")": 333,
    "*": 389,
    "+": 584,
    ",": 278,
    "-": 333,
    ".": 278,
    "/": 278,
    "0": 556,
    "1": 556,
    "2": 556,
    "3": 556,
    "4": 556,
    "5": 556,
    "6": 556,
    "7": 556,
    "8": 556,
    "9": 556,
    ":": 278,
    ";": 278,
    "<": 584,
    "=": 584,
    ">": 584,
    "?": 556,
    "@": 1015,
    "A": 667,
    "B": 667,
    "C": 722,
    "D": 722,
    "E": 667,
    "F": 611,
    "G": 778,
    "H": 722,
    "I": 278,
    "J": 500,
    "K": 667,
    "L": 556,
    "M": 833,
    "N": 722,
    "O": 778,
    "P": 667,
    "Q": 778,
    "R": 722,
    "S": 667,
    "T": 611,
    "U": 722,
    "V": 667,
    "W": 944,
    "X": 667,
    "Y": 667,
    "Z": 611,
    "[": 278,
    "\\": 278,
    "]": 278,
    "^": 469,
    "_": 556,
    "`": 333,
    "a": 556,
    "b": 556,
    "c": 500,
    "d": 556,
    "e": 556,
    "f": 278,
    "g": 556,
    "h": 556,
    "i": 222,
    "j": 222,
    "k": 500,
    "l": 222,
    "m": 833,
    "n": 556,
    "o": 556,
    "p": 556,
    "q": 556,
    "r": 333,
    "s": 500,
    "t": 278,
    "u": 556,
    "v": 500,
    "w": 722,
    "x": 500,
    "y": 500,
    "z": 500,
    "{": 334,
    "|": 260,
    "}": 334,
    "~": 584,
    "Δ": 612,
    "θ": 522,
    "φ": 556,
    "λ": 500,
    "ω": 722,
    "Ω": 768,
    "τ": 439,
    "σ": 592,
    "α": 559,
    "β": 592,
    "γ": 490,
    "κ": 500,
    "ψ": 592,
    "π": 522,
    "μ": 526,
    "δ": 592,
    "ε": 439,
    "×": 584,
    "·": 278,
    "≤": 584,
    "≥": 584,
    "≠": 584,
    "≡": 584,
    "≈": 584,
    "→": 1000,
    "∈": 667,
    "∑": 600,
    "√": 500,
    "°": 400,
    "±": 584,
}

_PAGE_CONTENT_WIDTH_MM = 176.0  # A4 width (210 mm) minus two 17 mm margins
_MM_PER_PT = 25.4 / 72.0


def _advance_pt(
    text: str, font_pt: float, bold: bool = False, mono: bool = False
) -> float:
    """Approximate the rendered advance width of ``text`` in PostScript points."""
    if not text:
        return 0.0
    if mono:
        width_pt = len(text) * font_pt * 0.6
    else:
        units = 0
        for char in unicodedata.normalize("NFKD", text):
            if unicodedata.combining(char):
                continue
            units += _HELVETICA_ADVANCE.get(char, 556)
        width_pt = units / 1000.0 * font_pt
    return width_pt * 1.06 if bold else width_pt


def _plain_text(fragment: str) -> str:
    """Strip markup/entities from an HTML fragment and collapse its whitespace."""
    fragment = re.sub(r"<br\s*/?>", " ", fragment)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    return re.sub(r"\s+", " ", html.unescape(fragment)).strip()


def _cell_metrics(cell_html: str, font_pt: float, bold: bool) -> tuple[float, float]:
    """Return ``(one_line_width_pt, longest_word_width_pt)`` for a table cell."""
    runs: list[tuple[str, bool]] = []
    cursor = 0
    for match in re.finditer(r"<code\b[^>]*>(.*?)</code>", cell_html, flags=re.DOTALL):
        runs.append((_plain_text(cell_html[cursor : match.start()]), False))
        runs.append((_plain_text(match.group(1)), True))
        cursor = match.end()
    runs.append((_plain_text(cell_html[cursor:]), False))

    one_line = 0.0
    longest_word = 0.0
    for text, mono in runs:
        one_line += _advance_pt(text, font_pt, bold=bold, mono=mono)
        for word in text.split():
            segments = [word]
            if mono and len(word) > 18:
                segments = re.split(r"_|(?<=[a-z0-9])(?=[A-Z])", word) or [word]
            for segment in segments:
                longest_word = max(
                    longest_word,
                    _advance_pt(segment, font_pt, bold=bold, mono=mono),
                )
    return one_line, longest_word


def _percentile(values: list[float], quantile: float) -> float:
    """Linear-interpolated percentile without pulling in a statistics dependency."""
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    fraction = position - low
    return ordered[low] * (1.0 - fraction) + ordered[high] * fraction


def _water_fill(
    widths: list[float], minimums: list[float], total: float
) -> list[float]:
    """Scale columns down to ``total`` while preserving each column's minimum."""
    widths = [max(width, minimum) for width, minimum in zip(widths, minimums)]
    current = sum(widths)
    if current <= total:
        return widths if current <= 0 else [w * total / current for w in widths]

    flexible = sum(width - minimum for width, minimum in zip(widths, minimums))
    overflow = current - total
    if flexible > 0 and overflow <= flexible:
        return [
            minimum + (width - minimum) * (1.0 - overflow / flexible)
            for width, minimum in zip(widths, minimums)
        ]

    floor_total = sum(minimums)
    if floor_total <= 0:
        return [total / len(widths)] * len(widths)
    return [minimum * total / floor_total for minimum in minimums]


def _add_code_break_opportunities(fragment: str) -> str:
    """Insert zero-width spaces in long identifiers so they wrap at word parts.

    ``overflow-wrap: break-word`` alone cuts a token at an arbitrary character
    (for example ``metr|ics``). Short identifiers such as ``MODIS_SP`` stay
    intact so they move to the next line as a unit.
    """

    def add_breaks(match: re.Match[str]) -> str:
        token = match.group(1)
        token = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "\u200b", token)
        if len(match.group(1)) > 18:
            token = token.replace("_", "_\u200b")
        return f"<code>{token}</code>"

    return re.sub(r"<code\b[^>]*>(.*?)</code>", add_breaks, fragment, flags=re.DOTALL)


def balance_table_columns(body_html: str) -> str:
    """Give every table explicit, content-aware column widths.

    Pandoc emits no ``<colgroup>`` and WeasyPrint's automatic layout either
    starves short columns or pushes wide tables past the right page margin. This
    pass measures each column (longest word = irreducible width, 75th percentile
    of cell text = preferred width) and writes percentage widths that sum to
    100 %. Tables with many dense columns fall back to a smaller font/padding.
    """

    def replace_table(match: re.Match[str]) -> str:
        table_html = match.group(0)
        if "colspan" in table_html or "rowspan" in table_html:
            return table_html

        rows = re.findall(r"<tr\b[^>]*>(.*?)</tr>", table_html, flags=re.DOTALL)
        parsed: list[list[tuple[str, str]]] = []
        for row in rows:
            cells = re.findall(r"<t([hd])\b[^>]*>(.*?)</t\1>", row, flags=re.DOTALL)
            if cells:
                parsed.append(cells)
        if len(parsed) < 2:
            return table_html

        column_count = len(parsed[0])
        if column_count < 2 or any(len(row) != column_count for row in parsed):
            return table_html

        # Try progressively smaller type (and tighter padding) until the
        # irreducible sum of longest words fits the printable width. Header
        # words may hyphenate, so only their first few syllables are fixed.
        def column_minimums(
            font_pt: float, padding_mm: float, hyphenate: bool
        ) -> list[float]:
            values: list[float] = []
            for column in range(column_count):
                header_word = 0.0
                body_word = 0.0
                has_code = False
                for row in parsed:
                    cell_html, is_header = row[column][1], row[column][0] == "h"
                    _, word_pt = _cell_metrics(cell_html, font_pt, is_header)
                    if is_header:
                        header_word = max(header_word, word_pt)
                    else:
                        body_word = max(body_word, word_pt)
                    has_code = has_code or "<code" in cell_html
                if hyphenate:
                    header_word = min(header_word, font_pt * 3.4)
                code_extra = (2.1 if padding_mm > 3 else 1.1) if has_code else 0.0
                values.append(
                    max(header_word, body_word) * _MM_PER_PT + padding_mm + code_extra
                )
            return values

        chosen_font = 6.5
        chosen_padding_mm = 2.00
        hyphenate = False
        for font_pt, padding_mm in (
            (8.3, 3.00),
            (8.0, 3.00),
            (7.7, 2.60),
            (7.4, 2.00),
            (7.1, 2.00),
            (6.8, 2.00),
            (6.5, 2.00),
        ):
            if column_count >= 9 and font_pt > 7.4:
                # Wide tables never fit at body size: go straight to compact.
                continue
            full_minimums = column_minimums(font_pt, padding_mm, hyphenate=False)
            if sum(full_minimums) <= 0.95 * _PAGE_CONTENT_WIDTH_MM:
                chosen_font = font_pt
                chosen_padding_mm = padding_mm
                hyphenate = False
                break
            hyphenated_minimums = column_minimums(font_pt, padding_mm, hyphenate=True)
            if sum(hyphenated_minimums) <= _PAGE_CONTENT_WIDTH_MM:
                chosen_font = font_pt
                chosen_padding_mm = padding_mm
                hyphenate = True
                break

        minimums = column_minimums(chosen_font, chosen_padding_mm, hyphenate)
        # Spread leftover width by how much body content each column carries,
        # not by header length: a long header may wrap, but a long data column
        # has no other place to go.
        weights: list[float] = []
        for column in range(column_count):
            body_widths = [
                _cell_metrics(row[column][1], chosen_font, False)[0]
                for row in parsed
                if row[column][0] != "h"
            ]
            weights.append(_percentile(body_widths, 0.75) * _MM_PER_PT)

        slack = _PAGE_CONTENT_WIDTH_MM - sum(minimums)
        weight_total = sum(weights)
        if slack > 0 and weight_total > 0:
            widths = [
                minimum + slack * weight / weight_total
                for minimum, weight in zip(minimums, weights)
            ]
        else:
            widths = _water_fill(minimums, minimums, _PAGE_CONTENT_WIDTH_MM)
        percentages = [width * 100.0 / _PAGE_CONTENT_WIDTH_MM for width in widths]
        percentages[-1] += 100.0 - sum(percentages)

        decimals = " ".join(
            f'<col style="width:{value:.2f}%"/>' for value in percentages
        )
        open_tag_end = table_html.index(">") + 1
        open_tag = re.sub(r'\s+(?:class|style)="[^"]*"', "", table_html[:open_tag_end])
        table_classes = "balanced-table"
        if chosen_font < 7.9:
            table_classes += " dense-table"
        if hyphenate:
            table_classes += " hyphenate-headers"
        open_tag = open_tag.replace(
            "<table",
            f'<table class="{table_classes}" style="font-size:{chosen_font}pt"',
            1,
        )
        return _add_code_break_opportunities(
            f"{open_tag}<colgroup>{decimals}</colgroup>{table_html[open_tag_end:]}"
        )

    return re.sub(
        r"<table\b[^>]*>.*?</table>", replace_table, body_html, flags=re.DOTALL
    )


def preprocess_markdown_for_weasyprint(
    md_content: str, workspace_root: Path
) -> tuple[str, dict[str, str]]:
    """Replace the cognitive Mermaid block with its vector SVG, format alerts, and convert LaTeX math."""
    html_injections: dict[str, str] = {}

    def mermaid_replacer(match: re.Match[str]) -> str:
        code = match.group(1)
        token = f"SVGDIAGRAMPLACEHOLDER{len(html_injections)}END"
        if "system1_triage" in code:
            html_injections[token] = _render_svg_container_as_data_uri(
                LANGGRAPH_FLOW_SVG
            )
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
            "IMPORTANT": ("Important", "callout-important"),
            "NOTE": ("Note", "callout-note"),
            "WARNING": ("Warning", "callout-warning"),
            "TIP": ("Tip", "callout-tip"),
        }
        title, css_cls = badge_map.get(alert_type, (alert_type, "callout-important"))
        return (
            f"\n<div class='callout-box {css_cls}'>"
            f"<div class='callout-header'>{title}</div>"
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
    margin: 20mm 17mm 18mm 17mm;
    @top-left {
        content: "FLARE-CHRONOS — NASA Space Apps Challenge 2026";
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-size: 7.5pt;
        color: #666666;
    }
    @bottom-left {
        content: "FLARE-CHRONOS · NASA Space Apps Challenge 2026";
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-size: 7.5pt;
        color: #888888;
    }
    @bottom-right {
        content: counter(page) " / " counter(pages);
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-size: 7.5pt;
        color: #666666;
    }
}

@page :first {
    @top-left { content: none; }
}

body {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 9.6pt;
    line-height: 1.5;
    color: #111111;
    margin: 0;
    padding: 0;
}

h1 {
    font-size: 19pt;
    font-weight: 700;
    line-height: 1.2;
    margin: 0 0 4mm 0;
    page-break-after: avoid;
}

h2 {
    font-size: 13pt;
    font-weight: 700;
    margin: 8mm 0 2mm 0;
    padding-bottom: 1.5mm;
    border-bottom: 0.6pt solid #999999;
    page-break-after: avoid;
}

h3 {
    font-size: 10.5pt;
    font-weight: 700;
    margin: 5mm 0 1.5mm 0;
    page-break-after: avoid;
}

h4 {
    font-size: 9.6pt;
    font-weight: 700;
    margin: 4mm 0 1mm 0;
    page-break-after: avoid;
}

p {
    margin: 0 0 2.6mm 0;
    text-indent: 1.5em;
}

.front-matter p {
    text-indent: 0;
}

h1 + p,
h2 + p,
h3 + p,
h4 + p,
blockquote p,
td p,
th p,
li p {
    text-indent: 0;
}

a {
    color: #111111;
    text-decoration: none;
}

ul, ol {
    margin: 0 0 2.6mm 0;
    padding-left: 5mm;
}

li {
    margin-bottom: 1mm;
}

hr {
    border: none;
    border-top: 0.5pt solid #cccccc;
    margin: 6mm 0;
}

blockquote {
    margin: 3mm 0;
    padding: 0 0 0 4mm;
    border-left: 2pt solid #999999;
    color: #333333;
}

blockquote p {
    margin-bottom: 1mm;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 3mm 0 4mm 0;
    font-size: 8.3pt;
    line-height: 1.35;
}

table.balanced-table {
    table-layout: fixed;
}

table.dense-table th,
table.dense-table td {
    padding: 3px 3px;
}

table.dense-table th {
    /* WeasyPrint under-measures wrapped header rows that end in <code>;
       the extra padding keeps the last pill clear of the row border. */
    padding-bottom: 6px;
}

table.dense-table code {
    font-size: 1em;
    padding: 0.5px 1px;
}

table.hyphenate-headers th {
    hyphens: auto;
    hyphenate-limit-chars: 7 3 3;
}

tr {
    page-break-inside: avoid;
}

thead {
    display: table-header-group;
}

th {
    background: #f0f0f0;
    color: #111111;
    font-weight: 700;
    text-align: left;
    padding: 4px 5px;
    border: 0.5pt solid #999999;
}

td {
    padding: 3.5px 5px;
    border: 0.5pt solid #bbbbbb;
    vertical-align: top;
    overflow-wrap: break-word;
}

tbody tr:nth-child(even) {
    background: #fafafa;
}

code {
    font-family: "Courier New", monospace;
    font-size: 8.3pt;
    background: #f4f4f4;
    padding: 0.5px 2px;
}

pre {
    background: #f4f4f4;
    color: #111111;
    padding: 3mm;
    font-family: "Courier New", monospace;
    font-size: 7.6pt;
    line-height: 1.35;
    white-space: pre-wrap;
    word-wrap: break-word;
    margin: 3mm 0;
    page-break-inside: avoid;
}

pre code {
    background: transparent;
    padding: 0;
}

img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 3mm auto;
    border: none;
}

figure {
    margin: 3mm 0;
    text-align: center;
    page-break-inside: avoid;
}

figcaption {
    font-size: 8pt;
    color: #555555;
    margin-top: 1.5mm;
}

.diagram-container {
    margin: 4mm 0;
    page-break-inside: avoid;
    text-align: center;
}

.diagram-title {
    font-size: 8.3pt;
    font-weight: 700;
    color: #333333;
    margin-bottom: 2mm;
    letter-spacing: 0.3px;
    text-transform: uppercase;
}

.callout-box {
    margin: 3mm 0;
    padding: 0 0 0 4mm;
    border-left: 2pt solid #999999;
}

.callout-header {
    font-size: 8.5pt;
    font-weight: 700;
    margin-bottom: 1mm;
}

.callout-body p {
    margin: 0;
}

.math-block {
    margin: 3mm 0;
    text-align: center;
    font-family: Georgia, serif;
    font-size: 9.6pt;
}

.math-inline {
    font-family: Georgia, serif;
}

.frac {
    display: inline-block;
    vertical-align: middle;
    text-align: center;
    margin: 0 2px;
}

.frac .num {
    display: block;
    padding: 0 2px;
    border-bottom: 0.5pt solid #111111;
    line-height: 1.1;
}

.frac .den {
    display: block;
    padding: 0 2px;
    line-height: 1.1;
}

"""


def build_pdf(
    md_path: Path,
    pdf_path: Path,
) -> None:
    """Convert a Markdown proposal or report into an A4 PDF."""
    workspace_root = Path(__file__).resolve().parents[1]

    print(f"[1/4] Preprocessing Markdown document: {md_path.name}...")
    raw_md = md_path.read_text(encoding="utf-8")
    processed_md, html_injections = preprocess_markdown_for_weasyprint(
        raw_md, workspace_root
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
    body_html = balance_table_columns(body_html)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Flare-Chronos — {html.escape(md_path.stem)}</title>
  <link rel="stylesheet" href="{temp_css.resolve().as_uri()}"/>
</head>
<body>
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
        description="Export PROPOSAL.md and REPORT.md to A4 PDFs with vector SVG diagrams."
    )
    parser.add_argument(
        "-i",
        "--input",
        default=None,
        help="Input Markdown file path (default: exports PROPOSAL.md and REPORT.md).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output PDF file path.",
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
        build_pdf(md_path=in_path, pdf_path=out_path)
    else:
        for fname in ("PROPOSAL.md", "REPORT.md"):
            md_file = exports_dir / fname
            if md_file.exists():
                pdf_file = md_file.with_suffix(".pdf")
                build_pdf(md_path=md_file, pdf_path=pdf_file)
