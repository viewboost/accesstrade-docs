# Phase A — Foundations

## Context Links

- **Plan root:** [plan.md](plan.md)
- **Prerequisites:** Branch `hotfix/group-users`, V1 go-live (user có `accountType`, `staffStatus`, `workplace*`)
- **PRD:** [prd-registration-v2-2026-04-12.md](../../prd-registration-v2-2026-04-12.md) — FR-001, FR-007, FR-015, FR-016, NFR-005
- **Research:**
  - [research/researcher-01-backend-patterns.md](research/researcher-01-backend-patterns.md) — MongoDB DAO pattern, Audit
  - [scout/scout-01-gaps.md](scout/scout-01-gaps.md) §Q4 DAO registration, §Q1 Workplace V1 model

## Overview

- **Date:** 2026-04-24
- **Description:** Móng backend cho V2 — refactor V1 actor support, thêm models/DAO registry + import history + import changes, util normalize phone, register MongoDB indexes.
- **Priority:** Must Have (block B, C)
- **Implementation Status:** Completed 2026-04-24
- **Review Status:** Approved 2026-04-24

## Key Insights

- Phase 0 refactor `VerifyStaff` là **non-breaking** — optional `actor *modelmg.StaffInfo`, nil → fallback gọi **helper mới** `internalservice.Staff().GetRoot(ctx)`. Helper wrap query `StaffRaw{isRoot:true}` (user verify: hiện **chỉ 1 call site raw** ở `pkg/public/service/opshub_webhook.go:161`). Refactor call site đó dùng helper luôn.
- `ImportHistoryRaw` + `ImportChangeRaw` là **bảng riêng**, KHÔNG reuse `AuditRaw` (user đã chốt) — lý do: schema khác (import_id, file_name, counters), audit V1 flat entry-per-change không fit batch import stats
- DAO factory pattern chuẩn: `XxxDAO() modelmg.XxxDAO { return &xxxDAO{DbShare: databasemongodb.GetDBShare()} }`
- Collection + index register là **2 nơi tách biệt**: `collection.go` (const) + `index.go` (unique + secondary)
- Phone normalize chuẩn: strip whitespace/`+`/`84-prefix`, reject length ≠ 10 → return `0xxxxxxxxx`

## Requirements

### FR-001 Employee Registry schema
- `employeeCode` unique, **không validate format** (user chốt: chấp nhận hết, chỉ trim whitespace + required)
- `fullName`, `phone` (normalized 10 số `0xxx...`), `workplaceName`
- `workplaceGroup` derived nullable (defer calculation sang đợt 2, field có sẵn)
- `status` enum `active|terminated` (default `active`)
- `genGreenUserId` nullable, `importedAt`, `importId`, `lastSeenImportId`

### FR-015/016 Import history + changes schema
- `import_history`: `importId`, `fileName`, `fileChecksum`, `filePath` (MinIO), `uploadedBy`, `timestamp`, `totalRecords`, counters (new/updated/autoVerified/cancelledMismatch/noMatch/missingFromFile/terminated), `status` enum `preview|processing|completed|failed|rolled_back`
- `import_changes`: `importId`, `userId?`, `employeeCode`, `action` enum, `reason?`, `field?`, `oldValue?`, `newValue?`, `actorType` (default `root_account`), `phase` enum `preview|applied`, `timestamp`

### FR-007 Phone normalize
- `NormalizePhone(raw string) (string, error)` — 10 số leading `0`
- Reject nếu sau strip còn ≠ 10 chữ số hoặc chứa non-digit

### Phase 0 Actor refactor
- **Tạo helper mới** `internalservice.Staff().GetRoot(ctx) (*modelmg.StaffRaw, error)` trong `internal/service/staff.go` (hoặc pkg tương đương). Wrap query `StaffRaw{isRoot:true}`, trả first match, log warning nếu count > 1.
- `VerifyStaff(ctx, userID, status, reason, actor *modelmg.StaffInfo) error` — old callers pass nil, nil fallback gọi `Staff().GetRoot(ctx)`
- `createAudit(ctx, payload, actor *modelmg.StaffInfo)` nếu cần — nil fallback cũng qua helper
- **Refactor call site hiện có** ở `pkg/public/service/opshub_webhook.go:161` dùng `Staff().GetRoot()` thay vì raw query, tránh duplicate
- Audit entry ghi `actorId`, `actorType` (`human_admin` | `root_account`)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│ pkg/util/phone.go          (standalone, no deps)        │
└─────────────────────────────────────────────────────────┘

