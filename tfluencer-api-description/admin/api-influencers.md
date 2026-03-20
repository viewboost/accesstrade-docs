# API Influencers - Admin

Base URL: `{{ADMIN_BASE_URL}}` (vd: `https://api.example.com/admin`)

---

## Muc quyen

| Middleware | Mo ta |
|---|---|
| `RequiredLogin` | Phai co token hop le |
| `IsAdmin` | Phai la Admin |
| `IsCampaginOwner` | Phai la Campaign Owner (hoac cao hon) |

---

## Bien dung trong doc nay

| Bien | Mo ta | Vi du |
|---|---|---|
| `{{INFLUENCER_ID}}` | ObjectID cua influencer (user_partner) | `664a1f2e3c4b5d6e7f8a9b0c` |
| `{{PROFILE_ID}}` | ObjectID cua influencer profile | `664a1f2e3c4b5d6e7f8a9b1d` |
| `{{REVIEW_ID}}` | ObjectID cua review | `664a1f2e3c4b5d6e7f8a9b2e` |
| `{{CONDITION_ID}}` | ObjectID cua dieu kien tu dong duyet | `664a1f2e3c4b5d6e7f8a9b3f` |

---

## Nhom 1: Influencers (IsAdmin)

Tat ca cac API trong nhom nay yeu cau middleware `RequiredLogin` + `IsAdmin`.

---

### 1. GetListInfluencer - Lay danh sach Influencer

**Quyen:** `IsAdmin`
**Endpoint:** `GET /influencers`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `page` | int | Khong | So trang | `1` |
| `limit` | int | Khong | So ban ghi tren trang (mac dinh: 20) | `20` |
| `status` | string | Khong | Trang thai influencer | `approved` / `rejected` |
| `source` | string | Khong | Nguon mang xa hoi | `youtube` / `tiktok` / `instagram` / `facebook` |
| `userId` | string | Khong | Loc theo User ID cu the | `664a1f2e3c4b5d6e7f8a9b0c` |
| `fromAt` | string | Khong | Ngay bat dau (ISO date) | `2024-01-01` |
| `toAt` | string | Khong | Ngay ket thuc (ISO date) | `2024-12-31` |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/influencers?page=1&limit=20&status=approved&source=tiktok" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "list": [
      {
        "_id": "664a1f2e3c4b5d6e7f8a9b0c",
        "user": "664a1f2e3c4b5d6e7f8a9b01",
        "partner": "664a1f2e3c4b5d6e7f8a9b02",
        "statusStaff": "approved",
        "code": "INF001",
        "isJoined": true,
        "joinedAt": "2024-03-15T08:00:00Z",
        "statistic": {
          "totalSubscribers": 150000,
          "totalViews": 2500000,
          "totalCash": 5000000
        },
        "socialSourceStats": {
          "tiktok": {
            "subscribers": 150000,
            "views": { "total": 2500000 },
            "cash": { "total": 5000000 }
          }
        },
        "createdAt": "2024-01-10T07:00:00Z",
        "updatedAt": "2024-03-20T10:00:00Z"
      }
    ],
    "total": 1
  }
}
```

#### Test loi

```bash
# Thieu token -> 401
curl -X GET "{{ADMIN_BASE_URL}}/influencers"

# Khong co quyen IsAdmin -> 403
curl -X GET "{{ADMIN_BASE_URL}}/influencers" \
  -H "Authorization: Bearer {{CAMPAIGN_OWNER_TOKEN}}"
```

---

### 2. ChangeStatusInfluencer - Doi trang thai Influencer

**Quyen:** `IsAdmin`
**Endpoint:** `PATCH /influencers/:id/change-status`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Path Params

| Param | Kieu | Bat buoc | Mo ta |
|---|---|---|---|
| `id` | string (ObjectID) | Co | ID cua influencer (`{{INFLUENCER_ID}}`) |

#### Body

| Field | Kieu | Bat buoc | Mo ta | Gia tri hop le |
|---|---|---|---|---|
| `status` | string | Co | Trang thai moi | `approved` / `rejected` |
| `reason` | string | Khong | Ly do thay doi trang thai | `"Khong du dieu kien"` |

#### cURL

```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/influencers/{{INFLUENCER_ID}}/change-status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "reason": ""
  }'
```

```bash
# Reject voi ly do
curl -X PATCH "{{ADMIN_BASE_URL}}/influencers/{{INFLUENCER_ID}}/change-status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "rejected",
    "reason": "Khong du so luong subscriber toi thieu"
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

```bash
# status khong hop le -> 400
curl -X PATCH "{{ADMIN_BASE_URL}}/influencers/{{INFLUENCER_ID}}/change-status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"status": "pending"}'

# ID sai format -> 400
curl -X PATCH "{{ADMIN_BASE_URL}}/influencers/invalid-id/change-status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"status": "approved"}'

# Thieu status -> 400
curl -X PATCH "{{ADMIN_BASE_URL}}/influencers/{{INFLUENCER_ID}}/change-status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

### 3. UpdateStatsInfluencer - Cap nhat thong ke Influencer

**Quyen:** `IsAdmin`
**Endpoint:** `PUT /influencers/:id/update-stats`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Path Params

| Param | Kieu | Bat buoc | Mo ta |
|---|---|---|---|
| `id` | string (ObjectID) | Co | ID cua influencer (`{{INFLUENCER_ID}}`) |

#### Body

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `channelId` | string | Khong | ID kenh mang xa hoi | `"UCxxxx"` |
| `name` | string | Khong | Ten kenh | `"My Channel"` |
| `stats` | object | Khong | Thong ke kenh | xem ben duoi |
| `stats.subscribers` | int | Khong | So luong subscriber | `150000` |
| `stats.views` | int | Khong | Tong luot xem | `2500000` |
| `stats.videos` | int | Khong | Tong so video | `200` |

#### cURL

```bash
curl -X PUT "{{ADMIN_BASE_URL}}/influencers/{{INFLUENCER_ID}}/update-stats" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "channelId": "UCxxxxxxxxxxxxxx",
    "name": "My YouTube Channel",
    "stats": {
      "subscribers": 150000,
      "views": 2500000,
      "videos": 200
    }
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

