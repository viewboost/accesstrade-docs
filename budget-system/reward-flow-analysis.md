# Luồng tính thưởng Ambassador Platform — Phân tích từ Code

> Tài liệu phân tích chi tiết reward lifecycle, dựa trên codebase `accesstrade-projects/ambassabor/backend/`
>
> Ngày tạo: 2026-03-23

---

## 1. Tổng quan Flow

```
┌─────────────┐    ┌──────────────┐    ┌───────────────┐    ┌──────────────┐    ┌───────────┐
│  Creator     │    │  Hệ thống    │    │  Hệ thống     │    │  Admin       │    │  Creator  │
│  đăng bài    │───▶│  cào metrics │───▶│  tính reward   │───▶│  đối soát    │───▶│  nhận tiền│
│  (Content)   │    │  (Crawl)     │    │  (EventReward) │    │  (Reconcile) │    │  (Balance)│
└─────────────┘    └──────────────┘    └───────────────┘    └──────────────┘    └───────────┘
     Bước 1             Bước 2              Bước 3               Bước 4            Bước 5
```

---

## 2. Chi tiết từng bước

### Bước 1: Creator đăng Content

**File:** `pkg/public/service/content.go` → `Create()` (line 42)

```
Creator submit URL (TikTok, YouTube, Facebook...)
  │
  ├── Validate: Event đang active, trong date range
  ├── Validate: Content.Source khớp Event.Options.ApplyForSources
  ├── Auto-join user vào event (Eligibility().JoinEvent())
  ├── Crawl metadata: title, cover, duration, view/like/comment ban đầu
  │
  └── Insert ContentRaw
        Status: StatusWaitingApproved
        Event: event.ID
        Source: "tiktok" / "youtube" / ...
```

**Output:** `ContentRaw` record — chờ admin duyệt content

---

### Bước 2: Cào Metrics hàng ngày (Crawl)

**File:** `internal/service/content_flow.go` → `CreateFlow()` (line 35)
**File:** `internal/service/content_analytic_daily.go` → `Update()` (line 371)

```
ContentFlow chạy định kỳ (hàng ngày hoặc theo schedule)
  │
  ├── Crawl lại video: lấy view/like/comment mới nhất
  ├── Tạo/Update ContentAnalyticDailyRaw cho ngày hôm nay:
  │     view.value, like.value, comment.value
  │     begin (số đầu ngày), end (số cuối ngày)
  │
  └── GỌI: EventSchema().UpdateRewardTypeByStatisticContent()    ◄── TRIGGER tính reward
           (line 502 trong content_analytic_daily.go)
```

**Output:** `ContentAnalyticDailyRaw` — lịch sử metrics từng ngày

**Quan trọng:** Mỗi lần crawl → trigger tính lại reward → cash có thể THAY ĐỔI

---

### Bước 3: Tính Reward (Core Logic)

**File:** `internal/service/event_schema.go` → `UpdateRewardTypeByStatisticContent()` (line 184)

#### 3.1 Reward theo View/Like/Comment (EventSchemaTypeByStatistic)

```
Tìm tất cả EventSchema active cho event + source
  │
  Cho mỗi Schema:
  │
  ├── Tính metrics MỚI (delta từ lần cuối):
  │     newViews = current_views - last_recorded_views
  │     newLikes = current_likes - last_recorded_likes
  │     newComments = current_comments - last_recorded_comments
  │
  ├── Tính Cash:
  │     cashView    = newViews × schema.CashPerView
  │     cashLike    = newLikes × schema.CashPerLike
  │     cashComment = newComments × schema.CashPerComment
  │     totalCash   = cashView + cashLike + cashComment
  │
  ├── Xử lý Extended Period:
  │     Nếu event hết hạn nhưng ExtendedPeriod enabled:
  │       → IsExtended = true
  │       → Cash = 0 (không trả tiền cho extended period)
  │
  ├── Xác định Status:
  │     Content.Status = WaitingApproved → Reward.Status = WaitingApproved
  │     Content.Status = Approved        → Reward.Status = Pending
  │     Content.Status = Rejected        → Reward.Status = Rejected
  │
  └── INSERT hoặc UPDATE EventRewardRaw
        (Nếu đã có reward cho user+schema+content+date → UPDATE cash)
        (Nếu chưa có → INSERT mới)
```

