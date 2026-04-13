# PRD: Đăng ký và Phân nhóm Tài khoản — V1

**Project:** Gen-Green Registration & Account Grouping
**Date:** 2026-04-12
**Version:** 1.0
**Status:** Draft
**Demo:** `demo-gen-green` → `/dang-ky-phan-nhom`

---

## 1. Executive Summary

Thu thập đầy đủ thông tin profile cho tất cả creator Gen-Green (họ tên, SĐT, email) và phân loại tài khoản thành 2 nhóm: **CBNV** (cán bộ nhân viên Vin) và **Creator bên ngoài**. CBNV khai thêm nơi làm việc + mã nhân viên, admin verify async.

V1 tập trung vào **user tự khai + admin manual verify**. Chưa có employee registry hay import pipeline (xem V2).

---

## 2. Business Objectives

| # | Objective | Success Metric |
|---|-----------|----------------|
| 1 | Thu thập SĐT + email cho tất cả creator | >80% creator có đầy đủ SĐT + email trong 30 ngày |
| 2 | Phân loại CBNV vs bên ngoài | Admin filter được theo phân loại trên dashboard |
| 3 | Thu thập nơi làm việc cho CBNV | Admin filter được theo cơ sở (57 cơ sở, 6 nhóm) |
| 4 | Không ảnh hưởng conversion đăng ký | Tỷ lệ hoàn tất form > 70% |

---

## 3. User Personas

| Persona | Nhu cầu |
|---------|---------|
| **Creator (existing)** | Popup cập nhật không quá phiền, cho "Để sau" vài lần |
| **Creator (new)** | Đăng ký nhanh bằng social login, bổ sung thông tin sau |
| **CBNV** | Khai nơi làm việc + mã NV dễ dàng, dropdown tìm nhanh |
| **Admin** | Xem phân loại trên table, verify mã NV |

---

## 4. Functional Requirements

### EPIC-001: Popup cập nhật thông tin

#### FR-001: Trigger popup cho user cũ

**Priority:** Must Have

**Description:**
User đã có tài khoản, thiếu SĐT/email/phân loại → hiện popup "Cập nhật thông tin" khi mở app.

**Acceptance Criteria:**
- [ ] Popup hiện nếu `profile_completed_at` = null
- [ ] Delay 3-5 giây sau khi vào app (cho user thấy dashboard trước)
- [ ] Pre-fill data có sẵn (tên, email từ social login)

---

#### FR-002: Trigger popup cho user mới

**Priority:** Must Have

**Description:**
User đăng nhập bằng TikTok/Google lần đầu → tạo account → hiện popup ngay.

**Acceptance Criteria:**
- [ ] Popup hiện ngay sau social login thành công
- [ ] Pre-fill tên + email từ social login data
- [ ] User ignore → `profile_completed_at` vẫn null → lần sau = trigger popup

---

#### FR-003: Progressive urgency

**Priority:** Must Have

**Description:**
Popup cho phép "Để sau" 2 lần. Lần thứ 3 trở đi = mandatory (không có nút đóng).

**Acceptance Criteria:**
- [ ] Lần 1-2: có nút "Để sau" + nút X
- [ ] Lần 2: text "Còn 1 lần bỏ qua"
- [ ] Lần 3+: không có nút đóng, blur content phía sau
- [ ] `dismiss_count` persist qua sessions

---

### EPIC-002: Form profile

#### FR-004: Form bước 1 — Thông tin cơ bản

**Priority:** Must Have

**Description:**
Form thu thập: Họ tên, SĐT, Email (required cho tất cả), Toggle "Tôi là nhân viên".

**Acceptance Criteria:**
- [ ] Họ tên: text, required, pre-fill từ social
- [ ] SĐT: text, required, inline validate format (10 số, bắt đầu 0)
- [ ] Email: text, required, inline validate format, pre-fill từ social
- [ ] Toggle nhân viên: default OFF
- [ ] SĐT trùng user khác → inline error
- [ ] Email trùng user khác → inline error

---

#### FR-005: Form bước 2 — Thông tin nhân viên

**Priority:** Must Have

**Description:**
Khi toggle "Tôi là nhân viên" = ON → hiện 2 field: Nơi làm việc (grouped searchable select) + Mã nhân viên.

**Acceptance Criteria:**
- [ ] Slide animation khi toggle ON/OFF
- [ ] Nơi làm việc: grouped dropdown, 6 nhóm, 57 cơ sở, có search
- [ ] Mã nhân viên: text, required khi toggle ON, min 3 ký tự
- [ ] Toggle OFF → clear employee fields

---

#### FR-006: Grouped searchable select cho cơ sở

**Priority:** Must Have

**Description:**
Component dropdown grouped cho 57 cơ sở. 6 nhóm cha: VinPalace (3), Vinpearl (17), VinWonders (15), Vinpearl Golf (5), Green SM (14), Khác (3). Search/filter text.

**Acceptance Criteria:**
- [ ] 6 nhóm hiển thị đúng với header group
- [ ] Search box filter toàn bộ (tên nhóm + tên cơ sở)
- [ ] Click ngoài → đóng dropdown
- [ ] Hiển thị: "Nhóm · Tên cơ sở" khi đã chọn

