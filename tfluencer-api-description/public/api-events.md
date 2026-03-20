# API Events - Tài liệu test API

## Thông tin chung

| Mục | Giá trị |
|-----|---------|
| Base URL | `{{BASE_URL}}/events` |
| Content-Type | `application/json` |

> Thay `{{BASE_URL}}` bằng URL server thực tế. VD: `https://api.viewboost.vn`

---

## Headers

### Headers bắt buộc

| Header | Giá trị | Khi nào cần |
|--------|---------|-------------|
| `Authorization` | `Bearer {{TOKEN}}` | Các API yêu cầu đăng nhập (xem bảng bên dưới) |
| `X-Device-ID` | `{{DEVICE_ID}}` | **Luôn gửi kèm** khi có `Authorization`. Device ID phải khớp với `deviceId` trong JWT token, nếu không sẽ bị **401** |
| `Content-Type` | `application/json` | Các API method POST/PUT |

### Headers tuỳ chọn

| Header | Giá trị mẫu | Mô tả |
|--------|-------------|-------|
| `Accept-Language` | `vi` hoặc `en` | Ngôn ngữ response. Mặc định `vi` nếu không gửi |
| `App-Version` | `1.0.0` | Phiên bản app |
| `OS-NAME` | `web` / `ios` / `android` | Hệ điều hành |
| `OS-VERSION` | `16.0` | Phiên bản OS |
| `PLATFORM` | `web` / `mobile` | Nền tảng |
| `Device-Model` | `iPhone 15 Pro` | Model thiết bị |
| `Browser-Name` | `Chrome` | Tên trình duyệt |
| `Browser-Version` | `120.0` | Phiên bản trình duyệt |
| `Fcm-Token` | `firebase_token_xxx` | Firebase Cloud Messaging token |
| `Source` | `web` | Nguồn request |

### Cơ chế xác thực (Authentication)

1. Middleware `Auth` chạy trên **tất cả** route
2. Nếu **không có** header `Authorization` → request vẫn đi qua, nhưng không có thông tin user
3. Nếu **có** header `Authorization`:
   - Parse JWT token (bỏ prefix `Bearer `)
   - Kiểm tra token hợp lệ, chưa hết hạn
   - Lấy `deviceId` từ claims trong token → so sánh với header `X-Device-ID` → **phải khớp**
   - Kiểm tra token có trong Redis cache (`user_token:{userId}:{deviceId}:{token}`)
   - Nếu bất kỳ bước nào fail → **401 Unauthorized**
4. Route có middleware `RequiredLogin` → user **phải** đăng nhập, nếu không → **401**

---

## Response format

**Thành công (200):**

```json
{
  "data": { ... },
  "code": 200
}
```

Với API có phân trang:

```json
{
  "data": [ ... ],
  "nextPageToken": "base64_encoded_string",
  "code": 200
}
```

**Lỗi:**

```json
{
  "data": null,
  "message": "Mô tả lỗi",
  "code": 400
}
```

| HTTP Status | Ý nghĩa |
|-------------|----------|
| `200` | Thành công |
| `400` | Thiếu param, validation lỗi, dữ liệu không hợp lệ |
| `401` | Thiếu token, token hết hạn, `X-Device-ID` không khớp |
| `404` | ID sai format ObjectID, resource không tồn tại |
| `429` | Rate limit (quá nhiều request) |

---

## Danh sách API

