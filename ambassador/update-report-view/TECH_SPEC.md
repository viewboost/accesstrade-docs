# Tách view được tính thưởng và view vượt ngân sách

Ngày: 2026-08-05

## Vấn đề

Ở kỳ đối soát, cột view không khớp cột tiền. Nguyên nhân là các content thuộc event đã vượt ngân sách: view vẫn được ghi nhận nhưng không sinh ra tiền thưởng.

Triệu chứng tương tự xuất hiện ở nhiều màn khác. Tài liệu này xử lý ba chỗ.

## Nguyên nhân gốc

Khi event vượt ngân sách, `processRewardForSchema` (`backend/internal/service/event_schema.go:190`) tách một ngày-content-schema thành hai document trong `event_reward`:

- **primary** — phần được trả tiền, `cash > 0`, `isBudgetExceeded = false`
- **overflow** — phần vượt ngân sách, `cash = 0`, `isBudgetExceeded = true`, nhưng `statistic.totalView/totalLike/totalComment > 0`

`splitStatistic` (`event_schema.go:464`) giữ bất biến `TotalView × CashPerView = TotalCashView` trên từng document, nên ở tầng dữ liệu hai loại view đã tách sạch.

Vấn đề ở tầng đọc: **không một aggregate nào trên `event_reward` lọc `isBudgetExceeded`**. Cờ này chỉ dùng ở đường ghi, trong `findRewardPair` (`event_schema.go:68`, điều kiện ở `:83` và `:89`).

Hai document mang cùng `status`, `date`, `options.contentId`, `options.source`, `schema._id`. Hệ quả:

- mọi tổng **tiền** đều đúng (cộng thêm 0)
- mọi tổng **view / like / comment** đều phồng
- mọi `$sum: 1` đếm document phồng gấp đôi với content bị tách

## Bẫy đặt tên cần biết trước khi đọc tiếp

`event_reward.status` có 4 giá trị, nhưng tên field Go lệch một nấc. Chú thích gốc ở `aggregate_pipeline/event_reward.go:132-136` xác nhận:

| Tên field trong code | `event_reward.status` | Nghĩa nghiệp vụ |
|---|---|---|
| `...Pending` | `waiting_approved` | content chưa duyệt |
| `...Completed` | `pending` | đã duyệt, chờ đối soát |
| `...Cashback` | `completed` | đã đối soát, tiền đã chi |
| `...Rejected` | `rejected` | bị từ chối |
| `...Transferred` | `isTransfer = true` | đã chuyển khoản |

Nhãn hiển thị trên UI thì đúng. Chỉ tên biến trong code là lệch.

## Phạm vi

| # | Màn hình | Pipeline nguồn | Đường dữ liệu |
|---|---|---|---|
| 1 | Menu thống kê admin | `GetStatisticRewardReport` | `event_analytic_daily` → `GET /events/statistic` |
| 2 | Reconciliation item | `GetTotalCashRewardByContent` | `reconciliation_item.content.*` |
| 3 | Trang cá nhân web user | `GetStatisticContentBySource` | `user_event.statistic.<source>` → `GET /events/by-slug` |

Sửa #2 kéo theo hai chỗ tự đúng: `cash_flow.Options.TotalView` và `NotificationOpts.TotalView` (`reconciliation_running.go:347`, `:387`) lấy thẳng từ item. Câu thông báo "Thưởng %d view ngày %s" (`internal/locale/cash_flow.go:56`) hiện ghép số view phồng với số tiền đúng, gửi cho ambassador qua ví và push notification.

Sửa #1 kéo theo 2 export event-analytic, vì cùng dùng chung pipeline đọc.

### Ngoài phạm vi

- `export_user_partner.go:209-213` — 5 cột view phồng cạnh cột cash đúng
- `admin/src/pages/dashboard/index.tsx:100` — "Tổng lượt xem" cạnh "Tổng tiền chờ/đã đối soát"
- `frontend/src/pages/statistic/components/tab-dashboard.tsx:62-88` và `tab-invitee.tsx:162-196`
- like và comment cũng phồng — ảnh hưởng `event_analytic_daily.statistic.{like,comment}.*`
- `aggregate_pipeline/event_reward.go:44` `totalReward: {$sum: 1}` đếm gấp đôi, chưa consumer nào đọc

### Vùng cấm

`GetEventRewardStatisticAllByContentIDs` (`aggregate_pipeline/event_reward.go:561`) → `GetStatisticContentIsRewardInDay` (`internal/service/content.go:588`) → `event_schema.go:767-770`:

```go
totalView := doc.View.Value - view.Completed
```

