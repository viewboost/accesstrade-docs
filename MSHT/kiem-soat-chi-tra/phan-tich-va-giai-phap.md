# Kiểm soát chi trả MSHT — phân tích và giải pháp

> **Trạng thái:** phân tích nội bộ, chờ founder chốt các quyết định ở mục 4.
> **Ngày:** 2026-09-08 · **Vai trò soạn:** Product Owner
> **Bối cảnh:** sự cố chi trùng — kỹ sư thấy lệnh báo lỗi, chi lại, sinh khoản thứ hai.
>
> Mọi phát biểu về hành vi hệ thống trong tài liệu này đọc trực tiếp từ mã nguồn nhánh release,
> không từ trí nhớ hay tài liệu cũ.
>
> **Tài liệu đi kèm:** [`mo-hinh-payout-va-tieu-chi-nghiem-thu.md`](./mo-hinh-payout-va-tieu-chi-nghiem-thu.md) ·
> [`van-de-can-at-core-ho-tro.md`](./van-de-can-at-core-ho-tro.md) ·
> [`checklist-dev-truoc-khi-lam-viec-at-core.md`](./checklist-dev-truoc-khi-lam-viec-at-core.md) ·
> [`cong-cu-cho-van-hanh-chi-tra.md`](./cong-cu-cho-van-hanh-chi-tra.md)

---

## 0. Tóm tắt cho lãnh đạo

**Đây không phải một dự án "sửa lỗi chi trùng".** Nó là việc dựng **hệ kiểm soát chi trả** cho MSHT.

| | |
| --- | --- |
| **Vấn đề** | MSHT có thể chi cùng một nghĩa vụ nhiều lần, khi kết quả của lần chi trước không rõ. |
| **Tác động** | Mất tiền mặt · khách nhận thông tin sai · mọi ca bất thường đều phải qua kỹ sư. |
| **Nguyên nhân gốc** | Khoản chi không có danh tính ổn định · trạng thái trong hệ không phản ánh thực tế giao dịch · không có đối soát và không có cổng chặn giữa các đợt. |
| **Đề xuất** | Dựng lớp kiểm soát chi trả: danh tính khoản chi · đợt · đôi mắt cho vận hành · thao tác có bằng chứng · đối soát · phân quyền. |
| **Kết quả kỳ vọng** | Chi trùng = 0 · số tiền chưa đối soát luôn nhìn thấy được · đợt sau không chạy khi đợt trước còn treo · sự cố vận hành không cần kỹ sư. |

### Bốn cổng phát hành

Đây là cách founder theo dõi tiến độ: **"đang ở cổng nào"**. Đội làm việc theo thứ tự phụ thuộc
UT0–UT6 ở mục 3 — cổng là lát cắt nghiệp vụ chồng lên đó, không phải cách chia thứ hai.

| Cổng | Qua được khi | Mốc | Ý nghĩa |
| --- | --- | --- | --- |
| **G1 · An toàn để GỬI** | Danh tính khoản chi ổn định · một nghĩa vụ một khoản đang hoạt động · không còn cửa chi tiền vô chủ · trạng thái chưa rõ không gửi lại được | UT0, UT1 | **Không tạo thêm khoản chi thứ hai nữa** |
| **G2 · An toàn để VẬN HÀNH** | Tra được AT-Core · có bằng chứng · có trạng thái chưa rõ · dời/gác được · thông báo khách đúng | UT2 | Vận hành xử lý được ca thường mà không cần kỹ sư |
| **G3 · An toàn để CHẠY TIẾP** | Đợt có chốt sổ · cổng chặn đợt sau · đối soát lớp 1 · cảnh báo · **công tắc dừng toàn hệ** | UT3 | Một sự cố không lan sang đợt kế |
| **G4 · An toàn để MỞ RỘNG** | Kênh chi tay · tách vai duyệt · audit đầy đủ · đối soát lớp 2 · bộ thước đo | UT4, UT5, UT6 | Chứng minh được tiền đã đi đúng |

> **G1 là cổng chặn máu.** Qua được G1 nghĩa là sự cố vừa rồi không lặp lại được nữa, kể cả khi mọi
> thứ khác chưa xong.

---

## 1. Bối cảnh hiện trạng

### 1.1 Tiền đi qua ba bên, không phải hai

MSHT là tính năng mua sắm hoàn tiền trong ứng dụng MBBank. Khách mua sắm qua nhãn hàng liên kết,
tiền hoàn tích lại, rồi chảy về tài khoản ngân hàng của họ.

**MSHT không chi thẳng qua ngân hàng.** Chuỗi thật:

```
Service chi trả (mình) → Lớp trung chuyển (mình) → AT-Core Chi hộ → Ngân hàng → Khách hàng
```

Bốn lần chuyển tay, mỗi lần đều đứt được. Từ đầu chuỗi nhìn xuống, **mọi kiểu đứt hiện ra giống hệt
nhau**: cùng một thông báo lỗi, cùng một trạng thái.

Hệ quả về đối soát: **đối tác đối soát của MSHT là AT-Core Chi hộ, không phải ngân hàng.**
Câu "tiền đã đi chưa" hỏi AT-Core. Câu "tiền có về đúng tài khoản khách không" mới hỏi tới ngân hàng.

### 1.2 Bước ngoặt: đã bỏ nút "Rút tiền" của khách

Từ 30/07/2026 sản phẩm chuyển sang tự động (tính năng RASI — tiền hoàn tự chuyển về Ví tiết kiệm
tiền lẻ). Đường tạo lệnh rút thủ công **chỉ còn bật ở môi trường phát triển**
(`withdraw/app/route/withdraw.go` — route `POST ""` nằm trong nhánh `if IsDev`).

Ở production, khách hàng **không còn cách nào tự khởi tạo một lệnh rút**. Một tác vụ chạy 7h sáng
mỗi ngày quét toàn bộ người đủ điều kiện và tự chi.

Về trải nghiệm đây là nâng cấp tốt. Về kiểm soát, nó lấy đi ba thứ cùng lúc mà chưa có gì thay:

| Mất gì | Hệ quả |
| --- | --- |
| Mốc đối chiếu "ý định" | Trước đây mỗi lệnh ứng với một lần khách bấm nút — sự kiện có thật, không nhân đôi được. Giờ không còn mốc nào để nói "hai lệnh này là cùng một ý định" |
| Người phát hiện lỗi sớm nhất | Khách từng là lớp kiểm tra đầu tiên. Giờ họ không biết hôm nay hệ thống có chi cho mình không |
| Giới hạn tự nhiên về tần suất | Một người bấm vài lần/tháng. Một tác vụ chi cho cả tập khách mỗi ngày — lỗi không còn ảnh hưởng một người mà cả mẻ |

