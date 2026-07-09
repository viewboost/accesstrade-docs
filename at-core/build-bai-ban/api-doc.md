# AT Core API Documentation

Tài liệu API cho partner tích hợp với AT Core.

**Base URL:** `https://api-at-core.diso.vn`
**Phiên bản:** v1
**Định dạng:** JSON

---

## Mục lục

1. [Authentication](#1-authentication)
2. [Enrich Profile](#2-enrich-profile)
3. [Job Status](#3-job-status)
4. [Webhook](#4-webhook)
5. [Error Codes](#5-error-codes)

---

## 1. Authentication

Mọi request tới `/v1/partners/*` phải kèm 2 header:

| Header | Giá trị |
|---|---|
| `X-Partner-ID` | Partner ID dạng MongoDB ObjectID hex (24 ký tự) |
| `X-API-Key` | API key dạng `at_prod_*` được AT cấp khi onboard |

Auth thất bại trả về:

```http
HTTP/1.1 401 Unauthorized
```
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid API key or partner ID"
  }
}
```

---

## 2. Enrich Profile

Gửi URL profile creator (Facebook / Instagram / TikTok / YouTube) để được enrich (lấy follower count, engagement, metadata...).

### Endpoint

```
POST /v1/partners/profiles/enrich
```

### Request

```json
{
  "url": "https://www.tiktok.com/@username",
  "category": "beauty",
  "visibility": "PUBLIC"
}
```

| Field | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `url` | string | ✅ | URL profile creator. Hỗ trợ FB / IG / TikTok / YouTube. |
| `category` | string | — | Phân loại creator (vd: `beauty`, `fashion`, `tech`). Mặc định auto-detect. |
| `visibility` | string | — | `PUBLIC` hoặc `PRIVATE`. Mặc định `PUBLIC`. |

### Response — `cached` (profile đã có trong pool, trả ngay)

```http
HTTP/1.1 200 OK
```
```json
{
  "jobId": "",
  "status": "completed",
  "mode": "cached",
  "profile": {
    "id": "65f1a2b3c4d5e6f7a8b9c0d1",
    "platform": "tiktok",
    "externalId": "@username",
    "name": "Username Display",
    "followersCount": 152340,
    "engagementRate": 4.2,
    "category": "beauty"
  }
}
```

### Response — `async` (profile mới, gửi xuống Vendor)

```http
HTTP/1.1 202 Accepted
```
```json
{
  "jobId": "65f1a2b3c4d5e6f7a8b9c0d1",
  "status": "submitted",
  "mode": "async"
}
```

Mode `async`: partner poll [GET /v1/partners/jobs/{id}](#3-job-status) hoặc nhận [Webhook](#4-webhook) khi job hoàn tất. Thời gian xử lý trung bình: 30 giây — 3 phút.

### cURL

```bash
curl -X POST https://api-at-core.diso.vn/v1/partners/profiles/enrich \
  -H "X-Partner-ID: 65f1a2b3c4d5e6f7a8b9c0d1" \
  -H "X-API-Key: at_prod_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.tiktok.com/@username",
    "category": "beauty"
  }'
```

---

## 3. Job Status

Poll trạng thái enrichment job khi mode = `async`.

### Endpoint

```
GET /v1/partners/jobs/{jobId}
```

### Response

```json
{
  "id": "65f1a2b3c4d5e6f7a8b9c0d1",
  "url": "https://www.tiktok.com/@username",
  "platform": "tiktok",
  "externalId": "@username",
  "status": "completed",
  "profileId": "65f1a2b3c4d5e6f7a8b9c0d2",
  "createdAt": "2026-06-08T10:00:00Z",
  "completedAt": "2026-06-08T10:02:15Z",
  "attempts": 1,
  "maxAttempts": 3
}
```

### Status

| Status | Ý nghĩa |
|---|---|
| `pending` | Job vừa tạo, chưa submit lên Vendor |
| `submitted` | Đã submit Vendor, chưa bắt đầu xử lý |
| `processing` | Vendor đang crawl |
| `completed` | Hoàn tất, đọc kết quả qua `profileId` |
| `failed` | Lỗi, xem `errorCode` + `errorMsg` |

---

## 4. Webhook

AT Core POST event tới `webhookUrl` của partner khi job hoàn tất. Yêu cầu: partner cấu hình `webhookUrl` + `webhookSecret` khi onboard.

### Event types

| Event | Khi nào |
|---|---|
| `job.completed` | Enrichment thành công |
| `job.failed` | Enrichment thất bại |

### Request AT Core gửi

```http
POST {webhookUrl} HTTP/1.1
Content-Type: application/json
User-Agent: AT-Core-Webhook/1.0
X-AT-Signature: sha256=8b94b3e2c1a4f5d6e7c8a9b0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0
X-AT-Timestamp: 1717840935
```

### Payload — `job.completed`

```json
{
  "event": "job.completed",
  "jobId": "65f1a2b3c4d5e6f7a8b9c0d1",
  "status": "completed",
  "profileId": "65f1a2b3c4d5e6f7a8b9c0d2",
  "partnerId": "65f1a2b3c4d5e6f7a8b9c0d3",
  "completedAt": "2026-06-08T10:02:15Z",
  "profile": {
    "platform": "tiktok",
    "externalId": "@username",
    "name": "Username Display",
    "followersCount": 152340,
    "engagementRate": 4.2,
    "avgViews": 25600,
    "totalViews": 8540000,
    "totalLikes": 450000
  }
}
```

### Payload — `job.failed`

```json
{
  "event": "job.failed",
  "jobId": "65f1a2b3c4d5e6f7a8b9c0d1",
  "status": "failed",
  "partnerId": "65f1a2b3c4d5e6f7a8b9c0d3",
  "errorCode": "CRAWL_FAILED",
  "errorMsg": "Profile is private or deleted"
}
```

### Verify HMAC signature

Thuật toán: `HMAC-SHA256` với `webhookSecret`, ký lên raw body.

#### Sample Go

```go
package webhook

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"strings"
)

func VerifySignature(secret string, body []byte, signatureHeader string) bool {
	if !strings.HasPrefix(signatureHeader, "sha256=") {
		return false
	}
	expected := strings.TrimPrefix(signatureHeader, "sha256=")

	mac := hmac.New(sha256.New, []byte(secret))
	mac.Write(body)
	actual := hex.EncodeToString(mac.Sum(nil))

	return hmac.Equal([]byte(expected), []byte(actual))
}
```

#### Sample TypeScript

```typescript
import crypto from "crypto";

function verifySignature(secret: string, body: string, header: string): boolean {
  if (!header.startsWith("sha256=")) return false;
  const expected = header.slice("sha256=".length);

  const actual = crypto
    .createHmac("sha256", secret)
    .update(body)
    .digest("hex");

  return crypto.timingSafeEqual(
    Buffer.from(expected, "hex"),
    Buffer.from(actual, "hex")
  );
}
```

### Retry

Nếu partner trả non-2xx hoặc timeout, AT Core retry tự động: `1m → 5m → 15m`. Sau 4 lần fail, đưa vào DLQ, admin AT retry thủ công.

Endpoint webhook partner phải **idempotent** (cùng `jobId` có thể nhận nhiều lần).

Yêu cầu trả `2xx` trong `≤ 10s`. Nếu xử lý lâu, acknowledge ngay rồi process async.

---

## 5. Error Codes

Format response lỗi:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description",
    "actions": ["suggested_action_1"]
  }
}
```

| Code | HTTP | Mô tả |
|---|---|---|
| `INVALID_URL` | 400 | URL không parse được hoặc platform không hỗ trợ |
| `MISSING_URL` | 400 | Thiếu field `url` |
| `INVALID_INPUT` | 400 | Body JSON malformed |
| `UNAUTHORIZED` | 401 | API key sai hoặc partner ID không tồn tại |
| `PROFILE_NOT_FOUND` | 404 | Profile không tồn tại trên platform |
| `DUPLICATE_PROFILE` | 409 | Profile đã có job đang chạy |
| `RATE_LIMITED` | 429 | Vượt rate limit hoặc quota tháng |
| `ENRICHMENT_FAILED` | 500 | Lỗi nội bộ |
| `ENCRYPTION_ERROR` | 500 | Lỗi nội bộ về encryption |
| `SERVICE_UNAVAILABLE` | 503 | Vendor tạm thời không khả dụng |
| `TIMEOUT` | 504 | Vendor không phản hồi trong thời gian giới hạn |
