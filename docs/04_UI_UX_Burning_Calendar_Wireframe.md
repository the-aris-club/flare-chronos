# 04. Đặc Tả Giao Diện Người Dùng & Trực Quan Hóa Lịch Hoạt Động Cháy (UI/UX & Burning Activity Calendar Wireframe Specification)

**Dự án:** **Flare-Chronos** — *26-Year Cross-Sensor Harmonized Active Fire Intelligence & Phenology Calendar*  
**Cuộc thi:** 2026 NASA Space Apps Challenge — *Harmonization of MODIS and VIIRS Hot Spots*  
**Tài liệu liên kết:** [GLOSSARY.md](../GLOSSARY.md) | [02_Cross_Sensor_Harmonization_Spec.md](02_Cross_Sensor_Harmonization_Spec.md) | [03_System_Architecture_and_Data_Pipeline.md](03_System_Architecture_and_Data_Pipeline.md)

---

## 1. Mục Tiêu Trải Nghiệm Người Dùng (UX Objectives)

Các nhà quản lý cháy rừng, lực lượng ứng phó khẩn cấp và nhà nghiên cứu sinh thái thường đứng trước hai rào cản trực quan hóa lớn khi dùng các bản đồ điểm nóng truyền thống:
1. **Ảo giác điểm vô hướng (*Point-Buffer Illusion*)**: Các cổng bản đồ thông thường vẽ mọi điểm nóng bằng một chấm tròn kích thước cố định, che khuất thực tế vật lý rằng một điểm ảnh MODIS ở rìa dải quét ($\theta = 55^\circ$) có diện tích elip mặt đất lên tới **$9.69\text{ km}^2$** ($4.83 \times 2.01\text{ km}$), gấp **$\sim 70\text{ lần}$** diện tích một điểm ảnh VIIRS ở tâm dải quét ($0.138\text{ km}^2$).
2. **Ảo giác bùng phát cháy do tăng số lượng vệ tinh (*Constellation Step-Jump Illusion*)**: Khi xem biểu đồ chuỗi thời gian thô từ năm 2000 đến 2026, việc đưa thêm Suomi-NPP vào năm 2012, NOAA-20 vào năm 2018/2020 và NOAA-21 vào năm 2024 làm số lượng điểm cháy nhảy vọt gấp $4\text{–}14\text{ lần}$, khiến người dùng không thể phân biệt đâu là một mùa cháy cực đoan thật sự (như hạn hán El Niño 2016 hay 2024) và đâu là hiệu ứng tăng mật độ cảm biến.

Giao diện **Flare-Chronos Workbench** giải quyết triệt để hai ảo giác này thông qua bố cục **4 vùng tương tác đồng bộ (Synchronized Four-Pane Analytical Workspace)**.

---

