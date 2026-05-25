# PRD — Tracking Facebook Post cho TCB

> Tài liệu yêu cầu sản phẩm (Product Requirements Document) cho tính năng nhận và theo dõi bài post Facebook (text/ảnh) trên TCB. Trọng tâm: **mô tả yêu cầu theo góc nhìn người dùng + tiêu chí nghiệm thu kiểm chứng được**, để QA / PM / Brand biết chính xác cần nghiệm thu cái gì.

**Ngày:** 18/05/2026
**Trạng thái:** Đề xuất
**Đối tượng đọc:** Business, Sales, PM, QA, Brand TCB, Dev
**Tài liệu liên quan:**
- [`overview.md`](./overview.md) — bối cảnh, lý do, scope nghiệp vụ
- [`tech-spec.md`](./tech-spec.md) — file/code path, regex, struct, switch-case (dành cho Dev)

> **Cách đọc tài liệu này:**
> - **Business / Sales / PM** → đọc mục 1–4 (mục tiêu, đối tượng, user stories, business rules).
> - **QA** → đọc mục 5–7 (tiêu chí nghiệm thu, bảng test case, dữ liệu test).
> - **Brand TCB** → đọc mục 1 và mục 5.4 (nghiệm thu dashboard).
> - **Dev** → đọc tài liệu này để hiểu "đúng nghĩa là gì", rồi qua [`tech-spec.md`](./tech-spec.md) để biết "sửa ở đâu".

---

## 1. Mục tiêu & phạm vi

### 1.1 Mục tiêu

Cho phép TCB **nhận, bóc tách metadata và theo dõi** bài post Facebook dạng text/ảnh của creator — loại content mà hiện tại hệ thống hoàn toàn không nhận diện được.

**Mục tiêu đo lường được (success metrics):**

| # | Chỉ số | Hiện tại | Sau release |
|---|--------|----------|-------------|
| M1 | Creator paste link bài post Facebook (text/ảnh) | Báo "link không hợp lệ" → bài vô hình | Hệ thống nhận, bóc tách, lưu được |
| M2 | Dashboard analytics phân loại theo nguồn | 2 nhóm: Facebook (video), Facebook Reels | 3 nhóm: thêm "Facebook Post" đứng riêng |
| M3 | Brand thấy được tương tác bài post của creator | Không thấy | Thấy số bài + like/comment/share tích lũy |
| M4 | Metadata bài post được cập nhật định kỳ | — | Cron tự cập nhật like/comment/share mới |

### 1.2 Trong phạm vi

- Nhận link Facebook Post (text/ảnh) — 6 dạng URL (xem mục 4, business rule BR-1).
- Bóc tách metadata: tiêu đề, mô tả, ảnh, like, comment, share, tác giả.
- Verify creator là chủ bài post (đối chiếu với tài khoản Facebook đã liên kết).
- Cập nhật metadata định kỳ qua cron.
- Dashboard analytics có breakdown riêng cho "Facebook Post".
- Bài post chảy qua OpsHub kiểm duyệt (nếu thử thách bật cờ OpsHub).

### 1.3 Ngoài phạm vi (KHÔNG nghiệm thu trong đợt này)

- ❌ **Trả thưởng** theo số bài Facebook Post (cash/point) — phase 2.
- ❌ Port sang vCreator-PH — phase 3.
- ❌ Re-classify content `facebook` cũ thành `facebook_post`.
- ❌ Tách view của video nhúng trong bài post.
- ❌ Tự động liên kết tài khoản Facebook khi creator paste link lần đầu.

> Nếu người nghiệm thu test các mục trên và "không thấy hoạt động" — đó là **đúng thiết kế**, không phải lỗi.

---

## 2. Đối tượng người dùng

| Vai trò | Mục đích sử dụng | Quan tâm gì |
|---------|------------------|-------------|
| **Creator** | Submit link bài post Facebook lên thử thách | Bài được nhận, không bị từ chối oan |
| **Admin DISO** | Duyệt bài, re-crawl, xem analytics | Phân loại đúng nguồn, dữ liệu chính xác |
| **Brand TCB (khách hàng B2B)** | Theo dõi hoạt động Facebook Post của creator trong chiến dịch | Số bài, tương tác, ai đăng bài nào |
| **OpsHub reviewer** | Kiểm duyệt nội dung bài post | Bài post hiển thị đúng (text + ảnh) để duyệt |

