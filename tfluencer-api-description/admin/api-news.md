# API News & Articles - Admin

Base URL: `{{ADMIN_BASE_URL}}`
Auth header: `Authorization: Bearer {{ADMIN_TOKEN}}`

---

## Tong quan

### News
| Method | Endpoint | Quyen | Mo ta |
|--------|----------|-------|-------|
| GET | `/news` | IsCampaignOwner | Lay danh sach news |
| POST | `/news` | IsCampaignOwner | Tao news moi |
| PUT | `/news/:id` | IsCampaignOwner | Cap nhat news |
| GET | `/news/:id` | IsCampaignOwner | Lay chi tiet news |
| PATCH | `/news/:id/status` | IsCampaignOwner | Doi trang thai news |
| POST | `/news/:id/clone` | IsCampaignOwner | Nhan ban news |

### Articles
| Method | Endpoint | Quyen | Mo ta |
|--------|----------|-------|-------|
| GET | `/articles` | IsCampaignOwner | Lay danh sach article |
| POST | `/articles` | IsCampaignOwner | Tao article moi |
| PATCH | `/articles/:id` | IsCampaignOwner | Cap nhat article |
| GET | `/articles/:id` | IsCampaignOwner | Lay chi tiet article |

---

## Cau truc du lieu

### FilePhoto
```json
{
  "_id": "64a1b2c3d4e5f6789012abcd",
  "name": "anh-bia.png",
  "dimensions": {
    "sm": { "url": "https://cdn.example.com/sm.png", "width": 375, "height": 200 },
    "md": { "url": "https://cdn.example.com/md.png", "width": 750, "height": 400 }
  }
}
```

### ActionType (cho News)
```json
{
  "type": "OPEN_URL",
  "value": "https://techcombank.com/promotion",
  "text": "Xem ngay"
}
```

| `type` | Can `value` | Mo ta |
|--------|-------------|-------|
| `OPEN_URL` | Co | Mo URL trong trinh duyet |
| `OPEN_INTERNAL_PATH` | Co | Mo man hinh noi bo |
| `OPEN_WITHDRAW_DETAIL` | Co | Mo chi tiet rut tien |
| `OPEN_ARTICLE_DETAIL` | Co | Mo chi tiet article |

### ArticleAction (cho Article)
```json
{
  "type": "open_url",
  "value": "https://techcombank.com",
  "text": "Xem chi tiet"
}
```

---

# PHAN I: NEWS

## 1. GET /news - Lay danh sach news

**Quyen:** IsCampaignOwner

### Headers
```
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Query Params
| Param | Kieu | Bat buoc | Mo ta |
|-------|------|----------|-------|
| `page` | int | Khong | Trang hien tai (mac dinh: 1) |
| `limit` | int | Khong | So ban ghi moi trang (mac dinh: 20) |
| `keyword` | string | Khong | Tim kiem theo tieu de |
| `type` | string | Khong | Loai: `home_banner`, `home_notice`, `popup`, `home_list` |
| `status` | string | Khong | Trang thai: `active`, `inactive` |
| `staff` | string | Khong | Filter theo staff ID (nguoi tao) |
| `partner` | string | Khong | Filter theo partner ID |
| `sort` | string | Khong | Sap xep (mac dinh: `createdAt:-1`) |

### cURL - Lay tat ca
```bash
curl -X GET "{{ADMIN_BASE_URL}}/news?page=1&limit=20" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### cURL - Loc theo loai va trang thai
```bash
curl -X GET "{{ADMIN_BASE_URL}}/news?page=1&limit=10&type=home_banner&status=active&partner={{PARTNER_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {
    "news": [
      {
        "_id": "64c1d2e3f4a5b6789012abcd",
        "title": "Uu dai T-Fluencers thang 3/2026",
        "code": "NEWS_THANG3_2026",
        "type": "home_banner",
        "status": "active",
        "order": 1,
        "shortDesc": "Chuong trinh uu dai dac biet cho T-Fluencers",
        "startAt": "2026-03-01T00:00:00Z",
        "endAt": "2026-03-31T23:59:59Z",
        "photo": {
          "_id": "64a1b2c3d4e5f6789012abcd",
          "name": "banner-thang3.png",
          "dimensions": {
            "sm": { "url": "https://cdn.example.com/banner-sm.png" },
            "md": { "url": "https://cdn.example.com/banner-md.png" }
          }
        },
        "isAllPartner": false,
        "partner": "64f3a1b2c3d4e5f678901234",
        "createdAt": "2026-02-20T08:00:00Z",
        "updatedAt": "2026-03-01T00:00:00Z"
      }
    ],
    "total": 1,
    "limit": 20
  },
  "message": ""
}
```

