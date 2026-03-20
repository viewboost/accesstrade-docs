# API Misc - Admin

Base URL: `{{ADMIN_BASE_URL}}` (vd: `https://api.example.com/admin`)

---

## Muc quyen

| Middleware | Mo ta |
|---|---|
| `NoAuth` | Khong can token (public) |
| `RequiredLogin` | Phai co token hop le |
| `IsAdmin` | Phai la Admin (cap cao nhat) |
| `IsCampaignOwner` | Admin hoac Campaign Owner |

---

## 1. Common

### 1.1 Ping

**Quyen:** `NoAuth`
**Endpoint:** `GET /ping`

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/ping"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "message": "pong"
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Server down | `503 Service Unavailable` |

---

### 1.2 Health Check

**Quyen:** `NoAuth`
**Endpoint:** `GET /health`

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/health"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "status": "ok"
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Server down | `503 Service Unavailable` |

---

### 1.3 GetListTopics

**Quyen:** `RequiredLogin`
**Endpoint:** `GET /common/get-list-topics`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/common/get-list-topics" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": ["technology", "fashion", "food", "travel", "beauty"]
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Token khong hop le | `401 Unauthorized` |

---

### 1.4 UpdateAnalyticEventDaily

**Quyen:** `RequiredLogin` (kem `key` query bat buoc)
**Endpoint:** `GET /common/update-event-daily`

> **Chu y:** Endpoint nay yeu cau query param `key` chinh xac. Neu sai, tra ve 401.

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Query Params

| Param | Kieu | Bat buoc | Mo ta |
|---|---|---|---|
| `key` | string | Co | Secret key kich hoat: `177ac2b7-7bed-43c2-8757-5cff85dd5518` |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/common/update-event-daily?key=177ac2b7-7bed-43c2-8757-5cff85dd5518" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {}
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Sai key | `401 Unauthorized` |
| Token khong hop le | `401 Unauthorized` |

---

### 1.5 GetListScope

**Quyen:** `RequiredLogin`
**Endpoint:** `GET /common/scopes`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/common/scopes" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "scopes": ["read", "write", "admin", "campaign_owner"]
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Token khong hop le | `401 Unauthorized` |

---

### 1.6 GetConfiguration

**Quyen:** `RequiredLogin`
**Endpoint:** `GET /common/configurations`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/common/configurations" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "type": "privacy",
    "privacy": {
      "termOfUse": "https://example.com/terms",
      "privacyPolicy": "https://example.com/privacy"
    }
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Token khong hop le | `401 Unauthorized` |

---

### 1.7 UpdateConfiguration

**Quyen:** `RequiredLogin`
**Endpoint:** `PUT /common/configurations`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `type` | string | Co | Loai config, hien tai chi ho tro `"privacy"` | `"privacy"` |
| `privacy` | object | Khong | Object cau hinh privacy | `{}` |
| `privacy.termOfUse` | string | Khong | URL dieu khoan su dung | `"https://example.com/terms"` |
| `privacy.privacyPolicy` | string | Khong | URL chinh sach bao mat | `"https://example.com/privacy"` |

#### cURL

```bash
curl -X PUT "{{ADMIN_BASE_URL}}/common/configurations" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "privacy",
    "privacy": {
      "termOfUse": "https://example.com/terms",
      "privacyPolicy": "https://example.com/privacy"
    }
  }'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": null
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Thieu `type` | `400 Bad Request` |
| `type` khong hop le (khong phai `"privacy"`) | `400 Bad Request` |
| Token khong hop le | `401 Unauthorized` |

---

### 1.8 GetListEventCategory

**Quyen:** `RequiredLogin`
**Endpoint:** `GET /common/event-categories`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `keyword` | string | Khong | Tim kiem theo ten | `"fashion"` |
| `partner` | string | Khong | ID partner | `"664a1f2e3c4b5d6e7f8a9b01"` |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/common/event-categories?keyword=fashion&partner=664a1f2e3c4b5d6e7f8a9b01" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": [
    {
      "_id": "664a1f2e3c4b5d6e7f8a9b10",
      "name": "Fashion",
      "code": "fashion",
      "partner": "664a1f2e3c4b5d6e7f8a9b01"
    }
  ]
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Token khong hop le | `401 Unauthorized` |

---

## 2. Tags

### 2.1 Create Tag

**Quyen:** `IsAdmin`
**Endpoint:** `POST /tags`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `name` | string | Co | Ten tag | `"Hot"` |
| `type` | string | Co | Loai tag (theo constants he thong) | `"content"` |
| `color` | string | Co | Ma mau hex | `"#FF5733"` |
| `partner` | string | Khong | ID partner (MongoDB ObjectID) | `"664a1f2e3c4b5d6e7f8a9b01"` |

#### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/tags" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hot",
    "type": "content",
    "color": "#FF5733",
    "partner": "664a1f2e3c4b5d6e7f8a9b01"
  }'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "664a1f2e3c4b5d6e7f8a9b20",
    "name": "Hot",
    "type": "content",
    "color": "#FF5733",
    "active": false,
    "partner": "664a1f2e3c4b5d6e7f8a9b01",
    "createdAt": "2024-03-20T08:00:00Z",
    "updatedAt": "2024-03-20T08:00:00Z"
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Thieu `name` | `400 Bad Request` |
| Thieu `type` | `400 Bad Request` |
| `type` khong hop le | `400 Bad Request` |
| Thieu `color` | `400 Bad Request` |
| Khong phai Admin | `403 Forbidden` |
| Token khong hop le | `401 Unauthorized` |

---

### 2.2 Update Tag

**Quyen:** `IsAdmin`
**Endpoint:** `PUT /tags/:id`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{TAG_ID}}` | MongoDB ObjectID cua tag |

#### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `name` | string | Co | Ten tag | `"Trending"` |
| `type` | string | Co | Loai tag | `"content"` |
| `color` | string | Co | Ma mau hex | `"#00BFFF"` |
| `partner` | string | Khong | ID partner | `"664a1f2e3c4b5d6e7f8a9b01"` |

#### cURL

```bash
curl -X PUT "{{ADMIN_BASE_URL}}/tags/{{TAG_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Trending",
    "type": "content",
    "color": "#00BFFF",
    "partner": "664a1f2e3c4b5d6e7f8a9b01"
  }'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "{{TAG_ID}}",
    "name": "Trending",
    "type": "content",
    "color": "#00BFFF",
    "active": true,
    "updatedAt": "2024-03-20T09:00:00Z"
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| `{{TAG_ID}}` khong phai ObjectID hop le | `404 Not Found` |
| Tag khong ton tai | `400 Bad Request` |
| Thieu `name` | `400 Bad Request` |
| Khong phai Admin | `403 Forbidden` |

---

### 2.3 ChangeStatus Tag

**Quyen:** `IsAdmin`
**Endpoint:** `PATCH /tags/:id/status`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{TAG_ID}}` | MongoDB ObjectID cua tag |

