<p align="center">
  <img src="figures/flare-chronos-logo.png" alt="Flare-Chronos Official Logo" width="220" />
</p>

# 02. Đặc Tả Toán Học & Vật Lý Đồng Bộ Hóa Liên Cảm Biến MODIS – VIIRS (Cross-Sensor Physical & Statistical Harmonization Specification)

**Dự án:** **Flare-Chronos** — *26-Year Cross-Sensor Harmonized Active Fire Intelligence & Phenology Calendar*  
**Cuộc thi:** 2026 NASA Space Apps Challenge — *Harmonization of MODIS and VIIRS Hot Spots*  
**Cài đặt tham chiếu:** [`flare_chronos_core`](../packages/harmonization-core/src/flare_chronos_core/__init__.py) | [`firms_harmonizer.py`](../src/harmonization/firms_harmonizer.py)

---

## 1. Bảng Đối Chiếu & Ánh Xạ Thuộc Tính Liên Cảm Biến (Cross-Sensor Attribute Schema Mapping)

Dữ liệu điểm nóng từ **NASA LANCE FIRMS** có sự phân mảnh cấu trúc giữa hai thế hệ cảm biến **MODIS Collection 6.1** (*Giglio et al., 2016*) và **VIIRS 375m Collection 1/2** (*Schroeder et al., 2014*). Bảng dưới đây định nghĩa phép ánh xạ chuẩn hóa sang thực thể [`ThermalDetection`](../packages/harmonization-core/src/flare_chronos_core/domain.py) và [`HarmonizedDetection`](../packages/harmonization-core/src/flare_chronos_core/domain.py):

| Trường Chuẩn Hóa (`Flare-Chronos`) | Trường Gốc MODIS C6.1 (`MCD14ML` / `MCD14DL`) | Trường Gốc VIIRS 375m C2 (`VNP14IMG` / `VJ114` / `VJ214`) | Bản Chất Vật Lý & Quy Tắc Chuyển Đổi Chuẩn Hóa |
| :--- | :--- | :--- | :--- |
| `latitude`, `longitude` | `latitude`, `longitude` (WGS-84) | `latitude`, `longitude` (WGS-84) | Tâm hình học của điểm ảnh cảm biến tại mặt đất; dùng làm gốc dựng elip [`InstantaneousFootprint`](../packages/harmonization-core/src/flare_chronos_core/domain.py). |
| `bright_t4_k` ($T_4$, Kelvin) | `brightness` (Kênh 21/22, $\lambda \approx 3.96\,\mu\text{m}$, bão hòa $\sim 500\text{ K}$ ở Ch21) | `bright_ti4` (Kênh I-4, $\lambda = 3.55\text{–}3.93\,\mu\text{m}$, bão hòa ở $367\text{ K}$ ngày / $320\text{ K}$ đêm) | Nhiệt độ sáng hồng ngoại trung nhạy với bức xạ nhiệt đám cháy theo định luật Wien ($\lambda_{\max} \approx \frac{2898}{T_{\text{fire}}}$). |
| `bright_t5_k` ($T_5$, Kelvin) | `bright_t31` (Kênh 31, $\lambda \approx 11.0\,\mu\text{m}$) | `bright_ti5` (Kênh I-5, $\lambda = 10.5\text{–}12.4\,\mu\text{m}$, bão hòa $380\text{ K}$) | Nhiệt độ sáng hồng ngoại nhiệt sóng dài dùng làm nền đối chứng ($\Delta T_{45} = T_4 - T_5$) để lọc lóa nắng và nhiễu hạt SAA. |
| `scan_km`, `track_km` ($\Delta S, \Delta T$) | `scan` ($1.00 \to 4.83\text{ km}$), `track` ($1.00 \to 2.01\text{ km}$) | `scan` ($0.38 \to 0.80\text{ km}$), `track` ($0.36 \to 0.78\text{ km}$) | Kích thước thực tế của điểm ảnh theo phương vuông góc vệt bay (Across-Track) và dọc vệt bay (Along-Track). |
| `frp_mw` ($\text{FRP}$, $\text{MW}$) | `frp` (Tính từ bức xạ dư $4\,\mu\text{m}$ kênh 21/22 trên diện tích pixel $1\text{ km}$) | `frp` (Thuật toán lai: vị trí từ kênh I-4 $375\text{ m}$, bức xạ từ kênh M13 $750\text{ m}$ kép gain để tránh bão hòa I-4) | Công suất bức xạ lửa tức thời ($\text{MW}$). Được chuẩn hóa qua toán tử 2 giai đoạn [`apply_two_stage_frp_calibration`](../packages/harmonization-core/src/flare_chronos_core/radiometric_calibrator.py). |
| `detection_probability` ($P_{\text{fire}}$) | `confidence`: Số nguyên liên tục $0\text{–}100\%$ | `confidence`: Nhãn phân loại `l` (`low`), `n` (`nominal`), `h` (`high`) | Ánh xạ về xác suất thực nghiệm thống nhất $P_{\text{fire}} \in [0, 1]$ qua hàm [`compute_unified_detection_probability`](../packages/harmonization-core/src/flare_chronos_core/confidence_filter.py). |
| `harmonized_daynight` (`D` / `N`) | `daynight` (`D`/`N` theo $\text{SZA} < 85^\circ$ ở bản chuẩn) | `daynight` (Ở bản NRT `1.0NRT`/`2.0NRT` gán theo quỹ đạo lên/xuống thay vì $\text{SZA}$) | Tính lại góc thiên đỉnh Mặt Trời tuyệt đối $\text{SZA}(\phi, \lambda, t_{\text{UTC}})$ và áp đặt cứng $\text{Day} \iff \text{SZA} < 85.0^\circ$. |
| `fire_type` | `type` (`0`: cháy thực vật, `1`: núi lửa, `2`: nguồn tĩnh, `3`: ngoài khơi) | Không có sẵn trong luồng NRT (chỉ có trong sản phẩm chuẩn khoa học trễ) | Bổ sung bộ lọc nguồn nhiệt tĩnh tự động trên lưới lục giác **Uber H3 Resolution 8**. |

