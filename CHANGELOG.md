# flare-chronos

## 1.1.0

### Minor Changes

- 3c2925f: 02/11/2026 — docs/01_NASA_SpaceApps_Proposal.md — cập nhật: thêm Phụ lục A, bảng 25 Measured Epoch mỗi vùng; năm 2026 là Interpolated Year
  02/11/2026 — docs/02_Cross_Sensor_Harmonization_Spec.md — cập nhật: hiệu chuẩn trên 20.552 cặp Aqua–SNPP; khoảng tin cậy 95% của mức giảm RMSE trên mẫu giữ lại bao trùm số 0
  02/11/2026 — docs/05_Pitch_Deck_and_Video_Script.md — cập nhật: số cặp, D_KS và mức giảm 69,8% theo bộ dữ liệu mới
  02/11/2026 — exports/PROPOSAL.md — cập nhật: cùng các số liệu hiệu chuẩn mới
  02/11/2026 — exports/REPORT.md — cập nhật: cùng các số liệu hiệu chuẩn mới
  02/11/2026 — README.md — cập nhật: vùng truy vấn FIRMS Mê Kông mở rộng xuống 8,5°N để gồm Đồng bằng sông Cửu Long

### Patch Changes

- ffb3efc: 03/11/2026 — apps/workbench — cập nhật: resolve all lint errors/warnings without config ignores
- 3a4a39c: 03/11/2026 — exports/PROPOSAL.md — cập nhật: FIRMS query box and headline numbers
  03/11/2026 — exports/REPORT.md — cập nhật: FIRMS query box and headline numbers
- 6f00425: 01/11/2026 — exports/MODEL_FLOW.md — cập nhật: Workbench đọc luồng sự kiện thay cho trang demo HTML
  01/11/2026 — exports/PROPOSAL.md — cập nhật: mô tả Workbench là ứng dụng đọc luồng sự kiện, dịch vụ không kèm trang HTML
  01/11/2026 — exports/REPORT.md — cập nhật: bỏ mục demo/index.html khỏi cây thư mục
- 96af572: 03/11/2026 — apps/workbench/tsconfig.json — cập nhật: include test files in type check and add bun types

## 1.0.0

### Major Changes

- 67025be: 23/10/2026 — exports/MODEL_FLOW.md — cập nhật: chốt mô hình luồng hai thế hệ cho bản phát hành v1.0.0
- 67025be: 23/10/2026 — exports/PROPOSAL.md — cập nhật: chốt pipeline đồng bộ hoá cho bản phát hành v1.0.0
- 67025be: 23/10/2026 — exports/REPORT.md — cập nhật: chốt kiến trúc và số liệu kiểm chứng cho bản phát hành v1.0.0

Nhật ký thay đổi của các tài liệu được nộp bên ngoài repo.

Định dạng mục: `[<hash>: ]dd/mm/yyyy — <tệp> — <hành động>: <mô tả>`; tiền tố `<hash>: ` là commit thay đổi tài liệu (không bắt buộc).
Hành động: `thêm` | `sửa` | `xoá` | `thay thế` | `cập nhật`.
