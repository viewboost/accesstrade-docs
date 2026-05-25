# Gap #40 — Staff account: invite qua email + forgot password + self-service đổi password — TCB có, vCreator/Ambassador chỉ có admin tạo + copy password thủ công

> **Priority**: 🟠 **P1** (initial 2026-05-10 — user self-listed gap)
> **Source**: User self-listed gap
> **Direction port**: TCB → vCreator + Ambassador
> **Last verified**: 2026-05-10

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

Khi onboard nhân viên/admin mới vào platform, cần các flow standard:
1. **Invite qua email**: admin gửi link mời tới email staff → staff click link → set password lần đầu → vào hệ thống
2. **Forgot password**: staff quên password → tự reset qua email không cần admin can thiệp
3. **Self-service đổi password**: staff đang login đổi password của chính mình
4. **Bulk invite**: invite nhiều staff cùng lúc qua CSV/list

**TCB có đầy đủ 4 flow trên**.

**vCreator + Ambassador**: chỉ có "admin tạo staff với password đã set sẵn → admin copy password gửi thủ công cho staff qua Slack/Telegram". Staff quên pass → admin phải set lại + gửi lại thủ công.

→ **Vấn đề bảo mật**: password truyền qua kênh không bảo mật (chat, copy-paste). **Vấn đề ops**: tốn thời gian admin, dễ rơi rớt khi onboard nhiều người.

## Bảng so sánh

| Method/Flow | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| `Create` (admin tạo staff) | ✅ | ✅ | ✅ |
| `Login` / `LoginWithGoogle` | ✅ | ✅ | ✅ |
| `GetMe` / `UpdateInfo` | ✅ | ✅ | ✅ |
| `ChangeStatus` (active/inactive) | ✅ | ✅ | ✅ |
| `GetList` | ✅ | ✅ | ✅ |
| `UpdatePassword` (admin đổi cho người khác) | ✅ | ✅ | ✅ |
| **`UpdateMyPassword` (staff tự đổi password)** | ✅ | ❌ | ❌ |
| **`InviteStaff` (mời 1 staff qua email)** | ✅ | ❌ | ❌ |
| **`ResendInvite` (gửi lại email mời)** | ✅ | ❌ | ❌ |
| **`BulkInvite` (mời nhiều staff cùng lúc)** | ✅ | ❌ | ❌ |
| **`VerifyInviteToken` + `AcceptInvite` (staff accept invite, set password lần đầu)** | ✅ | ❌ | ❌ |
| **`ForgotPassword` + `ResetPassword`** | ✅ | ❌ | ❌ |
| **`GenerateAuthCode` + `ExchangeAuthCode` (auth code flow)** | ✅ | ❌ | ❌ |
| Field model `InviteToken` + `InviteExpiry` + `InviteStatus` + `ResetToken` | ✅ | ❌ | ❌ |
| Email template (invite, reset password) | ✅ (SendGrid templates `staff_auth.go`) | ❌ | ❌ |

**Service LOC**:
- TCB: 980 LOC `staff.go` admin service
- vCreator: 453 LOC (chỉ ~46% scope của TCB)
- Ambassador: 453 LOC (chỉ ~46% scope của TCB)

## Hệ quả

- **Bảo mật**: vCr/Amb truyền password qua chat/email không bảo mật → rủi ro leak credentials. Staff không có cách reset tự động nếu admin rời công ty.
- **Ops**: admin tốn thời gian set/copy password mỗi lần onboard, mỗi lần forgot. Onboard 10 staff cần 10 lần manual.
- **UX staff**: staff không tự reset được password → blocked đợi admin → giảm productivity.
- **Compliance**: nhiều standard compliance (ISO 27001, SOC 2) yêu cầu password hash + secure invite — vCr/Amb không đáp ứng.

## Liên quan các gap khác

