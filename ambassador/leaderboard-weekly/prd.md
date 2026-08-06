# PRD: Bảng xếp hạng theo tuần cho campaign Ambassador

**Ngày:** 06/08/2026
**Author:** dinhnguyen
**Project:** Ambassador (Parasola)
**Project Level:** 1 (1–10 stories)
**Trạng thái:** Đã triển khai — chờ bật cho campaign thật
**Related:** [`overview.md`](./overview.md) · [`tech-spec.md`](./tech-spec.md)

> Narrative tiếng Việt, technical terms tiếng Anh. Mỗi FR có acceptance criteria (AC) testable — nguồn để sinh test case.

---

## Problem Statement

Bảng xếp hạng của một campaign xếp theo `statistic.pointTotal.completed` của collection `user_event` — con số luỹ kế từ ngày campaign bắt đầu, không có chiều thời gian.

Với campaign chạy vài tháng, thứ hạng đóng băng. Creator vào sau không thể đuổi kịp khoảng cách tích luỹ; creator cũ ngừng đăng bài vẫn giữ hạng. Bảng không phản ánh hoạt động hiện tại, và brand mất công cụ tạo nhịp truyền thông hàng tuần.

## Solution

Thêm cấu hình `leaderboardPeriod` vào `EventOpts` với hai giá trị `all_time` và `week`. Admin chọn trong form event.

Khi kỳ là `week`, bảng đọc từ collection thống kê theo ngày `user_event_analytic_daily` và cộng các bản ghi trong khoảng thứ Hai đến Chủ nhật của tuần hiện tại theo giờ Việt Nam. Khi kỳ là `all_time`, giữ nguyên luồng cũ không sửa một dòng.

Response bổ sung ba field mô tả kỳ (`period`, `periodStartAt`, `periodEndAt`), đều `omitempty` nên response của kỳ luỹ kế không đổi. Frontend Parasola hiển thị nhãn kỳ dưới tiêu đề bảng.

Kèm theo hai hạng mục hạ tầng bắt buộc: index `{event, date}` cho collection thống kê theo ngày, và cache mười phút cho endpoint bảng xếp hạng.

## User Stories

**Là creator mới tham gia giữa campaign,** tôi muốn thấy bảng xếp hạng tính theo tuần hiện tại, để biết nỗ lực tuần này của tôi được ghi nhận thay vì bị khoảng cách tích luỹ của người khác che lấp.

**Là creator đang hoạt động đều,** tôi muốn bảng ghi rõ khung thời gian đang tính, để không nhầm rằng thành tích của mình bị mất.

**Là creator,** tôi muốn tiền thưởng vẫn luỹ kế dù bảng xếp hạng reset, vì đó là tiền thật tôi đã kiếm.

**Là brand,** tôi muốn bật chế độ thi đua tuần cho riêng campaign của mình mà không ảnh hưởng campaign khác đang chạy.

**Là nhân viên vận hành,** tôi muốn tự bật/tắt trong admin và thấy hiệu lực ngay, không cần chờ đợt phát hành.

**Là kỹ sư,** tôi muốn hai kỳ trả về cùng một cấu trúc dữ liệu, để thêm giao diện mới không phải rẽ nhánh theo kỳ.

## Functional Requirements

### FR-1 — Cấu hình kỳ xếp hạng trên campaign

Thêm field `LeaderboardPeriod` vào struct `EventOpts`, giá trị `all_time` hoặc `week`.

**AC:**
- [ ] Field khai `omitempty` ở cả `bson` và `json`; document cũ không có field unmarshal ra chuỗi rỗng, không panic.
- [ ] Chuỗi rỗng, giá trị lạ (`month`, `abc`) và `all_time` đều rơi vào nhánh luỹ kế.
- [ ] Không cần migration dữ liệu.
- [ ] `EventOpts` truyền nguyên khối qua request/response admin, không phải sửa DTO nào.

### FR-2 — Ô chọn kỳ trong form event admin

Thêm select "Kỳ xếp hạng" vào tab Tuỳ chọn của form event, hai lựa chọn *Toàn thời gian* / *Theo tuần*.

**AC:**
- [ ] Ô nằm ở tab Tuỳ chọn, cạnh `maxContentPerDay` / `hashtags` / `applyForSources`.
- [ ] Giá trị mặc định khi tạo mới là *Toàn thời gian*.
- [ ] Mở event đã có cấu hình → ô hiển thị đúng giá trị đang lưu.
- [ ] Nhãn lấy từ file locale, không hardcode chuỗi trong component.

### FR-3 — Nhân bản event giữ nguyên cấu hình kỳ

`cloneEventOptions` phải chép field mới sang event nhân bản.

**AC:**
- [ ] Nhân bản event có kỳ `week` → event mới cũng `week`.
- [ ] Nhân bản event không cấu hình kỳ → event mới cũng không có field, không sinh chuỗi rỗng thừa.

### FR-4 — Xếp hạng theo tuần hiện tại

