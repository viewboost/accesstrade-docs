# Tech Spec — Merge Overflow Day

> Tài liệu kỹ thuật đi kèm [PRD Merge Overflow Day](./PRD.md).
> PRD trả lời **làm gì và vì sao**; file này trả lời **viết ở đâu, gọi hàm nào, ghi field gì**.
> Mọi tên hàm/field dưới đây đã đối chiếu với source thật trong `vcreator/backend`.

## Changelog

**2026-08-20 — bản đầu** (Thanh Trung).

**2026-08-20 — rà soát đối chiếu `vcreator@release` (`5ab1bc78`).** Mọi khối `> **Đính chính**` /
`> **Bổ sung**` là của đợt này, có trích code làm bằng. Xem Changelog của [PRD](./PRD.md) cho bốn nhóm
thay đổi; riêng ở file này, các mục bị viết lại là **1.2**, **1.3**, **2.1**, **2.2**, **3.2**, **3.3**,
**3.5**, **4.2**, **4.3**, **5**, **6**, **7**, **8**.

> Liên kết PRD ở bản đầu trỏ tới `./merge-overflow-day-event-analytic.md` — file không tồn tại, tên thật là
> `PRD.md`. Đã sửa.

## 1. Bối cảnh kỹ thuật

### 1.1 Chuỗi dữ liệu

```
content-flow ──(aggregate)──> content-analytic-daily ──> event-reward
                                                              │
                    content ──────────────────────────────────┤
                                                              ▼
                                    event-analytic-daily / user-event-analytic-daily
                                                              │
                                                              ▼
                                                        user-event
```

### 1.2 Ba sự thật quyết định thiết kế

**(a) `Update()` ghi đè, không cộng dồn.**
`internal/service/content_analytic_daily.go:405` — `ContentAnalyticDaily().Update()` aggregate lại toàn bộ `content-flow` của một ngày rồi **ghi đè** `view.value`:

```go
// nhánh doc đã tồn tại
doc.View = modelmg.ContentAnalyticDaily{
    Begin: doc.View.Begin,
    Value: s.TotalView + doc.TotalManualView,   // s = aggregate từ content-flow
    End:   doc.View.Begin + s.TotalView + doc.TotalManualView,
}
```

**(b) `content-flow` bị dọn sau 30 ngày.**
`internal/service/content_analytic_daily.go:243` — `DeleteContentFlow()` chạy ở cuối mỗi lần `Audit()`, backup rồi xóa flow của mọi doc có `auditStatus = valid` và `date <= now-30d`.

→ (a) + (b): nếu gọi `Update()` cho ngày đích khi flow ngày đích đã bị dọn, `s.TotalView` chỉ còn phần flow vừa dịch sang, và **ghi đè mất toàn bộ view gốc**. Đây là lý do migration **không dùng `Update()`**.

**(c) Các hàm phía sau không đọc `content-flow`.**

| Hàm | File | Nguồn aggregate |
|---|---|---|
| `UpdateRewardTypeByStatisticContent` | `internal/service/event_schema.go:173` | `doc.View.Value` của `content-analytic-daily` |
| `UpdateAnalyticEventDaily` | `internal/service/event.go:284` | `content` + `event-reward`, match `date = q.FromAt` |
| `UpdateAnalyticUserEventDaily` | `internal/service/event.go:40` | `content` + `event-reward`, match `date = q.FromAt` |

→ Gộp thẳng vào `content-analytic-daily` là đủ để **phần view** của chuỗi phía sau ra số đúng. Phần **tiền**
thì không — xem (d).

**(d) `UpdateRewardTypeByStatisticContent` không dùng được cho ngày đích.**
Ba lý do, đọc từ `internal/service/event_schema.go:173-325`:

```go
// (d1) hết suất schema -> bỏ qua, không sinh reward nào
if !schema.Quantity.IsUnlimited && schema.Quantity.Remaining <= 0 {
    if !isExtended { continue }
}

// (d2) chỉ nhận schema phủ ĐÚNG ngày của doc — startAt/endAt là của SCHEMA, không phải của event
if !isExtended {
    cond["endAt"]   = bson.M{"$gte": doc.Date}
    cond["startAt"] = bson.M{"$lte": doc.Date}
}

// (d3) chỉ trừ phần đã đối soát CỦA ĐÚNG NGÀY ĐANG TÍNH
view, like, comment := Content().GetStatisticContentIsRewardInDay(ctx, event, content, doc.Date, isExtended)
totalView := doc.View.Value - view.Completed
```

`GetStatisticContentIsRewardInDay` match `date = doc.Date` (`aggregate_pipeline/event_reward.go:772`), nên
reward đang nằm ở ngày nguồn **hoàn toàn vô hình** với nó. Gộp view vào ngày đích rồi gọi hàm này trong khi
reward ngày nguồn vẫn còn là **trả hai lần cho cùng một lượt view**.

→ Reward được **chuyển** từ ngày nguồn sang ngày đích bằng phép cộng tường minh, không recompute. Xem 3.5.

**(e) Ba trạng thái của reward là ba việc khác nhau.**

| Mốc | Nơi đặt | Nghĩa |
|---|---|---|
| `status = pending` | `event_schema.go:277-284`, suy từ `content.Status` | Tiền dự kiến |
| `status = completed` | `pkg/admin/service/reconciliation_running.go:261` | **Đã đối soát**. Chưa trả đồng nào |
| `isTransfer = true` + `transferId` | `pkg/admin/service/transfer.go:93-108` | **Đã chi** |

```go
// transfer.go — quét CashFlow của một transfer rồi đóng dấu ngược lên reward
"$set": bson.M{"transferId": d.TransferId, "isTransfer": true, "updatedAt": time.Now()}
```

→ Điều kiện chặn "đã chi" bám `isTransfer` / `transferId`. Bám `status = completed` là chặn oan mọi event
đã đối soát xong.

**(f) Reward milestone có hình dạng khác hẳn.**
`by-view-milestone` (`event_schema.go:97-125`) và `by-content-milestone` (`event_schema.go:438-460`):

```go
reward := &modelmg.EventRewardRaw{
    Type:    s.Type,                                  // by-view-milestone | by-content-milestone
    Date:    util.TimeStartOfDayInHCM(time.Now()),    // NGÀY JOB CHẠY, không phải ngày phát sinh view
    Options: &modelmg.EventRewardOpts{},              // RỖNG — không có contentId
    Statistic: modelmg.EventRewardStatistic{TotalCashMilestone: s.CashReward.CashMilestone},
}
```

Chống trùng bằng "đã tồn tại một dòng", không phải bằng khóa duy nhất:

```go
if totalClaimed := EventRewardDAO().CountByCondition(ctx, ..., bson.M{
    "event": event.ID, "user": userEvent.User, "schema._id": s.ID,
    "status": bson.M{"$ne": constants.StatusRejected},
}); totalClaimed >= 1 { return }
```

