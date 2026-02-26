# Hệ Thống Đối Soát V2+ — Tổng Quan & Lộ Trình

**Ngày cập nhật:** 26/02/2026
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

**Nguyên tắc thiết kế:** Tất cả luồng hiện tại giữ nguyên. V2 chỉ bổ sung — không sửa code cũ.

**Crawl snapshot:**

- Hệ thống crawl video hàng ngày và lưu snapshot vào bảng riêng (`reconciliation_snapshots`)
- Khi event còn active: daily crawl hiện tại đồng thời insert snapshot (phục vụ đối soát giữa kỳ)
- Khi event đã hết hạn: job crawl riêng tiếp tục chạy hàng ngày cho đến khi đối soát hoàn tất
- Job crawl dừng khi: admin đóng đối soát, hoặc không còn reward pending

**Hiển thị dữ liệu:**

- Tại thời điểm đối soát → đã có sẵn snapshot: view count, hashtag
- BTC tải file đối soát về → đã có đủ dữ liệu, không cần mở link thủ công

**Không làm trong V2:** Tự động hóa lịch đối soát, phân loại tự động, thông báo influencer.

---

### V3 — Checklist Đối Soát & Phân Loại Tự Động *(Tháng 3/2026)*

**Giải quyết vấn đề #2.**

#### Checklist đối soát — ngôn ngữ chung giữa các bên

Mỗi item đối soát (reward) có một bộ checklist — là các điều kiện business mà **influencer, admin, brand đều nhìn thấy và đồng ý**. Hệ thống tự thu thập bằng chứng (snapshot) để xác minh từng điều kiện.

Checklist khác nhau tùy loại reward:

**Checklist cho loại thưởng theo View (`by_view`):**

| # | Điều kiện | Mô tả |
|---|-----------|-------|
| 1 | Video có thể truy cập công khai | Video chưa bị xóa, chưa bị ẩn, chưa chuyển private |
| 2 | Video còn đủ hashtag campaign | Influencer chưa gỡ hashtag sau khi nhận thưởng |
| 3 | Lượt xem không giảm so với đã ghi nhận | Không có dấu hiệu view ảo bị platform gỡ |

**Checklist cho loại thưởng theo Milestone (`by_milestone`):**

| # | Điều kiện | Mô tả |
|---|-----------|-------|
| 1 | Admin xác nhận | Hệ thống không tự xác minh được milestone — bắt buộc admin review |

Loại `by_milestone` luôn rơi vào nhóm "Cần xem xét" vì điều kiện duy nhất luôn ở trạng thái chưa xác minh. Đây là giải pháp tạm ở giai đoạn V3 — Techcombank hiện chưa sử dụng loại thưởng này. V5+ sẽ làm rõ checklist riêng cho `by_milestone` khi có nhu cầu thực tế.

#### Trạng thái checklist item

Mỗi checklist item có 3 trạng thái:

| Trạng thái | Nghĩa | Ai đánh? |
|---|---|---|
| ✅ Pass | Xác nhận đạt | Hệ thống (tự động từ snapshot) hoặc Admin (thủ công) |
| ❌ Fail | Xác nhận vi phạm | Hệ thống (tự động từ snapshot) hoặc Admin (thủ công) |
| ⚠️ Chưa xác minh | Chưa có kết luận | Mặc định khi không có bằng chứng — chờ admin đánh |

#### Phân loại tự động dựa trên checklist

Khi có snapshot, hệ thống tự đánh giá từng checklist item. Khi fail, mỗi điều kiện có mức xử lý riêng:

**Với `by_view`:**

| # | Điều kiện | Fail → | Lý do |
|---|-----------|--------|-------|
| 1 | Video có thể truy cập công khai | 🔴 Auto reject | Nội dung không còn tồn tại = không phục vụ campaign |
| 2 | Video còn đủ hashtag campaign | 🔴 Auto reject | Vi phạm điều kiện campaign rõ ràng |
| 3 | Lượt xem không giảm | ⚠️ Warning | View có thể dao động tự nhiên, cần admin đánh giá |

**Khi hệ thống không lấy được bằng chứng** (crawl fail): tất cả checklist item ở trạng thái "Chưa xác minh" → chờ admin đánh thủ công.

#### Admin xử lý checklist "Chưa xác minh"

Khi checklist item ở trạng thái ⚠️ Chưa xác minh (do crawl fail hoặc do loại reward cần review thủ công), admin cần đánh tay:

**Với `by_view` — khi crawl fail:**

| Checklist item | Admin làm gì | Đánh |
|---|---|---|
| Video có thể truy cập công khai | Mở link video trên platform → video load được không? | ✅ hoặc ❌ |
| Video còn đủ hashtag campaign | Mở link → đọc caption, kiểm tra hashtag | ✅ hoặc ❌ |
| Lượt xem không giảm | Mở link → xem view count, so với view đã ghi nhận | ✅ hoặc ❌ |

**Với `by_milestone`:**

| Checklist item | Admin làm gì | Đánh |
|---|---|---|
| Admin xác nhận | Xem xét reward theo tiêu chí milestone của event | ✅ hoặc ❌ |

**Thao tác nhanh:**

