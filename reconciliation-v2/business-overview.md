# Hệ Thống Đối Soát V2+ — Tổng Quan & Lộ Trình

**Ngày cập nhật:** 25/02/2026
**Đối tượng:** Ban Thương Hiệu (BTC), Vận hành, Quản lý cấp cao

---

## Vấn Đề Cốt Lõi — Không Thể Đối Soát

**Techcombank và nhiều PnL khác hiện tại không thể thực hiện đối soát được.**

Nguyên nhân: hệ thống **dừng cào dữ liệu ngay khi campaign hết hạn**. Trong khi đó, đối soát thường diễn ra vài ngày sau khi campaign kết thúc. Đến lúc cần đối soát, không có cách nào biết:

- Video còn tồn tại trên nền tảng không?
- View có bị giảm so với thời điểm campaign không?
- Video còn đủ hashtag / điều kiện không?
- Content có bị xóa, ẩn, hoặc chuyển private không?

Kết quả: operations phải **dò từng video một** bằng cách mở link thủ công ra nền tảng để kiểm tra — không có cách nào khác. Campaign hàng trăm content là **bất khả thi**.

> **Techcombank đã yêu cầu cải tiến và bắt buộc phải hoàn thành trước đợt đối soát campaign tháng 2.**

---

## Các Vấn Đề Khác (Phụ)

Ngoài vấn đề cốt lõi trên, còn có các điểm nghẽn vận hành cần giải quyết theo thời gian:

| # | Vấn đề | Hệ quả | Giải quyết ở |
|---|--------|--------|-------------|
| 2 | Tạo đợt đối soát hoàn toàn thủ công | BTC mất thời gian thao tác lặp lại, dễ quên lịch | **V3** |
| 3 | Influencer không biết kết quả đối soát, không có kênh phản hồi chính thức | Tranh chấp qua email/chat, không có audit trail, BTC bị hỏi liên tục | **V4** |

---

## Lộ Trình Phát Triển

---

### V2 — Unblock Đối Soát *(Deadline: 28/02/2026)*

**Giải quyết vấn đề #1.**

Hệ thống tiếp tục crawl video sau khi campaign kết thúc, thay vì dừng như trước:

- Khi campaign hết hạn → hệ thống vẫn crawl toàn bộ video mỗi ngày
- Tại thời điểm đối soát → đã có sẵn snapshot: view count, trạng thái video, hashtag
- BTC tải file đối soát về → đã có đủ dữ liệu, không cần mở link thủ công

**Không làm trong V2:** Tự động hóa lịch đối soát, phân loại tự động, thông báo influencer.

---

### V3 — Lịch & Phân Loại Tự Động *(Tháng 3/2026)*

**Giải quyết vấn đề #2.**

**Lịch đối soát tự động:**

Admin cài lịch một lần khi tạo campaign, hệ thống tự tạo và xử lý từng đợt đúng hẹn:

```
Ví dụ: Campaign 3 tháng (01/01 → 31/03)
Admin cài: Đợt 1 → 31/01 | Đợt 2 → 28/02 | Đợt 3 → 31/03

→ Ngày 31/01: Hệ thống tự tạo Đợt 1, bắt đầu crawl & phân loại
→ Khi Đợt 1 xong: Hệ thống tự tạo Đợt 2
→ Khi Đợt 2 xong: Hệ thống tự tạo Đợt 3
```

**Phân loại tự động — hệ thống là nguồn phán quyết chính:**

V3 nâng cấp từ "có dữ liệu" (V2) lên "có kết luận". Hệ thống tự động phân loại từng phần thưởng dựa trên dữ liệu crawl — BTC chỉ cần xử lý những trường hợp ngoại lệ:

| Nhóm | Ý nghĩa | BTC cần làm gì? |
|------|---------|----------------|
| **Tự động duyệt** | Video còn tồn tại, view ổn định, đủ điều kiện | Không cần làm gì |
| **Cần xem xét** | View giảm đáng kể (>20%), thiếu hashtag, hoặc dữ liệu bất thường | BTC xem xét và quyết định |
| **Tự động hủy** | Video bị xóa/ẩn, view về 0, vi phạm điều kiện rõ ràng | Không cần làm gì |

