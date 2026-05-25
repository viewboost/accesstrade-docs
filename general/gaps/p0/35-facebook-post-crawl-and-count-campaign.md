# Gap #35 — Hỗ trợ crawl Facebook Post + campaign tính tiền theo số bài post (TCB yêu cầu làm ngay)

> **Priority**: 🔴 **P0** (initial 2026-05-10 — TCB đang yêu cầu làm ngay)
> **Source**: User self-listed gap
> **Direction port**: Ambassador → TCB (urgent) + Ambassador → vCreator
> **Last verified**: 2026-05-10

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

**Facebook Post** = bài đăng dạng **text/image** trên Facebook (KHÔNG phải video/reel).

Cần 2 capability:
1. **Crawl bài post**: lấy được URL post + đọc được số liệu (views/reactions/comments) để tracking
2. **Campaign tính tiền theo số bài post**: brand chốt "creator post X bài → trả Y tiền" thay vì "đạt X view → trả Y" (tiêu chí đơn giản hơn cho campaign nội bộ B2B)

Ambassador đã có cả 2:
- Có regex parse URL Facebook Post (text/image, không phải video) + Facebook Profile
- Có constant `SourceFacebookPost = "facebook_post"` + content source `ContentSourceFacebookPost`
- Tracking trong `Statistic.FacebookPost` + analytics
- Tận dụng schema **`EventSchemaMilestone.NumberOfContent`** **đã sẵn 3 sản phẩm** để tính campaign theo số bài post (chứ không phải theo view)

TCB và vCreator **chỉ có Facebook video/reel** (regex `RegexFacebook`, `RegexFacebookReel`) — **không có** regex post, không có constant `facebook_post` → không track được bài post text/image.

→ TCB đang có khách hàng yêu cầu campaign Facebook Post → **cần làm ngay**.

## Bảng so sánh

| Khía cạnh | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| Schema `EventSchemaMilestone.NumberOfContent` (đếm số bài) | ✅ | ✅ | ✅ |
| Regex Facebook Video (`RegexFacebook`) | ✅ | ✅ | ✅ |
| Regex Facebook Reel (`RegexFacebookReel`) | ✅ | ✅ | ✅ |
| **Regex Facebook Post** (`RegexFacebookPost`) | ❌ | ❌ | ✅ |
| **Regex Facebook Profile** (`RegexFacebookProfile`) | ❌ | ❌ | ✅ |
| Constant `SourceFacebookPost` | ❌ | ❌ | ✅ |
| Content source `ContentSourceFacebookPost` | ❌ | ❌ | ✅ |
| Crawl Facebook Post (fetch metadata) | ❌ | ❌ | ✅ |
| Tracking `Statistic.FacebookPost` | ❌ | ❌ | ✅ |
| Analytics dashboard `FacebookPost` source | ❌ | ❌ | ✅ |

## Hệ quả

- **TCB**: khách hàng đang yêu cầu campaign Facebook Post → **đang block sales/delivery**. Phải làm ngay.
- **vCreator**: nếu khách hàng B2B brand muốn đếm bài post → không support → mất deal
- **Reward schema đã sẵn 3 sản phẩm**: gap chính KHÔNG phải reward engine, mà là **crawl + tracking infrastructure** cho Facebook Post

## Liên quan các gap khác

- **Gap #34 (Threads binding)**: cùng pattern (Ambassador đã có, TCB/vCr thiếu) — có thể làm chung wave với #34
- **Gap #2 (InfluencerProfile)**: gap #2 đã note "Ambassador có special channels (facebook_post, threads)" — gap #35 này là phần scope con cho Facebook Post (cùng family với #34 Threads)
- **Gap #17 (Avatar cache)**: nếu port profile binding → áp dụng cùng pattern cache MinIO

## Giải pháp

### Phase 1 (TCB urgent): ~1-2 tuần
1. Thêm constants:
   - `SourceFacebookPost = "facebook_post"`
   - `SourceFacebookProfile = "facebook_profile"`
   - `ContentSourceFacebookPost = "facebook_post"`
2. Mở rộng `internal/module/social/facebook/facebook.go`:
   - Thêm `RegexFacebookPost` (regex từ Ambassador, ~1 dòng dài)
   - Thêm `RegexFacebookProfile`
   - Validation function tách video/reel/post
3. Crawl client: thêm fetch Facebook Post metadata (Graph API)
4. Content tracking schema migration: thêm field `Statistic.FacebookPost`
5. Analytics: thêm source `FacebookPost` vào `event_analytic_daily` + dashboard breakdown
6. Test campaign type "đếm số bài post" (dùng `EventSchemaMilestone.NumberOfContent` đã sẵn)

### Phase 2 (vCreator): ~1 tuần
- Tương tự Phase 1 nhưng adapt với schema vCreator

