# Product Requirements Document: Affiliate FE Creator — Gen-Green

**Date:** 2026-05-04
**Author:** vinhnguyen
**Version:** 1.0
**Project Type:** Feature Integration (clone từ Ambassador)
**Project Level:** Level 3
**Status:** Draft
**Platform:** Gen-Green (`accesstrade-projects/vcreator/`)

---

## Document Overview

PRD này định nghĩa requirements cho **FE Creator** — phần creator Gen-Green sử dụng affiliate: browse chiến dịch, tham gia (join), tạo link affiliate, xem hoa hồng. Toàn bộ chức năng + UX **clone từ Ambassador frontend** (đã production, verified với 150K creators tương tự), chỉ adapt Scalef API + Gen-Green design system.

**Related Documents:**
- Overview: [fe-display-generate-link-report-overview.md](fe-display-generate-link-report-overview.md)
- Source clone: [`accesstrade-projects/ambassabor/frontend/src/pages/affiliate-*`](../../../ambassabor/frontend/src/pages/)
- Reference Ambassador V1: [`pub2-affiliate-integration/prd-affiliate-v1-2026-03-31.md`](../../pub2-affiliate-integration/prd-affiliate-v1-2026-03-31.md) — FR-004, FR-005, FR-013, FR-016, FR-017, FR-018
- Reference Ambassador V2: [`pub2-affiliate-integration/prd-affiliate-v2-2026-03-31.md`](../../pub2-affiliate-integration/prd-affiliate-v2-2026-03-31.md) — FR-006, FR-011, FR-012, FR-019, FR-020, FR-023
- Phụ thuộc: [Account Linking](account-linking-overview.md), [Admin Setup](admin-setup-overview.md)
- Scalef API: [scalef-api.md](scalef-api.md)

---

## Executive Summary

Sau khi Admin Setup chuẩn bị catalog affiliate + Account Linking gắn `scalef_user_id` vào user Gen-Green, track này xây dựng UI cho **creator dùng affiliate**:

- Browse chiến dịch affiliate ngay trong Event hiện có
- Tham gia chiến dịch (join contract với Scalef)
- Tạo affiliate link cá nhân để gắn vào nội dung
- Theo dõi hoa hồng + danh sách đơn hàng

**Strategy:** **Clone trực tiếp từ Ambassador frontend** thay vì build từ đầu:
- 4 page chính có sẵn ở Ambassador: `affiliate-campaigns`, `affiliate-campaign-detail`, `affiliate-links`, `affiliate-commission`
- Service layer + interfaces có sẵn (`services/affiliate.ts`)
- Logic UI states (PENDING/REJECTED retry, copy link, accordion sections, conflict resolution touchpoint) đều đã verified ở Ambassador

→ Effort thực tế ~12.5 ngày (V1 + V2), thấp hơn ~50% so với build từ đầu (~24 ngày).

**Điểm khác biệt với Ambassador:**
- Backend proxy gọi **Scalef API** (theo [scalef-api.md](scalef-api.md)), không phải Pub2
- Touchpoint linking dẫn sang **Scalef SSO OAuth** (Phase 1), không phải SSO AccessTrade
- Design system Gen-Green (màu, typography, branding)

---

## Product Goals

### Business Objectives

1. **Mở khoá doanh thu affiliate cho creator** — sau khi Admin Setup + Linking ready, creator có UI để dùng. Không có FE = data đã setup không tạo doanh thu.
2. **Đạt activation rate 40%** active users tạo affiliate link trong 3 tháng đầu (theo target Ambassador).
3. **Giảm time-to-first-link** — creator từ lúc thấy chiến dịch → tạo link xong < 2 phút.
4. **Minh bạch thu nhập** — creator xem được hoa hồng theo trạng thái (chờ duyệt / tạm duyệt / đã xác nhận) + chi tiết đơn hàng.

### Success Metrics

| Metric | Target | Timeframe |
|--------|--------|-----------|
| Tỷ lệ creator tạo affiliate link | 40% active users | 3 tháng sau launch |
| Activation rate (linked → joined → generated) | 60% | 3 tháng |
| Time-to-first-link (sau khi link Scalef) | < 2 phút | — |
| Tỉ lệ creator return xem báo cáo hoa hồng / tuần | 30% | 3 tháng |
| Page load FE creator (p95) | < 1.5s | — |

---

## Functional Requirements

Functional Requirements (FRs) define **what** the system does - specific features and behaviors.

Each requirement includes:
- **ID**: Unique identifier (FR-001, FR-002, etc.)
- **Priority**: Must Have / Should Have / Could Have (MoSCoW)
- **Description**: What the system should do
- **Acceptance Criteria**: How to verify it's complete
- **Ambassador Reference**: File / FR reference để clone

---

### FR-001: Section affiliate trong Event detail

**Priority:** Must Have

**Description:**
Khi creator vào chi tiết Event hiện có → thấy section "Chiến Dịch Affiliate Liên Kết" hiển thị các affiliate campaigns đã được admin liên kết với Event này.

**Acceptance Criteria:**
- [ ] Section hiển thị nếu Event có ≥ 1 affiliate campaign mapping (status=active, chưa qua end_date)
- [ ] Nếu Event không có affiliate liên kết → ẩn section
- [ ] Grid layout: 1 cột mobile, 2 cột desktop
- [ ] Banner liên kết Scalef trên đầu section nếu user chưa link (`user.scalef_user_id == null`)
- [ ] Section title: "Chiến Dịch Affiliate Liên Kết"
- [ ] Loading state + error state
- [ ] **Authorization:** Mọi creator đăng nhập đều xem được, không cần liên kết Scalef trước

**Ambassador Reference:**
- File clone: `ambassabor/frontend/src/pages/home/components/affiliate-campaigns-section/`
- Service: `affiliateService.getCampaignsByEvent(eventId)` ở `services/affiliate.ts`
- Ambassador FR-004 (V1) ✅ Implemented

**Dependencies:** Admin Setup track (mapping data), Account Linking track (touchpoint banner)

---

### FR-002: Affiliate Item Card

**Priority:** Must Have

**Description:**
Card hiển thị từng affiliate campaign trong section. Click → vào trang chi tiết.

**Acceptance Criteria:**
- [ ] Banner image (aspect ratio ~5:2, rounded top, object-fit cover)
- [ ] Title (font 18px/semibold, 1 line ellipsis)
- [ ] URL link (`scalef_campaign_url`, color xanh, mở tab mới)
- [ ] CTA button "Khám phá ngay" (gradient purple-pink, pill shape)
- [ ] 3 info badges (stack dọc trên mobile <576px):
  - **Hoa hồng** — icon dollar, value `commission_info` (required)
  - **Thưởng thêm** — icon gift, value `bonus_info` (— nếu rỗng)
  - **Thời gian** — icon calendar, format `dd/mm/yyyy - dd/mm/yyyy` hoặc `Đến dd/mm/yyyy`
