# Brainstorming Session: Phân tích chức năng bị tác động bởi Budget System

**Date:** 2026-03-22
**Objective:** Kiểm tra tất cả chức năng có thể bị tác động khi implement Budget System 3 tầng (Event → User → Video)
**Context:** Dựa trên brainstorming-budget-system-2026-03-16.md, cần phân tích impact lên codebase hiện tại
**Reference:** Codebase `accesstrade-projects/ambassabor/backend/`

## Techniques Used
1. Mind Mapping — Map toàn bộ chức năng bị tác động
2. Starbursting — Câu hỏi chi tiết Who/What/Where/When/Why/How cho từng chức năng
3. Reverse Brainstorming — Cách nào làm hệ thống thất bại → rút ra giải pháp

---

## Hiện trạng Code (As-Is) — Phát hiện quan trọng

### Cấu trúc Budget hiện tại
```
PartnerRaw.Bpp        → Budget per partner (float64, đơn giản)
EventRaw.Bpe          → BudgetInfo{Total, Used, Remain, UsedPercent}
EventRaw.Bpc          → Budget per content (float64, đơn giản)
EventSchemaRaw.MaximumRewardPerUser → int (ĐÃ CÓ nhưng chưa rõ enforcement)
```

### Phát hiện CRITICAL từ code
| # | Phát hiện | File | Mức độ |
|---|-----------|------|--------|
| 1 | **Update Event budget RESET Used=0, Remain=Total** — code comment out logic giữ lại used/remain | `pkg/admin/service/event.go:289-309` | 🔴 CRITICAL |
| 2 | **Public API expose BudgetInfo nguyên xi** cho user (total, used, remain) | `pkg/public/model/response/event.go:62-63` | 🟡 MEDIUM |
| 3 | **Reconciliation KHÔNG reference budget** — không check budget khi approve | `pkg/admin/service/reconciliation_running.go` | 🔴 CRITICAL |
| 4 | **Bpc (budget per content) chỉ là float64 đơn giản** — không có tracking used/remain | `model/mg/event.go:50` | 🟡 MEDIUM |
| 5 | **Event Schema service KHÔNG check budget** khi tính reward | `internal/service/event_schema.go` | 🔴 CRITICAL |
| 6 | **Partner.Bpp đã có validation** khi tạo/sửa event (tổng budget events ≤ Bpp) | `pkg/admin/service/event.go:192-199` | ✅ Đã có |

---

## Technique 1: Mind Mapping — Chức năng bị tác động

```
                    ┌───────────────────────────────────┐
                    │     BUDGET SYSTEM 3 TẦNG          │
                    │  Event → User Cap → Video Cap     │
                    └──────────────┬────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
   ┌────┴─────┐            ┌───────┴───────┐          ┌──────┴──────┐
   │ ADMIN    │            │ USER/CREATOR  │          │ HỆ THỐNG   │
   │ FACING   │            │ FACING        │          │ BACKEND    │
   └────┬─────┘            └───────┬───────┘          └──────┬──────┘
        │                          │                          │
   ┌────┼─────────┐          ┌─────┼──────┐            ┌─────┼──────┐
   │    │         │          │     │      │            │     │      │
   A1  A2        A3         U1    U2     U3           S1    S2     S3
```

### A. Admin Facing (5 chức năng)

#### A1. Setup Budget trong Event (`pkg/admin/service/event.go`)
- **Create Event**: Thêm fields UserCap, VideoCap vào request body
- **Update Event**: Logic giữ lại Used/Remain khi sửa budget (HIỆN ĐANG BỊ COMMENT OUT!)
- **Duplicate Event**: Reset budget tracking khi clone
- **Change Status**: Khi deactivate → có freeze budget không?
- **Validation**: `VideoCap ≤ UserCap ≤ Total`, `new_total ≥ current_used`

