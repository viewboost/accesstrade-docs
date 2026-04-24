# Product Requirements Document: Pub2 Affiliate Integration — V3.1 (Discovery & Simplified Commission Dashboard)

**Date:** 2026-04-24
**Author:** vinhnguyen
**Version:** 1.0
**Project Type:** Feature Enhancement
**Project Level:** Level 2
**Status:** Draft
**Platform:** Ambassador (`accesstrade-projects/ambassabor/`)

---

## Document Overview

PRD này định nghĩa Phase 3 của Pub2 Affiliate Integration — tập trung vào **Campaign Discovery, Links Management, System Reliability** và một **Commission Dashboard tối giản**.

**Related Documents:**
- [PRD Gốc (v1.3)](./prd-affiliate-integration-2026-03-25.md)
- [PRD V1 — Implemented](./prd-affiliate-v1-2026-03-31.md)
- [PRD V2 — Complete](./prd-affiliate-v2-2026-03-31.md)
- [Architecture](./architecture-affiliate-integration-2026-03-25.md)
- [API Reference](./api-reference.md)

---

## Executive Summary

V1 hoàn thành core flow (join + link). V2 hoàn thành enhanced link generation, commission dashboard baseline, report API endpoints. **V3.1 bổ sung khả năng khám phá campaigns, quản lý links, ổn định hệ thống, và tinh chỉnh commission dashboard về dạng tối giản.**

**Existing Assets (from V2):**
- Backend: 6 report API endpoints đã có (`/affiliate/reports/*`)
- Backend: Pub2 client methods cho tất cả APIs
- Frontend: Commission Dashboard baseline (summary cards + orders list) — sẽ được refactor ở V3.1

**Scope V3.1:**
1. **Trang browse affiliate campaigns** cho influencer (FR-019)
2. **Trang quản lý links riêng** (FR-006)
3. **Commission Dashboard tối giản** — KPI cards + orders list, không có chart, không có date filter UI (FR-023)
4. **Circuit breaker** cho Pub2 API client (NFR-004)
5. **Swagger documentation** (NFR-008)

**Không nằm trong scope V3.1:**
- Biểu đồ click/conversion/commission/sale-amount theo ngày — huỷ vì data Pub2 dev lệch, insight trên khung 1-3 tháng không đáng kể.
- Report caching (Redis) — không cần khi không còn chart polling nhiều endpoint.
- CSV/PDF export — không trong use-case end-user, defer sau cho admin.
- UTM support — blocked chờ Pub2 confirm.

---

## Product Goals

### Business Objectives

1. **Discovery:** Influencer dễ tìm campaigns mới → tăng participation rate.
2. **Link management:** Quản lý links tập trung → tăng reuse rate.
3. **Clarity:** Commission Dashboard tối giản, dễ đọc — KPI + list đơn, không phân tán attention qua tabs/charts.
4. **Reliability:** Circuit breaker → graceful degradation khi Pub2 down.

### Success Metrics

| Metric | Target | Timeframe |
|---|---|---|
| Influencer browse campaigns page | 50% active users visit | 2 tháng |
| Links page visited (manage links) | 40% active affiliates | 2 tháng |
| Commission dashboard weekly visits | 60% active affiliates | 2 tháng |
| Pub2 API failure graceful handling | 100% (no crash) | Ongoing |

---

## Functional Requirements

---

### FR-019: Influencer browse danh sách Affiliate Campaigns

**Priority:** Must Have

**Description:**
Influencer vào trang riêng để xem danh sách tất cả affiliate campaigns đang active.

**Acceptance Criteria:**
- [ ] Trang riêng hiển thị danh sách affiliate campaigns có status = active
- [ ] Sắp xếp theo ngày tạo mới nhất trước
- [ ] Mỗi item: banner, title, commission info, bonus info (reuse Affiliate Item Card từ V1)
- [ ] Click vào item → navigate đến trang chi tiết affiliate campaign
- [ ] Phân trang (infinite scroll hoặc pagination)
- [ ] Responsive trên mobile (1 cột) và desktop (2 cột grid)
- [ ] Empty state khi không có campaigns

**Cần làm:**
- Backend: Public API endpoint `GET /affiliate/campaigns` (list active, pagination)
- Frontend page mới: `pages/affiliate-campaigns/index.tsx`
- Route + navigation link

**Dependencies:** None

---

### FR-006: Influencer xem danh sách Links đã tạo

