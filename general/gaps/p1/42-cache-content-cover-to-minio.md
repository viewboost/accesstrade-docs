# Gap #42 — Cache lại ảnh cover của top content (content-feature) — TCB vừa làm, vCreator/Ambassador chưa có

> **Priority**: 🟠 **P1** (initial 2026-05-10 — user self-listed gap, "lỗi này xuất hiện liên tục")
> **Source**: User self-listed gap
> **Direction port**: TCB → vCreator + Ambassador (TCB pattern production-ready)
> **Last verified**: 2026-05-10

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

Khi creator post content (TikTok video, Facebook reel, YouTube short), hệ thống crawl về metadata bao gồm **cover image URL** từ CDN của social platform (`fbcdn.net`, `tiktokcdn.com`, `ytimg.com`, ...).

CDN của social có **signature/expires query string** — sau vài giờ → vài ngày → URL hết hạn → ảnh **hỏng** trên platform AccessTrade. Đặc biệt với **top content** (content được feature, hiển thị nhiều) → user nhìn thấy ảnh hỏng liên tục → **ux tệ + giảm trust**.

User feedback: **"lỗi này xuất hiện liên tục"** — không phải hypothetical, đang là bug active.

**TCB vừa làm** giải pháp: download cover từ CDN → upload MinIO → lưu URL MinIO permanent vào DB. 2 commit gần đây:
- `dcd358bd` fix(partner-content): self-host TikTok cover to MinIO to prevent expired thumbnails
- `7197a1bd` fix(partner-content): host all platform covers to MinIO (not just TikTok)

vCreator + Ambassador **chưa có** giải pháp này → vẫn bị bug.

## Bảng so sánh

| Khía cạnh | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| File `content_catcher/cover_host.go` | ✅ 159 LOC | ❌ | ❌ |
| Function `ShouldHostCover(url) bool` | ✅ | ❌ | ❌ |
| Function `HostCoverToMinio(ctx, contentID, url) (newURL, error)` | ✅ | ❌ | ❌ |
| MinIO bucket `content-cover/` prefix | ✅ | (có MinIO module nhưng chưa wire) | (có MinIO module nhưng chưa wire) |
| Caller wire vào partner content service | ✅ `pkg/public/service/partner.go:491-496` | ❌ | ❌ |
| Cover platforms supported | TikTok + FB + YouTube + Instagram | ❌ | ❌ |
| Stable CDN suffix detection (skip cache nếu CDN ổn định) | ✅ | ❌ | ❌ |
| Browser-like User-Agent (tránh bot detection) | ✅ | ❌ | ❌ |
| Max file size limit (5MB) | ✅ | ❌ | ❌ |
| Download timeout (10s) | ✅ | ❌ | ❌ |

## Hệ quả

- **vCr + Amb**: top content/feature ở dashboard hoặc creator profile → ảnh hỏng sau vài giờ → user complaint, brand không vui
- **Tần suất**: TCB confirm "lỗi xuất hiện liên tục" trước khi fix → vCr/Amb đang gặp tương tự
- **Workaround không có**: không có cách avoid ngoài việc tự cache, vì social CDN không cung cấp permanent URL

## Liên quan các gap khác

- **Gap #17 (Avatar cache MinIO)**: cùng pattern — cache image từ social về MinIO. TCB đã có cho avatar (gap #17), giờ extend cho content cover. vCr/Amb cần cả 2.
- **Gap #41 (Markdown editor)**: cũng touch image upload pattern → có thể combo wave
- **Gap #15 (Reconciliation)**: top content trong reconciliation report cần cover ổn định

## Giải pháp

### Phase 1: vCreator (~3-5 ngày)

1. **Copy `cover_host.go`** (~1 giờ):
   - Copy `internal/module/social/content_catcher/cover_host.go` từ TCB (159 LOC)
   - Adapt với MinIO config vCreator
2. **Wire vào content service** (~1 ngày):
   - Locate caller equivalent với TCB `pkg/public/service/partner.go:491-496`
   - Thêm logic: khi crawl cover về → check `ShouldHostCover()` → nếu true → call `HostCoverToMinio()` → save MinIO URL thay vì CDN URL
