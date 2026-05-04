# Product Requirements Document: Affiliate Admin Setup — Gen-Green

**Date:** 2026-05-04
**Author:** vinhnguyen
**Version:** 1.0
**Project Type:** Feature Integration
**Project Level:** Level 2
**Status:** Draft
**Platform:** Gen-Green (`accesstrade-projects/vcreator/`)

---

## Document Overview

PRD này định nghĩa requirements cho **Admin Setup** — phần back-office của tích hợp affiliate trên Gen-Green, cho phép admin tạo và quản lý affiliate campaigns local + liên kết với Event hiện có.

**Related Documents:**
- Overview: [admin-setup-overview.md](admin-setup-overview.md)
- Reference Ambassador V1: [`pub2-affiliate-integration/prd-affiliate-v1-2026-03-31.md`](../../pub2-affiliate-integration/prd-affiliate-v1-2026-03-31.md) — FR-001, FR-002, FR-003, FR-015
- API Integration (next): [api-integration-overview.md](api-integration-overview.md)
- FE Display (next): [fe-display-generate-link-report-overview.md](fe-display-generate-link-report-overview.md)

---

## Executive Summary

Gen-Green hiện có hệ thống Event nội bộ. Admin Setup bổ sung **affiliate campaigns** — đối tượng mới được **liên kết (mapping) với Event hiện có**, không đứng riêng lẻ.

**Concept chính:** Affiliate campaign được gắn vào Event qua bảng quan hệ many-to-many. Admin tự tạo affiliate campaigns và liên kết với Event.

Admin sẽ:
1. Tạo affiliate campaign với thông tin nội bộ (title, banner, hoa hồng, thưởng thêm) + thông tin Scalef (`scalef_campaign_id`, `scalef_campaign_url`)
2. Quản lý danh sách affiliate campaigns (search, filter)
3. Liên kết affiliate campaign với 1 hoặc nhiều Event hiện có (cùng partner)
4. Activate/deactivate để control visibility cho creator

**Điểm quan trọng:**
- **Track độc lập** — không phụ thuộc Scalef account-linking phase, không phụ thuộc Scalef API client. Có thể start sớm nhất.
- **Affiliate campaign gắn vào Event** qua bảng mapping `campaign_affiliate_mappings`
- **Status mặc định là `inactive`** — admin chủ động activate sau khi review
- **Partner immutable** sau khi tạo (giống Event)
- **Chỉ liên kết được Event cùng partner** — filter theo partner của affiliate campaign
- Admin không cần quan tâm Scalef credentials — chỉ nhập `scalef_campaign_id` và `scalef_campaign_url`

---

## Product Goals

### Business Objectives

1. **Cho phép admin chuẩn bị catalog affiliate** trước khi creator-facing flow go-live, đảm bảo creator vào ngày đầu tiên đã có content
2. **Gatekeeping chất lượng:** Admin chọn lọc thủ công, không auto-sync mọi campaign từ Scalef. Loại bỏ campaign đối thủ, chỉ giữ campaign phù hợp khán giả Gen-Green
3. **Việt hóa nội dung:** Admin viết description tiếng Việt phù hợp creator Gen-Green, không lệ thuộc nội dung gốc Scalef
4. **Tách rời lifecycle:** Admin có thể deactivate affiliate khi cần (campaign hết hạn, partner kết thúc, vi phạm) mà không ảnh hưởng Event đang chạy

### Success Metrics

| Metric | Target | Timeframe |
|--------|--------|-----------|
| Số affiliate campaign active sẵn sàng trước launch | ≥ 20 | Trước launch creator |
| Tỉ lệ Event có ít nhất 1 affiliate mapping | 30% | 1 tháng sau launch |
| Thời gian admin tạo 1 campaign mới | < 5 phút | — |

---

## Functional Requirements

Functional Requirements (FRs) define **what** the system does - specific features and behaviors.

Each requirement includes:
- **ID**: Unique identifier (FR-001, FR-002, etc.)
- **Priority**: Must Have / Should Have / Could Have (MoSCoW)
- **Description**: What the system should do
- **Acceptance Criteria**: How to verify it's complete

---

### FR-001: Admin tạo Affiliate Campaign

