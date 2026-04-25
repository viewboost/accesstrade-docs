# Gen-Green Employee Registry & Import — Đợt 2+3 (Finish V2)

**Date:** 2026-04-25 | **Branch:** `hotfix/group-users` | **Project:** `accesstrade-projects/vcreator/`
**PRD:** [prd-registration-v2-2026-04-12.md](../../prd-registration-v2-2026-04-12.md) v2.2
**Đợt 1 ref:** [20260424-2255-employee-registry-import-dot1/plan.md](../20260424-2255-employee-registry-import-dot1/plan.md) ✅ committed
**Scope:** FR-004 (dry-run UI), FR-006 (rollback), FR-008/009/010 (match A/B/C), FR-011/012/013 (lifecycle), FR-014 (notify), FR-005 (async >1000 — phase H cuối)

---

## 1. Overview

Hoàn thiện V2 Employee Registry & Import: từ "đợt 1 đã upload + parse + validate" → tới "đầy đủ match logic, dry-run preview, apply/rollback, lifecycle terminate + grace period, notification, async >1000". Gộp đợt 2 + đợt 3 thành 1 plan lớn 5 phases. Phase H (async) tách cuối cùng, chạy sau khi F/G ổn định.

---

## 2. Phases

### Phase D — Match Logic Core (~5h)

**File:** [phase-D-match-logic.md](phase-D-match-logic.md) | **Progress:** [░░░░░░░░░] 0%
**Depends:** Đợt 1 (models + parser)

- D.1 [1h] CREATE `pkg/util/workplace.go` `DeriveWorkplaceGroup` 3-tier query
- D.2 [3h] CREATE `pkg/admin/service/employee_registry_match.go` `MatchEngine.GenerateChanges` (bulk 2-query + hash maps + 3 kịch bản A/B/C)
- D.3 [1h] CREATE `_test.go` integration test với local Mongo

### Phase E — Dry-run Backend + Preview API (~4h)

**File:** [phase-E-dryrun-preview-api.md](phase-E-dryrun-preview-api.md) | **Progress:** [░░░░░░░░░] 0%
**Depends:** Phase D

- E.1 [2h] `GenerateDryRun(importID)` — gọi MatchEngine, save `ImportChangeRaw{phase:preview}`
- E.2 [1.5h] Route `GET /imports/:importId/preview` + filter/sort/pagination
- E.3 [0.5h] Wire dry-run vào `CreateImport` (auto-call sau parse)

### Phase F — Dry-run UI + Apply + Rollback (~6h)

**File:** [phase-F-ui-apply-rollback.md](phase-F-ui-apply-rollback.md) | **Progress:** [░░░░░░░░░] 0%
**Depends:** Phase E. **Parallel:** F.1 (UI agent) || F.2/F.3 (backend agent)

- F.1 [3h] Admin UI `/employee-registry/preview/:importId` — counter cards + filter + table + footer actions
- F.2 [1.5h] `ApplyImport(importID, actor)` + handler + route. Build `UpdateWorkplace` mới
- F.3 [1h] `RollbackImport(importID, actor)` + handler + route
- F.4 [0.5h] Admin UI `/employee-registry/imports` history list

### Phase G — Lifecycle: Transferred + Missing + Grace + Notify + Register Hook (~5h)

**File:** [phase-G-lifecycle-notify.md](phase-G-lifecycle-notify.md) | **Progress:** [░░░░░░░░░] 0%
**Depends:** Phase F. **Parallel:** G.3 (cron agent) || G.4 (register agent) || G.1+G.2+G.5 (apply.go agent)

- G.1 [0.5h] FR-011 Transferred — confirm wire trong F.2 (re-verify, không task riêng)
- G.2 [1.5h] FR-012 Missing — scan `lastSeenImportId != currentImport`, UI checkbox confirm-2
- G.3 [1h] FR-013 Grace 7d cron — `staff_removal_cron.go` + AddFunc daily 00:00
- G.4 [1h] FR-009 Register hook — `MatchEngine.LookupSingle` từ CompleteProfile
- G.5 [1h] FR-014 Notify wire — 5 constants + `Notification().Push()` mỗi action

### Phase H — Async >1000 Rows (~3h) — PHASE CUỐI

**File:** [phase-H-async-large-import.md](phase-H-async-large-import.md) | **Progress:** [░░░░░░░░░] 0%
**Depends:** ALL F. **Sequential.**

- H.1 [1.5h] Detect >1000 → goroutine + `redsync` mutex + batch 100 rows
- H.2 [0.5h] Route `GET /imports/:importId/status` cho UI poll
- H.3 [0.5h] `ImportHistoryRaw.ProcessedRows` field
- H.4 [0.5h] UI progress bar + redirect khi done

