# PRD — Trigger sự kiện mini_game_v2 sang Portal Reward

- Ngày: 2026-08-28
- Service chủ trì: `event`
- Service bị ảnh hưởng: `tracking`, `transaction` (repo từng bank), submodule `external/`
- Trạng thái: draft, chờ review

## Problem Statement

Đội vận hành dựng được event `mini_game_v2` trên CRM, khai `gameCode` của Portal Reward,
khai điều kiện trong `condMiniGame` và `condTracking`, và người dùng mở được webview game
qua kênh LAUNCH. Nhưng game bên partner **không bao giờ nhận được tin gì về hành vi của
người dùng**: không biết ai vừa đặt đơn, đơn nào hoàn tất, đơn nào bị huỷ, ai vừa click.

Nguyên nhân: kênh EVENT của Portal Reward đã được viết đầy đủ trong `external/partnerapi/portalreward`
(ký HMAC, dẫn xuất khoá theo kênh, phân loại lỗi, dedupe phía partner) nhưng **chưa có một
chỗ nào trong hệ thống gọi tới nó**. Toàn repo chỉ gọi `CreateLaunch`; `SendEvent` chưa từng
được gọi.

Hệ quả với người dùng cuối: chơi mini game xong không được cộng lượt, không lên nhiệm vụ,
không nhận thưởng — dù đơn hàng và click của họ đã được ghi nhận đầy đủ trong hệ thống.

Hệ quả với vận hành: không trả lời được câu hỏi "đơn X đã đẩy sang partner chưa", không đối
soát được với partner, không retry được khi partner lỗi.

## Solution

Dựng một job chạy nền trong service `event`, hai tiếng một lần, làm đúng một việc: lấy các
sự việc đã xảy ra trong hệ thống mà event `mini_game_v2` quan tâm, và đẩy sang Portal Reward
qua kênh EVENT.

Từ góc nhìn người dùng: đặt đơn hoặc click xong, chậm nhất hai tiếng sau thì lượt chơi /
nhiệm vụ tương ứng bên game đã được ghi nhận.

Từ góc nhìn vận hành: mọi lượt gửi đều để lại dấu vết trong một bảng `system-events` — gửi
gì, lúc nào, partner trả về gì, mã truy vết là bao nhiêu, thất bại vì lý do gì. Cái nào
partner từ chối vì lỗi tạm thời thì job tự gửi lại; cái nào sai payload thì dừng lại chờ
người xử lý chứ không đấm mãi.

## User Stories

### Người dùng cuối

1. Là người dùng tham gia mini game, tôi muốn đơn hàng vừa đặt được ghi nhận sang game, để tôi nhận được lượt chơi mà không phải thao tác gì thêm.
2. Là người dùng tham gia mini game, tôi muốn đơn hàng của tôi khi hoàn tất (cashback) được báo sang game, để tôi nhận phần thưởng gắn với đơn hoàn tất.
3. Là người dùng tham gia mini game, tôi muốn đơn hàng bị từ chối được báo sang game, để bảng thành tích của tôi phản ánh đúng thực tế và tôi không bị treo lượt ảo.
4. Là người dùng tham gia mini game, tôi muốn hành vi click của tôi trong app được ghi nhận sang game, để tôi hoàn thành được nhiệm vụ dạng "truy cập / xem".
5. Là người dùng tham gia mini game, tôi muốn chỉ những đơn thoả điều kiện của event (giá trị tối thiểu, brand, shop, loại đơn) mới được tính, để luật chơi đúng như mô tả trên CRM.
6. Là người dùng tham gia mini game, tôi muốn chỉ những đơn phát sinh trong thời gian diễn ra event mới được tính, để không bị lẫn với đơn cũ ngoài kỳ.
7. Là người dùng tham gia nhiều event mini game cùng lúc, tôi muốn một đơn hàng được tính cho mọi event mà nó thoả điều kiện, để tôi không bị mất quyền lợi ở event còn lại.
8. Là người dùng tham gia mini game, tôi muốn không bị cộng lượt trùng khi hệ thống chạy lại job, để bảng xếp hạng công bằng.
9. Là người dùng tham gia mini game, tôi muốn danh tính của tôi bên game trùng với lúc mở webview, để lượt chơi rơi đúng vào tài khoản của tôi.