| Action | Khi nào dùng |
|---|---|
| **Duyệt nhanh** | Admin mở link, thấy video ổn → pass tất cả item cùng lúc |
| **Hủy nhanh** | Admin mở link, thấy video đã xóa → fail tất cả item cùng lúc |
| **Đánh từng item** | Một số item pass, một số fail → đánh riêng từng cái |

Sau khi admin đánh xong tất cả item chưa xác minh → hệ thống tổng hợp lại kết quả cuối cùng.

#### Tổng hợp kết quả

| Kết quả | Điều kiện | BTC cần làm gì? |
|---------|-----------|----------------|
| **Tự động duyệt** | Tất cả checklist pass | Không cần làm gì |
| **Tự động hủy** | Bất kỳ checklist nào fail với mức auto reject | Không cần làm gì (có thể override) |
| **Cần xem xét** | Có warning hoặc có item chưa xác minh | Admin đánh thủ công từng item, sau đó hệ thống tổng hợp |

BTC vẫn có toàn quyền override bất kỳ kết quả nào, kèm lý do được ghi nhận vào hệ thống.

---

### V4 — Lịch Đối Soát Tự Động & Minh Bạch Với Creator *(Sau tháng 3/2026)*

**Giải quyết vấn đề #2 (phần lịch tự động) và #3.**

#### Lịch đối soát tự động

Admin cài lịch một lần khi tạo campaign, hệ thống tự tạo và xử lý từng đợt đúng hẹn:

```
Ví dụ: Campaign 3 tháng (01/01 → 31/03)
Admin cài: Đợt 1 → 31/01 | Đợt 2 → 28/02 | Đợt 3 → 31/03

→ Ngày 31/01: Hệ thống tự tạo Đợt 1, dùng snapshot gần nhất để evaluate
→ Khi Đợt 1 xong: Hệ thống tự tạo Đợt 2
→ Khi Đợt 2 xong: Hệ thống tự tạo Đợt 3
```

Khi tất cả đợt hoàn thành, hệ thống gợi ý admin đóng campaign — admin xác nhận thủ công, không tự động đóng.

#### Thông báo kết quả cho influencer
- Khi BTC bấm "Công bố": hệ thống tự gửi email + notification đến từng influencer
- Influencer xem chi tiết trên Creator Portal: từng content, checklist result, lý do duyệt/hủy, tiền dự kiến
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
| **V2** | Không có dữ liệu để đối soát | Snapshot hàng ngày, hiển thị trong đối soát & export | 28/02/2026 | Đang phát triển |
| **V3** | Đối soát thủ công, tốn thời gian | Checklist đối soát, phân loại tự động | Tháng 3/2026 | Chờ phát triển |
| **V4** | Tạo đợt thủ công, influencer không biết kết quả | Lịch đối soát tự động, thông báo creator, kháng cáo | Sau tháng 3 | Chờ phát triển |

---

## Luồng Làm Việc Của BTC (Từ V3)

```
[Admin tạo đợt đối soát thủ công (V3) hoặc hệ thống tự tạo theo lịch (V4)]
             ↓
[Hệ thống dùng snapshot gần nhất → evaluate checklist → phân loại tự động]
             ↓
[BTC nhận thông báo: "X content cần xem xét"]
             ↓
[BTC vào xem — chỉ review nhóm "Cần xem xét" và "Chưa xác minh"]
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
PROCESSED          → Đã có dữ liệu, đang evaluate checklist & phân loại
REVIEWING          → Evaluate xong, BTC đang review các warning items
PUBLISHED          → BTC đã công bố kết quả cho influencer
RUNNING            → Đang chạy thanh toán
COMPLETED          → Hoàn tất
REJECTED           → Đợt này bị từ chối
```

---

## Câu Hỏi Thường Gặp

**Hỏi: Nếu một đợt bị từ chối, đợt tiếp theo có tự động tạo không?**
→ Có. "Từ chối" cũng được coi là "đã xong" — hệ thống vẫn chuyển sang đợt tiếp theo đúng lịch.

**Hỏi: BTC có thể can thiệp vào kết quả phân loại tự động không?**
→ Có. Với các item bị "Tự động hủy" hoặc "Cần xem xét", BTC vẫn có thể override, kèm lý do ghi nhận vào hệ thống.

**Hỏi: Khi hệ thống không crawl được video thì sao?**
→ Tất cả checklist item chuyển sang "Chưa xác minh". Admin mở link thủ công và đánh trạng thái cho từng điều kiện.

**Hỏi: Hệ thống crawl có ảnh hưởng đến dữ liệu analytics thông thường không?**
→ Không. Snapshot cho đối soát lưu vào bảng riêng, không ảnh hưởng đến reward hay analytics đã được tính. Khi event còn active, daily crawl hiện tại đồng thời insert snapshot — nhưng không thay đổi logic analytics.

**Hỏi: Campaign không dùng đối soát tự động thì sao?**
→ Hoàn toàn bình thường. Tính năng này là tùy chọn — chỉ kích hoạt khi admin cài lịch đối soát.

**Hỏi: Job crawl đối soát chạy đến khi nào?**
→ Dừng khi admin đóng đối soát, hoặc khi không còn reward pending cho event đó.