### 1.3 Có bốn cửa chi tiền

| Cửa | Ai dùng | Kiểm soát truy cập | Ghi ai bấm |
| --- | --- | --- | --- |
| Tác vụ tự động 7h sáng | Máy | Nội bộ | Log hệ thống |
| `POST /api/user/sandbox/trigger-auto-withdraw-with-user-ids` | Kỹ sư | Một mã khoá tĩnh | **Không** |
| `POST /api/withdraw/batch-transfer` (upload Excel) | Vận hành / kỹ sư | Basic auth dùng chung | **Không** |
| `PUT /api/withdraw/migration/withdraw/:id/approve` | Kỹ sư | **Không có** | **Không** |

Cửa thứ hai nằm trong nhóm đường dẫn tên `sandbox` nhưng **đăng ký trước** câu `if IsRelease { return }`
nên sống ở production (`user/app/route/sanbox.go`). Cửa thứ tư tên là *approve* — nghe như duyệt giấy
tờ, việc nó làm là đẩy tiền ra khỏi tài khoản công ty, và không cần đăng nhập.

### 1.4 Đợt đã có tên, chưa có hồ sơ

Chi trả MSHT **thực chất đã là chi theo đợt** — mỗi lần chạy 7h sáng là một đợt. Nhưng đợt đó
không tồn tại trong dữ liệu:

- `WithdrawBSON` có 15 trường, **không trường nào là mã đợt** (`withdraw/internal/model/withdraw.go`).
- Service withdraw dùng đúng 4 collection: `withdraw`, `transfers`, `user-stats`,
  `beneficiary-accounts`. **Không có collection nào cho đợt.**

Cái duy nhất gom một lần chạy lại là `trace_id`: `AutoWithdrawTick` sinh **một** trace cho cả run
rồi đẩy theo từng user sang service withdraw. Bình luận trong code ghi rõ mục đích — *"để cả run nối
được log với nhau"*.

⇒ **Đợt sống trong hệ thống log, chết ở cửa cơ sở dữ liệu.** Muốn lấy "đợt hôm qua" chỉ còn cách
suy ra từ `mode: auto` cộng khoảng `createdAt`.

**Hệ quả nặng nhất:** tác vụ 7h sáng và nút bấm tay của kỹ sư đi **chung một hàm**
(`autoWithdrawProcessUser`, gọi từ dòng 106 và dòng 218), và hàm đó hardcode `Mode: "auto"`.
Nên lệnh do kỹ sư bấm lại **trông y hệt lệnh tự động 7h sáng** trong cơ sở dữ liệu. Khác nhau duy
nhất là `createdAt`.

Đó là lý do sau sự cố không truy ngược được khoản nào sinh từ đâu — không phải vì mất log, mà vì
**dữ liệu chưa bao giờ ghi lại sự khác biệt đó**.

Cửa Excel còn tệ hơn: `WithdrawBatchTransfer` đếm số thành công/thất bại trong bộ nhớ rồi **vứt đi**.

### 1.5 Ba trạng thái, và trạng thái thứ tư đang thiếu

Một lệnh chi chỉ có: `pending` · `success` · `rejected`. Khách cũng chỉ thấy ba nhãn tương ứng.

Trạng thái thiếu là trạng thái xảy ra thường xuyên nhất khi sự cố:
**"đã gửi sang AT-Core nhưng chưa biết kết quả"**. Hệ thống buộc phải xếp nó vào `pending` — cùng ô
với lệnh chưa gửi đi đâu cả.

### 1.6 Cửa sổ nhìn sang AT-Core

> **Đính chính 2026-09-08.** Bản trước viết dựa trên client Go. Sau khi đọc tài liệu API chính thức
> *([bản `.md`](./at-core-partner-bank-gateway-api.md))*, bảng này phải sửa — **AT-Core có nhiều
> năng lực hơn hẳn những gì MSHT đang dùng.**

AT-Core có **16 endpoint**. Client Go bọc **7**. Luồng chi trả dùng **3**.

| Đã có bên AT-Core, MSHT **chưa dùng** | Thật sự **không có** |
| --- | --- |
| **Chống trùng theo `txn_id`** — trùng trả `400` | **Truy vấn giao dịch theo khoảng thời gian** |
| **Chuyển tiền hàng loạt** `POST /fund-transfers` | Mô tả callback/webhook *(không có trong tài liệu)* |
| **Kiểm tra số dư** `GET /balance` | |
| **Kiểm tra điều khoản TOS** `GET .../legal/check` | |
| Kiểm tra tài khoản nhận `.../account/info/check` | |
| Tính phí `calculate-fee` · thông báo cashback | |

🔴 **Điểm nặng nhất:** *"`txn_id` phải duy nhất theo partner"* — hàng rào chống trùng **đã tồn tại**.
MSHT sinh `txn_id` mới mỗi lần thử lại *(`TxnID = t.ID.Hex()`)* nên chưa bao giờ chạm tới nó.
**Sự cố chi trùng lẽ ra đã bị đối tác chặn.**

Ngoài ra có sẵn **rate limit 5 giây** cho cùng số tài khoản nhận — bắt được lần gửi liên tiếp,
không bắt được lần thử lại sau vài giờ.

`txn-inquiry` **có** trả `transfer_amount` — code MSHT chỉ đọc `TransferStatus` và `RefTxnID`,
bỏ qua trường số tiền. Việc đối chiếu số tiền là **sửa code, không phải đàm phán**.

### 1.7 Ba nhóm người vận hành, không nhóm nào đủ công cụ

| Nhóm | Nhìn | Làm | Kiểm chứng | Để lại dấu |
| --- | --- | --- | --- | --- |
| Vận hành | Chỉ thấy danh sách lệnh, không thấy câu trả lời của AT-Core | Có đúng một nút — nút nguy hiểm nhất | Không | Chỉ ghi người sửa khi đổi qua CRM |
| AT-Core Chi hộ | Không có kênh nào ta mở cho họ | Callback gửi lại lần hai bị trả lỗi `006` | Không | Không |
| Kỹ thuật | Đọc log, nhưng log nói sai | Bốn cửa chi tiền | Tra từng lệnh một | 3/4 cửa không ghi ai bấm |

