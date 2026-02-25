# Business Brief: Hệ thống Mời Nhân Viên & Tự Quản Lý Tài Khoản

**Dự án:** Techcombank
**Ngày:** 2026-02-24
**Đối tượng:** Business, Operations, Product

---

## Vấn Đề Cốt Lõi — Techcombank Không Thể Onboard Nhân Viên

**Techcombank hiện tại không có cách nào đưa nhân viên vào hệ thống một cách an toàn và tự lập.**

Vấn đề nằm ở **Admin Portal** — nơi quản lý toàn bộ tài khoản nhân viên. Admin Portal không có luồng onboarding chuẩn: không có cơ chế mời, không có cách nhân viên tự đặt mật khẩu, không có cách tự xử lý khi quên mật khẩu.

Hệ quả thực tế:

1. Admin tự tạo mật khẩu ngẫu nhiên cho nhân viên
2. Gửi mật khẩu ra ngoài qua Gmail, Zalo, hoặc kênh tương tự — **ngoài tầm kiểm soát của hệ thống**
3. Nhân viên đăng nhập bằng mật khẩu đó và **không có cách đổi**
4. Khi quên mật khẩu → mắc kẹt, phải nhờ admin reset thủ công

Kết quả: mật khẩu tài khoản nội bộ đang lưu hành qua các kênh không kiểm soát được, và mọi sự cố tài khoản đều phụ thuộc vào admin.

> **Techcombank yêu cầu giải quyết vấn đề này trước khi có thể triển khai hệ thống cho toàn bộ đội ngũ nhân viên.**

---

## Chúng ta sẽ giải quyết như thế nào?

Xây dựng luồng **mời nhân viên tự động qua email** và tính năng **tự quản lý mật khẩu** trực tiếp trên Admin Portal.

---

## Tính năng cụ thể

### 1. Mời nhân viên qua email

Admin thực hiện ngay trên giao diện quản trị:

- Nhấn nút **"Mời nhân viên"**, điền email + tên + vai trò
- Hệ thống tự động gửi **email mời** tới nhân viên với đường link kích hoạt
- Link có hiệu lực trong **48 giờ**

Nhân viên nhận email → nhấn link → đặt mật khẩu lần đầu → tự động đăng nhập vào hệ thống.

**Lợi ích:**
- Không cần chia sẻ mật khẩu thủ công
- Mỗi nhân viên tự chọn mật khẩu của mình ngay từ đầu

### 1b. Mời hàng loạt

Admin có thể mời nhiều nhân viên cùng lúc:

- Nhấn nút **"Mời hàng loạt"**, nhập danh sách email + tên + vai trò (tối đa 50 người/lần)
- Hệ thống xử lý song song và gửi email mời cho từng người
- Hiển thị kết quả chi tiết: thành công / thất bại + lý do từng người

---

### 2. Trạng thái lời mời

Trên danh sách nhân viên, admin thấy được trạng thái từng người:

| Trạng thái | Ý nghĩa |
|------------|---------|
| 🟡 Chờ xác nhận | Đã gửi email, nhân viên chưa kích hoạt |
| 🟢 Đã kích hoạt | Nhân viên đã đặt mật khẩu và vào hệ thống |
| 🔴 Hết hạn | Link mời đã quá 48h, cần gửi lại |

Admin có thể **gửi lại email mời** cho các trường hợp hết hạn hoặc chưa nhận được. Token cũ tự động bị vô hiệu hóa, token mới 48h được cấp.

---

### 3. Quên mật khẩu — tự xử lý

Khi nhân viên quên mật khẩu:

1. Nhấn **"Quên mật khẩu?"** trên trang đăng nhập
2. Nhập email → nhận email hướng dẫn đặt lại mật khẩu
3. Nhấn link trong email (có hiệu lực **1 giờ**) → đặt mật khẩu mới
4. Đăng nhập bình thường

> Hệ thống **không tiết lộ** email nào tồn tại hay không — bảo vệ thông tin người dùng.

**Lợi ích:** Admin không cần can thiệp vào việc reset mật khẩu nữa.

---

### 4. Đổi mật khẩu chủ động

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

- Các tính năng hiện có không bị ảnh hưởng
- Admin vẫn có thể reset mật khẩu nhân viên thủ công khi cần xử lý trường hợp đặc biệt

---

## Tóm tắt lợi ích

| Trước | Sau |
|-------|-----|
| Mật khẩu gửi qua kênh ngoài (không an toàn) | Email mời tự động, nhân viên tự đặt mật khẩu |
| Admin xử lý reset mật khẩu thủ công | Nhân viên tự reset qua email |
| Không biết nhân viên nào đã vào hệ thống chưa | Theo dõi trạng thái kích hoạt trực tiếp trên giao diện |
| Nhân viên phụ thuộc admin để quản lý tài khoản | Nhân viên tự chủ động quản lý tài khoản |

---

*Tài liệu kỹ thuật chi tiết: [prd-staff-invite-auth-2026-02-24.md](./prd-staff-invite-auth-2026-02-24.md)*
