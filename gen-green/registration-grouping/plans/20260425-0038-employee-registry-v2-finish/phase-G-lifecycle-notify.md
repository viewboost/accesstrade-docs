# Phase G — Lifecycle: Transferred + Missing + Grace + Notify + Register Hook

## Context Links

- **Plan root:** [plan.md](plan.md)
- **Depends:** [phase-F-ui-apply-rollback.md](phase-F-ui-apply-rollback.md)
- **PRD:** FR-011 (transferred), FR-012 (missing_from_file), FR-013 (grace 7d), FR-009 (register hook), FR-014 (notify)
- **Research:** [research/researcher-01-backend-patterns.md](research/researcher-01-backend-patterns.md) §1 cron, §2 notification, §3 register flow; [scout/scout-01-gaps.md](scout/scout-01-gaps.md) §Q3 cron

## Overview

- **Date:** 2026-04-25
- **Description:** Hoàn thiện lifecycle V2: missing_from_file detect, 7-day grace cron, register hook FR-009 auto-verify, 5 notification types wire-up. Transferred (FR-011) đã wire trong F.2 — confirm only.
- **Priority:** Must Have
- **Implementation Status:** Not Started
- **Review Status:** Pending

## Key Insights

- **G.1 Transferred là re-verify, không task riêng:** Match engine (Phase D) đã generate `action=transferred`. Apply (F.2) đã call `UpdateWorkplace`. G.1 chỉ confirm flow đúng.
- **G.2 Missing detection:** Scan `EmployeeRegistryDAO.Find(WHERE lastSeenImportId != currentImportID AND status=active)` trong `GenerateDryRun`. Tạo `ImportChangeRaw{action:missing_from_file, phase:preview}`. UI checkbox xác nhận-2 trong footer.
- **G.3 Grace period 7d:** Field `staffRemovalScheduledAt` trong `UserRaw`. Cron daily 00:00 VN scan `< now() AND staffStatus=pending_removal` → `RemoveStaffTag`. Daily granularity acceptable.
- **G.4 Register hook FR-009:** `MatchEngine.LookupSingle` (đã có Phase D.2.5) called từ `CompleteProfile` after submit `employeeCode`. 3 paths: A auto_verified, B inline error, C pending.
- **G.5 Notification 5 types:** Constants trong `internal/constants/notification.go`. `Notification().Push()` từ Apply (F.2 wire) cho mỗi successful action.
- **Parallel split:** G.3 cron + G.4 register hook + G.1+G.2+G.5 (apply.go agent) — 3 file-disjoint agents.

## Requirements

### FR-011 Transferred

- ✅ Detect: Phase D.2 match engine action `transferred` khi `existingUser.WorkplaceBrandCode != row.brandCode`
- ✅ Apply: Phase F.2 `UpdateWorkplace`
- G.1 confirm: notification `workplace_updated` push (G.5 wire)

### FR-012 Missing from file

- Trong `GenerateDryRun` (Phase E.1) thêm bước:
  - Scan `EmployeeRegistryDAO.Find(WHERE status=active AND lastSeenImportId != currentImportID)`
  - Insert `ImportChangeRaw{action:missing_from_file, employeeCode, phase:preview}` 1 record / missing
  - Counter `MissingFromFile`
- UI Phase F.1 thêm checkbox "Xác nhận terminate N nhân viên" trong footer trước Apply
- Apply (F.2) chỉ xử missing_from_file nếu admin tick checkbox → set `staffRemovalScheduledAt = now+7d`

### FR-013 Grace period 7 ngày

- New field `UserRaw.StaffRemovalScheduledAt *time.Time`
- New status const `StaffStatusPendingRemoval = "pending_removal"`
- Cron `RunStaffRemovalCron(ctx)`:
  ```go
  filter := bson.M{
    "staffRemovalScheduledAt": bson.M{"$lt": time.Now()},
    "staffStatus": "pending_removal",
  }
  // For each: RemoveStaffTag(userID, actor=root)
  // RemoveStaffTag = clear accountType, clear workplace*, clear employeeCode,
  //                  set staffStatus="", notify "staff_removed"
  ```
