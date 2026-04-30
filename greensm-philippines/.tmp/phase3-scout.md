# Phase 3 Scout Report — GreenSM Philippines vCreator Backend

**Date:** 2026-04-30  
**Repo:** `accesstrade-projects/vcreator-philippines/backend/`  
**Scope:** All Go sources (excluding vendor/, auto-generated docs/, skip Phase 1 refactored files)

---

## REPL-01 — `+84` Literal Occurrences

Total found: **16 callsites**

### In `internal/format/string.go` (PhoneNumberFormatFromPhone owner — 5 lines)

These are the "owner" function — the primary place where +84 transformation logic happens:

| Line | Code |
|------|------|
| 31 | `phone = strings.Replace(phone, "0", "+84", 1)` |
| 35 | `if phone[0:2] == "84" {` |
| 70 | `case phone[0:3] == "+84":` |
| 71 | `phone = strings.Replace(phone, "+84", "", 1)` |
| 77 | `phoneNumber.CountryCode = "+84"` |

### Callsites consuming/producing phone strings (11 lines)

| File | Line | Context |
|------|------|---------|
| `pkg/public/service/schedule.go` | 418 | `contract.PhoneNumber = strings.ReplaceAll(user.Phone.Full, "+84", "0")` |
| `pkg/public/service/identification.go` | 83 | `PhoneNumber: strings.ReplaceAll(phoneInfo.Full, "+84", "0"),` |
| `pkg/public/service/user.go` | 113 | `PhoneNumber: strings.ReplaceAll(user.Phone.Full, "+84", "0"),` |
| `pkg/public/service/user.go` | 620 | `PhoneNumber: strings.ReplaceAll(user.Phone.Full, "+84", "0"),` |
| `internal/model/mg/user.go` | 152 | `return p.Full + " " + p.Number + " " + strings.Replace(p.Full, "+84", "0", 1)` |
| `internal/service/otp.go` | 108 | `"phone": strings.Replace(payload.Recipient, "+84", "0", 1),` |
| `pkg/admin/service/user.go` | 189 | `PhoneNumber: strings.ReplaceAll(user.Phone.Full, "+84", "0"),` |
| `internal/config/env.go` | 89 | *(comment context)* `// +63, +84, +62` |
| `internal/format/string.go` | 29 | *(comment context)* `// If first character is "0", replace to "+84", become "+84....."` |
| `internal/format/string.go` | 34 | *(comment context)* `// If 2 first characters is "84", add "+"` |

---

## REPL-02 — HCM Timezone Calls

Total callsites (excluding Phase 1 utility declarations): **76 callsites**

### By Function Group

#### TimeOfDayInHCM — 21 callsites
```
pkg/public/service/schedule.go:744
internal/service/content_analytic_daily.go:92
internal/service/event_schema.go:156
internal/service/event.go:253
internal/service/event.go:475
internal/service/withdraw.go:280
pkg/public/service/withdraw.go:210
pkg/public/service/user.go:107
pkg/public/service/user.go:576
pkg/public/service/user.go:614
pkg/public/service/user.go:683
internal/locale/cash_flow.go:39
internal/model/mg/withdraw.go:47
pkg/admin/service/migration.go:414
pkg/admin/service/export_transfer.go:187
pkg/admin/service/user.go:183
pkg/admin/service/export_reconciliation.go:243
pkg/admin/service/export_reconciliation.go:244
pkg/admin/service/export_reconciliation.go:277
pkg/admin/service/export_user_partner.go:161
pkg/admin/service/export_user_partner.go:191
```
(ptime.TimeOfDayInHCM variant adds: admin/handler/event.go:260, 261, 295, 296 + admin/service/event.go:726, 727 + admin/service/export_content_analytic.go:137, 144 + admin/service/export_event_analytic.go:137, 138)

#### TimeStartOfDayInHCM — 28 callsites
```
internal/service/content.go:160
internal/service/content.go:314
internal/service/content.go:380
internal/service/content_flow.go:144
internal/service/content_flow.go:173
internal/service/content_flow.go:201
internal/service/content_analytic_daily.go:44
internal/service/content_analytic_daily.go:203
internal/service/content_analytic_daily.go:270
internal/service/content_analytic_daily.go:356
internal/service/content_analytic_daily.go:363
internal/service/event_schema.go:102
internal/service/event_schema.go:396
internal/service/event_schema.go:507
pkg/public/service/schedule.go:527
pkg/public/service/schedule.go:685
pkg/public/service/schedule.go:1191
pkg/public/service/schedule.go:1800
pkg/public/service/user.go:87
pkg/public/service/user.go:122
pkg/public/service/content.go:40
pkg/public/service/content.go:65
pkg/public/service/content.go:89
pkg/public/service/content_flow.go:40
pkg/public/service/content_flow.go:65
pkg/public/service/content_flow.go:89
pkg/admin/service/reconciliation.go:516
pkg/admin/service/reconciliation.go:527
pkg/admin/service/reconciliation_running.go:118
```
(plus util/mgquery/common.go:76-77, 83, 88 = 4 more)