**Key insight:** Reward cho 1 video KHÔNG chỉ tạo 1 lần — nó được **UPDATE liên tục** mỗi khi metrics thay đổi. Cash tăng dần theo view.

#### 3.2 Reward Milestone (Content Milestone / View Milestone)

**File:** `internal/service/event_schema.go` → `CheckPassSchemaByContentMilestone()` (line 372)

```
Milestone có 2 loại:

A. Content Milestone:
   "Đăng đủ N bài approved, mỗi bài ≥ X views → thưởng Y VND"
   │
   ├── Đếm content approved của user trong event
   ├── Check: count ≥ schema.Milestone.NumberOfContent?
   ├── Check: mỗi content có ≥ MinimumOfView?
   └── Nếu đủ điều kiện + chưa claim:
         → Tạo EventRewardRaw
           Cash = schema.CashReward.CashMilestone (SỐ TIỀN CỐ ĐỊNH)
           Status = StatusPending
         → Giảm schema.Quantity.Remaining

B. View Milestone:
   "Đạt tổng N views across all content → thưởng Y VND"
   │
   ├── Tổng views của user across all content trong event
   ├── Check: totalViews ≥ schema.Milestone.NumberOfView?
   └── Nếu đủ + chưa claim → tạo reward tương tự
```

**Key insight:** Milestone reward = cash CỐ ĐỊNH, chỉ tạo 1 LẦN. Khác hoàn toàn với Statistic reward (tăng dần).

#### 3.3 Bonus (Admin tạo thủ công)

**File:** `pkg/admin/service/event_bonus.go`

```
Admin tạo Bonus cho creator:
  │
  └── Insert EventBonusRaw
        Amount: số tiền cố định
        Status: StatusApproved
        Reason: lý do thưởng
        User, Event, Partner
```

**Key insight:** Bonus hoàn toàn thủ công, không liên quan đến view/metrics.

---

### Bước 4: Đối soát (Reconciliation)

#### 4.1 Phase Processing — Thu thập items

**File:** `pkg/admin/service/reconciliation_processing.go`

```
Admin tạo đối soát → Processing() chạy:
  │
  ├── ProcessingContent() (line 160):
  │     Aggregate tất cả EventReward pending cho event
  │     → Group by content → tạo ReconciliationItem (type=Content)
  │     → Item.Cash = tổng reward cash cho content đó
  │
  ├── ProcessingMilestone() (line 67):
  │     Tìm EventReward pending loại milestone
  │     → Tạo ReconciliationItem (type=Milestone)
  │     → Item.Cash = milestone cash
  │
  └── ProcessingBonus() (line 238):
        Tìm EventBonus approved chưa reconcile
        → Tạo ReconciliationItem (type=Bonus)
        → Item.Cash = bonus amount
```

**Output:** Danh sách `ReconciliationItemRaw` — admin review từng item

#### 4.2 Phase Running — Duyệt & tạo CashFlow

**File:** `pkg/admin/service/reconciliation_running.go` → `Running()` (line 33)

```
Admin nhấn "Duyệt" → Running() chạy:
  │
  ├── Dùng ants pool (50 goroutines) để process song song theo USER
  │
  └── Cho mỗi user → runCashBack() (line 235):
        │
        ├── Item type = Milestone:
        │     Verify reward.Status = Pending, cash đúng
        │     → Update EventReward → StatusCompleted
        │     → Tạo CashFlowPayload
        │
        ├── Item type = Content:
        │     Verify content.Status = Approved
        │     Recheck cash amount
        │     → Update TẤT CẢ EventReward matching → StatusCompleted
        │     → Update ContentAnalyticDaily → StatusCompleted
        │     → Tạo CashFlowPayload
        │
        └── Item type = Bonus:
              → Update EventBonus → StatusCompleted
              → Tạo CashFlowPayload

        Sau khi xử lý tất cả items:
        → Gọi CashFlow().AddCashFlow() cho tất cả payloads
        → Gọi SendCommissionToReferrer() (hoa hồng giới thiệu)
        → Push notification cho creator
```

**CRITICAL:** Hiện tại Running() **KHÔNG check budget**. Tất cả items đều auto-complete.

