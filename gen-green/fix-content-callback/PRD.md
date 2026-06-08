## Problem Statement

Khi event/cron của vcreator gửi request crawl số liệu một content cho **một ngày cụ thể** (ví dụ 27/04), service crawl đôi khi callback về **rất muộn** — có trường hợp tới 22/05, cách gần một tháng. Khi callback muộn đó được xử lý, hệ thống ghi số liệu (view/like/comment) **mới nhất** vào ô `content-analytic-daily` của **ngày request gốc (27/04)**.

Vì `content-analytic-daily` là **snapshot tích lũy theo ngày** (mỗi document lưu `View.Begin` đầu ngày / `End` cuối ngày, và `Begin` của ngày sau = `End` của ngày trước — `Begin` của một ngày mới được lấy bằng `End` của document liền trước), việc ghi đè số liệu của ~1 tháng sau vào một ngày quá khứ làm:
- `End` của ngày 27/04 phình to bất thường.
- Phá vỡ tính liên tục `Begin[N] = End[N-1]` của **toàn bộ chuỗi ngày** từ 28/04 → 22/05.

**Bản chất sâu hơn là DOUBLE-COUNTING, không chỉ "ghi sai ô ngày".** Trong khoảng 28/04 → 22/05, cron crawl vẫn chạy bình thường và **lượng view của content đã được tính dồn vào chuỗi các ngày đó rồi** (mỗi ngày `Begin = End[ngày trước]`). Khi callback muộn của 27/04 về vào 22/05 và ghi số liệu mới nhất vào ô 27/04:
- Ô 27/04 nhận một `Value`/`End` lớn, **nhưng các ngày 28/04 → 22/05 KHÔNG được tính lại** (vẫn giữ Begin/End cũ).
- Phần view đó vì vậy **bị đếm hai lần**: một lần đã nằm trong chuỗi 28/04→22/05, một lần nữa ở ô 27/04 vừa ghi đè.

Kết quả: tổng số liệu báo cáo của partner/event **bị thổi phồng (double count)** trên dải ngày rộng — nghiêm trọng hơn so với chỉ "một ngày bị sai".

## Solution

Thêm một **stale-callback guard** vào tiến trình xử lý callback (`ProcessContentCallback`): nếu một callback đến quá muộn so với thời điểm request được ghi nhận, nó được coi là **stale** và bị **bỏ qua hoàn toàn** — không cập nhật content, không tạo content flow, không cập nhật `content-analytic-daily`. Callback stale được đánh dấu `completed` kèm ghi chú lý do, và được đếm vào một metric riêng (`totalStale`) thay vì lẫn vào `totalFailed`.

Ngưỡng stale: **24 giờ** tính từ `ContentCallbackRaw.CreatedAt` (mốc thời điểm request được ghi nhận, KHÔNG bị cập nhật khi callback muộn về) tới thời điểm xử lý. Callback bình thường về trong vài phút–vài giờ; cron xử lý chạy mỗi giờ, nên 24h dư an toàn cho các callback trễ qua đêm/cuối tuần nhưng vẫn chặn được callback trễ cả tháng.

## User Stories

1. As một partner xem báo cáo, I want số liệu daily của mỗi ngày phản ánh đúng giá trị tại ngày đó, so that tôi tin được biểu đồ tăng trưởng view/like/comment.
2. As một event owner, I want số liệu của một ngày quá khứ không bị thay đổi bởi dữ liệu crawl về muộn, so that báo cáo đã chốt không bị "nhảy số" về sau.
3. As một data analyst, I want chuỗi `Begin/End` của `content-analytic-daily` luôn liền mạch (Begin[N] = End[N-1]), so that các phép tính chênh lệch theo ngày không bị âm/sai.
3a. As một partner xem báo cáo tổng, I want lượng view của một content KHÔNG bị đếm hai lần khi callback về muộn, so that tổng view/like/comment không bị thổi phồng. (Phần view của những ngày sau ngày request gốc đã được tính dồn vào chuỗi rồi; ghi lại vào ngày cũ sẽ double-count.)
4. As một vận hành viên (ops), I want callback đến quá muộn được nhận diện và bỏ qua tự động, so that tôi không phải dọn dữ liệu lệch thủ công.
5. As một vận hành viên, I want callback stale được ghi nhận bằng metric riêng (totalStale) tách khỏi totalFailed, so that con số "failed" trong log phản ánh đúng lỗi thật và không bị thổi phồng khi service crawl có backlog.
6. As một vận hành viên, I want callback stale vẫn được đánh dấu `completed` với ghi chú rõ lý do, so that tôi truy vết được vì sao một callback không được áp dụng.
7. As một developer bảo trì, I want logic "callback có quá cũ không" được tách thành một hàm thuần testable, so that tôi kiểm chứng ngưỡng và các biên (boundary) mà không cần dựng DB.
8. As một developer, I want có regression test bao trùm chính kịch bản bug (request 27/04 → callback 22/05), so that bug không tái phát mà không bị test phát hiện.
9. As một vận hành viên, I want record callback thiếu `CreatedAt` (legacy/malformed) được coi là stale và retire, so that các record không xác định được ngày không bao giờ ghi vào một ngày sai.
10. As một event owner ở chế độ extended period, I want guard áp dụng nhất quán cho mọi callback stale, so that hệ thống chỉ có một luồng xử lý duy nhất, dễ suy luận.
11. As một developer, I want ngưỡng stale là một hằng số có comment giải thích, so that người sau hiểu vì sao chọn 24h và điều chỉnh có cơ sở.
12. As một vận hành viên, I want guard chạy sớm (trước khi truy vấn content/event/user), so that các callback stale không tốn query thừa.

