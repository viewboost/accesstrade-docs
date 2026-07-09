# Technical Specification: Cập nhật trạng thái content hàng loạt bằng file Excel

**Date:** 2026-07-01
**Author:** vinhnguyen
**Version:** 1.0
**Project:** Gen-Green (vcreator)
**Project Level:** 1 (1–10 stories)
**Status:** Draft

---

## Document Overview

Tech spec cho feature **Cập nhật trạng thái content hàng loạt từ file Excel** trong admin Gen-Green. Focus kỹ thuật cho dev backend (Go) + frontend (UMI + DVA + AntD v4). Business/scope xem [`overview.md`](./overview.md); requirement testable xem [`prd.md`](./prd.md).

**Nguyên tắc chủ đạo:** feature này **clone pattern `employee-registry`** (đã chạy production) — đổi domain từ nhân sự sang content, đơn giản hóa logic phân loại (4 action, chỉ reject), **bỏ rollback**.

**Related code (đường dẫn thật, đọc trước khi code):**
- Model: `backend/internal/model/mg/import_history.go` (ImportHistoryRaw, ImportChangeRaw + constants)
- Model content: `backend/internal/model/mg/content.go` (ContentRaw: `Status`, `Reason`, `RejectedAt`, `RejectedBy`, `Title`, `Link`, `Author`)
- Parser tham chiếu: `backend/pkg/admin/service/employee_registry_parser.go` (`ParseExcel`, excelize)
- Service tham chiếu: `backend/pkg/admin/service/employee_registry.go` (`CreateImport`, `processImportAsync`, `GenerateDryRun`), `employee_registry_apply.go` (`ApplyImport` atomic lock)
- Match engine tham chiếu: `backend/internal/service/registry_match.go`
- Router tham chiếu: `backend/pkg/admin/router/employee_registry.go`
- Reject service reuse: `backend/internal/service/content.go` (`RejectListContentByIds`, `ActionAfterWhenChangeStatus`)
- Collections: `backend/internal/module/database/mongodb/collection.go` (`contents`, `import-histories`, `import-changes`)
- FE tham chiếu: `admin/src/pages/employee-registry/` (upload-modal, preview/, imports/, 3 DVA model, action-config.ts)

---

## Problem & Solution

### Problem
Ops hủy content lẻ từng cái trên UI. Mỗi đợt 50–500 content tốn 1–2 giờ, dễ sai, không audit.

### Solution
Upload `.xlsx` (ID content + Trạng thái mới + Lý do) → parse theo cột chuẩn → match với `contents` → preview phân loại 4 action → tick xác nhận → **bulk reject** (1 chiều). Reuse `import_history`/`import_changes`, cơ chế async (sync ≤1000 / async >1000 + Redsync), concurrency lock của employee-registry.

---

## Requirements

### What Needs to Be Built

1. **Excel Parser** (`content_status_import_parser.go`) — đọc `.xlsx` (excelize, `RawCellValue: true`), bỏ header + dòng trống, đọc 3 cột, validate row-level, aggregate errors.
2. **Match Engine** (`content_status_import_match.go`) — bulk query `contents` theo ID → phân 4 action.
3. **Import Service** (`content_status_import.go`) — `CreateImport`, `processImportAsync`, `GenerateDryRun`, `ApplyImport`, `CancelImport`, `GetImportStatus`, `GetPreview`, `GetImports`.
4. **Handler + Router** (`content_status_import.go` trong handler/router) — bind context, gọi service, map error → HTTP.
5. **Data model** — thêm `type` + counter content vào `import_history`; snapshot fields + action constants vào `import_changes`; `bulkImportId` optional vào `contents`; migration backfill.
6. **Admin FE** — clone folder `pages/content-status-import/`: upload modal + preview page + imports (history) + DVA models + action-config.

### What This Does NOT Include (phase 1)

- **Rollback** — không endpoint, không nút hoàn tác. Content đã reject phải phục hồi thủ công.
- **Target status khác `rejected`** — dòng khác `rejected` → `invalid`.
- **Label-header flexible mapping** — cột cố định theo template mẫu.
- **CSV** — chỉ `.xlsx`.
- **Partner scoping** — root/admin-only (như employee-registry).
- **Tách collection** — dùng chung `import-histories`/`import-changes`, phân biệt bằng `type`.