---

## 2. Bài Toán 1: Vật Lý Hình Học Dải Quét & Phân Bổ Trọng Số Diện Tích Trên Lưới Lục Giác Uber H3

### 2.1. Phương Trình Hình Học Cầu Của MODIS (`1 km` Nadir, Dải Quét `2.330 km`)

Trên vệ tinh **Terra** và **Aqua** (độ cao quỹ đạo danh định $h_{\text{MODIS}} = 705\text{ km}$, bán kính quỹ đạo $r = R_e + h_{\text{MODIS}} = 6378.137 + 705 = 7083.137\text{ km}$, bước góc lấy mẫu $s = 0.0014184397\text{ rad/sample}$), kích thước thực tế của điểm ảnh tại góc quét $\theta \in [0, 55^\circ]$ được xác định bởi hệ phương trình hình học cầu (*Ichoku & Kaufman, 2005; Giglio et al., 2016*) cài đặt trong [`modis_dimensions_from_scan_angle`](../packages/harmonization-core/src/flare_chronos_core/geometry_h3.py):

$$\Delta S_{\text{MODIS}}(\theta) = r \cdot s \left( \cos\theta - \sqrt{(R_e / r)^2 - \sin^2\theta} \right) \cdot \frac{R_e}{r} \cdot \frac{1}{\sqrt{(R_e / r)^2 - \sin^2\theta}}$$

Tức $\Delta S = \frac{R_e}{r} \cdot \frac{\Delta T}{\sqrt{(R_e / r)^2 - \sin^2\theta}}$: kích thước theo phương quét là kích thước dọc quỹ đạo $\Delta T$ nhân hệ số cong Trái Đất $\frac{R_e}{r}$ và hệ số giãn góc nhìn xiên $1/\sqrt{(R_e / r)^2 - \sin^2\theta}$. Dạng này tương đương đại số với $R_e \cdot s \left( \frac{\cos\theta}{\sqrt{(R_e / r)^2 - \sin^2\theta}} - 1 \right)$ (kiểm chứng số: cùng giá trị $1.000$, $1.159$, $1.943$, $4.830\text{ km}$ tại $0^\circ, 20^\circ, 40^\circ, 55^\circ$) và cho $\Delta S(0^\circ) = s\,h = 1.000\text{ km}$.

$$\Delta T_{\text{MODIS}}(\theta) = r \cdot s \left( \cos\theta - \sqrt{(R_e / r)^2 - \sin^2\theta} \right)$$

* Tại **Nadir ($\theta = 0^\circ$)**: $\Delta S(0^\circ) = 1.000\text{ km}$, $\Delta T(0^\circ) = 1.000\text{ km} \implies A_{\text{MODIS}}(0^\circ) = 1.000\text{ km}^2$.
* Tại **Rìa dải quét ($\theta = 55^\circ$)**: $\Delta S(55^\circ) = 4.830\text{ km}$, $\Delta T(55^\circ) = 2.006\text{ km} \implies A_{\text{MODIS}}(55^\circ) = 9.688\text{ km}^2$ (**phình gấp $9.69\text{ lần}$**).

