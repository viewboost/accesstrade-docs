# Tech Spec: Giới hạn tần suất crawl và retry request lỗi sang gateway V2

**Trạng thái:** Đã triển khai (branch `feature/update-flow-crawl`, commit `7f015ec6`, đã merge vào `develop`)
**Ngày:** 2026-11-23
**PRD:** [2026-11-23-crawl-rate-limit-retry-prd.md](2026-11-23-crawl-rate-limit-retry-prd.md)

---

## 1. Tổng quan luồng

```
Cron job crawl (mỗi platform cách nhau 1h30)
  └─ vòng lặp batch 10 URL
       ├─ contentcatcher.Client().GetDataV2(IsAsync=true)
       │    └─ postCrawlSocialV2(payload, retryOf = nil)
       │         ├─ POST {CONTENT_CATCHER_V2_BASE_URL}/v1.0/partner/crawl/social
       │         └─ saveV2RequestLog → markV2RetryState
       │              └─ async & HTTP != 200 → retryStatus=pending, nextRetryAt=+5p
       ├─ time.Sleep(1s)
       ├─ lỗi  → log, continue (batch sau)
       └─ OK   → InsertContentCallback(urls, requestId)

Cron RetryFailedCrawlRequests (2 phút/lần)
  ├─ scheduleGuard: skip nếu đang retry hoặc có crawler đang chạy
  ├─ Find crawl-request-logs {retryStatus: pending, nextRetryAt <= now} sort nextRetryAt, limit 100
  └─ mỗi log:
       ├─ crawler vừa bắt đầu chạy → dừng
       ├─ contentcatcher.RetryV2RequestLog(log)
       │    └─ postCrawlSocialV2(payload dựng lại từ log, retryOf = log._id)
       │         └─ saveV2RequestLog: log mới có retryOf, không vào hàng retry
       ├─ time.Sleep(1s)
       └─ cập nhật log gốc:
            HTTP 200           → retryStatus=success, unset nextRetryAt, InsertContentCallback(requestId mới)
            lỗi, count >= 3    → retryStatus=failed,  unset nextRetryAt
            lỗi, count < 3     → nextRetryAt = now + 5p
```

## 2. Danh sách file

| File | Thay đổi |
|---|---|
| `backend/internal/module/social/content_catcher/client.go` | Thêm `RetryV2RequestLog`; `postCrawlSocialV2` nhận thêm `retryOf` |
| `backend/internal/module/social/content_catcher/request_log.go` | Thêm hằng số retry, field retry trong `V2RequestLog`, hàm `markV2RetryState` |
| `backend/internal/module/social/content_catcher/request_log_test.go` | **Mới.** Test `markV2RetryState` |
| `backend/internal/module/database/mongodb/index.go` | Thêm index `{retryStatus, nextRetryAt}` cho `crawl-request-logs` |
| `backend/pkg/public/schedule/schedule.go` | Lịch cron mới, thêm cron retry |
| `backend/pkg/public/service/schedule.go` | Sleep 1s, `break` → `continue`, guard Threads/TikTok Self, `crawlerRunFlags`, `isAnyCrawlerRunning`, `ProcessTiktokUnauthorized` chạy tuần tự, sửa điều kiện dừng `processTiktokSelfCrawl` |
| `backend/pkg/public/service/schedule_crawl_retry.go` | **Mới.** Job `RetryFailedCrawlRequests` |

## 3. Chi tiết từng phần

### 3.1 Lịch cron: `pkg/public/schedule/schedule.go`

Cron dùng `robfig/cron/v3` với `WithSeconds()`, múi giờ `Asia/Ho_Chi_Minh`.

| Job | Hàm | Cron |
|---|---|---|
| TikTok | `CrawlDataContentTiktok` | `0 30 11,23 * * *` |
| TikTok Self | `CrawlDataContentTiktokSelf` | `0 0 10,22 * * *` |
| Facebook Post | `CrawlDataContentFacebookPost` | `0 30 8,20 * * *` |
| YouTube | `CrawlDataContent` | `0 0 7,19 * * *` |
| Threads | `CrawlDataContentThreads` | `0 30 5,17 * * *` |
| Facebook / Reels | `CrawlDataContentFacebook` | `0 0 4,16 * * *` |
| Retry | `RetryFailedCrawlRequests` | `0 */2 * * * *` |

`CrawlDataContentFacebook` và `CrawlDataContentFacebookPost` chỉ chạy khi `config.GetENV().Facebook.IsEnable = true` (logic có sẵn).

### 3.2 Giãn cách 1 giây: `pkg/public/service/schedule.go`

```go
// crawlRequestInterval khoảng nghỉ sau mỗi request crawl V2 trong job → tối đa 60 req/phút.
const crawlRequestInterval = time.Second
```

