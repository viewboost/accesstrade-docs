# Audit 04: Withdraw + Cashflow + Tax

**Files:**
- `pkg/public/service/withdraw.go` (278 dòng) — public service (DEAD code, route không wire)
- `internal/service/withdraw.go` (336 dòng) — internal service (được admin dùng)
- `internal/constants/constants.go` (tax constants)

---

## State of Withdraw module

### Public withdraw — DEAD CODE

`pkg/public/service/withdraw.go` tồn tại NHƯNG:
- Handler `pkg/public/handler/withdraw.go` không wire vào router
- → Code này KHÔNG ai gọi
- Có nhiều bug rõ rệt:
  - **Line 64**: `if user.ID.IsZero()` check user mà KHÔNG load user trước (no `FindById`) — luôn return UserKeyNotFound
  - **Line 254-255**: TYPO swap field — `TotalCashRejected: user.Statistic.TotalCashCompleted` và ngược lại
  - **Line 210**: `util.TimeOfDayInHCM` (VN timezone)

→ Decision: **delete file này** hoặc keep nhưng comment-out rõ là dead code.

### Internal withdraw — ACTIVE

`internal/service/withdraw.go` được gọi từ `pkg/admin/service/transfer_processing.go:90`.

Flow:
1. Admin tạo transfer batch (gom nhiều withdraw cho creator chưa rút)
2. Transfer process → call `Withdraw().Create()` cho từng creator
3. Insert WithdrawRaw + CashFlow tax + CashFlow withdraw

---

## Internal withdraw — Country issues

| Line | Code | Issue |
|---|---|---|
| **133** | `payload.CashTax = math.Round(payload.Body.Cash * constants.PercentTaxIndonesia / 100)` | 🟡 Hardcode tax IDR 12% — cần PH rate |
| **280** | `code := strings.ToUpper(referralCode) + util.TimeOfDayInHCM(now).Format(constants.CustomerDDMMYYYY) + ...` | 🔴 VN timezone HCM trong generate withdraw code |

---

## Tax constants

```go
// constants/constants.go
PercentTaxIndonesia float64 = 12   // line 226
PercentTaxVietNam   float64 = 10   // line 227 (VN leftover)
```

Tax usage trong codebase:
- `internal/service/withdraw.go:133` — withdraw flow
- `pkg/public/service/schedule.go:789` — monthly tax cron

→ Cả 2 chỗ dùng `PercentTaxIndonesia`. Cần đổi sang `PercentTaxPhilippines`.

---

## Withdraw flow chi tiết

### Withdraw business logic
1. Lock user qua Redis mutex (prevent double-withdraw)
2. Check user banned
3. Aggregate remaining cash từ CashFlow per partner
4. Validate bank card + bank info
5. **Calc tax: `Cash * 12% (Indonesia)`** (line 133)
6. ActualCash = Cash - Tax - Fee
7. Generate withdraw code: `referralCode + DDMMYYYY (HCM tz) + random4`
8. Insert WithdrawRaw + 3 CashFlow entries (withdraw, tax, fee nếu có)
9. Trigger UpdateStatistic

### Cash flow records sau withdraw
- **CashFlow Action="withdraw"**: `Value = -Cash`
- **CashFlow Action="tax"**: `Value = -Tax` (nếu Tax > 0)
- **CashFlow Action="withdraw_fee"**: `Value = -Fee` (nếu Fee > 0)

→ Tax applied **per withdraw**, không monthly. (Khác với schedule.go nói monthly)

⚠️ **Conflict:** Code có 2 nơi apply tax:
- `withdraw.go:133` — per-withdraw tax 12%
- `schedule.go:789` — monthly cron tax 12% qua `UpdateCashFlowTax`

→ User có thể bị **trừ tax 2 lần**? Cần verify business logic intent.

---

## Bank requirements

Line 217: `if bank.IsBranchRequired { ... }`

→ Bank model có field `IsBranchRequired` — bank nào cần branch (Vietcombank Vietnam có chi nhánh) thì validate. PH banks (BDO, BPI, ...) thường không cần branch — set `IsBranchRequired=false` ở data seed.

---

## Cleanup tasks

| Task ID | File:Line | Description | Priority | Effort |
|---|---|---|---|---|
| WD-01 | internal/service/withdraw.go:133 | Replace `PercentTaxIndonesia` → PH tax constant (verify rate với partner) | P0 | S |
| WD-02 | internal/service/withdraw.go:280 | Replace `TimeOfDayInHCM` → Manila timezone util | P0 | S |
| WD-03 | constants.go:226-227 | Cleanup: rename `PercentTaxIndonesia` thành `PercentTaxPHWithholding` hoặc tạo per-region map | P1 | S |
| WD-04 | constants.go:227 | Remove `PercentTaxVietNam` constant (không dùng nữa) | P2 | S |
| WD-05 | pkg/public/service/withdraw.go | Delete entire file (dead code) hoặc add deprecation comment | P2 | S |
| WD-06 | — | **Verify tax intent** — withdraw + cron có double-charge tax không? | P0 | S |
| WD-07 | DATA INIT | Seed PH banks với `IsBranchRequired=false` | P1 | S |

---

## Verdict

✅ Withdraw module **logic OK** cho PH — chỉ cần:
1. Đổi tax % và timezone constants
2. Verify business logic tax (per-withdraw vs monthly)
3. Seed PH banks data
4. Delete dead public service file

❌ KHÔNG cần build feature mới hoặc bỏ scope. Theo nguyên tắc "source có thì giữ", withdraw flow giữ nguyên.
