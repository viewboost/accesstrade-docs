# Product Requirements Document: Pub2 Affiliate Integration — V1 (Implemented)

**Date:** 2026-03-31
**Author:** vinhnguyen
**Version:** 1.0
**Project Type:** Feature Integration
**Project Level:** Level 3
**Status:** Implemented ✅
**Platform:** Ambassador (`accesstrade-projects/ambassabor/`)

---

## Document Overview

PRD này ghi nhận các chức năng affiliate marketing **đã được implement** trong Ambassador platform. Đây là baseline document cho Phase 1 — bao gồm Admin Campaign Management, Pub2 API Integration, và Influencer Campaign Experience.

**Related Documents:**
- [PRD Gốc (v1.3)](./prd-affiliate-integration-2026-03-25.md)
- [Architecture](./architecture-affiliate-integration-2026-03-25.md)
- [API Reference](./api-reference.md)
- [PRD V2 — Remaining Features](./prd-affiliate-v2-2026-03-31.md)

---

## Executive Summary

Phase 1 đã hoàn thành **core affiliate integration**: Admin tạo và quản lý affiliate campaigns, liên kết với events; Influencer browse, tham gia chiến dịch, tạo affiliate link. Backend Go proxy tới Pub2 APIs với HMAC authentication.

**Đã implement:**
- Admin CRUD affiliate campaigns + mapping với events
- Pub2 API Client (HMAC-SHA256) — join campaign + generate link
- Influencer xem affiliate campaigns trong campaign detail
- Influencer tham gia chiến dịch (join → contract)
- Influencer tạo & quản lý affiliate links
- Trang chi tiết affiliate campaign (2-column layout, accordion, tabs)
- Điểm chạm liên kết AccessTrade (banner + popup)

---

## Product Goals

### Business Objectives

1. **Tăng thu nhập influencer**: Dual revenue stream (views + affiliate commissions)
2. **Tăng engagement**: Incentive mạnh hơn để tạo nội dung chất lượng
3. **Tăng retention**: Influencer gắn bó lâu hơn nhờ thu nhập cao hơn
4. **Mở rộng giá trị platform**: Kết nối influencer với merchants qua affiliate

### Success Metrics

| Metric | Target | Timeframe |
|--------|--------|-----------|
| Tỷ lệ influencer tạo affiliate link | 40% active users | 3 tháng sau launch |
| Activation rate (linked → generated link) | 60% | 3 tháng |

---

## Functional Requirements (Implemented)

---

### FR-001: Admin tạo Affiliate Campaign ✅

**Priority:** Must Have
**Status:** Implemented

**Description:**
Admin tạo affiliate campaign mới trên Ambassador Admin panel. Campaign bao gồm thông tin nội bộ và liên kết với Pub2 qua `pub2_campaign_id`.

**Acceptance Criteria:**
- [x] Admin có thể tạo affiliate campaign với các trường: partner (required), title, description, short_desc, banner image (required), category, commission info (required), bonus_info, pub2_campaign_id, pub2_campaign_url (required), start_date, end_date
- [x] Partner là required khi tạo và immutable sau khi tạo
- [x] Status mặc định là `inactive` khi tạo
- [x] Admin có thể chỉnh sửa và cập nhật campaign (trừ partner)
- [x] Admin có thể thay đổi status: active / inactive
- [x] Validate `pub2_campaign_id` là required và không trùng lặp
- [x] Campaign chỉ hiển thị cho influencer khi status = active

**Implementation:**
- Backend: `pkg/admin/handler/affiliate.go` → `Create()`, `Update()`, `ChangeStatus()`
- Admin UI: `admin/src/pages/affiliate-campaign/` + `components/modal.tsx`
- Model: `internal/model/mg/affiliate.go` → `AffiliateCampaignRaw`
- Collection: `affiliate-campaigns`

---

### FR-002: Admin quản lý danh sách Affiliate Campaigns ✅

**Priority:** Must Have
**Status:** Implemented

**Description:**
Admin xem, tìm kiếm, lọc và quản lý danh sách affiliate campaigns.

