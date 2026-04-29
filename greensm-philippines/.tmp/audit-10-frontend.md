# Audit 10: Frontend (Creator + Admin)

**Codebase stats:**
- FE Creator: 231 files, 21,894 LOC TS/TSX
- Admin FE: 299 files, 33,675 LOC TS/TSX
- Total: 530 files, 55,569 LOC

---

## i18n Coverage

### Locale files (multiple paths)

```
locales/                             # Top-level shared
├── admin/  (en-US, id-ID, vi-VN)    409+408+408 lines
├── client/ (en-US, id-ID, vi-VN)    295+295+293 lines
└── server/ (en, id, vi)             345+345+346 lines

frontend/src/locales/  (en-US, id-ID, vi-VN)  229+231+226 lines
admin/src/locales/     (en-US, id-ID, vi-VN)  409+408+173 lines (vi incomplete)
```

→ **Có 3 layer locales**: top-level shared + frontend local + admin local
→ Top-level `locales/admin/` và `admin/src/locales/` content **giống hệt** — duplicate
→ Top-level `locales/client/` và `frontend/src/locales/` content **giống hệt** — duplicate
→ Filipino (`fil-PH`) hoàn toàn chưa có

### Default locale

| Path | Default |
|---|---|
| `frontend/config/config.ts` | `id-ID` |
| `admin/config/config.ts` | `id-ID` |

→ Default Indonesia. Cần đổi sang `en-US` cho PH.

### Translation status (3 ngôn ngữ existed)

✅ **Hoàn chỉnh**:
- en-US, id-ID, vi-VN ở `frontend/src/locales/` — content fully translated
- en-US, id-ID, vi-VN ở `locales/client/` — duplicate of above
- en-US, id-ID ở `admin/src/locales/` + `locales/admin/`

⚠️ **Incomplete**:
- vi-VN ở `admin/src/locales/` — chỉ 173 dòng (vs en-US 409 dòng) → bị truncate

---

## FE Creator (frontend/) — Country issues

### Config files

| File:Line | Code | Issue |
|---|---|---|
| **configs/app.tsx:58** | `const phoneNumberPrefix = '+84'` | 🔴 VN code hardcode |
| **configs/form.ts:3** | `phoneRegExp = /^(0\|\+62\|62)(\d{9}\|\d{10}\|\d{11}\|\d{12})$/` | 🟡 Indonesia regex |

→ **Conflict:** prefix là VN nhưng regex là Indonesia.

### Component leftover (7 chỗ tiếng Việt hardcode còn sót)

| File:Line | Issue |
|---|---|
| `pages/bank/components/user-cards/index.tsx:107` | "Đặt làm tài khoản mặc định" |
| `pages/bank/components/user-cards/index.tsx:123` | "Thêm tài khoản mới" |
| `pages/account/management/index.tsx:64` | Comment tiếng Việt |
| `pages/account/tax/components/form/index.tsx:102` | "Truy cập trang tra cứu của tổng cục thuế Việt Nam" |
| `pages/account/tax/components/form/index.tsx:164,170` | Tham chiếu Cục Cảnh sát Việt Nam |
| `pages/main-home/index.tsx:116` | Comment tiếng Việt |

→ Đa số là **trong page tax** (tax page reference luật VN) — sẽ bỏ vì PH không cần tax module same way.

### `utils/breadcrumb-utils.ts`
- Toàn bộ comments tiếng Việt (~10 comments)
- Code generic, không có VN-specific logic
- → Cleanup: dịch comments sang EN

### Currency / amount formatting
✅ FE creator KHÔNG có currency hardcode

---

## Admin FE (admin/) — Country issues

### `admin/src/utils/format.ts` 🔴 CRITICAL

| File:Line | Code | Issue |
|---|---|---|
| **format.ts:70** | `value = value.replace('+84', '0')` | 🔴 VN phone code |
| **format.ts:69** | Comment "Replace +84 to 0" | 🔴 |
| **format.ts:112** | `unit: 'VND'` | 🔴 Currency unit hardcode |
| **format.ts:138** | `str.replace(/đ/g, 'd')` | 🟡 VN char (Vietnamese đ) |
| **format.ts:225,237** | Vietnamese accent removal logic | 🟡 |

### Comments tiếng Việt admin
- `admin/src/utils/upload.ts:38` — Vietnamese error message hardcode
- `admin/src/utils/format.ts:152` — Vietnamese comment

