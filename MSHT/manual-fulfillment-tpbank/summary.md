# Tóm tắt: Rút tiền thủ công TPBank (báo cáo senior dev)

> Bản rút gọn để trình bày nhanh — chi tiết đầy đủ xem `docs/spec/0002-luong-rut-tien-thu-cong-tpbank.md`.

## Vấn đề

TPBank lỗi xác thực (401) trên API chi hộ + tra cứu trạng thái → team đã bật `WITHDRAW_DISABLED` để chặn khẩn cấp → **user rút tiền luôn bị reject cứng**, không có ETA sửa xong.

## Giải pháp

Tắt `WITHDRAW_DISABLED`, thêm field mới `ManualFulfillment`: khi bật, request rút tiền vẫn được validate + trừ tiền ngay (giữ nguyên optimistic-deduct hiện có), nhưng **bỏ qua gọi TPBank**, đánh dấu trạng thái mới `awaiting_manual`. Một job cron generate file Excel định kỳ để nhân viên nội bộ (MSHT Operator) tải, chuyển cho Kế toán AT xử lý tay (chuyển khoản ngoài hệ thống), rồi nộp kết quả ngược lại qua web-admin.

## Luồng tổng quan

```
User bấm "Rút tiền"
        │
        ▼
  NewWithdraw (validate + trừ tiền ngay — không đổi)
        │
        ▼
  ManualFulfillment = true ?
        │
   ┌────┴────┐
  Có         Không
   │           │
   ▼           ▼
awaiting_manual   (luồng cũ: gọi TPBank như hiện tại)
   │
   │  (job cron định kỳ)
   ▼
Generate file .xlsx (status=awaiting_manual, chưa exportedAt)
   │
   ▼
Upload MinIO (bucket DataExport, package `external/service/upload` có sẵn)
   │
   ▼
Đánh dấu Withdraw: exportedAt, manualExportId
   │
   ▼
MSHT Operator vào web-admin → tab "Rút tiền thủ công"
   │
   ├─► Tải file export ──► gửi Kế toán AT qua email/Slack (ngoài hệ thống)
   │                              │
   │                              ▼
   │                     Kế toán AT chuyển khoản tay
   │                     điền cột "Kết quả" (dropdown: Thành công/Thất bại)
   │                     gửi lại file qua email/Slack
   │                              │
   ◄──────────────────────────────┘
   │
   ▼
MSHT Operator upload file kết quả (xác nhận TOTP)
   │
   ▼
API trả 200 ngay (Status export → "processing"), xử lý NỀN
(pattern goroutine giống WithdrawBatchTransfer đã có)
   │
   ▼
Backend đọc từng dòng theo request_id + status=awaiting_manual
   │
   ├─ "Thành công" ──► set success
   └─ "Thất bại"   ──► set rejected + hoàn tiền (giống WithdrawErr hiện có)
   │
   ▼
Đếm lại: còn awaiting_manual thuộc export này? ──► Status export: error/completed
```

## Thay đổi chính (backend `withdraw`)

| Thành phần | Thay đổi |
| --- | --- |
| Config | `Withdraw.ManualFulfillment` (bool, mới, tách biệt `WITHDRAW_DISABLED`) |
| Status | `awaiting_manual` (mới, tách biệt `pending` — job sync tự động không quét nhầm) |
| `WithdrawBSON` | + `ManualExportID` (dùng `IsZero()` làm cờ, không cần thêm `ExportedAt` riêng) |
| Collection mới | `manualFulfillmentExports` (metadata file, `Status` 4 giá trị: pending/processing/error/completed, `ResultRuns[]`) |
| Job mới | cron generate file export định kỳ (`app/schedule/schedule.go`, lib có sẵn) |
| API mới (basic auth riêng) | `GET .../exports`, `GET .../exports/:id/download`, `GET .../exports/:id/result-download`, `POST .../exports/:exportId/result` |
| Storage | dùng `external/service/upload` có sẵn trong submodule (MinIO, bucket `DataExport` có sẵn) — chỉ cần cấu hình, không sửa submodule |

## Thay đổi chính (`web-admin`)

Tab mới "Rút tiền thủ công" trong Partner Detail (gated `partnerId === 'tpbank'`), dựng từ 2 pattern có sẵn:

- Bảng phân trang + Drawer lịch sử (`export-requests/`)
- `RcModalConfirmTotp` cho hành động ảnh hưởng tiền thật (`reconciliation/`)

Mỗi dòng export có 3 action: **Tải file export**, **Upload kết quả** (ẩn khi `Status=completed`, đổi label khi `processing`), **Lịch sử nộp** (Drawer). API nộp kết quả trả về ngay lập tức, không đợi xử lý xong — kết quả xem lại qua badge `Status` hoặc Drawer.

## Repo cần đổi

| Repo | Remote gốc để branch | Cần đổi |
| --- | --- | --- |
| `withdraw` | `tp/release` | ✅ Toàn bộ backend |
| `external` (submodule) | — | ❌ Không (chỉ cấu hình, dùng package có sẵn) |
| `web-admin` | `origin/release` | ✅ Tab mới |

## Rủi ro đã biết, chấp nhận

- Crash giữa 2 bước (update status / hoàn tiền) của cùng 1 dòng: rủi ro đã tồn tại sẵn ở `WithdrawErr` (luồng TPBank tự động hiện tại), không thêm transaction — giữ nguyên mức rủi ro hệ thống đang chấp nhận.

## Response cho client

`w.Status = awaiting_manual` chỉ tồn tại trong DB/logic nội bộ. Khi trả về client (mobile app, lịch sử giao dịch), hệ thống **map thành `pending`** ở tầng response — không đổi gì phía client, không cần phối hợp FE.
