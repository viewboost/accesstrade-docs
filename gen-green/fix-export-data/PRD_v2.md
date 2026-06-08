# PRD — Update Flow Export Data (Độ tin cậy hàng đợi Export)

**Ngày:** 08/06/2026

## Problem Statement

Trên trang Admin, team vận hành dùng chức năng "Xuất dữ liệu" (Data Export) để xuất nhiều loại báo cáo sang CSV/XLSX: nội dung, đối soát (reconciliation), người dùng theo partner, giao dịch rút/nạp, các loại chart. Đây là dữ liệu cần hàng ngày để chốt số và báo cáo KPI.

Nhưng hàng đợi export thường xuyên bị **kẹt cứng**:

- Bấm "Export" → đơn treo ở trạng thái **Running** hoặc **Waiting** mãi không xong.
- Mọi đơn tạo sau đó cũng kẹt theo, không đơn nào chạy được nữa.
- Cách duy nhất để gỡ là **báo dev restart server backend** — và restart xong vẫn còn xác suất kẹt lại, hoặc phải đợi tới **1 tiếng** (chu kỳ cron) thì đơn kế tiếp mới chạy.

Hệ quả: team vận hành mất giờ chờ data, phải mở ticket nhờ dev can thiệp database thủ công, ảnh hưởng trực tiếp tới tiến độ công việc.

## Solution

Biến cơ chế export từ "kẹt cứng khi sự cố" thành **tự phục hồi**, mà không thay đổi trải nghiệm tạo export của người dùng:

- **Tự dọn khi server khởi động lại:** mỗi lần backend bật lên, mọi đơn còn ghi nhận Running (chắc chắn là zombie vì process đã chết) được đưa về Waiting và kích hoạt một vòng pick ngay — không cần đợi cron, không cần can thiệp tay.
- **Nhịp tim phát hiện đơn chết (heartbeat):** khi một đơn vào Running, tiến trình xử lý "đập nhịp tim" mỗi phút. Đơn nào ngừng đập nhịp quá 3 phút (tiến trình đã chết) tự bị đánh **Failed** kèm lý do, giải phóng slot. Khác với mốc timeout cứng trước đây, đơn export nặng chạy lâu nhưng **vẫn còn đập nhịp** thì KHÔNG bị đánh nhầm — phân biệt được "chạy lâu hợp lệ" với "đã chết".
- **Không hồi sinh đơn đã bị dọn:** nếu một đơn bị đánh Failed (do mất nhịp tim) nhưng tiến trình thật sau đó vẫn chạy xong, hệ thống KHÔNG ghi đè kết quả lên trạng thái đã dọn — tránh trạng thái lẫn lộn.
- **Tự chạy đơn kế tiếp:** sau khi một đơn xong (thành công hay thất bại), hệ thống tự pick đơn Waiting kế tiếp ngay, queue chạy liên tục.
- **Chống crash dây chuyền:** toàn bộ luồng điều phối và xử lý export được bọc panic recovery — một đơn lỗi không kéo cả queue chết theo, và sửa một bug đóng file sai thứ tự từng làm crash tiến trình.
- **Khóa đồng bộ toàn cluster:** chỉ một tiến trình điều phối (`CheckRun`) được chạy tại một thời điểm trên toàn cluster nhờ Redis lock, đảm bảo đúng giới hạn 2 đơn chạy song song và không có đơn nào bị xử lý trùng.
- **Điều phối thường xuyên hơn:** cron quét hàng đợi đổi từ mỗi 1 giờ → mỗi 5 phút, rút ngắn thời gian phục hồi khi có sự cố hoặc backlog tồn đọng.

Với người dùng: đơn export không còn kẹt; đơn export nặng không bị đánh Failed nhầm; nếu có lỗi thì đơn ghi rõ lý do (mất nhịp tim, panic, server restart) để biết mà tạo lại; data về đúng hạn mà không cần nhờ dev.

## User Stories