## 2. Bố Cục Wireframe Tổng Thể (Full-Screen Workbench)

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
| Chỉ số hiển thị: (•) HFD (Sự kiện/100km2/ngày)   ( ) HRF (MW/km2)   ( ) SFAI Anomaly Z-Score   [x] Viền xanh Severe Anomaly  |
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
| [ĐỐI CHỨNG CHUỖI THỜI GIAN 2000-2026: RAW UNHARMONIZED SUM (Đường Đỏ Đất - Nhảy bậc ảo) vs. FLARE-CHRONOS (Xanh Lá)] |
|   Index ^                                                                             .--- Raw Unharmonized (+1324%) |
|   1200  |                                                                   .--------'                               |
|    400  |                                         .------------------------'                                         |
|    100  |================*================*=======*========*========*========*========*=== Flare-Chronos Physical    |
|         +--------+-------+--------+-------+-------+--------+--------+--------+--------+---> Năm                      |
|        2000    2005    2010     2012    2016    2020     2022     2024     2025     2026                             |
+----------------------------------------------------------------------------------------------------------------------+
```

---

## 3. Đặc Tả Chi Tiết 4 Thành Phần Giao Diện Tương Tác

### 3.1. Bản Đồ Không Gian WebGL Đa Độ Phân Giải (`Footprint & Iso-Area Hex Map`)
* **Lớp Đa giác Elip Dải quét Thực tế (`Instantaneous Footprint Layer`)**:
  - Thay vì vẽ điểm tròn vô hướng, mỗi `ThermalDetection` được kết xuất thành một hình elip định hướng với trục lớn $\Delta S(\theta)$, trục nhỏ $\Delta T(\theta)$ và xoay theo góc phương vị quỹ đạo $\alpha_{\text{track}}(\phi, i)$.
  - Người dùng quan sát trực tiếp hiện tượng một elip MODIS ở rìa dải quét ($\Delta S = 4.83\text{ km}, \Delta T = 2.01\text{ km}$) bao trùm lên $6\text{–}12$ điểm nóng VIIRS `375 m` bên trong cùng một đám cháy rừng tại cùng thời điểm bay qua `13:30 MLT`.
* **Lớp Lưới Lục Giác Đẳng Diện Tích Uber H3 (`Dual-Resolution H3 Layer`)**:
  - Ở mức thu phóng vùng (Zoom `5–9`), hiển thị lưới **Uber H3 Resolution 7** ($\bar{A}_7 = 5.161\text{ km}^2$).
  - Khi phóng to vào hiện trường đám cháy (Zoom `10–15`), tự động chuyển mượt sang **Uber H3 Resolution 8** ($\bar{A}_8 = 0.737\text{ km}^2$) với tỷ trọng năng lượng bức xạ $w_{p,h}$ được phân bổ chính xác từ các elip giao cắt.
* **Lớp Nguồn Nhiệt Tĩnh & Nhiễu Đã Tách (`Filtered Noise & Static Source Overlay`)**:
  - Các nguồn nhiệt công nghiệp (nhà máy xi măng, thép, trạm đốt khí đồng hành dầu khí, núi lửa) và các điểm nhiễu bức xạ hạt ban đêm trong vùng **Dị thường Nam Đại Tây Dương (SAA)** được hiển thị bằng biểu tượng riêng biệt (màu tím/xám) và tự động loại khỏi phép tính lịch cháy sinh khối.

### 3.2. Ma Trận Lịch Hoạt Động Cháy 26 Năm (`Harmonized Burning Activity Calendar Matrix`)
* **Cấu trúc Trục**:
  - **Trục Tung (Rows)**: $26\text{ năm}$ liên tục từ `2001` đến `2026` (kèm dòng trung bình khí hậu 25 năm ở trên cùng).
  - **Trục Hoành (Columns)**: $73\text{ Pentads}$ (mỗi Pentad đúng $5\text{ ngày}$ chuẩn khí hậu học, từ Pentad 1: `01/01–05/01` đến Pentad 73: `27/12–31/12`), loại bỏ hoàn toàn sai lệch độ dài tháng (28 vs. 31 ngày).
* **3 Chế độ Chỉ số Chuyển đổi Tức thời**:
  1. **$\text{HFD}$ (*Harmonized Fire Density*)**: Số sự kiện cháy chuẩn hóa trên mỗi $100\text{ km}^2$/ngày.
  2. **$\text{HRF}$ (*Harmonized Radiative Flux*)**: Mật độ công suất bức xạ lửa chuẩn hóa ($\text{MW}/\text{km}^2$).
  3. **$\text{SFAI}$ (*Standardized Fire Anomaly Index*)**: Chỉ số Z-score phi tham số đo độ lệch của Pentad hiện tại so với đường cơ sở 25 năm của chính Pentad đó:
     $$\text{SFAI}_{y,p} = \frac{\text{HRF}_{y,p} - \text{Median}_y(\text{HRF}_{\cdot, p})}{\sigma_{\text{robust}}(\text{HRF}_{\cdot, p})}$$
* **Nhận diện Tự động "Giai đoạn Cao điểm" & "Dị thường Ngoài mùa vụ"**:
  - Các ô có $\text{SFAI}_{y,p} \ge +2.2\sigma$ được đóng khung viền xanh lơ phát sáng (*Severe Anomaly Outline*), giúp chỉ huy cứu hỏa nhận ra ngay các đợt cháy rừng bùng phát sớm hơn quy luật mùa vụ (như đầu tháng 2 năm 2016 tại Tây Nguyên và Tiểu vùng Mekong). Ngưỡng này là **ngưỡng hiển thị** (khớp với chú thích của Hình 5), thấp hơn ngưỡng **báo động khủng hoảng** là $\text{SFAI} \ge +2.5\sigma$ (xem `docs/01` §6.1) — tức lịch cháy làm nổi bật dị thường nghiêm trọng *trước khi* báo động được kích hoạt.

### 3.3. Đồng Hồ Mùa Vụ Cháy Cực (`Polar Phenology Clock`)
* Biểu diễn chu kỳ $365\text{ ngày}$ ($73\text{ Pentads}$) trên hệ tọa độ cực $\psi_p = \frac{2\pi(p - 0.5)}{73}$:
  - Dải băng màu xám nhạt thể hiện khoảng tứ phân vị khí hậu 25 năm ($\text{IQR}: P_{25}\text{–}P_{75}$).
  - Đường nét đứt màu vàng cam thể hiện năm El Niño lịch sử (`2010` hoặc `2016`).
  - Đường liền nét màu xanh ngọc thể hiện diễn biến năm hiện tại (`2026`), cho phép so sánh trực quan độ lệch pha mùa cháy (*Phenological Phase Shift* — mùa cháy đến sớm hay kết thúc muộn bao nhiêu Pentad).

### 3.4. Thanh Đối Chứng Khử Bước Nhảy Giả Tạo (`Before/After Harmonization Comparator`)
* Hiển thị song song trên cùng một khung biểu đồ:
  - **Đường Đỏ Cam (Raw Unharmonized Sum)**: Tổng điểm nóng thô khi cộng gộp MODIS + S-NPP + NOAA-20 + NOAA-21 (bị nhảy bậc giả tạo năm 2012, 2020, 2024).
  - **Đường Xanh Ngọc (Flare-Chronos Harmonized Series)**: Đường xu thế vật lý sau khi qua bộ hiệu chuẩn hình học H3, toán tử quan sát góc quét, khử trùng lặp quỹ đạo 95 phút và chuẩn hóa nỗ lực quan sát $\Omega(y, \phi)$.

---

## 4. Minh Chứng Trực Quan Kết Xuất Thực Tế Từ Engine Python

Hình ảnh dưới đây được kết xuất trực tiếp từ `apps/benchmark-cli/src/benchmark_cli/run_experiments.py` trên dữ liệu thực tế NASA FIRMS cho **Tiểu vùng sông Mekong & Việt Nam** và **Rừng Amazon**:

![Harmonized Burning Activity Calendar](figures/fig5_harmonized_burning_calendar.png)