## Implementation Decisions

**Module mới (deep module, testable in isolation):**
- Một hàm thuần `isContentCallbackStale(createdAt, now time.Time) bool` cùng hằng số `contentCallbackStaleAfter = 24 * time.Hour`, đặt trong package `service` (pkg/public/service). Interface đơn giản, không phụ thuộc DB, đóng gói toàn bộ quyết định "callback có quá cũ không".
  - Quy ước: `createdAt.IsZero()` → trả về `true` (stale) để retire record legacy không xác định được ngày.
  - Biên: đúng 24h → CHƯA stale (cho phép callback trễ qua đêm). Vượt 24h → stale.

**Module sửa đổi:**
- `ProcessContentCallback` (pkg/public/service): chèn guard ở đầu vòng lặp xử lý từng callback, NGAY SAU khi tăng `totalProcess` và TRƯỚC khi lookup content trong map. Guard chỉ cần `callback.CreatedAt`, không cần content/event đã load.
  - Khi stale: log cảnh báo (link + createdAt), gọi `UpdateStatus(id, "completed", "<ghi chú stale>")`, tăng `totalStale`, `continue`.
  - Thêm biến đếm `totalStale` (tách khỏi `totalFailed`) và một dòng log tổng kết "Total stale skipped: N" ở cuối hàm.

**Quyết định nghiệp vụ (đã chốt với developer):**
- Phương án xử lý số liệu callback muộn: **bỏ qua callback quá cũ** (không gán số liệu mới vào ngày khác). KHÔNG chọn phương án "ghi vào ngày nhận callback" cũng KHÔNG "sửa logic cộng dồn cho ngày cũ".
- Mức bỏ qua: **skip toàn bộ** — không update content, không gọi `CreateFlow`. KHÔNG chọn phương án "chỉ skip CreateFlow nhưng vẫn update content".
- Ngưỡng: **24h (1 ngày)**.
- Metric: **tách `totalStale` riêng**, không lẫn vào `totalFailed`.
- Extended period: **vẫn áp dụng guard** cho mọi callback stale (kể cả extended event ghi vào ngày cố định qua `GetRecordingDate`), để giữ một luồng xử lý nhất quán — chấp nhận đánh đổi rằng extended event cũ cũng không được cập nhật dù vốn không bị lệch.

**Phạm vi:** chỉ **forward-fix** (sửa code để callback từ giờ về sau ghi đúng/bị chặn đúng). KHÔNG backfill dữ liệu đã lệch trong DB.

## Testing Decisions

**Triết lý test:** chỉ test **hành vi bên ngoài** của hàm quyết định — input (createdAt, now) → output (stale hay không) — không test chi tiết triển khai. Logic guard được tách thành hàm thuần chính là để có "correct seam": test exercise đúng quyết định gây ra bug tại call site.

**Module được test:** `isContentCallbackStale`.

Các case tối thiểu:
- Kịch bản bug thực tế: request 27/04, xử lý 22/05 → stale (đây là regression test cốt lõi).
- Vừa quá 24h → stale.
- Đúng 24h (boundary) → KHÔNG stale.
- Vài giờ (callback bình thường) → KHÔNG stale.
- 23h (trễ nhưng trong cửa sổ) → KHÔNG stale.
- `createdAt` zero (legacy/malformed) → stale.

