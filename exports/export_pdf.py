#!/usr/bin/env python3
"""
High-Resolution Vector PDF Exporter for Flare-Chronos:
1. exports/PROPOSAL.md -> exports/PROPOSAL.pdf (Standalone Scientific & Technical Proposal, zero codebase coupling)
2. exports/REPORT.md   -> exports/REPORT.pdf   (Codebase Architecture, Domain Model, ADRs & Empirical Report)

Modeled after CareAI/export_pdf.py using Pandoc + WeasyPrint with:
- Purpose-specific Vector SVG Architecture & Sequence Diagrams (Conceptual for PROPOSAL vs. Codebase for REPORT)
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
import subprocess
from pathlib import Path

# ==============================================================================
# 1A. CONCEPTUAL VECTOR SVG DIAGRAMS FOR STANDALONE PROPOSAL.PDF (ZERO CODEBASE REFS)
# ==============================================================================

PROPOSAL_ARCH_SVG = """
<div class="diagram-container">
<div class="diagram-title">HÌNH KIẾN TRÚC 1: SƠ ĐỒ KIẾN TRÚC TỔNG THỂ 5 TẦNG HỆ THỐNG ĐỒNG BỘ HÓA VẬT LÝ LIÊN CẢM BIẾN FLARE-CHRONOS</div>
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
  <text x="460" y="35" text-anchor="middle" font-size="11" font-weight="700" fill="#ffffff" letter-spacing="0.6">TẦNG 1: NGUỒN DỮ LIỆU VỆ TINH QUAN SÁT TRÁI ĐẤT NASA EARTHDATA &amp; LANCE FIRMS (2000–2026+)</text>

  <rect x="38" y="54" width="265" height="58" rx="7" fill="#ffffff" stroke="#60a5fa" stroke-width="1.2"/>
  <text x="170" y="73" text-anchor="middle" font-size="11" font-weight="700" fill="#1e3a8a">Cảm Biến MODIS Collection 6.1</text>
  <text x="170" y="89" text-anchor="middle" font-size="9.5" fill="#475569">Vệ tinh Terra (2000–2026) &amp; Aqua (2002–2026)</text>
  <text x="170" y="103" text-anchor="middle" font-size="9" font-weight="600" fill="#dc2626">Tâm quét 1.0 km → Rìa quét 4.83×2.01 km (9.69 km²)</text>

  <rect x="326" y="54" width="268" height="58" rx="7" fill="#ffffff" stroke="#60a5fa" stroke-width="1.2"/>
  <text x="460" y="73" text-anchor="middle" font-size="11" font-weight="700" fill="#1e3a8a">Cảm Biến VIIRS 375m Collection 2</text>
  <text x="460" y="89" text-anchor="middle" font-size="9.5" fill="#475569">Suomi-NPP (2012+), NOAA-20 (2018+), NOAA-21</text>
  <text x="460" y="103" text-anchor="middle" font-size="9" font-weight="600" fill="#059669">Gom cụm phần cứng 3 vùng (3:1, 2:1, 1:1) ≤ 0.62 km²</text>

  <rect x="617" y="54" width="265" height="58" rx="7" fill="#ffffff" stroke="#60a5fa" stroke-width="1.2"/>
  <text x="749" y="73" text-anchor="middle" font-size="11" font-weight="700" fill="#1e3a8a">Luồng Cảnh Báo Sớm &amp; Kho Lịch Sử</text>
  <text x="749" y="89" text-anchor="middle" font-size="9.5" fill="#475569">Chế độ URT / RT / NRT &amp; Standard Science (SP)</text>
  <text x="749" y="103" text-anchor="middle" font-size="9" font-weight="600" fill="#2563eb">Kiểm chứng trên 1.609.182 bản ghi điểm nóng thực tế</text>

  <line x1="170" y1="124" x2="170" y2="148" stroke="#2563eb" stroke-width="2" marker-end="url(#arrowBlue)"/>
  <line x1="460" y1="124" x2="460" y2="148" stroke="#2563eb" stroke-width="2" marker-end="url(#arrowBlue)"/>
  <line x1="749" y1="124" x2="749" y2="148" stroke="#2563eb" stroke-width="2" marker-end="url(#arrowBlue)"/>

  <!-- TIER 2: INGESTION & SCHEMA UNIFICATION -->
  <rect x="22" y="152" width="876" height="78" rx="10" fill="#f0fdf4" stroke="#86efac" stroke-width="1.5"/>
  <text x="40" y="171" font-size="10.5" font-weight="700" fill="#166534">TẦNG 2: THU THẬP ĐA CHẾ ĐỘ &amp; ĐỒNG NHẤT LƯỢC ĐỒ DỊ THƯỜNG NHIỆT (MULTI-SENSOR INGESTION &amp; SCHEMA UNIFICATION)</text>

  <rect x="38" y="180" width="410" height="38" rx="6" fill="#ffffff" stroke="#4ade80" stroke-width="1.2"/>
  <text x="243" y="197" text-anchor="middle" font-size="10.5" font-weight="700" fill="#15803d">Bộ Điều Phối Thu Thập Đa Nguồn &amp; Phân Trang Thời Gian</text>
  <text x="243" y="211" text-anchor="middle" font-size="9" fill="#475569">Ghép nối liền mạch dữ liệu Khoa học Chuẩn (SP) và Thời gian thực (NRT/URT)</text>

  <rect x="472" y="180" width="410" height="38" rx="6" fill="#ffffff" stroke="#4ade80" stroke-width="1.2"/>
  <text x="677" y="197" text-anchor="middle" font-size="10.5" font-weight="700" fill="#15803d">Chuẩn Hóa Thực Thể Dị Thường Nhiệt Liên Cảm Biến</text>
  <text x="677" y="211" text-anchor="middle" font-size="9" fill="#475569">Đồng nhất kênh nhiệt T4 (4 μm), T5 (11 μm), kích thước Scan×Track &amp; Bức xạ FRP</text>

  <line x1="448" y1="199" x2="470" y2="199" stroke="#059669" stroke-width="2" marker-end="url(#arrowGreen)"/>
  <line x1="460" y1="230" x2="460" y2="254" stroke="#ea580c" stroke-width="2.2" marker-end="url(#arrowOrange)"/>

  <!-- TIER 3: 5-STAGE PHYSICS HARMONIZATION ENGINE -->
  <rect x="22" y="258" width="876" height="196" rx="10" fill="#fff7ed" stroke="#fdba74" stroke-width="1.8"/>
  <rect x="22" y="258" width="876" height="26" rx="10" fill="url(#coreGrad)"/>
  <text x="460" y="275" text-anchor="middle" font-size="11" font-weight="700" fill="#ffffff" letter-spacing="0.5">TẦNG 3: LÕI ĐỒNG BỘ HÓA VẬT LÝ &amp; THỐNG KÊ 5 GIAI ĐOẠN (PHYSICS-GUIDED HARMONIZATION ENGINE)</text>

  <rect x="36" y="296" width="160" height="142" rx="8" fill="#ffffff" stroke="#fb923c" stroke-width="1.4"/>
  <rect x="36" y="296" width="160" height="24" rx="8" fill="#ffedd5"/>
  <text x="116" y="312" text-anchor="middle" font-size="9.8" font-weight="700" fill="#9a3412">GIAI ĐOẠN 1: Thiên Văn</text>
  <text x="116" y="332" text-anchor="middle" font-size="9" font-weight="700" fill="#1e293b">Chuẩn Hóa SZA &amp; Ngày/Đêm</text>
  <text x="116" y="350" text-anchor="middle" font-size="8.5" fill="#475569">Giải chuỗi Fourier bậc 3</text>
  <text x="116" y="364" text-anchor="middle" font-size="8.5" fill="#475569">Spencer (1971) tính góc</text>
  <text x="116" y="378" text-anchor="middle" font-size="8.5" font-weight="700" fill="#c2410c">SZA(φ, λ, UTC) &lt; 85.0°</text>
  <text x="116" y="396" text-anchor="middle" font-size="8.5" fill="#475569">Khử bất đồng nhất cờ</text>
  <text x="116" y="410" text-anchor="middle" font-size="8.5" fill="#475569">DayNight giữa NRT &amp; SP</text>

  <rect x="208" y="296" width="160" height="142" rx="8" fill="#ffffff" stroke="#fb923c" stroke-width="1.4"/>
  <rect x="208" y="296" width="160" height="24" rx="8" fill="#ffedd5"/>
  <text x="288" y="312" text-anchor="middle" font-size="9.8" font-weight="700" fill="#9a3412">GIAI ĐOẠN 2: Xác Suất</text>
  <text x="288" y="332" text-anchor="middle" font-size="9" font-weight="700" fill="#1e293b">Ánh Xạ P(fire) &amp; Lọc SAA</text>
  <text x="288" y="350" text-anchor="middle" font-size="8.5" fill="#475569">Quy đổi 0–100% &amp; l/n/h</text>
  <text x="288" y="364" text-anchor="middle" font-size="8.5" font-weight="700" fill="#c2410c">→ Xác suất P(fire) ∈ [0,1]</text>
  <text x="288" y="382" text-anchor="middle" font-size="8.5" fill="#475569">Lọc xung proton đêm</text>
  <text x="288" y="396" text-anchor="middle" font-size="8.5" font-weight="600" fill="#dc2626">Dị thường SAA Nam Mỹ</text>
  <text x="288" y="410" text-anchor="middle" font-size="8.5" fill="#475569">&amp; Nguồn nhiệt tĩnh</text>

  <rect x="380" y="296" width="160" height="142" rx="8" fill="#ffffff" stroke="#fb923c" stroke-width="1.4"/>
  <rect x="380" y="296" width="160" height="24" rx="8" fill="#ffedd5"/>
  <text x="460" y="312" text-anchor="middle" font-size="9.8" font-weight="700" fill="#9a3412">GIAI ĐOẠN 3: Hình Học</text>
  <text x="460" y="332" text-anchor="middle" font-size="9" font-weight="700" fill="#1e293b">Elip Quét &amp; Lưới Uber H3</text>
  <text x="460" y="350" text-anchor="middle" font-size="8.5" fill="#475569">Giải ngược góc quét θ</text>
  <text x="460" y="364" text-anchor="middle" font-size="8.5" font-weight="700" fill="#c2410c">Elip ΔS(θ) × ΔT(θ), góc α</text>
  <text x="460" y="382" text-anchor="middle" font-size="8.5" fill="#475569">Cầu phương 13 điểm lên</text>
  <text x="460" y="396" text-anchor="middle" font-size="8.5" font-weight="600" fill="#0f766e">Uber H3 Res 7 (5.16 km²)</text>
  <text x="460" y="410" text-anchor="middle" font-size="8.5" font-weight="600" fill="#0f766e">&amp; H3 Res 8 (0.74 km²)</text>

  <rect x="552" y="296" width="160" height="142" rx="8" fill="#ffffff" stroke="#fb923c" stroke-width="1.4"/>
  <rect x="552" y="296" width="160" height="24" rx="8" fill="#ffedd5"/>
  <text x="632" y="312" text-anchor="middle" font-size="9.8" font-weight="700" fill="#9a3412">GIAI ĐOẠN 4: Bức Xạ</text>
  <text x="632" y="332" text-anchor="middle" font-size="9" font-weight="700" fill="#1e293b">Toán Tử 4 μm &amp; Phân Vị</text>
  <text x="632" y="350" text-anchor="middle" font-size="8.5" fill="#475569">Bù giới hạn góc quét</text>
  <text x="632" y="364" text-anchor="middle" font-size="8.5" font-weight="700" fill="#c2410c">FRP_lim(θ, SZA) + EQM</text>
  <text x="632" y="382" text-anchor="middle" font-size="8.5" fill="#475569">11.553 cặp đồng thời</text>
  <text x="632" y="396" text-anchor="middle" font-size="8.5" fill="#475569">Aqua–SNPP (13:30 MLT)</text>
  <text x="632" y="410" text-anchor="middle" font-size="8.5" font-weight="700" fill="#15803d">Giảm 79.7% sai số KS!</text>

  <rect x="724" y="296" width="160" height="142" rx="8" fill="#ffffff" stroke="#fb923c" stroke-width="1.4"/>
  <rect x="724" y="296" width="160" height="24" rx="8" fill="#ffedd5"/>
  <text x="804" y="312" text-anchor="middle" font-size="9.8" font-weight="700" fill="#9a3412">GIAI ĐOẠN 5: Sự Kiện</text>
  <text x="804" y="332" text-anchor="middle" font-size="9" font-weight="700" fill="#1e293b">Khử Trùng Lặp &amp; Nỗ Lực</text>
  <text x="804" y="350" text-anchor="middle" font-size="8.5" fill="#475569">Gom cụm không-thời gian</text>
  <text x="804" y="364" text-anchor="middle" font-size="8.5" font-weight="700" fill="#c2410c">τ = 95 phút → Sự kiện cháy</text>
  <text x="804" y="382" text-anchor="middle" font-size="8.5" fill="#475569">Chia hệ số nỗ lực quét</text>
  <text x="804" y="396" text-anchor="middle" font-size="8.5" font-weight="700" fill="#15803d">Ω(y, φ) ∈ [0.52, 2.10]</text>
  <text x="804" y="410" text-anchor="middle" font-size="8.5" fill="#475569">Khử bước nhảy +1.324%</text>

  <line x1="196" y1="367" x2="206" y2="367" stroke="#ea580c" stroke-width="1.8" marker-end="url(#arrowOrange)"/>
  <line x1="368" y1="367" x2="378" y2="367" stroke="#ea580c" stroke-width="1.8" marker-end="url(#arrowOrange)"/>
  <line x1="540" y1="367" x2="550" y2="367" stroke="#ea580c" stroke-width="1.8" marker-end="url(#arrowOrange)"/>
  <line x1="712" y1="367" x2="722" y2="367" stroke="#ea580c" stroke-width="1.8" marker-end="url(#arrowOrange)"/>

  <line x1="460" y1="454" x2="460" y2="478" stroke="#059669" stroke-width="2.2" marker-end="url(#arrowGreen)"/>

  <!-- TIER 4: SPATIO-TEMPORAL CUBE & CALENDAR ENGINE -->
  <rect x="22" y="482" width="876" height="88" rx="10" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="1.5"/>
  <rect x="22" y="482" width="876" height="24" rx="10" fill="url(#calGrad)"/>
  <text x="460" y="498" text-anchor="middle" font-size="10.5" font-weight="700" fill="#ffffff" letter-spacing="0.5">TẦNG 4: KHỐI LẬP PHƯƠNG KHÔNG-THỜI GIAN ĐẲNG DIỆN TÍCH &amp; ĐỘNG CƠ LỊCH HOẠT ĐỘNG CHÁY 26 NĂM</text>

  <rect x="38" y="514" width="410" height="46" rx="6" fill="#ffffff" stroke="#34d399" stroke-width="1.2"/>
  <text x="243" y="532" text-anchor="middle" font-size="10.5" font-weight="700" fill="#065f46">Khối Dữ Liệu Lục Giác Đẳng Diện Tích (H3 × Year × Pentad Cube)</text>
  <text x="243" y="548" text-anchor="middle" font-size="9" fill="#475569">Lưu trữ Điểm nóng hiệu chuẩn • Sự kiện cháy độc lập • Lịch sử 26 năm (2000–2026)</text>

  <rect x="472" y="514" width="410" height="46" rx="6" fill="#ffffff" stroke="#34d399" stroke-width="1.2"/>
  <text x="677" y="532" text-anchor="middle" font-size="10.5" font-weight="700" fill="#065f46">Lịch Hoạt Động Cháy Thống Nhất (26 Năm × 73 Pentads)</text>
  <text x="677" y="548" text-anchor="middle" font-size="9" font-weight="600" fill="#047857">Bộ 3 chỉ số: HFD (Mật độ) • HRF (MW/km²) • SFAI Anomaly Z-Score</text>

  <line x1="448" y1="537" x2="470" y2="537" stroke="#059669" stroke-width="2" marker-end="url(#arrowGreen)"/>
  <line x1="460" y1="570" x2="460" y2="594" stroke="#2563eb" stroke-width="2.2" marker-end="url(#arrowBlue)"/>

  <!-- TIER 5: ANALYTICAL WORKBENCH -->
  <rect x="22" y="598" width="876" height="74" rx="10" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="40" y="617" font-size="10.5" font-weight="700" fill="#1e293b">TẦNG 5: KHÔNG GIAN PHÂN TÍCH TƯƠNG TÁC ĐỒNG BỘ 4 KHUNG NHÌN &amp; CẢNH BÁO SỚM (ANALYTICAL WORKBENCH)</text>

  <rect x="38" y="625" width="265" height="36" rx="6" fill="#ffffff" stroke="#94a3b8" stroke-width="1.2"/>
  <text x="170" y="641" text-anchor="middle" font-size="9.5" font-weight="700" fill="#1e3a8a">Bản Đồ WebGL Elip ΔS×ΔT &amp; Lưới H3</text>
  <text x="170" y="654" text-anchor="middle" font-size="8.5" fill="#475569">Hiển thị trực quan elip rìa quét 9.69 km²</text>

  <rect x="326" y="625" width="268" height="36" rx="6" fill="#ffffff" stroke="#94a3b8" stroke-width="1.2"/>
  <text x="460" y="641" text-anchor="middle" font-size="9.5" font-weight="700" fill="#9a3412">Ma Trận Lịch Cháy 26×73 &amp; Đồng Hồ Cực</text>
  <text x="460" y="654" text-anchor="middle" font-size="8.5" fill="#475569">Phát hiện cháy ngoài mùa vụ (SFAI ≥ +2.5σ)</text>

  <rect x="617" y="625" width="265" height="36" rx="6" fill="#ffffff" stroke="#94a3b8" stroke-width="1.2"/>
  <text x="749" y="641" text-anchor="middle" font-size="9.5" font-weight="700" fill="#065f46">Xuất Chuẩn Mở GIS &amp; Cảnh Báo Tác Chiến</text>
  <text x="749" y="654" text-anchor="middle" font-size="8.5" fill="#475569">Xuất đa giác elip GeoJSON &amp; Khối GeoParquet</text>
