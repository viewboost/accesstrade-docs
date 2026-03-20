# API Transfers - Admin

Base URL: `{{ADMIN_BASE_URL}}`
Auth header: `Authorization: Bearer {{ADMIN_TOKEN}}`

---

## Tong quan

Tat ca cac endpoint duoi day yeu cau quyen **IsAdmin**.

| Method | Endpoint | Mo ta |
|--------|----------|-------|
| GET | `/transfers` | Lay danh sach transfer |
| POST | `/transfers` | Tao transfer moi |
| PUT | `/transfers/:id` | Cap nhat transfer |
| GET | `/transfers/:id` | Lay chi tiet transfer |
| GET | `/transfers/:id/withdraw-cashes` | Lay danh sach lenh rut tien |
| PUT | `/transfers/:id/change-status` | Doi trang thai transfer |
| PATCH | `/transfers/:id/change-declined` | Doi trang thai lenh rut sang Declined |

---

## Cau truc du lieu

### Transfer - Trang thai hop le

| Gia tri | Mo ta |
|---------|-------|
| `processing` | Dang xu ly |
| `transferring` | Dang chuyen tien |
| `finished` | Hoan thanh |
| `rejected` | Tu choi |

### WithdrawCash - Type

| Gia tri | Mo ta |
|---------|-------|
| `confirm` | Lenh rut da xac nhan |
| `declined` | Lenh rut bi tu choi |

### WithdrawTableType (cho ChangeDeclined)

| Gia tri | Mo ta |
|---------|-------|
| `Confirm` | Bang xac nhan |
| `Rejected` | Bang tu choi |

---

## 1. GET /transfers - Lay danh sach transfer

**Quyen:** IsAdmin

### Headers
```
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Query Params
| Param | Kieu | Bat buoc | Mo ta |
|-------|------|----------|-------|
| `page` | int | Khong | Trang hien tai (>= 0, mac dinh: 1) |
| `limit` | int | Khong | So ban ghi moi trang (>= 0, mac dinh: 20) |
| `keyword` | string | Khong | Tim kiem theo ten transfer |
| `status` | string | Khong | Loc theo trang thai: `processing`, `transferring`, `finished`, `rejected` |
| `partner` | string | Khong | Loc theo partner ID (query param truc tiep) |

### cURL - Lay tat ca
```bash
curl -X GET "{{ADMIN_BASE_URL}}/transfers?page=1&limit=20" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### cURL - Loc theo trang thai va partner
```bash
curl -X GET "{{ADMIN_BASE_URL}}/transfers?page=1&limit=10&status=processing&partner={{PARTNER_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### cURL - Tim kiem theo ten
```bash
curl -X GET "{{ADMIN_BASE_URL}}/transfers?page=1&limit=20&keyword=thang3" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {
    "data": [
      {
        "_id": "64f7a8b9c0d1e2345678abcd",
        "name": "Chi tra T-Fluencers Thang 3/2026",
        "status": "processing",
        "partner": {
          "_id": "64f3a1b2c3d4e5f678901234",
          "name": "Techcombank HCM",
          "slug": "techcombank-hcm"
        },
        "conditions": {
          "startAt": "2026-03-01",
          "endAt": "2026-03-31",
          "minValueCashRemaining": 100000,
          "maxCashWithdraw": 10000000
        },
        "createdBy": "64a0b1c2d3e4f5678901abcd",
        "createdAt": "2026-03-20T08:00:00Z",
        "updatedAt": "2026-03-20T08:00:00Z"
      },
      {
        "_id": "64f7a8b9c0d1e2345678abce",
        "name": "Chi tra T-Fluencers Thang 2/2026",
        "status": "finished",
        "partner": {
          "_id": "64f3a1b2c3d4e5f678901234",
          "name": "Techcombank HCM"
        },
        "conditions": {
          "startAt": "2026-02-01",
          "endAt": "2026-02-28",
          "minValueCashRemaining": 100000,
          "maxCashWithdraw": 5000000
        },
        "createdAt": "2026-02-28T08:00:00Z",
        "updatedAt": "2026-03-15T10:00:00Z"
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
| `page` am | `page=-1` | 400 - page invalid |
| `limit` am | `limit=-5` | 400 - limit invalid |
| Token het han | Token cu | 401 Unauthorized |
| Khong co quyen IsAdmin | Token staff thuong | 403 Forbidden |

---

## 2. POST /transfers - Tao transfer moi

**Quyen:** IsAdmin

### Headers
```
Content-Type: application/json
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Request Body
```json
{
  "name": "Chi tra T-Fluencers Thang 4/2026",
  "partner": "64f3a1b2c3d4e5f678901234",
  "conditions": {
    "startAt": "2026-04-01",
    "endAt": "2026-04-30",
    "minValueCashRemaining": 100000,
    "maxCashWithdraw": 10000000
  }
}
```

### Validation Rules
| Field | Bat buoc | Mo ta |
|-------|----------|-------|
| `name` | Co | Ten dot chi tra |
| `partner` | Co | ID cua partner (MongoDB ObjectID) |
| `conditions.startAt` | Khong | Ngay bat dau (ISO 8601 date string) |
| `conditions.endAt` | Khong | Ngay ket thuc (ISO 8601 date string) |
| `conditions.minValueCashRemaining` | Khong | So du toi thieu de duoc rut (float) |
| `conditions.maxCashWithdraw` | Khong | So tien toi da moi lenh rut (float) |

### cURL
```bash
curl -X POST "{{ADMIN_BASE_URL}}/transfers" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -d '{
    "name": "Chi tra T-Fluencers Thang 4/2026",
    "partner": "64f3a1b2c3d4e5f678901234",
    "conditions": {
      "startAt": "2026-04-01",
      "endAt": "2026-04-30",
      "minValueCashRemaining": 100000,
      "maxCashWithdraw": 10000000
    }
  }'
```

### cURL - Khong co dieu kien
```bash
curl -X POST "{{ADMIN_BASE_URL}}/transfers" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -d '{
    "name": "Chi tra T-Fluencers Thang 4/2026",
    "partner": "64f3a1b2c3d4e5f678901234",
    "conditions": {}
  }'
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {
    "_id": "64f8b9c0d1e2f3456789abcd",
    "name": "Chi tra T-Fluencers Thang 4/2026",
    "status": "processing",
    "partner": "64f3a1b2c3d4e5f678901234",
    "conditions": {
      "startAt": "2026-04-01",
      "endAt": "2026-04-30",
      "minValueCashRemaining": 100000,
      "maxCashWithdraw": 10000000
    },
    "createdBy": "64a0b1c2d3e4f5678901abcd",
    "createdAt": "2026-03-20T09:00:00Z",
    "updatedAt": "2026-03-20T09:00:00Z"
  },
  "message": ""
}
```

### Test loi
| Case | Input | Expected |
|------|-------|----------|
| Thieu `name` | `name: ""` | 400 - name is required |
| Thieu `partner` | `partner: ""` | 400 - partner not found |
| `partner` khong ton tai | `partner: "000000000000000000000000"` | 400 - partner not found |
| Khong co quyen IsAdmin | Token staff thuong | 403 Forbidden |

---

## 3. PUT /transfers/:id - Cap nhat transfer

**Quyen:** IsAdmin

### Headers
```
Content-Type: application/json
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Path Params
| Param | Mo ta |
|-------|-------|
| `id` | ID cua transfer |

