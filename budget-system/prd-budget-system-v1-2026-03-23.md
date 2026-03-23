# Product Requirements Document: Budget System V1 — Core Engine

**Date:** 2026-03-23
**Author:** vinhnguyen
**Version:** 1.0
**Project Type:** Feature Enhancement
**Project Level:** 3
**Status:** Draft

---

## Document Overview

PRD này định nghĩa requirements cho **V1 — Budget Engine Core**: model dữ liệu, enforcement logic 3 tầng, và bug fixes. V1 tập trung vào backend — đảm bảo hệ thống CHẶN reward khi vượt budget, không bao gồm UI/UX cho admin hay creator.

**Related Documents:**
- [Brainstorming: Budget System](brainstorming-budget-system-2026-03-16.md)
- [Brainstorming: Hybrid Enforcement](brainstorming-hybrid-enforcement-2026-03-22.md)
- [Brainstorming: Impact Analysis](brainstorming-budget-impact-analysis-2026-03-22.md)
- [Overview: Budget System](overview-budget-system.md)
- [Reward Flow Analysis](reward-flow-analysis.md)

---

## Executive Summary

Ambassador Platform hiện **không có cơ chế kiểm soát ngân sách tự động**. Reward được tính không giới hạn, không có cap per user hay per video, bonus gộp chung vào budget. V1 triển khai hệ thống budget 3 tầng (Event → User → Video) với TCB-style delta-based enforcement — chặn thẳng tại thời điểm tạo/update reward, giống approach đã proven ở production Techcombank.

---

## Product Goals

### Business Objectives

1. **Kiểm soát chi tiêu tự động** — Hệ thống tự chặn reward khi vượt ngân sách, không phụ thuộc admin kiểm tra thủ công
2. **Phân bổ công bằng** — User Cap đảm bảo không creator nào độc chiếm ngân sách, Video Cap khuyến khích đăng nhiều video
3. **Tách biệt Bonus** — Bonus tracking riêng, không ảnh hưởng budget, báo cáo rõ ràng

### Success Metrics

| Metric | Target | Cách đo |
|--------|--------|---------|
| Overspend events | 0% | Không event nào chi vượt budget sau khi deploy |
| Budget accuracy | 100% | `cashValid = sum(Pending + Completed + Waiting)` luôn khớp |
| Crawl pipeline impact | < 10% latency increase | Monitor reward update duration trước/sau |
| Bug fix: budget reset | 0 occurrences | Update event không reset Used=0 |

---

## Functional Requirements

### FR-001: Event Budget Configuration

**Priority:** Must Have

**Description:**
Admin có thể set 3 thông số budget khi tạo/sửa event: Total Budget (tổng ngân sách), User Cap (giới hạn mỗi creator), Video Cap (giới hạn mỗi video). Cả 3 đều optional — giá trị 0 hoặc bỏ trống = unlimited.

**Acceptance Criteria:**
- [ ] Admin set Total, UserCap, VideoCap khi tạo event
- [ ] Admin sửa Total, UserCap, VideoCap trên event đã tạo
- [ ] Validation: `VideoCap ≤ UserCap` (nếu cả 2 đều > 0)
- [ ] Validation: `UserCap ≤ Total` (nếu cả 2 đều > 0)
- [ ] Giá trị 0 = unlimited, hệ thống hoạt động như cũ (backward compatible)
- [ ] BudgetInfo struct mở rộng: thêm UserCap, VideoCap, BonusUsed, Exhausted

**Dependencies:** Không

---

### FR-002: Budget Update Protection

**Priority:** Must Have

**Description:**
Khi admin sửa budget Total, hệ thống giữ lại giá trị Used và tính lại Remain. Không được reset Used=0 (fix bug hiện tại). Không cho phép giảm Total dưới mức đã chi.

**Acceptance Criteria:**
- [ ] Sửa Total: `Remain = new_total - Used` (giữ Used nguyên)
- [ ] Validation: `new_total ≥ Used` — từ chối nếu giảm dưới mức đã chi
- [ ] Sửa UserCap: `new_userCap ≥ max(user_earned)` cho user đã kiếm nhiều nhất
- [ ] Sửa VideoCap: `new_videoCap ≥ max(video_earned)` cho video đã kiếm nhiều nhất
- [ ] Khi tăng Total/Cap: nếu `IsBlockReward = true` và budget còn → clear flag, cho phép reward tiếp tục

**Dependencies:** FR-001

---

### FR-003: Bonus Separation

**Priority:** Must Have

**Description:**
Bonus tracking hoàn toàn tách riêng khỏi budget. Bonus KHÔNG tính vào cashValid, KHÔNG bị cap nào ảnh hưởng. BudgetInfo có field `BonusUsed` riêng để tracking.