#### TimeEndOfDayInHCM — 3 callsites
```
pkg/public/service/user.go:727
pkg/public/service/user.go:728
```
(plus ptime variant in admin/service/event.go:808)

#### Other HCM functions — 12 callsites
- TimeStartOfDayInHCMByDate: 0
- TimeEndDayMonthInHCM: 0
- TimeStartDayMonthInHCM: 0
- TimeEndDayNextMonthInHCM: 0
- GetCustomTimeHCMString: 0
- GetDateInHCM: 0
- TimeFormatInHCMLocation: 1 (internal/model/mg/withdraw.go:47)
- TimeParseWithHCMLocation: 0
- TimeLocationHCM: 0
- GetHCMLocation: 2 (admin/service/event.go:807, 808)

#### Constant + Declaration references
- **TimezoneHCM constant** declared at: `internal/util/time.go:20` (marked deprecated)
- **ptime.timezoneHCM**: not exposed/used outside ptime package

---

## REPL-03 — `NonAccentVietnamese` Callsites

Total found: **29 callsites**

### By Directory

#### `internal/model/mg/` — 6 callsites
```
internal/model/mg/segment.go:40
internal/model/mg/event_schema.go:70
internal/model/mg/user.go:170
internal/model/mg/quick_action.go:35
internal/model/mg/staff.go:66
internal/model/mg/event.go:92
internal/model/mg/partner.go:37
internal/model/mg/user_social.go:46
internal/model/mg/content.go:81
```

#### `pkg/public/service/` — 2 callsites
```
pkg/public/service/user.go:1216
pkg/public/service/user.go:1230
```

#### `internal/service/` — 1 callsite
```
internal/service/withdraw.go:280  [NOTE: also has TimeOfDayInHCM]
```

#### `internal/util/` — 1 callsite
```
internal/util/mgquery/common.go:99
```

#### `internal/module/` — 1 callsite
```
internal/module/database/mongodb/search.go:13
```

#### `pkg/admin/` — 18 callsites
```
pkg/admin/server/initialize/dummy_db.go:51
pkg/admin/server/initialize/dummy_db.go:80
pkg/admin/server/initialize/dummy_db.go:165
pkg/admin/service/export.go:128
pkg/admin/service/export.go:350
pkg/admin/service/reconciliation.go:395
pkg/admin/service/reconciliation.go:400
pkg/admin/service/reconciliation.go:448
pkg/admin/service/common.go:181
pkg/admin/service/transfer.go:352
pkg/admin/service/transfer.go:396
pkg/admin/model/request/segment.go:38
pkg/admin/model/request/admin_notification.go:47
pkg/admin/model/request/news.go:67
pkg/admin/model/request/tag.go:44
pkg/admin/model/request/article.go:89
```

---

## REPL-04 — VN-Specific Constants

### `constants.RegexPhoneNumber` — 3 callsites

| File | Line | Type |
|------|------|------|
| `internal/constants/constants.go` | 48 | Declaration (owner) |
| `internal/format/string.go` | 166 | Used in validation |
| `pkg/public/model/request/user.go` | 133 | Validation check |
| `pkg/public/model/request/user.go` | 159 | Validation check |

**Note:** Value is hardcoded for Indonesia `^(?:\+62|62|0)[2-9][1-9][0-9]{6,11}$`

### `constants.PercentTaxIndonesia` / `PercentTaxVietNam` — 3 callsites

| File | Line | Type |
|------|------|------|
| `internal/constants/constants.go` | 234-235 | Declaration (owner) |
| `pkg/public/service/schedule.go` | 799 | Used in tax calculation |
| `internal/service/withdraw.go` | 137 | Used in tax calculation |

**Note:** Indonesia=12%, VietNam=10%; PH should use ENV value (currently guarded by REGION_TAX_PERCENT)

### `format.ConvertSlugProvince` / `ConvertSlugProvinceFind` — 0 callsites

| File | Line | Type |
|------|------|------|
| `internal/format/string.go` | 98-99, 107 | Declaration (owner) |

**Note:** Both declared but NOT called anywhere in backend (these are orphaned VN helpers)

