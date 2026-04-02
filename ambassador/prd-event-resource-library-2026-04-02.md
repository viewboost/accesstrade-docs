# Product Requirements Document: Kho Tư Liệu Event (Resource Library Field)

**Date:** 2026-04-02
**Author:** Vinh Nguyen
**Version:** 2.0
**Project Level:** Level 1
**Status:** Draft

---

## Document Overview

PRD cho tính năng thêm field **Kho Tư Liệu** (`resourceLibrary`) vào Event. Admin setup action (URL hoặc file upload) ngay trong form Event trên Admin dashboard — theo pattern `ActionType` giống News.

**Related Documents:**
- Event model: `backend/internal/model/mg/event.go`
- ActionType: `backend/internal/model/mg/common.go` (line 63)
- Admin Event page: `admin/src/pages/event/`
- News modal (reference pattern): `admin/src/pages/news/components/modal.tsx`

---

## Executive Summary

Hiện tại, link kho tư liệu cho event đang hardcode trong frontend code. Mỗi lần thay đổi link phải release code mới.

**Giải pháp:** Thêm field `resourceLibrary` (type `ActionType`) vào `EventRaw` model. Admin setup URL hoặc upload file ngay trong form chỉnh sửa Event — giống cách News dùng `RcActionTypeFormNew`. Frontend đọc field này từ API event detail và hiển thị.

**Scope nhỏ gọn:** Không tạo collection mới, không tạo CRUD riêng, không tạo trang admin riêng. Chỉ thêm 1 field vào Event.

---

## Product Goals

### Business Objectives

1. **Giảm thời gian cập nhật tư liệu** — Admin setup trong form Event, không cần deploy
2. **Tăng tính linh hoạt** — Admin tự thay đổi link/file bất kỳ lúc nào

### Success Metrics

| Metric | Target |
|--------|--------|
| Thời gian cập nhật tư liệu | < 2 phút (setup trong form Event) |
| Số lần deploy để thay đổi tư liệu | 0 |

---

## Functional Requirements

### FR-001: Thêm field `resourceLibrary` vào Event Model

**Priority:** Must Have

**Description:**
Thêm field `resourceLibrary` (type `*ActionType`) vào `EventRaw` struct. Field này lưu action cho kho tư liệu của event — có thể là URL hoặc file upload.

**Thay đổi cụ thể:**
```go
// EventRaw — thêm field:
ResourceLibrary *ActionType `bson:"resourceLibrary,omitempty" json:"resourceLibrary,omitempty"`
```

**ActionType struct (đã có sẵn):**
```go
type ActionType struct {
    Value string `json:"value" bson:"value"`   // URL hoặc file URL
    Type  string `json:"type" bson:"type"`     // "url" hoặc "file"
    Text  string `json:"text" bson:"text"`     // Label hiển thị, vd: "Xem kho tư liệu"
}
```

**Acceptance Criteria:**
- [ ] Field `resourceLibrary` được thêm vào `EventRaw` struct
- [ ] Field optional (omitempty) — event cũ không bị ảnh hưởng
- [ ] Request/Response model của Event được cập nhật tương ứng

---

### FR-002: Admin Setup Kho Tư Liệu trong Form Event

**Priority:** Must Have

**Description:**
Thêm component `RcActionTypeFormNew` vào form tạo/sửa Event trên Admin dashboard. Admin có thể:
- Chọn type: URL hoặc File
- Nhập URL trực tiếp hoặc upload file
- Nhập text label hiển thị

**Acceptance Criteria:**
- [ ] Form Event (modal hoặc page) có thêm field "Kho tư liệu" dùng `RcActionTypeFormNew`
- [ ] Khi chọn type `url`: hiển thị input nhập URL
- [ ] Khi chọn type `file`: hiển thị upload, file được upload lên MinIO
- [ ] Có thể để trống (event không bắt buộc có kho tư liệu)
- [ ] Giá trị được lưu khi submit form Event

---

### FR-003: Frontend Hiển Thị Kho Tư Liệu từ Event Data

**Priority:** Must Have