3. **Migration data cũ** (~0.5 ngày):
   - Optional: re-host top content covers cũ. Cron batch background.
   - Hoặc skip — chỉ áp dụng cho content mới
4. **Test** (~0.5 ngày):
   - Crawl content TikTok, FB, YT → verify URL save là MinIO
   - Wait 24h → verify ảnh vẫn hiển thị ok
   - Test stable CDN suffix detection (không cache CDN ổn định để tiết kiệm storage)

### Phase 2: Ambassador (~3-5 ngày)
- Tương tự Phase 1

**Total**: ~1-2 tuần (3-5 ngày mỗi sản phẩm).

## Tại sao P1

- **Bug active**: user confirm "xuất hiện liên tục"
- **Effort thấp**: 159 LOC + wire 1 caller, TCB pattern production-tested
- **MinIO infrastructure đã sẵn**: vCr/Amb đều có MinIO module
- **UX impact rõ**: ảnh hỏng trên top content/dashboard ảnh hưởng trực tiếp brand trust
- **Pattern duplicate với #17 (avatar cache)**: validate gấp đôi nếu làm chung wave

→ Không phải P0 (vẫn vận hành được, chỉ ux xấu) nhưng sprint tới phải làm.

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

TCB có file `internal/module/social/content_catcher/cover_host.go` (159 LOC) + caller `pkg/public/service/partner.go:491-496` self-host cover của top content về MinIO. vCreator/Ambassador có MinIO module nhưng KHÔNG có file `cover_host.go` → cover URL vẫn lưu CDN của social, expire sau vài giờ/ngày.

## Verify code

### TCB (source of truth)

**File** — `internal/module/social/content_catcher/cover_host.go` (159 LOC):
```go
package contentcatcher

import (
    "context"
    "io"
    "net/http"
    "net/url"
    "os"
    "path/filepath"
    "strings"
    "time"

    "viewboost/internal/config"
    "viewboost/internal/module/minio"
)

const (
    coverObjectPrefix    = "content-cover/"
    coverDownloadTimeout = 10 * time.Second
    coverMaxSize         = 5 * 1024 * 1024 // 5MB
    coverFetchUserAgent  = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ..."
)

// stableCoverHostSuffixes là các CDN có URL ổn định theo ID (không có signature/expires)
// → skip cache để tiết kiệm storage
var stableCoverHostSuffixes = []string{...}

// ShouldHostCover quyết định có cần self-host cover không
func ShouldHostCover(url string) bool { ... }

// HostCoverToMinio download URL → upload MinIO → return new URL
func HostCoverToMinio(ctx context.Context, contentID primitive.ObjectID, sourceURL string) (string, error) {
    // 1. ShouldHostCover: skip nếu URL từ CDN ổn định
    // 2. HTTP GET với browser User-Agent (tránh bot detection)
    // 3. Validate Content-Type + size limit (5MB)
    // 4. Generate object name: content-cover/{contentID}.{ext}
    // 5. Upload MinIO
    // 6. Return MinIO URL
}
```

**Caller** — `pkg/public/service/partner.go:491-496`:
```go
if !contentcatcher.ShouldHostCover(content.Cover) {
    // skip — CDN ổn định
}

newURL, err := contentcatcher.HostCoverToMinio(ctx, content.ID, content.Cover)
if err == nil {
    content.Cover = newURL  // replace CDN URL bằng MinIO URL
}
```

**Recent commits**:
- `dcd358bd` fix(partner-content): self-host TikTok cover to MinIO to prevent expired thumbnails
- `7197a1bd` fix(partner-content): host all platform covers to MinIO (not just TikTok)

### vCreator status

```bash
ls vcreator/backend/internal/module/social/content_catcher/
# client.go, common.go, model.go (KHÔNG có cover_host.go)

ls vcreator/backend/internal/module/minio/
# minio.go ✅ ĐÃ CÓ infrastructure
```

→ Chỉ thiếu service layer, infrastructure đã sẵn.

### Ambassador status

```bash
ls ambassabor/backend/internal/module/social/content_catcher/
# client.go, common.go, model.go (KHÔNG có cover_host.go)
```

