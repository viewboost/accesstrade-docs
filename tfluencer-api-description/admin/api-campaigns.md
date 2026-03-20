# API Campaigns - Admin

Base URL: `{{ADMIN_BASE_URL}}` (vd: `https://admin-api.viewboost.vn`)

---

## Muc quyen

| Middleware | Mo ta |
|---|---|
| `RequiredLogin` | Phai co token hop le |
| `IsCampaginOwner` | Phai la Campaign Owner tro len |

Tat ca API trong file nay yeu cau **IsCampaginOwner**.

---

## Bien duong dan

| Bien | Mo ta | Vi du |
|---|---|---|
| `{{CAMPAIGN_ID}}` | MongoDB ObjectID cua Campaign | `664a1f2e3c4b5d6e7f8a9b0c` |
| `{{SESSION_ID}}` | MongoDB ObjectID cua Matching Session | `665b2f3e4c5b6d7e8f9a0b1c` |
| `{{BUDGET_ID}}` | MongoDB ObjectID cua Budget Campaign | `667c3d4e5d6c7e8f9a0b1c2d` |

---

# PHAN 1: CAMPAIGNS

---

## 1. Create - Tao Campaign

**Quyen:** `IsCampaginOwner`
**Endpoint:** `POST /campaigns`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `name` | string | **Co** | Ten campaign | `"T-Fluencers Q2 2025"` |
| `desc` | string | Khong | Mo ta campaign | `"Thay thach Q2"` |
| `categories` | string[] | Khong | Danh sach category ID | `["cat_lifestyle", "cat_finance"]` |
| `budgetTiers` | string[] | Khong | Danh sach budget tier | `["nano", "micro"]` |
| `minEngagement` | float | Khong | Ti le engagement toi thieu (0-100) | `2.5` |
| `budget` | float | Khong | Ngan sach campaign (VND) | `50000000` |
| `startAt` | string (ISO 8601) | Khong* | Ngay bat dau | `"2025-04-01T00:00:00Z"` |
| `endAt` | string (ISO 8601) | Khong* | Ngay ket thuc | `"2025-06-30T23:59:59Z"` |
| `weights` | object | Khong | Trong so chm diem (phai tong = 100) | xem ben duoi |
| `weights.category` | float | Khong | Trong so category (0-100) | `40` |
| `weights.tier` | float | Khong | Trong so tier (0-100) | `30` |
| `weights.engagement` | float | Khong | Trong so engagement (0-100) | `30` |

> **Luu y:**
> - Neu truyen `startAt` thi phai truyen `endAt` va nguoc lai.
> - `endAt` phai sau `startAt`.
> - Neu truyen `weights`, tong `category + tier + engagement` phai bang **100** (server tu chuyen ve phan so 0-1 khi luu).
> - `minEngagement` phai trong khoang 0-100.

### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/campaigns" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "T-Fluencers Q2 2025",
    "desc": "Thay thach T-Fluencers quy 2 nam 2025",
    "categories": ["cat_lifestyle", "cat_finance"],
    "budgetTiers": ["nano", "micro"],
    "minEngagement": 2.5,
    "budget": 50000000,
    "startAt": "2025-04-01T00:00:00Z",
    "endAt": "2025-06-30T23:59:59Z",
    "weights": {
      "category": 40,
      "tier": 30,
      "engagement": 30
    }
  }'
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "664a1f2e3c4b5d6e7f8a9b0c",
    "partner": "660a1b2c3d4e5f6a7b8c9d0e",
    "name": "T-Fluencers Q2 2025",
    "desc": "Thay thach T-Fluencers quy 2 nam 2025",
    "status": "draft",
    "categories": ["cat_lifestyle", "cat_finance"],
    "budgetTiers": ["nano", "micro"],
    "minEngagement": 2.5,
    "budget": 50000000,
    "startAt": "2025-04-01T00:00:00Z",
    "endAt": "2025-06-30T23:59:59Z",
    "weights": {
      "category": 0.4,
      "tier": 0.3,
      "engagement": 0.3
    },
    "selectedInfluencers": [],
    "matchingCount": 0,
    "createdBy": "661b2c3d4e5f6a7b8c9d0e1f",
    "createdAt": "2025-03-20T08:00:00Z",
    "updatedAt": "2025-03-20T08:00:00Z"
  }
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| Khong truyen `name` | `400` | `{"code": 400, "message": "name: cannot be blank"}` |
| `weights` tong != 100 | `400` | `{"code": 400, "message": "bad request"}` |
| `minEngagement` > 100 | `400` | `{"code": 400, "message": "bad request"}` |
| `endAt` truoc `startAt` | `400` | `{"code": 400, "message": "invalid end date"}` |
| Truyen `startAt` ma khong co `endAt` | `400` | `{"code": 400, "message": "invalid end date"}` |
| Khong co token | `401` | `{"code": 401, "message": "Unauthorized"}` |
| Khong du quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 2. GetList - Lay danh sach Campaign

