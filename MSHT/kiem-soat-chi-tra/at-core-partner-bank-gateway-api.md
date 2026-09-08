# Partner Bank Gateway API — AT-Core Chi hộ

> **Nguồn:** `[Tech] Partner Bank Gateway API Documentation and Functionality Overview` — bản PDF
> xuất từ Confluence *(Core Platform)*, ngày tạo 20/08/2026, 33 trang.
> Bản `.md` này chuyển từ PDF để tra cứu và trích dẫn được. **Nội dung kỹ thuật giữ nguyên**; chỉ
> sắp xếp lại cho dễ đọc. PDF gốc giữ trong cùng thư mục làm bản đối chiếu.
>
> Tài liệu mô tả API cho partner của `bankgw-service`: tra cứu ngân hàng, tài khoản, chuyển tiền,
> tra cứu giao dịch, tính phí, kiểm tra số dư, ký số HSM. Các API nằm **sau gateway nội bộ** —
> gateway chịu trách nhiệm xác thực, phân quyền, kiểm soát truy cập.

---

> ## ⚠️ Ghi chú của người chuyển đổi — đọc trước
>
> Phần này **không thuộc tài liệu gốc**. Là đối chiếu với hiện trạng MSHT.
>
> **1. Chống trùng ĐÃ CÓ, và mình đang tự vô hiệu hoá nó.**
> Mục B.1: *"`txn_id` phải duy nhất theo partner"*, và HTTP `400` trả về khi **`txn_id` trùng**.
> Nghĩa là AT-Core **từ chối** giao dịch trùng mã. Nhưng MSHT sinh `txn_id` mới mỗi lần thử lại,
> nên hàng rào này chưa bao giờ chạm tới.
> ⇒ Câu hỏi số 1 trong [`van-de-can-at-core-ho-tro.md`](./van-de-can-at-core-ho-tro.md)
> **đã có đáp án, không cần hỏi đối tác.**
>
> **2. Khoá chống trùng là `txn_id`, KHÔNG phải `request_id`.**
> `request_id` trong tài liệu là *"Request ID từ gateway"* — mã lần gọi, không phải khoá nghiệp vụ.
> Bất biến **BB-2** phải sửa theo: mã khoản chi gắn vào **`txn_id`**.
>
> **3. Chống trùng là TỪ CHỐI, không phải TRẢ LẠI KẾT QUẢ CŨ.**
> Gửi lại cùng `txn_id` ⇒ nhận `400`, **không** nhận lại kết quả giao dịch gốc. Nên luồng gửi lại
> đúng phải là: gặp `400 txn_id trùng` ⇒ **gọi `txn-inquiry`** để biết giao dịch gốc ra sao.
> Coi `400` là "thất bại" là lặp lại đúng con lỗi cũ ở một tầng khác.
>
> **4. Ba năng lực mình ghi là "không có" — thực ra CÓ SẴN:**
> - `POST /v1.0/partner/fund-transfers` — **chuyển tiền hàng loạt** *(B.2)*
> - `GET /v1.0/partner/balance` — **kiểm tra số dư tài khoản nguồn** *(B.7)*
> - `GET /v1.0/partner/bank/account/legal/check` — **kiểm tra khách đã đồng ý điều khoản** *(A.8)*
>
> **5. Thứ vẫn KHÔNG có: truy vấn giao dịch theo khoảng thời gian.**
> 16 endpoint, không cái nào trả danh sách giao dịch theo kỳ. `txn-inquiry` chỉ tra **một** giao dịch
> theo mã đã biết. ⇒ **Yêu cầu số 2 vẫn đứng vững, và giờ là yêu cầu DUY NHẤT thật sự cần đối tác.**
>
> **6. `txn-inquiry` chỉ nhận `txn_id` hoặc `ref_txn_id`** — tài liệu **không** liệt kê `request_id`.
> Client Go có gửi trường đó nhưng có thể bị bỏ qua. Cần kiểm bằng thực nghiệm.
>
> **7. Có rate limit 5 giây** cho cùng `credit_account_number` trên mỗi partner *(B.1)* — một lớp
> chặn trùng thô đã tồn tại, nhưng chỉ bắt được lần gửi liên tiếp, không bắt được lần thử lại sau vài giờ.
>
> **8. Tài liệu này KHÔNG mô tả callback/webhook.** Toàn bộ là API kéo. Hợp đồng callback
> *(chính sách gửi lại, chữ ký, mã xác nhận)* vẫn phải hỏi riêng.

