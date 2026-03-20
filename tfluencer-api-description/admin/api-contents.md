# API Contents - Admin

Base URL: `{{ADMIN_BASE_URL}}` (vd: `https://api.example.com/admin`)

---

## Muc quyen

| Middleware | Mo ta |
|---|---|
| `RequiredLogin` | Phai co token hop le |
| `CheckPermissionRole([CampaignOwner, Collaborator])` | CampaignOwner hoac Collaborator |
| `CheckPermissionRole([Collaborator])` | Chi danh cho Collaborator |
| `IsCampaignOwner` | Chi danh cho CampaignOwner |

> **Phan biet role:**
> - `CampaignOwner`: Quan ly toan bo noi dung, co the doc nhung khong doi trang thai
> - `Collaborator`: Co them quyen doi trang thai bai dang (approve/reject)

---

## PHAN 1: Contents

---

## 1. GetList - Lay danh sach bai dang

**Quyen:** `RequiredLogin` + `CheckPermissionRole([CampaignOwner, Collaborator])`
**Endpoint:** `GET /contents`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `page` | int | Khong | So trang (mac dinh: 1) | `1` |
| `limit` | int | Khong | So ban ghi (mac dinh: 20) | `20` |
| `keyword` | string | Khong | Tim kiem theo tieu de / link | `"review techcombank"` |
| `source` | string | Khong | Nen tang | `"tiktok"` / `"youtube"` |
| `status` | string | Khong | Trang thai bai dang | `"pending"` / `"approved"` / `"rejected"` |
| `createdBy` | string | Khong | ID nguoi dang (co the nhieu, ngan cach dau phay) | `"664a...0c,664a...0d"` |
| `event` | string | Khong | ID thu thach (co the nhieu, ngan cach dau phay) | `"664a...01"` |
| `partner` | string | Khong | ID partner | `"664a...01"` |
| `tag` | string | Khong | ID tag (co the nhieu, ngan cach dau phay) | `"664a...20"` |
| `isEmployee` | string | Khong | Loc nhan vien | `"true"` / `"false"` |
| `fromAt` | string | Khong | Tu ngay (ISO 8601 datetime) | `"2024-01-01T00:00:00.000Z"` |
| `toAt` | string | Khong | Den ngay (ISO 8601 datetime) | `"2024-03-31T23:59:59.000Z"` |
| `sort` | string | Khong | Sap xep | `"createdAt:desc"` |
| `id` | string | Khong | Loc theo ObjectID bai dang cu the | `"664a...30"` |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/contents?page=1&limit=20&status=pending&source=tiktok" \
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
        "_id": "664a1f2e3c4b5d6e7f8a9b30",
        "title": "Review the Cao Techcombank - Chuyen tien sieu nhanh",
        "link": "https://www.tiktok.com/@nguyenvana/video/123456789",
        "source": "tiktok",
        "status": "pending",
        "view": 52300,
        "like": 1240,
        "comment": 87,
        "share": 345,
        "isPinned": false,
        "event": {
          "_id": "664a1f2e3c4b5d6e7f8a9b01",
          "name": "Thu thach chia se trai nghiem Techcombank"
        },
        "createdBy": {
          "_id": "664a1f2e3c4b5d6e7f8a9b0c",
          "name": "Nguyen Van A"
        },
        "publishAt": "2024-03-15T10:00:00Z",
        "createdAt": "2024-03-15T11:30:00Z"
      }
    ],
    "total": 438,
    "page": 1,
    "limit": 20,
    "totalPages": 22
  }
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| Token khong hop le | `401` | `{"code": 401, "message": "Unauthorized"}` |
| Khong co quyen | `403` | `{"code": 403, "message": "Forbidden"}` |
| `sort` key khong hop le | `400` | `{"code": 400, "message": "sort key not allowed"}` |

---

## 2. GetDetail - Lay chi tiet bai dang

**Quyen:** `RequiredLogin` + `CheckPermissionRole([CampaignOwner, Collaborator])`
**Endpoint:** `GET /contents/:id`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

### Path Params

