# Product Requirements Document: Affiliate FE Creator — Gen-Green (Trimmed Scope)

**Date:** 2026-05-12
**Author:** vinhnguyen
**Version:** 2.0 (Trimmed)
**Project Type:** Feature Integration (clone từ Ambassador)
**Project Level:** Level 3
**Status:** Draft
**Platform:** Gen-Green (`accesstrade-projects/vcreator/`)
**Source:** Trimmed từ [prd-fe-creator-2026-05-04.md](prd-fe-creator-2026-05-04.md) v1.1

---

## Changes vs v1.1 (Trimmed scope)

**Bỏ 2 tính năng so với PRD gốc:**

| FR bỏ | Tên | Lý do |
|-------|-----|-------|
| ~~FR-007~~ | Trang "Browse chiến dịch affiliate" (`/affiliate-campaigns`) | Out of scope — bỏ danh sách affiliate campaign standalone |
| ~~FR-006~~ | Trang "Link affiliate của tôi" (`/affiliate-links`) | Out of scope — bỏ quản lý link |

**Tác động:**
- EPIC-001 (Affiliate Discovery): chỉ còn FR-001, FR-002, FR-003 (bỏ FR-007)
- EPIC-002 (Join + Generate Link): chỉ còn FR-004, FR-005 (bỏ FR-006)
- US-003, US-009 bỏ
- Creator KHÔNG có trang riêng để xem lại link đã tạo → link chỉ hiển thị tại trang chi tiết campaign sau khi generate
- Creator KHÔNG có entry point browse affiliate độc lập → chỉ vào affiliate qua Event detail (FR-001)
- BE: bỏ endpoint `GET /affiliate-links` và `GET /affiliate-campaigns` (list all). Collection `affiliate_links` vẫn cần (để lưu log + chống tạo trùng + commission tracking) nhưng không expose qua API list
- Service layer FE: bỏ `getMyLinks()` và `getAllCampaigns()`

**Effort giảm:** V1 từ ~7.5d xuống còn ~6d (-1.5d cho 2 page + endpoint)

---

## Document Overview

PRD này định nghĩa requirements cho **FE Creator** — phần creator Gen-Green sử dụng affiliate: xem chiến dịch trong Event hiện có, tham gia (join), tạo link affiliate, xem hoa hồng. Toàn bộ chức năng + UX **clone từ Ambassador frontend** (đã production, verified với 150K creators tương tự), chỉ adapt Scalef API + Gen-Green design system.

**Related Documents:**
- Original PRD (full scope): [prd-fe-creator-2026-05-04.md](prd-fe-creator-2026-05-04.md)
- Overview: [fe-display-generate-link-report-overview.md](fe-display-generate-link-report-overview.md)
- Source clone: [`accesstrade-projects/ambassabor/frontend/src/pages/affiliate-*`](../../../ambassabor/frontend/src/pages/)
- Reference Ambassador V1: [`pub2-affiliate-integration/prd-affiliate-v1-2026-03-31.md`](../../pub2-affiliate-integration/prd-affiliate-v1-2026-03-31.md) — FR-004, FR-005, FR-013, FR-016, FR-017, FR-018
- Reference Ambassador V2: [`pub2-affiliate-integration/prd-affiliate-v2-2026-03-31.md`](../../pub2-affiliate-integration/prd-affiliate-v2-2026-03-31.md) — FR-011, FR-012, FR-023
- Phụ thuộc: [Account Linking](account-linking-overview.md), [Admin Setup](admin-setup-overview.md)
- Scalef API: [scalef-api.md](scalef-api.md)

---

## Executive Summary

Sau khi Admin Setup chuẩn bị catalog affiliate + Account Linking gắn `scalef_user_id` vào user Gen-Green, track này xây dựng UI cho **creator dùng affiliate**:

- Xem chiến dịch affiliate ngay trong Event hiện có (entry point duy nhất)
- Tham gia chiến dịch (join contract với Scalef)
- Tạo affiliate link cá nhân để gắn vào nội dung
- Theo dõi hoa hồng (V2)

**Strategy:** **Clone trực tiếp từ Ambassador frontend** thay vì build từ đầu:
- 2 page chính: `affiliate-campaign-detail`, `affiliate-commission` (V2)
- Section affiliate trong Event detail (clone từ Ambassador home section)
- Service layer + interfaces có sẵn (`services/affiliate.ts`) — bỏ bớt 2 methods không dùng

→ Effort thực tế ~11 ngày (V1 + V2), thấp hơn ~50% so với build từ đầu.

