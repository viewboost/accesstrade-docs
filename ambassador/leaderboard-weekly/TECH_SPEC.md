# Bảng xếp hạng theo tuần

Ngày: 2026-08-06

Mọi đường dẫn tính từ gốc repo `AT-Core/ambassador`.

## Vấn đề

Bảng xếp hạng của một event xếp theo con số luỹ kế từ đầu campaign. Cần cho phép từng campaign chọn xếp theo phần phát sinh trong tuần hiện tại, mà không đụng vào hành vi của các campaign đang chạy.

## Nguyên nhân gốc

`GetLeaderBoard` (`backend/pkg/public/service/event.go`) đọc collection `user_event` và sắp theo `statistic.pointTotal.completed`.

`user_event` giữ **một document cho mỗi cặp user-event**, chứa con số hiện tại. Không có trường ngày, không có lịch sử. Con số trong đó hình thành từ ngày nào là thông tin không tồn tại trong collection này. Vì vậy không có cách nào cắt nó theo tuần — vấn đề nằm ở hình dạng dữ liệu, không phải ở câu truy vấn.

Chiều thời gian nằm ở chỗ khác: `user_event_analytic_daily` giữ **một document cho mỗi bộ ba user-event-ngày**. Document này dựng trong `UpdateAnalyticUserEventDaily` (`backend/internal/service/event.go`), gom từ collection `event_reward` lọc theo đúng ngày đang xử lý. Nghĩa là số trong đó là **phát sinh của riêng ngày ấy**, không phải ảnh chụp luỹ kế.

Tiền lệ dùng đúng ngữ nghĩa này đã có sẵn: `GetUserStatistic` (`backend/pkg/public/service/user_statistic.go`) cộng chính collection này theo khoảng `date` để ra thống kê của một creator trong một quãng thời gian.

## Bẫy đặt tên cần biết trước khi đọc tiếp

**`pointTotal` chứa số view, không phải điểm.** `UserContentStatistic.GetPoint()` (`backend/internal/model/mg/user_event.go:213`) dựng `Point` bằng cách chép nguyên các trường của `View`. Frontend đọc `statistic.pointTotal` để hiển thị cột Views. Nếu đọc tên mà tưởng là một hệ điểm riêng thì sẽ đi tìm chỗ quy đổi không tồn tại.

**`Completed` không có nghĩa là đã xong.** Quy ước bucket của `CommonStatisticContent` lệch một nấc so với tên trạng thái thật — chi tiết xem `../update-report-view/TECH_SPEC.md`. Ở tài liệu này chỉ cần biết: xếp hạng cộng `pending + completed` là cộng toàn bộ view chưa bị từ chối, đúng bằng con số frontend hiển thị.

**Kỳ tuần trả `_id` là id của creator.** Ở nhánh luỹ kế `_id` là id của document `user_event`. Ở nhánh tuần không có document tương ứng vì mỗi dòng là số đã gộp, nên dùng id creator làm khoá. Frontend chỉ dùng trường này làm `key` khi render nên không vướng, nhưng đừng dựa vào nó để truy ngược document.

## Phạm vi

