# PRD: Đăng ký và Phân nhóm Tài khoản — V2 (Employee Registry & Import)

**Project:** Gen-Green Registration & Account Grouping
**Date:** 2026-04-12
**Version:** 2.0
**Status:** Draft
**Prerequisite:** [PRD V1](prd-registration-v1-2026-04-12.md) đã go-live

---

## 1. Executive Summary

Xây dựng **Employee Registry** — danh sách nhân viên chính thức từ HR — và **Import Pipeline** để quản lý vòng đời nhân viên trên Gen-Green: import trước/sau đăng ký, điều chuyển công tác, nghỉ việc. Thay thế quy trình manual verify bằng auto-match từ registry.

V2 xây trên nền V1 (user đã tự khai mã NV, admin đã verify manual). V2 bổ sung nguồn sự thật từ HR để auto-verify và quản lý lifecycle.

---

## 2. Business Objectives

| # | Objective | Success Metric |
|---|-----------|----------------|
| 1 | Giảm thời gian verify mã NV từ manual → auto | >90% user auto-verified khi có registry |
| 2 | Phát hiện khai mã NV sai (mã người khác) | 100% identity mismatch được flag |
| 3 | Cập nhật tự động khi điều chuyển/nghỉ việc | Thời gian update < 24h sau HR import |
| 4 | Giảm tải admin | Admin chỉ xử lý conflict, không verify từng người |

---

## 3. User Personas

| Persona | Nhu cầu |
|---------|---------|
| **HR Vin** | Upload danh sách nhân viên định kỳ, không cần kỹ thuật phức tạp |
| **Admin AT** | Upload file từ HR, review conflict, xem import history |
| **CBNV (creator)** | Nhận thông báo khi status thay đổi (verify/điều chuyển/nghỉ) |

---

## 4. Functional Requirements

### EPIC-001: Employee Registry

#### FR-001: Bảng Employee Registry

**Priority:** Must Have

**Description:**
Tạo bảng `employee_registry` riêng biệt với user model. Lưu danh sách nhân viên chính thức từ HR. Đây là nguồn sự thật về "ai là nhân viên".

**Acceptance Criteria:**
- [ ] Bảng chứa: employee_code (unique), full_name, cccd, phone, email, workplace_group, workplace_name, department, status, gen_green_user_id (nếu đã match)
- [ ] employee_code là khóa chính, unique
- [ ] Trùng employee_code khi import → update record (không tạo mới)
- [ ] Tách biệt hoàn toàn với user model

---

#### FR-002: Admin xem danh sách registry

**Priority:** Must Have

**Description:**
Admin xem danh sách nhân viên trong registry. Filter theo cơ sở, trạng thái, matched/unmatched.

**Acceptance Criteria:**
- [ ] Table: mã NV, họ tên, cơ sở, phòng ban, status, matched Gen-Green user
- [ ] Filter: cơ sở, status (active/terminated), matched/unmatched
- [ ] Search: theo mã NV, tên, SĐT
- [ ] Pagination

---

### EPIC-002: Import Pipeline

#### FR-003: Upload file Excel

**Priority:** Must Have

**Description:**
Admin upload file Excel (.xlsx) chứa danh sách nhân viên. Validate format trước khi xử lý.

**Acceptance Criteria:**
- [ ] Accept .xlsx file
- [ ] Validate header: employee_code, full_name, workplace_group, workplace_name, status (required)
- [ ] Validate data: employee_code không rỗng, status hợp lệ
- [ ] Reject file nếu format sai → hiển thị lỗi cụ thể (dòng nào, cột nào)
- [ ] File size limit: 10MB

**Import columns:**

| Cột | Bắt buộc | Mô tả |
|-----|----------|-------|
| employee_code | ✅ | Mã nhân viên (unique) |
| full_name | ✅ | Họ tên |
| cccd | Nên có | CCCD (để match identity) |
| phone | Nên có | SĐT |
| email | Nên có | Email |
| workplace_group | ✅ | Nhóm cơ sở |
| workplace_name | ✅ | Tên cơ sở |
| department | Optional | Phòng ban |
| status | ✅ | active / terminated |