```bash
# ID sai format -> 400
curl -X PUT "{{ADMIN_BASE_URL}}/influencers/bad-id/update-stats" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

### 4. GetListCondition - Lay danh sach dieu kien tu dong duyet

**Quyen:** `IsAdmin`
**Endpoint:** `GET /influencers/conditions`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `page` | int | Khong | So trang | `1` |
| `limit` | int | Khong | So ban ghi tren trang | `20` |
| `source` | string | Khong | Nguon mang xa hoi | `youtube` / `tiktok` |
| `partner` | string | Khong | ObjectID cua partner | `664a1f2e3c4b5d6e7f8a9b02` |
| `status` | string | Khong | Trang thai cau hinh | `active` / `inactive` |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/influencers/conditions?page=1&limit=20&status=active" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

```bash
# Loc theo partner va nguon
curl -X GET "{{ADMIN_BASE_URL}}/influencers/conditions?partner=664a1f2e3c4b5d6e7f8a9b02&source=tiktok" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "list": [
      {
        "_id": "664a1f2e3c4b5d6e7f8a9b3f",
        "partner": "664a1f2e3c4b5d6e7f8a9b02",
        "source": "tiktok",
        "status": "active",
        "conditionAutoApprove": {
          "MinSubscribe": 10000,
          "MinVideo": 10,
          "MinView": 100000,
          "RequireDemographics": true,
          "StatusStaffRequired": "approved"
        },
        "createdAt": "2024-01-10T07:00:00Z",
        "updatedAt": "2024-03-20T10:00:00Z"
      }
    ],
    "total": 1
  }
}
```

#### Test loi

```bash
# Thieu token -> 401
curl -X GET "{{ADMIN_BASE_URL}}/influencers/conditions"
```

---

### 5. GetDetailCondition - Lay chi tiet dieu kien tu dong duyet

**Quyen:** `IsAdmin`
**Endpoint:** `GET /influencers/conditions/:id`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Kieu | Bat buoc | Mo ta |
|---|---|---|---|
| `id` | string (ObjectID) | Co | ID cua dieu kien (`{{CONDITION_ID}}`) |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/influencers/conditions/{{CONDITION_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "664a1f2e3c4b5d6e7f8a9b3f",
    "partner": "664a1f2e3c4b5d6e7f8a9b02",
    "source": "tiktok",
    "status": "active",
    "conditionAutoApprove": {
      "MinSubscribe": 10000,
      "MinVideo": 10,
      "MinView": 100000,
      "RequireDemographics": true,
      "StatusStaffRequired": "approved"
    },
    "createdAt": "2024-01-10T07:00:00Z",
    "updatedAt": "2024-03-20T10:00:00Z"
  }
}
```

#### Test loi

```bash
# ID sai format ObjectID -> 400
curl -X GET "{{ADMIN_BASE_URL}}/influencers/conditions/not-valid-id" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

---

### 6. UpsertCondition - Tao hoac cap nhat dieu kien tu dong duyet

**Quyen:** `IsAdmin`
**Endpoint:** `POST /influencers/conditions`

> Neu truyen `id` trong body: cap nhat dieu kien hien co. Neu khong co `id`: tao moi.

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Body

| Field | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `id` | string (ObjectID) | Khong | ID de cap nhat (bo trong de tao moi) | `"664a...3f"` |
| `source` | string | Co | Nguon mang xa hoi | `"youtube"` / `"tiktok"` |
| `partner` | string (ObjectID) | Co | ID cua partner | `"664a1f2e3c4b5d6e7f8a9b02"` |
| `conditionAutoApprove` | object | Co | Dieu kien tu dong duyet | xem ben duoi |
| `conditionAutoApprove.MinSubscribe` | int | Khong | So subscriber toi thieu | `10000` |
| `conditionAutoApprove.MinVideo` | int | Khong | So video toi thieu | `10` |
| `conditionAutoApprove.MinView` | int | Khong | So luot xem toi thieu | `100000` |
| `conditionAutoApprove.RequireDemographics` | bool | Khong | Yeu cau co thong tin demographics | `true` |
| `conditionAutoApprove.StatusStaffRequired` | string | Khong | Trang thai staff yeu cau | `"approved"` |

#### cURL - Tao moi

```bash
curl -X POST "{{ADMIN_BASE_URL}}/influencers/conditions" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "tiktok",
    "partner": "664a1f2e3c4b5d6e7f8a9b02",
    "conditionAutoApprove": {
      "MinSubscribe": 10000,
      "MinVideo": 10,
      "MinView": 100000,
      "RequireDemographics": true,
      "StatusStaffRequired": "approved"
    }
  }'
