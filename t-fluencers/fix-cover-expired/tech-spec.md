# Tech Spec — Fix Cover Expired (Self-host TikTok Cover lên MinIO)

> Tài liệu kỹ thuật chi tiết cho việc tự host ảnh `cover` của top 8 content trả về từ API `GET /partners/content-features` lên MinIO.

**Ngày:** 09/05/2026
**Trạng thái:** Đề xuất
**Đối tượng đọc:** Backend Dev, QA, Tech Lead
**Liên quan:** [overview.md](./overview.md), [test-cases.csv](./test-cases.csv)

---

## 1. Bối cảnh kỹ thuật

### 1.1. API và flow hiện tại

**Endpoint:** `GET /partners/content-features?partner={id}&limit=8`

**Call chain:**
- Handler: [`backend/pkg/public/handler/partner.go:103-136`](../../../techcombank/backend/pkg/public/handler/partner.go) (`GetContentFeature`)
- Service: [`backend/pkg/public/service/partner.go:108-264`](../../../techcombank/backend/pkg/public/service/partner.go) (`GetListContentLeaderboard`)
- Cache key: `CacheListContentFeature_{limit}_{page}_{partnerID}` — TTL 4h

**Logic chọn top 8 (giữ nguyên, không thay đổi):**
1. Đếm `count({status: "approved", isHidden: {$ne: true}})`
2. Nếu `total <= limit` → fallback `GetContentFeature` (filter event active, sort theo `param.Sort`)
3. Nếu `total > limit` → aggregation pipeline group theo user, mỗi user lấy 1 content tốt nhất (sort `order DESC, statistic.view.total DESC`)

**Field cover trả về:** `response.ContentResponse.Cover` (string)
- Nguồn 1: `ContentRaw.Cover` (URL TikTok hoặc MinIO sau khi migrate)
- Fallback: `ContentRaw.Thumbnail.Medium.URL` (khi `Cover == ""`)

### 1.2. Vấn đề

Mọi nền tảng đều cấp URL có expires:

| Nền tảng | Pattern | TTL |
|----------|---------|-----|
| TikTok | `tiktokcdn.com/...?x-expires=<unix>&x-signature=...` | ~2 ngày |
| Facebook | `fbcdn.net/...?oe=<hex_unix>&oh=...` | ~3-4 ngày |
| Instagram | `cdninstagram.com/...?oe=...` (cùng Meta CDN) | ~3-4 ngày |
| YouTube | `i.ytimg.com/vi/<id>/...` (URL ổn định, hiếm khi đổi) | rất lâu |

System đã lưu `coverExpiredAt` cho TikTok ([`content_catcher/common.go:67`](../../../techcombank/backend/internal/module/social/content_catcher/common.go)) nhưng **không có job re-crawl**. Khi campaign đóng → không crawl mới → URL chết.

### 1.3. FE consume

FE chỉ dùng field `cover` ở [`frontend/src/pages/home/components/video-item/index.tsx:32`](../../../techcombank/frontend/src/pages/home/components/video-item/index.tsx):
```tsx
<AppImage src={item?.cover} ... />
```
**Không dùng `thumbnail`** → scope chỉ cần xử lý `cover`.

---

## 2. Giải pháp

### 2.1. Tóm tắt

Trong service `GetListContentLeaderboard`, sau khi build xong response 8 content:
- **Async** (goroutine, không block response): với mỗi content có cover URL ngoài → download → upload MinIO → update DB field `cover` (ghi đè URL MinIO)
- Sau khi goroutine xong (nếu có ít nhất 1 cover được host) → **invalidate Redis cache** của partner → request kế tiếp lập tức trả URL MinIO mới (không phải đợi 4h cache TTL)

### 2.2. Phạm vi

| Áp dụng cho | Không áp dụng |
|-------------|---------------|
| API `GET /partners/content-features` | API `GET /events/{id}/content/leaderboards` (xét sau) |
| Field `cover` | Field `thumbnail` (FE không dùng) |
| TikTok, Facebook, Instagram, các CDN có signature/expires | URL đã là MinIO (host khớp `FileHost`) |
| Mọi cover URL HTTP(S) bên ngoài | URL rỗng / malformed / scheme khác http(s) |
| | **YouTube (ytimg.com, img.youtube.com)** — URL ổn định theo videoId, không expire |

**Logic**: cover URL nào không trỏ tới MinIO của mình **và không phải CDN có URL ổn định** → tải về và host.

