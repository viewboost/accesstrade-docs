# Events API - Admin

Tai lieu nay bao gom 4 nhom endpoint:
- **Events** - Quan ly thu thach (IsCampaginOwner / IsAdmin / IsRoot)
- **Event Schemas** - Cau hinh schema thu thach (IsCampaginOwner)
- **Event Bonus** - Thuong thu thach (RequiredLogin)
- **Event Categories** - Danh muc thu thach (IsCampaginOwner)

**Tong so endpoint: 26**

---

## Bien mau (Variables)

| Bien | Vi du |
|------|-------|
| `{{ADMIN_BASE_URL}}` | `https://admin-api.viewboost.vn` |
| `{{ADMIN_TOKEN}}` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `{{EVENT_ID}}` | `6507a1b2c3d4e5f6a7b8c9d0` |
| `{{SCHEMA_ID}}` | `6507a1b2c3d4e5f6a7b8c9d1` |
| `{{BONUS_ID}}` | `6507a1b2c3d4e5f6a7b8c9d2` |
| `{{CATEGORY_ID}}` | `6507a1b2c3d4e5f6a7b8c9d3` |

---

## Kieu du lieu chung

### FilePhoto object
```json
{
  "_id": "6507a1b2c3d4e5f6a7b8c900",
  "name": "cover_tet2024.jpg",
  "dimensions": {
    "sm": { "width": 375, "height": 130, "url": "https://cdn.viewboost.vn/sm_cover_tet2024.jpg" },
    "md": { "width": 750, "height": 250, "url": "https://cdn.viewboost.vn/md_cover_tet2024.jpg" }
  }
}
```

### FilePhotoWithPlatform object
```json
{
  "platform": "mobile",
  "photos": [],
  "default": { "_id": "6507a1b2c3d4e5f6a7b8c900", "name": "cover_tet2024.jpg", "dimensions": { "sm": {...}, "md": {...} } },
  "stretch": null
}
```

### Cac gia tri hop le

| Truong | Gia tri |
|--------|---------|
| `type` (Event) | `view_boost`, `tracking_campaign` |
| `status` | `active`, `inactive` |
| `type` (EventSchema) | `by-statistic`, `by-content-milestone`, `by-view-milestone` |
| `applyForSources` | `tiktok`, `youtube`, `youtube_shorts`, `facebook`, `facebook_reels`, `instagram`, `instagram_reels`, `threads`, `shopee` |
| `platform` (cover/tag) | `web`, `mobile`, `desktop` |
| status (EventBonus) | `pending`, `approved`, `rejected`, `completed` |

---

# EVENTS

## 1. Tao thu thach

**Quyen:** `IsCampaginOwner`
**Endpoint:** `POST /events`

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |
| `Content-Type` | `application/json` | Co |

### Body mau

```json
{
  "name": "Thu thach T-Fluencers Tet 2024",
  "code": "tfluencers-tet-2024",
  "type": "view_boost",
  "desc": "Tham gia thu thach chia se noi dung don Tet 2024 cung Techcombank va nhan thuong hap dan.",
  "guide": "6507a1b2c3d4e5f6a7b8c901",
  "privacy": "6507a1b2c3d4e5f6a7b8c902",
  "partner": "6507a1b2c3d4e5f6a7b8c903",
  "startAt": "2024-01-01T00:00:00Z",
  "endAt": "2024-02-15T23:59:59Z",
  "displayStartAt": "2023-12-25T00:00:00Z",
  "displayEndAt": "2024-02-15T23:59:59Z",
  "budget": 500000000,
  "reward": "Len den 5 trieu dong",
  "hashtag": "#TFluencersTet2024",
  "order": 1,
  "covers": [
    {
      "platform": "mobile",
      "photos": [],
      "default": {
        "_id": "6507a1b2c3d4e5f6a7b8c900",
        "name": "cover_tet2024_mobile.jpg",
        "dimensions": {
          "sm": { "width": 375, "height": 130, "url": "" },
          "md": { "width": 750, "height": 250, "url": "" }
        }
      }
    }
  ],
  "tags": [
    {
      "platform": "web",
      "photos": [],
      "default": {
        "_id": "6507a1b2c3d4e5f6a7b8c904",
        "name": "tag_tet2024.jpg",
        "dimensions": {
          "sm": { "width": 200, "height": 60, "url": "" },
          "md": { "width": 400, "height": 120, "url": "" }
        }
      }
    }
  ],
  "icon": {
    "_id": "6507a1b2c3d4e5f6a7b8c905",
    "name": "icon_tet2024.png",
    "dimensions": {
      "sm": { "width": 64, "height": 64, "url": "" },
      "md": { "width": 128, "height": 128, "url": "" }
    }
  },
  "options": {
    "maxContentPerDay": 3,
    "applyForSources": ["tiktok", "youtube", "instagram_reels"],
    "hashtags": [],
    "applyForStaff": false,
    "staffCodes": []
  },
  "autoRejectConditions": [
    {
      "view": 500,
      "comment": 0,
      "like": 0,
      "engagement": 0,
      "contentAge": 7,
      "applyForSources": ["tiktok"],
      "message": "Video Tiktok can dat toi thieu 500 luot xem va khong qua 7 ngay tuoi."
    }
  ],
  "videos": [],
  "criteriaContent": [
    "Video phai co hashtag #TFluencersTet2024",
    "Noi dung lien quan den Tet va Techcombank",
    "Khong vi pham ban quyen am nhac"
  ],
  "categories": ["6507a1b2c3d4e5f6a7b8c9d3"]
}
```

**Luu y validation:**
- `name`: bat buoc
- `code`: bat buoc, chi chua chu cai va so (`[a-zA-Z0-9_-]`)
- `type`: phai la `view_boost` hoac `tracking_campaign`
- `startAt` / `endAt`: neu co mot truong thi phai co ca hai
- `displayStartAt` / `displayEndAt`: tuong tu cap tren
- `reward`: toi da 20 ky tu
- `videos`: toi da 3 video
- `categories`: mang cac MongoID hop le

### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/events" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Thu thach T-Fluencers Tet 2024",
    "code": "tfluencers-tet-2024",
    "type": "view_boost",
    "desc": "Tham gia thu thach chia se noi dung don Tet 2024.",
    "partner": "6507a1b2c3d4e5f6a7b8c903",
    "startAt": "2024-01-01T00:00:00Z",
    "endAt": "2024-02-15T23:59:59Z",
    "budget": 500000000,
    "reward": "Len den 5 trieu dong",
    "order": 1,
    "options": {
      "maxContentPerDay": 3,
      "applyForSources": ["tiktok", "youtube", "instagram_reels"]
    },
    "categories": ["6507a1b2c3d4e5f6a7b8c9d3"]
  }'
