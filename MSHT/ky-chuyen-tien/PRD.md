# PRD: Kỳ đi tiền (Transfer Period) — tách tạo lệnh rút và đi tiền, admin điều khiển

> **Trạng thái:** `ready-for-agent`
> **Phạm vi repo:** `CB-MBBank/withdraw` (chính), `CB-MBBank/user`, submodule `external` (dùng chung giữa hai service).
> **Nhánh:** tạo nhánh mới từ `release` ở cả hai repo. Code TransferPeriod cũ trên `withdraw/develop` và `user/feature/update-transfer` chỉ dùng để tham khảo, **không merge**.
> **Spec thiết kế đi kèm:** `CB-MBBank/docs/superpowers/specs/2026-09-28-transfer-period-execution-design.md` (có tham chiếu code của luồng hiện tại).

---

## 1. Bối cảnh và vấn đề (Problem Statement)

### 1.1 Luồng hiện tại

1. Service `user` có cron **auto withdraw** chạy ở một giờ cố định. Cron quét bảng user đủ điều kiện:
   - không bị ban;
   - có tài khoản nhận (`rasiAccountNumber`);
   - số dư ≥ ngưỡng rút tối thiểu hiệu lực (env hoặc ICB event);
   - không thuộc danh sách source bị skip.
   Giới hạn tổng số user mỗi lần chạy theo `LIMIT_WITHDRAW`.
2. Với mỗi user, `user` gửi NATS `withdrawal:create` (mode `auto`) sang service `withdraw`.
3. Service `withdraw` làm **mọi việc trong một lần xử lý**:
   - kiểm tra điều kiện;
   - tạo lệnh rút status `pending`;
   - trừ số dư, bằng cách tính lại `currentCash` từ tổng các lệnh rút theo status;
   - **gọi bank/AT chuyển tiền ngay**;
   - cập nhật `success`, `rejected`, hoặc giữ `pending` để cron sync tra lại sau.
4. Toggle auto hiện chỉ có env `IS_AUTO_WITHDRAW`. Muốn tắt thì phải sửa env rồi restart.

### 1.2 Vấn đề vận hành

- **Không có điểm dừng giữa "tạo lệnh" và "chi tiền".**
  - Admin không biết trước hôm nay sẽ chi bao nhiêu lệnh, tổng bao nhiêu tiền.
  - Không loại được lệnh đáng ngờ trước khi tiền rời tài khoản.
- **Không chọn được thời điểm chi tiền.**
  - Không thể chuyển riêng một ngày sang chế độ "admin bấm mới chi", ví dụ khi AT có sự cố hoặc khi cần đối soát.
- **Không có khái niệm "đợt chi".**
  - Không thống kê được theo ngày: bao nhiêu lệnh pending, success, rejected, tổng tiền mỗi loại.
- **Không có công cụ điều tra lệnh treo.**
  - Admin không xem được AT đã thực sự nhận request gì và trả response gì cho một lệnh.
- **Không dừng được khi AT sự cố giữa đợt chi.**
  - Toàn bộ lệnh còn lại vẫn bị đẩy đi và treo ở `pending`.
- **Phải dùng được cho mọi partner.**
  - MBBank chạy auto withdraw.
  - Các bank khác (BIDV, LPBank, NamABank, PVCombank, SeaBank, TPBank, VPBank, VietinBank, OneAT) để user tự bấm rút trên webview và chuyển ngay, nhưng vẫn cần gom theo ngày để tra cứu và thống kê.

---

## 2. Giải pháp (Solution)

Mỗi ngày có **đúng một kỳ chuyển tiền** (transfer period). Luồng rút được tách làm hai bước độc lập.

### 2.1 Bước 1 — Gom lệnh (collect)

- Chạy bằng cron ở service `user`. Giờ chạy lấy từ env; mỗi partner tự cân đối để chạy **sau** job thả tiền của partner đó.
- Luôn tạo kỳ của ngày (nếu đã có thì dùng lại).
- **Partner bật auto** (`IS_AUTO_WITHDRAW=true`):
  - Quét user như logic hiện tại.
  - Tạo lệnh rút gắn kỳ với status **`waiting_process`** (chờ xử lý).
  - **Trừ số dư ngay** như cũ, nhưng **chưa chuyển tiền**.
- **Partner không bật auto** (`IS_AUTO_WITHDRAW=false`):
  - Chỉ tạo kỳ rỗng.
- Cuối bước này, kỳ được đánh dấu "sẵn sàng đi tiền".

### 2.2 Bước 2 — Đi tiền (execute)

- Lấy tất cả lệnh `waiting_process` của kỳ và chạy luồng chuyển tiền hiện có.
- Có hai cách kích hoạt:
  - **Tự động:** cron ở service `withdraw` (giờ lấy từ env), chỉ xử lý các kỳ có `mode = auto`.
  - **Thủ công:** admin bấm nút "đi tiền" cho một kỳ bất kỳ (auto hay manual đều được).
- `mode` mặc định của kỳ lấy từ env. Admin đổi được mode cho từng kỳ trước khi đi tiền.
- An toàn:
  - không chạy trùng;
  - dừng được giữa chừng;
  - tự dừng khi AT lỗi liên tiếp;
  - kiểm tra lại user ngay trước khi chuyển.

### 2.3 Lệnh do user tự bấm rút

- Chuyển tiền **ngay như cũ**, không chờ kỳ.
- Được gắn `transferPeriodId` của kỳ hôm nay để tra cứu và thống kê. Nếu hôm nay chưa có kỳ thì tạo mới.

### 2.4 Công cụ cho admin (service `withdraw`, khu vực `admin` mới)

- Danh sách kỳ và chi tiết kỳ, kèm **stats** (số lệnh và tổng tiền theo từng status).
- Đổi mode kỳ, bấm đi tiền, dừng đi tiền.
- Danh sách lệnh rút của kỳ.
- Xem **log request/response với AT** của một lệnh, tra theo id lệnh.
- **Reject** lệnh đang `waiting_process` hoặc `pending` (có hoàn tiền). Chỉ được chuyển sang `rejected`.