Hàng đối tác **trống hoàn toàn**. Hàng vận hành **bị đảo ngược**: có quyền GHI mà không có quyền ĐỌC.

---

## 2. Vấn đề

Mười vấn đề, gom theo bốn thứ đang thiếu.

### Thiếu danh tính

**P1 — Không tồn tại khái niệm "một lệnh chi".**
`request_id` gửi sang AT-Core là `_id` của document withdraw, sinh mới mỗi lần. Thử lại ⇒ mã mới ⇒
đối tác thấy hai lệnh độc lập và đều hợp lệ. **Thao tác "gửi lại" không tồn tại trong hệ thống** —
chỉ có "tạo mới".

**P2 — Đợt không có hồ sơ.** (mục 1.4)
Không có đơn vị nào để chốt sổ, để chặn, để phân quyền, hay để đối soát theo lô.

### Thiếu mắt

**P3 — Không phân biệt "chưa chi" với "không biết đã chi chưa".**
Khi kết nối gián đoạn, phần lõi xử lý đúng — giữ tiền đã trừ, đánh dấu chưa rõ kết quả. Nhưng thông
tin đó không tới người đọc: trên nhật ký, tình huống "có thể đã chi rồi" hiện ra bằng một chữ
**thất bại**. Kỹ sư đọc chữ đó và kết luận điều hợp lý duy nhất có thể kết luận.

**P4 — Không tự phát hiện được khoản chi trùng.**
`txn-inquiry` chỉ tra được mã mình đã biết. Ghép với P1: khoản trùng sinh dưới mã mới thì **cả hai
lệnh đều tra ra "thành công" và đều hợp lệ**. Kênh xác minh phụ hiện có đọc lại nhật ký của chính
lớp trung chuyển của mình — **kiểm chứng người đưa thư, không kiểm chứng đồng tiền**.

**P5 — Không lớp đối soát nào đang chạy.**
Ba câu hỏi, ba chủ sở hữu, không câu nào được hỏi: nội bộ (sổ ↔ số dư) · với AT-Core (sổ ↔ sổ đối
tác) · dòng tiền thật (sao kê ngân hàng). Tài liệu `RASI/full.md` dòng 495 ghi rằng bước
*"reconcile toàn bộ user cuối ngày"* **có trong PRD nhưng không được làm**.

### Thiếu phanh

**P6 — Lệnh hỏng không bao giờ tự kết thúc.**
`atStatusMapping` map cả `FAILED` lẫn `CANCEL` về `pending`. Job đối soát tra ra `FAILED`, quy về
`pending`, rồi bỏ qua — vô hạn. Tiền khách treo vĩnh viễn, và **cách duy nhất thoát ra là người vào
bấm tay**. Đây là gốc của câu "muốn làm gì cũng phải hỏi kỹ sư" — hệ thống đẩy việc đó cho họ.

**P7 — Không có cổng chặn giữa các đợt.**
Đợt 7h sáng chạy mỗi ngày bất kể đợt hôm trước đã chốt sổ hay chưa. Một sự cố không bị chặn lại ở
một đợt mà tự do lặp sang đợt sau.

**P8 — Quyền hoàn tiền không đòi bằng chứng.**
Nhân viên chuyển một lệnh treo sang `rejected` ⇒ tiền trả lại số dư khách. Hệ thống **không hỏi
AT-Core** lệnh đã đi chưa, **không cần người thứ hai**. Nếu AT-Core đã chi thật, thao tác này biến
một khoản thành hai — và đợt hôm sau sẽ chi lại số dư vừa khôi phục.

### Thiếu đường lui

**P9 — Chưa có đường chi tay khi AT-Core hỏng.**
Nếu API đối tác chết, hiện chỉ có hai lựa chọn: để lệnh treo vô hạn, hoặc tắt hẳn luồng rút.
Không có cách nào chi tiền cho khách bằng đường khác rồi nạp kết quả về hệ thống.

⚠️ Và khi làm đường này thì phát sinh một rủi ro mới cần thiết kế từ đầu: **khoản chi tay sẽ không
bao giờ xuất hiện trong sổ AT-Core.** Nếu đối soát lớp 2 không biết loại chúng ra, chúng sẽ bị báo
lệch vĩnh viễn. Ngược lại, nếu chi tay mà **không** ghi lại vào hệ thống, số dư khách không bị trừ
và **đợt kế tiếp sẽ chi cho họ lần nữa**.

**P10 — Không có phân quyền theo bước, không có dấu vết.**
3/4 cửa chi tiền không ghi ai bấm. Không có bảng audit cho thao tác đổi trạng thái. Nên hôm nay
câu trả lời trung thực cho "mức phụ thuộc kỹ sư là bao nhiêu" là **chưa đo được**.

### Ngoài ra: chính sách công bố khác chính sách đang chạy

| Quy tắc | Công bố với khách | Thực tế |
| --- | --- | --- |
| Hạn mức 1,9 triệu/tháng | Có trong bộ thông điệp gửi khách | Phần kiểm bị chú thích lại, **không chạy** |
| Ký hợp đồng điện tử trước khi rút | Có trong bộ thông điệp | Phần kiểm bị chú thích lại, **không chạy** |

Và khách nhận thông báo trái sự thật: khi nhân viên đánh dấu từ chối, khách nhận *"Rút tiền không
thành công"* **trong khi tiền có thể đang nằm trong tài khoản họ**. Các khoản chi qua cửa Excel thì
**không gửi thông báo nào**.

---

## 2B. Sổ rủi ro

Năm rủi ro, tách riêng vì **cách phòng khác nhau** — và vì hai trong số đó đối xứng nhau: siết cái
này quá tay thì cái kia nặng lên.

| Mã | Rủi ro | Nội dung | Mức | Khả năng — căn cứ từ mã nguồn | Gốc |
| --- | --- | --- | --- | --- | --- |
| **A** | **Chi trùng** | Cùng một nghĩa vụ bị trả hai lần | Nghiêm trọng | **Đã xảy ra** — không phải giả định | P1, P2 |
| **B** | **Hoàn tiền sai** | Đã chi thật, hệ tưởng hỏng, hoàn tiền vào số dư → đợt sau chi lại | Nghiêm trọng | **Cao** — một thao tác chuột, không cần bằng chứng, cơ chế còn nguyên | P3, P8 |
| **C** | **Tiền khách kẹt** | Hệ quá thận trọng, khoản chi hợp lệ treo vô hạn | Cao | **Chắc chắn** — `FAILED`/`CANCEL` map về `pending` nghĩa là mọi lệnh hỏng đều kẹt, theo thiết kế | P6 |
| **D** | **Thao tác không thẩm quyền** | Người vận hành đổi trạng thái tiền mà không đủ bằng chứng, không tách vai | Nghiêm trọng | **Không đo được** — 3/4 cửa chi tiền không ghi ai bấm, nên không biết đã xảy ra chưa | P8, P10 |
| **E** | **Lệch âm thầm** | Đợt sau vẫn chạy trong khi lệch của đợt trước chưa ai biết | Nghiêm trọng | **Chắc chắn** — không có lớp đối soát nào đang chạy, nên mọi lệch đều âm thầm theo định nghĩa | P5, P7 |