---

## 1. Cấu hình

### 1.1 Thông tin chung

| Mục | Giá trị |
| --- | --- |
| Base URL | `{{endpoint}}` |
| Path prefix (Bank) | `/v1.0/partner/bank` |
| Path prefix (Fund Transfer) | `/v1.0/partner` |
| API Version | 1.0 |
| Content-Type | `application/json` cho API có request body |
| Xác thực | Qua API Gateway *(xem tài liệu xác thực đi kèm)* |

| Môi trường | URL |
| --- | --- |
| **DEV** | `https://core-aff.dev.accesstrade.me/pgw-api/bankgw-service` |
| **PROD** | `https://apigw-core.oneat.org/pgw-api/bankgw-service` |

### 1.2 Định dạng response (JSend)

Thành công:

```json
{
  "status": "success",
  "data": { }
}
```

Lỗi:

```json
{
  "status": "fail",
  "data": null,
  "message": "Mô tả lỗi",
  "code": "ERROR_CODE"
}
```

### 1.3 Quy ước đặt tên

Tất cả field trong query parameter và request/response body dùng **snake_case**
*(ví dụ: `credit_bank_code`, `txn_id`)*.

---

## 2. Cấu trúc dữ liệu dùng chung

### 2.1 BankDTO

| Field | Type | Mô tả |
| --- | --- | --- |
| `id` | long | ID nội bộ |
| `bank_code` | string | Mã ngân hàng |
| `swift_code` | string | Mã SWIFT |
| `sml_code` | string | Mã SML (Napas) |
| `bank_name_en` | string | Tên ngân hàng (tiếng Anh) |
| `bank_name_vi` | string | Tên ngân hàng (tiếng Việt) |
| `partner_bank_code` | string | Mã ngân hàng theo partner |
| `citad_code` | string | Mã CITAD |

### 2.2 AccountInfoDTO

| Field | Type | Mô tả |
| --- | --- | --- |
| `account_name` | string | Tên tài khoản |
| `customer_name` | string | Tên khách hàng |
| `customer_short_name` | string | Tên viết tắt khách hàng |
| `customer_no` | string | Mã khách hàng |
| `account_number` | string | Số tài khoản |
| `bank_code` | string | Mã ngân hàng |

### 2.3 ElementListT — danh sách có phân trang

| Field | Type | Mô tả |
| --- | --- | --- |
| `element_list` | array[T] | Danh sách kết quả |
| `total` | long | Tổng số bản ghi |

### 2.4 TransferStatus

| Giá trị | Mô tả |
| --- | --- |
| `INIT` | Khởi tạo |
| `PENDING` | Chờ xử lý |
| `PROCESSING` | Đang xử lý |
| `SUCCESS` | Thành công |
| `FAILED` | Thất bại |
| `CANCEL` | Đã huỷ |
| `VERIFYING` | Đang xác minh |

### 2.5 FundTransferDTO

