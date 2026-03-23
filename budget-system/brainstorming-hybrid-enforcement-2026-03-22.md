# Brainstorming Session: Hybrid Budget Enforcement — Deep Dive

**Date:** 2026-03-22
**Objective:** Phân tích toàn diện phương án Hybrid Budget Enforcement, cân nhắc mọi edge case, trade-off, rủi ro. So sánh với TCB (chặn cứng) để đưa ra quyết định cuối cùng.
**Context:**
- Hệ thống Techcombank: CHẶN tạo reward khi hết budget (Option A — đang production)
- Ambassador brainstorm trước: CHẶN tại reconciliation (Option B)
- Phương án Hybrid (Option C): Vẫn tạo reward + soft check, enforce tại đối soát

## Techniques Used
1. Six Thinking Hats — 6 góc nhìn về Hybrid
2. Reverse Brainstorming — Cách nào làm Hybrid thất bại
3. SWOT Analysis — So sánh chi tiết 3 options

---

## Hiểu rõ 3 Options trước khi phân tích

### Option A: Chặn tạo Reward (TCB đang dùng)
```
View tăng → Check budget → Hết? → KHÔNG tạo reward
                           Còn? → Tạo reward (pending) → reserve budget
                                    ↓
                              Đối soát → Approve → CashFlow
```
**Đặc điểm TCB:**
- `cashValid = Pending + Completed + Waiting` → Pending ĐÃ reserve budget
- `IsBlockReward` flag trên Event → chặn cứng toàn bộ reward mới
- `IsBlockSubmitContent` flag → ở 95% còn chặn cả content submission
- Threshold notifications: 75%, 95%, 100%
- Reconciliation KHÔNG check budget lại (vì đã check khi tạo)

### Option B: Chặn tại Đối soát
```
View tăng → Tạo reward (pending) bình thường
              ↓
         Đối soát → Check budget → Approve/Reject → CashFlow
```

### Option C: Hybrid
```
View tăng → Tạo reward (pending) + soft check (cảnh báo)
              ↓
         Đối soát → Hard check budget → Approve/Reject → CashFlow
```

---

## Technique 1: Six Thinking Hats — Phân tích Hybrid

### White Hat (Sự thật & Dữ liệu)

**Sự thật về flow Ambassador hiện tại:**
1. Reward được tạo tự động bởi `UpdateRewardTypeByStatisticContent()` — chạy khi view/like/comment thay đổi
2. Reward có status: `pending` / `waitingApproved` / `approved` / `rejected` / `completed`
3. Đối soát tạo ReconciliationItem từ rewards pending → admin duyệt → `runCashBack` tạo CashFlow
4. CashFlow là điểm tiền thực sự vào balance creator
5. `ChangeStatusItem` cho phép admin reject/approve TỪNG item
6. `Running` duyệt TOÀN BỘ items pending cùng lúc (batch)

**Sự thật về TCB:**
1. TCB dùng `EstimateBudgetByEvent()` check budget MỖI LẦN tạo reward
2. Pending rewards ĐÃ reserve budget → budget giảm ngay khi reward tạo
3. Budget chỉ "mở lại" khi reward bị reject (Pending giảm → cashValid giảm)
4. TCB KHÔNG có manual `ChangeStatusItem` → reconciliation auto-complete all

**Sự thật về khác biệt Ambassador vs TCB:**

| Khác biệt | TCB | Ambassador |
|-----------|-----|-----------|
| Reward tạo cách nào | Auto, check budget | Auto, KHÔNG check |
| Pending reserve budget? | CÓ | KHÔNG |
| Admin duyệt từng item? | KHÔNG (batch all) | CÓ (`ChangeStatusItem`) |
| Reward update liên tục? | Tạo 1 lần | Có thể UPDATE cash khi view tăng |
| Content approval flow? | Đơn giản | Phức tạp (`waitingApproved` → `approved`) |

**Phát hiện CRITICAL:** Ambassador reward cash **thay đổi liên tục** — mỗi ngày `UpdateRewardTypeByStatisticContent` chạy lại, **UPDATE** cash của reward đã tồn tại (dòng 311-319 event_schema.go). TCB KHÔNG có behavior này.

