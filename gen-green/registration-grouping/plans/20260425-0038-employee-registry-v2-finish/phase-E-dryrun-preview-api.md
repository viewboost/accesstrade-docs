# Phase E — Dry-run Backend + Preview API

## Context Links

- **Plan root:** [plan.md](plan.md)
- **Depends:** [phase-D-match-logic.md](phase-D-match-logic.md)
- **PRD:** FR-004 (dry-run preview), FR-016 (import_changes schema), §FR-004 sort priority
- **Research:** [research/researcher-02-admin-ui-preview.md](research/researcher-02-admin-ui-preview.md)

## Overview

- **Date:** 2026-04-25
- **Description:** Wire `MatchEngine` vào `GenerateDryRun(importID)` — persist `ImportChangeRaw{phase:preview}` records vào MongoDB. Expose `GET /imports/:importId/preview` với filter, sort priority, search, pagination. Auto-call dry-run sau parse.
- **Priority:** Must Have (block F UI)
- **Implementation Status:** Not Started
- **Review Status:** Pending

## Key Insights

- **Persistent preview** thay vì in-memory cache: store `ImportChangeRaw{phase:preview}` cho phép admin browse, filter, sort không mất data nếu reload. Cron daily TTL 24h cleanup orphan.
- **Sort priority** PRD §FR-004: cancelled_mismatch (1) > transferred (2) > missing_from_file (3) > auto_verified (4) > new_record (5) > no_match (6) > unchanged (7) > invalid (8). Lưu `priority int` field hoặc compute trong `$addFields` aggregation.
- **Filter "Chỉ ảnh hưởng hệ thống"** = filter `action IN [cancelled_mismatch, transferred, missing_from_file]` (3 actions đầu).
- **Auto-call dry-run sau parse:** `CreateImport` → parse → save `ImportChangeRaw` chưa có → call `GenerateDryRun(importID)` → return `ImportCreateResult{counters: {...}}`. Admin redirect đến preview page.

## Requirements

### FR-004 Dry-run preview

- `ImportChangeRaw{phase:preview}` 1 record / parse row + thêm records `missing_from_file` (Phase G.2 wire)
- Counters: 8 action types + total
- Preview list: filter action[], workplace, search (employeeCode, fullName, phone), sort priority asc/desc, pagination
- Default sort: priority asc (cancelled_mismatch first)

### FR-016 ImportChangeRaw schema (đã có đợt 1, dùng tiếp)

- `importId, userId?, employeeCode, action, reason?, field?, oldValue?, newValue?, actorType, phase, timestamp`
- Thêm field `priority int` (Phase E.1) — derived từ action enum

## Architecture

```
POST /v1/admin/employee-registry/import (đợt 1)
        │
        ▼
┌─────────────────────────────────────┐
│ CreateImport(file, uploader)        │
│  1. Parse Excel (đợt 1)             │
│  2. ImportHistoryRaw{status:preview}│
│  3. NEW: GenerateDryRun(importID)   │
│     - MatchEngine.GenerateChanges() │
│     - InsertMany(ImportChangeRaw)   │
│  4. Return {importId, counters}     │
└─────────────────────────────────────┘
        │
        ▼ (admin redirect)
GET /v1/admin/employee-registry/imports/:importId/preview
?action[]=cancelled_mismatch&workplace=HN&q=&page=1&pageSize=50&sortByPriority=true
        │
        ▼
┌─────────────────────────────────────┐
│ GetPreview(importID, query)         │
│  - Filter import_changes{phase:preview, importId}│
│  - Build counters aggregation       │
│  - Sort priority asc                │
│  - Paginate                         │
│  - Return {counters, list, pagination}│
└─────────────────────────────────────┘
```

## Related Code Files

