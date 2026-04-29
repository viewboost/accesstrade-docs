# Audit Summary — vCreator-Philippines Source

**Date:** 2026-04-29
**Source:** `accesstrade-projects/vcreator-philippines/`
**Audits performed:** 10 reports, 2,198 dòng analysis trong `.tmp/`

---

## TL;DR

⚠️ **Source `vcreator-philippines` thực ra là Indonesia code chưa rename**, port từ Vietnam **chưa hoàn chỉnh**.

3 lớp leftover trong source:
1. **VN leftover** (chưa port hết khi VN → ID): timezone HCM (91 occurrences), `+84` phone code (12 chỗ), Vietnamese accent functions (38 chỗ), Bahasa contract (Indonesia luật), Vietnamese error messages
2. **ID-specific** (cần đổi sang PH): Tax 12% Indonesia, `+62` regex, `id-ID` default locale, contract Bahasa Jakarta
3. **PH-specific cần thêm mới**: `fil-PH` locale, `+63` phone, Manila tz, PH luật contract, PH bank list

---

## Codebase scale

| Layer | Files | LOC |
|---|---:|---:|
| Backend Go | 523 | 62,962 |
| FE Creator + Admin TS/TSX | 530 | 55,569 |
| **Total** | **1,053** | **118,531** |

---

## Country leftover statistics

### VN leftover (cần đổi)

| Pattern | Count | Files affected |
|---|---:|---|
| `TimeOfDayInHCM` / `TimeStartOfDayInHCM` / `Asia/Ho_Chi_Minh` | **91** | 25+ files (toàn backend) |
| `"+84"` hardcode (phone code) | **12** | 8 files (format/string.go, model/mg/user.go, service/otp.go, public/services, admin/services) |
| `NonAccentVietnamese` / `RemoveAccentVietnamese` | **38** | format/string.go + 11 callsites (event/partner/article/news/segment titles, bank, transfer, reconciliation) |
| `PercentTaxVietNam = 10` | **1** (constant unused) | constants.go:227 |
| Vietnamese error messages | **2+** | identification.go:453 ("Hủy bởi người dùng..."), schedule.go:1775 ("Nội dung đã bị xóa hashtag"), schedule.go:739 |
| Vietnamese comments | ~20 | utils/breadcrumb-utils.ts, utils/format.ts, breadcrumb-utils.ts |
| `ConvertSlugProvince` ("ho-chi-minh") | 2 funcs | format/string.go:99-112 |
| FE phone prefix `phoneNumberPrefix = '+84'` | 1 | configs/app.tsx:58 |
| FE admin format util `+84` replace | 1 | admin/utils/format.ts:70 |

### ID-specific (cần đổi sang PH)

| Pattern | Count | Files |
|---|---:|---|
| `PercentTaxIndonesia = 12` (constant) | 1 | constants.go:226 |
| Tax usage `PercentTaxIndonesia` | 2 | internal/service/withdraw.go:137 + public/service/schedule.go:789 |
| Phone regex Indonesia `^(?:\+62\|62\|0)...` | 1 (constant) | constants.go:40 |
| FE admin `unit: 'VND'` (??!) | 1 | admin/utils/format.ts:112 (VND lẫn lộn) |
| Contract Bahasa Indonesia (PT. Interspace, Jakarta, luật ID) | 1 file | constants/contract.go (219 dòng) |
| Default locale `id-ID` | 2 | frontend/config/config.ts + admin/config/config.ts |
| `IPCountryCodeID = "ID"` constant | 1 | locale/locale.go:29 |
| Bank common.go `if typeBank != "indo"` + `BeneficiaryForVietinbank` | 2 | admin/service/common.go:150,182 |
| Telegram RoomReconciliationID hardcoded | 1 | reconciliation_running.go:124 |

### PH-specific (cần thêm mới)

| Item | Status |
|---|---|
| `fil-PH` locale folder | ❌ chưa có |
| `IPCountryCodePH = "PH"` constant | ❌ chưa có |
| `+63` phone code/regex | ❌ chưa có |
| `Asia/Manila` timezone | ❌ chưa có |
| PH banks (BDO/BPI/...) | ❌ chưa có data seed |
| PH tax rate constant | ❌ chưa có |
| Contract template PH (luật RA 8792 + DPA 2012) | ❌ chưa có |
| GreenSM PH branding (logo/font/banner) | ⚠️ partner đã cung cấp file design |
| Region config (env-driven) | ❌ chưa có |

