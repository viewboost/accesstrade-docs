# Công cụ cho vận hành chi trả

> **Vì sao có tài liệu này:** bản phân tích đầu tiên viết cho người **xây** hệ thống, không viết cho
> người **sống với nó mỗi ngày**. Vận hành chi trả không phải nghề "chờ có sự cố rồi xử lý" — đó là
> nghề **kiểm tra đợt thường xuyên**, và phần lớn thời gian là việc thường ngày chứ không phải cứu hoả.
>
> **Trạng thái:** yêu cầu nghiệp vụ, chưa thiết kế giao diện.
> **Đi kèm:** [`phan-tich-va-giai-phap.md`](./phan-tich-va-giai-phap.md) ·
> [`van-de-can-at-core-ho-tro.md`](./van-de-can-at-core-ho-tro.md)

---

## 1. Nguyên tắc phân loại: hai loại thao tác, đừng trộn

Đây là nguyên tắc chi phối toàn bộ tài liệu.

| | **Loại A — Khẳng định về tiền** | **Loại B — Sắp xếp công việc** |
| --- | --- | --- |
| Ví dụ | "Lệnh này thành công" · "Lệnh này thất bại, hoàn tiền" | Dời sang đợt sau · Tạm gác · Loại khỏi đợt · Đánh dấu ưu tiên · Ghi chú |
| Đụng tiền? | **Có** | **Không** |
| Cần bằng chứng? | Bắt buộc — câu trả lời từ AT-Core | Không, chỉ cần lý do |
| Cần người thứ hai? | Có, trên ngưỡng | Không |
| Hoàn tác được? | Không | Có |

**Hiện trạng là bản đảo ngược của cái đúng:** vận hành chỉ có đúng **một** công cụ, và nó thuộc
loại A — nút đổi trạng thái tay. Còn loại B, thứ họ cần dùng hàng chục lần mỗi ngày, thì **không có
cái nào**.

⇒ Kết quả tất yếu: mọi bế tắc đều phải giải bằng công cụ nguy hiểm nhất, hoặc gọi kỹ sư.

**Đích cần đạt:** vận hành có thật nhiều công cụ loại B, và rất ít loại A.

---

## 2. Nhịp làm việc hằng ngày

Thiết kế công cụ phải bám nhịp này, không bám sơ đồ kỹ thuật.

### Trước đợt — khoảng 06:00

- Đợt hôm trước đã chốt sổ chưa? Cổng đang xanh hay đỏ?
- Đợt hôm nay dự kiến bao nhiêu lệnh, bao nhiêu tiền? Có bất thường so với hôm qua không?
- Nguồn tiền có đủ cho đợt không?
- AT-Core có đang bình thường không?
- Có lệnh nào từ đợt cũ dời sang đợt này? Bao nhiêu?

### Trong đợt — từ 07:00

- Tiến độ: đã gửi bao nhiêu, còn bao nhiêu, đang tắc ở đâu?
- Tỉ lệ lỗi có vọt bất thường không?
- **Cần dừng đợt giữa chừng thì bấm ở đâu?**

### Sau đợt

- Danh sách lệnh chưa có kết quả — tra từng ca.
- Ca nào chưa xử lý được thì **dời hoặc gác**, không để nó chặn.
- Trả lời khiếu nại khách trong ngày.

### Chốt sổ — khoảng 03:00 hôm sau

- Đối soát với AT-Core: sổ mình khớp sổ họ không?
- Dòng lệch: phân loại, xử lý hoặc chấp nhận có lý do.
- Kết luận cổng cho đợt kế tiếp.

### Hằng tuần / hằng tháng

- Báo cáo cho kế toán.
- Xu hướng: tỉ lệ hỏng, thời gian xử lý trung bình, số ca phải can thiệp tay.

---

## 3. Nhóm A — Giám sát đợt

Cái vận hành mở đầu tiên mỗi sáng.

- **Bảng đợt**: mỗi dòng một đợt — mã, loại, thời điểm, trạng thái vòng đời, số lệnh, tổng tiền,
  tách theo thành công / chưa rõ / hỏng / đã dời.
- **So với đợt trước**: số lệnh, tổng tiền, tỉ lệ thành công. Lệch bất thường phải nhìn ra ngay,
  không cần tự tính.
- **Đồng hồ ca cũ nhất**: lệnh treo lâu nhất đang bao nhiêu giờ.
- **Tình trạng đối tác**: AT-Core còn phản hồi không, tỉ lệ lỗi gần đây.
- **Nguồn tiền**: còn đủ cho đợt kế không (phụ thuộc mô hình thanh toán — xem checklist dev mục 1).
- **Tiến độ đợt đang chạy**, cập nhật liên tục, kèm **nút dừng đợt**.

