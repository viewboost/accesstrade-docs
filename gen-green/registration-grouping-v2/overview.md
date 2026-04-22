# Đăng ký và Phân nhóm Tài khoản — Overview

> **Project:** Gen-Green Registration & Account Grouping
> **Ngày:** 2026-04-12
> **Trạng thái:** Đang thiết kế
> **Tham chiếu:** [Meeting note 0410](../meeting-notes/0410.md) · [Brainstorm](.bmad/brainstorming-gengreen-registration-grouping-2026-04-12.md)

---

## 1. Bối cảnh

Gen-Green có ~150.000 creators, trong đó **core là đội ngũ cán bộ nhân viên (CBNV)** thuộc hệ sinh thái Vin (20 thương hiệu, phân cấp 3 layer). Hiện tại:

- Hệ thống chưa phân biệt được CBNV và user thường
- Admin muốn filter nội dung/creator theo cơ sở làm việc nhưng không có data
- Nhiều user đăng ký bằng social login (TikTok/Google) → thiếu SĐT hoặc email
- Chiến lược kinh doanh: **"đánh từ trong đánh ra"** — kích hoạt CBNV trước, mở rộng user thường sau

**Mục tiêu năm:** 1.000 user generate doanh thu affiliate, target 50 tỷ doanh thu.

---

## 2. Mục tiêu chức năng

1. **Thu thập đủ thông tin** cho tất cả creator: họ tên, SĐT, email (required cho mọi người)
2. **Phân loại tài khoản**: CBNV (có mã nhân viên + nơi làm việc) vs Không phải CBNV
3. **Hiển thị phân loại trên admin**: filter theo cơ sở làm việc, badge CBNV / Không phải CBNV ở tab Nội dung và tab Creator
4. **Hỗ trợ export**: cột nơi làm việc, phân loại creator trong report xuất ra

---

## 3. Hai luồng chính

### Luồng 1: User cũ — Popup cập nhật thông tin

User đã có tài khoản Gen-Green (đăng ký trước đó bằng social login), thiếu thông tin.

```
User mở app → đã đăng nhập → profile thiếu SĐT/email/phân loại?
  → Hiển thị popup "Cập nhật thông tin"
  → User điền: họ tên, SĐT, email, toggle nhân viên
  → Nếu nhân viên: chọn cơ sở làm việc + mã NV
  → Submit → Done
```

**Popup behavior:**
- Lần 1-2: có nút "Để sau" (dismissible)
- Lần 3+: mandatory — không có nút đóng, phải điền mới dùng tiếp

### Luồng 2: User mới — Đăng nhập social + popup ngay

User chưa có tài khoản, đăng nhập bằng TikTok/Google lần đầu.

```
User mở app → chưa có tài khoản → Login TikTok/Google
  → Social login OK → Tạo account (pre-fill tên, email từ social)
  → Popup "Cập nhật thông tin" ngay
  → User điền: SĐT (bắt buộc), confirm email, toggle nhân viên
  → Nếu nhân viên: chọn cơ sở + mã NV
  → Submit → Done
  → User ignore (Để sau) → lần sau vào = Luồng 1
```

**Lưu ý từ meeting 0410:**
- Quân đề xuất: nên chuyển sang form đăng ký truyền thống (tên + SĐT + email trước) thay vì social login trước → tránh user rơi vào vùng thiếu data
- Tuy nhiên, đụng vào luồng authentication hiện tại phức tạp → **V1 giữ social login + popup bổ sung**, cân nhắc chuyển form đăng ký ở version sau

---

## 4. Form chi tiết

### Bước 1: Thông tin cơ bản (required cho TẤT CẢ)

| Field | Type | Required | Pre-fill |
|-------|------|----------|----------|
| Họ tên | text | ✅ | Từ social login |
| Số điện thoại | text (format 0xxx) | ✅ | — |
| Email | text | ✅ | Từ social login |
| Tôi có mã nhân viên | toggle | ✅ | Default: OFF |

