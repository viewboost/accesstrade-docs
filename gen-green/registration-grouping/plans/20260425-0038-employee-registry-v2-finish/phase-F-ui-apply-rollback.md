# Phase F — Dry-run UI + Apply + Rollback

## Context Links

- **Plan root:** [plan.md](plan.md)
- **Depends:** [phase-E-dryrun-preview-api.md](phase-E-dryrun-preview-api.md)
- **PRD:** FR-004 (preview UI), FR-006 (rollback), FR-008 (apply), §EPIC-003 actions
- **Research:** [research/researcher-02-admin-ui-preview.md](research/researcher-02-admin-ui-preview.md), [scout/scout-01-gaps.md](scout/scout-01-gaps.md) §Q2 UpdateWorkplace
- **Đợt 1 ref UI:** `admin/src/pages/employee-registry/` (DVA + Umi)

## Overview

- **Date:** 2026-04-25
- **Description:** Admin UI preview page với counter cards + filter + table + footer actions Apply/Rollback. Backend `ApplyImport` gọi V1 `VerifyStaff` + build mới `UpdateWorkplace`. `RollbackImport` revert qua `oldValue`. Import history list page.
- **Priority:** Must Have (UX-facing, block G)
- **Implementation Status:** Not Started
- **Review Status:** Pending

## Key Insights

- **Parallel split:** F.1 (UI agent đụng `admin/`) || F.2 + F.3 (backend agent đụng `pkg/admin/service/`). F.4 (history page UI) gộp với F.1.
- **Apply gọi V1 không duplicate logic:** `auto_verified` → `VerifyStaff(action="verify", actor=root)`; `cancelled_mismatch` → `VerifyStaff(action="reject", reason, actor=root)`; `transferred` → `UpdateWorkplace` mới (build trong F.2).
- **Rollback risk:** Nếu user đã modify profile sau apply → revert overwrite user changes. UI confirm dialog warn rõ. Document rủi ro.
- **DVA URL params caveat:** `useParams()` không có sẵn trong Umi 3.5 + DVA, dùng `match.params.importId` từ component props.
- **Idempotent apply:** Status check `if importHistory.status != "preview" return error`. Tránh double-apply khi 2 admin click.

## Requirements

### FR-004 Preview UI

- 8 counter cards (Statistic component) — color-coded theo priority
- Filter: multi-select action[], workplace dropdown, search input, toggle "Chỉ ảnh hưởng hệ thống" (3 actions đầu)
- Table 9 cột: STT, Mã NV, Họ tên, SĐT, Đơn vị, Action badge, Impact, Lý do, Gen-Green user link
- Footer: button Apply (primary), Hủy, Export CSV (defer scope)

### FR-008 Apply (gọi V1 reuse)

- Loop `ImportChangeRaw{phase:preview}`:
  - `auto_verified` → `VerifyStaff(userID, "verify", "", actor=root)`
  - `cancelled_mismatch` → `VerifyStaff(userID, "reject", reason, actor=root)` + clear `staffStatus`
  - `transferred` → `UpdateWorkplace(userID, workplace, actor=root)` (build mới)
  - `staff_removed` (Phase G.2 wire) → set `staffRemovalScheduledAt = now+7d`
  - `new_record` → `EmployeeRegistryDAO.InsertOne`
  - `no_match`, `unchanged` → no-op log
- Mark each `ImportChangeRaw.phase = applied`
- Update `ImportHistoryRaw.status = completed` + per-action counters

### FR-006 Rollback

- Loop `ImportChangeRaw{phase:applied}`:
  - Reverse: dùng `oldValue` set lại field user
  - `cancelled_mismatch` revert → `staffStatus=pending, employeeCode=oldCode`
  - `transferred` revert → `WorkplaceBrandCode=oldBrandCode`
  - `staff_removed_scheduled` revert → unset `staffRemovalScheduledAt`
- Mark `ImportChangeRaw.phase = rolled_back`
- Update `ImportHistoryRaw.status = rolled_back`
- **Document risk:** rollback overwrite user-modified profile

### `UpdateWorkplace` mới

- `func (u userImpl) UpdateWorkplace(ctx, userID AppID, workplace WorkplaceFields, actor *modelmg.StaffInfo) error`
- Pattern theo `VerifyStaff`: nilable actor, fallback `Staff().GetRoot()`, audit ghi `actorType`
- Update fields: `WorkplaceBrandCode`, `WorkplaceBrandName`, `WorkplaceCompanyCode`, `WorkplaceUnitCode`, `WorkplaceName`

## Architecture

