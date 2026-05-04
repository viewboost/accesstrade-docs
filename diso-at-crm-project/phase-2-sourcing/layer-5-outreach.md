# Lớp 5 — Ngỏ lời Hợp tác

---

## Mục đích

Lớp 5 là nơi hệ thống chủ động gửi tin nhắn đầu tiên đến creator qua Zalo OA Business. Đây là lớp nhạy cảm nhất Phase 2 vì nếu gửi sai cách, Zalo OA của AccessTrade có thể bị flag spam, ảnh hưởng cả Phase 1.

Mục tiêu của Lớp 5: gửi tin nhắn cá nhân hoá đến creator đã được approve ở Lớp 4, theo lịch warm-up an toàn, có suppression list để tránh trùng lặp, và đo lường tỷ lệ phản hồi để cải thiện template.

---

## Người dùng chính

- **Care:** Soạn template, A/B test nội dung
- **Compliance:** Phê duyệt template trước khi đưa vào sử dụng
- **Lead Care:** Giám sát rate gửi, phản ứng khi có cảnh báo từ Zalo
- **BD:** Xem trạng thái outreach của batch mình submit

---

## Câu chuyện sử dụng

74 creator vừa được approve từ Lớp 4 đi vào outreach queue cho campaign Innisfree.

Hệ thống tự động chọn template "Beauty-Innisfree-T7-2026" đã được Compliance phê duyệt từ tuần trước. Template có placeholder cá nhân hoá: tên creator, ngành chính, lý do được chọn, link landing campaign.

Theo lịch warm-up tuần này (200 tin/ngày toàn AT), hệ thống chia 74 creator này thành 4 đợt nhỏ trong 2 ngày, mỗi đợt cách nhau 30 phút. Tin nhắn đi qua Zalo OA Business chính thức, có opt-out link cuối tin.

Sau 24 giờ:
- 12 creator đã đọc tin
- 8 creator đã phản hồi
- 1 creator bấm opt-out (tự động vào suppression list 90 ngày)

Trong số 8 creator phản hồi, 6 người tỏ ra quan tâm. Hệ thống tự động chuyển 6 creator này sang CRM Phase 1, gắn nguồn "BD-Innisfree-2026-07-20", auto-assign cho người phụ trách Care theo round-robin.

Lead Phương vào dashboard, thấy hôm nay đã gửi 95 tin (under limit 200), tỷ lệ phản hồi 10.8% (vượt mục tiêu 8%). Cô không cần can thiệp.

---

## Tính năng cốt lõi

### Template management
- Library template theo ngành, brand, mục đích
- Personalization placeholder (tên, ngành, lý do, link)
- Compliance phê duyệt trước khi active
- Version control, rollback nếu cần

### Warm-up sequence
- Tuần 1 sau go-live: 50 tin/ngày toàn AT
- Tuần 2: 100 tin/ngày
- Tuần 3: 200 tin/ngày
- Tuần 4 trở đi: scale theo response rate
- Tự động giảm rate nếu Zalo cảnh báo

### Throttling và scheduling
- Phân bổ đều trong giờ làm việc (8h-22h)
- Cách nhau tối thiểu 30 phút giữa các đợt
- Không gửi cuối tuần, ngày lễ
- Ưu tiên giờ vàng theo ngành

### Suppression list
- Creator opt-out: lock 90 ngày
- Creator đã từng outreach fail: lock 90 ngày toàn AT
- Creator đã active trong CRM: không outreach
- Creator do BD khác đã claim: không outreach

### Opt-out compliance
- Mỗi tin có link opt-out rõ ràng
- One-click opt-out, không cần đăng nhập
- Confirmation email sau khi opt-out
- Tuân thủ luật bảo vệ dữ liệu cá nhân

### Response handling
- Auto-detect response qua Zalo webhook
- Sentiment analysis: positive, neutral, negative
- Auto-route positive response sang CRM Phase 1
- Negative response: mark suppression, không retry

### A/B testing template
- Chia 50/50 hai biến thể template
- Đo response rate, sentiment
- Promote winner sau 100 mẫu

---

## Tích hợp

- **Zalo OA Business API:** kênh gửi tin chính thức
- **CRM Phase 1 (M2):** chuyển creator phản hồi tích cực
- **M5 phân công:** auto-assign Care cho lead mới
- **M14 thông báo:** báo Care khi có lead mới

---

## Đo lường

- Tỷ lệ phản hồi tin nhắn outreach, mục tiêu trên 8%
- Tỷ lệ creator opt-out, theo dõi để cải thiện template (mục tiêu dưới 5%)
- Số lần Zalo OA bị cảnh báo spam, mục tiêu bằng 0
- Thời gian từ outreach đến response trung bình
- Sentiment positive rate, mục tiêu trên 60%