> Cột "khả năng" không phải ước lượng cảm tính — mỗi ô suy ra từ một sự thật trong mã nguồn. Riêng
> **D là "không đo được"**, và đó chính là lý do ưu tiên 5 (dấu vết) không được cắt bỏ: chưa có dấu
> vết thì rủi ro này mãi mãi không ai biết đang ở mức nào.

> **A và C kéo ngược nhau.** Chặn chặt để tránh chi trùng thì tiền khách kẹt lâu hơn. Đây là chỗ
> founder phải chọn khẩu vị rủi ro — xem quyết định **D1**, và van xả bắt buộc ở mục 3 ưu tiên 0.

### Chính sách theo trạng thái — trạng thái không tự quyết định hành động

Trạng thái nói **hệ đang biết gì**. Nó phải ghép với **bằng chứng** mới ra được **hành động cho phép**.

| Trạng thái khoản chi | Gửi đi | Gửi lại | Hoàn tiền | Dời đợt | Tạm gác |
| --- | :---: | :---: | :---: | :---: | :---: |
| Chưa gửi | ✅ | — | ✅ | ✅ | ✅ |
| Đang xử lý ở đối tác | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Chưa rõ kết quả** | ❌ | ❌ | ❌ | ❌ | ✅ |
| Thành công | ❌ | ❌ | ❌ | ❌ | — |
| Hỏng, **đã xác nhận** | — | ✅ | ✅ | ✅ | ✅ |

🔴 Hàng **"chưa rõ kết quả"** là hàng sinh ra sự cố vừa rồi, và nó **cấm mọi thứ trừ tra soát và tạm
gác**. Không có hàng này trong hệ hiện tại — nó đang bị gộp vào "đang xử lý".

"Hỏng" chỉ mở khoá khi **đã xác nhận** bằng câu trả lời của AT-Core. Hỏng do đoán thì vẫn nằm ở hàng
"chưa rõ".

### Rủi ro → Kiểm soát → Chủ sở hữu → Thước đo

| Rủi ro | Kiểm soát | Làm ở | Chủ sở hữu | Thước đo | Đích |
| --- | --- | --- | --- | --- | --- |
| **A** · Chi trùng | Danh tính khoản chi ổn định · chống trùng ở đối tác · chặn gửi lại khi chưa rõ | Ưu tiên 1, 2 | Sản phẩm + Kỹ thuật | Số khoản chi trùng | **0** |
| **B** · Hoàn tiền sai | Bắt buộc bằng chứng từ AT-Core · người thứ hai duyệt trên ngưỡng | Ưu tiên 2, 5 | Vận hành | Số lần hoàn tiền không có bằng chứng | **0** |
| **C** · Tiền khách kẹt | Trạng thái kết thúc thật · SLA **D2** · van xả tạm gác · leo thang | Ưu tiên 2, 4 | Vận hành | Tuổi khoản treo lâu nhất · số khoản quá SLA | Trong **D2** |
| **D** · Thao tác không thẩm quyền | Tách vai người tạo / người duyệt · audit kèm bằng chứng · cảnh báo mỗi thao tác loại A | Ưu tiên 5 | Vận hành + Sản phẩm | % thao tác loại A có đủ audit | **100%** |
| **E** · Lệch âm thầm | Chốt sổ đợt · cổng chặn đợt sau · đối soát ba lớp | Ưu tiên 3, 6 | Kế toán + Sản phẩm | Số tiền chưa đối soát · thời gian từ lúc lệch tới lúc có người biết | **0** · **< 24h** |

> **A và C kéo ngược nhau, và bảng này cho thấy vì sao chúng phải làm cùng nhau.** Kiểm soát của A
> nằm ở ưu tiên 1–2; van xả của C cũng ở ưu tiên 2. Nếu làm A trước và để C lại sau thì có một giai
> đoạn khách bị kẹt mà không ai gỡ được.

---

## 3. Giải pháp theo thứ tự ưu tiên

Nguyên tắc xếp thứ tự: **cái gì chặn cái khác thì lên trước**, và trong cùng mức thì **gỡ bỏ trước
khi xây thêm**.

### Ưu tiên 0 — Chặn máu · trong tuần · không phụ thuộc gì

Cả ba đều là **xoá đi**, rủi ro gần bằng không:

1. Xoá đường `migration/withdraw/:id/approve` — không xác thực, chi tiền được, và là công cụ một lần
   dùng cho đợt migration đã xong.
2. Đưa `sandbox/trigger-auto-withdraw-with-user-ids` xuống **sau** `if IsRelease` như hai route cùng
   nhóm. Nó đang ở production vì đứng nhầm phía câu lệnh.
3. Chặn tạo lệnh mới khi khách còn lệnh đang treo.

> **Chưa khoá nút đổi trạng thái tay ở bước này.** Khoá bây giờ là đổi rủi ro "chi trùng" lấy rủi ro
> "tiền khách kẹt vô hạn", vì chưa có đường nào khác đóng một lệnh hỏng. Khoá ở ưu tiên 2, cùng lúc
> với việc trao đôi mắt.

### Ưu tiên 1 — Khai sinh danh tính khoản chi, rồi mới tới đợt

Đây là **hòn đá góc**. Bốn thứ ở dưới đều treo vào nó.

> **Đính chính 2026-09-08.** Bản trước viết `request_id` sinh từ `(mã đợt, user)`. Sai — và mâu thuẫn
> với chính yêu cầu "dời lệnh sang đợt khác" trong tài liệu công cụ vận hành. Dời đợt ⇒ đổi mã ⇒
> AT-Core thấy lệnh mới ⇒ đúng cái chi trùng đang chữa.

**Đợt là đơn vị THỰC THI. Khoản chi là đơn vị TIỀN.** Không được trộn hai thứ.

