# Product Requirements Document: Budget System V2 — Admin & Creator Experience

**Date:** 2026-03-23
**Author:** vinhnguyen
**Version:** 1.0
**Project Type:** Feature Enhancement
**Project Level:** 2
**Status:** Draft
**Prerequisite:** PRD V1 (Budget System Core Engine) phải hoàn thành trước

---

## Document Overview

PRD này định nghĩa requirements cho **V2 — Admin & Creator Experience**: hiển thị budget cho admin, trải nghiệm creator (progress bar, badges, per-video breakdown), và threshold alerts. V2 xây dựng trên V1 Core Engine đã deploy.

**Related Documents:**
- [PRD V1: Budget System Core Engine](prd-budget-system-v1-2026-03-23.md)
- [Brainstorming: Budget System](brainstorming-budget-system-2026-03-16.md)
- [Overview: Budget System](overview-budget-system.md)
- [Reward Flow Analysis](reward-flow-analysis.md)

---

## Executive Summary

V1 đã enforce budget ở backend — reward bị chặn khi vượt cap/budget. V2 bổ sung **trải nghiệm người dùng**: admin theo dõi budget realtime với breakdown chi tiết, creator thấy rõ cap cá nhân + progress + per-video breakdown, và hệ thống alert tự động khi budget gần hết.

---

## Product Goals

### Business Objectives

1. **Admin visibility** — Admin thấy rõ budget status, breakdown reward vs bonus, biết khi nào cần tăng budget
2. **Creator transparency** — Creator biết cap cá nhân, biết còn kiếm được bao nhiêu, biết tại sao bị chặn
3. **Proactive alerts** — Admin nhận cảnh báo sớm (75%, 95%) để kịp điều chỉnh

### Success Metrics

| Metric | Target | Cách đo |
|--------|--------|---------|
| Admin phát hiện budget cạn trước 100% | > 80% events | Admin thấy warning ở 75%/95% trước khi hết |
| Creator support tickets về reward | Giảm 50% | So sánh trước/sau deploy |
| Creator hiểu lý do bị chặn | > 90% | UI hiển thị rõ ràng, không cần hỏi support |

---

## Functional Requirements

### FR-012: Admin Budget Dashboard

**Priority:** Must Have

**Description:**
Admin thấy budget breakdown chi tiết trên trang chi tiết event: Total, Used (reward), BonusUsed (tách riêng), Remain, UserCap, VideoCap, trạng thái (Còn/Gần hết/Hết), và Exhausted flag.

**Acceptance Criteria:**
- [ ] Event detail hiển thị: Total, Used, BonusUsed, Remain, UsedPercent
- [ ] Hiển thị UserCap, VideoCap đã set
- [ ] Progress bar budget (visual)
- [ ] Trạng thái rõ ràng: "Còn ngân sách" / "Gần hết (>75%)" / "Đã hết"
- [ ] Hiển thị `IsBlockReward` status

**Dependencies:** V1 FR-001 (BudgetInfo model)

---

### FR-013: Admin Event List Budget Badge

**Priority:** Should Have

**Description:**
Trang danh sách events hiển thị badge trạng thái budget nhanh để admin scan được.

**Acceptance Criteria:**
- [ ] Badge trên mỗi event card/row: Còn (xanh) / Gần hết (vàng, >75%) / Đã hết (đỏ)
- [ ] Events không set budget: không hiện badge
- [ ] Sort/filter theo budget status

**Dependencies:** V1 FR-001

---

### FR-014: Threshold Alerts

**Priority:** Should Have

**Description:**
Hệ thống tự động gửi notification cho admin khi event budget đạt các ngưỡng: 75% (warning), 95% (urgent), 100% (exhausted). Mỗi ngưỡng chỉ trigger 1 lần (one-shot).