### 2.5 Tương thích FE

App webview và CRM **không phải sửa**. Status `waiting_process` được trả về thành `pending`, và khi lọc `pending` thì kết quả bao gồm cả `waiting_process`.

---

## 3. User Stories

### 3.1 Tạo kỳ và gom lệnh

1. Là **vận hành**, tôi muốn hệ thống tự tạo một kỳ chuyển tiền mỗi ngày, để mọi lệnh rút trong ngày được gom vào một đợt có định danh rõ ràng.
2. Là **vận hành**, tôi muốn mỗi ngày (theo giờ HCM) chỉ có đúng một kỳ, để việc chạy job nhiều lần hay chạy trên nhiều pod không sinh kỳ trùng.
3. Là **vận hành**, tôi muốn giờ chạy job gom lệnh cấu hình được bằng env cho từng partner, để job chạy sau job thả tiền và user nhận được phần tiền vừa thả ngay trong kỳ hôm đó.
4. Là **vận hành của partner bật auto withdraw**, tôi muốn job gom lệnh quét user đủ điều kiện và tạo lệnh `waiting_process` gắn kỳ hôm nay, để chưa có đồng nào rời tài khoản trước bước đi tiền.
5. Là **vận hành**, tôi muốn số dư user bị trừ ngay khi lệnh `waiting_process` được tạo, để lần quét sau hoặc lệnh user tự rút không chi trùng số tiền đó.
6. Là **vận hành của partner không bật auto**, tôi muốn job vẫn tạo kỳ rỗng cho ngày, để lệnh user tự rút có kỳ để gắn vào.
7. Là **vận hành**, tôi muốn scanner giữ nguyên toàn bộ điều kiện hiện có (không bị ban, có tài khoản nhận, ngưỡng rút tối thiểu gồm cả ICB event, danh sách source bị skip, giới hạn số user mỗi ngày, nhịp giãn cách), để việc thiết kế lại không làm thay đổi ai được chi tiền.
8. Là **vận hành**, tôi muốn job đánh dấu kỳ "sẵn sàng đi tiền" khi quét xong, để không bao giờ đi tiền trên một kỳ mới gom được một nửa.
9. Là **vận hành**, tôi muốn kỳ bị kẹt ở trạng thái "đang gom" (pod scanner chết) tự được coi là sẵn sàng sau một khoảng thời gian chờ, để một lần crash không chặn việc chi tiền mãi mãi.
10. Là **vận hành**, tôi muốn gọi tạo kỳ nhiều lần trong ngày luôn trả về cùng một kỳ, để job chạy lại không gây lỗi.

### 3.2 Lệnh user tự rút (partner không bật auto)

11. Là **người dùng cuối** của partner không bật auto, tôi muốn lệnh rút được chuyển tiền ngay như hiện tại, để trải nghiệm của tôi không thay đổi.
12. Là **vận hành**, tôi muốn lệnh user tự rút được gắn vào kỳ hôm nay, và kỳ được tạo luôn nếu chưa có, để báo cáo theo ngày bao phủ mọi lệnh rút.
13. Là **vận hành**, tôi muốn lệnh user tự rút không làm thay đổi trạng thái kỳ, để trạng thái kỳ chỉ phản ánh tiến trình đi tiền của các lệnh chờ.
14. Là **vận hành**, tôi muốn công cụ sandbox "trigger auto withdraw theo danh sách user" vẫn chuyển tiền ngay và tự gắn kỳ hôm nay, để công cụ vận hành hiện có vẫn dùng được.
15. Là **vận hành**, tôi muốn luồng batch-transfer bằng file xlsx giữ nguyên hành vi, chỉ tự gắn kỳ hôm nay.

### 3.3 Chế độ kỳ (auto/manual)

16. Là **admin**, tôi muốn mỗi kỳ có `mode` là `auto` hoặc `manual`, mặc định lấy từ env, để mỗi partner chọn hành vi mặc định của mình.
17. Là **admin**, tôi muốn đổi mode của một kỳ khi kỳ chưa đi tiền, để giữ lại một ngày cụ thể cho việc kiểm tra thủ công, hoặc ngược lại cho chạy tự động.
18. Là **admin**, tôi muốn bị báo lỗi rõ ràng khi đổi mode một kỳ đã/đang đi tiền, để tránh hiểu nhầm là thay đổi có tác dụng.

### 3.4 Đi tiền

19. Là **vận hành**, tôi muốn cron đi tiền (giờ lấy từ env) tự xử lý mọi kỳ `auto` đang sẵn sàng, theo thứ tự ngày cũ trước, để các kỳ bị sót cũng được chi.
20. Là **admin**, tôi muốn bấm nút "đi tiền" cho bất kỳ kỳ nào (auto hoặc manual), để chi tiền theo nhu cầu mà không phải chờ cron.
21. Là **admin**, tôi muốn API đi tiền trả về ngay và chạy nền, để giao diện không bị treo trong lúc chi một đợt dài.
22. Là **admin**, tôi muốn bị báo lỗi ngay nếu kỳ không ở trạng thái được phép đi tiền hoặc đang có tiến trình khác đi tiền, để biết thao tác không được thực hiện.
23. Là **vận hành**, tôi muốn một kỳ không bao giờ bị đi tiền song song, để bấm hai lần hay nhiều pod cùng chạy không chi trùng.
24. Là **vận hành**, tôi muốn mỗi lệnh được "giành quyền" nguyên tử (`waiting_process` → `pending`) ngay trước khi chuyển, để một lệnh vừa bị admin reject cùng lúc không bao giờ được chi.
25. Là **vận hành**, tôi muốn có khoảng nghỉ giữa các lần gọi bank, để không spam API của partner/bank.
26. Là **vận hành**, tôi muốn hệ thống kiểm tra lại user ngay trước khi chuyển (bị ban, hoặc số dư âm do clawback), và bỏ qua những lệnh này (giữ nguyên `waiting_process`), để không chi cho user đã không còn đủ điều kiện sau lúc gom.
27. Là **admin**, tôi muốn các lệnh bị bỏ qua vẫn nằm ở `waiting_process` và nhìn thấy được, để tôi quyết định reject hoặc đi tiền lại sau.
28. Là **admin**, tôi muốn đi tiền lại một kỳ đã xong hoặc đã dừng, để xử lý nốt các lệnh còn chờ.
29. Là **vận hành**, tôi muốn tiến trình đi tiền tiếp tục được an toàn nếu pod đang chạy bị chết, để crash chỉ làm kỳ bị chặn vài phút chứ không phải vài giờ.
30. Là **vận hành**, tôi muốn lỗi ở một lệnh không làm dừng cả đợt (trừ khi chạm ngưỡng circuit breaker), để một lệnh hỏng không chặn các lệnh khác.

