# Audit 01: Source Overview & State

**Date:** 2026-04-29
**Source:** `accesstrade-projects/vcreator-philippines/` — clone từ `viewboost/vcreator-philippines.git`, branch `main`, commit `9e2b817 init philippines`

---

## 1. Codebase Stats

| Layer | Files | LOC |
|---|---:|---:|
| Backend Go | 523 | 62,962 |
| Frontend (creator + admin) TS/TSX | 530 | 55,569 |
| **Total** | **1,053** | **118,531** |

---

## 2. State của source — TL;DR

⚠️ **Source này KHÔNG phải Philippines code.** Đây là **Indonesia code chưa được rename**.
Tên repo `vcreator-philippines` nhưng nội dung là Indonesia (Bahasa, IDR, +62, contract Indonesia).

Bằng chứng:
- Phone regex: `^(?:\+62|62|0)[2-9][1-9][0-9]{6,11}$` (Indonesia)
- Currency: `ToCurrencyIDR` (constants.go:226: `PercentTaxIndonesia = 12`)
- Contract: "PT. Interspace Indonesia, Menara Anugrah, Jakarta Selatan" (Bahasa Indonesia)
- Locales: `en-US`, `id-ID`, `vi-VN` (KHÔNG có `fil-PH`)

→ **Source này là Indonesia code đang được CHUẨN BỊ port sang Philippines, chưa làm gì.**

⚠️ **Indonesia source CHƯA port hoàn chỉnh từ VN** — vẫn còn nhiều VN leftover quan trọng.

Bằng chứng VN leftover:
- 8 chỗ hardcode `+84` chưa đổi sang `+62` (chưa nói gì đến `+63`)
- 47 chỗ dùng `TimeOfDayInHCM` / `Asia/Ho_Chi_Minh` timezone
- Constants `PercentTaxVietNam = 10` còn tồn tại
- format util `string.go:31` vẫn `phone = strings.Replace(phone, "0", "+84", 1)`
- model/mg/user.go:152: `strings.Replace(p.Full, "+84", "0", 1)`

→ **Tổng kết: Source = VN ➜ ID port chưa xong ➜ chưa bắt đầu port sang PH.**

---

## 3. Architecture

```
vcreator-philippines/
├── backend/        Go + Echo + MongoDB + Redis + MinIO
│   ├── internal/   Shared internal modules
│   ├── pkg/
│   │   ├── public/ Creator API (anonymous + authenticated)
│   │   ├── admin/  Admin backoffice API
│   │   └── file/   File serving
│   └── docs/       (?)
├── frontend/       UmiJS + React (creator UI)
├── admin/          UmiJS + React (admin UI)
└── locales/        Top-level shared locale JSONs
    ├── admin/      en-US, id-ID, vi-VN
    ├── client/     en-US, id-ID, vi-VN
    └── server/     en, id, vi
```

---

## 4. Backend Routes Summary

### Public (creator-facing) — 16 modules, ~70 routes

| Module | Routes | Notes |
|---|---:|---|
| user | 30 | Auth + profile + bank + identification + contract + cashflow + social + referral |
| event | 10 | Event list/detail + content submission |
| schedule | 5 | Cron crawl: TikTok, TikTok-self, Facebook, YouTube + content callback |
| content_callback | 1 | Webhook from content-catcher |
| user_statistic | 4 | Stats: contents + invitees |
| common | 3 | App data + bank list |
| article | 1 | Article detail |
| news | 2 | News list + analytic |
| notification | 2 | List + read |
| partner | 3 | Partner info |
| quick_action | 1 | Quick action buttons |
| transcript | 1 | Webhook transcript |

### Admin — 21 modules, ~100 routes

| Module | Notes |
|---|---|
| user, staff, role, segment, user_segment | RBAC + user management |
| event, event_schema | Event CRUD + reward schema |
| content, content_manual_flow | Content management |
| reconciliation | Đối soát: list + items + milestone + change-status |
| transfer | **Payout flow** (transfer = payout batch) |
| identification | KYC review |
| article, news, admin_notification, partner, tag, quick_action | CMS |
| audit | Audit log |
| common, configuration | App config + scopes + generate-bank |
| migration | One-time scripts |
| export | Export jobs |

→ **Reconciliation + Transfer/Withdraw có đầy đủ trong admin** — đây là payout system.

---

## 5. DB Collections (47 collections)

