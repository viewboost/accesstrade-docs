# Gap #2 — Khái niệm "Influencer Profile" — Ambassador BẮT BUỘC port, vCreator ĐỀ XUẤT port (chia sẻ creator pool)

> **Priority**: 🔴 **P0** (reclassified P1→P0 2026-05-07 sau khi user clarify business intent)
> **Source**: [semantic-diff-user-auth.md](../../semantic-diff-user-auth.md), [semantic-diff-targeting-matching.md](../../semantic-diff-targeting-matching.md)
> **Direction port**:
> - **Ambassador**: 🔴 BẮT BUỘC port InfluencerProfile từ TCB (Option B confirmed)
> - **vCreator**: 🟡 ĐỀ XUẤT port (long-term: chia sẻ creator pool giữa 3 sản phẩm)
> **Last verified**: 2026-05-07 (3-product code reading + business intent clarify)

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

3 sản phẩm AccessTrade đều có khái niệm "creator profile" nhưng **được dùng cho 3 mục đích nghiệp vụ khác nhau hoàn toàn**:

### TCB: Influencer là **chủ thể nghiệp vụ chính**
- Creator đăng ký nền tảng → submit hồ sơ wizard (categories, audience, demographics)
- TCB gọi **at-core** để **enrich** profile (lấy followers, engagement rate, score, category từ Accesstrade ecosystem)
- Tạo `InfluencerProfileRaw` collection riêng — **đây là "thẻ căn cước influencer"**
- Brand portal có trang **"Profiles"** browse + filter creator theo tier (nano/micro/macro/mega), engagement, category, score
- **Yêu cầu profile được approved** trước khi creator tham gia campaign
- Có config tự động duyệt theo `PartnerInfluencerConfig` (min subscribers, min videos, min views, statusStaff)

### Ambassador: User-social là **kênh đăng bài** + có scaffolding influencer-profile nhưng **simplified**
- Mỗi `UserSocial` = 1 kênh user link (TikTok / Facebook / Threads / Shopee...)
- Để tham gia campaign, user phải **submit application** cho từng partner (`SubmitApplicationPartner`)
- Ambassador **không có collection** `InfluencerProfileRaw` — admin "Profiles" page đọc trực tiếp từ `user_social`
- Có endpoint webhook at-core nhưng **chỉ dùng để update Stats** trong UserSocial, KHÔNG lưu enrichment data riêng
- **Comment trong code**: *"Simplified vs TCB: No PartnerInfluencerConfig auto-approve check, No AT Core score data, No StatusStaff/StaffCode... This is enough for FE's profiles list & detail rendering"*
- Hỗ trợ **đa dạng kênh content nhất**: tiktok, youtube, youtube_shorts, facebook, facebook_reels, **facebook_post**, instagram, instagram_reels, threads, shopee
- **`facebook_post` và `threads` chỉ Ambassador có** trong constants (TCB và vCreator không có `facebook_post`)

### vCreator: User-social là **kênh đăng bài** đơn giản, không có khái niệm "influencer profile"
- `UserSocial` chỉ 11 fields (so với TCB 21, Ambassador 23) — chỉ đủ cho login flow
- Không có `Stats`, không có `Demographics`, không có ownership verification
- Không có collection `InfluencerProfileRaw`, không có folder `influencer*` trong code
- Không có gọi at-core enrichment
- User-social chỉ phục vụ flow "đăng bài content cho campaign"

## Bảng so sánh 3 sản phẩm (góc nhìn business)

