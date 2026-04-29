# Audit Report: Content Services (Philippines Port)
**File location:** `/Users/vinhnguyen/workspaces/diso/accesstrade-projects/vcreator-philippines/backend/pkg/public/service/`
**Date:** 2026-04-29
**Status:** Read-only analysis

---

## Section 1: Function Inventory

### content.go (290 lines)

| Function | Line | Signature | Body Summary | Country Issues |
|----------|------|-----------|--------------|-----------------|
| `Create()` | 45 | `Create(ctx context.Context, eventId, userId modelmg.AppID, body request.CreateContentBody) error` | Main content submission entry point. Auto-detects social platform from URL, fetches content metadata via content-catcher, validates event constraints (source, max-per-day), checks hashtags, validates publish date range, deduplicates content, inserts into DB, triggers async flow creation. | 🔴 Line 87: HCM timezone hardcoded (line 87). 🔴 Line 122: HCM timezone again. 🔴 Lines 137-140: Vietnamese placeholder text hardcoded. 🔴 Line 140: viewboost.vn domain hardcoded. |
| `GetAccessToken()` | 266 | `GetAccessToken(ctx context.Context, userSocialId primitive.ObjectID) (string, error)` | Retrieves TikTok access token from user social record. Checks token expiry, renews if expired, updates user status to inactive on failure. | 🟢 No VN-specific logic. Uses generic locale keys. |

### content_callback.go (133 lines)

| Function | Line | Signature | Body Summary | Country Issues |
|----------|------|-----------|--------------|-----------------|
| `Create()` | 29 | `Create(ctx context.Context, payloadContent request.ContentCallbackCreateBody) error` | Webhook receiver from content-catcher service. Loops through callback data items, validates link exists in existing URLs, upserts link + metadata into DB with status="waiting". Pipeline aggregates existing links to verify match. | 🔴 Line 34: Vietnamese comment "Lặp qua từng phần tử trong mảng data" (should be English). 🟢 No hardcoded country logic in flow itself. |
| `GetAll()` | 108 | `GetAll(ctx context.Context, status string) ([]*modelmg.ContentCallbackRaw, error)` | Retrieves all callbacks filtered by optional status, sorted by createdAt ascending. No country-specific logic. | 🟢 OK |
| `UpdateStatus()` | 123 | `UpdateStatus(ctx context.Context, id modelmg.AppID, status string, desc string) error` | Updates callback record status + description. Simple DAO wrapper. | 🟢 OK |

### content_flow.go (120 lines)

| Function | Line | Signature | Body Summary | Country Issues |
|----------|------|-----------|--------------|-----------------|
| `CreateView()` | 80 | `CreateView(ctx context.Context, content *modelmg.ContentRaw, totalView float64) error` | Inserts view tracking record if totalView > previous value. Creates ContentFlowRaw document with delta calculation. | 🔴 Line 89: HCM timezone hardcoded in `util.TimeStartOfDayInHCM()` call. |
| `CreateLike()` | 28 | `CreateLike(ctx context.Context, content *modelmg.ContentRaw, totalLike float64) error` | Inserts like tracking record if totalLike changed. Skips if no change. | 🔴 Line 40: HCM timezone hardcoded. |
| `CreateComment()` | 54 | `CreateComment(ctx context.Context, content *modelmg.ContentRaw, totalComment float64) error` | Inserts comment tracking record if totalComment changed. Skips if no change. | 🔴 Line 65: HCM timezone hardcoded. |
| `getContentTotalValue()` (private) | 106 | `getContentTotalValue(ctx context.Context, contentId modelmg.AppID, contentFlowType string) (float64, error)` | Aggregates total view/like/comment from ContentAnalyticDaily using pipeline. Returns latest or 0. | 🟢 No country logic. |

---

## Section 2: Country-Specific Hardcode Issues

### 🔴 CRITICAL: HCM Timezone Baked In (Line-by-line)

**content.go:**
- **Line 87**: `day = util.TimeStartOfDayInHCM(now)` — Used for daily quota check. **Should be:** Dynamic country-based timezone from event config.
- **Line 122**: `Date: util.TimeStartOfDayInHCM(time.Now())` — Sets date field for newly created content. **Should be:** Event's timezone, not VN hardcoded.