**Total**: ~2-3 tuần (TCB urgent first, vCr theo sau).

## Tại sao P0

- **TCB đang yêu cầu làm ngay** — sales/delivery blocker
- **Effort không lớn**: chỉ cần copy regex + extend crawl client (~1-2 tuần)
- **Reward engine đã sẵn**: schema `EventSchemaMilestone.NumberOfContent` đã có 3 sản phẩm → KHÔNG cần build mới, chỉ cần wire data nguồn
- **Cross-product impact lớn**: cả vCr cũng cần để đa dạng hóa campaign type

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

Cả 3 sản phẩm đã có `EventSchemaMilestone.NumberOfContent` (đếm số bài post). Gap chính là **crawl infrastructure cho Facebook Post**: Ambassador có regex + constant + content source + tracking đầy đủ; TCB/vCr chỉ có Facebook video/reel, KHÔNG có post.

## Verify code

### Ambassador (source of truth)

**Constants** — `internal/constants/constants.go`:
```go
SourceFacebookProfile = "facebook_profile"  // line 187
SourceFacebookPost    = "facebook_post"     // line 193
```

**Content source** — `internal/constants/content.go:9, 32`:
```go
ContentSourceFacebookPost = "facebook_post"
// Allowed sources include facebook_post
```

**Module** — `internal/module/social/facebook/facebook.go` (177 LOC):
```go
const (
    RegexFacebook     = `...` // video URLs
    RegexFacebookReel = `...` // reel URLs
    RegexFacebookPost = `(?i)https?://(?:www\.|m\.|touch\.)?facebook\.com/` +
                        `(?:(?:groups/[^/]+/(?:permalink|posts)/)|` +
                        `(?:[^/]+/(?:posts|videos|reels)/)|` +
                        `(?:permalink\.php\?story_fbid=)|` +
                        `(?:photo\.php\?fbid=)|` +
                        `(?:photo/\?fbid=)|` +
                        `(?:share/p/))([0-9]+|pfbid[a-zA-Z0-9]+|[a-zA-Z0-9]+)`
    RegexFacebookProfile = `(?i)^https?://(?:www\.|m\.|touch\.)?facebook\.com/` +
                          `(?:profile\.php\?id=\d+|people/[^/]+/\d+|[a-zA-Z0-9.]{5,50})/?\??[^/]*$`
)
```

**Reward schema (đã sẵn)** — `internal/model/mg/event_schema.go:52-56`:
```go
type EventSchemaMilestone struct {
    NumberOfContent int64 `json:"numberOfContent,omitempty"` // ← đếm số bài
    NumberOfView    int64 `json:"numberOfView,omitempty"`
    MinimumOfView   int64 `json:"minimumOfView,omitempty"`
}
```

**Caller** — `internal/service/event_schema.go:839, 871`:
```go
if schema.Milestone == nil || schema.Milestone.NumberOfContent == 0 { ... }
if totalContent < schema.Milestone.NumberOfContent { ... } // chưa đủ số bài
```

**Tracking** — `internal/service/event_schema.go:529-530`:
```go
case constants.ContentSourceFacebookPost:
    viewTotal += userEvent.Statistic.FacebookPost.View.Completed