### Request Body
Tuong tu POST /transfers (cung struct `TransferBody`)
```json
{
  "name": "Chi tra T-Fluencers Thang 4/2026 - Cap nhat",
  "partner": "64f3a1b2c3d4e5f678901234",
  "conditions": {
    "startAt": "2026-04-01",
    "endAt": "2026-04-30",
    "minValueCashRemaining": 150000,
    "maxCashWithdraw": 15000000
  }
}
```

### cURL
```bash
curl -X PUT "{{ADMIN_BASE_URL}}/transfers/{{TRANSFER_ID}}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -d '{
    "name": "Chi tra T-Fluencers Thang 4/2026 - Cap nhat",
    "partner": "64f3a1b2c3d4e5f678901234",
    "conditions": {
      "startAt": "2026-04-01",
      "endAt": "2026-04-30",
      "minValueCashRemaining": 150000,
      "maxCashWithdraw": 15000000
    }
  }'
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {
    "_id": "{{TRANSFER_ID}}",
    "name": "Chi tra T-Fluencers Thang 4/2026 - Cap nhat",
    "status": "processing",
    "partner": "64f3a1b2c3d4e5f678901234",
    "conditions": {
      "startAt": "2026-04-01",
      "endAt": "2026-04-30",
      "minValueCashRemaining": 150000,
      "maxCashWithdraw": 15000000
    },
    "updatedAt": "2026-03-20T10:00:00Z"
  },
  "message": ""
}
```

### Test loi
| Case | Input | Expected |
|------|-------|----------|
| ID khong ton tai | `id: "000000000000000000000000"` | 400 - not found |
| Thieu `name` | `name: ""` | 400 - name is required |
| Thieu `partner` | `partner: ""` | 400 - partner not found |
| Khong co quyen IsAdmin | Token staff thuong | 403 Forbidden |

---

## 4. GET /transfers/:id - Lay chi tiet transfer

**Quyen:** IsAdmin

