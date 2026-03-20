# API Users - Admin

Base URL: `{{ADMIN_BASE_URL}}` (vd: `https://api.example.com/admin`)

---

## Muc quyen

| Middleware | Mo ta |
|---|---|
| `RequiredLogin` | Phai co token hop le |
| `IsAdmin` | Phai la Admin (cap cao nhat) |

---

## 1. GetList - Lay danh sach nguoi dung

**Quyen:** `RequiredLogin`
**Endpoint:** `GET /users`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Khong | `application/json` |

### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `page` | int | Khong | So trang (mac dinh: 1) | `1` |
| `limit` | int | Khong | So ban ghi tren trang (mac dinh: 20) | `20` |
| `keyword` | string | Khong | Tim kiem theo ten / email | `nguyen van a` |
| `status` | string | Khong | Trang thai tai khoan | `active` / `inactive` |
| `isBanned` | string | Khong | Loc theo trang thai ban | `true` / `false` |
| `partner` | string | Khong | ID partner | `664a1f2e3c4b5d6e7f8a9b0c` |
| `code` | string | Khong | Ma nhan vien | `TCB001` |
| `companyCode` | string | Khong | Ma cong ty | `TCB` |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/users?page=1&limit=20&keyword=nguyen&status=active" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "docs": [
      {
        "_id": "664a1f2e3c4b5d6e7f8a9b0c",
        "name": "Nguyen Van A",
        "email": "user@example.com",
        "staffCode": "TCB001",
        "companyCode": "TCB",
        "status": "active",
        "isBanned": false,
        "partner": "664a1f2e3c4b5d6e7f8a9b01",
        "createdAt": "2024-01-15T08:30:00Z",
        "updatedAt": "2024-03-10T14:22:00Z"
      },
      {
        "_id": "664a1f2e3c4b5d6e7f8a9b0d",
        "name": "Tran Thi B",
        "email": "user2@example.com",
        "staffCode": "TCB002",
        "companyCode": "TCB",
        "status": "active",
        "isBanned": false,
        "partner": "664a1f2e3c4b5d6e7f8a9b01",
        "createdAt": "2024-02-01T09:00:00Z",
        "updatedAt": "2024-03-12T10:00:00Z"
      }
    ],
    "total": 152,
    "page": 1,
    "limit": 20,
    "totalPages": 8
  }
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| Khong co token | `401` | `{"code": 401, "message": "Unauthorized"}` |
| Token het han | `401` | `{"code": 401, "message": "Token expired"}` |
| Khong co quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 2. CreateUser - Tao nguoi dung moi

**Quyen:** `RequiredLogin`
**Endpoint:** `POST /users`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `name` | string | Khong | Ho ten nguoi dung | `"Le Thi C"` |
| `partner` | string | **Co** | ID partner | `"664a1f2e3c4b5d6e7f8a9b01"` |
| `email` | string | Khong | Email | `"user3@example.com"` |
| `staffCode` | string | Khong | Ma nhan vien | `"TCB003"` |
| `companyCode` | string | Khong | Ma cong ty | `"TCB"` |

### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/users" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Le Thi C",
    "partner": "664a1f2e3c4b5d6e7f8a9b01",
    "email": "user3@example.com",
    "staffCode": "TCB003",
    "companyCode": "TCB"
  }'
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {}
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| Thieu `partner` | `400` | `{"code": 400, "message": "partner is required"}` |
| Token khong hop le | `401` | `{"code": 401, "message": "Unauthorized"}` |
| Email da ton tai | `400` | `{"code": 400, "message": "email already exists"}` |

---

## 3. CreateUserSocial - Tao social cho nguoi dung

**Quyen:** `RequiredLogin`
**Endpoint:** `POST /users/create-user-social`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `userId` | string | **Co** | ID nguoi dung | `"664a1f2e3c4b5d6e7f8a9b0c"` |
| `source` | string | **Co** | Nen tang mang xa hoi | `"tiktok"` / `"youtube"` / `"facebook"` |
| `link` | string | Khong | Link kenh | `"https://www.tiktok.com/@nguyenvana"` |
| `channelId` | string | Khong | ID kenh | `"@nguyenvana"` |
| `name` | string | Khong | Ten kenh | `"Nguyen Van A Official"` |

### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/users/create-user-social" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "{{USER_ID}}",
    "source": "tiktok",
    "link": "https://www.tiktok.com/@nguyenvana",
    "channelId": "@nguyenvana",
    "name": "Nguyen Van A Official"
  }'
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {}
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| Thieu `userId` | `400` | `{"code": 400, "message": "userId is required"}` |
| Thieu `source` | `400` | `{"code": 400, "message": "source is required"}` |
| `userId` khong ton tai | `400` | `{"code": 400, "message": "user not found"}` |

---

## 4. GetDetail - Lay chi tiet nguoi dung

**Quyen:** `RequiredLogin` + `IsAdmin`
**Endpoint:** `GET /users/:id`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

### Path Params

| Param | Bat buoc | Mo ta |
|---|---|---|
| `id` | Co | MongoDB ObjectID cua nguoi dung |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/users/{{USER_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "data": {
      "_id": "664a1f2e3c4b5d6e7f8a9b0c",
      "name": "Nguyen Van A",
      "email": "user@example.com",
      "staffCode": "TCB001",
      "companyCode": "TCB",
      "status": "active",
      "isBanned": false,
      "banReason": "",
      "partner": {
        "_id": "664a1f2e3c4b5d6e7f8a9b01",
        "name": "Techcombank"
      },
      "socials": [],
      "identification": {
        "frontImage": "https://cdn.example.com/id-front.jpg",
        "backImage": "https://cdn.example.com/id-back.jpg",
        "status": "approved"
      },
      "createdAt": "2024-01-15T08:30:00Z",
      "updatedAt": "2024-03-10T14:22:00Z"
    }
  }
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| `id` khong phai ObjectID | `400` | `{"code": 400, "message": "invalid id"}` |
| User khong ton tai | `400` | `{"code": 400, "message": "user not found"}` |
| Khong co quyen Admin | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 5. GetListSocial - Lay danh sach social cua nguoi dung

**Quyen:** `RequiredLogin` + `IsAdmin`
**Endpoint:** `GET /users/:id/socials`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

### Path Params

| Param | Bat buoc | Mo ta |
|---|---|---|
| `id` | Co | MongoDB ObjectID cua nguoi dung |

### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `page` | int | Khong | So trang | `1` |
| `limit` | int | Khong | So ban ghi | `20` |
| `source` | string | Khong | Loc theo nen tang | `"tiktok"` |
| `fromAt` | string | Khong | Tu ngay (ISO 8601 datetime) | `"2024-01-01T00:00:00.000Z"` |
| `toAt` | string | Khong | Den ngay (ISO 8601 datetime) | `"2024-03-31T23:59:59.000Z"` |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/users/{{USER_ID}}/socials?page=1&limit=20&source=tiktok" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "docs": [
      {
        "_id": "664a1f2e3c4b5d6e7f8a9b10",
        "userId": "664a1f2e3c4b5d6e7f8a9b0c",
        "source": "tiktok",
        "link": "https://www.tiktok.com/@nguyenvana",
        "channelId": "@nguyenvana",
        "name": "Nguyen Van A Official",
        "follower": 125000,
        "status": "active",
        "createdAt": "2024-01-20T10:00:00Z"
      },
      {
        "_id": "664a1f2e3c4b5d6e7f8a9b11",
        "userId": "664a1f2e3c4b5d6e7f8a9b0c",
        "source": "youtube",
        "link": "https://www.youtube.com/@nguyenvana",
        "channelId": "UCxxxxxxxxxxx",
        "name": "Nguyen Van A - Channel",
        "follower": 45000,
        "status": "active",
        "createdAt": "2024-02-05T08:00:00Z"
      }
    ],
    "total": 2,
    "page": 1,
    "limit": 20,
    "totalPages": 1
  }
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| `id` khong hop le | `400` | `{"code": 400, "message": "invalid id"}` |
| User khong ton tai | `400` | `{"code": 400, "message": "user not found"}` |
| Khong co quyen Admin | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 6. Ban - Khoa nguoi dung

**Quyen:** `RequiredLogin` + `IsAdmin`
**Endpoint:** `PATCH /users/:id/ban`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

### Path Params

| Param | Bat buoc | Mo ta |
|---|---|---|
| `id` | Co | MongoDB ObjectID cua nguoi dung |

### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `reason` | string | Khong | Ly do khoa tai khoan | `"Vi pham dieu khoan su dung"` |

> **Luu y:** `reason` duoc doc tu `query` param trong model (`query:"reason"`), co the gui qua query string hoac body.

### cURL

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/users/{{USER_ID}}/ban" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Vi pham dieu khoan su dung: dang noi dung khong phu hop"
  }'
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {}
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| User khong ton tai | `400` | `{"code": 400, "message": "user not found"}` |
| User da bi ban | `400` | `{"code": 400, "message": "user already banned"}` |
| Khong co quyen Admin | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 7. UnBan - Mo khoa nguoi dung

**Quyen:** `RequiredLogin` + `IsAdmin`
**Endpoint:** `PATCH /users/:id/un-ban`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

### Path Params

| Param | Bat buoc | Mo ta |
|---|---|---|
| `id` | Co | MongoDB ObjectID cua nguoi dung |

### cURL

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/users/{{USER_ID}}/un-ban" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {}
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| User khong ton tai | `400` | `{"code": 400, "message": "user not found"}` |
| User chua bi ban | `400` | `{"code": 400, "message": "user not banned"}` |
| Khong co quyen Admin | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 8. RejectedContract - Tu choi hop dong

**Quyen:** `RequiredLogin` + `IsAdmin`
**Endpoint:** `PATCH /users/:id/reject-contract`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

### Path Params

| Param | Bat buoc | Mo ta |
|---|---|---|
| `id` | Co | MongoDB ObjectID cua nguoi dung |

### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `reason` | string | Khong | Ly do tu choi hop dong | `"Thong tin CCCD khong hop le"` |

### cURL

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/users/{{USER_ID}}/reject-contract" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Thong tin CCCD khong hop le hoac khong ro rang"
  }'
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {}
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| User khong ton tai | `400` | `{"code": 400, "message": "user not found"}` |
| Hop dong khong o trang thai cho duyet | `400` | `{"code": 400, "message": "contract status invalid"}` |
| Khong co quyen Admin | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 9. CreateContractByUserId - Tao hop dong theo danh sach user

**Quyen:** `RequiredLogin` + `IsAdmin`
**Endpoint:** `POST /users/contract/generate-by-user-id`

> **Luu y:** Xu ly bat dong bo (async) - API tra ve ngay lap tuc, hop dong duoc tao o background.

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `userIds` | array[string] | Khong | Danh sach ID nguoi dung can tao hop dong | `["664a...0c", "664a...0d"]` |

### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/users/contract/generate-by-user-id" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "userIds": [
      "664a1f2e3c4b5d6e7f8a9b0c",
      "664a1f2e3c4b5d6e7f8a9b0d",
      "664a1f2e3c4b5d6e7f8a9b0e"
    ]
  }'
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {}
}
```

> API luon tra ve `200` ngay lap tuc. Ket qua tao hop dong duoc xu ly o background - kiem tra trang thai qua he thong thong bao hoac log.

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| Body khong phai JSON | `400` | `{"code": 400, "message": "Bad request"}` |
| Khong co quyen Admin | `403` | `{"code": 403, "message": "Forbidden"}` |
| Token khong hop le | `401` | `{"code": 401, "message": "Unauthorized"}` |

---

## Tom tat cac endpoint

| Method | Endpoint | Quyen | Mo ta |
|---|---|---|---|
| `GET` | `/users` | RequiredLogin | Lay danh sach nguoi dung |
| `POST` | `/users` | RequiredLogin | Tao nguoi dung moi |
| `POST` | `/users/create-user-social` | RequiredLogin | Tao social cho nguoi dung |
| `GET` | `/users/:id` | RequiredLogin + IsAdmin | Lay chi tiet nguoi dung |
| `GET` | `/users/:id/socials` | RequiredLogin + IsAdmin | Lay danh sach social |
| `PATCH` | `/users/:id/ban` | RequiredLogin + IsAdmin | Khoa nguoi dung |
| `PATCH` | `/users/:id/un-ban` | RequiredLogin + IsAdmin | Mo khoa nguoi dung |
| `PATCH` | `/users/:id/reject-contract` | RequiredLogin + IsAdmin | Tu choi hop dong |
| `POST` | `/users/contract/generate-by-user-id` | RequiredLogin + IsAdmin | Tao hop dong hang loat |