→ Nếu reserve budget tại thời điểm tạo reward (Option A), cash thay đổi sau đó sẽ làm budget tracking sai.

### Red Hat (Cảm xúc & Trực giác)

**Từ góc nhìn Creator:**
- Option A: "Tại sao bài tôi đăng 2 ngày trước có thưởng, bài hôm nay không có?" → Bực bội, không hiểu
- Option C (Hybrid): "Bài tôi vẫn có reward pending, nhưng khi đối soát bị reject" → Có thể thất vọng nhưng rõ ràng hơn
- Cả 2 đều gây khó chịu, nhưng Hybrid **minh bạch hơn** — creator thấy reward, biết có khả năng bị reject

**Từ góc nhìn Admin:**
- Option A: "Chiến dịch auto-stop, tôi không cần làm gì" → Nhẹ nhàng
- Option C: "Tôi phải review reward pending khi đối soát, quyết định ai được ai không" → Nhiều quyền kiểm soát hơn, nhưng cũng nhiều việc hơn
- Admin Ambassador đã quen **duyệt từng item** → Hybrid phù hợp workflow hiện tại

**Từ góc nhìn Brand:**
- Option A: "Budget tôi an toàn 100%, không bao giờ vượt" → Yên tâm
- Option C: "Budget vẫn an toàn, nhưng có thể thấy rewards pending > budget trên dashboard" → Có thể lo lắng nếu không hiểu pending ≠ approved

### Black Hat (Rủi ro & Cảnh báo)

**Rủi ro #1: Reward Pending tích tụ vượt xa budget — "Reward Inflation"**
- Ambassador reward tạo tự động mỗi ngày
- Chiến dịch 100tr budget, 500 creators, mỗi người kiếm 500k/ngày
- Sau 1 tuần: 500 × 500k × 7 = 1.75 tỷ pending (17.5x budget!)
- Đối soát phải reject 94% → creator phẫn nộ
- **Severity:** HIGH
- **Mitigation:** Soft cap warning + limit reward creation khi budget gần hết (ví dụ >150% pending/budget)

**Rủi ro #2: Thứ tự đối soát không công bằng — "First Come First Served"**
- Đối soát process items theo thứ tự creation
- Creator A đăng ngày 1 → approved (budget còn)
- Creator B đăng ngày 7 → rejected (budget hết)
- Creator B có thể có video tốt hơn nhưng đăng muộn hơn
- **Severity:** MEDIUM
- **Mitigation:** Admin review tổng thể trước, có thể chọn approve/reject từng item

**Rủi ro #3: Admin overwhelm — quá nhiều items phải review**
- Nếu pending 17x budget, admin phải reject hàng nghìn items
- `Running` hiện tại auto-complete ALL pending items → KHÔNG có logic reject
- **Severity:** HIGH
- **Mitigation:** Auto-reject items vượt budget trong `Running`, chỉ manual review edge cases

**Rủi ro #4: Budget display misleading cho admin**
- Dashboard hiện: `Used: 30tr / Total: 100tr` → "Còn 70tr"
- Thực tế: Pending = 200tr → sẽ bị reject 130tr khi đối soát
- Admin không nhận ra quy mô overspend cho đến đối soát
- **Severity:** MEDIUM
- **Mitigation:** Hiển thị cả Pending trên dashboard: "Used: 30tr | Pending: 200tr | Budget: 100tr"

**Rủi ro #5: Reward cash thay đổi liên tục — budget tracking trượt**
- Reward tạo hôm nay cash = 100k, mai view tăng → cash = 500k
- Nếu reserve 100k → đối soát thấy 500k → vượt reserve
- Nếu update reserve → phức tạp, phải track delta
- **Severity:** HIGH (đặc thù Ambassador, TCB không có vấn đề này)
- **Mitigation:** Đây là lý do chính không nên reserve budget tại thời điểm tạo reward

**Rủi ro #6: Extended Period + Hybrid**
- Event kết thúc → ExtendedPeriod enabled → reward vẫn tạo (cash=0)
- Đối soát cho extended period → cash=0 → không ảnh hưởng budget
- Nhưng nếu admin enable cash cho extended period sau đó?
- **Severity:** LOW (extended reward hiện tại cash=0)

