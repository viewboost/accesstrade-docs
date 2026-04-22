# Tích hợp Scalef — Liên kết Tài khoản — Overview

> **Project:** Gen-Green × Scalef Integration — Phase 1
> **Ngày:** 2026-04-12
> **Trạng thái:** Đang thiết kế
> **PRD:** [prd-scalef-integration-v1-2026-04-12.md](prd-scalef-integration-v1-2026-04-12.md)
> **Demo:** `demo-gen-green` → `/lien-ket-scalef`

---

## 1. Bối cảnh

Gen-Green (150K creators) và Scalef (~1K publishers) là 2 nền tảng riêng biệt trong hệ sinh thái Vin, cùng do AccessTrade vận hành:
- **Gen-Green**: Nền tảng sáng tạo nội dung — creator đăng video, nhận thu nhập từ lượt xem
- **Scalef**: Nền tảng affiliate — publisher chia sẻ link, nhận hoa hồng khi có đơn hàng

Tích hợp = creator Gen-Green có thêm nguồn thu nhập thứ 2 (hoa hồng affiliate) mà không cần rời nền tảng. Đồng thời giải quyết bài toán thuế TNCN (AccessTrade chi trả cho cả 2 bên, cần nhận diện "cùng 1 người").

**Chiến lược:** "Đánh từ trong đánh ra" — kích hoạt đội CBNV (cán bộ nhân viên) trước, mở rộng creator bên ngoài sau.

**Target:** 1K user generate doanh thu affiliate, 50 tỷ/năm.

---

## 2. Scope Phase 1: Liên kết Tài khoản

Phase 1 chỉ tập trung vào **liên kết tài khoản** — chưa có dashboard affiliate, tạo link, hay tham gia chiến dịch.

### Luồng tổng quan

```
Creator bấm "Liên kết Scalef" trên Gen-Green
  → Đồng ý chia sẻ thông tin (consent)
  → Đăng nhập SSO Scalef
  → Hệ thống so khớp CCCD / SĐT / Email
  → Nếu khớp → Liên kết thành công
  → Nếu lệch → User chọn thông tin giữ lại + OTP xác thực
  → Update cả 2 bên → Liên kết thành công
```

### Nguyên tắc cốt lõi

| Nguyên tắc | Mô tả |
|------------|-------|
| **User chọn, không bên nào là gốc** | Khi thông tin xung đột, user quyết định giữ bên nào |
| **Bên nào chưa có thì theo bên đã có** | Auto-fill, không cần user chọn |
| **CCCD là khóa identity** | Matching CCCD trước để xác nhận "cùng 1 người". CCCD khác → reject |
| **1-đối-1 bắt buộc** | 1 Gen-Green user ↔ 1 Scalef user, không liên kết chéo |
| **OTP bắt buộc khi update** | Chọn SĐT/email từ bên kia → phải verify OTP/magic link |
| **Bidirectional update** | Update thông tin ở cả 2 bên theo lựa chọn của user |
| **Data không qua browser** | CCCD, SĐT, email chỉ truyền backend-to-backend |

---

## 3. Luồng chi tiết — 5 bước

### Bước 1: Đăng nhập Scalef (OAuth SSO)

- User bấm "Liên kết Scalef" trên Gen-Green
- Redirect sang SSO Scalef → user đăng nhập
- Scalef redirect về Gen-Green kèm authorization code
- Backend Gen-Green đổi code → gọi `/userinfo` → nhận: Scalef User ID, CCCD, SĐT, Email, Tên

### Bước 2: Đồng ý chia sẻ thông tin (Consent)

- Hiển thị danh sách thông tin sẽ chia sẻ: Họ tên, CCCD, SĐT, Email
- User bấm "Đồng ý" hoặc "Từ chối"
- Ghi nhận consent timestamp

### Bước 3: So khớp & Xác nhận

Hệ thống so sánh từng field:

| Field | Gen-Green | Scalef | Kết quả |
|-------|-----------|--------|---------|
| CCCD | 012345678901 | 012345678901 | **Khớp** ✓ |
| SĐT | +84912345678 | +84987654321 | **Lệch** → user chọn |
| Email | hung@gmail.com | hung.pub@gmail.com | **Lệch** → user chọn |

**Logic matching:**

