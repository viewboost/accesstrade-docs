# vCreator Philippines Admin Frontend - Phase 3 Localization Scout Report

**Scope**: `admin/src/` and `admin/config/` only (creator frontend excluded)
**Date**: 2026-04-30

---

## Summary

Found **24 hardcoded VN/ID assumptions** across admin FE that need localization for Philippines (PH/en-PH):
- 9 currency/locale format hardcodes (VND, IDR, locale strings)
- 5 date format hardcodes (DD/MM/YYYY layouts)
- 5 Vietnamese error messages in code
- 3 phone formatting assumptions (+84 → 0)
- 1 import flow language override
- 1 currency symbol regex (₫ dongk)

---

## Phone Hardcodes (admin)

| File | Line | Match |
|------|------|-------|
| `src/utils/format.ts` | 70 | `value = value.replace('+84', '0');` |
| `src/utils/format.ts` | 64–83 | Function `phone()` assumes VN phone formatting (reverse-string logic for display) |

**Impact**: Phone formatting logic hardcoded for VN +84. PH phones (+63) need separate handler.

---

## Currency Hardcodes (admin)

| File | Line | Match |
|------|------|-------|
| `src/utils/format.ts` | 112 | `unit: 'VND',` (in `cashValuePositive` default) |
| `src/utils/format.ts` | 91 | `toLocaleString('id-ID')` |
| `src/utils/format.ts` | 116 | `return '0 ₫';` (Vietnamese dong symbol) |
| `src/utils/format.ts` | 127 | `replace(/\s\₫\|\₫\|\s\|(\.*)/g, '')` (parses VND currency string) |
| `config/config.dev.ts` | 9 | `'process.env.CASH_CURRENCY_STYLE': 'id-ID',` |
| `config/config.dev.ts` | 10 | `'process.env.CASH_CURRENCY_UNIT': 'IDR',` |
| `config/config.prod.ts` | 9 | `'process.env.CASH_CURRENCY_STYLE': 'id-ID',` |
| `config/config.prod.ts` | 10 | `'process.env.CASH_CURRENCY_UNIT': 'IDR',` |

**Status**: `config/config.local.ts` already PH-aware (`CASH_CURRENCY_STYLE='en-PH'`, `CASH_CURRENCY_UNIT='PHP'`).

**Impact**: `cashValuePositive()` still defaults to VND via hardcoded locale `'vi-VI'` and unit. Format functions use process.env, but fallback logic broken.

---

## Locale / Language Hardcodes (admin)

| File | Line | Match |
|------|------|-------|
| `src/utils/request.ts` | 88–89 | `case 'vi-VN': language = 'vi';` (request header language) |
| `src/utils/request.ts` | 91–92 | `case 'id-ID': language = 'id';` |
| `src/utils/request.ts` | 211 | `const language = 'vi';` (in `processOptionsImport()` — hardcoded VN!) |
| `config/config.ts` | 21 | `default: 'en-US',` (locale default is en-US, acceptable for PH) |

**Impact**: Import flow (`processOptionsImport()`) sends hardcoded `'vi'` Accept-Language. No PH case. Needs `'fil'` or `'en'` for PH.

---

## Date Format Hardcodes (admin)

| File | Line | Match |
|------|------|-------|
| `src/configs/app.ts` | 28 | `date: 'DD/MM/YYYY, HH:mm',` |
| `src/configs/app.ts` | 29 | `dateWithNoHour: 'DD/MM/YYYY',` |
| `src/configs/app.ts` | 32 | `dateWithSecond: 'DD/MM/YYYY, HH:mm:ss',` |
| `src/configs/app.ts` | 36 | `dateHourFirst: 'HH:mm DD/MM/YYYY',` |
| `src/utils/format.ts` | 175, 179, 181 | `'DD/MM/YYYY'` in moment calendar config (lastWeek, nextWeek, sameElse) |