- Schedule: `c.AddFunc("0 0 0 * * *", scheduleService.RunStaffRemovalCron)` daily 00:00 VN

### FR-009 Register hook

- Trong `pkg/public/service/user.go` `CompleteProfile`:
  - Nếu `body.EmployeeCode != ""`:
    - `result := MatchEngine.LookupSingle(ctx, body.EmployeeCode, normalizedPhone)`
    - Kịch bản A (`result.Match == true`):
      - set `staffStatus = "verified"`, `staffVerifiedAt = now`, `workplaceBrandCode/...` từ registry
      - link `EmployeeRegistryRaw.GenGreenUserID = userID`
      - Push notification `auto_verified`
    - Kịch bản B (`result.Match == false`):
      - return inline error 400 `{code: "REGISTRY_MISMATCH", message: "Thông tin không khớp dữ liệu HR. Vui lòng kiểm tra lại SĐT và mã nhân viên"}`
      - **không** save profile (rollback transaction)
    - Kịch bản C (`result.Registry == nil`):
      - set `staffStatus="pending"` (như cũ)
      - **không** notify

### FR-014 Notification 5 types

- 5 constants mới trong `internal/constants/notification.go`:
  ```go
  NotificationTypeAutoVerified = "auto_verified"
  NotificationTypeCancelledMismatch = "cancelled_mismatch"
  NotificationTypeWorkplaceUpdated = "workplace_updated"
  NotificationTypeStaffRemovedScheduled = "staff_removed_scheduled"
  NotificationTypeStaffRemoved = "staff_removed"
  ```
- Wire trong Phase F.2 `ApplyImport` per-action call `Notification().Push()` với title/content Vietnamese theo PRD §FR-014.

## Architecture

```
Phase E (đã có) GenerateDryRun
        │ + G.2 missing scan
        ▼
ImportChangeRaw{phase:preview} (8 actions)
        │
        ▼
Phase F (đã có) ApplyImport
        │ + G.5 notify per action
        ▼
       ┌────────────────────────┐
       │ User updated           │
       │ + staffRemovalScheduled│ ──┐
       └────────────────────────┘   │
                                    │ daily cron 00:00
                                    ▼
                         RunStaffRemovalCron
                                    │
                                    ▼
                         RemoveStaffTag + notify

Public flow: POST /users/complete-profile (FR-009)
        │
        ▼
   CompleteProfile + LookupSingle
        │
        ├── A → verified + notify auto_verified
        ├── B → 400 REGISTRY_MISMATCH (no save)
        └── C → pending (no notify)
```

## Related Code Files

| Action | File | Role |
|--------|------|------|
| EDIT | `backend/internal/model/mg/user.go` | Field `StaffRemovalScheduledAt *time.Time` |
| EDIT | `backend/internal/constants/staff.go` | Const `StaffStatusPendingRemoval` |
| EDIT | `backend/internal/constants/notification.go` | 5 notification type constants |
| CREATE | `backend/pkg/admin/service/staff_removal_cron.go` | `RunStaffRemovalCron` |
| EDIT | `backend/pkg/admin/schedule/init.go` | AddFunc `0 0 0 * * *` daily |
| EDIT | `backend/pkg/admin/service/employee_registry.go` | `GenerateDryRun` thêm missing scan (G.2) |
| EDIT | `backend/pkg/admin/service/employee_registry_apply.go` | Wire `Notification().Push()` per action (G.5), wire `staff_removed` action set scheduledAt |
| EDIT | `backend/pkg/public/service/user.go` | `CompleteProfile` + `LookupSingle` integration (G.4) |
| EDIT | `backend/pkg/admin/service/user.go` | New method `RemoveStaffTag(userID, actor)` |
| EDIT | `admin/src/pages/employee-registry/preview/components/footer-actions.tsx` | Checkbox "Xác nhận terminate N nhân viên" |
| REF | `backend/pkg/public/service/schedule.go` | Cron pattern existing |
| REF | `backend/internal/service/notification.go` | `Push(ctx, []*NotificationRaw) error` |

## Implementation Steps

