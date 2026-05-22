# Pitch Deck — Tách Brand Portal cho vCreator (VinGroup)

**Vai:** Product Owner → pitch Business team
**Khách minh họa:** VinGroup (vCreator)
**Mục tiêu deck:** Business gật chi ngân sách tách brand portal — bằng **ROI kép**: tiết kiệm chi phí vận hành **+** mở dòng upsell.
**Cập nhật:** 2026-05-22

> **Định cỡ deck (theo dữ kiện thật):** tải ops làm-hộ ở mức *trung bình (vài lần/tuần)* → tiết kiệm giờ ops là **thật nhưng không đủ một mình để thắng**. Vì vậy deck đặt **upsell ngang sức tiết kiệm** — hai vế bổ trợ, không vế nào là phụ.

---

## Slide 1 — Hook
- Một câu: *"VinGroup đang đăng nhập vào công cụ vận hành nội bộ của ta để xem báo cáo. Đó là rủi ro ta đang gánh — và doanh thu ta đang bỏ lỡ."*
- Đặt thẳng 2 đòn bẩy: **giảm rủi ro + chi phí vận hành** và **mở SKU upsell mới**.

## Slide 2 — Hiện trạng (không kỹ thuật)
- vCreator: brand (VinGroup) xem mọi thứ **trong admin operations**, chung chỗ đội vận hành.
- Hệ quả: brand thấy menu vận hành lạ; ops phải dè chừng từng thao tác; brand cần số liệu → ops làm hộ.
- Bằng chứng trong nhà: **TCB đã tách `dashboard/` riêng và chạy thật** → "ta đã làm được, không phải thử nghiệm".

## Slide 3 — 3 nỗi đau quy ra tiền
- **Đau 1 — Ops làm-hộ:** vài lần/tuần brand yêu cầu báo cáo/tra cứu = giờ công ops lặp lại. Quy ra tiền/năm.
- **Đau 2 — Rủi ro thao tác sai:** brand ở trong admin = một click nhầm vào duyệt-hủy đối soát / budget = lệch tiền + mất niềm tin. Chi phí một sự cố đối soát sai >> chi phí tách.
- **Đau 3 — Trần upsell:** không portal riêng = không có "sản phẩm" để bán thêm cho khách enterprise.

## Slide 4 — ROI vế 1: Tiết kiệm chi phí vận hành
Khung tính (điền số thật vCreator vào `[...]`):

| Biến | Giá trị | Ghi chú |
|---|---|---|
| Số yêu cầu brand/tuần | `[~ vài lần]` | báo cáo, tra cứu, export hộ |
| Giờ ops mỗi yêu cầu | `[Y giờ]` | gồm cả ngắt mạch công việc |
| Giờ ops/tháng phục vụ brand | `[N giờ]` | = yêu cầu/tháng × Y |
| % giảm sau self-service | ~70–80% | brand tự tra, ops chỉ xử lý ngoại lệ |
| Chi phí giờ ops | `[Z đ/giờ]` | |
| **Tiết kiệm/năm** | `[N × 80% × Z × 12]` | con số chủ đạo vế 1 |

- **Cộng thêm (rủi ro tránh được):** xác suất sự cố đối soát sai × chi phí mỗi sự cố → giá trị bảo hiểm.
- **Lưu ý trung thực:** tải trung bình → tiết kiệm giờ ở mức *khá*, không khổng lồ. Đây là lý do vế 2 (upsell) phải mạnh tương đương.

## Slide 5 — ROI vế 2: Upsell / doanh thu mới
- Portal riêng = **SKU bán được**, biến cost-center thành revenue-line:
  - **Brand Portal tier** — gói self-service analytics/báo cáo tính phí riêng.
  - **Tài chính minh bạch** — budget / đối soát / payment timeline: giá trị enterprise rõ.
  - **Branding theo khách** — logo/màu/tên riêng; bán theo từng tenant.
- Đòn đàm phán: *"Đây là thứ ta đặt lên bàn khi gia hạn/nâng cấp hợp đồng VinGroup."*
- Khung định giá (điền): giá gói/tháng `[...]` × số tenant tiềm năng → doanh thu năm.