```

#### cURL - Cap nhat

```bash
curl -X POST "{{ADMIN_BASE_URL}}/influencers/conditions" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "{{CONDITION_ID}}",
    "source": "tiktok",
    "partner": "664a1f2e3c4b5d6e7f8a9b02",
    "conditionAutoApprove": {
      "MinSubscribe": 20000,
      "MinVideo": 20,
      "MinView": 200000,
      "RequireDemographics": false,
      "StatusStaffRequired": "approved"
    }
  }'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "664a1f2e3c4b5d6e7f8a9b3f",
    "partner": "664a1f2e3c4b5d6e7f8a9b02",
    "source": "tiktok",
    "status": "active",
    "conditionAutoApprove": {
      "MinSubscribe": 10000,
      "MinVideo": 10,
      "MinView": 100000,
      "RequireDemographics": true,
      "StatusStaffRequired": "approved"
    },
    "createdAt": "2024-03-20T10:00:00Z",
    "updatedAt": "2024-03-20T10:00:00Z"
  }
}
```

#### Test loi

```bash
# Thieu source -> 400
curl -X POST "{{ADMIN_BASE_URL}}/influencers/conditions" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "partner": "664a1f2e3c4b5d6e7f8a9b02",
    "conditionAutoApprove": {}
  }'

# Thieu partner -> 400
curl -X POST "{{ADMIN_BASE_URL}}/influencers/conditions" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "tiktok",
    "conditionAutoApprove": {}
  }'
```

---

### 7. ChangeStatusCondition - Doi trang thai dieu kien tu dong duyet

**Quyen:** `IsAdmin`
**Endpoint:** `PATCH /influencers/conditions/:id/status`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Path Params

| Param | Kieu | Bat buoc | Mo ta |
|---|---|---|---|
| `id` | string (ObjectID) | Co | ID cua dieu kien (`{{CONDITION_ID}}`) |

#### Body

| Field | Kieu | Bat buoc | Mo ta | Gia tri hop le |
|---|---|---|---|---|
| `status` | string | Co | Trang thai moi | `active` / `inactive` |

#### cURL

```bash
# Tat dieu kien
curl -X PATCH "{{ADMIN_BASE_URL}}/influencers/conditions/{{CONDITION_ID}}/status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"status": "inactive"}'
```

```bash
# Bat dieu kien
curl -X PATCH "{{ADMIN_BASE_URL}}/influencers/conditions/{{CONDITION_ID}}/status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}'
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

```bash
# status khong hop le -> 400
curl -X PATCH "{{ADMIN_BASE_URL}}/influencers/conditions/{{CONDITION_ID}}/status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"status": "disabled"}'

# ID sai format -> 400
curl -X PATCH "{{ADMIN_BASE_URL}}/influencers/conditions/invalid/status" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}'
```

---

### 8. GetStatistic - Lay thong ke Influencer

**Quyen:** `IsAdmin`
**Endpoint:** `GET /influencers/statistic`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `partner` | string (ObjectID) | Khong | Loc theo partner | `664a1f2e3c4b5d6e7f8a9b02` |
| `fromAt` | string | Khong | Ngay bat dau (ISO date) | `2024-01-01` |
| `toAt` | string | Khong | Ngay ket thuc (ISO date) | `2024-12-31` |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/influencers/statistic?partner=664a1f2e3c4b5d6e7f8a9b02&fromAt=2024-01-01&toAt=2024-12-31" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

```bash
# Lay thong ke toan bo (khong loc)
curl -X GET "{{ADMIN_BASE_URL}}/influencers/statistic" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "total": 1250,
    "approved": 980,
    "rejected": 120,
    "pending": 150,
    "bySource": {
      "tiktok": 500,
      "youtube": 350,
      "instagram": 280,
      "facebook": 120
    }
  }
}
```

#### Test loi

```bash
# Thieu token -> 401
curl -X GET "{{ADMIN_BASE_URL}}/influencers/statistic"
```

---

## Nhom 2: Influencer Profiles (IsCampaginOwner)

Tat ca cac API trong nhom nay yeu cau middleware `RequiredLogin` + `IsCampaginOwner`.

---

### 9. GetProfileList - Lay danh sach Profile Influencer

**Quyen:** `IsCampaginOwner`
**Endpoint:** `GET /profiles`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Query Params

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|---|---|---|---|---|
| `page` | int | Khong | So trang (min: 1) | `1` |
| `limit` | int | Khong | So ban ghi (min: 1, max: 100) | `20` |
| `search` | string | Khong | Tim kiem theo ten / handle | `"nguyen"` |
| `source` | string | Khong | Nguon (CSV) | `"tiktok"` / `"tiktok,youtube"` |
| `at_core_status` | string | Khong | Trang thai AT Core (CSV) | `"active"` / `"active,pending"` |
| `tier` | string | Khong | Tier influencer (CSV) | `"nano"` / `"micro,macro"` |
| `engagement_tier` | string | Khong | Tier engagement (CSV) | `"high"` / `"high,medium"` |

> Cac param ho tro nhieu gia tri qua dau phay (CSV): `source=tiktok,youtube`

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/profiles?page=1&limit=20&search=nguyen&source=tiktok" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

