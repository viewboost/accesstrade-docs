# Audit 06: Small Public Services Batch

**Files audited:**
- notification.go (87 dòng)
- partner.go (238 dòng)
- quick_action.go (73 dòng)
- transcript.go (62 dòng)
- referral.go (91 dòng)
- article.go (99 dòng)
- news.go (132 dòng)
- common.go (113 dòng)
- user_statistic.go (301 dòng)
- event_reward.go (12 dòng — stub)

**Total:** 21 functions implementations + 6 factories/stubs.

---

## Per-file findings

### notification.go (2 functions)
- `GetList`, `Read`
- ✅ No country issues
- ⚠️ Background goroutine không có context cancellation

### partner.go (4 functions)
- `GetContentFeature`, `GetDetailBySlug`, `GetList`, `getSortContent` (helper)
- ✅ No country issues
- ✅ Clean

### quick_action.go (1 function)
- `GetList` — fetch active quick actions filtered by partner
- ✅ No country issues
- ✅ Clean

### transcript.go (1 function)
- `Webhook` — process transcript webhook from external service
- ✅ No country issues
- ⚠️ **Bug:** lines 28, 38: `return` thay vì `continue` trong loop → exit cả function nếu 1 record có empty link
- ⚠️ Line 31: dùng `context.Background()` thay vì passed ctx

### referral.go (2 functions)
- `InputReferralCode`, `newReferralRaw` (helper)
- ✅ No country issues
- ⚠️ **Bug:** Line 76 trả về `cash` luôn = 0 (init nhưng không set) — cashback amount missing

### article.go (2 functions)
- `GetDetail`, `articleIncreaseView`
- ✅ No country issues
- ⚠️ Line 82, 90-92: inconsistent field name `lastViewAt` vs `LastViewAt`

### news.go (3 functions)
- `AnalyticView`, `GetList`, `getAppResponse` (helper)
- ✅ No country issues
- ⚠️ **Bug:** Line 38 typo `"new"` thay vì `"news"`

### common.go (3 functions)
- `GetAppData`, `GetListBankBranch`, `GetBank`
- ✅ No country issues
- ✅ Clean

### user_statistic.go (4 functions)
- `GetStatisticInvitee`, `GetStatistic`, `GetListInvitee`, `GetContent`
- ✅ No country issues
- ⚠️ **Code smell:** `GetStatisticInvitee` (line 35-97) và `GetStatistic` (line 100-162) **gần copy-paste** — chỉ khác filter
- ⚠️ N+1 query: line 195, 265 nested `GetStatistic` call trong goroutine

### event_reward.go (stub)
- Empty interface, no methods
- ⚠️ Stub không complete

---

## Aggregate findings

✅ **Toàn bộ 10 small services SẠCH** về country-specific:
- Không có `+84/+62/+63` hardcode
- Không có VN/ID/PH timezone hardcode
- Không có Vietnamese/Bahasa text strings
- Không có currency literals

→ Country leftover **CHỈ tập trung ở user/identification/schedule/withdraw** (4 modules đã audit trước).

⚠️ **Bugs cần fix (general, không liên quan PH):**
- transcript.go bug `return` vs `continue`
- transcript.go context.Background()
- referral.go cash always 0
- news.go typo `"new"` → `"news"`
- article.go field name inconsistency
- user_statistic.go duplicate code GetStatistic vs GetStatisticInvitee
- user_statistic.go N+1 query
- event_reward.go stub incomplete
- notification.go background ctx leak

→ Không phải PH-specific, là tech debt source code.

---

## Cleanup tasks

| Task ID | File:Line | Description | Priority | Effort |
|---|---|---|---|---|
| SMALL-01 | transcript.go:28,38 | Replace `return` → `continue` | P1 | S |
| SMALL-02 | transcript.go:31 | Use passed ctx thay vì context.Background() | P1 | S |
| SMALL-03 | referral.go:76 | Populate `cash` return value | P1 | M |
| SMALL-04 | news.go:38 | Fix typo `"new"` → `"news"` | P1 | S |
| SMALL-05 | article.go:82,90-92 | Standardize field name | P2 | S |
| SMALL-06 | user_statistic.go:35-162 | Dedupe GetStatistic vs GetStatisticInvitee | P2 | M |
| SMALL-07 | user_statistic.go:195,265 | Fix N+1 query batch | P2 | M |
| SMALL-08 | event_reward.go | Implement methods hoặc remove stub | P2 | TBD |
| SMALL-09 | notification.go:75-84 | Background goroutine ctx cancellation | P2 | S |

---

## Verdict

✅ **10 small services KHÔNG cần PH-specific changes** — toàn bộ country issue ở 4 modules core (user, identification, schedule, withdraw).

→ Cleanup tasks ở batch này là **general tech debt**, không phải port PH.
