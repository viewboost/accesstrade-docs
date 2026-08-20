# PRD — Gộp dữ liệu ngày tràn của event về ngày kết thúc (Merge Overflow Day)

> Bối cảnh: sự cố dữ liệu production trên nhánh `feat/migration-event-view`.
> Event kết thúc ngày **31/07/2026** nhưng crawler vẫn ghi nhận và tạo dữ liệu sang ngày **01/08/2026**.

## Problem Statement

Một số event trên production có `endAt` là 31/07/2026. Do lỗi crawler, hệ thống vẫn tiếp tục ghi `content-flow` sau khi event đã kết thúc, kéo theo việc sinh ra `content-analytic-daily` (và các doc thống kê phụ thuộc) mang `date = 01/08/2026` — một ngày nằm ngoài vòng đời của event.

Hệ quả với người dùng:

- **Creator bị mất tiền thưởng.** `event-schema` chỉ khớp khi `startAt <= date <= endAt`, nên lượt view rơi vào ngày 01/08 không khớp schema nào và **không sinh `event-reward`**. Toàn bộ view của khoảng thời gian tràn này bị bỏ rơi, không được quy đổi thành cash.
- **Báo cáo event sai.** Biểu đồ và bảng thống kê của event xuất hiện thêm một cột ngày 01/08/2026 nằm ngoài thời gian chạy event, khiến admin và partner đối soát bị lệch. Tổng view của ngày cuối cùng (31/07) bị thiếu đúng bằng phần đã tràn sang.
- **Không thể tự khắc phục bằng tay.** Dữ liệu trải trên 5 collection có quan hệ phụ thuộc lẫn nhau (`content-flow` → `content-analytic-daily` → `event-reward` → `event-analytic-daily` / `user-event-analytic-daily` → `user-event`). Sửa tay một collection sẽ bị các job định kỳ ghi đè hoặc đánh dấu sai.

Ngoài ra, khi migration được chạy trên production, người vận hành **không có cách nào theo dõi nó đang chạy tới đâu**. Hệ thống hiện chỉ ghi log ra container; muốn biết migration đã đụng bao nhiêu content, dừng ở bước nào, hay vì sao bị chặn thì phải xin quyền vào container đọc log hoặc query thẳng database — cả hai đều không khả thi với người vận hành. Với một migration ghi vào 5 collection có quan hệ phụ thuộc, chạy mù như vậy là rủi ro không chấp nhận được.

Điểm mấu chốt: nếu chỉ sửa `content-analytic-daily` mà không xử lý `content-flow` gốc, mọi lần recompute sẽ **tái tạo lại** doc ngày 01/08, và job `Audit()` sẽ đánh doc ngày 31/07 là `auditStatus = invalid` với `codeReason = VIEW_INVALID` vì `view.value` không còn khớp tổng `content-flow` của ngày đó.

## Solution

Bổ sung một **migration có kiểm soát**, chạy theo từng event do người vận hành chỉ định, thực hiện gộp toàn bộ dữ liệu của ngày tràn về ngày kết thúc thật của event.

Từ góc nhìn người vận hành:

- Gọi một endpoint migration với `eventId`, ngày nguồn (01/08/2026) và ngày đích (31/07/2026).
- Mặc định chạy ở chế độ **dry-run**: hệ thống chỉ báo cáo sẽ đụng bao nhiêu doc ở mỗi collection, tổng view/cash của event trước và sau khi gộp, và danh sách content bị ảnh hưởng — không ghi gì vào DB.
- Khi số liệu dry-run đã được đối chiếu và chấp nhận, chạy lại với `dryRun=false` để thực thi.
- Sau khi chạy, event chỉ còn dữ liệu tới đúng ngày `endAt`; lượt view của ngày tràn đã được cộng vào ngày cuối cùng; `event-reward` của ngày cuối được tính lại nên creator nhận đủ tiền thưởng; báo cáo event khớp lại.
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
11. Là người vận hành, tôi muốn migration dừng lại khi phát hiện `event-reward` ở ngày nguồn đã ở trạng thái đã chi (`isTransfer` hoặc `completed`), để không bao giờ tạo ra lệch tiền đã chuyển.
12. Là người vận hành, tôi muốn migration báo rõ "không có gì để gộp" khi event không có doc nào ở ngày nguồn, để biết mình đã chọn nhầm event.
13. Là người vận hành, tôi muốn endpoint migration được bảo vệ bằng cơ chế xác thực và key migration sẵn có, để không ai ngoài đội vận hành gọi được.
14. Là người vận hành, tôi muốn mỗi lần trigger migration trả về ngay một `jobId` thay vì treo request cho tới khi chạy xong, để không bị timeout khi event có nhiều content.
15. Là người vận hành, tôi muốn poll tiến độ của một job qua HTTP bằng `jobId`, để biết migration đang xử lý record thứ mấy trên tổng bao nhiêu.
16. Là người vận hành, tôi muốn job ghi lại `dryRun`, `eventId`, `fromDate`, `toDate` đã truyền vào, để đối chiếu lại đúng tham số của lần chạy đó khi rà soát sau này.
17. Là người vận hành, tôi muốn job ghi lại lý do bị chặn của guard, để biết vì sao migration không thực thi mà không phải đọc log container.
18. Là người vận hành, tôi muốn job giữ lại danh sách mẫu các row bị lỗi kèm lý do, để debug được vài trường hợp đầu tiên ngay trên phản hồi HTTP.
19. Là người vận hành, tôi muốn job chuyển sang trạng thái `failed` kèm thông báo lỗi khi migration panic giữa chừng, để phân biệt được "chạy xong" với "chết giữa đường".
20. Là người vận hành, tôi muốn xem danh sách các job gần nhất, lọc theo loại migration, để nắm được lịch sử đã chạy những gì trên production.
21. Là người vận hành, tôi muốn báo cáo dry-run (số doc theo collection, tổng view/cash trước–sau, danh sách content bị ảnh hưởng) được lưu ngay trong job record, để đọc lại kết quả một lần chạy cũ mà không phải chạy lại.
22. Là người vận hành, tôi muốn job bị guard chặn mang một trạng thái riêng chứ không phải `done`, để không nhầm "bị chặn, chưa ghi gì" với "đã chạy xong".
23. Là người vận hành, tôi muốn hệ thống từ chối trigger khi đã có một job cùng loại đang chạy trên cùng event, để hai lần chạy không giẫm lên nhau.
24. Là creator tham gia event, tôi muốn lượt view sinh ra trong khoảng thời gian crawler ghi tràn vẫn được tính thưởng, để không bị thiệt vì lỗi kỹ thuật của hệ thống.
25. Là creator, tôi muốn `event-reward` của ngày cuối event phản ánh đúng tổng view sau khi gộp, để số tiền tôi nhận khớp với số view thực tế.
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

## Implementation Decisions

### Ngữ nghĩa dữ liệu đã xác lập

- `content-analytic-daily` lưu `view`, `like`, `comment` dưới dạng `{begin, value, end}`, trong đó `begin` là `end` của ngày trước đó, `value` là lượng phát sinh **trong ngày**, `end = begin + value`. Do đó gộp hai ngày là **cộng dồn `value`**, không phải lấy giá trị lớn hơn.
- **Nguồn gộp là `content-analytic-daily`, không phải `content-flow`.** Migration đọc doc của ngày nguồn và ngày đích, cộng `value` của hai ngày rồi ghi thẳng xuống doc ngày đích. Không gọi lại luồng recompute từ flow.
- Lý do: `internal/service/content_analytic_daily.go` — hàm `Update()` không cộng dồn mà **aggregate lại toàn bộ `content-flow` của ngày đó rồi ghi đè `view.value`**. Trong khi `DeleteContentFlow()` (chạy ở cuối mỗi lần `Audit()`) backup và xóa `content-flow` của mọi doc có `auditStatus = valid` và `date <= now - 30 ngày`. Nếu tới lúc chạy migration mà flow ngày đích đã bị dọn, recompute sẽ tính ra tổng chỉ từ phần flow còn lại rồi ghi đè — **toàn bộ view gốc của ngày đích biến mất**. Không phải thiếu, mà là mất. Gộp từ `content-analytic-daily` không có rủi ro này vì doc analytic được giữ vĩnh viễn.
- `TotalManualView` cũng phải cộng dồn hai ngày. Nếu để `Update()` recompute, manual view của ngày nguồn bị nuốt: nhánh update chỉ giữ `TotalManualView` của doc ngày đích, còn nhánh insert set thẳng về `0`.
- `content-flow` chỉ còn một vai trò: giữ cho `Audit()` không đánh nhầm. Nó **không** tham gia vào việc tính số.
- `event-schema` khớp theo `startAt <= date <= endAt`, nên ngày tràn **không sinh `event-reward`**. Migration không cần xóa reward ở ngày nguồn.
- Reward của ngày đích được tính lại qua `EventSchema().UpdateRewardTypeByStatisticContent`, hàm này đọc `doc.View.Value` của `content-analytic-daily` — **không** đọc `content-flow`, nên hợp với hướng gộp ở trên.
- `UpdateAnalyticEventDaily` và `UpdateAnalyticUserEventDaily` aggregate từ `content` và `event-reward`, cũng không đọc `content-flow`. Toàn bộ chuỗi recompute phía sau vì thế an toàn.
- Nhưng hai hàm đó match theo `content.date` / `event-reward.date` và ghi bằng **upsert**. `content.date` là ngày đăng bài, migration không thay đổi nó. Vì vậy doc analytic của ngày nguồn phải được **recompute rồi mới xóa nếu rỗng**, không được xóa mù — xóa mù thì lần recompute sau upsert nó trở lại.
- Ngày tràn là ngày cuối cùng của event, không có doc nào phía sau, nên `begin` của các ngày kế tiếp không cần dịch chuyển dây chuyền. Kể cả khi có doc phía sau, chuỗi vẫn liên tục: `end` mới của ngày đích (`begin₃₁ + v₃₁ + v₀₁`) đúng bằng `end` cũ của ngày nguồn.

