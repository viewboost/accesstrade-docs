# Semantic Diff — Campaign & Event Group

> **Generated**: 2026-05-07
> **Method**: Đọc 7 service files + 11 model files (~7300 LOC) ở 3 dự án, diff struct + key functions, focus reward calculation engine và budget control.
> **Files trong scope**:

| Service | TCB | vCreator | Ambassador | Notes |
|---|---:|---:|---:|---|
| `service/event.go` | 1503 | 1123 | 1596 | 3 md5 khác — divergent ở budget engine + analytics aggregation |
| `service/event_schema.go` | 902 | 747 | 1281 | 3 md5 khác — TCB+Amb có primary/overflow split, vCreator thì không |
| `service/filtered_campaigns.go` | 138 | ❌ | ❌ | TCB-only — analytics endpoint cho dashboard |
| **Total** | **2543** | **1870** | **2877** | **7290 LOC** |

**Models đọc cùng**: `event`, `event_schema`, `event_categories` (TCB-only), `event_bonus`, `event_reward`, `event_reward_temp`, `event_tracking_threshold` (TCB+Amb), `event_analytic_daily`, `user_event`, `user_event_analytic_daily`, `campaign` (TCB-only), `campaign_matching` (TCB-only).

---

## TL;DR

1. **Reward engine 3 dự án chia thành 2 thế hệ rõ rệt**:
   - **Thế hệ V2 (TCB + Ambassador)**: Multi-level budget (Event/User/Content) + distributed lock (`WithBudgetLock`) + **primary/overflow reward split** với priority Milestone > Like > Comment > View. Reward bị cắt khi vượt ngân sách → tạo "overflow" record (cash=0, `isBudgetExceeded=true`).
   - **Thế hệ V1 (vCreator)**: KHÔNG có budget concept ở level model (`Budget/Bpu/Bpc` đều thiếu). Reward = `view×CashPerView + like×CashPerLike + comment×CashPerComment` thẳng, không cap. Thay vào đó vCreator có **ExtendedPeriod** (force cash=0 sau khi event end) — concept hoàn toàn khác.

2. **TCB là dự án "campaign system" duy nhất**. `Event` = thử thách creator-facing. `Campaign` (model riêng `campaign.go` + `campaign_matching.go`) là **influencer matching engine**: chọn list influencer theo BudgetTiers/Categories/MinEngagement, score weights (Category/Tier/Engagement), lưu `SelectedInfluencer` + `MatchingSession` results. 2 dự án kia hoàn toàn không có concept campaign-matching. Đây là **flagship feature TCB** (T-Fluencers).

3. **Ambassador có 2 sophistication mới mà TCB chưa có**:
   - `RecoverRecheckInProgress()` — recovery cron quét reward bị stuck `recheckInProgress=true` và rerun `processRewardForSchema`.
   - `BudgetInfo` struct (Total/Used/Remain/UsedPercent) cho `Bpe` thay vì float đơn — pre-computed dashboard view của budget.
   - `HandleBudgetExceeded` tách rời (TCB embed trong `EstimateBudgetByEvent`).

4. **vCreator KHÔNG có** budget tracking, threshold alert, multi-level cap, primary/overflow split, recheck recovery, telegram alert. Tracking minimal: chỉ statistic theo source và update reward "naive" theo công thức × giá. Phù hợp với business model "single brand simple campaign".

5. **Per-platform support divergent**: TCB hỗ trợ 7 source (TikTok/YouTube/YT Short/FB/FB Reel/IG/IG Reel). vCreator thêm **Threads**. Ambassador thêm **Threads + ShopeeVideo + FacebookPost** (8 source). → Ambassador là dự án creator-economy **đa nền tảng nhất**.

---

## 1. `service/event.go` — Budget engine + statistic aggregation