| Param | Bat buoc | Mo ta |
|---|---|---|
| `id` | Co | MongoDB ObjectID cua bai dang |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/contents/{{CONTENT_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "data": {
      "_id": "664a1f2e3c4b5d6e7f8a9b30",
      "title": "Review the Cao Techcombank - Chuyen tien sieu nhanh",
      "link": "https://www.tiktok.com/@nguyenvana/video/123456789",
      "source": "tiktok",
      "status": "approved",
      "cover": "https://cdn.example.com/covers/abc123.jpg",
      "author": "@nguyenvana",
      "view": 52300,
      "like": 1240,
      "comment": 87,
      "share": 345,
      "isPinned": true,
      "warningTags": [],
      "event": {
        "_id": "664a1f2e3c4b5d6e7f8a9b01",
        "name": "Thu thach chia se trai nghiem Techcombank"
      },
      "createdBy": {
        "_id": "664a1f2e3c4b5d6e7f8a9b0c",
        "name": "Nguyen Van A",
        "email": "user@example.com"
      },
      "publishAt": "2024-03-15T10:00:00Z",
      "createdAt": "2024-03-15T11:30:00Z",
      "updatedAt": "2024-03-16T09:00:00Z"
    }
  }
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| `id` khong phai ObjectID | `400` | `{"code": 400, "message": "invalid id"}` |
| Bai dang khong ton tai | `400` | `{"code": 400, "message": "content not found"}` |
| Khong co quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 3. ChangeStatus - Doi trang thai bai dang

**Quyen:** `RequiredLogin` + `CheckPermissionRole([Collaborator])` (chi Collaborator)
**Endpoint:** `PATCH /contents/:id/status`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

### Path Params

| Param | Bat buoc | Mo ta |
|---|---|---|
| `id` | Co | MongoDB ObjectID cua bai dang |

### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Gia tri hop le |
|---|---|---|---|---|
| `status` | string | **Co** | Trang thai moi | `"approved"` / `"rejected"` / `"pending"` |
| `reason` | string | Khong | Ly do (khi reject) | `"Noi dung vi pham quy dinh"` |

### cURL

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/contents/{{CONTENT_ID}}/status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved"
  }'
```

**Vi du reject:**

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/contents/{{CONTENT_ID}}/status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "rejected",
    "reason": "Noi dung khong dap ung yeu cau cua thu thach"
  }'
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "664a1f2e3c4b5d6e7f8a9b30",
    "status": "approved",
    "updatedAt": "2024-03-20T14:00:00Z"
  }
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| Thieu `status` | `400` | `{"code": 400, "message": "status is invalid"}` |
| `status` khong hop le | `400` | `{"code": 400, "message": "status is invalid"}` |
| Bai dang khong ton tai | `400` | `{"code": 400, "message": "content not found"}` |
| Khong phai Collaborator | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 4. BatchChangeStatus - Doi trang thai hang loat

**Quyen:** `RequiredLogin` + `CheckPermissionRole([Collaborator])` (chi Collaborator)
**Endpoint:** `PATCH /contents/batch-status`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `status` | string | **Co** | Trang thai moi | `"approved"` / `"rejected"` |
| `reason` | string | Khong | Ly do (khi reject) | `"Noi dung khong phu hop"` |
| `ids` | array[string] | Khong | Danh sach ID can doi (neu khong dung `isAll`) | `["664a...30", "664a...31"]` |
| `isAll` | bool | Khong | Ap dung cho tat ca (theo filter) | `false` |
| `filter` | object | Khong | Bo loc khi dung `isAll: true` | xem ben duoi |

**Cau truc `filter`:**

| Field | Kieu | Mo ta |
|---|---|---|
| `keyword` | string | Tim kiem theo tu khoa |
| `source` | string | Nen tang |
| `status` | string | Trang thai hien tai |
| `createdBy` | string | ID nguoi dang |
| `event` | string | ID thu thach |
| `fromAt` | string | Tu ngay |
| `toAt` | string | Den ngay |
| `partner` | string | ID partner |

### cURL - Doi trang thai theo danh sach ID

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/contents/batch-status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "ids": [
      "664a1f2e3c4b5d6e7f8a9b30",
      "664a1f2e3c4b5d6e7f8a9b31",
      "664a1f2e3c4b5d6e7f8a9b32"
    ]
  }'
```

