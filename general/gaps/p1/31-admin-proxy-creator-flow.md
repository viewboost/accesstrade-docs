# Gap #31 — TCB cho phép admin tạo creator + import content giúp họ; vCreator/Ambassador không có

> **Priority**: 🟠 **P1** (reclassified P2→P1 2026-05-07)
> **Source**: Tách từ gap #13 (2026-05-07), rescope sau user clarify business intent
> **Direction port**: TCB → vCr/Amb (selective, theo business need)
> **Last verified**: 2026-05-07

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

Trong creator economy, có những trường hợp creator **không tự đăng ký** vào nền tảng:
- **Migration**: creator đã đăng nội dung trên TikTok/YouTube từ lâu, brand muốn import vào system mới mà creator chưa biết hệ thống
- **Onboarding partner**: partner mới (vd: Anker, HDBank) cung cấp danh sách creator + content history → admin set up giúp
- **Brand-managed**: brand muốn kiểm soát creator pool, tự tạo + quản lý thay vì để creator tự đăng ký
- **Backfill**: chạy campaign retroactive cho content đã đăng từ trước → admin link content vào event

Cho các use case này, hệ thống cần cho phép **admin đại diện creator** thực hiện toàn bộ flow:
1. Tạo creator account (thay vì creator tự register)
2. Link social channel của creator (thay vì creator tự link TikTok/YouTube)
3. Import content lịch sử của creator (thay vì creator tự submit từng cái)

**Hiện trạng 3 sản phẩm**:

### TCB — Có flow 3 bước đầy đủ ✅
- **Bước 1**: Admin tạo creator (`CreateUser`) — creator có flag `IsCreateByAdmin=true` để phân biệt với creator tự đăng ký
- **Bước 2**: Admin link social channel cho creator (`CreateUserSocial`) — paste link TikTok/YouTube, hệ thống verify channel
- **Bước 3**: Admin import content (`ImportContent`) — paste danh sách link content cho 1 event/user, hệ thống xử lý bulk
- Có theo dõi tiến độ + lịch sử (ai làm, lúc nào, item nào fail)

### vCreator — KHÔNG có ❌
- KHÔNG có flow admin tạo creator
- KHÔNG có flow admin link social channel
- KHÔNG có flow admin import content
- Chỉ có `CreateUserContractManually` (tạo contract record cho user **đã tồn tại** — concept khác)
- → Mọi creator phải tự đăng ký + tự link channel + tự submit content

### Ambassador — Có nhưng mục đích khác ⚠️
- Có `Create` user admin nhưng **KHÔNG phải proxy creator** — tạo user dạng "referral seed" (name `ref-{code}`, email giả) để gen referral code cho người khác đăng ký
- KHÔNG có admin link social
- KHÔNG có admin import content
- → Concept Ambassador hiện tại là "tạo seed cho referral", không phải "admin đại diện creator thật"

## Bảng so sánh 3 sản phẩm (góc nhìn business)

| Khía cạnh | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| **Admin tạo creator account thay creator** | ✅ Có (flag IsCreateByAdmin) | ❌ Không | 🟡 Có nhưng khác mục đích (seed referral) |
| **Admin link social channel cho creator** | ✅ Có | ❌ Không | ❌ Không |
| **Admin import content lịch sử cho creator** | ✅ Có (bulk + tracking) | ❌ Không | ❌ Không |
| **Phân biệt creator tự đăng ký vs admin tạo** | ✅ Có (flag) | — | — |
| **Theo dõi tiến độ import (đang xử lý / xong / fail)** | ✅ Có | — | — |
| **Lưu lịch sử các lần import (audit trail)** | ✅ Có | — | — |
| **Báo cáo chi tiết item nào fail và lý do** | ✅ Có | — | — |

→ TCB **cao cấp hơn nhiều** ở khía cạnh "admin operations" — vCr/Amb buộc creator phải tự thao tác mọi thứ.

## Tại sao cần (use cases business)

