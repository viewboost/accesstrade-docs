# PRD: Đăng ký & Phân nhóm Tài khoản — V1

**Project:** Gen-Green Registration & Account Grouping
**Date:** 2026-04-12
**Version:** 1.0 (rewrite — greenfield, chưa có implementation)
**Status:** Draft
**Tham chiếu:**
- [Overview v2](overview.md) — nguồn chính
- [Meeting note 0410](../meeting-notes/0410.md)
- [Brainstorm](.bmad/brainstorming-gengreen-registration-grouping-2026-04-12.md)

---

## 1. Executive Summary

Thiết kế luồng **đăng ký + thu thập thông tin + phân nhóm tài khoản** cho Gen-Green (greenfield — chưa có implementation). Hệ thống phải:

1. Thu thập đủ **Họ tên, SĐT, Email** cho 100% creator (required cho mọi người), có xác minh OTP.
2. Phân loại creator thành **CBNV** (cán bộ nhân viên hệ sinh thái Vin) và **Creator bên ngoài**.
3. Cho CBNV khai **nơi làm việc theo cấu trúc 3 layer** (Thương hiệu → Công ty → Cơ sở/Bộ phận) + **mã nhân viên**, admin verify async.
4. Cho admin **filter, hiển thị và export** theo phân nhóm + nơi làm việc trên admin dashboard (Tab Nội dung, Tab Creator, Analytics).

V1 tập trung vào **user tự khai + admin manual verify**. V1 CHƯA có employee registry (danh sách nhân viên từ HR) hay import pipeline — xem [PRD V2](prd-registration-v2-2026-04-12.md).

---

## 2. Business Objectives

| # | Objective | Success Metric |
|---|-----------|----------------|
| 1 | Thu thập đủ SĐT + Email verified cho tất cả creator | > 80% creator có đầy đủ SĐT + Email verified trong 30 ngày |
| 2 | Phân loại CBNV vs Bên ngoài | 100% creator có `account_type` sau 30 ngày; admin filter được |
| 3 | Thu thập nơi làm việc cho CBNV theo 3 layer | Admin filter được theo Thương hiệu / Công ty / Cơ sở |
| 4 | Không ảnh hưởng conversion đăng ký | Tỷ lệ hoàn tất form > 70% |
| 5 | Admin vận hành trả lời nhanh câu hỏi phân khúc | Thời gian tạo report "bao nhiêu CBNV cơ sở X tham gia chương trình Y" < 1 phút (thay cho ~30 phút export + Excel) |

---

## 3. User Personas

| Persona | Mô tả | Nhu cầu chính |
|---------|-------|---------------|
| **Creator (mới)** | Vừa cài app, đăng nhập lần đầu bằng social | Đăng ký nhanh, bổ sung thông tin ở bước sau |
| **Creator (cũ)** | Đã có tài khoản trước phase này, thiếu SĐT/Email | Popup cập nhật không quá phiền, "Để sau" vài lần |
| **CBNV** | Nhân viên Vin, tham gia làm creator | Khai nơi làm việc + mã NV dễ dàng, dropdown tìm nhanh theo 3 layer |
| **Admin AT** | Operator Gen-Green | Filter, hiển thị, export theo CBNV/cơ sở trên dashboard |

---

## 4. Scope

### 4.1. In Scope (V1)

**Registration & Profile (End-user)**
- Popup "Cập nhật thông tin" cho user cũ (progressive urgency)
- Popup ngay sau social login cho user mới
- Form 2 bước: thông tin cơ bản + thông tin nhân viên
- Verify SĐT qua OTP SMS
- Verify Email qua OTP email (Google login → auto-verified)
- **Searchable select nơi làm việc 3 layer**: Thương hiệu → Công ty → Cơ sở/Bộ phận (conditional theo config brand)
- Persist draft khi dismiss
- Settings — chỉnh sửa profile (SĐT/Email verified → read-only)

**Staff Verification (Admin)**
- Danh sách user pending → verify / reject
- Notification khi verify / reject

**Admin Dashboard — Filter & Hiển thị phân nhóm** *(gộp từ `admin-dashboard-upgrade`)*
- Tab Nội dung: filter cơ sở làm việc (3 layer), cột Phân loại, Cơ sở, Hashtag cá nhân
- Tab Creator: filter Nơi làm việc (3 layer), filter Phân loại (CBNV/Bên ngoài), cột Hashtag cá nhân, ẩn Ngày tạo
- Analytics: filter Phân loại CBNV + Cơ sở làm việc
- Export: column picker dialog + default preset (bỏ tick cột thừa, tick các cột mới)

**Cấu hình nơi làm việc (data)**
- Layer 1 (Thương hiệu): 20 items, có flag `hasLayer2` / `hasLayer3`
- Layer 2 (Công ty): chỉ Vinpearl cấu hình, brand khác mặc định `other`
- Layer 3 (Cơ sở/Bộ phận): Vinpearl (qua Layer 2) + Green SM (trực tiếp), brand khác bổ sung sau

### 4.2. Out of Scope (V1)

