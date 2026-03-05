# Mở Lại Campaign Đã Kết Thúc — Cho Creator Bổ Sung Video

**Ngày:** 2026-03-05
**Phạm vi:** Campaign chỉ có submit video + crawl view (không có thưởng, không thanh toán, không đối soát)

---

## 1. Vấn Đề

Có 1 campaign đã kết thúc năm 2025. Khách hàng muốn mở lại để creator submit thêm video và hệ thống tiếp tục đếm lượt xem (view).

**Tại sao không submit được?**
Hệ thống kiểm tra ngày kết thúc campaign — nếu đã qua ngày này thì không cho creator nộp video nữa. Hệ thống crawl lượt xem cũng chỉ chạy cho campaign đang hoạt động.

**Yêu cầu đặc biệt:**
Dù creator submit vào năm 2026, nhưng toàn bộ số liệu (ngày submit, lượt xem, thống kê) phải được ghi nhận như thể nằm trong năm 2025 — để báo cáo và thống kê không bị lẫn sang năm mới.

---

## 2. Giải Pháp: Mở Cửa Bổ Sung + Chuyển Số Liệu Về 2025

Thực hiện theo 2 bước:

### Bước 1: Mở cửa cho creator submit video

Cập nhật hệ thống để campaign nhận biết đang trong "thời gian bổ sung":
- Creator vào app thấy campaign và submit video bình thường
- Hệ thống tự động crawl lượt xem cho video mới
- Mọi thứ hoạt động như campaign bình thường

Sau khi creator submit xong → đóng cửa bổ sung.

### Bước 2: Chuyển số liệu về 2025

Chạy chương trình chuyển đổi ngày tháng tự động:
- Tất cả video submit trong đợt bổ sung sẽ được đổi ngày về tháng 12/2025
- Ví dụ: video submit ngày 3/3/2026 → chuyển thành 3/12/2025
- Lượt xem, thống kê theo ngày cũng được chuyển tương tự
- Kết quả: báo cáo campaign 2025 có đầy đủ dữ liệu, không bị lẫn sang 2026

**Dữ liệu cần chuyển ngày (6 bảng):**

| Dữ liệu | Mô tả |
|----------|-------|
| Video (content) | Ngày submit, ngày đăng |
| Lượt xem theo ngày (content_flow) | Số view/like/comment mỗi ngày |
| Thống kê video theo ngày (content_analytic_daily) | Tổng hợp chỉ số video |
| Thống kê campaign theo ngày (event_analytic_daily) | Tổng hợp toàn campaign |
| Thống kê creator theo ngày (user_event_analytic_daily) | Chỉ số từng creator |

**Lưu ý:** Ngày tạo thực tế (khi nào creator bấm submit, khi nào hệ thống crawl) vẫn được giữ nguyên để đối chiếu khi cần.

---

## 3. Quy Trình Thực Hiện

```
Ngày 1-2    │  Dev cập nhật code cho phép "thời gian bổ sung"
            │  Test trên môi trường thử nghiệm
            │
Ngày 3      │  Đưa lên production
            │  Mở cửa bổ sung cho campaign
            │  Thông báo creator submit video
            │
Ngày 4-X    │  Creator submit video
            │  Hệ thống crawl lượt xem tự động
            │  (Thời gian tùy thuộc creator submit hết chưa)
            │
Sau khi     │  Đóng cửa bổ sung
creator     │  Chạy chương trình chuyển số liệu về 2025
xong        │  Kiểm tra báo cáo đúng
```

---

## 4. Chi Phí & Thời Gian

| Hạng mục | Thời gian | Chi phí |
|----------|-----------|---------|
| Bước 1: Mở cửa bổ sung (code + test + deploy) | 15 giờ | $209 |
| Bước 2: Chuyển số liệu về 2025 (script + kiểm tra) | 11 giờ | $153 |
| **Tổng cộng** | **26 giờ** | **$362** |

**Timeline:** 3-4 ngày làm việc (chưa tính thời gian chờ creator submit)

---

## 5. Rủi Ro & Lưu Ý

| Rủi ro | Mức độ | Cách xử lý |
|--------|--------|------------|
| Chuyển ngày sai | Thấp | Backup toàn bộ dữ liệu trước khi chạy. Sai thì khôi phục |
| Creator submit sau khi đã đóng | Thấp | Hệ thống tự block khi hết thời gian bổ sung |
| Báo cáo bị ảnh hưởng | Thấp | Bước 2 chuyển hết về 2025, báo cáo sạch |

**Lưu ý quan trọng:**
- **Campaign này KHÔNG có tính thưởng, KHÔNG thanh toán, KHÔNG đối soát.** Phạm vi chỉ bao gồm: creator submit video và hệ thống crawl đếm lượt xem. Chi phí và thời gian ở trên chỉ áp dụng cho phạm vi này. Nếu campaign có thêm tính thưởng, thanh toán, hoặc đối soát thì cần đánh giá lại.
- Giải pháp "thời gian bổ sung" có thể tái sử dụng cho các campaign khác sau này nếu khách hàng cần mở lại lần nữa.

---

*Xem chi tiết báo giá: reopen-campaign-estimate.csv*