## Slide 6 — Đòn bẩy chi phí: KHÔNG build từ đầu
- **TCB `dashboard/` đã có** → port sang vCreator, không dựng mới → chi phí build thấp hơn nhiều.
- Chi phí một lần, **tái dùng cho khách thứ 3 (Ambassador, 13 brand)** → ROI nhân lên qua nhiều khách, không chỉ vCreator.
- Đây là điểm hạ payback period mạnh nhất.

## Slide 7 — Payback & ROI tổng
- **Payback = chi phí build ÷ (tiết kiệm/tháng + doanh thu upsell/tháng).**
- Vì build là port (rẻ) + ROI hai vế cộng dồn → payback ngắn. Đây là con số business muốn thấy nhất — đặt to, rõ.
- Trình 3 kịch bản: chỉ-tiết-kiệm / chỉ-upsell / cả-hai → cho thấy kể cả kịch bản dè dặt vẫn hoàn vốn.

## Slide 8 — Giảm rủi ro (cứng hóa)
- Cô lập ở **tầng code**, không chỉ phân quyền: thao tác nguy hiểm *không tồn tại* trong app brand → không thể click nhầm.
- Audit rõ: tách bạch brand vs ops đã làm gì.
- Lập luận: rủi ro lệch tiền/lộ thao tác *khó định giá nhưng đắt khi xảy ra* → tách là mua bảo hiểm rẻ.

## Slide 9 — So sánh phương án (đã cân nhắc kỹ)
- A (tách riêng — như TCB) vs B (giữ chung admin — như vCreator hiện tại).
- Lập luận: B chỉ rẻ khi brand mãi read-only; **một khi mở quyền, RBAC không đủ an toàn** → A đúng dài hạn.
- Thừa nhận hại của A (trùng lặp code) + lời giải: **brand-portal core dùng chung 3 dự án**.

## Slide 10 — Lộ trình & chi phí theo pha
| Pha | Nội dung | Giá trị thu | Dừng được ở đây? |
|---|---|---|---|
| P0 | Nền multi-tenant + RBAC + cô lập | An toàn để vận hành | — |
| P1 | Read-only core: analytics + tài chính viewer | ROI tiết kiệm + SKU cơ bản | ✅ Đã có ROI |
| P2 | Import (nếu cần) | Năng lực đầu vào | ✅ |
- Mỗi pha gắn thời gian + chi phí + giá trị → business thấy *dừng sau P1 vẫn lời*.

## Slide 11 — Rủi ro nếu KHÔNG làm (urgency)
- Ops tiếp tục đốt giờ làm-hộ; không scale khi thêm khách.
- Sự cố brand thao tác nhầm trong admin có thể xảy ra bất cứ lúc nào.
- Đối thủ chào enterprise bằng portal self-service — ta không có gì đối lại.

## Slide 12 — Ask
- Xin: ngân sách + người cho **P0 + P1**, mốc thời gian cụ thể.
- Cam kết: con số payback + **SKU upsell sẵn sàng đưa vào hợp đồng VinGroup kế tiếp**.

---

## Phụ lục — 2 insight làm deck thắng
1. **ROI kép là đòn quyết định.** Tải ops chỉ trung bình → một mình tiết kiệm chỉ khiến business "gật cho có". Tiết kiệm + upsell + tái dùng 3 khách → business *muốn* làm.
2. **Bằng chứng sống có sẵn trong nhà.** TCB = mô hình A đang chạy; vCreator = mô hình B đang chạy. Pitch không phải "thử nghiệm" mà là "nhân rộng cái đã chứng minh" → hạ rủi ro trong mắt business.

## Số cần điền trước khi trình
- Số yêu cầu brand/tuần, giờ ops mỗi yêu cầu, chi phí giờ ops (Slide 4).
- Giá gói brand portal/tháng + số tenant tiềm năng (Slide 5).
- Ước tính chi phí build (port từ TCB) (Slide 6–7).