### Test loi
| Case | Input | Expected |
|------|-------|----------|
| Token het han | Token cu | 401 Unauthorized |
| Khong co quyen | Token khong du quyen | 403 Forbidden |

---

## 2. POST /news - Tao news moi

**Quyen:** IsCampaignOwner

### Headers
```
Content-Type: application/json
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Request Body
```json
{
  "title": "Uu dai T-Fluencers thang 4/2026",
  "code": "NEWS_THANG4_2026",
  "type": "home_banner",
  "shortDesc": "Chuong trinh uu dai dac biet thang 4",
  "desc": "<p>Noi dung chi tiet chuong trinh uu dai T-Fluencers thang 4/2026...</p>",
  "contentType": "html",
  "order": 2,
  "startAt": "2026-04-01T00:00:00Z",
  "endAt": "2026-04-30T23:59:59Z",
  "partner": "64f3a1b2c3d4e5f678901234",
  "photo": {
    "_id": "64a1b2c3d4e5f6789012abcd",
    "name": "banner-thang4.png",
    "dimensions": {
      "sm": { "url": "https://cdn.example.com/banner-sm.png", "width": 375, "height": 200 },
      "md": { "url": "https://cdn.example.com/banner-md.png", "width": 750, "height": 400 }
    }
  },
  "photoStretchSize": null,
  "action": {
    "type": "OPEN_URL",
    "value": "https://techcombank.com/promotion-thang4",
    "text": "Xem ngay"
  }
}
```

### Validation Rules
| Field | Bat buoc | Mo ta |
|-------|----------|-------|
| `type` | Co | Phai thuoc: `home_banner`, `home_notice`, `popup`, `home_list` |
| `startAt` | Co (neu co `endAt`) | Dinh dang ISO 8601 |
| `endAt` | Co (neu co `startAt`) | Dinh dang ISO 8601 |
| `action.type` | Co (neu co `action`) | Phai thuoc ActionTypeInterfaces |
| `action.value` | Co (neu action yeu cau) | URL hoac path |
| `title` | Khong | Tieu de |
| `partner` | Khong | Partner ID; neu trong thi `isAllPartner = true` |
| `contentType` | Khong | `"html"` (mac dinh) |

> **Luu y:** News moi duoc tao voi `status = "inactive"` va `isAllPartner = true` neu khong co `partner`.

### cURL
```bash
curl -X POST "{{ADMIN_BASE_URL}}/news" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -d '{
    "title": "Uu dai T-Fluencers thang 4/2026",
    "code": "NEWS_THANG4_2026",
    "type": "home_banner",
    "shortDesc": "Chuong trinh uu dai dac biet thang 4",
    "desc": "<p>Noi dung chi tiet</p>",
    "contentType": "html",
    "order": 2,
    "startAt": "2026-04-01T00:00:00Z",
    "endAt": "2026-04-30T23:59:59Z",
    "partner": "64f3a1b2c3d4e5f678901234",
    "photo": null,
    "action": null
  }'
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {
    "_id": "64d4e5f6a7b8c9012345abcd",
    "title": "Uu dai T-Fluencers thang 4/2026",
    "code": "NEWS_THANG4_2026",
    "type": "home_banner",
    "status": "inactive",
    "order": 2,
    "shortDesc": "Chuong trinh uu dai dac biet thang 4",
    "desc": "<p>Noi dung chi tiet</p>",
    "contentType": "html",
    "isAllPartner": false,
    "partner": "64f3a1b2c3d4e5f678901234",
    "startAt": "2026-04-01T00:00:00Z",
    "endAt": "2026-04-30T23:59:59Z",
    "createdAt": "2026-03-20T10:00:00Z",
    "updatedAt": "2026-03-20T10:00:00Z"
  },
  "message": ""
}
```

### Test loi
| Case | Input | Expected |
|------|-------|----------|
| Thieu `type` | `type: ""` | 400 - type is required |
| `type` sai gia tri | `type: "sidebar"` | 400 - type invalid |
| Co `startAt` ma thieu `endAt` | `startAt` nhung `endAt` trong | 400 - endAt invalid |
| Co `endAt` ma thieu `startAt` | `endAt` nhung `startAt` trong | 400 - startAt invalid |
| `action.type` sai | `action.type: "INVALID"` | 400 - action type invalid |
| `action` yeu cau `value` nhung de trong | `action.type: "OPEN_URL", value: ""` | 400 - action text invalid |

---

## 3. PUT /news/:id - Cap nhat news

**Quyen:** IsCampaignOwner

### Headers
```
Content-Type: application/json
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Path Params
| Param | Mo ta |
|-------|-------|
| `id` | ID cua news |