```bash
# Loc theo nhieu nguon va tier
curl -X GET "{{ADMIN_BASE_URL}}/profiles?page=1&limit=50&source=tiktok,youtube&tier=micro,macro&at_core_status=active" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "list": [
      {
        "_id": "664a1f2e3c4b5d6e7f8a9b1d",
        "user": "664a1f2e3c4b5d6e7f8a9b01",
        "displayName": "Nguyen Van A",
        "handle": "@nguyenvana",
        "platform": "tiktok",
        "avatarUrl": "https://cdn.example.com/avatar.jpg",
        "categories": ["lifestyle", "food"],
        "subCategories": ["cooking", "travel"],
        "scoreTotal": 82.5,
        "scoreCategory": "micro",
        "avgViews": 50000,
        "totalViews": 10000000,
        "totalLikes": 500000,
        "isVerified": true,
        "country": "VN",
        "city": "Ho Chi Minh",
        "gender": "male",
        "createdAt": "2024-01-10T07:00:00Z",
        "updatedAt": "2024-03-20T10:00:00Z"
      }
    ],
    "total": 1
  }
}
```

#### Test loi

```bash
# page < 1 -> 400
curl -X GET "{{ADMIN_BASE_URL}}/profiles?page=0" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"

# limit > 100 -> 400
curl -X GET "{{ADMIN_BASE_URL}}/profiles?limit=200" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"

# Khong co quyen IsCampaginOwner -> 403
curl -X GET "{{ADMIN_BASE_URL}}/profiles" \
  -H "Authorization: Bearer {{REGULAR_STAFF_TOKEN}}"
```

---

### 10. GetProfileDetail - Lay chi tiet Profile Influencer

**Quyen:** `IsCampaginOwner`
**Endpoint:** `GET /profiles/:id`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Kieu | Bat buoc | Mo ta |
|---|---|---|---|
| `id` | string (ObjectID) | Co | ID cua profile (`{{PROFILE_ID}}`) |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/profiles/{{PROFILE_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "664a1f2e3c4b5d6e7f8a9b1d",
    "user": "664a1f2e3c4b5d6e7f8a9b01",
    "displayName": "Nguyen Van A",
    "handle": "@nguyenvana",
    "platform": "tiktok",
    "profileId": "tiktok_native_id_123",
    "avatarUrl": "https://cdn.example.com/avatar.jpg",
    "description": "Lifestyle & Food creator",
    "categories": ["lifestyle", "food"],
    "subCategories": ["cooking", "travel", "restaurant"],
    "contentLanguage": ["vi", "en"],
    "audienceAge": "18-24",
    "gender": "male",
    "city": "Ho Chi Minh",
    "country": "VN",
    "email": "nguyenvana@gmail.com",
    "dob": "1998-05-15T00:00:00Z",
    "scoreTotal": 82.5,
    "scoreCategory": "micro",
    "scoreHighlights": ["high_engagement", "consistent_posting"],
    "avgViews": 50000,
    "totalViews": 10000000,
    "totalLikes": 500000,
    "isVerified": true,
    "tracking": {
      "enrichedAt": "2024-03-15T08:00:00Z",
      "errorCode": "",
      "errorMsg": ""
    },
    "createdAt": "2024-01-10T07:00:00Z",
    "updatedAt": "2024-03-20T10:00:00Z"
  }
}
```

#### Test loi

```bash
# ID sai format -> 400
curl -X GET "{{ADMIN_BASE_URL}}/profiles/invalid-id" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"

# Profile khong ton tai -> 400
curl -X GET "{{ADMIN_BASE_URL}}/profiles/000000000000000000000000" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

---

### 11. GetInfluencerDetail - Lay chi tiet Influencer (theo User ID)

**Quyen:** `IsCampaginOwner`
**Endpoint:** `GET /influencers/:id`

> **Luu y:** Day la endpoint cua handler `influencer_profiles.go`, khac voi nhom Influencers (IsAdmin). Tra ve thong tin chi tiet cua influencer theo User ID.

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Kieu | Bat buoc | Mo ta |
|---|---|---|---|
| `id` | string (ObjectID) | Co | User ID cua influencer (`{{INFLUENCER_ID}}`) |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/influencers/{{INFLUENCER_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "_id": "664a1f2e3c4b5d6e7f8a9b01",
    "name": "Nguyen Van A",
    "email": "nguyenvana@gmail.com",
    "phone": "0901234567",
    "status": "active",
    "partner": "664a1f2e3c4b5d6e7f8a9b02",
    "userPartner": {
      "_id": "664a1f2e3c4b5d6e7f8a9b0c",
      "statusStaff": "approved",
      "code": "INF001",
      "isJoined": true,
      "joinedAt": "2024-03-15T08:00:00Z"
    },
    "createdAt": "2024-01-10T07:00:00Z",
    "updatedAt": "2024-03-20T10:00:00Z"
  }
}
```

#### Test loi

```bash
# ID sai format -> 400
curl -X GET "{{ADMIN_BASE_URL}}/influencers/not-valid" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"

# Influencer khong ton tai -> 400
curl -X GET "{{ADMIN_BASE_URL}}/influencers/000000000000000000000000" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

---

### 12. GetInfluencerProfiles - Lay danh sach Profile cua mot Influencer

