# Phương án nâng cấp hệ chi trả MSHT

> **Trình bày cho:** AccessTrade — đơn vị sở hữu MSHT trên MBBank
> **Ngày:** 2026-09-08 · **Người soạn:** Product Owner
> **Phạm vi:** chặng chi trả tiền hoàn về tài khoản khách hàng
>
> Tài liệu trình bày **bối cảnh, vấn đề và phương án** — các nhóm chức năng sẽ phát triển, thứ tự
> triển khai, và những điểm cần AT-Core phối hợp. Chi tiết kỹ thuật nằm ở bộ tài liệu đi kèm.

---

# PHẦN I — BỐI CẢNH

## 1.1 Dòng tiền của MSHT

MSHT là tính năng mua sắm hoàn tiền trong ứng dụng MBBank. Khách hàng mua sắm qua nhãn hàng liên kết,
tiền hoàn tích lại, và cuối cùng phải chảy về tài khoản ngân hàng của họ.

Tiền hoàn đi qua năm chặng:

| | Chặng | Nội dung |
| --- | --- | --- |
| 01 | Mua sắm | Khách đặt đơn qua nhãn hàng liên kết |
| 02 | Chờ duyệt | Nhãn hàng xác nhận đơn hợp lệ |
| 03 | Giữ 60 ngày | Phòng trường hợp hoàn/huỷ đơn |
| 04 | Đủ điều kiện | Vào số dư tiền hoàn được rút |
| **05** | **Chi trả** | **Chuyển về tài khoản khách hàng** |

**Phạm vi tài liệu này là chặng 05.** Bốn chặng đầu có thể sai lệch về số liệu và sửa được;
chỉ chặng 05 làm mất tiền mặt.

## 1.2 Chi trả đi qua ba bên

MSHT **không chi thẳng qua ngân hàng**. Chuỗi thực tế:

```
MSHT  →  AT-Core Chi hộ  →  Ngân hàng  →  Khách hàng
```

Điều này có hai hệ quả quan trọng:

- **Đối tác đối soát của MSHT là AT-Core**, không phải ngân hàng. Câu hỏi *"tiền đã đi chưa"* phải
  hỏi AT-Core.
- Mỗi lần chuyển tay đều có thể gián đoạn, và **từ đầu chuỗi nhìn xuống, mọi kiểu gián đoạn hiện ra
  giống hệt nhau**.

## 1.3 Bước ngoặt: mô hình tự động

Từ 30/07/2026, sản phẩm chuyển sang tự động — tiền hoàn tự chuyển về Ví tiết kiệm tiền lẻ, không cần
khách thao tác. Một tác vụ chạy mỗi sáng quét toàn bộ khách đủ điều kiện và chi trả.

Về trải nghiệm, đây là nâng cấp tốt và đúng hướng.

Về kiểm soát, bước ngoặt này **lấy đi ba thứ cùng lúc mà chưa có gì được đặt vào thay**:

| Mất gì | Hệ quả |
| --- | --- |
| **Mốc đối chiếu "ý định"** | Trước đây mỗi lệnh chi ứng với một lần khách bấm nút — một sự kiện có thật, không nhân đôi được. Nay không còn mốc nào để khẳng định hai lệnh là cùng một ý định |
| **Người phát hiện lỗi sớm nhất** | Khách hàng từng là lớp kiểm tra đầu tiên: họ bấm rút, họ theo dõi, họ khiếu nại ngay. Nay họ không biết hôm nay hệ thống có chi cho mình hay không |
| **Giới hạn tự nhiên về tần suất** | Một người bấm vài lần mỗi tháng. Một tác vụ tự động chi cho cả tập khách hàng mỗi ngày — một lỗi không còn ảnh hưởng một người mà cả mẻ |

---

# PHẦN II — VẤN ĐỀ

## 2.1 Tóm tắt

Hệ chi trả vận hành tốt ở **đường thuận**. Vấn đề nằm ở **đường nghịch** — khi có trục trặc.

Khi một lệnh chi gặp sự cố, hệ thống không tự kết luận được. Nó dừng lại và chờ một con người quyết
định — trong khi người đó **không có đủ dữ liệu để quyết đúng**, thao tác của họ **không hoàn tác
được**, và **không ai đối soát lại sau đó**.

