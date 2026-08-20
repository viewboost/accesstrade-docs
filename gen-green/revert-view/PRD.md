# PRD — Gộp dữ liệu ngày tràn của event về ngày kết thúc (Merge Overflow Day)

> Bối cảnh: sự cố dữ liệu production. Event kết thúc ngày **31/07/2026** nhưng hệ thống vẫn ghi nhận
> và tạo dữ liệu sang ngày **01/08/2026**.

## Changelog

**2026-08-20 — bản đầu** (Thanh Trung).

**2026-08-20 — rà soát đối chiếu source `vcreator@release` (commit `5ab1bc78`).** Mọi khối bắt đầu bằng
`> **Đính chính**` hoặc `> **Bổ sung**` trong tài liệu này là của đợt rà soát đó, có trích code làm bằng.
Bốn nhóm thay đổi:

1. **Ngữ nghĩa trạng thái reward.** `status = completed` là **đã đối soát**, KHÔNG phải đã chi. Đã chi là
   `isTransfer = true` / có `transferId`. Guard chặn phải đổi theo.
2. **Cách xử lý reward đổi hẳn.** Không gọi lại hàm recompute cho ngày đích nữa mà **chuyển reward
   ngày nguồn sang ngày đích** theo ba nhánh (by-statistic có/không dòng cùng schema, và milestone).
   Reward milestone trước đây không được nhắc tới trong tài liệu.
3. **Đổi tên tham số input.** `fromAt`/`toAt` trùng nghĩa "khoảng ngày" với toàn bộ endpoint migration
   sẵn có, dễ gõ ngược. Đổi thành `overflowDate` / `mergeIntoDate`.
4. **Sửa dẫn chứng sai** (key nằm ở header chứ không phải query, tên type port từ ambassador, số điểm
   khác bản gốc, lý do "recompute sẽ upsert doc quay lại", điều kiện chặn còn thiếu).

Còn **hai số liệu chưa có**, chặn việc bắt đầu code — xem mục ngay dưới Problem Statement.

## Problem Statement

Một số event trên production có `endAt` là 31/07/2026. Hệ thống vẫn tiếp tục ghi `content-flow` sau khi event đã kết thúc, kéo theo việc sinh ra `content-analytic-daily` (và các doc thống kê phụ thuộc) mang `date = 01/08/2026` — một ngày nằm ngoài vòng đời của event.

> **Bổ sung** — "lỗi crawler" hiện có **hai ứng viên nguyên nhân**, chưa xác định là cái nào (hoặc cả hai):
>
> **(a) Crawl chỉ định eventId bỏ qua bộ lọc `endAt`.** Commit `ad98d4db` "crawl event cu the"
> (`pkg/public/service/schedule.go`, 01/08/2026 21:03 — đúng ngày dữ liệu tràn) thêm nhánh: nếu truyền
> danh sách eventId thì **không** áp `endAt > now` nữa.
>
> ```go
> if query != nil && len(query.Events) > 0 {
>     condition["_id"] = bson.M{"$in": util.ConvertStringsToObjectIDs(eventIDStrs)}
> } else {
>     condition["status"]  = constants.StatusActive
>     condition["startAt"] = bson.M{"$lte": now}
>     condition["endAt"]   = bson.M{"$gt": now}   // <- nhánh này mới có chặn
> }
> ```
>
> Ba crawler còn lại (`CrawlDataContentTiktokSelf`, `CrawlDataContentFacebook`, `CrawlDataContent`) vẫn
> giữ bộ lọc. Nếu đây là nguyên nhân thì mỗi lần vận hành crawl chỉ định một event đã kết thúc là dữ
> liệu hỏng lại y hệt — **trên chính event vừa sửa**, không phải "event tiếp theo".
>
> **(b) Callback crawl về muộn.** Đã có issue riêng đang mở:
> `Vin-VCreator/vcreator#73 — [PRD] Stale-callback guard`. Phần Out of Scope của issue đó viết rằng việc
> dọn dữ liệu đã lệch "sẽ là một PRD riêng" — nhiều khả năng chính là tài liệu này. Hai bên nên trỏ vào nhau.

Hệ quả với người dùng:

- **Tiền thưởng nằm sai ngày, và có thể mất hẳn.** Hai khả năng, phải đo mới biết event này rơi vào cái nào:
  - *Không có reward ở ngày 01/08* → view tràn không được quy đổi, creator **mất tiền** thật.
  - *Có reward ở ngày 01/08* → creator **không mất tiền**, nhưng tiền nằm ở một ngày ngoài vòng đời event: sai kỳ đối soát, sai kỳ chi, và biên bản đối soát trỏ vào một ngày lẽ ra không tồn tại.

- **Báo cáo event sai.** Biểu đồ và bảng thống kê của event xuất hiện thêm một cột ngày 01/08/2026 nằm ngoài thời gian chạy event, khiến admin và partner đối soát bị lệch. Tổng view của ngày cuối cùng (31/07) bị thiếu đúng bằng phần đã tràn sang.
- **Reward milestone cũng rơi ra ngoài vòng đời event.** Reward loại `by-view-milestone` và
  `by-content-milestone` ghi `Date = TimeStartOfDayInHCM(time.Now())` — tức **ngày job chạy**, không phải ngày
  phát sinh view. Mốc thưởng đạt được trong ngày 01/08 sẽ mang `date = 01/08`, nằm ngoài event y như reward thường.
- **Không thể tự khắc phục bằng tay.** Dữ liệu trải trên 5 collection có quan hệ phụ thuộc lẫn nhau (`content-flow` → `content-analytic-daily` → `event-reward` → `event-analytic-daily` / `user-event-analytic-daily` → `user-event`). Sửa tay một collection sẽ bị các job định kỳ ghi đè hoặc đánh dấu sai.

> **Đính chính** — bản đầu khẳng định chắc "ngày tràn không sinh `event-reward`". Không suy ra được từ code.
> Cặp `startAt`/`endAt` trong điều kiện lọc là **của schema**, không phải của event
> (`internal/service/event_schema.go:200-208`):
>
> ```go
> if !isExtended {
>     cond["endAt"]   = bson.M{"$gte": doc.Date}
>     cond["startAt"] = bson.M{"$lte": doc.Date}
> }
> ```
>
> `EventSchemaRaw` có `StartAt`/`EndAt` riêng (`internal/model/mg/event_schema.go:26-28`) và không có chỗ
> nào trong code ràng buộc `schema.endAt <= event.endAt`. Schema phủ quá ngày kết thúc event thì ngày
> tràn **có** sinh reward. Đây là một trong hai số liệu đang chặn ở mục dưới.

Ngoài ra, khi migration được chạy trên production, người vận hành **không có cách nào theo dõi nó đang chạy tới đâu**. Hệ thống hiện chỉ ghi log ra container; muốn biết migration đã đụng bao nhiêu content, dừng ở bước nào, hay vì sao bị chặn thì phải xin quyền vào container đọc log hoặc query thẳng database — cả hai đều không khả thi với người vận hành. Với một migration ghi vào 5 collection có quan hệ phụ thuộc, chạy mù như vậy là rủi ro không chấp nhận được.

Điểm mấu chốt: nếu chỉ sửa `content-analytic-daily` mà không xử lý `content-flow` gốc, mọi lần recompute sẽ **tái tạo lại** doc ngày 01/08, và job `Audit()` sẽ đánh doc ngày 31/07 là `auditStatus = invalid` với `codeReason = VIEW_INVALID` vì `view.value` không còn khớp tổng `content-flow` của ngày đó.

> **Bổ sung** — `Audit()` chỉ quét doc có `auditStatus = pending` và `date < hôm nay`
> (`internal/service/content_analytic_daily.go:318-321`). Doc ngày đích đang ở `valid` hoặc `completed` thì
> `Audit()` **không đụng tới**, nên rủi ro `VIEW_INVALID` chỉ có thật khi doc đang `pending`.

## Chặn code — hai số liệu chưa có

Chưa trả lời được hai câu này thì **chưa chốt được thiết kế**, và không nên bắt đầu code phần reward.
Ai có quyền đọc production chạy hai truy vấn dưới rồi điền kết quả vào đây.