---

## 3. User Stories

> Mỗi story có tiêu chí nghiệm thu (AC) riêng ở mục 5. Cột "AC" trỏ tới ID kịch bản nghiệm thu tương ứng.

| ID | User Story | AC liên quan |
|----|-----------|--------------|
| US-1 | Là **creator**, tôi muốn paste link bài post Facebook (text/ảnh) lên thử thách và được hệ thống nhận, để bài của tôi được ghi nhận tham gia chiến dịch. | AC-01, AC-02 |
| US-2 | Là **creator**, tôi muốn được nhắc rõ ràng khi chưa liên kết tài khoản Facebook, để biết phải làm gì trước khi submit. | AC-03 |
| US-3 | Là **creator**, tôi không thể submit link bài post của người khác, để hệ thống đảm bảo bài thuộc đúng chủ tài khoản. | AC-04 |
| US-4 | Là **creator**, tôi được báo lỗi rõ ràng khi bài đăng ngoài thời gian thử thách, để biết bài không hợp lệ vì lý do thời gian. | AC-05 |
| US-5 | Là **admin**, tôi muốn thấy bài Facebook Post được phân loại đúng nguồn (không nhầm với video/reel) trong danh sách content. | AC-06 |
| US-6 | Là **admin**, tôi muốn re-crawl thủ công 1 bài Facebook Post để cập nhật metadata mới nhất. | AC-07 |
| US-7 | Là **hệ thống**, metadata bài post được cập nhật tự động định kỳ, để brand luôn thấy số liệu mới. | AC-08 |
| US-8 | Là **brand**, tôi muốn thấy breakdown "Facebook Post" riêng trên dashboard analytics, tách khỏi video và reel. | AC-09 |
| US-9 | Là **OpsHub reviewer**, tôi nhận được bài Facebook Post để kiểm duyệt khi thử thách bật cờ OpsHub. | AC-10 |
| US-10 | Là **toàn hệ thống**, content Facebook video/reel cũ vẫn hoạt động bình thường sau khi release tính năng này. | AC-11 |

---

## 4. Business Rules

> Luật nghiệp vụ — người nghiệm thu dựa vào đây để phân định "đúng" và "sai". Mỗi rule có lý do để không bị tranh cãi khi test.

| ID | Business Rule | Lý do |
|----|---------------|-------|
| **BR-1** | Hệ thống nhận 6 dạng link Facebook Post: `/{username}/posts/{id}`, `permalink.php?story_fbid=`, `photo.php?fbid=`, `photo/?fbid=`, `groups/{group}/posts/{id}`, `share/p/{id}`, link mobile `m.facebook.com/story.php`. | Đây là các format Facebook đang dùng cho bài text/ảnh. |
| **BR-2** | Link video (`watch?v=`, `/videos/`) và reel (`/reel/`, `share/r/`) **KHÔNG** được nhận diện là Facebook Post. | Video/reel là loại content khác, đã có flow riêng. |
| **BR-3** | Creator **BẮT BUỘC** liên kết tài khoản Facebook trước khi submit bài post. Chưa liên kết → không submit được. | TCB B2B nghiêm về xác thực chủ bài. Khác Ambassador (optional). |
| **BR-4** | Tài khoản Facebook đã liên kết phải được **duyệt** (partner approved) thì mới submit bài được. | Đảm bảo creator hợp lệ trong chương trình. |
| **BR-5** | Tác giả bài post phải **trùng** với tài khoản Facebook đã liên kết. Submit bài người khác → bị từ chối. | Tránh creator submit link bài của người khác để gian lận. |
| **BR-6** | Bài post phải đăng **trong khoảng thời gian thử thách** (`StartAt ≤ ngày đăng ≤ EndAt`). Bài đăng trước/sau → bị từ chối. | Brand chỉ ghi nhận hoạt động trong thử thách. |
| **BR-7** | Mỗi bài post chỉ được submit **1 lần** (chống trùng theo ID bài). | Tránh đếm trùng. |
| **BR-8** | Facebook Post **không có chỉ số view**. Tracking chỉ tính like, comment, share. View luôn = 0. | Bài text/ảnh không có view như video. |
| **BR-9** | Ảnh đính kèm của bài post được tải về và lưu trên hệ thống (MinIO), không dùng link ảnh gốc Facebook. | Link ảnh Facebook có thời hạn, sẽ hết hạn. |
| **BR-10** | Bài Facebook Post **không tính thưởng** trong đợt này — không cộng cash/point, không tính vào milestone. | Scope đợt này chỉ tracking. |
| **BR-11** | Bài đã duyệt mà creator xóa khỏi Facebook → hệ thống **giữ nguyên** trạng thái đã duyệt (không trừ ngược). | Theo pattern Ambassador production. |

