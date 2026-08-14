# Nội dung mô tả cho form Cấu hình bảng xếp hạng (admin)

**Dành cho:** Ops/Admin cấu hình bảng xếp hạng trong form sự kiện
**Bám theo:** `prd-leaderboard-period-v2-2026-08-06.md` FR-001 → FR-006
**Ngày:** 14/08/2026

Nguyên tắc viết: Ops không cần biết tên field kỹ thuật. Mỗi mô tả phải trả lời được *"chọn cái này thì người xem thấy gì khác đi"*, và nêu rõ hậu quả nếu chọn sai.

---

## 1. Kỳ xếp hạng

**Tooltip:**
> Khoảng thời gian mà bảng cộng số liệu.
> • **Toàn thời gian** — cộng từ ngày sự kiện bắt đầu, không giới hạn.
> • **Theo tuần** — chỉ tính phát sinh trong tuần, thứ Hai đến Chủ nhật (giờ Việt Nam).
> • **Theo tháng** — chỉ tính phát sinh trong tháng, ngày 1 đến hết ngày cuối tháng.
>
> Đổi kỳ **không** làm thay đổi số tiền creator thực nhận. Chỉ đổi cách bảng hiển thị và xếp hạng.

**Cảnh báo hiện kèm khi chọn Theo tuần / Theo tháng:**
> Sự kiện của partner đang hiển thị số liệu tách theo từng nền tảng (TikTok, YouTube, Facebook…) sẽ ra **toàn số 0** ở chế độ này, vì dữ liệu theo ngày không tách được theo nền tảng. Chỉ dùng cho partner hiển thị bảng dạng tổng.

**Vì sao cần nói:** creator vào giữa chiến dịch không bao giờ đuổi kịp ở chế độ Toàn thời gian — đó là lý do tính năng này ra đời. Nhưng Ops cần hiểu đây thuần tuý là cách trình bày, không phải cách tính thưởng.

---

## 2. Xếp hạng theo chỉ số

**Tooltip:**
> Chỉ số quyết định ai đứng trên ai. **Chỉ một chỉ số duy nhất** được dùng để sắp xếp; các cột còn lại chỉ để xem, không ảnh hưởng thứ tự.
>
> Nên để cột tương ứng đứng **đầu tiên** ở ô "Cột hiển thị", để người xem thấy bảng giảm dần từ trên xuống theo cột trái cùng.

**Vì sao cần nói:** nếu xếp hạng theo Lượt xem mà cột đầu là Tiền, người xem thấy cột trái cùng nhảy lung tung và tưởng bảng hỏng.

---

## 3. Tính điểm xếp hạng theo

> **Đề nghị đổi nhãn thành "Cơ sở tính số liệu"** — nhãn hiện tại nói "lượt xem" nhưng thiết lập này áp cho **cả tiền**, và cho **cả ba kỳ**.

**Tooltip:**
> Quyết định số liệu nào được đưa vào xếp hạng: chỉ phần **đã duyệt**, hay gồm cả phần **đang chờ duyệt**. Áp dụng cho mọi chỉ số và mọi kỳ.
>
> • **Chỉ số liệu đã duyệt** — con số chắc chắn, nhưng creator vừa đăng bài phải chờ duyệt mới lên bảng.
> • **Gồm cả số liệu chờ duyệt** — bảng phản ánh ngay hoạt động mới, nhưng thứ hạng có thể tụt khi bài bị từ chối.

**Cảnh báo tạm thời (gỡ khi Dev xử lý xong phần hiển thị):**
> Cột trên bảng hiện **luôn hiện tổng gồm cả phần chờ duyệt**. Nếu chọn "Chỉ số liệu đã duyệt", thứ hạng sẽ được tính theo con số khác với con số đang hiển thị — bảng trông như sắp xếp sai. Chỉ đổi khi đã trao đổi với đội kỹ thuật.

**Vì sao cần nói:** đây là ô nguy hiểm nhất của form. Một trong hai lựa chọn tạo ra bảng mâu thuẫn với chính nó.

---

## 4. Cột hiển thị

**Tooltip:**
> Chọn cột nào xuất hiện trên bảng và theo thứ tự nào. **Thứ tự các thẻ ở đây chính là thứ tự cột từ trái sang phải.**
>
> Bỏ thẻ "Tiền" ra tương đương tắt hiển thị số tiền trên bảng công khai.

**Ghi chú hiển thị dưới ô khi partner đã tắt hiển thị tiền ở cấu hình partner:**
> Partner này đang tắt hiển thị số tiền ở cấp partner. Thiết lập đó sẽ phủ lên lựa chọn tại đây.

---

## 5. Số ngày ân hạn đầu kỳ

**Tooltip:**
> Số ngày đầu kỳ mới mà bảng **vẫn hiển thị kỳ trước**.
>
> Số liệu của những ngày cuối kỳ cần thời gian để hệ thống thu thập và chốt. Chuyển kỳ ngay lúc 0h sẽ khiến bảng gần như trống, đồng thời kỳ vừa kết thúc chưa kịp đủ số.
>
> Ví dụ kỳ tuần, ân hạn 2 ngày: thứ Hai và thứ Ba vẫn hiện tuần trước, từ **thứ Tư** mới sang tuần mới.
>
> • Đặt **0** — đổi kỳ ngay lúc 0h, bảng đầu kỳ sẽ trống.
> • Đặt **càng lớn** — kỳ cũ càng có thời gian chốt số, nhưng creator phải chờ lâu hơn mới thấy thành tích kỳ mới.