**Câu 1 — ngày 01/08 event đó có reward không, loại gì, đã chi chưa?**

```js
db.getCollection('event-reward').aggregate([
  { $match: { event: ObjectId('<eventId>'),
              date: ISODate('2026-08-01T00:00:00+07:00') } },
  { $group: { _id: { type: '$type', status: '$status', isTransfer: '$isTransfer' },
              soDong: { $sum: 1 },
              tongCash: { $sum: '$cash' },
              tongView: { $sum: '$statistic.totalView' } } },
  { $sort: { soDong: -1 } },
])
```

Kết quả quyết định điều gì:
- **Không có dòng nào** → Problem Statement giữ nguyên hướng "creator mất tiền", migration chỉ cần gộp view.
- **Có dòng, tất cả `isTransfer` khác `true`** → bài toán là "chuyển tiền về đúng ngày", tổng cash phải KHÔNG đổi.
- **Có dòng `isTransfer = true`** → tiền đã ra khỏi hệ thống, migration **chặn**, giao lại vận hành.

**Câu 2 — có dữ liệu từ 02/08 trở đi không?**

```js
db.getCollection('content-analytic-daily').aggregate([
  { $match: { event: ObjectId('<eventId>'),
              date: { $gt: ISODate('2026-08-01T00:00:00+07:00') } } },
  { $group: { _id: '$date', soDoc: { $sum: 1 } } },
  { $sort: { _id: 1 } },
])
```

Có kết quả nghĩa là tràn nhiều hơn một ngày. Điều kiện chặn số 4 sẽ chặn sạch và migration này **không dùng
được** — phải mở rộng phạm vi trước, đừng code rồi mới phát hiện.

## Solution

Bổ sung một **migration có kiểm soát**, chạy theo từng event do người vận hành chỉ định, thực hiện gộp toàn bộ dữ liệu của ngày tràn về ngày kết thúc thật của event.

Từ góc nhìn người vận hành:

- Gọi một endpoint migration với `eventId`, ngày nguồn (01/08/2026) và ngày đích (31/07/2026).
- Mặc định chạy ở chế độ **dry-run**: hệ thống chỉ báo cáo sẽ đụng bao nhiêu doc ở mỗi collection, tổng view/cash của event trước và sau khi gộp, và danh sách content bị ảnh hưởng — không ghi gì vào DB.
- Khi số liệu dry-run đã được đối chiếu và chấp nhận, chạy lại với `dryRun=false` để thực thi.
- Sau khi chạy, event chỉ còn dữ liệu tới đúng ngày `endAt`; lượt view của ngày tràn đã được cộng vào ngày cuối cùng; **reward của ngày tràn được chuyển sang ngày cuối** (cộng dồn hoặc đổi ngày, xem mục Reward bên dưới) nên tiền nằm đúng kỳ; báo cáo event khớp lại.

> **Đính chính** — bản đầu ghi "`event-reward` của ngày cuối được **tính lại**", tức gọi
> `UpdateRewardTypeByStatisticContent`. Bỏ hướng đó. Hàm ấy tính `totalView = doc.View.Value - view.Completed`
> rồi phụ thuộc tiếp vào schema có phủ ngày đích không, `Quantity.Remaining` còn không, `content.Status` là gì.
> Ba biến số đó đều có thể làm tiền **bốc hơi hoặc nhân đôi** mà không ai thấy. Chuyển sang **cộng thẳng số của
> reward ngày nguồn vào reward ngày đích**: xác định được, kiểm chứng được, và cho một bất biến in ra được —
> **tổng cash của event trước và sau khi gộp phải bằng nhau**.
- Việc gộp lấy số từ `content-analytic-daily` của hai ngày và cộng lại, không phụ thuộc vào `content-flow` — nên chạy sớm hay muộn so với ngày sự cố đều cho cùng kết quả.

Migration **tự chặn** những tình huống nó không đủ an toàn để xử lý, thay vì cố chạy và làm hỏng thêm dữ liệu.

Song song với đó, mỗi lần trigger migration sinh ra một **bản ghi job** trong collection `migration-jobs` — giống cơ chế đã có bên ambassador. Người vận hành gọi endpoint, nhận về ngay một `jobId`, rồi poll qua HTTP để xem migration đang chạy tới record thứ mấy trên tổng bao nhiêu, kết quả từng bucket (đã xử lý / bỏ qua / lỗi), lý do của những row bị bỏ qua hay lỗi, và toàn bộ báo cáo dry-run khi job kết thúc. Không cần quyền truy cập database, không cần đọc log container. Lịch sử các lần chạy được giữ lại vĩnh viễn để trace về sau.

## User Stories

