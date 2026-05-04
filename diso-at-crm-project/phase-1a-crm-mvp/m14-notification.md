# M14 — Thông báo và Cảnh báo

> **Demo:** Hệ thống thông báo hiển thị qua badge trên https://vcreator.demo.accesstrade.click/mockup/console

---

## Mục đích

Module M14 đảm bảo người phụ trách không bao giờ bỏ lỡ tác vụ quan trọng. Trong môi trường có hàng nghìn creator, không ai có thể nhớ hết những việc cần làm. M14 đóng vai trò trợ lý cá nhân, nhắc nhở đúng lúc.

Thông báo phải đến đúng người, đúng thời điểm, qua đúng kênh. Spam quá nhiều sẽ bị bỏ qua. Thiếu thông báo sẽ làm mất việc. Cân bằng này là bài toán chính của M14.

Trong giai đoạn này, M14 hỗ trợ thông báo trong giao diện ứng dụng và qua email. Các kênh khác như Slack có thể bổ sung sau nếu cần.

---

## Người dùng chính

- Tất cả người dùng CRM (Care, Senior Care, Lead, BD, Compliance) đều nhận thông báo
- Admin cấu hình quy tắc thông báo

---

## Câu chuyện sử dụng

Tám giờ sáng, Linh mở email. Cô có một email digest từ AccessTrade CRM: "Hôm nay bạn có 3 task mới, 1 SLA gần vỡ, 2 creator phản hồi tin nhắn".

Cô đăng nhập CRM, thấy badge số 6 trên icon thông báo trên đầu trang. Cô bấm vào, xem danh sách: hai creator phản hồi, một creator chuyển trạng thái Approved, ba task mới được phân.

Trong khi cô làm việc, một thông báo realtime hiện ra góc dưới phải: "@beautyquynh vừa phản hồi tin nhắn của bạn". Cô bấm vào, được chuyển ngay đến Conversation Thread.

Mười một giờ, một creator của cô có SLA dưới 30 phút. Hệ thống gửi cảnh báo nổi bật trong giao diện và email. Cô xử lý ngay.

Mười hai giờ, cô đi ăn trưa. Trong giờ ăn, cô tắt thông báo realtime, chỉ nhận thông báo qua email. Khi quay lại, cô đọc email digest cho khoảng thời gian vừa qua.

---

## Tính năng cốt lõi

### Hai kênh thông báo
- **Trong giao diện ứng dụng:** Badge số trên header, panel thông báo dropdown, toast realtime góc màn hình
- **Email:** Email tức thời cho việc khẩn cấp, email digest hằng ngày cho tổng kết

### Quy tắc subscription thông minh
- Người phụ trách Care nhận thông báo về creator của mình (phản hồi, lifecycle change, SLA breach)
- Senior Care nhận thêm thông báo VIP signal
- Lead nhận thông báo tổng quan đội (creator vỡ SLA, anomaly)
- Compliance nhận thông báo creator có flag rủi ro

### Chế độ digest
- Cho phép người dùng chọn nhận tổng hợp thay vì realtime
- Daily digest gửi vào sáng đầu ngày làm việc
- Weekly digest cho Lead xem tổng quan tuần
- Giảm spam và mệt mỏi thông báo

### Tùy chỉnh kênh nhận
- Mỗi loại thông báo có thể chọn kênh: in-app, email, hoặc cả hai
- Người dùng tự cấu hình theo sở thích
- Mặc định ưu tiên in-app cho thông báo bình thường, cả hai cho khẩn cấp

### Thông báo realtime cho việc khẩn cấp
- SLA gần vỡ (dưới 1 giờ)
- Creator VIP phản hồi tin nhắn
- Compliance flag mới
- Anomaly từ Performance Care (Giai đoạn 1B)

### Lịch sử thông báo
- Lưu lại tất cả thông báo đã gửi
- Người dùng có thể xem lại các thông báo đã đọc
- Hữu ích khi cần tra cứu thông tin đã từng nhận

### Mute và Snooze
- Cho phép tạm tắt thông báo trong khoảng thời gian (ví dụ giờ ăn trưa)
- Snooze một thông báo cụ thể đến thời gian sau
- Sau khi snooze hết, thông báo quay lại

---

## Tích hợp

- **Với M2 Lifecycle:** Khi creator chuyển trạng thái, gửi thông báo cho người phụ trách
- **Với M4 SLA Timer (Giai đoạn 1B):** Khi SLA gần vỡ, gửi cảnh báo
- **Với M5 Owner Workload:** Khi có creator mới được phân công, gửi thông báo
- **Với M7 Outreach:** Khi creator phản hồi tin nhắn, gửi thông báo
- **Với M11 Performance Care (Giai đoạn 1B):** Khi phát hiện anomaly, gửi cảnh báo
- **Với M16 Relationship Vault (Giai đoạn 1B):** Khi có alert anti-poach, gửi cho Lead

---

## Đo lường thành công

- Tỷ lệ thông báo được mở/đọc, mục tiêu trên 70%
- Tỷ lệ creator có người phụ trách phản hồi trong vòng SLA, mục tiêu trên 90%
- Số lượng người dùng tùy chỉnh notification preference (cho thấy họ thực sự dùng)
- Tỷ lệ unsubscribe (theo dõi để tránh spam)

---

## Liên quan trong demo

Hệ thống thông báo không có trang riêng để demo, nhưng được thể hiện qua các badge:

- **My Queue:** https://vcreator.demo.accesstrade.click/mockup/console — số "47 active queue", "1 critical SLA" là kết quả của hệ thống tracking + notification
- **SLA Risk Dashboard:** https://vcreator.demo.accesstrade.click/mockup/sla — Lead view dùng dữ liệu từ SLA Timer + Notification