**Prior art:** theo đúng pattern các hàm guard thuần đã có trong codebase — ví dụ `content_guard_test.go` ở pkg/admin/service (test `shouldRunUnRejectGuard`, `buildActiveDuplicateFilter` bằng table-driven test, không cần DB). Test mới đặt cùng package, table-driven, dùng `time.Date` cố định để deterministic.

`ProcessContentCallback` KHÔNG được unit-test trực tiếp vì nó phụ thuộc DAO MongoDB toàn cục (seam quá sâu, test ở đó sẽ cho false confidence). Đây được ghi nhận là giới hạn kiến trúc, không phải thiếu sót.

## Out of Scope

- **Backfill / sửa dữ liệu `content-analytic-daily` đã lệch** trong quá khứ. Bug forward-fix chỉ chặn lệch mới; dữ liệu cũ đã bị double-count nên cần một script **recompute lại toàn bộ chuỗi Begin/End** từ ngày bị xen vào trở đi (không thể patch riêng từng ô) — sẽ là một PRD riêng.
- **Thiết kế lại nguồn gốc bug**: việc dùng chung trường `CreatedAt` cho cả "ngày request" lẫn "mốc thời gian số liệu". Một thiết kế bền hơn là callback mang theo timestamp thật của lần crawl và `ContentAnalyticDaily.Update` nhận một `dataAsOf` rõ ràng. Đề xuất cải thiện kiến trúc, không làm trong PRD này.
- Thay đổi tần suất cron `ProcessContentCallback` hoặc cơ chế giới hạn 55 phút.
- Cảnh báo/alert (Telegram, dashboard) cho tỉ lệ stale cao.

## Further Notes

**Double-count củng cố quyết định "skip toàn bộ":** vì view của những ngày SAU ngày request gốc đã được tính dồn vào chuỗi `content-analytic-daily` rồi, mọi phương án "ghi số liệu callback muộn vào ngày cũ" (kể cả ghi đúng ô 27/04) đều tạo đếm trùng. Đây là lý do KHÔNG chọn phương án "ghi vào ngày nhận callback" hay "sửa logic cộng dồn cho ngày cũ" — chỉ có **bỏ qua hoàn toàn** mới tránh được double-count mà không phải tính lại cả chuỗi.

**Ảnh hưởng tới backfill (out of scope nhưng cần ghi nhận):** vì bug là double-count chứ không chỉ "một ô sai", việc dọn dữ liệu lịch sử KHÔNG thể chỉ sửa riêng ô 27/04 — phải **tính lại toàn bộ chuỗi Begin/End** từ ngày bị xen vào trở đi để gỡ phần đếm trùng. Đây là lý do backfill cần một PRD riêng với cách tiếp cận recompute, không phải patch điểm.

**Trade-off đã biết của lựa chọn "skip toàn bộ":** nếu callback stale là lần crawl gần nhất của một video (ví dụ event đã kết thúc, không còn cron crawl lại), thì `content.statistic` (view/like/comment hiện tại của video) sẽ **đứng yên ở giá trị cũ**. Đây là hệ quả có chủ đích, KHÔNG phải bug — daily không lệch là ưu tiên cao hơn.

**Rủi ro biên 24h × backlog:** ngưỡng tính theo `now` tại lúc XỬ LÝ, không phải lúc callback về. Nếu cron bị backlog nặng (hàm có giới hạn 55 phút rồi break), một callback về đúng giờ nhưng có `CreatedAt` sát 24h và bị xử lý trễ sang hôm sau có thể bị skip oan. Rủi ro thấp với callback bình thường (về trong vài giờ); biên "đúng 24h chưa stale" được chọn để nới nhẹ.

**Rủi ro legacy data:** record `status="waiting"` thiếu `CreatedAt` sẽ bị guard đánh stale hàng loạt. Đã xác minh `InsertContentCallback` luôn set `CreatedAt = now`, nên record waiting mới đều hợp lệ; chỉ cần lưu ý nếu DB còn record waiting rất cũ từ trước khi field này tồn tại.

**Vì sao guard đặt trước lookup content:** chỉ cần `callback.CreatedAt`, đặt sớm giúp bỏ qua các truy vấn content/event/user không cần thiết cho callback stale.