| Field | Type | Mô tả |
| --- | --- | --- |
| `id` | long | ID nội bộ |
| `partner_id` | long | ID partner |
| `request_id` | string | Request ID từ gateway |
| `txn_id` | string | Mã giao dịch (hệ thống đối tác) |
| `ref_txn_id` | string | Mã giao dịch tham chiếu (hệ thống nội bộ) |
| `extra_txn_id` | string | Mã giao dịch bổ sung |
| `credit_bank_code` | string | Mã ngân hàng nhận |
| `credit_account_number` | string | Số tài khoản nhận |
| `credit_account_name` | string | Tên tài khoản nhận |
| `credit_account_type` | string | Loại tài khoản nhận (VD: `ACCOUNT`) |
| `transfer_amount` | long | Số tiền chuyển (VND) |
| `transfer_fee` | long | Phí chuyển |
| `transfer_status` | string | Trạng thái — xem 2.4 |
| `conversion_id` | string | Mã conversion |
| `transfer_time` | string | Thời gian chuyển, `yyyy-MM-dd'T'HH:mm:ssZ` (GMT+7) |
| `actual_transaction_time` | string | Thời gian giao dịch thực tế, cùng định dạng |
| `original_status` | string | Trạng thái gốc từ vendor |
| `remark` | string | Ghi chú |
| `error_code` | string | Mã lỗi (nếu có) |
| `error_message` | string | Thông báo lỗi (nếu có) |
| `user_id` | string | ID người dùng |
| `customer_id` | string | ID khách hàng |

### 2.6 FundTransferCreateDTO

Dùng trong API chuyển tiền hàng loạt.

| Field | Type | Bắt buộc | Mô tả |
| --- | --- | :---: | --- |
| `txn_id` | string | **Có** | Mã giao dịch — **duy nhất theo partner** |
| `request_id` | string | Không | Request ID |
| `conversion_id` | string | Không | Mã conversion |
| `credit_bank_code` | string | Không | Mã ngân hàng nhận |
| `credit_account_number` | string | **Có** | Số tài khoản nhận |
| `credit_account_name` | string | **Có** ¹ | Tên tài khoản nhận |
| `transfer_amount` | long | **Có** | Số tiền chuyển (VND) |
| `remark` | string | Không | Ghi chú |
| `account_id` | string | Không | ID tài khoản |
| `user_id` | string | Không | ID người dùng |
| `customer_id` | string | Không | ID khách hàng |

¹ Không bắt buộc khi vendor là `SEABANK`.

### 2.7 CalculateFeeResponse

| Field | Type | Mô tả |
| --- | --- | --- |
| `partner_id` | long | ID partner |
| `credit_bank_code` | string | Mã ngân hàng nhận |
| `credit_account_type` | string | Loại tài khoản nhận |
| `transfer_amount` | long | Số tiền chuyển |
| `transfer_fee` | long | Phí chuyển tính được |
| `fee_config` | FeeConfigDTO | Cấu hình phí áp dụng |

### 2.8 FeeConfigDTO

| Field | Type | Mô tả |
| --- | --- | --- |
| `id` | long | ID cấu hình |
| `partner_id` | long | ID partner |
| `fixed_amount` | decimal | Phí cố định |
| `percentage` | float | Phần trăm phí |
| `min_amount` | decimal | Phí tối thiểu |
| `max_amount` | decimal | Phí tối đa |
| `is_default` | boolean | Có phải cấu hình mặc định |
| `regex_bank` | string | Regex lọc ngân hàng |
| `banks` | array[BankDTO] | Danh sách ngân hàng áp dụng |

### 2.9 BalanceDTO

| Field | Type | Mô tả |
| --- | --- | --- |
| `balance` | decimal | Số dư tài khoản nguồn |

### 2.10 CashbackDTO

| Field | Type | Mô tả |
| --- | --- | --- |
| `status_desc` | string | Mô tả trạng thái |
| `status_code` | string | Mã trạng thái |

### 2.11 FundTransferESignResponse

| Field | Type | Mô tả |
| --- | --- | --- |
| `sign_content` | array[SignContentDTO] | Danh sách nội dung đã ký |
| `transaction_id` | long | ID giao dịch ký số |
| `request_id` | string | Request ID |

**SignContentDTO** *(response)*: `content_id` (string), `signed_content` (string).

---

## Phần A — API ngân hàng

