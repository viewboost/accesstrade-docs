# Gap #12 — vCreator/Ambassador thiếu lớp bảo vệ cho admin login

> **Priority**: ⚪ **P3** (reclassified P0→P3 2026-05-07 sau khi verify thực tế)
> **Source**: [semantic-diff-infrastructure-misc.md](../../semantic-diff-infrastructure-misc.md)
> **Direction port**: TCB → vCreator + Ambassador
> **Last verified**: 2026-05-07

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

Khi admin (staff TCB / vCreator / Ambassador) đăng nhập trang quản trị, có 2 vấn đề an toàn:

1. **Brute force**: Hacker thử mật khẩu hàng nghìn lần — server không có gì chặn → nếu password yếu, sớm muộn cũng bị crack
2. **Audit trail**: Không lưu lịch sử login — sau khi có incident (vd: dữ liệu bị thay đổi bất thường), không biết ai đã login từ IP nào lúc nào

**Hiện trạng**:
- **TCB** ✅ có cả 2 lớp bảo vệ:
  - **Rate limit**: thử password sai 7 lần trong 5 phút → block IP+email 2 tiếng
  - **Audit log**: ghi mọi lần login vào collection `AuditLoginRaw` (IP, email, timestamp, success/fail)
- **vCreator + Ambassador** ❌ KHÔNG có gì:
  - Hacker có thể thử password vô hạn lần — chỉ phụ thuộc vào CDN/firewall ở tầng trên (không có ở application layer)
  - Không có log → khó forensics khi có incident

**Ghi chú quan trọng — KHÔNG có OTP cho admin ở cả 3 dự án**:
- Tên hàm `CheckRateLimitRequestOTP` ở TCB là **misleading** (legacy naming)
- Thực tế nó chỉ rate limit **password login attempts**, KHÔNG có OTP gửi qua email/SMS cho admin
- Cả 3 dự án admin đăng nhập chỉ bằng email + password
- Cũng không có 2FA, không có Login Google ở UI admin (backend có handler nhưng frontend không gọi — dead code)

## Bảng so sánh 3 sản phẩm (góc nhìn business)

| Khía cạnh | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| **Admin đăng nhập bằng gì?** | Email + password | Email + password | Email + password |
| **Có OTP / 2FA không?** | ❌ Không | ❌ Không | ❌ Không |
| **Có Login Google ở UI?** | ❌ Không (backend có handler dead) | ❌ Không (backend có handler dead) | ❌ Không (backend có handler dead) |
| **Server chặn brute force password?** | ✅ Có (7 lần / 5 phút → block 2h) | ❌ Không | ❌ Không |
| **Server lưu log mọi lần login?** | ✅ Có | ❌ Không | ❌ Không |
| **Phát hiện được "ai đã login từ IP lạ"?** | ✅ Có | ❌ Không | ❌ Không |
| **Có lớp bảo vệ ở Cloudflare/nginx?** | (cần verify) | (cần verify) | (cần verify) |

→ **Cả 3 sản phẩm đều ở mức bảo mật cơ bản** (chỉ password). TCB hơn ở chỗ có monitoring + rate limit ở application layer.

## Rủi ro nếu không sửa (cho vCr/Amb)

**Rủi ro thấp đến trung bình**:
1. **Brute force password**: nếu admin nào đó dùng password yếu (vd: `admin123`) → có thể bị crack. Nhưng điều kiện cần: hacker biết email admin + endpoint admin
2. **Khó audit khi có incident**: nếu data bị thay đổi bất thường, không thể trace được "ai đã login từ IP nào" → mất khả năng forensics
3. **Không phát hiện attack đang diễn ra**: nếu hacker đang thử password, không có alert nào báo

**Rủi ro được giảm bởi**:
- vCr/Amb có Cloudflare/nginx có thể đã có rate limit chung ở tầng trên (cần verify với DevOps)
- Admin pool nhỏ, ít người ngoài biết URL admin
- vCr/Amb không phải target tấn công cao như platform tài chính (TCB là banking → target lớn hơn)

→ **Đây là lý do reclassify từ P0 xuống P3**: lớp bảo vệ là **defense-in-depth tốt** nhưng không phải critical fix.

## Đề xuất giải pháp (góc nhìn business)

