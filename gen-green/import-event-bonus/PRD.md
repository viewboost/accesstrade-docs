# PRD: Import Event Bonus từ Excel (Preview + Apply + Rollback + History)

## Problem Statement

Hiện admin vcreator chỉ có thể tạo từng event-bonus thủ công qua form CRUD trên trang `/bonus`. Khi cần phát thưởng hàng loạt cho nhiều user trong một sự kiện (event), nhân viên vận hành phải nhập tay từng dòng — vừa chậm, vừa dễ sai số tiền/ngày hết hạn, lại không có cách nào xem trước (preview) toàn bộ lô trước khi ghi vào hệ thống, và nếu lỡ tạo nhầm thì không có cơ chế hoàn tác cả lô. Đối tác (partner) cũng cần đảm bảo chỉ phát thưởng đúng cho các event thuộc phạm vi quyền của mình.

## Solution

Bổ sung chức năng **Import Event Bonus từ file Excel** cho admin vcreator theo luồng có kiểm soát: **upload → preview (dry-run, validate từng dòng) → apply → rollback**, kèm một trang **lịch sử import**.

Nhân viên tải lên một file `.xlsx` (mỗi dòng là một bonus với EventID/UserID dạng hex MongoDB ID), hệ thống parse và validate từng dòng, hiển thị bảng xem trước phân loại rõ dòng nào sẽ **tạo mới** và dòng nào **lỗi** (kèm lý do). Sau khi rà soát, nhân viên bấm **Áp dụng** để ghi toàn bộ dòng hợp lệ thành event-bonus (status `pending`), hoặc **Hủy** để bỏ lô. Mọi lô import được lưu lịch sử; lô đã áp dụng có thể **Hoàn tác** — các bonus đã tạo sẽ chuyển sang status `rejected` (giữ audit, không xóa cứng).

Apply và rollback chạy **bất đồng bộ** (background goroutine + Redis mutex để an toàn cross-pod): khi bấm, hệ thống khóa nguyên tử trạng thái lô và trả về ngay, lô chuyển sang `applying` / `rolling_back`; UI **poll tiến độ** (mỗi 3 giây) cho tới khi hoàn tất. Nhờ vậy lô lớn không làm treo request và admin thấy được trạng thái đang chạy.

Tính năng mượn template Excel hex-ID của ambassador, tái dùng pattern preview/history của `employee-registry`, nhưng đơn giản hóa logic phân loại: chỉ 2 action `new_record` / `invalid`, không match/update phức tạp.

## User Stories

