# PRD: Budget Per User (BPU) & Budget Per Content (BPC)

> Ngày viết: 2026-04-06
> Nguồn tham chiếu: Ambassador project (`/ambassador/backend/internal/service/event.go`, `event_schema.go`)
> Trạng thái: Draft

---

## 1. Tổng quan

### 1.1. Bối cảnh

Hệ thống hiện tại chỉ có **budget cấp Event** (`EventRaw.Budget`) — giới hạn tổng chi tiêu của toàn bộ thử thách. Khi budget event cạn, **tất cả user** đều bị block reward cùng lúc, bất kể mỗi user đã nhận bao nhiêu.

Điều này gây ra vấn đề:
- Một số user "ngốn" phần lớn budget → user khác không còn cơ hội nhận thưởng
- Một bài đăng viral có thể tiêu hết budget → các bài đăng khác bị thiệt thòi
- Không có cơ chế phân bổ công bằng

### 1.2. Giải pháp

Thêm 2 cấp budget mới:
- **BPU (Budget Per User)**: Giới hạn tổng tiền thưởng mỗi user nhận được trong 1 thử thách
- **BPC (Budget Per Content)**: Giới hạn tổng tiền thưởng mỗi bài đăng nhận được trong 1 thử thách

Khi tạo reward, hệ thống kiểm tra **3 cấp đồng thời** và lấy `min()`:
```
AvailableCash = min(EventAvailable, UserAvailable, ContentAvailable)
```

### 1.3. Scope

| Trong scope | Ngoài scope |
|-------------|-------------|
| Thêm `Bpu`, `Bpc` fields vào `EventRaw` | Thay đổi `EventRaw.Budget` sang `BudgetInfo` struct |
| Multi-level budget estimation (Event + User + Content) | Thay đổi logic budget-campaigns (threshold alerts) |
| Budget split algorithm cho reward `byStatistic` | Thay đổi flow email notification |
| Primary/Overflow reward pattern | Thay đổi Telegram alert logic |
| Redis distributed lock cho reward creation | Thay đổi `IsBlockReward` / `IsBlockSubmitContent` logic |
| Admin UI config Bpu/Bpc trên Event detail | Dashboard/report changes |
| `IsBudgetExceeded` flag trên EventReward | |

---

## 2. Thiết kế dữ liệu

### 2.1. EventRaw — Thêm 2 fields

```go
type EventRaw struct {
    // ... existing fields ...
    Budget float64 `bson:"budget,omitempty" json:"budget,omitempty"`  // GIỮ NGUYÊN
    Bpu    float64 `bson:"bpu,omitempty" json:"bpu,omitempty"`       // MỚI - Budget Per User
    Bpc    float64 `bson:"bpc,omitempty" json:"bpc,omitempty"`       // MỚI - Budget Per Content
}
```

**Quy ước giá trị:**
| Giá trị | Ý nghĩa |
|---------|---------|
| `Bpu = 0` | Không giới hạn per user (unlimited) |
| `Bpu > 0` | Giới hạn mỗi user tối đa nhận `Bpu` VND trong thử thách |
| `Bpc = 0` | Không giới hạn per content (unlimited) |
| `Bpc > 0` | Giới hạn mỗi bài đăng tối đa nhận `Bpc` VND |

**Backward compatibility:** Events cũ không có `bpu`/`bpc` → Go default `float64 = 0` → unlimited. Hoàn toàn tương thích.

### 2.2. EventRewardRaw — Thêm 2 fields

```go
type EventRewardRaw struct {
    // ... existing fields ...
    IsBudgetExceeded  bool `bson:"isBudgetExceeded" json:"isBudgetExceeded"`   // MỚI
    RecheckInProgress bool `bson:"recheckInProgress" json:"recheckInProgress"` // MỚI
}
```

| Field | Mô tả |
|-------|-------|
| `IsBudgetExceeded` | `true` = reward này là overflow (cash=0, chứa phần metrics chưa được trả tiền) |
| `RecheckInProgress` | `true` = reward đang được recalculate, tránh race condition |

**Backward compatibility:** Rewards cũ không có field này → Go default `bool = false`. Hoàn toàn tương thích.

### 2.3. Không thay đổi