- **Gap #12 (Admin login security)**: pair với gap này. #12 là rate limit + audit, #40 là password lifecycle. Có thể combo wave.
- **Gap #11 (Email transactional)**: cần email infrastructure (SendGrid hoặc SMTP) để gửi invite/reset email. Cả 3 đã có SMTP cơ bản, TCB còn dùng SendGrid template.
- **Gap #25 (Staff root account)**: là helper khác, không liên quan trực tiếp.

## Giải pháp

### Phase 1: vCreator (~5-7 ngày)

1. **Model migration** (~30 phút):
   - Thêm fields vào `Staff` struct: `InviteToken`, `InviteExpiry`, `InviteStatus`, `InvitedBy`, `ResetToken`
2. **Email templates** (~1 ngày):
   - 2 template SMTP/SendGrid: `staff_invite.html` (welcome + accept link), `staff_reset_password.html`
   - i18n vi/en
3. **Backend service** (~2-3 ngày, tham khảo TCB 527 LOC khác biệt):
   - `InviteStaff`: tạo staff record với status pending, generate token, gửi email
   - `ResendInvite`, `BulkInvite`: helpers
   - `VerifyInviteToken`, `AcceptInvite`: staff click link → verify token → set password
   - `ForgotPassword`, `ResetPassword`: tạo reset token, gửi email, verify, set new password
   - `UpdateMyPassword`: self-service đổi pass (verify old → set new)
   - `GenerateAuthCode`, `ExchangeAuthCode` (optional, low priority — TCB dùng cho SSO flow)
4. **Frontend admin** (~1-2 ngày):
   - Page invite staff (single + bulk CSV import)
   - Page accept-invite (public, no auth) → form set password
   - Page forgot-password (public)
   - Page reset-password (public, có token)
   - Settings: đổi password của mình
5. **Test** (~0.5-1 ngày):
   - E2E invite flow
   - Forgot password flow
   - Token expiry edge case

### Phase 2: Ambassador (~5-7 ngày)
- Tương tự Phase 1

**Total**: ~2-3 tuần (5-7 ngày mỗi sản phẩm).

## Tại sao P1

- **Bảo mật cao**: password truyền qua chat hiện tại là vấn đề security thật, không phải hypothetical
- **Effort tương đối lớn nhưng ROI cao**: ~1 tuần mỗi sản phẩm cho khoảng ~530 LOC service + 5 frontend pages
- **Pattern production-tested**: TCB đã có 18 methods, copy đầy đủ
- **Cross-product impact**: cả vCr lẫn Amb đều cần
- **Compliance baseline**: nhiều khách hàng B2B (đặc biệt enterprise) yêu cầu standard onboarding flow

→ Không phải P0 vì hiện tại workaround vẫn vận hành được (manual onboard) — nhưng sprint tới phải làm.

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

TCB có 18 staff methods (980 LOC service) đầy đủ invite/reset/self-service password lifecycle. vCr/Amb chỉ có 8 methods cơ bản (453 LOC) — admin tạo password thủ công, copy gửi qua chat, không có invite email, không có forgot password.

## Verify code

### TCB (source of truth)

**Handler interface** — `pkg/admin/handler/staff.go:23-40` (18 methods):
```go
type StaffInterface interface {
    // Common (cả 3 sản phẩm có)
    Create(c echo.Context) error
    Login(c echo.Context) error
    LoginWithGoogle(c echo.Context) error
    GetMe(c echo.Context) error
    UpdateInfo(c echo.Context) error
    UpdatePassword(c echo.Context) error      // admin đổi cho người khác
    ChangeStatus(c echo.Context) error
    GetList(c echo.Context) error

    // TCB-only (vCr/Amb thiếu 10 methods)
    UpdateMyPassword(c echo.Context) error    // self-service
    GenerateAuthCode(c echo.Context) error    // SSO flow
    ExchangeAuthCode(c echo.Context) error
    InviteStaff(c echo.Context) error
    ResendInvite(c echo.Context) error
    BulkInvite(c echo.Context) error
    VerifyInviteToken(c echo.Context) error
    AcceptInvite(c echo.Context) error
    ForgotPassword(c echo.Context) error
    ResetPassword(c echo.Context) error
}
```

