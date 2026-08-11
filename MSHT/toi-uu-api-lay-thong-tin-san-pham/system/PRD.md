# PRD — API v2 `/most-clicked` với Redis product cache

**Trạng thái:** ready-for-agent
**Ngày:** 2026-08-10
**Plan triển khai:** [2026-08-10-v2-most-clicked-cache.md](../plans/2026-08-10-v2-most-clicked-cache.md)

---

## Problem Statement

Màn hình "Đã xem gần đây" của app gọi `POST /api/products/most-clicked` với danh sách URL sản phẩm mà người dùng đã click gần đây. Mỗi lần mở màn hình, hệ thống gọi thẳng sang AccessTrade (`/v1/get_product_of_merchant`) để lấy tên, giá, ảnh, tên shop cho **toàn bộ** URL trong danh sách — kể cả những sản phẩm vừa được hỏi cách đó vài phút và gần như chắc chắn chưa đổi gì.

Hệ quả người dùng và vận hành:

- **Màn hình chậm.** Thời gian hiển thị "Đã xem gần đây" luôn bằng thời gian round-trip sang AccessTrade, kể cả khi dữ liệu không hề thay đổi.
- **Phụ thuộc hoàn toàn vào AccessTrade.** AT chậm hoặc lỗi thì danh sách trống, dù dữ liệu đã từng lấy được thành công vài phút trước.
- **Lãng phí quota AT.** Cùng một sản phẩm được hỏi lại nhiều lần trong ngày; số lời gọi tăng tuyến tính theo lượt mở màn hình chứ không theo số sản phẩm thật sự mới.

Nguyên nhân gốc nằm ở hợp đồng API v1: body chỉ gửi lên URL, không có định danh sản phẩm ổn định. Không có khóa định danh thì backend không thể biết "sản phẩm này tôi đã biết rồi", nên không thể cache ở mức từng sản phẩm.

## Solution

Thêm endpoint **`POST /api/v2/products/most-clicked`** dùng body mới trong đó mỗi URL đi kèm `productId`. Có `productId` làm khóa, backend đặt một lớp cache Redis đứng trước AccessTrade:

1. Với mỗi merchant, chia danh sách URL thành hai phần: những `productId` đã có trong cache và những cái chưa.
2. Phần đã có được lấy thẳng từ Redis — **URL đó không được đưa vào payload gửi AT**.
3. Chỉ khi còn ít nhất một URL chưa có trong cache thì mới gọi AccessTrade, và chỉ gọi với đúng phần còn thiếu.
4. Mọi sản phẩm AT vừa trả về được ghi vào Redis với TTL **2 giờ**, key là `productId`, value là nguyên vẹn thông tin sản phẩm trong response AT.
5. Kết quả cuối là phần cache-hit ghép với phần AT trả về, sắp xếp theo `urlOrder` client gửi lên — **response shape giữ nguyên như v1**, client không phải đổi parser.

Điều người dùng cảm nhận được: lần mở màn hình thứ hai trở đi (trong vòng 2 giờ) hiển thị gần như tức thì và vẫn hiển thị được ngay cả khi AccessTrade đang lỗi.

API v1 giữ nguyên, không đổi hành vi, để client cũ không bị ảnh hưởng.

## User Stories