---

#### FR-004: Dry-run mode

**Priority:** Must Have

**Description:**
Sau upload, hiển thị preview kết quả TRƯỚC khi commit. Admin xem rồi quyết định có commit hay không.

**Acceptance Criteria:**
- [ ] Preview hiển thị: N records new, M records updated, K matched users, J conflicts, L terminated
- [ ] Danh sách conflict (identity mismatch) hiển thị chi tiết
- [ ] Nút "Commit" để thực hiện
- [ ] Nút "Hủy" để bỏ qua
- [ ] Dry-run KHÔNG thay đổi data

---

#### FR-005: Async processing cho file lớn

**Priority:** Must Have

**Description:**
File >1000 records → xử lý background job. Email kết quả khi xong.

**Acceptance Criteria:**
- [ ] File ≤1000 records → xử lý sync, hiển thị kết quả ngay
- [ ] File >1000 records → queue background → email summary khi hoàn tất
- [ ] Chỉ 1 import chạy tại 1 thời điểm (queue)
- [ ] Progress indicator cho file đang xử lý

---

#### FR-006: Rollback import

**Priority:** Should Have

**Description:**
Mỗi import có import_id. Admin có thể rollback toàn bộ changes thuộc 1 import.

**Acceptance Criteria:**
- [ ] Import history table: import_id, file_name, uploaded_by, timestamp, records count, status
- [ ] Nút "Rollback" trên mỗi import record
- [ ] Rollback revert tất cả changes (registry + user updates) thuộc import_id
- [ ] Confirm dialog trước rollback

---

### EPIC-003: Auto-match & Verify

#### FR-007: Auto-match khi user đăng ký (registry có trước)

**Priority:** Must Have

**Description:**
Khi user đăng ký + khai mã NV → lookup employee_registry. Nếu match + identity OK → auto-verify.

**Acceptance Criteria:**
- [ ] Lookup `employee_registry` WHERE employee_code = mã NV user khai
- [ ] Found + identity match (≥1 trong CCCD/SĐT/email) → `staff_status = verified` tự động
- [ ] Found + identity mismatch → `staff_status = pending` + flag admin
- [ ] Not found → `staff_status = pending` (mã không trong registry, admin verify manual)

---

#### FR-008: Batch match khi import sau đăng ký

**Priority:** Must Have

**Description:**
Sau import registry → chạy batch match: tất cả user có `staff_status = pending` vs registry.

**Acceptance Criteria:**
- [ ] FOR EACH user WHERE staff_status = pending AND employee_code IS NOT NULL
- [ ] Lookup registry → match + identity OK → auto-verify
- [ ] Match + identity mismatch → flag admin
- [ ] No match → giữ pending
- [ ] Summary: N auto-verified, M flagged, K unchanged
- [ ] Email summary cho admin

---

#### FR-009: Match logic chi tiết

**Priority:** Must Have

**Description:**
Match = employee_code exact + ít nhất 1 identity field. Nếu mã NV đúng nhưng identity sai → flag.

**Acceptance Criteria:**
- [ ] Step 1: employee_code exact match (bắt buộc)
- [ ] Step 2: cross-check ít nhất 1 trong: CCCD, SĐT (normalized +84), email (lowercase)
- [ ] Cả employee_code + identity match → auto-verify
- [ ] employee_code match + identity mismatch → flag admin: "Mã NV đúng nhưng thông tin không khớp"
- [ ] Chuẩn hóa trước compare: SĐT → +84, email → lowercase

---

### EPIC-004: Lifecycle Management

#### FR-010: Import điều chuyển công tác

**Priority:** Must Have