BTC vẫn có toàn quyền override bất kỳ kết quả nào, kèm lý do được ghi nhận vào hệ thống.

Khi tất cả đợt hoàn thành, hệ thống gợi ý admin đóng campaign — admin xác nhận thủ công, không tự động đóng.

---

### V4 — Minh Bạch Với Creator & Luồng Kháng Cáo *(Sau tháng 3/2026)*

**Giải quyết vấn đề #3.**

**Thông báo kết quả cho influencer:**
- Khi BTC bấm "Công bố": hệ thống tự gửi email + notification đến từng influencer
- Influencer xem chi tiết trên Creator Portal: từng content, lý do duyệt/hủy, tiền dự kiến
- Cửa sổ X ngày để phản hồi — hết hạn không phản hồi = tự động chấp nhận

**Luồng kháng cáo trong hệ thống:**
- Influencer gửi kháng cáo kèm bằng chứng qua hệ thống
- BTC xét duyệt, có audit trail đầy đủ, phân quyền theo giá trị kháng cáo
- Kết quả thông báo lại ngay cho influencer

**Tự động đóng campaign:**
- Sau khi hết cửa sổ kháng cáo và không còn kháng cáo pending → hệ thống tự đóng campaign

---

### Tổng Quan Lộ Trình

| Phiên bản | Vấn đề giải quyết | Nội dung cốt lõi | Deadline | Trạng thái |
|-----------|------------------|-----------------|----------|-----------|
| **V2** | Không có dữ liệu để đối soát | Crawl sau khi campaign hết hạn | 28/02/2026 | Đang phát triển |
| **V3** | Tạo đợt thủ công, tốn thời gian | Lịch tự động, crawl & phân loại tự động | Tháng 3/2026 | Chờ phát triển |
| **V4** | Influencer không biết kết quả, không có kênh kháng cáo | Thông báo creator, kháng cáo trong hệ thống, tự động đóng campaign | Sau tháng 3 | Chờ phát triển |

---

## Luồng Làm Việc Của BTC (Từ V3)

```
[Admin cài lịch đối soát khi tạo campaign]
             ↓
[Đến ngày → Hệ thống tự tạo đợt đối soát]
             ↓
[Hệ thống tự crawl + phân loại mỗi ngày]
             ↓
[BTC nhận thông báo: "X content cần xem xét"]
             ↓
[BTC vào xem — chỉ review nhóm "Cần xem xét"]
             ↓
[BTC bấm "Công bố kết quả"]
             ↓
[BTC bấm "Chốt thanh toán" → sang bộ phận tài chính]
             ↓
[Hệ thống tự tạo đợt tiếp theo nếu còn lịch]
```

---

## Các Trạng Thái Đối Soát (Để Tham Khảo)

```
PENDING            → Vừa được tạo, chờ xử lý
PROCESSING         → Đang lấy dữ liệu rewards
PROCESSED          → Đã có dữ liệu, đang crawl & phân loại tự động
ĐANG XEM XÉT      → Crawl xong, BTC đang review các "warning" items
ĐÃ CÔNG BỐ        → BTC đã công bố kết quả cho influencer
RUNNING            → Đang chạy thanh toán
COMPLETED          → Hoàn tất
REJECTED           → Đợt này bị từ chối
```

---

## Câu Hỏi Thường Gặp

**Hỏi: Nếu một đợt bị từ chối, đợt tiếp theo có tự động tạo không?**
→ Có. "Từ chối" cũng được coi là "đã xong" — hệ thống vẫn chuyển sang đợt tiếp theo đúng lịch.

**Hỏi: BTC có thể can thiệp vào kết quả phân loại tự động không?**
→ Có. Với các item bị "Tự động hủy" hoặc "Cần xem xét", BTC vẫn có thể bấm "Override" để điều chỉnh, kèm lý do ghi nhận vào hệ thống.

**Hỏi: Hệ thống crawl có ảnh hưởng đến dữ liệu analytics thông thường không?**
→ Không. Luồng crawl cho đối soát hoàn toàn tách biệt, không ảnh hưởng đến reward hay analytics đã được tính.

**Hỏi: Campaign không dùng đối soát tự động thì sao?**
→ Hoàn toàn bình thường. Tính năng này là tùy chọn — chỉ kích hoạt khi admin cài lịch đối soát.
