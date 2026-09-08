# Những vấn đề cần AT-Core Chi hộ hỗ trợ

> **Trạng thái:** ghi chép nội bộ, ĐANG ĐỂ ĐÓ. Chưa soạn thành văn bản gửi đối tác.
> **Ngày dựng:** 2026-09-08 · dựng từ việc đọc mã nguồn, không phải từ trí nhớ.
> **Bối cảnh:** sự cố chi trùng — kỹ sư thấy lệnh báo lỗi, chi lại, sinh khoản thứ hai.
>
> **Tham chiếu mã nguồn** (repo `msht/cb-mbbank`, nhánh release):
> `withdraw/app/service/withdraw.go` · `withdraw/app/service/withdraw_communication.go` ·
> `withdraw/app/service/withdraw_webhook.go` · `withdraw/internal/nats/handler.go`
>
> **Tham chiếu client đối tác** (repo `msht/cb-b2b`):
> `external/partnerapi/accesstrade/const.go` · `external/partnerapi/accesstrade/access_trade.go`
>
> **Tham chiếu tài liệu:** `MSHT/RASI/test_case_integration_transfer_for_at.md` · `MSHT/RASI/full.md`

---

## Tóm tắt

Bốn việc cần AT-Core Chi hộ. Xếp theo thứ tự nên làm, không theo độ khó.

| # | Việc | Loại | Chặn cái gì |
| --- | --- | --- | --- |
| 2 | **Truy vấn kết quả theo khoảng thời gian** | Yêu cầu bổ sung năng lực | Chốt sổ đợt · phát hiện khoản trùng |
| 1 | Chốt quy tắc chống trùng theo `request_id` | **Câu hỏi đã bỏ ngỏ từ trước go-live** | Làm mọi thứ rẻ đi, không còn chặn |
| 3 | Làm rõ hợp đồng callback | Làm rõ cái đang có | Callback gửi lại đang bị trả lỗi |
| 4 | Đường xử lý sự cố hai chiều | Thoả thuận vận hành | Thu hồi khoản chi sai |

**Việc 1 tốn đúng một email** — gửi trước vì rẻ và vì thời gian chờ đối tác dài.

**Nhưng việc 2 mới là thứ quyết định.** Khi MSHT có danh tính khoản chi ổn định (xem hộp dưới),
`request_id` không đổi qua mọi lần gửi lại, nên việc 1 chuyển từ *chặn* thành *làm rẻ đi*.
Còn việc 2 thì không có gì thay thế được — xem phần "Quan hệ với việc 1".

> ### ⚠️ `request_id` gắn vào KHOẢN CHI, không gắn vào đợt
>
> **Đính chính 2026-09-08.** Bản trước ghi `request_id` sinh từ `(mã đợt, user)`. **Sai.**
>
> Vận hành phải **dời được một lệnh sang đợt khác** khi đợt này không xử lý kịp. Nếu mã gắn vào đợt
> thì dời đợt ⇒ đổi mã ⇒ AT-Core thấy một lệnh chi mới hoàn toàn ⇒ **đúng cái chi trùng đang chữa**.
>
> Mô hình đúng:
>
> ```
> Nghĩa vụ với khách  →  Khoản chi (payout)  →  Lần gửi (attempt)  →  Giao dịch AT-Core
>                             ↑ mã ổn định ở đây
> Đợt  ──chứa nhiều──→  Khoản chi
> ```
>
> - **Khoản chi** mang danh tính tài chính, ổn định suốt đời, **không đổi khi dời đợt**.
> - **Đợt** chỉ là đơn vị thực thi — gom các khoản chi lại để chạy cùng nhau.
> - `request_id` gửi AT-Core = **mã khoản chi**, không phải mã lần gửi.
>   Nếu gắn vào lần gửi thì mỗi lần thử lại là một mã mới — chính là lỗi hôm nay.

---

## Bảng hợp đồng tích hợp

Một bảng để founder nhìn và biết ngay: **cái nào mình tự làm được, cái nào chờ đối tác, cái nào phải
đàm phán thương mại.**

### A · Hợp đồng gửi lệnh

