# BẢN ĐỀ XUẤT KỸ THUẬT & THUYẾT MINH DỰ ÁN TOÀN DIỆN (MASTER TECHNICAL PROPOSAL)
# 🔥 FLARE-CHRONOS: Hệ Thống Đồng Bộ Hóa Vật Lý Liên Cảm Biến MODIS–VIIRS & Lịch Hoạt Động Cháy Thông Minh 26 Năm (2000–2026+)

> **Tên viết tắt (Acronym):** **FLARE-CHRONOS** (*Fire Long-term Archive Resolution & Cross-sensor Harmonization for Operational Near-real-time Observation System*)  
> **Thử thách (Challenge):** [Harmonization of MODIS and VIIRS Hot Spots](https://www.spaceappschallenge.org/2026/challenges/harmonization-of-modis-and-viirs-hot-spots/) — *2026 NASA Space Apps Challenge*  
> **Tác giả / Nhóm phát triển:** Lê Thành Trung (`lethanhtrung.trungle@gmail.com`)  
> **Kho mã nguồn & Kiến trúc Monorepo:** [`packages/harmonization-core`](file:///Users/xirothedev/workspace/flare-chronos/packages/harmonization-core/src/flare_chronos_core/__init__.py) | [`packages/firms-ingestion`](file:///Users/xirothedev/workspace/flare-chronos/packages/firms-ingestion/src/firms_ingestion/firms_client.py) | [`apps/benchmark-cli`](file:///Users/xirothedev/workspace/flare-chronos/apps/benchmark-cli/src/benchmark_cli/run_experiments.py) | [`src/harmonization/firms_harmonizer.py`](file:///Users/xirothedev/workspace/flare-chronos/src/harmonization/firms_harmonizer.py)  
> **Từ điển Miền & Hồ sơ Quyết định Kiến trúc (ADRs):** [GLOSSARY.md](file:///Users/xirothedev/workspace/flare-chronos/GLOSSARY.md) | [ADR-0001](file:///Users/xirothedev/workspace/flare-chronos/docs/adr/0001-dual-resolution-h3-fractional-allocation.md) | [ADR-0002](file:///Users/xirothedev/workspace/flare-chronos/docs/adr/0002-two-stage-physics-guided-frp-harmonization.md) | [ADR-0003](file:///Users/xirothedev/workspace/flare-chronos/docs/adr/0003-spatio-temporal-episode-deduplication-and-effort-normalization.md) | [ADR-0004](file:///Users/xirothedev/workspace/flare-chronos/docs/adr/0004-monorepo-deep-module-architecture.md)

---

## PHẦN 1: TÓM TẮT ĐIỀU HÀNH & ĐẶT VẤN ĐỀ KHOA HỌC (EXECUTIVE SUMMARY & PROBLEM STATEMENT)

### 1.1. Tóm Tắt Điều Hành (Three-Sentence Value Proposition)

> **Flare-Chronos** là nền tảng khoa học và phần mềm mã nguồn mở giải quyết sự đứt gãy lịch sử dài 26 năm giữa thế hệ cảm biến vệ tinh **MODIS** (`Terra/Aqua`, độ phân giải nadir $1\text{ km}$, `2000–2026`) đang dần ngừng hoạt động và thế hệ cảm biến kế nhiệm **VIIRS** (`Suomi-NPP/NOAA-20/NOAA-21`, độ phân giải nadir $375\text{ m}$, `2012–2026+`). Bằng cách thay thế phép đếm điểm thô bằng **5 thuật toán vật lý – thống kê** (phân bổ trọng số diện tích elip dải quét $\Delta S(\theta)\times\Delta T(\theta)$ lên lưới lục giác đẳng diện tích **Uber H3**, toán tử quan sát bức xạ $4\,\mu\text{m}$ hai giai đoạn, chuẩn hóa góc thiên đỉnh Mặt Trời $\text{SZA} < 85^\circ$, lọc nhiễu hạt Nam Đại Tây Dương, và gom cụm sự kiện cháy đa vệ tinh chuẩn hóa theo nỗ lực quan sát $\Omega(y, \phi)$), hệ thống đã được kiểm chứng thực nghiệm trên **$775.531$ điểm nóng thực tế từ NASA LANCE FIRMS**, giảm **$82,6\%$** sai số phân phối Kolmogorov-Smirnov ($D_{\text{KS}}$ từ $0.1180$ xuống $0.0205$ trên $N=5.769$ cặp ô lưới đồng thời). Đầu ra cốt lõi của hệ thống là **Lịch Hoạt Động Cháy Thống Nhất 26 Năm (*Harmonized Burning Activity Calendar*)** cấu trúc theo ma trận `26 Năm × 73 Pentads` cùng chỉ số cảnh báo sớm **$\text{SFAI Z-Score}$**, giúp lực lượng cứu hỏa, nhà quản lý lâm nghiệp và nhà khoa học khí hậu phân biệt chính xác mùa đốt phụ phẩm nông nghiệp định kỳ với các đợt khủng hoảng cháy rừng ngoài mùa vụ mà không bị đánh lừa bởi bước nhảy giả tạo $+1.324\%$ do tăng số lượng vệ tinh.

### 1.2. Cuộc Chuyển Giao Thế Hệ Cảm Biến Năm 2026 & 5 Rào Cản Vật Lý Liên Cảm Biến

Trong hơn hai thập kỷ rưỡi qua, hệ thống **NASA FIRMS (Fire Information for Resource Management System)** đã trở thành hạ tầng quan sát điểm nóng cháy toàn cầu quan trọng nhất của nhân loại. Tuy nhiên, vào năm **2026**, cộng đồng khoa học Trái Đất đang đứng trước một cuộc chuyển giao lịch sử:
- Cặp vệ tinh **Terra** (phóng tháng 12/1999, dữ liệu từ 11/2000) và **Aqua** (phóng tháng 05/2002) mang cảm biến **MODIS** đang ở giai đoạn cuối sứ mệnh sau hơn 24–26 năm hoạt động.
- Vệ tinh **Suomi-NPP** (phóng cuối năm 2011, dữ liệu VIIRS từ 01/2012) cũng tiến tới giai đoạn kết thúc vòng đời vào khoảng tháng 10/2026, chuyển giao trọng trách quan sát nhiệt cho chùm vệ tinh **JPSS** gồm **NOAA-20 (`J1`, từ 2018/2020)** và **NOAA-21 (`J2`, từ 2023/2024)**.

Khi các nhà quản lý rừng hoặc nhà nghiên cứu ghép nối trực tiếp chuỗi dữ liệu **MODIS Collection 6.1** (*Giglio et al., 2016*) và **VIIRS 375m Collection 1/2** (*Schroeder et al., 2014*), họ vấp phải **5 rào cản vật lý và quỹ đạo** làm biến dạng hoàn toàn chuỗi thời gian:

| Rào Cản Vật Lý & Kỹ Thuật | Cảm Biến MODIS Collection 6.1 (`MCD14ML` / `MCD14DL`) | Cảm Biến VIIRS 375m Collection 2 (`VNP14IMG` / `VJ114` / `VJ214`) | Hệ Quả Sai Lệch Nếu Không Đồng Bộ Hóa (Đã Kiểm Chứng Trên Dữ Liệu Thực NASA FIRMS) |
| :--- | :--- | :--- | :--- |
| **1. Hình học điểm ảnh & Hiệu ứng rìa dải quét (*Bow-Tie Distortion*)** | Độ cao $h = 705\text{ km}$, dải quét $2.330\text{ km}$ ($\theta_{\max} = \pm 55^\circ$). Điểm ảnh không gom cụm: từ **$1.00 \times 1.00\text{ km}$ ($1.00\text{ km}^2$)** ở nadir phình ra tới **$4.83 \times 2.01\text{ km}$ ($9.69\text{ km}^2$)** ở rìa quét (*Ichoku & Kaufman, 2005*). | Độ cao $h \approx 829\text{ km}$, dải quét $3.040\text{ km}$ ($\theta_{\max} = \pm 56.28^\circ$). Áp dụng gom cụm phần cứng 3 vùng (*Wolfe et al., 2013*): Zone 1 ($0^\circ\text{–}31.72^\circ$, gom $3:1$), Zone 2 ($31.72^\circ\text{–}44.86^\circ$, gom $2:1$), Zone 3 ($44.86^\circ\text{–}56.28^\circ$, giữ $1:1$). Diện tích chỉ từ **$0.131\text{ km}^2$** đến tối đa **$0.615\text{ km}^2$**. | Diện tích 1 pixel MODIS ở rìa quét lớn gấp **$74,23\text{ lần}$** 1 pixel VIIRS ở tâm quét! Coi điểm nóng là tọa độ điểm $(lat, lon)$ gây sai số định vị diện tích cháy lên tới $\pm 5\text{ km}$. |
| **2. Độ nhạy phát hiện & Công suất bức xạ lửa ($\text{FRP}$)** | Dùng kênh 21/22 ($\lambda \approx 3.96\,\mu\text{m}$) và kênh 31 ($11\,\mu\text{m}$). Ngưỡng phát hiện tối thiểu $\text{FRP}_{\text{lim}}$ ở nadir là $3.7\text{ MW}$ (đêm) / $8.2\text{ MW}$ (ngày), nhưng tăng vọt lên **$38.6\text{–}41.2\text{ MW}$** ở góc quét $55^\circ$ (*Sofiev & Kouznetsov, 2026*). | Phát hiện vị trí trên kênh I-4 ($375\text{ m}$, $3.55\text{–}3.93\,\mu\text{m}$); nhưng do I-4 bão hòa ở $367\text{ K}$ (ngày) / $320\text{ K}$ (đêm), $\text{FRP}$ được tính lai từ kênh M13 ($750\text{ m}$, dual-gain). Ngưỡng phát hiện $\text{FRP}_{\text{lim}} \approx 0.50\text{ MW}$ (đêm) và $\le 3.4\text{ MW}$ ở rìa quét ngày. | MODIS bỏ sót $65\text{–}85\%$ đám cháy nhỏ (đốt rơm rạ, cháy thực bì dưới tán rừng). Trên $5.769$ cặp ô lưới đồng thời Aqua–SNPP, VIIRS ghi nhận số điểm cháy gấp **$3,751\times$** và tổng $\text{FRP}$ gấp **$1,377\times$** MODIS. |
| **3. Thang đo độ tin cậy (`Confidence`) & Nhiễu SAA / Nguồn tĩnh** | Trường `confidence` là số nguyên liên tục từ **$0\%$ đến $100\%$** (dựa trên hàm thành viên ngữ cảnh của *Giglio et al., 2003*). Có trường `type` (`0..3`) trong bản chuẩn `MCD14ML`. | Trường `confidence` là biến phân loại 3 mức: **`low`** (lóa nắng hoặc $\Delta T_4 < 15\text{ K}$), **`nominal`** ($\Delta T_4 > 15\text{ K}$), và **`high`** (pixel bão hòa). Chịu nhiễu hạt proton ban đêm tại **Dị thường Nam Đại Tây Dương (SAA)**. | Không thể đặt ngưỡng lọc chung giữa số nguyên $0\text{–}100$ và nhãn chữ `l/n/h`. Tại Nam Mỹ, **$3,55\%\text{–}4,63\%$** điểm nóng VIIRS là xung nhiễu SAA ban đêm hoặc nguồn nhiệt công nghiệp tĩnh. |
| **4. Trùng lặp quỹ đạo đa vệ tinh (*Overpass Multiplicity*)** | Terra bay qua lúc `10:30 / 22:30 MLT`; Aqua bay qua lúc `13:30 / 01:30 MLT`. | Cả 3 vệ tinh Suomi-NPP (`13:30 MLT`), NOAA-20 (`~12:40 MLT`, lệch 50 phút) và NOAA-21 (`~13:05 MLT`, lệch 25 phút) cùng quét chồng lên một đám cháy trong vòng $\sim 55\text{ phút}$ đầu giờ chiều! | Số lượng vệ tinh tăng từ $1$ (năm 2000) lên $5$ (năm 2024–2026) tạo ra **bước nhảy giả tạo $+1.324\%$** tại Tiểu vùng Mekong (`3.580` $\to$ `50.988` điểm/5 ngày) và **$+714\%$** tại Amazon (`13.804` $\to$ `112.405` điểm/5 ngày)! |
| **5. Chế độ xử lý `URT/RT/NRT` vs. `Standard Science Quality`** | Bản NRT của Aqua có thể lệch vị trí vài km trong vòng 12 giờ sau khi tàu hiệu chỉnh quỹ đạo. | Bản NRT (`1.0NRT`/`2.0NRT`) gán cờ `DayNight` theo pha quỹ đạo lên/xuống (Ascending/Descending node) thay vì góc thiên đỉnh Mặt Trời $\text{SZA} < 85^\circ$ như bản Standard. | Gây lệch phân loại Ngày/Đêm ở vùng vĩ độ trung bình – cao và vùng hoàng hôn/bình minh khi ghép nối lịch sử (`SP`) với cảnh báo sớm (`NRT`). |

### 1.3. Phân Tích Lựa Chọn Phương Án Kỹ Thuật (Architectural Trade-Off Matrix)

| Bài Toán Cốt Lõi | Phương Án 1 (Cơ sở / Truyền thống) | Phương Án 2 (Trung gian / Thống kê thuần túy) | Phương Án 3 — **Giải Pháp Của Flare-Chronos (Vật Lý – Thống Kê Kết Hợp)** | Lý Do Chọn Phương Án 3 (Kèm Minh Chứng Định Lượng) |
| :--- | :--- | :--- | :--- | :--- |
| **1. Quy chiếu không gian & Chuẩn hóa Footprint** | **Gán tâm điểm vào lưới Kinh–Vĩ độ $0.05^\circ$ (CMG Point Binning)**: Gán $(lat, lon)$ vào ô vuông $0.05^\circ \times 0.05^\circ$. | **Gán tâm điểm vào lưới lục giác Uber H3 (Centroid H3 Assignment)**: Chỉ gán tâm điểm vào 1 ô H3 duy nhất. | **Khôi phục Elip Định hướng $\Delta S(\theta)\times\Delta T(\theta)$ + Phân bổ Trọng số 13 điểm lên Lưới Kép Uber H3 Res 7 ($5.16\text{ km}^2$) & Res 8 ($0.74\text{ km}^2$)** ([ADR-0001](file:///Users/xirothedev/workspace/flare-chronos/docs/adr/0001-dual-resolution-h3-fractional-allocation.md)). | Ô vuông kinh-vĩ độ bị co diện tích theo $\cos\phi$; gán tâm điểm bỏ qua việc 1 pixel MODIS rìa quét ($9.69\text{ km}^2$) phủ lên tới **13 ô H3 Res 8**. Phép cầu phương 13 điểm bảo toàn tuyệt đối tổng năng lượng ($\sum_h w_{p,h} = 1.0$). |
| **2. Hiệu chuẩn chéo Độ nhạy & $\text{FRP}$** | **Nhân hệ số hằng số toàn cầu (Global Constant Scaling)**: $\text{FRP}_{\text{harm}} = k \cdot \text{FRP}_{\text{MODIS}}$. | **Mạng Nơ-ron Hộp đen (Black-Box MLP Regressor)**: Huấn luyện MLP không ràng buộc vật lý. | **Toán tử 2 Giai đoạn (Two-Stage Operator)**: Bước 1 bù đuôi phân phối theo góc quét $\text{FRP}_{\text{lim}}(\theta, \text{SZA})$; Bước 2 khớp **Power-Law + Empirical Quantile Mapping (EQM)** trên cặp đồng thời Aqua–SNPP ([ADR-0002](file:///Users/xirothedev/workspace/flare-chronos/docs/adr/0002-two-stage-physics-guided-frp-harmonization.md)). | Tỷ số VIIRS/MODIS biến thiên mạnh theo góc quét $\theta$ (từ $1.3\times$ ở nadir lên $>6\times$ ở rìa quét). Toán tử 2 giai đoạn giảm $82,6\%$ khoảng cách KS ($D_{\text{KS}} = 0.0205$) và bảo toàn tính giải thích vật lý 100%. |
| **3. Khử trùng lặp đa vệ tinh & Chuẩn hóa dài hạn** | **Cộng gộp trực tiếp hoặc lấy Max theo ngày (Daily Grid Max)**: Bỏ qua cấu trúc giờ bay qua. | **Lọc khoảng cách cố định $1\text{ km}$**: Không xét diện tích elip theo góc quét và tần suất quét qua các thập kỷ. | **Gom cụm Không-Thời gian theo Bán kính Elip ($\tau = 95\text{ phút}$) thành `FireEpisode` + Chia Hệ số Nỗ lực Quan sát Hiệu dụng $\Omega(y, \phi)$** ([ADR-0003](file:///Users/xirothedev/workspace/flare-chronos/docs/adr/0003-spatio-temporal-episode-deduplication-and-effort-normalization.md)). | Gom chính xác đoàn tàu vệ tinh chiều (`NOAA-20` `12:40`, `NOAA-21` `13:05`, `S-NPP` `13:30`, `Aqua` `13:30 MLT`) thành 1 sự kiện cháy duy nhất với độ phức tạp $O(N)$ qua băm không gian. |
| **4. Thống nhất `Confidence` & `DayNight`** | **Giữ nguyên cờ `DayNight` gốc & cắt ngưỡng cứng `confidence >= 50`**. | **Quy đổi bậc thang cố định (Step Mapping): `low=30, nom=60, high=90`**. | **Tính lại góc thiên đỉnh Mặt Trời tuyệt đối $\text{SZA}(\phi, \lambda, t_{\text{UTC}}) < 85^\circ$ + Hàm Logistic Nhiệt $\Delta T_{45}$ + Bộ lọc Vật lý SAA & Nguồn nhiệt tĩnh**. | Khử hoàn toàn sai lệch cờ `DayNight` của luồng `1.0NRT/2.0NRT` và tự động lọc xung nhiễu proton ban đêm của S-NPP và NOAA-20 trong vùng SAA Nam Mỹ. |

---

## PHẦN 2: ĐẶC TẢ TOÁN HỌC & VẬT LÝ ĐỒNG BỘ HÓA LIÊN CẢM BIẾN (CROSS-SENSOR MATHEMATICAL & PHYSICAL SPECIFICATION)

### 2.1. Bảng Đối Chiếu & Ánh Xạ Thuộc Tính Liên Cảm Biến (Schema Mapping)

| Trường Chuẩn Hóa (`Flare-Chronos`) | Trường Gốc MODIS C6.1 (`MCD14ML` / `MCD14DL`) | Trường Gốc VIIRS 375m C2 (`VNP14IMG` / `VJ114` / `VJ214`) | Bản Chất Vật Lý & Quy Tắc Chuyển Đổi Chuẩn Hóa |
| :--- | :--- | :--- | :--- |
| `latitude`, `longitude` | `latitude`, `longitude` (WGS-84) | `latitude`, `longitude` (WGS-84) | Tâm hình học của điểm ảnh cảm biến tại mặt đất; dùng làm gốc dựng elip [`InstantaneousFootprint`](file:///Users/xirothedev/workspace/flare-chronos/packages/harmonization-core/src/flare_chronos_core/domain.py). |
| `bright_t4_k` ($T_4$, Kelvin) | `brightness` (Kênh 21/22, $\lambda \approx 3.96\,\mu\text{m}$, bão hòa $\sim 500\text{ K}$ ở Ch21) | `bright_ti4` (Kênh I-4, $\lambda = 3.55\text{–}3.93\,\mu\text{m}$, bão hòa ở $367\text{ K}$ ngày / $320\text{ K}$ đêm) | Nhiệt độ sáng hồng ngoại trung nhạy với bức xạ nhiệt đám cháy theo định luật Wien ($\lambda_{\max} \approx 2898 / T_{\text{fire}}$). |
| `bright_t5_k` ($T_5$, Kelvin) | `bright_t31` (Kênh 31, $\lambda \approx 11.0\,\mu\text{m}$) | `bright_ti5` (Kênh I-5, $\lambda = 10.5\text{–}12.4\,\mu\text{m}$, bão hòa $380\text{ K}$) | Nhiệt độ sáng hồng ngoại nhiệt sóng dài dùng làm nền đối chứng ($\Delta T_{45} = T_4 - T_5$) để lọc lóa nắng và nhiễu hạt SAA. |
| `scan_km`, `track_km` ($\Delta S, \Delta T$) | `scan` ($1.00 \to 4.83\text{ km}$), `track` ($1.00 \to 2.01\text{ km}$) | `scan` ($0.38 \to 0.80\text{ km}$), `track` ($0.36 \to 0.78\text{ km}$) | Kích thước thực tế của điểm ảnh theo phương ngang vệt bay (Across-Track) và dọc vệt bay (Along-Track). |
| `frp_mw` ($\text{FRP}$, $\text{MW}$) | `frp` (Tính từ bức xạ dư $4\,\mu\text{m}$ kênh 21/22 trên diện tích pixel $1\text{ km}$) | `frp` (Thuật toán lai: vị trí từ kênh I-4 $375\text{ m}$, bức xạ từ kênh M13 $750\text{ m}$ kép gain để tránh bão hòa I-4) | Công suất bức xạ lửa tức thời ($\text{MW}$). Được chuẩn hóa qua toán tử 2 giai đoạn [`apply_two_stage_frp_calibration`](file:///Users/xirothedev/workspace/flare-chronos/packages/harmonization-core/src/flare_chronos_core/radiometric_calibrator.py). |
| `detection_probability` ($P_{\text{fire}}$) | `confidence`: Số nguyên liên tục $0\text{–}100\%$ | `confidence`: Nhãn phân loại `l` (`low`), `n` (`nominal`), `h` (`high`) | Ánh xạ về xác suất thực nghiệm thống nhất $P_{\text{fire}} \in [0, 1]$ qua hàm [`compute_unified_detection_probability`](file:///Users/xirothedev/workspace/flare-chronos/packages/harmonization-core/src/flare_chronos_core/confidence_filter.py). |
| `harmonized_daynight` (`D` / `N`) | `daynight` (`D`/`N` theo $\text{SZA} < 85^\circ$ ở bản chuẩn) | `daynight` (Ở bản NRT `1.0NRT`/`2.0NRT` gán theo quỹ đạo lên/xuống thay vì $\text{SZA}$) | Tính lại góc thiên đỉnh Mặt Trời tuyệt đối $\text{SZA}(\phi, \lambda, t_{\text{UTC}})$ và áp đặt cứng $\text{Day} \iff \text{SZA} < 85.0^\circ$. |

### 2.2. Bài Toán 1: Phương Trình Hình Học Cầu Dải Quét & Phân Bổ Trọng Số Lưới Lục Giác Kép Uber H3

Trên vệ tinh **Terra** và **Aqua** ($h_{\text{MODIS}} = 705\text{ km}$, bán kính quỹ đạo $r = R_e + h_{\text{MODIS}} = 7083.137\text{ km}$, bước góc lấy mẫu $s = 0.0014184397\text{ rad}$), kích thước thực tế của điểm ảnh tại góc quét $\theta \in [0, 55^\circ]$ được xác định bởi hệ phương trình hình học cầu (*Ichoku & Kaufman, 2005; Giglio et al., 2016*):

$$\Delta S_{\text{MODIS}}(\theta) = R_e \cdot s \left( \frac{\cos\theta}{\sqrt{(R_e / r)^2 - \sin^2\theta}} - 1 \right)$$

$$\Delta T_{\text{MODIS}}(\theta) = r \cdot s \left( \cos\theta - \sqrt{(R_e / r)^2 - \sin^2\theta} \right)$$

Ngược lại, cảm biến **VIIRS** ($h_{\text{VIIRS}} \approx 829\text{ km}$, $r = 7207.137\text{ km}$, $\theta_{\max} = \pm 56.28^\circ$) áp dụng cơ chế gom cụm phần cứng 3 phân vùng (*Wolfe et al., 2013*): Zone 1 ($0^\circ \le |\theta| < 31.72^\circ$, gom $N_{\text{agg}} = 3$), Zone 2 ($31.72^\circ \le |\theta| < 44.86^\circ$, gom $N_{\text{agg}} = 2$), và Zone 3 ($44.86^\circ \le |\theta| \le 56.28^\circ$, giữ $N_{\text{agg}} = 1$).

| Thông Số Hình Học Cảm Biến | MODIS Collection 6.1 (`Terra` / `Aqua`) | VIIRS 375m Collection 2 (`S-NPP` / `NOAA-20` / `NOAA-21`) | Tỷ Số Tương Quan (MODIS / VIIRS) |
| :--- | :---: | :---: | :---: |
| **Kích thước tại Nadir ($\theta = 0^\circ$)** | $1.000 \times 1.000\text{ km}$ ($1.0000\text{ km}^2$) | $0.363 \times 0.360\text{ km}$ ($0.1305\text{ km}^2$) | **$7,66\times$** |
| **Kích thước tại Rìa dải quét ($\theta_{\max}$)** | $4.830 \times 2.006\text{ km}$ (**$9.6875\text{ km}^2$** tại $55^\circ$) | $0.778 \times 0.791\text{ km}$ (**$0.6154\text{ km}^2$** tại $56.28^\circ$) | **$15,74\times$** |
| **Tỷ số Rìa MODIS / Tâm VIIRS** | $9.6875\text{ km}^2$ | $0.1305\text{ km}^2$ | **$74,23\times$** |
| **Diện tích trung bình thực tế trên FIRMS** | **$2.155\text{ km}^2$** (Phân vị P95: **$5.270\text{ km}^2$**) | **$0.221\text{ km}^2$** (Phân vị P95: **$0.426\text{ km}^2$**) | **$9,75\times$** (Trung bình thực tế) |
| **Ngưỡng phát hiện $\text{FRP}_{\text{lim}}$ ban ngày** | $8.20\text{ MW}$ (Nadir) $\to$ **$41.20\text{ MW}$** (Rìa $55^\circ$) | $1.15\text{ MW}$ (Nadir) $\to$ **$3.40\text{ MW}$** (Rìa $56.3^\circ$) | **$12,12\times$** nhạy hơn ở rìa quét |

Thay vì gán toàn bộ năng lượng của một pixel MODIS $9.69\text{ km}^2$ vào một điểm tâm duy nhất, hàm [`allocate_footprint_to_h3`](file:///Users/xirothedev/workspace/flare-chronos/packages/harmonization-core/src/flare_chronos_core/geometry_h3.py) xoay hình elip $(\frac{\Delta S}{2}, \frac{\Delta T}{2})$ theo góc phương vị quỹ đạo $\sin\alpha_{\text{track}} = \frac{\cos i}{\cos\phi}$ và thực hiện phép cầu phương 13 điểm lên lưới lục giác đẳng diện tích **Uber H3 Resolution 7** ($\bar{A}_7 = 5.161\text{ km}^2$) và **Uber H3 Resolution 8** ($\bar{A}_8 = 0.737\text{ km}^2$), bảo toàn tuyệt đối năng lượng $\sum_{h \in \mathcal{H}} w_{p, h} \equiv 1.0000$.

![Figure 1 - Scan Angle Footprint Physics](file:///Users/xirothedev/workspace/flare-chronos/docs/figures/fig1_scan_angle_footprint_physics.png)

### 2.3. Bài Toán 2: Toán Tử Quan Sát Bức Xạ $4\,\mu\text{m}$ & Hiệu Chuẩn Chéo Hai Giai Đoạn Trên $N = 5.769$ Cặp Đồng Thời Aqua–SNPP

Công suất bức xạ lửa ($\text{FRP}$, đơn vị $\text{MW}$) tuân theo xấp xỉ bậc 4 của định luật Planck ở bước sóng $\lambda \approx 3.96\,\mu\text{m}$ (*Wooster et al., 2005*):

$$\text{FRP}_p = \frac{A_p \cdot \sigma_{\text{SB}}}{a \cdot \tau_4(\theta)} \left( L_4 - \bar{L}_{4,\text{bg}} \right)$$

Giới hạn phát hiện tối thiểu $\text{FRP}_{\text{lim}}(A_p, \text{SZA})$ tăng theo diện tích điểm ảnh $A_p(\theta)$:

$$\text{FRP}_{\text{lim, MODIS}}(A_p, \text{SZA}) = \left( 3.70 + 4.50 \cdot \max(0, \cos\text{SZA})^{0.75} \right) \cdot A_p^{1.04}$$

$$\text{FRP}_{\text{lim, VIIRS}}(A_p, \text{SZA}) = \left( 0.50 + 0.65 \cdot \max(0, \cos\text{SZA})^{0.75} \right) \cdot \left(\frac{A_p}{0.1406}\right)^{0.94}$$

Bằng cách ghép cặp các quan sát diễn ra trong cùng ngày và cùng chế độ Ngày/Đêm giữa vệ tinh **Aqua (MODIS)** và **Suomi-NPP (VIIRS)** (cùng bay qua lúc $\sim 13\text{:}30\text{ MLT}$ và $01\text{:}30\text{ MLT}$), mô hình hai giai đoạn thực hiện:
1. **Giai đoạn 1 — Bù khuyết đuôi phân phối theo góc quét**: $\widetilde{\text{FRP}}_{\text{MODIS}}(\theta) = \text{FRP}_{\text{MODIS}} \cdot \left[ 1 + \kappa \cdot \ln\left(\max(1, A_p(\theta))\right) \right]$.
2. **Giai đoạn 2 — Ánh xạ hỗn hợp Luật Lũy thừa & Phân vị Thực nghiệm (EQM)**:
   $$\widehat{\text{FRP}}_{\text{VIIRS-eq}} = \gamma \cdot \left( \alpha \cdot \widetilde{\text{FRP}}_{\text{MODIS}}^{\beta} \right) + (1 - \gamma) \cdot F_{\text{VIIRS}}^{-1}\!\left( F_{\widetilde{\text{MODIS}}}\!\left(\widetilde{\text{FRP}}_{\text{MODIS}}\right) \right)$$

| Chỉ Số Kiểm Định Thống Kê | Trước Đồng Bộ Hóa (Raw Aqua-MODIS vs. S-NPP VIIRS) | Sau Đồng Bộ Hóa (`Flare-Chronos` Two-Stage Operator) | Mức Cải Thiện Định Lượng |
| :--- | :---: | :---: | :--- |
| **Số cặp ô lưới đồng thời ($N_{\text{pairs}}$)** | $5.769\text{ ô lưới}$ | $5.769\text{ ô lưới}$ | Tập kiểm chứng thực tế NASA FIRMS |
| **Tỷ số số điểm nóng trung bình ($\bar{N}_{\text{VIIRS}} / \bar{N}_{\text{MODIS}}$)** | $3.751\times$ | $1.000\times$ (Đã chuẩn hóa tương đương) | Khử sạch độ lệch mật độ $+275,1\%$ |
| **Tỷ số tổng FRP trung bình ($\sum \text{FRP}_{\text{VIIRS}} / \sum \text{FRP}_{\text{MODIS}}$)** | $1.377\times$ | $1.004\times$ | Khử độ lệch thiếu hụt năng lượng $-27,4\%$ |
| **Hệ số xác định ($R^2$)** | $0.7349$ | **$0.7463$** | Tăng độ tương quan giải thích phương sai |
| **Sai số toàn phương trung bình ($\text{RMSE}$, $\text{MW/cell}$)** | $161.995\text{ MW}$ | **$158.479\text{ MW}$** | Giảm sai số bậc hai trên toàn dải |
| **Khoảng cách phân phối Kolmogorov-Smirnov ($D_{\text{KS}}$)** | $0.1180$ | **$0.0205$** | **Giảm $82,6\%$ sai lệch phân phối xác suất!** |

![Figure 3 - Cross-Sensor FRP Calibration](file:///Users/xirothedev/workspace/flare-chronos/docs/figures/fig3_cross_sensor_frp_quantile_mapping.png)

### 2.4. Bài Toán 3, 4, 5: Chuẩn Hóa Góc Thiên Đỉnh Mặt Trời ($\text{SZA} < 85^\circ$), Lọc Nhiễu SAA, Gom Cụm Sự Kiện Cháy & Hệ Số Nỗ Lực Quan Sát $\Omega(y, \phi)$

1. **Chuẩn hóa Ngày/Đêm tuyệt đối theo Góc thiên đỉnh Mặt Trời ($\text{SZA}$)**:
   $$\text{SZA}(\phi, \lambda, t_{\text{UTC}}) = \arccos\!\left( \sin\phi\sin\delta + \cos\phi\cos\delta\cos\omega \right), \quad \text{Harmonized DayNight} = \begin{cases} \text{'D'} & \text{nếu } \text{SZA} < 85.0^\circ \\ \text{'N'} & \text{nếu } \text{SZA} \ge 85.0^\circ \end{cases}$$
2. **Xác suất thực nghiệm thống nhất $P_{\text{fire}} \in [0, 1]$ & Bộ lọc Dị thường Nam Đại Tây Dương (SAA)**:
   $$P_{\text{fire}}(\text{MODIS}) = \frac{1}{1 + \exp\!\left[ -\left( \frac{C_{\text{MODIS}} - 38.0}{19.0} + 0.015 \cdot \text{clip}(\Delta T_{45} - 18.0, -10, 40) \right) \right]}$$
   Trong vùng SAA ($\phi \in [-55^\circ, +7^\circ], \lambda \in [-110^\circ, +11^\circ]$), các xung hạt proton ban đêm có $\Delta T_{45} = T_4 - T_5 < 16.5\text{ K}$ và $\text{FRP} < 2.2\text{ MW}$ được tự động gắn cờ `is_saa_anomaly = True` và loại bỏ.
3. **Gom cụm Không-Thời gian đa vệ tinh ($\tau_{\text{cluster}} = 95\text{ phút}$) & Chuẩn hóa Nỗ lực Quan sát $\Omega(y, \phi)$**:
   Hai phát hiện được gom vào cùng một `FireEpisode` $E_k$ khi $\Delta t \le 95\text{ phút}$ và khoảng cách Haversine nhỏ hơn tổng bán kính hiệu dụng:
   $$d_{\text{Haversine}}(x_i, x_j) \le \max\!\left( 1.35\text{ km}, \, \sqrt{\frac{A_{p_i}}{\pi}} + \sqrt{\frac{A_{p_j}}{\pi}} + 0.65\text{ km} \right) \quad \text{hoặc} \quad \text{H3}_8(x_i) = \text{H3}_8(x_j)$$
   Mỗi sự kiện được chia cho hệ số nỗ lực quan sát hiệu dụng $\Omega(y, \phi) = \Omega_0(y) \cdot \left[ 1 + 0.18 \left( \frac{1}{\max(0.55, \cos\phi)} - 1 \right) \right]$ (với $\Omega_0$ tăng từ $0.52$ năm 2000 lên $2.08$ giai đoạn 5 vệ tinh `2024–2026`).
4. **Bộ ba chỉ số Lịch Hoạt Động Cháy (`HFD`, `HRF`, `SFAI`) trên mỗi Pentad $p \in [1, 73]$**:
   $$\text{HFD}_{y,p} = \frac{100}{5 \cdot A_{\text{AOI}}} \sum_{E_k \in \mathcal{E}_{y,p}} \frac{P_{\text{episode}}(E_k) \cdot \psi_{\text{regime}}(y)}{\Omega(y, \phi_k)}, \quad \text{HRF}_{y,p} = \frac{1}{A_{\text{AOI}}} \sum_{E_k \in \mathcal{E}_{y,p}} \frac{\widehat{\text{FRP}}_{\text{VIIRS-eq}}(E_k)}{\Omega(y, \phi_k)}$$
   $$\text{SFAI}_{y,p} = \frac{\text{HRF}_{y,p} - \text{Median}_{y'\in[2001,2026]}\!\left(\text{HRF}_{y',p}\right)}{0.65 \cdot \left(1.4826 \cdot \text{MAD}_{y'}\!\left(\text{HRF}_{y',p}\right)\right) + 0.35 \cdot \text{Std}_{y'}\!\left(\text{HRF}_{y',p}\right)}$$

![Figure 2 - Overpass Deduplication and Effort Factor](file:///Users/xirothedev/workspace/flare-chronos/docs/figures/fig2_overpass_deduplication_sza.png)

---

## PHẦN 3: HAI NGHIÊN CỨU ĐIỂN HÌNH THỰC TIỄN TRÊN $775.531$ ĐIỂM NÓNG NASA FIRMS (EMPIRICAL CASE STUDIES)

### 3.1. Case Study 1: Tiểu Vùng Sông Mekong & Việt Nam (`BBOX: 100.0°E–109.5°E, 11.0°N–23.5°N`)

#### Bảng Số Liệu Thực Tế NASA FIRMS (Cửa Sổ 5 Ngày Cao Điểm Giữa Tháng 3: `15/03 – 19/03`)

| Năm (Epoch) | Tổ Hợp Cảm Biến Hoạt Động | Điểm Nóng Thô Theo Từng Nguồn (`Raw Counts`) | Tổng Điểm Nóng Thô (`Raw Sum`) | Sự Kiện Cháy Độc Lập (`Fire Episodes`) | Hệ Số Nén Trùng Lặp | Nỗ Lực Quan Sát $\Omega(y, \phi)$ | Sự Kiện Chuẩn Hóa `Flare-Chronos` (`VIIRS-eq`) | Chỉ Số Thô (`2005=100`) | Chỉ Số Chuẩn Hóa (`2005=100`) |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2005** | `MODIS_SP` (Terra+Aqua) | MODIS: `3.580` | **3.580** | 2.132 | $1.68\times$ | $1.0084$ | **7.717,0** | `100,0` | **`100,0`** |
| **2010** *(El Niño)* | `MODIS_SP` (Terra+Aqua) | MODIS: `8.222` | **8.222** | 4.440 | $1.85\times$ | $1.0084$ | **16.071,0** | `229,7` | **`208,3`** *(Đỉnh hạn)* |
| **2012** *(+S-NPP)* | `MODIS_SP` + `SNPP_SP` | MODIS: `7.297`<br/>SNPP: `25.720` | **33.017** | 16.952 | $1.95\times$ | $1.4925$ | **11.358,1** | `922,3` *(+822% ảo)* | **`147,2`** |
| **2016** *(Siêu El Niño)* | `MODIS_SP` + `SNPP_SP` | MODIS: `6.564`<br/>SNPP: `36.778` | **43.342** | 22.573 | $1.92\times$ | $1.4925$ | **15.124,3** | `1.210,7` | **`196,0`** *(Đỉnh hạn)* |
| **2020** | `MODIS_SP` + `SNPP_SP` | MODIS: `4.827`<br/>SNPP: `23.050` | **27.877** | 13.890 | $2.01\times$ | $1.7950$ | **7.738,2** | `778,7` | **`100,3`** |
| **2023** *(+NOAA-20)* | `MODIS_SP` + `SNPP_SP` + `NOAA20_SP` | MODIS: `4.086`<br/>SNPP: `19.824`<br/>NOAA20: `18.959` | **42.869** | 22.280 | $1.92\times$ | $1.9362$ | **9.279,9** | `1.197,5` | **`120,3`** |
| **2024** *(+NOAA-21)* | `MODIS_SP` + `SNPP_SP` + `NOAA20_SP` + `NOAA21_NRT` | MODIS: `3.446`<br/>SNPP: `16.020`<br/>NOAA20: `15.651`<br/>NOAA21: `15.871` | **50.988** | 22.557 | $2.26\times$ | $2.0975$ | **7.266,4** | **`1.424,2`** *(+1.324% ảo!)* | **`94,2`** *(Thực tế giảm 5,8%!)* |

> [!IMPORTANT]
> **Phát hiện chấn động từ dữ liệu thực tế tại Tiểu vùng sông Mekong & Việt Nam:**  
> Vào kỳ 5 ngày giữa tháng 3/2024, cảm biến chuẩn `MODIS_SP` ghi nhận `3.446` điểm cháy — **thấp hơn $3,7\%$** so với cùng kỳ năm 2005 (`3.580` điểm). Thế nhưng, do sự tham gia đồng thời của 3 vệ tinh VIIRS (`Suomi-NPP`, `NOAA-20`, `NOAA-21`), tổng số điểm nóng thô cộng gộp vọt lên tới **$50.988$ điểm (Chỉ số thô $= 1.424,2$, tức tăng giả tạo $+1.324,2\%$ so với năm 2005)!** Sau khi đi qua **Flare-Chronos**, chỉ số hoạt động cháy chuẩn hóa trả về đúng giá trị thực chất là **$94,2$** (giảm $5,8\%$ so với năm 2005), đồng thời giữ lại nguyên vẹn tín hiệu vật lý của hai đợt hạn hán lịch sử **El Niño 2010 (`208,3`)** và **El Niño 2016 (`196,0`)**.

### 3.2. Case Study 2: Vành Đai Cháy Rừng Nhiệt Đới Amazon, Brazil (`BBOX: 62.0°W–50.0°W, 14.0°S–4.0°S`)

#### Bảng Số Liệu Thực Tế NASA FIRMS (Cửa Sổ 5 Ngày Cao Điểm Cuối Tháng 8: `20/08 – 24/08`)

| Năm (Epoch) | Tổ Hợp Cảm Biến Hoạt Động | Điểm Nóng Thô Theo Từng Nguồn (`Raw Counts`) | Tổng Điểm Nóng Thô (`Raw Sum`) | Sự Kiện Cháy Độc Lập (`Fire Episodes`) | Hệ Số Nén Trùng Lặp | Xung Nhiễu SAA Đêm Đã Lọc | Sự Kiện Chuẩn Hóa `Flare-Chronos` (`VIIRS-eq`) | Chỉ Số Thô (`2005=100`) | Chỉ Số Chuẩn Hóa (`2005=100`) |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2005** *(Hạn lớn)* | `MODIS_SP` (Terra+Aqua) | MODIS: `13.804` | **13.804** | 6.303 | $2.19\times$ | 626 | **16.037,4** | `100,0` | **`100,0`** |
| **2010** *(Siêu hạn)* | `MODIS_SP` (Terra+Aqua) | MODIS: `16.304` | **16.304** | 6.654 | $2.45\times$ | 929 | **16.930,5** | `118,1` | **`105,6`** |
| **2012** *(+S-NPP)* | `MODIS_SP` + `SNPP_SP` | MODIS: `6.677`<br/>SNPP: `26.807` | **33.484** | 10.793 | $3.10\times$ | 4.145 | **7.276,3** | `242,6` *(Tăng ảo)* | **`45,4`** *(Giảm phá rừng thực tế)* |
| **2019** | `MODIS_SP` + `SNPP_SP` | MODIS: `4.770`<br/>SNPP: `16.882` | **21.652** | 7.331 | $2.95\times$ | 1.948 | **4.109,3** | `156,9` | **`25,6`** |
| **2020** | `MODIS_SP` + `SNPP_SP` | MODIS: `3.506`<br/>SNPP: `22.031` | **25.537** | 7.420 | $3.44\times$ | 4.905 | **4.159,2** | `185,0` | **`25,9`** |
| **2024** *(Hạn 2024 + 4 luồng)* | `MODIS_SP` + `SNPP_SP` + `NOAA20_SP` + `NOAA21_NRT` | MODIS: `8.151`<br/>SNPP: `35.647`<br/>NOAA20: `35.765`<br/>NOAA21: `32.842` | **112.405** | 22.579 | **$4.98\times$** | **18.097** | **11.343,1** | **`814,3`** *(+714% ảo!)* | **`70,7`** *(Đỉnh hạn thế kỷ 2020s)* |

![Figure 4 - Regime Shift Elimination](file:///Users/xirothedev/workspace/flare-chronos/docs/figures/fig4_regime_shift_elimination.png)

![Figure 5 - Harmonized Burning Activity Calendar](file:///Users/xirothedev/workspace/flare-chronos/docs/figures/fig5_harmonized_burning_calendar.png)

---

## PHẦN 4: KIẾN TRÚC HỆ THỐNG MONOREPO, ĐƯỜNG ỐNG DỮ LIỆU & CƠ SỞ DỮ LIỆU KHÔNG-THỜI GIAN (SYSTEM ARCHITECTURE & DATA PIPELINE)

### 4.1. Sơ Đồ Kiến Trúc Tổng Thể 5 Tầng (End-to-End Architecture)

```mermaid
flowchart TB
    subgraph NASA_SOURCES["1. Nguồn Dữ Liệu Vệ Tinh NASA Earthdata & LANCE FIRMS"]
        MODIS_SP["MODIS Collection 6.1 Standard (MCD14ML)<br/>Terra (2000–2026) & Aqua (2002–2026) | 1 km Nadir"]
        VIIRS_SP["VIIRS 375m Collection 2 Standard<br/>Suomi-NPP (2012–2026) & NOAA-20 (2018–2026)"]
        NRT_STREAMS["Near-Real-Time / URT Streams (LANCE)<br/>MODIS_NRT, VIIRS_SNPP_NRT, NOAA-20_NRT, NOAA-21_NRT (2024–2026+)"]
        OPEN_FEEDS["Direct Open Regional 7-Day Feeds<br/>SouthEast Asia & South America CSVs"]
    end

    subgraph INGESTION_SEAM["2. Tầng Thu Thập & Lưu Đệm (packages/firms-ingestion)"]
        API_ADAPTER["FIRMSClient Adapter<br/>Quản lý hạn mức 5.000 tx / 10 phút & Pacing 0.35s"]
        RAW_CACHE["Kho Lưu Trữ Dữ Liệu Thô (data/raw/*.csv & GeoParquet)<br/>775.531+ bản ghi thực tế đã xác thực"]
    end

    subgraph CORE_ENGINE["3. Lõi Đồng Bộ Hóa Vật Lý Liên Cảm Biến (packages/harmonization-core)"]
        STEP1["Bước 1: Chuẩn Hóa Thiên Văn & Chế Độ Xử Lý<br/>Tính chính xác góc SZA(lat, lon, UTC) -> Chuẩn hóa DayNight (SZA < 85°)"]
        STEP2["Bước 2: Ánh Xạ Xác Suất P(fire) & Khử Nhiễu Vật Lý<br/>Logistic/Thermal Mapping + Lọc vùng SAA (11°E–110°W, 7°N–55°S) + Nguồn tĩnh"]
        STEP3["Bước 3: Khôi Phục Hình Học Dải Quét & Phân Bổ Uber H3<br/>Giải ngược góc quét θ -> Elip ΔS×ΔT -> Phân bổ trọng số H3 Res 7 & Res 8"]
        STEP4["Bước 4: Hiệu Chuẩn Bức Xạ 2 Giai Đoạn (Two-Stage FRP Operator)<br/>Scan-Angle Observation Operator + Stratified Quantile Mapping (Aqua–SNPP)"]
        STEP5["Bước 5: Khử Trùng Lặp Quỹ Đạo & Chuẩn Hóa Nỗ Lực Quan Sát<br/>Spatio-Temporal Clustering (τ = 95 phút) -> Fire Episode / Ω(y, φ)"]
    end

    subgraph CALENDAR_STORAGE["4. Tầng Lưu Trữ Phân Tích & Lịch Hoạt Động Cháy"]
        DUCKDB["DuckDB / PostGIS Spatio-Temporal Store<br/>Bảng H3_Res7_Pentad_Cube & Episode_Catalog"]
        CAL_ENGINE["Burning Activity Calendar Engine<br/>Ma trận 26 Năm × 73 Pentads: HFD, HRF & Chỉ số dị thường SFAI Z-Score"]
    end

    subgraph PRESENTATION["5. Giao Diện Tương Tác & Cảnh Báo Sớm (WebGL + REST API)"]
        FASTAPI["FastAPI Harmonization Service<br/>/api/v1/harmonize-aoi & /api/v1/calendar"]
        DECKGL["MapLibre GL + Deck.gl Footprint Layer<br/>Hiển thị Elip ΔS×ΔT, Lưới H3 Res 7/8 & Lịch Nhiệt 26 Năm"]
    end

    MODIS_SP & VIIRS_SP & NRT_STREAMS & OPEN_FEEDS --> API_ADAPTER
    API_ADAPTER --> RAW_CACHE
    RAW_CACHE --> STEP1 --> STEP2 --> STEP3 --> STEP4 --> STEP5
    STEP5 --> DUCKDB --> CAL_ENGINE
    CAL_ENGINE --> FASTAPI --> DECKGL
```

### 4.2. Sơ Đồ Tuần Tự Luồng Xử Lý Dữ Liệu (Sequence Workflow)

```mermaid
sequenceDiagram
    autonumber
    actor User as Nhà Quản Lý Cháy / Nhà Khoa Học
    participant API as FastAPI / Benchmark CLI
    participant Ingest as FIRMSClient (firms-ingestion)
    participant Core as Harmonization Core (flare_chronos_core)
    participant DB as DuckDB / GeoParquet Cube

    User->>API: Chọn AOI (Bounding Box / Polygon) & Giai đoạn (2000–2026)
    API->>Ingest: Truy vấn dữ liệu MODIS (SP/NRT) & VIIRS (SNPP/NOAA20/NOAA21)
    alt Đã có trong bộ đệm cục bộ (Cache Hit)
        Ingest-->>API: Trả về DataFrame từ GeoParquet / CSV Cache
    else Chưa có trong bộ đệm (Cache Miss)
        Ingest->>Ingest: Chia nhỏ cửa sổ thời gian & Điều tiết nhịp gọi (Pacing 0.35s)
        Ingest-->>API: Tải từ NASA LANCE FIRMS API & Lưu cache bền vững
    end

    API->>Core: parse_firms_dataframe() -> List[ThermalDetection]
    Core->>Core: 1. harmonize_daynight_flag() qua góc thiên đỉnh Mặt Trời SZA < 85°
    Core->>Core: 2. compute_unified_detection_probability() & Lọc nhiễu SAA / Nguồn tĩnh
    Core->>Core: 3. reconstruct_instantaneous_footprint() & allocate_footprint_to_h3(Res 7, Res 8)
    Core->>Core: 4. apply_two_stage_frp_calibration() (Observation Operator + EQM)
    Core->>Core: 5. cluster_fire_episodes(τ=95 min) & Chia hệ số nỗ lực quan sát Ω(y, φ)
    Core->>Core: 6. build_burning_activity_calendar() -> Ma trận 26 Năm × 73 Pentads
    Core-->>DB: Lưu trữ FireEpisode & BurningCalendarCell
    DB-->>User: Hiển thị Lịch Hoạt Động Cháy (HFD, HRF, SFAI) & Xuất GeoJSON/CSV
```

### 4.3. Cấu Trúc Monorepo & Lược Đồ Cơ Sở Dữ Liệu Không-Thời Gian (DuckDB + Uber H3 Schema)

```sql
-- 1. Bảng Sự Kiện Cháy Độc Lập Sau Khử Trùng Lặp Đa Vệ Tinh (Deduplicated Fire Episodes)
CREATE TABLE fire_episodes (
    episode_id              VARCHAR PRIMARY KEY,
    start_utc               TIMESTAMPTZ NOT NULL,
    end_utc                 TIMESTAMPTZ NOT NULL,
    year                    SMALLINT NOT NULL,
    pentad                  TINYINT NOT NULL,          -- 1..73
    centroid_lat            DOUBLE NOT NULL,
    centroid_lon            DOUBLE NOT NULL,
    h3_res7_cell            VARCHAR(16) NOT NULL,
    h3_res8_cell            VARCHAR(16) NOT NULL,
    harmonized_daynight     CHAR(1) NOT NULL,
    contributing_platforms  VARCHAR NOT NULL,          -- e.g. 'Aqua,NOAA-20,NOAA-21,Suomi-NPP'
    raw_detection_count     INTEGER NOT NULL,
    combined_probability    DOUBLE NOT NULL,
    raw_sum_frp_mw          DOUBLE NOT NULL,
    harmonized_frp_mw       DOUBLE NOT NULL,
    effort_omega            DOUBLE NOT NULL,
    effort_norm_episodes    DOUBLE NOT NULL
);

-- 2. Khối Dữ Liệu Lịch Hoạt Động Cháy (H3 Resolution 7 x Year x Pentad Cube)
CREATE TABLE h3_burning_calendar_cube (
    h3_res7_cell            VARCHAR(16) NOT NULL,
    year                    SMALLINT NOT NULL,
    pentad                  TINYINT NOT NULL,          -- 1..73 (5-day step)
    raw_detection_count     INTEGER NOT NULL,
    episode_count           INTEGER NOT NULL,
    effective_effort_omega  DOUBLE NOT NULL,
    hfd_per_100km2_day      DOUBLE NOT NULL,           -- Harmonized Fire Density
    hrf_mw_per_km2          DOUBLE NOT NULL,           -- Harmonized Radiative Flux
    sfai_zscore             DOUBLE NOT NULL,           -- Standardized Fire Anomaly Index
    anomaly_tier            VARCHAR(48) NOT NULL,
    PRIMARY KEY (h3_res7_cell, year, pentad)
);
```

---

## PHẦN 5: THIẾT KẾ GIAO DIỆN NGƯỜI DÙNG & TRỰC QUAN HÓA LỊCH HOẠT ĐỘNG CHÁY (UI/UX & BURNING CALENDAR WIREFRAME)

```text
+----------------------------------------------------------------------------------------------------------------------+
| [🔥 FLARE-CHRONOS]  AOI: [ Tiểu vùng sông Mekong & Việt Nam v ]   Giai đoạn: [2000 - 2026]   Lưới: [H3 Res 7 (5km)] |
| Bộ lọc Vật lý: [x] Chuẩn hóa SZA < 85°  [x] Lọc nhiễu SAA Đêm  [x] Tách Nguồn Nhiệt Tĩnh  [x] Khử Trùng Lặp (95m)   |
+-------------------------------------------------------+--------------------------------------------------------------+
|                                                       |  [BẢNG ĐIỀU KHIỂN ĐỐI CHỨNG TRƯỚC / SAU ĐỒNG BỘ HÓA]         |
|   [KHUNG BẢN ĐỒ KHÔNG GIAN ĐA TẦNG - DECK.GL/MAPLIBRE]|  +----------------+----------------+----------------+        |
|                                                       |  | Raw Detections | Fire Episodes  | SFAI Z-Score   |        |
|      _.-""""-._      (Elip MODIS Rìa Quét: 4.8x2.0km) |  |  50,988 (Thô)  |  18,412 (Chuẩn)|  +2.84 sigma   |        |
|    .'          '.     o o (Cụm VIIRS 375m bên trong)  |  |  (+1,324% ảo)  |  (Khử trùng lặp|  [SEVERE RISK] |        |
|   /   o  o  o    \                                    |  +----------------+----------------+----------------+        |
|  |       o        |   / \ / \ / \ (Lưới Lục Giác     |                                                              |
|   \              /   | H3| H3| H3|  Đẳng Diện Tích)   |  [ĐỒNG HỒ MÙA VỤ CHÁY - POLAR PHENOLOGY CLOCK (365 NGÀY)]    |
|    '._        _.'     \ / \ / \ /                     |              Pentad 1 (01/01)                                |
|       `""""""`                                        |                 . - ~ ~ - .                                  |
|                                                       |             . '    _..._    ' .   * Cao điểm mùa cháy:       |
|   Chú giải Lớp Bản Đồ:                                |           /      .'     '.      \   Pentad 11 - 22           |
|   [x] Elip Footprint Thực (Scan x Track, góc alpha)   |          |      |  2016   |      |  (20/02 - 20/04)          |
|   [x] Lưới H3 Res 7/8 (Màu theo HRF MW/km^2)          |           \      '. ___ .'      / * Cảnh báo sớm ngoài mùa:  |
|   [x] Tâm Sự Kiện Cháy Độc Lập (Fire Episode)         |             .     ' - - '     .     Pentad 8 (Giữa tháng 2)  |
|   [x] Nguồn Nhiệt Tĩnh Đã Tách (Nhà máy/Khí đồng hành)|               ' - . _ _ . - '                                |
|                                                       |              Pentad 37 (02/07)                               |
+-------------------------------------------------------+--------------------------------------------------------------+
| [MA TRẬN LỊCH HOẠT ĐỘNG CHÁY THỐNG NHẤT 26 NĂM - HARMONIZED BURNING ACTIVITY CALENDAR (26 YEARS x 73 PENTADS)]       |
| Chỉ số hiển thị: (•) HFD (Sự kiện/100km2/ngày)   ( ) HRF (MW/km2)   ( ) SFAI Anomaly Z-Score   [x] Viền xanh Crisis  |
|                                                                                                                      |
| Năm   | Jan (P01-06) | Feb (P07-12) | Mar (P13-18) | Apr (P19-24) | May-Jul (P25-42) | Aug-Oct (P43-60) | Nov-Dec    |
| ------+--------------+--------------+--------------+--------------+------------------+------------------+----------- |
| 2001  | ░░░░░░░░░░░░ | ░░▒▒▓▓▓▓▒▒░░ | ▓▓████████▓▓ | ▒▒▓▓▒▒░░░░░░ | ░░░░░░░░░░░░░░░░ | ░░░░░░░░░░░░░░░░ | ░░░░░░░░░░ |
| 2005  | ░░░░░░░░░░░░ | ░░▒▒▓▓▓▓▓▓░░ | ▓▓████████▓▓ | ▒▒▓▓▒▒░░░░░░ | ░░░░░░░░░░░░░░░░ | ░░░░░░░░░░░░░░░░ | ░░░░░░░░░░ |
| 2010* | ░░░░░░░░░░░░ | ▒▒▓▓██████▓▓ | ████████████ | ▓▓████▒▒░░░░ | ░░░░░░░░░░░░░░░░ | ░░░░░░░░░░░░░░░░ | ░░░░░░░░░░ |
| 2012  | ░░░░░░░░░░░░ | ░░▒▒▓▓▓▓▒▒░░ | ▓▓████████▓▓ | ▒▒▓▓▒▒░░░░░░ | ░░░░░░░░░░░░░░░░ | ░░░░░░░░░░░░░░░░ | ░░░░░░░░░░ |
| 2016* | ░░░░░░▒▒▓▓░░ | ▓▓██████████ | ████████████ | ▓▓██████▒▒░░ | ░░▒▒░░░░░░░░░░░░ | ░░░░░░░░░░░░░░░░ | ░░░░░░░░░░ |
| 2020  | ░░░░░░░░░░░░ | ░░▒▒▓▓▓▓▒▒░░ | ▓▓████████▓▓ | ▒▒▓▓▒▒░░░░░░ | ░░░░░░░░░░░░░░░░ | ░░░░░░░░░░░░░░░░ | ░░░░░░░░░░ |
| 2024* | ░░░░░░░░░░░░ | ▒▒▓▓██████▓▓ | ████████████ | ▓▓████▒▒░░░░ | ░░░░░░░░░░░░░░░░ | ░░░░░░░░░░░░░░░░ | ░░░░░░░░░░ |
| 2026  | ░░░░░░░░░░░░ | ░░▒▒▓▓██████ | ▓▓████████▓▓ | ▒▒▓▓▒▒░░░░░░ | ░░░░░░░░░░░░░░░░ | ░░░░░░░░░░░░░░░░ | [NRT LIVE] |
+----------------------------------------------------------------------------------------------------------------------+
```

---

## PHẦN 6: CHIẾN LƯỢC CHẤM GIẢI TOÀN CẦU, KỊCH BẢN PITCH 7 SLIDES & LỘ TRÌNH 2027+ (PITCH DECK & ROADMAP)

### 6.1. Bảng Đối Chiếu 5 Tiêu Chí Chấm Giải Toàn Cầu Của NASA Space Apps

| Tiêu Chí NASA Space Apps | Trọng Tâm Đánh Giá Của Ban Giám Khảo | Điểm Ăn Tiền Độc Quyền Của **Flare-Chronos** |
| :--- | :--- | :--- |
| **1. Validity (Tính Xác Thực Khoa Học)** | Giải pháp có dựa trên định luật vật lý cảm biến và toán học vững chắc không? Có số liệu kiểm chứng thực tế không? | Kiểm chứng trực tiếp trên **$775.531$ điểm nóng thực tế từ NASA LANCE FIRMS**; giải phương trình cầu dải quét $\Delta S(\theta)\times\Delta T(\theta)$, toán tử quan sát bức xạ $4\,\mu\text{m}$ (*Wooster et al., 2005; Sofiev & Kouznetsov, 2026*) và hiệu chuẩn trên **$5.769$ cặp ô lưới đồng thời Aqua–SNPP**, giảm **$82,6\%$** sai số phân phối Kolmogorov-Smirnov ($D_{\text{KS}}$ từ $0.1180 \to 0.0205$). |
| **2. Relevance (Tính Bám Sát Đề Bài)** | Có giải quyết trọn vẹn bài toán bất đồng nhất giữa MODIS và VIIRS để dựng ra *Burning Activity Calendar* không? | Giải quyết toàn diện cả **5 rào cản liên cảm biến** (Footprint Bow-tie, Độ nhạy FRP, Thang Confidence & nhiễu SAA, Trùng lặp quỹ đạo 5 vệ tinh, Cờ NRT/Standard SZA) để xuất ra ma trận **26 Năm × 73 Pentads** cùng chỉ số dị thường **$\text{SFAI Z-Score}$**. |
| **3. Creativity (Tính Sáng Tạo Đột Phá)** | Phương pháp tiếp cận có mới mẻ, vượt qua cách gom ô lưới kinh-vĩ độ hay nhân hệ số tuyến tính đơn giản không? | Thay thế điểm tròn vô hướng bằng **Phép phân bổ trọng số diện tích elip định hướng lên lưới lục giác kép Uber H3 (Res 7 & Res 8)** kết hợp **Khử trùng lặp sự kiện cháy không-thời gian ($\tau = 95\text{ phút}$)** và chuẩn hóa theo **Nỗ lực quan sát hiệu dụng $\Omega(y, \phi)$**. |
| **4. Impact (Tác Động Thực Tiễn)** | Giải pháp giúp ích gì cho lực lượng cứu hỏa, quản lý rừng và nghiên cứu biến đổi khí hậu khi MODIS và Suomi-NPP ngừng hoạt động? | Ngăn chặn sai lầm chính sách do "bẫy nhảy bậc giả tạo $+1.324\%$" khi gộp thô đa cảm biến; tách bạch chính xác mùa đốt phụ phẩm nông nghiệp định kỳ với khủng hoảng cháy rừng El Niño ngoài mùa vụ tại **Việt Nam / Tiểu vùng Mekong** và **Rừng Amazon**. |
| **5. Presentation (Trình Bày & Trực Quan Hóa)** | Câu chuyện có súc tích, dễ hiểu và có sản phẩm thực thi rõ ràng không? | Bộ 5 biểu đồ khoa học chuẩn xuất bản kết xuất trực tiếp từ Python Engine cùng giao diện đồng bộ 4 khung nhìn (Elip Footprint + Lưới H3 + Ma trận 26×73 Pentad + Đồng hồ mùa vụ cực). |

### 6.2. Lộ Trình Mở Rộng Đa Cảm Biến Giai Đoạn 2027+ (Multi-Sensor Roadmap)
1. **Tích hợp Vệ tinh Địa tĩnh Thế hệ mới (Geostationary 10-Minute Fire Diurnal Cycle)**: Mở rộng Toán tử Quan sát Góc quét sang cảm biến **GOES-16/19 ABI**, **Himawari-9 AHI** (khu vực Việt Nam / Đông Nam Á) và **Meteosat Third Generation FCI** để tái tạo đường cong năng lượng cháy từng 10 phút trong ngày.
2. **Hiệu chuẩn Điểm nóng Siêu phân giải 30m từ Landsat 8/9/Next**: Sử dụng sản phẩm `LANDSAT_NRT` ($30\text{ m}$) đã có trên NASA FIRMS làm chuẩn đối chiếu thực địa cho các đám cháy rơm rạ cực nhỏ ($< 0.1\text{ MW}$).
3. **Kết hợp Vệ tinh Radar Khẩu độ Tổng hợp Băng tần Kép NISAR (`GCOV` & `GUNW` Fusion)**: Tích hợp dữ liệu Radar băng tần L ($24\text{ cm}$) và S ($10\text{ cm}$) từ vệ tinh **NISAR** để xuyên qua lớp khói mù dày đặc của đám cháy rừng, xác thực diện tích rừng bị suy thoái cấu trúc (`Coherence Loss` & `HV Backscatter Drop`) ngay sau khi **Flare-Chronos** phát hiện dị thường nhiệt.

---

## PHẦN 7: HƯỚNG DẪN CHẠY KIỂM CHỨNG TOÀN TRÌNH & TÀI LIỆU THAM KHẢO HỌC THUẬT (REPRODUCIBILITY & REFERENCES)

### 7.1. Lệnh Chạy Kiểm Chứng Trực Tiếp Trong Workspace

```bash
# 1. Chạy bộ kiểm thử đơn vị & bất biến vật lý (7/7 bài kiểm thử toán học)
python3 -m unittest discover -s tests -p "test_*.py" -v

# 2. Thu thập dữ liệu thực tế từ NASA LANCE FIRMS API (sử dụng FIRMS_MAP_KEY trong .env)
python3 apps/benchmark-cli/src/benchmark_cli/fetch_real_firms.py

# 3. Thực thi toàn bộ pipeline đồng bộ hóa trên 775.531 bản ghi thực tế & xuất 5 biểu đồ khoa học
python3 apps/benchmark-cli/src/benchmark_cli/run_experiments.py

# 4. Xuất toàn bộ tài liệu Proposal sang định dạng PDF chuẩn xuất bản A4
python3 exports/export_pdf.py
```

### 7.2. Tài Liệu Tham Khảo Học Thuật Chính Thức (Peer-Reviewed References)
1. **Giglio, L., Schroeder, W., & Justice, C. O. (2016).** *The collection 6 MODIS active fire detection algorithm and fire products.* Remote Sensing of Environment, 178, 31–41.
2. **Schroeder, W., Oliva, P., Giglio, L., & Csiszar, I. A. (2014).** *The New VIIRS 375 m active fire detection data product: Algorithm description and initial assessment.* Remote Sensing of Environment, 143, 85–96.
3. **Wooster, M. J., Roberts, G., Perry, G. L. W., & Kaufman, Y. J. (2005).** *Retrieval of biomass combustion rates and totals from fire radiative power (FRP) observations: FRP derivation and calibration relationships between MODIS and BIRD experimental satellite datasets.* Journal of Geophysical Research: Atmospheres, 110(D24).
4. **Ichoku, C., & Kaufman, Y. J. (2005).** *A method to derive smoke emission rates from MODIS fire radiative energy measurements.* IEEE Transactions on Geoscience and Remote Sensing, 43(11), 2636–2649.
5. **Wolfe, R. E., Lin, G., Nishihama, M., Tewari, K. P., Tilton, J. C., & Isaacman, A. R. (2013).** *Suomi NPP VIIRS prelaunch and on-orbit geometric calibration and characterization.* Journal of Geophysical Research: Atmospheres, 118(20), 11508–11521.
6. **Freeborn, P. H., Wooster, M. J., Roy, D. P., & Cochrane, M. A. (2014).** *Quantification of MODIS fire radiative power (FRP) measurement uncertainty for use in satellite-based active fire characterization and biomass burning estimation.* Geophysical Research Letters, 41(6), 1988–1994.
7. **Sofiev, M., & Kouznetsov, R. (2026).** *Analytical observation operators for satellite active fire detection limits and scan-angle FRP modulation across MODIS and VIIRS.* Copernicus / EGU Atmospheric Chemistry and Physics Discussions.
8. **NASA Earthdata LANCE FIRMS Documentation (2026).** *Active Fire Data Attributes and Processing Modes (URT/RT/NRT vs. Standard Science Quality) for MODIS C6.1 and VIIRS C2.* [https://www.earthdata.nasa.gov/data/tools/firms/faq](https://www.earthdata.nasa.gov/data/tools/firms/faq).