**Acceptance Criteria:**
- [ ] 75% budget used → notification "Ngân sách chiến dịch X đã sử dụng 75%"
- [ ] 95% budget used → notification urgent "Ngân sách chiến dịch X sắp hết (95%)"
- [ ] 100% budget used → notification "Ngân sách chiến dịch X đã hết, reward đã bị chặn"
- [ ] Mỗi ngưỡng chỉ trigger 1 lần per event (flag `alert_75_sent`, `alert_95_sent`, `alert_100_sent`)
- [ ] Notification qua in-app notification center
- [ ] Admin tăng budget → reset alert flags cho các ngưỡng chưa đạt lại

**Dependencies:** V1 FR-007 (Event Budget Enforcement)

---

### FR-015: ChangeStatusItem Budget Check

**Priority:** Must Have

**Description:**
Khi admin manually approve reconciliation item qua `ChangeStatusItem`, hệ thống check budget trước. Hiển thị warning nếu approve sẽ vượt budget.

**Acceptance Criteria:**
- [ ] Admin approve item → check: `cashValid + itemCash ≤ eventBudget`
- [ ] Nếu vượt → hiển thị warning "Approve item này sẽ vượt ngân sách X%"
- [ ] Admin có thể override warning (confirm approve)
- [ ] Bonus items: skip budget check, luôn cho approve

**Dependencies:** V1 FR-007

---

### FR-016: Creator Budget Progress API

**Priority:** Must Have

**Description:**
Public API trả về thông tin budget cá nhân cho creator: user cap, video cap, tiến trình cá nhân, per-video breakdown. KHÔNG expose tổng budget event.

**Acceptance Criteria:**
- [ ] Response chứa: `userCap`, `userEarned`, `userRemain`, `userCapReached`
- [ ] Response chứa: `videoCap` (giá trị chung, không per-video)
- [ ] Response chứa: per-video breakdown (danh sách video + earned + capReached per video)
- [ ] Response chứa: `bonusEarned` (tách riêng)
- [ ] Response chứa: `eventBudgetExhausted` (boolean — event hết ngân sách hay chưa)
- [ ] KHÔNG chứa: `eventBudgetTotal`, `eventBudgetUsed`, `eventBudgetRemain`
- [ ] KHÔNG chứa: earning của creator khác
- [ ] Endpoint: mở rộng event detail hoặc endpoint mới `/events/{id}/my-budget`

**Dependencies:** V1 FR-001, V1 FR-011 (Fix API leak)

---

### FR-017: Creator Budget Progress UI

**Priority:** Should Have

**Description:**
Frontend hiển thị budget progress cho creator trên trang chi tiết chiến dịch: progress bar, per-video breakdown, bonus tách riêng, trạng thái rõ ràng.

**Acceptance Criteria:**
- [ ] Progress bar: "Đã nhận: X / Tối đa: Y" (user cap)
- [ ] Per-video breakdown: danh sách video + số tiền đã nhận + trạng thái
- [ ] Video status badges: Còn slot / Đạt tối đa (video cap) / User cap hết / Event hết
- [ ] Bonus hiển thị tách: "Bonus (không tính vào giới hạn): +Z"
- [ ] Khi chạm user cap: "Bạn đã đạt mức hoa hồng tối đa cho chiến dịch này"
- [ ] Khi event hết: "Chiến dịch đã hết ngân sách. Bài đã đăng trước đó vẫn được thanh toán đầy đủ."
- [ ] Không set cap: không hiển thị phần cap tương ứng

**Dependencies:** FR-016 (API)

---

### FR-018: Creator Event Listing Badges

**Priority:** Should Have

**Description:**
Badge trạng thái trên danh sách chiến dịch để creator biết trước khi click vào.

**Acceptance Criteria:**
- [ ] Badge "Còn" (xanh): creator chưa chạm cap, event còn budget
- [ ] Badge "Đã đạt tối đa" (vàng): creator đã chạm user cap
- [ ] Badge "Hết ngân sách" (đỏ): event budget đã hết
- [ ] Events không set budget: không hiện badge

