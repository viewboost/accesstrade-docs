# API User Statistic - Tài liệu test API

Các API thống kê user. Không yêu cầu đăng nhập nhưng cần truyền `user` (User ID).

---

## Danh sách API

| # | Method | Endpoint | Auth | Mô tả |
|---|--------|----------|------|-------|
| 1 | GET | `/user-statistic` | Không | Thống kê tổng quan |
| 2 | GET | `/user-statistic/contents` | Không | Danh sách content |
| 3 | GET | `/user-statistic/invitees` | Không | Danh sách người được mời |
| 4 | GET | `/user-statistic/invitees/statistic` | Không | Thống kê người được mời |

---

## Query params chung

Tất cả API trong nhóm này dùng chung bộ query params:

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| partner | string | Không | Partner ID/slug |
| user | string | Không | User ID (hex string) |
| event | string | Không | Event ID |
| fromAt | string | Không | Ngày bắt đầu (ISO date). VD: `2026-01-01` |
| toAt | string | Không | Ngày kết thúc (ISO date). VD: `2026-03-31` |
| isSelf | string | Không | `all` / `true` / `false` |
| page | number | Không | Số trang |
| limit | number | Không | Số kết quả mỗi trang |

---

## 1. Thống kê tổng quan

```
GET {{BASE_URL}}/user-statistic
```

**Headers:**

```
Accept-Language: vi
```

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/user-statistic?user=660a1b2c3d4e5f6a7b8c9d01&partner=techcombank" \
  -H "Accept-Language: vi"
```

```bash
# Với khoảng thời gian
curl -X GET "{{BASE_URL}}/user-statistic?user=660a1b2c3d4e5f6a7b8c9d01&fromAt=2026-01-01&toAt=2026-03-31" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": {
    "totalInvitee": 15,
    "view": {
      "pending": 5000,
      "approved": 150000,
      "cashback": 200000,
      "transfer": 100000
    },
    "comment": {
      "pending": 100,
      "approved": 500
    },
    "like": {
      "pending": 200,
      "approved": 3000
    },
    "cash": {
      "pending": 500000.0,
      "approved": 2000000.0,
      "cashback": 1500000.0,
      "transfer": 1000000.0
    }
  },
  "code": 200
}
```

---

## 2. Danh sách Content

```
GET {{BASE_URL}}/user-statistic/contents
```

**Headers:**

```
Accept-Language: vi
```

> Sắp xếp mặc định: `_id` DESC

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/user-statistic/contents?user=660a1b2c3d4e5f6a7b8c9d01&limit=20" \
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
        "avatar": "https://cdn.example.com/avatar.jpg"
      },
      "title": "Review thẻ Techcombank",
      "desc": "...",
      "cover": "https://img.youtube.com/vi/abc123/maxresdefault.jpg",
      "author": "Nguyễn Văn A",
      "contentId": "abc123",
      "source": "youtube",
      "statisticBase": {
        "view": { "pending": 100, "approved": 5000 },
        "like": { "pending": 10, "approved": 200 },
        "comment": { "pending": 5, "approved": 50 }
      },
      "event": "event_001",
      "link": "https://www.youtube.com/watch?v=abc123",
      "status": "approved",
      "publishedAt": "2026-02-10T08:00:00Z",
      "reason": "",
      "createdAt": "2026-02-10T08:00:00Z",
      "updatedAt": "2026-03-15T12:00:00Z"
    }
  ],
  "code": 200
}
```

---

## 3. Danh sách Người được mời

```
GET {{BASE_URL}}/user-statistic/invitees
```

**Headers:**

```
Accept-Language: vi
```

> Sắp xếp mặc định: `_id` DESC

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/user-statistic/invitees?user=660a1b2c3d4e5f6a7b8c9d01&limit=20" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": [
    {
      "_id": "user_002",
      "name": "Trần Thị B",
      "avatar": "https://cdn.example.com/avatar2.jpg",
      "code": "REF_B123",
      "statistic": {
        "totalInvitee": 3,
        "view": { "approved": 20000 },
        "cash": { "approved": 500000.0 }
      },
      "createdAt": "2026-02-01T10:00:00Z"
    }
  ],
  "code": 200
}
```

---

## 4. Thống kê Người được mời

```
GET {{BASE_URL}}/user-statistic/invitees/statistic
```

**Headers:**

```
Accept-Language: vi
```

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/user-statistic/invitees/statistic?user=660a1b2c3d4e5f6a7b8c9d01" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": {
    "totalInvitee": 15,
    "view": {
      "pending": 2000,
      "approved": 80000,
      "cashback": 50000,
      "transfer": 30000
    },
    "comment": {
      "pending": 50,
      "approved": 300
    },
    "like": {
      "pending": 100,
      "approved": 1500
    },
    "cash": {
      "pending": 200000.0,
      "approved": 1000000.0,
      "cashback": 800000.0,
      "transfer": 500000.0
    }
  },
  "code": 200
}
```