### Headers
```
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Path Params
| Param | Mo ta |
|-------|-------|
| `id` | ID cua transfer |

### cURL
```bash
curl -X GET "{{ADMIN_BASE_URL}}/transfers/{{TRANSFER_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {
    "_id": "64f8b9c0d1e2f3456789abcd",
    "name": "Chi tra T-Fluencers Thang 4/2026",
    "status": "processing",
    "partner": {
      "_id": "64f3a1b2c3d4e5f678901234",
      "name": "Techcombank HCM",
      "slug": "techcombank-hcm"
    },
    "conditions": {
      "startAt": "2026-04-01",
      "endAt": "2026-04-30",
      "minValueCashRemaining": 100000,
      "maxCashWithdraw": 10000000
    },
    "totalWithdrawConfirm": 42,
    "totalWithdrawDeclined": 3,
    "totalCash": 8500000,
    "createdBy": "64a0b1c2d3e4f5678901abcd",
    "createdAt": "2026-03-20T09:00:00Z",
    "updatedAt": "2026-03-20T09:00:00Z"
  },
  "message": ""
}
```

### Test loi
| Case | Input | Expected |
|------|-------|----------|
| ID khong ton tai | `id: "000000000000000000000000"` | 400 - not found |
| ID sai dinh dang | `id: "invalid"` | 400 bad request |
| Token het han | Token cu | 401 Unauthorized |
| Khong co quyen IsAdmin | Token staff thuong | 403 Forbidden |

---

## 5. GET /transfers/:id/withdraw-cashes - Lay danh sach lenh rut tien

**Quyen:** IsAdmin

### Headers
```
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Path Params
| Param | Mo ta |
|-------|-------|
| `id` | ID cua transfer |

### Query Params
| Param | Kieu | Bat buoc | Mo ta |
|-------|------|----------|-------|
| `page` | int | Khong | Trang hien tai (>= 0) |
| `limit` | int | Khong | So ban ghi moi trang (>= 0) |
| `type` | string | **Co** | Loai lenh: `confirm` hoac `declined` |
| `keyword` | string | Khong | Tim kiem |
| `user` | string | Khong | Filter theo user ID |
| `status` | string | Khong | Filter theo trang thai |
| `cardNumber` | string | Khong | Filter theo so the ngan hang |

### cURL - Lay lenh rut da xac nhan
```bash
curl -X GET "{{ADMIN_BASE_URL}}/transfers/{{TRANSFER_ID}}/withdraw-cashes?page=1&limit=20&type=confirm" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### cURL - Lay lenh rut da tu choi
```bash
curl -X GET "{{ADMIN_BASE_URL}}/transfers/{{TRANSFER_ID}}/withdraw-cashes?page=1&limit=20&type=declined" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### cURL - Loc theo so the
```bash
curl -X GET "{{ADMIN_BASE_URL}}/transfers/{{TRANSFER_ID}}/withdraw-cashes?page=1&limit=20&type=confirm&cardNumber=19001234567890" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {
    "data": [
      {
        "_id": "64f9c0d1e2f3a4567890abcd",
        "user": {
          "_id": "64b2c3d4e5f678901234abcd",
          "name": "Nguyen Van A",
          "email": "nguyenvana@gmail.com",
          "phone": "0912345678"
        },
        "amount": 500000,
        "status": "confirm",
        "cardNumber": "19001234567890",
        "bankName": "Techcombank",
        "bankAccountName": "NGUYEN VAN A",
        "transferId": "64f8b9c0d1e2f3456789abcd",
        "createdAt": "2026-03-18T10:00:00Z",
        "updatedAt": "2026-03-18T10:00:00Z"
      },
      {
        "_id": "64f9c0d1e2f3a4567890abce",
        "user": {
          "_id": "64b2c3d4e5f678901234abce",
          "name": "Tran Thi B",
          "email": "tranthib@gmail.com",
          "phone": "0987654321"
        },
        "amount": 750000,
        "status": "confirm",
        "cardNumber": "19009876543210",
        "bankName": "Techcombank",
        "bankAccountName": "TRAN THI B",
        "transferId": "64f8b9c0d1e2f3456789abcd",
        "createdAt": "2026-03-18T11:00:00Z",
        "updatedAt": "2026-03-18T11:00:00Z"
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
| Thieu `type` | `type` khong truyen | 400 - type is required |
| `type` sai gia tri | `type=pending` | 400 - type invalid |
| `page` am | `page=-1` | 400 - page invalid |
| `limit` am | `limit=-5` | 400 - limit invalid |
| Transfer ID khong ton tai | `id: "000000000000000000000000"` | Tra ve ket qua rong |
| Token het han | Token cu | 401 Unauthorized |

---

## 6. PUT /transfers/:id/change-status - Doi trang thai transfer

**Quyen:** IsAdmin

### Headers
```
Content-Type: application/json
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Path Params
| Param | Mo ta |
|-------|-------|
| `id` | ID cua transfer |