Khi kỳ là `week`, xếp hạng theo lượt xem phát sinh trong khoảng thứ Hai 00:00:00 đến Chủ nhật 23:59:59 giờ Việt Nam.

**AC:**
- [ ] Tuần bắt đầu thứ Hai. Chủ nhật thuộc tuần hiện tại, không bị đẩy sang tuần sau.
- [ ] Biên hai tuần liền kề khít nhau — không hở giây nào, không chồng lấn.
- [ ] Tuần vắt qua ranh giới tháng tính đúng.
- [ ] Chỉ cộng bản ghi có `date` nằm trong khoảng; bản ghi ngoài khoảng không được tính.
- [ ] Thứ hạng dựa trên tổng `pending + completed` của lượt xem, đúng công thức frontend hiển thị ở cột Views.
- [ ] Creator không phát sinh lượt xem nào trong tuần không xuất hiện trên bảng.
- [ ] Hai creator cùng điểm có thứ tự ổn định giữa các lần gọi (tie-break theo `_id`).
- [ ] Kết quả trả về đúng cấu trúc `UserEventResponse` như nhánh luỹ kế: `statistic.pointTotal` và `statistic.cashTotal` có giá trị, các nhánh theo nền tảng để trống.

### FR-5 — Response mang thông tin kỳ

`UserEventAllResponse` bổ sung `period`, `periodStartAt`, `periodEndAt`.

**AC:**
- [ ] Ba field khai `omitempty`; kỳ `all_time` không trả field nào trong ba field này.
- [ ] Kỳ `week` trả đủ ba field, `periodStartAt` là thứ Hai 00:00 và `periodEndAt` là Chủ nhật 23:59:59 giờ Việt Nam.
- [ ] Server chốt biên kỳ; API không nhận tham số kỳ từ client.
- [ ] Frontend cũ gọi backend mới vẫn chạy (bỏ qua field lạ).
- [ ] Frontend mới gọi backend cũ hiểu là `all_time`, không hiện nhãn.

### FR-6 — Nhãn kỳ trên bảng xếp hạng Parasola

Hiển thị dòng `Tuần này · DD/MM – DD/MM` dưới tiêu đề bảng khi kỳ là `week`.

**AC:**
- [ ] Kỳ `all_time` không render dòng nào; giao diện giữ nguyên như trước.
- [ ] Kỳ `week` thiếu `periodStartAt`/`periodEndAt` → hiện "Tuần này" không kèm ngày, không vỡ layout.
- [ ] Ngày format theo offset giờ Việt Nam, không theo múi giờ trình duyệt.
- [ ] Hiển thị đúng ở cả desktop và mobile (breakpoint 768px).
- [ ] Frontend không gửi tham số kỳ lên API.

### FR-7 — Index cho truy vấn kỳ tuần

Thêm index `{event, date}` cho collection `user_event_analytic_daily`.

**AC:**
- [ ] Index tạo tự động lúc khởi động qua `Indexes()`, idempotent khi chạy lại.
- [ ] Thứ tự field là `event` trước `date` (equality trước, range sau).
- [ ] Truy vấn kỳ tuần dùng được index, không quét toàn collection.

### FR-8 — Cache bảng xếp hạng

Cache kết quả mười phút theo lối cache-aside.

**AC:**
- [ ] Khoá cache chứa event id, hậu tố kỳ, số trang, giới hạn.
- [ ] Hậu tố kỳ nhúng mốc kỳ (`week_2026-08-03`), không chỉ tên kỳ.
- [ ] Mọi thời điểm trong cùng một tuần sinh cùng một khoá.
- [ ] Sang tuần mới sinh khoá khác — bảng làm mới ngay 00:00 thứ Hai, không đợi hết TTL.
- [ ] Admin đổi kỳ → khoá đổi → người xem thấy ngay.
- [ ] Khoá của kỳ `all_time` không thay đổi theo thời gian.
- [ ] Kết quả rỗng hợp lệ **có** cache; truy vấn lỗi **không** cache.
- [ ] Redis không khả dụng → tính năng vẫn chạy, chỉ mất cache.

## Non-Functional Requirements

### NFR-1 — Backward compatibility

Campaign chưa cấu hình kỳ phải trả kết quả y hệt trước khi có tính năng. Đây là ràng buộc quan trọng nhất vì nó bảo vệ mọi campaign đang chạy.

**AC:**
- [ ] Logic nhánh luỹ kế không đổi (chỉ tách hàm, không đổi truy vấn hay thứ tự sắp xếp).
- [ ] Response kỳ `all_time` giống hệt trước, không thừa field nào.
- [ ] Rollback chỉ cần đổi lại lựa chọn trong admin, không cần rollback code.

### NFR-2 — Hiệu năng

Endpoint bảng xếp hạng là public, không xác thực, chịu tải trang chủ.

