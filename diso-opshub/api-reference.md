# OpsHub External API Reference

> Tài liệu hướng dẫn đấu nối với OpsHub - nền tảng quản lý duyệt content và social profile tập trung.
>
> **Base URL:** `https://opshub.example.com/api/v1`
>
> **Phiên bản:** v1 | **Cập nhật:** 2026-04-05

---

## Mục lục

1. [Tổng quan](#1-tổng-quan)
2. [Xác thực (Authentication)](#2-xác-thực-authentication)
3. [Rate Limiting](#3-rate-limiting)
4. [Response Format](#4-response-format)
5. [API Endpoints](#5-api-endpoints)
   - [Health Check](#51-health-check)
   - [Push Content](#52-push-content)
   - [Query Verdict](#53-query-verdict)
6. [Webhook Events (OpsHub → Partner)](#6-webhook-events-opshub--partner)
7. [Data Fields](#7-data-fields)
8. [Error Reference](#8-error-reference)
9. [Integration Checklist](#9-integration-checklist)

---

## 1. Tổng quan

OpsHub là nền tảng quản lý việc duyệt video và social profile với sự hỗ trợ của **AI Agent** và **human reviewer**. Các hệ thống đối tác (partner) đấu nối qua External API để:

1. **Push content** vào OpsHub để duyệt
2. **Nhận kết quả** qua webhook callback hoặc polling API

**Flow cơ bản:**

```
Partner push content → OpsHub xử lý & duyệt → Trả verdict về Partner
```

- Content gửi vào sẽ được OpsHub kiểm tra, đánh giá, và đưa ra kết quả duyệt (**approved** / **rejected**).
- Một số content có thể được quyết định ngay lập tức (trả kết quả trong response). Một số khác cần thời gian xử lý — kết quả sẽ gửi về qua webhook hoặc có thể polling.
- Mỗi partner được cấp **project code** và **API key** riêng biệt.

---

## 2. Xác thực (Authentication)

External API sử dụng **API Key** authentication qua HTTP headers.

### Headers bắt buộc

| Header | Mô tả | Ví dụ |
|--------|-------|-------|
| `X-Project-ID` | Project code được cấp bởi OpsHub admin | `your-project` |
| `X-API-Key` | API key (hiển thị 1 lần duy nhất khi tạo) | `opshub_prod_yourproject_a1b2c3d4e5...` |

### Ví dụ request

```bash
curl -X GET https://opshub.example.com/api/v1/external/health \
  -H "X-Project-ID: your-project" \
  -H "X-API-Key: opshub_prod_yourproject_a1b2c3d4e5f6..."
```

### Lưu ý bảo mật

- API key chỉ hiển thị **1 lần duy nhất** khi tạo hoặc rotate. Không thể recover.
- Key format: `opshub_{env}_{projectCode}_{random}`
- Nếu mất key, liên hệ OpsHub admin để **rotate** (tạo key mới, vô hiệu hóa key cũ).

### Lỗi xác thực

```json
// Thiếu headers
{
  "error": {
    "code": "MISSING_CREDENTIALS",
    "message": "X-Project-ID and X-API-Key headers are required"
  }
}

// Key sai hoặc project không khớp
{
  "error": {
    "code": "INVALID_API_KEY",
    "message": "Invalid API key or project mismatch"
  }
}
```

---

## 3. Rate Limiting

| Giới hạn | Window | Scope |
|----------|--------|-------|
| **100 requests/phút** (mặc định, có thể thay đổi theo project) | Sliding window 60s | Per project |

### Response headers

| Header | Mô tả |
|--------|-------|
| `X-RateLimit-Limit` | Tổng số request cho phép trong window |
| `X-RateLimit-Remaining` | Số request còn lại |
| `X-RateLimit-Reset` | Unix timestamp khi window reset |

### Khi bị rate limit

```
HTTP 429 Too Many Requests
Retry-After: 60
```

```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Too many requests for this project. Please try again later.",
    "retryAfter": 60
  }
}
```

---

## 4. Response Format

### Success

```json
{
  "data": { ... }
}
```

### Error

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Mô tả lỗi",
    "details": { ... }
  }
}
```

### HTTP Status Codes

| Code | Ý nghĩa |
|------|----------|
| `200` | Thành công — kết quả duyệt đã được quyết định ngay |
| `202` | Accepted — content đang được xử lý, chờ kết quả qua webhook hoặc polling |
| `400` | Validation error |
| `401` | Chưa xác thực / key sai |
| `404` | Không tìm thấy resource |
| `429` | Rate limited |
| `500` | Server error |

---

## 5. API Endpoints

### 5.1. Health Check

Kiểm tra kết nối và xác thực API key.

```
GET /api/v1/external/health
```

**Response 200:**

```json
{
  "data": {
    "status": "ok",
    "project": "Your Project Name",
    "timestamp": "2026-04-05T10:30:00.000Z"
  }
}
```

---

### 5.2. Push Content

Gửi content (video, social post) vào OpsHub để duyệt.

```
POST /api/v1/external/videos
```

#### Request Body

| Field | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `campaign_id` | `string` | **Có** | Campaign ID phía partner **hoặc** OpsHub ObjectId. OpsHub tự map qua `source_campaign_id` đã đăng ký. |
| `source_id` | `string` | **Có** | ID duy nhất của content trong hệ thống partner. Dùng để dedup — push cùng `source_id` sẽ update thay vì tạo mới. |
| `data` | `object` | Không | Metadata của content (xem [mục 7](#7-data-fields)) |
| `media_refs` | `array` | Không | Tham chiếu tới file media trên storage (MinIO/S3) |

#### `data` object — các fields chính

| Field | Type | Mô tả |
|-------|------|-------|
| `platform` | `string` | Platform của content: `tiktok`, `facebook`, `instagram`, `youtube`, `threads`, `shopee` |
| `media_type` | `string` | Loại content: `video`, `reel`, `post_images`, `livestream` |
| `source` | `string` | Compound platform string (e.g. `facebook_reels`). Nếu gửi field này, OpsHub tự tách thành `platform` + `media_type`. |
| `title` | `string` | Tiêu đề content |
| `caption` | `string` | Mô tả / caption |
| `duration` | `number` | Thời lượng video (giây) |
| `view_count` | `number` | Lượt xem |
| `like_count` | `number` | Lượt like |
| `comment_count` | `number` | Lượt comment |
| `share_count` | `number` | Lượt share |
| `hashtags` | `string[]` | Danh sách hashtags |
| `platform_content_id` | `string` | ID content trên social platform |
| `published_at` | `string` | Ngày đăng (ISO 8601) |
| `content_url` | `string` | URL content gốc trên platform |
| `creator_name` | `string` | Tên creator |
| `creator_followers` | `number` | Số followers của creator |

> **Lưu ý:** OpsHub cũng hỗ trợ một số field alias phổ biến (xem [mục 7](#7-data-fields)).

#### `media_refs[]` array

| Field | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `type` | `string` | **Có** | `"video"`, `"image"`, `"document"`, `"avatar"` |
| `source_bucket` | `string` | **Có** | Tên bucket trên storage |
| `source_key` | `string` | **Có** | Object key trong bucket |
| `content_type` | `string` | **Có** | MIME type, e.g. `"video/mp4"` |
| `size_bytes` | `number` | Không | Kích thước file (bytes) |
| `thumbnail_key` | `string` | Không | Object key của thumbnail |

#### Ví dụ request

```bash
curl -X POST https://opshub.example.com/api/v1/external/videos \
  -H "X-Project-ID: your-project" \
  -H "X-API-Key: opshub_prod_yourproject_..." \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "my-campaign-q2-2026",
    "source_id": "video-12345",
    "data": {
      "platform": "tiktok",
      "media_type": "video",
      "title": "Review san pham XYZ",
      "caption": "San pham chat luong cao #ThuongHieu #Review",
      "duration": 45,
      "view_count": 15000,
      "like_count": 1200,
      "comment_count": 85,
      "share_count": 30,
      "hashtags": ["#ThuongHieu", "#Review", "#SanPham"],
      "platform_content_id": "7345678901234567890",
      "published_at": "2026-04-01T08:30:00Z",
      "content_url": "https://tiktok.com/@creator/video/7345678901234567890",
      "creator_name": "Creator ABC",
      "creator_followers": 50000
    },
    "media_refs": [
      {
        "type": "video",
        "source_bucket": "partner-videos",
        "source_key": "campaigns/q2-2026/video-12345.mp4",
        "content_type": "video/mp4",
        "size_bytes": 15728640,
        "thumbnail_key": "campaigns/q2-2026/thumbs/video-12345.jpg"
      }
    ]
  }'
```

#### Response: Quyết định ngay (200)

Khi OpsHub có thể quyết định ngay lập tức:

```json
{
  "data": {
    "sync_entity_id": "661a2b3c4d5e6f7a8b9c0d1e",
    "processing_record_id": "661a2b3c4d5e6f7a8b9c0d2f",
    "outcome": "auto_rejected",
    "outcome_reason": "Wrong platform: snapchat",
    "auto_checks_count": 1,
    "duration_ms": 45
  }
}
```

#### Response: Cần xử lý thêm (202)

Khi content cần thời gian đánh giá:

```json
{
  "data": {
    "sync_entity_id": "661a2b3c4d5e6f7a8b9c0d1e",
    "processing_record_id": "661a2b3c4d5e6f7a8b9c0d2f",
    "outcome": "needs_review",
    "outcome_reason": "Content is being reviewed",
    "task_id": "661a2b3c4d5e6f7a8b9c0d3g",
    "auto_checks_count": 8,
    "duration_ms": 120
  }
}
```

#### Các kịch bản outcome

| `outcome` | HTTP | Ý nghĩa | Hành động tiếp theo |
|-----------|------|----------|---------------------|
| `auto_approved` | 200 | Content được duyệt ngay | **Xong.** |
| `auto_rejected` | 200 | Content bị từ chối ngay (không đạt tiêu chí cơ bản) | **Xong.** |
| `needs_review` | 202 | Content đang được đánh giá | Đợi webhook callback hoặc poll `GET /verdicts/:id` |

#### Idempotency

- Push cùng `source_id` sẽ **update** content thay vì tạo mới.
- Mỗi lần push sẽ tạo **processing record mới** (lịch sử xử lý được giữ lại).

---

### 5.3. Query Verdict

Tra cứu trạng thái duyệt của một content. Có thể truyền `processing_record_id` hoặc `task_id` (nhận từ response push content).

```
GET /api/v1/external/verdicts/:id
```

| Param | Type | Mô tả |
|-------|------|-------|
| `id` | `string` | `processing_record_id` hoặc `task_id` (ObjectId) |

#### Response: Đang xử lý

```json
{
  "data": {
    "processing_record_id": "661a2b3c4d5e6f7a8b9c0d2f",
    "outcome": "needs_review",
    "outcome_reason": "Content is being reviewed",
    "task_id": "661a2b3c4d5e6f7a8b9c0d3g",
    "task_status": "in_progress",
    "verdict": null
  }
}
```

#### Response: Đã có kết quả

```json
{
  "data": {
    "processing_record_id": "661a2b3c4d5e6f7a8b9c0d2f",
    "outcome": "needs_review",
    "outcome_reason": "Content is being reviewed",
    "task_id": "661a2b3c4d5e6f7a8b9c0d3g",
    "task_status": "completed",
    "verdict": {
      "final_decision": "approved",
      "confidence": 0.92,
      "reason": "Content meets all brand guidelines",
      "feedback_to_creator": "Good content quality. Consider adding more product close-ups.",
      "decided_at": "2026-04-05T11:45:00.000Z"
    }
  }
}
```

#### Verdict fields

| Field | Type | Mô tả |
|-------|------|-------|
| `final_decision` | `string` | Quyết định cuối cùng: `"approved"` hoặc `"rejected"` |
| `confidence` | `number` | Độ tin cậy (0-1) |
| `reason` | `string` | Lý do quyết định |
| `feedback_to_creator` | `string` | Feedback gửi cho creator (nếu có) |
| `decided_at` | `string` | Thời điểm quyết định (ISO 8601) |

#### Task status values

| Status | Ý nghĩa |
|--------|----------|
| `pending` | Chờ xử lý |
| `assigned` | Đã phân công |
| `in_progress` | Đang đánh giá |
| `review` | Đang xem xét kết quả |
| `completed` | Hoàn thành — xem `verdict.final_decision` |
| `cancelled` | Đã hủy |

---

## 6. Webhook Events (OpsHub → Partner)

Khi có kết quả xử lý, OpsHub gọi webhook về URL mà partner đã đăng ký. Webhook được gửi cho cả kết quả tự động (auto checks) lẫn kết quả duyệt thủ công/AI.

### Đăng ký webhook

Webhook được đăng ký bởi OpsHub admin. Liên hệ OpsHub admin để cung cấp webhook URL và chọn event types.

**Event types có thể đăng ký:**

| Event | Khi nào | Ghi chú |
|-------|---------|---------|
| `pipeline.auto_approved` | Content pass tất cả auto checks, được duyệt t��� động | Không có `verdict` object, có `outcome` + `outcome_reason` |
| `pipeline.auto_rejected` | Content fail auto check critical (sai platform, format, hashtag...) | Không có `task_id` (task chưa được tạo) |
| `verdict.approved` | Content được duyệt bởi human reviewer hoặc AI agent | Có đầy đủ `verdict` object |
| `verdict.rejected` | Content bị từ chối bởi human reviewer hoặc AI agent | Có đầy đủ `verdict` object |
| `verdict.request_edit` | Reviewer yêu cầu creator sửa content | Có `verdict` với `reason` + `feedback_to_creator` |
| `task.sla_violated` | Task review quá hạn SLA | Có `sla_deadline` + `breached_at` |

### Webhook Request Format

OpsHub gửi `POST` request tới webhook URL đã đăng ký:

```
POST https://your-system.example.com/webhooks/opshub
```

#### Headers

| Header | Mô tả |
|--------|-------|
| `Content-Type` | `application/json` |
| `X-Project-ID` | Project code của partner |
| `X-OpsHub-Event` | Event type (e.g. `verdict.approved`) |
| `X-OpsHub-Timestamp` | Unix timestamp (seconds) |
| `X-OpsHub-Delivery-ID` | ID duy nhất của lần delivery (dùng để dedup) |

#### Body — Verdict events (`verdict.approved`, `verdict.rejected`, `verdict.request_edit`)

```json
{
  "event": "verdict.approved",
  "task_id": "661a2b3c4d5e6f7a8b9c0d3g",
  "processing_record_id": "661a2b3c4d5e6f7a8b9c0d2f",
  "sync_entity_id": "661a2b3c4d5e6f7a8b9c0d1e",
  "source_id": "video-12345",
  "verdict": {
    "final_decision": "approved",
    "confidence": 0.92,
    "reason": "Content meets all brand guidelines",
    "feedback_to_creator": "Good content quality.",
    "decided_at": "2026-04-05T11:45:00.000Z"
  },
  "timestamp": "2026-04-05T11:45:01.000Z",
  "project": "your-project",
  "delivered_at": "2026-04-05T11:45:02.000Z"
}
```

| Field | Type | Mô tả |
|-------|------|-------|
| `event` | `string` | Event type |
| `task_id` | `string` | Task ID (ObjectId) |
| `processing_record_id` | `string` | Processing record ID |
| `sync_entity_id` | `string` | SyncEntity ID |
| `source_id` | `string` | ID content gốc của partner (đã push qua `POST /external/videos`) |
| `verdict.final_decision` | `string` | `"approved"` hoặc `"rejected"` |
| `verdict.confidence` | `number` | Độ tin cậy 0-1 (chủ yếu từ AI review) |
| `verdict.reason` | `string` | Lý do quyết định |
| `verdict.feedback_to_creator` | `string?` | Feedback gửi cho creator (nếu có) |
| `verdict.decided_at` | `string` | Thời điểm quyết định (ISO 8601) |
| `timestamp` | `string` | Thời điểm tạo webhook event (ISO 8601) |
| `project` | `string` | Project code |
| `delivered_at` | `string` | Thời điểm delivery (ISO 8601) |

#### Body — Pipeline events (`pipeline.auto_approved`, `pipeline.auto_rejected`)

```json
{
  "event": "pipeline.auto_rejected",
  "sync_entity_id": "661a2b3c4d5e6f7a8b9c0d1e",
  "processing_record_id": "661a2b3c4d5e6f7a8b9c0d2f",
  "source_id": "video-12345",
  "campaign_id": "661a2b3c4d5e6f7a8b9c0e4h",
  "outcome": "auto_rejected",
  "outcome_reason": "Wrong platform: snapchat",
  "timestamp": "2026-04-05T10:30:00.000Z",
  "project": "your-project",
  "delivered_at": "2026-04-05T10:30:01.000Z"
}
```

| Field | Type | Mô tả |
|-------|------|-------|
| `event` | `string` | `pipeline.auto_approved` hoặc `pipeline.auto_rejected` |
| `sync_entity_id` | `string` | SyncEntity ID |
| `processing_record_id` | `string` | Processing record ID |
| `source_id` | `string` | ID content gốc của partner |
| `campaign_id` | `string` | Campaign ID |
| `outcome` | `string` | `"auto_approved"` hoặc `"auto_rejected"` |
| `outcome_reason` | `string` | Lý do (e.g. `"Wrong platform: snapchat"`, `"All auto checks passed"`) |
| `timestamp` | `string` | ISO 8601 |

> **Lưu ý:** Pipeline events **không có** `task_id` và `verdict` object vì task chưa được tạo ở giai đoạn auto check.

#### Body — SLA event (`task.sla_violated`)

```json
{
  "event": "task.sla_violated",
  "task_id": "661a2b3c4d5e6f7a8b9c0d3g",
  "processing_record_id": "661a2b3c4d5e6f7a8b9c0d2f",
  "sync_entity_id": "661a2b3c4d5e6f7a8b9c0d1e",
  "source_id": "video-12345",
  "sla_deadline": "2026-04-05T10:00:00.000Z",
  "breached_at": "2026-04-05T10:00:00.000Z",
  "timestamp": "2026-04-05T10:05:00.000Z",
  "project": "your-project",
  "delivered_at": "2026-04-05T10:05:01.000Z"
}
```

| Field | Type | Mô tả |
|-------|------|-------|
| `sla_deadline` | `string` | H��n SLA đã quá (ISO 8601) |
| `breached_at` | `string` | Thời điểm SLA bị vi phạm (= `sla_deadline`) |

### Retry Policy

| Setting | Giá trị |
|---------|---------|
| Timeout | 10 giây |
| Max retries | 5 (production), 3 (staging/dev) |
| Backoff | Exponential: ~1m → ~2m → ~4m → ~8m → ~16m |

Webhook delivery là **at-least-once** — hệ thống partner cần handle duplicate deliveries (dùng `X-OpsHub-Delivery-ID` để dedup).

### Response mong đợi

Webhook endpoint của partner cần trả về HTTP `2xx` để OpsHub ghi nhận delivery thành công. Bất kỳ status nào khác → OpsHub retry theo policy trên.

---

## 7. Data Fields

### Các fields chuẩn (khuyến nghị)

| Field | Type | Mô tả |
|-------|------|-------|
| `platform` | `string` | `tiktok`, `facebook`, `instagram`, `youtube`, `threads`, `shopee` |
| `media_type` | `string` | `video`, `reel`, `post_images`, `livestream` |
| `caption` | `string` | Mô tả / caption |
| `duration` | `number` | Thời lượng (giây) |
| `view_count` | `number` | Lượt xem |
| `like_count` | `number` | Lượt like |
| `comment_count` | `number` | Lượt comment |
| `share_count` | `number` | Lượt share |
| `hashtags` | `string[]` | Danh sách hashtags |
| `platform_content_id` | `string` | ID content trên social platform |
| `published_at` | `string` | Ngày đăng (ISO 8601) |
| `content_url` | `string` | URL content gốc trên platform |

### Field aliases được hỗ trợ

OpsHub cũng chấp nhận một số alias phổ biến. Nếu field chuẩn chưa được set, alias sẽ tự động map:

| Alias | Mapped thành |
|-------|-------------|
| `desc` | `caption` |
| `duration_seconds` | `duration` |
| `view` | `view_count` |
| `like` | `like_count` |
| `comment` | `comment_count` |
| `share` | `share_count` |
| `hash_tag` | `hashtags` |
| `content_id` | `platform_content_id` |
| `publish_at` | `published_at` |
| `link` | `content_url` |

### Compound `source` field

Nếu partner gửi field `source` dạng compound string, OpsHub tự động tách thành `platform` + `media_type`:

| `source` value | `platform` | `media_type` |
|----------------|-----------|-------------|
| `tiktok` | `tiktok` | `video` |
| `facebook` | `facebook` | `video` |
| `facebook_reels` | `facebook` | `reel` |
| `instagram` | `instagram` | `post_images` |
| `instagram_reels` | `instagram` | `reel` |
| `youtube` | `youtube` | `video` |
| `youtube_shorts` | `youtube` | `reel` |
| `threads` | `threads` | `post_images` |
| `shopee` | `shopee` | `post_images` |

> Nếu `platform` và `media_type` đã được set trực tiếp trong `data`, chúng được ưu tiên hơn `source`.

---

## 8. Error Reference

| Code | HTTP | Mô tả |
|------|------|-------|
| `MISSING_CREDENTIALS` | 401 | Thiếu `X-Project-ID` hoặc `X-API-Key` header |
| `INVALID_API_KEY` | 401 | API key sai hoặc project không khớp |
| `VALIDATION_ERROR` | 400 | Request body không hợp lệ (thiếu `campaign_id`, `source_id`...) |
| `CAMPAIGN_NOT_FOUND` | 404 | Không tìm thấy campaign tương ứng trong OpsHub |
| `NOT_FOUND` | 404 | Không tìm thấy resource được yêu cầu |
| `PIPELINE_ERROR` | 500 | Lỗi xử lý nội bộ |
| `QUERY_FAILED` | 500 | Lỗi khi query verdict |
| `RATE_LIMITED` | 429 | Vượt quá giới hạn request |
| `INTERNAL_ERROR` | 500 | Lỗi server không xác định |

### Ví dụ lỗi thường gặp

```json
// Campaign chưa được setup trên OpsHub
{
  "error": {
    "code": "CAMPAIGN_NOT_FOUND",
    "message": "No campaign found for \"unknown-campaign\" in project \"your-project\""
  }
}

// Thiếu required field
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "campaign_id is required"
  }
}
```

---

## 9. Integration Checklist

### Chuẩn bị

- [ ] Nhận `X-Project-ID` và `X-API-Key` từ OpsHub admin
- [ ] Xác nhận campaign đã được tạo trên OpsHub (với `source_campaign_id` khớp với campaign ID phía partner)
- [ ] Cung cấp webhook URL cho OpsHub admin (nếu muốn nhận callback)

### Implement push flow

- [ ] Gọi `GET /external/health` để test kết nối
- [ ] Implement `POST /external/videos` với đầy đủ metadata
- [ ] Xử lý response: phân biệt `200` (quyết định ngay) và `202` (đang xử lý)
- [ ] Lưu `processing_record_id` và `task_id` (nếu có) để tra cứu sau

### Implement callback flow

- [ ] Implement webhook endpoint nhận `POST` request từ OpsHub
- [ ] Handle duplicate deliveries (idempotent, dùng `X-OpsHub-Delivery-ID`)
- [ ] Trả về HTTP `2xx` khi nhận webhook thành công
- [ ] (Optional) Implement `GET /external/verdicts/:id` để polling fallback

### Testing

- [ ] Test kết nối: `GET /external/health` → `200`
- [ ] Test push content hợp lệ → expect `200` hoặc `202`
- [ ] Test push content sai platform/format → expect `200` + `auto_rejected`
- [ ] Test sai API key → expect `401`
- [ ] Test rate limiting → expect `429` sau khi vượt giới hạn
- [ ] Test webhook nhận callback khi có kết quả duyệt
- [ ] Test idempotency: push cùng `source_id` 2 lần → content được update, không duplicate
