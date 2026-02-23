# Hệ Thống Đối Soát Mới — Tổng Quan Cho Bộ Phận Vận Hành

**Phiên bản:** 2.0
**Ngày cập nhật:** 23/02/2026
**Đối tượng:** Ban Thương Hiệu (BTC), Vận hành, Quản lý cấp cao

---

## Vấn Đề Hiện Tại

Quy trình đối soát thủ công đang tạo ra nhiều điểm nghẽn:

| Vấn đề | Hậu quả |
|--------|---------|
| Tạo đợt đối soát hoàn toàn thủ công | BTC mất thời gian thao tác lặp lại, dễ quên lịch |
| Phải tự tra cứu từng content để kiểm tra view | Mất hàng giờ mỗi đợt đối soát |
| Không có cơ chế cảnh báo tự động khi view giảm bất thường | Rủi ro thanh toán sai cho content gian lận hoặc bị xóa |
| Mỗi campaign chỉ đối soát 1 lần cuối | Không phát hiện được gian lận xảy ra giữa chừng |
| Không biết campaign nào đã "xong hoàn toàn" | Tốn công theo dõi thủ công |

---

## Giải Pháp: Hệ Thống Đối Soát V2

### Ý tưởng cốt lõi

> **Hệ thống tự động làm phần việc lặp lại. BTC chỉ cần xem xét những trường hợp thực sự cần phán quyết.**

---

## 3 Cải Tiến Lớn

---

### 1. Lịch Đối Soát Nhiều Đợt — Cài Một Lần, Chạy Mãi

**Trước đây:** Mỗi đợt đối soát, BTC vào hệ thống → tạo thủ công → chọn thời gian → xử lý.

**Bây giờ:** Admin cài sẵn lịch khi tạo campaign. Hệ thống tự tạo từng đợt đúng hẹn.

```
Ví dụ: Campaign 3 tháng (01/01 → 31/03)
Admin cài: Đợt 1 → 31/01 | Đợt 2 → 28/02 | Đợt 3 → 31/03

→ Ngày 31/01: Hệ thống tự tạo Đợt 1, bắt đầu xử lý
→ Khi Đợt 1 xong: Hệ thống tự tạo Đợt 2
→ Khi Đợt 2 xong: Hệ thống tự tạo Đợt 3
```

**Lợi ích:**
- Không bao giờ quên lịch đối soát
- Không cần thao tác lặp lại mỗi tháng
- Đảm bảo các đợt chạy đúng thứ tự, không chồng chéo

---

### 2. Crawl & Phân Loại Tự Động — Phát Hiện Gian Lận 24/7

Sau khi đợt đối soát được tạo, hệ thống **tự động kiểm tra lại toàn bộ content mỗi ngày** cho đến khi BTC công bố kết quả.

Mỗi content sẽ được phân vào 1 trong 3 nhóm:

| Nhóm | Màu | Ý nghĩa | BTC cần làm gì? |
|------|-----|---------|----------------|
| **Tự động duyệt** | Xanh lá | View ổn định, không dấu hiệu bất thường | Không cần làm gì |
| **Cần xem xét** | Cam | View giảm đáng kể (>20%), nghi ngờ bất thường | BTC xem và quyết định |
| **Tự động hủy** | Đỏ | View về 0, link chết, dấu hiệu gian lận rõ ràng | Không cần làm gì (tự hủy) |

**Lợi ích:**
- BTC không cần check từng content — chỉ tập trung vào nhóm **"Cần xem xét"**
- Phát hiện gian lận sớm hơn, không chờ cuối đợt mới biết
- Có lịch sử view tại thời điểm đối soát để đối chiếu nếu có tranh chấp

---

### 3. Trạng Thái "Đã Hoàn Tất Hoàn Toàn" — Biết Ngay Campaign Nào Xong

**Trước đây:** Không có cách nào biết campaign đã xong hoàn toàn chưa, phải theo dõi thủ công.

**Bây giờ:** Khi tất cả các đợt đối soát đã kết thúc (hoàn thành hoặc từ chối), hệ thống tự động đánh dấu campaign là **"Đã đóng hoàn toàn"**.

Từ thời điểm đó:
- Hệ thống dừng crawl campaign này (tiết kiệm tài nguyên)
- Danh sách campaign sẽ hiển thị rõ đã xong
- Không cần theo dõi nữa

---

## Luồng Làm Việc Mới Của BTC

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

## So Sánh Trước & Sau

| | Trước V2 | Sau V2 |
|---|----------|--------|
| **Tạo đợt đối soát** | Thủ công mỗi lần | Tự động theo lịch đã cài |
| **Kiểm tra view content** | BTC tự kiểm tra từng cái | Hệ thống crawl mỗi ngày, tự phân loại |
| **Phát hiện gian lận** | Cuối đợt mới biết | Liên tục, mỗi ngày |
| **Khối lượng BTC cần xem** | Toàn bộ content | Chỉ nhóm "Cần xem xét" |
| **Biết campaign xong chưa** | Không tự động | Hệ thống tự đánh dấu "Đã đóng" |
| **Campaign dài nhiều tháng** | 1 đợt cuối | N đợt tự động theo lịch |

---

## Các Trạng Thái Đối Soát (Để Tham Khảo)