1. **Brand cung cấp data sẵn**: brand có database creator + content history → muốn import vào platform mà không yêu cầu creator phải đăng ký lại từ đầu
2. **Migration từ system cũ**: chuyển dữ liệu từ platform khác sang Ambassador/vCreator → cần tạo creator + content history một cách bulk
3. **Onboarding partner mới**: partner ký hợp đồng với platform → cung cấp list creator → admin set up giúp để partner có thể chạy campaign ngay
4. **Backfill sau incident**: server crash mất data → admin re-import từ backup
5. **Retroactive campaign**: brand muốn campaign apply cho content đã đăng từ trước (vd: trước khi creator biết campaign launch) → admin import content lịch sử

## Rủi ro / Hệ quả nếu không có

1. **Creator không bao giờ join platform được** nếu họ không tự đăng ký (vCr/Amb hiện tại) → mất cơ hội credit content
2. **Admin tốn nhiều thời gian thủ công**: phải request creator đăng ký, đợi creator link channel, đợi creator submit content → onboarding 1 partner có thể mất tuần
3. **Brand không thể quản lý creator pool tập trung**: phải dựa vào creator self-service → creator drop-off cao
4. **Không có audit trail**: nếu admin có thể manipulate (vd: sửa DB trực tiếp), không biết ai làm khi nào — risk compliance
5. **Migration data khó**: không có tool bulk → phải viết script hoặc làm manual khi migrate

## Đề xuất giải pháp (góc nhìn business)

**Khuyến nghị**: Port flow "admin proxy creator" từ TCB sang vCreator/Ambassador **NẾU** có business need rõ ràng (cần verify trước với product/PM).

**Effort dự kiến mỗi sản phẩm**: ~2-3 tuần (3 bước: schema + admin handler + admin UI cho từng bước)

**3 module cần port (có thể làm tuần tự hoặc cùng lúc)**:

### Module 1: Admin tạo creator (Tuần 1)
- API admin: `POST /admin/users` — admin nhập thông tin creator (tên, email, partner)
- Backend tạo `UserRaw` với flag `IsCreateByAdmin=true`
- Auto-bind với partner (`UserPartnerRaw`)
- Audit log: ai tạo, lúc nào

### Module 2: Admin link social channel (Tuần 1-2)
- API admin: `POST /admin/users/{id}/socials` — paste link TikTok/YouTube/FB của creator
- Backend verify channel tồn tại + crawl thông tin (followers, profile)
- Tạo `UserSocialRaw` link với user
- Có option skip crawl nếu admin đã có data sẵn

### Module 3: Admin bulk import content (Tuần 2-3)
- API admin: `POST /admin/contents/import` — paste danh sách link content cho 1 event + 1 user
- Backend xử lý từng item (validate, crawl, tạo content record), update tracking
- API admin: `GET /admin/contents/import-tracking` — xem lịch sử + drill-down item nào fail
- Async processing để không timeout với batch lớn

**Cần product/business confirm trước khi triển khai**:
1. **vCreator**: có nhu cầu "admin tạo creator thay creator" không? (vd: HR Vin import nhân viên xong, admin set up giúp creator account thay vì để nhân viên tự đăng ký)
2. **Ambassador**: có roadmap onboarding partner mới với data sẵn không? (vd: Anker chuyển từ system cũ sang Ambassador)
3. **Migration data cụ thể**: có đợt migrate creator nào sắp tới không? Format data thế nào (CSV/Excel/API)?
4. **Workflow phân quyền**: admin nào được quyền proxy creator? Có cần approval flow (vd: admin tạo → manager approve trước khi creator được activate)?
5. **Notification**: khi admin tạo creator, có gửi email cho creator biết không? Hay creator chỉ biết khi đăng nhập lần đầu?

→ Nếu **vCreator + Ambassador không có nhu cầu rõ** → defer P3. Hiện tại P2 là tentative.

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

TCB có **3 admin endpoints** đầy đủ cho flow proxy creator:
- `POST /admin/users` — `CreateUser` admin handler
- `POST /admin/users/socials` — `CreateUserSocial` admin handler
- `POST /admin/contents/import` — `ImportContent` admin handler + tracking collection

vCr/Amb không có gì trong cả 3 module này (Ambassador `Create` user khác mục đích — referral seed).

