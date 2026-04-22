# PRD: Admin Dashboard Upgrade — Phân loại CBNV & Export

**Project:** Gen-Green Admin Dashboard Upgrade
**Date:** 2026-04-12
**Version:** 1.0
**Author:** Product Manager
**Status:** Draft
**Source:** [overview.md](overview.md)
**Related:** [VCreator Dashboard v2 PRD](../vcreator-dashboard/prd-vcreator-dashboard-v2-2026-04-12.md)

---

## 1. Executive Summary

Nâng cấp admin dashboard Gen-Green hiện tại (UMI) để hỗ trợ phân loại **CBNV / Bên ngoài**, filter theo **Cơ sở làm việc**, hiển thị thêm cột **Hashtag cá nhân**, và cho phép **chọn cột khi export**. Mục tiêu: team vận hành trả lời câu hỏi "bao nhiêu CBNV của cơ sở X tham gia chương trình Y?" trực tiếp trên giao diện, thay vì export → filter Excel.

**Lưu ý:** PRD này dành cho upgrade admin dashboard hiện tại. VCreator Dashboard v2 (clone từ TCB) có PRD riêng và đã bao gồm sẵn các yêu cầu CBNV/export.

---

## 2. Business Objectives

| # | Objective | Success Metric |
|---|-----------|----------------|
| 1 | Giảm thao tác thủ công khi lọc data CBNV | Thời gian tạo report CBNV giảm từ ~30 phút (export + Excel) xuống < 1 phút (filter trực tiếp) |
| 2 | Phân biệt CBNV và creator bên ngoài trên dashboard | 100% video/creator hiển thị phân loại + cơ sở làm việc |
| 3 | Tối ưu export: bỏ cột thừa, thêm cột mới, cho phép chọn | Export file size giảm ≥ 40% nhờ bỏ cột thừa mặc định |
| 4 | Không ảnh hưởng team khác cùng dùng export | Cơ chế chọn cột = mỗi user tự quyết, không bỏ cột cứng |

---

## 3. Scope

### In Scope

- Tab Nội dung: thêm filter, cột mới, chỉnh export
- Tab Creator: thêm filter, cột mới, chỉnh export
- Màn hình Thống kê (Analytics): thêm filter CBNV + Cơ sở
- Export chung: cơ chế chọn cột (column picker dialog)

### Out of Scope

| Feature | Lý do |
|---------|-------|
| VCreator Dashboard v2 (Next.js 16) | PRD riêng, clone từ TCB |
| Form đăng ký CBNV (thu thập workplace data) | Scope riêng, là prerequisite |
| Affiliate dashboard (Scalef data) | Scope riêng |
| Saved presets / drag-drop sắp xếp cột export | V2 — chỉ checkbox list + default preset cho V1 |
| Sentiment analysis mới | Giữ nguyên, chỉ bỏ khỏi default export |

---

## 4. Functional Requirements

### EPIC-001: Tab Nội dung — Filter & Cột mới

#### FR-001: Filter Cơ sở làm việc trên tab Nội dung

**Priority:** Must Have

**Description:**
Thêm dropdown filter "Cơ sở làm việc" trên tab Nội dung. Grouped dropdown (6 nhóm, ~57 cơ sở). Lọc video theo cơ sở làm việc của creator.

**Acceptance Criteria:**
- [ ] Grouped dropdown với 6 nhóm: VinPalace, Vinpearl, VinWonders, Vinpearl Golf, Green SM, Khác
- [ ] ~57 cơ sở hiển thị đúng nhóm
- [ ] Có search text trong dropdown
- [ ] Chọn cơ sở → table chỉ hiện video của creator thuộc cơ sở đó
- [ ] Kết hợp được với filter Event + filter khác hiện có

**Dependencies:** Backend field `workplace_name` trên user/content response

---

#### FR-002: Cột Phân loại creator trên tab Nội dung

**Priority:** Must Have

**Description:**
Thêm cột "Phân loại" vào table Nội dung. Hiển thị "CBNV" hoặc "Bên ngoài" cho mỗi video, dựa trên `account_type` của creator.