### Đội vận hành / CSKH

10. Là nhân viên CSKH, tôi muốn tra được một đơn hàng đã được đẩy sang partner hay chưa, để trả lời khiếu nại "tôi mua rồi mà không được cộng lượt".
11. Là nhân viên CSKH, tôi muốn thấy lý do thất bại của một lượt gửi, để biết đây là lỗi hệ thống mình hay lỗi phía partner.
12. Là nhân viên vận hành, tôi muốn thấy mã truy vết (`deliveryId`) partner cấp cho từng lượt gửi, để làm việc với partner khi hai bên lệch số liệu.
13. Là nhân viên vận hành, tôi muốn liệt kê được toàn bộ sự kiện đã gửi trong một ngày cụ thể, để đối chiếu với job quét theo ngày bên partner.
14. Là nhân viên vận hành, tôi muốn thấy nguyên văn payload đã gửi, để chứng minh với partner rằng gói tin của mình đúng khuôn.
15. Là nhân viên vận hành, tôi muốn hệ thống tự gửi lại những gói tin thất bại do partner lỗi tạm thời, để không phải can thiệp tay.
16. Là nhân viên vận hành, tôi muốn hệ thống ngừng gửi lại những gói tin bị partner từ chối vì sai khuôn, để không đốt hạn mức gọi API vào việc vô ích.
17. Là nhân viên vận hành, tôi muốn thấy số lần đã thử gửi của mỗi gói tin, để biết cái nào đang mắc kẹt.
18. Là nhân viên vận hành, tôi muốn job không gửi gì cả khi không có event `mini_game_v2` nào đang chạy, để không tạo tải vô ích lên transaction và tracking.

### Người dựng event trên CRM

19. Là người dựng event, tôi muốn khai `eventCodes` liên quan tới đơn hàng trong `condMiniGame`, để chọn đúng loại sự kiện đơn hàng mà game cần.
20. Là người dựng event, tôi muốn khai `eventCodes` liên quan tới click trong `condTracking`, để chọn nhiệm vụ dạng hành vi giao diện.
21. Là người dựng event, tôi muốn khai `eventCodes` rỗng cho nhánh mình không dùng, để event chỉ đẩy đúng loại sự kiện mình cần.
22. Là người dựng event, tôi muốn CRM chỉ cho chọn các mã sự kiện hợp lệ, để không khai nhầm mã mà partner sẽ từ chối.
23. Là người dựng event, tôi muốn `condTracking` nhập được từ CRM, để không phải nhờ kỹ thuật sửa tay trong database.

### Đội kỹ thuật

24. Là kỹ sư trực hệ thống, tôi muốn job không gửi trùng ngay cả khi hai instance chạy song song, để không phụ thuộc vào việc chỉ có đúng một worker sống.
25. Là kỹ sư trực hệ thống, tôi muốn mất Redis không dẫn tới gửi trùng, để sự cố hạ tầng chỉ làm chậm chứ không làm sai.
26. Là kỹ sư trực hệ thống, tôi muốn nhánh đơn hàng lỗi không kéo nhánh click chết theo, để một nguồn dữ liệu hỏng không chặn nguồn kia.
27. Là kỹ sư trực hệ thống, tôi muốn job có thể tắt bằng biến môi trường, để cô lập sự cố mà không cần deploy lại.
28. Là kỹ sư bảo trì, tôi muốn thay đổi hợp đồng NATS của transaction không làm vỡ gamification đang dùng, để triển khai được từng phần.
29. Là kỹ sư bảo trì, tôi muốn RPC mới của tracking không đụng vào `GetTracking` cũ, để gamification chạy nguyên trạng.
30. Là kỹ sư bảo trì, tôi muốn logic khớp điều kiện đơn hàng nằm đúng một chỗ, để không phải sửa hai nơi mỗi khi luật đổi.

## Implementation Decisions

### Phạm vi sự kiện

Danh mục mã sự kiện là **danh mục đóng** do partner quy định, đã khai sẵn trong module
`portalreward`. Bên mình chỉ được gửi bốn mã: `ORDER_CREATED`, `ORDER_COMPLETED`,
`ORDER_CANCELLED`, `UI_ACTION`. Hai mã `CHECKIN` và `STREAK_REACHED` là việc xảy ra bên
partner, mình không gửi.