1. Là người dùng app, tôi muốn màn hình "Đã xem gần đây" hiện ra nhanh hơn ở những lần mở sau, để tôi không phải chờ mỗi lần quay lại màn hình.
2. Là người dùng app, tôi muốn vẫn thấy được các sản phẩm đã xem gần đây khi đối tác AccessTrade đang chậm hoặc lỗi, để trải nghiệm không bị trống trơn.
3. Là người dùng app, tôi muốn thứ tự sản phẩm hiển thị đúng theo mức độ tôi click gần đây, để sản phẩm tôi quan tâm nhất nằm trên cùng — dù thông tin của nó đến từ cache hay từ AccessTrade.
4. Là người dùng app, tôi muốn thông tin giá và tên sản phẩm không quá cũ, để tôi không ra quyết định dựa trên giá đã lỗi thời.
5. Là người dùng app, tôi muốn không thấy sản phẩm nào bị thiếu ảnh, thiếu tên hoặc giá bằng 0, để danh sách trông hoàn chỉnh.
6. Là developer client, tôi muốn endpoint v2 trả về đúng cấu trúc response như v1, để tôi chỉ phải đổi phần dựng request chứ không phải viết lại toàn bộ tầng parse.
7. Là developer client, tôi muốn gửi kèm `productId` cho mỗi URL, để backend có khóa định danh ổn định phục vụ cache.
8. Là developer client, tôi muốn khi tôi không có `productId` cho một URL nào đó thì request vẫn hoạt động, để tôi migrate dần mà không phải chờ có đủ dữ liệu.
9. Là developer client, tôi muốn endpoint v1 tiếp tục hoạt động y như cũ, để các phiên bản app đang chạy ngoài thị trường không bị hỏng.
10. Là developer client, tôi muốn gửi danh sách rỗng thì nhận về nhóm rỗng chứ không phải lỗi, để tôi không phải xử lý case đặc biệt.
11. Là developer client, tôi muốn `products` luôn là mảng (kể cả rỗng) chứ không phải `null`, để tránh crash khi parse.
12. Là partner tích hợp, tôi muốn dữ liệu sản phẩm được lấy đúng theo AccessTrade token của partner mình, để không bị lẫn dữ liệu giữa các partner.
13. Là người vận hành hệ thống, tôi muốn giảm số lời gọi sang AccessTrade cho cùng một sản phẩm, để tiết kiệm quota và chi phí tích hợp.
14. Là người vận hành hệ thống, tôi muốn khi tất cả sản phẩm của một merchant đều có trong cache thì hoàn toàn không phát sinh lời gọi AT nào, để tiết kiệm được thật chứ không chỉ trên lý thuyết.
15. Là người vận hành hệ thống, tôi muốn khi một merchant gọi AT lỗi thì các merchant khác trong cùng request vẫn trả về bình thường, để một đối tác lỗi không kéo sập cả màn hình.
16. Là người vận hành hệ thống, tôi muốn khi AT lỗi mà phần cache-hit vẫn còn thì hệ thống trả về phần cache-hit đó, để giữ được càng nhiều dữ liệu càng tốt.
17. Là người vận hành hệ thống, tôi muốn dữ liệu cache tự hết hạn sau 2 giờ, để giá và thông tin sản phẩm không lệch quá lâu so với sàn.
18. Là người vận hành hệ thống, tôi muốn key cache có prefix riêng biệt, để có thể quét, đếm và xoá riêng nhóm cache này mà không đụng các cache khác.
19. Là người vận hành hệ thống, tôi muốn kiểm tra được TTL và nội dung một key cache bằng `redis-cli`, để chẩn đoán nhanh khi nghi ngờ cache sai.
20. Là người vận hành hệ thống, tôi muốn đối chiếu được payload thực tế gửi sang AT qua bản ghi audit `tracking-requests`, để xác nhận rằng URL đã cache-hit thật sự bị loại khỏi lời gọi.
21. Là người vận hành hệ thống, tôi muốn Redis lỗi hoặc chưa sẵn sàng thì API vẫn chạy đúng (chỉ mất phần tối ưu), để cache không trở thành điểm chết mới.
22. Là người vận hành hệ thống, tôi muốn dữ liệu cache cũ có cấu trúc không còn hợp lệ được coi như cache-miss, để một lần đổi schema không gây lỗi hàng loạt.
23. Là developer backend, tôi muốn phần map dữ liệu AT sang response và phần sắp xếp theo thứ tự click được dùng chung giữa v1 và v2, để hai version không trôi dạt khỏi nhau theo thời gian.
24. Là developer backend, tôi muốn logic cache được tách thành module có interface đơn giản, để test được mà không cần Redis chạy thật.
25. Là developer backend, tôi muốn logic chia URL thành cache-hit/miss là hàm thuần, để kiểm chứng mọi nhánh biên bằng unit test.
26. Là developer backend, tôi muốn URL trùng lặp trong cùng một request chỉ được gửi sang AT một lần, để payload không phình vô ích.
27. Là developer backend, tôi muốn `productId` rỗng được xử lý như cache-miss thay vì gây lỗi, để không phụ thuộc vào tính đầy đủ dữ liệu phía client.
28. Là developer backend, tôi muốn có log phân biệt rõ giữa v1 và v2 khi gọi AT lỗi, để đọc log biết ngay version nào đang có vấn đề.
29. Là QA, tôi muốn kiểm chứng được kịch bản cache lạnh → cache nóng → hit một phần, để xác nhận cơ chế hoạt động đúng trước khi lên production.
30. Là QA, tôi muốn xác nhận được rằng key ghi vào Redis trùng với `productId` client gửi lên, để phát hiện sớm trường hợp cache không bao giờ hit.