---

## Technical Approach

### Technology Stack

- **Backend:** Go 1.24+, package `viewboost`. Reuse `import_history` DAO, content reject service.
- **DB:** MongoDB — `contents`, `import-histories`, `import-changes`.
- **File storage:** MinIO (`minioclient.PutObject`), key: `content-status-imports/{importId}/{filename}`.
- **Concurrency:** `redisclient.NewMutexWithExpiration` (Redsync).
- **Frontend:** UMI v3 + DVA + AntD v4 (stack admin hiện tại).
- **Key libs (BE):** `github.com/xuri/excelize/v2` (parse), `crypto/sha256` (checksum), mongo-driver.

### Architecture Overview

```
[UploadModal] POST /content-status-import/import (multipart: file)
      │  echoupload.UploadSingle() → constants.KeyPayload = FileInfo
      ▼
[Handler.Import] → Service.CreateImport
      │  1. validate ext(.xlsx)+size(10MB)
      │  2. ParseExcel → rows + parseErrors  (max 5000 rows)
      │  3. checksum SHA256 → upload MinIO
      │  4. insert import_history (status=preview|processing, type=content_status)
      │  5. branch: ≤1000 sync GenerateDryRun ; >1000 spawn goroutine processImportAsync
      ▼
[GenerateDryRun] → MatchEngine.GenerateChanges
      │  bulk find contents by IDs → classify 4 action
      │  + build invalid changes từ parseErrors
      │  bulk insert import_changes (phase=preview) + compute counters
      ▼
[Response { importId, counters, status }] → FE redirect /preview

[Preview page] GET /imports/:id/preview (+ poll /status nếu processing)
      │  render counters + filter + table + footer checkbox
      │  tick "Xác nhận hủy N content" → POST /imports/:id/apply
      ▼
[Service.ApplyImport]
      │  atomic FindOneAndUpdate({importId,status:preview}→processing)  (else 409)
      │  load will_reject changes
      │  bulk reject content (reuse reject flow, reason per-change)
      │  import_changes.phase=applied ; import_history.status=completed
      ▼
[Response { applied, skipped, failed, errors[] }]
```

### Data Model

#### Reuse `import_history` — thêm `type` + counter content

`backend/internal/model/mg/import_history.go`:

```go
// MODIFY ImportHistoryRaw — thêm:
Type string `bson:"type"` // "employee_registry" | "content_status" (NEW)

// Counter content_status (dùng chung struct hoặc thêm field; đề xuất thêm field
// vì các *Count hiện tại đặt tên theo employee domain):
ContentTotal         int `bson:"contentTotal,omitempty"`
ContentWillReject    int `bson:"contentWillReject,omitempty"`
ContentAlreadyReject int `bson:"contentAlreadyReject,omitempty"`
ContentNotFound      int `bson:"contentNotFound,omitempty"`
ContentInvalid       int `bson:"contentInvalid,omitempty"`
ContentApplied       int `bson:"contentApplied,omitempty"`
ContentApplyFailed   int `bson:"contentApplyFailed,omitempty"`
```

> **Migration:** backfill `type = "employee_registry"` cho mọi record `import_history` hiện có (one-time script). Code đọc field với default `employee_registry` khi missing. **Regression test employee-registry** sau migration.

#### Reuse `import_changes` — thêm snapshot content + action

```go
// MODIFY ImportChangeRaw — thêm:
ContentID    *AppID `bson:"contentId,omitempty"`    // NEW
ContentTitle string `bson:"contentTitle,omitempty"` // snapshot cho preview
ContentLink  string `bson:"contentLink,omitempty"`  // snapshot
AuthorName   string `bson:"authorName,omitempty"`   // snapshot
TargetStatus string `bson:"targetStatus,omitempty"` // status đích đọc từ file
```

Constants (thêm vào `import_history.go`):