**Điểm khác biệt với Ambassador:**
- Backend proxy gọi **Scalef API**, không phải Pub2
- Touchpoint linking dẫn sang **Scalef SSO OAuth** (Phase 1), không phải SSO AccessTrade
- Design system Gen-Green
- **Bỏ trang browse standalone + bỏ trang my links** (khác Ambassador)

---

## Product Goals

### Business Objectives

1. **Mở khoá doanh thu affiliate cho creator** — sau khi Admin Setup + Linking ready, creator có UI để dùng.
2. **Đạt activation rate 40%** active users tạo affiliate link trong 3 tháng đầu.
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

> **Note:** Đây là entry point DUY NHẤT để creator vào affiliate. Trang browse standalone (`/affiliate-campaigns`) đã bỏ.

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

**Ambassador Reference:**
- File clone: `ambassabor/frontend/src/pages/affiliate-campaign-detail/index.tsx` (672 dòng)
- Hàm `parseDescSections()` parse markdown → accordion items
- Service: `affiliateService.getCampaignDetail(campaignId)`, `getContract(campaignId)`
- Ambassador FR-018 (V1) ✅ Implemented

**Dependencies:** FR-001, Account Linking

> **Note:** Vì bỏ trang "My Links", state HAS_LINK chỉ hiển thị link **mới nhất** của user cho campaign này. Không có chỗ khác để xem link cũ.

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
- [ ] Field **Tên link** (optional): để creator note/đặt tên link
- [ ] Validate Custom URL format (nếu nhập)

**Output:**
- [ ] BE gọi Scalef → trả `deeplink` (full) + `short_link` (rút gọn)
- [ ] Hiển thị 2 link với nút Copy riêng từng link
- [ ] Toast "Đã copy link" khi click copy
- [ ] Lưu link vào MongoDB Gen-Green (`affiliate_links` collection) — kèm `name` nếu user nhập
- [ ] Nút "Tạo link mới" cho phép tạo lại
- [ ] Link mới nhất hiển thị tại trang chi tiết campaign (state HAS_LINK)

**Error:**
- [ ] Map Scalef error
- [ ] Nếu Custom URL invalid → inline error trong modal

**Ambassador Reference:**
- Service: `affiliateService.generateLink(campaignId, {originalUrl?, name?})` — `services/affiliate.ts:29`
- File: `affiliate-campaign-detail/index.tsx:216 handleGenerateLink()`
- Ambassador FR-005 (V1) + FR-020 (V2 — Enhanced với custom URL/name) ✅ Implemented

**Dependencies:** FR-004, Scalef API `POST /campaigns/generate-link`

> **Note:** Collection `affiliate_links` vẫn cần lưu (commission tracking + chống tạo trùng + lịch sử nội bộ) nhưng KHÔNG expose qua trang my-links.

---

### ~~FR-006: Trang "Link affiliate của tôi"~~ — REMOVED

> ❌ **Bỏ khỏi scope** (2026-05-12). Creator không có trang riêng xem lại link đã tạo. Link mới nhất chỉ hiển thị tại trang chi tiết campaign (FR-003 state HAS_LINK).

---

### ~~FR-007: Trang "Browse chiến dịch affiliate"~~ — REMOVED

> ❌ **Bỏ khỏi scope** (2026-05-12). Không có entry point standalone (`/affiliate-campaigns`). Creator chỉ vào affiliate qua section trong Event detail (FR-001).

---

### FR-008: Touchpoint liên kết Scalef (Banner + Popup)

**Priority:** Must Have

**Description:**
Khi creator chưa link Scalef nhưng cố dùng affiliate, hệ thống chặn hoặc gợi ý liên kết.

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
Trang `/affiliate-commission` hiển thị hoa hồng + danh sách đơn hàng. **Layout simplified theo Ambassador V2:** chỉ KPI cards + orders list, **không** có chart, **không** có tabs.

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
- [ ] ~~Tabs Tổng quan / Click / Conversion / Sale~~
- [ ] ~~Charts theo ngày~~
- [ ] ~~Filter trạng thái đơn~~
- [ ] ~~Export CSV~~

**Ambassador Reference:**
- File clone: `ambassabor/frontend/src/pages/affiliate-commission/index.tsx` (403 dòng)
- Service: `affiliateService.reportCommission()`, `reportOrders()` — `services/affiliate.ts:47-54`
- Ambassador FR-011 + FR-012 + FR-023 (V2) ✅ Implemented

**Dependencies:** FR-004, Scalef Report APIs

---

### FR-010: Service layer + Interfaces (Frontend)