---

## Critical bugs (general — không phải PH-specific)

### Backend

| File:Line | Bug | Severity |
|---|---|---|
| `pkg/admin/service/transfer_processing.go:56` | `math.Max(MinValueCashRemaining, MaxCashWithdraw)` — logic inverted, filter sai | 🔴 P0 |
| `pkg/admin/service/staff.go:264` | GetMe() KHÔNG có permission check — staff có thể read profile staff khác | 🔴 P0 SECURITY |
| `pkg/admin/service/staff.go:325` | MongoDB syntax `"$nin": staff.ID` sai (phải là `"_id": bson.M{"$ne":...}`) | 🔴 P0 BUG |
| `pkg/admin/service/staff.go:339` | UpdateInfo cho phép user set `isRoot=true` → privilege escalation | 🔴 P0 SECURITY |
| `pkg/admin/service/staff.go:214` | reCAPTCHA v3 score không validate threshold | 🟡 P1 SECURITY |
| `pkg/admin/service/staff.go:118` | TOTP không có rate limit → brute force 10^6 attempts | 🟡 P1 SECURITY |
| `pkg/public/service/withdraw.go` (toàn file) | DEAD CODE — handler không wire route, logic có bug | 🟡 P1 |
| `pkg/public/service/withdraw.go:64` | `if user.ID.IsZero()` check user mà chưa load → luôn return error | (dead code) |
| `pkg/public/service/withdraw.go:254-255` | TYPO swap field TotalCashRejected ⇄ TotalCashCompleted | (dead code) |
| `pkg/public/service/event.go:296-298` | Sort GetList: boolean sort không stable | 🟡 P1 BUG |
| `pkg/public/service/event.go:574` | GetLeaderBoard không có SortInterface — ranking undefined | 🟡 P1 BUG |
| `pkg/public/service/event.go:314-319` | Commented time-window filter trong GetAllSchema | 🟡 P1 |
| `pkg/public/service/transcript.go:28,38` | `return` thay vì `continue` trong loop → exit cả function | 🟡 P1 BUG |
| `pkg/public/service/referral.go:76` | `cash` return value luôn = 0 | 🟡 P1 |
| `pkg/public/service/news.go:38` | TYPO `"new"` thay vì `"news"` | 🟡 P1 BUG |
| `pkg/public/service/user.go:1797` (isExistedEmail) | Chỉ check `google.email`, không check email khác fields → email trùng có thể đăng ký | 🟡 P1 BUG |
| `pkg/public/service/schedule.go:1408` (UpdateSearchStringContent) | Full table scan không pagination → OOM risk khi DB lớn | 🟡 P1 PERF |
| `internal/service/otp.go:712` (RequestOTP) | Dev mode hardcode OTP `"123456"` | 🟡 P1 (verify ENV) |
| `pkg/public/service/user.go:1639` (GenerateCode) | Recursive uniqueness check không có max depth | 🟢 P2 |

### Frontend

| File:Line | Bug | Severity |
|---|---|---|
| `frontend/src/configs/app.tsx:58` vs `configs/form.ts:3` | Phone prefix VN (`+84`) vs regex Indonesia (`+62`) **conflict** | 🔴 P0 BUG |
| `pkg/public/service/withdraw.go` toàn file | Dead code | (separate) |

---

## Security findings

| Issue | File:Line | Risk |
|---|---|---|
| Auth bypass GetMe() | staff.go:264 | Read any staff profile |
| Privilege escalation isRoot | staff.go:339 | Self-promote to root |
| MongoDB syntax bug $nin | staff.go:325 | Filter not working as intended |
| reCAPTCHA score not enforced | staff.go:214 | Bot login possible |
| TOTP no rate limit | staff.go:118 | Brute force 6-digit |
| Email case sensitivity | staff.go:207 | UX issue, blocks valid logins |
| OTP dev hardcode `123456` | service/otp.go:712 | Production risk if ENV misconfigured |