`time.Sleep(crawlRequestInterval)` được gọi **ngay sau** mỗi lần gọi gateway, trước khi kiểm tra lỗi, nên chạy cả khi request thành công lẫn khi lỗi. Có 8 chỗ:

| Hàm | Kiểu vòng lặp |
|---|---|
| `processThreadsCrawl` | phân trang theo `lastId` |
| `processTiktokSelfCrawl` | phân trang theo `page` trên mảng link của từng user social |
| `processFacebookCrawl` | `lastId` |
| `processFacebookPostCrawl` | `lastId` |
| `processTiktokCrawl` | `lastId` |
| `processYoutubeCrawl` | `lastId` |
| `crawlTiktokForUserSocial` | `page` |
| `RetryFailedCrawlRequests` | danh sách log |

Hàm dùng chung `postCrawlSocialV2` **không** có limiter hay sleep. Request đồng bộ của user (submit bài trong `pkg/public/service/content.go`, admin trong `pkg/admin/service/content.go`, profile Threads trong `internal/module/social/threads/client.go`) không bị chậm lại.

### 3.3 Batch lỗi không dừng vòng lặp

Với các vòng lặp phân trang theo `lastId`, `lastId` được cập nhật **trước** khi kiểm tra lỗi, rồi `continue`. Nếu không cập nhật trước, vòng lặp sẽ lấy lại đúng batch lỗi và lặp vô hạn.

```go
res, err := contentcatcher.Client().GetDataV2(ctx, contentcatcher.GetDataRequest{...IsAsync: true})
time.Sleep(crawlRequestInterval)
lastId = contents[len(contents)-1].ID
if err != nil {
    // Batch lỗi đã lưu crawl-request-logs (retryStatus=pending) → job retry gửi lại; crawl tiếp batch sau
    fmt.Println("Error content-catcher.Client().GetData : ", err.Error())
    continue
}
totalRequest++
s.InsertContentCallback(ctx, urls, res.Data.RequestID)
```

Với `processTiktokSelfCrawl`, `page++` được chuyển lên trước khi kiểm tra lỗi, với cùng lý do. `crawlTiktokForUserSocial` dùng `for page := 0; ...; page++` nên chỉ cần đổi `break` thành `continue`.

**Sửa lỗi kèm theo trong `processTiktokSelfCrawl`:** điều kiện dừng đổi từ `page*limit > len(links)` sang `>=`. Với điều kiện cũ, khi số link chia hết cho 10 (hoặc bằng 0), job gửi thêm một request có `urls` rỗng. Request này vừa chiếm một lượt 1 giây, vừa có thể bị ghi thành log lỗi rồi bị retry vô ích.

### 3.4 Guard chống chạy chồng

Dùng lại `scheduleGuard(flag, blockers...)` có sẵn (cờ bool trong bộ nhớ, bảo vệ bằng `scheduleMu`).

Cờ mới:

```go
isRunCrawlTiktokSelf   = false
isRunCrawlThreads      = false
isRunRetryCrawlRequest = false
```

`CrawlDataContentThreads` và `CrawlDataContentTiktokSelf` giờ gọi `scheduleGuard` ở đầu hàm, giống các job crawl khác.

```go
// crawlerRunFlags cờ đang chạy của các job crawl theo platform.
func crawlerRunFlags() []*bool {
    return []*bool{
        &isRunFacebookCrawl,
        &isRunFacebookPostCrawl,
        &isRunCrawlTiktok,
        &isRunCrawlTiktokSelf,
        &isRunCrawl, // youtube
        &isRunCrawlThreads,
    }
}

// isAnyCrawlerRunning true nếu có job crawl platform nào đang chạy (có lock scheduleMu).
func isAnyCrawlerRunning() bool
```

### 3.5 `ProcessTiktokUnauthorized`

Trước:

```go
for _, userSocial := range userSocials {
    ...
    go s.crawlTiktokForUserSocial(ctx, userSocial, userLinks)
}
```

Sau: một goroutine duy nhất chạy tuần tự, nên giãn cách 1 giây trong `crawlTiktokForUserSocial` có tác dụng trên tổng số request.

```go
go func() {
    for _, userSocial := range userSocials {
        ...
        s.crawlTiktokForUserSocial(ctx, userSocial, userLinks)
    }
}()
```

### 3.6 Model log: `content_catcher/request_log.go`

Hằng số:

```go
const (
    V2RetryMax      = 3
    V2RetryInterval = 5 * time.Minute

    V2RetryStatusPending = "pending" // chờ job retry gửi lại
    V2RetryStatusSuccess = "success" // gửi lại thành công (HTTP 200)
    V2RetryStatusFailed  = "failed"  // hết số lần retry vẫn lỗi
)
```

Field mới trong `V2RequestLog` (collection `crawl-request-logs`, TTL 30 ngày theo `createdAt`):