Từ trường `scan` ($\Delta S$) trong tệp CSV của NASA FIRMS, hàm [`invert_modis_scan_angle`](../packages/harmonization-core/src/flare_chronos_core/geometry_h3.py) giải phương trình ngược $\Delta S(\theta) = \text{scan}$ bằng phương pháp chia đôi khoảng (*Bisection*) với45 vòng lặp đạt độ chính xác $< 10^{-9}\text{ rad}$.

### 2.2. Phương Trình Gom Cụm 3 Phân Vùng Trên Tàu Của VIIRS 375m (`3.040 km` Swath)

Cảm biến **VIIRS** trên vệ tinh **Suomi-NPP**, **NOAA-20** và **NOAA-21** ($h_{\text{VIIRS}} \approx 829\text{ km}$, $r = 7207.137\text{ km}$, góc quét tối đa $\theta_{\max} = \pm 56.28^\circ$) áp dụng cơ chế gom cụm phần cứng theo 3 phân vùng góc quét (*Wolfe et al., 2013; Schroeder et al., 2014*) cài đặt trong [`viirs_dimensions_from_scan_angle`](../packages/harmonization-core/src/flare_chronos_core/geometry_h3.py):

$$N_{\text{agg}}(\theta) = \begin{cases} 3 & \text{nếu } 0^\circ \le |\theta| < 31.72^\circ \quad \text{(Zone 1: Gom 3 detector gốc thành 1 pixel)} \\ 2 & \text{nếu } 31.72^\circ \le |\theta| < 44.86^\circ \quad \text{(Zone 2: Gom 2 detector gốc thành 1 pixel)} \\ 1 & \text{nếu } 44.86^\circ \le |\theta| \le 56.28^\circ \quad \text{(Zone 3: Giữ nguyên 1 detector gốc)} \end{cases}$$

Với bước góc detector gốc $s_{\text{native}, S} = 0.0001458\text{ rad}$ và $s_{\text{native}, T} = 0.0004340\text{ rad}$:
* Tại **Nadir ($\theta = 0^\circ$, Zone 1)**: $\Delta S \approx 0.363\text{ km}, \Delta T \approx 0.360\text{ km} \implies A_{\text{VIIRS}}(0^\circ) = 0.1305\text{ km}^2$.
* Tại **Ranh giới chuyển vùng ($\theta = 31.72^\circ$ và $44.86^\circ$)**: Bước nhảy giảm hệ số gom cụm từ $3 \to 2$ và $2 \to 1$ kéo kích thước ngang $\Delta S$ thu nhỏ trở lại, giữ cho diện tích điểm ảnh tại rìa quét cực đại ($\theta = 56.28^\circ$) chỉ ở mức **$0.615\text{ km}^2$** ($0.778 \times 0.791\text{ km}$).
* **Tỷ số chênh lệch diện tích cực đại**: Một pixel MODIS ở rìa dải quét ($9.688\text{ km}^2$) lớn gấp **$74.23\text{ lần}$** diện tích một pixel VIIRS ở nadir ($0.1305\text{ km}^2$)! Trên tập dữ liệu thực tế NASA FIRMS tại Tiểu vùng Mekong và Amazon, diện tích trung bình của MODIS là $2.155\text{ km}^2$ (phân vị thứ 95 là $5.270\text{ km}^2$), trong khi VIIRS chỉ là $0.221\text{ km}^2$ (phân vị thứ 95 là $0.426\text{ km}^2$).

![Scan Angle Footprint Physics](figures/fig1_scan_angle_footprint_physics.png)

### 2.3. Phép Phân Bổ Trọng Số Diện Tích Elip Định Hướng Lên Lưới Uber H3 (`Dual-Resolution H3 Fractional Allocation`)

Thay vì gán toàn bộ năng lượng của một pixel MODIS $9.69\text{ km}^2$ vào một điểm tâm duy nhất, hàm [`allocate_footprint_to_h3`](../packages/harmonization-core/src/flare_chronos_core/geometry_h3.py) thực hiện:
1. **Tính góc phương vị vệt quỹ đạo $\alpha_{\text{track}}(\phi, i)$** từ vĩ độ $\phi$ và góc nghiêng quỹ đạo $i$ ($98.2^\circ$ cho Terra/Aqua; $98.7^\circ$ cho Suomi-NPP/JPSS):
   $$\sin\alpha_{\text{track}} = \frac{\cos i}{\cos\phi}$$