- [ ] Card container: white bg, rounded 16px, shadow nhẹ, hover shadow tăng
- [ ] Click "Khám phá ngay" → navigate đến `/affiliate-campaign-detail/:id`
- [ ] Click khi chưa link Scalef → show popup yêu cầu liên kết

**Ambassador Reference:**
- File clone: `ambassabor/frontend/src/pages/home/components/affiliate-item-card/`
- Ambassador FR-004 (V1) ✅ Implemented

**Dependencies:** FR-001

---

### FR-003: Trang chi tiết Affiliate Campaign

**Priority:** Must Have

**Description:**
Trang full chi tiết của 1 affiliate campaign. Hiển thị banner, mô tả, accordion thông tin chi tiết, action buttons (Tham gia / Tạo link / Retry).

**Acceptance Criteria:**

**Layout (Desktop):**
- [ ] 2 cột ngang, gap 20px, max-width 1280px
- [ ] Cột trái (598px): Banner image + 3 info badges
- [ ] Cột phải (flex-grow): Title, description short, action area, AT linking banner, accordion sections
- [ ] Background #FAFAFA, mỗi cột rounded 20px white bg

**Layout (Mobile):**
- [ ] Stack dọc, single column
- [ ] Banner full width

**Cột phải — Action area:**
- [ ] State **CHƯA_LINK_SCALEF**: Banner Scalef linking + nút "Tham gia" disable
- [ ] State **CHƯA_JOIN**: Nút "Tham gia chiến dịch" (primary)
- [ ] State **JOINING**: Spinner, disable click
- [ ] State **PENDING**: Banner vàng "Yêu cầu đang được xử lý — Thử lại sau X giờ" + countdown 24h
- [ ] State **REJECTED**: Banner đỏ "Bạn chưa đủ điều kiện — Thử lại sau X ngày" + countdown 14 ngày
- [ ] State **APPROVED**: Nút "Tạo link affiliate" (primary)
- [ ] State **HAS_LINK**: Hiển thị link đã tạo + nút Copy + nút "Tạo link mới"

**Description sections (accordion):**
- [ ] Parse markdown từ field `desc` theo heading `##`
- [ ] Mỗi section là 1 accordion (mặc định section đầu mở)
- [ ] Toggle expand/collapse
- [ ] (V2) Tabs "Thể lệ" / "Hướng dẫn" — Ambassador V1 có nhưng simplify ở V2 → bỏ

**Ambassador Reference:**
- File clone: `ambassabor/frontend/src/pages/affiliate-campaign-detail/index.tsx` (672 dòng)
- Hàm `parseDescSections()` parse markdown → accordion items
- Service: `affiliateService.getCampaignDetail(campaignId)`, `getContract(campaignId)`
- Ambassador FR-018 (V1) ✅ Implemented

**Dependencies:** FR-001, Account Linking

---

### FR-004: Tham gia chiến dịch (Join)

**Priority:** Must Have

**Description:**
Creator bấm "Tham gia chiến dịch" → BE proxy gọi Scalef `/campaigns/join` để tạo contract. Xử lý 3 trạng thái: APPROVED / PENDING / REJECTED với retry logic.

**Acceptance Criteria:**

**Pre-conditions:**
- [ ] Yêu cầu user đã `scalef_user_id != null` (đã link Scalef)
- [ ] Yêu cầu chưa join chiến dịch này (chưa có contract record)

**Action flow:**
- [ ] Click "Tham gia" → optimistic loading state
- [ ] BE gọi Scalef API → save contract (`contract_no`, `status`) vào MongoDB Gen-Green
- [ ] Hiển thị trạng thái contract:
  - **APPROVED** → toast "Đã tham gia chiến dịch" + chuyển sang state `APPROVED` (hiện nút "Tạo link")
  - **PENDING** → banner vàng + countdown 24h + nút "Thử lại" (disabled cho đến khi hết 24h)
  - **REJECTED** → banner đỏ + countdown 14 ngày + nút "Thử lại"

**Retry mechanism:**
- [ ] BE tính `canRetry` (bool) + `retryAfter` (timestamp) dựa vào `updatedAt` + ENV config
- [ ] ENV config: `AFFILIATE_RETRY_PENDING_SECONDS` (default 86400 = 24h), `AFFILIATE_RETRY_REJECTED_SECONDS` (default 1209600 = 14d)
- [ ] `canRetry=true` → enable nút "Thử lại" → click → BE gọi lại Scalef
- [ ] `canRetry=false` → disable nút + countdown text

**Error handling:**
- [ ] Map Scalef error code → message tiếng Việt thân thiện
- [ ] Network error → toast "Có lỗi, vui lòng thử lại"
- [ ] Scalef timeout → toast "Hệ thống đang chậm, thử lại sau"

**Ambassador Reference:**
- Service: `affiliateService.joinCampaign(campaignId)` — `services/affiliate.ts:17`
- File: `affiliate-campaign-detail/index.tsx:188 handleJoinCampaign()`
- Ambassador FR-017 (V1) ✅ Implemented (đầy đủ retry logic)

**Dependencies:** FR-003, Scalef API `POST /campaigns/join`

---

### FR-005: Tạo link affiliate

**Priority:** Must Have

**Description:**
Sau khi contract APPROVED, creator tạo affiliate link cá nhân. BE proxy gọi Scalef `/campaigns/generate-link`.

**Acceptance Criteria:**

**Pre-conditions:**
- [ ] Đã link Scalef + đã APPROVED contract

**Form input:**
- [ ] Bấm "Tạo link affiliate" → modal mở
- [ ] Field **Custom URL** (optional): URL sản phẩm cụ thể trong campaign — nếu rỗng dùng `scalef_campaign_url` default
- [ ] Field **Tên link** (optional): để creator note/đặt tên link cho dễ quản lý
- [ ] Validate Custom URL format (nếu nhập)

**Output:**
- [ ] BE gọi Scalef → trả `deeplink` (full) + `short_link` (rút gọn)
- [ ] Hiển thị 2 link với nút Copy riêng từng link
- [ ] Toast "Đã copy link" khi click copy
- [ ] Lưu link vào MongoDB Gen-Green (`affiliate_links` collection) — kèm `name` nếu user nhập
- [ ] Nút "Tạo link mới" cho phép tạo lại

**Error:**
- [ ] Map Scalef error
- [ ] Nếu Custom URL invalid → inline error trong modal

**Ambassador Reference:**
- Service: `affiliateService.generateLink(campaignId, {originalUrl?, name?})` — `services/affiliate.ts:29`
- File: `affiliate-campaign-detail/index.tsx:216 handleGenerateLink()`
- Ambassador FR-005 (V1) + FR-020 (V2 — Enhanced với custom URL/name) ✅ Implemented

**Dependencies:** FR-004, Scalef API `POST /campaigns/generate-link`

---

### FR-006: Trang "Link affiliate của tôi"

**Priority:** Must Have

