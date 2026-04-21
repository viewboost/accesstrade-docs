# Tech Spec: Cho phép submit lại content đã bị reject ở campaign khác

- **Project**: vcreator
- **Level**: 1 (small scope, 3-5 stories)
- **Date**: 2026-04-21
- **Related PRD**: [prd-vcreator-allow-resubmit-rejected-content-2026-04-21.md](./prd-vcreator-allow-resubmit-rejected-content-2026-04-21.md)
- **Status**: Draft

---

## 1. Problem & Solution

**Problem**: Duplicate-check ở submit content chặn toàn cục theo `contentId`, không phân biệt status/event. Content đã reject ở event A không thể submit lại ở event B → creator mất cơ hội nhận thưởng cho content hợp lệ.

**Solution**: Relax duplicate check — cho phép submit nếu tất cả bản ghi cùng `contentId` đều đã `rejected`, đồng thời thêm guard ở admin un-reject flow để tránh double-count reward.

---

## 2. Requirements

### In Scope
- **R1** — Sửa query duplicate check ở creator submit để lọc theo status (cho phép bỏ qua `rejected`).
- **R2** — Thêm guard ở admin un-reject flow: chặn chuyển `rejected` → `approved`/`waiting_approved` nếu đã có bản ghi active khác cùng `contentId`.
- **R3** — Thêm compound/partial index trên collection `contents` để đảm bảo performance và concurrency safety.
- **R4** — Viết unit test cho 4 case chính của duplicate check.
- **R5** — (Optional) Log/audit trail khi resubmit link đã từng reject, để admin event mới có context.

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

### Data Model — không thay đổi

