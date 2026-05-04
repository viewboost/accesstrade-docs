# M13 — Đa Thuê bao và Phân quyền

> **Demo:** Phân quyền hiển thị trong Lead view tại https://vcreator.demo.accesstrade.click/mockup/ams/am-phuong

---

## Mục đích

Module M13 là tầng kiểm soát truy cập của toàn bộ CRM. Nó quyết định ai được thấy gì, ai được làm gì.

Trong AccessTrade có nhiều vai trò: Creator Care, Senior Care, Lead, BD, Compliance, Admin. Mỗi vai trò có nhu cầu thông tin khác nhau và có ranh giới quyền hạn khác nhau. Một người phụ trách Care chỉ nên thấy creator của mình, không nên thấy creator của đồng nghiệp. Lead thấy tất cả. Compliance thấy creator có flag nhưng không can thiệp vận hành.

Module này cũng là nền móng cho việc mở rộng sang các thuê bao bên ngoài trong tương lai (mặc dù trong bốn tháng đầu chưa cần). Nếu xây tốt từ đầu, việc mở rộng sau này sẽ không phải làm lại.

---

## Người dùng chính

- **Admin AccessTrade:** Cấu hình vai trò, gán quyền cho từng người
- **Tất cả người dùng khác:** Chịu ảnh hưởng của phân quyền nhưng không tương tác trực tiếp với module

---

## Câu chuyện sử dụng

Admin AccessTrade thiết lập sáu vai trò chuẩn: Creator Care, Senior Care, Lead, BD, Compliance, Admin. Mỗi vai trò có tập quyền cụ thể.

Linh đăng nhập với vai trò Senior Care. Hệ thống hiển thị bốn mươi bảy creator của cô trên Task Console. Cô không thấy creator của Trang hay Hiếu. Khi cô vào trang Reports, cô chỉ thấy KPI cá nhân, không thấy KPI toàn đội.

Phương đăng nhập với vai trò Lead. Cô thấy tất cả creator của tất cả người phụ trách. Trên trang Reports, cô thấy dashboard tổng quan toàn đội. Cô có thể vào trang AM Detail của bất kỳ ai để review hiệu suất.

BD Đức đăng nhập, anh thấy danh sách creator được đánh dấu phù hợp campaign anh đang phụ trách, không thấy toàn bộ pool. Anh có quyền tạo BD Request (sẽ có ở Giai đoạn 2) nhưng không thay đổi tier creator được.

Bảo từ Compliance vào, anh thấy danh sách creator có flag rủi ro, có thể đọc audit log mọi tương tác, nhưng không thể chỉnh sửa creator hoặc gửi tin nhắn.

---

## Tính năng cốt lõi

### Mô hình vai trò chuẩn
- **Creator Care:** Quản lý creator được phân công, gửi tin nhắn, cập nhật lifecycle
- **Senior Care:** Quyền giống Care + ưu tiên VIP Candidate
- **Lead:** Quyền xem tất cả creator của đội, override decision, cấu hình quy tắc M5
- **BD:** Quyền xem creator phù hợp campaign của mình, tạo BD Request (Giai đoạn 2)
- **Compliance:** Quyền đọc audit log, gắn flag rủi ro, không can thiệp vận hành
- **Admin:** Quyền cao nhất, quản lý vai trò, audit toàn hệ thống

### Phân quyền theo cấp độ dữ liệu
- Mỗi creator chỉ hiển thị cho người phụ trách hiện tại + Lead + Admin
- Compliance thấy thông tin creator nhưng không có quyền thao tác
- BD thấy creator được tag thuộc campaign của mình

### Nhật ký kiểm toán toàn hệ thống
- Mọi thao tác (xem, sửa, xóa, gửi) được lưu lại
- Lưu thông tin: ai, khi nào, làm gì, trên đối tượng nào
- Phục vụ audit, compliance, điều tra sự cố

### Xác thực và quản lý phiên đăng nhập
- Đăng nhập bằng email công ty AccessTrade
- Tích hợp với hệ thống xác thực hiện có (nếu có)
- Quản lý phiên: đăng xuất sau X giờ không hoạt động
- Hỗ trợ xác thực hai yếu tố cho vai trò Admin và Lead

### Sẵn sàng cho mở rộng tương lai
- Cấu trúc dữ liệu phân tách rõ ràng theo thuê bao
- Khi cần mở rộng cho brand external (như TCB, VinFast tự đăng nhập xem dashboard riêng), không cần refactor
- Trong bốn tháng đầu chỉ AccessTrade là thuê bao duy nhất

---

## Tích hợp

- **Với mọi module khác:** Mọi truy vấn dữ liệu đều đi qua tầng phân quyền của M13
- **Với hệ thống đăng nhập AccessTrade:** Single sign-on (nếu có)
- **Với M14 Notification:** Phân quyền quyết định ai được nhận thông báo nào

---

## Đo lường thành công

- Tỷ lệ vi phạm phân quyền (truy cập trái phép), mục tiêu 0
- Thời gian thiết lập tài khoản mới cho người phụ trách, mục tiêu dưới 5 phút
- Tỷ lệ audit log đầy đủ (mọi thao tác đều được ghi), mục tiêu 100%

---

## Liên quan trong demo

Phân quyền không có giao diện riêng để demo, nhưng được thể hiện qua việc khác nhau giữa các view:

- **My Queue (Care view):** https://vcreator.demo.accesstrade.click/mockup/console — chỉ hiển thị creator của một người phụ trách
- **AM Detail (Lead view):** https://vcreator.demo.accesstrade.click/mockup/ams/am-phuong — hiển thị tổng quan đội
- **Reports Dashboard:** https://vcreator.demo.accesstrade.click/mockup/dashboard — chỉ Lead và Admin thấy được trang này
