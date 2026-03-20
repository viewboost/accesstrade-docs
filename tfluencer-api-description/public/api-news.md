# API News & Articles - Tài liệu test API

Các API tin tức và bài viết. Không yêu cầu đăng nhập.

---

## Danh sách API

| # | Method | Endpoint | Auth | Mô tả | Cache |
|---|--------|----------|------|-------|-------|
| 1 | GET | `/news` | Không | Danh sách tin tức | 2 phút |
| 2 | POST | `/news/:id/analytic-click` | Không | Ghi nhận click tin tức | Không |
| 3 | GET | `/articles/:id` | Không | Chi tiết bài viết | Không |

---

## 1. Danh sách Tin tức

```
GET {{BASE_URL}}/news
```

> Cache: Redis 2 phút

**Headers:**

```
Accept-Language: vi
```

**Query params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| type | string | Không | Lọc theo loại tin |
| status | string | Không | Lọc theo trạng thái |
| partner | string | Không | Lọc theo partner ID |

> Sắp xếp mặc định: `order` DESC → `createdAt` DESC

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/news" \
  -H "Accept-Language: vi"
```

```bash
# Có filter
curl -X GET "{{BASE_URL}}/news?partner=techcombank&type=banner" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "news": [
    {
      "_id": "news_001",
      "title": "Thử thách T-Fluencers Mùa 3 chính thức khởi động",
      "shortDesc": "Tham gia ngay để nhận giải thưởng hấp dẫn...",
      "desc": "Nội dung chi tiết...",
      "photo": {
        "url": "https://cdn.example.com/news/banner1.jpg"
      },
      "photoStretchSize": {
        "url": "https://cdn.example.com/news/banner1-stretch.jpg"
      },
      "actionType": {
        "type": "link",
        "value": "https://example.com/event"
      },
      "type": "banner",
      "contentType": "html",
      "order": 1,
      "startAt": "2026-01-01T00:00:00Z",
      "endAt": "2026-03-31T23:59:59Z",
      "expireAt": null
    }
  ],
  "code": 200
}
```

> **Lưu ý:** Response wrapper là `{"news": [...]}` chứ không phải `{"data": [...]}`.

---

## 2. Ghi nhận Click Tin tức

```
POST {{BASE_URL}}/news/:id/analytic-click
```

Ghi nhận analytics khi user click vào tin tức. Xử lý bất đồng bộ.

**Headers:**

```
Accept-Language: vi
```

**Path params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| id | string | **Có** | News ID (MongoDB ObjectID) |

**Body:** Không cần

**cURL:**

```bash
curl -X POST "{{BASE_URL}}/news/news_001/analytic-click" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "code": 200
}
```

**Test lỗi:**

```bash
# ID sai format → 404
curl -X POST "{{BASE_URL}}/news/invalid-id/analytic-click"
```

---

## 3. Chi tiết Bài viết

```
GET {{BASE_URL}}/articles/:id
```

**Headers:**

```
Accept-Language: vi
```

**Path params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| id | string | **Có** | Article ID (MongoDB ObjectID) |

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/articles/article_001" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": {
    "_id": "article_001",
    "title": "Hướng dẫn tham gia thử thách",
    "shortContent": "Tóm tắt nội dung...",
    "content": "<p>Nội dung HTML chi tiết...</p>",
    "contentType": "html",
    "covers": [
      { "url": "https://cdn.example.com/article/cover.jpg" }
    ],
    "statistic": {
      "view": 1500,
      "share": 120
    },
    "shareURL": "https://example.com/articles/article_001",
    "action": {
      "type": "link",
      "value": "https://example.com"
    },
    "tags": ["guide", "techcombank"],
    "createdAt": "2026-01-15T08:00:00Z",
    "updatedAt": "2026-01-15T08:00:00Z"
  },
  "code": 200
}
```

**Test lỗi:**

```bash
# ID sai format → 404
curl -X GET "{{BASE_URL}}/articles/invalid-id"
```