**Quyen:** `IsCampaginOwner`
**Endpoint:** `GET /influencers/:id/profiles`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Kieu | Bat buoc | Mo ta |
|---|---|---|---|
| `id` | string (ObjectID) | Co | User ID cua influencer (`{{INFLUENCER_ID}}`) |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/influencers/{{INFLUENCER_ID}}/profiles" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": [
    {
      "_id": "664a1f2e3c4b5d6e7f8a9b1d",
      "user": "664a1f2e3c4b5d6e7f8a9b01",
      "displayName": "Nguyen Van A - TikTok",
      "handle": "@nguyenvana",
      "platform": "tiktok",
      "avatarUrl": "https://cdn.example.com/avatar.jpg",
      "scoreTotal": 82.5,
      "scoreCategory": "micro",
      "isVerified": true,
      "createdAt": "2024-01-10T07:00:00Z",
      "updatedAt": "2024-03-20T10:00:00Z"
    },
    {
      "_id": "664a1f2e3c4b5d6e7f8a9b1e",
      "user": "664a1f2e3c4b5d6e7f8a9b01",
      "displayName": "Nguyen Van A - YouTube",
      "handle": "@nguyenvana_yt",
      "platform": "youtube",
      "avatarUrl": "https://cdn.example.com/avatar2.jpg",
      "scoreTotal": 75.0,
      "scoreCategory": "nano",
      "isVerified": false,
      "createdAt": "2024-02-01T09:00:00Z",
      "updatedAt": "2024-03-18T11:00:00Z"
    }
  ]
}
```

#### Test loi

```bash
# ID sai format -> 400
curl -X GET "{{ADMIN_BASE_URL}}/influencers/bad-id/profiles" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

---

## Nhom 3: Reviews

### Phan biet Admin vs Brand Portal

| Nhom | Prefix | Quyen | Mo ta |
|---|---|---|---|
| Admin | `/api/v1` | `IsAdmin` | Quan tri vien toan quyen |
| Brand Portal | (khong co prefix) | `RequiredLogin` | Brand nop danh gia sau campaign |

---

### 13. [Admin] SubmitReview - Nop danh gia Influencer

**Quyen:** `IsAdmin`
**Endpoint:** `POST /api/v1/profiles/:profile_id/reviews`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Path Params

| Param | Kieu | Bat buoc | Mo ta |
|---|---|---|---|
| `profile_id` | string (ObjectID) | Co | ID cua influencer profile (`{{PROFILE_ID}}`) |

#### Body

| Field | Kieu | Bat buoc | Mo ta | Rang buoc |
|---|---|---|---|---|
| `campaign_id` | string (ObjectID) | Co | ID cua campaign | Required |
| `content_quality` | int | Khong | Chat luong noi dung (1-5 sao) | 1 <= value <= 5 |
| `professionalism` | int | Khong | Tinh chuyen nghiep (1-5 sao) | 1 <= value <= 5 |
| `communication` | int | Khong | Kha nang giao tiep (1-5 sao) | 1 <= value <= 5 |
| `on_time_delivery` | int | Khong | Giao hang dung han (1-5 sao) | 1 <= value <= 5 |
| `performance_rating` | int | Khong | Hieu suat tong the (1-5 sao) | 1 <= value <= 5 |
| `review_text` | string | Khong | Nhan xet chu (toi da 500 ky tu) | max 500 chars |

> `overall_rating` duoc tinh tu dong bang gia tri trung binh cua cac tieu chi duoc dien.

#### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/api/v1/profiles/{{PROFILE_ID}}/reviews" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "664a1f2e3c4b5d6e7f8a9b05",
    "content_quality": 5,
    "professionalism": 4,
    "communication": 5,
    "on_time_delivery": 4,
    "performance_rating": 5,
    "review_text": "Influencer rat chuyen nghiep, noi dung chat luong cao, giao hang dung han."
  }'
```

```bash
# Chi nop mot so tieu chi
curl -X POST "{{ADMIN_BASE_URL}}/api/v1/profiles/{{PROFILE_ID}}/reviews" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "664a1f2e3c4b5d6e7f8a9b05",
    "content_quality": 4,
    "professionalism": 5
  }'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "Review submitted successfully",
  "data": {
    "id": "664a1f2e3c4b5d6e7f8a9b2e",
    "campaign_id": "664a1f2e3c4b5d6e7f8a9b05",
    "profile_id": "664a1f2e3c4b5d6e7f8a9b1d",
    "brand_id": "664a1f2e3c4b5d6e7f8a9b02",
    "reviewer_user_id": "664a1f2e3c4b5d6e7f8a9b10",
    "content_quality": 5,
    "professionalism": 4,
    "communication": 5,
    "on_time_delivery": 4,
    "performance_rating": 5,
    "overall_rating": 4.6,
    "review_text": "Influencer rat chuyen nghiep, noi dung chat luong cao, giao hang dung han.",
    "visibility": "private",
    "status": "active",
    "created_at": "2024-03-20T10:00:00Z",
    "updated_at": "2024-03-20T10:00:00Z"
  }
}
```

#### Test loi

```bash
# Thieu campaign_id -> 400
curl -X POST "{{ADMIN_BASE_URL}}/api/v1/profiles/{{PROFILE_ID}}/reviews" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "content_quality": 5
  }'

# Rating ngoai khoang [1,5] -> 400
curl -X POST "{{ADMIN_BASE_URL}}/api/v1/profiles/{{PROFILE_ID}}/reviews" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "664a1f2e3c4b5d6e7f8a9b05",
    "content_quality": 6
  }'

# review_text qua 500 ky tu -> 400
curl -X POST "{{ADMIN_BASE_URL}}/api/v1/profiles/{{PROFILE_ID}}/reviews" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "664a1f2e3c4b5d6e7f8a9b05",
    "review_text": "'"$(python3 -c "print('a'*501)")"'"
  }'
