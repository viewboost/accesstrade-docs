# PRD: Backfill Missing Event-Reward Migration

**Labels:** `ready-for-agent`
**Related plan:** `docs/superpowers/plans/2026-07-16-backfill-missing-event-reward.md`

## Problem Statement

Là admin vận hành chương trình event, tôi phát hiện có những `content-analytic-daily` (snapshot metric view/like/comment theo ngày của content trong một event) đã tồn tại nhưng **không** có `event-reward` tương ứng — tức là user đủ điều kiện nhận thưởng theo schema `by-statistic` nhưng khoản thưởng chưa được sinh ra (do lỗi lịch sử, downtime của luồng tính reward, hoặc dữ liệu daily được thêm/sửa sau khi luồng reward đã chạy). Hậu quả là user bị thiếu tiền thưởng và thống kê event/user không khớp thực tế.

Hiện tại không có công cụ nào để, theo một event và một khoảng thời gian cụ thể, rà lại toàn bộ daily và bù (backfill) các reward còn thiếu một cách an toàn — đúng logic tính tiền và ngân sách (budget) như luồng thật, không tạo bản ghi trùng, và có thể truy vết được reward nào do thao tác bù sinh ra.

## Solution

Cung cấp **một API admin** (`POST /api/admin/migration/backfill-event-reward`) nhận payload gồm `event` (bắt buộc) và khoảng thời gian `fromAt`/`toAt` (tùy chọn), chạy nền, quét toàn bộ `content-analytic-daily` trong phạm vi đó. Với mỗi daily, API **tái sử dụng đúng luồng tính reward thật** đang chạy production (`UpdateRewardTypeByStatisticContent`), vốn đã idempotent (chưa có thì tạo, có rồi thì cập nhật) và đã xử lý đầy đủ ngân sách BPE/BPU/BPC cùng cơ chế primary/overflow. Reward **mới** được sinh bởi thao tác này được đánh dấu bằng cờ `fromMigration=true` để truy vết.

API hỗ trợ chế độ `dryRun` để admin ước lượng khối lượng công việc (đếm số daily trong phạm vi) trước khi ghi thật, vì luồng tính reward chạy tuần tự dưới budget-lock nên phạm vi rộng sẽ tốn thời gian.

## User Stories

1. Là admin vận hành, tôi muốn gọi một API để bù các `event-reward` còn thiếu cho một event cụ thể, để user không bị mất tiền thưởng họ đáng được nhận.
2. Là admin, tôi muốn giới hạn phạm vi backfill theo `event` (bắt buộc), để không vô tình đụng dữ liệu của event khác.
3. Là admin, tôi muốn tùy chọn giới hạn phạm vi theo khoảng thời gian `fromAt`/`toAt`, để chỉ bù đúng giai đoạn nghi ngờ thiếu reward.
4. Là admin, tôi muốn để trống `fromAt`/`toAt` khi cần bù toàn bộ vòng đời của event, để xử lý trường hợp không rõ mốc thời gian bị lỗi.
5. Là admin, tôi muốn chạy `dryRun` trước, để biết có bao nhiêu daily sẽ được xử lý trước khi thực sự ghi DB.
6. Là admin, tôi muốn `dryRun` chỉ đếm và log mà tuyệt đối không tạo reward, để chạy thử an toàn không gây tác dụng phụ.
7. Là admin, tôi muốn API trả về ngay (chạy nền), để không bị timeout HTTP khi phạm vi lớn.
8. Là admin, tôi muốn log tiến độ (bắt đầu, lastId từng trang, tổng kết) ra stdout, để theo dõi công việc đang chạy nền qua log container.
9. Là admin, tôi muốn reward được bù đi qua đúng logic ngân sách (BPE/BPU/BPC), để không cấp vượt ngân sách event/user/content.
10. Là admin, tôi muốn cơ chế primary/overflow được giữ nguyên khi bù, để phần vượt ngân sách được ghi nhận đúng như luồng thật.
11. Là admin, tôi muốn thao tác backfill là idempotent, để chạy lại nhiều lần không sinh reward trùng.
12. Là admin, tôi muốn reward đã tồn tại chỉ được cập nhật (statistic/cash) khi có thay đổi, chứ không bị nhân bản, để dữ liệu sạch.
13. Là admin, tôi muốn mọi reward MỚI do backfill sinh ra mang cờ `fromMigration=true`, để về sau truy vết/đối soát được nguồn gốc.
14. Là admin, tôi muốn reward đã tồn tại từ trước KHÔNG bị đổi cờ `fromMigration`, để không làm sai lệch nguồn gốc của bản ghi cũ.
15. Là admin, tôi muốn statistic của user và event được cập nhật sau khi bù (qua cơ chế budget-statistic của luồng thật), để báo cáo khớp với reward thực tế.
16. Là admin, tôi muốn daily có content đã bị xóa/không tồn tại được bỏ qua và ghi nhận (skipped), để không làm hỏng cả job.
17. Là admin, tôi muốn API từ chối body rỗng, để tránh chạy nhầm bằng giá trị mặc định.
18. Là admin, tôi muốn API bắt buộc có field `dryRun` trong body, để mọi lần gọi đều là quyết định có ý thức (chạy thử hay chạy thật).
19. Là admin, tôi muốn API bắt buộc `event` là ObjectID hợp lệ (24-char hex), để tránh lỗi truy vấn.
20. Là admin, tôi muốn API từ chối `fromAt`/`toAt` sai định dạng RFC3339, để lỗi được phát hiện sớm ở tầng validate thay vì lúc chạy.
21. Là admin, tôi muốn endpoint yêu cầu đăng nhập (RequiredLogin), để chỉ người có quyền mới chạy được thao tác nhạy cảm này.
22. Là developer bảo trì, tôi muốn backfill KHÔNG tự viết lại logic tính tiền mà tái dùng hàm production, để không phát sinh sai lệch giữa hai đường tính reward.
23. Là developer bảo trì, tôi muốn backfill KHÔNG dùng bảng trung gian `event-reward-temps`, để tránh phụ thuộc quy trình 2 bước (check → apply) không cần thiết.
24. Là developer bảo trì, tôi muốn thay đổi vào luồng reward lõi được giới hạn tối thiểu (chỉ thêm một cờ), để giảm rủi ro hồi quy cho các luồng đang chạy.
25. Là developer bảo trì, tôi muốn các caller hiện có của luồng reward giữ nguyên hành vi (không đánh dấu migration), để chức năng tính reward thời gian thực không bị ảnh hưởng.
26. Là developer bảo trì, tôi muốn 3 tầng (router/handler/service) của tính năng mới nằm ở file riêng, để dễ đọc và không làm phình file migration hiện có.
27. Là QA, tôi muốn validate của request body được kiểm bằng unit test, để đảm bảo các nhánh hợp lệ/không hợp lệ hoạt động đúng.
28. Là admin, tôi muốn chạy backfill với phạm vi hẹp trước khi mở rộng, để kiểm soát tải và rủi ro.

