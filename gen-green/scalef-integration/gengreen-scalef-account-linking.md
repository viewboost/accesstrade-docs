# Liên kết Tài khoản Scalef — Phía Gen-Green

> **Dành cho:** Team Gen-Green
> **Ngày:** 2026-04-01
> **Liên quan:** [Tích hợp Scalef Affiliate](./gengreen-scalef-affiliate-integration-proposal.md)

---

## 1. Tổng quan

Creator trên Gen-Green cần liên kết tài khoản Scalef (1 lần) để tham gia chiến dịch affiliate.

Luồng cốt lõi:

```
Creator bấm nút trên Gen-Green
  → Sang SSO Scalef (đăng nhập hoặc đăng ký)
  → Return về Gen-Green
  → Hệ thống kiểm tra thông tin
  → Liên kết thành công hoặc báo lỗi
```

---

## 2. Điểm chạm trên Gen-Green

Những nơi creator thấy nút dẫn sang SSO Scalef:

| Nơi | Loại | Mô tả |
|-----|------|-------|
| Trang đăng nhập | Nút SSO | "Đăng nhập bằng Scalef" cạnh Google, Apple |
| Trang đăng ký | Nút SSO | "Đăng ký bằng Scalef" |
| Settings → Tài khoản liên kết | Gợi ý | Hiện trạng thái "Chưa liên kết" + nút [Liên kết] |
| Tab Affiliate trong dashboard | Gợi ý | Onboarding card giới thiệu affiliate |
| Chi tiết Campaign có affiliate | Gợi ý | Banner "Liên kết Scalef để tham gia" |
| Bấm "Tham gia chiến dịch" | Chặn | Popup "Cần liên kết tài khoản Scalef trước" |
| Bấm "Tạo link affiliate" | Chặn | Popup tương tự |

Tất cả đều dẫn tới cùng 1 đích: **redirect sang SSO Scalef**.

### Mockup

**Trang đăng nhập:**

```
┌──────────────────────────────────────┐
│        Đăng nhập Gen-Green           │
│                                      │
│  [ SĐT / Email          ]           │
│  [ Mật khẩu              ]           │
│  [ Đăng nhập ]                       │
│                                      │
│  ─────────── hoặc ──────────         │
│                                      │
│  [ Đăng nhập bằng Scalef ]          │
│  [ Đăng nhập bằng Google ]          │
│                                      │
│  Chưa có tài khoản? Đăng ký         │
└──────────────────────────────────────┘
```

**Popup chặn khi bấm "Tham gia chiến dịch":**

```
┌──────────────────────────────────────┐
│                                      │
│   Cần liên kết tài khoản Scalef     │
│                                      │
│   Để tham gia chiến dịch affiliate,  │
│   bạn cần liên kết tài khoản        │
│   Scalef trước.                      │
│                                      │
│   [ Liên kết ngay ]    [ Để sau ]   │
│                                      │
└──────────────────────────────────────┘
```

**Settings — Tài khoản liên kết:**

```
Chưa liên kết:   Scalef    Chưa liên kết      [Liên kết]
Đã liên kết:     Scalef    publisher@email.com  01/04/2026
```

Không có nút gỡ — chỉ admin mới gỡ được.

---

## 3. Luồng liên kết (user đã đăng nhập Gen-Green)

Áp dụng khi creator đã đăng nhập Gen-Green, bấm nút liên kết từ Settings / Campaign / Affiliate tab / popup chặn.

