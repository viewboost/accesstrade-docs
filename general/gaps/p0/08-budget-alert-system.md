# Gap #8 — vCreator thiếu hệ thống kiểm soát ngân sách campaign + tính thưởng có cap

> **Priority**: 🔴 **P0**
> **Source**: [semantic-diff-financial.md](../../semantic-diff-financial.md), [semantic-diff-campaign-event.md](../../semantic-diff-campaign-event.md)
> **Direction port**: Ambassador → vCreator
> **Last verified**: 2026-05-07

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

Mỗi campaign (chương trình thưởng nội dung) trong AccessTrade có một **ngân sách giới hạn** — số tiền tối đa platform sẽ trả thưởng cho creators. Khi campaign đạt giới hạn, hệ thống cần làm 4 việc:

1. **Dừng nhận content mới** (không cho creator submit thêm)
2. **Dừng tạo phần thưởng mới** (không tính tiền cho content đã submit nhưng chưa duyệt)
3. **Cap reward đã được tính** (nếu chỉ còn 50K mà reward đáng lẽ là 100K → trả 50K, ghi nhận thiếu 50K)
4. **Cảnh báo team operations** sớm để xử lý (gia hạn budget hoặc đóng campaign)

Hiện tại:
- **TCB** ✅ Đầy đủ — kiểm soát 3 mức (campaign / mỗi user / mỗi content) + tự động chặn + cap reward + cảnh báo Telegram & Email + distributed lock chống race condition
- **Ambassador** ✅ Tương đương TCB ~90% — đầy đủ kiểm soát + lock + Telegram alert + thêm feature recovery sau crash
- **vCreator** ❌ **KHÔNG có gì cả** — chạy campaign không có giới hạn chi tiêu, không có chống race condition

→ **Vấn đề cốt lõi của vCreator**: campaign không có **ngân sách + cap reward + race protection**. Engine tính thưởng vCreator hiện tại là kiểu "naive": `reward = views × giá + likes × giá + comments × giá` thẳng, không check budget, không có distributed lock. Nếu nhiều creator submit content cùng lúc (race condition) → backend tính reward đồng thời → có thể chi vượt budget hàng tỷ mà không ai biết cho đến cuối kỳ.

## Bảng so sánh 3 sản phẩm (góc nhìn business)

| Tính năng | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| **Cài đặt ngân sách tổng cho campaign** | ✅ Có | ❌ Không | ✅ Có |
| **Cài đặt ngân sách trần cho mỗi creator** | ✅ Có | ❌ Không | ✅ Có |
| **Cài đặt ngân sách trần cho mỗi bài content** | ✅ Có | ❌ Không | ✅ Có |
| **Tự động dừng nhận content khi hết budget** | ✅ Có | ❌ Không | ✅ Có |
| **Tự động dừng tạo reward khi hết budget** | ✅ Có | ❌ Không | ✅ Có |
| **Cap reward khi vượt budget (trả phần còn lại + ghi nhận phần thiếu)** | ✅ Có | ❌ Không | ✅ Có |
| **Khóa chống race condition khi tính reward** (Redis distributed lock) | ✅ 30s | ❌ Không | ✅ 2 phút |
| **Cảnh báo sớm tại 75% / 95% / 100% budget** | ✅ Có | ❌ Không | ✅ Có |
| **Báo cáo Telegram khi vượt ngưỡng** | ✅ Có | ❌ Không | ✅ Có (label `[Ambassador]`) |
| **Email cho creator: "Campaign sắp hết budget, submit nhanh"** | ✅ Có | ❌ Không | ❌ Không |
| **Admin tự cấu hình email alert riêng cho stakeholder** | ✅ Có (`BudgetCampaign`) | ❌ Không | ❌ Không |
| **Hiện sẵn % budget đã dùng trên dashboard** | 🟡 Phải tính lại mỗi lần | ❌ Không | ✅ Có sẵn (`BudgetInfo.UsedPercent`) |
| **Tự khôi phục trạng thái sau crash** | ❌ | ❌ | ✅ Có (`RecoverRecheckInProgress`) |

## Rủi ro nếu không sửa (cho vCreator)