→ Mỗi (user, event, schema) chỉ có **một** dòng, nên không tồn tại dòng ngày đích để cộng vào — nhánh duy
nhất là đổi `date`. Và **xóa dòng milestone là tự tạo lại sự cố**: lần kiểm tra sau sinh lại với ngày hôm nay.

→ Ngưỡng milestone tính từ `userEvent.Statistic.<nguồn>.View.Completed` (view đã đối soát), mà migration
không đụng trạng thái đối soát, nên gộp view **không** làm phát sinh hay mất mốc nào.

### 1.3 Hai cạm bẫy đã xác minh

**`ContentFlowRaw` không có `month` / `year`.** `internal/model/mg/content_flow.go` chỉ có `Date time.Time`. Hai field đó thuộc `ContentAnalyticDailyRaw`. Khi dịch flow chỉ update `date`.

**`UpdateAnalyticUserEventDaily` ghi bằng upsert** (`internal/service/event.go:258`, `options.Update().SetUpsert(true)`), match theo `content.date` — mà `content.date` là ngày đăng bài, migration không đụng tới.

> **Đính chính** — vế "xóa mù doc analytic ngày nguồn sẽ bị upsert lại ở lần recompute sau" là **sai**. Các job
> recompute duyệt **doc đang tồn tại**, không duyệt dải ngày (`internal/service/event.go:1046`,
> `pkg/admin/service/shedule.go:406`):
>
> ```go
> cond = bson.M{"event": event.ID, "date": bson.M{"$lt": q.FromAt}}
> _ = EventAnalyticDailyDAO().GetShare().Find(ctx, ..., cond)(&eventDaily)
> for _, ed := range eventDaily { /* recompute đúng ed.Date */ }
> ```
>
> Doc đã xóa thì không job nào ghé lại. Vẫn giữ thứ tự "recompute trước, xóa sau", nhưng vì lý do khác:
> chỉ sau khi recompute mới biết ngày nguồn còn content thật hay đã rỗng.

**Trùng doc ở cặp (content, date) là chuyện có thật.** Index `{content, date}` **không unique**
(`internal/module/database/mongodb/index.go:157-166`), và hệ thống có sẵn một migration chuyên gỡ trùng đúng
cặp khóa đó (`/migration/remove-duplicate/content-analytic-daily`). Planner gom theo `content` nên gặp hai doc
cùng ngày sẽ lấy một bỏ một, còn `DeleteMany` theo `{event, date}` thì xóa cả cụm.

> **Không dùng migration gỡ trùng sẵn có làm bước chuẩn bị.** Nó không trung tính — với mỗi cụm trùng có
> reward, nó ghi đè `view.value` thành `TotalViewCompleted` rồi reject sạch reward `pending`
> (`pkg/admin/service/migration.go:632-660`):
>
> ```go
> primaryDoc.View = modelmg.ContentAnalyticDaily{
>     Begin: primaryDoc.View.Begin,
>     Value: rewardReport.TotalViewCompleted,
>     End:   primaryDoc.View.Begin + rewardReport.TotalViewCompleted,
> }
> ...
> "$set": bson.M{"status": constants.StatusRejected, "note_migration": "migration_content_analytic_v2"}
> ```
>
> Gặp trùng thì **chặn và báo cáo**, không tự gỡ.

**`Audit()` chỉ chạm doc `pending`.** `cond = {auditStatus: pending, date: {$lt: hôm nay}, isExtended: {$ne: true}}`
(`internal/service/content_analytic_daily.go:318-321`). Doc ngày đích đang `valid` / `completed` thì bước 4
(`content-flow`) không có tác dụng gì lên nó — không sai, chỉ là thừa; giữ để không phải phân nhánh thêm.

## 2. Hạ tầng phải dựng mới

### 2.1 Collection và index

`internal/module/database/mongodb/collection.go` — thêm hai hằng số:

```go
CollectionMigrationJob               = "migration-jobs"
CollectionContentAnalyticDailyBackup = "content-analytic-daily-backups"
```

> `CollectionContentFollowBackup = "content-follow-backups"` đã có sẵn (dòng 28), nhưng **chưa có** collection backup cho `content-analytic-daily` — phải tạo mới. PRD nói "collection backup sẵn có" chỉ đúng với `content-flow`.

`internal/module/database/mongodb/index.go` — đăng ký index theo pattern của `affiliate_indexes.go`:

| Collection | Index | Mục đích |
|---|---|---|
| `migration-jobs` | `{type: 1, startedAt: -1}` | endpoint list: lọc `type`, sort `startedAt` desc |
| `content-analytic-daily-backups` | `{jobId: 1}` | tra backup của một lần chạy |
| `event-reward-backups` | `{jobId: 1}` | backup reward trước khi chuyển ngày |
| `content-analytic-daily` | `{event: 1, date: 1}` | **thiếu sẵn** — xem bên dưới |

> **Bổ sung** — `content-analytic-daily` hiện chỉ có `content`, `{content, date}`, `event`, `user`, `partner`,
> `auditStatus` (`index.go:157-166`). **Không có `{event, date}`**, trong khi mọi truy vấn của migration này
> (đếm cho guard, tìm doc hai ngày, xóa doc ngày nguồn) đều lọc đúng cặp đó — Mongo sẽ dùng index `event`
> rồi quét toàn bộ ngày của event. `content-flow` thì đã có sẵn `{event, date}` (`index.go:110`).
> `event-reward` đã có `{event, date}` (`index.go:148`).

### 2.2 Model mới

**`internal/model/mg/migration_job.go`** — port từ `ambassabor/backend/internal/model/mg/migration_job.go`,
**năm** khác biệt đã chốt ở PRD:

```go
const (
    MigrationJobTypeMergeOverflowDay = "merge-overflow-day"
)

const (
    MigrationJobStatusRunning = "running"
    MigrationJobStatusDone    = "done"
    MigrationJobStatusFailed  = "failed"
    MigrationJobStatusAborted = "aborted"   // KHÁC BẢN GỐC — guard chặn
)

type MigrationJobParams struct {                 // KHÁC BẢN GỐC — bỏ field ambassador-only
    DryRun        bool   `bson:"dryRun"        json:"dryRun"`
    Event         string `bson:"event"         json:"event"`         // event._id hex
    OverflowDate  string `bson:"overflowDate"  json:"overflowDate"`  // ISO date — ngày TRÀN (nguồn)
    MergeIntoDate string `bson:"mergeIntoDate" json:"mergeIntoDate"` // ISO date — ngày GỘP VỀ (đích)
    DatesDerived  bool   `bson:"datesDerived"  json:"datesDerived"`  // true = hệ thống tự suy từ event.endAt
}

type MigrationJobReport struct {                 // KHÁC BẢN GỐC — field mới
    AbortReasons     []string                  `bson:"abortReasons,omitempty"     json:"abortReasons,omitempty"`
    DocsAffected     map[string]int            `bson:"docsAffected"               json:"docsAffected"`      // collection -> số doc
    TotalViewBefore  float64                   `bson:"totalViewBefore"            json:"totalViewBefore"`
    TotalViewAfter   float64                   `bson:"totalViewAfter"             json:"totalViewAfter"`
    TotalCashBefore  float64                   `bson:"totalCashBefore"            json:"totalCashBefore"`
    TotalCashAfter   float64                   `bson:"totalCashAfter"             json:"totalCashAfter"`
    Contents         []MigrationJobContentItem `bson:"contents"                   json:"contents"`
    ContentsOnOverflowDate []string            `bson:"contentsOnOverflowDate,omitempty" json:"contentsOnOverflowDate,omitempty"` // content.date = ngày tràn, chặn xóa doc
    CashBySchema     []MigrationJobCashBySchema `bson:"cashBySchema"               json:"cashBySchema"`
    PaidRewards      []MigrationJobPaidReward   `bson:"paidRewards,omitempty"      json:"paidRewards,omitempty"`
}

type MigrationJobContentItem struct {
    Content    string  `bson:"content"    json:"content"`
    ViewBefore float64 `bson:"viewBefore" json:"viewBefore"`
    ViewAfter  float64 `bson:"viewAfter"  json:"viewAfter"`
}

// Cash phải tách theo schema, không chỉ một con số tổng: nhánh đổi ngày có thể
// làm reward rơi sang một schema khác đơn giá, tổng bằng nhau vẫn giấu được lệch.
type MigrationJobCashBySchema struct {
    Schema      string  `bson:"schema"      json:"schema"`      // schema._id hex
    SchemaType  string  `bson:"schemaType"  json:"schemaType"`  // by-statistic | by-view-milestone | by-content-milestone
    CashBefore  float64 `bson:"cashBefore"  json:"cashBefore"`
    CashAfter   float64 `bson:"cashAfter"   json:"cashAfter"`
    RowsMerged  int     `bson:"rowsMerged"  json:"rowsMerged"`  // số dòng cộng dồn
    RowsMoved   int     `bson:"rowsMoved"   json:"rowsMoved"`   // số dòng đổi ngày
}

// Đếm reward đã chi ở ngày nguồn. Khác 0 là abort — in ra để người vận hành
// thấy vì sao bị chặn mà không phải query DB.
type MigrationJobPaidReward struct {
    Reward     string  `bson:"reward"     json:"reward"`
    TransferId string  `bson:"transferId" json:"transferId"`
    Cash       float64 `bson:"cash"       json:"cash"`
}
```

Phần còn lại (`MigrationJobRaw`, `MigrationJobFailedSample`, `MigrationJobProgress`, `MigrationJobStats`,
`DbModelName()`) giữ nguyên như bản gốc, thêm field `Report *MigrationJobReport`.

> **Đính chính** — bốn chỗ lệch so với bản gốc ambassador:
>
> 1. Type mẫu tên thật là **`MigrationJobFailedSample`**, không phải `MigrationJobSample`.
> 2. Bản gốc **không có** `SkippedSamples` và **không có** helper `recordSkippedSample`. Bộ helper thật đúng
>    năm hàm: `newMigrationJob`, `saveMigrationJob`, `recordFailedSample`, `finishMigrationJob`, cộng
>    `GetMigrationJob` / `ListMigrationJobs`. Thêm `skippedSamples` là **khác biệt thứ tư**, phải kể vào.
> 3. `newMigrationJob(ctx, jobType string, dryRun, preferCache bool, requested int, startedBy string)` — bỏ
>    `preferCache`/`requested` là đổi chữ ký. **Khác biệt thứ năm.**
> 4. `MigrationJobRaw.StartedBy` là `string`, còn `cc.GetCurrentUserID()` trả `primitive.ObjectID`
>    (`internal/echo/echo.go:151`) — phải `.Hex()`.
>
> Đường dẫn ba file gốc ở PRD thiếu tiền tố `backend/`; đường đúng là
> `ambassabor/backend/internal/model/mg/migration_job.go`, `.../dao/migration_jobs.go`,
> `.../pkg/admin/service/migration_job.go`.

**`internal/model/mg/event_reward.go`** — thêm bốn field truy vết vào `EventRewardRaw`. Không sửa field cũ:

```go
MergedIntoRewardId  AppID     `bson:"mergedIntoRewardId,omitempty"  json:"mergedIntoRewardId,omitempty"`
MergedFromRewardIds []AppID   `bson:"mergedFromRewardIds,omitempty" json:"mergedFromRewardIds,omitempty"`
OriginalDate        time.Time `bson:"originalDate,omitempty"        json:"originalDate,omitempty"`
MigrationJobId      AppID     `bson:"migrationJobId,omitempty"      json:"migrationJobId,omitempty"`
```

Mục đích: biên bản đối soát cũ trỏ vào ngày nguồn vẫn lần ra được tiền đã đi đâu. `omitempty` để không làm
phình mọi doc reward khác.

**`internal/model/mg/content_analytic_daily_backup.go`** — copy `ContentAnalyticDailyRaw`, thêm `JobID AppID` và `BackupAt time.Time`, `DbModelName()` trả `CollectionContentAnalyticDailyBackup`.

### 2.3 DAO mới

`internal/module/database/mongodb/dao/migration_jobs.go`, `.../content_analytic_daily_backup.go` và
`.../event_reward_backup.go` — copy nguyên pattern của `dao/content_flow_backup.go` (struct rỗng +
`GetShare()` trả `GetDBShare()`).

> **Bổ sung** — `event-reward-backups` là collection mới. Bước 5 sửa dòng tiền (cộng dồn / đổi ngày) nên phải
> có bản gốc để lùi. Collection backup sẵn có trong repo chỉ có `content-follow-backups` (`collection.go:28`).

## 3. Module nghiệp vụ

Ba file trong `pkg/admin/service/`.

### 3.1 `merge_overflow_day_planner.go` — thuần logic, không import DAO

```go
type MergeInput struct {
    FromDocs []*modelmg.ContentAnalyticDailyRaw   // doc ngày nguồn
    ToDocs   []*modelmg.ContentAnalyticDailyRaw   // doc ngày đích
    // begin dự phòng cho content chưa từng có doc ngày đích:
    // map[content hex] = end của doc gần nhất TRƯỚC ngày đích
    PrevEnds map[string]modelmg.ContentAnalyticDaily
}

type MergeItem struct {
    Content         modelmg.AppID
    ToDocID         modelmg.AppID   // zero = phải insert doc mới
    View            modelmg.ContentAnalyticDaily
    Like            modelmg.ContentAnalyticDaily
    Comment         modelmg.ContentAnalyticDaily
    TotalManualView float64
    FromDocID       modelmg.AppID   // doc ngày nguồn sẽ bị xóa
}

type MergePlan struct {
    Items           []MergeItem
    TotalViewBefore float64
    TotalViewAfter  float64
}

func BuildMergePlan(in MergeInput) MergePlan
```