**Acceptance Criteria:**
- [ ] `BonusUsed` field riêng trong BudgetInfo
- [ ] `cashValid` chỉ tính reward (Statistic + Milestone), KHÔNG bao gồm bonus
- [ ] Bonus reward KHÔNG bị Video Cap, User Cap, hay Event Budget chặn
- [ ] Báo cáo tách rõ: reward spent vs bonus spent

**Dependencies:** FR-001

---

### FR-004: Partner Budget Validation Enhancement

**Priority:** Should Have

**Description:**
Enhance validation hiện có: khi sửa event budget, đảm bảo `sum(all_event_budgets) - old_budget + new_budget ≤ partner.Bpp`. Verify logic hiện tại có exclude event đang sửa không.

**Acceptance Criteria:**
- [ ] Tạo event: `sum(existing_events) + new_budget ≤ partner.Bpp`
- [ ] Sửa event: `sum(other_events) + new_budget ≤ partner.Bpp`
- [ ] Trả error message rõ ràng khi vượt partner budget

**Dependencies:** FR-001

---

### FR-005: Video Cap Enforcement

**Priority:** Must Have

**Description:**
Khi tính reward cho video, cash bị cap lại không vượt quá VideoCap. Phần vượt được lưu vào `overbudgetCash` để tracking performance thực tế.

**Acceptance Criteria:**
- [ ] `cash = min(calculated_reward, videoCap)` khi videoCap > 0
- [ ] `overbudgetCash = calculated_reward - cash` khi bị cap
- [ ] Video không có cap (videoCap = 0): hoạt động như cũ
- [ ] Áp dụng cho cả reward mới và reward update (view tăng)
- [ ] Bonus KHÔNG bị video cap

**Dependencies:** FR-001

---

### FR-006: User Cap Enforcement

**Priority:** Must Have

**Description:**
Tổng reward cash của 1 creator trong 1 event không vượt quá UserCap. Sử dụng delta-based check giống TCB: mỗi lần reward update, tính delta (phần tăng thêm) và check vs remaining user cap.

**Acceptance Criteria:**
- [ ] `userEarned = sum(all reward cash of user in event)`
- [ ] `userRemain = userCap - userEarned`
- [ ] Khi `delta > userRemain`: `cash = oldCash + userRemain`, lưu phần vượt vào overbudgetCash
- [ ] Khi `userRemain = 0`: chặn tất cả reward update cho user này trong event
- [ ] UserCap = 0: unlimited, không check
- [ ] Bonus KHÔNG tính vào userEarned, KHÔNG bị user cap

**Dependencies:** FR-005 (video cap check trước)

---

### FR-007: Event Budget Enforcement

**Priority:** Must Have

**Description:**
Tổng reward cash toàn event không vượt quá Event Budget. Áp dụng y hệt TCB `EstimateBudgetByEvent()` — delta-based check, set `IsBlockReward = true` khi hết budget.

**Acceptance Criteria:**
- [ ] `cashValid = sum(Pending + Completed + Waiting rewards)` — exclude Rejected, exclude Bonus
- [ ] `availableCash = eventBudget - cashValid`
- [ ] Reward mới: check `totalCash ≤ availableCash`, chặn nếu vượt
- [ ] Reward update: check `delta ≤ availableCash`, chặn update nếu vượt (giữ cash cũ)
- [ ] Khi hết budget: set `IsBlockReward = true` trên event
- [ ] `IsBlockReward = true` → skip tất cả reward creation/update cho event này
- [ ] Event Budget = 0: unlimited, không check

**Dependencies:** FR-006 (user cap check trước)

---

### FR-008: Milestone Budget Check

**Priority:** Must Have

**Description:**
Milestone reward (Content Milestone, View Milestone) có cash cố định — check budget cho toàn bộ cash trước khi tạo, giống TCB.

**Acceptance Criteria:**
- [ ] Check User Cap: `userEarned + milestoneCash ≤ userCap`
- [ ] Check Event Budget: `cashValid + milestoneCash ≤ eventBudget`
- [ ] Nếu vượt: KHÔNG tạo milestone reward
- [ ] Milestone KHÔNG có video cap (không gắn video cụ thể)

**Dependencies:** FR-006, FR-007

---

### FR-009: OverbudgetCash Tracking

**Priority:** Should Have

**Description:**
Lưu phần cash vượt cap/budget vào field `overbudgetCash` trên EventReward. Mục đích: tracking performance thực tế, hỗ trợ admin quyết định tăng budget/cap.