**Quyen:** `IsCampaginOwner`
**Endpoint:** `GET /campaigns`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `page` | int | Khong | So trang (0-based, mac dinh: 0) | `0` |
| `limit` | int | Khong | So ban ghi moi trang (mac dinh: 20) | `20` |
| `keyword` | string | Khong | Tim kiem theo ten campaign | `"T-Fluencers"` |
| `status` | string | Khong | Loc theo trang thai | `draft` / `active` / `paused` / `completed` / `archived` |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/campaigns?page=0&limit=20&keyword=T-Fluencers&status=active" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "list": [
      {
        "_id": "664a1f2e3c4b5d6e7f8a9b0c",
        "partner": "660a1b2c3d4e5f6a7b8c9d0e",
        "name": "T-Fluencers Q2 2025",
        "desc": "Thay thach T-Fluencers quy 2 nam 2025",
        "status": "active",
        "categories": ["cat_lifestyle", "cat_finance"],
        "budgetTiers": ["nano", "micro"],
        "minEngagement": 2.5,
        "budget": 50000000,
        "startAt": "2025-04-01T00:00:00Z",
        "endAt": "2025-06-30T23:59:59Z",
        "weights": {
          "category": 0.4,
          "tier": 0.3,
          "engagement": 0.3
        },
        "selectedInfluencers": [],
        "matchingCount": 3,
        "lastMatchedAt": "2025-04-10T10:00:00Z",
        "createdBy": "661b2c3d4e5f6a7b8c9d0e1f",
        "createdAt": "2025-03-20T08:00:00Z",
        "updatedAt": "2025-04-10T10:00:00Z"
      }
    ],
    "total": 1
  }
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| Khong co token | `401` | `{"code": 401, "message": "Unauthorized"}` |
| Khong du quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 3. GetDetail - Lay chi tiet Campaign

**Quyen:** `IsCampaginOwner`
**Endpoint:** `GET /campaigns/:id`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

### Path Params

