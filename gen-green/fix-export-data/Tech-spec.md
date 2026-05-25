# Tech Spec — Export Queue Stability Fix

**Liên quan PRD:** [export-queue-fix.md](./export-queue-fix.md)
**Ngày:** 2026-05-25
**Author:** Thanh Trung
**Status:** Implemented

---

## 1. Bối cảnh kỹ thuật

### 1.1. Kiến trúc hiện tại

Module: `backend/pkg/admin/service/export.go`
Persistence: MongoDB collection `data_export` (model `modelmg.DataExportRaw`)
Storage output: MinIO bucket `DataExport`
Trigger:
- **API:** `POST /admin/export` → `exportImpl.Export()`
- **Cron:** mỗi giờ → `scheduleImpl.RunExportData()` → `exportImpl.CheckRun()`

State machine của 1 đơn export:
```
Waiting ──pick──► Running ──success──► Completed
                     │
                     └──fail/panic──► Failed
```

Concurrency limit: 2 job `Running` đồng thời (hard-coded).

### 1.2. Các bug đã xác định

| ID | Root cause | Triệu chứng | Severity |
|----|-----------|-------------|----------|
| B1 | Không reset job `Running` khi server crash/restart | DB còn ≥2 record `Running` zombie → `CheckRun` bỏ qua vĩnh viễn | Critical |
| B2 | `RunExport` không gọi `CheckRun` sau khi xong | Đơn `Waiting` đợi cron 1h hoặc request mới | High |
| B3 | `defer f.Close()` đặt trước check `err` của `os.Create` | `f == nil` khi err ≠ nil → nil-pointer panic trong goroutine | High |
| B4 | Goroutine `RunExport` không có `recover()` | Panic làm chết goroutine, defer update status không chạy → job kẹt `Running` | Critical |
| B5 | Không có timeout cho job `Running` | Job treo (minio hang, query slow) → kẹt vô hạn | Medium |
| B6 | Không có lock giữa các caller `CheckRun` | Race: pick trùng job, vượt concurrency limit | Medium |

---

## 2. Thiết kế giải pháp

### 2.1. Tổng quan luồng mới

```
┌─────────────────────────┐
│  Server bootstrap       │
│  ResetOrphanedRunning() │  ── reset Running → Waiting, trigger CheckRun
└─────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────┐
│  CheckRun()                                      │
│  1. Redis lock TryLock (NoRetry, 35min)          │
│  2. defer recover() panic                        │
│  3. ResetStaleRunning() — timeout > 30min → Failed
│  4. Count Running ≥ 2 → return                   │
│  5. Pick Waiting đầu tiên (sort by _id ASC)      │
│  6. RunExport(doc)                               │
└──────────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────┐
│  RunExport(doc)                                  │
│  1. UpdateOne: Waiting → Running                 │
│  2. defer:                                       │
│     - recover() panic → errDesc = "panic: ..."   │
│     - Update doc status (Failed / Completed)     │
│     - go CheckRun() — trigger pick job kế tiếp  │
│  3. os.Create(path) — check err TRƯỚC defer Close│
│  4. Switch type → call Export<Type>()            │
│  5. minio.PutObject + append files               │
│  6. status = Completed                           │
└──────────────────────────────────────────────────┘
```

### 2.2. Chi tiết các thay đổi

#### F1. `ResetOrphanedRunning(ctx)` — chạy lúc bootstrap

```go
func ResetOrphanedRunning(ctx context.Context) {
    daomongodb.DataExportDAO().GetShare().UpdateMany(ctx, ...,
        bson.M{"status": constants.StatusRunning},
        bson.M{"$set": bson.M{
            "status": constants.StatusWaiting,
            "reason": "server restarted - requeued",
            "updatedAt": time.Now(),
        }})
    // Trigger CheckRun với staff isGenerate=true (giống cron RunExportData)
    go Export(staffInfo).CheckRun()
}
```