**Acceptance Criteria:**
- [x] Hiển thị danh sách campaigns với: title, status, commission, ngày tạo
- [x] Lọc theo status (active/inactive)
- [x] Tìm kiếm theo title
- [x] Sắp xếp theo ngày tạo, title
- [x] Bulk actions: activate / deactivate nhiều campaigns

**Implementation:**
- Backend: `pkg/admin/handler/affiliate.go` → `GetList()`
- Admin UI: `admin/src/pages/affiliate-campaign/index.tsx` + `components/table.tsx`

---

### FR-003: Admin liên kết Affiliate Campaign với Campaign/Event ✅

**Priority:** Must Have
**Status:** Implemented

**Description:**
Admin liên kết (mapping) affiliate campaign với campaign/event. Quan hệ many-to-many.

**Acceptance Criteria:**
- [x] Admin có thể liên kết 1 affiliate campaign với 1 hoặc nhiều campaigns/events
- [x] Admin có thể liên kết 1 campaign/event với 1 hoặc nhiều affiliate campaigns
- [x] Chỉ hiển thị events cùng partner khi liên kết
- [x] Quan hệ many-to-many: bảng mapping `campaign_affiliate_mappings`
- [x] Admin có thể gỡ liên kết (unlink)
- [x] Hiển thị danh sách events đã liên kết trong trang chi tiết affiliate campaign
- [x] Hiển thị danh sách affiliate campaigns đã liên kết trong trang chi tiết campaign
- [x] Event search autocomplete với debounce khi liên kết

**Implementation:**
- Backend: `pkg/admin/handler/affiliate.go` → `LinkToEvent()`, `UnlinkFromEvent()`, `GetMappingsByEvent()`, `GetMappingsByCampaign()`
- Model: `internal/model/mg/affiliate.go` → `CampaignAffiliateMappingRaw`
- Collection: `campaign-affiliate-mappings`
- Admin UI: `admin/src/pages/affiliate-campaign/detail/index.tsx`

---

### FR-004: Influencer xem Affiliate Campaign trong chi tiết Campaign ✅

**Priority:** Must Have
**Status:** Implemented

**Description:**
Influencer vào chi tiết campaign/event → thấy section affiliate campaign(s) liên kết.

**Acceptance Criteria:**
- [x] Section "Chiến Dịch Affiliate Liên Kết" hiển thị nếu campaign có liên kết affiliate
- [x] Nếu không có → không hiển thị section
- [x] Grid layout (1 cột mobile, 2 cột desktop)
- [x] Banner liên kết AccessTrade nếu chưa liên kết
- [x] Affiliate Item Card: banner, title, URL link, CTA "Khám phá ngay", info badges (Hoa hồng, Thưởng thêm, Thời gian)

**Implementation:**
- Frontend: `frontend/src/pages/home/components/affiliate-campaigns-section/index.tsx`
- Frontend: `frontend/src/pages/home/components/affiliate-item-card/index.tsx`

---

### FR-005: Influencer tạo Affiliate Link ✅

**Priority:** Must Have
**Status:** Implemented

**Description:**
Influencer tạo affiliate link cho campaign. Yêu cầu đã tham gia (contract_status = APPROVED).

**Acceptance Criteria:**
- [x] Chỉ cho phép tạo link khi contract_status = APPROVED
- [x] Chỉ cho phép khi đã liên kết tài khoản AccessTrade
- [x] Backend gọi Pub2 API 2 với HMAC authentication
- [x] Sử dụng sub parameters cho tracking
- [x] Trả về `affiliate_link` và `short_affiliate_link`
- [x] Influencer có thể copy link
- [x] Lưu link trong database Ambassador
- [x] Xử lý lỗi Pub2 API

**Implementation:**
- Backend: `pkg/public/handler/affiliate.go` → `GenerateLink()`
- Pub2 Client: `internal/module/pub2/client.go` → `GenerateAffiliateLink()`
- Model: `internal/model/mg/affiliate.go` → `AffiliateLinkRaw`
- Collection: `affiliate-links`
- Frontend: `frontend/src/pages/affiliate-campaign-detail/index.tsx`

---

### FR-013: Điểm chạm liên kết AccessTrade tại Campaign Detail ✅

**Priority:** Must Have
**Status:** Implemented

**Description:**
Touchpoint tại section affiliate campaign để hướng dẫn influencer liên kết AccessTrade.

