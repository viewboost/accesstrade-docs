# Tech Spec: Bảng xếp hạng theo tuần

**Ngày:** 2026-08-06 · **Branch thực tế:** `feat/leaderboard-weekly` (từ `origin/release`, rebase sang `develop`) · `perf/leaderboard-cache` (từ `origin/develop`)
**PRD:** `prd-leaderboard-weekly-2026-08-06.md`
**Trạng thái:** ✅ Đã triển khai FR-001→FR-005. **PR #97** merged 2026-08-05 vào `develop`; cache + sửa kèm → **PR #99** (open). 3 đề xuất §7 PRD chờ duyệt.

---

## 1. Phạm vi theo PRD

| FR | Thay đổi | File | Trạng thái |
|----|----------|------|-----------|
| FR-001 | Field `LeaderboardPeriod` + ô chọn admin + nhãn locale | `internal/model/mg/event.go`, `admin/src/pages/event/components/modal.tsx`, `admin/src/configs/app.ts` | ✅ Đã làm (#97) |
| FR-002 | Biên tuần + aggregate pipeline + rẽ nhánh service | `internal/util/time.go`, `.../aggregate_pipeline/user_event_analytic_daily.go`, `pkg/public/service/event.go` | ✅ Đã làm (#97) |
| FR-003 | 3 field kỳ trong response + nhãn kỳ FE | `pkg/public/model/response/event.go`, `parasola/.../leaderboard-list/` | ✅ Đã làm (#97) |
| FR-004 | Index `{event, date}` + cache 10 phút | `internal/module/database/mongodb/index.go`, `internal/module/redis/key.go` | ✅ Index #97, cache #99 |
| FR-005 | `cloneEventOptions` giữ cấu hình kỳ | `pkg/admin/service/event.go` | ✅ Đã làm (#97) |

Mọi đường dẫn tính từ gốc repo `AT-Core/ambassador`.

**Root cause tóm tắt:** `GetLeaderBoard` (`pkg/public/service/event.go`) đọc `user_event` — collection giữ 1 document cho mỗi cặp user-event, chứa con số hiện tại, **không có field ngày**. Con số hình thành từ ngày nào là thông tin không tồn tại → không cắt theo tuần được. Chiều thời gian nằm ở `user_event_analytic_daily`: 1 document cho mỗi bộ ba user-event-ngày, dựng trong `UpdateAnalyticUserEventDaily` (`internal/service/event.go`) gom từ `event_reward` lọc theo **đúng ngày đang xử lý** → là delta ngày, cộng theo khoảng ra đúng "phát sinh trong tuần".

⚠️ **Bẫy đặt tên — đọc trước khi vào §2.** `pointTotal` chứa **số lượt xem**, không phải điểm: `UserContentStatistic.GetPoint()` (`internal/model/mg/user_event.go:213`) dựng `Point` bằng cách chép nguyên các field của `View`. Frontend đọc `statistic.pointTotal` để hiển thị cột Views. Đọc tên mà tưởng có hệ điểm riêng thì sẽ đi tìm chỗ quy đổi không tồn tại.

---

## 2. Chi tiết implement

### 2.1 FR-001 — field cấu hình (`internal/model/mg/event.go`)

```go
// EventOpts — thêm field:
LeaderboardPeriod string `json:"leaderboardPeriod,omitempty" bson:"leaderboardPeriod,omitempty"`
```

```go
// internal/constants/constants.go
LeaderboardPeriodAllTime = "all_time"
LeaderboardPeriodWeek    = "week"
```

`omitempty` + chuỗi rỗng rơi vào nhánh luỹ kế cho tương thích ngược miễn phí: document cũ unmarshal ra struct zero, **không cần xử lý con trỏ rỗng ở đâu**. `EventOpts` truyền nguyên khối qua request/response admin (`*modelmg.EventOpts`) → không phải sửa DTO nào.

### 2.2 FR-002 — biên tuần (`internal/util/time.go`)

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

⚠️ `(weekday + 6) % 7` là chỗ dễ sai duy nhất: **Go đánh số Chủ nhật bằng 0**, không quy về thứ Hai bằng 0 thì Chủ nhật rơi sang tuần sau. Bất biến phải giữ:

```
TimeEndOfWeekInHCM(t)  <  TimeStartOfWeekInHCM(t + 7 ngày)  ≤  +1 giây
```

### 2.3 FR-002 — aggregate pipeline (`.../aggregate_pipeline/user_event_analytic_daily.go`)

`GetUserEventLeaderboard(cond, skip, limit)` — hàm thuần, trả mảng bước:

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

Ba quyết định nhỏ, mỗi cái đều có lý do:

**Cộng từng field bằng `$sum` rồi mới `$add`**, không `$add` trực tiếp trên field gốc — `$sum` bỏ qua field thiếu và luôn trả về số nên `$add` an toàn mà không cần `$ifNull`.

**Tie-break `_id` trong `$sort`** — thiếu nó thì hai creator cùng điểm có thể đổi chỗ giữa các lần gọi, gây lặp dòng hoặc mất dòng khi phân trang.

⚠️ **Chỉ gắn `$skip`/`$limit` khi giá trị hợp lệ.** Mongo ném lỗi nếu `$limit <= 0` hoặc `$skip` âm, mà lỗi đó bị tầng service nuốt (`if err != nil { return res }`) → bảng rỗng **không rõ nguyên nhân**. Nhánh luỹ kế vốn đã có guard tương đương bên trong `GetFindOptsUsingPage`.

### 2.4 FR-002, FR-004 — rẽ nhánh + cache (`pkg/public/service/event.go`)

`GetLeaderBoard` chỉ còn lo phân giải kỳ và cache; nhánh luỹ kế tách thành `getLeaderBoardAllTime` cho cân với `getLeaderBoardWeekly`.

```go
period, cacheSuffix := resolveLeaderBoardPeriod(event, time.Now())
cacheKey := redis.GetKeyCacheListLeaderBoardEvent(event.ID.Hex(), cacheSuffix, query.Page, query.Limit)

var cached *response.UserEventAllResponse
if ok := redis.GetJSON(cacheKey, &cached); ok && cached != nil {
    return cached
}

var err error
if period == constants.LeaderboardPeriodWeek {
    res, err = e.getLeaderBoardWeekly(ctx, query, event)
} else {
    res, err = e.getLeaderBoardAllTime(ctx, query, event)
}
if err != nil {
    return res // KHÔNG cache khi truy vấn hỏng
}
_ = redis.SetKeyValue(cacheKey, res, leaderBoardCacheTTL)
```

Hai nhánh trả `(*response.UserEventAllResponse, error)` — trả kèm lỗi để **phân biệt kết quả rỗng hợp lệ với truy vấn hỏng**. Rỗng hợp lệ (đầu tuần chưa ai ghi điểm) vẫn cache; truy vấn hỏng thì không, không thì một lần DB trục trặc khoá bảng rỗng suốt 10 phút.

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

⚠️ Các nhánh theo nền tảng **để trống** — `user_event_analytic_daily` không tách view theo nền tảng (`EventAnalyticSource` chỉ có số lượng content). Partner app nào hiển thị icon TikTok/Facebook/Threads kèm số riêng sẽ thấy toàn số 0 nếu bật kỳ tuần. Parasola không vướng vì bảng của nó là 2 cột Views / Kiếm được.

⚠️ `_id` của dòng dùng **id creator**, vì kỳ tuần không có document `user_event` tương ứng (mỗi dòng là số đã gộp). Frontend chỉ dùng field này làm `key` khi render nên không vướng, nhưng đừng dựa vào nó để truy ngược document.

### 2.5 FR-004 — khoá cache (`internal/module/redis/key.go`)

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

Nhờ vậy 00:00 thứ Hai là khoá tự đổi → dữ liệu tuần mới hiện ngay, không phải đợi hết TTL. Admin đổi kỳ cũng thấy ngay. Hàm dựng hậu tố là hàm thuần `resolveLeaderBoardPeriod(event, now)`.

⚠️ **Khoá không chứa định danh người xem**, vì response hiện giống hệt nhau với mọi người — tham số định danh của `GetLeaderBoard` đang không được dùng tới, và điều đó có **từ trước** tính năng này. Ai thêm dữ liệu riêng người xem (hạng của tôi, đánh dấu dòng của tôi) mà quên đưa định danh vào khoá thì **người này đọc phải dữ liệu của người kia**. Cảnh báo đã đặt ngay tại chỗ dựng khoá trong code.

### 2.6 FR-004 — index (`internal/module/database/mongodb/index.go`)

```go
// user_event_analytic_daily — thêm:
i.newIndex("event", "date"),
```

Sáu index sẵn có đều dẫn đầu bằng `user` hoặc `inviter`:

```
inviter · user · {user, event} · {user, partner} · {inviter, event} · {inviter, partner}
```

Truy vấn kỳ tuần lọc `{event, date}` — **không có `user`** → không index nào dùng được, Mongo quét toàn collection, mỗi lượt vào trang chủ một lần. Collection lớn theo tích của số creator × số event × số ngày.

Thứ tự `{event, date}` theo nguyên tắc equality trước, range sau. Đây là lệch chuẩn của chính repo chứ không phải yêu cầu mới: `user_event` và `content_analytic_daily` đều đã có index `event` từ trước.

### 2.7 FR-003 — nhãn kỳ (`parasola/.../leaderboard-list/index.tsx`)

```ts
const HCM_UTC_OFFSET = 7;

const renderPeriodLabel = (meta?: ILeaderboardPeriodMeta) => {
  if (meta?.period !== 'week') return null;          // all_time → không render dòng nào
  const { periodStartAt, periodEndAt } = meta;
  if (!periodStartAt || !periodEndAt) return 'Tuần này';
  const fmt = AppConst.format.dateWithDayMonthOnly;
  const inHCM = (v: string) => moment(v).utcOffset(HCM_UTC_OFFSET).format(fmt);
  return `Tuần này · ${inHCM(periodStartAt)} – ${inHCM(periodEndAt)}`;
};
```

⚠️ **Phải ghim `utcOffset(7)`.** `ptime.TimeResponse` serialize ra chuỗi ISO theo giờ UTC: thứ Hai 00:00 giờ Việt Nam thành `2026-08-02T17:00:00.000Z` — tức là **Chủ nhật**, theo giờ UTC. Gọi `moment(x).format('DD/MM')` thẳng thì trình duyệt render theo múi giờ máy người dùng → máy ngoài Việt Nam hiện `02/08` trong khi tuần thật là `03/08 – 09/08`.

Meta kỳ đi từ response qua `model.ts` → `_desktop.tsx` → `not-logged-in/index.tsx` → component. **Frontend không gửi kỳ lên API** — nếu gửi thì phải chờ dữ liệu event về mới gọi được bảng, sẽ có lúc gọi sai vì thứ tự tải.

### 2.8 FR-005 — nhân bản event (`pkg/admin/service/event.go`)

```go
res := &modelmg.EventOpts{
    MaxContentPerDay:  options.MaxContentPerDay,
    LeaderboardPeriod: options.LeaderboardPeriod, // ← thêm
}
```

⚠️ `cloneEventOptions` chép **từng field bằng tay**, không sao chép cả struct. Thêm field mới vào `EventOpts` mà quên chỗ này thì nhân bản event nuốt mất cấu hình — và **im lặng**, vì kết quả vẫn là một event hợp lệ.

### 2.9 Sửa kèm — gom truy vấn creator

Trước đây mỗi dòng bảng một `FindOne` → 20 dòng là 20 truy vấn, trên endpoint public không cache. Đổi thành 1 truy vấn `$in` cho cả trang, dùng chung **cả hai nhánh**:

```go
func (e eventImpl) getUserShortInfoMap(ctx context.Context, userIds []modelmg.AppID) map[modelmg.AppID]response.UserShortInfo
func userShortInfoOf(users map[modelmg.AppID]response.UserShortInfo, userId modelmg.AppID) response.UserShortInfo
```

Vòng lặp hết truy cập ra ngoài nên bỏ luôn goroutine + `sync.WaitGroup` ở cả hai nhánh. Creator không tìm thấy vẫn giữ chỗ với tên `Anonymous` — bỏ dòng thì thứ hạng nhảy số (1, 2, 4…).

### 2.10 Không sửa

- **Logic nhánh luỹ kế** — chỉ tách hàm, không đổi truy vấn hay thứ tự sắp xếp. Nó đang phục vụ mọi campaign đang chạy.
- **Cách tính tiền thưởng** — bảng reset theo tuần nhưng tiền luỹ kế.
- **API** — không đổi đường dẫn, không thêm query param.
- **`parasola/src/pages/home/components/logged-in-view/table.tsx`** — component `TableLeaderBoardView` **không file nào import**, sửa vào là sửa mù, không có cách kiểm chứng.

---

## 3. Thứ tự thực thi

1. Model + constants (2.1) — không phụ thuộc gì
2. Biên tuần (2.2) + pipeline (2.3) — hai hàm thuần, test được ngay
3. Rẽ nhánh service (2.4) + response FR-003 — cần 1 và 2
4. Index (2.6) — độc lập, nên vào cùng đợt deploy với 3
5. Admin (2.1 phần FE) + clone options (2.8)
6. Frontend Parasola (2.7) — cần response từ 3
7. Cache (2.4 phần cache) + khoá (2.5) + gom truy vấn (2.9) — PR riêng

---

## 4. Verify & test matrix

**API (so trước/sau, dùng event đã bật kỳ tuần):**

```bash
curl 'https://api.viewboost.vn/events/<event-id>/leaderboards'
# kỳ all_time: response KHÔNG có field period/periodStartAt/periodEndAt
# kỳ week:     có đủ 3 field, periodStartAt = T2 00:00 giờ VN dạng UTC
```

**UI — 6 case PRD FR-002**, chạy trên trang chủ campaign Parasola, desktop + mobile viewport:

| Case | Setup | Kỳ vọng |
|---|---|---|
| 1 | Event kỳ *Toàn thời gian* | Bảng y hệt trước, không có dòng nhãn kỳ |
| 2 | Event kỳ *Theo tuần*, giữa tuần | Chỉ hiện view phát sinh trong tuần; có dòng `Tuần này · DD/MM – DD/MM` |
| 3 | Creator ngừng đăng, tuần này 0 view | Không xuất hiện trên bảng |
| 4 | Chủ nhật 23:00 (đổi giờ máy hoặc chờ) | Vẫn thuộc tuần hiện tại |
| 5 | Thứ Hai 00:05, chưa có bản ghi | Bảng rỗng — hành vi theo kết quả duyệt §7 PRD |
| 6 | Hai creator cùng số view | Thứ tự không đổi giữa các lần F5 |

**Múi giờ:** đổi múi giờ máy sang UTC+0 hoặc UTC+9 → dòng nhãn vẫn phải hiện `03/08 – 09/08`.

**Cache:** đổi kỳ trong admin → F5 trang chủ thấy đổi ngay (khoá cache đổi theo kỳ).

**Đơn vị (13 hàm / 22 case, không cần DB):**

```bash
cd backend
go test ./internal/util/ -run Week -v                                    # biên tuần 5/7
go test ./internal/module/database/mongodb/aggregate_pipeline/ -v        # pipeline 4/8
go test ./pkg/public/service/ -run LeaderBoardPeriod -v                  # khoá cache 4/7
```

**Regression:** bảng xếp hạng của các partner khác Parasola (kỳ luỹ kế) không đổi; cờ `showLeaderboard` / `showLeaderboardAmount` theo partner vẫn hoạt động.

---

## 5. Lưu ý cho dev/QA (edge cases)

- **E1** — Bảng kỳ tuần rỗng cho tới lượt chạy đầu tiên của tác vụ thống kê trong tuần. QA test sáng thứ Hai dễ tưởng hỏng.
- **E2** — Cache TTL 10 phút. Sửa dữ liệu rồi F5 ngay có thể chưa thấy; đổi **kỳ** thì thấy ngay vì khoá đổi.
- **E3** — Partner app hiển thị icon từng nền tảng (`frontend`, `tpbank`, `anker`, `mbbank`, `lusso`) sẽ thấy toàn số 0 nếu bật kỳ tuần. Chưa hỗ trợ, xem 2.4.
- **E4** — `gofmt -w` trên `pkg/public/service/event.go` sẽ căn lại một struct literal **không liên quan** trong `GetList` (block đó lệch chuẩn từ trước). Kiểm tra diff trước khi commit.
- **E5** — `pkg/public/service` có 2 test đỏ sẵn trong `content_duplicate_test.go` (`buildDuplicateCheckFilter` chưa cập nhật sau khi bỏ `partnerID` khỏi filter). Đã xác minh đỏ y hệt trên `develop` sạch, **không liên quan** tính năng này.
- **E6** — Tạo index trên collection lớn có thể làm chậm lượt deploy đầu tiên. `Indexes()` chạy lúc khởi động, idempotent nên chạy lại an toàn.

---

## Unresolved

- **3 đề xuất §7 PRD chờ Sếp duyệt** — trạng thái rỗng đầu tuần, định nghĩa tuần, nhãn cho khối tiền cá nhân.
- **PR #99** (cache + sửa kèm A/B/C) chờ review.
- **TypeScript chưa typecheck được** — `typescript` không có trong `node_modules` của Parasola lẫn admin, cần `yarn install` rồi chạy lại.
- **Chưa chạy với dữ liệu thật** — chưa campaign nào bật kỳ tuần; cần 1 campaign staging để đối chiếu số liệu với `user_event_analytic_daily`.
- Sau deploy: Ops cần biết bật kỳ tuần cho campaign nào, và chỉ bật cho partner dùng giao diện dạng bảng (xem E3).