### Request Body
Tuong tu POST /news (cung struct `NewsUpsert`)
```json
{
  "title": "Uu dai T-Fluencers thang 4/2026 - Cap nhat",
  "code": "NEWS_THANG4_2026",
  "type": "home_banner",
  "shortDesc": "Cap nhat mo ta chuong trinh",
  "desc": "<p>Noi dung da cap nhat</p>",
  "contentType": "html",
  "order": 3,
  "startAt": "2026-04-01T00:00:00Z",
  "endAt": "2026-04-30T23:59:59Z",
  "partner": "64f3a1b2c3d4e5f678901234",
  "photo": null,
  "action": null
}
```

### cURL
```bash
curl -X PUT "{{ADMIN_BASE_URL}}/news/{{NEWS_ID}}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -d '{
    "title": "Uu dai T-Fluencers thang 4/2026 - Cap nhat",
    "code": "NEWS_THANG4_2026",
    "type": "home_banner",
    "shortDesc": "Cap nhat mo ta",
    "desc": "<p>Noi dung da cap nhat</p>",
    "contentType": "html",
    "order": 3,
    "startAt": "2026-04-01T00:00:00Z",
    "endAt": "2026-04-30T23:59:59Z"
  }'
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {
    "_id": "{{NEWS_ID}}",
    "title": "Uu dai T-Fluencers thang 4/2026 - Cap nhat",
    "type": "home_banner",
    "status": "inactive",
    "order": 3,
    "updatedAt": "2026-03-20T11:00:00Z"
  },
  "message": ""
}
```

### Test loi
| Case | Input | Expected |
|------|-------|----------|
| ID khong ton tai | `id: "000000000000000000000000"` | 400 - not found |
| Thieu `type` | `type: ""` | 400 - type is required |
| `type` sai gia tri | `type: "unknown"` | 400 - type invalid |
| Khong co quyen | Token khong du quyen | 403 Forbidden |

---

## 4. GET /news/:id - Lay chi tiet news

**Quyen:** IsCampaignOwner

