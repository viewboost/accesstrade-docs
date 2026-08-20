# Tech Spec — Merge Overflow Day

> Tài liệu kỹ thuật đi kèm [PRD Merge Overflow Day](./merge-overflow-day-event-analytic.md).
> PRD trả lời **làm gì và vì sao**; file này trả lời **viết ở đâu, gọi hàm nào, ghi field gì**.
> Mọi tên hàm/field dưới đây đã đối chiếu với source thật trong `vcreator/backend`.

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
| `UpdateAnalyticEventDaily` | `internal/service/event.go:283` | `content` + `event-reward`, match `date = q.FromAt` |
| `UpdateAnalyticUserEventDaily` | `internal/service/event.go:40` | `content` + `event-reward`, match `date = q.FromAt` |

→ Gộp thẳng vào `content-analytic-daily` là đủ để toàn bộ chuỗi phía sau ra số đúng.

### 1.3 Hai cạm bẫy đã xác minh

**`ContentFlowRaw` không có `month` / `year`.** `internal/model/mg/content_flow.go` chỉ có `Date time.Time`. Hai field đó thuộc `ContentAnalyticDailyRaw`. Khi dịch flow chỉ update `date`.

**`UpdateAnalyticUserEventDaily` ghi bằng upsert** (`internal/service/event.go:258`, `options.Update().SetUpsert(true)`), match theo `content.date` — mà `content.date` là ngày đăng bài, migration không đụng tới. Xóa mù doc analytic ngày nguồn sẽ bị upsert lại ở lần recompute sau.

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

### 2.2 Model mới

**`internal/model/mg/migration_job.go`** — port từ ambassador, ba khác biệt đã chốt ở PRD:

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
    DryRun bool   `bson:"dryRun"  json:"dryRun"`
    Event  string `bson:"event"   json:"event"`   // event._id hex
    FromAt string `bson:"fromAt"  json:"fromAt"`  // ISO date, ngày nguồn
    ToAt   string `bson:"toAt"    json:"toAt"`    // ISO date, ngày đích
}

type MigrationJobReport struct {                 // KHÁC BẢN GỐC — field mới
    AbortReasons     []string                  `bson:"abortReasons,omitempty"     json:"abortReasons,omitempty"`
    DocsAffected     map[string]int            `bson:"docsAffected"               json:"docsAffected"`      // collection -> số doc
    TotalViewBefore  float64                   `bson:"totalViewBefore"            json:"totalViewBefore"`
    TotalViewAfter   float64                   `bson:"totalViewAfter"             json:"totalViewAfter"`
    TotalCashBefore  float64                   `bson:"totalCashBefore"            json:"totalCashBefore"`
    TotalCashAfter   float64                   `bson:"totalCashAfter"             json:"totalCashAfter"`
    Contents         []MigrationJobContentItem `bson:"contents"                   json:"contents"`
    ContentsOnFromAt []string                  `bson:"contentsOnFromAt,omitempty" json:"contentsOnFromAt,omitempty"` // content.date = ngày nguồn, chặn xóa doc
}

type MigrationJobContentItem struct {
    Content    string  `bson:"content"    json:"content"`
    ViewBefore float64 `bson:"viewBefore" json:"viewBefore"`
    ViewAfter  float64 `bson:"viewAfter"  json:"viewAfter"`
}
```

Phần còn lại (`MigrationJobRaw`, `MigrationJobSample`, `MigrationJobProgress`, `MigrationJobStats`, `DbModelName()`) giữ nguyên như bản gốc, thêm field `Report *MigrationJobReport`.

**`internal/model/mg/content_analytic_daily_backup.go`** — copy `ContentAnalyticDailyRaw`, thêm `JobID AppID` và `BackupAt time.Time`, `DbModelName()` trả `CollectionContentAnalyticDailyBackup`.

### 2.3 DAO mới

`internal/module/database/mongodb/dao/migration_jobs.go` và `.../content_analytic_daily_backup.go` — copy nguyên pattern của `dao/content_flow_backup.go` (struct rỗng + `GetShare()` trả `GetDBShare()`).

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
    Event            *modelmg.EventRaw
    FromDate         time.Time
    ToDate           time.Time
    FromDocCount     int    // số content-analytic-daily ở ngày nguồn
    AfterFromCount   int    // số content-analytic-daily ở ngày SAU ngày nguồn
    PaidRewardOnFrom int    // event-reward ngày nguồn có isTransfer hoặc status completed
}

func CheckMergeOverflowDay(in GuardInput) []string   // rỗng = cho chạy
```