Đây là phép trừ chống trả thưởng trùng. Lọc `isBudgetExceeded` ở đây sẽ khiến hệ thống tưởng view vượt ngân sách chưa được xử lý và tính thưởng lại, ghi đè lên document primary đã `completed`. **Không sửa.**

## Nguyên tắc thiết kế

**Không đổi ngữ nghĩa bất kỳ field nào đang có.** Thêm field mới song song. Dữ liệu lịch sử không bị diễn giải sai, kỳ đối soát đã chốt vẫn đọc đúng như lúc chốt, không cần backfill để số cũ đúng.

**Field mới mang kiểu `CommonStatisticContent`**, không phải một số vô hướng. Nhờ vậy nó tự có breakdown theo từng status, và mỗi nơi trừ đúng bucket mình cần. Một con số vô hướng không mô tả nổi hai chiều status × vượt-ngân-sách.

**Pipeline chỉ cung cấp, không tự trừ. API quyết định.** View đứng cạnh tiền thì trừ; view đứng một mình như chỉ số hiệu suất thì để nguyên. Pipeline trả song song hai bộ số, mỗi consumer tự chọn.

Bất biến xuyên suốt, đúng cho từng bucket:

```
View.<bucket>  ==  (phần được tính thưởng)  +  ViewExceedBudget.<bucket>
```

## Thay đổi model

### `EventAnalyticDailyStatistic` — phục vụ #1

`backend/internal/model/mg/event_analytic_daily.go:28`. `UserEventAnalyticDailyRaw.Statistic` dùng **đúng cùng type** (`user_event_analytic_daily.go:24`), nên một field phủ cả hai collection.

```go
type EventAnalyticDailyStatistic struct {
    Cash             EventAnalyticCash      `json:"cash" bson:"cash"`
    View             CommonStatisticContent `json:"view" bson:"view"`
    // ViewExceedBudget: phần view KHÔNG sinh tiền thưởng vì event vượt ngân sách.
    // Là TẬP CON của View, cùng quy ước bucket với View.
    // Nguồn: event_reward, các doc có isBudgetExceeded = true.
    ViewExceedBudget CommonStatisticContent `json:"viewExceedBudget" bson:"viewExceedBudget"`
    Comment          CommonStatisticContent `json:"comment" bson:"comment"`
    Like             CommonStatisticContent `json:"like" bson:"like"`
    // ... các field còn lại giữ nguyên
}
```

Quy ước bucket của `ViewExceedBudget`, giống hệt `View` trong cùng struct:

| Slot | `event_reward.status` |
|---|---|
| `Total` | mọi status |
| `Pending` | `waiting_approved` |
| `Completed` | `pending` |
| `Cashback` | `completed` |
| `Rejected` | `rejected` |
| `Transfer` | `isTransfer = true` |

### `UserContentStatistic` — phục vụ #3

`backend/internal/model/mg/user_event.go:164`. **Đây là struct dùng chung**, không chỉ của `user_event`: `ContentRaw.Statistic` cũng dùng nó (`internal/model/mg/content.go:32`), và nó được phơi ra ở 5 response:

| Nơi | Ý nghĩa |
|---|---|
| `pkg/public/model/response/event.go:57` | `GET /events` (danh sách) |
| `pkg/public/model/response/event.go:94` | `GET /events/by-slug` |
| `pkg/public/model/response/event.go:119` | `UserEventResponse` |
| `pkg/public/model/response/content.go:24` | statistic của **content** |
| `pkg/admin/model/response/content.go:15` | statistic của content, phía admin |

Chỉ thêm dữ liệu **thô** vào đây, kiểu giá trị thường cho đồng bộ với các field còn lại:

```go
type UserContentStatistic struct {
    Point            CommonStatisticContent `json:"point" bson:"point"`
    View             CommonStatisticContent `json:"view" bson:"view"`
    // ViewExceedBudget: toàn bộ đến từ event_reward, quy ước bucket như bảng trên.
    // Chỉ được ghi cho user_event; với content luôn là zero.
    // CẢNH BÁO: khác với View trong cùng struct — View trộn hai nguồn, xem mục #3.
    ViewExceedBudget CommonStatisticContent `json:"viewExceedBudget" bson:"viewExceedBudget"`
    Like             CommonStatisticContent `json:"like" bson:"like"`
    Comment          CommonStatisticContent `json:"comment" bson:"comment"`
    Cash             CommonStatisticContent `json:"cash" bson:"cash"`
}
```

Hai hệ quả của kiểu giá trị, cả hai đều chấp nhận được:

- Field xuất hiện ở hai response content dưới dạng toàn số 0. Vô hại, và giống hệt cách `Point` đang nằm ở đó.
- Không cần xử lý `nil` ở đâu cả: document cũ thiếu field thì unmarshal ra struct zero. Đơn giản hơn hẳn phương án con trỏ.

Lưu ý khi sửa struct này: nó không phải struct chỉ để hiển thị. `View.Completed` được cộng dồn thành `viewTotal` để xét mốc thưởng theo view ở `event_schema.go:577-589` và `pkg/public/service/schedule.go:1161-1177`. Slot đó lấy từ collection `content` nên thay đổi trong tài liệu này không chạm tới, nhưng đừng đụng vào các slot hiện có.

### `ReconciliationItemContent` — phục vụ #2

`backend/internal/model/mg/reconciliation_item.go:32`. Ở đây chỉ một bucket cần tách nên dùng hai số vô hướng, không cần cả struct.

```go
// TotalViewPending giữ nguyên = tổng view status pending.
// Hai field dưới là hai phần của nó:
//   TotalViewPendingRewarded + TotalViewPendingExceeded == TotalViewPending
TotalViewPendingRewarded int64 `json:"totalViewPendingRewarded" bson:"totalViewPendingRewarded"`
TotalViewPendingExceeded int64 `json:"totalViewPendingExceeded" bson:"totalViewPendingExceeded"`
```

## #1 — Menu thống kê admin

### Hiện trạng

Ba tầng: `event_reward` → `event_analytic_daily` → API.

`GET /events/statistic` (router `pkg/admin/router/event.go:32`, service `pkg/admin/service/event.go:672`) chạy 4 truy vấn song song. Truy vấn view/cash dùng `GetEventStatistic` trên `event_analytic_daily`.

Response hiện tại (`pkg/admin/model/response/event.go:75`):

```json
{
  "creator": { "hasContent": 0 },
  "content": { "pending": 0, "approved": 0, "active": 0 },
  "view":    { "pending": 0, "approved": 0, "cashback": 0, "transfer": 0 },
  "cash":    { "pending": 0, "approved": 0, "cashback": 0, "transfer": 0 }
}
```

Cả 4 key `view` đều phồng. Cả 4 key `cash` đều đúng (`cash` còn cộng thêm tiền bonus từ `event_bonus`, phần này không có đối ứng bên view).

`event_analytic_daily.statistic.view.total` và `.rejected` đã lưu nhưng pipeline không đọc.

### Backend

**Pipeline nguồn** `GetStatisticRewardReport` (`aggregate_pipeline/event_reward.go:163`) — thêm bộ 7 nhánh song song với bộ view hiện có, khác đúng một điều kiện. Bộ cũ không đụng.

```go
"totalViewExceedBudget": bson.M{
    "$sum": bson.M{"$cond": []interface{}{
        bson.M{"$eq": []interface{}{"$isBudgetExceeded", true}},
        "$statistic.totalView", 0,
    }},
},
"totalViewExceedBudgetPending": bson.M{   // status = waiting_approved
    "$sum": bson.M{"$cond": []interface{}{
        bson.M{"$and": []bson.M{
            {"$eq": []string{"$status", constants.StatusWaitingApproved}},
            {"$eq": []interface{}{"$isBudgetExceeded", true}},
        }},
        "$statistic.totalView", 0,
    }},
},
// tương tự: ...Completed (status pending), ...Cashback (status completed),
//           ...Rejected, ...Transferred (isTransfer), ...NoRejected
```

Thêm 7 field tương ứng vào struct `StatisticRewardReport` (`event_reward.go:130`).

**Writer** — `UpdateAnalyticEventDaily` (`internal/service/event.go:742-775`) và `UpdateAnalyticUserEventDaily` (`:495-521`) gán thêm:

```go
ViewExceedBudget: modelmg.CommonStatisticContent{
    Total:     rewardAnalytics.TotalViewExceedBudget,
    Pending:   rewardAnalytics.TotalViewExceedBudgetPending,
    Rejected:  rewardAnalytics.TotalViewExceedBudgetRejected,
    Completed: rewardAnalytics.TotalViewExceedBudgetCompleted,
    Cashback:  rewardAnalytics.TotalViewExceedBudgetCashback,
    Transfer:  rewardAnalytics.TotalViewExceedBudgetTransferred,
},
```

**Pipeline đọc** `GetEventStatistic` (`aggregate_pipeline/event_analytic_daily.go:111`) — giữ nguyên 4 nhánh cũ, thêm 4 nhánh mới, **không `$subtract`**:

```go
"totalViewExceedPending":  bson.M{"$sum": "$statistic.viewExceedBudget.pending"},
"totalViewExceedApproved": bson.M{"$sum": "$statistic.viewExceedBudget.completed"},
"totalViewExceedCashback": bson.M{"$sum": "$statistic.viewExceedBudget.cashback"},
"totalViewExceedTransfer": bson.M{"$sum": "$statistic.viewExceedBudget.transfer"},
```

Không cần `$ifNull`: `$sum` bỏ qua field thiếu và trả 0. Document chưa backfill cho ra 0, tức phần trừ bằng 0, tức hiển thị y hệt hiện tại. Không có trạng thái trung gian sai.

Thêm 4 field vào struct `EventStatistic` (`event_analytic_daily.go:25`) và `EventChart` (`:48`).

### Ai trừ, ai không

`GetEventStatistic` được dùng ở 5 chỗ. Nguyên tắc: view đứng cạnh tiền thì trừ, view đứng một mình thì không.

| Consumer | Trừ | Lý do |
|---|---|---|
| `/events/statistic` — trang thống kê (`service/event.go:711`) | **Có** | 4 dòng view song song 4 dòng tiền |
| Biểu đồ ngày (`service/event.go:1008`) | Không | đường xu hướng hiệu suất |
| Biểu đồ tháng (`service/event.go:1071`) | Không | như trên |
| Export event-analytic ngày (`export_event_analytic.go:122`) | **Có** | Excel gửi partner, view cạnh cash |
| Export event-analytic tháng (`export_event_analytic.go:232`) | **Có** | như trên |

### Response mới

Ở `convertStatisticRepsonse` (`pkg/admin/service/event.go:965`), `view.*` trở thành **view được tính thưởng** — đây chính là bản sửa — và thêm nhóm thứ năm để hiển thị phần bị loại. Dùng lại generic `EventStatistic[int64]`, không định nghĩa type mới.

```json
{
  "creator":          { "hasContent": 0 },
  "content":          { "pending": 0, "approved": 0, "active": 0 },
  "view":             { "pending": 0, "approved": 0, "cashback": 0, "transfer": 0 },
  "viewExceedBudget": { "pending": 0, "approved": 0, "cashback": 0, "transfer": 0 },
  "cash":             { "pending": 0, "approved": 0, "cashback": 0, "transfer": 0 }
}
```

```go
View: response.EventStatistic[int64]{
    Pending:  r.TotalViewPending  - r.TotalViewExceedPending,
    Approved: r.TotalViewApproved - r.TotalViewExceedApproved,
    Cashback: r.TotalViewCashback - r.TotalViewExceedCashback,
    Transfer: r.TotalViewTransfer - r.TotalViewExceedTransfer,
},
ViewExceedBudget: response.EventStatistic[int64]{
    Pending: r.TotalViewExceedPending, Approved: r.TotalViewExceedApproved,
    Cashback: r.TotalViewExceedCashback, Transfer: r.TotalViewExceedTransfer,
},
```

### Frontend admin

`admin/src/pages/event-statistic/index.tsx:94-110` dựng nhóm "Số lượt xem" (render `:555-568`). Bốn dòng hiện có tự đúng theo response mới. Thêm nhóm hoặc bốn dòng "không được tính thưởng" từ `viewExceedBudget`. Nhãn mới vào `admin/src/locales/vi-VN.ts`.

### Export

`export_event_analytic.go` — cột view hiện có lấy giá trị đã trừ, thêm cột "Không được tính thưởng".

### Backfill

`event_analytic_daily` và `user_event_analytic_daily` là snapshot đã persist. Chạy lại `UpdateAnalyticEventDaily` và `UpdateAnalyticUserEventDaily` cho khoảng ngày cần thiết. Job có sẵn: `pkg/admin/service/shedule.go:486` và `:441`. Hàm lặp theo ngày có sẵn: `UpdateAnalyticOldEventDaily` (`internal/service/event.go:1519`), `UpdateUserEventAnalyticDaily` (`:1551`).

## #2 — Reconciliation item

### Hiện trạng

Một tầng. `GetTotalCashRewardByContent` (`aggregate_pipeline/event_reward.go:32`) group theo `(user, contentId, schema)`. Điều kiện: `date <= ToAt` + `event ∈ Events` + `type = byStatistic`. **Không lọc status** — `getConditionByReconciliation` (`pkg/admin/service/reconciliation.go:310`) chỉ gán `date` và `events`.

Đối chiếu hai bên trong `reconciliation_item.content`:

| Bucket | View | Cash |
|---|---|---|
| `waiting_approved` | *(chỉ nằm trong `TotalViewEnd`)* | không lưu |
| `pending` | `TotalViewPending` | `TotalCashPending` |
| `completed` | `TotalViewCompleted` | `TotalCashCompleted` |
| `rejected` | `TotalViewRejected` | `TotalCashRejected` |
| completed + rejected | `TotalViewBegin` | — |
| tổng trần cả 4 status | `TotalViewEnd` | — |

`item.TotalCash` từ pipeline (`$sum: "$cash"` không điều kiện) **không được dùng ở đâu cả**. Số tiền chi của kỳ là `TotalCash: item.TotalCashPending` (`reconciliation_processing.go:205`).

Hệ quả: **cặp duy nhất phải khớp nhau là `TotalViewPending` ↔ `TotalCashPending`**. `TotalViewEnd` và `TotalViewBegin` là bối cảnh cho người đối soát, không phải chứng từ thanh toán.

Ghi chú: `End − Begin − Pending` cho ra đúng phần `waiting_approved`, không liên quan gì tới vượt ngân sách. Một phương án suy ra dựa trên phép trừ này đã được cân nhắc và loại bỏ.

### Backend

**Pipeline** — thêm 2 nhánh, giữ nguyên `totalViewPending` ở `:86`:

```go
"totalViewPendingRewarded": bson.M{
    "$sum": bson.M{"$cond": []interface{}{
        bson.M{"$and": []bson.M{
            {"$eq": []string{"$status", constants.StatusPending}},
            {"$ne": []interface{}{"$isBudgetExceeded", true}},
        }},
        "$statistic.totalView", 0,
    }},
},
"totalViewPendingExceeded": bson.M{
    "$sum": bson.M{"$cond": []interface{}{
        bson.M{"$and": []bson.M{
            {"$eq": []string{"$status", constants.StatusPending}},
            {"$eq": []interface{}{"$isBudgetExceeded", true}},
        }},
        "$statistic.totalView", 0,
    }},
},
```

`$ne: [..., true]` ở nhánh rewarded xử lý luôn document cũ chưa có field `isBudgetExceeded` — missing ≠ true nên được tính là có thưởng.

Thêm 2 field vào struct `TotalCashRewardByContent` (`event_reward.go:11`).

**Writer** `ProcessingContent` (`reconciliation_processing.go:200-231`) — gán thêm 2 field.

**Guard ở `:192` phải đổi.** Hiện tại:

```go
if item.TotalViewPending == 0 { continue }
```

Vì `TotalViewPending` giữ nguyên nghĩa là tổng, guard này không loại được content mà toàn bộ view trong kỳ đều vượt ngân sách. Đổi thành:

```go
if item.TotalViewPendingRewarded == 0 { continue }
```

Đây là **thay đổi hành vi**: content 100% vượt ngân sách hiện đang vào kỳ với 0đ, sau thay đổi sẽ bị loại khỏi kỳ.

Đánh đổi đã chấp nhận: document overflow của những content này không được flip sang `completed` (vòng lặp `reconciliation_running.go:352-362` chỉ chạy trên item có trong kỳ), nên ở lại `status = pending` vô thời hạn. Không sinh item trùng ở kỳ sau vì guard vẫn loại chúng, nhưng số view đó sẽ cộng dồn vào `TotalViewPendingExceeded` của kỳ nào đó về sau nếu content ấy phát sinh thêm view được trả tiền. Nói cách khác `TotalViewPendingExceeded` là **view chưa được tính thưởng lũy kế**, không phải chỉ phát sinh trong kỳ.

**Response** `ReconciliationContentItem` (`pkg/admin/model/response/reconciliation.go:42`) — thêm `viewPendingRewarded` và `viewPendingExceeded`. Map ở `GetListContent` (`pkg/admin/service/reconciliation.go:206-229`).

**Export** `export_reconciliation.go` — cột "Lượt xem chờ đối soát" lấy `viewPendingRewarded`, thêm cột "Không được tính thưởng" (header `:91-99`, giá trị `:280-289`).

### Frontend admin

- `admin/src/pages/reconciliation/detail/components/tabs/content/components/table.tsx:53-73` — cột "Lượt xem chờ đối soát" đổi sang `viewPendingRewarded`, thêm cột "Không được tính thưởng" = `viewPendingExceeded`. Sau thay đổi, cột này khớp tuyệt đối với `cashPending` theo `CashPerView`.
- `.../content/components/info-modal.tsx:17-33` — thêm dòng tương ứng
- `.../content/type.d.ts:39-43` — thêm 2 key

### Backfill

