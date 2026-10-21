# Bảng Giải Thích Chi Tiết Ký Hiệu, Công Thức & Thuật Ngữ (Symbols, Formulas & Terms Reference)

**Dự án:** **Flare-Chronos** — *26-Year Cross-Sensor Harmonized Active Fire Intelligence & Phenology Calendar*
**Mục đích:** Giải thích chi tiết từng ký hiệu, công thức, thuật ngữ xuất hiện trong các tài liệu của dự án (`docs/*`, `GLOSSARY.md`, `exports/PROPOSAL.md`, `exports/REPORT.md`, `exports/export_pdf.py`, mã nguồn `packages/*`, `apps/*`, `src/*`, `tests/*`).
**Đối tượng:** Nhà khoa học, kỹ sư, người chấm thi, và bất kỳ ai cần tra cứu nhanh ý nghĩa của một ký hiệu hoặc thuật ngữ.

> **Quy ước đọc:** Ký hiệu in nghiêng ($\theta$) là biến toán học; ký hiệu `monospace` là tên hàm/biến trong mã nguồn. Đơn vị đi kèm sau dấu phẩy. Tham chiếu vị trí cài đặt theo dạng `file.py::function_name`.

---

## 1. Quy Ước Ký Hiệu (Notation Conventions)

| Quy ước | Ý nghĩa | Ví dụ |
| :--- | :--- | :--- |
| Chữ Hy Lạp thường ($\theta, \phi, \lambda, \omega, \delta, \gamma, \tau, \kappa, \alpha, \beta, \sigma$) | Đại lượng vật lý / góc / tham số | $\theta$ = góc quét |
| Chữ Latin hoa ($A, R, N, P, D, L, T, S$) | Tập hợp, diện tích, số lượng, xác suất, khoảng cách | $A_p$ = diện tích điểm ảnh |
| Chỉ số dưới ($p, k, i, j, y$) | Chỉ số phần tử / năm / kỳ | $E_k$ = sự kiện cháy thứ $k$ |
| Dấu mũ ($\hat{X}, \tilde{X}, \bar{X}, \widetilde{X}$) | Ước lượng / hiệu chỉnh / trung bình | $\widehat{\text{FRP}}_{\text{VIIRS-eq}}$ = FRP hiệu chỉnh tương đương VIIRS |
| Dấu mũi tên ($\Delta X$) | Sai phân / độ lớn thay đổi | $\Delta S$ = chiều rộng điểm ảnh across-track |
| $|x|$ | Giá trị tuyệt đối của $x$ | $|\theta|$, ví dụ $|-3| = 3$ |
| $\max(a,b)$, $\min(a,b)$ | Hàm max/min | $\max(0, \cos\text{SZA})$ |
| $\text{clip}(x, lo, hi)$ | Kẹp giá trị vào $[lo, hi]$ | $\text{clip}(\Delta T_{45}-18, -10, 40)$ |
| $\ln$, $\log$ | Logarit tự nhiên | $\ln(\max(1, A_p))$ |
| $\arccos$, $\arcsin$, $\arctan$ | Hàm lượng giác nghịch đảo | $\arccos(\cos\text{SZA})$ |
| $\sum$, $\prod$ | Tổng / tích | $\sum_{E_k} \text{FRP}$ |
| $\text{Median}$, $\text{MAD}$, $\text{Std}$ | Trung vị / độ lệch tuyệt đối trung vị / độ lệch chuẩn | $\text{MAD}_{y'}(\text{HRF})$ |
| $F^{-1}$ | Hàm phân vị ngược (quantile function) | $F_{\text{VIIRS}}^{-1}(\cdot)$ |
| $\mathbb{E}$ / $\bar{X}$ | Kỳ vọng / trung bình mẫu | $\bar{N}_{\text{VIIRS}}$ |

---

## 2. Hằng Số Vật Lý & Quỹ Đạo (Physical & Orbital Constants)

| Ký hiệu | Giá trị | Đơn vị | Ý nghĩa | Vị trí |
| :--- | :--- | :--- | :--- | :--- |
| $R_e$ | $6378.137$ | km | Bán kính Trái Đất (WGS-84 bán trục lớn) | `geometry_h3.py::R_EARTH_KM` |
| $h_{\text{MODIS}}$ | $705$ | km | Độ cao quỹ đạo danh định MODIS (Terra/Aqua) | `geometry_h3.py::MODIS_ALTITUDE_KM` |
| $r_{\text{MODIS}}$ | $7083.137$ | km | Bán kính quỹ đạo MODIS = $R_e + h_{\text{MODIS}}$ | `geometry_h3.py::MODIS_ORBIT_RADIUS_KM` |
| $s_{\text{MODIS}}$ | $0.0014184397$ | rad/sample | Bước góc lấy mẫu MODIS (1 km nominal) | `geometry_h3.py::MODIS_SAMPLING_RAD` |
| $\theta_{\max,\text{MODIS}}$ | $55.0$ | deg | Góc quét tối đa MODIS | `geometry_h3.py::MODIS_MAX_SCAN_DEG` |
| $h_{\text{VIIRS}}$ | $829$ | km | Độ cao quỹ đạo danh định VIIRS (S-NPP/JPSS) | `geometry_h3.py::VIIRS_ALTITUDE_KM` |
| $r_{\text{VIIRS}}$ | $7207.137$ | km | Bán kính quỹ đạo VIIRS | `geometry_h3.py::VIIRS_ORBIT_RADIUS_KM` |
| $s_{\text{native},S}$ | $0.0001458$ | rad | Bước góc detector gốc VIIRS across-track (~121 m) | `geometry_h3.py::VIIRS_NATIVE_SCAN_RAD` |
| $s_{\text{native},T}$ | $0.0004340$ | rad | Bước góc detector gốc VIIRS along-track (~360 m) | `geometry_h3.py::VIIRS_NATIVE_TRACK_RAD` |
| $\theta_{z1}$ | $31.72$ | deg | Giới hạn Zone 1 VIIRS (gom 3:1) | `geometry_h3.py::VIIRS_ZONE1_MAX_DEG` |
| $\theta_{z2}$ | $44.86$ | deg | Giới hạn Zone 2 VIIRS (gom 2:1) | `geometry_h3.py::VIIRS_ZONE2_MAX_DEG` |
| $\theta_{z3}$ | $56.28$ | deg | Giới hạn Zone 3 VIIRS (gom 1:1, max swath) | `geometry_h3.py::VIIRS_ZONE3_MAX_DEG` |
| $i_{\text{Terra/Aqua}}$ | $98.2$ | deg | Góc nghiêng quỹ đạo MODIS | `geometry_h3.py::compute_orbital_track_azimuth` |
| $i_{\text{S-NPP/JPSS}}$ | $98.7$ | deg | Góc nghiêng quỹ đạo VIIRS | `geometry_h3.py::compute_orbital_track_azimuth` |
| $\sigma_{\text{SB}}$ | $5.6704\times10^{-8}$ | W·m⁻²·K⁻⁴ | Hằng số Stefan-Boltzmann | `docs/02` §3.1 |
| $a$ (Planck coeff.) | $\approx 3.0\times10^{-9}$ | W·m⁻²·sr⁻¹·μm⁻¹·K⁻⁴ | Hằng số thực nghiệm phổ cảm biến (4 μm) | `docs/02` §3.1 |
| $\lambda_{\text{MODIS},4}$ | $\approx 3.96$ | μm | Kênh hồng ngoại trung MODIS (Ch21/22) | `domain.py::ThermalDetection.bright_t4_k` |
| $\lambda_{\text{VIIRS},4}$ | $3.55$–$3.93$ | μm | Kênh I-4 VIIRS | `domain.py::ThermalDetection.bright_t4_k` |
| $\lambda_{\text{MODIS},11}$ | $\approx 11.0$ | μm | Kênh sóng dài MODIS (Ch31) | `domain.py::ThermalDetection.bright_t5_k` |
| $\lambda_{\text{VIIRS},11}$ | $10.5$–$12.4$ | μm | Kênh I-5 VIIRS | `domain.py::ThermalDetection.bright_t5_k` |
| $T_{\text{sat,I-4}}$ (ngày/đêm) | $367/320$ | K | Nhiệt độ bão hòa kênh I-4 VIIRS | `docs/02` §1 |
| $T_{\text{sat,M13}}$ | $380$ | K | Nhiệt độ bão hòa kênh M13 VIIRS | `docs/02` §1 |
| $\bar{A}_7$ (H3 Res 7) | $5.16129336$ | km² | Diện tích ô lục giác H3 Resolution 7 | `geometry_h3.py::H3_RES7_AREA_KM2` |
| $\bar{A}_8$ (H3 Res 8) | $0.73732760$ | km² | Diện tích ô lục giác H3 Resolution 8 | `geometry_h3.py::H3_RES8_AREA_KM2` |
| $A_{\text{VIIRS,nadir,nominal}}$ | $0.140625$ | km² | $0.375\times0.375$ km² nominal VIIRS | `radiometric_calibrator.py` |
| $P_{\text{thresh}}$ | $85.0$ | deg | Ngưỡng SZA phân biệt ngày/đêm | `solar_sza.py::DAYNIGHT_SZA_THRESHOLD_DEG` |
| $\tau_{\text{cluster}}$ | $95.0$ | phút | Cửa sổ thời gian gom cụm đa vệ tinh | `deduplication.py::cluster_fire_episodes` |
| $P_{\text{min}}$ | $0.20$ | — | Xác suất phát hiện tối thiểu để vào cụm | `deduplication.py::cluster_fire_episodes` |
| $\text{SAA}$ bounds | $\phi\in[-55,7]$, $\lambda\in[-110,11]$ | deg | Hộp giới hạn Dị thường Nam Đại Tây Dương | `confidence_filter.py` |
| $\Omega_0$ baseline | $1.00$ | — | Kỷ nguyên chuẩn Terra+Aqua xích đạo 2003–2011 | `deduplication.py::compute_effective_observation_effort` |

---

## 3. Biến & Ký Hiệu Vật Lý (Variables & Symbols)

### 3.1. Hình học dải quét (Scan Geometry)

| Ký hiệu | Tên tiếng Việt | Đơn vị | Ý nghĩa |
| :--- | :--- | :--- | :--- |
| $\theta$ | Góc quét | rad / deg | Góc lệch so với nadir của điểm ảnh |
| $\Delta S(\theta)$ | Chiều rộng across-track | km | Kích thước điểm ảnh vuông góc vệt bay |
| $\Delta T(\theta)$ | Chiều dài along-track | km | Kích thước điểm ảnh dọc vệt bay |
| $A_p$ | Diện tích điểm ảnh tức thời | km² | $\Delta S \times \Delta T$ |
| $\alpha_{\text{track}}$ | Góc phương vị vệt quỹ đạo | deg | Hướng bay của vệ tinh (clockwise from North) |
| $i$ | Góc nghiêng quỹ đạo | deg | Inclination (98.2 / 98.7) |
| $\phi$ | Vĩ độ | deg | Latitude |
| $\lambda$ | Kinh độ | deg | Longitude |
| $z$ / zone | Phân vùng gom cụm | — | 1, 2, 3 (VIIRS) hoặc 0 (MODIS) |
| $N_{\text{agg}}$ | Hệ số gom cụm | — | 3, 2, 1 theo zone |
| $\text{scan}$ | Trường scan trong CSV | km | $\Delta S$ thực đo |
| $\text{track}$ | Trường track trong CSV | km | $\Delta T$ thực đo |

### 3.2. Bức xạ & FRP

| Ký hiệu | Tên | Đơn vị | Ý nghĩa |
| :--- | :--- | :--- | :--- |
| $\text{FRP}$ | Fire Radiative Power | MW | Công suất bức xạ lửa tức thời |
| $\text{FRP}_{\text{lim}}$ | Detection limit | MW | Ngưỡng phát hiện tối thiểu |
| $\widetilde{\text{FRP}}_{\text{MODIS}}$ | FRP hiệu chỉnh góc quét | MW | Sau Stage 1 (scan-angle operator) |
| $\widehat{\text{FRP}}_{\text{VIIRS-eq}}$ | FRP tương đương VIIRS | MW | Sau Stage 2 (calibration) |
| $\text{FRP}_{\text{raw}}$ | FRP thô | MW | Giá trị gốc từ FIRMS |
| $\text{scan\_corrected\_frp\_mw}$ | FRP hiệu chỉnh scan | MW | Trường trong `HarmonizedDetection` |
| $\text{calibrated\_viirs\_eq\_frp\_mw}$ | FRP VIIRS-eq | MW | Trường trong `HarmonizedDetection` |
| $\Delta T_{45}$ | Độ tương phản nhiệt | K | $T_4 - T_5$ |
| $T_4$ | Nhiệt độ sáng 4 μm | K | `bright_t4_k` |
| $T_5$ | Nhiệt độ sáng 11 μm | K | `bright_t5_k` |
| $\tau_4(\theta)$ | Độ truyền qua khí quyển | — | Atmospheric transmittance at 4 μm |
| $L_4$ | Bức xạ 4 μm | W·m⁻²·sr⁻¹·μm⁻¹ | Spectral radiance |
| $\bar{L}_{4,\text{bg}}$ | Bức xạ nền | same | Background radiance |
| $\text{FRP}_p$ | FRP trên pixel | MW | $A_p \cdot \sigma_{\text{SB}} / (a \tau_4) \cdot (L_4 - \bar{L}_{4,\text{bg}})$ |

### 3.3. Xác suất & lọc nhiễu

| Ký hiệu | Tên | Đơn vị | Ý nghĩa |
| :--- | :--- | :--- | :--- |
| $P_{\text{fire}}$ | Detection probability | [0,1] | Xác suất phát hiện cháy thật |
| $C_{\text{MODIS}}$ | Confidence MODIS | % | `raw_confidence` 0–100 |
| $P_0(\text{class})$ | Neo xác suất VIIRS | [0,1] | 0.94 (high), 0.78/0.84 (nominal D/N), 0.28/0.38 (low D/N) |
| $P_{\text{episode}}$ | Xác suất sự kiện cháy | [0,1] | $1 - \prod(1 - 0.85 P_i)$ |
| $\text{is\_saa\_anomaly}$ | Cờ SAA | bool | Nhiễu hạt proton ban đêm |
| $\text{is\_static\_source}$ | Cờ nguồn tĩnh | bool | Khí đốt/volcano/nền |
| $P_{\text{combined}}$ | Xác suất hợp chứng cứ | [0,1] | Bayesian combination |

### 3.4. Thiên văn & SZA

| Ký hiệu | Tên | Đơn vị | Ý nghĩa |
| :--- | :--- | :--- | :--- |
| $\text{SZA}$ | Solar Zenith Angle | deg | Góc thiên đỉnh Mặt Trời |
| $\text{DOY}$ | Day of Year | 1–366 | Ngày trong năm |
| $t_{\text{UTC}}$ | Giờ quốc tế | giờ thập phân | UTC time |
| $\gamma$ | Góc năm (fractional year) | rad | $2\pi/365.25 \cdot (\text{DOY}-1 + (t_{\text{UTC}}-12)/24)$ |
| $\Delta t_{\text{EoT}}$ | Equation of Time | phút | Phương trình thời gian |
| $\delta$ | Độ lệch Mặt Trời | rad | Solar declination |
| $\omega$ | Góc giờ Mặt Trời | deg | Solar hour angle |
| $\phi$ | Vĩ độ | deg | Latitude |
| $\lambda$ | Kinh độ | deg | Longitude |

### 3.5. Hiệu chuẩn chéo & tham số mô hình

| Ký hiệu | Tên | Giá trị / đơn vị | Ý nghĩa |
| :--- | :--- | :--- | :--- |
| $\alpha$ (day/night) | Power-law intercept | — | `day_power_alpha`, `night_power_alpha` |
| $\beta$ (day/night) | Power-law exponent | — | `day_power_beta`, `night_power_beta` |
| $\kappa$ | Scan-tail compensation | — | `scan_tail_kappa` |
| $\gamma$ | Blend weight parametric | 0.65 | Trọng số parametric trong blend |
| $1-\gamma$ | Blend weight EQM | 0.35 | Trọng số EQM trong blend |
| $\text{base\_count\_mult}$ | Count multiplier nadir | 2.85 (day), 3.40 (night) | Nhân số điểm hotspot tương đương |
| $\kappa_{\text{grid}}$ | Grid search kappa | [0.10, 0.55] | Tìm $\kappa$ tối ưu |
| $\alpha_{\text{track}}$ | Track azimuth | deg | Góc phương vị vệt quỹ đạo |

### 3.6. Nỗ lực quan sát & gom cụm

| Ký hiệu | Tên | Đơn vị | Ý nghĩa |
| :--- | :--- | :--- | :--- |
| $\Omega(y, \phi)$ | Effective observation effort | — | Chuẩn hóa = 1.00 tại Terra+Aqua xích đạo 2003–2011 |
| $\Omega_0(y)$ | Baseline effort theo năm | — | 0.52, 0.76, 1.00, 1.48, 1.78, 1.92, 2.08 |
| $\text{lat\_convergence}$ | Hội tụ vĩ độ | — | $1 + 0.18(1/\cos\phi - 1)$, bounded [1.0, 1.65] |
| $\tau_{\text{cluster}}$ | Cửa sổ gom cụm | phút | 95 |
| $d_{\text{Haversine}}$ | Khoảng cách great-circle | km | Haversine distance |
| $r_{\text{eff}}$ | Bán kính footprint hiệu dụng | km | $\sqrt{A_p/\pi}$ |
| $m$ | Số phát hiện trong cụm | — | raw_detection_count |

### 3.7. Lịch hoạt động cháy (Calendar)

| Ký hiệu | Tên | Đơn vị | Ý nghĩa |
| :--- | :--- | :--- | :--- |
| $\text{HFD}_{y,p}$ | Harmonized Fire Density | episodes / 100 km² / day | Mật độ cháy chuẩn hóa |
| $\text{HRF}_{y,p}$ | Harmonized Radiative Flux | MW / km² | Thông lượng bức xạ chuẩn hóa |
| $\text{SFAI}_{y,p}$ | Standardized Fire Anomaly Index | Z-score | Chỉ số dị thường robust |
| $\text{H3}_7, \text{H3}_8$ | Ô lục giác H3 | — | Resolution 7 / 8 |
| $p$ | Pentad | 1–73 | Kỳ 5 ngày |
| $y$ | Năm | 2000–2026 | Year |
| $A_{\text{AOI}}$ | Diện tích vùng quan tâm | km² | Area of interest |
| $\psi_{\text{regime}}(y)$ | Hệ số chế độ cảm biến | — | (trong công thức HFD) |
| $\text{Median}_{y'}$ | Trung vị HRF theo pentad | MW/km² | Baseline theo pentad |
| $\text{MAD}$ | Median absolute deviation | MW/km² | Độ lệch tuyệt đối trung vị |
| $\text{Std}$ | Độ lệch chuẩn | MW/km² | Standard deviation |
| $E_k$ | Sự kiện cháy (Fire Episode) | — | Cluster of detections |
| $\mathcal{E}_{y,p}$ | Tập sự kiện cháy trong (y,p) | — | Set of episodes |
| $\text{episode\_count}$ | Số sự kiện cháy | — | Deduplicated count |

### 3.8. Thống kê kiểm định

| Ký hiệu | Tên | Ý nghĩa |
| :--- | :--- | :--- |
| $N_{\text{pairs}}$ | Số cặp ô lưới đồng thời | 11,553 |
| $R^2$ | Hệ số xác định | Variance explained |
| $\text{RMSE}$ | Root mean square error | MW/cell |
| $D_{\text{KS}}$ | Kolmogorov-Smirnov distance | Khoảng cách phân phối |
| $\text{ECDF}$ | Empirical CDF | Phân phối tích lũy thực nghiệm |
| $\text{CDF}_v, \text{CDF}_m$ | CDF của VIIRS / MODIS | — |
| $\text{max\_axis\_mw}$ | Trục lớn nhất | MW |
| $\text{alpha}, \text{beta}$ | Tham số fitted | — |
| $\text{raw\_r2}, \text{harm\_r2}$ | R² trước/sau | — |
| $\text{ks\_before}, \text{ks\_after}$ | KS trước/sau | — |

---

## 4. Công Thức (Formulas)

Mỗi công thức kèm tên, biểu thức, biến, và vị trí cài đặt.

### F1. MODIS across-track $\Delta S(\theta)$
$$\Delta S_{\text{MODIS}}(\theta) = R_e \cdot s \left( \frac{\cos\theta}{\sqrt{(R_e/r)^2 - \sin^2\theta}} - 1 \right)$$
Biến: $R_e=6378.137$, $r=7083.137$, $s=0.0014184397$, $\theta$ rad.
Vị trí: `geometry_h3.py::modis_dimensions_from_scan_angle`.

### F2. MODIS along-track $\Delta T(\theta)$
$$\Delta T_{\text{MODIS}}(\theta) = r \cdot s \left( \cos\theta - \sqrt{(R_e/r)^2 - \sin^2\theta} \right)$$
Vị trí: cùng F1.

### F3. VIIRS dimensions (3-zone)
$$\Delta S = R_e \cdot (N_{\text{agg}}\cdot s_{\text{native},S}) \cdot \left(\frac{\cos\theta}{\sqrt{(R_e/r)^2-\sin^2\theta}}-1\right)$$
$$\Delta T = r \cdot s_{\text{native},T} \cdot (\cos\theta - \sqrt{(R_e/r)^2-\sin^2\theta})$$
$N_{\text{agg}} = 3/2/1$ theo zone. Vị trí: `geometry_h3.py::viirs_dimensions_from_scan_angle`.

### F4. VIIRS zone
$$N_{\text{agg}}(\theta_{\deg}) = \begin{cases}3 & |\theta|<31.72\\2 & 31.72\le|\theta|<44.86\\1 & 44.86\le|\theta|\le56.28\end{cases}$$
Vị trí: `geometry_h3.py::viirs_aggregation_zone`.

### F5. Inversion MODIS scan angle (bisection)
Giải $\Delta S(\theta)=\text{scan}$ trên $[0, 55.5^\circ]$, 45 vòng lặp, sai số $<10^{-9}$ rad.
Vị trí: `geometry_h3.py::invert_modis_scan_angle`.

### F6. Inversion VIIRS scan angle
Bisection trên track, sau đó refine bằng scan. Vị trí: `geometry_h3.py::invert_viirs_scan_angle`.

### F7. Orbital track azimuth
$$\sin\alpha_{\text{track}} = \frac{\cos i}{\cos\phi},\quad \cos\phi \ge 0.15$$
Ascending node logic theo platform/daynight. Vị trí: `geometry_h3.py::compute_orbital_track_azimuth`.

### F8. H3 fractional allocation (13-point stencil)
$$w_{p,h} = \sum_{k: \text{H3}(\phi_k,\lambda_k)=h} \omega_k,\quad \sum_h w_{p,h}=1.0$$
Stencils: center 0.28, inner ring 4×0.09, outer ring 8×0.045. Vị trí: `geometry_h3.py::allocate_footprint_to_h3`.

### F9. FRP detection limit
$$\text{FRP}_{\text{lim,MODIS}} = (3.70 + 4.50\cos^{0.75}\text{SZA})\cdot A_p^{1.04}$$
$$\text{FRP}_{\text{lim,VIIRS}} = (0.50 + 0.65\cos^{0.75}\text{SZA})\cdot (A_p/0.1406)^{0.94}$$
Vị trí: `radiometric_calibrator.py::compute_frp_detection_limit`.

### F10. Stage 1 scan-angle tail compensation
$$\widetilde{\text{FRP}}_{\text{MODIS}} = \text{FRP}_{\text{raw}} \cdot [1 + \kappa\cdot \ln(\max(1, A_p))]$$
Vị trí: `radiometric_calibrator.py::apply_two_stage_frp_calibration`.

### F11. Stage 2 parametric + EQM blend
$$\widehat{\text{FRP}}_{\text{VIIRS-eq}} = 0.65\cdot(\alpha\cdot \widetilde{\text{FRP}}^\beta + 0.35(\text{FRP}_{\text{lim}}-1.15)) + 0.35\cdot \text{EQM}(\widetilde{\text{FRP}})$$
Vị trí: `radiometric_calibrator.py::apply_two_stage_frp_calibration`.

### F12. VIIRS equivalent count
$$\text{viirs\_eq\_count} = \text{base\_count\_mult}\cdot A_p^{0.38}$$
Vị trí: `radiometric_calibrator.py::apply_two_stage_frp_calibration`.

### F13. EQM interpolation
$$\text{EQM}(x) = \text{interp}(x, Q_{\text{MODIS}}, Q_{\text{VIIRS}})$$
Vị trí: `numpy.interp` trong calibrator.

### F14. SZA computation (Spencer 1971)
$$\gamma = \frac{2\pi}{365.25}\left(\text{DOY}-1+\frac{t_{\text{UTC}}-12}{24}\right)$$
$$\Delta t_{\text{EoT}} = 229.18(0.000075 + 0.001868\cos\gamma - 0.032077\sin\gamma - 0.014615\cos2\gamma - 0.040849\sin2\gamma)$$
$$\delta = 0.006918 - 0.399912\cos\gamma + 0.070257\sin\gamma - 0.006758\cos2\gamma + 0.000907\sin2\gamma - 0.002697\cos3\gamma + 0.001480\sin3\gamma$$
$$\omega = \frac{(60t_{\text{UTC}}+\Delta t_{\text{EoT}}+4\lambda)\bmod 1440}{4}-180$$
$$\text{SZA} = \arccos(\sin\phi\sin\delta + \cos\phi\cos\delta\cos\omega)$$
Vị trí: `solar_sza.py::compute_solar_zenith_angle`.

### F15. Day/night flag
$$\text{DayNight} = \begin{cases}\text{'D'} & \text{SZA}<85.0\\ \text{'N'} & \text{SZA}\ge85.0\end{cases}$$
Vị trí: `solar_sza.py::harmonize_daynight_flag`.

### F16. Unified detection probability (MODIS)
$$P_{\text{fire}} = \frac{1}{1+\exp\left[-\left(\frac{C-38}{19}+0.015\cdot\text{clip}(\Delta T_{45}-18,-10,40)\right)\right]}$$
Vị trí: `confidence_filter.py::compute_unified_detection_probability`.

### F17. Unified detection probability (VIIRS)
$$P_{\text{fire}} = \text{clip}\left(P_0 + 0.06\tanh\left(\frac{\Delta T_{45}-20}{15}\right), 0.05, 0.99\right)$$
$P_0$: high=0.94, nominal D/N=0.78/0.84, low D/N=0.28/0.38.
Vị trí: `confidence_filter.py::compute_unified_detection_probability`.

### F18. SAA false alarm
Nếu $\phi\in[-55,7]$, $\lambda\in[-110,11]$, night, và ($\Delta T_{45}<16.5$ & FRP<2.2) hoặc (base_prob<0.45 & $\Delta T_{45}<19.5$): is_saa=True, prob×=0.12.
Vị trí: `confidence_filter.py::compute_unified_detection_probability`.

### F19. Episode combined probability
$$P_{\text{episode}} = 1 - \prod_{i=1}^{m}(1 - 0.85 P_i)$$
Vị trí: `deduplication.py::cluster_fire_episodes`.

### F20. Haversine distance
$$d = 2R_e \arcsin\sqrt{\sin^2(\Delta\phi/2)+\cos\phi_1\cos\phi_2\sin^2(\Delta\lambda/2)}$$
Vị trí: `deduplication.py::haversine_km`.

### F21. Effective observation effort
$$\Omega(y,\phi)=\Omega_0(y)\cdot[1+0.18(1/\max(0.55,\cos\phi)-1)]$$
$\Omega_0$: 0.52 (≤2001), 0.76 (2002), 1.00 (2003–2011), 1.48 (2012–2017), 1.78 (2018–2022), 1.92 (2023), 2.08 (≥2024).
Vị trí: `deduplication.py::compute_effective_observation_effort`.

### F22. Cluster condition
$$d_{\text{Haversine}} \le \max(1.35, r_{\text{eff},i}+r_{\text{eff},j}+0.65) \quad \text{hoặc} \quad \text{H3}_8(x_i)=\text{H3}_8(x_j)$$
với $\Delta t \le 95$ phút. Vị trí: `deduplication.py::cluster_fire_episodes`.

### F23. HFD
$$\text{HFD}_{y,p} = \frac{100}{5 A_{\text{AOI}}}\sum_{E_k\in\mathcal{E}_{y,p}} \frac{P_{\text{episode}}(E_k)\psi_{\text{regime}}(y)}{\Omega(y,\phi_k)}$$
Vị trí: `calendar_engine.py::build_burning_activity_calendar` (đơn giản hóa: harm_ep_sum).

### F24. HRF
$$\text{HRF}_{y,p} = \frac{1}{A_{\text{AOI}}}\sum_{E_k\in\mathcal{E}_{y,p}} \frac{\widehat{\text{FRP}}_{\text{VIIRS-eq}}(E_k)}{\Omega(y,\phi_k)}$$
Vị trí: `calendar_engine.py::build_burning_activity_calendar`.

### F25. SFAI
$$\text{SFAI}_{y,p} = \frac{\text{HRF}_{y,p}-\text{Median}_{y'}(\text{HRF}_{y',p})}{0.65(1.4826\cdot\text{MAD})+0.35\cdot\text{Std}}$$
Vị trí: `calendar_engine.py::build_burning_activity_calendar`.

### F26. Pentad mapping
$$\text{pentad} = \min(73, \max(1, \lfloor(\text{doy}-1)/5\rfloor+1))$$
Vị trí: `calendar_engine.py::day_of_year_to_pentad`.

### F27. Pentad DOY range
$$\text{start}=(p-1)\cdot5+1,\quad \text{end}=365 \text{ nếu } p=73 \text{ else } p\cdot5$$
Vị trí: `calendar_engine.py::pentad_to_doy_range`.

### F28. SFAI tier
$$\text{Tier} = \begin{cases}\text{QUIET} & \text{SFAI}<-0.5\\\text{BASELINE} & -0.5\le\text{SFAI}<1.0\\\text{ELEVATED} & 1.0\le\text{SFAI}<1.75\\\text{SEVERE} & 1.75\le\text{SFAI}<2.5\\\text{CRISIS} & \text{SFAI}\ge2.5\end{cases}$$
Vị trí: `calendar_engine.py::classify_sfai_tier`.

### F29. Calibration fit (least squares / grid search)
Grid search $\kappa\in[0.10,0.55]$ (19 steps) minimizing MSE giữa predicted và VIIRS. Sau đó polyfit log-log để lấy $\alpha,\beta$. KS statistic qua ECDF.
Vị trí: `radiometric_calibrator.py::fit_coincident_aqua_snpp_model`.

### F30. Coincident cell grouping
Group by (acq_date, daynight, lat_bin, lon_bin) với lat_bin = round(lat×18), lon_bin = round(lon×18) (~0.05°). Filter: m_frp≥5, v_frp≥5, 0.65≤v/m≤4.2.
Vị trí: `run_experiments.py::run_coincident_overpass_calibration`.

---

## 5. Thuật Ngữ Miền (Domain Terms)

Trích từ `GLOSSARY.md` (root). Mỗi thuật ngữ kèm định nghĩa và từ cần tránh.

### 5.1. Vật lý cảm biến

- **Thermal Detection**: Một quan sát điểm nóng/điểm dị thường nhiệt thô từ MODIS/VIIRS. Tránh: Fire point, hotspot row, raw fire.
- **Instantaneous Footprint**: Diện tích hình elip $\Delta S \times \Delta T$ tại góc quét $\theta$ và phương vị $\alpha_{\text{track}}$. Tránh: Pixel size, point buffer, nominal resolution.
- **Bow-Tie Distortion**: Phình và chồng lấn điểm ảnh về rìa dải quét. Tránh: Edge stretching, pixel blur.
- **Aggregation Zone**: 3 phân vùng góc quét VIIRS (0–31.72, 31.72–44.86, 44.86–56.28) với gom 3:1, 2:1, 1:1. Tránh: Scan band, swath sector.
- **FRP**: Công suất bức xạ lửa tức thời (MW). Tránh: Fire intensity, fire temperature, heat energy.
- **Detection Limit (FRP_lim)**: FRP tối thiểu để vượt ngưỡng nền tại $A_p$ và SZA. Tránh: Sensitivity cutoff, minimum brightness.
- **Observation Operator**: Hàm truyền liên hệ thông lượng dưới điểm ảnh với FRP quan sát được. Tránh: Scaling factor, correction multiplier.

### 5.2. Đồng bộ hóa không-thời gian

- **SZA**: Góc thiên đỉnh Mặt Trời, SZA < 85° = ban ngày. Tránh: Day/night flag, local time indicator.
- **Detection Probability (P_fire)**: Xác suất [0,1] điểm nóng là cháy thật. Tránh: Confidence score, quality flag.
- **SAA**: Dị thường Nam Đại Tây Dương (11°E–110°W, 7°N–55°S). Tránh: Atlantic noise zone.
- **Static Thermal Source**: Nguồn nhiệt tĩnh (khí đốt, nhà máy, núi lửa). Tránh: False fire, stationary hotspot.
- **Fire Episode**: Sự kiện cháy vật lý duy nhất gom từ nhiều overpass. Tránh: Deduplicated point, merged hotspot, fire cluster.
- **Effective Observation Effort ($\Omega$)**: Năng lực quan sát chuẩn hóa. Tránh: Overpass count, satellite multiplier.
- **Co-Incident Overpass Pair**: Quan sát đồng thời Aqua-MODIS & S-NPP VIIRS. Tránh: Matched points, overlapping passes.

### 5.3. Lưới không gian & lịch phenology

- **Iso-Area Cell**: Ô lục giác H3 Res 7/8. Tránh: Grid square, pixel bin, lat-lon box.
- **Pentad**: Kỳ 5 ngày (73/năm). Tránh: 5-day bin, mini-week.
- **HFD**: Mật độ cháy chuẩn hóa (episodes/100km²/day). Tránh: Normalized fire count, adjusted hotspot density.
- **HRF**: Mật độ thông lượng bức xạ (MW/km²). Tránh: Calibrated FRP, total heat flux.
- **SFAI**: Z-score robust theo pentad. Tránh: Fire risk score, anomaly percent.
- **Burning Activity Calendar**: Ma trận Year × Pentad. Tránh: Fire heatmap, hotspot timeline.

### 5.4. Chế độ xử lý & vệ tinh

- **ProcessingMode**: STANDARD, NRT, RT, URT.
- **SatellitePlatform**: TERRA, AQUA, SNPP, NOAA20, NOAA21.
- **SensorType**: MODIS, VIIRS.
- **AnomalyTier**: QUIET, BASELINE, ELEVATED, SEVERE, CRISIS.

### 5.5. Kiến trúc

- **Deep Module**: Module có interface nhỏ, implementation phức tạp (Ousterhout).
- **Seam**: Điểm nối giữa module (firms-ingestion ↔ core).
- **Facade**: `FIRMSHarmonizer` compat layer.
- **Bounded in-memory map**: Map có MAX_ENTRIES + TTL + FIFO.
- **Encapsulated resource component**: Component React quản lý object URL.

---

## 6. Từ Viết Tắt (Acronyms)

| Viết tắt | Nghĩa đầy đủ |
| :--- | :--- |
| ADR | Architecture Decision Record |
| AOI | Area of Interest |
| CDF / ECDF | Cumulative Distribution Function / Empirical CDF |
| DOY | Day of Year |
| EoT | Equation of Time |
| EQM | Empirical Quantile Mapping |
| FIRMS | Fire Information for Resource Management System |
| FRP | Fire Radiative Power |
| HFD | Harmonized Fire Density |
| HRF | Harmonized Radiative Flux |
| H3 | Uber H3 Hexagonal Hierarchical Spatial Index |
| KS | Kolmogorov-Smirnov |
| MLT | Mean Local Time |
| MODIS | Moderate Resolution Imaging Spectroradiometer |
| MW | Megawatt |
| NRT / RT / URT | Near-Real-Time / Real-Time / Ultra-Real-Time |
| RMSE | Root Mean Square Error |
| SAA | South Atlantic Anomaly |
| SFAI | Standardized Fire Anomaly Index |
| SP | Standard Processing (Science Quality) |
| SZA | Solar Zenith Angle |
| UTC | Coordinated Universal Time |
| VIIRS | Visible Infrared Imaging Radiometer Suite |
| WGS-84 | World Geodetic System 1984 |

---

## 7. Đơn Vị (Units)

| Đơn vị | Ý nghĩa |
| :--- | :--- |
| km | Kilometer |
| km² | Square kilometer |
| MW | Megawatt |
| MW/km² | Megawatt per square kilometer |
| episodes/100km²/day | Episodes per 100 km² per day |
| K | Kelvin |
| deg | Degree (angle) |
| rad | Radian |
| μm | Micrometer |
| sr | Steradian |
| W·m⁻²·K⁻⁴ | Watt per square meter per Kelvin to the fourth |
| min / phút | Minute |
| % | Percent |

---


## 8. Ghi Chú Về Tính Nhất Quán Dữ Liệu (Data Consistency Notes)

Sau audit, các số liệu sau đã được hiệu chỉnh cho khớp với `data/processed/empirical_results.json`:
- Tổng detections: **1,609,194** (không phải 1,609,182).
- Số lát cắt CSV: **138** (không phải 134).
- Thời gian test: **0.004s** (không phải 0.003s).
- `n_pairs`: **11,553**; R²: **0.7330 → 0.7470**; KS: **0.1166 → 0.0237**; count ratio: **3.56×**; FRP ratio: **1.371×**.
- MODIS nadir area: **1.000 km²**; edge (55°): **9.688 km²**.
- VIIRS nadir area: **0.1305 km²**; edge (56.28°): **0.615 km²**.

Các claim trong `PROPOSAL.md`/`REPORT.md` đã được cập nhật tương ứng. Các giá trị tổng hợp (synthetic) trong calendar 26 năm (noise rng, multiplier 1.55/1.85, điền VIIRS thiếu bằng ratio) **chưa** được hiệu chỉnh — xem Q4 trong handoff.

---

*Tài liệu này là phụ lục tham chiếu. Cập nhật khi thêm ký hiệu/công thức/thuật ngữ mới.*