**Files bị tác động:**
| File | Thay đổi |
|------|----------|
| `internal/model/mg/event.go` | Mở rộng `BudgetInfo` struct (+UserCap, +VideoCap, +BonusUsed, +Exhausted) |
| `pkg/admin/model/request/event.go` | Thêm fields UserCap, VideoCap vào request |
| `pkg/admin/model/response/event.go` | Response thêm budget chi tiết |
| `pkg/admin/service/event.go` | Create/Update logic + validation |

#### A2. Admin theo dõi Budget (`pkg/admin/service/event.go`)
- **Event List**: Thêm budget status (còn/hết/gần hết)
- **Event Detail**: Hiển thị breakdown budget (total, used, bonus_used, remain, user_cap, video_cap)
- **Event Statistic**: Budget burn rate, forecast
- **Event Chart**: Budget consumption over time

**Files bị tác động:**
| File | Thay đổi |
|------|----------|
| `pkg/admin/model/response/event.go` | Response thêm budget breakdown |
| `internal/module/database/mongodb/aggregate_pipeline/event.go` | Pipeline thêm budget aggregation |
| `internal/model/mg/user_event_analytic_daily.go` | Thêm budget tracking daily |

#### A3. Admin quản lý Reward + Bonus
- **Approve/Reject Reward**: Check budget trước khi approve
- **Create Bonus**: Check bonus tracking riêng
- **Event Schema CRUD**: Validation `MaximumRewardPerUser` vs UserCap

**Files bị tác động:**
| File | Thay đổi |
|------|----------|
| `pkg/admin/service/event_reward.go` | Check budget khi change status |
| `pkg/admin/service/event_bonus.go` | Bonus tracking tách riêng |
| `pkg/admin/service/event_schema.go` | Validation MaximumRewardPerUser ↔ UserCap |

### U. User/Creator Facing (3 chức năng)

#### U1. User theo dõi Budget (Public API)
- **Event Detail Page**: Hiển thị user cap, video cap, tiến trình cá nhân
- **Event Listing**: Badge trạng thái (còn budget / hết budget / đã đạt cap)
- **CRITICAL**: Hiện tại API expose `Bpe` nguyên xi → user thấy TỔNG BUDGET EVENT!

**Files bị tác động:**
| File | Thay đổi |
|------|----------|
| `pkg/public/model/response/event.go` | **PHẢI THAY ĐỔI** — chỉ expose user cap + progress, KHÔNG expose tổng budget event |
| `pkg/public/service/event.go:348-352` | Logic map budget cho user response |
| (MỚI) `pkg/public/model/response/user_budget.go` | Response mới cho user budget tracking |

#### U2. User xem Earnings
- **Earnings Page**: Phân biệt Hoa hồng vs Bonus
- **Per-video breakdown**: Mỗi video đã kiếm bao nhiêu / còn bao nhiêu
- **Status badges**: 🟢 Còn, 🟡 Đã đạt cap, 🔴 Hết ngân sách

**Files bị tác động:**
| File | Thay đổi |
|------|----------|
| `pkg/public/service/event.go` | Endpoint mới hoặc mở rộng GetDetail |
| `internal/module/database/mongodb/aggregate_pipeline/user_event.go` | Pipeline tính earning per video |

#### U3. User đăng Content
- **Trước khi đăng**: Hiển thị cảnh báo nếu gần/hết budget
- **Sau khi đăng**: Bài vẫn được nhận, nhưng reward có thể bị chặn
- **Content flow không bị chặn** — chỉ reward bị ảnh hưởng

**Files bị tác động:**
| File | Thay đổi |
|------|----------|
| `pkg/public/service/content.go` | Thêm budget status check khi user xem event detail |
| Không chặn submit content, chỉ cảnh báo | — |

### S. Hệ thống Backend (4 chức năng)

#### S1. Reward Calculation (`internal/service/event_schema.go`)
- **CORE CHANGE**: Logic tính reward phải check 3 tầng
- `reward = min(calculated, remaining_event, remaining_user, remaining_video)`
- Atomic deduction bằng MongoDB `findOneAndUpdate`

