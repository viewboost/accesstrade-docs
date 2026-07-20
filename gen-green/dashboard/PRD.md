# PRD — Thống kê nội dung theo nguồn (Content Source Breakdown) trên Dashboard

> Nguồn: PR [#127](https://github.com/Vin-VCreator/vcreator/pull/127) — `feature/update-page-report` → `release`

## Problem Statement

Dashboard admin hiện chỉ thống kê nội dung đã duyệt theo **2 nguồn**: YouTube và TikTok. Trong khi đó hệ thống đã hỗ trợ nạp nội dung từ nhiều nguồn khác (`youtube_shorts`, `facebook`, `facebook_reels`, `instagram`, `instagram_reels`, `threads`) — các nguồn này đã tồn tại trong `constants.ContentSource*`, đã có locale label và đã được xử lý ở tầng service nội dung.

Hệ quả với người dùng:

- Admin/vận hành nhìn biểu đồ tròn và khối chú thích dưới biểu đồ thì tin rằng toàn bộ nội dung của chiến dịch chỉ đến từ YouTube + TikTok. Nội dung Facebook/Instagram/Threads bị "biến mất" khỏi báo cáo.
- Phần trăm bị tính sai về mặt logic: `percentYoutubeContent` được suy ra bằng `100 - percentTiktokContent`, nên khi tồn tại nguồn thứ ba, phần trăm YouTube bị thổi phồng lên đúng bằng tỷ trọng của tất cả các nguồn còn lại.
- Mỗi lần vận hành mở thêm một nguồn nội dung mới, cả backend lẫn admin đều phải sửa code (thêm field response, thêm block JSX, thêm màu) — chi phí thay đổi cao, dễ quên một phía.

## Solution

Thay cặp field cứng YouTube/TikTok bằng một **breakdown động theo nguồn**:

- Backend trả về mảng `contentBySource` gồm `{ source, total, percent }` cho mọi nguồn có nội dung đã duyệt trong khoảng lọc. Nguồn có tổng bằng 0 bị lược bỏ để biểu đồ không có lát cắt rỗng.
- Khóa `source` dùng đúng giá trị hằng số `constants.ContentSource*` (`tiktok`, `youtube`, `youtube_shorts`, `facebook`, `facebook_reels`, `instagram`, `instagram_reels`, `threads`), để admin map nhãn/màu/icon mà không cần thỏa thuận chuỗi riêng.
- Phần trăm được tính trên **tổng nội dung đã duyệt của tất cả nguồn**, không suy ngược từ một nguồn duy nhất.
- Admin render biểu đồ tròn và danh sách chú thích trực tiếp từ `contentBySource`. Một bảng metadata duy nhất ánh xạ `source → nhãn locale + màu`, một bảng khác ánh xạ `source → icon`. Thêm nguồn mới trên UI chỉ là thêm một dòng vào bảng metadata; nếu backend trả về nguồn chưa được khai báo, UI vẫn hiển thị được bằng khóa thô + màu/chấm tròn dự phòng thay vì vỡ layout.
- Các field cũ (`totalYoutubeContent`, `totalTiktokContent`, `percentYoutubeContent`, `percentTiktokContent`) được giữ lại và đánh dấu deprecated để client hiện hữu không gãy trong lúc chuyển đổi; riêng `percentYoutubeContent` được sửa để tính đúng thay vì lấy phần bù.

## User Stories

1. Là admin vận hành, tôi muốn xem tỷ trọng nội dung đã duyệt theo từng nguồn mạng xã hội, để tôi biết kênh nào đang đóng góp nhiều nội dung nhất.
2. Là admin vận hành, tôi muốn thấy Facebook trong báo cáo dashboard, để nội dung từ Facebook không bị bỏ sót khỏi số liệu.
3. Là admin vận hành, tôi muốn thấy Instagram trong báo cáo dashboard, để đánh giá hiệu quả kênh Instagram.
4. Là admin vận hành, tôi muốn thấy Threads trong báo cáo dashboard, để theo dõi nguồn mới mở.
5. Là admin vận hành, tôi muốn thấy YouTube Shorts tách khỏi YouTube thường, để phân biệt nội dung dạng ngắn và dạng dài.
6. Là admin vận hành, tôi muốn thấy Facebook Reels tách khỏi Facebook, để đánh giá riêng định dạng video ngắn.
7. Là admin vận hành, tôi muốn thấy Instagram Reels tách khỏi Instagram, để so sánh định dạng nội dung.
8. Là admin vận hành, tôi muốn phần trăm của các nguồn cộng lại xấp xỉ 100%, để tôi tin được con số trên biểu đồ.
9. Là admin vận hành, tôi muốn nguồn không có nội dung nào bị ẩn khỏi biểu đồ, để biểu đồ không bị nhiễu bởi các lát cắt 0%.
10. Là admin vận hành, tôi muốn mỗi nguồn có màu riêng nhận diện được theo thương hiệu nền tảng, để đọc biểu đồ nhanh mà không phải dò chú thích.
11. Là admin vận hành, tôi muốn mỗi nguồn có icon nền tảng bên cạnh số liệu, để quét thông tin bằng mắt nhanh hơn.
12. Là admin vận hành, tôi muốn các biến thể Reels/Shorts dùng lại icon nền tảng gốc, để không phải học thêm biểu tượng mới.
13. Là admin vận hành, tôi muốn hover vào lát cắt biểu đồ và thấy đúng số lượng kèm phần trăm của nguồn đó, để lấy số chính xác mà không cần rời trang.
14. Là admin vận hành, tôi muốn nhãn nguồn hiển thị theo ngôn ngữ đang chọn, để đọc báo cáo bằng tiếng Việt.
15. Là admin vận hành, tôi muốn khối chú thích dưới biểu đồ tự xuống dòng khi có nhiều nguồn, để không bị tràn hoặc chồng chữ trên màn hình hẹp.
16. Là admin vận hành, tôi muốn breakdown thay đổi theo bộ lọc thời gian/chiến dịch đang chọn, để phân tích được từng giai đoạn.
17. Là quản lý chiến dịch, tôi muốn biết nguồn nào đang chiếm tỷ trọng thấp, để quyết định đẩy ngân sách hoặc dừng kênh đó.
18. Là quản lý chiến dịch, tôi muốn số liệu chỉ tính nội dung **đã duyệt**, để không bị nhiễu bởi nội dung chờ duyệt hoặc bị từ chối.
19. Là developer backend, tôi muốn mở thêm nguồn nội dung mới mà không phải đổi cấu trúc response, để giảm rủi ro phá vỡ client.
20. Là developer frontend, tôi muốn thêm nguồn mới chỉ bằng cách khai báo nhãn/màu/icon, để không phải sửa logic render.
21. Là developer frontend, tôi muốn UI không vỡ khi backend trả về một nguồn mà FE chưa khai báo metadata, để việc triển khai lệch phiên bản giữa hai phía vẫn an toàn.
22. Là developer tích hợp bên thứ ba, tôi muốn các field thống kê cũ vẫn còn trong response một thời gian, để có thời gian chuyển sang `contentBySource`.
23. Là developer tích hợp bên thứ ba, tôi muốn biết rõ field nào đã deprecated, để lập kế hoạch di trú.
24. Là admin vận hành, tôi muốn khi chưa có nội dung nào được duyệt thì dashboard hiển thị trạng thái rỗng thay vì biểu đồ lỗi, để hiểu là chưa có dữ liệu chứ không phải hệ thống hỏng.
25. Là admin vận hành, tôi muốn tổng dòng tiền (`totalCashFlow`) vẫn hiển thị đúng sau thay đổi, để phần báo cáo tài chính không bị ảnh hưởng.

## Data Lineage — Nguồn gốc từng field trong API response

Endpoint: `GET /admin/events/report-statistic` → `EventReportStatisticResponse`.

### Chuỗi dữ liệu tổng thể (từ dưới lên)

```
collection `content` (mỗi bản ghi = 1 nội dung của creator, có `source` + `status`)
        │
        │  pipeline GetStatisticContentReportDailyBySource
        │  $match {event, user, date} → $group by "$source"
        │  totalContentApproved = đếm bản ghi có status == StatusApproved
        ▼
job UpdateAnalyticEventDaily (internal/service/event.go)
        │  ghi vào từng nhánh statistic.<sourceCamel>.totalContentApproved
        │  upsert theo khóa {event, date}
        ▼
collection `event_analytic_daily` (1 document / chiến dịch / ngày)
        │
        │  pipeline GetReportDataEventAnalytic
        │  $match {partner?, event?, date range} → $group _id:"" 
        │  totalXxxContent = $sum "$statistic.<sourceCamel>.totalContentApproved"
        ▼
ReportDataEventAnalytic (struct trung gian, tất cả là float64)
        │
        │  buildContentBySource — lọc >0, tính %, gán khóa constants.ContentSource*
        ▼
EventReportStatisticResponse.contentBySource  →  Dashboard admin
```

### Điều kiện lọc (`cond`) áp cho khối analytic

Xây trong `GetReportStatistic` trước khi chạy pipeline, theo thứ tự:

1. `Staff.AssignPartnerForStaff` — ép `partner` của staff đang đăng nhập (scope dữ liệu theo đối tác).
2. Nếu staff là root hoặc chưa gắn partner → cho phép `AssignPartnerID` từ query, tức root chọn partner tùy ý.
3. `AssignEvent` — lọc theo chiến dịch nếu query có `event`.
4. `AssignFromToAtWithField(&cond, "date")` — lọc khoảng thời gian trên field `date` của `event_analytic_daily`.

Toàn bộ `contentBySource` và các chỉ số content/view/like/comment/cash đều dùng chung `cond` này, nên luôn đồng bộ với bộ lọc trên dashboard.

### Bảng lineage từng field

| Field response | Kiểu | Nguồn trực tiếp | Nguồn gốc sâu hơn |
|---|---|---|---|
| `totalCreator` | int | `Distinct("user")` trên collection `content` với `cond` | Số creator riêng biệt có nội dung trong phạm vi lọc. **Không** lấy từ `event_analytic_daily` |
| `totalContent` | int64 | `r.TotalContent` | `$sum "$statistic.totalContentApproved"` — tổng nội dung **đã duyệt** toàn chiến dịch, không phân nguồn. Ghi bởi nhánh `GetStatisticContentReportDaily` (không group theo source) |
| `totalView` | int64 | `r.TotalViewCompleted + r.TotalViewCashback` | `$sum "$statistic.view.completed"` + `$sum "$statistic.view.cashback"`, ghi từ `GetStatisticRewardReport` trên collection `event_reward` |
| `totalLike` | int64 | `r.TotalLikeCashback + r.TotalLikeCompleted` | `$sum "$statistic.like.cashback"` + `$sum "$statistic.like.completed"`, cùng nguồn `event_reward` |
| `totalComment` | int64 | `r.TotalCommentCashback + r.TotalCommentCompleted` | `$sum "$statistic.comment.cashback"` + `$sum "$statistic.comment.completed"`, cùng nguồn `event_reward` |
| `engagement` | float64 | `round((totalLike + totalComment) / totalView * 100) / 100` | Tính tại service, bằng 0 khi `totalView == 0`. Đơn vị: phần trăm, giữ 2 chữ số |
| `totalCashReward` | float64 | `r.TotalCashPending + r.TotalCashCompleted + bonus.TotalCashCompleted + bonus.TotalCashApproved` | Hai vế đầu từ `event_analytic_daily.statistic.cash`, hai vế sau từ collection `event_bonus` |
| `totalCashPending` | float64 | `r.TotalCashPending + bonus.TotalCashApproved` | `r.TotalCashPending` ← `$sum "$statistic.cash.completed"` (xem cảnh báo lệch tên bên dưới) |
| `totalCashCompleted` | float64 | `r.TotalCashCompleted + bonus.TotalCashCompleted` | `r.TotalCashCompleted` ← `$sum "$statistic.cash.cashback"` |
| `totalCashBonus` | float64 | `bonus.TotalCash` | Pipeline `GetTotalCashBonus` trên collection `event_bonus`, dùng **cond riêng**: lọc thời gian theo field `toAt` chứ không phải `date` |
| `totalCashFlow` | float64 | `abs(getTotalCashflow(...))` | Pipeline `GetTotalCashRewardEvent` trên collection `cash_flow`, cond riêng: `action = CashFlowActionWithdraw`, lọc thời gian theo `createdAt`, **không scope theo partner** |
| `contentBySource[].source` | string | `constants.ContentSource*` | Chuỗi hằng: `tiktok`, `youtube`, `youtube_shorts`, `facebook`, `facebook_reels`, `instagram`, `instagram_reels`, `threads` |
| `contentBySource[].total` | int64 | `int64(r.Total<Source>Content)` | `$sum "$statistic.<sourceCamel>.totalContentApproved"` (bảng ánh xạ tên bên dưới) |
| `contentBySource[].percent` | float64 | `round(total / Σtotal * 100)` | Mẫu số là **tổng của 8 nguồn trong danh sách**, không phải `totalContent` |
| `totalTiktokContent` *(deprecated)* | int64 | `int64(r.TotalTiktokContent)` | Cùng nguồn với phần tử `tiktok` của `contentBySource` |
| `totalYoutubeContent` *(deprecated)* | int64 | `int64(r.TotalYoutubeContent)` | Cùng nguồn với phần tử `youtube` |
| `percentTiktokContent` *(deprecated)* | float64 | `round(r.TotalTiktokContent / r.TotalContent * 100)` | Mẫu số là `totalContent` — **khác mẫu số của `contentBySource`** |
| `percentYoutubeContent` *(deprecated)* | float64 | `round(r.TotalYoutubeContent / r.TotalContent * 100)` | Trước PR là `100 - percentTiktokContent`; PR sửa thành tính độc lập |

### Bảng ánh xạ tên nguồn qua 3 tầng

| Khóa API (`source`) | Nhánh trong `event_analytic_daily` | Field struct trung gian | Giá trị `content.source` gốc |
|---|---|---|---|
| `tiktok` | `statistic.tiktok` | `TotalTiktokContent` | `tiktok` |
| `youtube` | `statistic.youtube` | `TotalYoutubeContent` | `youtube` |
| `youtube_shorts` | `statistic.youtubeShort` | `TotalYoutubeShortContent` | `youtube_shorts` |
| `facebook` | `statistic.facebook` | `TotalFacebookContent` | `facebook` |
| `facebook_reels` | `statistic.facebookReel` | `TotalFacebookReelContent` | `facebook_reels` |
| `instagram` | `statistic.instagram` | `TotalInstagramContent` | `instagram` |
| `instagram_reels` | `statistic.instagramReel` | `TotalInstagramReelContent` | `instagram_reels` |
| `threads` | `statistic.threads` | `TotalThreadsContent` | `threads` |

Ba cách đặt tên khác nhau cho cùng một nguồn (snake_case số nhiều ở API và ở `content.source`, camelCase số ít ở document analytic, PascalCase ở struct Go). Khi mở nguồn mới phải khai báo đủ ở cả bốn cột.

### Field phía admin

| Field FE (`Dashboard.Info`) | Nguồn |
|---|---|
| `contentBySource: ContentBySource[]` | Đổ thẳng từ response, mặc định `[]` trong `initStatistic` |
| `ContentBySource.source` | Khóa dùng để tra `SOURCE_META` (nhãn locale + màu) và `SOURCE_ICON` |
| `ContentBySource.total` | Con số lớn hiển thị dưới icon và là `value` của lát cắt pie |
| `ContentBySource.percent` | Phần trăm trong ngoặc và trong tooltip |
| `totalCashFlow` | Bổ sung giá trị khởi tạo `0` (trước đây thiếu, gây `undefined` khi chưa tải xong) |

Nhãn hiển thị đến từ `key.label.*` trong `admin/src/locales`, đã có sẵn cho cả 8 nguồn trước PR — PR chỉ nối khóa nguồn với khóa locale, không thêm bản dịch mới.

## Implementation Decisions

### Tầng aggregate (MongoDB)

- Mở rộng struct dữ liệu báo cáo `ReportDataEventAnalytic` với các trường tổng nội dung đã duyệt cho từng nguồn: TikTok, YouTube, YouTube Shorts, Facebook, Facebook Reels, Instagram, Instagram Reels, Threads.
- Pipeline `GetReportDataEventAnalytic` bổ sung các phép `$sum` tương ứng trên nhánh `statistic.<source>.totalContentApproved` của collection analytic daily. Tên nhánh document dùng dạng camelCase (`youtubeShort`, `facebookReel`, `instagramReel`, `threads`) — khác với khóa `source` trả ra API (snake_case). Ánh xạ giữa hai cách đặt tên nằm gọn trong tầng service.
- Không đổi điều kiện lọc (`cond`) hiện có, nên breakdown tự động tôn trọng bộ lọc thời gian/chiến dịch đang áp dụng.

### Module sâu: `buildContentBySource`

Tách một hàm thuần (pure) trong `eventImpl` nhận dữ liệu aggregate đã tổng hợp và trả về danh sách breakdown. Đây là điểm tập trung toàn bộ luật nghiệp vụ của tính năng, giao diện đơn giản và ổn định:

- Đầu vào: struct dữ liệu báo cáo đã aggregate. Đầu ra: `[]EventContentBySource`.
- Không truy cập DB, không dùng context — thuần tính toán, dễ kiểm thử độc lập.
- Luật: bỏ qua nguồn có tổng `<= 0`; mẫu số phần trăm là **tổng nội dung đã duyệt của các nguồn**, không phải `TotalContent` tổng thể; phần trăm làm tròn bằng `math.Round`; thứ tự phần tử cố định theo thứ tự khai báo nguồn để biểu đồ ổn định giữa các lần tải.
- Khóa `source` lấy trực tiếp từ `constants.ContentSource*`, không hard-code chuỗi.

### API contract

`EventReportStatisticResponse` bổ sung:

```
contentBySource: [
  { source: string, total: int64, percent: float64 }
]
```

- `source` ∈ { `tiktok`, `youtube`, `youtube_shorts`, `facebook`, `facebook_reels`, `instagram`, `instagram_reels`, `threads` }, mở rộng được về sau.
- Các field `totalYoutubeContent`, `totalTiktokContent`, `percentYoutubeContent`, `percentTiktokContent` giữ nguyên vị trí trong response nhưng đánh dấu **Deprecated**, sẽ gỡ khi mọi client đã chuyển sang `contentBySource`.
- Sửa lỗi tính toán: `percentYoutubeContent` trước đây là `100 - percentTiktokContent`, nay tính độc lập trên `TotalContent`.
- Struct response được sắp xếp lại nhóm field (chỉ số chung → tiền → breakdown → deprecated) cho dễ đọc; đây là thay đổi thứ tự khai báo, không phải thay đổi hợp đồng JSON.

### Tầng admin (React)

- Hai bảng metadata cấp module, không nằm trong component state:
  - `SOURCE_META`: `source → { labelKey, color }`. `labelKey` trỏ tới khóa locale sẵn có trong `key.label.*`; màu bám theo màu thương hiệu nền tảng, biến thể Reels/Shorts dùng tông lệch của nền tảng gốc.
  - `SOURCE_ICON`: `source → asset icon`. Biến thể Reels/Shorts dùng lại icon nền tảng gốc.
- Hằng `FALLBACK_COLOR` và nhánh dự phòng: nguồn chưa khai báo trong `SOURCE_META` hiển thị khóa thô làm nhãn; nguồn không có icon hiển thị chấm tròn tô màu tương ứng.
- `PieConfig` sinh `data` từ `contentBySource` thay vì hai phần tử cứng. `color` chuyển từ mảng cố định sang hàm ánh xạ theo `datum.type`. `tooltip.formatter` lấy `percent` từ chính phần tử breakdown thay vì chọn nhánh if/else theo tên nguồn.
- Khối chú thích dưới biểu đồ chuyển từ hai `Space` viết tay sang `map` trên breakdown, thêm `flexWrap` + `gap` để chịu được số lượng nguồn tăng dần.
- `sourceLabel` được memo hóa theo `intl`; `sourceStats` memo hóa theo `statistic` với mặc định mảng rỗng, tránh crash khi chưa có dữ liệu.
- Bổ sung 3 icon SVG mới (Facebook, Instagram, Threads) vào thư mục icon công khai và đăng ký trong config ảnh.
- `type.d.ts` bổ sung kiểu `ContentBySource` và trường `contentBySource` trong `Dashboard.Info`; `model.ts` bổ sung giá trị khởi tạo `contentBySource: []` và `totalCashFlow: 0`.

### Quyết định kiến trúc

- **Chọn breakdown động thay vì thêm field cứng cho từng nguồn.** Thêm field cứng sẽ nhân đôi chi phí cho mỗi nguồn mới ở cả BE và FE, và làm response phình theo thời gian.
- **Giữ tương thích ngược thay vì đổi breaking.** PR nhắm nhánh `release`, nên các client đang chạy phải tiếp tục hoạt động; việc gỡ field deprecated tách thành công việc riêng.
- **Ánh xạ nhãn/màu/icon đặt ở FE, không ở BE.** BE chỉ trả khóa nguồn trung tính; chuyện trình bày thuộc về client, cho phép mỗi client (admin, app, báo cáo) tự chọn cách hiển thị.
- **Lược bỏ nguồn bằng 0 ở BE, không ở FE.** Đảm bảo mọi client đều có cùng hành vi, không phải mỗi client tự lọc.

## Testing Decisions

Người yêu cầu PRD đã chốt: **không viết test cho phạm vi này**.

Tiêu chí nếu bổ sung test về sau: chỉ kiểm thử hành vi quan sát được từ bên ngoài (đầu vào dữ liệu aggregate → mảng breakdown trả ra; response JSON của endpoint báo cáo), không kiểm thử chi tiết cài đặt như thứ tự các bước trong pipeline hay cấu trúc nội bộ của component. Ứng viên đầu tiên là `buildContentBySource` vì đây là hàm thuần, giao diện hẹp, chứa toàn bộ luật nghiệp vụ (bỏ nguồn 0, mẫu số phần trăm, làm tròn, trường hợp không có dữ liệu).

## Out of Scope

- Gỡ bỏ các field deprecated (`totalYoutubeContent`, `totalTiktokContent`, `percentYoutubeContent`, `percentTiktokContent`) và di trú toàn bộ client.
- Breakdown theo nguồn cho các chỉ số khác ngoài nội dung đã duyệt (view, like, comment, engagement, tiền thưởng).
- Ghi nhận/thu thập dữ liệu nội dung từ các nguồn mới — phần này đã tồn tại sẵn ở tầng thu thập, PRD chỉ làm phần hiển thị báo cáo.
- Cho phép admin tự cấu hình màu/nhãn nguồn qua giao diện.
- Xuất báo cáo breakdown ra file (Excel/CSV).
- Thay đổi bộ lọc dashboard hoặc thêm bộ lọc theo nguồn.
- Cập nhật báo cáo phía app người dùng cuối.

## Further Notes

- Có sự lệch quy ước đặt tên cần lưu ý khi mở nguồn mới: khóa nhánh trong document analytic dùng camelCase số ít (`youtubeShort`, `facebookReel`, `instagramReel`) trong khi khóa `source` của API dùng snake_case số nhiều (`youtube_shorts`, `facebook_reels`, `instagram_reels`). Bảng ánh xạ nằm trong `buildContentBySource` — đây là chỗ duy nhất cần sửa khi thêm nguồn ở BE.
- Do phần trăm được làm tròn từng nguồn bằng `math.Round`, tổng các phần trăm có thể lệch khỏi 100 vài đơn vị khi số nguồn nhiều. Chấp nhận được cho mục đích đọc nhanh; nếu cần khớp tuyệt đối thì phải áp dụng thuật toán phân bổ phần dư.
- Mẫu số phần trăm ở `contentBySource` là tổng nội dung đã duyệt của các nguồn, khác với mẫu số của các field deprecated (dùng `TotalContent`). Hai bộ số có thể lệch nhau nếu tồn tại nội dung đã duyệt không thuộc nguồn nào trong danh sách — thêm một lý do để sớm gỡ field deprecated.
- Quy mô thay đổi: 10 file, +208/−54, chạm cả `backend` lẫn `admin`.

### Những điểm lệch phát hiện khi truy vết dữ liệu (nằm ngoài phạm vi PR, cần theo dõi)

- **Tên field tiền bị đảo trong pipeline báo cáo**: `totalCashPending` được `$sum` từ `statistic.cash.completed`, còn `totalCashCompleted` lại `$sum` từ `statistic.cash.cashback`. Tên struct không phản ánh nguồn thật. PR không đụng tới phần này, nhưng ai đọc `contentBySource` rồi suy diễn tương tự cho khối tiền sẽ hiểu sai.
- **`totalCashFlow` không scope theo partner**: `getTotalCashflow` chỉ gán `event` + khoảng thời gian theo `createdAt` + `action = withdraw`, bỏ qua `AssignPartnerForStaff`. Khi staff của một đối tác xem báo cáo không lọc theo chiến dịch cụ thể, con số này có thể bao gồm dữ liệu ngoài phạm vi của họ.
- **`totalCashBonus` lọc thời gian theo `toAt`** trong khi mọi chỉ số khác lọc theo `date`/`createdAt`. Hai mốc thời gian khác nhau nên tổng tiền thưởng có thể không khớp kỳ với phần còn lại của báo cáo.
- **Job phân tích cấp user chưa ghi nguồn Threads**: `UpdateAnalyticUserEventDaily` gán đủ 7 nguồn nhưng thiếu `Threads`, trong khi `UpdateAnalyticEventDaily` (nguồn dữ liệu của API này) đã có đủ 8. Không ảnh hưởng dashboard trong PRD này, nhưng báo cáo theo user sẽ thiếu Threads.
- **`totalContent` và tổng của `contentBySource` có thể lệch nhau**: `totalContent` đếm từ nhánh tổng `statistic.totalContentApproved`, còn breakdown cộng từ 8 nhánh nguồn. Nội dung đã duyệt có `source` nằm ngoài 8 giá trị đã khai báo sẽ được tính vào `totalContent` nhưng không xuất hiện trong breakdown.