**Acceptance Criteria:**
- [ ] Field `overbudgetCash` trên EventRewardRaw
- [ ] Ghi nhận khi bị video cap cắt, user cap cắt, hoặc event budget chặn
- [ ] Admin có thể query tổng overbudgetCash per event (reporting)
- [ ] Khi admin tăng cap/budget → lần crawl tiếp overbudgetCash tự giảm (stateless)

**Dependencies:** FR-005, FR-006, FR-007

---

### FR-010: Fix Budget Reset on Update (Bug Fix)

**Priority:** Must Have

**Description:**
Fix bug hiện tại: khi admin sửa event, code reset `Used=0, Remain=Total` — mất toàn bộ tracking. Code fix đã được viết nhưng bị comment out tại `pkg/admin/service/event.go:289-309`.

**Acceptance Criteria:**
- [ ] Update event giữ nguyên Used, BonusUsed
- [ ] `Remain = new_total - Used`
- [ ] `UsedPercent = Used / Total * 100`
- [ ] Không mất tracking khi sửa bất kỳ field nào của event

**Dependencies:** Không — có thể fix ngay, independent

---

### FR-011: Fix Public API Budget Leak (Bug Fix)

**Priority:** Must Have

**Description:**
Fix Public API đang expose `BudgetInfo` nguyên xi cho creator — creator thấy được tổng ngân sách chiến dịch (thông tin nhạy cảm của brand).

**Acceptance Criteria:**
- [ ] Public API response KHÔNG chứa `Bpe.Total`, `Bpe.Used`, `Bpe.Remain`
- [ ] V1: trả về trạng thái event budget (còn/hết) dạng boolean, không trả số cụ thể
- [ ] Backward compatible: field `Bpe` vẫn tồn tại nhưng chỉ chứa thông tin hạn chế

**Dependencies:** Không — có thể fix ngay, independent

---

## Non-Functional Requirements

### NFR-001: Budget Check Performance

**Priority:** Must Have

**Description:**
Budget check tại reward update không làm chậm crawl pipeline đáng kể.

**Acceptance Criteria:**
- [ ] Budget check (3 tầng) hoàn thành < 50ms per reward update
- [ ] Tổng latency tăng < 10% so với trước khi thêm budget check

**Rationale:**
Crawl pipeline chạy hàng ngày cho hàng nghìn videos. Budget check chậm → crawl backlog → data delay.

---

### NFR-002: Budget Query Performance

**Priority:** Must Have

**Description:**
Query sum user rewards phải sử dụng index, đảm bảo performance khi event có nhiều creators.

**Acceptance Criteria:**
- [ ] Index trên `(event, user, status)` cho EventReward collection
- [ ] Sum query < 20ms cho event có tới 10,000 rewards

**Rationale:**
User Cap check cần sum tất cả reward của user trong event — query này chạy mỗi lần reward update.

---

### NFR-003: Atomic Budget Deduction

**Priority:** Must Have

**Description:**
Budget deduction phải atomic — không overspend do race condition khi nhiều rewards update đồng thời.

**Acceptance Criteria:**
- [ ] Không overspend > 1% budget trong bất kỳ test scenario nào
- [ ] Race condition test: 50 concurrent reward updates trên cùng event

**Rationale:**
Crawl pipeline có thể update nhiều videos cùng lúc. Nếu budget check không atomic → multiple rewards pass check đồng thời → overspend.

---

### NFR-004: Budget Refund on Reject

**Priority:** Must Have

**Description:**
Khi reward bị reject, budget tự động hoàn lại — cashValid giảm, remain tăng.

**Acceptance Criteria:**
- [ ] Reject reward → `Used` giảm, `Remain` tăng tương ứng
- [ ] `IsBlockReward` tự động clear nếu reject làm budget còn lại > 0
- [ ] Refund áp dụng cho cả 3 tầng (event, user, video tracking)

**Rationale:**
Không có refund → "budget leak" — budget bị trừ vĩnh viễn cho reward đã bị reject.

---

### NFR-005: Backward Compatibility

**Priority:** Must Have

**Description:**
Events không set budget/cap phải hoạt động y hệt trước. Không breaking change cho events hiện tại.

**Acceptance Criteria:**
- [ ] Event với Total=0, UserCap=0, VideoCap=0 → không có budget check, reward tính như cũ
- [ ] Events hiện tại không bị ảnh hưởng khi deploy
- [ ] API response backward compatible

**Rationale:**
Hệ thống đang production, không thể break events đang chạy.

---

### NFR-006: Crawl Pipeline Independence

**Priority:** Must Have