**Files bị tác động:**
| File | Thay đổi |
|------|----------|
| `internal/service/event_schema.go:185` | `UpdateRewardTypeByStatisticContent` — thêm budget check |
| `internal/service/event.go:556` | `UpdateStatisticUserEvent` — thêm budget tracking |
| (MỚI) tracking per video | Cần struct/collection mới hoặc embed trong EventReward |

#### S2. Đối soát / Reconciliation
- **CRITICAL**: Hiện tại reconciliation KHÔNG check budget
- Khi approve reconciliation item → phải check budget còn không
- Khi reject → phải refund budget (Used giảm, Remain tăng)
- Budget data phải xuất hiện trong reconciliation report

**Files bị tác động:**
| File | Thay đổi |
|------|----------|
| `pkg/admin/service/reconciliation_processing.go` | Check budget khi tạo reconciliation items |
| `pkg/admin/service/reconciliation_running.go` | **Atomic budget deduction** khi approve items |
| `internal/model/mg/reconciliation.go` | Thêm budget info vào ReconciliationStatistic |
| `internal/model/mg/reconciliation_item.go` | Thêm budget tracking per item |
| `pkg/admin/model/request/reconciliation.go` | Request thêm budget-related filters |

#### S3. CashFlow & Transfer
- **AddCashFlow**: Cần ghi nhận budget deduction cùng lúc
- **Transfer**: Khi execute transfer → update budget used
- **Refund**: Khi reject → auto refund budget

**Files bị tác động:**
| File | Thay đổi |
|------|----------|
| `internal/service/cashflow.go:58` | `AddCashFlow` — trigger budget update |
| `internal/model/mg/cash_flow.go` | CashFlowOptions thêm budget reference |
| `internal/model/mg/transfer.go` | Transfer tracking budget impact |

#### S4. Partner Budget Validation (ĐÃ CÓ — cần enhance)
- **Hiện tại**: Check `sum(event_budgets) ≤ partner.Bpp` khi tạo/sửa event
- **Cần thêm**: Khi sửa event budget → re-validate partner budget

**Files bị tác động:**
| File | Thay đổi |
|------|----------|
| `pkg/admin/service/event.go:192-199` | Enhance validation (trừ budget cũ, cộng budget mới) |
| `internal/module/database/mongodb/aggregate_pipeline/event.go` | Pipeline tính tổng budget |

---

## Technique 2: Starbursting — Câu hỏi chi tiết

### Nhóm 1: Setup Budget trong Event

| Câu hỏi | Trả lời / Phân tích |
|----------|---------------------|
| **WHO** thiết lập budget? | Admin (staff) qua admin panel |
| **WHAT** data cần nhập? | Total, UserCap, VideoCap (cả 3 optional, mặc định = unlimited) |
| **WHEN** có thể sửa budget? | Bất kỳ lúc nào, nhưng `new_total ≥ current_used` |
| **WHERE** lưu trữ? | Embedded trong `EventRaw.Bpe` (BudgetInfo struct) |
| **WHY** code update đang reset Used=0? | BUG hoặc design choice cũ. Code comment out cho thấy đã từng có logic giữ used nhưng bị bỏ |
| **HOW** validate khi sửa? | `new_total ≥ used`, `VideoCap ≤ UserCap ≤ Total`, re-check partner budget |

### Nhóm 2: Admin theo dõi Budget

| Câu hỏi | Trả lời / Phân tích |
|----------|---------------------|
| **WHO** xem budget? | Admin/Staff qua admin panel |
| **WHAT** cần hiển thị? | Total, Used (reward), BonusUsed (tách), Remain, UserCap, VideoCap, Exhausted, burn rate |
| **WHEN** data cập nhật? | Real-time khi reward được tính/approve/reject |
| **WHERE** data đến từ? | `EventRaw.Bpe` + aggregate từ EventReward + EventBonus |
| **WHY** cần burn rate? | Dự đoán khi nào hết budget → admin chủ động điều chỉnh |
| **HOW** hiển thị? | Event detail page + Event list (badge status) + Dashboard chart |