**Skip list** (CDN có URL vĩnh viễn):
- `ytimg.com` — YouTube (`https://i.ytimg.com/vi/{videoId}/maxresdefault.jpg`)
- `img.youtube.com` — alias cũ của YouTube

→ Tránh tốn storage + bandwidth không cần thiết.

### 2.3. Strategy

- **Upload 1 lần, giữ vĩnh viễn** — không có job dọn dẹp, không re-upload
- **Async, fire-and-forget** — không block API response. Lần đầu user vẫn thấy URL TikTok (thường còn hạn 6–12h khi vừa crawl)
- **Idempotent** — kiểm tra cover đã là URL MinIO chưa, nếu rồi thì skip

---

## 3. Chi tiết implementation

### 3.1. Helper module mới

**File:** `backend/internal/module/social/content_catcher/cover_host.go` (mới)

API public:
- `ShouldHostCover(url string) bool` — true nếu URL là http(s) hợp lệ và **không** thuộc MinIO của mình. Không whitelist platform.
- `IsMinioCoverURL(url string) bool` — kiểm tra URL đã trỏ tới `FileHost` của mình (đã host).
- `HostCoverToMinio(ctx, contentID, coverURL) (string, error)` — download + upload + trả URL MinIO public.

**Điểm quan trọng:**
- Set header `User-Agent` = Chrome browser thường khi fetch — CDN binary endpoints (fbcdn.net, tiktokcdn.com, ytimg.com) accept browser UA. **Không** impersonate bot của Meta/TikTok để tránh ToS gray area.
- Object name: `content-cover/{contentID.Hex()}.{ext}` — idempotent theo contentID.
- Size limit 5MB qua `io.LimitReader` — chống OOM.
- Detect Content-Type → extension (`.jpg`/`.png`/`.webp`/`.gif`), fallback `.jpg`.
- Reject scheme khác `http(s)` (chống `file://`, `ftp://`, `javascript:`...).
- Idempotent: cùng `contentID` ghi đè cùng object → không tăng dung lượng khi retry.

### 3.2. Tích hợp vào service

**File:** `backend/pkg/public/service/partner.go` (sửa)

Thêm method private:

```go
// hostCoversAsync spawn goroutine fire-and-forget để host cover lên MinIO.
// Sau khi xong (nếu có ít nhất 1 cover được host), invalidate Redis cache
// để request kế tiếp lập tức trả URL MinIO mới (không phải đợi 4h cache TTL).
func (p partnerImpl) hostCoversAsync(contents []*modelmg.ContentRaw, partnerID string) {
    if len(contents) == 0 {
        return
    }
    go func() {
        defer func() {
            if r := recover(); r != nil {
                log.Printf("[hostCoversAsync] panic: %v", r)
            }
        }()
        ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
        defer cancel()

        var success, skipped, failed int
        for _, content := range contents {
            if content == nil || content.ID.IsZero() || content.Cover == "" {
                skipped++; continue
            }
            if !contentcatcher.ShouldHostCover(content.Cover) {
                skipped++; continue
            }

            newURL, err := contentcatcher.HostCoverToMinio(ctx, content.ID, content.Cover)
            if err != nil {
                log.Printf("[hostCoversAsync] content=%s err=%v", content.ID.Hex(), err)
                failed++; continue
            }

            if err := daomongodb.ContentDAO().GetShare().UpdateOne(ctx, new(modelmg.ContentRaw),
                bson.M{"_id": content.ID},
                bson.M{"$set": bson.M{"cover": newURL}},
            ); err != nil {
                log.Printf("[hostCoversAsync] update db content=%s err=%v", content.ID.Hex(), err)
                failed++; continue
            }
            success++
        }

        // Invalidate cache → request kế tiếp lập tức cache miss → trả URL MinIO mới
        if success > 0 && partnerID != "" {
            pattern := fmt.Sprintf("%s_*_*_%s", redis.CacheListContentFeature, partnerID)
            if err := redis.DelAllKeyByPattern(pattern); err != nil {
                log.Printf("[hostCoversAsync] cache invalidate err=%v", err)
            }
        }
    }()
}
```

**Sửa `GetListContentLeaderboard`:**

Trong cả 2 nhánh (leaderboard aggregation + fallback `GetContentFeature`), sau khi build xong `res.Data`, gom các `*modelmg.ContentRaw` đã chọn rồi gọi `p.hostCoversAsync(contents, query.PartnerID)` trước khi return.