```go
const (
    ImportTypeEmployeeRegistry = "employee_registry" // đã tồn tại ngầm — khai báo tường minh
    ImportTypeContentStatus    = "content_status"     // NEW

    ImportChangeActionWillReject      = "will_reject"       // NEW
    ImportChangeActionAlreadyRejected = "already_rejected"  // NEW
    ImportChangeActionNotFound        = "not_found"         // NEW
    // ImportChangeActionInvalid — đã có, reuse
)
```

#### Reuse `contents` — thêm `bulkImportId` (optional, audit)

Khi apply set: `status=rejected`, `reason=<từ file hoặc default>`, `rejectedBy=<adminID>`, `rejectedAt=now`, `bulkImportId=<importId>`.

```go
// MODIFY ContentRaw — thêm:
BulkImportID string `bson:"bulkImportId,omitempty"` // NEW — audit đợt import
```

> Field content là **`Reason`** (không phải `rejectReason`) — theo `content.go`. Đừng đặt nhầm tên.

#### Indexes mới

```js
db.import-histories.createIndex({ type: 1, status: 1, timestamp: -1 })
db.import-changes.createIndex({ importId: 1, action: 1 })
db.import-changes.createIndex({ contentId: 1 }, { sparse: true })
db.contents.createIndex({ bulkImportId: 1 }, { sparse: true })
```

### API Design

Base: `/content-status-import` — auth `RequiredLogin` + `IsRoot` (clone group employee-registry).

| Method | Path | Mô tả |
|---|---|---|
| POST | `/import` | Upload `.xlsx` (multipart `file`) → parse + dry-run → lô preview |
| GET | `/imports` | List history (`?status=&page=&pageSize=`) — chỉ `type=content_status` |
| GET | `/imports/:importId/status` | Poll `{status, processedRows, percent}` |
| GET | `/imports/:importId/preview` | `{counters, list[], pagination}` (`?action=&page=&pageSize=`) |
| POST | `/imports/:importId/apply` | Body `{confirmed:true}` → `{applied, skipped, failed, errors[]}` |
| POST | `/imports/:importId/cancel` | Hủy preview |

Router (clone `employee_registry.go`, đặt route tĩnh trước động):

```go
func contentStatusImport(e *echo.Group) {
    g := e.Group("/content-status-import", a.RequiredLogin, a.IsRoot)
    g.POST("/import", h.Import, echoupload.UploadSingle())
    g.GET("/imports", h.GetImports, v.GetImports)
    g.GET("/imports/:importId/status", h.GetImportStatus)
    g.GET("/imports/:importId/preview", h.GetPreview, v.Preview)
    g.POST("/imports/:importId/apply", h.Apply, v.ApplyBody)
    g.POST("/imports/:importId/cancel", h.Cancel)
    // KHÔNG có /rollback
}
```

**`POST /import` response:**
```json
{
  "importId": "665f...hex",
  "status": "preview",            // hoặc "processing" nếu >1000 dòng
  "totalRows": 234,
  "counters": { "willReject": 187, "alreadyRejected": 12, "notFound": 5, "invalid": 30 }
}
```
Errors: `400 INVALID_FILE_FORMAT` · `400 FILE_TOO_LARGE` · `409 PENDING_IMPORT_EXISTS` · `500`.

**`POST /imports/:id/apply` response 200 / 207 (partial):**
```json
{ "importId": "665f...", "applied": 187, "skipped": 0, "failed": 0, "errors": [] }
```

### Excel Parser — cột chuẩn

Template mẫu (dòng 1 = header):

| ID content | Trạng thái mới | Lý do |
|---|---|---|
| 665f0a1b... | rejected | Link sản phẩm đã hết hàng |

```go
type ContentStatusRow struct {
    RowNum       int    // 1-indexed (header = 0)
    ContentID    string // cột "ID content" (raw)
    TargetStatus string // cột "Trạng thái mới" (raw, normalize lower/trim)
    Reason       string // cột "Lý do" (optional)
}

type ParseResult struct {
    TotalRows int
    ValidRows []ContentStatusRow
    Errors    []RowError // {Row, Column, Code, Message}
}

func ParseExcel(path string) (*ParseResult, error)
```

