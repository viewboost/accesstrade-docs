# Brainstorming Session: Hệ thống Budget cho Ambassabor

**Date:** 2026-03-16
**Objective:** Phân tích và thiết kế chức năng Budget phân cấp cho platform Ambassabor
**Context:** Multi-partner influencer reward platform (Go + MongoDB), đã có budget cơ bản ở Event-level, cần nâng cấp lên hệ thống 3 tầng (Event → User → Video)

## Yêu cầu ban đầu & Đánh giá

| # | Yêu cầu | Verdict | Lý do |
|---|---------|---------|-------|
| 1 | Budget tối đa cho Brand | **DEFER** | Không phù hợp mô hình hiện tại — brand quản lý ngân sách bên ngoài platform, approve từng event. Cần khi chuyển sang self-serve |
| 2 | Budget tối đa cho User/Event | **MUST HAVE** | Tiêu chuẩn ngành, 100% platform đều có. Phân bổ công bằng, tránh 1 creator độc chiếm |
| 3 | Budget theo Event | **KEEP + ENHANCE** | Đã có `BudgetInfo`, cần thêm hard cap enforcement |
| 4 | Giới hạn số view/chiến dịch | **SIMPLIFY** | Nếu reward đã tính theo view → view cap ngầm tồn tại qua budget. Chỉ cần hiển thị estimated views, không cần cap riêng |
| 5 | Bonus tách riêng budget | **KEEP** | Đúng 100%, standard practice ngành |
| 6 | Alert đăng bài cho creator | **KEEP (đơn giản)** | Chỉ cần UI status trên event page, không cần multi-channel alert phức tạp |
| 7 | Budget tối đa cho mỗi Video | **KEEP** | Khuyến khích creator đăng nhiều video thay vì dồn hết vào 1 video viral. Phân tán rủi ro chi phí |

### Chi tiết đánh giá

**Brand Budget — Tại sao DEFER?**
- Các platform lớn (CreatorIQ, Grin, AspireIQ) KHÔNG có brand-level budget cap
- Brand quản lý ngân sách tổng ở bên ngoài platform (finance team, PO)
- Brand approve từng event — không "đổ tiền vào platform rồi chia"
- Chỉ cần khi có self-serve model (brand tự nạp tiền, tự tạo event)

**View Cap — Tại sao SIMPLIFY?**
- View khó validate (fake, bot, refresh)
- Nếu reward scheme đã tính theo view (500 VND/view) → event budget 50tr = max 100k views (ngầm)
- Chỉ cần hiển thị estimated max views trên UI, không cần hard cap riêng

**Alert — Tại sao đơn giản hóa?**
- Creator chỉ cần biết TRƯỚC khi đăng, không cần alert phức tạp
- Chỉ cần: (1) trạng thái budget trên event page, (2) banner khi chạm user cap, (3) badge "hết ngân sách" trên listing

## Scope được chọn

**Phase 1 (làm ngay):**
- Event Budget hard cap enforcement
- User Cap per Event (max earning per creator)
- Video Cap per Video (max earning per video)
- Bonus separation trong tracking
- UI status cho creator (budget còn/hết, per-video breakdown)

**Phase 2 (nếu cần):**
- Estimated view display (budget / CPV)
- Alert email cho admin khi event gần hết budget

**Phase 3 (khi scale lên self-serve):**
- Brand Budget + cascade validation
- Advanced analytics/forecasting

## Budget Behavior khi hết ngân sách

| Hành động | Budget còn | Budget hết |
|-----------|-----------|-----------|
| Cào view/metrics | Tiếp tục | **Tiếp tục** |
| Match bài đăng | Tiếp tục | Tiếp tục |
| Tính reward | Tạo reward | **CHẶN** |
| Bonus | Vẫn tính (độc lập) | **Vẫn tính** (độc lập) |
| Creator đăng bài mới | Cho phép | Cho phép, nhưng **cảnh báo** |

## Techniques Used
1. Mind Mapping — Cấu trúc phân cấp budget
2. Starbursting — Câu hỏi Who/What/Where/When/Why/How
3. Reverse Brainstorming — Cách làm hệ thống thất bại → giải pháp

---