### Headers
```
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Path Params
| Param | Mo ta |
|-------|-------|
| `id` | ID cua news |

### cURL
```bash
curl -X GET "{{ADMIN_BASE_URL}}/news/{{NEWS_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {
    "news": {
      "_id": "64d4e5f6a7b8c9012345abcd",
      "title": "Uu dai T-Fluencers thang 4/2026",
      "code": "NEWS_THANG4_2026",
      "type": "home_banner",
      "status": "active",
      "order": 2,
      "shortDesc": "Chuong trinh uu dai dac biet thang 4",
      "desc": "<p>Noi dung chi tiet</p>",
      "contentType": "html",
      "isAllPartner": false,
      "partner": "64f3a1b2c3d4e5f678901234",
      "photo": null,
      "photoStretchSize": null,
      "action": {
        "type": "OPEN_URL",
        "value": "https://techcombank.com/promotion",
        "text": "Xem ngay"
      },
      "startAt": "2026-04-01T00:00:00Z",
      "endAt": "2026-04-30T23:59:59Z",
      "createdAt": "2026-03-20T10:00:00Z",
      "updatedAt": "2026-03-20T11:00:00Z"
    }
  },
  "message": ""
}
```

> **Luu y:** Response duoc wrap trong key `"news"` khac voi cac API khac.

### Test loi
| Case | Input | Expected |
|------|-------|----------|
| ID khong ton tai | `id: "000000000000000000000000"` | Data null |
| ID sai dinh dang | `id: "invalid"` | 400 bad request |
| Token het han | Token cu | 401 Unauthorized |

---

## 5. PATCH /news/:id/status - Doi trang thai news

**Quyen:** IsCampaignOwner

### Headers
```
Content-Type: application/json
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Path Params
| Param | Mo ta |
|-------|-------|
| `id` | ID cua news |

### Request Body
```json
{
  "status": "active"
}
```

| Field | Bat buoc | Gia tri hop le |
|-------|----------|----------------|
| `status` | Co | `"active"`, `"inactive"` |

### cURL - Kich hoat
```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/news/{{NEWS_ID}}/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -d '{"status": "active"}'
```

### cURL - Vo hieu hoa
```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/news/{{NEWS_ID}}/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -d '{"status": "inactive"}'
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {
    "_id": "{{NEWS_ID}}",
    "status": "active",
    "updatedAt": "2026-03-20T12:00:00Z"
  },
  "message": ""
}
```

### Test loi
| Case | Input | Expected |
|------|-------|----------|
| `status` trong | `status: ""` | 400 - status is required |
| `status` sai gia tri | `status: "draft"` | 400 - status invalid |
| ID khong ton tai | `id: "000000000000000000000000"` | 400 - not found |
| Khong co quyen | Token khong du quyen | 403 Forbidden |

---

## 6. POST /news/:id/clone - Nhan ban news

**Quyen:** IsCampaignOwner

### Headers
```
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Path Params
| Param | Mo ta |
|-------|-------|
| `id` | ID cua news can nhan ban |

> **Khong can request body.**
> Ban sao duoc tao voi `status = "inactive"` va title/code giu nguyen (co the duoc them suffix).

### cURL
```bash
curl -X POST "{{ADMIN_BASE_URL}}/news/{{NEWS_ID}}/clone" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {},
  "message": ""
}
```

> **Luu y:** Response tra ve object rong `{}`. Lay ban sao bang GET /news voi filter moi nhat.

### Test loi
| Case | Input | Expected |
|------|-------|----------|
| ID khong ton tai | `id: "000000000000000000000000"` | 400 - not found |
| ID sai dinh dang | `id: "invalid"` | 400 bad request |
| Khong co quyen | Token khong du quyen | 403 Forbidden |

---

# PHAN II: ARTICLES

## 7. GET /articles - Lay danh sach article

**Quyen:** IsCampaignOwner

### Headers
```
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Query Params
| Param | Kieu | Bat buoc | Mo ta |
|-------|------|----------|-------|
| `page` | int | Khong | Trang hien tai (>= 0) |
| `limit` | int | Khong | So ban ghi moi trang (>= 0) |
| `keyword` | string | Khong | Tim kiem theo tieu de |
| `partner` | string | Khong | Filter theo partner ID |
| `sort` | string | Khong | Sap xep (mac dinh: `createdAt:-1`) |