#### cURL

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/tags/{{TAG_ID}}/status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "{{TAG_ID}}",
    "active": true
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| `{{TAG_ID}}` khong hop le | `404 Not Found` |
| Tag khong ton tai | `400 Bad Request` |
| Khong phai Admin | `403 Forbidden` |

---

### 2.4 GetList Tags

**Quyen:** `RequiredLogin`
**Endpoint:** `GET /tags`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `page` | int | Khong | So trang | `1` |
| `limit` | int | Khong | So ban ghi | `20` |
| `keyword` | string | Khong | Tim kiem theo ten | `"Hot"` |
| `type` | string | Khong | Loc theo loai tag | `"content"` |
| `active` | string | Khong | Loc theo trang thai | `"true"` / `"false"` |
| `partner` | string | Khong | ID partner | `"664a1f2e3c4b5d6e7f8a9b01"` |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/tags?page=1&limit=20&keyword=Hot&active=true" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "tag": [
      {
        "_id": "664a1f2e3c4b5d6e7f8a9b20",
        "name": "Hot",
        "type": "content",
        "color": "#FF5733",
        "active": true,
        "createdAt": "2024-03-20T08:00:00Z"
      }
    ],
    "total": 1,
    "limit": 20
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Token khong hop le | `401 Unauthorized` |

---

## 3. Segments

### 3.1 GetList Segments

**Quyen:** `IsCampaignOwner`
**Endpoint:** `GET /segments`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `page` | int | Khong | So trang | `1` |
| `limit` | int | Khong | So ban ghi | `20` |
| `keyword` | string | Khong | Tim kiem theo ten | `"VIP"` |
| `status` | string | Khong | Trang thai: `active` / `inactive` | `"active"` |
| `partner` | string | Khong | ID partner | `"664a1f2e3c4b5d6e7f8a9b01"` |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/segments?page=1&limit=20&status=active" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "data": [
      {
        "_id": "664a1f2e3c4b5d6e7f8a9b30",
        "name": "VIP Users",
        "type": "manual",
        "status": "active",
        "statistic": {
          "userTotal": 150
        },
        "createdAt": "2024-03-01T08:00:00Z"
      }
    ],
    "total": 1,
    "limit": 20
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Token khong hop le | `401 Unauthorized` |
| Khong co quyen | `403 Forbidden` |

---

### 3.2 Create Segment

**Quyen:** `IsCampaignOwner`
**Endpoint:** `POST /segments`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `name` | string | Co | Ten segment | `"VIP Users"` |
| `type` | string | Co | Loai: `"manual"` hoac `"automatic"` | `"manual"` |
| `partner` | string | Khong | ID partner | `"664a1f2e3c4b5d6e7f8a9b01"` |
| `conditionForAutomatic` | object | Khong | Dieu kien loc tu dong (chi dung khi `type = "automatic"`) | `{}` |
| `conditionForAutomatic.referralCodes` | string[] | Khong | Danh sach ma gioi thieu | `["REF001"]` |

#### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/segments" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "VIP Users",
    "type": "manual",
    "partner": "664a1f2e3c4b5d6e7f8a9b01"
  }'
```

**Vi du voi automatic segment:**

```bash
curl -X POST "{{ADMIN_BASE_URL}}/segments" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Referral Group",
    "type": "automatic",
    "partner": "664a1f2e3c4b5d6e7f8a9b01",
    "conditionForAutomatic": {
      "referralCodes": ["REF001", "REF002"]
    }
  }'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "664a1f2e3c4b5d6e7f8a9b30",
    "name": "VIP Users",
    "type": "manual",
    "status": "inactive",
    "statistic": {
      "userTotal": 0
    },
    "createdAt": "2024-03-20T08:00:00Z"
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Thieu `name` | `400 Bad Request` |
| Thieu `type` | `400 Bad Request` |
| `type` khong hop le | `400 Bad Request` |
| Khong co quyen | `403 Forbidden` |

---

### 3.3 Update Segment

**Quyen:** `IsCampaignOwner`
**Endpoint:** `PUT /segments/:id`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{SEGMENT_ID}}` | MongoDB ObjectID cua segment |

#### Body (JSON)

Tuong tu Create Segment (cac field giong nhau).

#### cURL

```bash
curl -X PUT "{{ADMIN_BASE_URL}}/segments/{{SEGMENT_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "VIP Users Updated",
    "type": "manual"
  }'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "{{SEGMENT_ID}}",
    "name": "VIP Users Updated",
    "type": "manual",
    "updatedAt": "2024-03-20T10:00:00Z"
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| `{{SEGMENT_ID}}` khong hop le | `404 Not Found` |
| Segment khong ton tai | `400 Bad Request` |
| Thieu `name` | `400 Bad Request` |
| Khong co quyen | `403 Forbidden` |

---

### 3.4 GetDetail Segment

**Quyen:** `IsCampaignOwner`
**Endpoint:** `GET /segments/:id`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{SEGMENT_ID}}` | MongoDB ObjectID cua segment |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/segments/{{SEGMENT_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "data": {
      "_id": "{{SEGMENT_ID}}",
      "name": "VIP Users",
      "type": "manual",
      "status": "active",
      "statistic": {
        "userTotal": 150
      },
      "conditionForAutomatic": null,
      "partner": "664a1f2e3c4b5d6e7f8a9b01",
      "createdAt": "2024-03-01T08:00:00Z",
      "updatedAt": "2024-03-20T10:00:00Z"
    }
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| `{{SEGMENT_ID}}` khong hop le | `404 Not Found` |
| Segment khong ton tai | `400 Bad Request` |
| Khong co quyen | `403 Forbidden` |

---

### 3.5 ChangeStatus Segment

**Quyen:** `IsCampaignOwner`
**Endpoint:** `PATCH /segments/:id/status`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{SEGMENT_ID}}` | MongoDB ObjectID cua segment |

#### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `status` | string | Co | Trang thai moi: `active` / `inactive` | `"active"` |

#### cURL

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/segments/{{SEGMENT_ID}}/status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "{{SEGMENT_ID}}",
    "status": "active"
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Thieu `status` | `400 Bad Request` |
| `status` khong hop le | `400 Bad Request` |
| `{{SEGMENT_ID}}` khong hop le | `404 Not Found` |
| Khong co quyen | `403 Forbidden` |

---

## 4. User Segments

### 4.1 GetList User Segments

