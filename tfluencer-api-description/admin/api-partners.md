# API Partners - Admin

Base URL: `{{ADMIN_BASE_URL}}`
Auth header: `Authorization: Bearer {{ADMIN_TOKEN}}`

---

## Tong quan

| Method | Endpoint | Quyen | Mo ta |
|--------|----------|-------|-------|
| POST | `/partners` | IsRoot | Tao partner moi |
| PUT | `/partners/:id` | IsRoot | Cap nhat partner |
| PATCH | `/partners/:id/status` | IsRoot | Doi trang thai partner |
| GET | `/partners/:id` | IsRoot | Lay chi tiet partner |
| GET | `/partners` | RequiredLogin | Lay danh sach partner |
| GET | `/partners/users` | RequiredLogin | Lay danh sach user cua partner |
| GET | `/partners/:id/users/:userId` | RequiredLogin | Lay chi tiet user trong partner |

---

## 1. POST /partners - Tao partner

**Quyen:** IsRoot

### Headers
```
Content-Type: application/json
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Request Body
```json
{
  "name": "Techcombank HCM",
  "slug": "techcombank-hcm",
  "desc": "Chi nhanh Techcombank khu vuc Ho Chi Minh",
  "website": "https://example.com",
  "logo": {
    "_id": "64a1b2c3d4e5f6789012abcd",
    "name": "logo-techcombank.png",
    "dimensions": {
      "sm": { "url": "https://cdn.example.com/logo-sm.png", "width": 100, "height": 100 },
      "md": { "url": "https://cdn.example.com/logo-md.png", "width": 300, "height": 300 }
    }
  },
  "covers": [
    {
      "platform": "mobile",
      "photos": [
        {
          "_id": "64a1b2c3d4e5f6789012abce",
          "name": "cover-mobile.png",
          "dimensions": {
            "sm": { "url": "https://cdn.example.com/cover-sm.png", "width": 375, "height": 200 },
            "md": { "url": "https://cdn.example.com/cover-md.png", "width": 750, "height": 400 }
          }
        }
      ],
      "default": {
        "_id": "64a1b2c3d4e5f6789012abcf",
        "name": "cover-default.png",
        "dimensions": {
          "sm": { "url": "https://cdn.example.com/default-sm.png", "width": 375, "height": 200 },
          "md": { "url": "https://cdn.example.com/default-md.png", "width": 750, "height": 400 }
        }
      }
    }
  ]
}
```

### Validation Rules
| Field | Bat buoc | Mo ta |
|-------|----------|-------|
| `name` | Co | Ten partner |
| `slug` | Co | Chi co chu cai va so, khong dau cach |
| `website` | Khong | Phai la URL hop le |
| `logo` | Khong | Object FilePhoto |
| `covers` | Khong | Mang FilePhotoWithPlatform |
| `desc` | Khong | Mo ta partner |

### cURL
```bash
curl -X POST "{{ADMIN_BASE_URL}}/partners" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -d '{
    "name": "Techcombank HCM",
    "slug": "techcombank-hcm",
    "desc": "Chi nhanh Techcombank khu vuc Ho Chi Minh",
    "website": "https://example.com",
    "logo": null,
    "covers": []
  }'
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {
    "_id": "64f3a1b2c3d4e5f678901234",
    "name": "Techcombank HCM",
    "slug": "techcombank-hcm",
    "desc": "Chi nhanh Techcombank khu vuc Ho Chi Minh",
    "website": "https://example.com",
    "logo": null,
    "covers": [],
    "status": "inactive",
    "createdAt": "2026-03-20T08:00:00Z",
    "updatedAt": "2026-03-20T08:00:00Z"
  },
  "message": ""
}
```

### Test loi
| Case | Input | Expected |
|------|-------|----------|
| Thieu `name` | `name: ""` | 400 - name is required |
| Thieu `slug` | `slug: ""` | 400 - slug is required |
| Slug co ky tu dac biet | `slug: "my partner!"` | 400 - slug must be character and number |
| Website sai dinh dang | `website: "not-a-url"` | 400 - website invalid |
| Khong co quyen IsRoot | Token cua user thuong | 403 Forbidden |

---

## 2. PUT /partners/:id - Cap nhat partner

**Quyen:** IsRoot

### Headers
```
Content-Type: application/json
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Path Params
| Param | Mo ta |
|-------|-------|
| `id` | ID cua partner (MongoDB ObjectID) |

### Request Body
Tuong tu POST /partners (cung struct `PartnerUpsertBody`)
```json
{
  "name": "Techcombank HCM - Updated",
  "slug": "techcombank-hcm",
  "desc": "Cap nhat mo ta chi nhanh Techcombank HCM",
  "website": "https://example.com.vn",
  "logo": null,
  "covers": []
}
```