Không tồn tại `ORDER_UPDATED` hay `ORDER_REFUNDED`: đơn huỷ và đơn hoàn cùng dùng
`ORDER_CANCELLED`.

### Nguồn `eventCodes` và cách rẽ nhánh

`eventCodes` nằm sẵn ở hai field điều kiện khác nhau của model event, nên việc rẽ nhánh
không cần suy luận từ tên mã:

- `condMiniGame.eventCodes` → nhánh **order**, nguồn dữ liệu là service transaction.
- `condTracking.eventCodes` → nhánh **click**, nguồn dữ liệu là service tracking.

`options.eventCodes` là chỗ thứ ba đang được subscriber `GetActiveEventCodes` đọc. Job này
**không dùng** `options.eventCodes`. Sự trùng lặp giữa ba chỗ được ghi nhận là nợ kỹ thuật,
xử lý ngoài phạm vi PRD này.

### Ánh xạ trạng thái đơn sang mã sự kiện

Bốn trạng thái transaction phủ trọn ba mã đơn hàng, không chồng lấn:

| Mã sự kiện | Trạng thái transaction |
|---|---|
| `ORDER_CREATED` | `pending`, `approved` |
| `ORDER_COMPLETED` | `cashback` |
| `ORDER_CANCELLED` | `rejected` |

Danh sách trạng thái gửi xuống transaction được **suy ra từ chính `eventCodes` của event**:
event chỉ khai `ORDER_COMPLETED` thì chỉ truy vấn đơn ở trạng thái `cashback`, không kéo về
rồi vứt.

### Chiến lược fetch: theo từng event

Đã cân nhắc hai phương án và **chọn fetch theo từng event**:

- Phương án bị loại — fetch một lần cho cả partner rồi khớp trong bộ nhớ: buộc phải gộp
  điều kiện kiểu OR (hợp `brandIds`, lấy `min` các `minOrderValue`), và `orderTimeStartAt/EndAt`
  không còn là của event nào cả. Quan trọng hơn: buộc phải nhân bản logic khớp `condMiniGame`
  từ transaction service sang event — hai bản logic chắc chắn lệch nhau về sau.
- Phương án đã chọn — mỗi event một chuỗi phân trang, request mang đúng `condMiniGame` và
  đúng `startAt`/`endAt` của event đó. Transaction service lọc, event không lọc lại. Số event
  `mini_game_v2` active cùng lúc của một partner là vài cái, không phải vài trăm, nên chi phí
  N chuỗi phân trang là chấp nhận được.

### Định danh người dùng

`externalUserId` gửi sang partner là `sourceId` của user, **bắt buộc trùng** giá trị đã dùng
ở kênh LAUNCH cho cùng người dùng — ràng buộc này đã được ghi trong code kênh LAUNCH.

Cả hai nguồn dữ liệu đều **không** mang sẵn `sourceId`: transaction trả về `userId`, tracking
trả về định danh user nội bộ. Tuyệt đối không được gửi thẳng định danh nội bộ này sang partner
— phải phân giải qua service user bằng gRPC.

Method phân giải **theo lô đã tồn tại** trong client user của `event`: nhận danh sách userId,
trả về thông tin user kèm `sourceId`. Không cần đổi proto, không cần thêm RPC.

Cách dùng: gom hết userId của một trang dữ liệu, gọi **một** lượt cho cả trang, giữ kết quả
trong bộ nhớ suốt lượt chạy job để các trang sau và các event sau dùng lại. Không gọi từng
bản ghi.

Hai ca biên mà method hiện tại xử lý im lặng, và tính năng này **phải** xử lý tường minh:

- Gọi gRPC thất bại: method trả về danh sách rỗng thay vì báo lỗi. Nếu cứ thế đi tiếp thì
  toàn bộ sự việc của lượt đó bị bỏ qua mà không ai biết. Phải phát hiện và dừng lượt xử lý
  đó lại, để lượt job sau làm lại.
- User không tồn tại hoặc chưa có `sourceId`: danh sách trả về ngắn hơn danh sách hỏi. Sự
  việc của những user này **không được gửi** — gửi với `externalUserId` rỗng thì client tự
  chặn, nhưng nên loại từ sớm và ghi nhận lại để truy vết.

