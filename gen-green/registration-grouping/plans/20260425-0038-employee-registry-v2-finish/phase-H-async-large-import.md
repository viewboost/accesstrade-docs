# Phase H — Async >1000 Rows (PHASE CUỐI)

## Context Links

- **Plan root:** [plan.md](plan.md)
- **Depends:** ALL Phase F (apply flow phải ổn định trước khi async hóa)
- **PRD:** FR-005 (async processing >1000 rows)
- **Research:** [scout/scout-01-gaps.md](scout/scout-01-gaps.md) §Q1 redsync mutex

## Overview

- **Date:** 2026-04-25
- **Description:** Unblock file >1000 rows. Trước đó (đợt 1) reject với `FILE_TOO_LARGE`. Phase H: spawn goroutine + redsync mutex 30m + batch processing 100 rows/batch + status polling endpoint cho UI progress bar.
- **Priority:** Should Have (đẩy cuối, sau F/G ổn định)
- **Implementation Status:** Not Started
- **Review Status:** Pending

## Key Insights

- **Goroutine + mutex** không phải full job queue: vcreator chưa có Asynq worker (TCB có, ko shared). Goroutine in-process đủ cho HR file 1k-10k rows. Defer sang Asynq nếu >10k.
- **Redsync mutex 30m TTL:** Đủ time process 10k rows (~5 min nếu batch 100 = 100 query/batch * 100 batches). Cross-pod safe.
- **Batch 100 rows/batch:** 1k rows = 10 batches, 10k = 100 batches. Update `processedRows += 100` mỗi batch để UI hiển thị progress.
- **Status polling 3s:** UI poll `GET /imports/:importId/status` mỗi 3s. Lightweight read, không cần WebSocket.
- **Sequential, không parallel:** Phase H phụ thuộc F apply flow + G missing detection. Phải xong cả F+G mới async hóa.

## Requirements

### FR-005 Async >1000

- Detect `parseRes.TotalRows > 1000` trong `CreateImport`:
  - KHÔNG return `ErrFileTooLarge`
  - Save `ImportHistoryRaw{status:processing, processedRows:0, totalRecords}`
  - Spawn goroutine `go processImportAsync(importID)`
  - Return ngay `{importId, status:"processing", totalRecords}`
- Goroutine:
  - `mu := redis.NewMutexWithExpiration("import:" + importID, 30*time.Minute)`
  - `mu.Lock()` (skip nếu đã có), defer `mu.Unlock()`
  - Loop batch 100 rows:
    - `MatchEngine.GenerateChanges(batch)` → `ImportChangeRaw[]`
    - `InsertMany(changes)`
    - Update `ImportHistoryRaw.processedRows += len(batch)`
  - Final: `status = "preview"` (admin có thể vào preview page apply)
- Status endpoint `GET /imports/:importId/status` → `{status, processedRows, totalRecords, percent}`
- Admin UI poll mỗi 3s → progress bar, redirect đến preview khi `status=preview`

## Architecture

```
POST /imports (file > 1000 rows)
        │
        ▼
CreateImport
   ├── Save ImportHistoryRaw{status:processing, processedRows:0}
   ├── go processImportAsync(importID)  ←── goroutine spawned
   └── Return {importId, status:"processing"}

processImportAsync goroutine:
  ┌─────────────────────────────────────┐
  │ 1. Acquire redsync mutex 30m        │
  │ 2. Re-parse file from MinIO         │
  │ 3. Loop batch 100 rows:             │
  │    - MatchEngine.GenerateChanges    │
  │    - InsertMany ImportChangeRaw     │
  │    - history.processedRows += 100   │
  │ 4. (G.2 missing scan)               │
  │ 5. Set status = "preview"           │
  │ 6. Release mutex                    │
  └─────────────────────────────────────┘

UI poll (every 3s):
GET /imports/:importId/status
  → { status, processedRows, totalRecords, percent }
  When status=preview → redirect /preview/:importId
```

## Related Code Files

| Action | File | Role |
|--------|------|------|
| EDIT | `backend/pkg/admin/service/employee_registry.go` | `CreateImport` async path; `processImportAsync` goroutine |
| EDIT | `backend/internal/model/mg/import_history.go` | Field `ProcessedRows int` |
| EDIT | `backend/pkg/admin/handler/employee_registry.go` | Handler `GetImportStatus` |
| EDIT | `backend/pkg/admin/router/employee_registry.go` | Route `GET /imports/:importId/status` |
| EDIT | `admin/src/pages/employee-registry/components/upload-modal.tsx` | Progress bar + polling |
| EDIT | `admin/src/pages/employee-registry/services.ts` | `getImportStatus` API |
| REF | `backend/internal/module/redis/mutex.go` | `NewMutexWithExpiration` |
| REF | Phase D `MatchEngine.GenerateChanges` | Per-batch invocation |