1. Là người vận hành, tôi muốn chỉ định đúng một `eventId` cho mỗi lần chạy migration, để phạm vi tác động luôn nằm trong tầm kiểm soát của tôi.
2. Là người vận hành, tôi muốn migration mặc định ở chế độ dry-run, để không bao giờ vô tình ghi vào production chỉ vì gõ thiếu tham số.
3. Là người vận hành, tôi muốn đọc được số doc sẽ bị đụng ở từng collection trong báo cáo dry-run của job, để ước lượng được quy mô thay đổi trước khi quyết định.
4. Là người vận hành, tôi muốn báo cáo dry-run của job chứa tổng view và tổng cash của event trước và sau khi gộp, để đối chiếu với số liệu tôi đang có trên dashboard.
5. Là người vận hành, tôi muốn báo cáo dry-run của job liệt kê danh sách content bị ảnh hưởng, để kiểm tra thủ công vài mẫu trước khi thực thi.
6. Là người vận hành, tôi muốn migration tự backup `content-analytic-daily` của cả ngày nguồn lẫn ngày đích (và `content-flow` ngày nguồn nếu còn) trước khi ghi, để có đường lùi nếu kết quả không như mong đợi.
7. Là người vận hành, tôi muốn migration dừng lại và báo lý do rõ ràng khi event đang bật `ExtendedPeriod`, vì ngày ghi nhận của event đó được dịch chuyển và việc gộp sẽ cho kết quả sai.
8. Là người vận hành, tôi muốn migration dừng lại khi ngày đích không phải là `endAt` của event, để tránh gộp nhầm sang một ngày giữa kỳ.
9. Là người vận hành, tôi muốn migration dừng lại khi ngày nguồn không liền kề ngay sau ngày đích, vì trường hợp đó không phải là lỗi tràn ngày và cần xử lý riêng.
10. Là người vận hành, tôi muốn migration dừng lại khi event còn dữ liệu ở ngày sau ngày nguồn, vì đó là tràn nhiều hơn một ngày và migration này không xử lý được.
11. Là người vận hành, tôi muốn migration dừng lại khi phát hiện `event-reward` ở ngày nguồn **đã chi** — nghĩa là `isTransfer = true` hoặc có `transferId`, KHÔNG phải `status = completed` — để không bao giờ tạo ra lệch với tiền đã chuyển.
12. Là người vận hành, tôi muốn migration báo rõ "không có gì để gộp" khi event không có doc nào ở ngày nguồn, để biết mình đã chọn nhầm event.
13. Là người vận hành, tôi muốn endpoint migration được bảo vệ bằng cơ chế xác thực và key migration sẵn có, để không ai ngoài đội vận hành gọi được.
14. Là người vận hành, tôi muốn mỗi lần trigger migration trả về ngay một `jobId` thay vì treo request cho tới khi chạy xong, để không bị timeout khi event có nhiều content.
15. Là người vận hành, tôi muốn poll tiến độ của một job qua HTTP bằng `jobId`, để biết migration đang xử lý record thứ mấy trên tổng bao nhiêu.
16. Là người vận hành, tôi muốn job ghi lại `dryRun`, `event`, `overflowDate`, `mergeIntoDate` đã truyền vào (kể cả khi hệ thống tự suy ra từ `endAt`), để đối chiếu lại đúng tham số của lần chạy đó khi rà soát sau này.
17. Là người vận hành, tôi muốn job ghi lại lý do bị chặn của guard, để biết vì sao migration không thực thi mà không phải đọc log container.
18. Là người vận hành, tôi muốn job giữ lại danh sách mẫu các row bị lỗi kèm lý do, để debug được vài trường hợp đầu tiên ngay trên phản hồi HTTP.
19. Là người vận hành, tôi muốn job chuyển sang trạng thái `failed` kèm thông báo lỗi khi migration panic giữa chừng, để phân biệt được "chạy xong" với "chết giữa đường".
20. Là người vận hành, tôi muốn xem danh sách các job gần nhất, lọc theo loại migration, để nắm được lịch sử đã chạy những gì trên production.
21. Là người vận hành, tôi muốn báo cáo dry-run (số doc theo collection, tổng view/cash trước–sau, danh sách content bị ảnh hưởng) được lưu ngay trong job record, để đọc lại kết quả một lần chạy cũ mà không phải chạy lại.
22. Là người vận hành, tôi muốn job bị guard chặn mang một trạng thái riêng chứ không phải `done`, để không nhầm "bị chặn, chưa ghi gì" với "đã chạy xong".
23. Là người vận hành, tôi muốn hệ thống từ chối trigger khi đã có một job cùng loại đang chạy trên cùng event, để hai lần chạy không giẫm lên nhau.
24. Là creator tham gia event, tôi muốn lượt view sinh ra trong khoảng thời gian ghi tràn vẫn được tính thưởng, để không bị thiệt vì lỗi kỹ thuật của hệ thống.
25. Là creator, tôi muốn tổng tiền thưởng của tôi **không đổi** sau khi migration chạy, chỉ đổi ngày ghi nhận, để tôi không bị mất cũng không được trả thừa vì một thao tác kỹ thuật.
26. Là creator, tôi muốn thống kê cá nhân của tôi trong event (`user-event`) được cập nhật lại sau khi gộp, để trang thống kê không mâu thuẫn với số tiền tôi nhận.
27. Là admin, tôi muốn báo cáo event không còn cột ngày nằm ngoài khoảng `startAt`–`endAt`, để biểu đồ đọc đúng vòng đời chiến dịch.
28. Là admin, tôi muốn `event-analytic-daily` của ngày kết thúc phản ánh đúng tổng đã gộp, để số liệu tổng hợp của event khớp với tổng các ngày.
29. Là admin, tôi muốn `user-event-analytic-daily` của ngày kết thúc được tính lại, để báo cáo theo từng creator khớp với báo cáo cấp event.
30. Là admin, tôi muốn doc analytic của ngày tràn được tính lại rồi mới xóa nếu rỗng, để cột ngày đó không bị luồng recompute upsert quay lại sau này.
31. Là admin, tôi muốn được báo rõ khi ngày tràn còn content thật (content có `date` sau `endAt`), để biết đó là vấn đề khác cần xử lý riêng chứ không bị xóa lặng lẽ.
32. Là partner, tôi muốn số liệu đối soát của event khớp giữa dashboard và file export, để không phải tranh luận về con số khi quyết toán.
33. Là developer, tôi muốn phần tính lại `view/like/comment` theo cấu trúc `{begin, value, end}` được tách thành module thuần, để kiểm chứng bằng unit test mà không cần dựng mongo.
34. Là developer, tôi muốn toàn bộ điều kiện chặn được gom vào một module thuần, để thêm điều kiện an toàn mới mà không phải đọc lại luồng ghi DB.
35. Là developer, tôi muốn migration tái sử dụng các hàm recompute sẵn có thay vì tự viết lại công thức thống kê, để kết quả luôn nhất quán với luồng chạy hằng ngày.
36. Là developer, tôi muốn sau khi migration chạy xong, job `Audit()` không đánh doc ngày kết thúc là `VIEW_INVALID` — hoặc vì flow đã được dịch cho khớp, hoặc vì doc đã ở `auditStatus = completed` nên `Audit()` bỏ qua.
37. Là developer, tôi muốn migration ghi log tiến trình theo từng bước, để theo dõi được khi chạy trên production và biết dừng ở đâu nếu lỗi.
38. Là developer, tôi muốn migration là idempotent — chạy lại lần hai trên cùng event không làm thay đổi thêm dữ liệu, để an toàn khi phải chạy lại vì nghi ngờ.

> **Bổ sung** — tám story dưới đây thuộc đợt rà soát 2026-08-20, sinh ra từ việc đổi cách xử lý reward.

39. Là người vận hành, tôi muốn migration **dừng lại** khi ngày tràn có `event-reward` đã chi (`isTransfer = true` hoặc có `transferId`), để không bao giờ tạo lệch với số tiền đã chuyển đi.
40. Là người vận hành, tôi muốn báo cáo dry-run cho tôi thấy **tổng cash của event trước và sau bằng nhau**, để tôi có đúng một con số để nhìn mà quyết định chạy thật hay không.
41. Là người vận hành, tôi muốn báo cáo dry-run nói rõ **gộp từ ngày nào vào ngày nào**, kèm `endAt` của event, để không bao giờ chạy ngược chiều.
42. Là kế toán đối soát, tôi muốn mỗi reward bị migration đụng vào đều mang **con trỏ ngược về reward gốc và ngày gốc**, để tra lại được biên bản đối soát cũ đang trỏ vào ngày 01/08.
43. Là creator đạt mốc thưởng, tôi muốn reward milestone của tôi được **chuyển sang ngày kết thúc event** chứ không bị xóa, để tôi không mất mốc đã đạt.
44. Là developer, tôi muốn migration **không bao giờ xóa** reward milestone, vì cơ chế chống trùng của hệ thống dựa trên "đã tồn tại một dòng"; xóa đi thì lần kiểm tra sau tạo lại với ngày hôm nay — đúng cái lỗi đang sửa.
45. Là người vận hành, tôi muốn migration **dừng lại** khi phát hiện `content-analytic-daily` bị trùng ở cặp (content, ngày), để không gộp nhầm rồi xóa mất một bản.
46. Là người vận hành, tôi muốn tham số ngày có tên **không trùng nghĩa với khoảng ngày** của các endpoint migration khác, để không gõ ngược nguồn với đích.

## Implementation Decisions

### Ngữ nghĩa dữ liệu đã xác lập

- `content-analytic-daily` lưu `view`, `like`, `comment` dưới dạng `{begin, value, end}`, trong đó `begin` là `end` của ngày trước đó, `value` là lượng phát sinh **trong ngày**, `end = begin + value`. Do đó gộp hai ngày là **cộng dồn `value`**, không phải lấy giá trị lớn hơn.
- **Nguồn gộp là `content-analytic-daily`, không phải `content-flow`.** Migration đọc doc của ngày nguồn và ngày đích, cộng `value` của hai ngày rồi ghi thẳng xuống doc ngày đích. Không gọi lại luồng recompute từ flow.
- Lý do: `internal/service/content_analytic_daily.go` — hàm `Update()` không cộng dồn mà **aggregate lại toàn bộ `content-flow` của ngày đó rồi ghi đè `view.value`**. Trong khi `DeleteContentFlow()` (chạy ở cuối mỗi lần `Audit()`) backup và xóa `content-flow` của mọi doc có `auditStatus = valid` và `date <= now - 30 ngày`. Nếu tới lúc chạy migration mà flow ngày đích đã bị dọn, recompute sẽ tính ra tổng chỉ từ phần flow còn lại rồi ghi đè — **toàn bộ view gốc của ngày đích biến mất**. Không phải thiếu, mà là mất. Gộp từ `content-analytic-daily` không có rủi ro này vì doc analytic được giữ vĩnh viễn.
- `TotalManualView` cũng phải cộng dồn hai ngày. Nếu để `Update()` recompute, manual view của ngày nguồn bị nuốt: nhánh update chỉ giữ `TotalManualView` của doc ngày đích, còn nhánh insert set thẳng về `0`.
- `content-flow` chỉ còn một vai trò: giữ cho `Audit()` không đánh nhầm. Nó **không** tham gia vào việc tính số.
- **Ba trạng thái của một `event-reward` là ba việc khác nhau.** Đây là chỗ bản đầu hiểu sai, kéo theo điều kiện chặn sai:

  | Mốc | Ai đặt | Nghĩa |
  |---|---|---|
  | `status = pending` | `UpdateRewardTypeByStatisticContent` suy từ `content.Status` (`event_schema.go:277-284`) | Tiền dự kiến |
  | `status = completed` | `pkg/admin/service/reconciliation_running.go:261` | **Đã đối soát**, chốt số với partner. Chưa trả đồng nào |
  | `isTransfer = true` + `transferId` | `pkg/admin/service/transfer.go:93-108` | **Đã chi** |

  ```go
  // transfer.go — quét CashFlow của một transfer rồi đóng dấu ngược lên reward
  }, bson.M{"$set": bson.M{
      "transferId": d.TransferId,
      "isTransfer": true,
      "updatedAt":  time.Now(),
  }})
  ```

  Suy ra: `view.Completed` mà `GetStatisticContentIsRewardInDay` trả về là view **đã đối soát**, không phải
  đã chi. Điều kiện chặn "đã chi" phải bám `isTransfer` / `transferId`, không được bám `status = completed`.

