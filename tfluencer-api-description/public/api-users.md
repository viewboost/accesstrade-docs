# API Users - Tài liệu test API

---

## Danh sách API

### Đăng ký / Đăng nhập (Không cần auth)

| # | Method | Endpoint | Mô tả |
|---|--------|----------|-------|
| 1 | POST | `/users/register` | Đăng ký tài khoản |
| 2 | POST | `/users/login` | Đăng nhập email/password |
| 3 | POST | `/users/login-with-google` | Đăng nhập Google |
| 4 | POST | `/users/login-with-tiktok` | Đăng nhập TikTok |
| 5 | POST | `/users/login-with-instagram` | Đăng nhập Instagram |
| 6 | POST | `/users/login-with-facebook` | Đăng nhập Facebook |
| 7 | GET | `/users/by-referral-code` | Lấy thông tin user qua referral code |

### Profile & Tài khoản (Bắt buộc auth)

| # | Method | Endpoint | Mô tả |
|---|--------|----------|-------|
| 8 | GET | `/users/me` | Thông tin user hiện tại |
| 9 | PUT | `/users/update` | Cập nhật profile |
| 10 | POST | `/users/device` | Đăng ký device token (FCM) |
| 11 | POST | `/users/logout` | Đăng xuất |
| 12 | POST | `/users/verify-otp` | Xác thực OTP |
| 13 | POST | `/users/request-otp` | Yêu cầu gửi OTP |
| 14 | POST | `/users/confirm-is-staff` | Xác nhận là nhân viên |
| 15 | POST | `/users/referral` | Nhập mã giới thiệu |

### Publisher

| # | Method | Endpoint | Mô tả |
|---|--------|----------|-------|
| 16 | POST | `/users/publisher` | Tạo publisher |
| 17 | GET | `/users/publisher` | Lấy thông tin publisher |

### Bank Cards

| # | Method | Endpoint | Mô tả |
|---|--------|----------|-------|
| 18 | GET | `/users/bank-cards` | Danh sách thẻ ngân hàng |
| 19 | POST | `/users/bank-cards` | Thêm thẻ ngân hàng |
| 20 | PUT | `/users/bank-cards/:id` | Cập nhật thẻ |
| 21 | PUT | `/users/bank-cards/:id/set-default` | Đặt thẻ mặc định |

### CMND / CCCD

| # | Method | Endpoint | Mô tả |
|---|--------|----------|-------|
| 22 | POST | `/users/identification` | Tạo giấy tờ tuỳ thân |
| 23 | GET | `/users/identification/me` | Xem giấy tờ của tôi |
| 24 | PUT | `/users/identification/:id` | Cập nhật giấy tờ |
| 25 | POST | `/users/identification/image` | Trích xuất ảnh CMND/CCCD |

### Hợp đồng

| # | Method | Endpoint | Mô tả |
|---|--------|----------|-------|
| 26 | POST | `/users/contract/info` | Tạo/cập nhật thông tin hợp đồng |
| 27 | POST | `/users/contract/estimate` | Xem hợp đồng mẫu |
| 28 | GET | `/users/contract/pre-signed` | Lấy URL ký hợp đồng |

### Cash Flow

| # | Method | Endpoint | Mô tả |
|---|--------|----------|-------|
| 29 | GET | `/users/cash-flow` | Lịch sử giao dịch |

### Social Accounts

| # | Method | Endpoint | Mô tả |
|---|--------|----------|-------|
| 30 | GET | `/users/socials` | Danh sách tài khoản social |
| 31 | GET | `/users/socials/:id` | Chi tiết tài khoản social |
| 32 | GET | `/users/socials/statistics` | Thống kê social |
| 33 | GET | `/users/socials/stats` | Stats tổng quan social |
| 34 | POST | `/users/socials/:id/demographics` | Cập nhật demographics |
| 35 | POST | `/users/socials/link` | Liên kết tài khoản social |

### Khác

| # | Method | Endpoint | Mô tả |
|---|--------|----------|-------|
| 36 | GET | `/users/service-tos/redirect-url` | URL điều khoản dịch vụ |

---

## 1. Đăng ký

```
POST {{BASE_URL}}/users/register
```

**Headers:**

```
Content-Type: application/json
X-Device-ID: {{DEVICE_ID}}
Accept-Language: vi
```

**Body:**