Không cần. Field chỉ ghi khi tạo item của kỳ mới. Kỳ đã chốt đọc ra 0 và hiển thị đúng như lúc chốt.

## #3 — Trang cá nhân web user

Route `/trang-ca-nhan` (`frontend/config/routes.ts:94`) → `@/pages/profile` → `logged-in-view` → card "Số tiền tạm tính" + bảng thống kê theo nguồn.

### Hiện trạng — chỗ duy nhất trộn hai collection

`user_event.statistic.<source>.view`, ghi bởi `UpdateStatisticUserEvent` (`internal/service/event.go:883`, mapping từ `:1125`):

| Slot | Nguồn | Công thức |
|---|---|---|
| `Total` | `content` | `Σ statistic.view.total`, mọi status |
| `Pending` | `content` | `Σ` where `content.status = waiting_approved` |
| `Rejected` | `content` | `Σ` where `content.status = rejected` |
| `Completed` | `content` | `Σ` where `content.status = approved` |
| `Cashback` | **`event_reward`** | `Σ statistic.totalView` where `status = completed` |
| `Transfer` | **`event_reward`** | `Σ statistic.totalView` where `isTransfer = true` |
| `Waiting`, `Manual` | — | không được ghi |

Bảng FE (`frontend/src/pages/home/components/statistic/table.tsx`): "Lượt xem" ← `view.completed` · "Đã đối soát" ← `view.cashback` · "Chờ đối soát" ← `max(completed − cashback, 0)`. Hàm `max(..., 0)` là bằng chứng tác giả cũ đã biết hai nguồn có thể lệch nhau.

### Backend

**Pipeline** `GetStatisticContentBySource` (`aggregate_pipeline/event_reward.go:826`) — thêm bộ nhánh exceeded song song, giữ nguyên các nhánh cũ. Thêm field tương ứng vào struct `StatisticContentBySource` (`:808`).

**Writer** `UpdateStatisticUserEvent` (`internal/service/event.go:883`) — mapping của **mỗi** source (youtube, youtubeShort, tiktok, facebook, facebookReels, facebookPost, instagram, instagramReels, threads, shopeeVideo; từ `:1125`) gán thêm `ViewExceedBudget`.

Câu ghi ở `:1502` dùng `$set: {"statistic": statistic}` — **ghi đè nguyên khối**, không phải từng field. Hai hệ quả: field mới tự xuất hiện ngay lần hàm chạy đầu tiên nên **không cần migration**; nhưng nếu quên gán ở bất kỳ source nào thì giá trị đã có của source đó bị **xoá**, không phải giữ nguyên. Phải phủ đủ 10 source.

**Response** — không cần sửa gì. `pkg/public/service/event.go:344` và `:858` gán thẳng `&userEvent.Statistic` vào response, nên `viewExceedBudget` tự chảy ra `userEventStatistic`.

**Không trừ ở backend.** `view.cashback` và `view.transfer` giữ nguyên là tổng. FE tự tính khi hiển thị.

### Cạm bẫy khi viết phép trừ

Trong `user_event`, `view` trộn hai collection còn `viewExceedBudget` thuần `event_reward`. Hai slot cùng tên mang nghĩa khác nhau:

| Slot | `view.<slot>` | `viewExceedBudget.<slot>` |
|---|---|---|
| `completed` | view của **content đã duyệt** (collection `content`) | view của reward **status `pending`** |
| `cashback` | view của reward status `completed` | view của reward status `completed` |

Chỉ `cashback` và `transfer` là so sánh trực tiếp được. `view.completed` và `viewExceedBudget.completed` **không cùng hệ đo**, trừ thẳng cho ra số vô nghĩa.

Cách tính đúng cho bốn cột:

```
Lượt xem          = view.completed
Đã đối soát       = view.cashback − viewExceedBudget.cashback
Không tính thưởng = viewExceedBudget.cashback + viewExceedBudget.completed
Chờ đối soát      = max(view.completed − view.cashback − viewExceedBudget.completed, 0)
```

Nơi đặt phép trừ này — trong response của API hay trong FE — **để người triển khai quyết định**. Nếu đặt ở API thì viết một helper dùng chung cho cả `:344` và `:858`, đừng chép hai lần.

**Giới hạn đã biết:** view vượt ngân sách của content **chưa duyệt** (`status = waiting_approved`) không nằm trong `view.completed` nên không xuất hiện ở bảng. Đúng, vì content chưa duyệt cũng chưa được tính vào "Lượt xem".

### Phạm vi white-label

`table.tsx` không có package dùng chung, mỗi app một bản. **14 file**, bốn biến thể:

| Biến thể | App | Khác biệt |
|---|---|---|
| A | `frontend`, `anker` | nhãn "Lượt xem" |
| B | `mbbank`, `turborg`, `flamingo`, `vnpay`, `yody` | nhãn "Views", class `bg-transparent` |
| C | `tpbank`, `vng`, `vpbank`, `wildrift` | nhãn "Views" |
| D | `parasola`, `lusso`, `hdbank` | nhãn "Views", sourceMap có thêm `facebook_post` |

`getData()` giống hệt nhau ở cả 14 bản nên patch áp gần như y nguyên. Interface của `userEventStatistic` (`src/interfaces/`) cũng nhân bản theo app — thêm `viewExceedBudget` ở tất cả.

`logged-in-view` có 9 biến thể (`frontend` và `anker` dùng kiến trúc sidebar một trang dài; 12 bản còn lại dùng hai tab "Tiến trình" / "Nội dung"). Bảng nằm trong `StatisticUser` ở mọi bản nên thay đổi không lan tới `logged-in-view`. Cần xác minh lại khi triển khai.

### Backfill

`user_event` là snapshot. Document cũ thiếu `viewExceedBudget` → unmarshal ra struct zero, JSON trả về toàn số 0 → cột "Không tính thưởng" bằng 0 và bảng hiển thị y hệt hiện tại. Không có trạng thái trung gian sai, không cần xử lý `nil`.

`UpdateStatisticUserEvent` tính lại từ đầu mỗi lần chạy (aggregate lại toàn bộ từ `content`, `event_reward`, `event_bonus`) nên tự chữa lành — backfill chỉ là chạy lại, không cần script riêng.

Với event đang chạy thì gần như không cần làm gì: hàm được gọi realtime sau mỗi lần tính thưởng qua `UpdateBudgetStatistic` (`internal/service/event.go:56`, trigger ở `event_schema.go:287`), cộng 5 điểm cron ở `pkg/public/service/schedule.go:1084`, `:1265`, `:1468`, `:1758`, `:1947`. Chỉ những cặp user-event đã ngừng phát sinh reward mới cần chạy thủ công.

Các điểm gọi còn lại, để tham chiếu: `pkg/admin/service/event.go:80` (reject reward), `reconciliation_running.go:501` (sau khi chạy kỳ), `backfill_event_reward.go:256`, `migration.go:253,297,355,797,1048`.

Nơi ghi duy nhất khác vào collection này là `pkg/public/service/eligibility.go:262` — `InsertOne` khi user tham gia event, không đụng `statistic`.

## Lỗi có sẵn sửa kèm

Ba lỗi phát hiện khi rà trang cá nhân, đã thống nhất sửa trong cùng đợt.

**1. Nhãn view trùng nhãn tiền.** Trong card "Số tiền tạm tính" (`statistic/index.tsx:54,99`), hai dòng "Đã đối soát" / "Chờ đối soát" là **VNĐ**. Ngay dưới, bảng (`table.tsx:43,50`) có hai cột trùng tên nhưng là **số view**. Đổi nhãn cột trong bảng để nói rõ là lượt xem. Áp cho cả 14 bản.

**2. Sorter sai.** `table.tsx:39,46,53` — cả ba cột đều so sánh `a.view - b.view` nên sort hai cột sau không đúng. Sửa để mỗi cột so sánh đúng giá trị của nó. Áp cho cả 14 bản.

**3. `bpe` không có trong response.** `BudgetAlert` (`budget-alert/index.tsx:17-50`) và pill "Ngân sách tối đa" (`statistic/index.tsx:66-69`) đọc `matchedEvent.bpe.{total,used,remain,usedPercent}` (gán ở `logged-in-view:74-82`). `EventBriefResponse` (`pkg/public/model/response/event.go:33-66`) chỉ expose `isBudgetExhausted` và `bpc`, **không có `bpe`** — nó chỉ tồn tại ở model DB (`internal/model/mg/event.go:49`). Nên `budgetInfo` luôn `null` và cả hai khối ngân sách **chưa bao giờ hiển thị**.

Expose `bpe` trong `EventBriefResponse` (`GET /events`). Liên quan trực tiếp tới chủ đề: khi ambassador nhìn thấy cột "Không tính thưởng", banner ngân sách chính là thứ giải thích tại sao.

Sửa kèm chuỗi placeholder chưa dọn ở `budget-alert/index.tsx:44` — hiện lẫn ghi chú nội bộ và sẽ render ra UI.

## Known issues — ghi nhận, không sửa