1. Là nhân viên vận hành (operations staff), tôi muốn mở trang `/bonus` và thấy nút "Import Excel", để tôi bắt đầu nhập thưởng hàng loạt thay vì tạo từng dòng.
2. Là nhân viên vận hành, tôi muốn một modal hướng dẫn rõ định dạng file (`.xlsx` với các cột EventID, UserID, Amount, ExpiredAt `DD/MM/YYYY HH:MM:SS`, Note, Reason; dòng đầu là tiêu đề), để tôi chuẩn bị file đúng ngay từ đầu.
3. Là nhân viên vận hành, tôi muốn chọn đúng một file `.xlsx` để tải lên, để tránh nhầm lẫn nhiều file trong một lần import.
4. Là nhân viên vận hành, tôi muốn hệ thống từ chối file không phải `.xlsx` hoặc file hỏng với thông báo rõ ràng, để tôi biết sửa lại file.
5. Là nhân viên vận hành, tôi muốn hệ thống chặn file vượt quá 5000 dòng dữ liệu với thông báo cụ thể, để tránh import quá tải.
6. Là nhân viên vận hành, tôi muốn hệ thống chặn file vượt quá 10MB, để tránh upload file bất thường.
7. Là nhân viên vận hành, sau khi upload tôi muốn được chuyển ngay sang trang xem trước (preview) của lô import đó, để rà soát trước khi ghi dữ liệu.
8. Là nhân viên vận hành, tôi muốn thấy số liệu tổng hợp ở đầu trang preview (tổng dòng, số dòng sẽ tạo mới, số dòng lỗi), để nắm nhanh chất lượng lô import.
9. Là nhân viên vận hành, tôi muốn mỗi dòng trong preview hiển thị trạng thái rõ ràng — "Tạo mới" (xanh) hoặc "Lỗi" (đỏ), để biết dòng nào sẽ được áp dụng.
10. Là nhân viên vận hành, tôi muốn dòng lỗi hiển thị lý do cụ thể (thiếu EventID, thiếu UserID, Amount không hợp lệ, ExpiredAt sai định dạng, thiếu Reason, Event không tồn tại, User không tồn tại, không có quyền với event), để tôi biết sửa gì trong file.
11. Là nhân viên vận hành, tôi muốn preview hiển thị tên Event và tên User (thay vì chỉ hex ID) khi resolve được, để dễ kiểm tra trực quan đúng người đúng sự kiện.
12. Là nhân viên vận hành, tôi muốn thấy số tiền định dạng theo locale Việt Nam và ngày hết hạn ở mỗi dòng, để rà soát giá trị thưởng.
13. Là nhân viên vận hành, tôi muốn lọc danh sách preview theo trạng thái (chỉ tạo mới / chỉ lỗi), để tập trung xử lý từng nhóm.
14. Là nhân viên vận hành, tôi muốn tìm kiếm trong preview theo EventID / UserID / tên User, để định vị nhanh một dòng cụ thể trong lô lớn.
15. Là nhân viên vận hành, tôi muốn phân trang danh sách preview, để xem được lô có nhiều dòng mà không treo trình duyệt.
16. Là nhân viên vận hành, tôi muốn bấm "Áp dụng" với xác nhận số lượng bonus sẽ được tạo, để chủ động trước khi ghi dữ liệu.
17. Là nhân viên vận hành, tôi muốn nút "Áp dụng" bị vô hiệu hóa khi không có dòng "tạo mới" nào, để tránh thao tác vô nghĩa.
18. Là nhân viên vận hành, khi apply tôi muốn thao tác trả về ngay và lô chuyển sang "Đang áp dụng", để không phải chờ một request đồng bộ kéo dài với lô lớn.
19. Là nhân viên vận hành, trong lúc lô "Đang áp dụng" / "Đang hoàn tác" tôi muốn UI tự động cập nhật tiến độ (poll mỗi vài giây) cho tới khi xong, để biết khi nào hoàn tất mà không cần tải lại trang thủ công.
20. Là nhân viên vận hành, sau khi áp dụng xong tôi muốn thấy thông báo và trạng thái lô chuyển "Đã áp dụng", để xác nhận kết quả.
21. Là nhân viên vận hành, tôi muốn các bonus mới tạo từ import xuất hiện trong danh sách `/bonus` với status `pending`, để chúng đi tiếp đúng quy trình duyệt thưởng hiện hữu.
22. Là nhân viên vận hành, tôi muốn khi áp dụng mà một số dòng lỗi (ví dụ ngày hết hạn không parse được, hoặc insert lỗi), các dòng còn lại vẫn được tạo, để không mất cả lô vì một vài dòng hỏng.
23. Là nhân viên vận hành, tôi muốn bấm "Hủy preview" (có xác nhận) để bỏ một lô đang xem trước mà chưa áp dụng, để dọn dẹp các lô nhập nhầm.
24. Là nhân viên vận hành, sau khi hủy preview tôi muốn lô đó chuyển trạng thái "Đã hủy" và không tạo bonus nào, để dữ liệu sạch.
25. Là nhân viên vận hành, tôi muốn vào trang "Lịch sử import" từ trang `/bonus`, để xem lại tất cả các lô đã upload.
26. Là nhân viên vận hành, tôi muốn lịch sử import hiển thị: STT, tên file, trạng thái, tổng dòng, số tạo mới, số đã áp dụng, số lỗi, người tải lên, thời gian, để theo dõi và đối soát.
27. Là nhân viên vận hành, tôi muốn trạng thái lô hiển thị bằng nhãn dễ hiểu — Đang xem trước / Đang áp dụng / Đã áp dụng / Đang hoàn tác / Đã hủy / Đã hoàn tác / Thất bại, để nắm chính xác tình trạng từng lô kể cả khi đang chạy nền.
28. Là nhân viên vận hành, tôi muốn click vào một dòng trong lịch sử để mở trang chi tiết (preview) của lô đó, để xem từng dòng dù lô đã apply/hủy/hoàn tác.
29. Là nhân viên vận hành, ở trang chi tiết một lô "Đã áp dụng" tôi muốn nút "Hoàn tác" nằm ở header trang (có xác nhận giải thích hậu quả), để đảo ngược cả lô khi phát hiện sai sót.
30. Là nhân viên vận hành, sau khi hoàn tác thành công tôi muốn lô chuyển "Đã hoàn tác" và các bonus tương ứng chuyển status `rejected`, để giữ audit mà vẫn vô hiệu hóa thưởng sai.
31. Là nhân viên vận hành, tôi muốn rollback chịu được lỗi từng item: nếu một bonus đã `rejected` từ trước thì coi như hoàn tác thành công (idempotent), và mỗi item lưu `rollbackStatus`/`rollbackReason` để tra cứu.
32. Là nhân viên vận hành, nếu rollback có item thất bại tôi muốn lô KHÔNG bị đánh dấu "Đã hoàn tác" hoàn toàn (quay lại "Đã áp dụng") để tôi biết còn bonus chưa được reject và có thể thử lại.
33. Là nhân viên vận hành, tôi muốn lịch sử import có phân trang và (tùy chọn) lọc theo trạng thái, để tìm lô cần thiết trong danh sách dài.
34. Là nhân viên vận hành, tôi muốn hệ thống chặn việc tạo lô import mới khi đang có một lô chưa hoàn tất (status `preview`, `applying`, hoặc `rolling_back`) — trả lỗi 409 — để buộc xử lý dứt điểm lô cũ trước, tránh chồng chéo.
35. Là đối tác (partner staff) không phải root, tôi muốn các dòng có event không thuộc phạm vi quyền của mình bị đánh dấu "Lỗi — Không có quyền với event này", để không vô tình phát thưởng ngoài phạm vi.
36. Là đối tác (partner staff) không phải root, tôi muốn chỉ apply/cancel/rollback được các lô do **chính mình** tải lên (lô của người khác bị từ chối với lỗi không có quyền), và chỉ bị chặn tạo lô mới bởi lô pending của chính mình — để không kẹt vì lô của đồng nghiệp.
37. Là quản trị root, tôi muốn import được mọi event không bị giới hạn phạm vi partner, và thao tác được mọi lô; đồng thời bị chặn tạo lô mới khi còn bất kỳ lô nào chưa hoàn tất (kiểm tra toàn cục), để vận hành tập trung mà không chồng lô.
38. Là người vận hành, tôi muốn các dòng trống hoàn toàn trong file bị bỏ qua (không tính vào tổng dòng, không báo lỗi), để file có dòng thừa cuối bảng vẫn import sạch.
39. Là người vận hành, tôi muốn mỗi lô import lưu lại checksum (SHA256) và đường dẫn file gốc trên MinIO, để đối soát/truy vết sau này.
40. Là người vận hành, tôi muốn việc apply hai lần cùng một lô bị guard chặn nguyên tử (lần hai trả lỗi đã xử lý), để tránh nhân đôi bonus ngay cả khi double-click hoặc nhiều pod.
41. Là người vận hành, tôi muốn không thể "Hoàn tác" một lô chưa từng được áp dụng, hoặc hoàn tác lần hai một lô đã hoàn tác, với thông báo rõ, để tránh thao tác sai trạng thái.
42. Là người vận hành, nếu job nền apply/rollback gặp lỗi hạ tầng (panic, hoặc không lấy được dữ liệu) tôi muốn lô được đánh dấu "Thất bại" thay vì kẹt vĩnh viễn ở trạng thái đang chạy.
43. Là người vận hành, nếu không lấy được khóa Redis (Redis lỗi), tôi muốn lô được revert về trạng thái trước đó (`applying`→`preview`, `rolling_back`→`applied`) để có thể thử lại, tránh kẹt.
44. Là người quản lý, tôi muốn mỗi bonus tạo từ import được ghi audit log ("Đã tạo bonus từ import Excel") và cập nhật thống kê user/partner, để bonus import nhất quán với bonus tạo tay.