---

## Modules có business logic clean (không cần touch)

✅ Backend public services clean (chỉ cần dịch text):
- article.go, news.go, common.go, partner.go, quick_action.go, notification.go, transcript.go, user_statistic.go (có code smell nhưng không country leftover)

✅ Backend admin services clean:
- audit.go, cache.go, article.go, event_reward.go (stub), event_schema.go, identification.go, news.go, quick_action.go, role.go, segment.go, tag.go, user_segment.go (12 files)

✅ FE component-level clean (i18n proper):
- Admin FE pages 100% qua i18n
- Creator FE chỉ 7 chỗ tiếng Việt còn sót (đa số trong page tax)

---

## Phone & Timezone util — Design config-driven

### Hiện trạng
- `internal/format/string.go` hardcode `+84` (8 chỗ, phone util core)
- `internal/util/time.go` (294 dòng) + `internal/util/ptime/parse.go` — duplicate HCM functions (15+ functions)
- `internal/constants/constants.go:40` regex `+62`, line 72 `timezoneHCM`, line 226-227 tax constants

### Đề xuất — Config-driven via ENV

Add struct `Region` vào `config/env.go`:

```go
Region struct {
    CountryCode string  `env:"COUNTRY_CODE,required"`     // "PH"
    PhoneCode   string  `env:"PHONE_CODE,required"`        // "+63"
    PhoneRegex  string  `env:"PHONE_REGEX,required"`       // "^(09|\\+639|639)\\d{9}$"
    Timezone    string  `env:"TIMEZONE,required"`          // "Asia/Manila"
    Currency    string  `env:"CURRENCY,required"`          // "PHP"
    TaxPercent  float64 `env:"TAX_PERCENT,required"`       // PH tax rate
    Language    string  `env:"LANGUAGE,required"`          // "fil"
} `env:",prefix=REGION_"`
```

Refactor utilities:
- `format.FormatPhoneCommon()` dùng `cfg.Region.PhoneCode`
- `format.PhoneNumberFormatFromPhone()` dùng `cfg.Region.PhoneCode`
- `util.TimeStartOfDayInRegion()` mới, deprecate `TimeStartOfDayInHCM`
- `util.TimezoneLocation()` — return `time.Location` based on `cfg.Region.Timezone`

→ **Migration strategy**:
1. Add config + new region functions (forward-compatible)
2. Update callsites batch by batch
3. Delete legacy HCM functions cuối cùng

---

## i18n strategy

### Hiện tại
- 3 ngôn ngữ JSON proper: `en-US`, `id-ID`, `vi-VN`
- 3 layers: `locales/{admin,client,server}/` (top-level shared) + `frontend/src/locales/` + `admin/src/locales/`
- Default locale: `id-ID`

### Cần làm cho PH

1. **Add `fil-PH` (Filipino/Tagalog)** — partner yêu cầu file Onboarding §46
2. **Đổi default `id-ID` → `en-US`**
3. **Thêm `IPCountryCodePH = "PH"` + `LangFil = "fil"`** trong `internal/locale/locale.go`
4. **Thêm folder `internal/locale/properties/fil/`** với JSON keys translated
5. **Translate ~3,800 keys** sang Filipino — cần native translator hoặc partner cung cấp text

### Optional cleanup
- Decide: dùng **top-level shared locales** OR **per-app locales** (không nên duplicate cả 2)
- Có thể remove `vi-VN` + `id-ID` để giảm bundle size sau khi launch PH

---

## Modules theo nhóm severity

### P0 BLOCKERS — Phải fix trước launch

| Module | Items |
|---|---|
| Internal phone util | format/string.go phải refactor config-driven (+84 hardcode) |
| Internal timezone | 91 occurrences `*HCM` cần refactor |
| Internal constants | Tax + regex + timezone hardcode |
| Contract template | Rewrite Bahasa Indonesia → EN/Filipino + luật PH |
| Admin staff.go | 4 P0 security bugs |
| Admin transfer_processing | math.Max bug |
| FE phone prefix | configs/app.tsx + form.ts conflict |
| FE admin format | +84 + VND hardcode |
| FE creator pages | 7 chỗ tiếng Việt còn sót (tax page) |
| i18n add fil-PH | 4 JSON files cho 3 layers |
| Locale default | id-ID → en-US |