| Khía cạnh | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| **Có khái niệm "Influencer Profile" (thẻ căn cước)** | ✅ Có (collection riêng) | ❌ Không | 🟡 Có scaffolding nhưng đọc từ user_social |
| **Wizard đăng ký profile (categories, audience, demographics)** | ✅ Có | ❌ Không | ❌ Không |
| **Gọi at-core để enrich score/handle/category** | ✅ Có (lưu enrichment data) | ❌ Không | 🟡 Có webhook nhưng chỉ update Stats |
| **Brand browse profiles theo tier/engagement/score** | ✅ Có (filter đầy đủ) | ❌ Không | 🟡 Có nhưng filter cơ bản (followers + engagement) |
| **Yêu cầu profile approved để tham gia campaign** | ✅ Có | ❌ Không | 🟡 Có application per-partner (`SubmitApplicationPartner`) |
| **Auto-approve config (`PartnerInfluencerConfig`)** | ✅ Có (min subs/videos/views/staff) | ❌ Không | ❌ Không |
| **User-social dùng để làm gì?** | Channel link + ownership verify | Channel đăng bài đơn giản | Channel đăng bài + Event/Partner approval matrix |
| **User-social có Stats (followers, engagement)** | ✅ Có (từ at-core) | ❌ Không | ✅ Có (từ at-core) |
| **User-social có ownership verification** | ✅ Có (oauth/hashtag) | ❌ Không | ✅ Có (giống TCB) |
| **User-social có per-event/per-partner approval** | ❌ Không | ❌ Không | ✅ Có (denormalized) |
| **Số kênh content hỗ trợ** | 8 platforms | 8 platforms | **10 platforms** (thêm `facebook_post`) |
| **Đa kênh đặc thù** | — | — | `facebook_post`, `threads` có flow scrape riêng |
| **LOC influencer-related** | ~3800 | 0 | ~1000 |

## Hệ quả khi 3 sản phẩm khác nhau

1. **Brand không thể browse creator giống nhau** trên 3 platform — TCB có "Profiles" filter mạnh, vCreator không có gì, Ambassador filter cơ bản
2. **Creator không có "thẻ căn cước" thống nhất** — ở TCB là cá nhân (1 user 1 profile chính), ở Ambassador là per-partner application, ở vCreator chỉ là collection of channels
3. **Khó migrate creator giữa 3 platform** — data shape khác nhau, business logic khác nhau
4. **Không thể chia sẻ dashboard analytics** — TCB build dashboard dựa trên `InfluencerProfileRaw`, không port qua được vì 2 sản phẩm kia không có collection này

## Đề xuất giải pháp (góc nhìn business — đã chốt direction)

User confirm 2026-05-07: *"Cái này sẽ là P0. Ambassador sẽ bắt buộc sử dụng. VCreator thì sẽ khuyến khích sử dụng, sau này có cơ hội chia sẽ creator pool."*

→ Direction đã rõ:

### Phase 1 — Ambassador BẮT BUỘC port InfluencerProfile (P0, 2-3 tuần)

**Tại sao bắt buộc**:
- Ambassador đã có scaffolding `influencer-profile` nhưng đang đọc tạm từ `user_social` → tech debt
- 3 comment trong code đã ghi *"Simplified vs TCB... port later if needed"* → giờ là lúc port
- Brand portal Ambassador cần filter mạnh hơn (categories, score, tier) để duyệt creator hiệu quả
- Ambassador là sản phẩm chạy chính — cần feature parity với TCB ở khía cạnh quản lý creator

**Việc cần làm (Ambassador)**:
- Tạo collection `InfluencerProfileRaw` (giống TCB, có thể adapt 27 fields cho phù hợp business)
- Update enrichment webhook from at-core: dual-write Stats vào UserSocial + enrichment data vào InfluencerProfile
- Update admin profiles list đọc từ `InfluencerProfile` (thay vì `UserSocial` như hiện tại)
- **GIỮ NGUYÊN** flow per-partner application (`SubmitApplicationPartner`) + special channels (`facebook_post`, `threads`) — đây là Ambassador-specific
- Auto-approve config (`PartnerInfluencerConfig`): cân nhắc port nếu có demand "tự động duyệt creator theo tiêu chí"

### Phase 2 — vCreator ĐỀ XUẤT port (P0, ~1 tháng — sau Ambassador hoàn tất)

**Tại sao đề xuất (không bắt buộc ngay)**:
- vCreator hiện tại là B2B workplace — creator được duyệt qua HR registry, không cần brand browse
- **Nhưng**: business intent là **chia sẻ creator pool 3 sản phẩm trong tương lai** → vCreator cần data shape tương thích với TCB/Ambassador
- Nếu không port sớm, mỗi creator có 3 profile rời rạc (TCB + Ambassador + vCreator) → khó merge sau

**Việc cần làm (vCreator)**:
- Tạo collection `InfluencerProfileRaw` (cùng schema TCB/Ambassador)
- Wizard onboarding cho creator vCreator submit profile (categories, demographics)
- Gọi at-core enrichment (cùng cơ chế TCB/Ambassador)
- **GIỮ NGUYÊN** workplace 3-tier + HR registry match (B2B-specific) — chỉ thêm InfluencerProfile bên cạnh
- Long-term: build brand portal browse creator (cho phép TCB/Ambassador brand browse creator vCreator)