## Implementation Decisions

**Phạm vi & nguyên tắc nền tảng (đã chốt với developer):**
- Apply logic = **chỉ insert mới**. Preview phân đúng 2 action: `new_record` (sẽ tạo) và `invalid` (lỗi validate / không có quyền / event hoặc user không tồn tại).
- **Có rollback**: revert = set status các bonus đã tạo từ lô đó về `rejected` (giữ audit, không xóa cứng).
- Excel dùng **hex MongoDB ID** cho EventID/UserID (giống ambassador). Cột: `EventID, UserID, Amount, ExpiredAt (DD/MM/YYYY HH:MM:SS), Note (optional), Reason (required)`.
- Giới hạn `maxDataRows = 5000` (vượt → lỗi) và file 10MB. KHÔNG có `detectMissing` / scope 3-tier.

**Apply & Rollback chạy BẤT ĐỒNG BỘ (khác plan gốc đồng bộ — quyết định thực tế trên branch):**
- Endpoint apply/rollback **không xử lý trong request**: dùng atomic `FindOneAndUpdate` để khóa trạng thái (`preview`→`applying`, `applied`→`rolling_back`), rồi **spawn goroutine** và trả response NGAY (rỗng).
- Goroutine dùng **Redis mutex** (`eb-apply:<importId>` / `eb-rollback:<importId>`, TTL 30 phút) để tránh chạy đồng thời cross-pod.
- Goroutine cập nhật `processedCount` tăng dần (kể cả item fail), set `totalToProcess`, và status cuối (`applied` / `rolled_back`).
- **Recover panic** → set status `failed`. **Redis lock fail** → revert status về trạng thái trước (tránh kẹt mãi ở `applying`/`rolling_back`).
- Có **endpoint `GET /status`** trả `{status, processedCount, totalToProcess, percent}`; FE **poll mỗi 3 giây** khi còn lô `applying`/`rolling_back`, dừng poll khi xong.

