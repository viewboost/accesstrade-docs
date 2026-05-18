# Tracking Facebook Post — TCB nhận thêm bài post text/ảnh

> Mở thêm loại content "bài post Facebook" (text/ảnh) cho TCB. Mục tiêu chỉ là **tracking** — nhận link, lấy metadata, đếm số bài, hiển thị riêng trên dashboard. **Không trả thưởng** trong phạm vi đợt này.

**Thời gian:** 11/05/2026
**Trạng thái:** Đề xuất
**Đối tượng:** Business, Sales, PM, Dev TCB
**Phạm vi:** TCB backend (Go) — module content, content-catcher, analytics dashboard

---

## ⚠️ Khác biệt quan trọng so với Ambassador

Team Ambassador đã làm Facebook Post từ lâu, nhưng cách 2 sản phẩm hoạt động khác nhau ở vài điểm. Khi triển khai cho TCB, team **giữ nguyên cách TCB đang vận hành**, không cào bằng theo Ambassador:

1. **Creator BẮT BUỘC link tài khoản Facebook trước khi đăng bài.** TCB hiện đã yêu cầu điều này cho cả Facebook video và reel — Facebook Post sẽ theo cùng luật. Trên Ambassador thì optional. Lý do: TCB B2B nghiêm hơn về xác thực chủ bài, brand cần biết chính xác ai đăng.

2. **Bài phải đăng trong khoảng thời gian thử thách.** Bài đăng trước ngày bắt đầu hoặc sau ngày kết thúc thử thách sẽ bị từ chối. Đây cũng là luật TCB hiện hành cho video/reel. Ambassador đã tắt rule này. Lý do giữ ở TCB: brand chỉ trả thưởng cho hoạt động trong thử thách, bài cũ không tính.

3. **Bài Facebook Post sẽ qua OpsHub kiểm duyệt** (nếu thử thách bật cờ `IsEnableOpsHub`). Brand vẫn duyệt từng bài như video — không phải auto-approve.

4. **Luồng đăng ký tài khoản Facebook trên TCB không đụng.** TCB dùng Facebook OAuth (đăng nhập bằng FB) còn Ambassador scrape qua content-catcher. Hai cơ chế khác hẳn, đợt này TCB giữ nguyên flow đăng ký hiện có.

---

## Tại sao phải làm?

**1. Có khách hàng đang chờ.**
Bên Sales TCB đang nhận yêu cầu từ khách hàng B2B muốn theo dõi hoạt động Facebook Post của creator. Brand cần thấy: creator có post bài về chiến dịch không, post bao nhiêu bài, mỗi bài có bao nhiêu tương tác (like, comment, share). Tracking chứ chưa cần tính thưởng.

Hiện TCB chỉ nhận link video và reel Facebook. Khi creator paste link bài post (text hoặc ảnh) lên, hệ thống không bóc tách được URL → coi như link không hợp lệ → bài post hoàn toàn vô hình trên hệ thống.

**2. Ambassador đã có sẵn pattern production.**
Ambassador (gen-green) đã hỗ trợ Facebook Post hơn 1 năm: regex bóc tách URL, gọi `content_catcher` lấy metadata, lưu source riêng `facebook_post`, dashboard breakdown theo source. Pattern đã chạy ổn định → việc copy sang TCB là **port có sẵn**, không phải design mới.

→ Đợt này team giải quyết: bổ sung khả năng nhận link Facebook Post + tracking metadata + breakdown analytics riêng. Không đụng tới video/reel hiện hành, không liên kết tới reward engine.

---

## Có gì mới?

### 1. Nhận link Facebook Post (text/ảnh)

Creator có thể paste các dạng link sau và TCB sẽ bóc tách được:

- `facebook.com/{username}/posts/{id}`
- `facebook.com/permalink.php?story_fbid=...`
- `facebook.com/photo.php?fbid=...` và `facebook.com/photo/?fbid=...`
- `facebook.com/groups/{group}/posts/{id}`
- Link share rút gọn `facebook.com/share/p/{id}`
- Link mobile `m.facebook.com/story.php?story_fbid=...`

Hệ thống tự nhận diện đây là Facebook Post (không nhầm với video hay reel), gọi tới content-catcher để lấy metadata: tiêu đề, mô tả, ảnh đính kèm, lượt like, lượt comment, lượt share, tác giả.

**Lưu ý về "view":**
Facebook Post (text/ảnh) **không có chỉ số view** như video/reel. Tracking sẽ tập trung vào **like, comment, share** thay vì view. Phần code aggregator nào đang cộng view tổng cũng không cộng view của Facebook Post (vì luôn = 0).

### 2. Cập nhật metadata định kỳ

Sau khi bài được lưu lần đầu, cron schedule sẽ định kỳ gọi lại content-catcher cho các bài Facebook Post đã duyệt để cập nhật like/comment/share mới nhất. Pattern giống như video/reel đang chạy — không phải logic mới, chỉ thêm source `facebook_post` vào danh sách job.

