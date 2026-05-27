# Product Requirements Document: Bỏ lọc thống kê theo event ở API public `/events/statistic` (T-Fluencers)

**Date:** 2026-05-26
**Author:** vinhnguyen
**Version:** 1.0
**Project:** T-Fluencers (Techcombank)
**Project Type:** Bug-fix / Security hardening (backend-public)
**Project Level:** 1 (scope hẹp — 1 endpoint, ~1 epic)
**Status:** Draft

---

## Document Overview

PRD này định nghĩa yêu cầu chức năng và phi chức năng cho việc **gỡ bỏ khả năng lọc thống kê theo từng `event`** trên API public `GET /events/statistic` của T-Fluencers (Techcombank). Đây là source of truth cho phần "what" và "how-well"; phần "how" (kỹ thuật) đã có trong tech-spec đi kèm.

> T-Fluencers là fork của vcreator (vcreator gốc 2024-10, TCB fork 2025-10) — cùng lớp vấn đề với vcreator (Gen-Green) và Ambassador. Fix này nên được đồng bộ cả 3 sản phẩm.

**Related Documents:**
- Overview: [`overview.md`](./overview.md)
- Tech Spec: [`tech-spec.md`](./tech-spec.md)
- Bản cùng họ: [`../../gen-green/event-statistic-remove-event-filter/`](../../gen-green/event-statistic-remove-event-filter/), [`../../ambassador/event-statistic-remove-event-filter/`](../../ambassador/event-statistic-remove-event-filter/)
- Code reference (BE — `techcombank/backend`): `pkg/public/handler/event.go:152-174`, `pkg/public/service/event.go:288-363`, `pkg/public/router/event.go:22`

---

## Executive Summary

API public `GET /events/statistic` nhận query param `event` (Event ID) và `partner`, trả về thống kê **của riêng event đó**: số video được duyệt (`totalContent`), tổng view (`totalView`), tổng hoa hồng (`totalCommission`), số user có content (`totalUserWithContent`).

Endpoint này là **public** (route không có `RequiredLogin`; middleware `auth.Auth` chỉ parse JWT optional). Bất kỳ ai biết một `event_id` đều gọi được và đọc số liệu business chi tiết của campaign đó — có thể enumerate nhiều `event_id` để gom số liệu toàn bộ. Đây là **rò rỉ thông tin business nhạy cảm**.

Mục tiêu: gỡ tác dụng của param `event` ở endpoint public này → public user chỉ thấy số liệu tổng hợp (theo domain/partner), không suy ra được số của một event cụ thể. API admin (nội bộ, có auth) **không** thay đổi.

---

## Product Goals

### Business Objectives

1. **Bịt rò rỉ dữ liệu business nhạy cảm** — public user không xem được hoa hồng đã chi / độ phủ content theo từng thử thách chỉ bằng `event_id`.
2. **Không gây gián đoạn** — frontend T-Fluencers và đối tác hiện tại vẫn hoạt động bình thường; không cần deploy đồng bộ FE+BE.
3. **Giữ chi phí thay đổi ở mức tối thiểu** — thay đổi khu trú trong 1 handler, không phá vỡ struct/middleware dùng chung.

### Success Metrics

- Sau deploy: gọi `/events/statistic?event=<bất kỳ>` trả về **cùng** dữ liệu với gọi không có `event` (0% sai khác).
- 0 lỗi 4xx/5xx mới phát sinh trên endpoint sau deploy.
- Trang home T-Fluencers vẫn render block thống kê (0 báo lỗi).
- Endpoint `/events/user-newest` (dùng chung struct) không thay đổi hành vi.

---

## Functional Requirements

### FR-001: Gỡ filter `event` khỏi endpoint public `/events/statistic`

**Priority:** Must Have

**Description:**
Khi xử lý `GET /events/statistic`, hệ thống **không** được dùng query param `event` để giới hạn phạm vi thống kê. Kết quả trả về luôn là số liệu tổng hợp theo domain (và `partner` nếu có), bất kể client có gửi `event` hay không.

**Acceptance Criteria:**
- [ ] `GET /events/statistic?event=<ID hợp lệ>` trả về **cùng** payload với `GET /events/statistic` (không có `event`).
- [ ] Truyền `event` không làm thay đổi bất kỳ field nào trong response (`totalView`, `totalContent`, `totalCommission`, `totalEventActive`, `totalUserWithContent`).
- [ ] Truyền `event` sai định dạng / không tồn tại vẫn trả 200 với số liệu tổng hợp (không 400, không leak việc event có tồn tại hay không).

**Dependencies:** —

---

### FR-002: Giữ nguyên filter `partner`

**Priority:** Must Have

**Description:**
Param `partner` vẫn là filter hợp lệ. Endpoint phải tiếp tục trả về số liệu lọc theo partner khi `partner` được truyền.