## Hiện trạng (As-Is)

### Techcombank (hệ thống cũ)
- Budget chỉ ở cấp Event (1 event = 1 budget alert)
- Chỉ cảnh báo ngưỡng (75%, 95%, 100%) qua email
- Model: `BudgetCampaignRaw` với `Threshold` (VND)
- KHÔNG có budget cho Brand/Partner level
- KHÔNG có budget cho User/Creator level
- KHÔNG phân biệt budget vs bonus
- Khi đạt 100% → chỉ đánh dấu "completed", không tự động chặn

### Ambassabor (hiện tại)
- `BudgetInfo` embedded trong Event: `{total, used, remain, usedPercent}`
- Hệ thống reward đầy đủ: EventReward, CashFlow, Transfer
- EventBonus rules tách riêng
- CHƯA CÓ budget cap cho Brand hay User level
- CHƯA CÓ alert system cho creator

---

## Ideas Generated

### Category 1: Budget Hierarchy (3 tầng)

#### Brand Budget (Level 1)
- Tổng ngân sách Brand cấp cho platform (VND)
- Period: monthly / quarterly / yearly / unlimited
- Renewal policy: auto-renew / manual top-up
- Phân bổ xuống Events: tổng budget các Events ≤ Brand budget
- Unallocated pool (phần chưa gán event)
- Re-allocation (chuyển budget giữa events)
- Real-time spend tracking + burn rate + forecasting
- Ngưỡng cảnh báo: 50%, 75%, 90%, 100%
- Auto-pause events khi brand budget hết

#### Event Budget (Level 2)
- Total budget (VND) — giới hạn tổng chi cho event
- Budget type: "hard cap" (CHẶN reward khi hết) vs "soft cap" (CHỈ CẢNH BÁO)
- Validation: event_budget ≤ remaining_brand_budget
- View-based budget: CPV (Cost Per View) rate, max views = budget / CPV
- Spending tracking: reward_spent + bonus_spent (TÁCH RIÊNG)
- Remaining = total - reward_spent (bonus KHÔNG tính)
- Lifecycle: Draft → Active → Paused → Completed
- Auto-complete khi budget = 0

#### User Budget (Level 3)
- Max earning per user per event (VND)
- Max earning per user per day (optional)
- Max posts counted per event (optional)
- Tracking: total earned, remaining cap, posts submitted vs rewarded
- Khi đạt cap → CHẶN tính reward cho bài mới
- Bài đã đăng trước cap → vẫn được trả
- Grace period cho bài đang pending
- Hiển thị remaining cap trên UI

### Category 2: Bonus Separation

- EventBonus rules hoạt động ĐỘC LẬP khỏi budget
- Bonus pool riêng biệt (có thể có giới hạn riêng hoặc không)
- KHÔNG trừ vào event budget, KHÔNG trừ vào user cap
- 2 trường tracking riêng: `budget_spent` vs `bonus_spent`
- Reporting tách riêng: "Chi budget: X, Chi bonus: Y"
- Creator thấy rõ: "Hoa hồng: X, Thưởng thêm: Y"

### Category 3: Alert & Notification

#### Event-level alerts (cho admin)
- 75% → Warning email
- 95% → Urgent alert + consider pausing
- 100% → Auto-complete + final notification

#### Brand-level alerts (cho brand admin)
- 50%, 75%, 90% → Progressive warnings
- 100% → Pause ALL events under brand

#### User-level alerts (cho Creator)
- 80% cap → In-app warning "Gần hết quota"
- 95% cap → Push notification "Đăng thêm 1-2 bài nữa"
- 100% cap → Banner "Đã chạm budget, bài mới sẽ không được thưởng"

#### Alert channels
- Email (admin, brand)
- In-app notification center (creator, admin)
- Push notification (creator mobile)
- Webhook (brand integration)

#### Alert actions (tự động)
- Pause event enrollment
- Block new reward calculation
- Show "budget exhausted" on event page
- Trigger reconciliation review
- One-shot alert: mỗi ngưỡng chỉ trigger 1 lần (flag `alert_75_sent`)

### Category 4: Data Integrity & Race Condition