**Rủi ro #7: Bonus trong đối soát**
- `runCashBack` xử lý cả 3 loại: Content, Milestone, Bonus
- Bonus KHÔNG bị budget cap → phải tách logic trong Running
- Hiện tại `Running` auto-complete ALL → bonus và reward gộp chung
- **Severity:** MEDIUM

### Yellow Hat (Lợi ích & Cơ hội)

**Lợi ích #1: Data đầy đủ — không mất reward records**
- Option A (TCB): Budget hết → reward không tạo → mất data về performance thực tế
- Hybrid: Reward vẫn tạo → admin thấy "nếu không cap thì chi 300tr" → insight cho planning chiến dịch sau

**Lợi ích #2: Phù hợp workflow Ambassador**
- Admin đã quen `ChangeStatusItem` (duyệt từng item)
- Hybrid tận dụng workflow có sẵn, chỉ thêm budget check
- TCB-style (`IsBlockReward`) cần thêm flag mới + auto-block logic

**Lợi ích #3: Flexibility cho Admin**
- Budget hết nhưng Creator A có video xuất sắc → admin vẫn có thể approve (override)
- Option A: Reward không tạo → không có gì để approve
- Hybrid: Reward pending → admin tăng budget hoặc override approve

**Lợi ích #4: Không cần giải quyết "reward cash thay đổi liên tục"**
- TCB-style reserve budget → phải re-reserve khi cash update → phức tạp
- Hybrid: Budget chỉ enforce tại đối soát → dùng cash cuối cùng → đơn giản

**Lợi ích #5: Backward compatible**
- Ambassador hiện tại tạo reward không check budget → Hybrid giữ nguyên flow này
- Chỉ thêm logic ở đối soát → ít thay đổi code hơn

### Green Hat (Sáng tạo & Giải pháp mới)

**Idea 1: "Budget Fence" — Hybrid với soft reservation**
```
Reward tạo → Soft reserve (estimate) → Cảnh báo khi estimate > budget
  ↓
Đối soát → Hard check (actual cash) → Approve nếu budget còn
```
- Soft reserve = estimate dựa trên cash hiện tại, KHÔNG binding
- Mục đích: early warning cho admin, KHÔNG chặn reward
- Khi cash update → estimate tự update

**Idea 2: "Budget Priority Queue" — Đối soát thông minh**
- Khi `Running`, thay vì auto-complete all:
  1. Sort items theo priority (cash/view ratio, engagement, time)
  2. Approve items từ trên xuống cho đến khi hết budget
  3. Reject phần còn lại
- Admin có thể customize priority rules

**Idea 3: "Two-Pass Reconciliation"**
- Pass 1 (Preview): Tính toán, hiển thị "Nếu approve all → tổng = X, budget = Y, vượt = Z"
- Pass 2 (Execute): Admin review preview → adjust → confirm
- Tương tự current `processing` → `running` flow nhưng thêm budget preview

**Idea 4: "Rolling Budget Check" — Kết hợp A + C**
- Reward tạo: Soft check → nếu budget < 20% → CHẶN reward mới (giống TCB)
- Reward đã tạo khi budget > 20%: Vẫn ở pending → enforce tại đối soát
- Tức là: Hybrid cho 80% đầu, TCB cho 20% cuối
- **Đây có thể là sweet spot**

**Idea 5: "Budget Snapshot at Reconciliation"**
- Khi tạo đối soát (`processing`): Snapshot budget hiện tại
- Khi `running`: Check items against snapshot
- Items tạo SAU snapshot → pending cho đợt đối soát sau
- Giải quyết vấn đề "first come first served"

### Blue Hat (Process & Tổng kết)

**Câu hỏi quyết định:**
1. Ambassador admin muốn kiểm soát chi tiết hay auto-pilot?
2. Reward cash thay đổi liên tục → TCB-style reserve có khả thi?
3. Có chấp nhận reward pending >> budget (inflation)?
4. Data đầy đủ (biết performance thực tế) vs Data sạch (chỉ reward hợp lệ)?

---

## Technique 2: Reverse Brainstorming — Cách làm Hybrid thất bại

