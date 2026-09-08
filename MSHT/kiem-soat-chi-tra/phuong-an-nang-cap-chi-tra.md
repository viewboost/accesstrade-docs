# Phương án nâng cấp hệ chi trả MSHT

> **Trình bày cho:** AccessTrade — đơn vị sở hữu MSHT trên MBBank
> **Ngày:** 2026-09-08 · **Người soạn:** Product Owner
> **Phạm vi:** chặng chi trả tiền hoàn về tài khoản khách hàng
>
> Tài liệu này trình bày **các nhóm chức năng sẽ phát triển, thứ tự triển khai, và những điểm cần
> AT-Core phối hợp**. Chi tiết kỹ thuật nằm ở bộ tài liệu đi kèm trong cùng thư mục.

---

## 1. Mục tiêu

Hệ chi trả hiện tại vận hành được ở đường thuận, nhưng **chưa có lớp kiểm soát cho đường nghịch**.
Khi một lệnh chi gặp trục trặc, hệ thống không tự kết luận được và phải chờ con người quyết định —
trong khi người đó không có đủ dữ liệu để quyết đúng.

Một sự cố chi trùng đã xảy ra theo đúng cơ chế đó.

Mục tiêu của phương án này:

> **Mỗi khoản tiền trả cho khách hàng có định danh rõ ràng · mọi trạng thái phản ánh đúng thực tế
> giao dịch · mọi thao tác đụng tiền đều có bằng chứng · hệ thống tự phát hiện và chặn sai lệch
> trước khi tiền tiếp tục chảy.**

Đây không phải một bản vá lỗi. Đây là **bổ sung lớp kiểm soát chi trả** mà một hệ thống thanh toán
cần có.

---

## 2. Cách tiếp cận

Ba nguyên tắc chi phối toàn bộ phương án:

**Nhìn trước, làm sau.** Đội vận hành hiện có quyền thay đổi trạng thái khoản chi nhưng không có
cách tra cứu tình trạng thật. Phương án đảo lại trật tự đó: trang bị khả năng tra cứu và đối chiếu
trước, rồi mới mở lại quyền thao tác — kèm điều kiện phải có bằng chứng.

**Chi trả theo đợt, và đợt sau chờ đợt trước.** Việc chi trả vốn đã diễn ra theo đợt hằng ngày,
nhưng đợt chưa được quản lý như một đối tượng có hồ sơ. Khi đợt trở thành đối tượng quản lý, ta có
đơn vị để đối soát, để chặn, và để phân quyền.

**Ưu tiên phòng ngừa hơn khắc phục.** Với chi hộ, khi tiền đã vào tài khoản khách hàng tại ngân hàng
thì khả năng thu hồi là rất thấp. Vì vậy trọng số dồn về việc **không tạo ra khoản chi sai**, thay
vì xử lý sau khi đã sai.

---

## 3. Các nhóm chức năng sẽ phát triển

### Nhóm A — Định danh và quản lý khoản chi

- Mỗi khoản tiền trả cho một khách hàng có **mã định danh duy nhất, không đổi suốt vòng đời** — kể
  cả khi phải gửi lại hay chuyển sang đợt khác.
- Ghi nhận **từng lần gửi** của một khoản chi: gửi lúc nào, nhận kết quả gì.
- **Quản lý theo đợt chi trả**: mỗi đợt có hồ sơ riêng — chi cho bao nhiêu người, tổng bao nhiêu
  tiền, đang ở giai đoạn nào.
- Phân biệt rõ **đợt tự động** và **đợt bù thủ công** trong dữ liệu.
- Tách bạch hai thao tác khác nhau về bản chất: *tạo một khoản chi mới* và *gửi lại một khoản chi
  đã có*.

> **Đây là nền của toàn bộ phương án.** Các nhóm sau đều dựa vào nó.

### Nhóm B — Theo dõi và tra cứu