### Skeleton chung (cả 3 đều có)
- `UpdateEventStatistic(eventId)`: aggregate cash totals từ `UserEventRaw` → update `event.statistic`
- `UpdateStatisticUserEvent(userId, eventId)`: aggregate per-platform stats (view/like/comment) cho 1 user trong 1 event → update `UserEventRaw.statistic`
- `UpdateAnalyticEventDaily / UpdateAnalyticUserEventDaily`: per-day rollup cho `event_analytic_daily` và `user_event_analytic_daily`

3 dự án **đều dùng goroutines song song** (`sync.WaitGroup`) để aggregate đồng thời từ 4-5 collection (`EventRewardRaw`, `ContentRaw`, `UserEventRaw`, `EventBonusRaw`, `ReferralRaw`).

### Khác biệt theo dự án

#### TCB (1503 LOC) — **Multi-level budget engine + threshold auto-block**

Interface:
```go
EstimateBudgetByEvent(ctx, event, tracking) bool                              // event-level only check + alert
EstimateBudgetMultiLevel(ctx, event, tracking, userId, contentId) MultiBudgetResult  // event + user + content
WithBudgetLock(ctx, eventId, fn) error                                        // Redis distributed lock
UpdateBudgetStatistic(ctx, userId, eventId, contentId)                        // post-reward refresh
UpdateAnalyticEventDailyWhenContentChangeStatus(...)                          // re-rollup ngày trước khi đổi status
```

Feature đặc biệt:
- **3 tier budget**: `event.Budget` (BPE) / `event.Bpu` (per-user) / `event.Bpc` (per-content) (model `event.go:44-46`).
- **Threshold tracking 75/95/100%** (`event_tracking_threshold` collection): khi đạt mỗi mốc thì:
  - 75%: gửi notification + email cho mọi user trong event (`Notification().SendNotificationAndEmailBudgetToAllUserInEvent`)
  - 95%: tự động `isBlockSubmitContent = true`
  - 100%: tự động `isBlockReward = true` + `isBlockSubmitContent = true` + Telegram alert (`token.budget` channel)
  - Logic ở `service/event.go:415-481` (`UpdateEventStatistic`)
- **`computeMaxCashForContent`** (line 284): tính max cash cho 1 content "add-back" lượng đang dùng của primary record cũ — dùng khi update reward không phải insert mới (avoid double-count).
- **`UpdateAnalyticEventDailyWhenContentChangeStatus`**: khi content đổi status (approved → rejected), re-rollup mọi `event_analytic_daily` trước thời điểm đó.

#### vCreator (1123 LOC) — **No budget, no lock, has ExtendedPeriod**

Interface:
```go
UpdateStatisticUserEvent(ctx, userId, eventId)
UpdateAnalyticEventDaily(...)
UpdateAnalyticUserEventDaily(...)
UpdateAnalyticOldEventDaily(ctx, event, q)        // unique vCr+Amb
```

Feature đặc biệt:
- **KHÔNG có** `EstimateBudget*`, `WithBudgetLock`, `UpdateBudgetStatistic`, `UpdateEventStatistic` (!) trong interface.
- Nhưng tracking **`ExtendedPeriod`** — model `event.go:81-87` (`ExtendedPeriodConfig{Enabled, RecordMonth, RecordYear}`). Trong `UpdateAnalyticUserEventDaily` (line 52-57):
  ```go
  isExtended = event.IsExtendedPeriod()
  if isExtended && !q.IsSkipChangeTimeExtended {
      fromAt = event.GetRecordingDate(fromAt)
  }
  ```
  → Sau khi event end, vẫn tracking thêm 1 chu kỳ tracking (record month/year) cho metric chasing — nhưng cash của reward = 0 (xem section 2 vCreator).
- **Ý nghĩa nghiệp vụ**: vCreator không cần ngân sách vì có thể chỉ là 1 brand single-tenant (không có rủi ro vượt ngân sách như multi-partner TCB). ExtendedPeriod = "track tiếp engagement nhưng không chi thêm tiền".

