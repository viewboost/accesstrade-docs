# Gap #33 — Ambassador có cơ chế "tạo user giả để reserve referral code", TCB và vCreator không có

> **Priority**: 🟡 **P2** (cần verify business need của TCB/vCr trước khi triển khai)
> **Source**: Phát hiện khi verify gap #31 (2026-05-07) — Ambassador `Create` admin có concept khác mục đích
> **Direction port**: Ambassador → TCB/vCr (nếu có business need)
> **Last verified**: 2026-05-07

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

Trong các campaign marketing, có khái niệm **"system referral code"** — code đặc biệt được dành riêng cho 1 mục đích (vd: "VIP2024", "TET2025", "PARTNER-ANKER") để **track nguồn user đăng ký từ campaign nào**.

Cách hoạt động của system referral code:
- Marketing tạo campaign "Đăng ký với code VIP2024 nhận quà"
- User đăng ký với `referralCode=VIP2024` → hệ thống cần biết code này hợp lệ + track user này thuộc campaign đó
- Sau campaign, ops report được "có X user đăng ký từ code VIP2024"

**Vấn đề**: ai sẽ "sở hữu" code VIP2024? Hệ thống cần 1 user record sở hữu code này — nhưng đó không phải user thật của ai cả.

**Hiện trạng 3 sản phẩm**:

### Ambassador — Có flow ✅
- Admin tạo "referral seed user" qua endpoint `POST /admin/users` với body chỉ có `ref` (code mong muốn, vd: "VIP2024")
- Hệ thống tạo user giả với:
  - Tên: `ref-VIP2024`
  - Email giả: `ref-VIP2024@system.local`
  - Password = refCode
  - `Referral.Codes` chứa code admin nhập
- User thật đăng ký với code này → hệ thống tìm user giả → attach inviter relation → track campaign

### TCB và vCreator — Không có ❌
- Cả 2 đều có model `Referral` giống Ambassador (cùng `Codes []string`)
- Nhưng KHÔNG có flow admin tạo "seed user" để reserve code
- Code chỉ được tạo khi user thật đăng ký (`Referral.Codes = [userCode]`)
- → Marketing không thể reserve code trước, không track campaign trước user nào đăng ký

## Bảng so sánh 3 sản phẩm (góc nhìn business)

| Khía cạnh | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| **Có concept Referral code không?** | ✅ Có (model giống Amb) | ✅ Có | ✅ Có |
| **Marketing reserve code trước khi user đăng ký?** | ❌ Không | ❌ Không | ✅ Có (admin tạo seed user) |
| **Tạo "system referral code" cho campaign promotion?** | ❌ Không | ❌ Không | ✅ Có |
| **Track user nào đăng ký từ code VIP2024?** | 🟡 Chỉ track inviter relation nếu code thuộc user thật | 🟡 Tương tự TCB | ✅ Tracked đầy đủ qua seed user |

## Use cases business

1. **Marketing campaign promotion**: launch campaign "Đăng ký với code TET2025 nhận quà" → cần reserve code này trước, không phụ thuộc user nào
2. **Partner co-marketing**: ký hợp đồng với Anker → reserve code "ANKER-2025" → mọi creator đăng ký với code này được attribute cho Anker
3. **Influencer ambassador program**: cấp code riêng cho 1 KOL nổi tiếng để chia sẻ → KOL không cần đăng ký vào platform mà vẫn có code track được
4. **A/B test**: tạo nhiều code khác nhau (vd: VIP2024-A, VIP2024-B) → đo conversion rate

## Hệ quả khi không có (TCB và vCreator)

1. **Marketing thiếu công cụ campaign tracking**: không thể launch campaign promotion với code reserve trước → phải dùng cách khác (UTM tracking, landing page riêng) ít chính xác hơn
2. **Co-marketing với partner khó**: không thể issue code riêng cho partner → partner không nhìn rõ ROI campaign của họ
3. **Workaround thủ công**: marketing phải tự tạo 1 user thật với code mong muốn → user data dirty, khó audit
4. **Influencer ambassador không thể implement**: KOL không phải creator của platform → không có cách cấp code riêng

## Đề xuất giải pháp (góc nhìn business)

**Khuyến nghị**: Port concept "referral seed user" từ Ambassador sang TCB và vCreator **NẾU** marketing/business có nhu cầu campaign promotion.

**Effort dự kiến**: ~3-5 ngày dev mỗi sản phẩm (rất nhỏ — chỉ thêm 1 admin endpoint).

**Việc cần làm**:
- Backend: thêm admin endpoint `POST /admin/users/create-referral-seed` với body `{ref: string}`
- Backend: tạo user record với pattern `name="ref-{code}"`, email giả, password=refCode, `Referral.Codes = [userCode, refCode]`
- Backend: audit log "Admin created referral user with code: X"
- Admin UI: form simple "Create Referral Code" — input code, submit → success message
- Optional: trang list referral codes (xem có codes nào active, mỗi code đã track bao nhiêu user)

