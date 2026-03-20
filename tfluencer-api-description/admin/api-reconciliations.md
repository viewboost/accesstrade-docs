# API Reconciliations - Tai lieu test API

## Thong tin chung

| Muc | Gia tri |
|-----|---------|
| Base URL | `{{ADMIN_BASE_URL}}/reconciliations` |
| Content-Type | `application/json` |
| Quyen | **IsAdmin** (tat ca endpoints) |

> Thay `{{ADMIN_BASE_URL}}` bang URL server admin thuc te. VD: `https://admin-api.viewboost.vn`

---

## Headers bat buoc (moi request)

| Header | Gia tri | Ghi chu |
|--------|---------|---------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | JWT token admin |
| `Content-Type` | `application/json` | Voi cac API co body (POST/PATCH) |

---

## Bien duong dan (Path variables)

| Bien | Mo ta | Vi du |
|------|-------|-------|
| `{{RECONCILIATION_ID}}` | MongoDB ObjectID cua reconciliation | `6650a1b2c3d4e5f6a7b8c9d0` |
| `{{EVENT_ID}}` | MongoDB ObjectID cua event | `6650a1b2c3d4e5f6a7b8c9d1` |
| `{{ITEM_ID}}` | MongoDB ObjectID cua reconciliation item (content) | `6650a1b2c3d4e5f6a7b8c9d2` |

---

## Trang thai (Status values)

| Status | Y nghia |
|--------|---------|
| `pending` | Cho xu ly |
| `processing` | Dang xu ly |
| `running` | Dang chay |
| `completed` | Hoan thanh |
| `rejected` | Tu choi |

## Loai reconciliation (Type values)

| Type | Y nghia |
|------|---------|
| `event-reward` | Doi soat phan thuong su kien (content) |
| `event-reward-statistic` | Doi soat theo thong ke su kien |
| `event-reward-milestone` | Doi soat moc thuong su kien |

## Phan loai checklist (Classification values)

| Classification | Y nghia |
|----------------|---------|
| `auto_approved` | Tu dong duyet boi he thong |
| `auto_rejected` | Tu dong tu choi boi he thong |
| `needs_review` | Can kiem tra thu cong |

---

## Danh sach API

| # | Method | Endpoint | Mo ta |
|---|--------|----------|-------|
| 1 | GET | `/reconciliations` | Lay danh sach reconciliation |
| 2 | POST | `/reconciliations` | Tao reconciliation moi |
| 3 | PATCH | `/reconciliations/:id` | Cap nhat reconciliation |
| 4 | GET | `/reconciliations/:id` | Lay chi tiet reconciliation |
| 5 | PATCH | `/reconciliations/:id/change-status` | Doi trang thai reconciliation |
| 6 | GET | `/reconciliations/:id/content` | Lay danh sach content items |
| 7 | GET | `/reconciliations/:id/milestone` | Lay danh sach milestone items |
| 8 | GET | `/reconciliations/:id/bonus` | Lay danh sach bonus items |
| 9 | PATCH | `/reconciliations/:id/item/:idItem/change-status` | Doi trang thai item |
| 10 | PATCH | `/reconciliations/events/:eventId/close` | Dong reconciliation theo event |
| 11 | POST | `/reconciliations/events/:eventId/makeup-crawl` | Chay lai crawl bo sung |
| 12 | POST | `/reconciliations/:id/evaluate` | Evaluate checklist tu dong |
| 13 | POST | `/reconciliations/:id/apply-classification` | Ap dung phan loai vao trang thai |
| 14 | GET | `/reconciliations/:id/content/:itemId/checklist` | Lay checklist cua content item |
| 15 | PATCH | `/reconciliations/:id/content/:itemId/checklist` | Cap nhat thu cong checklist item |
| 16 | POST | `/reconciliations/:id/content/:itemId/quick-approve` | Duyet nhanh tat ca checklist |
| 17 | POST | `/reconciliations/:id/content/:itemId/quick-reject` | Tu choi nhanh tat ca checklist |
| 18 | PATCH | `/reconciliations/:id/content/:itemId/override` | Ghi de phan loai item |
| 19 | POST | `/reconciliations/:id/content/:itemId/confirm-status` | Xac nhan trang thai item |
| 20 | POST | `/reconciliations/:id/content/:itemId/reset-checklist` | Reset checklist item ve trang thai goc |

---

## Chi tiet tung API

---

### 1. GetList - Lay danh sach reconciliation

**Quyen:** IsAdmin
**Endpoint:** `GET /reconciliations`

**Query params:**

| Tham so | Kieu | Bat buoc | Mo ta | Vi du |
|---------|------|----------|-------|-------|
| `page` | int | Khong | Trang hien tai (bat dau tu 0) | `0` |
| `limit` | int | Khong | So ban ghi moi trang (max 100) | `20` |
| `keyword` | string | Khong | Tim kiem theo ten reconciliation | `doi soat thang 6` |
| `status` | string | Khong | Loc theo trang thai | `pending` |
| `type` | string | Khong | Loc theo loai | `event-reward` |
| `event` | string | Khong | Loc theo event ID | `6650a1b2c3d4e5f6a7b8c9d1` |
| `partner` | string | Khong | Loc theo partner ID | `6650a1b2c3d4e5f6a7b8c9d3` |