Row validation → error code:
- `ContentID` rỗng → `EMPTY_CONTENT_ID`; sai format ObjectID (`^[a-f0-9]{24}$`) → `INVALID_CONTENT_ID`
- `TargetStatus` rỗng → `EMPTY_TARGET_STATUS`; khác `rejected` (case-insensitive) → `UNSUPPORTED_TARGET_STATUS`
- Dòng trống hoàn toàn → bỏ qua (không tính, không lỗi)
- File hỏng/sheet trống → return err `ErrInvalidFileFormat`; >5000 dòng → `ErrFileTooLarge`

> Dùng `excelize.Options{RawCellValue: true}` để ID không bị ép sang số / mất leading char (bài học từ employee-registry).

### Match Engine (dry-run)

```go
func BuildContentStatusChanges(rows []ContentStatusRow) []*modelmg.ImportChangeRaw {
    // parse errors (rows invalid) đã tách ở parser → build invalid changes riêng

    ids := extractValidObjectIDs(rows)                 // chỉ rows đã pass parser
    contents := contentDAO.FindByIDs(ids)              // BULK query (1 lần)
    contentMap := indexByID(contents)

    var changes []*modelmg.ImportChangeRaw
    for _, r := range rows {
        c, ok := contentMap[r.ContentID]
        switch {
        case !ok:
            changes = append(changes, buildNotFound(r))
        case c.Status == constants.StatusRejected:
            changes = append(changes, buildAlreadyRejected(r, c))
        case isRejectable(c.Status):                    // waiting|waiting_approved|approved|pending|reviewing
            changes = append(changes, buildWillReject(r, c)) // snapshot Title/Link/Author
        default:
            changes = append(changes, buildInvalid(r, "STATUS_NOT_REJECTABLE")) // vd deleted
        }
    }
    return changes
}

func isRejectable(status string) bool {
    switch status {
    case constants.StatusWaiting, constants.StatusWaitingApproved,
         constants.StatusApproved, constants.StatusPending, constants.StatusReviewing:
        return true
    }
    return false
}
```

### Apply Logic (1 chiều, atomic, idempotent, reason per-change)

```go
func Apply(importID string, admin modelmg.StaffInfo) (ApplyResult, error) {
    // 1. Atomic lock (clone employee_registry_apply.go)
    h := importHistoryDAO.FindOneAndUpdate(
        bson.M{"importId": importID, "status": constants.ImportHistoryStatusPreview},
        bson.M{"$set": bson.M{"status": constants.ImportHistoryStatusProcessing}},
    )
    if h == nil { return ErrImportAlreadyProcessed } // 409

    changes := importChangesDAO.FindByImportIDAndAction(importID, "will_reject")
    defaultReason := fmt.Sprintf("Hủy hàng loạt từ import %s ngày %s",
        h.FileName, h.Timestamp.Format("02-01-2006"))

    var applied, failed int
    var errs []ApplyError
    for _, ch := range changes {
        reason := ch.Reason
        if reason == "" { reason = defaultReason }

        // Atomic per-content: chỉ update khi chưa rejected (concurrent safety)
        res := contentDAO.UpdateOne(
            bson.M{"_id": ch.ContentID, "status": bson.M{"$ne": constants.StatusRejected}},
            bson.M{"$set": bson.M{
                "status":       constants.StatusRejected,
                "reason":       reason,        // ⚠️ field content = "reason", KHÔNG phải rejectReason
                "rejectedBy":   admin.ID,
                "rejectedAt":   time.Now(),
                "bulkImportId": importID,
            }},
        )
        if res.MatchedCount == 0 {
            failed++; errs = append(errs, ApplyError{ContentID: ch.ContentID.Hex(), Reason: "concurrent_or_not_found"}); continue
        }
        applied++
        importChangesDAO.MarkApplied(ch.ID)
        // side-effect: notification + statistic — reuse ActionAfterWhenChangeStatus
        go internalservice.Content().NotifyRejected(ch.ContentID, reason) // fire-and-forget
    }

    importHistoryDAO.Complete(importID, applied, failed) // status=completed
    return ApplyResult{Applied: applied, Failed: failed, Errors: errs}, nil
}
```

