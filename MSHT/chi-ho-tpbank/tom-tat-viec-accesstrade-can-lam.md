# TÓM TẮT VIỆC ACCESSTRADE CẦN PHỐI HỢP — MSHT × TPBANK CHI HỘ THEO LÔ (PHASE 2)

> **Bản nháp chờ a Vĩnh review trước khi gửi AccessTrade.** Nguồn: [ke-hoach-timeline.md](ke-hoach-timeline.md) v1.4. Mục "Câu hỏi cần a Vĩnh chốt" ở cuối file là ghi chú nội bộ, xoá đi trước khi gửi.

**Gửi:**
- **AT-Core:** Dev AT-Core (AT Core / HSM)
- **AT-MSHT:** Quỳnh (Nghiệp vụ)

**Lịch:** D = ngày release dự kiến **T5 22/10/2026**. Các mốc D-n tính theo ngày làm việc: D-3 = T2 19/10 · D-2 = T3 20/10 · D-1 = T4 21/10.
- Nghiệm thu E2E: **D-1**
- Release, chi theo lô có hiệu lực ngay sau deploy: **D**

**Cách chi mới:** MSHT gom lệnh và gọi AT Core **1 lần mỗi lô** vào 5 khung giờ 0h00 · 8h00 · 12h00 · 16h00 · 20h00. Mỗi lô tối đa 30 lệnh và 10.000.000đ, mỗi ngày tối đa 100 lệnh, theo ngưỡng chi hộ cập nhật ngày 10/09.

**Đầu mối phía MSHT:** Huyền (PM / QC) · Trung (Dev Lead / DevOps) · Ngọc Thảo (Biz, kênh escalate)

---

## 1. Trước D-1 — AT-Core

| Mốc | Việc | Kết quả mong muốn |
|---|---|---|
| D-3 | Chốt người trực nghiệm thu ngày D-1 | Lịch trực cụ thể |
| D-3 (chiều) | AT Core DEV sẵn sàng để MSHT test tích hợp chi theo lô | MSHT gọi thử được lô trên DEV |
| D-2 | Xác nhận AT Core Production sẵn sàng nhận lô từ MSHT: cert HSM còn hạn, dịch vụ chi hộ TPBank vẫn mở cho partner `TPBANK_MSHT` | Xác nhận qua email / Slack |

## 2. D-1 — Nghiệm thu E2E trên DEV và chuẩn bị cutover

| Bên | Người | Việc | Kết quả mong muốn |
|---|---|---|---|
| AT-Core | Dev AT-Core | Trực cùng Huyền: xác nhận tiền về đúng TK test; xác nhận case chi thất bại (sai TK) được xử lý đúng | Ảnh / sao kê làm bằng chứng |
| AT-Core | Dev AT-Core | Đối chiếu log AT Core với log lô MSHT cùng Trung | Khớp số lệnh, tổng tiền, trạng thái |
| AT-MSHT | Quỳnh | Xác nhận nghiệm thu nghiệp vụ | Email xác nhận **trước 17:00** |
| AT-MSHT | — | Chi kỳ thủ công **cuối cùng** theo file MSHT xuất như thường lệ | Gửi kết quả **trong ngày D-1**, để MSHT import trước Go/No-Go ngày D (tránh chi trùng) |
| AT-MSHT | Quỳnh | **Xác nhận việc huỷ các lệnh rút chưa chi trước golive** (Ngọc Thảo gửi thông báo) | Email xác nhận đồng ý huỷ; AT không chi thủ công thêm các lệnh này |

## 3. D — Release

| Bên | Người | Việc |
|---|---|---|
| AT-MSHT | Quỳnh | Nhận danh sách lệnh MSHT đã huỷ (Ngọc Thảo gửi trước khi deploy) |
| AT-Core | Dev AT-Core | Trực 2 lô production đầu tiên, đối chiếu realtime với Trung |
| AT-Core | Dev AT-Core | Xác nhận tiền đã về tài khoản user ở lô đầu tiên |
| AT-MSHT | — | Dừng chi thủ công **sau khi Ngọc Thảo xác nhận**. Trước đó vẫn giữ quy trình cũ |

## 4. Sau release (D+1 → D+6)

- **Đối soát hằng ngày:** Dev AT-Core (AT-Core) đối soát log lô với Trung mỗi sáng, kể cả các lô cuối tuần.
- **Rollback:** nếu MSHT báo lô lỗi và phải rollback về luồng cũ, AT-MSHT chi thủ công lại theo kỳ T2/T4 cho tới khi fix xong.

## 5. Cam kết thường trực — AT-Core

- **Đầu mối TPBank:** AT-Core làm đầu mối với TPBank cho mọi vấn đề phía ngân hàng.
- **Báo trước khi thay đổi:** AT-Core báo trước cho MSHT khi đổi key, cert HSM hoặc hạn mức. Sự cố tắt self key lần trước xảy ra chính vì thiếu bước này.

## 6. Cần AT trả lời trước D-3

1. TK test cấp ngày 10/09 còn dùng được cho nghiệm thu D-1 không?
2. Cert HSM hiện tại hết hạn ngày nào?
3. AT-MSHT đồng ý huỷ các lệnh rút chưa chi tính đến thời điểm golive không? Có cần MSHT thông báo cho user trước không?

---

## Câu hỏi cần a Vĩnh chốt (nội bộ — xoá trước khi gửi)

1. **Quy tắc xử lý lệnh thất bại:** kế hoạch ghi là "theo quy tắc đã thống nhất với AT" (hoàn số dư hay để chờ xử lý?), nhưng chưa có văn bản nào ghi cụ thể. Nếu chưa thật sự chốt thì thêm câu này vào mục 6 để AccessTrade trả lời.
2. **Số lần truy vấn trạng thái mỗi lô:** AC-03 ghi "số lần truy vấn đã chốt", nhưng chưa thấy con số cụ thể. Con số này quyết định phí HSM. Nếu chưa chốt thì thêm vào mục 6.
3. **AT-Core DEV sẵn sàng từ chiều D-3:** mốc này suy ra từ phương án của rủi ro R1, kế hoạch không ghi thẳng. Anh xác nhận có yêu cầu AT-Core mốc này không.
4. **Người chi kỳ thủ công cuối bên AT-MSHT:** đã bỏ vai trò Kế toán (Hằng) khỏi kế hoạch, các dòng chi thủ công đang để trống người. Anh xác nhận ai phụ trách, hay chỉ ghi chung là AT-MSHT.
5. **Lệnh bị huỷ trước golive:** user có được hoàn số dư để tạo lại yêu cầu rút không, và ai thông báo cho user?