1. Là nhân viên vận hành, tôi muốn tạo một đơn export và thấy nó được chạy ngay khi có slot trống, để tôi không phải đợi cron.
2. Là nhân viên vận hành, tôi muốn đơn export của mình chạy xong là đơn kế tiếp trong hàng đợi tự động chạy, để cả batch báo cáo hoàn tất liên tục không ngắt quãng.
3. Là nhân viên vận hành, khi backend được restart trong lúc đơn của tôi đang chạy, tôi muốn đơn đó tự được đưa lại vào hàng đợi và chạy lại, để tôi không phải tạo lại thủ công.
4. Là nhân viên vận hành, tôi muốn một đơn mà tiến trình xử lý đã chết (ngừng đập nhịp tim quá 3 phút) tự chuyển sang Failed kèm lý do, để hàng đợi không bị một đơn zombie chặn vĩnh viễn.
5. Là nhân viên vận hành xuất báo cáo nặng (vài triệu dòng), tôi muốn đơn của mình KHÔNG bị đánh Failed nhầm chỉ vì chạy lâu, miễn là tiến trình vẫn còn sống (vẫn đập nhịp tim), để báo cáo lớn vẫn hoàn tất được.
6. Là nhân viên vận hành, tôi muốn nhìn thấy lý do thất bại rõ ràng trên đơn (mất nhịp tim/stale, server restarted, panic), để biết nên tạo lại hay báo dev.
7. Là nhân viên vận hành, tôi muốn các đơn export khác vẫn chạy bình thường ngay cả khi một đơn gặp lỗi bất ngờ, để một báo cáo hỏng không làm hỏng cả ngày làm việc.
8. Là quản lý vận hành, tôi muốn không còn phải mở ticket nhờ dev "sửa DB cho export", để team tự chủ và giảm phụ thuộc kỹ thuật.
9. Là admin root, tôi muốn cơ chế điều phối tôn trọng giới hạn 2 đơn chạy song song trên toàn cluster, để không quá tải storage/DB khi chạy nhiều instance admin.
10. Là admin root, tôi muốn đơn được pick theo thứ tự FIFO (đơn tạo trước chạy trước), để công bằng và dễ dự đoán.
11. Là dev backend, tôi muốn chỉ một `CheckRun` chạy tại một thời điểm trên toàn cluster, để tránh race condition khiến một đơn bị chạy hai lần hoặc vượt giới hạn slot.
12. Là dev backend, tôi muốn một helper Redis lock "thử một lần rồi bỏ qua nếu đang chạy" thay vì block chờ, để các trigger `CheckRun` chồng nhau không xếp hàng tốn tài nguyên.
13. Là dev backend, tôi muốn `CheckRun` bỏ qua (skip) khi đã có tiến trình khác giữ lock, vì defer của đơn đang chạy sẽ gọi lại `CheckRun` nên không bị mất tín hiệu pick.
14. Là dev backend, tôi muốn `CheckRun` và `RunExport` được bọc panic recovery, để một panic không làm chết goroutine và đứng hình toàn bộ hàng đợi.
15. Là dev backend, tôi muốn bug `defer f.Close()` đặt trước nil-check được sửa, để khi tạo file thất bại tiến trình không panic vì close một file nil.
16. Là dev vận hành, khi server bật lên tôi muốn một vòng `CheckRun` được trigger ngay sau khi requeue zombie, để backlog được xả tức thì thay vì đợi cron.
17. Là dev vận hành, tôi muốn job requeue do restart mang lý do "server restarted - requeued", để phân biệt với đơn thất bại do mất nhịp tim hay panic khi truy vết.
18. Là dev vận hành, tôi muốn đơn bị reap mang lý do "recovered: job ngừng heartbeat (stale)", để biết nguyên nhân là tiến trình chết chứ không phải lỗi nghiệp vụ.
19. Là dev backend, tôi muốn đơn bị reap KHÔNG tự retry, để tránh loop vô hạn khi nguyên nhân là bug/data lỗi cố hữu cần can thiệp.
20. Là người dùng tạo export, tôi muốn link tải về (presigned URL) chỉ hoạt động khi đơn ở trạng thái Completed, để không tải nhầm file dở dang.
21. Là dev backend, tôi muốn `CheckRun` chạy bước reap (đánh thất bại đơn mất nhịp tim) ở đầu mỗi lượt điều phối, để slot được giải phóng trước khi đếm và pick.
22. Là dev backend, tôi muốn bước cập nhật trạng thái cuối của `RunExport` có guard `status == running` để không ghi đè nhầm khi đơn đã bị reap, để không tạo trạng thái lẫn lộn (Completed đè lên Failed).
23. Là dev vận hành, tôi muốn cron điều phối chạy mỗi 5 phút thay vì mỗi giờ, để thời gian phục hồi worst-case khi có sự cố được rút ngắn đáng kể.
24. Là dev vận hành sau khi deploy heartbeat, tôi muốn các đơn Running cũ (trước deploy, thiếu trường nhịp tim) vẫn được reaper dọn, để không còn đơn legacy kẹt vĩnh viễn vì thiếu dữ liệu heartbeat.
25. Là dev backend, tôi muốn ghi nhận `startedAt` (thời điểm bắt đầu chạy) và `heartbeatAt` (nhịp tim cuối) trên mỗi đơn, để có dữ liệu phân biệt đơn chạy lâu hợp lệ với đơn chết và truy vết khi cần.