| # | Điều kiện | Lý do trả về |
|---|---|---|
| 1 | `Event.IsExtendedPeriod()` | `EXTENDED_PERIOD_ENABLED` |
| 2 | `!ToDate.Equal(startOfDay(Event.EndAt))` | `TO_DATE_NOT_EVENT_END_AT` |
| 3 | `!FromDate.Equal(ToDate.AddDate(0,0,1))` | `FROM_DATE_NOT_ADJACENT` |
| 4 | `AfterFromCount > 0` | `OVERFLOW_MORE_THAN_ONE_DAY` |
| 5 | `PaidRewardOnFrom > 0` | `REWARD_ALREADY_PAID_ON_FROM_DATE` |
| 6 | `FromDocCount == 0` | `NOTHING_TO_MERGE` |

Trả **toàn bộ** lý do khớp, không return sớm ở lý do đầu tiên — vận hành cần thấy hết trong một lần dry-run.

### 3.3 `merge_overflow_day.go` — Executor, chỉ điều phối I/O

```go
func (m migrationImpl) MergeOverflowDay(
    ctx context.Context,
    job *modelmg.MigrationJobRaw,
    eventID modelmg.AppID,
    fromDate, toDate time.Time,
    dryRun bool,
)
```

Chạy trong goroutine, mở đầu bằng `defer m.finishMigrationJob(ctx, job, "[MIGRATION][MERGE-OVERFLOW-DAY]")`.

**Giai đoạn 0 — nạp và kiểm tra**

1. `EventDAO().FindById` → `EventRaw`. Không tìm thấy → abort `EVENT_NOT_FOUND`.
2. Đếm ba con số cho guard bằng `CountByCondition` trên `content-analytic-daily` / `event-reward`.
3. `CheckMergeOverflowDay(...)`. Có lý do → `job.Status = aborted`, `job.Report.AbortReasons = reasons`, return.
4. `Find` doc `content-analytic-daily` của hai ngày (`event` + `date`, `isExtended: {$ne: true}`).
5. Với content chỉ có ở ngày nguồn: `FindOne` doc gần nhất `date < toDate` cùng content, sort `date: -1` → `PrevEnds`.
6. `BuildMergePlan(...)` → set `job.Progress.Total = len(plan.Items)`, `saveMigrationJob`.
7. Dựng `job.Report` (số doc theo collection, tổng view/cash trước–sau, danh sách content).
8. `dryRun == true` → `saveMigrationJob`, return. **Không ghi gì.**

**Giai đoạn 1 — ghi (chỉ khi `dryRun == false`)**

| Bước | Thao tác | Ghi chú |
|---|---|---|
| 1 | Backup `content-analytic-daily` **cả hai ngày** + `content-flow` ngày nguồn, gắn `jobId` | `InsertMany` vào hai collection backup |
| 2 | Ghi doc ngày đích theo `plan.Items` | `BulkWrite`: `UpdateOne` nếu `ToDocID` khác zero, `InsertOne` nếu zero |
| 3 | Xóa doc `content-analytic-daily` ngày nguồn | `DeleteMany` theo `event` + `date` |
| 4 | Xử lý `content-flow` cho `Audit()` | xem 3.4 |
| 5 | Tính lại reward ngày đích | vòng lặp từng content, xem 3.5 |
| 6 | Recompute analytic cấp event/user **hai ngày** | xem 3.6 |

Sau mỗi content ở bước 5: `job.Progress.Current++`, flush mỗi `jobFlushEvery` (25) record. Lỗi một content → `recordFailedSample` + `job.Stats.Failed++`, **không** dừng cả job.

### 3.4 Bước 4 — `content-flow`

```go
flowOnTo := ContentFlowDAO().CountByCondition(ctx, ..., bson.M{"event": eventID, "date": toDate})
if flowOnTo > 0 {
    // Nhánh A — dịch date, Audit() sẽ khớp
    ContentFlowDAO().GetShare().UpdateMany(ctx, ...,
        bson.M{"event": eventID, "date": fromDate},
        bson.M{"$set": bson.M{"date": toDate, "updatedAt": time.Now()}},
    )
    // KHÔNG set month/year — ContentFlowRaw không có hai field này
} else {
    // Nhánh B — flow ngày đích đã bị DeleteContentFlow() dọn.
    // Backup + xóa flow ngày nguồn để nó không tái sinh doc ngày nguồn,
    // rồi đánh doc ngày đích completed để Audit() bỏ qua —
    // đúng quy ước của DeleteContentFlow (doc không còn flow => completed).
    ContentAnalyticDailyDAO().GetShare().UpdateMany(ctx, ...,
        bson.M{"event": eventID, "date": toDate},
        bson.M{"$set": bson.M{"auditStatus": constants.StatusCompleted}},
    )
}
```