## Implementation Decisions

**Kiến trúc tổng thể — tái dùng luồng reward thật, không tự build, không temp**
- Tính năng KHÔNG tự dựng lại `event-reward` và KHÔNG dùng `event-reward-temps` (khác hẳn cơ chế `CheckMissView`/`UpdateViewMiss`).
- Backfill chỉ là lớp **điều phối (orchestration)**: quét `content-analytic-daily` theo phạm vi rồi ủy quyền cho hàm production `EventSchema.UpdateRewardTypeByStatisticContent`, vốn:
  - Đã idempotent nhờ tìm cặp reward primary/overflow theo `(user, schema, content, date)` **không lọc theo status** → chưa có thì insert, có rồi thì update.
  - Đã xử lý ngân sách BPE (event) / BPU (user) / BPC (content) và cơ chế primary/overflow dưới một budget-lock.
  - Đã cập nhật budget-statistic của user/event sau khi ghi.

**Module deep được giữ và tận dụng (không thay đổi hành vi)**
- `processRewardForSchema` (cùng các hàm phụ trợ tính ngân sách và upsert primary/overflow) là module lõi tính tiền — giữ nguyên logic, chỉ mở rộng để mang thêm một cờ truy vết.

**Module mới (deep module, interface đơn giản, tách file riêng)**
- **Backfill orchestrator service**: interface tối giản `Run(eventID string, fromAt, toAt time.Time, dryRun bool)`.
  - Xây điều kiện truy vấn: `event` bắt buộc; thêm điều kiện `date >= fromAt` nếu có, `date <= toAt` nếu có.
  - Phân trang theo con trỏ `_id` tăng dần (pattern hiện hành trong các migration), mỗi trang 1000 bản ghi.
  - `dryRun=true`: chỉ đếm + log từng daily, không tải content, không tạo reward.
  - `dryRun=false`: tải content theo `doc.Content`; nếu content không tồn tại → bỏ qua và đếm skipped; ngược lại gọi luồng thật với cờ migration bật.
  - Chạy nền (goroutine), khởi động từ handler.