### Module: PortalRewardTrigger (mới)

Module điều phối, đặt trong tầng service của `event`, đăng ký vào cron sẵn có với biểu thức
hai tiếng một lần. Không nhét vào service mini game v1 hiện hữu — file đó đã lớn và đang lo
việc khác.

Trách nhiệm: quét event đang hiệu lực, tách hai nhánh, chạy hai nhánh song song, tổng hợp
kết quả. Không tự biết cách nói chuyện với transaction / tracking / partner — uỷ thác cho
các module dưới.

Điều kiện quét event: loại `mini_game_v2`, trạng thái `active`, thời điểm hiện tại nằm trong
`startAt`–`endAt`. Event không khai `eventCodes` ở cả hai nhánh thì bỏ qua ngay.

Bật/tắt bằng biến môi trường sẵn có của worker.

### Module: EventDispatcher (mới, deep module)

Đây là module sâu nhất và là chỗ đáng viết test nhất.

Giao diện: nhận vào một danh sách "sự việc thô" đã chuẩn hoá (định danh event, loại sự kiện,
định danh bản ghi gốc, sourceId, payload, thời điểm xảy ra) và trả về kết quả từng cái.

Bên trong nó gói trọn: sinh `code` ổn định, loại bỏ những cái đã gửi thành công, gửi qua
client partner theo lô song song, phân loại kết quả trả về thành bốn trạng thái, ghi bảng
`system-events`.

Nó **không biết** sự việc đến từ đơn hàng hay từ click. Nhờ vậy hai nhánh dùng chung một
đường gửi, và thêm nguồn dữ liệu thứ ba sau này không phải sửa nó.

### Module: OrderEventCollector (mới)

Nhận một event, trả về danh sách sự việc thô thuộc nhánh order.

Bên trong: dựng request từ `condMiniGame` và `startAt`/`endAt`, suy ra `statuses` từ
`eventCodes`, lặp phân trang theo con trỏ, phân giải `sourceId`, dựng payload đơn hàng.

Payload đơn hàng dùng khuôn `OrderPayload` có sẵn. Ràng buộc bắt buộc: có `amountMinor` thì
**phải** có `currency` — partner không mặc định VND, thiếu là bị từ chối. Module client đã
chặn sẵn ở hai lớp, collector chỉ cần điền đúng.

### Module: ClickEventCollector (mới)

Nhận một event, trả về danh sách sự việc thô thuộc nhánh click.

Bên trong: gọi RPC mới của tracking với khoảng thời gian của event, lặp phân trang theo con
trỏ `_id`, phân giải `sourceId`, dựng payload `UI_ACTION` với `actionKey` lấy từ loại click.

### Thay đổi hợp đồng: transaction (NATS)

Mở rộng request lấy danh sách transaction group, thêm các trường **đều tuỳ chọn** để caller
cũ (gamification) không đổi hành vi: mốc kết thúc, khoảng thời gian đặt đơn, danh sách brand,
danh sách shop, loại đơn, giá trị đơn tối thiểu, danh sách trạng thái, giới hạn số bản ghi.

Phía transaction service, phần dựng điều kiện truy vấn **tái dùng nguyên** helper đã có —
helper này đã xử lý sẵn brand gốc, trạng thái, thời gian đặt đơn, loại đơn, giá trị tối
thiểu, danh sách shop. Cờ "áp dụng tất cả" của brand và shop thì bỏ qua filter tương ứng.

Mở rộng response, thêm ba trường **bắt buộc cho tính năng này**:

- Mã đơn hàng — payload partner yêu cầu, hiện response chỉ có mã nhóm giao dịch.
- Trạng thái — không có thì không rẽ được ba mã `ORDER_*`, tức là không làm được tính năng.
- Thời điểm cập nhật gần nhất — làm con trỏ cho nhánh order, vì `ORDER_COMPLETED` và
  `ORDER_CANCELLED` là đơn cũ đổi trạng thái, con trỏ theo thời gian đặt đơn sẽ bỏ sót.

Sửa đồng bộ cả bản trong `external/` của `event` lẫn bản gốc trong repo transaction của từng
bank — đây là submodule dùng chung.

### Thay đổi hợp đồng: tracking (gRPC)

