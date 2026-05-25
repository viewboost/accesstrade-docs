# Technical Specification: Import file để hủy hàng loạt content

**Date:** 2026-05-11
**Author:** vinhnguyen
**Version:** 1.0
**Project:** Gen-Green (vcreator)
**Project Level:** 1 (1–10 stories)
**Status:** Draft

---

## Document Overview

Tech spec cho feature **Import CSV để hủy hàng loạt content** trong admin Gen-Green. Tài liệu này focus vào kỹ thuật cho dev backend (Go) + frontend (Next.js admin). Phần business/scope đã viết ở [`overview.md`](./overview.md).

**Related Documents:**
- Overview: [`overview.md`](./overview.md)
- Pattern tham chiếu: [`../registration-grouping/overview-v2-import-logic.md`](../registration-grouping/overview-v2-import-logic.md)
- Code reference: `vcreator/backend/internal/service/registry_match.go`, `vcreator/backend/internal/model/mg/import_history.go`

---

## Problem & Solution

### Problem Statement

Ops hiện phải hủy content lẻ từng cái trên admin UI. Mỗi đợt rà soát 50–500 content tốn 1–2 giờ thao tác, dễ sai sót, không có audit trail dễ tra cứu.

### Proposed Solution

Cho phép admin upload **file CSV xuất ra từ chức năng Data Export** (đã có sẵn), hệ thống parse theo **label header** (cột linh hoạt), match với DB, hiển thị **preview phân loại từng dòng**, admin **tick xác nhận** rồi apply hủy hàng loạt. Reuse pattern 2-phase (preview → apply) và collection `import_history` / `import_changes` của feature [registration grouping](../registration-grouping/overview-v2-import-logic.md).

---

## Requirements

### What Needs to Be Built

1. **CSV Parser theo label header** — nhận diện cột bằng text header (`ID`, `Lý do hủy`, `Trạng thái`), không theo thứ tự. Bắt buộc: `ID`. Optional: `Lý do hủy`, `Trạng thái`. Auto-detect encoding (UTF-8 / UTF-8-BOM / Windows-1258) + separator (`,` / `;`).

2. **Match Engine** — đối chiếu từng dòng CSV với collection `content` trong MongoDB → sinh ra 5 action:
   - `will_reject` — content tồn tại + status ∈ {`waiting_approved`, `approved`} → sẽ hủy
   - `already_rejected` — content tồn tại + status = `rejected` → no-op
   - `not_found` — `contentId` không tồn tại trong DB → skip + warning
   - `invalid` — dòng thiếu `ID` / `ID` sai format → skip + lỗi
   - `filtered_out` — file có cột `Trạng thái` nhưng value khác `rejected` → bỏ qua khỏi danh sách hủy

3. **API upload + preview** — admin upload CSV → BE parse + run match engine → lưu `import_history` (status=`preview`) + `import_changes` (phase=`preview`) → return `importId` để FE redirect sang preview page.

4. **API apply** — admin tick checkbox xác nhận → BE bulk update content status → `rejected`, set `rejectReason`. Cập nhật `import_history` status=`completed`, `import_changes` phase=`applied`.

5. **API cancel** — admin bỏ đợt preview → `import_history` status=`cancelled`, `import_changes` phase=`cancelled`.

6. **API list history + detail** — list các đợt import, xem chi tiết snapshot 1 đợt.

7. **Admin UI** — modal upload, preview page (table với counter/filter/badge action), lịch sử import.

8. **Concurrency lock** — chặn upload đợt mới khi đang có đợt cũ ở status `preview` hoặc `processing` (tương tự registration import).

### What This Does NOT Include

- **Rollback** — không có chức năng revert. Lỡ apply nhầm → Ops sửa thủ công.
- **Multi-action import** — chỉ hủy. Không có approve / restore / re-categorize qua import.
- **Async job + polling** — phase 1 dùng sync apply như registration (`processedRows` field có sẵn cho tương lai). File >5000 dòng sẽ reject ngay ở parser.
- **Public API / partner integration** — chỉ admin internal.
- **Notification customization** — dùng template hệ thống có sẵn.

---

## Technical Approach

### Technology Stack

