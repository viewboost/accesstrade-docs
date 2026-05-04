# **Integration API Documentation**

Tài liệu này hướng dẫn cách tích hợp các API của Module Integration dành cho bên thứ 3.

> **Source documents:**
> - Integration APIs (login/campaigns/reports — section 1-3 dưới): nội bộ Scalef
> - **SSO OAuth spec (section 0 dưới):** [Google Doc](https://docs.google.com/document/d/11JTnnXnrR7ENsUn5-7z6-zRCOvnzpKaysgakoj6sqhU/edit?tab=t.0)

---

## **0. SSO OAuth (Authorization Code Flow)**

Dùng cho luồng **liên kết tài khoản creator Gen-Green**: creator bấm "Liên kết Scalef" → redirect sang Scalef SSO → đăng nhập → return về Gen-Green với authorization code → backend đổi code → access token → gọi user info API.

### **0.1. Domains**

| Env | Base URL |
|---|---|
| Staging | `https://sso.directsale.vn/` |
| Dev | `https://sso-dev.directsale.vn/` |
| Production | TBD |

### **0.2. Client credentials (mẫu staging)**

| Key | Value |
|---|---|
| `CLIENT_ID` | `clientapp` |
| `CLIENT_SECRET` | `123456` |

> Production credentials sẽ được Scalef cấp riêng cho Gen-Green tenant.

### **0.3. Standard OAuth2 endpoints**

| Endpoint | URL | Mô tả |
|---|---|---|
| Authorize | `https://<sso-domain>/oauth/authorize` | Redirect user sang Scalef login |
| Login (manual) | `https://<sso-domain>/login` | Trang đăng nhập Scalef (browser thấy) |
| Token | `https://<sso-domain>/oauth/token` | Đổi authorization code → access token |
| Social token | `https://<sso-domain>/oauth/social-token` | Đổi social access token (Google/FB/Apple) → access token |
| Check token | `https://<sso-domain>/oauth/check_token` | Verify token còn hợp lệ |
| User info | `https://<sso-domain>/user/me` | Lấy thông tin user hiện tại |
| Logout | `https://<sso-domain>/logout` | Đăng xuất |

### **0.4. Authorization Code Flow (web login)**

**Step 1 — Generate state**

Client app generate `sessionID` / `uniqueID` random làm `state` parameter (chống CSRF). Lưu vào session để verify ở Step 7.

**Step 2 — Redirect user sang Scalef**

```
https://<sso-domain>/oauth/authorize?
  provider=&
  client_id=clientapp&
  scope=user_info&
  response_type=code&
  redirect_uri=https://pub-portal-dev.mp.directsale.vn/authentication/login&
  state=d473dc0bc3e0c53d7e00df51ec2c2aae5a1cfa2c5b5b3e1d5fced03e1668260f
```

| Param | Mô tả |
|---|---|
| `provider` | Optional. Có thể là `facebook`, `google`, `apple` (nếu user muốn login bằng social qua Scalef). Để trống → user nhập username/password Scalef. |
| `client_id` | Client ID được Scalef cấp |
| `scope` | `user_info` (Gen-Green chỉ cần thông tin user) |
| `response_type` | Bắt buộc `code` |
| `redirect_uri` | URL Gen-Green nhận callback. Phải khớp với URL đã đăng ký với Scalef. |
| `state` | Random string (chống CSRF). Verify ở Step 7. |

**Step 3-5 — User đăng nhập Scalef**

User nhập credentials trên màn Scalef. Scalef xử lý auth.

**Step 6 — Scalef redirect về Gen-Green với authorization code**

```
https://pub-portal-dev.mp.directsale.vn/authentication/login?
  code=LKLCWP&
  state=914e04bbb7eda385162cba3f673f4ad235a989c3b2a1f7fb3398bb1c0eba65c3
```

**Step 7 — Verify state**

Backend Gen-Green compare `state` từ query với `state` lưu ở Step 1. Khác → reject (CSRF attack).

**Step 8 — Đổi code → access token**

```http
POST https://<sso-domain>/oauth/token
Content-Type: application/x-www-form-urlencoded
Authorization: Basic {{auth_token}}

grant_type=authorization_code
code=LKLCWP
redirect_uri=https://pub-portal-dev.mp.directsale.vn/authentication/login
```

`{{auth_token}}` = `base64(client_id + ":" + client_secret)` — VD `base64("clientapp:123456")` = `Y2xpZW50YXBwOjEyMzQ1Ng==`

**Response:**

```json
{
  "token_type": "bearer",
  "access_token": "bb21fd49-6ae1-4e01-9b03-a1565f2ac236",
  "refresh_token": "f29decd1-9aed-4688-8f2d-1b3493cde7ab",
  "refresh_token_value": "f29decd1-9aed-4688-8f2d-1b3493cde7ab",
  "refresh_token_expires_in": 14399,
  "refresh_token_expires_at": "2023-02-17T13:18:18+0000",
  "expires_in": 9599,
  "expires_at": "2023-02-17T11:58:18+0000",
  "scope": "user_info read write",
  "user_id": 108,
  "user_name": "pub_4",
  "is_active": true,
  "phone": "+84921234568",
  "email": "pub_4_12@interspace.vn"
}
```

> Response `/oauth/token` đã trả luôn `user_id`, `user_name`, `phone`, `email` — Gen-Green có thể dùng trực tiếp để matching với Gen-Green user, **không bắt buộc gọi `/user/me`**. CCCD chưa thấy trong response — cần confirm với Scalef nếu cần CCCD cho luồng identity matching.

### **0.5. Grant types khác**

#### Password grant (API login — backend-to-backend)

```http
POST https://<sso-domain>/oauth/token
Content-Type: application/x-www-form-urlencoded
Authorization: Basic Y2xpZW50YXBwOjEyMzQ1Ng==

grant_type=password
username=pub_4
password=12345678
```

#### Refresh token grant

```http
POST https://<sso-domain>/oauth/token
Content-Type: application/x-www-form-urlencoded
Authorization: Basic Y2xpZW50YXBwOjEyMzQ1Ng==

grant_type=refresh_token
refresh_token=f29decd1-9aed-4688-8f2d-1b3493cde7ab
```

#### Social grant (đổi social access token → Scalef access token)

```http
POST https://<sso-domain>/oauth/social-token
Content-Type: application/x-www-form-urlencoded
Authorization: Basic Y2xpZW50YXBwOjEyMzQ1Ng==

grant_type=social
provider=google
app_id=null
access_token=ya29.a0AVvZVsq6ATZVuc2x4VlbO...
```

| Param | Mô tả |
|---|---|
| `provider` | `google` / `facebook` / `apple` |
| `app_id` | Bắt buộc khi `provider=facebook` |
| `access_token` | **Access token** thật từ provider, **không phải** Bearer token hay ID token |

> Verify Google access token: `curl "https://oauth2.googleapis.com/tokeninfo?access_token=ACCESS_TOKEN"`

### **0.6. Verify access token**

```http
GET https://<sso-domain>/oauth/check_token?token=aee44b00-9aab-4a1a-a7e7-bdb6e02a50ae
Content-Type: application/x-www-form-urlencoded
Authorization: Basic Y2xpZW50YXBwOjEyMzQ1Ng==
```

**Response:**

```json
{
  "user_name": "pub_1",
  "scope": ["user_info", "read", "write"],
  "authorities": ["ROLE_USER"],
  "refresh_token_value": "5ef4011d-835a-469b-bb7d-e17f475b7d4b",
  "refresh_token_expires_in": 883999,
  "refresh_token_expires_at": "2022-11-18T21:16:00+0700",
  "expires_at": "2022-11-09T00:02:40+0700",
  "exp": 1667926960,
  "aud": ["restservice"],
  "client_id": "clientapp"
}
```

### **0.7. APIs khác (sau khi có access token)**

Base URL: `http://domain.com/api/v1`

Header chung:
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

| API | Method | Mô tả | Role |
|---|---|---|---|
| `/user/logout` | GET | Logout user | User |
| `/user/{action}` | POST | createUser / editUser / updateUser / getUser / activeUser / inactiveUser / findUsers | Admin (User chỉ editUser được) |
| `/role/{action}` | POST | createRole / updateRole / getRole / activeRole / inactiveRole / findRoles | System, Admin (read-only) |
| `/permission/{action}` | POST | createPermission / updatePermission / getPermission / activePermission / inactivePermission / findPermissions | System, Admin (read-only) |

### **0.8. OAuth2 client examples (reference)**

- PHP: https://oauth.net/code/php/
- GitHub sample: https://github.com/aaronpk/sample-oauth2-client
- Python: https://github.com/joestump/python-oauth2
- Java (Spring Boot): https://github.com/spring-guides/tut-spring-boot-oauth2

### **0.9. Security notes (cho Gen-Green)**

- **State parameter bắt buộc** (Step 1 + Step 7) — chống CSRF
- **Access token / Client secret KHÔNG được lộ ra browser** — Gen-Green backend giữ
- **Authorization code chỉ dùng 1 lần** — sau khi đổi token thì code invalid
- `client_secret` mẫu (`123456`) là cho dev/staging — **production phải đổi**
- More info: https://www.oauth.com/oauth2-servers/access-tokens/

---

## **1. Thông tin chung**

- **Base URL**: `http://mp-publisher-backend.test/api/integration/v1`
- **Xác thực**:
    - Đối với **Login**: Sử dụng `INTEGRATION_CLIENT_ID` và `INTEGRATION_CLIENT_SECRET`.
    - Đối với **Các API khác**: Sử dụng `INTEGRATION_CLIENT_SECRET` và `X-Ref-User-Id` của người dùng.
- **Header bắt buộc**: `X-Port-Type: PUB` cho toàn bộ các request.
- **Thuật toán Signature**: HMAC-SHA256.

## **2. Xác thực & Headers**

### **2.1. Header cho API Đăng nhập (Login)**

| Header | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `X-Port-Type` | `string` | Bắt buộc là `PUB`. |
| `X-Client-Id` | `string` | Client ID được cấp (cấu hình trong `.env`). |
| `X-Timestamp` | `int` | Unix timestamp hiện tại. |
| `X-Signature` | `string` | Chữ ký HMAC-SHA256. |

**Công thức Signature Login:** `hash_hmac('sha256', timestamp + client_id, client_secret)`

### **2.2. Header cho các API khác (Campaign, Report,...)**

| Header | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `X-Port-Type` | `string` | Bắt buộc là `PUB`. |
| `X-Client-Id` | `string` | Client ID được cấp. |
| `X-Ref-User-Id` | `string`/`int` | ID của người dùng trên hệ thống Scalef. |
| `X-Timestamp` | `int` | Unix timestamp hiện tại. |
| `X-Signature` | `string` | Chữ ký HMAC-SHA256. |

**Công thức Signature API thường:** `hash_hmac('sha256', timestamp + ref_user_id, client_secret)`

---

## **3. Danh sách API**

### **3.1. Đăng nhập (Login)**

Xác thực thông tin tài khoản của người dùng.

- **Endpoint**: `/login-account`
- **Method**: `POST`
- **Body**:


    | Tham số | Kiểu | Bắt buộc | Mô tả |
    | --- | --- | --- | --- |
    | `username` | `string` | Có | Tên đăng nhập của người dùng. |
    | `password` | `string` | Có | Mật khẩu của người dùng. |
- **Response (Thành công)**:

    ```json
    {
      "status": "success",
      "data": {
          "username": "partner_user",
          "phone": "0987654321",
          "email": "user@example.com",
          "sso_scalef_id": 12345,
          "core_user_id": 229277
      }
    }
    ```


### **3.2. Danh sách chiến dịch**

Lấy danh sách các chiến dịch mà người dùng có thể nhìn thấy.

- **Endpoint**: `/campaigns`
- **Method**: `GET`
- **Query Params**:


    | Param | Kiểu dữ liệu | Mô tả |
    | --- | --- | --- |
    | `page` | `integer` | Trang hiện tại (mặc định 1). |
    | `page_size` | `integer` | Số lượng record mỗi trang. |
    | `filters[name]` | `string` | Tìm kiếm theo tên chiến dịch. |

### **3.3. Chi tiết chiến dịch**

Lấy thông tin chi tiết của một chiến dịch cụ thể.

- **Endpoint**: `/campaigns/{id}`
- **Method**: `GET`
- **Tham số đường dẫn (Path Params)**:


    | Tham số | Kiểu | Mô tả |
    | --- | --- | --- |
    | `id` | `integer` | ID của chiến dịch cần lấy thông tin. |
- **Response (Thành công)**:

    ```json
    {
      "status": "success",
      "data": {
          "id": 1690,
          "code": "CAMP123",
          "name": "Campaign Name",
          "url": "https://offer.vn",
          "description": "Mô tả về chiến dịch...",
          "status": {
              "id": 2,
              "code": "ACTIVATED",
              "name": "Activated"
          },
          "domain": "offer.vn",
          "started_at": "2024-01-01",
          "ended_at": "2025-01-01",
          "logo": "https://statics-cdn.affgrow.com/...",
          "categories": []
      }
    }
    ```


### **3.4. Tham gia chiến dịch (Join)**

Đăng ký tham gia một chiến dịch. Hệ thống sẽ tự động tạo Ad Space mặc định nếu người dùng chưa có.

- **Endpoint**: `/campaigns/join`
- **Method**: `POST`
- **Body**:


    | Tham số | Kiểu | Bắt buộc | Mô tả |
    | --- | --- | --- | --- |
    | `campaign_id` | `integer` | Có | ID của chiến dịch muốn tham gia. |
- **Response (Thành công)**:

    ```json
    {
      "status": "success",
      "data": {
          "contract": {
              "id": 5566,
              "code": "CON_XYZ",
              "campaign_id": 1690,
              "status": 1,
              "publisher_status": 1,
              "advertiser_status": 0,
              "created_at": "2024-04-20 09:45:00",
              "updated_at": "2024-04-20 09:45:00"
          }
      }
    }
    ```


###

```json
{
  "status": "success",
  "data": {
      "deeplink": "https://pub.accesstrade.vn/deep_link/...",
      "short_link": "https://at.link/xyz123"
  }
}
```

### **3.5. Tạo link Affiliate**

- **Endpoint**: `/campaigns/generate-link`
- **Method**: `POST`
- **Body**:


    | Tham số | Kiểu | Bắt buộc | Mô tả |
    | --- | --- | --- | --- |
    | `campaign_id` | `integer` | Có | ID của chiến dịch cần tạo link. |
    | `utm_source` | `string` | Không | Nguồn truy cập (ví dụ: facebook, google). |
    | `utm_medium` | `string` | Không | Phương thức quảng cáo. |
    | `utm_campaign` | `string` | Không | Tên chiến dịch marketing. |
    | `sub_1` | `string` | Không | Tham số Sub ID 1 để tracking. |
    | `sub_2` | `string` | Không | Tham số Sub ID 2. |
- **Ví dụ Request**:

    ```bash
    curl 'https://mp-publisher-backend.test/api/integration/v1/campaigns/generate-link' \
      -H 'X-Port-Type: PUB' \
      -H 'Content-Type: application/json' \
      --data-raw '{"campaign_id": 229, "utm_source": "facebook", "sub_1": "ad01"}'
    ```

- **Response**:

    ```json
    {
      "status": "success",
      "data": {
          "deeplink": "https://pub.accesstrade.vn/deep_link/...",
          "short_link": "https://at.link/xyz123"
      }
    }
    ```


### **3.6. Báo cáo Click**

Lấy thông tin so sánh click giữa 2 khoảng thời gian.

- **Endpoint**: `/report/click`
- **Method**: `POST`
- **Body**:


    | Tham số | Kiểu | Bắt buộc | Mô tả |
    | --- | --- | --- | --- |
    | `from_date` | `string` | Có | Ngày bắt đầu (Y-m-d). |
    | `to_date` | `string` | Có | Ngày kết thúc (Y-m-d). |
    | `campaigns` | `string` | Không | Danh sách ID chiến dịch (phân tách bằng dấu phẩy). |
    | `field` | `string` | Không | Trường dữ liệu cần lấy (mặc định: `total_conversion`). |
- **Ví dụ Request**:

    ```bash
    curl 'https://mp-publisher-backend.test/api/integration/v1/report/click' \
      -H 'X-Port-Type: PUB' \
      -H 'X-Client-Id: your_client_id' \
      -H 'X-Ref-User-Id: 229277' \
      -H 'X-Timestamp: 1713580800' \
      -H 'X-Signature: your_signature' \
      -H 'Content-Type: application/json' \
      --data-raw '{"field":"total_conversion","from_date":"2026-04-13","to_date":"2026-04-20","campaigns":""}'
    ```

- **Ví dụ Response**:

    ```json
    {
        "status": "success",
        "data": {
            "report": {
                "current": {
                    "report_data": [
                        { "unit": "1776013200000", "count_total": 0 },
                        { "unit": "1776099600000", "count_total": 0 },
                        { "unit": "1776186000000", "count_total": 1 },
                        { "unit": "1776272400000", "count_total": 2 },
                        { "unit": "1776358800000", "count_total": 1 },
                        { "unit": "1776445200000", "count_total": 0 },
                        { "unit": "1776531600000", "count_total": 0 }
                    ]
                },
                "compare": {
                    "report_data": []
                }
            }
        }
    }
    ```


### **3.7. Báo cáo tổng quan (Overview)**

- **Endpoint**: `/report/overview`
- **Method**: `POST`
- **Body**: Giống API Report Click.
- **Ví dụ Request**:

    ```bash
    curl 'https://mp-publisher-backend.test/api/integration/v1/report/overview' \
      -H 'X-Port-Type: PUB' \
      -H 'Content-Type: application/json' \
      --data-raw '{"field":"total_conversion","from_date":"2026-04-13","to_date":"2026-04-20","campaigns":""}'
    ```

- **Ví dụ Response**:

    ```json
    {
        "status": "success",
        "data": {
            "report": {
                "current": {
                    "status": "all",
                    "from_date": "2026/04/13",
                    "to_date": "2026/04/20",
                    "total_count": 4400,
                    "group_by": "day",
                    "data_group": [
                        { "unit": "1776013200000", "value": 0 },
                        { "unit": "1776186000000", "value": 110000 }
                    ],
                    "meta": {
                        "conversion": {
                            "total": 1100,
                            "approved": 0,
                            "pre_approved": 3,
                            "pending": 1097,
                            "rejected": 0,
                            "hold": 0
                        },
                        "pub_commission": {
                            "total": 110000,
                            "approved": 0,
                            "pre_approved": 300,
                            "pending": 109700
                        }
                    }
                },
                "compare": {
                    "status": "all",
                    "total_count": 0,
                    "data_group": []
                }
            }
        }
    }
    ```


### **3.8. Báo cáo Chuyển đổi (Conversion Report)**

Lấy danh sách chuyển đổi dựa trên các bộ lọc (thời gian, chiến dịch, trạng thái, UTM, Sub ID).

- **Endpoint**: `/publisher/conversion`
- **Method**: `GET`
- **Ghi chú**:
    - Tham số thời gian là **bắt buộc**.
    - Khoảng thời gian tìm kiếm (`from` đến `to`) tối đa là **90 ngày (3 tháng)**.
- **Query Parameters**:


    | Tham số | Kiểu | Bắt buộc | Mô tả |
    | --- | --- | --- | --- |
    | `from_time` | string | Có* | Thời gian bắt đầu (Y-m-d H:i:s). |
    | `to_time` | string | Có* | Thời gian kết thúc (Y-m-d H:i:s). |
    | `from_date` | string | Có* | Ngày bắt đầu (Y-m-d), dùng nếu không có from_time. |
    | `to_date` | string | Có* | Ngày kết thúc (Y-m-d), dùng nếu không có to_time. |
    | `campaign_id` | integer | Không | Lọc theo ID chiến dịch. |
    | `order_id` | string | Không | Lọc theo ID đơn hàng. |
    | `status` | string | Không | Lọc theo trạng thái chuyển đổi. |
    | `page` | integer | Không | Số trang hiện tại (Mặc định: 1). |
    | `page_size` | integer | Không | Số bản ghi mỗi trang (Mặc định: 20). |
- *Bắt buộc phải có cặp (from_date & to_date) hoặc (from_time & to_time).*
- **Ví dụ Request**:

    ```bash
    curl 'https://mp-publisher-backend.test/api/integration/v1/publisher/conversion?from_date=2026-04-01&to_date=2026-04-20&page=1' \
      -H 'X-Port-Type: PUB' \
      -H 'X-Ref-User-Id: 229277' \
      -H 'X-Timestamp: 1713580800' \
      -H 'X-Signature: your_signature'
    ```

- **Response**:

    ```json
    {
      "status": "success",
      "data": {
          "conversions": [
              {
                  "conversion_id": "69defb79...",
                  "click_id": "1a060ff3...",
                  "campaign_id": "229",
                  "campaign_code": "CAM000000229",
                  "order_id": "ord123...",
                  "status": "pre_approved",
                  "action_date_time": "2026-04-15T09:44:06+0700",
                  "total_sale_amount": {
                      "amount": 264000,
                      "currency": "VND"
                  },
                  "total_commission": {
                      "amount": 1100,
                      "currency": "VND"
                  },
                  "conversion_parts": [
                      {
                          "sku": "KUA",
                          "name": "But bi xanh",
                          "quantity": 1,
                          "price": 100000,
                          "sale_amount": 90000,
                          "commission": { "amount": 1100, "currency": "VND" },
                          "status": "pre_approved",
                          "category_name": "but"
                      }
                  ],
                  "created_time": "2026-04-15T09:44:09+0700",
                  "updated_time": "2026-04-16T14:05:49+0700"
              }
          ],
          "meta": {
              "total": 1,
              "per_page": 20,
              "current_page": 1,
              "last_page": 1
          }
      }
    }
    ```