---

## 5. Tiêu chí nghiệm thu (Acceptance Criteria)

> **Đây là phần quan trọng nhất cho người nghiệm thu.** Mỗi kịch bản viết theo cấu trúc **Given (điều kiện) — When (thao tác) — Then (kết quả mong đợi)**. Người nghiệm thu chỉ cần làm theo và đánh dấu Pass/Fail, không cần đọc code.
>
> **Quy ước:**
> - Mỗi AC có **mức nghiệm thu**: 🟢 = nghiệm thu được qua UI (PM/Brand làm được) · 🔵 = cần kiểm tra dữ liệu/log (QA làm).
> - "Thử thách" = event/campaign trên TCB. Cần chuẩn bị sẵn 1 thử thách test (xem mục 7.1).

### 5.1 Nhóm: Creator submit bài post

#### AC-01 🟢 — Submit bài post Facebook hợp lệ thành công
- **Given:** Creator đã liên kết tài khoản Facebook (đã duyệt); thử thách đang trong thời gian diễn ra.
- **When:** Creator paste link bài post Facebook (dạng `/{username}/posts/{id}`) của chính mình, bài đăng trong thời gian thử thách, rồi bấm Gửi.
- **Then:**
  - Bài được nhận, không báo lỗi.
  - Sau khi nhận, bài hiển thị trong danh sách content của creator với loại **"Facebook Post"**.
  - Bài hiển thị metadata: tiêu đề/mô tả, ảnh (nếu có), số like, comment, share.
  - Cột "View" hiển thị 0 (theo BR-8).

#### AC-02 🟢 — Hệ thống nhận đủ 6 dạng link bài post
- **Given:** Creator đủ điều kiện submit (như AC-01).
- **When:** Creator lần lượt submit 6 dạng link ở mục 7.2 (mỗi dạng 1 bài hợp lệ của chính creator).
- **Then:** Cả 6 dạng đều được nhận, không dạng nào báo "link không hợp lệ".

#### AC-03 🟢 — Chưa liên kết Facebook thì không submit được (BR-3)
- **Given:** Creator **chưa** liên kết tài khoản Facebook.
- **When:** Creator vào màn hình submit content và chọn/paste link bài post Facebook.
- **Then:**
  - Nút Gửi bị chặn (disabled) **hoặc** khi bấm Gửi hiện thông báo yêu cầu liên kết tài khoản Facebook trước.
  - Có hướng dẫn/đường dẫn tới trang "Liên kết tài khoản".
  - Bài **không** được lưu vào hệ thống.

#### AC-04 🟢 — Submit bài của người khác bị từ chối (BR-5)
- **Given:** Creator A đã liên kết tài khoản Facebook của A.
- **When:** Creator A paste link bài post của **người khác** (không phải A) và bấm Gửi.
- **Then:**
  - Hệ thống từ chối với thông báo dạng "Bài đăng không thuộc tài khoản đã liên kết".
  - Bài **không** được lưu.

#### AC-05 🟢 — Bài đăng ngoài thời gian thử thách bị từ chối (BR-6)
- **Given:** Creator đủ điều kiện; có 1 bài post đăng **trước** ngày bắt đầu thử thách.
- **When:** Creator submit link bài cũ đó.
- **Then:**
  - Hệ thống từ chối với thông báo bài đăng ngoài thời gian thử thách.
  - Bài **không** được lưu.