### 3.5 Dừng và circuit breaker

31. Là **admin**, tôi muốn có nút "dừng" cho kỳ đang đi tiền, để dừng chi ngay khi thấy bất thường.
32. Là **vận hành**, tôi muốn hệ thống tự dừng đi tiền sau N lần gọi chuyển khoản lỗi liên tiếp (N lấy từ env) và bắn cảnh báo lỗi, để sự cố AT/bank không đẩy cả đợt vào trạng thái treo.
33. Là **vận hành**, tôi muốn các trạng thái "bank đang xử lý" (bất đồng bộ) **không** bị tính là lỗi cho circuit breaker, để hành vi bình thường của bank không làm dừng đợt chi.
34. Là **vận hành**, tôi muốn kỳ đã bị dừng không bị cron tự chạy lại, để việc dừng (thủ công hay tự động) luôn cần người quyết định trước khi chi tiếp.
35. Là **admin**, tôi muốn thấy lý do dừng (admin hay circuit breaker), để biết cần xử lý gì trước khi chạy lại.

### 3.6 Tra cứu kỳ và stats

36. Là **admin**, tôi muốn xem danh sách kỳ, lọc theo khoảng ngày, status, mode, có phân trang, để tìm một ngày chi cụ thể.
37. Là **admin**, tôi muốn mỗi kỳ hiển thị stats (số lệnh và tổng tiền theo từng status: chờ xử lý, pending, success, rejected, và tổng), để biết chính xác đã chi và sắp chi bao nhiêu.
38. Là **admin**, tôi muốn stats luôn khớp với trạng thái thật của lệnh, kể cả các thay đổi từ webhook, cron sync, CRM và admin, để số liệu không bao giờ bị lệch.
39. Là **admin**, tôi muốn xem chi tiết một kỳ kèm stats, để kiểm tra trước khi bấm đi tiền.
40. Là **admin**, tôi muốn xem ai và khi nào đã đi tiền kỳ đó (cron hay admin nào), thời điểm bắt đầu và kết thúc, để có dấu vết kiểm toán.

### 3.7 Tra cứu lệnh và log AT

41. Là **admin**, tôi muốn xem danh sách lệnh rút của một kỳ, lọc theo status và user, với status **thô** (có `waiting_process`), để phân biệt "chưa gửi bank" với "đã gửi, chờ bank chốt".
42. Là **admin**, tôi muốn xem chính xác request và response đã trao đổi với AT cho một lệnh, tra theo id lệnh, để điều tra lệnh treo hoặc lệnh bị khiếu nại.
43. Là **admin**, tôi muốn log AT có sẵn các trường chính đã được parse (mã kết quả, trạng thái chuyển, mã tham chiếu bank), để không phải đọc JSON thô.
44. Là **admin**, tôi muốn nhận thông báo rõ ràng "chưa có log giao dịch" khi lệnh chưa được gửi qua communication, để hiểu vì sao không có dữ liệu.

### 3.8 Reject lệnh

45. Là **admin**, tôi muốn reject một lệnh đang `waiting_process` hoặc `pending`, để huỷ các lệnh đáng ngờ hoặc lỗi.
46. Là **admin**, tôi muốn reject xong thì user được hoàn tiền và nhận thông báo như khi reject trên CRM, để user được đối xử nhất quán.
47. Là **admin**, tôi muốn reject bị từ chối với lỗi xung đột nếu lệnh vừa đổi trạng thái cùng lúc (đã được giành để chuyển, hoặc bank đã chốt), để không bao giờ hoàn tiền cho lệnh đang hoặc đã được chi.
48. Là **admin**, tôi muốn API đổi status chỉ chấp nhận `rejected`, để không ai có thể đánh dấu thành công một lệnh chưa chi.
49. Là **admin**, tôi muốn tất cả API admin dùng cùng cơ chế xác thực admin như các admin service khác, để việc kiểm soát truy cập nhất quán.

### 3.9 Tương thích FE và hệ thống hiện có

50. Là **người dùng cuối**, tôi muốn lệnh đang chờ hiển thị là "pending" trên app, để app không lỗi vì status lạ.
51. Là **nhân viên CRM**, tôi muốn lệnh đang chờ hiển thị là "pending" trên CRM, và khi lọc "pending" thì thấy cả những lệnh này, để CRM tiếp tục hoạt động không cần sửa.
52. Là **nhân viên CRM**, tôi muốn reject được lệnh đang chờ (từng lệnh hoặc hàng loạt) với hoàn tiền, và bị chặn nếu đánh dấu thành công, để thao tác CRM an toàn.
53. Là **vận hành**, tôi muốn cron sync lệnh `pending` phân trang bằng cursor, để lượng lệnh `pending` tăng đột biến sau mỗi đợt đi tiền được sync đủ, không bỏ sót.
54. Là **vận hành**, tôi muốn gRPC balance-flow (các service khác dùng) tính cả lệnh đang chờ, để lịch sử số dư nhất quán.
55. Là **vận hành**, tôi muốn webhook AT và cron sync giữ hành vi chỉ nhận lệnh `pending`, để không có lệnh chưa gửi bank nào bị đổi trạng thái nhầm.

### 3.10 Triển khai và port partner

