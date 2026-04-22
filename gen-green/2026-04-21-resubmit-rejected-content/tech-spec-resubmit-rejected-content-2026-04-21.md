# Tech Spec: Cho phép submit lại content đã bị reject ở campaign khác

- **Project**: vcreator
- **Level**: 1 (small scope, 3-5 stories)
- **Date**: 2026-04-21
- **Related PRD**: [prd-vcreator-allow-resubmit-rejected-content-2026-04-21.md](./prd-vcreator-allow-resubmit-rejected-content-2026-04-21.md)
- **Status**: Draft

---

## 1. Problem & Solution

**Problem**: Duplicate-check ở submit content chặn toàn cục theo `contentId`, không phân biệt status/event. Content đã reject ở event A không thể submit lại ở event B → creator mất cơ hội nhận thưởng cho content hợp lệ.

**Solution**:
1. Thêm partner-level feature flag `allowResubmitRejectedContent` (default `false`).
2. Với partner đã bật flag: relax duplicate check — cho phép submit nếu tất cả bản ghi cùng `contentId` (trong cùng partner) đều đã `rejected` và thuộc event khác.
3. Thêm guard ở admin un-reject flow (áp dụng bất kể flag) để tránh double-count reward.

**Nguyên tắc**: Flag chỉ ảnh hưởng **tại thời điểm check submit** (D5). Không migrate dữ liệu cũ, không backfill, không phân biệt rejected records tạo trước/sau khi bật flag — tất cả rejected records đều được tính như nhau.

---

## 2. Requirements

### In Scope
- **R1** — Thêm struct `PartnerOptions` với field `AllowResubmitRejectedContent bool` vào model `PartnerRaw`.
- **R2** — Thêm admin API + UI để toggle flag `allowResubmitRejectedContent` cho từng partner.
- **R3** — Sửa query duplicate check ở creator submit để lọc theo status + partner, và chỉ relax khi partner flag bật.
- **R4** — Thêm guard ở admin un-reject flow (áp dụng bất kể flag): chặn chuyển `rejected` → `approved`/`waiting_approved` nếu đã có bản ghi active khác cùng `contentId` (cùng partner).
- **R5** — Thêm compound/partial index trên collection `contents` để đảm bảo performance và concurrency safety.
- **R6** — Viết unit test cho các case: partner flag off, partner flag on × các trạng thái bản ghi, admin un-reject guard.
- **R7** — Audit log khi admin toggle flag partner (để trace ai bật/tắt, khi nào).

### Out of Scope
- UI cảnh báo lịch sử submit cho creator (phase sau).
- Migration dữ liệu cũ.
- Thay đổi flow crawl metadata từ social platform.
- Thay đổi behavior reject/approve của admin (chỉ thêm guard).

---

## 3. Technical Approach

### Tech Stack
- **Language/Framework**: Go 1.24+ (backend vcreator)
- **Database**: MongoDB (collection `contents`, `eventRewards`, `contentAnalyticDaily`, `contentFlows`)
- **Testing**: Go testing + mockery (theo convention hiện tại của vcreator)

### Architecture Overview

```
Creator submit                         Admin un-reject
   │                                       │
   ▼                                       ▼
[public/service/content.go]       [admin/service/content.go]
       │                                  │
       │ 1. Validate event                │ 1. Load content
       │ 2. Crawl metadata                │ 2. (NEW) Check active duplicate
       │ 3. (CHANGED) Duplicate check     │ 3. Update status
       │    with status filter            │ 4. ActionAfterWhenChangeStatus
       │ 4. Insert content                │
       ▼                                   │
   DB: contents                            ▼
   (partial unique index                DB: contents
    on contentId where
    status ≠ rejected)
```

### Data Model Changes

**File**: [backend/internal/model/mg/partner.go](../../../vcreator/backend/internal/model/mg/partner.go)

Thêm struct `PartnerOptions` (theo pattern của `EventOpts`):
```go
type PartnerOptions struct {
    AllowResubmitRejectedContent bool `json:"allowResubmitRejectedContent" bson:"allowResubmitRejectedContent"`
}

type PartnerRaw struct {
    // ... existing fields ...
    Options *PartnerOptions `bson:"options,omitempty" json:"options,omitempty"`
}
```

Default: `nil` hoặc `{AllowResubmitRejectedContent: false}` → behavior cũ.

Collection `contents` không thay đổi schema, chỉ thêm index.

### Load Partner in Submit Flow

Hiện tại `Create()` không load `Partner` trực tiếp mà lấy `event.Partner` (ObjectID). Cần load thêm `PartnerRaw` để đọc `Options`:

```go
partner := new(modelmg.PartnerRaw)
_ = daomongodb.PartnerDAO().GetShare().FindById(ctx, partner, event.Partner)
if partner.ID.IsZero() {
    return errors.New(locale.PartnerKeyNotFound)
}

allowResubmit := partner.Options != nil && partner.Options.AllowResubmitRejectedContent
```

### Query Changes

**Current** — [pkg/public/service/content.go:264-273](../../../vcreator/backend/pkg/public/service/content.go#L264-L273):
```go
_ = daomongodb.ContentDAO().GetShare().FindOne(ctx, checkExists, bson.M{
    "contentId": contentInfo.ID,
})
if !checkExists.ID.IsZero() {
    return errors.New(locale.ContentKeyLinkUsed)
}
```

**Proposed**:
```go
filter := bson.M{
    "contentId": contentInfo.ID,
    "partner":   event.Partner, // scope theo partner (tenant isolation)
}

if allowResubmit {
    // Chỉ block khi có bản ghi active HOẶC rejected ở cùng event
    filter["$or"] = []bson.M{
        {"status": bson.M{"$ne": constants.StatusRejected}},
        {"event": eventId},
    }
}
// Nếu allowResubmit = false → giữ behavior cũ (block mọi bản ghi cùng partner)

_ = daomongodb.ContentDAO().GetShare().FindOne(ctx, checkExists, filter)
if !checkExists.ID.IsZero() {
    return errors.New(locale.ContentKeyLinkUsed)
}
```

Logic:
- **Flag off**: block nếu có bất kỳ bản ghi nào cùng `contentId` trong cùng partner (behavior cũ, chỉ thêm scope partner).
- **Flag on**:
  - Block nếu có bản ghi active (`status ≠ rejected`) cùng `contentId` cùng partner.
  - Block nếu có bản ghi rejected ở cùng event (chống spam cùng event).
  - Allow nếu chỉ có rejected ở event khác trong cùng partner.

**Lưu ý về behavior change với partner chưa bật flag**: query cũ không scope partner, query mới scope theo partner. Nghĩa là nếu hai partner từng có cùng `contentId` (rất hiếm nhưng có thể xảy ra với user social public), logic mới sẽ **allow** trong khi logic cũ **block**. Cần verify trên dữ liệu production hiện tại xem có case này không. Nếu có và muốn giữ behavior cũ tuyệt đối, có thể bỏ `"partner"` trong filter khi `allowResubmit = false`.

### Index Changes

File: [backend/internal/module/database/mongodb/index.go](../../../vcreator/backend/internal/module/database/mongodb/index.go)

**Thêm**:
```go
// Partial unique index: đảm bảo không có 2 bản ghi active cùng (partner, contentId)
// Scope theo partner vì query duplicate cũng scope theo partner
i.newPartialUniqueIndex(
    []string{"partner", "contentId"},
    bson.M{"status": bson.M{"$ne": constants.StatusRejected}},
)
```

Nếu helper `newPartialUniqueIndex` chưa có → thêm mới vào index module.

### Admin Un-reject Guard

File: [pkg/admin/service/content.go:176-249](../../../vcreator/backend/pkg/admin/service/content.go#L176-L249)

Trước khi update status từ `rejected` → status khác, thêm check (áp dụng **bất kể** partner flag):
```go
if oldStatus == constants.StatusRejected && newStatus != constants.StatusRejected {
    var active = new(modelmg.ContentRaw)
    _ = daomongodb.ContentDAO().GetShare().FindOne(ctx, active, bson.M{
        "contentId": content.ContentId,
        "partner":   content.Partner,
        "_id":       bson.M{"$ne": content.ID},
        "status":    bson.M{"$ne": constants.StatusRejected},
    })
    if !active.ID.IsZero() {
        return errors.New(locale.ContentKeyActiveDuplicateExists)
    }
}
```

Thêm locale key mới: `ContentKeyActiveDuplicateExists` = "Nội dung này đã được sử dụng ở event khác, không thể khôi phục".

### Admin API/UI — Toggle Partner Flag

**Permission (D4)**: Dùng lại permission **edit partner** có sẵn. Ai edit được partner → toggle được flag. KHÔNG thêm permission/role mới.

**Backend**: Mở rộng endpoint update partner (`PATCH /admin/partners/:id` hoặc tương tự) để nhận thêm field `options.allowResubmitRejectedContent`. Middleware permission giữ nguyên.

**Frontend admin**: Thêm toggle trong trang partner settings (tích hợp vào form edit partner hiện có). UX:
- Toggle có tooltip giải thích: "Cho phép creator submit lại content đã bị reject ở event khác trong cùng partner này"
- Confirm dialog khi bật (warning về rủi ro gian lận)
- Hiển thị last-updated-by/at để audit

**Audit log**: Ghi entry mỗi lần flag thay đổi (ai, khi nào, from → to).

---

## 4. Implementation Plan — Stories

| # | Story | Deliverable | Est |
|---|---|---|---|
| 1 | **Thêm `PartnerOptions` struct + field `AllowResubmitRejectedContent`** | Model change + migration (không cần backfill vì `nil` = default false) | 0.25d |
| 2 | **Admin API update partner options** | Mở rộng endpoint update partner để nhận field `options.allowResubmitRejectedContent` + audit log | 0.5d |
| 3 | **Admin UI toggle flag** | Thêm toggle trong trang partner settings (frontend admin) + confirm dialog | 0.5d |
| 4 | **Thêm partial unique index `(partner, contentId)`** | Migration code + verify trên dev DB | 0.5d |
| 5 | **Conditional duplicate check ở creator submit** | Load partner + sửa query theo flag ([content.go:264-273](../../../vcreator/backend/pkg/public/service/content.go#L264-L273)) + unit test cả 2 branch flag | 0.75d |
| 6 | **Guard admin un-reject** | Thêm check active duplicate trong admin update status + locale key mới + unit test | 0.5d |
| 7 | **Integration test end-to-end** | Test flow: flag off (behavior cũ); flag on với các case allow/block; admin un-reject guard | 0.5d |
| 8 | **(Optional) Audit log khi creator resubmit rejected link** | Ghi audit entry khi detect resubmit | 0.5d |

**Order**: 1 → 4 → 5 → 6 → 2 → 3 → 7 → 8 (model + index trước; backend logic; rồi admin API/UI; cuối cùng là test + optional)

**Total**: 3.5-4 ngày công (không tính story 8).

---

## 5. Acceptance Criteria

**Partner flag management:**
- [ ] Admin bật/tắt được flag `allowResubmitRejectedContent` qua UI partner settings
- [ ] Flag mặc định `false` cho tất cả partner hiện tại
- [ ] Có audit log mỗi lần toggle flag
- [ ] Confirm dialog xuất hiện khi bật flag (warning gian lận)

**Partner flag OFF (default — behavior cũ):**
- [ ] Creator submit link đã `rejected` ở event khác (cùng partner) → **fail** với `ContentKeyLinkUsed`
- [ ] Creator submit link đã `approved` → **fail** với `ContentKeyLinkUsed`

**Partner flag ON:**
- [ ] Creator submit link vào event B, link đó đã `rejected` ở event A (cùng partner) → **success**
- [ ] Creator submit link vào event B, link đó đang `waiting_approved` hoặc `approved` ở event A → **fail** với `ContentKeyLinkUsed`
- [ ] Creator submit link vào event A lần 2 sau khi bị reject ở event A → **fail** (chống spam cùng event)

**Admin un-reject guard (áp dụng bất kể flag):**
- [ ] Admin un-reject content ở event A, trong khi content đã được submit lại ở event B (active) → **fail** với `ContentKeyActiveDuplicateExists`
- [ ] Admin un-reject content ở event A, không có active dup nào → **success** (behavior cũ)

**Concurrency & data integrity:**
- [ ] 2 request song song cùng `(partner, contentId)`, cùng event → chỉ 1 insert thành công (nhờ partial unique index)
- [ ] Partial unique index `(partner, contentId)` where status ≠ rejected tồn tại trên collection `contents` sau deploy
- [ ] Không có reward double-count trong reconciliation sau 1 tuần monitor
- [ ] Partial unique index tồn tại trên collection `contents` sau deploy
- [ ] Unit test + integration test pass
- [ ] Không có reward double-count trong reconciliation sau 1 tuần monitor

---

## 6. Non-Functional Requirements

### Performance
- Query duplicate check phải sử dụng index `(contentId, status)` hoặc partial unique index. Acceptable: < 50ms P99.
- Không có full collection scan.

### Security
- Không có yêu cầu security mới. Giữ nguyên auth flow (`RequiredLogin` ở public route).

### Data Integrity
- Partial unique index đảm bảo: tại mỗi thời điểm, không tồn tại > 1 content active cùng `contentId`.
- Guard un-reject đảm bảo: admin không thể tạo trạng thái double-active bằng thao tác thủ công.

### Observability
- Log mỗi lần query duplicate check return reject (để đo R1 metric trong PRD).
- Log khi guard un-reject trigger (để đo tần suất admin cố un-reject khi có active dup).

---

## 7. Dependencies, Risks, Timeline

### Dependencies
- MongoDB version hỗ trợ partial index (MongoDB 3.2+). vcreator đã dùng phiên bản mới hơn → OK.
- Không phụ thuộc external service.

### Risks

| Risk | Mitigation |
|---|---|
| Partial unique index conflict với dữ liệu hiện tại (nếu đã có trùng `(partner, contentId)` active) | Trước khi tạo index, chạy aggregation query đếm duplicate active records. Nếu có, migration data trước. |
| Admin un-reject batch (multiple contents) có content bị guard chặn | Batch endpoint cần trả về partial success + list contents bị chặn để admin xem lại. |
| Performance regression khi query `$or` phức tạp | Verify explain plan trên dev DB, đảm bảo dùng index. |
| Locale key mới chưa có bản dịch | Thêm key vào toàn bộ locale files (vi/en) trước khi merge. |
| Partner bật flag nhầm → gian lận lọt qua | Confirm dialog + audit log + default false. Có thể thêm permission check riêng (chỉ super admin toggle được). |
| Behavior thay đổi ngầm với partner flag off (scope theo partner thay vì global) | Chạy query trước deploy để đếm cross-partner duplicate contentId. Nếu > 0, xem xét giữ query global cho branch flag-off. |
| Frontend admin partner settings có thể chưa có trang (cần tạo mới) | Verify sớm với FE team. Nếu chưa có, scope lại story 3. |

### Timeline
- **Target completion**: 2026-04-30 (1.5 tuần — tăng do thêm scope partner config + admin UI)
- **Milestones**:
  - Day 1: Story 1 + 4 (model + index)
  - Day 2-3: Story 5 + 6 (backend logic + guard)
  - Day 4: Story 2 + 3 (admin API + UI)
  - Day 5: Story 7 (integration test)
  - Day 6: Code review + fix
  - Day 7: Deploy staging + QA
  - Day 8-10: Deploy production + monitor + enable flag cho partner pilot

---

## 8. Files to Change (Reference)

### Backend
| File | Change |
|---|---|
| [backend/internal/model/mg/partner.go](../../../vcreator/backend/internal/model/mg/partner.go) | Thêm struct `PartnerOptions` + field `Options` vào `PartnerRaw` |
| [backend/pkg/public/service/content.go](../../../vcreator/backend/pkg/public/service/content.go) | Line 264-273: load partner + conditional query theo flag |
| [backend/pkg/admin/service/content.go](../../../vcreator/backend/pkg/admin/service/content.go) | Line 176-249: thêm guard un-reject |
| `backend/pkg/admin/service/partner.go` (hoặc tương tự) | Mở rộng update partner để nhận `options.allowResubmitRejectedContent` + audit log |
| `backend/pkg/admin/router/partner.go` | Expose route PATCH partner options |
| `backend/pkg/admin/routevalidation/partner.go` | Validation cho field mới |
| [backend/internal/module/database/mongodb/index.go](../../../vcreator/backend/internal/module/database/mongodb/index.go) | Thêm partial unique index `(partner, contentId)` |
| `backend/internal/constants/locale/*.go` | Thêm key `ContentKeyActiveDuplicateExists` |
| Test files tương ứng | Unit + integration test |

### Frontend admin
| File | Change |
|---|---|
| `admin/` (trang partner settings) | Thêm toggle `allowResubmitRejectedContent` + confirm dialog + call API |

---

## 9. Decisions & Open Questions

### Confirmed (từ PRD)
- **D1**: Cùng event đã reject → KHÔNG cho submit lại.
- **D2**: Scope query theo `partner`.
- **D3**: Frontend admin cần làm.
- **D4**: Permission toggle = role edit partner có sẵn (không thêm permission mới).
- **D5**: Check-time only — áp dụng cho mọi rejected record bất kể thời điểm tạo. Không migrate.

### Open
- **Q1**: Audit log khi creator resubmit (Story 8 optional).
- **Q2**: UX warning cho creator — out of scope.

---

## 10. Rollback Plan

- **Partner flag**: kill switch trực tiếp — tắt flag ở tất cả partner qua admin UI hoặc update DB: `db.partners.updateMany({}, {$set: {"options.allowResubmitRejectedContent": false}})` → behavior cũ khôi phục ngay lập tức.
- **Index**: có thể drop index bất cứ lúc nào (không mất data).
- **Query change**: revert commit → quay lại behavior cũ (chặn toàn cục).
- **Admin guard**: revert commit → admin un-reject không có guard (rủi ro double-count lại hiện hữu, cần xử lý manual nếu đã có dữ liệu xấu).

**Lưu ý**: Partner flag chính là feature flag built-in — không cần hạ tầng feature flag riêng. Có thể bật pilot cho 1 partner trước, sau đó rollout dần.
