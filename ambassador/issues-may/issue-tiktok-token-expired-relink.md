# Issue: Token TikTok hết hạn nhưng không liên kết lại được

**Ngày phát hiện:** 2026-05-17
**Trạng thái:** Đã fix — chờ merge
**Project:** Ambassador (accesstrade-projects/ambassabor)
**Mức độ:** Nghiêm trọng (user kẹt, không thể re-link token)
**PR:** [#2 — fix/tiktok-token-expired-flag](https://github.com/AT-Core/ambassador/pull/2)

---

## 1. Tóm tắt

Khi token TikTok của user hết hạn, hệ thống báo lỗi *"Tài khoản mạng xã hội của bạn đã hết hạn. Vui lòng liên kết lại!"* — nhưng ở trang Liên kết tài khoản, tài khoản TikTok **không có badge "Hết hạn"** và **không có nút "Liên kết lại"**, chỉ có nút "+ Thêm tài khoản". Bấm "Thêm tài khoản" thì backend trả lỗi *"Bạn đã liên kết tài khoản tiktok này trước đó"* (mã `1018`). User bị kẹt, không có cách nào cập nhật token.

---

## 2. Hiện tượng

- Token TikTok hết hạn → khi Gửi bài đăng / submit content, user thấy toast *"Tài khoản mạng xã hội của bạn đã hết hạn. Vui lòng liên kết lại!"*.
- Vào trang Liên kết tài khoản: TikTok hiển thị trạng thái bình thường (`Hoạt động`), không có nút "Liên kết lại".
- Chỉ có nút "+ Thêm tài khoản" — bấm vào → lỗi `1018` *"Bạn đã liên kết tài khoản tiktok này trước đó. Để thêm tài khoản tiktok khác, vui lòng truy cập website tiktok.com, thực hiện đăng xuất và thử lại!"*.
- → Không có đường nào để re-link token đã chết.

---

## 3. Nguyên nhân gốc

### Cơ chế hiển thị nút "Liên kết lại"

Frontend (`account/management/index.tsx`) chỉ render nút "Liên kết lại" khi `item.isTokenExpired === true`:

```jsx
{item.isTokenExpired && (
  <TiktokSection ... isReconnect={true} />
)}
```

### Vấn đề: cờ `isTokenExpired` gần như không bao giờ được bật

`isTokenExpired = true` chỉ được set ở 2 chỗ:

| Chỗ set cờ | Khi nào chạy |
|---|---|
| `InactiveUserTiktok` | Endpoint set **thủ công**, phải có người gọi |
| Job `schedule.go` | Job nền crawl content, callback `401` **và** refresh token đã chạm limit |

Nhưng 2 luồng **thực tế** phát hiện token chết lại **KHÔNG** set cờ — chỉ raise lỗi `ContentKeyUserSocialExpired`:

1. **`content.go`** (luồng submit content) — khi crawl content trả `StatusCode == 401` → chỉ `return error`.
2. **`RenewAccessToken`** (`user_social.go`) — khi refresh token TikTok hết hạn → set `status = "expired"` nhưng **quên `isTokenExpired = true`**.

→ Khi user gặp toast "hết hạn, liên kết lại" trong luồng thường gặp nhất, cờ `isTokenExpired` không bao giờ được bật → FE không hiển thị nút "Liên kết lại" → user kẹt.

---

## 4. Cách fix

Set `isTokenExpired = true` **ngay tại nguồn** — thời điểm backend phát hiện token thực sự chết:

- **`RenewAccessToken`** (`backend/internal/service/user_social.go`): khi refresh token TikTok hết hạn, thêm `isTokenExpired: true` vào `$set` (cùng `status: "expired"`).
- **`content.go`** (`backend/pkg/public/service/content.go`): khi crawl content trả `StatusCode == 401`, set `isTokenExpired = true` + `status = "expired"` cho user-social trước khi raise lỗi.

### Vì sao không dùng job quét định kỳ

Hệ thống đã phát hiện token chết **chính xác** ngay khi token được dùng và fail — đó là tín hiệu thật, không phải đoán. Set cờ tại nguồn cho kết quả tức thì (FE thấy nút "Liên kết lại" ngay lần load tiếp theo), không tốn tải, không độ trễ. Job quét định kỳ chỉ là chữa triệu chứng, có độ trễ, tốn rate limit TikTok.

### File thay đổi

- `backend/internal/service/user_social.go` — `RenewAccessToken`: set `isTokenExpired` khi refresh fail.
- `backend/pkg/public/service/content.go` — submit content: set `isTokenExpired` khi crawl trả `401`.

---

## 5. Lưu ý

Token đã chết **trước** khi deploy fix này sẽ không tự có cờ (record hiện có `status="expired"` nhưng `isTokenExpired=false`). Nếu cần xử lý các record cũ, chạy một migration một lần để backfill — không thuộc phạm vi PR này.

---

## 6. Liên quan

Issue này thuộc cùng flow re-link TikTok với [issue-link-social-403.md](issue-link-social-403.md) (vụ văng đăng nhập khi liên kết). Hai issue được tách thành 2 PR riêng.