| Feature | Ghi chú |
|---------|---------|
| Employee Registry (danh sách NV chính thức từ HR) | V2 |
| Import Excel danh sách NV từ HR | V2 |
| Auto-match / auto-verify từ registry | V2 |
| Luồng điều chuyển công tác tự động | V2 |
| Luồng nghỉ việc tự động | V2 |
| Form đăng ký truyền thống (thay đổi auth flow) | V2+ |
| Multi-select nơi làm việc (kiêm nhiệm) | V2+ |
| Saved export presets / drag-drop sắp xếp cột | V2+ |
| VCreator Dashboard v2 (Next.js 16 clone TCB) | PRD riêng |
| Affiliate dashboard (Scalef data) | Scope riêng |

---

## 5. Key User Flows

### 5.1. User cũ — Popup cập nhật thông tin

```
User mở app → đã đăng nhập → profile thiếu SĐT/Email/phân loại?
  → Delay 3-5s (cho user thấy dashboard trước)
  → Popup "Cập nhật thông tin"
  → User điền: Họ tên, SĐT (OTP), Email (OTP/auto), toggle nhân viên
  → Nếu nhân viên: chọn Thương hiệu → Công ty (nếu có) → Cơ sở/Bộ phận (nếu có) + Mã NV
  → Submit → Done
```

**Progressive urgency:**
- Lần 1-2: có nút "Để sau" (dismissible), lưu draft localStorage
- Lần 3+: mandatory — ẩn nút đóng, blur background, buộc điền

### 5.2. User mới — Social login + popup ngay

```
User mở app → chưa có tài khoản → Login TikTok/Google
  → Social login OK → Tạo account (pre-fill tên, email từ social)
  → Popup "Cập nhật thông tin" ngay
  → User điền (SĐT OTP, email auto-verified nếu Google, toggle nhân viên, 3 layer, mã NV)
  → Submit → Done
  → User ignore (Để sau) → lần sau vào = Luồng 1
```

### 5.3. Staff verification (Admin)

```
User submit (isStaff=true) → staff_status = "pending"
  → Badge "Đang xác minh" trên profile user
Admin mở danh sách pending
  → Verify → staff_status = "verified", gửi thông báo "✓ Đã xác minh"
  → Reject (kèm lý do) → staff_status = "rejected", gửi thông báo "Mã NV không hợp lệ"
```

### 5.4. Admin vận hành — Filter theo cơ sở

```
Admin mở Tab Nội dung / Tab Creator / Analytics
  → Chọn filter Thương hiệu (VD: Vinpearl)
  → Nếu brand có Layer 2 → hiện dropdown Công ty
  → Nếu brand có Layer 3 → hiện dropdown Cơ sở/Bộ phận
  → Kết hợp filter Phân loại (CBNV/Bên ngoài) / Sự kiện / các filter khác
  → Table / KPI / chart cập nhật realtime
```

---

## 6. Functional Requirements

> **Phạm vi:** 4 epic đầu (EPIC-001 → EPIC-004) là **End-user registration**. 3 epic sau (EPIC-005 → EPIC-007) là **Admin dashboard** (gộp từ `admin-dashboard-upgrade`).

---

### EPIC-001: Popup cập nhật thông tin

#### FR-001: Trigger popup cho user cũ

**Priority:** Must Have

**Description:**
User đã có tài khoản, thiếu SĐT/Email/phân loại → hiện popup "Cập nhật thông tin" khi mở app.

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
- [ ] User ignore → `profile_completed_at` vẫn null → lần sau = trigger như FR-001

---

#### FR-003: Progressive urgency

**Priority:** Must Have

**Description:**
Popup cho phép "Để sau" 2 lần. Lần thứ 3 trở đi = mandatory (không có nút đóng).

**Acceptance Criteria:**
- [ ] Lần 1: nút "Để sau" + nút X
- [ ] Lần 2: nút "Để sau" + text "Còn 1 lần bỏ qua"
- [ ] Lần 3+: không có nút đóng, blur content phía sau
- [ ] `dismiss_count` persist qua sessions

---

### EPIC-002: Form Profile — Thông tin cơ bản + OTP verify

#### FR-004: Form Bước 1 — Thông tin cơ bản

**Priority:** Must Have

**Description:**
Thu thập: Họ tên, SĐT, Email, Toggle "Tôi là nhân viên" (required cho tất cả).

**Acceptance Criteria:**
- [ ] Họ tên: text, required, pre-fill từ social
- [ ] SĐT: text, required, inline validate format (10 số, bắt đầu 0)
- [ ] Email: text, required, inline validate format, pre-fill từ social
- [ ] Toggle nhân viên: default OFF
- [ ] SĐT trùng user khác → inline error "SĐT đã được sử dụng" (check độc lập, debounce 500ms)
- [ ] Email trùng user khác → inline error tương tự
- [ ] SĐT phải verified trước submit (FR-006)
- [ ] Email phải verified trước submit (FR-007)

---

#### FR-005: Google login — Email auto-verify

**Priority:** Must Have

**Description:**
User login bằng Google → email được đánh dấu verified ngay tại thời điểm login, không cần OTP.

**Acceptance Criteria:**
- [ ] New user login Google → tạo user với `email_verified = true`
- [ ] Existing user login Google mà `email_verified = false` → set `email_verified = true`
- [ ] Nếu user sửa email trong form khác email Google → reset verified → cần OTP lại

---

#### FR-006: Verify SĐT qua OTP SMS

**Priority:** Must Have

**Description:**
User nhập SĐT → nhấn "Gửi mã" → nhận OTP qua SMS → nhập OTP → SĐT verified.