**cURL:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/reconciliations?page=0&limit=20&status=pending&type=event-reward" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json"
```

**Response mau (200):**

```json
{
  "data": {
    "list": [
      {
        "_id": "6650a1b2c3d4e5f6a7b8c9d0",
        "title": "Doi soat T-Fluencers Thang 6/2024",
        "status": "pending",
        "type": "event-reward",
        "conditions": {
          "fromAt": "2024-06-01T00:00:00Z",
          "toAt": "2024-06-30T23:59:59Z",
          "events": ["6650a1b2c3d4e5f6a7b8c9d1"]
        },
        "statistic": {
          "totalItem": 250,
          "totalItemRejected": 12,
          "totalItemCompleted": 198,
          "totalCash": 125000000,
          "totalCashRejected": 3500000,
          "totalCashCompleted": 98000000
        },
        "createdAt": "2024-06-15T08:00:00Z",
        "updatedAt": "2024-06-20T14:30:00Z"
      }
    ],
    "total": 1
  },
  "code": 200
}
```

**Test loi:**

| Truong hop | Input | HTTP | Message |
|-----------|-------|------|---------|
| Thieu token | Khong gui `Authorization` | 401 | `unauthorized` |
| Khong du quyen | Token khong phai IsAdmin | 403 | `forbidden` |
| Page am | `page=-1` | 400 | `page is invalid` |
| Limit am | `limit=-5` | 400 | `limit is invalid` |

---

### 2. Create - Tao reconciliation moi

**Quyen:** IsAdmin
**Endpoint:** `POST /reconciliations`

**Body:**

| Truong | Kieu | Bat buoc | Mo ta | Vi du |
|--------|------|----------|-------|-------|
| `title` | string | Co | Ten reconciliation | `Doi soat T-Fluencers Q3/2024` |
| `type` | string | Co | Loai: `event-reward`, `event-reward-statistic`, `event-reward-milestone` | `event-reward` |
| `condition` | object | Co | Dieu kien doi soat | |
| `condition.toAt` | string | Co | Ngay ket thuc (ISO date) | `2024-09-30` |
| `condition.event` | string | Khong | Event ID | `6650a1b2c3d4e5f6a7b8c9d1` |

**cURL:**

```bash
curl -X POST "{{ADMIN_BASE_URL}}/reconciliations" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Doi soat T-Fluencers Thang 9/2024",
    "type": "event-reward",
    "condition": {
      "toAt": "2024-09-30",
      "event": "{{EVENT_ID}}"
    }
  }'
```

**Response mau (200):**

```json
{
  "data": {
    "_id": "6650a1b2c3d4e5f6a7b8c9d0",
    "title": "Doi soat T-Fluencers Thang 9/2024",
    "status": "pending",
    "type": "event-reward",
    "conditions": {
      "toAt": "2024-09-30T00:00:00Z",
      "events": ["6650a1b2c3d4e5f6a7b8c9d1"]
    },
    "statistic": {
      "totalItem": 0,
      "totalItemRejected": 0,
      "totalItemCompleted": 0,
      "totalCash": 0,
      "totalCashRejected": 0,
      "totalCashCompleted": 0
    },
    "createdAt": "2024-09-25T09:00:00Z",
    "updatedAt": "2024-09-25T09:00:00Z"
  },
  "code": 200
}
```

**Test loi:**

| Truong hop | Input | HTTP | Message |
|-----------|-------|------|---------|
| Loai khong hop le | `"type": "invalid-type"` | 400 | `type is invalid` |
| Thieu condition | Khong gui `condition` | 400 | `bad request` |
| `toAt` sai dinh dang | `"toAt": "30-09-2024"` | 400 | `toAt is invalid` |
| Thieu `toAt` | Khong gui `condition.toAt` | 400 | `toAt is invalid` |

---

### 3. Update - Cap nhat reconciliation

**Quyen:** IsAdmin
**Endpoint:** `PATCH /reconciliations/:id`

**Path params:**

| Param | Mo ta |
|-------|-------|
| `:id` | `{{RECONCILIATION_ID}}` |

**Body:** Tuong tu Create (cung dung `ReconciliationBody`)

| Truong | Kieu | Bat buoc | Mo ta |
|--------|------|----------|-------|
| `title` | string | Co | Ten moi |
| `type` | string | Co | Loai moi |
| `condition` | object | Co | Dieu kien moi |
| `condition.toAt` | string | Co | Ngay ket thuc moi |
| `condition.event` | string | Khong | Event ID |

**cURL:**

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Doi soat T-Fluencers Thang 9/2024 (cap nhat)",
    "type": "event-reward",
    "condition": {
      "toAt": "2024-10-05",
      "event": "{{EVENT_ID}}"
    }
  }'
```

**Response mau (200):**

```json
{
  "data": {
    "_id": "6650a1b2c3d4e5f6a7b8c9d0",
    "title": "Doi soat T-Fluencers Thang 9/2024 (cap nhat)",
    "status": "pending",
    "type": "event-reward",
    "conditions": {
      "toAt": "2024-10-05T00:00:00Z",
      "events": ["6650a1b2c3d4e5f6a7b8c9d1"]
    },
    "updatedAt": "2024-09-26T10:15:00Z"
  },
  "code": 200
}
```

**Test loi:**