> **Note reuse reject:** `internalservice.Content().RejectListContentByIds(ctx, ids, reason, staff)` (`content.go:281`) nhận **1 reason chung cho cả list** và tự gọi `ActionAfterWhenChangeStatus` (notification/side-effect). Hai lựa chọn:
> - **(A) Group theo reason** → gọi `RejectListContentByIds` mỗi nhóm reason. Đơn giản, reuse side-effect có sẵn, nhưng khó lấy per-item failure.
> - **(B) Loop per-change** (pseudocode trên) dùng reason từng dòng + gọi `ActionAfterWhenChangeStatus` thủ công per content → kiểm soát partial failure + atomic guard tốt hơn.
>
> **Đề xuất: (B)** để đúng AC partial-success + idempotent, nhưng phải gọi `ActionAfterWhenChangeStatus` (hoặc equivalent notify) cho mỗi content để nhất quán với reject tay. Xác nhận với dev owner content service trước khi code.

### Async & Concurrency (clone employee-registry)

- **Sync ≤1000 dòng:** `CreateImport` gọi thẳng `GenerateDryRun`, return `status=preview`.
- **Async >1000 dòng:** spawn goroutine `processImportAsync`, return `status=processing`; FE poll `/status` mỗi 3s.
  - Redsync mutex: `redisclient.NewMutexWithExpiration("content-status-import:"+importID, 30*time.Minute)`.
  - Recover panic → set `status=failed`. Update `processedRows` tăng dần.
- **Pending guard:** `findPendingImport(type=content_status, status ∈ {preview, processing})` → có thì upload mới trả 409 `PENDING_IMPORT_EXISTS`.
- **Apply lock:** atomic `FindOneAndUpdate` (trên) chống double-apply.

### Frontend (clone `pages/employee-registry/` → `pages/content-status-import/`)

- **UploadModal:** chỉ `.xlsx`, nút "Tải file mẫu" (`/content_status_import_template.xlsx`), **bỏ** checkbox `detectMissing` (không dùng). Async: poll status → redirect preview.
- **Preview page:** clone `preview/index.tsx` + components (counter-cards, filter, table, footer-actions). `action-config.ts` = 4 action (will_reject / already_rejected / not_found / invalid) + màu + label + priority. Footer checkbox "Xác nhận hủy N content"; nút Apply disabled khi `willReject=0` / chưa tick; snapshot mode khi status cuối. Poll khi `processing`.
- **Imports (history):** clone `imports/index.tsx` + table. **Bỏ cột/nút Rollback** (employee-registry đang disabled sẵn — xóa hẳn ở đây). Click row → mở preview snapshot.
- **DVA models:** 3 model (upload+poll / preview / imports) trỏ endpoint `/content-status-import/*`.
- **Route:** đăng ký `/content-status-import`, `/content-status-import/imports`, `/content-status-import/imports/:importId/preview` (ẩn menu, vào từ trang content). Nút "Cập nhật trạng thái hàng loạt" + "Lịch sử import" trên trang Danh sách content.

---

## Implementation Plan

### Stories

1. **STORY-1: Data model + migration** (1.5h) — thêm `type`+counter content vào `import_history`; snapshot+action vào `import_changes`; `bulkImportId` vào `contents`; migration backfill `type=employee_registry`; constants. Add indexes.
2. **STORY-2: Excel Parser + test** (2.5h) — `content_status_import_parser.go` + `_test.go` (fixture: dòng hợp lệ, thiếu ID, ID sai format, thiếu/khác target status, dòng trống). TDD.
3. **STORY-3: Match Engine + Upload API** (3h) — `content_status_import_match.go` (bulk query + 4 action) + `CreateImport` sync/async + `processImportAsync` + MinIO + pending guard. Match test thuần.
4. **STORY-4: Apply + Cancel + list/status API** (2.5h) — `ApplyImport` atomic + partial failure + reason per-change + side-effect notify; `CancelImport`; `GetPreview`/`GetImports`/`GetImportStatus`.
5. **STORY-5: Admin FE** (4h) — clone folder, adjust service+model+action-config, bỏ detectMissing/rollback, nút trên trang content.
6. **STORY-6: QA + E2E** (4h) — fixtures thực tế; test sync+async; apply→content rejected; cancel; 409 pending; double-apply idempotent; **regression employee-registry** sau migration.