**Acceptance Criteria:**
- [ ] Nút "Gửi mã" bên cạnh field SĐT, active khi format hợp lệ + chưa verified
- [ ] Gửi OTP 6 số qua SMS
- [ ] Hiện input OTP + countdown 60s
- [ ] OTP hợp lệ → badge ✓ xanh + field read-only
- [ ] OTP sai → inline error "Mã OTP không đúng"
- [ ] OTP expire sau 5 phút
- [ ] Cooldown 60s giữa các lần gửi — hiện "Gửi lại sau Xs"
- [ ] User sửa SĐT khi đã verified → reset verify state

---

#### FR-007: Verify Email qua OTP

**Priority:** Must Have

**Description:**
User nhập email → nhấn "Gửi mã" → nhận OTP email → nhập OTP → email verified. Nếu email = email Google login → auto-verified (FR-005).

**Acceptance Criteria:**
- [ ] Email = email Google login → tự động verified, không cần OTP, field read-only
- [ ] Email khác → nút "Gửi mã" + flow giống FR-006
- [ ] OTP hợp lệ → badge ✓ + read-only
- [ ] User sửa email khi đã verified → reset verify state

---

#### FR-008: Persist draft khi dismiss

**Priority:** Should Have

**Description:**
User dismiss popup giữa chừng → lưu draft vào localStorage → restore khi popup mở lại.

**Acceptance Criteria:**
- [ ] Save draft on dismiss (tên, SĐT, email, toggle, 3 layer đã chọn)
- [ ] KHÔNG save OTP / verify state (security)
- [ ] Restore draft khi popup reopen
- [ ] Clear draft sau submit thành công

---

### EPIC-003: Form Profile — Nhân viên (3 Layer)

#### FR-009: Form Bước 2 — Toggle nhân viên

**Priority:** Must Have

**Description:**
Khi toggle "Tôi là nhân viên" = ON → hiện các field nhân viên theo cấu trúc 3 layer + Mã nhân viên.

**Acceptance Criteria:**
- [ ] Slide animation khi toggle ON/OFF
- [ ] Toggle OFF → clear hết employee fields (brand, company, unit, employee_code)
- [ ] Toggle ON → require: Thương hiệu, Mã nhân viên
- [ ] Toggle ON → conditionally require Công ty / Cơ sở theo config của brand

---

#### FR-010: Layer 1 — Chọn Thương hiệu

**Priority:** Must Have

**Description:**
Dropdown searchable hiển thị 20 thương hiệu (Vinpearl, Green SM, Vinhomes, Vincom, VinUni, Vinschool, VinFuture, Vinmec, VinFast, Green Future, V-Green, Quỹ Thiện Tâm, Quỹ Vì Tương Lai Xanh, VinEnergo, VinDynamics, VinSmart Future, VinCSS, VinMotion, VinRobotics, Vinspeed) + option **"Khác"** cho trường hợp thương hiệu không có trong list.

**Acceptance Criteria:**
- [ ] Dropdown luôn hiển thị khi toggle nhân viên ON
- [ ] Searchable theo tên brand
- [ ] Data load từ config/API (không hardcode frontend — dễ mở rộng)
- [ ] Mỗi brand có flag `hasLayer2` và `hasLayer3` (boolean)
- [ ] Chọn brand → trigger render Layer 2 / Layer 3 dropdown theo flag
- [ ] Đổi brand → reset Layer 2 + Layer 3 đã chọn
- [ ] **Option "Khác"** là 1 record bình thường trong bảng `WorkplaceBrand` (code `other_brand` hoặc tương tự), admin CRUD như brand khác — không phải giá trị đặc biệt hardcode trong code

---

#### FR-011: Layer 2 — Chọn Công ty (conditional)

**Priority:** Must Have

**Description:**
Chỉ hiển thị khi Layer 1 có `hasLayer2 = true`. V1 chỉ **Vinpearl** có Layer 2 với 5 option: VinPalace, Vinpearl, VinWonders, Vinpearl Golf, **Khác**.

**Acceptance Criteria:**
- [ ] Ẩn dropdown Layer 2 khi brand có `hasLayer2 = false` → auto gán `workplace_company = "other"` (giá trị sentinel nghĩa là "brand không có Layer 2", khác với user chọn option "Khác" trong danh sách)
- [ ] Hiển thị khi `hasLayer2 = true` → required, searchable
- [ ] Data Layer 2 phụ thuộc brand (chỉ Vinpearl có 5 option trên)
- [ ] **Option "Khác"** là 1 record bình thường trong `WorkplaceCompany` (vd `vinpearl_other`), admin CRUD như company khác
- [ ] Đổi Layer 2 → reset Layer 3 đã chọn

---

#### FR-012: Layer 3 — Chọn Cơ sở / Bộ phận (conditional)

**Priority:** Must Have

**Description:**
Chỉ hiển thị khi Layer 1 có `hasLayer3 = true`. V1:
- **Vinpearl** (qua Layer 2): VinPalace (3 + Khác), Vinpearl (19 + Khác), VinWonders (15 + Khác), Vinpearl Golf (5 + Khác), Khác (3)
- **Green SM** (trực tiếp, không qua Layer 2): 14 bộ phận + Khác
- **Brand khác**: `hasLayer3 = false` → không hiển thị, auto gán `workplace_unit = "other"`