### cURL
```bash
curl -X PUT "{{ADMIN_BASE_URL}}/partners/{{PARTNER_ID}}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -d '{
    "name": "Techcombank HCM - Updated",
    "slug": "techcombank-hcm",
    "desc": "Cap nhat mo ta chi nhanh Techcombank HCM",
    "website": "https://example.com.vn",
    "logo": null,
    "covers": []
  }'
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {
    "_id": "{{PARTNER_ID}}",
    "name": "Techcombank HCM - Updated",
    "slug": "techcombank-hcm",
    "desc": "Cap nhat mo ta chi nhanh Techcombank HCM",
    "website": "https://example.com.vn",
    "status": "inactive",
    "updatedAt": "2026-03-20T09:00:00Z"
  },
  "message": ""
}
```

### Test loi
| Case | Input | Expected |
|------|-------|----------|
| ID khong ton tai | `id: "000000000000000000000000"` | 400 - not found |
| ID sai dinh dang | `id: "invalid-id"` | 400 bad request |
| Thieu `name` | `name: ""` | 400 - name is required |
| Thieu `slug` | `slug: ""` | 400 - slug is required |
| Khong co quyen IsRoot | Token cua user thuong | 403 Forbidden |

---

## 3. PATCH /partners/:id/status - Doi trang thai

**Quyen:** IsRoot

### Headers
```
Content-Type: application/json
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Path Params
| Param | Mo ta |
|-------|-------|
| `id` | ID cua partner |

### Request Body
```json
{
  "status": "active"
}
```

| Field | Bat buoc | Gia tri hop le |
|-------|----------|----------------|
| `status` | Co | `"active"`, `"inactive"` |

### cURL
```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/partners/{{PARTNER_ID}}/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -d '{"status": "active"}'
```

### cURL - Vo hieu hoa
```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/partners/{{PARTNER_ID}}/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -d '{"status": "inactive"}'
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {
    "_id": "{{PARTNER_ID}}",
    "status": "active",
    "updatedAt": "2026-03-20T09:30:00Z"
  },
  "message": ""
}
```

### Test loi
| Case | Input | Expected |
|------|-------|----------|
| `status` trong | `status: ""` | 400 - status invalid |
| `status` sai gia tri | `status: "pending"` | 400 - status invalid |
| Thieu truong `status` | Body rong `{}` | 400 - status invalid |
| Khong co quyen IsRoot | Token user thuong | 403 Forbidden |

---

## 4. GET /partners/:id - Lay chi tiet partner

**Quyen:** IsRoot

### Headers
```
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Path Params
| Param | Mo ta |
|-------|-------|
| `id` | ID cua partner |

### cURL
```bash
curl -X GET "{{ADMIN_BASE_URL}}/partners/{{PARTNER_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {
    "_id": "64f3a1b2c3d4e5f678901234",
    "name": "Techcombank HCM",
    "slug": "techcombank-hcm",
    "desc": "Chi nhanh Techcombank khu vuc Ho Chi Minh",
    "website": "https://example.com",
    "logo": {
      "_id": "64a1b2c3d4e5f6789012abcd",
      "name": "logo-techcombank.png",
      "dimensions": {
        "sm": { "url": "https://cdn.example.com/logo-sm.png" },
        "md": { "url": "https://cdn.example.com/logo-md.png" }
      }
    },
    "covers": [],
    "status": "active",
    "createdAt": "2026-03-20T08:00:00Z",
    "updatedAt": "2026-03-20T09:30:00Z"
  },
  "message": ""
}
```

### Test loi
| Case | Input | Expected |
|------|-------|----------|
| ID khong ton tai | `id: "000000000000000000000000"` | 400 - not found |
| ID sai dinh dang | `id: "abc"` | 400 bad request |
| Khong co quyen IsRoot | Token user thuong | 403 Forbidden |

---

## 5. GET /partners - Lay danh sach partner

**Quyen:** RequiredLogin

### Headers
```
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Query Params
| Param | Kieu | Bat buoc | Mo ta |
|-------|------|----------|-------|
| `page` | int | Khong | Trang hien tai (mac dinh: 1) |
| `limit` | int | Khong | So ban ghi moi trang (mac dinh: 20) |
| `keyword` | string | Khong | Tim kiem theo ten partner |
| `status` | string | Khong | Loc theo trang thai: `active`, `inactive` |

### cURL - Lay tat ca
```bash
curl -X GET "{{ADMIN_BASE_URL}}/partners?page=1&limit=20" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### cURL - Loc va tim kiem
```bash
curl -X GET "{{ADMIN_BASE_URL}}/partners?page=1&limit=10&keyword=techcombank&status=active" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {
    "data": [
      {
        "_id": "64f3a1b2c3d4e5f678901234",
        "name": "Techcombank HCM",
        "slug": "techcombank-hcm",
        "status": "active",
        "website": "https://example.com",
        "createdAt": "2026-03-20T08:00:00Z"
      },
      {
        "_id": "64f3a1b2c3d4e5f678905678",
        "name": "Techcombank HN",
        "slug": "techcombank-hn",
        "status": "active",
        "website": "https://example.com",
        "createdAt": "2026-03-19T08:00:00Z"
      }
    ],
    "total": 2,
    "limit": 20
  },
  "message": ""
}
```