### cURL - Doi trang thai theo filter (isAll)

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/contents/batch-status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "rejected",
    "reason": "Noi dung khong dat yeu cau",
    "isAll": true,
    "filter": {
      "status": "pending",
      "event": "664a1f2e3c4b5d6e7f8a9b01",
      "fromAt": "2024-01-01T00:00:00.000Z",
      "toAt": "2024-01-31T23:59:59.000Z"
    }
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
| Thieu `status` | `400` | `{"code": 400, "message": "status is invalid"}` |
| `status` khong hop le | `400` | `{"code": 400, "message": "status is invalid"}` |
| Khong phai Collaborator | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 5. RejectBySelect - Tu choi nhieu bai dang theo danh sach

**Quyen:** `RequiredLogin` + `CheckPermissionRole([CampaignOwner, Collaborator])`
**Endpoint:** `POST /contents/reject-by-select`

> **Luu y:** Xu ly bat dong bo (async) - API tra ve ngay lap tuc.

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `contentIds` | array[string] | Khong | Danh sach ID bai dang can tu choi | `["664a...30", "664a...31"]` |
| `note` | string | Khong | Ghi chu ly do tu choi | `"Noi dung khong lien quan den thu thach"` |

### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/contents/reject-by-select" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "contentIds": [
      "664a1f2e3c4b5d6e7f8a9b30",
      "664a1f2e3c4b5d6e7f8a9b31",
      "664a1f2e3c4b5d6e7f8a9b32"
    ],
    "note": "Noi dung khong lien quan den thu thach Techcombank"
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

> API tra ve `200` ngay. Tu choi duoc xu ly o background.

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| Body khong phai JSON | `400` | `{"code": 400, "message": "Bad request"}` |
| Khong co quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 6. Pin - Ghim / Bo ghim bai dang

**Quyen:** `RequiredLogin` + `CheckPermissionRole([CampaignOwner, Collaborator])`
**Endpoint:** `PATCH /contents/:id/pin`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

### Path Params

| Param | Bat buoc | Mo ta |
|---|---|---|
| `id` | Co | MongoDB ObjectID cua bai dang |

### cURL

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/contents/{{CONTENT_ID}}/pin" \
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

> Hanh dong toggle: goi lan 1 se ghim, goi lan 2 se bo ghim.

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| `id` khong hop le | `400` | `{"code": 400, "message": "invalid id"}` |
| Bai dang khong ton tai | `400` | `{"code": 400, "message": "content not found"}` |
| Khong co quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 7. StatisticChart - Lay du lieu bieu do thong ke

**Quyen:** `RequiredLogin` + `CheckPermissionRole([CampaignOwner, Collaborator])`
**Endpoint:** `GET /contents/statistic-chart`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `createdBy` | string | Khong | ID nguoi dang | `"664a1f2e3c4b5d6e7f8a9b0c"` |
| `event` | string | Khong | ID thu thach | `"664a1f2e3c4b5d6e7f8a9b01"` |
| `partner` | string | Khong | ID partner | `"664a1f2e3c4b5d6e7f8a9b02"` |
| `content` | string | Khong | ID bai dang cu the | `"664a1f2e3c4b5d6e7f8a9b30"` |
| `fromAt` | string | Khong | Tu ngay (ISO 8601 datetime) | `"2024-01-01T00:00:00.000Z"` |
| `toAt` | string | Khong | Den ngay (ISO 8601 datetime) | `"2024-03-31T23:59:59.000Z"` |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/contents/statistic-chart?event=664a1f2e3c4b5d6e7f8a9b01&fromAt=2024-01-01T00:00:00.000Z&toAt=2024-03-31T23:59:59.000Z" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "data": [
      {
        "date": "2024-03-01",
        "view": 125000,
        "like": 4320,
        "comment": 890,
        "share": 2100
      },
      {
        "date": "2024-03-02",
        "view": 142000,
        "like": 5100,
        "comment": 1020,
        "share": 2450
      },
      {
        "date": "2024-03-03",
        "view": 98500,
        "like": 3200,
        "comment": 650,
        "share": 1800
      }
    ]
  }
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| `fromAt` sai dinh dang | `400` | `{"code": 400, "message": "invalid date format"}` |
| Khong co quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 8. AddStatisticForContent - Them thong ke thu cong cho bai dang