```
Nghĩa vụ với khách  →  Khoản chi  →  Lần gửi  →  Giao dịch AT-Core  →  Giao dịch ngân hàng
                          ↑
                    danh tính tài chính, ổn định suốt đời

Đợt  ──chứa nhiều──→  Khoản chi        (dời khoản chi sang đợt khác KHÔNG đổi danh tính)
```

| Tầng | Vai trò | Đổi khi nào |
| --- | --- | --- |
| **Khoản chi** | Nghĩa vụ trả tiền cho một người, một lần | Không bao giờ |
| **Lần gửi** | Một lượt thử thực thi khoản chi đó | Mỗi lần gửi lại |
| **Đợt** | Tập khoản chi gom lại chạy cùng nhau | Khoản chi dời được giữa các đợt |

**`request_id` gửi AT-Core = mã khoản chi.** Không phải mã lần gửi (mỗi lần thử lại thành mã mới —
chính là lỗi hôm nay), không phải mã đợt (dời đợt là đổi mã).

Việc cần làm:

- Khoản chi thành thực thể có danh tính riêng, sinh từ nghĩa vụ với khách, **ổn định suốt đời**.
- Lần gửi ghi lại từng lượt thử: gửi gì, nhận gì, lúc nào.
- Đợt thành thực thể có hồ sơ: mã, loại (tự động / bù tay / theo danh sách), phạm vi, người tạo,
  thời điểm, **trạng thái vòng đời của chính đợt**.
- Tách hẳn hai thao tác: **tạo khoản chi mới** và **gửi lại khoản chi đã có**.

**Vì sao lên trước mọi thứ khác:**

| Nó gỡ | Bằng cách nào |
| --- | --- |
| P1 | Mã lệnh ổn định — làm đúng ở đầu mình mà **không cần chờ AT-Core trả lời** |
| P2 | Hiển nhiên |
| P7 | Có đơn vị để chặn |
| P9 | Đợt bù tay là một loại đợt, không phải cửa sau |
| P10 | Có các bước thật để gắn quyền vào |

Việc này **nhỏ hơn tưởng**: cơ chế gom một đợt đã có và đã chạy xuyên hai service (`trace_id`).
Chỉ thiếu chỗ đậu và một cái tên có nghĩa nghiệp vụ.

> **Tiền lệ nên xem trước khi thiết kế:** dự án Techcombank trong workspace đã mô hình chi trả theo
> đợt — `techcombank/dashboard/src/hooks/use-transfers.ts` có 9 trạng thái vòng đời và thống kê theo
> từng đợt (tổng lệnh, tổng tiền, tách pending/success/rejected). Không nên vẽ lại từ đầu.

### Ưu tiên 2 — Cho vận hành đôi mắt, rồi mới trả lại tay

Toàn bộ dùng API đã có, không cần đối tác làm gì.

1. **Nút "Tra AT-Core"** cạnh mỗi lệnh treo — gọi `txn-inquiry`, hiện nguyên văn câu trả lời:
   trạng thái, **số tiền**, mã tham chiếu.
2. **Đọc `transfer_amount`** và so với số đã yêu cầu, ở cả luồng chi lẫn luồng đối soát.
3. **Danh sách lệnh treo quá hạn** (cần ngưỡng — quyết định **D2**).
4. **Tách trạng thái thứ tư**: "đã gửi, chưa rõ kết quả" khác hẳn "chưa gửi". Gỡ P3.
5. **Rồi mới mở lại nút đổi trạng thái**, kèm điều kiện: chỉ đổi được sang đúng thứ AT-Core vừa trả
   về. Người bấm không còn phải đoán. Gỡ P8.
6. Mọi cập nhật trạng thái phải kèm **điều kiện trạng thái hiện tại**, để callback và luồng chi
   không ghi đè ngược lên nhau.

Trật tự **mắt trước, tay sau** là điểm đảo ngược so với hiện tại.

### Ưu tiên 3 — Cổng chốt sổ, và chặn đợt kế tiếp

Ghép hai việc thành một cơ chế: **chốt sổ đợt cũ là điều kiện mở cổng đợt mới.**

```
03:00  chốt sổ đợt hôm trước  →  cổng xanh/đỏ  →  07:00  đợt mới chạy (hoặc không)
```

Khoảng 3h → 7h không phải con số tuỳ tiện: nó là **bốn tiếng người thật còn kịp can thiệp** trước
khi tiền đi. Giữ nguyên tính chất đó khi chọn giờ.

Thiết kế cổng phải **phân biệt lỗi lẻ với lỗi hệ thống**:

| Loại | Ví dụ | Cổng |
| --- | --- | --- |
| Lỗi lẻ | 3 lệnh hỏng trong 1.200 | Không chặn — mang sang đợt sau xử lý như ngoại lệ |
| Lỗi hệ thống | Tổng tiền lệch · số lệnh "không rõ kết quả" vọt lên · AT-Core không trả lời | Chặn |

> Nếu cổng đặt quá nhạy nó sẽ luôn đỏ, và người ta sẽ học cách bấm bỏ qua. Chỉ số luôn đỏ là chỉ số
> người ta thôi đọc.

Cộng thêm **giới hạn kích thước đợt** làm núm vặn rủi ro: bắt đầu nhỏ, nâng dần khi ba đợt liên tiếp
xanh, và giữ núm đó lại luôn — khi sự cố, thu nhỏ đợt là lựa chọn thứ ba giữa "chạy bình thường" và
"dừng hẳn".

> Nên vặn **kích thước** trước, không vặn **tần suất**. Kích thước không đổi kỳ vọng của khách (phần
> dư dồn sang đợt kế, khách vẫn nhận trong ngày) và đảo ngược dễ. Tần suất đổi cả kỳ vọng khách lẫn
> nhịp chốt sổ.

Cuối cùng: **đối soát lớp 1** (nội bộ — sổ lệnh ↔ số dư ↔ bút toán) làm được ngay ở bước này, không
phụ thuộc ai.

**Việc rẻ nên làm sớm nhất trong nhóm này — đèn báo khói:**

> Truy vấn hằng ngày: cùng một user, cùng số tiền, hai lệnh `success` cách nhau dưới 48 giờ.

Không phải bằng chứng, chỉ là mùi khói. Nhưng miễn phí, không phụ thuộc ai, và **sẽ bắt được đúng
sự cố vừa rồi**.

### Ưu tiên 4 — Chi tay là một KÊNH, không phải đường lui