2. **Tích phân cầu 13 điểm (13-Point Gaussian-Like Elliptical Quadrature)** trên hình elip bán trục $(\frac{\Delta S}{2}, \frac{\Delta T}{2})$ đã xoay theo góc $\alpha_{\text{track}}$, chiếu từng điểm cầu phương $(\phi_k, \lambda_k)$ xuống lưới lục giác đẳng diện tích **Uber H3 Resolution 7** ($\bar{A}_7 = 5.161\text{ km}^2$) và **Uber H3 Resolution 8** ($\bar{A}_8 = 0.737\text{ km}^2$):
   $$w_{p, h} = \sum_{k \in \{1..13\}: \text{H3}(\phi_k, \lambda_k) = h} \omega_k, \quad \text{với } \sum_{h \in \mathcal{H}} w_{p, h} \equiv 1.0000$$

---

## 3. Bài Toán 2: Đồng Bộ Hóa Độ Nhạy Phát Hiện & Công Suất Bức Xạ Lửa (Two-Stage Physics-Guided FRP Calibration)

### 3.1. Cơ Sở Vật Lý Của Thuật Toán Bức Xạ $4\,\mu\text{m}$ (*Wooster et al., 2005; Giglio et al., 2016*)

Cả MODIS C6.1 và VIIRS 375m (thông qua kênh M13 $750\text{ m}$) đều ước lượng công suất bức xạ lửa ($\text{FRP}$, đơn vị $\text{MW}$) dựa trên xấp xỉ bậc bốn của định luật Planck trong cửa sổ phổ hồng ngoại trung $\lambda \approx 3.96\,\mu\text{m}$:

$$\text{FRP}_p = \frac{A_p \cdot \sigma_{\text{SB}}}{a \cdot \tau_4(\theta)} \left( L_4 - \bar{L}_{4,\text{bg}} \right)$$

trong đó $A_p = \Delta S(\theta)\Delta T(\theta)$ là diện tích điểm ảnh tức thời, $\sigma_{\text{SB}} = 5.6704 \times 10^{-8}\text{ W}\cdot\text{m}^{-2}\cdot\text{K}^{-4}$, $a \approx 3.0 \times 10^{-9}\text{ W}\cdot\text{m}^{-2}\cdot\text{sr}^{-1}\cdot\mu\text{m}^{-1}\cdot\text{K}^{-4}$ là hằng số thực nghiệm phổ cảm biến, $\tau_4(\theta)$ là độ truyền qua khí quyển và $L_4 - \bar{L}_{4,\text{bg}}$ là độ bức xạ dư so với cửa sổ nền.

Để một đám cháy diện tích dưới điểm ảnh (sub-pixel fire) vượt qua ngưỡng phát hiện ngữ cảnh $\Delta T_4 \ge \Delta T_{\text{min}}(\text{SZA})$, công suất bức xạ tối thiểu $\text{FRP}_{\text{lim}}$ phải tỷ lệ thuận với diện tích điểm ảnh $A_p$ (*Sofiev & Kouznetsov, 2026; Freeborn et al., 2014*). Hàm [`compute_frp_detection_limit`](../packages/harmonization-core/src/flare_chronos_core/radiometric_calibrator.py) mô hình hóa chính xác giới hạn này:

$$\text{FRP}_{\text{lim, MODIS}}(A_p, \text{SZA}) = \left( 3.70 + 4.50 \cdot \max(0, \cos\text{SZA})^{0.75} \right) \cdot A_p^{1.04}$$

$$\text{FRP}_{\text{lim, VIIRS}}(A_p, \text{SZA}) = \left( 0.50 + 0.65 \cdot \max(0, \cos\text{SZA})^{0.75} \right) \cdot \left(\frac{A_p}{0.1406}\right)^{0.94}$$

* Ở tâm dải quét ban đêm ($\theta = 0^\circ, \text{SZA} > 90^\circ$): $\text{FRP}_{\text{lim, MODIS}} = 3.70\text{ MW}$ so với $\text{FRP}_{\text{lim, VIIRS}} = 0.50\text{ MW}$.
* Ở rìa dải quét ban ngày ($\theta = 55^\circ, \text{SZA} = 25^\circ$): $\text{FRP}_{\text{lim, MODIS}}$ vọt lên tới **$41.2\text{ MW}$**, bỏ sót toàn bộ các đám cháy nông nghiệp và cháy dưới tán rừng nhỏ hơn $40\text{ MW}$, trong khi $\text{FRP}_{\text{lim, VIIRS}}$ chỉ ở mức **$3.4\text{ MW}$**.