### 3. Verify chủ tài khoản (bắt buộc)

Creator phải link tài khoản Facebook trước. Khi paste link bài post lên, hệ thống đối chiếu `authorId` của bài với ID Facebook đã link:

- Chưa link FB → UI chặn nút submit, nhắc creator vào trang "Liên kết tài khoản"
- Đã link nhưng partner chưa được duyệt → từ chối nhận
- Đã link + đã duyệt nhưng `authorId` của bài ≠ FB đã link → từ chối với thông báo "Bài đăng không thuộc tài khoản đã liên kết"

Mục đích: brand B2B của TCB cần biết chính xác bài thuộc creator nào, tránh creator submit link bài của người khác.

### 4. Dashboard hiển thị riêng Facebook Post

Phần analytics theo source sẽ có thêm cột/breakdown **"Facebook Post"** — đứng riêng với **Facebook** (video) và **Facebook Reels**. Đây là pattern Ambassador đang dùng: trong `event_analytic_daily` có field riêng `facebookPost` ngang hàng `facebook`, `facebookReel`. Admin và brand thấy được:

- Tổng số bài post
- Bài đang chờ duyệt / đã duyệt / bị từ chối
- Like / comment / share tích luỹ (không có view)

### 5. Không đụng tới reward engine

Đợt này **không** thêm switch-case mới trong `event_schema.go`, **không** thêm field `FacebookPost` vào `UserEventStatistic` (struct phục vụ reward), **không** wiring vào `Milestone.NumberOfContent`. Khi brand chốt thêm campaign tính thưởng theo số bài Facebook Post (đợt sau), team sẽ làm phase 2.

---

## Chưa có gì (nhưng sẽ cân nhắc sau)

Team đã nghĩ tới một số ý tưởng nhưng chưa làm trong đợt này:

- **Campaign trả thưởng theo số bài post** — phase 2 khi brand chốt yêu cầu. Reward engine của TCB đã có sẵn `EventSchemaMilestone.NumberOfContent` → khi cần chỉ wire thêm.
- **vCreator-PH** — Phase 3 sẽ port pattern này sang vCreator. Đợt TCB urgent này chỉ làm cho TCB.
- **Re-classify content cũ** — bài Facebook submit trước release nếu thực ra là post text thì vẫn lưu với source `facebook`. Không re-classify để tránh đụng dữ liệu lịch sử.
- **Bóc tách video nhúng trong bài post** — một số bài Facebook Post có gắn video; hiện coi như post thường, không tách view của video riêng ra.
- **Tự động link tài khoản Facebook khi creator paste lần đầu** — đợt này yêu cầu link trước (qua flow UserSocial), không auto-bind từ link bài.

Các mục trên phụ thuộc nhu cầu thực tế khi dùng — cứ phản hồi, team sẽ làm tiếp.

---

## Một vài câu hỏi còn để ngỏ

1. Bài post bị duyệt rồi sau đó creator xoá khỏi Facebook → có cập nhật trạng thái không? Hiện theo pattern Ambassador là **giữ nguyên** (đã duyệt = đã ghi nhận, không trừ ngược).
2. Brand có cần xem nội dung bài (text + ảnh) trên dashboard không? Hệ thống lưu sẵn, chỉ là UI dashboard có bật hay không.
3. Có cần kéo cả comment để phân tích sentiment không, hay chỉ đếm số lượng comment?
4. **OpsHub** đã support kiểm duyệt content type `facebook_post` chưa? Nếu chưa cần phía OpsHub mở rộng trước khi TCB release.
5. **Content-catcher service** (endpoint `CoreContentCatcher`) đã support `source=facebook_post` cho tenant TCB chưa? Đây là dependency bắt buộc.

---

## Đọc thêm

- **Gap gốc:** [`general/gaps/p0/35-facebook-post-crawl-and-count-campaign.md`](../../general/gaps/p0/35-facebook-post-crawl-and-count-campaign.md) — phân tích gap gốc 3 sản phẩm (gap doc bao gồm cả phần reward, đợt này TCB chỉ làm phần tracking)
- **PRD:** [`prd.md`](./prd.md) — user stories, business rules và **tiêu chí nghiệm thu** (Given/When/Then + bảng test case) cho QA/PM/Brand
- **Tech Spec:** [`tech-spec.md`](./tech-spec.md) — file/code path cụ thể, regex, struct field, switch-case cần thêm
- **Source code tham chiếu (Ambassador):**
  - `accesstrade-projects/ambassabor/backend/internal/module/social/facebook/facebook.go` — regex + validation
  - `accesstrade-projects/ambassabor/backend/internal/model/mg/event_analytic_daily.go` — pattern breakdown riêng `facebookPost`

---

*Có thắc mắc, cứ phản hồi qua team backend TCB.*
