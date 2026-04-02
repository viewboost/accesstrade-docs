# Product Requirements Document: Cấu Hình Hiển Thị BXH theo Partner

**Date:** 2026-04-02
**Author:** Vinh Nguyen
**Version:** 1.1
**Project Level:** Level 1
**Status:** Draft

---

## Document Overview

PRD cho tính năng cho phép Admin cấu hình hiển thị **Bảng xếp hạng (BXH)** và **số tiền trong BXH** theo từng Partner. Setup trong form chi tiết Partner (không phải CRUD).

**Related Documents:**
- Partner model: `backend/internal/model/mg/partner.go`
- Admin Partner modal: `admin/src/pages/partner/components/modal.tsx`
- Leaderboard component: `frontend/src/pages/home/components/leaderboard-list/index.tsx`
- Leaderboard API: `backend/pkg/public/router/event.go` (GET `/:id/leaderboards`)

---

## Executive Summary

Hiện tại, BXH (Bảng xếp hạng) hiển thị mặc định cho tất cả Partner — không có cách nào để Admin bật/tắt BXH hoặc ẩn/hiện số tiền theo từng Partner.

**Giải pháp:** Thêm 2 field config vào `PartnerRaw` model:
- `showLeaderboard` — Có hiển thị BXH hay không
- `showLeaderboardAmount` — Có hiển thị số tiền trong BXH hay không

Admin setup 2 toggle này trong form chi tiết Partner. Frontend đọc config từ partner data để quyết định hiển thị.

**Scope nhỏ gọn:** Chỉ thêm 2 field boolean vào Partner. Không thay đổi logic BXH, không tạo API mới.

---

## Product Goals

### Business Objectives

1. **Linh hoạt theo Partner** — Một số Partner không muốn hiển thị BXH hoặc không muốn lộ số tiền
2. **Admin tự quản lý** — Không cần deploy code khi thay đổi cấu hình hiển thị BXH

### Success Metrics

| Metric | Target |
|--------|--------|
| Admin tự bật/tắt BXH cho Partner | < 1 phút |
| Không cần deploy để thay đổi config | 0 lần deploy |

---

## Functional Requirements

### FR-001: Thêm field `showLeaderboard` vào Partner Model

**Priority:** Must Have

**Description:**
Thêm field `showLeaderboard` (type `*bool`) vào `PartnerRaw` struct. Quyết định có hiển thị BXH cho Partner này hay không.

**Thay đổi cụ thể:**
```go
// PartnerRaw — thêm field:
ShowLeaderboard       *bool `bson:"showLeaderboard,omitempty" json:"showLeaderboard,omitempty"`
```

**Default behavior:**
- Nếu field null/undefined → hiển thị BXH (backward compatible, giữ behavior hiện tại)
- Nếu `false` → ẩn BXH hoàn toàn
- Nếu `true` → hiển thị BXH

**Acceptance Criteria:**
- [ ] Field `showLeaderboard` được thêm vào `PartnerRaw` struct
- [ ] Field optional (omitempty) — Partner cũ không bị ảnh hưởng
- [ ] Default behavior: null = hiển thị (backward compatible)

---

### FR-002: Thêm field `showLeaderboardAmount` vào Partner Model

**Priority:** Must Have

**Description:**
Thêm field `showLeaderboardAmount` (type `*bool`) vào `PartnerRaw` struct. Quyết định có hiển thị **số tiền (cash)** trong BXH hay không. Khi ẩn, BXH chỉ hiển thị **số view** theo platform.

**Clarification "số tiền":**
- **Cash** = `TotalCash`, `TotalCashPending`, `TotalCashCompleted`, `CashReward`, `TotalCommission` — các field liên quan đến tiền thưởng
- **View** = `statistic.[platform].view.completed` — số lượt xem theo platform (youtube, tiktok, facebook...)
- Khi `showLeaderboardAmount = false`: ẩn cash, **giữ nguyên số view**

**Thay đổi cụ thể:**
```go
// PartnerRaw — thêm field:
ShowLeaderboardAmount *bool `bson:"showLeaderboardAmount,omitempty" json:"showLeaderboardAmount,omitempty"`
```

**Default behavior:**
- Nếu field null/undefined → hiển thị số tiền (backward compatible)
- Nếu `false` → ẩn số tiền (cash) trong BXH, giữ số view
- Nếu `true` → hiển thị số tiền

**Acceptance Criteria:**
- [ ] Field `showLeaderboardAmount` được thêm vào `PartnerRaw` struct
- [ ] Field optional (omitempty) — Partner cũ không bị ảnh hưởng
- [ ] Default behavior: null = hiển thị (backward compatible)

---

### FR-003: Admin Setup Config BXH trong Form Chi Tiết Partner

**Priority:** Must Have

**Description:**
Thêm 2 toggle (Switch) vào modal Partner trên Admin dashboard. Admin có thể bật/tắt:
- Hiển thị BXH
- Hiển thị số tiền trong BXH

Toggle nằm trong section riêng "Cấu hình BXH" trong modal Partner.

**Acceptance Criteria:**
- [ ] Modal Partner có thêm section "Cấu hình BXH" (hoặc "Leaderboard")
- [ ] Toggle "Hiển thị BXH" — map với field `showLeaderboard`
- [ ] Toggle "Hiển thị số tiền trong BXH" — map với field `showLeaderboardAmount`
- [ ] Cả 2 toggle default ON (checked) khi tạo Partner mới
- [ ] Khi `showLeaderboard` = OFF → toggle `showLeaderboardAmount` bị disable (không có BXH thì không cần config tiền)
- [ ] Giá trị được lưu khi submit form Partner