**Acceptance Criteria:**
- [x] Banner trên đầu section khi chưa liên kết, kèm CTA "Liên kết tài khoản"
- [x] Popup khi bấm action mà chưa link → yêu cầu liên kết trước
- [x] Popup có nút redirect đến trang liên kết AccessTrade (SSO flow)
- [x] Sau khi liên kết → redirect về campaign detail
- [x] Banner tự ẩn khi đã liên kết

**Implementation:**
- Frontend: AT Linking Banner trong campaign detail + popup component

---

### FR-014: Backend Pub2 API Client (HMAC Authentication) ✅

**Priority:** Must Have
**Status:** Implemented

**Description:**
Backend Go service gọi Pub2 APIs với HMAC signature authentication.

**Acceptance Criteria:**
- [x] HMAC-SHA256 signature: `HMACSHA256(clientId + "|" + clientTraceNo + "|" + clientRequestTime, clientSecret)`
- [x] Headers: `client-id`, `client-trace-no` (UUID), `client-request-time`, `client-signature`
- [x] Config từ environment: `AFFILIATE_ENDPOINT`, `AFFILIATE_CLIENT_ID`, `AFFILIATE_CLIENT_SECRET`
- [x] Xử lý response chuẩn: check `status`, `code` (PX00000 = OK), `message`
- [x] Logging request/response cho debugging
- [x] Timeout configuration (default 10s)

**Implementation:**
- Module: `internal/module/pub2/client.go` + `hmac.go` + `models.go` + `errors.go`
- Config: `internal/config/env.go` → `AffiliateConfig`
- Logging: `internal/model/mg/affiliate.go` → `Pub2ApiLogRaw`

**Lưu ý:** Retry logic (max 3 retries) — cần verify có implement chưa.

---

### FR-015: Backend Affiliate Campaign CRUD APIs ✅

**Priority:** Must Have
**Status:** Implemented

**Description:**
Backend APIs cho Admin CRUD affiliate campaigns, lưu trong MongoDB.

**Acceptance Criteria:**
- [x] `POST /admin/affiliate-campaigns` — Tạo campaign
- [x] `GET /admin/affiliate-campaigns` — Danh sách campaigns (filter, search, pagination)
- [x] `GET /admin/affiliate-campaigns/:id` — Chi tiết campaign
- [x] `PUT /admin/affiliate-campaigns/:id` — Cập nhật campaign
- [x] `PATCH /admin/affiliate-campaigns/:id/status` — Thay đổi status
- [x] Validate: pub2_campaign_id unique, required fields, partner required
- [x] Mapping APIs (CRUD cho campaign ↔ affiliate campaign)
- [x] Public APIs cho influencer: `GET /events/:id/affiliate-campaigns`, `GET /affiliate-campaigns/:id`

**Implementation:**
- Admin: `pkg/admin/handler/affiliate.go` + `pkg/admin/service/affiliate.go` + `pkg/admin/router/affiliate.go`
- Public: `pkg/public/handler/affiliate.go` + `pkg/public/service/affiliate.go` + `pkg/public/router/affiliate.go`
- DAOs: `internal/module/database/mongodb/dao/affiliate_campaign.go`, `campaign_affiliate_mapping.go`

---

### FR-016: Backend Affiliate Link & Report APIs (Partial) ⚠️

**Priority:** Must Have
**Status:** Partially Implemented

**Đã implement:**
- [x] `POST /affiliate-campaigns/:id/join` — Tham gia chiến dịch (proxy Pub2 API 1.2)
- [x] `GET /affiliate-campaigns/:id/contract` — Lấy trạng thái tham gia
- [x] `POST /affiliate-campaigns/:id/generate-link` — Tạo affiliate link (proxy Pub2 API 2)
- [x] `GET /affiliate-links` — Danh sách links đã tạo
- [x] Tất cả APIs yêu cầu authentication + đã link AccessTrade
- [x] Tự động inject `sso_user_id` từ user data

**Chưa implement (→ V2):**
- [ ] `POST /affiliate-reports/clicks` — Báo cáo click
- [ ] `POST /affiliate-reports/conversions` — Báo cáo conversion
- [ ] `POST /affiliate-reports/sale-amount` — Báo cáo sale amount
- [ ] `POST /affiliate-reports/commission` — Báo cáo commission
- [ ] `POST /affiliate-reports/orders` — Danh sách đơn