Dùng collection `contents` hiện tại. Chỉ thêm index, không thêm field mới.

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
_ = daomongodb.ContentDAO().GetShare().FindOne(ctx, checkExists, bson.M{
    "contentId": contentInfo.ID,
    "$or": []bson.M{
        {"status": bson.M{"$ne": constants.StatusRejected}},
        {"event": eventId}, // block resubmit same event even if rejected
    },
})
if !checkExists.ID.IsZero() {
    return errors.New(locale.ContentKeyLinkUsed)
}
```

Logic:
- Nếu có bản ghi active (status ≠ rejected) cùng `contentId` → block.
- Nếu có bản ghi rejected cùng event → block (chống spam submit-reject-submit cùng event).
- Nếu chỉ có rejected ở event khác → allow.

### Index Changes

File: [backend/internal/module/database/mongodb/index.go](../../../vcreator/backend/internal/module/database/mongodb/index.go)

**Thêm**:
```go
// Partial unique index: chỉ áp dụng cho bản ghi active
// Đảm bảo concurrency: 2 request song song không thể cùng insert active record
i.newPartialUniqueIndex(
    []string{"contentId"},
    bson.M{"status": bson.M{"$ne": constants.StatusRejected}},
)
```

Nếu helper `newPartialUniqueIndex` chưa có → thêm mới vào index module.

### Admin Un-reject Guard

File: [pkg/admin/service/content.go:176-249](../../../vcreator/backend/pkg/admin/service/content.go#L176-L249)

Trước khi update status từ `rejected` → status khác, thêm check:
```go
if oldStatus == constants.StatusRejected && newStatus != constants.StatusRejected {
    var active = new(modelmg.ContentRaw)
    _ = daomongodb.ContentDAO().GetShare().FindOne(ctx, active, bson.M{
        "contentId": content.ContentId,
        "_id":       bson.M{"$ne": content.ID},
        "status":    bson.M{"$ne": constants.StatusRejected},
    })
    if !active.ID.IsZero() {
        return errors.New(locale.ContentKeyActiveDuplicateExists)
    }
}
```

Thêm locale key mới: `ContentKeyActiveDuplicateExists` = "Nội dung này đã được sử dụng ở event khác, không thể khôi phục".

---

## 4. Implementation Plan — Stories

| # | Story | Deliverable | Est |
|---|---|---|---|
| 1 | **Relax duplicate check ở creator submit** | Sửa query [content.go:264-273](../../../vcreator/backend/pkg/public/service/content.go#L264-L273) + unit test 4 case | 0.5d |
| 2 | **Thêm partial unique index `contentId`** | Migration code cho index + verify trên dev DB | 0.5d |
| 3 | **Guard admin un-reject** | Thêm check active duplicate trong admin update status + locale key mới + unit test | 0.5d |
| 4 | **Integration test end-to-end** | Test flow: submit → reject → submit event khác (pass); submit → approve → submit event khác (fail); admin un-reject khi có active dup (fail) | 0.5d |
| 5 | **(Optional) Audit log khi resubmit** | Thêm audit entry nếu detect resubmit của link đã reject | 0.5d |

**Order**: 2 → 1 → 3 → 4 → 5 (index trước để concurrency-safe ngay từ đầu)

**Total**: 2-2.5 ngày công (không tính story 5).

---

## 5. Acceptance Criteria

- [ ] Creator submit link vào event B, link đó đã `rejected` ở event A → **success**
- [ ] Creator submit link vào event B, link đó đang `waiting_approved` hoặc `approved` ở event A → **fail** với error `ContentKeyLinkUsed`
- [ ] Creator submit link vào event A lần 2 sau khi bị reject ở event A → **fail** (chống spam cùng event)
- [ ] Admin un-reject content ở event A, trong khi content đã được submit lại ở event B (active) → **fail** với error `ContentKeyActiveDuplicateExists`
- [ ] Admin un-reject content ở event A, không có active dup nào → **success** (behavior cũ)
- [ ] 2 request song song cùng `contentId`, cùng event → chỉ 1 insert thành công (nhờ partial unique index)
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
| Partial unique index conflict với dữ liệu hiện tại (nếu đã có trùng contentId active) | Trước khi tạo index, chạy aggregation query đếm duplicate active records. Nếu có, migration data trước. |
| Admin un-reject batch (multiple contents) có content bị guard chặn | Batch endpoint cần trả về partial success + list contents bị chặn để admin xem lại. |
| Performance regression khi query `$or` phức tạp | Verify explain plan trên dev DB, đảm bảo dùng index. |
| Locale key mới chưa có bản dịch | Thêm key vào toàn bộ locale files (vi/en) trước khi merge. |

### Timeline
- **Target completion**: 2026-04-28 (1 tuần)
- **Milestones**:
  - Day 1-2: Story 1-3 (code + unit test)
  - Day 3: Story 4 (integration test)
  - Day 4: Code review + fix
  - Day 5: Deploy staging + QA
  - Day 6-7: Deploy production + monitor

---

## 8. Files to Change (Reference)

| File | Change |
|---|---|
| [backend/pkg/public/service/content.go](../../../vcreator/backend/pkg/public/service/content.go) | Line 264-273: relax query |
| [backend/pkg/admin/service/content.go](../../../vcreator/backend/pkg/admin/service/content.go) | Line 176-249: thêm guard un-reject |
| [backend/internal/module/database/mongodb/index.go](../../../vcreator/backend/internal/module/database/mongodb/index.go) | Thêm partial unique index |
| `backend/internal/constants/locale/*.go` (hoặc file locale keys) | Thêm key `ContentKeyActiveDuplicateExists` |
| Test files tương ứng | Unit + integration test |

---

## 9. Open Questions (từ PRD — cần confirm trước khi code)

1. **Cùng event, đã reject → cho submit lại?** — Tech spec assume **KHÔNG** (đã phản ánh trong query `$or`).
2. **Cross-partner?** — Tech spec **CHƯA** scope theo partner. Nếu cần, thêm `"partner": content.Partner` vào query.
3. **Audit log resubmit?** — Để ở Story 5 (optional).
4. **UX warning cho creator?** — Out of scope.

---

## 10. Rollback Plan

- **Index**: có thể drop index bất cứ lúc nào (không mất data).
- **Query change**: revert commit → quay lại behavior cũ (chặn toàn cục).
- **Admin guard**: revert commit → admin un-reject không có guard (rủi ro double-count lại hiện hữu, cần xử lý manual nếu đã có dữ liệu xấu).

Feature flag (nếu có hạ tầng): wrap query change trong flag `ALLOW_RESUBMIT_REJECTED_CROSS_EVENT` để toggle nhanh.
