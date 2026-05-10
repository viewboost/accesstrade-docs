# Semantic Diff — Reconciliation & Audit Group

> **Generated**: 2026-05-07
> **Files trong scope**: `audit.go`, `reconciliation_checklist.go`, `reconciliation_snapshot.go`, `reconciliation_snapshot_job.go`

| Service | TCB | vCreator | Ambassador |
|---|---:|---:|---:|
| audit.go | 56 LOC | 80 LOC (+ActorType) | 56 LOC (=TCB md5) |
| reconciliation_checklist.go | **918 LOC** | ❌ | ❌ |
| reconciliation_snapshot.go | 361 LOC | ❌ | ❌ |
| reconciliation_snapshot_job.go | 107 LOC | ❌ | ❌ |

---

## TL;DR

1. **TCB là sản phẩm DUY NHẤT có reconciliation engine thật**. 3 service files (~1380 LOC) implement evaluation + classification + manual override + snapshot versioning.
2. **vCreator + Ambassador có 3 reconciliation models** (`reconciliation.go`, `reconciliation_item.go`, `reconciliation_history.go`) — **identical fields với TCB** — nhưng KHÔNG có service workflow. Chỉ có DAO + admin CRUD page.
3. **TCB có 3 model chuyên dụng riêng** (`reconciliation_checklist.go`, `reconciliation_event_config.go`, `reconciliation_snapshot.go`) cho engine evaluation.
4. **audit.go**: TCB + Ambassador identical (md5 match). vCreator thêm khái niệm `ActorType` (`human_admin` vs `root_account`) — dùng để phân biệt thao tác từ UI vs tự động hóa (webhook, batch import).

---

## 1. `service/audit.go` — Audit log service

### Existence
- TCB ↔ Ambassador: **md5 identical** (synced 100%, không cần phân tích).
- vCreator: divergent +24 LOC.

### Khác biệt vCreator vs TCB/Amb

vCreator thêm 2 ActorType constants:
```go
const (
    ActorTypeHumanAdmin   = "human_admin"   // staff thao tác qua UI
    ActorTypeRootAccount  = "root_account"  // system account: webhook, batch import
)
```

Và thêm field `ActorType` vào `PayloadAudit` struct + 1 hàm mới `CreatePayloadWithActorType`.

**Ý nghĩa nghiệp vụ**: vCreator có nhiều flow tự động (webhook, batch import → xem `module/pub_be`, `crosscheck`) cần audit nhưng không có staff thật → dùng "root_account" làm actor. TCB/Ambassador chưa cần phân biệt này.

→ Đây là **vCreator-led innovation** mà TCB/Ambassador chưa có. Có thể backport sang 2 sản phẩm còn lại nếu họ cũng muốn track actor type.

---

## 2. `service/reconciliation_checklist.go` — TCB-only (918 LOC)

Hàm public (13 fns):
- `EvaluateReconciliation(reconciliationID, overrideManual)` — chạy engine evaluate tất cả items pending trong 1 reconciliation
- `GetLatestResult(reconciliationItemID)` / `GetLatestResultMap(reconciliationID)` — query result mới nhất
- `ApplyClassification(reconciliationID, staffID, filter)` — apply auto-classification cho batch items
- `ManualEvaluateItem(itemID, code, status, staffID)` — manual override 1 item
- `QuickApprove(itemID, staffID)` / `QuickReject(itemID, staffID)` — shortcut buttons cho admin
- `Override(itemID, toStatus, reason, staffID)` — force change status với lý do
- `ConfirmStatus(itemID, targetStatus, reason, staffID)` — confirm staff decision
- `ResetChecklistItem(itemID, code)` — reset 1 checklist item về unverified
- `ComputeChecklistSummary(...)` — tính summary pass/fail counts
- `ValidateStatusFromChecklist(...)` — validate status transition

### Cấu trúc kết quả

```go
type EvaluateResult struct {
    TotalConditions, TotalConditionsPass, TotalConditionsFail, TotalConditionsSkipped int
    TotalAllItems, TotalSkippedItems, TotalItems int
    TotalAutoApproved, TotalAutoRejected, TotalNeedsReview int
}
```

→ Engine có **3 output bucket**: AutoApproved (qua tất cả check) / AutoRejected (fail critical check) / NeedsReview (manual). Đây là **classification 3 levels**, không phải binary approve/reject.

### Ý nghĩa nghiệp vụ

TCB tự động hóa quá trình đối chiếu (reconciliation) giữa data crawl (views, likes, comments) vs reward được trả cho creator. Workflow:

1. **Snapshot** ngày đó view/like count từ social platform (`reconciliation_snapshot.go`)
2. **Checklist evaluate**: mỗi item (1 content × 1 ngày) chạy qua nhiều condition (= rule), output pass/fail per condition.
3. **Classify**: nếu **tất cả** pass → auto-approve. Có critical fail → auto-reject. Còn lại → needs review.
4. **Admin manual**: Quick Approve/Reject hoặc Override với lý do.