---

### FR-017: Influencer tham gia chiến dịch (Join Campaign) ✅

**Priority:** Must Have
**Status:** Implemented

**Description:**
Influencer tham gia chiến dịch affiliate. Backend gọi Pub2 API 1.2 tạo contract.

**Acceptance Criteria:**
- [x] Chỉ cho phép khi đã liên kết AccessTrade
- [x] Backend gọi Pub2 API 1.2 với `partner_code`, `sso_id`, `partner_ref_campaign_id`
- [x] Lưu `contract_no` và `contract_status` vào database
- [x] Hiển thị trạng thái: PENDING / APPROVED / REJECTED
- [x] Xử lý error codes từ Pub2 API 1.2
- [x] Nút "Tham gia chiến dịch" trong affiliate campaign card
- [x] Sau join APPROVED → hiện nút "Tạo link affiliate"
- [x] **Retry mechanism cho PENDING/REJECTED:**
  - PENDING: Banner vàng "Yêu cầu tham gia đang được xử lý" + "Thử lại sau X giờ"
  - REJECTED: Banner đỏ "Bạn không đủ điều kiện" + "Thử lại sau X ngày"
  - Backend tính `canRetry` (bool) + `retryAfter` (timestamp) từ `updatedAt` + ENV config
  - ENV: `AFFILIATE_RETRY_PENDING_SECONDS` (default: 86400 = 24h), `AFFILIATE_RETRY_REJECTED_SECONDS` (default: 1209600 = 14 ngày)
  - `canRetry = true` → hiện nút "Thử lại", backend gọi lại Pub2 API
  - `canRetry = false` → hiện countdown "Thử lại sau X giờ/ngày"

**Implementation:**
- Backend: `pkg/public/handler/affiliate.go` → `JoinCampaign()`, `GetContract()`
- Backend: `pkg/public/service/affiliate.go` → `contractRetryInfo()`, `buildContractDetail()`
- Backend: `internal/service/affiliate.go` → retry logic cho PENDING/REJECTED
- Config: `internal/config/env.go` → `RetryPendingSeconds`, `RetryRejectedSeconds`
- Response: `pkg/public/model/response/affiliate.go` → `canRetry`, `retryAfter` fields
- Pub2: `internal/module/pub2/client.go` → `JoinCampaign()`
- Model: `internal/model/mg/affiliate.go` → `AffiliateContractRaw`
- Frontend: `frontend/src/pages/affiliate-campaign-detail/index.tsx` → retry UI states
- Collection: `affiliate-contracts`

---

### FR-018: Trang chi tiết Affiliate Campaign ✅

**Priority:** Must Have
**Status:** Implemented

**Description:**
Trang chi tiết affiliate campaign cho influencer. Layout 2 cột desktop, stack mobile.

**Acceptance Criteria:**
- [x] 2 cột ngang desktop, stack dọc mobile
- [x] Cột trái: Banner image + 3 info badges
- [x] Cột phải: Title, description, tabs (Thể lệ / Hướng dẫn), AT linking banner
- [x] Accordion sections parse từ field `desc` (markdown headings `##`)
- [x] Section đầu tiên mặc định mở

**Implementation:**
- Frontend: `frontend/src/pages/affiliate-campaign-detail/index.tsx`

---

## Non-Functional Requirements (Implemented)

---

### NFR-001: Performance — API Response Time ✅

- [x] Internal APIs (CRUD campaigns, list links): < 200ms cho 95% requests
- [x] Proxy APIs (Pub2): < 3s cho 95% requests

---

### NFR-002: Security — HMAC & Data Protection ✅

- [x] Pub2 credentials lưu trong environment variables
- [x] HMAC signature unique per request (UUID)
- [x] `sso_user_id` inject từ backend
- [x] Affiliate links chỉ thuộc user đã tạo
- [x] Admin APIs yêu cầu admin role

---

### NFR-003: Security — Tenant Isolation ✅

- [x] `sub2` parameter identify Ambassador platform
- [x] Report APIs filter by sso_user_id
- [x] Không expose pub2 credentials ra frontend

