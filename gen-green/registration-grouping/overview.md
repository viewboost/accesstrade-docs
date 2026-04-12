# Đăng ký và Phân nhóm Tài khoản — Overview

> **Project:** Gen-Green Registration & Account Grouping
> **Ngày:** 2026-04-12
> **Trạng thái:** Đang thiết kế
> **Tham chiếu:** [Meeting note 0410](../meeting-notes/0410.md) · [Brainstorm](.bmad/brainstorming-gengreen-registration-grouping-2026-04-12.md)

---

## 1. Bối cảnh

Gen-Green có ~150.000 creators, trong đó **core là đội ngũ cán bộ nhân viên (CBNV)** thuộc hệ sinh thái Vin (~57 cơ sở, 6 nhóm). Hiện tại:

- Hệ thống chưa phân biệt được CBNV và creator bên ngoài
- Admin muốn filter nội dung/creator theo cơ sở làm việc nhưng không có data
- Nhiều user đăng ký bằng social login (TikTok/Google) → thiếu SĐT hoặc email
- Chiến lược kinh doanh: **"đánh từ trong đánh ra"** — kích hoạt CBNV trước, mở rộng creator bên ngoài sau

**Mục tiêu năm:** 1.000 user generate doanh thu affiliate, target 50 tỷ doanh thu.

---

## 2. Mục tiêu chức năng

1. **Thu thập đủ thông tin** cho tất cả creator: họ tên, SĐT, email (required cho mọi người)
2. **Phân loại tài khoản**: CBNV (có nơi làm việc + mã nhân viên) vs Creator bên ngoài
3. **Hiển thị phân loại trên admin**: filter theo cơ sở làm việc, badge CBNV/bên ngoài ở tab Nội dung và tab Creator
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
| Tôi là nhân viên | toggle | ✅ | Default: OFF |

### Bước 2: Thông tin nhân viên (chỉ khi toggle ON)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| Nơi làm việc | grouped searchable select | ✅ | 6 nhóm, 57 cơ sở |
| Mã nhân viên | text | ✅ | Format check only (min 3 ký tự) |

---

## 5. Danh sách nơi làm việc

### VinPalace (3)
- Almaz
- VinPalace Cổ Loa
- VinPalace Ocean City

### Vinpearl (17)
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

### VinWonders (15)
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

### Vinpearl Golf (5)
- Vinpearl Golf Hải Phòng
- Vinpearl Golf Léman
- Vinpearl Golf Nam Hội An
- Vinpearl Golf Nha Trang
- Vinpearl Golf Phú Quốc

### Green SM (14)
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

### Khác (3)
- HO
- Aquafield Nha Trang
- Aquafield Ocean City

---

## 6. Phân nhóm tài khoản

### Hai nhóm chính

| Nhóm | Mô tả | Badge |
|------|-------|-------|
| `staff` | Cán bộ nhân viên Vin | "Nhân viên" + tên cơ sở |
| `creator` | Creator bên ngoài | "Creator" |

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
| `workplace_group` | string, nullable | VinPalace / Vinpearl / VinWonders / Golf / GreenSM / Khác |
| `workplace_name` | string, nullable | Tên cơ sở cụ thể |
| `employee_code` | string, nullable | Mã nhân viên |
| `staff_status` | `pending` \| `verified` \| `rejected`, nullable | Trạng thái xác minh |
| `staff_verified_at` | datetime, nullable | Thời điểm verify |

---

## 7. Admin — Hiển thị & Filter

Từ meeting note 0410, yêu cầu admin:

### Tab Nội dung (video)
- **Thêm cột**: Cơ sở làm việc, Phân loại creator (CBNV/bên ngoài)
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

## 8. Edge cases

| Case | Xử lý |
|------|-------|
| Mã NV sai / không tồn tại | Nhận form, tag `staff_pending`, admin reject sau |
| Nhân viên nghỉ việc | Admin gỡ staff tag → `account_type = creator` |
| Đổi nơi làm việc | Settings → sửa được, reset `staff_status` → pending |
| SĐT trùng user khác | Inline error "SĐT đã được sử dụng" |
| Email trùng user khác | Inline error tương tự |
| Social login không trả email | Field email trống, bắt buộc điền |
| User chọn nhân viên rồi đổi ý | Toggle OFF → clear employee fields |
| Nhiều nơi làm việc (kiêm nhiệm) | V1: chọn 1 nơi chính |
| Nơi LV không trong list | Chọn nhóm "Khác" |

---

## 9. Mở cho version sau

- Chuyển form đăng ký truyền thống (tên + SĐT + email trước social login) — cần redesign auth flow
- Multi-select nơi làm việc cho trường hợp kiêm nhiệm
- HR sync tự động: periodic check mã NV còn active không
- Staff benefits: chiến dịch nội bộ riêng, commission rate khác