**content_flow.go:**
- **Line 40**: `Date: util.TimeStartOfDayInHCM(time.Now())` — Like flow tracking date.
- **Line 65**: `Date: util.TimeStartOfDayInHCM(time.Now())` — Comment flow tracking date.
- **Line 89**: `Date: util.TimeStartOfDayInHCM(time.Now())` — View flow tracking date.

**All 5 instances break for Philippines (UTC+8) and Indonesia (UTC+7):**
- HCM/VN is UTC+7, Philippines is UTC+8, Indonesia varies (UTC+7 to UTC+9).
- Current code treats all as HCM/Vietnam time.
- **Impact:** Daily quotas, analytics, and flow timestamps are offset, causing wrong "day" boundaries.

### 🔴 HARDCODED VIETNAMESE TEXT (Content Defaults)

**content.go, Lines 137-140:**
```go
dataDefault.Title = "Đang lấy thông tin"       // "Fetching info" (VN)
dataDefault.Desc = "Đang lấy thông tin"        // "Fetching info" (VN)
dataDefault.Author = "Đang lấy thông tin"      // "Fetching info" (VN)
```
**Affected platforms:** Instagram, InstagramReels, Facebook (when `isCheckHashTag = false`).
**Should be:** Localized via `locale` package. Currently shows Vietnamese to all users.

### 🔴 HARDCODED DOMAIN (CDN/Image URL)

**content.go, Line 140:**
```go
dataDefault.Cover = "https://media.viewboost.vn/public/md_2024_06_29_14_38_53_0700_egkVWCvvYp.png"
```
- Domain `viewboost.vn` is Vietnam-specific.
- **Should be:** Config-driven or CDN agnostic.

### 🔴 HARDCODED HASHTAG VALIDATION DATES (Internal Service)

**internal/service/content.go, Lines 281 & 289:**
```go
if contentInfo.PublishAt.After(util.TimeParseISODate("2024-05-31T17:00:00.000Z")) {
    return errors.New(fmt.Sprintf("Nội dung tham gia chương trình bắt buộc phải chứa hashtag cá nhân...")) // VN error message
}

if contentInfo.PublishAt.Before(util.TimeParseISODate("2024-04-11T17:00:00.000Z")) && hashTag == "#vcreator" {
    continue
}
```
**Issues:**
1. **Date cutoffs (2024-05-31, 2024-04-11):** Hard-coded event-specific dates, not parameterized by event.
2. **Vietnamese error message (Line 282):** "Nội dung tham gia chương trình bắt buộc phải chứa hashtag cá nhân" = "Content participating in program must contain personal hashtag" (VN).
3. **Lines 305:** Another VN error message: "Nội dung không có chứa đầy đủ hashtag của chương trình" = "Content missing required program hashtags" (VN).

### 🟡 INDONESIAN TAX CONSTANT (Not Used Here)

**internal/constants/constants.go, Line 226:**
```go
const PercentTaxIndonesia float64 = 12
const PercentTaxVietNam   float64 = 10
```
- Defined but **not used in content services files**. Likely used in withdrawal/payout logic.
- **No 🇵🇭 Philippines tax constant exists.** If Philippines has different tax (typically 5-12%), missing.

### 🔴 INDONESIAN REGEX (Constants)

**internal/constants/constants.go, Line 40:**
```go
const RegexPhoneNumber = `^(?:\+62|62|0)[2-9][1-9][0-9]{6,11}$`
```
- **Hardcoded to Indonesia (+62)** phone format. No support for:
  - 🇵🇭 Philippines: `+63` or `0`
  - 🇻🇳 Vietnam: `+84`
- Not directly used in these 3 files, but infrastructure-level issue.

### 🟢 Locale Keys Are Used (Partial Mitigation)

**content.go uses locale keys:**
- `locale.ContentKeySourceInvalid`
- `locale.EventKeyNotFound`
- `locale.ContentKeyLinkCanNotCrawler`
- etc.

**However:** Not all strings are localized. Vietnamese text in:
- Default content placeholders (lines 137-140)
- Error messages in internal service (lines 282, 305, 282)

---

## Section 3: Business Logic Insights