### 3.5 Bước 5 — reward

Với mỗi `item` trong `plan.Items`:

```go
content := new(modelmg.ContentRaw)
_ = ContentDAO().GetShare().FindById(ctx, content, item.Content)

doc := new(modelmg.ContentAnalyticDailyRaw)
_ = ContentAnalyticDailyDAO().GetShare().FindOne(ctx, doc, bson.M{
    "content": item.Content, "date": toDate, "isExtended": bson.M{"$ne": true},
})

service.EventSchema().UpdateRewardTypeByStatisticContent(ctx, content, doc)
```

Hàm này tự kéo theo `UpdateStatisticUserEvent`, `Content().UpdateCashStatistic`, `User().UpdateStatistic` (`event_schema.go:317-324`) → **không cần bước `user-event` riêng**.

Hành vi cần biết: `rewardCond` khớp cả `status` (`event_schema.go:291`). Reward ngày đích đã `completed` sẽ không được update mà **insert reward mới cho phần chênh** — `GetStatisticContentIsRewardInDay` đã trừ phần completed nên không đúp số. Đúng thiết kế, không phải lỗi.

### 3.6 Bước 6 — analytic cấp event và user

```go
users := distinct(plan.Items -> content.User)

for _, d := range []time.Time{toDate, fromDate} {   // ngày đích TRƯỚC, ngày nguồn SAU
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
_ = EventAnalyticDailyDAO().GetShare().FindOne(ctx, doc, bson.M{"event": eventID, "date": fromDate})

if doc.Statistic.TotalContent == 0 {
    // rỗng thật -> xóa cả event-analytic-daily và user-event-analytic-daily ngày nguồn
} else {
    // còn content thật mang date = ngày nguồn (content đăng sau endAt).
    // GIỮ doc lại, ghi hex id các content đó vào job.Report.ContentsOnFromAt.
    // Xóa đi là giấu một vấn đề khác dưới vỏ migration này.
}
```

Thứ tự bắt buộc: recompute **trước**, xóa **sau**. Đảo lại thì upsert sinh doc mới ngay sau khi xóa.

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
    Event    string `query:"event"`
    FromAt   string `query:"fromAt"`
    ToAt     string `query:"toAt"`
    DryRun   *bool  `query:"dryRun"`   // con trỏ: thiếu tham số => true
}

func (p MergeOverflowDayQuery) Validate() error {
    return validation.ValidateStruct(&p,
        validation.Field(&p.Event, validation.Required),
        validation.Field(&p.FromAt, validation.Required),
        validation.Field(&p.ToAt, validation.Required),
    )
}