---

### Bước 5: Creator nhận tiền (CashFlow)

**File:** `internal/service/cashflow.go` → `AddCashFlow()` (line 58)

```
Cho mỗi CashFlowPayload:
  │
  ├── Lấy balance hiện tại của user
  ├── newBalance = oldBalance + payload.Value
  │
  └── Insert CashFlowRaw:
        OldBalance: balance trước
        NewBalance: balance sau
        Value: số tiền thêm
        Action: loại (reward statistic / milestone / bonus)
        Category: "event"
        TargetID: reward/bonus/content ID
```

**Output:** Tiền vào balance creator → creator có thể rút

---

## 3. Data Model (Các struct chính)

### EventRewardRaw
```go
type EventRewardRaw struct {
    ID        primitive.ObjectID
    User      primitive.ObjectID    // Creator
    Partner   primitive.ObjectID    // Đối tác
    Event     primitive.ObjectID    // Chiến dịch
    Type      string               // "by_statistic" | "by_content_milestone" | "by_view_milestone"
    Status    string               // waiting_approved → pending → completed / rejected
    Cash      float64              // Số tiền (THAY ĐỔI cho statistic, CỐ ĐỊNH cho milestone)
    Date      string               // Ngày tính (YYYY-MM-DD)
    Schema    EventSchemaInfo       // Thông tin schema (cash rates)
    Statistic EventRewardStatistic  // Chi tiết: TotalView, TotalLike, TotalComment, TotalCash*
    IsExtended bool                // Extended period?
    CreatedAt  time.Time
}
```

### EventSchemaCashReward
```go
type EventSchemaCashReward struct {
    CashPerLike    float64  // VND / like
    CashPerComment float64  // VND / comment
    CashPerView    float64  // VND / view
    CashPerShare   float64  // VND / share
    CashMilestone  float64  // VND cho milestone (cố định)
}
```

### BudgetInfo (hiện tại)
```go
type BudgetInfo struct {
    Total       float64  // Tổng budget event
    Used        float64  // Đã chi (nhưng KHÔNG được enforce)
    Remain      float64  // Còn lại
    UsedPercent float64  // % đã dùng
}
```

### EventBonusRaw
```go
type EventBonusRaw struct {
    ID      primitive.ObjectID
    Event   primitive.ObjectID
    User    primitive.ObjectID
    Partner primitive.ObjectID
    Amount  float64              // Số tiền bonus (cố định)
    Status  string               // approved → completed
    Reason  string               // Lý do thưởng
}
```

---

## 4. So sánh 3 loại thưởng

| Đặc điểm | Statistic (CPV/CPL/CPC) | Milestone | Bonus |
|-----------|-------------------------|-----------|-------|
| **Trigger** | Tự động khi metrics thay đổi | Tự động khi đạt ngưỡng | Admin tạo thủ công |
| **Cash** | **Thay đổi liên tục** (tăng theo view) | Cố định 1 lần | Cố định 1 lần |
| **Số lần tạo** | 1 record / video / schema / ngày, UPDATE liên tục | 1 record / milestone / user | 1 record / lần admin tạo |
| **Bị budget cap?** | Cần cap (event, user, video) | Cần cap (event, user) | **KHÔNG** — tách riêng |
| **Extended Period** | Cash = 0 | N/A | N/A |
| **Quan hệ với video** | 1 video → N rewards (1 per schema per day) | Không gắn 1 video cụ thể | Không gắn video |

---

## 5. Lifecycle Diagram

### 5.1 Flow hiện tại (KHÔNG có budget check)

```
    Content         Crawl              Reward                Reconciliation        Cash
    ─────────       ──────             ──────                ──────────────        ────

    Creator         Hệ thống           Hệ thống              Admin                Creator
    submit URL      cào view/like       tính tiền             duyệt                nhận tiền
       │               │                  │                     │                    │
       ▼               ▼                  ▼                     ▼                    ▼
    ┌──────┐      ┌──────────┐      ┌───────────┐       ┌────────────┐       ┌──────────┐
    │Create│      │Crawl     │      │Calculate  │       │Processing  │       │AddCash   │
    │Content│──▶  │Metrics   │──▶   │Reward     │──▶    │Items       │──▶    │Flow      │
    │      │      │Daily     │      │Cash       │       │            │       │          │
    └──────┘      └──────────┘      └───────────┘       └────────────┘       └──────────┘
                  Lặp hàng ngày     Cash THAY ĐỔI        Running              Tiền vào
                                    KHÔNG GIỚI HẠN        Auto-complete        balance
                                                          KHÔNG check budget
```