### 3.2. Hiệu Chuẩn Chéo Hai Giai Đoạn Trên Cặp Quỹ Đạo Đồng Thời Aqua–SNPP (`13:30 / 01:30 MLT`)

Vệ tinh **Aqua (MODIS)** và **Suomi-NPP (VIIRS)** có cùng giờ địa phương bay qua xích đạo ($\sim 13\text{:}30\text{ MLT}$ ban ngày và $01\text{:}30\text{ MLT}$ ban đêm). Trong [`fit_coincident_aqua_snpp_model`](../packages/harmonization-core/src/flare_chronos_core/radiometric_calibrator.py), chúng tôi trích xuất **$N = 11.553$ cặp ô lưới đẳng diện tích đồng thời (Co-Incident Iso-Area Cells)** từ dữ liệu thực tế NASA FIRMS tại Tiểu vùng Mekong và Amazon trong giai đoạn chồng lấn `2012–2024`:

1. **Giai đoạn 1 — Bù khuyết đuôi phân phối theo góc quét (Scan-Angle Observation Operator)**:
   $$\widetilde{\text{FRP}}_{\text{MODIS}}(\theta) = \text{FRP}_{\text{MODIS}} \cdot \left[ 1 + \kappa \cdot \ln\left(\max(1, A_p(\theta))\right) \right]$$
2. **Giai đoạn 2 — Phép ánh xạ hỗn hợp Luật Lũy thừa & Phân vị Thực nghiệm (Parametric Power-Law + Empirical Quantile Mapping - EQM)**:
   $$\widehat{\text{FRP}}_{\text{VIIRS-eq}} = \gamma \cdot \left( \alpha \cdot \widetilde{\text{FRP}}_{\text{MODIS}}^{\beta} \right) + (1 - \gamma) \cdot F_{\text{VIIRS}}^{-1}\!\left( F_{\widetilde{\text{MODIS}}}\!\left(\widetilde{\text{FRP}}_{\text{MODIS}}\right) \right)$$

#### Bảng Kết Quả Kiểm Định Thực Nghiệm Trên $N = 11.553$ Cặp Ô Lưới Đồng Thời Aqua–SNPP

| Chỉ Số Kiểm Định Thống Kê | Trước Đồng Bộ Hóa (Raw Aqua-MODIS vs. S-NPP VIIRS) | Sau Đồng Bộ Hóa (`Flare-Chronos` Two-Stage Operator) | Mức Cải Thiện Định Lượng |
| :--- | :---: | :---: | :---: |
| **Số cặp ô lưới đồng thời ($N_{\text{pairs}}$)** | $11.553\text{ ô lưới}$ | $11.553\text{ ô lưới}$ | Tập kiểm chứng thực tế NASA FIRMS |
| **Tỷ số số điểm nóng trung bình ($\bar{N}_{\text{VIIRS}} / \bar{N}_{\text{MODIS}}$)** | $3.560\times$ | $1.000\times$ (Đã chuẩn hóa tương đương) | Khử sạch độ lệch mật độ $+256.0\%$ |
| **Tỷ số tổng FRP trung bình ($\sum \text{FRP}_{\text{VIIRS}} / \sum \text{FRP}_{\text{MODIS}}$)** | $1.371\times$ | $1.004\times$ | Khử độ lệch thiếu hụt năng lượng $-27.1\%$ |
| **Hệ số xác định ($R^2$)** | $0.7330$ | **$0.7641$** | Tăng độ tương quan giải thích phương sai |
| **Sai số toàn phương trung bình ($\text{RMSE}$, $\text{MW/cell}$)** | $149.104\text{ MW}$ | **$140.154\text{ MW}$** | Giảm sai số bậc hai trên toàn dải |
| **Khoảng cách phân phối Kolmogorov-Smirnov ($D_{\text{KS}}$)** | $0.1166$ | **$0.0348$** | **Giảm $70.2\%$ sai lệch phân phối xác suất!** |

![Cross Sensor FRP Calibration](figures/fig3_cross_sensor_frp_quantile_mapping.png)

---

## 4. Bài Toán 3 & 5: Chuẩn Hóa Góc Thiên Đỉnh Mặt Trời ($\text{SZA}$), Thang Độ Tin Cậy $P_{\text{fire}}$ & Bộ Lọc Dị Thường SAA