**Quyen:** `IsAdmin`
**Endpoint:** `GET /user-segments`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `page` | int | Khong | So trang | `1` |
| `limit` | int | Khong | So ban ghi | `20` |
| `segment` | string | Khong | ID segment de loc | `"664a1f2e3c4b5d6e7f8a9b30"` |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/user-segments?page=1&limit=20&segment={{SEGMENT_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "data": [
      {
        "_id": "664a1f2e3c4b5d6e7f8a9b40",
        "user": "664a1f2e3c4b5d6e7f8a9b0c",
        "segment": "{{SEGMENT_ID}}",
        "createdAt": "2024-03-10T08:00:00Z"
      }
    ],
    "total": 1,
    "limit": 20
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Token khong hop le | `401 Unauthorized` |
| Khong phai Admin | `403 Forbidden` |

---

### 4.2 Add User Segments

**Quyen:** `IsAdmin`
**Endpoint:** `POST /user-segments`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `segmentId` | string | Co | MongoDB ObjectID cua segment | `"664a1f2e3c4b5d6e7f8a9b30"` |
| `userIds` | string[] | Khong | Danh sach MongoDB ObjectID cua user | `["664a1f2e3c4b5d6e7f8a9b0c"]` |

#### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/user-segments" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "segmentId": "{{SEGMENT_ID}}",
    "userIds": [
      "664a1f2e3c4b5d6e7f8a9b0c",
      "664a1f2e3c4b5d6e7f8a9b0d"
    ]
  }'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {}
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Thieu `segmentId` | `400 Bad Request` |
| `segmentId` khong phai MongoID | `400 Bad Request` |
| `userIds` chua gia tri khong phai MongoID | `400 Bad Request` |
| Khong phai Admin | `403 Forbidden` |

---

### 4.3 Delete User Segments

**Quyen:** `IsAdmin`
**Endpoint:** `DELETE /user-segments`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `segmentId` | string | Co | MongoDB ObjectID cua segment | `"664a1f2e3c4b5d6e7f8a9b30"` |
| `ids` | string[] | Khong | Danh sach MongoDB ObjectID cua ban ghi user-segment can xoa | `["664a1f2e3c4b5d6e7f8a9b40"]` |

#### cURL

```bash
curl -X DELETE "{{ADMIN_BASE_URL}}/user-segments" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "segmentId": "{{SEGMENT_ID}}",
    "ids": [
      "664a1f2e3c4b5d6e7f8a9b40"
    ]
  }'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {}
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Thieu `segmentId` | `400 Bad Request` |
| `segmentId` khong phai MongoID | `400 Bad Request` |
| `ids` chua gia tri khong phai MongoID | `400 Bad Request` |
| Khong phai Admin | `403 Forbidden` |

---

### 4.4 ImportExcel User Segments

**Quyen:** `IsAdmin`
**Endpoint:** `POST /user-segments/import-excel`

> File Excel phai chua cot dau tien la MongoDB ObjectID cua user (`userId`).

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `multipart/form-data` |

#### Form Data

| Field | Kieu | Bat buoc | Mo ta |
|---|---|---|---|
| `file` | file | Co | File Excel (.xlsx) chua danh sach userIds |
| `segmentId` | string | Co | MongoDB ObjectID cua segment |

#### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/user-segments/import-excel" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -F "file=@/path/to/users.xlsx" \
  -F "segmentId={{SEGMENT_ID}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {}
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Khong upload file | `400 Bad Request` |
| Thieu `segmentId` | `400 Bad Request` |
| File sai dinh dang | `400 Bad Request` |
| UserID trong file khong hop le | `400 Bad Request` |
| Khong phai Admin | `403 Forbidden` |

---

## 5. Admin Notifications

### 5.1 GetList Admin Notifications

**Quyen:** `IsCampaignOwner`
**Endpoint:** `GET /admin-notifications`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `page` | int | Khong | So trang | `1` |
| `limit` | int | Khong | So ban ghi | `20` |
| `keyword` | string | Khong | Tim kiem theo tieu de | `"Khuyen mai"` |
| `type` | string | Khong | Loai notification | `"push"` |
| `category` | string | Khong | Danh muc | `"marketing"` |
| `staff` | string | Khong | ID staff tao | `"664a1f2e3c4b5d6e7f8a9b05"` |
| `status` | string | Khong | Trang thai | `"pending"` |
| `partner` | string | Khong | ID partner | `"664a1f2e3c4b5d6e7f8a9b01"` |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/admin-notifications?page=1&limit=20&status=pending" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "data": [
      {
        "_id": "664a1f2e3c4b5d6e7f8a9b50",
        "title": "Khuyen mai mua he",
        "message": "Giam 50% cho tat ca san pham",
        "status": "pending",
        "isAutomaticTimer": false,
        "category": "marketing",
        "createdAt": "2024-03-20T08:00:00Z"
      }
    ],
    "total": 1,
    "limit": 20
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Token khong hop le | `401 Unauthorized` |
| Khong co quyen | `403 Forbidden` |

---

### 5.2 Create Admin Notification

**Quyen:** `IsCampaignOwner`
**Endpoint:** `POST /admin-notifications`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `title` | string | Co | Tieu de thong bao | `"Khuyen mai mua he"` |
| `message` | string | Co | Noi dung thong bao | `"Giam 50% cho tat ca san pham"` |
| `isAutomaticTimer` | boolean | Khong | Lich gui tu dong | `false` |
| `startAt` | datetime | Khong | Thoi gian gui (ISO 8601, chi dung khi `isAutomaticTimer=true`) | `"2024-04-01T08:00:00Z"` |
| `category` | string | Khong | Danh muc | `"marketing"` |
| `code` | string | Khong | Ma tham chieu | `"SUMMER2024"` |
| `partner` | string | Khong | ID partner | `"664a1f2e3c4b5d6e7f8a9b01"` |
| `users` | string[] | Khong | Danh sach MongoDB ObjectID cua user nhan | `["664a1f2e3c4b5d6e7f8a9b0c"]` |
| `image` | object | Khong | Anh kem theo | `{"url": "https://...", "name": "banner.jpg"}` |
| `filter` | object | Khong | Bo loc nguoi nhan | `{}` |
| `filter.targetUsers` | string | Khong | Loai nguoi nhan: `"all"` hoac `"specificUsers"` | `"all"` |
| `options` | object | Khong | Tuy chon them | `{}` |

#### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/admin-notifications" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Khuyen mai mua he",
    "message": "Giam 50% cho tat ca san pham",
    "isAutomaticTimer": false,
    "category": "marketing",
    "partner": "664a1f2e3c4b5d6e7f8a9b01",
    "filter": {
      "targetUsers": "all"
    }
  }'
```

**Lich gui cu the:**

```bash
curl -X POST "{{ADMIN_BASE_URL}}/admin-notifications" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Nhac lich su kien",
    "message": "Su kien bat dau luc 8 gio sang ngay mai",
    "isAutomaticTimer": true,
    "startAt": "2024-04-01T01:00:00Z",
    "filter": {
      "targetUsers": "specificUsers"
    },
    "users": ["664a1f2e3c4b5d6e7f8a9b0c"]
  }'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "664a1f2e3c4b5d6e7f8a9b50",
    "title": "Khuyen mai mua he",
    "message": "Giam 50% cho tat ca san pham",
    "status": "pending",
    "isAutomaticTimer": false,
    "createdAt": "2024-03-20T08:00:00Z"
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Thieu `title` | `400 Bad Request` |
| Thieu `message` | `400 Bad Request` |
| `users` chua MongoID khong hop le | `400 Bad Request` |
| Khong co quyen | `403 Forbidden` |

---

### 5.3 Update Admin Notification

**Quyen:** `IsCampaignOwner`
**Endpoint:** `PUT /admin-notifications/:id`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{NOTIFICATION_ID}}` | MongoDB ObjectID cua notification |

#### Body (JSON)

Tuong tu Create Admin Notification.

#### cURL

```bash
curl -X PUT "{{ADMIN_BASE_URL}}/admin-notifications/{{NOTIFICATION_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Khuyen mai mua he (cap nhat)",
    "message": "Giam 60% cho tat ca san pham",
    "isAutomaticTimer": false
  }'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "{{NOTIFICATION_ID}}",
    "title": "Khuyen mai mua he (cap nhat)",
    "updatedAt": "2024-03-20T09:00:00Z"
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| `{{NOTIFICATION_ID}}` khong hop le | `404 Not Found` |
| Thieu `title` | `400 Bad Request` |
| Khong co quyen | `403 Forbidden` |

---

### 5.4 GetDetail Admin Notification

**Quyen:** `IsCampaignOwner`
**Endpoint:** `GET /admin-notifications/:id`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{NOTIFICATION_ID}}` | MongoDB ObjectID cua notification |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/admin-notifications/{{NOTIFICATION_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "data": {
      "_id": "{{NOTIFICATION_ID}}",
      "title": "Khuyen mai mua he",
      "message": "Giam 50% cho tat ca san pham",
      "status": "pending",
      "isAutomaticTimer": false,
      "category": "marketing",
      "filter": {
        "targetUsers": "all"
      },
      "options": {},
      "users": [],
      "partner": "664a1f2e3c4b5d6e7f8a9b01",
      "createdAt": "2024-03-20T08:00:00Z",
      "updatedAt": "2024-03-20T08:00:00Z"
    }
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| `{{NOTIFICATION_ID}}` khong hop le | `404 Not Found` |
| Khong co quyen | `403 Forbidden` |

---

### 5.5 Clone Admin Notification

**Quyen:** `IsCampaignOwner`
**Endpoint:** `POST /admin-notifications/:id/clone`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{NOTIFICATION_ID}}` | MongoDB ObjectID cua notification can clone |

#### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/admin-notifications/{{NOTIFICATION_ID}}/clone" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {}
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| `{{NOTIFICATION_ID}}` khong hop le | `404 Not Found` |
| Notification khong ton tai | `400 Bad Request` |
| Khong co quyen | `403 Forbidden` |

---

### 5.6 Completed Admin Notification

**Quyen:** `IsCampaignOwner`
**Endpoint:** `PATCH /admin-notifications/:id/completed`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{NOTIFICATION_ID}}` | MongoDB ObjectID cua notification |

#### cURL

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/admin-notifications/{{NOTIFICATION_ID}}/completed" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {}
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| `{{NOTIFICATION_ID}}` khong hop le | `404 Not Found` |
| Notification khong o trang thai cho phep | `400 Bad Request` |
| Khong co quyen | `403 Forbidden` |

---

### 5.7 Rejected Admin Notification

**Quyen:** `IsCampaignOwner`
**Endpoint:** `PATCH /admin-notifications/:id/rejected`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{NOTIFICATION_ID}}` | MongoDB ObjectID cua notification |

#### cURL

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/admin-notifications/{{NOTIFICATION_ID}}/rejected" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {}
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| `{{NOTIFICATION_ID}}` khong hop le | `404 Not Found` |
| Notification khong o trang thai cho phep | `400 Bad Request` |
| Khong co quyen | `403 Forbidden` |

---

## 6. Identifications

### 6.1 GetList Identifications

**Quyen:** `IsAdmin`
**Endpoint:** `GET /identifications`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `page` | int | Khong | So trang | `1` |
| `limit` | int | Khong | So ban ghi | `20` |
| `status` | string | Khong | Trang thai xac minh | `"pending"` / `"approved"` / `"rejected"` |
| `fromAt` | string | Khong | Ngay bat dau (ISO date) | `"2024-01-01"` |
| `toAt` | string | Khong | Ngay ket thuc (ISO date) | `"2024-12-31"` |
| `user` | string | Khong | ID user | `"664a1f2e3c4b5d6e7f8a9b0c"` |
| `staff` | string | Khong | ID staff xu ly | `"664a1f2e3c4b5d6e7f8a9b05"` |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/identifications?page=1&limit=20&status=pending&fromAt=2024-01-01&toAt=2024-12-31" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "docs": [
      {
        "_id": "664a1f2e3c4b5d6e7f8a9b60",
        "user": "664a1f2e3c4b5d6e7f8a9b0c",
        "status": "pending",
        "frontImage": {"url": "https://cdn.example.com/cccd-front.jpg"},
        "backImage": {"url": "https://cdn.example.com/cccd-back.jpg"},
        "createdAt": "2024-03-15T10:00:00Z"
      }
    ],
    "total": 1,
    "limit": 20
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Token khong hop le | `401 Unauthorized` |
| Khong phai Admin | `403 Forbidden` |

---

### 6.2 GetDetail Identification

**Quyen:** `IsAdmin`
**Endpoint:** `GET /identifications/:id`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{IDENTIFICATION_ID}}` | MongoDB ObjectID cua identification |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/identifications/{{IDENTIFICATION_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "data": {
      "_id": "{{IDENTIFICATION_ID}}",
      "user": "664a1f2e3c4b5d6e7f8a9b0c",
      "status": "pending",
      "frontImage": {"url": "https://cdn.example.com/cccd-front.jpg", "name": "front.jpg"},
      "backImage": {"url": "https://cdn.example.com/cccd-back.jpg", "name": "back.jpg"},
      "note": "",
      "createdAt": "2024-03-15T10:00:00Z",
      "updatedAt": "2024-03-15T10:00:00Z"
    }
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| `{{IDENTIFICATION_ID}}` khong hop le | `404 Not Found` |
| Khong ton tai | `400 Bad Request` |
| Khong phai Admin | `403 Forbidden` |

---

### 6.3 ChangeStatus Identification

**Quyen:** `IsAdmin`
**Endpoint:** `PATCH /identifications/:id/status`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{IDENTIFICATION_ID}}` | MongoDB ObjectID cua identification |

#### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `status` | string | Co | Trang thai moi (xem constants he thong) | `"approved"` / `"rejected"` |
| `note` | string | Khong | Ghi chu ly do | `"Anh chup khong ro"` |

#### cURL

**Duyet:**

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/identifications/{{IDENTIFICATION_ID}}/status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"status": "approved"}'
```

**Tu choi:**

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/identifications/{{IDENTIFICATION_ID}}/status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"status": "rejected", "note": "Anh chup khong ro, vui long chup lai"}'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {}
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Thieu `status` | `400 Bad Request` |
| `status` khong hop le | `400 Bad Request` |
| `{{IDENTIFICATION_ID}}` khong hop le | `404 Not Found` |
| Khong phai Admin | `403 Forbidden` |

---

## 7. Roles

### 7.1 GetList Roles

**Quyen:** `IsAdmin`
**Endpoint:** `GET /roles`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `keyword` | string | Khong | Tim kiem theo ten role | `"admin"` |

> **Chu y:** Endpoint nay khong ho tro `page` va `limit` - tra ve toan bo danh sach.

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/roles?keyword=admin" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": [
    {
      "_id": "664a1f2e3c4b5d6e7f8a9b70",
      "name": "admin",
      "description": "Quan tri vien he thong",
      "scopes": ["read", "write", "admin"],
      "createdAt": "2024-01-01T00:00:00Z"
    },
    {
      "_id": "664a1f2e3c4b5d6e7f8a9b71",
      "name": "campaign_owner",
      "description": "Quan ly chien dich",
      "scopes": ["read", "write"],
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Token khong hop le | `401 Unauthorized` |
| Khong phai Admin | `403 Forbidden` |

---

## 8. Quick Actions

### 8.1 Create Quick Action

**Quyen:** `IsCampaignOwner`
**Endpoint:** `POST /quick-actions`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `name` | string | Co | Ten quick action | `"Xem su kien"` |
| `icon` | object | Khong | Icon (FilePhoto) | `{"url": "https://cdn.example.com/icon.png", "name": "icon.png"}` |
| `action` | object | Khong | Hanh dong khi bam | `{"type": "deeplink", "value": "app://events"}` |
| `partner` | string | Khong | ID partner | `"664a1f2e3c4b5d6e7f8a9b01"` |

#### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/quick-actions" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Xem su kien",
    "icon": {
      "url": "https://cdn.example.com/event-icon.png",
      "name": "event-icon.png"
    },
    "action": {
      "type": "deeplink",
      "value": "app://events"
    },
    "partner": "664a1f2e3c4b5d6e7f8a9b01"
  }'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "664a1f2e3c4b5d6e7f8a9b80",
    "name": "Xem su kien",
    "icon": {"url": "https://cdn.example.com/event-icon.png"},
    "action": {"type": "deeplink", "value": "app://events"},
    "partner": "664a1f2e3c4b5d6e7f8a9b01",
    "createdAt": "2024-03-20T08:00:00Z"
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Thieu `name` | `400 Bad Request` |
| Khong co quyen | `403 Forbidden` |
| Token khong hop le | `401 Unauthorized` |

---

### 8.2 Update Quick Action

**Quyen:** `IsCampaignOwner`
**Endpoint:** `PUT /quick-actions/:id`

> **Chu y:** Router dang khai bao method `[post]` cho Update, nhung dung `PUT` theo dac ta.

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{QUICK_ACTION_ID}}` | MongoDB ObjectID cua quick action |

#### Body (JSON)

Tuong tu Create Quick Action.

#### cURL

```bash
curl -X PUT "{{ADMIN_BASE_URL}}/quick-actions/{{QUICK_ACTION_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Xem su kien (cap nhat)",
    "action": {
      "type": "deeplink",
      "value": "app://events/list"
    }
  }'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "{{QUICK_ACTION_ID}}",
    "name": "Xem su kien (cap nhat)",
    "updatedAt": "2024-03-20T09:00:00Z"
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| `{{QUICK_ACTION_ID}}` khong hop le | `404 Not Found` |
| Thieu `name` | `400 Bad Request` |
| Khong co quyen | `403 Forbidden` |