**Acceptance Criteria:**
- [ ] Cột hiển thị đúng giá trị: "CBNV" (`account_type = staff`) / "Bên ngoài" (`account_type = creator`)
- [ ] Badge phân biệt màu: CBNV (xanh), Bên ngoài (xám)
- [ ] Cột nằm gần cột Tên creator để dễ đọc

**Dependencies:** Backend field `account_type` trên content response

---

#### FR-003: Cột Cơ sở làm việc trên tab Nội dung

**Priority:** Must Have

**Description:**
Thêm cột "Cơ sở làm việc" vào table Nội dung. Hiển thị tên cơ sở của creator (ví dụ: "VinWonders Phú Quốc").

**Acceptance Criteria:**
- [ ] Hiển thị tên cơ sở hoặc "—" nếu không có (creator bên ngoài)
- [ ] Data join từ user profile, không cần lookup riêng

**Dependencies:** Backend field `workplace_name` trên content response

---

#### FR-004: Cột Hashtag cá nhân trên tab Nội dung

**Priority:** Must Have

**Description:**
Thêm cột "Hashtag cá nhân" vào table Nội dung. Hiện hashtag cá nhân của creator tại mỗi video, để team vận hành không cần mapping thủ công từ tab Creator.

**Acceptance Criteria:**
- [ ] Hiển thị hashtag cá nhân (đã có ở tab Creator, cần join vào content response)
- [ ] Hiển thị "—" nếu creator chưa có hashtag

**Dependencies:** Backend join `personal_hashtag` vào content response

---

### EPIC-002: Tab Nội dung — Export

#### FR-005: Bỏ cột thừa khỏi default export tab Nội dung

**Priority:** Must Have

**Description:**
Các cột sau mặc định bỏ tick (unchecked) trong export dialog tab Nội dung:
- ID video
- Thumbnail
- Đối tác / Mã sự kiện
- Tích cực / Trung lập / Tiêu cực (3 cột sentiment)

**Acceptance Criteria:**
- [ ] 6 cột trên mặc định unchecked trong column picker
- [ ] User vẫn có thể tick lại nếu muốn
- [ ] Không bỏ cột hoàn toàn — chỉ thay đổi default state

**Dependencies:** FR-012 (Column Picker Dialog)

---

#### FR-006: Thêm cột mới vào export tab Nội dung

**Priority:** Must Have

**Description:**
Thêm 3 cột mới vào danh sách export tab Nội dung: Cơ sở làm việc, Hashtag cá nhân, Phân loại (CBNV/Bên ngoài). Mặc định tick (checked).

**Acceptance Criteria:**
- [ ] 3 cột mới xuất hiện trong column picker
- [ ] Mặc định checked
- [ ] Data xuất đúng giá trị

**Dependencies:** FR-002, FR-003, FR-004, FR-012

---

### EPIC-003: Tab Creator — Filter & Cột

#### FR-007: Filter Nơi làm việc trên tab Creator

**Priority:** Must Have

**Description:**
Thêm dropdown filter "Nơi làm việc" trên tab Creator. Grouped dropdown, lọc tất cả CBNV thuộc 1 cơ sở.

**Acceptance Criteria:**
- [ ] Grouped dropdown giống FR-001 (6 nhóm, ~57 cơ sở)
- [ ] Chọn cơ sở → hiện tất cả CBNV thuộc cơ sở đó
- [ ] Kết hợp được với filter khác

**Dependencies:** Backend field `workplace_name`, FR-001 (share component)

---

#### FR-008: Filter Tệp bên ngoài trên tab Creator

**Priority:** Must Have

**Description:**
Option filter để lọc creator không phải CBNV (bên ngoài). Có thể là toggle/dropdown: Tất cả / CBNV / Bên ngoài.

**Acceptance Criteria:**
- [ ] Dropdown 3 options: Tất cả, CBNV, Bên ngoài
- [ ] Chọn CBNV → chỉ hiện creator có `account_type = staff`
- [ ] Chọn Bên ngoài → chỉ hiện creator có `account_type = creator`

**Dependencies:** Backend field `account_type`

---

#### FR-009: Cột Hashtag cá nhân trên tab Creator

**Priority:** Must Have

