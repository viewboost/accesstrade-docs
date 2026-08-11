# PRD — Tích hợp API Most-Clicked v2

**Category:** enhancement
**State:** ready-for-agent
**Related:** [Implementation plan](../superpowers/plans/2026-08-11-most-clicked-v2.md), [Spec partner](../api_get_most_product.md)

---

## Problem Statement

Người dùng mở màn hình "Đã xem gần đây" trong app và phải chờ danh sách sản phẩm load xong mới thấy được nội dung. Mỗi lần cache phía `brand` hết hạn, hệ thống lại phải hỏi AccessTrade từ đầu cho **toàn bộ** sản phẩm — kể cả những sản phẩm vừa được hỏi vài phút trước và gần như chắc chắn chưa đổi giá.

Nguyên nhân: service `brand` đang gọi System qua API `v1` (`POST /api/products/most-clicked`), vốn chỉ nhận danh sách URL trần. Không có mã định danh sản phẩm, System không có khoá để cache thông tin từng sản phẩm, nên mọi URL đều phải đi tiếp sang AccessTrade.

Hệ quả người dùng cảm nhận được:

- Màn hình "Đã xem gần đây" load chậm mỗi khi cache lạnh.
- Độ trễ tăng tuyến tính theo số sàn người dùng đã click (mỗi sàn là một lời gọi AccessTrade).
- Khi AccessTrade chậm hoặc lỗi, người dùng thấy danh sách thiếu sản phẩm hoặc rỗng, dù dữ liệu đó vừa được lấy thành công không lâu trước.

## Solution

Chuyển service `brand` sang gọi System API `v2` (`POST /api/v2/products/most-clicked`), gửi kèm `productId` cho từng URL.

Với `productId`, System cache được thông tin từng sản phẩm với TTL 2 giờ và chỉ hỏi AccessTrade phần còn thiếu. Nếu toàn bộ sản phẩm trong request đã có trong cache, System không gọi AccessTrade lần nào và trả về gần như tức thì.

Từ góc nhìn người dùng: màn hình "Đã xem gần đây" mở nhanh hơn rõ rệt từ lần thứ hai trở đi trong vòng 2 giờ, và ít bị thiếu sản phẩm hơn khi AccessTrade gặp sự cố — vì phần đã cache vẫn trả về được.

Từ góc nhìn client tích hợp: **không có gì thay đổi**. Endpoint `GET /api/brand/products/most-clicked` giữ nguyên đường dẫn, giữ nguyên cấu trúc response. Đây là thay đổi thuần tuý bên trong.

Điểm mấu chốt phát hiện khi khảo sát code: field `productId` **đã tồn tại sẵn** trên document `click` trong MongoDB. Vấn đề là aggregation pipeline khi gom nhóm click theo URL đã làm rơi mất field này. Không cần thay đổi schema, không cần backfill dữ liệu — chỉ cần giữ lại thứ vốn đã có.

## User Stories