- **Backend:** Go 1.24+, package `viewboost` (vcreator project). Reuse module `import_history` DAO.
- **Database:** MongoDB (collections: `content`, `import_history`, `import_changes`).
- **File storage:** MinIO (lưu file CSV gốc, key pattern: `imports/content-reject/{importId}/{filename}`).
- **Frontend:** Next.js admin (vcreator/admin). Reuse component pattern từ trang registration import preview.
- **Key libraries (BE):**
  - `encoding/csv` (stdlib) — parse CSV
  - `golang.org/x/text/encoding/charmap` — handle Windows-1258
  - `golang.org/x/text/encoding/unicode` — handle UTF-8 BOM
  - MongoDB driver hiện có
- **Key libraries (FE):** giữ stack hiện tại của admin (Next.js + UI lib hiện dùng).

### Architecture Overview

```
[Admin UI: Modal upload]
        │ POST /admin/imports/content-reject/upload (multipart: file + flag)
        ▼
[ImportContentRejectController.Upload]
        │
        ▼
[CSV Parser]
   - Detect encoding (BOM / UTF-8 / Windows-1258)
   - Detect separator
   - Read header row → map column index theo label
   - Validate required column `ID`
   - Stream rows → []ContentRejectRow (max 5000)
        │
        ▼
[Match Engine: BuildContentRejectChanges]
   - Bulk query: db.content.find({ _id: $in: contentIds })
   - Hash contentMap by contentId
   - Loop rows → classify action
   - (Nếu file có cột Trạng thái) áp filter trước classify
        │
        ▼
[Persist preview]
   - Insert import_history (status=preview, type=content_reject)
   - Insert []import_changes (phase=preview)
   - Upload raw CSV → MinIO
        │
        ▼
[Response: { importId, counters }]
        │
        ▼
[FE redirect → /admin/imports/content-reject/{importId}/preview]


[Admin UI: Preview page]
   - Fetch GET /admin/imports/content-reject/{importId}
   - Render counters + filter + table
   - User tick "Xác nhận hủy N content" → POST /apply
        │
        ▼
[ImportContentRejectService.Apply]
   - Verify status=preview, lock
   - For each will_reject change:
       updateOne({ _id: contentId, status: {$ne: rejected} },
                 { $set: { status: rejected, rejectReason, rejectedBy, rejectedAt }})
   - Update import_changes.phase=applied
   - Update import_history.status=completed, write counters
   - Trigger notification jobs (async fire-and-forget)
        │
        ▼
[Response: { applied, skipped, failed }]
```

### Data Model

#### Reuse: `import_history` (thêm `type` field)

Schema hiện tại trong `vcreator/backend/internal/model/mg/import_history.go`. **Thay đổi cần thiết:**

```go
// MODIFY: thêm field
type ImportHistoryRaw struct {
    // ... existing fields ...
    Type string `bson:"type"` // "employee_registry" | "content_reject" (NEW)
    // Counter fields hiện tại chỉ phù hợp employee_registry
    // → thêm counters domain-specific cho content_reject
    ContentRejectCounters *ContentRejectCountersRaw `bson:"contentRejectCounters,omitempty"`
}

// NEW
type ContentRejectCountersRaw struct {
    Total            int `bson:"total"`
    WillReject       int `bson:"willReject"`
    AlreadyRejected  int `bson:"alreadyRejected"`
    NotFound         int `bson:"notFound"`
    Invalid          int `bson:"invalid"`
    FilteredOut      int `bson:"filteredOut"`
    AppliedCount     int `bson:"appliedCount,omitempty"`
    AppliedFailedCount int `bson:"appliedFailedCount,omitempty"`
}
```

**Migration:** Tất cả record `import_history` hiện có default `type = "employee_registry"` (one-time backfill script).

#### Reuse: `import_changes`

Schema cũ có sẵn các field generic (`importId`, `action`, `reason`, `phase`, ...). **Thêm field cho domain content:**