```
Admin UI: /employee-registry/preview/:importId
        │
        ▼
DVA: employeeRegistryPreviewModel
        │ dispatch effects: getPreview, applyImport, rollbackImport
        ▼
Backend Routes
   GET  /imports/:importId/preview      → existing E.2
   POST /imports/:importId/apply        → ApplyImport
   POST /imports/:importId/rollback     → RollbackImport

ApplyImport(importID, actor=admin):
  ┌────────────────────────────────────────┐
  │ 1. Load ImportHistoryRaw + status check│
  │ 2. Load ImportChangeRaw{phase:preview} │
  │ 3. Per-record switch action:           │
  │    - auto_verified  → VerifyStaff verify│
  │    - cancelled_mis. → VerifyStaff reject│
  │    - transferred    → UpdateWorkplace  │
  │    - staff_removed  → set scheduled+7d │
  │    - new_record     → insert registry  │
  │ 4. Mark phase=applied per record       │
  │ 5. ImportHistoryRaw.status=completed   │
  └────────────────────────────────────────┘
```

## Related Code Files

| Action | File | Role |
|--------|------|------|
| CREATE | `admin/src/pages/employee-registry/preview/index.tsx` | Page route + connect DVA |
| CREATE | `admin/src/pages/employee-registry/preview/model.ts` | DVA namespace `employeeRegistryPreviewModel` |
| CREATE | `admin/src/pages/employee-registry/preview/components/counter-cards.tsx` | 8 Statistic counters |
| CREATE | `admin/src/pages/employee-registry/preview/components/filter.tsx` | Multi-select action + workplace + search + toggle |
| CREATE | `admin/src/pages/employee-registry/preview/components/table.tsx` | ProTable + RcTableNew 9 cột |
| CREATE | `admin/src/pages/employee-registry/preview/components/footer-actions.tsx` | Apply/Hủy/Export buttons |
| CREATE | `admin/src/pages/employee-registry/preview/service.ts` | API client |
| EDIT | `admin/src/pages/employee-registry/imports/index.tsx` | History list page (F.4) |
| EDIT | `admin/config/routes.ts` | Routes preview + history |
| CREATE | `backend/pkg/admin/service/employee_registry_apply.go` | `ApplyImport(importID, actor)` |
| CREATE | `backend/pkg/admin/service/employee_registry_rollback.go` | `RollbackImport(importID, actor)` |
| EDIT | `backend/pkg/admin/service/user.go` | NEW method `UpdateWorkplace(userID, workplace, actor)` |
| EDIT | `backend/pkg/admin/handler/employee_registry.go` | Handlers Apply + Rollback |
| EDIT | `backend/pkg/admin/router/employee_registry.go` | Routes apply + rollback |
| REF | `backend/pkg/admin/service/user.go:653-709` | `VerifyStaff` pattern (đợt 1 đã refactor) |

## Implementation Steps

### F.1 Admin UI Preview Page (~3h) — UI agent

1. [10m] Add route trong `admin/config/routes.ts`:
   ```ts
   { path: '/employee-registry/imports', component: './employee-registry/imports' },
   { path: '/employee-registry/preview/:importId', component: './employee-registry/preview' },
   ```
2. [40m] CREATE `preview/model.ts` DVA namespace `employeeRegistryPreviewModel`:
   ```ts
   state: { importId, counters, list, filter, pagination, applying }
   effects: { *getPreview, *apply, *rollback }
   reducers: { updateState }
   ```
3. [40m] CREATE `preview/components/counter-cards.tsx`:
   ```tsx
   const CARDS = [
     { type: 'cancelledMismatch', label: 'Hủy do mismatch', color: 'red', priority: 1 },
     { type: 'transferred', label: 'Chuyển đơn vị', color: 'orange', priority: 2 },
     { type: 'missingFromFile', label: 'Thiếu trong file', color: 'volcano', priority: 3 },
     { type: 'autoVerified', label: 'Auto verify', color: 'green', priority: 4 },
     { type: 'newRecord', label: 'Mới', color: 'blue', priority: 5 },
     { type: 'noMatch', label: 'Không match', color: 'gold', priority: 6 },
     { type: 'unchanged', label: 'Không đổi', color: 'default', priority: 7 },
     { type: 'invalid', label: 'Lỗi', color: 'magenta', priority: 8 },
   ];
   <Row gutter={[24,24]}>
     {CARDS.map(c => <Col span={6}><Statistic title={c.label} value={counters[c.type]} valueStyle={{color: c.color}}/></Col>)}
   </Row>
   ```
4. [40m] CREATE `preview/components/filter.tsx`:
   - `Select mode="multiple"` cho action[] (8 options)
   - Workplace `Select` (load from workplace_brands)
   - `Input.Search` cho q
   - `Switch` "Chỉ ảnh hưởng hệ thống" → set actions=[cancelled_mismatch, transferred, missing_from_file]
