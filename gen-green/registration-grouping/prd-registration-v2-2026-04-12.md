# PRD: Đăng ký và Phân nhóm Tài khoản — V2 (Employee Registry & Import)

**Project:** Gen-Green Registration & Account Grouping
**Date:** 2026-04-12 (updated 2026-04-21)
**Version:** 2.1
**Status:** Draft
**Prerequisite:** [PRD V1](prd-registration-v1-2026-04-12.md) đã go-live
**Reference file:** [VP_Mẫu danh sách trường CBNV 1.xlsx](VP_Mẫu danh sách trường CBNV 1.xlsx) — file mẫu do đối tác (Vin) cung cấp

---

## 1. Executive Summary

Xây dựng **Employee Registry** — danh sách nhân viên chính thức từ HR — và **Import Pipeline** để quản lý vòng đời nhân viên trên Gen-Green: import trước/sau đăng ký, điều chuyển công tác, nghỉ việc. Thay thế quy trình manual verify bằng auto-match từ registry.

V2 xây trên nền V1 (user đã tự khai mã NV, admin đã verify manual). V2 bổ sung nguồn sự thật từ HR để auto-verify và quản lý lifecycle.

### Thay đổi chính so với bản v2.0 (2026-04-12)

- **Format import được chốt theo file mẫu đối tác cung cấp**: chỉ 5 cột (STT, Họ tên, SĐT, Đơn vị thành viên, Mã nhân viên). Bỏ các cột CCCD, email, department, status vì đối tác không cung cấp trong file mẫu v1.
- **Match logic simplify**: key match = `SĐT + mã nhân viên` (không còn CCCD/email vì file mẫu không có).
- **Auto-verify flow chi tiết hoá 3 kịch bản**: khớp cả 2 → auto-fix phòng ban; lệch → cancel + yêu cầu sửa lại; không tìm thấy → giữ pending.
- **Validation cụ thể theo file mẫu**: STT 5 chữ số, SĐT 10 chữ số, mã NV 8 chữ số, họ tên in hoa chữ cái đầu có dấu.
- **Đơn vị thành viên** dùng validation list (data validation Excel cột J) — reject nếu không nằm trong DS hợp lệ.

---

## 2. Business Objectives

| # | Objective | Success Metric |
|---|-----------|----------------|
| 1 | Giảm thời gian verify mã NV từ manual → auto | >90% user auto-verified khi có registry |
| 2 | Phát hiện khai mã NV sai (mã người khác) | 100% identity mismatch được flag + cancel |
| 3 | Cập nhật tự động khi điều chuyển/nghỉ việc | Thời gian update < 24h sau HR import |
| 4 | Giảm tải admin | Admin chỉ xử lý conflict, không verify từng người |

---

## 3. User Personas

| Persona | Nhu cầu |
|---------|---------|
| **HR Vin** | Export danh sách nhân viên từ HRIS sang Excel theo template sẵn, không cần kỹ thuật |
| **Admin AT** | Upload file từ HR, review conflict, xem import history |
| **CBNV (creator)** | Nhận thông báo khi status thay đổi (auto-verified / cancel / điều chuyển / nghỉ) |

---

## 4. Functional Requirements

### EPIC-001: Employee Registry

#### FR-001: Bảng Employee Registry

**Priority:** Must Have

**Description:**
Tạo bảng `employee_registry` riêng biệt với user model. Lưu danh sách nhân viên chính thức từ HR. Đây là nguồn sự thật về "ai là nhân viên".

**Acceptance Criteria:**
- [ ] Bảng chứa: employee_code (unique), full_name, phone, workplace_name, status, gen_green_user_id (nếu đã match), imported_at, import_id
- [ ] employee_code là khóa chính, unique
- [ ] Trùng employee_code khi import → update record (không tạo mới)
- [ ] Tách biệt hoàn toàn với user model
- [ ] Phone được normalize về dạng chuẩn (84xxxxxxxxx hoặc 0xxxxxxxxx — chọn 1 format, lưu consistently)

---

#### FR-002: Admin xem danh sách registry

**Priority:** Must Have

**Description:**
Admin xem danh sách nhân viên trong registry. Filter theo cơ sở, trạng thái, matched/unmatched.

**Acceptance Criteria:**
- [ ] Table columns: mã NV, họ tên, SĐT, đơn vị, status, matched Gen-Green user
- [ ] Filter: đơn vị, status (active/terminated), matched/unmatched
- [ ] Search: theo mã NV, tên, SĐT
- [ ] Pagination

---

### EPIC-002: Import Pipeline

#### FR-003: Upload file Excel theo template đối tác

