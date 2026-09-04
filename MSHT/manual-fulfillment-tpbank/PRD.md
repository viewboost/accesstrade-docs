# PRD: Bật lại rút tiền, bỏ qua gọi TPBank (ManualFulfillment)

- **Ngày**: 2026-09-04 (cập nhật lần 2)
- **Trạng thái**: ready-for-agent
- **Tóm tắt ngắn**: [summary.md](./summary.md)
- **Phạm vi repo**: `Cashbag-TPBank/withdraw` (backend, duy nhất — không còn thay đổi `web-admin`)

> **Ghi chú thay đổi so với bản đầu (2026-09-04)**: bản này thay thế thiết kế đầy đủ ban đầu (trạng thái `awaiting_manual` riêng, job export định kỳ, collection `manualFulfillmentExports`, tab web-admin cho MSHT Operator/Kế toán AT) bằng một lát cắt hẹp hơn: tái sử dụng `pending` có sẵn, không job export, không UI web-admin. Đội vận hành tự truy vấn danh sách cần xử lý qua Metabase và nộp kết quả qua 1 API nội bộ mới. Xem mục Out of Scope cho danh sách đầy đủ những gì đã bị bỏ.

## Problem Statement

TPBank đổi phương thức xác thực trên production khiến API chi hộ trực tiếp (`funds/v1.0/authority`) trả lỗi 401. Đội vận hành đã bật `WITHDRAW_DISABLED` để chặn khẩn cấp — nghĩa là mọi request rút tiền hiện tại bị reject cứng ngay lập tức, user bấm "Rút tiền" luôn nhận lỗi, không có trải nghiệm "đang xử lý".

Trong lúc chờ TPBank khắc phục, team cần một cách để user tiếp tục rút được tiền (request được ghi nhận, số dư bị trừ, trải nghiệm không đổi so với bình thường), nhưng **không** phục hồi luồng gọi thẳng TPBank đang lỗi. Việc chi tiền thực tế cho các request này sẽ được xử lý ngoài hệ thống, và kết quả được nạp lại vào hệ thống sau qua một API nội bộ riêng.

## Solution

Thêm 1 flag cấu hình mới `ManualFulfillment`. Khi bật, `NewWithdraw` vẫn validate, tạo bản ghi Withdraw, và trừ tiền user ngay như luồng bình thường (optimistic-deduct không đổi) — nhưng bỏ qua hoàn toàn bước gọi TPBank. Withdraw giữ nguyên trạng thái `pending` sẵn có (không thêm trạng thái mới).

Thêm 1 API nội bộ mới (basic auth riêng, cùng pattern với `/batch-transfer`) nhận file `.xlsx` gồm 2 cột (`request_id`, `result`) để đóng các request `pending` này lại thành `success` hoặc `rejected` (hoàn tiền nếu `rejected`), xử lý đồng bộ, trả về báo cáo theo từng dòng.

## User Stories