## Implementation Decisions

**Mô hình hàng đợi giữ nguyên.** Vẫn dùng MongoDB collection `data_export` làm queue với state machine `Waiting → Running → Completed | Failed`, giới hạn `MAX_CONCURRENT = 2` đơn Running đồng thời. Điều phối qua `CheckRun`, được trigger từ ba nguồn: API tạo export, cron `RunExportData`, và defer của `RunExport` sau khi một đơn kết thúc.

**Module được build/sửa:**

- **Schema `data_export`** — thêm 2 trường: `startedAt` (thời điểm đơn vào Running) và `heartbeatAt` (nhịp tim cuối cùng). Cả hai dùng `omitempty` để đơn cũ trước migration không gây lỗi unmarshal.
- **Redis mutex module** — thêm một biến thể lock mới `NewMutexNoRetry(name, expiration)`: chỉ thử lock một lần (`WithTries(1)`) thay vì retry 10 lần như các helper cũ. Lock fail trả lỗi ngay để caller tự quyết định bỏ qua. Đây là primitive cho semantic "skip nếu đang chạy".
- **Export job lifecycle (deep module)** — đây là module nghiệp vụ sâu nhất, gom toàn bộ logic chuyển trạng thái và phục hồi:
  - `ResetOrphanedRunning(ctx)` — chỉ gọi ở bootstrap. Đưa MỌI đơn Running về Waiting (zombie chắc chắn vì goroutine `RunExport` đã chết sau restart), set reason `"server restarted - requeued"`, rồi trigger ngay một `CheckRun` để pick đơn vừa requeue mà không đợi cron.
  - `ResetStaleRunning(ctx)` — chỉ gọi trong `CheckRun` (server đang sống). Đánh **Failed** các đơn Running mất nhịp tim, set reason `"recovered: job ngừng heartbeat (stale)"`. Điều kiện reap: `heartbeatAt < now - heartbeatStaleThreshold` (3 phút) **HOẶC** đơn thiếu hẳn `heartbeatAt` (đơn legacy trước deploy — `$lt` không khớp document thiếu field nên cần thêm `$exists:false`). KHÔNG reset về Waiting để tránh retry vô hạn.
  - Hai hàm này phân biệt theo ngữ cảnh: restart ⇒ zombie ⇒ an toàn requeue; mất nhịp tim khi đang sống ⇒ nghi lỗi cố hữu ⇒ fail không retry.