**Các module sẽ xây / đã có (4 deep module):**

1. **Excel Parser (deep module, thuần)** — `ParseEventBonusExcel(path)`. Đọc `.xlsx` bằng excelize (RawCellValue giữ leading zero), bỏ header + dòng trống, validate từng dòng theo cột, trả `TotalRows`, `ValidRows` (đã normalize), `Errors` (mỗi lỗi có `Row`, `Column`, `Code`, `Message`). Không chạm DB/MinIO → test cô lập.
   - Mã lỗi: `EMPTY_EVENT_ID`, `EMPTY_USER_ID`, `INVALID_AMOUNT`, `INVALID_EXPIRED_AT`, `EMPTY_REASON`, `INVALID_FILE_FORMAT`, `FILE_TOO_LARGE`. Layout ngày: `02/01/2006 15:04:05`.

2. **Import Service (deep module)** — `EventBonusImport(staff)` trả interface 7 thao tác:
   - `CreateImport`: validate ext/size → parse → checksum SHA256 → upload MinIO → **batch-fetch** events/users (tránh N+1) → resolve + check quyền partner → tạo history (`preview`, history-first) rồi change records (`preview`).
   - `GetPreview`: trả change records của lô (KHÔNG filter theo phase — mỗi importId là 1 lô) kèm counters + status lô; filter `action`, search `q` (regex đã escape), phân trang. Trả thêm `phase`, `rollbackStatus`, `rollbackReason` mỗi item.
   - `GetImports`: danh sách history, filter status + phân trang, resolve tên người tải.
   - `ApplyImport`: atomic lock `preview`→`applying` + ownership guard → spawn `processApplyAsync` → trả ngay.
   - `CancelImport`: đồng bộ, chỉ khi `preview` + ownership guard → history `cancelled`, change `cancelled`.
   - `RollbackImport`: atomic lock `applied`→`rolling_back` + ownership guard → spawn `processRollbackAsync` → trả ngay.
   - `GetImportStatus`: trả tiến độ cho FE poll.
   - Side-effect khi tạo bonus: `UpdateStatistic(user, partner)` + ghi audit ("Đã tạo bonus từ import Excel").
   - Rollback dùng `EventBonus(staff).UpdateStatus(bonusID, rejected)`, **idempotent** (bonus đã rejected = success); nếu có item fail → status quay về `applied`.
   - Error vars: `PENDING_IMPORT_EXISTS` (409), `IMPORT_NOT_FOUND` (404), `IMPORT_ALREADY_PROCESSED` (409), `IMPORT_NOT_APPLIED` (400), `IMPORT_ALREADY_ROLLED_BACK` (409), `NO_PERMISSION`.