RPC `GetTracking` hiện tại **giữ nguyên xi**: nó đọc một khoá Redis rồi xoá khoá đó, và
gamification đang phụ thuộc chính xác hành vi đó. Không thể thêm lọc theo thời gian vào RPC
này mà không làm vỡ gamification, và Redis cũng không phải nguồn bền.

Thêm một RPC mới đọc thẳng collection click trong Mongo — nguồn bền, đã tồn tại sẵn. Request
nhận: partner, mốc bắt đầu, mốc kết thúc, con trỏ, giới hạn, và danh sách loại click tuỳ
chọn. Response trả từng bản ghi click kèm định danh riêng để làm con trỏ và làm `refId`.

Phía tracking, tầng truy cập dữ liệu của click hiện chỉ có ghi và đếm — phải bổ sung đường
đọc theo điều kiện.

Cần index trên collection click theo thời gian tạo và định danh; không có thì mỗi lượt quét
là quét toàn bảng.

Phía event, dựng mới client gRPC tracking theo đúng khuôn client transaction đã có, kèm biến
môi trường địa chỉ gRPC tracking (hiện chưa khai).

### Thay đổi CRM

`condTracking` hiện chỉ tồn tại ở model nội bộ, chưa có ở model CRM — nghĩa là không nhập
được từ giao diện. Bổ sung vào model CRM, đi qua cùng hàm chuẩn hoá `eventCodes` mà
`options.eventCodes` đang dùng.

Bổ sung kiểm tra giá trị: `eventCodes` phải nằm trong danh mục đóng. Hàm chuẩn hoá hiện tại
chỉ khử trùng lặp và bỏ chuỗi rỗng, không kiểm nội dung — khai sai chính tả thì tới lúc
partner trả lỗi mới biết.

Ràng buộc theo nhánh: `condMiniGame.eventCodes` chỉ nhận ba mã `ORDER_*`;
`condTracking.eventCodes` chỉ nhận `UI_ACTION`.

### Schema: bảng `system-events`

Bảng mới trong database của `event`, đặt tên theo convention kebab-case số nhiều đang dùng.

Mỗi partner có database riêng nên **không có** trường mã partner trong bảng này.

Các nhóm trường:

- **Định danh sự việc**: `code` (chính là `eventId` gửi partner), `type`, `provider`.
- **Nguồn gốc**: event nội bộ, user, `source` (tức `sourceId`), `refId` (mã đơn hoặc định
  danh click), `channel` (`order` hoặc `click`).
- **Nội dung đã gửi**: payload nguyên văn, thời điểm xảy ra, và `date`.
- **Kết quả gửi**: trạng thái, số lần thử, mã truy vết partner, cờ đã trùng, mã HTTP, mã lỗi
  nghiệp vụ, chi tiết lỗi.
- **Dấu thời gian**: tạo, cập nhật, gửi.

`code` sinh bằng băm ổn định từ (event, loại sự kiện, refId). Chạy lại bao nhiêu lần cũng ra
cùng một giá trị — đúng định nghĩa của partner: `eventId` là định danh của **sự việc**, không
phải của **lượt gửi**. Không cần thêm mã partner vào công thức vì database đã tách riêng và
định danh event không đụng nhau.

`date` là thời điểm xảy ra cắt về 00:00 giờ HCM rồi lưu dạng UTC, dùng helper sẵn có. Lý do
tồn tại: partner có job quét lại các sự kiện thuộc một ngày cụ thể, mà truy vấn theo khoảng
thời gian chính xác tới giây thì không khớp được ranh giới ngày bên họ. Mốc tính là **thời
điểm sự việc xảy ra**, không phải thời điểm gửi — để hai bên cùng gọi tên một ngày; nếu lấy
mốc gửi thì đơn xảy ra 23:50 hôm trước, job chạy 00:30 hôm sau sẽ bị ghi lệch một ngày so
với partner.

Payload lưu nguyên văn để hai việc: gửi lại mà không phải hỏi lại transaction / tracking, và
chứng minh với partner khi hai bên tranh luận về nội dung gói tin.

Index:

- **Duy nhất** trên `code` — đây là hàng rào chống trùng thật sự. Kể cả logic ứng dụng sai,
  Redis mất, hay hai instance chạy song song, database vẫn không cho ghi trùng. Chống trùng
  là ràng buộc dữ liệu, không phải quy ước lập trình.