**Priority:** Must Have

**Description:**
Admin tạo affiliate campaign mới trên Gen-Green Admin panel. Campaign bao gồm thông tin nội bộ (title, description, banner, commission info) và liên kết với Scalef qua `scalef_campaign_id`.

**Acceptance Criteria:**
- [ ] **Authorization:** Chỉ Root + Admin có quyền tạo / sửa / đổi status. Collaborator gọi API mutation → 403. Admin có `staff.partner` set: chỉ tạo được campaign cho partner mình (BE force `campaign.partner = staff.partner`, ignore client value). Admin không partner + Root: tự chọn partner trong dropdown.
- [ ] Admin có thể tạo affiliate campaign với các trường: partner (required), title, description, short_desc (mô tả ngắn, hiển thị trên card listing và trang chi tiết thay cho desc), banner image (required), commission info (required), bonus_info, scalef_campaign_id, scalef_campaign_url (required), start_date, end_date
- [ ] **Partner là required khi tạo và immutable sau khi tạo** (giống event). Root staff chọn partner trong dropdown; Admin có `partner` set thì tự auto-fill `staff.partner` (immutable, không hiển thị dropdown)
- [ ] **Status mặc định là `inactive` khi tạo** — admin không chọn status lúc tạo, chỉ thay đổi sau khi tạo
- [ ] Admin có thể chỉnh sửa và cập nhật campaign (trừ partner)
- [ ] Admin có thể thay đổi status: active / inactive
- [ ] Validate `scalef_campaign_id` là required và không trùng lặp
- [ ] Validate `scalef_campaign_url` là URL hợp lệ
- [ ] Validate `start_date < end_date` nếu cả 2 cùng có giá trị
- [ ] Campaign chỉ hiển thị cho creator khi `status=active` **và** (chưa qua `end_date` hoặc `end_date` rỗng) — logic ẩn theo end_date xử lý ở query layer (FE Display + API Integration), không tự động đổi status
- [ ] Khi campaign đã qua `end_date`, badge "Hết hạn" hiển thị trong admin list để admin biết

**Dependencies:** None

---

### FR-002: Admin quản lý danh sách Affiliate Campaigns

**Priority:** Must Have

**Description:**
Admin xem, tìm kiếm, lọc và quản lý danh sách affiliate campaigns đã tạo.

**Acceptance Criteria:**
- [ ] **Authorization:** Root + Admin + Collaborator đều xem được. Admin có `staff.partner` set: BE auto-filter list chỉ trả campaign cùng partner. Root: thấy tất cả. Collaborator: read-only, không thấy nút edit/toggle status.
- [ ] Hiển thị danh sách campaigns với: banner thumbnail, title, status, partner, commission, ngày tạo
- [ ] Lọc theo status (active / inactive / all)
- [ ] Lọc theo partner (Root only — Admin có partner thì auto-filter theo `staff.partner`)
- [ ] Tìm kiếm theo title (partial match, case-insensitive)
- [ ] Sắp xếp theo ngày tạo (default desc), title, end_date
- [ ] Pagination 20 items/page
- [ ] Hiển thị số lượng Event đã mapping cho mỗi campaign (preview)
- [ ] Empty state khi chưa có campaign nào

**Dependencies:** FR-001

---

### FR-003: Admin liên kết Affiliate Campaign với Event

**Priority:** Must Have

**Description:**
Admin liên kết (mapping) một affiliate campaign với một hoặc nhiều Event hiện có của Gen-Green. Đây là bảng quan hệ giữa 2 đối tượng: Event ↔ Affiliate Campaign.

