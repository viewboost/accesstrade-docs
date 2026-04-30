# Overview V3 — Registration Grouping (Gap Items + Meeting Follow-up)

**Date:** 2026-04-30
**Source:**
- PRD V1: [prd-registration-v1-2026-04-12.md](prd-registration-v1-2026-04-12.md)
- PRD V2: [prd-registration-v2-2026-04-12.md](prd-registration-v2-2026-04-12.md)
- Meeting 0410: [meeting-notes/0410.md](../meeting-notes/0410.md)
- Gap analysis: [gap-analysis-2026-04-30.md](gap-analysis-2026-04-30.md), [gap-meeting-0410-vs-impl-2026-04-30.md](gap-meeting-0410-vs-impl-2026-04-30.md)

**Mục đích:** Tổng hợp các chức năng **chưa làm** hoặc **đã làm nhưng chưa đúng spec** sau khi review V1+V2 + Meeting 0410. Gom theo **module/tab** để dễ theo dõi.

---

## Trạng thái tóm gọn

| Module | Tổng items | Done | Pending |
|---|---|---|---|
| 🎥 Tab Nội dung (`/content`) | 5 | 5 | 0 |
| 👤 Tab Creator (`/user-partner`) | 6 | 4 | **2** |
| 📤 Export | 4 | 1 | **3** |
| 📊 Admin Analytics Dashboard | 3 | 0 | **3** |
| 🔧 Backend V2 (employee-registry) | 3 | 0 | **3** |
| 🔍 Verify items | 1 | 0 | 1 |

**Total pending: 12 items, ~46h dev.**

---

## 🎥 Module 1: Tab Nội dung (`/content`)

✅ **Done — không có gap.**

| FR | Item | Status |
|---|---|---|
| FR-019 | Filter 3-tier workplace cascading | ✅ |
| FR-020 | Cột Phân loại CBNV | ✅ |
| FR-021 | Cột Cơ sở làm việc | ✅ |
| FR-022 | Cột Hashtag cá nhân | ✅ |

---

## 👤 Module 2: Tab Creator (`/user-partner`)

### ✅ Done

| FR | Item |
|---|---|
| FR-023 | Filter 3-tier workplace |
| FR-024 | Filter Phân loại CBNV |
| FR-025 | Cột Hashtag cá nhân + Cơ sở làm việc |
| FR-026 | Ẩn cột Ngày tạo, giữ Ngày tham gia |

### ❌ Thiếu so với Meeting 0410

Meeting yêu cầu Tab Creator hiển thị **"trực quan"** với các cột:

| Cột | Status hiện tại | Effort |
|---|---|---|
| Tên | ✅ | — |
| Hashtag cá nhân | ✅ | — |
| **Tổng view** (creator's total views) | ❌ Chưa có | 1h |
| Tổng tiền (cash remaining) | ✅ | — |
| Tổng tiền đã rút (cash withdraw) | ✅ | — |
| **Tổng số video đã nộp/tham gia** | ❌ Chưa có | 1h |
| Ngày tham gia | ✅ | — |

**Effort:** 2h backend + frontend.

---

## 📤 Module 3: Export

### ✅ Done

| FR | Item |
|---|---|
| FR-029 (1/2) | Export `/content` Column Picker Dialog với 25 cột |
| FR-030 (1/2) | Export `/content` 3 cột mới (Phân loại / Cơ sở / Hashtag) |

### ⚠️ Default preset SAI spec PRD

PRD V1 §FR-029 nói default preset:
- **Bỏ tick:** ID video, Thumbnail, Đối tác/Mã sự kiện, Tích cực/Trung lập/Tiêu cực
- **Tick sẵn:** cột mới (Phân loại / Cơ sở / Hashtag) + standard

Hiện tại implement: **tất cả checked default** (theo user override gần đây).

→ **Cần confirm** với HR/operation: dùng default theo spec hay giữ tất cả check?

### ❌ Thiếu

| Item | Effort |
|---|---|
| Export `/user-partner` Column Picker — meeting yêu cầu cả 2 tab | 4h |
| Backend `export_user_partner.go` thêm 3 cột mới (Phân loại / Nơi làm việc / Hashtag) | 2h |
| **FR-031** Admin CRUD Workplace Master với toggle `hasLayer2/3` | ⚠️ verify (page `/department` có sẵn nhưng chưa rõ form edit có toggle) |

**Effort:** 4-6h.

---

## 📊 Module 4: Admin Analytics Dashboard ⚠️ Critical Gap

**Cam kết Meeting 0410 (Speaker 1 Vĩnh):**

> "Mình sửa nhiều để đưa cái màn hình thống kê ra một cái màn hình tiện dụng hơn. Nhiều bộ lọc."

> "Trước khi làm thì mình sẽ tổng hợp lại rồi mình lên một cái mockup."

**Speaker 2 yêu cầu cụ thể:**

> "Em muốn biết bao nhiêu CBNV của Phú Quốc tham gia chương trình ABC. Em chỉ muốn chọn đây và nhìn số ngay, thay vì kéo Excel xuống filter."

### Status

❌ **Hoàn toàn chưa làm:**
- Chưa có mockup
- Chưa có spec/PRD epic riêng
- Code chưa nâng cấp

### Items cần làm

| # | Item | Effort |
|---|---|---|
| 4.1 | **Mockup dashboard analytics** | 4h thiết kế |
| 4.2 | PRD spec mới — bổ sung filter CBNV / Workplace 3-tier / Sự kiện | 2h |
| 4.3 | Implement filter + tổng hợp số liệu | 12h |

**Effort:** ~18h. Cần PM/PO duyệt trước khi code.

---

## 🔧 Module 5: Backend V2 (Employee Registry)

### ❌ Chưa làm (từ gap-analysis V2)

| Item | Effort | Files chính |
|---|---|---|
| **5.1** Workplace 3-tier derive `workplaceGroup` populate từ master `workplace_units` | 4h | `pkg/admin/service/employee_registry_apply.go`, `internal/service/workplace_group.go` (NEW), registry table UI |
| **5.2** V2 Filter scope theo Brand cho rà soát nghỉ việc — thay toggle all-or-nothing | 8h | Schema `ImportHistory.detectMissingScope`, `detectMissingFromFile(scope)`, upload modal multi-select Brand |
| **5.3** PRD V2 §EPIC-001 §FR-001 schema spec đã ghi `workplaceGroup` nhưng "derive đợt 2" — chưa implement | (gộp vào 5.1) | — |

**Effort:** ~12h.

---

## 🔍 Module 6: Verify Items

### ⚠️ Cần verify trước khi quyết định implement

| Item | Effort | Note |
|---|---|---|
| **6.1** FR-018b Admin edit user profile (workplace + employeeCode) | 30min verify + 3h impl nếu cần | Hiện admin chỉ verify/reject, không edit fields |
| **6.2** FR-031 trang `/department` form edit có toggle `hasLayer2/3` chưa? | 30min verify | UI có 3 tabs Brand/Company/Unit nhưng chưa rõ form |

**Effort:** 1h verify, +3h nếu phải implement FR-018b.

---

## 📋 Roadmap đề xuất

### Sprint A — Quick wins (~10h)

1. **Module 2:** Add 2 cột Tổng view + Tổng video vào `/user-partner` table (2h)
2. **Module 5.1:** Workplace `workplaceGroup` derive (4h)
3. **Module 6.1 + 6.2:** Verify FR-018b + FR-031 form (1h)
4. **Module 3:** Confirm default preset Export — sync với HR (30min discuss)
5. **Module 3:** Mở rộng Column Picker cho `/user-partner` export + 3 cột mới (5h)

### Sprint B — Critical Gap (~18h, cần PM/Designer)

1. **Module 4:** Phối hợp Designer làm mockup Dashboard Analytics
2. **Module 4:** PRD spec EPIC mới cho Analytics nâng cấp
3. **Module 4:** Implement filter analytics theo CBNV/Workplace/Sự kiện

### Sprint C — V2 Filter Scope (~8h)

1. **Module 5.2:** Brainstorm flow upload modal multi-select Brand
2. Schema migration `ImportHistory.detectMissingScope`
3. Match logic + UI badge scope

---

## Mapping nhanh tới spec gốc

| Module | Section | PRD ref |
|---|---|---|
| Tab Nội dung | EPIC-005 | [prd-v1 §EPIC-005](prd-registration-v1-2026-04-12.md#EPIC-005) |
| Tab Creator | EPIC-006 | [prd-v1 §EPIC-006](prd-registration-v1-2026-04-12.md#EPIC-006) |
| Export | EPIC-007 | [prd-v1 §EPIC-007](prd-registration-v1-2026-04-12.md#EPIC-007) |
| Admin Analytics | (chưa có epic) | Cần tạo EPIC-008 mới |
| BE V2 Employee Registry | EPIC-001..005 | [prd-v2](prd-registration-v2-2026-04-12.md) |

---

## Open questions

1. **Default Export preset** — sync với HR: dùng PRD spec (bỏ tick một số cột) hay tất cả check?
2. **Analytics Dashboard** — ai làm mockup? Designer team có sẵn? Hay dev tự lo?
3. **V2 Filter scope theo Brand** — cần brainstorm UX flow trước (upload modal vs preview-time scope picker?)
4. **FR-018b** — admin edit profile có cần thiết không, hay flow reject + user resubmit là đủ?