#### Ambassador (1596 LOC, file lớn nhất) — **TCB pattern + recovery + Bpe struct**

Interface:
```go
EstimateBudget(ctx, event, tracking, userId, contentId) MultiBudgetResult     // gộp event/user/content vào 1 hàm
WithBudgetLock(ctx, eventId, fn) error
HandleBudgetExceeded(ctx, event, tracking)        // tách riêng (TCB embed trong EstimateBudgetByEvent)
UpdateEventStatistic / UpdateStatisticUserEvent / UpdateAnalyticEventDaily / UpdateAnalyticUserEventDaily / UpdateAnalyticOldEventDaily / UpdateBudgetStatistic
```

Feature đặc biệt:
- **`event.Bpe` là struct `BudgetInfo{Total, Used, Remain, UsedPercent}`** thay vì float — pre-compute dashboard view, update mỗi lần `UpdateEventStatistic` (line 103-118). TCB lưu raw `event.Budget` float + tự tính khi cần.
- **Lock 2 phút** thay vì 30s của TCB (`event.go:278`): `redis.NewMutexWithExpiration(... 2*time.Minute)` → có lẽ Ambassador có flow long-running cần lock lâu hơn.
- **`HandleBudgetExceeded`** (line 296-365) là hàm độc lập — caller phải gọi rõ ràng sau khi nhận `MultiBudgetResult.EventExceeded == true`. TCB nhúng logic này vào `EstimateBudgetByEvent`.
- **Threshold alert chỉ gửi 1 lần / 1 mốc**: Ambassador có flag `isSendNotification` (line 299) — chỉ gửi telegram khi insert mới threshold record. TCB không có flag này (gửi mỗi lần phát hiện vượt — có thể spam).
- Telegram message format: "🚫 [Ambassador] Cảnh báo..." (line 341) — TCB chỉ "🚫 Cảnh báo..." → 2 dự án dùng channel telegram riêng cho phép phân biệt source.
- **`event.Category AppID`** (line 47) là field direct trong EventRaw, không phải collection riêng như TCB. **`IsApproved bool`** (line 48) → Ambassador có admin approval flow cho event trước khi go-live (TCB và vCr không có).
- **`ParticipationRequirements`** (line 53, struct riêng): Email/Phone/Facebook required + `FacebookMinFollowers` + `FacebookMinAccountAgeMonths` → gating ai được join event (TCB và vCr không có).
- **`ResourceLibrary *ActionType`** — link đến library kit (asset/template) cho creator (chỉ Ambassador).

---

## 2. `service/event_schema.go` — Reward calculation core

### Skeleton chung
- `CheckPassSchemaByContentMilestone` / `CheckPassSchemaByViewMilestone`: check milestone schema (1-time bonus)
- `CheckPassSchemaByStatistic`: check statistic schema (per-view/like/comment) — gọi `CheckPassSchemaWithContent` cho mỗi schema.
- `RecheckSchemaWithContentWhenChangeStatus`: re-process khi content đổi status
- `UpdateRewardTypeByStatisticContent`: core — tính cash từ doc analytics rồi upsert reward record
- `CheckPassSchemaTypeByViewMilestoneWithListSchema`: bulk check view milestone "version II"

### Khác biệt CỐT LÕI: cách tạo reward

#### TCB & Ambassador — **Primary/Overflow split pattern (V2)**

Cả 2 dự án có:
- `processRewardParams` struct (TCB:634, Amb:50) — đồng bộ 8 field: Event, Content, Schema, Doc, Status, FullStat, FullCash
- `findRewardPair(userId, schemaId, contentId, date, ...)` — tìm 2 record (primary với `isBudgetExceeded=false`, overflow với `isBudgetExceeded=true`)
- `splitStatistic(origStat, maxCash, cashReward)` — chia stat theo priority **Milestone > Like > Comment > View** (TCB:681, Amb:401). Floor division cho discrete units.
- `upsertPrimaryReward / upsertOverflowReward / deleteOverflowIfExists`
- `processRewardForSchema(ctx, p)` — orchestrator gọi `WithBudgetLock` + `computeMaxCashForContent` + `splitStatistic` + upsert.