1. Là vận hành hệ thống, tôi muốn tắt được `WITHDRAW_DISABLED` mà không phục hồi luồng gọi thẳng TPBank đang lỗi 401, để user có thể tiếp tục rút tiền trong lúc chờ TPBank khắc phục.
2. Là user, khi bấm "Rút tiền" trong giai đoạn xử lý thủ công, tôi muốn request của tôi được nhận, validate (đủ số dư, đúng hạn mức, đúng tài khoản) và số dư bị trừ ngay như bình thường, để trải nghiệm rút tiền không khác biệt so với lúc hệ thống hoạt động bình thường.
3. Là user, tôi không muốn thấy lỗi cứng khi bấm rút tiền trong giai đoạn này (khác với hiện tại khi `WITHDRAW_DISABLED=true`), để tôi biết yêu cầu của mình đã được ghi nhận.
4. Là user, tôi thấy trạng thái `pending` (giống hệt trạng thái đã có, không phải giá trị mới) trong response API/lịch sử giao dịch khi request của tôi đang ở giai đoạn xử lý thủ công, để không cần đội FE (mobile app) cập nhật gì thêm.
5. Là hệ thống rút tiền, khi `ManualFulfillment` bật, tôi muốn bỏ qua hoàn toàn bước gọi TPBank (`TPBankGenerateWithdrawToken`/`TPBankRequestTransfer`), để không tiếp tục gửi request tới một API đang trả 401.
6. Là lập trình viên bảo trì, tôi muốn `ManualFulfillment` là một field cấu hình mới, tách biệt hoàn toàn khỏi `WITHDRAW_DISABLED` (reject cứng, dùng cho bảo trì toàn phần), để giữ khả năng dùng `WITHDRAW_DISABLED` độc lập cho case bảo trì thật sự sau này.
7. Là vận hành hệ thống, tôi muốn tự truy vấn danh sách các Withdraw đang `pending` do `ManualFulfillment` qua Metabase (không cần hệ thống sinh file export riêng), lấy `request_id` (`ClientMessageID`) để đối chiếu và chuyển khoản tay.
8. Là vận hành hệ thống, tôi muốn nộp lại kết quả xử lý (thành công/thất bại) qua 1 file Excel 2 cột (`request_id`, `result`) vào 1 API nội bộ mới, để hệ thống tự động cập nhật trạng thái và số dư tương ứng.
9. Là hệ thống rút tiền, khi nhận file kết quả, tôi muốn xử lý đồng bộ trong request (không chạy nền), trả về ngay báo cáo theo từng dòng (áp dụng được / bị bỏ qua kèm lý do), để vận hành biết ngay dòng nào cần sửa và nộp lại.
10. Là hệ thống rút tiền, với mỗi dòng trong file kết quả, tôi muốn bỏ qua (không dừng cả file) khi: không tìm thấy Withdraw theo `request_id`, Withdraw không còn ở trạng thái `pending`, hoặc giá trị cột `result` không khớp chính xác `success`/`rejected`.
11. Là hệ thống rút tiền, khi nhận kết quả `success` cho một Withdraw `pending`, tôi muốn chuyển trạng thái thành `success`, không đổi thêm số dư (tiền đã trừ từ đầu).
12. Là hệ thống rút tiền, khi nhận kết quả `rejected` cho một Withdraw `pending`, tôi muốn chuyển trạng thái thành `rejected` và hoàn lại số tiền đã trừ trước đó cho user, dùng đúng cơ chế hoàn tiền đã có (`WithdrawErr`), không hoàn 2 lần.
13. Là vận hành hệ thống, tôi muốn API nộp file kết quả dùng basic auth riêng (không dùng chung credential với `/batch-transfer`), theo đúng pattern route nội bộ đã có trong repo.
14. Là vận hành hệ thống, khi TPBank khắc phục xong và tắt `ManualFulfillment`, tôi muốn các Withdraw request mới quay lại gọi TPBank tự động như bình thường; các Withdraw cũ còn `pending` từ giai đoạn thủ công tiếp tục được đóng qua API nộp file kết quả cho tới hết (không có cơ chế tự động chuyển tiếp nào chạy lại chúng qua TPBank).

## Implementation Decisions

- **Cấu hình mới**: `Withdraw.ManualFulfillment` (bool, `env:"WITHDRAW_MANUAL_FULFILLMENT"`, mặc định `false`) trong `internal/config/env_key.go`, cùng struct `Withdraw` với `Disabled`. Field độc lập, không tái sử dụng `Disabled` (giữ nguyên nghĩa "reject cứng toàn phần").

- **Nhánh trong `NewWithdraw`**: giữ nguyên toàn bộ luồng hiện có (validate, lock redis, insert Withdraw với status mặc định hiện tại, `updateUserStats` trừ tiền). Ngay trước bước gọi `TPBankGenerateWithdrawToken`/`TPBankRequestTransfer`, kiểm tra `internalconfig.GetEnv().Withdraw.ManualFulfillment`:
  - Nếu bật: bỏ qua hoàn toàn 2 lời gọi TPBank trên, trả về ngay cho user với `status = pending` (giá trị đã có sẵn, không phải giá trị mới), không lỗi — giống hình dạng response nhánh thành công.
  - Nếu tắt: giữ nguyên luồng hiện tại không đổi (gọi TPBank như cũ).

- **Không thêm trạng thái mới, không thêm field marker trên `WithdrawBSON`**: tái sử dụng `pending` sẵn có. `WithdrawSyncAllPendingStatus` (job định kỳ quét `status = pending` và tra cứu TPBank) hiện đã bị comment-out hoàn toàn trong `app/schedule/schedule.go` (xác nhận qua git log — không chạy trên production), nên không có rủi ro job này tự động poll các bản ghi `ManualFulfillment` không có gì để tra cứu. Nếu job này được bật lại sau này, thêm filter loại trừ khi đó, không làm trước (YAGNI).

