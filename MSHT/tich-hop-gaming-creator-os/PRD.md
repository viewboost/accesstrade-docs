# PRD: Tích hợp Mini Game V2 (Portal Reward)

**Ngày**: 2026-08-25
**Trạng thái**: Draft — chờ review
**Scope**: Mở webview game của partner Portal Reward + cung cấp danh sách event code cho các service khác

---

## Problem Statement

Hệ thống event hiện chỉ hỗ trợ **một** nhà cung cấp mini game duy nhất. Toàn bộ thông tin kết nối (base URL, access key, secret key, action type) được hardcode qua một block env `MINI_GAME_`, và service chỉ biết một cách duy nhất để sinh URL SSO mở webview.

Nay có thêm partner mới — **Portal Reward** — cũng cung cấp dịch vụ gaming qua webview. Với kiến trúc hiện tại, không có cách nào để:

1. Setup một event trỏ tới partner mới mà không phá vỡ các event mini game đang chạy.
2. Mở webview của partner mới, vì luồng sinh URL SSO chỉ có một nhánh cứng.
3. Cho các service khác (đơn hàng, giao dịch...) biết được những loại sự kiện nào (`ORDER_CREATED`, `ORDER_UPDATED`, ...) cần được đẩy sang Portal Reward — thông tin này hiện không tồn tại ở bất kỳ đâu.

Kết quả: đội vận hành không thể triển khai chương trình với partner mới, và các service khác không có nguồn thông tin để biết khi nào cần gửi dữ liệu sang Portal Reward.

## Solution

Bổ sung một loại event mới `mini_game_v2` chạy **song song** với `mini_game` hiện tại, không sửa đổi hành vi của event cũ.

Về phía vận hành, admin setup event `mini_game_v2` với `gameCode` do Portal Reward cấp (giống hệt cách làm với event cũ), kèm thêm một danh sách **event code** — những loại sự kiện mà Portal Reward yêu cầu hệ thống đẩy sang.

Về phía người dùng cuối, trải nghiệm không đổi: mở app, vào chương trình, webview game hiện lên. API sinh URL SSO giữ nguyên hợp đồng hoàn toàn — vẫn chỉ nhận `gameCode`. Vì `gameCode` là duy nhất trên toàn hệ thống, hệ thống tra ra event rồi tự biết cần gọi partner nào dựa vào loại của event đó; client không cần biết partner.

Về phía các service nội bộ, có một API NATS mới để hỏi "những event code nào đang được bật?" — trả về đầy đủ ngữ cảnh (event code, gameCode, event ID) để service gọi tự quyết định có gửi dữ liệu sang Portal Reward hay không, và gửi kèm thông tin gì.

Toàn bộ phần giao tiếp với Portal Reward được đóng gói trong một module partner API riêng, tách biệt hoàn toàn khỏi code của partner cũ.

## User Stories

### Setup event (Admin)

1. Là một admin vận hành, tôi muốn tạo event với loại `mini_game_v2`, để triển khai chương trình game với partner Portal Reward.
2. Là một admin vận hành, tôi muốn nhập `gameCode` do Portal Reward cấp khi tạo event `mini_game_v2`, để hệ thống biết mở game nào của partner.
3. Là một admin vận hành, tôi muốn hệ thống báo lỗi rõ ràng khi tôi tạo event `mini_game_v2` mà bỏ trống `gameCode`, để tôi không tạo ra event không dùng được.
4. Là một admin vận hành, tôi muốn hệ thống chặn việc tạo event có `gameCode` trùng với bất kỳ event nào đang active, để không xảy ra mơ hồ khi người dùng mở game.
5. Là một admin vận hành, tôi muốn ràng buộc trùng `gameCode` áp dụng chung cho cả `mini_game` và `mini_game_v2`, để một mã game luôn xác định duy nhất một chương trình bất kể partner nào.
6. Là một admin vận hành, tôi muốn hệ thống chặn việc chuyển một event sang trạng thái active khi đã có event khác cùng `gameCode` đang active, để giữ ràng buộc duy nhất kể cả khi thay đổi trạng thái sau này.
7. Là một admin vận hành, tôi muốn khai báo danh sách event code (`ORDER_CREATED`, `ORDER_UPDATED`, ...) khi setup event `mini_game_v2`, để chỉ định những loại sự kiện nào cần được đẩy sang Portal Reward.
8. Là một admin vận hành, tôi muốn sửa danh sách event code của một event đang chạy, để điều chỉnh phạm vi dữ liệu gửi sang partner mà không phải tạo lại chương trình.
9. Là một admin vận hành, tôi muốn để trống danh sách event code, để triển khai chương trình chỉ mở webview mà không đẩy dữ liệu nào sang partner.
10. Là một admin vận hành, tôi muốn các thao tác setup event `mini_game_v2` được ghi audit log như mọi event khác, để truy vết được ai đã thay đổi cấu hình.
11. Là một admin vận hành, tôi muốn các event `mini_game` cũ tiếp tục hoạt động y hệt sau khi tính năng mới lên, để không phải làm gì với các chương trình đang chạy.