```go
type ImportChangeRaw struct {
    // ... existing fields ...
    ContentID    *AppID `bson:"contentId,omitempty"`    // NEW
    ContentTitle string `bson:"contentTitle,omitempty"` // NEW — snapshot cho preview UI
    ContentLink  string `bson:"contentLink,omitempty"`  // NEW — snapshot
    AuthorName   string `bson:"authorName,omitempty"`   // NEW — snapshot
    EventCode    string `bson:"eventCode,omitempty"`    // NEW — snapshot từ cột "Mã sự kiện"

    // Action mới cho content_reject domain:
    // "will_reject" | "already_rejected" | "not_found" | "invalid" | "filtered_out"
}
```

**Constants thêm:**

```go
const (
    ImportTypeEmployeeRegistry = "employee_registry"
    ImportTypeContentReject    = "content_reject"

    ImportChangeActionWillReject       = "will_reject"
    ImportChangeActionAlreadyRejected  = "already_rejected"
    ImportChangeActionNotFound         = "not_found"
    ImportChangeActionFilteredOut      = "filtered_out"
    // ImportChangeActionInvalid đã có sẵn — reuse
)
```

#### Reuse: `content` collection

Không thêm column mới. Khi apply hủy, set:
- `status = "rejected"`
- `rejectReason = <reason từ CSV hoặc default>`
- `rejectedBy = <admin ID>`
- `rejectedAt = <now>`
- `bulkImportId = <importId>` (NEW field — optional, để audit)

**Migration:** Thêm field `bulkImportId` optional vào content schema (no-op cho existing records).

#### Indexes mới

```js
// import_history
db.import_history.createIndex({ type: 1, status: 1, timestamp: -1 })

// import_changes
db.import_changes.createIndex({ importId: 1, action: 1 })
db.import_changes.createIndex({ contentId: 1 }, { sparse: true })

// content
db.content.createIndex({ bulkImportId: 1 }, { sparse: true })
```

### API Design

Base path: `/admin/imports/content-reject`

| Method | Path | Mô tả | Auth |
|---|---|---|---|
| `POST` | `/upload` | Upload CSV, parse, match, persist preview. Multipart: `file` (binary), `dryRun` (bool, optional). | Admin |
| `GET` | `/{importId}` | Get import history + counters + changes (paginated). Query: `?action=will_reject&page=1&limit=50`. | Admin |
| `POST` | `/{importId}/apply` | Apply preview. Body: `{ confirmed: true }`. Trả về `{ applied, skipped, failed, errors[] }`. | Admin |
| `POST` | `/{importId}/cancel` | Hủy preview. | Admin |
| `GET` | `/history` | List các đợt import. Query: `?page=1&limit=20&status=completed`. | Admin |
| `GET` | `/{importId}/download` | Download lại file CSV gốc từ MinIO. | Admin |

#### Request/Response chi tiết

**`POST /upload`**

Request: multipart/form-data
- `file`: CSV file (max 10MB)
- (không có flag nào ở phase 1 — toàn bộ logic auto)

Response 200:
```json
{
  "importId": "imp_2026_05_11_abc123",
  "totalRows": 234,
  "counters": {
    "willReject": 187,
    "alreadyRejected": 12,
    "notFound": 5,
    "invalid": 8,
    "filteredOut": 22
  },
  "hasStatusColumn": true,
  "detectedColumns": ["ID", "Trạng thái", "Lý do hủy", "Tiêu đề", "..."],
  "previewUrl": "/admin/imports/content-reject/imp_2026_05_11_abc123/preview"
}
```

Error responses:
- `400 INVALID_CSV` — file không phải CSV / parse fail
- `400 MISSING_REQUIRED_COLUMN` — không có cột `ID`
- `400 FILE_TOO_LARGE` — >10MB hoặc >5000 dòng
- `409 IMPORT_IN_PROGRESS` — đang có import khác status=preview/processing
- `500 INTERNAL_ERROR`

**`POST /{importId}/apply`**

Request:
```json
{ "confirmed": true }
```

Response 200:
```json
{
  "importId": "imp_2026_05_11_abc123",
  "applied": 187,
  "skipped": 0,
  "failed": 0,
  "errors": []
}
```

Response 207 (partial):
```json
{
  "applied": 184,
  "skipped": 0,
  "failed": 3,
  "errors": [
    { "contentId": "abc123", "reason": "concurrent_update" }
  ]
}
```

### CSV Parser — Label Header Mapping