56. Là **dev port sang partner khác**, tôi muốn phần kỳ, đi tiền, luật status và API admin không phụ thuộc bank, với hàm chuyển khoản là điểm cắm duy nhất, để việc port chủ yếu là copy rồi chỉnh một hàm.
57. Là **vận hành**, tôi muốn deploy `withdraw` trước `user` mà payload NATS vẫn tương thích hoàn toàn, để quá trình rollout không bao giờ chi tiền sai thời điểm.
58. Là **vận hành**, tôi muốn log có cấu trúc kèm trace id xuyên suốt gom lệnh, tạo lệnh và đi tiền, để theo dõi được một đợt chi từ đầu đến cuối.
59. Là **vận hành**, tôi muốn dữ liệu cũ (lệnh không có kỳ) vẫn hoạt động bình thường mà không cần migrate.

---

## 4. Quyết định triển khai (Implementation Decisions)

### 4.1 Tổng quan kiến trúc

- **Service `user`** sở hữu việc **chọn user để chi**: điều kiện scanner, ngưỡng tối thiểu, danh sách source bị skip. Nó chỉ lo tạo kỳ và gửi yêu cầu tạo lệnh.
- **Service `withdraw`** sở hữu **kỳ, lệnh rút, trừ số dư, chuyển khoản, đi tiền, API admin**.
  - Logic đi tiền nằm cạnh dữ liệu lệnh rút và code chuyển khoản.
  - Lock, nhịp giãn cách gọi bank và circuit breaker tập trung ở một chỗ.
- Giao tiếp giữa hai service qua NATS (contract nằm trong submodule `external`, dùng chung).
- Các phương án đã loại:
  - `user` điều phối đi tiền (gọi NATS cho từng lệnh): thừa một điểm lỗi, và `user` không sở hữu collection lệnh rút.
  - `withdraw` tự quét user qua gRPC: trùng lặp logic scanner, dễ lệch điều kiện.

### 4.2 Các module

Module đánh dấu ★ là **module sâu**: giao diện đơn giản, bao nhiều logic, test độc lập được.

#### ★ M1. Vòng đời kỳ (Transfer Period Lifecycle) — `withdraw`

Giao diện:
- **Lấy hoặc tạo kỳ theo ngày:**
  - Upsert theo đầu ngày giờ HCM, `date` là unique.
  - Nếu gặp lỗi trùng khoá khi nhiều request cùng lúc thì đọc lại bản ghi.
  - Kỳ mới có `status = collecting` và `mode` lấy từ env.
- **Đánh dấu gom xong:** chỉ chuyển `collecting` → `waiting`. Các trạng thái khác thì bỏ qua (idempotent).
- **Đổi mode:** chỉ khi kỳ đang `collecting` hoặc `waiting`.
- **Yêu cầu dừng:** chỉ khi kỳ đang `processing`; set cờ `stopRequested`.
- **Luật "được phép đi tiền":** theo bảng dưới.

State machine của kỳ:

```
collecting ──gom xong──▶ waiting ──đi tiền──▶ processing ──hết lệnh──▶ done
                                                  │
                                    dừng tay / circuit breaker
                                                  ▼
                                               stopped ──đi tiền──▶ processing
```

| Trạng thái kỳ | Được đi tiền? | Ghi chú |
|---|---|---|
| `collecting` | Chỉ khi đã tạo quá **2 giờ** | Scanner coi như đã chết (2h = TTL lock scanner) |
| `waiting` | Có | Trường hợp bình thường |
| `processing` | Có | Tiếp tục sau khi pod chết. Lock bảo đảm không có tiến trình khác đang chạy |
| `stopped` | Có (chỉ admin) | Cron **không** tự chạy lại |
| `done` | Có (chỉ admin) | Xử lý nốt lệnh bị bỏ qua ở lần trước |

Cron tự động chỉ lấy các kỳ `mode = auto` ở trạng thái `waiting`, `processing`, hoặc `collecting` đã quá hạn.

#### ★ M2. Bộ đi tiền (Transfer Period Executor) — `withdraw`

Giao diện: `đi tiền(kỳ, người thực hiện) → kết quả {processed, skipped, failed}`.

Phụ thuộc được **inject** để test bằng fake:
- hàm "chuyển khoản một lệnh" (điểm cắm riêng từng bank);
- hàm "kiểm tra user đủ điều kiện" (gRPC user);
- đồng hồ và hàm sleep.

Hành vi chi tiết:

1. **Lock theo kỳ:** Redis SetNX key riêng theo id kỳ, **TTL 5 phút**, gia hạn sau mỗi lệnh (heartbeat), xoá khi kết thúc. Không lấy được lock thì trả lỗi "kỳ đang được đi tiền".
2. **Kiểm tra trạng thái** theo luật của M1. Hợp lệ thì set:
   - `status = processing`;
   - `stopRequested = false`, xoá `stopReason`;
   - `executedBy`, `executedAt`.
3. **Duyệt lệnh bằng cursor `_id` tăng dần:** mỗi trang 50 lệnh `{transferPeriodId = kỳ, status = waiting_process, _id > lastId}`.
   - Không dùng skip, và không luôn lấy trang đầu, vì lệnh bị bỏ qua vẫn giữ `waiting_process` và sẽ gây lặp vô hạn.
4. **Với từng lệnh:**
   1. Đọc lại kỳ. Nếu `stopRequested = true` thì thoát với lý do `admin`.
   2. **Kiểm tra lại user:** nếu bị ban hoặc `currentCash < 0` thì bỏ qua, giữ `waiting_process`, `skipped++`, log mức Warn. **Không tự reject.**
   3. **Giành quyền nguyên tử:** cập nhật có điều kiện `status = waiting_process` → `pending`. Không khớp (vừa bị reject) thì bỏ qua.
   4. Gọi hàm chuyển khoản. Sau bước này lệnh đi theo luồng cũ: `success`, `rejected`, hoặc giữ `pending` cho cron sync.
   5. **Circuit breaker:**
      - Lệnh gọi chuyển khoản **trả lỗi** (lỗi mạng, timeout, proxy, mã AT không thành công, nhánh legacy lỗi) thì `consecutiveFail++`. Thành công thì reset về 0.
      - Kết quả AT được map sang `pending` nhưng không lỗi (INIT/PENDING/PROCESSING/VERIFYING...) **không** tính là lỗi.
      - Khi `consecutiveFail ≥ TRANSFER_PERIOD_MAX_CONSECUTIVE_FAIL`: thoát với lý do `circuit_breaker` và log mức **Error** (bắn cảnh báo).
   6. Nghỉ **2 giây** (nhịp giãn cách chuyển từ scanner sang đây).
   7. Lỗi của từng lệnh log mức ErrorSilent rồi đi tiếp.