| Truong hop | Input | HTTP | Message |
|-----------|-------|------|---------|
| ID khong ton tai | ID random | 400 | `reconciliation not found` |
| ID sai format | `id=abc` | 404 | `not found` |
| `type` khong hop le | `"type": "bonus"` | 400 | `type is invalid` |

---

### 4. GetDetail - Lay chi tiet reconciliation

**Quyen:** IsAdmin
**Endpoint:** `GET /reconciliations/:id`

**Path params:**

| Param | Mo ta |
|-------|-------|
| `:id` | `{{RECONCILIATION_ID}}` |

**cURL:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**Response mau (200):**

```json
{
  "data": {
    "_id": "6650a1b2c3d4e5f6a7b8c9d0",
    "title": "Doi soat T-Fluencers Thang 9/2024",
    "status": "processing",
    "type": "event-reward",
    "conditions": {
      "fromAt": "2024-09-01T00:00:00Z",
      "toAt": "2024-09-30T23:59:59Z",
      "events": ["6650a1b2c3d4e5f6a7b8c9d1"]
    },
    "statistic": {
      "totalItem": 320,
      "totalItemRejected": 18,
      "totalItemCompleted": 245,
      "totalCash": 186000000,
      "totalCashRejected": 6200000,
      "totalCashCompleted": 147500000
    },
    "createdAt": "2024-09-25T09:00:00Z",
    "updatedAt": "2024-09-28T16:45:00Z"
  },
  "code": 200
}
```

**Test loi:**

| Truong hop | HTTP | Message |
|-----------|------|---------|
| ID sai format ObjectID | 404 | `not found` |
| Khong tim thay | 400 | `reconciliation not found` |

---

### 5. ChangeStatus - Doi trang thai reconciliation

**Quyen:** IsAdmin
**Endpoint:** `PATCH /reconciliations/:id/change-status`

**Path params:**

| Param | Mo ta |
|-------|-------|
| `:id` | `{{RECONCILIATION_ID}}` |

**Body:**

| Truong | Kieu | Bat buoc | Gia tri hop le | Mo ta |
|--------|------|----------|----------------|-------|
| `status` | string | Co | `processing`, `running`, `rejected` | Trang thai moi |
| `reason` | string | Khong | - | Ly do (nen gui khi rejected) |

**cURL - Chuyen sang processing:**

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/change-status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "processing"
  }'
```

**cURL - Tu choi reconciliation:**

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/change-status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "rejected",
    "reason": "Du lieu khong hop le, can kiem tra lai cac bai dang thang 9"
  }'
```

**Response mau (200):**

```json
{
  "data": {
    "_id": "6650a1b2c3d4e5f6a7b8c9d0",
    "status": "processing",
    "updatedAt": "2024-09-28T17:00:00Z"
  },
  "code": 200
}
```

**Test loi:**

| Truong hop | Input | HTTP | Message |
|-----------|-------|------|---------|
| Thieu `status` | Khong gui `status` | 400 | `status is required` |
| Status khong hop le | `"status": "completed"` | 400 | `status is invalid` |
| Status khong hop le | `"status": "pending"` | 400 | `status is invalid` |

---

### 6. GetListContent - Lay danh sach content items

**Quyen:** IsAdmin
**Endpoint:** `GET /reconciliations/:id/content`

**Path params:**

| Param | Mo ta |
|-------|-------|
| `:id` | `{{RECONCILIATION_ID}}` |

**Query params:**

| Tham so | Kieu | Bat buoc | Mo ta | Vi du |
|---------|------|----------|-------|-------|
| `page` | int | Khong | Trang hien tai | `0` |
| `limit` | int | Khong | So ban ghi moi trang | `20` |
| `keyword` | string | Khong | Tim kiem theo tu khoa | `nguyen thi` |
| `user` | string | Khong | Loc theo user ID | `6650a1b2c3d4e5f6a7b8c9d4` |
| `status` | string | Khong | Loc theo trang thai item | `pending` |
| `sort` | string | Khong | Sap xep (chi ho tro `content.totalCashPending`) | `content.totalCashPending` |

**cURL:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/content?page=0&limit=20&status=pending" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**cURL voi sort:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/content?page=0&limit=50&sort=content.totalCashPending" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**Response mau (200):**

```json
{
  "data": {
    "list": [
      {
        "_id": "6650a1b2c3d4e5f6a7b8c9d2",
        "reconciliation": "6650a1b2c3d4e5f6a7b8c9d0",
        "user": {
          "_id": "6650a1b2c3d4e5f6a7b8c9d4",
          "name": "Nguyen Thi Lan Anh",
          "username": "lananh_tcb"
        },
        "type": "content",
        "status": "pending",
        "totalCash": 450000,
        "content": {
          "_id": "6650a1b2c3d4e5f6a7b8c9d5",
          "totalViewBegin": 15000,
          "totalViewPending": 12500,
          "totalViewCompleted": 10200,
          "totalViewRejected": 800,
          "totalViewEnd": 10000,
          "totalCashPending": 450000,
          "totalCashCompleted": 0,
          "totalCashRejected": 0,
          "cashPerView": 45,
          "engagement": 0.083
        },
        "firstAt": "2024-09-02T10:30:00Z",
        "lastAt": "2024-09-25T18:00:00Z",
        "createdAt": "2024-09-26T08:00:00Z",
        "updatedAt": "2024-09-26T08:00:00Z"
      }
    ],
    "total": 248
  },
  "code": 200
}
```

