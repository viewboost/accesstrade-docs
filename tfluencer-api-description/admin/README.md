# Admin API Documentation

## Thong tin chung

| Muc | Gia tri |
|-----|---------|
| Base URL | `{{ADMIN_BASE_URL}}` |
| Content-Type | `application/json` |

> Thay `{{ADMIN_BASE_URL}}` bang URL server admin thuc te. VD: `https://admin-api.viewboost.vn`

---

## Headers

### Headers bat buoc

| Header | Gia tri | Khi nao can |
|--------|---------|-------------|
| `Authorization` | `Bearer {{ADMIN_TOKEN}}` | API yeu cau dang nhap |
| `Content-Type` | `application/json` | Cac API POST/PUT/PATCH co body |

### Headers tuy chon

| Header | Gia tri mau | Mo ta |
|--------|-------------|-------|
| `Accept-Language` | `vi` / `en` | Ngon ngu response. Mac dinh `vi` |

---

## Cap do quyen (Auth Levels)

Admin API co nhieu cap do quyen, ap dung theo tung nhom API:

| Middleware | Mo ta | Ap dung cho |
|------------|-------|-------------|
| **RequiredLogin** | Chi can dang nhap | Audit, Event Bonus, Tag list, User list, Staff /me |
| **IsAdmin** | Quyen Admin tro len | User CRUD, Reconciliation, Transfer, Identification, Manage Code, Blacklist, Role, User Segment |
| **IsRoot** | Quyen Root (cao nhat) | Partner CRUD, Event reject/rerun reward |
| **IsCampaginOwner** | Quyen Campaign Owner | Event CRUD, Content, News, Article, Campaign, Segment, Analytics, Performance, Export, Quick Action, Admin Notification |
| **CheckPermissionRole** | Kiem tra role cu the (CampaignOwner/Collaborator) | Content management |
| **CheckRateLimitLoginAdmin** | Rate limit dang nhap | Staff login |
| **CheckRateLimitAuthExchange** | Rate limit auth exchange | Auth code exchange |
| **CheckKeyMigration** | Key migration dac biet | Migration (khong document) |

---

## Co che xac thuc Admin

1. Staff dang nhap qua `POST /staffs/login` hoac `POST /staffs/login-with-google`
2. Nhan JWT token trong response
3. Gui token trong header `Authorization: Bearer {{ADMIN_TOKEN}}` cho cac API tiep theo
4. Token duoc ky bang secret rieng cua Admin (`config.AuthSecret.Admin`)
5. Middleware `Auth` parse token va gan thong tin staff vao context
6. Tuy theo route, middleware kiem tra quyen: `RequiredLogin` → `IsAdmin` → `IsRoot` → `IsCampaginOwner`

---

## Response format

**Thanh cong (200):**

```json
{
  "data": { ... },
  "code": 200
}
```

**Thanh cong voi phan trang (page/limit):**

```json
{
  "data": {
    "list": [ ... ],
    "total": 150
  },
  "code": 200
}
```

**Loi:**

```json
{
  "data": null,
  "message": "Mo ta loi",
  "code": 400
}
```

| HTTP Status | Y nghia |
|-------------|---------|
| `200` | Thanh cong |
| `400` | Validation loi, thieu param, du lieu khong hop le |
| `401` | Thieu/sai token, khong co quyen |
| `403` | Khong du quyen (vd: CampaignOwner truy cap API IsAdmin) |
| `404` | ID sai format ObjectID, resource khong ton tai |
| `429` | Rate limit (login, auth exchange) |

---

## Bien moi truong (Postman / Thunder Client)

| Bien | Mo ta | Vi du |
|------|-------|-------|
| `{{ADMIN_BASE_URL}}` | URL server admin | `https://admin-api.viewboost.vn` |
| `{{ADMIN_TOKEN}}` | JWT token admin (lay tu API login) | `eyJhbGciOiJIUzI1NiIs...` |

---

## Danh sach tai lieu API

| File | Nhom | So API | Mo ta |
|------|------|--------|-------|
| [api-staffs.md](api-staffs.md) | Staffs | 18 | Dang nhap, dang ky, invite, mat khau, auth code |
| [api-users.md](api-users.md) | Users | 10 | Quan ly user, ban, socials, hop dong |
| [api-events.md](api-events.md) | Events | 26 | Event CRUD, schema, bonus, categories |
| [api-contents.md](api-contents.md) | Contents | 16 | Content management, manual flows |
| [api-reconciliations.md](api-reconciliations.md) | Reconciliations | 19 | Doi soat, checklist, evaluate |
| [api-partners.md](api-partners.md) | Partners | 7 | Partner management |
| [api-news.md](api-news.md) | News & Articles | 10 | Tin tuc, bai viet |
| [api-transfers.md](api-transfers.md) | Transfers | 7 | Chuyen khoan, rut tien |
| [api-campaigns.md](api-campaigns.md) | Campaigns | 15 | Campaign, matching, budget |
| [api-influencers.md](api-influencers.md) | Influencers | 16 | Influencer, profiles, reviews |
| [api-analytics.md](api-analytics.md) | Analytics | 16 | Analytics dashboard, performance |
| [api-misc.md](api-misc.md) | Misc | ~30 | Tags, segments, notifications, audit, export, codes, blacklist, auto-approve, roles, identifications, quick actions |

**Tong: ~190 endpoints**

> **Luu y:** API Migration va RunJob khong duoc document (chi dung noi bo / dev).
