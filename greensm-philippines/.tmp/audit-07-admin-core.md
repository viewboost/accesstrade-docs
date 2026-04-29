# Audit 07: Admin Core Modules (Transfer + Reconciliation + Staff)

**Files audited:**
- Transfer: transfer.go (634), transfer_processing.go (104), transfer_finish.go (179), transfer_transferring.go (127) = 1044 dòng
- Reconciliation: reconciliation.go (641), reconciliation_processing.go (231), reconciliation_running.go (348) = 1220 dòng
- Staff: staff.go (589 dòng)

---

## Module 1 — Transfer (Payout Batch Flow)

### Function inventory (key functions)

| Function | Line | Summary |
|---|---|---|
| `Create` | transfer.go:320 | Tạo payout batch với conditions (min cash, max withdraw) |
| `Update` | transfer.go:383 | Update batch name & conditions khi status=new |
| `GetList` | transfer.go:424 | Paginated list với partner RBAC filter |
| `ChangeStatus` | transfer.go:265 | State transition handler |
| `IsValidStatus` | transfer.go:305 | State machine: new→processing→transferring→finished |
| `ChangeDeclined` | transfer.go:474 | Toggle decline cho specific withdrawals |
| `GetListWithdrawCashes` | transfer.go:157 | Query withdraws của transfer batch |
| `GetStatistic` | transfer.go:595 | Aggregate withdraw counts by status |
| `UpdateTransferIdForEventReward` | transfer.go:58 | Async backfill transferId cho event rewards & cashflows |
| `Processing` | transfer_processing.go:17 | Generate withdrawals cho eligible users (banned=false, contract complete) |
| `Transferring` | transfer_transferring.go:15 | Record cashflows (withdraw + tax + bank fee), mark transferring |
| `Finish` | transfer_finish.go:36 | Complete approved, refund declined, update event rewards |

### Business flow

```
[NEW] (admin tạo batch + conditions)
  ↓
[PROCESSING] (loop eligible users → tạo withdraw records)
  Filter: banned=false + contract.status=completed + cashRemaining ≥ MinValue
  ↓
[TRANSFERRING] (tạo CashFlow entries)
  - Withdraw: -Cash
  - Tax: -CashTax (nếu có)
  - Fee: -BankFee (nếu có)
  ↓
[FINISHED] (Finish complete + refund)
  - Approved → StatusCompleted
  - Declined → StatusRejected + refund cashflows + clear EventReward.transferId
```

### Country issues

| File:Line | Issue | Severity |
|---|---|---|
| `transfer_processing.go:56` | **Logic bug:** `math.Max(MinValueCashRemaining, MaxCashWithdraw)` — sai logic. MaxCashWithdraw không phải min threshold | 🔴 CRITICAL bug |
| `transfer.go:352, 396` | `format.NonAccentVietnamese()` cho transfer name | 🔴 VN leftover |
| `transfer_finish.go:121` (gián tiếp) | Gọi `UpdateTransferIdForEventReward` trong reconciliation.go có HCM tz | 🔴 VN leftover |

### Bug / Red flags

1. ❌ **CRITICAL Logic bug** transfer_processing.go:56 — `math.Max` filter sai
2. ❌ NonAccentVietnamese hardcoded
3. ⚠️ Concurrent goroutines fire-and-forget (line 294) — `go t.Processing()`, `go t.Transferring()`, `go t.Finish()` no error propagation
4. ⚠️ Race condition trong ChangeDeclined — không write lock
5. ⚠️ No bank fee strategy documented — BankFee đến từ đâu?
6. ⚠️ No currency validation (VND vs PHP assumed same)

---

## Module 2 — Reconciliation (Đối soát)

### Function inventory (key functions)

