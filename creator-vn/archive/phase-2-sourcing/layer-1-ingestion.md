# Lớp 1 — Thu thập dữ liệu

> **Tận dụng:** Metric POC infrastructure đã có sẵn của Diso

---

## Mục đích

Lớp 1 là cửa ngõ dữ liệu của Phase 2. Mỗi tuần phải thu thập trên 5.000 hồ sơ creator mới từ TikTok, Instagram, Facebook để cung cấp nguyên liệu cho các lớp xử lý phía sau.

Vì Diso đã có Metric POC chạy ổn định cho việc thu thập creator phục vụ campaign hiện tại, Lớp 1 không xây mới mà tích hợp với Metric POC. Đây là quyết định quan trọng giúp tiết kiệm thời gian Phase 2.

Tuy nhiên, Lớp 1 thêm một bước hard-filter ngay khi ingest để không lưu trữ lãng phí. Creator dưới 10K follower hoặc nội dung không phải tiếng Việt sẽ bị loại bỏ ngay, không vào pool.

---

## Nguồn dữ liệu

### Metric POC scrapers (đã có)
- TikTok: ngành chính, pool lớn nhất
- Instagram: bổ sung cho beauty, fashion, lifestyle
- Facebook: phù hợp cho mom-baby, fnb

### Threads scraper (mới)
- Cần thêm vì có một số campaign Threads đang chạy

### Official APIs khi có
- TikTok Marketing API — cho phép search creator marketplace
- Instagram Graph API — giới hạn nhưng dữ liệu chính xác

### Manual upload
- BD có thể upload danh sách creator từ Excel khi đã có sẵn
- Hệ thống tự enrich và score

---

## Quy tắc lọc khi ingest

Để tránh đầy bộ nhớ với dữ liệu junk:

- Số follower tối thiểu: 10.000
- Ngôn ngữ content: tiếng Việt (detect bằng NLP)
- Engagement rate tối thiểu: 2%
- Có hoạt động trong 90 ngày qua (loại trừ tài khoản chết)
- Không phải bot account (heuristic check)

Creator không pass filter sẽ không được lưu, tiết kiệm storage và xử lý phía sau.

---

## Chống bị block IP

- Multi-region proxy rotation (đã có trong Metric POC)
- Rate limiting tự động: TikTok 2K request/giờ, Instagram 1K/giờ
- Cool-down khi phát hiện block
- Tận dụng infrastructure proxy đã proven của Metric POC

---

## Đo lường

- Số creator thu thập mỗi tuần, mục tiêu trên 5.000
- Tỷ lệ creator pass hard-filter, mục tiêu khoảng 60-70%
- Tỷ lệ thành công request crawl, mục tiêu trên 95%
- Số lần bị block IP và thời gian cool-down