```json
{
  "name": "Nguyễn Văn A",
  "email": "user1@example.com",
  "phone": "0900000001",
  "password": "P@ssw0rd123",
  "confirmPassword": "P@ssw0rd123",
  "gender": "M",
  "city": 79,
  "ref": "REF_CODE"
}
```

| Tên | Kiểu | Bắt buộc | Validation |
|-----|------|----------|------------|
| name | string | **Có** | Tối thiểu 3 ký tự |
| email | string | **Có** | Email hợp lệ |
| phone | string | **Có** | Regex: `^(0|\+84)[0-9]{9,10}$` |
| password | string | **Có** | Tối thiểu 6 ký tự |
| confirmPassword | string | **Có** | Phải khớp `password` |
| gender | string | Không | `M` hoặc `F` |
| city | number | Không | Mã tỉnh/thành |
| ref | string | Không | Mã giới thiệu |

**cURL:**

```bash
curl -X POST "{{BASE_URL}}/users/register" \
  -H "Content-Type: application/json" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Accept-Language: vi" \
  -d '{
    "name": "Nguyễn Văn A",
    "email": "user1@example.com",
    "phone": "0900000001",
    "password": "P@ssw0rd123",
    "confirmPassword": "P@ssw0rd123",
    "gender": "M"
  }'
```

**Response 200:**

```json
{
  "data": {
    "_id": "660a1b2c3d4e5f6a7b8c9d01",
    "isFirstLogin": true,
    "isNewUser": true,
    "token": "eyJhbGciOiJIUzI1NiIs..."
  },
  "code": 200
}
```

> **Lưu ý:** Lưu `token` làm `{{TOKEN}}` cho các request tiếp theo.

**Test lỗi:**

```bash
# Thiếu email → 400
curl -X POST "{{BASE_URL}}/users/register" \
  -H "Content-Type: application/json" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -d '{"name": "Test", "phone": "0900000001", "password": "123456", "confirmPassword": "123456"}'

# Password không khớp → 400
curl -X POST "{{BASE_URL}}/users/register" \
  -H "Content-Type: application/json" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -d '{"name": "Test", "email": "test@test.com", "phone": "0900000001", "password": "123456", "confirmPassword": "654321"}'

# Phone sai format → 400
curl -X POST "{{BASE_URL}}/users/register" \
  -H "Content-Type: application/json" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -d '{"name": "Test", "email": "test@test.com", "phone": "123", "password": "123456", "confirmPassword": "123456"}'
```

---

## 2. Đăng nhập

```
POST {{BASE_URL}}/users/login
```

**Headers:**

```
Content-Type: application/json
X-Device-ID: {{DEVICE_ID}}
Accept-Language: vi
```

**Body:**

```json
{
  "email": "user1@example.com",
  "password": "P@ssw0rd123"
}
```

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| email | string | **Có** | Email đã đăng ký |
| password | string | **Có** | Mật khẩu |

**cURL:**

```bash
curl -X POST "{{BASE_URL}}/users/login" \
  -H "Content-Type: application/json" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Accept-Language: vi" \
  -d '{
    "email": "user1@example.com",
    "password": "P@ssw0rd123"
  }'
```

**Response 200:**

```json
{
  "data": {
    "_id": "660a1b2c3d4e5f6a7b8c9d01",
    "isFirstLogin": false,
    "isNewUser": false,
    "token": "eyJhbGciOiJIUzI1NiIs..."
  },
  "code": 200
}
```

> **Quan trọng:** `X-Device-ID` gửi khi login **phải giống** `X-Device-ID` ở tất cả request sau. Nếu khác → 401.

---

## 3. Đăng nhập Google

```
POST {{BASE_URL}}/users/login-with-google
```

**Headers:**

```
Content-Type: application/json
X-Device-ID: {{DEVICE_ID}}
Accept-Language: vi
```

**Body:**

```json
{
  "token": "google_access_token_here"
}
```

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| token | string | **Có** | Google access token |

**cURL:**

```bash
curl -X POST "{{BASE_URL}}/users/login-with-google" \
  -H "Content-Type: application/json" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -d '{"token": "google_access_token_here"}'
```