### Nhóm 3: User theo dõi Budget

| Câu hỏi | Trả lời / Phân tích |
|----------|---------------------|
| **WHO** xem? | Creator/User qua public app |
| **WHAT** user được thấy? | UserCap, VideoCap, personal earned, per-video earned, bonus (tách) |
| **WHAT** user KHÔNG được thấy? | Tổng budget event, budget remaining event, earning creator khác |
| **WHEN** hiển thị? | Khi xem event detail, earnings page, event listing |
| **WHERE** tính toán? | Backend aggregate per user per event + per video |
| **WHY** API hiện tại sai? | `Bpe` expose nguyên `BudgetInfo{Total, Used, Remain}` → user thấy tổng budget event! |
| **HOW** fix? | Tạo response struct mới, chỉ expose user-specific data |

### Nhóm 4: Đối soát (Reconciliation)

| Câu hỏi | Trả lời / Phân tích |
|----------|---------------------|
| **WHO** thực hiện đối soát? | Admin |
| **WHAT** thay đổi khi có budget? | Thêm budget check khi approve, budget refund khi reject, budget data trong report |
| **WHEN** check budget? | Tại thời điểm approve (hard check), không phải lúc tạo reconciliation |
| **WHERE** budget bị trừ? | Khi reconciliation item status → completed, atomic update `EventRaw.Bpe` |
| **WHY** hiện tại không check? | Vì budget system chưa implement enforcement |
| **HOW** handle race condition? | MongoDB atomic `findOneAndUpdate` với condition `remain >= amount` |

### Nhóm 5: Các vấn đề khác

| Câu hỏi | Trả lời / Phân tích |
|----------|---------------------|
| **Extended Period** ảnh hưởng budget? | Event hết hạn nhưng ExtendedPeriod enabled → reward vẫn tính → budget vẫn bị trừ |
| **MaximumRewardPerUser** vs UserCap? | `MaximumRewardPerUser` ở EventSchema level (per schema), UserCap ở Event level (tổng). Cần clarify overlap |
| **EventSchemaQuantity** vs budget? | `Quantity.Total/Remaining` đếm số lượng reward, budget đếm tiền. Hai hệ thống song song |
| **Bonus trong reconciliation?** | `ReconciliationItemRaw.Bonus` field đã có → bonus ĐÃ trong reconciliation flow |
| **Auto-reject conditions** vs budget? | `EventAutoRejectCondition` check view/engagement, KHÔNG check budget. Cần thêm? |

---

## Technique 3: Reverse Brainstorming — Cách làm hệ thống thất bại

### Anti-pattern 1: Race Condition dẫn overspend
**Cách thất bại:** 10 rewards approve cùng lúc, mỗi cái check `remain > 0` → tất cả pass → budget vượt 10x
**Giải pháp:** MongoDB atomic `findOneAndUpdate` với `$inc: -amount` + condition `remain >= amount`
**Áp dụng cho:** Event budget, User cap, Video cap — CẢ 3 TẦNG

### Anti-pattern 2: Budget leak khi reject
**Cách thất bại:** Reward approved → trừ budget → reject sau đó → budget KHÔNG hoàn lại → "mất tiền"
**Giải pháp:** Auto-refund pipeline: reject → `$inc: +amount` cho budget + user tracking + video tracking
**Files:** `reconciliation_running.go`, `event_reward.go` (ChangeStatus)

### Anti-pattern 3: Update budget mất dữ liệu (ĐÃ XẢY RA!)
**Cách thất bại:** Admin sửa budget total → code reset `Used=0, Remain=Total` → mất toàn bộ tracking
**Giải pháp:** Uncomment và fix logic: `used = event.Bpe.Used`, `remain = new_total - used`
**File:** `pkg/admin/service/event.go:289-309` — code comment out cho thấy đã nhận ra vấn đề nhưng chưa fix