| Hạng mục | Hiện có | Cần đạt | Ai làm | Loại |
| --- | --- | --- | --- | --- |
| Ngữ nghĩa `request_id` | Sinh mới mỗi lần thử | Ổn định theo khoản chi, có tiền tố sản phẩm | **MSHT** | Tự làm |
| Cam kết chống trùng | **Chưa rõ** | Xác nhận bằng văn bản + tự test được | **AT-Core** | Hỏi / đàm phán |
| Hành vi khi gửi lại | Chưa định nghĩa | Cùng mã ⇒ cùng kết quả, không chi thêm | **AT-Core** | Hỏi / đàm phán |

### B · Hợp đồng tra cứu

| Hạng mục | Hiện có | Cần đạt | Ai làm | Loại |
| --- | --- | --- | --- | --- |
| Tra theo `request_id` | ✅ Có, **chưa dùng** | Dùng trước mọi quyết định gửi lại | **MSHT** | Tự làm |
| Đọc `transfer_amount` | ✅ Có, **bỏ qua** | Đọc và đối chiếu số tiền | **MSHT** | Tự làm |
| Truy vấn theo khoảng thời gian | ❌ Không có | Có, đủ để chốt sổ một đợt | **AT-Core** | Đàm phán |
| Thời hạn phản hồi tra cứu | Chưa định nghĩa | Có cam kết | **AT-Core** | Đàm phán |
| **Cổng tra cứu cho người vận hành** | ❌ Không có, **chưa từng hỏi** | Vận hành tự tra, không qua kỹ sư | **AT-Core** | Đàm phán |
| Trang tình trạng dịch vụ | ❌ Không có | Biết đối tác đang sự cố mà không phải đoán | **AT-Core** | Đàm phán |

### C · Hợp đồng callback

| Hạng mục | Hiện có | Cần đạt | Ai làm | Loại |
| --- | --- | --- | --- | --- |
| Bộ nhận idempotent | ❌ Trả lỗi `006` khi đã xử lý | Trả thành công | **MSHT** | Tự làm — **lỗi của mình** |
| Chính sách gửi lại | Chưa rõ | Số lần, giãn cách, điều kiện dừng | **AT-Core** | Hỏi |
| Chữ ký | **Chưa xác minh** | Có ký, hoặc xác nhận là không | Cả hai | Kiểm tra rồi mới quyết |
| Số tiền trong payload | ❌ Không có | **Không xin** — dùng tra cứu sau callback | **MSHT** | Tự làm |

### D · Hợp đồng sự cố

| Hạng mục | Hiện có | Cần đạt | Ai làm | Loại |
| --- | --- | --- | --- | --- |
| Đầu mối và kênh | ❌ Không có | Đầu mối hai bên, kênh chính thức, có mã theo dõi | Cả hai | Đàm phán |
| Thời hạn phản hồi | ❌ Không có | Có cam kết theo mức nghiêm trọng | Cả hai | Đàm phán |
| **Thủ tục thu hồi khoản chi sai** | ❌ Không có | Xác định **có tồn tại hay không** | **AT-Core** | **Quyết định nghiệp vụ** |
| Lịch bảo trì báo trước | ❌ Không có | Báo trước, tránh giờ chạy đợt | **AT-Core** | Đàm phán |

### Nền — phải chốt trước mọi thứ

| Hạng mục | Hiện có | Cần đạt | Ai làm | Loại |
| --- | --- | --- | --- | --- |
| **Mô hình thanh toán** — nạp trước hay quyết toán sau kỳ | **Không ai biết** | Chốt rõ | MSHT (hợp đồng + kế toán) | **Câu hỏi số 0** |
| Bản `api_gateway.md` của AT-Core | **Không có trong workspace** | Tìm lại bản mới nhất | MSHT | Tự làm |

> 🔴 Hai dòng cuối chặn phần còn lại. Không biết mô hình thanh toán thì không biết nên xin "số dư"
> hay "bảng kê quyết toán". Không có tài liệu API thì có thể đang đi hỏi thứ đã có sẵn đáp án.

### Dòng đáng chú ý nhất

**"Thủ tục thu hồi khoản chi sai"** không phải câu hỏi kỹ thuật — nó là **quyết định nghiệp vụ**.
Nếu câu trả lời là *"không thu hồi được"* thì **chi trùng ≈ mất trắng**, và toàn bộ khẩu vị rủi ro
của hệ thống thay đổi: mọi trọng số dồn về phòng ngừa, và quyết định **D1** gần như tự trả lời.