Các model sau **KHÔNG thay đổi** vì đã có đủ fields cần thiết:
- `UserEventStatistic.GetCashTotal()` — đã aggregate cash từ tất cả platforms
- `ContentRaw.Statistic.Cash` — đã track cash per content (Pending/Completed)
- `EventStatistic` — đã track tổng cash per event
- `BudgetCampaignRaw` — giữ nguyên toàn bộ

---

## 3. Business Logic

### 3.1. Multi-level Budget Estimation

Khi tạo/update reward, hệ thống tính available cash tại 3 cấp:

```
┌─────────────────────────────────────────────────────┐
│  estimateBudgetByEvent(event)                       │
│  if event.Budget == 0 → return MaxFloat64 (unlimit) │
│  cashValid = Pending + Completed + Waiting          │
│  available = event.Budget - cashValid               │
│  return max(available, 0)                           │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  estimateBudgetByUser(event, userId)                │
│  if event.Bpu == 0 → return MaxFloat64 (unlimited)  │
│  Query UserEvent → GetCashTotal()                   │
│  cashValid = Pending + Completed + Waiting          │
│  available = event.Bpu - cashValid                  │
│  return max(available, 0)                           │
│  On DB error → return 0 (fail-closed)               │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  estimateBudgetByContent(event, contentId)           │
│  if event.Bpc == 0 → return MaxFloat64 (unlimited)  │
│  Query Content → Statistic.Cash                     │
│  cashValid = Pending + Completed + Waiting          │
│  available = event.Bpc - cashValid                  │
│  return max(available, 0)                           │
│  On DB error → return 0 (fail-closed)               │
└─────────────────────────────────────────────────────┘

Combined:
  maxCash = min(eventAvailable, userAvailable, contentAvailable)
```

**Nguyên tắc fail-closed:** Khi DB query lỗi → return 0 (không cho chi thêm), KHÔNG return unlimited. Điều này ngăn overspend khi hệ thống gặp sự cố.

### 3.2. Budget Lock (Redis Distributed Mutex)

Để ngăn race condition khi nhiều goroutine crawl cùng event đồng thời:

```
WithBudgetLock(eventId, func(freshEvent) {
    // 1. Re-read event từ DB (fresh data)
    // 2. Compute maxCash
    // 3. Create/update reward
    // 4. Update statistics
})
```

| Tham số | Giá trị |
|---------|---------|
| Key pattern | `budget_event_{eventId}` |
| Expiration | 2 phút |
| Retry | 10 lần, mỗi lần cách 100ms |
| Library | `go-redsync/redsync` (đã có sẵn trong project) |

**Lưu ý:** Lock per event, không phải per user/content. Tất cả reward creation cho cùng 1 event sẽ serialize qua lock này.

### 3.3. Primary/Overflow Reward Pattern

Mỗi combo (user, schema, content, date) có thể tạo **2 reward documents**:

| Document | Điều kiện | Cash | IsBudgetExceeded | Chứa gì |
|----------|-----------|------|-------------------|---------|
| **Primary** | `isBudgetExceeded != true` | >= 0 (actual amount) | `false` | Phần metrics đã được trả tiền |
| **Overflow** | `isBudgetExceeded = true` | = 0 (luôn luôn) | `true` | Phần metrics CHƯA được trả tiền |

**Quy trình tìm reward pair:**
```go
// Primary: không bị budget exceeded
primaryCond["isBudgetExceeded"] = bson.M{"$ne": true}

// Overflow: bị budget exceeded
overflowCond["isBudgetExceeded"] = true
```

**3 kịch bản quyết định:**

```
fullCash = totalView*CashPerView + totalLike*CashPerLike + totalComment*CashPerComment

if fullCash <= maxCash:
    → PRIMARY: cash = fullCash (full metrics)
    → OVERFLOW: xóa nếu tồn tại
    
else if maxCash > 0:
    → PRIMARY: cash = partial (split metrics theo priority)
    → OVERFLOW: cash = 0 (phần metrics còn lại)
    
else (maxCash == 0):
    → PRIMARY: cash = 0
    → OVERFLOW: cash = 0 (full metrics)
```

### 3.4. Budget Split Algorithm