Một sự cố chi trùng đã xảy ra theo đúng cơ chế này.

## 2.2 Sáu khoảng trống

### ① Khoản chi chưa có định danh ổn định

Mỗi lần thử lại một khoản chi, hệ thống sinh ra một mã giao dịch mới gửi sang AT-Core. Dưới góc nhìn
của đối tác, lần thử thứ hai **không phải là thử lại — nó là một khoản chi mới, độc lập và hợp lệ**.

Nói cách khác: hiện tại thao tác "gửi lại" không tồn tại. Chỉ có "tạo mới".

### ② Không phân biệt "chưa chi" với "chưa biết kết quả"

Khi kết nối tới đối tác gián đoạn, hệ thống không biết lệnh đã đi hay chưa. Nhưng trên nhật ký vận
hành, tình huống *"có thể đã chi rồi"* hiện ra **giống hệt** tình huống *"chưa chi gì cả"*.

Người vận hành đọc và kết luận điều hợp lý duy nhất có thể kết luận với thông tin họ có.

### ③ Khoản chi hỏng không có điểm kết thúc

Khi đối tác báo giao dịch thất bại, hệ thống hiện không có trạng thái kết thúc tương ứng. Khoản chi
đó ở lại trạng thái chờ **vô thời hạn**.

Hệ quả kép: tiền của khách bị treo không có hạn, và cách duy nhất để đóng lại là có người can thiệp
thủ công. Đây là gốc rễ của việc mọi tình huống bất thường đều phải qua kỹ thuật.

### ④ Chưa có đối soát

Hiện chưa có cơ chế nào đối chiếu sổ chi trả của MSHT với sổ của AT-Core, hay với sao kê ngân hàng.

Hệ quả: **sai lệch chỉ được phát hiện khi có người bên ngoài nói cho biết** — khách hàng khiếu nại,
hoặc kế toán tình cờ đối chiếu. Chúng ta chưa có cách biết quy mô thực tế bằng số liệu.

### ⑤ Đội vận hành thiếu công cụ

Đội vận hành hiện có quyền thay đổi trạng thái khoản chi — thao tác đụng trực tiếp tới tiền — nhưng
**không có cách tra cứu tình trạng thật** ở phía đối tác trước khi quyết định.

Trật tự đang bị đảo ngược: có quyền ghi mà không có quyền đọc. Kết quả là mọi tình huống đều dồn về
đội kỹ thuật, kể cả những việc lẽ ra vận hành tự làm được.

### ⑥ Không có ranh giới giữa các đợt chi trả

Việc chi trả diễn ra theo đợt hằng ngày, nhưng đợt chưa được quản lý như một đối tượng có hồ sơ.
Không có bước chốt sổ, và **đợt sau vẫn chạy bất kể đợt trước đã xử lý xong hay chưa**.

Một sự cố vì thế không dừng lại ở một đợt.

## 2.3 Bốn nhóm rủi ro

| Rủi ro | Nội dung |
| --- | --- |
| **Chi trùng** | Cùng một nghĩa vụ được trả hai lần |
| **Hoàn tiền sai** | Đã chi thật nhưng hệ thống ghi nhận thất bại, hoàn tiền vào số dư, rồi đợt sau chi lại |
| **Tiền khách treo** | Hệ thống quá thận trọng, khoản chi hợp lệ nằm chờ không có hạn |
| **Sai lệch âm thầm** | Đợt sau tiếp tục chạy trong khi sai lệch của đợt trước chưa ai biết |

Hai rủi ro đầu làm mất tiền. Rủi ro thứ ba ảnh hưởng khách hàng và uy tín sản phẩm trong ứng dụng
ngân hàng. Rủi ro thứ tư khiến ba cái còn lại khó phát hiện.

> **Lưu ý về khả năng thu hồi:** với mô hình chi hộ, khi tiền đã ghi có vào tài khoản khách hàng tại
> ngân hàng thì khả năng thu hồi là rất thấp. Đây là lý do phương án dồn trọng số vào **phòng ngừa**
> thay vì khắc phục.