Vì vậy câu này nên hỏi **sớm**, cùng lúc với câu chống trùng.

---

## Phần 0 — Những gì KHÔNG cần AT-Core

Ghi ra để không lẫn vào văn bản gửi đối tác. Ba việc dưới đây tưởng là thiếu năng lực tích hợp,
thực ra là **mình chưa dùng hết thứ đã có**.

| Tưởng thiếu | Thực tế | Việc phải làm |
| --- | --- | --- |
| Không đối chiếu được số tiền đối tác đã chi | `txn-inquiry` **có** trả `transfer_amount`. Code chỉ đọc `TransferStatus` và `RefTxnID`, bỏ qua trường số tiền | Sửa code MSHT |
| Không tra được lệnh khi chưa có mã tham chiếu | `txn-inquiry` nhận **cả ba** định danh: `request_id`, `txn_id`, `ref_txn_id` | Sửa code MSHT |
| Không kiểm tra được tài khoản người nhận | Đã có `bank/account/info/check` và `bank/account/legal/check`, luồng withdraw không gọi | Sửa code MSHT |

Bề mặt API AT-Core có **7 endpoint**, luồng chi trả MSHT dùng **3**. Xem phụ lục A.

---

## Việc 1 — Chốt quy tắc chống trùng theo `request_id`

### Đây không phải phát hiện mới

Chính đội mình đã ghi câu hỏi này ra **trước khi lên production**, trong
`MSHT/RASI/test_case_integration_transfer_for_at.md` mục 9, điểm 2:

> *"**Idempotency của refNumber/RequestID**: `RequestID = w.ClientMessageID` (ID withdraw).
> Nên có test partner nhận trùng RequestID (retry) không tạo giao dịch kép — **cần partner/mock hỗ trợ**."*

Câu này được viết ra, đánh dấu *"cần partner hỗ trợ"*, rồi không ai đóng. Sự cố chi trùng xảy ra
đúng ở chỗ đó.

### Vì sao nó quyết định mọi thứ còn lại

`RequestID` gửi sang AT-Core hiện là `_id` của document withdraw
(`withdraw.go` — `clientMsgID = w.ID.Hex()`, rồi `withdraw_communication.go` — `RequestID: w.ClientMessageID`).
Mỗi lần thử lại tạo một document mới ⇒ một `request_id` mới ⇒ **đối tác nhìn thấy hai lệnh chi
độc lập và đều hợp lệ**.

### Ba câu cần trả lời bằng văn bản

1. Khi nhận `fund-transfer` với `request_id` **đã dùng trước đó** — AT-Core trả lại kết quả của
   giao dịch cũ, hay tạo một giao dịch mới?
2. Nếu có chống trùng: theo `request_id` hay `txn_id`? Cửa sổ thời gian bao lâu (24h? vĩnh viễn?)
3. Cho MSHT một môi trường test để **tự chứng minh** điều đó. Không nhận trả lời miệng.

### Hai nhánh kết quả

| Nếu AT-Core trả lời | Thì |
| --- | --- |
| **Có** chống trùng theo `request_id` | MSHT chỉ cần dùng lại đúng mã cũ khi gửi lại. Vấn đề gốc gần như xong, không cần đối tác làm gì thêm |
| **Không** | Thành yêu cầu thay đổi có trọng lượng thật, phải đưa vào lịch của đối tác. Trong lúc chờ, MSHT phải tự chặn ở đầu mình |

---

## Việc 2 — Kết quả theo khoảng thời gian, để chốt sổ từng đợt

> **Cập nhật 2026-09-08 (founder):** chi trả MSHT là chi **theo đợt**. Yêu cầu này vì thế hẹp hơn
> "sao kê kỳ" chung chung, và dễ được chấp thuận hơn: mình chỉ cần **kết quả của một khoảng thời
> gian do mình chỉ định** — đúng khoảng của một đợt.

### Cần gì

- **Truy vấn kết quả theo khoảng thời gian**: mọi giao dịch trong khoảng `[từ, đến]` do MSHT chỉ định,
  mỗi dòng có `request_id`, `txn_id`, `ref_txn_id`, số tiền, trạng thái, thời điểm.
  API hoặc file đều được.