### G.1 Transferred confirm (~0m, no task) — gộp vào G.5

- Phase D.2 đã generate `action=transferred`
- Phase F.2 đã call `UpdateWorkplace`
- G.5 wire notification `workplace_updated` cho action này

### G.2 Missing from file detection (~1.5h)

1. [10m] EDIT `pkg/admin/service/employee_registry.go` `GenerateDryRun` thêm sau khi insert match changes:
   ```go
   // Scan registry với lastSeenImportId != currentImportID
   missingRegistry := []EmployeeRegistryRaw{}
   filter := bson.M{
       "status": "active",
       "lastSeenImportId": bson.M{"$ne": importID},
   }
   registryDAO.Find(ctx, &missingRegistry, filter)
   for _, m := range missingRegistry {
       changes = append(changes, &ImportChangeRaw{
           ImportID: importID, EmployeeCode: m.EmployeeCode,
           UserID: m.GenGreenUserID,  // có thể nil nếu chưa link
           Action: "missing_from_file",
           Phase: "preview",
           Priority: 3,
           Timestamp: time.Now(),
       })
   }
   counters.MissingFromFile = len(missingRegistry)
   ```
2. [40m] EDIT `pkg/admin/service/employee_registry_apply.go` thêm case `missing_from_file`:
   ```go
   case "missing_from_file":
       if !req.ConfirmTerminate {
           // Skip nếu admin không tick checkbox
           continue
       }
       userService.ScheduleStaffRemoval(ctx, *change.UserID, time.Now().Add(7*24*time.Hour), actor)
       // change.action = "staff_removed_scheduled" applied
   ```
3. [30m] EDIT `admin/src/pages/employee-registry/preview/components/footer-actions.tsx` thêm `Checkbox`:
   ```tsx
   <Checkbox checked={confirmTerminate} onChange={...}>
     Xác nhận terminate {counters.missingFromFile} nhân viên (sau 7 ngày grace period)
   </Checkbox>
   <Button disabled={counters.missingFromFile > 0 && !confirmTerminate} onClick={apply}>Apply</Button>
   ```
4. [10m] Pass `confirmTerminate` flag vào `POST /apply` body. Backend verify

### G.3 Grace period 7d cron (~1h)

1. [10m] EDIT `internal/model/mg/user.go` thêm field:
   ```go
   StaffRemovalScheduledAt *time.Time `bson:"staffRemovalScheduledAt,omitempty"`
   ```
2. [5m] EDIT `internal/constants/staff.go`:
   ```go
   StaffStatusPendingRemoval = "pending_removal"
   ```
3. [5m] EDIT `pkg/admin/service/user.go` thêm method `ScheduleStaffRemoval(userID, scheduledAt, actor) error`:
   - Set `staffStatus=pending_removal`, `staffRemovalScheduledAt=scheduledAt`
   - Audit ghi `actorType`
   - Push notification `staff_removed_scheduled` (defer G.5 wire)
4. [10m] Thêm method `RemoveStaffTag(userID, actor) error`:
   - Clear `accountType`, `workplace*`, `employeeCode`, `staffStatus`, `staffRemovalScheduledAt`
   - Audit + notification `staff_removed`
5. [25m] CREATE `pkg/admin/service/staff_removal_cron.go`:
   ```go
   func (s *scheduleImpl) RunStaffRemovalCron() {
       ctx := context.Background()
       filter := bson.M{
           "staffRemovalScheduledAt": bson.M{"$lt": time.Now()},
           "staffStatus": "pending_removal",
       }
       users := []*modelmg.UserRaw{}
       userDAO.Find(ctx, &users, filter)
       root, _ := internalservice.Staff().GetRoot(ctx)
       actor := &modelmg.StaffInfo{ID: root.ID, IsRoot: true}
       for _, u := range users {
           if err := userService.RemoveStaffTag(ctx, u.ID, actor); err != nil {
               log.Errorf("RemoveStaffTag fail userID=%s: %v", u.ID.Hex(), err)
               continue
           }
       }
       log.Infof("RunStaffRemovalCron: removed %d staffs", len(users))
   }
   ```