**Acceptance Criteria:**
- [ ] Ẩn dropdown Layer 3 khi brand có `hasLayer3 = false` → auto gán `workplace_unit = "other"` (sentinel)
- [ ] Hiển thị khi `hasLayer3 = true` → required, searchable
- [ ] Data Layer 3 filter theo Layer 1 (+ Layer 2 nếu có)
- [ ] Vinpearl: data hiển thị theo Layer 2 đã chọn
- [ ] Green SM: hiển thị trực tiếp 14 bộ phận (không cần Layer 2)
- [ ] **Option "Khác"** xuất hiện ở mọi nhóm Layer 3 có data — là record bình thường trong `WorkplaceUnit`, admin CRUD như unit khác

---

#### Quy tắc chung cho option "Khác" ở tất cả 3 layer

**Priority:** Must Have (nằm trong FR-010 → FR-012)

- "Khác" **KHÔNG** phải giá trị đặc biệt trong code — là 1 record bình thường trong các bảng `WorkplaceBrand` / `WorkplaceCompany` / `WorkplaceUnit` (vd code `other_brand`, `vinpearl_other`, `gsm_other`, ...)
- Admin quản lý option "Khác" qua CRUD / Import Excel hoàn toàn giống các record khác (FR-031)
- Khác biệt với sentinel `"other"` dùng khi brand không có Layer 2/3: sentinel là giá trị nội bộ để query/export đồng nhất; "Khác" là option user **chọn** từ dropdown, không lẫn lộn
- Nếu brand chưa có data Layer 2/3 (ngoại trừ "Khác") → vẫn cần 1 record "Khác" để user có option chọn khi muốn
- User chọn "Khác" → lưu code của record đó bình thường (vd `workplace_unit = "gsm_other"`), admin thống kê được số lượng user khai "Khác" để bổ sung data

---

#### FR-013: Mã nhân viên

**Priority:** Must Have

**Description:**
Text field khi toggle nhân viên ON.

**Acceptance Criteria:**
- [ ] Required khi toggle nhân viên ON
- [ ] Min 3 ký tự (format check only — V1 chưa cross-check với registry)
- [ ] V1 không validate mã realtime — chỉ format check, admin verify sau

---

#### FR-014: Loại dữ liệu nơi làm việc (config data)

**Priority:** Must Have

**Description:**
Backend phải lưu trữ và expose cấu trúc 3 layer qua API. Mỗi brand có config `hasLayer2` / `hasLayer3`. Khi brand có data bổ sung sau, chỉ cần bật flag + thêm data, không cần deploy lại frontend.

**Acceptance Criteria:**
- [ ] API `GET /workplace/brands` — trả về 20 brands với flag `hasLayer2`, `hasLayer3`
- [ ] API `GET /workplace/companies?brand={code}` — trả về Layer 2 options của brand
- [ ] API `GET /workplace/units?brand={code}&company={code}` — trả về Layer 3 options
- [ ] Brand không có Layer 2 → `GET /workplace/companies?brand=X` trả `[]`
- [ ] Brand không có Layer 3 → `GET /workplace/units?brand=X` trả `[]`
- [ ] Admin có CRUD riêng để quản lý config (xem EPIC-007)

---

#### FR-015: Submit + lưu profile

**Priority:** Must Have

**Description:**
Submit form → validate → kiểm tra SĐT + email đã verified → lưu profile → set `profile_completed_at`.

**Acceptance Criteria:**
- [ ] Validate tất cả required fields trước submit
- [ ] SĐT phải verified → nếu chưa → error "Vui lòng xác minh số điện thoại"
- [ ] Email phải verified → nếu chưa → error "Vui lòng xác minh email"
- [ ] Lưu `account_type` = staff/creator
- [ ] Nếu staff → lưu đủ `workplace_brand`, `workplace_company` (hoặc `other`), `workplace_unit` (hoặc `other`), `employee_code`, `staff_status = "pending"`
- [ ] Set `profile_completed_at = now` → popup không hiện nữa
- [ ] Nếu staff → hiển thị badge "Đang xác minh"

---

### EPIC-004: Staff Verification (Admin)

#### FR-016: Admin verify mã nhân viên

**Priority:** Must Have

**Description:**
Admin xem danh sách user có `staff_status = pending` → verify hoặc reject.

**Acceptance Criteria:**
- [ ] Admin thấy danh sách pending: tên, mã NV, Thương hiệu, Công ty, Cơ sở, ngày submit
- [ ] Nút Verify → `staff_status = verified`, `staff_verified_at = now`
- [ ] Nút Reject → `staff_status = rejected`, lưu `staff_reject_reason` (optional)
- [ ] Sort / search / filter theo brand, pending time

---

#### FR-017: Notification verify/reject

**Priority:** Should Have

**Description:**
User nhận thông báo khi admin verify / reject mã NV.

**Acceptance Criteria:**
- [ ] Verified → "Mã nhân viên đã được xác minh ✓"
- [ ] Rejected → "Mã nhân viên không hợp lệ. Vui lòng kiểm tra lại" + lý do (nếu có)
- [ ] In-app notification + update badge trên profile

---

#### FR-018: Chỉnh sửa profile sau submit (Settings)

**Priority:** Should Have

**Description:**
User vào Settings sửa thông tin. Email/SĐT verified → read-only. Đổi nơi LV / mã NV → reset `staff_status = pending`.