- **Lưu ý nghiệm thu:** Test thêm 1 bài đăng **sau** ngày kết thúc thử thách → cùng kết quả từ chối.

#### AC-12 🟢 — Submit trùng bài bị chặn (BR-7)
- **Given:** Creator đã submit thành công 1 bài post (AC-01).
- **When:** Creator submit lại **đúng link đó** lần thứ hai.
- **Then:** Hệ thống báo bài đã tồn tại / không cho submit trùng; danh sách chỉ có 1 bản ghi của bài đó.

### 5.2 Nhóm: Phân loại & không nhầm lẫn

#### AC-06 🔵 — Bài post được phân loại đúng nguồn, không nhầm video/reel (BR-1, BR-2)
- **Given:** Đã có sẵn trong hệ thống các bài: 1 video Facebook, 1 reel Facebook, 1 post Facebook.
- **When:** Admin xem danh sách content (admin panel) hoặc QA kiểm tra trường `source` trong DB.
- **Then:**
  - Bài post có nguồn = **"Facebook Post"** (`facebook_post`).
  - Bài video vẫn = "Facebook", bài reel vẫn = "Facebook Reels".
  - **Không** bài nào bị phân loại lẫn lộn.
- **Kiểm tra thêm (QA):** Submit thử 3 link video/reel ở mục 7.3 → hệ thống KHÔNG nhận diện chúng là Facebook Post.

#### AC-11 🔵 — Content cũ không bị ảnh hưởng (regression — BR quan trọng nhất)
- **Given:** Hệ thống đang có content Facebook video và Facebook Reels hoạt động bình thường trước release.
- **When:** Sau khi release tính năng Facebook Post: creator submit 1 video Facebook mới và 1 reel Facebook mới; admin xem dashboard.
- **Then:**
  - Video/reel mới submit được như trước (không lỗi, không từ chối oan).
  - Dashboard video/reel hiển thị đúng số liệu như trước.
  - **Đặc biệt:** link rút gọn (shortlink) của video/reel vẫn được resolve đúng (do tech-spec đổi cách xử lý query string — xem tech-spec mục 4.3).

### 5.3 Nhóm: Cập nhật metadata & re-crawl

#### AC-07 🔵 — Admin re-crawl 1 bài post thủ công
- **Given:** Có 1 bài Facebook Post đã lưu trong hệ thống.
- **When:** Admin bấm chức năng re-crawl bài đó trong admin panel.
- **Then:** Số like/comment/share của bài được cập nhật theo dữ liệu mới nhất từ Facebook (có thể chênh so với lần crawl đầu).

#### AC-08 🔵 — Cron cập nhật metadata định kỳ
- **Given:** Có các bài Facebook Post (trạng thái đã duyệt hoặc chờ duyệt) thuộc thử thách đang diễn ra.
- **When:** QA chạy thủ công endpoint cron `GET /api/schedule/crawl-content-facebook-post` (hoặc chờ cron tự chạy lúc 10:15).
- **Then:**
  - Log hệ thống xuất hiện dòng tag `[Facebook Post]` báo crawler bắt đầu/kết thúc.
  - Sau vài giây (crawl bất đồng bộ), số like/comment/share của các bài post được cập nhật.
  - Bài video/reel **không** bị cron này đụng tới.

### 5.4 Nhóm: Dashboard & Brand (nghiệm thu cho Brand TCB)

#### AC-09 🟢 — Dashboard hiển thị breakdown "Facebook Post" riêng (BR-8)
- **Given:** Thử thách có ít nhất 1 bài Facebook Post, 1 video Facebook, 1 reel Facebook.
- **When:** Brand/Admin mở dashboard analytics của thử thách, xem phần phân tích theo nguồn.
- **Then:**
  - Có mục/cột **"Facebook Post"** đứng riêng, tách khỏi "Facebook" (video) và "Facebook Reels".
  - Mục Facebook Post hiển thị: tổng số bài, số bài chờ duyệt / đã duyệt / bị từ chối.
  - Hiển thị like / comment / share tích lũy.
  - View của Facebook Post = 0 (hoặc ẩn cột View) — không cộng nhầm vào tổng view.

### 5.5 Nhóm: Kiểm duyệt OpsHub

