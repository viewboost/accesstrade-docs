# Affiliate — API Integration — Overview

> **Project:** Gen-Green × Affiliate Integration — Phase 2 (Affiliate trong Gen-Green)
> **Ngày:** 2026-05-04
> **Trạng thái:** Đang thiết kế
> **Phụ thuộc:** [Scalef Phase 1 — Liên kết Tài khoản](../scalef-integration/overview.md) (đã có `scalef_user_id` trên user)
> **Tham chiếu Pub2:** [`pub2-affiliate-integration/api-reference.md`](../../pub2-affiliate-integration/api-reference.md)
> **Tham chiếu Ambassador V1:** [`prd-affiliate-v1-2026-03-31.md`](../../pub2-affiliate-integration/prd-affiliate-v1-2026-03-31.md) — FR-014, FR-015, FR-016

---

## 1. Bối cảnh

Gen-Green backend đóng vai **proxy/middleware** giữa Gen-Green frontend (creator) và Pub2 (AccessTrade affiliate core). Lý do dùng proxy thay vì creator gọi thẳng Pub2:

1. **Bảo mật:** HMAC credentials (clientId/clientSecret) không lộ ra browser
2. **Tenant isolation:** Inject `sso_user_id` từ session — creator không tự khai
3. **Tracking:** Sub params (`sub2='GENGREEN'`) inject từ BE để analytics theo tenant
4. **Local cache:** Lưu contract + link vào MongoDB Gen-Green để hiển thị nhanh, không gọi Pub2 mỗi request
5. **Error normalization:** Convert error code Pub2 sang message Việt thân thiện
6. **Retry logic:** PENDING/REJECTED contract có business rule retry — xử lý ở BE
7. **Audit log:** Mỗi request/response Pub2 đều ghi log để debug

**Architecture:**
```
Creator (FE) ──→ Gen-Green BE ──HMAC──→ Pub2 (AccessTrade core-aff)
                      │
                      ├── MongoDB local (campaign, mapping, contract, link, log)
                      └── Lookup user.scalef_user_id (Phase 1 đã set)
```

---

## 2. Scope

### Phase V1 (in scope)

- Pub2 API client với HMAC-SHA256
- API 1.2: Join campaign (tạo contract)
- API 2: Generate affiliate link
- Local cache: contract status + retry logic
- Public APIs cho creator (FE consume)
- Admin APIs cho campaign CRUD + mapping
- Logging Pub2 request/response

### Phase V2 (out of scope V1)

- API 3.1: Báo cáo click
- API 3.2: Báo cáo conversion
- API 3.3: Báo cáo sale amount
- API 3.4: Báo cáo commission
- API 6: Báo cáo tổng hợp
- API 7: Webhook từ Pub2 (Optional)
- API 8: Danh sách đơn

### Out of Scope (future)
- API 1: Lấy thông tin Campaign (Pub2 chưa cung cấp; data đã ở DISO)
- Auto-sync campaigns từ Pub2 về Gen-Green admin

---

## 3. Pub2 Authentication

### Endpoint

| Env | URL |
|-----|-----|
| Dev | `https://core-aff.dev.accesstrade.me` |
| Staging | TBD (cần confirm Pub2 team) |
| Prod | TBD |

### Required Headers

| Header | Mô tả |
|--------|-------|
| `client-id` | Mã định danh Gen-Green tại Pub2 |
| `client-trace-no` | UUID v4 lowercase, unique per request |
| `client-request-time` | Unix epoch **milliseconds** (VD `1777043989000`) |
| `client-signature` | HMAC-SHA256 |

### Signature

```
client-signature = HMAC-SHA256(
  client_id + "|" + client_trace_no + "|" + client_request_time,
  client_secret
)
```

**Lưu ý so với module `pub_be` hiện có ở vcreator/gen-green:** plain text Pub2 chuẩn ghép **3 phần** (`clientID|traceNo|epochMs`), không phải 4. Cần verify lại module hiện tại hoặc fork ra `pub2/` riêng.

### Response chuẩn

```json
{
  "status": "success" | "fail" | "error",
  "code": "PX00000",  // PX00000 = success
  "message": "success",
  "data": { ... }
}
```

