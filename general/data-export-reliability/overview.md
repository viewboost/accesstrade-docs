# Khắc phục lỗi tải file dữ liệu bị treo và xếp hàng vĩnh viễn

> Hệ thống xuất file (data-export) của vCreator hiện có thể bị "kẹt" vĩnh viễn khi gặp sự cố: file đang tải dở bị treo mãi, các lượt tải sau xếp hàng mà không bao giờ tới lượt, và sau khi nâng cấp hệ thống thì hàng tồn được giải phóng rất chậm. Tài liệu này mô tả nguyên nhân và cách khắc phục.

**Ngày:** 27/05/2026
**Trạng thái:** Đề xuất
**Đối tượng đọc:** Business, Ops, PM
**Phạm vi:** Chức năng "Xuất dữ liệu / Tải file" trong trang admin vCreator (báo cáo nội dung, đối soát, rút tiền, biểu đồ thống kê...)

---

## 1. Hiện tượng người dùng đang gặp

Trong trang admin, khi nhân viên cần lấy dữ liệu ra file (Excel/CSV) — ví dụ xuất danh sách nội dung, bảng đối soát, lịch sử rút tiền — họ bấm "Xuất dữ liệu", hệ thống nhận yêu cầu và xử lý ở chế độ nền. Yêu cầu lần lượt đi qua các trạng thái: **chờ → đang chạy → hoàn thành** (hoặc **thất bại**).

Có ba tình huống khiến chức năng này hỏng:

1. **File tải dở bị treo mãi mãi.** Nếu server gặp sự cố ngay lúc đang tạo file (server bị khởi động lại, hết bộ nhớ, hoặc deploy phiên bản mới giữa chừng), yêu cầu đó kẹt vĩnh viễn ở trạng thái "đang chạy". Người dùng nhìn thấy nó quay mãi không bao giờ xong, cũng không báo lỗi.

2. **Tất cả lượt tải sau bị xếp hàng vô thời hạn.** Hệ thống chỉ cho phép tối đa 2 file chạy cùng lúc để tránh quá tải. Nếu cả 2 "ô" này bị chiếm bởi các yêu cầu treo (ở tình huống 1), thì **mọi yêu cầu mới đều mắc kẹt ở trạng thái "chờ" mãi mãi** — không bao giờ tới lượt, vì hệ thống tưởng vẫn còn 2 file đang chạy.

3. **Sau khi nâng cấp hệ thống, hàng tồn được giải phóng quá chậm.** Khi đội kỹ thuật nâng cấp (ví dụ chuyển đổi cơ sở dữ liệu), các yêu cầu treo buộc phải được đánh dấu "thất bại" thủ công. Nhưng tác vụ định kỳ chạy mỗi giờ chỉ "đẩy" được **đúng một** yêu cầu mỗi lần — nên nếu có hàng chục yêu cầu đang chờ, chúng được xử lý nhỏ giọt mỗi giờ một cái, dù máy chủ hoàn toàn rảnh.

→ Hệ quả thực tế: nhân viên báo "không tải được file", "file quay mãi không xong", hoặc "đã chờ cả buổi vẫn chưa thấy". Đội vận hành phải vào tận cơ sở dữ liệu sửa tay mỗi lần.

---

## 2. Nguyên nhân

### Cơ chế hiện tại

Mỗi yêu cầu xuất file là một bản ghi trong cơ sở dữ liệu, mang một trong các trạng thái: chờ, đang chạy, hoàn thành, thất bại. Một "bộ điều phối" quyết định khi nào đẩy yêu cầu từ "chờ" sang "đang chạy", với hai quy tắc:

1. **Tối đa 2 file chạy đồng thời** — để không làm nghẽn máy chủ.
2. **Một tác vụ định kỳ chạy mỗi giờ** kiểm tra xem có yêu cầu nào đang chờ và còn chỗ trống không, nếu có thì đẩy đi.

### Vấn đề: hệ thống không phân biệt được "đang chạy thật" với "đã chết"

Khi một yêu cầu chuyển sang "đang chạy", việc đánh dấu nó "hoàn thành" hay "thất bại" chỉ xảy ra **nếu tiến trình xử lý còn sống tới lúc kết thúc**. Nếu server chết giữa chừng, bước đánh dấu cuối không bao giờ chạy — và **không có ai khác đứng ra dọn dẹp**. Bản ghi nằm ì ở "đang chạy" mãi mãi.

### Vì sao hệ thống không tự xử lý?

- ❌ Không có cơ chế "đếm giờ" — không phát hiện được một file đã "chạy" quá lâu bất thường.
- ❌ Không có tín hiệu "còn sống" định kỳ — không phân biệt được file đang chạy thật (chỉ là lâu) với file đã chết.
- ❌ Không có bước dọn dẹp lúc khởi động lại — sau khi server hồi phục, nó không rà soát các file kẹt từ lần chết trước.

### Tại sao càng để lâu càng tệ?

Hai "ô chạy" là tài nguyên hữu hạn. Mỗi lần một file chết mà không được dọn, nó chiếm vĩnh viễn một ô. Chỉ cần **hai sự cố** là cả hai ô bị khóa cứng — toàn bộ chức năng xuất file ngừng hoạt động cho tới khi có người sửa tay. Đây là lỗi tích lũy: hệ thống chạy càng lâu, xác suất kẹt cứng càng cao.

---

## 3. Giải pháp đề xuất

### Tóm tắt giải pháp

**Trang bị cho mỗi file đang chạy một "nhịp tim" — nếu nhịp tim ngừng đập, hệ thống tự hiểu file đó đã chết và giải phóng ô, thay vì chờ vô hạn.** Đồng thời cho bộ điều phối xử lý nhiều yêu cầu mỗi lượt và chạy thường xuyên hơn.