**Thay đổi tối thiểu vào luồng reward lõi để truy vết nguồn gốc**
- Thêm trường boolean `fromMigration` vào bản ghi `event-reward`.
- Bổ sung một tham số cờ `fromMigration` vào interface/hàm `UpdateRewardTypeByStatisticContent` và luồng nó xuống tham số của `processRewardForSchema`.
- Cờ được set **chỉ ở nhánh INSERT** của cả reward primary và overflow; **nhánh UPDATE không đụng** tới trường này (để reward đã tồn tại giữ nguyên nguồn gốc).
- Tất cả caller hiện có của `UpdateRewardTypeByStatisticContent` truyền `false` → hành vi production không đổi.

**API contract**
- Route: `POST /api/admin/migration/backfill-event-reward`, yêu cầu đăng nhập.
- Request body:
  ```json
  {
    "event": "<ObjectID hex 24-char, bắt buộc>",
    "fromAt": "<RFC3339, tùy chọn>",
    "toAt": "<RFC3339, tùy chọn>",
    "dryRun": true
  }
  ```
- Validate: `event` bắt buộc + phải là MongoID; `fromAt`/`toAt` nếu có phải đúng RFC3339; middleware ép body không rỗng và **bắt buộc có field `dryRun`** (chống chạy nhầm bằng zero-value).
- Response: HTTP 200 ngay lập tức (job chạy nền), echo lại `event/fromAt/toAt/dryRun` và message xác nhận đã chạy nền.

**Schema change**
- `event-rewards`: thêm field `fromMigration` (bool, omitempty). Không migration dữ liệu cũ (mặc định vắng mặt = false).

**Quan sát vận hành**
- Log stdout theo pattern hiện hành (aurora): dòng bắt đầu (kèm nhãn DRY-RUN nếu có), `lastId` mỗi trang, và dòng tổng kết (số daily quét, số skipped).

## Testing Decisions

**Thế nào là test tốt:** chỉ kiểm hành vi bên ngoài (input → kết quả quan sát được), không phụ thuộc chi tiết cài đặt. Với codebase này, phần kiểm được bằng unit test thuần (không cần Mongo) là **validation của request body**.

**Module được test:**
- Request body `BackfillEventRewardBody.Validate()` — kiểm bảng case: hợp lệ (chỉ event; event + khoảng thời gian), không hợp lệ (thiếu event; event sai định dạng; `fromAt` sai định dạng; `toAt` sai định dạng).

**Prior art:** theo mẫu `pkg/admin/model/request/affiliate_test.go` (bảng case struct → gọi `Validate()` → assert nil/không-nil). Đây là pattern test request duy nhất đang tồn tại và phù hợp trong `pkg/admin`.

**Không viết integration test Mongo cho service backfill:** `pkg/admin/service` hiện KHÔNG có test harness cho tầng service phụ thuộc Mongo. Thay vào đó, tầng service/handler được kiểm chứng bằng: biên dịch sạch (`go build ./...`, `go vet ./...`) để bắt sót caller khi đổi signature, và smoke test thủ công theo kịch bản `dryRun` rồi `dryRun=false` phạm vi hẹp, kiểm cờ `fromMigration` và tính idempotent (chạy lại không nhân bản).

## Out of Scope

- Không có UI/màn hình admin cho thao tác này (chỉ API).
- Không tạo tài liệu markdown mô tả collection `event-rewards` (đã xác nhận "docs" nghĩa là **document/bản ghi** event_reward, không phải file tài liệu).
- Không dùng cơ chế job-tracking (`migration-jobs` + poll `GET /migration/jobs/:id`); job chỉ chạy nền + log stdout.
- Không backfill cho các loại schema khác `by-statistic` (không xử lý `by-view-milestone`, `by-content-milestone` trong phạm vi này).
- Không thay đổi logic tính tiền/ngân sách lõi (chỉ thêm cờ truy vết).
- Không migrate/đặt lại giá trị `fromMigration` cho các reward đã tồn tại.
- Không có cơ chế hủy/tạm dừng job đang chạy.
- Không đụng tới luồng `CheckMissView`/`UpdateViewMiss`/`event-reward-temps`.

## Further Notes

- Tính idempotent do luồng thật đảm bảo (tìm cặp primary/overflow theo `(user, schema, content, date)` không lọc status). Chạy lại cùng payload là an toàn.
- Vì mỗi daily đi qua budget-lock tuần tự, phạm vi rộng sẽ chậm; `dryRun` giúp ước lượng khối lượng trước và khuyến nghị chạy phạm vi hẹp trước.
- Cờ `fromMigration` cố ý chỉ set khi INSERT: mục tiêu là đánh dấu bản ghi **được sinh** bởi backfill; nếu về sau luồng thật update chính bản ghi đó, nguồn gốc vẫn được giữ.
- Điểm rủi ro cần review kỹ khi hiện thực: thay đổi signature của hàm reward lõi phải cập nhật **tất cả** caller (dựa vào trình biên dịch bắt sót), và tuyệt đối không set cờ ở nhánh UPDATE.