- **CheckRun (điều phối)** — bọc bằng Redis single-flight + panic recovery:
  - Lấy `NewMutexNoRetry(checkRunLockKey, checkRunLockExpiration)`; nếu lock fail thì `return` (skip), không xếp hàng. `defer Unlock()`.
  - `defer recover()` log panic, không cho panic thoát ra giết goroutine.
  - Chạy `ResetStaleRunning` đầu lượt, rồi đếm Running, nếu `>= 2` thì dừng; ngược lại pick một đơn Waiting theo FIFO (`_id` tăng) và gọi `RunExport` **đồng bộ** (blocking trong cùng lock).
- **RunExport (worker)** — bổ sung robustness + heartbeat:
  - Khi vào Running: set `status=running`, `startedAt`, `heartbeatAt` atomic trong cùng một update (nên không có cửa sổ "running nhưng thiếu heartbeat" cho đơn mới).
  - Khởi động một goroutine **ticker** đập `heartbeatAt = now` mỗi `heartbeatInterval` (1 phút), với điều kiện filter `status == running` (nếu đơn đã bị reap thì update là no-op, không hồi sinh). Ticker dừng qua `close(stopHeartbeat)` ở defer cuối — không rò rỉ goroutine kể cả khi panic.
  - `defer recover()` bắt panic, ghi vào `reason` dạng `"panic: ..."`.
  - **Guard `status == running`** ở bước cập nhật trạng thái cuối: nếu đơn đã bị reap (Failed) thì update cuối là no-op, không ghi đè Completed lên Failed.
  - Sau khi đơn kết thúc, `go e.CheckRun()` để pick đơn kế tiếp ngay (drain liên tục).
  - Sửa thứ tự `defer f.Close()`: đặt **sau** nil-check `os.Create` để không close file nil khi tạo file thất bại.
- **Cron điều phối** — `RunExportData` đổi lịch từ `0 0 */1 * * *` (mỗi giờ) sang `0 */5 * * * *` (mỗi 5 phút).
- **Bootstrap** — gọi `service.ResetOrphanedRunning(context.Background())` trước khi đăng ký route, để dọn zombie ngay khi server lên.

**Hằng số (encode trong code, không đưa vào env theo quyết định):**
```
heartbeatInterval        = 1 * time.Minute    // ticker đập nhịp tim mỗi phút khi đang chạy
heartbeatStaleThreshold  = 3 * time.Minute    // heartbeatAt cũ hơn ngưỡng này ⇒ reap (= 3 × interval, chịu 1-2 nhịp lỡ)
checkRunLockKey          = "export:check_run_lock"
checkRunLockExpiration   = 35 * time.Minute   // PHẢI bao trọn thời gian 1 job chạy đồng bộ trong lock — xem quyết định kiến trúc
MAX_CONCURRENT           = 2                   // giữ nguyên hành vi hiện tại
```

**Quyết định kiến trúc:**