**Priority:** Must Have

**Description:**
Admin upload file Excel (.xlsx) chứa danh sách nhân viên theo đúng template đối tác cung cấp. Validate format trước khi xử lý.

**File format tham chiếu:** [VP_Mẫu danh sách trường CBNV 1.xlsx](VP_Mẫu danh sách trường CBNV 1.xlsx)

**Import columns (khớp 100% template đối tác):**

| Cột | Bắt buộc | Validation | Mô tả |
|-----|----------|------------|-------|
| STT | ✅ | 5 chữ số (e.g. `00001`) | Số thứ tự |
| Họ tên | ✅ | In hoa chữ cái đầu, có dấu | Họ tên đầy đủ |
| SĐT | ✅ | Đúng 10 chữ số, không ký tự đặc biệt | Số điện thoại liên hệ |
| Các đơn vị thành viên | ✅ | Phải nằm trong DS đơn vị hợp lệ (cột J của template) | Nơi làm việc |
| Mã nhân viên | ✅ | 8 chữ số | Mã NV nội bộ |

**Acceptance Criteria:**
- [ ] Accept .xlsx file, match template đối tác
- [ ] Detect header row (bỏ qua row đầu rỗng + row `VD` minh hoạ)
- [ ] Validate từng field theo quy tắc trên
- [ ] Reject file nếu format sai → hiển thị lỗi cụ thể (dòng nào, cột nào, lý do)
- [ ] File size limit: 10MB
- [ ] Validate "Đơn vị thành viên" phải khớp với DS master trong hệ thống (tham chiếu `overview.md` mục 5 — VinPalace/Vinpearl/VinWonders/Golf/GreenSM/Khác). Nếu HR thêm đơn vị mới chưa có trong master → warn admin, cho phép auto-thêm vào master list.

---

#### FR-004: Dry-run mode

**Priority:** Must Have

**Description:**
Sau upload, hiển thị preview kết quả TRƯỚC khi commit. Admin xem rồi quyết định có commit hay không.

**Acceptance Criteria:**
- [ ] Preview hiển thị: N records new, M records updated, K users auto-verified, J conflicts (cancel), L terminated
- [ ] Danh sách conflict (phone/employee_code mismatch) hiển thị chi tiết kèm lý do
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

### EPIC-003: Auto-match & Verify (V2.1 — CHI TIẾT HOÁ)

#### FR-007: Match key = SĐT + Mã nhân viên

**Priority:** Must Have

**Description:**
Match logic v2.1 dùng **2 field**: `phone` và `employee_code`. Bỏ CCCD/email vì file mẫu đối tác không cung cấp. Mọi so sánh đều dùng phone đã normalize.

**Acceptance Criteria:**
- [ ] Normalize SĐT trước compare: loại bỏ khoảng trắng, dấu `+`, prefix `84` → dạng `0xxxxxxxxx` 10 số
- [ ] Reject SĐT không đủ 10 số khi import
- [ ] Mã NV so sánh exact (case-sensitive, trim whitespace)

---

#### FR-008: 3 Kịch bản auto-verify khi user đã đăng ký TRƯỚC import

**Priority:** Must Have

**Description:**
Khi HR import registry, hệ thống chạy auto-match cho tất cả user đã đăng ký. Có 3 kịch bản rõ ràng:

##### Kịch bản A: Khớp cả SĐT và mã nhân viên → AUTO-VERIFY

```
Tìm user có phone = registry.phone AND employee_code = registry.employee_code
  → MATCH
  → Nếu staff_status = pending → chuyển sang "verified"
  → Update workplace_name từ registry (auto-fix phòng ban/đơn vị)
  → Nếu user đã verified nhưng workplace khác → auto-update workplace
  → Notify user: "Mã nhân viên đã được xác minh tự động ✓. Đơn vị: [X]"
  → Ghi log: auto_verified + workplace_updated
```

**Acceptance Criteria:**
- [ ] Query: WHERE user.phone = registry.phone (normalized) AND user.employee_code = registry.employee_code
- [ ] Match → staff_status = verified, workplace_name = registry.workplace_name
- [ ] Nếu workplace user khác với registry → vẫn update (registry là nguồn sự thật)
- [ ] Nếu full_name user khác với registry → KHÔNG overwrite (tên là do user tự nhập, có thể khác định dạng) nhưng log warning để admin review
- [ ] Notification in-app

---

##### Kịch bản B: Lệch SĐT HOẶC mã nhân viên → CANCEL + yêu cầu sửa lại