---

#### FR-007: Submit + lưu profile

**Priority:** Must Have

**Description:**
Submit form → validate → lưu profile → set `profile_completed_at`.

**Acceptance Criteria:**
- [ ] Validate tất cả required fields trước submit
- [ ] Lưu `account_type` = staff/creator
- [ ] Nếu staff → `staff_status` = "pending"
- [ ] Set `profile_completed_at` = now → popup không hiện nữa
- [ ] Nếu staff → hiển thị badge "Đang xác minh"

---

#### FR-008: Persist partial input

**Priority:** Should Have

**Description:**
User dismiss popup giữa chừng → lưu draft vào localStorage → restore khi popup mở lại.

**Acceptance Criteria:**
- [ ] Save draft on dismiss
- [ ] Restore draft khi popup reopen
- [ ] Clear draft sau submit thành công

---

### EPIC-003: Staff verification

#### FR-009: Admin verify mã nhân viên

**Priority:** Must Have

**Description:**
Admin xem danh sách user có `staff_status = pending`. Verify hoặc reject.

**Acceptance Criteria:**
- [ ] Admin thấy danh sách pending: tên, mã NV, nơi LV
- [ ] Nút Verify → `staff_status = verified`, `staff_verified_at = now`
- [ ] Nút Reject → `staff_status = rejected`
- [ ] Reject có thể kèm lý do (optional)

---

#### FR-010: Notification khi verify/reject

**Priority:** Should Have

**Description:**
User nhận thông báo khi admin verify hoặc reject mã NV.

**Acceptance Criteria:**
- [ ] Verified → "Mã nhân viên đã được xác minh ✓"
- [ ] Rejected → "Mã nhân viên không hợp lệ. Vui lòng kiểm tra lại"
- [ ] In-app notification + badge trên profile

---

#### FR-011: Chỉnh sửa profile sau submit

**Priority:** Should Have

**Description:**
User vào Settings sửa được thông tin. Đổi nơi LV / mã NV → reset `staff_status` → pending.

**Acceptance Criteria:**
- [ ] Settings page hiển thị profile hiện tại
- [ ] Editable: tên, SĐT, email, toggle nhân viên, nơi LV, mã NV
- [ ] Đổi nơi LV hoặc mã NV → reset staff_status = pending
- [ ] Đổi SĐT/email → check unique trước save

---

## 5. Non-Functional Requirements

### NFR-001: Performance — Popup load

**Priority:** Must Have

Popup render < 200ms. Grouped dropdown mở < 100ms (57 items, no API call — static data).

### NFR-002: Mobile UX

**Priority:** Must Have

Popup = full-screen bottom sheet trên mobile. Grouped dropdown scrollable. Keyboard không che input fields.

### NFR-003: Data validation

**Priority:** Must Have

SĐT: regex `^0\d{9}$`. Email: basic format check. Mã NV: min 3 ký tự. Tất cả validate inline on blur.

### NFR-004: Unique constraint

**Priority:** Must Have

SĐT + email phải unique trên toàn hệ thống. Check realtime khi user blur field (debounce 500ms).

---

## 6. Data Model

| Field | Type | Description |
|-------|------|-------------|
| `profile_completed_at` | datetime, nullable | Null = popup hiện |
| `dismiss_count` | int, default 0 | Số lần dismiss |
| `account_type` | `creator` \| `staff` | Phân nhóm |
| `workplace_group` | string, nullable | Nhóm cơ sở |
| `workplace_name` | string, nullable | Tên cơ sở |
| `employee_code` | string, nullable | Mã nhân viên |
| `staff_status` | `pending` \| `verified` \| `rejected`, nullable | Trạng thái xác minh |
| `staff_verified_at` | datetime, nullable | Thời điểm verify |

---

## 7. Epics & Traceability

| Epic | FRs | Stories (est.) | Priority |
|------|-----|----------------|----------|
| EPIC-001: Popup trigger | FR-001 → FR-003 | 3-4 | Must Have |
| EPIC-002: Form profile | FR-004 → FR-008 | 5-6 | Must Have |
| EPIC-003: Staff verification | FR-009 → FR-011 | 3-4 | Must Have |

**Tổng:** 3 epics · 11 FRs · 4 NFRs · 11-14 stories

---

## 8. Prioritization

| Priority | FRs | NFRs |
|----------|-----|------|
| Must Have | 8 | 4 |
| Should Have | 3 | 0 |

---

## 9. Out of Scope (V1)

- Employee registry (danh sách nhân viên chính thức từ HR)
- Import pipeline (upload Excel nhân viên)
- Auto-match / auto-verify từ registry
- Luồng điều chuyển công tác / nghỉ việc tự động
- Form đăng ký truyền thống (thay đổi auth flow)
- Multi-select nơi làm việc

→ Xem [PRD V2](prd-registration-v2-2026-04-12.md) cho các features trên.

---

## 10. Timeline

| Phase | Thời gian | Nội dung |
|-------|-----------|----------|
| Phase 1 | 3 ngày | Popup + Form (2 bước) + Grouped select |
| Phase 2 | 2 ngày | Staff verification admin + Notification + Settings edit |
| **Tổng** | **~5 ngày** | |