**Description:**
Trang riêng `/affiliate-links` hiển thị danh sách link creator đã tạo. Group theo chiến dịch.

**Acceptance Criteria:**
- [ ] Title page: "Link Affiliate của bạn"
- [ ] Search box: tìm theo tên link / URL / chiến dịch
- [ ] Group by campaign — mỗi group có heading là tên chiến dịch
- [ ] Mỗi link row hiển thị:
  - Tên link (nếu user đặt) hoặc default "Link #ID"
  - `short_link` (font monospace, copy được)
  - `deeplink` (truncate, copy được)
  - Ngày tạo
  - Nút "Sao chép link rút gọn" + "Sao chép link đầy đủ"
- [ ] Empty state: "Bạn chưa tạo link nào" với CTA browse chiến dịch
- [ ] Empty search state: "Không tìm thấy link nào"
- [ ] Pagination hoặc infinite scroll (Ambassador hiện top 50)

**Ambassador Reference:**
- File clone: `ambassabor/frontend/src/pages/affiliate-links/index.tsx` (269 dòng)
- Service: `affiliateService.getMyLinks()` — `services/affiliate.ts:36`
- Ambassador FR-006 (V2) ✅ Implemented

**Dependencies:** FR-005

---

### FR-007: Trang "Browse chiến dịch affiliate"

**Priority:** Must Have

**Description:**
Trang `/affiliate-campaigns` hiển thị **toàn bộ** chiến dịch affiliate active (không phụ thuộc Event). Khác với FR-001 (chỉ trong context Event).

**Acceptance Criteria:**
- [ ] Title: "Chiến dịch Affiliate"
- [ ] Grid card affiliate (tái dùng AffiliateItemCard từ FR-002)
- [ ] Filter (V2): theo partner, theo category
- [ ] Search theo title
- [ ] Pagination (page, limit)
- [ ] Empty state nếu không có chiến dịch nào active
- [ ] Click card → trang detail (FR-003)

**Ambassador Reference:**
- File clone: `ambassabor/frontend/src/pages/affiliate-campaigns/index.tsx` (242 dòng)
- Service: `affiliateService.getAllCampaigns(params)` — `services/affiliate.ts:67`
- Ambassador FR-019 (V2) ✅ Implemented

**Dependencies:** FR-002, Admin Setup

---

### FR-008: Touchpoint liên kết Scalef (Banner + Popup)

**Priority:** Must Have

**Description:**
Khi creator chưa link Scalef nhưng cố dùng affiliate, hệ thống chặn hoặc gợi ý liên kết. Có 2 dạng touchpoint:

**Acceptance Criteria:**

**Banner (passive):**
- [ ] Hiển thị trên đầu section affiliate trong Event detail (FR-001) khi `user.scalef_user_id == null`
- [ ] Hiển thị trên đầu cột phải trang chi tiết affiliate (FR-003)
- [ ] CTA "Liên kết tài khoản Scalef" → redirect sang flow [Account Linking](account-linking-overview.md)
- [ ] Auto ẩn khi user đã link

**Popup (chặn action):**
- [ ] Trigger khi user click "Khám phá ngay" / "Tham gia" / "Tạo link" mà chưa link
- [ ] Title: "Cần liên kết Scalef trước khi tham gia"
- [ ] Body: "Để tham gia chiến dịch affiliate và kiếm hoa hồng, bạn cần liên kết tài khoản Scalef."
- [ ] 2 nút: "Liên kết ngay" (primary, → flow linking) | "Để sau" (secondary, đóng popup)
- [ ] Sau khi link xong → redirect về đúng trang trước đó (preserve context)

**Ambassador Reference:**
- AT Linking Banner trong campaign detail + popup component
- Ambassador FR-013 (V1) ✅ Implemented

**Dependencies:** Account Linking track

---

### FR-009: Trang "Hoa hồng của tôi" (Commission Dashboard)

**Priority:** Should Have (V2)

**Description:**
Trang `/affiliate-commission` hiển thị hoa hồng + danh sách đơn hàng. **Layout simplified theo Ambassador V2 (FR-023):** chỉ KPI cards + orders list, **không** có chart, **không** có tabs.

**Acceptance Criteria:**

**Layout:**
- [ ] Title page: "Hoa hồng của bạn"
- [ ] Subtitle: tên chiến dịch đang chọn (hoặc "Tổng hợp tất cả chiến dịch")
- [ ] Sidebar trái (desktop): list chiến dịch đã tham gia + option "Tất cả"
- [ ] Mobile: dropdown chọn chiến dịch ở đầu

**Date range filter:**
- [ ] 4 preset: 7 ngày / 1 tháng / 3 tháng / Custom
- [ ] Custom: RangePicker (max 3 tháng — limit Scalef)
- [ ] Default: 1 tháng gần nhất

**3 KPI cards:**
- [ ] Card 1 — **Hoa hồng chờ duyệt** (pending) — icon waiting, color cam
- [ ] Card 2 — **Hoa hồng tạm duyệt** (pre-approved) — icon approved, color xanh dương
- [ ] Card 3 — **Hoa hồng đã xác nhận** (approved) — icon received, color xanh lá
- [ ] Mỗi card: amount (format VND) + label