### Phase 3 — Long-term: Shared creator pool (sau khi 3 sản phẩm đều có InfluencerProfile)

**Vision**:
- 1 creator có 1 `InfluencerProfile` thống nhất across 3 sản phẩm
- Brand TCB có thể browse creator Ambassador / vCreator (và ngược lại)
- Single source of truth cho enrichment data từ at-core
- Có thể migrate creator giữa 3 sản phẩm dễ dàng

**Effort long-term**: cần unification layer (vd: `at-core` proxy quản lý chung profile) — sẽ là 1 task lớn riêng (>2 tháng), không nằm trong scope gap này.

## Cần product/business confirm trước khi triển khai

1. **Ambassador**: schema InfluencerProfile có cần adapt gì không, hay copy y nguyên TCB? (vd: bỏ `StatusStaff`/`StaffCode` vì Ambassador không có concept staff)
2. **Ambassador per-partner application**: có conflict với khái niệm "1 user 1 profile" không? Đề xuất: giữ song song — InfluencerProfile cho enrichment data + applicaton flow cho partner approval
3. **vCreator timing**: làm song song Ambassador hay sau? (đề xuất: sau, để học từ migration Ambassador)
4. **Auto-approve config (`PartnerInfluencerConfig`)**: chỉ port khi có demand, hay port luôn để có feature parity?
5. **Migration data Ambassador**: existing user_social records có cần migrate sang InfluencerProfile không, hay chỉ apply cho creator mới?

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR (sau verify 3-product code reading)

Initial gap-analysis nói "Ambassador chưa có auto-approve influencer + notification" — chỉ đúng **1 phần nhỏ** của gap thật.

**Gap thật là kiến trúc**: 3 sản phẩm có 3 mental model khác nhau cho "creator":
- TCB: `User + InfluencerProfile + UserSocial` (3-tier)
- Ambassador: `User + UserSocial(với approval matrix)` (2-tier, scaffolding influencer-profile rỗng)
- vCreator: `User + UserSocial(minimal)` (2-tier, chỉ login + post content)

## Verify 5-layer

### Layer 1: Code tồn tại

| Component | TCB | vCreator | Ambassador |
|---|---|---|---|
| Model `InfluencerProfileRaw` | ✅ 56 LOC | ❌ | ❌ (model không có nhưng có folder) |
| Model `PartnerInfluencerConfigRaw` | ✅ | ❌ | ❌ |
| Service `pkg/public/service/influencer_profile.go` | ✅ | ❌ | ✅ (simplified) |
| Service `pkg/public/service/social_profile.go` (FB scrape) | ✅ | ❌ | ✅ (simplified) |
| Handler `pkg/public/handler/influencer_profile.go` | ✅ webhook at-core | ❌ | ✅ webhook at-core (simplified) |
| Admin handler/service `influencer_profiles.go` | ✅ filter mạnh | ❌ | ✅ filter cơ bản |
| Function `CheckUserSocialWithConfig` (auto-approve) | ✅ trong `internal/service/influencer.go` | ❌ | ❌ |
| Function `SubmitApplicationPartner` | ❌ | ❌ | ✅ Ambassador-only |
| Constants `ContentSourceFacebookPost` | ❌ | ❌ | ✅ Ambassador-only |
| Constants `ContentSourceThreads` | ✅ | ✅ | ✅ |
| **Total LOC influencer-related** | **~3800** | **0** | **~1000** |

### Layer 2: Code được gọi

**TCB** — `InfluencerProfileRaw` được dùng ở:
- `pkg/public/service/influencer_profile.go:OnEnrichmentWebhook` — write enrichment data từ at-core
- `pkg/admin/service/influencer_profiles.go:GetProfileList` — brand portal list view với filter mạnh
- `pkg/admin/service/migration.go:2090:MigrationEnrichProfile` — bulk enrich
- `pkg/admin/service/campaign_matching.go:97:atcore.MatchingBatch` — campaign matching engine dùng profile data