```
users, user-partners, user-socials, user-devices, user-events
user-publishers, user-bank-cards, user-contracts, user-segments
user-event-analytic-daily, user-income-month
contents, content-callbacks, content-crawl-histories
content-transcripts, content-analytic-daily, content-follows
content-manual-follows, content-follow-backups
events, event-rewards, event-reward-temps, event-schemas
event-analytic-daily
reconciliation, reconciliation-items, reconciliation-histories
transfers, withdraw, cash-flows
identifications, tracking-identifications
notifications, admin-notifications
articles, article-views, news, partners, segments, tags
quick-actions, referrals
staffs, admin-2fa, roles, sessions
configurations, otp-codes, otp-tracking-requests
files, videos, bank, bank-branch, data-exports
countries, provinces
```

→ **Schema phức tạp** — payout/transfer/reconciliation đầy đủ. Đây là e-commerce affiliate creator platform thật sự.

---

## 6. Country-Specific Things còn lưu

### Hardcoded country code (VN/ID confused)

| File:Line | Context | Code |
|---|---|---|
| constants.go:40 | Phone regex | `^(?:\+62\|62\|0)[2-9][1-9][0-9]{6,11}$` (ID) |
| constants.go:72 | Timezone | `timezoneHCM = "Asia/Ho_Chi_Minh"` (VN!) |
| constants.go:226 | Tax | `PercentTaxIndonesia = 12` |
| constants.go:227 | Tax | `PercentTaxVietNam = 10` (VN leftover) |
| format/string.go:31 | Phone normalize | `phone = strings.Replace(phone, "0", "+84", 1)` (VN!) |
| format/string.go:77 | CountryCode | `phoneNumber.CountryCode = "+84"` (VN!) |
| model/mg/user.go:152 | Search string | `strings.Replace(p.Full, "+84", "0", 1)` (VN!) |
| service/otp.go:108 | OTP send | `strings.Replace(payload.Recipient, "+84", "0", 1)` (VN!) |
| service/withdraw.go:137 | Tax calc | `payload.CashTax = math.Round(... * PercentTaxIndonesia / 100)` (ID) |
| public/service/user.go:113, 616 | Contract | `strings.ReplaceAll(user.Phone.Full, "+84", "0")` (VN!) |
| public/service/identification.go:83 | Contract | `strings.ReplaceAll(phoneInfo.Full, "+84", "0")` (VN!) |
| public/service/schedule.go:413, 789 | Crawl + tax | VN phone replace + ID tax |
| admin/service/user.go:184 | Contract | `strings.ReplaceAll(user.Phone.Full, "+84", "0")` (VN!) |

→ **Phone handling rối**: regex Indonesia, nhưng logic format/replace dùng VN code (+84).

### Contract template (Bahasa Indonesia)

`internal/constants/contract.go` chứa hợp đồng Bahasa Indonesia luật ID:
- Pihak A: PT. Interspace Indonesia (Jakarta Selatan)
- Tax: "Pihak B bertanggung jawab penuh atas kewajiban pajak sesuai hukum Indonesia"
- 5 điều khoản về advertising rules theo luật ID

### Locales

| Layer | Languages |
|---|---|
| `locales/admin/` | en-US ✅, id-ID ✅, vi-VN ✅ |
| `locales/client/` | en-US ✅, id-ID ✅, vi-VN ✅ |
| `locales/server/` | en ✅, id ✅, vi ✅ |
| `frontend/src/locales/` | en-US ✅, id-ID ✅, vi-VN ✅ |
| `admin/src/locales/` | en-US ✅, id-ID ✅, vi-VN ⚠️ (173 dòng — incomplete) |

→ **Filipino (fil-PH) hoàn toàn chưa có.**

---

## 7. Configuration / Env Variables

### Variables CHƯA có khái niệm region/country

`config/env.go` không có:
- `REGION` / `COUNTRY` constant
- `PHONE_COUNTRY_CODE`
- `TIMEZONE`
- `CURRENCY`

→ **Tất cả country-specific là HARDCODE trong source code, không config-driven.**

### Variables config được

| Group | Vars |
|---|---|
| Server | ENV, ADMIN_*, FILE_*, PUBLIC_*, FILE_HOST, WEB_HOST |
| DB | MONGO_*, MINIO_*, REDIS_* |
| Auth | AUTH_SECRET_ADMIN, AUTH_SECRET_PUBLIC, GOOGLE_CLIENT_ID |
| Social | TIKTOK_*, FACEBOOK_*, INSTAGRAM_* |
| Notification | FIREBASE_*, TELEGRAM_*, ACCESS_TRADE_SMS_* |
| Storage | GOOGLE_DRIVE_* |
| Crawl | CONTENT_CATCHER_*, LIMIT_LINK_PER_PAGE_CRAWL |
| 2FA | TOTP_*, CAPTCHA_* |