### Cách hoạt động

1. **Nhịp tim (heartbeat).** Trong suốt thời gian một file đang được tạo, hệ thống "đập" một tín hiệu sống mỗi phút. File chạy thật — dù lâu — vẫn đập đều. File mà tiến trình đã chết sẽ ngừng đập.

2. **Tự động dọn file chết.** Trước mỗi lần điều phối, hệ thống rà soát: file nào đang ở "đang chạy" nhưng đã **ngừng đập quá 3 phút** thì bị đánh dấu "thất bại" kèm lý do "tiến trình đã dừng (tự phục hồi)". Ô chạy được trả lại ngay.

3. **Xử lý nhiều yêu cầu mỗi lượt.** Bộ điều phối lặp cho đến khi hết chỗ trống hoặc hết hàng chờ — thay vì chỉ đẩy đúng một yêu cầu rồi dừng. Sau sự cố hoặc nâng cấp, hàng tồn được xả nhanh thay vì nhỏ giọt.

4. **Chạy thường xuyên hơn.** Tác vụ định kỳ chạy **mỗi 5 phút** thay vì mỗi giờ, để file chết được phát hiện và hàng chờ được giải phóng kịp thời.

### Phạm vi áp dụng

**Chỉ áp dụng cho:** chức năng xuất file dữ liệu (data-export) trong admin vCreator — tất cả các loại xuất hiện có (nội dung, đối soát, rút tiền, chuyển tiền, các loại biểu đồ thống kê, user-partner).

**Không áp dụng cho:** các luồng tải/upload khác (upload ảnh, hợp đồng, import dữ liệu) — đây là cơ chế riêng, không thuộc phạm vi này.

### Trường hợp đặc biệt: file bị dọn nhầm

Rất hiếm khi, một file đang chạy thật nhưng tín hiệu sống bị gián đoạn (ví dụ trục trặc mạng tới cơ sở dữ liệu) lâu hơn 3 phút có thể bị đánh "thất bại" oan. Khi đó người dùng chỉ cần bấm xuất lại. Đây là đánh đổi chấp nhận được: thà thỉnh thoảng phải xuất lại còn hơn kẹt cứng vĩnh viễn. Ngưỡng 3 phút (so với nhịp đập 1 phút) đủ rộng để tình huống này gần như không xảy ra trong thực tế.

---

## 4. Lợi ích kỳ vọng

### Cho người dùng
- ✅ File treo sẽ tự chuyển sang "thất bại" trong vài phút, biết để xuất lại — thay vì chờ vô vọng.
- ✅ Yêu cầu mới không còn bị kẹt "chờ" vĩnh viễn sau sự cố.
- ✅ Sau nâng cấp hệ thống, file xuất hoạt động lại bình thường nhanh chóng.

### Cho hệ thống
- ✅ Tự phục hồi sau khi server chết/khởi động lại, không cần can thiệp.
- ✅ Hai "ô chạy" không còn bị khóa cứng vĩnh viễn.
- ✅ Chống được tình huống hai luồng cùng "giành" một yêu cầu (xử lý trùng).

### Cho vận hành
- ✅ Không còn phải vào cơ sở dữ liệu sửa tay mỗi khi có file kẹt.
- ✅ Sau khi chuyển đổi cơ sở dữ liệu, không phải lo "đánh thức" hàng chờ thủ công.

---

## 5. Chi phí và rủi ro

### Chi phí

| Hạng mục | Ước tính |
|----------|----------|
| Công phát triển | ~1 ngày (backend Go) |
| Tải thêm lên cơ sở dữ liệu | Không đáng kể — mỗi file đang chạy ghi 1 cập nhật nhỏ/phút |
| Thay đổi hạ tầng | Không — tận dụng cơ sở dữ liệu hiện có, không cần thêm dịch vụ |

### Rủi ro & cách xử lý

| Rủi ro | Mức độ | Cách xử lý |
|--------|--------|------------|
| File chạy thật bị dọn nhầm do gián đoạn mạng | Thấp | Ngưỡng 3 phút (gấp 3 lần nhịp đập) đủ rộng; người dùng xuất lại nếu hiếm khi gặp |
| File chết sau khi bị dọn lại "hồi sinh" và ghi đè kết quả | Thấp | Bước hoàn tất chỉ cập nhật nếu file vẫn đang ở trạng thái "đang chạy" — đã bị dọn thì bỏ qua |
| Chạy định kỳ 5 phút làm tăng tải | Thấp | Mỗi lượt vẫn tôn trọng giới hạn 2 file đồng thời; xử lý tuần tự trên một máy chủ duy nhất |

---

## 6. Phạm vi không ảnh hưởng

Tài liệu này **không thay đổi**:
- Giao diện trang admin và thao tác bấm "Xuất dữ liệu" của người dùng.
- Định dạng và nội dung file xuất ra (Excel/CSV).
- Cách lấy link tải file (link có thời hạn từ kho lưu trữ).
- Giới hạn tối đa 2 file chạy đồng thời (vẫn giữ nguyên).
- Các loại dữ liệu được phép xuất.

---

## 7. Tài liệu liên quan

- **PRD:** [`prd.md`](./prd.md) — yêu cầu chức năng (FR/NFR) chi tiết, nguồn sinh test case
- **Implementation plan:** [`../../../vcreator/plans/data-export-reliability-fix.md`](../../../vcreator/plans/data-export-reliability-fix.md) — kế hoạch triển khai gốc (chi tiết kỹ thuật: model, heartbeat, atomic claim)
- **Mã nguồn liên quan:** `vcreator/backend/pkg/admin/service/export.go` — bộ điều phối và logic xuất file