### Bước 2: Thông tin nhân viên (chỉ khi toggle ON)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| Thương hiệu (Layer 1) | searchable select | ✅ | 20 thương hiệu, luôn hiển thị |
| Công ty (Layer 2) | searchable select | Conditional | Chỉ hiển thị nếu Layer 1 có `hasLayer2 = true`. Mặc định `other` nếu brand không bật |
| Cơ sở / Bộ phận (Layer 3) | searchable select | Conditional | Chỉ hiển thị nếu Layer 1 có `hasLayer3 = true`. Mặc định `other` nếu brand không bật |
| Mã nhân viên | text | ✅ | Format check only (min 3 ký tự) |

**Logic hiển thị form:**
- Mỗi brand (Layer 1) có 2 flag config: `hasLayer2` và `hasLayer3`
- Flag bật → render dropdown tương ứng trên UI
- Flag tắt → ẩn dropdown, auto gán giá trị `other`

---

## 5. Cấu trúc dữ liệu nơi làm việc — 3 Layer

Data nơi làm việc được tổ chức thành **3 layer phân cấp**, cấu hình theo từng thương hiệu.

### Layer 1 — Thương hiệu (20)

| # | Thương hiệu | hasLayer2 | hasLayer3 |
|---|-------------|-----------|-----------|
| 1 | Vinpearl | ✅ | ✅ |
| 2 | Green SM | ❌ | ✅ |
| 3 | Vinhomes | ❌ | ❌ |
| 4 | Vincom | ❌ | ❌ |
| 5 | VinUni | ❌ | ❌ |
| 6 | Vinschool | ❌ | ❌ |
| 7 | VinFuture | ❌ | ❌ |
| 8 | Vinmec | ❌ | ❌ |
| 9 | VinFast | ❌ | ❌ |
| 10 | Green Future | ❌ | ❌ |
| 11 | V-Green | ❌ | ❌ |
| 12 | Quỹ Thiện Tâm | ❌ | ❌ |
| 13 | Quỹ Vì Tương Lai Xanh | ❌ | ❌ |
| 14 | VinEnergo | ❌ | ❌ |
| 15 | VinDynamics | ❌ | ❌ |
| 16 | VinSmart Future | ❌ | ❌ |
| 17 | VinCSS | ❌ | ❌ |
| 18 | VinMotion | ❌ | ❌ |
| 19 | VinRobotics | ❌ | ❌ |
| 20 | Vinspeed | ❌ | ❌ |
| 21 | **Khác** | ❌ | ❌ |

> **Quy tắc:** Brand nào chưa có data Layer 2/Layer 3 → flag tương ứng = `false` → UI ẩn dropdown → giá trị mặc định = `other`. Khi có data bổ sung cho brand, chỉ cần bật flag lại.
>
> **Option "Khác" ở mỗi layer:** Là 1 record bình thường trong bảng `WorkplaceBrand` / `WorkplaceCompany` / `WorkplaceUnit`, admin CRUD / import như các record khác — không phải giá trị đặc biệt hardcode trong code. Admin có thể ẩn, đổi tên, bổ sung option "Khác" như mọi item khác.

### Layer 2 — Công ty (chỉ Vinpearl có)

Chỉ **Vinpearl** cấu hình Layer 2. Các thương hiệu khác đều mặc định `other`.

| Công ty (thuộc Vinpearl) |
|--------------------------|
| VinPalace |
| Vinpearl |
| VinWonders |
| Vinpearl Golf |
| Khác (other) |

### Layer 3 — Cơ sở / Bộ phận

Layer 3 tùy thuộc cấu hình của Layer 1 (và Layer 2 nếu có).

#### 3.1. Vinpearl (qua Layer 2)

**VinPalace** (3 + Khác)
- Almaz
- VinPalace Cổ Loa
- VinPalace Ocean City
- Khác

**Vinpearl** (19 + Khác)
- Four Points by Sheraton Hà Giang
- Four Points by Sheraton Lạng Sơn
- Hòn Tằm Resort
- Imperial Club
- Sheraton Vinh
- Vinpearl Beachfront Nha Trang
- Vinpearl Cửa Hội Resort Aff. by Meliá
- Vinpearl Cửa Sót Resort Aff. by Meliá
- Vinpearl Empire Nha Trang, Aff. by Meliá
- Vinpearl Hà Tĩnh Affiliated by Meliá
- Vinpearl Hotel Bắc Ninh
- Vinpearl Luxury Nha Trang
- Vinpearl Resort & Golf Nam Hội An
- Vinpearl Resort & Spa Hạ Long
- Vinpearl Resort & Spa Nha Trang Bay
- Vinpearl Resort & Spa Phú Quốc
- Vinpearl Resort Nha Trang
- Vinpearl Wonderworld Phú Quốc
- Vinholidays Fiesta Phú Quốc
- Khác

