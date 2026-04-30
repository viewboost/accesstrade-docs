# Phase 3 Code Review — GreenSM PH Localization

**Date:** 2026-04-30  
**Reviewer:** code-reviewer  
**Scope:** Working-tree diff for Phase 3 (REPL-01–05, FE-01 admin)

---

## Summary Table

| # | Concern | Verdict | Severity |
|---|---------|---------|----------|
| 1 | Vietinbank rename safety | ✅ Pass | — |
| 2 | `LocalPhoneFromFull` correctness | ✅ Pass | — |
| 3 | `PhoneNumberIsValid` regex recompile | ⚠ Caution | Low |
| 4 | `schedule_not_eligible_at` locale `%s` | ✅ Pass | — |
| 5 | `UploadContract` early-return before `LocalPhoneFromFull` | ✅ Pass | — |
| 6 | `parseCurrency` decimal stripping | ⚠ Caution | Medium |
| 7 | i18n key collisions | ✅ Pass | — |
| 8 | General hygiene | ⚠ Caution | Low |

---

## Per-Concern Detail

### 1. Vietinbank rename safety — ✅ Pass

`internal/model/mg/bank.go:28` — Go field `BeneficiaryName` carries `bson:"beneficiaryForVietinbank"`. BSON tag preserved; existing Mongo documents unaffected.

`pkg/admin/service/common.go:48` — `BankResponse.BeneficiaryName` carries `json:"beneficiaryForVietinbank"`. Wire contract intact; `bank.json` keys (`"beneficiaryForVietinbank"`) match at lines 9, 17, 25, etc.

No callsite uses the old Go field name `BeneficiaryForVietinbank`; the only consumer is `common.go:183` which correctly uses `item.BeneficiaryName` (the new Go name on the `BankResponse` struct, whose JSON tag reads from JSON). Clean.

---

### 2. `LocalPhoneFromFull` correctness — ✅ Pass

`internal/format/phone.go:97`:
```go
return strings.Replace(full, pre, "0", 1)
```
Behavior: replaces only the first occurrence of the prefix literal. For `"+639171234567"` with `pre="+63"` → `"09171234567"`. Semantically identical to the legacy `strings.Replace(full, "+84", "0", 1)`. The `+` is a string literal (not regex) in both Go and the FE (`value.replace('+63', '0')`) — no regex metachar issue.

Edge case (prefix mid-string): theoretically possible if a user entered a number like `"+630963..."`, but `strings.Replace` with `n=1` would still mutate only the leading prefix. Practically impossible in a properly-validated phone. Acceptable.

Empty-prefix guard (`pre == ""` returns `full` unchanged) is correct.

---

### 3. `PhoneNumberIsValid` regex recompile — ⚠ Caution (Low)

`internal/format/phone.go:82`:
```go
func PhoneNumberIsValidRegion(phone string) bool {
    r := regexp.MustCompile(config.GetENV().Region.PhoneRegex)
    return r.MatchString(phone)
}
```
The regex is re-compiled on every call. Previously the legacy VN behavior in `string.go` had the same pattern. Current callers are on per-request HTTP paths (registration, login, identification) — not tight loops. Performance impact is low but non-zero.

No race condition: `config.GetENV()` returns a pointer to the package-level `env` struct which is initialized in `initialize/initialize.go:14` (`config.Init()`) before any HTTP handler runs. Safe.

**Suggested fix (non-blocking):** compile once with `var phoneRegexp = sync.OnceValue(func() *regexp.Regexp { return regexp.MustCompile(config.GetENV().Region.PhoneRegex) })` or cache in a package-level var after config init. Low urgency.

---

### 4. `schedule_not_eligible_at` locale — ✅ Pass

`pkg/public/service/schedule.go:745`:
```go
fmt.Sprintf(locale.GetMessageByKey(config.GetENV().Region.Language, locale.ScheduleNotEligibleAt),
    util.TimeOfDayInRegion(time.Now()).Format(constants.FormatTimeDDMMYYYY))
```

All three locale JSON files contain `%s` as the format verb:
- `locales/server/en.json:347` → `"Currently not eligible at %s"`
- `locales/server/vi.json:347` → `"Hiện tại, không thỏa điều kiện %s"`
- `locales/server/id.json:347` → `"Saat ini tidak memenuhi syarat pada %s"`

`fmt.Sprintf` with one `%s` arg and one string arg is correct. No issue.

---

### 5. `UploadContract` early-return vs `LocalPhoneFromFull` — ✅ Pass

**Admin service** (`pkg/admin/service/user.go:156–161`): `UploadContract` returns `"", nil` immediately when `constants.ContractTemplate == ""`. `LocalPhoneFromFull` is called at line 189, which is inside the function body **after** that guard. If template is empty, line 189 is never reached.