- **Không có job export định kỳ, không có collection mới, không có tab web-admin**: đội vận hành tự truy vấn danh sách Withdraw `status = pending` cần xử lý trực tiếp qua Metabase (đã có sẵn quyền truy cập), lấy cột `clientMessageId` làm `request_id`. Đây là điểm khác biệt chính so với bản thiết kế đầu tiên — bản đó có job sinh file `.xlsx` tự động kèm dữ liệu tra cứu sẵn; bản này bỏ hẳn phần đó.

- **API nộp file kết quả (nội bộ, basic auth riêng)**: 1 endpoint mới, ví dụ `POST /withdraw/manual-fulfillment/result`, theo đúng pattern route hiện có của `/batch-transfer` (`app/route/withdraw.go`): `middleware.BasicAuth` với credential riêng (`ManualFulfillment.Auth.{Username,Password}` trong config, không dùng chung `BatchTransfer.Auth`), nhận file qua `externalmiddleware.UploadSingle("file", []string{".xlsx"})`.

- **Định dạng file kết quả**: `.xlsx`, đúng 2 cột:
  - `request_id`: giá trị `ClientMessageID` của Withdraw (vận hành copy trực tiếp từ Metabase).
  - `result`: `success` hoặc `rejected`, so khớp chính xác (case-sensitive, không nhận biến thể).

- **Xử lý đồng bộ, không chạy nền**: khác với `WithdrawBatchTransfer` (chạy `go func()`, trả `200` ngay). API này xử lý toàn bộ file ngay trong request và trả về báo cáo kết quả theo từng dòng trước khi response — vì đây là thao tác low-volume, vận hành cần biết ngay kết quả để sửa và nộp lại nếu có dòng lỗi.

- **Xử lý từng dòng**:
  - Đọc file bằng `tealeg/xlsx` (đã có sẵn trong `go.mod`, cùng thư viện `WithdrawBatchTransferFromFile` đang dùng).
  - Nếu `result` rỗng hoặc không khớp chính xác `success`/`rejected` → bỏ qua dòng, ghi nhận lý do "invalid result value".
  - Tìm Withdraw theo `ClientMessageID = request_id`. Không tìm thấy → bỏ qua, ghi nhận "request_id not found".
  - Nếu tìm thấy nhưng `status != pending` → bỏ qua, ghi nhận "already processed" (guard chống xử lý 2 lần, tự nhiên hỗ trợ nộp lại file idempotent — dòng đã xử lý ở lần trước tự động bị bỏ qua ở lần sau).

    Ghi chú: đây không phải cùng cơ chế với `WithdrawBatchTransfer` — API nộp file kết quả này là mới hoàn toàn, không sửa route/handler `/batch-transfer` hiện có.

  - `result = success` → set `status = success`, không đổi số dư (đã trừ từ đầu), `PushWithdrawNotification` (theo đúng pattern nhánh thành công hiện có).
  - `result = rejected` → set `status = rejected`, hoàn tiền qua `updateUserStats(w, w.Cash, true)` (logic giống hệt `WithdrawErr`, tái dùng để không viết lại), `PushWithdrawNotification`.
  - Response: danh sách theo từng dòng, mỗi dòng gồm `request_id` (nếu đọc được), kết quả áp dụng (`applied`/`skipped`) và lý do nếu bị bỏ qua.

- **Response cho user không đổi**: `NewWithdraw` không đổi shape response khi `ManualFulfillment` bật — status trả về vẫn là `pending` như trước giờ khi bank call chưa có kết quả, không có giá trị mới nào lộ ra client/mobile app.

- **Rollback khi hết sự cố**: tắt `ManualFulfillment` chỉ dừng việc tạo mới các request bỏ qua TPBank — request mới trở lại đi qua TPBank tự động ngay. Các Withdraw đang `pending` tồn đọng từ giai đoạn thủ công **không** tự động được gọi lại qua TPBank — tiếp tục đóng qua API nộp file kết quả cho tới khi hết tồn đọng.