5. **Kết thúc:**
   - Thoát do dừng: `status = stopped`, `stopReason`.
   - Hết lệnh: `status = done`, `finishedAt`.
   - Log kết quả `{processed, skipped, failed}`.

Rủi ro được chấp nhận: pod chết **sau khi giành quyền nhưng trước khi gọi bank** thì lệnh kẹt `pending`. Trường hợp này xử lý như lỗi mạng hiện nay: cron sync tra lại, hoặc admin reject sau khi xem log AT.

#### ★ M3. Luật trạng thái lệnh rút (Withdraw Status Policy) — `withdraw`

- **Hiển thị status:** `waiting_process` → `pending`. Áp dụng cho API danh sách của app và CRM, **không** áp dụng cho API admin mới.
- **Mở rộng filter:** khi app/CRM lọc `pending` thì query `pending` hoặc `waiting_process`.
- **Chuyển trạng thái thủ công:**

| Trạng thái hiện tại | → `rejected` | → `success` |
|---|---|---|
| `waiting_process` | Admin, CRM (đơn và hàng loạt) | **Cấm** |
| `pending` | Admin, CRM (đơn và hàng loạt) | Chỉ CRM (như hiện tại) |
| `success`, `rejected` | Cấm | Cấm |

- **Reject nguyên tử:**
  - Cập nhật có điều kiện `status ∈ {pending, waiting_process}` → `rejected`, kèm người cập nhật và thời điểm.
  - Không khớp thì trả **xung đột**.
  - Khớp thì hoàn tiền (tính lại số dư) và gửi thông báo.
  - Một hàm dùng chung cho CRM đơn lẻ, CRM hàng loạt và API admin.

#### ★ M4. Stats kỳ (Period Stats) — `withdraw`

- Giao diện: `stats(danh sách id kỳ) → map id kỳ → stats`.
- Chạy **một** aggregation trên collection lệnh rút: lọc `transferPeriodId ∈ ids`, nhóm theo `(kỳ, status)`, đếm số lệnh và cộng tiền. Sau đó gộp trong code.
- **Tính lúc đọc, không lưu**, vì status lệnh đổi từ 5 nguồn (đi tiền, webhook, cron sync, CRM, admin). Lưu sẵn sẽ phải đồng bộ ở cả 5 chỗ và dễ lệch.
- Lệnh user tự rút gắn kỳ cũng được tính vào stats.

#### M5. Tách tạo lệnh / chuyển khoản — `withdraw`

Hàm tạo và chuyển tiền hiện tại được tách làm hai:

- **Tạo lệnh:**
  - lock theo user;
  - toàn bộ kiểm tra hiện có (ngưỡng tối thiểu, user tồn tại và không bị ban, đủ số dư, tài khoản hợp lệ);
  - tạo bản ghi transfer và lệnh rút;
  - gán kỳ: lấy từ request, nếu không có thì lấy hoặc tạo kỳ hôm nay;
  - gán status: có cờ chờ thì `waiting_process`, không thì `pending`;
  - insert, rồi trừ số dư.
- **Chuyển khoản:**
  - toàn bộ phần gọi bank hiện có (nhánh communication/AT và nhánh legacy MBBank);
  - xử lý lỗi, cập nhật status và mã tham chiếu, tính lại số dư, gửi thông báo.
  - **Giữ nguyên hành vi.** Đây là **điểm cắm riêng từng bank** khi port.
- **Hàm cũ:** gọi "tạo lệnh", và nếu status là `pending` thì gọi tiếp "chuyển khoản". Luồng user tự rút, batch-transfer và sandbox giữ nguyên hành vi.

#### M6. Tra log AT (Transfer Log lookup) — `withdraw`

- Tìm lệnh theo id, rồi đọc log HTTP ở service communication theo `clientMessageId` của lệnh, dùng đúng cặp `reqTo`/`purpose` như lúc gửi (cùng cách luồng xác minh chéo hiện tại đang tra).
- Trả về: request id, url, method, query, body, response, HTTP status code, thời điểm tạo và hoàn thành. Nếu parse được response thì kèm các trường **đã parse** (mã kết quả, trạng thái chuyển, mã tham chiếu).
- Communication vốn không trả header, nên không lộ key đối tác.

#### M7. Lớp HTTP admin — `withdraw`

- Khu vực `admin` mới (route, controller, service, model) theo khuôn khu vực admin của service `user`, mount tại `/admin/withdraw`. **Không** đặt trong khu vực CRM.
- Xác thực: thêm middleware `RequireAdmin` **giống hệt** service `user`/`brand` (kiểm tra JWT hợp lệ có user id). **Không** dùng xác thực CRM staff.
- Việc giới hạn truy cập `/admin/*` dựa vào gateway, như các admin service khác.

#### M8. Bộ gom lệnh phía user (Collector) — `user`

Entry cron mới (giờ lấy từ env) **thay thế** cron auto withdraw giờ cố định hiện tại. Chỉ chạy khi `ENABLE_WORKER`.

1. Gọi NATS tạo kỳ để lấy id kỳ.
2. Nếu `IS_AUTO_WITHDRAW = true`: chạy scanner hiện có, giữ nguyên lock, điều kiện, giới hạn và nhịp. Mỗi user gửi yêu cầu tạo lệnh kèm id kỳ và **cờ chờ xử lý**.
3. **Luôn** gọi NATS "gom xong" ở cuối, kể cả khi scanner dừng giữa chừng vì lỗi.