| Field (bson) | Kiểu | Ý nghĩa |
|---|---|---|
| `retryOf` | `*ObjectID` | Chỉ có ở log của một lần gửi lại, trỏ về `_id` log gốc |
| `retryStatus` | `string` | Chỉ có ở log gốc cần retry: `pending`, `success` hoặc `failed` |
| `retryCount` | `int` | Số lần đã gửi lại |
| `nextRetryAt` | `*time.Time` | Thời điểm sớm nhất được gửi lại; bị unset khi `success`/`failed` |

Tất cả đều `omitempty`. Log thành công hoặc log của request sync không có các field này.

`saveV2RequestLog` nhận thêm tham số `retryOf primitive.ObjectID` và gọi `markV2RetryState`:

```go
func markV2RetryState(log *V2RequestLog, isAsync bool, retryOf primitive.ObjectID) {
    if !retryOf.IsZero() {
        log.RetryOf = &retryOf
        return
    }
    if isAsync && log.HTTPStatus != http.StatusOK {
        nextRetryAt := log.CreatedAt.Add(V2RetryInterval)
        log.RetryStatus = V2RetryStatusPending
        log.NextRetryAt = &nextRetryAt
    }
}
```

Lưu ý:
- Lỗi mạng hoặc timeout được lưu với `httpStatus = 0`, nên cũng được đánh dấu `pending`.
- Log của một lần gửi lại **không bao giờ** được đánh dấu `pending`. Việc quyết định retry tiếp hay dừng nằm ở job retry, dựa trên log gốc, nên không có chuỗi retry lồng nhau.

### 3.7 Client: `content_catcher/client.go`

`postCrawlSocialV2(payload GetDataRequest, retryOf primitive.ObjectID)`: chỉ thêm `retryOf` để truyền xuống `saveV2RequestLog`. `GetDataV2` và `GetProfileV2` truyền `primitive.NilObjectID`.

Hàm mới:

```go
// RetryV2RequestLog gửi lại request của 1 log lỗi. Trả mã HTTP để job quyết định retry tiếp hay dừng.
func RetryV2RequestLog(ctx context.Context, log *V2RequestLog) (int, GetDataV2Response, error)
```

- Dựng lại `GetDataRequest` từ log: `Source`, `URLs`, `Request.Body["access_token"]`, `Request.Body["is_async"]`. DB lưu đầy đủ giá trị gốc; chỉ API search mới che các giá trị nhạy cảm bằng `[REDACTED]`.
- Gọi `postCrawlSocialV2(payload, log.ID)`. Chữ ký HMAC, `client-trace-no` và `client-request-time` được tạo mới cho mỗi lần gửi.
- Trả `(statusCode, res, err)`, trong đó `err != nil` khi lỗi mạng, HTTP khác 200, không parse được body, hoặc `status` khác `success`.

### 3.8 Job retry: `pkg/public/service/schedule_crawl_retry.go`

```go
const retryCrawlRequestBatch = 100 // 1 req/s → ~100s, dưới chu kỳ cron 2 phút

func (s scheduleImpl) RetryFailedCrawlRequests() {
    release := scheduleGuard(&isRunRetryCrawlRequest, crawlerRunFlags()...)
    if release == nil {
        return
    }
    defer release()
    ...
}
```

1. `scheduleGuard` với blocker là toàn bộ cờ crawler. Bỏ qua lượt nếu đang retry hoặc có crawler đang chạy.
2. Query `{retryStatus: "pending", nextRetryAt: {$lte: now}}`, sort `nextRetryAt` tăng dần, limit 100.
3. Với mỗi log:
   - Nếu `isAnyCrawlerRunning()` thì `break`.
   - Gọi `contentcatcher.RetryV2RequestLog(ctx, log)`, sau đó `time.Sleep(crawlRequestInterval)`.
   - `retryCount = log.RetryCount + 1`, rồi cập nhật log gốc:

| Kết quả | Cập nhật |
|---|---|
| HTTP 200 | `retryStatus=success`, `$unset nextRetryAt`. Nếu `err == nil` và có `request_id` thì `InsertContentCallback(log.URLs, requestId)` |
| HTTP khác 200 và `retryCount >= 3` | `retryStatus=failed`, `$unset nextRetryAt` |
| HTTP khác 200 và `retryCount < 3` | `nextRetryAt = now + 5p` |

Trường hợp HTTP 200 nhưng body `status` khác `success`: log gốc vẫn được đánh `success`, vì gửi lại không thay đổi kết quả, nhưng không tạo callback vì không có `request_id`.

`RetryFailedCrawlRequests` được thêm vào `ScheduleInterface`.

### 3.9 Index: `internal/module/database/mongodb/index.go`

