# PRD: Tích hợp OpsHub vào vCreator

**Ngày:** 2026-04-05
**Phiên bản:** 1.0
**Tác giả:** Product Manager (AI-assisted)
**Trạng thái:** Draft

---

## 1. Executive Summary

Tích hợp hệ thống duyệt content tập trung OpsHub vào vCreator backend, cho phép tự động hóa quy trình kiểm duyệt video/content từ creator trước khi được tính thưởng. Hệ thống kết hợp AI Agent và human reviewer để xử lý **10.000+ video/tháng** với đội ngũ human tối thiểu, giảm sai sót và tăng tốc độ duyệt so với quy trình thủ công hiện tại.

**Scope:** Backend-to-backend integration only. Admin UI và Creator-facing UI đã có sẵn, chỉ cần cập nhật data source.

---

## 2. Business Objectives

| # | Objective | Đo lường | Target |
|---|-----------|----------|--------|
| **O1** | Giảm manual review, giảm nhân sự human | % content auto-decided (không cần human) | >= 60% auto-decided |
| **O2** | Giảm sai sót trong duyệt content | Tỷ lệ false positive/negative so với audit random | < 5% error rate |
| **O3** | Tăng tốc độ duyệt | Thời gian trung bình từ submit → verdict | < 2 phút (auto), < 24h (human) |
| **O4** | Scale lên 10K video/tháng | Throughput ổn định không cần tăng headcount | 10K video/tháng, 2-3 human reviewers |

---

## 3. Success Metrics

| Metric | Baseline (hiện tại) | Target (sau tích hợp) |
|--------|---------------------|----------------------|
| Thời gian duyệt trung bình | Manual: 2-5 phút/video | Auto: < 2s, AI: < 30s, Human: < 24h |
| % content cần human review | 100% (tất cả manual) | < 40% |
| Số human reviewer cần thiết cho 10K video/tháng | 5-8 người | 2-3 người |
| Tỷ lệ sai sót (miss violation) | Không đo được | < 5% |
| Content bị stuck (không có verdict) | N/A | < 1% |

---

## 4. User Personas

| Persona | Vai trò | Liên quan đến tích hợp này |
|---------|---------|---------------------------|
| **vCreator System** | Backend service tự động push content | Actor chính — gọi OpsHub API, nhận webhook |
| **Campaign Admin** | Quản lý campaign, bật/tắt OpsHub per event | Config `isEnableOpsHub` trên event (đã có) |
| **OpsHub Admin** | Setup project, API key, campaign mapping, review template | Phía OpsHub — ngoài scope implement |
| **Creator** | Submit content trên vCreator | Không bị ảnh hưởng trực tiếp — content vẫn publish bình thường |

---

## 5. Scope

### In Scope

- vCreator backend push content sang OpsHub khi content mới được crawl
- Nhận kết quả duyệt qua webhook callback từ OpsHub
- Polling fallback khi webhook fail
- Cập nhật trạng thái content trong MongoDB dựa trên verdict
- Retry logic cho push failures
- Scheduled sync cho content chưa được push (catch-up)
- Config per event (bật/tắt OpsHub integration)

### Out of Scope

- Xây dựng/thay đổi OpsHub (đã có sẵn)
- Thay đổi Admin UI vCreator (đã có sẵn)
- Thay đổi Creator-facing UI (đã có sẵn)
- Chặn publish content (content vẫn publish bình thường, duyệt chạy song song)
- Multi-tenant / multi-country OpsHub (phase sau)

---

## 6. Functional Requirements

### FR-001: Push Content sang OpsHub

**Priority:** Must Have

**Description:**
Khi content mới được crawl thành công từ social platform (qua Content Catcher), vCreator tự động gửi content data sang OpsHub qua `POST /api/v1/external/videos` nếu event có bật `isEnableOpsHub`.

**Acceptance Criteria:**
- [ ] Content được push ngay sau khi crawl thành công (trong cùng flow xử lý)
- [ ] Payload bao gồm: `campaign_id` (event ObjectId), `source_id` (content ObjectId), `data` (metadata từ ContentRaw)
- [ ] Data fields mapping đúng: `Source` → `source`, `Desc` → `desc`, `View` → `view`, `Like` → `like`, `Comment` → `comment`, `Duration` → `duration`, `HashTag` → `hash_tag`, `Link` → `link`, `PublishAt` → `publish_at`
- [ ] Gửi thêm `creator_id`, `follower_count`, `is_public` nếu có
- [ ] Chỉ push khi `event.Options.IsEnableOpsHub == true`
- [ ] Đánh dấu `isSendOpsHub = true` khi push thành công
- [ ] Ghi log kết quả push (success/failure)

