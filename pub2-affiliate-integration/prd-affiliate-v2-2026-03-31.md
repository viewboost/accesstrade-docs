# Product Requirements Document: Pub2 Affiliate Integration — V2 (Reports & Dashboard)

**Date:** 2026-03-31
**Author:** vinhnguyen
**Version:** 1.0
**Project Type:** Feature Enhancement
**Project Level:** Level 2
**Status:** Complete ✅
**Platform:** Ambassador (`accesstrade-projects/ambassabor/`)

---

## Document Overview

PRD này định nghĩa các chức năng **chưa implement** từ PRD gốc v1.3, tập trung vào **Affiliate Reports, Dashboard, và các gap còn thiếu**. Đây là Phase 2 của Pub2 Affiliate Integration.

**Related Documents:**
- [PRD Gốc (v1.3)](./prd-affiliate-integration-2026-03-25.md)
- [PRD V1 — Implemented Features](./prd-affiliate-v1-2026-03-31.md)
- [Architecture](./architecture-affiliate-integration-2026-03-25.md)
- [API Reference](./api-reference.md)

---

## Executive Summary

Phase 1 đã hoàn thành core flow: Admin quản lý campaigns, Influencer tham gia và tạo affiliate link. **Phase 2 bổ sung khả năng theo dõi hiệu suất** — influencer cần thấy clicks, conversions, commission, danh sách đơn hàng để đánh giá kết quả và tiếp tục tham gia.

**Điểm đặc biệt:** Backend Pub2 client (`internal/module/pub2/client.go`) **đã có sẵn** các method cho report APIs (`GetClickStats`, `GetConversionStats`, `GetSaleAmountStats`, `GetCommissionStats`, `GetConversions`). Công việc chính là **expose qua Public API endpoints** và **xây dựng frontend**.

**Scope V2:**
1. **Trang browse affiliate campaigns** cho influencer (FR-019)
2. **5 Public Report API endpoints** (proxy Pub2 APIs 3.1, 3.2, 3.3, 3.4, 8)
3. **Frontend báo cáo:** biểu đồ click/conversion/commission theo ngày
4. **Danh sách đơn hàng chi tiết** với filter, phân trang
5. **Dashboard tổng hợp** aggregate từ 4 APIs
6. **Trang quản lý links riêng** (FR-006)
7. **Circuit breaker** cho Pub2 client (NFR-004)
8. **Swagger documentation** cho affiliate APIs

---

## Product Goals

### Business Objectives

1. **Transparency:** Influencer thấy hiệu suất → tin tưởng platform → tiếp tục tham gia
2. **Data-driven decisions:** Influencer biết campaign nào hiệu quả → tập trung resources
3. **Retention:** Dashboard + reports tạo lý do quay lại app thường xuyên

### Success Metrics

| Metric | Target | Timeframe |
|--------|--------|-----------|
| Avg. influencer income tăng | +40% | 6 tháng sau V1 launch |
| Influencer retention | +15% | 6 tháng |
| DAU xem reports/dashboard | 30% active affiliates | 2 tháng sau V2 launch |
| Influencer quay lại xem report ≥ 2 lần/tuần | 50% | 3 tháng |

---

## Functional Requirements

---

### FR-020: Enhanced Link Generation — Custom URL, Naming, History ✅

**Priority:** Must Have
**Status:** Implemented (2026-04-09)

**Description:**
Nâng cấp chức năng tạo affiliate link: cho phép influencer nhập custom original URL (deep link sản phẩm cụ thể), đặt tên link, tạo nhiều link cho cùng campaign, và xem lịch sử link đã tạo. Layout 2 cột: bên trái accordion mô tả, bên phải panel tạo link + history.