```
User có phone trùng registry nhưng employee_code khác
  HOẶC
User có employee_code trùng registry nhưng phone khác
  → MISMATCH → có thể user khai nhầm/mạo danh
  → Hủy yêu cầu verify (staff_status = rejected)
  → Reset fields: employee_code = null, workplace_name = null, workplace_group = null
  → account_type = creator (tạm thời)
  → Notify user: "Thông tin nhân viên không khớp dữ liệu HR. Vui lòng sửa lại mã nhân viên/SĐT và gửi lại yêu cầu xác minh."
  → Flag cho admin review
  → Ghi log: cancelled_mismatch + reason (phone_mismatch | code_mismatch)
```

**Acceptance Criteria:**
- [ ] Detect 2 loại mismatch: (a) phone khớp nhưng code khác, (b) code khớp nhưng phone khác
- [ ] staff_status → "rejected" (dùng lại enum đã có ở V1)
- [ ] Clear employee_code + workplace để user nhập lại
- [ ] Notification + flag admin
- [ ] Audit log ghi rõ loại mismatch

---

##### Kịch bản C: Không tìm thấy trong registry → GIỮ PENDING

```
User khai mã NV mà registry không có
  → Not found
  → Giữ staff_status = pending (không đổi)
  → KHÔNG notify user (tránh spam — chờ đợt import sau có thể khớp)
  → Admin có thể review manual
```

**Acceptance Criteria:**
- [ ] Không touch user record
- [ ] Log vào import_changes với action = "no_match" để admin xem báo cáo
- [ ] Nếu user giữ pending >30 ngày → admin được nhắc review manual

---

#### FR-009: Auto-match khi user đăng ký MỚI (registry đã có trước)

**Priority:** Must Have

**Description:**
Khi user đăng ký + khai mã NV → lookup `employee_registry`. Áp dụng cùng 3 kịch bản A/B/C như FR-008, chạy realtime trong registration flow.

**Acceptance Criteria:**
- [ ] Tại thời điểm user submit registration form, lookup registry WHERE employee_code = user.employee_code
- [ ] Kịch bản A (khớp cả phone + code) → tạo user với staff_status = verified ngay
- [ ] Kịch bản B (lệch) → reject với inline error: "Thông tin không khớp dữ liệu HR. Vui lòng kiểm tra lại SĐT và mã nhân viên"
- [ ] Kịch bản C (not found) → tạo user với staff_status = pending, thông báo "Đang chờ xác minh"

---

#### FR-010: Batch match endpoint

**Priority:** Must Have

**Description:**
Pipeline gọi batch match cho TẤT CẢ user (đã đăng ký) sau mỗi lần import commit. Xử lý cả 3 kịch bản A/B/C.

**Acceptance Criteria:**
- [ ] Trigger sau khi import commit thành công
- [ ] Scan toàn bộ user có employee_code IS NOT NULL
- [ ] Áp dụng FR-008 (A/B/C) cho mỗi user
- [ ] Summary: N verified, M cancelled (mismatch), K unchanged
- [ ] Email summary cho admin + attach danh sách mismatch

---

### EPIC-004: Lifecycle Management

#### FR-011: Import điều chuyển công tác

**Priority:** Must Have

**Description:**
HR upload file mới (hoặc delta) có nhân viên đã đổi đơn vị → update registry + user profile.

**Acceptance Criteria:**
- [ ] Khi import phát hiện employee_code đã tồn tại + workplace_name khác → đánh dấu là "transferred"
- [ ] Update employee_registry
- [ ] Tìm Gen-Green user đã link → update workplace_name
- [ ] KHÔNG reset staff_status (vẫn verified)
- [ ] Notify user: "Nơi làm việc đã cập nhật: [Đơn vị mới]"
- [ ] Ghi log: workplace_updated với old_value/new_value

---

#### FR-012: Import nghỉ việc (nhân viên biến mất khỏi danh sách)

**Priority:** Must Have

**Description:**
File mẫu đối tác KHÔNG có cột `status`. Nghỉ việc được detect implicit — nhân viên không còn trong file full-dump mới nhất.

**Hai cơ chế:**
1. **Full-dump mode** (V2 default): HR gửi full list mỗi tháng. Employee_code trong registry nhưng không có trong file mới → flag "có thể đã nghỉ", chờ admin confirm trước khi gỡ staff tag.
2. **Explicit terminate mode** (V2.1 optional): Admin đánh dấu manually hoặc đối tác bổ sung cột `status` vào template sau này.