### Content Submission Flow (content.go::Create, lines 45-263)

```
Creator submits URL
  ↓
[Auto-detect platform] — Valid TikTok, YouTube, Facebook, Instagram, Reels/Shorts
  ↓
[Event validation]
  ├─ Event exists & active (line 92-99)
  ├─ Event accepts source type (line 101)
  ├─ Daily quota not exceeded (line 105-112) ← USES HCM TIMEZONE
  └─ Error: return to user
  ↓
[Content metadata fetch] — via contentcatcher service
  ├─ YouTube: GetData(SourceYoutube) → extract title, desc, author, cover, views, likes, comments, duration
  ├─ TikTok: GetData(SourceTiktok) + AccessToken (if user-owned) → same metadata
  ├─ Instagram/Reels: skip fetch (isCheckHashTag=false), use defaults
  ├─ Facebook/Reels: fetch if enabled in config, else skip
  └─ On failure: "ContentKeyLinkCanNotCrawler"
  ↓
[Validation checks]
  ├─ Content ID exists (line 220): Prevent duplicate content_id
  ├─ Publish date in event range (line 204-207)
  ├─ HashTag validation (line 209-214)
  │   ├─ User personal hashtag required (if not self-published)
  │   ├─ Event hashtags required
  │   └─ HARDCODED DATE CHECKS: 2024-04-11, 2024-05-31
  └─ On failure: return to user
  ↓
[Save to MongoDB]
  ├─ Insert ContentRaw (line 252)
  ├─ status = "waiting_approved"
  ├─ Date field uses HCM timezone
  └─ On success: 200 OK
  ↓
[Async background tasks] (line 255-261, goroutine)
  ├─ CreateFlow() — track initial view/like/comment
  ├─ UpdateUserPartnerStatistic()
  └─ UpdateAnalyticEventDaily()
```

**🔴 Timezone Bug Impact:**
- Line 87: Daily quota resets at "HCM midnight", not local Philippines/Indonesia midnight.
  - Example: Event in Manila (UTC+8). At Manila midnight, HCM is 1 hour behind (23:00 previous day).
  - User can submit 1 extra content before HCM midnight.
  - **Exploit:** Creator gets higher daily quota by crossing timezone boundaries.

**🔴 Hardcoded Date Cutoffs:**
- Lines 281, 289: Hashtag rules change at specific ISO dates.
- Rules not parameterized per-event → All events follow same timeline.
- **Unclear:** Are these rules still active in 2026? Code from 2024 era.

### Callback Flow (content_callback.go::Create, lines 29-105)

```
content-catcher service calls webhook POST /callback
  ↓
[Validate input]
  ├─ data array non-empty (line 30)
  ├─ RequestID provided (implicit in aggregation)
  └─ On failure: skip & return nil
  ↓
[For each data item]
  ├─ Extract "link" field (line 36)
  ├─ Query existing callbacks matching RequestID via aggregation pipeline (lines 42-53)
  ├─ Check if new link exists in existing URLs (line 69)
  ├─ If new link found → skip (line 71)
  ├─ If new link missing → UPSERT (lines 83-88)
  │   ├─ Match: {request_id, link}
  │   ├─ Set: {link, information, status="waiting", receivedAt, updatedAt}
  │   └─ Insert or update
  └─ On error: return & stop processing
  ↓
[Status = "waiting"] — Ready for callback processor to consume
```

**🔴 Design Issue:**
- Line 59: Aggregation pipeline runs **inside the loop** for every data item.
  - Inefficient: Could aggregate once before loop.
  - Example: 10 items → 10 DB queries. Should be 1.

**🟢 OK:**
- Aggregation prevents duplicate links for same RequestID.
- Status transitions: "waiting" → ("processed" | "failed") handled elsewhere.

### Content Flow Tracking (content_flow.go)