**Khác biệt nhỏ TCB vs Ambassador**:
- **TCB `findRewardPair` filter thêm `status`** (line 654: `"status": status`) — match primary/overflow trong cùng status. Ambassador KHÔNG filter status (line 67) → "rewards persist across status changes" (comment ở Amb line 62).
  - **Ý nghĩa**: Ambassador giữ 1 reward record xuyên suốt status pending → approved → rejected. TCB tạo record riêng cho từng status → chuỗi audit dài hơn nhưng có thể duplicate.
- **TCB có `isSkipBlockReward bool` parameter** trong `CheckPassSchemaByStatistic / CheckPassSchemaWithContent` (line 23, 26) — Ambassador và vCreator không có. Cho phép admin force-create reward bỏ qua block check (manual recovery scenario).
- **Ambassador có `RecoverRecheckInProgress()`** (line 1160) — chỉ Ambassador. Recovery cron:
  ```go
  // Find all rewards still flagged
  bson.M{"recheckInProgress": true, "type": "by_statistic"}
  // Group by contentId+date (dedup)
  // Re-run processRewardForSchema
  ```
  → Phòng case service crash giữa chừng khi đang `WithBudgetLock` rồi update `recheckInProgress=true` nhưng chưa kịp set false. TCB chưa port phần này.
- **`processRewardForSchema` return**: TCB trả `error`, Ambassador trả `void` (line 185) — Ambassador "fire and forget" hơn.

#### vCreator — **Naive single-record per (user, schema, content, date, status, isExtended)**

Không có `processRewardParams`, `findRewardPair`, `splitStatistic`, primary/overflow concept. `UpdateRewardTypeByStatisticContent` (line 173-329):

```go
totalLike := doc.Like.Value - like.Completed
totalView := doc.View.Value - view.Completed
totalComment := doc.Comment.Value - comment.Completed

reward := &EventRewardRaw{
    Statistic: EventRewardStatistic{
        TotalLike:        int64(totalLike),
        TotalCashLike:    pfloat.RoundToOneDecimal(totalLike * schema.CashReward.CashPerLike),
        ...
    },
}
// Extended period: force cash = 0
if doc.IsExtended {
    reward.Statistic.TotalCashView = 0
    reward.Statistic.TotalCashLike = 0
    reward.Statistic.TotalCashComment = 0
    reward.IsExtended = true
}
reward.Cash = pfloat.RoundToOneDecimal(reward.Statistic.TotalCashLike + reward.Statistic.TotalCashComment + reward.Statistic.TotalCashView)
```

Sau đó upsert đơn giản 1 record bằng `BulkWrite` (insert hoặc update). KHÔNG có budget check, KHÔNG có cap. → vCreator hoàn toàn tin tưởng admin sẽ chọn schema phù hợp với ngân sách.

**ExtendedPeriod handling unique**:
- Schema condition skip startAt/endAt nếu `isExtended` (line 201-208) — cho phép tạo reward cho ngày sau khi event end.
- Reward `IsExtended = true` → cash forced 0 nhưng vẫn track stat → để analytics tracking.
- Filter reward existing thêm điều kiện `isExtended` (line 298-302) → reward thường và reward extended là 2 record riêng biệt.

**`CheckPassSchemaByContentMilestone`** vCreator KHÔNG có hàm `computeMaxCashForContent` — milestone reward tạo trực tiếp với cash = `s.CashReward.CashMilestone` không qua budget lock.

### Diff bảng `EventSchemaInterface`

