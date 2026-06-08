# PRD: Liên kết tài khoản Threads & Cải tiến Video nổi bật

**Tác giả:** Project Manager
**Ngày tạo:** 2026-06-08
**Phiên bản:** 1.0
**Trạng thái:** Draft

---

## 1. Tổng quan (Overview)

### 1.1 Bối cảnh
Nền tảng hiện tại đã hỗ trợ liên kết các tài khoản mạng xã hội (Facebook, TikTok, YouTube...) cho phép người dùng tổng hợp và quản lý nội dung tập trung. Threads đang phát triển mạnh và trở thành kênh nội dung quan trọng, đặc biệt với nhóm KOL/Creator. Bên cạnh đó, mục "Video nổi bật" hiện đang hiển thị lẫn cả bài viết dạng text/ảnh, gây nhiễu trải nghiệm cho người xem muốn tập trung vào nội dung video.

### 1.2 Mục tiêu
- **Mục tiêu chính:** Mở rộng hệ sinh thái mạng xã hội bằng việc tích hợp Threads, đồng thời tối ưu trải nghiệm xem video tại mục "Video nổi bật".
- **Mục tiêu phụ:**
  - Tăng số lượng tài khoản liên kết trung bình/người dùng.
  - Tăng thời gian xem video (watch time) tại mục Video nổi bật.
  - Giảm tỷ lệ bounce ở trang profile/feed.

### 1.3 Phạm vi
- Tích hợp OAuth Threads (đăng nhập, ủy quyền, đồng bộ profile).
- Đồng bộ nội dung từ Threads về hệ thống.
- Lọc và chỉ hiển thị nội dung dạng video tại mục "Video nổi bật".

---

## 2. Yêu cầu chức năng (Functional Requirements)

### 2.1 Tính năng A: Liên kết tài khoản Threads

#### FR-A1: Khởi tạo liên kết
- Tại trang **Cài đặt → Tài khoản liên kết**, hiển thị thêm nút **"Liên kết 
Threads"** với logo Threads chính thức.
- Trạng thái nút:
  - `Chưa kết nối`: hiển thị "Thêm tài khoản".
  - `Đã kết nối`: hiển thị tên tài khoản Threads 


#### FR-A2: Luồng OAuth
- Sử dụng **Threads Graph API** (Meta) qua giao thức OAuth 2.0.
- Scope yêu cầu tối thiểu: `threads_basic`, `threads_content_publish` (read-only ở giai đoạn 1).
- Sau khi user authorize, hệ thống lưu `access_token`, `refresh_token`, `expires_at`, `threads_user_id`.
- Token được mã hóa AES-256 trước khi lưu DB.

#### FR-A3: Đồng bộ dữ liệu
- Sau khi liên kết thành công, hệ thống tự động đồng bộ:
  - Profile: avatar, display name, bio, follower count.
  - Bài đăng gần nhất: tối đa **50 bài** lần đầu, sau đó delta sync mỗi **15 phút**.
- Mỗi bài đăng phân loại theo media type: `TEXT`, `IMAGE`, `VIDEO`, `CAROUSEL`.

#### FR-A4: Quản lý kết nối
- User có thể ngắt kết nối bất kỳ lúc nào → revoke token + xóa dữ liệu cache (giữ lại dữ liệu đã đăng public).
- Hiển thị thời gian đồng bộ gần nhất.
- Thông báo cho user khi token hết hạn (in-app + email).

---

### 2.2 Tính năng B: Video nổi bật chỉ hiển thị video

#### FR-B1: Logic lọc
- Mục **"Video nổi bật"** chỉ hiển thị các item có `media_type IN ('VIDEO')`.
- Loại bỏ hoàn toàn: text post, image post, carousel chỉ chứa ảnh.
- Với carousel có chứa video → chỉ trích xuất phần video.

#### FR-B2: Tiêu chí sắp xếp và số lượng hiển thị
- **Giữ nguyên logic sắp xếp cũ:** sort theo `order` ASC, sau đó theo `view` DESC.
- Hiển thị **8 video nổi bật** cho cả desktop lẫn mobile (cố định, không đổi theo breakpoint).
- Chỉ lấy item dạng video (theo FR-B1), không hiển thị bài viết dạng text/ảnh.

---

## 3. Yêu cầu phi chức năng (Non-Functional Requirements)

| Hạng mục | Yêu cầu |
|---|---|
| **Hiệu năng** | API list video nổi bật P95 < 300ms; sync Threads batch < 5s/50 items |
| **Bảo mật** | Token mã hóa AES-256; tuân thủ Meta Platform Policy; log audit khi connect/disconnect |
| **Khả dụng** | Uptime ≥ 99.9%; có fallback khi Threads API down (hiển thị cache) |
| **Quyền riêng tư** | Tuân thủ GDPR & Nghị định 13/2023; cho phép user xóa toàn bộ dữ liệu đã sync |
| **Tương thích** | Web responsive, iOS ≥ 14, Android ≥ 8 |
| **i18n** | Hỗ trợ tiếng Việt và tiếng Anh ở giai đoạn 1 |

---