**Acceptance Criteria:**
- [ ] Dry-run phải hiển thị rõ: "N nhân viên trong registry không có trong file này — nghi ngờ nghỉ việc"
- [ ] Admin phải xác nhận trước khi gỡ staff tag (KHÔNG auto-terminate trong v2.1 vì rủi ro file thiếu)
- [ ] Khi admin confirm terminate:
  - employee_registry.status = "terminated"
  - Gen-Green user: account_type = creator, staff_status = null, workplace = null
- [ ] Ghi log: staff_removed với reason = "not_in_latest_import"

---

#### FR-013: Grace period nghỉ việc

**Priority:** Should Have

**Description:**
Khi nhân viên được xác nhận nghỉ, không gỡ staff tag ngay. Grace period 7 ngày — notify trước, gỡ sau.

**Acceptance Criteria:**
- [ ] Notify user ngay: "Tài khoản sẽ chuyển về Creator từ ngày X" (7 ngày sau)
- [ ] Sau 7 ngày → tự động gỡ staff tag (scheduled job)
- [ ] Trong 7 ngày vẫn giữ quyền staff
- [ ] Admin có thể override (gỡ ngay hoặc cancel)

---

#### FR-014: Notification khi status thay đổi

**Priority:** Must Have

**Description:**
User nhận thông báo khi status thay đổi do import: auto-verified, cancel (mismatch), điều chuyển, sắp nghỉ.

**Acceptance Criteria:**
- [ ] Auto-verified: "Mã nhân viên đã được xác minh tự động ✓. Đơn vị: [X]"
- [ ] Cancel — phone mismatch: "SĐT không khớp với mã nhân viên bạn đã khai. Vui lòng cập nhật lại."
- [ ] Cancel — code mismatch: "Mã nhân viên không khớp với SĐT đã đăng ký. Vui lòng cập nhật lại."
- [ ] Điều chuyển: "Nơi làm việc đã cập nhật: [Đơn vị mới]"
- [ ] Sắp nghỉ: "Tài khoản sẽ chuyển về Creator từ ngày [X]"
- [ ] Đã nghỉ: "Tài khoản đã chuyển về dạng Creator"
- [ ] In-app notification (bắt buộc), SMS/email (optional — V3)

---

### EPIC-005: Audit & History

#### FR-015: Import history

**Priority:** Must Have

**Description:**
Admin xem lịch sử tất cả import: file name, người upload, thời gian, số records, kết quả.

**Acceptance Criteria:**
- [ ] Table: import_id, file_name, uploaded_by, timestamp, total_records, new, updated, auto_verified, cancelled_mismatch, terminated
- [ ] Click vào → xem chi tiết changes
- [ ] Filter theo thời gian

---

#### FR-016: Audit trail cho changes

**Priority:** Must Have

**Description:**
Ghi log tất cả thay đổi trên user profile do import gây ra.

**Acceptance Criteria:**
- [ ] Mỗi change: user_id, import_id, field, old_value, new_value, action, reason, timestamp
- [ ] Actions: auto_verified, workplace_updated, cancelled_mismatch, staff_removed, no_match, flagged
- [ ] Reasons cho cancelled_mismatch: phone_mismatch | code_mismatch
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

`employee_code` unique trong registry. Import file đã xử lý trước đó → detect bằng checksum, warn admin.

### NFR-005: Phone normalization consistency

**Priority:** Must Have

Mọi SĐT (cả user register và registry import) phải normalize về cùng 1 format trước khi so sánh. Chuẩn chọn: `0xxxxxxxxx` (10 số, leading 0). Trim whitespace, strip `+84`/`84` prefix.

---

## 6. Data Model

### employee_registry

| Field | Type | Mô tả |
|-------|------|-------|
| `employee_code` | string, unique | Khóa chính, 8 chữ số |
| `full_name` | string | Họ tên HR (in hoa chữ cái đầu, có dấu) |
| `phone` | string | SĐT normalized (0xxxxxxxxx), 10 số |
| `workplace_name` | string | Tên đơn vị (từ DS master) |
| `workplace_group` | string, nullable | Derived từ workplace_name (VinPalace/Vinpearl/VinWonders/Golf/GreenSM/Khác) |
| `status` | enum | `active` / `terminated` — default active, terminated do admin confirm |
| `gen_green_user_id` | string, nullable | Linked user |
| `imported_at` | datetime | Import gần nhất |
| `import_id` | string | Batch import ID |
| `last_seen_import_id` | string | Import ID cuối cùng thấy record này (để detect "mất khỏi list") |