```
PENDING          → Vừa được tạo, chờ xử lý
PROCESSING       → Đang lấy dữ liệu rewards
PROCESSED        → Đã có dữ liệu, đang crawl & phân loại tự động
ĐANG XEM XÉT    → Crawl xong, BTC đang review các "warning" items
ĐÃ CÔNG BỐ      → BTC đã công bố kết quả cho influencer
RUNNING          → Đang chạy thanh toán
COMPLETED        → Hoàn tất
REJECTED         → Đợt này bị từ chối
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

---

## Tóm Tắt Giá Trị Mang Lại

1. **Tiết kiệm thời gian vận hành** — BTC không còn phải tạo thủ công hay kiểm tra view từng content
2. **Giảm rủi ro gian lận** — Phát hiện tự động mỗi ngày, không chờ đến cuối đợt
3. **Minh bạch hơn** — Mọi quyết định có lý do ghi nhận, có thể đối chiếu khi tranh chấp
4. **Scale được** — Campaign 3 tháng, 10 đợt đối soát → không tốn thêm công sức vận hành
5. **Luôn biết trạng thái thực** — Dashboard hiển thị rõ campaign nào đang đối soát, đã xong, cần xem xét

---

## Lộ Trình Phát Triển Tiếp Theo

Phiên bản V2 tập trung vào tự động hóa phần lõi. Các tính năng dưới đây đã được thiết kế và sẽ được phát triển trong các milestone tiếp theo.

---

### Milestone 3 — Công Bố Kết Quả Cho Influencer

**Vấn đề hiện tại:** Sau khi BTC công bố, influencer không biết kết quả — phải hỏi thủ công hoặc chờ email.

**Tính năng sẽ có:**

- **Thông báo tự động** khi BTC bấm "Công bố": hệ thống gửi email + thông báo trong app đến từng influencer, kèm chi tiết từng content được duyệt/bị hủy và tổng tiền dự kiến
- **Trang kết quả đối soát** trên Creator Portal: influencer tự vào xem chi tiết từng content, lý do bị hủy (nếu có), không cần hỏi BTC
- **Cửa sổ thời gian kháng cáo**: hiển thị countdown rõ ràng (ví dụ: "Còn 68 giờ để kháng cáo"), tự động nhắc nhở trước 24 giờ khi sắp hết hạn

**Lợi ích:**
- Giảm tải cho BTC: không còn bị hỏi "kết quả đâu rồi"
- Tăng trải nghiệm influencer: biết ngay, minh bạch
- Tạo "điểm không thể quay lại" — sau khi công bố, BTC không tự ý thay đổi được; mọi điều chỉnh phải qua kháng cáo có ghi nhận

---

### Milestone 4 — Luồng Kháng Cáo

**Vấn đề hiện tại:** Influencer bị hủy content không có kênh chính thức để phản hồi — dẫn đến tranh chấp qua email/chat, mất thời gian cả hai bên, thiếu audit trail.

**Tính năng sẽ có:**

- **Form kháng cáo có hướng dẫn thông minh**: tùy theo lý do bị hủy, hệ thống gợi ý loại bằng chứng cần nộp
  - Bị hủy vì "link chết" → "Vui lòng upload screenshot cho thấy link hoạt động trong thời gian campaign"
  - Bị hủy vì "view giảm bất thường" → "Giải thích lý do và đính kèm analytics từ platform"
- **Upload bằng chứng**: ảnh chụp màn hình, file PDF, tối đa 5 file
- **Hàng đợi xét duyệt cho BTC**: tab "Kháng cáo" riêng biệt, hiển thị song song kết quả gốc và bằng chứng influencer gửi lên
- **Phân quyền xét duyệt theo giá trị**:
  - Dưới 100K VND → bất kỳ BTC reviewer
  - 100K – 1M VND → BTC Senior
  - Trên 1M VND → BTC Senior + Quản lý xác nhận
- **Kết quả kháng cáo**: Duyệt toàn bộ / Duyệt một phần (điều chỉnh view count) / Từ chối kèm lý do → thông báo ngay cho influencer

**Lợi ích:**
- Tranh chấp có kênh chính thức, minh bạch, có lịch sử đầy đủ
- BTC xử lý nhanh hơn vì có đủ thông tin ngay từ đầu
- Influencer tin tưởng hơn vì có quy trình rõ ràng

---

### Milestone 5 — Phân Tích & Báo Cáo Nâng Cao

**Tính năng sẽ có:**

- **Báo cáo lý do hủy**: content bị hủy vì lý do gì nhiều nhất (link chết, view giảm, gian lận...) — phân tích theo platform, theo tháng → giúp cải thiện tiêu chí campaign
- **Báo cáo kháng cáo**: tỷ lệ kháng cáo thành công theo lý do, thời gian xử lý trung bình (SLA), influencer nào kháng cáo nhiều bất thường (fraud signal)
- **Lịch sử kiểm tra đầy đủ (Audit Trail)**: mọi thao tác trên từng content — từ lần crawl đầu tiên, phân loại tự động, override của BTC, đến kháng cáo — đều được lưu lại không thể xóa, phục vụ đối chiếu khi có tranh chấp pháp lý

---

### Tổng Quan Lộ Trình

| Milestone | Nội dung chính | Trạng thái |
|-----------|---------------|-----------|
| **V2 (hiện tại)** | Lịch đối soát tự động, crawl & phân loại tự động, đóng campaign tự động | Đang phát triển |
| **Milestone 3** | Thông báo influencer, trang xem kết quả, cửa sổ kháng cáo | Đã thiết kế, chờ phát triển |
| **Milestone 4** | Form kháng cáo, hàng đợi BTC xét duyệt, phân quyền theo giá trị | Đã thiết kế, chờ phát triển |
| **Milestone 5** | Báo cáo phân tích, audit trail đầy đủ | Đã thiết kế, chờ phát triển |