| Function | TCB | vCr | Amb |
|---|:---:|:---:|:---:|
| CheckPassSchemaByContentMilestone | ✅ | ✅ | ✅ |
| CheckPassSchemaByViewMilestone | ✅ | ✅ | ✅ |
| CheckPassSchemaByStatistic | ✅ (+ `isSkipBlockReward`) | ✅ | ✅ |
| CheckPassSchemaWithContent | ✅ (+ `isSkipBlockReward`) | ✅ | ✅ |
| RecheckSchemaWithContentWhenChangeStatus | ✅ (return error) | ✅ (void) | ✅ (void) |
| UpdateRewardTypeByStatisticContent | ✅ (return error, primary/overflow) | ✅ (void, naive) | ✅ (void, primary/overflow) |
| CheckPassSchemaTypeByViewMilestoneWithListSchema | ✅ (sequential) | ✅ (goroutine per schema) | ✅ |
| **RecoverRecheckInProgress** | ❌ | ❌ | ✅ |

---

## 3. `service/filtered_campaigns.go` — TCB-only analytics endpoint

### Existence
TCB-only (138 LOC). vCreator và Ambassador đều ❌.

### Function
1 hàm public: `GetFilteredCampaigns(ctx, q *mgquery.CommonQuery) (*FilteredCampaignsResponse, error)`

Aggregation pipeline duy nhất từ `event_analytic_daily`:
- Filter theo `date`, `event` (eventIds), `partner`
- `$lookup` để join với event để lấy Name/Code/Status/Budget
- Trả `FilteredCampaignData` 16 field cho từng event:
  - Tổng: Videos, Views, Likes, Comments, Shares
  - Cash: Budget, BudgetUsed (= TotalCash - TotalCashRejected)
  - **CPV** (Cost Per View) = round(BudgetUsed / Views, 2 decimals)
  - Phân loại: ApprovedVideos, PendingVideos, RejectedVideos
  - CreatorCount

### Ý nghĩa nghiệp vụ
Endpoint này feed **T-Fluencers Analytics Dashboard** (CLAUDE.md TCB nói rõ project này là Next.js dashboard). 16 fields gần như map 1-1 với widget KPI dashboard (bảng Influencer Performance, KPI cards). 2 dự án còn lại không cần dashboard kiểu này → không port.

Có hàm `buildCacheKey` (line 122-138) nhưng không thấy dùng trong file → có thể là dead code chuẩn bị cho future caching hoặc dùng ở handler.

---

## 4. Models phát hiện thú vị

### `EventRaw` — divergent nhất

| Field | TCB (36) | vCr (27) | Amb (34) | Ý nghĩa |
|---|:---:|:---:|:---:|---|
| `Categories []AppID` | ✅ | ❌ | ❌ | TCB có thể nhiều category/event |
| `Category AppID` (single) | ❌ | ❌ | ✅ | Ambassador 1 category/event (đơn giản hơn) |
| `CriteriaContent []string` | ✅ | ❌ | ❌ | TCB có rule check content |
| `Budget` (float) | ✅ | ❌ | ❌ | TCB raw budget |
| `Bpe *BudgetInfo` (struct) | ❌ | ❌ | ✅ | Amb pre-computed budget view |
| `Bpu, Bpc` | ✅ | ❌ | ✅ | Per-user/per-content cap |
| `IsBlockReward, IsBlockSubmitContent` | ✅ | ❌ | ❌ | TCB auto-block khi vượt ngân sách |
| `Reward string` | ❌ | ✅ | ✅ | Free-text reward description |
| `Videos []*FileVideo` | ❌ | ✅ | ✅ | Media gallery cho event |
| `AutoRejectConditions` | ❌ | ✅ | ✅ | Auto reject content theo view/like/engagement |
| `ExtendedPeriod *ExtendedPeriodConfig` | ❌ | ✅ | ❌ | vCr-only: track sau khi end |
| `IsApproved` | ❌ | ❌ | ✅ | Amb-only: admin approval gate |
| `ParticipationRequirements` | ❌ | ❌ | ✅ | Amb-only: gating ai join (FB followers + age) |
| `ResourceLibrary *ActionType` | ❌ | ❌ | ✅ | Amb-only: asset/template kit |
| `Options.ApplyForStaff/ApplyForSegments/StaffCodes` | ✅ | ❌ | ❌ | TCB-only: staff-targeting + segment-targeting |