Khi `maxCash < fullCash` nhưng `maxCash > 0`, reward được chia theo **thứ tự ưu tiên**:

```
Priority: Milestone → Like → Comment → View

1. Milestone (fixed amount):
   primary.CashMilestone = min(origMilestone, remaining)
   remaining -= primary.CashMilestone

2. Like (discrete, floor division):
   primary.TotalLike = floor(remaining / CashPerLike)
   primary.TotalLike = min(primary.TotalLike, origTotalLike)
   primary.TotalCashLike = primary.TotalLike * CashPerLike
   remaining -= primary.TotalCashLike

3. Comment (discrete, floor division):
   primary.TotalComment = floor(remaining / CashPerComment)
   primary.TotalComment = min(primary.TotalComment, origTotalComment)
   primary.TotalCashComment = primary.TotalComment * CashPerComment
   remaining -= primary.TotalCashComment

4. View (last priority, gets remainder):
   primary.TotalView = floor(remaining / CashPerView)
   primary.TotalView = min(primary.TotalView, origTotalView)
   primary.TotalCashView = primary.TotalView * CashPerView

Overflow = original - primary (cho mỗi metric)
```

**Floor division:** Đảm bảo không có fractional engagement counts (4.7 likes → 4 likes).

**Invariant:** `TotalView * CashPerView == TotalCashView` luôn đúng sau split.

### 3.5. Add-back Mechanism

Khi recalculate reward (content thay đổi view/like/comment), `currentPrimaryCash` được **trừ khỏi "đã dùng"** trước khi tính available:

```
// Không add-back (SAI):
userCashValid = userEvent.GetCashTotal().Pending  // bao gồm primary cũ
available = Bpu - userCashValid                    // quá nhỏ vì đếm trùng

// Có add-back (ĐÚNG):
userCashValid = userEvent.GetCashTotal().Pending
othersUsed = userCashValid - currentPrimaryCash    // trừ primary cũ ra
available = Bpu - othersUsed                       // chính xác
```

Điều này đảm bảo recalculation là **idempotent** — chạy lại N lần cho cùng kết quả.

### 3.6. Milestone Rewards và BPU/BPC

Milestone rewards (`byContentMilestone`, `byViewMilestone`) có cash cố định → **KHÔNG split**, chỉ **block hoặc allow**:

```
maxCash = computeMaxCashForContent(...)
if milestoneCash > maxCash:
    → BLOCK: không tạo reward
else:
    → ALLOW: tạo reward bình thường (cash = milestoneCash)
```

### 3.7. Tương tác với hệ thống Budget Campaign hiện tại

**KHÔNG thay đổi** logic budget-campaigns. Hai hệ thống hoạt động **song song, độc lập**:

```
Event Budget (Budget field)
├── BPU/BPC (MỚI)
│   └── Kiểm tra khi tạo reward
│   └── Block/split reward nếu vượt
│   └── Hoạt động tự động, real-time
│
├── Budget Campaigns (GIỮ NGUYÊN)
│   └── Kiểm tra sau mỗi crawl
│   └── Gửi email alert khi vượt threshold
│   └── Đánh dấu completed
│
├── Threshold Tracking (GIỮ NGUYÊN - 75%/95%/100%)
│   └── Block submit content tại 95%
│   └── Block reward tại 100%
│   └── Telegram alerts
```

---

## 4. API Design

### 4.1. Update Event Budget — Admin API

**Endpoint:** `PUT /events/:id/budget`

**Request:**
```json
{
    "bpu": 500000,
    "bpc": 200000
}
```

**Validation:**
| Rule | Error |
|------|-------|
| `bpu >= 0` | "budget values must be >= 0" |
| `bpc >= 0` | "budget values must be >= 0" |
| Nếu `event.Budget > 0`: `bpu <= event.Budget` | "bpu must be <= event budget" |
| Nếu `event.Budget > 0`: `bpc <= event.Budget` | "bpc must be <= event budget" |

**Response:** `200 OK`

**Permission:** `budget_edit` hoặc `budget_full`

### 4.2. Event Detail — Response bổ sung

GET `/events/:id` response bổ sung 2 fields:
```json
{
    "_id": "...",
    "budget": 10000000,
    "bpu": 500000,
    "bpc": 200000,
    "statistic": { ... }
}
```

