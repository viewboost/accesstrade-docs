# Technical Specification: Mời nhân sự qua email và tự quản lý mật khẩu — Ambassador Admin Portal

**Date:** 2026-09-29
**Author:** Nguyễn Đăng Định
**Version:** 1.0 — đồng bộ với code tại commit `2baf13649`
**Status:** Final
**PRD:** [prd-moi-nhan-su-va-mat-khau-2026-09-29.md](./prd-moi-nhan-su-va-mat-khau-2026-09-29.md) v2.0
**Repo:** `AT-Core/ambassador`

| Nhánh | Nền | Trạng thái |
|---|---|---|
| `feat/staff-invite-password` | `release` (`ccda54288`) | Đã merge vào `release` — PR #253 (2026-09-29) |
| `feat/staff-invite-password-develop` | `develop` (`254dc9c30`) + merge nhánh trên | Đã merge vào `develop` — PR #252 (2026-09-29) |

---

## 1. Tổng quan

Tài liệu mô tả cách hiện thực hoá PRD v2.0. Thuật ngữ dùng theo mục 0 của PRD; mã FR/NFR/HF trỏ về PRD.

### Nguyên tắc

**Port logic backend của T-Fluencers, viết mới phần giao diện.** Cơ chế lời mời, token và email lấy theo T-Fluencers (TF). Phần frontend viết mới vì hai hệ đăng nhập ở hai ứng dụng khác nhau.

Chỉ đi khác TF ở ba loại chỗ, ghi rõ tại từng mục:

1. Ràng buộc kiến trúc Ambassador (mục 1.2)
2. Lỗi đã kiểm chứng trên mã nguồn TF — sửa, không port (PRD mục 2.3)
3. Thứ TF không có: thu hồi lời mời, rate limiting cho quên mật khẩu, fail-closed

### 1.1 Bảng đối chiếu file nguồn ↔ file đích

| Chức năng | T-Fluencers (`Viewboost-2025/techcombank`) | Ambassador |
|---|---|---|
| Model | `internal/model/mg/staff.go` | như nguồn — thêm trường lời mời, `InviteStatus`, `AcceptedAt` |
| Service mời | `pkg/admin/service/staff.go` (gộp chung) | **tách file**: `staff_invite.go`, `staff_password_reset.go`, `staff_auth_token.go`, `staff_auth_mail.go`, `staff_login_lookup.go` |
| Rate limiting | trong `staff.go`, đếm theo IP, mặc định tắt | **viết mới**: `staff_auth_attempt_limit.go` |
| Router | `pkg/admin/router/staff.go` | như nguồn, thêm `revoke-invite`, bỏ `login-with-google` |
| Request/validation | `pkg/admin/model/request/staff.go` | tách `request/staff_auth.go` |
| Locale | `internal/locale/staff.go` | tách `locale/staff_auth.go`, `locale/password_limit.go` |
| Template email | `internal/module/sendgird/templates/staff_auth.go` (render Go) | `internal/module/smtp/templates/*.html` — **chỉ là file mẫu** gửi AT, gateway render |
| Trang nhận lời mời / quên / đặt lại | `dashboard/src/app/[locale]/…` (Next.js) | **viết mới**: `admin/src/pages/staff-auth/` (umi 3) |
| Màn quản lý nhân sự | `admin/src/pages/staff/` | như nguồn về luồng, viết lại component |

### 1.2 Ràng buộc bắt buộc

| # | Ràng buộc | Hệ quả kỹ thuật |
|---|---|---|
| 1 | Nhân sự Ambassador đăng nhập ở Admin Portal (umi 3, antd 4), không có ứng dụng `dashboard` | 3 trang công khai viết mới, khai `layout: false` và bỏ qua `GET /staffs/me` khi khởi tạo (mục 9.1) |
| 2 | Quản lý nhân sự chỉ Root (PQ-011) | Mọi endpoint quản lý lời mời nằm dưới middleware `IsRoot`, không cần kiểm ADV người mời |
| 3 | ADV của nhân sự là tuỳ chọn (RQ-4) | `partner` trong body mời không bắt buộc, giữ đúng hành vi API tạo cũ |
| 4 | Email qua API AccessTrade bằng bộ khoá `ACCESS_TRADE_SMS_*` | Không có luồng SMTP dự phòng như TF; gửi thất bại thì báo `emailSent=false` |
| 5 | Code cắt từ `release` (RQ-8) | Không dùng được Lịch sử đăng nhập (chỉ có trên `develop`) → FR-013 hoãn |

### 1.3 Cấu trúc commit

| Commit | Nội dung | Phát hành độc lập được |
|---|---|---|
| `267b9be96` fix(backend) | HF-1 → HF-3 và script dọn audit | Có — build và test riêng đã đạt |
| `991fa039d` feat(backend) | Toàn bộ backend của tính năng | Cần commit trước |
| `2baf13649` feat(admin) | Admin Portal | Cần backend |

---

## 2. Model, hằng số, cấu hình

### 2.1 `StaffRaw` — bổ sung trường

File: `backend/internal/model/mg/staff.go`. Mọi trường mới `omitempty`: bản ghi cũ không có trường nào, không cần migration.

| Trường | BSON | Kiểu | Ý nghĩa |
|---|---|---|---|
| `Password` | `password` | string | **Thêm `json:"-"`** (HF-1) — `createAudit` chụp document bằng JSON |
| `InviteToken` | `inviteToken` | string, `json:"-"` | SHA-256 hex của token mời. Xoá khi nhận, thu hồi, hoặc đổi email |
| `InviteExpiry` | `inviteExpiry` | *time.Time | Hạn token mời |
| `InviteStatus` | `inviteStatus` | string | `pending` / `accepted` / `revoked`. Rỗng = tài khoản tạo theo luồng cũ |
| `InvitedBy` | `invitedBy` | AppID | Người gửi lời mời **gần nhất** (gửi lại thì ghi đè) |
| `InvitedAt` | `invitedAt` | *time.Time | Thời điểm gửi gần nhất |
| `AcceptedAt` | `acceptedAt` | *time.Time | Thời điểm nhận lời mời |
| `ResetToken` | `resetToken` | string, `json:"-"` | SHA-256 hex của token đặt lại mật khẩu |
| `ResetExpiry` | `resetExpiry` | *time.Time | Hạn token đặt lại |

### 2.2 Vòng đời lời mời