| # | Method | Endpoint | Auth | Mô tả |
|---|--------|----------|------|-------|
| 1 | GET | `/events` | Không bắt buộc | Danh sách event |
| 2 | GET | `/events/user-newest` | Không bắt buộc | User mới tham gia event |
| 3 | GET | `/events/statistic` | Không bắt buộc | Thống kê event |
| 4 | GET | `/events/current` | Không bắt buộc | Event đang active |
| 5 | GET | `/events/by-slug` | Không bắt buộc | Event theo slug |
| 6 | GET | `/events/:id/leaderboards` | Không bắt buộc | Bảng xếp hạng user |
| 7 | GET | `/events/:id/content` | Không bắt buộc | Danh sách content |
| 8 | GET | `/events/:id/content/leaderboards` | Không bắt buộc | Bảng xếp hạng content |
| 9 | GET | `/events/:id/schemas` | Không bắt buộc | Schema/milestone |
| 10 | GET | `/events/:id/content/me` | **Bắt buộc** | Content của tôi |
| 11 | POST | `/events/:id/input-code-join-event` | **Bắt buộc** | Nhập code tham gia |
| 12 | POST | `/events/:id/content` | **Bắt buộc** | Submit content mới |

---

## 1. Lấy danh sách Event

```
GET {{BASE_URL}}/events
```

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (không bắt buộc)
X-Device-ID: {{DEVICE_ID}}              (không bắt buộc)
Accept-Language: vi                      (không bắt buộc, mặc định vi)
```

**Query params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| pageToken | string | Không | Token phân trang, lấy từ `nextPageToken` của response trước |
| limit | number | Không | Số event trả về. VD: `10` |
| keyword | string | Không | Tìm kiếm theo tên event |
| sort | string | Không | Sắp xếp |
| partner | string | Không | Lọc theo partner ID |
| categories | string | Không | Lọc theo danh mục |

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/events?limit=10" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": [
    {
      "_id": "6501abcd1234567890ef0001",
      "type": "challenge",
      "name": "Thử thách T-Fluencers Mùa 3",
      "covers": ["https://cdn.example.com/cover1.jpg"],
      "tags": ["techcombank", "tfluencers"],
      "slug": "thu-thach-t-fluencers-mua-3",
      "desc": "Mô tả thử thách...",
      "guide": "Hướng dẫn tham gia...",
      "options": {
        "maxContentPerDay": 5,
        "applyForSources": ["youtube", "tiktok", "facebook"],
        "hashtags": ["#TFluencers", "#Techcombank"],
        "applyForStaff": false
      },
      "privacy": "public",
      "startAt": "2026-01-01T00:00:00Z",
      "endAt": "2026-03-31T23:59:59Z",
      "isRequireCode": false,
      "isApplyForAll": true,
      "icon": "https://cdn.example.com/icon.png",
      "code": "",
      "displayStartAt": "2026-01-01T00:00:00Z",
      "displayEndAt": "2026-03-31T23:59:59Z",
      "status": "active",
      "contents": [],
      "order": 1,
      "userStatistic": {},
      "userEventStatistic": {},
      "lastUpdatedAt": "2026-03-15T10:30:00Z",
      "videos": [],
      "reward": "Tổng giải thưởng 500 triệu",
      "isCanSubmit": true,
      "statisticBudget": {},
      "isMaxBudget": false,
      "totalUserWithContent": 150,
      "createdAt": "2025-12-15T08:00:00Z",
      "updatedAt": "2026-03-15T10:30:00Z"
    }
  ],
  "nextPageToken": "eyJsYXN0SWQiOiI2NTAxYWJjZDEyMzQ1Njc4OTBlZjAwMDEifQ==",
  "code": 200
}
```

**Lấy trang tiếp theo:**

```bash
curl -X GET "{{BASE_URL}}/events?limit=10&pageToken=eyJsYXN0SWQiOiI2NTAxYWJjZDEyMzQ1Njc4OTBlZjAwMDEifQ==" \
  -H "Accept-Language: vi"
```

---

## 2. User mới tham gia Event

```
GET {{BASE_URL}}/events/user-newest
```