1. **Chi vượt ngân sách trực tiếp** — không có cơ chế gate, campaign hot có thể trả thưởng vượt số tiền đã duyệt
2. **Race condition khi nhiều creator cùng submit** — không có distributed lock → 100 creator submit content cùng lúc, mỗi process tính reward độc lập → có thể chi gấp nhiều lần budget mà metric vẫn báo "chưa vượt"
3. **Không cap được khi đã vượt** — nếu campaign đáng lẽ chỉ trả 50K còn lại nhưng creator submit content xứng 100K → vCreator sẽ trả full 100K, không có khái niệm "primary 50K + overflow 50K"
4. **Phát hiện muộn** — không có Telegram alert → ops team không biết campaign sắp cạn cho đến cuối kỳ
5. **Khó audit** — không có lịch sử threshold tracking → khó báo cáo cho stakeholder "campaign này đạt 95% lúc nào"
6. **Operations bị động** — admin phải manual check trên dashboard hàng ngày thay vì có cảnh báo tự động

## Đề xuất giải pháp (góc nhìn business)

**Khuyến nghị**: Port toàn bộ engine ngân sách + tính thưởng có cap từ **Ambassador → vCreator**.

**Lý do chọn Ambassador làm template**:
- Ambassador và TCB có engine giống nhau ~90% (cùng thế hệ)
- Nhưng Ambassador đơn giản hơn (chỉ Telegram, không có email)
- vCreator chưa có hệ thống gửi email transactional → port từ Ambassador không cần setup SendGrid mới
- Kết quả tương đương về mặt protection: chặn chi vượt + cap reward + chống race + cảnh báo Telegram

**Effort dự kiến**: 2-3 tuần developer (~600-800 LOC backend + migration data).

**Cần product/business confirm trước khi triển khai**:
1. vCreator hiện có những campaign nào lớn cần kiểm soát? (Nếu chỉ là test campaigns nhỏ → có thể defer)
2. Ai care về budget control ở vCreator? (CFO? Operations? Brand owner?)
3. Có sẵn Telegram channel `[vCreator]` cho budget alert chưa? (cần tạo trước khi launch)
4. Migration: các event vCreator hiện tại sẽ default budget = 0 (không giới hạn) — OK không? Hay cần backfill budget cho các campaign đang chạy?
5. Ambassador có feature `RecoverRecheckInProgress` (tự khôi phục trạng thái sau crash). vCreator có cần luôn không, hay defer P2?
6. Reward V1 hiện tại của vCreator (tính naive không cap) có records cũ — có cần migration để gán `IsBudgetExceeded=false` cho records cũ không?

**Tách 2 việc riêng (có thể defer P2 — không nằm trong gap này)**:
- Port `BudgetInfo` struct (UsedPercent pre-compute) từ Ambassador → TCB: cải thiện performance dashboard TCB
- Port `BudgetCampaign` (custom email alert config) từ TCB → Ambassador: cho team marketing setup alert riêng cho từng stakeholder

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

vCreator thiếu **toàn bộ stack** engine kiểm soát budget + tính reward có cap. Cụ thể thiếu 3 layer:

1. **Schema layer**: `EventRaw` thiếu fields `Budget/Bpu/Bpc/IsBlockReward/IsBlockSubmitContent`. `EventRewardRaw` thiếu fields `IsBudgetExceeded/RecheckInProgress`. `EventTrackingThresholdRaw` collection không tồn tại.
2. **Engine layer**: `event.go` thiếu functions `EstimateBudgetMultiLevel`, `WithBudgetLock`, `HandleBudgetExceeded`, `findRewardPair`, `splitStatistic`, `upsertPrimaryReward`, `upsertOverflowReward`.
3. **Trigger layer**: chỗ tạo reward không gọi budget check, không acquire lock — tính naive `view×giá + like×giá + comment×giá` thẳng.

→ Port từ Ambassador (hoặc TCB) toàn bộ 3 layer.

## So sánh schema chi tiết

### `EventRaw` model

| Field | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| `Budget float64` (event-level cap) | ✅ | ❌ | ✅ (`Bpe *BudgetInfo` struct với UsedPercent) |
| `Bpu float64` (per-user cap) | ✅ | ❌ | ✅ |
| `Bpc float64` (per-content cap) | ✅ | ❌ | ✅ |
| `IsBlockReward bool` | ✅ | ❌ | ✅ |
| `IsBlockSubmitContent bool` | ✅ | ❌ | ✅ |
| `ExtendedPeriod *ExtendedPeriodConfig` | ❌ | ✅ unique | ❌ |

