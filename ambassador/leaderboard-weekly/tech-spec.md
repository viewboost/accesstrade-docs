# Technical Specification: Bảng xếp hạng theo tuần cho campaign Ambassador

**Date:** 2026-08-06
**Author:** dinhnguyen
**Version:** 1.0
**Project:** Ambassador (Parasola)
**Project Level:** 1 (1–10 stories)
**Status:** Implemented

---

## Document Overview

Thiết kế kỹ thuật cho tính năng cho phép mỗi campaign chọn xếp hạng creator theo phần phát sinh trong tuần hiện tại thay vì con số luỹ kế.

Mọi đường dẫn trong tài liệu tính từ gốc repo `AT-Core/ambassador`.

**Related:**
- [`overview.md`](./overview.md) — bối cảnh nghiệp vụ
- [`prd.md`](./prd.md) — yêu cầu chi tiết kèm AC
- [`../prd-partner-leaderboard-config-2026-04-02.md`](../prd-partner-leaderboard-config-2026-04-02.md) — cấu hình bảng xếp hạng theo partner

**Bẫy đặt tên cần biết trước khi đọc tiếp:**

`pointTotal` chứa số lượt xem, không phải điểm. `UserContentStatistic.GetPoint()` (`backend/internal/model/mg/user_event.go:213`) dựng `Point` bằng cách chép nguyên các field của `View`. Frontend đọc `statistic.pointTotal` để hiển thị cột Views. Đọc tên mà tưởng có hệ điểm riêng thì sẽ đi tìm chỗ quy đổi không tồn tại.

`Completed` không có nghĩa là đã xong — quy ước bucket của `CommonStatisticContent` lệch một nấc so với tên trạng thái thật, chi tiết ở [`../update-report-view/TECH_SPEC.md`](../update-report-view/TECH_SPEC.md). Ở đây chỉ cần biết cộng `pending + completed` là cộng toàn bộ lượt xem chưa bị từ chối, đúng bằng con số frontend hiển thị.

## Problem & Solution

`GetLeaderBoard` (`backend/pkg/public/service/event.go`) đọc collection `user_event` và sắp theo `statistic.pointTotal.completed`.

`user_event` giữ một document cho mỗi cặp user-event, chứa con số hiện tại. Không có field ngày, không có lịch sử. Con số hình thành từ ngày nào là thông tin không tồn tại trong collection này — vấn đề nằm ở hình dạng dữ liệu, không phải ở câu truy vấn.

Chiều thời gian nằm ở `user_event_analytic_daily`: một document cho mỗi bộ ba user-event-ngày, dựng trong `UpdateAnalyticUserEventDaily` (`backend/internal/service/event.go`) gom từ collection `event_reward` lọc theo đúng ngày đang xử lý. Số trong đó là phát sinh của riêng ngày ấy, không phải ảnh chụp luỹ kế. Cộng theo khoảng ngày ra đúng nghĩa "phát sinh trong tuần".

Tiền lệ dùng đúng ngữ nghĩa này đã có: `GetUserStatistic` (`backend/pkg/public/service/user_statistic.go`) cộng chính collection này theo khoảng `date`.

**Giải pháp:** thêm cấu hình kỳ ở cấp event, rẽ nhánh theo kỳ trong `GetLeaderBoard`, nhánh tuần đọc collection thống kê theo ngày và trả về đúng cấu trúc của nhánh luỹ kế.

## Requirements

Ánh xạ sang FR trong [`prd.md`](./prd.md):

| FR | Nội dung | Vùng ảnh hưởng |
|----|----------|----------------|
| FR-1 | Field `LeaderboardPeriod` trên `EventOpts` | Model |
| FR-2 | Ô chọn kỳ trong form event | Admin |
| FR-3 | Nhân bản event giữ cấu hình | Admin service |
| FR-4 | Xếp hạng theo tuần hiện tại | Backend public |
| FR-5 | Response mang thông tin kỳ | Backend public |
| FR-6 | Nhãn kỳ trên bảng | Frontend Parasola |
| FR-7 | Index `{event, date}` | Hạ tầng DB |
| FR-8 | Cache mười phút | Hạ tầng cache |

### Nguyên tắc thiết kế

Không đổi ngữ nghĩa field đang tồn tại; thêm field mới, giá trị rỗng đồng nghĩa hành vi cũ.

Nhánh luỹ kế không sửa logic — nó đang phục vụ mọi campaign đang chạy.

Hai nhánh trả cùng cấu trúc `UserEventResponse`; frontend không rẽ nhánh theo kỳ.

Server chốt biên tuần theo giờ Việt Nam rồi trả xuống; client chỉ hiển thị lại.