```

### Response mau (200)

```json
{
  "data": {
    "_id": "6507a1b2c3d4e5f6a7b8c9d0",
    "type": "view_boost",
    "partner": "6507a1b2c3d4e5f6a7b8c903",
    "categories": ["6507a1b2c3d4e5f6a7b8c9d3"],
    "covers": [],
    "tags": [],
    "name": "Thu thach T-Fluencers Tet 2024",
    "code": "tfluencers-tet-2024",
    "slug": "tfluencers-tet-2024",
    "desc": "Tham gia thu thach chia se noi dung don Tet 2024.",
    "order": 1,
    "startAt": "2024-01-01T00:00:00Z",
    "endAt": "2024-02-15T23:59:59Z",
    "budget": 500000000,
    "reward": "Len den 5 trieu dong",
    "status": "inactive",
    "options": {
      "maxContentPerDay": 3,
      "applyForSources": ["tiktok", "youtube", "instagram_reels"]
    },
    "autoRejectConditions": [],
    "statistic": {
      "totalCash": 0,
      "totalCashWaiting": 0,
      "totalCashPending": 0,
      "totalCashCompleted": 0,
      "totalCashRejected": 0,
      "totalCashTransferred": 0,
      "totalCashCashback": 0
    },
    "createdAt": "2024-01-01T08:00:00Z",
    "updatedAt": "2024-01-01T08:00:00Z"
  },
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| Thieu `name` | `name: ""` | 400 | "name is required" |
| Thieu `code` | `code: ""` | 400 | "code is required" |
| `code` chua ky tu dac biet | `code: "tet 2024!"` | 400 | "slug must be character and number" |
| `type` khong hop le | `type: "invalid"` | 400 | "type invalid" |
| `startAt` co ma thieu `endAt` | `startAt: "..."`, `endAt: ""` | 400 | "endAt is invalid" |
| `reward` > 20 ky tu | `reward: "Thuong rat nhieu tien qua"` | 400 | "reward exceed character" |
| Token sai / het han | - | 401 | "unauthorized" |
| Khong du quyen | Token CampaignOwner | 403 | "forbidden" |

---

## 2. Cap nhat thu thach

**Quyen:** `IsCampaginOwner`
**Endpoint:** `PUT /events/:id`

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |
| `Content-Type` | `application/json` | Co |

### Path Params

| Param | Kieu | Mo ta |
|-------|------|-------|
| `id` | string (ObjectID) | ID cua thu thach |

### Body mau

Body giong `POST /events` (EventUpsertBody). Chi can gui cac truong muon cap nhat:

```json
{
  "name": "Thu thach T-Fluencers Tet 2024 (Cap nhat)",
  "code": "tfluencers-tet-2024",
  "type": "view_boost",
  "desc": "Mo ta da duoc cap nhat.",
  "partner": "6507a1b2c3d4e5f6a7b8c903",
  "startAt": "2024-01-01T00:00:00Z",
  "endAt": "2024-02-20T23:59:59Z",
  "budget": 600000000,
  "reward": "Len den 6 trieu",
  "order": 1,
  "options": {
    "maxContentPerDay": 5,
    "applyForSources": ["tiktok", "youtube", "facebook_reels", "instagram_reels"]
  },
  "categories": ["6507a1b2c3d4e5f6a7b8c9d3"]
}
```

### cURL

```bash
curl -X PUT "{{ADMIN_BASE_URL}}/events/{{EVENT_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Thu thach T-Fluencers Tet 2024 (Cap nhat)",
    "code": "tfluencers-tet-2024",
    "type": "view_boost",
    "partner": "6507a1b2c3d4e5f6a7b8c903",
    "startAt": "2024-01-01T00:00:00Z",
    "endAt": "2024-02-20T23:59:59Z",
    "budget": 600000000,
    "reward": "Len den 6 trieu",
    "order": 1,
    "options": {
      "maxContentPerDay": 5,
      "applyForSources": ["tiktok", "youtube", "facebook_reels"]
    },
    "categories": ["6507a1b2c3d4e5f6a7b8c9d3"]
  }'
```

### Response mau (200)

```json
{
  "data": {
    "_id": "6507a1b2c3d4e5f6a7b8c9d0",
    "name": "Thu thach T-Fluencers Tet 2024 (Cap nhat)",
    "code": "tfluencers-tet-2024",
    "type": "view_boost",
    "endAt": "2024-02-20T23:59:59Z",
    "budget": 600000000,
    "status": "active",
    "updatedAt": "2024-01-05T10:30:00Z"
  },
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| `id` sai dinh dang | `/events/invalid-id` | 404 | "not found" |
| `reward` > 20 ky tu | `reward: "Thuong rat nhieu tien that su"` | 400 | "reward exceed character" |
| Token thieu | - | 401 | "unauthorized" |

---

## 3. Doi trang thai thu thach

**Quyen:** `IsCampaginOwner`
**Endpoint:** `PATCH /events/:id/status`

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |
| `Content-Type` | `application/json` | Co |

### Path Params

| Param | Kieu | Mo ta |
|-------|------|-------|
| `id` | string (ObjectID) | ID cua thu thach |

### Body mau

```json
{
  "status": "active"
}
```

### cURL

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/events/{{EVENT_ID}}/status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}'
```

### Response mau (200)

```json
{
  "data": {
    "_id": "6507a1b2c3d4e5f6a7b8c9d0",
    "status": "active",
    "updatedAt": "2024-01-05T10:30:00Z"
  },
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| `status` trong | `status: ""` | 400 | "status is invalid" |
| `status` khong hop le | `status: "deleted"` | 400 | "status is invalid" |
| `id` khong ton tai | ID la ObjectID hop le nhung khong tim thay | 400 | "not found" |
| Token thieu | - | 401 | "unauthorized" |

---

## 4. Lay chi tiet thu thach

**Quyen:** `IsCampaginOwner`
**Endpoint:** `GET /events/:id`

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |

### Path Params

| Param | Kieu | Mo ta |
|-------|------|-------|
| `id` | string (ObjectID) | ID cua thu thach |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/events/{{EVENT_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200)

```json
{
  "data": {
    "_id": "6507a1b2c3d4e5f6a7b8c9d0",
    "type": "view_boost",
    "partner": "6507a1b2c3d4e5f6a7b8c903",
    "categories": ["6507a1b2c3d4e5f6a7b8c9d3"],
    "covers": [
      {
        "platform": "mobile",
        "photos": [],
        "default": {
          "_id": "6507a1b2c3d4e5f6a7b8c900",
          "name": "cover_tet2024_mobile.jpg",
          "dimensions": {
            "sm": { "width": 375, "height": 130, "url": "https://cdn.viewboost.vn/sm_cover_tet2024_mobile.jpg" },
            "md": { "width": 750, "height": 250, "url": "https://cdn.viewboost.vn/md_cover_tet2024_mobile.jpg" }
          }
        }
      }
    ],
    "tags": [],
    "name": "Thu thach T-Fluencers Tet 2024",
    "code": "tfluencers-tet-2024",
    "slug": "tfluencers-tet-2024",
    "desc": "Tham gia thu thach chia se noi dung don Tet 2024.",
    "order": 1,
    "startAt": "2024-01-01T00:00:00Z",
    "endAt": "2024-02-15T23:59:59Z",
    "displayStartAt": "2023-12-25T00:00:00Z",
    "displayEndAt": "2024-02-15T23:59:59Z",
    "budget": 500000000,
    "reward": "Len den 5 trieu dong",
    "hashtag": "#TFluencersTet2024",
    "status": "active",
    "isBlockSubmitContent": false,
    "isBlockReward": false,
    "isApplyForAll": false,
    "options": {
      "maxContentPerDay": 3,
      "applyForSources": ["tiktok", "youtube", "instagram_reels"],
      "hashtags": [],
      "applyForStaff": false,
      "staffCodes": []
    },
    "autoRejectConditions": [
      {
        "view": 500,
        "contentAge": 7,
        "applyForSources": ["tiktok"],
        "message": "Video Tiktok can dat toi thieu 500 luot xem va khong qua 7 ngay tuoi."
      }
    ],
    "videos": [],
    "criteriaContent": [
      "Video phai co hashtag #TFluencersTet2024",
      "Noi dung lien quan den Tet va Techcombank"
    ],
    "statistic": {
      "totalCash": 12500000,
      "totalCashWaiting": 1500000,
      "totalCashPending": 2000000,
      "totalCashCompleted": 9000000,
      "totalCashRejected": 500000,
      "totalCashTransferred": 8000000,
      "totalCashCashback": 0
    },
    "icon": {
      "_id": "6507a1b2c3d4e5f6a7b8c905",
      "name": "icon_tet2024.png",
      "dimensions": {
        "sm": { "width": 64, "height": 64, "url": "https://cdn.viewboost.vn/sm_icon_tet2024.png" },
        "md": { "width": 128, "height": 128, "url": "https://cdn.viewboost.vn/md_icon_tet2024.png" }
      }
    },
    "createdAt": "2024-01-01T08:00:00Z",
    "updatedAt": "2024-01-05T10:30:00Z"
  },
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| `id` sai dinh dang | `/events/abc` | 404 | "not found" |
| Token thieu | - | 401 | "unauthorized" |

---

## 5. Lay danh sach thu thach

**Quyen:** `IsCampaginOwner`
**Endpoint:** `GET /events`

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |

### Query Params

| Param | Kieu | Bat buoc | Mo ta |
|-------|------|----------|-------|
| `page` | int | Khong | So trang (mac dinh: 1) |
| `limit` | int | Khong | So ban ghi moi trang (mac dinh: 20) |
| `keyword` | string | Khong | Tim kiem theo ten thu thach |
| `status` | string | Khong | `active` / `inactive` |
| `categories` | string | Khong | ID danh muc |
| `partner` | string | Khong | ID partner |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/events?page=1&limit=20&status=active&keyword=Tet" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### cURL (loc theo partner va category)

```bash
curl -X GET "{{ADMIN_BASE_URL}}/events?partner=6507a1b2c3d4e5f6a7b8c903&categories=6507a1b2c3d4e5f6a7b8c9d3&page=1&limit=10" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200)

```json
{
  "data": {
    "list": [
      {
        "_id": "6507a1b2c3d4e5f6a7b8c9d0",
        "name": "Thu thach T-Fluencers Tet 2024",
        "code": "tfluencers-tet-2024",
        "type": "view_boost",
        "status": "active",
        "partner": "6507a1b2c3d4e5f6a7b8c903",
        "categories": ["6507a1b2c3d4e5f6a7b8c9d3"],
        "startAt": "2024-01-01T00:00:00Z",
        "endAt": "2024-02-15T23:59:59Z",
        "budget": 500000000,
        "order": 1,
        "statistic": {
          "totalCash": 12500000,
          "totalCashCompleted": 9000000,
          "totalCashPending": 2000000,
          "totalCashWaiting": 1500000,
          "totalCashRejected": 500000,
          "totalCashTransferred": 8000000,
          "totalCashCashback": 0
        },
        "createdAt": "2024-01-01T08:00:00Z",
        "updatedAt": "2024-01-05T10:30:00Z"
      },
      {
        "_id": "6507a1b2c3d4e5f6a7b8c9e0",
        "name": "Thu thach T-Fluencers He 2024",
        "code": "tfluencers-he-2024",
        "type": "tracking_campaign",
        "status": "inactive",
        "partner": "6507a1b2c3d4e5f6a7b8c903",
        "categories": [],
        "startAt": "2024-06-01T00:00:00Z",
        "endAt": "2024-08-31T23:59:59Z",
        "budget": 300000000,
        "order": 2,
        "createdAt": "2024-05-01T08:00:00Z",
        "updatedAt": "2024-05-01T08:00:00Z"
      }
    ],
    "total": 2
  },
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| Token thieu | - | 401 | "unauthorized" |
| Khong du quyen | Token level thap | 403 | "forbidden" |

---

## 6. Lay thong ke thu thach (Statistic)

**Quyen:** `IsCampaginOwner`
**Endpoint:** `GET /events/statistic`

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |

### Query Params

| Param | Kieu | Bat buoc | Mo ta |
|-------|------|----------|-------|
| `event` | string | Khong | ID cua thu thach |
| `partner` | string | Khong | ID partner |
| `fromAt` | string (ISO date) | Khong | Tu ngay (YYYY-MM-DD) |
| `toAt` | string (ISO date) | Khong | Den ngay (YYYY-MM-DD) |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/events/statistic?event={{EVENT_ID}}&fromAt=2024-01-01&toAt=2024-02-15" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200)

```json
{
  "data": {
    "totalCash": 12500000,
    "totalCashWaiting": 1500000,
    "totalCashPending": 2000000,
    "totalCashCompleted": 9000000,
    "totalCashRejected": 500000,
    "totalCashTransferred": 8000000,
    "totalCashCashback": 0,
    "totalContent": 450,
    "totalInfluencer": 120
  },
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| Token thieu | - | 401 | "unauthorized" |
| `event` ID sai dinh dang | `event=abc` | 400 | "bad request" |

---

## 7. Lay du lieu bieu do thu thach (Chart)

**Quyen:** `IsCampaginOwner`
**Endpoint:** `GET /events/chart`

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |

### Query Params

| Param | Kieu | Bat buoc | Mo ta |
|-------|------|----------|-------|
| `event` | string | Khong | ID cua thu thach |
| `partner` | string | Khong | ID partner |
| `fromAt` | string (ISO date) | Khong | Tu ngay (YYYY-MM-DD) |
| `toAt` | string (ISO date) | Khong | Den ngay (YYYY-MM-DD) |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/events/chart?event={{EVENT_ID}}&fromAt=2024-01-01&toAt=2024-01-31" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200)

```json
{
  "data": [
    {
      "date": "2024-01-01",
      "totalCash": 450000,
      "totalContent": 15,
      "totalInfluencer": 8
    },
    {
      "date": "2024-01-02",
      "totalCash": 680000,
      "totalContent": 22,
      "totalInfluencer": 14
    },
    {
      "date": "2024-01-03",
      "totalCash": 520000,
      "totalContent": 17,
      "totalInfluencer": 10
    }
  ],
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| Token thieu | - | 401 | "unauthorized" |
| `fromAt` > `toAt` | Ngay bat dau sau ngay ket thuc | 400 | "bad request" |

---

## 8. Khoa nguoi dung nop noi dung (Block User Submit Content)

**Quyen:** `IsAdmin`
**Endpoint:** `PATCH /events/:id/block-user-submit-content`

Bat / tat che do khoa tat ca nguoi dung khong the nop noi dung vao thu thach. Thao tac toggle: neu dang mo thi khoa, neu dang khoa thi mo.

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |

### Path Params

| Param | Kieu | Mo ta |
|-------|------|-------|
| `id` | string (ObjectID) | ID cua thu thach |

### cURL

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/events/{{EVENT_ID}}/block-user-submit-content" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200)

```json
{
  "data": {},
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| `id` khong hop le | `/events/invalid/block-user-submit-content` | 404 | "not found" |
| Khong du quyen (CampaignOwner) | Token CampaignOwner | 403 | "forbidden" |
| Token thieu | - | 401 | "unauthorized" |

---

## 9. Khoa tao thuong (Block Create Reward)

**Quyen:** `IsAdmin`
**Endpoint:** `PATCH /events/:id/block-create-reward`

Bat / tat che do khoa viec tao reward cho thu thach. Chay bat dong bo (async) nen response tra ve ngay lap tuc.

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |

### Path Params

| Param | Kieu | Mo ta |
|-------|------|-------|
| `id` | string (ObjectID) | ID cua thu thach |

### cURL

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/events/{{EVENT_ID}}/block-create-reward" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200)

```json
{
  "data": {},
  "code": 200
}
```

**Luu y:** API nay tra ve 200 ngay lap tuc, xu ly thuc su dien ra bat dong bo nen khong co thong bao ket qua cu the trong response.

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| Khong du quyen | Token CampaignOwner | 403 | "forbidden" |
| Token thieu | - | 401 | "unauthorized" |

---

## 10. Lay bao cao thong ke (Report Statistic)

**Quyen:** `IsAdmin`
**Endpoint:** `GET /events/report-statistic`

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |

### Query Params

| Param | Kieu | Bat buoc | Mo ta |
|-------|------|----------|-------|
| `event` | string | Khong | ID cua thu thach |
| `partner` | string | Khong | ID partner |
| `fromAt` | string (ISO date) | Khong | Tu ngay (YYYY-MM-DD) |
| `toAt` | string (ISO date) | Khong | Den ngay (YYYY-MM-DD) |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/events/report-statistic?event={{EVENT_ID}}&fromAt=2024-01-01&toAt=2024-01-31" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200)

```json
{
  "data": {
    "totalCash": 12500000,
    "totalCashWaiting": 1500000,
    "totalCashPending": 2000000,
    "totalCashCompleted": 9000000,
    "totalCashRejected": 500000,
    "totalCashTransferred": 8000000,
    "totalContent": 450,
    "totalInfluencer": 120,
    "byEvent": [
      {
        "eventId": "6507a1b2c3d4e5f6a7b8c9d0",
        "eventName": "Thu thach T-Fluencers Tet 2024",
        "totalCash": 12500000,
        "totalContent": 450,
        "totalInfluencer": 120
      }
    ]
  },
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| Khong du quyen | Token CampaignOwner | 403 | "forbidden" |
| Token thieu | - | 401 | "unauthorized" |

---

## 11. Chay phan tich hang ngay (Run Analytic Daily)

**Quyen:** `IsAdmin`
**Endpoint:** `GET /events/run-analytic-daily`

Kich hoat chay lai job phan tich du lieu hang ngay cho tat ca event dang hoat dong. Chay bat dong bo.

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/events/run-analytic-daily" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200)

```json
{
  "data": {},
  "code": 200
}
```

**Luu y:** API tra ve 200 ngay lap tuc. Job phan tich chay ngam duoi nen.

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| Khong du quyen | Token CampaignOwner | 403 | "forbidden" |
| Token thieu | - | 401 | "unauthorized" |

---

## 12. Tu choi thuong cua thu thach (Reject Event Reward)

**Quyen:** `IsRoot`
**Endpoint:** `POST /events/reject-reward-event`

Tu choi hang loat reward cua nhieu thu thach. Chay bat dong bo.

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |
| `Content-Type` | `application/json` | Co |

### Body mau

```json
{
  "ids": [
    "6507a1b2c3d4e5f6a7b8c9d0",
    "6507a1b2c3d4e5f6a7b8c9e0",
    "6507a1b2c3d4e5f6a7b8c9f0"
  ]
}
```

### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/events/reject-reward-event" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "ids": [
      "6507a1b2c3d4e5f6a7b8c9d0",
      "6507a1b2c3d4e5f6a7b8c9e0"
    ]
  }'
```

### Response mau (200)

```json
{
  "data": {},
  "code": 200
}
```

**Luu y:** API tra ve 200 ngay lap tuc. Xu ly tu choi reward chay ngam duoi nen.

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| Khong du quyen (Admin) | Token Admin (khong phai Root) | 403 | "forbidden" |
| Token thieu | - | 401 | "unauthorized" |

---

## 13. Chay lai thuong theo Content Analytic Daily

**Quyen:** `IsRoot`
**Endpoint:** `GET /events/rerun-reward-event-by-cad`

Chay lai qua trinh tinh thuong dua tren du lieu Content Analytic Daily. Yeu cau them `key` bao mat trong query string. Chay bat dong bo.

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |

### Query Params

| Param | Kieu | Bat buoc | Mo ta |
|-------|------|----------|-------|
| `key` | string | **Co** | Key bao mat dac biet (lien he DevOps) |
| `event` | string | Khong | ID thu thach can chay lai |
| `partner` | string | Khong | ID partner |
| `content` | string | Khong | ID content cu the |
| `fromAt` | string (ISO date) | Khong | Tu ngay |
| `toAt` | string (ISO date) | Khong | Den ngay |
| `limit` | int | Khong | Gioi han so ban ghi xu ly |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/events/rerun-reward-event-by-cad?key=177ac2b7-7bed-43c2-8757-5cff85dd5518&event={{EVENT_ID}}&fromAt=2024-01-01&toAt=2024-01-31" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200)

```json
{
  "data": {},
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| Thieu `key` hoac `key` sai | `key=wrong-key` | 401 | "unauthorized" |
| Khong du quyen (Admin) | Token Admin | 403 | "forbidden" |
| Token thieu | - | 401 | "unauthorized" |

---

# EVENT SCHEMAS

## 14. Tao schema thu thach

**Quyen:** `IsCampaginOwner`
**Endpoint:** `POST /event-schemas`

Schema dinh nghia co che thuong cho tung chu ky / hang muc cua thu thach.

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |
| `Content-Type` | `application/json` | Co |

### Body mau

**Schema loai `by-statistic` (thuong theo luot xem / like / comment):**
```json
{
  "title": "Thuong luot xem Tiktok - Tet 2024",
  "desc": "Moi luot xem hop le tren Tiktok duoc thuong 10 dong.",
  "type": "by-statistic",
  "event": "6507a1b2c3d4e5f6a7b8c9d0",
  "startAt": "2024-01-01T00:00:00Z",
  "endAt": "2024-02-15T23:59:59Z",
  "applyForSources": ["tiktok"],
  "maximumRewardPerUser": 5000000,
  "order": 1,
  "quantity": {
    "isUnlimited": true,
    "total": 0,
    "remaining": 0
  },
  "cashReward": {
    "cashPerView": 0.01,
    "cashPerLike": 0,
    "cashPerComment": 0,
    "cashPerShare": 0,
    "cashMilestone": 0
  },
  "milestone": null
}
```

**Schema loai `by-content-milestone` (thuong khi dat moc so bai dang):**
```json
{
  "title": "Moc 10 bai dang - Tet 2024",
  "desc": "Dat 10 bai dang hop le nhan thuong 200,000 dong.",
  "type": "by-content-milestone",
  "event": "6507a1b2c3d4e5f6a7b8c9d0",
  "startAt": "2024-01-01T00:00:00Z",
  "endAt": "2024-02-15T23:59:59Z",
  "applyForSources": ["tiktok", "youtube", "instagram_reels"],
  "maximumRewardPerUser": 1,
  "order": 2,
  "quantity": {
    "isUnlimited": false,
    "total": 1000,
    "remaining": 1000
  },
  "cashReward": {
    "cashMilestone": 200000
  },
  "milestone": {
    "numberOfContent": 10,
    "numberOfView": 0
  }
}
```

**Schema loai `by-view-milestone` (thuong khi dat moc tong luot xem):**
```json
{
  "title": "Moc 100K view - Tet 2024",
  "desc": "Dat tong cong 100,000 luot xem nhan thuong 500,000 dong.",
  "type": "by-view-milestone",
  "event": "6507a1b2c3d4e5f6a7b8c9d0",
  "startAt": "2024-01-01T00:00:00Z",
  "endAt": "2024-02-15T23:59:59Z",
  "applyForSources": ["tiktok", "youtube"],
  "maximumRewardPerUser": 1,
  "order": 3,
  "quantity": {
    "isUnlimited": true,
    "total": 0,
    "remaining": 0
  },
  "cashReward": {
    "cashMilestone": 500000
  },
  "milestone": {
    "numberOfContent": 0,
    "numberOfView": 100000
  }
}
```

**Luu y validation:**
- `title`: bat buoc
- `type`: bat buoc, phai la `by-statistic`, `by-content-milestone`, hoac `by-view-milestone`
- `applyForSources`: moi phan tu phai la gia tri hop le trong danh sach source
- `startAt` / `endAt`: neu co mot truong thi phai co ca hai

### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/event-schemas" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Thuong luot xem Tiktok - Tet 2024",
    "type": "by-statistic",
    "event": "6507a1b2c3d4e5f6a7b8c9d0",
    "startAt": "2024-01-01T00:00:00Z",
    "endAt": "2024-02-15T23:59:59Z",
    "applyForSources": ["tiktok"],
    "maximumRewardPerUser": 5000000,
    "order": 1,
    "quantity": { "isUnlimited": true, "total": 0, "remaining": 0 },
    "cashReward": { "cashPerView": 0.01 }
  }'
```

### Response mau (200)

```json
{
  "data": {
    "_id": "6507a1b2c3d4e5f6a7b8c9d1",
    "title": "Thuong luot xem Tiktok - Tet 2024",
    "type": "by-statistic",
    "event": "6507a1b2c3d4e5f6a7b8c9d0",
    "status": "inactive",
    "startAt": "2024-01-01T00:00:00Z",
    "endAt": "2024-02-15T23:59:59Z",
    "applyForSources": ["tiktok"],
    "maximumRewardPerUser": 5000000,
    "order": 1,
    "quantity": { "isUnlimited": true, "total": 0, "remaining": 0 },
    "cashReward": { "cashPerView": 0.01 },
    "milestone": null,
    "createdAt": "2024-01-01T08:00:00Z",
    "updatedAt": "2024-01-01T08:00:00Z"
  },
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| Thieu `title` | `title: ""` | 400 | "title is invalid" |
| Thieu `type` | `type: ""` | 400 | "type invalid" |
| `type` khong hop le | `type: "bonus"` | 400 | "type invalid" |
| `applyForSources` chua gia tri sai | `["tiktok", "twitter"]` | 400 | "source invalid" |
| `startAt` co ma thieu `endAt` | `startAt: "2024-01-01"`, `endAt: ""` | 400 | "endAt is invalid" |
| Token thieu | - | 401 | "unauthorized" |

---

## 15. Cap nhat schema thu thach

**Quyen:** `IsCampaginOwner`
**Endpoint:** `PUT /event-schemas/:id`

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |
| `Content-Type` | `application/json` | Co |

### Path Params

| Param | Kieu | Mo ta |
|-------|------|-------|
| `id` | string (ObjectID) | ID cua schema |

### Body mau

```json
{
  "title": "Thuong luot xem Tiktok - Tet 2024 (Cap nhat)",
  "desc": "Moi luot xem hop le tren Tiktok duoc thuong 15 dong.",
  "type": "by-statistic",
  "event": "6507a1b2c3d4e5f6a7b8c9d0",
  "startAt": "2024-01-01T00:00:00Z",
  "endAt": "2024-02-15T23:59:59Z",
  "applyForSources": ["tiktok", "youtube_shorts"],
  "maximumRewardPerUser": 7000000,
  "order": 1,
  "quantity": { "isUnlimited": true, "total": 0, "remaining": 0 },
  "cashReward": { "cashPerView": 0.015 }
}
```

### cURL

```bash
curl -X PUT "{{ADMIN_BASE_URL}}/event-schemas/{{SCHEMA_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Thuong luot xem Tiktok - Tet 2024 (Cap nhat)",
    "type": "by-statistic",
    "event": "6507a1b2c3d4e5f6a7b8c9d0",
    "startAt": "2024-01-01T00:00:00Z",
    "endAt": "2024-02-15T23:59:59Z",
    "applyForSources": ["tiktok", "youtube_shorts"],
    "maximumRewardPerUser": 7000000,
    "order": 1,
    "quantity": { "isUnlimited": true, "total": 0, "remaining": 0 },
    "cashReward": { "cashPerView": 0.015 }
  }'
```

### Response mau (200)

```json
{
  "data": {
    "_id": "6507a1b2c3d4e5f6a7b8c9d1",
    "title": "Thuong luot xem Tiktok - Tet 2024 (Cap nhat)",
    "type": "by-statistic",
    "event": "6507a1b2c3d4e5f6a7b8c9d0",
    "status": "active",
    "applyForSources": ["tiktok", "youtube_shorts"],
    "maximumRewardPerUser": 7000000,
    "cashReward": { "cashPerView": 0.015 },
    "updatedAt": "2024-01-10T09:00:00Z"
  },
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| `id` sai dinh dang | `/event-schemas/bad-id` | 404 | "not found" |
| Thieu `title` | `title: ""` | 400 | "title is invalid" |
| Token thieu | - | 401 | "unauthorized" |

---

## 16. Doi trang thai schema

**Quyen:** `IsCampaginOwner`
**Endpoint:** `PATCH /event-schemas/:id/status`

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |
| `Content-Type` | `application/json` | Co |

### Path Params

| Param | Kieu | Mo ta |
|-------|------|-------|
| `id` | string (ObjectID) | ID cua schema |

### Body mau

```json
{
  "status": "active"
}
```

### cURL

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/event-schemas/{{SCHEMA_ID}}/status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}'
```

### Response mau (200)

```json
{
  "data": {
    "_id": "6507a1b2c3d4e5f6a7b8c9d1",
    "status": "active",
    "updatedAt": "2024-01-10T09:00:00Z"
  },
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| `status` trong | `status: ""` | 400 | "status is invalid" |
| `status` khong hop le | `status: "paused"` | 400 | "status is invalid" |
| `id` khong ton tai | ID hop le nhung khong tim thay | 400 | "not found" |
| Token thieu | - | 401 | "unauthorized" |

---

## 17. Lay danh sach schema

**Quyen:** `IsCampaginOwner`
**Endpoint:** `GET /event-schemas`

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |

### Query Params

| Param | Kieu | Bat buoc | Mo ta |
|-------|------|----------|-------|
| `page` | int | Khong | So trang (mac dinh: 1) |
| `limit` | int | Khong | So ban ghi moi trang |
| `keyword` | string | Khong | Tim kiem theo ten schema |
| `status` | string | Khong | `active` / `inactive` |
| `event` | string | Khong | Loc theo ID thu thach |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/event-schemas?event={{EVENT_ID}}&status=active&page=1&limit=20" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200)

```json
{
  "data": {
    "list": [
      {
        "_id": "6507a1b2c3d4e5f6a7b8c9d1",
        "title": "Thuong luot xem Tiktok - Tet 2024",
        "type": "by-statistic",
        "event": "6507a1b2c3d4e5f6a7b8c9d0",
        "status": "active",
        "startAt": "2024-01-01T00:00:00Z",
        "endAt": "2024-02-15T23:59:59Z",
        "applyForSources": ["tiktok"],
        "maximumRewardPerUser": 5000000,
        "order": 1,
        "quantity": { "isUnlimited": true, "total": 0, "remaining": 0 },
        "cashReward": { "cashPerView": 0.01 },
        "createdAt": "2024-01-01T08:00:00Z"
      },
      {
        "_id": "6507a1b2c3d4e5f6a7b8c9d4",
        "title": "Moc 10 bai dang - Tet 2024",
        "type": "by-content-milestone",
        "event": "6507a1b2c3d4e5f6a7b8c9d0",
        "status": "active",
        "startAt": "2024-01-01T00:00:00Z",
        "endAt": "2024-02-15T23:59:59Z",
        "applyForSources": ["tiktok", "youtube", "instagram_reels"],
        "maximumRewardPerUser": 1,
        "order": 2,
        "quantity": { "isUnlimited": false, "total": 1000, "remaining": 856 },
        "cashReward": { "cashMilestone": 200000 },
        "milestone": { "numberOfContent": 10, "numberOfView": 0 },
        "createdAt": "2024-01-01T08:05:00Z"
      }
    ],
    "total": 2
  },
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| Token thieu | - | 401 | "unauthorized" |

---

# EVENT BONUS

## 18. Lay danh sach bonus

**Quyen:** `RequiredLogin`
**Endpoint:** `GET /event-bonus`

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |

### Query Params

| Param | Kieu | Bat buoc | Mo ta |
|-------|------|----------|-------|
| `page` | int | Khong | So trang (mac dinh: 1) |
| `limit` | int | Khong | So ban ghi moi trang |
| `status` | string | Khong | `pending` / `approved` / `rejected` / `completed` |
| `event` | string | Khong | ID thu thach |
| `user` | string | Khong | ID nguoi dung |
| `partner` | string | Khong | ID partner |
| `reconciliation` | string | Khong | ID doi soat |
| `createdBy` | string | Khong | ID staff tao bonus |
| `fromAt` | string (ISO date) | Khong | Tu ngay tao |
| `toAt` | string (ISO date) | Khong | Den ngay tao |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/event-bonus?event={{EVENT_ID}}&status=pending&page=1&limit=20" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### cURL (loc theo ngay va partner)

```bash
curl -X GET "{{ADMIN_BASE_URL}}/event-bonus?partner=6507a1b2c3d4e5f6a7b8c903&fromAt=2024-01-01&toAt=2024-01-31&status=approved" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200)

```json
{
  "data": {
    "list": [
      {
        "_id": "6507a1b2c3d4e5f6a7b8c9d2",
        "event": "6507a1b2c3d4e5f6a7b8c9d0",
        "user": "6507a1b2c3d4e5f6a7b8c910",
        "partner": "6507a1b2c3d4e5f6a7b8c903",
        "toAt": "2024-03-31T23:59:59Z",
        "amount": 500000,
        "status": "pending",
        "note": "Bonus dac biet cho top Influencer Tet 2024",
        "createdBy": "6507a1b2c3d4e5f6a7b8c920",
        "isTransfer": false,
        "createdAt": "2024-01-15T10:00:00Z",
        "updatedAt": "2024-01-15T10:00:00Z"
      },
      {
        "_id": "6507a1b2c3d4e5f6a7b8c9d5",
        "event": "6507a1b2c3d4e5f6a7b8c9d0",
        "user": "6507a1b2c3d4e5f6a7b8c911",
        "partner": "6507a1b2c3d4e5f6a7b8c903",
        "toAt": "2024-04-30T23:59:59Z",
        "amount": 1000000,
        "status": "approved",
        "note": "Bonus hang thang thang 1/2024",
        "reconciliation": "6507a1b2c3d4e5f6a7b8c930",
        "createdBy": "6507a1b2c3d4e5f6a7b8c920",
        "isTransfer": false,
        "createdAt": "2024-01-20T14:30:00Z",
        "updatedAt": "2024-01-22T09:00:00Z"
      }
    ],
    "total": 2
  },
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| Token thieu | - | 401 | "unauthorized" |
| `status` khong hop le | `status=cancelled` | 400 | "status invalid" |

---

## 19. Lay chi tiet bonus

**Quyen:** `RequiredLogin`
**Endpoint:** `GET /event-bonus/:id`

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |

### Path Params

| Param | Kieu | Mo ta |
|-------|------|-------|
| `id` | string (ObjectID) | ID cua bonus |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/event-bonus/{{BONUS_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200)

```json
{
  "data": {
    "_id": "6507a1b2c3d4e5f6a7b8c9d2",
    "event": {
      "_id": "6507a1b2c3d4e5f6a7b8c9d0",
      "name": "Thu thach T-Fluencers Tet 2024",
      "code": "tfluencers-tet-2024"
    },
    "user": {
      "_id": "6507a1b2c3d4e5f6a7b8c910",
      "name": "Nguyen Van A",
      "phone": "0901234567"
    },
    "partner": {
      "_id": "6507a1b2c3d4e5f6a7b8c903",
      "name": "Techcombank"
    },
    "toAt": "2024-03-31T23:59:59Z",
    "amount": 500000,
    "status": "pending",
    "note": "Bonus dac biet cho top Influencer Tet 2024",
    "reason": "",
    "isTransfer": false,
    "createdBy": {
      "_id": "6507a1b2c3d4e5f6a7b8c920",
      "name": "Admin Nguyen"
    },
    "createdAt": "2024-01-15T10:00:00Z",
    "updatedAt": "2024-01-15T10:00:00Z"
  },
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| `id` sai dinh dang | `/event-bonus/abc` | 404 | "not found" |
| Bonus khong ton tai | ID hop le nhung khong ton tai | 400 | "not found" |
| Token thieu | - | 401 | "unauthorized" |

---

## 20. Tao bonus

**Quyen:** `RequiredLogin`
**Endpoint:** `POST /event-bonus`

Tao bonus thu cong cho mot Influencer trong mot thu thach cu the.

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |
| `Content-Type` | `application/json` | Co |

### Body mau

```json
{
  "event": "6507a1b2c3d4e5f6a7b8c9d0",
  "user": "6507a1b2c3d4e5f6a7b8c910",
  "partner": "6507a1b2c3d4e5f6a7b8c903",
  "amount": 500000,
  "toAt": "2024-03-31",
  "note": "Bonus dac biet cho top Influencer Tet 2024 thang 1"
}
```

**Luu y validation:**
- `toAt`: bat buoc, phai la ngay trong tuong lai (ISO date)
- `event`: bat buoc (MongoID)
- `user`: bat buoc (MongoID)
- `partner`: bat buoc (MongoID)
- `amount`: >= 0

### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/event-bonus" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "6507a1b2c3d4e5f6a7b8c9d0",
    "user": "6507a1b2c3d4e5f6a7b8c910",
    "partner": "6507a1b2c3d4e5f6a7b8c903",
    "amount": 500000,
    "toAt": "2024-03-31",
    "note": "Bonus dac biet cho top Influencer Tet 2024"
  }'
```

### Response mau (200)

```json
{
  "data": null,
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| Thieu `toAt` | `toAt: ""` | 400 | "toAt is required" |
| `toAt` la ngay qua khu | `toAt: "2020-01-01"` | 400 | "toAt is invalid" |
| Thieu `event` | `event: ""` | 400 | "event not found" |
| Thieu `user` | `user: ""` | 400 | "user not found" |
| Thieu `partner` | `partner: ""` | 400 | "partner not found" |
| `amount` am | `amount: -100` | 400 | "amount is required" |
| Token thieu | - | 401 | "unauthorized" |

---

## 21. Cap nhat bonus

**Quyen:** `RequiredLogin`
**Endpoint:** `PUT /event-bonus/:id`

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |
| `Content-Type` | `application/json` | Co |

### Path Params

| Param | Kieu | Mo ta |
|-------|------|-------|
| `id` | string (ObjectID) | ID cua bonus |

### Body mau

```json
{
  "toAt": "2024-04-30",
  "amount": 750000,
  "note": "Da cap nhat gia tri bonus sau doi soat lan 2"
}
```

**Luu y validation:**
- `toAt`: bat buoc, phai la ngay trong tuong lai
- `amount`: >= 0

### cURL

```bash
curl -X PUT "{{ADMIN_BASE_URL}}/event-bonus/{{BONUS_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "toAt": "2024-04-30",
    "amount": 750000,
    "note": "Da cap nhat gia tri bonus sau doi soat lan 2"
  }'
```

### Response mau (200)

```json
{
  "data": null,
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| `toAt` la ngay qua khu | `toAt: "2023-12-01"` | 400 | "toAt is invalid" |
| `amount` am | `amount: -500` | 400 | "amount is required" |
| `id` sai dinh dang | `/event-bonus/bad-id` | 404 | "not found" |
| Token thieu | - | 401 | "unauthorized" |

---

## 22. Doi trang thai bonus

**Quyen:** `RequiredLogin`
**Endpoint:** `PATCH /event-bonus/:id/change-status`

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |
| `Content-Type` | `application/json` | Co |

### Path Params

| Param | Kieu | Mo ta |
|-------|------|-------|
| `id` | string (ObjectID) | ID cua bonus |

### Body mau

**Duyet bonus:**
```json
{
  "status": "approved",
  "reason": ""
}
```

**Tu choi bonus:**
```json
{
  "status": "rejected",
  "reason": "Influencer khong du dieu kien theo dieu khoan chuong trinh."
}
```

**Hoan thanh bonus:**
```json
{
  "status": "completed",
  "reason": ""
}
```

**Gia tri `status` hop le:** `pending` | `approved` | `rejected` | `completed`

### cURL (Duyet)

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/event-bonus/{{BONUS_ID}}/change-status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"status": "approved", "reason": ""}'
```

### cURL (Tu choi)

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/event-bonus/{{BONUS_ID}}/change-status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"status": "rejected", "reason": "Influencer khong du dieu kien."}'
```

### Response mau (200)

```json
{
  "data": null,
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| `status` trong | `status: ""` | 400 | "status is required" |
| `status` khong hop le | `status: "cancelled"` | 400 | "status is invalid" |
| `id` sai dinh dang | `/event-bonus/abc/change-status` | 404 | "not found" |
| Token thieu | - | 401 | "unauthorized" |

---

## 23. Import bonus tu file Excel

**Quyen:** `RequiredLogin`
**Endpoint:** `POST /event-bonus/import-excel`

Import hang loat bonus tu file Excel. File phai co dinh dang `.xlsx`.

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |
| `Content-Type` | `multipart/form-data` | Co (tu dong tu cURL) |

### Form Data

| Field | Kieu | Bat buoc | Mo ta |
|-------|------|----------|-------|
| `file` | file (.xlsx) | Co | File Excel chua danh sach bonus |

### Cau truc file Excel

| Cot | So cot | Bat buoc | Mo ta | Vi du |
|-----|--------|----------|-------|-------|
| Event ID | 1 | Co | MongoDB ID cua thu thach | `6507a1b2c3d4e5f6a7b8c9d0` |
| User ID | 2 | Co | MongoDB ID cua nguoi dung | `6507a1b2c3d4e5f6a7b8c910` |
| Amount | 3 | Co | So tien bonus (so) | `500000` |
| Expired At | 4 | Co | Ngay het han bonus (ISO date) | `2024-03-31` |
| Note | 5 | Khong | Ghi chu | `Bonus Tet 2024` |

**Luu y:**
- File bat dau tu dong 1 (khong co header row hoac header o hang dau bi bo qua)
- Cac dong rong se bi bo qua tu dong
- Moi dong phai co day du Event ID, User ID, Amount va Expired At
- `Expired At` phai la ngay trong tuong lai

### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/event-bonus/import-excel" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -F "file=@/path/to/bonus_list_tet2024.xlsx"
```

### Response mau (200)

```json
{
  "data": null,
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| Khong chon file | Khong gui file | 400 | "bad request" |
| File sai dinh dang | `.csv` hoac `.xls` | 400 | "bad request" |
| Dong thieu Event ID | Cot 1 trong | 400 | "event not found" |
| Dong thieu User ID | Cot 2 trong | 400 | "user not found" |
| Dong thieu Amount | Cot 3 trong | 400 | "amount is required" |
| Dong thieu Expired At | Cot 4 trong | 400 | "toAt is required" |
| Token thieu | - | 401 | "unauthorized" |

---

# EVENT CATEGORIES

## 24. Lay danh sach danh muc

**Quyen:** `IsCampaginOwner`
**Endpoint:** `GET /event-categories`

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |

### Query Params

| Param | Kieu | Bat buoc | Mo ta |
|-------|------|----------|-------|
| `page` | int | Khong | So trang (mac dinh: 1) |
| `limit` | int | Khong | So ban ghi moi trang |
| `keyword` | string | Khong | Tim kiem theo ten danh muc |

### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/event-categories?page=1&limit=20" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### cURL (tim kiem)

```bash
curl -X GET "{{ADMIN_BASE_URL}}/event-categories?keyword=Tai+chinh&limit=10" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau (200)

```json
{
  "data": {
    "list": [
      {
        "_id": "6507a1b2c3d4e5f6a7b8c9d3",
        "name": "Tai chinh & Ngan hang",
        "code": "tai-chinh-ngan-hang",
        "partner": "6507a1b2c3d4e5f6a7b8c903",
        "icon": {
          "_id": "6507a1b2c3d4e5f6a7b8c940",
          "name": "icon_finance.png",
          "dimensions": {
            "sm": { "width": 64, "height": 64, "url": "https://cdn.viewboost.vn/sm_icon_finance.png" },
            "md": { "width": 128, "height": 128, "url": "https://cdn.viewboost.vn/md_icon_finance.png" }
          }
        },
        "createdAt": "2024-01-01T08:00:00Z",
        "updatedAt": "2024-01-01T08:00:00Z"
      },
      {
        "_id": "6507a1b2c3d4e5f6a7b8c9d6",
        "name": "Cuoc song & Phong cach",
        "code": "cuoc-song-phong-cach",
        "partner": "6507a1b2c3d4e5f6a7b8c903",
        "icon": null,
        "createdAt": "2024-01-02T10:00:00Z",
        "updatedAt": "2024-01-02T10:00:00Z"
      },
      {
        "_id": "6507a1b2c3d4e5f6a7b8c9d7",
        "name": "Du lich & Kham pha",
        "code": "du-lich-kham-pha",
        "partner": "6507a1b2c3d4e5f6a7b8c903",
        "icon": null,
        "createdAt": "2024-01-03T10:00:00Z",
        "updatedAt": "2024-01-03T10:00:00Z"
      }
    ],
    "total": 3
  },
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| Token thieu | - | 401 | "unauthorized" |
| Khong du quyen | Token thuong | 403 | "forbidden" |

---

## 25. Tao danh muc thu thach

**Quyen:** `IsCampaginOwner`
**Endpoint:** `POST /event-categories`

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |
| `Content-Type` | `application/json` | Co |

### Body mau

**Khong co icon:**
```json
{
  "name": "Am thuc & An uong",
  "code": "am-thuc-an-uong"
}
```

**Co icon:**
```json
{
  "name": "The thao & Suc khoe",
  "code": "the-thao-suc-khoe",
  "icon": {
    "_id": "6507a1b2c3d4e5f6a7b8c941",
    "name": "icon_sport.png",
    "dimensions": {
      "sm": { "width": 64, "height": 64, "url": "" },
      "md": { "width": 128, "height": 128, "url": "" }
    }
  }
}
```

**Luu y validation:**
- `name`: bat buoc
- `code`: bat buoc
- `icon`: tuy chon (FilePhoto object)

### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/event-categories" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Am thuc & An uong",
    "code": "am-thuc-an-uong"
  }'
```

### cURL (co icon)

```bash
curl -X POST "{{ADMIN_BASE_URL}}/event-categories" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "The thao & Suc khoe",
    "code": "the-thao-suc-khoe",
    "icon": {
      "_id": "6507a1b2c3d4e5f6a7b8c941",
      "name": "icon_sport.png",
      "dimensions": {
        "sm": { "width": 64, "height": 64, "url": "" },
        "md": { "width": 128, "height": 128, "url": "" }
      }
    }
  }'
```

### Response mau (200)

```json
{
  "data": {},
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| Thieu `name` | `name: ""` | 400 | "name is required" |
| Thieu `code` | `code: ""` | 400 | "code is required" |
| Token thieu | - | 401 | "unauthorized" |
| Khong du quyen | Token thuong | 403 | "forbidden" |

---

## 26. Cap nhat danh muc thu thach

**Quyen:** `IsCampaginOwner`
**Endpoint:** `PATCH /event-categories/:id`

### Headers

| Header | Gia tri | Bat buoc |
|--------|---------|----------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | Co |
| `Content-Type` | `application/json` | Co |

### Path Params

| Param | Kieu | Mo ta |
|-------|------|-------|
| `id` | string (ObjectID) | ID cua danh muc |

### Body mau

**Cap nhat ten va code:**
```json
{
  "name": "Tai chinh, Ngan hang & Dau tu",
  "code": "tai-chinh-ngan-hang-dau-tu"
}
```

**Cap nhat ca icon:**
```json
{
  "name": "Tai chinh, Ngan hang & Dau tu",
  "code": "tai-chinh-ngan-hang-dau-tu",
  "icon": {
    "_id": "6507a1b2c3d4e5f6a7b8c942",
    "name": "icon_finance_v2.png",
    "dimensions": {
      "sm": { "width": 64, "height": 64, "url": "" },
      "md": { "width": 128, "height": 128, "url": "" }
    }
  }
}
```

**Xoa icon (dat ve null):**
```json
{
  "name": "Tai chinh, Ngan hang & Dau tu",
  "code": "tai-chinh-ngan-hang-dau-tu",
  "icon": null
}
```

**Luu y:** Tat ca cac truong deu tuy chon trong update. Chi can gui cac truong muon cap nhat.

### cURL

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/event-categories/{{CATEGORY_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tai chinh, Ngan hang & Dau tu",
    "code": "tai-chinh-ngan-hang-dau-tu"
  }'
```

### Response mau (200)

```json
{
  "data": {},
  "code": 200
}
```

### Test loi

| Truong hop | Input | HTTP | Message |
|------------|-------|------|---------|
| `id` sai dinh dang | `/event-categories/bad-id` | 404 | "not found" |
| ID khong ton tai | ID hop le nhung khong ton tai | 400 | "not found" |
| Token thieu | - | 401 | "unauthorized" |
| Khong du quyen | Token thuong | 403 | "forbidden" |

---

## Tong ket

| # | Endpoint | Method | Quyen | Mo ta |
|---|----------|--------|-------|-------|
| 1 | `/events` | POST | IsCampaginOwner | Tao thu thach |
| 2 | `/events/:id` | PUT | IsCampaginOwner | Cap nhat thu thach |
| 3 | `/events/:id/status` | PATCH | IsCampaginOwner | Doi trang thai thu thach |
| 4 | `/events/:id` | GET | IsCampaginOwner | Chi tiet thu thach |
| 5 | `/events` | GET | IsCampaginOwner | Danh sach thu thach |
| 6 | `/events/statistic` | GET | IsCampaginOwner | Thong ke thu thach |
| 7 | `/events/chart` | GET | IsCampaginOwner | Du lieu bieu do |
| 8 | `/events/:id/block-user-submit-content` | PATCH | IsAdmin | Khoa nop noi dung |
| 9 | `/events/:id/block-create-reward` | PATCH | IsAdmin | Khoa tao thuong |
| 10 | `/events/report-statistic` | GET | IsAdmin | Bao cao thong ke |
| 11 | `/events/run-analytic-daily` | GET | IsAdmin | Chay phan tich hang ngay |
| 12 | `/events/reject-reward-event` | POST | IsRoot | Tu choi thuong hang loat |
| 13 | `/events/rerun-reward-event-by-cad` | GET | IsRoot | Chay lai thuong theo CAD |
| 14 | `/event-schemas` | POST | IsCampaginOwner | Tao schema |
| 15 | `/event-schemas/:id` | PUT | IsCampaginOwner | Cap nhat schema |
| 16 | `/event-schemas/:id/status` | PATCH | IsCampaginOwner | Doi trang thai schema |
| 17 | `/event-schemas` | GET | IsCampaginOwner | Danh sach schema |
| 18 | `/event-bonus` | GET | RequiredLogin | Danh sach bonus |
| 19 | `/event-bonus/:id` | GET | RequiredLogin | Chi tiet bonus |
| 20 | `/event-bonus` | POST | RequiredLogin | Tao bonus |
| 21 | `/event-bonus/:id` | PUT | RequiredLogin | Cap nhat bonus |
| 22 | `/event-bonus/:id/change-status` | PATCH | RequiredLogin | Doi trang thai bonus |
| 23 | `/event-bonus/import-excel` | POST | RequiredLogin | Import bonus tu Excel |
| 24 | `/event-categories` | GET | IsCampaginOwner | Danh sach danh muc |
| 25 | `/event-categories` | POST | IsCampaginOwner | Tao danh muc |
| 26 | `/event-categories/:id` | PATCH | IsCampaginOwner | Cap nhat danh muc |