### Anti-pattern 4: User thấy budget event (privacy leak)
**Cách thất bại:** API trả `Bpe{Total: 100000000, Used: 80000000}` → creator biết tổng ngân sách chiến dịch
**Giải pháp:** Public response chỉ chứa: user_cap, user_earned, video_cap, per_video_earned
**File:** `pkg/public/model/response/event.go:62-63`

### Anti-pattern 5: Reconciliation approve không check budget
**Cách thất bại:** Budget hết 100% → admin vẫn approve reconciliation → overspend
**Giải pháp:** Reconciliation running phải atomic check + deduct budget trước khi complete item
**File:** `pkg/admin/service/reconciliation_running.go`

### Anti-pattern 6: Bonus tính vào budget
**Cách thất bại:** Bonus 500k + Reward 500k → budget trừ 1tr → budget cháy gấp đôi
**Giải pháp:** `BonusUsed` tracking riêng, `Remain = Total - Used` (Used CHỈ là reward, KHÔNG bao gồm bonus)
**Data model:** Thêm `BonusUsed float64` vào BudgetInfo

### Anti-pattern 7: MaximumRewardPerUser conflict với UserCap
**Cách thất bại:** Schema set MaximumRewardPerUser = 10 (SỐ LƯỢNG), UserCap = 5tr (SỐ TIỀN). Creator đăng 2 video viral → kiếm 5tr chỉ với 2 rewards → MaximumRewardPerUser=10 vô nghĩa
**Giải pháp:** Clarify: `MaximumRewardPerUser` = số lượng reward (content), `UserCap` = số tiền VND. Hai constraint khác nhau, cần check CẢ HAI

### Anti-pattern 8: Extended Period không check budget
**Cách thất bại:** Event kết thúc, ExtendedPeriod enabled → views tiếp tục tăng → reward tiếp tục tính → budget đã hết nhưng reward vẫn tạo
**Giải pháp:** Budget check phải apply cho CẢ extended period, không chỉ event active period

### Anti-pattern 9: Duplicate Event copy budget tracking
**Cách thất bại:** Duplicate event → copy cả `Used`, `Remain` từ event cũ → event mới bắt đầu với budget sai
**Giải pháp:** Duplicate phải reset: `Used=0, BonusUsed=0, Remain=Total, Exhausted=false`

### Anti-pattern 10: Budget không đồng bộ khi sửa reward manually
**Cách thất bại:** Admin manually edit reward amount → budget tracking bị lệch
**Giải pháp:** Mọi thay đổi reward amount phải trigger budget recalculation

### Anti-pattern 11: CashFlow ghi nhận nhưng budget không trừ
**Cách thất bại:** AddCashFlow tạo entry → balance tăng → nhưng Event.Bpe.Used không tăng → budget tracking sai
**Giải pháp:** Budget deduction phải atomic cùng CashFlow creation (hoặc ít nhất cùng transaction)

### Anti-pattern 12: Partner budget validation khi sửa event
**Cách thất bại:** Event A budget 50tr, Event B budget 60tr, Partner Bpp = 100tr. Sửa Event A → 80tr → tổng = 140tr > 100tr nhưng validation chỉ check `new_total + sum(other_events)`, KHÔNG trừ `old_total`
**Giải pháp:** Validation: `sum(all_event_budgets) - old_budget + new_budget ≤ partner.Bpp`
**Hiện trạng:** Code hiện tại có thể đã handle qua `budgetInEvents[0].TotalBudget + body.Bpe` nhưng cần verify khi update (có exclude event đang sửa không)

### Anti-pattern 13: Hệ thống cào view bị ảnh hưởng
**Cách thất bại:** Khi budget hết → stop cào view/metrics → mất data analytics
**Giải pháp:** View/metrics crawling PHẢI tiếp tục bất kể budget status. Chỉ REWARD bị chặn

### Anti-pattern 14: Content manual flow bỏ qua budget
**Cách thất bại:** `ContentManualFlow` (admin tạo content thủ công) → tạo reward → không check budget
**Giải pháp:** Budget check phải apply cho MỌI reward creation path, kể cả manual