```go
// Reserved column labels (case-insensitive, trim spaces)
var ColumnAliases = map[string][]string{
    "id":     {"id", "ID", "content id", "mã content"},
    "status": {"trạng thái", "status", "trang thai"},
    "reason": {"lý do hủy", "ly do huy", "rejection reason", "reason"},
    // Snapshot fields (optional, dùng cho UI preview)
    "title":      {"tiêu đề", "title", "tieu de"},
    "link":       {"link", "url"},
    "author":     {"người đăng", "nguoi dang", "author"},
    "eventCode":  {"mã sự kiện", "event code", "ma su kien"},
}

// Parse flow:
// 1. Detect encoding: check BOM → UTF-8; else try UTF-8 decode → Windows-1258 fallback
// 2. Detect separator: count `,` vs `;` in first line
// 3. Read header row → normalize (lowercase, trim) → match aliases
// 4. Required: column `id` MUST exist → else error MISSING_REQUIRED_COLUMN
// 5. Stream rows, build []ContentRejectRow
```

Type definition:

```go
type ContentRejectRow struct {
    RowNum      int    // 1-indexed (header = 0)
    ContentID   string // raw từ cột ID
    StatusInFile string // raw từ cột Trạng thái (empty nếu không có cột)
    Reason      string // raw từ cột Lý do hủy
    Title       string // snapshot
    Link        string // snapshot
    Author      string // snapshot
    EventCode   string // snapshot
}
```

### Match Engine Logic (pseudocode)

```go
func BuildContentRejectChanges(rows []ContentRejectRow, hasStatusCol bool) []ImportChangeRaw {
    // Filter by status column if exists
    var processedRows []ContentRejectRow
    var filteredOut []ContentRejectRow
    for _, r := range rows {
        if hasStatusCol && !strings.EqualFold(r.StatusInFile, "rejected") {
            filteredOut = append(filteredOut, r)
            continue
        }
        processedRows = append(processedRows, r)
    }

    // Build set of contentIds, bulk query
    ids := extractIDs(processedRows)
    contents := contentDAO.FindByIDs(ids) // []Content
    contentMap := indexByID(contents)

    var changes []ImportChangeRaw
    for _, r := range processedRows {
        // Validate
        if r.ContentID == "" || !isValidObjectID(r.ContentID) {
            changes = append(changes, buildInvalidChange(r, "invalid_content_id"))
            continue
        }
        c, ok := contentMap[r.ContentID]
        if !ok {
            changes = append(changes, buildNotFoundChange(r))
            continue
        }
        if c.Status == constants.StatusRejected {
            changes = append(changes, buildAlreadyRejectedChange(r, c))
            continue
        }
        // will_reject (waiting_approved or approved)
        changes = append(changes, buildWillRejectChange(r, c))
    }
    for _, r := range filteredOut {
        changes = append(changes, buildFilteredOutChange(r))
    }
    return changes
}
```

### Apply Logic

```go
func Apply(importID string, adminID AppID) (ApplyResult, error) {
    // 1. Verify history status=preview, set processing (atomic)
    history := importHistoryDAO.AcquireForApply(importID)
    if history == nil { return ErrAlreadyApplied }

    // 2. Stream will_reject changes
    changes := importChangesDAO.FindByImportIDAndAction(importID, "will_reject")

    var applied, failed int
    var errors []ApplyError
    defaultReason := fmt.Sprintf("Hủy hàng loạt từ import %s ngày %s",
        history.FileName, history.Timestamp.Format("02-01-2026"))

    for _, ch := range changes {
        reason := ch.Reason
        if reason == "" { reason = defaultReason }

        // Atomic update: only if not already rejected (concurrent safety)
        res := contentDAO.UpdateOne(
            bson.M{"_id": ch.ContentID, "status": bson.M{"$ne": "rejected"}},
            bson.M{"$set": bson.M{
                "status":       "rejected",
                "rejectReason": reason,
                "rejectedBy":   adminID,
                "rejectedAt":   time.Now(),
                "bulkImportId": importID,
            }},
        )
        if res.MatchedCount == 0 {
            failed++
            errors = append(errors, ApplyError{ContentID: ch.ContentID, Reason: "concurrent_update_or_not_found"})
            continue
        }
        applied++
        // Mark change as applied
        importChangesDAO.MarkApplied(ch.ID)

        // Fire-and-forget notification
        go notifyContentRejected(ch.ContentID, reason)
    }

    // 3. Update history
    importHistoryDAO.Complete(importID, applied, failed)
    return ApplyResult{Applied: applied, Failed: failed, Errors: errors}, nil
}
```