1. Là người dùng app, tôi muốn màn hình "Đã xem gần đây" mở nhanh, để tôi quay lại sản phẩm mình quan tâm mà không phải chờ.
2. Là người dùng app, tôi muốn danh sách sản phẩm đã xem hiển thị đầy đủ tên, giá và ảnh, để tôi nhận ra ngay sản phẩm mình từng xem.
3. Là người dùng app, tôi muốn sản phẩm tôi click gần nhất nằm ở đầu danh sách, để tôi tìm lại thứ vừa xem nhanh nhất.
4. Là người dùng app, tôi muốn danh sách không lặp lại cùng một sản phẩm, để không bị rối khi lướt.
5. Là người dùng app, tôi muốn thấy được sản phẩm từ nhiều sàn khác nhau trong cùng một danh sách, để tôi có cái nhìn thống nhất về những gì mình đã xem.
6. Là người dùng app, tôi muốn danh sách vẫn hiển thị được phần lớn sản phẩm ngay cả khi một sàn đang gặp sự cố, để trải nghiệm không bị hỏng hoàn toàn.
7. Là người dùng app đã từng click sản phẩm từ trước khi tính năng này ra đời, tôi muốn những sản phẩm cũ đó vẫn hiển thị bình thường, để lịch sử xem của tôi không bị mất.
8. Là người dùng app chưa click sản phẩm nào, tôi muốn thấy danh sách rỗng thay vì màn hình lỗi, để hiểu rằng mình chưa có lịch sử chứ không phải app hỏng.
9. Là người dùng chưa đăng nhập, tôi muốn endpoint trả về danh sách rỗng thay vì lỗi, để app không crash khi render.
10. Là người dùng app, tôi muốn giá sản phẩm hiển thị không quá cũ, để tôi không bị bất ngờ khi bấm vào mua.
11. Là người dùng app, tôi muốn thông tin brand (logo, màu, tên sàn) hiển thị đúng với sàn của sản phẩm, để tôi biết mình sẽ được chuyển tới đâu.
12. Là client tích hợp, tôi muốn đường dẫn endpoint không đổi, để tôi không phải release lại app.
13. Là client tích hợp, tôi muốn cấu trúc JSON response không đổi, để code parse hiện tại tiếp tục chạy.
14. Là client tích hợp, tôi muốn trường `products` luôn là mảng (rỗng thì `[]`, không phải `null`), để tôi không phải viết null-check.
15. Là client tích hợp, tôi muốn `group.code` luôn là `"most-clicked"` và `group.name` luôn là `"Đã xem gần đây"`, để tôi hiển thị tiêu đề ổn định.
16. Là developer bảo trì service, tôi muốn logic gom nhóm sản phẩm theo sàn tách khỏi phần gọi mạng và truy vấn DB, để tôi kiểm chứng được nó mà không cần dựng hạ tầng.
17. Là developer bảo trì service, tôi muốn có test tự động cho việc gắn `productId` vào từng URL, để lỗi cache-miss âm thầm không lọt lên production.
18. Là developer bảo trì service, tôi muốn có test cho trường hợp click thiếu `productId`, để chắc chắn dữ liệu cũ không làm rơi sản phẩm khỏi danh sách.
19. Là developer bảo trì service, tôi muốn có test cho việc khử trùng lặp URL, để không vô tình gửi thừa sản phẩm sang System.
20. Là developer bảo trì service, tôi muốn kết quả gom nhóm merchant có thứ tự ổn định giữa các lần chạy, để test không bị flaky và log dễ đọc.
21. Là developer vận hành, tôi muốn log ghi rõ đang gọi phiên bản v2 kèm danh sách gửi lên, để tôi xác nhận được `productId` có thực sự được gửi hay không.
22. Là developer vận hành, tôi muốn biết cách xoá cache tầng `brand` khi kiểm thử, để tôi quan sát được lời gọi mới thay vì dữ liệu cũ.
23. Là developer vận hành, tôi muốn rollback được về `v1` chỉ bằng cách đổi lại đường dẫn, để xử lý sự cố nhanh nếu System v2 có vấn đề.
24. Là team System, tôi muốn `brand` gửi `productId` ổn định giữa các lần gọi, để cache của tôi thực sự trúng.
25. Là team System, tôi muốn `brand` gom mọi sản phẩm cùng một sàn vào một phần tử `merchantURLs`, để tôi chỉ phải gọi AccessTrade một lần cho mỗi sàn.
26. Là team System, tôi muốn `brand` gửi URL đã chuẩn hoá (bỏ query params, xử lý redirect Shopee), để khoá so khớp thứ tự của tôi hoạt động đúng.
27. Là product owner, tôi muốn thay đổi này không cần migration dữ liệu, để triển khai không có downtime.
28. Là product owner, tôi muốn API `v1` vẫn còn hoạt động sau khi chuyển, để có đường lùi nếu cần.

## Implementation Decisions

### Module sẽ xây / sửa

**`buildMerchantURLs` — deep module mới (tách từ code hiện có)**

Đây là module duy nhất được tách mới trong PRD này, và là nơi chứa toàn bộ giá trị cốt lõi của thay đổi.

- **Interface:** nhận danh sách click gần nhất của user và config môi trường; trả về danh sách nhóm-theo-merchant kèm map thứ hạng URL.
- **Tính chất:** pure function, không I/O — không chạm MongoDB, không chạm Redis, không gọi HTTP.
- **Trách nhiệm đóng gói:** chuẩn hoá URL (xử lý redirect Shopee, bỏ `universal-link`, strip query params + fragment), khử trùng lặp theo URL đã chuẩn hoá, ánh xạ brand ID sang mã sàn AccessTrade, gom nhóm theo sàn, gắn `productId` vào từng URL, và sinh map `urlOrder`.
- **Lý do tách:** logic này hiện nằm inline trong hàm điều phối, xen kẽ với truy vấn Mongo, đọc/ghi Redis và lời gọi HTTP — nên không kiểm chứng được nếu không dựng cả ba hạ tầng. Tách ra khiến toàn bộ phần dễ sai của v2 (`productId` có gắn đúng không, dedupe có sót không, thứ tự có đúng không) trở nên test được bằng unit test thuần.
- **Độ ổn định của interface:** cao. Interface phản ánh đúng contract với System (`merchantURLs` + `urlOrder`), vốn đã được cam kết giữ nguyên giữa v1 và v2.