| Param | Mo ta |
|---|---|
| `id` | MongoDB ObjectID cua Campaign (`{{CAMPAIGN_ID}}`) |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/campaigns/{{CAMPAIGN_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "664a1f2e3c4b5d6e7f8a9b0c",
    "partner": "660a1b2c3d4e5f6a7b8c9d0e",
    "name": "T-Fluencers Q2 2025",
    "desc": "Thay thach T-Fluencers quy 2 nam 2025",
    "status": "active",
    "categories": ["cat_lifestyle", "cat_finance"],
    "budgetTiers": ["nano", "micro"],
    "minEngagement": 2.5,
    "budget": 50000000,
    "startAt": "2025-04-01T00:00:00Z",
    "endAt": "2025-06-30T23:59:59Z",
    "weights": {
      "category": 0.4,
      "tier": 0.3,
      "engagement": 0.3
    },
    "selectedInfluencers": [
      {
        "platform": "tiktok",
        "externalId": "tiktok_user_123",
        "name": "Nguyen Van A",
        "score": 85,
        "addedAt": "2025-04-10T10:00:00Z"
      }
    ],
    "matchingCount": 3,
    "lastMatchedAt": "2025-04-10T10:00:00Z",
    "createdBy": "661b2c3d4e5f6a7b8c9d0e1f",
    "createdAt": "2025-03-20T08:00:00Z",
    "updatedAt": "2025-04-10T10:00:00Z"
  }
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| `id` sai format ObjectID | `404` | `{"code": 404, "message": ""}` |
| Campaign khong ton tai | `400` | `{"code": 400, "message": "not found"}` |
| Khong co token | `401` | `{"code": 401, "message": "Unauthorized"}` |
| Khong du quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 4. Update - Cap nhat Campaign

**Quyen:** `IsCampaginOwner`
**Endpoint:** `PUT /campaigns/:id`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

### Path Params

| Param | Mo ta |
|---|---|
| `id` | MongoDB ObjectID cua Campaign (`{{CAMPAIGN_ID}}`) |

### Body (JSON)

Cung cau truc voi [Create](#1-create---tao-campaign). Cac field deu optional ngoai `name`.

| Field | Kieu | Bat buoc | Mo ta |
|---|---|---|---|
| `name` | string | **Co** | Ten campaign |
| `desc` | string | Khong | Mo ta |
| `categories` | string[] | Khong | Danh sach category |
| `budgetTiers` | string[] | Khong | Danh sach budget tier |
| `minEngagement` | float | Khong | Ti le engagement toi thieu (0-100) |
| `budget` | float | Khong | Ngan sach (VND) |
| `startAt` | string | Khong* | Ngay bat dau (ISO 8601) |
| `endAt` | string | Khong* | Ngay ket thuc (ISO 8601) |
| `weights` | object | Khong | Trong so (tong = 100) |

### cURL

```bash
curl -X PUT "{{ADMIN_BASE_URL}}/campaigns/{{CAMPAIGN_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "T-Fluencers Q2 2025 - Updated",
    "desc": "Cap nhat mo ta",
    "minEngagement": 3.0,
    "budget": 60000000,
    "weights": {
      "category": 50,
      "tier": 25,
      "engagement": 25
    }
  }'
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "664a1f2e3c4b5d6e7f8a9b0c",
    "name": "T-Fluencers Q2 2025 - Updated",
    "desc": "Cap nhat mo ta",
    "status": "active",
    "minEngagement": 3.0,
    "budget": 60000000,
    "weights": {
      "category": 0.5,
      "tier": 0.25,
      "engagement": 0.25
    },
    "updatedAt": "2025-03-20T10:00:00Z"
  }
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| `id` sai format ObjectID | `404` | `{"code": 404, "message": ""}` |
| Khong truyen `name` | `400` | `{"code": 400, "message": "name: cannot be blank"}` |
| `weights` tong != 100 | `400` | `{"code": 400, "message": "bad request"}` |
| Khong co token | `401` | `{"code": 401, "message": "Unauthorized"}` |
| Khong du quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 5. ChangeStatus - Doi trang thai Campaign

**Quyen:** `IsCampaginOwner`
**Endpoint:** `PATCH /campaigns/:id/status`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

### Path Params

| Param | Mo ta |
|---|---|
| `id` | MongoDB ObjectID cua Campaign (`{{CAMPAIGN_ID}}`) |

### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Gia tri cho phep |
|---|---|---|---|---|
| `status` | string | **Co** | Trang thai moi | `draft` / `active` / `paused` / `completed` / `archived` |

### cURL

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/campaigns/{{CAMPAIGN_ID}}/status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}'
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "664a1f2e3c4b5d6e7f8a9b0c",
    "status": "active",
    "updatedAt": "2025-03-20T10:30:00Z"
  }
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| `id` sai format ObjectID | `404` | `{"code": 404, "message": ""}` |
| `status` khong hop le | `400` | `{"code": 400, "message": "status invalid"}` |
| Khong truyen `status` | `400` | `{"code": 400, "message": "status invalid"}` |
| Khong co token | `401` | `{"code": 401, "message": "Unauthorized"}` |
| Khong du quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

# PHAN 2: CAMPAIGN MATCHING

---

## 6. RunMatching - Chay Matching

Tinh diem va xep hang influencer cho campaign. Ket qua duoc luu thanh mot Matching Session moi.

**Quyen:** `IsCampaginOwner`
**Endpoint:** `POST /campaigns/:id/matching/run`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

### Path Params

| Param | Mo ta |
|---|---|
| `id` | MongoDB ObjectID cua Campaign (`{{CAMPAIGN_ID}}`) |

### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Rang buoc |
|---|---|---|---|---|
| `influencers` | object[] | **Co** | Danh sach influencer can chay matching | Min 1, max 100 phan tu |
| `influencers[].platform` | string | **Co** | Platform cua influencer | `"tiktok"`, `"youtube"`, `"facebook"` |
| `influencers[].externalId` | string | **Co** | External ID cua influencer tren platform | |

### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/campaigns/{{CAMPAIGN_ID}}/matching/run" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "influencers": [
      {"platform": "tiktok", "externalId": "tiktok_user_123"},
      {"platform": "youtube", "externalId": "yt_channel_abc"},
      {"platform": "facebook", "externalId": "fb_page_xyz"}
    ]
  }'
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "665b2f3e4c5b6d7e8f9a0b1c",
    "campaignId": "664a1f2e3c4b5d6e7f8a9b0c",
    "partner": "660a1b2c3d4e5f6a7b8c9d0e",
    "request": {
      "influencers": [
        {"platform": "tiktok", "externalId": "tiktok_user_123"},
        {"platform": "youtube", "externalId": "yt_channel_abc"},
        {"platform": "facebook", "externalId": "fb_page_xyz"}
      ],
      "criteria": {
        "categories": ["cat_lifestyle", "cat_finance"],
        "budgetTiers": ["nano", "micro"],
        "minEngagement": 2.5
      },
      "weights": {
        "category": 0.4,
        "tier": 0.3,
        "engagement": 0.3
      }
    },
    "results": [
      {
        "platform": "tiktok",
        "externalId": "tiktok_user_123",
        "name": "Nguyen Van A",
        "handle": "@nguyenvana",
        "followersCount": 50000,
        "engagementRate": 4.2,
        "finalScore": 85,
        "suitable": true,
        "breakdown": {
          "category": {"raw": 90, "weight": 0.4, "contribution": 36, "explanation": "Khop 2/2 category"},
          "tier": {"raw": 80, "weight": 0.3, "contribution": 24, "explanation": "Nano tier"},
          "engagement": {"raw": 83, "weight": 0.3, "contribution": 25, "explanation": "4.2% > 2.5% min"}
        }
      }
    ],
    "errors": [],
    "totalRequested": 3,
    "totalScored": 3,
    "totalSuitable": 1,
    "avgScore": 71,
    "latencyMs": 234,
    "createdBy": "661b2c3d4e5f6a7b8c9d0e1f",
    "createdAt": "2025-03-20T10:00:00Z"
  }
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| `influencers` rong | `400` | `{"code": 400, "message": "influencers: cannot be blank"}` |
| `influencers` qua 100 phan tu | `400` | `{"code": 400, "message": "influencers: cannot exceed 100 items per batch"}` |
| Thieu `platform` trong item | `400` | `{"code": 400, "message": "influencers[0].platform: cannot be blank"}` |
| Thieu `externalId` trong item | `400` | `{"code": 400, "message": "influencers[0].externalId: cannot be blank"}` |
| Campaign ID sai format | `404` | `{"code": 404, "message": ""}` |
| Campaign khong ton tai | `400` | `{"code": 400, "message": "not found"}` |
| Khong co token | `401` | `{"code": 401, "message": "Unauthorized"}` |
| Khong du quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 7. GetHistory - Lay lich su Matching

Lay danh sach cac phien matching da chay cho campaign, sap xep moi nhat len dau.

**Quyen:** `IsCampaginOwner`
**Endpoint:** `GET /campaigns/:id/matching/history`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

### Path Params

| Param | Mo ta |
|---|---|
| `id` | MongoDB ObjectID cua Campaign (`{{CAMPAIGN_ID}}`) |

### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `page` | int | Khong | So trang (0-based, mac dinh: 0) | `0` |
| `limit` | int | Khong | So ban ghi moi trang (mac dinh: 20) | `10` |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/campaigns/{{CAMPAIGN_ID}}/matching/history?page=0&limit=10" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "list": [
      {
        "_id": "665b2f3e4c5b6d7e8f9a0b1c",
        "campaignId": "664a1f2e3c4b5d6e7f8a9b0c",
        "totalRequested": 10,
        "totalScored": 10,
        "totalSuitable": 4,
        "avgScore": 67,
        "latencyMs": 312,
        "createdBy": "661b2c3d4e5f6a7b8c9d0e1f",
        "createdAt": "2025-04-10T10:00:00Z"
      },
      {
        "_id": "665b2f3e4c5b6d7e8f9a0b2d",
        "campaignId": "664a1f2e3c4b5d6e7f8a9b0c",
        "totalRequested": 5,
        "totalScored": 5,
        "totalSuitable": 2,
        "avgScore": 72,
        "latencyMs": 198,
        "createdBy": "661b2c3d4e5f6a7b8c9d0e1f",
        "createdAt": "2025-04-08T14:30:00Z"
      }
    ],
    "total": 3
  }
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| Campaign ID sai format | `404` | `{"code": 404, "message": ""}` |
| Khong co token | `401` | `{"code": 401, "message": "Unauthorized"}` |
| Khong du quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 8. GetSession - Lay chi tiet Matching Session

Lay ket qua chi tiet cua mot phien matching cu the.

**Quyen:** `IsCampaginOwner`
**Endpoint:** `GET /campaigns/:id/matching/:sid`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

### Path Params

| Param | Mo ta |
|---|---|
| `id` | MongoDB ObjectID cua Campaign (`{{CAMPAIGN_ID}}`) |
| `sid` | MongoDB ObjectID cua Matching Session (`{{SESSION_ID}}`) |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/campaigns/{{CAMPAIGN_ID}}/matching/{{SESSION_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "665b2f3e4c5b6d7e8f9a0b1c",
    "campaignId": "664a1f2e3c4b5d6e7f8a9b0c",
    "partner": "660a1b2c3d4e5f6a7b8c9d0e",
    "request": {
      "influencers": [
        {"platform": "tiktok", "externalId": "tiktok_user_123"}
      ],
      "criteria": {
        "categories": ["cat_lifestyle"],
        "budgetTiers": ["nano"],
        "minEngagement": 2.5
      },
      "weights": {
        "category": 0.4,
        "tier": 0.3,
        "engagement": 0.3
      }
    },
    "results": [
      {
        "platform": "tiktok",
        "externalId": "tiktok_user_123",
        "name": "Nguyen Van A",
        "handle": "@nguyenvana",
        "followersCount": 50000,
        "engagementRate": 4.2,
        "finalScore": 85,
        "suitable": true,
        "breakdown": {
          "category": {"raw": 90, "weight": 0.4, "contribution": 36, "explanation": "Khop 1/1 category"},
          "tier": {"raw": 80, "weight": 0.3, "contribution": 24, "explanation": "Nano tier"},
          "engagement": {"raw": 83, "weight": 0.3, "contribution": 25, "explanation": "4.2% > 2.5% min"}
        }
      }
    ],
    "errors": [],
    "totalRequested": 1,
    "totalScored": 1,
    "totalSuitable": 1,
    "avgScore": 85,
    "latencyMs": 120,
    "createdBy": "661b2c3d4e5f6a7b8c9d0e1f",
    "createdAt": "2025-04-10T10:00:00Z"
  }
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| Campaign ID sai format | `404` | `{"code": 404, "message": ""}` |
| Session ID sai format | `404` | `{"code": 404, "message": ""}` |
| Session khong ton tai | `400` | `{"code": 400, "message": "not found"}` |
| Khong co token | `401` | `{"code": 401, "message": "Unauthorized"}` |
| Khong du quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 9. AddInfluencer - Them Influencer vao Campaign

Them mot influencer da duoc chon thu cong vao danh sach `selectedInfluencers` cua campaign.

**Quyen:** `IsCampaginOwner`
**Endpoint:** `POST /campaigns/:id/influencers`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

### Path Params

| Param | Mo ta |
|---|---|
| `id` | MongoDB ObjectID cua Campaign (`{{CAMPAIGN_ID}}`) |

### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `platform` | string | **Co** | Platform cua influencer | `"tiktok"` |
| `externalId` | string | **Co** | External ID tren platform | `"tiktok_user_123"` |
| `name` | string | Khong | Ten hien thi cua influencer | `"Nguyen Van A"` |
| `score` | int | Khong | Diem matching (lay tu matching session) | `85` |

### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/campaigns/{{CAMPAIGN_ID}}/influencers" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "tiktok",
    "externalId": "tiktok_user_123",
    "name": "Nguyen Van A",
    "score": 85
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
| Khong truyen `platform` | `400` | `{"code": 400, "message": "platform: cannot be blank"}` |
| Khong truyen `externalId` | `400` | `{"code": 400, "message": "externalId: cannot be blank"}` |
| Campaign ID sai format | `404` | `{"code": 404, "message": ""}` |
| Campaign khong ton tai | `400` | `{"code": 400, "message": "not found"}` |
| Khong co token | `401` | `{"code": 401, "message": "Unauthorized"}` |
| Khong du quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 10. RemoveInfluencer - Xoa Influencer khoi Campaign

Xoa mot influencer khoi danh sach `selectedInfluencers` cua campaign.

**Quyen:** `IsCampaginOwner`
**Endpoint:** `DELETE /campaigns/:id/influencers`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

### Path Params

| Param | Mo ta |
|---|---|
| `id` | MongoDB ObjectID cua Campaign (`{{CAMPAIGN_ID}}`) |

### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `platform` | string | **Co** | Platform cua influencer | `tiktok` |
| `externalId` | string | **Co** | External ID tren platform | `tiktok_user_123` |

### cURL

```bash
curl -X DELETE "{{ADMIN_BASE_URL}}/campaigns/{{CAMPAIGN_ID}}/influencers?platform=tiktok&externalId=tiktok_user_123" \
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
| Khong truyen `platform` | `400` | `{"code": 400, "message": "platform and externalId are required"}` |
| Khong truyen `externalId` | `400` | `{"code": 400, "message": "platform and externalId are required"}` |
| Campaign ID sai format | `404` | `{"code": 404, "message": ""}` |
| Campaign khong ton tai | `400` | `{"code": 400, "message": "not found"}` |
| Khong co token | `401` | `{"code": 401, "message": "Unauthorized"}` |
| Khong du quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

# PHAN 3: BUDGET CAMPAIGNS

Budget Campaign la cau hinh canh bao ngan sach gan voi mot Campaign. He thong se gui thong bao khi chi phi vuot qua nguong `threshold`.

---

## 11. Create - Tao Budget Campaign

**Quyen:** `IsCampaginOwner`
**Endpoint:** `POST /budget-campaigns`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `name` | string | **Co** | Ten budget campaign | `"Alert Q2 2025"` |
| `campaignId` | string | **Co** | ObjectID cua Campaign gan kem | `"664a1f2e3c4b5d6e7f8a9b0c"` |
| `threshold` | float | **Co** | Nguong chi phi canh bao (VND) | `40000000` |
| `staffIds` | string[] | Khong | Danh sach ObjectID staff nhan canh bao | `["661b2c3d4e5f6a7b8c9d0e1f"]` |
| `notificationForEmails` | string[] | Khong | Danh sach email nhan canh bao | `["manager@techcombank.com.vn"]` |

### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/budget-campaigns" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alert Q2 2025",
    "campaignId": "664a1f2e3c4b5d6e7f8a9b0c",
    "threshold": 40000000,
    "staffIds": ["661b2c3d4e5f6a7b8c9d0e1f"],
    "notificationForEmails": ["manager@techcombank.com.vn"]
  }'
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "id": "667c3d4e5d6c7e8f9a0b1c2d",
    "name": "Alert Q2 2025",
    "threshold": 40000000,
    "status": "active",
    "notificationForEmails": ["manager@techcombank.com.vn"],
    "staffIds": ["661b2c3d4e5f6a7b8c9d0e1f"],
    "createdAt": "2025-03-20T08:00:00Z",
    "updatedAt": "2025-03-20T08:00:00Z"
  }
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| Khong truyen `name` | `400` | `{"code": 400, "message": "name: cannot be blank"}` |
| Khong truyen `campaignId` | `400` | `{"code": 400, "message": "campaignId: cannot be blank"}` |
| Khong truyen `threshold` | `400` | `{"code": 400, "message": "threshold: cannot be blank"}` |
| Khong co token | `401` | `{"code": 401, "message": "Unauthorized"}` |
| Khong du quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 12. Update - Cap nhat Budget Campaign