**Priority:** Must Have

**Description:**
Service module gọi BE proxy + TypeScript interfaces cho data structure.

**Acceptance Criteria:**
- [ ] File `services/affiliate.ts` clone từ Ambassador, replace endpoints theo Gen-Green BE
- [ ] Interfaces TypeScript cho: `AffiliateCampaign`, `AffiliateContract`, `AffiliateLink`, `CommissionReport`, `Order`
- [ ] 8 service methods (bỏ 2 vs Ambassador 11 methods):
  - `getCampaignsByEvent(eventId)` — FR-001
  - `getCampaignDetail(campaignId)` — FR-003
  - `joinCampaign(campaignId)` — FR-004
  - `getContract(campaignId)` — FR-004 (status check)
  - `generateLink(campaignId, {originalUrl?, name?})` — FR-005
  - `getMyCampaigns()` — FR-009 (sidebar)
  - `reportCommission(data)` — FR-009
  - `reportOrders(data)` — FR-009
  - ~~`getMyLinks(params?)`~~ — bỏ (FR-006 removed)
  - ~~`getAllCampaigns(params?)`~~ — bỏ (FR-007 removed)
  - ~~`reportClicks/Conversions/SaleAmount`~~ — bỏ stub luôn
- [ ] ApiConst config riêng cho Gen-Green
- [ ] Error handling chung qua `request.call()` utility

**Ambassador Reference:** `ambassabor/frontend/src/services/affiliate.ts` (72 dòng)

**Dependencies:** Backend proxy endpoints

---

### FR-011: BE Proxy Scalef APIs (Backend Foundation)

**Priority:** Must Have

**Description:**
Gen-Green backend proxy gọi Scalef APIs. Backbone cho tất cả FR khác.

**Acceptance Criteria:**

**Scalef Client module:**
- [ ] Tạo `internal/module/scalef/client.go` (clone pattern Ambassador `internal/module/pub2/`)
- [ ] HMAC-SHA256 signature theo spec Scalef
- [ ] Headers: `X-Port-Type: PUB`, `X-Client-Id`, `X-Ref-User-Id`, `X-Timestamp`, `X-Signature`
- [ ] Timeout 10s default
- [ ] Logging request/response vào collection `scalef_api_logs`

**Public endpoints (cho creator):**
- [ ] `GET /events/:id/affiliate-campaigns` (FR-001)
- [ ] `GET /affiliate-campaigns/:id` (FR-003)
- [ ] `POST /affiliate-campaigns/:id/join` + `GET /:id/contract` (FR-004)
- [ ] `POST /affiliate-campaigns/:id/generate-link` (FR-005)
- [ ] `GET /affiliate-campaigns/me` (FR-009 sidebar — joined campaigns)
- [ ] `POST /affiliate-reports/commission` (FR-009)
- [ ] `POST /affiliate-reports/orders` (FR-009)
- [ ] ~~`GET /affiliate-links`~~ — bỏ (FR-006 removed)
- [ ] ~~`GET /affiliate-campaigns` (list all)~~ — bỏ (FR-007 removed)
- [ ] ~~Stub `POST /affiliate-reports/{clicks,conversions,sale-amount}`~~ — bỏ

**Tenant isolation:**
- [ ] Mọi public endpoint yêu cầu auth + `user.scalef_user_id != null` (trả 403 với code `SCALEF_NOT_LINKED`)
- [ ] Inject `X-Ref-User-Id = user.scalef_user_id` từ session

**Local cache + storage:**
- [ ] Collection: `affiliate_contracts` (user_id, affiliate_campaign_id, contract_no, status, retry_at)
- [ ] Collection: `affiliate_links` (user_id, affiliate_campaign_id, name, short_link, deeplink, original_url, created_at) — **vẫn lưu cho commission tracking, không expose qua API list**
- [ ] Collection: `scalef_api_logs` (TTL 90 ngày)

**Ambassador Reference:** `ambassabor/backend/internal/module/pub2/`, `pkg/public/handler/affiliate.go`

**Dependencies:** Scalef API spec, Account Linking

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
- [ ] Reuse analytics infrastructure hiện có (Firebase / GTM)

**Dependencies:** Gen-Green analytics framework

---

## Non-Functional Requirements