- Atomic budget deduction: MongoDB `findOneAndUpdate` với `$inc` + `$gte` condition
- Redis distributed lock cho concurrent reward approval
- Double-check: check khi submit (soft) + check khi approve (hard/binding)
- Budget refund tự động khi reward reject
- Floor validation: `new_budget ≥ current_spent` khi sửa budget
- Fail-safe strategy: khi budget service lỗi → queue retry, KHÔNG auto-approve/reject
- Cascade validation: `sum(event_budgets) ≤ brand_remaining`
- Immutable audit log cho mọi budget change

### Category 5: View-to-Money Conversion

- CPV (Cost Per View) rate do admin set khi tạo event
- Max views = budget / CPV
- View counting rules: unique view? organic only? sau bao lâu?
- View cap per creator (chống spam)
- Deduplication (unique user) + bot detection
- Dynamic pricing option (CPV thay đổi theo performance)

### Category 6: Creator UX & Transparency

- Progress bar trên event page: "350k / 500k used"
- Transparent breakdown: "Cap: 500k | Đã nhận: 350k | Còn lại: 150k | ~2 bài nữa"
- Creator KHÔNG thấy tổng budget event, CHỈ thấy cap của mình
- Real-time budget status trên UI (không delay)
- Earnings page: phân biệt "Hoa hồng" vs "Thưởng thêm"
- Event page: badge "Budget exhausted" khi hết
- Notification khi reward bị reject vì budget

### Category 8: Creator Budget Communication (UX Flow chi tiết)

> **Nguyên tắc chính:** Creator phải biết cap + progress TRƯỚC khi đăng bài, không phải sau.

#### 8.1 Trang chi tiết chiến dịch (Event Detail Page)

Đây là nơi **quan trọng nhất** — creator vào đây để quyết định có đăng bài không.

**Trạng thái: Còn budget, chưa chạm cap**
```
┌─────────────────────────────────────────┐
│  💰 Hoa hồng của bạn                   │
│                                         │
│  Tối đa mỗi chiến dịch: 5,000,000 VND  │
│  Tối đa mỗi video: 2,000,000 VND       │
│  ████████████░░░░░░░░  60%              │
│  Đã nhận: 3,000,000 VND (2 video)      │
│  Còn lại: 2,000,000 VND                │
│                                         │
│  Chi tiết video:                        │
│  • Video 1: 2,000,000 ✅ (đạt tối đa)  │
│  • Video 2: 1,000,000 🟢 (còn slot)    │
│                                         │
│  Bonus (không tính vào giới hạn):       │
│  +500,000 VND                           │
└─────────────────────────────────────────┘
```

**Trạng thái: Gần chạm user cap (≥ 80%)**
```
┌─────────────────────────────────────────┐
│  💰 Hoa hồng của bạn                   │
│                                         │
│  Tối đa mỗi chiến dịch: 5,000,000 VND  │
│  Tối đa mỗi video: 2,000,000 VND       │
│  ██████████████████░░  90%              │
│  Đã nhận: 4,500,000 VND (3 video)      │
│  Còn lại: 500,000 VND                  │
│                                         │
│  ⚠️ Bạn sắp đạt mức hoa hồng tối đa   │
│                                         │
│  Chi tiết video:                        │
│  • Video 1: 2,000,000 ✅ (đạt tối đa)  │
│  • Video 2: 2,000,000 ✅ (đạt tối đa)  │
│  • Video 3:   500,000 🟢 (còn slot)    │
│                                         │
│  Bonus (không tính vào giới hạn):       │
│  +500,000 VND                           │
└─────────────────────────────────────────┘
```

**Trạng thái: Đã chạm user cap**
```
┌─────────────────────────────────────────┐
│  💰 Hoa hồng của bạn                   │
│                                         │
│  Tối đa mỗi chiến dịch: 5,000,000 VND  │
│  Tối đa mỗi video: 2,000,000 VND       │
│  ████████████████████  100%             │
│  Đã nhận: 5,000,000 VND (3 video)      │
│                                         │
│  ✅ Bạn đã đạt mức hoa hồng tối đa     │
│     cho chiến dịch này.                 │
│     Bài đăng mới sẽ không được tính     │
│     hoa hồng, nhưng vẫn có thể nhận    │
│     bonus nếu có.                       │
│                                         │
│  Chi tiết video:                        │
│  • Video 1: 2,000,000 ✅ (đạt tối đa)  │
│  • Video 2: 2,000,000 ✅ (đạt tối đa)  │
│  • Video 3: 1,000,000 ⚠️ (user cap)    │
│                                         │
│  Bonus (không tính vào giới hạn):       │
│  +800,000 VND                           │
└─────────────────────────────────────────┘
```