**Description:**
Thêm cột "Hashtag cá nhân" vào table Creator. (Cột này có thể đã tồn tại — cần verify. Nếu chưa có thì thêm mới.)

**Acceptance Criteria:**
- [ ] Cột hiển thị hashtag cá nhân của creator
- [ ] Hiển thị "—" nếu chưa có

---

#### FR-010: Bỏ cột Ngày tạo trên tab Creator

**Priority:** Should Have

**Description:**
Ẩn cột "Ngày tạo" khỏi table Creator. Giữ lại cột "Ngày tham gia".

**Acceptance Criteria:**
- [ ] Cột Ngày tạo không hiển thị trên table
- [ ] Cột Ngày tham gia vẫn hiển thị
- [ ] Cột Ngày tạo vẫn available trong export (nếu user muốn tick)

---

### EPIC-004: Tab Creator — Export

#### FR-011: Chỉnh export tab Creator

**Priority:** Must Have

**Description:**
- Bỏ tick mặc định: Đối tác VinWonders, Ngày tạo
- Thêm cột: Nơi làm việc, Hashtag cá nhân, Phân loại

**Acceptance Criteria:**
- [ ] 2 cột mặc định unchecked trong column picker
- [ ] 3 cột mới mặc định checked
- [ ] Data xuất đúng

**Dependencies:** FR-012

---

### EPIC-005: Export chung — Column Picker

#### FR-012: Column Picker Dialog

**Priority:** Must Have

**Description:**
Khi bấm "Xuất dữ liệu" trên bất kỳ tab nào → hiện dialog checkbox list cho user chọn cột muốn xuất. Mỗi tab có danh sách cột và default preset riêng. Giải quyết triệt để vấn đề: không cần dev mỗi lần team vận hành muốn bỏ/thêm cột.

**Acceptance Criteria:**
- [ ] Dialog hiển thị danh sách checkbox, mỗi checkbox = 1 cột
- [ ] Default preset: tick cột hữu ích, bỏ tick cột thừa (theo FR-005, FR-011)
- [ ] Nút "Chọn tất cả" — tick hết
- [ ] Nút "Mặc định" — reset về default preset
- [ ] Bấm "Xuất" → tạo export với chỉ các cột đã chọn
- [ ] Cột mới (CBNV, Cơ sở, Hashtag) đánh dấu badge "MỚI"

**UX Flow:**
```
Bấm "Xuất dữ liệu"
  → Dialog hiện danh sách cột (checkbox, default theo preset)
  → User bỏ tick cột không cần / tick thêm cột cần
  → Bấm "Xuất" → file chỉ chứa cột đã chọn
```

**Dependencies:** Backend API hỗ trợ param `columns[]` trong export request

---

### EPIC-006: Màn hình Thống kê (Analytics)

#### FR-013: Filter CBNV trên Analytics

**Priority:** Must Have

**Description:**
Thêm filter phân loại CBNV trên màn hình Thống kê. Hiện tại chỉ filter được theo sự kiện.

**Acceptance Criteria:**
- [ ] Dropdown: Tất cả / CBNV / Bên ngoài
- [ ] Chọn → tất cả KPIs, charts cập nhật theo filter
- [ ] Kết hợp được với filter Sự kiện hiện có

**Dependencies:** Backend API analytics hỗ trợ query param `account_type`

---

#### FR-014: Filter Cơ sở làm việc trên Analytics

**Priority:** Must Have

**Description:**
Thêm filter Cơ sở làm việc trên màn hình Thống kê. Grouped dropdown giống FR-001.

**Acceptance Criteria:**
- [ ] Grouped dropdown (6 nhóm, ~57 cơ sở)
- [ ] Chọn → KPIs, charts filter theo cơ sở
- [ ] Disable/ẩn khi Phân loại = "Bên ngoài"

**Dependencies:** Backend API analytics hỗ trợ query param `workplace_name`, FR-013

---

#### FR-015: Tích hợp với dashboard mới

**Priority:** Should Have

**Description:**
Dashboard mới (đã demo, sử dụng được ~80% use case) cần update để include trường CBNV + Cơ sở làm việc trong các widget thống kê.

