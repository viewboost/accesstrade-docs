# Gap #15 — vCreator/Ambassador thiếu hệ thống đối chiếu (reconciliation) tiền thưởng định kỳ + audit trail crawl chống fraud

> **Priority**: 🟠 **P1 (top priority)** — combined gap #6 + #15
> **Source**: Tổng hợp gap #6 (Reconciliation engine) + #15 (ReconciliationSnapshot) sau user clarify business intent
> **Direction port**: TCB → vCr/Amb (full stack)
> **Last verified**: 2026-05-07

---

# 📋 BUSINESS OVERVIEW

## Vấn đề là gì?

Sau khi platform trả tiền thưởng cho creator dựa trên metric tại thời điểm nhất định (vd: views ngày 1/5/2026 = 100k), có thể phát sinh các vấn đề:

1. **Fraud view boost**: creator dùng tool boost view giả → metric hiển thị 100k nhưng thật chỉ 10k → platform trả tiền sai
2. **Metric fluctuation**: TikTok/YouTube đôi khi adjust số liệu sau vài ngày → view ban đầu 100k, sau 1 tuần còn 80k (do platform clean fake views)
3. **Crawl missing**: hôm nào đó crawl bị lỗi → thiếu data ngày đó → reward tính sai
4. **Audit compliance**: kiểm toán hỏi "tại sao trả creator X số tiền Y vào ngày Z?" → cần tra ngược metric chính xác lúc đó

→ Cần hệ thống **đối chiếu định kỳ (reconciliation)** giữa "tiền đã trả" vs "metric thật sau khi đã ổn định" + **lưu lịch sử metric mỗi lần crawl** (audit trail) để tra ngược + **đánh dấu reward sai** cho admin xử lý.

## Hiện trạng 3 sản phẩm

### TCB — Có hệ thống đầy đủ ✅
- **ReconciliationSnapshot** (collection): mỗi lần crawl content → lưu snapshot {metric, hashtags, source_type (daily/post_expiry/makeup), date}. Chạy 3 luồng:
  - `daily_crawl`: cron hằng ngày
  - `post_expiry_crawl`: cron sau khi event hết hạn (đảm bảo có data cuối)
  - `makeup_crawl`: bù các ngày bị thiếu (admin trigger hoặc auto)
- **ReconciliationItem + Checklist**: admin tạo "đợt đối chiếu" → engine evaluate từng reward (so sánh metric snapshot vs reward đã trả) → output: `auto_approved` / `auto_rejected` / `needs_review`
- **Admin tools**: trang processing (đang chạy), running (đang xử lý), export, history audit trail
- **Engine functions**: 9 actions chính (Evaluate, ApplyClassification, ManualEvaluateItem, QuickApprove, QuickReject, Override, ConfirmStatus, ResetChecklistItem, GetLatestResult)

### vCreator + Ambassador — Có chân, không có thân ❌
- **Có 3 models cơ bản**: `reconciliation`, `reconciliation_item`, `reconciliation_history` (giống TCB)
- **Có admin page** `reconciliation` (frontend)
- **NHƯNG THIẾU**: 3 models nâng cao (`reconciliation_checklist`, `reconciliation_event_config`, `reconciliation_snapshot`), cả 3 services (engine, snapshot, snapshot job), 3 admin handlers nâng cao (processing, running, export)
- **Cũng có `content_crawl_history`** (lưu lịch sử crawl đơn giản giống cả 3 dự án), nhưng KHÔNG có snapshot per-day per-event như TCB
- → Admin page reconciliation tồn tại nhưng **KHÔNG có engine xử lý** — có thể là dead UI hoặc CRUD đơn thuần (chưa verify thật)

## Bảng so sánh 3 sản phẩm (góc nhìn business)

| Khía cạnh | TCB | vCreator | Ambassador |
|---|:---:|:---:|:---:|
| **Lưu lịch sử crawl đơn giản (mỗi content mỗi lần crawl)** | ✅ | ✅ | ✅ |
| **Lưu snapshot metric per-day per-event (cho đối chiếu sau)** | ✅ | ❌ | ❌ |
| **Crawl định kỳ daily** | ✅ | (giống nhau) | (giống nhau) |
| **Crawl bù sau khi event hết hạn (post-expiry)** | ✅ | ❌ | ❌ |
| **Crawl bù các ngày thiếu (makeup)** | ✅ | ❌ | ❌ |
| **Phát hiện ngày thiếu data tự động** | ✅ | ❌ | ❌ |
| **Engine đối chiếu tự động (auto-approve/reject/needs review)** | ✅ | ❌ | ❌ |
| **Admin tools đối chiếu (processing/running/export)** | ✅ | 🟡 Có UI nhưng không có engine | 🟡 Tương tự |
| **Audit trail compliance (tra ngược metric ngày X)** | ✅ | ❌ | ❌ |