```

---

### 14. [Admin] ListReviews - Lay danh sach danh gia cua mot Profile

**Quyen:** `IsAdmin`
**Endpoint:** `GET /api/v1/profiles/:profile_id/reviews`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Kieu | Bat buoc | Mo ta |
|---|---|---|---|
| `profile_id` | string | Co | ID cua profile (`{{PROFILE_ID}}`) |

#### Query Params

| Param | Kieu | Bat buoc | Mo ta | Mac dinh |
|---|---|---|---|---|
| `page` | int | Khong | So trang (min: 1) | `1` |
| `limit` | int | Khong | So ban ghi (max: 100) | `20` |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/api/v1/profiles/{{PROFILE_ID}}/reviews?page=1&limit=20" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "reviews": [
      {
        "id": "664a1f2e3c4b5d6e7f8a9b2e",
        "campaign_id": "664a1f2e3c4b5d6e7f8a9b05",
        "profile_id": "664a1f2e3c4b5d6e7f8a9b1d",
        "brand_id": "664a1f2e3c4b5d6e7f8a9b02",
        "reviewer_user_id": "664a1f2e3c4b5d6e7f8a9b10",
        "content_quality": 5,
        "professionalism": 4,
        "communication": 5,
        "on_time_delivery": 4,
        "performance_rating": 5,
        "overall_rating": 4.6,
        "review_text": "Influencer rat chuyen nghiep.",
        "visibility": "private",
        "status": "active",
        "created_at": "2024-03-20T10:00:00Z",
        "updated_at": "2024-03-20T10:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "limit": 20
  }
}
```

#### Test loi

```bash
# profile_id trong -> 400
curl -X GET "{{ADMIN_BASE_URL}}/api/v1/profiles//reviews" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

---

### 15. [Admin] GetReview - Lay chi tiet mot danh gia

**Quyen:** `IsAdmin`
**Endpoint:** `GET /api/v1/reviews/:review_id`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Kieu | Bat buoc | Mo ta |
|---|---|---|---|
| `review_id` | string | Co | ID cua review (`{{REVIEW_ID}}`) |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/api/v1/reviews/{{REVIEW_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "id": "664a1f2e3c4b5d6e7f8a9b2e",
    "campaign_id": "664a1f2e3c4b5d6e7f8a9b05",
    "profile_id": "664a1f2e3c4b5d6e7f8a9b1d",
    "brand_id": "664a1f2e3c4b5d6e7f8a9b02",
    "reviewer_user_id": "664a1f2e3c4b5d6e7f8a9b10",
    "content_quality": 5,
    "professionalism": 4,
    "communication": 5,
    "on_time_delivery": 4,
    "performance_rating": 5,
    "overall_rating": 4.6,
    "review_text": "Influencer rat chuyen nghiep.",
    "visibility": "private",
    "status": "active",
    "created_at": "2024-03-20T10:00:00Z",
    "updated_at": "2024-03-20T10:00:00Z"
  }
}
```

#### Test loi

```bash
# review_id trong -> 400
curl -X GET "{{ADMIN_BASE_URL}}/api/v1/reviews/" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"

# Review khong ton tai -> 400
curl -X GET "{{ADMIN_BASE_URL}}/api/v1/reviews/000000000000000000000000" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

---

### 16. [Admin] UpdateReview - Cap nhat danh gia (trong 24 gio)

**Quyen:** `IsAdmin`
**Endpoint:** `PUT /api/v1/reviews/:review_id`

> **Rang buoc:** Chi co the cap nhat review trong vong 24 gio sau khi tao. Admin chi duoc sua review cua chinh minh.

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Path Params

| Param | Kieu | Bat buoc | Mo ta |
|---|---|---|---|
| `review_id` | string | Co | ID cua review (`{{REVIEW_ID}}`) |

#### Body

| Field | Kieu | Bat buoc | Mo ta | Rang buoc |
|---|---|---|---|---|
| `content_quality` | int | Khong | Chat luong noi dung (1-5 sao) | 1 <= value <= 5 |
| `professionalism` | int | Khong | Tinh chuyen nghiep (1-5 sao) | 1 <= value <= 5 |
| `communication` | int | Khong | Kha nang giao tiep (1-5 sao) | 1 <= value <= 5 |
| `on_time_delivery` | int | Khong | Giao hang dung han (1-5 sao) | 1 <= value <= 5 |
| `performance_rating` | int | Khong | Hieu suat tong the (1-5 sao) | 1 <= value <= 5 |
| `review_text` | string | Khong | Nhan xet chu (toi da 500 ky tu) | max 500 chars |

#### cURL

```bash
curl -X PUT "{{ADMIN_BASE_URL}}/api/v1/reviews/{{REVIEW_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "content_quality": 4,
    "professionalism": 5,
    "communication": 4,
    "on_time_delivery": 5,
    "performance_rating": 4,
    "review_text": "Cap nhat: Rat hai long voi ket qua campaign."
  }'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "Review updated successfully",
  "data": {
    "id": "664a1f2e3c4b5d6e7f8a9b2e",
    "campaign_id": "664a1f2e3c4b5d6e7f8a9b05",
    "profile_id": "664a1f2e3c4b5d6e7f8a9b1d",
    "brand_id": "664a1f2e3c4b5d6e7f8a9b02",
    "reviewer_user_id": "664a1f2e3c4b5d6e7f8a9b10",
    "content_quality": 4,
    "professionalism": 5,
    "communication": 4,
    "on_time_delivery": 5,
    "performance_rating": 4,
    "overall_rating": 4.4,
    "review_text": "Cap nhat: Rat hai long voi ket qua campaign.",
    "visibility": "private",
    "status": "active",
    "created_at": "2024-03-20T10:00:00Z",
    "updated_at": "2024-03-20T10:30:00Z"
  }
}
```

#### Test loi

```bash
# Rating ngoai khoang [1,5] -> 400
curl -X PUT "{{ADMIN_BASE_URL}}/api/v1/reviews/{{REVIEW_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"professionalism": 0}'

