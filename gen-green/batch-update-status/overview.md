# Cập nhật trạng thái content hàng loạt bằng file Excel

> Cho phép Ops/Admin upload 1 file Excel danh sách content cần đổi trạng thái, hệ thống đọc file → đối chiếu → preview phân loại từng dòng → admin tick xác nhận → cập nhật hàng loạt kèm lý do. Giải quyết bài toán đổi trạng thái content số lượng lớn mà hiện đang phải thao tác từng cái một trên giao diện.

**Ngày:** 01/07/2026
**Trạng thái:** Đề xuất
**Đối tượng đọc:** Business, Ops (đội duyệt content), PM
**Phạm vi:** Module content management — Gen-Green admin

---

## 1. Bối cảnh — Ops đang phải đổi trạng thái content từng cái một

Hiện tại trên admin Gen-Green, mỗi khi cần hủy (reject) 1 content — vì link lỗi, sai nội dung, vi phạm, không đủ điều kiện — Ops phải:

1. Mở trang **Danh sách content**
2. Tìm content theo ID hoặc filter
3. Click vào từng content → chọn action "Hủy" → nhập lý do → confirm
4. Lặp lại cho content tiếp theo

**Vấn đề:**

- **Mỗi đợt rà soát**, Ops thường có danh sách 50–500 content cần hủy (ví dụ: sau buổi review nội dung tuần, sau khi crawl phát hiện link chết, sau khi đối tác báo content vi phạm).
- Thao tác lặp đi lặp lại → tốn 1–2 giờ cho 1 đợt → dễ sai sót (click nhầm content, quên paste lý do).
- Không có audit trail dễ tra cứu — Ops không biết đợt rà soát tuần trước hủy những gì, lý do gì, ai làm.

> **Bối cảnh thực tế:** Đội duyệt content thường xuất file từ chức năng **Data Export** ra Excel, mark thủ công ngoài Excel xem content nào cần hủy, rồi vào admin hủy từng cái. Đây là vòng lặp dư thừa — file đã có sẵn ID + lý do, sao không upload thẳng lại để hệ thống xử lý một phát?

---

## 2. Tại sao làm theo hướng "import từ file Excel"?

### Tận dụng pattern import đã chạy tốt trong hệ thống

Gen-Green admin **đã có sẵn** một luồng import file Excel hoàn chỉnh ở chức năng **Import danh sách nhân sự** (employee registry): upload file → hệ thống đọc và đối chiếu → hiển thị **preview phân loại từng dòng** → admin **tick xác nhận** → **áp dụng hàng loạt**. Ops đã quen với luồng 3 bước này, và nó đã được kiểm chứng an toàn qua nhiều đợt import nhân sự.

Feature này **tái sử dụng chính xác pattern đó** cho content: cùng cách upload, cùng bố cục preview (counter tổng hợp + bảng phân loại + nút xác nhận), cùng cơ chế chống trùng lô. Ops không phải học UI mới, đội dev không phải xây lại từ đầu.

### Làm việc trên Excel quen thuộc

Ops đã quen xuất file → mở Excel → rà soát → đánh dấu. Việc upload lại chính file Excel đã đánh dấu là bước tự nhiên nhất, không cần công cụ mới, không cần training.

### Có preview + xác nhận trước khi ghi

Vì đây là thao tác **ghi hàng loạt không hoàn tác được**, bước preview cho Ops nhìn thấy chính xác content nào sẽ bị đổi trạng thái, lý do gì, trước khi bấm nút cuối cùng — giảm tối đa rủi ro làm nhầm.

---

## 3. Có gì mới?

### 1. Nút "Cập nhật trạng thái hàng loạt" trong trang Danh sách content

Bên cạnh các nút action hiện có, thêm 1 button mở modal upload. Modal cho phép:

- Chọn file Excel (`.xlsx`)
- Tải về **file mẫu** đúng định dạng cột
- Nếu file sai định dạng / thiếu cột bắt buộc / vượt giới hạn dòng → hiển thị lỗi ngay trên modal, không cho upload tiếp

### 2. Cấu trúc file Excel

File Excel mỗi dòng là một content cần đổi trạng thái, gồm các cột:

| Cột | Bắt buộc? | Vai trò |
|---|---|---|
| **ID content** | ✅ Có | Khóa để tìm content trong hệ thống (dạng ID hệ thống) |
| **Trạng thái mới** | ✅ Có | Trạng thái đích muốn chuyển content sang |
| **Lý do** | ⚠️ Optional | Nếu có, dùng làm lý do đổi trạng thái; nếu không, dùng lý do mặc định |

