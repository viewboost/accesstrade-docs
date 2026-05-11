# Tech Spec — Tracking Facebook Post cho TCB

> Port từ Ambassador (`viewboost`) sang TCB. Phạm vi: **chỉ tracking + analytics breakdown**, không reward.

**Ngày:** 11/05/2026
**Trạng thái:** Đề xuất
**Đối tượng:** Dev TCB backend (Go)
**Overview:** [`overview.md`](./overview.md)
**Source of truth:** `accesstrade-projects/ambassabor/backend/` (Ambassador production)

---

## ⚠️ 0. Khác biệt TCB ↔ Ambassador — đọc TRƯỚC khi code

Đợt rà soát 10/05/2026 phát hiện **10 điểm khác biệt** giữa 2 codebase mà ảnh hưởng trực tiếp tới implementation. **KHÔNG copy mù** từ Ambassador. Mỗi điểm dưới đây có quyết định chính thức cho TCB:

### 0.1 — `UserSocialId` BẮT BUỘC ở TCB (Ambassador optional)

[`pkg/public/model/request/content.go:30-32`](accesstrade-projects/techcombank/backend/pkg/public/model/request/content.go#L30-L32) (TCB) bắt buộc `UserSocialId != ""` ngay tại validation. Ambassador không có check này.

**Quyết định:** Giữ pattern TCB. **Creator BẮT BUỘC link tài khoản Facebook (`UserSocial` source `facebook`) trước khi submit Facebook Post.** UI cần guard nút submit nếu chưa link.

**Implication tech-spec:**
- Trong case `ContentSourceFacebookPost` (section 4.7), `body.UserSocialId` luôn != "" → bỏ `if body.UserSocialId != ""` wrap quanh verify `authorId`.
- Validation request thêm `ContentSourceFacebookPost` vào allowed source list (đã có).
- **Bonus:** Có sẵn `UserSocialPartner` approved check ở đầu hàm — FB Post inherit miễn phí.

### 0.2 — TCB có `UserSocialPartner` (Amb không có)

TCB có concept `UserSocialPartner` (mapping userSocial ↔ partner với status `approved/pending/rejected`). [`content.go:159-170`](accesstrade-projects/techcombank/backend/pkg/public/service/content.go#L159-L170) check `userSocialPartner.Status == StatusApproved` trước khi cho submit. Amb không có.

**Quyết định:** Giữ pattern TCB. FB Post submit cần `UserSocialPartner` đã approved giống video/reel. Block verify này nằm **ở đầu hàm**, FB Post case **không cần copy lại**.

### 0.3 — `GetData` vs `GetDataCore` (2 endpoint khác nhau)

TCB content-catcher có **2 endpoint riêng biệt**:

- `GetData` → URL `config.ContentCatcher.BaseURL` (legacy, dùng cho Instagram, Tiktok)
- `GetDataCore` → URL `config.CoreContentCatcher.BaseURL` (mới, có HTTP tracking metadata, dùng cho Youtube, Facebook video/reel, Tiktok khi flag bật)

Switch giữa 2 endpoint qua config flag `IsCoreContentCatcher.<source>` (e.g. `IsCoreContentCatcher.Youtube`, `IsCoreContentCatcher.Facebook`).

**Quyết định:** FB Post dùng **`GetDataCore`** + thêm config flag `IsCoreContentCatcher.FacebookPost`. Lý do: consistent với FB video/reel hiện tại; có tracking; có thể fallback `GetData` qua config nếu Core service chưa support source `facebook_post`.

**Prerequisite:** Confirm với team content-catcher rằng **CoreContentCatcher** (chứ không phải legacy ContentCatcher) đã support `source=facebook_post`.

### 0.4 — `InsertTrackingRequestCrawl` async (Amb không có)

Mỗi lần gọi `GetDataCore`, TCB ghi log request qua `InsertTrackingRequestCrawl` async để debug + analytics performance content-catcher.

**Quyết định:** FB Post case phải gọi `go internalservice.InsertTrackingRequestCrawl(ctx, payload, res, nil)` sau `GetDataCore`. Pattern giống FB video/reel.

### 0.5 — `PublishAt` enforce trong khoảng event (Amb đã comment out)

TCB enforce `PublishAt` phải trong `[event.StartAt, event.EndAt]`, fail thì reject. Ambassador comment out check này.

**Quyết định (user xác nhận):** **Enforce** cho FB Post — giống video/reel TCB. Bài đăng trước event start hoặc sau event end sẽ bị reject với `ContentKeyPublishAtInvalid`.

**Risk:** Creator có bài cũ trên Facebook muốn dùng cho thử thách mới → bị reject. Cần thông báo rõ qua UI.

### 0.6 — OpsHub moderation (TCB đã có client đầy đủ, chỉ wire)

TCB đã có:

- **OpsHub client + helper sẵn sàng** ở [`internal/module/opshub/`](accesstrade-projects/techcombank/backend/internal/module/opshub/) (`client.go`, `helper.go`, `model.go`, `webhook_model.go`, `init.go`)
- Hàm `opshub.SendVideoForContent(ctx, content, opts)` đã được gọi trong public content create flow ([`content.go:369-377`](accesstrade-projects/techcombank/backend/pkg/public/service/content.go#L369-L377)) khi `event.Options.IsEnableOpsHub = true`
- Hàm này truyền **`content.Source` lên OpsHub trong field `Data.Source`** — tức là khi `source = facebook_post`, OpsHub sẽ nhận đúng giá trị này
- Shape `VideoData` đã có sẵn các field FB Post cần: `Source`, `ContentID`, `Link`, `Desc`, `Like`, `Comment`, `Share`, `PublishAt`, `Author`, `Cover`, `Title`
- Có tag system seed sẵn cho moderation suggestion: `OpsHubAutoApproved`, `OpsHubAutoRejected`, `OpsHubApproved`, `OpsHubRejected`, `OpsHubRequestEdit`, `OpsHubSLAViolated`
- Có webhook handler nhận kết quả moderation từ OpsHub

Ambassador có pattern gần giống nhưng helper khác (`opshub.SendVideoForContent` + struct `SendVideoOpts` shape khác đôi chút).

**Quyết định (user xác nhận):** **Bài Facebook Post sẽ chảy qua OpsHub** y hệt video/reel:

- FB Post sau khi crawl + save → tự động gửi qua OpsHub nếu `event.Options.IsEnableOpsHub = true`
- Side effect tự nhiên vì FB Post case chỉ thêm vào switch, đoạn `// Send to OpsHub if enabled` ở dưới switch đã handle async — **không cần code mới cho TCB backend**
- Mapping fields:
  - `content.Source = "facebook_post"` (FB Post không có `Duration`, sẽ truyền 0)
  - `content.View = 0` (FB Post không có view)
  - `content.Like / Comment / Share` → từ content-catcher
  - `content.Cover` → ảnh đính kèm đầu tiên (đã upload MinIO ở image upload block trước đó)

**⚠️ Prerequisite phía OpsHub service:**

1. **OpsHub có support `source = facebook_post` không?** Field `Data.Source` là string tự do — OpsHub có thể đã accept any source. Nhưng UI review của OpsHub có hiển thị FB Post text/ảnh đúng không (vs video player cho video)? **Verify với team OpsHub trước khi release**.
2. **Moderation rule cho FB Post**: brand thường review video bằng cách xem video; FB Post text cần review nội dung text + ảnh. Logic SLA + auto-suggest có giữ nguyên không? Có thể OpsHub cần extend UI cho FB Post.

**Risk mitigation:** Nếu OpsHub chưa support FB Post hoàn chỉnh, có thể **tạm thời skip OpsHub cho FB Post** bằng cách thêm filter:

```go
// Trong content.go sau switch:
if event.Options != nil && event.Options.IsEnableOpsHub &&
   b.Source != constants.ContentSourceFacebookPost {  // tạm skip FB Post
    opsHubResult, err := opshub.SendVideoForContent(...)
}
```

Sau khi OpsHub xong UI cho FB Post → bỏ filter này (revert lại như video/reel).

### 0.7 — `dataDefault` fallback khi crawl tắt

TCB có pattern `if !config.GetENV().Facebook.IsEnable { contentInfo = dataDefault }` (Instagram, FB video khi tắt crawl → vẫn cho submit với placeholder data). Ambassador không dùng.

**Quyết định:** **Không dùng** `dataDefault` cho FB Post. FB Post bắt buộc crawl thành công mới lưu, vì cần `contentInfo.AuthorId` để verify ownership. Nếu `Facebook.IsEnable = false` → reject submit FB Post.

### 0.8 — `TranscriptStatus` field — **TẮT với FB Post**

TCB `ContentRaw.TranscriptStatus` ([`content.go:57`](accesstrade-projects/techcombank/backend/internal/model/mg/content.go#L57)) là field để pipeline transcript audio→text cho video. 4 trạng thái: `pending`, `processing`, `completed`, `failed`. Hiện TCB set `TranscriptStatusPending` cho **mọi content** trong [`public/service/content.go:328`](accesstrade-projects/techcombank/backend/pkg/public/service/content.go#L328) — kể cả Facebook video/reel.

Có cron [`schedule.go:2607`](accesstrade-projects/techcombank/backend/pkg/public/service/schedule.go#L2607) query `transcriptStatus: Pending` để pick up content cần transcript → nếu FB Post cũng set Pending, cron sẽ thử transcript bài text/ảnh **vô nghĩa** (tốn tài nguyên + có thể gây error).

**Quyết định:** **TẮT transcript với FB Post**. Sửa đoạn `b.TranscriptStatus = constants.TranscriptStatusPending` thành:

```go
// Chỉ set transcript pending cho content có audio/video
if b.Source != constants.ContentSourceFacebookPost {
    b.TranscriptStatus = constants.TranscriptStatusPending
}
```

Hoặc sạch hơn — wrap trong helper:

```go
// internal/constants/content.go - thêm helper
func IsTranscriptableSource(source string) bool {
    return source != ContentSourceFacebookPost
    // future: cũng exclude threads, instagram_image, etc. nếu cần
}

// public/service/content.go:328
if constants.IsTranscriptableSource(b.Source) {
    b.TranscriptStatus = constants.TranscriptStatusPending
}
```

**Verify schedule cron:** trong query `bson.M{"transcriptStatus": Pending}`, có thể thêm explicit exclude FB Post để safe:

```go
{"transcriptStatus": constants.TranscriptStatusPending, "source": bson.M{"$ne": constants.ContentSourceFacebookPost}}
```

→ Phòng trường hợp data cũ bị set Pending nhầm. Không bắt buộc nhưng khuyến nghị.

### 0.9 — Locale keys khác nhau

| Mục đích | Ambassador | TCB |
|---|---|---|
| Link không hợp lệ | `ContentKeyLinkInvalid` | `ContentKeyLinkCanNotCrawler` |
| User social chưa link | `ContentKeyUserSocialNotLink` | `ContentKeyUserSocialNotLink` ✅ |
| Social partner chưa approved | — | `ContentKeyUserSocialNotApproved` |
| Author bài ≠ user social | `ContentKeyUserSocialNotMatch` | **cần thêm mới** |
| Phải truyền userSocialId | — | `ContentKeyUserSocialIdRequired` |

**Quyết định:** Dùng locale key của TCB. Cần thêm `ContentKeyUserSocialNotMatch` (cho Facebook Post + cho extend tương lai sang Threads, Instagram).

### 0.10 — Luồng đăng ký UserSocial source `facebook` khác hẳn

TCB và Amb có cơ chế khác hẳn cho `LinkUserSocial` source `facebook`:

| Khía cạnh | TCB | Ambassador |
|---|---|---|
| Lấy data FB | `GetUserInfoFromFacebook(token)` qua Graph API + OAuth token client-side | `contentcatcher.GetDataProfile({source: facebook_profile})` scrape |
| URL validation | `ValidateFacebookPageLinkOrPageUser` | `IsValidFacebookProfileURL` |
| Data lưu | `CommonFacebookGraphMeData` (có Token, ExpiredAt, Email, Gender) | `ProfileInfo` (Avatar, Follower, Desc, không có OAuth token) |
| Side effect | `CreateJobCrawlFacebookProfile` + `GenerateUserSocialPartner` | Không |

**Quyết định:** **KHÔNG đụng tới `LinkUserSocial`** trong đợt này. Tận dụng `UserSocial.Data.ID` có sẵn từ flow TCB hiện tại để verify `authorId == userSocial.Data.ID`. Không cần port `IsValidFacebookProfileURL`, `RegexFacebookProfile`, `SourceFacebookProfile`, `GetDataProfile`.

---

## 1. Nguyên tắc port

Tất cả thay đổi **copy logic** từ Ambassador, **nhưng adapt theo 10 khác biệt section 0**. Đừng tự chế lại regex, đừng cải tiến validation logic. Khi có conflict giữa pattern TCB hiện tại và pattern Amb, **ưu tiên TCB** cho các điểm đã liệt kê ở section 0.

**KHÔNG làm trong đợt này:**

- ❌ Field `FacebookPost` trong `UserEventStatistic` (struct phục vụ reward)
- ❌ Cộng vào `GetCashTotal()` / `GetPointTotal()`
- ❌ Switch-case `ContentSourceFacebookPost` trong `internal/service/event_schema.go` (milestone calculation)
- ❌ Wire vào `Milestone.NumberOfContent`
- ❌ Flow link Facebook profile của creator (`SourceFacebookProfile` + `GetDataProfile`) — đợt này không validate ownership bằng profile API; chỉ verify `authorId` nếu user đã link Facebook qua flow hiện hữu

**LÀM trong đợt này:**

- ✅ Constants + regex + validation function
- ✅ Content-catcher client field bổ sung (`Images`, `AuthorId`)
- ✅ Public API create content case `facebook_post`
- ✅ Admin re-crawl case `facebook_post`
- ✅ Admin import normalize/validate case (TCB-specific, Amb không có)
- ✅ Cron re-crawl định kỳ `CrawlDataContentFacebookPost`
- ✅ Analytics `EventAnalyticDailyStatistic.FacebookPost` + 4 chỗ extract trong `event.go`

---

## 2. Tech stack

| Khía cạnh | Giá trị |
|---|---|
| Language | Go 1.24+ |
| Framework | Echo (HTTP) |
| DB | MongoDB (collection `content`, `event_analytic_daily`) |
| External service | `content_catcher` (HTTP API, đã có sẵn trên TCB) |
| Cron | gocron via `pkg/public/schedule/schedule.go` |
| Object storage | MinIO (upload ảnh từ FB Post) |

---

## 3. File path mapping Amb → TCB

| # | Amb (source) | TCB (target) | Loại thay đổi |
|---|---|---|---|
| 1 | `internal/constants/constants.go` | `internal/constants/constants.go` | Thêm 1 const (`SourceFacebookPost`) |
| 2 | `internal/constants/content.go` | `internal/constants/content.go` | Thêm 1 const + 2 chỗ (display map + interface list) |
| 3 | `internal/module/social/facebook/facebook.go` | `internal/module/social/facebook/facebook.go` | Thêm 1 regex + 1 fn + fix shortlink resolver |
| 4 | `internal/module/social/content_catcher/model.go` | `internal/module/social/content_catcher/model.go` | Thêm 2 field `Images`, `AuthorId` vào `ContentInfo` |
| 5 | `internal/model/mg/event_analytic_daily.go` | `internal/model/mg/event_analytic_daily.go` | Thêm field `FacebookPost EventAnalyticSource` |
| 6 | `pkg/public/model/request/content.go` | `pkg/public/model/request/content.go` | Thêm 2 chỗ (allowed list + switch case) |
| 7 | `pkg/public/service/content.go` | `pkg/public/service/content.go` | Thêm case `ContentSourceFacebookPost` trong create flow |
| 8 | `pkg/admin/service/content.go` (re-crawl) | `pkg/admin/service/content.go` | Thêm case re-crawl + (TCB-specific) case normalize/validate import |
| 9 | `internal/service/event.go` | `internal/service/event.go` | 4 chỗ extract stats + 1 chỗ ghi vào struct analytics |
| 10 | `pkg/public/service/schedule.go` | `pkg/public/service/schedule.go` | Thêm `CrawlDataContentFacebookPost` + `processFacebookPostCrawl` |
| 11 | `pkg/public/schedule/schedule.go` | `pkg/public/schedule/schedule.go` | Đăng ký cron entry |
| 12 | `pkg/public/service/schedule.go` (interface) | `pkg/public/service/schedule.go` (interface) | Thêm method vào interface |
| 13 | `pkg/public/handler/schedule.go` | `pkg/public/handler/schedule.go` | Thêm handler `CrawlDataContentFacebookPost` (manual trigger) |
| 14 | `pkg/public/router/schedule.go` | `pkg/public/router/schedule.go` | Đăng ký route |

---

## 4. Changes chi tiết (copy nguyên văn Amb)

### 4.1 — `internal/constants/constants.go`

Amb định nghĩa `SourceFacebookPost` ngang hàng các source khác. TCB thêm vào block source hiện tại (sau `SourceTiktok`):

```go
SourceFacebookPost = "facebook_post"
```

**Bỏ qua trong đợt này:** `SourceFacebookProfile = "facebook_profile"` (Amb có nhưng chỉ dùng cho flow link FB profile của creator — TCB chưa làm flow này).

### 4.2 — `internal/constants/content.go`

Thêm const:

```go
ContentSourceFacebookPost = "facebook_post"
```

Thêm vào `ContentSourceDisplayName` map:

```go
ContentSourceFacebookPost: "Facebook Post",
```

Thêm vào `ContentSourceInterface` slice (sau `ContentSourceFacebookReels`):

```go
ContentSourceFacebookPost,
```

### 4.3 — `internal/module/social/facebook/facebook.go`

**Thêm regex** (copy nguyên văn từ Amb [facebook.go:20-29](accesstrade-projects/ambassabor/backend/internal/module/social/facebook/facebook.go#L20-L29) — không reformat):

```go
// RegexFacebookPost matches Facebook post URLs (text/image posts, not videos/reels):
// - facebook.com/{username}/posts/{post_id}
// - facebook.com/permalink.php?story_fbid=...
// - facebook.com/photo.php?fbid=...
// - facebook.com/photo/?fbid=...
// - facebook.com/{username}/photos/...
// - m.facebook.com/story.php?story_fbid=...
// - facebook.com/share/p/{id}
// - facebook.com/photo/?fbid=...&set=...
RegexFacebookPost = `(?i)https?://(?:www\.|m\.|touch\.)?facebook\.com/(?:(?:groups/[^/]+/(?:permalink|posts)/)|(?:[^/]+/(?:posts|videos|reels)/)|(?:permalink\.php\?story_fbid=)|(?:photo\.php\?fbid=)|(?:photo/\?fbid=)|(?:share/p/))([0-9]+|pfbid[a-zA-Z0-9]+|[a-zA-Z0-9]+)`
```

**Thêm validation function** ([facebook.go:144-154](accesstrade-projects/ambassabor/backend/internal/module/social/facebook/facebook.go#L144-L154)):

```go
// IsValidFacebookPostURL validates Facebook post URLs (text/image posts, not videos/reels)
func IsValidFacebookPostURL(url string) bool {
    facebookPostRegex := regexp.MustCompile(RegexFacebookPost)
    // Check original URL first without HTTP request
    if facebookPostRegex.MatchString(url) {
        return true
    }
    // If not matched, try to resolve short link
    resolvedURL := facebookGetURLByShortLink(url)
    return facebookPostRegex.MatchString(resolvedURL)
}
```

**Fix `facebookGetURLByShortLink`** — hiện tại TCB chỉ giữ `?v=...`:

```go
// Trước (TCB hiện tại - dòng 124-127):
if res.Request.URL.Query().Get("v") != "" {
    redirectEndpoint += fmt.Sprintf("?v=%s", res.Request.URL.Query().Get("v"))
}
```

Đổi sang (theo Amb [facebook.go:130-133](accesstrade-projects/ambassabor/backend/internal/module/social/facebook/facebook.go#L130-L133)):

```go
// Keep all query params if present
if res.Request.URL.RawQuery != "" {
    redirectEndpoint += fmt.Sprintf("?%s", res.Request.URL.RawQuery)
}
```

**⚠️ Rủi ro regression:** Đổi từ chỉ giữ `?v=...` sang giữ toàn bộ query string sẽ thay đổi URL trả về của `facebookGetURLByShortLink` cho cả Facebook video/reel. Phải test lại `IsValidFacebookURL` + `IsValidFacebookReelsURL` để chắc không break. Regex của video/reel match `watch?v=...` nên giữ thêm query khác (như `?mibextid=...`) không ảnh hưởng — nhưng phải verify bằng test.

**KHÔNG thêm trong đợt này:** `RegexFacebookProfile`, `IsValidFacebookProfileURL` (chỉ dùng cho flow link FB profile — out of scope).

### 4.4 — `internal/module/social/content_catcher/model.go`

Thêm 2 field vào `ContentInfo`:

```go
Images   []string `json:"images" bson:"images"`
AuthorId string   `json:"authorId" bson:"authorId"`
```

**Tại sao cần `AuthorId`:** verify chủ tài khoản nếu user đã link Facebook (so sánh `contentInfo.AuthorId` với `userSocial.Data.ID`).

**Tại sao cần `Images`:** Facebook Post có ảnh đính kèm, cần upload lên MinIO trước khi hiển thị (FB ảnh có expired URL).

**⚠️ Giữ nguyên** các field TCB-specific hiện có: `IsSwitchVendor`, `ChannelId`, `HTTPStatusCode`, `HTTPDurationMs`, `HTTPEndpoint`, `HTTPRawBody`. Không xoá.

### 4.5 — `internal/model/mg/event_analytic_daily.go`

Thêm 1 field vào `EventAnalyticDailyStatistic` (vị trí: sau `FacebookReel`):

```go
FacebookPost EventAnalyticSource `json:"facebookPost" bson:"facebookPost"`
```

**Backward compat:** field mới sẽ là zero-value cho document cũ — MongoDB không cần migration script.

### 4.6 — `pkg/public/model/request/content.go`

Trong `CreateContentBody.Validate()`:

**Giữ nguyên** check `UserSocialId` required ở đầu hàm (0.1) — FB Post inherit.

**Thêm vào allowed source list** (sau `ContentSourceInstagramReels`):

```go
constants.ContentSourceFacebookPost,
```

**Thêm switch case** (sau `ContentSourceFacebookReels`):

```go
case constants.ContentSourceFacebookPost:
    if !socialfacebook.IsValidFacebookPostURL(b.URL) {
        isNotMatchSource = true
        nameSocial = "Facebook Post"
    }
```

⚠️ **TCB validation pattern khác Amb**: TCB dùng cờ `isNotMatchSource = true` + `nameSocial` rồi return error chung ở cuối hàm. Không return error trực tiếp như Amb.

### 4.7 — `pkg/public/service/content.go`

**KHÔNG copy nguyên văn từ Amb.** Adapt theo 10 quyết định ở section 0:

- Dùng `GetDataCore` thay vì `GetData` (0.3)
- Gọi `InsertTrackingRequestCrawl` async (0.4)
- Bỏ block check `UserSocialId` (đã required ở validation + check ở đầu hàm — 0.1, 0.2)
- Không set `dataDefault` fallback khi `Facebook.IsEnable = false` (0.7)
- Không set `TranscriptStatus` (0.8)
- Dùng locale key TCB (0.9)
- Verify `authorId == userSocial.Data.ID` (block verify generic ở đầu hàm đã match `userSocial.Source = facebook` rồi)

Thêm case mới trong switch tạo content:

```go
case constants.ContentSourceFacebookPost:
    if !config.GetENV().Facebook.IsEnable {
        return errors.New(locale.ContentKeyLinkCanNotCrawler)
    }
    fbPayload := contentcatcher.GetDataRequest{
        Source: constants.SourceFacebookPost,
        URLs: []string{
            body.URL,
        },
        Action: constants.TrackingCrawlActionCrawlContent,
    }
    var res contentcatcher.GetDataResponse
    if config.GetENV().IsCoreContentCatcher.FacebookPost {
        res, _ = contentcatcher.Client().GetDataCore(ctx, fbPayload)
        go internalservice.InsertTrackingRequestCrawl(context.Background(), fbPayload, res, nil)
    } else {
        res, _ = contentcatcher.Client().GetData(ctx, fbPayload)
    }
    if len(res.Data.Data) == 0 {
        return errors.New(locale.ContentKeyLinkCanNotCrawler)
    }
    contentInfo = res.Data.Data[0]
    // userSocialId luôn != "" (validation đã require ở 0.1)
    // Block đầu hàm đã verify userSocial.ID != Zero + userSocialPartner approved
    // Ở đây chỉ cần verify authorId trùng với Facebook account đã link
    if contentInfo.AuthorId != userSocial.Data.ID {
        return errors.New(locale.ContentKeyUserSocialNotMatch)
    }
```

**Thêm config flag `IsCoreContentCatcher.FacebookPost`** vào `internal/config/`. Default `true` (dùng Core như video/reel) hoặc `false` (fallback legacy) tuỳ team content-catcher confirm.

**Sau switch case, các logic TCB hiện hữu vẫn áp dụng cho FB Post** (KHÔNG bypass):
- `PublishAt` check trong `[event.StartAt, event.EndAt]` (0.5) — FB Post enforce
- `CheckHashTag` nếu `config.IsCheckHashTag` bật — FB Post inherit
- `checkExists` (duplicate `contentId`) — FB Post inherit
- OpsHub `SendVideoForContent` async nếu `event.Options.IsEnableOpsHub` (0.6) — **verify OpsHub có support `facebook_post` content type chưa**, nếu chưa cần extend phía OpsHub trước

**Image upload (giữ pattern Amb)**: trong block sau switch, thêm:

```go
if b.Source == constants.ContentSourceFacebookPost && len(contentInfo.Images) > 0 {
    uploadedImageURL, err := internalservice.Content().UploadImagesFromURLs(ctx, contentInfo.Images[0])
    if err != nil {
        fmt.Println("Failed to upload image facebook post from URL:", err)
        b.Images = contentInfo.Images
    }
    if uploadedImageURL != "" {
        b.Images = []string{uploadedImageURL}
    }
}
```

**Verify trước khi code:** TCB có hàm `internalservice.Content().UploadImagesFromURLs` không. Nếu không có, port từ Amb (~30 LOC) hoặc dùng pattern MinIO upload hiện có.

**KHÔNG set `b.TranscriptStatus`** cho FB Post (0.8). Để zero value.

**Thêm vào image upload block** ([content.go:347-359](accesstrade-projects/ambassabor/backend/pkg/public/service/content.go#L347-L359)):

```go
if funk.Contains([]string{
    constants.ContentSourceThreads,
    constants.ContentSourceFacebookPost,  // thêm dòng này
}, b.Source) && len(contentInfo.Images) > 0 {
    uploadedImageURL, err := internalservice.Content().UploadImagesFromURLs(ctx, contentInfo.Images[0])
    // ... rest giống Amb
}
```

**⚠️ Verify trước khi code:** check TCB có hàm `internalservice.Content().UploadImagesFromURLs` không. Nếu TCB không có → cần port hàm này từ Amb hoặc thay bằng pattern upload MinIO hiện có của TCB.

**Locale keys cần có:**

- `ContentKeyLinkInvalid` — hiện đã có
- `ContentKeyUserSocialNotLink` — verify
- `ContentKeyUserSocialNotMatch` — verify
- Nếu thiếu → thêm vào `internal/locale/`

### 4.8 — `pkg/admin/service/content.go`

**(a) Case re-crawl** ([Amb content.go:847-848](accesstrade-projects/ambassabor/backend/pkg/admin/service/content.go#L847-L848)):

Trong switch `content.Source` của `CrawlContentInfoById`:

```go
case constants.ContentSourceFacebookPost:
    source = constants.SourceFacebookPost
```

**(b) TCB-specific — admin import normalize:**

TCB có flow `normalizeImportSource` (Amb không có). Khi creator được link với UserSocial source `facebook`, link import sẽ cần phân loại video / reel / post. Thêm vào switch (sau check `IsValidFacebookReelsURL`):

```go
case constants.SourceFacebook:
    item := ContentDataImport{
        Source: constants.ContentSourceFacebook,
        Link:   link,
    }
    if socialfacebook.IsValidFacebookReelsURL(link) {
        item.Source = constants.ContentSourceFacebookReels
    } else if socialfacebook.IsValidFacebookPostURL(link) {
        item.Source = constants.ContentSourceFacebookPost
    }
    res = append(res, item)
```

**(c) TCB-specific — admin import validate:**

Trong `validateImportSourceWithURL`:

```go
case constants.ContentSourceFacebookPost:
    if !socialfacebook.IsValidFacebookPostURL(link) {
        isNotMatch = true
        nameSocial = "Facebook Post"
    }
```

**⚠️ Thứ tự check quan trọng:** Reel trước, Post sau. Vì regex Post có alternative `/reels/` overlap với Reel — nhưng test bằng cách check Reel trước → nếu khớp Reel thì khớp luôn, không cần Post fallback. Verify bằng unit test.

### 4.9 — `internal/service/event.go`

Trong `UpdateAnalyticEventDaily`, thêm 3 chỗ:

**(a) Khai báo biến** ([Amb event.go:377](accesstrade-projects/ambassabor/backend/internal/service/event.go#L377)):

```go
contentFacebookPostStats = aggregatepipeline.StatisticContentReportDailyBySource{}
```

**(b) Extract stats trong goroutine** ([Amb event.go:445-450](accesstrade-projects/ambassabor/backend/internal/service/event.go#L445-L450)):

```go
facebookPostInterface := funk.Find(data, func(i aggregatepipeline.StatisticContentReportDailyBySource) bool {
    return i.Source == constants.ContentSourceFacebookPost
})
if facebookPostInterface != nil {
    contentFacebookPostStats = facebookPostInterface.(aggregatepipeline.StatisticContentReportDailyBySource)
}
```

**(c) Ghi vào struct analytics** ([Amb event.go:570-575](accesstrade-projects/ambassabor/backend/internal/service/event.go#L570-L575)):

```go
FacebookPost: modelmg.EventAnalyticSource{
    TotalContent:         contentFacebookPostStats.TotalContent,
    TotalContentPending:  contentFacebookPostStats.TotalContentPending,
    TotalContentRejected: contentFacebookPostStats.TotalContentRejected,
    TotalContentApproved: contentFacebookPostStats.TotalContentApproved,
},
```

**Lưu ý 4 chỗ extract:** Amb có 4 location dùng pattern này (`event.go:446, 687, 959, 1066`). Verify TCB có những hàm tương đương nào → thêm vào TẤT CẢ những nơi extract stats per source (thường là `UpdateAnalyticEventDaily`, các hàm report admin tương tự).

### 4.10 — `pkg/public/service/schedule.go`

**(a) Thêm guard variable** ([Amb schedule.go:513](accesstrade-projects/ambassabor/backend/pkg/public/service/schedule.go#L513)):

```go
isRunFacebookPostCrawl = false
```

**(b) Thêm method `CrawlDataContentFacebookPost`** (copy [Amb schedule.go:672-723](accesstrade-projects/ambassabor/backend/pkg/public/service/schedule.go#L672-L723)):

```go
func (s scheduleImpl) CrawlDataContentFacebookPost() {
    if !config.GetENV().Facebook.IsEnable {
        return
    }
    release := scheduleGuard(&isRunFacebookPostCrawl)
    if release == nil {
        return
    }
    defer release()

    fmt.Println(aurora.Green("[Facebook Post] Start run crawler " + time.Now().Format(util.FormatTimeExcel)))

    var (
        ctx          = context.Background()
        events       = make([]*modelmg.EventRaw, 0)
        missions     = make([]*modelmg.MissionRaw, 0)
        now          = time.Now()
        totalRequest = 0
    )

    _ = daomongodb.EventDAO().GetShare().Find(ctx, new(modelmg.EventRaw), bson.M{
        "status":  constants.StatusActive,
        "startAt": bson.M{"$lte": now},
        "endAt":   bson.M{"$gt": now},
    })(&events)

    _ = daomongodb.MissionDAO().GetShare().Find(ctx, new(modelmg.MissionRaw), bson.M{
        "status":  constants.StatusActive,
        "startAt": bson.M{"$lte": now},
        "endAt":   bson.M{"$gt": now},
        "type":    constants.MissionTypeByContentWithCrawl,
    })(&missions)

    if len(events) == 0 && len(missions) == 0 {
        return
    }

    for _, event := range events {
        count := s.processFacebookPostCrawl(ctx, bson.M{"event": event.ID}, "event", event.ID.Hex())
        totalRequest += count
    }

    for _, mission := range missions {
        count := s.processFacebookPostCrawl(ctx, bson.M{"mission": mission.ID}, "mission", mission.ID.Hex())
        totalRequest += count
    }

    fmt.Println(aurora.Green(fmt.Sprintf("[Facebook Post] Done run crawler with %d requests at %s", totalRequest, time.Now().Format(util.FormatTimeExcel))))
}
```

**(c) Thêm `processFacebookPostCrawl`** ([Amb schedule.go:725-790](accesstrade-projects/ambassabor/backend/pkg/public/service/schedule.go#L725-L790)):

```go
func (s scheduleImpl) processFacebookPostCrawl(ctx context.Context, additionalFilter bson.M, entityType string, entityID string) int {
    var (
        lastId       primitive.ObjectID
        totalRequest = 0
        cond         = bson.M{
            "status": bson.M{
                "$in": []string{
                    constants.StatusApproved,
                    constants.StatusWaitingApproved,
                },
            },
            "source": constants.ContentSourceFacebookPost,
        }
        q = &mgquery.CommonQuery{
            Limit: 10,
            SortInterface: bson.D{
                {Key: "_id", Value: 1},
            },
        }
    )

    for k, v := range additionalFilter {
        cond[k] = v
    }

    for {
        if !lastId.IsZero() {
            cond["_id"] = bson.M{"$gt": lastId}
        }

        var (
            contents = make([]*modelmg.ContentRaw, 0)
            urls     = make([]string, 0)
        )

        _ = daomongodb.ContentDAO().GetShare().Find(ctx, new(modelmg.ContentRaw), cond, q.GetFindOptsUsingPage())(&contents)
        if len(contents) == 0 {
            break
        }

        for _, content := range contents {
            urls = append(urls, content.Link)
        }

        requestId := util.GenerateRequestId()
        _, err := contentcatcher.Client().GetData(ctx, contentcatcher.GetDataRequest{
            Source:    constants.SourceFacebookPost,
            URLs:      urls,
            IsAsync:   true,
            RequestID: requestId,
        })

        if err != nil {
            fmt.Println("Error content-catcher.Client().GetData : ", err.Error())
            break
        }

        totalRequest++
        s.InsertContentCallback(ctx, urls, requestId)

        fmt.Println(aurora.Green(fmt.Sprintf("[Facebook Post] Sent %d posts for processing", len(contents))))
        lastId = contents[len(contents)-1].ID
    }

    fmt.Println(aurora.Green(fmt.Sprintf("[Facebook Post] Crawler success %s: %s", entityType, entityID)))
    return totalRequest
}
```

**(d) Thêm vào interface** (block service interface declaration):

```go
CrawlDataContentFacebookPost()
```

**⚠️ Verify:** TCB có `scheduleGuard`, `InsertContentCallback`, `MissionTypeByContentWithCrawl` không? Nếu TCB không có Mission flow → bỏ phần `missions`, chỉ làm cho `events`.

### 4.11 — `pkg/public/schedule/schedule.go`

Đăng ký cron (Amb chạy 10:15 AM + 10:15 PM mỗi ngày):

```go
c.AddFunc("0 15 10,22 * * *", service.Schedule().CrawlDataContentFacebookPost)
```

Khuyến nghị **lệch giờ** với cron `CrawlDataContentFacebook` hiện hữu (Amb dùng `0 0 10,22 * * *` = đúng giờ 10/22, và FB Post dùng `0 15 ...` = lệch 15 phút) để tránh nghẽn content-catcher.

### 4.12 — `pkg/public/handler/schedule.go` + `pkg/public/router/schedule.go`

Thêm handler manual trigger + route (theo pattern của `CrawlDataContentFacebook` hiện hữu):

```go
// handler/schedule.go
func (s scheduleImpl) CrawlDataContentFacebookPost(c echo.Context) error {
    go func() {
        sv := service.Schedule()
        sv.CrawlDataContentFacebookPost()
    }()
    return c.JSON(http.StatusOK, response.NewResponseOK())
}

// router/schedule.go
g.GET("/crawl-content-facebook-post", h.CrawlDataContentFacebookPost, v.ScheduleQuery)
```

---

## 5. Data flow (sequence)

### 5.1 — Creator submit Facebook Post

```
1. Creator paste URL bài post Facebook lên app
2. Frontend → POST /api/contents { url, source: "facebook_post", userSocialId? }
3. Backend validate URL bằng IsValidFacebookPostURL (regex + fallback shortlink resolve)
4. Backend gọi content_catcher.GetData({ source: "facebook_post", urls: [url] })
5. Content-catcher trả về ContentInfo { id, title, desc, images, like, comment, share, author, authorId, publishAt, ... }
6. (Nếu userSocialId != "") verify contentInfo.AuthorId == userSocial.Data.ID
7. Backend check duplicate (contentId trong collection content)
8. Upload Images[0] lên MinIO → b.Images
9. Save ContentRaw với source = "facebook_post"
10. Async: ContentFlow.CreateFlow (record initial stats), Event.UpdateAnalyticEventDaily
```

### 5.2 — Cron re-crawl định kỳ

```
1. Cron tick (10:15 AM / 10:15 PM)
2. CrawlDataContentFacebookPost lấy events + missions đang active
3. Với mỗi event/mission: processFacebookPostCrawl
4. Query content source=facebook_post, status in [approved, waitingApproved], page 10
5. Gửi batch URLs lên content_catcher (IsAsync=true, RequestID)
6. InsertContentCallback ghi nhận RequestID + URLs → để content_catcher callback về sau update
7. Lặp tiếp page tiếp theo
```

---

## 6. Acceptance criteria

- [ ] **Constants** — `SourceFacebookPost`, `ContentSourceFacebookPost` có trong code, hiển thị "Facebook Post" trong UI dashboard
- [ ] **Regex** — `IsValidFacebookPostURL` pass với 10 URL test sau (xem section 8) và **không nhầm** với video/reel
- [ ] **Public API** — `POST /api/contents { source: "facebook_post", url: "..." }` tạo được content với source đúng, fetch được metadata (title, images, like, comment)
- [ ] **Require link Facebook trước khi submit** — submit không có `UserSocialId` → error `ContentKeyUserSocialIdRequired` (0.1)
- [ ] **Verify partner approved** — `UserSocialPartner.Status != Approved` → error `ContentKeyUserSocialNotApproved` (0.2)
- [ ] **Verify ownership** — submit bài người khác (`contentInfo.AuthorId != userSocial.Data.ID`) → error `ContentKeyUserSocialNotMatch` (0.9 — locale key mới)
- [ ] **PublishAt enforce** — bài đăng ngoài khoảng `event.StartAt-EndAt` → error `ContentKeyPublishAtInvalid` (0.5)
- [ ] **OpsHub** — `event.Options.IsEnableOpsHub = true` → bài FB Post được gửi qua OpsHub async (0.6)
- [ ] **Image upload** — bài có ảnh → ảnh được upload lên MinIO, không lưu link FB CDN gốc (sẽ expire)
- [ ] **Cron re-crawl** — chạy thử `GET /api/schedule/crawl-content-facebook-post` → content cũ trong DB được update like/comment mới (chậm vài giây vì IsAsync)
- [ ] **Analytics breakdown** — `event_analytic_daily.statistic.facebookPost` populate đúng (totalContent, totalContentPending, totalContentApproved, totalContentRejected)
- [ ] **Backward compat** — content có source `facebook` và `facebook_reels` cũ không bị ảnh hưởng (test create + view dashboard)
- [ ] **`facebookGetURLByShortLink` regression** — `IsValidFacebookURL` + `IsValidFacebookReelsURL` vẫn pass cho URL hiện hành sau khi đổi `?v=` → `RawQuery`

---

## 7. Stories implementation

| # | Story | Effort | Phụ thuộc |
|---|---|---|---|
| 1 | Constants + regex + validation function | 0.5d | — |
| 2 | Content-catcher model field (`Images`, `AuthorId`) | 0.25d | — |
| 3 | `EventAnalyticDailyStatistic.FacebookPost` field | 0.25d | — |
| 4 | Public API create content case + request validation | 0.5d | 1, 2 |
| 5 | Admin re-crawl case | 0.25d | 1, 2 |
| 6 | Admin import normalize/validate case (TCB-specific) | 0.5d | 1 |
| 7 | `event.go` extract stats (4 chỗ) + analytics struct | 0.5d | 3 |
| 8 | Cron `CrawlDataContentFacebookPost` + route handler | 0.5d | 1 |
| 9 | E2E test + regression test shortlink resolver | 1d | tất cả |

**Total:** ~3.5–4 ngày dev (1 dev). Có thể parallel 1-3, 4-5-6, 7-8 → còn ~2-2.5 ngày calendar.

---

## 8. Test cases regex Facebook Post

URLs phải PASS `IsValidFacebookPostURL`:

```
https://www.facebook.com/username/posts/123456789
https://facebook.com/permalink.php?story_fbid=123&id=456
https://www.facebook.com/photo.php?fbid=123456&set=a.789
https://m.facebook.com/photo/?fbid=12345
https://facebook.com/share/p/abcd1234
https://www.facebook.com/username/posts/pfbid0abc123xyz
https://www.facebook.com/groups/mygroup/posts/9876543
https://touch.facebook.com/permalink.php?story_fbid=1234
```

URLs phải FAIL (là video/reel, không phải post):

```
https://www.facebook.com/watch?v=123456
https://facebook.com/reel/abc123
https://www.facebook.com/share/r/xyz789
```

⚠️ **Edge case overlap:** Regex Post có alternative `/videos/` và `/reels/` → 1 số URL video sẽ match Post regex. Vì thứ tự check trong code là **Reel → Video → Post** (xem section 4.8.b), URL `/reels/...` match Reel trước và không rơi xuống Post. **Phải đảm bảo thứ tự này** trong cả `normalizeImportSource` và `validateImportSourceWithURL`.

---

## 9. Non-functional requirements

| Khía cạnh | Yêu cầu |
|---|---|
| **Performance** | Public API create content: <2s (bao gồm 1 lần gọi content-catcher sync). Cron batch 10 URLs/request, async — không block. |
| **Throughput cron** | ~10 events × 10 contents/page × N pages. Test với data volume hiện tại để verify content-catcher không throttle. |
| **Security** | URL validation chặn nhập tay XSS qua URL field — Echo + ozzo-validation đã cover. Owner verification giảm rủi ro creator submit bài người khác. |
| **Reliability** | Content-catcher fail → trả lỗi `ContentKeyLinkInvalid` ra user (không crash). Cron fail giữa batch → log lỗi và `break` (không retry trong tick này; tick sau sẽ pick up). |
| **Observability** | Log line tag `[Facebook Post]` trong cron. Có thể grep để xem progress. |

---

## 10. Dependencies

**External:**

- `content_catcher` service phải support `source=facebook_post` — **verify với team content-catcher trước khi merge**. Đây là blocker thực sự, không phải code TCB.
- Facebook không thay đổi URL format (regex sẽ break nếu FB đổi).

**Internal:**

- TCB phải có `internalservice.Content().UploadImagesFromURLs` hoặc tương đương — verify.
- TCB phải có `scheduleGuard`, `InsertContentCallback` — verify.
- Locale keys `ContentKeyUserSocialNotLink`, `ContentKeyUserSocialNotMatch` — verify hoặc thêm.

---

## 11. Risks & mitigations

| Rủi ro | Mức độ | Cách xử lý |
|---|---|---|
| Content-catcher chưa support `facebook_post` cho TCB tenant | Cao | Confirm với team content-catcher trước khi code. Có thể cần config thêm |
| Đổi shortlink resolver từ `?v=` → `RawQuery` break video/reel | TB | Regression test 5-10 URL video/reel quen thuộc trước khi merge |
| Regex overlap reel/video → URL post bị classify nhầm | TB | Code switch theo thứ tự **Reel → Video → Post** + unit test 8-10 URL |
| TCB không có `UploadImagesFromURLs` | Thấp | Port từ Amb (~30 LOC) hoặc dùng pattern MinIO upload hiện có |
| User submit link bài private/đã xoá | Thấp | Content-catcher trả status code → đã có pattern handle (`StatusCode 403/401`) ở các source khác, áp dụng tương tự nếu cần |
| Facebook Post không có view → dashboard hiển thị 0 view | Thấp | Doc rõ trong overview. UI có thể ẩn cột View khi source = facebook_post (đề xuất, không bắt buộc) |

---

## 12. Out of scope (nhắc lại từ overview)

- ❌ Reward/cash/point cho Facebook Post (KHÔNG đụng `UserEventStatistic.FacebookPost`, KHÔNG đụng `event_schema.go` switch case milestone)
- ❌ Flow link Facebook profile creator (`GetDataProfile`, `IsValidFacebookProfileURL`, `SourceFacebookProfile`)
- ❌ Port sang vCreator-PH
- ❌ Re-classify content cũ có source `facebook` mà thực ra là post text
- ❌ Tách view của video nhúng trong bài post

---

## 13. Timeline

| Milestone | Ngày |
|---|---|
| Confirm content-catcher support `facebook_post` cho TCB | 12/05/2026 |
| Merge story 1-6 (foundation + main flow) | 14/05/2026 |
| Merge story 7-8 (analytics + cron) | 15/05/2026 |
| QA + regression | 16-17/05/2026 |
| Release production | 19/05/2026 |

**Target:** ~1 tuần làm việc kể từ confirm.

---

## 14. Tài liệu liên quan

- **Overview:** [`overview.md`](./overview.md)
- **Gap gốc:** [`general/gaps/p0/35-facebook-post-crawl-and-count-campaign.md`](../../general/gaps/p0/35-facebook-post-crawl-and-count-campaign.md)
- **Source Ambassador (reference khi code):**
  - `accesstrade-projects/ambassabor/backend/internal/module/social/facebook/facebook.go`
  - `accesstrade-projects/ambassabor/backend/pkg/public/service/content.go` (case `ContentSourceFacebookPost`)
  - `accesstrade-projects/ambassabor/backend/pkg/public/service/schedule.go` (cron `CrawlDataContentFacebookPost`)
  - `accesstrade-projects/ambassabor/backend/internal/service/event.go` (analytics extract pattern)
  - `accesstrade-projects/ambassabor/backend/internal/model/mg/event_analytic_daily.go`

---

*Có thắc mắc kỹ thuật, ping team backend TCB hoặc cross-reference Ambassador trước khi tự chế.*