**Ambassador** — không có model nhưng có scaffolding:
- `pkg/admin/service/influencer_profiles.go:135` — đọc trực tiếp từ `UserSocialDAO`, **không** từ `InfluencerProfileDAO` (vì DAO không tồn tại)
- `pkg/public/service/influencer_profile.go:OnEnrichmentWebhook` — chỉ update Stats trong UserSocial, **không** write `InfluencerProfileRaw`

**vCreator** — 0 references, 0 caller.

### Layer 3: Runtime DB

**TCB**: collection `influencer_profile` ghi data thật từ enrichment webhook.
**Ambassador**: KHÔNG có collection `influencer_profile` — admin profiles page query từ `user_social` collection.
**vCreator**: Không có concept.

### Layer 4: Business need ở target

User clarify (2026-05-07):
- *"Bên TCB mới có khái niệm influencer profile"*
- *"vCreator: user-social không được tính là influencer-profile, nó là kênh đăng bài, cách dùng hoàn toàn khác"*
- *"Ambassador có threads, facebook posts là 1 kiểu khác dựa trên user-social nữa"*

→ Confirm: 3 sản phẩm có 3 mental model khác nhau **theo design**, không phải bug "vCr/Amb chưa có ActorType".

### Layer 5: Direction port

**KHÔNG có direction port đơn giản**:
- TCB → Ambassador: Ambassador **đã có scaffolding** + comment "simplified vs TCB" → có thể port nhưng cần align với business model Ambassador (multi-partner)
- TCB → vCreator: vCreator KHÔNG có business case (B2B workplace, brand không browse creator)
- Ambassador special features (FacebookPost, Threads) → có thể port sang TCB nếu TCB cần mở rộng kênh content

## Diff models chi tiết

### `UserSocialRaw` (3-product diff)

| Field | TCB (21 fields) | vCreator (11 fields) | Ambassador (23 fields) |
|---|---|---|---|
| ID, User, Source, SearchString, Data, AccessToken, IsUseLogin, IsTokenExpired, Status, CreatedAt, UpdatedAt | ✅ | ✅ | ✅ |
| **Stats** (UserChannelStats) | ✅ | ❌ | ✅ |
| **Demographics** (UserSocialDemographics) | ✅ | ❌ | ✅ |
| **IsEnriched + AtCoreJobID + AtCoreStatus + AtCoreSyncedAt** | ✅ | ❌ | ✅ |
| **OwnershipStatus + OwnershipMethod + OwnershipAt** | ✅ | ❌ | ✅ |
| **IsPrimary** | ✅ | ❌ | ✅ |
| **EventApproval** (per-event approve denormalized) | ❌ | ❌ | ✅ |
| **PartnerApproval** (per-partner approve denormalized) | ❌ | ❌ | ✅ |

→ vCreator UserSocial là **minimal** (login only). TCB và Ambassador đều có Stats + Ownership + AtCore. Ambassador thêm 2 fields denormalized cho approval flow per-event/per-partner.

### `InfluencerProfileRaw` (TCB-only model, 27 fields)

```go
type InfluencerProfileRaw struct {
    ID, User, DisplayName
    Categories []string       // max 3
    SubCategories []string    // max 10
    ContentLanguage []string
    AudienceAge string         // "18-24" | "25-34" | etc
    DOB, Gender, City, Email
    UserSocial AppID            // link tới user_social primary
    ProfileId string            // at-core internal ID
    ScoreTotal float64
    ScoreCategory string
    Handle, Platform, AvatarUrl, Description, Country
    IsVerified bool
    ScoreHighlights []string
    AvgViews, TotalViews, TotalLikes int64
    Tracking EnrichmentTracking  // enrichedAt, errorCode, errorMsg
    CreatedAt, UpdatedAt
}
```

→ Đây là "thẻ căn cước" full-fledged. Ambassador KHÔNG có struct tương đương trong models.

### `PartnerInfluencerConfigRaw` (TCB-only)

Config auto-approve influencer per partner:
- `MinSubscribe, MinVideo, MinView` — gate quantitative
- `StatusStaffRequired` — gate qualitative (creator phải là staff đã verified)
- Engine `CheckUserSocialWithConfig` re-evaluate khi config thay đổi

## Smoking guns trong code