## Implementation Decisions

### Kiến trúc: 3 module sâu + 1 lớp glue mỏng

**Module 1 — ProductCache (lớp cache sản phẩm)**
Đóng gói toàn bộ chi tiết lưu trữ: prefix key, TTL, serialize/deserialize. Interface ra ngoài chỉ gồm hai thao tác:

- `get(productId) -> (product, found)` — trả `found = false` khi `productId` rỗng, khi key không tồn tại, hoặc khi payload cũ không giải mã được.
- `set(productId, product)` — no-op khi `productId` rỗng; ghi với TTL cố định.

Hai thao tác này được expose dưới dạng biến hàm cấp package để test hoán đổi được bằng cache in-memory. Lý do: Redis trong codebase là singleton toàn cục khởi tạo lúc `init()`, không inject được qua tham số. Đây là điểm gián tiếp duy nhất được thêm vào, và nó nằm gọn trong một module.

**Module 2 — CachePartitioner (chia URL theo trạng thái cache)**
Hàm thuần, không I/O ngoài việc gọi `ProductCache.get`. Nhận danh sách `{productId, url}` của một merchant, trả về hai phần: các sản phẩm lấy được từ cache, và các URL còn thiếu cần hỏi AT. Luật xử lý biên nằm trọn trong module này: URL rỗng bị loại, URL trùng chỉ tính một lần, `productId` rỗng luôn là miss.

**Module 3 — MostClickedAssembler (dựng response)**
Tách ra từ phần đang inline trong service v1, gồm ba thao tác thuần:

- map danh sách sản phẩm AT sang model response, bỏ qua bản ghi thiếu tên / giá bằng 0 / thiếu ảnh;
- sắp xếp tại chỗ theo `urlOrder` (so khớp URL sau khi bỏ query params; sản phẩm không có trong `urlOrder` rơi xuống cuối);
- bọc kết quả vào đúng một group `most-clicked`, `products` luôn khác `null`.

Cả v1 và v2 đều dùng chung module này — đây là lý do v1 được refactor. Refactor không đổi hành vi v1.

**Lớp glue — Service V2 + controller + route**
Service v2 chỉ điều phối: với mỗi merchant, gọi CachePartitioner → nếu còn thiếu thì gọi AT → ghi cache những gì AT trả về → gộp → nhờ Assembler dựng response. Controller bind body v2 và trả về theo chuẩn `Response200`/`Response400` như các endpoint khác. Route đăng ký trong group v2 hiện có.

### Hợp đồng API

