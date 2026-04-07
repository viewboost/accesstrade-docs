# Hướng dẫn tích hợp OpsHub — Dành cho Developer

**Cập nhật:** 2026-04-07

---

## Tổng quan

Hệ thống của bạn gửi video lên OpsHub để kiểm duyệt, nhận kết quả về qua webhook. Toàn bộ tích hợp là backend-to-backend, không cần thay đổi UI phía creator.

**Flow:**

1. Hệ thống bạn gọi API push video lên OpsHub
2. OpsHub xử lý (kiểm tra tự động + AI phân tích)
3. OpsHub gọi webhook về hệ thống bạn với kết quả duyệt

---

## 1. Chuẩn bị

### Thông tin cần nhận từ OpsHub Admin

| Thông tin | Mô tả | Ví dụ |
|-----------|-------|-------|
| `BASE_URL` | URL OpsHub API | `https://opshub-api.example.com` |
| `PROJECT_ID` | Mã project của bạn trên OpsHub | `gengreen` |
| `API_KEY` | API key để xác thực khi push video | `opk_abc123...` |
| `WEBHOOK_API_KEY` | API key OpsHub gửi kèm khi gọi webhook về | `whk_xyz789...` |
| `CAMPAIGN_ID` | ObjectID của campaign trên OpsHub | `69c1a2b3...` |

### Environment Variables

```env
OPSHUB_IS_ENABLE=true
OPSHUB_BASE_URL=https://opshub-api.example.com
OPSHUB_PROJECT_ID=gengreen
OPSHUB_API_KEY=opk_abc123...
OPSHUB_WEBHOOK_API_KEY=whk_xyz789...
```

---

## 2. Push Video lên OpsHub

### API Endpoint

```
POST {BASE_URL}/api/v1/external/videos
```

### Headers

| Header | Giá trị |
|--------|---------|
| `Content-Type` | `application/json` |
| `X-API-Key` | API key được cấp |
| `X-Project-ID` | Mã project |

### Request Body

```json
{
  "campaign_id": "69c1a2b3...",
  "source_id": "id-của-content-trong-hệ-thống-bạn",
  "data": {
    "source": "tiktok_video",
    "content_id": "7123456789",
    "link": "https://tiktok.com/@user/video/7123456789",
    "desc": "Caption của video...",
    "hash_tag": ["#xanhsm", "#dichuyendien"],
    "creator_hashtag": "#nguyenvana",
    "event_hashtag": ["#xanhsm", "#gogreen"],
    "duration": 45,
    "view": 12500,
    "like": 350,
    "comment": 28,
    "share": 15,
    "publish_at": "2026-04-01T10:30:00Z",
    "author": "nguyenvana",
    "follower_count": 50000,
    "title": "Trải nghiệm Xanh SM lần đầu",
    "cover": "https://example.com/cover.jpg"
  }
}
```

### Các field quan trọng

| Field | Bắt buộc | Mô tả |
|-------|----------|-------|
| `campaign_id` | Có | ObjectID campaign trên OpsHub |
| `source_id` | Có | ID content trong hệ thống bạn (dùng để match khi nhận webhook) |
| `data.source` | Có | Platform + format: `tiktok_video`, `facebook_reels`, `youtube_video`, `instagram_reels` |
| `data.link` | Có | URL trực tiếp đến video (AI cần xem video qua link này) |
| `data.desc` | Nên có | Caption — AI kiểm tra nội dung caption |
| `data.hash_tag` | Nên có | Mảng hashtag — kiểm tra hashtag bắt buộc/cấm |
| `data.duration` | Nên có | Thời lượng video (giây) — kiểm tra min/max duration |
| `data.view` | Nên có | Lượt xem — kiểm tra min views |
| `data.follower_count` | Nên có | Follower của creator — kiểm tra min followers |
| `data.publish_at` | Nên có | Thời gian đăng — kiểm tra tần suất đăng bài |

### Response

```json
{
  "code": 1,
  "data": {
    "sync_entity_id": "69d12345...",
    "processing_record_id": "69d12346...",
    "outcome": "ai_processing",
    "outcome_reason": "AI review dispatched",
    "auto_checks_count": 8,
    "duration_ms": 245
  },
  "message": "Success"
}
```

**Lưu ý về `outcome`:**

| Outcome | Nghĩa | Cần làm gì? |
|---------|-------|-------------|
| `auto_rejected` | Tier 1 reject ngay (sai platform, sai format...) | Content bị từ chối, không cần đợi webhook |
| `ai_processing` | Đang chờ AI phân tích (~30 giây) | Đợi webhook trả kết quả cuối cùng |
| `auto_approved` | Duyệt ngay (chỉ khi không có AI checks) | Content đã duyệt |

### Khi nào push video?

- Push ngay khi content mới được crawl/submit
- Có thể push lại cùng `source_id` — OpsHub sẽ tạo processing record mới (không trùng)
- Nếu OpsHub không response hoặc lỗi, retry sau 30 giây (max 3 lần)

---

## 3. Nhận kết quả qua Webhook

### Setup webhook trên OpsHub

Nhờ OpsHub Admin tạo webhook cho project của bạn, trỏ về endpoint bạn chuẩn bị:

```
URL: https://api.gen-green.global/webhook/opshub
Events: pipeline.auto_approved, pipeline.auto_rejected, verdict.approved, verdict.rejected, verdict.request_edit
```

### Webhook endpoint của bạn

Tạo 1 endpoint POST nhận webhook từ OpsHub:

```
POST /webhook/opshub
```

### Xác thực webhook

OpsHub gửi kèm headers:

| Header | Mô tả |
|--------|-------|
| `X-OpsHub-Event` | Tên event (`pipeline.auto_rejected`, `verdict.approved`...) |
| `X-OpsHub-Delivery-ID` | ID delivery (dùng để dedup) |
| `X-OpsHub-Timestamp` | Thời gian gửi |
| `X-API-Key` | Webhook API key — so sánh với `WEBHOOK_API_KEY` đã cấu hình |

Bước đầu tiên: kiểm tra `X-API-Key` có khớp không. Nếu không → trả 401.

### Webhook Payload — Pipeline Events

Khi AI/hệ thống tự quyết định (không qua người duyệt):

```json
{
  "event": "pipeline.auto_rejected",
  "processing_record_id": "69d12346...",
  "source_id": "id-content-của-bạn",
  "reason": "Critical fail: A3_duration: Duration 23s < min 30s",
  "timestamp": "2026-04-07T04:16:47Z",
  "sync_entity_id": "69d12345...",
  "campaign_id": "69c1a2b3...",
  "outcome": "auto_rejected",
  "summary": "Video bị từ chối vì thời lượng chỉ 23 giây, yêu cầu tối thiểu 30 giây.",
  "verdict": {
    "final_decision": "rejected",
    "reason": "Critical fail: A3_duration: Duration 23s < min 30s",
    "summary": "Video bị từ chối vì thời lượng chỉ 23 giây, yêu cầu tối thiểu 30 giây.",
    "decided_by": "ai",
    "decided_at": "2026-04-07T04:16:47Z"
  }
}
```

### Webhook Payload — Verdict Events

Khi người kiểm duyệt ra quyết định:

```json
{
  "event": "verdict.rejected",
  "task_id": "69d214130...",
  "processing_record_id": "69d12346...",
  "sync_entity_id": "69d12345...",
  "source_id": "id-content-của-bạn",
  "verdict": {
    "final_decision": "rejected",
    "confidence": 1,
    "reason": "Nội dung không đề cập đến thông điệp chính của campaign",
    "feedback_to_creator": "Video chưa nhắc đến chương trình miễn phí đổi pin",
    "decided_at": "2026-04-07T10:30:00Z"
  },
  "summary": "Video bị từ chối bởi người kiểm duyệt. Lý do: nội dung không đề cập đến thông điệp chính.",
  "timestamp": "2026-04-07T10:30:00Z"
}
```

### Xử lý webhook — Cách đơn giản nhất

1. Parse `source_id` → tìm content trong DB của bạn
2. Đọc `verdict.final_decision` → `"approved"` hoặc `"rejected"`
3. Cập nhật trạng thái content
4. Lưu `verdict` object vào content để tham chiếu sau
5. (Tùy chọn) Đọc `summary` để hiển thị lý do cho người dùng

```
Nhận webhook
  → Parse source_id → Tìm content
  → verdict.final_decision == "approved" → Duyệt content
  → verdict.final_decision == "rejected" → Từ chối content, lưu summary làm lý do
  → Trả 200 OK
```

### Các event cần xử lý

| Event | Nghĩa | Hành động |
|-------|-------|-----------|
| `pipeline.auto_approved` | Hệ thống tự duyệt | Cập nhật content → approved |
| `pipeline.auto_rejected` | Hệ thống tự từ chối | Cập nhật content → rejected |
| `verdict.approved` | Người duyệt → duyệt | Cập nhật content → approved |
| `verdict.rejected` | Người duyệt → từ chối | Cập nhật content → rejected |
| `verdict.request_edit` | Yêu cầu chỉnh sửa | Thông báo creator sửa lại |
| `task.sla_violated` | Quá hạn SLA | Cảnh báo (không thay đổi trạng thái) |

### Response

Trả `200 OK` với body bất kỳ để xác nhận đã nhận. OpsHub sẽ retry tối đa 3 lần nếu không nhận được 2xx.

---

## 4. Polling Fallback (không bắt buộc)

Nếu webhook fail, có thể query kết quả:

```
GET {BASE_URL}/api/v1/external/videos/{source_id}/verdict
Headers: X-API-Key, X-Project-ID
```

---

## 5. Checklist tích hợp

- [ ] Cấu hình env vars (BASE_URL, API_KEY, PROJECT_ID, WEBHOOK_API_KEY)
- [ ] Implement push video khi content mới
- [ ] Implement webhook endpoint nhận kết quả
- [ ] Xác thực webhook bằng API key
- [ ] Xử lý các event types (approved, rejected, request_edit)
- [ ] Cập nhật trạng thái content dựa trên verdict
- [ ] Lưu verdict object vào content record
- [ ] Test end-to-end: push 1 video → nhận webhook → verify trạng thái
- [ ] Xử lý retry khi push fail
- [ ] (Tùy chọn) Implement polling fallback

---

*Tài liệu kỹ thuật API đầy đủ: [api-reference.md](api-reference.md)*