### Error codes đã gặp

| Code | HTTP | Mô tả |
|------|------|-------|
| `PX00000` | 200 | Success |
| `PX00002` | 400 | Sai format date |
| `PX00099` | 400 | Body không đúng spec / range > 3 tháng |
| `PX000100` | 400 | Lỗi upstream / `partner_ref_campaign_id` rỗng |

Detail → [Pub2 API Reference](../../pub2-affiliate-integration/api-reference.md)

---

## 4. Pub2 Module Design (Backend)

### Cấu trúc

```
backend/internal/module/pub2/
├── client.go         # Main client + Action method
├── hmac.go           # Signature builder
├── models.go         # Request/response struct
└── errors.go         # Custom error types
```

### Interface

```go
type ClientInterface interface {
    JoinCampaign(ctx, partnerCode, ssoId, partnerRefCampaignId) (*JoinResp, error)
    GenerateAffiliateLink(ctx, ssoUserId, campaignId, originalUrl, sub1, sub2, sub3, sub4, sub5) (*LinkResp, error)
    // V2:
    GetClickReport(ctx, ssoUserId, fromDate, toDate, campaignIds) (*ClickReport, error)
    GetConversionReport(...)
    GetSaleAmountReport(...)
    GetCommissionReport(...)
    GetOrders(...)
}
```

### Config (env)

| Env var | Mô tả |
|---------|-------|
| `PUB2_BASE_URL` | Endpoint Pub2 |
| `PUB2_CLIENT_ID` | HMAC client ID |
| `PUB2_CLIENT_SECRET` | HMAC secret |
| `PUB2_TIMEOUT_MS` | Default 10000 (10s) |
| `AFFILIATE_PARTNER_CODE` | Default `PARTNER_1_POINT_5` (cần confirm với Pub2) |
| `AFFILIATE_SUB2_TENANT` | `GENGREEN` (identify tenant) |
| `AFFILIATE_RETRY_PENDING_SECONDS` | 86400 (24h) |
| `AFFILIATE_RETRY_REJECTED_SECONDS` | 1209600 (14d) |

### Pub2 Dev Override (chỉ dev env)

Pub2 dev chỉ có seeded data cho `sso_user_id=504` và Q1-Q2/2023. Helper `applyDevReportOverride()` chỉ dùng cho Report APIs (V2):
- Override `from_date` / `to_date` về `2023-03-01` → `2023-05-31`
- Override `sso_user_id` về `504`

**Tuyệt đối không** override cho mutation APIs (JoinCampaign, GenerateLink) — phải giữ flow thật.

---

## 5. API 1.2 — Join Campaign

### Pub2 spec

```
POST {endpoint}/pgw-api/campaign-service/api/v1/contracts

Body:
{
  "partner_code": "PARTNER_1_POINT_5",
  "sso_id": 504,
  "partner_ref_campaign_id": "4751584435713464237"
}

Response data:
{
  "contract_no": "CTR_xxx",
  "contract_status": "PENDING" | "APPROVED" | "REJECTED",
  ...
}
```

### Gen-Green BE behavior

```
POST /api/affiliate-campaigns/:id/join (auth required)

1. Load user → require user.scalef_user_id != null
2. Load affiliate_campaign by id → require status=active + có pub2_campaign_id
3. Check existing contract:
   - Nếu APPROVED → return ngay (idempotent)
   - Nếu PENDING/REJECTED → check retry window:
     * canRetry=false → return current state + retryAfter
     * canRetry=true → tiếp tục gọi Pub2
4. Gọi Pub2 API 1.2:
   partner_code = AFFILIATE_PARTNER_CODE
   sso_id = user.scalef_user_id (int)
   partner_ref_campaign_id = campaign.pub2_campaign_id
5. Lưu/upsert AffiliateContract:
   - contract_no, contract_status, retry_at = now() + retryWindow
   - last_pub2_response (debug)
6. Trả response: { contract_status, canRetry, retryAfter }
7. Log Pub2 request/response vào pub2_api_logs
```

### Error handling

