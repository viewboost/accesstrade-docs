# Import file để hủy hàng loạt content

> Cho phép Ops/Admin upload 1 file CSV danh sách content cần hủy, hệ thống đọc file → đối chiếu → preview → admin xác nhận → hủy hàng loạt kèm lý do. Giải quyết bài toán hủy content số lượng lớn mà hiện đang phải hủy từng cái một trên giao diện.

**Ngày:** 11/05/2026
**Trạng thái:** Đề xuất
**Đối tượng đọc:** Business, Ops (đội duyệt content), PM
**Phạm vi:** Module content management — Gen-Green admin

---

## 1. Bối cảnh — Ops đang phải hủy content từng cái một

Hiện tại trên admin Gen-Green, mỗi khi cần hủy 1 content (vì link lỗi, sai nội dung, vi phạm, không đủ điều kiện...), Ops phải:

1. Mở trang **Danh sách content**
2. Tìm content theo ID hoặc filter
3. Click vào từng content → chọn action "Hủy" → nhập lý do → confirm
4. Lặp lại cho content tiếp theo

**Vấn đề:**

- **Mỗi đợt rà soát**, Ops thường có danh sách 50–500 content cần hủy (ví dụ: sau buổi review nội dung tuần, sau khi crawl phát hiện link chết, sau khi đối tác báo content vi phạm).
- Thao tác lặp đi lặp lại → tốn 1–2 giờ cho 1 đợt → dễ sai sót (click nhầm content, quên paste lý do).
- Không có audit trail dễ tra cứu — Ops không biết đợt rà soát tuần trước hủy những gì, lý do gì.

> **Bối cảnh thực tế:** Đội duyệt content thường xuất file CSV từ chức năng **Data Export → type Content**, mark thủ công ngoài Excel xem cái nào hủy, rồi vào admin hủy từng cái. Đây là vòng lặp dư thừa — file đã có sẵn ID + lý do, sao không upload thẳng lại?

---

## 2. Tại sao làm theo hướng "import từ file CSV export ra"?

### Tận dụng pipeline có sẵn

Chức năng **Data Export type Content** đã sinh ra file CSV chuẩn với đủ thông tin: ID content, link, người đăng, sự kiện, trạng thái, lý do hủy (nếu đã hủy)... Đây chính là format **tự nhiên nhất** để Ops làm việc:

1. Export ra → mở Excel → đánh dấu content cần hủy (sửa cột `Trạng thái` thành `rejected`, điền cột `Lý do hủy`)
2. Upload lại file đã sửa → hệ thống đọc → hủy theo file

→ Không cần học format mới, không cần template riêng, không cần training.

### Cột linh hoạt theo lựa chọn export

Vì chức năng **Data Export** cho phép Ops chọn cột export (có thể chỉ 5 cột, có thể full 20+ cột), file CSV upload sẽ **không có cấu trúc cột cố định**. Hệ thống phải nhận diện cột bằng **label header** (vd: cột nào có header "ID" = ID content, cột nào có header "Lý do hủy" = rejection reason), không dựa vào thứ tự cột.

### Tham chiếu pattern đã hoạt động tốt

Feature [Import nhân viên Gen-Green](../registration-grouping/overview-v2-import-logic.md) đã chạy ổn với pattern **2 bước: Preview → Apply**. Reuse pattern này: admin upload → xem preview với phân loại từng dòng → tick xác nhận → apply hàng loạt. Pattern này đã được Ops làm quen, ít rủi ro hủy nhầm.

---

## 3. Có gì mới?

### 1. Nút "Hủy hàng loạt từ file" trong trang Danh sách content

Bên cạnh các nút action hiện có, thêm 1 button mở modal upload. Modal cho phép:
- Kéo thả hoặc chọn file CSV
- Hệ thống tự detect file CSV xuất từ Data Export (so khớp label header)
- Nếu file sai format / thiếu cột bắt buộc → hiển thị lỗi ngay trên modal, không cho upload tiếp

### 2. Cột bắt buộc và cột tùy chọn

Hệ thống đọc file CSV theo **label header**, không theo thứ tự cột. Quy ước:

| Loại | Label header trong file | Bắt buộc? | Vai trò |
|---|---|---|---|
| ID content | `ID` | ✅ Có | Khóa để tìm content trong DB |
| Lý do hủy | `Lý do hủy` | ⚠️ Optional | Nếu có, dùng làm rejection reason; nếu không, dùng default "Hủy hàng loạt từ import [tên file] [ngày]" |
| Trạng thái | `Trạng thái` | ⚠️ Optional | Filter — chỉ xử lý dòng có giá trị `rejected` (xem mục 4) |
| Các cột khác | (bất kỳ) | ❌ Không | Bỏ qua, không ảnh hưởng logic |

→ Ops chỉ cần file có cột `ID` là chạy được. Có thêm `Lý do hủy` và `Trạng thái` thì kết quả chính xác hơn.

### 3. Preview với phân loại từng dòng

Sau khi upload, hệ thống parse file → đối chiếu từng dòng với DB → redirect sang trang Preview hiển thị:

**Phân loại action cho mỗi dòng:**

| Action | Khi nào | Apply làm gì |
|---|---|---|
| 🔴 `will_reject` | Content tồn tại trong DB + đang ở trạng thái có thể hủy (vd: `approved`, `pending`) | Đổi status → `rejected`, set `rejectReason` theo file (hoặc default) |
| 🟡 `already_rejected` | Content đã ở trạng thái `rejected` rồi | No-op. Hiển thị info, không touch. |
| ⚠️ `not_found` | ID content trong file không tồn tại trong DB | Skip. Hiển thị warning, không thể hủy. |
| ⚫ `invalid` | Dòng thiếu cột `ID` hoặc ID sai format | Skip. Hiển thị lỗi. |
| ⚪ `filtered_out` | Có cột `Trạng thái` nhưng giá trị khác `rejected` | Bỏ qua, không count vào danh sách hủy (xem mục 4) |

**UI preview:**
- Counter pills tổng số mỗi loại action
- Filter dropdown theo action / sự kiện / người đăng
- Table hiển thị ID, link, tiêu đề content, người đăng, action badge, lý do hủy sẽ apply
- Top bar: nút **Hủy bỏ** / **Apply**
- Footer: checkbox "Xác nhận hủy N content" — bắt buộc tick trước khi Apply

### 4. Filter theo cột `Trạng thái` (nếu có)

Nếu file CSV có cột `Trạng thái`, hệ thống **chỉ xử lý các dòng có giá trị `rejected`** trong cột này. Các dòng có giá trị khác (`approved`, `pending`, `published`...) sẽ được đánh dấu `filtered_out` và **không hiện trong danh sách hủy**.

**Lý do:** File export thường chứa cả content đang OK lẫn content cần hủy. Ops chỉ cần đổi cột `Trạng thái` thành `rejected` cho những dòng muốn hủy → khỏi xóa các dòng khác khỏi file.

**Nếu file KHÔNG có cột `Trạng thái`:** Hệ thống coi như tất cả dòng đều là yêu cầu hủy.

> ⚠️ **Lưu ý cho Ops:** Nếu upload nhầm file full export mà không filter cột `Trạng thái`, hệ thống sẽ hủy **toàn bộ content trong file**. Đây là lý do bắt buộc có **bước preview + checkbox xác nhận** trước Apply.

### 5. Lịch sử import

Mỗi đợt import được lưu lại với:
- File CSV gốc (đính kèm)
- Snapshot kết quả preview (ai bị hủy, lý do gì)
- Người thực hiện + thời gian
- Trạng thái: `preview` / `applied` / `cancelled`

Ops có thể vào **Lịch sử import content** để xem lại các đợt cũ — phục vụ audit, đối soát, tra cứu khi creator khiếu nại.

---

## 4. Lợi ích kỳ vọng

### Cho Ops
- ✅ Hủy 500 content trong 2–3 phút thay vì 1–2 giờ
- ✅ Làm việc trên Excel/Sheets quen thuộc, không cần học UI mới
- ✅ Có preview để check trước khi hủy → giảm rủi ro hủy nhầm
- ✅ Có audit trail rõ ràng: ai hủy, khi nào, lý do gì, từ file nào

### Cho người tạo content (Creator)
- ✅ Lý do hủy chi tiết hơn (vì Ops có không gian Excel để viết kỹ) → hiểu rõ lý do, ít khiếu nại
- ✅ Nhận thông báo hủy nhanh hơn (vì hủy hàng loạt 1 phát)