**Lý do reset về `Waiting` (không phải `Failed`):**
- Server vừa restart → mọi goroutine `RunExport` đã chết → 100% là zombie.
- Đơn chưa thực sự bị lỗi nghiệp vụ → requeue an toàn, UX tốt hơn (không bắt user tạo lại).

**Gọi tại:** `backend/pkg/admin/server/bootstrap.go::Bootstrap()` sau `initialize.Init()`.

#### F2. `ResetStaleRunning(ctx)` — chạy trong `CheckRun`

```go
const exportJobTimeout = 30 * time.Minute

func ResetStaleRunning(ctx context.Context) {
    daomongodb.DataExportDAO().GetShare().UpdateMany(ctx, ...,
        bson.M{
            "status":    constants.StatusRunning,
            "updatedAt": bson.M{"$lt": time.Now().Add(-exportJobTimeout)},
        },
        bson.M{"$set": bson.M{
            "status": constants.StatusFailed,
            "reason": "job timeout - reset stale running",
            "updatedAt": time.Now(),
        }})
}
```

**Lý do reset về `Failed` (không `Waiting`):**
- Server đang sống → job có thể đang chạy thật, chỉ là chậm (network/DB).
- Mark `Failed` để user biết và quyết định retry thủ công, tránh loop vô hạn nếu nguyên nhân là bug cố hữu.

#### F3. Redis distributed lock cho `CheckRun`

Helper mới tại `backend/internal/module/redis/mutex.go`:
```go
func NewMutexNoRetry(name string, d time.Duration) *redsync.Mutex {
    rs := redsync.New(goredis.NewPool(store))
    return rs.NewMutex(name,
        redsync.WithTries(1),       // không retry, fail thì trả lỗi ngay
        redsync.WithExpiry(d))
}
```

Usage trong `CheckRun`:
```go
const (
    checkRunLockKey        = "export:check_run_lock"
    checkRunLockExpiration = 35 * time.Minute  // > exportJobTimeout
)

mu := redisclient.NewMutexNoRetry(checkRunLockKey, checkRunLockExpiration)
if err := mu.Lock(); err != nil {
    return  // đã có instance khác chạy, skip
}
defer func() { _, _ = mu.Unlock() }()
```

**Lý do `WithTries(1)`:** Pattern dùng helper mặc định (`NewMutex`) sẽ retry 10 lần × 100ms — không phù hợp "skip nếu đang chạy" mà sẽ block 1s rồi mới fail.

**Lý do expiration 35 phút:**
- Phải > `exportJobTimeout` (30 phút) để lock không tự release giữa lúc job đang chạy hợp lệ.
- Trade-off: nếu process crash, lock kẹt tối đa 35 phút trước khi cluster tự khôi phục. Chấp nhận được vì cũng có `ResetOrphanedRunning` chạy lúc bootstrap.

**Multi-instance safe:** Redis lock survive cross-process, đảm bảo đúng concurrency limit kể cả khi scale horizontal.

#### F4. Recover + chain trigger trong `RunExport`

```go
defer func() {
    if r := recover(); r != nil {
        errDesc = fmt.Sprintf("panic: %v", r)
        log.Printf("[Export] RunExport panic recovered: %v\n", r)
    }
    // Update doc status (status default = Failed, override = Completed nếu OK)
    daomongodb...UpdateOne(...)
    // Chain trigger để pick job kế tiếp
    go e.CheckRun()
}()
```

**Đặc điểm:**
- `status` default = `Failed` ngay từ đầu, chỉ override = `Completed` khi pipeline OK đến cuối → panic ở bất kỳ đâu vẫn ghi nhận đúng.
- `errDesc` được set bởi recover hoặc bởi từng nhánh error.
- `go e.CheckRun()` đặt trong defer → chạy **sau khi update DB xong**, đảm bảo CheckRun mới thấy job vừa xong đã thoát `Running`.

#### F5. Fix `defer f.Close()` nil panic

```go
// Trước:
f, err := os.Create(path)
defer f.Close()        // PANIC nếu err != nil → f == nil
if err != nil { ... }

// Sau:
f, err := os.Create(path)
if err != nil { errDesc = err.Error(); return }
defer f.Close()
```

