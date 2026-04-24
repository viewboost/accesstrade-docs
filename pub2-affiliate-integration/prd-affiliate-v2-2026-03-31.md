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

**Scope V2 (final):**
1. **Enhanced Link Generation** — custom URL, naming, history (FR-020) ✅
2. **5 Public Report API endpoints** (proxy Pub2 APIs 3.1, 3.2, 3.3, 3.4, 8) (FR-016B) ✅
3. **Commission Dashboard baseline** — summary cards + orders list (FR-011, FR-012) ✅
4. **Trang browse affiliate campaigns** cho influencer (FR-019) ✅
5. **Trang quản lý links riêng** (FR-006) ✅
6. **Circuit breaker** cho Pub2 client (NFR-004) ✅
7. **Commission Dashboard Simplified** — refactor về KPI + list, không tabs/charts (FR-023) ✅
8. **Report charts** (click / conversion / sale-amount / commission theo ngày) — prototyped rồi **huỷ** (FR-007/8/9/10)
9. **Swagger documentation** — deferred (NFR-008)

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

### FR-019: Influencer browse danh sách Affiliate Campaigns ✅

**Priority:** Must Have
**Status:** Implemented (2026-04-16)

**Description:**
Influencer vào trang riêng để xem danh sách tất cả affiliate campaigns đang active.

**Acceptance Criteria:**
- [x] Trang riêng hiển thị danh sách affiliate campaigns có status = active
- [x] Sắp xếp theo ngày tạo mới nhất trước (descending)
- [x] Mỗi item hiển thị: banner, title, commission info, bonus info
- [x] Click vào item → navigate đến trang chi tiết affiliate campaign
- [x] Phân trang + search
- [x] Responsive mobile/desktop
- [x] Empty state khi không có campaigns

**Implementation:**
- Backend: `GET /api/public/affiliate-campaigns` (handler + service + router)
- Frontend page: `frontend/src/pages/affiliate-campaigns/index.tsx` + `index.scss`
- Frontend service: `affiliate.ts` → `getAllCampaigns()`
- Route: `frontend/config/routes.ts`

**Dependencies:** None

---

### FR-006: Influencer xem danh sách Link đã tạo ✅

**Priority:** Must Have
**Status:** Implemented (2026-04-16)

**Description:**
Influencer xem lại tất cả affiliate links đã tạo, grouped theo campaign.

**Acceptance Criteria:**
- [x] Trang riêng hiển thị danh sách links
- [x] Mỗi link: campaign name, short link, ngày tạo
- [x] Copy link nhanh
- [x] Link đến campaign detail
- [x] Phân trang
- [x] Responsive trên mobile

**Implementation:**
- Frontend page: `frontend/src/pages/affiliate-links/index.tsx` + `index.scss`
- Route: `frontend/config/routes.ts`
- Backend API: `GET /api/public/affiliate/my-links` (đã có từ V1)

**Dependencies:** None (API đã có)

---

### FR-007 / FR-008 / FR-009 / FR-010: Report Charts ❌ Cancelled

**Priority:** ~~Must Have / Should Have~~ Cancelled (2026-04-24)

**Cancelled items:**
- FR-007: Báo cáo Click (chart theo ngày)
- FR-008: Báo cáo Conversion (chart theo ngày)
- FR-009: Báo cáo Sale Amount (chart + status breakdown)
- FR-010: Báo cáo Commission (chart + status breakdown)

**Lý do huỷ:**
Khi prototype với recharts đã build xong, review UI thực tế cho thấy biểu đồ theo ngày trên khung thời gian ngắn (7/30/90 ngày) không cho insight đáng kể cho influencer. Data Pub2 sparse + UI tab-based tạo friction (6 tabs: Tổng quan / Lượt click / Đơn hàng / Hoa hồng / Doanh số / Chi tiết đơn) — giá trị thực tế nằm trọn ở KPI cards + list đơn.