- Theo trạng thái — gom việc gửi lại.
- Theo `date`, và theo `date` + loại — phục vụ đối soát theo ngày.
- Theo event + loại — tra cứu theo event.
- Theo `channel` + `refId` — tra ngược từ một đơn hàng hoặc một click cụ thể.

Hàm tạo index duy nhất đã tồn tại trong module database nhưng chưa chỗ nào dùng; đây là chỗ
dùng đầu tiên.

### Bốn trạng thái và luật gửi lại

| Trạng thái | Nghĩa | Lượt job sau |
|---|---|---|
| `pending` | Đã dựng gói tin, chưa gửi xong (job chết giữa chừng) | Gửi lại |
| `success` | HTTP 200, **kể cả** khi partner báo đã trùng | Bỏ qua vĩnh viễn |
| `failed` | 429 hoặc 5xx hoặc lỗi mạng | Gửi lại, tăng số lần thử |
| `dropped` | 400, 409, 422 — sai khuôn, gửi lại vẫn sai | Dừng, chờ người xử lý |

Ranh giới giữa `failed` và `dropped` lấy thẳng từ hàm `IsRetryable` của module partner,
không tự chế logic song song.

Partner báo trùng (`deduplicated`) là kết quả **thành công**, không phải lỗi. Mã truy vết
`deliveryId` có thể vắng mặt ở lượt thành công — đó cũng không phải lỗi, không gửi lại vì lý
do đó. Ngược lại, `deliveryId` phải được ghi lại ở **mọi** lượt kể cả lượt bị từ chối 422,
theo yêu cầu của tài liệu tích hợp.

### Gửi lại: tái dùng chính cron hai tiếng

Không dựng cron riêng. Đầu mỗi lượt chạy, trước khi quét dữ liệu mới, xử lý những bản ghi
`pending` và `failed` chưa vượt ngưỡng số lần thử, cũ trước mới sau. Vượt ngưỡng thì chuyển
`dropped`.

Giãn cách theo số lần đã thử để không đấm liên tục vào partner đang lỗi: chỉ thử lại khi đã
qua một khoảng tăng dần kể từ lần cập nhật gần nhất. Với chu kỳ hai tiếng, thực tế vài lần
đầu sẽ thử lại ngay lượt kế, các lần sau giãn dần.

### Con trỏ Redis: tối ưu, không phải cơ chế đúng-sai

Redis dùng chung giữa các partner (khác với Mongo đã tách database), nên **mọi khoá phải mang
mã partner**. Khoá con trỏ gồm mã partner, định danh event, và tên nhánh.

- Nhánh **click**: con trỏ là định danh bản ghi click cuối đã xử lý. Click là bản ghi bất
  biến, chỉ thêm mới, nên con trỏ an toàn tuyệt đối.
- Nhánh **order**: con trỏ là thời điểm cập nhật gần nhất đã xử lý. Đơn đổi trạng thái thì
  mốc này nhảy lên nên vẫn bắt được, trong khi khoảng thời gian đặt đơn vẫn giữ cố định theo
  event.

Mất Redis dẫn tới quét lại từ đầu kỳ event; index duy nhất trên `code` chặn gửi trùng. **Chậm
chứ không sai** — đó chính là lý do bảng `system-events` là bắt buộc còn con trỏ thì không.

Ghi nhận nợ kỹ thuật đã phát hiện: một số khoá Redis hiện hữu trong `event` và `gamification`
đang **thiếu mã partner**. Không sửa trong phạm vi PRD này.

### Không lưu trạng thái trước của đơn

Một đơn đi từ `pending` sang `cashback` sinh ra hai bản ghi khác nhau vì loại sự kiện khác
nhau nên `code` khác nhau. Không cần lưu trạng thái trước, không cần so sánh.

Đơn nhảy thẳng từ `pending` sang `rejected` mà job chưa kịp gửi `ORDER_CREATED` thì chỉ
`ORDER_CANCELLED` được gửi. Partner nhận `ORDER_CANCELLED` không cần `ORDER_CREATED` đi
trước, và đây cũng là hành vi đúng.

### Song song và cô lập lỗi