**Note:** Bỏ CCCD, email, department vì file mẫu đối tác v1 không cung cấp. Có thể bổ sung ở V3 nếu đối tác mở rộng template.

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
| `updated_count` | int | Records update (transferred) |
| `auto_verified_count` | int | Users auto-verified (kịch bản A) |
| `cancelled_mismatch_count` | int | Users bị cancel do mismatch (kịch bản B) |
| `no_match_count` | int | Users pending giữ nguyên (kịch bản C) |
| `missing_from_file_count` | int | Records trong registry nhưng không có trong file này (nghi ngờ nghỉ) |
| `terminated_count` | int | Được confirm terminate bởi admin |
| `status` | enum | `completed` / `processing` / `failed` / `rolled_back` |

### import_changes

| Field | Type | Mô tả |
|-------|------|-------|
| `import_id` | string | Ref import_history |
| `user_id` | string, nullable | Gen-Green user (nếu có) |
| `employee_code` | string | Mã NV |
| `action` | enum | `auto_verified` / `workplace_updated` / `cancelled_mismatch` / `staff_removed` / `no_match` / `new_record` / `flagged` |
| `reason` | string, nullable | Lý do chi tiết (vd: `phone_mismatch`, `code_mismatch`, `not_in_latest_import`) |
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
| EPIC-003: Auto-match & Verify | FR-007 → FR-010 | 4-5 | Must Have |
| EPIC-004: Lifecycle Management | FR-011 → FR-014 | 4-5 | Must Have |
| EPIC-005: Audit & History | FR-015 → FR-016 | 2-3 | Must Have |

**Tổng:** 5 epics · 16 FRs · 5 NFRs · 16-21 stories

---

## 8. Prioritization

| Priority | FRs | NFRs |
|----------|-----|------|
| Must Have | 14 | 5 |
| Should Have | 2 | 0 |

---

## 9. Dependencies

| Dependency | Status |
|-----------|--------|
| V1 go-live (user model có account_type, staff_status, workplace) | Prerequisite |
| HR Vin cung cấp file theo template [VP_Mẫu danh sách trường CBNV 1.xlsx](VP_Mẫu danh sách trường CBNV 1.xlsx) | ✅ Đã có file mẫu |
| HR Vin confirm frequency gửi file (monthly/ad-hoc) | Cần confirm |
| DS master "Đơn vị thành viên" đồng bộ giữa app + template Excel | Cần đồng bộ |
| Admin dashboard có trang upload + review | Cần build |

---

## 10. Out of Scope (V2)

- HR Vin tự upload trực tiếp (V2 = admin AT upload hộ)
- API sync tự động từ hệ thống HR Vin
- CCCD/email trong registry (đối tác chưa cung cấp — để V3)
- Explicit `status` column trong import (auto-terminate) — V2 cần admin confirm
- Multi-select nơi làm việc
- Saved import templates

→ Cân nhắc cho V3 nếu volume import cao hoặc đối tác mở rộng template.

---

## 11. Timeline

| Phase | Thời gian | Nội dung |
|-------|-----------|----------|
| Phase 1 | 3 ngày | Employee registry + Import pipeline (upload, validate theo template đối tác, dry-run) |
| Phase 2 | 3 ngày | Auto-match 3 kịch bản (A/B/C) + Batch match + Lifecycle (điều chuyển, nghỉ với admin confirm) |
| Phase 3 | 2 ngày | Notification + Audit trail + Import history |
| **Tổng** | **~8 ngày** | |

**Prerequisite:** V1 go-live trước.

---

## 12. Appendix: Ví dụ validation lỗi

Tham chiếu [file mẫu đối tác](VP_Mẫu danh sách trường CBNV 1.xlsx), các lỗi validation cần hiển thị rõ ràng:

| Lỗi | Ví dụ | Message |
|-----|-------|---------|
| STT sai format | `1` thay vì `00001` | "Dòng 3: STT phải có 5 chữ số (vd: 00001)" |
| SĐT không đủ 10 số | `088680796` | "Dòng 3: SĐT phải đúng 10 chữ số" |
| SĐT có ký tự đặc biệt | `0886-807-963` | "Dòng 3: SĐT không được chứa ký tự đặc biệt" |
| Mã NV sai format | `11111` | "Dòng 3: Mã nhân viên phải có 8 chữ số" |
| Đơn vị không hợp lệ | `Vin Gì Đó` | "Dòng 3: Đơn vị 'Vin Gì Đó' không nằm trong danh sách hợp lệ. Xem cột J của template." |
| Họ tên không in hoa | `lâm thanh bình` | "Dòng 3: Họ tên phải in hoa chữ cái đầu mỗi từ" (warning, không reject) |
| Trùng mã NV trong file | 2 dòng cùng mã `00111111` | "Dòng 5 và 7: Mã nhân viên bị trùng" |