**Test loi:**

| Truong hop | Input | HTTP | Message |
|-----------|-------|------|---------|
| Sort key khong hop le | `sort=invalidKey` | 400 | `sort key is invalid` |
| ID reconciliation sai | ID khong ton tai | 400 | `reconciliation not found` |

---

### 7. GetListMilestone - Lay danh sach milestone items

**Quyen:** IsAdmin
**Endpoint:** `GET /reconciliations/:id/milestone`

**Path params:**

| Param | Mo ta |
|-------|-------|
| `:id` | `{{RECONCILIATION_ID}}` |

**Query params:**

| Tham so | Kieu | Bat buoc | Mo ta | Vi du |
|---------|------|----------|-------|-------|
| `page` | int | Khong | Trang hien tai | `0` |
| `limit` | int | Khong | So ban ghi moi trang | `20` |
| `user` | string | Khong | Loc theo user ID | `6650a1b2c3d4e5f6a7b8c9d4` |
| `status` | string | Khong | Loc theo trang thai | `completed` |
| `schema` | string | Khong | Loc theo schema ID | `6650a1b2c3d4e5f6a7b8c9d6` |

**cURL:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/milestone?page=0&limit=20" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**Response mau (200):**

```json
{
  "data": {
    "list": [
      {
        "_id": "6650a1b2c3d4e5f6a7b8c9e0",
        "reconciliation": "6650a1b2c3d4e5f6a7b8c9d0",
        "user": {
          "_id": "6650a1b2c3d4e5f6a7b8c9d4",
          "name": "Tran Van Minh",
          "username": "minhtrancreator"
        },
        "type": "milestone",
        "status": "completed",
        "totalCash": 2000000,
        "milestone": {
          "reward": "6650a1b2c3d4e5f6a7b8c9e1",
          "schema": "6650a1b2c3d4e5f6a7b8c9d6",
          "schemaName": "Moc 10 trieu luot xem"
        },
        "createdAt": "2024-09-26T08:00:00Z",
        "updatedAt": "2024-09-28T14:00:00Z"
      }
    ],
    "total": 35
  },
  "code": 200
}
```

**Test loi:**

| Truong hop | HTTP | Message |
|-----------|------|---------|
| ID sai format | 404 | `not found` |
| Page am | 400 | `page is invalid` |

---

### 8. GetListBonus - Lay danh sach bonus items

**Quyen:** IsAdmin
**Endpoint:** `GET /reconciliations/:id/bonus`

**Path params:**

| Param | Mo ta |
|-------|-------|
| `:id` | `{{RECONCILIATION_ID}}` |

**Query params:**

| Tham so | Kieu | Bat buoc | Mo ta | Vi du |
|---------|------|----------|-------|-------|
| `page` | int | Khong | Trang hien tai | `0` |
| `limit` | int | Khong | So ban ghi moi trang | `20` |
| `user` | string | Khong | Loc theo user ID | `6650a1b2c3d4e5f6a7b8c9d4` |
| `status` | string | Khong | Loc theo trang thai | `pending` |

**cURL:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/bonus?page=0&limit=20&status=pending" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**Response mau (200):**

```json
{
  "data": {
    "list": [
      {
        "_id": "6650a1b2c3d4e5f6a7b8c9f0",
        "reconciliation": "6650a1b2c3d4e5f6a7b8c9d0",
        "user": {
          "_id": "6650a1b2c3d4e5f6a7b8c9d4",
          "name": "Le Thi Huong",
          "username": "huongle_tfluencer"
        },
        "type": "bonus",
        "status": "pending",
        "totalCash": 5000000,
        "bonus": "6650a1b2c3d4e5f6a7b8c9f1",
        "createdAt": "2024-09-26T08:00:00Z",
        "updatedAt": "2024-09-26T08:00:00Z"
      }
    ],
    "total": 12
  },
  "code": 200
}
```

**Test loi:**

| Truong hop | HTTP | Message |
|-----------|------|---------|
| Thieu token | 401 | `unauthorized` |
| ID sai format | 404 | `not found` |

---

### 9. ChangeStatusItem - Doi trang thai item

**Quyen:** IsAdmin
**Endpoint:** `PATCH /reconciliations/:id/item/:idItem/change-status`

**Path params:**

| Param | Mo ta |
|-------|-------|
| `:id` | `{{RECONCILIATION_ID}}` |
| `:idItem` | `{{ITEM_ID}}` - ID cua reconciliation item |

**Body:**

| Truong | Kieu | Bat buoc | Gia tri hop le | Mo ta |
|--------|------|----------|----------------|-------|
| `status` | string | Co | `pending`, `rejected` | Trang thai moi cua item |

> **Luu y:** Chi cho phep doi sang `pending` hoac `rejected`. Khong the doi sang `completed` qua API nay (dung `confirm-status` hoac `override`).

**cURL - Tu choi item:**

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/item/{{ITEM_ID}}/change-status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "rejected"
  }'
```

**cURL - Dua item ve pending:**

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/item/{{ITEM_ID}}/change-status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "pending"
  }'
```

**Response mau (200):**

```json
{
  "data": {},
  "code": 200
}
```

**Test loi:**