## Hệ quả khi không có (vCreator/Ambassador)

1. **Không phát hiện fraud được**: nếu creator boost view giả → tiền thưởng đã trả không thể đối chiếu → mất tiền
2. **Không xử lý được metric fluctuation**: TikTok/YouTube revise data sau → reward đã trả không match → khó khôi phục
3. **Không có audit trail**: kiểm toán hỏi → không tra được metric tại thời điểm trả tiền → risk compliance
4. **Admin page reconciliation hiện tại có thể là dead UI**: tồn tại nhưng không có engine backend → confusing cho dev mới + ops
5. **Không phát hiện ngày crawl bị thiếu**: cron lỗi 1 ngày → reward ngày đó tính sai → không có cách auto-detect

## User confirm business intent (2026-05-07)

> *"Cái này quan trọng, để ở P1 nhưng ở vị trí trên cùng luôn"*
> *"vì lúc làm TCB tôi đã đánh giá kỹ rồi, nó ảnh hưởng nhiều lắm"*

→ User đã eval kỹ ở TCB → confidence cao là vCr/Amb cũng cần đầy đủ stack. Combine gap #6 (Reconciliation engine) + gap #15 (Snapshot) thành **1 task lớn**.

## Đề xuất giải pháp (góc nhìn business)

**Khuyến nghị**: Port toàn bộ stack reconciliation từ TCB sang vCreator + Ambassador. KHÔNG tách snapshot port riêng (Option A) vì snapshot mà không có engine = data lưu nhưng không dùng được.

**3 layers cần port (làm tuần tự)**:

### Layer 1: Snapshot infrastructure (~1-2 tuần mỗi sản phẩm)
- Tạo collection `reconciliation_snapshot` per (User, Event, Content, Date) với metric + raw data
- Thêm 3 source types: `daily_crawl`, `post_expiry_crawl`, `makeup_crawl`
- Insert hook vào content crawl flow của vCr/Amb (`CreateFlow` của content_flow.go)
- Functions: GetLatestSnapshot, GetLatestSnapshotMap, DetectMissingDays

### Layer 2: Snapshot jobs (~1 tuần mỗi sản phẩm)
- Cron `RunPostExpiryCrawl`: chạy sau khi event hết hạn, crawl content lần cuối
- Function `MakeupCrawl`: phát hiện + crawl bù các ngày thiếu
- Wire vào scheduler hiện có của vCr/Amb

### Layer 3: Reconciliation engine (~2-3 tuần mỗi sản phẩm)
- Tạo 3 collections nâng cao: `reconciliation_checklist`, `reconciliation_event_config`, mở rộng `reconciliation_item`
- Engine 9 functions: Evaluate, ApplyClassification, ManualEvaluateItem, QuickApprove/Reject, Override, ConfirmStatus, ResetChecklistItem
- Admin handlers: processing, running, export
- Refactor admin page reconciliation hiện có (dead UI) thành working flow

**Effort tổng**: ~4-6 tuần mỗi sản phẩm. Làm song song hoặc tuần tự.

### Có thể subset?

- **Subset A — Chỉ Snapshot**: ~2 tuần. Có audit trail nhưng không có engine đối chiếu. Đã từ chối (user xác nhận cần full).
- **Subset B — Snapshot + Engine, không có admin tools**: ~3-4 tuần. Engine chạy nhưng admin phải query DB trực tiếp.
- **Full (recommended)**: ~4-6 tuần. Tất cả 3 layers.

## Cần product/business confirm trước khi triển khai

1. **Ưu tiên port sản phẩm nào trước**: Ambassador (creator economy, có risk fraud cao) hay vCreator (B2B workplace, ít risk fraud)?
2. **Reuse 3 models cơ bản** (`reconciliation`, `reconciliation_item`, `reconciliation_history`) có ở vCr/Amb hay tạo lại từ TCB? Nếu reuse → cần migration để align fields với TCB.
3. **Admin page reconciliation hiện tại** ở vCr/Amb có records production không? Nếu có → cần migration data.
4. **Frequency cron daily crawl**: TCB crawl định kỳ — vCr/Amb hiện chỉ crawl theo trigger events. Đổi sang crawl định kỳ ảnh hưởng infra (load, content catcher quota).
5. **Compliance team**: có yêu cầu audit trail format cụ thể không? (vd: SOX/SOC yêu cầu retention >5 năm)