Kỳ đọc từ cấu hình event, không nhận từ client — nếu nhận từ client thì frontend phải chờ dữ liệu event về mới gọi được bảng, sẽ có lúc gọi sai vì thứ tự tải.

Mọi tính toán thuần tách thành hàm nhận tham số trả giá trị, để test không cần cơ sở dữ liệu.

### Vùng cấm

Không sửa logic nhánh luỹ kế. Không đổi cách tính tiền thưởng. Không thêm tham số kỳ vào API. Không đụng `parasola/src/pages/home/components/logged-in-view/table.tsx` — component này không file nào import, sửa vào là sửa mù.

## Technical Approach

### Thay đổi model — FR-1

`backend/internal/model/mg/event.go`:

```go
LeaderboardPeriod string `json:"leaderboardPeriod,omitempty" bson:"leaderboardPeriod,omitempty"`
```

`backend/internal/constants/constants.go`:

```go
LeaderboardPeriodAllTime = "all_time"
LeaderboardPeriodWeek    = "week"
```

`omitempty` cộng với việc chuỗi rỗng rơi vào nhánh luỹ kế cho tương thích ngược miễn phí: document cũ unmarshal ra struct zero, không cần xử lý con trỏ rỗng ở đâu. `EventOpts` truyền nguyên khối qua request/response admin nên không phải sửa DTO nào.

### Biên tuần — FR-4

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

Bất biến: tuần liền kề khít nhau, không hở giây nào và không chồng lấn.

```
TimeEndOfWeekInHCM(t)  <  TimeStartOfWeekInHCM(t + 7 ngày)  ≤  +1 giây
```

### Aggregate pipeline — FR-4

`GetUserEventLeaderboard` trong `backend/internal/module/database/mongodb/aggregate_pipeline/user_event_analytic_daily.go` — hàm thuần nhận điều kiện lọc cùng phân trang, trả mảng bước:

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

Cộng từng field bằng `$sum` rồi mới `$add` hai kết quả, không `$add` trực tiếp trên field gốc — `$sum` bỏ qua field thiếu và luôn trả về số nên `$add` an toàn mà không cần `$ifNull`.

Sắp xếp có tie-break `_id`. Thiếu nó thì hai creator cùng điểm có thể đổi chỗ giữa các lần gọi, gây lặp dòng hoặc mất dòng khi phân trang.

Hai bước phân trang chỉ gắn khi giá trị hợp lệ. Mongo ném lỗi nếu `$limit <= 0` hoặc `$skip` âm, mà lỗi đó bị tầng service nuốt, kết quả là bảng rỗng không rõ nguyên nhân. Nhánh luỹ kế vốn đã có guard tương đương bên trong `GetFindOptsUsingPage`.

### Cấu trúc service — FR-4, FR-5

`GetLeaderBoard` chỉ còn lo phân giải kỳ và cache, rồi gọi một trong hai nhánh. Nhánh luỹ kế tách thành `getLeaderBoardAllTime` cho cân với `getLeaderBoardWeekly`.

Hai nhánh trả `(*response.UserEventAllResponse, error)` — trả kèm lỗi để phân biệt kết quả rỗng hợp lệ với truy vấn hỏng, cần cho quyết định có cache hay không.

Ánh xạ kết quả aggregate sang response:

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

Các nhánh theo nền tảng để trống — collection nguồn không tách lượt xem theo nền tảng. Partner app nào hiển thị icon từng nền tảng sẽ thấy toàn số 0 nếu bật kỳ tuần.

`_id` của dòng dùng id creator, vì kỳ tuần không có document `user_event` tương ứng (mỗi dòng là số đã gộp). Frontend chỉ dùng field này làm `key` khi render nên không vướng, nhưng đừng dựa vào nó để truy ngược document.

### Gom truy vấn creator — NFR-2

Trước đây mỗi dòng một `FindOne`, hai mươi dòng là hai mươi truy vấn trên endpoint công khai không cache. Đổi thành một truy vấn `$in` cho cả trang, dùng chung cho cả hai nhánh:

```go
func (e eventImpl) getUserShortInfoMap(ctx, userIds []modelmg.AppID) map[modelmg.AppID]response.UserShortInfo
func userShortInfoOf(users map[...], userId modelmg.AppID) response.UserShortInfo
```

Vòng lặp hết truy cập ra ngoài nên bỏ luôn goroutine và `sync.WaitGroup` ở cả hai nhánh. Creator không tìm thấy vẫn giữ chỗ với tên `Anonymous` — bỏ dòng thì thứ hạng nhảy số.

### Response — FR-5

`backend/pkg/public/model/response/event.go`:

```go
Period        string              `json:"period,omitempty"`
PeriodStartAt *ptime.TimeResponse `json:"periodStartAt,omitempty"`
PeriodEndAt   *ptime.TimeResponse `json:"periodEndAt,omitempty"`
```