### P1 IMPORTANT — Fix sớm

- General bugs: event sort, leaderboard, transcript loop, referral cash, news typo
- Security: reCAPTCHA threshold, TOTP rate limit, email case
- Tax intent verification (per-withdraw vs monthly conflict)
- Branch card feature broken/commented (decision: enable OR remove)
- Bank list seed PH

### P2 NICE-TO-HAVE — Sau launch

- Vietnamese comments cleanup (utils files)
- Code dedupe (user_statistic GetStatistic vs GetStatisticInvitee)
- N+1 query optimizations
- Recursion guards
- Search string indexing optimization

---

## Quyết định cần partner clarify

1. **Tax rate PH**: % bao nhiêu? (Indonesia là 12%, PH có thể khác)
2. **Tax model**: Per-withdraw hay monthly cron? (Source hiện có cả 2 — duplicate)
3. **Bank list PH**: BDO/BPI/Metrobank/UnionBank/LandBank/Security Bank/RCBC/PNB? (Cần code chính thức)
4. **Branch card**: Có dùng concept "chi nhánh ngân hàng" không? (Nếu không → uncomment xóa luôn)
5. **eKYC provider**: Manual hay auto? Nếu auto → Jumio/Sumsub/HyperVerge?
6. **SMS provider**: Semaphore/Globe Labs/Twilio/Movider?
7. **Filipino translator**: Partner cung cấp text hay DISO thuê?
8. **Default locale**: en-US hay fil-PH?
9. **Bỏ vi-VN + id-ID locale sau launch PH** không?
10. **Telegram admin notifications**: Channel mới cho PH hay reuse?

---

## Tóm tắt số liệu cleanup

### Backend (Go)

| Layer | Files cần touch | Effort |
|---|---|---|
| Internal (format/util/locale/constants) | ~10 files | L (~2-3 ngày) |
| Public services (user/identification/schedule + other) | ~10 files | L (~2-3 ngày) |
| Admin services (transfer/recon/staff + export + content + event + user + partner + common) | ~15 files | L (~3-4 ngày) |
| Constants/contract template rewrite | 1 file (219 dòng) | M (~1 ngày + legal review) |

### Frontend

| Layer | Effort |
|---|---|
| FE creator config + 7 hardcode | S (~0.5 ngày) |
| Admin FE utils format | S (~0.5 ngày) |
| i18n add fil-PH (4 files × 3,800 keys) | M (~2-3 ngày + translator) |
| Default locale change | S (~30 min) |

### Data init

- PH bank list seed
- PH partner config
- PH staff accounts
- PH event sample

→ M (~1 ngày)

---

## Estimated total effort (rough)

```
Backend cleanup:        ~10 ngày
Frontend cleanup:        ~3 ngày
Translation (Filipino):  ~3 ngày (parallel)
Data init + branding:    ~2 ngày
Testing + UAT:           ~3 ngày
Bug fixes (P0/P1):       ~3 ngày
─────────────────────────────────
Total:                   ~24 ngày dev (with overlap → ~3-4 weeks calendar)
```

→ Khả thi với team 1BE + 1FE + 1QC + 1PM + 1Designer trong ~4 tuần.

---

## Files audit chi tiết (`.tmp/`)

| File | Topic |
|---|---|
| audit-01-overview.md | Codebase overview + state |
| audit-user-service.md | user.go (1896 dòng) deep audit |
| audit-02-schedule-service.md | schedule.go (1976 dòng) — crawl + reward + tax cron |
| audit-03-event-service.md | event.go (860 dòng) — clean module |
| audit-04-withdraw-cashflow.md | withdraw + tax flow |
| audit-05-content-services.md | content + content_callback + content_flow |
| audit-06-small-public-services.md | 10 small public services batch |
| audit-07-admin-core.md | transfer + reconciliation + staff (3 admin core) |
| audit-08-admin-remaining.md | 28 admin services batch |
| audit-09-internal-modules.md | format + util + locale + constants + contract |
| audit-10-frontend.md | FE creator + admin + i18n |