**Description:**
Frontend đọc field `resourceLibrary` từ response API event detail. Nếu có → hiển thị button/link. Nếu không có → ẩn.

**Acceptance Criteria:**
- [ ] Frontend đọc `event.resourceLibrary` từ API response hiện tại
- [ ] Nếu `resourceLibrary` có giá trị → hiển thị button với text label
- [ ] Click button → mở `resourceLibrary.value` (URL) trong tab mới
- [ ] Nếu `resourceLibrary` null/undefined → không hiển thị gì
- [ ] Xóa hardcoded resource links trong frontend code (nếu có)

---

## Non-Functional Requirements

### NFR-001: Backward Compatibility

**Priority:** Must Have

**Description:**
Field mới phải không ảnh hưởng event cũ. MongoDB schemaless nên event cũ tự động có `resourceLibrary = null`.

**Acceptance Criteria:**
- [ ] Event cũ không bị lỗi khi thiếu field
- [ ] API response event cũ: `resourceLibrary` không xuất hiện hoặc null
- [ ] Không cần migration data

---

### NFR-002: Cache Invalidation

**Priority:** Should Have

**Description:**
Khi admin update event (bao gồm field `resourceLibrary`), cache event detail trên Redis phải được invalidate.

**Acceptance Criteria:**
- [ ] Update event → invalidate Redis cache (đã có sẵn trong flow update event hiện tại)

---

## Implementation Scope

### Thay đổi cần làm:

| Layer | File | Thay đổi |
|-------|------|----------|
| **Model** | `backend/internal/model/mg/event.go` | Thêm field `ResourceLibrary *ActionType` vào `EventRaw` |
| **Admin Request** | `backend/pkg/admin/model/request/event.go` | Thêm field `ResourceLibrary` vào request struct |
| **Admin Response** | `backend/pkg/admin/model/response/event.go` | Thêm field `ResourceLibrary` vào response struct |
| **Public Response** | `backend/pkg/public/model/response/event.go` | Thêm field `ResourceLibrary` vào public response |
| **Admin UI** | `admin/src/pages/event/components/...` | Thêm `RcActionTypeFormNew` vào form Event |
| **Frontend** | Client apps (lusso, etc.) | Đọc `resourceLibrary` từ event data, hiển thị button |

### KHÔNG làm:
- Không tạo MongoDB collection mới
- Không tạo API endpoint mới
- Không tạo admin page/router mới
- Không tạo service/handler mới
- Không thêm status, order, thumbnail riêng cho tư liệu

---

## User Flow

### Admin Setup

```
Admin mở Event detail trên Admin Dashboard
→ Tìm field "Kho tư liệu" (RcActionTypeFormNew)
→ Chọn type: URL → nhập link  |  File → upload file
→ Nhập text label (vd: "Xem kho tư liệu")
→ Save Event
→ Done — frontend hiển thị ngay
```

### KOC Xem

```
KOC mở trang Event
→ Thấy button "Xem kho tư liệu" (hoặc label admin đặt)
→ Click → mở link trong tab mới
```

---

## Assumptions

1. `ActionType` struct và component `RcActionTypeFormNew` đã stable, reuse trực tiếp
2. Flow update event hiện tại đã handle cache invalidation
3. Public API event detail đã trả đủ fields — chỉ cần thêm field mới vào response

---

## Out of Scope

- Nhiều tư liệu per event (chỉ 1 action)
- Trang quản lý tư liệu riêng
- Status active/inactive cho tư liệu (muốn ẩn thì xóa field)
- Order/sorting tư liệu
- Thumbnail riêng cho tư liệu

---

## Open Questions

1. **Nhiều link?** — Nếu sau này cần nhiều tư liệu per event, có thể đổi sang `[]*ActionType`. Hiện tại 1 link đủ chưa?
2. **Vị trí trên frontend?** — Button kho tư liệu hiển thị ở đâu trên trang event? (cạnh Guide? Header? Footer?)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-02 | Vinh Nguyen | Initial PRD (over-scoped) |
| 2.0 | 2026-04-02 | Vinh Nguyen | Simplified — chỉ thêm field ActionType vào Event |