### Mở webview (Người dùng cuối)

12. Là một người dùng app, tôi muốn mở được webview game của Portal Reward từ trong chương trình, để tham gia chơi game nhận thưởng.
13. Là một người dùng app, tôi muốn phiên game được đăng nhập sẵn bằng tài khoản của mình, để không phải đăng nhập lại ở webview của partner.
14. Là một người dùng app, tôi muốn nhận được thông báo rõ ràng khi chương trình chưa bắt đầu, để biết khi nào quay lại.
15. Là một người dùng app, tôi muốn nhận được thông báo rõ ràng khi chương trình đã kết thúc, để không chờ đợi vô ích.
16. Là một người dùng app, tôi muốn không mở được webview khi chương trình không ở trạng thái active, để không rơi vào phiên game không hợp lệ.
17. Là một người dùng app đang chơi game của partner cũ, tôi muốn trải nghiệm không thay đổi gì, để không bị gián đoạn.
18. Là một client (mobile/web), tôi muốn tiếp tục gọi endpoint sinh URL cũ với duy nhất `gameCode` như trước, để không phải cập nhật gì cả cho chương trình cũ lẫn chương trình mới.
19. Là một client (mobile/web), tôi muốn mở game của partner mới bằng đúng cách đang dùng cho partner cũ, để không phải phân biệt partner ở phía client.
20. Là một client (mobile/web), tôi muốn nhận về `redirectURI` với cùng cấu trúc response như hiện tại, để dùng lại nguyên code mở webview.
21. Là một người dùng app, tôi muốn nhận thông báo lỗi thân thiện khi partner gặp sự cố không sinh được URL, để biết là lỗi hệ thống chứ không phải do mình.

### Cung cấp thông tin event code (Service nội bộ)

22. Là một service nội bộ, tôi muốn hỏi service event xem những event code nào đang được bật, để biết có cần gửi dữ liệu sang Portal Reward hay không.
23. Là một service nội bộ, tôi muốn truyền vào một danh sách event code cụ thể để lọc, để chỉ nhận về những code mình quan tâm.
24. Là một service nội bộ, tôi muốn bỏ trống danh sách lọc và nhận về toàn bộ event code đang được bật, để nạp cấu hình một lần lúc khởi động.
25. Là một service nội bộ, tôi muốn kết quả trả về chỉ gồm các event thực sự đang hiệu lực (active và trong khoảng thời gian diễn ra), để không gửi dữ liệu cho chương trình đã kết thúc hoặc chưa bắt đầu.
26. Là một service nội bộ, tôi muốn nhận kèm `gameCode` của từng event code, để đưa vào payload gửi sang Portal Reward.
27. Là một service nội bộ, tôi muốn nhận kèm ID và tên chương trình, để log và truy vết được dữ liệu thuộc chương trình nào.
28. Là một service nội bộ, tôi muốn nhận kèm thời gian bắt đầu/kết thúc của chương trình, để tự kiểm tra hiệu lực nếu có cache phía mình.
29. Là một service nội bộ, tôi muốn nhận về danh sách rỗng thay vì lỗi khi không có event nào khớp, để xử lý luồng bình thường không cần bắt exception.
30. Là một service nội bộ, tôi muốn gọi API này qua NATS như các API nội bộ khác, để dùng lại hạ tầng và client sẵn có.