### Notable: Có TOTP + Captcha

Khác vCreator VN: source này có:
- `admin-2fa` collection
- TOTP config (Issuer/AppName/PassPhrase)
- Captcha config (SecretKey/Endpoint)
- Admin 2FA flow (`/staffs/:id/totp`, `/staffs/captcha`)

→ Admin authentication mạnh hơn VN.

---

## 8. Frontend — FE Routes

Routes đã English (`/account`, `/payment-info`, `/e-contract`, `/notification`, `/connect-tiktok`...).

FE creator pages:
- 404 / account / article / bank / common-article / connect-tiktok / contact /
- content / contract / guide / home / login-tiktok / main-home /
- notification / partner-home / profile / statistic

Admin pages:
- article / configuration / content / dashboard / data / event / event-statistic /
- identification / login / news / notification / partner / quick-action / reconciliation /
- segment / staff / tag / transfer / user / user-partner

---

## 9. Khác biệt chính so với vCreator VN

### Source ID THIẾU (so với VN):
- Public: `migration.go`, `opshub_webhook.go`, `workplace.go`
- Admin: `employee_registry.go`, `event_bonus.go`, `event_reward.go`, `workplace.go`
- Routes: `/users/identification/image`, `/users/ekyc/*`, `/users/link-account`, `/users/update-phone-number`, `/users/check-bank-account`, `/users/bank/list`, `/users/complete-profile`, `/users/check-unique`, `/users/dismiss-profile-popup`, `/users/profile/request-otp`, `/users/profile/verify-otp`, `/users/econtract/*`
- Schedule: `/crawl-content-threads`, `/update-contract-status`

### Source ID THÊM (so với VN):
- Locales structure top-level (admin/client/server)
- Admin 2FA + Captcha + TOTP
- `/users/contract/agree` (1 endpoint thay 3 endpoints econtract của VN)
- Admin: `/users/:id/reject-contract`, `/users/:id/un-ban`, `/users/contract/generate-by-user-id`
- Admin staff: `/staffs/captcha`, `/staffs/:id/totp`, `/staffs/:id/reset-2fa`, `/staffs/:id/update-info`, `/staffs/:id/update-password`
- Admin reconciliation: `/reconciliations/:id/milestone` + `/item/:idItem/change-status`
- Admin common: `/generate-bank` (??)

→ Source ID **không phải subset của VN** — có evolution riêng.

---

## 10. Câu hỏi cần answer trước khi build task list

### Fundamental
1. **Có cần audit thêm modules cụ thể không?** Tôi đã verify user/identification kỹ. Còn schedule (1976 dòng), event (860), withdraw (278) chưa audit kỹ.
2. **Quyết định scope cuối cùng** — bỏ Tax + Withdraw + Bank như đã chốt với GreenSM PH? (vì khách tự payout qua payroll)
3. **Filipino translation** — Partner cung cấp text hay dev tự thuê?

### Technical decisions
4. **Phone handling refactor** — rewrite `format/string.go` thành multi-region hay hardcode `+63`?
5. **Timezone** — Manila (Asia/Manila, UTC+8) hay giữ HCM (cũng UTC+8 nhưng semantics sai)?
6. **Config-driven hay hardcode?** Source ID hardcode tất cả. Build PH theo cách hardcode mới (nhanh) hay refactor config-driven (sạch hơn)?

### Scope
7. **Source ID có Reconciliation/Transfer admin** — partner GreenSM PH có dùng? Hay bỏ luôn?
8. **Admin 2FA + Captcha** — giữ hay bỏ?
9. **Publisher mode** (`/users/publisher`) — feature gì? Cần verify.

---

## 11. Recommendation cho audit tiếp theo

Để build task list chính xác, audit kỹ thêm 4 modules:

1. **`service/schedule.go`** (1976 dòng) — chứa logic crawl + có `PercentTaxIndonesia` reference
2. **`service/event.go`** (860 dòng) — core business: campaign + reward
3. **`service/withdraw.go`** (278 dòng) — verify để bỏ scope đúng
4. **Admin services** — toàn bộ thư mục `admin/service/` (chưa list)

Sau đó mới đủ data để viết task list.