**Trạng thái: Event budget đã hết (toàn bộ chiến dịch)**
```
┌─────────────────────────────────────────┐
│  🔴 Chiến dịch đã hết ngân sách        │
│                                         │
│  Đã nhận: 3,200,000 VND (2 video)      │
│                                         │
│  Bài đăng mới sẽ không được tính       │
│  hoa hồng. Bài đã đăng trước đó        │
│  vẫn được thanh toán đầy đủ.           │
│                                         │
│  Chi tiết video:                        │
│  • Video 1: 2,000,000 ✅ (đạt tối đa)  │
│  • Video 2: 1,200,000 🔴 (event hết)   │
│                                         │
│  Bonus (không tính vào giới hạn):       │
│  +500,000 VND                           │
└─────────────────────────────────────────┘
```

#### 8.2 Trang theo dõi hoa hồng (Earnings Page)

Tổng quan tất cả earnings của creator across events.

```
┌─────────────────────────────────────────────────────────────┐
│  📊 Hoa hồng của tôi                                       │
│                                                             │
│  Chiến dịch          Hoa hồng      Cap         Trạng thái  │
│  ──────────────────────────────────────────────────────────  │
│  Tết Nguyên Đán      3,000,000   / 5,000,000   🟢 Còn      │
│  Summer Sale         5,000,000   / 5,000,000   🟡 Đã đạt   │
│  Back to School      1,200,000   / 5,000,000   🟢 Còn      │
│  Mùa Thu Vàng        2,800,000   / —           🔴 Hết NS   │
│                                                             │
│  ──────────────────────────────────────────────────────────  │
│  Tổng hoa hồng:     12,000,000 VND                         │
│  Tổng bonus:         1,800,000 VND                          │
│  ──────────────────────────────────────────────────────────  │
│  Tổng thu nhập:     13,800,000 VND                          │
└─────────────────────────────────────────────────────────────┘
```

**Trạng thái badges:**
- 🟢 **Còn** — creator vẫn kiếm thêm được
- 🟡 **Đã đạt cap** — creator đã chạm giới hạn cá nhân (event vẫn còn budget)
- 🔴 **Hết ngân sách** — event budget đã hết (chưa chạm cap cá nhân nhưng event hết tiền)

#### 8.3 Event Listing (Danh sách chiến dịch)

Badge nhanh trên card chiến dịch để creator biết trước khi click vào.

