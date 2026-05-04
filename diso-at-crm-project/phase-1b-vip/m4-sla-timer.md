# M4 — Đồng hồ SLA và Leo thang

> **Demo:** https://vcreator.demo.accesstrade.click/mockup/sla

---

## Mục đích

Module M4 đảm bảo cam kết của AccessTrade với creator được tuân thủ. Nếu AccessTrade hứa "VIP nhận phản hồi trong 4 giờ" mà thực tế là 24 giờ, niềm tin sẽ vỡ.

M4 đặt đồng hồ ngược cho mỗi tác vụ liên quan đến creator. Đồng hồ chạy theo thời gian thực, hiển thị nổi bật trên giao diện người phụ trách. Khi gần hết hạn, hệ thống cảnh báo. Khi vượt hạn, tự động leo thang lên cấp cao hơn.

Đây là tính năng mà Excel hoàn toàn không thể làm được. Trong Excel, không ai biết SLA của creator nào sắp vỡ cho đến khi đã muộn.

---

## Người dùng chính

- **Người phụ trách Care:** Thấy SLA timer trên mọi tác vụ trong My Queue
- **Trưởng nhóm Lead:** Theo dõi SLA Risk Dashboard tổng quan toàn đội, can thiệp khi cần
- **Senior Care:** Nhận leo thang khi tác vụ Care không kịp xử lý

---

## Câu chuyện sử dụng

@beautyquynh được phân công cho Linh lúc tám giờ sáng. M4 đặt đồng hồ SLA: "VIP Candidate ở giai đoạn Outreach (Process 2.2) phải được liên hệ trong 4 giờ".

Lúc mười một giờ, đồng hồ còn 1 giờ. M4 gửi cảnh báo trong giao diện cho Linh và email. Cô đang xử lý task khác, nhưng thấy badge đỏ.

Lúc 11:30, còn 30 phút. M4 leo thang: gửi thông báo cho Senior Care nếu Linh chưa hoàn thành. Linh thấy nguy cơ, ngừng task khác để xử lý ngay Quỳnh.

Lúc 11:45, Linh hoàn thành. M4 dừng đồng hồ, ghi nhận SLA tuân thủ.

Trường hợp khác: Trang đang phụ trách creator @reviewervn, SLA đã vượt hạn 2 tiếng. M4 tự động:
- Đánh dấu breach trong audit log
- Thông báo Lead Phương
- Tự động phân lại creator cho Senior Care nếu rule cấu hình như vậy
- Ghi vào dashboard SLA của Trang để Lead theo dõi xu hướng

Cuối tuần, Phương vào SLA Risk Dashboard, thấy tỷ lệ tuân thủ toàn đội 92%. Có một người phụ trách compliance dưới 85%, cô lên kế hoạch training cho người đó.

---

## Tính năng cốt lõi

### SLA cấu hình theo (state × tier)
- Mỗi cặp (lifecycle state, tier) có SLA riêng
- VIP Candidate ở Outreach: 4 giờ
- Normal ở Onboarding: 48 giờ
- Watchlist phản hồi tin nhắn: 24 giờ
- Cấu hình từ giao diện, không cần lập trình

### Đồng hồ event-driven
- Bắt đầu đếm khi creator vào state mới
- Dừng khi creator chuyển sang state tiếp theo
- Snooze được nếu có lý do hợp lệ (creator đang trong kỳ nghỉ, đang chờ document)
- Sau snooze hết hạn, đồng hồ tiếp tục

### Hệ thống cảnh báo ba ngưỡng
- **50% thời gian sử dụng:** Thông báo nhẹ cho người phụ trách
- **80% thời gian sử dụng:** Cảnh báo nổi bật cho người phụ trách + thông báo Lead
- **100% — vượt hạn:** Tự động leo thang lên Senior Care, ghi breach record, thông báo Lead

### Quy tắc leo thang
- Cấu hình ai nhận leo thang theo trường hợp
- Mặc định: Care vỡ → Senior Care; Senior vỡ → Lead
- Có thể tùy biến cho từng loại creator (VIP vỡ leo thẳng cho Lead)

### Snooze có lý do
- Cho phép dừng đồng hồ với lý do cụ thể
- Lý do phải nằm trong danh sách hợp lệ (ví dụ: creator nghỉ phép, chờ duyệt brand, document chưa đủ)
- Lưu lý do để audit

### Ghi nhận breach record
- Mỗi lần vượt SLA được lưu lại
- Phân tích pattern: creator nào hay vỡ, người phụ trách nào hay vỡ, state nào hay vỡ
- Phục vụ cải thiện quy trình và đào tạo

### SLA Risk Dashboard cho Lead
- Hiển thị tất cả creator đang có nguy cơ vỡ SLA
- Phân theo độ ưu tiên (critical, warning, safe)
- Heatmap theo người phụ trách
- Biểu đồ trend tuân thủ SLA 30 ngày

---

## Tích hợp

- **Với M2 Lifecycle:** SLA gắn với state hiện tại của creator
- **Với M3 Tier Engine:** SLA khác nhau theo tier
- **Với M5 Owner Workload:** Khi leo thang, tự động phân lại owner
- **Với M6 Task Console:** Mỗi task hiển thị SLA timer trực quan với màu sắc tương ứng
- **Với M14 Notification:** Hệ thống cảnh báo SLA breach gửi qua thông báo

---

## Đo lường thành công

- Tỷ lệ tuân thủ SLA toàn đội, mục tiêu trên 90%
- Tỷ lệ tuân thủ SLA cho VIP, mục tiêu trên 95%
- Số lần leo thang trong tháng, theo dõi để cải thiện capacity
- Thời gian trung bình từ khi vào state đến khi xử lý, mục tiêu giảm dần theo thời gian

---

## Liên quan trong demo

- **SLA Risk Dashboard (Lead view):** https://vcreator.demo.accesstrade.click/mockup/sla
- Trang demo có dải KPI bốn loại (Total / Critical / Warning / Safe) cho phép Lead lọc nhanh
- Heatmap theo người phụ trách hiển thị visualize ai có nhiều SLA risk nhất
- **My Queue:** https://vcreator.demo.accesstrade.click/mockup/console — mỗi creator trong queue có badge SLA màu (đỏ / cam / xanh)