**Impact**: DD/MM/YYYY format is acceptable for PH (used regionally). Low priority, but centralizing in a config constant is recommended for consistency.

---

## Vietnamese UI Strings in Code (admin)

| File | Line | Match | Context |
|------|------|-------|---------|
| `src/utils/helper.tsx` | 413 | `Những sản phẩm không hợp lệ: ` | "Invalid products:" — displayed in import error node |
| `src/utils/helper.tsx` | 422 | `symbol: 'Xem thêm',` | "View more" expand symbol |
| `src/utils/upload.ts` | 19 | `'Bạn chỉ có thể tải lên tệp JPG/PNG/JPEG!'` | "You can only upload JPG/PNG/JPEG files!" |
| `src/utils/upload.ts` | 23 | `` `Hình ảnh phải nhỏ hơn ${imageSize}MB!` `` | "Image must be smaller than X MB!" |
| `src/utils/upload.ts` | 38 | `` `Bạn chỉ có thể tải lên tệp video định dạng mov\|avi\|wmv\|flv\|3gp\|mp4\|mpg\|webm\|mkv!` `` | "You can only upload video in formats..." |
| `src/utils/upload.ts` | 43 | `` `Video nên nhỏ hơn ${videoSize}MB!` `` | "Video should be smaller than X MB!" |
| `src/utils/upload.ts` | 54 | `` `File nên nhỏ hơn ${fileSize}MB!` `` | "File should be smaller than X MB!" |

**Impact**: 7 hardcoded Vietnamese strings in utility functions (not locales/ dir). These should be moved to translation keys or i18n calls. Currently will break for PH users.

---

## Other VN/ID Assumptions (admin)

| File | Line | Match |
|------|------|-------|
| `src/utils/format.ts` | 130–158 | Function `removeVietnameseTones()` — removes Vietnamese diacritics. Utility function, not user-facing; acceptable. |
| `src/utils/format.ts` | 221–245 | Function `stringToSlugSupplier()` — includes Vietnamese char replacements. Used for slug generation, not user-facing; acceptable. |

---

## reCAPTCHA Keys

- `config/config.local.ts` line 8: Demo key (used for dev/testing)
- `config/config.dev.ts` line 8: Dev key (Indonesia-specific)
- `config/config.prod.ts` line 8: Prod key (Indonesia-specific)

**Note**: These are environment-specific. For PH prod, a PH-specific reCAPTCHA key is needed.

---

## Effort Estimate

**Ballpark: ~6-8 hours** to make admin FE PH-clean, assuming:

1. **Translation strings** (7 hardcoded VN messages in upload/helper): ~2 hours
   - Move to `src/locales/en-PH.json` (add PH locale file if missing)
   - Replace inline strings with i18n keys in `src/utils/upload.ts` and `src/utils/helper.tsx`

2. **Phone formatting** (2 affected lines): ~1 hour
   - Add PH phone handler in `phone()` function or detect country dynamically
   - Remove hardcoded +84 → 0 replacement; use country-aware logic

3. **Currency/locale defaults** (hardcoded VND, vi-VI, id-ID in configs + functions): ~2 hours
   - Fix `cashValuePositive()` default from `'vi-VI'` → use process.env or PH config
   - Ensure config.dev/prod have PH equivalents for `CASH_CURRENCY_STYLE` and `CASH_CURRENCY_UNIT`
   - Fix import flow `processOptionsImport()` to handle PH language header (line 211)

4. **Date formats** (5 hardcodes): ~1 hour
   - Already acceptable (DD/MM/YYYY works in PH), but consolidate to config constant for future flexibility

5. **Testing + edge cases**: ~1–2 hours
   - Verify locale switching (umi locale plugin) includes en-PH or 'fil'
   - Test currency formatting, phone display, error messages with PH config

**Most painful**: Translation strings are scattered (not centralized in i18n service). Effort heavily frontloaded on hunting down all user-facing text. Currency defaults need careful cascade audit (process.env → function parameter → fallback).
