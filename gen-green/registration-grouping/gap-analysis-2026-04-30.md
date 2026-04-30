# Gap Analysis — Registration Grouping V1 + V2

**Date:** 2026-04-30
**PRD V1:** [prd-registration-v1-2026-04-12.md](prd-registration-v1-2026-04-12.md)
**PRD V2:** [prd-registration-v2-2026-04-12.md](prd-registration-v2-2026-04-12.md)
**Mục đích:** Liệt kê các chức năng **chưa làm** hoặc **làm chưa đúng** so với PRD. Mỗi item dẫn link về spec gốc.

---

## ❌ V1 — Chưa làm hoặc Sai

### EPIC-006: Admin — Tab Creator (`/user-partner`)

**Status:** Hầu hết chưa làm.

#### FR-023: Filter Nơi làm việc 3-tier ([prd-v1 §FR-023](prd-registration-v1-2026-04-12.md#FR-023))
- ❌ Chưa có. Filter `/user-partner` hiện chỉ có User + Partner.
- 🔧 Đang implement (cùng commit gap-analysis này).

#### FR-024: Filter Phân loại CBNV ([prd-v1 §FR-024](prd-registration-v1-2026-04-12.md#FR-024))
- ❌ Chưa có. Cần dropdown 3 options: Tất cả / CBNV / Không phải CBNV.
- 🔧 Đang implement.

#### FR-025: Cột Hashtag cá nhân ([prd-v1 §FR-025](prd-registration-v1-2026-04-12.md#FR-025))
- ⚠️ Có hashtag trong response nhưng **chưa hiện cột** trong table.
- 🔧 Đang implement.

#### FR-026: Ẩn cột Ngày tạo, giữ Ngày tham gia ([prd-v1 §FR-026](prd-registration-v1-2026-04-12.md#FR-026))
- ⚠️ Cần verify table hiện đang có cột nào (Ngày tạo vs Ngày tham gia).
- 🔧 Đang implement.

---

### EPIC-007: Admin — Export & Quản trị data nơi làm việc

#### FR-029: Column Picker Dialog khi Export ([prd-v1 §FR-029](prd-registration-v1-2026-04-12.md#FR-029))
- ❌ Chưa làm. Modal export hiện chỉ có date range + type, không có checkbox chọn cột.
- File: `admin/src/components/modal-export/index.tsx`
- Acceptance Criteria thiếu hết:
  - Dialog checkbox list cột
  - Default preset (bỏ tick / tick sẵn cột mới)
  - Nút "Chọn tất cả", "Mặc định"
  - Backend export API hỗ trợ param `columns[]`

#### FR-030: Export data cột mới ([prd-v1 §FR-030](prd-registration-v1-2026-04-12.md#FR-030))
- ❌ Chưa làm. Phụ thuộc FR-029.
- Cột Phân loại / Cơ sở / Hashtag chưa được expose trong export.

#### FR-031: Admin CRUD Quản lý cấu hình 3 layer ([prd-v1 §FR-031](prd-registration-v1-2026-04-12.md#FR-031))
- ❌ Chưa có trang admin `/workplace-management` (hoặc tương tự).
- Backend đã có endpoint CRUD (`/workplace-brands`, `/workplace-companies`, `/workplace-units` — POST/PUT/PATCH).
- Frontend chưa có UI để admin manage. Hiện admin phải thao tác trực tiếp DB.
- Acceptance thiếu:
  - List + filter brand/company/unit
  - Form add/edit brand với toggle hasLayer2/hasLayer3
  - Bật/tắt status active/inactive

---

### EPIC-002 / 003 — Form Profile (cần verify)

#### FR-014: API workplace có flag hasLayer2/hasLayer3 ([prd-v1 §FR-014](prd-registration-v1-2026-04-12.md#FR-014))
- ⚠️ Cần verify response `/workplace-brands` có trả `hasLayer2` / `hasLayer3` không. Nếu chưa → form đăng ký không thể conditional render Layer 2/3.

#### Quy tắc "Khác" sentinel ([prd-v1 §FR-012](prd-registration-v1-2026-04-12.md#FR-012))
- ⚠️ Cần verify backend xử lý 2 case khác nhau:
  - Brand không có Layer 2 → user được auto-set `workplace_company = "other"` (sentinel)
  - User chọn option "Khác" trong dropdown → lưu code thực của record (vd `gsm_other`)

---

## ❌ V2 — Chưa làm hoặc Sai

### Match Logic + Apply

Hiện tại **đã ship hết** các FR-001 → FR-018 trong V2 PRD theo bảng "Đã ship". Tuy nhiên có 1 số bug + thiếu sót phát hiện sau audit (chưa ghi vào PRD V2):