```
Creator bấm "Liên kết Scalef"
         │
         ▼
Gen-Green user đã liên kết Scalef user khác rồi?
  CÓ → REJECT ngay (không cần sang Scalef)
  CHƯA ↓
         │
         ▼
══════ SANG SCALEF ══════════════════════════════════════════
Redirect sang SSO Scalef.

Bên Scalef:
• Đã có tài khoản → đăng nhập bình thường
• Chưa có tài khoản → Scalef hiện màn xác nhận:
  "Đăng ký bằng tài khoản Gen-Green?"
  (hiển thị tên, SĐT, email từ Gen-Green)
  → User bấm xác nhận → Scalef tự tạo tài khoản
  (không cần điền form — xem mục 5 Bảo mật)

Scalef xử lý xong → redirect về Gen-Green kèm
authorization code.
═════════════════════════════════════════════════════════════
         │
         ▼
Gen-Green backend đổi code → gọi Scalef API /userinfo
→ nhận: Scalef User ID, CCCD, SĐT, Email, Tên
(backend-to-backend, không qua browser)
         │
         ▼
╔═════════════════════════════════════════════════════════╗
║  CHECK 1: Scalef user đã liên kết Gen-Green user khác? ║
║                                                        ║
║  CÓ → REJECT                                          ║
╚═════════════════════════════════════════════════════════╝
         │ Pass
         ▼
╔═════════════════════════════════════════════════════════╗
║  CHECK 2: Thông tin 2 bên có mâu thuẫn không?         ║
║                                                        ║
║  So sánh từng trường giữa Scalef và Gen-Green user:   ║
║                                                        ║
║  • CCCD:  cả 2 bên đều có mà khác nhau? → REJECT      ║
║  • SĐT:  cả 2 bên đều có mà khác nhau? → REJECT      ║
║  • Email: cả 2 bên đều có mà khác nhau? → REJECT      ║
║                                                        ║
║  Nếu 1 bên không có → bỏ qua trường đó, cho qua.     ║
╚═════════════════════════════════════════════════════════╝
         │ Pass
         ▼
╔═════════════════════════════════════════════════════════╗
║  CHECK 3: Thông tin Scalef đã thuộc Gen-Green          ║
║           user khác chưa?                              ║
║                                                        ║
║  Với mỗi thông tin Scalef trả về, tìm trong           ║
║  toàn bộ Gen-Green user (trừ user hiện tại):           ║
║                                                        ║
║  • CCCD đã thuộc Gen-Green user khác?  → REJECT        ║
║  • SĐT đã thuộc Gen-Green user khác?  → REJECT        ║
║  • Email đã thuộc Gen-Green user khác? → REJECT        ║
║                                                        ║
║  Chỉ check trường mà Scalef CÓ trả về.                ║
╚═════════════════════════════════════════════════════════╝
         │ Pass
         ▼
    ✓ LIÊN KẾT THÀNH CÔNG
```

### Ví dụ minh họa

**Ví dụ 1 — Happy path:**

| | Scalef | Gen-Green user hiện tại |
|--|--------|------------------------|
| CCCD | 012345678901 | 012345678901 |
| SĐT | +84912345678 | +84912345678 |
| Email | a@gmail.com | a@gmail.com |

Check 1: chưa ai liên kết ✓ → Check 2: tất cả khớp ✓ → Check 3: không trùng ai khác ✓ → **Thành công**

**Ví dụ 2 — Gen-Green thiếu thông tin:**

| | Scalef | Gen-Green user hiện tại |
|--|--------|------------------------|
| CCCD | 012345678901 | 012345678901 |
| SĐT | +84912345678 | *(trống)* |
| Email | a@gmail.com | *(trống)* |

Check 2: CCCD khớp ✓, SĐT bỏ qua (Gen-Green trống) ✓, Email bỏ qua ✓
Check 3: SĐT +84912345678 đã thuộc Gen-Green user khác? Email a@gmail.com đã thuộc Gen-Green user khác?
- Không trùng ai → **Thành công**
- SĐT đã thuộc user khác → **REJECT**

**Ví dụ 3 — Thông tin mâu thuẫn:**

| | Scalef | Gen-Green user hiện tại |
|--|--------|------------------------|
| CCCD | 012345678901 | 999999999999 |

Check 2: CCCD cả 2 bên đều có nhưng khác nhau → **REJECT**

---

## 4. Luồng "Đăng nhập bằng Scalef" (user chưa đăng nhập)

Áp dụng khi user bấm "Đăng nhập bằng Scalef" hoặc "Đăng ký bằng Scalef" trên trang login/register. User chưa đăng nhập Gen-Green → cần tìm hoặc tạo Gen-Green user.

```
Bấm "Đăng nhập bằng Scalef"
         │
         ▼
Sang SSO Scalef → đăng nhập hoặc đăng ký
         │
         ▼
Return về Gen-Green, backend lấy thông tin từ Scalef:
Scalef User ID, CCCD, SĐT, Email, Tên
         │
         ▼
╔═════════════════════════════════════════════════════════╗
║  BƯỚC 1: Scalef user đã liên kết Gen-Green user chưa? ║
║                                                        ║
║  CÓ → Đăng nhập vào Gen-Green user đó. Xong.          ║
║  CHƯA → tiếp Bước 2                                   ║
╚═════════════════════════════════════════════════════════╝
         │
         ▼
╔═════════════════════════════════════════════════════════╗
║  BƯỚC 2: Thông tin Scalef đã thuộc Gen-Green user      ║
║          nào chưa? (CCCD, SĐT, Email)                 ║
║                                                        ║
║  CÓ → REJECT                                          ║
║  "Đã tồn tại tài khoản Gen-Green với thông tin này.   ║
║   Vui lòng đăng nhập Gen-Green rồi liên kết Scalef    ║
║   trong phần Cài đặt."                                 ║
║                                                        ║
║  KHÔNG → tiếp Bước 3                                   ║
╚═════════════════════════════════════════════════════════╝
         │
         ▼
╔═════════════════════════════════════════════════════════╗
║  BƯỚC 3: Tạo tài khoản Gen-Green mới                  ║
║                                                        ║
║  Điền sẵn từ Scalef: tên, SĐT, email, CCCD            ║
║  Thiếu thông tin thì tạo luôn, bổ sung sau.            ║
║                                                        ║
║  Tạo xong → liên kết Scalef luôn → đăng nhập          ║
╚═════════════════════════════════════════════════════════╝
```