### Anti-pattern 1: Reward Inflation không kiểm soát
**Thất bại:** 1000 rewards pending tổng 500tr vs budget 50tr → admin bị choáng khi đối soát
**Insight:** Cần "soft ceiling" — khi pending > 150% budget → hiển thị warning nổi bật, có thể slow down reward creation (giảm tần suất check, không tính mới)

### Anti-pattern 2: `Running` auto-approve tất cả
**Thất bại:** Admin nhấn "Duyệt" → `Running` auto-complete ALL items → vượt budget 5x
**Insight:** `Running` PHẢI có budget enforcement: approve đến khi hết budget → reject phần còn lại. Đây là thay đổi CRITICAL trong `reconciliation_running.go`

### Anti-pattern 3: Race condition trong Running
**Thất bại:** 50 goroutines (`ants` pool size 50) chạy `runCashBack` đồng thời → mỗi goroutine check "budget còn" → tất cả pass → overspend
**Insight:** Budget deduction phải SEQUENTIAL hoặc dùng MongoDB atomic operation. Không thể parallel budget check trong goroutine pool.
**Code hiện tại:** `p, _ := ants.NewPoolWithFunc(50, func(...)` → 50 concurrent workers!

### Anti-pattern 4: ChangeStatusItem bypass budget
**Thất bại:** Admin manually approve item qua `ChangeStatusItem` → KHÔNG check budget → overspend
**Insight:** `ChangeStatusItem` cũng phải check budget nếu status = approve/complete

### Anti-pattern 5: Creator không biết bị reject cho đến đối soát
**Thất bại:** Creator đăng 10 video, thấy 10 rewards pending → đối soát reject 8 → creator tức giận "tại sao bảo tôi còn tiền?"
**Insight:** UI PHẢI hiển thị rõ: "Reward pending — chưa xác nhận, phụ thuộc vào ngân sách chiến dịch". Thêm disclaimer ngay từ đầu.

### Anti-pattern 6: Đối soát reject nhưng không notification
**Thất bại:** 100 rewards rejected → creator không biết → check balance → "tiền đâu?"
**Insight:** `runCashBack` hiện CHỈ push notification cho items COMPLETED. Cần thêm notification cho items REJECTED vì budget.

### Anti-pattern 7: Bonus bị reject nhầm
**Thất bại:** `Running` loop qua items, check budget → bonus item bị reject vì "hết budget"
**Insight:** Bonus items phải SKIP budget check, luôn approve (trừ khi data invalid)

### Anti-pattern 8: Referral commission tính sai
**Thất bại:** `SendCommissionToReferrer` tính commission từ `totalCash` của items → items bị reject → commission vẫn gửi
**Insight:** `SendCommissionToReferrer` phải chạy SAU khi items đã final (chỉ tính từ completed items)

### Anti-pattern 9: UpdateStatisticUserEvent sau reject
**Thất bại:** Reject 80% items → nhưng statistic vẫn tính tất cả pending → dashboard sai
**Insight:** `UpdateStatisticUserEvent` phải chạy lại SAU `Running` hoàn thành (đã có ở dòng 500-502)

### Anti-pattern 10: Budget không cập nhật Used sau đối soát
**Thất bại:** Đối soát approve 50tr → nhưng `EventRaw.Bpe.Used` vẫn = 0 → budget tracking sai
**Insight:** `Running` phải update `EventRaw.Bpe` sau khi process xong: `Used = sum(completed items cash)`, `Remain = Total - Used`

---

## Technique 3: SWOT Analysis — So sánh 3 Options

### Option A: Chặn tạo Reward (TCB-style)

| | |
|---|---|
| **Strengths** | **Weaknesses** |
| Budget KHÔNG BAO GIỜ vượt | Reward cash thay đổi liên tục → reserve bị lệch |
| Đơn giản cho admin (auto-pilot) | Mất data performance thực tế |
| Proven (TCB đang dùng) | Creator bị "im lặng" reject — không thấy reward |
| Không cần thay đổi đối soát | Không phù hợp Ambassador workflow (admin duyệt chi tiết) |
| | Cần giải quyết cash-update-after-reserve |
| | `IsBlockReward` flag → tất cả creator bị chặn cùng lúc |
| **Opportunities** | **Threats** |
| Tận dụng code pattern TCB | Ambassador reward update mechanism → phải redesign |
| Consistency giữa 2 systems | Creator churn (không hiểu tại sao không có reward) |