- Đường dẫn: `POST /api/v2/products/most-clicked` (group `/api` → `/v2` → `/products`, khớp cách `brandV2` đang tổ chức).
- Middleware: `getPartnerId`, giống v1.
- Request body: `ProductMostClickedV2Req` — **đã tồn tại sẵn trong model**, gồm `merchantURLs[]` (mỗi phần tử có `merchant`, `brandId`, `urls[]` với `urls[i] = {productId, url}`) và `urlOrder` (map URL → thứ hạng, 0 là click nhiều nhất).
- Response: giữ nguyên `ProductGroupListResp` của v1 — một group duy nhất, `group.code = "most-clicked"`, `group.name = "Đã xem gần đây"`.
- `merchantURLs` rỗng → HTTP 200 với danh sách group rỗng, không chạm Redis, không gọi AT.

### Quyết định về cache

- **Khóa cache là `product_id` do AccessTrade trả về**, không map ngược theo URL. Quyết định của người ra yêu cầu. Rủi ro đã biết: nếu `product_id` AT khác `productId` client gửi lên thì cache sẽ không bao giờ hit — bước kiểm chứng thủ công đối chiếu trực tiếp điểm này trước khi lên production.
- **TTL cố định 2 giờ**, hard-code, không đưa vào Zookeeper. Không có cơ chế invalidation chủ động; giá có thể lệch tối đa 2 giờ — đánh đổi đã chấp nhận.
- **Value là nguyên vẹn item trong response AT**, không phải model response đã map. Lý do: giữ nguyên payload gốc cho phép đổi cách map về sau mà không phải xả cache.
- **Key có prefix riêng** `cache.api.product.most-clicked:`, tách biệt với các prefix cache đang có.
- **Cache dùng chung giữa các partner**, không đưa `partnerID` vào key. Lý do: item AT trả về ở endpoint này chỉ chứa dữ liệu sản phẩm công khai (tên, giá, ảnh, shop, link) — không có commission hay link affiliate phụ thuộc token. Nếu AT bổ sung trường phụ thuộc token, phải đưa `partnerID` vào key.
- **Chỉ ghi cache cho sản phẩm AT vừa trả về**, không ghi lại phần đã cache-hit (tránh gia hạn TTL vô hạn cho sản phẩm được xem liên tục).
- **Không cache negative.** URL mà AT không trả về kết quả sẽ được hỏi lại ở lần sau.

### Xử lý lỗi

- AT lỗi ở một merchant: log và bỏ qua **phần miss** của merchant đó; phần cache-hit của chính merchant đó vẫn được trả về. Các merchant khác không bị ảnh hưởng. Request tổng thể vẫn trả HTTP 200.
- Redis lỗi/không đọc được: mọi lượt tra cứu thành cache-miss → hành vi thoái lui đúng bằng v1. Ghi cache thất bại chỉ khiến lần sau miss.

### Quan hệ với luồng audit AT

Lời gọi `get_product_of_merchant` đã được ghi vào collection `tracking-requests` bởi cơ chế tracking chung của AT client. Không cần thêm gì; bản ghi audit chính là công cụ để QA xác minh rằng payload gửi AT chỉ chứa URL bị miss.

## Testing Decisions

**Nguyên tắc:** test hành vi quan sát được từ bên ngoài module, không test chi tiết cài đặt. Cụ thể: kiểm tra "URL đã cache-hit không nằm trong danh sách gửi AT", chứ không kiểm tra "hàm nào được gọi bao nhiêu lần bên trong". Test không được phụ thuộc vào Redis, MongoDB hay Zookeeper đang chạy — module nào cần hạ tầng thật thì chỉ test phần thuần của nó và ghi rõ phần còn lại được kiểm chứng thủ công.

**Prior art trong codebase:** `app/service/product_test.go` (test logic thuần, đánh dấu `t.Skip` kèm lý do cho phần cần hạ tầng), `app/service/product_information_test.go`, và `internal/util/atapi/tracking_test.go` (pattern hoán đổi biến hàm cấp package rồi khôi phục bằng `t.Cleanup`) — pattern cuối cùng chính là thứ ProductCache sẽ dùng.