**Khuyến nghị**: **Defer** cho đến khi có một trong các trigger sau:

1. **Compliance team yêu cầu** (vd: SOX, ISO 27001 audit log requirement)
2. **Có incident brute force** thực tế (admin nào đó báo thấy nghi ngờ)
3. **vCr/Amb mở rộng admin pool** (nhiều staff hơn → bề mặt tấn công lớn hơn)
4. **Rảnh resource** → backport easy win (~2-3 ngày)

**Khi triển khai**, port 3 thứ từ TCB:

1. **Audit log model** (`AuditLoginRaw`) — lưu mọi login attempt
2. **Rate limit middleware** + Redis key block
3. **Config thresholds** (mặc định: 7/5min → 2h block — có thể chỉnh)

**Effort dự kiến**: 2-3 ngày developer, ~113 LOC backend mỗi sản phẩm. Không cần migration data, không break gì.

**Cần product/business confirm**:
1. Có Cloudflare/nginx rate limit ở tầng trên cho vCr/Amb không? (xem DevOps có yêu cầu doublé bảo vệ application layer)
2. Compliance Ambassador có chuẩn audit log cụ thể không?
3. Admin pool TCB lớn hơn vCr/Amb bao nhiêu lần? (nếu vCr/Amb cũng mở rộng → revisit priority)
4. Có cân nhắc add 2FA cho admin (Google Authenticator, SMS OTP) trong tương lai không? Nếu có → port chung block này luôn.

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

| Component | TCB | vCreator | Ambassador |
|---|---|---|---|
| `internal/service/check_rate_limit.go` | ✅ 113 LOC, 2 fns | ❌ | ❌ |
| Model `AuditLoginRaw` | ✅ 33 LOC | ❌ | ❌ |
| Middleware `CheckRateLimitLoginAdmin` | ✅ wired | ❌ | ❌ |
| Middleware `CheckRateLimitAuthExchange` | ✅ wired (dead path — UI không gọi) | ❌ | ❌ |
| Endpoint `POST /staffs/login` | ✅ với rate limit | ✅ không rate limit | ✅ không rate limit |
| Endpoint `POST /staffs/login-with-google` | ✅ backend (dead — UI không gọi) | ✅ backend (dead) | ✅ backend (dead) |
| Endpoint `POST /staffs/auth/exchange` | ✅ backend (dead — UI không gọi) | ❌ | ❌ |

## Verify 5-layer (theo methodology)

### Layer 1: Code tồn tại

**TCB** (`internal/service/check_rate_limit.go`):
```go
type RateLimit struct {
    RemoteIP string
    StaffID  modelmg.AppID
}

// CheckRateLimitRequestOTP — TÊN GÂY HIỂU LẦM, thực tế là rate limit password attempts
func (r RateLimit) CheckRateLimitRequestOTP(ctx context.Context) (int, error) {
    // Count audit log entries với activity = "login_admin" trong window
    // Nếu vượt threshold → set Redis key block IP
}

// CheckRateLimitAuthExchange — limits auth code exchange to 5/min/IP
func (r RateLimit) CheckRateLimitAuthExchange(ctx context.Context) (int, error) {...}
```

**Constants** trong `audit_login.go`:
```go
const AuditLogActionLoginAdmin    = "login_admin"
const AuditLogActionAuthExchange  = "auth_exchange"
```

**Config defaults** (`config.go:GetLoginRateLimit`):
- Maximum: 7 attempts
- Window: 5 minutes
- BlockDuration: 2 hours

### Layer 2: Code được gọi

**Routes có rate limit** (TCB `pkg/admin/router/staff.go`):
```go
g.POST("/login", h.Login, v.Login, a.CheckRateLimitLoginAdmin)               // line 21
gAuth.POST("/exchange", h.ExchangeAuthCode, v.ExchangeAuthCode, a.CheckRateLimitAuthExchange)  // line 34
```

**Audit log được ghi** (TCB `pkg/admin/service/staff.go` — function Login):
```go
defer func() {
    _ = daomongodb.AuditLoginDAO().GetShare().InsertOne(ctx, &modelmg.AuditLoginRaw{
        ID, User: staff.ID, RemoteIP: remoteIP,
        Payload: &AuditLogPayload{Email: body.Email},
        Activity: AuditLogActionLoginAdmin,
        CreatedAt, UpdatedAt,
    })
}()
```