---

## Implementation Plan

### Stories

1. **STORY-1: Data model + migration** (2h)
   Thêm field `type`, `contentRejectCounters` vào `import_history`; thêm field snapshot vào `import_changes`; thêm `bulkImportId` vào `content`; viết migration script backfill `type=employee_registry`. Add constants action types.

2. **STORY-2: CSV Parser service** (3h)
   `services/content_reject_parser.go` — encoding/separator detection, label header mapping, validation, stream rows. Unit test với fixtures (UTF-8 BOM, Windows-1258, có/không cột status, header lệch thứ tự).

3. **STORY-3: Match Engine + Upload API** (3h)
   `services/content_reject_import.go` — match logic, persist preview. Controller `POST /upload`. Concurrency lock check. MinIO upload raw file.

4. **STORY-4: Apply + Cancel API** (2h)
   `Apply()` với atomic update + partial failure handling. `Cancel()` set status=cancelled. `GET /{importId}` + `GET /history`. Atomic acquire-for-apply để chống double-click.

5. **STORY-5: Admin UI — Upload modal + Preview page** (4h)
   Modal upload với drag-drop + validation. Preview page reuse pattern từ registration: counter pills, filter dropdown (action/event/author), table với badge, top bar Cancel/Apply, footer checkbox xác nhận. Lịch sử import page.

6. **STORY-6: QA + E2E** (4h)
   Test fixtures: file đầy đủ, file không có cột Status, file Windows-1258, file >5000 rows, file có ID không tồn tại, file có ID format sai, concurrent upload, concurrent apply. Test với file CSV thực tế từ Ops.

### Development Phases

**Phase 1 (BE — STORY-1 → STORY-4):** ~10h. Backend xong → API có thể test qua Postman.
**Phase 2 (FE — STORY-5):** ~4h. Có thể chạy song song với cuối Phase 1.
**Phase 3 (QA — STORY-6):** ~4h. Sau khi BE+FE đều xong.

Tổng: ~18h dev + QA. Cộng 2h PM review = ~20h.

---

## Acceptance Criteria

- [ ] Upload file CSV (xuất từ Data Export type Content) thành công → redirect preview
- [ ] Preview hiển thị đúng counter 5 action types: `will_reject` / `already_rejected` / `not_found` / `invalid` / `filtered_out`
- [ ] File có cột "Trạng thái" → chỉ count `will_reject` cho dòng status=`rejected`, các dòng khác `filtered_out`
- [ ] File KHÔNG có cột "Trạng thái" → tất cả dòng valid được xét hủy
- [ ] Cột không theo thứ tự cố định — đổi vị trí cột vẫn parse OK
- [ ] File encoding khác nhau (UTF-8, UTF-8 BOM, Windows-1258) đều parse OK
- [ ] File quá 5000 dòng → error rõ ràng, không crash
- [ ] Tick checkbox xác nhận → Apply hủy đúng N content
- [ ] Sau Apply, vào DB check: content có `status=rejected`, `rejectReason`, `rejectedBy`, `rejectedAt`, `bulkImportId`
- [ ] Apply 2 lần liên tiếp (concurrent click) chỉ apply 1 lần (idempotent)
- [ ] Cancel preview → `import_history` status=cancelled, không content nào bị đổi
- [ ] Trang lịch sử import list được các đợt cũ kèm counters
- [ ] Click vào 1 đợt cũ → xem được snapshot đầy đủ (cả khi đã apply lâu rồi)
- [ ] Concurrent upload đợt thứ 2 khi đợt 1 chưa apply/cancel → 409 error
- [ ] Registration import (feature cũ) vẫn chạy bình thường, không bị ảnh hưởng

---

## Non-Functional Requirements

### Performance

- File ≤5000 dòng phải xử lý xong upload+preview trong **<10s** (P95).
- Apply 5000 dòng phải xong trong **<60s** (sync mode).
- Bulk query content + bulk write update — không loop 1-by-1 query DB.

