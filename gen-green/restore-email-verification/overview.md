# Mở lại tính năng xác thực email — vCreator

> Trước đây phần xác thực email bị tạm ẩn vì chưa có key của dịch vụ gửi email. Nay key đã sẵn sàng, đợt này team bật lại để creator có thể xác minh email và hệ thống hiển thị rõ trạng thái "đã/chưa xác minh".

**Ngày:** 27/05/2026
**Trạng thái:** Đề xuất
**Đối tượng đọc:** Business, Ops, PM
**Phạm vi:** Trang **Tài khoản** (`account`) của vCreator frontend — phần thông tin email của creator

---

## Tại sao phải bật lại?

Khi xây dựng trang tài khoản, team đã làm sẵn phần xác thực email: creator nhập email, hệ thống gửi mã về hộp thư, creator nhập mã để xác minh. Email đã xác minh sẽ hiển thị nhãn xanh "Đã xác minh", chưa xác minh thì hiển thị nhãn vàng "Chưa xác minh".

Tuy nhiên ở giai đoạn đó **chưa có key của dịch vụ gửi email** (dịch vụ chịu trách nhiệm gửi mã xác thực tới hộp thư người dùng). Không có key thì mã không gửi đi được, creator bấm xác minh sẽ không nhận được gì → trải nghiệm bế tắc. Vì vậy team **tạm ẩn** toàn bộ phần xác thực để tránh người dùng bấm vào một nút "chết".

**1. Key đã sẵn sàng.**
Dịch vụ gửi email đã được cấu hình key, mã xác thực giờ gửi được tới hộp thư. Rào cản kỹ thuật khiến phải ẩn tính năng đã được gỡ.

**2. Cần biết email nào đáng tin.**
Hiện tại email creator nhập vào chỉ là một ô chữ, hệ thống không biết email đó có thật và thuộc về creator hay không. Khi cần liên hệ, gửi thông báo, hay đối soát danh tính, email chưa xác minh là một rủi ro.

→ Đợt này team giải quyết: **bật lại phần giao diện và luồng xác thực email trên trang tài khoản**, tận dụng dịch vụ gửi email đã có key.

---

## Có gì mới?

### 1. Ô email hiển thị trạng thái xác minh

Bên cạnh ô nhập email sẽ có một nhãn nhỏ cho biết email đã xác minh hay chưa:

- ✅ **Đã xác minh** — nhãn xanh, email đã được creator xác nhận sở hữu
- ⚠️ **Chưa xác minh** — nhãn vàng, kèm hành động để bắt đầu xác minh

### 2. Luồng xác minh bằng mã gửi qua email

Khi creator chọn xác minh:

1. Hệ thống gửi một mã (OTP) tới địa chỉ email creator vừa nhập
2. Creator mở hộp thư, lấy mã và nhập vào ô xác thực
3. Nhập đúng mã → email chuyển sang trạng thái "Đã xác minh"

Luồng này tận dụng đúng dịch vụ gửi email vừa được cấp key.

### 3. Dọn lại phần code đã ẩn

Phần xác thực trước đây bị gỡ/ẩn khỏi giao diện. Đợt này team khôi phục lại đúng vị trí cũ trên trang tài khoản, đảm bảo nhất quán với phần backend đã sẵn sàng.

---

## Chưa có gì (nhưng sẽ cân nhắc sau)

- **Bắt buộc xác minh email mới được dùng tính năng X** — đợt này chỉ hiển thị trạng thái và cho phép xác minh, chưa chặn (gate) bất kỳ chức năng nào theo trạng thái email. Sẽ bàn riêng nếu nghiệp vụ cần.
- **Xác minh số điện thoại** — phần điện thoại hiện vẫn đang ẩn, không nằm trong đợt này.

Các mục này phụ thuộc nhu cầu thực tế — cứ phản hồi, team sẽ làm tiếp.

---

## Lợi ích kỳ vọng

### Cho người dùng
- ✅ Biết rõ email của mình đã được xác minh hay chưa, ngay trên trang tài khoản
- ✅ Tự xác minh email một cách đơn giản qua mã gửi về hộp thư

### Cho hệ thống
- ✅ Phân biệt được email đáng tin (đã xác minh) và email chưa xác minh
- ✅ Giao diện khớp với backend đã sẵn sàng, không còn phần "chết" bị ẩn

### Cho vận hành
- ✅ Email đã xác minh giúp việc liên hệ, gửi thông báo, đối soát danh tính tin cậy hơn

---

## Chi phí và rủi ro

### Rủi ro & cách xử lý

| Rủi ro | Mức độ | Cách xử lý |
|--------|--------|------------|
| Mã xác thực không tới hộp thư (vào spam, trễ) | Trung bình | Cho phép gửi lại mã; ghi rõ hướng dẫn kiểm tra spam |
| Creator nhập sai/nhiều lần mã | Thấp | Giới hạn số lần thử và thời gian hiệu lực của mã |
| Dịch vụ gửi email lỗi/key hết hạn | Thấp | Theo dõi tỉ lệ gửi thành công; có cảnh báo khi gửi thất bại |

---

## Phạm vi không ảnh hưởng

Tài liệu này **không thay đổi**:
- Các thông tin khác trên trang tài khoản (tên hiển thị, giới tính, ngày sinh, ảnh đại diện)
- Phần xác minh số điện thoại (vẫn đang ẩn)
- Luồng đăng nhập/đăng ký hiện có

---

## Tài liệu liên quan

- **Yêu cầu chi tiết:** [`prd-restore-email-verification-2026-05-27.md`](./prd-restore-email-verification-2026-05-27.md) — FR/NFR + acceptance criteria cho dev/PM
- **Code liên quan:** `vcreator/frontend/src/pages/account/components/form/index.tsx` — ô email hiện tại (chưa có xác thực)

---

*Có thắc mắc, cứ phản hồi qua team vCreator.*