```
[Async trigger from content.go line 256]
  ↓
CreateFlow(event, content, contentInfo) → calls internal/service/content_flow.go
  ↓
[Parallel goroutines]
  ├─ CreateView(totalView) — if totalView > 0
  │   ├─ Query latest flow record from ContentAnalyticDaily
  │   ├─ Calculate delta = totalView - oldValue
  │   ├─ If delta > 0: Insert ContentFlowRaw
  │   └─ Date set to HCM midnight ← BUG
  │
  ├─ CreateLike(totalLike)
  │   ├─ Query latest flow record
  │   ├─ Calculate delta = totalLike - oldValue
  │   ├─ If delta changed: Insert ContentFlowRaw
  │   └─ Date set to HCM midnight ← BUG
  │
  └─ CreateComment(totalComment)
      ├─ Query latest flow record
      ├─ Calculate delta = totalComment - oldValue
      ├─ If delta changed: Insert ContentFlowRaw
      └─ Date set to HCM midnight ← BUG
  ↓
[Update statistics]
  └─ ContentRaw.Statistic = {view: totalView, like: totalLike, comment: totalComment}
```

**🔴 Date Field Bug:**
- All 3 CreateView/Like/Comment use `TimeStartOfDayInHCM()`.
- Content submitted in Philippines (08:00 AM) gets recorded as HCM date (07:00 AM same day or previous day).
- **Result:** Analytics show views/likes on wrong day → Daily reports misaligned by 1 day.

**🟢 Delta Calculation:**
- Correctly tracks incremental changes, preventing duplicate counts.
- Supports backward compatibility if stats decrease (e.g., deleted comments).

### Hashtag Validation Rules (internal/service/content.go, lines 265-309)

```
[CheckHashTag called from content.go line 210]
  ↓
[Early return if dev environment]
  └─ Line 267-269: If config.IsEnvDevelop() → return nil (skip all validation)
  ↓
[User personal hashtag check]
  ├─ Search for user.Hashtag in content description/title (case-insensitive)
  ├─ If NOT found AND:
  │   ├─ content.PublishAt > 2024-05-31 17:00:00 UTC AND
  │   ├─ NOT self-published (isSelf=false)
  │   └─ Return ERROR: "Nội dung tham gia chương trình bắt buộc phải chứa hashtag cá nhân..."
  ├─ If self-published OR before cutoff → allow without personal hashtag
  └─ HARDCODED CUTOFF DATE: 2024-05-31 17:00:00 UTC ← 🔴 ISSUE
  ↓
[Event hashtag check]
  ├─ For each event.Options.Hashtags:
  │   ├─ Special rule: If before 2024-04-11 17:00:00 UTC, skip #vcreator check
  │   ├─ Else: Check hashtag exists in desc/title (case-insensitive)
  │   ├─ If NOT found: Add to missing list
  │   └─ HARDCODED CUTOFF DATE: 2024-04-11 17:00:00 UTC ← 🔴 ISSUE
  └─ If any missing: Return ERROR: "Nội dung không có chứa đầy đủ hashtag..."
```

**🔴 Hashtag Rules Issues:**

1. **Hardcoded dates (2024-04-11, 2024-05-31):**
   - These are Vietnam VCreator campaign dates.
   - **Not parameterized by event** → All events forced to follow same timeline.
   - 🇵🇭 Philippines may need different dates.
   - 🇮🇩 Indonesia may need different dates.

2. **Vietnamese error messages (lines 282, 305):**
   - Not localized → All users see Vietnamese text regardless of language setting.

3. **Case-insensitive hashtag check:**
   - Allows flexibility (good).
   - But doesn't handle variations like "#vcreator" vs "#VCreator".

4. **Comment (line 34):**
   - Line 34: `// Lặp qua từng phần tử trong mảng data` (Vietnamese comment in English codebase).

---

## Section 4: Cleanup Tasks (Priority & Effort)

### P0 (Critical - Breaks Functionality)

| File:Line | Issue | Effort | Priority | Notes |
|-----------|-------|--------|----------|-------|
| `content.go:87` | HCM timezone for daily quota. Use event timezone. | M | P0 | Causes quota bugs across timezones. Affects all daily limits. |
| `content.go:122` | HCM timezone for content date. Use event timezone. | M | P0 | All content records have wrong date. Breaks analytics. |
| `content_flow.go:40, 65, 89` | HCM timezone hardcoded 3x. Use event timezone. | M | P0 | All flow records have wrong dates. Reporting is off-by-1-day for PHP/IDN. |
| `internal/constants/constants.go:40` | RegexPhoneNumber hardcoded to Indonesia (+62). Add PHP (+63). | S | P0 | User registration/validation will fail for PH. |
| `internal/service/content.go:281, 289` | Hardcoded hashtag cutoff dates (2024-04-11, 2024-05-31). Parameterize by event. | L | P0 | Rules aren't portable to other campaigns/countries. |