### Security

- API chỉ accessible cho admin role (reuse middleware `requireAdminAuth` hiện có).
- Validate file: chỉ accept `.csv` extension + content-type `text/csv`/`application/vnd.ms-excel`.
- Audit trail: mọi action có `uploadedBy`, `rejectedBy` lưu admin ID.
- File MinIO key có UUID → không guessable.
- Sanitize CSV content khi render preview (chống CSV injection ở Excel — prefix `=`, `+`, `-`, `@` với `'`).

### Other

- **i18n:** UI tiếng Việt (admin Gen-Green chỉ tiếng Việt).
- **Browser support:** Chrome/Edge/Safari latest 2 versions (consistent với admin hiện tại).
- **Logging:** Log ở mức INFO cho upload/apply success, ERROR cho parse fail / apply fail. Include `importId` trong mọi log line để trace.

---

## Dependencies

- **Hệ thống:** MongoDB content collection + status enum hiện có; MinIO bucket; admin auth middleware.
- **Code:** Pattern + DAO của `import_history` / `import_changes` từ registration grouping. **Coupling:** Migration thêm field `type` vào `import_history` sẽ touch records của registration → cần test regression registration import.
- **Data:** File CSV xuất từ Data Export type Content (Ops cung cấp mẫu).
- **Team:** Không có dependency external.

---

## Risks & Mitigation

- **Risk:** Migration `type` field làm hỏng registration import.
  - **Mitigation:** Backfill script chạy trước deploy. Code đọc field với default `employee_registry` nếu missing. Regression test registration upload+apply trước khi merge.

- **Risk:** Ops upload nhầm file full export (không filter cột Trạng thái) → flag toàn bộ là `will_reject`.
  - **Mitigation:** UI hiển thị counter to + cảnh báo rõ "Sẽ hủy N content" trên checkbox xác nhận. Khi >100 will_reject, hiển thị banner màu đỏ.

- **Risk:** Concurrent apply (admin click 2 lần) → apply duplicate.
  - **Mitigation:** Atomic `AcquireForApply` ở DB level: `findOneAndUpdate({importId, status: preview}, {$set: {status: processing}})`. Click thứ 2 return null → 409.

- **Risk:** File CSV có ID format MongoDB lạ (UUID, số nguyên, ObjectID rút gọn).
  - **Mitigation:** Validate ID format match `^[a-f0-9]{24}$` (ObjectID). Sample file user gửi có ID 24 hex chars — OK. Nếu format khác sẽ phát hiện ngay từ row đầu.

- **Risk:** File CSV >10MB hoặc >5000 dòng → memory OOM.
  - **Mitigation:** Reject ở multipart limit + row counter trong streaming parser. Sample file thực tế ~234 dòng → 5000 là cap an toàn.

- **Risk:** Apply nhầm không có rollback.
  - **Mitigation:** Đã chấp nhận tradeoff (xem overview). 2 lớp xác nhận (preview + checkbox) là phòng tuyến chính. Ops sửa thủ công nếu lỡ.

---

## Timeline

**Target Completion:** 2026-05-20 (1.5 tuần tính từ kickoff)

**Milestones:**
- **2026-05-12** — Kickoff, STORY-1 (migration) merged
- **2026-05-15** — STORY-2 → STORY-4 done, BE API testable qua Postman
- **2026-05-18** — STORY-5 done, FE+BE integrated trên staging
- **2026-05-20** — QA pass + Ops UAT, production deploy

---

## Approval

**Reviewed By:**
- [ ] vinhnguyen (Author)
- [ ] Tech Lead Gen-Green
- [ ] Ops Manager (UAT representative)

---

## Next Steps

1. Tech Lead review tech spec → confirm reuse `import_history` strategy
2. Ops review overview → confirm scope (đặc biệt rule "trừ rejected") trước khi dev start
3. Create stories trong tracker (Jira/Linear) theo breakdown trong mục Implementation Plan
4. Story 1 (migration) phải merge & deploy staging **trước** các story khác để unblock

---

*Tech Spec này không thay thế overview — đọc kèm [`overview.md`](./overview.md) để có business context đầy đủ.*
