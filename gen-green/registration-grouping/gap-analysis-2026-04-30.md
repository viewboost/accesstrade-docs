# Gap Analysis — Registration Grouping V1 + V2

**Date:** 2026-04-30 (re-audited)
**PRD V1:** [prd-registration-v1-2026-04-12.md](prd-registration-v1-2026-04-12.md)
**PRD V2:** [prd-registration-v2-2026-04-12.md](prd-registration-v2-2026-04-12.md)
**Mục đích:** Liệt kê chức năng **chưa làm** hoặc **làm chưa đúng** so với PRD. Mỗi item dẫn link spec gốc.

---

## ❌ V1 — Chưa làm

### EPIC-006: Admin — Tab Creator (`/user-partner`) ✅ JUST DONE

#### FR-023: Filter Nơi làm việc 3-tier ([prd-v1 §FR-023](prd-registration-v1-2026-04-12.md#FR-023))
- ✅ Implement: `/user-partner` filter có `<WorkplaceFilter>` 3-tier cascading.

#### FR-024: Filter Phân loại CBNV ([prd-v1 §FR-024](prd-registration-v1-2026-04-12.md#FR-024))
- ✅ Implement: dropdown 3 options + ẩn workplace khi chọn "Không phải CBNV".

#### FR-025: Cột Hashtag cá nhân ([prd-v1 §FR-025](prd-registration-v1-2026-04-12.md#FR-025))
- ✅ Implement.

#### FR-026: Ẩn cột Ngày tạo ([prd-v1 §FR-026](prd-registration-v1-2026-04-12.md#FR-026))
- ✅ Implement.

---

### EPIC-007: Admin — Export

#### FR-029: Column Picker Dialog khi Export ([prd-v1 §FR-029](prd-registration-v1-2026-04-12.md#FR-029))
- ❌ **Chưa làm.** Modal export hiện chỉ có date range + type, **KHÔNG có checkbox chọn cột**.
- File: `admin/src/components/modal-export/index.tsx` — verify lại không thấy section Checkbox.
- Acceptance Criteria thiếu:
  - Dialog checkbox list cột
  - Default preset (bỏ tick / tick sẵn cột mới)
  - Nút "Chọn tất cả", "Mặc định"
  - Backend export API hỗ trợ param `columns[]`

#### FR-030: Export data cột mới ([prd-v1 §FR-030](prd-registration-v1-2026-04-12.md#FR-030))
- ❌ Chưa làm. Phụ thuộc FR-029. Cột Phân loại / Cơ sở / Hashtag chưa expose export.

---

### EPIC-007: Workplace Master CRUD

#### FR-031: Admin CRUD Quản lý cấu hình 3 layer ([prd-v1 §FR-031](prd-registration-v1-2026-04-12.md#FR-031))
- ✅ **CÓ TRANG admin** `/department` với 3 tabs Brand/Company/Unit (`src/pages/department/components/tab-{brand,unit,company}.tsx`).
- ⚠️ **Verify:** UI có form edit + toggle `hasLayer2`/`hasLayer3`? **Cần check thêm để xác nhận đầy đủ.**

---

### Form Profile (User)

#### FR-014: API workplace có flag `hasLayer2`/`hasLayer3` ([prd-v1 §FR-014](prd-registration-v1-2026-04-12.md#FR-014))
- ✅ **DONE — implementation khác spec nhưng đạt mục đích:**
  - Backend không có field schema `hasLayer2`/`hasLayer3`.
  - Frontend `frontend-green/src/components/form/workplace-cascading-select/` derive runtime: `hasLayer2 = brandCode && companies.length > 0`, tương tự cho Layer 3.
  - Brand không có Layer 2 → API trả empty companies → FE auto ẩn dropdown.
- ⚠️ Cách này hợp lệ — admin không cần toggle explicit, data quyết định UI. Skip nếu không có yêu cầu specific khác.

#### FR-018b: Profile Edit Mode (admin) ([prd-v1 §FR-018b](prd-registration-v1-2026-04-12.md#FR-018b))
- ⚠️ Admin user detail page **chỉ có Verify/Reject staff**, **KHÔNG có edit workplace + employeeCode manual** (`src/pages/user/index.tsx`).
- 🔧 **Cần verify spec đầy đủ + implement edit mode** nếu PRD yêu cầu.

---

## ❌ V2 — Chưa làm hoặc Sai