**Pattern**:
- TCB tập trung **budget control + staff targeting** (multi-tenant với HR integration).
- vCreator tập trung **reward description + extended tracking** (single-brand simple).
- Ambassador tập trung **gating + media kit + admin approval** (creator-economy với KYC).

### `EventSchemaRaw` — gần như đồng bộ

3 dự án **17 fields giống nhau ở EventSchemaRaw**. Khác biệt nhỏ:
- vCreator + Ambassador: `EventSchemaMilestone` có thêm field `MinimumOfView` (3 fields). TCB chỉ 2 fields (`NumberOfContent, NumberOfView`).
  - **Ý nghĩa**: vCr/Amb cho phép schema "phải đạt ≥ X view mới start tracking milestone" → guard khỏi bots/spam impressions ban đầu.

### `EventRewardRaw` — primary/overflow signature

| Field | TCB | vCr | Amb |
|---|:---:|:---:|:---:|
| `IsBudgetExceeded bool` | ✅ | ❌ | ✅ |
| `RecheckInProgress bool` | ✅ | ❌ | ✅ |
| `IsExtended bool` | ❌ | ✅ | ❌ |

→ TCB và Ambassador **đồng bộ schema reward** (primary/overflow flag + recheck flag). vCreator chỉ có `IsExtended` cho ExtendedPeriod logic riêng. Chứng tỏ TCB và Ambassador cùng "thế hệ V2" của reward engine, vCreator là V1.

### `EventBonusRaw` — TCB có 2 field thêm

TCB EventBonusRaw có thêm `SearchString` + `CompletedAt` (17 fields). vCr và Amb chỉ 15 fields giống nhau.
- `SearchString` = search index Vietnamese non-accent
- `CompletedAt` = timestamp khi bonus được transfer

→ TCB cần search admin UI cho bonus + cần track "completion" cho reconciliation.

### `EventTrackingThresholdRaw` — TCB+Amb only

Identical 5 fields ở TCB và Ambassador (`ID, Event, Threshold, CreatedAt, UpdatedAt`). vCreator KHÔNG có collection này → vCreator không có alert system nhiều mức.

### `EventCategoriesRaw` — TCB-only

Standalone collection 8 fields (TCB). vCreator + Ambassador: KHÔNG có. Ambassador thay bằng `Category AppID` direct trong EventRaw → less normalized nhưng đơn giản hơn.

### `UserEventStatistic` — divergent ở per-platform support

| Platform fields | TCB (15) | vCr (16) | Amb (18) |
|---|:---:|:---:|:---:|
| Tiktok, Youtube, YoutubeShort, Facebook, FacebookReels, Instagram, InstagramReels | ✅ | ✅ | ✅ |
| Threads | ❌ | ✅ | ✅ |
| FacebookPost, ShopeeVideo | ❌ | ❌ | ✅ |
| `UserEventOpts.CodeInput, StatusEmployee` | ✅ | ❌ | ❌ |

→ Ambassador hỗ trợ creator nhiều nhất (8 platform). TCB ít nhất nhưng có **`UserEventOpts.CodeInput`** (mã invitation) + **`StatusEmployee`** (link với user-partner staff approval) → tracking employee-only events.

### `EventAnalyticDailyRaw` — TCB+Amb track Bonus, Amb track Category

- TCB: 17 fields trong `EventAnalyticDailyStatistic`, có `Bonus` (event_bonus rollup).
- vCr: 17 fields, **không có Bonus**, có `Threads`.
- Amb: 19 fields (nhiều nhất), có `FacebookPost`, `ShopeeVideo`, `Threads` + `Category` ở root level.

### `CampaignRaw` & `CampaignMatchingSessionRaw` — TCB-only