```
Check 1-đối-1: GG user đã link SF khác? SF user đã link GG khác?
  → Vi phạm → REJECT

Match CCCD:
  → Cả 2 có, giống → PASS (cùng người)
  → Cả 2 có, khác → REJECT (khác người)
  → 1 bên thiếu → bỏ qua, dùng SĐT/Email fallback

So field SĐT, Email:
  → Khớp → bỏ qua
  → 1 bên trống → auto-fill từ bên có
  → Cả 2 có, khác → user chọn (bước 4)
```

Hiển thị bảng so sánh Gen-Green vs Scalef với badge Khớp/Lệch/Bổ sung. CCCD masked (chỉ 4 số cuối).

### Bước 4: Lựa chọn & Bổ sung thông tin

Với mỗi field lệch, UI hiển thị 2 card cho user chọn:

```
Số điện thoại
  ⚪ +84912345678  (Gen-Green)
  ⚪ +84987654321  (Scalef)
```

Sau khi chọn, nếu cần update bên kia → **OTP xác thực**:
- Chọn SĐT Scalef → update Gen-Green → OTP gửi về SĐT mới
- Chọn Email Scalef → update Gen-Green → magic link/OTP về email mới

**Check unique trước commit:** SĐT/Email mới không được thuộc user khác ở cả 2 hệ thống.

### Bước 5: Liên kết thành công

- Lưu `scalef_user_id`, `scalef_linked_at`, `scalef_link_method` vào Gen-Green user
- Ghi log liên kết vào `scalef_link_history`
- Hiển thị profile hợp nhất + danh sách chiến dịch affiliate sẵn sàng

---

## 4. Xử lý Reject

Mọi trường hợp reject hiển thị cùng 1 màn hình:

| Điều kiện | User thấy |
|-----------|-----------|
| GG user đã liên kết SF khác | "Tài khoản Gen-Green đã liên kết với tài khoản Scalef khác." |
| SF user đã liên kết GG khác | "Tài khoản Scalef này đã liên kết với tài khoản Gen-Green khác." |
| CCCD 2 bên khác nhau | "Thông tin CCCD không khớp giữa 2 tài khoản." |
| SĐT/Email đã thuộc user khác | "SĐT/Email này đã được sử dụng bởi tài khoản khác." |

Nút **"Gửi yêu cầu hỗ trợ"** → hệ thống tự tạo ticket (Gen-Green User ID, Scalef User ID, lý do, timestamp). User không cần nhập gì. Hẹn phản hồi 3 ngày.

---

## 5. Phân loại field theo risk level

| Field | Risk | Update policy |
|-------|------|---------------|
| SĐT | Low | User chọn + OTP verify |
| Email | Low | User chọn + magic link / OTP verify |
| CCCD | High | Khác → REJECT. Không cho user tự update |
| Tên pháp lý | High | Route admin review nếu conflict |

---

## 6. Chuẩn hóa dữ liệu trước khi so sánh

| Field | Chuẩn hóa | Ví dụ |
|-------|----------|-------|
| CCCD | Bỏ khoảng trắng, chỉ giữ số | "012 345 678 901" → "012345678901" |
| SĐT | Đưa về +84, bỏ khoảng trắng | "0912 345 678" → "+84912345678" |
| Email | Lowercase, bỏ khoảng trắng | "User@Gmail.COM " → "user@gmail.com" |

---

## 7. Data Model

### User model — thêm fields

| Field | Type | Mô tả |
|-------|------|-------|
| `scalef_user_id` | string, nullable | ID tài khoản Scalef đã liên kết |
| `scalef_linked_at` | datetime, nullable | Thời điểm liên kết |
| `scalef_link_method` | enum, nullable | `oauth` / `batch` / `admin` |

### Bảng pending_scalef_link (resumable state)

| Field | Type | Mô tả |
|-------|------|-------|
| `user_id` | string | Gen-Green user ID |
| `scalef_user_id` | string | Scalef user ID |
| `scalef_snapshot` | object | Tên, CCCD, SĐT, Email từ Scalef |
| `step` | enum | `compared` / `awaiting_otp` / `awaiting_email_verify` / `committed` |
| `created_at` | datetime | TTL 15 phút |

### Bảng scalef_link_history