| Function | Line | Summary |
|---|---|---|
| `Create` | reconciliation.go:431 | Tạo reconciliation cho event (status=pending) |
| `Update` | reconciliation.go:380 | Update title & conditions khi pending |
| `ChangeStatus` | reconciliation.go:216 | Route: pending→processing/running, running→completed |
| `GetListContent` | reconciliation.go:142 | Fetch content-type items |
| `GetListMilestone` | reconciliation.go:83 | Fetch milestone-type items |
| `ChangeStatusItem` | reconciliation.go:55 | Toggle item status (chỉ khi status=processed) |
| `UpdateStatistic` | reconciliation.go:596 | Aggregate item counts |
| `ValidTime` | reconciliation.go:520 | Validate ToAt ≤ today (HCM tz) |
| `Processing` | reconciliation_processing.go:23 | Load content + milestone items vào DB |
| `ProcessingMilestone` | reconciliation_processing.go:64 | Scan EventReward type=by-milestone |
| `ProcessingContent` | reconciliation_processing.go:156 | Aggregate EventReward by content |
| `Running` | reconciliation_running.go:29 | Iterate users, runCashBack (worker pool 50) |
| `runCashBack` | reconciliation_running.go:127 | Per item: validate + create CashFlow + update EventReward |

### Business flow

```
[PENDING] admin tạo RC cho event + ToAt
  Validate: ToAt ≤ today, no other RC running on same event type
  ↓
[PROCESSING] admin click "start"
  ProcessingMilestone: scan EventReward type=by-milestone
  ProcessingContent: aggregate EventReward by content
  ↓
[PROCESSED] items đã load
  Admin có thể ChangeStatusItem (approve/reject từng item)
  ↓
[RUNNING] admin click "run cashback"
  groupByUser → worker pool 50 → runCashBack
  Per item:
    Milestone → CashFlowActionReconciliationEventRewardMilestone + notification
    Content → CashFlowActionReconciliationEventRewardStatistic + update ContentAnalyticDaily + notification
  ↓
[COMPLETED]
  Trigger Schedule().UpdateAnalyticOldEventDaily()
```

### Country issues

| File:Line | Issue | Severity |
|---|---|---|
| `reconciliation.go:516, 527` | `util.TimeStartOfDayInHCM` validate ToAt | 🔴 VN leftover |
| `reconciliation_running.go:118` | `util.TimeStartOfDayInHCM` cho FromAt | 🔴 VN leftover |
| `reconciliation.go:395, 400, 448` | `format.NonAccentVietnamese` cho title | 🔴 VN leftover |
| `reconciliation_running.go:124` | Telegram RoomReconciliationID hardcoded | 🟡 ID-specific |

### Bug / Red flags

1. ❌ **3 chỗ TimeStartOfDayInHCM** — daily cutoffs lệch 1h (PH UTC+8 vs VN UTC+7) — wait đều là UTC+8 thực tế
2. ❌ NonAccentVietnamese (3 chỗ)
3. ⚠️ Race condition duplicate detection (running.go:111-128)
4. ⚠️ No rollback on runCashBack failure — partial processing không recoverable (line 304)
5. ⚠️ Worker pool hardcoded 50
6. ⚠️ Engagement calc (line 224): chia cho item.TotalView có thể = 0

---

## Module 3 — Staff (Admin Auth + 2FA + Captcha)

### Function inventory

| Function | Line | Summary |
|---|---|---|
| `Register` | staff.go:145 | Tạo staff account (active=false) |
| `Login` | staff.go:202 | Email + password + captcha → token hoặc 2FA secret |
| `VerifyTOTP` | staff.go:98 | Verify TOTP code → mark IsVerify=true |
| `Reset2FA` | staff.go:61 | Delete old 2FA, generate new secret + QR |
| `Captcha` | staff.go:52 | Verify reCAPTCHA v3 |
| `GetMe` | staff.go:264 | Fetch current staff profile |
| `UpdateInfo` | staff.go:304 | Update name/email/phone/role/partner; reset tokens |
| `UpdatePassword` | staff.go:396 | Hash + update password; reset tokens |
| `ChangeStatus` | staff.go:426 | Toggle active flag |
| `GetList` | staff.go:456 | Paginated list staff |

### 2FA + Captcha flow