**Cụ thể vị trí gọi:**
- Nhánh leaderboard: trước `return res` ở [`partner.go:188`](../../../techcombank/backend/pkg/public/service/partner.go) và sau loop `contentsBackup`
- Nhánh fallback `GetContentFeature`: trước `return res` ở cuối function

**Thu thập content cần host:** dùng `*modelmg.ContentRaw` gốc (không phải `response.ContentResponse`) để có access `ID` và `Cover` từ DB — đảm bảo update đúng record.

### 3.3. Không thay đổi

- Không thay đổi response shape
- Không thay đổi sort/filter logic
- Không cần migration data — content cũ sẽ tự migrate dần khi lọt top
- Cache TTL 4h giữ nguyên (chỉ thêm invalidate sau khi host xong)

---

## 4. Schema & Config

### 4.1. Database

**Không cần migration.** Field `cover` đã tồn tại ở `ContentRaw`:
```go
// backend/internal/model/mg/content.go:28
Cover string `bson:"cover,omitempty"`
```

Chỉ ghi đè giá trị từ URL nền tảng gốc → URL MinIO.

### 4.2. Environment variables

**Không cần biến mới.** Dùng các biến đã có:

| ENV | Mô tả | Đã tồn tại? |
|-----|-------|-------------|
| `MINIO_END_POINT` | MinIO endpoint | ✅ |
| `MINIO_ACCESS_KEY` | MinIO access key | ✅ |
| `MINIO_SECRET_KEY` | MinIO secret key | ✅ |
| `MINIO_BUCKET_PUBLIC_FILE` | Bucket public cho ảnh | ✅ |
| `FILE_HOST` | Public host serving MinIO bucket | ✅ |

### 4.3. MinIO bucket policy

Bucket `PublicFile` cần policy public-read (đã có sẵn — avatar, file image dùng cùng bucket này). Không cần thay đổi.

### 4.4. Object naming convention

Format: `content-cover/{contentID}.{ext}`

Ví dụ: `content-cover/68f48c96753ef5c3a39bb695.jpg`

**Lý do dùng `contentID`:**
- 1 content → 1 cover → tránh duplicate khi retry
- Idempotent: upload nhiều lần cùng object → ghi đè, không tăng dung lượng

---

## 5. Error handling & edge cases

| Case | Xử lý |
|------|-------|
| Download timeout (>10s) | Log error, skip content đó. Lần cache miss kế tiếp retry |
| HTTP 4xx/5xx từ nền tảng gốc | Log warn, skip silently. Thường vì URL đã expired (campaign đóng lâu). User thấy ảnh vỡ cho video đó nhưng không break flow — content khác trong batch vẫn host được. |
| MinIO PutObject fail | Log error, skip. Không update DB → giữ nguyên URL cũ |
| Update MongoDB fail | Log error. Object đã upload MinIO nhưng DB không update — lần sau retry sẽ ghi đè cùng object → idempotent OK |
| Content `cover` rỗng | Skip — fallback logic FE/BE dùng `Thumbnail.Medium.URL` |
| Cover đã là URL MinIO | Skip — `IsMinioCoverURL()` check |
| Cover URL malformed/scheme khác http(s) | Skip — `ShouldHostCover()` reject |
| Goroutine panic | Phải có `recover()` ở đầu goroutine để tránh crash service |
| Goroutine leak khi service shutdown | `context.WithTimeout(60s)` đảm bảo goroutine tự cleanup |
| Redis DEL fail (cache invalidate lỗi) | Log error, không retry. Worst case: user phải đợi 4h cache TTL — fallback an toàn |
| Concurrent request cùng partner | Cùng spawn 2 goroutine, cùng host MinIO (idempotent), cùng DEL cache (idempotent) → OK |
| Goroutine xong nhưng tất cả fail (success=0) | Skip cache invalidate — tránh thừa 1 Redis op vô nghĩa |

**Bổ sung recover:**
```go
go func() {
    defer func() {
        if r := recover(); r != nil {
            log.Printf("[hostCoversAsync] panic: %v", r)
        }
    }()
    // ... rest of logic
}()
```

---

## 6. Performance & Resource

### 6.1. Ước lượng load

| Metric | Giá trị |
|--------|---------|
| Cover size trung bình | 50–200 KB |
| Số content top/partner | 8 |
| Số partner active | ~5–10 |
| Cache TTL | 4h |
| → Số upload/ngày | ~8 × 10 × 6 = ~480 lần upload (worst case nếu mỗi cache miss đều cần upload) |
| → Sau 1 tháng ổn định | <100 upload/ngày (đa số content top đã được host) |
| Storage 1 năm | <1 GB |
| Bandwidth download TikTok | <100 MB/ngày |