Công cụ sandbox "trigger theo danh sách user" giữ nguyên: không gửi cờ chờ, nên chuyển ngay.

#### M9. Sửa cron sync lệnh `pending` — `withdraw`

- Phân trang chuyển từ skip sang **cursor `_id`**. Skip bỏ sót lệnh vì lệnh đã sync rời khỏi filter giữa chừng.
- Filter vẫn chỉ `pending`.
- Webhook AT vẫn chỉ nhận `pending`. Điều này đúng, vì bước đi tiền đã chuyển lệnh sang `pending` trước khi gọi bank.

#### M10. Contract NATS — submodule `external`

Mọi field mới đều optional, nên payload cũ vẫn decode được.

| Subject | Request | Response |
|---|---|---|
| `withdrawal:transfer.period.create` (mới) | `{date}` | `{id}` |
| `withdrawal:transfer.period.collect.done` (mới) | `{id}` | `{ok}` |
| `withdrawal:create` (có sẵn) | thêm `transferPeriodId` (string), `waitingProcess` (bool, mặc định false) | không đổi `{accepted}` |

Handler được đăng ký ở `withdraw` khi `ENABLE_WORKER`, cùng chỗ với handler tạo lệnh.

### 4.3 Thay đổi schema

**Collection mới `transfer-periods`:**

| Field | Kiểu | Ghi chú |
|---|---|---|
| `_id` | ObjectID | |
| `date` | datetime | Đầu ngày giờ HCM, **unique** |
| `mode` | string | `auto` \| `manual` |
| `status` | string | `collecting` \| `waiting` \| `processing` \| `stopped` \| `done` |
| `stopRequested` | bool | |
| `stopReason` | string | `admin` \| `circuit_breaker`, có thể rỗng |
| `executedBy` | string | `cronjob` hoặc id admin của lần đi tiền gần nhất |
| `executedAt` | datetime | có thể rỗng |
| `finishedAt` | datetime | có thể rỗng |
| `createdAt`, `updatedAt` | datetime | |

Index: `date` (unique), `status`, `-createdAt`.

**Collection `withdraw`:**
- Thêm field `transferPeriodId` (ObjectID, có thể rỗng).
- Thêm giá trị status `waiting_process`. Hằng số đặt trong submodule dùng chung.
- Thêm index `{transferPeriodId: 1, status: 1}`.

State machine của lệnh rút:

```
waiting_process ──giành quyền khi đi tiền──▶ pending ──▶ success | rejected | (giữ pending → cron sync)
waiting_process ──admin/CRM reject──▶ rejected (hoàn tiền)
pending         ──admin/CRM reject──▶ rejected (hoàn tiền)
pending         ──CRM success──▶ success (như hiện tại)
```

`waiting_process` **chỉ** do scanner tạo. Mọi luồng khác vào thẳng `pending`.

**Số dư user (bắt buộc):**
- `currentCash` được tính lại từ tổng lệnh rút theo status, không trừ trực tiếp.
- Hàm tổng hợp lệnh rút theo user phải **cộng `waiting_process` vào tiền pending**. Nếu thiếu, số dư không giảm và **có nguy cơ chi trùng**.
- gRPC danh sách lệnh cho balance-flow phải bao gồm `waiting_process`.

### 4.4 Contract API admin

Mọi API đều dùng `RequireAdmin`. Response theo khuôn chuẩn của service (có locale message).

| # | Method | Path | Mô tả | Mã lỗi |
|---|---|---|---|---|
| 1 | GET | `/admin/withdraw/transfer-periods` | Danh sách kỳ. Query: `page`, `limit`, `fromDate`, `toDate`, `status`, `mode`. Sort `date` giảm dần. Mỗi item kèm `stats` | |
| 2 | GET | `/admin/withdraw/transfer-periods/:id` | Chi tiết kỳ kèm `stats` | 404 không có kỳ |
| 3 | PATCH | `/admin/withdraw/transfer-periods/:id/mode` | Body `{ "mode": "auto" \| "manual" }` | 400 mode sai / kỳ không ở `collecting`/`waiting` |
| 4 | POST | `/admin/withdraw/transfer-periods/:id/execute` | Lấy lock và kiểm tra trạng thái **đồng bộ**, rồi chạy nền. Trả **202** | 400 trạng thái không hợp lệ; 409 đang có tiến trình đi tiền |
| 5 | POST | `/admin/withdraw/transfer-periods/:id/stop` | Yêu cầu dừng | 400 kỳ không `processing` |
| 6 | GET | `/admin/withdraw/withdraws` | Danh sách lệnh. Query: `transferPeriodId`, `status`, `user`, `page`, `limit`. Status **thô** | |
| 7 | GET | `/admin/withdraw/withdraws/:id/transfer-log` | Log request/response AT | 404 không có lệnh; 404 "chưa có log giao dịch"; 400 communication chưa cấu hình |
| 8 | PATCH | `/admin/withdraw/withdraws/:id/status` | Body `{ "status": "rejected" }` | 400 status khác `rejected`; 400 lệnh không ở `pending`/`waiting_process`; 409 lệnh vừa đổi trạng thái |

**Dạng dữ liệu một kỳ trong response:**

```json
{
  "_id": "…",
  "date": "2026-09-28T00:00:00+07:00",
  "mode": "auto",
  "status": "waiting",
  "stopReason": "",
  "executedBy": "",
  "executedAt": null,
  "finishedAt": null,
  "createdAt": "…",
  "updatedAt": "…",
  "stats": {
    "total": 0, "totalCash": 0,
    "waitingProcess": 0, "waitingProcessCash": 0,
    "pending": 0, "pendingCash": 0,
    "success": 0, "successCash": 0,
    "rejected": 0, "rejectedCash": 0
  }
}
```

**Dạng dữ liệu log AT:**