**Dependencies:** FR-016 (API)

---

### FR-019: Creator Earnings Page Enhancement

**Priority:** Could Have

**Description:**
Trang tổng quan earnings của creator across events, phân biệt hoa hồng vs bonus, trạng thái per event.

**Acceptance Criteria:**
- [ ] Bảng: Event name | Hoa hồng | Cap | Trạng thái
- [ ] Tổng hoa hồng + Tổng bonus (tách riêng)
- [ ] Trạng thái per event: Còn / Đã đạt cap / Hết ngân sách

**Dependencies:** FR-016 (API)

---

## Non-Functional Requirements

### NFR-007: Creator API Privacy

**Priority:** Must Have

**Description:**
Creator không thể truy cập tổng budget event qua bất kỳ API endpoint nào.

**Acceptance Criteria:**
- [ ] Không có endpoint nào return `eventBudgetTotal` hoặc `eventBudgetRemain` cho public role
- [ ] Penetration test: creator role không thể query budget thông tin nhạy cảm

**Rationale:**
Tổng ngân sách chiến dịch là thông tin nhạy cảm của brand. Creator biết → ảnh hưởng đàm phán, mất niềm tin.

---

### NFR-008: Creator UI Response Time

**Priority:** Should Have

**Description:**
Budget progress data cho creator phải load nhanh trên mobile.

**Acceptance Criteria:**
- [ ] Budget progress API < 200ms (P95)
- [ ] Per-video breakdown cho event có tới 50 videos: < 300ms

**Rationale:**
Creator chủ yếu dùng mobile. API chậm → UX kém → creator không check trước khi đăng bài.

---

## Epics

### EPIC-003: Admin Budget Experience

**Description:**
Admin thấy budget status realtime trên event detail và event list. Threshold alerts notification tự động. Budget check khi approve thủ công.

**Functional Requirements:**
- FR-012 (Admin Budget Dashboard)
- FR-013 (Admin Event List Badge)
- FR-014 (Threshold Alerts)
- FR-015 (ChangeStatusItem Budget Check)

**Story Count Estimate:** 5-7

**Priority:** Must Have (FR-012, FR-015) + Should Have (FR-013, FR-014)

**Business Value:**
Admin cần visibility để quản lý chiến dịch hiệu quả. Không có dashboard → admin không biết budget đang ở đâu cho đến khi hết.

---

### EPIC-004: Creator Budget Transparency

**Description:**
Creator thấy budget cap cá nhân, progress, per-video breakdown, và trạng thái rõ ràng. Creator biết TRƯỚC khi đăng bài là còn kiếm được hay không.

**Functional Requirements:**
- FR-016 (Creator Budget Progress API)
- FR-017 (Creator Budget Progress UI)
- FR-018 (Creator Event Listing Badges)
- FR-019 (Creator Earnings Page Enhancement)

**Story Count Estimate:** 5-8

**Priority:** Must Have (FR-016) + Should Have (FR-017, FR-018) + Could Have (FR-019)

**Business Value:**
Creator transparency giảm support tickets, tăng trust. Creator biết cap → chiến lược đăng bài thông minh hơn (nhiều video thay vì 1 video viral).

---

## User Stories (High-Level)

### EPIC-003: Admin Budget Experience

- As an **admin**, I want to see budget breakdown (reward vs bonus) on event detail so that I know exactly how budget is being spent.
- As an **admin**, I want to see budget status badges on event list so that I can quickly identify events that need attention.
- As an **admin**, I want to receive alerts when budget reaches 75%/95%/100% so that I can proactively adjust.
- As an **admin**, I want a budget warning when manually approving reconciliation items so that I don't accidentally overspend.

### EPIC-004: Creator Budget Transparency