Cả bốn phần đều được viết test:

**ProductCache**
- Prefix key đúng và khác biệt với các prefix cache đang tồn tại.
- TTL đúng 2 giờ.
- Round-trip: giá trị ghi vào đọc ra nguyên vẹn.
- `productId` rỗng luôn cache-miss ở cả `get` lẫn `set`.

**CachePartitioner**
- Hit một phần: đúng sản phẩm cache-hit được trả, đúng URL miss được gom.
- Hit toàn bộ: danh sách miss rỗng — đây là điều kiện để hoàn toàn không gọi AT.
- `productId` rỗng → tính là miss.
- URL rỗng bị loại; URL trùng chỉ xuất hiện một lần trong danh sách miss.

**MostClickedAssembler**
- Bỏ qua sản phẩm thiếu tên, giá bằng 0, hoặc thiếu ảnh; giữ nguyên các trường còn lại kể cả brand.
- Sắp xếp đúng theo `urlOrder`, so khớp URL sau khi bỏ query params, sản phẩm lạ rơi xuống cuối.
- `urlOrder` rỗng → giữ nguyên thứ tự đầu vào.
- Response luôn có đúng một group `most-clicked` và `products` khác `null`.

**Service V2 orchestration**
- Nhánh input rỗng: trả group rỗng, không chạm cache, không gọi AT.
- Phần merge thuần: sản phẩm AT vừa trả về được ghi cache đúng một lượt mỗi item, phần cache-hit không bị ghi lại, kết quả gộp đúng thứ tự sau khi sort.
- Phần còn lại của hàm (gọi AT thật, tra brand từ MongoDB, đọc config Zookeeper) không unit-test được — kiểm chứng bằng kịch bản thủ công cache lạnh → cache nóng → hit một phần, có đối chiếu `redis-cli` và bản ghi `tracking-requests`.

## Out of Scope

- Cơ chế invalidation chủ động khi giá sản phẩm đổi (webhook, sync job). Dữ liệu chỉ hết hạn theo TTL.
- Đưa TTL vào cấu hình Zookeeper.
- Cache cho endpoint v1 — v1 giữ nguyên hành vi gọi AT mỗi lần.
- Cache cho các endpoint AT khác (`product-information`, `product-suggestion`, `product_recommendation`, `get_original_url`).
- Warm cache chủ động / prefetch nền.
- Metric và alert cho tỉ lệ cache hit (chỉ dựa vào log và `tracking-requests` ở giai đoạn này).
- Cache theo partner — chỉ cần khi AT bổ sung trường phụ thuộc token.
- Thay đổi phía client app để chuyển sang gọi v2 (thuộc phạm vi team mobile).
- Deprecate hoặc gỡ bỏ v1.

## Further Notes

- Các struct request v2 (`ProductMostClickedV2Req`, `MerchantV2URLs`, `URLV2`) **đã có sẵn** trong model, không tạo mới.
- Phần refactor v1 để dùng chung Assembler là thay đổi có rủi ro cao nhất trong PRD này, vì nó động vào endpoint đang chạy production. Vì vậy nó được làm thành bước riêng, có test bao phủ trước, và có bước kiểm chứng v1 riêng ở giai đoạn verify.
- Ở nhánh hiện tại có 4 test đang fail sẵn từ trước (`TestPreprocessURL_LazadaShortLink`, `TestPreprocessURL_ShopeeShort`, `TestGenerateShareShortLink_OneAT`, `TestGenerateShareShortLink_Timeout`). Chúng không liên quan tới thay đổi này; mọi test fail ngoài 4 test đó đều là hồi quy.
- Không tìm thấy cấu hình issue tracker trong repo nên PRD được lưu thành file trong `docs/superpowers/prds/` thay vì publish lên tracker. Nhãn triage tương ứng: `ready-for-agent`.