### Phases
- **Phase 1 (BE, STORY-1→4):** ~9.5h → API testable qua Postman.
- **Phase 2 (FE, STORY-5):** ~4h, song song cuối Phase 1.
- **Phase 3 (QA, STORY-6):** ~4h.
- Tổng ~18h dev+QA + 2h PM = ~20h.

---

## Acceptance Criteria (rút gọn — đầy đủ ở prd.md)

- [ ] Upload `.xlsx` (ID/Trạng thái mới/Lý do) → redirect preview với counter 4 action đúng
- [ ] Cột không hợp lệ (thiếu ID / target khác `rejected`) → `invalid` kèm lý do
- [ ] Content đang `rejected` → `already_rejected` (no-op); ID không có → `not_found`
- [ ] File `.xlsx` với ID dạng số/leading zero → parse đúng (RawCellValue)
- [ ] >1000 dòng → async, poll tiến độ, xong redirect; >5000 → lỗi rõ ràng
- [ ] Tick xác nhận → content `will_reject` chuyển `status=rejected` + `reason`/`rejectedBy`/`rejectedAt`/`bulkImportId`
- [ ] Content bị hủy gửi notification cho creator (nhất quán reject tay)
- [ ] Double-click apply → chỉ apply 1 lần (409 lần 2)
- [ ] Cancel → `import_history` status=cancelled, không content nào đổi
- [ ] Lịch sử import list đúng lô `type=content_status`, click mở snapshot
- [ ] Upload lô 2 khi lô 1 chưa apply/cancel → 409 `PENDING_IMPORT_EXISTS`
- [ ] **Employee-registry import vẫn chạy đúng sau migration** (regression)
- [ ] **Không có** endpoint/nút rollback

---

## Non-Functional Requirements

**Performance:** ≤1000 dòng upload+preview <10s (P95); >1000 async không block; apply bulk, không loop query.
**Security:** admin-only (`RequiredLogin`+`IsRoot`); validate ext+size ở service; MinIO key có importId; sanitize ô preview chống formula injection; audit `uploadedBy`/`rejectedBy`.
**Reliability:** atomic apply lock; Redsync mutex TTL 30m; recover panic → `failed`; apply idempotent.
**i18n:** UI tiếng Việt; badge màu qua `action-config` single source.
**Logging:** INFO upload/apply success, ERROR parse/apply fail; mọi log kèm `importId`.

---

## Dependencies

- **Hệ thống:** `contents` + status enum; MinIO; Redis; admin auth middleware.
- **Code reuse:** `import_history`/`import_changes` DAO + pattern employee-registry; content reject flow (`RejectListContentByIds`/`ActionAfterWhenChangeStatus`); `echoupload.UploadSingle`, `minioclient`, `redisclient`, `internalservice.Audit`, `NewAppID().Hex()`.
- **Coupling:** migration `type` vào `import_history` touch record employee-registry → **bắt buộc regression test**.

---

## Risks & Mitigation

- **Migration `type` làm hỏng employee-registry** → backfill trước deploy; đọc field default `employee_registry`; regression test trước merge.
- **Ops upload nhầm → hủy nhầm (không rollback)** → preview + checkbox xác nhận; banner đỏ khi `willReject` lớn; đây là tradeoff đã chốt.
- **Reason per-content vs `RejectListContentByIds` (1 reason/list)** → dùng apply loop per-change (option B) hoặc group theo reason; xác nhận với owner content service.
- **Double-apply / multi-pod** → atomic `FindOneAndUpdate` + Redsync.
- **ID format lạ** → validate `^[a-f0-9]{24}$` ở parser, phát hiện sớm.
- **File lớn OOM** → cap 5000 dòng + 10MB ở parser/multipart.

---

## Next Steps

1. Tech Lead confirm chiến lược reuse `import_history` + apply option (A/B với content service owner).
2. Ops confirm scope (chỉ `rejected`, không rollback) + số dòng tối đa thực tế.
3. STORY-1 (migration) merge & deploy staging **trước** để unblock các story khác.
4. Chuẩn bị file `.xlsx` mẫu + fixtures thực tế từ Ops cho QA.

---

*Đọc kèm [`overview.md`](./overview.md) (business) + [`prd.md`](./prd.md) (requirement/AC).*