| Truong hop | Input | HTTP | Message |
|-----------|-------|------|---------|
| Status khong hop le | `"status": "completed"` | 400 | `status is invalid` |
| Status khong hop le | `"status": "running"` | 400 | `status is invalid` |
| Thieu `status` | Khong gui `status` | 400 | `status is required` |
| `idItem` sai format | `idItem=abc` | 400 | `invalid itemId` |

---

### 10. CloseReconciliation - Dong reconciliation theo event

**Quyen:** IsAdmin
**Endpoint:** `PATCH /reconciliations/events/:eventId/close`

**Path params:**

| Param | Mo ta |
|-------|-------|
| `:eventId` | `{{EVENT_ID}}` - ID cua event can dong reconciliation |

> **Mo ta:** Dong toan bo reconciliation lien quan den event nay. Thuong dung khi event ket thuc va da hoan thanh doi soat.

**cURL:**

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/reconciliations/events/{{EVENT_ID}}/close" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json"
```

**Response mau (200):**

```json
{
  "data": {},
  "code": 200
}
```

**Test loi:**

| Truong hop | Input | HTTP | Message |
|-----------|-------|------|---------|
| `eventId` sai format | `eventId=abc123` | 400 | `invalid eventId` |
| Event khong ton tai | ID random | 400 | `event not found` |
| Reconciliation da dong | Event da close | 400 | `reconciliation already closed` |

---

### 11. MakeupCrawl - Chay lai crawl bo sung

**Quyen:** IsAdmin
**Endpoint:** `POST /reconciliations/events/:eventId/makeup-crawl`

**Path params:**

| Param | Mo ta |
|-------|-------|
| `:eventId` | `{{EVENT_ID}}` - ID cua event can crawl lai |

> **Mo ta:** Khoi dong lai tien trinh crawl du lieu bo sung cho event. Su dung khi mot so bai dang chua duoc crawl du lieu day du.

**cURL:**

```bash
curl -X POST "{{ADMIN_BASE_URL}}/reconciliations/events/{{EVENT_ID}}/makeup-crawl" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json"
```

**Response mau (200):**

```json
{
  "data": {
    "message": "Makeup crawl started"
  },
  "code": 200
}
```

**Test loi:**

| Truong hop | Input | HTTP | Message |
|-----------|-------|------|---------|
| `eventId` sai format | `eventId=invalid` | 400 | `invalid eventId` |
| Event khong ton tai | ID khong co trong DB | 400 | `event not found` |

---

### 12. EvaluateChecklist - Evaluate checklist tu dong

**Quyen:** IsAdmin
**Endpoint:** `POST /reconciliations/:id/evaluate`

**Path params:**

| Param | Mo ta |
|-------|-------|
| `:id` | `{{RECONCILIATION_ID}}` |

**Body:**

| Truong | Kieu | Bat buoc | Mo ta | Mac dinh |
|--------|------|----------|-------|----------|
| `overrideManual` | bool | Khong | Co ghi de ket qua evaluate thu cong truoc do khong | `false` |

> **Mo ta:** He thong tu dong chay checklist cho tat ca content items trong reconciliation. Kiem tra cac tieu chi: `video_accessible` (video con truy cap), `hashtag_present` (co hashtag quy dinh), `view_not_dropped` (luot xem khong giam dot ngot), `admin_confirm` (xac nhan admin).

**cURL - Evaluate tat ca (giu lai manual):**

```bash
curl -X POST "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/evaluate" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "overrideManual": false
  }'
```

**cURL - Evaluate va ghi de ca ket qua thu cong:**

```bash
curl -X POST "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/evaluate" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "overrideManual": true
  }'
```

**Response mau (200):**

```json
{
  "data": {
    "totalEvaluated": 248,
    "totalAutoApproved": 215,
    "totalAutoRejected": 18,
    "totalNeedsReview": 15
  },
  "code": 200
}
```

**Test loi:**

| Truong hop | HTTP | Message |
|-----------|------|---------|
| Reconciliation chua o trang thai hop le | 400 | `reconciliation status invalid for evaluate` |
| ID sai format | 404 | `not found` |

---

### 13. ApplyClassification - Ap dung phan loai vao trang thai item

**Quyen:** IsAdmin
**Endpoint:** `POST /reconciliations/:id/apply-classification`

**Path params:**

| Param | Mo ta |
|-------|-------|
| `:id` | `{{RECONCILIATION_ID}}` |

**Body:**

| Truong | Kieu | Bat buoc | Gia tri hop le | Mo ta |
|--------|------|----------|----------------|-------|
| `classification` | string | Khong | `""`, `auto_approved`, `auto_rejected` | Ap dung tat ca neu de trong, hoac chi ap dung theo classification cu the |

> **Mo ta:** Sau khi evaluate checklist, goi API nay de ap dung ket qua phan loai (auto_approved/auto_rejected) vao trang thai thuc te cua tung item. Items voi `needs_review` can xu ly thu cong.

**cURL - Ap dung tat ca phan loai:**

```bash
curl -X POST "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/apply-classification" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "classification": ""
  }'
```

**cURL - Chi ap dung auto_approved:**

```bash
curl -X POST "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/apply-classification" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "classification": "auto_approved"
  }'
```

**cURL - Chi ap dung auto_rejected:**

```bash
curl -X POST "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/apply-classification" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "classification": "auto_rejected"
  }'