**Acceptance Criteria:**
- [ ] Settings hiển thị profile hiện tại
- [ ] Editable: tên, toggle nhân viên, 3 layer, mã NV
- [ ] Email đã verified → read-only + badge ✓
- [ ] SĐT đã verified → read-only + badge ✓
- [ ] Đổi bất kỳ field nào trong nhóm staff (brand/company/unit/mã NV) → reset `staff_status = pending`
- [ ] User chưa verified SĐT/email (edge case) → cho sửa + yêu cầu verify lại

---

### EPIC-005: Admin — Tab Nội dung (Filter & Cột mới)

> Gộp từ `admin-dashboard-upgrade`. Mục tiêu: admin vận hành lọc video theo CBNV / cơ sở làm việc của creator ngay trên giao diện, không cần export rồi filter Excel.

#### FR-019: Filter Cơ sở làm việc trên Tab Nội dung

**Priority:** Must Have

**Description:**
Thêm filter "Cơ sở làm việc" theo 3 layer vào Tab Nội dung. Lọc video theo nơi làm việc của creator.

**Acceptance Criteria:**
- [ ] Hàng filter hiển thị 3 dropdown cascading: Thương hiệu → Công ty → Cơ sở/Bộ phận
- [ ] Thương hiệu luôn hiển thị
- [ ] Công ty chỉ hiển thị khi brand có `hasLayer2 = true`
- [ ] Cơ sở/Bộ phận chỉ hiển thị khi brand có `hasLayer3 = true`
- [ ] Có search text trong từng dropdown
- [ ] Chọn filter → table chỉ hiện video của creator thuộc phạm vi đã chọn
- [ ] Filter kết hợp được với filter Sự kiện + filter khác hiện có
- [ ] Clear filter button

**Dependencies:** FR-014 (workplace config APIs), backend join workplace vào content response

---

#### FR-020: Cột Phân loại creator trên Tab Nội dung

**Priority:** Must Have

**Description:**
Hiển thị "CBNV" / "Bên ngoài" cho mỗi video, dựa trên `account_type` của creator.

**Acceptance Criteria:**
- [ ] Cột "Phân loại" hiển thị sát cột Tên creator
- [ ] Badge phân biệt: CBNV (xanh), Bên ngoài (xám)
- [ ] Creator không có `account_type` → mặc định hiển thị "Bên ngoài"

---

#### FR-021: Cột Cơ sở làm việc trên Tab Nội dung

**Priority:** Must Have

**Description:**
Hiển thị tên cơ sở của creator theo format gộp 3 layer ngắn gọn.

**Acceptance Criteria:**
- [ ] Format hiển thị: `[Thương hiệu] · [Công ty (nếu ≠ other)] · [Cơ sở (nếu ≠ other)]`
  - VD Vinpearl: "Vinpearl · VinWonders · VinWonders Phú Quốc"
  - VD Green SM: "Green SM · Khối Kinh doanh"
  - VD Vinhomes: "Vinhomes"
- [ ] Creator bên ngoài → "—"
- [ ] Tooltip hiển thị đầy đủ nếu bị truncate

---

#### FR-022: Cột Hashtag cá nhân trên Tab Nội dung

**Priority:** Must Have

**Description:**
Hiển thị hashtag cá nhân của creator tại mỗi video, để admin vận hành không cần mapping thủ công từ Tab Creator.

**Acceptance Criteria:**
- [ ] Hiển thị `personal_hashtag` của creator
- [ ] Hiển thị "—" nếu creator chưa có hashtag

**Dependencies:** Backend join `personal_hashtag` vào content response

---

### EPIC-006: Admin — Tab Creator & Analytics (Filter & Cột)

#### FR-023: Filter Nơi làm việc trên Tab Creator

**Priority:** Must Have

**Description:**
Filter 3 layer giống FR-019 trên Tab Creator. Lọc tất cả CBNV thuộc phạm vi đã chọn.

**Acceptance Criteria:**
- [ ] Dùng chung component với FR-019
- [ ] Chọn cơ sở → hiện tất cả CBNV thuộc phạm vi
- [ ] Kết hợp được với filter Phân loại (FR-024)

---

#### FR-024: Filter Phân loại trên Tab Creator

**Priority:** Must Have

**Description:**
Dropdown 3 options: Tất cả / CBNV / Bên ngoài.

**Acceptance Criteria:**
- [ ] Chọn CBNV → chỉ hiện creator có `account_type = staff`
- [ ] Chọn Bên ngoài → chỉ hiện creator có `account_type = creator`
- [ ] Khi chọn "Bên ngoài" → ẩn/disable filter 3 layer (FR-023)

---

#### FR-025: Cột Hashtag cá nhân trên Tab Creator

**Priority:** Must Have

**Description:**
Cột hashtag cá nhân trong table Creator (verify xem đã có chưa — nếu chưa thì thêm mới).

**Acceptance Criteria:**
- [ ] Cột hiển thị `personal_hashtag`
- [ ] Hiển thị "—" nếu chưa có

---

#### FR-026: Ẩn cột Ngày tạo trên Tab Creator

**Priority:** Should Have

**Description:**
Ẩn cột "Ngày tạo" khỏi table Creator, giữ "Ngày tham gia".

**Acceptance Criteria:**
- [ ] Cột "Ngày tạo" không hiển thị trên giao diện
- [ ] Cột "Ngày tham gia" vẫn hiển thị
- [ ] Cột "Ngày tạo" vẫn available trong export (nếu user tick)