---

# PHẦN III — GIẢI PHÁP

## 3.1 Mục tiêu

> **Mỗi khoản tiền trả cho khách hàng có định danh rõ ràng · mọi trạng thái phản ánh đúng thực tế
> giao dịch · mọi thao tác đụng tiền đều có bằng chứng · hệ thống tự phát hiện và chặn sai lệch
> trước khi tiền tiếp tục chảy.**

Đây không phải một bản vá lỗi, mà là **bổ sung lớp kiểm soát chi trả** mà một hệ thống thanh toán
cần có.

## 3.2 Ba nguyên tắc

**Nhìn trước, làm sau.** Trang bị khả năng tra cứu và đối chiếu trước, rồi mới mở lại quyền thao tác
— kèm điều kiện phải có bằng chứng. Đây là đảo ngược trật tự hiện tại.

**Chi trả theo đợt, và đợt sau chờ đợt trước.** Khi đợt trở thành đối tượng quản lý có hồ sơ, ta có
đơn vị để đối soát, để chặn, và để phân quyền.

**Phòng ngừa hơn khắc phục.** Vì khả năng thu hồi thấp, trọng số dồn vào việc không tạo ra khoản chi
sai ngay từ đầu.

## 3.3 Sáu nhóm chức năng sẽ phát triển

### Nhóm A — Định danh và quản lý khoản chi

- Mỗi khoản tiền trả cho một khách hàng có **mã định danh duy nhất, không đổi suốt vòng đời** — kể
  cả khi phải gửi lại hay chuyển sang đợt khác.
- Ghi nhận **từng lần gửi**: gửi lúc nào, nhận kết quả gì.
- **Quản lý theo đợt chi trả**: mỗi đợt có hồ sơ riêng — bao nhiêu người, bao nhiêu tiền, đang ở
  giai đoạn nào.
- Phân biệt **đợt tự động** và **đợt bù thủ công** trong dữ liệu.
- Tách bạch hai thao tác khác nhau về bản chất: *tạo khoản chi mới* và *gửi lại khoản chi đã có*.

> **Đây là nền của toàn bộ phương án.** Năm nhóm sau đều dựa vào nó. *(Gỡ vấn đề ① và ⑥)*

### Nhóm B — Theo dõi và tra cứu

- **Bảng theo dõi đợt chi trả**: tiến độ, số lượng, số tiền, so sánh với đợt trước.
- **Tra cứu tình trạng khoản chi** và đối chiếu trực tiếp với AT-Core.
- **Đối chiếu số tiền** thực tế đã chi với số tiền yêu cầu.
- Phân biệt rõ ba tình huống đang bị gộp: *chưa chi* · *đã chi* · *đã gửi nhưng chưa rõ kết quả*.
- Hồ sơ đầy đủ một khoản chi để trả lời khách hàng. *(Gỡ vấn đề ② và ⑤)*

### Nhóm C — Xử lý tình huống cho vận hành

- **Công cụ sắp xếp công việc**: chuyển khoản chi sang đợt sau, tạm gác chờ xử lý, đánh dấu ưu tiên.
  Những thao tác này **không đụng tới tiền** nên vận hành dùng được thoải mái.
- **Quy trình xử lý khoản treo có thời hạn cam kết**: sau bao lâu cảnh báo, sau bao lâu chủ động
  liên hệ khách hàng.
- **Chi trả thủ công** khi hệ thống đối tác gián đoạn — đi qua đúng quy trình như chi tự động, có
  người duyệt và có đối soát. *(Gỡ vấn đề ③ và ⑤)*

### Nhóm D — Kiểm soát rủi ro

- **Cổng kiểm tra giữa các đợt**: đợt sau không tự chạy khi đợt trước chưa chốt sổ.
- **Điều chỉnh quy mô đợt** để kiểm soát mức độ ảnh hưởng — bắt đầu nhỏ, nâng dần khi ổn định.
- **Công tắc dừng khẩn cấp** ở hai mức: dừng một đợt, hoặc dừng toàn bộ chi trả tự động.
- **Cảnh báo tự động**, mỗi cảnh báo có người chịu trách nhiệm xử lý. *(Gỡ vấn đề ⑥)*