**Quyen:** `IsCampaginOwner`
**Endpoint:** `PUT /budget-campaigns/:id`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

### Path Params

| Param | Mo ta |
|---|---|
| `id` | MongoDB ObjectID cua Budget Campaign (`{{BUDGET_ID}}`) |

### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `name` | string | **Co** | Ten budget campaign | `"Alert Q2 2025 - Updated"` |
| `threshold` | float | **Co** | Nguong chi phi canh bao (VND) | `45000000` |
| `staffIds` | string[] | Khong | Danh sach ObjectID staff nhan canh bao | `["661b2c3d4e5f6a7b8c9d0e1f"]` |
| `notificationForEmails` | string[] | Khong | Danh sach email nhan canh bao | `["team@techcombank.com.vn"]` |

> **Luu y:** `campaignId` khong the thay doi sau khi tao. Chi Update duoc `name`, `threshold`, `staffIds`, `notificationForEmails`.

### cURL

```bash
curl -X PUT "{{ADMIN_BASE_URL}}/budget-campaigns/{{BUDGET_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alert Q2 2025 - Updated",
    "threshold": 45000000,
    "staffIds": ["661b2c3d4e5f6a7b8c9d0e1f"],
    "notificationForEmails": ["team@techcombank.com.vn"]
  }'
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "id": "667c3d4e5d6c7e8f9a0b1c2d",
    "name": "Alert Q2 2025 - Updated",
    "threshold": 45000000,
    "notificationForEmails": ["team@techcombank.com.vn"],
    "staffIds": ["661b2c3d4e5f6a7b8c9d0e1f"],
    "updatedAt": "2025-03-20T11:00:00Z"
  }
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| `id` sai format ObjectID | `404` | `{"code": 404, "message": ""}` |
| Khong truyen `name` | `400` | `{"code": 400, "message": "name: cannot be blank"}` |
| Khong truyen `threshold` | `400` | `{"code": 400, "message": "threshold: cannot be blank"}` |
| Khong co token | `401` | `{"code": 401, "message": "Unauthorized"}` |
| Khong du quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 13. ChangeStatus - Doi trang thai Budget Campaign

**Quyen:** `IsCampaginOwner`
**Endpoint:** `PATCH /budget-campaigns/:id/status`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

### Path Params

| Param | Mo ta |
|---|---|
| `id` | MongoDB ObjectID cua Budget Campaign (`{{BUDGET_ID}}`) |

### Body (JSON)

| Field | Kieu | Bat buoc | Mo ta | Gia tri cho phep |
|---|---|---|---|---|
| `status` | string | **Co** | Trang thai moi | `active` / `inactive` |

### cURL

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/budget-campaigns/{{BUDGET_ID}}/status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"status": "inactive"}'
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "id": "667c3d4e5d6c7e8f9a0b1c2d",
    "status": "inactive",
    "updatedAt": "2025-03-20T12:00:00Z"
  }
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| `id` sai format ObjectID | `404` | `{"code": 404, "message": ""}` |
| `status` khong hop le | `400` | `{"code": 400, "message": "status invalid"}` |
| Khong truyen `status` | `400` | `{"code": 400, "message": "status is required"}` |
| Khong co token | `401` | `{"code": 401, "message": "Unauthorized"}` |
| Khong du quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 14. GetList - Lay danh sach Budget Campaign

**Quyen:** `IsCampaginOwner`
**Endpoint:** `GET /budget-campaigns`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `page` | int | Khong | So trang (0-based, min: 0, mac dinh: 0) | `0` |
| `limit` | int | Khong | So ban ghi moi trang (min: 0, mac dinh: 20) | `20` |
| `keyword` | string | Khong | Tim kiem theo ten | `"Alert Q2"` |
| `event` | string | Khong | Loc theo event ID | `"663a1f2e3c4b5d6e7f8a9b0a"` |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/budget-campaigns?page=0&limit=20&keyword=Alert" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "list": [
      {
        "id": "667c3d4e5d6c7e8f9a0b1c2d",
        "name": "Alert Q2 2025",
        "threshold": 40000000,
        "status": "active",
        "notificationForEmails": ["manager@techcombank.com.vn"],
        "staffIds": ["661b2c3d4e5f6a7b8c9d0e1f"],
        "createdAt": "2025-03-20T08:00:00Z",
        "updatedAt": "2025-03-20T08:00:00Z"
      }
    ],
    "total": 1
  }
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| `page` < 0 | `400` | `{"code": 400, "message": "page invalid"}` |
| `limit` < 0 | `400` | `{"code": 400, "message": "limit invalid"}` |
| Khong co token | `401` | `{"code": 401, "message": "Unauthorized"}` |
| Khong du quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## 15. GetDetail - Lay chi tiet Budget Campaign

**Quyen:** `IsCampaginOwner`
**Endpoint:** `GET /budget-campaigns/:id`

### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

### Path Params

| Param | Mo ta |
|---|---|
| `id` | MongoDB ObjectID cua Budget Campaign (`{{BUDGET_ID}}`) |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/budget-campaigns/{{BUDGET_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "id": "667c3d4e5d6c7e8f9a0b1c2d",
    "name": "Alert Q2 2025",
    "searchString": "alert q2 2025",
    "threshold": 40000000,
    "status": "active",
    "notificationForEmails": ["manager@techcombank.com.vn"],
    "staffIds": ["661b2c3d4e5f6a7b8c9d0e1f"],
    "completedAt": null,
    "createdAt": "2025-03-20T08:00:00Z",
    "updatedAt": "2025-03-20T08:00:00Z"
  }
}
```