```
               Invite / BulkInvite
                      │
                      ▼
   ┌──────────── pending (active=false, chưa mật khẩu) ─────────────┐
   │                  │                                              │
   │ RevokeInvite     │ AcceptInvite                                 │ quá inviteExpiry
   ▼                  ▼                                              ▼
revoked ──────▶  accepted (active=true, có mật khẩu)          expired (chỉ suy ra
   │  ResendInvite                                             khi trả về, không lưu)
   └──────────────▶ pending                          ◀──── ResendInvite
```

- `expired` **không lưu DB**. `staffInviteStatusForDisplay` suy ra khi `pending` mà `inviteExpiry` rỗng hoặc đã qua. `inviteExpiry` rỗng xảy ra khi admin đổi email của lời mời đang chờ (mục 4.11).
- "Lời mời còn mở" (`isStaffInviteOpen`) = `pending` hoặc `revoked`. Tài khoản còn mở không bật/tắt trạng thái được, không đặt mật khẩu hộ được (FR-006).
- Tài khoản chờ có `active=false` và không có mật khẩu → cửa đăng nhập (lọc `active=true`, so bcrypt) không bao giờ cho qua trước khi nhận lời mời.

### 2.3 Hằng số

| Hằng | File | Giá trị |
|---|---|---|
| `constants.StaffInviteStatus` | `internal/constants/staff.go` | `pending`, `accepted`, `revoked`, `expired` |
| `EmailTemplateStaffInvite` | `internal/constants/email_template.go` | `AMBASSADOR_EMAIL_STAFF_INVITE` — **tạm đặt, chờ AT cấp** |
| `EmailTemplateStaffResetPassword` | như trên | `AMBASSADOR_EMAIL_STAFF_RESET_PASSWORD` — **tạm đặt** |
| `staffInviteTTL` / `staffResetTTL` | `pkg/admin/service/staff_auth_token.go` | 48 giờ / 60 phút |
| `staffAcceptInvitePath` / `staffResetPasswordPath` | như trên | `/accept-invite` / `/reset-password` |
| `StaffPasswordMinLength` / `StaffBulkInviteMax` | `pkg/admin/model/request/staff_auth.go` | 8 ký tự / 50 email |
| `util.PasswordMaxBytes` | `internal/util/password_limit.go` | 72 byte |

### 2.4 Cấu hình

| Biến | Bắt buộc | Dùng cho |
|---|---|---|
| `ADMIN_WEB_HOST` | Không | Dựng đường dẫn trong thư. Thiếu → mời, gửi lại, quên mật khẩu trả lỗi cấu hình. Đây là **kill switch** (NFR-009) |
| `ACCESS_TRADE_SMS_*` (4 khoá) | Không khai `required` | Client API email AT. Service admin **phải có** cùng giá trị với service public — tới nay admin chưa gửi email thành công lần nào (PRD D-3) |

`ADMIN_WEB_HOST` được `strings.TrimSpace` và cắt `/` cuối trước khi dùng.

---

## 3. Database & Redis

### 3.1 MongoDB

- **Không migration.** Bản ghi cũ thiếu trường mời → giao diện hiện "Tạo thủ công".
- **Không thêm unique index cho `email`** (RQ-10). Kiểm trùng bằng `CountByCondition` trước khi ghi; mời hàng loạt ghi tuần tự nên hai dòng trùng trong cùng danh sách không cùng lọt.
- **So email không phân biệt hoa thường** qua `staffEmailFilter`: `{"email": {$regex: "^<QuoteMeta(email)>$", $options: "i"}}`. Regex có cờ `i` không dùng index hiệu quả; chấp nhận vì collection `staffs` nhỏ. `regexp.QuoteMeta` chặn ký tự đặc biệt trong email biến thành pattern.
- **Tra token** theo `inviteToken` / `resetToken` (hash) — không index, cùng lý do.
- **Single-use** bảo đảm bằng `FindOneAndUpdate` gộp điều kiện và `$unset` token trong một lệnh (mục 5.3).

### 3.2 Redis — bộ đếm rate limiting

Khoá: `staff_auth_attempt:<rule>:<subject>`, giá trị là số đếm, TTL = cửa sổ.

| `rule` | `subject` | Ví dụ |
|---|---|---|
| `login:email` | email đã chuẩn hoá (lowercase, trim) | `staff_auth_attempt:login:email:an@x.com` |
| `login:ip` | IP từ `c.RealIP()` | `staff_auth_attempt:login:ip:203.0.113.5` |
| `forgot:email` | email đã chuẩn hoá | |
| `forgot:ip` | IP | |

Ngưỡng ở mục 6.1.

### 3.3 Script dọn audit (HF-1)

`backend/scripts/strip-staff-password-from-audits.js` — mongosh.

- Lọc `audits` có `data` là chuỗi chứa `"Password":"`
- Parse JSON, `delete Password`, ghi lại; không parse được thì thay bằng regex
- **Mặc định chạy thử** (chỉ đếm). Ghi thật: `--eval 'var APPLY = true'`
- Chạy lại an toàn: bản ghi đã dọn không còn khớp bộ lọc
- Header script có lệnh `mongoexport` backup đúng các bản ghi sẽ sửa

---

## 4. Backend — API

### 4.1 Router

File: `backend/pkg/admin/router/staff.go`. Prefix `/api/admin/staffs`.

| Method | Path | Middleware | Handler | Ghi chú |
|---|---|---|---|---|
| POST | `/invite` | `IsRoot` | `StaffAuth.Invite` | FR-001 |
| POST | `/bulk-invite` | `IsRoot` | `StaffAuth.BulkInvite` | FR-002 |
| POST | `/:id/resend-invite` | `IsRoot` | `StaffAuth.ResendInvite` | FR-004 |
| POST | `/:id/revoke-invite` | `IsRoot` | `StaffAuth.RevokeInvite` | FR-005 |
| PUT | `/me/update-password` | `RequiredLogin` | `StaffAuth.UpdateMyPassword` | FR-010 |
| POST | `/invite/verify` | công khai | `StaffAuth.VerifyInviteToken` | FR-007 |
| POST | `/invite/accept` | công khai | `StaffAuth.AcceptInvite` | FR-007 |
| POST | `/forgot-password` | công khai | `StaffAuth.ForgotPassword` | FR-008, FR-012 |
| POST | `/reset-password` | công khai | `StaffAuth.ResetPassword` | FR-009 |
| ~~POST~~ | ~~`/login-with-google`~~ | — | — | **Gỡ route**: handler và validation chỉ có `panic("implement me")`, FE không gọi |

