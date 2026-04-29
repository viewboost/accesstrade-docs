# Audit 08: Admin Remaining Services Batch

**Files audited:** 28 admin service files (~10,000 LOC excl. transfer/recon/staff đã audit trước)

---

## Summary table

| File | Functions | LOC | Country issues | Verdict |
|---|---:|---:|---|---|
| admin_notification.go | 16 | 680 | None | ⚠️ Minor (debug pretty.Printer) |
| article.go | 6 | 197 | None | ✅ clean |
| audit.go | 3 | 80 | None | ✅ clean |
| cache.go | 3 | 30 | None | ✅ clean |
| common.go | 6 | 192 | line 150 `"indo"`, 181 NonAccentVietnamese, 182 BeneficiaryForVietinbank | 🔴 CRITICAL |
| content.go | 12 | 708 | line 99 TimeStartOfDayInHCM | 🔴 HIGH |
| content_manual_flow.go | 6 | 216 | lines 86, 173 TimeStartOfDayInHCM | 🔴 HIGH |
| event.go | 21 | 969 | lines 147, 189 RemoveAccentVietnamese; 726-727, 807-808 TimeOfDayInHCM/GetHCMLocation | 🔴 CRITICAL |
| event_reward.go | 1 | 11 | None (stub) | ✅ clean |
| event_schema.go | 9 | 282 | None | ✅ clean |
| export.go | 9 | 357 | lines 128, 350 NonAccentVietnamese | 🔴 HIGH |
| export_content.go | 2 | 241 | lines 231-232 TimeOfDayInHCM | 🔴 HIGH |
| export_content_analytic.go | 2 | 201 | lines 137, 144 TimeOfDayInHCM | 🔴 HIGH |
| export_event_analytic.go | 4 | 358 | lines 137-138, 145, 267-268 TimeOfDayInHCM/GetHCMLocation | 🔴 CRITICAL |
| export_reconciliation.go | 4 | 280 | lines 243-244, 277 TimeOfDayInHCM | 🔴 HIGH |
| export_transfer.go | 3 | 209 | line 187 TimeOfDayInHCM | 🔴 HIGH |
| export_transfer_user_cash.go | 2 | 183 | None visible | ⚠️ check |
| export_user_partner.go | 3 | 194 | lines 161, 191 TimeOfDayInHCM | 🔴 HIGH |
| identification.go | 7 | 321 | None | ✅ clean |
| migration.go | 12 | 773 | line 414 TimeOfDayInHCM | 🔴 HIGH (one-time scripts) |
| news.go | 10 | 284 | None | ✅ clean |
| partner.go | 11 | 362 | lines 163, 206 RemoveAccentVietnamese | 🔴 CRITICAL |
| quick_action.go | 8 | 298 | None | ✅ clean |
| role.go | 2 | 67 | None | ✅ clean |
| segment.go | 8 | 205 | None | ✅ clean |
| shedule.go | 11 | 513 | line 500 TimeStartOfDayInHCM | 🔴 HIGH |
| tag.go | 6 | 189 | None | ✅ clean |
| user.go | 14 | 463 | line 178 TimeOfDayInHCM, line 184 `+84` hardcode | 🔴 CRITICAL |
| user_segment.go | 7 | 300 | None | ✅ clean |

---

## Files cần đặc biệt note

### 1. user.go — 🔴 CRITICAL
- **Line 178**: `confirmAt := util.TimeOfDayInHCM(user.Contract.ConfirmAt)` — VN tz cho contract confirmation
- **Line 184**: `PhoneNumber: strings.ReplaceAll(user.Phone.Full, "+84", "0")` — VN code hardcode

### 2. event.go — 🔴 CRITICAL
- Lines 147, 189: `format.RemoveAccentVietnamese(body.Code)` cho event slug — sẽ corrupt Filipino names (ñ, á)
- Lines 726-727, 807-808: `ptime.TimeOfDayInHCM` + `ptime.GetHCMLocation()` cho event analytics

### 3. partner.go — 🔴 CRITICAL
- Lines 163, 206: `format.RemoveAccentVietnamese(partner.Slug)` cho partner slug

### 4. common.go — 🔴 CRITICAL
- **Line 150**: `if typeBank != "indo"` — hardcode Indonesia type check trong bank generation
- **Line 181**: `SearchString: format.NonAccentVietnamese(...)` cho bank search
- **Line 182**: `BeneficiaryForVietinbank` — field rõ ràng VN bank trong source PH

### 5. Export files cascade (timezone)
- export_content.go:231-232
- export_content_analytic.go:137, 144
- export_event_analytic.go:137-138, 145, 267-268
- export_reconciliation.go:243-244, 277
- export_transfer.go:187
- export_user_partner.go:161, 191
- export.go:128, 350 (NonAccentVietnamese cho filename)

### 6. Schedule/timing files
- content.go:99
- content_manual_flow.go:86, 173
- migration.go:414
- shedule.go:500

---

## Aggregate cleanup tasks

| Task ID | File:Line | Description | Priority | Effort |
|---|---|---|---|---|
| ADMIN-R-01 | user.go:184 | Replace `+84` hardcode | P0 | S |
| ADMIN-R-02 | user.go:178 | Replace TimeOfDayInHCM | P0 | S |
| ADMIN-R-03 | event.go:147, 189 | Replace RemoveAccentVietnamese cho slug | P0 | S |
| ADMIN-R-04 | event.go:726-727, 807-808 | Replace TimeOfDayInHCM/GetHCMLocation | P0 | S |
| ADMIN-R-05 | partner.go:163, 206 | Replace RemoveAccentVietnamese | P0 | S |
| ADMIN-R-06 | common.go:150 | Replace `"indo"` typeBank check | P0 | S |
| ADMIN-R-07 | common.go:181 | Replace NonAccentVietnamese | P0 | S |
| ADMIN-R-08 | common.go:182 | Refactor BeneficiaryForVietinbank field | P0 | M |
| ADMIN-R-09 | export_*.go (7 files) | Replace TimeOfDayInHCM/GetHCMLocation toàn bộ | P0 | M |
| ADMIN-R-10 | export.go:128, 350 | Replace NonAccentVietnamese cho filename | P1 | S |
| ADMIN-R-11 | content.go:99, content_manual_flow.go:86,173 | Replace TimeStartOfDayInHCM | P0 | S |
| ADMIN-R-12 | shedule.go:500 | Replace TimeStartOfDayInHCM | P0 | S |
| ADMIN-R-13 | migration.go:414 | Replace TimeOfDayInHCM (one-time script — low priority) | P2 | S |

---

## Clean files (12 files — không cần touch)

- audit.go, cache.go, article.go, event_reward.go (stub), event_schema.go
- identification.go, news.go, quick_action.go, role.go, segment.go, tag.go, user_segment.go

---

## Verdict

✅ **12/28 admin files SẠCH country leftover**

🔴 **15/28 files có HCM timezone hoặc NonAccentVietnamese hardcode**

→ Pattern: country leftover **tập trung ở functions xử lý time (export reports, scheduling) + slug/search string normalization (event/partner names)**.

→ Fix một lần khi làm phone util + timezone util config-driven (sẽ design ở step tiếp).
