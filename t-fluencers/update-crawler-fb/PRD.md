# PRD — Cập nhật flow crawler content Facebook (PR #753)

> Nguồn: [viewboost/techcombank#753](https://github.com/viewboost/techcombank/pull/753) — branch `feature/update-crawler-content-facebook`, base `release`.
> Phạm vi PRD bám sát diff của PR (4 thay đổi cốt lõi + locale), không mở rộng ra toàn bộ feature crawler Facebook.

## Problem Statement

Là một creator submit link bài Facebook vào một event/campaign, tôi gặp hai vấn đề:

1. **Bị chặn oan khi crawler không lấy được thông tin bài.** Với nguồn Facebook / Facebook Reels, nếu hệ thống crawl không trả về dữ liệu (bài mới đăng, bài bị giới hạn hiển thị, crawler tạm lỗi), hệ thống báo lỗi "không thể lấy thông tin link" và từ chối thẳng. Tôi không submit được dù link hoàn toàn hợp lệ.

2. **Có thể vô tình (hoặc cố ý) submit trùng cùng một bài nhiều lần.** ID của content được sinh từ URL. Chỉ cần thêm query param vào link (ví dụ `?fbclid=...`) là ra một URL khác → một ID khác → lách được cơ chế chống trùng, tạo nhiều content cho cùng một bài đăng.

Đồng thời, ở phía quản trị (admin/staff), khi nhập số liệu thống kê thủ công cho một content bằng `contentId`, không có gì ngăn staff gán một `contentId` đang thuộc về một content khác — gây trùng ID giữa hai content và sai lệch dữ liệu.

## Solution

- **Fallback mềm cho Facebook/Facebook Reels/Facebook Post:** khi crawler không trả dữ liệu, thay vì từ chối, hệ thống tạo content ở trạng thái tạm ("Đang lấy thông tin") với ID sinh từ URL đã được chuẩn hóa, và bỏ qua bước check hashtag. Creator submit được ngay, thông tin sẽ được bổ sung sau. 

- **Chuẩn hóa URL trước khi sinh ID:** loại bỏ query param và fragment khỏi URL trước khi encode thành ID. Nhờ đó cùng một bài — dù đính kèm `?fbclid=...` hay `#...` — luôn cho ra cùng một ID, đóng lỗ hổng lách chống trùng.

- **Chống gán trùng contentId khi nhập thủ công:** khi staff thêm/cập nhật số liệu qua `contentId`, hệ thống chặn nếu `contentId` đó đang thuộc về một content khác, kèm thông báo lỗi rõ ràng (song ngữ VI/EN). `contentId` cũng trở thành trường bắt buộc.

## User Stories

1. Là một creator, tôi muốn submit link Facebook mà crawler tạm chưa lấy được thông tin vẫn thành công, để tôi không bị chặn oan bởi lỗi kỹ thuật của crawler.
2. Là một creator, tôi muốn content vừa submit hiển thị trạng thái "Đang lấy thông tin" khi thông tin chưa về, để tôi biết bài đã được ghi nhận và đang chờ xử lý.
3. Là một creator, tôi muốn submit link Facebook Reels chưa crawl được vẫn được ghi nhận, để tương tự nguồn Facebook thường.
4. Là một creator submit bài Facebook Post, tôi muốn hệ thống vẫn bắt buộc xác minh quyền sở hữu (AuthorId) trước khi chấp nhận, để đảm bảo tôi chỉ được nộp bài do chính tài khoản của tôi đăng.
5. Là một creator, tôi muốn không thể submit trùng cùng một bài bằng cách thêm `?fbclid=...` vào link, để đảm bảo tính công bằng của campaign — mỗi bài chỉ tính một lần.
6. Là một creator, tôi muốn hệ thống coi `https://facebook.com/post/123` và `https://facebook.com/post/123?fbclid=abc` là cùng một bài, để tôi không vô tình tạo hai content cho một nội dung.
7. Là một creator, tôi muốn khi submit trùng một bài đã tồn tại thì nhận được thông báo "link đã được sử dụng" rõ ràng, để tôi hiểu vì sao bị chặn.
8. Là một staff quản trị, tôi muốn khi nhập số liệu thủ công cho content phải cung cấp `contentId`, để hệ thống biết chính xác đang cập nhật cho bài nào.
9. Là một staff quản trị, tôi muốn bị chặn nếu gán một `contentId` đang thuộc về content khác, để tránh tạo ra hai content cùng một ID bài đăng.
10. Là một staff quản trị, tôi muốn nhận thông báo lỗi "ID bài đăng này đã tồn tại ở một nội dung khác!" bằng tiếng Việt và tiếng Anh, để tôi hiểu và xử lý đúng bất kể ngôn ngữ đang dùng.
11. Là một quản trị viên hệ thống, tôi muốn số liệu thống kê không bị trùng contentId giữa các content, để báo cáo campaign chính xác.
12. Là một creator, tôi muốn việc chuẩn hóa URL không phá vỡ các link hợp lệ (link không có query param vẫn hoạt động như cũ), để trải nghiệm submit không thay đổi với đa số trường hợp.
13. Là một creator, tôi muốn nếu URL bị lỗi định dạng thì hệ thống vẫn cố gắng chuẩn hóa (fallback cắt thủ công `?`/`#`) thay vì làm hỏng submit, để không bị chặn bởi edge case định dạng.
14. Là một creator submit các nguồn khác (YouTube, TikTok, Instagram), tôi muốn hành vi của các nguồn đó không bị thay đổi bởi thay đổi này, để không phát sinh regression ngoài phạm vi Facebook.

## Implementation Decisions

**Module mới: `util.StripURLQuery` (deep module, tách riêng, test độc lập được)**
- Interface: `StripURLQuery(rawURL string) string`.
- Trách nhiệm duy nhất: chuẩn hóa URL về `scheme://host/path`, loại bỏ query (`RawQuery`) và fragment (`Fragment`).
- Trim khoảng trắng; chuỗi rỗng trả về nguyên trạng.
- Fallback: nếu `url.Parse` lỗi, cắt thủ công tại ký tự `?` hoặc `#` đầu tiên; nếu không có thì trả nguyên chuỗi. Đây là hàm thuần (pure), không side-effect — ứng viên lý tưởng cho unit test.

**Flow submit content công khai (public content service — hàm `Create`)**
- ID mặc định (`dataDefault.ID`) được sinh từ `Base64EncodeToString(StripURLQuery(body.URL))` thay vì trực tiếp từ `body.URL`.
- Nhánh nguồn `Facebook` / `FacebookReels`: sau khi gọi crawler, nếu `contentInfo.ID == ""` (crawler rỗng hoặc lỗi) thì fallback về `dataDefault` và tắt `isCheckHashTag`. Content vẫn được tạo với tiêu đề/mô tả/tác giả tạm là "Đang lấy thông tin".
- Nhánh nguồn `FacebookPost` giữ nguyên ràng buộc chặt: bắt buộc `Facebook.IsEnable`, bắt buộc crawler trả dữ liệu và `contentInfo.ID != ""`, verify `userSocial` thuộc user hiện tại + source facebook, và `contentInfo.AuthorId == userSocial.Data.ID`. Không dùng dataDefault.
- Cơ chế chống trùng hiện có (query `contentId` trên collection content) được giữ nguyên; thay đổi chỉ đảm bảo ID sinh ra đã được chuẩn hóa nên chống trùng chặt hơn.

**Flow nhập số liệu thủ công (admin content service — hàm `AddStatisticForContent`)**
- Thêm bước kiểm tra tồn tại: query content có `contentId == body.ContentId` và `_id != content.ID`. Nếu tìm thấy → trả lỗi `ContentKeyContentIdUsed`.
- Bước check này đặt sau khi đã xác thực content tồn tại, source nằm trong danh sách cho phép (Facebook/Facebook Reels/Facebook Post/Instagram/Instagram Reels), và event tồn tại.

**Contract request (admin request model — `ContentAddStatisticBody`)**
- `ContentId` chuyển thành trường bắt buộc trong `Validate()` (`Required`), lỗi trả về key `CommonKeyBadRequest`.

**Locale — khóa mới `ContentKeyContentIdUsed`**
- Đăng ký khóa + code trong bảng event locale, có `Message{En, Vi}`.
- VI: "ID bài đăng này đã tồn tại ở một nội dung khác!"
- EN: "This post ID already exists in another content!"

## Testing Decisions

**Nguyên tắc test tốt:** chỉ test hành vi bên ngoài (input → output / lỗi trả về), không test chi tiết cài đặt nội bộ. Với các flow phụ thuộc DB/crawler, test ở ranh giới quan sát được: giá trị trả về, loại lỗi, và tác dụng phụ có thể verify.

**Module ưu tiên test — `util.StripURLQuery`:** là hàm thuần, không phụ thuộc DB/network — bao phủ được bằng table-driven unit test. Các case cần bao gồm:
- URL có query param (`?fbclid=xxx`) → query bị loại bỏ.
- URL có fragment (`#section`) → fragment bị loại bỏ.
- URL có cả query lẫn fragment → cả hai bị loại bỏ.
- URL sạch (không query/fragment) → giữ nguyên.
- Chuỗi rỗng / chỉ khoảng trắng → trả nguyên trạng (sau trim).
- URL lỗi định dạng khiến `url.Parse` fail nhưng vẫn chứa `?`/`#` → nhánh fallback cắt thủ công.
- Hai URL cùng bài khác query → ra cùng kết quả (property chống-trùng).

**Prior art:** đã có sẵn các test cạnh kề trong cùng package service (`business_member_test.go`, `business_profile_test.go`, `code_id_test.go`, `common_test.go`) làm mẫu cho phong cách test của codebase. Test cho `StripURLQuery` nên đặt cạnh `url.go` trong package `util` theo cùng convention `_test.go`.

**Ngoài phạm vi test tự động (ghi chú):** các nhánh `AddStatisticForContent` và `Create` phụ thuộc nặng vào MongoDB DAO và crawler client; nếu không có harness mock/integration sẵn thì để lại kiểm thử thủ công thay vì viết unit test giả tạo bám vào implementation.

## Out of Scope

- Toàn bộ feature crawler Facebook rộng hơn (logic verify ownership Facebook Post qua AuthorId, hashtag check, transcript, OpsHub…) — chỉ đề cập tới mức cần thiết để mô tả ranh giới thay đổi, không phải mục tiêu build của PRD này.
- Thay đổi hành vi crawl cho YouTube, TikTok, Instagram / Instagram Reels.
- Cải tiến bản thân crawler (độ ổn định, retry, coverage lấy dữ liệu Facebook).
- Cơ chế bổ sung thông tin sau này cho content ở trạng thái "Đang lấy thông tin" (job re-crawl) — giả định đã tồn tại, không thuộc PR.
- Migration dữ liệu cho các content trùng ID đã tồn tại trước thay đổi này.

## Further Notes

- Việc chuẩn hóa URL và fallback mềm bổ trợ nhau: fallback tạo content với ID sinh từ URL, nên nếu URL không được strip thì lỗ hổng lách-chống-trùng vẫn còn. Hai thay đổi cần đi cùng nhau.
- Sự bất đối xứng giữa Facebook/Facebook Reels (fallback mềm) và Facebook Post (bắt buộc crawl) là có chủ đích: Facebook Post cần AuthorId để xác minh quyền sở hữu, không thể fallback về dataDefault.
- Thông báo lỗi ở phía creator khi trùng bài là `ContentKeyLinkUsed` (đã có sẵn); khóa mới `ContentKeyContentIdUsed` chỉ dành cho luồng admin nhập số liệu thủ công — hai luồng dùng hai message khác nhau, không gộp.
