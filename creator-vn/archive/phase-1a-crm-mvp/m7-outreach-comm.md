# M7 — Lưu trữ Trao đổi

> **Demo:** https://vcreator.demo.accesstrade.click/mockup/conversations/conv-beautyquynh-1

---

## Mục đích

Module M7 đảm bảo mọi tin nhắn, email, cuộc gọi giữa người phụ trách và creator được lưu tập trung trong CRM. Đây là điều kiện tiên quyết cho hai mục tiêu lớn: chất lượng chăm sóc đồng nhất, và bảo vệ tài sản quan hệ khi nhân sự thay đổi.

Hiện tại đa số đội Creator Care liên hệ creator qua Zalo cá nhân. Khi người phụ trách nghỉ việc, toàn bộ lịch sử trao đổi đi theo họ. Creator hỏi "anh chị nào của AccessTrade từng nhắn em" — không ai biết. Đây là rủi ro lớn cho doanh nghiệp.

M7 thay thế Zalo cá nhân bằng Zalo OA chính thức của AccessTrade, đảm bảo mọi tin nhắn ở lại trong hệ thống công ty mãi mãi.

---

## Người dùng chính

- Người phụ trách Care và Senior Care: gửi và nhận tin nhắn với creator hằng ngày
- Trưởng nhóm: review chất lượng tương tác để training
- Compliance: audit khi có tranh chấp

---

## Câu chuyện sử dụng

Linh nhận tác vụ "Liên hệ @beautyquynh — VIP Candidate" từ M6. Cô bấm "Send message", M7 mở Conversation Thread với @beautyquynh.

Nếu đây là lần đầu, hệ thống tự khởi tạo conversation mới. Nếu đã có lịch sử, toàn bộ tin nhắn cũ hiển thị theo timeline.

Linh chọn một template từ thư viện: "VIP Candidate — Initial Outreach". Template tự điền thông tin cá nhân hóa: tên creator, số follower, ngành. Cô tinh chỉnh đôi câu rồi bấm Send.

Tin nhắn được gửi qua Zalo OA chính thức của AccessTrade. Quỳnh nhận tin trên Zalo, phản hồi sau hai tiếng. Phản hồi tự động vào lại Conversation Thread, Linh nhận thông báo.

Sau hai tuần, Linh đi nghỉ phép. Trang vào thay vẫn thấy toàn bộ lịch sử với @beautyquynh, không cần Linh chuyển bàn giao gì. Trang nhắn tiếp được ngay, mạch trao đổi liền lạc.

Sáu tháng sau, Linh chuyển công việc khác. Hà nhận @beautyquynh. Hà mở Conversation Thread, đọc lịch sử ba tháng trao đổi, hiểu được context, tiếp tục chăm sóc mượt mà. Quỳnh không cảm thấy bị bỏ rơi.

---

## Tính năng cốt lõi

### Conversation Thread đa kênh
- Lưu trữ tin nhắn từ Zalo OA, email, ghi chú cuộc gọi, tin nhắn trong app
- Hiển thị theo timeline thời gian
- Phân biệt rõ tin từ AccessTrade vs từ creator
- Có thể đính kèm file, hình ảnh

### Tích hợp Zalo OA chính thức
- Sử dụng tài khoản Zalo OA Business của AccessTrade, không phải Zalo cá nhân
- Tin nhắn gửi và nhận đều được sync vào CRM
- Webhook nhận phản hồi creator realtime
- Đảm bảo mọi tương tác ở lại trong hệ thống công ty

### Thư viện template
- Bộ template phân theo: ngành creator × tier × giai đoạn (initial outreach, follow-up, deal proposal, win-back)
- Template có biến cá nhân hóa: tên creator, follower count, deal phù hợp
- Trưởng nhóm có thể tạo và quản lý template chuẩn
- Người phụ trách có thể tinh chỉnh trước khi gửi

### Theo dõi phản hồi
- Trạng thái mỗi conversation: Active, Awaiting Response, No Response, Closed
- Tự động chuyển sang "No Response" sau X ngày không có phản hồi
- Tự động nhắc nhở người phụ trách follow-up

### Nhắc nhở tự động follow-up
- Nếu creator không phản hồi sau 3 ngày, hệ thống tạo task nhắc người phụ trách
- Cho phép tinh chỉnh khoảng thời gian follow-up theo tier

### Ghi chú cuộc gọi
- Khi gọi điện thoại creator, người phụ trách có thể ghi chú nhanh nội dung cuộc gọi vào Conversation Thread
- Đảm bảo cả tương tác offline cũng được lưu

### Audit log toàn diện
- Mọi tin nhắn được gắn timestamp, sender, channel
- Compliance có thể tra cứu khi có tranh chấp

### Chia sẻ context giữa các vai trò
- Khi BD cần biết creator đã được Care liên hệ ra sao trước khi gọi mời campaign
- Khi Compliance review tranh chấp
- Khi Lead training người phụ trách mới

---

## Tích hợp

- **Với Zalo OA Business:** Webhook và API gửi nhận tin nhắn
- **Với M1 Creator Identity:** Mỗi conversation gắn với một creator
- **Với M2 Lifecycle:** Khi conversation chuyển trạng thái (creator phản hồi đồng ý), tự cập nhật lifecycle
- **Với M5 Owner Workload:** Conversation thuộc về người phụ trách hiện tại
- **Với M14 Notification:** Khi có tin nhắn mới, người phụ trách được thông báo
- **Với M16 Relationship Vault (Giai đoạn 1B):** M7 là nguồn dữ liệu quan trọng nhất cho Relationship Capital

---

## Đo lường thành công

- Tỷ lệ tập trung hóa trao đổi vào hệ thống, mục tiêu trên 95%
- Thời gian phản hồi trung bình của người phụ trách, mục tiêu giảm 50%
- Số lượng template được sử dụng (theo dõi để tối ưu thư viện)
- Tỷ lệ creator phản hồi tin nhắn lần đầu, mục tiêu trên 60%

---

## Liên quan trong demo

- **Conversation Thread:** https://vcreator.demo.accesstrade.click/mockup/conversations/conv-beautyquynh-1
- Trên trang demo, có thể thấy lịch sử tin nhắn giữa Linh và Quỳnh, kênh Zalo OA, sidebar bên phải hiển thị context creator
- Bấm các thread khác trong sidebar trái để chuyển nhanh
- Khu vực bên trái có thư viện template, khu vực giữa là chat, khu vực bên phải là context creator
