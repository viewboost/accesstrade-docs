# Product Requirements Document: Pub2 Affiliate Integration — V3 (Discovery, Charts & Polish)

**Date:** 2026-04-09
**Author:** vinhnguyen
**Version:** 1.0
**Project Type:** Feature Enhancement
**Project Level:** Level 2
**Status:** Draft
**Platform:** Ambassador (`accesstrade-projects/ambassabor/`)

---

## Document Overview

PRD này định nghĩa Phase 3 của Pub2 Affiliate Integration — tập trung vào **Campaign Discovery, Report Charts, Links Management, và System Reliability**. Đây là các items deferred từ V2.

**Related Documents:**
- [PRD Gốc (v1.3)](./prd-affiliate-integration-2026-03-25.md)
- [PRD V1 — Implemented](./prd-affiliate-v1-2026-03-31.md)
- [PRD V2 — Complete](./prd-affiliate-v2-2026-03-31.md)
- [Architecture](./architecture-affiliate-integration-2026-03-25.md)
- [API Reference](./api-reference.md)

---

## Executive Summary

V1 hoàn thành core flow (join + link). V2 hoàn thành enhanced link generation, commission dashboard, report endpoints. **V3 bổ sung khả năng khám phá campaigns, biểu đồ chi tiết, quản lý links, và ổn định hệ thống.**

**Existing Assets (from V2):**
- Backend: 6 report API endpoints đã có (`/affiliate/reports/*`) ✅
- Backend: Pub2 client methods cho tất cả APIs ✅
- Frontend: Commission Dashboard với summary cards + orders list ✅
- Frontend: Enhanced link generation (custom URL, naming, history) ✅

**Scope V3:**
1. **Trang browse affiliate campaigns** cho influencer (FR-019)
2. **Trang quản lý links riêng** (FR-006)
3. **Report charts** — biểu đồ click/conversion/commission theo ngày (FR-007, FR-008, FR-010)
4. **Sale Amount report** (FR-009)
5. **Circuit breaker** cho Pub2 API (NFR-004)
6. **Swagger documentation** (NFR-008)
7. **Report caching** — cache response Pub2 giảm load
8. **Export reports** CSV/PDF

---

## Product Goals

### Business Objectives

1. **Discovery:** Influencer dễ tìm campaigns mới → tăng participation rate
2. **Data visualization:** Biểu đồ trực quan → influencer hiểu performance → optimize content
3. **Link management:** Quản lý links tập trung → tăng reuse rate
4. **Reliability:** Circuit breaker → graceful degradation khi Pub2 down

### Success Metrics

| Metric | Target | Timeframe |
|--------|--------|-----------|
| Influencer browse campaigns page | 50% active users visit | 2 tháng |
| Report charts viewed | 30% active affiliates | 2 tháng |
| Links page visited (manage links) | 40% active affiliates | 2 tháng |
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
- Backend API đã có ✅

**Dependencies:** None (API đã có)

---

### FR-007: Báo cáo Click (Chart)

**Priority:** Should Have

**Description:**
Biểu đồ số lượt click theo ngày. Backend endpoint đã có (`POST /affiliate/reports/clicks`).

**Acceptance Criteria:**
- [ ] Biểu đồ line/bar chart click theo ngày (epoch time → date)
- [ ] Tổng click hiển thị
- [ ] Lọc theo khoảng thời gian (max 3 tháng)
- [ ] Lọc theo campaign (optional)
- [ ] Loading + error states

**Cần làm:**
- Frontend: Chart component + page/tab
- Chart library: chọn 1 (recharts recommended — compatible React 16)

**Dependencies:** FR-016B ✅

---

### FR-008: Báo cáo Conversion (Chart)

**Priority:** Should Have

**Description:**
Biểu đồ conversion theo ngày. Backend endpoint đã có.

**Acceptance Criteria:**
- [ ] Biểu đồ conversion theo ngày
- [ ] Tổng conversions hiển thị
- [ ] Lọc theo thời gian + campaign

**Dependencies:** FR-016B ✅

---

### FR-009: Báo cáo Sale Amount (Chart)

**Priority:** Should Have

**Description:**
Biểu đồ giá trị đơn hàng theo ngày, phân theo trạng thái. Backend endpoint đã có.

**Acceptance Criteria:**
- [ ] Biểu đồ sale amount theo ngày
- [ ] Phân theo trạng thái: REJECTED, WAITING_FOR_APPROVED, APPROVED, TEMPORARY_APPROVED
- [ ] Tổng sale amount hiển thị

**Dependencies:** FR-016B ✅

---

### FR-010: Báo cáo Commission (Chart)

**Priority:** Should Have

**Description:**
Biểu đồ hoa hồng theo ngày, phân theo trạng thái. Backend endpoint đã có.

**Acceptance Criteria:**
- [ ] Biểu đồ commission theo ngày
- [ ] Phân theo trạng thái
- [ ] Tổng commission hiển thị
- [ ] Có thể tích hợp vào Commission Dashboard hoặc tab riêng

**Dependencies:** FR-016B ✅

---

### FR-021: Report Caching

**Priority:** Should Have

**Description:**
Cache response từ Pub2 report APIs để giảm load và tăng tốc.

**Acceptance Criteria:**
- [ ] Cache layer (Redis) cho report API responses
- [ ] TTL: 5 phút cho click/conversion, 15 phút cho commission/sale-amount
- [ ] Cache key: `affiliate:report:{type}:{sso_user_id}:{from}:{to}:{campaign_ids_hash}`
- [ ] Cache invalidation: manual flush endpoint (admin)
- [ ] Bypass cache: query param `?nocache=1` (dev only)