---

## 5. Reward Creation Flow (sau khi implement)

### 5.1. Flow cho schema `byStatistic`

```
Crawl Analytics → UpdateRewardTypeByStatisticContent()
        │
        ▼
  Load event, content, schema
  Tính fullStatistic (views, likes, comments)
  Tính fullCash = sum(metrics * rates)
        │
        ▼
  WithBudgetLock(eventId)          ← Redis mutex
        │
        ▼
  Re-read freshEvent từ DB
  findRewardPair()                 ← Tìm primary + overflow
        │
        ▼
  computeMaxCashForContent()
  ├── estimateBudgetByEvent()      → Event.Budget - cashValid
  ├── estimateBudgetByUser()       → Event.Bpu - userCashValid
  └── estimateBudgetByContent()    → Event.Bpc - contentCashValid
  (với add-back: trừ currentPrimaryCash)
        │
        ▼
  maxCash = min(3 levels)
        │
  ┌─────┼─────────────────┐
  │     │                 │
  ▼     ▼                 ▼
 FULL  SPLIT           EXCEEDED
 ≤max  0<max<full      max=0
  │     │                 │
  ▼     ▼                 ▼
 Upsert  splitStatistic()  Upsert
 primary  │                primary(0)
 Delete   Upsert primary   Upsert
 overflow Upsert overflow  overflow(full)
        │
        ▼
  UpdateBudgetStatistic()
  ├── UpdateStatisticUserEvent()
  ├── Content.UpdateCashStatistic()
  └── UpdateEventStatistic()
        │
        ▼
  HandleBudgetExceeded()  (nếu event-level exceeded)
  (GIỮ NGUYÊN logic hiện tại: threshold 75%/95%/100%)
```

### 5.2. Flow cho schema Milestone

```
Check milestone condition
        │
        ▼
  computeMaxCashForContent()
  maxCash = min(eventAvail, userAvail, contentAvail)
        │
        ▼
  milestoneCash > maxCash?
  ├── YES → BLOCK (không tạo reward)
  └── NO  → Tạo reward bình thường
```

---

## 6. Các file cần thay đổi

### 6.1. Backend — Models

| File | Thay đổi | Rủi ro |
|------|----------|--------|
| `internal/model/mg/event.go` | Thêm `Bpu`, `Bpc` fields | Thấp |
| `internal/model/mg/event_reward.go` | Thêm `IsBudgetExceeded`, `RecheckInProgress` | Thấp |

### 6.2. Backend — Aggregation Pipelines

| File | Thay đổi | Rủi ro |
|------|----------|--------|
| `aggregate_pipeline/event_reward.go` — `GetTotalCashRewardByEvent` (line 652) | Thêm filter `"isBudgetExceeded": bson.M{"$ne": true}` vào match stage | Trung bình |
| `aggregate_pipeline/event_reward.go` — `GetTotalCashRewardByContent` (line 238) | Thêm filter `"isBudgetExceeded": bson.M{"$ne": true}` vào match stage | Trung bình |
| `aggregate_pipeline/event_reward.go` — `GetEventRewardStatisticAllByContentIDs` (line 766) | Thêm `Waiting` status vào cash aggregation | Trung bình |

**Lưu ý:** Các pipeline khác (`GetStatisticRewardReport`, `GetStatisticContentBySource`, `GetEventUserStatisticByUserAndEvent`) **KHÔNG cần sửa** vì:
- Cash sums tự nhiên đúng (overflow.cash = 0)
- View/like/comment sums cần bao gồm cả primary + overflow (= tổng thực tế)

### 6.3. Backend — Services

| File | Thay đổi | Rủi ro |
|------|----------|--------|
| `internal/service/event.go` | Thêm: `estimateBudgetByUser()`, `estimateBudgetByContent()`, `CombineBudgetEstimates()`, `computeMaxCashForContent()`, `WithBudgetLock()`, `UpdateBudgetStatistic()`. **GIỮ NGUYÊN** hàm `EstimateBudgetByEvent()` cũ. | Trung bình |
| `internal/service/event_schema.go` | **VIẾT LẠI** `UpdateRewardTypeByStatisticContent()` và `CheckPassSchemaWithContent()` dùng processRewardForSchema pattern. Thêm: `findRewardPair()`, `splitStatistic()`, `upsertPrimaryReward()`, `upsertOverflowReward()`. Thêm BPU/BPC check vào milestone functions. | **CAO** |
| `internal/service/content.go` — `UpdateCashStatistic` | Thêm `Waiting` vào cash statistic mapping | Thấp |

