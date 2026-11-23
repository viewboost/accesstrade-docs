# PRD: Giới hạn tần suất crawl và retry request lỗi sang gateway V2

**Trạng thái:** Đã triển khai (branch `feature/update-flow-crawl`, commit `7f015ec6`, đã merge vào `develop`)
**Ngày:** 2026-11-23
**Tech spec:** [2026-11-23-crawl-rate-limit-retry-tech-spec.md](2026-11-23-crawl-rate-limit-retry-tech-spec.md)

---

## Problem Statement

Toàn bộ dữ liệu bài đăng (view, like, comment, cover...) của YouTube, TikTok, Facebook, Facebook Post, Threads và Instagram được lấy qua **gateway crawl V2** (`POST /v1.0/partner/crawl/social`). Gateway này áp dụng giới hạn **120 request/phút cho mỗi path API**. Mọi lời gọi crawl của hệ thống đều đi vào cùng một path, gồm job định kỳ, user submit bài, admin cập nhật bài và crawl profile Threads, nên tất cả dùng chung giới hạn 120 request/phút.

Các job crawl định kỳ hiện không tính tới giới hạn này:

- **Bắn request liên tục.** Mỗi job lấy content theo batch 10 URL và gửi một request async cho mỗi batch, không nghỉ giữa các request. Request async trả về rất nhanh nên vòng lặp chạy dồn dập. Một event vài nghìn bài là đủ vượt giới hạn trong chưa tới một phút.
- **Các job chạy sát nhau.** Sáu job crawl xếp trong khoảng 10:00–11:45 (và 22:00–23:45), mỗi job cách nhau 15–30 phút. Job trước chưa xong thì job sau đã bắt đầu, nên tải dồn vào gateway cùng lúc.
- **Một lỗi bỏ cả event.** Khi một request lỗi (ví dụ bị 429 do vượt giới hạn), vòng lặp `break`. Toàn bộ content còn lại của event hoặc mission đó không được crawl cho tới lượt cron sau, tức **12 tiếng sau**. Lỗi chỉ được in ra console, không được lưu lại để xử lý tiếp.
- **Job song song không kiểm soát.** `ProcessTiktokUnauthorized` tạo một goroutine cho mỗi tài khoản TikTok, mỗi goroutine gửi request riêng, nên có thể bắn hàng chục request cùng lúc.
- **Tranh quota với user.** Khi job đang bắn dồn, request của user submit bài cũng dễ bị gateway từ chối. User nhận lỗi "link không hợp lệ" dù link đúng.

Hệ quả: số liệu view/like của content bị thiếu hoặc chậm cập nhật một cách ngẫu nhiên, ảnh hưởng trực tiếp tới thống kê, mốc thưởng và đối soát. Vận hành không có cách nào biết batch nào đã bị bỏ sót.

## Solution

Ba thay đổi chính:

1. **Giãn lịch các job crawl.** Mỗi platform chạy cách nhau 1 tiếng rưỡi, theo thứ tự ưu tiên, tính lùi từ 23:30. Mỗi job vẫn chạy 2 lần/ngày, cách nhau 12 tiếng.
2. **Mỗi giây chỉ gửi 1 request.** Trong các job crawl, sau mỗi request sang gateway, job nghỉ 1 giây. Như vậy một job tối đa 60 request/phút, bằng một nửa giới hạn của gateway, chừa phần còn lại cho user submit, admin và các job khác.
3. **Tự động retry request lỗi.** Request async của job bị lỗi HTTP (khác 200) được đánh dấu trong `crawl-request-logs`. Một cron chạy 2 phút/lần gửi lại các request này, tối đa 3 lần, mỗi lần cách nhau 5 phút. Job retry chỉ chạy khi không có job crawl nào đang chạy, và tại mỗi thời điểm chỉ có một lượt retry.

Kèm theo đó, các job crawl **không dừng cả event/mission khi một batch lỗi** nữa. Batch lỗi đã có cơ chế retry, nên job chạy tiếp các batch sau.

## Lịch chạy mới

| Thứ tự ưu tiên | Job | Lịch cũ | Lịch mới |
|---|---|---|---|
| 1 | TikTok | 10:30 / 22:30 | **11:30 / 23:30** |
| 2 | TikTok Self (TikTok có access token) | 11:00 / 23:00 | **10:00 / 22:00** |
| 3 | Facebook Post | 10:15 / 22:15 | **08:30 / 20:30** |
| 4 | YouTube | 11:15 / 23:15 | **07:00 / 19:00** |
| 5 | Threads | 11:45 / 23:45 | **05:30 / 17:30** |
| 6 | Facebook / Facebook Reels | 10:00 / 22:00 | **04:00 / 16:00** |
| — | Retry request crawl lỗi (mới) | — | **2 phút/lần** |