6. [5m] EDIT `pkg/admin/schedule/init.go` thêm:
   ```go
   c.AddFunc("0 0 0 * * *", scheduleService.RunStaffRemovalCron)
   // TTL cleanup preview changes
   c.AddFunc("0 0 1 * * *", scheduleService.RunPreviewChangesTTLCleanup) // daily 01:00
   ```
7. [10m] CREATE TTL cleanup function `RunPreviewChangesTTLCleanup` — delete `import_changes{phase:preview, createdAt < now-24h}`

### G.4 Register hook FR-009 (~1h)

1. [10m] EDIT `pkg/public/service/user.go` import `MatchEngine` (hoặc inject helper service)
2. [40m] Trong `CompleteProfile` after `body.EmployeeCode != ""` block:
   ```go
   if body.EmployeeCode != "" {
       phone, _ := util.NormalizePhone(body.Phone)
       result, err := matchEngine.LookupSingle(ctx, body.EmployeeCode, phone)
       if err == nil && result.Registry != nil {
           if result.Match {
               // Kịch bản A
               set["staffStatus"] = constants.StaffStatusVerified
               set["staffVerifiedAt"] = now
               set["accountType"] = constants.AccountTypeStaff
               set["workplaceBrandCode"] = result.Registry.WorkplaceBrandCode
               // ... other workplace fields
               // Link registry
               registryDAO.UpdateById(ctx, registry, result.Registry.ID,
                   bson.M{"$set": bson.M{"genGreenUserId": userID}})
               // Push notification
               internalservice.Notification().Push(ctx, []*modelmg.NotificationRaw{{
                   UserID: userID,
                   Type: constants.NotificationTypeAutoVerified,
                   Title: "Tài khoản đã được xác minh",
                   Content: "Mã nhân viên đã khớp dữ liệu HR. Bạn có thể bắt đầu tham gia chương trình.",
               }})
           } else {
               // Kịch bản B: mismatch
               return errors.New("REGISTRY_MISMATCH: " + result.MismatchReason)
           }
       } else {
           // Kịch bản C: registry không có
           set["staffStatus"] = constants.StaffStatusPending
       }
   }
   ```
3. [10m] Update handler `CompleteProfile` map error code `REGISTRY_MISMATCH` → 400 với message Việt

### G.5 Notification wire-up (~1h)

1. [10m] EDIT `internal/constants/notification.go` thêm 5 const:
   ```go
   NotificationTypeAutoVerified = "auto_verified"
   NotificationTypeCancelledMismatch = "cancelled_mismatch"
   NotificationTypeWorkplaceUpdated = "workplace_updated"
   NotificationTypeStaffRemovedScheduled = "staff_removed_scheduled"
   NotificationTypeStaffRemoved = "staff_removed"
   ```
2. [40m] EDIT `pkg/admin/service/employee_registry_apply.go` per-action notification:
   ```go
   notifications := []*modelmg.NotificationRaw{}
   switch change.Action {
   case "auto_verified":
       notifications = append(notifications, &modelmg.NotificationRaw{
           UserID: *change.UserID,
           Type: constants.NotificationTypeAutoVerified,
           Title: "Tài khoản đã được xác minh",
           Content: "Thông tin nhân viên khớp dữ liệu HR.",
       })
   case "cancelled_mismatch":
       // ...
   case "transferred":
       // type WorkplaceUpdated, content "Đơn vị làm việc đã được cập nhật"
   case "missing_from_file" /* applied as staff_removed_scheduled */:
       // type StaffRemovedScheduled, content "Tài khoản sẽ chuyển Creator sau 7 ngày"
   }
   // Defer notification flush sau loop để batch:
   internalservice.Notification().Push(ctx, notifications)
   ```
3. [10m] Test push notification flow (smoke) — verify `notifications` collection có record với type đúng

## Todo List