### Module

- **MergeOverflowDayPlanner** — module sâu, thuần logic, không phụ thuộc DB. Đầu vào: danh sách `content-analytic-daily` của ngày nguồn và ngày đích. Đầu ra: một `MergePlan` mô tả danh sách content bị ảnh hưởng, giá trị `{begin, value, end}` và `totalManualView` mới cho doc ngày đích của từng content, và tổng view trước/sau. Đây là nơi chứa toàn bộ số học của migration — và cũng là **nguồn ghi thật**, không chỉ dự báo cho dry-run: Executor ghi thẳng những con số Planner tính ra.
- **MergeOverflowDayGuard** — module sâu, thuần logic. Đầu vào: `EventRaw` cùng snapshot analytic/reward của ngày nguồn và ngày đích. Đầu ra: danh sách lý do abort. Các điều kiện chặn:
  - event bật `ExtendedPeriod`;
  - ngày đích khác `endAt` của event;
  - ngày nguồn không liền kề ngay sau ngày đích;
  - **tồn tại `content-analytic-daily` của event ở ngày sau ngày nguồn** — nghĩa là tràn nhiều hơn một ngày, ngoài phạm vi migration này;
  - tồn tại `event-reward` ở ngày nguồn đã chi (`isTransfer` hoặc trạng thái completed) — điều kiện phòng thủ, trên lý thuyết không bao giờ kích hoạt vì ngày tràn không sinh reward;
  - không có dữ liệu nào ở ngày nguồn.
- **MergeOverflowDayExecutor** — module mỏng, chỉ điều phối I/O: backup → ghi doc `content-analytic-daily` ngày đích theo `MergePlan` và xóa doc ngày nguồn → xử lý `content-flow` cho `Audit()` → tính lại reward ngày đích → xóa và recompute `event-analytic-daily` cùng `user-event-analytic-daily`. Không chứa công thức tính toán.
- **MigrationJob** — hạ tầng theo dõi tiến độ, port nguyên pattern từ ambassador (`internal/model/mg/migration_job.go`, `internal/module/database/mongodb/dao/migration_jobs.go`, `pkg/admin/service/migration_job.go`). Gồm: model `MigrationJobRaw` + DAO trỏ vào collection `migration-jobs`, và bộ helper `newMigrationJob` / `saveMigrationJob` / `recordFailedSample` / `recordSkippedSample` / `finishMigrationJob`. Executor chỉ gọi các helper này; nó không tự viết logic ghi job.
- **Handler / Router / Validation** — module mỏng, bám theo pattern nhóm route migration hiện có, dùng lại middleware `RequiredLogin` và `CheckKeyMigration`.

### API contract

- Endpoint trigger trong nhóm route migration: `GET /migration/merge-overflow-day`.
- Tham số: `eventId` (bắt buộc), `fromDate` (ngày nguồn, bắt buộc), `toDate` (ngày đích, bắt buộc), `dryRun` (mặc định `true`).
- Mỗi lần gọi xử lý đúng một event. Không hỗ trợ chạy hàng loạt.
- Migration chạy **nền** ở cả hai chế độ — dry-run cũng async, không có nhánh đồng bộ riêng. Endpoint trigger trả về ngay `jobId` cùng tham số đã nhận. Trường hợp guard chặn vẫn sinh job record với status `aborted` kèm lý do, để lưu vết lần thử.
- Trigger trả lỗi ngay (không sinh job) khi đã tồn tại một job `merge-overflow-day` ở trạng thái `running` trên cùng `eventId` — xem mục chống chạy song song bên dưới.
- Hai endpoint theo dõi, port từ ambassador, đặt trong **group riêng** `/migration-jobs` chỉ gắn `RequiredLogin`:
  - `GET /migration-jobs?type=&limit=` — danh sách job mới nhất, sắp xếp theo `startedAt` giảm dần, lọc theo `type`, mặc định 20 bản ghi.
  - `GET /migration-jobs/:id` — chi tiết một job, dùng lại `routevalidation.Common().ParamID`. Trả 404 khi không tồn tại, phân biệt rõ với lỗi DB.