**Dependencies:** Không

---

### FR-002: Lưu Processing Record ID từ OpsHub Response

**Priority:** Must Have

**Description:**
Sau khi push content, OpsHub trả về `processing_record_id`, `outcome`, và `task_id` (nếu có). vCreator cần lưu các ID này vào ContentRaw để tra cứu verdict sau.

**Acceptance Criteria:**
- [ ] Lưu `processing_record_id` vào field mới `opsHubProcessingId` trên ContentRaw
- [ ] Lưu `task_id` (nếu có) vào field mới `opsHubTaskId`
- [ ] Lưu `outcome` ban đầu vào field `opsHubOutcome` (`auto_approved`, `auto_rejected`, `needs_review`)
- [ ] Nếu outcome là `auto_approved` hoặc `auto_rejected` → cập nhật `opsHubVerdict` ngay (không cần chờ webhook)
- [ ] Xử lý đúng cả HTTP 200 (auto-decided) và HTTP 202 (needs_review)

**Dependencies:** FR-001

---

### FR-003: Webhook Endpoint nhận Verdict từ OpsHub

**Priority:** Must Have

**Description:**
Implement webhook endpoint trên vCreator backend để nhận verdict callback từ OpsHub khi content đã được duyệt xong (AI hoặc human review).

**Acceptance Criteria:**
- [ ] Endpoint: `POST /api/v1/webhooks/opshub/verdict`
- [ ] Xác thực webhook bằng shared secret (header `X-OpsHub-Delivery-ID` + verify logic)
- [ ] Parse event types: `verdict.approved`, `verdict.rejected`
- [ ] Extract `source_id` (= content ObjectId) từ payload để match content trong DB
- [ ] Cập nhật ContentRaw: `opsHubVerdict`, `opsHubVerdictAt`, `opsHubFeedback`
- [ ] Handle duplicate deliveries: idempotent (check `X-OpsHub-Delivery-ID` đã xử lý chưa)
- [ ] Trả HTTP 200 OK ngay sau khi nhận (xử lý async nếu cần)
- [ ] Log mọi webhook nhận được (success + error)

**Dependencies:** Không

---

### FR-004: Cập nhật Trạng thái Content dựa trên Verdict

**Priority:** Must Have

**Description:**
Khi nhận verdict từ OpsHub (qua webhook hoặc auto-decided response), cập nhật trạng thái content trong vCreator để admin và creator thấy được kết quả.

**Acceptance Criteria:**
- [ ] Thêm fields mới vào ContentRaw model:
  - `opsHubProcessingId` (string) — OpsHub processing record ID
  - `opsHubTaskId` (string) — OpsHub task ID (nullable)
  - `opsHubOutcome` (string) — initial outcome: `auto_approved`, `auto_rejected`, `needs_review`
  - `opsHubVerdict` (string) — final verdict: `approved`, `rejected`, `pending`
  - `opsHubVerdictAt` (time) — thời điểm verdict
  - `opsHubFeedback` (string) — feedback từ reviewer (nullable)
  - `opsHubConfidence` (float) — confidence score (nullable)
- [ ] Verdict `approved` → `opsHubVerdict = "approved"`
- [ ] Verdict `rejected` → `opsHubVerdict = "rejected"`
- [ ] Content chưa có verdict → `opsHubVerdict = "pending"`
- [ ] Không thay đổi content status hiện tại (content vẫn active/published bình thường)

**Dependencies:** FR-002, FR-003

---

### FR-005: Polling Fallback cho Verdict

**Priority:** Should Have

**Description:**
Implement scheduled job polling `GET /api/v1/external/verdicts/:id` cho content đã push nhưng chưa nhận được verdict qua webhook (fallback khi webhook fail).

**Acceptance Criteria:**
- [ ] Job chạy mỗi 15 phút
- [ ] Query content có `isSendOpsHub = true` AND `opsHubOutcome = "needs_review"` AND `opsHubVerdict = "pending"` AND `opsHubVerdictAt` is null AND push time > 30 phút trước
- [ ] Gọi `GET /api/v1/external/verdicts/:opsHubProcessingId` cho mỗi content
- [ ] Nếu verdict đã có → cập nhật giống FR-004
- [ ] Giới hạn batch size: tối đa 50 content/lần poll
- [ ] Không poll content đã quá 7 ngày (coi như stuck, log warning)
- [ ] Respect rate limit OpsHub (100 req/phút)