## Testing Decisions

- **Guard `ManualFulfillment` trong `NewWithdraw`**: test rằng khi bật, không có lời gọi nào tới `TPBankGenerateWithdrawToken`/`TPBankRequestTransfer` được thực hiện; Withdraw vẫn được insert và số dư vẫn bị trừ đúng như luồng bình thường; status trả về là `pending`. Test qua effect (side-effect không xảy ra) hoặc qua cơ chế fake hiện có của repo cho các hàm TPBank, theo đúng cách các nhánh trạng thái khác (`errUserNotEnoughCash`, `errWithdrawDisabled`, ...) đang được test.
- **Hàm xử lý file kết quả**: tách thành 1 hàm thuần (nhận danh sách row đã parse, không phụ thuộc HTTP context — cùng pattern `WithdrawBatchTransferFromFile` tách phần đọc file khỏi phần xử lý business), test trực tiếp đồng bộ (không cần test qua HTTP): map đúng `success` → không đổi số dư, `rejected` → hoàn tiền đúng 1 lần, `request_id` không tìm thấy/`status` không phải `pending`/`result` không hợp lệ → bị bỏ qua có báo cáo rõ ràng, không panic, không cập nhật nhầm.
- **Tiền lệ trong codebase**: `WithdrawErr` đã có logic hoàn tiền với guard tương tự — tái dùng nguyên xi (`updateUserStats(w, w.Cash, true)`), không viết lại từ đầu. `WithdrawBatchTransferFromFile`/`appmodel.TransferExcelRecord` là tiền lệ trực tiếp cho việc đọc `.xlsx` bằng `row.ReadStruct`.
- Không cần test tầng HTTP/route đầy đủ (basic auth, request/response marshal, multipart upload) cho scope này — theo pattern các API nội bộ khác trong repo hiện cũng không có test tầng route riêng.

## Out of Scope

- Trạng thái `awaiting_manual` riêng biệt — bỏ hẳn, tái sử dụng `pending` có sẵn.
- Job định kỳ sinh file export tự động, collection Mongo `manualFulfillmentExports`, cơ chế `ResultRuns`/audit trail nhiều lần nộp — bỏ hẳn.
- Tab web-admin "Rút tiền thủ công", xác nhận TOTP, actor Kế toán AT/MSHT Operator — bỏ hẳn. Vận hành thao tác trực tiếp qua Metabase + API nội bộ, không qua UI.
- Marker field (`SentToTP` hoặc tương đương) để loại trừ khỏi `WithdrawSyncAllPendingStatus` — không cần vì job này đã bị comment-out hoàn toàn, không chạy trên production.
- Hạn mức rút tiền riêng cho giai đoạn thủ công — giữ nguyên hạn mức hiện tại, không áp thêm giới hạn mới.
- Tạm dừng cơ chế ICB (Instant Cashback) trong giai đoạn thủ công — không thuộc phạm vi thay đổi code của spec này.
- Cơ chế chặn rút trùng ở tầng hệ thống — vẫn dựa vào optimistic-deduct hiện có (check `u.Stats.CurrentCash < cash`), không thêm cơ chế mới.
- Thông báo in-app/banner cho user về thời gian xử lý kéo dài — thuộc phạm vi FE, không thuộc scope backend này.
- Thay đổi bất kỳ gì ở repo `web-admin` — bản thiết kế đầu tiên có yêu cầu tab mới ở `web-admin`; bản này không cần, phạm vi chỉ còn repo `withdraw`.

## Further Notes

- Tài liệu này đã được cập nhật để thay thế thiết kế trước đó (trạng thái `awaiting_manual`, job export, tab web-admin, actor Kế toán AT/MSHT Operator) bằng lát cắt hẹp hơn ở trên — xem mục Out of Scope cho danh sách đầy đủ những gì đã bị bỏ.
- Thuật ngữ `ManualFulfillment` trong `CONTEXT.md` (repo `withdraw`) đã được cập nhật lại để khớp với thiết kế mới (bỏ `awaiting_manual`, Kế toán AT, MSHT Operator; thêm **Manual Resolution Upload** cho API nộp file kết quả).
- Không phụ thuộc FE: client/mobile app không thấy giá trị status mới nào ở bất kỳ thời điểm nào trong luồng này.