**Description:**
HR upload delta file nhân viên thay đổi cơ sở/phòng ban → update registry + user profile.

**Acceptance Criteria:**
- [ ] Parse: employee_code, new_workplace_group, new_workplace_name, new_department
- [ ] Update employee_registry
- [ ] Tìm Gen-Green user đã link → update workplace_group, workplace_name
- [ ] KHÔNG reset staff_status (vẫn verified)
- [ ] Ghi log: "Điều chuyển từ X sang Y"

---

#### FR-011: Import nghỉ việc

**Priority:** Must Have

**Description:**
HR upload nhân viên nghỉ → update registry status = terminated → gỡ staff tag trên Gen-Green.

**Acceptance Criteria:**
- [ ] Update employee_registry: status = "terminated"
- [ ] Tìm Gen-Green user đã link:
  - account_type → "creator"
  - staff_status → null
  - workplace → null
- [ ] Ghi log: "Nghỉ việc, gỡ staff tag"

---

#### FR-012: Grace period nghỉ việc

**Priority:** Should Have

**Description:**
Khi nhân viên nghỉ, không gỡ staff tag ngay. Grace period 7 ngày — notify trước, gỡ sau.

**Acceptance Criteria:**
- [ ] Notify user ngay: "Tài khoản sẽ chuyển về Creator từ ngày X" (7 ngày sau)
- [ ] Sau 7 ngày → tự động gỡ staff tag
- [ ] Trong 7 ngày vẫn giữ quyền staff
- [ ] Admin có thể override (gỡ ngay hoặc cancel)

---

#### FR-013: Notification khi status thay đổi

**Priority:** Must Have

**Description:**
User nhận thông báo khi status thay đổi do import: auto-verified, điều chuyển, sắp nghỉ.

**Acceptance Criteria:**
- [ ] Auto-verified: "Mã nhân viên đã được xác minh tự động ✓"
- [ ] Điều chuyển: "Nơi làm việc đã cập nhật: [Cơ sở mới]"
- [ ] Sắp nghỉ: "Tài khoản sẽ chuyển về Creator từ ngày [X]"
- [ ] Đã nghỉ: "Tài khoản đã chuyển về dạng Creator"
- [ ] In-app notification

---

### EPIC-005: Audit & History

#### FR-014: Import history

**Priority:** Must Have

**Description:**
Admin xem lịch sử tất cả import: file name, người upload, thời gian, số records, kết quả.

**Acceptance Criteria:**
- [ ] Table: import_id, file_name, uploaded_by, timestamp, total_records, new, updated, matched, conflicts, terminated
- [ ] Click vào → xem chi tiết changes
- [ ] Filter theo thời gian

---

#### FR-015: Audit trail cho changes

**Priority:** Must Have

**Description:**
Ghi log tất cả thay đổi trên user profile do import gây ra.

**Acceptance Criteria:**
- [ ] Mỗi change: user_id, import_id, field, old_value, new_value, action, timestamp
- [ ] Actions: auto_verified, workplace_updated, staff_removed, flagged
- [ ] Admin xem được audit trail theo user hoặc theo import

---

## 5. Non-Functional Requirements

### NFR-001: Performance — Import

**Priority:** Must Have

File 1000 records sync < 30 giây. File 10000 records async < 5 phút. Batch match < 1 phút cho 5000 pending users.

### NFR-002: Reliability — Atomicity

**Priority:** Must Have

Import per-record transactional. Failed records log riêng, successful records commit. Partial failure không ảnh hưởng records đã thành công.

### NFR-003: Security — File upload

**Priority:** Must Have

Validate file type (.xlsx only). Size limit 10MB. Scan content (no macros/scripts). Upload qua authenticated admin endpoint.

### NFR-004: Data integrity — Dedup

**Priority:** Must Have

employee_code unique trong registry. Import file đã xử lý trước đó → detect bằng checksum, warn admin.

---

## 6. Data Model

### employee_registry