Hoàn toàn khác concept với Event:
- `CampaignRaw` (19 fields): `BudgetTiers []string`, `MinEngagement`, `Weights{Category, Tier, Engagement}`, `SelectedInfluencers []SelectedInfluencer{Platform, ExternalID, Name, Score, AddedAt}`, `MatchingCount`, `LastMatchedAt`.
- `CampaignMatchingSessionRaw` (13 fields): per-session log với `Influencers (input)`, `Results []MatchingSessionResult{FinalScore, Suitable, Breakdown{Category, Tier, Engagement}}`, `LatencyMs`, `AvgScore`.

→ Đây là **Influencer Matching Engine**: nhập danh sách influencer + criteria + weights → API chấm điểm theo từng dimension → trả ranked list. Đây là feature core T-Fluencers (TCB analytics platform). Không liên quan trực tiếp đến `Event` (creator-facing thử thách).

**Lưu ý cẩn**: `EventBudget` struct trong Ambassador (`event.go:67`) định nghĩa `{Event, PerUser, PerContent}` nhưng `grep -r "EventBudget"` chỉ thấy 1 hit duy nhất (định nghĩa) → **dead code**. Ambassador chuyển sang dùng `Bpe (BudgetInfo) + Bpc + Bpu` floats thay thế.

---

## 5. Câu hỏi business mở (cần PM/business team xác nhận)

1. **vCreator có dự định port budget engine không?** Hiện tại vCreator chỉ có `EventSchemaCashReward` (CashPerLike/View/Comment/Milestone) nhưng không có cap. Nếu chạy event lớn với KOL nhiều view → có rủi ro vượt ngân sách thực tế. Có phải vCreator cố ý đơn giản hóa vì 1 brand cố định, hay là tech debt?

2. **TCB Campaign vs Event là 2 concept hoàn toàn khác?** Confirm: `Event` = thử thách (creator submit content, được thưởng). `Campaign` = tool admin chọn list influencer mời tham gia (matching engine). 2 cái này có liên kết runtime không? (Tôi không thấy field `event` trong `CampaignRaw` hoặc ngược lại.)

3. **Ambassador `LinkCampaignToEvent`** trong `affiliate.go` (separate group) tạo `CampaignAffiliateMappingRaw` — đây là concept campaign khác với TCB Campaign. Ambassador có 2 loại "campaign" (affiliate campaign vs event)? Confirm naming.

4. **Ambassador `BudgetInfo` struct cho Bpe có phải để show realtime trên admin UI?** Pre-compute UsedPercent thay vì tính khi cần — chứng tỏ admin có dashboard hiển thị progress bar budget. TCB lưu raw float → cần frontend tự tính. Cân nhắc port `BudgetInfo` sang TCB cho consistency.

5. **vCreator ExtendedPeriod (RecordMonth/RecordYear)** dùng cho metric chasing nào? Ví dụ: event end tháng 3 nhưng vẫn track view ngày 2-3 tháng 4 (record month=3). Đây có phải cho cycle reward dạng "thưởng theo tháng" hay là tránh skip data ngày cuối?

6. **`Ambassador.RecoverRecheckInProgress`** — có cron call nó không? Logic recovery tốt nhưng nếu không có scheduler → dead code. Tôi không grep thử trong handlers/jobs để verify.

---

## 6. Tổng kết group

### Bảng tổng hợp