**Priority:** Must Have

**Description:**
Trang riêng quản lý tất cả affiliate links đã tạo, grouped theo campaign. Backend API `GET /affiliate/my-links` đã có.

**Acceptance Criteria:**
- [ ] Trang riêng hiển thị danh sách links grouped theo campaign
- [ ] Mỗi link: name, short link, full link, ngày tạo, nút copy
- [ ] Search by name
- [ ] Phân trang
- [ ] Responsive trên mobile

**Cần làm:**
- Frontend page mới: `pages/affiliate-links/index.tsx`
- Route + navigation link
- Backend API đã có

**Dependencies:** None

---

### FR-023: Commission Dashboard tối giản

**Priority:** Must Have

**Description:**
Refactor trang `/hoa-hong-affiliate` về dạng 1 view phẳng: sidebar chọn campaign, header title, 3 KPI cards commission theo trạng thái, và danh sách đơn hàng. Không có tabs, không có chart, không có date filter UI.

**Acceptance Criteria:**

- [ ] **Layout:**
  - Sidebar trái: danh sách campaigns user đã join (item "Tất cả" ở đầu, không icon).
  - Main content: breadcrumb, header (title + subtitle), 3 KPI cards, danh sách đơn hàng.
- [ ] **3 KPI cards** (gradient border, icon, giá trị tiền):
  - "Hoa hồng chờ duyệt" = `WAITING_FOR_APPROVED + TEMPORARY_APPROVED` (từ `reportCommission.statisticDetails`)
  - "Hoa hồng đã duyệt" = `APPROVED`
  - "Hoa hồng đã nhận" = `total - waiting - approved - rejected`
- [ ] **Danh sách đơn** (list dọc, tối đa 50 đơn):
  - Icon theo trạng thái, campaign name, sale time (hh:mm, dd/mm/yyyy).
  - Số tiền `+commission`, badge trạng thái (Chờ duyệt / Đã duyệt / Đã nhận / Từ chối) với màu tương ứng.
- [ ] **Data fetching:** load song song 2 API `reportCommission` + `reportOrders` khi mount và khi đổi campaign filter.
- [ ] **Date range:** cố định 90 ngày tính tới hiện tại, không lộ ra UI.
- [ ] **Campaign filter:** click "Tất cả" → `campaign_ids=[]`; click 1 campaign → `campaign_ids=[campaignId]`.
- [ ] **Empty states:** "Chưa tham gia chiến dịch nào" (sidebar), "Chưa có đơn hàng nào trong khoảng thời gian này" (list).
- [ ] **Responsive:** mobile → sidebar scroll ngang; KPI stack dọc.

**Cần làm:**
- Frontend: refactor `pages/affiliate-commission/index.tsx` và `index.scss` — gỡ tabs, `ReportChart`, date range buttons, imports recharts.
- Backend: không đổi (tái sử dụng `reportCommission` + `reportOrders` hiện có).

**Out of scope (explicit):**
- Chart các metrics click / conversion / sale amount / commission theo ngày.
- Date filter buttons 7/30/90 ngày trên UI.
- Tab navigation các report loại khác nhau.
- Nút "Chia sẻ nhận hoa hồng".

**Dependencies:** V2 endpoints `/affiliate/reports/commission`, `/affiliate/reports/orders`.

---

## Non-Functional Requirements

---

### NFR-004: Circuit Breaker cho Pub2 Client

**Priority:** Must Have

**Description:**
Xử lý graceful khi Pub2 API down hoặc trả lỗi liên tục.

**Acceptance Criteria:**
- [ ] Circuit breaker pattern: CLOSED → OPEN → HALF_OPEN.
- [ ] Threshold: 5 failures liên tiếp → OPEN (short-circuit 30s).
- [ ] Half-open: cho 1 request qua để test → nếu success → CLOSED.
- [ ] Per-endpoint scope: report APIs fail không block join/link APIs (chia thành 2 breakers: `reportCB` và `mutationCB`).
- [ ] Logging: log state changes.
- [ ] Frontend: hiện thông báo "Hệ thống đang bận, vui lòng thử lại" khi circuit open.

**Implementation Notes:**
- Go: tự implement lightweight breaker tại `internal/module/pub2/circuit-breaker.go` (tránh thêm dependency).
- Scope tại `pub2.Client` level — mọi call đều đi qua `cb.allow()` trước khi hit HTTP.

