## PRD V2 — Gen-Green Affiliate (Trích lược: Thống kê Hoa hồng & Đơn hàng)

**Date:** 2026-05-15
**Author:** vinhnguyen
**Version:** 1.0
**Status:** Draft
**Scope:** Trích lược từ [prd-v2-2026-05-12.md](prd-v2-2026-05-12.md) — chỉ giữ phần thống kê hoa hồng + đơn hàng affiliate. Bỏ toàn bộ phần kiểm tra xung đột / account linking.

**Source PRD gốc:**
- [prd-fe-creator-2026-05-04.md](prd-fe-creator-2026-05-04.md) — FE Creator

---

## Scope Summary

**Mục tiêu:** Cung cấp cho creator dashboard để xem hoa hồng + danh sách đơn hàng affiliate đã phát sinh.

| Track | FR count | Effort |
|-------|:---:|---|
| FE Creator — Commission/Orders | 2 (Commission Dashboard, Tracking events) | ~3-4d |

---

## Track 3: FE Creator — Commission & Orders

### FR-T3-009: Commission Dashboard

**Source:** FE Creator PRD — FR-009
**Priority:** Should Have V2

Trang `/affiliate-commission` — 3 KPI cards + orders list (không chart, không tabs).

**Key Acceptance Criteria:**
- Sidebar desktop / dropdown mobile: chọn campaign (hoặc "Tất cả")
- Date range filter: 7d / 1m / 3m / Custom (max 3 tháng — Scalef limit)
- 3 KPI cards: Hoa hồng chờ duyệt / tạm duyệt / đã xác nhận
- Orders table: Campaign, Order ID, Sale amount, Commission, Status badge, Ngày
- Status badge colors: Chờ duyệt (#DC6803), Đã duyệt (#1570EF), Đã nhận (#079455), Từ chối (#B42318)
- Pagination top 50

**Service methods add V2:**
- `getMyCampaigns()` — sidebar
- `reportCommission(data)`
- `reportOrders(data)`

**BE endpoints add V2:**
- `GET /affiliate-campaigns/me`
- `POST /affiliate-reports/commission`
- `POST /affiliate-reports/orders`

**Open question:** Order status `hold` (Scalef có 6 status, Ambassador chỉ map 4) — clarify với Scalef dev.

**Full spec:** [FE Creator FR-009](prd-fe-creator-2026-05-04.md#fr-009-trang-hoa-hồng-của-tôi-commission-dashboard)

---

### FR-T3-012: Tracking events (Analytics) — phần liên quan commission/orders

**Source:** FE Creator PRD — FR-012
**Priority:** Should Have V2

**Key Acceptance Criteria:**
- Events liên quan commission/orders:
  - `affiliate_section_viewed`
  - `affiliate_link_generated`
  - `affiliate_link_copied`
- Reuse analytics infrastructure GG (Firebase / GTM)

**Full spec:** [FE Creator FR-012](prd-fe-creator-2026-05-04.md#fr-012-tracking-events-analytics)

---

## Effort Estimate

| Item | Effort |
|------|---|
| FR-T3-009 Commission Dashboard | ~3d |
| FR-T3-012 Tracking (subset) | ~0.5-1d |
| **Tổng** | **~3-4d** |

---

## Open Questions

1. **Order status `hold` mapping** — block FR-T3-009 (Scalef 6 status vs Ambassador 4 status)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-15 | vinhnguyen | Trích lược từ prd-v2-2026-05-12.md, chỉ giữ phần commission/orders (FR-T3-009 + subset FR-T3-012). Bỏ toàn bộ Account Linking (Track 2) và FE Creator FR-T3-006/007. |