- **Bảng theo dõi đợt chi trả**: tiến độ, số lượng, số tiền, so sánh với đợt trước.
- **Tra cứu tình trạng một khoản chi** và đối chiếu trực tiếp với hệ thống AT-Core.
- **Đối chiếu số tiền** thực tế đã chi với số tiền yêu cầu.
- Phân biệt rõ ba tình huống hiện đang bị gộp làm một: *chưa chi* · *đã chi* · *đã gửi nhưng chưa
  rõ kết quả*.
- Hồ sơ đầy đủ một khoản chi để trả lời khách hàng: đã qua những bước nào, ai xử lý, dựa trên gì.

### Nhóm C — Xử lý tình huống cho vận hành

- **Công cụ sắp xếp công việc**: chuyển khoản chi sang đợt sau, tạm gác chờ xử lý, đánh dấu ưu tiên
  cho ca khiếu nại. Những thao tác này **không đụng tới tiền**, nên vận hành dùng được thoải mái.
- **Quy trình xử lý khoản chi treo có thời hạn cam kết**: sau bao lâu thì cảnh báo, sau bao lâu thì
  chủ động liên hệ khách hàng.
- **Chi trả thủ công** khi hệ thống đối tác gián đoạn — đi qua đúng quy trình như chi tự động, có
  người duyệt và có đối soát, không phải đường vòng.

### Nhóm D — Kiểm soát rủi ro

- **Cổng kiểm tra giữa các đợt**: đợt sau không tự chạy khi đợt trước chưa chốt sổ. Một sự cố dừng
  lại ở một đợt thay vì lan sang các đợt tiếp theo.
- **Điều chỉnh quy mô đợt** để kiểm soát mức độ ảnh hưởng — bắt đầu nhỏ, nâng dần khi ổn định.
- **Công tắc dừng khẩn cấp** ở hai mức: dừng một đợt, hoặc dừng toàn bộ chi trả tự động.
- **Cảnh báo tự động** cho các dấu hiệu bất thường, mỗi cảnh báo có người chịu trách nhiệm xử lý.

### Nhóm E — Đối soát

Ba lớp, trả lời ba câu hỏi khác nhau, do ba bộ phận khác nhau chịu trách nhiệm:

| Lớp | Câu hỏi | Chủ sở hữu |
| --- | --- | --- |
| Nội bộ | Sổ chi trả có khớp số dư khách hàng không? | Vận hành |
| Với AT-Core | Sổ của mình có khớp sổ đối tác không? | Kế toán |
| Với ngân hàng | Tiền rời tài khoản có khớp tổng đã chi không? | Kế toán |

Kèm báo cáo định kỳ cho kế toán và cơ chế xử lý khoản lệch.

### Nhóm F — Phân quyền và truy vết

- **Phân quyền theo từng bước** của quy trình: tạo đợt, duyệt đợt, chạy, chốt sổ, xử lý ngoại lệ.
- **Nguyên tắc hai người** cho các thao tác đụng tới tiền: người duyệt phải khác người tạo.
- **Nhật ký đầy đủ**: ai thao tác, lúc nào, trên khoản nào, đổi từ trạng thái gì sang gì, và **dựa
  trên bằng chứng nào**.

---

## 4. Thứ tự triển khai

Bốn giai đoạn, mỗi giai đoạn là một mốc có thể tuyên bố đạt được.

### Giai đoạn 1 — An toàn để chi

**Đạt khi:** hệ thống không thể tạo ra khoản chi thứ hai cho cùng một nghĩa vụ khi chưa biết khoản
thứ nhất đã đi hay chưa.

Gồm: nhóm A đầy đủ, cộng việc siết lại các đường chi tiền hiện chưa có kiểm soát truy cập.

> **Đây là giai đoạn quan trọng nhất.** Hoàn thành giai đoạn này nghĩa là sự cố vừa rồi không lặp
> lại được nữa, kể cả khi các giai đoạn sau chưa xong.