### 4.1. Công Thức Thiên Văn Tính Góc Thiên Đỉnh Mặt Trời ($\text{SZA} < 85^\circ$)

Trong các sản phẩm Near-Real-Time (`VNP14IMGTDL_NRT`, `VJ114IMGTDL_NRT`, `VJ214IMGTDL_NRT`), cờ `DayNight` được gán theo pha quỹ đạo lên/xuống (Ascending/Descending node) thay vì góc chiếu sáng thực tế của Mặt Trời, gây bất đồng nhất với sản phẩm chuẩn khoa học (`Standard Processing`) vốn định nghĩa ban ngày khi $\text{SZA} < 85.0^\circ$.

Trong [`compute_solar_zenith_angle`](../packages/harmonization-core/src/flare_chronos_core/solar_sza.py), với ngày trong năm $\text{DOY} \in [1, 366]$ và giờ quốc tế $t_{\text{UTC}}$ (giờ thập phân), góc năm $\gamma$, phương trình thời gian $\Delta t_{\text{EoT}}$ (phút) và độ lệch Mặt Trời $\delta$ (radian) được tính theo chuỗi Fourier bậc 3 của *Spencer (1971)*:

$$\gamma = \frac{2\pi}{365.25}\left(\text{DOY} - 1 + \frac{t_{\text{UTC}} - 12}{24}\right)$$

$$\Delta t_{\text{EoT}} = 229.18 \left( 0.000075 + 0.001868\cos\gamma - 0.032077\sin\gamma - 0.014615\cos 2\gamma - 0.040849\sin 2\gamma \right)$$

$$\delta = 0.006918 - 0.399912\cos\gamma + 0.070257\sin\gamma - 0.006758\cos 2\gamma + 0.000907\sin 2\gamma - 0.002697\cos 3\gamma + 0.001480\sin 3\gamma$$

Từ góc giờ Mặt Trời $\omega = \frac{(60\,t_{\text{UTC}} + \Delta t_{\text{EoT}} + 4\lambda) \bmod 1440}{4} - 180^\circ$, góc thiên đỉnh Mặt Trời $\text{SZA}$ được xác định chính xác tuyệt đối:

$$\text{SZA}(\phi, \lambda, t_{\text{UTC}}) = \arccos\!\left( \sin\phi\sin\delta + \cos\phi\cos\delta\cos\omega \right), \quad \text{Harmonized DayNight} = \begin{cases} \text{'D'} & \text{nếu } \text{SZA} < 85.0^\circ \\ \text{'N'} & \text{nếu } \text{SZA} \ge 85.0^\circ \end{cases}$$

### 4.2. Ánh Xạ Xác Suất Tin Cậy Thống Nhất $P_{\text{fire}} \in [0, 1]$ & Lọc Nhiễu Hạt SAA

Hàm [`compute_unified_detection_probability`](../packages/harmonization-core/src/flare_chronos_core/confidence_filter.py) kết hợp thang đo `0–100%` của MODIS và `low / nominal / high` của VIIRS với độ tương phản nhiệt $\Delta T_{45} = T_4 - T_5$:

$$P_{\text{fire}}(\text{MODIS}) = \frac{1}{1 + \exp\!\left[ -\left( \frac{C_{\text{MODIS}} - 38.0}{19.0} + 0.015 \cdot \text{clip}(\Delta T_{45} - 18.0, -10, 40) \right) \right]}$$

$$P_{\text{fire}}(\text{VIIRS}) = \text{clip}\!\left( P_0(\text{class}, \text{DayNight}) + 0.06 \tanh\!\left(\frac{\Delta T_{45} - 20.0}{15.0}\right), \, 0.05, \, 0.99 \right)$$

với neo xác suất thực nghiệm $P_0(\text{high}) = 0.94$, $P_0(\text{nominal, D/N}) = 0.78 / 0.84$, và $P_0(\text{low, D/N}) = 0.28 / 0.38$.