- As a **creator**, I want to see my personal cap and progress on event detail page so that I know how much more I can earn.
- As a **creator**, I want to see per-video breakdown so that I can optimize which videos to promote.
- As a **creator**, I want clear status badges on event listing so that I know before clicking which events still have budget.
- As a **creator**, I want to understand why my reward was blocked so that I don't blame the platform.
- As a **creator**, I want to see bonus separately from reward so that I know my true earning breakdown.

---

## User Personas

| Persona | Vai trò | Quan tâm | Platform |
|---------|---------|----------|----------|
| **Admin/Staff** | Quản lý chiến dịch | Budget overview, proactive alerts, approve control | Web (admin panel) |
| **Creator** | Đăng bài, kiếm hoa hồng | Cap cá nhân, còn kiếm được không, tại sao bị chặn | Mobile + Web |
| **Brand** (indirect) | Đối tác chiến dịch | Budget không bị lộ cho creator, chi tiêu hợp lý | Không trực tiếp dùng |

---

## Key User Flows

### Flow 1: Admin theo dõi budget chiến dịch
```
Admin → Event List → Thấy badge "Gần hết" (vàng) trên Event X
  → Click vào Event X → Thấy dashboard:
    Total: 100tr | Used: 78tr | Bonus: 12tr | Remain: 22tr
    Progress bar 78%
    UserCap: 5tr | VideoCap: 2tr
  → Nhận notification "Event X đã sử dụng 75% ngân sách"
  → Quyết định tăng budget hoặc chờ
```

### Flow 2: Creator check budget trước khi đăng bài
```
Creator → Event Detail → Thấy:
  "Hoa hồng của bạn"
  Tối đa mỗi chiến dịch: 5,000,000 VND
  Tối đa mỗi video: 2,000,000 VND
  ████████████░░░░░░░░  60%
  Đã nhận: 3,000,000 VND (2 video)
  Còn lại: 2,000,000 VND
  Bonus: +500,000 VND
  → Creator biết còn kiếm được 2tr → đăng thêm video
```

### Flow 3: Creator thấy chiến dịch hết budget
```
Creator → Event Listing → Thấy badge "Hết ngân sách" (đỏ)
  → Click vào → Thấy:
    "Chiến dịch đã hết ngân sách"
    "Bài đã đăng trước đó vẫn được thanh toán đầy đủ."
  → Creator hiểu, không submit thêm bài
```

---

## Dependencies

### Internal Dependencies

| Dependency | Mô tả | Impact |
|------------|--------|--------|
| **V1 Core Engine (PHẢI deploy trước)** | Budget model, enforcement logic | V2 build on top of V1 |
| Admin panel (React/Next.js) | Frontend thay đổi | Admin UI |
| Public app (Frontend) | Frontend thay đổi | Creator UI |
| Notification service | In-app notification | Threshold alerts |

### External Dependencies

Không có external dependencies.

---

## Assumptions

1. V1 Core Engine đã deploy và stable trước khi bắt đầu V2
2. Admin panel có component library để render progress bar, badges
3. Public app hỗ trợ hiển thị per-video breakdown (có thể cần new component)
4. Creator chủ yếu xem trên mobile → UI cần responsive
5. Notification service hiện có đủ để gửi threshold alerts

---

## Out of Scope (V2)

| Item | Lý do | Khi nào |
|------|-------|---------|
| Brand Budget (tầng trên Partner) | Phase 3 | Khi chuyển self-serve |
| Estimated view display (budget / CPV) | Phase 3 | Nice to have |
| Budget analytics/forecasting/burn rate | Phase 3 | Nice to have |
| Push notification cho creator khi chạm cap | Phase 3 | Hiện chỉ cần UI status |
| Email alert cho admin | Phase 3 | Hiện chỉ cần in-app notification |
| Export budget report cho brand | Phase 3 | Reconciliation report |

---

## Open Questions