### 5.2 Flow mới (TCB-style budget enforcement)

```
    Content         Crawl              Reward + Budget Check       Reconciliation     Cash
    ─────────       ──────             ─────────────────────       ──────────────     ────

    Creator         Hệ thống           Hệ thống                    Admin              Creator
    submit URL      cào view/like       tính tiền + CHECK BUDGET    duyệt              nhận tiền
       │               │                  │                          │                   │
       ▼               ▼                  ▼                          ▼                   ▼
    ┌──────┐      ┌──────────┐      ┌─────────────────────┐   ┌────────────┐     ┌──────────┐
    │Create│      │Crawl     │      │ Calculate raw cash   │   │Processing  │     │AddCash   │
    │Content│──▶  │Metrics   │──▶   │         │            │   │Items       │──▶  │Flow      │
    │      │      │Daily     │      │         ▼            │   │            │     │          │
    └──────┘      └──────────┘      │ ┌─────────────────┐  │   └────────────┘     └──────────┘
                  Lặp hàng ngày     │ │ Video Cap check  │  │     Running
                                    │ │ min(cash,vidCap) │  │     KHÔNG cần
                                    │ └────────┬────────┘  │     check budget
                                    │          ▼           │     (đã enforce
                                    │ ┌─────────────────┐  │      ở reward)
                                    │ │ User Cap check   │  │
                                    │ │ delta vs remain  │  │
                                    │ └────────┬────────┘  │
                                    │          ▼           │
                                    │ ┌─────────────────┐  │
                                    │ │ Event Budget     │  │
                                    │ │ delta vs avail   │  │
                                    │ │ (giống TCB)      │  │
                                    │ └────────┬────────┘  │
                                    │          ▼           │
                                    │   OK → Update cash   │
                                    │   HẾT → CHẶN update  │
                                    │   + overbudgetCash    │
                                    └─────────────────────┘
```

---

## 6. Điểm KHÔNG có Budget Check (Gaps hiện tại)

| # | Điểm trong flow | File | Hiện tại | Cần thêm |
|---|-----------------|------|----------|----------|
| 1 | Tạo/Update Reward | `event_schema.go:184` | Tính cash không giới hạn | Check 3 tầng: Video Cap → User Cap → Event Budget (delta-based, giống TCB) |
| 2 | Update Event Budget | `event.go:289` | Reset Used=0 khi sửa | Giữ lại Used, chỉ update Total |
| 3 | Public API | `response/event.go:62` | Expose BudgetInfo nguyên xi | Chỉ expose user cap + progress |
| 4 | ChangeStatusItem | `reconciliation.go` | Approve/reject thủ công | Check budget khi approve (nếu admin approve thủ công) |

**Lưu ý:** Với TCB-style enforcement tại reward creation/update, Reconciliation **KHÔNG cần** check budget (giống TCB) — vì budget đã được reserve khi tạo/update reward.

---

## 7. Tóm tắt cho Budget System Design

### Quyết định: TCB-style Delta-based Budget Check cho cả 3 tầng

Dựa trên phân tích, Ambassador sẽ áp dụng **cùng approach với TCB** — chặn thẳng tại thời điểm tạo/update reward, check budget bằng delta (phần cash tăng thêm).

### Đặc điểm hệ thống:

1. **Reward cash THAY ĐỔI liên tục** — giống TCB, xử lý bằng delta check mỗi lần update
2. **1 video có thể có nhiều reward records** (1 per schema per day) — video cap cần tổng hợp
3. **Milestone reward cash CỐ ĐỊNH** — check budget cho toàn bộ cash khi tạo (giống TCB)
4. **Bonus TÁCH RIÊNG** — không bị budget cap, không tính vào cashValid
5. **Budget enforce tại reward creation/update** — giống TCB, KHÔNG cần check lại tại Reconciliation
6. **Extended Period**: cash = 0, không ảnh hưởng budget
7. **Content approval flow**: reward chỉ Pending khi content Approved