# review_id trong -> 400
curl -X PUT "{{ADMIN_BASE_URL}}/api/v1/reviews/" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{}'

# Review qua 24 gio -> 400 (business logic)
curl -X PUT "{{ADMIN_BASE_URL}}/api/v1/reviews/{{OLD_REVIEW_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"content_quality": 3}'
```

---

### 17. [Brand] SubmitReview - Nop danh gia (Brand Portal)

**Quyen:** `RequiredLogin` (khong can IsAdmin)
**Endpoint:** `POST /profiles/:profile_id/reviews`

> Endpoint nay danh cho Brand Portal. Khac voi Admin (`/api/v1/`), `campaign_id` la **tuy chon** (SubmitReviewBrand).

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |
| `Content-Type` | Co | `application/json` |

#### Path Params

| Param | Kieu | Bat buoc | Mo ta |
|---|---|---|---|
| `profile_id` | string | Co | ID cua influencer profile (`{{PROFILE_ID}}`) |

#### Body

| Field | Kieu | Bat buoc | Mo ta | Rang buoc |
|---|---|---|---|---|
| `campaign_id` | string | Khong | ID cua campaign | Tuy chon (khi goi tu Brand Portal) |
| `content_quality` | int | Khong | Chat luong noi dung (1-5 sao) | 1 <= value <= 5 |
| `professionalism` | int | Khong | Tinh chuyen nghiep (1-5 sao) | 1 <= value <= 5 |
| `communication` | int | Khong | Kha nang giao tiep (1-5 sao) | 1 <= value <= 5 |
| `on_time_delivery` | int | Khong | Giao hang dung han (1-5 sao) | 1 <= value <= 5 |
| `performance_rating` | int | Khong | Hieu suat tong the (1-5 sao) | 1 <= value <= 5 |
| `review_text` | string | Khong | Nhan xet chu (toi da 500 ky tu) | max 500 chars |

#### cURL

```bash
curl -X POST "{{ADMIN_BASE_URL}}/profiles/{{PROFILE_ID}}/reviews" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "664a1f2e3c4b5d6e7f8a9b05",
    "content_quality": 5,
    "professionalism": 4,
    "communication": 5,
    "on_time_delivery": 3,
    "performance_rating": 4,
    "review_text": "Noi dung tot nhung giao muon mot chut."
  }'
```

```bash
# Nop khong co campaign_id (Brand Portal cho phep)
curl -X POST "{{ADMIN_BASE_URL}}/profiles/{{PROFILE_ID}}/reviews" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "content_quality": 5,
    "professionalism": 5,
    "review_text": "Rat hai long."
  }'
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "Review submitted successfully",
  "data": {
    "id": "664a1f2e3c4b5d6e7f8a9b2f",
    "campaign_id": "664a1f2e3c4b5d6e7f8a9b05",
    "profile_id": "664a1f2e3c4b5d6e7f8a9b1d",
    "brand_id": "664a1f2e3c4b5d6e7f8a9b02",
    "reviewer_user_id": "664a1f2e3c4b5d6e7f8a9b10",
    "content_quality": 5,
    "professionalism": 4,
    "communication": 5,
    "on_time_delivery": 3,
    "performance_rating": 4,
    "overall_rating": 4.2,
    "review_text": "Noi dung tot nhung giao muon mot chut.",
    "visibility": "private",
    "status": "active",
    "created_at": "2024-03-20T11:00:00Z",
    "updated_at": "2024-03-20T11:00:00Z"
  }
}
```

#### Test loi

```bash
# Rating ngoai khoang [1,5] -> 400
curl -X POST "{{ADMIN_BASE_URL}}/profiles/{{PROFILE_ID}}/reviews" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"content_quality": 10}'

# review_text > 500 ky tu -> 400
curl -X POST "{{ADMIN_BASE_URL}}/profiles/{{PROFILE_ID}}/reviews" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"review_text": "'"$(python3 -c "print('x'*501)")"'"}'
```

---

### 18. [Brand] ListReviews - Lay danh sach danh gia (Brand Portal)

**Quyen:** `RequiredLogin`
**Endpoint:** `GET /profiles/:profile_id/reviews`

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Kieu | Bat buoc | Mo ta |
|---|---|---|---|
| `profile_id` | string | Co | ID cua influencer profile (`{{PROFILE_ID}}`) |

#### Query Params

| Param | Kieu | Bat buoc | Mo ta | Mac dinh |
|---|---|---|---|---|
| `page` | int | Khong | So trang | `1` |
| `limit` | int | Khong | So ban ghi (max: 100) | `20` |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/profiles/{{PROFILE_ID}}/reviews?page=1&limit=10" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "reviews": [
      {
        "id": "664a1f2e3c4b5d6e7f8a9b2f",
        "campaign_id": "664a1f2e3c4b5d6e7f8a9b05",
        "profile_id": "664a1f2e3c4b5d6e7f8a9b1d",
        "overall_rating": 4.2,
        "review_text": "Noi dung tot.",
        "status": "active",
        "created_at": "2024-03-20T11:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "limit": 20
  }
}
```