```

**Response mau (200):**

```json
{
  "data": {
    "totalApplied": 233,
    "totalCompleted": 215,
    "totalRejected": 18
  },
  "code": 200
}
```

**Test loi:**

| Truong hop | HTTP | Message |
|-----------|------|---------|
| Chua evaluate checklist truoc | 400 | `checklist not evaluated` |
| ID sai format | 404 | `not found` |

---

### 14. GetChecklist - Lay checklist cua content item

**Quyen:** IsAdmin
**Endpoint:** `GET /reconciliations/:id/content/:itemId/checklist`

**Path params:**

| Param | Mo ta |
|-------|-------|
| `:id` | `{{RECONCILIATION_ID}}` |
| `:itemId` | `{{ITEM_ID}}` - ID cua content item |

**cURL:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/content/{{ITEM_ID}}/checklist" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**Response mau (200):**

```json
{
  "data": {
    "_id": "6650a1b2c3d4e5f6a7b8ca00",
    "reconciliation": "6650a1b2c3d4e5f6a7b8c9d0",
    "reconciliationItem": "6650a1b2c3d4e5f6a7b8c9d2",
    "event": "6650a1b2c3d4e5f6a7b8c9d1",
    "content": "6650a1b2c3d4e5f6a7b8c9d5",
    "user": "6650a1b2c3d4e5f6a7b8c9d4",
    "rewardType": "content",
    "version": 2,
    "classification": "auto_approved",
    "items": [
      {
        "code": "video_accessible",
        "status": "pass",
        "evaluatedBy": "system",
        "detail": {
          "expected": true,
          "actual": true,
          "message": "Video van con truy cap duoc"
        }
      },
      {
        "code": "hashtag_present",
        "status": "pass",
        "evaluatedBy": "system",
        "detail": {
          "expected": ["#TFluencers", "#Techcombank"],
          "actual": ["#TFluencers", "#Techcombank", "#Challenge"],
          "message": "Du hashtag yeu cau"
        }
      },
      {
        "code": "view_not_dropped",
        "status": "pass",
        "evaluatedBy": "system",
        "detail": {
          "expected": 0.1,
          "actual": 0.05,
          "message": "Luot xem giam it hon nguong cho phep"
        }
      },
      {
        "code": "admin_confirm",
        "status": "unverified",
        "evaluatedBy": "system",
        "detail": null
      }
    ],
    "evaluatedAt": "2024-09-27T10:00:00Z",
    "createdAt": "2024-09-26T08:00:00Z"
  },
  "code": 200
}
```

**Checklist codes:**

| Code | Mo ta | Fail level khi fail |
|------|-------|---------------------|
| `video_accessible` | Video con truy cap duoc tren TikTok/Instagram | `auto_reject` |
| `hashtag_present` | Bai dang co du hashtag quy dinh | `auto_reject` |
| `view_not_dropped` | Luot xem khong giam qua nguong cho phep | `warning` |
| `admin_confirm` | Admin xac nhan thu cong | `warning` |

**Test loi:**

| Truong hop | Input | HTTP | Message |
|-----------|-------|------|---------|
| `itemId` sai format | `itemId=abc` | 400 | `invalid itemId` |
| Checklist chua duoc tao | Item moi tao | 400 | `checklist not found` |

---

### 15. UpdateChecklist - Cap nhat thu cong checklist item

**Quyen:** IsAdmin
**Endpoint:** `PATCH /reconciliations/:id/content/:itemId/checklist`

**Path params:**

| Param | Mo ta |
|-------|-------|
| `:id` | `{{RECONCILIATION_ID}}` |
| `:itemId` | `{{ITEM_ID}}` |

**Body:**

| Truong | Kieu | Bat buoc | Gia tri hop le | Mo ta |
|--------|------|----------|----------------|-------|
| `code` | string | Co | `video_accessible`, `hashtag_present`, `view_not_dropped`, `admin_confirm` | Ma checklist item can cap nhat |
| `status` | string | Co | `pass`, `fail` | Ket qua danh gia thu cong |

**cURL - Danh dau pass:**

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/content/{{ITEM_ID}}/checklist" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "admin_confirm",
    "status": "pass"
  }'
```

**cURL - Danh dau fail:**

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/content/{{ITEM_ID}}/checklist" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "video_accessible",
    "status": "fail"
  }'