5. [40m] CREATE `preview/components/table.tsx`:
   - 9 cột: STT, Mã NV, Họ tên, SĐT, Đơn vị, Action (Tag color), Impact (số), Lý do, Gen-Green link
   - Sort theo `priority` server-side via `onChange`
   - Pagination 50/page
6. [30m] CREATE `preview/components/footer-actions.tsx`:
   - Button Apply primary danger → confirm dialog `Modal.confirm` với warn nội dung "Sau khi apply, các thay đổi sẽ ghi vào hệ thống. Rollback có thể overwrite thay đổi user-modified."
   - Button Hủy → router back
   - Button Export CSV (placeholder, scope sau)
7. [20m] CREATE `preview/index.tsx` page:
   ```tsx
   const Preview = ({ employeeRegistryPreviewModel, match, dispatch }) => {
     const importId = match.params.importId;
     useEffect(() => { dispatch({ type: 'employeeRegistryPreviewModel/getPreview', payload: { importId } }); }, [importId]);
     return <PageContainer><CounterCards/><Filter/><Table/><FooterActions/></PageContainer>;
   };
   export default connect(({ employeeRegistryPreviewModel }) => ({ employeeRegistryPreviewModel }))(Preview);
   ```
8. [20m] CREATE `preview/service.ts` — `getPreview`, `apply`, `rollback` API clients

### F.2 Apply backend (~1.5h) — Backend agent

1. [20m] CREATE `pkg/admin/service/user.go` thêm `UpdateWorkplace`:
   ```go
   func (u userImpl) UpdateWorkplace(ctx context.Context, userID modelmg.AppID, wp WorkplaceFields, actor *modelmg.StaffInfo) error {
       if actor == nil {
           root, _ := internalservice.Staff().GetRoot(ctx)
           actor = &modelmg.StaffInfo{ID: root.ID, IsRoot: true}
       }
       set := bson.M{
           "workplaceBrandCode": wp.BrandCode,
           "workplaceBrandName": wp.BrandName,
           "workplaceCompanyCode": wp.CompanyCode,
           "workplaceUnitCode": wp.UnitCode,
           "workplaceName": wp.Name,
           "updatedAt": time.Now(),
       }
       err := daomongodb.UserDAO().GetShare().UpdateById(ctx, new(modelmg.UserRaw), userID, bson.M{"$set": set})
       // audit ghi actorId, actorType
       return internalservice.Audit().Create(ctx, &modelmg.AuditRaw{
           UserID: userID, Action: "update_workplace",
           OldValue: oldWp, NewValue: wp, ActorID: actor.ID,
           ActorType: actor.ActorType(),
       })
   }
   ```
2. [50m] CREATE `pkg/admin/service/employee_registry_apply.go`:
   ```go
   func ApplyImport(ctx, importID string, actor *modelmg.StaffInfo) (*ApplyResult, error) {
       // 1. Load ImportHistoryRaw, check status == "preview"
       // 2. Lock redsync mutex "apply:" + importID, TTL 30m
       // 3. Set status = "processing"
       // 4. Load all ImportChangeRaw{importId, phase:preview}
       // 5. Loop:
       switch change.Action {
       case "auto_verified":
           userService.VerifyStaff(ctx, *change.UserID, "verify", "", actor)
       case "cancelled_mismatch":
           userService.VerifyStaff(ctx, *change.UserID, "reject", change.Reason, actor)
       case "transferred":
           userService.UpdateWorkplace(ctx, *change.UserID, parseWorkplaceFromNewValue(change.NewValue), actor)
       case "staff_removed":
           // set staffRemovalScheduledAt = now+7d (Phase G.2 wire)
           userService.ScheduleStaffRemoval(ctx, *change.UserID, time.Now().Add(7*24*time.Hour), actor)
       case "new_record":
           registryDAO.InsertOne(...)
       case "no_match", "unchanged":
           // no-op
       }
       // Mark change.phase = "applied"
       // 6. Update ImportHistoryRaw.status = "completed" + counters
   }
   ```
3. [20m] Handler `ApplyHandler(c echo.Context)` — extract `importId`, get actor from context (admin staff), call `ApplyImport`. Route `POST /imports/:importId/apply`.

### F.3 Rollback backend (~1h) — Backend agent

1. [40m] CREATE `pkg/admin/service/employee_registry_rollback.go`:
   ```go
   func RollbackImport(ctx, importID, actor) error {
       // 1. Status check: must be "completed"
       // 2. Lock mutex "rollback:" + importID
       // 3. Load ImportChangeRaw{importId, phase:applied}
       // 4. Loop reverse:
       switch change.Action {
       case "auto_verified":
           // revert: set staffStatus=pending, clear staffVerifiedAt
       case "cancelled_mismatch":
           // revert: set staffStatus=pending, employeeCode=change.OldValue
       case "transferred":
           // revert: UpdateWorkplace với OldValue
       case "staff_removed":
           // revert: unset staffRemovalScheduledAt
       case "new_record":
           // revert: delete EmployeeRegistryRaw
       }
       // Mark phase = "rolled_back"
       // Update history.status = "rolled_back"
   }
   ```
