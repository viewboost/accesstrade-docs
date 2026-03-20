# Admin API - Analytics & Performance

## Thong tin chung

| Muc | Gia tri |
|-----|---------|
| Base URL | `{{ADMIN_BASE_URL}}` |
| Quyen yeu cau | `IsCampaginOwner` |
| Content-Type | `application/json` |

**Headers bat buoc cho moi request:**

```
Authorization: Bearer {{ADMIN_TOKEN}}
```

---

## Muc luc

### Analytics
1. [GET /analytics/global/dashboard](#1-get-analyticsglobaldashboard)
2. [GET /analytics/dashboard](#2-get-analyticsdashboard)
3. [GET /analytics/platforms](#3-get-analyticsplatforms)
4. [GET /analytics/creators](#4-get-analyticscreators)
5. [GET /analytics/creators/segments](#5-get-analyticscreatorsSegments)
6. [GET /analytics/approval](#6-get-analyticsapproval)
7. [GET /analytics/export](#7-get-analyticsexport)
8. [GET /analytics/trends](#8-get-analyticstrends)
9. [GET /analytics/creator-kpis](#9-get-analyticscreator-kpis)
10. [GET /analytics/transfers](#10-get-analyticstransfers)
11. [GET /analytics/campaigns](#11-get-analyticscampaigns)

### Performance
12. [POST /performance/import](#12-post-performanceimport)
13. [GET /performance/list](#13-get-performancelist)
14. [GET /performance/batches](#14-get-performancebatches)
15. [DELETE /performance/batches/:id](#15-delete-performancebatchesid)
16. [GET /analytics/performance/trends](#16-get-analyticsperformancetrends)

---

## Analytics

---

### 1. GET /analytics/global/dashboard

**Quyen:** `IsCampaginOwner`

**Mo ta:** Lay metrics tong hop toan nen tang, khong can filter theo event. Dung cho dashboard tong quan.

**Query params:** Khong co

**cURL:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/global/dashboard" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**Response thanh cong (200):**

```json
{
  "data": {
    "totalInfluencers": 1250,
    "totalVideos": 45320,
    "totalViews": 198500000,
    "totalLikes": 3200000,
    "totalComments": 850000,
    "totalPayment": 2500000000,
    "activeEvents": 5,
    "totalEvents": 18
  },
  "code": 200
}
```

**Test loi:**

```bash
# Thieu token → 401
curl -X GET "{{ADMIN_BASE_URL}}/analytics/global/dashboard"

# Token sai / het han → 401
curl -X GET "{{ADMIN_BASE_URL}}/analytics/global/dashboard" \
  -H "Authorization: Bearer invalid_token"
```

---

### 2. GET /analytics/dashboard

**Quyen:** `IsCampaginOwner`

**Mo ta:** Lay KPI tong hop cho dashboard theo event va khoang thoi gian. Ho tro so sanh voi ky truoc.

**Query params:**

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|-------|------|----------|-------|-------|
| `event` | string | Khong | ID cua 1 event (MongoDB ObjectID) | `67a1b2c3d4e5f6a7b8c9d0e1` |
| `events` | string | Khong | Nhieu event ID, phan cach dau phay | `67a1b2c3d4e5f6a7b8c9d0e1,67a1b2c3d4e5f6a7b8c9d0e2` |
| `startDate` | string | Khong | Ngay bat dau `YYYY-MM-DD` | `2024-01-01` |
| `endDate` | string | Khong | Ngay ket thuc `YYYY-MM-DD` | `2024-03-31` |
| `compareWith` | string | Khong | So sanh voi ky: `previousPeriod`, `lastWeek`, `lastMonth` | `previousPeriod` |

> **Luu y:** `events` uu tien hon `event` khi ca hai duoc truyen. Neu khong truyen ca hai, tra ket qua tat ca events.

**cURL - Lay KPI theo event va ngay:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/dashboard?events=67a1b2c3d4e5f6a7b8c9d0e1&startDate=2024-01-01&endDate=2024-03-31" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**cURL - Lay KPI voi so sanh ky truoc:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/dashboard?events=67a1b2c3d4e5f6a7b8c9d0e1&startDate=2024-01-01&endDate=2024-03-31&compareWith=previousPeriod" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**cURL - Tat ca events, khong filter ngay:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/dashboard" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**Response thanh cong - khong so sanh (200):**

```json
{
  "data": {
    "totalVideos": 3210,
    "totalViews": 15800000,
    "totalLikes": 420000,
    "totalComments": 98000,
    "totalInfluencers": 350,
    "totalPayment": 185000000,
    "approvedVideos": 2890,
    "pendingVideos": 210,
    "rejectedVideos": 110
  },
  "code": 200
}
```

**Response thanh cong - co so sanh (200):**

```json
{
  "data": {
    "current": {
      "totalVideos": 3210,
      "totalViews": 15800000,
      "totalPayment": 185000000
    },
    "previous": {
      "totalVideos": 2800,
      "totalViews": 12500000,
      "totalPayment": 160000000
    },
    "changes": {
      "totalVideos": 14.64,
      "totalViews": 26.4,
      "totalPayment": 15.63
    }
  },
  "code": 200
}
```

**Test loi:**

```bash
# event ID sai format → 400
curl -X GET "{{ADMIN_BASE_URL}}/analytics/dashboard?event=not-valid-id" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"

# compareWith sai gia tri → 400
curl -X GET "{{ADMIN_BASE_URL}}/analytics/dashboard?compareWith=invalidValue" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

---

### 3. GET /analytics/platforms

**Quyen:** `IsCampaginOwner`

**Mo ta:** Lay phan bo video theo platform (TikTok, YouTube, Facebook, Instagram...). Co the kem theo metrics (views, likes, comments) cho tung platform.

**Query params:**

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|-------|------|----------|-------|-------|
| `event` | string | Khong | ID cua 1 event | `67a1b2c3d4e5f6a7b8c9d0e1` |
| `events` | string | Khong | Nhieu event ID, phan cach dau phay | `67a1b2c3d4e5f6a7b8c9d0e1,67a1b2c3d4e5f6a7b8c9d0e2` |
| `startDate` | string | Khong | Ngay bat dau `YYYY-MM-DD` | `2024-01-01` |
| `endDate` | string | Khong | Ngay ket thuc `YYYY-MM-DD` | `2024-03-31` |
| `withMetrics` | bool | Khong | `true` de kem views/likes/comments theo platform | `true` |

**cURL - Phan bo so luong video:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/platforms?events=67a1b2c3d4e5f6a7b8c9d0e1&startDate=2024-01-01&endDate=2024-03-31" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**cURL - Kem metrics tuong tac:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/platforms?events=67a1b2c3d4e5f6a7b8c9d0e1&startDate=2024-01-01&endDate=2024-03-31&withMetrics=true" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**Response - khong withMetrics (200):**

```json
{
  "data": {
    "platforms": [
      { "platform": "tiktok", "count": 1850, "percentage": 57.6 },
      { "platform": "youtube", "count": 680, "percentage": 21.2 },
      { "platform": "facebook", "count": 420, "percentage": 13.1 },
      { "platform": "instagram", "count": 260, "percentage": 8.1 }
    ],
    "total": 3210
  },
  "code": 200
}
```

**Response - co withMetrics=true (200):**

```json
{
  "data": {
    "platforms": [
      {
        "platform": "tiktok",
        "count": 1850,
        "percentage": 57.6,
        "views": 9800000,
        "likes": 280000,
        "comments": 62000
      },
      {
        "platform": "youtube",
        "count": 680,
        "percentage": 21.2,
        "views": 3200000,
        "likes": 95000,
        "comments": 21000
      }
    ],
    "total": 3210
  },
  "code": 200
}
```

**Test loi:**

```bash
# Event ID sai format → 400
curl -X GET "{{ADMIN_BASE_URL}}/analytics/platforms?event=abc123" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

---

### 4. GET /analytics/creators

**Quyen:** `IsCampaginOwner`

**Mo ta:** Lay danh sach xep hang influencer theo hieu suat. Ho tro phan trang, sap xep va tim kiem.

**Query params:**

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|-------|------|----------|-------|-------|
| `event` | string | Khong | ID cua 1 event | `67a1b2c3d4e5f6a7b8c9d0e1` |
| `events` | string | Khong | Nhieu event ID, phan cach dau phay | `67a1b2c3d4e5f6a7b8c9d0e1,67a1b2c3d4e5f6a7b8c9d0e2` |
| `startDate` | string | Khong | Ngay bat dau `YYYY-MM-DD` | `2024-01-01` |
| `endDate` | string | Khong | Ngay ket thuc `YYYY-MM-DD` | `2024-03-31` |
| `page` | int | Khong | Trang hien tai (mac dinh: 1) | `1` |
| `limit` | int | Khong | So ban ghi/trang (mac dinh: 20, toi da: 100) | `20` |
| `sortBy` | string | Khong | Truong sap xep: `totalViews`, `totalVideos`, `totalPayment`, `totalLikes`, `totalComments` | `totalViews` |
| `sortOrder` | string | Khong | Chieu sap xep: `asc`, `desc` | `desc` |
| `search` | string | Khong | Tim kiem theo ten influencer | `nguyen` |

**cURL - Lay top influencer theo luot xem:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/creators?events=67a1b2c3d4e5f6a7b8c9d0e1&startDate=2024-01-01&endDate=2024-03-31&sortBy=totalViews&sortOrder=desc&page=1&limit=20" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**cURL - Tim kiem influencer theo ten:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/creators?events=67a1b2c3d4e5f6a7b8c9d0e1&search=nguyen&sortBy=totalVideos&sortOrder=desc" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**Response (200):**

```json
{
  "data": {
    "list": [
      {
        "rank": 1,
        "userId": "65f1a2b3c4d5e6f7a8b9c0d1",
        "username": "nguyenthia",
        "displayName": "Nguyen Thi A",
        "totalVideos": 25,
        "totalViews": 2500000,
        "totalLikes": 85000,
        "totalComments": 12000,
        "totalPayment": 12500000,
        "platforms": ["tiktok", "youtube"]
      },
      {
        "rank": 2,
        "userId": "65f1a2b3c4d5e6f7a8b9c0d2",
        "username": "tranthib",
        "displayName": "Tran Thi B",
        "totalVideos": 18,
        "totalViews": 1800000,
        "totalLikes": 62000,
        "totalComments": 9500,
        "totalPayment": 9000000,
        "platforms": ["tiktok"]
      }
    ],
    "total": 350,
    "page": 1,
    "limit": 20
  },
  "code": 200
}
```

**Test loi:**

```bash
# sortBy sai gia tri → 400
curl -X GET "{{ADMIN_BASE_URL}}/analytics/creators?sortBy=invalidField" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"

# sortOrder sai gia tri → 400
curl -X GET "{{ADMIN_BASE_URL}}/analytics/creators?sortOrder=random" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"

# limit vuot toi da → 400
curl -X GET "{{ADMIN_BASE_URL}}/analytics/creators?limit=200" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

---

### 5. GET /analytics/creators/segments

**Quyen:** `IsCampaginOwner`

**Mo ta:** Lay phan loai influencer theo segment (tham gia, khong hoat dong, moi, quay lai).

**Query params:**

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|-------|------|----------|-------|-------|
| `event` | string | Khong | ID cua 1 event | `67a1b2c3d4e5f6a7b8c9d0e1` |
| `events` | string | Khong | Nhieu event ID, phan cach dau phay | `67a1b2c3d4e5f6a7b8c9d0e1,67a1b2c3d4e5f6a7b8c9d0e2` |

> **Luu y:** Endpoint nay khong nhan filter theo ngay.

**cURL:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/creators/segments?events=67a1b2c3d4e5f6a7b8c9d0e1" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**cURL - Tat ca events:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/creators/segments" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**Response (200):**

```json
{
  "data": {
    "participating": {
      "count": 280,
      "percentage": 80.0
    },
    "inactive": {
      "count": 45,
      "percentage": 12.9
    },
    "new": {
      "count": 18,
      "percentage": 5.1
    },
    "returning": {
      "count": 7,
      "percentage": 2.0
    },
    "total": 350
  },
  "code": 200
}
```

**Test loi:**

```bash
# Event ID sai format → 400
curl -X GET "{{ADMIN_BASE_URL}}/analytics/creators/segments?event=not-a-mongo-id" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"

# Nhieu event ID co 1 ID sai format → 400
curl -X GET "{{ADMIN_BASE_URL}}/analytics/creators/segments?events=67a1b2c3d4e5f6a7b8c9d0e1,invalid" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

---

### 6. GET /analytics/approval

**Quyen:** `IsCampaginOwner`

**Mo ta:** Lay thong ke duyet noi dung (tong bai duyet, ty le duyet, tu choi). Co the kem phan bo theo platform.

**Query params:**

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|-------|------|----------|-------|-------|
| `event` | string | Khong | ID cua 1 event | `67a1b2c3d4e5f6a7b8c9d0e1` |
| `events` | string | Khong | Nhieu event ID, phan cach dau phay | `67a1b2c3d4e5f6a7b8c9d0e1,67a1b2c3d4e5f6a7b8c9d0e2` |
| `startDate` | string | Khong | Ngay bat dau `YYYY-MM-DD` | `2024-01-01` |
| `endDate` | string | Khong | Ngay ket thuc `YYYY-MM-DD` | `2024-03-31` |
| `byPlatform` | bool | Khong | `true` de kem phan bo theo platform | `true` |

**cURL - Thong ke tong:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/approval?events=67a1b2c3d4e5f6a7b8c9d0e1&startDate=2024-01-01&endDate=2024-03-31" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**cURL - Kem phan bo theo platform:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/approval?events=67a1b2c3d4e5f6a7b8c9d0e1&startDate=2024-01-01&endDate=2024-03-31&byPlatform=true" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**Response - khong byPlatform (200):**

```json
{
  "data": {
    "total": 3210,
    "approved": 2890,
    "pending": 210,
    "rejected": 110,
    "approvalRate": 90.03,
    "rejectionRate": 3.43,
    "pendingRate": 6.54
  },
  "code": 200
}
```

**Response - co byPlatform=true (200):**

```json
{
  "data": {
    "total": 3210,
    "approved": 2890,
    "pending": 210,
    "rejected": 110,
    "approvalRate": 90.03,
    "byPlatform": [
      {
        "platform": "tiktok",
        "total": 1850,
        "approved": 1680,
        "pending": 110,
        "rejected": 60,
        "approvalRate": 90.81
      },
      {
        "platform": "youtube",
        "total": 680,
        "approved": 620,
        "pending": 40,
        "rejected": 20,
        "approvalRate": 91.18
      }
    ]
  },
  "code": 200
}
```

**Test loi:**

```bash
# Event ID sai format → 400
curl -X GET "{{ADMIN_BASE_URL}}/analytics/approval?event=bad-id" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

---

### 7. GET /analytics/export

**Quyen:** `IsCampaginOwner`

**Mo ta:** Xuat du lieu analytics ra file CSV hoac XLSX. Tra ve file nhi phan de tai xuong.

**Query params:**

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|-------|------|----------|-------|-------|
| `event` | string | Khong | ID cua 1 event | `67a1b2c3d4e5f6a7b8c9d0e1` |
| `events` | string | Khong | Nhieu event ID, phan cach dau phay | `67a1b2c3d4e5f6a7b8c9d0e1,67a1b2c3d4e5f6a7b8c9d0e2` |
| `type` | string | **Co** | Loai du lieu: `creators`, `platforms`, `dashboard` | `creators` |
| `format` | string | **Co** | Dinh dang file: `csv`, `xlsx` | `xlsx` |
| `startDate` | string | Khong | Ngay bat dau `YYYY-MM-DD` | `2024-01-01` |
| `endDate` | string | Khong | Ngay ket thuc `YYYY-MM-DD` | `2024-03-31` |

**cURL - Xuat danh sach influencer ra XLSX:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/export?events=67a1b2c3d4e5f6a7b8c9d0e1&type=creators&format=xlsx&startDate=2024-01-01&endDate=2024-03-31" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  --output creators_export.xlsx
```

**cURL - Xuat platform breakdown ra CSV:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/export?events=67a1b2c3d4e5f6a7b8c9d0e1&type=platforms&format=csv&startDate=2024-01-01&endDate=2024-03-31" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  --output platforms_export.csv
```

**cURL - Xuat dashboard summary ra XLSX:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/export?type=dashboard&format=xlsx&startDate=2024-01-01&endDate=2024-03-31" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  --output dashboard_export.xlsx
```

**Response thanh cong (200):**

```
HTTP/1.1 200 OK
Content-Type: application/octet-stream
Content-Disposition: attachment; filename=creators_2024-01-01_2024-03-31.xlsx
Content-Length: 28672

<binary file data>
```

**Test loi:**

```bash
# Thieu type → 400
curl -X GET "{{ADMIN_BASE_URL}}/analytics/export?format=csv" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"

# Thieu format → 400
curl -X GET "{{ADMIN_BASE_URL}}/analytics/export?type=creators" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"

# type sai gia tri → 400
curl -X GET "{{ADMIN_BASE_URL}}/analytics/export?type=influencers&format=csv" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"

# format sai gia tri → 400
curl -X GET "{{ADMIN_BASE_URL}}/analytics/export?type=creators&format=pdf" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

---

### 8. GET /analytics/trends

**Quyen:** `IsCampaginOwner`

**Mo ta:** Lay du lieu xu huong theo thoi gian (timeline) de ve bieu do. Co the chon period ngan gon hoac truyen ngay cu the.

**Query params:**

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|-------|------|----------|-------|-------|
| `events` | string | Khong | Nhieu event ID, phan cach dau phay | `67a1b2c3d4e5f6a7b8c9d0e1` |
| `period` | string | Bat buoc neu khong co startDate/endDate | Ky du lieu ngan gon: `7d`, `30d`, `90d`, `custom` | `30d` |
| `startDate` | string | Bat buoc neu khong co period | Ngay bat dau (ISO 8601 hoac `YYYY-MM-DD`) | `2024-01-01` |
| `endDate` | string | Bat buoc neu khong co period | Ngay ket thuc (ISO 8601 hoac `YYYY-MM-DD`) | `2024-03-31` |
| `metrics` | string[] | Khong | Cac chi so can lay: `views`, `videos`, `engagement` | `views,videos` |

> **Luu y:** Truyen `period` HOAC (`startDate` + `endDate`). Neu truyen `period=custom` thi phai kem `startDate` va `endDate`.

**cURL - Dung period:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/trends?events=67a1b2c3d4e5f6a7b8c9d0e1&period=30d&metrics=views&metrics=videos" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**cURL - Dung khoang ngay cu the:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/trends?events=67a1b2c3d4e5f6a7b8c9d0e1&startDate=2024-01-01&endDate=2024-03-31&metrics=views&metrics=engagement" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**cURL - Period custom voi ngay:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/trends?events=67a1b2c3d4e5f6a7b8c9d0e1&period=custom&startDate=2024-02-01&endDate=2024-02-29&metrics=views" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**Response (200):**

```json
{
  "data": {
    "points": [
      {
        "date": "2024-01-01",
        "views": 450000,
        "videos": 85,
        "engagement": 18500
      },
      {
        "date": "2024-01-02",
        "views": 520000,
        "videos": 92,
        "engagement": 21000
      },
      {
        "date": "2024-01-03",
        "views": 480000,
        "videos": 78,
        "engagement": 19200
      }
    ],
    "period": "30d",
    "from": "2024-01-01",
    "to": "2024-01-31"
  },
  "code": 200
}
```

**Test loi:**

```bash
# Khong co period va khong co startDate/endDate → 400
curl -X GET "{{ADMIN_BASE_URL}}/analytics/trends?events=67a1b2c3d4e5f6a7b8c9d0e1" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"

# period sai gia tri → 400
curl -X GET "{{ADMIN_BASE_URL}}/analytics/trends?period=1year" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"

# period=custom nhung thieu startDate → 400
curl -X GET "{{ADMIN_BASE_URL}}/analytics/trends?period=custom&endDate=2024-03-31" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

---

### 9. GET /analytics/creator-kpis

**Quyen:** `IsCampaginOwner`

**Mo ta:** Lay KPI chi tiet cua influencer, co the filter theo danh sach user ID cu the.

**Query params:**

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|-------|------|----------|-------|-------|
| `event` | string | Khong | ID cua 1 event | `67a1b2c3d4e5f6a7b8c9d0e1` |
| `events` | string | Khong | Nhieu event ID, phan cach dau phay | `67a1b2c3d4e5f6a7b8c9d0e1,67a1b2c3d4e5f6a7b8c9d0e2` |
| `startDate` | string | Khong | Ngay bat dau `YYYY-MM-DD` | `2024-01-01` |
| `endDate` | string | Khong | Ngay ket thuc `YYYY-MM-DD` | `2024-03-31` |
| `userIds` | string | Khong | Loc theo danh sach user ID, phan cach dau phay | `65f1a2b3c4d5e6f7a8b9c0d1,65f1a2b3c4d5e6f7a8b9c0d2` |

**cURL - KPI tat ca influencer:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/creator-kpis?events=67a1b2c3d4e5f6a7b8c9d0e1&startDate=2024-01-01&endDate=2024-03-31" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**cURL - KPI cua influencer cu the:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/creator-kpis?events=67a1b2c3d4e5f6a7b8c9d0e1&userIds=65f1a2b3c4d5e6f7a8b9c0d1,65f1a2b3c4d5e6f7a8b9c0d2&startDate=2024-01-01&endDate=2024-03-31" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**Response (200):**

```json
{
  "data": {
    "totalInfluencers": 350,
    "activeInfluencers": 280,
    "avgVideosPerInfluencer": 9.17,
    "avgViewsPerInfluencer": 45142.86,
    "avgPaymentPerInfluencer": 528571.43,
    "topPlatform": "tiktok",
    "influencers": [
      {
        "userId": "65f1a2b3c4d5e6f7a8b9c0d1",
        "username": "nguyenthia",
        "totalVideos": 25,
        "totalViews": 2500000,
        "totalPayment": 12500000,
        "avgViewsPerVideo": 100000
      }
    ]
  },
  "code": 200
}
```

**Test loi:**

```bash
# Event ID sai format → 400
curl -X GET "{{ADMIN_BASE_URL}}/analytics/creator-kpis?event=bad" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

---

### 10. GET /analytics/transfers

**Quyen:** `IsCampaginOwner`

**Mo ta:** Lay du lieu chuyen khoan trong khoang thoi gian. Mac dinh tra ve 1 thang gan nhat.

**Query params:**

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|-------|------|----------|-------|-------|
| `startDate` | string | Khong | Ngay bat dau (ISO date) | `2024-01-01` |
| `endDate` | string | Khong | Ngay ket thuc (ISO date) | `2024-03-31` |

> **Luu y:** Thoi gian duoc quy doi sang gio HCM (UTC+7) truoc khi query.

**cURL:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/transfers?startDate=2024-01-01&endDate=2024-03-31" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**cURL - Du lieu 1 thang gan nhat (mac dinh):**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/transfers" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**Response (200):**

```json
{
  "data": {
    "totalTransfers": 1250,
    "totalAmount": 185000000,
    "successfulTransfers": 1220,
    "failedTransfers": 20,
    "pendingTransfers": 10,
    "avgAmountPerTransfer": 148000,
    "transfers": [
      {
        "date": "2024-01-15",
        "count": 45,
        "amount": 6750000,
        "status": "completed"
      },
      {
        "date": "2024-01-16",
        "count": 38,
        "amount": 5700000,
        "status": "completed"
      }
    ]
  },
  "code": 200
}
```

**Test loi:**

```bash
# Thieu token → 401
curl -X GET "{{ADMIN_BASE_URL}}/analytics/transfers?startDate=2024-01-01&endDate=2024-03-31"
```

---

### 11. GET /analytics/campaigns

**Quyen:** `IsCampaginOwner`

**Mo ta:** Lay danh sach thu thach (campaign) duoc loc theo event ID va khoang thoi gian. Dung cho bo loc dropdown tren dashboard.

**Query params:**

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|-------|------|----------|-------|-------|
| `event` | string | Khong | ID cua 1 event (fallback khi khong co `events`) | `67a1b2c3d4e5f6a7b8c9d0e1` |
| `events` | string | Khong | Nhieu event ID, phan cach dau phay | `67a1b2c3d4e5f6a7b8c9d0e1,67a1b2c3d4e5f6a7b8c9d0e2` |
| `startDate` | string | Khong | Ngay bat dau `YYYY-MM-DD` | `2024-01-01` |
| `endDate` | string | Khong | Ngay ket thuc `YYYY-MM-DD` | `2024-03-31` |

> **Luu y:** `events` uu tien hon `event`. Neu khong truyen ca hai, tra tat ca thu thach.

**cURL:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/campaigns?events=67a1b2c3d4e5f6a7b8c9d0e1&startDate=2024-01-01&endDate=2024-03-31" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**cURL - Lay tat ca thu thach:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/campaigns" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**Response (200):**

```json
{
  "data": {
    "campaigns": [
      {
        "id": "65f1a2b3c4d5e6f7a8b9c001",
        "name": "Thu thach mua he 2024",
        "eventId": "67a1b2c3d4e5f6a7b8c9d0e1",
        "startDate": "2024-06-01",
        "endDate": "2024-08-31",
        "status": "active"
      },
      {
        "id": "65f1a2b3c4d5e6f7a8b9c002",
        "name": "Thu thach Tet 2024",
        "eventId": "67a1b2c3d4e5f6a7b8c9d0e1",
        "startDate": "2024-01-01",
        "endDate": "2024-02-15",
        "status": "ended"
      }
    ],
    "total": 2
  },
  "code": 200
}
```

**Test loi:**

```bash
# Event ID sai format → 400
curl -X GET "{{ADMIN_BASE_URL}}/analytics/campaigns?event=not-valid" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"

# Mot trong nhieu event ID sai format → 400
curl -X GET "{{ADMIN_BASE_URL}}/analytics/campaigns?events=67a1b2c3d4e5f6a7b8c9d0e1,not-valid-id" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

---

## Performance

---

### 12. POST /performance/import

**Quyen:** `IsCampaginOwner`

**Mo ta:** Import du lieu performance tu file CSV. Gom 2 buoc: `preview` (xem truoc, khong luu) va `confirm` (xac nhan luu vao database).

**Query params:**

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|-------|------|----------|-------|-------|
| `mode` | string | **Co** | Che do: `preview` hoac `confirm` | `preview` |

**Body:** `multipart/form-data` chua file CSV

| Field | Kieu | Mo ta |
|-------|------|-------|
| `file` | file | File CSV du lieu performance |

**Format CSV mong doi:**

```
date,sourceCode,channel,username,views,likes,comments
2024-01-15,TCBQ1,tiktok,nguyenthia,150000,5200,830
2024-01-15,TCBQ1,youtube,tranthib,85000,3100,450
2024-01-16,TCBQ2,tiktok,levanc,220000,7800,1200
```

**cURL - Buoc 1: Preview (xem truoc):**

```bash
curl -X POST "{{ADMIN_BASE_URL}}/performance/import?mode=preview" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -F "file=@/path/to/performance_data.csv"
```

**cURL - Buoc 2: Confirm (xac nhan luu):**

```bash
curl -X POST "{{ADMIN_BASE_URL}}/performance/import?mode=confirm" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -F "file=@/path/to/performance_data.csv"
```

**Response preview (200):**

```json
{
  "data": {
    "mode": "preview",
    "totalRows": 150,
    "validRows": 148,
    "invalidRows": 2,
    "preview": [
      {
        "row": 1,
        "date": "2024-01-15",
        "sourceCode": "TCBQ1",
        "channel": "tiktok",
        "username": "nguyenthia",
        "views": 150000,
        "likes": 5200,
        "comments": 830,
        "valid": true
      }
    ],
    "errors": [
      {
        "row": 45,
        "message": "Invalid date format"
      },
      {
        "row": 89,
        "message": "Missing sourceCode"
      }
    ]
  },
  "code": 200
}
```

**Response confirm (200):**

```json
{
  "data": {
    "mode": "confirm",
    "batchId": "65f9a8b7c6d5e4f3a2b1c0d9",
    "importedRows": 148,
    "skippedRows": 2,
    "importedAt": "2024-03-20T10:30:00Z"
  },
  "code": 200
}
```

**Test loi:**

```bash
# Thieu mode → 400
curl -X POST "{{ADMIN_BASE_URL}}/performance/import" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -F "file=@/path/to/data.csv"

# mode sai gia tri → 400
curl -X POST "{{ADMIN_BASE_URL}}/performance/import?mode=upload" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -F "file=@/path/to/data.csv"

# Khong co file → 400
curl -X POST "{{ADMIN_BASE_URL}}/performance/import?mode=preview" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

---

### 13. GET /performance/list

**Quyen:** `IsCampaginOwner`

**Mo ta:** Lay danh sach ban ghi performance da import. Ho tro phan trang, loc theo ngay, sourceCode, channel va sap xep.

**Query params:**

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|-------|------|----------|-------|-------|
| `page` | int | Khong | Trang hien tai (mac dinh: 1) | `1` |
| `limit` | int | Khong | So ban ghi/trang (mac dinh: 20, toi da: 100) | `20` |
| `startDate` | string | Khong | Loc tu ngay `YYYY-MM-DD` | `2024-01-01` |
| `endDate` | string | Khong | Loc den ngay `YYYY-MM-DD` | `2024-03-31` |
| `sourceCode` | string | Khong | Loc theo ma nguon | `TCBQ1` |
| `channel` | string | Khong | Loc theo kenh: `tiktok`, `youtube`, `facebook`, `instagram` | `tiktok` |
| `sortBy` | string | Khong | Truong sap xep: `date`, `sourceCode`, `channel`, `username` | `date` |
| `sortOrder` | string | Khong | Chieu sap xep: `asc`, `desc` | `desc` |

**cURL - Lay danh sach:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/performance/list?page=1&limit=20&startDate=2024-01-01&endDate=2024-03-31" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**cURL - Loc theo sourceCode va channel:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/performance/list?sourceCode=TCBQ1&channel=tiktok&sortBy=date&sortOrder=desc" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**Response (200):**

```json
{
  "data": {
    "list": [
      {
        "id": "65f9a8b7c6d5e4f3a2b1c0d1",
        "batchId": "65f9a8b7c6d5e4f3a2b1c0d9",
        "date": "2024-01-15",
        "sourceCode": "TCBQ1",
        "channel": "tiktok",
        "username": "nguyenthia",
        "views": 150000,
        "likes": 5200,
        "comments": 830,
        "importedAt": "2024-03-20T10:30:00Z"
      },
      {
        "id": "65f9a8b7c6d5e4f3a2b1c0d2",
        "batchId": "65f9a8b7c6d5e4f3a2b1c0d9",
        "date": "2024-01-15",
        "sourceCode": "TCBQ1",
        "channel": "youtube",
        "username": "tranthib",
        "views": 85000,
        "likes": 3100,
        "comments": 450,
        "importedAt": "2024-03-20T10:30:00Z"
      }
    ],
    "total": 148,
    "page": 1,
    "limit": 20
  },
  "code": 200
}
```

**Test loi:**

```bash
# startDate sai format → 400
curl -X GET "{{ADMIN_BASE_URL}}/performance/list?startDate=01-01-2024" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"

# limit vuot toi da → 400
curl -X GET "{{ADMIN_BASE_URL}}/performance/list?limit=200" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"

# sortBy sai gia tri → 400
curl -X GET "{{ADMIN_BASE_URL}}/performance/list?sortBy=views" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"

# sortOrder sai gia tri → 400
curl -X GET "{{ADMIN_BASE_URL}}/performance/list?sortOrder=newest" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

---

### 14. GET /performance/batches

**Quyen:** `IsCampaginOwner`

**Mo ta:** Lay lich su cac lan import CSV (danh sach batch). Moi batch la 1 lan import CSV.

**Query params:**

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|-------|------|----------|-------|-------|
| `page` | int | Khong | Trang hien tai (mac dinh: 1) | `1` |
| `limit` | int | Khong | So batch/trang (mac dinh: 20, toi da: 50) | `10` |

**cURL:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/performance/batches?page=1&limit=10" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**Response (200):**

```json
{
  "data": {
    "list": [
      {
        "id": "65f9a8b7c6d5e4f3a2b1c0d9",
        "filename": "performance_q1_2024.csv",
        "importedRows": 148,
        "skippedRows": 2,
        "importedBy": "staff@techcombank.com",
        "importedAt": "2024-03-20T10:30:00Z"
      },
      {
        "id": "65f9a8b7c6d5e4f3a2b1c0e0",
        "filename": "performance_feb_2024.csv",
        "importedRows": 95,
        "skippedRows": 0,
        "importedBy": "staff@techcombank.com",
        "importedAt": "2024-03-01T09:15:00Z"
      }
    ],
    "total": 8,
    "page": 1,
    "limit": 10
  },
  "code": 200
}
```

**Test loi:**

```bash
# limit vuot toi da (50) → 400
curl -X GET "{{ADMIN_BASE_URL}}/performance/batches?limit=100" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

---

### 15. DELETE /performance/batches/:id

**Quyen:** `IsCampaginOwner`

**Mo ta:** Xoa mot batch import va tat ca ban ghi performance thuoc batch do. Hanh dong nay khong the hoan tac.

**Path params:**

| Param | Mo ta | Vi du |
|-------|-------|-------|
| `id` | Batch ID (MongoDB ObjectID) | `65f9a8b7c6d5e4f3a2b1c0d9` |

**cURL:**

```bash
curl -X DELETE "{{ADMIN_BASE_URL}}/performance/batches/65f9a8b7c6d5e4f3a2b1c0d9" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**Response (200):**

```json
{
  "data": {
    "batchId": "65f9a8b7c6d5e4f3a2b1c0d9",
    "deletedRows": 148,
    "deletedAt": "2024-03-20T11:00:00Z"
  },
  "code": 200
}
```

**Test loi:**

```bash
# ID khong ton tai → 400
curl -X DELETE "{{ADMIN_BASE_URL}}/performance/batches/65f9a8b7c6d5e4f3a2b1c099" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"

# ID sai format (khong phai MongoID) → 400
curl -X DELETE "{{ADMIN_BASE_URL}}/performance/batches/not-a-valid-id" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"

# Thieu token → 401
curl -X DELETE "{{ADMIN_BASE_URL}}/performance/batches/65f9a8b7c6d5e4f3a2b1c0d9"
```

---

### 16. GET /analytics/performance/trends

**Quyen:** `IsCampaginOwner`

**Mo ta:** Lay xu huong performance theo thoi gian tu du lieu CSV da import. Co the loc theo sourceCode.

**Query params:**

| Param | Kieu | Bat buoc | Mo ta | Vi du |
|-------|------|----------|-------|-------|
| `startDate` | string | Khong | Ngay bat dau `YYYY-MM-DD` (mac dinh: 30 ngay truoc) | `2024-01-01` |
| `endDate` | string | Khong | Ngay ket thuc `YYYY-MM-DD` (mac dinh: hom nay) | `2024-03-31` |
| `sourceCode` | string | Khong | Loc theo ma nguon | `TCBQ1` |

**cURL - Xu huong toan bo:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/performance/trends?startDate=2024-01-01&endDate=2024-03-31" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**cURL - Xu huong theo sourceCode:**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/performance/trends?startDate=2024-01-01&endDate=2024-03-31&sourceCode=TCBQ1" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**cURL - 30 ngay gan nhat (mac dinh):**

```bash
curl -X GET "{{ADMIN_BASE_URL}}/analytics/performance/trends" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

**Response (200):**

```json
{
  "data": {
    "points": [
      {
        "date": "2024-01-01",
        "totalViews": 450000,
        "totalLikes": 18500,
        "totalComments": 3200,
        "recordCount": 12
      },
      {
        "date": "2024-01-02",
        "totalViews": 520000,
        "totalLikes": 21000,
        "totalComments": 3800,
        "recordCount": 15
      },
      {
        "date": "2024-01-03",
        "totalViews": 390000,
        "totalLikes": 16200,
        "totalComments": 2900,
        "recordCount": 10
      }
    ],
    "summary": {
      "totalViews": 15800000,
      "totalLikes": 620000,
      "totalComments": 98000,
      "totalRecords": 148
    },
    "from": "2024-01-01",
    "to": "2024-03-31",
    "sourceCode": "TCBQ1"
  },
  "code": 200
}
```

**Test loi:**

```bash
# Thieu token → 401
curl -X GET "{{ADMIN_BASE_URL}}/analytics/performance/trends?startDate=2024-01-01&endDate=2024-03-31"

# Token het han / sai → 401
curl -X GET "{{ADMIN_BASE_URL}}/analytics/performance/trends" \
  -H "Authorization: Bearer expired_token_here"
```

---

## Tong hop - Tat ca endpoints

| Method | Endpoint | Handler | Mo ta |
|--------|----------|---------|-------|
| GET | `/analytics/global/dashboard` | `GetGlobalDashboard` | Metrics tong nen tang |
| GET | `/analytics/dashboard` | `GetDashboardKPIs` | KPI dashboard theo event |
| GET | `/analytics/platforms` | `GetPlatformBreakdown` | Phan bo theo platform |
| GET | `/analytics/creators` | `GetCreatorLeaderboard` | Xep hang influencer |
| GET | `/analytics/creators/segments` | `GetCreatorSegments` | Phan khuc influencer |
| GET | `/analytics/approval` | `GetApprovalAnalytics` | Thong ke duyet noi dung |
| GET | `/analytics/export` | `ExportAnalytics` | Xuat file CSV/XLSX |
| GET | `/analytics/trends` | `GetTimelineTrends` | Xu huong theo thoi gian |
| GET | `/analytics/creator-kpis` | `GetCreatorKPIs` | KPI chi tiet influencer |
| GET | `/analytics/transfers` | `GetTransfers` | Du lieu chuyen khoan |
| GET | `/analytics/campaigns` | `GetFilteredCampaigns` | Danh sach thu thach |
| POST | `/performance/import` | `ImportCSV` | Import CSV performance |
| GET | `/performance/list` | `List` | Danh sach ban ghi performance |
| GET | `/performance/batches` | `ListBatches` | Lich su import batch |
| DELETE | `/performance/batches/:id` | `DeleteBatch` | Xoa batch import |
| GET | `/analytics/performance/trends` | `GetTrends` | Xu huong performance |

---

## Luu y chung

### Xu ly Event ID

Tat ca endpoint ho tro bo loc event deu nhan theo thu tu uu tien sau:

1. `events` (chuoi ID phan cach dau phay) — uu tien cao nhat
2. `event` (1 ID don le) — fallback khi khong co `events`
3. Khong truyen ca hai — tra ket qua tat ca events

```bash
# Vi du truyen nhieu event
?events=67a1b2c3d4e5f6a7b8c9d0e1,67a1b2c3d4e5f6a7b8c9d0e2,67a1b2c3d4e5f6a7b8c9d0e3
```

### Format ngay

- Analytics endpoints: chap nhan ca `YYYY-MM-DD` va `YYYY-MM-DDTHH:mm:ssZ`
- Performance endpoints: chi chap nhan `YYYY-MM-DD`
- Mac dinh khi khong truyen: 30 ngay truoc den hom nay

### Quy doi gio

- Cac endpoint `approval` va `transfers` tu dong quy doi sang gio HCM (UTC+7) khi tinh toan dau/cuoi ngay.

### Rate limiting

Analytics endpoints khong co rate limit dac biet, tuy nhien nen tranh goi trong vong lap ngan. Endpoint `export` co the mat vai giay voi du lieu lon.