Sau khi tách, hàm điều phối `GetProductMostClicked` trở thành lớp mỏng: kiểm tra user → đọc cache Redis → truy vấn DAO → gọi `buildMerchantURLs` → POST sang System → ghi cache.

**Tầng DAO — sửa shape dữ liệu trả về**

- Struct kết quả của truy vấn "URL click gần nhất của user" được bổ sung trường mã sản phẩm.
- Aggregation pipeline: stage `$group` (gom theo URL, giữ bản ghi gần nhất) được bổ sung để giữ lại `productId` bằng `$first`. Vì pipeline đã sắp xếp giảm dần theo thời gian tạo trước khi `$group`, `$first` lấy đúng `productId` của lần click gần nhất cho URL đó.
- Signature của hàm truy vấn **không đổi** — chỉ shape kết quả giàu thêm.

**Tầng model — đổi shape phần tử URL**

- Bổ sung kiểu mới đại diện cho một sản phẩm gửi lên System: gồm mã sản phẩm và URL.
- Trường `urls` trong nhóm-theo-merchant đổi từ mảng chuỗi sang mảng của kiểu mới này.
- Các trường `merchant` và `brandId` giữ nguyên.

**Tầng service — đổi endpoint đích**

- Đường dẫn gọi System đổi từ `/api/products/most-clicked` sang `/api/v2/products/most-clicked`.
- Struct parse response **không đổi** — v2 trả về cùng cấu trúc wrapper với v1.

### Schema changes

**Không có.** Field `productId` đã tồn tại trên document `click` (kiểu chuỗi, optional). Không thêm collection, không thêm field, không cần backfill, không cần index mới.

### API contract

**Contract với client (endpoint public của `brand`) — không đổi:**

- Method + path: `GET /api/brand/products/most-clicked`
- Xác thực: JWT của user qua header `Authorization`; user ID lấy từ context của service.
- Response: wrapper chuẩn `{code, message, data}`, trong đó `data.list` luôn chứa đúng một nhóm với `group.code = "most-clicked"`, `group.name = "Đã xem gần đây"`, và `products` luôn là mảng.

**Contract với System (thay đổi):**

- Path: `/api/v2/products/most-clicked`, method POST.
- Header: `PartnerID` (đã có sẵn trong code hiện tại) + `Content-Type: application/json`. **Không** forward `Authorization` của user — System v2 định danh partner qua `PartnerID`.
- Body: `merchantURLs` (mảng nhóm-theo-sàn) + `urlOrder` (map URL → thứ hạng, `0` là gần nhất). Khác biệt duy nhất so với v1 nằm ở `merchantURLs[].urls`: từ mảng chuỗi thành mảng object `{productId, url}`.
- Response: giữ nguyên như v1.

### Quyết định kỹ thuật

1. **Thiếu `productId` không loại bỏ sản phẩm.** Click cũ ghi trước khi hệ thống lưu `productId` sẽ decode thành chuỗi rỗng. Những sản phẩm này vẫn được gửi lên System bình thường, chỉ mất lợi ích cache. Điều này cho phép migrate dần mà không mất dữ liệu lịch sử của người dùng.

2. **`omitempty` cho `productId` khi serialize.** Không gửi trường rỗng lên System, giảm nhiễu và khớp với mô tả "nên có" (không bắt buộc) trong spec partner.

3. **Thứ tự merchant phải ổn định.** Code hiện tại duyệt map để build danh sách merchant — mà thứ tự duyệt map trong Go là ngẫu nhiên. Module mới ghi nhận thứ tự merchant xuất hiện lần đầu và dùng thứ tự đó khi xuất kết quả. Điều này khiến test không flaky và log dễ đối chiếu.

4. **`productId` lấy từ click gần nhất của mỗi URL**, không phải click đầu tiên. Đảm bảo dùng mã sản phẩm mới nhất mà hệ thống ghi nhận được.

