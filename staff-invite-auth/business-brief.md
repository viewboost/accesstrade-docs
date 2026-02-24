# Business Brief: Hệ thống Mời Nhân Viên & Tự Quản Lý Tài Khoản

**Dự án:** Techcombank Dashboard
**Ngày:** 2026-02-24
**Đối tượng:** Business, Operations, Product

---

## Vấn đề hiện tại là gì?

Hiện tại, khi cần thêm một nhân viên mới vào hệ thống, quy trình diễn ra thủ công và rời rạc:

1. Admin tự tạo mật khẩu ngẫu nhiên cho nhân viên
2. Gửi mật khẩu qua email ngoài hệ thống (Gmail, Zalo, v.v.)
3. Nhân viên mới đăng nhập bằng mật khẩu đó — **không có cách đổi mật khẩu**
4. Nếu nhân viên quên mật khẩu → phải liên hệ admin để reset thủ công

**Hệ quả:**
- Mật khẩu bị chia sẻ qua kênh không an toàn
- Admin mất thời gian xử lý các yêu cầu reset mật khẩu
- Nhân viên bị phụ thuộc hoàn toàn vào admin để xử lý tài khoản

---

## Chúng ta sẽ giải quyết như thế nào?

Xây dựng một luồng **mời nhân viên tự động qua email** kết hợp với tính năng **tự quản lý mật khẩu** ngay trên Dashboard.

---

## Tính năng cụ thể

### 1. Mời nhân viên qua email (Admin Panel)

Admin thực hiện ngay trên giao diện quản trị:

- Nhấn nút **"Mời nhân viên"**, điền email + tên + vai trò
- Hệ thống tự động gửi **email mời** tới nhân viên với đường link kích hoạt
- Link có hiệu lực trong **48 giờ**

Nhân viên nhận email → nhấn link → đặt mật khẩu lần đầu → tự động đăng nhập vào Dashboard.

**Lợi ích:**
- Không cần chia sẻ mật khẩu thủ công
- Mỗi nhân viên tự chọn mật khẩu của mình ngay từ đầu

### 1b. Mời hàng loạt (Admin Panel)

Admin có thể mời nhiều nhân viên cùng lúc:

- Nhấn nút **"Mời hàng loạt"**, nhập danh sách email + tên + vai trò (tối đa 50 người/lần)
- Hệ thống xử lý song song và gửi email mời cho từng người
- Hiển thị kết quả chi tiết: thành công / thất bại + lý do từng người

---

### 2. Trạng thái lời mời (Admin Panel)

Trên danh sách nhân viên, admin thấy được trạng thái từng người:

| Trạng thái | Ý nghĩa |
|------------|---------|
| 🟡 Chờ xác nhận | Đã gửi email, nhân viên chưa kích hoạt |
| 🟢 Đã kích hoạt | Nhân viên đã đặt mật khẩu và vào hệ thống |
| 🔴 Hết hạn | Link mời đã quá 48h, cần gửi lại |

Admin có thể **gửi lại email mời** (nút ✉️ trong hàng) cho các trường hợp hết hạn hoặc chưa nhận được. Token cũ tự động bị vô hiệu hóa, token mới 48h được cấp.

---

### 3. Đăng nhập trực tiếp trên Dashboard

Thay vì phải đăng nhập từ trang Admin rồi mới vào Dashboard, nhân viên giờ có thể:

- Đăng nhập trực tiếp bằng **email + mật khẩu** ngay trên trang Dashboard
- Có link "Quên mật khẩu?" để tự xử lý khi cần

---

### 4. Quên mật khẩu — tự xử lý (Dashboard)

Khi nhân viên quên mật khẩu:

1. Nhấn **"Quên mật khẩu?"** trên trang đăng nhập
2. Nhập email → nhận email hướng dẫn đặt lại mật khẩu
3. Nhấn link trong email (có hiệu lực **1 giờ**) → đặt mật khẩu mới
4. Đăng nhập bình thường

> Hệ thống **không tiết lộ** email nào tồn tại hay không — bảo vệ thông tin người dùng.

**Lợi ích:** Admin không cần can thiệp vào việc reset mật khẩu nữa.

---

### 5. Đổi mật khẩu chủ động (Dashboard — Trang Cài đặt)

Nhân viên có thể đổi mật khẩu bất kỳ lúc nào:

- Vào trang **Cài đặt → Bảo mật**
- Nhập mật khẩu hiện tại → nhập mật khẩu mới
- Lưu lại

---

## Ai dùng tính năng này?

| Người dùng | Tính năng sử dụng |
|------------|------------------|
| **Admin** | Mời nhân viên (đơn lẻ hoặc hàng loạt), xem trạng thái, gửi lại email |
| **Nhân viên mới** | Nhận email, đặt mật khẩu lần đầu, tự đăng nhập |
| **Nhân viên hiện tại** | Đổi mật khẩu, xử lý quên mật khẩu tự lập |

---

## Điều gì KHÔNG thay đổi?

- Admin Panel vẫn có hệ thống đăng nhập riêng (bảo mật tách biệt)
- Các tính năng hiện có trên Dashboard không bị ảnh hưởng
- Admin vẫn có thể reset mật khẩu nhân viên khi cần (ví dụ: trường hợp đặc biệt)

---

## Tóm tắt lợi ích

| Trước | Sau |
|-------|-----|
| Mật khẩu gửi qua kênh ngoài (không an toàn) | Email mời tự động, nhân viên tự đặt mật khẩu |
| Admin xử lý reset mật khẩu thủ công | Nhân viên tự reset qua email |
| Không biết nhân viên nào đã vào hệ thống chưa | Theo dõi trạng thái kích hoạt trực tiếp trên giao diện |
| Nhân viên phụ thuộc admin để quản lý tài khoản | Nhân viên tự chủ động quản lý tài khoản |

---

*Tài liệu kỹ thuật chi tiết: `plans/staff-invite-auth-selfservice.md`*