- Lý do tách group: ở vcreator, `CheckKeyMigration` được gắn ở cấp group `/migration` (khác ambassador chỉ có `RequiredLogin`). Nếu để endpoint job trong group đó, mỗi lần poll đều phải kèm key migration — trong khi poll là thao tác chỉ đọc, lặp liên tục. Endpoint **trigger** vẫn nằm trong `/migration` và vẫn chịu `CheckKeyMigration`.
- Báo cáo (trạng thái, lý do bị chặn, số doc bị đụng theo từng collection, tổng view và tổng cash trước/sau, danh sách content bị ảnh hưởng) nằm trong job record, đọc qua `GET /migration-jobs/:id`.

### Migration job tracking

**Phạm vi port.** Khung và bộ helper port nguyên trạng từ ambassador — cùng tên hàm, cùng ngữ nghĩa, cùng hằng số. Phần được phép khác đúng ba chỗ, liệt kê tường minh ở đây: thêm status `aborted`, gọn lại `MigrationJobParams`, và thêm field `report`. Ngoài ba chỗ này thì bám nguyên bản.

**Hạ tầng phải dựng mới ở vcreator** (chưa tồn tại):

- Hằng số `CollectionMigrationJob = "migration-jobs"` trong `internal/module/database/mongodb/collection.go`.
- Index `{type: 1, startedAt: -1}` đăng ký cùng chỗ với các index sẵn có (`internal/module/database/mongodb/index.go`), phục vụ endpoint list vốn luôn sort giảm dần theo `startedAt` và lọc theo `type`.
- Model `MigrationJobRaw` + DAO trỏ vào `GetDBShare()`, và service helper — port từ ba file gốc bên ambassador.

**Nội dung một job record:**

- Collection `migration-jobs`, giữ vĩnh viễn (không TTL) để trace lịch sử các đợt migration. Một record cho một lần trigger.
- Job type mới: `merge-overflow-day`. Mode `dry-run` hoặc `apply`, suy ra từ tham số `dryRun`.
- Status: `running` → `done` / `failed` / **`aborted`**. `aborted` là trạng thái thêm mới so với model gốc, dành riêng cho trường hợp guard chặn: job không ghi gì vào DB. Không dùng `done` cho trường hợp này — người vận hành poll thấy `done` sẽ hiểu nhầm là migration đã chạy xong.
- `startedBy` lấy từ `cc.GetCurrentUserID()` của context admin đang đăng nhập, giống cách các handler admin sẵn có đọc staff id.
- `params` gọn lại còn đúng những gì migration này dùng: `dryRun`, `event` (chính là `eventId`), `fromAt` (ngày nguồn), `toAt` (ngày đích) — tái dùng ba field `Event` / `FromAt` / `ToAt` đã có sẵn trong model gốc, không thêm field mới. Các field chỉ phục vụ job type của ambassador (`preferCache`, `requested`, `source`, `limit`, `syncedBefore`) và `createdSocialIds` **không port sang** — chúng vô nghĩa ở đây và chỉ làm doc khó đọc.
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
5. **`event-reward` ngày đích** — gọi `EventSchema().UpdateRewardTypeByStatisticContent(ctx, content, doc)` với doc ngày đích vừa ghi. Hàm này đọc `doc.View.Value` nên nhận đúng số đã gộp. Nó cũng tự kéo theo `UpdateStatisticUserEvent`, `Content().UpdateCashStatistic` và `User().UpdateStatistic`, nên `user-event` **không cần bước riêng**.
   - Lưu ý hành vi: điều kiện tìm reward cũ khớp cả `status`. Nếu reward ngày đích đã `completed` (đã chi), hàm sẽ **insert một reward mới** cho phần chênh thay vì update doc cũ — `GetStatisticContentIsRewardInDay` đã trừ phần đã completed nên số không bị đúp. Đây là hành vi mong muốn, không phải lỗi.