- **Khóa nhận dạng một `event-reward` by-statistic** là bộ năm, lấy đúng từ `rewardCond` của code (`event_schema.go:291-299`):

  ```go
  rewardCond := bson.M{
      "user":              content.User,
      "schema._id":        schema.ID,
      "options.contentId": content.ID,
      "status":            reward.Status,
      "date":              doc.Date,
  }
  ```

  Dùng `schema._id` chứ không phải `type`: một event có thể có nhiều schema cùng type `by-statistic` khác
  nguồn, khác đơn giá. Và `status` nằm trong khóa — reward đổi status là hàm mất dấu nó rồi **chèn dòng mới**.

- **Reward milestone có khóa khác hẳn.** `by-view-milestone` (`event_schema.go:97-125`) và
  `by-content-milestone` (`event_schema.go:438-460`) đều:
  - `Options = &modelmg.EventRewardOpts{}` — **rỗng, không có `contentId`**;
  - `Date = util.TimeStartOfDayInHCM(time.Now())` — ngày job chạy, không phải ngày phát sinh view;
  - chỉ claim **một lần** cho mỗi (user, event, schema): `if totalClaimed := CountByCondition(...); totalClaimed >= 1 { return }`.

  Vì mỗi bộ chỉ có đúng một dòng nên **không tồn tại dòng ở ngày đích để cộng vào** — nhánh duy nhất đúng
  là đổi `date`. Và vì cơ chế chống trùng dựa trên "đã có một dòng", **xóa dòng milestone là tự tạo lại sự cố**:
  lần kiểm tra sau sẽ sinh lại với `date = hôm nay`.

- **Ngưỡng milestone không bị migration làm xê dịch.** Nó tính từ `userEvent.Statistic.<nguồn>.View.Completed`
  — view **đã đối soát**. Gộp view không đụng trạng thái đối soát, nên gộp không làm ai vừa đủ ngưỡng mà đạt
  thêm mốc mới, cũng không làm ai tụt mất mốc đã đạt. Chỉ dời ngày dòng đã có, không tính lại ngưỡng.
- `UpdateAnalyticEventDaily` và `UpdateAnalyticUserEventDaily` aggregate từ `content` và `event-reward`, cũng không đọc `content-flow`. Toàn bộ chuỗi recompute phía sau vì thế an toàn.
- Hai hàm đó match theo `content.date` / `event-reward.date` và ghi bằng **upsert**. `content.date` là ngày đăng bài, migration không thay đổi nó. Doc analytic của ngày nguồn vẫn phải **recompute rồi mới xóa nếu rỗng**, không xóa mù — nhưng lý do khác với bản đầu.

> **Đính chính** — bản đầu nói "xóa mù thì lần recompute sau upsert nó trở lại". Không đúng với các job thật.
> Cả `UpdateAnalyticOldEventDaily` (`internal/service/event.go:1046`) lẫn `UpdateUserEventAnalyticDaily`
> (`pkg/admin/service/shedule.go:406`) đều duyệt **các doc đang tồn tại** rồi recompute từng cái, chứ không
> duyệt một dải ngày:
>
> ```go
> cond = bson.M{"event": event.ID, "date": bson.M{"$lt": q.FromAt}}
> _ = daomongodb.EventAnalyticDailyDAO().GetShare().Find(ctx, ..., cond)(&eventDaily)
> for _, ed := range eventDaily { /* recompute đúng ed.Date */ }
> ```
>
> Doc đã xóa thì không job nào ghé lại. Nên xóa mù **không** bị upsert quay về — nhưng vẫn giữ thứ tự
> "recompute trước, xóa sau", vì lý do thật là: chỉ sau khi recompute mới biết ngày nguồn còn **content thật**
> (`content.date` = ngày nguồn) hay đã rỗng. Xóa mù là giấu mất thông tin đó.
- Ngày tràn là ngày cuối cùng của event, không có doc nào phía sau, nên `begin` của các ngày kế tiếp không cần dịch chuyển dây chuyền. Kể cả khi có doc phía sau, chuỗi vẫn liên tục: `end` mới của ngày đích (`begin₃₁ + v₃₁ + v₀₁`) đúng bằng `end` cũ của ngày nguồn.

### Module

- **MergeOverflowDayPlanner** — module sâu, thuần logic, không phụ thuộc DB. Đầu vào: danh sách `content-analytic-daily` của ngày nguồn và ngày đích. Đầu ra: một `MergePlan` mô tả danh sách content bị ảnh hưởng, giá trị `{begin, value, end}` và `totalManualView` mới cho doc ngày đích của từng content, và tổng view trước/sau. Đây là nơi chứa toàn bộ số học của migration — và cũng là **nguồn ghi thật**, không chỉ dự báo cho dry-run: Executor ghi thẳng những con số Planner tính ra.
- **MergeOverflowDayGuard** — module sâu, thuần logic. Đầu vào: `EventRaw` cùng snapshot analytic/reward của ngày nguồn và ngày đích. Đầu ra: danh sách lý do abort. Các điều kiện chặn:
  - event bật `ExtendedPeriod`;
  - ngày đích khác `endAt` của event;
  - ngày nguồn không liền kề ngay sau ngày đích;
  - **tồn tại `content-analytic-daily` của event ở ngày sau ngày nguồn** — nghĩa là tràn nhiều hơn một ngày, ngoài phạm vi migration này;
  - **tồn tại `event-reward` ở ngày nguồn ĐÃ CHI** — `isTransfer = true` hoặc có `transferId`. Đây không còn là điều kiện phòng thủ hình thức mà là nhánh chính: tiền đã ra khỏi hệ thống, sửa số là lệch với chứng từ chi;
  - **tồn tại `content-analytic-daily` trùng ở cặp (content, ngày)** ở ngày nguồn hoặc ngày đích;
  - không có dữ liệu nào ở ngày nguồn.

> **Đính chính** — điều kiện "đã chi" ở bản đầu ghi là "`isTransfer` hoặc trạng thái completed". Bỏ vế
> `completed` đi: đó là **đã đối soát**, chưa chi (xem bảng ba trạng thái ở trên). Giữ vế `completed` thì
> migration bị chặn oan trên mọi event đã đối soát xong — tức gần như mọi event đã kết thúc.