- **Heartbeat thay timeout cứng:** thiết kế cũ (PR #72) reap theo `updatedAt` cũ hơn 30 phút — dễ đánh Failed nhầm đơn export nặng chạy >30 phút. Heartbeat phân biệt được "chạy lâu hợp lệ" (vẫn đập nhịp) với "đã chết" (ngừng đập), giảm ngưỡng phát hiện job chết từ ≤30 phút xuống ≤3 phút mà không reap nhầm.
- **Redis là dependency bắt buộc** cho cơ chế khóa. Nếu Redis chết, `CheckRun` bị skip cho tới khi Redis sống lại — an toàn (không double-run) nhưng queue tạm dừng. Chấp nhận được vì đây là chức năng nội bộ vận hành.
- **`RunExport` chạy ĐỒNG BỘ bên trong lock `CheckRun`** ⇒ `checkRunLockExpiration` phải đủ lớn để bao trọn thời gian chạy 1 job export nặng (giữ 35 phút). Nếu lock hết hạn giữa lúc job đang chạy, instance khác sẽ chiếm được lock → mất tính single-flight (pick trùng, unlock nhầm lock của instance khác). Đây là lý do KHÔNG giảm lock xuống vài phút. (Nếu sau này tách `RunExport` ra chạy ngoài lock thì mới giảm được — xem Out of Scope.)
- **Heartbeat update có guard `status == running`** ⇒ ticker và bước reap không bao giờ "hồi sinh" một đơn đã bị dọn. Bước cập nhật cuối cũng dùng cùng guard ⇒ không có trạng thái Completed đè lên Failed.
- **Skip thay vì queue** cho các `CheckRun` chồng nhau: vì defer của `RunExport` luôn gọi lại `CheckRun`, không có tín hiệu pick nào bị mất khi một lượt bị skip.
- **Phân biệt reason theo nguyên nhân** (`server restarted - requeued`, `recovered: job ngừng heartbeat (stale)`, `panic: ...`) làm thành kênh observability tối thiểu cho vận hành truy vết.

## Testing Decisions

**Triết lý test:** chỉ test hành vi bên ngoài quan sát được (đơn chuyển trạng thái nào, với reason gì, slot được giải phóng hay không), KHÔNG test chi tiết triển khai (tên hàm nội bộ, số lần gọi DAO). Test phải sống sót qua refactor miễn là hành vi queue giữ nguyên.

**Module được test (ưu tiên theo quyết định của user):**

- **Export job lifecycle (deep module — bắt buộc test):** `ResetOrphanedRunning` và `ResetStaleRunning` là logic nghiệp vụ thuần nhất, dễ cô lập nhất, và là nơi chứa rủi ro cao nhất (chuyển sai trạng thái ⇒ kẹt hoặc mất data). Các kịch bản:
  - `ResetOrphanedRunning`: cho N đơn Running ⇒ tất cả thành Waiting với reason `"server restarted - requeued"`; đơn ở trạng thái khác không bị động.
  - `ResetStaleRunning`: đơn Running `heartbeatAt` cũ hơn 3 phút ⇒ Failed với reason stale; đơn Running còn đập nhịp (heartbeatAt gần đây) KHÔNG bị động dù `startedAt` đã rất lâu; đơn Running legacy thiếu `heartbeatAt` ⇒ vẫn bị reap (nhánh `$exists:false`); đơn Waiting/Completed không bị động.
  - Để test cô lập không cần Mongo thật, cần inject được DAO (qua interface) và thời gian (clock provider) — ghi nhận đây là khoản refactor nhỏ để mở khóa khả năng test cho deep module này.

> Lưu ý: bản cập nhật heartbeat này được ship theo quyết định "không quan tâm test" — mỗi task chỉ verify bằng `go build`/`go vet`. Các kịch bản trên giữ lại làm nguồn sinh test case khi quay lại bổ sung test.
- **CheckRun điều phối (test khi có thể):** với 0 Running + ≥1 Waiting ⇒ một đơn được pick (Running); với 2 Running ⇒ không pick thêm; pick theo FIFO. Phần Redis lock có thể test bằng Redis thật (integration) hoặc mock; semantic cần khẳng định là "hai `CheckRun` đồng thời ⇒ chỉ một đơn được claim".
- **RunExport robustness (test khi có thể):** inject lỗi/panic ở bước xử lý ⇒ đơn kết thúc ở Failed với reason chứa thông điệp panic, và `CheckRun` kế tiếp vẫn được trigger; tạo file thất bại ⇒ không panic vì close file nil.

**Prior art trong codebase:** tham chiếu các test service hiện có trong `pkg/admin/service` (theo pattern test có sẵn của dự án) cho cách dựng fixture Mongo/mock DAO. Tài liệu `data-export.prd` đã định nghĩa các acceptance criteria dạng AC-xx có thể tái dùng làm nguồn sinh test case cho phần lifecycle.

## Out of Scope

Các phần của `data-export.prd` **chưa** triển khai trong bản cập nhật này (cố ý để lại):

- **Atomic claim bằng `FindOneAndUpdate`** (FR-05 của `data-export.prd`): hiện vẫn pick đơn bằng `FindOne` rồi `UpdateOne` riêng. An toàn nhờ Redis lock đảm bảo single-flight, nhưng chưa atomic ở tầng DB. Để lại làm cải tiến tương lai.
- **Drain-loop nhiều đơn/lượt** (FR-06): một lượt `CheckRun` vẫn pick 1 đơn; backlog được xả liên tục nhờ defer `go CheckRun()` thay vì vòng lặp trong một lượt.
- **Compound index `{status, _id}`** (MIG-02): hiện chỉ có index `status` đơn. Để lại.
- **Tách `RunExport` chạy NGOÀI lock `CheckRun`** — sẽ cho phép giảm `checkRunLockExpiration` xuống vài phút (lock chỉ cần bao bước điều phối, không bao thời gian chạy job). Hiện giữ kiến trúc đồng bộ + lock 35 phút.

Ngoài phạm vi chung:

- **Chạy song song thật nhiều `RunExport`** trong cùng process — hiện đồng bộ tuần tự, đủ dùng.
- **Chuyển sang message queue chuyên dụng** (Asynq/Redis) với retry/dead-letter/dashboard chuẩn — chỉ làm khi export thành nút nghẽn.
- **Gửi email thông báo** khi export xong (field `emails` đã tồn tại nhưng ngoài phạm vi).
- **Auto-retry đơn Failed** do reap — cố ý không làm để tránh loop vô hạn.
- **Đưa các hằng số (heartbeat, lock key, concurrency) vào env/config** — hardcode theo quyết định hiện tại.
- Các luồng upload/import khác.

## Further Notes

- **Đã giải quyết "reap nhầm job nặng":** điểm yếu của PR #72 (mốc timeout cứng 30 phút có thể đánh Failed nhầm đơn export nặng chạy >30 phút) đã được xử lý bằng heartbeat — đơn vẫn đập nhịp thì không bị reap dù chạy bao lâu.
- **Đã giải quyết "hồi sinh đơn đã reap":** bước cập nhật trạng thái cuối của `RunExport` nay có guard `status == running`; ticker heartbeat cũng dùng cùng guard. Không còn rủi ro Completed đè lên Failed.
- **Migration đơn legacy:** đơn Running cũ (trước deploy) thiếu `heartbeatAt`. Reaper xử lý qua nhánh `$exists:false`; ngoài ra `ResetOrphanedRunning` ở bootstrap cũng requeue mọi Running về Waiting khi server restart. Không cần script migration thủ công nếu có một lần restart sau deploy.
- **Ràng buộc lock 35 phút:** vì `RunExport` chạy đồng bộ trong lock, `checkRunLockExpiration` giữ 35 phút làm biên an toàn cho job export lớn nhất. Nếu trong tương lai có job export dự kiến chạy >35 phút, phải tăng giá trị này (hoặc tách job ra ngoài lock) — nếu không lock sẽ hết hạn giữa chừng và mất single-flight.
- **Files thay đổi:**
  - [internal/model/mg/export.go](../../backend/internal/model/mg/export.go) — thêm field `startedAt`/`heartbeatAt`.
  - [pkg/admin/service/export.go](../../backend/pkg/admin/service/export.go) — heartbeat ticker, reaper theo nhịp tim, guard status, hằng số, Redis lock.
  - [pkg/admin/schedule/init.go](../../backend/pkg/admin/schedule/init.go) — cron 5 phút.
  - [pkg/admin/server/bootstrap.go](../../backend/pkg/admin/server/bootstrap.go) — reset zombie khi khởi động (từ PR #72).
  - [internal/module/redis/mutex.go](../../backend/internal/module/redis/mutex.go) — helper `NewMutexNoRetry` (từ PR #72).
- **Triển khai:** chi tiết task-by-task xem [plan heartbeat](../superpowers/plans/2026-06-08-update-flow-export-data.md).