```

**Response mau (200):**

```json
{
  "data": {
    "_id": "6650a1b2c3d4e5f6a7b8ca00",
    "items": [
      {
        "code": "admin_confirm",
        "status": "pass",
        "evaluatedBy": "staff_6650a1b2c3d4e5f6a7b8ca01",
        "detail": null
      }
    ],
    "updatedAt": "2024-09-28T11:00:00Z"
  },
  "code": 200
}
```

**Test loi:**

| Truong hop | Input | HTTP | Message |
|-----------|-------|------|---------|
| Thieu `code` | Khong gui `code` | 400 | `bad request` |
| Thieu `status` | Khong gui `status` | 400 | `status is required` |
| `status` khong hop le | `"status": "unverified"` | 400 | `status is invalid` |
| `itemId` sai format | `itemId=xyz` | 400 | `invalid itemId` |

---

### 16. QuickApproveChecklist - Duyet nhanh tat ca checklist unverified

**Quyen:** IsAdmin
**Endpoint:** `POST /reconciliations/:id/content/:itemId/quick-approve`

**Path params:**

| Param | Mo ta |
|-------|-------|
| `:id` | `{{RECONCILIATION_ID}}` |
| `:itemId` | `{{ITEM_ID}}` |

> **Mo ta:** Danh dau `pass` cho tat ca checklist items dang o trang thai `unverified`. Cac items da duoc evaluate (pass/fail) se khong bi thay doi.

**cURL:**

```bash
curl -X POST "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/content/{{ITEM_ID}}/quick-approve" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json"
```

**Response mau (200):**

```json
{
  "data": {},
  "code": 200
}
```

**Test loi:**

| Truong hop | Input | HTTP | Message |
|-----------|-------|------|---------|
| `itemId` sai format | `itemId=abc` | 400 | `invalid itemId` |
| Khong co item unverified | Tat ca da duoc evaluate | 400 | `no unverified items` |

---

### 17. QuickRejectChecklist - Tu choi nhanh tat ca checklist unverified

**Quyen:** IsAdmin
**Endpoint:** `POST /reconciliations/:id/content/:itemId/quick-reject`

**Path params:**

| Param | Mo ta |
|-------|-------|
| `:id` | `{{RECONCILIATION_ID}}` |
| `:itemId` | `{{ITEM_ID}}` |

> **Mo ta:** Danh dau `fail` cho tat ca checklist items dang o trang thai `unverified`. Nguoc lai voi `quick-approve`.

**cURL:**

```bash
curl -X POST "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/content/{{ITEM_ID}}/quick-reject" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json"
```

**Response mau (200):**

```json
{
  "data": {},
  "code": 200
}
```

**Test loi:**

| Truong hop | Input | HTTP | Message |
|-----------|-------|------|---------|
| `itemId` sai format | `itemId=abc` | 400 | `invalid itemId` |
| Khong co item unverified | Tat ca da duoc evaluate | 400 | `no unverified items` |

---

### 18. OverrideClassification - Ghi de phan loai item

**Quyen:** IsAdmin
**Endpoint:** `PATCH /reconciliations/:id/content/:itemId/override`

**Path params:**

| Param | Mo ta |
|-------|-------|
| `:id` | `{{RECONCILIATION_ID}}` |
| `:itemId` | `{{ITEM_ID}}` |

**Body:**

| Truong | Kieu | Bat buoc | Gia tri hop le | Mo ta |
|--------|------|----------|----------------|-------|
| `toStatus` | string | Co | `completed`, `rejected` | Trang thai muc tieu muon ghi de |
| `reason` | string | Co | - | Ly do ghi de (bat buoc) |

> **Mo ta:** Ghi de phan loai he thong voi audit trail. Su dung khi admin can can thiep thu cong vao ket qua tu dong (vi du: he thong auto_rejected nhung bai dang thuc te hop le).

**cURL - Override tu rejected sang completed:**

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/content/{{ITEM_ID}}/override" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "toStatus": "completed",
    "reason": "Video bi loi ky thuat thoang qua nhung noi dung hop le, da xac minh thu cong"
  }'
```

**cURL - Override tu completed sang rejected:**

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/content/{{ITEM_ID}}/override" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "toStatus": "rejected",
    "reason": "Phat hien noi dung vi pham quy dinh sau khi da duyet"
  }'
```

**Response mau (200):**

```json
{
  "data": {},
  "code": 200
}
```

**Test loi:**

| Truong hop | Input | HTTP | Message |
|-----------|-------|------|---------|
| Thieu `toStatus` | Khong gui `toStatus` | 400 | `status is required` |
| `toStatus` khong hop le | `"toStatus": "pending"` | 400 | `status is invalid` |
| `toStatus` khong hop le | `"toStatus": "running"` | 400 | `status is invalid` |
| Thieu `reason` | Khong gui `reason` | 400 | `bad request` |
| `itemId` sai format | `itemId=xyz` | 400 | `invalid itemId` |

---

### 19. ConfirmStatus - Xac nhan trang thai item qua checklist

**Quyen:** IsAdmin
**Endpoint:** `POST /reconciliations/:id/content/:itemId/confirm-status`

**Path params:**

| Param | Mo ta |
|-------|-------|
| `:id` | `{{RECONCILIATION_ID}}` |
| `:itemId` | `{{ITEM_ID}}` |

**Body:**

| Truong | Kieu | Bat buoc | Gia tri hop le | Mo ta |
|--------|------|----------|----------------|-------|
| `status` | string | Co | `completed`, `rejected` | Trang thai xac nhan cuoi cung |
| `reason` | string | Bat buoc khi rejected | - | Ly do tu choi (bat buoc khi `status=rejected`) |

> **Mo ta:** Xac nhan trang thai cuoi cung cua item sau khi checklist da day du. Khac voi `override`, `confirm-status` di qua quy trinh validation checklist truoc khi ap dung.

**cURL - Duyet (completed):**

```bash
curl -X POST "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/content/{{ITEM_ID}}/confirm-status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }'
```

**cURL - Tu choi (rejected):**

```bash
curl -X POST "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/content/{{ITEM_ID}}/confirm-status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "rejected",
    "reason": "Bai dang khong du hashtag bat buoc #TFluencers #Techcombank"
  }'