**Acceptance Criteria:**
- [ ] **Authorization:** Chỉ Root + Admin có quyền link / unlink. Collaborator → 403 trên mutation, được xem list mapping. Admin có `staff.partner`: chỉ link/unlink được mapping mà cả `affiliate_campaign.partner` và `event.partner` đều khớp `staff.partner`. Vi phạm → 403.
- [ ] Admin có thể liên kết 1 affiliate campaign với 1 hoặc nhiều Events
- [ ] Admin có thể liên kết 1 Event với 1 hoặc nhiều affiliate campaigns
- [ ] **Chỉ hiển thị Events cùng partner** khi liên kết — event search được filter theo partner của affiliate campaign
- [ ] Quan hệ many-to-many: bảng mapping `campaign_affiliate_mappings` với `event_id` + `affiliate_campaign_id`
- [ ] Admin có thể gỡ liên kết (unlink) với confirm modal
- [ ] Hiển thị danh sách Events đã liên kết trong trang chi tiết affiliate campaign — bao gồm tên event, trạng thái, ngày liên kết
- [ ] Hiển thị danh sách affiliate campaigns đã liên kết trong trang chi tiết Event (admin)
- [ ] Event search autocomplete với debounce 300ms khi liên kết
- [ ] Không cho mapping trùng (unique compound `(event_id, affiliate_campaign_id)`)
- [ ] BE verify `event.partner == affiliate_campaign.partner` trước khi insert

**Dependencies:** FR-001

---

### FR-004: Backend Affiliate Campaign CRUD APIs

**Priority:** Must Have

**Description:**
Backend APIs cho Admin CRUD affiliate campaigns + mapping, lưu trong MongoDB.

**Acceptance Criteria:**
- [ ] **Authorization** (cột "Middleware" sử dụng pattern `routeauth.Auth()` ở `pkg/admin/router/routeauth/auth.go`):

| Endpoint | Method | Middleware | Mục đích |
|----------|--------|------------|----------|
| `/admin/affiliate-campaigns` | POST | `a.IsAdmin` | Tạo campaign |
| `/admin/affiliate-campaigns` | GET | `a.IsCollaborator` | List campaigns (filter status, partner, search, pagination) |
| `/admin/affiliate-campaigns/:id` | GET | `a.IsCollaborator` | Detail + events đã mapping |
| `/admin/affiliate-campaigns/:id` | PUT | `a.IsAdmin` | Update campaign (trừ partner) |
| `/admin/affiliate-campaigns/:id/status` | PATCH | `a.IsAdmin` | Đổi status active/inactive |
| `/admin/affiliate-campaigns/:id/events` | POST | `a.IsAdmin` | Link với event |
| `/admin/affiliate-campaigns/:id/events/:eventId` | DELETE | `a.IsAdmin` | Unlink |
| `/admin/affiliate-campaigns/:id/events` | GET | `a.IsCollaborator` | List events đã link |
| `/admin/events/:eventId/affiliate-campaigns` | GET | `a.IsCollaborator` | Reverse: list affiliate đã link với event |

- [ ] Tenant isolation: BE filter mọi query theo `staff.partner` cho non-root staff (Admin/Collaborator có partner). Root thấy tất cả.
- [ ] Validate: scalef_campaign_id unique, required fields, partner required + immutable, mapping cùng partner
- [ ] Response trả error message tiếng Việt thân thiện cho UI hiển thị

**Dependencies:** FR-001, FR-002, FR-003

---

### FR-005: Search & Autocomplete Event khi liên kết

**Priority:** Must Have

**Description:**
Khi admin link Event với affiliate campaign, cần search box autocomplete để tìm Event nhanh.

**Acceptance Criteria:**
- [ ] **Authorization:** Chỉ Root + Admin có quyền search Event để link (vì search này phục vụ link/unlink action — Collaborator không cần). Endpoint dùng middleware `a.IsAdmin`.
- [ ] Search box trong link-event modal
- [ ] Debounce 300ms trước khi gửi request
- [ ] Filter: chỉ Event có `partner == affiliate_campaign.partner`
- [ ] Filter: loại bỏ Event đã link với campaign này (tránh duplicate)
- [ ] Hiển thị dropdown kết quả: tên Event, status, start_date, end_date
- [ ] Hỗ trợ chọn nhiều (multi-select) trong cùng 1 lần thao tác
- [ ] Empty state: "Không tìm thấy Event phù hợp"
- [ ] Limit 20 kết quả mỗi query

**Dependencies:** FR-003

---

## Non-Functional Requirements

Non-Functional Requirements (NFRs) define **how** the system performs - quality attributes and constraints.

---

### NFR-001: Performance — API Response Time

**Priority:** Must Have