→ Tương tự vCreator.

## Đề xuất implementation

### Phase 1: vCreator (~3-5 ngày)

1. **Copy file** (~30 phút):
   ```bash
   cp tcb/internal/module/social/content_catcher/cover_host.go \
      vcr/internal/module/social/content_catcher/cover_host.go
   cp tcb/internal/module/social/content_catcher/cover_host_test.go \
      vcr/internal/module/social/content_catcher/cover_host_test.go
   ```
   Adapt import paths nếu khác.

2. **Wire caller** (~1 ngày):
   - Locate content crawl service ở vCreator (likely `pkg/public/service/partner.go` hoặc `internal/service/content.go`)
   - Sau khi crawl content metadata + cover URL → wire:
   ```go
   if contentcatcher.ShouldHostCover(content.Cover) {
       newURL, err := contentcatcher.HostCoverToMinio(ctx, content.ID, content.Cover)
       if err == nil {
           content.Cover = newURL
       }
   }
   ```

3. **MinIO config** (~30 phút):
   - Verify bucket policy cho prefix `content-cover/` public read (hoặc presigned URL pattern)
   - Adapt config vCreator nếu khác

4. **Migration data cũ** (~0.5 ngày, optional):
   - Cron batch: scan top content recently → re-host cover
   - Hoặc skip nếu top content được crawl lại trong N ngày → tự fix

5. **Test** (~1 ngày):
   - Unit test (copy `cover_host_test.go` từ TCB)
   - Integration: crawl content TikTok/FB/YT → verify cover URL là MinIO
   - Wait 24h → ảnh vẫn hiển thị
   - Edge case: file > 5MB, timeout, CDN trả 403

### Phase 2: Ambassador (~3-5 ngày)
Tương tự Phase 1.

**Total**: ~1-2 tuần.

## Risks + mitigations

1. **MinIO storage**: top content nhiều → tốn dung lượng MinIO
   - **Mitigation**: 5MB limit per cover. Stable CDN suffix detection skip cache. Cron cleanup orphan cover sau N ngày.
2. **Bandwidth**: download cover từ social CDN có thể bị rate limit
   - **Mitigation**: 10s timeout per request. User-Agent browser bình thường tránh bot detection. Retry với exponential backoff.
3. **CDN format thay đổi**: TikTok/FB có thể đổi URL pattern → regex `stableCoverHostSuffixes` outdated
   - **Mitigation**: monitor + update regex. Default behavior: cache nếu URL có signature query string.
4. **Concurrent upload conflict**: 2 process cùng host 1 contentID → overwrite
   - **Mitigation**: idempotent (cùng object name = overwrite OK). Hoặc check existence trước.
5. **Public access vs private**: MinIO bucket public read hay private?
   - **Mitigation**: TCB hiện public read (URL như CDN). Nếu cần private → frontend gen presigned URL trên-the-fly.

## Files referenced

**TCB (source of truth)**:
- `internal/module/social/content_catcher/cover_host.go` (159 LOC)
- `internal/module/social/content_catcher/cover_host_test.go` (test cases)
- `internal/module/minio/minio.go` (MinIO client, đã có)
- `pkg/public/service/partner.go:491-496` (caller wire)
- Commits `dcd358bd` + `7197a1bd` (TCB fix history)

**vCreator (target — chưa có)**:
- KHÔNG có `internal/module/social/content_catcher/cover_host.go`
- ✅ ĐÃ CÓ `internal/module/minio/minio.go`
- Caller ở partner/content service chưa wire

**Ambassador (target — chưa có)**:
- Tương tự vCreator

## Lịch sử phân loại

- **2026-05-10 (initial P1)**: User self-listed gap. Quote: "Cache lại ảnh của top bài đăng (content-feature) / Mới làm cho TCB. lỗi này xuất hiện liên tục" + "P1".
  - Lý do P1: bug active, user confirm "lỗi xuất hiện liên tục" — không hypothetical. TCB vừa fix (commits dcd358bd + 7197a1bd) → có pattern production-tested, copy nhanh. Effort thấp (159 LOC + wire 1 caller). Pair tốt với #17 (avatar cache) cùng pattern image hosting.