**Quyen:** `RequiredLogin` + `CheckPermissionRole([CampaignOwner, Collaborator])`
**Endpoint:** `POST /contents/:id/add-statistic`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

### Path Params

| Param | Bat buoc | Mo ta |
|---|---|---|
| `id` | Co | MongoDB ObjectID cua bai dang |

### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `contentId` | string | Khong | ID bai dang (co the bo qua, lay tu path param) | `"664a...30"` |
| `cover` | string | Khong | URL anh bia | `"https://cdn.example.com/cover.jpg"` |
| `author` | string | Khong | Ten tac gia | `"@nguyenvana"` |
| `publishAt` | string | Khong | Ngay dang (ISO 8601 datetime) | `"2024-03-15T10:00:00Z"` |
| `title` | string | Khong | Tieu de bai dang | `"Review the cao Techcombank"` |
| `desc` | string | Khong | Mo ta | `"Trai nghiem chuyen tien sieu nhanh"` |
| `view` | int | Khong | So luot xem | `52300` |
| `like` | int | Khong | So luot thich | `1240` |
| `share` | int | Khong | So luot chia se | `345` |
| `comment` | int | Khong | So binh luan | `87` |

### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/contents/{{CONTENT_ID}}/add-statistic" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "view": 52300,
    "like": 1240,
    "share": 345,
    "comment": 87,
    "title": "Review the cao Techcombank - Chuyen tien sieu nhanh",
    "author": "@nguyenvana",
    "publishAt": "2024-03-15T10:00:00Z"
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
| `id` khong hop le | `400` | `{"code": 400, "message": "invalid id"}` |
| Bai dang khong ton tai | `400` | `{"code": 400, "message": "content not found"}` |
| Khong co quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 9. UpdateTag - Cap nhat warning tag cho bai dang

**Quyen:** `RequiredLogin` + `CheckPermissionRole([CampaignOwner, Collaborator])`
**Endpoint:** `PATCH /contents/tag`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `contentIds` | array[ObjectID] | Khong | Danh sach ID bai dang | `["664a...30", "664a...31"]` |
| `warningTags` | array[ObjectID] | Khong | Danh sach ID tag canh bao | `["664a...50", "664a...51"]` |

