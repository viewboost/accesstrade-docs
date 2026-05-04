# Dự án CRM Creator AccessTrade — Diso đồng hành

> **Trang demo:** https://vcreator.demo.accesstrade.click/
> **Cập nhật:** 2026-05-01
> **Vai trò tài liệu:** Mô tả nghiệp vụ tổng quan từng module dành cho người không chuyên kỹ thuật. File chi tiết task và ước lượng thời gian sẽ được làm riêng sau.

---

## Mục tiêu dự án

Xây dựng hệ thống CRM nội bộ cho đội Creator Care của AccessTrade, đặt trên nền at-core. Hệ thống tiếp nhận creator từ sự kiện 7 tháng 5, chăm sóc theo quy trình chuẩn V2, và mở rộng sang tìm kiếm creator chủ động trên mạng xã hội.

Lộ trình bốn tháng được chia thành bốn giai đoạn rõ ràng. Mỗi giai đoạn có phạm vi cụ thể, mục tiêu đo lường được và các module triển khai song song hoặc tuần tự.

---

## Bốn giai đoạn triển khai

### Giai đoạn 0 — Cổng đăng ký Sự kiện
**Thời gian:** Tuần 1 đến Tuần 2 (1/5 → 14/5/2026)
**Mục tiêu:** Sẵn sàng cho sự kiện Creator For Vietnam ngày 7/5. Thu hút trên 500 creator đăng ký trực tiếp tại sự kiện, mỗi creator có trải nghiệm "wow" sau khi đăng ký để giữ chân trong 14 ngày đầu.

**Các surface chính:** Trang giới thiệu sự kiện, biểu mẫu đăng ký ba bước, trang chào mừng cá nhân hóa, thẻ hồ sơ cá nhân chia sẻ.

📁 [phase-0-event/](./phase-0-event/)

---

### Giai đoạn 1A — CRM Phiên bản Khả dụng Tối thiểu
**Thời gian:** Tuần 3 đến Tuần 6 (15/5 → 15/6/2026)
**Mục tiêu:** Thay thế hoàn toàn Excel cho đội Creator Care. Toàn bộ creator từ sự kiện được phân công người phụ trách trong 24 giờ. Mọi tương tác với creator được lưu tập trung trong hệ thống.

**Các module chính:** Quản lý định danh creator, vòng đời quản lý, phân công sở hữu, hộp thoại tác vụ, lưu trữ trao đổi, đa thuê bao, thông báo.

📁 [phase-1a-crm-mvp/](./phase-1a-crm-mvp/)

---

### Giai đoạn 1B — Phân nhánh VIP và Bảo vệ Quan hệ
**Thời gian:** Tuần 7 đến Tuần 10 (16/6 → 15/7/2026)
**Mục tiêu:** Cho phép một người phụ trách cấp cao chăm sóc trên 50 creator nhờ tự động hóa phân hạng và đồng hồ SLA. Đảm bảo quan hệ với creator là tài sản công ty, không bị mất khi nhân sự nghỉ việc.

**Các module chính:** Hệ thống chấm điểm phân hạng, đồng hồ SLA và leo thang, đồng bộ hiệu suất, bảng chăm sóc hiệu suất, quản lý tài sản quan hệ, báo cáo và xuất dữ liệu.

📁 [phase-1b-vip/](./phase-1b-vip/)

---

### Giai đoạn 2 — Tìm kiếm Creator Chủ động
**Thời gian:** Tuần 11 đến Tuần 17 (16/7 → 31/8/2026)
**Mục tiêu:** Đảo chiều dòng chảy lead, từ tiếp nhận thụ động sang chủ động tìm kiếm creator phù hợp với từng ngành hàng và thương hiệu. Tự động gửi tin nhắn ngỏ lời hợp tác qua Zalo OA. Đội Phát triển Kinh doanh có thể nhập yêu cầu và hệ thống đề xuất danh sách creator phù hợp trong 24 giờ.

**Các lớp chính:** Thu thập dữ liệu mạng xã hội, làm giàu hồ sơ, chấm điểm lead, hộp thư tìm kiếm, ngỏ lời hợp tác tự động, công cụ yêu cầu của Đội Phát triển Kinh doanh, theo dõi chuyển đổi.

📁 [phase-2-sourcing/](./phase-2-sourcing/)

---

## Cách đọc tài liệu này

Mỗi file module trong các thư mục giai đoạn được viết theo cấu trúc chuẩn:

| Phần | Nội dung |
|---|---|
| **Mục đích** | Module này giải quyết bài toán nghiệp vụ gì |
| **Người dùng chính** | Vai trò nào trong AccessTrade sẽ tương tác hằng ngày |
| **Câu chuyện sử dụng** | Một tình huống thực tế minh họa luồng làm việc |
| **Tính năng cốt lõi** | Danh sách các chức năng module cần có |
| **Tích hợp** | Module này kết nối với module nào, hệ thống nào bên ngoài |
| **Đo lường thành công** | Cách đánh giá module hoạt động tốt |
| **Liên quan trong demo** | Đường dẫn cụ thể trên trang demo để xem trực quan |

---

## Các nguồn tài liệu liên quan

- **Trang demo:** https://vcreator.demo.accesstrade.click/
- **Lộ trình bốn tháng:** https://vcreator.demo.accesstrade.click/roadmap
- **Sơ đồ kiến trúc CRM:** https://vcreator.demo.accesstrade.click/phase-1
- **Bản mẫu CRM tương tác:** https://vcreator.demo.accesstrade.click/mockup
- **Cổng đăng ký sự kiện:** https://vcreator.demo.accesstrade.click/event/creator-for-vietnam

---

## Bối cảnh hệ thống

CRM at-core không hoạt động độc lập, mà nằm trong hệ sinh thái có sẵn của Diso và AccessTrade.

**Diso đã có:**
- influence-meter — bộ máy thu thập hồ sơ creator và chấm điểm
- Metric POC — bộ máy thu thập dữ liệu mạng xã hội đã chứng minh hiệu quả

**AccessTrade đã có:**
- ambassador.koc.com.vn — nền tảng quản lý chiến dịch hiện hành. CRM at-core không quản lý chiến dịch, chỉ tham chiếu thông tin từ ambassador để hiển thị thống kê.
- Tài khoản Zalo OA chính thức để liên hệ creator
- Đội Creator Care đang vận hành bằng Excel

CRM at-core là tầng quản lý quan hệ giữa AccessTrade và creator. Mọi thao tác liên quan đến chiến dịch vẫn diễn ra trên ambassador.koc.com.vn, CRM chỉ phục vụ việc tiếp nhận, phân loại, chăm sóc và mở rộng pool creator.