> **Bổ sung** — điều kiện trùng doc là điều kiện mới. Trùng ở cặp (content, ngày) là chuyện **đã xảy ra thật**
> trong hệ thống này: index `{content, date}` của `content-analytic-daily` không unique
> (`internal/module/database/mongodb/index.go:157-166`), và đã có sẵn một migration chuyên gỡ trùng đúng cặp
> khóa đó (`/migration/remove-duplicate/content-analytic-daily`). Planner gom theo `content` nên gặp hai doc
> cùng ngày sẽ lấy một bỏ một, trong khi bước xóa `DeleteMany` theo `{event, date}` xóa cả cụm — mất view,
> không cảnh báo.
>
> **Không được chạy migration gỡ trùng sẵn có như bước chuẩn bị.** Nó không phải dedup trung tính: với mỗi
> cụm trùng có reward, nó ghi đè `view.value` thành `TotalViewCompleted` rồi **reject sạch mọi reward
> `pending`** của cặp (content, date) đó (`pkg/admin/service/migration.go:632-660`):
>
> ```go
> primaryDoc.View = modelmg.ContentAnalyticDaily{
>     Begin: primaryDoc.View.Begin,
>     Value: rewardReport.TotalViewCompleted,      // cắt bỏ phần chưa đối soát
>     End:   primaryDoc.View.Begin + rewardReport.TotalViewCompleted,
> }
> ...
> "$set": bson.M{"status": constants.StatusRejected, "note_migration": "migration_content_analytic_v2"}
> ```
>
> Chạy nó trước là tự tay hủy đúng phần tiền đang định cứu. Gặp trùng thì **báo cáo và dừng**, xử lý riêng.
- **MergeOverflowDayExecutor** — module mỏng, chỉ điều phối I/O: backup → ghi doc `content-analytic-daily` ngày đích theo `MergePlan` và xóa doc ngày nguồn → xử lý `content-flow` cho `Audit()` → **chuyển reward ngày nguồn sang ngày đích** → xóa và recompute `event-analytic-daily` cùng `user-event-analytic-daily`. Không chứa công thức tính toán.
- **MergeOverflowDayRewardPlanner** — module sâu, thuần logic, tách khỏi Executor. Đầu vào: danh sách `event-reward` của hai ngày. Đầu ra: danh sách hành động, mỗi hành động thuộc đúng một trong ba nhánh:

  | Loại reward | Có dòng ngày đích cùng `schema._id` + `status`? | Hành động |
  |---|---|---|
  | `by-statistic` | Có | **Cộng dồn** vào dòng ngày đích, zero dòng ngày nguồn, gắn con trỏ liên kết |
  | `by-statistic` | Không | **Đổi `date`** sang ngày đích, giữ nguyên số, ghi lại ngày gốc |
  | `by-view-milestone` / `by-content-milestone` | Luôn là không (mỗi bộ chỉ một dòng) | **Đổi `date`** sang ngày đích. Không cộng, không xóa |

  Cộng dồn nghĩa là `statistic.totalView += ...`, `totalCashView += ...`, tương tự cho like/comment/milestone, và `cash += ...`. Không gọi lại hàm recompute nào.

  Nhánh đổi ngày được chọn thay vì "cộng vào một dòng khác schema" vì dòng kết quả phải còn giải thích được: `cash` của một reward phải suy ra được từ `schema.cashReward` của chính nó. Trộn hai schema vào một dòng là làm mất khả năng đó.

- **Trường truy vết trên `event-reward`** — thêm mới, để đối soát cũ trỏ vào ngày nguồn vẫn lần ra được tiền đi đâu. Bốn trường:
  - `mergedIntoRewardId` — đặt trên dòng ngày nguồn, trỏ sang dòng ngày đích (nhánh cộng dồn);
  - `mergedFromRewardIds` — đặt trên dòng ngày đích, liệt kê các dòng đã gộp vào nó;
  - `originalDate` — ngày gốc, dùng cho cả nhánh cộng dồn lẫn nhánh đổi ngày;
  - `migrationJobId` — lần chạy nào gây ra, nối thẳng vào job record.

> **Bổ sung** — một cảnh báo vận hành cho nhánh đổi ngày: transfer quét reward theo `date < EndAt` của kỳ chi
> (`pkg/admin/service/transfer.go:99`). Reward dời từ 01/08 về 31/07 sẽ rơi vào kỳ chi khác — đúng ý đồ, nhưng
> kỳ thanh toán kế tiếp sẽ nhặt nó lên. Vận hành cần biết trước, đừng để bất ngờ khi đối soát kỳ sau.
- **MigrationJob** — hạ tầng theo dõi tiến độ, port nguyên pattern từ ambassador (`internal/model/mg/migration_job.go`, `internal/module/database/mongodb/dao/migration_jobs.go`, `pkg/admin/service/migration_job.go`). Gồm: model `MigrationJobRaw` + DAO trỏ vào collection `migration-jobs`, và bộ helper `newMigrationJob` / `saveMigrationJob` / `recordFailedSample` / `recordSkippedSample` / `finishMigrationJob`. Executor chỉ gọi các helper này; nó không tự viết logic ghi job.
- **Handler / Router / Validation** — module mỏng, bám theo pattern nhóm route migration hiện có, dùng lại middleware `RequiredLogin` và `CheckKeyMigration`.

### API contract

- Endpoint trigger trong nhóm route migration: `GET /migration/merge-overflow-day`.
- Tham số: `event` (bắt buộc), `overflowDate` (ngày tràn — nguồn, **tùy chọn**), `mergeIntoDate` (ngày gộp về — đích, **tùy chọn**), `dryRun` (mặc định `true`).
- Key migration đi ở **header `Api-Key`**, không phải query string.

> **Đính chính** — bản đầu đặt tên hai tham số ngày là `fromDate`/`toDate` (Tech Spec ghi `fromAt`/`toAt`).
> Hai chuyện phải sửa:
>
> **(a) Hai tài liệu gọi khác tên nhau** cho cùng một thứ. Chốt một bộ: `overflowDate` / `mergeIntoDate`.
>
> **(b) `fromAt`/`toAt` trong repo này luôn có nghĩa "khoảng ngày".** `mgquery.CommonQuery` có
> `AssignFromToAtWithField(&cond, "date")` sinh ra `$gte`/`$lte`, và **mọi** endpoint trong nhóm `/migration`
> hiện có đều dùng `MigrationQuery` với đúng nghĩa đó. Đặt một cặp nguồn→đích ngay cạnh chúng là mời người
> ta gõ `fromAt=31/07&toAt=01/08` theo phản xạ — tức chạy ngược chiều, gộp ngày kết thúc vào ngày tràn.
>
> **Hai ngày để tùy chọn.** Guard vốn đã ép `mergeIntoDate` phải đúng bằng đầu ngày `event.endAt` và
> `overflowDate` phải là ngày liền sau, nên cả hai suy ra được từ event. Không truyền thì hệ thống tự suy;
> có truyền mà lệch thì chặn và in ra cặp hệ thống tự suy để đối chiếu. Thêm một điều kiện chặn nữa:
> `overflowDate <= mergeIntoDate` là chặn ngay, báo "ngày tràn phải nằm sau ngày kết thúc event".
- Mỗi lần gọi xử lý đúng một event. Không hỗ trợ chạy hàng loạt.
- Migration chạy **nền** ở cả hai chế độ — dry-run cũng async, không có nhánh đồng bộ riêng. Endpoint trigger trả về ngay `jobId` cùng tham số đã nhận. Trường hợp guard chặn vẫn sinh job record với status `aborted` kèm lý do, để lưu vết lần thử.
- Trigger trả lỗi ngay (không sinh job) khi đã tồn tại một job `merge-overflow-day` ở trạng thái `running` trên cùng `eventId` — xem mục chống chạy song song bên dưới.
- Hai endpoint theo dõi, port từ ambassador, đặt trong **group riêng** `/migration-jobs` chỉ gắn `RequiredLogin`:
  - `GET /migration-jobs?type=&limit=` — danh sách job mới nhất, sắp xếp theo `startedAt` giảm dần, lọc theo `type`, mặc định 20 bản ghi.
  - `GET /migration-jobs/:id` — chi tiết một job, dùng lại `routevalidation.Common().ParamID`. Trả 404 khi không tồn tại, phân biệt rõ với lỗi DB.
- Lý do tách group: ở vcreator, `CheckKeyMigration` được gắn ở cấp group `/migration` (khác ambassador chỉ có `RequiredLogin`). Nếu để endpoint job trong group đó, mỗi lần poll đều phải kèm key migration — trong khi poll là thao tác chỉ đọc, lặp liên tục. Endpoint **trigger** vẫn nằm trong `/migration` và vẫn chịu `CheckKeyMigration`.
- Báo cáo (trạng thái, lý do bị chặn, số doc bị đụng theo từng collection, tổng view và tổng cash trước/sau, danh sách content bị ảnh hưởng) nằm trong job record, đọc qua `GET /migration-jobs/:id`.
- Báo cáo phải đọc được bằng mắt, không bắt người vận hành tự ghép field. Định dạng chốt:

```
Event : "Tên event"   (endAt = 31/07/2026)
Gộp   : ngày 01/08/2026  ──vào──>  ngày 31/07/2026

                        Trước           Sau
  31/07  view          1.200.000      1.350.000
         cash         12.000.000     13.500.000
  01/08  view            150.000              0
         cash          1.500.000              0
  ------------------------------------------------
  Tổng cash event     13.500.000     13.500.000   (không đổi)

  content bị đụng           : 87
  reward by-statistic       : 62 dòng cộng dồn, 5 dòng đổi ngày
  reward milestone          : 3 dòng đổi ngày
  reward đã chi (isTransfer): 0        <- khác 0 là chặn
```

  Dòng **tổng cash không đổi** là thứ người vận hành nhìn để bấm `dryRun=false`. Lệch là dừng, không chạy.
  Riêng trường hợp ngày tràn vốn không có reward nào thì tổng cash **tăng** đúng bằng phần lẽ ra được thưởng —
  báo cáo phải nói rõ đây là tăng có chủ đích, không phải lệch.

### Migration job tracking

**Phạm vi port.** Khung và bộ helper port nguyên trạng từ ambassador — cùng tên hàm, cùng ngữ nghĩa, cùng hằng số. Phần được phép khác **năm chỗ**, liệt kê tường minh ở đây: thêm status `aborted`, gọn lại `MigrationJobParams`, thêm field `report`, thêm `skippedSamples` cùng helper `recordSkippedSample`, và đổi chữ ký `newMigrationJob`. Ngoài năm chỗ này thì bám nguyên bản.

> **Đính chính** — bản đầu ghi "đúng ba chỗ" nhưng chính nó mô tả thêm hai chỗ nữa mà không kể vào. Đối chiếu
> file gốc `ambassabor/backend/pkg/admin/service/migration_job.go`, bộ helper thật chỉ có năm hàm:
> `newMigrationJob`, `saveMigrationJob`, `recordFailedSample`, `finishMigrationJob`, cộng
> `GetMigrationJob` / `ListMigrationJobs`. **Không có `recordSkippedSample`.**
>
> Trong `ambassabor/backend/internal/model/mg/migration_job.go` cũng **không có** field `SkippedSamples`, và
> type mẫu tên là `MigrationJobFailedSample` chứ không phải `MigrationJobSample`:
>
> ```go
> type MigrationJobFailedSample struct {
>     RowID  string `bson:"rowId"  json:"rowId"`
>     Reason string `bson:"reason" json:"reason"`
> }
> ```
>
> Chỗ thứ năm: `newMigrationJob(ctx, jobType string, dryRun, preferCache bool, requested int, startedBy string)`.
> Bỏ `preferCache` và `requested` khỏi params là đổi luôn chữ ký hàm.
>
> Và câu "theo đúng quy ước gốc, skip đương nhiên của dry-run không ghi vào `skippedSamples`" đang viện dẫn
> một quy ước không tồn tại ở bản gốc. Giữ quy ước đó thì được, nhưng phải ghi là **quy ước mới của tài liệu này**.
>
> Đường dẫn ba file gốc thiếu tiền tố `backend/`. Đường đúng:
> `backend/internal/model/mg/migration_job.go`,
> `backend/internal/module/database/mongodb/dao/migration_jobs.go`,
> `backend/pkg/admin/service/migration_job.go`.

**Hạ tầng phải dựng mới ở vcreator** (chưa tồn tại):

- Hằng số `CollectionMigrationJob = "migration-jobs"` trong `internal/module/database/mongodb/collection.go`.
- Index `{type: 1, startedAt: -1}` đăng ký cùng chỗ với các index sẵn có (`internal/module/database/mongodb/index.go`), phục vụ endpoint list vốn luôn sort giảm dần theo `startedAt` và lọc theo `type`.
- Model `MigrationJobRaw` + DAO trỏ vào `GetDBShare()`, và service helper — port từ ba file gốc bên ambassador.

**Nội dung một job record:**

- Collection `migration-jobs`, giữ vĩnh viễn (không TTL) để trace lịch sử các đợt migration. Một record cho một lần trigger.
- Job type mới: `merge-overflow-day`. Mode `dry-run` hoặc `apply`, suy ra từ tham số `dryRun`.
- Status: `running` → `done` / `failed` / **`aborted`**. `aborted` là trạng thái thêm mới so với model gốc, dành riêng cho trường hợp guard chặn: job không ghi gì vào DB. Không dùng `done` cho trường hợp này — người vận hành poll thấy `done` sẽ hiểu nhầm là migration đã chạy xong.
- `startedBy` lấy từ `cc.GetCurrentUserID()` của context admin đang đăng nhập, giống cách các handler admin sẵn có đọc staff id. Lưu ý kiểu: `MigrationJobRaw.StartedBy` là `string` còn `GetCurrentUserID()` trả `primitive.ObjectID` (`internal/echo/echo.go:151`) — phải `.Hex()`.
- `params` gọn lại còn đúng những gì migration này dùng: `dryRun`, `event`, `overflowDate` (ngày tràn), `mergeIntoDate` (ngày gộp về). Hai field ngày **đặt tên mới**, không tái dùng `FromAt`/`ToAt` của model gốc — vì trong repo này cặp đó nghĩa là một khoảng, dùng lại là tự cài bẫy đọc nhầm cho người rà soát job sau này. Các field chỉ phục vụ job type của ambassador (`preferCache`, `requested`, `source`, `limit`, `syncedBefore`) và `createdSocialIds` **không port sang** — chúng vô nghĩa ở đây và chỉ làm doc khó đọc.
- `progress` là `{current, total}`. Job record được insert **trước** khi Planner dựng xong plan, nên lúc đầu `total = 0`; ngay sau khi có `MergePlan`, set `total` = số content bị ảnh hưởng rồi flush một lần. Không để `0/0` kéo dài, người poll sẽ tưởng job rỗng.
- Flush progress xuống Mongo mỗi N record (hằng số `jobFlushEvery` = 25, giữ nguyên như ambassador) để giảm IOPS.
- `stats` giữ nguyên bốn bucket của model gốc; ngữ nghĩa cho job type này: `synced` = content đã gộp và recompute xong, `submitted` = không dùng, `skipped` = content bỏ qua, `failed` = lỗi khi ghi/recompute một content. Ở chế độ dry-run, mọi content trong plan tính vào `skipped`.
- `failedSamples` và `skippedSamples` cap ở `maxFailedSamples` (20), lý do truncate ở `reasonTruncateAt` (200 ký tự), flush ngay khi append để poll thấy trong vòng dưới một chu kỳ. Theo đúng quy ước gốc, skip "đương nhiên" của dry-run **không** ghi vào `skippedSamples` — chỉ ghi skip bất thường.
- Lý do abort của guard **không** nhét vào `skippedSamples` mà nằm ở field `report.abortReasons`, đi kèm status `aborted`.
- `report` — field thêm mới, chứa báo cáo của lần chạy: danh sách lý do bị chặn, số doc bị đụng theo từng collection, tổng view và tổng cash trước/sau, danh sách content bị ảnh hưởng, và danh sách content còn mang `date` = ngày nguồn (nếu có) khiến doc analytic ngày nguồn không xóa được. Đây là thứ người vận hành đọc để quyết định có chạy `dryRun=false` hay không, và để tra lại kết quả một lần chạy cũ. Không nhét báo cáo vào `stats`.
- `finishMigrationJob` gọi trong `defer`: recover panic → status `failed` kèm `error`; nếu status đang là `aborted` thì giữ nguyên; ngược lại `done`. Flush lần cuối rồi log + gửi Telegram summary như bên ambassador (config Telegram đã có sẵn ở vcreator).
- Ghi job là **best-effort** — lỗi ghi job không làm migration dừng. Đây là observability, không phải critical path.

**Chống chạy song song.** Trước khi sinh job, trigger kiểm tra tồn tại job `type = merge-overflow-day`, `status = running`, `params.event = eventId`; nếu có thì từ chối và không sinh record mới. Hai lần chạy `dryRun=false` đồng thời trên cùng event sẽ cùng backup, cùng dịch `content-flow`, cùng recompute — kết quả không xác định. Tính idempotent nêu ở phần dưới chỉ đúng khi các lần chạy **tuần tự**.