```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ 🟢 Tết Nguyên Đán│  │ 🟡 Summer Sale   │  │ 🔴 Back to School│
│                  │  │                  │  │                  │
│ Hoa hồng/view    │  │ Hoa hồng/view    │  │ Hoa hồng/view    │
│ Cap: 5tr/người   │  │ Đã đạt tối đa   │  │ Hết ngân sách    │
│                  │  │                  │  │                  │
│ [Xem chi tiết]   │  │ [Xem chi tiết]   │  │ [Xem chi tiết]   │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

#### 8.4 Quy tắc hiển thị

| Dữ liệu | Creator thấy | Creator KHÔNG thấy |
|----------|-------------|-------------------|
| User cap (giới hạn cá nhân) | ✅ Có | — |
| Video cap (giới hạn mỗi video) | ✅ Có | — |
| Số tiền đã nhận per video | ✅ Có (chi tiết từng video) | — |
| Số tiền bonus (tách riêng) | ✅ Có | — |
| Tổng budget event | ❌ | Không hiển thị |
| Budget còn lại event | ❌ | Không hiển thị |
| Số tiền creator khác nhận | ❌ | Không hiển thị |
| Trạng thái event (còn/hết) | ✅ Badge | Không hiển số cụ thể |

#### 8.5 Video status badges trong chi tiết

| Badge | Ý nghĩa |
|-------|---------|
| 🟢 (còn slot) | Video chưa chạm video cap, vẫn kiếm thêm được |
| ✅ (đạt tối đa) | Video đã chạm video cap |
| ⚠️ (user cap) | Video chưa chạm video cap nhưng user cap đã hết → video bị giới hạn bởi tầng trên |
| 🔴 (event hết) | Event budget đã hết → video bị giới hạn bởi tầng trên |

#### 8.6 Edge Cases UX

| Tình huống | Hiển thị cho Creator |
|-----------|---------------------|
| Event không set user cap | Không hiển thị phần user cap, chỉ hiển thị earnings + video cap |
| Event không set video cap | Không hiển thị phần video cap, chỉ hiển thị earnings + user cap |
| Event hết budget nhưng creator chưa chạm cap | "Chiến dịch đã hết ngân sách" (creator hiểu là không phải lỗi của họ) |
| Creator chạm user cap nhưng event còn budget | "Bạn đã đạt mức tối đa" (creator hiểu là giới hạn cá nhân) |
| Video chạm video cap nhưng user cap còn | Video badge ✅, nhưng creator vẫn đăng video mới được |
| Reward bị reject → budget hoàn lại | Cập nhật lại progress bar + video badge, có thể đổi từ ✅→🟢 |
| Creator mới tham gia event đã gần hết | Hiển thị event budget status (🔴) trên listing để creator cân nhắc |

### Category 9: Video Cap (Budget per Video)

> **Bổ sung sau brainstorm ban đầu** — layer thứ 3 trong hệ thống budget

#### 9.1 Tại sao cần Video Cap?

**Vấn đề không có Video Cap:**
```
Event budget: 100tr, User cap: 5tr, Reward: 500đ/view
Creator A đăng 1 video viral 1 triệu views:
→ Reward = 5,000,000 VND (ĂN HẾT USER CAP bằng 1 video)
→ Video 2, 3, 4... → reward 0
→ Creator không có động lực đăng thêm
```

**Có Video Cap:**
```
Event budget: 100tr, User cap: 5tr, Video cap: 2tr
Creator A đăng 3 video:
├── Video 1: 500k views → reward 2,000,000 (HIT VIDEO CAP)
├── Video 2: 100k views → reward 1,500,000
├── Video 3: 200k views → reward 1,500,000 (HIT USER CAP tổng = 5tr)
→ Creator đăng 3 video thay vì 1 → nhiều content hơn cho brand
```

#### 9.2 Hệ thống 3 tầng Budget

```
Event Budget (100 triệu)
  └── User Cap (5 triệu / creator)
        └── Video Cap (2 triệu / video)
```

#### 9.3 Logic kiểm tra (thứ tự ưu tiên)

```
Khi tính reward cho 1 video:
  1. Check Event Budget còn không?     → Nếu hết → CHẶN
  2. Check User Cap còn không?         → Nếu hết → CHẶN
  3. Check Video Cap còn không?        → Nếu hết → CHẶN (cho video này)
  4. Reward = min(calculated_reward, remaining_event, remaining_user, remaining_video)