### Vận hành & cấu hình

31. Là một kỹ sư vận hành, tôi muốn cấu hình kết nối Portal Reward qua biến môi trường riêng, để không đụng tới cấu hình của partner cũ.
32. Là một kỹ sư vận hành, tôi muốn `.env.example` liệt kê đầy đủ biến môi trường mới, để biết cần khai báo gì khi deploy.
33. Là một lập trình viên, tôi muốn toàn bộ code gọi Portal Reward nằm trong một module riêng, để khi partner đổi API chỉ phải sửa một chỗ.
34. Là một lập trình viên, tôi muốn module Portal Reward có interface ổn định và test độc lập, để yên tâm rằng việc điền chi tiết API sau này không ảnh hưởng phần còn lại.
35. Là một lập trình viên, tôi muốn lỗi khi gọi Portal Reward được log đủ ngữ cảnh, để chẩn đoán sự cố tích hợp nhanh chóng.

## Implementation Decisions

### Loại event mới thay vì thêm provider

Đã cân nhắc hai hướng: (a) giữ nguyên `mini_game` và thêm trường `provider` trong options, (b) thêm loại event mới. **Chốt phương án (b)**: `mini_game_v2`.

Lý do quyết định: event của Portal Reward mang thêm dữ liệu cấu hình mà event cũ hoàn toàn không có (danh sách event code). Nhồi chung vào một loại sẽ tạo ra options có trường chỉ hợp lệ với một nửa số bản ghi. Tách loại cũng làm ràng buộc trùng `gameCode` tự nhiên tách theo loại, không cần khoá phức hợp.

Hệ quả: không cần migrate dữ liệu — event cũ giữ nguyên loại `mini_game`.

### Loại event `mini_game_v2`

- Thêm hằng số loại event mới bên cạnh `mini_game`, đăng ký vào các danh sách loại event hợp lệ hiện có.
- Xác định các danh sách nào loại mới phải có mặt: danh sách loại event hợp lệ để tạo/hiển thị, và bảng ánh xạ trạng thái thưởng mặc định ban đầu. Vì phần thưởng nằm ngoài scope, trạng thái thưởng của loại mới dùng cùng giá trị khởi tạo như `mini_game`.
- Loại mới **không** tham gia vào các luồng tạo phần thưởng, thống kê, hay đối soát.

### Cấu trúc dữ liệu

Mở rộng options của event với một trường mới:

- `eventCodes`: mảng chuỗi, optional. Chứa các mã sự kiện mà Portal Reward yêu cầu đẩy sang, ví dụ `ORDER_CREATED`, `ORDER_UPDATED`.

Trường `gameCode` sẵn có được dùng lại nguyên vẹn cho loại event mới, không đổi ý nghĩa.

`eventCodes` chỉ có ý nghĩa với loại `mini_game_v2`; các loại khác bỏ qua.

### Ràng buộc phía admin

- Khi tạo event loại `mini_game_v2`, `gameCode` là bắt buộc — tái sử dụng thông điệp lỗi hiện có cho trường hợp thiếu mã game.
- **`gameCode` là duy nhất trên toàn hệ thống**, không phân biệt loại event: không cho phép tồn tại hai event có cùng `gameCode` ở trạng thái active, kể cả khi khác loại. Điều kiện kiểm tra giữ nguyên như hiện tại (`gameCode` + `status`), chỉ mở rộng phạm vi áp dụng sang loại event mới.
- Kiểm tra tương tự được áp dụng khi chuyển trạng thái event sang active, giống cách event `mini_game` đang làm.
- Hệ quả quan trọng: vì `gameCode` xác định duy nhất một event, việc định tuyến partner có thể suy ra hoàn toàn từ loại của event tra được — không cần tham số bổ sung nào từ phía client.
- `eventCodes` được nhận từ request tạo/sửa event, không validate nội dung từng phần tử (danh sách mã do partner định nghĩa và có thể thay đổi); chỉ loại bỏ phần tử rỗng và trùng lặp.

### Module partner API Portal Reward

Tạo module partner API mới, đặt cạnh các module partner hiện có, theo đúng cấu trúc đang dùng: tách riêng phần hằng số, phần model request/response, và phần client.