> **Cách gọi quan trọng.** Nếu coi chi tay là "ngoại lệ khi đối tác hỏng" thì nó sẽ không có vòng
> đời, không ai đối soát, và trở thành **một hệ thống nằm ngoài hệ thống**. Nó phải là một **kênh
> chi chính thức**, đi qua đúng vòng đời như kênh AT-Core:
>
> ```
> Tạo → Duyệt → Thực thi → Ghi nhận bằng chứng → Đối soát → Đóng
> ```
>
> Khác nhau duy nhất là đối soát ở lớp nào — xem
> [`mo-hinh-payout-va-tieu-chi-nghiem-thu.md`](./mo-hinh-payout-va-tieu-chi-nghiem-thu.md) mục 1.

Tổ chức **đã giải bài này rồi** cho TPBank ngày 04/09/2026 —
xem [`../manual-fulfillment-tpbank/PRD.md`](../manual-fulfillment-tpbank/PRD.md). Khuôn đã chứng minh:

1. Cờ cấu hình `ManualFulfillment` — vẫn nhận yêu cầu, vẫn trừ tiền, **bỏ qua gọi đối tác**.
2. Vận hành tra danh sách cần xử lý, chuyển khoản bằng đường khác.
3. Nộp kết quả về bằng file 2 cột (`request_id`, `result`) qua một API nội bộ riêng.
4. Xử lý đồng bộ, trả báo cáo theo từng dòng.
5. **Idempotent tự nhiên**: dòng nào lệnh đã rời trạng thái chờ thì bỏ qua với lý do "đã xử lý" —
   nộp lại cùng file lần hai vô hại.

**Mượn hình dáng, đừng chép điểm yếu.** Bản TPBank có đúng những điểm mình đang chữa ở MSHT:

| Điểm yếu bản TPBank | MSHT phải làm khác |
| --- | --- |
| Tái dùng `pending`, nên "chưa gửi đi đâu" và "đã gửi chưa rõ kết quả" lại chung một ô | Dùng trạng thái thứ tư của ưu tiên 2 |
| An toàn nhờ job đối soát đang bị comment-out trên production — một sự trùng hợp gánh việc | Ở MSHT job đó là **mã sống**: `cronjob.Init()` đăng ký `WithdrawSyncAllPendingStatus` lịch `0 8,14 * * *`, chỉ gác sau cờ `EnableWorker` (`.env.example` để `true`). Phải loại trừ các lệnh chi tay **tường minh**, không dựa vào việc job đang tắt |
| Hoàn tiền: đổi trạng thái trước, hoàn sau, không giao dịch | Chấp nhận tạm, nhưng ghi vào nợ kỹ thuật |
| Vận hành tự tra Metabase, không có màn | Đã có màn từ ưu tiên 2 |
| Không có thực thể đợt | **Đợt bù tay là một đợt**, có mã, có người duyệt |

**Và một điểm bản TPBank không gặp mà MSHT sẽ gặp:** khoản chi tay không bao giờ xuất hiện trong sổ
AT-Core. Nên ngay từ khi thiết kế, mỗi lệnh phải mang **kênh chi** (`at-core` / `chi tay`) để đối
soát lớp 2 biết loại ra, và để đối soát lớp 3 (sao kê ngân hàng) biết nhận về. Không có trường này
thì các khoản chi tay sẽ bị báo lệch vĩnh viễn.

### Ưu tiên 5 — Phân quyền theo bước, và dấu vết

Có đợt rồi mới có bước thật để gắn quyền:

| Bước | Ai | Ghi chú |
| --- | --- | --- |
| Tạo đợt (kể cả đợt bù) | Vận hành | |
| Duyệt đợt trước khi chạy | Người thứ hai | **Bắt buộc khác người tạo** |
| Chạy | Hệ thống | |
| Chốt sổ | Hệ thống, người xem kết quả | |
| Mở cổng khi cổng đỏ | Cấp cao hơn | **Bắt buộc ghi lý do** — đây là van xả duy nhất, và là chỗ sự cố sau sẽ đi qua |
| Bù cá nhân trong đợt | Vận hành | Trong hạn mức |

**Quy tắc xung đột lợi ích — chặt hơn "người duyệt khác người tạo":**

> Với một thao tác loại A trên **cùng một khoản chi**, ba vai **tạo · duyệt · thực thi** phải do
> **ít nhất hai người khác nhau** đảm nhiệm, và người duyệt **không được là người tạo**.

Không đủ nếu chỉ dựa vào việc hai tài khoản có vai khác nhau trên giao diện — một người giữ hai vai
vẫn tự duyệt được việc mình tạo. Hệ thống phải chặn theo **danh tính người**, không theo vai.

Cùng lúc: **bảng audit** cho mọi thao tác đổi trạng thái — ai · lúc nào · lệnh/đợt nào · từ trạng
thái gì sang gì · **dựa trên bằng chứng nào**.

Bảng này không sửa được đồng nào đã mất, nhưng nó là **dấu vết vật lý** để đo mức phụ thuộc kỹ sư.
Cách đo là hỏi ngược, không dựng sổ tay:

> Có lệnh chi nào **đổi trạng thái mà không có hàng audit của một người vận hành đứng sau** không?

Có ⇒ nó đổi ngoài giao diện ⇒ đó là can thiệp kỹ thuật. Dấu này **tự sinh**, không ai phải nhớ ghi.

### Ưu tiên 6 — Đối soát lớp 2 · phụ thuộc AT-Core

Chặn bởi kết quả đàm phán ở [`van-de-can-at-core-ho-tro.md`](./van-de-can-at-core-ho-tro.md).
Khởi động đàm phán **ngay từ ưu tiên 0** vì thời gian chờ đối tác dài nhất trong cả kế hoạch.

### Đây không phải một đường thẳng

Đánh số 0→6 dễ bị đọc thành "làm xong cái này mới tới cái kia". Sai. Có **ba làn chạy song song**,
và làn đàm phán đối tác **bắt đầu ngay từ ngày đầu** vì thời gian chờ dài nhất:

```
        ┌───── Làn đối tác: đàm phán AT-Core ──────────────────────────┐
        │  bắt đầu NGAY · chỉ ưu tiên 6 thật sự chờ kết quả            │
        └──────────────────────────────────────────────────────────────┘

  UT0 ──► UT1 ──────► UT2 ─────────► UT3
 chặn    danh tính   đôi mắt        cổng chốt sổ
 máu     + đợt         │
                       ├──► UT4 kênh chi tay
                       └──► UT5 phân quyền + dấu vết

        ┌───── Làn vận hành: truy vấn tạm · quy tắc bấm nút ───────────┐
        │  làm trong tuần đầu, không chờ bất kỳ ưu tiên nào            │
        └──────────────────────────────────────────────────────────────┘
```