Endpoint công khai không có middleware đăng nhập. Chống đoán token nhờ entropy 256 bit; `forgot-password` có bộ đếm riêng.

### 4.2 Định dạng phản hồi

Theo khuôn chung `{code, message, data}`; `code: 1` là thành công.

| HTTP | Khi nào | `data` |
|---|---|---|
| 200 | Thành công | tuỳ endpoint |
| 400 | Lỗi nghiệp vụ, validate | `null`; `message` là câu tiếng Việt theo locale (mục 8) |
| 429 | Chạm ngưỡng rate limiting | `{"retryAfterSeconds": <int>}` — thời gian chờ dài nhất trong các bộ đang chặn |
| 503 | Không đọc được bộ đếm Redis | `{}` |

`respondStaffAuthError` (`handler/staff_auth.go`) đổi `StaffAuthThrottledError` → 429, `StaffAuthUnavailableError` → 503, còn lại → 400. Hàm `Login` có sẵn dùng cùng hàm này.

### 4.3 Mời một nhân sự — `POST /invite`

Request `StaffInviteBody`: `name` (bắt buộc), `email` (bắt buộc), `role` (MongoID, bắt buộc), `partner` (MongoID, tuỳ chọn).

Validate: email được trim + lowercase; **tra MX** (`is.Email`) để bắt tên miền gõ nhầm.

Luồng:

1. `staffAdminWebHost()` — thiếu cấu hình thì dừng **trước khi ghi DB**, không để lại tài khoản chờ không gửi được thư
2. `resolveStaffRoleAndPartner` — role phải tồn tại; partner nếu có phải tồn tại
3. `createInvitedStaff` — kiểm trùng email (không phân biệt hoa thường) → sinh token → insert bản ghi `pending`, `active=false`, không mật khẩu
4. Gửi thư (timeout 15 giây)
5. Audit "Đã gửi lời mời qua email" (goroutine)