### 6.4. Backend — Tests (files mới)

| File | Mô tả |
|------|-------|
| `internal/service/budget_split_test.go` | Tests cho `splitStatistic()`, `CombineBudgetEstimates()` |
| `internal/service/budget_change_status_test.go` | Tests cho `computeMaxCashForContent()`, add-back mechanism, idempotency |

### 6.5. Backend — Handler & Router

| File | Thay đổi |
|------|----------|
| `pkg/admin/handler/event_budget.go` | **Mới** — `UpdateBudget` handler |
| `pkg/admin/router/event.go` | Thêm route `PUT /:id/budget` |
| `pkg/admin/router/routevalidation/event_budget.go` | **Mới** — Validation middleware |

### 6.6. Frontend — Admin

| File | Thay đổi |
|------|----------|
| `admin/src/pages/event/detail/components/tabs/budget/index.tsx` | Thêm form config Bpu/Bpc (phía trên table budget-campaigns hiện tại) |
| `admin/src/configs/api.ts` | Thêm endpoint `updateBudget` |
| `admin/src/services/budget.ts` hoặc `event.ts` | Thêm API call |

---

## 7. Risk Matrix

### 7.1. Rủi ro CAO

| # | Rủi ro | Tác động | Giải pháp |
|---|--------|----------|-----------|
| R1 | **Viết lại reward creation flow** — `UpdateRewardTypeByStatisticContent` và `CheckPassSchemaWithContent` phải viết lại hoàn toàn để support primary/overflow pattern | Sai logic → reward sai, thống kê sai, tiền sai | Port chính xác từ Ambassador. Unit test cover tất cả cases trước khi viết code. Test trên staging với event thật. |
| R2 | **Race condition trong reward creation** — Hiện tại không có distributed lock. Thêm `WithBudgetLock` phải wrap đúng scope | Lock quá hẹp → race vẫn xảy ra. Lock quá rộng → deadlock | Lock bao quanh: findPair → computeMax → upsert → updateStats. Expire 2 phút. |
| R3 | **Aggregation pipeline đếm trùng overflow** — `GetTotalCashRewardByEvent` và `GetTotalCashRewardByContent` sẽ đếm `totalReward` trùng nếu không filter | Thống kê số lượng reward hiển thị sai (x2) | Thêm `"isBudgetExceeded": bson.M{"$ne": true}` vào `$match` của 2 pipelines này |
| R4 | **`UpdateCashStatistic` thiếu Waiting status** — Aggregation pipeline chỉ track Pending/Completed/Rejected, không có Waiting | BPC tính sai available cash → cho phép chi vượt giới hạn | Sửa pipeline + mapping trước khi implement BPC logic |

### 7.2. Rủi ro TRUNG BÌNH

| # | Rủi ro | Tác động | Giải pháp |
|---|--------|----------|-----------|
| R5 | **Recheck flow khi content đổi status** — Approve→Reject→Approve phải recalculate split + handle overflow | Reward orphan hoặc mất data | Port `processRewardForSchema` pattern (luôn tìm pair, luôn recalculate) |
| R6 | **Performance impact** — Mỗi reward creation thêm 2 DB reads + Redis lock | Crawl chậm hơn khi event có nhiều user/content đồng thời | Acceptable trade-off. Ambassador đã chạy production OK. |
| R7 | **Milestone + BPU/BPC** — Milestone rewards không nên split nhưng vẫn cần check budget | Milestone bị split → UX lạ | Milestone chỉ block/allow, không gọi `splitStatistic` |

### 7.3. Rủi ro THẤP

