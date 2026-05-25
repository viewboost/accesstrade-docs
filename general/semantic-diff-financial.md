# Semantic Diff — Financial Group

> **Generated**: 2026-05-07
> **Files trong scope**: `cashflow.go`, `withdraw.go`, `budget.go`

| Service | TCB | vCreator | Ambassador | Notes |
|---|---:|---:|---:|---|
| cashflow.go | 155 LOC | 163 LOC | 154 LOC | 3 md5 khác, structurally similar |
| withdraw.go | 290 LOC | 336 LOC | 336 LOC | vCr+Amb cùng LOC nhưng md5 khác (Amb đã comment out 1 chunk) |
| budget.go | 188 LOC | ❌ | ❌ | TCB-only |

---

## TL;DR

Group này có 3 khía cạnh chính:

1. **`cashflow.go` rất đồng bộ** ở interface (4 fns: AddCashFlow, GetRemaining, GetPartnerRemaining, GetTotalRevenueInMonth) — chỉ khác chi tiết nhỏ.
2. **`withdraw.go` divergent ở Ambassador**: Ambassador đã **comment out logic check user bank card** — temporary workaround, có thể là feature đang phát triển hoặc bị bỏ.
3. **`budget.go` TCB-only**: alert email khi campaign vượt threshold budget — flagship feature TCB tied với reconciliation/dashboard.

---

## 1. `service/cashflow.go` — Cash flow ledger

### Interface chung (cả 3 đều có)
```go
AddCashFlow(payloads, userId)
GetRemaining(userId)
GetPartnerRemaining(userId, partnerId)
GetTotalRevenueInMonth(userId, firstMonth)
```

→ Đây là **financial ledger layer**. Mỗi cash flow là 1 record với:
- `Action` (credit/debit)
- `Category` (event_reward, withdrawal, refund...)
- `Partner` (multi-tenant scope)
- `Value` (số tiền)
- `TargetID + TargetType` (link tới event/content/withdraw...)
- `Options` + `TransferId`

### Khác biệt nhỏ giữa 3 dự án

**vCreator vs TCB/Ambassador**:
- vCreator thêm field `ID` trong `CashFlowPayload` → có thể cập nhật (idempotency hoặc retry an toàn)
- vCreator import thêm `pfloat` → dùng `pfloat.RoundToOneDecimal` cho cash values (tránh float precision)

**TCB vs Amb**: identical interface, khác implementation chi tiết (~10 LOC).

### Ý nghĩa nghiệp vụ
Đây là **service core của 3 dự án** (đều phải track tiền). Sự đồng bộ cao chứng tỏ feature này đã stable. Khác biệt chỉ là quality-of-life:
- vCreator có thêm safety (ID + round) → có thể từ incident production
- TCB/Amb chưa adopt cải tiến đó

→ **vCreator-led innovation**, có thể backport `pfloat.RoundToOneDecimal` sang 2 sản phẩm khác (~10 LOC change).

---

## 2. `service/withdraw.go` — Withdrawal/payout processing

### Interface
```go
Create(...)  // submit withdrawal request
Withdraw()   // service constructor
```

### Skeleton chung
- `DataPayloadWithdrawCashTransaction` với fields: User, Body, UserBankCard, Bank, Branch, Fee, CashRemaining, CashTax, ActualCash
- `WithdrawCashBody` body: cash amount, via (bank/momo/...), userBankCardID, transferID
- Lock cashflow qua **redsync** (Redis distributed lock)
- Validate: số tiền, fee, tax, balance còn lại
- Insert `WithdrawRaw` record

### Khác biệt vCreator vs Ambassador (cùng LOC 336 nhưng md5 khác)

**Ambassador đã COMMENT OUT** logic check user bank card:

```go
// Ambassador (line ~109)
// userBankCard, bank, branch, _ := w.scheckUserBankCardValid(ctx, body)  // [TYPO: scheck]
// if err != nil {
//     return nil, err
// }

// And later at line ~252-269:
// Bank:          bank,           // (commented)
// CardNumber:    data.UserBankCard.CardNumber,  // (commented)
// CardHolderName: data.UserBankCard.CardHolderName,  // (commented)
// Branch:        data.Branch.ID,  // (commented)
// BranchName:    data.Branch.Name,  // (commented)
```

→ Ambassador withdraw KHÔNG yêu cầu user bank card validation. Fields Bank/Branch/CardNumber/CardHolderName **không được lưu** trong WithdrawRaw.

**Có 3 khả năng giải thích**:
1. **Ambassador đang dùng affiliate model** (commission qua external Accesstrade SSO, không cần bank card local)
2. Feature đang **work in progress** — bank verification chưa hoàn thiện
3. **Bank flow đã chuyển sang module khác** (qua pub2 hoặc external)

→ Cần verify với business: Ambassador withdraw chạy thế nào nếu không check bank card?

**TCB vs vCreator**: 52 dòng khác nhau (count diff `^[<>]`). Cần đọc kỹ hơn để biết chính xác — nhưng skeleton giống.