### 1. Ambassador `pkg/public/service/influencer_profile.go:20-24`
```go
// This is a simplified version of TCB's. Differences:
//   - No InfluencerProfileRaw collection (TCB uses it to store score/handle/categories
//     for ranking; ambassador only needs Stats updates on user-socials).
//   - No TrackingRequestWebhookRaw audit log (uses console logging instead).
//   - No RecoverStaleEnrichments cron (port later if needed).
```

### 2. Ambassador `pkg/admin/service/influencer_profiles.go:21-27`
```go
// Simplified vs TCB:
//   - No PartnerInfluencerConfig auto-approve check
//   - No AT Core score data on the response (kept fields nullable)
//   - No StatusStaff / StaffCode (no UserPartnerRaw lookup)
//   - No SubCategories / ContentLanguage
//   - Tier / EngagementTier filter use simple followers/engagement ranges
```

### 3. Ambassador `pkg/public/service/social_profile.go:22-30`
```go
// Simplified vs TCB:
//   - No TrackingRequestWebhookRaw audit log.
//   - No PartnerInfluencerConfig auto-approve check (uses StatusPending only).
//   - No SendNotificationInfluencerChangeStatus.
//   - No updateInfluencerProfileEnrichment (no InfluencerProfileRaw collection).
```

→ Ambassador developer **đã có ý thức** Ambassador là phiên bản simplified, không phải bug.

## Action items (sau khi user chốt direction 2026-05-07)

### Phase 1 — Ambassador port (BẮT BUỘC, P0, 2-3 tuần)
1. ✅ **Document khái niệm** (file này + memory)
2. **Schema design meeting** (1 ngày): adapt `InfluencerProfileRaw` cho Ambassador (bỏ StaffStatus, giữ core fields)
3. **Tạo model + DAO** `InfluencerProfileRaw` ở Ambassador
4. **Update enrichment webhook** `pkg/public/service/influencer_profile.go`:
   - Dual-write: Stats → UserSocial, enrichment data → InfluencerProfile
   - Bỏ comment "No InfluencerProfileRaw collection"
5. **Update admin profiles list** `pkg/admin/service/influencer_profiles.go`:
   - Đọc từ `InfluencerProfileDAO` thay vì `UserSocialDAO`
   - Bỏ comment "Simplified vs TCB"
6. **Migration script**: tạo InfluencerProfile records cho existing UserSocial (nếu có demand)
7. **Test regression**: per-partner application flow + special channels (facebook_post, threads) không break

### Phase 2 — vCreator port (ĐỀ XUẤT, P0, ~1 tháng — sau Ambassador)
8. **Wizard onboarding UI** cho creator vCreator submit profile
9. **Tạo model + DAO** `InfluencerProfileRaw` ở vCreator (cùng schema)
10. **Setup at-core enrichment** flow (vCreator chưa có module atcore)
11. **Public API** + **admin profiles page** giống Ambassador
12. **Long-term**: brand portal browse creator (cho phép cross-product browse)

### Phase 3 — Shared creator pool (long-term, scope riêng)
13. Strategic meeting về unification layer (`at-core` proxy chung?)
14. Migration plan để merge profile records của cùng 1 creator across 3 sản phẩm

## Effort estimate

| Phase | Action | Effort |
|---|---|---|
| 0 | Document khái niệm (file này) | 0.5 ngày ✅ |
| 1 | **Ambassador port (P0 BẮT BUỘC)** | **2-3 tuần** |
| 2 | **vCreator port (P0 ĐỀ XUẤT)** | **~1 tháng** |
| 3 | Shared creator pool (long-term) | >2 tháng (scope riêng) |
| | **Tổng Phase 1+2 cho gap này** | **~6-8 tuần** |

## Lịch sử phân loại

### Lần 1 — Initial (2026-05-07): TITLE SAI HOÀN TOÀN
- Title cũ: "Ambassador chưa có auto-approve influencer + notification (TCB → Ambassador)"
- Score: P1 (14)
- Sai vì: chỉ thấy 1 dòng comment "not yet ported" trong code Ambassador → đoán đây là gap đơn giản port từ TCB. Bỏ qua **toàn bộ kiến trúc khác nhau** giữa 3 sản phẩm.

### Lần 2 — User clarify scope (2026-05-07): RESCOPE GAP
User: *"Bên TCB mới có khái niệm influencer profile. Mặc dù 2 bên kia cũng có user-social nhưng cách làm việc nó khác... Ambassador có threads, facebook posts là 1 kiểu khác dựa trên user-social nữa."*