### So sánh approach cũ vs mới:

| Tiêu chí | Hybrid (approach cũ) | TCB-style delta check (approach mới) |
|----------|---------------------|--------------------------------------|
| Enforcement | Tại đối soát (hard) + reward (soft) | Tại reward creation/update (hard) |
| Reward inflation | CÓ — pending có thể >> budget | KHÔNG — chặn ngay khi vượt |
| Admin overwhelm | CÓ — phải reject hàng loạt | KHÔNG — không có reward vượt budget |
| Complexity | 2 điểm check, rewrite Running | 1 điểm check, giống TCB code |
| Race condition ở Running | CÓ (50 goroutines) | KHÔNG CÒN — budget đã enforce trước đó |
| Data performance thực tế | Đầy đủ (reward vẫn tạo) | Có `overbudgetCash` tracking phần vượt |

---

## 9. TCB Budget Enforcement — Cách Techcombank chặn reward khi hết budget

> Phân tích từ `accesstrade-projects/techcombank/backend/`

### 9.1 Mô hình: Reservation-based (Reserve ngay khi tạo reward)

```
cashValid = TotalCashPending + TotalCashCompleted + TotalCashWaiting
                 ↑                    ↑                    ↑
           Reward vừa tạo     Đã duyệt xong        Chờ duyệt content

availableBudget = Event.Budget - cashValid
```

**Nguyên tắc:** Reward ở status `pending`, `completed`, `waiting_approved` → ĐỀU tính vào budget. Chỉ `rejected` mới trả lại budget.

### 9.2 Flow chặn reward

```
View tăng → Tính cash = views × CashPerView + likes × CashPerLike + ...
  │
  ├── Check 1: event.IsBlockReward == true?
  │     YES → CHẶN ngay, không tạo reward
  │     NO  → tiếp
  │
  ├── Check 2: EstimateBudgetByEvent()
  │     cashValid = Pending + Completed + Waiting
  │     availableCash = Budget - cashValid
  │     availableCash < newRewardCash?
  │       YES → CHẶN + set IsBlockReward=true + alert
  │       NO  → tiếp
  │
  └── Insert EventRewardRaw (Status: Pending)
        → cashValid tự tăng → budget giảm ngay
```

**File:** `internal/service/event.go` → `EstimateBudgetByEvent()` (line 88)
**File:** `internal/service/event_schema.go` → `UpdateRewardTypeByStatisticContent()` (line 293)

### 9.3 Hệ thống ngưỡng cảnh báo (Threshold)

| Ngưỡng | Hành động | Block gì? |
|--------|-----------|-----------|
| **75%** | Gửi email + notification cho admin | Không block |
| **95%** | Gửi alert + set `IsBlockSubmitContent = true` | Block **đăng content mới** |
| **100%** | Set `IsBlockReward = true` + `IsBlockSubmitContent = true` + Telegram alert | Block **tất cả** (content + reward) |

**File:** `internal/service/event.go` → `UpdateEventStatistic()` (line 207)

### 9.4 Budget Recalculation

```
Khi nào recalculate?
  → Sau mỗi thay đổi content status (approve/reject)
  → Sau mỗi reconciliation complete
  → UpdateEventStatistic() aggregate lại từ event_reward collection

Pipeline: Aggregate tất cả EventReward → group by status → sum cash → update event.Statistic
```

**File:** `internal/module/database/mongodb/aggregate_pipeline/user_event.go` → `GetEventAnalyticCash()`

### 9.5 Reconciliation — KHÔNG check budget

TCB **KHÔNG** check budget tại đối soát vì:
- Budget đã được reserve khi tạo reward (pending đã trừ)
- Reconciliation chỉ chuyển status: `completed → transferred`
- Không thêm tiền mới → không cần check lại

### 9.6 Chi tiết: TCB check budget bằng DELTA khi update reward

**Phát hiện quan trọng:** TCB reward cash cũng THAY ĐỔI hàng ngày, giống Ambassador. TCB xử lý bằng cách check budget cho phần **delta** (cash tăng thêm) mỗi lần update.

**File:** `internal/service/event_schema.go` (line 316-341)