```

**Analytics** — `internal/service/event.go:377, 446-449, 570-574`:
```go
contentFacebookPostStats = aggregatepipeline.StatisticContentReportDailyBySource{}
// filter: i.Source == constants.ContentSourceFacebookPost
// EventAnalyticSource.FacebookPost = {TotalContent, TotalContentPending, ...}
```

### TCB status

**Constants** — `internal/constants/constants.go:181-184`:
```go
SourceFacebook  = "facebook"
SourceYoutube   = "youtube"
SourceInstagram = "instagram"
SourceTiktok    = "tiktok"
// ❌ KHÔNG có SourceFacebookPost, SourceFacebookProfile
```

**Module** — `internal/module/social/facebook/facebook.go` (157 LOC):
```go
RegexFacebook         // video
RegexFacebookReel     // reel
RegexFacebookPageUser // page (TCB-specific)
// ❌ KHÔNG có RegexFacebookPost, RegexFacebookProfile
```

**Schema reward** — `internal/model/mg/event_schema.go:33, 49, 52`:
```go
Milestone *EventSchemaMilestone  // ✅ ĐÃ CÓ
type EventSchemaMilestone struct {
    NumberOfContent ... // ✅ đếm số bài đã sẵn
}
```

→ Schema sẵn rồi. Chỉ thiếu crawl + content source.

### vCreator status

**Constants** — `internal/constants/constants.go:184-188`:
```go
SourceFacebook, SourceYoutube, SourceInstagram, SourceTiktok, SourceThreads
// ❌ KHÔNG có SourceFacebookPost, SourceFacebookProfile
```

**Module** — `internal/module/social/facebook/facebook.go` (122 LOC):
```go
RegexFacebook, RegexFacebookReel
// ❌ KHÔNG có RegexFacebookPost, RegexFacebookProfile, RegexFacebookPageUser
```

**Schema reward**: ✅ đã có `EventSchemaMilestone.NumberOfContent`.

## Đề xuất implementation

### Phase 1: TCB urgent (~1-2 tuần)
1. **Constants** (5 phút):
   ```go
   // internal/constants/constants.go
   SourceFacebookPost    = "facebook_post"
   SourceFacebookProfile = "facebook_profile"
   // internal/constants/content.go
   ContentSourceFacebookPost = "facebook_post"
   ```
2. **Module facebook regex** (~1-2 giờ):
   - Copy `RegexFacebookPost` + `RegexFacebookProfile` từ Ambassador
   - Thêm validation function `IsValidFacebookPost(url)`, `IsValidFacebookProfile(url)`
3. **Crawl client** (~3-5 ngày):
   - Mở rộng Facebook Graph API client để fetch Post metadata (text, image, reaction count)
   - Lưu ý: Facebook Graph API có rate limit + permission policy nghiêm — có thể cần workaround (scrape qua at-core hoặc external service)
4. **Content tracking schema** (~2-3 ngày):
   - Migration thêm field `Statistic.FacebookPost` vào `EventAnalyticDaily`, `UserEvent`
   - Wire `event_schema.go` switch-case `ContentSourceFacebookPost`
5. **Analytics dashboard** (~2-3 ngày):
   - Aggregate pipeline filter source `facebook_post`
   - Dashboard breakdown by source thêm `FacebookPost`
6. **Test E2E** (~1-2 ngày):
   - Tạo campaign milestone NumberOfContent = N → creator post N bài Facebook Post → trigger reward
   - Verify dashboard hiển thị đúng số bài

### Phase 2: vCreator (~1 tuần)
- Tương tự Phase 1 nhưng adapt với schema vCreator (có Threads, không có Page User)

**Total**: ~2-3 tuần.

## Risks + mitigations

1. **Facebook Graph API permission**: Facebook đã thắt chặt permission cho fetch post metadata không phải của owner — có thể cần app review từ Meta hoặc scrape qua external service
   - **Mitigation**: dùng pattern Ambassador (đã production), nếu Amb cũng workaround thì copy. Nếu cần app review, đăng ký TCB app sớm.
2. **Regex coverage**: Facebook URL formats nhiều variant (groups, photos, share, permalink, mobile) — regex của Ambassador rất phức tạp
   - **Mitigation**: copy nguyên si regex từ Amb, **không tự chế lại**.
3. **Migration data cũ**: TCB có thể có content cũ với source = `facebook` mà thực ra là post text → có thể cần re-classify
   - **Mitigation**: KHÔNG re-classify. Chỉ áp dụng cho content mới sau release.
4. **Campaign engine compatibility**: cần verify `EventSchemaMilestone.NumberOfContent` đếm đúng số bài (không bị nhầm với view milestone)
   - **Mitigation**: Ambassador đã production-tested, follow đúng pattern.

## Files referenced

**Ambassador (source of truth)**:
- `internal/constants/constants.go:187, 193` (SourceFacebookPost, SourceFacebookProfile)
- `internal/constants/content.go:9, 32` (ContentSourceFacebookPost)
- `internal/module/social/facebook/facebook.go` (177 LOC, có RegexFacebookPost + RegexFacebookProfile)
- `internal/model/mg/event_schema.go:52-56` (EventSchemaMilestone — đã sẵn 3 sản phẩm)
- `internal/service/event_schema.go:529-530, 839, 871` (caller switch source + check NumberOfContent)
- `internal/service/event.go:377, 446-449, 570-574` (analytics aggregate)
- `internal/model/mg/event_analytic_daily.go` (FacebookPost field)

**TCB (target — urgent)**:
- `internal/constants/constants.go` (THIẾU SourceFacebookPost, SourceFacebookProfile)
- `internal/module/social/facebook/facebook.go` 157 LOC (THIẾU RegexFacebookPost, RegexFacebookProfile)
- `internal/model/mg/event_schema.go` ✅ ĐÃ CÓ EventSchemaMilestone.NumberOfContent
- THIẾU tracking + analytics cho FacebookPost source

**vCreator (target — sau TCB)**:
- Tương tự TCB

## Lịch sử phân loại

- **2026-05-10 (initial P0)**: User self-listed gap. Quote: "TCB đang yêu cầu làm ngay" → P0 priority.
  - Reward schema (`EventSchemaMilestone.NumberOfContent`) đã sẵn 3 sản phẩm
  - Gap chính là crawl + tracking infrastructure cho Facebook Post
  - Ambassador có pattern production-ready, copy không tốn nhiều effort