---

## Tổng hợp: Danh sách chức năng bị tác động (theo priority)

### 🔴 P0 — Phải thay đổi (Core Logic)

| # | Chức năng | File(s) | Thay đổi | Impact |
|---|-----------|---------|----------|--------|
| 1 | **BudgetInfo model** | `model/mg/event.go` | Thêm UserCap, VideoCap, BonusUsed, Exhausted | Foundation |
| 2 | **Reward calculation** | `internal/service/event_schema.go` | Check 3 tầng budget trước khi tính reward | Core |
| 3 | **Event Update budget** | `pkg/admin/service/event.go:289-309` | Fix logic giữ Used/Remain khi sửa budget | BUG FIX |
| 4 | **Reconciliation approve** | `pkg/admin/service/reconciliation_running.go` | Atomic budget deduction khi approve | Core |
| 5 | **Reconciliation reject/refund** | `pkg/admin/service/reconciliation_running.go` | Auto refund budget khi reject item | Core |
| 6 | **Public API response** | `pkg/public/model/response/event.go` | KHÔNG expose tổng budget, chỉ user cap + progress | Privacy |

### 🟡 P1 — Nên thay đổi (UX + Tracking)

| # | Chức năng | File(s) | Thay đổi |
|---|-----------|---------|----------|
| 7 | **User budget tracking** | (MỚI) + aggregate pipeline | Per-user per-event + per-video earning tracking |
| 8 | **Admin event detail** | `pkg/admin/model/response/event.go` | Budget breakdown (reward vs bonus, user distribution) |
| 9 | **Event listing badge** | `pkg/admin/service/event.go` + public | Status badge: 🟢 Active 🟡 >80% 🔴 Exhausted |
| 10 | **Bonus tracking tách riêng** | `model/mg/event.go` + service | `BonusUsed` field riêng, KHÔNG trừ budget |
| 11 | **CashFlow + Budget sync** | `internal/service/cashflow.go` | Budget update atomic cùng CashFlow |
| 12 | **Event Create validation** | `pkg/admin/service/event.go` | Validate VideoCap ≤ UserCap ≤ Total |

### 🟢 P2 — Nice to have

| # | Chức năng | File(s) | Thay đổi |
|---|-----------|---------|----------|
| 13 | **Extended Period budget check** | `internal/service/event.go` | Budget enforcement trong extended period |
| 14 | **Partner budget re-validation** | `pkg/admin/service/event.go:249-257` | Fix validation khi update (exclude current event) |
| 15 | **Event Statistic + Chart** | `pkg/admin/service/event.go` | Budget burn rate, forecast |
| 16 | **Admin alert email** | (MỚI) | Email khi event budget > 75%, 95%, 100% |
| 17 | **Reconciliation report** | `pkg/admin/service/reconciliation.go` | Thêm budget data vào report export |
| 18 | **MaximumRewardPerUser clarification** | `model/mg/event_schema.go` | Document: count-based vs money-based cap |

---

## Key Insights

### Insight 1: Budget enforcement hiện tại = ZERO — chỉ có tracking
**Impact:** CRITICAL | **Effort:** HIGH
**Source:** Code analysis + Reverse Brainstorming
**Why:** `BudgetInfo` hiện tại chỉ track `Used/Remain` nhưng KHÔNG có code nào CHẶN reward khi budget hết. Reconciliation không check budget. Reward calculation không check budget. Hệ thống có thể overspend vô hạn.

### Insight 2: Code Update Event đang có BUG — reset budget tracking
**Impact:** HIGH | **Effort:** LOW
**Source:** Code analysis (`event.go:289-309`)
**Why:** Khi admin sửa budget total, code SET `Used=0, Remain=Total` thay vì giữ lại Used. Đoạn code fix đã được viết nhưng bị COMMENT OUT. Đây là bug cần fix ngay, bất kể có implement budget system mới hay không.