→ Đây là **TCB-specific compliance/audit feature** cho creator economy: tránh trả thưởng cho content fake views, content vi phạm content policy. Không có ở vCreator (chỉ workflow content_flow đơn giản) và Ambassador (manual review qua admin).

---

## 3. `service/reconciliation_snapshot.go` — TCB-only (361 LOC)

Hàm public (6 fns):
- `InsertSnapshot(...)` — insert 1 snapshot từ crawl result
- `GetLatestSnapshot(...)` / `GetLatestSnapshotMap(...)` — get/map snapshot mới nhất
- `DetectMissingDays(...)` — phát hiện ngày thiếu snapshot (reconciliation gap)
- `MakeupCrawl(...)` — re-crawl các ngày thiếu (post-event reconciliation)

### Model `ReconciliationSnapshotRaw` (TCB-only, 17 fields)
`User, Event, Content, ContentSource, Date, ViewCount, LikeCount, CommentCount, ShareCount, Hashtags, CrawlSuccess, StatusCode, Data, Source...`

→ Lưu **per-day per-content metrics snapshot** từ crawl. Mục đích: dù content sau này bị xóa/edit, vẫn có lịch sử raw để đối chiếu.

### Ý nghĩa nghiệp vụ

`MakeupCrawl` đặc biệt thú vị: sau khi event kết thúc, TCB tự động tìm các ngày creator KHÔNG có snapshot (vd: API rate limit, network fail) và re-crawl. Đây là **eventual consistency** cho data crawl.

`DetectMissingDays` cho admin xem creator nào có gap data → cần chạy makeup trước khi đối chiếu.

→ Đây là **anti-fraud + data integrity feature**, ít platform có. vCreator/Ambassador chấp nhận data như được crawl, không có post-event makeup.

---

## 4. `service/reconciliation_snapshot_job.go` — TCB-only (107 LOC)

Hàm public (2 fns):
- `ReconciliationSnapshotJob()` — entry point cho async job
- `RunPostExpiryCrawl(...)` — chạy makeup crawl sau khi event hết hạn

→ Wrap snapshot logic trong async job (qua `asynq` queue) để chạy hàng đêm hoặc khi event close. Là **integration layer** giữa snapshot service + queue infrastructure.

---

## 5. Models phát hiện thú vị

### Models có CẢ 3 dự án (identical)
- `ReconciliationRaw` (10 fields) — top-level reconciliation record (title, status, conditions, statistic).
- `ReconciliationItemRaw` (16 fields) — 1 item = 1 (user, content/milestone, time range) cần đối chiếu.
- `ReconciliationHistoryRaw` (6 fields) — audit trail (type, options, author).

→ vCr/Amb có data shape giống TCB → có thể họ **đã chuẩn bị** cho reconciliation nhưng chưa implement engine, hoặc dùng admin manual.

### Models TCB-only (3)
- **`ReconciliationChecklistResultRaw`** + `ChecklistSummaryResult` — kết quả evaluation per item (pass/fail/unverified counts, suggested status).
- **`ReconciliationEventConfigRaw`** (7 fields: Event, ReconciliationClosed, ClosedAt, ClosedBy) — config close reconciliation per event (sau khi close, không evaluate nữa).
- **`ReconciliationSnapshotRaw`** (17 fields) — snapshot crawl data per day.

→ 3 model này là **engine layer**. Nếu vCr/Amb muốn port engine → cần tạo cả 3.

---

## 6. Câu hỏi business mở

1. **vCr/Amb có dùng admin reconciliation page không?** Đã verify trong matrix v2: cả 3 dự án có `admin/src/pages/reconciliation/`. Nhưng nếu không có service evaluation → admin page chỉ là CRUD list/manual override → có dùng thật?
2. **TCB `ReconciliationEventConfig.ReconciliationClosed`** — sau khi close, có cho phép re-open không? (Không thấy hàm `ReopenReconciliation` trong service.) Cần verify với business.
3. **vCreator `ActorType`** — có dùng cho audit batch import từ at-core không? `crosscheck` module có thể là consumer chính.
4. **Liên quan đến `docs/reconciliation-v2/`** — có folder docs cho reconciliation v2 trong repo `accesstrade-projects/docs/` → có thể đã có plan port reconciliation engine. Worth read.

---

## 7. Tổng kết group

| Khía cạnh | TCB | vCreator | Ambassador |
|---|---|---|---|
| **Reconciliation engine** | ✅ Đầy đủ (evaluate + classify + manual + snapshot + makeup) | ❌ Chỉ có model + admin CRUD | ❌ Chỉ có model + admin CRUD |
| **Audit ActorType** | ❌ | ✅ Phân biệt human_admin vs root_account | ❌ |
| **Snapshot crawl makeup** | ✅ Detect missing + post-expiry crawl | ❌ | ❌ |

**Hành động port khả thi**:
- TCB → vCr/Amb: port reconciliation engine (effort lớn — 3 services + 3 models + admin handlers)
- vCreator → TCB/Amb: port audit ActorType (effort nhỏ — vài chục LOC, chủ yếu thêm constants + 1 hàm)
