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

URL TikTok cover có dạng:
```
https://p16-sign-sg.tiktokcdn.com/.../tos-alisg-p-0037/...?x-expires=1715250000&x-signature=...
```

Param `x-expires` (Unix timestamp) → URL chết sau **vài giờ tới ~24h**. System đã lưu `coverExpiredAt` ([`content_catcher/common.go:67`](../../../techcombank/backend/internal/module/social/content_catcher/common.go)) nhưng **không có job re-crawl**.

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
- **Async** (goroutine, không block response): với mỗi content có cover URL TikTok → download → upload MinIO → update DB field `cover` (ghi đè URL MinIO)
- Lần cache miss kế tiếp (sau 4h) → DB đã có URL MinIO → response có URL MinIO

### 2.2. Phạm vi

| Áp dụng cho | Không áp dụng |
|-------------|---------------|
| API `GET /partners/content-features` | API `GET /events/{id}/content/leaderboards` (xét sau) |
| Field `cover` | Field `thumbnail` (FE không dùng) |
| Source = TikTok | YouTube (URL ổn định, không cần) |
| Cover URL có `x-expires` hoặc match domain `tiktokcdn.com` | URL đã là MinIO (host khớp `FileHost`) |

### 2.3. Strategy

- **Upload 1 lần, giữ vĩnh viễn** — không có job dọn dẹp, không re-upload
- **Async, fire-and-forget** — không block API response. Lần đầu user vẫn thấy URL TikTok (thường còn hạn 6–12h khi vừa crawl)
- **Idempotent** — kiểm tra cover đã là URL MinIO chưa, nếu rồi thì skip

---

## 3. Chi tiết implementation

### 3.1. Helper module mới

**File:** `backend/internal/module/social/content_catcher/cover_host.go` (mới)

```go
package contentcatcher

import (
    "context"
    "fmt"
    "io"
    "net/http"
    "net/url"
    "os"
    "path/filepath"
    "strings"
    "time"

    "viewboost/internal/config"
    "viewboost/internal/module/minio"

    "go.mongodb.org/mongo-driver/bson/primitive"
)

const (
    coverObjectPrefix = "content-cover/"
    coverDownloadTimeout = 10 * time.Second
)

// IsTikTokCoverURL kiểm tra URL có phải URL TikTok có hạn không
func IsTikTokCoverURL(coverURL string) bool {
    if coverURL == "" {
        return false
    }
    u, err := url.Parse(coverURL)
    if err != nil {
        return false
    }
    // Match TikTok CDN domains
    if !strings.Contains(u.Host, "tiktokcdn") && !strings.Contains(u.Host, "tiktok.com") {
        return false
    }
    return true
}

// IsMinioCoverURL kiểm tra URL đã là URL MinIO (đã migrate) chưa
func IsMinioCoverURL(coverURL string) bool {
    fileHost := config.GetENV().FileHost
    return fileHost != "" && strings.HasPrefix(coverURL, fileHost)
}

// HostCoverToMinio download URL về và upload lên MinIO public bucket.
// Trả về URL MinIO public, error.
func HostCoverToMinio(ctx context.Context, contentID primitive.ObjectID, coverURL string) (string, error) {
    // 1. Download
    client := &http.Client{Timeout: coverDownloadTimeout}
    req, _ := http.NewRequestWithContext(ctx, http.MethodGet, coverURL, nil)
    resp, err := client.Do(req)
    if err != nil {
        return "", fmt.Errorf("download cover: %w", err)
    }
    defer resp.Body.Close()
    if resp.StatusCode != http.StatusOK {
        return "", fmt.Errorf("download cover status: %d", resp.StatusCode)
    }

    // 2. Detect ext (fallback .jpg)
    ext := ".jpg"
    if ct := resp.Header.Get("Content-Type"); strings.HasPrefix(ct, "image/") {
        switch ct {
        case "image/png":
            ext = ".png"
        case "image/webp":
            ext = ".webp"
        }
    }

    // 3. Save to temp file
    filename := fmt.Sprintf("%s%s%s", coverObjectPrefix, contentID.Hex(), ext)
    tmpPath := filepath.Join(os.TempDir(), strings.ReplaceAll(filename, "/", "_"))
    f, err := os.Create(tmpPath)
    if err != nil {
        return "", fmt.Errorf("create temp file: %w", err)
    }
    if _, err := io.Copy(f, resp.Body); err != nil {
        f.Close()
        os.Remove(tmpPath)
        return "", fmt.Errorf("copy temp file: %w", err)
    }
    f.Close()

    // 4. Upload MinIO (PutObject sẽ tự os.Remove)
    bucketName := config.GetENV().MinioCfg.BucketName.PublicFile
    contentType := resp.Header.Get("Content-Type")
    if contentType == "" {
        contentType = "image/jpeg"
    }
    if err := minio.PutObject(tmpPath, filename, contentType, bucketName); err != nil {
        return "", fmt.Errorf("minio put: %w", err)
    }

    // 5. Build public URL
    publicURL := fmt.Sprintf("%s/%s/%s",
        config.GetENV().FileHost,
        bucketName,
        filename,
    )
    return publicURL, nil
}
```

### 3.2. Tích hợp vào service

**File:** `backend/pkg/public/service/partner.go` (sửa)

Thêm method private:

```go
// hostCoversAsync chạy goroutine để host cover lên MinIO cho top content.
// Fire-and-forget, không block response.
func (p partnerImpl) hostCoversAsync(contents []*modelmg.ContentRaw) {
    if len(contents) == 0 {
        return
    }
    go func() {
        ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
        defer cancel()

        for _, content := range contents {
            content := content
            if content == nil || content.Cover == "" {
                continue
            }
            // Skip nếu đã là URL MinIO
            if contentcatcher.IsMinioCoverURL(content.Cover) {
                continue
            }
            // Chỉ xử lý TikTok URL
            if !contentcatcher.IsTikTokCoverURL(content.Cover) {
                continue
            }

            newURL, err := contentcatcher.HostCoverToMinio(ctx, content.ID, content.Cover)
            if err != nil {
                log.Printf("[hostCoversAsync] content=%s err=%v", content.ID.Hex(), err)
                continue
            }

            // Update DB
            err = daomongodb.ContentDAO().GetShare().UpdateOne(ctx, new(modelmg.ContentRaw),
                bson.M{"_id": content.ID},
                bson.M{"$set": bson.M{"cover": newURL}},
            )
            if err != nil {
                log.Printf("[hostCoversAsync] update db content=%s err=%v", content.ID.Hex(), err)
            }
        }
    }()
}
```

**Sửa `GetListContentLeaderboard`:**

Trong cả 2 nhánh (leaderboard aggregation + fallback `GetContentFeature`), sau khi build xong `res.Data`, gom các `*modelmg.ContentRaw` đã chọn rồi gọi `p.hostCoversAsync(...)` trước khi return.

**Cụ thể vị trí gọi:**
- Nhánh leaderboard: trước `return res` ở [`partner.go:188`](../../../techcombank/backend/pkg/public/service/partner.go) và sau loop `contentsBackup`
- Nhánh fallback `GetContentFeature`: trước `return res` ở cuối function

**Thu thập content cần host:** dùng `*modelmg.ContentRaw` gốc (không phải `response.ContentResponse`) để có access `ID` và `Cover` từ DB — đảm bảo update đúng record.

### 3.3. Không thay đổi

- Không thay đổi cache logic (Redis 4h vẫn giữ nguyên)
- Không thay đổi response shape
- Không thay đổi sort/filter logic
- Không cần migration data — content cũ sẽ tự migrate dần khi lọt top

---

## 4. Schema & Config

### 4.1. Database

**Không cần migration.** Field `cover` đã tồn tại ở `ContentRaw`:
```go
// backend/internal/model/mg/content.go:28
Cover string `bson:"cover,omitempty"`
```

Chỉ ghi đè giá trị từ URL TikTok → URL MinIO.

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
| HTTP 4xx/5xx từ TikTok | Log error, skip. Có thể URL đã expired hoặc bị block |
| MinIO PutObject fail | Log error, skip. Không update DB → giữ nguyên URL cũ |
| Update MongoDB fail | Log error. Object đã upload MinIO nhưng DB không update — lần sau retry sẽ ghi đè cùng object → idempotent OK |
| Content `cover` rỗng | Skip — fallback logic FE/BE dùng `Thumbnail.Medium.URL` |
| Cover đã là URL MinIO | Skip — `IsMinioCoverURL()` check |
| Cover không phải TikTok URL (YouTube, FB...) | Skip — `IsTikTokCoverURL()` check. YouTube URL ổn định, không cần host |
| Goroutine panic | Phải có `recover()` ở đầu goroutine để tránh crash service |
| Goroutine leak khi service shutdown | `context.WithTimeout(60s)` đảm bảo goroutine tự cleanup |

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
- Tránh spam: cùng 1 partner trong 4h cache window chỉ tạo 1 goroutine
- Không cần worker pool / rate limit ở giai đoạn này (load thấp)

### 6.3. API response time

**Không thay đổi** — async fire-and-forget.

---

## 7. Logging & Monitoring

### 7.1. Log format

```
[hostCoversAsync] start contents=8 partner=68f48c96753ef5c3a39bb695
[hostCoversAsync] content=abc123 url=https://...tiktokcdn... result=hosted minio_url=https://...
[hostCoversAsync] content=def456 err=download cover status: 403
[hostCoversAsync] done success=6 skipped=1 failed=1 duration=2.3s
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
2. **Có cần resize/optimize ảnh trước khi upload không?** — Hiện tại upload nguyên bản. Cover TikTok ~720x1280, JPEG quality default. Nếu cần tối ưu bandwidth FE, phase 2 có thể resize 540x960.
3. **Có cần CDN trước MinIO?** — Tùy infra. Hiện tại `FileHost` đã serve qua CDN/proxy nội bộ, không cần thêm.

---

## 11. Files thay đổi

| File | Loại | Mô tả |
|------|------|-------|
| `backend/internal/module/social/content_catcher/cover_host.go` | Mới | Helper download + upload MinIO |
| `backend/pkg/public/service/partner.go` | Sửa | Thêm `hostCoversAsync`, gọi trong `GetListContentLeaderboard` |
| `backend/internal/module/social/content_catcher/cover_host_test.go` | Mới | Unit test helper |

**Estimated effort:** 2–3 ngày (1 dev), bao gồm code + test + deploy staging.