### Insight 3: Public API đang leak tổng budget cho creator
**Impact:** HIGH | **Effort:** LOW
**Source:** Starbursting (What user KHÔNG nên thấy)
**Why:** Response field `Bpe *BudgetInfo` expose nguyên struct cho client. Creator có thể thấy tổng ngân sách chiến dịch (ví dụ 100 triệu) — thông tin nhạy cảm của brand. Phải thay bằng user-specific response.

### Insight 4: Reconciliation là điểm enforcement chính — nhưng đang bỏ trống
**Impact:** CRITICAL | **Effort:** MEDIUM
**Source:** Mind Mapping + Reverse Brainstorming
**Why:** Flow hiện tại: Reward tạo (pending) → Reconciliation approve → CashFlow → Transfer. Budget PHẢI được check và deduct tại Reconciliation approve (hard check), vì đây là điểm tiền thực sự được ghi nhận. Nếu không → overspend.

### Insight 5: MaximumRewardPerUser và UserCap là HAI khái niệm khác nhau
**Impact:** MEDIUM | **Effort:** LOW
**Source:** Starbursting
**Why:** `MaximumRewardPerUser` (EventSchema) = giới hạn SỐ LƯỢNG reward (bài đăng). `UserCap` (Event) = giới hạn SỐ TIỀN VND. Hai constraint không thay thế nhau mà bổ sung nhau. Phải check CẢ HAI.

### Insight 6: Bonus đã tách riêng trong model nhưng chưa tách trong budget tracking
**Impact:** MEDIUM | **Effort:** LOW
**Source:** Code analysis
**Why:** `EventBonusRaw` là model riêng, reconciliation item có `Bonus` field. Nhưng `BudgetInfo.Used` hiện tại không phân biệt reward vs bonus. Nếu bonus tính vào Used → budget cháy nhanh gấp đôi.

### Insight 7: Race condition tại 3 tầng — cần 3 atomic operations
**Impact:** CRITICAL | **Effort:** HIGH
**Source:** Reverse Brainstorming
**Why:** Mỗi tầng (Event, User, Video) cần atomic check + deduct riêng. Nếu Event pass nhưng User fail → phải rollback Event. Cần consider: (1) Optimistic locking, (2) Two-phase: reserve → confirm, (3) Single atomic operation check all 3.

### Insight 8: Hệ thống cào view + content matching KHÔNG bị ảnh hưởng
**Impact:** HIGH (risk mitigation) | **Effort:** N/A
**Source:** Reverse Brainstorming
**Why:** Budget CHỈ ảnh hưởng reward calculation. View crawling, content matching, analytics — tất cả phải tiếp tục bình thường. Đây là nguyên tắc quan trọng để không phá vỡ data pipeline hiện có.

---

## Statistics
- **Total ideas/issues found:** ~65
- **Categories:** 8 (Admin setup, Admin tracking, User tracking, Reconciliation, Reward calc, CashFlow, Partner, Edge cases)
- **Key insights:** 8
- **Techniques applied:** 3 (Mind Mapping, Starbursting, Reverse Brainstorming)
- **Anti-patterns identified:** 14
- **Files bị tác động:** ~25 files
- **Bugs phát hiện:** 2 (Update budget reset, Public API leak)

---

## Recommended Next Steps

1. **Ngay:** Fix bug Update Event budget reset (`event.go:289-309`) — P0, effort LOW
2. **Ngay:** Fix Public API không expose tổng budget — P0, effort LOW
3. **Sau đó:** Tạo PRD chi tiết cho Budget System → `/bmad:prd`
4. **Architecture:** Design atomic budget deduction tại reconciliation → `/bmad:architecture`
5. **Implementation order:**
   - P0: BudgetInfo model upgrade → Reward check → Reconciliation enforcement → Public API fix
   - P1: User tracking → Admin UI → Bonus separation → CashFlow sync
   - P2: Extended period → Partner validation → Alerts → Reports

---

*Generated by BMAD Method v6 - Creative Intelligence*
*Session date: 2026-03-22*