</svg>
</div>
"""

PROPOSAL_SEQ_SVG = """
<div class="diagram-container">
<div class="diagram-title">HÌNH KIẾN TRÚC 2: SƠ ĐỒ TUẦN TỰ LUỒNG ĐỒNG BỘ HÓA &amp; TRUY VẤN LỊCH HOẠT ĐỘNG CHÁY 26 NĂM</div>
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
    <text x="67" y="18" text-anchor="middle" font-size="10" font-weight="700" fill="#ffffff">Nhà Quản Lý / Khoa Học</text>
    <text x="67" y="32" text-anchor="middle" font-size="8.5" fill="#bfdbfe">Bản Đồ Tương Tác AOI</text>

    <rect x="180" y="0" width="145" height="40" rx="7" fill="#1d4ed8"/>
    <text x="252" y="18" text-anchor="middle" font-size="10" font-weight="700" fill="#ffffff">Cổng Dịch Vụ Phân Tích</text>
    <text x="252" y="32" text-anchor="middle" font-size="8.5" fill="#bfdbfe">Điều Phối Truy Vấn AOI</text>

    <rect x="365" y="0" width="150" height="40" rx="7" fill="#047857"/>
    <text x="440" y="18" text-anchor="middle" font-size="10" font-weight="700" fill="#ffffff">Tầng Thu Thập FIRMS</text>
    <text x="440" y="32" text-anchor="middle" font-size="8.5" fill="#a7f3d0">Kho Lịch Sử SP &amp; NRT</text>

    <rect x="555" y="0" width="160" height="40" rx="7" fill="#c2410c"/>
    <text x="635" y="18" text-anchor="middle" font-size="10" font-weight="700" fill="#ffffff">Lõi Đồng Bộ Hóa Vật Lý</text>
    <text x="635" y="32" text-anchor="middle" font-size="8.5" fill="#fed7aa">5 Giai Đoạn Toán Học</text>

    <rect x="750" y="0" width="115" height="40" rx="7" fill="#334155"/>
    <text x="807" y="18" text-anchor="middle" font-size="10" font-weight="700" fill="#ffffff">Khối Lịch Cháy H3</text>
    <text x="807" y="32" text-anchor="middle" font-size="8.5" fill="#cbd5e1">Ma Trận 26×73</text>
  </g>

  <line x1="97" y1="58" x2="97" y2="490" stroke="#94a3b8" stroke-width="1.3" stroke-dasharray="5,4"/>
  <line x1="282" y1="58" x2="282" y2="490" stroke="#94a3b8" stroke-width="1.3" stroke-dasharray="5,4"/>
  <line x1="470" y1="58" x2="470" y2="490" stroke="#94a3b8" stroke-width="1.3" stroke-dasharray="5,4"/>
  <line x1="665" y1="58" x2="665" y2="490" stroke="#94a3b8" stroke-width="1.3" stroke-dasharray="5,4"/>
  <line x1="837" y1="58" x2="837" y2="490" stroke="#94a3b8" stroke-width="1.3" stroke-dasharray="5,4"/>

  <line x1="97" y1="84" x2="278" y2="84" stroke="#1e40af" stroke-width="1.8" marker-end="url(#seqArrow)"/>
  <text x="187" y="77" text-anchor="middle" font-size="9" font-weight="600" fill="#1e3a8a">1. Chọn Vùng Quan Tâm (AOI / Lưới H3) &amp; Chu kỳ 2000–2026</text>

  <line x1="282" y1="114" x2="466" y2="114" stroke="#1e40af" stroke-width="1.8" marker-end="url(#seqArrow)"/>
  <text x="374" y="107" text-anchor="middle" font-size="9" font-weight="600" fill="#1e3a8a">2. Truy vấn chuỗi dữ liệu MODIS (SP/NRT) &amp; VIIRS (SNPP/J1/J2)</text>

  <rect x="355" y="124" width="230" height="40" rx="6" fill="#ecfdf5" stroke="#34d399" stroke-width="1.2"/>
  <text x="470" y="140" text-anchor="middle" font-size="8.8" font-weight="700" fill="#065f46">3. Hợp Nhất Kho Lưu Trữ &amp; Luồng Thời Gian Thực</text>
  <text x="470" y="155" text-anchor="middle" font-size="8.2" fill="#047857">Đồng nhất lược đồ thuộc tính • 1.609.182 bản ghi thực tế</text>

  <line x1="470" y1="176" x2="286" y2="176" stroke="#047857" stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#seqArrowRet)"/>
  <text x="378" y="170" text-anchor="middle" font-size="8.8" font-weight="600" fill="#047857">4. Trả về tập thực thể Dị Thường Nhiệt Thô</text>

  <line x1="282" y1="204" x2="661" y2="204" stroke="#c2410c" stroke-width="1.8" marker-end="url(#seqArrowCore)"/>
  <text x="472" y="197" text-anchor="middle" font-size="9" font-weight="700" fill="#9a3412">5. Kích hoạt Đường ống Đồng bộ hóa Vật lý – Thống kê 5 Giai đoạn</text>

  <rect x="520" y="216" width="290" height="156" rx="8" fill="#fff7ed" stroke="#fb923c" stroke-width="1.5"/>
  <text x="665" y="235" text-anchor="middle" font-size="9.5" font-weight="700" fill="#9a3412">Thực Thi 5 Thuật Toán Vật Lý – Thống Kê:</text>
  <text x="534" y="254" font-size="8.8" fill="#1e293b">• [5a] Tính góc thiên đỉnh Mặt Trời SZA(φ,λ,t) &lt; 85° (Day/Night)</text>
  <text x="534" y="272" font-size="8.8" fill="#1e293b">• [5b] Tính xác suất P(fire) ∈ [0,1] &amp; Lọc nhiễu SAA / Nguồn tĩnh</text>
  <text x="534" y="290" font-size="8.8" fill="#1e293b">• [5c] Giải góc quét θ → Elip ΔS×ΔT → Trọng số H3 Res 7 &amp; 8</text>
  <text x="534" y="308" font-size="8.8" fill="#1e293b">• [5d] Hiệu chuẩn 2 giai đoạn FRP_lim(θ) + EQM (D_KS = 0.0237)</text>
  <text x="534" y="326" font-size="8.8" fill="#1e293b">• [5e] Gom cụm sự kiện cháy (τ = 95 phút) &amp; Chia nỗ lực Ω(y, φ)</text>
  <text x="534" y="344" font-size="8.8" font-weight="700" fill="#c2410c">• [5f] Tổng hợp Ma trận 26 Năm × 73 Pentads (HFD, HRF, SFAI)</text>

  <line x1="665" y1="392" x2="833" y2="392" stroke="#1e40af" stroke-width="1.8" marker-end="url(#seqArrow)"/>
  <text x="750" y="385" text-anchor="middle" font-size="8.8" font-weight="600" fill="#1e3a8a">6. Lưu Khối Lịch Cháy H3</text>

  <line x1="837" y1="426" x2="286" y2="426" stroke="#047857" stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#seqArrowRet)"/>
  <text x="560" y="419" text-anchor="middle" font-size="9" font-weight="600" fill="#047857">7. Truy xuất Ma trận Lịch Hoạt Động Cháy (HFD, HRF, SFAI Z-Score) &lt; 50ms</text>

  <line x1="282" y1="460" x2="101" y2="460" stroke="#047857" stroke-width="2" marker-end="url(#seqArrowRet)"/>
  <text x="190" y="453" text-anchor="middle" font-size="9" font-weight="700" fill="#065f46">8. Hiển thị Elip H3, Lịch 26×73 &amp; Cảnh báo SFAI</text>