---

# 🔧 TECHNICAL SPECIFICATION

## TL;DR

TCB có **3 layers reconciliation** đầy đủ:
- **Layer 1**: `ReconciliationSnapshot` collection + service `reconciliation_snapshot.go` (~360 LOC, 5 fns)
- **Layer 2**: `reconciliation_snapshot_job.go` cron RunPostExpiryCrawl
- **Layer 3**: `ReconciliationChecklist` engine (~700 LOC, 9 fns) + `ReconciliationEventConfig` + admin handlers (processing, running, export)

vCr/Amb **có chân không có thân**: 3 models cơ bản + admin page tồn tại nhưng KHÔNG có 3 services chính + 3 models nâng cao.

## Verify code

### Models comparison

| Model | TCB | vCreator | Ambassador |
|---|---|---|---|
| `reconciliation.go` | ✅ 49 LOC | ✅ | ✅ |
| `reconciliation_item.go` | ✅ 58 LOC | ✅ | ✅ |
| `reconciliation_history.go` | ✅ 30 LOC | ✅ | ✅ |
| `reconciliation_checklist.go` (Result + Override) | ✅ 102 LOC | ❌ | ❌ |
| `reconciliation_event_config.go` | ✅ 28 LOC | ❌ | ❌ |
| `reconciliation_snapshot.go` | ✅ 46 LOC | ❌ | ❌ |

### Services comparison

| Service | TCB | vCreator | Ambassador |
|---|---|---|---|
| `reconciliation_checklist.go` (engine) | ✅ ~700 LOC | ❌ | ❌ |
| `reconciliation_snapshot.go` | ✅ 360 LOC, 5 fns | ❌ | ❌ |
| `reconciliation_snapshot_job.go` | ✅ ~150 LOC | ❌ | ❌ |

### Admin handlers comparison

| Handler | TCB | vCreator | Ambassador |
|---|---|---|---|
| `reconciliation.go` (basic CRUD) | ✅ | ✅ | ✅ |
| `reconciliation_processing.go` | ✅ | ❌ | ❌ |
| `reconciliation_running.go` | ✅ | ❌ | ❌ |
| `export_reconciliation.go` | ✅ | ❌ | ❌ |

### TCB ReconciliationSnapshot service (Layer 1)

**Interface** (`internal/service/reconciliation_snapshot.go:20`):
```go
type ReconciliationSnapshotInterface interface {
    InsertSnapshot(ctx, payload InsertSnapshotPayload) error
    GetLatestSnapshot(ctx, eventID, contentID modelmg.AppID) *modelmg.ReconciliationSnapshotRaw
    GetLatestSnapshotMap(ctx, eventID modelmg.AppID, contentIDs []AppID) map[AppID]*ReconciliationSnapshotRaw
    DetectMissingDays(ctx, eventID modelmg.AppID) ([]time.Time, error)
    MakeupCrawl(ctx, eventID modelmg.AppID, force bool) (*MakeupCrawlResult, error)
}
```

**Insert hook** (`internal/service/content_flow.go:CreateFlow`):
```go
// Insert reconciliation snapshot (async, non-blocking)
go func() {
    _ = ReconciliationSnapshot().InsertSnapshot(context.Background(), InsertSnapshotPayload{
        UserID:        b.User,
        EventID:       event.ID,
        ContentID:     b.ID,
        ContentSource: b.Source,
        ContentInfo:   contentInfo,
        Source:        modelmg.SnapshotSourceDailyCrawl,
    })
}()
```

**Snapshot sources** (`internal/model/mg/reconciliation_snapshot.go`):
```go
const (
    SnapshotSourceDailyCrawl  = "daily_crawl"
    SnapshotSourcePostExpiry  = "post_expiry_crawl"
    SnapshotSourceMakeupCrawl = "makeup_crawl"
)

type ReconciliationSnapshotRaw struct {
    ID            AppID
    User, Event, Content AppID
    ContentSource string
    Date          time.Time
    ViewCount, LikeCount, CommentCount, ShareCount int64
    Hashtags      []string
    CrawlSuccess  bool
    StatusCode    int
    Data          contentcatcher.ContentInfo  // raw response
    Source        string  // daily/post_expiry/makeup
    CrawledAt, CreatedAt time.Time
}
```

### TCB ReconciliationSnapshotJob (Layer 2)

