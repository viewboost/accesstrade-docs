# Đánh giá từng module — Mô hình Booking

> **Bản nháp để review.** Đi qua từng module trong [đề bài gốc](01-de-bai-goc.md): mô tả · giải nghĩa thuật ngữ · mức độ khớp với hệ thống Ambassador hiện có · các điểm cần làm rõ với business.
>
> Ký hiệu: ✅ Ambassador đã có · 🔶 cần mở rộng · 🆕 build mới · ❓ **cần hỏi business**.

---

## Trước hết — làm rõ các thuật ngữ then chốt

Đề bài dùng nhiều từ dễ hiểu lệch. Thống nhất nghĩa trước khi đánh giá:

| Thuật ngữ | Nghĩa trong tài liệu này |
|-----------|--------------------------|
| **Job** | Một "lời mời tuyển" do admin/brand đăng — có mô tả, ngân sách, **quota (cần N KOC)**. Nhiều KOC apply vào cùng 1 job. *(1 job → nhiều KOC, theo đề bài)* |
| **Brief** | Tài liệu **hướng dẫn nội dung** cho KOC: làm gì, hashtag, yêu cầu, deadline. **KHÁC hợp đồng** (brief không có giá trị pháp lý). |
| **Contract (HĐ)** | Hợp đồng **pháp lý** ký số (OTP/eSign), có giá trị ràng buộc — điều kiện để thanh toán. |
| **Tier** | Hạng creator theo lượng follower (Nano/Micro/Macro/Mega). |
| **KOC / Creator** | Người làm nội dung tham gia job. |
| **ADV / Brand** | Nhãn hàng đặt job. |

---

## ① Danh sách Jobs

**Mô tả (đề bài):** Brand/Admin tạo job với brief, ngân sách, quota. KOC thấy feed job được lọc theo tier và platform của họ.

**3 phần:**
1. **Tạo Job** — tên, mô tả, yêu cầu, ngân sách, timeline, quota KOC
2. **Điều kiện tham gia** — tier / follower min, platform, ngành/niche
3. **Hiển thị cho KOC** — feed phù hợp profile, filter platform/tier, deadline đăng ký

**Đánh giá khớp Ambassador:**
- 🔶 Ambassador đã có "campaign/event" với ngân sách + điều kiện tham gia → mở rộng thành job.
- 🆕 **Quota KOC** (giới hạn số người/job) — chưa có, cần bổ sung.
- 🆕 **Feed job lọc theo profile** — hiện creator chưa có màn "tự khám phá job", cần build.

**❓ Hỏi business:**
- "Quota KOC" — đủ số người thì **tự đóng job** hay admin đóng tay?
- "Deadline đăng ký" có khác "deadline nộp bài" không (2 mốc riêng)?
- Lọc theo ngành/niche — 1 KOC nhiều ngành thì khớp thế nào (trùng 1 ngành là đủ)?

---

## ② Tham gia Job

**Mô tả (đề bài):** KOC apply → Admin duyệt → hệ thống tự gửi brief + hướng dẫn.

**3 phần:**
1. **KOC apply** — chọn job → apply, xem brief trước, status Pending
2. **Admin duyệt** — review profile KOC, approve/reject, notify KOC
3. **Gửi Brief + HD** — file brief tự động gửi, hướng dẫn nộp bài, deadline content

**Đánh giá khớp Ambassador:**
- 🆕 **Luồng apply → duyệt** — hiện Ambassador cho creator tham gia campaign **tự động**, chưa có bước "apply rồi admin duyệt". Đây là phần lõi cần bổ sung.
- ✅ **Notify KOC** — hệ thống thông báo đã có.
- 🆕 **Brief** — chưa có khái niệm brief riêng (xem giải nghĩa ở trên). Cần làm.

**❓ Hỏi business:**
- "Brief" là **tài liệu riêng** (admin soạn/gửi) đúng không — KHÁC hợp đồng?
- Brief gửi tự động khi nào: ngay khi duyệt, hay admin bấm gửi?
- "Xem brief trước" (khi apply) — KOC xem được brief đầy đủ trước khi apply, hay chỉ mô tả tóm tắt?

---

## ③ Nộp bài Content  ·  *(đề bài ghi: module phức tạp nhất)*

**Mô tả (đề bài):** KOC submit link + proof → Admin review (tối đa 2 lần revise) → track performance.

**3 phần:**
1. **KOC submit** — link post/video, thời gian đăng, screenshot proof
2. **Review bài** — admin check content, pass / yêu cầu sửa, **max 2 lần revise**
3. **Track performance** — view/like/comment, đơn/GMV (nếu affiliate), auto-update KPI

