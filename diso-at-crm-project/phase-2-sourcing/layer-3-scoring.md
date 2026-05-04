# Lớp 3 — Chấm điểm Lead

---

## Mục đích

Lớp 3 chấm điểm phù hợp 0-100 cho mỗi creator trong pool sourcing, giống như M3 ở Phase 1B nhưng với mục đích khác. M3 chấm để phân tier chăm sóc. Lớp 3 chấm để quyết định "creator này có đáng outreach không".

Khi BD nhập yêu cầu (ví dụ "tìm 50 creator beauty 50K-200K"), Lớp 3 dùng điểm số để xếp hạng creator phù hợp nhất, trả về top kết quả cho BD chọn.

Điểm cao = nhiều khả năng creator phản hồi tích cực + có khả năng tạo GMV cao = ROI outreach tốt.

---

## Năm tiêu chí chấm điểm

### 1. Follower fit (25%)
- Số follower có rơi đúng khoảng BD yêu cầu không
- Quá ít hoặc quá nhiều đều giảm điểm
- Sweet spot khác nhau theo ngành

### 2. Engagement quality (25%)
- Engagement rate của 30 bài gần nhất
- So với benchmark ngành
- Phát hiện engagement bot

### 3. Niche match (20%)
- Content có phù hợp ngành BD yêu cầu không
- NLP phân tích caption + image classification
- Lịch sử content trong 90 ngày

### 4. Brand-safety (15%)
- Không có scandal
- Content sạch
- Lịch sử brand collaboration sạch
- Không trong blacklist

### 5. Behavioral signals (15%)
- Có lịch sử commercial intent (đã từng làm affiliate, brand deal)
- Tần suất đăng bài đều đặn
- Có CTA tốt trong content
- Audience có buy intent

---

## Industry classification

- Tự động phân loại creator vào ngành chính
- Có thể có nhiều ngành (ví dụ Beauty + Lifestyle)
- Phục vụ matching với brand yêu cầu cụ thể

---

## Predicted tier estimate

- Dự đoán tier (Bronze/Silver/Gold/Diamond) creator có thể đạt nếu vào AccessTrade
- Giúp BD biết creator này có tiềm năng VIP hay không
- Khác với M3 chấm tier thực sự sau khi creator vào hệ thống

---

## Match score per active campaign

- Khi BD tạo request gắn với campaign cụ thể, Lớp 3 tính match score riêng cho campaign đó
- Cộng các yếu tố cụ thể của campaign (ví dụ TCB Visa cần creator có audience finance)

---

## Score breakdown UI minh bạch

- Hiển thị chi tiết 5 tiêu chí cho BD
- BD hiểu được tại sao creator này được suggest
- Build trust của BD với hệ thống

---

## Cải tiến model theo thời gian

- Mỗi outreach thành công/thất bại được feedback lại
- Care đánh dấu lead "good" hoặc "bad"
- Hằng tuần retrain model với feedback

---

## Đo lường

- Tỷ lệ creator pass scoring filter (top 10-15% pool)
- Tỷ lệ outreach success cho creator score cao vs thấp (validate model)
- Sự nhất quán giữa predicted tier và actual tier sau khi creator vào AT
- BD trust score (khảo sát hàng tháng)