### cURL

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/contents/tag" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "contentIds": [
      "664a1f2e3c4b5d6e7f8a9b30",
      "664a1f2e3c4b5d6e7f8a9b31"
    ],
    "warningTags": [
      "664a1f2e3c4b5d6e7f8a9b50"
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

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| ObjectID khong hop le | `400` | `{"code": 400, "message": "Bad request"}` |
| Khong co quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 10. ImportContent - Import bai dang tu link

**Quyen:** `RequiredLogin` + `CheckPermissionRole([CampaignOwner, Collaborator])`
**Endpoint:** `POST /contents/import`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `userId` | string | **Co** | MongoDB ObjectID cua nguoi dung | `"664a1f2e3c4b5d6e7f8a9b0c"` |
| `eventId` | string | **Co** | MongoDB ObjectID cua thu thach | `"664a1f2e3c4b5d6e7f8a9b01"` |
| `contents` | array[object] | **Co** | Danh sach bai can import | xem ben duoi |

**Cau truc moi phan tu trong `contents`:**

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `source` | string | **Co** | Nen tang | `"tiktok"` / `"youtube"` |
| `link` | array[string] | **Co** | Danh sach link bai dang | `["https://tiktok.com/..."]` |

### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/contents/import" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "{{USER_ID}}",
    "eventId": "664a1f2e3c4b5d6e7f8a9b01",
    "contents": [
      {
        "source": "tiktok",
        "link": [
          "https://www.tiktok.com/@nguyenvana/video/123456789",
          "https://www.tiktok.com/@nguyenvana/video/987654321"
        ]
      },
      {
        "source": "youtube",
        "link": [
          "https://www.youtube.com/watch?v=abcdefghijk"
        ]
      }
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

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| Thieu `userId` | `400` | `{"code": 400, "message": "user not found"}` |
| `userId` khong phai ObjectID | `400` | `{"code": 400, "message": "id mongo invalid"}` |
| Thieu `eventId` | `400` | `{"code": 400, "message": "event not found"}` |
| `contents` rong | `400` | `{"code": 400, "message": "bad request"}` |
| `source` khong hop le | `400` | `{"code": 400, "message": "source invalid"}` |
| Khong co quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 11. GetImportTrackingList - Lay lich su import

**Quyen:** `RequiredLogin` + `CheckPermissionRole([CampaignOwner, Collaborator])`
**Endpoint:** `GET /contents/import-tracking`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `page` | int | Khong | So trang | `1` |
| `limit` | int | Khong | So ban ghi | `20` |
| `event` | string | Khong | ID thu thach | `"664a1f2e3c4b5d6e7f8a9b01"` |
| `partner` | string | Khong | ID partner | `"664a1f2e3c4b5d6e7f8a9b02"` |
| `user` | string | Khong | ID nguoi dung | `"664a1f2e3c4b5d6e7f8a9b0c"` |
| `status` | string | Khong | Trang thai | `"success"` / `"failed"` / `"processing"` |
| `fromAt` | string | Khong | Tu ngay (ISO 8601 datetime) | `"2024-03-01T00:00:00.000Z"` |
| `toAt` | string | Khong | Den ngay (ISO 8601 datetime) | `"2024-03-31T23:59:59.000Z"` |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/contents/import-tracking?page=1&limit=20&status=success" \
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
        "_id": "664a1f2e3c4b5d6e7f8a9b60",
        "userId": "664a1f2e3c4b5d6e7f8a9b0c",
        "eventId": "664a1f2e3c4b5d6e7f8a9b01",
        "status": "success",
        "totalLinks": 3,
        "successCount": 3,
        "failedCount": 0,
        "source": "tiktok",
        "createdBy": {
          "_id": "664a1f2e3c4b5d6e7f8a9b70",
          "name": "Admin Techcombank"
        },
        "createdAt": "2024-03-18T10:30:00Z"
      },
      {
        "_id": "664a1f2e3c4b5d6e7f8a9b61",
        "userId": "664a1f2e3c4b5d6e7f8a9b0d",
        "eventId": "664a1f2e3c4b5d6e7f8a9b01",
        "status": "failed",
        "totalLinks": 2,
        "successCount": 0,
        "failedCount": 2,
        "source": "youtube",
        "errorMessage": "Video not found or private",
        "createdBy": {
          "_id": "664a1f2e3c4b5d6e7f8a9b70",
          "name": "Admin Techcombank"
        },
        "createdAt": "2024-03-18T11:00:00Z"
      }
    ],
    "total": 25,
    "page": 1,
    "limit": 20,
    "totalPages": 2
  }
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| Token khong hop le | `401` | `{"code": 401, "message": "Unauthorized"}` |
| Khong co quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 12. CrawlContentInfoById - Thu thap lai thong tin bai dang

**Quyen:** `RequiredLogin` + `CheckPermissionRole([CampaignOwner, Collaborator])` + **Chi Root Staff**
**Endpoint:** `POST /contents/:id/crawl-info`

> **Luu y quan trong:** API nay co kiem tra them `staff.IsRoot` - chi Root Staff moi co the su dung. Neu khong phai Root se nhan loi `Permission denied`.

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

### Path Params

| Param | Bat buoc | Mo ta |
|---|---|---|
| `id` | Co | MongoDB ObjectID cua bai dang |

### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/contents/{{CONTENT_ID}}/crawl-info" \
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
| Khong phai Root Staff | `400` | `{"code": 400, "message": "Permission denied"}` |
| Bai dang khong ton tai | `400` | `{"code": 400, "message": "content not found"}` |
| Khong co quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 13. UpdateStatusDataContents - Cap nhat trang thai du lieu noi dung (background)

