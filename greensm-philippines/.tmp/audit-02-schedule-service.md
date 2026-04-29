# Audit 02: schedule.go (1976 dòng)

**Source:** `vcreator-philippines/backend/pkg/public/service/schedule.go`
**Method:** Đọc body từng function

---

## Function inventory (~24 functions)

| Function | Line | Body Summary | Country Issues |
|----------|------|-------------|----------------|
| `CrawlDataContentTiktokSelf` | 77 | Crawl TikTok với user token. Batch URLs qua `contentcatcher.Client()`. Pagination via `LimitLinkPerPageCrawl`. | None |
| `CrawlDataContentFacebook` | 186 | Fetch FB/Reels từ active events. Gate `config.Facebook.IsEnable`. Guard `isRunFacebookCrawl`. | None |
| `RecheckVideoNotFound` | 287 | Re-validate deleted TikTok videos (totalNotFound 3-5). Calls `contentcatcher.TiktokIsVideoPublic()`. | None |
| `UpdateViewHasTransfer` | 326 | Mark rewards `isTransfer=true` khi user cash.remaining=0. Bulk update EventRewardDAO. | None |
| `UpdateInfoContract` | 374 | Update contract fields (bank, card) từ UserBankCard. | 🔴 Line 413: hardcode `+84` |
| `UpdateUserHashTag` | 450 | Aggregate user hashtags từ content. Update search index. | None |
| `RecheckStatisticByEvent` | 496 | Re-process schemas cho 1 event/date. | 🟡 Line 522: `TimeStartOfDayInHCM` |
| `UpdateUserEventByEvent` | 563 | Update `UserEvent.Statistic` cho all users trong event. | None |
| `RecheckMilestoneByEvent` | 583 | Re-process milestone triggers. Goroutine pool 50 workers. | None |
| `UpdateCashFlowTax` | 756 | Apply tax monthly. **Hardcode `PercentTaxIndonesia`**. | 🟡 Line 789 + line 760 hardcode date `2024-03-31` |
| `UpdateCashFlowOptions` | 815 | Enrich CashFlow với reconciliation metadata (EventName/SchemaName/Link/TotalView). | None |
| `ReCheckPassSchemaByStatisticByDate` | 914 | On-demand recheck cho 1 date. | None |
| `UpdateContentFlowStatus` | 956 | Sync ContentFlow.Status với Content.Status. | None |
| `CrawlDataContentTiktok` | 977 | **Core TikTok crawler** — public videos. Guard `isRunCrawlTiktok`. | None |
| `UpdateContentAnalytic` | 1091 | Aggregate daily stats từ ContentFlow (views/likes/comments). | None |
| `RunCheckPassSchemaStatisticAfterDay` | 1169 | Reprocess schemas cho content thay đổi. Telegram notify. | 🟡 Line 1181: `TimeStartOfDayInHCM` |
| `CrawlDataContent` | 1245 | Crawl YouTube + Shorts (approved only). Guard `isRunCrawl`. | None |
| `RunCheckPassSchemaByStatistic` | 1351 | Reprocess schemas cho user updated trong 4h gần đây. | ❓ Line 1389: hardcode `-4h` window |
| `UpdateSearchStringContent` | 1408 | Regenerate search string cho **all content** (full table scan). | ⚠️ OOM risk |
| `CheckMilestoneView` | 1425 | Concurrent view-milestone validation. 50 workers. | None |
| `ProcessContentCallback` | 1471 | **Core reward trigger** — poll ContentCallbackRaw status="waiting". Process từ content-catcher. 55min timeout. | 🔴 Line 1775: tiếng Việt hardcode |
| `CleanupOldContentCallback` | 1805 | Delete ContentCallback >3 tháng. | None |
| `InsertContentCallback` | 1836 | Bulk insert tracking records. | None |
| `ProcessTiktokUnauthorized` | 1855 | Retry handler cho TikTok 401. Refresh tokens, re-crawl. | None |
| `crawlTiktokForUserSocial` | 1948 | Helper batch URL → contentcatcher. | None |

---

## 🔴 Country-specific issues

### P0 - VN leftover (CRITICAL)

