# Scout 01 — Codebase Gaps Fill (Đợt 2+3)

**Date:** 2026-04-25 | **Project:** `accesstrade-projects/vcreator/backend/`

---

## Q1. Redis Mutex Pattern — ✅ CÓ SẴN

**File:** `backend/internal/module/redis/mutex.go`

**Library:** `github.com/go-redsync/redsync/v4` (distributed lock cross-pod safe)

**Functions:**
- `NewMutex(name string) *redsync.Mutex` — default 10 tries, 100ms retry
- `NewMutexWithExpiration(name, duration time.Duration) *redsync.Mutex` — custom TTL
- Methods (từ redsync): `Lock()`, `Unlock()`

**Usage example:** `backend/internal/service/withdraw.go:67-78`

```go
mu := redis.NewMutex("withdraw:" + userID.Hex())
if err := mu.Lock(); err != nil {
    if errors.Is(err, redsync.ErrFailed) {
        return errors.New("withdraw đang xử lý")
    }
    return err
}
defer mu.Unlock()
// ... critical section
```

**Áp dụng cho FR-005 (Phase H):** Lock theo `importId` để tránh 2 admin upload cùng file. TTL 30m (đủ time process file 10k rows).

---

## Q2. UpdateWorkplace API V1 — ❌ KHÔNG CÓ, CẦN BUILD

**Status:** Method `UpdateWorkplace(userID, workplace, actor)` **chưa tồn tại** trong `pkg/admin/service/user.go`.

**Fields exist trong `modelmg.UserRaw`:**
- `WorkplaceBrandCode` (indexed)
- `WorkplaceCompanyCode`
- `WorkplaceUnitCode`
- `WorkplaceName`

**Routes hiện có:** `/workplaces` trong `pkg/public/router/workplace.go` (list workplace cho user chọn). **KHÔNG có** PUT `/users/:id/workplace`.

**Implication cho Phase F.2 (Apply):**
- Phải build method mới `UpdateWorkplace(ctx, userID, workplaceFields, actor *StaffInfo) error` (~30 phút)
- File touch: `pkg/admin/service/user.go` (thêm method) + audit ghi `actorType`
- Pattern theo `VerifyStaff` đã refactor (accept actor param, fallback `Staff().GetRoot()` nếu nil)

---

## Q3. Cron / Scheduled Jobs — ✅ CÓ SẴN

**Library:** `github.com/robfig/cron/v3` v3.0.1 (go.mod)

**Init pattern:**
```go
c := cron.New(cron.WithLocation(loc), cron.WithSeconds())
c.AddFunc("0 0 0 * * *", func() { ... }) // 6-field, seconds-aware
c.Start()
```

**Entry points (3):**
- `backend/pkg/admin/schedule/init.go` — main cron, ~7 scheduled jobs (RemoveHistoryCrawl, RecheckEventAnalyticDaily, AutoRejectedContent, ...)
- `backend/pkg/file/schedule/schedule.go`
- `backend/pkg/public/schedule/schedule.go`

**KHÔNG có** `cmd/cron/main.go` riêng — schedule chạy chung main API process.

**Áp dụng cho FR-013 (Phase G.3) Grace Period:**
- Thêm AddFunc daily `"0 0 0 * * *"` (mỗi ngày 0h) trong `pkg/admin/schedule/init.go`
- Function: scan `UserRaw WHERE staffRemovalScheduledAt < now() AND staffStatus = pending_removal` → gỡ staff tag
- File touch: EDIT `pkg/admin/schedule/init.go` (~+10 lines) + CREATE `pkg/admin/service/staff_removal_cron.go` impl

**Áp dụng cho TTL cleanup `import_changes{phase:preview}` (đợt 2):**
- Thêm AddFunc daily scan `import_changes WHERE phase=preview AND createdAt < now()-24h` → drop
- 5-minute job để tránh giữ orphan preview

---

## Q4. Test Scaffolding — ⚠️ PARTIAL

**Current pattern:** `pkg/admin/service/employee_registry_parser_test.go` (đợt 1)
- File-based tests: tạo file xlsx tạm với `excelize.NewFile()`
- KHÔNG có MongoDB mocking (`mtest`, `mongo-mock`, `*Mock`)
- DAO global access: `daomongodb.UserDAO().GetShare()` (no DI)

**Implication cho Phase D match logic test:**
- Match engine cần test với fixture registry data + user data + verify call V1 API
- Options:
  1. **Real MongoDB testcontainers** (~30m setup): `testcontainers-go` spin up mongo container per test run. Slow first run (~5s pull image), fast subsequent. Pros: real behavior, cons: dep cài.
  2. **Refactor DAO injection** (~1h refactor): EmployeeRegistryService accept DAO interface qua factory → mockable. Pros: fast tests, cons: scope creep, đụng đợt 1 code.
  3. **Integration test với existing dev MongoDB** (~5m): test trỏ thẳng `MONGO_URI=localhost:27017/test_db`, mỗi test setup/teardown collection. Pros: simple, cons: không isolated, conflict CI.

**Recommend:** Option 3 cho đợt 2 (đơn giản, không scope creep). Document `make test-integration` cần MongoDB local. Nếu CI fail thì chuyển option 1 sau.

---

## Summary Table

| Question | Status | Effort thêm | Notes |
|----------|--------|-------------|-------|
| Q1. Redis Mutex | ✅ Có sẵn | 0 | redsync/v4, distributed-safe, dùng trực tiếp |
| Q2. UpdateWorkplace | ❌ Cần build | ~30m | Method + audit, follow VerifyStaff pattern |
| Q3. Cron Schedule | ✅ Có sẵn | 0 | robfig/cron/v3 + 3 schedule entries |
| Q4. Test Scaffolding | ⚠️ Partial | ~5m setup | Recommend integration test với local Mongo, defer testcontainers |

---

## Unresolved

1. **MongoDB transaction support** — Apply flow (Phase F.2) có nên wrap trong transaction để rollback khi 1 user fail? vcreator có replicaset chưa? Nếu chưa → per-record commit + audit, manual rollback qua `import_changes.phase=applied` reverse.
2. **Test data isolation** — Nếu chọn option 3 (integration với Mongo dev), 2 dev chạy test cùng lúc sẽ conflict. Recommend prefix collection theo PID hoặc skip CI.