**Acceptance Criteria:**
- [ ] Dashboard mới hiển thị data có phân loại CBNV
- [ ] Filter CBNV/Cơ sở hoạt động trên dashboard mới
- [ ] Các widget KPI phản ứng theo filter

**Dependencies:** FR-013, FR-014, Dashboard mới deployment

---

---

## 5. Non-Functional Requirements

### NFR-001: Performance — Filter Response

**Priority:** Must Have

**Description:** Filter Cơ sở làm việc và Phân loại CBNV phải response nhanh trên dataset lớn (~57 cơ sở, hàng nghìn creator).

**Acceptance Criteria:**
- [ ] Filter response < 500ms
- [ ] Dropdown render < 200ms (57 items grouped)
- [ ] Table re-render sau filter < 1s

---

### NFR-002: Performance — Export

**Priority:** Must Have

**Description:** Export với column selection không được chậm hơn đáng kể so với export hiện tại.

**Acceptance Criteria:**
- [ ] Export time không tăng > 10% so với export cũ
- [ ] File size giảm tỷ lệ thuận với số cột bỏ bớt

---

### NFR-003: Compatibility — Backward

**Priority:** Must Have

**Description:** Upgrade không ảnh hưởng các team khác đang dùng dashboard và export. Cơ chế chọn cột = mỗi user tự quyết.

**Acceptance Criteria:**
- [ ] Export default vẫn chứa tất cả cột (tick hết = behavior cũ)
- [ ] Không có breaking change trên API response hiện tại
- [ ] Thêm fields mới vào response, không xóa fields cũ

---

### NFR-004: Usability — Filter UX

**Priority:** Should Have

**Description:** Filter mới phải nhất quán giữa 3 tab (Nội dung, Creator, Analytics). Cùng component, cùng behavior.

**Acceptance Criteria:**
- [ ] Filter Cơ sở dùng chung component grouped dropdown trên cả 3 tab
- [ ] Filter Phân loại dùng chung component dropdown 3 options trên cả 3 tab
- [ ] Behavior cascade nhất quán

---

### NFR-005: Data Integrity

**Priority:** Must Have

**Description:** Phân loại CBNV/Bên ngoài phải chính xác, dựa trên `account_type` từ backend.

**Acceptance Criteria:**
- [ ] Không có trường hợp creator hiển thị sai phân loại
- [ ] Creator chưa có `account_type` mặc định hiển thị "Bên ngoài"
- [ ] Cơ sở làm việc = `null` hiển thị "—" (không crash)

---

---

## 6. Epics & Traceability

| Epic ID | Epic Name | FRs | Story Estimate | Priority |
|---------|-----------|-----|----------------|----------|
| EPIC-001 | Tab Nội dung — Filter & Cột mới | FR-001, FR-002, FR-003, FR-004 | 3-4 stories | Must Have |
| EPIC-002 | Tab Nội dung — Export | FR-005, FR-006 | 1-2 stories | Must Have |
| EPIC-003 | Tab Creator — Filter & Cột | FR-007, FR-008, FR-009, FR-010 | 3-4 stories | Must Have |
| EPIC-004 | Tab Creator — Export | FR-011 | 1 story | Must Have |
| EPIC-005 | Export chung — Column Picker | FR-012 | 2-3 stories | Must Have |
| EPIC-006 | Analytics — Filter CBNV | FR-013, FR-014, FR-015 | 2-3 stories | Must Have |

**Tổng:** 6 epics, 15 FRs, 5 NFRs, ước tính **12-17 stories**

---

## 7. Prioritization Summary

| Priority | FRs | NFRs |
|----------|-----|------|
| **Must Have** | 13 | 4 |
| **Should Have** | 2 | 1 |
| **Total** | 15 | 5 |

---

## 8. Data Model Requirements

### Cột mới cần backend hỗ trợ