**Description:**
Admin APIs phải đảm bảo response time đủ nhanh để không cản trở vận hành.

**Acceptance Criteria:**
- [ ] CRUD APIs (single record): p95 < 200ms
- [ ] List với filter + pagination: p95 < 300ms
- [ ] Event autocomplete search: p95 < 200ms

**Rationale:**
Admin team thao tác nhiều campaign mỗi ngày, latency cao sẽ ảnh hưởng productivity.

---

### NFR-002: Security — Authorization & Tenant Isolation

**Priority:** Must Have

**Description:**
Nguyên tắc tổng quát về authorization. Phân quyền chi tiết theo từng action quy định trong **Acceptance Criteria của FR tương ứng** (xem FR-001 → FR-005). Bảng tổng quan quyền nằm ở section [User Personas — Permissions Matrix](#user-personas).

**Acceptance Criteria:**
- [ ] **Reuse framework:** Tất cả admin APIs dùng middleware `routeauth.Auth()` hiện có (`a.IsRoot`, `a.IsAdmin`, `a.IsCollaborator`). Không định nghĩa role/middleware mới.
- [ ] **Authentication:** Mọi admin API yêu cầu valid session (JWT cookie/header) — reuse pattern `RequiredLogin` hiện có.
- [ ] **Tenant isolation (server-side):** Non-root staff có `staff.partner` set: BE auto-inject filter `partner=staff.partner` vào mọi query (list, detail, mapping). Client không thể bypass bằng cách truyền `partner` khác trong query/body.
- [ ] **Cross-partner protection:** Khi non-root staff thao tác trên record có `record.partner != staff.partner` → 403 (kể cả khi truy vấn trực tiếp by ID).
- [ ] **Audit trail:** Mọi mutation (FR-001/003/004) ghi audit log qua `internal/service/audit.go` với `actorType=ActorTypeHumanAdmin` + `actionBy=staff.id`.
- [ ] **No credential leakage:** Scalef credentials (HMAC client_id/secret) không xuất hiện ở Admin Setup track — track này chỉ lưu metadata text `scalef_campaign_id` + `scalef_campaign_url`.

**Rationale:**
Multi-tenant: 1 partner không được biết / thao tác campaign của partner khác. Reuse middleware có sẵn để giảm risk implement sai security.

---

### NFR-003: Maintainability — Independent track

**Priority:** Must Have

**Description:**
Code Admin Setup phải build/test/deploy được độc lập với các track còn lại (Scalef linking, FE creator, Scalef API client).

**Acceptance Criteria:**
- [ ] Code Admin Setup không import từ module Scalef API client (không tồn tại ở thời điểm này)
- [ ] Schema MongoDB chuẩn bị sẵn fields cần thiết cho API Integration track sử dụng sau (đặc biệt `scalef_campaign_id`, `scalef_campaign_url`)
- [ ] Unit + integration tests chạy được mà không cần mock Scalef API
- [ ] Có thể deploy lên môi trường staging/prod ngay khi xong, không chờ track khác

**Rationale:**
Track này được xác định là khởi đầu sớm nhất → cần đảm bảo không tạo dependency ngược.

---

### NFR-004: Compatibility — Existing System

**Priority:** Must Have

**Description:**
Admin Setup không được phá vỡ hệ thống hiện có.

**Acceptance Criteria:**
- [ ] Affiliate campaigns là collection riêng — không thay đổi `events` collection schema
- [ ] Mapping table riêng — không thay đổi `events` schema
- [ ] Admin pages mới không conflict với pages hiện có (route prefix riêng `/admin/affiliate-campaigns`)
- [ ] Reuse permission framework hiện có
- [ ] Reuse file upload (banner) module hiện có (MinIO)
- [ ] Reuse markdown editor hiện có (nếu có) cho field `description`

**Rationale:**
Tránh regression cho các tính năng đang chạy.

---

### NFR-005: Usability — Admin UX

**Priority:** Should Have

**Description:**
Admin UI phải dễ dùng cho operations team không cần training nhiều.

**Acceptance Criteria:**
- [ ] Form validate inline (không phải submit mới biết sai)
- [ ] Confirm modal cho mọi action mutating (delete, deactivate, unlink) với message rõ ràng
- [ ] Error message hiển thị bằng tiếng Việt
- [ ] Loading state cho mọi async action
- [ ] Toast notification cho success/error
- [ ] Banner image preview ngay sau upload

**Rationale:**
Admin team có nhiều người không phải dev, UX kém sẽ tạo support burden.

---

## Epics

Epics are logical groupings of related functionality that will be broken down into user stories during sprint planning (Phase 4).

---

### EPIC-001: Affiliate Campaign Management (Core)

**Description:**
CRUD đầy đủ cho affiliate campaign — entity trung tâm của track. Bao gồm form tạo/sửa, list page với filter/search, detail page, đổi status.

**Functional Requirements:**
- FR-001
- FR-002
- FR-004 (CRUD endpoints)

**Story Count Estimate:** 5-7

**Priority:** Must Have

**Business Value:**
Đây là backbone của Admin Setup — không có epic này thì không có gì để map hay hiển thị.

---

### EPIC-002: Event Mapping

**Description:**
Liên kết affiliate campaign ↔ Event qua bảng many-to-many. Bao gồm UI search/autocomplete event trong affiliate detail, link/unlink, hiển thị danh sách events đã link.

**Functional Requirements:**
- FR-003
- FR-004 (mapping endpoints)
- FR-005 (autocomplete search)

**Story Count Estimate:** 3-4

**Priority:** Must Have

**Business Value:**
Mapping là cơ chế để FE creator biết Event nào hiển thị affiliate nào — không có mapping thì creator không thấy gì.

---

## User Stories (High-Level)

User stories follow the format: "As a [user type], I want [goal] so that [benefit]."

---

### EPIC-001 stories

- **US-001:** As a Root staff, I want to create a new affiliate campaign so that creators có content affiliate để promote.
- **US-002:** As an Admin (có partner gắn), I want to chỉ thấy campaigns của partner mình so that không can thiệp partner khác.
- **US-003:** As an admin, I want to filter và search campaigns so that tìm nhanh trong số hàng chục campaigns.
- **US-004:** As an admin, I want to upload banner và preview ngay so that biết banner trông thế nào trước khi save.
- **US-005:** As an admin, I want to thấy badge "Hết hạn" cho campaign quá end_date so that biết để cân nhắc gia hạn.
- **US-006:** As a Collaborator, I want to xem list/detail campaign read-only so that nắm trạng thái mà không lo thao tác nhầm.

### EPIC-002 stories

- **US-007:** As an admin, I want to link affiliate campaign với 1 hoặc nhiều Event so that creator thấy affiliate trong context Event.
- **US-008:** As an admin, I want to autocomplete search Event khi link so that không phải nhớ ID.
- **US-009:** As an admin, I want to unlink affiliate khỏi Event so that gỡ campaign sai/lỗi nhanh chóng.

---

## User Personas

Reuse role hiện có của vcreator (xem `pkg/admin/router/routeauth/auth.go`):

| Persona | Code | Mô tả |
|---------|------|-------|
| **Root** | `staff.isRoot=true` | Toàn quyền trên tất cả partners. Toàn cảnh hệ thống. |
| **Admin** | `role.code='admin'` (+ optional `staff.partner`) | Đại diện vận hành — có thể bound 1 partner cụ thể qua `staff.partner` (chỉ thấy/thao tác data partner mình); nếu không bound thì hành xử như Root. |
| **Collaborator** | `role.code='collaborator'` | Cộng tác viên — read-only. |

### Permissions Matrix (cheat sheet)

> Bảng tổng quan để stakeholder nhanh chóng nắm. **Source of truth là Acceptance Criteria của từng FR.**

| Action | Root | Admin (no partner) | Admin (có partner) | Collaborator |
|--------|:----:|:------------------:|:------------------:|:------------:|
| Tạo campaign (FR-001) | ✅ chọn partner | ✅ chọn partner | ✅ auto-fill `staff.partner` | ❌ 403 |
| Sửa campaign (FR-001) | ✅ tất cả | ✅ tất cả | ✅ chỉ partner mình | ❌ 403 |
| Đổi status (FR-001) | ✅ | ✅ | ✅ chỉ partner mình | ❌ 403 |
| Xem list/detail (FR-002) | ✅ tất cả | ✅ tất cả | ✅ filter theo partner | ✅ filter theo partner |
| Filter theo partner (FR-002) | ✅ dropdown | ✅ dropdown | ❌ auto-fix theo `staff.partner` | ❌ auto-fix theo `staff.partner` |
| Link/Unlink Event (FR-003) | ✅ | ✅ | ✅ chỉ khi cả 2 cùng partner mình | ❌ 403 |
| Search Event để link (FR-005) | ✅ | ✅ | ✅ filter theo partner | ❌ 403 |
| Cross-partner data | ✅ thấy | ✅ thấy | ❌ 403 | ❌ 403 |

---

## User Flows

### Flow 1: Tạo affiliate campaign mới (happy path)

```
Admin login → menu "Affiliate Campaigns" → bấm "+ Tạo mới"
  → Form modal mở (Root chọn partner trong dropdown; Admin có partner thì auto-fill staff.partner immutable)
  → Nhập title, short_desc, description, upload banner
  → Nhập commission_info, bonus_info, scalef_campaign_id, scalef_campaign_url
  → Set start_date, end_date
  → Submit
  → BE validate (required, unique scalef_campaign_id, URL format, date range)
  → Tạo với status=inactive + audit log
  → Redirect detail page
  → Admin review xong → toggle status = active
```

### Flow 2: Liên kết affiliate với Event

```
Admin vào affiliate detail → tab "Events đã liên kết"
  → Bấm "+ Liên kết Event"
  → Modal autocomplete: type tên event → debounce 300ms
  → BE search Events cùng partner, exclude đã link
  → Admin chọn 1 hoặc nhiều → "Xác nhận"
  → BE tạo mappings (skip duplicate) + audit log
  → Modal đóng, list reload
```

### Flow 3: Campaign tự ẩn khi qua end_date (no cron)

```
Campaign status=active, end_date=2026-05-01
  → Đến ngày 2026-05-02:
    - Status DB: vẫn 'active' (không tự đổi)
    - FE creator query: filter `end_date IS NULL OR end_date > now()` → không trả ra → ẩn
    - Admin list: vẫn hiển thị, kèm badge "Hết hạn"
  → Admin tự deactivate manual nếu muốn dọn dẹp (hoặc kệ)
```

**Lý do giữ status=active:** đơn giản hệ thống, không cần cron, không cần migration. Logic ẩn xử lý ở query layer của FE Display + API Integration.

---

## Dependencies

### Internal Dependencies

- **Admin authentication + permission framework** — đã có ở Gen-Green admin
- **Event entity + admin pages** — đã có
- **Partner entity** — đã có
- **File upload module** — MinIO client đã có ở `backend/internal/module/minio/`
- **Audit framework** — đã có ở `backend/internal/service/audit.go` (`AuditInterface.CreateAudits()`, collection `audit`, `ActorType` enum). Reuse để log create / update / change_status / link_event / unlink_event
- **Notification module** — Telegram bot đã có ở `backend/internal/module/telegram/`
- **Markdown editor (admin UI)** — kiểm tra component lib admin đã có chưa

### External Dependencies

- **MongoDB** — collection mới: `affiliate_campaigns`, `campaign_affiliate_mappings`. Audit log reuse collection `audit` hiện có (xem `internal/model/mg/audit.go`)
- **MinIO bucket** — banner storage (reuse `MINIO_BUCKET_PUBLIC_FILE` hiện có)

**Lưu ý:** Track này KHÔNG depend Scalef API, Scalef SSO, hoặc HMAC credentials. `scalef_campaign_id` và `scalef_campaign_url` chỉ là metadata text, lấy thủ công từ team Scalef.

---

## Assumptions

1. **Permission framework hiện tại đủ dùng** — vcreator đã có 3 cấp `Root` / `Admin` / `Collaborator` (verified ở `pkg/admin/router/routeauth/auth.go`). Affiliate campaign reuse cùng pattern Event ở `pkg/admin/router/event.go`.
2. **Event entity có field `partner`** — để filter mapping. Đã verified: `EventRaw.Partner` ở `backend/internal/model/mg/event.go`.
3. **Admin team chuẩn bị sẵn list campaigns cần tạo** trước khi feature deploy — không phải responsibility của Admin Setup track tạo data mẫu.
4. **`scalef_campaign_id` + `scalef_campaign_url` lấy thủ công** từ Scalef admin/portal hoặc team Scalef cung cấp — track này không gọi Scalef API để fetch.
5. **Banner image** dùng MinIO public bucket, không cần xử lý CDN/resize phức tạp ở V1.
6. **Markdown rendering ở FE creator** sẽ do FE Display track xử lý — Admin Setup chỉ lưu markdown text raw.

---

## Out of Scope

| Feature | Lý do | Chuyển sang |
|---------|-------|-------------|
| Auto-sync campaigns từ Scalef API | Cần Scalef API client (chưa có ở phase này) | Future enhancement |
| Cron auto-deactivate campaign hết hạn | Đơn giản hệ thống — campaign vẫn `active` sau end_date, FE tự ẩn theo end_date filter | Could Have nếu admin yêu cầu sau |
| Admin xử lý dispute / refund | Liên quan payment, không thuộc setup | Phase report (V2) |
| Admin gỡ liên kết Scalef của user | Thuộc Scalef linking phase | Scalef Phase 1 (đã có scope) |
| Admin xem dashboard hoa hồng / đơn hàng | Cần report APIs từ Scalef | Phase Report (V2) |
| Multi-language cho campaign title/desc | Gen-Green hiện chỉ tiếng Việt | Future |
| Versioning / draft mode cho campaign | Không phải MVP | Future |
| Export campaigns ra CSV | Không phải MVP | Could Have nếu admin yêu cầu sau |

---

## Open Questions

_(Không còn câu hỏi mở — toàn bộ phụ thuộc đã verified ở vcreator codebase: role middleware, audit service, MinIO storage, markdown editor pattern.)_

---

## Approval & Sign-off

### Stakeholders

| Role | Name | Responsibility |
|------|------|----------------|
| Product Owner | TBD | Approve scope + priorities |
| Engineering Lead | TBD | Approve technical approach |
| Admin Operations Lead | TBD | Approve UX + workflow |
| QA Lead | TBD | Approve test coverage |

### Approval Status

- [ ] Product Owner
- [ ] Engineering Lead
- [ ] Design Lead
- [ ] QA Lead

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-04 | vinhnguyen | Initial PRD. Format theo BMAD template + reference Ambassador V1 (FR-001/002/003/015). Track độc lập với Scalef linking. Đổi `pub2_` → `scalef_` cho variables. |
| 1.1 | 2026-05-04 | vinhnguyen | Bỏ FR cron auto-deactivate (giữ logic hiện có: status `active` + filter theo end_date ở query layer). Renumber FR-006/007/008/009 → FR-005/006/007/008. |
| 1.2 | 2026-05-04 | vinhnguyen | Bỏ FR-005 cũ (audit log) — reuse `internal/service/audit.go` có sẵn. Bỏ FR-008 cũ (tab trong Event detail) — Ambassador không có. Bỏ NFR-006 (Auditability), bỏ EPIC-003. Renumber: FR-006→FR-005, FR-007→FR-006. Sửa role nomenclature: Super/Partner/Operator → **Root / Admin / Collaborator** (đúng vcreator). Bỏ field `category` (Ambassador đã bỏ). Đóng toàn bộ Open Questions vì phụ thuộc đã verified. |
| 1.3 | 2026-05-04 | vinhnguyen | Bỏ FR-006 (Bulk Activate/Deactivate) — không cần. Restructure Authorization: thêm dòng **"Authorization"** vào Acceptance Criteria của từng FR (FR-001 → FR-005), trong FR-004 dùng bảng endpoint × middleware. NFR-002 rewrite thành **nguyên tắc tổng quát** + reference "xem FR liên quan" (không liệt kê chi tiết action nữa). User Personas thêm **Permissions Matrix** dạng cheat sheet (Action × Role). |

---

## Next Steps

### Phase 3: Architecture

Run `/architecture` để thiết kế chi tiết:
- Backend Go structure (model, DAO, service, handler, router)
- MongoDB schema + indexes
- Admin UI component tree (DVA model, pages, services)
- Permission integration với framework hiện có

### Phase 4: Sprint Planning

Sau khi architecture xong:
- Break 3 epics thành stories chi tiết
- Estimate từng story
- Plan sprint (estimate ~2 tuần / ~10.5 ngày effort)
- Kick-off implementation

---

**This document was created using BMAD Method v6 - Phase 2 (Planning)**

---

## Appendix A: Requirements Traceability Matrix

| Epic ID | Epic Name | Functional Requirements | Story Count (Est.) |
|---------|-----------|-------------------------|-------------------|
| EPIC-001 | Affiliate Campaign Management (Core) | FR-001, FR-002, FR-004 | 5-7 |
| EPIC-002 | Event Mapping | FR-003, FR-004 (mapping), FR-005 | 3-4 |

**Total estimated stories:** 8-11

---

## Appendix B: Prioritization Details

### Functional Requirements

| Priority | Count | FRs |
|----------|-------|-----|
| Must Have | 5 | FR-001, FR-002, FR-003, FR-004, FR-005 |
| Should Have | 0 | — |
| Could Have | 0 | — |

### Non-Functional Requirements

| Priority | Count | NFRs |
|----------|-------|------|
| Must Have | 4 | NFR-001, NFR-002, NFR-003, NFR-004 |
| Should Have | 1 | NFR-005 |

### MVP Scope (Must Have only)

Build chỉ Must Have FRs + NFRs sẽ ra một feature đủ dùng cho admin team:
- Tạo / sửa / list / search campaign
- Link / unlink với Event
- Permission đúng (Root / Admin / Collaborator — reuse middleware Event)
- Autocomplete search Event khi link mapping
- Performance đủ nhanh
- Không phá vỡ hệ thống hiện có

→ MVP = full scope V1: ~7d (~1.5 tuần).

---

## Appendix C: Data Model Reference

### Collection: `affiliate_campaigns`

| Field | Type | Mô tả |
|-------|------|-------|
| `_id` | ObjectId | |
| `partner` | string, required, immutable | Partner code |
| `title` | string, required | |
| `short_desc` | string | Hiển thị card listing + đầu detail |
| `description` | string | Markdown, accordion `##` heading ở detail page |
| `banner` | object `{url, width, height}` (required) | |
| `commission_info` | string, required | VD "Tới 8%/đơn" |
| `bonus_info` | string | VD "+100K đơn đầu" |
| `scalef_campaign_id` | string, required, unique | |
| `scalef_campaign_url` | string, required | Format URL |
| `status` | enum `active` / `inactive`, default `inactive` | |
| `start_date` | datetime, nullable | |
| `end_date` | datetime, nullable | |
| `created_by` | ObjectId | Admin id |
| `updated_by` | ObjectId | Admin id |
| `created_at`, `updated_at` | datetime | |

**Indexes:**
- `scalef_campaign_id` unique
- `(partner, status, created_at desc)`
- `end_date` (cho query "đang còn hiệu lực" của FE)

### Collection: `campaign_affiliate_mappings`

| Field | Type | Mô tả |
|-------|------|-------|
| `_id` | ObjectId | |
| `event_id` | ObjectId, required | FK → events |
| `affiliate_campaign_id` | ObjectId, required | FK → affiliate_campaigns |
| `partner` | string (denorm) | Để filter nhanh |
| `created_by` | ObjectId | |
| `created_at` | datetime | |

**Indexes:**
- `(event_id, affiliate_campaign_id)` unique compound
- `event_id`
- `affiliate_campaign_id`

### Audit logging

Reuse collection `audit` + service `internal/service/audit.go` hiện có của vcreator. Mỗi mutation gọi `Audit().CreateAudits(ctx, payloads)` với:
- `targetId` = affiliate_campaign id (hoặc mapping id cho link/unlink)
- `data` = old/new value object
- `message` = action description (VD `"affiliate_campaign.create"`, `"affiliate_campaign.change_status"`, `"affiliate_campaign.link_event"`)
- `actionBy` = staff id từ session
- `actorType` = `ActorTypeHumanAdmin`

Không cần tạo collection mới.
