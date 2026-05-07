# M6 — Hộp thoại Tác vụ

> **Demo:** https://vcreator.demo.accesstrade.click/mockup/console

---

## Mục đích

Module M6 là giao diện chính mà người phụ trách Care làm việc tám tiếng mỗi ngày. Đây là sản phẩm thay thế trực tiếp cho file Excel mà họ đang dùng. Nếu M6 không tốt hơn Excel rõ rệt, họ sẽ không chuyển đổi.

Mục tiêu của M6 là biến công việc chăm sóc creator thành một danh sách tác vụ rõ ràng, có thứ tự ưu tiên, có thể bấm và xử lý lần lượt. Người phụ trách mở M6 vào buổi sáng, biết ngay hôm nay cần làm gì, không phải tự nghĩ.

---

## Người dùng chính

- Người phụ trách Care, Senior Care: tất cả thao tác hằng ngày diễn ra trên đây
- BD: phiên bản BD-specific để xử lý các creator đặc biệt cho campaign
- Compliance: phiên bản Compliance-specific để duyệt các trường hợp gắn cờ

---

## Câu chuyện sử dụng

Tám giờ sáng, Linh đăng nhập CRM. Trang đầu tiên cô thấy là My Queue, hộp thoại tác vụ của riêng cô.

Phía trên là dải KPI: cô có 47 creator active, 12 trong số đó là VIP, 1 đang có nguy cơ vỡ SLA dưới hai giờ, GMV tuần này là 284 triệu, tỷ lệ tuân thủ SLA của cô là 94%.

Bên dưới là danh sách creator được sắp xếp theo độ ưu tiên. Đầu tiên là @beautyquynh — VIP Candidate, SLA chỉ còn 1 giờ 24 phút, có ghi chú "Brand Innisfree đề cử". Cô bấm vào, mở trang chi tiết creator, xem nhanh hồ sơ, viết phản hồi qua Conversation Thread.

Cô bấm tab "Filter VIP" để chỉ xem mười hai VIP của mình. Xử lý xong nhóm này trong khoảng một tiếng.

Buổi chiều, cô vào tab "Watchlist" để xem ba creator có dấu hiệu inactive. Cô nhắn tin nhắc nhở từng người.

Cô không bao giờ phải mở Excel hoặc Zalo cá nhân để tra cứu thông tin. Mọi thứ ở trong M6.

---

## Tính năng cốt lõi

### My Queue — Hàng đợi cá nhân
- Hiển thị toàn bộ creator dưới quyền người phụ trách hiện tại
- Sắp xếp mặc định theo độ ưu tiên (SLA breach risk → tier → last activity)
- Cho phép thay đổi cách sắp xếp

### Dải KPI cá nhân
- Số creator đang quản lý
- Số VIP Candidate
- Số creator có nguy cơ vỡ SLA
- GMV trong tuần
- Tỷ lệ tuân thủ SLA

### Hệ thống lọc và phân loại
- Lọc theo tier: VIP, Gold + Potential, Normal, Watchlist
- Lọc theo trạng thái lifecycle
- Lọc theo ngành creator
- Tìm kiếm theo handle, tên, hoặc ngành

### Hành động hàng loạt
- Chọn nhiều creator cùng lúc
- Phân công lại owner hàng loạt
- Gắn thẻ hàng loạt
- Gửi tin nhắn template hàng loạt

### Phím tắt cho người dùng power
- ⌘K mở thanh tìm kiếm nhanh
- Phím lên xuống điều hướng
- Phím Enter mở trang chi tiết creator
- Phím A để phân công, T để đổi tier
- Giúp người phụ trách kinh nghiệm thao tác cực nhanh

### View đã lưu
- Cho phép người phụ trách lưu các bộ lọc thường dùng
- Ví dụ: "VIP cần action hôm nay", "SLA dưới 4 giờ"
- Truy cập nhanh vào view yêu thích

### Hành động ngay trong dòng
- Không cần rời khỏi M6 để thao tác
- Bấm vào creator hiển thị tác vụ inline
- Có thể tag, comment, snooze ngay tại dòng creator

### Phiên bản cho các vai trò khác
- BD Console: tập trung vào creator đang trong campaign
- Compliance Console: tập trung vào creator có flag cảnh báo
- Lead Console: tổng quan toàn đội (kết hợp với M5)

---

## Tích hợp

- **Với M2 Lifecycle:** Mỗi creator trong queue có trạng thái lifecycle hiển thị
- **Với M3 + M4 (Giai đoạn 1B):** Tier badge và SLA timer hiển thị nổi bật
- **Với M5 Owner Workload:** Queue chỉ hiển thị creator của người phụ trách hiện tại
- **Với M7 Outreach:** Bấm "Send message" mở Conversation Thread mà không rời M6
- **Với M14 Notification:** Khi có tác vụ mới hoặc SLA gần vỡ, hiển thị badge realtime

---

## Đo lường thành công

- Tỷ lệ áp dụng của đội Creator Care, mục tiêu 100% sau bốn tuần ra mắt
- Thời gian trung bình xử lý một creator (từ mở đến hoàn thành tác vụ), mục tiêu giảm 50% so với Excel
- Năng suất xử lý mỗi người phụ trách (số creator/ngày), mục tiêu tăng gấp 2-3 lần
- Mức độ hài lòng người dùng (khảo sát hằng tháng), mục tiêu trên 4/5

---

## Liên quan trong demo

- **My Queue:** https://vcreator.demo.accesstrade.click/mockup/console
- Trên trang demo, ở đầu trang có "DEMO · view as" cho phép chuyển nhanh giữa các góc nhìn của các người phụ trách khác nhau
- Bấm vào một creator trong queue để mở trang chi tiết creator
- Bấm tab filter VIP/Gold/Normal/Watchlist để thấy hệ thống lọc
