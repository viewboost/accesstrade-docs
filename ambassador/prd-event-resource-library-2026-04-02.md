# Product Requirements Document: Kho Tu Lieu Event (Resource Library Field)

**Date:** 2026-04-02
**Author:** Vinh Nguyen
**Version:** 3.0
**Project Level:** Level 1
**Status:** Draft

---

## Document Overview

PRD cho tinh nang them field **Kho Tu Lieu** (`resourceLibrary`) vao Event. Admin setup action (URL hoac file upload) ngay trong form Event tren Admin dashboard — theo pattern `ActionType` giong News.

**Related Documents:**
- Event model: `backend/internal/model/mg/event.go` — struct `EventRaw`
- ActionType: `backend/internal/model/mg/common.go` — struct `ActionType`
- News model (reference pattern): `backend/internal/model/mg/news.go` — field `Action ActionType`
- Admin Event request: `backend/pkg/admin/model/request/event.go` — struct `EventUpsertBody`
- Admin Event response: `backend/pkg/admin/model/response/event.go` — struct `EventDetail`
- Public Event response: `backend/pkg/public/model/response/event.go` — struct `EventDetailResponse`, `EventBriefResponse`
- Admin Event page: `admin/src/pages/event/`
- Admin Event modal: `admin/src/pages/event/components/modal.tsx`
- News modal (reference pattern): `admin/src/pages/news/components/modal.tsx`

**Source repo:** `viewboost/ambassabor` (branch: `master`)

---

## Executive Summary

Hien tai, link kho tu lieu cho event dang hardcode trong frontend code. Moi lan thay doi link phai release code moi.

**Giai phap:** Them field `resourceLibrary` (type `ActionType`) vao `EventRaw` model. Admin setup URL hoac upload file ngay trong form chinh sua Event — giong cach News dung `ActionType` cho field `action`. Frontend doc field nay tu API event detail va hien thi.

**Scope nho gon:** Khong tao collection moi, khong tao CRUD rieng, khong tao trang admin rieng. Chi them 1 field vao Event.

---

## Product Goals

### Business Objectives

1. **Giam thoi gian cap nhat tu lieu** — Admin setup trong form Event, khong can deploy
2. **Tang tinh linh hoat** — Admin tu thay doi link/file bat ky luc nao

### Success Metrics

| Metric | Target |
|--------|--------|
| Thoi gian cap nhat tu lieu | < 2 phut (setup trong form Event) |
| So lan deploy de thay doi tu lieu | 0 |

---

## Functional Requirements

### FR-001: Them field `resourceLibrary` vao Event Model

**Priority:** Must Have

**Description:**
Them field `resourceLibrary` (type `ActionType`) vao `EventRaw` struct. Field nay luu action cho kho tu lieu cua event — co the la URL hoac file upload.

**Thay doi cu the:**

File: `backend/internal/model/mg/event.go`
```go
// EventRaw — them field:
ResourceLibrary *ActionType `bson:"resourceLibrary,omitempty" json:"resourceLibrary,omitempty"`
```

**ActionType struct (da co san tai `backend/internal/model/mg/common.go`):**
```go
type ActionType struct {
    Value string `json:"value" bson:"value"`   // URL hoac file URL
    Type  string `json:"type" bson:"type"`     // "url" hoac "file"
    Text  string `json:"text" bson:"text"`     // Label hien thi, vd: "Xem kho tu lieu"
}
```

**Reference:** News model (`backend/internal/model/mg/news.go`) da dung `ActionType` cho field `Action`:
```go
type NewsRaw struct {
    // ...
    Action ActionType `bson:"action" json:"action"`
    // ...
}
```

**Acceptance Criteria:**
- [ ] Field `resourceLibrary` duoc them vao `EventRaw` struct
- [ ] Field optional (omitempty) — event cu khong bi anh huong
- [ ] Request/Response model cua Event duoc cap nhat tuong ung

---

### FR-002: Cap nhat Admin Request/Response Models

**Priority:** Must Have

**Description:**
Them field `ResourceLibrary` vao cac struct request va response cua Event trong admin va public packages.

**Thay doi cu the:**

File: `backend/pkg/admin/model/request/event.go`
```go
// EventUpsertBody — them field:
ResourceLibrary *modelmg.ActionType `json:"resourceLibrary,omitempty"`
```

File: `backend/pkg/admin/model/response/event.go`
```go
// EventDetail — them field:
ResourceLibrary *modelmg.ActionType `json:"resourceLibrary,omitempty"`
```

File: `backend/pkg/public/model/response/event.go`
```go
// EventBriefResponse — them field:
ResourceLibrary *modelmg.ActionType `json:"resourceLibrary,omitempty"`

// EventDetailResponse — them field:
ResourceLibrary *modelmg.ActionType `json:"resourceLibrary,omitempty"`
```

**Acceptance Criteria:**
- [ ] Field `resourceLibrary` co trong admin request struct `EventUpsertBody`
- [ ] Field `resourceLibrary` co trong admin response struct `EventDetail`
- [ ] Field `resourceLibrary` co trong public response structs `EventBriefResponse` va `EventDetailResponse`
- [ ] Cac service handler (create/update) truyen field nay vao EventRaw khi luu

---

### FR-003: Admin Setup Kho Tu Lieu trong Form Event

**Priority:** Must Have

**Description:**
Admin Event modal dang dung StepsForm (ant-design pro-form) voi 4 steps: Overview, Photo, Option, Condition. Them field "Kho tu lieu" vao step Overview hoac tao them 1 input don gian.