Interface của module — đây là ranh giới ổn định, phần thân sẽ được điền khi có tài liệu API chính thức từ partner:

- Khởi tạo client từ base URL và cặp khoá xác thực.
- Một thao tác sinh URL game: nhận vào mã game, định danh người dùng phía hệ thống, tên hiển thị người dùng, và một mã request duy nhất; trả về URL đích để mở webview, hoặc lỗi.

Quyết định thiết kế: đây là **deep module** — toàn bộ chi tiết HTTP, cách ký request, format response, mã lỗi của partner đều nằm sau interface trên. Phần còn lại của hệ thống không biết Portal Reward giao tiếp bằng giao thức gì. Khi tài liệu API về, chỉ phần thân module thay đổi; không có chỗ gọi nào phải sửa.

Tại thời điểm PRD này, thân hàm sinh URL chưa gọi API thật — trả về lỗi "chưa triển khai" một cách tường minh, và được đánh dấu rõ trong code là điểm cần hoàn thiện.

### Cấu hình

Thêm một nhóm biến môi trường riêng cho Portal Reward, tiền tố tách biệt với nhóm của partner cũ, gồm base URL và cặp khoá xác thực. Nhóm cũ giữ nguyên không đụng tới. Cập nhật file mẫu biến môi trường.

Các biến của partner mới không đặt `required` để service vẫn khởi động được ở môi trường chưa cấu hình partner này.

### API sinh URL webview

**Hợp đồng API không thay đổi gì cả**: giữ nguyên endpoint, phương thức, tham số đầu vào (`gameCode`), và cấu trúc response. Client không phải sửa một dòng nào, cho cả chương trình cũ lẫn chương trình mới.

Đã cân nhắc việc thêm query param `eventType` để client chỉ định partner. **Quyết định bỏ**: vì `gameCode` đã unique toàn cục, tham số này không mang thêm thông tin nào mà chỉ tạo thêm một đường cho dữ liệu mâu thuẫn lọt vào.

Hành vi định tuyến:

- Truy vấn event theo `gameCode` và trạng thái active — **y hệt hiện tại**.
- Mở rộng điều kiện chấp nhận về loại: trước đây chỉ chấp nhận `mini_game`, nay chấp nhận cả `mini_game_v2`.
- Rẽ nhánh dựa vào loại của chính event tra được.

Sau khi tìm được event và xác thực hiệu lực (dùng nguyên logic kiểm tra hiệu lực hiện có), rẽ nhánh theo loại event để chọn cách sinh URL:

- Loại `mini_game`: chạy nguyên khối logic hiện tại, được tách ra thành một hàm riêng. Đây là thao tác **di chuyển code, không đổi logic** — cùng cách ký, cùng payload, cùng endpoint partner.
- Loại `mini_game_v2`: gọi module Portal Reward.

Việc lấy thông tin người dùng qua gRPC dùng chung cho cả hai nhánh, thực hiện trước khi rẽ nhánh.

Response trả về giữ nguyên cấu trúc chứa `redirectURI`, kể cả bước giải mã URL ở tầng handler.

Ghi chú: chú thích swagger của endpoint này hiện khai báo sai kiểu dữ liệu trả về (khai là chi tiết event, thực tế trả về URL). Sửa luôn trong lần này vì đang đụng vào.

### API cung cấp danh sách event code

Thêm một API NATS request/reply mới, khai báo trong module hợp đồng NATS dùng chung, đăng ký handler cùng chỗ với các API request/reply hiện có.

**Request**: một trường `eventCodes` kiểu mảng chuỗi, optional.

**Hành vi truy vấn**: luôn giới hạn trong các event thoả **đồng thời**:

- loại là `mini_game_v2`
- trạng thái active
- thời điểm hiện tại nằm trong khoảng bắt đầu — kết thúc của event
- thuộc đúng partner của hệ thống

Ba điều kiện đầu tương đương định nghĩa "event đang hiệu lực" đã có sẵn trong model. Quyết định: thể hiện điều kiện này trực tiếp ở tầng truy vấn database thay vì lọc sau khi lấy về, vì đây là truy vấn danh sách chứ không phải kiểm tra một event đơn lẻ.