**AC:**
- [ ] Không có truy vấn N+1: tra thông tin creator gom một lượt cho cả trang.
- [ ] Truy vấn kỳ tuần dùng index, không collection scan.
- [ ] Cache hit chỉ tốn một truy vấn (lấy event); cache miss tốn ba (event, aggregate, users).

### NFR-3 — Đúng múi giờ

**AC:**
- [ ] Biên tuần chốt theo `Asia/Ho_Chi_Minh` ở phía server.
- [ ] Trình duyệt ở múi giờ khác vẫn hiển thị đúng ngày của tuần theo giờ Việt Nam.

### NFR-4 — Bảo mật

**AC:**
- [ ] Response không chứa dữ liệu riêng của người xem.
- [ ] Khoá cache không chứa định danh người xem — kèm cảnh báo tại chỗ dựng khoá rằng nếu thêm dữ liệu riêng người xem thì phải bổ sung định danh vào khoá.

## Data Model (tóm tắt — chi tiết ở tech-spec)

Một field mới trên `EventOpts`, không xoá hay đổi field nào:

```go
LeaderboardPeriod string `json:"leaderboardPeriod,omitempty" bson:"leaderboardPeriod,omitempty"`
```

Ba field mới trên `UserEventAllResponse`, đều `omitempty`: `Period`, `PeriodStartAt`, `PeriodEndAt`.

Một index mới: `user_event_analytic_daily {event, date}`.

Không tạo collection mới, không migration.

## API (endpoint `GET /events/{id}/leaderboards` — chi tiết ở tech-spec)

Không đổi đường dẫn, không thêm query param. Kỳ đọc từ `event.options.leaderboardPeriod`.

| Kỳ | Nguồn dữ liệu | Field kỳ trong response |
|----|---------------|-------------------------|
| `all_time` (mặc định) | `user_event` | Không có |
| `week` | `user_event_analytic_daily` | `period`, `periodStartAt`, `periodEndAt` |

## Testing Decisions

Tính năng gần như không có logic nghiệp vụ phức tạp. Rủi ro nằm ở ba chỗ tính toán thuần mà sai thì im lặng: biên tuần, cấu trúc pipeline, khoá cache. Cả ba đều là hàm thuần nên test không cần cơ sở dữ liệu.

Prior art: `creator-os` tách `mergePinnedRanked` thành hàm export riêng để test không cần DB. Áp dụng đúng cách đó.

Đã có 13 hàm test, 22 case:

| Nhóm | File | Hàm | Case |
|------|------|:---:|:----:|
| Biên tuần | `backend/internal/util/time_week_test.go` | 5 | 7 |
| Pipeline | `.../aggregate_pipeline/user_event_analytic_daily_test.go` | 4 | 8 |
| Khoá cache | `backend/pkg/public/service/leaderboard_period_test.go` | 4 | 7 |

**Không test:** tầng truy cập cơ sở dữ liệu; component frontend (thay đổi chỉ là một dòng nhãn có điều kiện).

**Hồi quy bắt buộc:** campaign không cấu hình kỳ trả kết quả y hệt trước khi có tính năng.

**Chưa kiểm chứng:** TypeScript chưa typecheck được vì `typescript` không có trong `node_modules` của Parasola lẫn admin; chưa chạy với dữ liệu thật vì chưa campaign nào bật kỳ tuần.

## Out of Scope (phase 1)

Kỳ theo tháng — `creator-os` có sẵn ba kỳ trong model nhưng khách chỉ yêu cầu tuần.

Xem lại bảng xếp hạng của tuần đã qua — cần thêm API liệt kê các tuần trong khoảng thời gian campaign.

Hiển thị thứ hạng của chính người xem khi họ nằm ngoài danh sách.

Ghim creator lên đầu bảng.

Trao thưởng tự động theo tuần.

Nhãn kỳ cho các giao diện partner ngoài Parasola.

## Further Notes

Tính năng mượn mô hình và cách gọi tên của `creator-os` (`LeaderboardDefinition.period`, nhãn *Toàn thời gian / Theo tuần*) nhưng phần truy vấn phải tự làm: bên đó `queryRanked` bỏ qua field kỳ, tài liệu ghi rõ kỳ tuần là hạng mục hoãn lại do *"cần daily rollup đầy đủ"*. Ambassador có sẵn bảng thống kê theo ngày chính là daily rollup đó.

Khác biệt có chủ đích so với `creator-os`: bên đó không hiển thị kỳ ở trang công khai. Bê nguyên thì creator thấy bảng đổi số mà không biết vì sao.

Cấu hình này độc lập với `showLeaderboard` / `showLeaderboardAmount` ở cấp partner (xem [`../prd-partner-leaderboard-config-2026-04-02.md`](../prd-partner-leaderboard-config-2026-04-02.md)): partner quyết định có hiện bảng không, campaign quyết định bảng tính theo kỳ nào.

Code ở repo `AT-Core/ambassador` — PR #97 (tính năng, đã merge), PR #99 (cache, đang mở).

Ba câu hỏi còn để ngỏ ghi ở mục 8 của [`overview.md`](./overview.md).