---

### 8.3 ChangeStatus Quick Action

**Quyen:** `IsCampaignOwner`
**Endpoint:** `PATCH /quick-actions/:id/status`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{QUICK_ACTION_ID}}` | MongoDB ObjectID cua quick action |

#### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `status` | string | Co | Trang thai moi: `active` / `inactive` | `"active"` |

#### cURL

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/quick-actions/{{QUICK_ACTION_ID}}/status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "{{QUICK_ACTION_ID}}",
    "status": "active"
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Thieu `status` | `400 Bad Request` |
| `status` khong hop le | `400 Bad Request` |
| `{{QUICK_ACTION_ID}}` khong hop le | `404 Not Found` |
| Khong co quyen | `403 Forbidden` |

---

### 8.4 GetList Quick Actions

**Quyen:** `IsCampaignOwner`
**Endpoint:** `GET /quick-actions`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `page` | int | Khong | So trang | `1` |
| `limit` | int | Khong | So ban ghi | `20` |
| `keyword` | string | Khong | Tim kiem theo ten | `"Xem su kien"` |
| `status` | string | Khong | Trang thai | `"active"` |
| `partner` | string | Khong | ID partner | `"664a1f2e3c4b5d6e7f8a9b01"` |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/quick-actions?page=1&limit=20&status=active" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": [
    {
      "_id": "664a1f2e3c4b5d6e7f8a9b80",
      "name": "Xem su kien",
      "icon": {"url": "https://cdn.example.com/event-icon.png"},
      "action": {"type": "deeplink", "value": "app://events"},
      "status": "active",
      "updatedAt": "2024-03-20T08:00:00Z"
    }
  ]
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Token khong hop le | `401 Unauthorized` |
| Khong co quyen | `403 Forbidden` |

---

### 8.5 GetDetail Quick Action

**Quyen:** `IsCampaignOwner`
**Endpoint:** `GET /quick-actions/:id`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{QUICK_ACTION_ID}}` | MongoDB ObjectID cua quick action |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/quick-actions/{{QUICK_ACTION_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "{{QUICK_ACTION_ID}}",
    "name": "Xem su kien",
    "icon": {"url": "https://cdn.example.com/event-icon.png", "name": "event-icon.png"},
    "action": {"type": "deeplink", "value": "app://events"},
    "status": "active",
    "partner": "664a1f2e3c4b5d6e7f8a9b01",
    "createdAt": "2024-03-20T08:00:00Z",
    "updatedAt": "2024-03-20T08:00:00Z"
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| `{{QUICK_ACTION_ID}}` khong hop le | `404 Not Found` |
| Khong co quyen | `403 Forbidden` |

---

## 9. Data Exports

### 9.1 Export (Create)

**Quyen:** `IsCampaignOwner`
**Endpoint:** `POST /data-exports`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `name` | string | Khong | Ten file export | `"Bao cao thang 3"` |
| `type` | string | Khong | Loai data export | `"content"` / `"user"` / `"transfer"` |
| `emails` | string[] | Khong | Email nhan ket qua | `["admin@example.com"]` |
| `isShowStatistic` | boolean | Khong | Co kem thong ke | `true` |
| `condition` | object | Khong | Dieu kien loc du lieu | `{}` |
| `condition.fromAt` | string | Khong | Ngay bat dau | `"2024-01-01"` |
| `condition.toAt` | string | Khong | Ngay ket thuc | `"2024-03-31"` |
| `condition.event` | string | Khong | ID su kien | `"664a1f2e3c4b5d6e7f8a9b02"` |
| `condition.events` | string[] | Khong | Danh sach ID su kien | `["664a..."]` |
| `condition.status` | string | Khong | Trang thai | `"approved"` |
| `condition.keyword` | string | Khong | Tu khoa tim kiem | `"nguyen"` |
| `condition.partner` | string | Khong | ID partner | `"664a1f2e3c4b5d6e7f8a9b01"` |
| `condition.user` | string | Khong | ID user | `"664a1f2e3c4b5d6e7f8a9b0c"` |
| `condition.users` | string[] | Khong | Danh sach ID user | `["664a..."]` |
| `condition.source` | string | Khong | Nguon du lieu | `"tiktok"` |
| `condition.tag` | string | Khong | ID tag | `"664a1f2e3c4b5d6e7f8a9b20"` |
| `condition.format` | string | Khong | Dinh dang file | `"xlsx"` |
| `condition.entities` | string[] | Khong | Danh sach entity | `["content", "user"]` |

#### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/data-exports" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bao cao thang 3",
    "type": "content",
    "emails": ["admin@example.com"],
    "isShowStatistic": true,
    "condition": {
      "fromAt": "2024-03-01",
      "toAt": "2024-03-31",
      "partner": "664a1f2e3c4b5d6e7f8a9b01"
    }
  }'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "664a1f2e3c4b5d6e7f8a9b90"
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Khong co quyen | `403 Forbidden` |
| Token khong hop le | `401 Unauthorized` |

---

### 9.2 GetList Data Exports

**Quyen:** `IsCampaignOwner`
**Endpoint:** `GET /data-exports`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `page` | int | Khong | So trang (>= 0) | `1` |
| `limit` | int | Khong | So ban ghi (>= 0) | `20` |
| `status` | string | Khong | Trang thai export | `"done"` / `"processing"` / `"failed"` |
| `type` | string | Khong | Loai export | `"content"` |
| `keyword` | string | Khong | Tim kiem theo ten | `"Bao cao"` |
| `partner` | string | Khong | ID partner | `"664a1f2e3c4b5d6e7f8a9b01"` |
| `filterByOwner` | boolean | Khong | Chi hien thi export cua minh | `true` |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/data-exports?page=1&limit=20&status=done&filterByOwner=true" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "docs": [
      {
        "_id": "664a1f2e3c4b5d6e7f8a9b90",
        "name": "Bao cao thang 3",
        "type": "content",
        "status": "done",
        "fileUrl": "https://s3.example.com/exports/report-march.xlsx",
        "createdAt": "2024-03-20T08:00:00Z",
        "updatedAt": "2024-03-20T08:05:00Z"
      }
    ]
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| `page` < 0 | `400 Bad Request` |
| `limit` < 0 | `400 Bad Request` |
| Khong co quyen | `403 Forbidden` |

