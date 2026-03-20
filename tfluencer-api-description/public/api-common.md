# API Common - Tài liệu test API

Các API công khai, không yêu cầu đăng nhập.

---

## Danh sách API

| # | Method | Endpoint | Auth | Mô tả |
|---|--------|----------|------|-------|
| 1 | GET | `/ping` | Không | Health check |
| 2 | GET | `/health` | Không | Health check |
| 3 | GET | `/app-data` | Không | Cấu hình app |
| 4 | GET | `/bank` | Không | Danh sách ngân hàng |
| 5 | GET | `/bank/:id/branch` | Không | Chi nhánh ngân hàng |
| 6 | GET | `/countries` | Không | Danh sách quốc gia |
| 7 | GET | `/provinces` | Không | Danh sách tỉnh/thành |
| 8 | GET | `/data-demographics` | Không | Dữ liệu demographics |
| 9 | GET | `/event-categories` | Không | Danh mục event |

---

## 1. Health Check - Ping

```
GET {{BASE_URL}}/ping
```

**Headers:** Không cần

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/ping"
```

**Response 200:**

```json
{
  "message": "pong"
}
```

---

## 2. Health Check - Health

```
GET {{BASE_URL}}/health
```

**Headers:** Không cần

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/health"
```

**Response 200:**

```json
{
  "status": "ok"
}
```

---

## 3. Cấu hình App

```
GET {{BASE_URL}}/app-data
```

**Headers:**

```
Accept-Language: vi
```

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/app-data" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": {
    "privacy": {
      "title": "Chính sách bảo mật",
      "content": "..."
    }
  },
  "code": 200
}
```

---

## 4. Danh sách Ngân hàng

```
GET {{BASE_URL}}/bank
```

**Headers:**

```
Accept-Language: vi
```

**Query params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| pageToken | string | Không | Token phân trang |
| keyword | string | Không | Tìm kiếm theo tên |
| sort | string | Không | Sắp xếp |

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/bank" \
  -H "Accept-Language: vi"
```

```bash
# Tìm kiếm
curl -X GET "{{BASE_URL}}/bank?keyword=techcombank" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": [
    {
      "_id": "bank_001",
      "name": "Ngân hàng TMCP Kỹ Thương Việt Nam",
      "shortName": "Techcombank",
      "logo": {
        "url": "https://cdn.example.com/bank/techcombank.png"
      },
      "isBranchRequired": true
    },
    {
      "_id": "bank_002",
      "name": "Ngân hàng TMCP Ngoại Thương Việt Nam",
      "shortName": "Vietcombank",
      "logo": {
        "url": "https://cdn.example.com/bank/vietcombank.png"
      },
      "isBranchRequired": false
    }
  ],
  "code": 200
}
```

---

## 5. Chi nhánh Ngân hàng

```
GET {{BASE_URL}}/bank/:id/branch
```

**Headers:**

```
Accept-Language: vi
```

**Path params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| id | string | **Có** | Bank ID (MongoDB ObjectID, 24 ký tự hex) |

**Query params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| pageToken | string | Không | Token phân trang |
| keyword | string | Không | Tìm theo tên chi nhánh |
| sort | string | Không | Sắp xếp |

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/bank/bank_001/branch" \
  -H "Accept-Language: vi"
```

```bash
# Tìm chi nhánh ở TP.HCM
curl -X GET "{{BASE_URL}}/bank/bank_001/branch?keyword=Ho Chi Minh" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": [
    {
      "_id": "branch_001",
      "name": "Chi nhánh Hồ Chí Minh",
      "bank": "bank_001",
      "city": "Hồ Chí Minh",
      "bankCode": "TCB"
    }
  ],
  "nextPageToken": "",
  "code": 200
}
```

**Test lỗi:**

```bash
# ID sai format → 404
curl -X GET "{{BASE_URL}}/bank/invalid-id/branch"
```

---

## 6. Danh sách Quốc gia

```
GET {{BASE_URL}}/countries
```

**Headers:**

```
Accept-Language: vi
```

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/countries" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": [
    {
      "_id": "country_001",
      "slug": "vietnam",
      "name": "Việt Nam",
      "createdAt": "2025-01-01T00:00:00Z",
      "updatedAt": "2025-01-01T00:00:00Z"
    }
  ],
  "code": 200
}
```

---

## 7. Danh sách Tỉnh/Thành

```
GET {{BASE_URL}}/provinces
```

**Headers:**

```
Accept-Language: vi
```

**Query params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| pageToken | string | Không | Token phân trang |
| countrySlug | string | Không | Lọc theo quốc gia (VD: `vietnam`) |
| keyword | string | Không | Tìm kiếm |
| sort | string | Không | Sắp xếp |

> Default limit: 20

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/provinces?countrySlug=vietnam" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": [
    {
      "_id": "province_001",
      "name": "Hồ Chí Minh",
      "code": 79,
      "slug": "ho-chi-minh",
      "countrySlug": "vietnam",
      "createdAt": "2025-01-01T00:00:00Z",
      "updatedAt": "2025-01-01T00:00:00Z"
    },
    {
      "_id": "province_002",
      "name": "Hà Nội",
      "code": 1,
      "slug": "ha-noi",
      "countrySlug": "vietnam",
      "createdAt": "2025-01-01T00:00:00Z",
      "updatedAt": "2025-01-01T00:00:00Z"
    }
  ],
  "nextPageToken": "",
  "code": 200
}
```

---

## 8. Dữ liệu Demographics

```
GET {{BASE_URL}}/data-demographics
```

**Headers:**

```
Accept-Language: vi
```

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/data-demographics" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": {
    "ages": [...],
    "genders": [...],
    "topics": [...],
    "platforms": [...],
    "incomeLevels": [...],
    "educationLevels": [...],
    "professions": [...]
  },
  "code": 200
}
```

---

## 9. Danh mục Event

```
GET {{BASE_URL}}/event-categories
```

**Headers:**

```
Accept-Language: vi
```

**Query params:**

| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| pageToken | string | Không | Token phân trang |
| keyword | string | Không | Tìm kiếm |
| sort | string | Không | Sắp xếp |

> Default limit: 20. Sắp xếp mặc định: theo `name` tăng dần.

**cURL:**

```bash
curl -X GET "{{BASE_URL}}/event-categories" \
  -H "Accept-Language: vi"
```

**Response 200:**

```json
{
  "data": [
    {
      "_id": "cat_001",
      "name": "Finance",
      "icon": {
        "url": "https://cdn.example.com/icons/finance.png"
      },
      "code": "finance"
    },
    {
      "_id": "cat_002",
      "name": "Lifestyle",
      "icon": {
        "url": "https://cdn.example.com/icons/lifestyle.png"
      },
      "code": "lifestyle"
    }
  ],
  "code": 200
}
```
