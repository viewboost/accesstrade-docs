# API Quick Actions - Tài liệu test API

---

## 1. Danh sách Quick Actions

```
GET {{BASE_URL}}/quick-actions
```

**Headers:**

```
Accept-Language: vi
```

**Query params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| partner | string | Không | Lọc theo partner ID |

> Sắp xếp mặc định: `order` DESC → `_id` ASC

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/quick-actions" \
  -H "Accept-Language: vi"
```

```bash
# Lọc theo partner
curl -X GET "{{BASE_URL}}/quick-actions?partner=techcombank" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": [
    {
      "_id": "qa_001",
      "name": "Tham gia thử thách",
      "logo": {
        "url": "https://cdn.example.com/icons/challenge.png"
      },
      "action": {
        "type": "deeplink",
        "value": "app://events/current"
      },
      "partner": {
        "_id": "partner_001",
        "name": "Techcombank"
      },
      "createdAt": "2025-12-01T00:00:00Z",
      "updatedAt": "2025-12-01T00:00:00Z"
    },
    {
      "_id": "qa_002",
      "name": "Mời bạn bè",
      "logo": {
        "url": "https://cdn.example.com/icons/referral.png"
      },
      "action": {
        "type": "deeplink",
        "value": "app://referral"
      },
      "partner": null,
      "createdAt": "2025-12-01T00:00:00Z",
      "updatedAt": "2025-12-01T00:00:00Z"
    }
  ],
  "code": 200
}
```