### Ví dụ

**Ví dụ 1 — Đã liên kết trước đó (Bước 1):**

Publisher Minh đã liên kết Scalef với Gen-Green tuần trước. Hôm nay mở gen-green.global, bấm "Đăng nhập bằng Scalef".

→ Bước 1: Scalef user của Minh đã liên kết Gen-Green user → đăng nhập luôn. Xong.

**Ví dụ 2 — Đã có tài khoản Gen-Green nhưng chưa liên kết (Bước 2 → reject):**

Publisher Lan có tài khoản Scalef (SĐT 0912345678). Lan cũng đã đăng ký Gen-Green trước đó bằng cùng SĐT 0912345678, nhưng chưa liên kết Scalef.

Lan vào gen-green.global, bấm "Đăng nhập bằng Scalef".

→ Bước 1: Scalef user chưa liên kết ai → tiếp
→ Bước 2: SĐT 0912345678 đã thuộc Gen-Green user (chính Lan) → **REJECT**
→ Hiển thị: "Đã tồn tại tài khoản Gen-Green với SĐT này. Vui lòng đăng nhập gen-green.global rồi liên kết Scalef trong phần Cài đặt."

Lan đăng nhập Gen-Green bằng SĐT → vào Settings → bấm "Liên kết Scalef" → chạy luồng mục 3 → thành công.

**Ví dụ 3 — Chưa có tài khoản Gen-Green (Bước 3):**

Publisher Hùng có tài khoản Scalef (SĐT 0987654321, email hung@gmail.com). Hùng chưa từng dùng Gen-Green.

Hùng vào gen-green.global, bấm "Đăng ký bằng Scalef".

→ Bước 1: Scalef user chưa liên kết ai → tiếp
→ Bước 2: SĐT 0987654321 chưa thuộc ai, email hung@gmail.com chưa thuộc ai → tiếp
→ Bước 3: Tạo Gen-Green user mới (tên: Hùng, SĐT: 0987654321, email: hung@gmail.com) + liên kết Scalef luôn → đăng nhập.

---

## 5. Bảo mật

Thông tin nhạy cảm (CCCD, SĐT, email) **không bao giờ đi qua browser**. Chỉ truyền backend-to-backend.

### Chiều đi: Gen-Green → Scalef (tạo tài khoản nhanh)

Khi user chưa có tài khoản Scalef, Scalef cần thông tin Gen-Green để tạo tài khoản. Thông tin truyền qua prefill token (backend-to-backend), không qua URL.

```
Gen-Green backend tạo prefill token (1 lần, hết hạn 5 phút)
         │
         ▼
Redirect browser kèm token:
scalef.vn/oauth/authorize?client_id=gengreen&prefill_token=xxx
(token là chuỗi random, KHÔNG chứa thông tin user)
         │
         ▼
Scalef backend gọi API Gen-Green để đổi token → thông tin:
GET gengreen.vn/api/prefill/{token} → {tên, SĐT, email, CCCD}
Token bị xóa ngay sau khi dùng
         │
         ▼
Scalef hiện màn xác nhận: "Đăng ký bằng tài khoản Gen-Green?"
(hiển thị tên, SĐT, email — KHÔNG hiện CCCD)
User bấm xác nhận → Scalef tự tạo tài khoản
```

### Chiều về: Scalef → Gen-Green (trả kết quả)

```
Scalef redirect browser kèm authorization code:
gengreen.vn/callback?code=abc123
(code là chuỗi random, KHÔNG chứa thông tin user)
         │
         ▼
Gen-Green backend đổi code → access token (backend-to-backend)
         │
         ▼
Gen-Green backend gọi Scalef API /userinfo
→ nhận: Scalef User ID, CCCD, SĐT, Email, Tên
```

---

## 6. Khi bị reject

Mọi trường hợp reject đều hiển thị cùng 1 màn hình:

```
┌──────────────────────────────────────────────┐
│                                              │
│   Không thể liên kết tài khoản               │
│                                              │
│   Lý do: {xem bảng bên dưới}                │
│                                              │
│   Nếu đây là nhầm lẫn, chúng tôi sẽ        │
│   phản hồi qua email trong 3 ngày           │
│   làm việc.                                  │
│                                              │
│   [ Gửi yêu cầu hỗ trợ ]      [ Đóng ]    │
│                                              │
└──────────────────────────────────────────────┘
```

Bấm "Gửi yêu cầu hỗ trợ" → hệ thống **tự động tạo ticket** (Gen-Green User ID, Scalef User ID, lý do reject, timestamp). User không cần nhập gì. Email thông báo gửi về admin.

### Bảng lý do reject

| Check | Điều kiện | User thấy |
|-------|-----------|-----------|
| Trước SSO | Gen-Green user đã liên kết Scalef user khác | "Tài khoản Gen-Green của bạn đã liên kết với tài khoản Scalef khác." |
| 1 | Scalef user đã liên kết Gen-Green user khác | "Tài khoản Scalef này đã liên kết với tài khoản Gen-Green khác." |
| 2 | CCCD 2 bên khác nhau | "Thông tin CCCD không khớp giữa 2 tài khoản." |
| 2 | SĐT 2 bên khác nhau | "Số điện thoại không khớp giữa 2 tài khoản." |
| 2 | Email 2 bên khác nhau | "Email không khớp giữa 2 tài khoản." |
| 3 | CCCD Scalef đã thuộc Gen-Green user khác | "CCCD này đã được sử dụng bởi tài khoản Gen-Green khác." |
| 3 | SĐT Scalef đã thuộc Gen-Green user khác | "Số điện thoại này đã được sử dụng bởi tài khoản Gen-Green khác." |
| 3 | Email Scalef đã thuộc Gen-Green user khác | "Email này đã được sử dụng bởi tài khoản Gen-Green khác." |

---

## 7. Quy tắc nghiệp vụ

| Quy tắc | Chi tiết |
|---------|---------|
| **1-đối-1** | 1 Gen-Green user ↔ 1 Scalef user |
| **Thông tin khác → reject** | CCCD, SĐT, Email: cả 2 bên đều có mà khác nhau → reject. 1 bên thiếu → bỏ qua, cho qua |
| **Trùng user khác → reject** | CCCD/SĐT/Email Scalef đã thuộc Gen-Green user khác → reject |
| **Không tự gỡ** | Chỉ admin gỡ liên kết |
| **Scalef ID từ backend** | Frontend không gửi Scalef ID, backend tự inject khi gọi API Scalef |
| **Reject → ticket tự động** | Hệ thống tự tạo ticket, user không nhập gì. Hẹn phản hồi 3 ngày |
| **Ghi log mọi thứ** | Liên kết, reject, gỡ đều lưu lịch sử |

---

## 8. Chuẩn hóa dữ liệu trước khi so sánh

| Trường | Chuẩn hóa | Ví dụ |
|--------|----------|-------|
| CCCD | Bỏ khoảng trắng, chỉ giữ số | "012 345 678 901" → "012345678901" |
| SĐT | Đưa về +84, bỏ khoảng trắng | "0912 345 678" → "+84912345678" |
| Email | Viết thường, bỏ khoảng trắng | "User@Gmail.COM " → "user@gmail.com" |

---

## 9. Dữ liệu lưu trữ

### User model — thêm fields

| Trường | Kiểu | Mô tả |
|--------|------|-------|
| `scalef_user_id` | string, nullable | ID tài khoản Scalef đã liên kết |
| `scalef_linked_at` | datetime, nullable | Thời điểm liên kết |
| `scalef_link_method` | enum, nullable | `"oauth"` / `"batch"` / `"auto_create"` |

### Bảng lịch sử liên kết

| Trường | Kiểu | Mô tả |
|--------|------|-------|
| `id` | ObjectId | |
| `gen_green_user_id` | string | |
| `scalef_user_id` | string | |
| `action` | enum | `"linked"` / `"unlinked"` / `"rejected"` |
| `method` | enum | `"oauth"` / `"batch"` / `"admin"` |
| `reject_reason` | string, nullable | Lý do reject |
| `performed_by` | string | User ID hoặc Admin ID |
| `timestamp` | datetime | |

---

*Tham chiếu: [Tích hợp Scalef Affiliate vào Gen-Green](./gengreen-scalef-affiliate-integration-proposal.md) · [Brainstorm 2026-04-01](../../.bmad/brainstorming-gengreen-scalef-account-linking-2026-04-01.md)*