> **Phạm vi phase 1:** Cột "Trạng thái mới" ở phase này chỉ chấp nhận giá trị **`rejected` (Hủy)**. File có thể có sẵn cấu trúc cột "Trạng thái mới" để mở rộng về sau, nhưng dòng nào ghi giá trị khác `rejected` sẽ được đánh dấu **không hợp lệ** và **không áp dụng**. Xem mục 6 (Phạm vi không ảnh hưởng) và mục 7 (Hướng mở rộng).

### 3. Preview với phân loại từng dòng

Sau khi upload, hệ thống đọc file → đối chiếu từng dòng với content trong hệ thống → chuyển sang trang **Preview** hiển thị phân loại:

| Phân loại | Khi nào | Áp dụng làm gì |
|---|---|---|
| 🔴 **Sẽ hủy** | Content tồn tại + đang ở trạng thái có thể hủy (vd: `waiting_approved`, `approved`, `pending`) | Đổi trạng thái → `rejected`, ghi lý do theo file (hoặc mặc định) |
| 🟡 **Đã hủy rồi** | Content đã ở trạng thái `rejected` | Bỏ qua (no-op). Hiển thị thông tin, không đụng tới. |
| ⚠️ **Không tìm thấy** | ID content trong file không tồn tại trong hệ thống | Bỏ qua + cảnh báo. |
| ⚫ **Lỗi định dạng** | Dòng thiếu ID / ID sai định dạng / trạng thái đích không nằm trong danh sách được phép | Bỏ qua + báo lỗi rõ lý do. |

**UI preview:**
- Counter tổng hợp mỗi phân loại (số dòng sẽ hủy / đã hủy rồi / không tìm thấy / lỗi)
- Bộ lọc theo phân loại
- Bảng hiển thị: ID, tiêu đề content, người đăng, sự kiện, badge phân loại, lý do sẽ áp dụng
- Thanh trên: nút **Hủy bỏ** / **Áp dụng**
- Chân trang: checkbox "Xác nhận hủy N content" — bắt buộc tick trước khi Áp dụng

### 4. Xử lý lô lớn không làm treo hệ thống

Giống luồng import nhân sự: file nhỏ xử lý ngay trong lúc upload; file lớn (nhiều dòng) được xử lý ở chế độ **chạy nền**, giao diện hiển thị **thanh tiến độ** và tự cập nhật cho tới khi xong. Nhờ vậy đợt import hàng nghìn content không làm treo trình duyệt hay timeout.

### 5. Chống trùng lô import

Khi đang có 1 đợt import chưa hoàn tất (đang preview hoặc đang chạy), hệ thống **chặn tạo đợt mới** để tránh chồng chéo và nhầm lẫn. Ops phải xử lý dứt điểm đợt cũ (áp dụng hoặc hủy bỏ) trước khi bắt đầu đợt mới.

### 6. Lịch sử import

Mỗi đợt import được lưu lại với:
- File Excel gốc (đính kèm)
- Snapshot kết quả preview (content nào bị hủy, lý do gì)
- Người thực hiện + thời gian
- Trạng thái đợt: đang xem trước / đã áp dụng / đã hủy bỏ

Ops có thể vào **Lịch sử import** để xem lại các đợt cũ — phục vụ audit, đối soát, tra cứu khi creator khiếu nại.

---

## 4. Lợi ích kỳ vọng

### Cho Ops
- ✅ Hủy 500 content trong 2–3 phút thay vì 1–2 giờ
- ✅ Làm việc trên Excel quen thuộc, không cần học UI mới
- ✅ Có preview để check trước khi hủy → giảm rủi ro làm nhầm
- ✅ Có audit trail rõ ràng: ai hủy, khi nào, lý do gì, từ file nào

### Cho người tạo content (Creator)
- ✅ Lý do hủy chi tiết hơn (Ops có không gian Excel để viết kỹ) → hiểu rõ lý do, ít khiếu nại
- ✅ Nhận thông báo hủy nhanh hơn (hủy hàng loạt một phát)

### Cho hệ thống
- ✅ Giảm số thao tác lẻ tẻ → ít load hơn
- ✅ Audit trail chuẩn dạng bulk operation → dễ truy vết khi có sự cố

### Cho vận hành (Tech)
- ✅ Reuse pattern preview/apply + model lịch sử import từ feature import nhân sự → ít code mới, ít rủi ro logic
- ✅ Reuse dịch vụ hủy content hàng loạt đã có sẵn trong hệ thống

---

## 5. Chi phí và rủi ro

### Chi phí

| Hạng mục | Ước tính |
|----------|----------|
| Dev backend (parser Excel, match engine, apply service, lịch sử) | 8h |
| Dev frontend (modal upload, preview page, lịch sử import) | 4h |
| QA + test với file Excel thực tế của Ops | 4h |
| PM (review spec, nghiệm thu) | 2h |
| Tổng | ~18h (~2.5 ngày công) |