| Khía cạnh | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| **Reward engine generation** | V2 (primary/overflow) | V1 (naive) | V2 (primary/overflow) |
| **Budget control** | 3 tier (BPE/BPU/BPC) raw float | KHÔNG có | 3 tier với BPE struct |
| **Distributed lock** | Redis 30s | KHÔNG có | Redis 2 phút |
| **Threshold alerts** | 75/95/100% (auto-block) | KHÔNG có | 75/95/100% (single-fire flag) |
| **Telegram alert** | ✅ | ❌ | ✅ (label `[Ambassador]`) |
| **Recheck recovery** | ❌ | ❌ | ✅ `RecoverRecheckInProgress` |
| **Extended period** | ❌ | ✅ unique | ❌ |
| **Admin approval (event)** | ❌ | ❌ | ✅ `IsApproved` |
| **Participation gating** | Staff/Segment | ❌ | FB followers/age/email/phone |
| **Resource library kit** | ❌ | ❌ | ✅ |
| **Categories** | Collection riêng | ❌ | Field direct (single) |
| **Campaign matching engine** | ✅ unique | ❌ | ❌ |
| **Filtered campaigns analytics** | ✅ unique | ❌ | ❌ |
| **Platforms supported (UserEvent)** | 7 | 8 (+Threads) | 8 (+FacebookPost/ShopeeVideo/Threads) |

### Direction port đề xuất

**Từ TCB → vCreator** (nếu vCr cần budget control):
- Port `EstimateBudget*` + `WithBudgetLock` + `EventTrackingThresholdRaw` + `findRewardPair`+`splitStatistic`+`upsertPrimaryReward`+`upsertOverflowReward`
- ~600-800 LOC port effort
- Block: vCr cần thêm 4 fields vào `EventRaw` (Budget/Bpu/Bpc/IsBlockReward) → migration data.

**Từ Ambassador → TCB**:
- Port `BudgetInfo struct` thay cho float `Budget` → nicer dashboard view (~50 LOC + migration `event` collection).
- Port `RecoverRecheckInProgress` cron → robustness sau crash (~80 LOC + add job scheduler).
- Port `isSendNotification` flag (single-fire alert) → tránh spam telegram khi crash loop (~5 LOC).

**Từ TCB → Ambassador**:
- Port `isSkipBlockReward bool` parameter → cho phép admin override (~10 LOC, ít rủi ro).

**Tách rời lâu dài**:
- TCB `Campaign` + `CampaignMatching` → flagship feature riêng (T-Fluencers), không nên port ra dự án khác.
- vCreator `ExtendedPeriod` → đặc thù single-brand, không nên port nếu TCB/Amb không có use case.
- Ambassador `ParticipationRequirements` → đặc thù creator-economy (FB followers gate), TCB thay bằng staff/segment, không tương đương.

### Effort thực tế cho doc này
- Đọc 7 service files + 13 model files (~7300 LOC): ~60 phút
- Diff Python script + grep smoke test: ~5 phút
- Synthesis viết doc: ~25 phút
- **Tổng ~90 phút** — đúng dự đoán cho group lớn nhất.

---

## Files referenced

- TCB:
  - `accesstrade-projects/techcombank/backend/internal/service/{event,event_schema,filtered_campaigns}.go`
  - `accesstrade-projects/techcombank/backend/internal/model/mg/{event,event_schema,event_categories,event_bonus,event_reward,event_reward_temp,event_tracking_threshold,event_analytic_daily,user_event,user_event_analytic_daily,campaign,campaign_matching}.go`
- vCreator:
  - `accesstrade-projects/vcreator/backend/internal/service/{event,event_schema}.go`
  - `accesstrade-projects/vcreator/backend/internal/model/mg/{event,event_schema,event_bonus,event_reward,event_reward_temp,event_analytic_daily,user_event,user_event_analytic_daily}.go`
- Ambassador:
  - `accesstrade-projects/ambassabor/backend/internal/service/{event,event_schema}.go`
  - `accesstrade-projects/ambassabor/backend/internal/model/mg/{event,event_schema,event_bonus,event_reward,event_reward_temp,event_tracking_threshold,event_analytic_daily,user_event,user_event_analytic_daily}.go`
- Related (ngoài scope nhưng tham chiếu):
  - Ambassador `service/affiliate.go` — `LinkCampaignToEvent` (concept campaign khác).
  - TCB `frontend/admin/dashboard` — consumer của `filtered_campaigns.go`.