**Acceptance Criteria:**
- [ ] `GET /events/statistic?partner=<X>` trả về số liệu tổng hợp **theo partner X**.
- [ ] `GET /events/statistic?event=<bất kỳ>&partner=<X>` cho kết quả giống `?partner=<X>` (event bị bỏ qua, partner còn tác dụng).

**Dependencies:** FR-001

---

### FR-003: Cache không phân mảnh / không trả số liệu theo-event

**Priority:** Must Have

**Description:**
Cache Redis của endpoint không còn key theo `event`. Sau deploy, cache cũ (đã chứa số liệu theo từng event) không được trả lại cho client. Cache key của T-Fluencers hiện theo `(event, partner)` → bỏ chiều `event`.

**Acceptance Criteria:**
- [ ] Cache key của statistic không chứa thành phần `event` (chỉ theo partner/domain).
- [ ] Sau deploy + purge/đổi format key: gọi với `event` khác nhau không trả về các entry cache khác nhau.
- [ ] Không có key cache cũ chứa số liệu theo-event được phục vụ quá thời điểm purge (TTL 30s).

**Dependencies:** FR-001

---

### FR-004: Không ảnh hưởng các caller dùng chung struct/validation

**Priority:** Must Have

**Description:**
Struct `request.EventStatistic` và middleware validation đang được route `GET /events/user-newest` dùng chung. Thay đổi không được làm hỏng các caller này. API admin cũng không bị đụng.

**Acceptance Criteria:**
- [ ] `GET /events/user-newest?event=<ID>` vẫn lọc danh sách user theo event như trước (hành vi không đổi).
- [ ] Struct `request.EventStatistic` không bị xóa field `Event`.
- [ ] API admin `/events/statistic` (backend-admin) không bị thay đổi — admin vẫn xem được thống kê theo event.

**Dependencies:** FR-001

---

## Non-Functional Requirements

### NFR-001: Security — Không leak thống kê theo event qua API public

**Priority:** Must Have

**Description:**
Public user (không bắt buộc login) không được suy ra số liệu thống kê của một event cụ thể từ `event_id`.

**Acceptance Criteria:**
- [ ] Không tồn tại tham số/đường nào trên endpoint public `/events/statistic` cho phép thu hẹp số liệu về 1 event.
- [ ] Phản hồi cho `event` hợp lệ và `event` không tồn tại là không phân biệt được.

**Rationale:** Số liệu theo từng thử thách (hoa hồng đã chi, độ phủ content) là thông tin business nhạy cảm — đây là mục tiêu chính của task.

---

### NFR-002: Backward Compatibility

**Priority:** Must Have

**Description:**
Client cũ tiếp tục gửi `?event=...` không được nhận lỗi; param chỉ bị bỏ qua. Không yêu cầu deploy đồng bộ FE+BE.

**Acceptance Criteria:**
- [ ] Request có `event` trả 200, không 4xx.
- [ ] Shape response `EventStatisticResponse` giữ nguyên (đủ 5 field, đúng kiểu).
- [ ] FE T-Fluencers hiện tại không cần sửa để hoạt động.

**Rationale:** Tránh downtime và phụ thuộc thứ tự deploy.

---

### NFR-003: Performance

**Priority:** Should Have

**Description:**
Bỏ filter event khiến query quét rộng hơn (toàn domain). Thời gian phản hồi phải nằm trong ngưỡng chấp nhận được nhờ cache.

**Acceptance Criteria:**
- [ ] P95 response time của `/events/statistic` < 1s sau thay đổi.
- [ ] Cache TTL (30s) tiếp tục hoạt động, giảm tải DB cho các call lặp.

**Rationale:** Không filter event → aggregate trên `event_analytic_daily` phạm vi lớn hơn; cần đảm bảo không gây chậm/đột biến tải DB.

---

### NFR-004: Maintainability — Thay đổi khu trú

**Priority:** Should Have

**Description:**
Thay đổi giới hạn trong handler `GetStatistic` (+ cache key), không sửa service logic hay struct dùng chung.

**Acceptance Criteria:**
- [ ] Service `GetStatistic` không phải sửa (dựa vào `AssignEvent` tự no-op khi `Event` rỗng).
- [ ] Diff không chạm `request.EventStatistic` / middleware validation.

**Rationale:** Giảm rủi ro vỡ `/user-newest` và dễ review.

---

## Epics

### EPIC-001: Siết quyền truy cập thống kê event trên API public (T-Fluencers)

**Description:**
Gỡ bỏ khả năng public user lọc/đọc thống kê theo từng event qua `GET /events/statistic`, đảm bảo không phá vỡ caller hiện hữu và đối tác.

**Functional Requirements:** FR-001, FR-002, FR-003, FR-004

**Story Count Estimate:** 2 stories

**Priority:** Must Have

**Business Value:**
Đóng lỗ rò rỉ dữ liệu business nhạy cảm với chi phí thay đổi tối thiểu và không gián đoạn người dùng.

---

## User Stories (High-Level)

### EPIC-001