**Public service** (`pkg/public/service/user.go:101–125`): `LocalPhoneFromFull` is called at line 113 inside `AgreeTermAndCondition`, which constructs `dataSign` before calling `UploadContract`. The `ContractTemplate == ""` guard is inside `UploadContract` (line 668), which receives `dataSign` as a pre-built struct. The `LocalPhoneFromFull` call executes unconditionally, but since `UploadContract` returns early anyway and the result isn't used elsewhere, this is a minor inefficiency, not a bug.

---

### 6. `parseCurrency` decimal stripping — ⚠ Caution (Medium)

`admin/src/utils/format.ts:123`:
```ts
const parseCurrency = (value: any) => {
  return Number.parseInt(value?.replace(/[^\d-]/g, ''));
};
```

The regex `/[^\d-]/g` strips everything that isn't a digit or `-`. This includes the decimal point `.`.

**PHP vs legacy behavior:**
- IDR (`id-ID`): `Intl.NumberFormat('id-ID', {style:'currency', currency:'IDR'}).format(100)` → `"Rp 100"` (no decimal places). Legacy parser: no `.` to strip. No bug.
- PHP (`en-PH`): `Intl.NumberFormat('en-PH', {style:'currency', currency:'PHP'}).format(100)` → `"₱100.00"`. Parser strips `.` → `"10000"` → `parseInt` = `10000` ≠ `100`. **100× inflation.**

**Is this triggered?** Only one caller: `form-input-number/index.tsx:91` with `type="currency"`. Grep across all pages shows `RcInputNumberFormNew` is used in two reconciliation modals but **none of the found usages pass `type="currency"` as a prop** (no `type` prop visible in those instances, defaulting to plain number formatter). So this is latent but not currently triggered.

**If any future component adds `type="currency"`, numeric input will silently submit 100× the intended value.** This is a correctness trap.

**Fix:**
```ts
const parseCurrency = (value: any) => {
  // Strip currency symbols and thousand separators; preserve decimal point.
  const cleaned = value?.replace(/[^\d.-]/g, '') ?? '';
  return Math.round(parseFloat(cleaned) * 100) / 100;
};
```
Or simpler for PH whole-peso amounts: use `minimumFractionDigits: 0` in `cashValue` to avoid emitting decimals.

---

### 7. i18n key collisions — ✅ Pass

New keys added by FE-01:
- `upload.error.imageType` (line 409), `.imageSize`, `.videoType`, `.videoSize`, `.fileSize`

These appear exactly once in each of `en-US.json`, `vi-VN.json`, `id-ID.json`. No duplicates found. All five keys have matching entries in all three locale files. No collision.

`helper.tsx:167,169,176,178` still uses the deprecated alias `removeVietnameseTones`; the alias is correctly exported in `format.ts:256`. Not a bug.

---

### 8. General hygiene — ⚠ Caution (Low)

**a. `internal/format/string.go` — `FormatPhoneCommon` still hardcodes `+84`** (lines 30, 34). This function is not in Phase 3 scope (no callers in the changed files were listed), but it's a stale VN-specific function that will confuse future PH developers. Not introduced by Phase 3, but now more visible as the only remaining `+84` literal in the format package. Low urgency.

**b. `processOptionsImport` in `request.ts:213`** uses `stored.split('-')[0]` which correctly handles `'en-US'→'en'`, `'vi-VN'→'vi'`, `'id-ID'→'id'`. Meanwhile `processOptions` (line 85) uses a full `switch` statement for the same purpose. The two implementations now diverge in style. Not a bug, but inconsistent.

**c. No orphaned imports found.** `internal/format/phone.go` imports `regexp` and `strings` — both are used. `internal/constants/constants.go` imports only `time` — correct after deletions.

**d. `FormatTimeDDMMYYYY` constant** used at `schedule.go:745` — PH date format is typically `MM/DD/YYYY`. If this constant is `"02/01/2006"` (Vietnamese convention), the schedule rejection note will show a month/day-swapped date to PH users. Not introduced by Phase 3 (constant predates it), but worth flagging.

---

## Recommended Actions

1. **(Fix before merge — Medium)** `parseCurrency` in `format.ts:123`: strip `.` corrupts PHP decimal values if `type="currency"` is ever used. Fix the regex or suppress decimals in the formatter. Safe to land with a comment noting it's latent, but clean it now while the file is open.

2. **(Low — next sprint)** Cache `regexp.MustCompile` in `PhoneNumberIsValidRegion` to avoid per-call compilation. A `sync.OnceValue` or package-level `var` after `config.Init()` is the cleanest approach.

3. **(Low — follow-up)** `FormatPhoneCommon` in `string.go` still hardcodes `+84`. Add a deprecation comment pointing to `FormatPhoneRegion`.

4. **(Low — follow-up)** Align `processOptions` and `processOptionsImport` in `request.ts` to use the same locale-parsing strategy.

---

## If you only have time to fix one thing

**Fix `parseCurrency`** (`admin/src/utils/format.ts:123`). The regex currently strips the decimal separator, which will silently 100× any PHP currency value the moment `type="currency"` is passed to `RcInputNumberFormNew`. All other findings are either confirmed correct or low-risk latent issues.