## Implementation Steps

### H.1 Async goroutine + mutex (~1.5h)

1. [10m] Đọc `internal/module/redis/mutex.go` API + `pkg/admin/service/employee_registry.go` đợt 1 `CreateImport` flow
2. [60m] EDIT `CreateImport`:
   ```go
   func (e *employeeRegistryImpl) CreateImport(ctx, file, uploaderID) (*ImportCreateResult, error) {
       // ... validate, parse header, upload MinIO, save history
       parseRes, err := e.parser.Parse(file)
       if err != nil { return nil, err }

       history := &modelmg.ImportHistoryRaw{
           ImportID: uuid.New().String(),
           // ...
           Status: "processing",
           ProcessedRows: 0,
           TotalRecords: parseRes.TotalRows,
       }
       historyDAO.InsertOne(ctx, history)

       if parseRes.TotalRows > 1000 {
           go e.processImportAsync(history.ImportID, parseRes.Rows)
           return &ImportCreateResult{ImportID: history.ImportID, Status: "processing", TotalRecords: parseRes.TotalRows}, nil
       }
       // Sync path (đợt 2 GenerateDryRun)
       counters, err := e.GenerateDryRun(ctx, history.ImportID, parseRes.Rows)
       // ...
   }

   func (e *employeeRegistryImpl) processImportAsync(importID string, rows []parser.ParseRow) {
       ctx := context.Background()
       mu := redis.NewMutexWithExpiration("import:"+importID, 30*time.Minute)
       if err := mu.Lock(); err != nil {
           if errors.Is(err, redsync.ErrFailed) {
               log.Warnf("import %s already processing", importID)
               return
           }
           log.Errorf("redsync lock fail: %v", err)
           return
       }
       defer mu.Unlock()

       batchSize := 100
       for i := 0; i < len(rows); i += batchSize {
           end := i + batchSize
           if end > len(rows) { end = len(rows) }
           batch := rows[i:end]

           result, err := matchEngine.GenerateChanges(ctx, batch, importID)
           if err != nil {
               log.Errorf("batch fail: %v", err)
               historyDAO.UpdateById(ctx, history, importID, bson.M{"$set": bson.M{"status": "failed"}})
               return
           }
           // Insert changes
           for _, c := range result.Changes {
               c.Phase = "preview"
               c.Priority = ActionPriority[c.Action]
           }
           changeDAO.InsertMany(ctx, result.Changes)
           // Update progress
           historyDAO.UpdateById(ctx, history, importID, bson.M{"$inc": bson.M{"processedRows": len(batch)}})
       }
       // Phase G.2 missing scan
       e.scanMissingFromFile(ctx, importID)
       // Done
       historyDAO.UpdateById(ctx, history, importID, bson.M{"$set": bson.M{"status": "preview"}})
   }
   ```
3. [20m] Handle redsync.ErrFailed (mutex đã bị giữ): return early, log warn

### H.2 Status polling endpoint (~30m)

1. [10m] Handler `GetImportStatus(c echo.Context)`:
   ```go
   func GetImportStatus(c echo.Context) error {
       importID := c.Param("importId")
       history := new(modelmg.ImportHistoryRaw)
       err := historyDAO.FindOne(ctx, history, bson.M{"importId": importID})
       percent := 0
       if history.TotalRecords > 0 {
           percent = int(float64(history.ProcessedRows) / float64(history.TotalRecords) * 100)
       }
       return c.JSON(200, map[string]any{
           "status": history.Status,
           "processedRows": history.ProcessedRows,
           "totalRecords": history.TotalRecords,
           "percent": percent,
       })
   }
   ```
2. [10m] Route `GET /imports/:importId/status`
3. [10m] Smoke test với processing import

### H.3 Schema field ProcessedRows (~30m)

1. [5m] EDIT `internal/model/mg/import_history.go` thêm:
   ```go
   ProcessedRows int `bson:"processedRows"`
   ```
2. [25m] Backfill existing records: migration script set `processedRows = totalRecords` cho `status=preview/completed`. Defer nếu không cần (field có default 0).

### H.4 UI progress bar + polling (~30m)

