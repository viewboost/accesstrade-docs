# Affiliate x Pub2 API Reference

## Mục lục

- [Security & Authentication](#security--authentication)
- [Error Code](#error-code)
- [Practical Testing Notes](#practical-testing-notes)
  - [Dev environment seeded data](#7-dev-environment-seeded-data--client-side-overrides)
- [API 1: Lấy thông tin Campaign (Optional)](#api-1-lấy-thông-tin-campaign-optional)
- [API 1.2: Tham gia chiến dịch](#api-12-tham-gia-chiến-dịch)
- [API 2: Lấy Link Affiliate](#api-2-lấy-link-affiliate)
- [API 3.1: Báo cáo Click](#api-31-báo-cáo-click)
- [API 3.2: Báo cáo Conversion](#api-32-báo-cáo-conversion)
- [API 3.3: Báo cáo Sale Amount](#api-33-báo-cáo-sale-amount)
- [API 3.4: Báo cáo Commission (Hoa hồng)](#api-34-báo-cáo-commission-hoa-hồng)
- [API 6: Báo cáo Tổng hợp](#api-6-báo-cáo-tổng-hợp)
- [API 7: Webhook (Optional)](#api-7-webhook-optional)
- [API 8: Danh sách đơn](#api-8-danh-sách-đơn)

---

## Security & Authentication

### Endpoint

```
https://core-aff.dev.accesstrade.me
```

### Required Headers

| Header | Mô tả |
|---|---|
| `client-id` | Mã định danh đối tác |
| `client-trace-no` | Mã yêu cầu định danh cho yêu cầu gửi (duy nhất) |
| `client-request-time` | Thời gian gửi yêu cầu |
| `client-signature` | Chữ ký xác thực yêu cầu gửi |

### Cách tạo Signature

```
client-signature = HMACSHA256(clientId + "|" + clientTraceNo + "|" + clientRequestTime, clientSecret)
```

### Credentials (Dev/Mock)

| Key | Value |
|---|---|
| `partnergw_client_id` | `rB6v1sntuoaqWUki` |
| `partnergw_client_secret_key` | `BWLFwsIIE8PjAn6f2oa3mjemLf0GNWhe` |

---

## Error Code

Response chuẩn bao gồm 3 trường:

| Field | Ý nghĩa | Giá trị |
|---|---|---|
| `status` | Kết quả hành động | `"success"` — Thành công |
| | | `"fail"` — Thất bại do dữ liệu/logic |
| | | `"error"` — Thất bại do hệ thống |
| `code` | Mã lỗi | `PX00000` = thành công. Khác giá trị này là thất bại, nội dung lỗi tương ứng với `message` |
| `message` | Nội dung tương ứng code | `"success"` |

### Mã lỗi đã gặp thực tế

| Code | HTTP | Message | Nguyên nhân thực tế |
|---|---|---|---|
| `PX00000` | 200 | `success` | Thành công |
| `PX00002` | 400 | `Invalid value for parameter 'from_date'` | Sai format ngày tháng (xem [Practical Testing Notes](#practical-testing-notes)) |
| `PX00099` | 400 | `Dữ liệu không đúng định dạng` | Body hoặc field không đúng spec (ví dụ `from_date` format sai với `conversion-service`) |
| `PX00099` | 400 | `Khoảng thời gian tìm kiếm vượt quá 3 tháng` | `to_date - from_date > 3 months` (xem [Practical Testing Notes](#practical-testing-notes)) |
| `PX000100` | 400 | `Có lỗi xảy ra phía nhà cung cấp` | Lỗi upstream Pub2. Thực tế: xảy ra khi `partner_ref_campaign_id` rỗng/không hợp lệ ở [API 2](#api-2-lấy-link-affiliate) |

---

## Practical Testing Notes

> Ghi chú dựa trên kết quả test thực tế trên môi trường `core-aff.dev.accesstrade.me` (verified 2026-04-24, sso_user_id=504).

### 1. Format `from_date` / `to_date` (BẮT BUỘC)

Pub2 **chỉ chấp nhận** format ISO-8601 có offset timezone **không có dấu `:` trong offset**:

```
YYYY-MM-DDTHH:mm:ss+0700
```

- ✅ Hợp lệ: `2026-02-23T00:00:00+0700`
- ❌ Reject (`PX00002` / `PX00099`): `2026-02-23 00:00:00`, `2026-02-23T00:00:00+07:00`, `2026-02-23T00:00:00Z`

Backend implementation tương ứng: [`formatPub2Date()`](../../ambassabor/backend/pkg/public/service/affiliate.go) — convert input sang `Asia/Ho_Chi_Minh` rồi format `2006-01-02T15:04:05+0700` (Go layout).

### 2. Giới hạn khoảng thời gian 3 tháng

Tất cả API report (API 3.1, 3.2, 3.3, 3.4) và API 8 (danh sách đơn) đều reject nếu `to_date - from_date > 3 tháng` với:

```json
{ "code": "PX00099", "message": "Khoảng thời gian tìm kiếm vượt quá 3 tháng" }
```

**Khuyến nghị**: validate ở client/BFF trước khi gọi Pub2 để trả về error message thân thiện (hoặc chia nhỏ range).

### 3. `partner_ref_campaign_id` không được rỗng ở API 2

Ở [API 2 (Lấy Link Affiliate)](#api-2-lấy-link-affiliate), nếu truyền `"partner_ref_campaign_id": ""` (rỗng), Pub2 trả:

```json
{ "code": "PX000100", "message": "Có lỗi xảy ra phía nhà cung cấp" }
```

Phải luôn truyền campaign ID hợp lệ (VD: `4751584435713464237` — Shopee Smartlink trên môi trường dev).

### 4. Signature & timestamp

- `client-request-time` là **Unix epoch milliseconds** (ví dụ `1777043989000`), không phải giây hay ISO string.
- `client-trace-no` là UUID v4 (lowercase).
- Signature HMAC-SHA256 với message ghép bằng ký tự `|`:

```
HMAC-SHA256(client_id + "|" + client_trace_no + "|" + client_request_time, client_secret)
```

Test nhanh bằng `openssl`:

```sh
echo -n "$CLIENT_ID|$TRACE_NO|$REQUEST_TIME" | openssl dgst -sha256 -hmac "$CLIENT_SECRET" -hex
```

### 5. Data shape đặc biệt

- **`statistics` key là Unix epoch seconds** (theo ngày, `+0700`), không phải date string → FE phải parse và format lại.
- **`statistic_details` chỉ xuất hiện ở API 3.3 (sale-amount) và 3.4 (commission)**; API 3.1 (click) và 3.2 (conversion) không có breakdown theo trạng thái.
- Trong response API 8, `total_sale_amount` có thể là **scientific notation** (VD `6.74502E7` = 67,450,200) — JSON parser chuẩn handle OK, nhưng cần lưu ý khi hiển thị.

### 6. Testing script

Script test end-to-end: [`.tmp/pub2-test/test-pub2.sh`](../../../.tmp/pub2-test/test-pub2.sh) (trong thư mục workspaces root) — gọi cả 6 APIs với `sso_user_id=504` và lưu response từng API ra file JSON riêng.

### 7. Dev environment: seeded data & client-side overrides

> Chỉ áp dụng trên môi trường **`core-aff.dev.accesstrade.me`**. Không tồn tại trong staging/production code path.

**Seeded data trên Pub2 dev** chỉ có cho `sso_user_id=504`. Scan toàn bộ Q1/2023 → Q2/2026 cho thấy data tập trung ở:

| Tháng | Orders | Clicks | Conversions | Sale | Commission |
|---|---|---|---|---|---|
| 2023-04 | 29,046 | 0 | 29,900 | ~7.38 tỷ | ~1.13 tỷ |
| 2023-05 | 2,301 | 1 | 1,745 | ~27 triệu | ~205 triệu |
| 2023-03 | 24 | 0 | 2 | 0.12M | 14K |
| 2026-03 | 6 | 0 | 0 | 0 | 0 |
| Các tháng khác | 0 | 0 | 0 | 0 | 0 |

**Hệ quả**: nếu gọi Pub2 dev với bất kỳ `sso_user_id` nào khác 504, hoặc với range ngoài 2023-03 → 2023-05, kết quả là **rỗng**.

**Client-side override pattern khuyến nghị** khi chạy backend ở `ENV=development`:
- Rewrite `from_date` / `to_date` → `2023-03-01T00:00:00+0700` / `2023-05-31T23:59:59+0700` (đúng 3 tháng — sát hard-limit Pub2).
- Rewrite `sso_user_id` → `504`.
- Clear `campaign_ids` về rỗng (vì pub2 campaign IDs map từ Mongo dev DB có thể không trùng với campaigns có seeded data — test với `4751584435713464237` Shopee Smartlink và `5250371113292977031` Shopee KOL NEW là chắc chắn có).

Áp dụng overrides **chỉ cho report/listing APIs** (API 3.1–3.4 + API 8). **Tuyệt đối không** override cho mutation APIs (API 1.2 JoinCampaign, API 2 GenerateLink) — cần giữ `sso_user_id` thật để test flow contract.

Reference implementation (Go): xem `backend/internal/module/pub2/client.go` — helper `applyDevReportOverride()` bảo vệ bằng `config.IsEnvDevelop()`, no-op ngoài dev.

---

## API 1: Lấy thông tin Campaign (Optional)

> **Trạng thái:** Chưa cung cấp ở thời điểm hiện tại.
>
> Thông tin đã được tổ chức bên DISO, API này chỉ dùng để validate `campaign_id`.

---

## API 1.2: Tham gia chiến dịch

Đăng ký tham gia chiến dịch (tạo affiliation/contract).

- **Method:** `POST`
- **URL:** `{{endpoint}}/pgw-api/campaign-service/api/v1/contracts`
- **Security:** Xem [Security & Authentication](#security--authentication)

### Request Body

```json
{
    "partner_code": "PARTNER_1_POINT_5",
    "sso_id": 504,
    "partner_ref_campaign_id": "4751584435713464237"
}
```

| Field | Type | Mô tả |
|---|---|---|
| `partner_code` | String | Để mặc định `"PARTNER_1_POINT_5"` |
| `sso_id` | Number | Mã định danh người dùng (mã SSO) |
| `partner_ref_campaign_id` | String | Mã định danh chiến dịch |

### Response

```json
{
    "status": "success",
    "error_code": 0,
    "message": "Affiliation already exist",
    "data": {
        "contract_no": "6826007805108298670",
        "contract_status": "APPROVED"
    }
}
```

| Field | Type | Mô tả |
|---|---|---|
| `status` | String | Kết quả hành động |
| `error_code` | Number | Mã lỗi trả về |
| `message` | String | Nội dung lỗi trả về |
| `data.contract_no` | String | Mã liên kết giữa publisher và campaign |
| `data.contract_status` | String | Trạng thái mã liên kết (xem bảng bên dưới) |

### Error Code

| error_code | Mô tả |
|---|---|
| `0` | Thành công (Không lỗi) |
| `1` | Publisher không tồn tại |
| `2` | Campaign hoặc merchant không tồn tại |
| `5` | Ekyc thất bại |
| `7` | Chưa đăng ký campaign cha |
| `8` | Lỗi tạo affiliation |
| `9` | Đang trong quá trình đồng bộ tài khoản (Sync account) |
| `10` | Không đủ điều kiện tham gia |
| `11` | Campaign cha không tồn tại |
| `12` | Đồng bộ người dùng thất bại (Sync user fail) |
| `13` | Đang trong quá trình đồng bộ site (Sync site) |
| Khác | Lỗi hệ thống không xác định |

### Contract Status

| Status | Mô tả |
|---|---|
| `PENDING` | Chờ duyệt |
| `APPROVED` | Đã duyệt |
| `REJECTED` | Từ chối |

---

## API 2: Lấy Link Affiliate

Tạo link affiliate cho campaign.

- **Method:** `POST`
- **URL:** `{{endpoint}}/pgw-api/tracking-service/api/v1.0/publisher/affiliate/link`
- **Security:** Xem [Security & Authentication](#security--authentication)

### Request Body

```json
{
    "partner_code": "PARTNER_1_POINT_5",
    "original_url": "https://avay.vn/?utm_campaign=cps",
    "partner_ref_campaign_id": "4984260100521590721",
    "sso_user_id": 504,
    "sub1": "504",
    "sub2": "231",
    "sub3": "sample_template",
    "sub4": "oneatapp",
    "utm_source": null,
    "utm_medium": null,
    "utm_campaign": null,
    "utm_content": null
}
```

| Field | Type | Mô tả |
|---|---|---|
| `partner_code` | String | Để mặc định `"PARTNER_1_POINT_5"` |
| `original_url` | String | Link gốc — phải được chiến dịch hỗ trợ |
| `partner_ref_campaign_id` | String | Mã định danh chiến dịch |
| `sso_user_id` | Number | Mã định danh người dùng |
| `sub1` — `sub4` | String | Layer tracking |
| `utm_source`, `utm_medium`, `utm_campaign`, `utm_content` | String | Tạm thời không quan tâm |

> **Lưu ý quan trọng:** `partner_ref_campaign_id` **không được rỗng**. Nếu truyền `""` thì Pub2 trả `PX000100 "Có lỗi xảy ra phía nhà cung cấp"` (xem [Practical Testing Notes §3](#3-partner_ref_campaign_id-không-được-rỗng-ở-api-2)).

### Response

```json
{
    "status": "success",
    "data": {
        "affiliate_link": "https://me-tracking.dev.accesstrade.me/deep_link/v6/4348611760548105593/4984260100521590721?sub1=504&sub2=231&sub3=sample_template&sub4=oneatapp&url_enc=aHR0cHM6Ly9hdmF5LnZuLz91dG1fY2FtcGFpZ249Y3Bz",
        "short_affiliate_link": "https://me-slink.vpbank.com/taYj3UJV",
        "available_shorten_links": [
            "https://shorten.dev.accesstrade.me"
        ],
        "available_tracking_domains": [
            "tracking.dev.accesstrade.me"
        ]
    },
    "message": "success",
    "code": "PX00000"
}
```

| Field | Type | Mô tả |
|---|---|---|
| `affiliate_link` | String | Link affiliate dài |
| `short_affiliate_link` | String | Link affiliate ngắn |
| `available_shorten_links` | Array | Danh sách shorten link hệ thống hỗ trợ |
| `available_tracking_domains` | Array | Danh sách tracking domain |

---

## API 3.1: Báo cáo Click

Lấy thống kê số lượt click.

- **Method:** `POST`
- **URL:** `{{endpoint}}/pgw-api/tracking-service/api/v1.0/publisher/affiliate/statistics/click`
- **Security:** Xem [Security & Authentication](#security--authentication)

### Request Body

```json
{
    "partner_code": "PARTNER_1_POINT_5",
    "sso_user_id": 504,
    "from_date": "2023-11-01T00:00:00+0700",
    "to_date": "2023-11-30T23:59:59+0700",
    "campaign_ids": [],
    "subs": {
        "sub1": "504",
        "sub2": "231",
        "sub3": "sample_template",
        "sub4": "oneatapp"
    }
}
```

| Field | Type | Mô tả |
|---|---|---|
| `partner_code` | String | Mã partner mặc định |
| `sso_user_id` | Number | Mã định danh người dùng |
| `from_date` | Date | Thời gian bắt đầu lọc |
| `to_date` | Date | Thời gian kết thúc lọc |
| `campaign_ids` | Array | Mã định danh chiến dịch |
| `subs` | Object | Sub tracking (`sub1` — `sub4`) |

> **Lưu ý:**
> - Thời gian lọc tối đa **3 tháng** — vượt quá trả `PX00099`.
> - `from_date`/`to_date` bắt buộc format `YYYY-MM-DDTHH:mm:ss+0700` (không có dấu `:` trong offset). Xem [Practical Testing Notes §1](#1-format-from_date--to_date-bắt-buộc).

### Response

```json
{
    "status": "success",
    "data": {
        "statistics": {
            "1698771600": 0,
            "1698858000": 0,
            "1700931600": 1,
            "1701018000": 1,
            "1701104400": 1,
            "1701190800": 0,
            "1701277200": 0
        },
        "meta": {
            "total": 3
        }
    },
    "message": "success",
    "code": "PX00000"
}
```

| Field | Type | Mô tả |
|---|---|---|
| `statistics` | Object | Dữ liệu trả theo biểu đồ, key là **Epoch time** |
| `meta.total` | Number | Tổng số click |

---

## API 3.2: Báo cáo Conversion

Lấy thống kê đơn hàng (conversion).

- **Method:** `POST`
- **URL:** `{{endpoint}}/pgw-api/conversion-service/api/v1.0/publisher/affiliate/statistics/conversion`
- **Security:** Xem [Security & Authentication](#security--authentication)

### Request Body

Giống [API 3.1](#api-31-báo-cáo-click).

### Response

```json
{
    "status": "success",
    "data": {
        "statistics": {
            "1698796800": 0,
            "1700784000": 2
        },
        "meta": {
            "total": 2
        }
    },
    "message": "success",
    "code": "PX00000"
}
```

| Field | Type | Mô tả |
|---|---|---|
| `statistics` | Object | Dữ liệu conversion theo Epoch time |
| `meta.total` | Number | Tổng số conversion |

---

## API 3.3: Báo cáo Sale Amount

Lấy thống kê giá trị đơn hàng (sale amount).

- **Method:** `POST`
- **URL:** `{{endpoint}}/pgw-api/conversion-service/api/v1.0/publisher/affiliate/statistics/sale-amount`
- **Security:** Xem [Security & Authentication](#security--authentication)

### Request Body

Giống [API 3.1](#api-31-báo-cáo-click).

### Response

```json
{
    "status": "success",
    "data": {
        "statistics": {
            "1700758800": 824
        },
        "meta": {
            "total_pub_sale_amount": 824
        },
        "statistic_details": {
            "REJECTED": {
                "statistics": { "...": 0 },
                "meta": { "total_pub_sale_amount": 0 }
            },
            "WAITING_FOR_APPROVED": {
                "statistics": { "1700758800": 824 },
                "meta": { "total_pub_sale_amount": 824 }
            },
            "APPROVED": {
                "statistics": { "...": 0 },
                "meta": { "total_pub_sale_amount": 0 }
            },
            "TEMPORARY_APPROVED": {
                "statistics": { "...": 0 },
                "meta": { "total_pub_sale_amount": 0 }
            }
        }
    },
    "message": "success",
    "code": "PX00000"
}
```

### Trạng thái đơn hàng

| Status | Mô tả |
|---|---|
| `REJECTED` | Bị hủy |
| `WAITING_FOR_APPROVED` | Chờ duyệt |
| `APPROVED` | Đã duyệt |
| `TEMPORARY_APPROVED` | Tạm duyệt |

---

## API 3.4: Báo cáo Commission (Hoa hồng)

Lấy thống kê hoa hồng (commission).

- **Method:** `POST`
- **URL:** `{{endpoint}}/pgw-api/conversion-service/api/v1.0/publisher/affiliate/statistics/commission`
- **Security:** Xem [Security & Authentication](#security--authentication)

### Request Body

Giống [API 3.1](#api-31-báo-cáo-click).

### Response

Cấu trúc giống [API 3.3: Sale Amount](#api-33-báo-cáo-sale-amount), bao gồm `statistic_details` phân theo trạng thái đơn hàng.

---

## API 6: Báo cáo Tổng hợp

> **Trạng thái:** Chưa cung cấp 1 API chung tổng quát.
>
> Sử dụng các API 3.1 — 3.4 ở trên để xây dựng dashboard tương ứng.

---

## API 7: Webhook (Optional)

> **Trạng thái:** Chưa cung cấp API này.

---

## API 8: Danh sách đơn

Lấy danh sách đơn hàng (conversions) chi tiết.

- **Method:** `POST`
- **URL:** `{{endpoint}}/pgw-api/conversion-service/api/v1.0/publisher/affiliate/conversions`
- **Security:** Xem [Security & Authentication](#security--authentication)

### Request Body

```json
{
    "partner_code": "PARTNER_1_POINT_5",
    "from_date": "2022-10-03T00:00:00+0700",
    "to_date": "2022-12-31T00:00:00+0700",
    "sso_user_id": 504,
    "page": 1,
    "page_size": 20,
    "subs": {
        "sub1": "504",
        "sub2": "231",
        "sub3": "sample_template",
        "sub4": "oneatapp"
    },
    "campaign_ids": [],
    "campaign_invoice_ids": ["098765"]
}
```

| Field | Type | Mô tả |
|---|---|---|
| `partner_code` | String | Mã định danh NCC: `PARTNER_1_POINT_5`, `PARTNER_D2C` |
| `from_date` | Date | Ngày bắt đầu tìm kiếm (Sale date) |
| `to_date` | Date | Ngày kết thúc tìm kiếm (Sale date) |
| `sso_user_id` | Number | Mã định danh người dùng |
| `page` | Number | Trang dữ liệu bắt đầu lấy |
| `page_size` | Number | Kích thước trang dữ liệu |
| `subs` | Object | Sub tracking (`sub1` — `sub4`) |
| `campaign_ids` | Array\<String\> | Mã định danh chiến dịch |
| `campaign_invoice_ids` | Array\<String\> | Mã định danh thanh toán của chiến dịch. **Nếu truyền giá trị này thì không quan tâm `from_date`, `to_date`** |

### Response

```json
{
    "status": "success",
    "data": {
        "conversions": [
            {
                "updated_time": "2023-08-09T11:02:00+0700",
                "partner_code": "PARTNER_1_POINT_5",
                "conversion_id": "AT_TEST_DON_SHOPEE_322_vong_quay_shopee_ATTEMPT_04@shopee",
                "adv_account": "shopee",
                "adv_ref_code": "AT_TEST_DON_SHOPEE_322_vong_quay_shopee_ATTEMPT_04",
                "campaign_id": "4751584435713464237",
                "campaign_name": "Shopee Việt Nam Smartlink cho tất cả thiết bị",
                "total_pub_com": 1500.0,
                "total_product_quantity": 1,
                "total_sale_amount": 150000.0,
                "conversion_sale_time": "2023-03-09T18:12:00+0700",
                "utm": {},
                "sub": {},
                "calculate_status": "CALCULATED",
                "sso_user_id": 504,
                "campaign_invoice_id": "098765"
            }
        ],
        "meta": {
            "page": 1,
            "page_size": 20,
            "total": 1
        }
    },
    "message": "success",
    "code": "PX00000"
}
```

| Field | Type | Mô tả |
|---|---|---|
| `updated_time` | Date | Thời điểm cập nhật đơn |
| `partner_code` | String | Mã định danh nhà cung cấp |
| `conversion_id` | String | Mã định danh đơn hàng |
| `adv_account` | String | Nhà cung cấp tương ứng |
| `adv_ref_code` | String | Mã định danh nhà cung cấp tương ứng |
| `campaign_id` | String | Mã định danh chiến dịch |
| `campaign_name` | String | Tên chiến dịch |
| `total_pub_com` | Number | Hoa hồng phát sinh |
| `total_product_quantity` | Number | Số lượng sản phẩm |
| `total_sale_amount` | Number | Giá trị đơn hàng |
| `conversion_sale_time` | Date | Thời điểm phát sinh đơn |
| `calculate_status` | String | Trạng thái tính toán |
| `sso_user_id` | Number | Mã định danh người dùng |
| `campaign_invoice_id` | String | Mã định danh thanh toán |
| `meta.page` | Number | Trang hiện tại |
| `meta.page_size` | Number | Kích thước trang |
| `meta.total` | Number | Tổng số đơn |
