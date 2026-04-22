# OpsHub — Nền tảng Kiểm duyệt Content bằng AI

**Cập nhật:** 2026-04-07

---

## Vấn đề hiện tại

Quy trình kiểm duyệt video từ creator đang gặp các hạn chế:

- **Duyệt thủ công toàn bộ** — Mỗi video phải được nhân viên xem và đánh giá, tốn 2-5 phút/video
- **Khó mở rộng** — 10.000 video/tháng cần 5-8 nhân viên duyệt, tăng campaign = tăng chi phí nhân sự
- **Sai sót khó kiểm soát** — Người duyệt nhiều video liên tục dễ bỏ sót vi phạm, không có tiêu chuẩn đồng nhất
- **Chậm trễ thanh toán** — Video chờ duyệt lâu → creator chờ thưởng lâu → giảm động lực tham gia

---

## Giải pháp: OpsHub

OpsHub nâng cấp quy trình kiểm duyệt bằng cách đưa **AI Agent** vào hỗ trợ — thay vì duyệt 100% thủ công, AI sẽ tự động kiểm tra và ra quyết định cho phần lớn video, nhân viên chỉ cần xử lý các trường hợp AI không chắc chắn.

### Cách hoạt động

**Bước 1: Kiểm tra tự động (dưới 1 giây)**
Video được kiểm tra các quy tắc cứng: thời lượng, hashtag, định dạng, nền tảng. Vi phạm rõ ràng sẽ bị từ chối ngay.

**Bước 2: AI Agent phân tích (khoảng 30 giây)**
AI xem video, nghe nội dung lời nói, đọc caption — đánh giá toàn diện theo tiêu chí campaign.

**Bước 3: Ra quyết định**
- Đạt tất cả tiêu chí => Duyệt tự động
- Vi phạm nghiêm trọng => Từ chối tự động
- Chưa rõ ràng => Chuyển cho nhân viên xem xét

### AI Agent kiểm tra những gì?

| Hạng mục | Mô tả | Ví dụ |
|----------|-------|-------|
| **Thông điệp thương hiệu** | Creator có nhắc đến đủ key messages của campaign không? | "Miễn phí đổi pin 3 năm", "Thu nhập 15 triệu/tháng" |
| **An toàn thương hiệu** | Video có chứa nội dung nhạy cảm không? | Bạo lực, 18+, chính trị, phản cảm |
| **Tỷ lệ nội dung quảng cáo** | Bao nhiêu % video nói về sản phẩm/dịch vụ? | Yêu cầu tối thiểu 50% nội dung liên quan |
| **Trang phục & hình ảnh** | Creator ăn mặc phù hợp? Logo brand hiển thị đúng? | Trang phục lịch sự, logo không bị lật ngược |
| **Tính xác thực caption** | Caption có phải do AI viết không? | Phát hiện caption copy-paste hoặc do ChatGPT tạo |

### Kết quả duyệt

Mỗi video sẽ nhận 1 trong 3 kết quả:

- **Duyệt tự động** — AI đánh giá đạt tất cả tiêu chí → video được duyệt ngay, không cần người xem
- **Từ chối tự động** — Vi phạm nghiêm trọng (nội dung 18+, sai nền tảng...) → từ chối ngay
- **Cần người duyệt** — AI không chắc chắn (ví dụ: key messages được nhắc nhưng chưa rõ ràng) → chuyển cho nhân viên

Kết quả được gửi về hệ thống đối tác qua webhook ngay khi có quyết định, kèm:
- Lý do duyệt/từ chối (tiếng Việt, dễ hiểu)
- Chi tiết từng tiêu chí đạt/không đạt
- Góp ý cho creator (nếu cần chỉnh sửa)

---

## Hiệu quả mong đợi

| Chỉ số | Trước (thủ công) | Sau (có AI) |
|--------|-----------------|-------------|
| Thời gian duyệt trung bình | 2-5 phút/video | Dưới 30 giây (auto) |
| % video cần người duyệt | 100% | Dưới 40% |
| Nhân sự cần cho 10.000 video/tháng | 5-8 người | 2-3 người |
| Tỷ lệ bỏ sót vi phạm | Không đo được | Dưới 5% |
| Thời gian từ submit đến kết quả | 1-2 ngày | Dưới 2 phút (auto), dưới 24 giờ (cần người) |

---

## Lộ trình triển khai

### Giai đoạn 1: AI gợi ý, người duyệt quyết định *(Hiện tại)*

AI Agent phân tích video và đưa ra **đề xuất** (duyệt / từ chối / cần xem thêm). Nhân viên Operation xem đề xuất của AI, kiểm tra lại nếu cần, rồi bấm xác nhận kết quả.

**Mục tiêu:**
- Xây dựng độ tin cậy cho AI — theo dõi tỷ lệ AI đề xuất đúng
- Giảm thời gian duyệt — nhân viên chỉ cần xác nhận thay vì xem toàn bộ video
- Thu thập dữ liệu — những trường hợp AI sai sẽ được dùng để cải thiện

**Kết quả bước này:**
- Video vẫn được duyệt bởi người, nhưng nhanh hơn nhờ AI hỗ trợ
- Bắt đầu đo lường độ chính xác của AI

### Giai đoạn 2: AI tự duyệt, tự từ chối *(Sắp tới)*

Khi AI đã chứng minh độ tin cậy (tỷ lệ đúng > 95%), cho phép AI **tự động ra quyết định** mà không cần người xác nhận:

- Video đạt tiêu chí rõ ràng → **Duyệt ngay**, tính thưởng luôn
- Video vi phạm nghiêm trọng → **Từ chối ngay**, thông báo creator
- Video không rõ ràng → Vẫn chuyển cho người duyệt

**Mục tiêu:**
- 60-70% video được xử lý hoàn toàn tự động
- Nhân viên chỉ xử lý 30-40% video khó/mơ hồ
- Scale lên 50.000+ video/tháng mà không tăng nhân sự

---

## Tùy chỉnh theo campaign

Mỗi campaign có thể cấu hình riêng:

- **Key messages** — Danh sách thông điệp creator cần nhắc đến, hỗ trợ cấu trúc AND/OR phức tạp (ví dụ: phải nhắc đủ 3 thông điệp bắt buộc, hoặc chọn ít nhất 2 trong 5 chủ đề)
- **Mức độ nghiêm ngặt** — Cho phép AI tự duyệt khi tin cậy trên X%, hoặc luôn cần người duyệt
- **Checklist nhân viên** — Bổ sung các hạng mục chỉ người mới kiểm tra được (ví dụ: chất lượng sáng tạo)
- **Thể lệ campaign** — Paste text thể lệ, AI tự động phân tích và tạo bộ quy tắc kiểm tra

---

## Thông báo & tích hợp

- **Webhook** — Kết quả duyệt được gửi về hệ thống đối tác ngay khi có quyết định
- **Telegram** — Thông báo vào group Telegram khi có video cần người duyệt
- **Dashboard** — Giao diện quản lý cho nhân viên Operation xem và duyệt video

---