### Công tắc dừng — phải có HAI mức

Dừng một đợt là chưa đủ. Có **bốn cửa chi tiền**; dừng đợt mà cửa khác vẫn chạy được thì đó không
phải kiểm soát toàn hệ.

| Mức | Dừng cái gì | Ai bấm được | Dùng khi |
| --- | --- | --- | --- |
| **1 · Dừng đợt** | Đợt đang chạy | Vận hành | Tỉ lệ lỗi vọt · phát hiện bất thường giữa đợt |
| **2 · Dừng toàn hệ** | **Mọi đường chi tự động, cả bốn cửa** | Cấp cao hơn | AT-Core bất thường · nghi ngờ chi trùng hàng loạt · đối soát vỡ · nghi vấn toàn vẹn callback · sự cố bảo mật |

Mức 2 phải: bật/tắt **không cần triển khai lại mã** · sinh cảnh báo ngay · ghi audit ai bấm và vì sao.

> Sau khi bật mức 2, **kênh chi tay vẫn dùng được** — đó là lý do nó phải là kênh chính thức chứ
> không phải đường lui. Dừng tự động không có nghĩa là dừng trả tiền cho khách.

---

## 4. Nhóm B — Tra cứu

Khách gọi lên, phải tìm ra hồ sơ của họ trong vòng ba mươi giây.

- **Tra theo**: mã lệnh · mã đợt · người dùng · số tài khoản nhận · số tiền · khoảng thời gian.
- **Hồ sơ đầy đủ một lệnh**: mọi lần đổi trạng thái, ai đổi, lúc nào, **dựa trên bằng chứng nào**.
- **Nguyên văn đã gửi và đã nhận** với AT-Core cho lệnh đó.
- **Nút "Tra AT-Core ngay"** — gọi `txn-inquiry`, hiện nguyên văn: trạng thái, **số tiền**, mã tham chiếu.
- **Khách đang thấy gì**: trạng thái hiển thị trong ứng dụng và các thông báo đã gửi cho họ.
  Vận hành phải biết khách đang đọc gì trước khi nói chuyện.
- **Ghi chú vào hồ sơ** để người trực ca sau đọc được.

---

## 5. Nhóm C — Xử lý ca kẹt

Đây là nhóm quan trọng nhất và đang **trống hoàn toàn**.

### Quy tắc an toàn: được làm gì phụ thuộc lệnh đã gửi đi chưa

| Trạng thái lệnh | Dời đợt | Tạm gác | Loại khỏi đợt | Gửi lại | Đóng bằng bằng chứng |
| --- | :---: | :---: | :---: | :---: | :---: |
| **Chưa gửi** đi đâu cả | ✅ | ✅ | ✅ | — | — |
| **Đã gửi, chưa rõ kết quả** | ❌ | ✅ | ❌ | ❌ | Chỉ sau khi tra AT-Core |
| **Đã có kết quả dứt khoát** | — | — | — | Chỉ khi hỏng, cùng mã cũ | ✅ |

> 🔴 **Dòng giữa là dòng sinh ra sự cố vừa rồi.** Một lệnh đã gửi mà chưa rõ kết quả thì **không được
> dời, không được loại, không được gửi lại** — vì mọi thao tác đó đều có thể dẫn tới lần chi thứ hai.
> Nó chỉ được **tra** và **gác**. Công cụ phải tự chặn, không dựa vào người dùng nhớ.

### Các thao tác cần có

| Thao tác | Loại | Dùng khi |
| --- | :---: | --- |
| **Dời sang đợt sau** | B | Lệnh chưa gửi mà đợt này không xử lý được — để nó không chặn đợt chốt sổ |
| **Tạm gác** (kèm lý do, kèm hạn xem lại) | B | Đang chờ thông tin, chờ đối tác, chờ khách. Không tính vào cổng |
| **Loại khỏi đợt trước khi chạy** | B | Phát hiện bất thường lúc soát đợt |
| **Đánh dấu ưu tiên** | B | Ca khiếu nại gấp |
| **Gửi lại lệnh cũ** (đúng nghĩa: **cùng mã**) | A | Chỉ khi có kết quả dứt khoát là hỏng |
| **Đóng bằng bằng chứng ngoài** | A | Đã chi tay qua đường khác — kèm mã giao dịch ngân hàng |
| **Hoàn tiền cho khách** | A | Chỉ khi AT-Core khẳng định không chi. Cần người thứ hai trên ngưỡng |