**Dependencies:** Redis (đã có trong stack)

---

### FR-022: Export Reports (CSV)

**Priority:** Should Have

**Description:**
Influencer export báo cáo và danh sách đơn hàng ra CSV.

**Acceptance Criteria:**
- [ ] Nút "Xuất CSV" trên Commission Dashboard
- [ ] Export orders list: campaign, commission, sale amount, status, date
- [ ] Stream response (không load toàn bộ vào memory)
- [ ] Giới hạn: max 3 tháng data per export

**Dependencies:** FR-016B ✅

---

## Non-Functional Requirements

---

### NFR-004: Circuit Breaker cho Pub2 Client

**Priority:** Must Have

**Description:**
Xử lý graceful khi Pub2 API down hoặc trả lỗi liên tục.

**Acceptance Criteria:**
- [ ] Circuit breaker pattern: CLOSED → OPEN → HALF_OPEN
- [ ] Threshold: 5 failures liên tiếp → OPEN (short-circuit 30s)
- [ ] Half-open: cho 1 request qua để test → nếu success → CLOSED
- [ ] Per-endpoint circuit breaker (report APIs fail không block join/link APIs)
- [ ] Logging: log state changes (CLOSED→OPEN, OPEN→HALF_OPEN, etc.)
- [ ] Frontend: hiện thông báo "Hệ thống đang bận, vui lòng thử lại" khi circuit open

**Implementation Notes:**
- Go library: `sony/gobreaker` hoặc `afex/hystrix-go`
- Implement tại `internal/module/pub2/client.go` level

---

### NFR-008: Swagger API Documentation

**Priority:** Should Have

**Description:**
Bổ sung Swagger documentation cho tất cả affiliate API endpoints.

**Acceptance Criteria:**
- [ ] Public affiliate APIs documented
- [ ] Admin affiliate APIs documented
- [ ] Request/response examples
- [ ] Error response format documented

---

### NFR-009: UTM Support (Pending Pub2)

**Priority:** Should Have — Blocked

**Description:**
Pub2 API nhận UTM fields nhưng hiện "Tạm thời không quan tâm". Khi Pub2 confirm hỗ trợ → bật UTM builder trong link generation form.

**Acceptance Criteria:**
- [ ] UTM builder accordion trong link generation form (4 fields: source, medium, campaign, content)
- [ ] Backend pass UTM to Pub2 `GenerateLinkRequest`
- [ ] Lưu UTM params vào `AffiliateLinkRaw`

**Status:** Blocked — chờ Pub2 confirm. Model Go đã có fields (`UTMSource`, `UTMMedium`, etc.)

---

## Epics

---

### EPIC-006: Campaign Discovery & Links Management

**Functional Requirements:** FR-019, FR-006

**Priority:** Must Have

**Estimated Stories:** 3-4

---

### EPIC-007: Report Charts & Data Export

**Functional Requirements:** FR-007, FR-008, FR-009, FR-010, FR-021, FR-022

**Priority:** Should Have

**Estimated Stories:** 6-8

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

Phase 3B (Should Have — Charts):
  4. Chart library setup (recharts) (~0.5 ngày)
  5. FR-007 + FR-008: Click + Conversion charts (~2 ngày)
  6. FR-010 + FR-009: Commission + Sale Amount charts (~2 ngày)

Phase 3C (Should Have — Polish):
  7. FR-021: Report caching (~1 ngày)
  8. FR-022: CSV export (~1 ngày)
  9. NFR-008: Swagger docs (~1 ngày)
  10. NFR-009: UTM support (khi Pub2 confirm)
```

**Total estimate:** ~10-12 ngày

---

## Out of Scope (V3)

1. **Webhook real-time** (Pub2 API 7 chưa có)
2. **Email digest** báo cáo hàng tuần
3. **Admin report dashboard** (admin xem tổng hợp tất cả influencers)
4. **AI campaign recommendations** dựa trên performance data
5. **Comparison charts** (so sánh giữa campaigns)
6. **Mobile SDK**
7. **WhatsApp / Instagram channels**

---

## Dependencies

### Internal (from V1 + V2 — all done)

| Dependency | Status |
|-----------|--------|
| V1: Core affiliate flow (join, link, campaigns) | ✅ |
| V2: Enhanced link generation | ✅ |
| V2: 6 report API endpoints | ✅ |
| V2: Commission Dashboard | ✅ |
| V2: Pub2 client (all methods) | ✅ |

### External

| Dependency | Status |
|-----------|--------|
| Chart library (recharts) | ⏳ Cần install |
| Pub2 UTM support | ❌ Blocked — "Tạm thời không quan tâm" |

---

## Open Questions

| # | Question | Owner | Status |
|---|----------|-------|--------|
| 1 | Chart library: recharts vs chart.js? (recommend recharts — React-native, lightweight) | Engineering | Open |
| 2 | Report caching TTL: 5 min vs 15 min? | Product + Engineering | Open |
| 3 | Circuit breaker: threshold 5 failures, recovery 30s — ok? | Engineering | Open |
| 4 | UTM: khi nào Pub2 hỗ trợ? | Pub2 team | Blocked |
| 5 | Campaign listing: cần search/filter không? Hay chỉ list + pagination? | Product | Open |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-09 | vinhnguyen | Initial V3 PRD. Deferred items from V2 + new items (caching, export, UTM). |

---

**This document was created using BMAD Method v6 - Phase 2 (Planning)**