Response `StaffInviteResponse`: `{"_id", "emailSent"}`. **Cố ý không trả đường dẫn** (PRD 2.3 #3, RQ-1). Thư lỗi → `emailSent=false`, Root dùng "Gửi lại".

### 4.4 Mời hàng loạt — `POST /bulk-invite`

Request `StaffBulkInviteBody`: `role`, `partner`, `items: [{email, name?}]`, 1–50 phần tử. Mọi dòng cùng vai trò, cùng ADV.

Luồng:

1. Kiểm cấu hình, role, partner một lần cho cả lượt
2. **Ghi DB tuần tự** từng dòng:
   - `ValidateForBulk` — **chỉ kiểm định dạng** (`is.EmailFormat`), không tra MX: tra MX tuần tự 50 lần có thể vượt timeout 60 giây của proxy
   - Trùng trong danh sách (`seen` map) → lỗi dòng
   - Tên trống → lấy phần trước `@`
   - Trùng trong DB → lỗi dòng
3. **Gửi thư song song**: 10 worker, mỗi thư timeout 5 giây. Xấu nhất 50 thư = 5 lượt × 5 giây = 25 giây
4. Audit từng tài khoản "Đã gửi lời mời qua email (mời nhiều)"

Response: `{"results": [{"email", "_id"?, "emailSent", "error"?}]}` — cùng thứ tự với `items`. Một dòng lỗi không làm hỏng cả lượt.

Khác TF (PRD 2.3 #4): TF xử lý song song, mỗi dòng tự kiểm trùng rồi ghi → hai dòng trùng email tạo hai tài khoản.

### 4.5 Gửi lại — `POST /:id/resend-invite`

- Điều kiện: `active=false` và `inviteStatus ∈ {pending, revoked}` (gồm cả pending đã hết hạn)
- `UpdateOne` với **điều kiện trạng thái lặp lại trong filter** — tránh race với người nhận đang bấm nhận lời mời. `MatchedCount == 0` → `InviteNotPending`
- `$set`: token mới, hạn mới, `inviteStatus=pending`, `invitedBy`/`invitedAt` = người gửi lại (khớp tên người gửi trong thư)
- Token cũ mất hiệu lực ngay vì bị ghi đè

### 4.6 Thu hồi — `POST /:id/revoke-invite`

- `UpdateOne` filter `{_id, active:false, inviteStatus:"pending"}` → `$set inviteStatus=revoked`, `$unset inviteToken, inviteExpiry`
- Giữ bản ghi để còn dấu ai mời ai. Muốn mời lại → Gửi lại
- `MatchedCount == 0` → `InviteNotRevocable`

### 4.7 Kiểm tra và nhận lời mời

**`POST /invite/verify`** — body `{token}`. Trang nhận lời mời gọi trước khi hiện form. Trả `{name, email}`.

**`POST /invite/accept`** — body `{token, password, confirmPassword}`.

- Validate mật khẩu theo `ValidateStaffNewPassword` (mục 4.12)
- **Một lệnh `FindOneAndUpdate`**:
  - filter `openInviteFilter`: `{inviteToken: sha256(token), inviteStatus: "pending", inviteExpiry: {$gt: now}}`
  - update: `$set password (bcrypt), active=true, inviteStatus=accepted, acceptedAt` + `$unset inviteToken, inviteExpiry`
- Không cấp phiên đăng nhập. FE chuyển về `/login?email=…` để đi đúng một cửa đăng nhập có rate limiting

Token không khớp → `inviteTokenError` phân biệt:

| Tình huống | Lỗi |
|---|---|
| Hash khớp, `pending`, nhưng quá hạn | `InviteTokenExpired` — "nhờ quản trị viên gửi lại" |
| Không khớp / đã dùng / đã thu hồi | `InviteTokenInvalid` |

Phân biệt không lộ gì cho người đoán mò vì chỉ người cầm đúng token mới thấy "hết hạn".

### 4.8 Quên mật khẩu — `POST /forgot-password`

Body `{email}`; validate chỉ kiểm định dạng (không tra MX — API công khai không làm dò DNS hộ người ngoài).

Luồng, theo đúng thứ tự:

1. `checkStaffAttempts(forgot:email, forgot:ip)` — chặn thì 429
2. **`hitStaffAttempts` ngay**, trước khi tra tài khoản. Đếm sau thì chỉ email có thật bị chặn → lộ tài khoản
3. Kiểm `ADMIN_WEB_HOST` — lỗi cấu hình trả như nhau cho mọi email
4. Tìm tài khoản `active=true` theo email (không phân biệt hoa thường). Không có → trả thành công
5. Có → `go issueStaffResetPassword(...)`: sinh token, ghi `resetToken`/`resetExpiry`, gửi thư. **Chạy nền** để nhánh "có tài khoản" không chậm hơn nhánh "không có" đúng một lượt ghi DB (account enumeration qua timing)

Tài khoản chờ nhận lời mời không nhận thư đặt lại — Root gửi lại lời mời.

### 4.9 Đặt lại mật khẩu — `POST /reset-password`

Body `{token, password, confirmPassword}`.

- `FindOneAndUpdate` filter `{resetToken: sha256(token), resetExpiry: {$gt: now}, active: true}` → `$set password`, `$unset resetToken, resetExpiry`
- Không khớp: đếm bản ghi có hash khớp + `active` → có thì `ResetTokenExpired`, không thì `ResetTokenInvalid`
- Thành công:
  - Xoá bộ đếm `login:email` — người vừa chứng minh sở hữu hộp thư không bị khoá tiếp
  - `resetToken(staff)` — **đăng xuất mọi phiên** (NFR-005)
  - Audit "Đã đặt lại mật khẩu qua email"

### 4.10 Tự đổi mật khẩu — `PUT /me/update-password`

Body `{currentPassword (bắt buộc), password, confirmPassword}`. TF để `currentPassword` tuỳ chọn → chiếm phiên là đổi được mật khẩu (PRD 2.3 #1).

Luồng:

1. Kiểm bộ đếm `login:email` của chính tài khoản — dùng chung với đăng nhập sai, để phiên bị chiếm không thành chỗ dò mật khẩu
2. Sai mật khẩu hiện tại → `hit`. Nếu **vừa chạm ngưỡng** → `resetToken(staff)` cắt mọi phiên (kể cả phiên đang dò) và trả 429. Chưa chạm → `CurrentPasswordWrong`
3. Mật khẩu mới trùng hiện tại → `PasswordSameAsCurrent`
4. Ghi mật khẩu → xoá bộ đếm → `resetToken` đăng xuất mọi phiên, gồm phiên hiện tại → audit

### 4.11 Đăng nhập — `POST /login`

Chữ ký đổi thành `Login(ctx, body, header echocustom.HeaderInfo)` để lấy IP.

1. `checkStaffAttempts(login:email, login:ip)`
2. `findActiveStaffForLogin`:
   - Tìm `active=true` theo `staffEmailFilter`, `limit 2`
   - 1 kết quả → dùng
   - 2 kết quả (dữ liệu cũ có email chỉ khác chữ hoa) → **quay về so khớp chính xác** như trước bản vá
3. Không tìm thấy → so bcrypt với **hash giả** (`staffLoginDummyHash`, sinh một lần, cùng cost 12) để thời gian phản hồi không lộ email tồn tại → `hit` → `LoginFailed`
4. Sai mật khẩu → `hit` → `LoginFailed`
5. Đúng → **xoá bộ đếm `login:email`** (không xoá bộ IP) → cấp token

Chỉ đếm lần **thất bại**; TF đếm cả lần thành công (PRD 2.3 #5).

Trên `develop`, bước 5 còn ghi Lịch sử đăng nhập (giữ nguyên code của `develop` khi merge — mục 12).

### 4.12 Thay đổi ở API quản lý nhân sự có sẵn

| API | Thay đổi | Lý do |
|---|---|---|
| `POST /register` | Kiểm trùng email không phân biệt hoa thường; **bỏ `res.Token`** (HF-3); chặn mật khẩu > 72 byte (HF-2) | FR-017, FR-018 |
| `PUT /:id/update-info` | Sửa filter kiểm trùng email: cũ đặt `"$nin"` ở cấp gốc là truy vấn không hợp lệ, đếm lỗi thành 0 nên **kiểm trùng khi sửa chưa từng chạy**. Nay `staffEmailFilter` + `_id: {$ne}` | Bug có sẵn |
| `PUT /:id/update-info` | Sửa email của lời mời `pending` → `$unset inviteToken, inviteExpiry` | Thư đã đi tới địa chỉ gõ nhầm; không huỷ thì người nhận nhầm chiếm được tài khoản |
| `PUT /:id/update-password` | Chặn tài khoản có lời mời còn mở; chặn > 72 byte | FR-006, HF-2 |
| `PATCH /:id/status` | Chặn tài khoản có lời mời còn mở | Bật `active` cho tài khoản chưa có mật khẩu tạo ra tài khoản "hoạt động" không ai đăng nhập được |
| `GET /staffs` | Trả `inviteStatus` (có `expired` suy ra), `inviteExpiry`, `invitedAt`, `invitedBy {_id, name}`, `acceptedAt`. Sửa data race: biến `role` dùng chung giữa các goroutine làm dòng này hiện vai trò của dòng khác | FR-003; bug có sẵn |

**Chính sách mật khẩu** (`ValidateStaffNewPassword`, cho 3 luồng mới):

| Luật | Đơn vị | Ghi chú |
|---|---|---|
| ≤ 72 | **byte** | Giới hạn bcrypt; kiểm trước tiên |
| ≥ 8 | **ký tự** (rune) | Đếm byte thì 4 chữ có dấu đã "đủ 8" |
| Có chữ và số | `unicode.IsLetter` / `IsDigit` | Chữ có dấu tính là chữ |
| Khớp xác nhận | | |

Luồng cũ (tạo kèm mật khẩu, đặt hộ) giữ tối thiểu 6 ký tự tới khi tắt (RQ-11), chỉ thêm trần 72 byte.

---

## 5. Token

### 5.1 Sinh và lưu

- 32 byte từ `crypto/rand` → `base64.RawURLEncoding` (43 ký tự, an toàn cho URL)
- DB chỉ lưu `hex(sha256(raw))`. SHA-256 đủ vì token đã đủ entropy; cần hàm băm **tất định** để tra ngược — không dùng bcrypt
- Bản gốc chỉ nằm trong thư. Response API không bao giờ chứa bản gốc hay hash (`json:"-"`)

### 5.2 Đường dẫn

`buildStaffAuthLink(host, path, raw)` = `ADMIN_WEB_HOST + path + "?token=" + url.QueryEscape(raw)`.

### 5.3 Single-use và race condition

| Thao tác | Cơ chế |
|---|---|
| Nhận lời mời, đặt lại mật khẩu | `FindOneAndUpdate` gộp điều kiện + `$unset` token trong một lệnh. Hai lần bấm cùng lúc: chỉ một lần khớp |
| Gửi lại lời mời | Điều kiện trạng thái lặp lại trong filter của `UpdateOne` |
| Yêu cầu đặt lại nhiều lần | Token mới ghi đè token cũ — chỉ thư gần nhất còn dùng được |

---

## 6. Rate limiting

File: `pkg/admin/service/staff_auth_attempt_limit.go`.

### 6.1 Luật

| Rule | Ngưỡng | Cửa sổ | Đếm gì |
|---|---|---|---|
| `login:email` | 5 | 15 phút | Đăng nhập sai; nhập sai mật khẩu hiện tại khi tự đổi |
| `login:ip` | 20 | 15 phút | Đăng nhập sai |
| `forgot:email` | 3 | 30 phút | **Mọi** lần gọi, kể cả email không tồn tại |
| `forgot:ip` | 10 | 60 phút | Mọi lần gọi |

Ngưỡng theo RQ-6; Security điều chỉnh được bằng một dòng.

### 6.2 Cơ chế

- **Fixed window**: `Hit` chạy `MULTI { SETNX key 0 EX window; INCR key }`. Đặt hạn trước rồi mới tăng, trong cùng transaction → tiến trình chết giữa chừng không để lại khoá không hạn (khoá không hạn = khoá vĩnh viễn)
- Chặn khi `count >= max`; thời gian chờ = `TTL` của khoá (TTL lỗi → dùng cả cửa sổ)
- Nhiều bộ cùng chặn → trả thời gian dài nhất
- `subject` rỗng (vd không lấy được IP) → không chặn, không đếm

### 6.3 Fail-closed (RQ-5)

`Get` trả lỗi khác `redis.Nil` → `StaffAuthUnavailableError` → HTTP 503.

Lý do: mọi request đã đăng nhập đều tra phiên trong Redis (`routeauth.Auth`). Redis sập thì Portal vốn không dùng được; fail-open chỉ mở khe brute-force không giới hạn đúng lúc hệ thống yếu nhất.

### 6.4 Email là lớp chính, IP là lớp phụ

IP lấy từ `c.RealIP()`. Server **chưa khai `IPExtractor`** nên `RealIP` đọc `X-Forwarded-For` do client gửi — đổi header là né được bộ IP. Vì vậy **không hạ ngưỡng email vì tin vào ngưỡng IP**. Khai `IPExtractor` đúng chuỗi proxy thật (Cloudflare: `CF-Connecting-IP`) là việc của DevOps (PRD D-4).

### 6.5 Log giám sát (NFR-013)

| Sự kiện | Log |
|---|---|
| Chặn 429 | `[staff-auth] chan <rule> <subject>, con <thời gian>` |
| Redis lỗi 503 | `[staff-auth] khong doc duoc bo dem <rule>: <err>` |
| Gửi thư | `[staff-auth] da gui …` / `gui … that bai toi <email>: <err>` |

Cảnh báo cần cấu hình trên hệ thống giám sát.

---

## 7. Email

File: `pkg/admin/service/staff_auth_mail.go`.

### 7.1 Kênh gửi

`core.Client().SmsGatewayAction(ctx, POST, "/v1.0/partner/email/send", nil, body, false)` — cùng đường với thư OTP của backend public. Body:

```json
{ "template_code": "AMBASSADOR_EMAIL_STAFF_INVITE", "template_data": { … }, "send_tos": ["an@x.com"] }
```

- API trả HTTP 200 kèm `status` trong body → chỉ coi là thành công khi `status == "success"`
- **`isDebug=false`**: bật debug thì resty in nguyên body ra log — tức in đường dẫn chứa token
- Timeout: 15 giây (mời lẻ, gửi lại, đặt lại), 5 giây (mời hàng loạt). Client gốc không đặt timeout

### 7.2 `template_data`

| Template | Khoá |
|---|---|
| Mời | `recipientName`, `inviterName` (trống → "Quản trị viên"; template không dùng — câu mời ghi cố định "Admin %company%"), `acceptUrl`, `expiryHours` ("48"), `year`, `company` ("AccessTrade") |
| Đặt lại | `recipientName`, `resetUrl`, `expiryMinutes` ("60"), `year`, `company` |

Trùng bộ biến với `TECHCOMBANK_EMAIL_STAFF_*` → AT nhân bản được (PRD D-1).

### 7.3 File mẫu HTML

`internal/module/smtp/templates/staff_invite_email.html`, `staff_reset_password_email.html` (bản sao trong `email-templates/` cạnh PRD).

- Biến viết theo cú pháp gateway **`%key%`** — cùng cú pháp bộ template TF đã bàn giao, AT dán thẳng được
- Header comment ghi tiêu đề email, ngôn ngữ, bảng biến, yêu cầu không log `acceptUrl`/`resetUrl`
- Test `TestStaffAuthMailData_MatchesHTMLSamples` đối chiếu hai chiều: mọi `%key%` trong mẫu phải có trong `template_data` và ngược lại; bỏ qua khối comment; báo lỗi nếu còn cú pháp `{{…}}`

### 7.4 Khi gửi thất bại

- Mời / gửi lại: `emailSent=false` trong response; FE báo "chưa gửi được" và gợi ý Gửi lại (NFR-007)
- Đặt lại: chỉ log (API đã trả thành công để chống enumeration)
- **Môi trường develop**: in đường dẫn ra log để QA đi tiếp luồng khi template chưa được cấp. Không bao giờ in ở staging/production (`config.IsEnvDevelop()`)

---

## 8. Locale

| File | Dải mã | Khoá |
|---|---|---|
| `internal/locale/password_limit.go` | 399 | `PasswordKeyTooLong` — dùng chung staff và creator (HF-2) |
| `internal/locale/staff_auth.go` | 250–267 | 18 khoá `StaffAuthKey*`, nằm trong dải staff 200–400 |

Đăng ký trong `locale.go`: `passwordLimitLoadLocale` ngay sau `commonLoadLocales`; `staffAuthLoadLocale` sau `staffLoadLocales`.

| Mã | Khoá | Mã | Khoá |
|---|---|---|---|
| 250 | InviteTokenInvalid | 259 | TooManyAttempts |
| 251 | ResetTokenInvalid | 260 | AdminWebHostMissing |
| 252 | InviteNotPending | 261 | BulkInviteEmpty |
| 253 | InviteNotRevocable | 262 | BulkInviteTooMany |
| 254 | InvitePendingNoStatus | 263 | BulkInviteDuplicate |
| 255 | PasswordWeak | 264 | EmailInvalid |
| 256 | PasswordConfirmInvalid | 265 | InviteTokenExpired |
| 257 | CurrentPasswordWrong | 266 | ResetTokenExpired |
| 258 | PasswordSameAsCurrent | 267 | Unavailable |

Nội dung tiếng Việt: PRD Phụ lục C.

---

## 9. Frontend — Admin Portal

### 9.1 Route công khai

| Route | Component |
|---|---|
| `/accept-invite` | `pages/staff-auth/accept-invite` |
| `/forgot-password` | `pages/staff-auth/forgot-password` |
| `/reset-password` | `pages/staff-auth/reset-password` |

Cả ba khai `layout: false` trong `config/routes.ts` **và** nằm trong `PUBLIC_PATHS` của `src/app.tsx`. Thiếu `PUBLIC_PATHS` thì `getInitialState` gọi `/staffs/me` không token và đá người nhận thư về `/login`.

### 9.2 `utils/request.ts` — gọi API công khai

| Thay đổi | Lý do |
|---|---|
| `requiredToken: false` → không gắn header `Authorization` | Trình duyệt còn token cũ đã hết phiên thì backend trả 401 |
| `parseJSON(response, redirectOn401)` — tắt redirect cho API công khai | 401 trên trang công khai (vd FE lên trước backend) hiện thành lỗi trên trang, không đá sang `/login` giữa chừng |

Service: `services/staff-auth.ts`. `staffAuthErrorMessage` ghép số phút chờ khi HTTP 429 (`data.retryAfterSeconds`).

### 9.3 Trang công khai

| Trang | Hành vi |
|---|---|
| Nhận lời mời | Gọi `verify` trước → hiện tên, email → form đặt mật khẩu → thành công: **xoá token đăng nhập trong `localStorage`** rồi về `/login?email=…` |
| Quên mật khẩu | Luôn hiện "Đã ghi nhận yêu cầu… nếu email thuộc một tài khoản đang hoạt động" |
| Đặt lại | Form đặt mật khẩu → thành công: xoá token trong `localStorage` → `/login` |

Xoá token trước khi chuyển trang: nếu không, token cũ còn trong `localStorage` làm `/login` tự vào hệ thống bằng phiên đã bị `resetToken` huỷ.

Component dùng chung: `staff-auth-shell.tsx` (khung trang), `new-password-form.tsx`.

### 9.4 Màn Nhân viên

| Thành phần | File | Ghi chú |
|---|---|---|
| Nút "Mời qua email", "Mời nhiều" | `pages/staff/index.tsx` | Nút tạo cũ giữ nguyên tới RQ-11 |
| Modal mời lẻ | `components/invite-modal.tsx` | Role/ADV lấy qua `use-role-partner-options.ts` |
| Modal mời nhiều | `components/bulk-invite-modal.tsx` | Hiện kết quả từng dòng sau khi gửi |
| Tách danh sách dán | `components/parse-bulk-invite.ts` | Mỗi dòng `email` hoặc `email, Họ tên`; tách bằng `,` `;` hoặc tab (dán từ Excel); lowercase; loại dòng sai định dạng và trùng; tối đa 50 |
| Cột trạng thái lời mời | `components/invite-status-cell.tsx` | Chờ nhận / Hết hạn / Đã nhận / Đã thu hồi / Tạo thủ công; tooltip người mời, thời điểm |
| Thao tác theo dòng | `components/table.tsx` | Lời mời còn mở: Gửi lại, Thu hồi (trừ `revoked`), **ẩn** đặt mật khẩu hộ, **khoá** công tắc trạng thái |

### 9.5 Đổi mật khẩu và đăng nhập

- `components/RightContent/change-my-password-modal.tsx` + mục "Đổi mật khẩu" trong `AvatarDropdown.tsx`. Thành công → đăng xuất về `/login` (backend đã huỷ mọi phiên)
- `pages/login/components/login-form.tsx`: link "Quên mật khẩu?"; tự điền email từ `?email=` **qua `useLocation()`**, không qua prop `location` — `develop` đã bỏ prop này khỏi form (mục 12)

### 9.6 Chính sách mật khẩu phía FE

`utils/staff-password.ts` khớp backend: độ dài theo `Array.from` (ký tự), trần 72 byte theo `TextEncoder`, có chữ (chữ có dấu tính là chữ) và số.

#### Ba điểm dễ sai ở tầng FE

1. Đếm độ dài bằng `value.length` — sai với chữ có dấu và emoji. Dùng `Array.from` cho ký tự, `TextEncoder` cho byte
2. Quên thêm route mới vào `PUBLIC_PATHS` — trang công khai bị đá về `/login`
3. Gọi API công khai bằng `request.call` mặc định — gắn token cũ, 401 làm redirect

---

## 10. Hotfix HF-1 → HF-3

Nằm riêng ở commit `267b9be96`, phát hành trước tính năng được.

| HF | Lỗi | Sửa | File |
|---|---|---|---|
| HF-1 | `createAudit` chụp `StaffRaw` bằng JSON, `Password` không có tag → hash bcrypt nằm trong `audits.data`; `GET /audits` chỉ cần đăng nhập | `json:"-"` cho `Password`; script dọn dữ liệu cũ (mục 3.3) | `model/mg/staff.go`, `scripts/strip-staff-password-from-audits.js` |
| HF-2 | `x/crypto` v0.47 trả `ErrPasswordTooLong` cho > 72 byte; `util.HashPassword` nuốt lỗi và trả chuỗi rỗng → lưu hash rỗng, tài khoản hỏng vĩnh viễn (staff và creator) | Chặn ở validate mọi luồng đặt mật khẩu; `HashPassword` log lỗi thay vì nuốt | `util/password_limit.go`, `util/hash.go`, `request/staff.go`, `public/model/request/user.go`, `locale/password_limit.go` |
| HF-3 | `POST /staffs/register` trả token phiên của người vừa tạo → Root cầm phiên hợp lệ 8 giờ của người khác | Bỏ `res.Token` | `service/staff.go` |

---

## 11. Ánh xạ FR/NFR → file

| Yêu cầu | Backend | Frontend |
|---|---|---|
| FR-001 Mời lẻ | `staff_invite.go` Invite | `invite-modal.tsx` |
| FR-002 Mời hàng loạt | `staff_invite.go` BulkInvite | `bulk-invite-modal.tsx`, `parse-bulk-invite.ts` |
| FR-003 Trạng thái lời mời | `staff.go` GetList, `staffInviteStatusForDisplay` | `invite-status-cell.tsx` |
| FR-004 Gửi lại | `staff_invite.go` ResendInvite | `table.tsx` |
| FR-005 Thu hồi | `staff_invite.go` RevokeInvite | `table.tsx` |
| FR-006 Ràng buộc tài khoản chờ, email duy nhất | `staff.go` UpdatePassword/ChangeStatus/UpdateInfo, `createInvitedStaff` | `table.tsx` |
| FR-007 Nhận lời mời | `staff_invite.go` Verify/AcceptInvite | `staff-auth/accept-invite` |
| FR-008 Quên mật khẩu | `staff_password_reset.go` ForgotPassword | `staff-auth/forgot-password` |
| FR-009 Đặt lại | `staff_password_reset.go` ResetPassword | `staff-auth/reset-password` |
| FR-010 Tự đổi | `staff_password_reset.go` UpdateMyPassword | `change-my-password-modal.tsx` |
| FR-011 Rate limiting đăng nhập | `staff_auth_attempt_limit.go`, `staff.go` Login | `services/staff-auth.ts` (hiện số phút chờ) |
| FR-012 Rate limiting quên mật khẩu | như trên | như trên |
| FR-013 Ghi nhận đăng nhập thất bại | **Hoãn** — mã đã viết trên nền `develop`, tác giả giữ dạng patch cục bộ (chưa đưa lên repo); áp lại khi Lịch sử đăng nhập lên `release` | — |
| FR-014 Audit | `createAudit` ở từng thao tác | — |
| FR-015, FR-016 Email | `staff_auth_mail.go`, `templates/*.html` | — |
| FR-017 Không cấp phiên khi tạo | `staff.go` Register | — |
| FR-018 Email không phân biệt hoa thường, chống enumeration | `staff_login_lookup.go`, `staffEmailFilter` | `login-form.tsx` |
| NFR-001, 002 Token | `staff_auth_token.go` | — |
| NFR-003 Mật khẩu | `request/staff_auth.go`, `util/password_limit.go` | `utils/staff-password.ts` |
| NFR-005 Session invalidation | `resetToken` sau reset/tự đổi/chạm ngưỡng | xoá `localStorage` trước khi về `/login` |
| NFR-009 Kill switch | `staffAdminWebHost` | — |

---

## 12. Đồng bộ sang `develop`

Nhánh nguồn cắt từ `release`; **không merge `develop` ngược vào nhánh nguồn** (PR vào `release` sẽ kéo theo 189 commit lạ).

Cách làm: nhánh `feat/staff-invite-password-develop` cắt từ `develop`, merge nhánh nguồn, giải conflict, mở PR vào `develop` (#252).

| File conflict | Cách giải |
|---|---|
| `backend/pkg/admin/service/staff.go` — hàm `Login` | Giữ goroutine ghi Lịch sử đăng nhập của `develop`; lấy phần rate limiting, `findActiveStaffForLogin`, dummy hash của nhánh nguồn |
| `admin/src/pages/login/components/login-form.tsx` — import | Giữ `getLandingRoute` của `develop`; thêm `Link`, `useLocation` |

**Lỗi ngữ nghĩa git không báo:** `develop` bỏ prop `location` khỏi `LoginForm`. Dòng tự điền email viết theo prop sẽ đọc nhầm `window.location` (không có `.query`) và âm thầm không chạy. Đã sửa ngay trên nhánh nguồn bằng `useLocation()`, để hai nhánh dùng chung một dòng.

**Tương thích vai trò `config_editor`** (chỉ có trên `develop`): mời được không cần sửa gì, vì luồng mời chọn vai trò theo bản ghi `Role` như API tạo nhân sự.

**Đối chiếu cây:** cây sau merge trùng khít `develop` + đúng phần thay đổi (`git diff` rỗng) → không file nào bị kéo về bản cũ, không mất thay đổi của `develop`.

Lần sau có commit mới: commit trên nhánh nguồn, rồi merge nhánh nguồn vào nhánh `-develop` — thường không conflict vì merge-base đã dời.

---

## 13. Test plan

### 13.1 Unit test (18 test mới)

| File | Test | Kiểm gì |
|---|---|---|
| `request/staff_auth_test.go` | `TestValidateStaffNewPassword` | Ký tự vs byte, chữ có dấu, chữ + số, 72 byte |
| | `TestStaffUpdateMyPasswordBody_RequiresCurrentPassword` | Bắt buộc mật khẩu hiện tại |
| | `TestStaffBulkInviteBody_Limits` | Rỗng, > 50 |
| | `TestStaffForgotPasswordBody_NormalizesEmail` | Trim, lowercase |
| | `TestStaffInviteBody_ValidateForBulkSkipsDomainLookup` | Hàng loạt không tra MX |
| `request/staff_password_limit_test.go` | `TestLegacyStaffPasswordFlows_RejectOver72Bytes` | HF-2 ở luồng cũ |
| `public/model/request/user_password_limit_test.go` | `TestCreatorPassword_RejectOver72Bytes` | HF-2 ở creator |
| `service/staff_auth_attempt_limit_test.go` | `…BlocksAtMaxAndReleasesAfterWindow` | Ngưỡng, hết cửa sổ |
| | `…ResetClearsCounter` | Xoá bộ đếm |
| | `…EmptySubjectNeverBlocks` | Subject rỗng |
| | `TestCheckStaffAttempts_RedisErrorFailsClosed` | Fail-closed |
| | `TestCheckStaffAttempts_ReturnsLongestWait` | Chờ dài nhất |
| | `TestStaffAttemptRules_AreSane` | Luật hợp lệ |
| `service/staff_auth_token_test.go` | `TestNewStaffAuthToken_RandomAndHashed` | Ngẫu nhiên, hash |
| | `TestBuildStaffAuthLink_EscapesToken` | Escape URL |
| | `TestStaffEmailFilter_CaseInsensitiveAndEscaped` | Regex `i`, `QuoteMeta` |
| | `TestStaffInviteStatusForDisplay` | Suy ra `expired` |
| | `TestStaffAuthMailData_MatchesHTMLSamples` | Biến mẫu ↔ `template_data` |

Bộ đếm Redis thay bằng fake qua interface `staffAttemptCounter` (fake trả `redis.Nil` khi chưa có khoá, như Redis thật).

### 13.2 Kịch bản tích hợp (QA, DB thật)

| # | Kịch bản | Kỳ vọng |
|---|---|---|
| 1 | Root mời → mở thư → đặt mật khẩu → đăng nhập | Trạng thái Chờ nhận → Đã nhận; `/login` điền sẵn email |
| 2 | Mở lại đường dẫn đã dùng | "Đường dẫn mời không hợp lệ" |
| 3 | Gửi lại → mở đường dẫn cũ | Đường dẫn cũ không hợp lệ, mới dùng được |
| 4 | Thu hồi → mở đường dẫn | Không hợp lệ; cột hiện Đã thu hồi; Gửi lại được |
| 5 | Chỉnh `inviteExpiry` về quá khứ → mở đường dẫn | "Lời mời đã hết hạn"; cột hiện Hết hạn |
| 6 | Mời nhiều 50 dòng gồm dòng trùng, sai định dạng, đã tồn tại | Kết quả từng dòng đúng; không tạo trùng |
| 7 | Mời email đã có với chữ hoa khác | "Email đã tồn tại" |
| 8 | Đăng nhập sai 5 lần | Lần 6 bị 429 kèm số phút; đúng mật khẩu cũng bị chặn tới hết cửa sổ |
| 9 | Quên mật khẩu với email có / không có tài khoản | Cùng thông báo, thời gian phản hồi tương đương; lần 4 trong 30 phút bị 429 |
| 10 | Đặt lại mật khẩu khi đang đăng nhập ở tab khác | Tab kia bị đăng xuất |
| 11 | Tự đổi mật khẩu, sai mật khẩu hiện tại 5 lần | Lần 5 bị 429 và mọi phiên bị cắt |
| 12 | Bỏ `ADMIN_WEB_HOST` | Mời, gửi lại, quên mật khẩu báo lỗi cấu hình; đăng nhập bình thường |
| 13 | Dừng Redis | Đăng nhập, quên mật khẩu trả 503 |
| 14 | Tài khoản chờ: bật trạng thái, đặt mật khẩu hộ | Bị chặn ở cả UI và API |
| 15 | Sửa email của lời mời đang chờ | Đường dẫn cũ mất hiệu lực; cột hiện Hết hạn |
| 16 | Mật khẩu 73 byte ở tạo nhân sự, đặt hộ, đăng ký creator | Bị từ chối; tài khoản không hỏng |
| 17 | `GET /audits` sau khi sửa nhân sự | Không có `Password` |

Trên develop khi template chưa được cấp: lấy đường dẫn từ log backend (`[staff-auth][develop] duong dan …`).

### 13.3 Kiểm tra trước khi merge

```bash
cd backend
go build ./pkg/... ./internal/... ./cmd/...
go test ./internal/... ./pkg/admin/... ./pkg/public/... -vet=off -count=1
# Đỏ sẵn, không liên quan: TestBuildDuplicateCheckFilter_* (pkg/public/service)

cd admin
# tsc 4.1.2 của repo ngã ở .d.ts — typecheck bằng TypeScript 5.x, lọc nhiễu umi
# (TS2305/TS2724/TS7xxx/TS6133). TS2769 ở AvatarDropdown onClick={onMenuClick} có sẵn.
```

---

## 14. Rollout

| Bước | Việc | Owner | Điều kiện |
|---|---|---|---|
| 0 | Phát hành HF (`267b9be96`); backup rồi chạy script dọn audit | Dev, DBA | Độc lập |
| 1 | AT cấp 2 mã template; cập nhật 2 hằng trong `email_template.go` | AT, Dev | Critical path |
| 2 | Khai `ADMIN_WEB_HOST`; kiểm service admin có đủ `ACCESS_TRADE_SMS_*`; khai `IPExtractor` | DevOps | Trước bước 3 |
| 3 | Phát hành backend | Dev | Có mã template thật |
| 4 | Phát hành Admin Portal | Dev | Sau bước 3 |
| 5 | Tắt luồng cũ (RQ-11) | PO, Dev | Email đã chạy thật trên production |

**Rollback:**

- Kill switch: bỏ `ADMIN_WEB_HOST`
- Backend: endpoint mới là bổ sung, bản cũ bỏ qua trường mới
- Dữ liệu: tài khoản chờ vẫn `active=false`, không đăng nhập được, không ảnh hưởng tài khoản khác
- Frontend: rollback độc lập

---

## 15. Rủi ro và nợ kỹ thuật

| # | Rủi ro / nợ | Mức | Xử lý |
|---|---|---|---|
| T-1 | Bộ đếm IP né được bằng `X-Forwarded-For` giả | Trung bình | Email là lớp chính; DevOps khai `IPExtractor` (D-4) |
| T-2 | Token nằm trong query string của trang FE → có thể vào access log của server phục vụ FE, lịch sử trình duyệt, header `Referer` | Thấp | Single-use + TTL. Nâng cấp sau: chuyển token sang fragment (`#token=`) hoặc đặt `Referrer-Policy: no-referrer` cho 3 trang công khai |
| T-3 | Regex email `i` không dùng index | Thấp | Collection `staffs` nhỏ; nếu lớn lên thì lưu thêm trường `emailLower` có index |
| T-4 | Không unique index cho email | Rất thấp | RQ-10; một Root, kiểm trùng trước khi ghi |
| T-5 | Audit ghi câu mô tả, chưa theo cấu trúc PQ-009 | Thấp | Chuyển khi PQ-009 phát hành (FR-014) |
| T-6 | FR-013 chưa có trên `release` | Thấp | Áp patch khi Lịch sử đăng nhập lên `release` |
| T-7 | Service admin thiếu `ACCESS_TRADE_SMS_*` mà không báo lỗi khi khởi động | Trung bình | DevOps kiểm trước bước 3 của rollout; triệu chứng là log `gui … that bai` |
| T-8 | AT cấp template chậm | Trung bình | Tính năng phát hành được, `emailSent=false` phản ánh đúng; kill switch |

---

## 16. Revision History

| Version | Date | Author | Thay đổi |
|---|---|---|---|
| 1.0 | 2026-09-29 | Nguyễn Đăng Định | Bản đầu, đồng bộ với code tại `2baf13649`, PR #253 (`release`) và #252 (`develop`) |