```

**Response mau (200):**

```json
{
  "data": {
    "_id": "6650a1b2c3d4e5f6a7b8c9d2",
    "status": "completed",
    "updatedAt": "2024-09-28T15:30:00Z"
  },
  "code": 200
}
```

**Test loi:**

| Truong hop | Input | HTTP | Message |
|-----------|-------|------|---------|
| Thieu `status` | Khong gui `status` | 400 | `status is required` |
| `status` khong hop le | `"status": "pending"` | 400 | `status is invalid` |
| `status=rejected` nhung thieu `reason` | Khong gui `reason` | 400 | `reason is required for rejection` |
| `itemId` sai format | `itemId=abc` | 400 | `invalid itemId` |
| Checklist chua hoan thanh | Con item unverified | 400 | `checklist not fully resolved` |

---

### 20. ResetChecklist - Reset checklist item ve trang thai goc

**Quyen:** IsAdmin
**Endpoint:** `POST /reconciliations/:id/content/:itemId/reset-checklist`

**Path params:**

| Param | Mo ta |
|-------|-------|
| `:id` | `{{RECONCILIATION_ID}}` |
| `:itemId` | `{{ITEM_ID}}` |

**Body:**

| Truong | Kieu | Bat buoc | Mo ta | Vi du |
|--------|------|----------|-------|-------|
| `code` | string | Co | Ma checklist item can reset | `admin_confirm` |

> **Mo ta:** Reset mot checklist item cu the ve trang thai `unverified` (hoac trang thai he thong ban dau). Dung khi admin muon evaluate lai mot tieu chi cu the ma khong can chay lai toan bo checklist.

**cURL:**

```bash
curl -X POST "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/content/{{ITEM_ID}}/reset-checklist" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "admin_confirm"
  }'
```

**cURL - Reset video_accessible:**

```bash
curl -X POST "{{ADMIN_BASE_URL}}/reconciliations/{{RECONCILIATION_ID}}/content/{{ITEM_ID}}/reset-checklist" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "video_accessible"
  }'
```

**Response mau (200):**

```json
{
  "data": {
    "_id": "6650a1b2c3d4e5f6a7b8ca00",
    "items": [
      {
        "code": "admin_confirm",
        "status": "unverified",
        "evaluatedBy": "system",
        "detail": null
      }
    ],
    "updatedAt": "2024-09-28T16:00:00Z"
  },
  "code": 200
}
```

**Test loi:**

| Truong hop | Input | HTTP | Message |
|-----------|-------|------|---------|
| Thieu `code` | Khong gui `code` hoac de trong | 400 | `code is required` |
| `code` khong ton tai | `"code": "invalid_code"` | 400 | `checklist code not found` |
| `itemId` sai format | `itemId=abc` | 400 | `invalid itemId` |

---

## Quy trinh doi soat dien hinh

Duoi day la luong xu ly doi soat thuong gap:

```
1. Tao reconciliation
   POST /reconciliations
   └─ type: "event-reward", condition.toAt, condition.event

2. Khoi dong doi soat
   PATCH /reconciliations/{id}/change-status
   └─ status: "processing"

3. (Tuy chon) Crawl bo sung neu thieu du lieu
   POST /reconciliations/events/{eventId}/makeup-crawl

4. Evaluate checklist tu dong
   POST /reconciliations/{id}/evaluate
   └─ overrideManual: false

5. Kiem tra ket qua phan loai
   GET /reconciliations/{id}/content?status=pending
   └─ Xem cac item needs_review

6. Xu ly thu cong cac item needs_review
   a. Xem chi tiet checklist:
      GET /reconciliations/{id}/content/{itemId}/checklist
   b. Cap nhat checklist thu cong:
      PATCH /reconciliations/{id}/content/{itemId}/checklist
   c. Hoac quick approve/reject:
      POST /reconciliations/{id}/content/{itemId}/quick-approve
      POST /reconciliations/{id}/content/{itemId}/quick-reject
   d. Xac nhan trang thai cuoi cung:
      POST /reconciliations/{id}/content/{itemId}/confirm-status

7. Ap dung phan loai vao trang thai
   POST /reconciliations/{id}/apply-classification
   └─ classification: "" (tat ca)

8. Dong reconciliation
   PATCH /reconciliations/events/{eventId}/close
```

---

## Luu y quan trong

- **Sort:** `GET /content` chi ho tro sort theo `content.totalCashPending`. Sort key khac se tra ve loi 400.
- **ChangeStatusItem:** Chi cho phep doi sang `pending` hoac `rejected`. Doi sang `completed` phai dung `confirm-status` hoac `override`.
- **ConfirmStatus:** Bat buoc gui `reason` khi `status=rejected`.
- **OverrideClassification:** Bat buoc gui `reason` trong moi truong hop (ca khi completed).
- **ResetChecklist:** Bat buoc gui `code` (ten checklist item can reset). Body trong se tra 400.
- **CloseReconciliation va MakeupCrawl:** `eventId` zero-value (ObjectID all zeros) se tra ve 400 ngay tai handler, truoc khi vao service.
- **EvaluateChecklist:** Khong gui body hoac gui `{}` se dung mac dinh `overrideManual: false`.
- **ApplyClassification:** Gui `classification: ""` hoac khong gui field nay de ap dung tat ca phan loai.