## Verify code

### TCB stack đầy đủ

**Module 1: `CreateUser` admin**

```go
// pkg/admin/handler/user.go:65, router POST /users
// pkg/admin/service/user.go:95
func (s userImpl) CreateUser(ctx, body request.CreateUserRequest) error {
    // Validate partner permission (root or staff.partner == body.partner)
    // Check email/staffCode unique
    u := &modelmg.UserRaw{
        Name, Email, StaffCode, CompanyCode,
        IsCreateByAdmin: true,  // ← KEY FLAG phân biệt với public register
        ...
    }
    InsertOne user
    InsertOne userPartner (auto-join)
}
```

**Module 2: `CreateUserSocial` admin**

```go
// pkg/admin/handler/user.go:50, router POST /users/socials
// pkg/admin/service/user.go:61
func (s userImpl) CreateUserSocial(ctx, body request.CreateUserSocialRequest) error {
    // Find user by ID
    // Check user belongs to staff's partner
    // Call internalservice.UserSocial().CheckUserSocialProfile() with IsSkipCrawlProfile option
}
```

**Module 3: `ImportContent` admin**

```go
// pkg/admin/handler/content.go:54, router POST /contents/import
// pkg/admin/service/content.go:ImportContent (lớn, ~250 LOC)
type ContentImportBody struct {
    UserID   string  // creator đã tồn tại
    EventID  string  // campaign event
    Contents []ContentImportItem
}

type ContentImportItem struct {
    Source string
    Link   []string
}

// Flow:
// 1. Validate event + user + permission
// 2. Tạo tracking record (status=processing)
// 3. Loop items: normalize source, group by source/userSocial
// 4. Trigger async crawl từng group
// 5. Return tracking ID cho admin poll progress

// Async update via callback (pkg/public/service/schedule.go):
// Khi crawl xong → update tracking item status=success/failed
// Khi processingItems=0 → tracking status=completed
```

**Tracking collection `internal/model/mg/content_import_tracking.go`**:
- `ContentImportTrackingRaw`: tổng quát (totalItems, successItems, processingItems, failedItems, status, contents[])
- `ContentImportTrackingItem`: per-item (source, link, contentID, status, message)

### vCreator status

```bash
ls vcreator/backend/internal/model/mg/ | grep content_import → 0 results
ls vcreator/backend/pkg/admin/handler/ | grep -E "import|^user.go" → user.go (chỉ có CreateUserContractManually)
```

→ KHÔNG có flow proxy creator. Chỉ có `CreateUserContractManually` để tạo contract record cho user đã tồn tại — concept khác.

### Ambassador status — có CreateUser nhưng khác mục đích

```go
// pkg/admin/service/user.go:484
func (s userImpl) Create(ctx, body request.CreateUserBody) (res, err) {
    refCode := body.Ref
    name := fmt.Sprintf("ref-%s", refCode)       // ← Tên giả
    email := fmt.Sprintf("ref-%s@system.local", refCode)  // ← Email giả
    user := &modelmg.UserRaw{
        Name, Email,
        Code, Hashtag,
        Referral: { Codes: [code, refCode] },
        HashedPassword: HashPassword(refCode),  // password = refCode
    }
    Insert user
}
```

→ Đây là pattern "tạo seed cho referral" (creator A tạo seed → bạn của A dùng refCode đăng ký → bind referral). KHÔNG phải proxy creator thật. KHÔNG có flow link social + import content tiếp theo.

## Đề xuất implementation

### Phase 1: Module 1 — Admin tạo creator (~5-7 ngày mỗi sản phẩm)
- Schema: thêm flag `IsCreateByAdmin` vào `UserRaw` (nếu chưa có) + migration default false
- Admin handler: `POST /admin/users` với validate body
- Admin service: tạo user + auto-bind partner + audit log
- Admin UI: form admin nhập thông tin creator

### Phase 2: Module 2 — Admin link social channel (~3-5 ngày)
- Tận dụng module crawl social hiện có (cả vCr/Amb đều có module crawl)
- Admin handler: `POST /admin/users/{id}/socials`
- Admin service: validate user + verify channel + skip-crawl option