### Nhóm E — Đối soát

Ba lớp, ba câu hỏi, ba bộ phận chịu trách nhiệm:

| Lớp | Câu hỏi | Chủ sở hữu |
| --- | --- | --- |
| Nội bộ | Sổ chi trả có khớp số dư khách hàng không? | Vận hành |
| Với AT-Core | Sổ của mình có khớp sổ đối tác không? | Kế toán |
| Với ngân hàng | Tiền rời tài khoản có khớp tổng đã chi không? | Kế toán |

Kèm báo cáo định kỳ và cơ chế xử lý khoản lệch. *(Gỡ vấn đề ④)*

### Nhóm F — Phân quyền và truy vết

- **Phân quyền theo từng bước**: tạo đợt, duyệt, chạy, chốt sổ, xử lý ngoại lệ.
- **Nguyên tắc hai người** cho thao tác đụng tiền: người duyệt khác người tạo.
- **Nhật ký đầy đủ**: ai thao tác, lúc nào, trên khoản nào, đổi từ gì sang gì, **dựa trên bằng chứng
  nào**. *(Gỡ vấn đề ⑤)*

## 3.4 Thứ tự triển khai

Bốn giai đoạn, mỗi giai đoạn là một mốc có thể tuyên bố đạt được.

| Giai đoạn | Đạt khi | Gồm |
| --- | --- | --- |
| **1 · An toàn để chi** | Hệ thống không thể tạo khoản chi thứ hai cho cùng một nghĩa vụ khi chưa biết khoản thứ nhất đã đi hay chưa | Nhóm A, cộng siết lại các đường chi tiền chưa có kiểm soát |
| **2 · An toàn để vận hành** | Đội vận hành xử lý được phần lớn tình huống mà không cần kỹ sư | Nhóm B, C |
| **3 · An toàn để chạy tiếp** | Một sự cố ở đợt này không lan sang đợt sau | Nhóm D, cộng đối soát nội bộ |
| **4 · An toàn để mở rộng** | MSHT tự chứng minh được tiền đã đi đúng, bằng số liệu | Nhóm F, cộng hai lớp đối soát còn lại |

> **Giai đoạn 1 là quan trọng nhất.** Hoàn thành giai đoạn này nghĩa là sự cố vừa rồi **không lặp lại
> được nữa**, kể cả khi các giai đoạn sau chưa xong.

### Ba luồng chạy song song

Thứ tự trên không phải một đường thẳng:

- **Luồng phát triển** đi theo bốn giai đoạn.
- **Luồng phối hợp AT-Core** bắt đầu **ngay từ ngày đầu** — thời gian phản hồi của bên thứ ba dài
  nhất trong toàn bộ kế hoạch.
- **Luồng vận hành** cũng bắt đầu ngay: quy trình tạm thời, kịch bản trả lời khách hàng, danh sách
  theo dõi thủ công — để đội vận hành có công cụ dùng trong lúc chờ hệ thống.

---

# PHẦN IV — NHỮNG ĐIỂM CẦN AT-CORE HỖ TRỢ

Sau khi rà soát tài liệu API của AT-Core, **phần lớn năng lực cần thiết đã có sẵn** — vấn đề là phía
MSHT chưa sử dụng. Bốn việc dưới đây **không cần AT-Core làm gì thêm**:

| Năng lực | Tình trạng |
| --- | --- |
| Chống trùng khoản chi | ✅ Đã có. MSHT điều chỉnh cách sinh mã để kích hoạt |
| Kiểm tra số dư tài khoản nguồn | ✅ Đã có. MSHT sẽ bắt đầu sử dụng |
| Chi trả theo lô | ✅ Đã có. MSHT sẽ chuyển sang dùng |
| Kiểm tra tài khoản nhận và điều khoản khách hàng | ✅ Đã có. MSHT bổ sung vào quy trình |

**Ba điểm thật sự cần AT-Core phối hợp:**

## 4.1 Truy vấn kết quả giao dịch theo khoảng thời gian — *ưu tiên cao nhất*