### Rủi ro & cách xử lý

| Rủi ro | Mức độ | Cách xử lý |
|--------|--------|------------|
| Ops upload nhầm file → hủy nhầm content | **Cao** | Bắt buộc bước Preview + checkbox xác nhận "Hủy N content" trước Áp dụng. Hiển thị counter to + cảnh báo khi số lượng hủy lớn. |
| Không có chức năng hoàn tác (rollback) | **Cao** | Phase 1 là thao tác **1 chiều**. Preview + checkbox xác nhận là phòng tuyến chính. Lỡ hủy nhầm → Ops phải vào phục hồi thủ công từng content. Chấp nhận tradeoff để giữ scope phase 1 gọn. |
| File Excel định dạng lạ (ID bị Excel format thành số, dòng trống thừa) | TB | Parser đọc giá trị ô ở dạng thô (giữ nguyên leading zero), bỏ qua dòng trống hoàn toàn. Test với file thực tế từ Ops. |
| ID content trong file không tồn tại (content đã bị xóa) | Thấp | Đánh dấu "Không tìm thấy", bỏ qua + cảnh báo, không làm hỏng cả lô. |
| 2 Ops upload cùng lúc → chồng lô | TB | Chặn tạo lô mới khi đang có lô cũ chưa áp dụng/hủy bỏ (giống import nhân sự). |
| File quá lớn → treo/timeout | Thấp | Phase 1 giới hạn số dòng tối đa mỗi file; lô lớn xử lý chạy nền + poll tiến độ. |

---

## 6. Phạm vi không ảnh hưởng

Tài liệu này **không thay đổi:**

- Chức năng hủy content lẻ trên trang Danh sách content (giữ nguyên cho case hủy 1–2 content)
- Logic crawl content / submit content / duyệt content
- Cấu trúc trạng thái content hiện có (chỉ tiêu thụ trạng thái đích `rejected`)
- Các trạng thái đích khác ngoài `rejected` (approve / reset về chờ / ...) — **ngoài phạm vi phase 1**, dòng nào ghi trạng thái khác sẽ bị đánh dấu lỗi
- Chức năng hoàn tác (rollback) cả lô — **không có ở phase 1**
- Luồng import nhân sự (employee registry) — chạy độc lập, chỉ mượn lại pattern/model
- Chức năng **Data Export** — chỉ tiêu thụ output, không động vào logic Export

---

## 7. Hướng mở rộng (sau phase 1)

- **Mở rộng trạng thái đích:** cho phép import chuyển content sang `approved`, `pending`, `waiting_approved`... với bảng transition hợp lệ (chặn các chuyển đổi vô lý). Kiến trúc phase 1 đã tách cột "Trạng thái mới" sẵn để dễ mở rộng.
- **Rollback cả lô:** lưu trạng thái cũ từng content để hoàn tác một phát (giống import nhân sự / event bonus).
- **Nhận diện cột theo label header linh hoạt:** cho phép upload thẳng file Data Export không cần chỉnh cột (nhận cột theo tên tiêu đề thay vì thứ tự cố định).

---

## 8. Câu hỏi còn để ngỏ

1. **Số dòng tối đa / file:** giới hạn bao nhiêu là hợp lý theo usage thực tế của Ops? → Cần kiểm tra file thực tế.
2. **Thông báo cho creator khi content bị hủy:** gửi từng cái hay batch 1 thông báo? → Ưu tiên tận dụng cơ chế thông báo hủy content hiện có.
3. **Phân quyền:** dùng quyền "Hủy content" hiện có hay tạo quyền riêng cho action bulk? → Cần PM xác nhận.

---

## 9. Tài liệu liên quan

- **Pattern tham chiếu (đã chạy production):** Import danh sách nhân sự Gen-Green — luồng upload/preview/apply, phân loại action, 2 lớp xác nhận, xử lý async + chống trùng lô
- **Feature tương tự (doc):** [`../import-content-to-reject/overview.md`](../import-content-to-reject/overview.md) — hủy content hàng loạt qua CSV (phiên bản trước, cùng bài toán)
- **Feature import Excel gần nhất (doc):** [`../import-event-bonus/PRD.md`](../import-event-bonus/PRD.md) — pattern upload/preview/apply Excel đầy đủ nhất hiện tại
- **PRD:** [`prd.md`](./prd.md)
- **Tech Spec:** [`tech-spec.md`](./tech-spec.md)

---

*Có thắc mắc / phản hồi, liên hệ team Gen-Green Ops.*