1. [10m] EDIT `admin/src/pages/employee-registry/components/upload-modal.tsx`:
   ```tsx
   const [polling, setPolling] = useState(false);
   const [progress, setProgress] = useState(0);

   const onUploaded = (response) => {
     if (response.status === 'processing') {
       setPolling(true);
       const interval = setInterval(async () => {
         const res = await getImportStatus(response.importId);
         setProgress(res.percent);
         if (res.status === 'preview') {
           clearInterval(interval);
           history.push(`/employee-registry/preview/${response.importId}`);
         } else if (res.status === 'failed') {
           clearInterval(interval);
           message.error('Import thất bại');
         }
       }, 3000);
     } else {
       history.push(`/employee-registry/preview/${response.importId}`);
     }
   };

   {polling && <Progress percent={progress} status="active" />}
   ```
2. [10m] Add `getImportStatus` vào `services.ts`
3. [10m] Smoke test upload 2000-row file → progress bar tăng dần → redirect

## Todo List

- [ ] H.1.1 Detect `>1000 rows` trong `CreateImport`
- [ ] H.1.2 Save `ImportHistoryRaw{status:processing, processedRows:0}`
- [ ] H.1.3 Spawn goroutine `processImportAsync`
- [ ] H.1.4 Acquire redsync mutex 30m, handle ErrFailed
- [ ] H.1.5 Loop batch 100 rows + InsertMany changes
- [ ] H.1.6 Update `processedRows += len(batch)` mỗi batch
- [ ] H.1.7 Final set `status = preview`
- [ ] H.1.8 Error handling → set `status = failed`
- [ ] H.2.1 Handler `GetImportStatus`
- [ ] H.2.2 Route `GET /imports/:importId/status`
- [ ] H.3.1 Field `ProcessedRows` schema
- [ ] H.4.1 UI progress bar component
- [ ] H.4.2 Polling logic 3s interval
- [ ] H.4.3 Redirect `preview` khi done
- [ ] H.4.4 Service client `getImportStatus`

## Success Criteria

- [ ] Upload file 2000 rows → response 200 ngay (~500ms), không block 30s
- [ ] UI progress bar tăng dần từ 0% → 100%
- [ ] Status endpoint return chính xác `{status, processedRows, totalRecords, percent}`
- [ ] Concurrent upload cùng `importID` (rare) → second goroutine reject qua redsync
- [ ] Goroutine die do panic → recover middleware log + status=failed (defer)
- [ ] File 5000 rows process < 5 phút wall-time
- [ ] Mutex TTL 30m không bị stale lock

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Goroutine die do panic giữa chừng | HIGH | Wrap goroutine trong `defer recover()`. Set status=failed khi panic. Document. |
| Mutex stale lock 30m nếu pod crash | MED | TTL 30m auto-release. Subsequent retry khả dụng. Defer admin "force unlock" UI. |
| Memory leak parse rows giữ trong goroutine | MED | Stream parse từ MinIO thay vì load toàn file vào memory. Defer optimization, 10k rows ~ 5MB acceptable. |
| MongoDB connection pool exhaust với 100 concurrent batches | LOW | Sequential batches trong 1 goroutine. 1 connection / batch. |
| UI polling load nếu 100 admin upload cùng lúc | LOW | 3s polling × 100 = 33 req/s lightweight read. Acceptable. |
| Multi-pod goroutine race | MED | redsync mutex cross-pod. Test verify 2 pod 1 importID không race. |
| Async file process xong nhưng admin browser closed | LOW | History page show `status=preview` admin có thể quay lại apply sau. |
| Progress bar stuck ở 99% (last batch fail) | MED | Status=failed visible. Retry path defer (admin click "Retry processing"). |

## Security Considerations

- **Goroutine context:** `context.Background()` không cancel khi request kết thúc — đúng intentional cho async. Tránh leak resource: defer mu.Unlock + recover.
- **Status endpoint authorization:** Admin role check existing middleware. Không expose status cho user.
- **MinIO file re-read trong goroutine:** Re-parse cần credentials backend. Không expose presigned URL.
- **Redsync key collision:** Prefix `import:` đủ unique. Không collide với `withdraw:` hoặc khác.
- **DoS upload spam:** Phase H không thêm rate limit. Defer admin upload throttle nếu issue.
- **Audit not generated trong goroutine:** Match phase chỉ generate `ImportChangeRaw` preview. Audit ghi ở Apply (Phase F.2) khi thực sự touch user.

## Next Steps

Đợt 2+3 hoàn thành. V2 Employee Registry & Import production-ready. Future:
- Phase I (defer): retry processing UI cho async failed
- Phase J (defer): smart rollback check `user.updatedAt > applied.timestamp` để skip overwrite user-modified
- Phase K (defer): Asynq worker thay goroutine khi cần distributed retry
- Phase L (defer): Slack alert cho cron failure + import failure