### Option B: Chặn tại Đối soát (thuần túy)

| | |
|---|---|
| **Strengths** | **Weaknesses** |
| Admin có toàn quyền kiểm soát | Reward inflation không kiểm soát |
| Data đầy đủ 100% | Admin bị overwhelm khi đối soát |
| Phù hợp workflow hiện tại | Creator thấy reward rồi bị reject → UX tệ |
| Không cần sửa reward creation | Không có early warning |
| | `Running` hiện tại auto-complete → phải rewrite |
| **Opportunities** | **Threats** |
| Leverage manual review workflow | Overspend nếu admin approve tất cả (human error) |
| Budget flexibility | Creator trust issues |

### Option C: Hybrid (Soft check + Hard enforce)

| | |
|---|---|
| **Strengths** | **Weaknesses** |
| Data đầy đủ | Phức tạp hơn Option A |
| Admin flexibility (override possible) | Reward inflation (cần mitigation) |
| Early warning (soft check) | Creator có thể confused về pending vs confirmed |
| Budget safe (hard check tại đối soát) | `Running` vẫn phải rewrite |
| Không cần giải quyết cash-update issue | 2 điểm check → 2 điểm maintain |
| Backward compatible với reward creation | |
| Phù hợp Ambassador workflow | |
| **Opportunities** | **Threats** |
| Kết hợp Idea 4 (Rolling) cho best of both | Nếu soft check quá weak → giống Option B |
| Budget Priority Queue cho đối soát smart | Nếu soft check quá strong → giống Option A |
| Two-Pass Reconciliation cho transparency | Complexity tax dài hạn |

---

## Tổng hợp: Ma trận quyết định

| Tiêu chí | Trọng số | Option A (TCB) | Option C (Hybrid) |
|----------|:--------:|:---------:|:--------:|
| Budget safety (không overspend) | 25% | ⭐⭐⭐⭐⭐ (5) | ⭐⭐⭐⭐ (4) |
| Data completeness | 15% | ⭐⭐ (2) | ⭐⭐⭐⭐⭐ (5) |
| Creator UX | 15% | ⭐⭐ (2) | ⭐⭐⭐ (3) |
| Admin flexibility | 15% | ⭐⭐ (2) | ⭐⭐⭐⭐⭐ (5) |
| Implementation effort | 10% | ⭐⭐ (2) | ⭐⭐⭐ (3) |
| Compatibility với codebase | 10% | ⭐⭐ (2) | ⭐⭐⭐⭐ (4) |
| Maintenance simplicity | 10% | ⭐⭐⭐⭐ (4) | ⭐⭐⭐ (3) |
| **Weighted Total** | **100%** | **3.05** | **3.90** |

**Option B thuần túy bị loại** — không có early warning, reward inflation quá cao, admin overwhelm.

---

## Key Insights

### Insight 1: Reward cash thay đổi liên tục là LÝ DO SỐ 1 nên chọn Hybrid thay vì TCB-style
**Impact:** CRITICAL | **Effort:** N/A (đây là constraint)
**Source:** Six Thinking Hats (White) + Code analysis
**Why:** Ambassador `UpdateRewardTypeByStatisticContent` UPDATE cash mỗi ngày. TCB tạo reward 1 lần với cash cố định. Nếu reserve budget lúc tạo reward (cash=100k) rồi cash tăng lên 500k → reserve sai 5x. Fix vấn đề này cần re-reserve mỗi khi cash update → phức tạp, race condition. Hybrid tránh hoàn toàn vấn đề này bằng cách chỉ check budget tại đối soát (dùng cash final).