| Pub2 result | BE response |
|------------|-------------|
| status=success, code=PX00000 | Lưu contract → trả JSON status |
| status=fail (validation) | 400 với message Việt hóa |
| status=error (upstream) | 502 + retry sau |
| Timeout | 504 + creator thấy "Thử lại sau" |

### Retry logic chi tiết

```
contract.contract_status = PENDING
canRetry = (now - contract.updated_at) >= AFFILIATE_RETRY_PENDING_SECONDS
retryAfter = contract.updated_at + AFFILIATE_RETRY_PENDING_SECONDS

contract.contract_status = REJECTED
canRetry = (now - contract.updated_at) >= AFFILIATE_RETRY_REJECTED_SECONDS
retryAfter = contract.updated_at + AFFILIATE_RETRY_REJECTED_SECONDS
```

---

## 6. API 2 — Generate Affiliate Link

### Pub2 spec

```
POST {endpoint}/pgw-api/short-link-service/api/v1/short-links

Body:
{
  "sso_user_id": 504,
  "campaign_id": "4751584435713464237",
  "original_url": "https://shopee.vn/...",
  "sub1": "...",
  "sub2": "GENGREEN",
  "sub3": "<event_id>",
  "sub4": "<affiliate_campaign_id>",
  "sub5": "..."
}

Response data:
{
  "affiliate_link": "https://gateway.../...",
  "short_affiliate_link": "https://s.io/abc"
}
```

### Gen-Green BE behavior

```
POST /api/affiliate-campaigns/:id/generate-link (auth required)

1. Load user → require user.scalef_user_id != null
2. Load affiliate_campaign + check active + có pub2_campaign_id
3. Load existing contract → require contract_status = APPROVED
4. Validate input.original_url:
   - Nếu rỗng → dùng campaign.pub2_campaign_url
   - Nếu có → validate URL format
5. Gọi Pub2 API 2 với sub params:
   sub1 = user._id
   sub2 = AFFILIATE_SUB2_TENANT  // 'GENGREEN'
   sub3 = input.event_id (optional)
   sub4 = affiliate_campaign._id
   sub5 = '' (reserved)
6. Lưu AffiliateLink:
   user_id, affiliate_campaign_id, event_id (optional),
   original_url, affiliate_link, short_affiliate_link, sub1-5,
   created_at
7. Trả { affiliate_link, short_affiliate_link, _id }
8. Log
```

### Lưu ý

- Mỗi lần gọi tạo bản ghi mới (cho phép cùng creator tạo nhiều link cùng campaign với URL khác nhau)
- Link có TTL ở Pub2? — cần confirm. V1 giả định không expire.

---

## 7. Public APIs (cho FE creator)

| Endpoint | Method | Auth | Mô tả |
|----------|--------|------|-------|
| `/api/events/:id/affiliate-campaigns` | GET | Login | List affiliate campaign liên kết với event (status=active) |
| `/api/affiliate-campaigns/:id` | GET | Login | Detail affiliate campaign |
| `/api/affiliate-campaigns/:id/contract` | GET | Login + Linked Scalef | Trạng thái contract của user |
| `/api/affiliate-campaigns/:id/join` | POST | Login + Linked Scalef | Tham gia / retry |
| `/api/affiliate-campaigns/:id/generate-link` | POST | Login + Linked Scalef + APPROVED | Tạo link |
| `/api/affiliate-links` | GET | Login | List link đã tạo (filter by campaign, event, date) |
| `/api/affiliate-links/:id` | DELETE | Login (owner) | Soft-delete link cũ (không gọi Pub2) |

**Middleware mới:**
- `RequireScalefLinked`: check `user.scalef_user_id != null`. 403 nếu chưa link với code `SCALEF_NOT_LINKED` (FE bắt code này hiển thị popup linking).

---

## 8. Admin APIs