Lịch được tính lùi từ 23:30: platform ưu tiên cao nhất (TikTok) chạy lúc 23:30, mỗi platform tiếp theo chạy sớm hơn 1 tiếng rưỡi. Vòng thứ hai chạy sớm hơn vòng thứ nhất 12 tiếng.

## User Stories

### Vận hành / đối soát

- Là người vận hành, tôi muốn số liệu content của mọi platform được cập nhật đầy đủ sau mỗi lượt crawl, để thống kê và mốc thưởng không bị thiếu.
- Là người vận hành, khi một batch crawl bị lỗi tạm thời (gateway quá tải, timeout), tôi muốn hệ thống tự gửi lại mà không cần thao tác tay.
- Là người vận hành, tôi muốn tra được batch nào đã lỗi, đã retry bao nhiêu lần và kết quả cuối cùng, để khi user khiếu nại tôi biết content đó có được crawl hay không.

### User (KOL/KOC)

- Là user, khi tôi submit link bài đăng, tôi muốn hệ thống lấy được thông tin bài ngay, không bị báo "link không hợp lệ" chỉ vì job nền đang chiếm hết quota.

### Đội kỹ thuật

- Là dev, tôi muốn hệ thống không bao giờ vượt giới hạn của gateway do lỗi của chính mình, để không bị đối tác chặn.
- Là dev, tôi muốn các job crawl không chồng lên nhau và không tranh quota với job retry.

## Implementation Decisions

### Giãn cách đặt trong từng job, không đặt ở client dùng chung

Việc nghỉ 1 giây được đặt trong vòng lặp của từng job schedule, không đặt ở hàm gọi gateway dùng chung (`postCrawlSocialV2`). Lý do: hàm dùng chung còn phục vụ request đồng bộ của user (submit bài, admin, profile Threads). Nếu đặt limiter ở đó, user sẽ phải xếp hàng sau job nền.

Hệ quả cần chấp nhận: giãn cách chỉ đúng khi tại một thời điểm chỉ có một job gọi gateway. Điều này được đảm bảo bằng lịch cách nhau 1 tiếng rưỡi và guard chống chạy chồng (xem bên dưới).

### Chỉ retry request async của job

Chỉ request **async** (từ các job crawl, kết quả trả về sau qua callback) mới được retry. Request **đồng bộ** (user submit bài, admin, crawl profile) không retry, vì người gọi đã nhận lỗi ngay và tự quyết định thử lại. Retry ở nền cho các request này không có ích, vì kết quả không được ai dùng.

### Điều kiện retry: HTTP khác 200

Request được coi là lỗi cần retry khi mã HTTP khác 200, kể cả lỗi mạng hoặc timeout (HTTP 0). Trường hợp HTTP 200 nhưng body báo `status` khác `success` **không** retry, vì đó là lỗi nghiệp vụ từ gateway (ví dụ link không tồn tại), gửi lại cũng không thay đổi kết quả.

### Tối đa 3 lần, mỗi lần cách 5 phút

- Lần retry đầu tiên được hẹn 5 phút sau request gốc.
- Mỗi lần retry lỗi thì hẹn lần tiếp theo sau 5 phút.
- Đến lần thứ 3 vẫn lỗi thì dừng, đánh dấu `failed`.

Cron retry quét 2 phút/lần, nên khoảng cách thực tế giữa hai lần retry là 5–7 phút.

### Job retry nhường cho job crawl

- Job retry **bỏ qua lượt chạy** nếu có bất kỳ job crawl platform nào đang chạy.
- Job retry **bỏ qua lượt chạy** nếu lượt trước của chính nó chưa xong. Tại một thời điểm chỉ có một lượt retry.
- Nếu đang retry mà một job crawl bắt đầu chạy, job retry dừng ngay, phần còn lại để lượt sau.

Lý do: cả hai cùng gọi gateway với nhịp 1 request/giây. Chạy song song sẽ thành 2 request/giây.

### Lưu vết mỗi lần retry

- Log gốc của request lỗi mang trạng thái retry: `pending`, `success` hoặc `failed`, cùng số lần đã retry và thời điểm retry kế tiếp.
- Mỗi lần gửi lại tạo một log mới có `retryOf` trỏ về log gốc. Từ một log gốc, tra được toàn bộ các lần gửi lại.
- Khi retry thành công, hệ thống tạo `contents-callback` với `request_id` mới, để job `ProcessContentCallback` nhận kết quả như một request bình thường.

