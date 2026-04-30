# PRD V3 — Registration Grouping (Post-Meeting 0410 Updates)

**Version:** 3.0
**Date:** 2026-04-30
**Status:** Draft — chờ QC test
**Project:** Gen-Green Registration & Account Grouping

**Tham chiếu:**
- [PRD V1](prd-registration-v1-2026-04-12.md)
- [PRD V2](prd-registration-v2-2026-04-12.md)
- [Meeting 0410](../meeting-notes/0410.md)
- [Overview V3](overview-v3.md)
- [Gap analysis](gap-analysis-2026-04-30.md)

---

## 1. Executive Summary

PRD V3 bổ sung các requirement xuất phát từ Meeting 0410 (HR + AT) chưa cover trong V1/V2. Phạm vi V3 gồm 4 module:

1. **Tab Nội dung (`/content`)** — filter + cột mới (đã ship V1 EPIC-005, document chính thức)
2. **Tab Creator (`/user-partner`)** — filter + cột (vừa ship + bổ sung)
3. **Export Column Picker** — modal export (vừa ship `/content`, mở rộng `/user-partner`)
4. **Admin Analytics Dashboard nâng cấp** — pending mockup

V3 PRD này dùng cho QC test acceptance criteria từng FR.

---

## 2. Scope

### 2.1 In Scope V3

- **Tab Nội dung:** 4 FR đã ship (FR-V3-001 → FR-V3-004)
- **Tab Creator:** 4 FR đã ship + 2 FR mới (FR-V3-005 → FR-V3-010)
- **Export:** 2 FR đã ship + 2 FR pending (FR-V3-011 → FR-V3-014)
- **Analytics Dashboard:** 3 FR pending mockup (FR-V3-015 → FR-V3-017)

### Status summary

| FR | Module | Title | Priority | Status |
|---|---|---|---|---|
| FR-V3-001 | Nội dung | Filter 3-tier | Must | ✅ Ship |
| FR-V3-002 | Nội dung | Cột Loại tài khoản | Must | ✅ Ship |
| FR-V3-003 | Nội dung | Cột Cơ sở làm việc | Must | ✅ Ship |
| FR-V3-004 | Nội dung | Cột Hashtag cá nhân | Must | ✅ Ship |
| FR-V3-005 | Creator | Filter 3-tier | Must | ✅ Ship |
| FR-V3-006 | Creator | Filter Phân loại | Must | ✅ Ship |
| FR-V3-007 | Creator | 3 cột mới (Phân loại + Cơ sở + Hashtag) | Must | ✅ Ship |
| FR-V3-008 | Creator | Ẩn cột Ngày tạo | Should | ✅ Ship |
| FR-V3-009 | Creator | Cột Tổng view | Must | ✅ Ship |
| FR-V3-010 | Creator | Cột Tổng video đã nộp | Must | ✅ Ship |
| FR-V3-011..014 | Export | Column picker /content + /user-partner | Must | (sẽ thêm) |
| FR-V3-015..017 | Analytics | Dashboard nâng cấp | Must | (pending mockup) |

### 2.2 Out of Scope V3

| Item | Defer |
|---|---|
| SSO 2 hệ thống Skelet ↔ Gen-Green | V4+ |
| Form đăng ký truyền thống thay social login | V4+ |
| Multi-select nơi làm việc (kiêm nhiệm) | V4+ |

---

## 3. Functional Requirements

### EPIC-V3-A: Tab Nội dung (`/content`)

#### FR-V3-001: Filter Cơ sở làm việc 3 layer cascading ✅ Shipped

**Priority:** Must Have
**Status:** ✅ Shipped — verify trong QC.

**Description:** Admin filter video theo workplace của creator (Brand → Company → Unit).

**Acceptance Criteria:**
- [ ] Filter section có 3 dropdown: Thương hiệu / Công ty / Cơ sở
- [ ] Chọn Brand → load Companies (filter by brandCode), Units (filter by brandCode)
- [ ] Chọn Company → reload Units (filter by brand + company)
- [ ] Disable Company + Unit khi chưa chọn Brand
- [ ] Chọn filter → table reload, chỉ video creator thuộc phạm vi
- [ ] Clear button reset về all
- [ ] Component shared `<WorkplaceFilter>` (sync với Tab Creator)

