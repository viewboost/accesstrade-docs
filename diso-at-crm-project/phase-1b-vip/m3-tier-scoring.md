# M3 — Hệ thống Chấm điểm Phân hạng

> **Demo:** Tier breakdown hiển thị trên https://vcreator.demo.accesstrade.click/mockup/creators/cr-beautyquynh

---

## Mục đích

Module M3 tự động phân loại creator vào các tier (Bronze, Silver, Gold, Diamond hoặc Watchlist) dựa trên dữ liệu khách quan. Tier quyết định mức độ ưu tiên chăm sóc, mức quyền lợi mở khoá, và việc creator có được Senior Care chăm sóc hay không.

Trước M3, việc phân loại creator phụ thuộc vào cảm nhận của từng người phụ trách. Người này coi creator A là VIP, người khác lại không. Quyết định không nhất quán dẫn đến tài nguyên chăm sóc bị lãng phí cho creator không tiềm năng và bỏ sót creator đáng đầu tư.

M3 mang lại sự nhất quán: cùng dữ liệu vào, cùng kết quả ra. Đồng thời cho phép Lead override khi cần, vì luôn có những trường hợp đặc biệt mà data không bắt được.

---

## Người dùng chính

- **Hệ thống tự động:** Chấm điểm chạy ngầm, không cần con người trigger
- **Người phụ trách Care:** Xem score breakdown để hiểu tại sao creator được phân tier nào
- **Trưởng nhóm Lead:** Override khi có lý do đặc biệt, cấu hình rule chấm điểm
- **BD:** Sử dụng tier để quyết định ưu tiên đề xuất campaign

---

## Câu chuyện sử dụng

@beautyquynh đăng ký tại sự kiện. Trong vòng một giây sau khi submit, M3 tính điểm dựa trên:

- Audience quality 22/25 (engagement rate cao, follower thật)
- GMV potential 23/25 (ngành Beauty CR cao + lịch sử buy intent tốt)
- Brand-safety 25/25 (không có scandal, content sạch)
- Strategic fit 17/25 (phù hợp với một số brand đang active)

Tổng: 87/100. M3 phân vào tier "VIP Candidate" (ngưỡng VIP Candidate là 80+).

Sau hai tuần làm việc, Quỳnh có hiệu suất tốt với hai chiến dịch đầu. M10 sync dữ liệu GMV. M3 chạy lại scoring với dữ liệu mới. Score nhảy lên 92, tier chuyển từ "VIP Candidate" sang "VIP Confirmed".

Cuối tháng, có một creator beauty khác score 78, gần ngưỡng VIP nhưng chưa đủ. Tuy nhiên Lead Phương biết creator này có quan hệ đặc biệt với một brand lớn, dù score chưa cao nhưng giá trị chiến lược thì có. Cô bấm "Manual override", chuyển tier sang VIP Candidate, ghi lý do "Strategic relationship với brand X". Hệ thống lưu lại quyết định, hiển thị badge "Override" trên tier.

---

## Tính năng cốt lõi

### Bốn tiêu chí chấm điểm
- **Audience quality (25 điểm):** Chất lượng người theo dõi — engagement rate, follower thật, demographics phù hợp
- **GMV potential (25 điểm):** Tiềm năng tạo doanh thu — CR ngành, lịch sử buy intent, content có CTA tốt
- **Brand-safety (25 điểm):** An toàn thương hiệu — không scandal, không content nhạy cảm, lịch sử sạch
- **Strategic fit (25 điểm):** Phù hợp chiến lược — match với brand đang active, ngành ưu tiên của AccessTrade

### Năm tier chuẩn
- **Watchlist (dưới 30 điểm hoặc có flag):** Creator có rủi ro, cần Senior review trước khi action
- **Bronze (30-49):** Creator cơ bản, chăm sóc theo workflow chuẩn
- **Silver (50-64):** Creator tiềm năng, nên đầu tư thêm
- **Gold (65-79):** Creator chất lượng cao, ưu tiên các chiến dịch
- **VIP Candidate (80-89):** Cần Senior Care, có khả năng lên VIP
- **VIP Confirmed (90+):** Creator hàng đầu, mọi nguồn lực ưu tiên, có account manager riêng

### Cấu hình rule từ giao diện
- Trưởng nhóm có thể điều chỉnh ngưỡng tier từ giao diện
- Có thể điều chỉnh trọng số bốn tiêu chí
- Có thể thêm rule custom (ví dụ "Creator có brand đề cử trực tiếp tự động lên VIP Candidate")
- Không cần lập trình, không cần Diso can thiệp

### Hai điểm phân nhánh VIP
- **Lần một (P1.2):** Khi creator vừa vào hệ thống, dựa trên profile data → có thể lên VIP Candidate ngay
- **Lần hai (P7.2):** Sau khi có dữ liệu performance thực tế → confirm VIP hoặc downgrade

### Override thủ công
- Lead có quyền override tier
- Bắt buộc ghi lý do
- Lưu lịch sử để audit
- Hiển thị badge "Override" trên tier để mọi người biết đây là quyết định manual

### Re-score định kỳ
- Tự động chạy lại scoring hàng tuần
- Cập nhật khi có dữ liệu mới (campaign mới hoàn thành, follower thay đổi)
- Báo cáo creator chuyển tier để Lead theo dõi

### Score breakdown UI minh bạch
- Hiển thị chi tiết bốn tiêu chí cho mỗi creator
- Người phụ trách hiểu được tại sao creator được tier này
- BD hiểu được tại sao một creator được đề xuất hoặc không
- Creator (qua Welcome Page) hiểu được điểm số của mình

---

## Tích hợp

- **Với M1 Creator Identity:** Sử dụng dữ liệu profile từ influence-meter
- **Với M10 Performance Sync:** Sử dụng dữ liệu GMV/đơn hàng để chấm GMV potential
- **Với M5 Owner Workload:** Tier quyết định ai phụ trách (VIP cần Senior Care)
- **Với M2 Lifecycle:** Khi creator chuyển tier, lifecycle có thể chuyển sang Tiered state
- **Với M11 Performance Care:** Score và tier là input cho việc ra quyết định Scale/Optimize/Pause

---

## Đo lường thành công

- Tỷ lệ chuyển đổi từ VIP Candidate sang VIP Confirmed, mục tiêu trên 40%
- Tỷ lệ override manual, theo dõi để cải thiện rule (nếu quá nhiều override = rule chưa đúng)
- Sự nhất quán giữa score và GMV thực tế (creator score cao có GMV tương ứng cao)
- Số rule custom được Lead thêm (cho thấy hệ thống flexible đủ)

---

## Liên quan trong demo

- **Trang chi tiết creator với tier breakdown:** https://vcreator.demo.accesstrade.click/mockup/creators/cr-beautyquynh
- Trên trang demo, phần "Tier Score Breakdown" hiển thị bốn tiêu chí với thanh tiến độ trực quan
- Có nút "Manual override" cho Lead
- Trang Welcome Page tại sự kiện cũng dùng kết quả M3 để hiển thị tier cho creator