Công thức cho từng content, áp dụng giống nhau cho `view` / `like` / `comment`:

```
begin = begin(ToDoc)                    nếu ToDoc tồn tại
      = PrevEnds[content].End           nếu không
value = value(ToDoc) + value(FromDoc)   (thiếu vế nào thì coi là 0)
end   = begin + value
totalManualView = totalManualView(ToDoc) + totalManualView(FromDoc)
```

Bất biến: `TotalViewAfter == TotalViewBefore`. Content chỉ có ở ngày đích **không** vào `Items`.

### 3.2 `merge_overflow_day_guard.go` — thuần logic, không import DAO

```go
type GuardInput struct {
    Event             *modelmg.EventRaw
    OverflowDate      time.Time
    MergeIntoDate     time.Time
    OverflowDocCount  int    // số content-analytic-daily ở ngày tràn
    AfterOverflowCount int   // số content-analytic-daily ở ngày SAU ngày tràn
    PaidRewardCount   int    // event-reward ngày tràn có isTransfer=true HOẶC transferId khác zero
    DuplicateDocCount int    // số cặp (content, date) bị trùng ở hai ngày liên quan
}

func CheckMergeOverflowDay(in GuardInput) []string   // rỗng = cho chạy
```

| # | Điều kiện | Lý do trả về |
|---|---|---|
| 1 | `Event.IsExtendedPeriod()` | `EXTENDED_PERIOD_ENABLED` |
| 2 | `!MergeIntoDate.Equal(startOfDay(Event.EndAt))` | `MERGE_INTO_DATE_NOT_EVENT_END_AT` |
| 3 | `!OverflowDate.Equal(MergeIntoDate.AddDate(0,0,1))` | `OVERFLOW_DATE_NOT_ADJACENT` |
| 4 | `!OverflowDate.After(MergeIntoDate)` | `OVERFLOW_DATE_NOT_AFTER_MERGE_INTO_DATE` |
| 5 | `AfterOverflowCount > 0` | `OVERFLOW_MORE_THAN_ONE_DAY` |
| 6 | `PaidRewardCount > 0` | `REWARD_ALREADY_TRANSFERRED_ON_OVERFLOW_DATE` |
| 7 | `DuplicateDocCount > 0` | `DUPLICATE_CONTENT_ANALYTIC_DAILY` |
| 8 | `OverflowDocCount == 0` | `NOTHING_TO_MERGE` |