#### Bug 1: Match logic case `hasReg && !hasUser` không detect HR đính chính ✅ Fixed
- Trước: luôn flag `unchanged` dù phone/workplace HR đổi.
- Fix: thêm action mới `registry_updated` (action thứ 9, ngoài 8 actions PRD V2 §2.3 nêu).
- ⚠️ **PRD V2 §2.3 cần update:** thêm action `registry_updated` vào bảng 8 actions → 9 actions. **(Đã update trong commit `cd1d140`.)**

#### Bug 2: 2 user cùng employeeCode ✅ Partially fixed
- Scenario: user A và B đăng ký trước HR import, cùng mã NV khác phone.
- Hiện tại: A khớp phone → verified, B → vẫn pending với cùng mã NV.
- Behavior này đúng với spec PRD nhưng để lại "dirty data" — B cần admin xử lý manual.
- 🔧 **Chưa có trong PRD V2.** Cân nhắc thêm FR mới: bulk match cleanup user khác phone cùng code → flag `cancelled_mismatch`.

#### Bug 3: Cron RemoveStaffTag chỉ update User, không terminate Registry ✅ Fixed
- Trước: cron gỡ user staff tag nhưng registry vẫn `active`, `genGreenUserId` còn link → trang admin hiển thị nhân viên đã nghỉ là "Đã khớp".
- Fix: RemoveStaffTag nay terminate registry + unset `genGreenUserId`.
- ⚠️ **PRD V2 §FR-013 cần update:** mô tả flow này.

#### Bug 4: Apply `missing_from_file` orphan record (registry chưa user claim) ✅ Fixed
- Trước: skip → loop vô hạn (mỗi import flag missing).
- Fix: terminate registry direct (không grace period).
- ⚠️ **PRD V2 §FR-012/FR-013 cần update.**

---

### V2 Phase tiếp theo (chưa làm)

#### Filter scope rà soát nghỉ việc theo Brand/Company/Unit
- Status: brainstorm xong, chưa implement.
- Hiện tại toggle "Rà soát nghỉ việc" all-or-nothing — nếu HR upload file partial (vd 1 brand) + bật toggle → false positive flag toàn corp.
- Recommend: Phase MVP — multi-select Brand. (Chi tiết trong session brainstorm trước đó.)

#### Workplace 3-tier derive (`workplaceGroup` field)
- ⚠️ PRD V2 §EPIC-001 §FR-001 schema có field `workplaceGroup` nhưng đang **bỏ trống** (defer đợt 2).
- Plan Phase D ban đầu nói: derive từ `workplace_units` master (brandCode/brandName).
- Hiện UI ẩn cột "Nhóm" để tránh hiển thị `—` rỗng (commit `8fc8ffd6`).
- 🔧 Cần implement derive logic + populate field.

---

## ⚠️ Cần verify

### Profile Edit (FR-018b)
- File `admin/src/pages/user/detail/components/tabs/overview/index.tsx` — có section staff verify nhưng **chưa rõ edit-mode** đầy đủ (sửa workplace, mã NV, etc.).
- ⚠️ Cần kiểm tra spec FR-018b vs implementation.

### Public API workplace (FR-014)
- ⚠️ Verify `/workplaces/brands` (public, no auth) trả đầy đủ flag `hasLayer2/hasLayer3` cho frontend đăng ký user.

---

## ✅ Đã làm (sample, không ghi đầy đủ)

- V1 EPIC-001 → 004: Popup, OTP, Form 3-layer, Verify staff — ship.
- V1 EPIC-005 (`/content`): Filter 3-tier, cột Phân loại + Cơ sở + Hashtag — ship.
- V2 EPIC-001 → 005: Registry CRUD, Import pipeline, Match engine, Lifecycle, Audit — ship (với các bug đã fix bổ sung trong V2 hotfix).

---

## Tổng kết

**Còn lại priority:**

| Priority | Item | Effort estimate |
|---|---|---|
| 🔴 High | FR-023 + FR-024 + FR-025 + FR-026 (`/user-partner`) | 4h (đang làm) |
| 🟠 Medium | FR-029 + FR-030 (Export column picker) | 8h |
| 🟠 Medium | FR-031 (Admin CRUD workplace) | 16h |
| 🟡 Low | V2 Filter scope theo Brand cho rà soát nghỉ việc | 8h |
| 🟡 Low | Workplace 3-tier derive (`workplaceGroup`) | 4h |
| 🟢 Verify | FR-014 hasLayer2/hasLayer3 public API | 1h |
| 🟢 Verify | FR-018b Profile edit mode | 2h |
| 🟠 Update | PRD V2 §FR-012, §FR-013, §2.3 — sync với fix sau ship | 1h |

**Total estimate:** ~44h dev + 4h verify/docs.