Giữ nguyên từ PRD v1.1 (NFR-001 → NFR-008). Xem [prd-fe-creator-2026-05-04.md](prd-fe-creator-2026-05-04.md#non-functional-requirements).

---

## Epics (Updated)

| Epic | Tên | FRs còn lại | Story Count | Priority |
|------|-----|-------------|-------------|----------|
| EPIC-001 | Affiliate Discovery | FR-001, FR-002, FR-003 (~~FR-007~~) | 3-5 | Must Have |
| EPIC-002 | Join + Generate Link Flow | FR-004, FR-005 (~~FR-006~~) | 3-5 | Must Have |
| EPIC-003 | Touchpoint Liên kết Scalef | FR-008 | 2-3 | Must Have |
| EPIC-004 | Backend Foundation | FR-010, FR-011 | 5-7 | Must Have |
| EPIC-005 | Commission Dashboard (V2) | FR-009 | 3-4 | Should Have |
| EPIC-006 | Analytics & Polish | FR-012, NFR-008 | 2-3 | Should Have |

**Total estimated stories:** 18-27 (giảm từ 23-32)

---

## User Stories (Updated)

### EPIC-001 stories
- **US-001:** As a creator, I want to xem các chiến dịch affiliate trong Event đang quan tâm so that biết Event này có cơ hội kiếm hoa hồng không.
- **US-002:** As a creator, I want to xem chi tiết chiến dịch affiliate so that quyết định có tham gia hay không.
- ~~**US-003:** Browse tất cả chiến dịch affiliate~~ — bỏ

### EPIC-002 stories
- **US-004:** As a creator (đã link Scalef), I want to tham gia chiến dịch affiliate so that bắt đầu kiếm hoa hồng.
- **US-005:** As a creator có contract PENDING, I want to thấy countdown 24h và nút "Thử lại".
- **US-006:** As a creator có contract REJECTED, I want to thấy lý do + countdown 14 ngày.
- **US-007:** As a creator (APPROVED), I want to tạo link affiliate với URL tuỳ chỉnh + tên gợi nhớ.
- **US-008:** As a creator, I want to copy link rút gọn / link đầy đủ với 1 click.
- ~~**US-009:** Xem danh sách link đã tạo~~ — bỏ

### EPIC-003, 004, 005, 006 stories
Giữ nguyên từ PRD v1.1.

---

## User Flows (Updated)

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

⚠️ Lưu ý: Sau khi đóng tab/quay lại sau, creator chỉ thấy link mới nhất ở trang detail.
   Không có trang "My Links" để xem lại lịch sử link đã tạo.
```

### Flow 2, 3, 4
Giữ nguyên từ PRD v1.1.

---

## Out of Scope (Updated)

| Feature | Trạng thái | Lý do |
|---------|-----------|-------|
| **Trang browse all affiliate campaigns** (FR-007 cũ) | ❌ Bỏ V2 trimmed | Creator chỉ vào affiliate qua Event |
| **Trang my affiliate links** (FR-006 cũ) | ❌ Bỏ V2 trimmed | Link hiển thị tại trang detail campaign |
| Charts báo cáo theo ngày | ❌ Skip | Clone simplification từ Ambassador V2 |
| Tabs trong commission page | ❌ Skip | Clone simplification |
| Filter trạng thái đơn hàng | Chưa làm | Giống Ambassador |
| Export CSV báo cáo | Chưa làm | Giống Ambassador |
| UTM Builder | 🚫 Blocked | Chờ Scalef confirm support |
| Webhook realtime | Chưa làm | V1 polling |
| Withdraw hoa hồng affiliate | Out of scope V1+V2 | Phase 3 |

---

## Effort Estimate (Updated)

### V1 Scope (Must Have only)
- EPIC-001 (Discovery, no browse): ~1.5d
- EPIC-002 (Join + Generate Link, no my-links): ~2d
- EPIC-003 (Touchpoint): ~1d
- EPIC-004 (BE Foundation, bỏ 2 endpoint): ~2d

**V1 effort:** ~6.5 ngày (giảm 1d so với v1.1 = 7.5d)

### V2 Scope (Should Have)
- EPIC-005 (Commission dashboard): ~3.5d
- EPIC-006 (Analytics + a11y): ~1.5d

**V2 effort:** ~5 ngày

**Tổng V1+V2:** ~11.5 ngày (~2.3 tuần)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.0 | 2026-05-12 | vinhnguyen | Trimmed scope: bỏ FR-006 (My Links), FR-007 (Browse all campaigns). US-003, US-009 bỏ. Service methods giảm 11 → 8. BE endpoints giảm tương ứng. Effort V1 giảm 7.5d → 6.5d. |
| 1.1 | 2026-05-04 | vinhnguyen | (Original) See [prd-fe-creator-2026-05-04.md](prd-fe-creator-2026-05-04.md) |