```json
{
  "requestId": "…",
  "url": "…",
  "method": "POST",
  "query": {},
  "body": "…",
  "response": "…",
  "statusCode": 200,
  "createdAt": "…",
  "completedAt": "…",
  "parsed": { "code": "…", "transferStatus": "…", "refTxnId": "…" }
}
```

### 4.5 Thay đổi các API và luồng hiện có

| Chỗ | Thay đổi |
|---|---|
| API danh sách lệnh của app | Status `waiting_process` hiển thị `pending`; filter `pending` được mở rộng |
| API danh sách lệnh của CRM | Như trên |
| CRM đổi status một lệnh | Cho phép khi lệnh `pending` hoặc `waiting_process`; `waiting_process` chỉ được sang `rejected` |
| CRM reject hàng loạt | Chấp nhận lệnh `pending` hoặc `waiting_process` |
| Export CRM | Giữ nguyên (chỉ `success`) |
| Cron sync `pending` | Cursor `_id` (M9) |
| Webhook AT | Giữ nguyên |
| Tổng hợp số dư theo user | Cộng `waiting_process` vào pending (**bắt buộc**) |
| gRPC balance-flow | Bao gồm `waiting_process` |
| Tạo lệnh user tự rút / batch / sandbox | Tự gắn kỳ hôm nay; hành vi chuyển tiền không đổi |
| Cron auto withdraw giờ cố định ở `user` | Thay bằng cron gom lệnh (M8) |

### 4.6 Cấu hình (env)

Các env dùng chung do vận hành tự set trong `common.env`.

| Env | Mặc định | Service đọc | Ý nghĩa |
|---|---|---|---|
| `AUTO_WITHDRAW_COLLECT_CRON` | `0 0 4 * * *` | user | Giờ tạo kỳ và gom lệnh. Phải sau job thả tiền của partner |
| `TRANSFER_PERIOD_EXECUTE_CRON` | `0 0 10 * * *` | withdraw | Giờ tự đi tiền các kỳ `auto` |
| `TRANSFER_PERIOD_DEFAULT_MODE` | `auto` | withdraw | Mode mặc định khi tạo kỳ |
| `TRANSFER_PERIOD_MAX_CONSECUTIVE_FAIL` | `5` | withdraw | Ngưỡng circuit breaker |
| `IS_AUTO_WITHDRAW` (có sẵn) | `false` | user | Bật scanner tạo lệnh chờ |
| `LIMIT_WITHDRAW` (có sẵn) | `500` | user | Giới hạn số lệnh mỗi lần gom |

Hằng số (không phải env):
- thời gian chờ coi kỳ `collecting` là kẹt: 2 giờ;
- TTL lock đi tiền: 5 phút (có heartbeat);
- khoảng nghỉ giữa các lệnh: 2 giây;
- kích thước trang: 50.

### 4.7 Các quyết định khác

- **Tài khoản nhận** được snapshot trên lệnh lúc tạo. `rasiAccountNumber` cố định, không bao giờ đổi, nên không cần đọc lại khi đi tiền.
- **Bước đi tiền không tự reject lệnh nào.** Lệnh bị bỏ qua hoặc lỗi được để lại cho người quyết định (reject) hoặc cho cron sync (với lệnh `pending`).
- **Thứ tự deploy bắt buộc: `withdraw` trước, `user` sau.** Nếu `user` mới lên trước, `withdraw` cũ bỏ qua cờ chờ và **chuyển tiền ngay lúc gom**, sai thời điểm.
- **Dữ liệu cũ** không có `transferPeriodId`, không cần migrate.
- **Log:** mọi bước (gom, tạo, đi tiền) mang trace id. Lỗi theo từng lệnh trong vòng lặp dùng mức ErrorSilent để không tạo cảnh báo hàng loạt. Circuit breaker dùng mức Error để bắn cảnh báo.

---

## 5. Quyết định về test (Testing Decisions)

### 5.1 Nguyên tắc

- Test **hành vi bên ngoài** qua giao diện public của module: trạng thái bản ghi sau khi chạy, số dư, kết quả trả về, mã HTTP. **Không** assert thứ tự gọi nội bộ.
- Chỉ dùng fake ở **biên thật**: gọi bank/AT, gRPC user, NATS, đồng hồ/sleep.
- Test cần DB gate bằng `DATABASE_URI` (không có thì skip).
- Test logic thuần **không** import package có `init()` đọc file theo đường dẫn tương đối (ví dụ package locale), vì sẽ làm vỡ `go test`.
- Tiền lệ trong codebase:
  - test DAO với Mongo gate env ở package dao của `withdraw` (test beneficiary);
  - test thuần ở package tracectx của `withdraw`;
  - test config env ở package config của `user`.

### 5.2 Kịch bản test theo module

**M1 — Vòng đời kỳ:**
- Gọi lấy/tạo kỳ song song cho cùng ngày ra đúng một kỳ; các lần gọi sau trả cùng id.
- Ngày được chuẩn hoá về đầu ngày HCM (các thời điểm 00:05 và 23:55 cùng ngày ra cùng kỳ).
- "Gom xong" chuyển `collecting` → `waiting`; gọi lần hai không đổi gì; gọi trên kỳ `processing` không đổi gì.
- Đổi mode được khi `collecting`/`waiting`, bị từ chối ở các trạng thái khác.
- Ma trận "được đi tiền" đúng bảng ở mục 4.2, gồm `collecting` < 2h (không) và > 2h (có).
- Yêu cầu dừng chỉ được khi `processing`.