**Acceptance Criteria:**
- [x] Form tạo link thay thế nút đơn "Lấy link affiliate"
- [x] **Original URL input:** Pre-fill `pub2CampaignUrl`, influencer có thể override bằng deep link sản phẩm cụ thể
- [x] **Link naming:** Input "Đặt tên link" (tuỳ chọn, max 100 ký tự) để dễ nhận diện
- [x] **Multi-link per campaign:** Bỏ giới hạn 1 link/user/campaign, cho phép tạo nhiều link với URL/tên khác nhau
- [x] **URL validation:** Backend validate format URL (http/https only), block javascript:/data: schemes
- [x] **Link history:** Section "Lịch sử tạo link" hiển thị danh sách link đã tạo cho campaign hiện tại
- [x] **Search by name:** Tìm kiếm link theo tên trong history (debounced, regex escaped)
- [x] **History card:** Mỗi link hiển thị: tên (hoặc "Chưa đặt tên"), short link, ngày tạo, nút copy, status badge
- [x] **Layout 2 cột:** Bên trái 50% = accordion mô tả, bên phải 50% = form + history (sticky)
- [x] **"Tạo thêm link mới":** Sau khi tạo xong, hiện kết quả + nút tạo thêm
- [x] **Backward compatible:** API vẫn hoạt động khi gọi POST không có body (default = campaign URL)

**Existing Assets:**
- Pub2 API 2: `GenerateLinkRequest.original_url` ✅ (đã hỗ trợ custom URL)
- Pub2 client: `client.go → GenerateAffiliateLink()` ✅
- V1: link generation + display ✅

**Implementation:**

Backend (6 files):
- `internal/model/mg/affiliate.go` — Thêm `Name`, `OriginalUrl` vào `AffiliateLinkRaw`
- `internal/service/affiliate.go` — Bỏ idempotent 1:1, nhận `originalUrl` + `name`, use custom URL or default
- `internal/module/database/mongodb/index.go` — Đổi unique index → non-unique trên `affiliate-links`
- `pkg/public/model/request/affiliate.go` — Thêm `GenerateLinkBody` (URL validation), `Keyword` trong `AffiliateMyLinks`
- `pkg/public/model/response/affiliate.go` — Thêm `Name`, `OriginalUrl` vào response
- `pkg/public/handler/affiliate.go` — Parse + validate request body
- `pkg/public/service/affiliate.go` — Pass params, keyword search (regex escaped)

Frontend (4 files):
- `interfaces/campaign-link.ts` — Thêm `name?`, `originalUrl?` vào `IAffiliateLink`
- `services/affiliate.ts` — `generateLink` nhận optional data body
- `pages/affiliate-campaign-detail/index.tsx` — Layout 2 cột, form tạo link, link history, debounced search
- `pages/affiliate-campaign-detail/index.scss` — Styles cho bottom layout, form, link panel, history list

**DB Migration:**
```js
db.getCollection("affiliate-links").dropIndex("userId_1_affiliateCampaignId_1")
```

**Lưu ý UTM:** Pub2 API nhận UTM fields nhưng doc ghi "Tạm thời không quan tâm" — DEFERRED cho đến khi Pub2 confirm hỗ trợ.

**Dependencies:** V1 FR-005 (generate link), FR-018 (campaign detail page)

**Brainstorming:** [brainstorming-enhanced-link-generation-2026-04-08.md](../.bmad/brainstorming-enhanced-link-generation-2026-04-08.md)

---

### FR-019: Influencer browse danh sách Affiliate Campaigns

**Priority:** Must Have

**Description:**
Influencer vào trang riêng để xem danh sách tất cả affiliate campaigns đang active. Hiện tại influencer chỉ thấy affiliate campaigns trong chi tiết campaign/event (FR-004 V1), chưa có trang listing riêng để browse toàn bộ.

**Acceptance Criteria:**
- [ ] Trang riêng hiển thị danh sách affiliate campaigns có status = active
- [ ] Sắp xếp theo ngày tạo mới nhất trước (descending)
- [ ] Mỗi item hiển thị: banner, title, commission info, bonus info (reuse Affiliate Item Card từ V1)
- [ ] Click vào item → navigate đến trang chi tiết affiliate campaign
- [ ] Phân trang (infinite scroll hoặc pagination)
- [ ] Responsive trên mobile (1 cột) và desktop (2 cột grid)
- [ ] Empty state khi không có campaigns