---

## 3. Dependency Graph

```
Đợt 1 ✅ (models + parser + upload)
   ↓
Phase D (5h) match logic core ──┐
   ↓                             │
Phase E (4h) dry-run + preview ──┤
   ↓                             │
Phase F (6h) UI + apply + rollback ──┐
   ↓                                  │
Phase G (5h) lifecycle + notify + hook
   ↓
Phase H (3h) async ── CUỐI
```

---

## 4. Acceptance Criteria (đợt 2+3 toàn cục)

- [ ] Match engine generate 8 actions đúng theo PRD §EPIC-003: `auto_verified`, `cancelled_mismatch`, `transferred`, `missing_from_file`, `new_record`, `no_match`, `unchanged`, `invalid`
- [ ] Bulk match performance: 1000 rows < 2s (2 queries + in-memory)
- [ ] Preview API: filter action[], workplace, search, sort priority, pagination 50/page
- [ ] Apply: gọi V1 `VerifyStaff(actor=root)` cho auto_verified/cancelled_mismatch; `UpdateWorkplace` cho transferred
- [ ] Rollback: revert applied changes qua `oldValue`. Document warn risk overwrite user-modified profile
- [ ] Cron daily 00:00 VN: scan `staffRemovalScheduledAt < now AND staffStatus=pending_removal` → remove staff tag
- [ ] Cron daily TTL 24h: cleanup `import_changes{phase:preview, createdAt < now-24h}`
- [ ] Register hook: user submit profile với `employeeCode` → call `LookupSingle`, kịch bản A auto-verify, B inline error, C pending
- [ ] 5 notification types push ở apply: `auto_verified`, `cancelled_mismatch`, `workplace_updated`, `staff_removed_scheduled`, `staff_removed`
- [ ] Async >1000: goroutine + redsync mutex 30m, UI poll status, progress bar
- [ ] Concurrent apply 2 admin → idempotent qua status check (reject second)

---

## 5. Total Estimate

**~22h dev (~3-4 ngày).** Wall-time với parallel agents F + G: ~16h (~2 ngày).

---

## 6. Decisions (user-confirmed 2026-04-25)

1. **1 plan lớn** gộp đợt 2 + đợt 3 (5 phases D/E/F/G/H)
2. **Preview storage:** `import_changes{phase:preview}` persistent + cron daily TTL 24h cleanup
3. **Match perf:** Bulk 2 queries (`employeeCode IN [...]` + `phone IN [...]`) + in-memory hash maps
4. **Async (FR-005) cuối cùng:** Phase H scope tối giản, sau F/G

## 7. V1 API Reuse Constraint

- Match logic GỌI `VerifyStaff(...)` của V1 với `actor = StaffInfo{IsRoot:true}` (lookup qua `Staff().GetRoot()`)
- `UpdateWorkplace` build mới Phase F.2 (~30m), pattern theo `VerifyStaff` (accept actor, audit ghi actorType)
- Notification reuse `internalservice.Notification().Push()`

---

## 8. Critical Pitfalls (document trong từng phase)

1. **Rollback không hoàn hảo:** User có thể đã modify profile sau apply → rollback overwrite có thể destroy user changes. UI confirm dialog warn.
2. **Cron timing:** Daily 00:00 VN. Admin confirm terminate 23:55 → grace thực tế 6d 5min. Acceptable, không cần ms-precise.
3. **Concurrent apply:** 2 admin click cùng lúc → idempotent qua status check (`status != "preview"` reject second).
4. **Notification spam:** 1000 rows → 1000 notifications. Recommend rate-limit hoặc batch.
5. **Missing_from_file false positive:** HR delta file → tất cả existing flagged. Document required: HR phải full-dump, hoặc admin skip checkbox.
6. **Test isolation:** Integration test với local Mongo cùng DB dev → wipe data risk. Use prefix `test_employee_registry` hoặc env `TEST_DB_NAME`.

---

## 9. Unresolved Questions

- **MongoDB transaction support** Apply flow nên wrap transaction? vcreator có replicaset chưa? Nếu chưa → per-record commit + manual reverse qua `import_changes`
- **HR import frequency** monthly full-dump hay ad-hoc delta? Ảnh hưởng `missing_from_file` logic. Cần xác nhận với HR Vin
- **Cột J validation list** đối tác Excel — runtime đọc file hay master DB? Chốt khi làm dry-run
- **modelmg.NotificationRaw shape** required fields (title, content, deeplink) — xác định khi wire G.5
- **Test concurrency** 2 dev chạy test cùng lúc collide collection — defer test isolation strategy