Tương thích hai chiều: frontend cũ gọi backend mới thì bỏ qua field lạ; frontend mới gọi backend cũ thì không thấy `period`, hiểu là kỳ luỹ kế, không hiện nhãn.

### Index — FR-7

`user_event_analytic_daily` đang có sáu index, tất cả dẫn đầu bằng `user` hoặc `inviter`:

```
inviter · user · {user, event} · {user, partner} · {inviter, event} · {inviter, partner}
```

Truy vấn kỳ tuần lọc `{event, date}` — không có `user`. Không index nào dùng được, Mongo quét toàn collection, mỗi lượt vào trang chủ một lần. Collection này lớn theo tích của số creator, số event và số ngày.

Thêm vào `backend/internal/module/database/mongodb/index.go`:

```go
i.newIndex("event", "date"),
```

Thứ tự theo nguyên tắc equality trước, range sau. Đây là lệch chuẩn của chính repo chứ không phải yêu cầu mới: `user_event` và `content_analytic_daily` đều đã có index `event`.

### Cache — FR-8

Bảng xếp hạng nhiệm vụ đã cache mười phút theo lối cache-aside ở tầng handler (`backend/pkg/public/handler/mission.go`). Bảng xếp hạng event chưa có cache nào dù truy vấn kỳ tuần nặng hơn.

```
list_leader_board_event_%s_%s_%d_%d
                        │  │  │  └─ limit
                        │  │  └──── page
                        │  └─────── hậu tố kỳ
                        └────────── event id
```

Hậu tố kỳ nhận diện cả mốc kỳ, không chỉ tên kỳ:

| Kỳ | Hậu tố |
|----|--------|
| Luỹ kế | `all_time` |
| Tuần | `week_2026-08-03` |

Nhờ vậy 00:00 thứ Hai là khoá tự đổi, dữ liệu tuần mới hiện ngay chứ không phải đợi hết mười phút. Admin đổi kỳ cũng thấy ngay. Hàm dựng hậu tố là hàm thuần `resolveLeaderBoardPeriod(event, now)`.

Kết quả rỗng có cache — đầu tuần chưa ai ghi điểm là trạng thái hợp lệ. Truy vấn hỏng không cache, không thì một lần cơ sở dữ liệu trục trặc sẽ khoá bảng rỗng suốt mười phút. Redis chết thì tính năng vẫn chạy, chỉ mất cache.

**Cảnh báo bắt buộc đọc trước khi mở rộng:** khoá cache không chứa định danh người xem, vì response hiện giống hệt nhau với mọi người — tham số định danh của `GetLeaderBoard` đang không được dùng tới, và điều đó có từ trước tính năng này. Ai thêm dữ liệu riêng của người xem mà quên đưa định danh vào khoá thì người này sẽ đọc phải dữ liệu của người kia. Cảnh báo đã đặt ngay tại chỗ dựng khoá trong code.

### Frontend Parasola — FR-6

`parasola/src/pages/home/components/leaderboard-list/index.tsx` thêm một dòng nhãn dưới tiêu đề khi kỳ khác luỹ kế. Kỳ luỹ kế trả `null`, không render dòng nào, giao diện giữ nguyên từng pixel.

Meta kỳ đi từ response qua `model.ts` xuống `_desktop.tsx` rồi `not-logged-in` tới component. Frontend không gửi kỳ lên API.

**Múi giờ — chỗ dễ sai nhất của cả tính năng.** `ptime.TimeResponse` serialize ra chuỗi ISO theo giờ UTC. Thứ Hai 00:00 giờ Việt Nam thành `2026-08-02T17:00:00.000Z` — tức là Chủ nhật, theo giờ UTC. Gọi `moment(x).format('DD/MM')` thẳng thì trình duyệt render theo múi giờ máy người dùng: máy ở Việt Nam ra đúng, máy ở múi giờ khác ra `02/08` trong khi tuần thật là `03/08 – 09/08`.

```ts
const HCM_UTC_OFFSET = 7;
const inHCM = (v: string) => moment(v).utcOffset(HCM_UTC_OFFSET).format(fmt);
```

### Admin — FR-2, FR-3

Ô chọn thứ tư trong tab Tuỳ chọn của `admin/src/pages/event/components/modal.tsx`, nhãn lấy từ creator-os. Bảng ánh xạ đặt trong `admin/src/configs/app.ts` theo đúng dạng các hằng lựa chọn khác, nhãn khai trong `locales/key.ts` và `locales/vi-VN.ts`.

`cloneEventOptions` (`backend/pkg/admin/service/event.go`) chép từng field bằng tay chứ không sao chép cả struct. Không bổ sung field mới vào đây thì nhân bản event sẽ nuốt mất cấu hình kỳ — và im lặng, vì kết quả vẫn là một event hợp lệ.