---

### NFR-005: Usability — Mobile Responsive ✅

- [x] Campaign list, detail responsive trên mobile (≥ 320px)
- [x] Copy link hoạt động trên mobile

---

### NFR-006: Maintainability — Pub2 Client Module ✅

- [x] Pub2 client là Go package riêng trong `internal/module/pub2/`
- [x] Config externalized (endpoint, credentials, timeout)

---

### NFR-007: Compatibility — Existing System ✅

- [x] Affiliate campaigns là collection riêng trong MongoDB
- [x] Routing mới không conflict với routes hiện có
- [x] Chức năng liên kết AccessTrade không bị ảnh hưởng

---

## Epics (V1 — Implemented)

---

### EPIC-001: Admin Affiliate Campaign Management ✅

**Functional Requirements:** FR-001, FR-002, FR-003, FR-015

**Status:** Fully implemented

---

### EPIC-002: Pub2 API Integration (Backend) ✅

**Functional Requirements:** FR-014, FR-016 (partial — link & join only)

**Status:** Core integration complete. Report API proxy endpoints deferred to V2.

---

### EPIC-003: Influencer Affiliate Campaign Experience ✅

**Functional Requirements:** FR-004, FR-017, FR-018, FR-005, FR-013

**Status:** Fully implemented

---

## Implementation Reference

### Backend Structure

```
backend/
├── internal/
│   ├── config/env.go                    # AffiliateConfig
│   ├── model/mg/affiliate.go            # All affiliate MongoDB models
│   ├── service/affiliate.go             # Core business logic (AffiliateInterface)
│   └── module/
│       ├── pub2/
│       │   ├── client.go                # Pub2 API client
│       │   ├── hmac.go                  # HMAC-SHA256 signature
│       │   ├── models.go                # Request/response structs
│       │   └── errors.go               # Error types
│       └── database/mongodb/
│           ├── collection.go            # Collection names
│           └── dao/
│               ├── affiliate_campaign.go
│               ├── affiliate_contract.go
│               ├── affiliate_link.go
│               └── campaign_affiliate_mapping.go
├── pkg/
│   ├── admin/
│   │   ├── handler/affiliate.go
│   │   ├── service/affiliate.go
│   │   ├── router/affiliate.go
│   │   └── model/{request,response}/affiliate.go
│   └── public/
│       ├── handler/affiliate.go
│       ├── service/affiliate.go
│       ├── router/affiliate.go
│       └── model/{request,response}/affiliate.go
```

### Frontend Structure

```
frontend/src/
├── pages/
│   ├── affiliate-campaign-detail/index.tsx     # Detail page
│   └── home/components/
│       ├── affiliate-campaigns-section/        # Campaigns listing section
│       └── affiliate-item-card/                # Campaign card component
├── services/affiliate.ts                        # API service layer
└── interfaces/campaign-link.ts                  # TypeScript interfaces
```

### Admin Structure

```
admin/src/
├── pages/affiliate-campaign/
│   ├── index.tsx                # List page
│   ├── detail/index.tsx         # Detail + mappings
│   ├── components/modal.tsx     # Create/edit modal
│   ├── components/table.tsx     # Campaigns table
│   ├── model.ts                 # DVA state management
│   └── type.d.ts                # TypeScript interfaces
└── services/affiliate-campaign.ts  # API service
```

### MongoDB Collections

| Collection | Model | Purpose |
|-----------|-------|---------|
| `affiliate-campaigns` | `AffiliateCampaignRaw` | Campaign metadata + Pub2 link |
| `campaign-affiliate-mappings` | `CampaignAffiliateMappingRaw` | Event ↔ Campaign many-to-many |
| `affiliate-contracts` | `AffiliateContractRaw` | User join status with Pub2 |
| `affiliate-links` | `AffiliateLinkRaw` | Generated affiliate links |
| `pub2-api-logs` | `Pub2ApiLogRaw` | API request/response logs |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-31 | vinhnguyen | Tách PRD V1 từ PRD gốc v1.3. Ghi nhận trạng thái implemented của Phase 1. |

---

**This document was created using BMAD Method v6 - Phase 2 (Planning)**