2. [20m] Handler + route `POST /imports/:importId/rollback`

### F.4 Imports history list UI (~30m) — UI agent

1. [10m] CREATE `admin/src/pages/employee-registry/imports/index.tsx`:
   - List `ImportHistoryRaw` (cần backend route `GET /v1/admin/employee-registry/imports?page&pageSize` — đợt 1 chưa làm, thêm route ở Phase F)
   - Cột: timestamp, fileName, uploadedBy, status badge, totalRecords, action buttons (Preview / Rollback)
2. [10m] Reuse table pattern từ Phase B (đợt 1) — RcTableNew + ProColumns
3. [10m] CREATE backend `GET /imports` route + handler nếu chưa có (~10m thêm vào F.2 backend agent)

## Todo List

- [ ] F.1.1 Add routes preview + history vào `routes.ts`
- [ ] F.1.2 DVA model `employeeRegistryPreviewModel`
- [ ] F.1.3 Counter cards 8 actions
- [ ] F.1.4 Filter (multi-select + search + toggle)
- [ ] F.1.5 Table 9 cột + sort priority
- [ ] F.1.6 Footer actions với confirm dialog
- [ ] F.1.7 `preview/index.tsx` page wiring
- [ ] F.1.8 `preview/service.ts` API client
- [ ] F.2.1 `UpdateWorkplace` method trong `pkg/admin/service/user.go`
- [ ] F.2.2 `ApplyImport` service với 6 action switch
- [ ] F.2.3 Status check + redsync lock + mark phase=applied
- [ ] F.2.4 Update `ImportHistoryRaw.status=completed` + counters
- [ ] F.2.5 Apply handler + route
- [ ] F.3.1 `RollbackImport` service reverse logic
- [ ] F.3.2 Status check completed → rolled_back
- [ ] F.3.3 Rollback handler + route
- [ ] F.4.1 History list UI page
- [ ] F.4.2 Backend route `GET /imports` (nếu chưa có)

## Success Criteria

- [ ] Admin upload file → redirect `/preview/:importId` → counter cards hiển thị 8 numbers
- [ ] Filter "Chỉ ảnh hưởng hệ thống" → table chỉ show 3 action types
- [ ] Apply 100 rows < 10s, status updates đúng
- [ ] V1 verify/reject flow KHÔNG break (regression test)
- [ ] Concurrent apply 2 admin → second nhận 409 Conflict
- [ ] Rollback completed import → user fields revert đúng `oldValue`
- [ ] Rollback đã rollback → reject "Already rolled back"
- [ ] Audit có entries với `actorType=human_admin` cho mỗi user touch

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Apply 1000 rows timeout (>30s default) | HIGH | Per-record commit, no transaction. Async path Phase H >1000. Sync path 500 rows max ~15s. |
| `UpdateWorkplace` field mismatch (BrandCode vs Code) | MED | Reuse models từ existing user.workplace*. Test với real data. |
| Rollback overwrite user-modified profile | HIGH | UI confirm dialog warn rõ. Document trong PRD. Defer "smart rollback" check user.updatedAt > applied.timestamp. |
| Concurrent apply 2 admin | HIGH | redsync mutex `apply:importID` + status check `if status != "preview" return 409`. |
| `VerifyStaff` reject với reason rỗng | MED | Default reason "Mismatch HR data" nếu `change.Reason == ""`. |
| Notification spam 1000 users cùng lúc | MED | Phase G.5 wire — recommend batch hoặc rate-limit. Phase F không gửi notification. |
| Audit table bloat 1000 entries / import | LOW | Acceptable, audit retention chính sách hiện tại. |

## Security Considerations

- **Authorization Apply/Rollback:** Admin role check ở handler (existing middleware). Log `actorId` từ JWT.
- **Audit `actorType=human_admin`:** Apply path có actor từ request → `actorType=human_admin`, không fallback root. Trace responsibility.
- **Rollback access control:** Same admin role. Document log warn rollback action với high visibility (Slack alert defer).
- **CSRF preview API:** POST routes có CSRF token verify (existing).
- **Rate limit Apply:** Defer. Per-import idempotent qua status check đủ cho v1.
- **Input validation `:importId`:** Validate ObjectID format, reject otherwise.

## Next Steps

→ Phase G [phase-G-lifecycle-notify.md](phase-G-lifecycle-notify.md): wire missing_from_file detection vào dry-run, grace period cron, register hook FR-009, notification 5 types.