### Test loi
| Case | Input | Expected |
|------|-------|----------|
| Token het han | Token cu | 401 Unauthorized |
| `status` sai gia tri | `status=unknown` | Tra ve tat ca (khong validate status o day) |

---

## 6. GET /partners/users - Lay danh sach user

**Quyen:** RequiredLogin

### Headers
```
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Query Params
| Param | Kieu | Bat buoc | Mo ta |
|-------|------|----------|-------|
| `page` | int | Khong | Trang hien tai |
| `limit` | int | Khong | So ban ghi moi trang |
| `partner` | string | Khong | Filter theo partner ID |
| `user` | string | Khong | Filter theo user ID |
| `keyword` | string | Khong | Tim kiem theo ten/email |
| `fromAt` | string | Khong | Tu ngay (ISO 8601 datetime, vd: `2026-01-01T00:00:00.000Z`) |
| `toAt` | string | Khong | Den ngay (ISO 8601 datetime, vd: `2026-03-31T23:59:59.000Z`) |
| `sort` | string | Khong | Sap xep (vd: `createdAt:-1`) |
| `code` | string | Khong | Ma the mo |
| `companyCode` | string | Khong | Ma cong ty |
| `codeTopics` | string | Khong | Ma chu de |
| `fromCash` | string | Khong | So tien tu (float) |
| `toCash` | string | Khong | So tien den (float) |

### cURL - Lay user theo partner
```bash
curl -X GET "{{ADMIN_BASE_URL}}/partners/users?page=1&limit=20&partner={{PARTNER_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### cURL - Loc nang cao
```bash
curl -X GET "{{ADMIN_BASE_URL}}/partners/users?page=1&limit=20&partner={{PARTNER_ID}}&fromAt=2026-01-01T00:00:00.000Z&toAt=2026-03-31T23:59:59.000Z&keyword=nguyen" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {
    "data": [
      {
        "_id": "64b2c3d4e5f678901234abcd",
        "name": "Nguyen Van A",
        "email": "user1@example.com",
        "phone": "0900000001",
        "partnerId": "64f3a1b2c3d4e5f678901234",
        "status": "active",
        "cash": 1500000,
        "createdAt": "2026-02-15T10:00:00Z"
      }
    ],
    "total": 1,
    "limit": 20
  },
  "message": ""
}
```

### Test loi
| Case | Input | Expected |
|------|-------|----------|
| Token het han | Token cu | 401 Unauthorized |
| `partner` ID sai dinh dang | `partner=invalid` | Co the tra ve ket qua rong |

---

## 7. GET /partners/:id/users/:userId - Chi tiet user trong partner

**Quyen:** RequiredLogin

### Headers
```
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Path Params
| Param | Mo ta |
|-------|-------|
| `id` | ID cua partner |
| `userId` | ID cua user (MongoDB ObjectID) |

### cURL
```bash
curl -X GET "{{ADMIN_BASE_URL}}/partners/{{PARTNER_ID}}/users/{{USER_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {
    "user": {
      "_id": "64b2c3d4e5f678901234abcd",
      "name": "Nguyen Van A",
      "email": "user1@example.com",
      "phone": "0900000001",
      "status": "active",
      "cash": 2500000,
      "totalWithdraw": 500000,
      "partnerId": "64f3a1b2c3d4e5f678901234",
      "createdAt": "2026-02-15T10:00:00Z"
    },
    "partner": {
      "_id": "64f3a1b2c3d4e5f678901234",
      "name": "Techcombank HCM",
      "slug": "techcombank-hcm"
    }
  },
  "message": ""
}
```

### Test loi
| Case | Input | Expected |
|------|-------|----------|
| `userId` trong | `userId: ""` | 400 - User ID is required |
| `userId` sai dinh dang | `userId: "abc"` | 400 - User ID is required |
| `userId` la zero ID | `userId: "000000000000000000000000"` | 400 - User ID is required |
| Partner ID khong ton tai | ID ngau nhien | 400 - not found |
| Token het han | Token cu | 401 Unauthorized |