**Orders list (table):**
- [ ] Title: "Danh sách đơn hàng"
- [ ] Columns: Campaign name, Order ID, Sale amount, Commission, Status badge, Ngày phát sinh
- [ ] Status badges với màu: Chờ duyệt (#DC6803), Đã duyệt (#1570EF), Đã nhận (#079455), Từ chối (#B42318)
- [ ] Pagination (BE hỗ trợ, FE hiện top 50)
- [ ] Filter campaign từ sidebar tự apply

**KHÔNG có (theo simplification V2):**
- [ ] ~~Tabs Tổng quan / Click / Conversion / Sale~~ — bỏ
- [ ] ~~Charts theo ngày~~ — bỏ
- [ ] ~~Filter trạng thái đơn~~ — Ambassador không có, Gen-Green cũng không làm
- [ ] ~~Export CSV~~ — Ambassador không có, Gen-Green cũng không làm

**Ambassador Reference:**
- File clone: `ambassabor/frontend/src/pages/affiliate-commission/index.tsx` (403 dòng)
- Service: `affiliateService.reportCommission()`, `reportOrders()` — `services/affiliate.ts:47-54`
- Ambassador FR-011 + FR-012 + FR-023 (V2) ✅ Implemented

**Dependencies:** FR-006, Scalef Report APIs (`POST /report/click`, `POST /report/overview`, `GET /publisher/conversion`)

---

### FR-010: Service layer + Interfaces (Frontend)

**Priority:** Must Have

**Description:**
Service module gọi BE proxy + TypeScript interfaces cho data structure.

**Acceptance Criteria:**
- [ ] File `services/affiliate.ts` clone từ Ambassador, replace endpoints theo Gen-Green BE
- [ ] Interfaces TypeScript cho: `AffiliateCampaign`, `AffiliateContract`, `AffiliateLink`, `CommissionReport`, `Order`
- [ ] 11 service methods (clone Ambassador):
  - `getCampaignsByEvent(eventId)` — FR-001
  - `getCampaignDetail(campaignId)` — FR-003
  - `joinCampaign(campaignId)` — FR-004
  - `getContract(campaignId)` — FR-004 (status check)
  - `generateLink(campaignId, {originalUrl?, name?})` — FR-005
  - `getMyLinks(params?)` — FR-006
  - `getMyCampaigns()` — FR-009 (sidebar)
  - `reportCommission(data)` — FR-009
  - `reportOrders(data)` — FR-009
  - `getAllCampaigns(params?)` — FR-007
  - `reportClicks/Conversions/SaleAmount(data)` — keep stub, không có UI caller
- [ ] ApiConst config riêng cho Gen-Green
- [ ] Error handling chung qua `request.call()` utility

**Ambassador Reference:** `ambassabor/frontend/src/services/affiliate.ts` (72 dòng)

**Dependencies:** Backend proxy endpoints

---

### FR-011: BE Proxy Scalef APIs (Backend Foundation)

**Priority:** Must Have

**Description:**
Gen-Green backend proxy gọi Scalef APIs theo spec [scalef-api.md](scalef-api.md). Đây là backbone cho tất cả FR-001 → FR-009.

**Acceptance Criteria:**

**Scalef Client module:**
- [ ] Tạo `internal/module/scalef/client.go` (clone pattern Ambassador `internal/module/pub2/`)
- [ ] HMAC-SHA256 signature theo spec Scalef:
  - Login: `hash_hmac('sha256', timestamp + client_id, client_secret)`
  - Other APIs: `hash_hmac('sha256', timestamp + ref_user_id, client_secret)`
- [ ] Headers: `X-Port-Type: PUB`, `X-Client-Id`, `X-Ref-User-Id`, `X-Timestamp`, `X-Signature`
- [ ] Timeout 10s default
- [ ] Logging request/response vào collection `scalef_api_logs`

**Public endpoints (cho creator):**
- [ ] `GET /events/:id/affiliate-campaigns` (FR-001)
- [ ] `GET /affiliate-campaigns/:id` (FR-003)
- [ ] `POST /affiliate-campaigns/:id/join` + `GET /:id/contract` (FR-004)
- [ ] `POST /affiliate-campaigns/:id/generate-link` (FR-005)
- [ ] `GET /affiliate-links` (FR-006)
- [ ] `GET /affiliate-campaigns` (FR-007 — list all)
- [ ] `GET /affiliate-campaigns/me` (FR-009 sidebar — joined campaigns)
- [ ] `POST /affiliate-reports/commission` (FR-009)
- [ ] `POST /affiliate-reports/orders` (FR-009)
- [ ] (Stub) `POST /affiliate-reports/{clicks,conversions,sale-amount}` — endpoint exist nhưng không có UI caller (giống Ambassador)

**Tenant isolation:**
- [ ] Mọi public endpoint yêu cầu auth + `user.scalef_user_id != null` (trả 403 với code `SCALEF_NOT_LINKED` để FE bắt show popup)
- [ ] Inject `X-Ref-User-Id = user.scalef_user_id` từ session, không trust client

**Local cache + storage:**
- [ ] Collection mới: `affiliate_contracts` (user_id, affiliate_campaign_id, contract_no, status, retry_at)
- [ ] Collection mới: `affiliate_links` (user_id, affiliate_campaign_id, name, short_link, deeplink, original_url, created_at)
- [ ] Collection mới: `scalef_api_logs` (TTL 90 ngày)

**Ambassador Reference:** `ambassabor/backend/internal/module/pub2/`, `pkg/public/handler/affiliate.go`

**Dependencies:** Scalef API spec ([scalef-api.md](scalef-api.md)), Account Linking (set `scalef_user_id`)

---

### FR-012: Tracking events (Analytics)

**Priority:** Should Have

**Description:**
Track creator behavior trên affiliate funnel để đo activation + conversion.

**Acceptance Criteria:**
- [ ] Event `affiliate_section_viewed` — section hiển thị trong Event detail
- [ ] Event `affiliate_campaign_clicked` — click card
- [ ] Event `at_linking_banner_clicked` — click banner Scalef
- [ ] Event `at_linking_popup_shown` — popup chặn hiển thị
- [ ] Event `affiliate_join_clicked` — bấm "Tham gia"
- [ ] Event `affiliate_join_result` — kèm status APPROVED/PENDING/REJECTED
- [ ] Event `affiliate_link_generated` — tạo link thành công
- [ ] Event `affiliate_link_copied` — bấm copy
- [ ] Event `affiliate_retry_clicked` — bấm retry
- [ ] Reuse analytics infrastructure hiện có của Gen-Green (Firebase / GTM)

**Ambassador Reference:** Ambassador không có FR riêng cho analytics — nếu Gen-Green đã có pattern thì reuse

**Dependencies:** Gen-Green analytics framework

---

## Non-Functional Requirements

Non-Functional Requirements (NFRs) define **how** the system performs - quality attributes and constraints.

---

### NFR-001: Performance — Page Load Time

**Priority:** Must Have

**Description:**
Page render đủ nhanh để creator không bỏ giữa flow.

**Acceptance Criteria:**
- [ ] Section affiliate trong Event detail: render < 500ms (cache hit) / < 2s (cache miss)
- [ ] Trang chi tiết affiliate: first paint < 1.5s
- [ ] Generate link API call: p95 < 3s (BE proxy Scalef, network bound)
- [ ] Copy link: instant (< 100ms)
- [ ] My links page: < 1s for top 50 records
- [ ] Commission dashboard: < 2s (multiple Scalef API calls)

**Rationale:**
Creator có nhiều cách kiếm tiền khác — page chậm = drop off cao.

---

### NFR-002: Performance — Mobile Bundle Size

**Priority:** Should Have

**Description:**
Tối ưu bundle size để không impact các tính năng hiện có.

**Acceptance Criteria:**
- [ ] Bundle size tăng thêm < 50KB gzipped sau khi thêm 4 page affiliate
- [ ] Lazy-load (route-level code split) cho `affiliate-campaign-detail`, `affiliate-links`, `affiliate-commission`, `affiliate-campaigns`
- [ ] Tree-shake unused chart libraries (theo cancel chart từ Ambassador V2)

**Rationale:**
Mobile chiếm > 70% creator base. Bundle size = battery + data cost.

---

### NFR-003: Security — Authentication & Authorization

**Priority:** Must Have

**Description:**
Bảo vệ data creator + credentials Scalef.

**Acceptance Criteria:**
- [ ] Tất cả public APIs yêu cầu valid session (reuse Gen-Green auth)
- [ ] Action affiliate (join, generate link, view links, view commission) yêu cầu `user.scalef_user_id != null` — BE trả 403 + code `SCALEF_NOT_LINKED` nếu chưa link
- [ ] **Scalef credentials (HMAC client_id/secret) chỉ ở backend** — không lộ ra browser
- [ ] **`scalef_user_id` inject từ session backend**, không trust client param/body
- [ ] Affiliate links chỉ thuộc user đã tạo — query luôn filter `user_id = session.user_id`
- [ ] Rate limit: generate-link 60 req/min/user (chống spam)

**Rationale:**
Multi-tenant. Affiliate liên quan tiền — phải chặn cross-user data leak.

---

### NFR-004: Reliability — Error Handling & Retry

**Priority:** Must Have

**Description:**
Scalef API có thể chậm/timeout/lỗi — không để creator stuck.

**Acceptance Criteria:**
- [ ] Mọi error từ BE/Scalef có message tiếng Việt thân thiện (KHÔNG raw error code)
- [ ] Network timeout → toast "Mất kết nối, vui lòng thử lại" + retry button
- [ ] Scalef timeout → toast "Hệ thống đang chậm, thử lại sau"
- [ ] Scalef 5xx → BE retry 3 lần với exponential backoff (1s, 2s, 4s)
- [ ] Pub2/Scalef circuit breaker pattern (theo Ambassador NFR-004) — sau 5 fail consecutive → open circuit 1 phút
- [ ] User chưa link Scalef → KHÔNG gọi Scalef API, hiện popup linking ngay
- [ ] Logs: mọi Scalef call ghi `scalef_api_logs` để debug

**Rationale:**
Affiliate là feature mới — lỗi đầu mở app sẽ ảnh hưởng lòng tin creator.

---

### NFR-005: Usability — Mobile Responsive

**Priority:** Must Have

**Description:**
Mobile-first cho creator base 70%+ mobile.

**Acceptance Criteria:**
- [ ] Mọi page hoạt động ≥ 320px width
- [ ] Touch target ≥ 44x44px cho action buttons
- [ ] Copy link hoạt động trên mobile (clipboard API + fallback select-all)
- [ ] Modal generate link full-screen trên mobile, dialog trên desktop
- [ ] Sidebar campaign list (commission page) → dropdown trên mobile
- [ ] Date range picker mobile-friendly

**Rationale:**
70%+ creator dùng mobile. Mobile UX kém = drop off.

---

### NFR-006: Compatibility — Existing Gen-Green System

**Priority:** Must Have

**Description:**
Không phá vỡ tính năng hiện có khi thêm affiliate.

**Acceptance Criteria:**
- [ ] Routes mới (`/affiliate-campaigns`, `/affiliate-campaign-detail/:id`, `/affiliate-links`, `/affiliate-commission`) không conflict
- [ ] Section affiliate trong Event detail là component nhúng — không thay đổi Event detail layout cũ
- [ ] Reuse design system Gen-Green (button, card, modal, toast components)
- [ ] Reuse auth + permission framework
- [ ] Reuse `request.call()` HTTP utility hiện có

**Rationale:**
Avoid regression. Gen-Green có 150K active users — không downtime.

---

### NFR-007: Maintainability — Clone Strategy

**Priority:** Must Have

**Description:**
Clone từ Ambassador để giảm risk + effort, nhưng phải maintainable lâu dài.

**Acceptance Criteria:**
- [ ] Code clone phải document `// Cloned from ambassabor/frontend/src/pages/affiliate-X` ở đầu file
- [ ] Adapt theo Gen-Green design system (KHÔNG copy nguyên class CSS Ambassador)
- [ ] Service layer thay endpoints, KHÔNG copy ApiConst Ambassador
- [ ] Test cases adapt từ Ambassador test suite (nếu có)
- [ ] README ghi rõ "FE Creator clone từ Ambassador X version" để dev tương lai biết source

**Rationale:**
Future divergence: Gen-Green vs Ambassador có thể tách hẳn. Cần truy được nguồn gốc khi maintain.

---

### NFR-008: Accessibility (Basic)

**Priority:** Should Have

**Description:**
Cơ bản a11y — không full WCAG nhưng đảm bảo hữu dụng.

**Acceptance Criteria:**
- [ ] Mọi button có `aria-label` (đặc biệt icon-only buttons)
- [ ] Modal có focus trap + ESC to close
- [ ] Color contrast text/background ≥ 4.5:1
- [ ] Keyboard navigation cho tab list + accordion
- [ ] Screen reader announce trạng thái contract change

**Rationale:**
Compliance + một số creator có disability.

---

## Epics

Epics are logical groupings of related functionality that will be broken down into user stories during sprint planning.

---

### EPIC-001: Affiliate Discovery (Browse + Detail)

**Description:**
Creator browse chiến dịch affiliate (trong Event hoặc standalone), xem chi tiết.

**Functional Requirements:**
- FR-001 (Section trong Event)
- FR-002 (Affiliate card)
- FR-003 (Detail page)
- FR-007 (Browse all campaigns)

**Story Count Estimate:** 5-7

**Priority:** Must Have

**Business Value:**
Bước đầu funnel — creator phải thấy chiến dịch trước khi join.

---

### EPIC-002: Join + Generate Link Flow

**Description:**
Creator tham gia chiến dịch + tạo affiliate link cá nhân. Includes retry logic cho PENDING/REJECTED.

**Functional Requirements:**
- FR-004 (Join campaign + retry)
- FR-005 (Generate link)
- FR-006 (My links page)

**Story Count Estimate:** 5-7

**Priority:** Must Have

**Business Value:**
Chuyển đổi chính của FE Creator — không có epic này = không có doanh thu affiliate.

---

### EPIC-003: Touchpoint Liên kết Scalef

**Description:**
Banner + popup hướng creator chưa link Scalef đi qua flow Account Linking.

**Functional Requirements:**
- FR-008 (Touchpoint banner + popup)

**Story Count Estimate:** 2-3

**Priority:** Must Have

**Business Value:**
Cầu nối giữa FE Creator và Account Linking. Conversion rate phụ thuộc UX touchpoint.

---

### EPIC-004: Backend Foundation (Scalef Proxy)

**Description:**
BE Gen-Green proxy gọi Scalef APIs. Backbone cho mọi FR khác.

**Functional Requirements:**
- FR-010 (Service layer FE)
- FR-011 (BE proxy module + endpoints)

**Story Count Estimate:** 6-8

**Priority:** Must Have

**Business Value:**
Không có epic này = không có FR nào hoạt động được.

---

### EPIC-005: Commission Dashboard (V2)

**Description:**
Trang hoa hồng + đơn hàng. Simplified theo Ambassador V2 (KPI cards + orders list, không charts).

**Functional Requirements:**
- FR-009 (Commission dashboard)

**Story Count Estimate:** 3-4

**Priority:** Should Have

**Business Value:**
Minh bạch thu nhập = giữ creator. Có thể launch sau V1 nếu cần ship sớm.

---

### EPIC-006: Analytics & Polish

**Description:**
Tracking events + a11y + performance optimization.

**Functional Requirements:**
- FR-012 (Tracking events)
- NFR-008 (Accessibility)

**Story Count Estimate:** 2-3

**Priority:** Should Have

**Business Value:**
Đo được hiệu quả launch + đảm bảo chất lượng baseline.

---

## User Stories (High-Level)

### EPIC-001 stories

- **US-001:** As a creator, I want to xem các chiến dịch affiliate trong Event đang quan tâm so that biết Event này có cơ hội kiếm hoa hồng không.
- **US-002:** As a creator, I want to xem chi tiết chiến dịch affiliate (mô tả, hoa hồng, thưởng, thể lệ) so that quyết định có tham gia hay không.
- **US-003:** As a creator, I want to browse tất cả chiến dịch affiliate active (không chỉ trong Event) so that khám phá thêm cơ hội.

### EPIC-002 stories

- **US-004:** As a creator (đã link Scalef), I want to tham gia chiến dịch affiliate so that bắt đầu kiếm hoa hồng.
- **US-005:** As a creator có contract PENDING, I want to thấy countdown 24h và nút "Thử lại" so that biết khi nào có thể retry.
- **US-006:** As a creator có contract REJECTED, I want to thấy lý do + countdown 14 ngày so that hiểu mình thiếu điều kiện gì.
- **US-007:** As a creator (APPROVED), I want to tạo link affiliate với URL tuỳ chỉnh + tên gợi nhớ so that gắn link đúng vào nội dung và quản lý dễ.
- **US-008:** As a creator, I want to copy link rút gọn / link đầy đủ với 1 click so that paste vào video/bio nhanh.
- **US-009:** As a creator, I want to xem danh sách link đã tạo (group theo chiến dịch + search) so that tìm lại link cũ.

### EPIC-003 stories

- **US-010:** As a creator chưa link Scalef, I want to thấy banner gợi ý liên kết trong section affiliate so that biết bước tiếp theo.
- **US-011:** As a creator chưa link Scalef, I want to bấm action affiliate thì thấy popup chặn rõ ràng so that không bị confused.

### EPIC-004 stories

- **US-012:** As BE dev, I want to scalef client module với HMAC signature đúng spec so that gọi Scalef API safely.
- **US-013:** As BE dev, I want to log mọi Scalef request/response vào `scalef_api_logs` so that debug khi có issue.
- **US-014:** As BE dev, I want to circuit breaker cho Scalef client so that không cascade fail khi Scalef down.

### EPIC-005 stories (V2)

- **US-015:** As a creator, I want to xem 3 card hoa hồng (chờ duyệt / tạm duyệt / đã xác nhận) so that biết tổng quan thu nhập.
- **US-016:** As a creator, I want to filter hoa hồng theo thời gian + chiến dịch so that phân tích kênh nào hiệu quả.
- **US-017:** As a creator, I want to xem danh sách đơn hàng chi tiết với status badge màu so that track từng order.

### EPIC-006 stories

- **US-018:** As PM, I want to track funnel events (view → click → join → generate → copy) so that đo activation rate.
- **US-019:** As a creator dùng screen reader, I want to accordion + modal có ARIA labels đầy đủ so that nav được bằng keyboard.

---

## User Personas

| Persona | Mô tả | Nhu cầu |
|---------|-------|---------|
| **Creator mới** (chưa link Scalef) | Đăng ký Gen-Green, tham gia Event, chưa biết affiliate là gì | Hiểu nhanh affiliate là gì + cách kiếm hoa hồng + onboarding mượt sang Scalef linking |
| **Creator active** (đã link, đã join chiến dịch) | Tạo nội dung thường xuyên, đã có affiliate link | Tạo link nhanh, copy 1-click, quản lý link cũ |
| **Creator power-user** | Tham gia nhiều chiến dịch, theo dõi hiệu quả | Dashboard hoa hồng minh bạch, filter theo campaign + thời gian |
| **Creator chờ duyệt** (PENDING/REJECTED) | Vừa join chiến dịch nhưng chưa được approve | Thông tin rõ ràng về retry + lý do reject |

---

## User Flows

### Flow 1: Happy path — Creator đã link Scalef tham gia chiến dịch

```
Creator vào Event detail
  → Section "Chiến dịch Affiliate Liên Kết" hiển thị 2 card
  → Click card → Trang chi tiết affiliate
  → Đọc mô tả + thể lệ (accordion)
  → Bấm "Tham gia chiến dịch"
  → BE gọi Scalef → trả APPROVED ngay
  → Toast "Đã tham gia"
  → Nút "Tạo link affiliate" hiện
  → Bấm → Modal mở (optional Custom URL + Tên link)
  → Submit → BE gọi Scalef → trả deeplink + short_link
  → Hiển thị 2 link với nút Copy
  → Creator copy short_link → paste vào video TikTok
```

### Flow 2: Chưa link Scalef

```
Creator vào Event detail
  → Banner "Liên kết Scalef để kiếm hoa hồng" hiện trên đầu section
  → Bấm CTA "Liên kết ngay" → flow Account Linking
  → (HOẶC) Click card → click "Tham gia" → Popup chặn
  → Bấm "Liên kết ngay" trong popup → flow Account Linking
  → Hoàn tất link → quay lại trang trước → Banner ẩn → Tham gia bình thường
```

### Flow 3: Contract PENDING/REJECTED

```
Creator bấm "Tham gia"
  → BE gọi Scalef → trả PENDING
  → Banner vàng "Yêu cầu đang được xử lý — Thử lại sau 23h59"
  → Sau 24h: nút "Thử lại" enable
  → Creator click → BE gọi lại Scalef → có thể APPROVED hoặc REJECTED
  → Nếu REJECTED → banner đỏ + countdown 14 ngày
```

### Flow 4: Xem báo cáo hoa hồng (V2)

```
Creator vào menu "Hoa hồng của tôi"
  → Default: 1 tháng gần nhất, "Tất cả chiến dịch"
  → 3 KPI cards: Chờ duyệt 500K / Tạm duyệt 1.2tr / Đã xác nhận 800K
  → Table đơn hàng top 50
  → Click chiến dịch trong sidebar → filter theo campaign đó
  → Đổi date range → 3 tháng → reload
```

---

## Dependencies

### Internal Dependencies

- **Account Linking track** — phải hoàn thành Phase 1 trước khi launch FE Creator (cần `scalef_user_id` trên user)
- **Admin Setup track** — phải có ít nhất vài affiliate campaigns active để test/launch
- **Gen-Green Event detail page** — FR-001 nhúng section vào page hiện có
- **Gen-Green auth + session framework**
- **Gen-Green design system** (button, card, modal, toast)
- **Gen-Green analytics framework** (Firebase / GTM) — cho FR-012

### External Dependencies

- **Scalef APIs** theo spec [scalef-api.md](scalef-api.md):
  - SSO OAuth (cho Account Linking, đã có spec mới ở section 0)
  - `POST /campaigns/join` (FR-004)
  - `POST /campaigns/generate-link` (FR-005)
  - `GET /campaigns`, `GET /campaigns/{id}` (FR-001, FR-003, FR-007)
  - `POST /report/click`, `POST /report/overview`, `GET /publisher/conversion` (FR-009)
- **Scalef sandbox/staging** environment để test E2E
- **Scalef credentials** cấp riêng cho Gen-Green tenant (production)

---

## Assumptions

1. **Ambassador frontend code đã production và stable** — verified với 150K creators, code clone được trực tiếp.
2. **Scalef APIs implemented đủ cho V1+V2** — login (đã có), campaigns (3.1-3.4), generate-link (3.5), reports (3.6-3.8).
3. **`partner_code` Gen-Green** sẽ được Scalef cấp (giống Ambassador có `PARTNER_1_POINT_5`).
4. **`sub2` convention** = `'GENGREEN'` để identify tenant trong Scalef tracking (giống `'AMBASSADOR'` của Ambassador).
5. **Account Linking Phase 1 launch trước** FE Creator launch.
6. **Creator base biết Scalef** — không cần explainer dài về affiliate là gì.
7. **Mobile chiếm ≥ 70%** creator base → mobile-first design.

---

## Out of Scope

**Nguyên tắc:** Gen-Green clone đúng những gì Ambassador đã làm. Chức năng Ambassador chưa làm thì Gen-Green cũng không đụng tới (tránh divergence).

| Feature | Trạng thái Ambassador | Gen-Green |
|---------|----------------------|-----------|
| Charts báo cáo theo ngày (clicks, conversion, sale, commission) | ❌ Cancelled (data sparse, UI friction) | ❌ Skip — clone simplification |
| Tabs trong commission page | ❌ Cancelled — gộp 1 view phẳng | ❌ Skip — clone simplification |
| Filter trạng thái đơn hàng | Chưa có | Chưa làm — giữ giống Ambassador |
| Filter `campaign_invoice_ids` | Chưa có | Chưa làm |
| Export CSV báo cáo | Chưa có | Chưa làm |
| UTM Builder trong link generation | 🚫 Blocked (chờ Pub2 confirm) | 🚫 Blocked — chờ Scalef team confirm support |
| Webhook realtime | Chưa implement | Chưa làm — V1 polling |
| Swagger API documentation | Chưa làm đầy đủ | Bỏ — Scalef bên kia tự làm |
| Withdraw hoa hồng affiliate | Out of scope V1+V2 | Phase 3 — gộp với cashflow Gen-Green |
| Affiliate dashboard real-time | Out of scope | Future |
| Recommend campaign theo content creator | Out of scope | Future |
| Affiliate cho story / live | Out of scope | Future |

---

## Open Questions

> **⚠️ Phải làm việc với Scalef dev team để clear trước khi kick-off implementation.** Các item này block code commit final của FR-004, FR-005, FR-009.

### Cần Scalef dev clear

1. **Contract status mapping (CRITICAL):**
   - Scalef trả int (`status: 1`, `publisher_status: 1`, `advertiser_status: 0`) — Ambassador (Pub2) trả string `PENDING/APPROVED/REJECTED`
   - **Cần biết:** giá trị int nào = APPROVED / PENDING / REJECTED?
   - **Cần biết:** `publisher_status` vs `advertiser_status` chênh nhau khi nào? Logic UI dùng status nào?
   - → Note: clone code Ambassador hiện tại theo string enum, sau khi clear với Scalef sẽ refactor mapping. Xem [Appendix D](#appendix-d-status-mapping-scalef-vs-pub2).

2. **Order status `hold`:**
   - Scalef `/report/overview.meta.conversion` có 6 status: `total / approved / pre_approved / pending / rejected / hold`
   - Ambassador chỉ map 4 (không có `hold`)
   - **Cần biết:** `hold` nghĩa là gì? Gộp vào `pending` hay tạo badge riêng (màu, label)?
   - → Note: clone Ambassador trước (4 status), sau khi Scalef clear sẽ thêm `hold` nếu cần.

3. **`partner_code` cho Gen-Green:**
   - Scalef cấp riêng hay giống Ambassador `PARTNER_1_POINT_5`?

4. **`sub2` tenant identifier:**
   - Convention `'GENGREEN'` (giống Ambassador `'AMBASSADOR'`) đã agree với data team chưa?

5. **TTL của affiliate link:**
   - Link Scalef có hết hạn không? Khi nào?

6. **Rate limit Scalef** cho Gen-Green tenant:
   - Limit/giây hoặc limit/ngày?
   - Cần biết để chống 429 + tune circuit breaker.

7. **Sandbox/staging Scalef:**
   - Có sẵn cho QA test E2E chưa?
   - Credentials staging cấp khi nào?

### Cần Scalef dev confirm support

8. **UTM support:**
   - Scalef API spec section 3.5 cho phép `utm_source`, `utm_medium`, `utm_campaign`, `sub_1`, `sub_2` — **đã hỗ trợ thật chưa hay chỉ là spec**?
   - Nếu support → Gen-Green có thể đi trước Ambassador (Ambassador đang block UTM theo NFR-009 V2). Hiện đang giữ Out of Scope chờ confirm.

---

## Approval & Sign-off

### Stakeholders

| Role | Name | Responsibility |
|------|------|----------------|
| Product Owner | TBD | Approve scope + priorities |
| Engineering Lead (BE) | TBD | Approve BE proxy + Scalef integration |
| Engineering Lead (FE) | TBD | Approve clone strategy + adapt design system |
| Design Lead | TBD | Adapt UI Ambassador → Gen-Green |
| QA Lead | TBD | E2E test với Scalef sandbox |

### Approval Status

- [ ] Product Owner
- [ ] Engineering Lead (BE)
- [ ] Engineering Lead (FE)
- [ ] Design Lead
- [ ] QA Lead

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-04 | vinhnguyen | Initial PRD. Format theo BMAD template. Clone từ Ambassador frontend (V1 + V2). Apply simplification của Ambassador V2 (no charts, no tabs in commission page). Map sang Scalef APIs thay Pub2. |
| 1.1 | 2026-05-04 | vinhnguyen | Cleanup theo audit Ambassador: bỏ Swagger (Scalef tự làm), bỏ webhook V1 (Ambassador chưa làm), giữ filter status đơn không có (Ambassador chưa làm). Gộp Open Questions thành 2 nhóm: cần Scalef dev clear (contract status int mapping, `hold` status) + cần Scalef dev confirm support (UTM). Note rõ status mapping sẽ làm việc với Scalef dev rồi refactor sau. |

---

## Next Steps

### Phase 3: Architecture

Run `/architecture` để thiết kế chi tiết:
- Backend Go: Scalef client module, public handlers, service layer, MongoDB collections
- Frontend: routing, lazy loading, design system adaptation, service layer endpoints
- Integration: error handling matrix, retry logic, circuit breaker

### Phase 4: Sprint Planning

Sau khi architecture xong:
- Break 6 epics thành stories chi tiết (tổng ~25-32 stories)
- Estimate effort từng story
- Plan sprint (~12.5d effort cho V1+V2)
- Kick-off implementation, ưu tiên EPIC-004 (BE Foundation) trước

---

**This document was created using BMAD Method v6 - Phase 2 (Planning)**

---

## Appendix A: Requirements Traceability Matrix

| Epic ID | Epic Name | Functional Requirements | Story Count (Est.) |
|---------|-----------|-------------------------|-------------------|
| EPIC-001 | Affiliate Discovery (Browse + Detail) | FR-001, FR-002, FR-003, FR-007 | 5-7 |
| EPIC-002 | Join + Generate Link Flow | FR-004, FR-005, FR-006 | 5-7 |
| EPIC-003 | Touchpoint Liên kết Scalef | FR-008 | 2-3 |
| EPIC-004 | Backend Foundation (Scalef Proxy) | FR-010, FR-011 | 6-8 |
| EPIC-005 | Commission Dashboard (V2) | FR-009 | 3-4 |
| EPIC-006 | Analytics & Polish | FR-012, NFR-008 | 2-3 |

**Total estimated stories:** 23-32

---

## Appendix B: Prioritization Details

### Functional Requirements

| Priority | Count | FRs |
|----------|-------|-----|
| Must Have | 9 | FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-010, FR-011 |
| Should Have | 2 | FR-009, FR-012 |
| Could Have | 0 | — |

### Non-Functional Requirements

| Priority | Count | NFRs |
|----------|-------|------|
| Must Have | 5 | NFR-001, NFR-003, NFR-004, NFR-005, NFR-006, NFR-007 |
| Should Have | 2 | NFR-002, NFR-008 |

### MVP Scope (V1 — Must Have only)

V1 launch khi đủ:
- Browse + detail chiến dịch (EPIC-001)
- Join + generate link + my links (EPIC-002)
- Touchpoint linking (EPIC-003)
- BE foundation (EPIC-004)

**V1 effort:** ~7.5 ngày (1 BE + 1 FE)

### V2 Scope (Should Have)

V2 launch sau V1 ~2 tuần:
- Commission dashboard (EPIC-005)
- Analytics + a11y (EPIC-006)

**V2 effort:** ~5 ngày

**Tổng V1+V2:** ~12.5 ngày (~2.5 tuần) — thấp hơn ~50% so với build từ đầu (~24 ngày Ambassador) nhờ clone.

---

## Appendix C: Clone Mapping Table

### Frontend pages

| Gen-Green page | File clone từ Ambassador | Lines | Adapt |
|----------------|--------------------------|-------|-------|
| Section trong Event | `home/components/affiliate-campaigns-section/` | ~150 | Replace API endpoint, design system |
| Affiliate card | `home/components/affiliate-item-card/` | ~100 | Design system |
| Campaign detail | `affiliate-campaign-detail/index.tsx` | 672 | API endpoints, status mapping |
| My links | `affiliate-links/index.tsx` | 269 | API endpoint, design |
| Commission dashboard | `affiliate-commission/index.tsx` | 403 | Map field Scalef vs Pub2 |
| Browse all campaigns | `affiliate-campaigns/index.tsx` | 242 | API endpoint, filter |

### Service layer

| Gen-Green service | File clone | Methods |
|-------------------|-----------|---------|
| `services/affiliate.ts` | `ambassabor/frontend/src/services/affiliate.ts` (72 dòng) | 11 methods (FR-010) |

### Backend modules

| Gen-Green BE | Pattern clone từ Ambassador |
|--------------|---------------------------|
| `internal/module/scalef/` | `internal/module/pub2/` (client.go, hmac.go, models.go, errors.go) |
| `internal/service/affiliate.go` | Same pattern |
| `pkg/public/handler/affiliate.go` | Same pattern |
| MongoDB collections | Same naming (affiliate_contracts, affiliate_links, scalef_api_logs) |

---

## Appendix D: Status Mapping Scalef vs Pub2

> **⚠️ TBD — phải làm việc với Scalef dev team để clear, sau đó refactor code.**
>
> Strategy: **Clone code Ambassador trước** (theo string enum Pub2). Sau khi Scalef dev clear mapping → tạo translation layer ở BE proxy (Scalef int → Pub2-style string) để FE clone giữ nguyên không phải sửa.

### Contract status (CRITICAL — block FR-004)

| Ambassador (Pub2) | Gen-Green (Scalef) | UI hiển thị |
|-------------------|---------------------|-------------|
| `PENDING` | `?` (publisher_status = ?) | Banner vàng + countdown 24h |
| `APPROVED` | `?` (publisher_status = ?) | Hiện nút "Tạo link" |
| `REJECTED` | `?` (publisher_status = ?) | Banner đỏ + countdown 14 ngày |

**Câu hỏi cho Scalef dev:**
1. `status` (top-level) vs `publisher_status` vs `advertiser_status` — UI nên dùng cái nào?
2. Giá trị int nào = APPROVED / PENDING / REJECTED?
3. Có giá trị nào ngoài 3 trạng thái trên không (VD: HOLD, EXPIRED)?
4. Khi `publisher_status=1` mà `advertiser_status=0` → contract đã active hay vẫn chờ?

### Order status (block FR-009)

Scalef `/report/overview.meta.conversion` trả 6 status, Ambassador chỉ map 4:

| Status Scalef | Ambassador có map? | Color hiện tại Ambassador | Action cho Gen-Green |
|---------------|--------------------|----------------------------|----------------------|
| `pending` | ✅ | #DC6803 (Chờ duyệt) | Clone trực tiếp |
| `pre_approved` | ✅ | #1570EF (Đã duyệt) | Clone trực tiếp |
| `approved` | ✅ | #079455 (Đã nhận) | Clone trực tiếp |
| `rejected` | ✅ | #B42318 (Từ chối) | Clone trực tiếp |
| `hold` | ❌ Chưa map | — | **TBD — hỏi Scalef** |
| `total` | N/A (aggregate) | — | Skip (không phải state đơn) |

**Câu hỏi cho Scalef dev:**
1. `hold` nghĩa là gì trong context creator? (Tạm giữ chờ verify? Bị flag fraud? Khác?)
2. UI Gen-Green nên gộp `hold` vào `pending` hay hiển thị riêng?
3. Nếu hiển thị riêng → suggest label tiếng Việt + màu badge.

### Khi Scalef clear → action items

- [ ] Update bảng trên với giá trị mapping cụ thể
- [ ] BE: tạo translation function `scalefStatusToString(int) → string` ở `internal/module/scalef/`
- [ ] FE: nếu có `hold` → thêm badge mới trong commission page
- [ ] Cập nhật PRD revision history v1.2 với changes