---

### 9.3 GetById Data Export

**Quyen:** `IsCampaignOwner`
**Endpoint:** `GET /data-exports/:id`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{EXPORT_ID}}` | MongoDB ObjectID cua export job |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/data-exports/{{EXPORT_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "{{EXPORT_ID}}",
    "name": "Bao cao thang 3",
    "type": "content",
    "status": "done",
    "emails": ["admin@example.com"],
    "isShowStatistic": true,
    "condition": {
      "fromAt": "2024-03-01",
      "toAt": "2024-03-31",
      "partner": "664a1f2e3c4b5d6e7f8a9b01"
    },
    "createdBy": "664a1f2e3c4b5d6e7f8a9b05",
    "createdAt": "2024-03-20T08:00:00Z",
    "updatedAt": "2024-03-20T08:05:00Z"
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| `{{EXPORT_ID}}` khong hop le | `404 Not Found` |
| Export khong ton tai | `400 Bad Request` |
| Khong co quyen | `403 Forbidden` |

---

### 9.4 GetPreSign Data Export

**Quyen:** `IsCampaignOwner`
**Endpoint:** `GET /data-exports/:id/pre-sign`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{EXPORT_ID}}` | MongoDB ObjectID cua export job |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/data-exports/{{EXPORT_ID}}/pre-sign" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "url": "https://s3.example.com/exports/report-march.xlsx?X-Amz-Signature=abc123&X-Amz-Expires=3600"
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| `{{EXPORT_ID}}` khong hop le | `404 Not Found` |
| Export chua done | `400 Bad Request` |
| Khong co quyen | `403 Forbidden` |