### Phase 3: Module 3 — Admin bulk import content (~7-10 ngày)
- Schema: tạo `content_import_tracking` collection
- Admin handler: `POST /admin/contents/import` + `GET /admin/contents/import-tracking`
- Admin service: validate + tracking + async update
- Wire vào content crawl flow của target sản phẩm
- Admin UI: form upload + trang lịch sử

**Tổng effort**: ~3-4 tuần mỗi sản phẩm (full flow 3 modules).

**Có thể làm subset**: nếu vCr/Amb chỉ cần Module 3 (import content cho creator đã tồn tại) → effort giảm xuống ~1 tuần.

## Risks + mitigations

1. **Crawl integration khác nhau giữa vCr/Amb/TCB** → từng sản phẩm có module crawl riêng (TikTok, YouTube...) → port logic phải adapt
   - **Mitigation**: copy skeleton TCB, refactor per-source theo crawl module của target
2. **Permission check khác nhau** → TCB check root/partner. vCr/Amb có concept role khác
   - **Mitigation**: dùng role check existing của target sản phẩm
3. **Ambassador đã có `Create` user khác mục đích** → conflict naming convention
   - **Mitigation**: đổi tên `Create` thành `CreateReferralSeed` để rõ nghĩa, thêm `CreateUser` mới cho proxy creator flow
4. **Email creator khi admin tạo**: TCB hiện không gửi email (creator không biết account đã được tạo)
   - **Mitigation**: thêm option `notifyCreator: bool` cho admin chọn

## Files referenced

**TCB (source of truth)**:
- `pkg/admin/handler/user.go:65` — `CreateUser`
- `pkg/admin/service/user.go:95` — `CreateUser` logic + `IsCreateByAdmin` flag
- `pkg/admin/handler/user.go:50` — `CreateUserSocial`
- `pkg/admin/service/user.go:61` — `CreateUserSocial` logic
- `pkg/admin/handler/content.go:414` — `ImportContent`
- `pkg/admin/service/content.go:ImportContent` — bulk import logic
- `internal/model/mg/content_import_tracking.go` — tracking schema
- `pkg/public/service/schedule.go` — async update tracking khi crawl xong
- `internal/model/mg/user.go:UserRaw.IsCreateByAdmin` — flag phân biệt

**vCreator (target — chưa có)**:
- KHÔNG có admin user create flow
- KHÔNG có admin user social create
- KHÔNG có content import + tracking
- Chỉ có `CreateUserContractManually` — concept khác (tạo contract cho user đã tồn tại)

**Ambassador (cần verify scope khi port)**:
- Có `Create` user admin nhưng cho mục đích "referral seed" — không phải proxy creator
- Cần đổi naming convention khi port flow mới

## Lịch sử phân loại

- **2026-05-07 (gap #13 cũ)**: Thuộc gap #13 "Content moderation tools" — title misleading vì gộp 5 features khác nhau
- **2026-05-07 (split lần 1)**: Tách thành gap #31 với title "Bulk content import" — nghĩ chỉ là tool import bulk content
- **2026-05-07 (rescope)**: User clarify: *"TCB cho phép tạo creator dưới danh nghĩa admin, sau đó mới là import content của họ vào hệ thống giúp họ"* → scope thực tế là **flow 3 bước "admin proxy creator"** (tạo user → link social → import content), không phải chỉ import content
- **Verify 3 sản phẩm**: TCB có đủ 3 modules, vCreator KHÔNG có gì, Ambassador có CreateUser khác mục đích (referral seed)
- **Direction port**: TCB → vCr/Amb (selective theo business need)
- **Liên quan gap #14 "TCB ContentImportTracking"**: đã merge vì cùng concept

### Bài học methodology

- Initial split chỉ nhìn vào "ContentImportTracking" model → miss flow upstream `CreateUser` + `CreateUserSocial`
- User clarify mới hiện ra picture đầy đủ — đây là feature **end-to-end** không phải single endpoint
- Khi mô tả gap, cần map ra **business flow** (use case journey), không chỉ list endpoints rời rạc