**Response 200:** Giống [API #2](#2-đăng-nhập).

---

## 4. Đăng nhập TikTok

```
POST {{BASE_URL}}/users/login-with-tiktok
```

**Headers:**

```
Content-Type: application/json
X-Device-ID: {{DEVICE_ID}}
Accept-Language: vi
```

**Body:**

```json
{
  "code": "tiktok_oauth_code",
  "redirectURI": "https://yourapp.com/callback"
}
```

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| code | string | **Có** | OAuth authorization code |
| redirectURI | string | Không | Redirect URI |

**cURL:**

```bash
curl -X POST "{{BASE_URL}}/users/login-with-tiktok" \
  -H "Content-Type: application/json" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -d '{"code": "tiktok_oauth_code", "redirectURI": "https://yourapp.com/callback"}'
```

**Response 200:** Giống [API #2](#2-đăng-nhập).

---

## 5. Đăng nhập Instagram

```
POST {{BASE_URL}}/users/login-with-instagram
```

**Body:**

```json
{
  "token": "instagram_access_token"
}
```

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| token | string | **Có** | Instagram access token |

**cURL:**

```bash
curl -X POST "{{BASE_URL}}/users/login-with-instagram" \
  -H "Content-Type: application/json" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -d '{"token": "instagram_access_token"}'
```

---

## 6. Đăng nhập Facebook

```
POST {{BASE_URL}}/users/login-with-facebook
```

**Body:**

```json
{
  "token": "facebook_access_token"
}
```

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| token | string | **Có** | Facebook access token |

**cURL:**

```bash
curl -X POST "{{BASE_URL}}/users/login-with-facebook" \
  -H "Content-Type: application/json" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -d '{"token": "facebook_access_token"}'
```

---

## 7. Lấy thông tin User qua Referral Code

```
GET {{BASE_URL}}/users/by-referral-code
```

> Không cần đăng nhập.

**Headers:**

```
Accept-Language: vi
```

**Query params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| code | string | **Có** | Referral code |

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/users/by-referral-code?code=REF_ABC123" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": {
    "_id": "660a1b2c3d4e5f6a7b8c9d01",
    "name": "Nguyễn Văn A",
    "avatar": "https://cdn.example.com/avatar.jpg",
    "code": "REF_ABC123",
    "inviter": {
      "_id": "user_000",
      "name": "Người giới thiệu"
    }
  },
  "code": 200
}
```

---

## 8. Thông tin User hiện tại

```
GET {{BASE_URL}}/users/me
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (BẮT BUỘC)
X-Device-ID: {{DEVICE_ID}}              (BẮT BUỘC)
Accept-Language: vi
```

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/users/me" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": {
    "_id": "660a1b2c3d4e5f6a7b8c9d01",
    "name": "Nguyễn Văn A",
    "phone": {
      "number": "0900000001",
      "isVerified": true
    },
    "info": {
      "email": "user1@example.com",
      "cityCode": 79,
      "cityName": "Hồ Chí Minh",
      "gender": "M",
      "birthDay": "1995-01-15",
      "occupation": "Developer"
    },
    "avatar": {
      "url": "https://cdn.example.com/avatar.jpg"
    },
    "statistic": {
      "totalRemaining": 2500000.0,
      "totalCash": 5000000.0,
      "totalCashPending": 500000.0,
      "totalCashRejected": 0,
      "totalCashCompleted": 4500000.0
    },
    "identification": {
      "_id": "id_001",
      "status": "approved",
      "taxNumber": "0000000000",
      "identificationNumber": "000000000000"
    },
    "contract": {
      "phone": "0900000001",
      "name": "Nguyễn Văn A"
    },
    "totalNotificationUnseen": 3,
    "code": "REF_ABC123",
    "google": {
      "email": "user1@example.com"
    },
    "tiktok": null,
    "facebook": null,
    "socialInfo": {
      "photo": "https://cdn.example.com/social.jpg",
      "status": "active"
    },
    "hashtag": "#TFluencers",
    "contractTOS": {
      "contractId": "contract_001",
      "status": "signed",
      "signedAt": "2026-01-10T08:00:00Z"
    },
    "referralByCode": "REF_XYZ",
    "createdAt": "2025-06-01T00:00:00Z",
    "updatedAt": "2026-03-18T10:00:00Z"
  },
  "code": 200
}
```

---

## 9. Cập nhật Profile

```
PUT {{BASE_URL}}/users/update
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (BẮT BUỘC)
X-Device-ID: {{DEVICE_ID}}              (BẮT BUỘC)
Content-Type: application/json
Accept-Language: vi
```

**Body:**

```json
{
  "name": "Nguyễn Văn B",
  "gender": "M",
  "email": "user2@example.com",
  "birthDay": "1995-01-15",
  "cityCode": 79,
  "occupation": "Marketing",
  "avatar": {
    "url": "https://cdn.example.com/new-avatar.jpg"
  }
}
```

| Tên | Kiểu | Bắt buộc | Validation |
|-----|------|----------|------------|
| name | string | Không | — |
| gender | string | **Có** | `M` hoặc `F` |
| email | string | Không | Email hợp lệ (nếu có) |
| birthDay | string | Không | Date string |
| cityCode | number | Không | Mã tỉnh/thành |
| occupation | string | Không | — |
| avatar | object | Không | `{ "url": "..." }` |

**cURL:**

```bash
curl -X PUT "{{BASE_URL}}/users/update" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -H "Accept-Language: vi" \
  -d '{"name": "Nguyễn Văn B", "gender": "M"}'
```

**Response 200:**

```json
{
  "data": {},
  "code": 200
}
```

---

## 10. Đăng ký Device Token

```
POST {{BASE_URL}}/users/device
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (BẮT BUỘC)
X-Device-ID: {{DEVICE_ID}}              (BẮT BUỘC)
Content-Type: application/json
```

**Body:**

```json
{
  "deviceToken": "fcm_token_abc123xyz",
  "platform": "web"
}
```

| Tên | Kiểu | Bắt buộc | Validation |
|-----|------|----------|------------|
| deviceToken | string | **Có** | FCM token |
| platform | string | **Có** | `web` / `ios` / `android` |

**cURL:**

```bash
curl -X POST "{{BASE_URL}}/users/device" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{"deviceToken": "fcm_token_abc123xyz", "platform": "web"}'
```

**Response 200:**

```json
{
  "data": {},
  "code": 200
}
```

---

## 11. Đăng xuất

```
POST {{BASE_URL}}/users/logout
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (BẮT BUỘC)
X-Device-ID: {{DEVICE_ID}}              (BẮT BUỘC)
Content-Type: application/json
```

**Body:**

```json
{
  "deviceToken": "fcm_token_abc123xyz"
}
```

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| deviceToken | string | Không | FCM token cần xoá |

**cURL:**

```bash
curl -X POST "{{BASE_URL}}/users/logout" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{"deviceToken": "fcm_token_abc123xyz"}'
```

**Response 200:**

```json
{
  "data": {},
  "code": 200
}
```

---

## 12. Xác thực OTP

```
POST {{BASE_URL}}/users/verify-otp
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (BẮT BUỘC)
X-Device-ID: {{DEVICE_ID}}              (BẮT BUỘC)
Content-Type: application/json
```

**Body:**

```json
{
  "code": "123456"
}
```

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| code | string | **Có** | Mã OTP |

**cURL:**

```bash
curl -X POST "{{BASE_URL}}/users/verify-otp" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{"code": "123456"}'
```

**Response 200:**

```json
{
  "data": {},
  "code": 200
}
```

---

## 13. Yêu cầu gửi OTP

```
POST {{BASE_URL}}/users/request-otp
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (BẮT BUỘC)
X-Device-ID: {{DEVICE_ID}}              (BẮT BUỘC)
Content-Type: application/json
```

**Body:**

```json
{
  "purpose": "verify_phone"
}
```

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| purpose | string | **Có** | Mục đích gửi OTP |

**cURL:**

```bash
curl -X POST "{{BASE_URL}}/users/request-otp" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{"purpose": "verify_phone"}'
```

**Response 200:**

```json
{
  "data": {
    "channel": "sms"
  },
  "code": 200
}
```

---

## 14. Xác nhận là nhân viên

```
POST {{BASE_URL}}/users/confirm-is-staff
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (BẮT BUỘC)
X-Device-ID: {{DEVICE_ID}}              (BẮT BUỘC)
Content-Type: application/json
```

**Body:**

```json
{
  "partner": "partner_001",
  "isStaff": true,
  "code": "STAFF_CODE_123"
}
```

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| partner | string | **Có** | Partner ID |
| isStaff | boolean | Không | Xác nhận là staff |
| code | string | Không | Staff code |

**cURL:**

```bash
curl -X POST "{{BASE_URL}}/users/confirm-is-staff" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{"partner": "partner_001", "isStaff": true, "code": "STAFF_CODE_123"}'
```

**Response 200:**

```json
{
  "data": {},
  "code": 200
}
```

---

## 15. Nhập mã giới thiệu

```
POST {{BASE_URL}}/users/referral
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (BẮT BUỘC)
X-Device-ID: {{DEVICE_ID}}              (BẮT BUỘC)
Content-Type: application/json
```

**Body:**

```json
{
  "ref": "REF_ABC123"
}
```

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| ref | string | **Có** | Mã giới thiệu (sẽ tự chuyển lowercase) |

**cURL:**

```bash
curl -X POST "{{BASE_URL}}/users/referral" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{"ref": "REF_ABC123"}'
```

**Response 200:**

```json
{
  "data": {},
  "code": 200
}
```

---

## 16. Tạo Publisher

```
POST {{BASE_URL}}/users/publisher
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (BẮT BUỘC)
X-Device-ID: {{DEVICE_ID}}              (BẮT BUỘC)
Content-Type: application/json
```

**Body:**

```json
{
  "name": "Kênh của Nguyễn Văn A",
  "desc": "Kênh review tài chính cá nhân"
}
```

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| name | string | **Có** | Tên publisher |
| desc | string | **Có** | Mô tả |
| channel | object | Không | Thông tin kênh |

**cURL:**

```bash
curl -X POST "{{BASE_URL}}/users/publisher" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{"name": "Kênh của Nguyễn Văn A", "desc": "Kênh review tài chính"}'
```

**Response 200:**

```json
{
  "data": {
    "_id": "pub_001",
    "name": "Kênh của Nguyễn Văn A",
    "desc": "Kênh review tài chính",
    "createdAt": "2026-03-18T10:00:00Z",
    "updatedAt": "2026-03-18T10:00:00Z"
  },
  "code": 200
}
```

---

## 17. Lấy thông tin Publisher

```
GET {{BASE_URL}}/users/publisher
```

> **BẮT BUỘC ĐĂNG NHẬP**

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/users/publisher" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}"
```

---

## 18. Danh sách Thẻ ngân hàng

```
GET {{BASE_URL}}/users/bank-cards
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (BẮT BUỘC)
X-Device-ID: {{DEVICE_ID}}              (BẮT BUỘC)
Accept-Language: vi
```

**Query params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| pageToken | string | Không | Token phân trang |
| keyword | string | Không | Tìm kiếm |

> Default limit: 20

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/users/bank-cards" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}"
```

**Response 200:**

```json
{
  "data": [
    {
      "_id": "card_001",
      "bank": {
        "_id": "bank_001",
        "name": "Techcombank",
        "shortName": "TCB",
        "logo": { "url": "..." }
      },
      "branch": "branch_001",
      "branchName": "Chi nhánh HCM",
      "cardNumber": "0000000000000000",
      "cardHolderName": "NGUYEN VAN A",
      "isDefault": true
    }
  ],
  "nextPageToken": "",
  "code": 200
}
```

---

## 19. Thêm Thẻ ngân hàng

```
POST {{BASE_URL}}/users/bank-cards
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (BẮT BUỘC)
X-Device-ID: {{DEVICE_ID}}              (BẮT BUỘC)
Content-Type: application/json
```

**Body:**

```json
{
  "bank": "bank_001",
  "cardNumber": "0000000000000000",
  "cardHolderName": "NGUYEN VAN A",
  "branch": "branch_001"
}
```

| Tên | Kiểu | Bắt buộc | Validation |
|-----|------|----------|------------|
| bank | string | **Có** | MongoDB ObjectID của bank |
| cardNumber | string | **Có** | Chỉ chứa số |
| cardHolderName | string | **Có** | Tên chủ thẻ |
| branch | string | Không | Branch ID |

**cURL:**

```bash
curl -X POST "{{BASE_URL}}/users/bank-cards" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{"bank": "bank_001", "cardNumber": "0000000000000000", "cardHolderName": "NGUYEN VAN A"}'
```

**Test lỗi:**

```bash
# cardNumber chứa chữ → 400
curl -X POST "{{BASE_URL}}/users/bank-cards" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{"bank": "bank_001", "cardNumber": "ABC123", "cardHolderName": "TEST"}'
```

---

## 20. Cập nhật Thẻ ngân hàng

```
PUT {{BASE_URL}}/users/bank-cards/:id
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Path params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| id | string | **Có** | Bank card ID |

**Body:** Giống [API #19](#19-thêm-thẻ-ngân-hàng).

**cURL:**

```bash
curl -X PUT "{{BASE_URL}}/users/bank-cards/card_001" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{"bank": "bank_001", "cardNumber": "0000000000000000", "cardHolderName": "NGUYEN VAN A"}'
```

---

## 21. Đặt Thẻ mặc định

```
PUT {{BASE_URL}}/users/bank-cards/:id/set-default
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Path params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| id | string | **Có** | Bank card ID |

**Body:** Không cần

**cURL:**

```bash
curl -X PUT "{{BASE_URL}}/users/bank-cards/card_001/set-default" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}"
```

**Response 200:**

```json
{
  "data": {},
  "code": 200
}
```

---

## 22. Tạo giấy tờ tuỳ thân

```
POST {{BASE_URL}}/users/identification
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (BẮT BUỘC)
X-Device-ID: {{DEVICE_ID}}              (BẮT BUỘC)
Content-Type: application/json
```

**Body:**

```json
{
  "identifications": [
    {
      "type": "CCCD",
      "number": "000000000000",
      "name": "Nguyễn Văn A",
      "address": "123 Nguyễn Huệ, Q1, TP.HCM",
      "issuePlace": "Cục CS QLHC về TTXH",
      "issueDate": "2020-06-15",
      "gender": "M",
      "birthday": "1995-01-15",
      "isNone": false
    }
  ],
  "photos": {
    "frontSide": { "url": "https://cdn.example.com/cmnd-front.jpg" },
    "backSide": { "url": "https://cdn.example.com/cmnd-back.jpg" },
    "type": "CCCD"
  },
  "taxNumber": "0000000000"
}
```

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| identifications | array | **Có** | Mảng giấy tờ (không rỗng) |
| identifications[].type | string | **Có** | `CMND` hoặc `CCCD` (unique trong mảng) |
| identifications[].number | string | **Có** (CCCD) | Số giấy tờ |
| identifications[].name | string | Không | Họ tên |
| identifications[].address | string | Không | Địa chỉ |
| identifications[].issuePlace | string | **Có** (CCCD) | Nơi cấp |
| identifications[].issueDate | string | **Có** (CCCD) | Ngày cấp |
| identifications[].gender | string | Không | Giới tính |
| identifications[].birthday | string | Không | Ngày sinh |
| identifications[].isNone | boolean | Không | `true` = bỏ qua validation |
| photos | object | Không | Ảnh CMND/CCCD |
| taxNumber | string | Không | Mã số thuế |

**cURL:**

```bash
curl -X POST "{{BASE_URL}}/users/identification" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{
    "identifications": [{"type": "CCCD", "number": "000000000000", "name": "Nguyễn Văn A", "issuePlace": "Cục CS QLHC về TTXH", "issueDate": "2020-06-15"}],
    "taxNumber": "0000000000"
  }'
```

---

## 23. Xem giấy tờ của tôi

```
GET {{BASE_URL}}/users/identification/me
```

> **BẮT BUỘC ĐĂNG NHẬP**

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/users/identification/me" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}"
```

**Response 200:**

```json
{
  "data": {
    "_id": "id_001",
    "status": "approved",
    "taxNumber": "0000000000",
    "identificationNumber": "000000000000",
    "completedAt": "2026-01-20T10:00:00Z",
    "note": ""
  },
  "code": 200
}
```

---

## 24. Cập nhật giấy tờ

```
PUT {{BASE_URL}}/users/identification/:id
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Path params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| id | string | **Có** | Identification ID |

**Body:** Giống [API #22](#22-tạo-giấy-tờ-tuỳ-thân) (trừ field `photos` có thể khác).

---

## 25. Trích xuất ảnh CMND/CCCD

```
POST {{BASE_URL}}/users/identification/image
```

> **BẮT BUỘC ĐĂNG NHẬP**
>
> **Content-Type:** `multipart/form-data` (KHÔNG phải JSON)

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (BẮT BUỘC)
X-Device-ID: {{DEVICE_ID}}              (BẮT BUỘC)
```

**Form data:**

| Tên | Kiểu | Bắt buộc | Validation |
|-----|------|----------|------------|
| image | file | **Có** | JPG, JPEG, hoặc PNG |

**cURL:**

```bash
curl -X POST "{{BASE_URL}}/users/identification/image" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -F "image=@/path/to/cmnd_front.jpg"
```

**Test lỗi:**

```bash
# File không phải ảnh → 400
curl -X POST "{{BASE_URL}}/users/identification/image" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -F "image=@/path/to/document.pdf"
```

---

## 26. Tạo/Cập nhật thông tin Hợp đồng

```
POST {{BASE_URL}}/users/contract/info
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Body:**

```json
{
  "phone": "0900000001",
  "name": "Nguyễn Văn A",
  "identificationNumber": "000000000000",
  "taxNumber": "0000000000",
  "email": "user1@example.com",
  "address": "123 Nguyễn Huệ, Q1, TP.HCM",
  "dob": "1995-01-15",
  "issue_date": "2020-06-15",
  "issue_place": "Cục CS QLHC về TTXH",
  "card_front": "https://cdn.example.com/front.jpg",
  "card_back": "https://cdn.example.com/back.jpg"
}
```

| Tên | Kiểu | Bắt buộc | Validation |
|-----|------|----------|------------|
| phone | string | **Có** | Regex: `^(0|\+84)[0-9]{9,10}$` |
| name | string | **Có** | — |
| identificationNumber | string | **Có** | — |
| taxNumber | string | Không | — |
| email | string | Không | — |
| address | string | Không | — |
| dob | string | Không | Date of birth |
| issue_date | string | Không | — |
| issue_place | string | Không | — |
| card_front | string | Không | URL ảnh mặt trước |
| card_back | string | Không | URL ảnh mặt sau |

**cURL:**

```bash
curl -X POST "{{BASE_URL}}/users/contract/info" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{"phone": "0900000001", "name": "Nguyễn Văn A", "identificationNumber": "000000000000"}'
```

---

## 27. Xem Hợp đồng mẫu

```
POST {{BASE_URL}}/users/contract/estimate
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Body:** (tất cả field đều không bắt buộc)

```json
{
  "identificationNumber": "000000000000",
  "bankCardNumber": "0000000000000000",
  "bankName": "Techcombank",
  "phoneNumber": "0900000001",
  "taxNumber": "0000000000",
  "name": "Nguyễn Văn A",
  "bankAccountName": "NGUYEN VAN A",
  "bankBranch": "Chi nhánh HCM",
  "email": "user1@example.com",
  "address": "123 Nguyễn Huệ, Q1, TP.HCM",
  "dob": "1995-01-15",
  "issue_date": "2020-06-15",
  "issue_place": "Cục CS QLHC về TTXH"
}
```

**cURL:**

```bash
curl -X POST "{{BASE_URL}}/users/contract/estimate" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{"name": "Nguyễn Văn A"}'
```

---

## 28. Lấy URL ký Hợp đồng

```
GET {{BASE_URL}}/users/contract/pre-signed
```

> **BẮT BUỘC ĐĂNG NHẬP**

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/users/contract/pre-signed" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}"
```

**Response 200:**

```json
{
  "data": {
    "redirectUrl": "https://tos-service.example.com/sign?contractId=xxx&token=yyy"
  },
  "code": 200
}
```

---

## 29. Lịch sử giao dịch

```
GET {{BASE_URL}}/users/cash-flow
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (BẮT BUỘC)
X-Device-ID: {{DEVICE_ID}}              (BẮT BUỘC)
Accept-Language: vi
```

**Query params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| pageToken | string | Không | Token phân trang |
| keyword | string | Không | Tìm kiếm |
| sort | string | Không | Sắp xếp |
| category | string | Không | Lọc theo loại |

> Default limit: 21

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/users/cash-flow" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": [
    {
      "_id": "cf_001",
      "title": "Thưởng video đạt 1000 views",
      "action": "credit",
      "oldBalance": 2000000.0,
      "newBalance": 2100000.0,
      "value": 100000.0,
      "type": "reward",
      "targetId": "content_001",
      "targetType": "content",
      "createdAt": "2026-03-15T10:00:00Z"
    }
  ],
  "nextPageToken": "",
  "code": 200
}
```

---

## 30. Danh sách tài khoản Social

```
GET {{BASE_URL}}/users/socials
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (BẮT BUỘC)
X-Device-ID: {{DEVICE_ID}}              (BẮT BUỘC)
```

**Query params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| source | string | Không | Lọc theo nền tảng (youtube, tiktok, ...) |
| keyword | string | Không | Tìm kiếm |
| partner | string | Không | Partner filter |
| status | string | Không | Lọc theo trạng thái |

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/users/socials" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}"
```

**Response 200:**

```json
{
  "data": [
    {
      "_id": "social_001",
      "user": "660a1b2c3d4e5f6a7b8c9d01",
      "source": "youtube",
      "data": {
        "id": "UC1234567890",
        "name": "Nguyễn Văn A Channel",
        "avatar": "https://yt3.ggpht.com/..."
      },
      "status": "approved",
      "stats": {
        "subscriberCount": 15000,
        "videoCount": 120,
        "viewCount": 500000
      },
      "isTokenExpired": false,
      "demographics": {},
      "atCoreStatus": "synced",
      "createdAt": "2025-06-01T00:00:00Z",
      "updatedAt": "2026-03-15T10:00:00Z"
    }
  ],
  "code": 200
}
```

---

## 31. Chi tiết tài khoản Social

```
GET {{BASE_URL}}/users/socials/:id
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Path params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| id | string | **Có** | User Social ID (MongoDB ObjectID) |

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/users/socials/social_001" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}"
```

**Response 200:** Giống 1 item trong [API #30](#30-danh-sách-tài-khoản-social).

---

## 32. Thống kê Social

```
GET {{BASE_URL}}/users/socials/statistics
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Query params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| partner | string | **Có** | Partner ID |

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/users/socials/statistics?partner=techcombank" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}"
```

**Response 200:**

```json
{
  "data": {
    "total": 3,
    "totalApproved": 2,
    "totalPending": 1,
    "totalRejected": 0
  },
  "code": 200
}
```

---

## 33. Stats tổng quan Social

```
GET {{BASE_URL}}/users/socials/stats
```

> **BẮT BUỘC ĐĂNG NHẬP**

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/users/socials/stats" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}"
```

**Response 200:**

```json
{
  "data": {
    "total": 3,
    "totalVideo": 120,
    "totalSubscriber": 15000,
    "totalView": 500000,
    "totalLike": 25000
  },
  "code": 200
}
```

---

## 34. Cập nhật Demographics

```
POST {{BASE_URL}}/users/socials/:id/demographics
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Path params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| id | string | **Có** | User Social ID |

**Body:**

```json
{
  "subscribersCount": 15000,
  "audienceAges": [
    { "code": "18-24", "value": 35 },
    { "code": "25-34", "value": 45 }
  ],
  "genders": [
    { "code": "male", "value": 60 },
    { "code": "female", "value": 40 }
  ],
  "topics": [
    { "code": "finance", "value": 70 }
  ],
  "countryCode": "VN",
  "provinceCode": ["HCM", "HN"]
}
```

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| subscribersCount | number | Không | Số subscriber |
| audienceAges | array | Không | Phân bổ độ tuổi `[{code, value}]` |
| genders | array | Không | Phân bổ giới tính |
| topics | array | Không | Chủ đề |
| interactionTimes | array | Không | Thời gian tương tác |
| platforms | array | Không | Nền tảng |
| incomeLevels | array | Không | Thu nhập |
| educationLevels | array | Không | Trình độ học vấn |
| professions | array | Không | Nghề nghiệp |
| analyticsSources | array | Không | Nguồn analytics |
| countryCode | string | Không | Mã quốc gia |
| provinceCode | array | Không | Mã tỉnh/thành |

**cURL:**

```bash
curl -X POST "{{BASE_URL}}/users/socials/social_001/demographics" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{"subscribersCount": 15000, "countryCode": "VN"}'
```

---

## 35. Liên kết tài khoản Social

```
POST {{BASE_URL}}/users/socials/link
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Body:**

```json
{
  "source": "youtube",
  "token": "google_oauth_token",
  "redirectURI": "https://yourapp.com/callback",
  "isSyncToken": false,
  "userSocialId": "",
  "linkChannel": ""
}
```

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| source | string | **Có** | Nền tảng: `youtube`, `tiktok`, `facebook`, `instagram` |
| token | string | Không | OAuth token |
| redirectURI | string | Không | Redirect URI |
| isSyncToken | boolean | Không | Đồng bộ token |
| userSocialId | string | Không | User social ID |
| linkChannel | string | Không | Kênh liên kết |

**cURL:**

```bash
curl -X POST "{{BASE_URL}}/users/socials/link" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{"source": "youtube", "token": "google_oauth_token"}'
```

**Response 200:**

```json
{
  "data": {
    "userSocialId": "social_002"
  },
  "code": 200
}
```

---

## 36. URL Điều khoản dịch vụ

```
GET {{BASE_URL}}/users/service-tos/redirect-url
```

> **BẮT BUỘC ĐĂNG NHẬP**

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/users/service-tos/redirect-url" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}"
```

**Response 200:**

```json
{
  "data": {
    "redirectUrl": "https://tos-service.example.com/view?token=xxx"
  },
  "code": 200
}
```