---

### NFR-008: Swagger API Documentation

**Priority:** Should Have

**Description:**
Bổ sung Swagger documentation cho tất cả affiliate API endpoints.

**Acceptance Criteria:**
- [ ] Public affiliate APIs documented.
- [ ] Admin affiliate APIs documented.
- [ ] Request/response examples.
- [ ] Error response format documented.

---

### NFR-009: UTM Support (Pending Pub2)

**Priority:** Should Have — Blocked

**Description:**
Pub2 API nhận UTM fields nhưng hiện "Tạm thời không quan tâm". Khi Pub2 confirm hỗ trợ → bật UTM builder trong link generation form.

**Acceptance Criteria:**
- [ ] UTM builder accordion trong link generation form (4 fields: source, medium, campaign, content).
- [ ] Backend pass UTM to Pub2 `GenerateLinkRequest`.
- [ ] Lưu UTM params vào `AffiliateLinkRaw`.

**Status:** Blocked — chờ Pub2 confirm. Model Go đã có fields (`UTMSource`, `UTMMedium`, etc.)

---

## Epics

---

### EPIC-006: Campaign Discovery & Links Management

**Functional Requirements:** FR-019, FR-006

**Priority:** Must Have

**Estimated Stories:** 3-4

---

### EPIC-007: Commission Dashboard Simplification

**Functional Requirements:** FR-023

**Priority:** Must Have

**Estimated Stories:** 1-2

---

### EPIC-008: System Reliability & Documentation

**Non-Functional Requirements:** NFR-004, NFR-008, NFR-009

**Priority:** Must Have (NFR-004), Should Have (NFR-008, NFR-009)

**Estimated Stories:** 2-3

---

## Recommended Implementation Order

```
Phase 3A (Must Have):
  1. FR-019: Campaign listing page (~1-2 ngày)
  2. FR-006: Links management page (~1-2 ngày)
  3. NFR-004: Circuit breaker (~1 ngày)
  4. FR-023: Commission Dashboard simplification (~0.5 ngày)

Phase 3B (Should Have):
  5. NFR-008: Swagger docs (~1 ngày)
  6. NFR-009: UTM support (khi Pub2 confirm)
```

**Total estimate:** ~5-6 ngày

---

## Out of Scope (V3.1)

Các items dưới đây từng được cân nhắc nhưng quyết định **không** đưa vào scope:

1. **Report charts** (click / conversion / sale-amount / commission theo ngày) — data Pub2 ngắn hạn không đủ dày để cho insight, UI tab-based tạo friction; influencer tra cứu tổng + list đơn là đủ.
2. **Report caching (Redis)** — không còn polling nhiều endpoint thì cache không đáng setup.
3. **CSV/PDF export** — không phải use-case end-user, defer cho admin dashboard sau này.
4. **Webhook real-time** (Pub2 API 7 chưa có).
5. **Email digest** báo cáo hàng tuần.
6. **Admin report dashboard** (admin xem tổng hợp tất cả influencers).
7. **AI campaign recommendations**.
8. **Comparison charts** (so sánh giữa campaigns).

---

## Dependencies

### Internal (from V1 + V2 — all done)

| Dependency | Status |
|---|---|
| V1: Core affiliate flow (join, link, campaigns) | Done |
| V2: Enhanced link generation | Done |
| V2: 6 report API endpoints | Done |
| V2: Commission Dashboard baseline | Done (sẽ refactor ở FR-023) |
| V2: Pub2 client (all methods) | Done |

### External

| Dependency | Status |
|---|---|
| Pub2 UTM support | Blocked — "Tạm thời không quan tâm" |

---

## Open Questions

| # | Question | Owner | Status |
|---|---|---|---|
| 1 | Campaign listing: cần search/filter không, hay chỉ list + pagination? | Product | Open |
| 2 | Circuit breaker: threshold 5 failures, recovery 30s — ok? | Engineering | Open |
| 3 | UTM: khi nào Pub2 hỗ trợ? | Pub2 team | Blocked |
| 4 | Commission Dashboard có cần "trending" badge hoặc "Top campaign" metric không? | Product | Open |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-04-24 | vinhnguyen | Initial V3.1 PRD. Discovery + Links + simplified Commission Dashboard + Reliability. Charts/caching/export explicitly out of scope. |

---

**This document was created using BMAD Method v6 - Phase 2 (Planning)**
