# M2 — Vòng đời Quản lý đa luồng

> **Demo:** https://vcreator.demo.accesstrade.click/mockup/creators/cr-beautyquynh

---

## Mục đích

Module M2 là xương sống của CRM. Nó trả lời câu hỏi quan trọng nhất trong vận hành: "Mỗi creator đang ở bước nào của quy trình chăm sóc?"

Quy trình V2 mà AccessTrade đã thiết kế có bảy giai đoạn lớn, mỗi giai đoạn lại có nhiều bước nhỏ. Một creator có thể chạy đồng thời nhiều luồng (ví dụ vừa onboarding lần đầu, vừa tham gia campaign mới), không phải đi theo một đường thẳng.

Nếu không có M2, mỗi người phụ trách sẽ tự ghi nhớ trong đầu hoặc viết tay vào Excel, dẫn đến mất tracking, missed deadlines, và creator rơi qua các kẽ hở giữa các giai đoạn.

---

## Người dùng chính

- Người phụ trách Care: cập nhật trạng thái creator hằng ngày
- Trưởng nhóm: theo dõi tổng thể pipeline, phát hiện creator bị tắc ở giai đoạn nào
- Người phụ trách cấp cao: tập trung vào creator ở các giai đoạn cao (Active, Tiered)

---

## Câu chuyện sử dụng

Khi @beautyquynh đăng ký tại sự kiện ngày 7/5, M2 tự động đặt cô vào trạng thái "New" của Process 1 (Source & Qualify). Hệ thống biết đây là creator mới chưa được liên hệ.

Trong vòng năm phút sau, người phụ trách Linh được phân công và gửi tin nhắn chào mừng qua Zalo OA. M2 tự động chuyển trạng thái sang "Contacted".

Quỳnh phản hồi sau hai tiếng, đồng ý quan tâm. M2 chuyển sang "Applied" của Process 2. Linh review profile, approve. M2 chuyển sang "Approved" của Process 3.

Quỳnh hoàn tất setup tài khoản Shopee Affiliate. M2 chuyển sang "Setup Done", và "Ready" của Process 4. Creator này giờ sẵn sàng nhận campaign.

Khi cô tham gia campaign Innisfree đầu tiên, M2 đặt thêm một luồng song song "Campaign Active" cho cô. Cô vẫn đang ở "Ready" của onboarding, đồng thời "Publishing" của campaign. Hai trạng thái cùng tồn tại.

Trưởng nhóm Phương vào dashboard tổng quan, thấy có ba creator bị tắc ở "Applied" hơn năm ngày, đồng nghĩa người phụ trách quên approve. Cô nhắn nhở.

---

## Tính năng cốt lõi

### Bảy quy trình lớn theo V2
1. **Source & Qualify** — Phát hiện và đánh giá creator tiềm năng
2. **Outreach & Application** — Liên hệ và creator nộp hồ sơ
3. **Review & Platform Setup** — Duyệt hồ sơ và setup các tài khoản nền tảng
4. **Onboarding & Channel Strategy** — Hướng dẫn ban đầu và xây dựng chiến lược kênh
5. **Commerce Activation** — Kích hoạt thương mại, gửi sản phẩm, đăng nội dung
6. **Tracking & Care** — Theo dõi hiệu suất và chăm sóc liên tục
7. **Payout, Tiering & Loyalty** — Thanh toán, phân hạng và xây dựng lòng trung thành

### Trạng thái chính cho mỗi creator
- New (vừa vào hệ thống)
- Contacted (đã được liên hệ)
- Applied (đã nộp hồ sơ)
- Approved (đã được duyệt)
- Setup (đang hoàn tất setup nền tảng)
- Ready (sẵn sàng nhận campaign)
- Active.Publishing (đang đăng nội dung)
- Active.Tracking (đang theo dõi hiệu suất)
- Tiered (đã được phân hạng chính thức)
- Paused (tạm dừng do lý do nào đó)

### Quản lý đa luồng
- Một creator có thể có nhiều trạng thái cùng lúc
- Ví dụ: creator vừa Active trong một campaign, vừa đang Onboarding với brand pool mới
- Hệ thống hiển thị tất cả luồng song song trên trang chi tiết creator

### Quy tắc chuyển trạng thái
- Mỗi chuyển đổi có điều kiện cụ thể (ví dụ: chuyển từ Approved sang Setup yêu cầu form đầy đủ)
- Hệ thống tự động kiểm tra điều kiện trước khi cho phép chuyển
- Có thể chuyển manual (người phụ trách bấm) hoặc auto (event từ hệ thống ngoài)

### Chuyển trạng thái tự động từ event
- Khi Shopee report đơn hàng đầu tiên của creator, hệ thống tự chuyển sang Active.Tracking
- Khi creator hoàn thành form onboarding, tự chuyển sang Ready
- Giảm gánh nặng cho người phụ trách phải cập nhật thủ công

### Nhật ký kiểm toán
- Mọi thay đổi trạng thái được lưu lại: ai chuyển, khi nào, lý do
- Hữu ích khi audit và khi creator hỏi "tại sao tôi bị từ chối"

### Cấu hình từ giao diện
- Trưởng nhóm có thể điều chỉnh quy tắc trạng thái mà không cần lập trình
- Quy trình V2 có thể được tinh chỉnh theo thực tế vận hành

---

## Tích hợp

- **Với M1 Creator Identity:** Mỗi trạng thái gắn với một creator cụ thể
- **Với M5 Owner Workload:** Khi creator chuyển sang "Approved", tự động trigger phân công người phụ trách phù hợp giai đoạn tiếp theo
- **Với M6 Task Console:** Hàng đợi tác vụ được tạo từ trạng thái hiện tại của creator (ví dụ creator ở "Applied" tạo task "Review hồ sơ")
- **Với M4 SLA Timer (Giai đoạn 1B):** Mỗi trạng thái có thời hạn SLA riêng
- **Với ambassador.koc.com.vn:** Khi creator tham gia campaign mới, ambassador thông báo về CRM, M2 tạo luồng mới

---

## Đo lường thành công

- Tỷ lệ creator có trạng thái cập nhật trong vòng 24 giờ, mục tiêu trên 95%
- Số lượng creator bị tắc ở mỗi giai đoạn (theo dõi để tối ưu quy trình)
- Tỷ lệ chuyển đổi từ giai đoạn New đến Active, mục tiêu trên 50%
- Thời gian trung bình một creator đi từ New đến Tiered, mục tiêu dưới 30 ngày

---

## Liên quan trong demo

- **Trang chi tiết creator:** https://vcreator.demo.accesstrade.click/mockup/creators/cr-beautyquynh
- Trên trang chi tiết creator, phần "Lifecycle Timeline" hiển thị bảy giai đoạn của V2 với giai đoạn hiện tại được đánh dấu nổi bật
- **My Queue:** https://vcreator.demo.accesstrade.click/mockup/console — mỗi tác vụ trong queue đều xuất phát từ trạng thái lifecycle của creator