### Bảng phụ thuộc

| Ưu tiên | Chờ AT-Core? | Chờ đợt (ưu tiên 1)? |
| --- | :---: | :---: |
| 0 — Chặn máu | Không | Không |
| 1 — Khai sinh đợt | Không | — |
| 2 — Đôi mắt cho vận hành | Không | Không (làm song song được) |
| 3 — Cổng chốt sổ | Không | **Có** |
| 4 — Đường lui chi tay | Không | **Có** |
| 5 — Phân quyền & dấu vết | Không | **Có** |
| 6 — Đối soát lớp 2 | **Có** | **Có** |

**Chỉ một hạng mục thật sự chờ đối tác.** Cuộc nói chuyện với AT-Core không được thành lý do để chờ.

---

## 4. Quyết định cần founder chốt

Ghi theo dạng **biên bản quyết định**, không phải danh sách câu hỏi — mỗi mục có lựa chọn, đề xuất
của PO, hệ quả kèm theo, và hạn.

---

### D1 — Khi chưa rõ AT-Core đã chi hay chưa, mặc định là gì?

**Đây là quyết định gốc.** Mọi thứ khác suy ra từ đây.

| | |
| --- | --- |
| **Lựa chọn A** | Coi như **đã chi**. Không hoàn tiền, không chi lại, chờ tra soát. |
| **Lựa chọn B** | Coi như **chưa chi**. Hoàn tiền hoặc chi lại ngay để khách không phải chờ. |
| **PO đề xuất** | **A** |
| **Vì sao** | Thiệt hại hai chiều không cân nhau. Chọn sai theo hướng A: khách chờ thêm, có thể xin lỗi và bù. Chọn sai theo hướng B: mất tiền mặt, và **nhiều khả năng không đòi lại được** — tiền đã vào tài khoản khách tại ngân hàng, bên chi hộ không rút ngược. |
| **Hệ quả phải chấp nhận** | Rủi ro C (tiền khách kẹt) tăng ⇒ **bắt buộc** kèm SLA (D2), van xả tạm gác, và kịch bản trả lời khách. |
| **Hiện trạng** | Hệ đang chọn A ở phần lõi nhưng chọn B ở phần con người đọc log. **Chính mâu thuẫn đó gây ra sự cố.** |
| **Người quyết** | Founder |
| **Hạn** | Trước khi bắt đầu ưu tiên 2 |

---

### D2 — Một khoản chi được phép treo bao lâu?

| | |
| --- | --- |
| **Lựa chọn** | 24h · 48h · 72h · theo loại đợt |
| **PO đề xuất** | 24h để cảnh báo, 72h để leo thang |
| **Vì sao** | D1 chọn A nghĩa là khách phải chờ. Chờ **phải có trần**, nếu không A biến thành "kẹt vô hạn". |
| **Hệ quả** | Là ngưỡng cho cảnh báo, cho danh sách quá hạn, và cho định nghĩa "hỏng" ở D3. |
| **Người quyết** | Founder + vận hành |
| **Hạn** | Cùng D1 |

---

### D3 — Chốt sổ một đợt nghĩa là gì?

| | |
| --- | --- |
| **Lựa chọn A** | Mọi khoản chi phải có kết quả dứt khoát mới coi là chốt. |
| **Lựa chọn B** | Cho phép mang khoản chưa rõ sang đợt sau, vẫn coi là đã chốt, miễn là số lượng dưới ngưỡng. |
| **PO đề xuất** | **B**, kèm trần số lượng và trần tuổi |
| **Vì sao** | A nghe chặt hơn nhưng thực tế sẽ **không bao giờ chốt được** — luôn có vài ca chờ đối tác. Cổng không bao giờ xanh là cổng người ta học cách bỏ qua. |
| **Hệ quả** | Cần định nghĩa "khoản mang sang" và giới hạn số lần được mang. |
| **Người quyết** | Founder |
| **Hạn** | Trước ưu tiên 3 |

---

### D4 — Ngưỡng nào chặn đợt kế tiếp?

| | |
| --- | --- |
| **Lựa chọn** | Theo số tuyệt đối · theo tỉ lệ · theo số tiền lệch · kết hợp |
| **PO đề xuất** | Kết hợp, và **phân biệt lỗi lẻ với lỗi hệ thống** — vài khoản hỏng trong một nghìn thì mang sang đợt sau; tổng tiền lệch hoặc tỉ lệ "chưa rõ" vọt thì chặn. |
| **Vì sao** | Chặn cả đợt vì ba ca lẻ là phạt hàng nghìn người vô can. |
| **Hệ quả** | Cần số liệu nền (mục 5) mới đặt ngưỡng có nghĩa. Đặt tạm rồi hiệu chỉnh sau ba đợt. |
| **Người quyết** | Founder + vận hành |
| **Hạn** | Trước ưu tiên 3 |

---

### D5 — Đợt bù có chịu cùng cổng chặn không?

| | |
| --- | --- |
| **Lựa chọn A** | Có — cổng đỏ thì bù cũng dừng. |
| **Lựa chọn B** | Không — đợt bù luôn chạy được. |
| **PO đề xuất** | **B có điều kiện**: đợt bù chạy được khi cổng đỏ, nhưng giới hạn số khoản và bắt buộc người thứ hai duyệt. |
| **Vì sao** | Cổng đỏ là lúc khiếu nại nhiều nhất. Khoá tay hỗ trợ đúng lúc đó là phản tác dụng. |
| **Hệ quả** | Đợt bù thành đường vòng qua cổng ⇒ phải là đường **hẹp và được ghi lại**, không phải cửa mở. |
| **Người quyết** | Founder + vận hành |
| **Hạn** | Trước ưu tiên 4 |

---

### D6 — Hạn mức 1,9 triệu/tháng còn hiệu lực không?

| | |
| --- | --- |
| **Lựa chọn** | Bật lại phần kiểm · gỡ khỏi thông điệp gửi khách · đổi con số |
| **PO đề xuất** | Chọn một trong hai hướng đầu, **không giữ nguyên hiện trạng** |
| **Vì sao** | Công bố mà không thực thi là lựa chọn tệ nhất trong ba — vừa không có trần chặn khoản bất thường, vừa có rủi ro tuân thủ trong sản phẩm mang thương hiệu ngân hàng. |
| **Người quyết** | Founder + pháp chế |
| **Hạn** | Trước ưu tiên 2 |