**VinWonders** (15 + Khác)
- GrandWorld Phú Quốc
- Học viện ngựa Vũ Yên
- Khu Tắm Bùn Hòn Tằm
- VinKE & Aquarium Times City
- Vinpearl Harbour
- Vinpearl Safari Phú Quốc
- VinWonders Cửa Hội
- VinWonders Grand Park
- VinWonders Hà Nội
- VinWonders Nam Hội An
- VinWonders Nha Trang
- VinWonders Nha Trang_CTCP
- VinWonders Phú Quốc
- VinWonders Vũ Yên
- VinWonders Mỹ Lâm
- Khác

**Vinpearl Golf** (5 + Khác)
- Vinpearl Golf Hải Phòng
- Vinpearl Golf Léman
- Vinpearl Golf Nam Hội An
- Vinpearl Golf Nha Trang
- Vinpearl Golf Phú Quốc
- Khác

**Khác (Vinpearl)** (3)
- HO
- Aquafield Nha Trang
- Aquafield Ocean City

#### 3.2. Green SM (trực tiếp, không qua Layer 2)

14 bộ phận + Khác:
- Khối Kinh doanh
- Khối Marketing
- Khối Vận hành
- Khối Tài chính Đầu tư
- Khối Tài chính Quản trị
- Khối Hỗ trợ
- Khối Thanh tra, KSCL và ANAT
- Khối Công nghệ
- Phòng Pháp chế
- Phòng Quan hệ đối ngoại
- Phát triển thị trường & Setup
- Vận hành VinBus
- Vận hành DV Di chuyển
- Trung tâm CSKH
- Khác

#### 3.3. Các thương hiệu còn lại

Chưa có data Layer 3 → `hasLayer3 = false` → UI chỉ hỏi Layer 1, Layer 2/3 mặc định `other`. Data sẽ bổ sung sau theo yêu cầu từng brand.

---

## 6. Phân nhóm tài khoản

### Hai nhóm chính

| Nhóm | Mô tả | Badge |
|------|-------|-------|
| `staff` | Cán bộ nhân viên Vin | "Nhân viên" + tên cơ sở |
| `creator` | Không phải CBNV | "Không phải CBNV" |

### Staff verification flow

```
User submit (isStaff=true)
  → staff_status = "pending"
  → Badge "Đang xác minh" trên profile
  → Admin/HR verify async
    → verified → Badge "Nhân viên ✓", unlock chiến dịch nội bộ
    → rejected → Thông báo "Mã nhân viên không hợp lệ"
```

**Không validate mã NV realtime** — chỉ format check. Admin verify sau.

### Data model

| Field | Type | Description |
|-------|------|-------------|
| `profile_completed_at` | datetime, nullable | Null = popup hiện |
| `dismiss_count` | int, default 0 | Số lần dismiss popup |
| `account_type` | `creator` \| `staff` | Phân nhóm chính |
| `workplace_brand` | string, nullable | **Layer 1** — Thương hiệu (Vinpearl, GreenSM, Vinhomes, ...) |
| `workplace_company` | string, nullable | **Layer 2** — Công ty (VinPalace, Vinpearl, VinWonders, Vinpearl Golf, other) |
| `workplace_unit` | string, nullable | **Layer 3** — Cơ sở / Bộ phận cụ thể (hoặc `other`) |
| `employee_code` | string, nullable | Mã nhân viên |
| `staff_status` | `pending` \| `verified` \| `rejected`, nullable | Trạng thái xác minh |
| `staff_verified_at` | datetime, nullable | Thời điểm verify |

**Quy tắc lưu:**
- Brand nào `hasLayer2 = false` → `workplace_company = "other"`
- Brand nào `hasLayer3 = false` → `workplace_unit = "other"`
- Luôn lưu đủ 3 field để query/export đồng nhất.

---

## 7. Admin — Hiển thị & Filter

Từ meeting note 0410, yêu cầu admin:

### Tab Nội dung (video)
- **Thêm cột**: Cơ sở làm việc, Loại tài khoản (CBNV / Không phải CBNV)
- **Thêm filter**: Dropdown cơ sở làm việc
- **Bỏ cột thừa**: ID video, Thumbnail, Đối tác/Mã s��� kiện, Tích cực/Trung lập/Tiêu cực
- **Thêm cột**: Hashtag cá nhân

### Tab Creator
- **Thêm filter**: Nơi làm việc (dropdown grouped)
- **Hiển thị**: Tên, Hashtag cá nhân, Tổng view, Tổng tiền, Tổng tiền đã rút, Tổng video
- **Bỏ cột**: Ngày tạo (chỉ giữ Ngày tham gia)

### Export
- Cho phép **chọn cột khi xuất** (không xuất hết mặc định)
- Bổ sung cột: Cơ sở làm việc, Phân loại creator

---

## 8. Import mã nhân viên (Employee Registry)

### Vấn đề hiện tại

Hệ thống chưa có "danh sách nhân viên chính thức" để validate. Hoàn toàn dựa vào user tự khai mã NV + admin manual verify. → Chậm, dễ sai, không scale.

### Giải pháp: Bảng Employee Registry

Tạo bảng `employee_registry` riêng biệt với user model — đây là **nguồn sự thật từ HR** về danh sách nhân viên. User model chỉ reference tới registry qua `employee_code`.

| Field | Type | Mô tả |
|-------|------|-------|
| `employee_code` | string, unique | Khóa chính |
| `full_name` | string | Họ tên theo HR |
| `cccd` | string, nullable | Để match identity |
| `phone` | string, nullable | Để match identity |
| `email` | string, nullable | Để match identity |
| `workplace_brand` | string | **Layer 1** — Thương hiệu |
| `workplace_company` | string | **Layer 2** — Công ty (hoặc `other`) |
| `workplace_unit` | string | **Layer 3** — Cơ sở / Bộ phận (hoặc `other`) |
| `department` | string, nullable | Phòng ban |
| `status` | enum | `active` / `inactive` / `terminated` |
| `gen_green_user_id` | string, nullable | Linked Gen-Green user (nếu đã match) |
| `imported_at` | datetime | Lần import gần nhất |
| `import_id` | string | ID batch import |

### 4 luồng import — cùng 1 pipeline

Cả 4 scenario đi qua cùng 1 pipeline: **Upload → Parse → Validate → Update Registry → Match Users → Action → Notify → Log**. Chỉ khác ở bước Action.

#### Luồng 1: Import TRƯỚC khi user đăng ký

```
HR upload danh sách nhân viên (Excel)
  → Lưu vào employee_registry
  → Chưa match ai (chỉ là registry)

Sau đó user đăng ký + khai mã NV
  → Lookup registry WHERE employee_code = mã NV
    → Found + match identity (CCCD/SĐT/email) → auto-verify
    → Found + identity mismatch → pending + flag admin
    → Not found → pending (mã không trong registry)
```

#### Luồng 2: Import SAU khi user đã đăng ký

```
User đã tự khai mã NV (staff_status = pending)
HR upload danh sách nhân viên
  → Update employee_registry
  → Batch match: tất cả user pending vs registry
    → Match + identity OK → auto-verify
    → Match + identity mismatch → flag admin
    → No match → giữ pending
  → Email summary cho admin: N verified, M flagged, K unchanged
```

#### Luồng 3: Import khi ĐIỀU CHUYỂN công tác

```
HR upload delta file (nhân viên thay đổi cơ sở/phòng ban)
  → Update employee_registry: workplace_brand / workplace_company / workplace_unit
  → Tìm Gen-Green user đã link → update user profile
  → KHÔNG reset staff_status (vẫn verified)
  → Notify user: "Thông tin nơi làm việc đã cập nhật: [Cơ sở mới]"
  → Ghi log: "Điều chuyển từ X sang Y"
```

#### Luồng 4: Import khi NGHỈ VIỆC

```
HR upload delta file (nhân viên nghỉ)
  → Update employee_registry: status = "terminated"
  → Tìm Gen-Green user đã link:
    → account_type → "creator" (gỡ staff)
    → staff_status → null
    → workplace → null
  → Notify user: "Tài khoản chuyển về dạng Creator từ ngày X"
  → Grace period 7 ngày trước khi mất quyền chiến dịch nội bộ
  → Ghi log: "Nghỉ việc, gỡ staff tag"
```