- **Tổng đã chi trong khoảng đó** — để so với tổng của đợt bên mình.
- (Mong muốn thêm) **Số dư tài khoản chi hộ**.

### Vì sao cần, nói theo nhịp vận hành

Mô hình đích: **đợt sau không mở khi đợt trước chưa chốt sổ**. Ví dụ đợt chạy 7h sáng thì 3h sáng
chốt kết quả đợt hôm trước. Muốn chốt được thì phải hỏi được AT-Core *"trong khoảng thời gian đó,
bên anh đã chi những gì"* — chứ không phải tra từng lệnh một.

Đây là thứ biến đối soát từ **một báo cáo không ai đọc** thành **cổng mở đợt kế tiếp**.

### Vì sao không thay thế được bằng `txn-inquiry`

Hiện MSHT **chỉ hỏi được về giao dịch mà mình đã biết là có** — `txn-inquiry` tra theo mã.
Không có endpoint nào trả về danh sách.

Hệ quả: khi một khoản trùng sinh ra dưới `request_id` mới, **cả hai lệnh đều tra ra "thành công"
và đều hợp lệ**. Không câu hỏi nào MSHT đặt được cho AT-Core mà câu trả lời hé lộ rằng hai lệnh đó
lẽ ra là một.

### Quan hệ với việc 1

Khi `request_id` gắn vào **khoản chi** (không phải đợt, không phải lần gửi), nó **ổn định qua mọi
lần gửi lại** — không còn phụ thuộc câu trả lời của việc 1 để làm đúng ở đầu mình.

Lúc đó truy vấn theo khoảng thời gian còn gánh thêm một vai: **phát hiện hai giao dịch cùng
`request_id`**. Nghĩa là kể cả khi AT-Core *không* chống trùng, MSHT vẫn tự nhìn ra được khoản trùng.

⇒ Sau khi có mô hình đợt, **việc 2 quan trọng hơn việc 1**. Việc 1 làm mọi thứ rẻ đi; việc 2 là thứ
quyết định mình có mắt hay không.

### Ghi chú

`bank/accounts` (`GetBankAccounts`) trả về `[]AccountInfo` — chỉ tên/số tài khoản/mã ngân hàng,
**không có số dư**. Nên số dư đúng là chưa có, không phải chưa gọi.

---

## Việc 3 — Làm rõ hợp đồng callback

### Cái đang hỏng âm thầm

Payload callback hiện chỉ mang ba trường (`cb-b2b` — `communication/pkg/api/model/webhook.go`,
struct `ATTransferCallback`):

```
ref_txn_id · transfer_status · txn_id
```

**Không có số tiền.**

Và phía nhận của MSHT (`withdraw/app/service/withdraw_webhook.go` — `WithdrawUpdateStatusFromWebhook`)
trả về mã lỗi `006` *"Transaction status not pending"* khi lệnh đã rời trạng thái chờ.

⇒ Nếu AT-Core gửi lại callback vì không nhận được xác nhận, họ nhận về **một lỗi**. Họ không có cách
nào phân biệt *"MSHT đã xử lý rồi"* với *"MSHT đang hỏng"*.

### Cần chốt

| Điểm | Câu hỏi |
| --- | --- |
| Gửi lại | Bao nhiêu lần, cách nhau bao lâu, dừng khi nào? |
| Xác nhận | Mã trả về nào nghĩa là "đã nhận, đừng gửi nữa"? Mã nào nghĩa là "gửi lại đi"? |
| Chữ ký | Callback có ký không? **Chưa xác minh được** — cần đọc thêm phần nhận HTTP ở communication/gateway. Nếu không ký thì ai biết URL cũng đổi được trạng thái một lệnh chi |
| Số tiền | Thêm `transfer_amount` vào payload để đối chiếu ngay tại chỗ |

---

## Việc 4 — Đường xử lý sự cố hai chiều

Hiện **trống hoàn toàn**. Chưa ai hỏi AT-Core cần gì ở MSHT khi có sự cố, và ngược lại.

Cần thoả thuận:

- Đầu mối hai bên và kênh chính thức (không phải tin nhắn cá nhân).
- Thời hạn phản hồi khi MSHT hỏi về một lệnh nghi ngờ.
- AT-Core chủ động báo MSHT trong những trường hợp nào (sự cố bên họ, bất thường họ phát hiện).
- **Thủ tục thu hồi một khoản chi sai** — câu quan trọng nhất về mặt tiền:
  đòi lại được không · bằng cách nào · trong bao lâu · ai chịu chi phí.