6. **`event-analytic-daily` và `user-event-analytic-daily`** — recompute **cả hai ngày**, không chỉ ngày đích:
   - Gọi `UpdateAnalyticEventDaily` / `UpdateAnalyticUserEventDaily` với `fromAt` = **ngày đích**, để doc ngày cuối phản ánh số đã gộp.
   - Gọi tiếp với `fromAt` = **ngày nguồn**. Không xóa mù doc ngày nguồn: hai hàm này match theo `content.date` và `event-reward.date`, mà `content.date` (ngày đăng bài) **migration không đụng tới**. Xóa mù chỉ có tác dụng tạm — chúng ghi bằng **upsert**, nên lần nào luồng recompute chạy lại với mốc ngày nguồn là doc quay về, kéo cột 01/08 trở lại báo cáo.
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
- **MergeOverflowDayGuard** — mỗi điều kiện chặn một test: event bật `ExtendedPeriod`, ngày đích khác `endAt`, ngày nguồn không liền kề, còn dữ liệu ở ngày sau ngày nguồn, reward ngày nguồn đã chi, ngày nguồn rỗng. Thêm một test cho trường hợp hợp lệ, khẳng định không có lý do abort nào.

**Không viết test cho** MigrationJob helper, Executor, Handler, Router — chúng chỉ điều phối và sẽ được kiểm chứng bằng dry-run trên production trước khi thực thi.

**Prior art:** các file test sẵn có trong nhóm service admin, đặc biệt là những test kiểm chứng bộ lọc và bộ tính toán thuần của luồng `event-bonus-import`, và test densify của luồng export analytic event. Cùng phong cách: table-driven, không dựng mongo, dữ liệu vào ra dựng thẳng trong test.

## Out of Scope

- **Sửa lỗi crawler.** PRD này chỉ khắc phục dữ liệu đã sinh sai. Việc chặn crawler ghi tiếp sau `endAt` là một hạng mục riêng — nếu không xử lý, sự cố sẽ lặp lại ở event tiếp theo.
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

- Thứ tự các bước là bắt buộc. Ghi doc ngày đích (bước 2) phải đi trước khi tính lại reward (bước 5), và bước 5 phải đi trước recompute analytic cấp event (bước 6) — vì bước 6 aggregate từ `event-reward`. Trong bước 6, recompute phải đi trước khi xóa doc ngày nguồn, không phải ngược lại.
- Sau khi chạy, nên xác nhận job `Audit()` không đánh doc ngày đích là `VIEW_INVALID`. Nếu có, kiểm tra xem `content-flow` ngày nguồn đã được dịch hết chưa, hoặc doc đã được chuyển sang `auditStatus = completed` chưa.
- `Audit()` so `s.TotalView == d.View.Value`, trong khi `Update()` của luồng hằng ngày ghi `value = TotalView + TotalManualView`. Nghĩa là **content có manual view sẽ luôn bị đánh `VIEW_INVALID`** kể cả khi không có migration nào chạy — đây là lỗi sẵn có của hệ thống, không phải do migration gây ra. Đừng dùng nó làm tiêu chí nghiệm thu cho nhóm content này; nếu muốn xử lý thì mở hạng mục riêng.
- `content-flow` cũ hơn 30 ngày sẽ bị `DeleteContentFlow()` chuyển sang collection backup rồi xóa. Vì migration không còn tính số từ flow nên chuyện này **không làm sai kết quả gộp** — nó chỉ quyết định bước 4 đi nhánh dịch flow hay nhánh đánh `completed`. Đây chính là lý do hướng gộp từ `content-analytic-daily` được chọn thay vì gọi lại `Update()`.
- Hạ tầng `migration-jobs` bám theo ambassador, không thiết kế lại. Đọc đúng ba file gốc (`internal/model/mg/migration_job.go`, `internal/module/database/mongodb/dao/migration_jobs.go`, `pkg/admin/service/migration_job.go`) rồi port sang — job type khác nhau nhưng khung phải giống để sau này port tiếp các migration khác không phải học lại. Ba điểm được phép khác bản gốc đã liệt kê tường minh ở mục Migration job tracking; ngoài ba điểm đó thì không tự chế biến thể mới.
- Mọi mốc thời gian trong hệ thống dùng đầu ngày theo múi giờ Hồ Chí Minh. Tham số ngày truyền vào phải được chuẩn hóa về đúng mốc này trước khi so khớp, nếu không sẽ không tìm thấy doc nào.