5. **URL được chuẩn hoá trước khi dùng làm khoá dedupe và khoá `urlOrder`.** Cùng một sản phẩm click qua hai đường link khác query params chỉ được gửi một lần. Giữ nguyên hành vi chuẩn hoá hiện có (redirect Shopee `origin_link`, bỏ `universal-link`, strip query + fragment).

6. **Cache Redis tầng `brand` giữ nguyên** — key theo user, TTL 1 giờ. Đây là lớp cache độc lập với cache 2 giờ theo sản phẩm của System; hai lớp bổ trợ nhau chứ không thay thế.

7. **Xử lý lỗi giữ nguyên.** Code hiện tại chỉ coi là lỗi khi System trả non-2xx. System v2 trả HTTP 200 kèm dữ liệu một phần khi một sàn gặp sự cố, nên nguyên tắc "trả về càng nhiều dữ liệu càng tốt" của spec được tôn trọng mà không cần sửa gì thêm.

8. **Rollback bằng cách đổi lại một dòng đường dẫn.** API v1 vẫn hoạt động và không có kế hoạch ngừng hỗ trợ. Tuy nhiên lưu ý: rollback cần revert cả shape của `urls` về mảng chuỗi, vì v1 không hiểu dạng object.

## Testing Decisions

### Thế nào là một test tốt ở đây

Test chỉ kiểm chứng **hành vi quan sát được từ bên ngoài** của module: cho đầu vào là danh sách click, kết quả trả ra có đúng nhóm, đúng `productId`, đúng thứ tự, đúng số lượng sau dedupe hay không.

Test **không** khẳng định về cách module đạt được kết quả đó — không kiểm tra biến trung gian, không kiểm tra hàm nội bộ nào được gọi, không kiểm tra thứ tự các bước bên trong. Nhờ vậy khi ai đó refactor phần chuẩn hoá URL hay đổi cách gom nhóm, test vẫn xanh miễn là contract không đổi.

Cụ thể là test dùng đầu vào giả lập (không chạm Mongo/Redis/HTTP) và so khớp toàn bộ giá trị trả về, thay vì kiểm tra rời rạc từng trường.

### Module được test

**Chỉ `buildMerchantURLs`.** Đây là module duy nhất chứa logic thực sự và là module duy nhất pure, nên là nơi duy nhất unit test mang lại giá trị tương xứng chi phí.

Ba nhóm test:

1. **Gom nhóm theo merchant kèm `productId`** — nhiều sàn, nhiều sản phẩm; kiểm chứng mỗi sàn thành đúng một nhóm, `brandId` gắn đúng, mỗi URL mang đúng `productId`, URL đã được strip query, và `urlOrder` phản ánh đúng thứ tự click đầu vào.
2. **Click thiếu `productId`** — kiểm chứng sản phẩm vẫn xuất hiện trong kết quả với mã rỗng, không bị loại bỏ, không panic. Đây là test bảo vệ dữ liệu lịch sử của người dùng.
3. **Khử trùng lặp URL** — hai click cùng trỏ về một sản phẩm qua query params khác nhau; kiểm chứng chỉ một phần tử được gửi lên và `urlOrder` chỉ có một khoá.

### Module không được test bằng unit test

- **Tầng DAO** — chỉ là thay đổi shape struct + một dòng trong pipeline. Test cần Mongo thật; giá trị thấp hơn chi phí. Được kiểm chứng qua bước verify thủ công (quan sát `productId` khác rỗng trong log).
- **Tầng model** — chỉ là định nghĩa kiểu, không có hành vi.
- **`GetProductMostClicked`** — sau khi tách, chỉ còn là lớp điều phối gọi Mongo + Redis + HTTP. Test cần mock cả ba, mà phần dễ sai đã nằm trong `buildMerchantURLs` rồi. Được kiểm chứng qua bước verify thủ công.

### Prior art trong codebase

Codebase dùng `github.com/stretchr/testify/assert`, đặt test cùng package với file được test, tên file `<tên>_test.go`. Các test hiện có theo phong cách table-driven hoặc assert trực tiếp — cả hai đều được chấp nhận. Ví dụ tham khảo: test format số điện thoại trong `external/util`, test AES trong cùng thư mục, test DAO share-link trong `internal/dao`.

### Kiểm chứng thủ công

Unit test không chứng minh được lời gọi HTTP thực sự đi tới v2 và cache của System thực sự trúng. Cần một vòng verify thủ công:

- Chạy service ở môi trường develop.
- **Xoá cache Redis của user test trước mỗi lần gọi** — cache 1 giờ tầng `brand` sẽ che mất lời gọi HTTP mới và làm bước verify vô nghĩa nếu bỏ qua.
- Gọi endpoint, xác nhận trong log thấy đang gọi v2 và danh sách gửi lên có `productId` khác rỗng ở phần lớn phần tử.
- Xoá cache lần nữa, gọi lại trong vòng 2 giờ, xác nhận response nhanh hơn rõ rệt.
- Đối chiếu: số sản phẩm trả về **có thể ít hơn** số URL gửi lên — System loại bản ghi thiếu tên, giá `0`, hoặc thiếu ảnh. Đây là hành vi đúng theo spec, không phải bug. Nếu `products` rỗng hoàn toàn trong khi log cho thấy có URL gửi lên, kiểm tra partner đã được cấu hình token AccessTrade chưa.

## Out of Scope

- **Thay đổi endpoint public của `brand`.** Đường dẫn và cấu trúc response giữ nguyên; client không phải sửa gì.
- **Bất kỳ thay đổi nào phía System hoặc AccessTrade.** Cơ chế cache 2 giờ theo `productId`, việc gọi AccessTrade một lần mỗi sàn, việc lọc bỏ sản phẩm thiếu dữ liệu — tất cả do System thực hiện và đã sẵn sàng. PRD này chỉ đảm bảo `brand` gửi đúng thứ System cần.
- **Backfill `productId` cho click cũ.** Dữ liệu lịch sử thiếu `productId` được chấp nhận vận hành ở chế độ không cache. Nếu sau này muốn tối ưu, đó là công việc riêng.
- **Thay đổi cơ chế hoặc TTL cache Redis tầng `brand`.** Giữ nguyên key theo user và TTL 1 giờ.
- **Bỏ hỗ trợ API v1.** v1 vẫn chạy; không xoá gì.
- **Tăng số lượng sản phẩm lấy về** (hiện giới hạn 10 URL gần nhất) hoặc đổi danh sách brand được phép hiển thị.
- **Forward `Authorization` của user sang System.** Endpoint most-clicked định danh qua `PartnerID`; khác với luồng lấy thông tin sản phẩm theo link vốn có forward.
- **Hiển thị `cashbackText`.** Spec ghi trường này hiện luôn rỗng, để dành cho tính năng sau.
- **Đảm bảo giá thời gian thực.** Dữ liệu có thể cũ tối đa 2 giờ. Màn hình cần giá chính xác tức thời (vd thanh toán) phải dùng API lấy thông tin sản phẩm theo link, không dùng API này.

## Further Notes

**Về mức độ rủi ro.** Thay đổi nhỏ về lượng code nhưng chạm vào ba tầng (DAO → model → service). Rủi ro lớn nhất không phải crash mà là **hỏng âm thầm**: nếu `productId` không được gửi đúng, mọi thứ vẫn chạy bình thường, response vẫn đúng, chỉ là cache không bao giờ trúng và toàn bộ lợi ích của v2 biến mất mà không ai nhận ra. Đây chính là lý do bước verify thủ công phải xác nhận bằng mắt rằng `productId` xuất hiện trong log — unit test không bắt được kiểu lỗi này.

**Về thứ tự triển khai.** Việc đổi kiểu `urls` sẽ làm build đỏ tạm thời giữa bước sửa model và bước sửa service. Đây là dự kiến, không phải sự cố; hai bước này nên nằm trong cùng một commit.

**Về hiệu quả cache trong thực tế.** Lần gọi đầu (cache lạnh) có độ trễ tương đương v1 — không nên kỳ vọng cải thiện ngay. Lợi ích thể hiện từ lần gọi thứ hai trở đi trong vòng 2 giờ. Đồng thời, cache 1 giờ tầng `brand` đã hấp thụ phần lớn lượt gọi lặp lại của cùng một user, nên cải thiện rõ nhất sẽ ở nhóm user quay lại sau khi cache `brand` hết hạn nhưng cache System còn sống — tức khoảng thời gian giữa giờ thứ 1 và giờ thứ 2.

**Về sự phụ thuộc vào chất lượng dữ liệu click.** Hiệu quả của v2 tỉ lệ thuận với tỉ lệ click có `productId`. Nếu sau khi triển khai thấy log toàn `productId` rỗng, vấn đề nằm ở luồng ghi click chứ không phải ở thay đổi này — cần điều tra riêng ở phía luồng tạo click.
