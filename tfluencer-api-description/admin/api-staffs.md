# API Staffs - Admin Panel

Tai lieu API quan ly nhan vien (Staff) cho Admin Panel.

**Base URL variable:** `{{ADMIN_BASE_URL}}` (vi du: `https://api.example.com/admin/v1`)
**Token variable:** `{{ADMIN_TOKEN}}` (JWT token lay tu API Login)

---

## Muc luc

| # | Ten API | Method | Path | Quyen |
|---|---------|--------|------|-------|
| 1 | [Login](#1-login) | POST | `/staffs/login` | Public |
| 2 | [Login With Google](#2-login-with-google) | POST | `/staffs/login-with-google` | Public |
| 3 | [Get Me](#3-get-me) | GET | `/staffs/me` | RequiredLogin |
| 4 | [Get List](#4-get-list) | GET | `/staffs` | RequiredLogin |
| 5 | [Update My Password](#5-update-my-password) | PUT | `/staffs/me/update-password` | RequiredLogin |
| 6 | [Generate Auth Code](#6-generate-auth-code) | POST | `/staffs/auth/generate-code` | RequiredLogin |
| 7 | [Exchange Auth Code](#7-exchange-auth-code) | POST | `/staffs/auth/exchange` | Public (rate limited) |
| 8 | [Verify Invite Token](#8-verify-invite-token) | POST | `/staffs/invite/verify` | Public |
| 9 | [Accept Invite](#9-accept-invite) | POST | `/staffs/invite/accept` | Public |
| 10 | [Forgot Password](#10-forgot-password) | POST | `/staffs/forgot-password` | Public |
| 11 | [Reset Password](#11-reset-password) | POST | `/staffs/reset-password` | Public |
| 12 | [Register (Create) Staff](#12-register-create-staff) | POST | `/staffs/register` | IsAdmin |
| 13 | [Update Staff Info](#13-update-staff-info) | PUT | `/staffs/:id/update-info` | IsAdmin |
| 14 | [Update Staff Password](#14-update-staff-password) | PUT | `/staffs/:id/update-password` | IsAdmin |
| 15 | [Change Status](#15-change-status) | PATCH | `/staffs/:id/status` | IsAdmin |
| 16 | [Invite Staff](#16-invite-staff) | POST | `/staffs/invite` | IsAdmin |
| 17 | [Bulk Invite](#17-bulk-invite) | POST | `/staffs/bulk-invite` | IsAdmin |
| 18 | [Resend Invite](#18-resend-invite) | POST | `/staffs/:id/resend-invite` | IsAdmin |

---

## Cau truc Response chung

### Thanh cong
```json
{
  "data": { ... },
  "code": 200,
  "message": ""
}
```

### That bai
```json
{
  "data": null,
  "code": 400,
  "message": "Mo ta loi"
}
```

### Cau truc StaffAuthenResponse
```json
{
  "_id": "64a1b2c3d4e5f6a7b8c9d0e1",
  "token": "{{TOKEN}}",
  "inviteLink": "https://dashboard.example.com/vi/accept-invite?token=abc123"
}
```

### Cau truc StaffMeResponse
```json
{
  "_id": "64a1b2c3d4e5f6a7b8c9d0e1",
  "name": "Nguyen Van An",
  "email": "an.nguyen@example.com",
  "isRoot": false,
  "avatar": {
    "_id": "64a1b2c3d4e5f6a7b8c9d0e2",
    "name": "avatar.jpg",
    "dimensions": {
      "sm": { "width": 375, "height": 130, "url": "https://files.example.com/sm_avatar.jpg" },
      "md": { "width": 750, "height": 250, "url": "https://files.example.com/md_avatar.jpg" }
    }
  },
  "role": {
    "_id": "64a1b2c3d4e5f6a7b8c9d0e3",
    "name": "Quan tri vien",
    "code": "admin"
  },
  "partner": {
    "_id": "64a1b2c3d4e5f6a7b8c9d0e4",
    "name": "ViewBoost Vietnam"
  }
}
```

### Cau truc StaffDetail (dung trong GetList / ChangeStatus)
```json
{
  "_id": "64a1b2c3d4e5f6a7b8c9d0e1",
  "name": "Tran Thi Bich",
  "email": "bich.tran@example.com",
  "isRoot": false,
  "active": true,
  "avatar": { ... },
  "partner": { "_id": "...", "name": "ViewBoost Vietnam" },
  "role": { "_id": "...", "name": "Nhan vien" },
  "inviteStatus": "accepted",
  "inviteExpiry": null,
  "createdAt": { "value": "2024-01-15T08:30:00Z" },
  "updatedAt": { "value": "2024-01-20T14:00:00Z" }
}
```

---

## 1. Login

**Quyen:** Public (co rate limiting)
**Endpoint:** `POST /staffs/login`

**Headers:**
| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| Content-Type | application/json | Co |
| x-device-id | `<device-id>` | Co (dung de gen token) |

**Body mau:**
```json
{
  "email": "admin@example.com",
  "password": "P@ssw0rd123"
}
```

**Validation:**
- `email`: bat buoc, phai la email hop le
- `password`: bat buoc

**cURL:**
```bash
curl -X POST '{{ADMIN_BASE_URL}}/staffs/login' \
  -H 'Content-Type: application/json' \
  -H 'x-device-id: device-web-001' \
  -d '{
    "email": "admin@example.com",
    "password": "P@ssw0rd123"
  }'
```

**Response thanh cong (200):**
```json
{
  "data": {
    "_id": "64a1b2c3d4e5f6a7b8c9d0e1",
    "token": "{{TOKEN}}"
  },
  "code": 200,
  "message": ""
}
```

**Test loi:**
| Case | Cach test | Expected |
|------|-----------|----------|
| Email sai | `"email": "khong-ton-tai@example.com"` | 400, "Dang nhap that bai" |
| Mat khau sai | Email dung, password sai | 400, "Dang nhap that bai" |
| Tai khoan inactive | Staff bi disable | 400, "Dang nhap that bai" |
| Email rong | `"email": ""` | 400, validation error |
| Email khong hop le | `"email": "khongemail"` | 400, validation error |

---

## 2. Login With Google

**Quyen:** Public
**Endpoint:** `POST /staffs/login-with-google`

> **Luu y:** Tinh nang nay chua duoc trien khai (panic: "implement me"). Goi API nay se tra ve 500 Internal Server Error.

**Headers:**
| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| Content-Type | application/json | Co |

**cURL:**
```bash
curl -X POST '{{ADMIN_BASE_URL}}/staffs/login-with-google' \
  -H 'Content-Type: application/json' \
  -d '{}'
```

**Response hien tai:**
```json
{
  "code": 500,
  "message": "Internal Server Error"
}
```

---

## 3. Get Me

**Quyen:** RequiredLogin
**Endpoint:** `GET /staffs/me`

**Headers:**
| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| Authorization | Bearer {{ADMIN_TOKEN}} | Co |

**cURL:**
```bash
curl -X GET '{{ADMIN_BASE_URL}}/staffs/me' \
  -H 'Authorization: Bearer {{ADMIN_TOKEN}}'
```

**Response thanh cong (200):**
```json
{
  "data": {
    "_id": "64a1b2c3d4e5f6a7b8c9d0e1",
    "name": "Nguyen Van An",
    "email": "an.nguyen@example.com",
    "isRoot": false,
    "avatar": {
      "_id": "64a1b2c3d4e5f6a7b8c9d0e2",
      "name": "avatar_an.jpg",
      "dimensions": {
        "sm": { "width": 375, "height": 130, "url": "https://files.example.com/sm_avatar_an.jpg" },
        "md": { "width": 750, "height": 250, "url": "https://files.example.com/md_avatar_an.jpg" }
      }
    },
    "role": {
      "_id": "64a1b2c3d4e5f6a7b8c9d0e3",
      "name": "Quan tri vien",
      "code": "admin"
    },
    "partner": {
      "_id": "64a1b2c3d4e5f6a7b8c9d0e4",
      "name": "ViewBoost Vietnam"
    }
  },
  "code": 200,
  "message": ""
}
```

**Test loi:**
| Case | Cach test | Expected |
|------|-----------|----------|
| Khong co token | Xoa header Authorization | 401 Unauthorized |
| Token het han | Dung token cu qua 8h | 401 Unauthorized |
| Token sai | `"Bearer invalid-token"` | 401 Unauthorized |

---

## 4. Get List

**Quyen:** RequiredLogin
**Endpoint:** `GET /staffs`

**Headers:**
| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| Authorization | Bearer {{ADMIN_TOKEN}} | Co |

**Query params:**
| Param | Type | Bat buoc | Mo ta |
|-------|------|----------|-------|
| page | int | Khong | So trang, mac dinh 1 |
| limit | int | Khong | So ban ghi/trang, mac dinh theo config |
| keyword | string | Khong | Tim kiem theo ten hoac email |
| status | string | Khong | Loc theo trang thai: `active` hoac `inactive` |

**Luu y:**
- Staff `isRoot` thay duoc tat ca nhan vien cua moi partner
- Staff thuong chi thay duoc nhan vien trong cung partner cua minh
- Ket qua khong bao gom staff `isRoot`

**cURL:**
```bash
# Lay tat ca (trang 1)
curl -X GET '{{ADMIN_BASE_URL}}/staffs?page=1&limit=20' \
  -H 'Authorization: Bearer {{ADMIN_TOKEN}}'

# Tim kiem theo ten
curl -X GET '{{ADMIN_BASE_URL}}/staffs?page=1&limit=20&keyword=nguyen' \
  -H 'Authorization: Bearer {{ADMIN_TOKEN}}'

# Loc staff dang hoat dong
curl -X GET '{{ADMIN_BASE_URL}}/staffs?page=1&limit=20&status=active' \
  -H 'Authorization: Bearer {{ADMIN_TOKEN}}'
```

**Response thanh cong (200):**
```json
{
  "data": {
    "data": [
      {
        "_id": "64a1b2c3d4e5f6a7b8c9d0e1",
        "name": "Nguyen Van An",
        "email": "an.nguyen@example.com",
        "isRoot": false,
        "active": true,
        "avatar": {
          "_id": "64a1b2c3d4e5f6a7b8c9d0e2",
          "name": "avatar_an.jpg",
          "dimensions": {
            "sm": { "width": 375, "height": 130, "url": "https://files.example.com/sm_avatar_an.jpg" },
            "md": { "width": 750, "height": 250, "url": "https://files.example.com/md_avatar_an.jpg" }
          }
        },
        "partner": { "_id": "64a1b2c3d4e5f6a7b8c9d0e4", "name": "ViewBoost Vietnam" },
        "role": { "_id": "64a1b2c3d4e5f6a7b8c9d0e3", "name": "Nhan vien" },
        "inviteStatus": "accepted",
        "createdAt": { "value": "2024-01-15T08:30:00Z" },
        "updatedAt": { "value": "2024-01-20T14:00:00Z" }
      }
    ],
    "total": 1
  },
  "code": 200,
  "message": ""
}
```

**Test loi:**
| Case | Cach test | Expected |
|------|-----------|----------|
| Khong co token | Xoa header Authorization | 401 Unauthorized |
| Trang khong ton tai | `page=9999` | 200, `data: []`, `total: N` |

---

## 5. Update My Password

**Quyen:** RequiredLogin
**Endpoint:** `PUT /staffs/me/update-password`

**Headers:**
| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| Authorization | Bearer {{ADMIN_TOKEN}} | Co |
| Content-Type | application/json | Co |

**Body mau:**
```json
{
  "currentPassword": "OldP@ss123",
  "password": "NewP@ss456",
  "confirmPassword": "NewP@ss456"
}
```

**Validation:**
- `currentPassword`: khong bat buoc nhung se duoc kiem tra neu co truyen vao
- `password`: bat buoc, toi thieu 6 ky tu
- `confirmPassword`: bat buoc, phai trung khop voi `password`

**cURL:**
```bash
curl -X PUT '{{ADMIN_BASE_URL}}/staffs/me/update-password' \
  -H 'Authorization: Bearer {{ADMIN_TOKEN}}' \
  -H 'Content-Type: application/json' \
  -d '{
    "currentPassword": "OldP@ss123",
    "password": "NewP@ss456",
    "confirmPassword": "NewP@ss456"
  }'
```

**Response thanh cong (200):**
```json
{
  "data": {},
  "code": 200,
  "message": ""
}
```

**Luu y:** Sau khi doi mat khau thanh cong, tat ca cac token hien tai se bi vo hieu hoa (logout khoi tat ca thiet bi).

**Test loi:**
| Case | Cach test | Expected |
|------|-----------|----------|
| Mat khau cu sai | `currentPassword` sai | 400, "Mat khau hien tai khong dung" |
| Mat khau qua ngan | `password: "abc"` | 400, "Mat khau phai co it nhat 6 ky tu" |
| Xac nhan khong khop | `confirmPassword` khac `password` | 400, validation error |
| Mat khau rong | `"password": ""` | 400, validation error |

---

## 6. Generate Auth Code

**Quyen:** RequiredLogin
**Endpoint:** `POST /staffs/auth/generate-code`

Tao mot ma xac thuc tam thoi (32 ky tu, URL-safe base64) de trao doi lay token moi tren Dashboard. Ma nay co hieu luc trong **120 giay** va chi dung duoc **1 lan**.

**Headers:**
| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| Authorization | Bearer {{ADMIN_TOKEN}} | Co |
| Content-Type | application/json | Co |

**Body mau:** Khong can body (hoac truyen `{}`)

**cURL:**
```bash
curl -X POST '{{ADMIN_BASE_URL}}/staffs/auth/generate-code' \
  -H 'Authorization: Bearer {{ADMIN_TOKEN}}' \
  -H 'Content-Type: application/json' \
  -d '{}'
```

**Response thanh cong (200):**
```json
{
  "data": {
    "code": "aB3xKm9pQrT7vWzL2nYhGcFe8sUdJiNo"
  },
  "code": 200,
  "message": ""
}
```

**Test loi:**
| Case | Cach test | Expected |
|------|-----------|----------|
| Khong co token | Xoa header Authorization | 401 Unauthorized |
| Staff inactive | Token cua staff bi disable | 400, "Staff khong hoat dong" |

---

## 7. Exchange Auth Code

**Quyen:** Public (co rate limiting)
**Endpoint:** `POST /staffs/auth/exchange`

Dung `code` lay duoc tu API [Generate Auth Code](#6-generate-auth-code) de doi lay JWT token moi. Ma nay chi dung duoc **1 lan** va het han sau **120 giay**.

**Headers:**
| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| Content-Type | application/json | Co |

**Body mau:**
```json
{
  "code": "aB3xKm9pQrT7vWzL2nYhGcFe8sUdJiNo",
  "deviceId": "dashboard-web-prod-001"
}
```

**Validation:**
- `code`: bat buoc
- `deviceId`: bat buoc

**cURL:**
```bash
curl -X POST '{{ADMIN_BASE_URL}}/staffs/auth/exchange' \
  -H 'Content-Type: application/json' \
  -d '{
    "code": "aB3xKm9pQrT7vWzL2nYhGcFe8sUdJiNo",
    "deviceId": "dashboard-web-prod-001"
  }'
```

**Response thanh cong (200):**
```json
{
  "data": {
    "_id": "64a1b2c3d4e5f6a7b8c9d0e1",
    "token": "{{TOKEN}}"
  },
  "code": 200,
  "message": ""
}
```

**Test loi:**
| Case | Cach test | Expected |
|------|-----------|----------|
| Code het han | Doi qua 120s moi goi | 400, "Ma khong hop le hoac da het han" |
| Code da dung | Goi API nay lan 2 voi cung code | 400, "Ma khong hop le hoac da het han" |
| Code rong | `"code": ""` | 400, validation error |
| deviceId rong | `"deviceId": ""` | 400, validation error |

---

## 8. Verify Invite Token

**Quyen:** Public
**Endpoint:** `POST /staffs/invite/verify`

Kiem tra tinh hop le cua token trong email moi (invite link). Token het han sau **48 gio** ke tu khi gui.

**Headers:**
| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| Content-Type | application/json | Co |

**Body mau:**
```json
{
  "token": "rawTokenFromEmailLink123456789012"
}
```

**Validation:**
- `token`: bat buoc

**cURL:**
```bash
curl -X POST '{{ADMIN_BASE_URL}}/staffs/invite/verify' \
  -H 'Content-Type: application/json' \
  -d '{
    "token": "rawTokenFromEmailLink123456789012"
  }'
```

**Response thanh cong (200):**
```json
{
  "data": {
    "_id": "64a1b2c3d4e5f6a7b8c9d0e5",
    "name": "Le Thi Cam",
    "email": "cam.le@example.com",
    "isRoot": false
  },
  "code": 200,
  "message": ""
}
```

**Test loi:**
| Case | Cach test | Expected |
|------|-----------|----------|
| Token sai | Truyen chuoi ngau nhien | 400, "Token moi khong hop le" |
| Token het han | Doi qua 48h sau khi duoc moi | 400, "Token moi khong hop le" |
| Token da chap nhan | Sau khi da Accept Invite | 400, "Token moi khong hop le" |
| Token rong | `"token": ""` | 400, validation error |

---

## 9. Accept Invite

**Quyen:** Public
**Endpoint:** `POST /staffs/invite/accept`

Chap nhan loi moi va thiet lap mat khau lan dau. Sau khi thanh cong, tai khoan duoc kich hoat (`active: true`) va tra ve JWT token de dang nhap ngay.

**Headers:**
| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| Content-Type | application/json | Co |
| x-device-id | `<device-id>` | Co (dung de gen token) |

**Body mau:**
```json
{
  "token": "rawTokenFromEmailLink123456789012",
  "password": "NewP@ss789"
}
```

**Validation:**
- `token`: bat buoc
- `password`: bat buoc (phai qua kiem tra do manh cua password)

**cURL:**
```bash
curl -X POST '{{ADMIN_BASE_URL}}/staffs/invite/accept' \
  -H 'Content-Type: application/json' \
  -H 'x-device-id: device-web-001' \
  -d '{
    "token": "rawTokenFromEmailLink123456789012",
    "password": "NewP@ss789"
  }'
```

**Response thanh cong (200):**
```json
{
  "data": {
    "_id": "64a1b2c3d4e5f6a7b8c9d0e5",
    "token": "{{TOKEN}}"
  },
  "code": 200,
  "message": ""
}
```

**Test loi:**
| Case | Cach test | Expected |
|------|-----------|----------|
| Token het han | Doi qua 48h | 400, "Token moi khong hop le" |
| Token da dung | Goi API lan 2 voi cung token | 400, "Token moi khong hop le" |
| Mat khau yeu | `"password": "123"` | 400, loi validate mat khau |
| Token rong | `"token": ""` | 400, validation error |

---

## 10. Forgot Password

**Quyen:** Public
**Endpoint:** `POST /staffs/forgot-password`

Gui email dat lai mat khau. Link reset co hieu luc **60 phut**.

**Luu y bao mat:** API luon tra ve 200 du email co ton tai hay khong (tranh lo thong tin tai khoan).

**Headers:**
| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| Content-Type | application/json | Co |

**Body mau:**
```json
{
  "email": "an.nguyen@example.com"
}
```

**Validation:**
- `email`: bat buoc, phai la email hop le

**cURL:**
```bash
curl -X POST '{{ADMIN_BASE_URL}}/staffs/forgot-password' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "an.nguyen@example.com"
  }'
```

**Response thanh cong (200):**
```json
{
  "data": {},
  "code": 200,
  "message": ""
}
```

**Test loi:**
| Case | Cach test | Expected |
|------|-----------|----------|
| Email khong ton tai | Email chua dang ky | 200 (khong lo thong tin) |
| Email inactive | Tai khoan bi vo hieu hoa | 200 (khong gui email) |
| Email rong | `"email": ""` | 400, validation error |
| Email sai dinh dang | `"email": "khongemail"` | 400, validation error |

---

## 11. Reset Password

**Quyen:** Public
**Endpoint:** `POST /staffs/reset-password`

Dat lai mat khau bang token trong email. Token het han sau **60 phut** ke tu khi yeu cau Forgot Password.

**Headers:**
| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| Content-Type | application/json | Co |

**Body mau:**
```json
{
  "token": "rawResetTokenFromEmail12345678901",
  "password": "ResetP@ss123"
}
```

**Validation:**
- `token`: bat buoc
- `password`: bat buoc (phai qua kiem tra do manh cua password)

**cURL:**
```bash
curl -X POST '{{ADMIN_BASE_URL}}/staffs/reset-password' \
  -H 'Content-Type: application/json' \
  -d '{
    "token": "rawResetTokenFromEmail12345678901",
    "password": "ResetP@ss123"
  }'
```

**Response thanh cong (200):**
```json
{
  "data": {},
  "code": 200,
  "message": ""
}
```

**Luu y:** Sau khi doi mat khau thanh cong, tat ca cac token hien tai cua staff do se bi vo hieu hoa.

**Test loi:**
| Case | Cach test | Expected |
|------|-----------|----------|
| Token sai | Truyen chuoi ngau nhien | 400, "Token dat lai mat khau khong hop le" |
| Token het han | Doi qua 60 phut | 400, "Token dat lai mat khau khong hop le" |
| Mat khau yeu | `"password": "abc"` | 400, loi validate mat khau |
| Token rong | `"token": ""` | 400, validation error |

---

## 12. Register (Create) Staff

**Quyen:** IsAdmin (RequiredLogin + IsAdmin)
**Endpoint:** `POST /staffs/register`

Tao nhan vien moi truc tiep voi mat khau (khong qua luong invite). Neu khong phai `isRoot`, bat buoc phai co `role`.

**Headers:**
| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| Authorization | Bearer {{ADMIN_TOKEN}} | Co |
| Content-Type | application/json | Co |

**Body mau:**
```json
{
  "name": "Pham Van Duc",
  "email": "duc.pham@example.com",
  "phone": "0900000001",
  "password": "P@ssw0rd456",
  "confirmPassword": "P@ssw0rd456",
  "partner": "64a1b2c3d4e5f6a7b8c9d0e4",
  "role": "64a1b2c3d4e5f6a7b8c9d0e3",
  "isRoot": false,
  "avatar": {
    "_id": "64a1b2c3d4e5f6a7b8c9d0e6",
    "name": "avatar_duc.jpg",
    "dimensions": {
      "sm": { "width": 375, "height": 130, "url": "" },
      "md": { "width": 750, "height": 250, "url": "" }
    }
  }
}
```

**Validation:**
- `name`: bat buoc
- `email`: bat buoc, phai la email hop le, khong duoc trung voi email da ton tai
- `password`: bat buoc, toi thieu 6 ky tu
- `confirmPassword`: bat buoc, phai trung voi `password`
- `role`: bat buoc neu `isRoot: false`, phai la MongoDB ObjectID hop le
- `partner`: bắt buoc, phai la `_id` cua Partner ton tai trong he thong
- `phone`, `avatar`: khong bat buoc

**cURL:**
```bash
curl -X POST '{{ADMIN_BASE_URL}}/staffs/register' \
  -H 'Authorization: Bearer {{ADMIN_TOKEN}}' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Pham Van Duc",
    "email": "duc.pham@example.com",
    "phone": "0900000001",
    "password": "P@ssw0rd456",
    "confirmPassword": "P@ssw0rd456",
    "partner": "64a1b2c3d4e5f6a7b8c9d0e4",
    "role": "64a1b2c3d4e5f6a7b8c9d0e3",
    "isRoot": false
  }'
```

**Response thanh cong (200):**
```json
{
  "data": {
    "_id": "64a1b2c3d4e5f6a7b8c9d0e7",
    "token": ""
  },
  "code": 200,
  "message": ""
}
```

**Test loi:**
| Case | Cach test | Expected |
|------|-----------|----------|
| Email da ton tai | Dung email da co trong he thong | 400, "Email da ton tai" |
| Partner khong ton tai | `partner` la ObjectID khong hop le | 400, loi partner |
| Role khong ton tai | `role` la ObjectID khong hop le | 400, loi role |
| Da co 1 admin | Them admin thu 2 cho cung partner | 400, "Moi partner chi co 1 admin" |
| Mat khau qua ngan | `password: "abc"` | 400, loi mat khau |
| Khong phai admin | Goi voi token staff thuong | 403 Forbidden |

---

## 13. Update Staff Info

**Quyen:** IsAdmin (RequiredLogin + IsAdmin)
**Endpoint:** `PUT /staffs/:id/update-info`

Cap nhat thong tin ca nhan cua mot nhan vien bat ky.

**Headers:**
| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| Authorization | Bearer {{ADMIN_TOKEN}} | Co |
| Content-Type | application/json | Co |

**Path param:**
| Param | Type | Mo ta |
|-------|------|-------|
| id | string (MongoDB ObjectID) | `_id` cua staff can cap nhat |

**Body mau:**
```json
{
  "name": "Pham Van Duc (Updated)",
  "email": "duc.pham.new@example.com",
  "phone": "0900000002",
  "partner": "64a1b2c3d4e5f6a7b8c9d0e4",
  "role": "64a1b2c3d4e5f6a7b8c9d0e3",
  "isRoot": false,
  "avatar": {
    "_id": "64a1b2c3d4e5f6a7b8c9d0e8",
    "name": "new_avatar_duc.jpg",
    "dimensions": {
      "sm": { "width": 375, "height": 130, "url": "" },
      "md": { "width": 750, "height": 250, "url": "" }
    }
  }
}
```

**Validation:**
- `name`: bat buoc
- `email`: bat buoc, phai la email hop le, khong duoc trung voi email cua staff khac
- `role`: bat buoc neu `isRoot: false`, phai la MongoDB ObjectID hop le

**cURL:**
```bash
curl -X PUT '{{ADMIN_BASE_URL}}/staffs/64a1b2c3d4e5f6a7b8c9d0e7/update-info' \
  -H 'Authorization: Bearer {{ADMIN_TOKEN}}' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Pham Van Duc (Updated)",
    "email": "duc.pham.new@example.com",
    "phone": "0900000002",
    "partner": "64a1b2c3d4e5f6a7b8c9d0e4",
    "role": "64a1b2c3d4e5f6a7b8c9d0e3",
    "isRoot": false
  }'
```

**Response thanh cong (200):**
```json
{
  "data": {},
  "code": 200,
  "message": ""
}
```

**Luu y:** Sau khi cap nhat thanh cong, tat ca cac token hien tai cua staff do se bi vo hieu hoa (can dang nhap lai).

**Test loi:**
| Case | Cach test | Expected |
|------|-----------|----------|
| Staff khong ton tai | ID khong hop le hoac khong co trong DB | 400, "Khong tim thay nhan vien" |
| Email trung | Dung email cua staff khac | 400, "Email da ton tai" |
| Khong phai admin | Goi voi token staff thuong | 403 Forbidden |
| ID khong hop le | `id` khong phai ObjectID | 400, validation error |

---

## 14. Update Staff Password

**Quyen:** IsAdmin (RequiredLogin + IsAdmin)
**Endpoint:** `PUT /staffs/:id/update-password`

Admin doi mat khau cho mot nhan vien bat ky. Admin khong can nhap `currentPassword` cua nhan vien.

**Headers:**
| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| Authorization | Bearer {{ADMIN_TOKEN}} | Co |
| Content-Type | application/json | Co |

**Path param:**
| Param | Type | Mo ta |
|-------|------|-------|
| id | string (MongoDB ObjectID) | `_id` cua staff can doi mat khau |

**Body mau:**
```json
{
  "password": "SetP@ss789",
  "confirmPassword": "SetP@ss789"
}
```

**Validation:**
- `password`: bat buoc, toi thieu 6 ky tu
- `confirmPassword`: bat buoc, phai trung voi `password`
- `currentPassword`: khong bat buoc trong luong nay (chi dung khi staff tu doi)

**cURL:**
```bash
curl -X PUT '{{ADMIN_BASE_URL}}/staffs/64a1b2c3d4e5f6a7b8c9d0e7/update-password' \
  -H 'Authorization: Bearer {{ADMIN_TOKEN}}' \
  -H 'Content-Type: application/json' \
  -d '{
    "password": "SetP@ss789",
    "confirmPassword": "SetP@ss789"
  }'
```

**Response thanh cong (200):**
```json
{
  "data": {},
  "code": 200,
  "message": ""
}
```

**Luu y:** Sau khi doi mat khau thanh cong, tat ca cac token hien tai cua staff do se bi vo hieu hoa.

**Test loi:**
| Case | Cach test | Expected |
|------|-----------|----------|
| Staff khong ton tai | ID khong co trong DB | 400, "Khong tim thay nhan vien" |
| Mat khau qua ngan | `password: "abc"` | 400, loi mat khau |
| Xac nhan khong khop | `confirmPassword` khac `password` | 400, validation error |
| Khong phai admin | Goi voi token staff thuong | 403 Forbidden |

---

## 15. Change Status

**Quyen:** IsAdmin (RequiredLogin + IsAdmin)
**Endpoint:** `PATCH /staffs/:id/status`

Bat/tat trang thai hoat dong cua mot nhan vien (toggle). Neu dang `active: true` se chuyen thanh `active: false` va nguoc lai.

**Headers:**
| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| Authorization | Bearer {{ADMIN_TOKEN}} | Co |

**Path param:**
| Param | Type | Mo ta |
|-------|------|-------|
| id | string (MongoDB ObjectID) | `_id` cua staff can thay doi trang thai |

**Body:** Khong can body

**cURL:**
```bash
# Bat/tat trang thai (toggle)
curl -X PATCH '{{ADMIN_BASE_URL}}/staffs/64a1b2c3d4e5f6a7b8c9d0e7/status' \
  -H 'Authorization: Bearer {{ADMIN_TOKEN}}'
```

**Response thanh cong (200) - Staff vua bi disable:**
```json
{
  "data": {
    "_id": "64a1b2c3d4e5f6a7b8c9d0e7",
    "name": "Pham Van Duc",
    "email": "duc.pham@example.com",
    "isRoot": false,
    "active": false,
    "avatar": {
      "_id": "64a1b2c3d4e5f6a7b8c9d0e6",
      "name": "avatar_duc.jpg",
      "dimensions": {
        "sm": { "width": 375, "height": 130, "url": "https://files.example.com/sm_avatar_duc.jpg" },
        "md": { "width": 750, "height": 250, "url": "https://files.example.com/md_avatar_duc.jpg" }
      }
    },
    "partner": { "_id": "64a1b2c3d4e5f6a7b8c9d0e4", "name": "ViewBoost Vietnam" },
    "inviteStatus": "accepted",
    "createdAt": { "value": "2024-01-15T08:30:00Z" },
    "updatedAt": { "value": "2024-03-20T10:00:00Z" }
  },
  "code": 200,
  "message": ""
}
```

**Luu y:** Khi disable (`active: false`), tat ca cac token dang nhap cua staff do se bi vo hieu hoa ngay lap tuc.

**Test loi:**
| Case | Cach test | Expected |
|------|-----------|----------|
| Staff khong ton tai | ID khong co trong DB | 400, error |
| Khong phai admin | Goi voi token staff thuong | 403 Forbidden |
| ID khong hop le | `id` khong phai ObjectID | 400, validation error |

---

## 16. Invite Staff

**Quyen:** IsAdmin (RequiredLogin + IsAdmin)
**Endpoint:** `POST /staffs/invite`

Gui email moi nhan vien moi. He thong tao tai khoan voi trang thai `pending` va gui link kich hoat qua email. Link co hieu luc **48 gio**.

**Headers:**
| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| Authorization | Bearer {{ADMIN_TOKEN}} | Co |
| Content-Type | application/json | Co |

**Body mau:**
```json
{
  "name": "Hoang Thi Mai",
  "email": "mai.hoang@example.com",
  "role": "64a1b2c3d4e5f6a7b8c9d0e3",
  "partner": "64a1b2c3d4e5f6a7b8c9d0e4"
}
```

**Validation:**
- `name`: bat buoc
- `email`: bat buoc, phai la email hop le, chua ton tai trong he thong
- `role`: khong bat buoc trong validation nhung can thiet de phan quyen
- `partner`: khong bat buoc trong validation nhung bat buoc trong business logic (Partner phai ton tai)

**cURL:**
```bash
curl -X POST '{{ADMIN_BASE_URL}}/staffs/invite' \
  -H 'Authorization: Bearer {{ADMIN_TOKEN}}' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Hoang Thi Mai",
    "email": "mai.hoang@example.com",
    "role": "64a1b2c3d4e5f6a7b8c9d0e3",
    "partner": "64a1b2c3d4e5f6a7b8c9d0e4"
  }'
```

**Response thanh cong (200):**
```json
{
  "data": {
    "_id": "64a1b2c3d4e5f6a7b8c9d0e9",
    "token": "",
    "inviteLink": "https://dashboard.example.com/vi/accept-invite?token=aB3xKm9pQrT7vWzL2nYhGcFe8sUdJiNo"
  },
  "code": 200,
  "message": ""
}
```

**Test loi:**
| Case | Cach test | Expected |
|------|-----------|----------|
| Email da ton tai | Moi nhan vien co email da dang ky | 400, "Email da ton tai" |
| Partner khong ton tai | `partner` la ObjectID khong hop le | 400, loi partner |
| Da co 1 admin | Assign role admin cho partner da co admin | 400, "Moi partner chi co 1 admin" |
| Khong phai admin | Goi voi token staff thuong | 403 Forbidden |

---

## 17. Bulk Invite

**Quyen:** IsAdmin (RequiredLogin + IsAdmin)
**Endpoint:** `POST /staffs/bulk-invite`

Moi nhieu nhan vien cung mot luc. Toi da **50 nhan vien** moi lan. He thong xu ly song song va tra ve ket qua tung nguoi.

**Headers:**
| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| Authorization | Bearer {{ADMIN_TOKEN}} | Co |
| Content-Type | application/json | Co |

**Body mau:**
```json
{
  "items": [
    {
      "name": "Vo Thi Lan",
      "email": "lan.vo@example.com",
      "role": "64a1b2c3d4e5f6a7b8c9d0e3",
      "partner": "64a1b2c3d4e5f6a7b8c9d0e4"
    },
    {
      "name": "Dang Van Khoa",
      "email": "khoa.dang@example.com",
      "role": "64a1b2c3d4e5f6a7b8c9d0e3",
      "partner": "64a1b2c3d4e5f6a7b8c9d0e4"
    },
    {
      "name": "Nguyen Thi Huong",
      "email": "email-da-ton-tai@example.com",
      "role": "64a1b2c3d4e5f6a7b8c9d0e3",
      "partner": "64a1b2c3d4e5f6a7b8c9d0e4"
    }
  ]
}
```

**Validation:**
- `items`: bat buoc, khong duoc rong, toi da 50 phan tu

**cURL:**
```bash
curl -X POST '{{ADMIN_BASE_URL}}/staffs/bulk-invite' \
  -H 'Authorization: Bearer {{ADMIN_TOKEN}}' \
  -H 'Content-Type: application/json' \
  -d '{
    "items": [
      {
        "name": "Vo Thi Lan",
        "email": "lan.vo@example.com",
        "role": "64a1b2c3d4e5f6a7b8c9d0e3",
        "partner": "64a1b2c3d4e5f6a7b8c9d0e4"
      },
      {
        "name": "Dang Van Khoa",
        "email": "khoa.dang@example.com",
        "role": "64a1b2c3d4e5f6a7b8c9d0e3",
        "partner": "64a1b2c3d4e5f6a7b8c9d0e4"
      }
    ]
  }'
```

**Response thanh cong (200) - Co ca thanh cong va that bai:**
```json
{
  "data": {
    "results": [
      {
        "email": "lan.vo@example.com",
        "inviteLink": "https://dashboard.example.com/vi/accept-invite?token=token1xxxxxxxxxxxxx"
      },
      {
        "email": "khoa.dang@example.com",
        "inviteLink": "https://dashboard.example.com/vi/accept-invite?token=token2xxxxxxxxxxxxx"
      },
      {
        "email": "email-da-ton-tai@example.com",
        "error": "Email da ton tai"
      }
    ],
    "success": 2,
    "failed": 1
  },
  "code": 200,
  "message": ""
}
```

**Luu y:** API luon tra ve 200 ke ca khi mot so nhan vien that bai. Kiem tra truong `error` trong tung item de biet ket qua.

**Test loi:**
| Case | Cach test | Expected |
|------|-----------|----------|
| items rong | `"items": []` | 400, "Danh sach moi khong duoc trong" |
| Qua 50 item | Truyen 51+ item | 400, "Toi da 50 nhan vien moi lan" |
| Tat ca email trung | Moi nhan vien da co tai khoan | 200, `success: 0`, `failed: N` |
| Khong phai admin | Goi voi token staff thuong | 403 Forbidden |

---

## 18. Resend Invite

**Quyen:** IsAdmin (RequiredLogin + IsAdmin)
**Endpoint:** `POST /staffs/:id/resend-invite`

Gui lai email moi cho nhan vien co trang thai `pending` (chua chap nhan loi moi). He thong tao token moi voi hieu luc **48 gio** va vo hieu hoa token cu.

**Headers:**
| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| Authorization | Bearer {{ADMIN_TOKEN}} | Co |

**Path param:**
| Param | Type | Mo ta |
|-------|------|-------|
| id | string (MongoDB ObjectID) | `_id` cua staff can gui lai invite |

**Body:** Khong can body

**cURL:**
```bash
curl -X POST '{{ADMIN_BASE_URL}}/staffs/64a1b2c3d4e5f6a7b8c9d0e9/resend-invite' \
  -H 'Authorization: Bearer {{ADMIN_TOKEN}}'
```

**Response thanh cong (200):**
```json
{
  "data": {
    "_id": "64a1b2c3d4e5f6a7b8c9d0e9",
    "token": "",
    "inviteLink": "https://dashboard.example.com/vi/accept-invite?token=newToken456789012345678901234"
  },
  "code": 200,
  "message": ""
}
```

**Test loi:**
| Case | Cach test | Expected |
|------|-----------|----------|
| Staff khong ton tai | ID khong co trong DB | 400, "Khong tim thay nhan vien" |
| Staff da kich hoat | `inviteStatus: "accepted"` hoac `active: true` | 400, "Nhan vien nay da kich hoat tai khoan" |
| Khong phai admin | Goi voi token staff thuong | 403 Forbidden |
| ID khong hop le | `id` khong phai ObjectID | 400, validation error |

---

## Luu y chung

### Header x-device-id
Cac API Login va Accept Invite dung header `x-device-id` de gen JWT token gan voi thiet bi. Moi combination `(staffId, deviceId)` se co token rieng trong Redis. Khi logout hoac doi mat khau, tat ca token theo `staffId` bi xoa.

### Token JWT
- Het han sau **8 gio** ke tu luc tao
- Chua cac claim: `_id`, `name`, `email`, `phone`, `isRoot`, `deviceId`, `partner`
- Luu vao Redis voi TTL 8h, bi xoa khi doi mat khau / doi thong tin / disable

### Rate Limiting
- `/staffs/login`: co rate limiting phong chong brute force
- `/staffs/auth/exchange`: co rate limiting rieng

### InviteStatus values
| Gia tri | Y nghia |
|---------|---------|
| `pending` | Da gui invite, chua chap nhan |
| `accepted` | Da chap nhan, tai khoan hoat dong |

### Quyen truy cap
| Quyen | Mo ta |
|-------|-------|
| Public | Khong can token |
| RequiredLogin | Can `Authorization: Bearer {{ADMIN_TOKEN}}` hop le |
| IsAdmin | Can login + role admin (hoac `isRoot: true`) |