Nếu request có truyền `eventCodes`, lọc thêm những event có ít nhất một mã khớp, và kết quả trả về chỉ chứa các mã nằm trong danh sách yêu cầu.

**Response**: vì đây là API nội bộ, trả về đầy đủ ngữ cảnh thay vì chỉ danh sách mã. Mỗi phần tử gồm:

- danh sách event code đang bật của chương trình đó
- `gameCode` của chương trình
- định danh chương trình
- tên chương trình
- thời gian bắt đầu và kết thúc

Không có event nào khớp thì trả về danh sách rỗng, không phải lỗi.

### Những gì KHÔNG thay đổi

Ghi rõ để tránh hiểu nhầm khi triển khai:

- Luồng sinh URL của partner cũ: không đổi logic, chỉ được tách thành hàm riêng.
- Webhook nhận thưởng hiện có: không đụng tới. Vì `gameCode` unique toàn cục nên việc tra cứu bằng `gameCode` vẫn ra đúng event; tuy nhiên webhook chưa phân biệt loại event khi xử lý, đây là nợ kỹ thuật đã ghi nhận (xem Further Notes).
- Các luồng tạo thưởng, thống kê, đối soát, xuất dữ liệu: không đụng tới.
- Cấu hình của partner cũ: không đụng tới.

## Testing Decisions

### Nguyên tắc

Test chỉ kiểm chứng **hành vi quan sát được từ bên ngoài** của module: cho đầu vào này thì đầu ra là gì, gọi ra ngoài với dữ liệu gì. Không test cấu trúc nội bộ, không assert vào tên hàm private hay thứ tự các bước bên trong. Tiêu chí: refactor bên trong mà không đổi hành vi thì test phải vẫn xanh.

### Module được test

**Module partner Portal Reward** — ưu tiên cao nhất, vì đây là ranh giới với hệ thống bên ngoài và là nơi dễ sai nhất khi điền chi tiết API sau này.

Các hành vi cần phủ:

- Sinh URL thành công: partner trả về hợp lệ thì module trả đúng URL.
- Partner trả về mã lỗi HTTP: module trả lỗi, không panic.
- Partner trả về body không đúng định dạng: module trả lỗi.
- Request gửi đi đúng: đúng đường dẫn, đúng header xác thực, payload chứa đủ các trường bắt buộc.
- Mã request là duy nhất giữa các lần gọi.

Khi tài liệu API về và phần ký request được triển khai, bổ sung test kiểm chứng chữ ký sinh ra khớp với giá trị kỳ vọng từ bộ dữ liệu mẫu của partner.

**Kiểm tra trùng `gameCode` phía admin** — ưu tiên cao, vì ràng buộc này là nền tảng cho toàn bộ cơ chế định tuyến partner.

Các hành vi cần phủ:

- Tạo event `mini_game_v2` thiếu `gameCode` bị từ chối.
- Tạo hai event `mini_game_v2` cùng `gameCode` active: cái thứ hai bị từ chối.
- Tạo event `mini_game_v2` có `gameCode` trùng với một event `mini_game` đang active: **bị từ chối** — ràng buộc duy nhất áp dụng xuyên loại.
- Chiều ngược lại: tạo event `mini_game` trùng mã với `mini_game_v2` active cũng bị từ chối.
- Chuyển trạng thái sang active khi đã có event cùng mã đang active (bất kể loại): bị từ chối.

**Định tuyến API sinh URL** — mức trung bình.

- `gameCode` trỏ tới event `mini_game`: đi nhánh partner cũ.
- `gameCode` trỏ tới event `mini_game_v2`: đi nhánh Portal Reward.
- Event thuộc loại không phải hai loại trên: bị từ chối.
- Event không tồn tại hoặc hết hiệu lực: trả lỗi phù hợp.
- Hợp đồng API không đổi: request chỉ có `gameCode`, response giữ nguyên cấu trúc.

**API danh sách event code** — mức trung bình.