> Cache: Redis 60 giây

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (không bắt buộc)
X-Device-ID: {{DEVICE_ID}}              (không bắt buộc)
Accept-Language: vi
```

**Query params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| event | string | **Có** | Event ID |
| partner | string | Không | Partner ID |

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/events/user-newest?event=6501abcd1234567890ef0001" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": [
    {
      "_id": "660a1b2c3d4e5f6a7b8c9d01",
      "name": "Nguyễn Văn A",
      "avatar": "https://cdn.example.com/avatar/user1.jpg",
      "socialInfo": {
        "youtube": { "id": "UC123", "name": "NguyenVanA Channel" }
      },
      "totalView": 25000
    },
    {
      "_id": "660a1b2c3d4e5f6a7b8c9d02",
      "name": "Trần Thị B",
      "avatar": "https://cdn.example.com/avatar/user2.jpg",
      "socialInfo": {
        "tiktok": { "id": "user123", "name": "@tranthib" }
      },
      "totalView": 18500
    }
  ],
  "code": 200
}
```

**Test lỗi:**

```bash
# Thiếu event → 400
curl -X GET "{{BASE_URL}}/events/user-newest"
```

---

## 3. Thống kê Event

```
GET {{BASE_URL}}/events/statistic
```

> Cache: Redis 30 giây

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (không bắt buộc)
X-Device-ID: {{DEVICE_ID}}              (không bắt buộc)
Accept-Language: vi
```

**Query params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| event | string | **Có** | Event ID |
| partner | string | Không | Partner ID |

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/events/statistic?event=6501abcd1234567890ef0001" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": {
    "totalView": 1500000,
    "totalContent": 320,
    "totalCommission": 50000000.0,
    "totalEventActive": 3,
    "totalUserWithContent": 85
  },
  "code": 200
}
```

---

## 4. Event hiện tại (trang chủ)

```
GET {{BASE_URL}}/events/current
```

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (không bắt buộc)
X-Device-ID: {{DEVICE_ID}}              (không bắt buộc)
Accept-Language: vi
```

**Query params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| partner | string | Không | Partner ID hoặc domain |

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/events/current" \
  -H "Accept-Language: vi"
```

```bash
# Có partner
curl -X GET "{{BASE_URL}}/events/current?partner=techcombank" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}"
```

**Response 200:**

```json
{
  "data": {
    "_id": "6501abcd1234567890ef0001",
    "type": "challenge",
    "name": "Thử thách T-Fluencers Mùa 3",
    "covers": ["https://cdn.example.com/cover1.jpg"],
    "tags": ["techcombank"],
    "slug": "thu-thach-t-fluencers-mua-3",
    "desc": "Mô tả event...",
    "guide": "Hướng dẫn...",
    "isRequireCode": false,
    "privacy": "public",
    "guideContent": {
      "title": "Hướng dẫn tham gia",
      "body": "<p>Nội dung HTML hướng dẫn...</p>"
    },
    "privacyContent": {
      "title": "Chính sách bảo mật",
      "body": "<p>Nội dung HTML chính sách...</p>"
    },
    "startAt": "2026-01-01T00:00:00Z",
    "endAt": "2026-03-31T23:59:59Z",
    "options": {
      "maxContentPerDay": 5,
      "applyForSources": ["youtube", "tiktok"],
      "hashtags": ["#TFluencers"],
      "applyForStaff": false
    },
    "isApplyForAll": true,
    "icon": "https://cdn.example.com/icon.png",
    "eventOthers": [
      {
        "_id": "6501abcd1234567890ef0002",
        "name": "Thử thách Mùa 2",
        "slug": "thu-thach-mua-2"
      }
    ],
    "code": "",
    "displayStartAt": "2026-01-01T00:00:00Z",
    "displayEndAt": "2026-03-31T23:59:59Z",
    "status": "active",
    "userStatistic": {},
    "userEventStatistic": {},
    "lastUpdatedAt": "2026-03-15T10:30:00Z",
    "contents": [],
    "order": 1,
    "videos": [],
    "reward": "Tổng giải thưởng 500 triệu",
    "isCanSubmit": true,
    "statisticBudget": {},
    "categories": [
      { "_id": "cat001", "name": "Finance" }
    ],
    "createdAt": "2025-12-15T08:00:00Z",
    "updatedAt": "2026-03-15T10:30:00Z"
  },
  "code": 200
}
```