- **STORY-1 (BE):** As a system owner, I want `/events/statistic` ignore param `event` so that public users cannot read per-campaign metrics from an event ID. (FR-001, FR-002, FR-003)
- **STORY-2 (Verify):** As a developer, I want regression checks on `/events/user-newest`, FE T-Fluencers, và admin statistic so that gỡ filter không phá vỡ caller hiện hữu. (FR-004, NFR-002)

> Chi tiết story chốt ở sprint planning (Phase 4). Tech-spec đã breakdown tương đương (STORY-1, ~1.5-2h).

---

## User Personas

- **Public user / Influencer (chưa login hoặc đã login):** xem block thống kê tổng hợp ở trang home T-Fluencers. Không được phép xem số liệu của 1 thử thách cụ thể.
- **Đối tác (partner):** gọi qua `partner` filter, xem số liệu theo partner mình. Hành vi giữ nguyên.
- **Admin nội bộ (Techcombank):** dùng API admin (có auth) để xem thống kê chi tiết theo thử thách. Không bị ảnh hưởng.

---

## User Flows

1. **Influencer vào trang home** → FE gọi statistic (domain/partner) → BE trả số liệu tổng hợp → render block thống kê.
2. **Kẻ tấn công thử `?event=<ID>`** → BE bỏ qua `event` → trả số tổng hợp giống mọi người → không lấy được số riêng của thử thách đó.
3. **Admin xem báo cáo thử thách** → dùng API admin (ngoài phạm vi PRD) → vẫn xem chi tiết theo event.

---

## Dependencies

### Internal Dependencies

- Hàm `CommonQuery.AssignEvent` (`internal/util/mgquery/common.go`) — đã no-op khi `Event` rỗng (dựa vào đây để không sửa service).
- Struct `request.EventStatistic` + middleware validation — **dùng chung** với `/events/user-newest`; không được xóa/sửa.
- Redis cache key statistic (`internal/module/redis/key.go`, `GetKeyCacheStatisticEvent`) — cần đổi format/purge.

### External Dependencies

- Không có.

---

## Assumptions

- Cần **verify FE T-Fluencers** không truyền `event` lên `/events/statistic` (tham chiếu vcreator: cả 2 FE vcreator đã verify KHÔNG truyền `event`; T-Fluencers cùng dòng FE nên nhiều khả năng tương tự).
- Không có đối tác bên ngoài đang phụ thuộc hợp pháp vào số liệu theo-event ở endpoint public; nếu có, họ chuyển sang API admin có auth.
- TTL cache 30s đủ ngắn để tác động của cache cũ không đáng kể nếu không kịp purge.

---

## Out of Scope

- Thay đổi API admin `/events/statistic` (backend-admin) — admin vẫn xem chi tiết theo event.
- Xóa struct `request.EventStatistic` hoặc middleware validation chung.
- Thêm yêu cầu login/auth mới cho endpoint public.
- Audit/siết các endpoint public khác (`/leaderboards`, `/:id/content`, `/user-newest`...).
- Đổi shape response `EventStatisticResponse`.

---

## Open Questions

1. Xử lý cache cũ: **đổi format key** (sạch hơn) hay **flush key prefix statistic** sau deploy?
2. Có cần verify lại FE T-Fluencers trên staging trước prod không (phòng FE ngầm dùng `event`)?
3. Đồng bộ fix sang vcreator & ambassador trong cùng đợt?

---

## Approval & Sign-off

### Stakeholders

- vinhnguyen (Author / PM)
- Tech Lead T-Fluencers
- (Optional) Ops/Đối tác

### Approval Status

- [ ] Product Owner
- [ ] Engineering Lead
- [ ] Design Lead (N/A — không có thay đổi UI)
- [ ] QA Lead

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-26 | vinhnguyen | Initial PRD |

---

## Next Steps

### Phase 3: Architecture
Scope hẹp — không cần architecture workflow đầy đủ. Tech-spec ([`tech-spec.md`](./tech-spec.md)) đã đóng vai trò thiết kế kỹ thuật.

### Phase 4: Sprint Planning
Chạy `/bmad:create-story` hoặc dùng trực tiếp STORY-1 trong tech-spec để implement (~1.5-2h).

---

## Appendix A: Requirements Traceability Matrix

| Epic ID | Epic Name | Functional Requirements | Story Count (Est.) |
|---------|-----------|-------------------------|--------------------|
| EPIC-001 | Siết quyền truy cập thống kê event trên API public (T-Fluencers) | FR-001, FR-002, FR-003, FR-004 | 2 stories |

---

## Appendix B: Prioritization Details

**Functional Requirements:** 4 tổng (4 Must Have, 0 Should, 0 Could)
**Non-Functional Requirements:** 4 tổng (2 Must Have, 2 Should Have)

Toàn bộ FR là Must Have vì là thay đổi nguyên khối: bỏ filter event mà không bịt cache hoặc làm vỡ `/user-newest` thì không đạt mục tiêu bảo mật. NFR performance & maintainability ở mức Should.