---

#### FR-027: Filter Phân loại CBNV trên Analytics

**Priority:** Must Have

**Description:**
Thêm filter phân loại CBNV/Bên ngoài trên màn hình Thống kê.

**Acceptance Criteria:**
- [ ] Dropdown: Tất cả / CBNV / Bên ngoài
- [ ] Chọn → tất cả KPI, chart cập nhật
- [ ] Kết hợp được với filter Sự kiện hiện có

---

#### FR-028: Filter Cơ sở làm việc trên Analytics

**Priority:** Must Have

**Description:**
Filter 3 layer giống FR-019 trên Analytics.

**Acceptance Criteria:**
- [ ] Dùng chung component với FR-019, FR-023
- [ ] KPI / chart filter theo phạm vi đã chọn
- [ ] Disable khi FR-027 = "Bên ngoài"

---

### EPIC-007: Admin — Export & Quản trị dữ liệu nơi làm việc

#### FR-029: Column Picker Dialog khi Export

**Priority:** Must Have

**Description:**
Khi bấm "Xuất dữ liệu" trên bất kỳ tab nào → hiện dialog checkbox list cho user chọn cột muốn xuất. Giải quyết triệt để vấn đề: không cần dev mỗi lần team vận hành muốn bỏ/thêm cột.

**Acceptance Criteria:**
- [ ] Dialog hiển thị danh sách checkbox = danh sách cột
- [ ] Default preset:
  - Tab Nội dung — **bỏ tick sẵn**: ID video, Thumbnail, Đối tác/Mã sự kiện, Tích cực, Trung lập, Tiêu cực
  - Tab Nội dung — **tick sẵn cột mới**: Phân loại, Cơ sở làm việc, Hashtag cá nhân
  - Tab Creator — **bỏ tick sẵn**: Đối tác VinWonders, Ngày tạo
  - Tab Creator — **tick sẵn cột mới**: Nơi làm việc, Hashtag cá nhân, Phân loại
- [ ] Nút "Chọn tất cả" — tick hết
- [ ] Nút "Mặc định" — reset về default preset
- [ ] Bấm "Xuất" → file chỉ chứa cột đã tick
- [ ] Cột mới đánh badge "MỚI"

**Dependencies:** Backend export API hỗ trợ param `columns[]`

---

#### FR-030: Export data — cột mới (Phân loại, Cơ sở, Hashtag)

**Priority:** Must Have

**Description:**
Export file phải chứa đúng data các cột mới khi user tick.

**Acceptance Criteria:**
- [ ] Cột Phân loại: "CBNV" / "Bên ngoài"
- [ ] Cột Cơ sở làm việc: format ngắn như FR-021 (`Brand · Company · Unit`)
- [ ] Cột Hashtag cá nhân: giá trị hashtag hoặc rỗng
- [ ] Creator bên ngoài → Cơ sở = rỗng

---

#### FR-031: Admin CRUD — Quản lý cấu hình 3 layer

**Priority:** Must Have

**Description:**
Admin có page riêng để quản lý cấu hình 20 brand + Layer 2 + Layer 3, bao gồm bật/tắt `hasLayer2` / `hasLayer3` từng brand.

**Acceptance Criteria:**
- [ ] Page "Quản lý nơi làm việc" có 3 tab: Thương hiệu, Công ty, Cơ sở/Bộ phận
- [ ] Tab Thương hiệu: list 20 brand + toggle `hasLayer2` + toggle `hasLayer3` + status active/inactive
- [ ] Tab Công ty: CRUD Layer 2 theo brand (filter theo brand)
- [ ] Tab Cơ sở/Bộ phận: CRUD Layer 3 theo brand + Layer 2
- [ ] Import Excel (optional V1 — nếu cần khởi tạo data lớn)
- [ ] Soft-delete (chuyển inactive), không hard-delete nếu đã có user tham chiếu
- [ ] **Option "Khác"** ở mọi layer được seed mặc định lúc khởi tạo (vd "Khác" ở Layer 1, "Khác" ở mỗi company có Layer 3 của Vinpearl, "Khác" ở Green SM), admin có thể ẩn / đổi tên / bổ sung — không hardcode trong code backend

---

## 7. Non-Functional Requirements

### NFR-001: Performance — Popup load

**Priority:** Must Have

Popup render < 200ms sau khi user mở app. Dropdown mở < 100ms (data cache state hoặc prefetch). API workplace config cache HTTP 5 phút.

---

### NFR-002: Performance — Filter admin

**Priority:** Must Have

Filter 3 layer trên admin response < 500ms trên dataset vài nghìn creator. Dropdown render ≤ 200ms. Table re-render ≤ 1s sau apply filter.

**Acceptance Criteria:**
- [ ] API filter dùng index trên `workplace_brand`, `workplace_company`, `workplace_unit`
- [ ] Debounce filter input (300ms)

---

### NFR-003: Mobile UX

**Priority:** Must Have

Popup = full-screen bottom sheet trên mobile. Các dropdown Layer scrollable. Keyboard không che input field. Form responsive chuẩn.

---

### NFR-004: Data Validation

**Priority:** Must Have

- SĐT: regex `^0\d{9}$` (10 số, bắt đầu 0)
- Email: basic format check (RFC 5322 simplified)
- Mã NV: min 3 ký tự (format only, không cross-check registry ở V1)
- Tất cả validate inline on blur + debounce 500ms cho unique check