- Không truyền bộ lọc: trả về mọi event code của các event `mini_game_v2` đang hiệu lực.
- Có truyền bộ lọc: chỉ trả về các mã khớp.
- Event đã kết thúc, chưa bắt đầu, hoặc không active: bị loại khỏi kết quả.
- Không có event nào khớp: trả về danh sách rỗng, không lỗi.
- Response chứa đủ ngữ cảnh đã cam kết.

### Prior art

Đã có sẵn test cho các module partner API khác trong dự án theo đúng mô hình cần dùng ở đây — dựng HTTP server giả lập, cho client trỏ vào, kiểm chứng request gửi đi và response nhận về. Test module Portal Reward bám theo mô hình này.

## Out of Scope

- **Toàn bộ phần thưởng của partner mới**: nhận webhook trả thưởng, tạo bản ghi thưởng, duyệt/từ chối thưởng, đối soát. Theo thống nhất, mọi thống kê nằm phía Portal Reward; hệ thống chỉ cần mở được webview.
- **Việc thực sự đẩy dữ liệu sang Portal Reward**: service event chỉ *lưu và cung cấp* danh sách event code. Việc gửi dữ liệu do các service khác tự thực hiện sau khi hỏi API này.
- **Triển khai chi tiết giao thức gọi API Portal Reward**: chờ tài liệu chính thức từ partner. PRD này dựng khung module và ranh giới interface.
- **Cache phía service gọi**: mỗi service tự quyết định có cache kết quả hay không và cách làm mới cache.
- **Giao diện CMS**: phần hiển thị form nhập danh sách event code trên CMS do đội frontend triển khai theo hợp đồng API.
- **Thống kê, báo cáo, xuất dữ liệu** cho event loại mới.
- **Cơ chế thông báo khi cấu hình thay đổi**: các service gọi tự chịu trách nhiệm làm mới thông tin.

## Further Notes

### Điểm nợ kỹ thuật cần theo dõi

Webhook nhận thưởng hiện tra cứu event bằng `gameCode` và trạng thái active, rồi xử lý mà không phân biệt loại event. Nhờ ràng buộc `gameCode` unique toàn cục, nó vẫn tra ra đúng event — nhưng nếu một event `mini_game_v2` được tra ra, luồng xử lý thưởng của partner cũ sẽ chạy trên dữ liệu của partner mới.

Trong scope hiện tại chưa xảy ra vì partner mới chưa có luồng thưởng nào bắn vào. **Phải xử lý trước khi triển khai phần thưởng cho Portal Reward.** Được ghi nhận là nợ kỹ thuật có chủ đích, không phải thiếu sót.

### Về việc đảo chiều quyết định thiết kế

Trong quá trình thảo luận, phương án ban đầu là thêm trường `provider` vào options và giữ nguyên loại `mini_game`. Quyết định được đổi sang thêm loại mới sau khi phát sinh yêu cầu lưu danh sách event code — dữ liệu chỉ tồn tại ở partner mới. Ghi lại để người đọc sau hiểu vì sao chọn tách loại thay vì tham số hoá.

### Về hằng số action type có sẵn

Hệ thống đã khai báo một action type dành cho việc mở mini game, là hợp đồng với client và CMS. **Không cần thay đổi gì**: admin vẫn set action với cùng type và value là `gameCode` như đang làm cho event cũ. Client thấy action type đó thì gọi API sinh URL với `gameCode` — không cần biết đằng sau là partner nào. Việc phân biệt partner nằm hoàn toàn ở backend, dựa vào loại của event tra được.

Đây là hệ quả trực tiếp của quyết định giữ `gameCode` unique toàn cục: nó cho phép toàn bộ phía client — cả app lẫn CMS — không phải nhận biết sự tồn tại của partner thứ hai.

### Thứ tự triển khai gợi ý

1. Loại event mới, trường options mới, và các ràng buộc phía admin — độc lập, có thể merge trước.
2. Module partner Portal Reward với interface đầy đủ và thân hàm chờ tài liệu.
3. Định tuyến API sinh URL.
4. API NATS cung cấp danh sách event code — độc lập với ba phần trên, có thể làm song song.
5. Điền chi tiết gọi API Portal Reward khi có tài liệu.

Các bước 1, 2, 4 không phụ thuộc lẫn nhau và có thể chia cho nhiều người.