**Thay thế bằng:** [FR-023 Commission Dashboard Simplified](#fr-023-commission-dashboard-simplified) — gộp về 1 view phẳng: 3 KPI cards commission theo trạng thái + danh sách đơn hàng. Loại bỏ tabs, charts, date filter.

**Backend assets vẫn giữ:** 5 report endpoints (`POST /affiliate/reports/clicks|conversions|sale-amount|commission|orders`) đã implement ở FR-016B → dùng lại cho FR-023 (commission + orders). Click / conversion / sale-amount endpoints tồn tại nhưng không có UI caller — giữ lại phòng trường hợp cần mở lại sau.

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

### FR-023: Commission Dashboard Simplified ✅

**Priority:** Must Have
**Status:** Implemented (2026-04-24)

**Description:**
Refactor trang `/hoa-hong-affiliate` (FR-012 baseline) về dạng 1 view phẳng: sidebar chọn campaign, header, 3 KPI cards commission theo trạng thái, và danh sách đơn hàng. Loại bỏ tabs, charts, date filter UI đã prototype. Đây là quyết định course-correction sau khi huỷ FR-007/8/9/10.

**Acceptance Criteria:**
- [x] Layout: sidebar trái (campaigns + "Tất cả" không icon) + main content (breadcrumb, header, 3 KPI, list đơn)
- [x] 3 KPI cards (gradient border, icon, tiền):
  - "Hoa hồng chờ duyệt" = `WAITING_FOR_APPROVED + TEMPORARY_APPROVED`
  - "Hoa hồng đã duyệt" = `APPROVED`
  - "Hoa hồng đã nhận" = `total - waiting - approved - rejected`
- [x] Danh sách đơn (tối đa 50): icon theo status, campaign name, sale time, commission, badge trạng thái
- [x] Load song song `reportCommission` + `reportOrders` khi mount và khi đổi campaign filter
- [x] Date range cố định 90 ngày, không lộ UI
- [x] Empty states
- [x] Responsive mobile

**Implementation:**
- Frontend refactor: `pages/affiliate-commission/index.tsx` + `index.scss` — gỡ tabs, `ReportChart`, date range buttons, recharts imports
- Backend: không đổi (tái sử dụng FR-016B endpoints)
- Bug fix kèm theo: thêm `TotalPubCommission` field vào `pub2.ReportStatsMeta` (Pub2 commission API trả `meta.total_pub_commission`, model thiếu field → KPI trước đó luôn bằng 0)
- Menu icon polish: đổi icon "Hoa hồng affiliate" trong avatar dropdown, bỏ icon "Tất cả" trong sidebar

**Out of scope (explicit):**
- Chart các metrics theo ngày
- Date filter 7/30/90 buttons
- Tab navigation
- Nút "Chia sẻ nhận hoa hồng"

**Dependencies:** FR-016B, FR-012

---

### FR-012: Commission Dashboard (Quản lý hoa hồng) ✅

**Priority:** Should Have → Implemented
**Status:** Implemented (2026-04-09), simplified by FR-023 (2026-04-24)

**Description:**
Dashboard quản lý hoa hồng affiliate. Hiển thị commission breakdown theo status, danh sách đơn hàng, filter theo campaign. **Layout hiện tại xem [FR-023](#fr-023-commission-dashboard-simplified)** (đã gỡ tabs + charts + date filter).

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

### NFR-004: Reliability — Error Handling & Circuit Breaker ✅

**Priority:** Must Have
**Status:** Implemented (2026-04-16)

**Description:**
Xử lý graceful khi Pub2 API down hoặc trả lỗi liên tục.

**Acceptance Criteria:**
- [x] Pub2 error response (code != PX00000): parse message và hiển thị cho user
- [x] Retry logic: max 3 retries với 500ms → 2s wait time (resty built-in) cho network errors
- [x] **Circuit breaker: Pub2 fail liên tục > 5 lần → short-circuit 30s**
- [x] Per-scope circuit breaker: `reportCB` (report APIs) và `mutationCB` (join/link APIs) tách biệt → lỗi report không block mutation
- [x] Frontend: hiện thông báo error từ backend khi circuit open

**Implementation:**
- Lightweight custom breaker tại `internal/module/pub2/circuit-breaker.go` (tránh thêm dependency)
- Applied tại mọi method của `pub2.Client` — mỗi method gọi `cb.allow()` trước khi hit HTTP, `cb.recordSuccess()/recordFailure()` sau
- State machine: CLOSED → OPEN (5 failures) → HALF_OPEN (sau 30s) → CLOSED (1 success) hoặc OPEN lại

---

### NFR-005B: Usability — Report Charts Responsive ❌ Cancelled

**Priority:** ~~Should Have~~ Cancelled (2026-04-24)

**Lý do:** Cùng lý do với FR-007/8/9/10 — không còn chart nào trên UI. Responsive requirement cho orders list + KPI cards được cover trong FR-023.

---

### NFR-008: Swagger API Documentation ⏳ Deferred

**Priority:** Should Have
**Status:** Deferred (low priority — `api-reference.md` hiện đủ dùng cho internal)

**Description:**
Bổ sung Swagger documentation cho tất cả affiliate API endpoints.

**Acceptance Criteria:**
- [ ] Public affiliate APIs documented trong `docs/public/swagger.yaml`
- [ ] Admin affiliate APIs documented trong `docs/admin/swagger.yaml`
- [ ] Request/response examples cho mỗi endpoint
- [ ] Error response format documented

---

### NFR-009: UTM Support (Pending Pub2) 🚫 Blocked

**Priority:** Should Have
**Status:** Blocked — chờ Pub2 confirm hỗ trợ

**Description:**
Pub2 API nhận UTM fields (`utm_source`, `utm_medium`, `utm_campaign`, `utm_content`) nhưng docs hiện ghi "Tạm thời không quan tâm". Khi Pub2 confirm → bật UTM builder trong link generation form.

**Acceptance Criteria:**
- [ ] UTM builder accordion trong link generation form (4 fields)
- [ ] Backend pass UTM to Pub2 `GenerateLinkRequest`
- [ ] Lưu UTM params vào `AffiliateLinkRaw`

**Existing Assets:** Go struct `pub2.GenerateLinkRequest` đã có sẵn 4 fields UTM (pointer string để nullable).

---

## Epics

---

### EPIC-004: Affiliate Reports & Dashboard ✅

**Description:**
Backend report endpoints + Commission Dashboard tối giản (KPI cards + danh sách đơn hàng). Không bao gồm chart-based reports (huỷ).

**Functional Requirements:**
- FR-016B: Backend Report API Endpoints ✅
- FR-011: Danh sách đơn hàng chi tiết ✅
- FR-012: Commission Dashboard (baseline) ✅
- FR-023: Commission Dashboard Simplified ✅
- ~~FR-007 / FR-008 / FR-009 / FR-010: Report Charts~~ ❌ Cancelled

**Business Value:** Transparency — influencer xem nhanh commission + list đơn

---

### EPIC-005: Affiliate Campaign Discovery, Links Management & Polish ✅

**Description:**
Trang browse affiliate campaigns, trang quản lý links riêng, enhanced link generation, circuit breaker.

**Functional Requirements:**
- FR-020: Enhanced Link Generation ✅
- FR-019: Browse danh sách affiliate campaigns ✅
- FR-006: Danh sách links riêng ✅

**Non-Functional Requirements:**
- NFR-004: Circuit breaker ✅
- NFR-008: Swagger documentation (deferred)

**Business Value:** Influencer khám phá campaigns dễ dàng hơn, hoàn thiện trải nghiệm, ổn định hệ thống

---

## User Stories

### EPIC-004: Reports & Dashboard

- As an **Influencer**, I want to see my commission earnings by status (approved, pending, received) so that I know my actual and expected income.
- As an **Influencer**, I want to see a detailed list of my orders with status, amount, and commission so that I can track individual conversions.
- As an **Influencer**, I want to filter orders & commission by campaign so that I can analyze individual campaigns.
- As an **Influencer**, I want a simple dashboard with KPI cards so that I get a quick snapshot without noise.

### EPIC-005: Campaign Discovery, Links Management & Polish

- As an **Influencer**, I want to browse all available affiliate campaigns in one place so that I can discover and join new campaigns without navigating through individual events.
- As an **Influencer**, I want a dedicated page listing all my generated affiliate links grouped by campaign so that I can easily find and reuse them.
- As a **System**, I want circuit breaker protection on Pub2 API calls so that failures don't cascade and degrade the entire platform.

---

## User Flows

### Flow 4: Influencer xem báo cáo hoa hồng

```
Influencer đã có affiliate links
  → Vào menu "Hoa hồng affiliate" (avatar dropdown)
  → Thấy trang Commission Dashboard:
      - Sidebar: danh sách campaigns đã tham gia + "Tất cả" (default)
      - 3 KPI cards: Chờ duyệt / Đã duyệt / Đã nhận (commission theo status)
      - Danh sách đơn hàng 90 ngày gần nhất (tối đa 50)
  → Click 1 campaign ở sidebar → KPI + list reload theo campaign đó
  → Click "Tất cả" → reset về tổng hợp toàn bộ campaigns
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
| ~~Chart library (Frontend)~~ | ~~Biểu đồ cho reports~~ | N/A — charts cancelled |

---

## Assumptions

1. Pub2 report APIs (3.1→3.4, 8) ổn định và response format consistent
2. Frontend chart library tương thích với React 16 + Umi 3 hiện tại
3. Pub2 API rate limit đủ cho volume report requests (on-demand, không cache)
4. Report data từ Pub2 là near-real-time (có thể delay vài phút)
5. Influencer chủ yếu xem report 1-2 lần/ngày, không liên tục refresh

---

## Out of Scope (V2)

1. **Chart-based reporting** (click / conversion / sale-amount / commission theo ngày) — prototyped rồi huỷ, xem [FR-007/8/9/10](#fr-007--fr-008--fr-009--fr-010-report-charts--cancelled). Có thể mở lại sau khi có insight khác về UX.
2. **Scheduled sync / caching reports** — vẫn dùng on-demand, không cần khi đã bỏ chart polling.
3. **Webhook real-time** (Pub2 API 7 chưa có).
4. **Export reports** (CSV/PDF).
5. **Email digest** báo cáo hàng tuần.
6. **Admin report dashboard** (admin xem tổng hợp tất cả influencers).
7. **AI campaign recommendations** dựa trên performance data.
8. **Comparison charts** (so sánh giữa campaigns).
9. **UTM support** — blocked chờ Pub2 confirm. Model Go đã có fields.

---

## Open Questions

| # | Question | Owner | Status |
|---|----------|-------|--------|
| 1 | Khi nào Pub2 hỗ trợ UTM fields? | Pub2 team | Blocked |
| 2 | Có cần mở lại charts sau này không? (Nếu Pub2 có realtime data dày hơn) | Product | Open |
| 3 | Dashboard có cần thêm "trending" badge / "Top campaign" metric không? | Product | Open |
| 4 | Production có cần verify lại KPI bằng data thật không? | QA | Open |

**Resolved:**
- ~~Chart library nào? (recharts / chart.js / nivo)~~ → Đã prototype recharts rồi huỷ (charts cancelled).
- ~~Report data caching TTL?~~ → Không cache, dùng on-demand.
- ~~Dashboard sparkline?~~ → Không (dashboard đã simplified).
- ~~Mobile orders: card view vs table?~~ → Card view (đã implement).
- ~~Circuit breaker config?~~ → 5 failures → OPEN 30s (đã implement).

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
| 1.4 | 2026-04-09 | vinhnguyen | V2 marked COMPLETE (partial). Remaining FRs (019, 006, 007-010) + NFRs (004, 008) deferred. |
| 1.5 | 2026-04-16 | vinhnguyen | FR-019, FR-006, NFR-004 implemented. Campaign listing page + Links page + Circuit breaker. |
| 1.6 | 2026-04-25 | vinhnguyen | Cancel FR-007/8/9/10 + NFR-005B (charts dropped after prototype). Add FR-023 Commission Dashboard Simplified. V3 draft archived, V2 now complete across all retained scope. |

---

## Next Steps

### Implementation Timeline

```
✅ FR-020: Enhanced Link Generation — Custom URL, Naming, History (2026-04-09)
✅ FR-016B: 6 Backend Report API Endpoints (2026-04-09)
✅ FR-012: Commission Dashboard baseline (2026-04-09)
✅ FR-011: Orders list — integrated trong Dashboard (2026-04-09)
✅ FR-019: Affiliate campaigns listing page (2026-04-16)
✅ FR-006: Links management page (2026-04-16)
✅ NFR-004: Circuit breaker (2026-04-16)
✅ FR-023: Commission Dashboard Simplified (2026-04-24)
❌ FR-007 / FR-008 / FR-009 / FR-010: Report charts — Cancelled (2026-04-24)
❌ NFR-005B: Report charts responsive — Cancelled (2026-04-24)
⏳ NFR-008: Swagger docs — deferred (low priority)
🚫 NFR-009: UTM — blocked by Pub2

V2 COMPLETE across all retained scope.
```

### Architecture Notes

Backend report endpoints pattern:
```
Handler (validate request, inject sso_user_id)
  → Service (call Pub2 client method with dev-only overrides if applicable)
    → Pub2 Client (HMAC auth, HTTP call, circuit breaker, retry, parse response)
      → Return formatted response
```

Circuit breaker scope: 2 instances — `reportCB` (report APIs) vs `mutationCB` (join / link). Failure trong report không block mutation flow.

Dev-only data: xem [api-reference.md §7 "Dev environment: seeded data & client-side overrides"](./api-reference.md#7-dev-environment-seeded-data--client-side-overrides).

---

## Appendix A: Requirements Traceability Matrix

| Epic ID | Epic Name | Functional Requirements | NFRs | Status |
|---|---|---|---|---|
| EPIC-004 | Reports & Dashboard | FR-011 ✅, FR-012 ✅, FR-016B ✅, FR-023 ✅ (FR-007/8/9/10 ❌ Cancelled) | NFR-001B, ~~NFR-005B~~ | Complete |
| EPIC-005 | Campaign Discovery, Links Management & Polish | FR-019 ✅, FR-006 ✅, FR-020 ✅ | NFR-004 ✅, NFR-008 ⏳ | Complete |

---

## Appendix B: Prioritization Details

### Functional Requirements

| Priority | Count | FRs |
|----------|-------|-----|
| **Must Have — Shipped** | 7 | FR-006 ✅, FR-011 ✅, FR-012 ✅, FR-016B ✅, FR-019 ✅, FR-020 ✅, FR-023 ✅ |
| **Cancelled** | 4 | ~~FR-007~~, ~~FR-008~~, ~~FR-009~~, ~~FR-010~~ |

### Non-Functional Requirements

| Priority | Count | NFRs |
|----------|-------|------|
| **Must Have — Shipped** | 1 | NFR-004 ✅ |
| **Must Have — Not tracked** | 1 | NFR-001B (performance — no SLO tracking in place) |
| **Should Have — Deferred** | 1 | NFR-008 (Swagger) |
| **Should Have — Cancelled** | 1 | ~~NFR-005B~~ |
| **Blocked** | 1 | NFR-009 (UTM — Pub2 side) |

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