**Existing Assets:**
- Admin backend: `GET /admin/affiliate-campaigns` (có sẵn, nhưng cần public endpoint)
- Frontend component: `affiliate-item-card/` (reuse từ V1)
- Model: `AffiliateCampaignRaw` ✅

**Cần làm:**
- Backend: Public API endpoint `GET /api/public/affiliate-campaigns` (list active campaigns, sorted by created_at desc, pagination)
- Frontend page mới: `frontend/src/pages/affiliate-campaigns/index.tsx`
- Frontend service method: `affiliate.ts` → `getAffiliateCampaigns()`
- Route mới trong `frontend/config/routes.ts`
- Navigation link trong sidebar/menu

**Dependencies:** None

---

### FR-006: Influencer xem danh sách Link đã tạo

**Priority:** Must Have

**Description:**
Influencer xem lại tất cả affiliate links đã tạo, grouped theo campaign. Backend API `GET /affiliate/my-links` đã có, cần **frontend page riêng** (hiện tại chỉ hiển thị inline trong campaign detail).

**Acceptance Criteria:**
- [ ] Trang riêng hiển thị danh sách links grouped theo campaign
- [ ] Mỗi link: campaign name, short link, ngày tạo
- [ ] Copy link nhanh (cả dài và ngắn)
- [ ] Link đến campaign detail
- [ ] Phân trang
- [ ] Responsive trên mobile

**Existing Assets:**
- Backend API: `GET /api/public/affiliate/my-links` ✅
- Frontend service: `affiliate.ts` → `getMyLinks()` ✅
- Interface: `IAffiliateLink` ✅

**Cần làm:**
- Frontend page mới: `frontend/src/pages/affiliate-links/index.tsx`
- Route mới trong `frontend/config/routes.ts`
- Navigation link trong sidebar/menu

**Dependencies:** None (API đã có)

---

### FR-007: Báo cáo Click

**Priority:** Must Have

**Description:**
Influencer xem báo cáo số lượt click affiliate links. Backend proxy Pub2 API 3.1.

**Acceptance Criteria:**
- [ ] Hiển thị tổng click trong khoảng thời gian chọn
- [ ] Biểu đồ click theo ngày (dữ liệu epoch time từ Pub2 → convert sang ngày)
- [ ] Lọc theo khoảng thời gian (max 3 tháng)
- [ ] Lọc theo campaign (optional, dropdown danh sách campaigns đã tham gia)
- [ ] Gọi Pub2 API on-demand khi user request
- [ ] Loading state khi đang fetch data
- [ ] Error state khi Pub2 API fail

**Existing Assets:**
- Pub2 Client method: `client.go` → `GetClickStats()` ✅

**Cần làm:**
- Backend: Public API endpoint `POST /api/public/affiliate-reports/clicks`
- Backend: Handler + Service trong `pkg/public/`
- Frontend: Report page component với chart library
- Frontend: Service method `getClickReport()`

**Dependencies:** FR-014 (Pub2 client — đã implement)

---

### FR-008: Báo cáo Conversion

**Priority:** Must Have

**Description:**
Influencer xem báo cáo số đơn hàng (conversions). Backend proxy Pub2 API 3.2.

**Acceptance Criteria:**
- [ ] Hiển thị tổng conversion trong khoảng thời gian
- [ ] Biểu đồ conversion theo ngày
- [ ] Lọc theo thời gian (max 3 tháng) và campaign
- [ ] Gọi Pub2 API on-demand
- [ ] Loading + error states

**Existing Assets:**
- Pub2 Client method: `client.go` → `GetConversionStats()` ✅

**Cần làm:**
- Backend: `POST /api/public/affiliate-reports/conversions`
- Frontend: Conversion chart component

**Dependencies:** FR-014

---

### FR-009: Báo cáo Sale Amount

**Priority:** Should Have

**Description:**
Influencer xem báo cáo giá trị đơn hàng (sale amount), phân theo trạng thái. Backend proxy Pub2 API 3.3.

