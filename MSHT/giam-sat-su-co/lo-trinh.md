# Hệ giám sát MSHT — lộ trình

> **Trang đầu của bộ tài liệu này.** Đọc file này để nắm toàn cảnh, rồi mở file chi tiết khi cần.
> **Ngày:** 2026-09-14 · **Trạng thái:** chờ chốt **G1** và quyết định nguồn lực.

---

## Project này là gì

Dựng hệ giám sát cho MSHT, để:

> mỗi lỗi khách hàng báo trở thành **dữ liệu** thay vì một tin nhắn · và hệ tự biết mình đang hỏng
> ở đâu **trước khi** khách nói cho biết.

Chi tiết bài toán, sáu nhóm chức năng và các bất biến: [`tai-lieu-du-an.md`](./tai-lieu-du-an.md).

---

## Bộ tài liệu

| File | Dành cho | Nội dung |
| --- | --- | --- |
| **`lo-trinh.md`** *(đang đọc)* | Tất cả | Toàn cảnh, thứ tự làm, cái gì đang chặn |
| [`tai-lieu-du-an.md`](./tai-lieu-du-an.md) | Founder · lãnh đạo | Bối cảnh · 5 khoảng trống · 6 nhóm chức năng M1–M6 · bất biến BB-1…BB-6 · quyết định **G1–G7** · rủi ro |
| [`webview-monitoring.md`](./webview-monitoring.md) | Kỹ thuật | **Cấu phần M4 — đã hiện thực.** Tài liệu nghiệp vụ do đội web-webview soạn và sở hữu |

---

## Ba làn chạy song song

Bốn giai đoạn không phải một đường thẳng. Có ba làn, và **hai làn phải bắt đầu ngay tuần này** vì
có đuôi chờ dài.

```
Làn tổ chức   ├─ chốt G1/G7 · làm việc với CSKH từng ngân hàng ────────┤  lead time dài nhất
Làn dữ liệu   ├─ bật M4 production · tích 14 ngày lập đường cơ sở ─────┤  bắt đầu ngay, có đuôi chờ
Làn xây       │   M1 ──► M2 ──────► M3 / M5 ──────► M6                 │
```

### 🔴 Vì sao bật M4 ngay tuần 1, dù M4 thuộc giai đoạn 3

Nghe như mâu thuẫn với quy tắc *"thứ tự không đảo được"* ở mục 3.6 tài liệu dự án. Không phải.

Quy tắc đó cấm **dựng biểu đồ và cảnh báo** trước khi M1 nói cho biết khách đang kêu gì — vì khi đó
sẽ đo nhầm thứ. Còn **bật thu thập** chỉ là tích dữ liệu, không quyết định điều gì, và nó cần
**14 ngày liên tục** mới ra được đường cơ sở.

⇒ Hoãn hai tuần là mất trắng hai tuần, không đổi lại được gì. Bật sớm, phân tích sau.

---

## Mốc và cổng

| Tuần | Làm gì | Ai |
| --- | --- | --- |
| **T1**<br>15–21/9 | Chốt **G1** (một cái tên sở hữu) và **G7** (một biểu mẫu hay nhiều) · **bật M4 production** · **liệt kê quy tắc chặn từ mã nguồn** · thêm cột tenant vào bảng ghi nhận · rà 3 mục còn lại ở 7.3 | Founder · Kỹ thuật · PM |
| **T2–T3**<br>22/9–5/10 | Triển khai M1 tới CSKH **từng ngân hàng một** · đóng hẳn kênh chat · M4 tích dữ liệu · **ước lượng M2** dựa trên khảo sát T1 · chốt **G2**, **G3** | PM · CSKH · Kỹ thuật |
| **T4**<br>6–12/10 | 🚪 **Cổng 1 — Có chỗ ghi** · M4 đủ 14 ngày → đường cơ sở đầu tiên · bắt đầu nhịp rà soát tuần | |
| **T5–T8**<br>13/10–9/11 | Xây **M2** — mã lý do chặn · màn tra cứu · bảng xếp hạng theo tenant · chốt **G4** | Kỹ thuật · PM |
| **T8** | 🚪 **Cổng 2 — Trả lời được "vì sao"** | |
| **T9–T12**<br>10/11–7/12 | **M3** bấm thử từng tenant · **M5** tín hiệu cho 4 luồng nghiệp vụ còn lại · chốt **G5**, **G6** | Kỹ thuật |
| **T12** | 🚪 **Cổng 3 — Biết trước khách** | |
| **T13–T16**<br>8/12–4/1 | **M6** vòng đời sự cố · ma trận trạng thái · biên bản sau sự cố | Vận hành · Kỹ thuật |
| **T16** | 🚪 **Cổng 4 — Đóng vòng** | |