`PartnerBankRestApiController` · path prefix `{{endpoint}}/v1.0/partner/bank`

### A.1 Tra cứu ngân hàng theo SWIFT Code

```
GET {{endpoint}}/v1.0/partner/bank/swift-code/{swiftCode}
```

| Parameter | Type | Bắt buộc | Mô tả |
| --- | --- | :---: | --- |
| `swiftCode` | string (path) | **Có** | Mã SWIFT của ngân hàng |

Response `200`:

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "bank_code": "MSCBVNVX",
    "swift_code": "MSCBVNVX",
    "sml_code": "970422",
    "bank_name_en": "Military Commercial Joint Stock Bank",
    "bank_name_vi": "Ngân hàng TMCP Quân Đội",
    "partner_bank_code": "MB",
    "citad_code": "01311001"
  }
}
```

Lỗi: `400` thiếu `swift_code` hoặc ngân hàng không tồn tại · `403` từ chối truy cập · `500` lỗi server.

```bash
curl -X GET "{{endpoint}}/v1.0/partner/bank/swift-code/MSCBVNVX"
```

### A.2 Tra cứu ngân hàng theo SML Code

```
GET {{endpoint}}/v1.0/partner/bank/sml-code/{smlCode}
```

| Parameter | Type | Bắt buộc | Mô tả |
| --- | --- | :---: | --- |
| `smlCode` | string (path) | **Có** | Mã SML (Napas) |

Response `200` — cấu trúc tương tự A.1. Lỗi: `400` · `403` · `500`.

```bash
curl -X GET "{{endpoint}}/v1.0/partner/bank/sml-code/970422"
```

### A.3 Tìm kiếm ngân hàng

```
GET {{endpoint}}/v1.0/partner/bank/find
```

| Parameter | Type | Bắt buộc | Mô tả |
| --- | --- | :---: | --- |
| `search_text` | string | Không | Từ khoá (tên, mã ngân hàng…) |
| `page` | integer | **Có** | Số trang, bắt đầu từ 1. Giá trị `< 1` báo lỗi |
| `size` | integer | Không | Số bản ghi mỗi trang |
| `sort_field` | string | Không | Trường sắp xếp (mặc định `id`) |
| `direction` | string | Không | `ASC` hoặc `DESC` (mặc định `ASC`) |

Response `200` — `ElementListT<BankDTO>`. Lỗi: `400` `page < 1` hoặc thiếu header bắt buộc · `403` · `500`.

```bash
curl -G "{{endpoint}}/v1.0/partner/bank/find" --data-urlencode "search_text=Quan Doi" --data-urlencode "page=1" --data-urlencode "size=20"
```

### A.4 Lấy thông tin tài khoản ngân hàng

```
GET {{endpoint}}/v1.0/partner/bank/account/info
```

| Parameter | Type | Bắt buộc | Mô tả |
| --- | --- | :---: | --- |
| `account_number` | string | **Có** | Số tài khoản |
| `bank_code` | string | **Có** | Mã ngân hàng (SWIFT/bank code) |
| `legal_id` | string | Không | Số CMND/CCCD |
| `user_id` | string | Không | ID người dùng |
| `customer_id` | string | Không | ID khách hàng |

Response `200` — `AccountInfoDTO`. Lỗi: `400` thiếu `account_number` hoặc `bank_code` · `403` ·
`500` lỗi server hoặc lỗi từ vendor ngân hàng.

```bash
curl -G "{{endpoint}}/v1.0/partner/bank/account/info" --data-urlencode "account_number=0011234567890" --data-urlencode "bank_code=MSCBVNVX"
```

### A.5 Lấy danh sách tài khoản ngân hàng

```
GET {{endpoint}}/v1.0/partner/bank/accounts
```

| Parameter | Type | Bắt buộc | Mô tả |
| --- | --- | :---: | --- |
| `user_id` | string | **Có** | ID người dùng |
| `account_number` | string | Không | Số tài khoản |
| `bank_code` | string | Không | Mã ngân hàng |
| `legal_id` | string | Không | Số CMND/CCCD |
| `customer_id` | string | Không | ID khách hàng |

Response `200` — `array[AccountInfoDTO]`. Lỗi: `400` thiếu `user_id` · `403` · `500`.

```bash
curl -G "{{endpoint}}/v1.0/partner/bank/accounts" --data-urlencode "user_id=user_123"
```

### A.6 Lấy tài khoản theo Legal ID

```
GET {{endpoint}}/v1.0/partner/bank/account/info/by-legal-id
```

| Parameter | Type | Bắt buộc | Mô tả |
| --- | --- | :---: | --- |
| `legal_id` | string | **Có** | Số CMND/CCCD |
| `user_id` | string | **Có** | ID người dùng |
| `customer_id` | string | Không | ID khách hàng |
| `account_number` | string | Không | Số tài khoản |
| `bank_code` | string | Không | Mã ngân hàng |

Response `200` — `array[AccountInfoDTO]`. Lỗi: `400` thiếu `legal_id` hoặc `user_id` · `403` · `500`.

### A.7 Kiểm tra thông tin tài khoản

```
GET {{endpoint}}/v1.0/partner/bank/account/info/check
```

Kiểm tra tài khoản ngân hàng có hợp lệ hay không. **Phải có ít nhất một trong hai:**
`account_number` hoặc `legal_id`.

| Parameter | Type | Bắt buộc | Mô tả |
| --- | --- | :---: | --- |
| `customer_id` | string | **Có** | ID khách hàng |
| `account_number` | string | Có ¹ | Số tài khoản |
| `legal_id` | string | Có ¹ | Số CMND/CCCD |

Response `200`: `{"status":"success","data":{"check_account":true}}`

Lỗi: `400` thiếu `customer_id`, hoặc thiếu cả `account_number` và `legal_id` · `403` · `500`.

### A.8 Kiểm tra điều khoản pháp lý tài khoản

```
GET {{endpoint}}/v1.0/partner/bank/account/legal/check
```

Kiểm tra khách hàng đã đồng ý điều khoản sử dụng (TOS) hay chưa.

| Parameter | Type | Bắt buộc | Mô tả |
| --- | --- | :---: | --- |
| `customer_id` | string | **Có** | ID khách hàng |
| `legal_id` | string | **Có** | Số CMND/CCCD |
| `account_number` | string | Không | Số tài khoản |

Response `200`: `{"status":"success","data":{"check_legal":true}}`

Lỗi: `400` thiếu `customer_id` hoặc `legal_id` · `403` · `500`.

---

## Phần B — API chuyển tiền

`PartnerFundTransferRestAPIController` · path prefix `{{endpoint}}/v1.0/partner`

### B.1 Chuyển tiền (đơn lẻ)

```
POST {{endpoint}}/v1.0/partner/fund-transfer
```

> 🔴 **`txn_id` phải duy nhất theo partner.**
> Hệ thống có **rate limit 5 giây** cho cùng `credit_account_number` trên mỗi partner.

| Field | Type | Bắt buộc | Mô tả |
| --- | --- | :---: | --- |
| `txn_id` | string | **Có** | Mã giao dịch — **duy nhất theo partner** |
| `credit_bank_code` | string | **Có** | Mã ngân hàng nhận (phải tồn tại trong hệ thống) |
| `credit_account_number` | string | **Có** | Số tài khoản nhận |
| `credit_account_name` | string | **Có** ¹ | Tên tài khoản nhận |
| `credit_account_type` | string | **Có** | Loại tài khoản nhận (VD: `ACCOUNT`) |
| `transfer_amount` | long | **Có** | Số tiền chuyển (VND) |
| `remark` | string | Không | Ghi chú giao dịch |
| `account_id` | string | Không | ID tài khoản |
| `user_id` | string | Không | ID người dùng |
| `customer_id` | string | Không | ID khách hàng |

¹ Không bắt buộc khi vendor là `SEABANK`.

> **Tài khoản nguồn (debit) được cấu hình sẵn cho partner** — `FUND_TRANSFER_DEBIT_BANK_CODE`,
> `FUND_TRANSFER_DEBIT_RESOURCE_NUMBER`, `FUND_TRANSFER_DEBIT_NAME`. **Không gửi trong request.**

Response `200`:

```json
{
  "status": "success",
  "data": {
    "id": 1001,
    "partner_id": 1,
    "request_id": "trace-abc-123",
    "txn_id": "183b69a0c8084607aef618d2c6222ac5",
    "ref_txn_id": "atcore_183b69a0c8084607aef618d2c6222ac5",
    "credit_bank_code": "MSCBVNVX",
    "credit_account_number": "0011234567890",
    "credit_account_name": "Nguyen Van A",
    "credit_account_type": "ACCOUNT",
    "transfer_amount": 100000,
    "transfer_fee": 0,
    "transfer_status": "PROCESSING",
    "transfer_time": "2026-06-24T10:30:00+0700",
    "remark": "Chuyen tien cashback",
    "user_id": "user_123",
    "customer_id": "CIF001"
  }
}
```

| HTTP | Ý nghĩa |
| --- | --- |
| `400` | Thiếu field bắt buộc · **`txn_id` trùng** · `credit_bank_code` không hợp lệ · rate limit |
| `403` | Quyền truy cập bị từ chối |
| `500` | Lỗi server hoặc lỗi từ vendor chuyển tiền |

```bash
curl -X POST "{{endpoint}}/v1.0/partner/fund-transfer" -H "Content-Type: application/json" -d '{"txn_id":"183b69a0c8084607aef618d2c6222ac5","credit_bank_code":"MSCBVNVX","credit_account_number":"0011234567890","credit_account_name":"Nguyen Van A","credit_account_type":"ACCOUNT","transfer_amount":100000,"remark":"Chuyen tien cashback"}'
```

### B.2 Chuyển tiền hàng loạt

```
POST {{endpoint}}/v1.0/partner/fund-transfers
```

Thực hiện nhiều giao dịch chuyển tiền trong một request.

> **Lưu ý:** với partner `TPBANK` chỉ hỗ trợ trong 1 lô gồm các tài khoản TPB **hoặc** NAPAS —
> nếu trộn sẽ trả lỗi.

| Field | Type | Bắt buộc | Mô tả |
| --- | --- | :---: | --- |
| `fund_transfers` | array[FundTransferCreateDTO] | **Có** | Danh sách giao dịch — xem 2.6 |

Response `200` — `array[FundTransferDTO]`, mỗi phần tử có `txn_id`, `ref_txn_id`, `transfer_status`.

Lỗi: `400` `fund_transfers` rỗng, thiếu field bắt buộc, **`txn_id` trùng** · `403` · `500`.

### B.3 Tra cứu giao dịch

```
GET {{endpoint}}/v1.0/partner/txn-inquiry
```

Tra cứu trạng thái giao dịch chuyển tiền theo `txn_id` hoặc `ref_txn_id`.

| Parameter | Type | Bắt buộc | Mô tả |
| --- | --- | :---: | --- |
| `txn_id` | string | Có ¹ | Mã giao dịch (hệ thống đối tác) |
| `ref_txn_id` | string | Có ¹ | Mã giao dịch tham chiếu (hệ thống nội bộ) |

¹ **Phải có ít nhất một trong hai.** Tài liệu không liệt kê `request_id` làm tham số tra cứu.

Response `200` — `FundTransferDTO` *(có `transfer_amount`, `transfer_status`, `error_code`…)*.

Lỗi: `400` thiếu cả hai mã · `403` · `404` không tìm thấy giao dịch · `500`.

```bash
curl -G "{{endpoint}}/v1.0/partner/txn-inquiry" --data-urlencode "txn_id=183b69a0c8084607aef618d2c6222ac5"
```

### B.4 Tính phí chuyển tiền (đơn lẻ)

```
GET {{endpoint}}/v1.0/partner/calculate-fee
```

| Parameter | Type | Bắt buộc | Mô tả |
| --- | --- | :---: | --- |
| `credit_bank_code` | string | **Có** | Mã ngân hàng nhận |
| `credit_account_type` | string | **Có** | Loại tài khoản nhận |
| `transfer_amount` | long | **Có** | Số tiền chuyển (VND) |

Response `200` — `CalculateFeeResponse`. Lỗi: `400` · `403` · `500`.

### B.5 Tính phí chuyển tiền (nhiều ngân hàng)

```
GET {{endpoint}}/v1.0/partner/calculate-fees
```

| Parameter | Type | Bắt buộc | Mô tả |
| --- | --- | :---: | --- |
| `credit_bank_codes` | array[string] | **Có** | Danh sách mã ngân hàng nhận |
| `credit_account_type` | string | **Có** | Loại tài khoản nhận |
| `transfer_amount` | long | **Có** | Số tiền chuyển (VND) |

Response `200` — `array[CalculateFeeResponse]`.

### B.6 Cập nhật trạng thái Cashback

```
POST {{endpoint}}/v1.0/partner/cashback/status
```

Gửi thông báo cập nhật trạng thái cashback/đơn hàng cho người dùng.
**Phải có ít nhất một trong hai:** `cashback_status` hoặc `order_status`.

| Field | Type | Bắt buộc | Mô tả |
| --- | --- | :---: | --- |
| `user_id` | string | **Có** | ID người dùng |
| `cashback_status` | CashbackStatusDTO | Có ¹ | Thông tin trạng thái cashback |
| `order_status` | OrderStatusDTO | Có ¹ | Thông tin trạng thái đơn hàng |
| `lang` | string | Không | `VI` hoặc `EN` |
| `notification_content` | string | Không | Nội dung thông báo đầy đủ |
| `short_notification_content` | string | Không | Nội dung thông báo ngắn |
| `subject` | string | Không | Tiêu đề thông báo |
| `cif` | string | Không | Mã CIF khách hàng |
| `redirect_type` | string | Không | Loại redirect |
| `redirect_value` | string | Không | Giá trị redirect |

**CashbackStatusDTO**: `request_id`, `request_amount`, `request_time`, `status`.
**OrderStatusDTO**: `order_id`, `brand`, `order_amount`, `order_commission`, `order_time`, `status`.

Response `200` — `CashbackDTO` *(`status_desc`, `status_code`)*.

### B.7 Kiểm tra số dư

```
GET {{endpoint}}/v1.0/partner/balance
```

Kiểm tra **số dư tài khoản nguồn chuyển tiền của partner**.
Không yêu cầu query parameter — partner được xác định qua header gateway.

Response `200`:

```json
{
  "status": "success",
  "data": { "balance": 150000000.00 }
}
```

Lỗi: `400` partner không tồn tại hoặc thiếu header bắt buộc · `403` · `500`.

### B.8 Ký số HSM (e-Sign)

```
POST {{endpoint}}/v1.0/partner/e-sign
```

Ký số nội dung bằng HSM. **`request_id` (header `trace-no`) phải duy nhất.**

| Field | Type | Bắt buộc | Mô tả |
| --- | --- | :---: | --- |
| `sign_type` | string | **Có** | Hiện hỗ trợ: `HSM` |
| `swift_code` | string | Không | Mã SWIFT ngân hàng |
| `sign_content` | array[SignContentDTO] | **Có** | Danh sách nội dung cần ký |

**SignContentDTO** *(request)*: `content_id`, `content_type` (`PDF` · `PLAIN_TEXT` · `OFFICE` · `XML`),
`content` (base64 hoặc plain text).

Lỗi: `400` thiếu `sign_type`, `sign_content` rỗng, thiếu field, **`request_id` trùng** · `403` · `500`.

---

## 3. Bảng tóm tắt API

### Phần A — Ngân hàng

| # | Method | Endpoint | Mô tả | MSHT dùng? |
| --- | --- | --- | --- | :---: |
| A.1 | GET | `/v1.0/partner/bank/swift-code/{swiftCode}` | Tra cứu ngân hàng theo SWIFT | ❌ |
| A.2 | GET | `/v1.0/partner/bank/sml-code/{smlCode}` | Tra cứu ngân hàng theo SML | ❌ |
| A.3 | GET | `/v1.0/partner/bank/find` | Tìm kiếm ngân hàng | ❌ |
| A.4 | GET | `/v1.0/partner/bank/account/info` | Lấy thông tin tài khoản | ✅ |
| A.5 | GET | `/v1.0/partner/bank/accounts` | Lấy danh sách tài khoản | ❌ |
| A.6 | GET | `/v1.0/partner/bank/account/info/by-legal-id` | Lấy tài khoản theo Legal ID | ❌ |
| A.7 | GET | `/v1.0/partner/bank/account/info/check` | Kiểm tra tài khoản | ❌ |
| A.8 | GET | `/v1.0/partner/bank/account/legal/check` | Kiểm tra TOS pháp lý | ❌ |

### Phần B — Chuyển tiền

| # | Method | Endpoint | Mô tả | MSHT dùng? |
| --- | --- | --- | --- | :---: |
| B.1 | POST | `/v1.0/partner/fund-transfer` | Chuyển tiền đơn lẻ | ✅ |
| B.2 | POST | `/v1.0/partner/fund-transfers` | **Chuyển tiền hàng loạt** | ❌ |
| B.3 | GET | `/v1.0/partner/txn-inquiry` | Tra cứu giao dịch | ✅ |
| B.4 | GET | `/v1.0/partner/calculate-fee` | Tính phí (đơn lẻ) | ❌ |
| B.5 | GET | `/v1.0/partner/calculate-fees` | Tính phí (nhiều ngân hàng) | ❌ |
| B.6 | POST | `/v1.0/partner/cashback/status` | Cập nhật trạng thái cashback | ❌ |
| B.7 | GET | `/v1.0/partner/balance` | **Kiểm tra số dư** | ❌ |
| B.8 | POST | `/v1.0/partner/e-sign` | Ký số HSM | ❌ |

**16 endpoint · MSHT đang dùng 3.**

---

## 4. Bảng tóm tắt HTTP Status

| HTTP | Ý nghĩa |
| --- | --- |
| `200` | Thành công |
| `400` | Lỗi request — thiếu field, sai định dạng, **`txn_id` trùng**, rate limit |
| `403` | Quyền truy cập bị từ chối |
| `404` | Không tìm thấy *(chỉ ở `txn-inquiry`)* |
| `500` | Lỗi server nội bộ hoặc lỗi từ vendor |

---

## 5. Luồng tích hợp gợi ý *(theo tài liệu gốc)*

1. **Tra cứu ngân hàng** — `GET /v1.0/partner/bank/sml-code/{smlCode}` hoặc `GET /v1.0/partner/bank/find`
2. **Xác minh tài khoản** — `GET /v1.0/partner/bank/account/info` hoặc `.../account/info/check` **trước khi chuyển tiền**
3. **Tính phí** — `GET /v1.0/partner/calculate-fee`
4. **Kiểm tra số dư** — `GET /v1.0/partner/balance` để đảm bảo đủ số dư
5. **Chuyển tiền** — `POST /v1.0/partner/fund-transfer` với **`txn_id` duy nhất**
6. **Tra cứu kết quả** — `GET /v1.0/partner/txn-inquiry`
7. **Thông báo cashback** — `POST /v1.0/partner/cashback/status`

> Luồng MSHT hiện tại bỏ qua bước **2, 3, 4 và 7**.