**Acceptance Criteria:**
- [ ] Hiển thị tổng sale amount
- [ ] Phân theo trạng thái: REJECTED, WAITING_FOR_APPROVED, APPROVED, TEMPORARY_APPROVED
- [ ] Biểu đồ theo ngày
- [ ] Lọc theo thời gian (max 3 tháng) và campaign

**Existing Assets:**
- Pub2 Client method: `client.go` → `GetSaleAmountStats()` ✅

**Cần làm:**
- Backend: `POST /api/public/affiliate-reports/sale-amount`
- Frontend: Sale amount chart + status breakdown

**Dependencies:** FR-014

---

### FR-010: Báo cáo Commission (Hoa hồng)

**Priority:** Must Have

**Description:**
Influencer xem báo cáo hoa hồng, phân theo trạng thái. Backend proxy Pub2 API 3.4.

**Acceptance Criteria:**
- [ ] Hiển thị tổng commission
- [ ] Phân theo trạng thái: REJECTED, WAITING_FOR_APPROVED, APPROVED, TEMPORARY_APPROVED
- [ ] Biểu đồ theo ngày
- [ ] Lọc theo thời gian (max 3 tháng) và campaign

**Existing Assets:**
- Pub2 Client method: `client.go` → `GetCommissionStats()` ✅

**Cần làm:**
- Backend: `POST /api/public/affiliate-reports/commission`
- Frontend: Commission chart + status breakdown

**Dependencies:** FR-014

---

### FR-011: Danh sách đơn hàng chi tiết ✅

**Priority:** Must Have
**Status:** Implemented (2026-04-09) — integrated trong Commission Dashboard

**Description:**
Influencer xem danh sách đơn hàng chi tiết (conversions list). Backend proxy Pub2 API 8.