```go
// Khi reward ĐÃ TỒN TẠI → tính delta
totalCashOld := rewardCheck.Statistic.TotalCashLike + TotalCashComment + TotalCashView
totalCashNew := reward.Statistic.TotalCashLike + TotalCashComment + TotalCashView
totalCash := totalCashNew - totalCashOld    // DELTA = phần tăng thêm

if totalCash > 0 {
    // Check budget CHỈ cho phần delta
    isExcceedBudget := Event().EstimateBudgetByEvent(ctx, event, EstimateBudgetTracking{
        TotalCashPending: totalCash,    // ← delta, KHÔNG phải toàn bộ cash
    })
    if isExcceedBudget {
        // CHẶN update — cash giữ nguyên giá trị cũ
        content.IsLastReward = true
        return errors.New(locale.EventKeyBlockReward)
    }
}
// OK → Update reward với cash mới
UpdateOne(..., { "cash": reward.Cash, "statistic": reward.Statistic })
```

**Flow thực tế:**
```
Ngày 1: Tạo reward, cash = 100k → cashValid += 100k (reserve 100k)
Ngày 2: View tăng → cash mới = 300k → delta = 200k
         → Check budget cho 200k → OK → Update cash = 300k (cashValid += 200k)
Ngày 3: View tăng → cash mới = 800k → delta = 500k
         → Check budget cho 500k → HẾT → CHẶN, cash giữ = 300k
         → content.IsLastReward = true (đánh dấu không tính nữa)
```

**Kết quả:** Budget luôn chính xác vì mỗi lần cash tăng đều check và reserve delta.

### 9.7 Điểm khác biệt TCB vs Ambassador

| Đặc điểm | TCB | Ambassador |
|-----------|-----|-----------|
| **Reward cash** | Thay đổi hàng ngày (giống nhau) | Thay đổi hàng ngày (giống nhau) |
| **Budget check khi update** | CÓ — check delta mỗi lần cash tăng | KHÔNG — chưa implement |
| **Reserve budget** | CÓ — cashValid = Pending + Completed + Waiting | KHÔNG |
| **Khi hết budget** | Chặn update cash (giữ giá trị cũ) + set IsBlockReward | Không chặn |
| **Reconciliation check** | KHÔNG (đã enforce ở reward creation/update) | KHÔNG (chưa implement) |
| **Block flags** | `IsBlockReward`, `IsBlockSubmitContent` | Chưa có |
| **Threshold alerts** | 75%, 95%, 100% | Chưa có |
| **Admin duyệt từng item** | KHÔNG (batch auto-complete) | CÓ (`ChangeStatusItem`) |

### 9.8 Áp dụng TCB-style cho Ambassador

**KHẢ THI** — approach delta-based budget check hoàn toàn áp dụng được:

```
Ambassador UpdateRewardTypeByStatisticContent():
  │
  ├── Reward MỚI (chưa tồn tại):
  │     totalCash = views × CashPerView + ...
  │     → Check budget cho totalCash
  │     → OK → InsertOne (cashValid += totalCash)
  │     → HẾT → CHẶN, không tạo reward
  │
  └── Reward ĐÃ TỒN TẠI (update cash):
        totalCashOld = reward hiện tại
        totalCashNew = tính lại từ metrics mới
        delta = totalCashNew - totalCashOld
        → delta > 0? → Check budget cho delta
        → OK → UpdateOne cash = totalCashNew (cashValid += delta)
        → HẾT → CHẶN update, cash giữ giá trị cũ
```

**Khác biệt duy nhất cần xử lý thêm cho Ambassador:**
- Ambassador có `ChangeStatusItem` (admin duyệt từng item) → cần check budget ở đây nữa
- Ambassador cần thêm Video Cap + User Cap (TCB chỉ có Event Budget)

---

## 10. Phân tích khả năng chặn thẳng theo từng tầng (TCB-style delta check)

> Dựa trên phát hiện: TCB dùng **delta-based budget check** — check phần cash tăng thêm mỗi lần update, không phải check toàn bộ.

### 10.1 Tầng Video Cap — ✅ Chặn thẳng (Rất phù hợp)

```
UpdateRewardTypeByStatisticContent():
  calculated = views × CashPerView + likes × CashPerLike + ...
  cash = min(calculated, videoCap)
  overbudgetCash = calculated - cash    ← tracking phần vượt
```