### Điều kiện qua cổng

| Cổng | Qua được khi |
| --- | --- |
| **1 · Có chỗ ghi** | Mọi lỗi khách báo nằm trong một nơi · tách được theo tenant · **tỉ lệ báo cáo đi qua M1 đo được và ổn định** — không phải "đã dựng xong bảng" |
| **2 · Trả lời được "vì sao"** | Vận hành tự trả lời ca "bị chặn" dưới 30 giây · **số ca trả về "không xác định được lý do" đo được** |
| **3 · Biết trước khách** | Có ít nhất một sự cố diện rộng được máy phát hiện **trước** khi khách đầu tiên gọi |
| **4 · Đóng vòng** | Mọi sự cố đóng đều có kết luận · báo cáo xu hướng chạy đều hai kỳ liên tiếp |

> Điều kiện cổng 1 và 2 đều là **số đo**, không phải "đã bàn giao". Một hệ giám sát nghiệm thu bằng
> "đã dựng xong" là hệ sẽ không ai dùng sau hai tuần.

---

## Đường găng không nằm ở kỹ thuật

Đây là chỗ hầu hết lộ trình giám sát tính sai. Thứ quyết định ngày về đích không phải tốc độ viết mã:

```
G1 (ai sở hữu)  →  M1 tới tay CSKH của N ngân hàng  →  có dữ liệu thật  →  ước lượng đúng phần còn lại
```

**CSKH là nhiều tổ chức ở nhiều công ty khác nhau** *(xem mục 1.5 tài liệu dự án)*. Triển khai M1
không phải một buổi hướng dẫn, mà là **N cuộc làm việc** với N bên có lịch riêng, ưu tiên riêng, và
không bên nào báo cáo cho mình.

⇒ Đây là hạng mục dễ trượt nhất và khó ép nhất trong cả lộ trình. **Bắt đầu liên hệ từ tuần 1, đừng
đợi bảng hoàn thiện.** Chấp nhận triển khai lệch pha giữa các tenant còn hơn chờ đủ.

---

## Tuần đầu — cụ thể

Không việc nào dưới đây cần sửa mã trong sản phẩm, trừ việc 2.

| # | Việc | Ai | Vì sao tuần này |
| --- | --- | --- | --- |
| 1 | Chốt **G1** — một cái tên sở hữu hệ giám sát | Founder | Chặn mọi thứ còn lại |
| 2 | **Bật thu thập M4 trên production** | Kỹ thuật *(đội web-webview)* | Đồng hồ 14 ngày bắt đầu chạy |
| 3 | **Liệt kê quy tắc đang chặn khách rút tiền, đọc từ mã nguồn** | Kỹ thuật | Quyết định toàn bộ khối lượng M2 |
| 4 | Thêm cột **tenant** vào bảng ghi nhận | PM | Đang vi phạm **BB-6** |
| 5 | Liên hệ CSKH ngân hàng đầu tiên, hẹn lịch | PM | Lead time dài nhất |
| 6 | Chốt **G7** — một biểu mẫu chung hay mỗi tenant một bản | PM + CSKH | Quyết định hình dạng M1 |
| 7 | Rà mục 3, 4, 5 ở 7.3 | Kỹ thuật | Ba ẩn số còn lại |

> Việc 2 và việc 3 do **đội khác** làm, không nằm trong quyền điều phối của PM dự án này. Phải đưa
> vào lịch của họ, không phải vào lịch của mình.

---

## Ba ẩn số có thể làm lệch toàn bộ