---

## 10. Manage Codes

### 10.1 Create Manage Code

**Quyen:** `IsAdmin`
**Endpoint:** `POST /manage-codes`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `partner` | string | Co | MongoDB ObjectID cua partner | `"664a1f2e3c4b5d6e7f8a9b01"` |
| `code` | string | Co | Ma nhan vien | `"TCB001"` |

#### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/manage-codes" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "partner": "664a1f2e3c4b5d6e7f8a9b01",
    "code": "TCB001"
  }'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "664a1f2e3c4b5d6e7f8a9ba0",
    "partner": "664a1f2e3c4b5d6e7f8a9b01",
    "code": "TCB001",
    "isUsed": false,
    "type": "employee",
    "createdAt": "2024-03-20T08:00:00Z"
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Thieu `partner` | `400 Bad Request` |
| `partner` khong phai MongoID | `400 Bad Request` |
| Thieu `code` | `400 Bad Request` |
| Khong phai Admin | `403 Forbidden` |

---

### 10.2 Delete Manage Code

**Quyen:** `IsAdmin`
**Endpoint:** `DELETE /manage-codes/:id`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{CODE_ID}}` | MongoDB ObjectID cua manage code |

#### cURL

```bash
curl -X DELETE "{{ADMIN_BASE_URL}}/manage-codes/{{CODE_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {}
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| `{{CODE_ID}}` khong hop le | `404 Not Found` |
| Code khong ton tai | `400 Bad Request` |
| Khong phai Admin | `403 Forbidden` |

---

### 10.3 GetList Manage Codes

**Quyen:** `IsAdmin`
**Endpoint:** `GET /manage-codes`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `page` | int | Khong | So trang | `1` |
| `limit` | int | Khong | So ban ghi | `20` |
| `partner` | string | Khong | ID partner | `"664a1f2e3c4b5d6e7f8a9b01"` |
| `code` | string | Khong | Tim kiem theo ma | `"TCB001"` |
| `isUsed` | string | Khong | Da su dung chua | `"true"` / `"false"` |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/manage-codes?page=1&limit=20&partner=664a1f2e3c4b5d6e7f8a9b01&isUsed=false" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "manageCode": [
      {
        "_id": "664a1f2e3c4b5d6e7f8a9ba0",
        "partner": "664a1f2e3c4b5d6e7f8a9b01",
        "code": "TCB001",
        "isUsed": false,
        "type": "employee",
        "createdAt": "2024-03-20T08:00:00Z"
      }
    ],
    "total": 1,
    "limit": 20
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Token khong hop le | `401 Unauthorized` |
| Khong phai Admin | `403 Forbidden` |