┌──────────────────────────────┐   ┌────────────────────────┐
│ internal/model/mg/            │   │ internal/module/       │
│ - employee_registry.go        │   │ database/mongodb/      │
│ - import_history.go           │──▶│ - collection.go (const)│
│   (ImportHistoryRaw +         │   │ - index.go (CreateIdx) │
│    ImportChangeRaw)           │   │ - dao/employee_registry│
└──────────────────────────────┘   │ - dao/import_history   │
                                    └────────────────────────┘

┌──────────────────────────────┐
│ pkg/admin/service/user.go    │
│   VerifyStaff(..., actor)    │── fallback ──▶ StaffRaw{isRoot:true}
│ internal/service/audit.go    │
│   createAudit(..., actor)    │── ghi actorType
└──────────────────────────────┘
```

## Related Code Files

| Action | File | Role |
|--------|------|------|
| CREATE | `backend/internal/model/mg/employee_registry.go` | `EmployeeRegistryRaw` + `EmployeeRegistryDAO` interface |
| CREATE | `backend/internal/model/mg/import_history.go` | `ImportHistoryRaw` + `ImportChangeRaw` + 2 DAO interfaces |
| CREATE | `backend/internal/module/database/mongodb/dao/employee_registry.go` | DAO impl + factory |
| CREATE | `backend/internal/module/database/mongodb/dao/import_history.go` | DAO impl (2 factories cho history + change) |
| CREATE | `backend/pkg/util/phone.go` + `phone_test.go` | `NormalizePhone` pure util |
| EDIT | `backend/internal/module/database/mongodb/collection.go` | Thêm `CollectionEmployeeRegistry`, `CollectionImportHistory`, `CollectionImportChanges` |
| EDIT | `backend/internal/module/database/mongodb/index.go` | Register indexes (template line 260-292 workplace) |
| EDIT | `backend/pkg/admin/service/user.go:653-709` | `VerifyStaff` accept `actor *modelmg.StaffInfo` |
| EDIT | `backend/internal/service/audit.go` | `createAudit` accept actor nếu cần ghi `actorType` |
| REF | `backend/pkg/public/service/opshub_webhook.go:159-166` | Pattern query root staff `StaffRaw{isRoot:true}` — COPY |
| REF | `backend/internal/module/database/mongodb/dao/workplace_brand.go:8-22` | DAO factory template |
| REF | `backend/internal/model/mg/user.go` | Model `Raw` + `DbModelName()` convention |

## Implementation Steps

### A.1 Refactor V1 VerifyStaff + audit actor + Root helper (~1h15m)

1. [10m] Đọc `pkg/admin/service/user.go:653-709` `VerifyStaff` + `internal/service/audit.go` `createAudit`/`CreateAudits` + `pkg/public/service/opshub_webhook.go:161` raw query
2. [20m] **Tạo helper `internalservice.Staff().GetRoot(ctx) (*modelmg.StaffRaw, error)`**:
   - Check `internal/service/staff.go` tồn tại chưa. Nếu chưa, tạo file + interface + impl theo pattern các service khác
   - Impl query `StaffRaw{isRoot:true}` (optionally `deletedAt:nil`), sort ổn định (`createdAt asc`), `FindOne`
   - Log warning + count nếu có > 1 root (query `Count` trước khi `FindOne`, chỉ khi dev mode tránh overhead)
3. [10m] Refactor `opshub_webhook.go:161` dùng `internalservice.Staff().GetRoot(ctx)` thay raw query — smoke test webhook không break
4. [15m] Refactor `VerifyStaff(ctx, userID, status, reason, actor *modelmg.StaffInfo)`. Nếu `actor == nil` → gọi `Staff().GetRoot(ctx)`, wrap thành `StaffInfo`
5. [10m] Refactor `createAudit` / `CreateAudits` ghi `actorId` + `actorType` vào `AuditRaw` (field mới nếu chưa có). `actorType` = `"human_admin"` nếu actor từ request, `"root_account"` nếu fallback
6. [10m] Update existing callers `VerifyStaff(...)` truyền `nil` actor. `go build ./...` compile check

### A.2 Phone normalizer util + test (~1h)

1. [10m] Tạo `backend/pkg/util/phone.go` với `NormalizePhone(raw string) (string, error)`
2. [20m] Impl:
   - Strip whitespace, `+`, leading `84` → add leading `0`
   - Validate: only digits, len == 10, starts with `0`
   - Return `("0xxxxxxxxx", nil)` hoặc `("", ErrInvalidPhone)`
3. [30m] Tạo `phone_test.go` test cases:
   - `"+84886807963"` → `"0886807963"`
   - `"84886807963"` → `"0886807963"`
   - `" 0886807963 "` → `"0886807963"`
   - `"0886-807-963"` → error (chứa `-`)
   - `"088680796"` (9 số) → error
   - `""` → error

### A.3 Models + DAO (~3h)

1. [30m] Tạo `internal/model/mg/employee_registry.go`:
   ```go
   type EmployeeRegistryRaw struct {
       ID               modelmg.AppID `bson:"_id"`
       EmployeeCode     string        `bson:"employeeCode"`
       FullName         string        `bson:"fullName"`
       Phone            string        `bson:"phone"`
       WorkplaceName    string        `bson:"workplaceName"`
       WorkplaceGroup   string        `bson:"workplaceGroup,omitempty"`
       Status           string        `bson:"status"` // active | terminated
       GenGreenUserID   *modelmg.AppID `bson:"genGreenUserId,omitempty"`
       ImportedAt       time.Time     `bson:"importedAt"`
       ImportID         string        `bson:"importId"`
       LastSeenImportID string        `bson:"lastSeenImportId"`
       CreatedAt        time.Time     `bson:"createdAt"`
       UpdatedAt        time.Time     `bson:"updatedAt"`
   }
   func (e *EmployeeRegistryRaw) DbModelName() string { return CollectionEmployeeRegistry }
   type EmployeeRegistryDAO interface { GetShare() databasemongodb.IDatabase }
   ```
2. [45m] Tạo `internal/model/mg/import_history.go` chứa cả `ImportHistoryRaw` + `ImportChangeRaw`:
   - `ImportHistoryRaw`: ID, ImportID (unique), FileName, FileChecksum, FilePath, UploadedBy (AppID), Timestamp, TotalRecords, NewCount, UpdatedCount, AutoVerifiedCount, CancelledMismatchCount, NoMatchCount, MissingFromFileCount, TerminatedCount, Status
   - `ImportChangeRaw`: ID, ImportID, UserID (*AppID), EmployeeCode, Action, Reason, Field, OldValue, NewValue, ActorType, Phase, Timestamp
   - 2 DAO interfaces: `ImportHistoryDAO`, `ImportChangeDAO`
3. [45m] Tạo `internal/module/database/mongodb/dao/employee_registry.go`:
   ```go
   type employeeRegistryDAO struct { *databasemongodb.DbShare }
   func (d *employeeRegistryDAO) GetShare() databasemongodb.IDatabase { return d.DbShare.GetDatabase() }
   func EmployeeRegistryDAO() modelmg.EmployeeRegistryDAO {
       return &employeeRegistryDAO{DbShare: databasemongodb.GetDBShare()}
   }
   ```
4. [45m] Tạo `internal/module/database/mongodb/dao/import_history.go` với 2 factory `ImportHistoryDAO()` + `ImportChangeDAO()`
5. [15m] `go build ./...` verify compile clean

### A.4 Collection const + indexes (~1h)

1. [10m] Edit `internal/module/database/mongodb/collection.go`:
   ```go
   CollectionEmployeeRegistry = "employee-registries"
   CollectionImportHistory    = "import-histories"
   CollectionImportChanges    = "import-changes"
   ```
2. [40m] Edit `internal/module/database/mongodb/index.go` theo template line 260-292:
   - `employee-registries`: unique `{employeeCode:1}`; secondary `{phone:1}`, `{workplaceName:1}`, `{genGreenUserId:1}`, `{importId:1}`, `{lastSeenImportId:1}`
   - `import-histories`: unique `{importId:1}`; secondary `{timestamp:-1}`, `{status:1}`, `{uploadedBy:1}`
   - `import-changes`: secondary `{importId:1}`, `{userId:1}`, `{employeeCode:1}`; compound `{importId:1, phase:1}`
3. [10m] Run index creation (if there's a script/CLI, document it) — verify MongoDB đã tạo index qua shell `db.collection.getIndexes()`

## Todo List

- [x] A.1.1 Đọc và hiểu VerifyStaff + createAudit + opshub_webhook.go:161
- [x] A.1.2 Tạo helper `internalservice.Staff().GetRoot(ctx)` + log warning nếu > 1 root
- [x] A.1.3 Refactor `opshub_webhook.go:161` dùng helper
- [x] A.1.4 Refactor VerifyStaff accept optional actor, nil fallback `GetRoot()`
- [x] A.1.5 Refactor createAudit/CreateAudits ghi actorId + actorType
- [x] A.1.6 Update existing VerifyStaff callers truyền nil actor, compile clean
- [x] A.1.7 Regression test thủ công V1 verify/reject flow + OpsHub webhook auto-approve
- [x] A.2.1 Implement `NormalizePhone`
- [x] A.2.2 Unit test >= 8 cases pass (17 cases, 17 PASS)
- [x] A.3.1 Model `EmployeeRegistryRaw` + DAO interface
- [x] A.3.2 Model `ImportHistoryRaw` + `ImportChangeRaw` + 2 DAO interfaces
- [x] A.3.3 DAO impl `employee_registry.go`
- [x] A.3.4 DAO impl `import_history.go` (2 factories)
- [x] A.3.5 `go build ./...` clean
- [x] A.4.1 Thêm 3 collection const
- [x] A.4.2 Register indexes cho 3 collections
- [x] A.4.3 Verify indexes tạo thành công qua MongoDB shell

## Success Criteria

- [x] `NormalizePhone` test pass 100%, edge cases covered
- [x] `go build ./...` clean, `go vet` không warning
- [x] V1 verify/reject staff flow work identical như trước (regression pass)
- [x] `mongo> db["employee-registries"].getIndexes()` show unique index on `employeeCode`
- [x] `import_history.status=preview` có thể insert qua DAO test harness (hoặc stubbed)
- [x] Audit entries của V1 bây giờ có `actorType="human_admin"`, fallback root có `actorType="root_account"`

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Refactor V1 VerifyStaff break existing callers | HIGH | Keep signature backward-compat (optional actor pointer, nil = old behavior). Search tất cả callers compile-time. Test regression. |
| Multiple root staff trong `StaffRaw{isRoot:true}` | MED | Helper `GetRoot()` query `FindOne` sort ổn định (`createdAt asc`), count warning nếu > 1. Document ở audit log lần đầu fallback. |
| Refactor `opshub_webhook.go:161` break existing webhook | HIGH | Smoke test webhook payload trên staging. Helper `GetRoot()` return shape identical với raw query hiện có (same `*StaffRaw`). |
| Index duplicate khi đã có từ trước | LOW | `CreateIndexes` idempotent theo Mongo driver. Kiểm tra `index.go` existing pattern. |
| `AuditRaw` chưa có `actorType` field | MED | Nếu chưa có → add field `bson:"actorType,omitempty"` với default empty. Migration không cần (new field nullable). |
| Phone normalize edge case quốc tế | LOW | Scope đợt 1 chỉ VN number — reject input không khớp `0xxxxxxxxx`/`84xxxxxxxxx`/`+84xxxxxxxxx`. Document. |

## Security Considerations

- **Audit integrity:** `actorType="root_account"` chỉ được set qua path fallback có log rõ. Không cho phép caller pass arbitrary `actorType` từ request.
- **Root staff lookup:** Query `StaffRaw{isRoot:true, deletedAt:nil}` (hoặc equivalent filter) tránh lấy root đã disable.
- **Phone input:** `NormalizePhone` reject mọi input chứa ký tự non-digit sau khi strip `+84` prefix — tránh injection qua phone search.
- **BSON injection:** DAO dùng struct binding (bson tag), không build query từ string → an toàn.

## Next Steps

Sau khi Phase A xong → unblock Phase B (list API + admin UI + upload skeleton). Xem [phase-B-registry-list-upload-skeleton.md](phase-B-registry-list-upload-skeleton.md).

Đợt 2 sẽ dùng các models/DAO này cho:
- `EmployeeRegistryDAO.FindByEmployeeCode` / `FindByPhone` (match logic FR-008)
- `ImportHistoryDAO` ghi counters, update `status=completed/failed`
- `ImportChangeDAO` ghi per-record action (preview → applied)