→ **Login attempt được log mỗi lần**, kể cả failed (defer chạy cả khi error).

### Layer 3: Runtime behavior

**Flow khi user gọi `POST /staffs/login` ở TCB**:
1. Middleware `CheckRateLimitLoginAdmin` chạy trước
2. Service lookup `AuditLoginRaw` count attempt với `activity=login_admin`, `remoteIP=X`, trong window 5 phút
3. Nếu count ≥ 7 → set Redis key `BlockIPRequestOTP:{staffID|anonymous}:{IP}` TTL 2h, return error 429
4. Nếu chưa block → cho qua, hàm Login chạy
5. Sau Login (thành công hay fail), defer ghi `AuditLoginRaw`

→ Lần thử thứ 8 trong 5 phút sẽ bị 429. Block 2h kể cả password đúng (phải đợi).

### Layer 4: vCr/Amb có flow tương đương không?

**Verify**:
```bash
# vCreator + Ambassador
grep -rln "RateLimit\|AuditLogin\|BlockIP" vcreator/backend/internal/ vcreator/backend/pkg/ambassabor/backend/internal/ ambassabor/backend/pkg/
# → 0 kết quả
```

→ **Hoàn toàn không có**:
- Không có service rate limit
- Không có model audit_login
- Login service không defer ghi log
- Router admin login không có middleware rate limit

vCr/Amb function `Login` (đã grep):
```go
func (s staffImpl) Login(ctx context.Context, body request.StaffLoginBody) (response.StaffAuthenResponse, error) {
    // KHÔNG có defer audit
    // Match email + verify password
    // Trả token nếu OK
}
```

→ Không có audit, không có rate limit ở application layer.

### Layer 5: Direction port + caveat

**Direction**: TCB → vCreator + Ambassador