### Match Logic + Apply (đã có nhiều fix sau ship — PRD V2 thiếu update)

#### Bug 1: Match logic case `hasReg && !hasUser` không detect HR đính chính ✅ Fixed
- Fix: thêm action mới `registry_updated` (action thứ 9, ngoài 8 actions PRD V2 §2.3 nêu).
- ✅ PRD V2 §2.3 đã update từ "8 Action Types" → "9 Action Types" (commit `170293a`).

#### Bug 2: Cron RemoveStaffTag chỉ update User, không terminate Registry ✅ Fixed
- Fix: RemoveStaffTag nay terminate registry + unset `genGreenUserId`.
- ⚠️ **PRD V2 §FR-013 cần update** mô tả flow này.

#### Bug 3: Apply `missing_from_file` orphan record ✅ Fixed
- Trước: skip → loop vô hạn. Fix: terminate registry direct.
- ⚠️ **PRD V2 §FR-012/§FR-013 cần update.**

---

### V2 Phase tiếp theo (chưa làm)

#### Filter scope rà soát nghỉ việc theo Brand
- ❌ Status: brainstorm xong, **chưa implement**.
- Hiện tại toggle "Rà soát nghỉ việc" all-or-nothing — false positive khi HR upload file partial.
- File `pkg/admin/service/employee_registry.go` `detectMissingFromFile` chưa nhận scope.
- Recommend MVP: multi-select Brand.

#### Workplace 3-tier derive (`workplaceGroup` field)
- ❌ Schema `EmployeeRegistryRaw.WorkplaceGroup` field tồn tại nhưng **không có code populate** (chỉ ở test fixtures).
- Plan ban đầu: derive từ `workplace_units` master (brandCode/brandName) → set vào `registry.workplaceGroup`.
- UI ẩn cột "Nhóm" (commit `8fc8ffd6`) để tránh hiển thị `—` rỗng.
- 🔧 **Cần implement derive logic trong import apply phase.**

---

## ⚠️ Cần verify thêm

### FR-031 trang `/department` đầy đủ
- Có 3 tabs Brand/Company/Unit
- Cần test: form edit có chứa toggle `hasLayer2`/`hasLayer3` chưa? (depend FR-014 schema)
- Cần test: Import Excel cho master data (PRD V1 nhắc tới)

### FR-018b admin edit user profile
- Verify spec PRD chi tiết
- Implement edit workplace + emp code nếu cần

### Public API `/workplaces/brands`
- Verify response có flag `hasLayer2`/`hasLayer3` cho frontend đăng ký user (depend FR-014)

---

## ✅ Đã làm (sample)

- V1 EPIC-001 → 004: Popup, OTP, Form 3-layer, Verify staff — ship.
- V1 EPIC-005 (`/content`): Filter 3-tier, cột Phân loại + Cơ sở + Hashtag — ship.
- V1 **EPIC-006** (`/user-partner`): JUST DONE (commit `0cbf1b2c`).
- V1 EPIC-007 §FR-031: trang `/department` ship (cần verify hasLayer flags).
- V2 EPIC-001 → 005: Registry CRUD, Import pipeline, Match engine, Lifecycle, Audit — ship.
- V2 hotfix: registry_updated action, RemoveStaffTag terminate, orphan terminate — ship.

---

## Tổng kết priority

| Priority | Item | Status | Effort |
|---|---|---|---|
| ✅ Done | FR-023..FR-026 (`/user-partner`) | Done | — |
| ✅ Done | FR-014 hasLayer2/3 (FE derive runtime) | Done | — |
| ✅ Done | FR-031 trang `/department` 3 tabs Brand/Company/Unit | Done | — |
| ✅ Done | Workplace write→IsRoot | Done | — |
| ✅ Done | PRD V2 §2.3 update 9 actions | Done | — |
| 🔴 High | **PRD V2 §FR-012, §FR-013 sync** | Chưa | 1h |
| 🟠 Medium | **Workplace 3-tier derive `workplaceGroup`** | Chưa | 4h |
| 🟠 Medium | **FR-029 + FR-030 Export column picker** | Chưa | 8h |
| 🟡 Low | **V2 Filter scope theo Brand** | Chưa | 8h |
| 🟢 Verify | FR-018b admin edit profile | Verify | 2h |

**Total remaining:** ~21h dev + 2h verify.
