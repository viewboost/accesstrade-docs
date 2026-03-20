# API Partners - Tài liệu test API

Các API liên quan đến Partner. Không yêu cầu đăng nhập.

---

## Danh sách API

| # | Method | Endpoint | Auth | Mô tả | Cache |
|---|--------|----------|------|-------|-------|
| 1 | GET | `/partners` | Không | Danh sách partner | 2 giờ |
| 2 | GET | `/partners/by-slug` | Không | Chi tiết partner theo slug | Không |
| 3 | GET | `/partners/content-features` | Không | Content nổi bật | 4 giờ |
| 4 | GET | `/partners/:id/status-employee` | Không | Trạng thái nhân viên | Không |
| 5 | GET | `/partners/top-influencers` | Không | Top influencer | Không |

---

## 1. Danh sách Partner

```
GET {{BASE_URL}}/partners
```

> Cache: Redis 2 giờ (theo domain)

**Headers:**

```
Accept-Language: vi
```

**Query params:** Không có

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/partners" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": [
    {
      "_id": "partner_001",
      "name": "Techcombank",
      "covers": [
        {
          "url": "https://cdn.example.com/cover.jpg",
          "platform": "web"
        }
      ],
      "logo": {
        "url": "https://cdn.example.com/logo.png"
      },
      "slug": "techcombank",
      "desc": "Ngân hàng TMCP Kỹ Thương Việt Nam",
      "website": "https://example.com",
      "createdAt": "2025-01-01T00:00:00Z",
      "updatedAt": "2025-06-01T00:00:00Z"
    }
  ],
  "allowHeaderPartner": true,
  "code": 200
}
```

---

## 2. Chi tiết Partner theo Slug

```
GET {{BASE_URL}}/partners/by-slug
```

**Headers:**

```
Accept-Language: vi
```

**Query params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| slug | string | **Có** | Slug của partner |
| partner | string | Không | Partner ID |

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/partners/by-slug?slug=techcombank" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": {
    "_id": "partner_001",
    "name": "Techcombank",
    "slug": "techcombank",
    "desc": "...",
    "logo": { "url": "..." },
    "covers": [{ "url": "...", "platform": "web" }],
    "website": "https://example.com",
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-06-01T00:00:00Z"
  },
  "code": 200
}
```

**Test lỗi:**

```bash
# Thiếu slug → 400
curl -X GET "{{BASE_URL}}/partners/by-slug"

# Slug không tồn tại
curl -X GET "{{BASE_URL}}/partners/by-slug?slug=khong-ton-tai"
```

---

## 3. Content nổi bật

```
GET {{BASE_URL}}/partners/content-features
```

> Cache: Redis 4 giờ

**Headers:**

```
Accept-Language: vi
```

**Query params:**

| Tên | Kiểu | Bắt buộc | Default | Mô tả |
|-----|------|----------|---------|-------|
| pageToken | string | Không | — | Token phân trang |
| limit | number | Không | `8` | Số kết quả |
| keyword | string | Không | — | Tìm kiếm |
| sort | string | Không | — | Sắp xếp |
| partner | string | Không | — | Lọc theo partner |
| categories | string | Không | — | Lọc theo danh mục |

> Sắp xếp mặc định: `order` DESC → `statistic.point.total` DESC → `_id` DESC

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/partners/content-features?partner=techcombank&limit=8" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": [
    {
      "_id": "content_001",
      "user": {
        "_id": "user_001",
        "name": "Nguyễn Văn A",
        "avatar": "https://cdn.example.com/avatar.jpg",
        "totalView": 50000
      },
      "title": "Review thẻ Techcombank",
      "desc": "...",
      "cover": "https://img.youtube.com/vi/abc123/maxresdefault.jpg",
      "author": "Nguyễn Văn A",
      "contentId": "abc123",
      "source": "youtube",
      "statistic": {
        "point": { "total": 5000 },
        "pointTotal": { "completed": 5000 }
      },
      "event": "event_001",
      "link": "https://www.youtube.com/watch?v=abc123",
      "status": "approved",
      "reason": "",
      "createdAt": "2026-02-10T08:00:00Z",
      "updatedAt": "2026-03-15T12:00:00Z"
    }
  ],
  "nextPageToken": "",
  "code": 200
}
```

---

## 4. Trạng thái nhân viên

```
GET {{BASE_URL}}/partners/:id/status-employee
```

**Headers:**

```
Accept-Language: vi
```

**Path params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| id | string | **Có** | Partner ID (MongoDB ObjectID) |

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/partners/partner_001/status-employee" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": {
    "isOpenInputStaffCode": true
  },
  "code": 200
}
```

---

## 5. Top Influencer

```
GET {{BASE_URL}}/partners/top-influencers
```

**Headers:**

```
Accept-Language: vi
```

**Query params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| slug | string | Không | Slug của partner |
| partner | string | Không | Partner ID |

> Default limit: 10. Sắp xếp: `contentStatistic.view.completed` DESC → `_id` DESC

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/partners/top-influencers?slug=techcombank" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": [
    {
      "_id": "user_001",
      "name": "Nguyễn Văn A",
      "avatar": {
        "url": "https://cdn.example.com/avatar.jpg"
      },
      "socialInfo": {
        "photo": "https://cdn.example.com/social.jpg",
        "status": "active"
      }
    },
    {
      "_id": "user_002",
      "name": "Trần Thị B",
      "avatar": {
        "url": "https://cdn.example.com/avatar2.jpg"
      },
      "socialInfo": {
        "photo": "https://cdn.example.com/social2.jpg",
        "status": "active"
      }
    }
  ],
  "code": 200
}
```