**Reference:** [PRD V1 §FR-019](prd-registration-v1-2026-04-12.md#FR-019)

---

#### FR-V3-002: Cột "Loại tài khoản" ✅ Shipped

**Priority:** Must Have
**Status:** ✅ Shipped.

**Description:** Cột hiển thị `creator.accountType` của user post video.

**Acceptance Criteria:**
- [ ] Cột "Loại tài khoản" sát cột Tên creator
- [ ] Value `staff` → Tag "Cán bộ/Nhân viên" (màu blue)
- [ ] Value `creator` → Tag "Không phải là nhân viên" (màu green)
- [ ] Value rỗng → Tag "Chưa phân loại" (màu default)

**Reference:** [PRD V1 §FR-020](prd-registration-v1-2026-04-12.md#FR-020)

---

#### FR-V3-003: Cột "Cơ sở làm việc" ✅ Shipped

**Priority:** Must Have
**Status:** ✅ Shipped.

**Description:** Cột hiển thị workplace của creator dạng gộp.

**Acceptance Criteria:**
- [ ] Format `Brand - Company - Unit` (vd "Vinpearl - VinPalace - VinPalace Cổ Loa")
- [ ] Auto skip part rỗng (nếu user không có Company → "Brand - Unit")
- [ ] Empty → hiển thị "—" màu xám
- [ ] Source: `createdBy.workplaceBrandName`, `workplaceCompanyName`, `workplaceUnitName`

**Reference:** [PRD V1 §FR-021](prd-registration-v1-2026-04-12.md#FR-021)

---

#### FR-V3-004: Cột "Hashtag cá nhân" ✅ Shipped

**Priority:** Must Have
**Status:** ✅ Shipped.

**Description:** Cột hiển thị hashtag cá nhân của creator (đỡ admin phải mapping từ Tab Creator).

**Acceptance Criteria:**
- [ ] Hiển thị `#{hashtag}` link (Typography.Link)
- [ ] Empty → "—" màu xám
- [ ] Source: `createdBy.hashtag`

**Reference:** [PRD V1 §FR-022](prd-registration-v1-2026-04-12.md#FR-022)

---

### EPIC-V3-B: Tab Creator (`/user-partner`)

#### FR-V3-005: Filter Cơ sở làm việc 3 layer ✅ Shipped

**Priority:** Must Have
**Status:** ✅ Shipped — verify trong QC.

**Description:** Tab Creator có dropdown 3 layer giống Tab Nội dung. Lọc tất cả creator thuộc phạm vi đã chọn.

**Acceptance Criteria:**
- [ ] Filter section có 3 dropdown cascading: Thương hiệu → Công ty → Cơ sở
- [ ] Component shared `<WorkplaceFilter>` (sync với Tab Nội dung)
- [ ] Chọn Brand → load Companies + Units, reset selection
- [ ] Chọn Company → reload Units (filter by brand + company)
- [ ] Disable Company + Unit khi chưa chọn Brand
- [ ] Backend filter creator theo workplace fields trong UserRaw (qua user collection lookup)
- [ ] Kết hợp được với filter Phân loại (FR-V3-006)
- [ ] Pagination + total count cập nhật đúng theo filter

**Source data:** `UserRaw.workplaceBrandCode`, `workplaceCompanyCode`, `workplaceUnitCode` (qua 2-phase query backend)

**Reference:** [PRD V1 §FR-023](prd-registration-v1-2026-04-12.md#FR-023), [Meeting 0410 line 57](../meeting-notes/0410.md)

---

#### FR-V3-006: Filter Phân loại creator ✅ Shipped

**Priority:** Must Have
**Status:** ✅ Shipped.

**Description:** Dropdown 3 options: Tất cả / CBNV / Không phải CBNV. Khi chọn "Không phải CBNV" → ẩn workplace filter.

**Acceptance Criteria:**
- [ ] Dropdown "Phân loại" với 3 options: rỗng (Tất cả) / `staff` (Cán bộ/Nhân viên) / `creator` (Không phải là nhân viên)
- [ ] Chọn `staff` → table chỉ hiện creator có `accountType = staff`
- [ ] Chọn `creator` → table chỉ hiện creator có `accountType = creator` AND ẩn/disable workplace filter (FR-V3-005)
- [ ] Chọn rỗng → tất cả creator
- [ ] Chọn "creator" + đã có workplace filter → reset workplace filter

**Reference:** [PRD V1 §FR-024](prd-registration-v1-2026-04-12.md#FR-024)

---

#### FR-V3-007: Cột "Cơ sở làm việc" (gộp Phân loại) + "Hashtag" ✅ Shipped

**Priority:** Must Have
**Status:** ✅ Shipped (post-iteration).

**Description:** Tab Creator table gộp Phân loại + Cơ sở thành 1 cột để gọn UX. Hashtag riêng.

**Acceptance Criteria:**
- [ ] Cột "Cơ sở làm việc" gộp logic phân loại:
  - `accountType = staff` → hiển thị workplace `Brand - Company - Unit` (rỗng → "—")
  - `accountType = creator` → hiển thị text "Không phải nhân viên" màu xanh
  - `accountType = null/empty` → "—"
- [ ] Cột "Hashtag" — `#{hashtag}` Typography.Link, "—" nếu rỗng

**Note:** Cột "Phân loại" riêng đã bỏ — info đã hiển thị trong "Cơ sở làm việc" qua text fallback.

**Reference:** [PRD V1 §FR-025](prd-registration-v1-2026-04-12.md#FR-025), [Meeting 0410 line 63](../meeting-notes/0410.md)

---

#### FR-V3-008: Ẩn cột "Ngày tạo", giữ "Ngày tham gia" ✅ Shipped

**Priority:** Should Have
**Status:** ✅ Shipped.

**Description:** Theo Meeting 0410 (Speaker 3 line 65-67): cột Ngày tạo không cần thiết, ẩn khỏi UI list.

**Acceptance Criteria:**
- [ ] Cột "Ngày tham gia" hiển thị (`joinedAt`)
- [ ] Cột "Ngày tạo" ẩn khỏi table UI (vẫn available trong export nếu admin tick)

**Reference:** [PRD V1 §FR-026](prd-registration-v1-2026-04-12.md#FR-026), [Meeting 0410 line 65](../meeting-notes/0410.md)

---

#### FR-V3-009: Cột "Tổng view" ✅ Shipped

**Priority:** Must Have
**Status:** ✅ Shipped 2026-04-30.

**Description:** Hiển thị tổng số views creator đã tích lũy qua tất cả videos. Speaker 3 line 63: "tổng view của họ".

**Acceptance Criteria:**
- [ ] Cột "Tổng view" với số format có thousand separator (vd `1,250,000`)
- [ ] Source: `userPartner.contentStatistic.view.total` (BE đã có sẵn field)
- [ ] Empty/0 → "0"
- [ ] Sortable (nếu BE support)

**Backend:** Field `ContentStatistic.View.Total` có sẵn trong `UserPartnerRaw`. Không cần thêm field mới.

**Frontend:** Add column trong `admin/src/pages/user-partner/components/table.tsx`. Effort ~1h.

**Reference:** [Meeting 0410 line 63](../meeting-notes/0410.md)

---

#### FR-V3-010: Cột "Tổng số video đã nộp" ✅ Shipped

**Priority:** Must Have
**Status:** ✅ Shipped 2026-04-30.

**Description:** Hiển thị tổng số video creator đã nộp về (mọi trạng thái: pending/approved/rejected). Speaker 3 line 63: "tổng số video creator đã nộp về và đã tham gia".

**Acceptance Criteria:**
- [ ] Cột "Tổng video" với số nguyên
- [ ] Source: `userPartner.contentStatistic.total` (BE đã có sẵn)
- [ ] Empty/0 → "0"
- [ ] Tooltip giải thích "Tổng tất cả video đã nộp (kể cả pending/rejected)"

**Backend:** Field `ContentStatistic.Total` có sẵn. Không cần thêm field.

**Frontend:** Add column trong table. Effort ~1h.

**Reference:** [Meeting 0410 line 63](../meeting-notes/0410.md)

---

### EPIC-V3-C: Export Column Picker

> *Sẽ bổ sung trong các bản tiếp theo.*

---

### EPIC-V3-D: Admin Analytics Dashboard

> *Pending mockup — sẽ bổ sung sau khi designer team có spec.*

---

## 4. Test Plan tổng quát

### 4.1 Tab Nội dung

**Test data:**
- 5 video — 2 từ creator CBNV (Vinpearl, GreenSM), 3 từ creator non-CBNV
- Workplace coverage: brand "Vinpearl" → company "VinPalace" → unit "VinPalace Cổ Loa", "VinPalace Ocean City"

**Test cases:**
1. Mở `/content` → 4 cột mới hiển thị đúng (Loại tài khoản, Cơ sở, Hashtag)
2. Filter Brand=Vinpearl → table chỉ video của 2 user CBNV Vinpearl
3. Filter Brand=Vinpearl, Company=VinPalace → 2 video
4. Filter Brand=Vinpearl, Company=VinPalace, Unit=VinPalace Cổ Loa → 1 video
5. Clear filter → tất cả 5 video
6. User non-CBNV → cột Cơ sở hiển thị "—", Loại tài khoản = "Không phải là nhân viên"
7. User chưa nhập hashtag → cột Hashtag hiển thị "—"

### 4.2 Tab Creator

**Test data:**
- 5 user-partner records:
  - 2 CBNV Vinpearl (1 VinPalace Cổ Loa, 1 VinPalace Ocean City) có view + video stats
  - 1 CBNV GreenSM
  - 2 non-CBNV (creator thường)
- ContentStatistic seed: user A có 10 video / 50K view, user B có 5 video / 12K view, others 0

**Test cases (FR-V3-005..008 — đã ship):**
1. Mở `/user-partner` → table có cột Cơ sở làm việc (gộp Phân loại), Hashtag, KHÔNG có cột Ngày tạo
2. Filter Brand=Vinpearl → 2 user CBNV Vinpearl hiện
3. Filter Brand=Vinpearl + Company=VinPalace + Unit=VinPalace Cổ Loa → 1 user
4. Filter Phân loại=Không phải CBNV → 2 user creator hiện, workplace filter ẩn/disabled
5. Filter Phân loại=CBNV → 3 user staff
6. Clear filter → 5 user
7. User non-CBNV: cột Cơ sở làm việc hiển thị "Không phải nhân viên" (xanh)
8. User CBNV không có workplace: cột "—"
9. User chưa có accountType: cột "—"

**Test cases (FR-V3-009 + FR-V3-010 — sau khi ship):**
8. User A: cột "Tổng view" = `50,000`, cột "Tổng video" = `10`
9. User B: cột "Tổng view" = `12,000`, cột "Tổng video" = `5`
10. User chưa có content: cả 2 cột = `0`
11. Mở admin user detail → contentStatistic match cột summary trong table

---

## 5. Migration Notes

V3 không có schema migration. Tất cả fields đã có sẵn trong V1/V2.

---

## 6. Open Questions

1. **Default Export preset** — sync với HR: dùng PRD spec (bỏ tick một số cột) hay tất cả check?
2. **Analytics Dashboard mockup** — designer team timeline?
3. **Tab Creator missing columns** (Tổng view, Tổng video) — implement V3 hay defer?

---

## 7. Changelog

| Version | Date | Author | Changes |
|---|---|---|---|
| 3.0-draft | 2026-04-30 | Claude | Initial draft — Tab Nội dung 4 FRs |
| 3.1-draft | 2026-04-30 | Claude | Tab Creator 6 FRs (4 ship + 2 pending) |
| 3.2-draft | 2026-04-30 | Claude | Tab Creator phase complete — FR-V3-009/010 shipped |
| 3.3-draft | 2026-04-30 | Claude | Tab Creator UX iteration — gộp Phân loại vào Cơ sở làm việc, layout fix scroll |
