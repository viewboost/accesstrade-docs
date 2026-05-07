# M10 — Đồng bộ Hiệu suất

> **Demo:** Performance hiển thị trên https://vcreator.demo.accesstrade.click/mockup/creators/cr-beautyquynh

---

## Mục đích

Module M10 mang dữ liệu hiệu suất thực tế từ các nền tảng bên ngoài (Shopee, TikTok Shop, ambassador.koc.com.vn) về CRM. Không có M10, người phụ trách phải mở từng nền tảng để xem GMV, đơn hàng, hoa hồng — mất thời gian và dữ liệu rời rạc.

M10 đảm bảo CRM luôn có dữ liệu performance mới nhất để các module khác sử dụng: M3 chấm điểm dựa trên GMV, M11 phát hiện anomaly, M15 tạo báo cáo. Đây là "blood" của hệ thống — không có data flow này, mọi module phía trên đều thiếu chất xám để ra quyết định đúng.

Vì AccessTrade là MCN có quyền truy cập sâu vào dữ liệu các nền tảng (qua các quan hệ partnership có sẵn), M10 có lợi thế lớn so với các đối thủ phải scrape data công khai.

---

## Người dùng chính

- **Hệ thống tự động:** M10 chạy ngầm theo lịch
- **M3 Tier Engine:** Sử dụng dữ liệu để chấm điểm
- **M11 Performance Care:** Sử dụng dữ liệu để phát hiện anomaly
- **Người phụ trách Care:** Xem dữ liệu performance trên trang chi tiết creator
- **Lead:** Xem báo cáo tổng quan trên Reports Dashboard

---

## Câu chuyện sử dụng

@beautyquynh đăng nội dung review son MAC trên TikTok lúc tám giờ tối. Video bắt đầu có view, tracking link gắn trong bio dẫn về Shopee.

Sáng hôm sau, M10 chạy đồng bộ định kỳ. Nó kéo dữ liệu từ:
- Shopee Affiliate API: 12 đơn hàng có UTM của Quỳnh trong 24 giờ qua, GMV 8 triệu, hoa hồng 1.2 triệu
- TikTok Shop: 240K view, 5K click vào link
- ambassador.koc.com.vn: Cho biết Quỳnh đang trong campaign "Innisfree Summer Glow"

M10 tổng hợp dữ liệu, attribute đúng cho creator @beautyquynh thông qua mapping ID. Cập nhật vào CRM.

Linh mở trang chi tiết creator của Quỳnh, thấy ngay performance hôm trước: GMV 8M, CR 4.2%, view 240K. Cô không phải mở Shopee Affiliate dashboard riêng.

M3 chạy lại scoring với dữ liệu mới. Score Quỳnh tăng từ 87 lên 92, chuyển từ VIP Candidate sang VIP Confirmed.

M11 phát hiện CR 4.2% là cao bất thường, đánh dấu là "trending up", đề xuất Linh cân nhắc scale bằng GMV Max.

---

## Tính năng cốt lõi

### Kết nối với các nguồn dữ liệu
- **Shopee Affiliate API:** Pull dữ liệu đơn hàng, GMV, hoa hồng, refund/cancel
- **TikTok Shop API:** View, engagement, click-through, conversion
- **ambassador.koc.com.vn:** Campaign creator đang tham gia, brand commitment
- **Meta Insights (Facebook, Instagram):** Reach, engagement, ad spend
- **TAP API:** TAP campaign performance

### Tổng hợp ở cấp độ creator
- Mapping dữ liệu từ nhiều nguồn về cùng một creator
- Sử dụng các mã định danh trên nền tảng (Shopee Affiliate ID, TikTok Creator ID)
- Tổng hợp metrics: total GMV, total view, average CR, refund rate

### Tổng hợp ở cấp độ campaign
- Cho biết creator này tham gia campaign nào
- GMV phân theo campaign
- Cho phép Lead biết campaign nào hiệu quả nhất
- Lưu ý: chỉ đọc, không quản lý campaign — campaign vẫn ở ambassador.koc.com.vn

### Lịch đồng bộ thông minh
- VIP creator: đồng bộ mỗi giờ (do GMV cao, cần realtime)
- Gold/Silver: đồng bộ mỗi 6 giờ
- Normal: đồng bộ hằng ngày
- Watchlist: đồng bộ mỗi 12 giờ để theo dõi sát

### Cảnh báo chất lượng dữ liệu
- Khi link tracking sai (UTM lỗi), cảnh báo người phụ trách
- Khi traffic giảm đột ngột, cảnh báo
- Khi refund spike, cảnh báo Compliance

### Lưu trữ lịch sử
- Lưu snapshot performance mỗi ngày
- Phục vụ phân tích trend dài hạn
- Phục vụ M15 tạo báo cáo so sánh giai đoạn

---

## Tích hợp

- **Với Shopee, TikTok, Meta:** API trực tiếp với các nền tảng (qua quan hệ partnership AccessTrade)
- **Với ambassador.koc.com.vn:** API hai chiều, M10 đọc dữ liệu campaign và performance
- **Với M1 Creator Identity:** Sử dụng mã định danh để mapping đúng creator
- **Với M3 Tier Engine:** Cung cấp dữ liệu GMV cho việc chấm điểm
- **Với M11 Performance Care:** Cung cấp dữ liệu raw để phát hiện anomaly
- **Với M15 Reporting:** Cung cấp dữ liệu cho dashboard và báo cáo

---

## Đo lường thành công

- Tỷ lệ đồng bộ thành công, mục tiêu trên 99%
- Độ trễ trung bình của dữ liệu (từ khi event xảy ra đến khi vào CRM), mục tiêu dưới 1 giờ cho VIP
- Tỷ lệ data quality issues phát hiện sớm, mục tiêu trên 80%
- Số lượng creator có dữ liệu performance đầy đủ, mục tiêu 100% creator active

---

## Liên quan trong demo

- **Trang chi tiết creator — Performance section:** https://vcreator.demo.accesstrade.click/mockup/creators/cr-beautyquynh
- Phần "Performance Last 30d" hiển thị GMV, CR, view với phân theo Shopee/TikTok Shop/TAP
- Performance là input quan trọng cho tier scoring, hiển thị trong cùng trang