**Model fields** — `internal/model/mg/staff.go:39-43`:
```go
type StaffRaw struct {
    // ... existing fields
    InviteToken  string    `bson:"inviteToken,omitempty"`
    InviteExpiry time.Time `bson:"inviteExpiry,omitempty"`
    InviteStatus string    `bson:"inviteStatus,omitempty"`  // pending, accepted, expired
    InvitedBy    AppID     `bson:"invitedBy,omitempty"`
    ResetToken   string    `bson:"resetToken,omitempty"`
}
```

**Email templates** — `internal/module/sendgird/templates/staff_auth.go`:
- Templates cho invite + reset password (TCB dùng SendGrid)

**Service LOC**: `pkg/admin/service/staff.go` — 980 LOC

### vCreator status

**Handler interface** — `pkg/admin/handler/staff.go:18-25` (8 methods):
```go
type StaffInterface interface {
    Create, Login, LoginWithGoogle, GetMe, UpdateInfo,
    UpdatePassword (admin đổi cho người khác),
    ChangeStatus, GetList
}
```

**Model fields**: ❌ KHÔNG có `InviteToken`, `InviteExpiry`, `InviteStatus`, `ResetToken`.

**Email templates**: ❓ chưa verify chi tiết, nhưng không có flow invite nên template không tồn tại.

**Service LOC**: 453 LOC (~46% scope TCB) + 1 file `staff_removal_cron.go` (cron riêng).

### Ambassador status

Tương tự vCreator: 8 methods, 453 LOC, không có invite/reset/self-service password fields.

## Đề xuất implementation

### Phase 1: vCreator (~5-7 ngày)

1. **Model migration** (~30 phút):
   ```go
   // vcreator/backend/internal/model/mg/staff.go
   type StaffRaw struct {
       // ... existing
       InviteToken  string    `bson:"inviteToken,omitempty"`
       InviteExpiry time.Time `bson:"inviteExpiry,omitempty"`
       InviteStatus string    `bson:"inviteStatus,omitempty"`
       InvitedBy    AppID     `bson:"invitedBy,omitempty"`
       ResetToken   string    `bson:"resetToken,omitempty"`
   }
   ```

2. **Constants** (~15 phút):
   ```go
   InviteStatusPending  = "pending"
   InviteStatusAccepted = "accepted"
   InviteStatusExpired  = "expired"

   InviteTokenExpiry = 7 * 24 * time.Hour  // 7 days
   ResetTokenExpiry  = 1 * time.Hour       // 1 hour
   ```

3. **Email templates** (~1 ngày):
   - vCreator có thể dùng SMTP base (không nhất thiết SendGrid)
   - Template `staff_invite.html`: link `https://admin.vcreator.com/accept-invite?token=...`
   - Template `staff_reset.html`: link `https://admin.vcreator.com/reset-password?token=...`
   - i18n vi/en

4. **Backend service** (~2-3 ngày, tham khảo TCB 527 LOC khác biệt):
   ```go
   // pkg/admin/service/staff.go
   func InviteStaff(ctx, payload, invitedBy) error {
       // validate email không trùng
       // generate UUID token
       // create Staff với InviteStatus=pending, InviteToken, InviteExpiry
       // send email via mailer
   }

   func VerifyInviteToken(ctx, token) (*StaffRaw, error) {
       // find by token, check expiry
   }

   func AcceptInvite(ctx, token, password) error {
       // verify token, set password (hash), clear token, set InviteStatus=accepted
   }

   func ForgotPassword(ctx, email) error {
       // generate reset token, set ResetToken, send email
   }

   func ResetPassword(ctx, token, newPassword) error {
       // verify token, set new password, clear token
   }

   func UpdateMyPassword(ctx, staffID, oldPwd, newPwd) error {
       // verify old, set new
   }
   ```