→ **Negligible**, không ảnh hưởng performance.

### 6.2. Concurrency

- Mỗi request `GetListContentLeaderboard` spawn **1 goroutine** xử lý tuần tự 8 content
- Sau khi goroutine xong + invalidate cache → request kế tiếp lập tức cache miss → spawn goroutine mới (nhưng `ShouldHostCover` skip cover đã là MinIO → không upload lại). 1 vòng "self-correcting" rồi ổn định
- Không cần worker pool / rate limit ở giai đoạn này (load thấp)

### 6.3. API response time

**Không thay đổi** — async fire-and-forget.

---

## 7. Logging & Monitoring

### 7.1. Log format

```
[hostCoversAsync] content=def456 err=download cover status: 403
[hostCoversAsync] update db content=ghi789 err=mongo timeout
[hostCoversAsync] cache invalidate err=redis: connection refused  (nếu fail)
[hostCoversAsync] done success=6 skipped=1 failed=1 duration=2.3s partner=68f48c96753ef5c3a39bb695
```

### 7.2. Metrics đề xuất (optional, phase 2)

- Counter: `content_cover_host_total{result="success|failed|skipped"}`
- Histogram: `content_cover_host_duration_seconds`

---

## 8. Rollout plan

1. **Phase 1 — Code & test**
   - Implement helper + service integration
   - Unit test `IsTikTokCoverURL`, `IsMinioCoverURL`
   - Integration test với mock TikTok URL → kiểm tra DB update

2. **Phase 2 — Deploy staging**
   - Deploy backend
   - Gọi API `GET /partners/content-features` qua admin/dev tool
   - Check log goroutine, MinIO bucket có file mới, DB content cover URL đã đổi
   - Verify FE staging hiển thị ảnh từ MinIO

3. **Phase 3 — Deploy production**
   - Deploy ngoài giờ peak
   - Monitor log error rate trong 24h đầu
   - Sau 1 tuần: spot-check 20 content random ở top → 100% cover URL phải là MinIO

4. **Phase 4 — Optional follow-up**
   - Backfill script (nếu cần): chạy 1 lần qua tất cả content `status=approved, isHidden!=true` để host cover ngay (thay vì đợi lọt top)
   - Mở rộng cho `/events/{id}/content/leaderboards`
   - Mở rộng cho YouTube/FB nếu phát hiện cover expire

---

## 9. Rollback plan

Nếu có sự cố:
1. **Revert code** — tắt `p.hostCoversAsync(...)` call → API quay lại behavior cũ (URL TikTok)
2. **Không cần xóa MinIO files** — ảnh đã host vẫn dùng được
3. **Không cần rollback DB** — URL MinIO trong DB vẫn hợp lệ (file vẫn tồn tại)

→ Rollback an toàn, không mất dữ liệu.

---

## 10. Open questions

1. **Có cần host cover cho `/events/{id}/content/leaderboards` không?** — API tương tự, dùng cùng aggregation. Để phase sau, đo traffic trước.
2. **Có cần resize/optimize ảnh trước khi upload không?** — Hiện tại upload nguyên bản. Cover ~720x1280, JPEG quality default. Nếu cần tối ưu bandwidth FE, phase 2 có thể resize 540x960.
3. **Có cần CDN trước MinIO?** — Tùy infra. Hiện tại `FileHost` đã serve qua CDN/proxy nội bộ, không cần thêm.
4. **Backfill cho content cũ?** — Hiện tại lazy migrate khi lọt top 8. Nếu muốn backfill 100% content `status=approved` để chuẩn bị cho future top, cần script one-shot riêng.

---

## 11. Files thay đổi

| File | Loại | Mô tả |
|------|------|-------|
| `backend/internal/module/social/content_catcher/cover_host.go` | Mới | Helper `ShouldHostCover` / `IsMinioCoverURL` / `HostCoverToMinio` |
| `backend/internal/module/social/content_catcher/cover_host_test.go` | Mới | Unit test helper (~30 sub-tests) |
| `backend/pkg/public/service/partner.go` | Sửa | Thêm `hostCoversAsync(contents, partnerID)`, gọi trong `GetListContentLeaderboard` (cả 2 nhánh) + invalidate Redis cache sau khi xong |

**Estimated effort:** 2–3 ngày (1 dev), bao gồm code + test + deploy staging.
