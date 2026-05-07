# Lớp 2 — Làm giàu hồ sơ

> **Tận dụng:** influence-meter của Diso

---

## Mục đích

Sau khi Lớp 1 thu thập handle creator cơ bản, Lớp 2 làm giàu hồ sơ với các trường thông tin cần thiết cho việc chấm điểm. Đây là nơi influence-meter (đã có sẵn của Diso) phát huy giá trị nhất.

Mỗi creator cần có đủ thông tin để Lớp 3 chấm điểm chính xác: số follower thật (không phải bot), engagement rate, demographics audience, niche content, brand-safety check.

---

## Các bước làm giàu

### Profile resolve
- Từ handle → truy xuất full profile public
- Avatar, bio, location, ngôn ngữ
- Lượng follower và following

### Audience demographics estimate
- Phân tích audience từ engagement pattern
- Ước lượng giới tính, độ tuổi, vị trí địa lý
- Hữu ích cho việc match với target brand

### Engagement rate calculation
- Tính trung bình engagement của 30 bài đăng gần nhất
- Like + comment + share / follower
- Phát hiện engagement bot bằng pattern bất thường

### Content categorization
- NLP phân tích caption và hashtag
- Image classification phân loại visual
- Gắn nhãn ngành (Beauty, F&B, Travel, Tech...)
- Sub-category cụ thể (ví dụ Beauty → Skincare, Makeup, Hair)

### Language detection
- Đảm bảo creator viết tiếng Việt
- Phân biệt tiếng Việt vs tiếng Anh trong content mix

### Brand-safety scan
- Quét scandal cũ trên các nền tảng
- Phát hiện từ ngữ cấm, content nhạy cảm
- Check blacklist nội bộ AccessTrade

---

## Cập nhật định kỳ

- Profile được làm giàu một lần khi vào pool
- Re-enrich hằng tháng để cập nhật engagement mới
- Re-enrich ngay khi có outreach để dữ liệu mới nhất

---

## Đo lường

- Tỷ lệ creator có hồ sơ đầy đủ (≥ 80% trường), mục tiêu trên 90%
- Tỷ lệ phát hiện brand-safety risk sớm, mục tiêu trên 95%
- Thời gian làm giàu trung bình một creator, mục tiêu dưới 30 giây