**Description:**
Budget chỉ ảnh hưởng reward calculation. View/like/comment crawling và content matching phải tiếp tục bình thường bất kể budget status.

**Acceptance Criteria:**
- [ ] `IsBlockReward = true` → crawl vẫn chạy, analytics vẫn update
- [ ] Content matching vẫn hoạt động khi budget hết
- [ ] Chỉ reward creation/update bị chặn, không ảnh hưởng data pipeline

**Rationale:**
View data có giá trị cho analytics/reporting. Dừng crawl khi hết budget → mất data.

---

## Epics

### EPIC-001: Budget Model & Configuration

**Description:**
Mở rộng data model BudgetInfo, thêm fields mới (UserCap, VideoCap, BonusUsed, Exhausted, overbudgetCash), validation rules, và fix bugs hiện tại.

**Functional Requirements:**
- FR-001 (Event Budget Configuration)
- FR-002 (Budget Update Protection)
- FR-003 (Bonus Separation)
- FR-004 (Partner Budget Validation)
- FR-010 (Fix Budget Reset)
- FR-011 (Fix Public API Leak)

**Story Count Estimate:** 6-8

**Priority:** Must Have

**Business Value:**
Foundation cho toàn bộ budget system. Fix 2 bugs đang production. Không có model đúng → không thể enforce.

---

### EPIC-002: Budget Enforcement Engine

**Description:**
Implement TCB-style delta-based budget check tại reward creation/update cho cả 3 tầng: Video Cap → User Cap → Event Budget. Bao gồm milestone check và overbudgetCash tracking.

**Functional Requirements:**
- FR-005 (Video Cap Enforcement)
- FR-006 (User Cap Enforcement)
- FR-007 (Event Budget Enforcement)
- FR-008 (Milestone Budget Check)
- FR-009 (OverbudgetCash Tracking)

**Story Count Estimate:** 7-10

**Priority:** Must Have

**Business Value:**
Core engine — đây là lý do tồn tại của budget system. Chặn overspend, phân bổ công bằng.

---

## User Stories (High-Level)

### EPIC-001: Budget Model & Configuration

- As an **admin**, I want to set Total Budget, User Cap, and Video Cap when creating an event so that I can control spending from the start.
- As an **admin**, I want to modify budget/cap on a running event so that I can adjust based on campaign performance, without losing tracking data.
- As an **admin**, I want bonus tracked separately from budget so that I can see actual reward spend vs bonus spend.
- As a **system**, I want to validate `VideoCap ≤ UserCap ≤ Total` so that invalid configurations are prevented.
- As a **system**, I want to fix the budget reset bug so that updating events doesn't lose spend tracking.
- As a **system**, I want to hide total event budget from public API so that brand budget information stays private.

### EPIC-002: Budget Enforcement Engine

- As a **system**, I want to cap each video's reward at VideoCap so that no single video consumes too much budget.
- As a **system**, I want to cap each creator's total reward at UserCap so that budget is distributed fairly.
- As a **system**, I want to block new rewards when event budget is exhausted so that spending never exceeds budget.
- As a **system**, I want to check budget using delta (cash increase) so that daily reward updates are accurately controlled.
- As a **system**, I want to check budget before creating milestone rewards so that milestones don't cause overspend.
- As a **system**, I want to track overbudgetCash so that admins can see actual performance beyond caps.
- As a **system**, I want to automatically unblock rewards when budget increases so that admin adjustments take effect immediately.

---

## User Personas

| Persona | Vai trò | Quan tâm |
|---------|---------|----------|
| **Admin/Staff** | Quản lý chiến dịch | Budget không bị vượt, tracking chính xác |
| **System** | Tự động enforce | Performance, atomic operations, backward compatible |

*Creator persona sẽ được define chi tiết trong V2 (UX).*

---

## Key User Flows

### Flow 1: Admin tạo event với budget
```
Admin → Tạo Event → Set Total=100tr, UserCap=5tr, VideoCap=2tr
  → Validation pass → Event created với BudgetInfo
```

### Flow 2: Reward bị cap tại 3 tầng
```
Crawl update video → Tính raw cash
  → Video Cap: min(cash, 2tr)
  → User Cap: delta check vs userRemain
  → Event Budget: delta check vs availableCash
  → Update reward với cash cuối cùng
```

### Flow 3: Event hết budget
```
Reward update → delta > availableCash
  → Chặn update, giữ cash cũ
  → Set IsBlockReward = true
  → Tất cả reward update sau đó bị skip
  → Admin tăng budget → IsBlockReward clear → tiếp tục
```

---

## Dependencies

### Internal Dependencies