Ba chỗ phải sửa, đánh số dùng lại ở phần sau: cấu hình kỳ trên event (**#1**), nhánh xếp hạng theo tuần ở backend (**#2**), nhãn kỳ trên parasola (**#3**).

Kèm theo là hai hạng mục hạ tầng bắt buộc để #2 chạy được ngoài môi trường thật: index và cache.

### Ngoài phạm vi

Kỳ theo tháng. Xem lại tuần đã qua. Hạng của chính người xem. Ghim creator lên đầu bảng. Nhãn kỳ cho partner app ngoài parasola.

### Vùng cấm

Không sửa logic nhánh luỹ kế — nó đang phục vụ mọi campaign đang chạy.

Không đổi cách tính tiền thưởng.

Không thêm tham số kỳ vào API cho client truyền lên.

Không đụng `parasola/src/pages/home/components/logged-in-view/table.tsx`. Component này không file nào import; sửa vào là sửa mù, không có cách kiểm chứng.

## Nguyên tắc thiết kế

Thêm trường cấu hình mới, không đổi ngữ nghĩa trường cũ. Giá trị rỗng đồng nghĩa hành vi cũ, nên không cần migration và rollback chỉ là đổi lại lựa chọn trong admin.

Hai nhánh trả cùng hình dạng `UserEventResponse`. Frontend không rẽ nhánh theo kỳ.

Server chốt biên tuần theo giờ Việt Nam rồi trả xuống. Client chỉ hiển thị lại.

Kỳ đọc từ cấu hình event, không nhận từ client. Nếu nhận từ client thì frontend phải chờ dữ liệu event về mới gọi được bảng, và sẽ có lúc gọi sai vì thứ tự tải.

Mọi tính toán thuần tách thành hàm nhận tham số trả giá trị, để test không cần cơ sở dữ liệu.

## Thay đổi model

Một trường mới trên `EventOpts` (`backend/internal/model/mg/event.go`), không xoá hay đổi trường nào:

```go
LeaderboardPeriod string `json:"leaderboardPeriod,omitempty" bson:"leaderboardPeriod,omitempty"`
```

Hai hằng trong `backend/internal/constants/constants.go`:

```go
LeaderboardPeriodAllTime = "all_time"
LeaderboardPeriodWeek    = "week"
```

`omitempty` cộng với việc chuỗi rỗng rơi vào nhánh luỹ kế cho ta tương thích ngược miễn phí: document cũ unmarshal ra chuỗi rỗng, không cần xử lý con trỏ rỗng ở đâu cả.

`EventOpts` được truyền nguyên khối qua request và response của admin nên **không phải sửa DTO nào**.

## #1 — Cấu hình kỳ trên event

### Hiện trạng

Form event có tab tuỳ chọn với ba trường: số content tối đa mỗi ngày, hashtag, nguồn áp dụng.

### Admin

Thêm ô chọn thứ tư trong `admin/src/pages/event/components/modal.tsx`, hai lựa chọn lấy nhãn từ creator-os: *Toàn thời gian* và *Theo tuần*.

Bảng ánh xạ đặt trong `admin/src/configs/app.ts` theo đúng dạng các hằng lựa chọn khác, nhãn khai trong `locales/key.ts` và `locales/vi-VN.ts`.

### Nhân bản event

`cloneEventOptions` (`backend/pkg/admin/service/event.go`) chép từng trường bằng tay chứ không sao chép cả struct. Không bổ sung trường mới vào đây thì nhân bản event sẽ nuốt mất cấu hình kỳ — và im lặng, vì kết quả vẫn là một event hợp lệ.

## #2 — Nhánh xếp hạng theo tuần

### Hiện trạng

`GetLeaderBoard` làm ba việc trong một hàm: tìm event, truy vấn `user_event`, dựng response.

### Cấu trúc sau khi sửa

`GetLeaderBoard` chỉ còn lo phân giải kỳ và cache, rồi gọi một trong hai nhánh. Nhánh luỹ kế tách ra thành `getLeaderBoardAllTime` cho cân với `getLeaderBoardWeekly`.

Hai nhánh trả `(*response.UserEventAllResponse, error)`. Trả kèm lỗi là để phân biệt **kết quả rỗng hợp lệ** với **truy vấn hỏng** — cần cho quyết định có cache hay không ở mục sau.

### Biên tuần

`backend/internal/util/time.go`:

```go
func TimeStartOfWeekInHCM(t time.Time) time.Time {
    l, _ := time.LoadLocation(TimezoneHCM)
    timeHCM := t.In(l)
    offset := (int(timeHCM.Weekday()) + 6) % 7
    y, m, d := timeHCM.AddDate(0, 0, -offset).Date()
    return time.Date(y, m, d, 0, 0, 0, 0, l).UTC()
}

func TimeEndOfWeekInHCM(t time.Time) time.Time {
    return TimeEndOfDayInHCM(TimeStartOfWeekInHCM(t).AddDate(0, 0, 6))
}
```

Phép `(weekday + 6) % 7` là chỗ dễ sai duy nhất: Go đánh số Chủ nhật bằng 0, không quy về thứ Hai bằng 0 thì Chủ nhật rơi sang tuần sau.

Bất biến: tuần liền kề phải khít, không hở giây nào và không chồng lấn.

```
TimeEndOfWeekInHCM(t)  <  TimeStartOfWeekInHCM(t + 7 ngày)  ≤  +1 giây
```

### Pipeline

`GetUserEventLeaderboard` trong `backend/internal/module/database/mongodb/aggregate_pipeline/user_event_analytic_daily.go`, hàm thuần nhận điều kiện lọc cùng phân trang, trả mảng bước:

```
$match     { event, date: { $gte: T2 00:00, $lte: CN 23:59 } }
$group     _id: "$user"
           totalViewPending   = $sum statistic.view.pending
           totalViewCompleted = $sum statistic.view.completed
           totalCashPending   = $sum statistic.cash.pending
           totalCashCompleted = $sum statistic.cash.completed
$addFields totalView = totalViewCompleted + totalViewPending
$match     totalView > 0
$sort      { totalView: -1, _id: -1 }
$skip      chỉ gắn khi > 0
$limit     chỉ gắn khi > 0
```

Cộng từng trường bằng `$sum` rồi mới `$add` hai kết quả, chứ không `$add` trực tiếp trên trường gốc. `$sum` bỏ qua trường thiếu và luôn trả về số, nên `$add` an toàn mà không cần `$ifNull`.

Sắp xếp có tiêu chí phân định khi bằng điểm. Thiếu nó thì hai creator cùng điểm có thể đổi chỗ giữa các lần gọi, gây lặp dòng hoặc mất dòng khi phân trang.

Hai bước phân trang chỉ được gắn khi giá trị hợp lệ. Mongo ném lỗi nếu giới hạn bằng hoặc nhỏ hơn 0, mà lỗi đó bị tầng service nuốt, kết quả là bảng rỗng không rõ nguyên nhân. Nhánh luỹ kế vốn đã có guard tương đương bên trong `GetFindOptsUsingPage`.

### Ánh xạ sang response

```go
Statistic: modelmg.UserEventStatistic{
    PointTotal: modelmg.CommonStatisticContent{
        Total:     sf.TotalViewCompleted + sf.TotalViewPending,
        Pending:   sf.TotalViewPending,
        Completed: sf.TotalViewCompleted,
    },
    CashTotal: modelmg.CommonStatisticCashContent{
        Total:     sf.TotalCashCompleted + sf.TotalCashPending,
        Pending:   sf.TotalCashPending,
        Completed: sf.TotalCashCompleted,
    },
}
```

Các nhánh theo nền tảng để trống. Đây là chỗ mất mát đã nói ở PRD: collection nguồn không tách view theo nền tảng, nên partner app nào hiển thị icon từng nền tảng sẽ thấy toàn số 0 nếu bật kỳ tuần.

### Tra thông tin creator

Trước đây mỗi dòng một `FindOne`, hai mươi dòng là hai mươi truy vấn, trên endpoint công khai không cache. Đổi thành một truy vấn `$in` cho cả trang, dùng chung cho **cả hai nhánh**:

```go
func (e eventImpl) getUserShortInfoMap(ctx, userIds []modelmg.AppID) map[modelmg.AppID]response.UserShortInfo
func userShortInfoOf(users map[...], userId modelmg.AppID) response.UserShortInfo
```

Vòng lặp hết truy cập ra ngoài nên bỏ luôn goroutine và `sync.WaitGroup` ở cả hai nhánh.

Creator không tìm thấy vẫn giữ chỗ với tên `Anonymous`. Bỏ dòng thì thứ hạng nhảy số.

### Response

Ba trường mới trên `UserEventAllResponse`, đều `omitempty` nên response của kỳ luỹ kế không đổi một byte nào:

```go
Period        string              `json:"period,omitempty"`
PeriodStartAt *ptime.TimeResponse `json:"periodStartAt,omitempty"`
PeriodEndAt   *ptime.TimeResponse `json:"periodEndAt,omitempty"`
```

Tương thích hai chiều: frontend cũ gọi backend mới thì bỏ qua trường lạ; frontend mới gọi backend cũ thì không thấy `period`, hiểu là kỳ luỹ kế, không hiện nhãn.

## Index

`user_event_analytic_daily` đang có sáu index, tất cả đều dẫn đầu bằng `user` hoặc `inviter`:

```
inviter · user · {user, event} · {user, partner} · {inviter, event} · {inviter, partner}
```

Truy vấn kỳ tuần lọc `{event, date}` — **không có `user`**. Không index nào dùng được, Mongo quét toàn bộ collection, mỗi lượt vào trang chủ một lần. Collection này lớn theo tích của số creator, số event và số ngày.

Thêm vào `backend/internal/module/database/mongodb/index.go`:

```go
i.newIndex("event", "date"),
```

Thứ tự theo nguyên tắc so-sánh-bằng trước, khoảng-giá-trị sau.

Đây là lệch chuẩn của chính repo chứ không phải yêu cầu mới: `user_event` và `content_analytic_daily` đều đã có index `event` từ trước.

Index tạo lúc khởi động qua `Indexes()`, idempotent. Trên collection đã nhiều bản ghi thì lần tạo đầu tiên có thể lâu — theo dõi lượt deploy đầu.

## Cache

### Hiện trạng

Bảng xếp hạng nhiệm vụ đã cache mười phút theo lối cache-aside ở tầng handler (`backend/pkg/public/handler/mission.go`). Bảng xếp hạng event chưa có cache nào, dù truy vấn kỳ tuần nặng hơn và endpoint thì công khai, không xác thực.

### Khoá

```
list_leader_board_event_%s_%s_%d_%d
                        │  │  │  └─ limit
                        │  │  └──── page
                        │  └─────── hậu tố kỳ
                        └────────── event id
```

Hậu tố kỳ nhận diện **cả mốc kỳ**, không chỉ tên kỳ:

| Kỳ | Hậu tố |
|----|--------|
| Luỹ kế | `all_time` |
| Tuần | `week_2026-08-03` |

Nhờ vậy 00:00 thứ Hai là khoá tự đổi, dữ liệu tuần mới hiện ngay chứ không phải đợi hết mười phút. Admin đổi kỳ cũng thấy ngay.

Hàm dựng hậu tố là hàm thuần, `resolveLeaderBoardPeriod(event, now)`, trả về cặp kỳ và hậu tố.

### Cache gì và không cache gì

Kết quả rỗng **có** cache — đầu tuần chưa ai ghi điểm là trạng thái hợp lệ, không phải lỗi.

Truy vấn hỏng **không** cache. Không thì một lần cơ sở dữ liệu trục trặc sẽ khoá bảng rỗng suốt mười phút. Đây là lý do hai nhánh phải trả kèm lỗi.

Redis chết thì tính năng vẫn chạy, chỉ mất cache.

### Cảnh báo bắt buộc đọc trước khi mở rộng

**Khoá cache không chứa định danh người xem**, vì response hiện giống hệt nhau với mọi người — tham số định danh của `GetLeaderBoard` đang không được dùng tới, và điều đó có từ trước tính năng này.

Ai thêm dữ liệu riêng của người xem — hạng của tôi, đánh dấu dòng của tôi — mà quên đưa định danh vào khoá thì người này sẽ đọc phải dữ liệu của người kia. Cảnh báo đã đặt ngay tại chỗ dựng khoá trong code.

## #3 — Nhãn kỳ trên parasola

### Hiện trạng

`parasola/src/pages/home/components/leaderboard-list/index.tsx` render một card có tiêu đề "Bảng xếp hạng" rồi tới bảng bốn cột. Chỉ được render ở `not-logged-in/index.tsx`, sau khi qua cờ bật/tắt theo partner.

### Thay đổi

Thêm một dòng nhãn dưới tiêu đề khi kỳ khác luỹ kế. Kỳ luỹ kế trả `null`, không render dòng nào, giao diện giữ nguyên từng pixel.

Meta kỳ đi từ response qua `model.ts` xuống `_desktop.tsx` rồi `not-logged-in` tới component. Frontend **không** gửi kỳ lên API.

### Múi giờ — chỗ dễ sai nhất của cả tính năng

`ptime.TimeResponse` serialize ra chuỗi ISO theo giờ UTC. Thứ Hai 00:00 giờ Việt Nam thành `2026-08-02T17:00:00.000Z` — tức là **Chủ nhật**, theo giờ UTC.

Gọi `moment(x).format('DD/MM')` thẳng thì trình duyệt render theo múi giờ máy người dùng. Máy ở Việt Nam ra đúng, máy ở múi giờ khác ra `02/08` trong khi tuần thật là `03/08 – 09/08`.

```ts
const HCM_UTC_OFFSET = 7;
const inHCM = (v: string) => moment(v).utcOffset(HCM_UTC_OFFSET).format(fmt);
```

## Test

Mười ba hàm, hai mươi hai trường hợp, không hàm nào cần cơ sở dữ liệu.

| Nhóm | File | Hàm | Case |
|------|------|:---:|:----:|
| Biên tuần | `backend/internal/util/time_week_test.go` | 5 | 7 |
| Pipeline | `.../aggregate_pipeline/user_event_analytic_daily_test.go` | 4 | 8 |
| Khoá cache | `backend/pkg/public/service/leaderboard_period_test.go` | 4 | 7 |

Biên tuần che ca Chủ nhật, ca hai tuần liền kề phải khít, ca vắt qua ranh giới tháng.

Pipeline che guard phân trang với năm tổ hợp giá trị, thứ tự các bước, công thức xếp hạng, tiêu chí phân định khi bằng điểm, và bộ lọc loại creator không có view.

Khoá cache che mặc định luỹ kế khi cấu hình rỗng hoặc lạ, cùng tuần cho cùng khoá, sang tuần đổi khoá, và khoá luỹ kế không trôi theo thời gian.

### Chưa kiểm chứng

TypeScript chưa typecheck được — `typescript` không có trong `node_modules` của parasola lẫn admin, phải cài phụ thuộc trước.

Chưa chạy với dữ liệu thật; chưa campaign nào bật kỳ tuần.

`backend/pkg/public/service` có hai test đỏ sẵn trong `content_duplicate_test.go`, đã xác minh đỏ y hệt trên nhánh `develop` sạch, không liên quan tính năng này.

## Triển khai

Không cần migration dữ liệu. Index tự tạo lúc khởi động. Thứ tự deploy backend hay frontend trước đều được.

Rollback: đổi kỳ về *Toàn thời gian* trong admin, không cần rollback code.

## Bẫy cho người sửa sau

Thêm dữ liệu riêng của người xem thì phải đưa định danh vào khoá cache.

Đổi công thức xếp hạng thì phải đổi cả cột frontend hiển thị, không thì thứ hạng mâu thuẫn với con số bên cạnh.

Thêm kỳ mới thì hậu tố khoá cache phải nhúng mốc kỳ, giống `week_2026-08-03`, không thì kỳ mới không tự làm mới.

Muốn dựng giao diện icon từng nền tảng cho kỳ tuần thì phải đổi nguồn sang `content_analytic_daily` — nhưng collection đó không có tiền thưởng.

Đừng để frontend tự tính biên tuần.

`gofmt -w` trên `backend/pkg/public/service/event.go` sẽ căn lại một struct literal không liên quan trong `GetList`; block đó lệch chuẩn từ trước. Kiểm tra diff trước khi commit.