**Job chết giữa chừng.** Một job `failed` có thể để lại trạng thái nửa vời: một phần `content-flow` đã dịch sang ngày đích, phần còn lại vẫn ở ngày nguồn. Chạy lại lúc đó, nếu backup ghi đè bản cũ thì đường lùi thật đã mất — bản backup mới chỉ còn phần chưa dịch. Vì vậy **backup gắn theo `jobId`**: mỗi lần chạy ghi ra một bộ backup riêng, không ghi đè bộ của lần trước. Trước khi chạy lại một event đã có job `failed`, người vận hành phải xem job đó để biết nó dừng ở đâu.

### Trình tự thực thi

Ở chế độ **dry-run**, luồng dừng sau khi Guard và Planner chạy xong: ghi `report` vào job record rồi kết thúc. Không backup, không thực hiện bất kỳ bước nào dưới đây. Các bước sau chỉ chạy khi `dryRun=false` và Guard không trả lý do abort nào.

1. **Backup** doc `content-analytic-daily` của event ở ngày nguồn **và ngày đích**, cùng `content-flow` của ngày nguồn nếu còn, sang collection backup sẵn có, gắn theo `jobId` của lần chạy, trước bất kỳ thao tác ghi nào. Phải backup cả doc ngày đích vì bước 2 ghi đè lên nó.
2. **`content-analytic-daily` ngày đích** — ghi thẳng giá trị từ `MergePlan`, không gọi `Update()`:
   - `view.value = value₃₁ + value₀₁`, `view.begin` giữ nguyên, `view.end = begin + value` mới. `like` và `comment` làm tương tự.
   - `totalManualView = totalManualView₃₁ + totalManualView₀₁`.
   - Với content chỉ có doc ở ngày nguồn (chưa từng có doc ngày đích): tạo doc mới cho ngày đích, `begin` lấy từ `end` của doc gần nhất trước ngày đích của cùng content, `month`/`year` set theo ngày đích.
3. **Xóa doc `content-analytic-daily` của ngày nguồn.**
4. **`content-flow`** — chỉ để `Audit()` không đánh nhầm, không tham gia tính số:
   - Nếu flow ngày đích còn nguyên: dịch `date` của flow ngày nguồn sang ngày đích. Chỉ `date` — `ContentFlowRaw` **không có** field `month`/`year`, hai field đó thuộc `content-analytic-daily`. Sau bước này tổng flow ngày đích khớp `view.value` mới nên `Audit()` đánh `valid`.
   - Nếu flow ngày đích đã bị `DeleteContentFlow()` dọn: không dịch được, set `auditStatus = completed` cho doc ngày đích để `Audit()` bỏ qua — đúng quy ước sẵn có của `DeleteContentFlow` (doc không còn flow thì đánh `completed`). Backup rồi xóa flow ngày nguồn để nó không tái sinh doc ngày nguồn ở lần crawl sau.
5. **`event-reward` — chuyển từ ngày nguồn sang ngày đích.** Không gọi `UpdateRewardTypeByStatisticContent`.
   - Quét **toàn bộ** `event-reward` của event ở ngày nguồn, không đi ké danh sách content trong `MergePlan`. Reward milestone không có `options.contentId` nên không thể tìm qua content; và có thể tồn tại reward ở ngày nguồn cho một content không có doc analytic ở ngày đó.
   - Với mỗi dòng, áp đúng một nhánh theo bảng ở mục Module: cộng dồn, hoặc đổi `date`.
   - Ghi bốn trường truy vết (`mergedIntoRewardId`, `mergedFromRewardIds`, `originalDate`, `migrationJobId`).
   - Sau khi xong toàn bộ reward của một user, gọi `Event().UpdateStatisticUserEvent(ctx, user, event)` một lần cho user đó. Hàm này aggregate lại **tất cả** reward của cặp (user, event), không lọc theo ngày (`internal/service/event.go:524`), nên gọi sau cùng là đủ để `user-event` khớp lại — **không cần bước riêng**. Gọi tiếp `Content().UpdateCashStatistic` và `User().UpdateStatistic` cho các content bị đụng.

> **Đính chính** — bản đầu gọi `UpdateRewardTypeByStatisticContent` cho ngày đích và coi hành vi "insert một
> reward mới cho phần chênh" là mong muốn. Bỏ cả hai. Ba lý do, đều đọc được từ `event_schema.go:173-325`:
>
> **(a) Hàm đó có thể nuốt mất tiền.** Nếu schema đã hết suất thì nó bỏ qua thẳng, không sinh reward nào:
>
> ```go
> if !schema.Quantity.IsUnlimited && schema.Quantity.Remaining <= 0 {
>     if !isExtended { continue }
> }
> ```
>
> **(b) Hàm đó phụ thuộc schema có phủ ngày đích hay không** (điều kiện `startAt`/`endAt` của schema ở trên).
> Schema phủ ngày tràn mà không phủ ngày đích thì view chuyển về nhưng tiền biến mất.
>
> **(c) Nó chỉ trừ phần đã đối soát **của đúng ngày đang tính**.** `GetStatisticContentIsRewardInDay` match
> `date = doc.Date` (`aggregate_pipeline/event_reward.go:772`), nên reward đang nằm ở ngày nguồn hoàn toàn
> vô hình với nó. Gộp view vào ngày đích rồi gọi hàm này, trong khi reward ngày nguồn vẫn còn nguyên, là
> **trả hai lần cho cùng một lượt view**.
>
> Cộng thẳng thì không dính cả ba: số xác định, tổng cash bất biến, không phụ thuộc trạng thái schema.
6. **`event-analytic-daily` và `user-event-analytic-daily`** — recompute **cả hai ngày**, không chỉ ngày đích:
   - Gọi `UpdateAnalyticEventDaily` / `UpdateAnalyticUserEventDaily` với `fromAt` = **ngày đích**, để doc ngày cuối phản ánh số đã gộp.
   - Gọi tiếp với `fromAt` = **ngày nguồn**. Không xóa mù doc ngày nguồn — nhưng lý do là để **phát hiện content thật** còn mang `date` = ngày nguồn, chứ không phải vì sợ upsert kéo nó về (xem khối đính chính ở mục Ngữ nghĩa dữ liệu).
   - Bước 5 phải chạy xong trước bước này. Hai hàm recompute aggregate từ `event-reward`, mà reward vừa được chuyển ngày ở bước 5; đảo thứ tự thì cột ngày nguồn vẫn còn tiền.
   - Sau khi recompute ngày nguồn, đọc lại doc vừa ghi:
     - Nếu số liệu về rỗng (không content, không reward ở ngày đó) → xóa doc ngày nguồn. Đây là trường hợp thường gặp: phần tràn chỉ là view của content cũ, không phát sinh content mới.
     - Nếu vẫn còn `totalContent > 0` — tức có content thật mang `date` = ngày nguồn → **giữ doc lại** và ghi vào `report` danh sách content đó. Đây là dữ liệu nằm ngoài phạm vi migration (content đăng sau `endAt`, không phải view tràn); xóa đi là giấu vấn đề, phải giao lại cho vận hành quyết định.

### Quyết định kỹ thuật khác

- Không tự động quét toàn bộ event có `endAt` là 31/07/2026. Vận hành truyền `eventId` cụ thể cho từng lần chạy.
- Event bật `ExtendedPeriod` bị chặn thay vì được xử lý, vì cơ chế dịch ngày ghi nhận của chế độ này khiến ngữ nghĩa "ngày tràn" không còn rõ ràng. Trường hợp này xử lý riêng khi phát sinh.
- Migration được thiết kế idempotent: sau lần chạy đầu, ngày nguồn không còn doc nào nên guard sẽ chặn với lý do "không có gì để gộp".
- Tái sử dụng triệt để các hàm recompute và collection backup sẵn có, không viết lại công thức thống kê.

## Testing Decisions

Test tốt là test kiểm chứng **hành vi quan sát được từ bên ngoài module**: cùng một tập đầu vào cho ra cùng một kết luận. Không test cấu trúc nội bộ, không test thứ tự lời gọi, không mock DAO để khẳng định "hàm X đã được gọi".

**Module được test:**