3. **Backend Handler + Route** — bind context (staff, file payload, query), gọi service, map error → HTTP. Route trong group `/event-bonus`, đặt route tĩnh `/import`, `/imports` **trước** route động `/:id`.

4. **Frontend admin (UMI v3 + DVA + AntD v4)** — modal upload, trang preview (chi tiết lô, có nút rollback ở header khi lô `applied`, poll status khi đang chạy), trang lịch sử (click row mở chi tiết, **không có cột action**, poll khi có lô đang chạy), 2 DVA model. Nút "Import Excel" + "Lịch sử import" trên `/bonus`, 2 route ẩn menu.

**State machine của một lô import:**
```
preview ──apply (lock)──▶ applying ──(job xong)──▶ applied ──rollback (lock)──▶ rolling_back ──(job xong, mọi item OK)──▶ rolled_back
   │                          │                                                      │
   │                          └─(panic/lỗi)─▶ failed                                 └─(panic/lỗi)─▶ failed
   │                          └─(Redis lock fail)─▶ preview                          └─(Redis lock fail / có item fail)─▶ applied
   └──cancel──▶ cancelled
```
- Chỉ `preview` mới apply/cancel. Chỉ `applied` mới rollback. Lock nguyên tử chặn double-apply / double-rollback.
- Bonus do apply tạo ở `pending`; rollback đưa về `rejected`.

**Schema (collection riêng):**
- `event-bonus-imports` (history): importId, fileName, fileChecksum, filePath, uploadedBy, timestamp, totalRecords, newRecordCount, invalidCount, appliedCount, **processedCount**, **totalToProcess**, status (`preview|applying|applied|rolling_back|cancelled|rolled_back|failed`), createdAt, updatedAt.
- `event-bonus-import-changes`: importId, rowNum, raw (eventId/userId/amount/expiredAt/note/reason), eventName, userName, partner, action (`new_record|invalid`), reasonInvalid, bonusId, **rollbackStatus** (`success|failed`), **rollbackReason**, phase (`preview|applied|cancelled|rolled_back`), timestamp.

**API contracts (group `/event-bonus`, yêu cầu đăng nhập):**
- `POST /event-bonus/import` (multipart) → tạo lô + preview.
- `GET /event-bonus/imports/:importId/preview?action=&q=&page=&pageSize=` → `{status, counters, list[], pagination}`.
- `GET /event-bonus/imports?status=&page=&pageSize=` → `{list[], pagination}`.
- `POST /event-bonus/imports/:importId/apply` → trả ngay (rỗng); job chạy nền.
- `GET /event-bonus/imports/:importId/status` → `{importId, status, processedCount, totalToProcess, percent}`.
- `POST /event-bonus/imports/:importId/cancel` → `{importId, status:"cancelled"}`.
- `POST /event-bonus/imports/:importId/rollback` → trả ngay (rỗng); job chạy nền.
- pageSize tối đa 100.