**Cảnh báo hiện khi giá trị < 2:**
> Với giá trị nhỏ hơn 2, bảng chuyển sang kỳ mới trước khi số liệu ngày cuối kỳ cũ kịp chốt. Nếu có trao thưởng theo kỳ, thứ hạng kỳ cũ có thể chưa phải kết quả cuối cùng.

**Ghi chú vận hành đặt cạnh ô:**
> Nếu trao thưởng theo kỳ, chỉ chốt kết quả **sau khi hết thời gian ân hạn**.

---

## 6. Kỳ đang hiển thị (nhãn ở đầu khối Ghim)

**Tooltip:**
> Khoảng thời gian mà bảng **đang thực sự hiển thị** cho người xem ngay lúc này, đã tính cả ân hạn đầu kỳ.
>
> Dùng đúng mốc này khi đối chiếu số liệu và khi ghim creator — trong những ngày ân hạn, kỳ đang hiển thị **không phải** kỳ hiện tại theo lịch.

---

## 7. Ghim creator lên đầu bảng

**Tooltip:**
> Đưa creator lên đầu bảng bất kể thứ hạng thật của họ.
>
> Chỉ ghim được creator **có phát sinh số liệu trong kỳ đang hiển thị**. Ghim người không có số liệu sẽ khiến bảng công khai hiện tên họ kèm 0 lượt xem, 0đ.
>
> Ghim ảnh hưởng trực tiếp tới thứ hạng và giải thưởng, nên bắt buộc ghi lý do và hệ thống lưu lại người thực hiện.

**Tooltip cho ô hạn ghim:**
> Thời điểm ghim tự hết hiệu lực. **Nên đặt trùng ngày cuối của kỳ.** Nếu đặt dài hơn kỳ, sang kỳ sau creator đó vẫn nằm đầu bảng dù không còn hoạt động, và số liệu sẽ về 0.

**Placeholder ô tìm kiếm — đề nghị đổi:**
> Hiện tại: `Tìm theo tên trong sự kiện`
> Đề nghị: `Tìm creator có số liệu trong kỳ đang hiển thị`

**Vì sao đổi:** điều kiện được ghim là **có phát sinh trong kỳ**, không phải **đã tham gia sự kiện**. Hai tập này khác nhau, và nhầm sẽ dẫn thẳng tới dòng 0 view/0đ trên landing.

---

## 8. Nhãn các lựa chọn

| Ô | Nhãn hiện tại | Đề nghị | Lý do |
|---|---|---|---|
| Kỳ xếp hạng | Toàn thời gian / Theo tuần / Theo tháng | giữ nguyên | rõ ràng |
| Xếp hạng theo chỉ số | Lượt xem / Tiền | giữ nguyên | rõ ràng |
| Tính điểm xếp hạng theo | Gồm cả lượt xem chờ duyệt | **Gồm cả số liệu chờ duyệt** | thiết lập áp cho cả tiền, không riêng lượt xem |
| Tính điểm xếp hạng theo | (lựa chọn còn lại) | **Chỉ số liệu đã duyệt** | đối xứng với nhãn trên |
| Cột hiển thị | Tiền / Lượt xem | giữ nguyên | khớp tên cột trên landing |

---

## 9. Nhãn kế thừa từ partner (đề nghị bổ sung)

Form đang hiển thị giá trị cụ thể ở mọi ô nên Ops không phân biệt được đâu là giá trị **kế thừa từ partner**, đâu là giá trị **ghi đè riêng cho sự kiện này**. Bấm Lưu một lần là toàn bộ giá trị kế thừa bị đóng băng thành ghi đè cấp sự kiện — từ đó partner đổi mặc định sẽ không còn tác dụng lên sự kiện này.

**Đề nghị:** mỗi ô đang lấy giá trị kế thừa thì hiện nhãn nhỏ bên dưới:

> Đang kế thừa từ cấu hình partner. Sửa ô này sẽ tạo thiết lập riêng cho sự kiện.

Và bổ sung nút:

> **Trả về mặc định của partner**

---

## 10. Câu Ops hay hỏi — gợi ý đưa vào phần trợ giúp

**"Đổi kỳ xếp hạng có làm creator mất tiền không?"**
> Không. Kỳ xếp hạng chỉ đổi cách bảng hiển thị và xếp thứ tự. Tiền thưởng vẫn được tính và chi trả theo đúng luật của sự kiện, không phụ thuộc thiết lập này.

**"Sáng đầu tuần mở bảng thấy vẫn là tuần trước, có phải lỗi không?"**
> Không. Đó là thời gian ân hạn đầu kỳ, xem ô "Số ngày ân hạn đầu kỳ". Nhãn "Kỳ đang hiển thị" luôn cho biết bảng đang hiện khoảng nào.

**"Vừa đổi cấu hình mà bảng chưa đổi?"**
> Bảng có bộ nhớ đệm khoảng 10 phút. Đổi kỳ xếp hạng thì thấy ngay, các thiết lập khác có thể chờ tới 10 phút.

**"Creator vừa đăng bài mà chưa lên bảng?"**
> Nếu đang để "Chỉ số liệu đã duyệt" thì bài phải được duyệt mới tính. Ngoài ra số liệu theo ngày được hệ thống thu thập định kỳ, không tức thời.