#### F6. Recover trong `CheckRun`

```go
defer func() {
    if r := recover(); r != nil {
        log.Printf("[Export] CheckRun panic recovered: %v\n", r)
    }
}()
```

**Scope:** chỉ catch panic ở bước query DB / acquire lock. Panic trong `RunExport` đã có recover riêng (F4) nên không bubble lên — không cần update status ở đây.

---

## 3. Files thay đổi

| File | Thay đổi |
|------|---------|
| [backend/pkg/admin/service/export.go](../../backend/pkg/admin/service/export.go) | Thêm `ResetOrphanedRunning`, `ResetStaleRunning`, Redis lock, recover, chain trigger, fix `defer f.Close()` order |
| [backend/pkg/admin/server/bootstrap.go](../../backend/pkg/admin/server/bootstrap.go) | Gọi `service.ResetOrphanedRunning(ctx)` sau `initialize.Init()` |
| [backend/internal/module/redis/mutex.go](../../backend/internal/module/redis/mutex.go) | Thêm helper `NewMutexNoRetry(name, d)` |

---

## 4. Test plan

### 4.1. Manual / staging

| Scenario | Cách reproduce | Expected |
|----------|---------------|----------|
| Server restart giữa lúc export đang chạy | Tạo export, kill backend process khi status=Running | Sau restart, đơn về Waiting và được pick lại tự động trong vài giây |
| Job treo > 30 phút | Mock minio.PutObject sleep 35 phút | Sau ~30 phút, job tự chuyển Failed với reason "job timeout" |
| Panic trong export function | Inject panic vào `ExportContent` | Job chuyển Failed với reason "panic: ..." (không kẹt Running) |
| Nhiều caller CheckRun đồng thời | Spawn 10 goroutine cùng gọi `CheckRun()` | Chỉ 1 acquire được lock, 9 còn lại return ngay; không có job nào bị pick trùng |
| Chain trigger | Tạo 5 đơn export liên tiếp | Cả 5 chạy lần lượt không cần đợi cron 1h |
| Multi-instance | Chạy 2 pod admin song song, mỗi pod gọi CheckRun | Đúng max 2 job Running tổng cộng (không phải 2 per pod) |

### 4.2. Verify trên DB sau deploy

```js
// Không còn job Running quá hạn:
db.data_export.find({status: "running", updatedAt: {$lt: new Date(Date.now() - 30*60*1000)}})
// → []

// Đơn vừa requeue sau restart:
db.data_export.find({reason: "server restarted - requeued"}).sort({updatedAt: -1}).limit(5)
```

---

## 5. Rollout

- **Risk:** Low — thay đổi backward-compatible, không thay schema/API.
- **Migration:** Không cần. Job Running zombie hiện hữu sẽ tự được reset sau lần restart đầu tiên với code mới.
- **Rollback:** Revert commit là đủ. Job đang chạy không bị ảnh hưởng vì chỉ thay đổi cơ chế recovery, không đổi logic export.

---

## 6. Dependencies

- Redis (đã có sẵn) — bắt buộc để `CheckRun` chạy.
  - **Failure mode:** Redis down → `mu.Lock()` fail → CheckRun skip → queue tạm dừng cho đến khi Redis sống lại. Không corrupt data.
- MongoDB (đã có sẵn) — không thay đổi schema.

---

## 7. Open questions / Future work

- **Q1:** `exportJobTimeout = 30 min` có hợp lý cho mọi loại export? Cần measure thực tế các loại nặng (Content, EventChart) để tune.
- **Q2:** Cron `RunExportData` hiện 1h/lần — có nên giảm xuống 5 phút không? (Vì giờ đã có chain trigger, vai trò cron chỉ là failsafe.)
- **Future:** Migrate sang [Asynq](https://github.com/hibiken/asynq) hoặc [River](https://github.com/riverqueue/river) cho job queue chuyên dụng — có sẵn retry policy, dashboard, scheduling, dead-letter queue.