| Line | Code | Impact |
|------|------|--------|
| **413** | `contract.PhoneNumber = strings.ReplaceAll(user.Phone.Full, "+84", "0")` | PH `+63` numbers KHÔNG bị replace, format sai trong contract |
| **522** | `dateHCM := util.TimeStartOfDayInHCM(date)` | Reward timing dùng VN timezone |
| **553** | `util.TimeStartOfDayInHCM(date)` | Same |
| **680** | `util.TimeStartOfDayInHCM(time.Now())` | Same |
| **739** | `"note": "Hiện tại, không thỏa điều kiện " + util.TimeOfDayInHCM(...).Format(...)` | **Vietnamese rejection message + HCM tz** |
| **790** | `util.TimeStartOfDayInHCM(time.Now())` | Same |
| **1181** | `util.TimeStartOfDayInHCM(time.Now())` | Same |
| **1790** | `util.TimeStartOfDayInHCM(time.Now())` | Same |
| **1775** | `RejectListContentByIds(..., "Nội dung đã bị xóa hashtag", ...)` | **Vietnamese rejection reason** |

### P1 - Indonesia specific (cần đổi sang PH)

| Line | Code | Impact |
|------|------|--------|
| **789** | `estimateCashTax := math.Round(totalRevenue * constants.PercentTaxIndonesia / 100)` | Tax rate sai cho PH |
| **760** | `firstMonth = util.TimeParseISODate("2024-03-31T17:00:00.000Z")` | Hardcode launch date |

---

## Business logic insights

### Reward calculation flow
1. **Content Crawl** → external `content-catcher` fetch stats từ social APIs
2. **Callback Processing** (`ProcessContentCallback` line 1471) → poll ContentCallbackRaw status="waiting"
3. **Schema Validation** — 2 paths:
   - **Statistic-based**: user accumulated views/engagements ≥ threshold
   - **Milestone-based**: single video hits view count
4. **Reward Creation** → insert `EventRewardRaw` (status="pending", cash từ schema.CashReward.CashMilestone)
5. **Notification** → async Notification record

### Tax handling
- **Function:** `UpdateCashFlowTax()` line 756 — chạy monthly cron
- **Logic:**
  1. Query users với `statistic.totalCashCompleted > 0`
  2. Sum revenue từ firstMonth (2024-03-31)
  3. `estimateCashTax = revenue × PercentTaxIndonesia / 100`
  4. Insert CashFlow âm với `Action="tax"`, `Category="tax"`
  5. Deduct balance: `newBalance = oldBalance - tax`
- **No approval workflow** — tự động trừ
- **Red flag:** Hardcode IDR tax 12%. PH withholding tax khác.

### Reconciliation flow (gián tiếp qua schedule)
- `UpdateCashFlowOptions` line 815 — enrich CashFlow với reconciliation metadata
- Link CashFlow → ReconciliationRaw → ReconciliationItemRaw
- 2 reconciliation actions:
  - `CashFlowActionReconciliationEventRewardMilestone` (line 873)
  - `CashFlowActionReconciliationEventRewardStatistic` (line 882)

### Crawl logic
- **TikTok Self** (line 77): authenticated user tokens, faster, batch ~10
- **TikTok Public** (line 977): no auth, public videos only — main crawler
- **Facebook** (line 186): gated by config.Facebook.IsEnable
- **YouTube** (line 1245): approved content only, sources YT + Shorts
- All crawlers: call `contentcatcher.Client().GetData()` async, insert ContentCallbackRaw tracking

---

## Cleanup tasks (file:line)

| Task ID | File:Line | Description | Priority | Effort |
|---|---|---|---|---|
| SCHED-01 | schedule.go:413 | Replace `+84` → PH country code (refactor phone util) | P0 | S |
| SCHED-02 | schedule.go:522,553,680,739,790,1181,1790 | Replace all `TimeStartOfDayInHCM`/`TimeOfDayInHCM` (7+ occurrences) | P0 | M |
| SCHED-03 | schedule.go:789 | Replace `PercentTaxIndonesia` → `PercentTaxPhilippines` (verify rate với partner) | P0 | S |
| SCHED-04 | schedule.go:760 | Update hardcoded date `2024-03-31` → PH launch date hoặc env var | P1 | S |
| SCHED-05 | schedule.go:739, 1775 | Translate Vietnamese rejection messages → EN/Filipino | P0 | S |
| SCHED-06 | schedule.go:1389 | Document `-4h` window hoặc extract const | P2 | S |
| SCHED-07 | schedule.go:1408 | UpdateSearchStringContent OOM risk (full table scan) — add pagination | P2 | M |

---

## Findings summary

✅ **Positive:**
- Clean separation: crawl / callback / schema validation / reward creation
- Goroutine pool đúng pattern (ants library)
- Pagination ở hầu hết functions
- Async processing tốt

⚠️ **Risks:**
1. **Timezone mismatch HCM → PH** affect reward timing
2. **Tax rate ID hardcode** — sai amount cho PH
3. **Vietnamese UI text** trong rejection messages
4. **Concurrent access guards là module-level vars** — không thread-safe khi multi-instance deploy
5. **Full table scan** trong UpdateSearchStringContent → OOM risk