### Match logic

1. **employee_code** exact match (bắt buộc)
2. Cross-check ít nhất 1 identity field: CCCD, SĐT, hoặc email
3. Mã NV match + identity mismatch → flag admin (có thể user khai mã người khác)

### Import format

Excel (.xlsx) — HR quen dùng. Columns:

| Cột | Bắt buộc | Mô tả |
|-----|----------|-------|
| employee_code | ✅ | Mã nhân viên |
| full_name | ✅ | Họ tên |
| cccd | Nên có | CCCD |
| phone | Nên có | SĐT |
| email | Nên có | Email |
| workplace_brand | ✅ | Layer 1 — Thương hiệu |
| workplace_company | Conditional | Layer 2 — Công ty (bỏ qua nếu brand `hasLayer2=false`) |
| workplace_unit | Conditional | Layer 3 — Cơ sở/Bộ phận (bỏ qua nếu brand `hasLayer3=false`) |
| department | Optional | Phòng ban |
| status | ✅ | active / terminated |

### Quy tắc import

| Quy tắc | Chi tiết |
|---------|---------|
| **Dry-run bắt buộc** | Preview kết quả trước khi commit: "12 verified, 3 conflict, 5 new, 2 terminated" |
| **employee_code unique** | Trùng mã → update record (không tạo mới) |
| **Validate format trước** | Check header, data types, required fields. Reject file nếu format sai |
| **Async processing** | File lớn (>1000 records) → background job → email kết quả |
| **Rollback** | Mỗi import có import_id. Rollback = revert tất cả changes thuộc import_id |
| **1 queue** | Chỉ 1 import chạy tại 1 thời điểm |
| **Notify trước thay đổi** | Đặc biệt nghỉ việc: grace period 7 ngày |
| **Audit đầy đủ** | import_id, file_name, uploaded_by, timestamp, records_affected |

### Ai thực hiện?

- **V1:** HR Vin gửi file → Admin AT upload vào hệ thống
- **V2:** HR Vin có quyền upload trực tiếp (nếu cần)
- **V3:** API sync tự động từ hệ thống HR Vin (periodic)

### Frequency

- **V1:** Ad-hoc — khi HR gửi file (điều chuyển, nghỉ việc, nhân viên mới)
- **V2:** Monthly — HR gửi full dump đầu mỗi tháng

---

## 9. Edge cases

| Case | Xử lý |
|------|-------|
| Mã NV sai / không tồn tại | Nếu có registry → not found → pending. Nếu chưa có registry → pending + admin verify manual |
| Mã NV đúng nhưng identity mismatch | Flag admin review — có thể user khai mã người khác |
| Nhân viên nghỉ việc | Import luồng 4 → gỡ staff tag, grace period 7 ngày |
| Đổi nơi làm việc (user tự đổi) | Settings → sửa được, reset `staff_status` → pending |
| Đổi nơi làm việc (HR import) | Import luồng 3 → auto-update, giữ verified |
| SĐT trùng user khác | Inline error "SĐT đã được sử dụng" |
| Email trùng user khác | Inline error tương tự |
| Social login không trả email | Field email trống, bắt buộc điền |
| User chọn nhân viên rồi đổi ý | Toggle OFF → clear employee fields |
| Nhiều nơi làm việc (kiêm nhiệm) | V1: chọn 1 nơi chính |
| Nơi LV không trong list | Chọn nhóm "Khác" |
| HR upload sai file / file cũ | Dry-run mode bắt buộc + dedup bằng import_id |
| Nhân viên có nhiều mã NV (cũ/mới) | employee_code unique, mã cũ → terminated, mã mới → active |
| Import file lớn (>1000 records) | Async background job, email kết quả khi xong |

---

## 10. Mở cho version sau

- Chuyển form đăng ký truyền thống (tên + SĐT + email trước social login) — cần redesign auth flow
- Multi-select nơi làm việc cho trường hợp kiêm nhiệm
- HR Vin upload trực tiếp (không qua admin AT)
- API sync tự động từ hệ thống HR Vin (periodic monthly)
- Staff benefits: chiến dịch nội bộ riêng, commission rate khác