| # | Rủi ro | Tác động | Giải pháp |
|---|--------|----------|-----------|
| R8 | **Backward compatibility** — Events/Rewards cũ thiếu field mới | Crash hoặc behavior sai | Go zero-value: `float64=0` (unlimited), `bool=false` (not exceeded). An toàn. |
| R9 | **Admin UI confusion** — 2 khu vực budget config (Bpu/Bpc form + budget-campaigns table) | Admin nhầm lẫn | UI clear separation: "Cài đặt ngân sách" section ở trên, "Cảnh báo ngân sách" table ở dưới |

---

## 8. Implementation Phases

### Phase 0: Prerequisites (~0.5 ngày)

**Mục tiêu:** Chuẩn bị nền tảng, không thay đổi behavior hiện tại.

| # | Task | File |
|---|------|------|
| 0.1 | Thêm `Bpu`, `Bpc` vào `EventRaw` | `model/mg/event.go` |
| 0.2 | Thêm `IsBudgetExceeded`, `RecheckInProgress` vào `EventRewardRaw` | `model/mg/event_reward.go` |
| 0.3 | Sửa `GetTotalCashRewardByEvent` — thêm filter overflow | `aggregate_pipeline/event_reward.go` |
| 0.4 | Sửa `GetTotalCashRewardByContent` — thêm filter overflow | `aggregate_pipeline/event_reward.go` |
| 0.5 | Sửa `UpdateCashStatistic` — thêm Waiting vào cash mapping | `service/content.go` |

**Verify:** Build pass, chạy test pass, behavior hiện tại không đổi.

### Phase 1: Budget Engine (~1.5 ngày)

**Mục tiêu:** Xây dựng toàn bộ budget calculation engine. Chưa integrate vào reward flow.

| # | Task | File |
|---|------|------|
| 1.1 | Implement `estimateBudgetByUser()` | `service/event.go` |
| 1.2 | Implement `estimateBudgetByContent()` | `service/event.go` |
| 1.3 | Implement `CombineBudgetEstimates()` | `service/event.go` |
| 1.4 | Implement `computeMaxCashForContent()` | `service/event.go` |
| 1.5 | Implement `WithBudgetLock()` | `service/event.go` |
| 1.6 | Implement `splitStatistic()` | `service/event_schema.go` |
| 1.7 | Implement `findRewardPair()` | `service/event_schema.go` |
| 1.8 | Implement `upsertPrimaryReward()` | `service/event_schema.go` |
| 1.9 | Implement `upsertOverflowReward()` | `service/event_schema.go` |
| 1.10 | Port `budget_split_test.go` | `service/budget_split_test.go` |
| 1.11 | Port `budget_change_status_test.go` | `service/budget_change_status_test.go` |

**Verify:** Tất cả unit tests pass.

### Phase 2: Reward Flow Refactor (~2 ngày) ⚠️ HIGHEST RISK

**Mục tiêu:** Integrate budget engine vào reward creation flow.

| # | Task | File |
|---|------|------|
| 2.1 | Viết lại `UpdateRewardTypeByStatisticContent()` — dùng `WithBudgetLock` + `findRewardPair` + `computeMaxCashForContent` + `splitStatistic` | `service/event_schema.go` |
| 2.2 | Viết lại `CheckPassSchemaWithContent()` — tương tự | `service/event_schema.go` |
| 2.3 | Thêm BPU/BPC check vào `CheckPassSchemaByContentMilestone()` — block/allow only | `service/event_schema.go` |
| 2.4 | Thêm BPU/BPC check vào `CheckPassSchemaTypeByViewMilestoneWithListSchema()` — block/allow only | `service/event_schema.go` |
| 2.5 | Implement `UpdateBudgetStatistic()` — call sau mỗi reward upsert | `service/event.go` |
| 2.6 | Update `RecheckSchemaWithContentWhenChangeStatus()` — handle overflow cleanup | `service/event_schema.go` |

**Verify:** Integration test với event có Bpu/Bpc. Test approve→reject→approve cycle. Test race condition.

### Phase 3: Admin API + UI (~1 ngày)

**Mục tiêu:** Admin có thể config Bpu/Bpc qua UI.