### cURL - Lay tat ca
```bash
curl -X GET "{{ADMIN_BASE_URL}}/articles?page=1&limit=20" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### cURL - Loc theo partner
```bash
curl -X GET "{{ADMIN_BASE_URL}}/articles?page=1&limit=10&partner={{PARTNER_ID}}&keyword=techcombank" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {
    "data": [
      {
        "_id": "64e5f6a7b8c9d0123456abcd",
        "title": "Huong dan dang ky T-Fluencers",
        "code": "ARTICLE_HDDK",
        "showOn": "all",
        "content": "<p>Noi dung huong dan...</p>",
        "contentType": "html",
        "covers": [],
        "partner": "64f3a1b2c3d4e5f678901234",
        "createdBy": "64a0b1c2d3e4f5678901abcd",
        "createdAt": "2026-03-10T08:00:00Z",
        "updatedAt": "2026-03-15T10:00:00Z"
      }
    ],
    "total": 1,
    "limit": 20
  },
  "message": ""
}
```

### Test loi
| Case | Input | Expected |
|------|-------|----------|
| `page` am | `page=-1` | 400 - page invalid |
| `limit` am | `limit=-5` | 400 - limit invalid |
| Token het han | Token cu | 401 Unauthorized |

---

## 8. POST /articles - Tao article moi

**Quyen:** IsCampaignOwner

### Headers
```
Content-Type: application/json
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Request Body
```json
{
  "title": "Huong dan tham gia T-Fluencers Challenge",
  "content": "<h2>Dieu kien tham gia</h2><p>Influencer can co it nhat 1000 followers...</p>",
  "contentType": "html",
  "code": "ARTICLE_HDTG",
  "showOn": "all",
  "partner": "64f3a1b2c3d4e5f678901234",
  "covers": [
    {
      "_id": "64a1b2c3d4e5f6789012abce",
      "name": "cover-article.png",
      "dimensions": {
        "sm": { "url": "https://cdn.example.com/article-sm.png", "width": 375, "height": 200 },
        "md": { "url": "https://cdn.example.com/article-md.png", "width": 750, "height": 400 }
      }
    }
  ],
  "action": {
    "type": "open_url",
    "value": "https://techcombank.com/challenge",
    "text": "Tham gia ngay"
  }
}
```

### Validation Rules
| Field | Bat buoc | Mo ta |
|-------|----------|-------|
| `title` | Co | Tieu de bai viet |
| `content` | Co | Noi dung HTML hoac text |
| `showOn` | Co | Chi ho tro: `"all"` |
| `code` | Khong | Ma dinh danh |
| `partner` | Khong | Partner ID |
| `covers` | Khong | Mang anh bia (ListPhoto) |
| `action` | Khong | Hanh dong dinh kem |
| `contentType` | Khong | `"html"` (mac dinh) |

### cURL
```bash
curl -X POST "{{ADMIN_BASE_URL}}/articles" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -d '{
    "title": "Huong dan tham gia T-Fluencers Challenge",
    "content": "<h2>Dieu kien tham gia</h2><p>Influencer can co it nhat 1000 followers</p>",
    "contentType": "html",
    "code": "ARTICLE_HDTG",
    "showOn": "all",
    "partner": "64f3a1b2c3d4e5f678901234",
    "covers": [],
    "action": null
  }'
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {
    "_id": "64f6a7b8c9d0e1234567abcd",
    "title": "Huong dan tham gia T-Fluencers Challenge",
    "content": "<h2>Dieu kien tham gia</h2><p>Influencer can co it nhat 1000 followers</p>",
    "contentType": "html",
    "code": "ARTICLE_HDTG",
    "showOn": "all",
    "covers": [],
    "partner": "64f3a1b2c3d4e5f678901234",
    "createdBy": "64a0b1c2d3e4f5678901abcd",
    "createdAt": "2026-03-20T14:00:00Z",
    "updatedAt": "2026-03-20T14:00:00Z"
  },
  "message": ""
}
```

### Test loi
| Case | Input | Expected |
|------|-------|----------|
| Thieu `title` | `title: ""` | 400 - title is required |
| Thieu `content` | `content: ""` | 400 - content is required |
| Thieu `showOn` | `showOn: ""` | 400 - showOn is required |
| `showOn` sai gia tri | `showOn: "partner"` | 400 - type invalid |
| Khong co quyen | Token khong du quyen | 403 Forbidden |