---

### NFR-005: Unique Constraint

**Priority:** Must Have

SĐT và Email phải unique **độc lập** trên toàn hệ thống (không phải cặp). Check realtime khi user blur field. Nếu trùng → inline error.

---

### NFR-006: Security — OTP

**Priority:** Must Have

- OTP 6 số, expire 5 phút
- Rate limit gửi OTP: tối đa 3 lần / 10 phút / user
- Cooldown 60s giữa các lần gửi
- OTP hash khi lưu DB (không lưu plain text)
- Không lưu OTP / verify session vào localStorage

---

### NFR-007: Compatibility — Backward

**Priority:** Must Have

Upgrade admin dashboard không ảnh hưởng team khác đang dùng. Không breaking change trên API response hiện có — chỉ thêm field mới, không xóa field cũ.

---

### NFR-008: Data Integrity

**Priority:** Must Have

- Creator chưa có `account_type` → mặc định "Bên ngoài" trên UI
- `workplace_*` field = null → hiển thị "—", không crash
- Staff submit phải lưu đủ 3 layer (dùng `"other"` cho layer không apply) để query/export đồng nhất

---

### NFR-009: Usability — Filter UX nhất quán

**Priority:** Should Have

Filter 3 layer (FR-019, FR-023, FR-028) dùng chung **1 component** trên cả 3 tab. Cùng behavior cascade, cùng data source.

---

## 8. Data Model

### 8.1. User (mở rộng)

| Field | Type | Description |
|-------|------|-------------|
| `profile_completed_at` | datetime, nullable | Null = popup hiện |
| `dismiss_count` | int, default 0 | Số lần dismiss popup |
| `account_type` | `creator` \| `staff` | Phân nhóm chính |
| `workplace_brand` | string, nullable | Layer 1 — Thương hiệu (code) |
| `workplace_company` | string, nullable | Layer 2 — Công ty (code hoặc `"other"`) |
| `workplace_unit` | string, nullable | Layer 3 — Cơ sở/Bộ phận (code hoặc `"other"`) |
| `employee_code` | string, nullable | Mã nhân viên (format check) |
| `staff_status` | `pending` \| `verified` \| `rejected`, nullable | Trạng thái xác minh |
| `staff_verified_at` | datetime, nullable | Thời điểm verify |
| `staff_reject_reason` | string, nullable | Lý do reject (optional) |
| `phone_verified` | bool, default false | SĐT đã verify |
| `phone_verified_at` | datetime, nullable | Thời điểm verify SĐT |
| `email_verified` | bool, default false | Email đã verify |
| `email_verified_at` | datetime, nullable | Thời điểm verify email |

**Quy tắc lưu staff:**
- Brand có `hasLayer2 = false` → lưu `workplace_company = "other"`
- Brand có `hasLayer3 = false` → lưu `workplace_unit = "other"`
- Luôn lưu đủ 3 field để query/export đồng nhất

---

### 8.2. WorkplaceBrand (Layer 1)

| Field | Type | Description |
|-------|------|-------------|
| `code` | string, PK | Mã brand (VD: `vinpearl`, `greensm`, `vinhomes`) |
| `name` | string | Tên hiển thị |
| `has_layer2` | bool | Bật dropdown Công ty hay không |
| `has_layer3` | bool | Bật dropdown Cơ sở/Bộ phận hay không |
| `status` | `active` \| `inactive` | Trạng thái |
| `order` | int | Thứ tự hiển thị |

---

### 8.3. WorkplaceCompany (Layer 2)

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Mã company (unique per brand) |
| `brand_code` | string, FK → WorkplaceBrand | Thuộc brand nào |
| `name` | string | Tên hiển thị |
| `status` | `active` \| `inactive` | Trạng thái |

**V1:** Chỉ có 5 record thuộc brand Vinpearl.

---

### 8.4. WorkplaceUnit (Layer 3)

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Mã unit |
| `brand_code` | string, FK → WorkplaceBrand | Thuộc brand |
| `company_code` | string, nullable | Thuộc company (null nếu brand không có Layer 2) |
| `name` | string | Tên cơ sở / bộ phận |
| `status` | `active` \| `inactive` | Trạng thái |

**V1:** Vinpearl (~45 record theo Layer 2) + Green SM (14 record, `company_code = null`).

---

### 8.5. API Surface tóm tắt

| Endpoint | Purpose |
|----------|---------|
| `POST /users/check-unique` | Check unique SĐT/Email |
| `POST /users/profile/request-otp` | Request OTP SĐT/email |
| `POST /users/profile/verify-otp` | Verify OTP |
| `PUT /users/complete-profile` | Submit profile form |
| `GET /workplace/brands` | List 20 brand + flag |
| `GET /workplace/companies?brand={code}` | Layer 2 theo brand |
| `GET /workplace/units?brand={code}&company={code}` | Layer 3 theo brand (+company) |
| `GET /admin/users?staff_status=pending` | Danh sách verify |
| `PATCH /admin/users/:id/verify-staff` | Verify / reject |
| `GET /admin/contents?workplace_brand=&workplace_company=&workplace_unit=&account_type=` | Filter content |
| `GET /admin/creators?workplace_brand=&workplace_company=&workplace_unit=&account_type=` | Filter creator |
| `GET /admin/analytics?workplace_brand=&workplace_company=&workplace_unit=&account_type=&event_id=` | Filter analytics |
| `POST /admin/export?tab=content\|creator&columns[]=...` | Export với column picker |
| `GET/POST/PUT/DELETE /admin/workplace/brands\|companies\|units` | CRUD config |