| Tiêu chí | Đánh giá |
|----------|----------|
| Race condition? | KHÔNG — 1 video = 1 reward, update tuần tự |
| Cần reserve? | KHÔNG — chỉ cần cap lại khi tính |
| Cash thay đổi? | Có, nhưng luôn ≤ videoCap → an toàn |
| Complexity | RẤT THẤP — thêm 1 dòng `min()` |

### 10.2 Tầng User Cap — ✅ Chặn thẳng (TCB-style delta check)

Áp dụng cùng approach delta như TCB cho Event Budget, nhưng scope per-user:

```
UpdateRewardTypeByStatisticContent() cho Video X của User A:
  │
  ├── Tính cash mới cho video X (đã qua video cap)
  ├── delta = newCash - oldCash
  │
  ├── Check User Cap:
  │     userEarned = sum(tất cả reward cash của User A trong event)  ← query DB
  │     userRemain = userCap - userEarned
  │     delta > userRemain?
  │       YES → cash = oldCash + userRemain (cắt lại vừa đủ cap)
  │              overbudgetCash = delta - userRemain
  │       NO  → cash = newCash (bình thường)
  │
  └── Update reward
```

| Tiêu chí | Đánh giá |
|----------|----------|
| Race condition? | THẤP — crawl thường chạy tuần tự per content, ít khi 2 video cùng user update đồng thời |
| Cần reserve? | KHÔNG — check real-time sum mỗi lần update (giống TCB check cashValid) |
| Cash thay đổi? | CÓ — nhưng mỗi lần update đều check delta vs userRemain |
| Complexity | THẤP-TRUNG BÌNH — thêm 1 query sum + so sánh |

**So với Video Cap:** Phức tạp hơn vì cần query tổng reward của user, nhưng logic tương tự — check rồi cắt.

### 10.3 Tầng Event Budget — ✅ Chặn thẳng (Giống hệt TCB)

Áp dụng **y hệt** TCB `EstimateBudgetByEvent()`:

```
UpdateRewardTypeByStatisticContent() cho bất kỳ reward nào:
  │
  ├── Tính delta (sau khi đã qua video cap + user cap)
  │
  ├── Check Event Budget (giống TCB):
  │     cashValid = sum(Pending + Completed + Waiting) across ALL users
  │     availableCash = eventBudget - cashValid
  │     delta > availableCash?
  │       YES → CHẶN update + set IsBlockReward = true
  │       NO  → OK, update reward
  │
  └── Threshold alerts (75%, 95%, 100%)
```

| Tiêu chí | Đánh giá |
|----------|----------|
| Race condition? | CÓ THỂ — nhiều user crawl cùng lúc. Nhưng TCB cũng có vấn đề này và chấp nhận được |
| TCB-style khả thi? | **CÓ** — approach delta hoàn toàn giống, chỉ copy logic |
| Complexity | THẤP — gần như copy TCB `EstimateBudgetByEvent()` |

### 10.4 Thứ tự check 3 tầng khi update reward

```
UpdateRewardTypeByStatisticContent():
  │
  Step 1: Tính raw cash
  │  calculated = views × CashPerView + likes × CashPerLike + ...
  │
  Step 2: Video Cap (chặn đầu tiên, đơn giản nhất)
  │  cash = min(calculated, videoCap)
  │
  Step 3: User Cap (check tổng user)
  │  delta = cash - oldCash
  │  userRemain = userCap - sum(user rewards)
  │  Nếu delta > userRemain → cash = oldCash + userRemain
  │  Recalculate delta
  │
  Step 4: Event Budget (check tổng event — giống TCB)
  │  cashValid = sum(all Pending + Completed + Waiting)
  │  availableCash = eventBudget - cashValid
  │  Nếu delta > availableCash → CHẶN hoặc cắt lại
  │
  └── Update reward với cash cuối cùng + overbudgetCash
```

**Mỗi tầng cắt dần → tầng sau nhận delta đã giảm → budget luôn an toàn.**

### 10.5 Ví dụ end-to-end