### Giai đoạn 2 — An toàn để vận hành

**Đạt khi:** đội vận hành xử lý được phần lớn tình huống mà không cần đến kỹ sư.

Gồm: nhóm B và nhóm C.

### Giai đoạn 3 — An toàn để chạy tiếp

**Đạt khi:** một sự cố ở đợt này không lan sang đợt sau.

Gồm: nhóm D, cộng lớp đối soát nội bộ của nhóm E.

### Giai đoạn 4 — An toàn để mở rộng

**Đạt khi:** MSHT tự chứng minh được tiền đã đi đúng, bằng số liệu chứ không bằng niềm tin.

Gồm: nhóm F, cộng hai lớp đối soát còn lại của nhóm E.

### Ba luồng chạy song song

Thứ tự trên **không phải một đường thẳng**:

- **Luồng phát triển** đi theo bốn giai đoạn.
- **Luồng phối hợp với AT-Core** bắt đầu **ngay từ ngày đầu** — vì thời gian phản hồi của bên thứ ba
  dài nhất trong toàn bộ kế hoạch.
- **Luồng vận hành** cũng bắt đầu ngay: quy trình tạm thời, kịch bản trả lời khách hàng, danh sách
  theo dõi thủ công — để đội vận hành có công cụ dùng trong lúc chờ hệ thống.

---

## 5. Những điểm cần AT-Core hỗ trợ

Sau khi rà soát tài liệu API của AT-Core, **phần lớn năng lực cần thiết đã có sẵn** — vấn đề là phía
MSHT chưa sử dụng. Cụ thể, ba việc dưới đây **không cần AT-Core làm gì thêm**:

| Năng lực | Tình trạng |
| --- | --- |
| Chống trùng khoản chi | ✅ Đã có. MSHT sẽ điều chỉnh cách sinh mã để kích hoạt |
| Kiểm tra số dư tài khoản nguồn | ✅ Đã có. MSHT sẽ bắt đầu sử dụng |
| Chi trả theo lô | ✅ Đã có. MSHT sẽ chuyển sang dùng |
| Kiểm tra tài khoản nhận, điều khoản khách hàng | ✅ Đã có. MSHT sẽ bổ sung vào quy trình |

**Ba điểm thật sự cần AT-Core phối hợp:**

### 5.1 Truy vấn kết quả giao dịch theo khoảng thời gian — *ưu tiên cao nhất*

**Cần gì:** khả năng lấy danh sách giao dịch trong một khoảng thời gian do MSHT chỉ định, kèm mã
giao dịch, số tiền, trạng thái và thời điểm.

**Vì sao cần:** hiện MSHT chỉ tra cứu được từng giao dịch mà mình đã biết mã. Điều này đủ để kiểm
tra một trường hợp cụ thể, nhưng **không đủ để đối soát cả một đợt** — và cũng không cho phép phát
hiện một khoản chi bất thường mà MSHT không biết là có.

**Ảnh hưởng nếu không có:** lớp đối soát với AT-Core (giai đoạn 4) không triển khai được. Ba giai
đoạn đầu vẫn chạy bình thường.

**Đề xuất:** API hoặc file định kỳ đều được. Nhịp mong muốn là sẵn sàng trước giờ chốt sổ hằng ngày.

### 5.2 Làm rõ hợp đồng thông báo kết quả (callback)

**Cần gì:** thống nhất bằng văn bản về chính sách gửi lại khi MSHT chưa xác nhận, cách xác thực
nguồn gốc thông báo, và mã phản hồi nào có nghĩa là đã nhận thành công.

**Vì sao cần:** tài liệu API hiện tại mô tả các lệnh gọi chủ động, chưa mô tả kênh thông báo ngược.
Việc thiếu thống nhất khiến hai bên có thể hiểu khác nhau về việc một thông báo đã được xử lý hay chưa.