Vi `ActionType` trong ambassador project chi co 3 fields don gian (value, type, text), co the dung:
- Select cho `type` (url/file)
- Input cho `value` (URL hoac upload)
- Input cho `text` (label hien thi)

**Admin Event modal hien tai:** `admin/src/pages/event/components/modal.tsx`
- Dung `StepsForm` tu `@ant-design/pro-form`
- Step 1 (Overview): `admin/src/pages/event/components/overview.tsx`

**Acceptance Criteria:**
- [ ] Form Event co them section "Kho tu lieu" trong step Overview
- [ ] Khi chon type `url`: hien thi input nhap URL
- [ ] Khi chon type `file`: hien thi upload, file duoc upload len storage
- [ ] Co the de trong (event khong bat buoc co kho tu lieu)
- [ ] Gia tri duoc gui kem trong payload khi submit form Event

---

### FR-004: Frontend Hien Thi Kho Tu Lieu tu Event Data

**Priority:** Must Have

**Description:**
Frontend doc field `resourceLibrary` tu response API event detail. Neu co -> hien thi button/link. Neu khong co -> an.

**Public API response da tra cac structs:**
- `EventBriefResponse` (list events)
- `EventDetailResponse` (event detail)

Chi can them field `resourceLibrary` vao 2 structs nay la frontend co data.

**Acceptance Criteria:**
- [ ] Frontend doc `event.resourceLibrary` tu API response
- [ ] Neu `resourceLibrary` co gia tri -> hien thi button voi text label
- [ ] Click button -> mo `resourceLibrary.value` (URL) trong tab moi
- [ ] Neu `resourceLibrary` null/undefined -> khong hien thi gi
- [ ] Xoa hardcoded resource links trong frontend code (neu co)

---

## Non-Functional Requirements

### NFR-001: Backward Compatibility

**Priority:** Must Have

**Description:**
Field moi phai khong anh huong event cu. MongoDB schemaless nen event cu tu dong co `resourceLibrary = null`.

**Acceptance Criteria:**
- [ ] Event cu khong bi loi khi thieu field
- [ ] API response event cu: `resourceLibrary` khong xuat hien hoac null
- [ ] Khong can migration data

---

## Implementation Scope

### Thay doi can lam:

| Layer | File | Thay doi |
|-------|------|----------|
| **Model** | `backend/internal/model/mg/event.go` | Them field `ResourceLibrary *ActionType` vao `EventRaw` |
| **Admin Request** | `backend/pkg/admin/model/request/event.go` | Them field `ResourceLibrary` vao `EventUpsertBody` |
| **Admin Response** | `backend/pkg/admin/model/response/event.go` | Them field `ResourceLibrary` vao `EventDetail` |
| **Public Response** | `backend/pkg/public/model/response/event.go` | Them field `ResourceLibrary` vao `EventBriefResponse` va `EventDetailResponse` |
| **Admin Service** | `backend/pkg/admin/service/event.go` (can verify) | Truyen `resourceLibrary` khi create/update Event |
| **Admin UI** | `admin/src/pages/event/components/overview.tsx` | Them input cho resourceLibrary (type selector + value input + text input) |
| **Frontend** | Client apps (lusso, etc.) | Doc `resourceLibrary` tu event data, hien thi button |

### KHONG lam:
- Khong tao MongoDB collection moi
- Khong tao API endpoint moi
- Khong tao admin page/router moi
- Khong tao service/handler moi
- Khong them status, order, thumbnail rieng cho tu lieu

---

## User Flow

### Admin Setup

```
Admin mo Event detail tren Admin Dashboard
-> Click Edit -> Step 1 (Overview)
-> Tim field "Kho tu lieu"
-> Chon type: URL -> nhap link  |  File -> upload file
-> Nhap text label (vd: "Xem kho tu lieu")
-> Next steps -> Submit
-> Done — frontend hien thi ngay
```

### KOC Xem

```
KOC mo trang Event
-> Thay button "Xem kho tu lieu" (hoac label admin dat)
-> Click -> mo link trong tab moi
```

---

## Assumptions

1. `ActionType` struct da stable, reuse truc tiep tu `backend/internal/model/mg/common.go`
2. News model (`NewsRaw.Action`) la reference pattern da hoat dong tot
3. Public API event detail da tra du fields — chi can them field moi vao response structs
4. Admin Event modal dung StepsForm — them field vao step Overview la hop ly nhat

---

## Out of Scope

- Nhieu tu lieu per event (chi 1 action)
- Trang quan ly tu lieu rieng
- Status active/inactive cho tu lieu (muon an thi xoa field)
- Order/sorting tu lieu
- Thumbnail rieng cho tu lieu

---

## Open Questions

1. **Nhieu link?** — Neu sau nay can nhieu tu lieu per event, co the doi sang `[]*ActionType`. Hien tai 1 link du chua?
2. **Vi tri tren frontend?** — Button kho tu lieu hien thi o dau tren trang event? (canh Guide? Header? Footer?)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-02 | Vinh Nguyen | Initial PRD (over-scoped) |
| 2.0 | 2026-04-02 | Vinh Nguyen | Simplified — chi them field ActionType vao Event |
| 3.0 | 2026-04-03 | Claude | Verified & updated against remote source code (`viewboost/ambassabor@master`). Fixed: file paths, struct names (`EventRaw` not `EventBSON`), request/response model paths, admin UI component details (StepsForm pattern), added FR-002 for request/response models, added reference to News ActionType pattern |