---

## 9. PATCH /articles/:id - Cap nhat article

**Quyen:** IsCampaignOwner

### Headers
```
Content-Type: application/json
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Path Params
| Param | Mo ta |
|-------|-------|
| `id` | ID cua article |

### Request Body
Tuong tu POST /articles (cung struct `ArticleBody`)
```json
{
  "title": "Huong dan tham gia T-Fluencers Challenge - Cap nhat",
  "content": "<h2>Dieu kien tham gia (cap nhat)</h2><p>Influencer can co it nhat 500 followers...</p>",
  "contentType": "html",
  "code": "ARTICLE_HDTG",
  "showOn": "all",
  "partner": "64f3a1b2c3d4e5f678901234",
  "covers": [],
  "action": null
}
```

### cURL
```bash
curl -X PATCH "{{ADMIN_BASE_URL}}/articles/{{ARTICLE_ID}}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}" \
  -d '{
    "title": "Huong dan tham gia T-Fluencers Challenge - Cap nhat",
    "content": "<h2>Dieu kien cap nhat</h2><p>Influencer can co it nhat 500 followers</p>",
    "contentType": "html",
    "code": "ARTICLE_HDTG",
    "showOn": "all",
    "partner": "64f3a1b2c3d4e5f678901234",
    "covers": [],
    "action": null
  }'
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {
    "_id": "{{ARTICLE_ID}}",
    "title": "Huong dan tham gia T-Fluencers Challenge - Cap nhat",
    "content": "<h2>Dieu kien cap nhat</h2><p>Influencer can co it nhat 500 followers</p>",
    "contentType": "html",
    "code": "ARTICLE_HDTG",
    "showOn": "all",
    "updatedAt": "2026-03-20T15:00:00Z"
  },
  "message": ""
}
```

### Test loi
| Case | Input | Expected |
|------|-------|----------|
| ID khong ton tai | `id: "000000000000000000000000"` | 400 - not found |
| Thieu `title` | `title: ""` | 400 - title is required |
| Thieu `content` | `content: ""` | 400 - content is required |
| `showOn` sai gia tri | `showOn: "mobile"` | 400 - type invalid |
| Khong co quyen | Token khong du quyen | 403 Forbidden |

---

## 10. GET /articles/:id - Lay chi tiet article

**Quyen:** IsCampaignOwner

### Headers
```
Authorization: Bearer {{ADMIN_TOKEN}}
```

### Path Params
| Param | Mo ta |
|-------|-------|
| `id` | ID cua article |

### cURL
```bash
curl -X GET "{{ADMIN_BASE_URL}}/articles/{{ARTICLE_ID}}" \
  -H "Authorization: Bearer {{ADMIN_TOKEN}}"
```

### Response mau - Thanh cong (200)
```json
{
  "code": 200,
  "data": {
    "_id": "64f6a7b8c9d0e1234567abcd",
    "title": "Huong dan tham gia T-Fluencers Challenge",
    "content": "<h2>Dieu kien tham gia</h2><p>Influencer can co it nhat 1000 followers</p>",
    "contentType": "html",
    "code": "ARTICLE_HDTG",
    "showOn": "all",
    "covers": [],
    "action": null,
    "partner": "64f3a1b2c3d4e5f678901234",
    "createdBy": "64a0b1c2d3e4f5678901abcd",
    "createdAt": "2026-03-20T14:00:00Z",
    "updatedAt": "2026-03-20T15:00:00Z"
  },
  "message": ""
}
```

### Test loi
| Case | Input | Expected |
|------|-------|----------|
| ID khong ton tai | `id: "000000000000000000000000"` | 400 - not found |
| ID sai dinh dang | `id: "invalid"` | 400 bad request |
| Token het han | Token cu | 401 Unauthorized |
| Khong co quyen | Token khong du quyen | 403 Forbidden |