**Cần product/business confirm trước khi triển khai**:
1. **Marketing TCB** có nhu cầu tạo system referral code cho campaign promotion không? (vd: TCB chạy campaign "Đăng ký nhận voucher" với code riêng)
2. **Marketing vCreator** có nhu cầu tương tự không? (vCreator B2B workplace có thể ít cần — partner đã có HR registry)
3. **Ambassador**: feature này đã chạy production OK chưa? Có data thực tế để verify business value không?
4. **Naming convention**: pattern `ref-{code}` cho name + email giả OK không, hay cần convention khác cho TCB/vCr?
5. **Cleanup policy**: sau campaign kết thúc, có cần xóa hoặc disable seed user không? (Ambassador hiện tại không có)

**Cảnh báo data quality**:
- Pattern này tạo user "giả" với email không thật → data hơi dirty
- Cần đảm bảo các flow downstream (notification, email, profile browse) không gửi email/notification cho seed user
- Nên thêm flag `IsReferralSeed` để phân biệt (Ambassador hiện tại không có flag → khó filter)

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

Ambassador có endpoint admin `POST /admin/users` với business logic riêng:
- Body: chỉ có `Ref` (referral code admin muốn reserve)
- Backend tạo user giả với `name="ref-{ref}"`, email giả, `Referral.Codes = [generatedCode, ref]`
- Public register sau đó dùng `body.Ref` để tìm user giả → attach inviter relation

TCB và vCreator có cùng `ReferralInfo` model nhưng không có flow admin tạo seed user.

## Verify code

### Ambassador stack (`pkg/admin/service/user.go:484`)

```go
func (s userImpl) Create(ctx, body request.CreateUserBody) (res response.CreateUserResponse, err error) {
    refCode := strings.ToLower(strings.TrimSpace(body.Ref))

    // 1. Check ref code chưa được dùng
    existing := UserDAO.CountByCondition(ctx, ..., bson.M{"referral.codes": refCode})
    if existing > 0 {
        return res, errors.New(locale.ReferralKeyCodeIsExisted)
    }

    // 2. Generate userCode unique
    code := s.generateCode(ctx)  // 7 chars random

    // 3. Tạo user giả
    name := fmt.Sprintf("ref-%s", refCode)
    email := fmt.Sprintf("ref-%s@system.local", refCode)
    user := &modelmg.UserRaw{
        Name, Email,
        Code, Hashtag: "#" + code,
        Referral: &modelmg.ReferralInfo{
            Enabled: true,
            Codes: []string{code, refCode},  // ← CONTAIN cả userCode và refCode admin nhập
        },
        HashedPassword: util.HashPassword(refCode),
        Status: StatusActive,
        ...
    }
    Insert user

    // 4. Audit log
    s.createAudit(user, s.Staff.ID, fmt.Sprintf("Admin created referral user with code: %s", refCode))

    return CreateUserResponse{ID, Name, Code: user.Code}
}
```

**Body schema** (`pkg/admin/model/request/user.go`):
```go
type CreateUserBody struct {
    Ref string `json:"ref"`
}

func (m *CreateUserBody) Validate() error {
    return validation.ValidateStruct(m,
        validation.Field(&m.Ref,
            validation.Required.Error(locale.ReferralKeyCodeRequired),
            validation.Length(7, 20).Error(locale.ReferralKeyCodeInvalid),
            validation.Match(regexp.MustCompile(`^[a-zA-Z0-9]+$`)).Error(locale.ReferralKeyCodeInvalid)),
    )
}
```

**Router** (`pkg/admin/router/user.go:28`):
```go
gRoot.POST("", h.Create, v.CreateUser)  // ← chỉ root staff được gọi
```

### Public register dùng seed user (`pkg/public/service/user.go:1925`)

```go
// 3. Check referral code
var inviter = new(modelmg.UserRaw)
if body.Ref != "" {
    _ = UserDAO.FindOne(ctx, inviter, bson.D{
        {"referral.codes", body.Ref},  // ← tìm user nào có codes chứa body.Ref
        {"referral.enabled", true},
    })
    if inviter.ID.IsZero() {
        return res, errors.New(locale.UserKeyReferralCodeNotFound)  // ← code không hợp lệ
    }
}

// 4. Create New user (user thật)
// ...

// Sau khi tạo user thành công, attach referral relation
if !inviter.ID.IsZero() {
    go func() {
        _, _ = Referral().InputReferralCode(context.Background(), user.ID, body.Ref)
    }()
}
```

→ User thật đăng ký với `body.Ref="VIP2024"` → tìm user nào có `referral.codes` chứa "VIP2024" → đó là seed user → attach inviter relation. User thật trở thành "invitee" của seed user.

### TCB và vCreator status

```bash
# Cả 2 đều có model ReferralInfo giống Amb
grep "type ReferralInfo" {tcb,vcr}/backend/internal/model/mg/user.go → có

# Nhưng KHÔNG có admin endpoint tạo seed
grep 'fmt.Sprintf("ref-%s",' {tcb,vcr}/backend/pkg/admin/ → 0 results

# CreateUserBody khác (không phải referral seed)
# TCB CreateUserRequest: name, email, partner, staffCode, companyCode → admin tạo creator thật
# vCreator: không có CreateUser admin nói chung
```