### Cho hệ thống
- ✅ Giảm số API call lẻ tẻ → ít load cho DB
- ✅ Audit trail chuẩn dạng bulk operation → dễ truy vết khi có sự cố

### Cho vận hành (Tech)
- ✅ Reuse pattern preview/apply từ feature import nhân viên → ít code mới, ít rủi ro logic
- ✅ Reuse model `import_history` + `import_changes` → consistent với các luồng import khác

---

## 5. Chi phí và rủi ro

### Chi phí

| Hạng mục | Ước tính |
|----------|----------|
| Dev backend (parser CSV theo label header, match engine, apply service) | 8h |
| Dev frontend (modal upload, preview page, lịch sử import) | 4h |
| QA + test với file CSV thực tế của Ops | 4h |
| PM (review spec, nghiệm thu) | 2h |
| Tổng | ~18h (~2.5 ngày công) |

### Rủi ro & cách xử lý

| Rủi ro | Mức độ | Cách xử lý |
|--------|--------|------------|
| Ops upload nhầm file → hủy toàn bộ content | **Cao** | Bắt buộc bước Preview + checkbox xác nhận "Hủy N content" trước Apply. Default cột `Trạng thái` filter `= rejected` để chỉ hủy dòng được mark. |
| File CSV format lạ (Excel xuất ra với BOM, separator khác, encoding khác) | TB | Parser nhận dạng autodetect encoding (UTF-8 / UTF-8 BOM / Windows-1258), separator (`,` / `;`). Test với file thực tế từ Ops. |
| ID content trong file không tồn tại (content đã bị xóa) | Thấp | Action `not_found`, skip + cảnh báo, không fail cả batch. |
| 2 Ops upload cùng lúc → race condition | TB | Lock theo nguyên tắc "đợt cũ chưa apply/cancel thì không cho upload đợt mới" (giống registration import). |
| Hủy xong mới phát hiện sai | TB | Bước preview + checkbox xác nhận là phòng tuyến chính. Nếu lỡ apply nhầm, Ops phải vào sửa thủ công từng content (chấp nhận tradeoff để giữ scope phase 1 gọn). |
| File quá lớn (>10k dòng) | Thấp | Phase 1 giới hạn 5000 dòng / file. Nếu cần lớn hơn, làm async job phase sau. |

---

## 6. Phạm vi không ảnh hưởng

Tài liệu này **không thay đổi:**

- Chức năng hủy content lẻ trên trang Danh sách content (giữ nguyên cho case hủy 1–2 content)
- Logic crawl content / submit content / approve content
- Cấu trúc bảng content trong DB (chỉ thêm column tham chiếu đợt import nếu cần audit)
- Chức năng **Data Export** — chỉ tiêu thụ output của Export, không động vào logic Export
- Các luồng import khác (import nhân viên Gen-Green, import decision rules) — chạy độc lập

---

## 7. Câu hỏi còn để ngỏ

1. **Notification cho creator khi content bị hủy:** Gửi từng cái 1 hay batch 1 thông báo "N content của bạn đã bị hủy"? → Ưu tiên gửi từng cái để creator biết content cụ thể nào.
2. **Cột `Lý do hủy` để trống:** Dùng default reason ("Hủy hàng loạt từ import") hay bắt buộc Ops điền? → Đề xuất: cho phép trống, dùng default. Ops có quyền chủ động.
3. **Có cần phân quyền riêng cho action này không?** Hay tận dụng quyền "Hủy content" hiện có? → Cần PM xác nhận.
4. **Số dòng tối đa / file:** 5000 là vừa hay nên thấp hơn (1000) cho an toàn? → Cần kiểm tra usage thực tế của Ops.

---

## 8. Tài liệu liên quan

- **Pattern tham chiếu:** [Overview V2 — Logic Import Nhân Viên](../registration-grouping/overview-v2-import-logic.md) — workflow upload/preview/apply, action types, 2 lớp xác nhận
- **File CSV mẫu:** [`content-list.csv`](./content-list.csv) — sample export từ Data Export type Content
- **Chức năng Data Export:** (link nếu có doc)
- **Tech Spec:** `tech-spec.md` (sẽ tạo sau khi overview được approve)

---

*Có thắc mắc / phản hồi, liên hệ team Gen-Green Ops.*