**Dependencies:** FR-002, FR-004

---

### FR-006: Scheduled Catch-up Sync

**Priority:** Must Have

**Description:**
Job định kỳ tìm content thuộc event OpsHub-enabled nhưng chưa được push (do lỗi, service down, race condition) và push lại.

**Acceptance Criteria:**
- [ ] Job chạy mỗi 10 phút
- [ ] Query: `event.options.isEnableOpsHub = true` AND `isSendOpsHub = false` AND `createdAt` trong 7 ngày gần nhất
- [ ] Push từng content qua FR-001 flow
- [ ] Batch size tối đa 100 content/lần
- [ ] Log số lượng content catch-up mỗi lần chạy
- [ ] Không retry content đã fail > 3 lần (đánh dấu `opsHubSendError`)

**Dependencies:** FR-001

---

### FR-007: Retry Logic cho Push Failures

**Priority:** Must Have

**Description:**
Khi push content sang OpsHub thất bại (network error, 5xx, timeout), implement retry với exponential backoff.

**Acceptance Criteria:**
- [ ] Retry tối đa 3 lần với backoff: 5s, 15s, 45s
- [ ] Không retry cho 4xx errors (client error — fix data, không retry)
- [ ] Sau 3 lần fail → đánh dấu `opsHubSendError` với error message, để catch-up job xử lý sau
- [ ] Log mỗi lần retry với error detail
- [ ] Timeout per request: 10 giây

**Dependencies:** FR-001

---

### FR-008: Config per Event

**Priority:** Must Have

**Description:**
Campaign admin có thể bật/tắt OpsHub integration per event. Đã có field `isEnableOpsHub` trên Event model.

**Acceptance Criteria:**
- [ ] Sử dụng field `event.Options.IsEnableOpsHub` đã tồn tại
- [ ] Khi `false` → content không push sang OpsHub, flow hiện tại giữ nguyên
- [ ] Khi `true` → content tự động push sau crawl
- [ ] Thay đổi config giữa chừng không ảnh hưởng content đã push/chưa push (catch-up job xử lý)
- [ ] Không cần thêm UI (admin đã set được field này)

**Dependencies:** Không

---

### FR-009: Campaign Mapping Setup

**Priority:** Must Have

**Description:**
Mỗi vCreator event cần được map với campaign trên OpsHub. vCreator gửi `campaign_id = event.ObjectId`, OpsHub cần có campaign với `source_campaign_id` trùng khớp.

**Acceptance Criteria:**
- [ ] Khi push content, `campaign_id` = `content.Event.Hex()` (event ObjectId)
- [ ] OpsHub admin cần tạo campaign với `source_campaign_id` = event ObjectId trước khi bật OpsHub cho event đó
- [ ] Nếu OpsHub trả `CAMPAIGN_NOT_FOUND` → log error, đánh dấu `opsHubSendError`, không retry
- [ ] Document quy trình setup cho ops team: tạo campaign OpsHub → copy event ID → set source_campaign_id

**Dependencies:** FR-001

---

### FR-010: Health Check và Monitoring

**Priority:** Should Have

**Description:**
vCreator cần kiểm tra kết nối OpsHub định kỳ và alert khi service không khả dụng.

**Acceptance Criteria:**
- [ ] Gọi `GET /api/v1/external/health` mỗi 5 phút
- [ ] Nếu fail 3 lần liên tiếp → gửi alert Telegram
- [ ] Log health check status
- [ ] Khi OpsHub down, content vẫn được crawl bình thường (graceful degradation) — push sẽ fail và catch-up job retry sau

**Dependencies:** Không

---

### FR-011: Enrichment Data bổ sung

**Priority:** Should Have

**Description:**
Gửi thêm data enrichment từ vCreator sang OpsHub để tăng accuracy của review pipeline.

**Acceptance Criteria:**
- [ ] Gửi `hash_tag` (pre-extracted array) nếu có từ Content Catcher
- [ ] Gửi `follower_count` từ UserSocial data
- [ ] Gửi `creator_id` (platform-specific user ID)
- [ ] Gửi `is_public` (infer từ crawl success)
- [ ] Gửi `media_refs` nếu content có file trên MinIO (bucket + key)
- [ ] Các field optional — không fail nếu thiếu