| Field | Type | Mô tả |
|-------|------|-------|
| `gen_green_user_id` | string | |
| `scalef_user_id` | string | |
| `action` | enum | `linked` / `unlinked` / `rejected` / `profile_updated` |
| `method` | enum | `oauth` / `batch` / `admin` |
| `reject_reason` | string, nullable | |
| `changes` | object, nullable | `{field, old_value, new_value, source}` |
| `performed_by` | string | User ID hoặc Admin ID |
| `timestamp` | datetime | |

---

## 8. Giao diện chung 2 chiều

UI conflict resolution dùng chung cho cả 2 chiều:
- **Gen-Green → Scalef**: Creator Gen-Green bấm "Liên kết Scalef" (đa số user)
- **Scalef → Gen-Green**: Publisher Scalef bấm "Liên kết Gen-Green" (1K legacy user)

Sau OAuth, cả 2 luồng đổ về cùng 1 màn so khớp + lựa chọn + OTP.

---

## 9. Legacy Migration (1K publisher Scalef)

Scalef sắp chặn đăng ký mới → 1K user Scalef-only cần path vào Gen-Green:

| Tình huống | Xử lý |
|-----------|-------|
| Scalef user có cùng CCCD/SĐT với Gen-Green user | Liên kết qua flow chung (tự phục vụ hoặc admin batch) |
| Scalef user chưa có trên Gen-Green | Cần tạo Gen-Green account (admin batch hoặc user tự đăng ký) |
| Thông tin mâu thuẫn | Admin review |

**Batch migration (optional):** Admin upload danh sách Scalef user → tạo Gen-Green account → gửi email set password → auto-link.

---

## 10. Quy tắc nghiệp vụ

| Quy tắc | Chi tiết |
|---------|---------|
| 1-đối-1 | 1 Gen-Green user ↔ 1 Scalef user |
| User chọn khi xung đột | Không bên nào tự động override |
| Auto-fill khi 1 bên trống | Bên chưa có → lấy từ bên đã có |
| CCCD khác → reject | Không phải cùng người, không cho merge |
| OTP bắt buộc khi update | Dù data đến từ Scalef, vẫn phải verify |
| Không tự gỡ liên kết | Chỉ admin gỡ được |
| Ghi log mọi thứ | Liên kết, reject, gỡ, update profile |

---

## 11. Phụ thuộc

### Cần từ Scalef

| API | Mô tả | Status |
|-----|-------|--------|
| SSO OAuth2 | Redirect login + authorization code | Cần confirm |
| `GET /userinfo` | Trả Scalef User ID, CCCD, SĐT, Email, Tên | Cần confirm |
| `PUT /users/:id/profile` | Update SĐT/Email (bidirectional) | Cần confirm |
| Sandbox/staging | Test end-to-end | Cần confirm |

### Cần từ Gen-Green backend

| Service | Mô tả |
|---------|-------|
| OTP service | Gửi + verify OTP qua SĐT |
| Email verification | Magic link / OTP qua email |
| Unique check | Query SĐT/Email trên user collection |

---

## 12. Edge Cases

| Case | Xử lý |
|------|-------|
| CCCD đổi (CMND 9 số → CCCD 12 số) | Có thể cùng 1 người mà CCCD khác → admin override |
| CCCD "000000000000" (test data) | Validation: CCCD phải > 0 và đúng 12 số |
| Tên khác nhau (Unicode vs ASCII) | Tên không dùng để matching, chỉ CCCD/SĐT/Email |
| SĐT đổi format (+84 vs 0xxx) | Chuẩn hóa trước khi compare |
| Scalef API timeout giữa flow | Graceful fallback, pending state resumable, retry |
| 2 user cùng thao tác link cùng lúc | Race condition → check unique + lock |
| User refresh browser giữa chừng | Pending state TTL 15 phút, resumable |

---

## 13. Lộ trình tổng thể (3 Phase)

| Phase | Tên | Thời gian | Nội dung | Trạng thái |
|-------|-----|-----------|----------|-----------|
| **1** | **Liên kết tài khoản** | 2.5 tuần | Luồng liên kết, matching, conflict resolution, OTP | **← Đang thiết kế** |
| 2 | Affiliate trong Gen-Green | 2 tuần | Dashboard affiliate, tạo link, tham gia chiến dịch | Chờ Phase 1 |
| 3 | Hợp nhất tài khoản | 6 tuần | Vin Creator Portal, 1 cửa đăng nhập, thanh toán hợp nhất | Chờ Phase 2 |

Mỗi phase go-live riêng, dừng được bất kỳ lúc nào.