Nếu chi trùng mà không có đường đòi lại, thì mọi khoản trùng đều là mất trắng — và điều đó thay đổi
hoàn toàn mức độ ưu tiên của việc 1 và 2.

---

## Lập luận nên mang theo

Chặng ngay **trước** chi trả — job thả tiền sau 60 ngày — **đã làm chống trùng đúng**:
collection `cash-transfer-tracking` có unique index trên `transactionId`, insert bỏ qua trùng
(`MSHT/RASI/full.md`, dòng 152).

Cùng một pipeline, cùng một đội. Chặng 04 chống trùng. Chặng 05 — chặng duy nhất tiêu tiền thật —
thì không.

Và cùng tài liệu đó, dòng 495, ghi rằng bước *"reconcile toàn bộ user cuối ngày"* **có trong PRD
nhưng không được làm**.

⇒ Cả hai thứ đang gây mất tiền đều **từng được viết ra và bị bỏ qua**, không phải chưa ai nghĩ tới.
Đây là sự thiếu nhất quán, không phải giới hạn năng lực — và là lập luận để đóng dứt điểm lần này
thay vì lại ghi vào tài liệu rồi để đó.

---

## Phụ lục A — Bề mặt API AT-Core

Từ `cb-b2b/external/partnerapi/accesstrade/const.go`.

| Endpoint | Hàm client | Luồng chi trả MSHT có dùng? |
| --- | --- | --- |
| `/v1.0/partner/fund-transfer` | `MakeTransfer` | ✅ |
| `/v1.0/partner/txn-inquiry` | `QueryTransactionStatus` | ✅ (bỏ qua trường `transfer_amount`) |
| `/v1.0/partner/bank/account/info` | `QueryBeneficiaryAcc` | ✅ |
| `/v1.0/partner/bank/account/info/check` | `CheckAccNumber` | ❌ |
| `/v1.0/partner/bank/account/legal/check` | `CheckAccountLegal` | ❌ |
| `/v1.0/partner/bank/find` | *(chưa có hàm)* | ❌ |
| `/v1.0/partner/bank/accounts` | `GetBankAccounts` | ❌ — và không trả số dư |
| *(không tồn tại)* | — | 🔴 **Không có endpoint trả danh sách giao dịch theo kỳ** |

---

## Phụ lục B — Một điểm lệch giữa tài liệu và mã nguồn

`MSHT/RASI/test_case_integration_transfer_for_at.md` mô tả mapping trạng thái:

> `CANCEL` / `FAILED` → `rejected`, **có** revert cash

Mã nguồn hiện tại **không còn như vậy**: cả `CANCEL` và `FAILED` đều map về `pending`, không revert
(`withdraw_communication.go` — bảng `atStatusMapping`; đổi ở commit *"feat: pending all transfer failed"*).

Hệ quả: lệnh AT-Core báo hỏng **không bao giờ tự kết thúc** trong hệ MSHT — job đối soát tra ra
`FAILED`, quy về `pending`, rồi bỏ qua, lặp vô hạn.

Cần thống nhất lại tài liệu với mã nguồn **trước khi** mang bảng mapping này ra nói chuyện với đối tác.

---

## Cách kiểm chứng lại

Xác nhận `txn-inquiry` có trả số tiền:

```bash
grep -n "TransferAmount" msht/cb-b2b/external/partnerapi/accesstrade/access_trade.go
```

Xác nhận luồng chi trả bỏ qua trường số tiền:

```bash
grep -rn "res.Data" msht/cb-mbbank/withdraw/app/service/withdraw_webhook.go
```

Liệt kê toàn bộ endpoint AT-Core:

```bash
cat msht/cb-b2b/external/partnerapi/accesstrade/const.go
```

Xem lại câu hỏi idempotency đã bỏ ngỏ:

```bash
sed -n '190,200p' accesstrade-projects/accesstrade-docs/MSHT/RASI/test_case_integration_transfer_for_at.md
```

*(Ba lệnh đầu chạy từ `~/workspaces/diso`; lệnh cuối cũng vậy.)*