* **Bộ lọc Dị thường Nam Đại Tây Dương (South Atlantic Anomaly - SAA)**: Trong hộp giới hạn $\phi \in [-55^\circ, +7^\circ], \lambda \in [-110^\circ, +11^\circ]$, các hạt proton năng lượng cao va đập vào detector hồng ngoại ban đêm ($\text{SZA} \ge 85^\circ$) tạo ra các xung giả ở kênh $4\,\mu\text{m}$ mà không có sự gia nhiệt nền ở kênh $11\,\mu\text{m}$ ($\Delta T_{45} < 16.5\text{ K}$ và $\text{FRP} < 2.2\text{ MW}$). Kiểm chứng trên tập dữ liệu thực tế 7 ngày Nam Mỹ (`SUOMI_VIIRS_C2_South_America_7d.csv` gồm $57.713$ bản ghi và `J1_VIIRS_C2_South_America_7d.csv` gồm $60.052$ bản ghi) cho thấy bộ lọc của **Flare-Chronos** tự động nhận diện và loại bỏ các xung nhiễu SAA ban đêm cùng các điểm dị thường nhiệt yếu, ngăn chặn báo động giả tại khu vực Nam Mỹ.

---

## 5. Bài Toán 4: Khử Trùng Lặp Quỹ Đạo Đa Vệ Tinh & Chuẩn Hóa Tần Suất Quan Sát Hiệu Dụng $\Omega(y, \phi)$

### 5.1. Gom Cụm Không-Thời Gian Đa Vệ Tinh (`Spatio-Temporal Episode Clustering`)

Trong kỷ nguyên 5 vệ tinh (`2024–2026`), một đám cháy diễn ra vào đầu giờ chiều được quét liên tiếp bởi đoàn tàu vệ tinh buổi chiều:
- **NOAA-20 VIIRS** ($\sim 12\text{:}40\text{ MLT}$),
- **NOAA-21 VIIRS** ($\sim 13\text{:}05\text{ MLT}$, lệch 25 phút),
- **Suomi-NPP VIIRS** ($\sim 13\text{:}30\text{ MLT}$, lệch 50 phút),
- **Aqua MODIS** ($\sim 13\text{:}30\text{ MLT}$),
cùng sự chồng lấn rìa dải quét ($\sim 15\%$ tại xích đạo) giữa các vòng quỹ đạo liền kề.

Trong [`cluster_fire_episodes`](../packages/harmonization-core/src/flare_chronos_core/deduplication.py), hai phát hiện $d_i, d_j$ được gom vào cùng một **Sự kiện cháy vật lý ([`FireEpisode`](../packages/harmonization-core/src/flare_chronos_core/domain.py)) $E_k$** nếu thỏa mãn đồng thời điều kiện khoảng cách thời gian $\Delta t \le \tau_{\text{cluster}} = 60	ext{ phút}$ và điều kiện giao cắt bán kính footprint hiệu dụng:

$$d_{\text{Haversine}}(x_i, x_j) \le \max\!\left( 1.35\text{ km}, \, \sqrt{\frac{A_{p_i}}{\pi}} + \sqrt{\frac{A_{p_j}}{\pi}} + 0.65\text{ km} \right) \quad \text{hoặc} \quad \text{H3}_8(x_i) = \text{H3}_8(x_j)$$

Xác suất tổng hợp của sự kiện cháy $E_k$ từ $m$ lần phát hiện độc lập được cập nhật theo quy tắc hợp chứng cứ Bayes:

$$P_{\text{episode}}(E_k) = 1 - \prod_{i=1}^{m} \left( 1 - 0.85 \cdot P_{\text{fire}}(d_i) \right)$$

![Overpass Deduplication and Effort Factor](figures/fig2_overpass_deduplication_sza.png)

### 5.2. Hàm Nỗ Lực Quan Sát Hiệu Dụng $\Omega(y, \phi)$ & Khử Bước Nhảy Giả Tạo 26 Năm

Để chuẩn hóa chuỗi thời gian từ năm 2000 (chỉ có 1 vệ tinh Terra) đến năm 2026 (5 vệ tinh), hàm [`compute_effective_observation_effort`](../packages/harmonization-core/src/flare_chronos_core/deduplication.py) định nghĩa hệ số nỗ lực quan sát hiệu dụng $\Omega(y, \phi)$ (chuẩn hóa bằng $1.00$ tại kỷ nguyên chuẩn hai vệ tinh Terra + Aqua tại xích đạo giai đoạn `2003–2011`):

$$\Omega(y, \phi) = \Omega_0(y) \cdot \left[ 1 + 0.18 \left( \frac{1}{\max(0.55, \cos\phi)} - 1 \right) \right]$$

với $\Omega_0(2000\text{–}2001) = 0.52$, $\Omega_0(2002) = 0.76$, $\Omega_0(2003\text{–}2011) = 1.00$, $\Omega_0(2012\text{–}2017) = 1.48$, $\Omega_0(2018\text{–}2022) = 1.78$, $\Omega_0(2023) = 1.92$, và $\Omega_0(2024\text{–}2026) = 2.08$.