### Test loi

| Truong hop | Status | Response |
|---|---|---|
| `id` sai format ObjectID | `404` | `{"code": 404, "message": ""}` |
| Budget Campaign khong ton tai | `400` | `{"code": 400, "message": "not found"}` |
| Khong co token | `401` | `{"code": 401, "message": "Unauthorized"}` |
| Khong du quyen | `403` | `{"code": 403, "message": "Forbidden"}` |

---

## Tong hop endpoints

| # | Method | Endpoint | Handler | Mo ta |
|---|---|---|---|---|
| 1 | `POST` | `/campaigns` | Create | Tao campaign moi |
| 2 | `GET` | `/campaigns` | GetList | Lay danh sach campaign |
| 3 | `GET` | `/campaigns/:id` | GetDetail | Lay chi tiet campaign |
| 4 | `PUT` | `/campaigns/:id` | Update | Cap nhat campaign |
| 5 | `PATCH` | `/campaigns/:id/status` | ChangeStatus | Doi trang thai campaign |
| 6 | `POST` | `/campaigns/:id/matching/run` | RunMatching | Chay matching influencer |
| 7 | `GET` | `/campaigns/:id/matching/history` | GetHistory | Lich su cac lan matching |
| 8 | `GET` | `/campaigns/:id/matching/:sid` | GetSession | Chi tiet mot phien matching |
| 9 | `POST` | `/campaigns/:id/influencers` | AddInfluencer | Them influencer vao campaign |
| 10 | `DELETE` | `/campaigns/:id/influencers` | RemoveInfluencer | Xoa influencer khoi campaign |
| 11 | `POST` | `/budget-campaigns` | Create | Tao budget campaign |
| 12 | `PUT` | `/budget-campaigns/:id` | Update | Cap nhat budget campaign |
| 13 | `PATCH` | `/budget-campaigns/:id/status` | ChangeStatus | Doi trang thai budget campaign |
| 14 | `GET` | `/budget-campaigns` | GetList | Lay danh sach budget campaign |
| 15 | `GET` | `/budget-campaigns/:id` | GetDetail | Lay chi tiet budget campaign |

**Tong: 15 endpoints** | **Quyen: IsCampaginOwner (tat ca)**