| Field | Type | Mô tả |
|-------|------|-------|
| `employee_code` | string, unique | Khóa chính |
| `full_name` | string | Họ tên HR |
| `cccd` | string, nullable | Match identity |
| `phone` | string, nullable | Match identity |
| `email` | string, nullable | Match identity |
| `workplace_group` | string | Nhóm cơ sở |
| `workplace_name` | string | Tên cơ sở |
| `department` | string, nullable | Phòng ban |
| `status` | enum | active / inactive / terminated |
| `gen_green_user_id` | string, nullable | Linked user |
| `imported_at` | datetime | Import gần nhất |
| `import_id` | string | Batch import ID |

### import_history

| Field | Type | Mô tả |
|-------|------|-------|
| `import_id` | string, unique | ID batch |
| `file_name` | string | Tên file upload |
| `file_checksum` | string | Detect duplicate file |
| `uploaded_by` | string | Admin ID |
| `timestamp` | datetime | Thời gian import |
| `total_records` | int | Tổng records trong file |
| `new_count` | int | Records mới |
| `updated_count` | int | Records update |
| `matched_count` | int | Users auto-verified |
| `conflict_count` | int | Identity mismatch |
| `terminated_count` | int | Nghỉ việc |
| `status` | enum | completed / processing / failed / rolled_back |

### import_changes

| Field | Type | Mô tả |
|-------|------|-------|
| `import_id` | string | Ref import_history |
| `user_id` | string, nullable | Gen-Green user (nếu có) |
| `employee_code` | string | Mã NV |
| `action` | enum | auto_verified / workplace_updated / staff_removed / flagged / new_record |
| `field` | string, nullable | Field thay đổi |
| `old_value` | string, nullable | Giá trị cũ |
| `new_value` | string, nullable | Giá trị mới |
| `timestamp` | datetime | |

---

## 7. Epics & Traceability

| Epic | FRs | Stories (est.) | Priority |
|------|-----|----------------|----------|
| EPIC-001: Employee Registry | FR-001 → FR-002 | 2-3 | Must Have |
| EPIC-002: Import Pipeline | FR-003 → FR-006 | 4-5 | Must Have |
| EPIC-003: Auto-match & Verify | FR-007 → FR-009 | 3-4 | Must Have |
| EPIC-004: Lifecycle Management | FR-010 → FR-013 | 4-5 | Must Have |
| EPIC-005: Audit & History | FR-014 → FR-015 | 2-3 | Must Have |

**Tổng:** 5 epics · 15 FRs · 4 NFRs · 15-20 stories

---

## 8. Prioritization

| Priority | FRs | NFRs |
|----------|-----|------|
| Must Have | 13 | 4 |
| Should Have | 2 | 0 |

---

## 9. Dependencies

| Dependency | Status |
|-----------|--------|
| V1 go-live (user model có account_type, staff_status, workplace) | Prerequisite |
| HR Vin cung cấp file danh sách nhân viên | Cần coordinate |
| HR Vin confirm format file + frequency gửi | Cần confirm |
| Admin dashboard có trang upload + review | Cần build |

---

## 10. Out of Scope (V2)

- HR Vin tự upload trực tiếp (V2 = admin AT upload hộ)
- API sync tự động từ hệ thống HR Vin
- Multi-select nơi làm việc
- Saved import templates

→ Cân nhắc cho V3 nếu volume import cao.

---

## 11. Timeline

| Phase | Thời gian | Nội dung |
|-------|-----------|----------|
| Phase 1 | 3 ngày | Employee registry + Import pipeline (upload, validate, dry-run) |
| Phase 2 | 3 ngày | Auto-match + Batch match + Lifecycle (điều chuyển, nghỉ việc) |
| Phase 3 | 2 ngày | Notification + Audit trail + Import history |
| **Tổng** | **~8 ngày** | |

**Prerequisite:** V1 go-live trước.