**Dependencies:** FR-001

---

### FR-012: Audit Log cho OpsHub Events

**Priority:** Should Have

**Description:**
Ghi lại tất cả interaction với OpsHub vào audit log để traceability.

**Acceptance Criteria:**
- [ ] Log khi push content: content ID, event ID, timestamp, outcome
- [ ] Log khi nhận webhook: content ID, verdict, delivery ID, timestamp
- [ ] Log khi polling: content ID, verdict found/not found
- [ ] Log khi retry/fail: content ID, error, retry count
- [ ] Sử dụng audit service hiện có của vCreator (`internal/service/audit.go`)

**Dependencies:** FR-001, FR-003, FR-005

---

## 7. Non-Functional Requirements

### NFR-001: Performance — Push Throughput

**Priority:** Must Have

**Description:**
Push content sang OpsHub không được làm chậm flow crawl content hiện tại.

**Acceptance Criteria:**
- [ ] Push request timeout: max 10 giây
- [ ] Push chạy **async** (goroutine hoặc background job) — không block response trả về creator
- [ ] Throughput: xử lý >=500 push/giờ (peak) mà không degradation
- [ ] Nếu OpsHub chậm/down → content vẫn được crawl bình thường

**Rationale:** Content crawl là flow critical — OpsHub integration phải non-blocking.

---

### NFR-002: Reliability — Không mất Content

**Priority:** Must Have

**Description:**
Mọi content thuộc event OpsHub-enabled phải được push tới OpsHub, không mất.

**Acceptance Criteria:**
- [ ] Catch-up job chạy mỗi 10 phút bắt content bị miss
- [ ] Content miss > 7 ngày → alert Telegram
- [ ] Tỷ lệ content stuck (push nhưng không bao giờ nhận verdict) < 1%
- [ ] Mọi failure đều được log và có path để recovery (retry hoặc manual)

**Rationale:** Mất content = mất duyệt = risk compliance.

---

### NFR-003: Security — API Key & Webhook Verification

**Priority:** Must Have

**Description:**
Communication giữa vCreator và OpsHub phải được xác thực 2 chiều.

**Acceptance Criteria:**
- [ ] API key lưu trong env variable, KHÔNG hardcode
- [ ] Webhook endpoint verify `X-OpsHub-Delivery-ID` hoặc shared secret
- [ ] Webhook endpoint chỉ accept request từ OpsHub (không public)
- [ ] Không log API key trong plaintext

**Rationale:** Data chứa thông tin creator, brand, content — cần bảo mật.

---

### NFR-004: Scalability — 10K video/tháng

**Priority:** Must Have

**Description:**
Hệ thống phải xử lý ổn định 10K video/tháng (~330 video/ngày, ~15 video/giờ peak).

**Acceptance Criteria:**
- [ ] Batch push (catch-up) không quá 100 items/lần, stagger requests
- [ ] Respect OpsHub rate limit: 100 req/phút
- [ ] Không tạo connection pool exhaustion (reuse HTTP client)
- [ ] Memory footprint tăng < 50MB so với trước integration

**Rationale:** Target scale O4.

---

### NFR-005: Observability — Logging & Alerting

**Priority:** Should Have

**Description:**
Đủ log và alert để monitor health của integration.

**Acceptance Criteria:**
- [ ] Structured log cho mọi OpsHub interaction (push, webhook, poll)
- [ ] Alert Telegram khi: OpsHub down > 15 phút, content stuck > 24h, error rate > 10%
- [ ] Dashboard metric (optional): push success rate, avg verdict time, auto-decided rate

**Rationale:** Cần visibility để operate 10K video/tháng với ít người.

---

### NFR-006: Graceful Degradation

**Priority:** Must Have

**Description:**
Khi OpsHub unavailable, vCreator phải hoạt động bình thường.

**Acceptance Criteria:**
- [ ] Content vẫn crawl, publish, tính analytics bình thường
- [ ] Push failures được queue để retry (catch-up job)
- [ ] Không throw error lên creator hoặc admin UI
- [ ] Khi OpsHub recover → catch-up tự động push accumulated content

**Rationale:** OpsHub là enhancement, không phải critical dependency.

---

## 8. Epics

### EPIC-001: Content Push Pipeline

**Description:**
Implement flow push content từ vCreator sang OpsHub, bao gồm data mapping, retry logic, và response handling.

