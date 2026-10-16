# TÓM TẮT VIỆC ACCESSTRADE CẦN PHỐI HỢP — MSHT × TPBANK CHI HỘ THEO LÔ (PHASE 2)

> **Bản nháp chờ a Vĩnh review trước khi gửi AccessTrade.** Nguồn: [ke-hoach-timeline.md](ke-hoach-timeline.md) v1.2. Mục "Câu hỏi cần a Vĩnh chốt" ở cuối file là ghi chú nội bộ, xoá đi trước khi gửi.

**Gửi:**
- **AT-Core:** Dev AT-Core (AT Core / HSM)
- **AT-MSHT:** Quỳnh (Nghiệp vụ) · Hằng (Kế toán)

**Lịch:** nghiệm thu E2E **T3 21/10**, release và bật chi tự động **T4 22/10**.

**Cách chi mới:** MSHT gom lệnh và gọi AT Core **1 lần mỗi lô** vào 5 khung giờ 0h00 · 8h00 · 12h00 · 16h00 · 20h00. Mỗi lô tối đa 30 lệnh, mỗi ngày tối đa 100 lệnh, theo ngưỡng chi hộ cập nhật ngày 10/09.

**Đầu mối phía MSHT:** Huyền (PM / QC) · Trung (Dev Lead / DevOps) · Ngọc Thảo (Biz, kênh escalate)

---

## 1. Trước 21/10 — AT-Core

| Ngày | Việc | Kết quả mong muốn |
|---|---|---|
| T2 19/10 | Chốt người trực nghiệm thu ngày 21/10 | Lịch trực cụ thể |
| T2 19/10 (chiều) | AT Core DEV sẵn sàng để MSHT test tích hợp chi theo lô | MSHT gọi thử được lô trên DEV |
| T3 20/10 | Xác nhận AT Core Production sẵn sàng nhận lô từ MSHT: cert HSM còn hạn, dịch vụ chi hộ TPBank vẫn mở cho partner `TPBANK_MSHT` | Xác nhận qua email / Slack |

## 2. T3 21/10 — Nghiệm thu E2E trên DEV

| Bên | Người | Việc | Kết quả mong muốn |
|---|---|---|---|
| AT-Core | Dev AT-Core | Trực cùng Huyền: xác nhận tiền về đúng TK test; xác nhận case chi thất bại (sai TK) được xử lý đúng | Ảnh / sao kê làm bằng chứng |
| AT-Core | Dev AT-Core | Đối chiếu log AT Core với log lô MSHT cùng Trung | Khớp số lệnh, tổng tiền, trạng thái |
| AT-MSHT | Quỳnh | Xác nhận nghiệm thu nghiệp vụ | Email xác nhận **trước 17:00** |
| AT-MSHT | Hằng | Chi kỳ thủ công **cuối cùng** theo file MSHT xuất như thường lệ | Gửi kết quả **trong ngày 21/10**, để MSHT import trước Go/No-Go sáng 22/10 (tránh chi trùng) |

## 3. T4 22/10 — Release

| Bên | Người | Việc |
|---|---|---|
| AT-Core | Dev AT-Core | Trực 2 lô production đầu tiên, đối chiếu realtime với Trung |
| AT-Core | Dev AT-Core | Xác nhận tiền đã về tài khoản user ở lô đầu tiên |
| AT-MSHT | Hằng | Dừng chi thủ công **sau khi Ngọc Thảo xác nhận**. Trước đó vẫn giữ quy trình cũ |

## 4. Sau release (23/10 → 30/10)

- **Đối soát hằng ngày:** Dev AT-Core (AT-Core) và Hằng (AT-MSHT) đối soát log lô với Trung mỗi sáng, kể cả các lô cuối tuần.
- **Rollback:** nếu MSHT báo lô lỗi và phải tắt chi tự động, Hằng (AT-MSHT) chi thủ công lại theo kỳ T2/T4 cho tới khi fix xong.

## 5. Cam kết thường trực — AT-Core

- **Đầu mối TPBank:** AT-Core làm đầu mối với TPBank cho mọi vấn đề phía ngân hàng.
- **Báo trước khi thay đổi:** AT-Core báo trước cho MSHT khi đổi key, cert HSM hoặc hạn mức. Sự cố tắt self key lần trước xảy ra chính vì thiếu bước này.

## 6. Cần AT-Core trả lời trước 19/10

1. TK test cấp ngày 10/09 còn dùng được cho nghiệm thu 21/10 không?
2. Cert HSM hiện tại hết hạn ngày nào?

---

## Câu hỏi cần a Vĩnh chốt (nội bộ — xoá trước khi gửi)

1. **Quy tắc xử lý lệnh thất bại:** kế hoạch ghi là "theo quy tắc đã thống nhất với AT" (hoàn số dư hay để chờ xử lý?), nhưng chưa có văn bản nào ghi cụ thể. Nếu chưa thật sự chốt thì thêm câu này vào mục 6 để AccessTrade trả lời.
2. **Số lần truy vấn trạng thái mỗi lô:** AC-03 ghi "số lần truy vấn đã chốt", nhưng chưa thấy con số cụ thể. Con số này quyết định phí HSM. Nếu chưa chốt thì thêm vào mục 6.
3. **AT-Core DEV sẵn sàng từ chiều 19/10:** mốc này suy ra từ phương án của rủi ro R1, kế hoạch không ghi thẳng. Anh xác nhận có yêu cầu AT-Core mốc này không.
4. **Hạn Hằng gửi kết quả kỳ thủ công cuối:** kế hoạch chỉ ghi "trước Go/No-Go 22/10". Bản này đang chốt là "trong ngày 21/10". Anh xem có cần giờ cụ thể không.
5. **Quỳnh (Nghiệp vụ) và Hằng (Kế toán) thuộc AT-MSHT:** bản này đang xếp như vậy, anh xác nhận giúp có đúng không.