→ Verify code 3 sản phẩm:
- TCB có collection `InfluencerProfileRaw` riêng (27 fields)
- Ambassador có scaffolding `influencer-profile` nhưng KHÔNG có model — admin service đọc từ `user_social`
- vCreator KHÔNG có gì
- Ambassador hỗ trợ thêm 2 platform unique: `facebook_post` + `threads` flow scrape riêng
- 3 comment trong code Ambassador nói rõ "Simplified vs TCB"

→ **Rescope**: title đổi từ "auto-approve influencer" thành "Khái niệm Influencer Profile 3 cách triển khai khác".

### Lần 3 — User clarify business intent (2026-05-07): RECLASSIFY P1 → P0
User: *"Cái này sẽ là P0. Ambassador sẽ bắt buộc sử dụng. VCreator thì sẽ khuyến khích sử dụng, sau này có cơ hội chia sẽ creator pool."*

→ Direction port đã rõ:
- Ambassador: BẮT BUỘC (Option B confirmed) — 2-3 tuần
- vCreator: ĐỀ XUẤT — ~1 tháng (long-term: chia sẻ creator pool)
- Bỏ Option A (giữ nguyên hiện trạng) khỏi consideration

→ Reclassify từ P1 (Total 14) lên **P0** vì có business intent rõ ràng + roadmap unification creator pool.

### Bài học methodology
1. **Comment "not yet ported"** trong code KHÔNG luôn nghĩa là gap nhỏ port qua. Có thể là **simplified-by-design** với business model khác nhau.
2. **Cần đếm LOC** + **đọc cả admin service + public service** trước khi conclude. TCB ~3800 LOC influencer vs Ambassador ~1000 LOC — chênh lệch quá lớn để gọi là "1 feature port qua".
3. **Hỏi user** về business intent trước khi suggest port. User confirm "3 cách dùng khác nhau" → priority có thể reclassify.
4. **Business intent quyết định priority**: Cùng 1 gap, score "tech impact" có thể không đổi (vẫn 14) — nhưng **roadmap business** (creator pool unification) làm gap quan trọng → reclassify P0. Đây là **layer 5** trong methodology (business intent ở target).

## Files referenced

**TCB (full influencer system, ~3800 LOC)**:
- `internal/model/mg/influencer_profile.go` (56 LOC)
- `internal/model/mg/partner_influencer_config.go`
- `internal/service/influencer.go` (332 LOC, 13 fns)
- `pkg/public/service/influencer_profile.go` — webhook at-core
- `pkg/public/service/social_profile.go` — Facebook scrape callback
- `pkg/admin/service/influencer_profiles.go` — filter mạnh (tier, engagement, score, category)
- `pkg/admin/service/campaign_matching.go:97` — atcore.MatchingBatch dùng profile data
- `pkg/admin/service/migration.go:2090` — MigrationEnrichProfile bulk

**Ambassador (simplified scaffolding, ~1000 LOC)**:
- `pkg/public/service/influencer_profile.go:20-24` — comment "simplified vs TCB"
- `pkg/public/service/social_profile.go:22-30` — comment "simplified vs TCB"
- `pkg/admin/service/influencer_profiles.go:21-27` — comment "simplified vs TCB"
- `pkg/admin/service/influencer_profiles.go:135` — đọc từ UserSocialDAO (không phải InfluencerProfileDAO)
- `pkg/public/service/user.go:2902:SubmitApplicationPartner` — flow application per-partner Ambassador-only
- `internal/constants/content.go:9:ContentSourceFacebookPost` — Ambassador-only
- `internal/module/social/threads/` — scrape Threads profile + post

**vCreator (0 LOC influencer-related)**:
- `internal/model/mg/user_social.go` — 11 fields minimal
- KHÔNG có influencer*.go files

## Liên quan đến gap khác

- **Gap #20** (Ambassador Affiliate suite): Ambassador có business model multi-partner affiliate → giải thích lý do có `SubmitApplicationPartner` flow riêng
- **Gap #28** (Multi-tenant Partner): 3 sản phẩm có 3 mental model partner — tied chặt với gap này
- **Gap #16** (Profile Review + Rating): TCB có review system phụ thuộc vào InfluencerProfile collection → port review system sẽ blocked nếu chưa có InfluencerProfile ở vCr/Amb