**Tái dùng hạ tầng:** event-bonus CRUD + `EventBonus(staff).UpdateStatus`, `EventBonusRaw`, pattern preview/history của employee-registry, `pages/bonus`, `echoupload.UploadSingle()`, `minioclient.PutObject`, `redisclient.NewMutexWithExpiration`, `internalservice.Audit()` + `User().UpdateStatistic`, `util.GetAppIDFromHex`, `modelmg.NewAppID().Hex()` (làm importId).

## Testing Decisions

**Nguyên tắc test tốt:** chỉ test hành vi đối ngoại của module, không test chi tiết triển khai. Với parser: cho file `.xlsx` đầu vào → khẳng định kết quả phân loại (tổng dòng / số hợp lệ / số & loại lỗi) đúng.

**Module có test tự động (đã chốt với developer): chỉ Excel Parser.**
- Đã có `event_bonus_import_parser_test.go` (TDD) với helper `makeXLSX`. Ca: dòng hợp lệ; 5 ca dòng lỗi (thiếu EventID/UserID, Amount sai, date sai, thiếu Reason → đếm đủ 5 lỗi, 0 hợp lệ); dòng trống bị bỏ qua.
- Deep module thuần, không cần DB/MinIO → test nhanh, ổn định.

**Các module còn lại (Import Service async, Handler/Route, Frontend): KHÔNG test tự động** — verify bằng E2E thủ công: upload → preview → apply (lô `applying` → poll → `applied`, bonus `pending`) → rollback (lô `rolling_back` → poll → `rolled_back`, bonus `rejected`) → cancel (`cancelled`, không tạo bonus) → chặn lô mới khi còn lô chưa hoàn tất (409) → ownership (non-root không thao tác được lô người khác).

**Prior art:** test parser theo style test service trong `backend/pkg/admin/service/` (Go testing + fixture excelize). Pattern preview/apply/rollback của `employee-registry` là tham chiếu hành vi khi test thủ công.

## Out of Scope

- Logic match/update bản ghi đã tồn tại, `detectMissing`, scope 3-tier như employee-registry — chỉ insert mới.
- Dùng chung collection `import-histories` với employee-registry — tách collection riêng.
- Chỉnh sửa từng dòng trực tiếp trong trang preview (sửa lỗi phải sửa file rồi upload lại).
- Tải file mẫu (template) từ UI — modal chỉ mô tả định dạng cột bằng chữ.
- Hỗ trợ định dạng ngoài `.xlsx`.
- Thông báo email/push khi job nền hoàn tất (hiện chỉ poll trên UI khi đang mở trang).
- Resume/retry tự động một lô `failed` (admin phải xử lý thủ công).
- Phụ thuộc thư viện uuid (dùng `NewAppID().Hex()`).

## Further Notes

- **Lệch với plan gốc:** plan `2026-06-04-event-bonus-import.md` đặc tả apply/rollback **đồng bộ, không polling**. Code thực tế đã chuyển sang **async goroutine + Redis mutex + poll status** với các trạng thái mới `applying`/`rolling_back`/`failed`, ownership guard, idempotent rollback, batch-fetch event/user, và side-effect audit/statistic. PRD này phản ánh code thực tế.
- **Phụ thuộc dữ liệu:** EventID/UserID trong file phải là hex MongoDB ID có thật; partner derive từ event để check quyền.
- **Rủi ro cần lưu ý khi review:**
  - Notification job nền hoàn tất chỉ thấy khi đang mở trang lịch sử/preview (poll). Đóng tab giữa chừng sẽ không có thông báo — chỉ thấy trạng thái khi quay lại.
  - Trùng `minioKey` nếu hai lô upload cùng tên file (key = `event-bonus-imports/<filename>`) — file sau ghi đè file trước; cân nhắc thêm importId vào key.
  - Rollback có item fail giữ lô ở `applied` — cần đảm bảo admin retry được đến khi sạch.
- Plan kỹ thuật chi tiết: `docs/superpowers/plans/2026-06-04-event-bonus-import.md`.