- **MergeOverflowDayPlanner** — nạp `content-analytic-daily` giả lập của hai ngày, kiểm chứng `MergePlan` trả về: `value` của ngày đích bằng tổng hai ngày, `end` bằng `begin` cộng `value` mới, `begin` giữ nguyên, tổng view sau bằng tổng view trước, danh sách content bị ảnh hưởng đầy đủ và không trùng lặp. Bao gồm các trường hợp biên: content chỉ có dữ liệu ở ngày nguồn (chưa từng có doc ngày đích), content chỉ có ở ngày đích (không bị đụng), `totalManualView` của hai ngày được **cộng dồn** chứ không phải lấy của một ngày, và `like`/`comment` được gộp cùng quy tắc với `view`.
- **MergeOverflowDayGuard** — mỗi điều kiện chặn một test: event bật `ExtendedPeriod`, ngày đích khác `endAt`, ngày nguồn không liền kề, ngày tràn không nằm sau ngày đích, còn dữ liệu ở ngày sau ngày nguồn, reward ngày nguồn **đã chi** (`isTransfer`/`transferId`), có doc trùng cặp (content, ngày), ngày nguồn rỗng. Thêm một test cho trường hợp hợp lệ, khẳng định không có lý do abort nào. Thêm một test khẳng định reward ngày nguồn ở `status = completed` mà **chưa** `isTransfer` thì **không** bị chặn — đây đúng là chỗ bản đầu hiểu sai, phải có test khóa lại.
- **MergeOverflowDayRewardPlanner** — nạp danh sách reward giả lập của hai ngày, kiểm chứng danh sách hành động trả về. Các case: by-statistic có dòng ngày đích cùng `schema._id` và cùng `status` thì ra hành động cộng dồn; khác `schema._id` thì ra hành động đổi ngày; khác `status` thì cũng ra đổi ngày; milestone luôn ra đổi ngày và **không bao giờ** ra hành động xóa. Và một bất biến bao trùm mọi case: **tổng cash của các hành động sau bằng tổng cash trước** — đây là assertion phải phá được code mới thấy đỏ, không phải assertion trang trí.

**Không viết test cho** MigrationJob helper, Executor, Handler, Router — chúng chỉ điều phối và sẽ được kiểm chứng bằng dry-run trên production trước khi thực thi.

**Prior art:** các file test sẵn có trong nhóm service admin, đặc biệt là những test kiểm chứng bộ lọc và bộ tính toán thuần của luồng `event-bonus-import`, và test densify của luồng export analytic event. Cùng phong cách: table-driven, không dựng mongo, dữ liệu vào ra dựng thẳng trong test.

## Out of Scope

- **Sửa nguồn sinh dữ liệu sai.** PRD này chỉ khắc phục dữ liệu đã sinh. Việc chặn hệ thống ghi tiếp sau `endAt` là hạng mục riêng — xem hai ứng viên nguyên nhân ở Problem Statement. Nếu nguyên nhân là nhánh crawl chỉ định eventId thì sự cố **lặp lại ngay trên chính event vừa sửa** mỗi lần vận hành crawl lại nó, không phải "ở event tiếp theo". Chạy migration mà không bịt nguồn là dọn xong lại bẩn.
- **Chạy hàng loạt.** Không tự động quét và xử lý mọi event bị ảnh hưởng.
- **Event bật `ExtendedPeriod`.** Bị chặn, xử lý riêng khi phát sinh.
- **Gộp nhiều hơn một ngày tràn.** Chỉ hỗ trợ ngày nguồn liền kề ngay sau ngày đích; guard chặn khi phát hiện còn dữ liệu ở ngày sau ngày nguồn.
- **Sửa lệch giữa `Audit()` và `TotalManualView`.** Lỗi sẵn có của hệ thống, không thuộc phạm vi migration này.
- **Content đăng sau `endAt`.** Nếu ngày tràn còn content thật (`content.date` sau `endAt`), migration báo cáo lại chứ không tự sửa `content.date` — đó là vấn đề khác, cùng gốc với lỗi crawler.
- **Hoàn tác tự động.** Có backup nhưng không có endpoint rollback; khôi phục làm thủ công từ collection backup.
- **Điều chỉnh tiền đã chuyển.** Nếu phát hiện reward đã chi ở ngày nguồn, migration dừng và giao lại cho vận hành.
- **Thay đổi giao diện admin.** Không có thay đổi phía frontend — job được theo dõi bằng cách gọi thẳng endpoint, không có màn hình danh sách job.
- **Hủy job đang chạy.** Không có endpoint stop; job chạy tới khi xong hoặc chết. Job `running` bị treo do process restart cũng không được tự dọn — phải sửa tay, và nó sẽ chặn lần trigger tiếp theo trên cùng event.
- **Dọn dẹp `migration-jobs`.** Không đặt TTL, không có job xóa bản ghi cũ.

## Further Notes

- Thứ tự các bước là bắt buộc. Ghi doc ngày đích (bước 2) phải đi trước khi chuyển reward (bước 5), và bước 5 phải đi trước recompute analytic cấp event (bước 6) — vì bước 6 aggregate từ `event-reward`. Trong bước 6, recompute phải đi trước khi xóa doc ngày nguồn, không phải ngược lại.
- **Chỉ số `{event, date}` đang thiếu trên `content-analytic-daily`.** Index hiện có là `content`, `{content, date}`, `event`, `user`, `partner`, `auditStatus` (`internal/module/database/mongodb/index.go:157-166`) — không có cặp `{event, date}`, trong khi **mọi** truy vấn của migration này (đếm cho guard, tìm doc hai ngày, xóa doc ngày nguồn) đều lọc đúng cặp đó. Bổ sung index này vào phần hạ tầng. `content-flow` thì đã có sẵn `{event, date}` (`index.go:110`).
- **Tên gọi đang lệch ở ba chỗ** cho cùng một việc: thư mục `gen-green/revert-view/`, tiêu đề tài liệu `merge-overflow-day`, và liên kết trong Tech Spec trỏ tới `./merge-overflow-day-event-analytic.md` (file thật tên `PRD.md`). Chưa kể commit đưa hai file này lên mang message `docs(ambassador): refine PRD and tech spec for view anomaly alerts` — tra `git log` theo tên tính năng sẽ không ra. Nên thống nhất một tên.
- Sau khi chạy, nên xác nhận job `Audit()` không đánh doc ngày đích là `VIEW_INVALID`. Nếu có, kiểm tra xem `content-flow` ngày nguồn đã được dịch hết chưa, hoặc doc đã được chuyển sang `auditStatus = completed` chưa.
- `Audit()` so `s.TotalView == d.View.Value`, trong khi `Update()` của luồng hằng ngày ghi `value = TotalView + TotalManualView`. Nghĩa là **content có manual view sẽ luôn bị đánh `VIEW_INVALID`** kể cả khi không có migration nào chạy — đây là lỗi sẵn có của hệ thống, không phải do migration gây ra. Đừng dùng nó làm tiêu chí nghiệm thu cho nhóm content này; nếu muốn xử lý thì mở hạng mục riêng.
- `content-flow` cũ hơn 30 ngày sẽ bị `DeleteContentFlow()` chuyển sang collection backup rồi xóa. Vì migration không còn tính số từ flow nên chuyện này **không làm sai kết quả gộp** — nó chỉ quyết định bước 4 đi nhánh dịch flow hay nhánh đánh `completed`. Đây chính là lý do hướng gộp từ `content-analytic-daily` được chọn thay vì gọi lại `Update()`.
- Hạ tầng `migration-jobs` bám theo ambassador, không thiết kế lại. Đọc đúng ba file gốc (`internal/model/mg/migration_job.go`, `internal/module/database/mongodb/dao/migration_jobs.go`, `pkg/admin/service/migration_job.go`) rồi port sang — job type khác nhau nhưng khung phải giống để sau này port tiếp các migration khác không phải học lại. Ba điểm được phép khác bản gốc đã liệt kê tường minh ở mục Migration job tracking; ngoài ba điểm đó thì không tự chế biến thể mới.
- Mọi mốc thời gian trong hệ thống dùng đầu ngày theo múi giờ Hồ Chí Minh. Tham số ngày truyền vào phải được chuẩn hóa về đúng mốc này trước khi so khớp, nếu không sẽ không tìm thấy doc nào.