---

### D7 — MSHT và creator-os dùng chung một adapter AT-Core?

| | |
| --- | --- |
| **Lựa chọn A** | Chung một adapter + một kênh đối soát. |
| **Lựa chọn B** | Mỗi bên một cái. |
| **PO đề xuất** | Cần khảo sát trước khi chốt — nhưng **phải chốt sớm** |
| **Vì sao** | Milestone M2.1 của `creator-os` đã liệt `payout` vào năng lực AT-Core cần dựng adapter. Cùng đối tác, cùng nghiệp vụ. Chọn B thì trả giá hai lần và đối soát ở hai nơi với hai bộ số. |
| **Hệ quả** | Ảnh hưởng trực tiếp tới cách sinh mã khoản chi — nếu dùng chung thì mã **bắt buộc có tiền tố định danh sản phẩm** để không đụng nhau ở phía AT-Core. |
| **Người quyết** | Founder |
| **Hạn** | Trước khi chốt cách sinh mã ở ưu tiên 1 |

---

## 5. Đề xuất định nghĩa "đạt"

Viết theo khuôn milestone tổ chức đang dùng, để ghép được vào cùng hệ thống theo dõi:

> **ĐẠT KHI:** một khoản tiền hoàn đi trọn đường — đủ điều kiện → vào một đợt → AT-Core Chi hộ →
> tài khoản khách → đợt chốt sổ khớp — mà **không ai can thiệp tay**.
>
> Và **ba thứ đúng khi có sự cố:**
> lệnh gián đoạn thì không sinh khoản chi thứ hai ·
> đợt hỏng thì đợt kế tiếp không tự chạy ·
> lệch giữa sổ mình và sổ AT-Core thì có người nhìn thấy trước khi đợt sau mở.

### Bộ thước đo

Chỉ số dẫn đường mượn từ `creator-os` M1.7 — nhưng **không dùng một mình**:

```
Engineering intervention required for operational workflow = 0
```

> ⚠️ Chỉ số này **đạt được bằng cách không cho ai làm gì cả**. Dừng luồng chi thì kỹ sư cũng hết
> phải can thiệp. Nên nó phải đi kèm nhóm an toàn và nhóm khách hàng ở dưới, nếu không nó đo sai.

| Nhóm | Thước đo | Đích |
| --- | --- | --- |
| **An toàn** | Số khoản chi trùng | 0 |
| | Số lần gửi lại khi kết quả chưa rõ | 0 |
| | Số thao tác đổi trạng thái tiền không đủ bằng chứng | 0 |
| **Vận hành** | % ca xử lý xong không cần kỹ sư | tăng dần → 95% |
| | % đợt chốt sổ tự động, không người can thiệp | tăng dần |
| | Thời gian trung bình xử lý một ca | giảm |
| | % thao tác tay có audit đầy đủ kèm bằng chứng | 100% |
| **Đối soát** | Số tiền chưa đối soát | → 0 |
| | Tuổi khoản lệch lâu nhất | trong SLA |
| | % đợt đối soát xong trước khi đợt sau mở | 100% |
| | Thời gian từ lúc lệch phát sinh tới lúc có người biết | < 24h |
| **Khách hàng** | Tỉ lệ chi thành công | giữ |
| | % khoản chi trong SLA cam kết | tăng |
| | Số khách nhận thông báo sai trạng thái | 0 |

### Số cần lấy trước khi chốt phạm vi

Tài liệu chứng minh được "có thể mất tiền" nhưng **chưa lượng hoá**. Chia làm hai nhóm — nhóm đầu
lấy được ngay từ dữ liệu đang có, đừng để nó chờ:

**Lấy được tuần này, không cần dựng gì:**

- Một đợt trung bình bao nhiêu khoản chi, bao nhiêu tiền · đỉnh là bao nhiêu.
- Tổng chi mỗi ngày · phân bố số tiền mỗi khoản.
- **Số tiền đang treo chưa rõ kết quả tại thời điểm này** — con số quan trọng nhất để nói với lãnh đạo.
- Bao nhiêu khách đang có khoản treo, và khoản lâu nhất treo bao lâu.
- Số khoản chi trùng đã biết trong lịch sử, và tổng tiền.

**Phải dựng dấu vết mới đo được (ưu tiên 5):**

- Số ca cần kỹ sư mỗi tháng · số giờ kỹ sư và giờ vận hành tiêu vào đó.
- Thời gian xử lý trung bình một ca.
- Bao nhiêu ca phải tra log hoặc truy vấn cơ sở dữ liệu bằng tay.

Bốn hạng mục ở mục 3 lấp đúng bốn phase đang trống của khung M1.7:
**Incident** (ưu tiên 2, 4) · **Payout** (ưu tiên 1) · **Reconciliation** (ưu tiên 3, 6) ·
**Governance** (ưu tiên 5).

---

## Phụ lục — Tiền lệ trong tổ chức, nên xem trước khi thiết kế

| Nguồn | Dùng cho |
| --- | --- |
| `MSHT/manual-fulfillment-tpbank/PRD.md` | Khuôn chi tay khi đối tác hỏng (ưu tiên 4) |
| `techcombank/dashboard/src/hooks/use-transfers.ts` | Mô hình đợt: 9 trạng thái + thống kê theo lô (ưu tiên 1) |
| `MSHT/RASI/full.md` dòng 152 | Chống trùng bằng unique index — chặng 04 đã làm đúng |
| `creator-os` epic #2125 (M1.7) | Khung chín phase vòng đời vận hành (ưu tiên 5) |
| `creator-os` #2131 | Tách đối soát nội bộ khỏi đối soát tích hợp — **không gộp một màn** |
| `creator-os` #2150 | Phép đo ngược, và vì sao không dựng sổ tay |

**Lập luận nên mang theo khi xin nguồn lực:** chặng ngay trước chi trả — job thả tiền sau 60 ngày —
**đã chống trùng đúng** bằng unique index trên `transactionId`. Cùng pipeline, cùng đội. Chặng chi
trả, chặng duy nhất tiêu tiền thật, thì không. Và bước đối soát cuối ngày **có trong PRD mà không
được làm**.

⇒ Cả hai thứ đang gây mất tiền đều **từng được viết ra và bị bỏ qua**, không phải chưa ai nghĩ tới.
Đây là sự thiếu nhất quán, không phải giới hạn năng lực.