```
Event Budget = 100tr, User Cap = 5tr, Video Cap = 2tr

Creator A đăng Video 1:
  Ngày 1: views = 1000 → calculated = 500k
    Step 2 (Video Cap): min(500k, 2tr) = 500k ✅
    Step 3 (User Cap): userEarned = 0, delta = 500k, remain = 5tr → OK ✅
    Step 4 (Event Budget): cashValid = 0, delta = 500k, avail = 100tr → OK ✅
    → cash = 500k, reserve 500k

  Ngày 5: views = 10000 → calculated = 5tr
    Step 2 (Video Cap): min(5tr, 2tr) = 2tr ✅ (video cap cắt)
    Step 3 (User Cap): userEarned = 500k, delta = 2tr - 500k = 1.5tr, remain = 4.5tr → OK ✅
    Step 4 (Event Budget): cashValid = 500k, delta = 1.5tr, avail = 99.5tr → OK ✅
    → cash = 2tr, overbudgetCash = 3tr (phần vượt video cap)

Creator A đăng Video 2:
  Ngày 6: views = 8000 → calculated = 4tr
    Step 2 (Video Cap): min(4tr, 2tr) = 2tr ✅ (video cap cắt)
    Step 3 (User Cap): userEarned = 2tr(V1), delta = 2tr, remain = 3tr → OK ✅
    Step 4 (Event Budget): cashValid = 2tr, delta = 2tr, avail = 98tr → OK ✅
    → cash = 2tr

Creator A đăng Video 3:
  Ngày 7: views = 5000 → calculated = 2.5tr
    Step 2 (Video Cap): min(2.5tr, 2tr) = 2tr ✅
    Step 3 (User Cap): userEarned = 4tr(V1+V2), delta = 2tr, remain = 1tr → VƯỢT!
    → cash = oldCash(0) + 1tr = 1tr (user cap cắt)
    → overbudgetCash = 1tr (phần vượt user cap)
    Step 4 (Event Budget): delta = 1tr, avail = 96tr → OK ✅
    → cash = 1tr

  Ngày 8: views tăng thêm → calculated tăng
    Step 3 (User Cap): userEarned = 5tr = userCap → remain = 0 → CHẶN
    → cash giữ = 1tr, không update nữa
```

### 10.6 Edge Cases đã giải quyết

| Edge Case | Cách xử lý |
|-----------|------------|
| Admin tăng budget/cap | Stateless — lần crawl tiếp tự check lại, remain tăng → tiếp tục |
| Admin giảm budget/cap | `new_total ≥ current_used` → không cho giảm dưới mức đã chi |
| Reward bị reject | cashValid giảm → remain tăng → reward khác có thể tiếp tục |
| Bonus | KHÔNG tính vào cashValid, không bị cap nào ảnh hưởng |
| Milestone reward | Check budget cho toàn bộ cash (cố định), giống TCB |
| Extended Period | Cash = 0 → delta = 0 → không ảnh hưởng budget |
| Content chưa approved | Reward status = WaitingApproved → vẫn tính vào cashValid (giống TCB) |
| Video crawl trước/sau | First come first served — video crawl trước được ưu tiên (giống TCB) |

---

## 11. Quyết định cuối cùng

### Phương án: TCB-style Delta-based Budget Check — Chặn thẳng tại reward creation/update

**Bỏ phương án Hybrid** (brainstorming trước đó). Lý do:
- TCB approach đã proven ở production
- Cùng codebase pattern, dễ maintain
- Không có reward inflation (pending >> budget)
- Admin không bị overwhelm khi đối soát
- `overbudgetCash` field giữ data performance thực tế (không mất insight)
- Reconciliation KHÔNG cần rewrite — giữ nguyên flow hiện tại

**Thay đổi so với TCB:**
- Thêm 2 tầng mới: Video Cap + User Cap (TCB chỉ có Event Budget)
- Thêm `overbudgetCash` tracking (TCB không có)
- Ambassador có `ChangeStatusItem` → cần check budget khi admin approve thủ công
- Bonus tách riêng khỏi cashValid

---

*Tài liệu được tạo: 2026-03-23*
*Cập nhật: 2026-03-23 — Xác nhận TCB-style enforcement cho cả 3 tầng*
*Dựa trên code analysis của `accesstrade-projects/ambassabor/backend/` và `accesstrade-projects/techcombank/backend/`*
