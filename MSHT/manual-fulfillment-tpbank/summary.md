# Tóm tắt: Bật lại rút tiền, bỏ qua gọi TPBank (báo cáo senior dev)

> Bản rút gọn để trình bày nhanh — chi tiết đầy đủ xem [PRD.md](./PRD.md).
>
> **Đây là bản cập nhật lần 2**, thay thế thiết kế đầy đủ ban đầu (trạng thái `awaiting_manual`, job export định kỳ, tab web-admin). Không còn thay đổi ở repo `web-admin`.

## Vấn đề

TPBank lỗi xác thực (401) trên API chi hộ → team đã bật `WITHDRAW_DISABLED` để chặn khẩn cấp → **user rút tiền luôn bị reject cứng**, không có ETA sửa xong.

## Giải pháp

Thêm field mới `ManualFulfillment`: khi bật, request rút tiền vẫn được validate + trừ tiền ngay (giữ nguyên optimistic-deduct hiện có), nhưng **bỏ qua gọi TPBank**. Withdraw giữ nguyên trạng thái `pending` có sẵn (không có trạng thái mới). Đội vận hành tự tra danh sách `pending` qua Metabase, xử lý tay, rồi nộp kết quả (thành công/thất bại) qua 1 API nội bộ mới bằng file Excel 2 cột.

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
bỏ qua gọi TPBank   (luồng cũ: gọi TPBank như hiện tại)
status = pending (không đổi)
   │
   │  (vận hành tự tra qua Metabase, chuyển khoản tay)
   ▼
Vận hành nộp file .xlsx (request_id, result) qua API nội bộ mới
   │
   ▼
Xử lý ĐỒNG BỘ trong request (không chạy nền), trả báo cáo theo dòng ngay
   │
   ▼
Mỗi dòng: tìm theo request_id + status=pending
   │
   ├─ không tìm thấy / status khác / result không hợp lệ ──► bỏ qua, ghi lý do
   ├─ "success" ──► set success
   └─ "rejected" ──► set rejected + hoàn tiền (giống WithdrawErr hiện có)
```

## Thay đổi chính (backend `withdraw`, repo duy nhất bị ảnh hưởng)

| Thành phần | Thay đổi |
|---|---|
| Config | `Withdraw.ManualFulfillment` (bool, mới, tách biệt `WITHDRAW_DISABLED`) |
| Status | không đổi — tái sử dụng `pending` có sẵn |
| `NewWithdraw` | thêm 1 nhánh `if` trước bước gọi TPBank, bỏ qua `TPBankGenerateWithdrawToken`/`TPBankRequestTransfer` khi flag bật |
| API mới (basic auth riêng) | 1 endpoint `POST .../manual-fulfillment/result`, nhận `.xlsx` (`request_id`, `result`), xử lý đồng bộ, trả báo cáo theo dòng |
| Export/job/UI | **không có** — vận hành tự tra Metabase, không cần hệ thống sinh file |

## Repo cần đổi

| Repo | Cần đổi |
|---|---|
| `withdraw` | ✅ 1 flag config + 1 nhánh trong `NewWithdraw` + 1 API mới |
| `external` (submodule) | ❌ Không |
| `web-admin` | ❌ Không (khác với bản thiết kế đầu tiên) |

## Rủi ro đã biết, chấp nhận

- Job đồng bộ trạng thái tự động (`WithdrawSyncAllPendingStatus`) hiện đã bị comment-out hoàn toàn trên production, nên tái sử dụng `pending` không có rủi ro job này poll nhầm các bản ghi chưa từng gửi TPBank. Nếu job được bật lại sau này, cần thêm filter loại trừ khi đó.
- Hoàn tiền dùng đúng pattern `WithdrawErr` hiện có (update status trước, hoàn tiền sau, không transaction) — chấp nhận cùng mức rủi ro crash-giữa-2-bước đã tồn tại sẵn trong luồng tự động.

## Response cho client

Không đổi gì — `status` trả về vẫn luôn là `pending` cho tới khi được đóng qua API nộp kết quả, đúng như hành vi hiện tại.