**Cần gì:** lấy được danh sách giao dịch trong một khoảng thời gian do MSHT chỉ định, kèm mã giao
dịch, số tiền, trạng thái, thời điểm.

**Vì sao:** hiện MSHT chỉ tra cứu được từng giao dịch đã biết mã. Đủ để kiểm tra một trường hợp cụ
thể, nhưng **không đủ để đối soát cả một đợt** — và không phát hiện được giao dịch bất thường mà
MSHT không biết là có.

**Nếu không có:** lớp đối soát với AT-Core (giai đoạn 4) không triển khai được. Ba giai đoạn đầu vẫn
chạy bình thường.

**Đề xuất:** API hoặc file định kỳ đều được, sẵn sàng trước giờ chốt sổ hằng ngày.

## 4.2 Làm rõ hợp đồng thông báo kết quả

**Cần gì:** thống nhất bằng văn bản về chính sách gửi lại khi MSHT chưa xác nhận, cách xác thực
nguồn gốc thông báo, và phản hồi nào có nghĩa là đã nhận thành công.

**Vì sao:** tài liệu API hiện tại mô tả các lệnh gọi chủ động, chưa mô tả kênh thông báo ngược. Thiếu
thống nhất khiến hai bên có thể hiểu khác nhau về việc một thông báo đã được xử lý hay chưa.

## 4.3 Thủ tục tra soát và xử lý khoản chi sai

**Cần gì:** xác định có thủ tục thu hồi một khoản chi sai hay không, ai khởi tạo, thời gian xử lý,
và đầu mối liên hệ khi có sự cố kèm thời hạn phản hồi.

**Vì sao:** đây là **câu hỏi nghiệp vụ, không phải kỹ thuật**. Nếu câu trả lời là không thu hồi được,
khẩu vị rủi ro của cả hệ thống thay đổi và trọng số phải dồn hoàn toàn về phòng ngừa.

## 4.4 Mong muốn thêm — cổng tra cứu cho đội vận hành

Hiện mọi tra cứu sang AT-Core đều phải đi qua hệ thống, tức là qua kỹ sư. Một cổng tra cứu dành cho
người vận hành — tra giao dịch, xem trạng thái, tải file đối soát, xem tình trạng dịch vụ — sẽ giảm
đáng kể phụ thuộc kỹ thuật ở cả hai phía.

---

# PHẦN V — KẾT QUẢ ĐO ĐƯỢC

| Nhóm | Chỉ số | Mục tiêu |
| --- | --- | --- |
| An toàn tài chính | Số khoản chi trùng đã xác nhận | **0** |
| Độc lập vận hành | Tỉ lệ tình huống xử lý xong không cần kỹ sư | tăng dần đến **95%** |
| Đối soát | Số tiền chưa đối soát | về **0** |
| Khách hàng | Thời gian chờ của khoản chi lâu nhất | trong cam kết |
| Quản trị | Tỉ lệ thao tác đụng tiền có đầy đủ bằng chứng | **100%** |

---

# PHẦN VI — NHỮNG ĐIỀU CẦN ACCESSTRADE QUYẾT

**6.1 — Khi chưa rõ giao dịch đã đi hay chưa, mặc định xử lý thế nào?**
Coi như *đã chi* (an toàn về tiền, khách hàng chờ lâu hơn) hay coi như *chưa chi* (khách nhận nhanh,
doanh nghiệp chịu rủi ro chi trùng)?
**Đề xuất: coi như đã chi** — thiệt hại hai chiều không cân nhau và khả năng thu hồi thấp.

**6.2 — Một khoản chi được phép chờ tối đa bao lâu** trước khi cảnh báo, và trước khi chủ động liên
hệ khách hàng?

**6.3 — Hạn mức rút tiền theo tháng còn hiệu lực không?**
Hiện có hạn mức được công bố trong thông điệp gửi khách nhưng chưa được thực thi trong hệ thống. Cần
thống nhất: khôi phục hạn mức, hay điều chỉnh nội dung công bố.

**6.4 — Mức độ ưu tiên và nguồn lực** cho từng giai đoạn.

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
