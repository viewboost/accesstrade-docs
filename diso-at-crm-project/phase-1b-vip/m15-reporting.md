# M15 — Báo cáo và Xuất dữ liệu

> **Demo:** https://vcreator.demo.accesstrade.click/mockup/dashboard

---

## Mục đích

Module M15 cung cấp báo cáo định kỳ và công cụ xuất dữ liệu cho leadership và team Creator Care. Nếu không có M15, người dùng phải mở từng creator hoặc từng người phụ trách để cộng tổng — không thể nắm được bức tranh toàn cảnh.

Đặc biệt, đội Creator Care đã quen với Excel. M15 đảm bảo họ có thể xuất dữ liệu ra Excel khi cần làm báo cáo phức tạp hoặc share với các bên ngoài hệ thống. Việc giữ nguyên thói quen Excel cho các tình huống đặc biệt giúp việc chuyển đổi sang CRM ít phản ứng hơn.

---

## Người dùng chính

- **Trưởng nhóm Lead Care:** Sử dụng dashboard hằng ngày, xuất báo cáo tuần
- **Leadership AccessTrade:** Xem dashboard tổng quan để ra quyết định chiến lược
- **BD:** Sử dụng báo cáo về creator phù hợp campaign
- **Compliance:** Xuất audit log khi cần điều tra

---

## Câu chuyện sử dụng

Sáng thứ Hai, Lead Phương vào Reports Dashboard. Cô thấy KPI tuần qua:
- 250 creator đang active (tăng 12 so với tuần trước)
- 22% đạt VIP tier
- GMV tuần 2.8 tỷ (tăng 18%)
- SLA compliance 92%
- Relationship strength trung bình 76

Cô bấm vào Tier Distribution chart, thấy phân bổ creator theo tier. Click vào Brand Pool chart, thấy thống kê creator theo brand (TCB pool 18 creator, VinFast pool 24 creator, AT general 208 creator).

Cô cuộn xuống Top Creators by GMV, thấy danh sách 10 creator mang lại GMV cao nhất. Cô screenshot share cho leadership.

Top AMs by GMV under care cho thấy Phương (Lead) đang quản lý team có GMV tổng cao nhất, kế đến là Linh, Đức.

GMV Trend chart 30 ngày hiển thị xu hướng tăng đều, có một đỉnh nhỏ vào ngày Mega Live.

Cô cần báo cáo chi tiết cho leadership. Cô bấm "Export — Excel" ở cuối trang, chọn các trường cần (creator, tier, GMV, owner), download file. Mở Excel, làm thêm các phân tích pivot table riêng.

Cô cũng tạo một custom query: "Tất cả creator beauty tier Gold với GMV trên 30 triệu tháng qua". Hệ thống hiển thị 12 creator. Cô lưu query này thành "Beauty Gold Top Performers" để truy cập nhanh các tuần sau.

---

## Tính năng cốt lõi

### Dashboard tổng quan (Reports Home)
- KPI strip với các chỉ số chính: số creator, VIP, AM active, GMV, SLA, relationship strength
- Quick links đến các view quan trọng (Watchlist, SLA Risk, Offboarding)

### Báo cáo pre-built
- **SLA compliance theo tuần/tháng:** Phân tích tỷ lệ tuân thủ theo người phụ trách, tier
- **Owner KPI report:** So sánh hiệu suất các người phụ trách
- **Tier conversion funnel:** Tỷ lệ chuyển đổi qua các tier
- **GMV by tier/brand:** Phân tích GMV theo phân loại
- **Lifecycle distribution:** Số creator ở mỗi giai đoạn của V2

### Tier distribution chart
- Visual phân bổ creator theo tier (Diamond/Gold/Silver/Bronze/Watchlist)
- Phần trăm và số lượng cụ thể
- Insight tự động (ví dụ "VIP conversion 22% — vượt target 20%")

### Brand pool stats
- Phân tích creator theo brand (TCB, VinFast, AT general)
- GMV mỗi brand
- Số chiến dịch active
- Link external ra ambassador.koc.com.vn để quản lý chiến dịch

### Top performers
- Top 10 creator theo GMV
- Top 5 người phụ trách theo GMV under care
- Cho phép xem chi tiết bằng cách bấm vào

### GMV trend chart
- Stacked chart 30 ngày phân theo brand
- Cho phép so sánh các giai đoạn
- Identify spike và dip

### Custom query builder
- Cho phép Lead tạo truy vấn riêng theo nhiều điều kiện
- Lưu query để dùng lại
- Share query với người khác

### Xuất dữ liệu
- Excel: format đẹp, có header
- CSV: lightweight cho integrate với tool khác
- PDF: cho báo cáo gửi leadership

### Lịch gửi báo cáo tự động
- Báo cáo tuần tự động gửi vào email Lead vào sáng thứ Hai
- Báo cáo tháng vào ngày đầu tháng
- Cấu hình recipient và format

---

## Tích hợp

- **Với mọi module khác:** M15 đọc dữ liệu từ tất cả module (M1-M14, M16) để tạo báo cáo
- **Với ambassador.koc.com.vn:** Lấy thống kê chiến dịch để hiển thị Brand Pool report
- **Với Excel/Google Sheets:** Format xuất tương thích để Lead có thể tiếp tục phân tích
- **Với email:** Gửi báo cáo định kỳ qua email

---

## Đo lường thành công

- Số người dùng truy cập Reports Dashboard hằng tuần, mục tiêu 100% Lead
- Số custom query được tạo và sử dụng, theo dõi để hiểu nhu cầu
- Tỷ lệ Lead xuất báo cáo Excel mỗi tuần, theo dõi để cải thiện báo cáo trong CRM
- Sự hài lòng leadership với báo cáo (khảo sát hàng quý)

---

## Liên quan trong demo

- **Reports Dashboard:** https://vcreator.demo.accesstrade.click/mockup/dashboard
- Trang demo có đầy đủ KPI strip, tier distribution, brand pool, top creators, top AMs, GMV trend, export CTA
- Phía dưới có nút "Custom query" cho Lead truy vấn riêng