**Functional Requirements:**
- FR-001: Push Content sang OpsHub
- FR-002: Lưu Processing Record ID
- FR-007: Retry Logic
- FR-008: Config per Event
- FR-009: Campaign Mapping Setup
- FR-011: Enrichment Data

**Story Count Estimate:** 5-7

**Priority:** Must Have

**Business Value:**
Core integration — không có push thì không có gì.

**User Stories:**
- Là vCreator system, tôi muốn tự động push content mới sang OpsHub khi event bật OpsHub, để content được duyệt tự động.
- Là vCreator system, tôi muốn lưu processing record ID từ OpsHub, để tra cứu verdict sau này.
- Là vCreator system, tôi muốn retry khi push fail, để không mất content.
- Là campaign admin, tôi muốn bật/tắt OpsHub per event, để linh hoạt chọn campaign nào cần duyệt tự động.

---

### EPIC-002: Verdict Reception

**Description:**
Implement webhook endpoint nhận verdict từ OpsHub và polling fallback, cập nhật trạng thái content trong DB.

**Functional Requirements:**
- FR-003: Webhook Endpoint
- FR-004: Cập nhật Trạng thái Content
- FR-005: Polling Fallback

**Story Count Estimate:** 4-6

**Priority:** Must Have

**Business Value:**
Nhận kết quả duyệt để admin và creator biết content được approved hay rejected.

**User Stories:**
- Là vCreator system, tôi muốn nhận webhook từ OpsHub khi có verdict, để cập nhật trạng thái content ngay.
- Là vCreator system, tôi muốn polling verdict cho content quá lâu chưa có kết quả, để không có content bị stuck.
- Là vCreator system, tôi muốn handle duplicate webhook deliveries, để không cập nhật sai trạng thái.

---

### EPIC-003: Reliability & Monitoring

**Description:**
Implement catch-up sync, health check, audit logging, và alerting để đảm bảo integration chạy ổn định.

**Functional Requirements:**
- FR-006: Scheduled Catch-up Sync
- FR-010: Health Check & Monitoring
- FR-012: Audit Log

**Story Count Estimate:** 3-5

**Priority:** Should Have

**Business Value:**
Đảm bảo không mất content, phát hiện sớm khi có vấn đề, traceability cho audit.

**User Stories:**
- Là ops team, tôi muốn content bị miss được tự động push lại, để không có content nào bị bỏ sót.
- Là ops team, tôi muốn nhận alert khi OpsHub down hoặc content stuck, để xử lý kịp thời.
- Là ops team, tôi muốn xem audit log mọi interaction với OpsHub, để trace khi có dispute.

---

## 9. Traceability Matrix

| Epic | FRs | NFRs | Story Estimate |
|------|-----|------|----------------|
| EPIC-001: Content Push Pipeline | FR-001, FR-002, FR-007, FR-008, FR-009, FR-011 | NFR-001, NFR-004, NFR-006 | 5-7 |
| EPIC-002: Verdict Reception | FR-003, FR-004, FR-005 | NFR-002, NFR-003 | 4-6 |
| EPIC-003: Reliability & Monitoring | FR-006, FR-010, FR-012 | NFR-005 | 3-5 |
| **Tổng** | **12 FRs** | **6 NFRs** | **12-18 stories** |

---

## 10. Prioritization Summary

### Functional Requirements

| Priority | Count | FRs |
|----------|-------|-----|
| Must Have | 8 | FR-001, FR-002, FR-003, FR-004, FR-006, FR-007, FR-008, FR-009 |
| Should Have | 4 | FR-005, FR-010, FR-011, FR-012 |
| Could Have | 0 | — |

### Non-Functional Requirements

| Priority | Count | NFRs |
|----------|-------|------|
| Must Have | 4 | NFR-001, NFR-002, NFR-003, NFR-004 |
| Should Have | 2 | NFR-005, NFR-006 |

---

## 11. Dependencies

### Internal

| Dependency | Mô tả | Status |
|-----------|-------|--------|
| vCreator ContentRaw model | Cần thêm fields mới cho OpsHub | Cần implement |
| vCreator Event model | Field `isEnableOpsHub` đã tồn tại | Done |
| vCreator OpsHub module | Client + model + helper đã có cơ bản | Cần mở rộng |
| vCreator Audit service | Ghi audit log | Có sẵn |
| vCreator Telegram module | Gửi alert | Có sẵn |
| vCreator Scheduled jobs | Infrastructure cho catch-up sync, polling | Có sẵn |

### External