**Caveat từ user clarify**:
- Tên hàm `CheckRateLimitRequestOTP` có chữ "OTP" gây hiểu lầm. **KHÔNG có OTP cho admin ở cả 3 dự án.**
- Login Google ở admin chỉ là **dead code endpoint** (giống pattern gap #1): backend có handler nhưng frontend admin 3 dự án đều KHÔNG gọi `login-with-google`. Người dùng trong code TCB là `pkg/public/handler/user.go` (cho user creator, không phải admin).
- Auth code exchange flow của TCB cũng chỉ ở backend, frontend admin TCB hiện tại không gọi `/auth/exchange`. Có thể là feature multi-device đã build nhưng chưa expose UI.

→ Nếu port sang vCr/Amb, **chỉ port phần `CheckRateLimitLoginAdmin` + `AuditLoginRaw`** là đủ. Bỏ qua `CheckRateLimitAuthExchange` vì cả 3 frontend đều không có flow exchange code.

## Đề xuất implementation (khi nào triển khai)

### Phase 1: Backend changes (~2 ngày mỗi sản phẩm)

#### Step 1: Tạo model `AuditLoginRaw`
File `internal/model/mg/audit_login.go` (33 LOC):
```go
type AuditLoginRaw struct {
    ID, User: AppID
    RemoteIP: string
    Payload: *AuditLogPayload  // {Email: string}
    Activity: string            // "login_admin"
    CreatedAt, UpdatedAt time.Time
}
```

#### Step 2: Copy `internal/service/check_rate_limit.go` từ TCB
- Strip `CheckRateLimitAuthExchange` (vì vCr/Amb không có flow exchange)
- Giữ lại `CheckRateLimitRequestOTP` (rename → `CheckRateLimitLogin` để clearer)
- Constants `AuditLogActionLoginAdmin = "login_admin"`

#### Step 3: Thêm middleware vào `pkg/admin/router/routeauth/auth.go`
```go
CheckRateLimitLoginAdmin(next echo.HandlerFunc) echo.HandlerFunc {
    rateLimit := internalservice.RateLimit{RemoteIP: cc.RealIP(), StaffID: ...}
    seconds, err := rateLimit.CheckRateLimitLogin(ctx)
    if err != nil { return cc.Response429(...) }
    return next(c)
}
```

#### Step 4: Wire middleware vào router
File `pkg/admin/router/staff.go`:
```go
g.POST("/login", h.Login, v.Login, a.CheckRateLimitLoginAdmin)
```

#### Step 5: Thêm audit log defer vào `Login` service
File `pkg/admin/service/staff.go`:
```go
defer func() {
    _ = daomongodb.AuditLoginDAO().GetShare().InsertOne(ctx, &modelmg.AuditLoginRaw{...})
}()
```

#### Step 6: Config defaults
File `internal/config/config.go`:
```go
func GetLoginRateLimit() LoginRateLimitCfg {
    cfg := env.LoginRateLimit
    if cfg.Maximum == 0       { cfg.Maximum = 7 }
    if cfg.Window == 0        { cfg.Window = 5 * 60 }
    if cfg.BlockDuration == 0 { cfg.BlockDuration = 2 * 60 * 60 }
    return cfg
}
```

### Phase 2: Test (~0.5 ngày)
- Unit test rate limit logic
- Integration test: thử password sai 8 lần → expect 429 lần thứ 8
- Verify audit log entry được tạo

### Phase 3: Optional cleanup (~0.5 ngày)
- **Rename** `CheckRateLimitRequestOTP` → `CheckRateLimitLogin` ở TCB để tránh hiểu lầm cho dev tương lai (cleanup tech debt liên quan)
- **Xóa dead code** `LoginWithGoogle` ở admin handler (hoặc xác nhận có roadmap revive)

## Effort estimate

| Task | Effort |
|---|---|
| Backend changes — vCreator | 2-3 ngày |
| Backend changes — Ambassador | 2-3 ngày |
| Test + verify | 1 ngày |
| Optional rename + dead code cleanup TCB | 0.5 ngày |
| **Tổng** | **~5-7 ngày dev** |

## Lịch sử phân loại

### Lần 1 — Initial classification (2026-05-07): SAI
- Priority: 🔴 **P0** (Total 17)
- Title: "TCB rate limit OTP cho admin"
- Sai vì: tin tên function `CheckRateLimitRequestOTP` → đoán có OTP flow

### Lần 2 — User push dò code thực tế (2026-05-07): ĐÃ ĐÚNG
User: *"bạn phải tự dò chứ — tôi là tôi chưa thấy mấy cái OTP ở chỗ nào luôn á"*

→ Verify code thực tế:
- TCB admin login chỉ password (không OTP)
- Login Google ở admin = dead code endpoint (frontend không gọi, giống pattern gap #1)
- AuthExchange flow chỉ backend (frontend cũng không gọi)
- Tên `CheckRateLimitRequestOTP` chỉ là legacy naming

→ Rename gap thành "Security cho admin login" thay vì "OTP".
→ User confirm reclassify P0 → **P3** vì vCr/Amb không phải target tấn công lớn, có thể defer.

### Bài học methodology

**Sai pattern lần thứ N**: Tin tên function/biến mà không đọc nội dung. `CheckRateLimitRequestOTP` đọc từ ngoài tưởng "có OTP flow"; vào trong mới biết là rate limit password attempt count audit log.

→ **Verify name vs implementation** trước khi tổng hợp. Function name có thể legacy/misleading.

## Files referenced

**TCB (source of truth)**:
- `internal/service/check_rate_limit.go` (113 LOC)
- `internal/model/mg/audit_login.go` (33 LOC)
- `pkg/admin/router/routeauth/auth.go:124-167` — middlewares
- `pkg/admin/router/staff.go:21,34` — wired endpoints
- `pkg/admin/service/staff.go` — function Login với defer audit
- `internal/config/config.go:GetLoginRateLimit` — config defaults

**vCreator + Ambassador (target — chưa cần port nếu là P3)**:
- `pkg/admin/service/staff.go` — function Login không có audit, không có rate limit
- `pkg/admin/router/staff.go` — login endpoint không có middleware rate limit

**Note về dead code**:
- `pkg/admin/router/staff.go` của 3 dự án đều có `POST /staffs/login-with-google` nhưng frontend admin không gọi
- TCB có thêm `POST /staffs/auth/exchange` cũng không được frontend gọi
- → Có thể document chung với gap #1 (dead code endpoint pattern)