#### AC-10 🔵 — Bài post chảy qua OpsHub khi bật cờ
- **Given:** Thử thách bật cờ `IsEnableOpsHub`; OpsHub đã hỗ trợ loại content `facebook_post` (xem mục 6 — dependency).
- **When:** Creator submit thành công 1 bài Facebook Post vào thử thách đó.
- **Then:**
  - Bài post xuất hiện trong hàng chờ kiểm duyệt của OpsHub.
  - OpsHub reviewer xem được nội dung bài (text + ảnh) để duyệt.
  - Kết quả duyệt từ OpsHub phản ánh ngược về trạng thái bài trên TCB.
- **Nếu OpsHub chưa hỗ trợ:** xem mục 6 — có phương án tạm skip OpsHub cho Facebook Post; khi đó AC-10 hoãn nghiệm thu, ghi rõ "blocked by OpsHub".

---

## 6. Phụ thuộc & điều kiện tiên quyết

> Người nghiệm thu cần xác nhận các mục dưới **đã sẵn sàng** trước khi bắt đầu, nếu không một số AC sẽ không test được.

| ID | Phụ thuộc | Ai xác nhận | Ảnh hưởng nếu chưa sẵn sàng |
|----|-----------|-------------|------------------------------|
| DEP-1 | Content-catcher service hỗ trợ `source=facebook_post` cho tenant TCB | Team content-catcher | **Blocker** — AC-01, AC-02, AC-07, AC-08 không test được |
| DEP-2 | OpsHub hỗ trợ kiểm duyệt loại content `facebook_post` (UI hiển thị text/ảnh) | Team OpsHub | AC-10 không nghiệm thu được; có phương án tạm skip |
| DEP-3 | Có thử thách test trên môi trường staging với thời gian phù hợp | QA / PM | Toàn bộ AC nhóm 5.1 không test được |
| DEP-4 | Có ≥ 2 tài khoản creator test, mỗi tài khoản đã/chưa liên kết Facebook | QA | AC-03, AC-04 không test được |

---

## 7. Dữ liệu & môi trường test

### 7.1 Chuẩn bị môi trường

- **Môi trường:** Staging TCB.
- **Thử thách test:** 1 thử thách đang diễn ra (`StartAt` trong quá khứ, `EndAt` trong tương lai). Tạo thêm 1 phiên bản bật `IsEnableOpsHub` để test AC-10.
- **Tài khoản test:**
  - Creator A — đã liên kết Facebook, partner đã duyệt (dùng cho AC-01, AC-02, AC-04, AC-05, AC-12).
  - Creator B — **chưa** liên kết Facebook (dùng cho AC-03).
- **Quyền truy cập:** QA cần quyền vào admin panel + xem DB collection `content`, `event_analytic_daily` + xem log service.

### 7.2 Link bài post hợp lệ — phải được NHẬN

```
https://www.facebook.com/{username}/posts/123456789
https://facebook.com/permalink.php?story_fbid=123&id=456
https://www.facebook.com/photo.php?fbid=123456&set=a.789
https://m.facebook.com/photo/?fbid=12345
https://facebook.com/share/p/abcd1234
https://www.facebook.com/groups/mygroup/posts/9876543
```

> Lưu ý: thay `{username}` và ID bằng link bài post **thật** của creator test, vì hệ thống cần crawl được metadata thật.

### 7.3 Link video/reel — phải KHÔNG bị nhận là Facebook Post

```
https://www.facebook.com/watch?v=123456          (video)
https://facebook.com/reel/abc123                  (reel)
https://www.facebook.com/share/r/xyz789           (reel rút gọn)
```

### 7.4 Bảng tổng hợp test case