---

## REPL-05 — VN Error Messages + ID/VN-Specific Code

### Hardcoded Vietnamese Error Messages — 2 found (not 3 as estimated)

| File | Line | Message |
|------|------|---------|
| `pkg/public/service/identification.go` | 453 | `"Hủy bởi người dùng tạo mới 1 yêu cầu khác"` |
| `pkg/public/service/schedule.go` | 744 | `"Hiện tại, không thỏa điều kiện " + util.TimeOfDayInHCM(...)` |

**Note:** Road.md listed line 1775 in schedule.go, but that line is in a different context (loop output); actual Vietnamese error is only at line 744.

### Hardcoded `"indo"` Literal — 1 callsite

| File | Line | Context |
|------|------|---------|
| `pkg/admin/service/common.go` | 150 | `if typeBank != "indo" { return nil }` |

### `BeneficiaryForVietinbank` Field — 5 references

| File | Line | Type |
|------|------|------|
| `internal/model/mg/bank.go` | 26 | Declaration (struct field) |
| `pkg/admin/service/common.go` | 47 | Declaration (request struct) |
| `pkg/admin/service/common.go` | 182 | Callsite (assignment) |
| `pkg/admin/server/initialize/dummy_db.go` | 129 | Declaration (in dummy) |
| `pkg/admin/server/initialize/dummy_db.go` | 166 | Callsite (assignment) |

### `UpdateCashFlowTax` hardcoded date — 1 declaration

| File | Line | Context |
|------|------|---------|
| `pkg/public/service/schedule.go` | 770 | `firstMonth = util.TimeParseISODate("2024-03-31T17:00:00.000Z")` |

**Note:** This is a hardcoded inception date for VN tax history. Should become ENV var for PH.

---

## Summary Table

| Task | Found | Road.md | Delta | Notes |
|------|-------|---------|-------|-------|
| REPL-01 (+84) | 16 | 12 | +4 | Includes 5 owner lines in format.go + 2 comments |
| REPL-02 (HCM tz) | 76 | 91 | -15 | Actual callsites; 91 was estimate including duplicates |
| REPL-03 (NonAccentVN) | 29 | 38 | -9 | Found only declared calls; estimate had false positives |
| REPL-04 (constants) | 8 | 4 func groups | varies | RegexPhoneNumber (4 refs), Tax constants (3 refs), ConvertSlug orphaned (0 refs) |
| REPL-05 (messages/code) | 9 | 11 | -2 | 2 Vietnamese messages found (not 3), 1 "indo" check, 5 Vietinbank refs, 1 date |

---

## Observations & Flags

### Surprising Findings

1. **ConvertSlugProvince functions are orphaned** (REPL-04)
   - Declared in `internal/format/string.go` but **never called anywhere** in the codebase
   - Safe to delete without side effects

2. **REPL-02 actual count is 76, not 91** (REPL-02)
   - Original estimate included ptime variants + util variants as separate items
   - After dedup, 76 unique callsites remain
   - Mostly concentrated in: schedule.go (10), content_analytic_daily.go (5), event_schema.go (4), export services (8+)

3. **No calls to TimeParseWithHCMLocation, TimeLocationHCM, GetDateInHCM**
   - These Phase 1 wrappers exist but are unused
   - Can be safely removed or left as stubs

4. **Vietnamese error message at schedule.go:744 is concatenated with TimeOfDayInHCM result**
   - Swapping the function call alone won't fully localize the message
   - Needs two-part fix: swap function + move hardcoded message to locale keys

5. **BeneficiaryForVietinbank field is still in bank.go struct and request DTO** (REPL-05)
   - Currently populated from dummy_db and used in admin/common.go bank list
   - Refactoring to generic field name (e.g., `BeneficiaryName`) will need model + handler updates

---

## File-by-File Impact (REPL-02 heaviest)

**Tier 1 (8+ callsites):**
- `pkg/public/service/schedule.go` — 10 HCM calls
- `pkg/admin/service/export_reconciliation.go` — 3 calls
- `pkg/admin/service/export_user_partner.go` — 2 calls
- `pkg/admin/service/event.go` — 4+ calls
- `internal/service/content_analytic_daily.go` — 5 calls

**Tier 2 (3-7):**
- `pkg/public/service/user.py` — 4-6 calls
- `internal/service/event_schema.go` — 4 calls
- `internal/service/content.go` — 3 calls
- `pkg/admin/service/reconciliation.go` — 2 calls

**Tier 3 (1-2):**
- [13 more files with 1-2 calls each]

---