### P1 (High - Incorrect Localization)

| File:Line | Issue | Effort | Priority | Notes |
|-----------|-------|--------|----------|-------|
| `content.go:137-139` | Vietnamese placeholder text "Đang lấy thông tin" hardcoded. Use locale keys. | S | P1 | Users see VN text for Instagram/Facebook defaults. Should be localized. |
| `content.go:140` | Domain `viewboost.vn` hardcoded. Make config-driven. | S | P1 | CDN domain should be parameterized per-country. |
| `internal/service/content.go:282, 305` | Vietnamese error messages not localized. Use locale keys with language param. | S | P1 | All users see Vietnamese hashtag validation errors. Need English/Filipino translations. |
| `content_callback.go:34` | Vietnamese comment "Lặp qua từng phần tử..." Change to English. | S | P1 | Codebase should be English for international team. |

### P2 (Medium - Performance/Design)

| File:Line | Issue | Effort | Priority | Notes |
|-----------|-------|--------|----------|-------|
| `content_callback.go:59` | Aggregation query inside loop. Move before loop for batch query. | M | P2 | Performance: O(n) queries → O(1). Matters for high-volume callbacks. |
| `internal/constants/constants.go` | Add Philippines tax constant `PercentTaxPhilippines`. | S | P2 | Currently only VN (10%) and IDN (12%) defined. PHP rate varies (5-12%) by income. |
| `internal/service/content.go:267-269` | Dev environment skips ALL hashtag validation. Should be feature-flagged per event. | S | P2 | Dangerous: Dev behavior affects production if config mismatched. Use event flag instead. |

---

## Section 5: Key Findings Summary

### ✅ What's Good

1. **Locale infrastructure exists:** Service uses `locale.*` keys for most error messages.
2. **Async processing:** Content flow tracking happens async → Non-blocking for user.
3. **Deduplication logic:** Content ID uniqueness prevents duplicate submissions.
4. **Delta calculation:** Flow tracking correctly computes incremental changes.
5. **Platform detection:** Auto-detects social source from URL (YouTube, TikTok, Instagram, Facebook).

### ❌ What's Broken

1. **HCM timezone baked into 5 locations:** All dates use VN timezone, ignoring country context.
2. **Hardcoded Vietnamese text:** Placeholders and error messages in Vietnamese only.
3. **Hardcoded campaign dates:** Hashtag rules tied to specific 2024 dates, not portable.
4. **Missing Philippines support:** No PHP tax, no PHP phone regex, no PHP timezone handling.
5. **N+1 query bug:** Callback aggregation inside loop instead of batch query.

### 🚩 Risks

1. **Daily quota exploitable:** Creator spanning HCM/PH timezone boundary gets extra quota.
2. **Analytics misreported:** All reports off-by-1-day in PH/IDN due to timezone.
3. **User confusion:** Non-Vietnamese users see Vietnamese error messages.
4. **Campaign rules stuck in 2024:** Hashtag validation tied to old campaign dates, not re-usable.
5. **Database bloat:** N+1 callback queries on high-volume days.

---

## Investigation Notes

- **Source:** This is clearly Vietnam-first code (VN timezone, VN tax%, VN error messages, VN campaign dates).
- **Clone status:** Indonesia code cloned from Vietnam, but Indonesia timezone/tax/localization only partially ported.
- **Philippines port:** Started but incomplete. Missing PH timezone, PH tax, PH localization, PH phone validation.
- **Timeline:** Hardcoded dates (2024-04-11, 2024-05-31) suggest code from Q2 2024, now 2 years old.
- **No 🇵🇭 Country Config:** Event model likely has country field, but not used in these 3 files.

---

**Recommendation:** Refactor to use event-level timezone/locale context instead of hardcoded defaults. Create CountryConfig struct mapping country → {timezone, tax%, currency, locale, phone_regex, error_messages}.