> **Đính chính** — điều kiện cũ số 5 đọc là "`event-reward` ngày nguồn có `isTransfer` **hoặc** `status
> completed`". Bỏ vế `completed`: đó là **đã đối soát**, chưa chi (xem 1.2(e)). Giữ vế đó thì migration bị chặn
> oan trên gần như mọi event đã kết thúc, vì đối soát xong là reward về `completed` hết. Điều kiện đúng:
>
> ```go
> paidCond := bson.M{
>     "event": eventID, "date": overflowDate,
>     "$or": []bson.M{
>         {"isTransfer": true},
>         {"transferId": bson.M{"$exists": true, "$ne": primitive.NilObjectID}},
>     },
> }
> ```
>
> Bản đầu còn gọi điều kiện này là "phòng thủ, trên lý thuyết không bao giờ kích hoạt". Không đúng — ngày tràn
> **có thể** có reward (1.2(d2)), và nếu đã chi thì đây là nhánh chặn chính, không phải hình thức.

> **Bổ sung** — điều kiện 4 và 7 là mới. Số 4 chặn gõ ngược nguồn/đích. Số 7 chặn trùng doc, xem 1.3.

Trả **toàn bộ** lý do khớp, không return sớm ở lý do đầu tiên — vận hành cần thấy hết trong một lần dry-run.

### 3.3 `merge_overflow_day.go` — Executor, chỉ điều phối I/O

```go
func (m migrationImpl) MergeOverflowDay(
    ctx context.Context,
    job *modelmg.MigrationJobRaw,
    eventID modelmg.AppID,
    overflowDate, mergeIntoDate time.Time,
    dryRun bool,
)
```

Chạy trong goroutine, mở đầu bằng `defer m.finishMigrationJob(ctx, job, "[MIGRATION][MERGE-OVERFLOW-DAY]")`.

**Giai đoạn 0 — nạp và kiểm tra**

1. `EventDAO().FindById` → `EventRaw`. Không tìm thấy → abort `EVENT_NOT_FOUND`.
2. Đếm **bốn** con số cho guard bằng `CountByCondition`: doc ngày tràn, doc ngày sau ngày tràn, **reward đã chi
   ở ngày tràn** (`isTransfer = true` hoặc có `transferId`), và **số cặp (content, date) bị trùng** ở hai ngày.
3. `CheckMergeOverflowDay(...)`. Có lý do → `job.Status = aborted`, `job.Report.AbortReasons = reasons`, return.
4. `Find` doc `content-analytic-daily` của hai ngày (`event` + `date`, `isExtended: {$ne: true}`).
5. Với content chỉ có ở ngày tràn: `FindOne` doc gần nhất `date < mergeIntoDate` cùng content, sort `date: -1` → `PrevEnds`.
6. `Find` **`event-reward` của cả hai ngày** (`{event, date}`) → `BuildRewardPlan(...)`, xem 3.5.
7. `BuildMergePlan(...)` → set `job.Progress.Total = len(plan.Items)`, `saveMigrationJob`.
8. Dựng `job.Report`: số doc theo collection, tổng view trước–sau, **cash trước–sau tách theo từng schema**,
   danh sách content, và danh sách reward đã chi (nếu có, để giải thích lý do abort).
9. `dryRun == true` → `saveMigrationJob`, return. **Không ghi gì.**

**Giai đoạn 1 — ghi (chỉ khi `dryRun == false`)**

| Bước | Thao tác | Ghi chú |
|---|---|---|
| 1 | Backup `content-analytic-daily` **cả hai ngày**, `content-flow` ngày tràn, **và `event-reward` cả hai ngày**, gắn `jobId` | `InsertMany` vào ba collection backup |
| 2 | Ghi doc ngày đích theo `plan.Items` | `BulkWrite`: `UpdateOne` nếu `ToDocID` khác zero, `InsertOne` nếu zero |
| 3 | Xóa doc `content-analytic-daily` ngày tràn | `DeleteMany` theo `event` + `date` |
| 4 | Xử lý `content-flow` cho `Audit()` | xem 3.4 |
| 5 | **Chuyển reward** ngày tràn sang ngày đích | quét theo `{event, date}`, KHÔNG đi theo `plan.Items`, xem 3.5 |
| 6 | Recompute analytic cấp event/user **hai ngày** | xem 3.6 |

> **Bổ sung** — bước 1 thêm backup `event-reward`. Bước 5 sửa dòng tiền nên phải có đường lùi.
> Bước 5 quét độc lập với `plan.Items` vì reward milestone không có `options.contentId`, và có thể tồn tại
> reward ở ngày tràn cho một content không có doc analytic ở ngày đó — đi ké danh sách content sẽ bỏ sót,
> để lại reward mồ côi ngoài vòng đời event.

Sau mỗi content ở bước 5: `job.Progress.Current++`, flush mỗi `jobFlushEvery` (25) record. Lỗi một content → `recordFailedSample` + `job.Stats.Failed++`, **không** dừng cả job.

### 3.4 Bước 4 — `content-flow`

> **Đính chính** — bản đầu đếm flow ngày đích **theo cả event** rồi chọn một nhánh cho tất cả. Sai tầng:
> `DeleteContentFlow()` dọn **theo từng doc**, điều kiện `auditStatus = valid` và `date <= now-30d`
> (`internal/service/content_analytic_daily.go:243-262`), nên trạng thái là **trộn** — content này còn flow,
> content kia đã bị dọn. Quyết định nhánh phải theo **từng content**:
>
> ```go
> for _, item := range plan.Items {
>     flowOnTo := ContentFlowDAO().CountByCondition(ctx, ..., bson.M{
>         "content": item.Content, "date": mergeIntoDate,
>     })
>     // ... nhánh A hoặc B cho riêng content này
> }
> ```
>
> Ở thời điểm ngay sau sự cố (ngày đích mới 20 ngày tuổi) mọi content đều rơi vào nhánh A, nên khác biệt chưa
> lộ. Chạy muộn quá 30 ngày thì lộ.

Khung logic (viết theo cả event cho gọn; khi cài đặt thì lặp theo từng content như khối trên):

```go
flowOnTo := ContentFlowDAO().CountByCondition(ctx, ..., bson.M{"event": eventID, "date": mergeIntoDate})
if flowOnTo > 0 {
    // Nhánh A — dịch date, Audit() sẽ khớp
    ContentFlowDAO().GetShare().UpdateMany(ctx, ...,
        bson.M{"event": eventID, "date": overflowDate},
        bson.M{"$set": bson.M{"date": mergeIntoDate, "updatedAt": time.Now()}},
    )
    // KHÔNG set month/year — ContentFlowRaw không có hai field này
} else {
    // Nhánh B — flow ngày đích đã bị DeleteContentFlow() dọn.
    // Backup + xóa flow ngày nguồn để nó không tái sinh doc ngày nguồn,
    // rồi đánh doc ngày đích completed để Audit() bỏ qua —
    // đúng quy ước của DeleteContentFlow (doc không còn flow => completed).
    ContentAnalyticDailyDAO().GetShare().UpdateMany(ctx, ...,
        bson.M{"event": eventID, "date": mergeIntoDate},
        bson.M{"$set": bson.M{"auditStatus": constants.StatusCompleted}},
    )
}
```

### 3.5 Bước 5 — chuyển reward từ ngày tràn sang ngày đích

> **Đính chính** — mục này thay hoàn toàn bản đầu. Bản đầu gọi `UpdateRewardTypeByStatisticContent` cho ngày
> đích và coi hành vi "insert reward mới cho phần chênh" là đúng thiết kế. Bỏ cả hai, lý do ở 1.2(d):
> hàm đó **nuốt tiền** khi schema hết suất, **mất tiền** khi schema không phủ ngày đích, và **trả đúp** vì nó
> chỉ trừ phần đã đối soát của đúng ngày đang tính — reward ở ngày tràn hoàn toàn vô hình với nó.

**Module thuần `merge_overflow_day_reward_planner.go`** — không import DAO:

```go
type RewardInput struct {
    OnOverflow []*modelmg.EventRewardRaw   // reward ngày tràn
    OnMergeInto []*modelmg.EventRewardRaw  // reward ngày đích
}

type RewardActionKind int
const (
    RewardActionAccumulate RewardActionKind = iota  // cộng dồn vào dòng ngày đích
    RewardActionMoveDate                            // đổi date sang ngày đích
)

type RewardAction struct {
    Kind     RewardActionKind
    Source   modelmg.AppID          // reward ngày tràn
    Target   modelmg.AppID          // reward ngày đích (zero khi MoveDate)
    AddStat  modelmg.EventRewardStatistic  // phần cộng thêm (chỉ dùng cho Accumulate)
    AddCash  float64
}

func BuildRewardPlan(in RewardInput) []RewardAction
```

Luật chọn nhánh:

| Loại | Có dòng ngày đích cùng `schema._id` **và** cùng `status`? | Nhánh |
|---|---|---|
| `by-statistic` | Có | `Accumulate` |
| `by-statistic` | Không | `MoveDate` |
| `by-view-milestone` / `by-content-milestone` | Luôn không (mỗi bộ một dòng, 1.2(f)) | `MoveDate` |

Khớp theo `schema._id` chứ không theo `type`: một event có nhiều schema cùng type `by-statistic` khác nguồn,
khác đơn giá (1.2(e)). Khớp cả `status` vì đó là một phần khóa nhận dạng reward (`event_schema.go:291-299`).

Không có nhánh xóa. Với milestone, xóa là tự tạo lại sự cố (1.2(f)).

**Executor thi hành:**

```go
// Accumulate — cộng thẳng, không recompute
UpdateOne(ctx, ..., bson.M{"_id": a.Target}, bson.M{
    "$inc": bson.M{
        "statistic.totalView":          a.AddStat.TotalView,
        "statistic.totalCashView":      a.AddStat.TotalCashView,
        "statistic.totalLike":          a.AddStat.TotalLike,
        "statistic.totalCashLike":      a.AddStat.TotalCashLike,
        "statistic.totalComment":       a.AddStat.TotalComment,
        "statistic.totalCashComment":   a.AddStat.TotalCashComment,
        "statistic.totalCashMilestone": a.AddStat.TotalCashMilestone,
        "cash":                         a.AddCash,
    },
    "$addToSet": bson.M{"mergedFromRewardIds": a.Source},
    "$set":      bson.M{"migrationJobId": job.ID, "updatedAt": time.Now()},
})
// dòng ngày tràn: zero số, giữ dòng làm dấu vết
UpdateOne(ctx, ..., bson.M{"_id": a.Source}, bson.M{"$set": bson.M{
    "statistic": modelmg.EventRewardStatistic{}, "cash": 0,
    "mergedIntoRewardId": a.Target, "originalDate": overflowDate,
    "migrationJobId": job.ID, "updatedAt": time.Now(),
}})