**Đánh giá khớp Ambassador:**
- ✅ **Submit link + review** — luồng nộp bài + duyệt đã có.
- 🔶 **Max 2 lần revise** — hiện chỉ có duyệt/từ chối, chưa có vòng "yêu cầu sửa" giới hạn 2 lần. Cần bổ sung.
- ✅ **Track view/like/comment** — đã có.
- ❓ **Track "đơn/GMV"** — đây là phần cần làm rõ kỹ (xem dưới).

**❓ Hỏi business:**
- **"Screenshot proof"** — KOC có **bắt buộc** upload ảnh chứng minh không, hay chỉ cần link?
- **"Đơn / GMV (nếu affiliate)"** — số liệu đơn hàng/doanh thu này lấy từ đâu? (gắn link affiliate có theo dõi? nhập tay? hay chưa cần ở giai đoạn đầu?) — đây là điểm mơ hồ nhất.
- "Max 2 lần revise" — quá 2 lần mà chưa đạt thì xử lý sao (từ chối hẳn? vẫn trả tiền một phần?)?

---

## ④ Ký HĐ điện tử

**Mô tả (đề bài):** Template HĐ tự động điền theo job, KOC ký OTP/eSign, lưu PDF có timestamp.

**3 phần:**
1. **Tạo HĐ tự động** — template theo job type, fill tên/số tiền, điều khoản chuẩn
2. **KOC ký số** — OTP/eSign, xác nhận điều khoản, lưu PDF timestamp
3. **Lưu trữ + pháp lý** — HĐ 2 bên đã ký, gắn với job ID, download anytime

**Đánh giá khớp Ambassador:**
- ✅ **Engine ký số (OTP/eSign/PDF)** — Ambassador đã có sẵn cơ chế ký điện tử (đang dùng cho hợp đồng creator). Tái dùng được — **không phải tích hợp eSign provider từ đầu**.
- 🆕 **HĐ theo job** — hiện HĐ là loại cố định (KYC creator), chưa có HĐ riêng từng job với giá/tên job. Cần mở rộng.

**❓ Hỏi business:**
- HĐ ký **2 bên** (KOC ↔ nền tảng) hay **3 bên** (brand ↔ KOC ↔ nền tảng)?
- "Số tiền" trên HĐ lấy từ đâu — admin nhập khi duyệt, hay theo bảng giá?
- Mọi job đều **bắt buộc** ký HĐ, hay chỉ job giá trị lớn?
- Ai cung cấp **nội dung điều khoản** HĐ chuẩn?

---

## ⑤ Theo dõi Thanh toán  ·  *(gắn chặt module ④: HĐ là điều kiện TT)*

**Mô tả (đề bài):** Sau khi bài approved → Finance xác nhận → upload proof → KOC nhận thông báo + xác nhận.

**3 phần:**
1. **Xét duyệt TT** — sau bài approved, Finance xác nhận, status Pending pay
2. **Thực hiện TT** — chuyển khoản/ví, upload bill proof, status Paid
3. **KOC xem & xác nhận** — lịch sử TT, thông báo real-time, xác nhận nhận tiền

**Đánh giá khớp Ambassador:**
- ✅ **Chuyển khoản + lịch sử thanh toán** — Ambassador đã có luồng thanh toán (rút tiền/đối soát). Tái dùng được.
- ✅ **Phân quyền duyệt thanh toán** — đi theo cơ chế phân quyền sẵn có của Ambassador (không thêm role mới).
- 🔶 **Gate "HĐ signed = điều kiện TT"** — hiện thanh toán chưa check trạng thái HĐ. Cần thêm điều kiện.
- 🆕 **Upload bill proof** + **KOC xác nhận nhận tiền** (2 chiều) — chưa có.

**❓ Hỏi business:**
- "Xác nhận nhận tiền" của KOC — có **bắt buộc** không (2 chiều), hay chỉ thông báo 1 chiều?
- Thanh toán theo **từng bài** hay **gom theo đợt** (cuối tháng/cuối chiến dịch)?

---

## Tổng hợp — các điểm cần hỏi business (ưu tiên)

| # | Câu hỏi | Ảnh hưởng |
|---|---------|-----------|
| 1 | "Đơn/GMV" (module ③) lấy số liệu từ đâu? cần ở giai đoạn đầu không? | 🔴 module phức tạp nhất |
| 2 | HĐ 2 bên hay 3 bên? số tiền từ đâu? job nào bắt buộc? | 🔴 module ④⑤ |
| 3 | "Brief" là tài liệu riêng (≠ HĐ)? | 🟡 module ②④ |
| 4 | Thanh toán theo bài hay theo đợt? | 🟡 module ⑤ |
| 5 | Screenshot proof bắt buộc? quota tự đóng? deadline 2 mốc? | 🟢 chi tiết |

---

*Bản nháp đánh giá module — chờ review + trả lời các câu hỏi business. Đánh giá "khớp Ambassador" ở mức cao, chưa đi vào chi tiết kỹ thuật.*