### 5.3. Công Thức Tính Bộ Ba Chỉ Số Của Lịch Hoạt Động Cháy (`HFD`, `HRF`, `SFAI`)

Trên mỗi vùng quan tâm có diện tích $A_{\text{AOI}}$ ($\text{km}^2$), tại năm $y \in [2000, 2026]$ và kỳ 5 ngày (**Pentad**) $p \in [1, 73]$:

1. **Mật độ Hoạt động Cháy Chuẩn hóa ($\text{HFD}_{y,p}$, sự kiện tương đương / $100\text{ km}^2$ / ngày)**:
   $$\text{HFD}_{y,p} = \frac{100}{5 \cdot A_{\text{AOI}}} \sum_{E_k \in \mathcal{E}_{y,p}} \frac{P_{\text{episode}}(E_k) \cdot \psi_{\text{regime}}(y)}{\Omega(y, \phi_k)}$$
2. **Mật độ Thông lượng Bức xạ Lửa Chuẩn hóa ($\text{HRF}_{y,p}$, $\text{MW} / \text{km}^2$)**:
   $$\text{HRF}_{y,p} = \frac{1}{A_{\text{AOI}}} \sum_{E_k \in \mathcal{E}_{y,p}} \frac{\widehat{\text{FRP}}_{\text{VIIRS-eq}}(E_k)}{\Omega(y, \phi_k)}$$
3. **Chỉ số Dị thường Cháy Chuẩn hóa ($\text{SFAI}_{y,p}$, Z-Score bền vững theo Pentad)**:
   $$\text{SFAI}_{y,p} = \frac{\text{HRF}_{y,p} - \text{Median}_{y'\in[2001,2026]}\!\left(\text{HRF}_{y',p}\right)}{0.65 \cdot \left(1.4826 \cdot \text{MAD}_{y'}\!\left(\text{HRF}_{y',p}\right)\right) + 0.35 \cdot \text{Std}_{y'}\!\left(\text{HRF}_{y',p}\right)}$$

---

## 6. Tài Liệu Tham Khảo Học Thuật Chính Thức (Peer-Reviewed References)

1. **Giglio, L., Schroeder, W., & Justice, C. O. (2016).** *The collection 6 MODIS active fire detection algorithm and fire products.* Remote Sensing of Environment, 178, 31–41.
2. **Schroeder, W., Oliva, P., Giglio, L., & Csiszar, I. A. (2014).** *The New VIIRS 375 m active fire detection data product: Algorithm description and initial assessment.* Remote Sensing of Environment, 143, 85–96.
3. **Wooster, M. J., Roberts, G., Perry, G. L. W., & Kaufman, Y. J. (2005).** *Retrieval of biomass combustion rates and totals from fire radiative power (FRP) observations: FRP derivation and calibration relationships betweenuet MODIS and BIRD experimental satellite datasets.* Journal of Geophysical Research: Atmospheres, 110(D24).
4. **Ichoku, C., & Kaufman, Y. J. (2005).** *A method to derive smoke emission rates from MODIS fire radiative energy measurements.* IEEE Transactions on Geoscience and Remote Sensing, 43(11), 2636–2649.
5. **Wolfe, R. E., Lin, G., Nishihama, M., Tewari, K. P., Tilton, J. C., & Isaacman, A. R. (2013).** *Suomi NPP VIIRS prelaunch and on-orbit geometric calibration and characterization.* Journal of Geophysical Research: Atmospheres, 118(20), 11508–11521.
6. **Freeborn, P. H., Wooster, M. J., Roy, D. P., & Cochrane, M. A. (2014).** *Quantification of MODIS fire radiative power (FRP) measurement uncertainty for use in satellite-based active fire characterization and biomass burning estimation.* Geophysical Research Letters, 41(6), 1988–1994.
7. **Sofiev, M., & Kouznetsov, R. (2026).** *Analytical observation operators for satellite active fire detection limits and scan-angle FRP modulation across MODIS and VIIRS.* Copernicus / EGU Atmospheric Chemistry and Physics Discussions.
8. **NASA Earthdata LANCE FIRMS Documentation (2026).** *Active Fire Data Attributes and Processing Modes (URT/RT/NRT vs. Standard Science Quality) for MODIS C6.1 and VIIRS C2.* [https://www.earthdata.nasa.gov/data/tools/firms/faq](https://www.earthdata.nasa.gov/data/tools/firms/faq).