---

## 5. Lấy Event theo Slug

```
GET {{BASE_URL}}/events/by-slug
```

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (không bắt buộc)
X-Device-ID: {{DEVICE_ID}}              (không bắt buộc)
Accept-Language: vi
```

**Query params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| slug | string | **Có** | Slug URL-friendly của event |
| partner | string | Không | Partner ID |

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/events/by-slug?slug=thu-thach-t-fluencers-mua-3" \
  -H "Accept-Language: vi"
```

**Response 200:** Giống response [API #4](#4-event-hiện-tại-trang-chủ).

**Test lỗi:**

```bash
# Thiếu slug → 400
curl -X GET "{{BASE_URL}}/events/by-slug"

# Slug không tồn tại → data: null
curl -X GET "{{BASE_URL}}/events/by-slug?slug=khong-ton-tai-abc"
```

---

## 6. Bảng xếp hạng User

```
GET {{BASE_URL}}/events/:id/leaderboards
```

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (không bắt buộc)
X-Device-ID: {{DEVICE_ID}}              (không bắt buộc)
Accept-Language: vi
```

**Path params:**

| Tên | Kiểu | Bắt buộc | Validation |
|-----|------|----------|------------|
| id | string | **Có** | MongoDB ObjectID (24 ký tự hex). VD: `6501abcd1234567890ef0001` |

**Query params:**

| Tên | Kiểu | Bắt buộc | Default | Mô tả |
|-----|------|----------|---------|-------|
| pageToken | string | Không | — | Token phân trang |
| limit | number | Không | `10` | Số kết quả mỗi trang |
| keyword | string | Không | — | Tìm kiếm theo tên user |
| sort | string | Không | — | Sắp xếp |
| partner | string | Không | — | Partner filter |
| categories | string | Không | — | Category filter |

> Sắp xếp mặc định: `statistic.pointTotal.completed` DESC → `_id` DESC

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/events/6501abcd1234567890ef0001/leaderboards?limit=20" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": [
    {
      "_id": "ue_001",
      "user": {
        "_id": "660a1b2c3d4e5f6a7b8c9d01",
        "name": "Nguyễn Văn A",
        "avatar": "https://cdn.example.com/avatar/user1.jpg"
      },
      "event": "6501abcd1234567890ef0001",
      "eventType": "challenge",
      "statistic": {
        "pointTotal": {
          "completed": 15000
        },
        "totalView": 500000,
        "totalContent": 8
      },
      "createdAt": "2026-01-05T09:00:00Z",
      "updatedAt": "2026-03-18T14:30:00Z"
    }
  ],
  "totalVideo": 320,
  "nextPageToken": "eyJsYXN0SWQiOiJ1ZV8wMDIifQ==",
  "code": 200
}
```

**Test lỗi:**

```bash
# ID sai format → 404
curl -X GET "{{BASE_URL}}/events/invalid-id/leaderboards"

# ID đúng format nhưng không tồn tại → data: []
curl -X GET "{{BASE_URL}}/events/000000000000000000000000/leaderboards"
```

---

## 7. Danh sách Content của Event

```
GET {{BASE_URL}}/events/:id/content
```

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (không bắt buộc)
X-Device-ID: {{DEVICE_ID}}              (không bắt buộc)
Accept-Language: vi
```

**Path params:**

| Tên | Kiểu | Bắt buộc | Validation |
|-----|------|----------|------------|
| id | string | **Có** | MongoDB ObjectID (24 ký tự hex) |

**Query params:**

| Tên | Kiểu | Bắt buộc | Default | Mô tả |
|-----|------|----------|---------|-------|
| pageToken | string | Không | — | Token phân trang |
| limit | number | Không | `20` | Số kết quả mỗi trang |
| keyword | string | Không | — | Tìm kiếm |
| sort | string | Không | — | Sắp xếp |
| partner | string | Không | — | Partner filter |
| categories | string | Không | — | Category filter |

> Sắp xếp mặc định: `order` DESC → `statistic.point.total` DESC → `_id` DESC

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/events/6501abcd1234567890ef0001/content?limit=20" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": [
    {
      "_id": "content_001",
      "user": {
        "_id": "660a1b2c3d4e5f6a7b8c9d01",
        "name": "Nguyễn Văn A",
        "avatar": "https://cdn.example.com/avatar/user1.jpg"
      },
      "title": "Review thẻ Techcombank Visa Signature",
      "desc": "Video review chi tiết...",
      "cover": "https://img.youtube.com/vi/abc123/maxresdefault.jpg",
      "author": "Nguyễn Văn A",
      "contentId": "abc123xyz",
      "source": "youtube",
      "statistic": {
        "point": { "total": 5000 },
        "pointTotal": { "completed": 5000 }
      },
      "event": "6501abcd1234567890ef0001",
      "link": "https://www.youtube.com/watch?v=abc123xyz",
      "status": "approved",
      "reason": "",
      "createdAt": "2026-02-10T08:00:00Z",
      "updatedAt": "2026-03-15T12:00:00Z"
    },
    {
      "_id": "content_002",
      "user": {
        "_id": "660a1b2c3d4e5f6a7b8c9d02",
        "name": "Trần Thị B",
        "avatar": "https://cdn.example.com/avatar/user2.jpg"
      },
      "title": "TikTok: Mở thẻ Techcombank siêu dễ",
      "desc": "",
      "cover": "https://cdn.example.com/tiktok-cover.jpg",
      "author": "Trần Thị B",
      "contentId": "7123456789012345678",
      "source": "tiktok",
      "statistic": {
        "point": { "total": 3200 },
        "pointTotal": { "completed": 3200 }
      },
      "event": "6501abcd1234567890ef0001",
      "link": "https://www.tiktok.com/@tranthib/video/7123456789012345678",
      "status": "approved",
      "reason": "",
      "createdAt": "2026-02-12T14:30:00Z",
      "updatedAt": "2026-03-14T09:00:00Z"
    }
  ],
  "nextPageToken": "eyJsYXN0SWQiOiJjb250ZW50XzAwMiJ9",
  "code": 200
}
```

---

## 8. Bảng xếp hạng Content

```
GET {{BASE_URL}}/events/:id/content/leaderboards
```

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (không bắt buộc)
X-Device-ID: {{DEVICE_ID}}              (không bắt buộc)
Accept-Language: vi
```

**Path params:**

| Tên | Kiểu | Bắt buộc | Validation |
|-----|------|----------|------------|
| id | string | **Có** | MongoDB ObjectID (24 ký tự hex) |

**Query params:** Giống [API #7](#7-danh-sách-content-của-event) (limit mặc định `20`)

> Sắp xếp mặc định: `statistic.pointTotal.completed` DESC → `_id` DESC

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/events/6501abcd1234567890ef0001/content/leaderboards?limit=10" \
  -H "Accept-Language: vi"
```

**Response 200:** Cấu trúc giống [API #7](#7-danh-sách-content-của-event), sắp xếp theo điểm cao nhất.

---

## 9. Danh sách Schema / Milestone

```
GET {{BASE_URL}}/events/:id/schemas
```

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (không bắt buộc)
X-Device-ID: {{DEVICE_ID}}              (không bắt buộc)
Accept-Language: vi
```

**Path params:**

| Tên | Kiểu | Bắt buộc | Validation |
|-----|------|----------|------------|
| id | string | **Có** | MongoDB ObjectID (24 ký tự hex) |

**Query params:** Không có

> Sắp xếp mặc định: `order` DESC → `_id` ASC

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/events/6501abcd1234567890ef0001/schemas" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": [
    {
      "_id": "schema_001",
      "title": "Đạt 1,000 lượt xem",
      "desc": "Video cần đạt 1,000 lượt xem trong 7 ngày",
      "status": "active",
      "type": "milestone",
      "startAt": "2026-01-01T00:00:00Z",
      "endAt": "2026-03-31T23:59:59Z",
      "event": "6501abcd1234567890ef0001",
      "applyForSources": ["youtube", "tiktok", "facebook"],
      "cashReward": {
        "amount": 100000,
        "currency": "VND"
      },
      "milestone": {
        "target": 1000,
        "type": "views"
      },
      "isPass": false,
      "completedAt": null,
      "order": 1,
      "createdAt": "2025-12-20T08:00:00Z",
      "updatedAt": "2025-12-20T08:00:00Z"
    },
    {
      "_id": "schema_002",
      "title": "Đạt 10,000 lượt xem",
      "desc": "Video cần đạt 10,000 lượt xem",
      "status": "active",
      "type": "milestone",
      "startAt": "2026-01-01T00:00:00Z",
      "endAt": "2026-03-31T23:59:59Z",
      "event": "6501abcd1234567890ef0001",
      "applyForSources": ["youtube", "tiktok"],
      "cashReward": {
        "amount": 500000,
        "currency": "VND"
      },
      "milestone": {
        "target": 10000,
        "type": "views"
      },
      "isPass": false,
      "completedAt": null,
      "order": 2,
      "createdAt": "2025-12-20T08:00:00Z",
      "updatedAt": "2025-12-20T08:00:00Z"
    }
  ],
  "code": 200
}
```

---

## 10. Content của tôi

```
GET {{BASE_URL}}/events/:id/content/me
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (BẮT BUỘC)
X-Device-ID: {{DEVICE_ID}}              (BẮT BUỘC - phải khớp deviceId trong token)
Accept-Language: vi
```

**Path params:**

| Tên | Kiểu | Bắt buộc | Validation |
|-----|------|----------|------------|
| id | string | **Có** | MongoDB ObjectID (24 ký tự hex) |

**Query params:**

| Tên | Kiểu | Bắt buộc | Default | Mô tả |
|-----|------|----------|---------|-------|
| pageToken | string | Không | — | Token phân trang |
| limit | number | Không | `20` | Số kết quả mỗi trang |
| keyword | string | Không | — | Tìm kiếm |
| sort | string | Không | — | Sắp xếp |
| partner | string | Không | — | Partner filter |
| categories | string | Không | — | Category filter |

> Sắp xếp mặc định: `createdAt` DESC → `_id` DESC
>
> Chỉ trả về content của user đang đăng nhập.

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/events/6501abcd1234567890ef0001/content/me?limit=10" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Accept-Language: vi"
```

**Response 200:** Cấu trúc giống [API #7](#7-danh-sách-content-của-event), chỉ chứa content của user hiện tại.

**Test lỗi:**

```bash
# Thiếu token → 401
curl -X GET "{{BASE_URL}}/events/6501abcd1234567890ef0001/content/me"

# Có token nhưng thiếu X-Device-ID → 401
curl -X GET "{{BASE_URL}}/events/6501abcd1234567890ef0001/content/me" \
  -H "Authorization: Bearer {{TOKEN}}"

# Có token nhưng X-Device-ID sai → 401
curl -X GET "{{BASE_URL}}/events/6501abcd1234567890ef0001/content/me" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: wrong-device-id"
```

---

## 11. Nhập code tham gia Event

```
POST {{BASE_URL}}/events/:id/input-code-join-event
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (BẮT BUỘC)
X-Device-ID: {{DEVICE_ID}}              (BẮT BUỘC)
Content-Type: application/json
Accept-Language: vi
```

**Path params:**

| Tên | Kiểu | Bắt buộc | Validation |
|-----|------|----------|------------|
| id | string | **Có** | MongoDB ObjectID (24 ký tự hex) |

**Body:**

```json
{
  "code": "STAFF2024"
}
```

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| code | string | **Có** | Mã staff để tham gia event. Không được rỗng |

**Validation:**
- `code` không được rỗng
- Event phải tồn tại và đang active (trong khoảng `startAt` → `endAt`)
- `code` phải khớp với 1 trong các staff code của event

**cURL:**

```bash
curl -X POST "{{BASE_URL}}/events/6501abcd1234567890ef0001/input-code-join-event" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -H "Accept-Language: vi" \
  -d '{"code": "STAFF2024"}'
```

**Response 200 (thành công):**

```json
{
  "data": null,
  "code": 200
}
```

**Test lỗi:**

```bash
# Thiếu token → 401
curl -X POST "{{BASE_URL}}/events/6501abcd1234567890ef0001/input-code-join-event" \
  -H "Content-Type: application/json" \
  -d '{"code": "STAFF2024"}'

# Code rỗng → 400
curl -X POST "{{BASE_URL}}/events/6501abcd1234567890ef0001/input-code-join-event" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{"code": ""}'

# Code sai → 400
curl -X POST "{{BASE_URL}}/events/6501abcd1234567890ef0001/input-code-join-event" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{"code": "WRONG_CODE"}'

# Event ID sai format → 404
curl -X POST "{{BASE_URL}}/events/invalid-id/input-code-join-event" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{"code": "STAFF2024"}'
```

---

## 12. Submit Content mới

```
POST {{BASE_URL}}/events/:id/content
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (BẮT BUỘC)
X-Device-ID: {{DEVICE_ID}}              (BẮT BUỘC)
Content-Type: application/json
Accept-Language: vi
```

**Path params:**

| Tên | Kiểu | Bắt buộc | Validation |
|-----|------|----------|------------|
| id | string | **Có** | MongoDB ObjectID (24 ký tự hex) |

**Body:**

```json
{
  "url": "https://www.youtube.com/watch?v=abc123xyz",
  "hashTag": "#TFluencers",
  "source": "youtube",
  "userSocialId": "UC1234567890abcdef"
}
```

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| url | string | **Có** | URL video/bài đăng. Phải là URL hợp lệ |
| hashTag | string | Không | Hashtag |
| source | string | Không | Nguồn nội dung (xem bảng bên dưới) |
| userSocialId | string | **Có** | ID tài khoản mạng xã hội đã liên kết |

**Giá trị `source` hợp lệ:**

| source | Nền tảng | URL mẫu hợp lệ |
|--------|----------|-----------------|
| `youtube` | YouTube (video thường, KHÔNG phải Shorts) | `https://www.youtube.com/watch?v=abc123` |
| `youtubeShorts` | YouTube Shorts | `https://www.youtube.com/shorts/abc123` |
| `tiktok` | TikTok | `https://www.tiktok.com/@user/video/7123456789` |
| `facebook` | Facebook (bài đăng) | `https://www.facebook.com/user/posts/123456` |
| `facebookReels` | Facebook Reels | `https://www.facebook.com/reel/123456` |
| `instagram` | Instagram (bài đăng, KHÔNG phải Reels) | `https://www.instagram.com/p/ABC123/` |
| `instagramReels` | Instagram Reels | `https://www.instagram.com/reel/ABC123/` |

**Validation:**
- `url` phải hợp lệ và **khớp** với `source` (VD: gửi YouTube URL thì source phải là `youtube`)
- `userSocialId` bắt buộc — user phải đã liên kết tài khoản social tương ứng
- Event phải đang active, chưa bị block submit, chưa vượt budget
- User chưa vượt giới hạn content/ngày (nếu event có `maxContentPerDay`)
- `source` phải nằm trong `applyForSources` của event (nếu event có cấu hình)
- Nếu event `isRequireCode = true` → user phải đã nhập staff code trước
- Nếu event `applyForStaff = true` → user phải là staff

**cURL — YouTube video:**

```bash
curl -X POST "{{BASE_URL}}/events/6501abcd1234567890ef0001/content" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -H "Accept-Language: vi" \
  -d '{
    "url": "https://www.youtube.com/watch?v=abc123xyz",
    "hashTag": "#TFluencers",
    "source": "youtube",
    "userSocialId": "UC1234567890abcdef"
  }'
```

**cURL — TikTok:**

```bash
curl -X POST "{{BASE_URL}}/events/6501abcd1234567890ef0001/content" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.tiktok.com/@myuser/video/7123456789012345678",
    "hashTag": "#TFluencers",
    "source": "tiktok",
    "userSocialId": "myuser_tiktok_id"
  }'
```

**cURL — Facebook Reels:**

```bash
curl -X POST "{{BASE_URL}}/events/6501abcd1234567890ef0001/content" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.facebook.com/reel/123456789",
    "source": "facebookReels",
    "userSocialId": "fb_user_id_123"
  }'
```

**Response 200 (thành công):**

```json
{
  "data": {},
  "code": 200
}
```

**Test lỗi:**

```bash
# Thiếu token → 401
curl -X POST "{{BASE_URL}}/events/6501abcd1234567890ef0001/content" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=abc123", "source": "youtube", "userSocialId": "UC123"}'

# Thiếu X-Device-ID khi có token → 401
curl -X POST "{{BASE_URL}}/events/6501abcd1234567890ef0001/content" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=abc123", "source": "youtube", "userSocialId": "UC123"}'

# URL không hợp lệ → 400
curl -X POST "{{BASE_URL}}/events/6501abcd1234567890ef0001/content" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{"url": "not-a-url", "source": "youtube", "userSocialId": "UC123"}'

# URL không khớp source (YouTube URL nhưng khai tiktok) → 400
curl -X POST "{{BASE_URL}}/events/6501abcd1234567890ef0001/content" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=abc123", "source": "tiktok", "userSocialId": "UC123"}'

# Thiếu userSocialId → 400
curl -X POST "{{BASE_URL}}/events/6501abcd1234567890ef0001/content" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=abc123", "source": "youtube"}'

# YouTube Shorts URL nhưng source là youtube (phải là youtubeShorts) → 400
curl -X POST "{{BASE_URL}}/events/6501abcd1234567890ef0001/content" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/shorts/abc123", "source": "youtube", "userSocialId": "UC123"}'

# Event ID sai format → 404
curl -X POST "{{BASE_URL}}/events/invalid-id/content" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=abc123", "source": "youtube", "userSocialId": "UC123"}'
```

---

## Biến môi trường (Postman / Thunder Client)

Tạo các biến sau trong environment:

| Biến | Mô tả | Ví dụ |
|------|-------|-------|
| `{{BASE_URL}}` | URL server | `https://api.viewboost.vn` |
| `{{TOKEN}}` | JWT token (lấy sau khi gọi API login) | `eyJhbGciOiJIUzI1NiIs...` |
| `{{DEVICE_ID}}` | Device ID (phải khớp với `deviceId` trong token) | `device-abc-123-xyz` |
| `{{EVENT_ID}}` | ID event đang test | `6501abcd1234567890ef0001` |

### Cách lấy token để test

Gọi API login trước:

```bash
curl -X POST "{{BASE_URL}}/users/login" \
  -H "Content-Type: application/json" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -d '{
    "email": "test@example.com",
    "password": "your_password"
  }'
```

Response sẽ chứa `token` → copy vào biến `{{TOKEN}}`.

> **Lưu ý:** `X-Device-ID` gửi khi login phải giống `X-Device-ID` gửi ở tất cả request sau đó. Nếu khác → 401.