Hai nhánh order và click chạy song song, một nhánh hỏng không kéo nhánh kia chết. Trong mỗi
nhánh, các event xử lý tuần tự; việc gửi partner chạy song song có giới hạn worker theo khuôn
đã dùng ở các job hiện hữu.

Mọi lượt gọi partner đi qua transport đẩy sang service communication để lưu log HTTP tập
trung — đã được cài sẵn ở module khởi tạo client, không cần làm gì thêm. Ràng buộc phải giữ:
thân gói tin đã ký được chuyển **nguyên vẹn**, không tuần tự hoá lại, nếu không chữ ký lệch.

## Testing Decisions

### Thế nào là một test tốt ở đây

Chỉ kiểm hành vi quan sát được từ bên ngoài module: cho đầu vào này thì gọi ra ngoài cái gì,
ghi xuống cái gì, trả về cái gì. Không kiểm tên hàm nội bộ, không kiểm thứ tự các bước bên
trong, không mock những thứ thuộc về chính module đang kiểm.

Cụ thể với tính năng này: test phải sống sót khi đổi cách phân trang, đổi kích thước lô, đổi
số worker song song — vì đó là chi tiết cài đặt. Test phải gãy khi đổi công thức sinh `code`,
đổi ánh xạ trạng thái sang mã sự kiện, hay đổi luật phân loại lỗi thành có/không gửi lại — vì
đó là hợp đồng.

### Module được test

**EventDispatcher** — ưu tiên cao nhất, đây là deep module thật sự. Các ca:

- `code` sinh ra ổn định: cùng đầu vào chạy hai lần cho cùng giá trị.
- `code` khác nhau khi đổi loại sự kiện, dù cùng đơn hàng và cùng event.
- `code` khác nhau khi cùng đơn hàng nhưng khác event.
- Sự việc đã có bản ghi `success` thì không gửi lại.
- Partner trả 200 kèm cờ đã trùng thì ghi `success`, không phải lỗi.
- Partner trả 200 nhưng thiếu mã truy vết thì vẫn `success`.
- Partner trả 429 và 5xx thì ghi `failed` và tăng số lần thử.
- Partner trả 422, 409, 400 thì ghi `dropped` và không tăng cơ hội gửi lại.
- Mã truy vết được ghi lại cả ở lượt thành công lẫn lượt bị từ chối 422.
- Vượt ngưỡng số lần thử thì chuyển `dropped`.

**Ánh xạ trạng thái và mã sự kiện** — thuần hàm, rẻ, đáng test đầy đủ:

- Bốn trạng thái transaction ánh xạ đúng ba mã sự kiện, phủ hết, không chồng lấn.
- Suy ngược từ `eventCodes` ra danh sách trạng thái cần truy vấn.
- Mã ngoài danh mục đóng bị từ chối.

**Tính `date`** — quanh các ranh giới dễ sai:

- Sự việc lúc 23:50 giờ HCM và lúc 00:10 giờ HCM rơi vào hai ngày khác nhau.
- Đầu vào ở múi giờ UTC vẫn cho ra đúng ngày theo giờ HCM.
- Giá trị lưu xuống là mốc UTC của 00:00 giờ HCM.

**OrderEventCollector** — dựng request đúng:

- Cờ "áp dụng tất cả" của brand và shop thì không gửi danh sách lọc tương ứng.
- Khoảng thời gian đặt đơn lấy đúng `startAt`/`endAt` của event.
- Danh sách trạng thái suy đúng từ `eventCodes`.
- Có giá trị tiền thì payload phải kèm đơn vị tiền tệ.

**ClickEventCollector** — tương tự, ở mức nhẹ hơn vì điều kiện đơn giản.

**Phân giải `userId` → `sourceId`** — chỗ dễ hỏng im lặng nhất:

- Nhiều bản ghi cùng một user thì chỉ gọi service user một lượt.
- Service user trả về thiếu một số user thì sự việc của những user đó bị loại, không gửi đi.
- Gọi service user thất bại thì lượt xử lý dừng lại, không âm thầm bỏ qua toàn bộ dữ liệu.
- Không có đường nào để định danh user nội bộ lọt vào trường `externalUserId`.

**PortalRewardTrigger** — chỉ test phần điều phối:

- Không có event hợp lệ thì không gọi transaction và không gọi tracking.
- Event chỉ khai nhánh order thì không chạm tracking, và ngược lại.
- Một nhánh lỗi thì nhánh kia vẫn hoàn tất.