**M2 — Bộ đi tiền** (fake chuyển khoản, fake kiểm tra user, Mongo thật):
- Kỳ có N lệnh chờ: cả N được chuyển, kỳ kết thúc `done`, kết quả `processed = N`.
- Gọi đi tiền lần hai trong khi lần một đang chạy thì bị lock từ chối.
- Lệnh bị reject trước khi được giành quyền thì **không** bị gọi chuyển khoản.
- User bị ban hoặc số dư âm thì bị bỏ qua, lệnh giữ `waiting_process`, `skipped` tăng.
- Có lệnh bị bỏ qua thì vòng lặp vẫn kết thúc (không lặp vô hạn).
- Bật cờ dừng giữa chừng thì dừng trước lệnh kế tiếp, kỳ `stopped` với lý do `admin`, các lệnh còn lại giữ `waiting_process`.
- N lỗi chuyển khoản liên tiếp thì kỳ `stopped` với lý do `circuit_breaker`.
- Nhiều kết quả "pending không lỗi" liên tiếp thì **không** dừng.
- Lỗi xen kẽ thành công (chưa đủ N liên tiếp) thì không dừng.
- Đi tiền lại kỳ `stopped` hoặc `done` thì xử lý nốt các lệnh còn chờ.
- Lock hết hạn (mô phỏng pod chết) thì có thể đi tiền tiếp kỳ `processing`.

**M3 — Luật trạng thái:**
- Hiển thị: `waiting_process` → `pending`; các status khác giữ nguyên.
- Filter `pending` mở rộng thành `pending` + `waiting_process`; filter khác giữ nguyên.
- Bảng chuyển trạng thái ở mục 4.2 (cho phép và cấm).
- Reject `waiting_process` hoặc `pending`: status `rejected`, số dư được hoàn **đúng một lần**.
- Reject lệnh vừa được giành quyền hoặc đã `success` thì trả xung đột, không hoàn tiền.
- Hai lần reject song song trên cùng lệnh: chỉ một lần thành công, chỉ hoàn tiền một lần.

**M4 — Stats và tổng hợp số dư:**
- Nhiều kỳ với lệnh ở đủ loại status: stats từng kỳ đúng số lượng và tổng tiền, chỉ tốn một lần gọi.
- Kỳ không có lệnh: stats toàn 0.
- Tổng hợp số dư theo user: lệnh `waiting_process` được tính vào tiền pending.

**M5 — Tách tạo lệnh / chuyển khoản:**
- Hồi quy: luồng user tự rút, batch và sandbox cho cùng status, cùng biến động số dư, cùng thông báo như trước khi tách (fake bank trả thành công, trả pending, trả lỗi có hoàn tiền, trả lỗi không hoàn tiền).
- Có cờ chờ: lệnh `waiting_process`, số dư đã trừ, **không** gọi chuyển khoản.
- Không có id kỳ: lệnh tự gắn kỳ hôm nay (tạo kỳ nếu chưa có).
- Có id kỳ trong request: dùng đúng kỳ đó.

**M9 — Cron sync cursor:**
- Có lệnh rời khỏi filter `pending` trong lúc chạy: mọi lệnh `pending` đều được duyệt đúng một lần.

**M8 — Collector** (fake NATS client):
- Luôn tạo kỳ và luôn gọi "gom xong".
- Chỉ gửi yêu cầu tạo lệnh (kèm id kỳ và cờ chờ) khi `IS_AUTO_WITHDRAW = true`.
- Scanner lỗi giữa chừng vẫn gọi "gom xong".
- Tạo kỳ thất bại thì không quét, log lỗi.

### 5.3 Kiểm thử thủ công trên dev

1. Bật `IS_AUTO_WITHDRAW`, trigger gom lệnh. Kiểm tra: kỳ `waiting`, lệnh `waiting_process`, số dư user đã giảm, app/CRM hiển thị `pending`.
2. Admin xem stats kỳ. Reject một lệnh. Kiểm tra user được hoàn tiền và nhận thông báo.
3. Admin bấm đi tiền. Kiểm tra lệnh chuyển `success`/`pending`, xem được log AT.
4. Dừng giữa chừng. Kiểm tra kỳ `stopped`, lệnh còn lại vẫn chờ. Bấm đi tiền lại để xử lý nốt.
5. Tắt `IS_AUTO_WITHDRAW`. User tự rút: chuyển ngay, có gắn kỳ. Kỳ rỗng vẫn qua `waiting` rồi `done`.
6. Đổi kỳ sang `manual`. Đến giờ cron đi tiền thì kỳ không bị chạy.

---

## 6. Ngoài phạm vi (Out of Scope)

- Port sang các partner khác (BIDV, LPBank, NamABank, PVCombank, SeaBank, TPBank, VPBank, VietinBank, OneAT). Mỗi partner có plan riêng, dùng lại thiết kế này.
- Giao diện admin (FE).
- Reject hàng loạt qua API admin (CRM đã có reject hàng loạt).
- Lưu stats kỳ dạng snapshot.
- Thay đổi điều kiện chọn user của scanner, hoặc logic chuyển khoản/bank.
- Tự động reject lệnh bị bỏ qua hoặc lỗi.
- Phân quyền theo role ngoài mô hình `RequireAdmin` + gateway hiện có.

---

## 7. Ghi chú thêm (Further Notes)

- **Giờ gom lệnh** phải đặt sau job thả tiền của partner. Với MBBank, service `transaction` thả tiền lúc 01:00. Chạy cùng giờ thì user nào được quét trước lúc thả tiền sẽ chỉ rút được phần tiền cũ, tức kết quả phụ thuộc thứ tự quét.
- **`RequireAdmin`** chỉ kiểm tra JWT hợp lệ, giống các admin service khác. Việc bảo vệ `/admin/*` dựa vào gateway.
- **Reject lệnh `pending`** có thể hoàn tiền cho khoản bank đã chuyển thật. Admin cần xem log AT trước khi reject; giao diện nên hiện cảnh báo này.
- **Lệnh đi nhánh legacy MBBank** (khi `ENABLE_COMMUNICATION=false`) không có log ở communication, nên API log AT trả "chưa có log giao dịch".
- **Rollout đề xuất:**
  1. Deploy `withdraw` (tương thích ngược, chưa có gì thay đổi hành vi vì chưa có ai gửi cờ chờ).
  2. Set env mới trong `common.env`.
  3. Deploy `user`: cron auto withdraw cũ bị thay bằng cron gom lệnh.
  4. Theo dõi kỳ đầu tiên qua API admin trước giờ cron đi tiền. Có thể chuyển kỳ đầu sang `manual` để tự bấm.