```

Ví dụ:
```
calculated_reward = 3,000,000 (từ view count)
remaining_event  = 50,000,000 ✅
remaining_user   = 4,000,000 ✅ nhưng < calculated
remaining_video  = 2,000,000 ✅ nhưng < remaining_user
→ Actual reward = min(3tr, 50tr, 4tr, 2tr) = 2,000,000 (video cap giới hạn)
```

#### 9.4 Validation Rules

| Rule | Mô tả |
|------|--------|
| `video_cap ≤ user_cap` | Video cap không thể lớn hơn user cap (vô nghĩa) |
| `video_cap > 0` hoặc `0 = unlimited` | 0 = không giới hạn per video, chỉ bị user cap + event budget |
| Video cap chỉ áp dụng reward | Bonus KHÔNG bị video cap giới hạn |
| Thay đổi giữa chừng | Chỉ áp dụng cho reward chưa tính, không retroactive |

#### 9.5 Edge Cases

| Tình huống | Xử lý |
|-----------|-------|
| User cap = 5tr, Video cap = 3tr, creator đăng 2 video | Video 1: max 3tr, Video 2: max 2tr (user cap giới hạn tổng) |
| Admin set Video cap = 0 | Unlimited per video, chỉ bị user cap + event budget |
| Video bị xoá sau khi reward approved | KHÔNG refund — reward đã approved là final |
| Video cap thay đổi giữa chừng | Áp dụng cho reward chưa tính, reward đã tính giữ nguyên |
| Reward bị reject → video budget hoàn lại | CÓ refund video budget, creator có thể kiếm thêm từ video đó |

### Category 7: Audit & Compliance

- Immutable audit log: who, when, old_value → new_value
- Budget change history cho mỗi entity
- Export budget report cho brand (reconciliation)
- Dashboard: tổng chi, chi theo event, burn rate, forecast
- UTC internally, display theo brand timezone

---

## Key Insights (đã cập nhật sau review)

### Insight 1: Budget 3 tầng (Event → User → Video), Brand Budget DEFER
**Impact:** HIGH | **Effort:** MEDIUM
**Source:** Mind Mapping + Starbursting + Senior Review + Video Cap Analysis
**Why:** 3 tầng giải quyết 3 bài toán khác nhau: Event cap kiểm soát tổng chi chiến dịch, User cap phân bổ công bằng giữa creators, Video cap khuyến khích đăng nhiều video thay vì dồn hết vào 1 video viral. Brand Budget chỉ cần khi chuyển self-serve model.

### Insight 2: Bonus PHẢI tách hoàn toàn khỏi Budget
**Impact:** HIGH | **Effort:** LOW
**Source:** Mind Mapping + Reverse Brainstorming
**Why:** Gộp → budget cháy nhanh gấp đôi. Cần 2 trường riêng (`budget_spent` vs `bonus_spent`), 2 logic riêng, 2 dòng báo cáo riêng. EventBonus rules đã tách trong model, chỉ cần đảm bảo spending tracking cũng tách.

### Insight 3: Race condition là rủi ro #1 — cần Atomic Budget Deduction
**Impact:** CRITICAL | **Effort:** MEDIUM
**Source:** Reverse Brainstorming + Starbursting
**Why:** Nhiều reward approve đồng thời có thể vượt budget. Giải pháp: MongoDB atomic `findOneAndUpdate` với condition `remaining >= reward_amount`. Double-check tại submit (soft) + approve (hard).

### Insight 4: Creator chỉ cần UI status đơn giản, không cần multi-channel alert
**Impact:** HIGH | **Effort:** LOW
**Source:** Reverse Brainstorming + Senior Review
**Why:** Over-engineering alert system (push, email, webhook) là waste. Creator chỉ cần: (1) trạng thái budget trên event page, (2) banner rõ ràng khi chạm user cap, (3) badge "hết ngân sách" trên event listing. Không cần multi-threshold alerts (75%, 95%...).

### Insight 5: View cap không cần riêng — đã ngầm tồn tại qua budget + reward scheme
**Impact:** MEDIUM | **Effort:** N/A (không cần build)
**Source:** Senior Review
**Why:** Nếu reward = 500 VND/view, budget = 50tr → max views = 100k (ngầm). Chỉ cần hiển thị estimated max views trên UI dựa trên budget/CPV rate. Không cần build view cap system riêng.

### Insight 6: Budget refund mechanism khi reward bị reject
**Impact:** MEDIUM | **Effort:** LOW
**Source:** Reverse Brainstorming
**Why:** Reward approved → trừ budget. Reject sau đó → budget phải hoàn lại tự động. Không có → "budget leak".

### Insight 7: Khi budget hết — vẫn cào view, vẫn tracking, chỉ CHẶN reward
**Impact:** HIGH | **Effort:** LOW
**Source:** TFluencer reference + Senior Review
**Why:** View data vẫn có giá trị cho analytics/reporting. Creator vẫn được đăng bài (có cảnh báo). Bonus vẫn hoạt động độc lập. Chỉ reward mới bị chặn.

### Insight 8: Video Cap khuyến khích đăng nhiều video — phân tán rủi ro
**Impact:** HIGH | **Effort:** LOW
**Source:** Six Thinking Hats + Video Cap Analysis
**Why:** Không có video cap → 1 video viral ăn hết user cap → creator không đăng thêm → brand chỉ có 1 bài content. Có video cap → creator phải đăng nhiều bài mới đạt user cap → brand có nhiều content hơn. Logic: `reward = min(calculated, remaining_event, remaining_user, remaining_video)`. Validation: `video_cap ≤ user_cap`.

---

## Statistics
- **Total ideas:** ~125
- **Categories:** 9
- **Key insights:** 8
- **Techniques applied:** 3 + Six Thinking Hats (Video Cap)
- **Anti-patterns identified:** 14

## Data Model Proposal (scope Phase 1)

### Updated: Event.BudgetInfo (enhance cái đã có)
```go
type BudgetInfo struct {
    Total       float64     // Tổng budget event (VND)
    Used        float64     // Đã chi reward (KHÔNG bao gồm bonus)
    BonusUsed   float64     // Đã chi bonus (tracking TÁCH RIÊNG)
    Remain      float64     // Còn lại = Total - Used
    UsedPercent float64
    UserCap     float64     // Max earning per user per event (0 = unlimited)
    VideoCap    float64     // Max earning per video (0 = unlimited)
    Exhausted   bool        // true khi Used >= Total → chặn reward mới
}
```

### Updated: EventReward (thêm user + video budget tracking)
```go
// Tracking per user per event
type UserBudgetTracking struct {
    UserTotalEarned  float64  // Tổng creator đã kiếm reward trong event
    UserBonusEarned  float64  // Tổng bonus (tracking riêng, không tính vào cap)
    UserCapReached   bool     // true khi UserTotalEarned >= UserCap
}