### Ý nghĩa nghiệp vụ
- TCB: withdraw đầy đủ (bank validation, fee, tax)
- vCreator: withdraw đầy đủ (giống TCB nhiều)
- Ambassador: **simplified** (skip bank validation), có thể withdrawal là internal credit chưa ra bank thật

---

## 3. `service/budget.go` — Budget threshold alert (TCB-only, 188 LOC)

### Hàm public (2 hàm)

| Hàm | Mục đích |
|---|---|
| `CheckThresholdByEventID(event)` | Check tổng cash đã chi cho event vượt threshold của budget chưa → fire alert |
| `SendThresholdEmail(...)` | Gửi email alert tới `NotificationForEmails` + staff trong `StaffIds` |

### Logic

1. Tính `totalCashValid = TotalCashPending + TotalCashCompleted + TotalCashWaiting` (từ `event.Statistic`)
2. Query `BudgetCampaignRaw` với event ID + status=active + threshold ≤ totalCashValid
3. Cho mỗi budget vượt threshold:
   - Loop qua `NotificationForEmails` → send email cho từng email
   - Loop qua `StaffIds` → fetch staff → send email
4. Mark budget đã alert (write back) để không spam

### Email template
Dùng SendGrid + custom HTML/text template từ `internal/module/sendgird/templates`. Subject + body include:
- Tên event, tên budget
- Threshold value vs actual spending
- Link admin để review

### Ý nghĩa nghiệp vụ
TCB partners (chi nhánh banking) có **budget allocation** cố định cho campaign. Khi tổng tiền chi (cash valid) vượt threshold (vd: 80% budget) → cảnh báo cho:
- Brand owner (`NotificationForEmails`)
- Staff TCB đã assign (`StaffIds`)

→ Đây là **proactive cost control** — không có ở vCr/Amb vì 2 sản phẩm kia không có budget allocation per-campaign.

### Liên kết với reconciliation/dashboard
- `event.Statistic.TotalCashWaiting` đề cập field chưa thấy ở vCr/Amb → likely TCB-specific concept (cash đang ở reconciliation phase)
- Service này được trigger từ event reward processing → tied với reconciliation engine

---

## 4. Models phát hiện thú vị

### Models shared cả 3
- `CashFlowRaw` — ledger record
- `WithdrawRaw` — withdrawal request
- `TransferRaw` — internal transfer
- `BankRaw`, `BankBranchRaw`, `UserBankCardRaw` — bank info

### TCB-specific
- `BudgetCampaignRaw` — budget config per campaign (threshold, NotificationForEmails, StaffIds, Status)
- `BudgetAlertRaw` — alert history (đã thấy trong inventory model)

→ 2 model này KHÔNG có ở vCr/Amb. Nếu port budget feature thì phải tạo cả 2.

### Ambassador outlier
- `WithdrawRaw` ở Ambassador có cùng schema nhưng **field bank info không được populate** (vì service đã skip).

---

## 5. Câu hỏi business mở

1. **Ambassador withdraw không check bank card** — đây là intentional design (affiliate commission flow khác bank withdraw) hay bug/WIP? Cần check git blame + PM verify.
2. **TCB `TotalCashWaiting`** — đây là cash đang ở phase reconciliation chưa final? Confirm với Reconciliation group.
3. **TCB `BudgetCampaignRaw.NotificationForEmails`** vs `StaffIds` — tại sao có 2 list (custom emails + staff IDs)? Use case: email không phải staff TCB (brand external)?
4. **vCreator `pfloat.RoundToOneDecimal`** — tại sao chỉ vCr round, TCB/Amb không round? Có incident nào liên quan đến float precision không?
5. **Budget threshold trigger** — service này được gọi từ đâu (cron? event reward callback?)? Cần grep callers để hiểu lifecycle.

---

## 6. Tổng kết group

| Khía cạnh | TCB | vCreator | Ambassador |
|---|---|---|---|
| **Cash flow ledger** | ✅ Full (4 fns) | ✅ Full + ID idempotent + pfloat round | ✅ Full |
| **Withdrawal processing** | ✅ Bank validation + fee + tax | ✅ Bank validation + fee + tax | ⚠️ Bank validation **commented out** |
| **Budget allocation + alert** | ✅ Threshold email alert (SendGrid) | ❌ | ❌ |
| **Float precision rounding** | ❌ | ✅ pfloat.RoundToOneDecimal | ❌ |

**Đặc điểm group**:
- Ledger layer **gần như đã sync** — phù hợp dùng làm shared lib
- Withdrawal có vấn đề Ambassador (commented logic) → cần investigate
- Budget là TCB-specific (campaign budget control)

**Direction port nếu cần**:
- TCB → vCr/Amb: budget alert system (effort medium ~188 LOC + 2 models, cần SendGrid integration)
- vCreator → TCB/Amb: pfloat round + ID idempotency (effort cực nhỏ, ~10 LOC)
- Ambassador withdraw: cần **fix** (commented code) hoặc clarify business intent