Đã liệt kê chi tiết ở [Admin Setup Overview](admin-setup-overview.md#8-api-surface-admin). Tóm lược:

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/admin/affiliate-campaigns` | POST/GET | Tạo / List |
| `/admin/affiliate-campaigns/:id` | GET/PUT | Detail / Update |
| `/admin/affiliate-campaigns/:id/status` | PATCH | Đổi status |
| `/admin/affiliate-campaigns/bulk-status` | POST | Bulk |
| `/admin/affiliate-campaigns/:id/events` | POST/GET | Mapping |
| `/admin/affiliate-campaigns/:id/events/:eventId` | DELETE | Unlink |
| `/admin/events/:eventId/affiliate-campaigns` | GET | Reverse lookup |

V2 admin reports:
| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/admin/affiliate-reports/summary` | GET | Tổng quan |
| `/admin/affiliate-reports/by-creator` | GET | Breakdown theo creator |
| `/admin/affiliate-reports/by-campaign` | GET | Breakdown theo campaign |

---

## 9. Data Models (MongoDB)

### `affiliate_campaigns`

Xem [Admin Setup §3](admin-setup-overview.md#3-entities)

### `campaign_affiliate_mappings`

Xem Admin Setup §3

### `affiliate_contracts`

| Field | Type |
|-------|------|
| `_id` | ObjectId |
| `user_id` | ObjectId |
| `affiliate_campaign_id` | ObjectId |
| `pub2_campaign_id` | string (denorm) |
| `sso_user_id` | string (snapshot từ Scalef) |
| `contract_no` | string |
| `contract_status` | enum: PENDING / APPROVED / REJECTED |
| `retry_at` | datetime (next allowed retry) |
| `last_pub2_response` | object (debug) |
| `created_at`, `updated_at` | datetime |

**Index:** `(user_id, affiliate_campaign_id)` unique

### `affiliate_links`

| Field | Type |
|-------|------|
| `_id` | ObjectId |
| `user_id` | ObjectId |
| `affiliate_campaign_id` | ObjectId |
| `event_id` | ObjectId, nullable (nếu sinh từ context event) |
| `pub2_campaign_id` | string (denorm) |
| `sso_user_id` | string |
| `original_url` | string |
| `affiliate_link` | string |
| `short_affiliate_link` | string |
| `sub1`–`sub5` | string |
| `deleted_at` | datetime, nullable (soft delete) |
| `created_at` | datetime |

**Index:** `(user_id, created_at desc)`, `(affiliate_campaign_id)`, `(event_id)`

### `pub2_api_logs`

| Field | Type |
|-------|------|
| `_id` | ObjectId |
| `endpoint` | string (VD `join_campaign`, `generate_link`) |
| `request_body` | object |
| `request_headers` | object (mask sensitive) |
| `response_body` | object |
| `http_status` | int |
| `pub2_status` | string |
| `pub2_code` | string |
| `duration_ms` | int |
| `user_id` | ObjectId, nullable |
| `error` | string, nullable |
| `created_at` | datetime |

**TTL index:** 90 ngày — tự xóa log cũ.

---

## 10. Security

| Aspect | Implementation |
|--------|----------------|
| HMAC credentials | Env vars only — không commit, không log |
| HMAC log | Mask `client-secret`, signature OK log full để verify |
| `sso_user_id` | Inject từ session, không trust client input |
| Public API authorization | Bearer token + `RequireScalefLinked` middleware |
| Affiliate link ownership | Mọi GET/DELETE check `user_id` match session |
| Admin API | Permission framework hiện có (super admin / partner admin) |
| Rate limit | Per-user 60 req/min cho generate-link (chống spam) |
| Idempotency | Join campaign check existing contract trước khi gọi Pub2 |

---

## 11. Logging & Monitoring

### Application logs (existing logger)

- Mọi Pub2 call: log endpoint, duration, status
- Error → log full request/response (đã mask secret)
- Slow query > 3s → warning

### `pub2_api_logs` collection

- Lưu cho debug & support
- Admin có thể truy vấn logs theo user / campaign / time range
- TTL 90 ngày

### Metrics (future)

- Counter: số contract theo status
- Counter: số link generated / day
- Histogram: Pub2 latency
- Alert: Pub2 error rate > 5% trong 5 phút

---

## 12. Performance

| Yêu cầu | Target |
|---------|--------|
| Internal CRUD APIs | p95 < 200ms |
| Proxy APIs (Pub2) | p95 < 3s (network bound) |
| List affiliate by event | p95 < 300ms (Mongo + cache) |
| Generate link | p95 < 3s |
| Concurrent join requests / user | Idempotent — chỉ 1 contract / (user, campaign) |

**Caching:** affiliate-campaign list per event cache 5' (Redis) — invalidate khi admin thay đổi mapping/status.

---

## 13. Testing

### Unit
- HMAC builder (compare với `openssl` reference)
- Retry window calculation
- Status state machine

### Integration
- Pub2 client với mock server
- Public APIs end-to-end (real Mongo, mock Pub2)
- Middleware `RequireScalefLinked`

### Contract testing (Pact, optional V1)
- Verify request/response shape khớp Pub2 spec
- Reuse pattern from at-core (Go + Pact)

### E2E
- Test với Pub2 dev env: sso_user_id=504, campaign Shopee `4751584435713464237`
- Smoke test sau mỗi deploy

---

## 14. Migration & Rollout

### Pre-launch checklist

- [ ] Pub2 endpoint dev/staging/prod confirmed
- [ ] Credentials issued cho Gen-Green tenant
- [ ] `partner_code` confirmed với Pub2 team
- [ ] HMAC signature verify được bằng curl test
- [ ] Mongo indexes created
- [ ] Redis cache configured
- [ ] Logs TTL configured
- [ ] Admin permission updated

### Rollout plan

1. **Internal beta** (1 tuần): bật cho 10 admin + 50 nội bộ creator (Vin staff). Monitor errors.
2. **Soft launch** (2 tuần): bật cho 1000 creator được chọn. A/B affiliate section visibility.
3. **Public launch:** bật cho toàn bộ 150K creator.

### Rollback

- Feature flag `AFFILIATE_ENABLED` (env-level) để tắt nhanh
- Tắt → FE ẩn affiliate section, BE return 404 cho public APIs
- Admin APIs vẫn hoạt động (data không mất)

---

## 15. Open Questions

1. **Pub2 endpoint cho Gen-Green tenant**: dùng chung với Ambassador (`core-aff.dev.accesstrade.me`) hay riêng?
2. **`partner_code`**: Gen-Green dùng `PARTNER_1_POINT_5` hay code khác?
3. **`sub2` convention**: `GENGREEN` đã được agree với data team chưa?
4. **Pub_BE module hiện tại** (4-part HMAC): có phải dùng cho Pub2 luôn không, hay tạo module riêng?
5. **Webhook Pub2**: có hỗ trợ realtime callback (thay vì polling reports) không?
6. **TTL của affiliate link**: link có hết hạn ở Pub2 không?
7. **Rate limit Pub2**: limit nào tới Gen-Green? (cần confirm để tránh 429)
8. **Sandbox staging**: có Pub2 staging environment riêng cho QA không?

---

## 16. Estimate

| Module | Effort |
|--------|--------|
| Pub2 client module (HMAC + 2 APIs V1) | 2d |
| Config + collection scaffold + DAO | 1d |
| Internal service `affiliate.go` + retry logic | 1.5d |
| Admin handlers + service + router (CRUD + mapping) | 2d |
| Public handlers + service + router (join/contract/generate/list) | 2d |
| Middleware `RequireScalefLinked` | 0.5d |
| Logging + metrics | 0.5d |
| Unit + integration tests | 2d |
| QA + bug fix | 1.5d |
| **Tổng V1** | **~13d (~2.5 tuần)** |

V2 (Reports + Webhook): ~10d thêm.

---

## 17. Liên quan

- [Admin Setup Overview](admin-setup-overview.md)
- [FE Display + Generate Link + Report Overview](fe-display-generate-link-report-overview.md)
- [Pub2 API Reference](../../pub2-affiliate-integration/api-reference.md)
- [Ambassador V1 PRD](../../pub2-affiliate-integration/prd-affiliate-v1-2026-03-31.md)
- [Ambassador V2 PRD](../../pub2-affiliate-integration/prd-affiliate-v2-2026-03-31.md)
- [Scalef Linking Phase 1](../scalef-integration/overview.md)
- Ambassador reference code: `internal/module/pub2/`, `internal/service/affiliate.go`, `pkg/{admin,public}/{handler,service,router}/affiliate.go`