---

### 19. [Brand] GetRatingStats - Lay thong ke danh gia tong hop cua Profile

**Quyen:** `RequiredLogin`
**Endpoint:** `GET /profiles/:profile_id/ratings/stats`

> Tra ve thong ke tong hop (cache) cua tat ca danh gia cho mot profile. Neu cache chua co hoac da cu, he thong se tu tinh lai truoc khi tra ve.

#### Headers

| Header | Bat buoc | Gia tri |
|---|---|---|
| `Authorization` | Co | `Bearer {{ADMIN_TOKEN}}` |

#### Path Params

| Param | Kieu | Bat buoc | Mo ta |
|---|---|---|---|
| `profile_id` | string | Co | ID cua influencer profile (`{{PROFILE_ID}}`) |

#### cURL

```bash
curl -X GET "{{ADMIN_BASE_URL}}/profiles/{{PROFILE_ID}}/ratings/stats" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

#### Response mau (200 OK - co du lieu)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "profile_id": "664a1f2e3c4b5d6e7f8a9b1d",
    "avg_overall": 4.35,
    "avg_content_quality": 4.6,
    "avg_professionalism": 4.4,
    "avg_communication": 4.5,
    "avg_on_time": 4.1,
    "avg_performance": 4.2,
    "total_reviews": 28,
    "last_recalculated_at": "2024-03-20T09:00:00Z"
  }
}
```

#### Response mau (200 OK - chua co danh gia)

```json
{
  "code": 200,
  "message": "",
  "data": {
    "profile_id": "664a1f2e3c4b5d6e7f8a9b1d",
    "avg_overall": 0,
    "avg_content_quality": 0,
    "avg_professionalism": 0,
    "avg_communication": 0,
    "avg_on_time": 0,
    "avg_performance": 0,
    "total_reviews": 0,
    "last_recalculated_at": "0001-01-01T00:00:00Z"
  }
}
```

#### Test loi

```bash
# profile_id trong -> 400
curl -X GET "{{ADMIN_BASE_URL}}/profiles//ratings/stats" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"

# Thieu token -> 401
curl -X GET "{{ADMIN_BASE_URL}}/profiles/{{PROFILE_ID}}/ratings/stats"
```

---

## Tom tat tat ca endpoints

### Nhom Influencers (IsAdmin)

| # | Method | Endpoint | Handler | Mo ta |
|---|---|---|---|---|
| 1 | GET | `/influencers` | GetListInfluencer | Danh sach influencer |
| 2 | PATCH | `/influencers/:id/change-status` | ChangeStatusInfluencer | Doi trang thai |
| 3 | PUT | `/influencers/:id/update-stats` | UpdateStatsInfluencer | Cap nhat thong ke |
| 4 | GET | `/influencers/conditions` | GetListCondition | Danh sach dieu kien |
| 5 | GET | `/influencers/conditions/:id` | GetDetailCondition | Chi tiet dieu kien |
| 6 | POST | `/influencers/conditions` | UpsertCondition | Tao / cap nhat dieu kien |
| 7 | PATCH | `/influencers/conditions/:id/status` | ChangeStatusCondition | Doi trang thai dieu kien |
| 8 | GET | `/influencers/statistic` | GetStatistic | Thong ke influencer |

### Nhom Influencer Profiles (IsCampaginOwner)

| # | Method | Endpoint | Handler | Mo ta |
|---|---|---|---|---|
| 9 | GET | `/profiles` | GetProfileList | Danh sach profile |
| 10 | GET | `/profiles/:id` | GetProfileDetail | Chi tiet profile |
| 11 | GET | `/influencers/:id` | GetInfluencerDetail | Chi tiet influencer (by user ID) |
| 12 | GET | `/influencers/:id/profiles` | GetInfluencerProfiles | Danh sach profile cua influencer |

### Nhom Reviews - Admin (IsAdmin, prefix `/api/v1`)

| # | Method | Endpoint | Handler | Mo ta |
|---|---|---|---|---|
| 13 | POST | `/api/v1/profiles/:profile_id/reviews` | SubmitReview | Nop danh gia |
| 14 | GET | `/api/v1/profiles/:profile_id/reviews` | ListReviews | Danh sach danh gia |
| 15 | GET | `/api/v1/reviews/:review_id` | GetReview | Chi tiet danh gia |
| 16 | PUT | `/api/v1/reviews/:review_id` | UpdateReview | Cap nhat danh gia |

### Nhom Reviews - Brand Portal (RequiredLogin, khong co prefix)

| # | Method | Endpoint | Handler | Mo ta |
|---|---|---|---|---|
| 17 | POST | `/profiles/:profile_id/reviews` | SubmitReview | Nop danh gia (brand) |
| 18 | GET | `/profiles/:profile_id/reviews` | ListReviews | Danh sach danh gia (brand) |
| 19 | GET | `/profiles/:profile_id/ratings/stats` | GetRatingStats | Thong ke danh gia tong hop |

**Tong: 19 endpoints**