| Action | File | Role |
|--------|------|------|
| EDIT | `backend/pkg/admin/service/employee_registry.go` | Thêm `GenerateDryRun(importID)` + wire vào `CreateImport` |
| CREATE | `backend/pkg/admin/handler/employee_registry_preview.go` | Handler `GetPreview` (hoặc thêm vào `employee_registry.go` đợt 1) |
| EDIT | `backend/pkg/admin/router/employee_registry.go` | Route `GET /imports/:importId/preview` |
| CREATE | `backend/pkg/admin/request/employee_registry_preview.go` | `PreviewQuery` body model |
| CREATE | `backend/pkg/admin/response/employee_registry_preview.go` | `PreviewResult{counters, list, pagination}`, `PreviewItem` |
| EDIT | `backend/pkg/admin/service/employee_registry_match.go` | (Phase D output) — không touch |
| REF | `backend/pkg/admin/service/employee_registry.go` (đợt 1) | `CreateImport` flow |
| REF | `backend/internal/model/mg/import_history.go` | `ImportChangeRaw` schema |

## Implementation Steps

### E.1 GenerateDryRun service method (~2h)

1. [20m] Define `priority` map action → int trong `pkg/admin/service/employee_registry_match.go` (hoặc constants):
   ```go
   var ActionPriority = map[string]int{
       "cancelled_mismatch":  1,
       "transferred":         2,
       "missing_from_file":   3,
       "auto_verified":       4,
       "new_record":          5,
       "no_match":            6,
       "unchanged":           7,
       "invalid":             8,
   }
   ```
2. [60m] EDIT `pkg/admin/service/employee_registry.go` thêm method:
   ```go
   func (e *employeeRegistryImpl) GenerateDryRun(ctx context.Context, importID string) (*MatchCounters, error) {
       // 1. Load parse rows từ MinIO file (re-parse) hoặc cache trong import_history
       // 2. matchResult, err := MatchEngine.GenerateChanges(rows, importID)
       // 3. Set Priority field cho mỗi change
       // 4. InsertMany(ImportChangeRaw{phase:preview})
       // 5. (Phase G.2) thêm missing_from_file scan
       // 6. Update ImportHistoryRaw counters
       // 7. Return counters
   }
   ```
3. [40m] Cleanup logic: nếu re-run dry-run cho cùng `importID` → delete existing `ImportChangeRaw{importId, phase:preview}` trước khi insert. Idempotent.

### E.2 Preview API + filter/sort/pagination (~1.5h)

1. [20m] `request.PreviewQuery`:
   ```go
   type PreviewQuery struct {
       Actions       []string `query:"action"`
       Workplace     string   `query:"workplace"`
       Q             string   `query:"q"` // search employeeCode/fullName/phone
       Page          int64    `query:"page"`
       PageSize      int64    `query:"pageSize"`
       SortByPriority bool    `query:"sortByPriority"`
   }
   ```
2. [20m] `response.PreviewResult`:
   ```go
   type PreviewResult struct {
       Counters   PreviewCounters `json:"counters"`
       List       []PreviewItem   `json:"list"`
       Pagination Pagination      `json:"pagination"`
   }
   type PreviewCounters struct {
       Total, AutoVerified, CancelledMismatch, Transferred, MissingFromFile,
       NewRecord, NoMatch, Unchanged, Invalid int64
   }
   type PreviewItem struct {
       ID, EmployeeCode, FullName, Phone, WorkplaceName, Action,
       Reason, OldValue, NewValue string
       UserID         *modelmg.AppID `json:",omitempty"`
       GenGreenUserURL string         // helper link admin/user/:id
       ImpactCount    int64          // số system entity bị ảnh hưởng (1 cho user-touching, 0 cho new_record/no_match)
       Priority       int
   }
   ```
3. [50m] Handler `GetPreview`:
   - Build query filter:
     ```go
     filter := bson.M{"importId": importID, "phase": "preview"}
     if len(query.Actions) > 0 { filter["action"] = bson.M{"$in": query.Actions} }
     if query.Workplace != "" { filter["workplaceName"] = query.Workplace }
     if query.Q != "" {
         filter["$or"] = bson.A{
             bson.M{"employeeCode": bson.M{"$regex": query.Q}},
             bson.M{"fullName": bson.M{"$regex": query.Q}},
             bson.M{"phone": bson.M{"$regex": query.Q}},
         }
     }
     ```
   - Counters: separate aggregation `$group` by `action`
   - Sort: `bson.D{{"priority", 1}, {"timestamp", -1}}` nếu `SortByPriority=true`
   - Pagination: skip + limit