### Batch lỗi không dừng cả event/mission

Trước đây một batch lỗi làm job `break` khỏi vòng lặp của event/mission đó. Giờ job ghi nhận lỗi (đã có log để retry) và **chạy tiếp batch sau**.

### Chạy tuần tự trong `ProcessTiktokUnauthorized`

Phần crawl lại TikTok cho các tài khoản vừa làm mới token trước đây chạy song song mỗi tài khoản một goroutine. Giờ các tài khoản được crawl **tuần tự trong một goroutine duy nhất**, mỗi request cách nhau 1 giây. Hàm cha (`ProcessContentCallback`) vẫn không bị chặn.

### Thêm guard cho Threads và TikTok Self

Hai job này trước đây không có cờ chống chạy chồng. Giờ chúng có guard như các job crawl khác. Nhờ vậy job retry biết được khi nào hai job này đang chạy.

## Testing Decisions

- **Unit test** cho logic quyết định log nào cần retry, với 5 trường hợp: async lỗi 429, async lỗi mạng (HTTP 0), async thành công, sync lỗi (user submit), và log của một lần gửi lại bị lỗi (chỉ gắn `retryOf`, không tạo lượt retry mới).
- Build, `go vet` và test của package `content_catcher` đều pass.
- **Chưa kiểm chứng với gateway thật.** Cần theo dõi sau khi deploy (xem phần "Theo dõi sau deploy").

## Out of Scope

- **Retry request đồng bộ** (user submit, admin, profile Threads).
- **Retry khi HTTP 200 nhưng body báo lỗi.**
- **Giới hạn tần suất chung giữa nhiều process/replica.** Giãn cách và guard chỉ có hiệu lực trong một process (xem "Hạn chế đã biết").
- **Giao diện xem trạng thái retry.** Hiện tra qua API `crawl-request-logs` có sẵn (response đã kèm các field retry) hoặc query DB.
- **Retry các log được tạo trước khi deploy.** Các log này không có `retryStatus` nên không được retry.
- **Thay đổi batch size** (vẫn 10 URL mỗi request).

## Further Notes

### Năng lực xử lý của mỗi job

Mỗi request 10 URL, nghỉ 1 giây giữa các request, nên mỗi job xử lý tối đa khoảng **600 URL/phút**, tức khoảng 54.000 URL trong một khung 1 tiếng rưỡi (chưa tính thời gian phản hồi của gateway). Nếu một platform có nhiều content hơn mức này, job sẽ chạy lấn sang khung của job kế tiếp. Khi đó hai job chạy song song và tổng tần suất lên 2 request/giây, chạm đúng giới hạn 120 request/phút. Cần theo dõi thời gian chạy thực tế của từng job (log `Done run crawler ... with N requests at ...`).

### Hạn chế đã biết

- **`ProcessTiktokUnauthorized` có thể chạy trùng một job crawl.** Hàm này chạy phút 50 mỗi giờ (bên trong `ProcessContentCallback`) và không được tính là job crawl platform. Nếu trùng với một job crawl, tổng tối đa khoảng 120 request/phút, vừa đúng giới hạn.
- **Giới hạn chỉ tính trong từng process.** Cờ chống chạy chồng và giãn cách nằm trong bộ nhớ của process. Admin là process riêng và cũng gọi gateway. Nếu backend public chạy nhiều replica, mỗi replica có cron riêng, và vấn đề chạy trùng cron đã có từ trước.
- **Access token dùng khi retry là token tại thời điểm gửi gốc.** Nếu token TikTok hết hạn trong khoảng thời gian retry, cả 3 lần retry đều có thể lỗi và log chuyển sang `failed`.
- **Gateway sập lâu.** Khi đó mọi batch của job đều lỗi và đều được đưa vào hàng retry. Mỗi lượt retry xử lý tối đa 100 log, nên hàng đợi có thể mất nhiều lượt mới hết. Log quá 3 lần sẽ `failed`, và content sẽ được crawl lại ở lượt cron kế tiếp của platform đó.

### Theo dõi sau deploy

- Số log `retryStatus = pending` có giảm dần về 0 giữa các khung crawl không.
- Tỷ lệ log `failed` so với `success`. Nếu `failed` cao, cần xem lỗi gốc là gì (429, 5xx hay token).
- Thời gian chạy thực tế của từng job crawl, có lấn sang khung của job sau không.
- Gateway còn trả 429 không (field `httpStatus` trong `crawl-request-logs`).