**Acceptance Criteria:**
- [x] Hiển thị danh sách đơn: campaign name, commission, trạng thái, ngày phát sinh
- [x] Phân trang (page, page_size) — backend hỗ trợ, frontend hiện top 50
- [x] Lọc theo campaign (sidebar chọn campaign hoặc "Tất cả")
- [ ] Lọc theo trạng thái — deferred (V2.1)
- [ ] Lọc theo campaign_invoice_ids — deferred
- [x] Hiển thị trạng thái đơn với màu: Chờ duyệt (#DC6803), Đã duyệt (#1570EF), Đã nhận (#079455), Từ chối (#B42318)
- [x] Icon theo status (3 SVG icons: waiting/approved/received)

**Implementation:**
- Backend: `POST /affiliate/reports/orders` ✅
- Frontend: Orders list integrated trong Commission Dashboard page ✅

**Dependencies:** FR-014

---

### FR-012: Commission Dashboard (Quản lý hoa hồng) ✅

**Priority:** Should Have → Implemented
**Status:** Implemented (2026-04-09)

**Description:**
Dashboard quản lý hoa hồng affiliate. Hiển thị commission breakdown theo status, danh sách đơn hàng, filter theo campaign.

**Acceptance Criteria:**
- [x] 3 Summary cards: Hoa hồng chờ duyệt, Hoa hồng đã duyệt, Hoa hồng đã nhận (gradient border)
- [x] Gọi Commission API (API 3.4) + Orders API (API 8)
- [x] Mặc định hiển thị dữ liệu 30 ngày gần nhất
- [x] Sidebar: danh sách campaigns đã tham gia + "Tất cả" (default)
- [x] Transaction list: campaign name, datetime, commission, status badge
- [x] 3 SVG icons theo design (waiting/approved/received)
- [x] Menu entry "Hoa hồng affiliate" trong avatar dropdown
- [x] Route `/hoa-hong-affiliate` với header + footer
- [ ] Cho phép thay đổi khoảng thời gian — deferred (V2.1)
- [ ] Loading skeleton cho mỗi card — deferred

**Implementation:**
- Frontend: `pages/affiliate-commission/` (index.tsx + index.scss)
- Frontend: 3 SVG icons trong `assets/icons/`
- Frontend: Avatar menu entry trong `profile.tsx`
- Frontend: Route + layout fix trong `routes.ts` + `home/index.tsx`
- Backend: `GET /affiliate/my-campaigns` + `POST /affiliate/reports/commission` + `POST /affiliate/reports/orders`

**Dependencies:** FR-016B

---

### FR-016B: Backend Report API Endpoints ✅

**Priority:** Must Have
**Status:** Implemented (2026-04-09)

**Description:**
Expose 6 report endpoints qua Public API. Pub2 client methods đã có, tạo handler/service/router layer.

**Acceptance Criteria:**
- [x] `POST /affiliate/reports/clicks` — proxy Pub2 API 3.1
- [x] `POST /affiliate/reports/conversions` — proxy Pub2 API 3.2
- [x] `POST /affiliate/reports/sale-amount` — proxy Pub2 API 3.3
- [x] `POST /affiliate/reports/commission` — proxy Pub2 API 3.4 (with `statistic_details` breakdown)
- [x] `POST /affiliate/reports/orders` — proxy Pub2 API 8
- [x] `GET /affiliate/my-campaigns` — user's joined campaigns (APPROVED contracts)
- [x] Tất cả require authentication + đã link AccessTrade
- [x] Tự động inject `sso_user_id` từ user data
- [x] Request validation: fromDate/toDate required
- [x] Response mapping: Pub2 response → Ambassador response format
- [x] `resolvePub2CampaignIDs`: convert MongoDB IDs → Pub2 campaign IDs
- [x] `formatPub2Date`: convert ISO UTC → VN timezone (+0700)
- [x] `ReportStatsResponse.StatisticDetails` parse breakdown per status

**Implementation:**
- `pkg/public/handler/affiliate.go` — 6 handler methods (5 reports + GetMyCampaigns)
- `pkg/public/service/affiliate.go` — `GetReportStats`, `GetReportOrders`, `GetMyCampaigns`
- `pkg/public/router/affiliate.go` — 6 routes under `/affiliate/reports/`
- `pkg/public/model/request/affiliate.go` — `AffiliateReportBody`, `AffiliateOrdersBody`
- `pkg/public/model/response/affiliate.go` — `AffiliateReportStatsResponse`, `AffiliateOrderItem`, `AffiliateOrdersResponse`
- `internal/module/pub2/models.go` — `ReportStatsDetail`, `StatisticDetails` in response
- `internal/service/affiliate.go` — `GetUserContracts`

**Dependencies:** FR-014 (Pub2 client — đã implement)

---

## Non-Functional Requirements

---

### NFR-001B: Performance — Report & Dashboard Response Time

**Priority:** Must Have

**Description:**
Report APIs phải responsive, dashboard aggregate không quá lâu.

**Acceptance Criteria:**
- [ ] Proxy APIs (Pub2 reports): < 3s cho 95% requests
- [ ] Dashboard aggregate (4 parallel API calls): < 5s
- [ ] Frontend loading states hiển thị ngay, không blank screen

**Rationale:** User experience — influencer không chờ lâu khi xem báo cáo

---

### NFR-004: Reliability — Error Handling & Circuit Breaker

**Priority:** Must Have

**Description:**
Xử lý graceful khi Pub2 API down hoặc trả lỗi. **Chưa implement circuit breaker.**

**Acceptance Criteria:**
- [ ] Pub2 API timeout: hiển thị thông báo "Hệ thống đang bận, vui lòng thử lại"
- [ ] Pub2 error response (code != PX00000): parse message và hiển thị cho user
- [ ] Retry logic: max 3 retries với exponential backoff cho network errors
- [ ] **Circuit breaker: nếu Pub2 fail liên tục > 5 lần → short-circuit 30s**

**Implementation Notes:**
- Có thể dùng Go library như `sony/gobreaker` hoặc `afex/hystrix-go`
- Implement tại `internal/module/pub2/client.go` level
- Cần per-endpoint circuit breaker (report APIs fail không block join/link APIs)

**Rationale:** Pub2 là external dependency, cần graceful degradation

---

### NFR-005B: Usability — Report Charts Responsive

**Priority:** Should Have

**Description:**
Biểu đồ báo cáo phải responsive và usable trên mobile.

**Acceptance Criteria:**
- [ ] Biểu đồ báo cáo responsive trên mobile (≥ 320px)
- [ ] Touch-friendly: tap để xem data point
- [ ] Landscape mode support cho charts
- [ ] Orders table: switch sang card view trên mobile

---

### NFR-008: Swagger API Documentation

**Priority:** Should Have

**Description:**
Bổ sung Swagger documentation cho tất cả affiliate API endpoints.

**Acceptance Criteria:**
- [ ] Public affiliate APIs documented trong `docs/public/swagger.yaml`
- [ ] Admin affiliate APIs documented trong `docs/admin/swagger.yaml`
- [ ] Request/response examples cho mỗi endpoint
- [ ] Error response format documented

---

## Epics

---

### EPIC-004: Affiliate Reports & Dashboard

**Description:**
Influencer xem báo cáo hiệu suất affiliate: clicks, conversions, sale amount, commission, danh sách đơn. Dashboard tổng hợp.

**Functional Requirements:**
- FR-016B: Backend Report API Endpoints ✅
- FR-007: Báo cáo Click
- FR-008: Báo cáo Conversion
- FR-009: Báo cáo Sale Amount
- FR-010: Báo cáo Commission
- FR-011: Danh sách đơn hàng chi tiết ✅
- FR-012: Commission Dashboard ✅

**Story Count Estimate:** 8-12 (FR-016B, FR-011, FR-012 done)

**Priority:** Must Have (FR-007, 008, 010 remaining), Should Have (FR-009)

**Business Value:** Transparency — influencer cần thấy hiệu suất để tiếp tục sử dụng

---

### EPIC-005: Affiliate Campaign Discovery, Links Management & Polish

**Description:**
Trang browse affiliate campaigns, trang quản lý links riêng, enhanced link generation, circuit breaker, Swagger docs.

**Functional Requirements:**
- FR-020: Enhanced Link Generation — Custom URL, Naming, History ✅
- FR-019: Browse danh sách affiliate campaigns
- FR-006: Danh sách links riêng

**Non-Functional Requirements:**
- NFR-004: Circuit breaker
- NFR-008: Swagger documentation

**Story Count Estimate:** 4-6 (FR-020 done)

**Priority:** Must Have (FR-019, FR-006, NFR-004), Should Have (NFR-008)

**Business Value:** Influencer khám phá campaigns dễ dàng hơn, hoàn thiện trải nghiệm, ổn định hệ thống

---

## User Stories

### EPIC-004: Reports & Dashboard

- As an **Influencer**, I want to see click statistics over time so that I know how my links perform.
- As an **Influencer**, I want to see conversion statistics so that I know how many orders my links generate.
- As an **Influencer**, I want to see my commission earnings by status (approved, pending, rejected) so that I know my actual and expected income.
- As an **Influencer**, I want to see a detailed list of my orders with status, amount, and commission so that I can track individual conversions.
- As an **Influencer**, I want to filter reports by date range and campaign so that I can analyze specific periods or campaigns.
- As an **Influencer**, I want a dashboard overview with summary cards so that I get a quick snapshot of my affiliate performance.

### EPIC-005: Campaign Discovery, Links Management & Polish

- As an **Influencer**, I want to browse all available affiliate campaigns in one place so that I can discover and join new campaigns without navigating through individual events.
- As an **Influencer**, I want a dedicated page listing all my generated affiliate links grouped by campaign so that I can easily find and reuse them.
- As a **System**, I want circuit breaker protection on Pub2 API calls so that failures don't cascade and degrade the entire platform.

---

## User Flows

### Flow 4: Influencer xem báo cáo

```
Influencer đã có affiliate links
  → Vào menu "Báo cáo Affiliate" (hoặc từ Dashboard)
  → Thấy Dashboard: 4 summary cards (Clicks, Conversions, Commission, Sale Amount)
  → Mặc định: dữ liệu 30 ngày gần nhất
  → Chọn tab cụ thể: "Click" / "Conversion" / "Hoa hồng" / "Đơn hàng"
  → Xem biểu đồ theo ngày
  → Lọc theo khoảng thời gian (date picker, max 3 tháng)
  → Lọc theo campaign (dropdown)
  → Tab "Đơn hàng": xem bảng chi tiết, phân trang, filter theo trạng thái
```

### Flow 6: Influencer browse affiliate campaigns

```
Influencer đã liên kết AccessTrade
  → Vào menu "Chiến Dịch Affiliate"
  → Thấy danh sách campaigns active, mới nhất trước
  → Scroll xuống để xem thêm (infinite scroll / pagination)
  → Click vào campaign → navigate đến trang chi tiết affiliate campaign
  → Từ đó có thể tham gia + tạo link (flow V1)
```

### Flow 5: Influencer quản lý links

```
Influencer đã tạo affiliate links
  → Vào menu "Link Affiliate"
  → Thấy danh sách links grouped theo campaign
  → Copy link nhanh (button copy)
  → Click vào campaign name → navigate đến campaign detail
  → Phân trang nếu nhiều links
```

---

## Dependencies

### Internal Dependencies

| Dependency | Mô tả | Status |
|-----------|--------|--------|
| V1 Implementation | Phase 1 đã implement xong | ✅ Done |
| Pub2 Client methods | `GetClickStats`, `GetConversionStats`, etc. | ✅ Có sẵn trong `client.go` |
| Authentication middleware | Auth + AccessTrade link check | ✅ Có sẵn |

### External Dependencies

| Dependency | Mô tả | Status |
|-----------|--------|--------|
| Pub2 API 3.1 (Click) | Report click statistics | ✅ Available |
| Pub2 API 3.2 (Conversion) | Report conversion statistics | ✅ Available |
| Pub2 API 3.3 (Sale Amount) | Report sale amount | ✅ Available |
| Pub2 API 3.4 (Commission) | Report commission | ✅ Available |
| Pub2 API 8 (Orders) | List conversions/orders | ✅ Available |
| Chart library (Frontend) | Biểu đồ cho reports | ⏳ Cần chọn (recharts / chart.js) |

---

## Assumptions

1. Pub2 report APIs (3.1→3.4, 8) ổn định và response format consistent
2. Frontend chart library tương thích với React 16 + Umi 3 hiện tại
3. Pub2 API rate limit đủ cho volume report requests (on-demand, không cache)
4. Report data từ Pub2 là near-real-time (có thể delay vài phút)
5. Influencer chủ yếu xem report 1-2 lần/ngày, không liên tục refresh

---

## Out of Scope (V2)

1. **Scheduled sync / caching reports** — Vẫn dùng on-demand, cache nếu cần là V3
2. **Webhook real-time** (Pub2 API 7 chưa có)
3. **Export reports** (CSV/PDF) — V3
4. **Email digest** báo cáo hàng tuần — V3
5. **Admin report dashboard** (admin xem tổng hợp tất cả influencers) — V3
6. **AI campaign recommendations** dựa trên performance data — V3
7. **Comparison charts** (so sánh giữa campaigns) — V3

---

## Open Questions

| # | Question | Owner | Status |
|---|----------|-------|--------|
| 1 | Chart library nào phù hợp? (recharts vs chart.js vs nivo) — cần tương thích React 16 | Engineering | Open |
| 2 | Report data có cache không? Nếu có thì TTL bao lâu? | Product + Engineering | Open |
| 3 | Dashboard cards có cần sparkline mini-chart không? | Design | Open |
| 4 | Mobile: orders table dùng card view hay horizontal scroll table? | Design | Open |
| 5 | Circuit breaker config: threshold bao nhiêu? Recovery time? | Engineering | Open |

---

## Approval & Sign-off

### Stakeholders

| Role | Name | Responsibility |
|------|------|---------------|
| Product Owner | TBD | Requirements approval |
| Engineering Lead | vinhnguyen | Technical feasibility, implementation |

### Approval Status

- [ ] Product Owner
- [ ] Engineering Lead

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-31 | vinhnguyen | Tách PRD V2 từ PRD gốc v1.3. Focus: Reports, Dashboard, Links page, Circuit breaker, Swagger docs. |
| 1.1 | 2026-04-01 | vinhnguyen | Bổ sung FR-019: Influencer browse danh sách affiliate campaigns (listing page). |
| 1.2 | 2026-04-09 | vinhnguyen | Thêm FR-020: Enhanced Link Generation (Custom URL, Naming, History). Implemented. UTM deferred. |
| 1.3 | 2026-04-09 | vinhnguyen | FR-016B, FR-012, FR-011 implemented. Commission Dashboard + 6 report endpoints. |
| 1.4 | 2026-04-09 | vinhnguyen | V2 marked COMPLETE. Remaining FRs (019, 006, 007-010) + NFRs (004, 008) deferred to V3. |

---

## Next Steps

### Recommended Implementation Order

```
✅ FR-020: Enhanced Link Generation — Custom URL, Naming, History (2026-04-09)
✅ FR-016B: 6 Backend Report API Endpoints (2026-04-09)
✅ FR-012: Commission Dashboard — Quản lý hoa hồng (2026-04-09)
✅ FR-011: Orders list — integrated trong Dashboard (2026-04-09)

V2 COMPLETE.
```

### Deferred to V3

Các items sau chuyển sang PRD V3:
- FR-019: Affiliate campaigns listing page
- FR-006: Links management page (trang riêng)
- FR-007 + FR-008 + FR-010: Report charts (Click, Conversion, Commission theo ngày)
- FR-009: Sale Amount report
- NFR-004: Circuit breaker cho Pub2 client
- NFR-008: Swagger documentation

### Architecture Notes

Backend report endpoints pattern (tất cả giống nhau):
```
Handler (validate request, inject sso_user_id)
  → Service (call Pub2 client method)
    → Pub2 Client (HMAC auth, HTTP call, parse response)
      → Return formatted response
```

Vì Pub2 client methods đã implement, effort chính là:
- **Backend:** ~2-3 ngày (boilerplate handler/service/router + request validation)
- **Frontend:** ~5-7 ngày (chart components, orders table, dashboard, links page)
- **Circuit breaker:** ~1 ngày

---

## Appendix A: Requirements Traceability Matrix

| Epic ID | Epic Name | Functional Requirements | NFRs | Story Count (Est.) |
|---------|-----------|-------------------------|------|-------------------|
| EPIC-004 | Reports & Dashboard | FR-007, FR-008, FR-009, FR-010, FR-011, FR-012, FR-016B | NFR-001B, NFR-005B | 8-12 |
| EPIC-005 | Campaign Discovery, Links Management & Polish | FR-019, FR-006 | NFR-004, NFR-008 | 4-6 |

**Total Estimated Stories:** 12-18

---

## Appendix B: Prioritization Details

### Functional Requirements

| Priority | Count | FRs |
|----------|-------|-----|
| **Must Have** | 8 | FR-020 ✅, FR-016B ✅, FR-011 ✅, FR-019, FR-006, FR-007, FR-008, FR-010 |
| **Should Have** | 2 | FR-009, FR-012 ✅ |

### Non-Functional Requirements

| Priority | Count | NFRs |
|----------|-------|------|
| **Must Have** | 2 | NFR-001B, NFR-004 |
| **Should Have** | 2 | NFR-005B, NFR-008 |

---

## Appendix C: Existing Pub2 Client Methods (Ready to Expose)

| Method | Pub2 API | File | Notes |
|--------|----------|------|-------|
| `GetClickStats()` | API 3.1 | `internal/module/pub2/client.go` | Request: date range, campaign_id, sso_user_id |
| `GetConversionStats()` | API 3.2 | `internal/module/pub2/client.go` | Request: date range, campaign_id, sso_user_id |
| `GetSaleAmountStats()` | API 3.3 | `internal/module/pub2/client.go` | Response includes status breakdown |
| `GetCommissionStats()` | API 3.4 | `internal/module/pub2/client.go` | Response includes status breakdown |
| `GetConversions()` | API 8 | `internal/module/pub2/client.go` | Supports pagination, filter by status |

---

**This document was created using BMAD Method v6 - Phase 2 (Planning)**