### Components
- KHÔNG có component-level tiếng Việt hardcode (i18n proper)
- Default locale `id-ID`

---

## Pages structure

### FE Creator pages (18 pages)
```
404/ account/ article/ bank/ common-article/ connect-tiktok/
contact/ content/ contract/ guide/ home/ login-tiktok/
main-home/ notification/ partner-home/ profile/ statistic/
```

### Admin FE pages (~24 pages)
```
403, 404, article, configuration, content, dashboard, data,
event, event-statistic, identification, login, news, notification,
partner, quick-action, reconciliation, segment, staff, tag,
transfer, user, user-partner
```

---

## Cleanup tasks Frontend

| Task ID | File:Line | Description | Priority | Effort |
|---|---|---|---|---|
| FE-01 | configs/app.tsx:58 | Replace `phoneNumberPrefix = '+84'` → `'+63'` (or config-driven) | P0 | S |
| FE-02 | configs/form.ts:3 | Replace phoneRegExp Indonesia → PH regex `^(09\|\+639\|639)\d{9}$` | P0 | S |
| FE-03 | utils/formatter.ts:74,126 | Verify dùng AppConst.phoneNumberPrefix (auto inherit từ FE-01) | P0 | S |
| FE-04 | locales JSON files | Add `fil-PH.json` cho frontend + admin + client + server (4 paths) | P0 | M |
| FE-05 | locales/admin/vi-VN.json (top-level + admin/src/) | Sync 408 keys vs 173 keys (admin/src/locales/vi-VN.json incomplete) | P1 | S |
| FE-06 | config.ts (frontend + admin) | Đổi default `id-ID` → `en-US` | P0 | S |
| FE-07 | pages/bank/.../user-cards/index.tsx:107,123 | Replace tiếng Việt hardcode | P0 | S |
| FE-08 | pages/account/tax/components/form/index.tsx | Bỏ luôn page tax hoặc rewrite cho PH (xem decision tax scope) | P0 | M |
| FE-09 | pages/account/management/index.tsx:64 + main-home/index.tsx:116 | Cleanup Vietnamese comments | P2 | S |
| FE-10 | utils/breadcrumb-utils.ts | Translate comments → EN (toàn file) | P2 | S |
| FE-11 | admin/src/utils/format.ts:70 | Replace `+84` hardcode | P0 | S |
| FE-12 | admin/src/utils/format.ts:112 | Replace `unit: 'VND'` → `'PHP'` (or config-driven) | P0 | S |
| FE-13 | admin/src/utils/format.ts:138,225,237 | Verify Vietnamese accent functions còn cần không (search indexing) | P2 | S |
| FE-14 | admin/src/utils/upload.ts:38 | Translate error message tiếng Việt → EN | P1 | S |
| FE-15 | locales duplicate | Decide: dùng top-level shared OR per-app locales (không nên cả 2) | P1 | M |

---

## i18n strategy cho PH

### Decision: Add `fil-PH` hay không?

**Yêu cầu partner (file Onboarding §46):** "tiếng Filipino (dựa trên tiếng Tagalog) và tiếng Anh"

→ **PHẢI add Filipino**.

### Effort thêm Filipino

- 4 JSON files: `frontend/src/locales/fil-PH.json` + `admin/src/locales/fil-PH.json` + `locales/client/fil-PH.json` + `locales/admin/fil-PH.json`
- Tổng keys cần translate: ~3,800 keys (295 client + 409 admin + 345 server, x4 vì duplicate)
- Cần native translator hoặc partner cung cấp text

### Default locale strategy

Đề xuất:
- **Default: `en-US`** (tiếng Anh)
- Cho user toggle EN ↔ Filipino
- KHÔNG cần Indonesia + Vietnamese cho PH market → có thể remove `id-ID` + `vi-VN` để giảm bundle size (hoặc giữ làm reference cho dev)

---

## Verdict — Frontend

✅ **FE i18n đã proper với 3 ngôn ngữ JSON đã dịch đầy đủ**.

⚠️ **Country leftover ở FE rất ít**:
- 2 config conflicts (phone prefix VN vs regex ID)
- 7 chỗ tiếng Việt hardcode còn sót
- Admin format util `+84` + VND
- Comments tiếng Việt trong utility files

✅ **Admin FE clean** ở component level — chỉ cleanup utils.

→ Effort port FE ≈ 3-4 ngày (chủ yếu là i18n add Filipino + sửa config phone/currency).