| Dependency | Mô tả | Status |
|-----------|-------|--------|
| OpsHub External API | Push video, query verdict | Đã sẵn sàng |
| OpsHub Webhook | Callback verdict | Đã sẵn sàng |
| OpsHub Project setup | API key + campaign mapping | Cần OpsHub admin setup |
| OpsHub Review Template | Template cho campaign | Cần OpsHub admin tạo |

---

## 12. Assumptions

1. OpsHub External API đã stable và sẵn sàng production
2. OpsHub admin sẽ setup project (vcreator), API key, campaign mapping, review template trước khi vCreator bật integration
3. Content vẫn publish bình thường (OpsHub duyệt song song, không blocking)
4. Verdict từ OpsHub không trigger hành động tự động nào trên vCreator (chỉ cập nhật trạng thái) — phase sau mới có auto-action (ví dụ: auto-hide rejected content)
5. OpsHub rate limit 100 req/phút đủ cho 10K video/tháng (~15 video/giờ average)
6. Network giữa vCreator và OpsHub ổn định (cùng infrastructure)

---

## 13. Open Questions

| # | Câu hỏi | Impact | Owner |
|---|---------|--------|-------|
| Q1 | Khi content bị rejected trên OpsHub, vCreator có cần auto-action gì không (ẩn content, notify creator, hold thưởng)? | Nếu có → thêm FRs mới | Product |
| Q2 | Campaign mapping: tự động tạo campaign trên OpsHub khi vCreator tạo event mới, hay manual? | Nếu auto → thêm FR create campaign API | Product |
| Q3 | Cần gửi video file (media_refs) hay chỉ metadata? | Nếu gửi file → cần shared MinIO access hoặc pre-signed URL | Tech |
| Q4 | OpsHub webhook URL cần expose ra internet hay internal network? | Ảnh hưởng security setup | Infra |
| Q5 | Khi vCreator update content (re-crawl), có cần re-push sang OpsHub không? | Nếu có → thêm logic detect content changes | Product |

---

## 14. Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| OpsHub down → content không được duyệt | Medium | Medium | Graceful degradation (NFR-006), catch-up sync (FR-006) |
| Webhook miss → content stuck ở "pending" | Medium | Medium | Polling fallback (FR-005), alert (FR-010) |
| Rate limit OpsHub bị hit khi batch sync lớn | Low | Low | Stagger requests, respect limit (NFR-004) |
| Campaign chưa mapping → push fail | Medium | Low | Validation check trước push (FR-009), alert |
| Data mapping sai → verdict không chính xác | Low | High | Test kỹ với real content, audit log (FR-012) |

---

## 15. Phụ lục: Existing Code Reference

### vCreator — Đã có

| File | Mô tả |
|------|-------|
| `backend/internal/module/opshub/client.go` | HTTP client gọi OpsHub API |
| `backend/internal/module/opshub/model.go` | Request/Response models |
| `backend/internal/module/opshub/helper.go` | `SendVideoForContent()` — map ContentRaw → payload |
| `backend/internal/config/env.go` | Config: `OPSHUB_IS_ENABLE`, `OPSHUB_BASE_URL`, `OPSHUB_PROJECT_ID`, `OPSHUB_API_KEY` |
| `backend/internal/model/mg/event.go` | `IsEnableOpsHub` field trên Event Options |
| `backend/internal/model/mg/content.go` | `IsSendOpsHub` field trên ContentRaw |
| `backend/pkg/public/service/content.go` | Gọi `SendVideoForContent` sau crawl |
| `backend/pkg/public/service/schedule.go` | `SyncOpsHubContents()` — catch-up job |

### vCreator — Cần thêm/sửa

| Component | Thay đổi |
|-----------|----------|
| `model/mg/content.go` | Thêm fields: `opsHubProcessingId`, `opsHubTaskId`, `opsHubOutcome`, `opsHubVerdict`, `opsHubVerdictAt`, `opsHubFeedback`, `opsHubConfidence`, `opsHubSendError` |
| `module/opshub/client.go` | Thêm `QueryVerdict()` method |
| `module/opshub/model.go` | Thêm response models cho verdict, webhook payload |
| Webhook handler (mới) | Route + handler cho `POST /api/v1/webhooks/opshub/verdict` |
| Scheduled jobs | Thêm polling job, update catch-up job |
| Alert module | Thêm OpsHub health check alert |

### OpsHub External API Reference

Xem: `accesstrade-projects/docs/diso-opshub/api-reference.md`