// MoveDate — đổi ngày, giữ nguyên số
UpdateOne(ctx, ..., bson.M{"_id": a.Source}, bson.M{"$set": bson.M{
    "date": mergeIntoDate, "originalDate": overflowDate,
    "migrationJobId": job.ID, "updatedAt": time.Now(),
}})
```

**Sau khi xong toàn bộ reward của một user**, gọi một lần cho user đó:

```go
service.Event().UpdateStatisticUserEvent(ctx, userID, eventID)
```

Hàm này aggregate lại **tất cả** reward của cặp (user, event), không lọc theo ngày
(`internal/service/event.go:524`), nên gọi sau cùng là đủ để `user-event` khớp lại — **không cần bước riêng**.
Gọi tiếp `Content().UpdateCashStatistic` và `User().UpdateStatistic` cho các content bị đụng.

**Bất biến phải kiểm:** tổng `cash` của event trước và sau bước 5 **bằng nhau**. Ngoại lệ duy nhất là khi ngày
tràn vốn không có reward nào — lúc đó không có gì để chuyển, và phần view gộp thêm chỉ ra tiền nếu có ai đó
chạy recompute sau này; báo cáo phải nói rõ trường hợp này để vận hành không tưởng là migration làm mất tiền.

> **Bổ sung — cảnh báo vận hành.** Transfer quét reward theo `date < EndAt` của kỳ chi
> (`pkg/admin/service/transfer.go:99`). Reward dời từ ngày tràn về ngày đích sẽ rơi vào kỳ chi khác — đúng ý
> đồ, nhưng kỳ thanh toán kế tiếp sẽ nhặt nó lên. Báo trước cho vận hành.

> **Bổ sung — `quantity.remaining` là số dẫn xuất**, tính bằng `Total - đếm reward chưa bị reject`
> (`event_schema.go:731-745`). Nhánh `Accumulate` giữ nguyên số dòng (dòng ngày tràn vẫn tồn tại, chỉ zero số)
> nên số suất không đổi. Đây là một lý do nữa để **zero chứ không xóa**.

### 3.6 Bước 6 — analytic cấp event và user

```go
users := distinct(plan.Items -> content.User)

for _, d := range []time.Time{mergeIntoDate, overflowDate} {   // ngày đích TRƯỚC, ngày tràn SAU
    q := &mgquery.CommonQuery{FromAt: d, SortInterface: bson.D{{"_id", 1}}}
    service.Event().UpdateAnalyticEventDaily(ctx, primitive.NilObjectID, event, q)
    for _, u := range users {
        service.Event().UpdateAnalyticUserEventDaily(ctx, u, event, q)
    }
}
```

Sau khi recompute **ngày nguồn**, đọc lại doc vừa upsert:

```go
doc := new(modelmg.EventAnalyticDailyRaw)
_ = EventAnalyticDailyDAO().GetShare().FindOne(ctx, doc, bson.M{"event": eventID, "date": overflowDate})

if doc.Statistic.TotalContent == 0 {
    // rỗng thật -> xóa cả event-analytic-daily và user-event-analytic-daily ngày nguồn
} else {
    // còn content thật mang date = ngày nguồn (content đăng sau endAt).
    // GIỮ doc lại, ghi hex id các content đó vào job.Report.ContentsOnOverflowDate.
    // Xóa đi là giấu một vấn đề khác dưới vỏ migration này.
}
```

Thứ tự bắt buộc: **bước 5 xong rồi mới tới bước 6** (hai hàm này aggregate từ `event-reward`, mà reward vừa
được chuyển ngày ở bước 5 — đảo lại thì cột ngày tràn vẫn còn tiền), và trong bước 6 thì **recompute trước,
xóa sau**.

> **Đính chính** — bản đầu giải thích thứ tự recompute-trước-xóa-sau là "đảo lại thì upsert sinh doc mới ngay
> sau khi xóa". Không đúng: các job recompute duyệt doc đang tồn tại, không duyệt dải ngày (xem 1.3). Lý do
> thật là chỉ sau khi recompute mới đọc được `TotalContent` để biết ngày tràn còn content thật hay đã rỗng.

## 4. Tầng HTTP

### 4.1 Router

`pkg/admin/router/migration.go` — thêm vào group `/migration` (đã gắn `RequiredLogin` + `CheckKeyMigration`):

```go
g.GET("/merge-overflow-day", h.MergeOverflowDay, v.MergeOverflowDayQuery)
```

`pkg/admin/router/router.go` (hoặc chỗ khai báo group admin) — **group mới**, chỉ `RequiredLogin`:

```go
func migrationJobs(e *echo.Group) {
    var (
        a = routeauth.Auth()
        g = e.Group("/migration-jobs", a.RequiredLogin)
        h = handler.Migration{}
        c = routevalidation.Common()
    )
    g.GET("", h.ListMigrationJobs)
    g.GET("/:id", h.GetMigrationJob, c.ParamID)
}
```

Lý do tách: `CheckKeyMigration` gắn ở cấp group `/migration` (`migration.go:14`) nên nếu để chung, mỗi lần poll đều phải kèm key.

### 4.2 Request và validation

`pkg/admin/model/request/migration.go` — struct mới (không nhét vào `MigrationQuery` vì `dryRun` phải bắt buộc có mặt định `true`):

```go
type MergeOverflowDayQuery struct {
    Event         string `query:"event"`
    OverflowDate  string `query:"overflowDate"`  // tùy chọn — rỗng thì suy từ event.endAt
    MergeIntoDate string `query:"mergeIntoDate"` // tùy chọn — rỗng thì = đầu ngày event.endAt
    DryRun        *bool  `query:"dryRun"`        // con trỏ: thiếu tham số => true
}

func (p MergeOverflowDayQuery) Validate() error {
    return validation.ValidateStruct(&p,
        validation.Field(&p.Event, validation.Required),
    )
}