## Implementation Plan

| Giai đoạn | Nội dung | Trạng thái |
|-----------|----------|-----------|
| 1 | Model + constants + biên tuần + pipeline + service + response | ✅ PR #97 đã merge |
| 1 | Admin form + clone options | ✅ PR #97 |
| 1 | Frontend Parasola + index | ✅ PR #97 |
| 2 | Cache + tách `getLeaderBoardAllTime` + gom truy vấn creator | 🔄 PR #99 đang mở |
| 3 | Trạng thái rỗng đầu tuần, hạng của chính mình, nhãn kỳ cho khối tiền | 📋 chờ chốt câu hỏi để ngỏ |

## Acceptance Criteria (rút gọn — đầy đủ ở prd.md)

Campaign chưa cấu hình kỳ trả kết quả y hệt trước khi có tính năng.

Tuần bắt đầu thứ Hai theo giờ Việt Nam; Chủ nhật thuộc tuần hiện tại; biên hai tuần liền kề khít nhau.

Thứ hạng dựa trên `pending + completed`, khớp con số frontend hiển thị.

Sang tuần mới bảng làm mới ngay, không đợi hết TTL.

Nhãn kỳ hiển thị đúng ngày kể cả trên trình duyệt ở múi giờ khác.

Nhân bản event giữ nguyên cấu hình kỳ.

## Non-Functional Requirements

**Hiệu năng.** Cache hit tốn một truy vấn, cache miss tốn ba. Truy vấn kỳ tuần dùng index. Không N+1.

**Độ tin cậy.** Truy vấn lỗi trả bảng rỗng và không cache. Redis chết thì mất cache chứ tính năng vẫn chạy. Creator đã xoá vẫn giữ chỗ để thứ hạng không nhảy số.

**Bảo mật.** Response không chứa dữ liệu riêng người xem; ràng buộc về khoá cache ghi ở mục Cache.

**Khả năng mở rộng.** Thêm kỳ mới không đổi cấu trúc response, nhưng hậu tố khoá cache phải nhúng mốc kỳ.

## Dependencies

Collection `user_event_analytic_daily` phải được cập nhật đều bởi tác vụ thống kê theo ngày. Bảng kỳ tuần rỗng cho tới lượt chạy đầu tiên của tuần.

Redis — không bắt buộc, thiếu thì mất cache.

Không phụ thuộc dịch vụ ngoài, không migration.

## Risks & Mitigation

**Bảng rỗng đầu tuần bị ẩn khỏi trang.** Điều kiện hiển thị hiện tại là danh sách không rỗng. Giảm thiểu: hiện trạng thái rỗng thay vì ẩn — cần PM chốt, xem mục 8 của [`overview.md`](./overview.md).

**Tạo index trên collection lớn làm chậm lượt deploy đầu.** `Indexes()` chạy lúc khởi động. Giảm thiểu: theo dõi lượt deploy đầu tiên.

**Partner app hiển thị icon từng nền tảng sẽ thấy toàn số 0 nếu bật kỳ tuần.** Giảm thiểu: chỉ bật kỳ tuần cho partner dùng giao diện dạng bảng như Parasola, cho tới khi có phương án nguồn dữ liệu khác.

**Người mở rộng sau quên đưa định danh người xem vào khoá cache → rò dữ liệu giữa các user.** Giảm thiểu: cảnh báo đặt ngay tại chỗ dựng khoá trong code và ở mục Cache của tài liệu này.

## Next Steps

Chốt ba câu hỏi để ngỏ ở mục 8 của [`overview.md`](./overview.md).

Chạy `yarn install` ở `parasola` và `admin` rồi typecheck — hiện chưa kiểm chứng được.

Chạy thử với một campaign staging bật kỳ tuần, đối chiếu số liệu với `user_event_analytic_daily`.

Merge PR #99 (cache).

## Bẫy cho người sửa sau

Thêm dữ liệu riêng của người xem thì phải đưa định danh vào khoá cache.

Đổi công thức xếp hạng thì phải đổi cả cột frontend hiển thị, không thì thứ hạng mâu thuẫn với con số bên cạnh.

Thêm kỳ mới thì hậu tố khoá cache phải nhúng mốc kỳ.

Muốn dựng giao diện icon từng nền tảng cho kỳ tuần thì phải đổi nguồn sang `content_analytic_daily` — nhưng collection đó không có tiền thưởng.

Đừng để frontend tự tính biên tuần.

`gofmt -w` trên `backend/pkg/public/service/event.go` sẽ căn lại một struct literal không liên quan trong `GetList`; block đó lệch chuẩn từ trước. Kiểm tra diff trước khi commit.