// Tracking per video (có thể embedded trong Reward record)
type VideoBudgetTracking struct {
    VideoTotalEarned  float64  // Tổng reward video này đã kiếm
    VideoCapReached   bool     // true khi VideoTotalEarned >= VideoCap
}
```

### Logic tính reward (pseudo-code)
```go
func CalculateReward(event, user, video, rawReward) float64 {
    // 3 tầng check, lấy min
    remainEvent := event.BudgetInfo.Remain
    remainUser  := event.BudgetInfo.UserCap - user.UserTotalEarned  // 0 nếu UserCap = unlimited
    remainVideo := event.BudgetInfo.VideoCap - video.VideoTotalEarned // 0 nếu VideoCap = unlimited

    caps := []float64{remainEvent}
    if event.BudgetInfo.UserCap > 0 {
        caps = append(caps, remainUser)
    }
    if event.BudgetInfo.VideoCap > 0 {
        caps = append(caps, remainVideo)
    }

    return min(rawReward, min(caps...))
}
```

### Validation rules
```
- VideoCap ≤ UserCap (nếu cả hai đều > 0)
- UserCap ≤ Total (nếu cả hai đều > 0)
- Không cho phép giảm cap dưới mức đã chi
- VideoCap, UserCap = 0 nghĩa là unlimited
```

### Lưu ý kỹ thuật
- Dùng MongoDB atomic `findOneAndUpdate` với `$inc` + condition `remain >= amount` để tránh race condition
- Budget refund tự động khi reward bị reject (hoàn lại `Used`, tăng `Remain`, giảm `VideoTotalEarned`)
- `BonusUsed` chỉ để tracking/reporting, KHÔNG ảnh hưởng budget logic
- Bonus KHÔNG bị video cap hay user cap giới hạn

---

## Recommended Next Steps

1. **Ngay:** Tạo PRD chi tiết cho Budget System → `/bmad:prd`
2. **Sau đó:** Architecture design → `/bmad:architecture`
3. **Ưu tiên implement:**
   - P0: Event Budget hard cap + User Cap + Video Cap (3 tầng core)
   - P0: Bonus separation trong spending tracking
   - P1: Creator UI status (banner chạm cap, badge hết budget, per-video breakdown)
   - P1: Alert email cho admin khi event gần hết budget
   - P2: Estimated view display trên UI
   - P3 (khi scale): Brand Budget + cascade validation

---

*Generated by BMAD Method v6 - Creative Intelligence*
*Session date: 2026-03-16*