| Ẩn số | Ảnh hưởng | Gỡ bằng |
| --- | --- | --- |
| **Có bao nhiêu quy tắc chặn rút tiền** | Quyết định T5–T8 là 4 tuần hay 8 tuần. Hiện **không ai biết con số này** | Việc 3 tuần đầu — làm trước tiên |
| **Nguồn lực chưa được phân** | Lộ trình này giả định có người làm. Hiện **chưa ai được giao** | **G1** + quyết định nguồn lực |
| **CSKH mỗi ngân hàng hợp tác tới đâu** | Có thể kéo cổng 1 từ 4 tuần thành 8 | Liên hệ sớm · chấp nhận lệch pha giữa các tenant |

> ⚠️ **Đừng đọc bảng tuần như một cam kết.** Nó là lộ trình **có điều kiện**: đúng nếu G1 chốt trong
> tuần này và có người được giao. **Mỗi tuần G1 chậm là cả lộ trình lùi một tuần** — không phải vì
> thiếu việc để làm, mà vì không có ai quyết được việc nào làm trước.

---

## Đang chặn

| Chặn gì | Cần ai quyết | Hạn |
| --- | --- | --- |
| **G1** — ai sở hữu hệ giám sát *(một cái tên, không phải phòng ban)* | **Founder** | **Tuần này** |
| **G7** — một biểu mẫu chung có cột tenant, hay mỗi tenant một bản | PM + CSKH | Tuần này |
| **G2** — định nghĩa mức độ sự cố, mức nào báo lên ngân hàng nào | Founder | Trước cổng 1 |
| **G3** — dựng công cụ mới hay dùng công cụ CSKH đang có | PM + CSKH | Trước cổng 1 |
| **G4** — có hiển thị lý do bị chặn cho khách không | Founder + pháp chế | Trước cổng 2 |
| **G5** — có trực ngoài giờ không | Founder + vận hành | Trước cổng 3 |
| **G6** — ranh giới trách nhiệm với từng ngân hàng | Founder | Trước cổng 3 |
| **Nguồn lực** — ai làm, bao nhiêu người | **Founder** | **Tuần này** |

### G1 là câu gốc

Mọi dự án giám sát đều thất bại theo cùng một cách: dựng xong, không ai sở hữu, hai tuần sau không
ai mở. Cấu phần M4 đã cho thấy trước hình dạng của rủi ro này — tài liệu của nó ghi rõ hệ có **đúng
một người dùng thật**, kiêm luôn cả vai vận hành, và **không có kế hoạch có đội ops**.

⇒ Với dự án này, câu trả lời cho G1 **không thể là "vẫn người đó"**.

---

## Nếu chỉ được cấp hai tuần

Làm đúng bốn việc:

1. Chốt **G1** — một cái tên
2. **Bật M4 production** — đồng hồ 14 ngày bắt đầu chạy
3. Thêm cột tenant vào bảng ghi nhận, đưa tới CSKH của **một** ngân hàng làm thử
4. **Liệt kê quy tắc chặn từ mã nguồn**

Hết hai tuần sẽ có thứ hôm nay chưa có: **một con số thật về quy mô vấn đề**, và **một ước lượng có
căn cứ** cho phần còn lại. Đó là đủ để quyết định có đầu tư tiếp hay không — mà chính là điều dự án
này tồn tại để phục vụ.

---

## Biết đã xong bằng năm số

| Nhóm | Số | Đích |
| --- | --- | --- |
| Phát hiện | Tỉ lệ sự cố **máy phát hiện trước khách** | tăng dần → **80%** |
| Ghi nhận | % báo cáo của khách được gắn vào một sự cố | **100%** |
| Vận hành | % ca "bị chặn" xử lý xong không cần kỹ sư | → **95%** |
| Chất lượng | Số sự cố lặp lại cùng nguyên nhân | → **0** |
| Quản trị | % sự cố nghiêm trọng có biên bản kết luận | **100%** |

Cả năm số **tách theo tenant**, và **đọc kèm độ phủ**. Một tỉ lệ không kèm mẫu số là một con số không
kiểm chứng được.

> Các đích ở trên đang đặt trên nền chưa biết. **Phải lập đường cơ sở trước** — đó là việc của cổng 1.
> Đặt mức cải thiện trước khi biết điểm xuất phát là bịa.