| # | Câu hỏi | Status | Quyết định |
|---|---------|--------|------------|
| 1 | ChangeStatusItem override: admin có nên được phép approve vượt budget không? | Open | Đề xuất: cho phép với warning + confirm |
| 2 | Threshold alerts gửi qua channel nào? | Open | Đề xuất: In-app notification (phase 1), email (phase 2) |
| 3 | Creator có cần notification khi reward bị chặn vì budget? | Open | Đề xuất: V2 chỉ UI status, notification là phase sau |

---

## Approval & Sign-off

### Stakeholders

| Vai trò | Người | Trách nhiệm |
|---------|-------|-------------|
| Product Owner | vinhnguyen | Approve requirements |
| Engineering Lead | TBD | Approve technical feasibility |
| Design Lead | TBD | Approve UX flows & mockups |

### Approval Status

- [ ] Product Owner
- [ ] Engineering Lead
- [ ] Design Lead

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-23 | vinhnguyen | Initial PRD V2 — Admin & Creator Experience |

---

## Next Steps

### After V2 Approved:

1. **UX Design** — Run `/bmad:create-ux-design` cho creator budget UI (đã có mockups trong brainstorming)
2. **Architecture Design** — Extend V1 architecture cho API endpoints mới
3. **Sprint Planning** — Break stories, plan sprints (V2 có thể chạy song song với V1 ở phần API)

---

## Appendix A: Requirements Traceability Matrix

| Epic ID | Epic Name | Functional Requirements | Story Count (Est.) |
|---------|-----------|-------------------------|-------------------|
| EPIC-003 | Admin Budget Experience | FR-012, FR-013, FR-014, FR-015 | 5-7 stories |
| EPIC-004 | Creator Budget Transparency | FR-016, FR-017, FR-018, FR-019 | 5-8 stories |

---

## Appendix B: Prioritization Details

### Functional Requirements

| Priority | Count | FRs |
|----------|-------|-----|
| Must Have | 3 | FR-012, FR-015, FR-016 |
| Should Have | 4 | FR-013, FR-014, FR-017, FR-018 |
| Could Have | 1 | FR-019 |

### Non-Functional Requirements

| Priority | Count | NFRs |
|----------|-------|------|
| Must Have | 1 | NFR-007 |
| Should Have | 1 | NFR-008 |

### Summary

- **Total FRs:** 8 (3 Must, 4 Should, 1 Could)
- **Total NFRs:** 2 (1 Must, 1 Should)
- **Total Epics:** 2
- **Estimated Stories:** 10-15

---

## Appendix C: Creator UI Mockups (từ Brainstorming)

> Chi tiết mockups xem tại [brainstorming-budget-system-2026-03-16.md](brainstorming-budget-system-2026-03-16.md) — Category 8: Creator Budget Communication

### Tóm tắt 4 trạng thái UI:

| Trạng thái | Hiển thị |
|------------|----------|
| Còn budget, chưa chạm cap | Progress bar + "Đã nhận: X / Tối đa: Y" + per-video list |
| Gần chạm user cap (≥80%) | Warning banner "Bạn sắp đạt mức hoa hồng tối đa" |
| Đã chạm user cap | "Bạn đã đạt mức hoa hồng tối đa. Bài mới sẽ không được tính hoa hồng." |
| Event budget đã hết | "Chiến dịch đã hết ngân sách. Bài đã đăng vẫn được thanh toán." |

### Quy tắc bảo mật hiển thị:

| Dữ liệu | Creator thấy | Creator KHÔNG thấy |
|----------|-------------|-------------------|
| User cap + progress | ✅ | — |
| Video cap + per-video earned | ✅ | — |
| Bonus (tách riêng) | ✅ | — |
| Tổng budget event | ❌ | Không hiển thị |
| Budget còn lại event | ❌ | Không hiển thị |
| Earning creator khác | ❌ | Không hiển thị |

---

**This document was created using BMAD Method v6 - Phase 2 (Planning)**