### Request Body
```json
{
  "status": "transferring",
  "reason": ""
}
```

| Field | Bat buoc | Gia tri hop le | Mo ta |
|-------|----------|----------------|-------|
| `status` | Khong | `processing`, `transferring`, `finished`, `rejected` | Trang thai moi |
| `reason` | Khong | string | Ly do (bat buoc khi `status = "rejected"`) |

### cURL - Chuyen sang "Dang chuyen tien"
```bash
curl -X PUT "{{ADMIN_BASE_URL}}/transfers/{{TRANSFER_ID}}/change-status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -d '{"status": "transferring", "reason": ""}'
```

### cURL - Hoan thanh
```bash
curl -X PUT "{{ADMIN_BASE_URL}}/transfers/{{TRANSFER_ID}}/change-status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -d '{"status": "finished", "reason": ""}'
```

### cURL - Tu choi voi ly do
```bash
curl -X PUT "{{ADMIN_BASE_URL}}/transfers/{{TRANSFER_ID}}/change-status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -d '{"status": "rejected", "reason": "Khong du dieu kien chi tra trong ky nay"}'
```

### Luong chuyen trang thai thuong gap
```
processing -> transferring -> finished
processing -> rejected
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {
    "_id": "{{TRANSFER_ID}}",
    "status": "transferring",
    "reason": "",
    "updatedAt": "2026-03-20T14:00:00Z"
  },
  "message": ""
}
```

### Test loi
| Case | Input | Expected |
|------|-------|----------|
| `status` sai gia tri | `status: "pending"` | 400 - status invalid |
| ID khong ton tai | `id: "000000000000000000000000"` | 400 - not found |
| Token het han | Token cu | 401 Unauthorized |
| Khong co quyen IsAdmin | Token staff thuong | 403 Forbidden |

---

## 7. PATCH /transfers/:id/change-declined - Doi sang Declined

**Quyen:** IsAdmin

Dung de chuyen mot danh sach lenh rut tien tu trang thai hien tai sang trang thai tu choi (Declined).

### Headers
```
Content-Type: application/json
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Path Params
| Param | Mo ta |
|-------|-------|
| `id` | ID cua transfer |

### Request Body
```json
{
  "withdrawIDs": [
    "64f9c0d1e2f3a4567890abcd",
    "64f9c0d1e2f3a4567890abce",
    "64f9c0d1e2f3a4567890abcf"
  ],
  "currentType": "Confirm"
}
```

| Field | Bat buoc | Gia tri hop le | Mo ta |
|-------|----------|----------------|-------|
| `withdrawIDs` | Co | Mang MongoDB ObjectID | Danh sach ID lenh rut can chuyen sang Declined |
| `currentType` | Co | `"Confirm"`, `"Rejected"` | Bang nguon chua cac lenh rut nay |

> **Luu y:** `currentType` phan biet chu hoa: `"Confirm"` (C hoa) va `"Rejected"` (R hoa).

### cURL - Chuyen lenh tu Confirm sang Declined
```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/transfers/{{TRANSFER_ID}}/change-declined" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -d '{
    "withdrawIDs": [
      "64f9c0d1e2f3a4567890abcd",
      "64f9c0d1e2f3a4567890abce"
    ],
    "currentType": "Confirm"
  }'
```

### cURL - Chuyen lai tu Rejected sang Declined
```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/transfers/{{TRANSFER_ID}}/change-declined" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -d '{
    "withdrawIDs": [
      "64f9c0d1e2f3a4567890abcf"
    ],
    "currentType": "Rejected"
  }'
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {},
  "message": ""
}
```

> **Luu y:** Response tra ve object rong `{}`. Kiem tra ket qua bang GET /transfers/:id/withdraw-cashes?type=declined.

### Test loi
| Case | Input | Expected |
|------|-------|----------|
| `withdrawIDs` rong | `withdrawIDs: []` | 400 - withdrawID is required |
| `withdrawIDs` chua ID sai dinh dang | `withdrawIDs: ["not-a-mongo-id"]` | 400 - ID mongo invalid |
| Thieu `currentType` | `currentType: ""` | 400 - table type is required |
| `currentType` sai gia tri | `currentType: "confirm"` (chu thuong) | 400 - table type invalid |
| Transfer ID khong ton tai | `id: "000000000000000000000000"` | 400 - not found |
| Token het han | Token cu | 401 Unauthorized |
| Khong co quyen IsAdmin | Token staff thuong | 403 Forbidden |