5. **Handler + router** (~0.5 ngày):
   - 9 endpoints mới (invite/resend/bulk/verify/accept/forgot/reset/my-password/auth-code)
   - Public routes cho accept-invite, forgot-password, reset-password (không cần auth)

6. **Frontend admin** (~1-2 ngày):
   - 5 pages mới: invite (single+bulk), accept-invite, forgot-password, reset-password, change-my-password
   - Bulk invite: paste CSV emails hoặc upload file
   - Token URL handling (extract from query string)

7. **Test** (~0.5-1 ngày):
   - E2E invite flow (gửi → accept → login)
   - Forgot password (gửi → reset → login)
   - Token expiry edge case
   - Bulk invite với invalid emails

### Phase 2: Ambassador (~5-7 ngày)
Tương tự Phase 1.

**Total**: ~2-3 tuần.

## Risks + mitigations

1. **Email deliverability**: invite/reset email có thể vào spam → staff không nhận được
   - **Mitigation**: dùng SendGrid (như TCB) hoặc verify SPF/DKIM domain. Có resend invite endpoint.
2. **Token security**: token leak qua URL → ai cũng dùng được
   - **Mitigation**: token expiry ngắn (7d invite, 1h reset), single-use (clear sau khi accept), hash trong DB nếu cần
3. **Brute force reset**: attacker spam ForgotPassword cho user → user bị spam email
   - **Mitigation**: rate limit endpoint (kết hợp gap #12), không reveal email tồn tại không (response generic)
4. **Migration data cũ**: staff đang chạy có cần force re-set password không?
   - **Mitigation**: KHÔNG force, giữ password hiện tại. Chỉ áp dụng flow mới cho staff invite mới hoặc forgot.
5. **i18n email**: subject + body theo locale staff
   - **Mitigation**: lưu locale preference trong Staff record, render template theo locale.
6. **Bulk invite — performance**: 100+ staff invite cùng lúc → email gửi tuần tự chậm
   - **Mitigation**: queue async (Asynq/Goroutine) gửi background, response immediate.

## Files referenced

**TCB (source of truth)**:
- `pkg/admin/handler/staff.go:23-40` (18 methods interface)
- `pkg/admin/service/staff.go` (980 LOC)
- `pkg/admin/router/staff.go` (routes including public for accept-invite, forgot, reset)
- `pkg/admin/model/request/staff.go` (StaffInviteBody, BulkInviteBody, ForgotPasswordBody, ...)
- `internal/model/mg/staff.go:39-43` (InviteToken, InviteExpiry, InviteStatus, InvitedBy, ResetToken fields)
- `internal/module/sendgird/templates/staff_auth.go` (email templates)

**vCreator (target — chưa có 10 methods)**:
- `pkg/admin/handler/staff.go:18-25` (chỉ 8 methods)
- `pkg/admin/service/staff.go` (453 LOC, ~46% scope TCB)
- `internal/model/mg/staff.go` — KHÔNG có InviteToken/ResetToken fields

**Ambassador (target — tương tự vCreator)**:
- Tương tự vCreator

## Lịch sử phân loại

- **2026-05-10 (initial P1)**: User self-listed gap. Quote: "Đổi mật khẩu cho staff account (mời, set password, đổi password) / TCB đã có đổi mật khẩu, gửi invite qua email cẩn thận, forgot password / Các bên còn lại chỉ có mỗi admin tạo ra, copy password gửi thủ công" + "P1".
  - Lý do P1: bảo mật cao (password truyền qua chat hiện tại là vấn đề security thật), effort vừa phải (~1 tuần mỗi sản phẩm), ROI cao, pattern production-tested. Pair tốt với #12 (admin login security) cho compliance baseline.
