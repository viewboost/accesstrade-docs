# Duyệt hồ sơ tự động

## 🎯 Mục tiêu tính năng

Tính năng **Duyệt hồ sơ tự động** giúp hệ thống tự động xét duyệt hồ sơ **Creator** theo bộ điều kiện do **Operations** cấu hình nhằm:

- Giảm tải thao tác duyệt thủ công.
- Chuẩn hoá tiêu chí theo từng **Partner** và **Nguồn** (YouTube/TikTok/Facebook…).
- Đảm bảo chất lượng hồ sơ đầu vào.

---

## 🧭 Điều kiện cần trước khi thao tác

- Tài khoản có quyền **Operations/Admin**.
- Đã có hồ sơ Creator được đồng bộ dữ liệu (subscribe, view, số video… tuỳ nền tảng).
- Xác định rõ phạm vi áp dụng:
    - **Partner** áp dụng (ví dụ: Techcombank).
    - **Nguồn** áp dụng (ví dụ: YouTube).

---

## 🧩 Vị trí tính năng trên hệ thống

Vào menu: **Hồ sơ** → tab **Điều kiện duyệt tự động**.

Tại đây bao gồm:

- Nút **Thêm điều kiện**.
- Danh sách các điều kiện đã tạo.
- Cột **Trạng thái** và nút gạt **ON/OFF** để bật/tắt áp dụng tự động.

---

## ⚙️ Tạo mới điều kiện duyệt tự động

1. Vào **Hồ sơ** → **Điều kiện duyệt tự động**.
2. Chọn **Thêm điều kiện**.
3. Nhập/Chọn các trường trong form:
- **Partner**: Chọn nhãn hàng/đối tác áp dụng điều kiện (bắt buộc).
- **Nguồn**: Chọn nền tảng áp dụng (bắt buộc), ví dụ **YouTube**.
- **Số subscribe tối thiểu**: Ngưỡng subscribers tối thiểu.
- **Số video tối thiểu**: Ngưỡng số lượng video tối thiểu.
- **Số view tối thiểu**: Ngưỡng lượt xem tối thiểu.
- **Trạng thái nhân viên**: Lọc theo trạng thái (ví dụ: **Không phải nhân viên**).
- **Yêu cầu cập nhật Demographics**: Bật nếu bắt buộc Creator phải có Demographics đầy đủ thì mới được duyệt.
1. Nhấn **Cập nhật** để lưu.

---

## ✏️ Chỉnh sửa điều kiện

1. Trong danh sách điều kiện, nhấn biểu tượng **chỉnh sửa (✏️)**.
2. Popup **Chỉnh sửa điều kiện hồ sơ** xuất hiện.
3. Cập nhật các ngưỡng/tuỳ chọn cần thay đổi.
4. Nhấn **Cập nhật** để lưu hoặc **Huỷ** để thoát.

---

## 🔛 Bật/Tắt áp dụng tự động (ON/OFF)

- Gạt **ON**: Điều kiện bắt đầu được hệ thống dùng để tự động duyệt **cả hồ sơ mới và hồ sơ cũ khi được cập nhật dữ liệu**.
- Gạt **OFF**: Tạm dừng áp dụng điều kiện, hồ sơ sẽ không còn được auto-approve theo rule này.

Khuyến nghị vận hành:

- Chỉ bật **ON** sau khi đã rà soát kỹ ngưỡng tối thiểu.
- Khi thay đổi tiêu chí, nên thao tác theo quy trình: **OFF → chỉnh sửa → ON** để kiểm soát rủi ro.

---

## ✅ Logic duyệt (Operations cần nắm)

Hồ sơ sẽ được hệ thống duyệt tự động khi **thoả toàn bộ điều kiện** của rule đang bật, thường gồm:

- Đúng **Partner**.
- Đúng **Nguồn**.
- Thỏa các ngưỡng tối thiểu (**subscribe / video / view**).
- Thỏa **Trạng thái nhân viên**.
- Nếu bật **Yêu cầu cập nhật Demographics** thì hồ sơ phải có dữ liệu demographics **hợp lệ/đầy đủ**.

---

## 🧪 Checklist kiểm tra sau khi cấu hình

- Rule đã **lưu thành công** (không lỗi validation).
- Rule đang ở trạng thái **Đang hoạt động**.
- Nút gạt đang **ON**.
- Test nhanh bằng hồ sơ mẫu:
    - 01 hồ sơ **đạt**.
    - 01 hồ sơ **không đạt** (thiếu 01 tiêu chí) để xác nhận hệ thống không duyệt nhầm.

---

## ⚠️ Lỗi thường gặp & cách xử lý nhanh

- **Hồ sơ không được duyệt dù đã bật ON**
    - Kiểm tra hồ sơ có đúng **Partner/Nguồn** không.
    - Kiểm tra dữ liệu hồ sơ có được cập nhật mới nhất (subscribe/view/video) không.
    - Nếu bật Demographics: kiểm tra Creator đã nhập/đồng bộ demographics chưa.
- **Duyệt nhầm nhiều hồ sơ**
    - Ngưỡng tối thiểu đặt quá thấp.
    - Rule áp dụng sai Partner/Nguồn.
    - Có nhiều rule cùng phạm vi: cần rà soát rule trùng/chồng chéo.

---

## 📌 Khuyến nghị cấu hình chuẩn cho Operations

- Mỗi **Partner + Nguồn** nên có **01 rule chính** để tránh chồng chéo.
- Thiết lập ngưỡng tối thiểu theo “mức sàn”, các trường hợp đặc biệt xử lý bằng duyệt thủ công.
- Bật **Yêu cầu cập nhật Demographics** nếu Partner cần tệp audience rõ ràng.

---