```go
i.newIndex("retryStatus", "nextRetryAt"),
```

Thêm vào nhóm index của `crawl-request-logs`. Index được tạo khi khởi động (`CreateMany`), không cần migration.

## 4. Kiểm thử

| Test | Nội dung |
|---|---|
| `TestMarkV2RetryState/async lỗi 429` | `retryStatus=pending`, `nextRetryAt = createdAt + 5p` |
| `TestMarkV2RetryState/async lỗi mạng (HTTP 0)` | `pending` |
| `TestMarkV2RetryState/async thành công` | Không có field retry |
| `TestMarkV2RetryState/sync lỗi` | Không có field retry |
| `TestMarkV2RetryState/lần gửi lại lỗi` | Chỉ có `retryOf`, không `pending` |

```bash
cd backend
go test ./internal/module/social/content_catcher/ -run TestMarkV2RetryState -v
go build ./internal/... ./pkg/...
```

**Chưa có test** cho `RetryFailedCrawlRequests` và vòng lặp các job, vì cần MongoDB và gateway. **Chưa chạy thử với gateway thật.**

### Kiểm tra thủ công sau deploy

```js
// Hàng đợi retry hiện tại
db.getCollection("crawl-request-logs").find({ retryStatus: "pending" }).sort({ nextRetryAt: 1 })

// Thống kê kết quả retry
db.getCollection("crawl-request-logs").aggregate([
  { $match: { retryStatus: { $exists: true } } },
  { $group: { _id: "$retryStatus", total: { $sum: 1 } } }
])

// Các lần gửi lại của một log gốc
db.getCollection("crawl-request-logs").find({ retryOf: ObjectId("<id log gốc>") }).sort({ createdAt: 1 })

// Gateway còn trả 429 không
db.getCollection("crawl-request-logs").countDocuments({ httpStatus: 429, createdAt: { $gte: ISODate("<từ thời điểm deploy>") } })
```

API tra log có sẵn `GET /crawl-request-logs` (cần `key`) cũng trả về các field retry mới.

## 5. Biến môi trường

Không thêm biến mới. Vẫn dùng:

| Biến | Dùng cho |
|---|---|
| `CONTENT_CATCHER_V2_BASE_URL` | URL gateway |
| `CONTENT_CATCHER_V2_CLIENT_ID` | `client-id`, chữ ký HMAC |
| `CONTENT_CATCHER_V2_CLIENT_SECRET` | Khoá ký HMAC |

## 6. Rủi ro triển khai

### 6.1 Job chạy lấn sang khung của job sau

Mỗi job tối đa khoảng 600 URL/phút, tức khoảng 54.000 URL trong 1 tiếng rưỡi, chưa tính thời gian phản hồi. Platform nào nhiều content hơn sẽ chạy lấn sang khung kế tiếp. Các job crawl **không chặn lẫn nhau** (chỉ chặn chính nó), nên khi lấn thì hai job chạy song song, khoảng 2 request/giây, chạm đúng giới hạn 120 request/phút. Theo dõi log `Done run crawler ... with N requests at ...` của từng job.

### 6.2 `ProcessTiktokUnauthorized` không được tính là crawler

Hàm này chạy phút 50 mỗi giờ trong `ProcessContentCallback`, không có trong `crawlerRunFlags`. Nó có thể chạy cùng một job crawl, và job retry cũng không chờ nó.

### 6.3 Guard và giãn cách chỉ trong một process

Cờ guard nằm trong bộ nhớ. Admin (process riêng) và các replica public khác không biết nhau. Nếu public chạy nhiều replica, cron chạy trên mọi replica, và vấn đề này đã có từ trước.

### 6.4 Đổi `break` thành `continue` khi gateway sập

Khi gateway sập hẳn, job vẫn duyệt hết mọi batch (mỗi batch 1 giây cộng thời gian timeout) và tạo log `pending` cho từng batch. Hàng đợi retry phình ra, mỗi lượt retry xử lý 100 log. Sau 3 lần retry, các log này chuyển `failed`, và content được crawl lại ở lượt cron kế tiếp.

### 6.5 Token hết hạn khi retry

Retry dùng `access_token` lưu trong log gốc. Nếu token TikTok bị làm mới hoặc hết hạn trong lúc chờ retry, cả 3 lần retry có thể lỗi.

### 6.6 Log cũ

Log được tạo trước khi deploy không có `retryStatus`, nên không được retry.

## 7. Lịch sử commit

| Commit | Nội dung |
|---|---|
| `f86c8659` | Log request gửi gateway V2 (`crawl-request-logs`) và API search (có từ trước, là nền cho tính năng này) |
| `7f015ec6` | Giãn lịch crawl, sleep 1s/request, retry request lỗi |
| `d52dfea0` | Merge `feature/update-flow-crawl` vào `develop` |
