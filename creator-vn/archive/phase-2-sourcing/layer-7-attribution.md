# Lớp 7 — Theo dõi Chuyển đổi

---

## Mục đích

Lớp 7 đóng vòng feedback của toàn pipeline Phase 2. Mỗi outreach gửi đi cần được đo lường: creator có đọc không, có phản hồi không, sentiment thế nào, có active trong CRM không, có tạo GMV không.

Dữ liệu attribution dùng cho hai mục đích:
1. **Báo cáo BD và brand:** ROI cụ thể của mỗi batch sourcing
2. **Cải tiến mô hình:** feedback loop để retrain scoring và AI suggest

Không có Lớp 7, toàn bộ Phase 2 chạy mù — không biết thành công hay thất bại.

---

## Người dùng chính

- **BD:** Xem ROI của batch mình submit
- **Lead Care:** Tổng hợp performance toàn team
- **Diso ML team:** Dùng feedback để retrain model
- **AccessTrade leadership:** Báo cáo brand và đánh giá Phase 2

---

## Câu chuyện sử dụng

Sau 30 ngày kể từ khi go-live Phase 2, Lead Phương vào dashboard tổng:

**Tháng 8/2026:**
- 12 BD requests submitted
- 850 creator outreached
- 72 responded (8.5% — đạt mục tiêu 8%)
- 28 active trong CRM (3.3% conversion — vượt mục tiêu 3%)
- Tổng GMV từ creator sourcing: 420 triệu VND
- Cost per acquired creator: 95K VND (vs 250K BD tự tìm thủ công)

Drill down theo BD:
- Đức (TCB campaign): 5 batches, 17% response rate, GMV 180tr
- Linh (Innisfree): 3 batches, 14% response rate, GMV 95tr
- Hoa (mom-baby): 4 batches, 6% response rate (dưới mục tiêu) — cần review template

Phương click vào batch của Hoa, thấy template "Mom-Baby-T8-2026" có sentiment positive chỉ 30% (vs 60% mục tiêu). Cô tag Compliance để review template, đề xuất A/B test phiên bản mới.

ML team Diso vào tab "Model performance":
- Score correlation với actual response: 0.65 (tốt)
- Top 10% score có response rate 22%, bottom 10% có 2% (model phân biệt tốt)
- Predicted tier vs actual tier (sau khi creator vào AT): 78% chính xác
- Recommendation: retrain model với 850 mẫu mới tuần này

---

## Tính năng cốt lõi

### UTM tracking
- Mỗi outreach có UTM riêng (source=sourcing, batch=BD-xxx)
- Theo dõi click landing page, đăng ký
- Phân biệt nguồn organic vs sourcing

### Response analytics
- Tỷ lệ đọc tin (read rate)
- Tỷ lệ phản hồi (response rate)
- Sentiment phân loại (positive/neutral/negative)
- Thời gian từ outreach đến response

### Conversion funnel
- Outreached → Read → Responded → Met → Active → First GMV
- Drop-off rate ở từng bước
- Funnel theo BD, theo brand, theo ngành

### GMV attribution
- Doanh thu từ creator sourcing trong 30/60/90 ngày
- LTV ước lượng dựa trên tier
- ROI vs cost per acquired creator

### Sentiment analysis
- NLP phân loại response
- Keyword extraction (lý do từ chối, lý do đồng ý)
- Theo dõi sentiment theo template

### Feedback loop cho ML
- Mỗi outreach có outcome label
- Care đánh dấu lead "good" / "bad" trong CRM Phase 1
- Hằng tuần export dataset cho ML retrain
- A/B test model version mới vs cũ

### BD performance scoreboard
- Leaderboard theo response rate, conversion, GMV
- Gamification để khuyến khích BD viết request tốt
- Public trong nội bộ AT

### Brand reporting
- Báo cáo tự động cho brand mỗi tuần/tháng
- Số creator mới cho campaign, GMV, ROI
- Format chuẩn, có thể export PDF

---

## Tích hợp

- **CRM Phase 1 (M2, M5):** lấy data về creator active, assignment
- **CRM Phase 1 (M3 scoring):** lấy actual tier sau khi creator vào AT
- **GMV tracking (M11/M15):** lấy doanh thu attribution
- **Lớp 3 scoring engine:** feed back để retrain
- **External BI tools:** export data cho leadership dashboard

---

## Đo lường

- Tỷ lệ chuyển đổi từ outreach đến active creator, mục tiêu trên 3%
- Cost per acquired creator (CAC), mục tiêu dưới 100K VND
- ROI tổng Phase 2 (GMV / chi phí), mục tiêu trên 5x sau 6 tháng
- Model accuracy (predicted tier vs actual), mục tiêu trên 75%
- Sự cải thiện response rate theo từng quarter (mục tiêu +1% mỗi quarter nhờ retrain)