```
[LOGIN]
  1. Verify reCAPTCHA v3 token (score-based, no challenge)
  2. Find staff by email + active=true
  3. Compare password hash
  4. Check Admin2FA record:
     - Existed + IsVerify=true → return token (done)
     - Else: generate secret + QR → store Admin2FA → return secret + QR
[VERIFY TOTP] (after scanning QR)
  module2fa.Validation(secret, code)
  Mark IsVerify=true
  Return token
[RESET2FA]
  Delete Admin2FA records
  Generate new secret + QR
  Insert unverified record
```

### Country issues

✅ **Staff module SẠCH country leftover**:
- No HCM timezone
- No NonAccentVietnamese
- No phone format hardcode

### Bug / Red flags (security critical!)

1. ❌ **CRITICAL: GetMe() không có permission check** (line 264) — Staff có thể fetch profile của staff khác
2. ❌ **CRITICAL: UpdateInfo privilege escalation** (line 339) — `isRoot` field writable by user
3. ❌ **CRITICAL: $nin syntax error** (line 325) — MongoDB syntax sai: `"$nin": staff.ID` thay vì `"_id": bson.M{"$ne": staff.ID}`
4. ⚠️ **reCAPTCHA v3 score not validated** (line 214) — chỉ check `valid` boolean, không check score threshold
5. ⚠️ **No rate limiting on TOTP** (line 118) — brute-force 6-digit code (10^6 attempts)
6. ⚠️ **Email case sensitivity** (line 207) — case mismatch blocks login
7. ⚠️ **Typo function name** `VerfifyCaptchaV3` (extra 'f')

---

## Aggregate cleanup tasks

| Task ID | File:Line | Description | Priority | Effort |
|---|---|---|---|---|
| ADMIN-01 | transfer_processing.go:56 | Fix `math.Max` logic — phải là MinValueCashRemaining only | P0 BUG | S |
| ADMIN-02 | transfer.go:352,396 | Replace NonAccentVietnamese → generic UTF-8 normalization | P0 | S |
| ADMIN-03 | reconciliation.go:516,527 + running.go:118 | Replace TimeStartOfDayInHCM → Manila tz | P0 | S |
| ADMIN-04 | reconciliation.go:395,400,448 | Replace NonAccentVietnamese | P0 | S |
| ADMIN-05 | staff.go:264 | Add permission check vào GetMe (validate userID==tokenOwner OR isRoot) | P0 SEC | S |
| ADMIN-06 | staff.go:339 | Block `isRoot` field từ user-controlled body trong UpdateInfo | P0 SEC | S |
| ADMIN-07 | staff.go:325 | Fix MongoDB syntax `$nin` → `$ne` | P0 BUG | S |
| ADMIN-08 | staff.go:214 | Validate reCAPTCHA v3 score threshold | P1 SEC | S |
| ADMIN-09 | staff.go:118 | Add rate limit cho TOTP (lock after N attempts) | P1 SEC | M |
| ADMIN-10 | staff.go:207 | Normalize email lowercase trong login | P1 | S |
| ADMIN-11 | reconciliation_running.go:124 | Telegram RoomReconciliationID per-country config | P2 | S |
| ADMIN-12 | transfer.go:294 | Fire-and-forget goroutines — add error propagation | P2 | M |
| ADMIN-13 | transfer.go (no field) | Document bank fee source — config-driven? | P1 | M |
| ADMIN-14 | reconciliation_running.go:304 | Rollback EventReward khi runCashBack fail | P1 | M |
| ADMIN-15 | transfer.go (multiple) | Currency validation cho amount fields | P2 | S |

---

## Verdict

✅ **Reconciliation + Transfer logic OK** — chỉ cần thay timezone + NonAccentVietnamese + fix math.Max bug.

❌ **Staff module có 4 security bugs P0** — cần fix trước khi onboard staff GreenSM PH.

⚠️ **2FA + Captcha có sẵn nhưng implementation có flaws** — cần security review riêng.