---

## 9. Epics & Traceability

| Epic | Scope | FRs | Story Estimate | Priority |
|------|-------|-----|----------------|----------|
| EPIC-001: Popup trigger | End-user | FR-001, FR-002, FR-003 | 2-3 stories | Must |
| EPIC-002: Form cơ bản + OTP | End-user | FR-004, FR-005, FR-006, FR-007, FR-008 | 5-7 stories | Must |
| EPIC-003: Form nhân viên + 3 Layer | End-user | FR-009, FR-010, FR-011, FR-012, FR-013, FR-014, FR-015 | 6-8 stories | Must |
| EPIC-004: Staff verification | Admin | FR-016, FR-017, FR-018 | 2-3 stories | Must |
| EPIC-005: Admin Tab Nội dung | Admin | FR-019, FR-020, FR-021, FR-022 | 3-4 stories | Must |
| EPIC-006: Admin Tab Creator & Analytics | Admin | FR-023, FR-024, FR-025, FR-026, FR-027, FR-028 | 4-5 stories | Must |
| EPIC-007: Admin Export & Config | Admin | FR-029, FR-030, FR-031 | 3-4 stories | Must |

**Tổng:** 7 epics · 31 FRs · 9 NFRs · ~25-34 stories

---

## 10. Prioritization Summary

| Priority | FRs | NFRs |
|----------|-----|------|
| **Must Have** | 26 | 8 |
| **Should Have** | 5 | 1 |

---

## 11. Dependencies

### Internal

| Dependency | Status | Blocking? |
|-----------|--------|-----------|
| Auth flow social login (TikTok / Google) hiện có | Assumed available | No |
| SMS gateway để gửi OTP | Cần confirm provider | **Yes** — EPIC-002 |
| Email SMTP để gửi OTP | Cần confirm provider | **Yes** — EPIC-002 |
| Admin dashboard (UMI) | Đang dùng — sẽ upgrade | No |
| VCreator Dashboard v2 (Next.js 16) | PRD riêng, clone TCB | No — không phụ thuộc |

### External

| Dependency | Status |
|-----------|--------|
| Danh sách chính xác 20 brand + config `hasLayer2`/`hasLayer3` | Có trong overview |
| Data Layer 2 (Vinpearl) + Layer 3 (Vinpearl + Green SM) | Có trong overview |
| Xác nhận scope qua email từ phía khách hàng | Đang chờ |

---

## 12. Assumptions

1. Auth flow social login (TikTok, Google) đã có — chỉ cần hook vào callback để trigger popup
2. SMS + Email gateway có sẵn hoặc sẽ được cấp
3. Danh sách 20 brand tương đối ổn định trong V1 — data driven, có CRUD admin để mở rộng
4. Admin dashboard (UMI) vẫn được duy trì song song với VCreator Dashboard v2
5. Brand chưa có data Layer 2/3 → dùng `"other"`, KHÔNG block user submit
6. V1 không có cross-check mã NV với registry HR (sang V2)

---

## 13. Open Questions

| # | Câu hỏi | Impact |
|---|---------|--------|
| 1 | SMS provider nào? Rate limit / chi phí? | FR-006 |
| 2 | Email SMTP provider nào? Template email OTP? | FR-007 |
| 3 | `dismiss_count` scope — theo user hay theo device? | FR-003 |
| 4 | Popup có nên block navigation hay chỉ overlay? | FR-003 UX |
| 5 | Column picker lưu preference user (localStorage/server) hay mỗi lần chọn lại? | FR-029 |
| 6 | Export format V1: chỉ Excel (.xlsx) hay thêm CSV? | FR-029 scope |
| 7 | Policy khi creator bên ngoài đổi thành CBNV sau (upgrade account_type)? | FR-018 |
| 8 | Admin Config 3 layer (FR-031) — V1 có cần Import Excel hay chỉ CRUD form? | FR-031 scope |

---

## 14. Timeline (Estimate)

| Phase | Ngày | Nội dung |
|-------|------|----------|
| Phase 1 — Data & config API | 1-2 | Model WorkplaceBrand/Company/Unit + CRUD admin + seed data |
| Phase 2 — Auth + OTP backend | 2-3 | Profile completion APIs, OTP request/verify, rate limit |
| Phase 3 — Popup + Form frontend | 3-4 | Popup progressive urgency, Form 2 bước, 3 layer cascading, OTP UI |
| Phase 4 — Staff verification | 1 | Admin danh sách pending + verify/reject + notification |
| Phase 5 — Admin dashboard upgrade | 3-4 | Filter 3 layer (3 tab), cột mới, Column Picker, Export mới |
| Phase 6 — Settings edit + polish | 1 | Settings page + edge cases + mobile responsive |
| **Tổng** | **~11-15 ngày** | Backend / Admin / Frontend có thể chạy parallel một phần |

**Target:** Đầu tháng 5/2026.

---

## 15. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-12 | Product Manager | Rewrite greenfield. Chuyển sang cấu trúc 3 layer. Gộp filter admin từ `admin-dashboard-upgrade`. |

---

*Created with BMAD Method v6 — Phase 2 (Planning)*