### 5.3 Thủ tục tra soát và xử lý khoản chi sai

**Cần gì:** xác định rõ có thủ tục thu hồi một khoản chi sai hay không, ai khởi tạo, thời gian xử lý,
và đầu mối liên hệ khi có sự cố kèm thời hạn phản hồi.

**Vì sao cần:** đây là **câu hỏi nghiệp vụ, không phải kỹ thuật**. Nếu câu trả lời là không thu hồi
được, khẩu vị rủi ro của cả hệ thống thay đổi và trọng số phải dồn hoàn toàn về phòng ngừa.

### 5.4 Mong muốn thêm — cổng tra cứu cho đội vận hành

Hiện mọi tra cứu sang AT-Core đều phải qua hệ thống, tức là qua kỹ sư. Một cổng tra cứu dành cho
người vận hành — tra giao dịch, xem trạng thái, tải file đối soát, xem tình trạng dịch vụ — sẽ giảm
đáng kể phụ thuộc kỹ thuật ở cả hai phía.

---

## 6. Kết quả đo được

Sau khi hoàn thành, năm chỉ số theo dõi:

| Nhóm | Chỉ số | Mục tiêu |
| --- | --- | --- |
| An toàn tài chính | Số khoản chi trùng đã xác nhận | **0** |
| Độc lập vận hành | Tỉ lệ tình huống xử lý xong không cần kỹ sư | tăng dần đến **95%** |
| Đối soát | Số tiền chưa đối soát | về **0** |
| Khách hàng | Thời gian chờ của khoản chi lâu nhất | trong cam kết |
| Quản trị | Tỉ lệ thao tác đụng tiền có đầy đủ bằng chứng | **100%** |

---

## 7. Những điều cần AccessTrade quyết

Bốn quyết định nghiệp vụ đang chặn phần thiết kế:

**7.1 — Khi chưa rõ giao dịch đã đi hay chưa, mặc định xử lý thế nào?**
Coi như *đã chi* (an toàn về tiền, khách hàng chờ lâu hơn) hay coi như *chưa chi* (khách hàng nhận
nhanh, doanh nghiệp chịu rủi ro chi trùng)?
*Đề xuất: coi như đã chi* — vì thiệt hại hai chiều không cân nhau và khả năng thu hồi thấp.

**7.2 — Một khoản chi được phép chờ tối đa bao lâu** trước khi cảnh báo và trước khi chủ động liên
hệ khách hàng?

**7.3 — Hạn mức rút tiền theo tháng còn hiệu lực không?**
Hiện có hạn mức được công bố trong thông điệp gửi khách nhưng chưa được thực thi trong hệ thống.
Cần thống nhất: khôi phục hạn mức, hay điều chỉnh nội dung công bố.

**7.4 — Mức độ ưu tiên và nguồn lực** cho từng giai đoạn.

---

## Phụ lục — Bộ tài liệu chi tiết

| Tài liệu | Nội dung |
| --- | --- |
| [`lo-trinh.md`](./lo-trinh.md) | Lộ trình, mốc, phụ thuộc |
| [`phan-tich-va-giai-phap.md`](./phan-tich-va-giai-phap.md) | Phân tích hiện trạng, sổ rủi ro, quyết định |
| [`mo-hinh-payout-va-tieu-chi-nghiem-thu.md`](./mo-hinh-payout-va-tieu-chi-nghiem-thu.md) | Mô hình dữ liệu, tiêu chí nghiệm thu |
| [`cong-cu-cho-van-hanh-chi-tra.md`](./cong-cu-cho-van-hanh-chi-tra.md) | Yêu cầu công cụ vận hành |
| [`van-de-can-at-core-ho-tro.md`](./van-de-can-at-core-ho-tro.md) | Chi tiết các điểm cần AT-Core |
| [`at-core-partner-bank-gateway-api.md`](./at-core-partner-bank-gateway-api.md) | Tài liệu API AT-Core |