**Quyen:** `RequiredLogin` + `CheckPermissionRole([CampaignOwner, Collaborator])`
**Endpoint:** `GET /contents/update-status-data-contents`

> **Luu y:** Day la trigger job chay o background. API tra ve `200` ngay lap tuc.

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `event` | string | Khong | ID thu thach | `"664a1f2e3c4b5d6e7f8a9b01"` |
| `id` | string | Khong | ID bai dang cu the | `"664a1f2e3c4b5d6e7f8a9b30"` |
| `fromAt` | string | Khong | Tu ngay (ISO 8601 datetime) | `"2024-03-01T00:00:00.000Z"` |
| `toAt` | string | Khong | Den ngay (ISO 8601 datetime) | `"2024-03-31T23:59:59.000Z"` |
| `limit` | int | Khong | Gioi han so ban ghi xu ly | `100` |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/contents/update-status-data-contents?event=664a1f2e3c4b5d6e7f8a9b01&limit=100" \
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
| Token khong hop le | `401` | `{"code": 401, "message": "Unauthorized"}` |
| Khong co quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 14. UpdateWarningTagsContent - Cap nhat warning tag (background)

**Quyen:** `RequiredLogin` + `CheckPermissionRole([CampaignOwner, Collaborator])`
**Endpoint:** `GET /contents/update-warning-tags-content`

> **Luu y:** Day la trigger job chay o background. API tra ve `200` ngay lap tuc.

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `event` | string | Khong | ID thu thach | `"664a1f2e3c4b5d6e7f8a9b01"` |
| `id` | string | Khong | ID bai dang cu the | `"664a1f2e3c4b5d6e7f8a9b30"` |
| `tag` | string | Khong | ID tag can cap nhat | `"664a1f2e3c4b5d6e7f8a9b50"` |
| `fromAt` | string | Khong | Tu ngay (ISO 8601 datetime) | `"2024-03-01T00:00:00.000Z"` |
| `toAt` | string | Khong | Den ngay (ISO 8601 datetime) | `"2024-03-31T23:59:59.000Z"` |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/contents/update-warning-tags-content?event=664a1f2e3c4b5d6e7f8a9b01&tag=664a1f2e3c4b5d6e7f8a9b50" \
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
| Token khong hop le | `401` | `{"code": 401, "message": "Unauthorized"}` |
| Khong co quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## PHAN 2: Content Manual Flows

---

## 15. GetList - Lay danh sach luong thu cong

**Quyen:** `RequiredLogin` + `IsCampaignOwner`
**Endpoint:** `GET /content-manual-flows`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `page` | int | Khong | So trang | `1` |
| `limit` | int | Khong | So ban ghi | `20` |
| `content` | string | Khong | ID bai dang | `"664a1f2e3c4b5d6e7f8a9b30"` |
| `createdBy` | string | Khong | ID nguoi tao | `"664a1f2e3c4b5d6e7f8a9b70"` |
| `actionType` | string | Khong | Loai hanh dong | `"add"` / `"subtract"` |
| `type` | string | Khong | Loai luong | xem gia tri hop le |
| `status` | string | Khong | Trang thai | `"pending"` / `"done"` |
| `fromAt` | string | Khong | Tu ngay (ISO 8601 datetime) | `"2024-03-01T00:00:00.000Z"` |
| `toAt` | string | Khong | Den ngay (ISO 8601 datetime) | `"2024-03-31T23:59:59.000Z"` |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/content-manual-flows?page=1&limit=20&actionType=add" \
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
        "_id": "664a1f2e3c4b5d6e7f8a9b80",
        "contentId": "664a1f2e3c4b5d6e7f8a9b30",
        "content": {
          "_id": "664a1f2e3c4b5d6e7f8a9b30",
          "title": "Review the cao Techcombank",
          "source": "tiktok"
        },
        "view": 10000,
        "actionType": "add",
        "type": "view",
        "status": "done",
        "createdBy": {
          "_id": "664a1f2e3c4b5d6e7f8a9b70",
          "name": "Admin Techcombank"
        },
        "createdAt": "2024-03-18T14:00:00Z"
      }
    ],
    "total": 12,
    "page": 1,
    "limit": 20,
    "totalPages": 1
  }
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| Token khong hop le | `401` | `{"code": 401, "message": "Unauthorized"}` |
| Khong phai CampaignOwner | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 16. Create - Tao luong dieu chinh view thu cong