---

### 10.4 ImportExcel Manage Codes

**Quyen:** `IsAdmin`
**Endpoint:** `POST /manage-codes/import-excel`

> File Excel phai chua cot dau tien la ma nhan vien (`code`).

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `multipart/form-data` |

#### Form Data

| Field | Kieu | Bat buoc | Mo ta |
|---|---|---|---|
| `file` | file | Co | File Excel (.xlsx) chua danh sach ma nhan vien |
| `partner` | string | Co | MongoDB ObjectID cua partner |

#### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/manage-codes/import-excel" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -F "file=@/path/to/codes.xlsx" \
  -F "partner=664a1f2e3c4b5d6e7f8a9b01"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {}
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Khong upload file | `400 Bad Request` |
| Thieu `partner` | `400 Bad Request` |
| `partner` khong phai MongoID | `400 Bad Request` |
| Ma trong file bi trong | `400 Bad Request` |
| Khong phai Admin | `403 Forbidden` |

---

## 11. Blacklist Keywords

### 11.1 Create Blacklist Keyword

**Quyen:** `IsAdmin`
**Endpoint:** `POST /blacklist-keywords`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `keyword` | string | Co | Tu khoa bi cam | `"spam"` |

#### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/blacklist-keywords" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "spam"}'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "664a1f2e3c4b5d6e7f8a9bb0",
    "keyword": "spam",
    "active": true,
    "createdAt": "2024-03-20T08:00:00Z"
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Thieu `keyword` | `400 Bad Request` |
| Khong phai Admin | `403 Forbidden` |

---

### 11.2 Update Blacklist Keyword

**Quyen:** `IsAdmin`
**Endpoint:** `PUT /blacklist-keywords/:id`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{KEYWORD_ID}}` | MongoDB ObjectID cua blacklist keyword |

#### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `keyword` | string | Co | Tu khoa moi | `"spam content"` |

#### cURL

```bash
curl -X PUT "{{ADMIN_BASE_URL}}/blacklist-keywords/{{KEYWORD_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "spam content"}'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "{{KEYWORD_ID}}",
    "keyword": "spam content",
    "updatedAt": "2024-03-20T09:00:00Z"
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| `{{KEYWORD_ID}}` khong hop le | `404 Not Found` |
| Thieu `keyword` | `400 Bad Request` |
| Khong phai Admin | `403 Forbidden` |

---

### 11.3 Delete Blacklist Keyword

**Quyen:** `IsAdmin`
**Endpoint:** `DELETE /blacklist-keywords/:id`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{KEYWORD_ID}}` | MongoDB ObjectID cua blacklist keyword |

#### cURL

```bash
curl -X DELETE "{{ADMIN_BASE_URL}}/blacklist-keywords/{{KEYWORD_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {}
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| `{{KEYWORD_ID}}` khong hop le | `404 Not Found` |
| Keyword khong ton tai | `400 Bad Request` |
| Khong phai Admin | `403 Forbidden` |

---

### 11.4 ChangeStatus Blacklist Keyword

**Quyen:** `IsAdmin`
**Endpoint:** `PATCH /blacklist-keywords/:id/status`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{KEYWORD_ID}}` | MongoDB ObjectID cua blacklist keyword |

> **Chu y:** ChangeStatus toggle trang thai hien tai (active <-> inactive), khong can body.

#### cURL

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/blacklist-keywords/{{KEYWORD_ID}}/status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "{{KEYWORD_ID}}",
    "active": false
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| `{{KEYWORD_ID}}` khong hop le | `404 Not Found` |
| Keyword khong ton tai | `400 Bad Request` |
| Khong phai Admin | `403 Forbidden` |

---

### 11.5 GetList Blacklist Keywords

**Quyen:** `IsAdmin`
**Endpoint:** `GET /blacklist-keywords`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `page` | int | Khong | So trang | `1` |
| `limit` | int | Khong | So ban ghi | `20` |
| `keyword` | string | Khong | Tim kiem tu khoa | `"spam"` |
| `active` | string | Khong | Trang thai kich hoat | `"true"` / `"false"` |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/blacklist-keywords?page=1&limit=20&keyword=spam&active=true" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "blacklistKeyword": [
      {
        "_id": "664a1f2e3c4b5d6e7f8a9bb0",
        "keyword": "spam",
        "active": true,
        "createdAt": "2024-03-20T08:00:00Z"
      }
    ],
    "total": 1,
    "limit": 20
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Token khong hop le | `401 Unauthorized` |
| Khong phai Admin | `403 Forbidden` |

---

### 11.6 ImportExcel Blacklist Keywords

**Quyen:** `IsAdmin`
**Endpoint:** `POST /blacklist-keywords/import-excel`

> File Excel phai chua cot dau tien la tu khoa (`keyword`).

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `multipart/form-data` |

#### Form Data

| Field | Kieu | Bat buoc | Mo ta |
|---|---|---|---|
| `file` | file | Co | File Excel (.xlsx) chua danh sach tu khoa bi cam |

#### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/blacklist-keywords/import-excel" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -F "file=@/path/to/keywords.xlsx"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "imported": 50,
    "skipped": 2
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Khong upload file | `400 Bad Request` |
| Tu khoa trong file bi trong | `400 Bad Request` |
| File sai dinh dang | `400 Bad Request` |
| Khong phai Admin | `403 Forbidden` |

---

## 12. Auto Approve Rules

### 12.1 Create Auto Approve Rule

**Quyen:** `IsAdmin`
**Endpoint:** `POST /auto-approve-rules`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `eventId` | string | Co | ID su kien ap dung | `"664a1f2e3c4b5d6e7f8a9b02"` |
| `name` | string | Co | Ten quy tac | `"Quy tac duyet tu dong TikTok"` |
| `minOverallScore` | int | Khong | Diem tong thieu nieu | `70` |
| `requireMatchEvent` | boolean | Khong | Bat buoc noi dung phai match su kien | `true` |
| `requireNoBlacklist` | boolean | Khong | Bat buoc khong co tu khoa bi cam | `true` |
| `minCriteriaScore` | int | Khong | Diem tieu chi toi thieu | `60` |
| `minView` | float | Khong | Luot xem toi thieu | `1000` |
| `minEngagement` | float | Khong | Ti le tuong tac toi thieu (%) | `2.5` |
| `applyForSources` | string[] | Khong | Nguon ap dung: `tiktok`, `youtube`, `facebook`, ... | `["tiktok"]` |
| `active` | boolean | Khong | Kich hoat ngay | `true` |

#### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/auto-approve-rules" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "664a1f2e3c4b5d6e7f8a9b02",
    "name": "Quy tac duyet tu dong TikTok",
    "minOverallScore": 70,
    "requireMatchEvent": true,
    "requireNoBlacklist": true,
    "minCriteriaScore": 60,
    "minView": 1000,
    "minEngagement": 2.5,
    "applyForSources": ["tiktok"],
    "active": true
  }'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "664a1f2e3c4b5d6e7f8a9bc0",
    "eventId": "664a1f2e3c4b5d6e7f8a9b02",
    "name": "Quy tac duyet tu dong TikTok",
    "minOverallScore": 70,
    "requireMatchEvent": true,
    "requireNoBlacklist": true,
    "minCriteriaScore": 60,
    "minView": 1000,
    "minEngagement": 2.5,
    "applyForSources": ["tiktok"],
    "active": true,
    "createdAt": "2024-03-20T08:00:00Z"
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Thieu `eventId` | `400 Bad Request` |
| Thieu `name` | `400 Bad Request` |
| Khong phai Admin | `403 Forbidden` |

---

### 12.2 Update Auto Approve Rule

**Quyen:** `IsAdmin`
**Endpoint:** `PUT /auto-approve-rules/:id`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{RULE_ID}}` | MongoDB ObjectID cua auto approve rule |

#### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `name` | string | Co | Ten quy tac | `"Quy tac cap nhat"` |
| `minOverallScore` | int | Khong | Diem tong thieu nhat | `80` |
| `requireMatchEvent` | boolean | Khong | Bat buoc match su kien | `false` |
| `requireNoBlacklist` | boolean | Khong | Bat buoc khong blacklist | `true` |
| `minCriteriaScore` | int | Khong | Diem tieu chi toi thieu | `65` |
| `minView` | float | Khong | Luot xem toi thieu | `2000` |
| `minEngagement` | float | Khong | Ti le tuong tac toi thieu (%) | `3.0` |
| `applyForSources` | string[] | Khong | Nguon ap dung | `["tiktok", "youtube"]` |
| `active` | boolean | Khong | Trang thai kich hoat | `true` |

#### cURL

```bash
curl -X PUT "{{ADMIN_BASE_URL}}/auto-approve-rules/{{RULE_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Quy tac cap nhat",
    "minOverallScore": 80,
    "minView": 2000,
    "applyForSources": ["tiktok", "youtube"],
    "active": true
  }'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "{{RULE_ID}}",
    "name": "Quy tac cap nhat",
    "minOverallScore": 80,
    "updatedAt": "2024-03-20T09:00:00Z"
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| `{{RULE_ID}}` khong hop le | `404 Not Found` |
| Thieu `name` | `400 Bad Request` |
| Khong phai Admin | `403 Forbidden` |

---

### 12.3 Delete Auto Approve Rule

**Quyen:** `IsAdmin`
**Endpoint:** `DELETE /auto-approve-rules/:id`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{RULE_ID}}` | MongoDB ObjectID cua auto approve rule |

#### cURL

```bash
curl -X DELETE "{{ADMIN_BASE_URL}}/auto-approve-rules/{{RULE_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {}
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| `{{RULE_ID}}` khong hop le | `404 Not Found` |
| Rule khong ton tai | `400 Bad Request` |
| Khong phai Admin | `403 Forbidden` |

---

### 12.4 ChangeStatus Auto Approve Rule

**Quyen:** `IsAdmin`
**Endpoint:** `PATCH /auto-approve-rules/:id/status`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Mo ta |
|---|---|
| `{{RULE_ID}}` | MongoDB ObjectID cua auto approve rule |

> **Chu y:** ChangeStatus toggle trang thai active hien tai, khong can body.

#### cURL

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/auto-approve-rules/{{RULE_ID}}/status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "{{RULE_ID}}",
    "active": false
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| `{{RULE_ID}}` khong hop le | `404 Not Found` |
| Rule khong ton tai | `400 Bad Request` |
| Khong phai Admin | `403 Forbidden` |

---

### 12.5 GetList Auto Approve Rules

**Quyen:** `IsAdmin`
**Endpoint:** `GET /auto-approve-rules`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `page` | int | Khong | So trang | `1` |
| `limit` | int | Khong | So ban ghi | `20` |
| `keyword` | string | Khong | Tim kiem theo ten | `"TikTok"` |
| `active` | string | Khong | Trang thai | `"true"` / `"false"` |
| `eventId` | string | Co | ID su kien (bat buoc de loc dung su kien) | `"664a1f2e3c4b5d6e7f8a9b02"` |

> **Chu y:** `eventId` la bat buoc trong GetList. Neu khong truyen se bi loi validation.

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/auto-approve-rules?page=1&limit=20&eventId=664a1f2e3c4b5d6e7f8a9b02&active=true" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "autoApproveRules": [
      {
        "_id": "664a1f2e3c4b5d6e7f8a9bc0",
        "eventId": "664a1f2e3c4b5d6e7f8a9b02",
        "name": "Quy tac duyet tu dong TikTok",
        "minOverallScore": 70,
        "minView": 1000,
        "minEngagement": 2.5,
        "applyForSources": ["tiktok"],
        "active": true,
        "createdAt": "2024-03-20T08:00:00Z"
      }
    ],
    "total": 1,
    "limit": 20
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Thieu `eventId` | `400 Bad Request` |
| Token khong hop le | `401 Unauthorized` |
| Khong phai Admin | `403 Forbidden` |

---

## 13. Audits

### 13.1 GetList Audits

**Quyen:** `RequiredLogin`
**Endpoint:** `GET /audits`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `page` | int | Khong | So trang | `1` |
| `limit` | int | Khong | So ban ghi | `20` |
| `staff` | string | Khong | ID staff thuc hien hanh dong | `"664a1f2e3c4b5d6e7f8a9b05"` |
| `targetId` | string | Khong | ID doi tuong bi tac dong | `"664a1f2e3c4b5d6e7f8a9b02"` |

> **Chu y:** Theo handler, cac field loc ho tro la `staff` va `targetId`. Tham so `action` va `staffId` trong dac ta goc la alias cua `targetId` va `staff`.

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/audits?page=1&limit=20&staff=664a1f2e3c4b5d6e7f8a9b05" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**Loc theo doi tuong:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/audits?page=1&limit=20&targetId=664a1f2e3c4b5d6e7f8a9b02" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "audit": [
      {
        "_id": "664a1f2e3c4b5d6e7f8a9bd0",
        "action": "update_campaign",
        "staff": "664a1f2e3c4b5d6e7f8a9b05",
        "targetId": "664a1f2e3c4b5d6e7f8a9b02",
        "targetType": "campaign",
        "before": {"status": "inactive"},
        "after": {"status": "active"},
        "createdAt": "2024-03-20T10:30:00Z"
      },
      {
        "_id": "664a1f2e3c4b5d6e7f8a9bd1",
        "action": "approve_content",
        "staff": "664a1f2e3c4b5d6e7f8a9b05",
        "targetId": "664a1f2e3c4b5d6e7f8a9b10",
        "targetType": "content",
        "createdAt": "2024-03-20T09:15:00Z"
      }
    ],
    "total": 2,
    "limit": 20
  }
}
```

#### Test loi

| Truong hop | Expected |
|---|---|
| Token khong hop le | `401 Unauthorized` |