func (p MergeOverflowDayQuery) IsDryRun() bool { return p.DryRun == nil || *p.DryRun }
```

`pkg/admin/router/routevalidation/migration.go` — thêm `MergeOverflowDayQuery` theo đúng khuôn của `MigrationQuery` hiện có (bind → validate → `c.Set(constants.KeyQuery, payload)`).

### 4.3 Handler

`pkg/admin/handler/migration.go`:

```go
func (h Migration) MergeOverflowDay(c echo.Context) error {
    var (
        cc       = echocustom.EchoGetCustomCtx(c)
        p        = cc.Get(constants.KeyQuery).(request.MergeOverflowDayQuery)
        s        = service.Migration{}
        fromDate = util.TimeStartOfDayInHCM(util.TimeParseISODate(p.FromAt))
        toDate   = util.TimeStartOfDayInHCM(util.TimeParseISODate(p.ToAt))
    )

    eventID, err := primitive.ObjectIDFromHex(p.Event)
    if err != nil {
        return cc.Response400(nil, "event id invalid")
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

    job := newMergeOverflowDayJob(ctxBg, p, cc.GetCurrentUserID())
    go s.MergeOverflowDay(context.Background(), job, eventID, fromDate, toDate, p.IsDryRun())

    return cc.Response200(echo.Map{"jobId": job.ID.Hex(), "params": job.Params}, "")
}
```

`ListMigrationJobs` / `GetMigrationJob` port nguyên từ ambassador (`pkg/admin/service/migration_job.go`), `GetMigrationJob` trả `(nil, nil)` khi không tồn tại để handler phân biệt 404 với lỗi DB.

> Chuẩn hóa ngày bằng `util.TimeStartOfDayInHCM` là **bắt buộc**. Mọi `date` trong hệ thống là đầu ngày giờ HCM; lệch một giờ là không match doc nào.

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

**Guard:** mỗi điều kiện trong bảng 3.2 một case, cộng một case hợp lệ trả slice rỗng, cộng một case nhiều lý do cùng lúc để khẳng định không return sớm.

**Không viết test cho** Executor / Handler / Router / MigrationJob helper — kiểm chứng bằng dry-run trên production.

## 6. Checklist triển khai

- [ ] `collection.go`: thêm `CollectionMigrationJob`, `CollectionContentAnalyticDailyBackup`
- [ ] `index.go`: index `{type:1, startedAt:-1}` và `{jobId:1}`
- [ ] `model/mg/migration_job.go` (port + `aborted` + params gọn + `report`)
- [ ] `model/mg/content_analytic_daily_backup.go`
- [ ] `dao/migration_jobs.go`, `dao/content_analytic_daily_backup.go`
- [ ] `service/migration_job.go` (port helper từ ambassador)
- [ ] `service/merge_overflow_day_planner.go` + test
- [ ] `service/merge_overflow_day_guard.go` + test
- [ ] `service/merge_overflow_day.go` (Executor)
- [ ] `model/request/migration.go`: `MergeOverflowDayQuery`
- [ ] `routevalidation/migration.go`: middleware tương ứng
- [ ] `handler/migration.go`: `MergeOverflowDay`, `ListMigrationJobs`, `GetMigrationJob`
- [ ] `router/migration.go` + group `/migration-jobs`
- [ ] `go build ./...` sạch, `go test ./pkg/admin/service/...` xanh
- [ ] Xóa binary vừa build

## 7. Quy trình chạy trên production

1. `GET /migration/merge-overflow-day?event=<id>&fromAt=2026-08-01&toAt=2026-07-31&key=<migration-key>` → nhận `jobId`.
2. `GET /migration-jobs/<jobId>` → đọc `report`. Đối chiếu `totalViewBefore/After` với dashboard, kiểm tra vài content mẫu.
3. Nếu `status = aborted` → đọc `report.abortReasons`, xử lý rồi chạy lại. Không ép chạy.
4. Số liệu khớp → gọi lại với `&dryRun=false`.
5. Poll `progress.current/total` tới khi `status = done`.
6. Kiểm tra `report.contentsOnFromAt` — nếu không rỗng, còn content đăng sau `endAt`, xử lý riêng.
7. Xác nhận báo cáo event không còn cột ngày ngoài `startAt`–`endAt`, và `Audit()` không đánh `VIEW_INVALID` mới.

**Ràng buộc thời điểm:** hướng gộp từ `content-analytic-daily` không phụ thuộc `content-flow` nên chạy muộn **không sai số**. Nhưng nếu flow ngày đích đã bị dọn (quá 30 ngày), bước 4 rơi vào nhánh B — doc bị đánh `completed` thay vì `valid`. Chạy sớm thì sạch hơn.

## 8. Rủi ro đã biết

| Rủi ro | Xử lý |
|---|---|
| Job `running` treo do process restart | Không tự dọn; sửa tay trong `migration-jobs`, nếu không sẽ chặn lần trigger sau |
| `Audit()` vs `TotalManualView` lệch sẵn (`Audit` so `TotalView == View.Value`, `Update` ghi `TotalView + TotalManualView`) | Lỗi có sẵn của hệ thống, không do migration. Không dùng làm tiêu chí nghiệm thu cho content có manual view |
| Job chết giữa chừng để lại trạng thái nửa vời | Backup gắn `jobId` nên không mất đường lùi; đọc job để biết dừng ở đâu trước khi chạy lại |
| Content đăng sau `endAt` | Báo cáo qua `report.contentsOnFromAt`, không tự sửa `content.date` |
| Crawler vẫn ghi tiếp sau `endAt` | Ngoài phạm vi — không xử lý thì sự cố lặp lại ở event sau |