**Cron `RunPostExpiryCrawl`** (`internal/service/reconciliation_snapshot_job.go`):
- Tìm events đã hết hạn (`endAt < now`, `status=active`) chưa được closed (`reconciliationClosed=false`)
- Loop từng event → crawl tất cả contents → insert snapshot với source=`post_expiry_crawl`
- Trigger từ scheduler `pkg/public/service/schedule.go:RunPostExpiryCrawl`

### TCB ReconciliationChecklist Engine (Layer 3)

**Interface** (`internal/service/reconciliation_checklist.go`):
```go
type ReconciliationChecklistInterface interface {
    EvaluateReconciliation(ctx, reconciliationID modelmg.AppID, overrideManual bool) (*EvaluateResult, error)
    GetLatestResult(ctx, reconciliationItemID modelmg.AppID) *ReconciliationChecklistResultRaw
    GetLatestResultMap(ctx, reconciliationID modelmg.AppID) map[AppID]*ReconciliationChecklistResultRaw
    ApplyClassification(ctx, reconciliationID, staffID modelmg.AppID, classificationFilter string) (*ApplyResult, error)
    ManualEvaluateItem(ctx, reconciliationItemID modelmg.AppID, code, status string, staffID modelmg.AppID) (*ReconciliationChecklistResultRaw, error)
    QuickApprove(ctx, reconciliationItemID, staffID modelmg.AppID) error
    QuickReject(ctx, reconciliationItemID, staffID modelmg.AppID) error
    Override(ctx, reconciliationItemID modelmg.AppID, toStatus, reason string, staffID modelmg.AppID) error
    ConfirmStatus(ctx, reconciliationItemID modelmg.AppID, targetStatus, reason string, staffID modelmg.AppID) (*ReconciliationChecklistResultRaw, error)
    ResetChecklistItem(ctx, reconciliationItemID modelmg.AppID, code string) (*ReconciliationChecklistResultRaw, error)
}
```

**EvaluateResult**:
```go
type EvaluateResult struct {
    TotalConditions, TotalConditionsPass, TotalConditionsFail, TotalConditionsSkipped int
    TotalAllItems, TotalSkippedItems, TotalItems int
    TotalAutoApproved, TotalAutoRejected, TotalNeedsReview int
}
```

→ Engine evaluate items theo conditions từ snapshot data → categorize 3 nhóm: auto-approved, auto-rejected, needs-review.

## Đề xuất implementation

### Phase 1: Snapshot infrastructure (~1-2 tuần mỗi sản phẩm)

1. **Schema**: tạo collection `reconciliation_snapshot` với 17 fields giống TCB
2. **Service**: copy `reconciliation_snapshot.go` từ TCB (~360 LOC)
3. **Insert hook**: thêm vào `content_flow.go:CreateFlow` của vCr/Amb (giống TCB pattern — async non-blocking)
4. **Test**: tạo content + crawl → verify snapshot được insert

### Phase 2: Snapshot jobs (~1 tuần mỗi sản phẩm)

5. **Job**: copy `reconciliation_snapshot_job.go` (~150 LOC)
6. **Wire vào scheduler** của vCr/Amb (cả 2 đều có scheduler infrastructure)
7. **Test**: tạo event sắp hết hạn → cron chạy → verify post_expiry snapshot được insert

### Phase 3: Reconciliation engine (~2-3 tuần mỗi sản phẩm)

8. **Schema**: tạo 3 collections nâng cao + extend `reconciliation_item` nếu cần
9. **Service**: copy `reconciliation_checklist.go` (~700 LOC) + adapt với business model target
10. **Admin handlers**: copy 3 handlers (processing, running, export)
11. **Frontend admin**: refactor admin page reconciliation để wire với engine mới
12. **Migration**: kiểm tra records hiện tại trong `reconciliation` collection (nếu có) → align schema

### Phase 4: Integration test + rollout (~3-5 ngày)

13. End-to-end test: tạo event → crawl content → expire event → cron crawl bù → admin tạo reconciliation → engine evaluate → admin review
14. Smoke test với data production (1 event nhỏ)
15. Rollout từng partner một (Ambassador có nhiều partners → rollout từng cái)

## Tổng effort

| Phase | vCreator | Ambassador |
|---|---|---|
| Phase 1: Snapshot infra | 1-2 tuần | 1-2 tuần |
| Phase 2: Snapshot jobs | 1 tuần | 1 tuần |
| Phase 3: Engine | 2-3 tuần | 2-3 tuần |
| Phase 4: Test + rollout | 3-5 ngày | 3-5 ngày |
| **Tổng mỗi sản phẩm** | **~5-7 tuần** | **~5-7 tuần** |