| Dependency | Mô tả | Impact |
|------------|--------|--------|
| EventReward model | Thêm overbudgetCash field | Model change |
| BudgetInfo struct | Mở rộng fields | Model change |
| event_schema.go | Sửa UpdateRewardTypeByStatisticContent | Core logic change |
| event.go (admin) | Sửa Create/Update event | Admin API change |
| event.go (public) | Sửa response model | Public API change |

### External Dependencies

Không có external dependencies.

---

## Assumptions

1. TCB-style delta check đã proven ở production — approach tương tự sẽ hoạt động cho Ambassador
2. Crawl pipeline chạy tuần tự per content (không parallel) — race condition ở user cap thấp
3. Admin chấp nhận first-come-first-served khi budget gần hết (video crawl trước được ưu tiên)
4. `overbudgetCash` chỉ cần tracking, không cần hiển thị cho creator (V1)
5. Events hiện tại không có budget set → hoạt động như cũ sau deploy

---

## Out of Scope (V1)

| Item | Lý do | Khi nào |
|------|-------|---------|
| Admin budget dashboard/UI | V2 | PRD V2 |
| Creator budget progress UI | V2 | PRD V2 |
| Creator budget badges | V2 | PRD V2 |
| Threshold alerts (75%, 95%) | V2 | PRD V2 |
| Brand Budget (tầng trên Partner) | Phase 3 | Khi chuyển self-serve |
| Estimated view display | Phase 3 | Nice to have |
| Budget analytics/forecasting | Phase 3 | Nice to have |

---

## Open Questions

| # | Câu hỏi | Status | Quyết định |
|---|---------|--------|------------|
| 1 | Race condition khi nhiều video cùng user crawl đồng thời? | Resolved | Crawl thường sequential, chấp nhận risk thấp. Nếu cần → MongoDB atomic |
| 2 | Milestone có bị Video Cap không? | Resolved | KHÔNG — milestone không gắn video cụ thể, chỉ bị User Cap + Event Budget |
| 3 | Content chưa approved, reward status=WaitingApproved có tính vào cashValid? | Open | TCB tính vào → Ambassador nên giống? |
| 4 | Khi reject reward, refund tự động hay cần admin action? | Resolved | Tự động — cashValid tính real-time từ status |

---

## Approval & Sign-off

### Stakeholders

| Vai trò | Người | Trách nhiệm |
|---------|-------|-------------|
| Product Owner | vinhnguyen | Approve requirements |
| Engineering Lead | TBD | Approve technical feasibility |

### Approval Status

- [ ] Product Owner
- [ ] Engineering Lead

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-23 | vinhnguyen | Initial PRD V1 — Core Engine |

---

## Next Steps

### After V1 Approved:

1. **Architecture Design** — Run `/bmad:architecture` để design system chi tiết
2. **V2 PRD** — Admin/Creator UX (đã tạo song song)
3. **Sprint Planning** — Break stories, estimate, plan sprints

### Implementation Priority:

```
P0: FR-010 (Fix budget reset bug) — có thể deploy ngay
P0: FR-011 (Fix API leak) — có thể deploy ngay
P0: FR-001 (Model upgrade) → FR-005 → FR-006 → FR-007 (3 tầng enforcement)
P1: FR-003 (Bonus separation) → FR-008 (Milestone check) → FR-009 (OverbudgetCash)
P2: FR-004 (Partner validation enhance)
```

---

## Appendix A: Requirements Traceability Matrix

| Epic ID | Epic Name | Functional Requirements | Story Count (Est.) |
|---------|-----------|-------------------------|-------------------|
| EPIC-001 | Budget Model & Configuration | FR-001, FR-002, FR-003, FR-004, FR-010, FR-011 | 6-8 stories |
| EPIC-002 | Budget Enforcement Engine | FR-005, FR-006, FR-007, FR-008, FR-009 | 7-10 stories |

---

## Appendix B: Prioritization Details

### Functional Requirements

| Priority | Count | FRs |
|----------|-------|-----|
| Must Have | 9 | FR-001, FR-002, FR-003, FR-005, FR-006, FR-007, FR-008, FR-010, FR-011 |
| Should Have | 2 | FR-004, FR-009 |
| Could Have | 0 | — |

### Non-Functional Requirements

| Priority | Count | NFRs |
|----------|-------|------|
| Must Have | 6 | NFR-001, NFR-002, NFR-003, NFR-004, NFR-005, NFR-006 |

### Summary

- **Total FRs:** 11 (9 Must, 2 Should)
- **Total NFRs:** 6 (6 Must)
- **Total Epics:** 2
- **Estimated Stories:** 13-18

---

**This document was created using BMAD Method v6 - Phase 2 (Planning)**