### Không test

Client partner (`portalreward`) đã có bộ test riêng khá đầy đủ trong `external/` — không viết
lại. Phần dựng điều kiện truy vấn bên transaction service test tại repo đó nếu cần.

### Prior art

Module `portalreward` trong `external/partnerapi` là mẫu gần nhất và tốt nhất trong repo: mỗi
file nguồn có file test tương ứng, test theo bảng ca, kiểm hành vi qua giao diện công khai,
transport được thay bằng bản giả để chặn gọi mạng thật.

Bộ test đó cũng là mẫu cho cách thay transport — chính cơ chế `SetTransport` sẽ dùng để giả
lập phản hồi partner khi test EventDispatcher.

## Out of Scope

- Hợp nhất ba chỗ đang chứa `eventCodes` (`options`, `condMiniGame`, `condTracking`) về một
  chỗ. Ghi nhận là nợ kỹ thuật.
- Bổ sung mã partner vào các khoá Redis hiện hữu đang thiếu. Chỉ khoá mới của tính năng này
  là có.
- Sửa lỗi rẽ nhánh loại click trong job của gamification (kiểm nhầm nhóm dữ liệu). Không
  thuộc luồng này.
- Chuyển gamification sang dùng RPC mới của tracking. RPC cũ giữ nguyên, gamification chạy
  nguyên trạng.
- Giao diện CRM để xem bảng `system-events`. Giai đoạn đầu tra cứu trực tiếp trong database.
- Cảnh báo tự động khi số bản ghi `dropped` tăng bất thường.
- Đẩy sự kiện theo thời gian thực. Chu kỳ hai tiếng là thoả thuận hiện tại; nếu sau này cần
  gần thời gian thực thì đó là thay đổi kiến trúc riêng, dùng NATS thay vì quét định kỳ.
- Xử lý hai mã `CHECKIN` và `STREAK_REACHED`. Partner tự sinh, mình không được gửi.
- Cơ chế xoay khoá bí mật của partner khi service đang chạy. Client đã hỗ trợ sẵn nhưng chưa
  có đường vận hành để kích hoạt.

## Further Notes

**Thứ tự triển khai gợi ý.** Ba thay đổi hợp đồng liên service là đường găng và nên đi trước,
theo thứ tự: mở rộng hợp đồng transaction, thêm RPC tracking cùng index, rồi mới tới job bên
event. Phần CRM có thể đi song song vì độc lập.

**Rủi ro lớn nhất là sai lệch `sourceId`.** Nếu `sourceId` gửi ở kênh EVENT không trùng với
`sourceId` đã gửi ở kênh LAUNCH cho cùng người dùng, partner sẽ nhận sự kiện nhưng gắn vào
một danh tính khác — hệ thống không báo lỗi gì cả, người dùng chỉ đơn giản không được cộng
lượt. Đây là loại lỗi im lặng, nên bước phân giải `userId → sourceId` cần được kiểm kỹ và
cần một cách đối chiếu với dữ liệu LAUNCH.

**Chi phí dung lượng.** Lưu payload nguyên văn cho mọi sự việc là khoản tốn nhất của bảng
này. Đổi lại được khả năng gửi lại mà không hỏi lại nguồn, và khả năng chứng minh với partner.
Nếu dung lượng thành vấn đề, hướng xử lý là dọn payload của các bản ghi `success` đã quá một
khoảng thời gian, giữ nguyên phần còn lại — không phải bỏ trường này.

**Về ngưỡng số lần thử.** Đặt ở mức năm là con số khởi điểm. Với chu kỳ hai tiếng, năm lần
trải ra khoảng vài ngày, đủ để vượt qua một sự cố kéo dài của partner mà không tích tụ vô
hạn. Nên đưa thành cấu hình để chỉnh khi có số liệu thực tế.

**Về việc partner tự dedupe.** Partner có cơ chế khử trùng riêng và trả về cờ báo đã trùng.
Cơ chế đó là lưới an toàn lớp hai, không phải lớp một: mỗi lượt gửi trùng vẫn là một lượt gọi
HTTP thật và vẫn đếm vào hạn mức. Bảng `system-events` tồn tại để không phải dựa vào lưới đó.