→ Có thể làm song song 2 sản phẩm (mỗi dev 1 product) → ~5-7 tuần real time.

## Risks + mitigations

1. **Schema migration**: 3 collections `reconciliation`, `reconciliation_item`, `reconciliation_history` có thể có records cũ ở vCr/Amb → fields cần align với TCB
   - **Mitigation**: dry-run migration trên staging, nếu có conflict → manual data fix
2. **Content catcher quota**: cron daily crawl + post-expiry crawl + makeup crawl sẽ tăng load lên content catcher service
   - **Mitigation**: phối hợp với team content catcher, có thể staggered rollout per partner
3. **Admin page reconciliation hiện có**: đã wire với 3 collections cơ bản → refactor có thể break existing
   - **Mitigation**: backward compat — giữ existing flow + thêm flow mới song song, deprecate dần
4. **Engine output có thể lệch giữa 3 sản phẩm**: business logic reconciliation (vd: ngưỡng auto-approve) có thể khác nhau
   - **Mitigation**: extract config thành `ReconciliationEventConfig` per-event, không hardcode ngưỡng

## Files referenced

**TCB (source of truth)**:
- `internal/model/mg/reconciliation.go` (49 LOC)
- `internal/model/mg/reconciliation_item.go` (58 LOC)
- `internal/model/mg/reconciliation_history.go` (30 LOC)
- `internal/model/mg/reconciliation_checklist.go` (102 LOC) — Result + Override structs
- `internal/model/mg/reconciliation_event_config.go` (28 LOC)
- `internal/model/mg/reconciliation_snapshot.go` (46 LOC)
- `internal/service/reconciliation_snapshot.go` (~360 LOC, 5 fns)
- `internal/service/reconciliation_snapshot_job.go` (~150 LOC)
- `internal/service/reconciliation_checklist.go` (~700 LOC, 9 fns)
- `internal/service/content_flow.go:CreateFlow` — snapshot insert hook
- `pkg/admin/handler/reconciliation.go` + `reconciliation_processing.go` + `reconciliation_running.go` + `export_reconciliation.go`
- `pkg/admin/service/reconciliation.go` + `export_reconciliation.go`
- `pkg/public/service/schedule.go:RunPostExpiryCrawl`

**vCreator + Ambassador (target — cần port)**:
- Đã có: 3 models cơ bản (`reconciliation`, `reconciliation_item`, `reconciliation_history`)
- Đã có: admin page `reconciliation` (frontend)
- Đã có: admin handler `reconciliation.go` cơ bản
- THIẾU: 3 models nâng cao + 3 services + 3 admin handlers nâng cao

## Liên quan đến gap khác

- **Gap #6 (TCB Reconciliation engine)**: gộp vào gap này 2026-05-07 — cùng task, không tách
- **Gap #9 (RecheckInProgress recovery)**: tied với reconciliation flow — khi engine evaluate gặp content thay đổi → cần safety state. Combine có thể tiết kiệm.
- **Gap #2 (InfluencerProfile concept)**: tied với at-core enrichment → khi port reconciliation, có thể tận dụng at-core data đã có

## Lịch sử phân loại

- **Initial gap-analysis (2026-05-07)**:
  - Gap #6: P2 (Total 11) — "TCB Reconciliation engine — chỉ TCB có. Port chỉ nếu cần"
  - Gap #15: P1 (Total 13) — "TCB ReconciliationSnapshot insert per crawl — anti-fraud audit trail"
- **2026-05-07 user clarify**: *"Cái này quan trọng, để ở P1 nhưng ở vị trí trên cùng luôn. Vì lúc làm TCB tôi đã đánh giá kỹ rồi, nó ảnh hưởng nhiều lắm."*
- **Decision**: Combine gap #6 + #15 thành 1 task lớn (Option B). Không port snapshot riêng (Option A) vì snapshot mà không có engine = data lưu nhưng không dùng được.
- **Reclassified**:
  - Gap #6: merged → này (gap #15)
  - Gap #15: P1 top priority với scope full reconciliation stack
  - Score: BV=5, Risk=4, Effort=2, XProd=4 → Total **15**

### Bài học methodology

- vCr/Amb **không phải "không có gì"** — có 3 models cơ bản + admin page. Đây là pattern thường thấy ở hàng loạt gaps (gap #5, #9): **TCB partial implementation** hoặc **vCr/Amb leftover from fork**.
- Khi gap mark "TCB-only feature" lần đầu, cần verify: vCr/Amb có dấu vết gì không? → quyết định strategy migrate vs port from scratch.
- User đã eval kỹ → trust user decision khi port full stack thay vì subset.