---

### FR-004: Frontend Đọc Config BXH từ Partner Data

**Priority:** Must Have

**Description:**
Frontend đọc `showLeaderboard` và `showLeaderboardAmount` từ partner data (trong event detail hoặc partner detail API). Dựa vào config để quyết định hiển thị.

**Logic hiển thị:**

| showLeaderboard | showLeaderboardAmount | Kết quả |
|---|---|---|
| null / true | null / true | Hiển thị BXH + view + cash (hiện tại) |
| null / true | false | Hiển thị BXH + view, **ẩn cash** |
| false | (bất kỳ) | Ẩn toàn bộ BXH |

**Acceptance Criteria:**
- [ ] Frontend đọc config từ partner data
- [ ] Nếu `showLeaderboard` = false → ẩn component `LeaderBoardList`
- [ ] Nếu `showLeaderboardAmount` = false → ẩn cash/commission trong BXH, giữ nguyên số view theo platform
- [ ] Nếu field null/undefined → hiển thị như hiện tại (backward compatible)

---

## Non-Functional Requirements

### NFR-001: Backward Compatibility

**Priority:** Must Have

**Description:**
2 field mới phải không ảnh hưởng Partner cũ. MongoDB schemaless nên Partner cũ tự động có cả 2 field = null → behavior giữ nguyên (hiển thị BXH + tiền).

**Acceptance Criteria:**
- [ ] Partner cũ không bị lỗi khi thiếu field
- [ ] API response Partner cũ: 2 field không xuất hiện hoặc null
- [ ] Không cần migration data
- [ ] Frontend xử lý null/undefined = hiển thị

---

## Implementation Scope

### Thay đổi cần làm:

| Layer | File | Thay đổi |
|-------|------|----------|
| **Model** | `backend/internal/model/mg/partner.go` | Thêm 2 field `ShowLeaderboard`, `ShowLeaderboardAmount` vào `PartnerRaw` |
| **Admin Request** | `backend/pkg/admin/model/request/partner.go` | Thêm 2 field vào request struct |
| **Admin Response** | `backend/pkg/admin/model/response/partner.go` | Thêm 2 field vào response struct |
| **Public Response** | `backend/pkg/public/model/response/event.go` | Thêm 2 field vào `EventDetailResponse` (partner config truyền qua event) |
| **Admin UI** | `admin/src/pages/partner/components/modal.tsx` | Thêm 2 Switch toggle trong section "Cấu hình BXH" |
| **Admin Type** | `admin/src/pages/partner/type.d.ts` | Thêm 2 field vào `Partner.Info` |
| **Frontend** | `frontend/src/pages/home/components/leaderboard-list/index.tsx` | Check config trước khi render |
| **Frontend** | `frontend/src/pages/home/components/content-rank-item/index.tsx` | Check config ẩn/hiện số tiền |

### KHÔNG làm:
- Không tạo MongoDB collection mới
- Không tạo API endpoint mới
- Không tạo admin page/router mới
- Không thay đổi logic tính BXH
- Không thay đổi API leaderboard response (chỉ thay đổi frontend render)

---

## User Flow

### Admin Setup

```
Admin mở Partner modal (Edit)
→ Thấy section "Cấu hình BXH"
→ Toggle "Hiển thị BXH": ON/OFF
→ Toggle "Hiển thị số tiền trong BXH": ON/OFF (disable nếu BXH = OFF)
→ Save Partner
→ Done — frontend áp dụng ngay
```

### KOC Xem Event

```
KOC mở trang Event của Partner
→ Nếu Partner config showLeaderboard = true/null → thấy BXH
→ Nếu Partner config showLeaderboardAmount = false → BXH không có số tiền
→ Nếu Partner config showLeaderboard = false → không thấy BXH
```

---

## Cache Invalidation

**Đã có sẵn** — Admin partner service có `clearCache()` (`backend/pkg/admin/service/partner.go:252`) tự động xóa:
- `CacheListPartner` (`list_partner_active_*`)
- `CacheDomainListPartner` (`domain_partner_*`)

Flow update partner hiện tại đã gọi `clearCache()`. **Không cần thêm logic cache invalidation mới.**

---

## Assumptions

1. Partner data đã available trong event detail context trên frontend (hoặc có thể truyền qua event detail API)
2. Flow update Partner hiện tại đã handle cache invalidation (confirmed: `clearCache()` đã có)
3. Frontend có thể access partner config khi render leaderboard component

---

## Out of Scope

- Config BXH theo từng Event (chỉ config theo Partner)
- Thay đổi ranking algorithm
- Thay đổi leaderboard API response structure
- Custom columns trong BXH (chỉ bật/tắt toàn bộ hoặc bật/tắt số tiền)
- Phân quyền: ai được thay đổi config (dùng quyền admin Partner hiện tại)

---

## Resolved Questions

1. **Config theo Partner hay Event?** → **Theo Partner**, setup trong chi tiết Partner. Apply cho tất cả event của Partner đó.
2. **"Số tiền" cụ thể là gì?** → **Cash** (TotalCash, CashReward, commission). Khi ẩn, BXH chỉ hiển thị số view theo platform.
3. **Cache invalidation** → **Đã có sẵn**. `clearCache()` trong admin partner service tự động xóa cache khi update partner.

## Open Questions

_(Không còn)_

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-02 | Vinh Nguyen | Initial PRD |
| 1.1 | 2026-04-02 | Vinh Nguyen | Resolved open questions: config theo Partner, "số tiền" = cash (giữ view), cache đã có sẵn |
