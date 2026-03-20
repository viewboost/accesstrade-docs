# API Notifications - Tài liệu test API

Tất cả API thông báo đều **yêu cầu đăng nhập**.

---

## Danh sách API

| # | Method | Endpoint | Auth | Mô tả |
|---|--------|----------|------|-------|
| 1 | GET | `/notifications` | **Bắt buộc** | Danh sách thông báo |
| 2 | GET | `/notifications/:id` | **Bắt buộc** | Đánh dấu đã đọc |

---

## 1. Danh sách Thông báo

```
GET {{BASE_URL}}/notifications
```

> **BẮT BUỘC ĐĂNG NHẬP**

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (BẮT BUỘC)
X-Device-ID: {{DEVICE_ID}}              (BẮT BUỘC)
Accept-Language: vi
```

**Query params:**

| Tên | Kiểu | Bắt buộc | Default | Mô tả |
|-----|------|----------|---------|-------|
| pageToken | string | Không | — | Token phân trang |
| keyword | string | Không | — | Tìm kiếm |
| sort | string | Không | — | Sắp xếp |
| category | string | Không | — | Lọc theo loại |
| partner | string | Không | — | Lọc theo partner |

> Default limit: 20. Sắp xếp mặc định: `updatedAt` DESC

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/notifications?limit=20" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": [
    {
      "_id": "notif_001",
      "title": "Bạn đã nhận được 100,000đ",
      "body": "Video của bạn đã đạt 1,000 lượt xem...",
      "type": "reward",
      "isRead": false,
      "createdAt": "2026-03-18T10:00:00Z",
      "updatedAt": "2026-03-18T10:00:00Z"
    }
  ],
  "nextPageToken": "",
  "code": 200
}
```

**Test lỗi:**

```bash
# Thiếu token → 401
curl -X GET "{{BASE_URL}}/notifications"

# Token nhưng thiếu X-Device-ID → 401
curl -X GET "{{BASE_URL}}/notifications" \
  -H "Authorization: Bearer {{TOKEN}}"
```

---

## 2. Đánh dấu Đã đọc

```
GET {{BASE_URL}}/notifications/:id
```

> **BẮT BUỘC ĐĂNG NHẬP**
>
> Đánh dấu thông báo là đã đọc cho user hiện tại.

**Headers:**

```
Authorization: Bearer {{TOKEN}}          (BẮT BUỘC)
X-Device-ID: {{DEVICE_ID}}              (BẮT BUỘC)
Accept-Language: vi
```

**Path params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| id | string | **Có** | Notification ID (MongoDB ObjectID) |

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/notifications/notif_001" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}" \
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
# Thiếu token → 401
curl -X GET "{{BASE_URL}}/notifications/notif_001"

# ID sai format → 404
curl -X GET "{{BASE_URL}}/notifications/invalid-id" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "X-Device-ID: {{DEVICE_ID}}"
```