func (p MergeOverflowDayQuery) IsDryRun() bool { return p.DryRun == nil || *p.DryRun }
```

> **Đính chính** — bản đầu đặt tên `fromAt`/`toAt` và bắt buộc cả hai. Hai chuyện phải sửa:
>
> **(a) `fromAt`/`toAt` trong repo này luôn nghĩa là "khoảng ngày".** `mgquery.CommonQuery` có
> `AssignFromToAtWithField(&cond, "date")` sinh `$gte`/`$lte`, và **mọi** endpoint trong nhóm `/migration`
> đều dùng `MigrationQuery` với đúng nghĩa đó. Đặt một cặp nguồn→đích ngay cạnh chúng là mời gõ
> `fromAt=31/07&toAt=01/08` theo phản xạ — tức chạy ngược chiều.
>
> **(b) Hai ngày suy ra được từ event** (guard đã ép `mergeIntoDate = startOfDay(endAt)` và `overflowDate =
> mergeIntoDate + 1`), nên để tùy chọn. Không truyền thì tự suy và set `params.datesDerived = true`; có truyền
> mà lệch thì **chặn**, in ra cặp hệ thống tự suy để đối chiếu.

`pkg/admin/router/routevalidation/migration.go` — thêm `MergeOverflowDayQuery` theo đúng khuôn của `MigrationQuery` hiện có (bind → validate → `c.Set(constants.KeyQuery, payload)`).

### 4.3 Handler

`pkg/admin/handler/migration.go`:

```go
func (h Migration) MergeOverflowDay(c echo.Context) error {
    var (
        cc = echocustom.EchoGetCustomCtx(c)
        p  = cc.Get(constants.KeyQuery).(request.MergeOverflowDayQuery)
        s  = service.Migration{}
    )

    eventID, err := primitive.ObjectIDFromHex(p.Event)
    if err != nil {
        return cc.Response400(nil, "event id invalid")
    }

    // Suy hai ngày từ event.endAt; tham số truyền vào (nếu có) chỉ để xác nhận.
    event := new(modelmg.EventRaw)
    _ = daomongodb.EventDAO().GetShare().FindById(c.Request().Context(), event, eventID)
    if event.ID.IsZero() {
        return cc.Response400(nil, "event not found")
    }
    mergeIntoDate := util.TimeStartOfDayInHCM(event.EndAt)
    overflowDate  := mergeIntoDate.AddDate(0, 0, 1)
    datesDerived  := true
    if p.MergeIntoDate != "" || p.OverflowDate != "" {
        datesDerived = false
        if p.MergeIntoDate != "" && !util.TimeStartOfDayInHCM(util.TimeParseISODate(p.MergeIntoDate)).Equal(mergeIntoDate) {
            return cc.Response400(echo.Map{"mergeIntoDate": mergeIntoDate}, "mergeIntoDate lệch với endAt của event")
        }
        if p.OverflowDate != "" && !util.TimeStartOfDayInHCM(util.TimeParseISODate(p.OverflowDate)).Equal(overflowDate) {
            return cc.Response400(echo.Map{"overflowDate": overflowDate}, "overflowDate không phải ngày liền sau endAt")
        }
    }

    // chống chạy song song
    running := daomongodb.MigrationJobDAO().GetShare().CountByCondition(c.Request().Context(),
        new(modelmg.MigrationJobRaw), bson.M{
            "type":         modelmg.MigrationJobTypeMergeOverflowDay,
            "status":       modelmg.MigrationJobStatusRunning,
            "params.event": p.Event,
        })
    if running > 0 {
        return cc.Response400(nil, "a merge-overflow-day job is already running for this event")
    }

    job := newMergeOverflowDayJob(context.Background(), p, cc.GetCurrentUserID().Hex(), datesDerived)
    go s.MergeOverflowDay(context.Background(), job, eventID, overflowDate, mergeIntoDate, p.IsDryRun())

    return cc.Response200(echo.Map{"jobId": job.ID.Hex(), "params": job.Params}, "")
}
```

> **Đính chính** — `cc.GetCurrentUserID()` trả `primitive.ObjectID` (`internal/echo/echo.go:151`) còn
> `MigrationJobRaw.StartedBy` là `string`: phải `.Hex()`. Và `ctxBg` trong bản đầu không được khai báo ở đâu.

`ListMigrationJobs` / `GetMigrationJob` port nguyên từ ambassador (`pkg/admin/service/migration_job.go`), `GetMigrationJob` trả `(nil, nil)` khi không tồn tại để handler phân biệt 404 với lỗi DB.

> Chuẩn hóa ngày bằng `util.TimeStartOfDayInHCM` là **bắt buộc**. Mọi `date` trong hệ thống là đầu ngày giờ HCM; lệch một giờ là không match doc nào.

> **Đính chính** — key migration đi ở **header `Api-Key`**, không phải query string. `CheckKeyMigration`
> (`pkg/admin/router/routeauth/auth.go:38-49`):
>
> ```go
> apiKey = cc.GetHeaderKey("Api-Key")
> if apiKey != config.GetENV().KeyMigration {
>     return cc.Response401(nil, locale.CommonKeyNoPermission)
> }
> ```
>
> Mục 7 của bản đầu hướng dẫn gọi kèm `&key=<migration-key>` trên URL — làm theo sẽ ăn 401.

## 5. Test

`pkg/admin/service/merge_overflow_day_planner_test.go` và `merge_overflow_day_guard_test.go` — table-driven, không dựng mongo, theo phong cách các test thuần sẵn có trong `pkg/admin/service`.

**Planner:**

| Case | Kỳ vọng |
|---|---|
| Content có doc cả hai ngày | `value = v_to + v_from`, `begin` giữ nguyên, `end = begin + value` |
| Content chỉ có ở ngày nguồn | doc mới, `begin = PrevEnds[content].End`, `ToDocID` zero |
| Content chỉ có ở ngày đích | không xuất hiện trong `Items` |
| `totalManualView` hai ngày | **cộng dồn**, không lấy của một ngày |
| `like` / `comment` | cùng quy tắc với `view` |
| Bất biến tổng | `TotalViewAfter == TotalViewBefore` |
| Không trùng lặp | mỗi content xuất hiện đúng một lần trong `Items` |

**Guard:** mỗi điều kiện trong bảng 3.2 một case, cộng một case hợp lệ trả slice rỗng, cộng một case nhiều lý
do cùng lúc để khẳng định không return sớm. Thêm **một case khóa chỗ hiểu sai của bản đầu**: reward ngày tràn ở
`status = completed` mà `isTransfer = false` và không có `transferId` thì **không** bị chặn.

**RewardPlanner** (`merge_overflow_day_reward_planner_test.go`) — module mới ở 3.5:

| Case | Kỳ vọng |
|---|---|
| by-statistic, có dòng ngày đích cùng `schema._id` và cùng `status` | `Accumulate`, `AddCash` đúng bằng cash dòng ngày tràn |
| by-statistic, khác `schema._id` | `MoveDate` |
| by-statistic, cùng `schema._id` nhưng khác `status` | `MoveDate` |
| `by-view-milestone` / `by-content-milestone` | luôn `MoveDate` |
| Bất kỳ case nào | **không bao giờ** sinh hành động xóa |
| Bất biến tiền | tổng cash sau khi áp mọi hành động **bằng** tổng cash trước |

Bất biến tiền là assertion phải **phá được code mới thấy đỏ**: sửa `AddCash` thành `AddCash * 2` hoặc bỏ bước
zero dòng ngày tràn thì test phải đỏ đúng con số, không phải chỉ đỏ chung chung.

**Không viết test cho** Executor / Handler / Router / MigrationJob helper — kiểm chứng bằng dry-run trên production.

## 6. Checklist triển khai

**Chặn:** hai số liệu production ở mục "Chặn code" của [PRD](./PRD.md) phải có trước khi làm phần reward.

- [ ] `collection.go`: thêm `CollectionMigrationJob`, `CollectionContentAnalyticDailyBackup`, `CollectionEventRewardBackup`
- [ ] `index.go`: `{type:1, startedAt:-1}`, `{jobId:1}` (hai collection backup), và **`{event:1, date:1}` cho `content-analytic-daily`**
- [ ] `model/mg/migration_job.go` (port + `aborted` + params đổi tên ngày + `report` + `skippedSamples` + chữ ký `newMigrationJob`)
- [ ] `model/mg/content_analytic_daily_backup.go`, `model/mg/event_reward_backup.go`
- [ ] `model/mg/event_reward.go`: thêm 4 field truy vết (`mergedIntoRewardId`, `mergedFromRewardIds`, `originalDate`, `migrationJobId`)
- [ ] `dao/migration_jobs.go`, `dao/content_analytic_daily_backup.go`, `dao/event_reward_backup.go`
- [ ] `service/migration_job.go` (port helper từ ambassador, nhớ `.Hex()` cho `StartedBy`)
- [ ] `service/merge_overflow_day_planner.go` + test
- [ ] `service/merge_overflow_day_guard.go` + test (gồm case `completed` mà chưa `isTransfer` thì KHÔNG chặn)
- [ ] `service/merge_overflow_day_reward_planner.go` + test (gồm bất biến tổng cash)
- [ ] `service/merge_overflow_day.go` (Executor)
- [ ] `model/request/migration.go`: `MergeOverflowDayQuery` với `overflowDate` / `mergeIntoDate` tùy chọn
- [ ] `routevalidation/migration.go`: middleware tương ứng
- [ ] `handler/migration.go`: `MergeOverflowDay`, `ListMigrationJobs`, `GetMigrationJob`
- [ ] `router/migration.go` + group `/migration-jobs`
- [ ] `go build ./...` sạch, `go test ./pkg/admin/service/...` xanh
- [ ] Xóa binary vừa build

## 7. Quy trình chạy trên production

1. Chạy trước hai truy vấn ở mục "Chặn code" của [PRD](./PRD.md). Có `isTransfer = true` ở ngày tràn thì
   **dừng ở đây**, không chạy migration.
2. Trigger — key đi ở **header**, hai ngày để trống cho hệ thống tự suy:

   ```
   curl -H "Api-Key: <migration-key>" -H "Authorization: Bearer <token>" \
        "https://<host>/migration/merge-overflow-day?event=<eventId>"
   ```

   → nhận `jobId`. Muốn gõ ngày để xác nhận thì thêm `&overflowDate=2026-08-01&mergeIntoDate=2026-07-31`;
   lệch với `endAt` là bị chặn ngay ở tầng handler, chưa sinh job.
3. `GET /migration-jobs/<jobId>` → đọc `report`. Nhìn theo thứ tự: **tổng cash trước/sau có bằng nhau không**,
   rồi `reward đã chi` phải bằng 0, rồi mới tới `totalViewBefore/After` đối chiếu dashboard và vài content mẫu.
   Định dạng khối báo cáo xem mục API contract của PRD.
4. Nếu `status = aborted` → đọc `report.abortReasons`, xử lý rồi chạy lại. Không ép chạy.
5. Số liệu khớp → gọi lại với `&dryRun=false`.
6. Poll `progress.current/total` tới khi `status = done`.
7. Kiểm tra `report.contentsOnOverflowDate` — nếu không rỗng, còn content đăng sau `endAt`, xử lý riêng.
8. Xác nhận: báo cáo event không còn cột ngày ngoài `startAt`–`endAt`; `Audit()` không đánh `VIEW_INVALID` mới;
   và **tổng tiền của event không đổi** so với trước khi chạy.
9. Bịt nguồn sinh dữ liệu sai (xem Problem Statement của PRD). Không bịt thì lần crawl chỉ định tiếp theo
   trên chính event này sẽ tạo lại đúng sự cố vừa dọn.

**Ràng buộc thời điểm:** hướng gộp từ `content-analytic-daily` không phụ thuộc `content-flow` nên chạy muộn **không sai số**. Nhưng nếu flow ngày đích đã bị dọn (quá 30 ngày), bước 4 rơi vào nhánh B — doc bị đánh `completed` thay vì `valid`. Chạy sớm thì sạch hơn.

## 8. Rủi ro đã biết

| Rủi ro | Xử lý |
|---|---|
| Job `running` treo do process restart | Không tự dọn; sửa tay trong `migration-jobs`, nếu không sẽ chặn lần trigger sau |
| `Audit()` vs `TotalManualView` lệch sẵn (`Audit` so `TotalView == View.Value`, `Update` ghi `TotalView + TotalManualView`) | Lỗi có sẵn của hệ thống, không do migration. Không dùng làm tiêu chí nghiệm thu cho content có manual view |
| Job chết giữa chừng để lại trạng thái nửa vời | Backup gắn `jobId` nên không mất đường lùi; đọc job để biết dừng ở đâu trước khi chạy lại |
| Content đăng sau `endAt` | Báo cáo qua `report.contentsOnOverflowDate`, không tự sửa `content.date` |
| **Nguồn sinh dữ liệu sai vẫn mở** | Ngoài phạm vi. Nếu là nhánh crawl chỉ định eventId (bỏ qua `endAt`) thì sự cố lặp lại **ngay trên event vừa sửa**, không phải "event sau". Xem hai ứng viên nguyên nhân ở PRD |
| **Reward rơi vào kỳ chi khác sau khi đổi ngày** | Có chủ đích. Transfer quét theo `date < EndAt` của kỳ (`transfer.go:99`) nên kỳ kế tiếp sẽ nhặt lên. Báo trước cho vận hành |
| **Biên bản đối soát cũ trỏ vào ngày tràn** | Bốn field truy vết trên `event-reward` (`mergedIntoRewardId`, `mergedFromRewardIds`, `originalDate`, `migrationJobId`) cho phép lần ngược |
| **Nhánh đổi ngày làm reward rơi sang schema khác đơn giá** | Không xảy ra: nhánh đổi ngày giữ nguyên dòng và nguyên `schema`. Nhưng cash theo từng schema vẫn phải in trong report để nhìn ra nếu có |
| **`quantity.remaining` lệch sau khi chạy** | Nó là số dẫn xuất, đếm số dòng reward chưa reject (`event_schema.go:731-745`). Nhánh cộng dồn giữ nguyên số dòng nên không lệch — đây là lý do **zero chứ không xóa** |