**Quyen:** `RequiredLogin` + `IsCampaignOwner`
**Endpoint:** `POST /content-manual-flows`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Gia tri hop le |
|---|---|---|---|---|
| `contentId` | string | **Co** | MongoDB ObjectID cua bai dang | ObjectID hop le |
| `view` | int | **Co** | So luot xem can dieu chinh | So nguyen duong |
| `actionType` | string | Khong | Loai hanh dong | `"add"` / `"subtract"` (theo `ContentAdjustViewActionType`) |

> **Validation:** `contentId` phai la MongoDB ObjectID hop le. `view` bat buoc. `actionType` phai nam trong danh sach `ContentAdjustViewActionType`.

### cURL - Them luot xem

```bash
curl -X POST "{{ADMIN_BASE_URL}}/content-manual-flows" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "contentId": "{{CONTENT_ID}}",
    "view": 10000,
    "actionType": "add"
  }'
```

### cURL - Tru luot xem

```bash
curl -X POST "{{ADMIN_BASE_URL}}/content-manual-flows" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "contentId": "{{CONTENT_ID}}",
    "view": 5000,
    "actionType": "subtract"
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
| `contentId` khong phai ObjectID | `400` | `{"code": 400, "message": "id mongo invalid"}` |
| Thieu `view` | `400` | `{"code": 400, "message": "bad request"}` |
| `actionType` khong hop le | `400` | `{"code": 400, "message": "type invalid"}` |
| Bai dang khong ton tai | `400` | `{"code": 400, "message": "content not found"}` |
| Khong phai CampaignOwner | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## Tom tat cac endpoint

### Contents

| Method | Endpoint | Quyen | Mo ta |
|---|---|---|---|
| `GET` | `/contents` | CampaignOwner / Collaborator | Lay danh sach bai dang |
| `GET` | `/contents/:id` | CampaignOwner / Collaborator | Lay chi tiet bai dang |
| `PATCH` | `/contents/:id/status` | **Collaborator only** | Doi trang thai bai dang |
| `PATCH` | `/contents/batch-status` | **Collaborator only** | Doi trang thai hang loat |
| `POST` | `/contents/reject-by-select` | CampaignOwner / Collaborator | Tu choi nhieu bai (async) |
| `PATCH` | `/contents/:id/pin` | CampaignOwner / Collaborator | Ghim / bo ghim bai dang |
| `GET` | `/contents/statistic-chart` | CampaignOwner / Collaborator | Du lieu bieu do thong ke |
| `POST` | `/contents/:id/add-statistic` | CampaignOwner / Collaborator | Them thong ke thu cong |
| `PATCH` | `/contents/tag` | CampaignOwner / Collaborator | Cap nhat warning tag |
| `POST` | `/contents/import` | CampaignOwner / Collaborator | Import bai dang tu link |
| `GET` | `/contents/import-tracking` | CampaignOwner / Collaborator | Lich su import |
| `POST` | `/contents/:id/crawl-info` | CampaignOwner / Collaborator + **Root** | Thu thap lai thong tin |
| `GET` | `/contents/update-status-data-contents` | CampaignOwner / Collaborator | Trigger cap nhat trang thai (async) |
| `GET` | `/contents/update-warning-tags-content` | CampaignOwner / Collaborator | Trigger cap nhat warning tag (async) |

### Content Manual Flows

| Method | Endpoint | Quyen | Mo ta |
|---|---|---|---|
| `GET` | `/content-manual-flows` | **CampaignOwner only** | Lay danh sach luong dieu chinh |
| `POST` | `/content-manual-flows` | **CampaignOwner only** | Tao luong dieu chinh view |