| # | Task | File |
|---|------|------|
| 3.1 | Implement `UpdateBudget` handler | `pkg/admin/handler/event_budget.go` |
| 3.2 | Implement validation middleware | `pkg/admin/router/routevalidation/event_budget.go` |
| 3.3 | Thêm route `PUT /:id/budget` | `pkg/admin/router/event.go` |
| 3.4 | Update admin budget tab — thêm Bpu/Bpc form | `admin/src/pages/event/detail/components/tabs/budget/index.tsx` |
| 3.5 | Thêm API endpoint config | `admin/src/configs/api.ts` |
| 3.6 | Thêm API service call | `admin/src/services/budget.ts` |

**Verify:** Admin có thể set/update Bpu/Bpc. Giá trị lưu đúng vào DB. Budget-campaigns table không bị ảnh hưởng.

---

## 9. Test Strategy

### 9.1. Unit Tests (bắt buộc)

| Test | Mô tả |
|------|-------|
| `TestSplitStatistic_ViewOnly` | Split chỉ có views |
| `TestSplitStatistic_ViewLikeComment` | Split đa metrics, đúng priority order |
| `TestSplitStatistic_NonEvenMaxCash` | Budget không chia hết cho rate |
| `TestSplitStatistic_ZeroMaxCash` | Budget = 0, tất cả vào overflow |
| `TestSplitStatistic_FloorDivision` | Đảm bảo floor, không ceiling (999/200 = 4) |
| `TestCombineBudgetEstimates_AllEnough` | 3 levels đều đủ |
| `TestCombineBudgetEstimates_UserBottleneck` | User budget là bottleneck |
| `TestCombineBudgetEstimates_ContentBottleneck` | Content budget là bottleneck |
| `TestCombineBudgetEstimates_AllUnlimited` | Tất cả = 0 → unlimited |
| `TestComputeMaxCash_AddsBackCurrentPrimary` | Add-back mechanism hoạt động đúng |
| `TestNewFlow_ApproveRejectApprove` | Idempotent recalculation |

### 9.2. Integration Tests (staging)

| Test | Mô tả |
|------|-------|
| Event không có Bpu/Bpc | Behavior y hệt hiện tại (backward compat) |
| Event có Bpu=500k | User nhận max 500k, reward split khi gần limit |
| Event có Bpc=200k | Mỗi bài nhận max 200k |
| Event có cả Budget + Bpu + Bpc | Min(3 levels) hoạt động đúng |
| Content approve → reject → approve | Overflow cleanup + recalculate đúng |
| 2 goroutine crawl cùng event | Không race condition, budget không bị overspend |
| Budget-campaigns vẫn gửi email | Logic cũ không bị ảnh hưởng |

### 9.3. Regression Tests

| Test | Mô tả |
|------|-------|
| Tạo reward khi event không có budget | Vẫn tạo bình thường (unlimited) |
| Threshold 75%/95%/100% | Vẫn block submit/reward đúng |
| Budget-campaigns CRUD | Create/Update/ChangeStatus vẫn hoạt động |
| Admin event detail | Hiển thị statistic đúng, không đếm trùng overflow |

---

## 10. Rollback Plan

Nếu phát hiện bug nghiêm trọng sau deploy:

1. **Set `Bpu=0`, `Bpc=0`** cho tất cả events → behavior quay về unlimited (vô hiệu hóa BPU/BPC)
2. **Xóa overflow rewards** (`db.event_rewards.deleteMany({isBudgetExceeded: true})`) nếu cần
3. **Recalculate statistics** cho các events bị ảnh hưởng

Code mới không break code cũ vì:
- Hàm `EstimateBudgetByEvent()` cũ vẫn giữ nguyên
- Bpu/Bpc = 0 → skip check (unlimited)
- Overflow rewards có cash=0 → không ảnh hưởng cash sums

---

## 11. Monitoring

Sau deploy, theo dõi:

| Metric | Cách kiểm tra | Alert nếu |
|--------|---------------|-----------|
| Overspend | `db.events.find({bpu: {$gt: 0}})` → check user cash > bpu | User cash vượt Bpu |
| Orphan overflow | `db.event_rewards.find({isBudgetExceeded: true, cash: {$gt: 0}})` | Overflow có cash > 0 (bug) |
| Lock timeout | Log `"budget lock failed"` | > 10 lần/giờ |
| Reward creation latency | So sánh trước/sau deploy | Tăng > 200% |