</svg>
</div>
"""


# ==============================================================================
# 1B. CODEBASE IMPLEMENTATION VECTOR SVG DIAGRAMS FOR REPORT.PDF
# ==============================================================================

REPORT_ARCH_SVG = """
<div class="diagram-container">
<div class="diagram-title">HÌNH KIẾN TRÚC 1: SƠ ĐỒ KIẾN TRÚC MONOREPO DEEP-MODULE 5 TẦNG CỦA CODEBASE FLARE-CHRONOS</div>
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
      <path d="M 0 1 L 10 5 L 0 9Z" fill="#059669"/>
    </marker>
  </defs>

  <rect width="920" height="690" rx="12" fill="url(#bgGrad)" stroke="#cbd5e1" stroke-width="1.5"/>

  <rect x="22" y="18" width="876" height="106" rx="10" fill="#eff6ff" stroke="#93c5fd" stroke-width="1.5"/>
  <rect x="22" y="18" width="876" height="26" rx="10" fill="url(#nasaGrad)"/>
  <text x="460" y="35" text-anchor="middle" font-size="11" font-weight="700" fill="#ffffff" letter-spacing="0.6">TẦNG 1: NGUỒN DỮ LIỆU VỆ TINH QUAN SÁT TRÁI ĐẤT NASA EARTHDATA &amp; LANCE FIRMS API (2000–2026+)</text>

  <rect x="38" y="54" width="265" height="58" rx="7" fill="#ffffff" stroke="#60a5fa" stroke-width="1.2"/>
  <text x="170" y="73" text-anchor="middle" font-size="11" font-weight="700" fill="#1e3a8a">MODIS Collection 6.1 (MCD14ML)</text>
  <text x="170" y="89" text-anchor="middle" font-size="9.5" fill="#475569">Terra (2000–2026) &amp; Aqua (2002–2026)</text>
  <text x="170" y="103" text-anchor="middle" font-size="9" font-weight="600" fill="#dc2626">Nadir 1.0 km → Rìa quét 4.83×2.01 km (9.69 km²)</text>

  <rect x="326" y="54" width="268" height="58" rx="7" fill="#ffffff" stroke="#60a5fa" stroke-width="1.2"/>
  <text x="460" y="73" text-anchor="middle" font-size="11" font-weight="700" fill="#1e3a8a">VIIRS 375m Collection 2 (VNP14IMG/VJ114)</text>
  <text x="460" y="89" text-anchor="middle" font-size="9.5" fill="#475569">Suomi-NPP (2012+), NOAA-20 (2018+), NOAA-21</text>
  <text x="460" y="103" text-anchor="middle" font-size="9" font-weight="600" fill="#059669">Gom cụm 3 phân vùng (3:1, 2:1, 1:1) ≤ 0.62 km²</text>

  <rect x="617" y="54" width="265" height="58" rx="7" fill="#ffffff" stroke="#60a5fa" stroke-width="1.2"/>
  <text x="749" y="73" text-anchor="middle" font-size="11" font-weight="700" fill="#1e3a8a">LANCE URT / RT / NRT &amp; Open Archive</text>
  <text x="749" y="89" text-anchor="middle" font-size="9.5" fill="#475569">Luồng cảnh báo sớm &amp; CSV khu vực 7 ngày</text>
  <text x="749" y="103" text-anchor="middle" font-size="9" font-weight="600" fill="#2563eb">1.609.182 bản ghi thực tế đã xác thực trong data/raw/</text>

  <line x1="170" y1="124" x2="170" y2="148" stroke="#2563eb" stroke-width="2" marker-end="url(#arrowBlue)"/>
  <line x1="460" y1="124" x2="460" y2="148" stroke="#2563eb" stroke-width="2" marker-end="url(#arrowBlue)"/>
  <line x1="749" y1="124" x2="749" y2="148" stroke="#2563eb" stroke-width="2" marker-end="url(#arrowBlue)"/>

  <rect x="22" y="152" width="876" height="78" rx="10" fill="#f0fdf4" stroke="#86efac" stroke-width="1.5"/>
  <text x="40" y="171" font-size="10.5" font-weight="700" fill="#166534">TẦNG 2: ADAPTER THU THẬP &amp; ĐIỀU TIẾT TỐC ĐỘ (packages/firms-ingestion — Seam Layer)</text>

  <rect x="38" y="180" width="410" height="38" rx="6" fill="#ffffff" stroke="#4ade80" stroke-width="1.2"/>
  <text x="243" y="197" text-anchor="middle" font-size="10.5" font-weight="700" fill="#15803d">FIRMSClient Rate-Limited Adapter (firms_client.py)</text>
  <text x="243" y="211" text-anchor="middle" font-size="9" fill="#475569">Điều tiết hạn mức 5.000 tx / 10 phút • Pacing 0.35s • parse_firms_dataframe()</text>

  <rect x="472" y="180" width="410" height="38" rx="6" fill="#ffffff" stroke="#4ade80" stroke-width="1.2"/>
  <text x="677" y="197" text-anchor="middle" font-size="10.5" font-weight="700" fill="#15803d">Immutable Local Data Cache (data/raw/*.csv &amp; Manifest)</text>
  <text x="677" y="211" text-anchor="middle" font-size="9" fill="#475569">134 lát cắt đa kỷ nguyên (2001–2026) • Mekong/Việt Nam &amp; Rừng Nhiệt Đới Amazon</text>

  <line x1="448" y1="199" x2="470" y2="199" stroke="#059669" stroke-width="2" marker-end="url(#arrowGreen)"/>
  <line x1="460" y1="230" x2="460" y2="254" stroke="#ea580c" stroke-width="2.2" marker-end="url(#arrowOrange)"/>

  <rect x="22" y="258" width="876" height="196" rx="10" fill="#fff7ed" stroke="#fdba74" stroke-width="1.8"/>
  <rect x="22" y="258" width="876" height="26" rx="10" fill="url(#coreGrad)"/>
  <text x="460" y="275" text-anchor="middle" font-size="11" font-weight="700" fill="#ffffff" letter-spacing="0.5">TẦNG 3: LÕI ĐỒNG BỘ HÓA VẬT LÝ &amp; THỐNG KÊ 5 BƯỚC (packages/harmonization-core — Pure Zero-I/O Deep Module)</text>

  <rect x="36" y="296" width="160" height="142" rx="8" fill="#ffffff" stroke="#fb923c" stroke-width="1.4"/>
  <rect x="36" y="296" width="160" height="24" rx="8" fill="#ffedd5"/>
  <text x="116" y="312" text-anchor="middle" font-size="10" font-weight="700" fill="#9a3412">BƯỚC 1: SZA &amp; DayNight</text>
  <text x="116" y="332" text-anchor="middle" font-size="9" font-weight="600" fill="#1e293b">solar_sza.py</text>
  <text x="116" y="350" text-anchor="middle" font-size="8.5" fill="#475569">Phương trình thiên văn</text>
  <text x="116" y="364" text-anchor="middle" font-size="8.5" fill="#475569">Spencer (1971) tính góc</text>
  <text x="116" y="378" text-anchor="middle" font-size="8.5" font-weight="700" fill="#c2410c">SZA(φ, λ, UTC) &lt; 85.0°</text>
  <text x="116" y="396" text-anchor="middle" font-size="8.5" fill="#475569">Khử lệch cờ DayNight</text>
  <text x="116" y="410" text-anchor="middle" font-size="8.5" fill="#475569">giữa luồng NRT &amp; SP</text>

  <rect x="208" y="296" width="160" height="142" rx="8" fill="#ffffff" stroke="#fb923c" stroke-width="1.4"/>
  <rect x="208" y="296" width="160" height="24" rx="8" fill="#ffedd5"/>
  <text x="288" y="312" text-anchor="middle" font-size="10" font-weight="700" fill="#9a3412">BƯỚC 2: P(fire) &amp; Lọc SAA</text>
  <text x="288" y="332" text-anchor="middle" font-size="9" font-weight="600" fill="#1e293b">confidence_filter.py</text>
  <text x="288" y="350" text-anchor="middle" font-size="8.5" fill="#475569">Ánh xạ 0–100% &amp; l/n/h</text>
  <text x="288" y="364" text-anchor="middle" font-size="8.5" font-weight="700" fill="#c2410c">→ Xác suất P(fire) ∈ [0,1]</text>
  <text x="288" y="382" text-anchor="middle" font-size="8.5" fill="#475569">Lọc xung proton đêm</text>
  <text x="288" y="396" text-anchor="middle" font-size="8.5" font-weight="600" fill="#dc2626">Vùng SAA Nam Mỹ</text>
  <text x="288" y="410" text-anchor="middle" font-size="8.5" fill="#475569">&amp; Nguồn nhiệt tĩnh H3</text>

  <rect x="380" y="296" width="160" height="142" rx="8" fill="#ffffff" stroke="#fb923c" stroke-width="1.4"/>
  <rect x="380" y="296" width="160" height="24" rx="8" fill="#ffedd5"/>
  <text x="460" y="312" text-anchor="middle" font-size="10" font-weight="700" fill="#9a3412">BƯỚC 3: Hình Học H3 Kép</text>
  <text x="460" y="332" text-anchor="middle" font-size="9" font-weight="600" fill="#1e293b">geometry_h3.py</text>
  <text x="460" y="350" text-anchor="middle" font-size="8.5" fill="#475569">Giải ngược góc quét θ</text>
  <text x="460" y="364" text-anchor="middle" font-size="8.5" font-weight="700" fill="#c2410c">Elip ΔS(θ) × ΔT(θ), góc α</text>
  <text x="460" y="382" text-anchor="middle" font-size="8.5" fill="#475569">Cầu phương 13 điểm lên</text>
  <text x="460" y="396" text-anchor="middle" font-size="8.5" font-weight="600" fill="#0f766e">Uber H3 Res 7 (5.16 km²)</text>
  <text x="460" y="410" text-anchor="middle" font-size="8.5" font-weight="600" fill="#0f766e">&amp; H3 Res 8 (0.74 km²)</text>

  <rect x="552" y="296" width="160" height="142" rx="8" fill="#ffffff" stroke="#fb923c" stroke-width="1.4"/>
  <rect x="552" y="296" width="160" height="24" rx="8" fill="#ffedd5"/>
  <text x="632" y="312" text-anchor="middle" font-size="10" font-weight="700" fill="#9a3412">BƯỚC 4: Hiệu Chuẩn FRP</text>
  <text x="632" y="332" text-anchor="middle" font-size="9" font-weight="600" fill="#1e293b">radiometric_calibrator.py</text>
  <text x="632" y="350" text-anchor="middle" font-size="8.5" fill="#475569">Toán tử giới hạn góc quét</text>
  <text x="632" y="364" text-anchor="middle" font-size="8.5" font-weight="700" fill="#c2410c">FRP_lim(θ, SZA) + EQM</text>
  <text x="632" y="382" text-anchor="middle" font-size="8.5" fill="#475569">11.553 cặp đồng thời</text>
  <text x="632" y="396" text-anchor="middle" font-size="8.5" fill="#475569">Aqua–SNPP (13:30 MLT)</text>
  <text x="632" y="410" text-anchor="middle" font-size="8.5" font-weight="700" fill="#15803d">Giảm 79.7% sai số KS!</text>

  <rect x="724" y="296" width="160" height="142" rx="8" fill="#ffffff" stroke="#fb923c" stroke-width="1.4"/>
  <rect x="724" y="296" width="160" height="24" rx="8" fill="#ffedd5"/>
  <text x="804" y="312" text-anchor="middle" font-size="10" font-weight="700" fill="#9a3412">BƯỚC 5: Khử Trùng Lặp</text>
  <text x="804" y="332" text-anchor="middle" font-size="9" font-weight="600" fill="#1e293b">deduplication.py</text>
  <text x="804" y="350" text-anchor="middle" font-size="8.5" fill="#475569">Băm không gian O(N)</text>
  <text x="804" y="364" text-anchor="middle" font-size="8.5" font-weight="700" fill="#c2410c">τ = 95 phút → FireEpisode</text>
  <text x="804" y="382" text-anchor="middle" font-size="8.5" fill="#475569">Chia hệ số nỗ lực quét</text>
  <text x="804" y="396" text-anchor="middle" font-size="8.5" font-weight="700" fill="#15803d">Ω(y, φ) ∈ [0.52, 2.10]</text>
  <text x="804" y="410" text-anchor="middle" font-size="8.5" fill="#475569">Khử bước nhảy +1.324%</text>

  <line x1="196" y1="367" x2="206" y2="367" stroke="#ea580c" stroke-width="1.8" marker-end="url(#arrowOrange)"/>
  <line x1="368" y1="367" x2="378" y2="367" stroke="#ea580c" stroke-width="1.8" marker-end="url(#arrowOrange)"/>
  <line x1="540" y1="367" x2="550" y2="367" stroke="#ea580c" stroke-width="1.8" marker-end="url(#arrowOrange)"/>
  <line x1="712" y1="367" x2="722" y2="367" stroke="#ea580c" stroke-width="1.8" marker-end="url(#arrowOrange)"/>

  <line x1="460" y1="454" x2="460" y2="478" stroke="#059669" stroke-width="2.2" marker-end="url(#arrowGreen)"/>

  <rect x="22" y="482" width="876" height="88" rx="10" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="1.5"/>
  <rect x="22" y="482" width="876" height="24" rx="10" fill="url(#calGrad)"/>
  <text x="460" y="498" text-anchor="middle" font-size="10.5" font-weight="700" fill="#ffffff" letter-spacing="0.5">TẦNG 4: CƠ SỞ DỮ LIỆU KHÔNG-THỜI GIAN DUCKDB/H3 &amp; ĐỘNG CƠ LỊCH HOẠT ĐỘNG CHÁY (calendar_engine.py)</text>

  <rect x="38" y="514" width="410" height="46" rx="6" fill="#ffffff" stroke="#34d399" stroke-width="1.2"/>
  <text x="243" y="532" text-anchor="middle" font-size="10.5" font-weight="700" fill="#065f46">DuckDB / PostGIS + GeoParquet Spatio-Temporal Store</text>
  <text x="243" y="548" text-anchor="middle" font-size="9" fill="#475569">Bảng harmonized_detections • fire_episodes • h3_burning_calendar_cube</text>

  <rect x="472" y="514" width="410" height="46" rx="6" fill="#ffffff" stroke="#34d399" stroke-width="1.2"/>
  <text x="677" y="532" text-anchor="middle" font-size="10.5" font-weight="700" fill="#065f46">build_burning_activity_calendar() (26 Năm × 73 Pentads)</text>
  <text x="677" y="548" text-anchor="middle" font-size="9" font-weight="600" fill="#047857">Bộ 3 chỉ số: HFD (Mật độ) • HRF (MW/km²) • SFAI Anomaly Z-Score</text>

  <line x1="448" y1="537" x2="470" y2="537" stroke="#059669" stroke-width="2" marker-end="url(#arrowGreen)"/>
  <line x1="460" y1="570" x2="460" y2="594" stroke="#2563eb" stroke-width="2.2" marker-end="url(#arrowBlue)"/>

  <rect x="22" y="598" width="876" height="74" rx="10" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="40" y="617" font-size="10.5" font-weight="700" fill="#1e293b">TẦNG 5: ỨNG DỤNG CLI THỰC NGHIỆM, KẾT XUẤT BIỂU ĐỒ &amp; KIỂM THỬ BẤT BIẾN (apps/benchmark-cli &amp; tests/)</text>

  <rect x="38" y="625" width="265" height="36" rx="6" fill="#ffffff" stroke="#94a3b8" stroke-width="1.2"/>
  <text x="170" y="641" text-anchor="middle" font-size="9.5" font-weight="700" fill="#1e3a8a">fetch_real_firms.py &amp; run_experiments.py</text>
  <text x="170" y="654" text-anchor="middle" font-size="8.5" fill="#475569">Xuất data/processed/empirical_results.json</text>

  <rect x="326" y="625" width="268" height="36" rx="6" fill="#ffffff" stroke="#94a3b8" stroke-width="1.2"/>
  <text x="460" y="641" text-anchor="middle" font-size="9.5" font-weight="700" fill="#9a3412">figure_renderer.py &amp; exports/export_pdf.py</text>
  <text x="460" y="654" text-anchor="middle" font-size="8.5" fill="#475569">Kết xuất 5 biểu đồ PNG (1800×1080) &amp; Hồ sơ PDF</text>

  <rect x="617" y="625" width="265" height="36" rx="6" fill="#ffffff" stroke="#94a3b8" stroke-width="1.2"/>
  <text x="749" y="641" text-anchor="middle" font-size="9.5" font-weight="700" fill="#065f46">test_harmonization_suite.py &amp; Facade</text>
  <text x="749" y="654" text-anchor="middle" font-size="8.5" fill="#475569">7/7 Unit &amp; Physical Invariant Tests (0.010s)</text>
</svg>
</div>
"""

REPORT_SEQ_SVG = """
<div class="diagram-container">
<div class="diagram-title">HÌNH KIẾN TRÚC 2: SƠ ĐỒ TUẦN TỰ LUỒNG GỌI HÀM TRONG CODEBASE FLARE-CHRONOS</div>
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
    <text x="67" y="18" text-anchor="middle" font-size="10" font-weight="700" fill="#ffffff">Nhà Nghiên Cứu / CI</text>
    <text x="67" y="32" text-anchor="middle" font-size="8.5" fill="#bfdbfe">CLI / Test Runner</text>

    <rect x="180" y="0" width="145" height="40" rx="7" fill="#1d4ed8"/>
    <text x="252" y="18" text-anchor="middle" font-size="10" font-weight="700" fill="#ffffff">apps/benchmark-cli</text>
    <text x="252" y="32" text-anchor="middle" font-size="8.5" fill="#bfdbfe">run_experiments.py</text>

    <rect x="365" y="0" width="150" height="40" rx="7" fill="#047857"/>
    <text x="440" y="18" text-anchor="middle" font-size="10" font-weight="700" fill="#ffffff">firms-ingestion</text>
    <text x="440" y="32" text-anchor="middle" font-size="8.5" fill="#a7f3d0">firms_client.py + Cache</text>

    <rect x="555" y="0" width="160" height="40" rx="7" fill="#c2410c"/>
    <text x="635" y="18" text-anchor="middle" font-size="10" font-weight="700" fill="#ffffff">harmonization-core</text>
    <text x="635" y="32" text-anchor="middle" font-size="8.5" fill="#fed7aa">flare_chronos_core</text>

    <rect x="750" y="0" width="115" height="40" rx="7" fill="#334155"/>
    <text x="807" y="18" text-anchor="middle" font-size="10" font-weight="700" fill="#ffffff">Artifacts &amp; Figures</text>
    <text x="807" y="32" text-anchor="middle" font-size="8.5" fill="#cbd5e1">JSON + 5 PNGs</text>
  </g>

  <line x1="97" y1="58" x2="97" y2="490" stroke="#94a3b8" stroke-width="1.3" stroke-dasharray="5,4"/>
  <line x1="282" y1="58" x2="282" y2="490" stroke="#94a3b8" stroke-width="1.3" stroke-dasharray="5,4"/>
  <line x1="470" y1="58" x2="470" y2="490" stroke="#94a3b8" stroke-width="1.3" stroke-dasharray="5,4"/>
  <line x1="665" y1="58" x2="665" y2="490" stroke="#94a3b8" stroke-width="1.3" stroke-dasharray="5,4"/>
  <line x1="837" y1="58" x2="837" y2="490" stroke="#94a3b8" stroke-width="1.3" stroke-dasharray="5,4"/>

  <line x1="97" y1="84" x2="278" y2="84" stroke="#1e40af" stroke-width="1.8" marker-end="url(#seqArrow)"/>
  <text x="187" y="77" text-anchor="middle" font-size="9" font-weight="600" fill="#1e3a8a">1. Khởi chạy run_experiments.py</text>

  <line x1="282" y1="114" x2="466" y2="114" stroke="#1e40af" stroke-width="1.8" marker-end="url(#seqArrow)"/>
  <text x="374" y="107" text-anchor="middle" font-size="9" font-weight="600" fill="#1e3a8a">2. Gọi parse_firms_dataframe() trên 134 tệp CSV</text>

  <rect x="355" y="124" width="230" height="40" rx="6" fill="#ecfdf5" stroke="#34d399" stroke-width="1.2"/>
  <text x="470" y="140" text-anchor="middle" font-size="8.8" font-weight="700" fill="#065f46">3. Đọc data/raw/*.csv &amp; Chuẩn hóa Cột</text>
  <text x="470" y="155" text-anchor="middle" font-size="8.2" fill="#047857">1.609.182 bản ghi thực tế (2001–2026)</text>

  <line x1="470" y1="176" x2="286" y2="176" stroke="#047857" stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#seqArrowRet)"/>
  <text x="378" y="170" text-anchor="middle" font-size="8.8" font-weight="600" fill="#047857">4. Trả về List[ThermalDetection]</text>

  <line x1="282" y1="204" x2="661" y2="204" stroke="#c2410c" stroke-width="1.8" marker-end="url(#seqArrowCore)"/>
  <text x="472" y="197" text-anchor="middle" font-size="9" font-weight="700" fill="#9a3412">5. Gọi fit_coincident_aqua_snpp_model() &amp; harmonize_detections()</text>

  <rect x="520" y="216" width="290" height="156" rx="8" fill="#fff7ed" stroke="#fb923c" stroke-width="1.5"/>
  <text x="665" y="235" text-anchor="middle" font-size="9.5" font-weight="700" fill="#9a3412">Chuỗi Gọi Hàm Nội Bộ Trong flare_chronos_core:</text>
  <text x="534" y="254" font-size="8.8" fill="#1e293b">• [5a] harmonize_daynight_flag() → SZA(φ,λ,t) &lt; 85.0°</text>
  <text x="534" y="272" font-size="8.8" fill="#1e293b">• [5b] compute_unified_detection_probability() &amp; SAA Filter</text>
  <text x="534" y="290" font-size="8.8" fill="#1e293b">• [5c] reconstruct_instantaneous_footprint() &amp; allocate_h3()</text>
  <text x="534" y="308" font-size="8.8" fill="#1e293b">• [5d] apply_two_stage_frp_calibration() (D_KS = 0.0237)</text>
  <text x="534" y="326" font-size="8.8" fill="#1e293b">• [5e] cluster_fire_episodes(95m) &amp; effort Ω(y, φ)</text>
  <text x="534" y="344" font-size="8.8" font-weight="700" fill="#c2410c">• [5f] build_burning_activity_calendar() → 26×73 Matrix</text>

  <line x1="665" y1="392" x2="833" y2="392" stroke="#1e40af" stroke-width="1.8" marker-end="url(#seqArrow)"/>
  <text x="750" y="385" text-anchor="middle" font-size="8.8" font-weight="600" fill="#1e3a8a">6. Ghi empirical_results.json</text>

  <line x1="837" y1="426" x2="286" y2="426" stroke="#047857" stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#seqArrowRet)"/>
  <text x="560" y="419" text-anchor="middle" font-size="9" font-weight="600" fill="#047857">7. Kết xuất 5 biểu đồ khoa học PNG (fig1..fig5.png) qua figure_renderer.py</text>

  <line x1="282" y1="460" x2="101" y2="460" stroke="#047857" stroke-width="2" marker-end="url(#seqArrowRet)"/>
  <text x="190" y="453" text-anchor="middle" font-size="9" font-weight="700" fill="#065f46">8. Hoàn tất kiểm chứng &amp; Xuất PDF</text>
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
    (r"\\max(?![a-zA-Z])", "max"),
    (r"\\min(?![a-zA-Z])", "min"),
    (r"\\ln(?![a-zA-Z])", "ln"),
    (r"\\exp(?![a-zA-Z])", "exp"),
    (r"\\sin(?![a-zA-Z])", "sin"),
    (r"\\cos(?![a-zA-Z])", "cos"),
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
    """Replace Mermaid blocks with placeholders, format GitHub alerts, and convert LaTeX math."""
    html_injections: dict[str, str] = {}
    arch_svg = REPORT_ARCH_SVG if is_report else PROPOSAL_ARCH_SVG
    seq_svg = REPORT_SEQ_SVG if is_report else PROPOSAL_SEQ_SVG

    def mermaid_replacer(match: re.Match[str]) -> str:
        code = match.group(1)
        token = f"SVGDIAGRAMPLACEHOLDER{len(html_injections)}END"
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
                "PHÁT HIỆN KHOA HỌC & THỰC NGHIỆM TRỌNG YẾU",
                "callout-important",
            ),
            "NOTE": ("GHI CHÚ KỸ THUẬT", "callout-note"),
            "WARNING": ("CẢNH BÁO VẬT LÝ", "callout-warning"),
            "TIP": ("KHUYẾN NGHỊ VẬN HÀNH", "callout-tip"),
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

    figures_dir = (workspace_root / "docs" / "figures").resolve()
    md_content = md_content.replace(
        "](docs/figures/", f"](file://{figures_dir}/"
    ).replace("](../docs/figures/", f"](file://{figures_dir}/")

    return md_content, html_injections


# ==============================================================================
# 3. PROFESSIONAL A4 CSS TEMPLATE (CAREAI STYLE + SCIENTIFIC TYPOGRAPHY)
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
        content: "Trang " counter(page) " / " counter(pages);
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
    """Convert a Markdown proposal or report file into a high-resolution A4 PDF."""
    workspace_root = Path(__file__).resolve().parents[1]
    exports_dir = Path(__file__).resolve().parent
    is_report = "REPORT" in md_path.stem.upper()

    print(f"[1/4] Đang đọc và tiền xử lý tài liệu Markdown: {md_path.name}...")
    raw_md = md_path.read_text(encoding="utf-8")
    processed_md, html_injections = preprocess_markdown_for_weasyprint(
        raw_md, workspace_root, is_report=is_report
    )

    temp_md = exports_dir / f".temp_{md_path.stem}.md"
    temp_html = exports_dir / f".temp_{md_path.stem}.html"
    temp_css = exports_dir / ".temp_pdf_style.css"

    temp_md.write_text(processed_md, encoding="utf-8")
    temp_css.write_text(CSS_CONTENT, encoding="utf-8")

    print("[2/4] Đang biên dịch Markdown sang cấu trúc HTML5 qua Pandoc...")
    pandoc_cmd = [
        "/opt/homebrew/bin/pandoc",
        str(temp_md),
        "-f",
        "markdown+gfm_auto_identifiers+fenced_divs+pipe_tables+backtick_code_blocks+raw_html-tex_math_dollars",
        "-t",
        "html5",
        "--syntax-highlighting=pygments",
        "-o",
        str(temp_html),
    ]
    res = subprocess.run(pandoc_cmd, capture_output=True, text=True, check=False)
    if res.returncode != 0:
        pandoc_cmd = [
            "/opt/homebrew/bin/pandoc",
            str(temp_md),
            "-f",
            "markdown-tex_math_dollars",
            "-t",
            "html5",
            "--highlight-style=pygments",
            "-o",
            str(temp_html),
        ]
        subprocess.run(pandoc_cmd, check=True)

    body_html = temp_html.read_text(encoding="utf-8")
    for token, svg_html in html_injections.items():
        body_html = body_html.replace(f"<p>{token}</p>", svg_html).replace(
            token, svg_html
        )

    safe_name = html.escape(watermark_name.strip())
    safe_email = html.escape(watermark_email.strip())
    doc_role = (
        "Codebase & Empirical Report" if is_report else "Official Technical Proposal"
    )
    badge_text = (
        "2026 NASA SPACE APPS CHALLENGE • CODEBASE ARCHITECTURE & EMPIRICAL REPORT — FLARE-CHRONOS"
        if is_report
        else "2026 NASA SPACE APPS CHALLENGE • OFFICIAL TECHNICAL PROPOSAL — FLARE-CHRONOS"
    )

    watermark_block = ""
    if safe_name or safe_email:
        watermark_block = f"""
  <div class="watermark-overlay">
    <span class="wm-name">{safe_name} • FLARE-CHRONOS</span>
    <span class="wm-email">{safe_email} • {doc_role}</span>
  </div>"""

    full_html = f"""<!DOCTYPE html>
<html lang="vi">
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
        f"[3/4] Đang kết xuất PDF Vector độ phân giải cao qua WeasyPrint -> {pdf_path.name}..."
    )
    weasy_cmd = [
        "/opt/homebrew/bin/weasyprint",
        "--base-url",
        str(workspace_root.resolve()),
        str(temp_html),
        str(pdf_path),
    ]
    subprocess.run(weasy_cmd, check=True)

    for tmp in (temp_md, temp_html, temp_css):
        if tmp.exists():
            os.remove(tmp)

    size_kb = pdf_path.stat().st_size / 1024.0
    print(f"[4/4] Hoàn tất xuất PDF thành công: {pdf_path} ({size_kb:.1f} KB)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Xuất bộ đôi tài liệu PROPOSAL.md và REPORT.md sang PDF chuẩn A4 kèm Watermark cho dự án Flare-Chronos."
    )
    parser.add_argument(
        "-i",
        "--input",
        default=None,
        help="Đường dẫn file Markdown đầu vào (mặc định: xuất cả PROPOSAL.md và REPORT.md trong exports/).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Đường dẫn file PDF đầu ra.",
    )
    parser.add_argument(
        "--watermark-name",
        default="Lê Thành Trung",
        help="Tên tác giả hiển thị trên watermark chéo.",
    )
    parser.add_argument(
        "--watermark-email",
        default="lethanhtrung.trungle@gmail.com",
        help="Email hiển thị trên watermark chéo.",
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
        for fname in ("PROPOSAL.md", "REPORT.md"):
            md_file = exports_dir / fname
            if md_file.exists():
                pdf_file = md_file.with_suffix(".pdf")
                build_pdf(
                    md_path=md_file,
                    pdf_path=pdf_file,
                    watermark_name=args.watermark_name,
                    watermark_email=args.watermark_email,
                )