| Test ID | AC | Kịch bản tóm tắt | Mức | Kết quả mong đợi | Pass/Fail | Tester | Ngày |
|---------|-----|------------------|-----|-------------------|-----------|--------|------|
| TC-01 | AC-01 | Submit bài post hợp lệ | 🟢 | Bài được nhận, loại "Facebook Post", có metadata | ☐ | | |
| TC-02 | AC-02 | Submit 6 dạng link bài post | 🟢 | Cả 6 dạng đều được nhận | ☐ | | |
| TC-03 | AC-03 | Creator chưa liên kết FB submit | 🟢 | Bị chặn + nhắc liên kết | ☐ | | |
| TC-04 | AC-04 | Submit bài của người khác | 🟢 | Bị từ chối "không thuộc tài khoản" | ☐ | | |
| TC-05 | AC-05 | Bài đăng trước ngày thử thách | 🟢 | Bị từ chối ngoài thời gian | ☐ | | |
| TC-06 | AC-05 | Bài đăng sau ngày thử thách | 🟢 | Bị từ chối ngoài thời gian | ☐ | | |
| TC-07 | AC-12 | Submit trùng bài | 🟢 | Bị chặn trùng, chỉ 1 bản ghi | ☐ | | |
| TC-08 | AC-06 | Phân loại đúng post/video/reel | 🔵 | Source đúng, không nhầm | ☐ | | |
| TC-09 | AC-06 | Submit link video/reel | 🔵 | Không bị nhận là Facebook Post | ☐ | | |
| TC-10 | AC-07 | Admin re-crawl 1 bài post | 🔵 | Like/comment/share cập nhật | ☐ | | |
| TC-11 | AC-08 | Chạy cron crawl định kỳ | 🔵 | Log `[Facebook Post]`, metadata cập nhật | ☐ | | |
| TC-12 | AC-09 | Dashboard breakdown Facebook Post | 🟢 | Mục riêng, đủ chỉ số, view = 0 | ☐ | | |
| TC-13 | AC-10 | Bài post qua OpsHub | 🔵 | Bài vào hàng chờ OpsHub | ☐ | | |
| TC-14 | AC-11 | Video/reel cũ vẫn hoạt động | 🔵 | Submit + dashboard video/reel bình thường | ☐ | | |
| TC-15 | AC-11 | Shortlink video/reel resolve đúng | 🔵 | Link rút gọn video/reel vẫn hợp lệ | ☐ | | |

---

## 8. Định nghĩa "Hoàn thành" (Definition of Done)

Tính năng được coi là **nghiệm thu đạt** khi:

- [ ] Toàn bộ test case TC-01 → TC-15 ở mức 🟢 **Pass** (PM/Brand nghiệm thu được).
- [ ] Toàn bộ test case mức 🔵 **Pass** (QA nghiệm thu được), hoặc có ghi chú "blocked by dependency" rõ ràng cho mục không test được.
- [ ] TC-14 và TC-15 (regression) **Pass** — không có hồi quy trên video/reel cũ.
- [ ] Các phụ thuộc DEP-1 → DEP-4 đã được xác nhận sẵn sàng (hoặc ghi rõ mục nào hoãn).
- [ ] Không có lỗi mức nghiêm trọng (crash, mất dữ liệu, content cũ hỏng).

> **Lưu ý OpsHub (AC-10/TC-13):** Nếu DEP-2 chưa sẵn sàng, được phép release với phương án tạm skip OpsHub cho Facebook Post (xem tech-spec mục 0.6). Khi đó DoD vẫn tính là đạt, nhưng phải mở một mục theo dõi để bật lại OpsHub sau.

---

## 9. Câu hỏi còn để ngỏ (cần Business/Brand chốt)

> Các câu hỏi này không chặn nghiệm thu phần đã định nghĩa, nhưng cần chốt để hoàn thiện hoặc lên kế hoạch phase sau.

1. Bài post đã duyệt mà creator xóa khỏi Facebook → hiện theo BR-11 là giữ nguyên. Brand có cần cơ chế đánh dấu "bài đã bị xóa" không?
2. Brand có cần xem **nội dung bài** (text + ảnh) trực tiếp trên dashboard không? (Hệ thống đã lưu sẵn, chỉ là bật/tắt hiển thị.)
3. Có cần kéo cả comment để phân tích sentiment không, hay chỉ đếm số lượng?
4. Khi nào brand cần phase 2 (trả thưởng theo số bài Facebook Post)?

---

## 10. Lịch sử thay đổi

| Ngày | Phiên bản | Thay đổi |
|------|-----------|----------|
| 18/05/2026 | 1.0 | Tạo PRD, bổ sung tiêu chí nghiệm thu cho overview + tech-spec đã có |