4. [20m] Route `GET /v1/admin/employee-registry/imports/:importId/preview`:
   ```go
   group.GET("/imports/:importId/preview", handler.GetPreview)
   ```

### E.3 Wire dry-run vào CreateImport (~30m)

1. [20m] EDIT `pkg/admin/service/employee_registry.go` `CreateImport`:
   - Sau khi parse + save `ImportHistoryRaw{status:preview}` → call `GenerateDryRun(importID)` synchronously
   - Update return type `ImportCreateResult` thêm field `Counters PreviewCounters`
   - Async path defer Phase H (>1000 rows)
2. [10m] Smoke test: upload file 10 rows → response include counters

## Todo List

- [ ] E.1.1 Define `ActionPriority` map
- [ ] E.1.2 Impl `GenerateDryRun(importID)`
- [ ] E.1.3 Idempotent re-run (delete existing preview changes)
- [ ] E.1.4 Update `ImportHistoryRaw.counters` sau dry-run
- [ ] E.2.1 `request.PreviewQuery` model
- [ ] E.2.2 `response.PreviewResult`/`PreviewItem`/`PreviewCounters` models
- [ ] E.2.3 Handler `GetPreview` filter + sort + pagination + counters aggregation
- [ ] E.2.4 Route `GET /imports/:importId/preview`
- [ ] E.3.1 Wire `GenerateDryRun` vào `CreateImport`
- [ ] E.3.2 Update `ImportCreateResult.Counters`
- [ ] E.3.3 Smoke test 10-row file → counters chính xác

## Success Criteria

- [ ] Upload file 10 rows → response `{importId, counters: {total:10, ...}}`
- [ ] `GET /preview?action[]=cancelled_mismatch` chỉ trả mismatch records, counters total ≠ filtered count
- [ ] Sort priority asc default → cancelled_mismatch ở top
- [ ] Re-run dry-run cùng importID không duplicate `ImportChangeRaw` (idempotent)
- [ ] Pagination total chính xác = số records sau filter

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| InsertMany 1000 records timeout | MED | Batch 500/insertion. MongoDB driver hỗ trợ. Phase H async cho >1000. |
| Re-parse file từ MinIO chậm | LOW | Parse 1000 rows < 1s. Nếu chậm → cache parse output trong `import_history.parsedRowsBlob` (defer). |
| Counters drift khi re-run dry-run đồng thời 2 admin | MED | Status check `if status != "preview" skip`. Hoặc Redis lock theo `importId`. |
| Filter `$regex` injection | HIGH | Use `regexp.QuoteMeta(query.Q)` trước khi build regex. |
| Index miss trên `import_changes{importId, phase}` | HIGH | Đợt 1 đã add compound index `{importId:1, phase:1}`. Verify lại. |

## Security Considerations

- **Regex injection trong search:** `regexp.QuoteMeta()` escape `.*+?()[]{}|^$\` trong `query.Q` trước khi build `$regex`.
- **Pagination DoS:** Reject `pageSize > 200`, default 50, max 100.
- **Authorization:** Route admin-only (existing middleware). Không expose `import_changes` cho user role.
- **Audit:** `GenerateDryRun` không tạo audit (chỉ preview). Audit ghi ở Apply (F.2).
- **MinIO presigned URL TTL:** Re-parse từ MinIO yêu cầu credentials backend, không expose presigned cho client.

## Next Steps

→ Phase F [phase-F-ui-apply-rollback.md](phase-F-ui-apply-rollback.md): admin UI render counters + filter + table, Apply API thực sự gọi `VerifyStaff` + `UpdateWorkplace`, Rollback revert.