### Insight 2: `Running` với 50 goroutines là BLOCKER — phải sequential budget check
**Impact:** CRITICAL | **Effort:** MEDIUM
**Source:** Reverse Brainstorming (Anti-pattern #3)
**Why:** `ants.NewPoolWithFunc(50, ...)` chạy 50 users đồng thời. Mỗi user loop qua items. Nếu budget check parallel → race condition → overspend. Giải pháp: Budget deduction phải nằm NGOÀI parallel loop, hoặc dùng MongoDB atomic `findOneAndUpdate` cho mỗi item.

### Insight 3: Hybrid cần "Budget Fence" — soft ceiling để kiểm soát inflation
**Impact:** HIGH | **Effort:** LOW
**Source:** Six Thinking Hats (Green — Idea 1)
**Why:** Nếu không có soft ceiling, pending có thể 17x budget → admin overwhelm khi đối soát. Budget Fence = khi `sum(pending cash) > 150% budget` → hiển thị warning nổi bật trên admin dashboard + có thể trigger notification.

### Insight 4: Rolling Budget Check (Idea 4) là sweet spot — Hybrid cho 80%, Hard cho 20%
**Impact:** HIGH | **Effort:** MEDIUM
**Source:** Six Thinking Hats (Green — Idea 4)
**Why:** Khi budget > 20% → tạo reward bình thường (Hybrid). Khi budget < 20% → chặn reward mới (TCB-style). Tránh inflation lớn (chỉ 20% cuối bị chặn), vẫn có data cho 80% đầu, và hard stop cho 20% cuối đảm bảo budget safe. Threshold 20% có thể config per event.

### Insight 5: `ChangeStatusItem` là lỗ hổng budget — phải patch
**Impact:** HIGH | **Effort:** LOW
**Source:** Reverse Brainstorming (Anti-pattern #4)
**Why:** Admin có thể manually approve items vượt budget qua `ChangeStatusItem` hiện tại KHÔNG check budget. Cần thêm budget check, hoặc ít nhất warning "Approve item này sẽ vượt budget X%".

### Insight 6: Bonus phải tách khỏi budget logic ở MỌI điểm
**Impact:** MEDIUM | **Effort:** LOW
**Source:** Reverse Brainstorming (Anti-pattern #7)
**Why:** `runCashBack` xử lý 3 loại items cùng loop: Content, Milestone, Bonus. Budget check phải SKIP bonus items. `ReconciliationStatistic` cần tách: `TotalCashReward` vs `TotalCashBonus`.

### Insight 7: Notification cho rejected items là BẮT BUỘC
**Impact:** HIGH | **Effort:** LOW
**Source:** Reverse Brainstorming (Anti-pattern #5, #6)
**Why:** Hiện tại `runCashBack` chỉ notify items completed. Creator sẽ không biết reward bị reject. Cần: (1) In-app notification "Reward bị từ chối do hết ngân sách", (2) UI disclaimer "Reward pending — chưa xác nhận" ngay từ đầu.

### Insight 8: Two-Pass Reconciliation giải quyết admin overwhelm
**Impact:** MEDIUM | **Effort:** MEDIUM
**Source:** Six Thinking Hats (Green — Idea 3)
**Why:** Pass 1 = Preview (hiển thị: tổng pending, budget, ai được ai không). Pass 2 = Execute (admin confirm). Tận dụng flow hiện tại: `processing` = Pass 1, `running` = Pass 2. Chỉ cần thêm budget preview ở step `processing`.

---

## Kết luận & Đề xuất

### Đề xuất: Option C — Hybrid với Rolling Budget Check

```
┌──────────────────────────────────────────────────────────────────┐
│                    HYBRID + ROLLING BUDGET                        │
│                                                                  │
│  Còn > 20% budget: Tạo reward bình thường + soft check (cảnh báo) │
│  Còn ≤ 20% budget: CHẶN tạo reward mới (TCB-style hard block)    │
│  Đối soát:       Hard check + auto-reject nếu vượt budget       │
│  Bonus:          Luôn tạo, luôn approve (tách riêng)            │
│  ChangeStatusItem: Thêm budget check + warning                  │
└──────────────────────────────────────────────────────────────────┘
```

### Chi tiết flow đề xuất:

```
View tăng
  ↓
UpdateRewardTypeByStatisticContent()
  ├── Check 1: Event budget remain > 20%?
  │     YES → Tạo/Update reward bình thường
  │     NO  → Check 2: Event.IsBlockReward?
  │              YES → KHÔNG tạo reward (log cho analytics)
  │              NO  → Set IsBlockReward = true + alert admin
  ↓
Reward (pending) tồn tại
  ↓
Admin tạo Đối soát (processing)
  ├── Preview: Tính tổng pending vs budget
  ├── Hiển thị: "Tổng pending: 120tr | Budget còn: 80tr | Vượt: 40tr"
  ├── Gợi ý: auto-reject items dư (FIFO hoặc priority)
  ↓
Admin chạy Đối soát (running)
  ├── Items REWARD: Atomic budget check → approve/reject
  │     ├── Sort theo priority (date, engagement, cash)
  │     ├── Approve từ trên xuống cho đến hết budget
  │     ├── Reject phần còn lại (note: "Hết ngân sách")
  │     └── Update EventRaw.Bpe (Used, Remain, Exhausted)
  ├── Items BONUS: LUÔN approve (skip budget check)
  ├── Items MILESTONE: Budget check tương tự reward
  ↓
Post-Running:
  ├── Notification: Creator nhận notify cho cả completed + rejected
  ├── Statistic: UpdateStatisticUserEvent cho tất cả users
  ├── Budget: Update EventRaw.Bpe final
  └── Referral: SendCommissionToReferrer (CHỈ từ completed items)
```

### Thay đổi cần thiết:

| Ưu tiên | Thay đổi | File | Effort |
|---------|---------|------|--------|
| P0 | Budget check trong `Running` (sequential, atomic) | `reconciliation_running.go` | HIGH |
| P0 | Bonus tách khỏi budget logic trong `runCashBack` | `reconciliation_running.go` | LOW |
| P0 | Update `EventRaw.Bpe` sau Running | `reconciliation_running.go` | MEDIUM |
| P1 | Rolling check trong reward creation (>20% → allow, ≤20% → block) | `internal/service/event_schema.go` | MEDIUM |
| P1 | Budget preview trong `processing` step | `reconciliation_processing.go` | MEDIUM |
| P1 | `ChangeStatusItem` budget check | `reconciliation.go` | LOW |
| P1 | Notification cho rejected items | `reconciliation_running.go` | LOW |
| P2 | Budget Fence warning cho admin dashboard | `pkg/admin/service/event.go` | LOW |
| P2 | Creator UI disclaimer "Reward pending — chưa xác nhận" | Frontend | LOW |

---

## Bảng so sánh cuối cùng: Tại sao KHÔNG chọn TCB-style (Option A) cho Ambassador?

| Vấn đề | TCB | Ambassador |
|--------|-----|-----------|
| Reward cash cố định sau khi tạo? | ✅ Có | ❌ KHÔNG — cash update hàng ngày |
| Reserve budget chính xác? | ✅ Có | ❌ KHÔNG THỂ — cash thay đổi |
| Admin cần duyệt chi tiết? | Không | ✅ Có (ChangeStatusItem) |
| Cần data performance thực tế? | Không quan trọng | ✅ Quan trọng (insight cho brand) |
| Content approval flow đơn giản? | ✅ Có | ❌ KHÔNG (waitingApproved → approved) |

**TCB-style không phù hợp Ambassador vì fundamental difference: reward cash thay đổi liên tục.** Reserve budget tại thời điểm tạo sẽ luôn sai.

---

## Statistics
- **Total ideas:** ~80
- **Categories:** 6 (Flow design, Race condition, Creator UX, Admin UX, Data integrity, Compatibility)
- **Key insights:** 8
- **Anti-patterns identified:** 10
- **Techniques applied:** 3 (Six Thinking Hats, Reverse Brainstorming, SWOT)
- **Options analyzed:** 3 (A: TCB-style, B: Reconciliation-only, C: Hybrid)

## Recommended Next Steps

1. **Ngay:** Align với business team — Hybrid + Rolling Budget Check có chấp nhận được không?
2. **Nếu OK:** Tạo PRD chi tiết cho Budget System (Hybrid) → `/bmad:prd`
3. **Architecture:** Design atomic budget deduction trong `Running` → `/bmad:architecture`
4. **Implementation:** Bắt đầu từ P0 (reconciliation_running.go là core thay đổi)

---

*Generated by BMAD Method v6 - Creative Intelligence*
*Session date: 2026-03-22*