| Field | Nơi hiển thị | Nguồn data | Ghi chú |
|-------|-------------|------------|---------|
| `account_type` | Tab Nội dung + Creator + Analytics + Export | `user.account_type` | `staff` = CBNV, `creator` = Bên ngoài |
| `workplace_name` | Tab Nội dung + Creator + Analytics + Export | `user.workplace_name` | Tên cơ sở (VinWonders Phú Quốc, ...) |
| `personal_hashtag` | Tab Nội dung + Creator + Export | `user.personal_hashtag` | Đã có ở tab Creator, cần join vào content response |

### Filter mới → API query params

| Filter | Tabs | API param |
|--------|------|-----------|
| Cơ sở làm việc | Nội dung, Creator, Analytics | `workplace_name={value}` |
| Phân loại CBNV | Creator, Analytics | `account_type={staff\|creator}` |

### Export API thay đổi

| Thay đổi | Mô tả |
|----------|-------|
| Thêm param `columns[]` | Array of column IDs, backend chỉ export columns được chọn |
| Thêm 3 cột mới vào available columns | `account_type`, `workplace_name`, `personal_hashtag` |

---

## 9. Dependencies

### Internal

| Dependency | Status | Blocking? |
|-----------|--------|-----------|
| Chức năng phân loại CBNV (form đăng ký) | Đang thiết kế | **Yes** — phải có `account_type` + `workplace_name` trong user model trước |
| Backend API: join workplace/hashtag vào content response | Chưa có | **Yes** — cần endpoint hoặc field mới |
| Backend API: analytics endpoint hỗ trợ filter CBNV/cơ sở | Chưa có | **Yes** — cho EPIC-006 |
| Backend API: export endpoint hỗ trợ `columns[]` | Chưa có | **Yes** — cho EPIC-005 |

### External

| Dependency | Status |
|-----------|--------|
| Danh sách cơ sở làm việc (6 nhóm, ~57 cơ sở) | Cần confirm danh sách chính thức |
| Xác nhận scope qua email | Đang chờ |

---

## 10. Assumptions

1. User model đã có (hoặc sẽ có trước go-live) fields `account_type` và `workplace_name`
2. Danh sách cơ sở làm việc tương đối ổn định (~57 items), có thể hardcode hoặc load từ API
3. Export hiện tại trả về tất cả cột → thêm `columns[]` param chỉ filter output, không thay đổi data pipeline
4. Admin dashboard hiện tại (UMI) vẫn duy trì và nhận upgrade, không bị replace ngay bởi VCreator Dashboard v2

---

## 11. Open Questions

| # | Câu hỏi | Impact |
|---|---------|--------|
| 1 | Danh sách chính xác 57 cơ sở + 6 nhóm? Có API hay hardcode? | FR-001, FR-007, FR-014 |
| 2 | Default `account_type` cho creator cũ chưa có phân loại? | FR-002, NFR-005 |
| 3 | Column picker lưu preference (localStorage/server) hay mỗi lần chọn lại? | FR-012 UX |
| 4 | Analytics dashboard mới (demo) deploy khi nào? | FR-015 timeline |
| 5 | Export format: chỉ Excel (.xlsx) hay thêm CSV? | FR-012 scope |

---

## 12. Timeline

| Phase | Thời gian | Nội dung |
|-------|-----------|----------|
| **Phase 1: Backend** | 1-2 ngày | Thêm fields mới vào API response, filter params, export `columns[]` |
| **Phase 2: Tab Nội dung** | 1 ngày | Filter Cơ sở, 3 cột mới, export chỉnh |
| **Phase 3: Tab Creator** | 0.5 ngày | Filter Nơi làm việc + Phân loại, cột Hashtag, bỏ Ngày tạo, export chỉnh |
| **Phase 4: Column Picker** | 1 ngày | Dialog chọn cột chung cho tất cả tab |
| **Phase 5: Analytics** | 1 ngày | Filter CBNV + Cơ sở trên Analytics, tích hợp dashboard mới |
| **Phase 6: Test & Polish** | 0.5 ngày | Cross-tab testing, edge cases, responsive |
| **Tổng** | **~5-6 ngày** | |

**Target:** Đầu tháng 5/2026

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-12 | Product Manager | Initial PRD từ meeting 0410 overview |

---

**This document was created using BMAD Method v6 — Phase 2 (Planning)**

*To continue: Run `/bmad:architecture` to design system architecture.*