Mọi thao tác đều **bắt buộc nhập lý do** và ghi vào bảng audit.

### Van xả cho bẫy "chặn lệnh mới khi còn lệnh treo"

Ưu tiên 0 trong tài liệu phân tích chặn tạo lệnh mới khi khách còn lệnh treo. Ghép với việc lệnh
hỏng không tự kết thúc, khách có thể bị khoá vô hạn.

**Van xả bắt buộc đi kèm, không được để sau:** thao tác **tạm gác** phải gỡ khách khỏi tình trạng bị
chặn. Lệnh gác vẫn tồn tại, vẫn phải xử lý, nhưng **không chặn đợt sau của người đó nữa**.

Không có van này thì ưu tiên 0 tạo ra một hàng đợi khiếu nại mới.

---

## 6. Nhóm D — Cảnh báo

Nguyên tắc: **mỗi cảnh báo phải có người sở hữu và một hành động kèm theo.** Cảnh báo không ai xử lý
thì sau hai tuần không ai mở nữa.

| Cảnh báo | Ngưỡng | Ai nhận | Làm gì |
| --- | --- | --- | --- |
| Đợt không khởi động đúng giờ | Trễ 15 phút | Vận hành + kỹ sư trực | Kiểm lịch chạy và khoá |
| Đợt chạy quá lâu chưa xong | Vượt thời lượng thường ngày | Vận hành | Xem tiến độ, cân nhắc dừng |
| Tỉ lệ "chưa rõ kết quả" vọt | Ngưỡng chốt ở **D4** | Vận hành | **Dừng đợt**, tra AT-Core |
| Lệnh treo quá hạn | Ngưỡng chốt ở **D2** | Vận hành | Tra soát từng ca |
| Tổng tiền đợt lệch dự báo | Lệch quá x% | Vận hành + PO | Dừng, kiểm trước khi tiếp |
| **Nghi ngờ chi trùng** (đèn báo khói) | Cùng người, cùng số tiền, hai lệnh thành công < 48h | Vận hành | **Ưu tiên cao nhất**, tra ngay |
| Đối soát lệch với AT-Core | Bất kỳ dòng nào | Vận hành + kế toán | Phân loại lệch, xử lý hoặc chấp nhận có lý do |
| AT-Core không phản hồi | Lỗi liên tục quá X phút | Vận hành + kỹ sư | Cân nhắc bật chế độ chi tay |
| Callback không về sau khi gửi lệnh | Quá X phút | Vận hành | Chủ động tra thay vì chờ |
| Nguồn tiền sắp cạn | Còn đủ dưới N đợt | Vận hành + kế toán | Bổ sung |
| **Có người dùng van xả mở cổng đỏ** | Mỗi lần | PO / founder | Xem ai mở, vì sao — đây là chỗ sự cố sau sẽ đi qua |
| **Có thao tác loại A được thực hiện** | Mỗi lần | PO | Kiểm có đúng quy trình không |

Hai dòng cuối là **cảnh báo về chính con người**, không về hệ thống. Chúng là thứ giữ cho quy trình
không bị mòn theo thời gian.

---

## 7. Nhóm E — AT-Core phải cung cấp gì cho vận hành

**Đây là phần bị bỏ sót hoàn toàn trong bản phân tích đầu.** Yêu cầu gửi đối tác mới chỉ toàn API —
tức là mọi lần tra cứu vẫn phải đi qua kỹ sư. **Như vậy là dựng lại đúng vấn đề "phải hỏi kỹ sư",
lần này ở ranh giới đối tác.**

### Cổng tra cứu cho người, không phải cho máy

- **Tài khoản riêng cho vận hành MSHT** — không dùng chung tài khoản kỹ thuật.
- **Tra cứu giao dịch** theo cả ba loại mã, theo khoảng thời gian, theo số tài khoản, theo số tiền.
- **Chi tiết một giao dịch**: trạng thái thật, số tiền thật, thời điểm từng bước, lý do hỏng nếu có.
- **Xuất file đối soát** theo kỳ, tự lấy được, không phải xin.
- **Trang tình trạng dịch vụ**: đang bình thường hay sự cố. Không có trang này thì mỗi lần AT-Core
  trục trặc, bên mình phải **đoán**, và đoán sai chính là cách sự cố vừa rồi bắt đầu.
- **Lịch bảo trì báo trước**, để không trùng giờ chạy đợt.
- **Kênh báo sự cố có mã theo dõi và thời hạn phản hồi** — không phải tin nhắn cá nhân.