- [ ] G.2.1 EDIT `GenerateDryRun` scan missing_from_file
- [ ] G.2.2 EDIT `ApplyImport` case `missing_from_file` với confirm flag
- [ ] G.2.3 UI footer checkbox "Xác nhận terminate N"
- [ ] G.2.4 Pass `confirmTerminate` qua API body
- [ ] G.3.1 Field `StaffRemovalScheduledAt` trong UserRaw
- [ ] G.3.2 Const `StaffStatusPendingRemoval`
- [ ] G.3.3 Method `ScheduleStaffRemoval`
- [ ] G.3.4 Method `RemoveStaffTag`
- [ ] G.3.5 Cron function `RunStaffRemovalCron`
- [ ] G.3.6 Cron function `RunPreviewChangesTTLCleanup`
- [ ] G.3.7 AddFunc daily 00:00 + 01:00 vào `schedule/init.go`
- [ ] G.4.1 EDIT `CompleteProfile` integration `LookupSingle`
- [ ] G.4.2 Kịch bản A auto-verify + notify
- [ ] G.4.3 Kịch bản B inline error 400 REGISTRY_MISMATCH
- [ ] G.4.4 Kịch bản C pending (default)
- [ ] G.4.5 Smoke test register flow 3 kịch bản
- [ ] G.5.1 5 notification constants
- [ ] G.5.2 Per-action notification trong ApplyImport
- [ ] G.5.3 Batch push notification (defer sau loop)

## Success Criteria

- [ ] `GenerateDryRun` detect missing_from_file đúng (counter > 0 nếu HR file thiếu nhân viên đang active)
- [ ] Admin tick checkbox terminate → Apply set `staffRemovalScheduledAt = now+7d`, status=pending_removal
- [ ] Cron daily 00:00 VN run: scan + remove staff tag, notify `staff_removed`
- [ ] Cron daily 01:00 VN run: cleanup `import_changes{phase:preview} > 24h`
- [ ] Register `POST /complete-profile` với valid employeeCode + phone → 200 + status verified + notify
- [ ] Register với mismatch phone → 400 `REGISTRY_MISMATCH` không save user
- [ ] Register với chưa có registry → 200 + status pending (no notify)
- [ ] 5 notification types push thành công cho mỗi tương ứng action

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Missing_from_file false positive (HR delta file) | HIGH | Document required: HR full-dump. Admin có thể skip checkbox. PRD note. |
| Cron timing mismatch (admin click 23:55 → 6d 5min grace) | LOW | Acceptable, daily granularity. Document. |
| Cron fail silently (no retry) | MED | Log error + Slack alert (defer). robfig cron không auto-retry. |
| LookupSingle race condition register hook | LOW | Single-row query, no concurrent write trên cùng employeeCode trong CompleteProfile. |
| Notification 1000 records spam | MED | Batch `Push(ctx, []NotificationRaw)` — `notification` service hỗ trợ. Throttle ở Firebase level. |
| `RemoveStaffTag` không reset audit history | LOW | Audit immutable, không touch. New audit entry "staff_removed" có ActorType=root. |
| Cron run lúc DB migration | MED | `schedule.Init()` chạy chung main process — startup delay nếu DB chưa ready. Fallback retry. |
| `StaffRemovalScheduledAt` nilable check | MED | Use pointer `*time.Time`, omitempty bson. Test query với `$ne: nil` syntax. |

## Security Considerations

- **Cron actor `root_account`:** Audit entries có `actorType=root_account` rõ ràng — tránh nhầm với admin manual action.
- **Register hook validation:** Phone phải `NormalizePhone` trước `LookupSingle`. Tránh injection.
- **REGISTRY_MISMATCH error message:** Không leak thông tin nội bộ (e.g. "Phone trong registry là 0907..."). Generic message: "Thông tin không khớp dữ liệu HR".
- **Notification deeplink:** Sanitize `userID` trong deeplink URL.
- **TTL cleanup race:** Nếu cron chạy lúc admin đang preview → không sao, query filter `createdAt < now-24h` chỉ xóa preview cũ.
- **Cron concurrent run:** robfig cron đảm bảo single-instance per cron entry trong process. Multi-pod → cần redsync mutex `cron:staff_removal` (defer nếu mới 1 pod).

## Next Steps

→ Phase H [phase-H-async-large-import.md](phase-H-async-large-import.md): unblock file >1000 rows qua goroutine + redsync + UI progress polling.
