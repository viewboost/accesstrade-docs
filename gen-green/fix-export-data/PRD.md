# PRD — Sửa lỗi luồng Export bị kẹt ở trang Admin

**Ngày:** 2026-05-25
**Người thực hiện:** Thanh Trung
**Phạm vi:** Backend admin — chức năng xuất dữ liệu (Export)

---

## 1. Vấn đề

Trên trang Admin có chức năng "Xuất dữ liệu" (export sang Excel/CSV) cho nhiều loại báo cáo: nội dung, đối soát, người dùng, giao dịch, v.v.

**Triệu chứng người dùng gặp:**
- Bấm "Export" → đơn export bị treo ở trạng thái **"Đang chạy"** (Running) hoặc **"Chờ"** (Waiting) mãi không xong.
- Mọi đơn export tạo sau đó cũng bị kẹt theo, không chạy được.
- **Giải pháp tạm thời duy nhất:** restart server backend, sau đó vẫn còn xác suất kẹt lại.

**Tần suất:** Lặp lại thường xuyên, ảnh hưởng trực tiếp đến team vận hành cần data hàng ngày.

---

## 2. Nguyên nhân

Hệ thống export hoạt động theo cơ chế hàng đợi (queue): đơn export mới sẽ vào trạng thái "Chờ", hệ thống pick từng đơn ra "Đang chạy", chạy xong thì chuyển "Hoàn thành" / "Thất bại". Giới hạn tối đa 2 đơn chạy song song.

**Các lỗ hổng khiến queue bị tắc:**

| # | Nguyên nhân | Hệ quả |
|---|---|---|
| 1 | Khi server crash/restart giữa lúc đang chạy export, đơn đó vẫn bị ghi nhận "Đang chạy" trong database — nhưng tiến trình thực tế đã chết | Hệ thống đếm thấy đã đủ 2 đơn "Đang chạy" → không pick đơn mới nữa → **queue đứng hình** |
| 2 | Sau khi 1 đơn chạy xong, hệ thống **không tự pick đơn kế tiếp** trong hàng đợi | Đơn sau phải đợi cron 1 tiếng/lần mới được chạy, hoặc đợi có người tạo export mới |
| 3 | Một lỗi nhỏ trong code (gọi đóng file khi file chưa tạo được) có thể làm crash tiến trình → đơn export đó kẹt vĩnh viễn ở "Đang chạy" | Cùng hệ quả như #1 |
| 4 | Không có cơ chế "timeout" cho đơn chạy quá lâu | Đơn treo do mạng/storage chậm sẽ không bao giờ tự thoát |
| 5 | Nhiều luồng có thể cùng pick 1 đơn export do không có khóa đồng bộ | Race condition → có lúc 1 đơn bị chạy 2 lần, có lúc vượt giới hạn 2 đơn song song |

---

## 3. Giải pháp đã triển khai

### 3.1. Tự dọn dẹp khi server khởi động lại
Mỗi lần server bật lên, hệ thống tự động:
- Tìm các đơn đang ghi nhận "Đang chạy" (chắc chắn là đơn zombie vì tiến trình đã chết khi restart).
- Đưa các đơn đó về lại trạng thái "Chờ" để hệ thống pick lại từ đầu.
- Kích hoạt ngay một vòng pick mới — **không cần đợi cron 1 tiếng**.

→ **Người dùng không còn phải chờ hay can thiệp thủ công.**

### 3.2. Timeout cho đơn chạy quá lâu
Đơn nào ở trạng thái "Đang chạy" quá **30 phút** sẽ tự động bị đánh dấu "Thất bại" (kèm lý do "job timeout"). Người dùng có thể tạo lại đơn mới.

→ **Không còn tình trạng kẹt vĩnh viễn dù vì lý do gì.**

### 3.3. Tự động chạy đơn kế tiếp
Sau khi 1 đơn export hoàn thành (dù thành công hay thất bại), hệ thống tự động kích hoạt vòng pick mới để chạy đơn "Chờ" tiếp theo.

→ **Hàng đợi chạy liên tục, không còn ngắt quãng đợi 1 tiếng.**

### 3.4. Chống crash do lỗi bất ngờ
Toàn bộ luồng xử lý export được bọc trong cơ chế bắt lỗi (recover). Nếu xảy ra lỗi bất ngờ (kết nối storage, database lỗi…), đơn sẽ được đánh dấu "Thất bại" kèm lý do thay vì làm chết tiến trình.

→ **1 đơn lỗi không kéo cả queue chết theo.**

### 3.5. Khóa đồng bộ qua Redis (chống race condition)
Sử dụng Redis lock để đảm bảo **toàn cluster (kể cả khi chạy nhiều server admin song song) chỉ có 1 tiến trình pick đơn tại 1 thời điểm**. Nếu Redis lock fail (đang có tiến trình khác chạy), caller bỏ qua thay vì xếp hàng.

→ **Đảm bảo nhất quán dữ liệu, đúng giới hạn 2 đơn song song.**

---

## 4. Tác động đến người dùng

| Trước | Sau |
|---|---|
| Đơn export kẹt → phải báo dev restart server | Hệ thống tự khôi phục khi restart |
| Restart xong vẫn đợi tới 1 tiếng để đơn kế tiếp chạy | Đơn kế tiếp chạy ngay sau khi đơn trước xong |
| Không biết tại sao đơn kẹt | Đơn lỗi có ghi rõ lý do (timeout, panic, server restart) |
| Vận hành mất giờ chờ data, ảnh hưởng KPI | Data có đúng hạn, không cần can thiệp thủ công |

---

## 5. Rủi ro & lưu ý

- **Timeout 30 phút** là giá trị mặc định. Nếu có đơn export rất nặng (vài chục triệu dòng) có thể chạy lâu hơn 30 phút và bị đánh dấu thất bại nhầm — cần monitor và điều chỉnh nếu cần.
- **Đơn "Thất bại" do timeout không tự retry** để tránh loop vô hạn khi nguyên nhân là lỗi cố hữu. Người dùng cần tạo lại đơn thủ công.
- **Redis là dependency bắt buộc** — nếu Redis chết, cơ chế khóa sẽ fail, CheckRun sẽ bị skip cho đến khi Redis sống lại (an toàn nhưng queue tạm dừng).

---

## 6. Đề xuất tiếp theo (optional)

- **Ngắn hạn:** Đổi cron `RunExportData` từ 1 tiếng/lần → 5 phút/lần để rút ngắn thời gian phục hồi worst-case.
- **Dài hạn:** Chuyển sang job queue chuyên dụng (Asynq + Redis) thay cho cơ chế goroutine ad-hoc hiện tại — sẽ có sẵn retry, dashboard monitor, scheduling, priority queue.

---

## 7. Files thay đổi

- [backend/pkg/admin/service/export.go](../../backend/pkg/admin/service/export.go) — logic queue, timeout, recover, Redis lock
- [backend/pkg/admin/server/bootstrap.go](../../backend/pkg/admin/server/bootstrap.go) — reset zombie jobs khi khởi động
- [backend/internal/module/redis/mutex.go](../../backend/internal/module/redis/mutex.go) — thêm helper `NewMutexNoRetry`