### Chiều ngược lại

Cũng phải hỏi: **AT-Core cần gì từ MSHT khi có sự cố?** Đầu mối bên mình là ai, họ báo vào đâu,
mình cam kết phản hồi trong bao lâu. Hiện chưa ai hỏi câu này.

---

## 8. Nhóm F — Đối soát và báo cáo

- **Bảng lệch hằng ngày**, phân loại theo lớp — nội bộ · với AT-Core · với sao kê ngân hàng.
  Ba lớp này **không gộp một màn**: khác câu hỏi, khác người đọc, khác nhịp.

### Mỗi lớp đối soát phải có chủ

Không có dòng này thì đối soát trở thành một tác vụ chạy đều mỗi ngày mà **không ai sở hữu khoản lệch**.

| Lớp | Câu hỏi | Chủ sở hữu | Nhịp | Ai được đóng khoản lệch |
| --- | --- | --- | --- | --- |
| **1 · Nội bộ** | Sổ lệnh có khớp số dư và bút toán không? | Sản phẩm + Vận hành | Hằng ngày | Vận hành |
| **2 · Với AT-Core** | Sổ mình có khớp sổ đối tác không? | Kế toán + Sản phẩm | Hằng ngày | **Kế toán** |
| **3 · Sao kê ngân hàng** | Tiền rời tài khoản công ty có khớp tổng đã chi không? | Kế toán | Hằng ngày | **Kế toán** |

Quyền **đóng một khoản lệch** khác quyền **nhìn thấy nó**. Lớp 2 và lớp 3 đụng tới sổ sách tài chính
nên quyền đóng thuộc kế toán, không thuộc vận hành.
- **Nút "chấp nhận lệch có lý do"** kèm audit — không phải mọi lệch đều là lỗi.
- **Đánh dấu kênh chi** (`AT-Core` / `chi tay`) trên từng lệnh. Khoản chi tay **không bao giờ xuất
  hiện trong sổ AT-Core**; không có trường này thì chúng bị báo lệch vĩnh viễn.
- **Xuất báo cáo cho kế toán** theo kỳ.

---

## 9. Hôm nay có gì, cần gì

| Nhóm | Hôm nay | Khoảng cách |
| --- | --- | --- |
| A · Giám sát đợt | Không có gì — đợt còn chưa tồn tại trong dữ liệu | Toàn bộ |
| B · Tra cứu | Danh sách lệnh trong CRM, không tra được AT-Core | Lớn |
| C · Xử lý ca kẹt | **Không có thao tác loại B nào** | Toàn bộ |
| D · Cảnh báo | Không có | Toàn bộ |
| E · Cổng đối tác | Không có, và **chưa từng hỏi** | Toàn bộ |
| F · Đối soát | Không có | Toàn bộ |
| Loại A nguy hiểm | **Có sẵn, không rào chắn** | Cần siết lại |

---

## 10. Thứ tự làm

Bám theo mức ưu tiên trong [`phan-tich-va-giai-phap.md`](./phan-tich-va-giai-phap.md):

| Đợt làm | Việc | Vì sao thứ tự này |
| --- | --- | --- |
| **Ngay, cùng ưu tiên 0** | Truy vấn lưu sẵn: lệnh treo quá 24h, kèm mã tra cứu · quy tắc tạm cho nút loại A · kịch bản trả lời khách | Vận hành cần sống sót tuần này, trước khi có màn nào |
| **Cùng ưu tiên 1** | Bảng đợt (nhóm A) — có đợt thì có cái để xem | Đợt là điều kiện của mọi thứ |
| **Cùng ưu tiên 2** | Tra cứu + nút tra AT-Core (nhóm B) · **thao tác loại B** (nhóm C) · van xả cho bẫy chặn | Mắt trước, tay sau |
| **Cùng ưu tiên 3** | Cảnh báo (nhóm D) · đối soát lớp 1 (nhóm F) | Có cổng rồi mới có cái để cảnh báo |
| **Đưa vào đàm phán ngay** | Cổng tra cứu cho vận hành (nhóm E) | Thời gian chờ đối tác dài nhất — hỏi sớm, dùng sau |

> Dòng đầu tiên là dòng dễ bị bỏ qua nhất và cũng rẻ nhất. **Ba việc đó không cần một dòng mã nào
> ở service chi trả** — một truy vấn lưu sẵn, một quy tắc viết ra giấy, một kịch bản trả lời. Làm
> được trong ngày.