**View vượt ngân sách bị khóa vĩnh viễn.** `reconciliation_running.go:349-362` flip **mọi** document `event_reward` pending sang `completed`, kể cả overflow. Sau đó `GetStatisticContentIsRewardInDay` trả `view.Completed` bao gồm cả view vượt ngân sách, và `event_schema.go:769` tính `totalView = doc.View.Value − view.Completed = 0`. Nếu event được nạp thêm ngân sách sau đó, số view kia không có đường nào để được trả thưởng. Chưa rõ là chính sách cố ý hay lỗi. Cần phiên thiết kế riêng.

**Engagement ở kỳ đối soát sai hai lần độc lập.** `reconciliation_processing.go:229`:

```go
Engagement = (content.Statistic.Like.Total + content.Statistic.Comment.Total) / item.TotalView
```

Tử số lấy từ collection `content` — là tổng like/comment **hiện tại của content**, không chặn theo `ToAt` của kỳ. Mẫu số lấy từ `event_reward` — có chặn theo `ToAt`, và phồng vì view vượt ngân sách. Hai cột `TotalLike`/`TotalComment` (`:211-212`) cũng lấy từ `content.Statistic` nên cũng không phải số của kỳ.

**Lỗi copy-paste ở nhánh youtube.** `internal/service/event.go:1128` — nhánh `youtube` và `youtubeShort` gán `View.Pending = contentStats.TotalCommentPending`, lấy nhầm số comment. Nhánh `tiktok` dùng đúng `TotalViewPending`.

## Kiểm thử

**Bất biến cốt lõi.** Với mỗi content trong một kỳ đối soát:

```
TotalViewPendingRewarded + TotalViewPendingExceeded == TotalViewPending
TotalViewPendingRewarded × CashPerView              == TotalCashPending
```

Với `event_analytic_daily` và `user_event_analytic_daily`, đúng cho **mọi** bucket vì `View` và `ViewExceedBudget` cùng nguồn `event_reward`:

```
ViewExceedBudget.<bucket> <= View.<bucket>
```

Với `user_event`, bất biến này **chỉ đúng ở hai slot** `Cashback` và `Transfer` — là hai slot duy nhất của `View` lấy từ `event_reward`. Bốn slot còn lại của `View` đến từ collection `content` nên không so sánh được với `ViewExceedBudget`; cụ thể `ViewExceedBudget.Completed` (status `pending` của reward) hoàn toàn có thể lớn hơn `View.Completed` (view của content đã duyệt) và đó không phải lỗi.

Với bảng trang cá nhân, bốn cột cộng lại đúng bằng cột đầu:

```
"Đã đối soát" + "Không tính thưởng" + "Chờ đối soát" == "Lượt xem"
```

Chỉ đúng khi cột cuối chưa bị clamp về 0. Bị clamp nghĩa là `view.cashback` (từ `event_reward`) đã vượt `view.completed` (từ `content`) — hai nguồn lệch nhau. Tình huống này có sẵn từ trước, không do thay đổi này gây ra, nhưng nên log lại khi gặp.

**Các ca cần phủ:**

| Ca | Mong đợi |
|---|---|
| Event còn đủ ngân sách | mọi số `exceed` = 0; toàn bộ hiển thị y hệt trước thay đổi |
| Event vượt ngân sách một phần (nhánh split) | `exceed` > 0; các bất biến trên đúng |
| Event hết sạch ngân sách (`maxCash = 0`) | ở #2 content bị guard loại khỏi kỳ; ở #1 và #3 `exceed` bằng đúng số view của bucket |
| Content 100% vượt ngân sách, kỳ trước bị loại, kỳ này có thêm view được trả tiền | item được tạo; `TotalViewPendingExceeded` gồm cả phần tồn của kỳ trước |
| Document `event_reward` cũ không có `isBudgetExceeded` | `$ne: [..., true]` cho `true` → tính là có thưởng, không rơi vào `exceed` |
| Document snapshot cũ chưa backfill | `$sum` field thiếu trả 0 → phần trừ bằng 0 → hiển thị y hệt hiện tại |
| Content có nhiều schema | kiểm tra riêng — `GetCashByContent` (`reconciliation.go:340`) chỉ lấy `data[0]`, là hạn chế có sẵn |
| Milestone | không split (`event_schema.go:990-995` chỉ set `cash=0` trên một doc) → `exceed` không áp dụng |

**Hồi quy bắt buộc:** chạy lại toàn bộ luồng tính thưởng trên dữ liệu có sẵn và xác nhận `event_reward` không đổi. Không thay đổi nào trong tài liệu này chạm vào đường ghi reward.