→ TCB có `CreateUser` nhưng cho mục đích khác (admin proxy creator — gap #31). vCreator không có admin create user nào.

## Đề xuất implementation

### Phase 1: Schema (~0 ngày — không cần thay đổi)
- Cả TCB và vCreator đã có `ReferralInfo.Codes []string` → reuse
- Optional: thêm flag `IsReferralSeed bool` vào `UserRaw` để filter dễ hơn (Ambassador hiện tại không có flag, dùng pattern tên `ref-{code}` để identify)

### Phase 2: Admin endpoint (~2-3 ngày)
- Copy logic từ Ambassador `pkg/admin/service/user.go:Create` (chỉ ~70 LOC)
- Adapt với constants/locale của target sản phẩm
- Tránh conflict với existing `CreateUser` (TCB đã có `CreateUser` cho proxy creator) → đặt tên endpoint khác (vd: `POST /admin/users/referral-seed` hoặc `POST /admin/referral-codes`)
- Validate code format (7-20 chars alphanumeric, lowercase)

### Phase 3: Audit + cleanup logic (~1 ngày)
- Thêm audit log với ActorType (nếu đã port gap #5)
- Thêm flag `IsReferralSeed=true` (recommend — easier filter)
- Optional: thêm endpoint `DELETE /admin/users/referral-seed/{id}` để cleanup code không dùng

### Phase 4: Admin UI (~1 ngày)
- Form đơn giản: input code, submit
- Hiển thị danh sách codes đã tạo + count user invited
- Optional: link tới analytics campaign

**Total effort**: ~3-5 ngày mỗi sản phẩm.

## Risks + mitigations

1. **Email giả `ref-{code}@system.local`** có thể conflict với email thật nếu domain `system.local` được dùng đâu đó
   - **Mitigation**: dùng UUID-based email (`ref-{uuid}@noreply.local`) hoặc domain riêng không tồn tại
2. **Seed user xuất hiện trong list creator** → ops/admin confused
   - **Mitigation**: thêm flag `IsReferralSeed` + filter mặc định trong admin user list
3. **Notification system gửi email cho seed user** → bounce email
   - **Mitigation**: check flag `IsReferralSeed` trong notification flow → skip
4. **Naming convention conflict** với existing `CreateUser` (TCB)
   - **Mitigation**: endpoint riêng `/admin/users/referral-seed` thay vì reuse `/admin/users`

## Files referenced

**Ambassador (source of truth)**:
- `pkg/admin/handler/user.go:328-353` — `Create` admin handler
- `pkg/admin/service/user.go:484-548` — Create service logic
- `pkg/admin/model/request/user.go:CreateUserBody` — body schema
- `pkg/admin/router/user.go:28` — router POST /users
- `pkg/public/service/user.go:1925-1960` — public register dùng seed user
- `pkg/public/service/referral.go:InputReferralCode` — attach inviter relation
- `internal/model/mg/user.go:ReferralInfo` — Codes []string

**TCB (cần port)**:
- `internal/model/mg/user.go:ReferralInfo` — đã có ✅
- KHÔNG có admin endpoint create referral seed
- Đã có `CreateUser` admin nhưng cho mục đích khác (proxy creator — gap #31)

**vCreator (cần port)**:
- `internal/model/mg/user.go:ReferralInfo` — đã có ✅
- KHÔNG có admin endpoint create user nào (chỉ `CreateUserContractManually` cho user đã tồn tại)

## Liên quan đến gap khác

- **Gap #31** (TCB admin proxy creator flow): cùng touch admin user create endpoint. Khi port cả 2:
  - Endpoint `/admin/users` → CreateUser cho proxy creator (gap #31)
  - Endpoint `/admin/users/referral-seed` → CreateReferralSeed (gap #33)
  - Cần phân biệt rõ naming để dev không confuse
- **Gap #5** (ActorType audit): khi port, dùng ActorType=`human_admin` cho audit log

## Lịch sử phân loại

- **2026-05-07 (phát hiện)**: Khi verify gap #31 (admin proxy creator flow), thấy Ambassador có `Create` admin handler nhưng làm việc khác — tạo "referral seed user" thay vì proxy creator
- **2026-05-07 (tách thành gap #33)**: User confirm: *"Tạo thêm 1 cái cho Ambassador, Có nhưng khác mục đích (referral seed) → cũng là 1 gap"*
- **Direction port**: Ambassador → TCB/vCr (Ambassador là source of truth)
- **Priority P2**: tentative, tăng lên P1 nếu marketing có nhu cầu campaign promotion với code reserve

### Bài học methodology

- Khi 1 sản phẩm "có feature nhưng khác mục đích" — đó **không phải bug đoán nhầm**, mà là **gap kiến trúc** (1 sản phẩm có capability mà 2 sản phẩm khác không có)
- Direction port có thể **ngược chiều** với gap chính (gap #31 port TCB→vCr/Amb, gap #33 port Amb→TCB/vCr) — vì mỗi sản phẩm có innovation riêng cần share
- Khi compare cross-product, không phải lúc nào TCB cũng là source of truth — cần verify business intent từng feature