### `EventRewardRaw` model

| Field | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| `IsBudgetExceeded bool` (overflow marker) | ✅ | ❌ | ✅ |
| `RecheckInProgress bool` (đang recheck sau crash) | ✅ | ❌ | ✅ |
| `IsExtended bool` (vCreator's ExtendedPeriod marker) | ❌ | ✅ unique | ❌ |
| `Note string` | ✅ | ✅ | ✅ |

### Models cần tạo mới ở vCreator
- `EventTrackingThresholdRaw` — track threshold milestones (75/95/100%) đã trigger để alert single-fire (không spam)
- `BudgetAlertRaw` (TCB-only optional, defer P2 — không cần trong scope này)

## So sánh engine logic chi tiết

### Reward generation flow

**vCreator hiện tại (V1 naive)**:
```go
// pkg/admin/service/scheduler.go (vCreator) - simplified pseudocode
for each user_event in active campaigns:
    cash := view × CashPerView + like × CashPerLike + comment × CashPerComment
    EventRewardDAO.Insert(EventRewardRaw{
        Cash: cash,
        // KHÔNG check budget
        // KHÔNG acquire lock
        // KHÔNG split primary/overflow
    })
```

**TCB / Ambassador (V2 engine)**:
```go
// internal/service/event.go - simplified pseudocode
WithBudgetLock(eventId, func(freshEvent) {
    available := EstimateBudgetMultiLevel(freshEvent, tracking, userId, contentId)
    // available = min(BPE còn lại, BPU còn lại, BPC còn lại) - totalCashPending

    if available <= 0:
        HandleBudgetExceeded(freshEvent, tracking)  // set IsBlockReward=true + Telegram alert
        return  // không tạo reward

    if cashCalculated > available:
        // Split: primary với cash=available + overflow với cash=0
        upsertPrimaryReward(cash=available)
        upsertOverflowReward(cash=0, IsBudgetExceeded=true)
    else:
        upsertPrimaryReward(cash=cashCalculated)
})
```

### Budget engine functions cần port

Từ Ambassador `internal/service/event.go`:
- `EstimateBudget(ctx, event, tracking, userId, contentId) MultiBudgetResult` — check 3 mức (event/user/content), trả về min available
- `estimateBudgetByEvent(event) float64` — pure calculation BPE
- `estimateBudgetByUser(ctx, event, userId) float64` — query UserEvent → cashTotal đã pending/completed
- `estimateBudgetByContent(ctx, event, contentId) float64` — query Content statistic
- `CombineBudgetEstimates(totalCashPending, ...availableCashes) BudgetEstimateResult` — min available across levels
- `WithBudgetLock(ctx, eventId, fn) error` — Redis distributed lock per event 2 phút
- `HandleBudgetExceeded(ctx, event, tracking)` — track threshold + set block flags + Telegram alert

Reward split functions:
- `findRewardPair(...)` — tìm cặp primary + overflow đã tạo cho user-content
- `splitStatistic(stat, available)` — split metric thành 2 phần (theo budget còn lại)
- `upsertPrimaryReward(...)` — create/update reward với cash > 0
- `upsertOverflowReward(...)` — create/update reward với cash = 0, IsBudgetExceeded = true

## Migration data plan

**vCreator existing records**:
- Tất cả `EventRaw` records: thêm 5 fields default (`Budget=0`, `Bpu=0`, `Bpc=0`, `IsBlockReward=false`, `IsBlockSubmitContent=false`). `Budget=0` đồng nghĩa "no limit" — match behavior cũ.
- Tất cả `EventRewardRaw` records: thêm 2 fields default (`IsBudgetExceeded=false`, `RecheckInProgress=false`)
- `EventTrackingThresholdRaw` collection: tạo mới, rỗng

→ Migration **safe** — không thay đổi behavior cũ cho các campaign hiện hữu. Admin chỉ set Budget cho campaign mới muốn áp dụng.

## Action items

### Phase 1: Schema migration (~1 ngày)

1. **Migrate `EventRaw`**: thêm 5 fields budget + block flags
2. **Migrate `EventRewardRaw`**: thêm 2 fields V2 markers
3. **Tạo collection `EventTrackingThresholdRaw`** + DAO

### Phase 2: Engine port (~1.5-2 tuần)

4. **Port budget engine** từ Ambassador `internal/service/event.go`:
   - `EstimateBudget` + 3 helper functions per level
   - `CombineBudgetEstimates`
   - `WithBudgetLock` (Redis lock)
   - `HandleBudgetExceeded`
5. **Port reward split logic**:
   - `findRewardPair` / `splitStatistic` / `upsertPrimaryReward` / `upsertOverflowReward`
6. **Update reward generation flow** (`pkg/admin/service/scheduler.go` hoặc tương đương) để gọi engine V2 thay vì tính naive

### Phase 3: Alert + recovery (~3 ngày)

7. **Setup Telegram bot config** cho vCreator (chat ID + token riêng — không share với TCB/Ambassador)
8. **Wire `HandleBudgetExceeded` → Telegram message** với label `[vCreator]`
9. **Optional**: port `RecoverRecheckInProgress` cron từ Ambassador (defer P2 nếu không cần ngay)

### Phase 4: Test + rollout (~3 ngày)

10. **Unit test engine functions** (estimate, lock, split)
11. **Integration test**:
    - Tạo event với Budget=1M, Bpu=100K, Bpc=50K
    - 5 creator submit content vượt budget → verify primary + overflow records
    - 100 goroutines submit cùng lúc → verify lock prevent race
12. **Manual smoke test** với staging campaign nhỏ (Budget=100K) để verify alert Telegram

## Effort estimate

| Phase | Task | Effort |
|---|---|---|
| 1 | Schema migration | 1 ngày |
| 2 | Engine port (budget + reward split) | 1.5-2 tuần |
| 3 | Alert + Telegram setup | 3 ngày |
| 4 | Test + rollout | 3 ngày |
| | **Tổng** | **~2-3 tuần** |

Ước lượng LOC: ~600-800 LOC service + ~50 LOC schema + ~50 LOC migration script.

## Risks + mitigations

1. **Schema migration affect existing data** → Default values (Budget=0 = no limit) ensure backward compat
2. **Redis lock timeout có thể block reward generation** → Test với realistic load, monitor lock contention metric
3. **Telegram channel chưa setup** → Tạo channel + bot trước khi merge, fallback: log to console nếu config trống (TCB và Ambassador đều có pattern này)
4. **vCreator reward V1 records cũ không có overflow concept** → Migration safe: existing records giữ nguyên logic V1, V2 chỉ apply cho records mới sau khi merge

## Câu hỏi business mở

1. **Telegram chat config**: vCreator có cần tách channel riêng `[vCreator]` hay share với Ambassador?
2. **Backfill budget cho campaign cũ**: ops team có muốn set Budget cho campaign đang chạy không? Nếu có → cần tool admin để bulk update.
3. **`PartnerInfluencerConfig` (TCB-only)**: vCreator có cần concept "auto-approve creator theo budget tier" không? Hay chỉ cần budget control thuần túy.

## Files referenced

**Ambassador (source of truth — recommended port from)**:
- `internal/service/event.go` — engine V2 (~250 LOC budget + reward split logic)
- `internal/model/mg/event.go:49-51,...` — fields `Bpe/Bpu/Bpc/IsBlockReward/IsBlockSubmitContent`
- `internal/model/mg/event_reward.go:21-23` — fields `IsBudgetExceeded/RecheckInProgress`
- `internal/model/mg/event_tracking_threshold.go` — threshold tracking schema
- `pkg/admin/handler/event_budget.go` — admin `UpdateBudget` API

**TCB (alternative source, có thêm email alert + BudgetCampaign)**:
- `internal/service/event.go:95-170` — `EstimateBudgetByEvent` + threshold + telegram
- `internal/service/budget.go` — `BudgetCampaign.CheckThresholdByEventID` + email
- `internal/model/mg/budget_alert.go` — `BudgetCampaignRaw` schema (custom alert)

**vCreator (target)**:
- `internal/service/event.go` — KHÔNG có budget engine
- `internal/model/mg/event.go` — KHÔNG có 5 fields budget
- `internal/model/mg/event_reward.go` — KHÔNG có 2 fields V2 markers
