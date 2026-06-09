# PRD: Liên kết tài khoản Threads cho VCreator

**Sản phẩm:** VCreator
**Tính năng:** Liên kết (đăng ký) tài khoản Threads
**Tác giả:** Product Team
**Ngày tạo:** 2026-06-09
**Phiên bản:** 1.0
**Trạng thái:** Draft
**Tham chiếu:** Tính năng "Liên kết tài khoản Threads" đã triển khai trên Ambassador (`ambassabor`)

---

## 1. Tổng quan (Overview)

### 1.1 Bối cảnh
VCreator hiện cho phép Creator liên kết các kênh mạng xã hội (TikTok, Google, Facebook) tại trang **Tài khoản → Quản lý liên kết**, phục vụ việc đăng bài tham gia thử thách và tổng hợp số liệu. Threads (Meta) đang tăng trưởng nhanh và trở thành kênh nội dung quan trọng với nhóm Creator, nhưng VCreator **chưa cho phép Creator liên kết tài khoản Threads ở phía giao diện**.

Khảo sát mã nguồn cho thấy **backend VCreator đã có sẵn hạ tầng Threads** (module `social/threads` với `ScrapeProfile`/`ScrapePost`, hằng số `SourceThreads`, model `user.Threads`, và `service/user.go` đã trả Threads trong danh sách kênh đã liên kết). Việc còn thiếu chủ yếu nằm ở **frontend** và **hoàn thiện luồng lưu liên kết**.

Ambassador đã triển khai đầy đủ tính năng này và là mẫu tham chiếu trực tiếp. Mục tiêu của PRD là đưa tính năng tương đương về VCreator.

### 1.2 Mục tiêu
- **Mục tiêu chính:** Cho phép Creator liên kết tài khoản Threads vào VCreator, hiển thị trong danh sách kênh đã liên kết và dùng để tham gia thử thách như các nền tảng hiện có.
- **Mục tiêu phụ:**
  - Tăng số kênh liên kết trung bình/Creator.
  - Mở rộng nguồn nội dung video/bài đăng đủ điều kiện tính thưởng.
  - Đồng bộ trải nghiệm liên kết MXH giữa Ambassador và VCreator.

### 1.3 Phi mục tiêu (Out of Scope)
- Đăng bài trực tiếp lên Threads từ VCreator (chỉ liên kết + nhập link bài đăng theo luồng hiện hữu).
- Phân tích/analytics chuyên sâu riêng cho Threads (dùng pipeline thống kê hiện có).
- Kiểm duyệt nội dung Threads, webhook real-time.
- Thay đổi cơ chế xác thực sang OAuth Threads Graph API (xem mục 7 – Phương án thay thế).

### 1.4 Mô hình kỹ thuật được chọn
Theo đúng cách Ambassador và backend VCreator đang vận hành: **liên kết bằng cách dán URL profile Threads** (không dùng OAuth). Hệ thống validate định dạng URL rồi gọi **external Threads scraping API** để lấy thông tin profile (username, tên hiển thị, ảnh đại diện, follower) và lưu lại. Xác thực quyền sở hữu được đảm bảo bằng cơ chế **hashtag cá nhân đặt trong Bio** + duyệt thủ công (giống TikTok/Threads hiện tại).

---

## 2. Hiện trạng & Khoảng cách (Current State & Gap Analysis)

| Hạng mục | Ambassador (mẫu) | VCreator hiện tại | Cần làm cho VCreator |
|---|---|---|---|
| Hằng số `SourceThreads = "threads"` | ✅ | ✅ Đã có | Không |
| Module backend `social/threads` (validate URL, scrape profile/post) | ✅ (regex) | ✅ Đầy đủ (`ScrapeProfile`, `ScrapePost`) | Không |
| Model `user.Threads` (ID, Username, FullName, ProfilePic, Followers, LinkSocial) | ✅ | ✅ Đã có | Không |
| `service/user.go` trả Threads trong danh sách kênh | ✅ | ✅ Đã có (`case SourceThreads`) | Kiểm tra/giữ |
| API lưu liên kết qua `linkSocial` (scrape & lưu) | ✅ | ⚠️ Cần xác minh nhánh xử lý `source=threads` | **Bổ sung/kiểm tra** |
| FE: `threads-section` (nút "Thêm tài khoản") | ✅ | ❌ Chưa có | **Làm mới** |
| FE: `threads-modal` (hướng dẫn + nhập link + hashtag) | ✅ | ❌ Chưa có | **Làm mới** |
| FE: thêm Threads vào `listSocialConnect` trang quản lý | ✅ | ❌ Chưa có | **Bổ sung** |
| FE: `postLinkUserSocial` hỗ trợ payload `linkSocial` (không phải `token`) | ✅ | ⚠️ Hiện chỉ gửi `token` | **Sửa** |
| FE: Threads là "special source" trong post-modal (chọn tài khoản, ẩn hashtag cá nhân, validate URL bài đăng) | ✅ | ❌ Chưa có | **Bổ sung** |
| Asset logo/avatar mặc định Threads | ✅ | ⚠️ Cần kiểm tra | Thêm nếu thiếu |

> Kết luận: phần lớn công việc nằm ở **frontend** (3 luồng giao diện) và **hoàn thiện nhánh lưu liên kết `linkSocial=threads`** ở backend nếu chưa có.

---

## 3. Đối tượng người dùng & User Stories

- **Là Creator**, tôi muốn liên kết tài khoản Threads của mình vào VCreator để có thể nộp bài đăng Threads tham gia thử thách.
- **Là Creator**, tôi muốn được hướng dẫn rõ ràng cách xác thực quyền sở hữu kênh (đặt hashtag cá nhân vào Bio) để liên kết được duyệt.
- **Là Creator**, tôi muốn nhìn thấy tài khoản Threads đã liên kết (tên, ảnh đại diện, trạng thái) cùng các kênh khác.
- **Là Creator**, tôi muốn chọn đúng tài khoản Threads khi nộp bài và hệ thống chỉ hiển thị hashtag chương trình (không kèm hashtag cá nhân).

---

## 4. Yêu cầu chức năng (Functional Requirements)

### 4.1 FR-1: Mục liên kết Threads trên trang Quản lý tài khoản
- Tại **Tài khoản → Quản lý liên kết**, bổ sung Threads vào danh sách kênh (`listSocialConnect`) với:
  - Logo Threads chính thức.
  - Tên: "Threads".
  - Mô tả: "Bạn có thể liên kết nhiều tài khoản".
  - `connectSection`: component `ThreadsSection`.
- Hành vi hiển thị `connectSection` cho phép **liên kết nhiều tài khoản** (tương tự TikTok: luôn hiển thị nút "Thêm tài khoản" kể cả khi đã có kênh).
- Mỗi tài khoản đã liên kết hiển thị: ảnh đại diện, tên/username, badge trạng thái (`active` → "Hoạt động", `rejected/expired` → "Hết hạn").

### 4.2 FR-2: ThreadsSection — nút khởi tạo liên kết
- Hiển thị dòng "➕ Thêm tài khoản" (giống TikTok/Ambassador).
- Khi bấm → mở `ThreadsModal`.
- Truyền `hashtag` cá nhân của user (`user.hashtag`) và trạng thái `loading` (theo effect `userState/postLinkUserSocial`).

### 4.3 FR-3: ThreadsModal — nhập link & hướng dẫn xác thực
- Tiêu đề: **"Đăng ký kênh Threads"**, nút xác nhận: **"Đăng ký"**.
- Khối hướng dẫn:
  - Bước 1: Mở tài khoản Threads, điền **hashtag cá nhân** vào phần **Bio**.
  - Bước 2: Quay lại VCreator, nhập **link tài khoản Threads** để đăng ký.
  - Hiển thị hashtag cá nhân kèm nút **Copy**.
  - Ghi chú: có thể xóa hashtag cá nhân khỏi Bio **sau khi được duyệt**.
- Trường nhập: **Link tài khoản Threads**
  - Placeholder: `https://www.threads.net/@tencuaban`
  - Ví dụ hợp lệ: `https://www.threads.net/@tencuaban`, `threads.net/@tencuaban`
- **Validate phía client:** không để trống; thông báo lỗi tiếng Việt rõ ràng ("Vui lòng nhập link tài khoản Threads").
- Khi submit → gọi `onSuccess('threads', profileUrl)`.

### 4.4 FR-4: Lưu liên kết (payload `linkSocial`)
- Frontend `postLinkUserSocial` phải hỗ trợ payload đặc thù cho Threads:
  ```ts
  // Với threads (và facebook/youtube dạng link): truyền linkSocial thay vì token
  if (source === 'threads') {
    data = { source, linkSocial: profileUrl };
  } else {
    data = { source, token: accessToken, redirectURI };
  }
  ```
- Backend nhận `source=threads`, `linkSocial=<profileUrl>`:
  1. **Validate** định dạng URL profile bằng `threads.IsValidProfileURL` (regex đã có).
  2. Gọi `threads.Client().ScrapeProfile(ctx, url)` để lấy `ProfileData` (username, full_name, profile_pic, followers, pk, is_verified, ...).
  3. Lưu/cập nhật `user.Threads` (ID/PK, Username, FullName, ProfilePic, Followers, LinkSocial = URL gốc).
  4. Trả về kết quả để FE refresh danh sách (`getListUserSocial`).
- Sau khi lưu thành công → đóng modal, làm mới danh sách kênh.

### 4.5 FR-5: Trạng thái duyệt & xác thực quyền sở hữu
- Liên kết Threads mới có thể ở trạng thái **chờ duyệt** đến khi xác nhận hashtag cá nhân xuất hiện trong Bio (theo cơ chế duyệt hiện hành của VCreator cho special source).
- Cập nhật badge trạng thái theo kết quả duyệt (`active`/`rejected`).
- (Tùy chọn) Cho phép Creator gỡ liên kết tài khoản Threads.

### 4.6 FR-6: Threads là "special source" trong luồng nộp bài (Post Modal)
> Bổ sung để liên kết phát huy tác dụng đầu cuối; có thể tách phase 2 nếu cần.
- Thêm `threads` vào mảng `specialSource` (yêu cầu **chọn tài khoản** trước khi nộp).
- Component chọn tài khoản (`social-select-account`) hiển thị danh sách tài khoản Threads đã liên kết.
- **Hashtag:** với `source === 'tiktok' || source === 'threads'` → chỉ hiển thị **hashtag chương trình**, ẩn hashtag cá nhân.
- **Validate URL bài đăng Threads** (dùng `threads.IsValidPostURL` đã có):
  - `https://www.threads.net/@username/post/postId`
  - `https://www.threads.net/t/postId`
  - Placeholder & ví dụ tương ứng trong modal.
- `transformSource`: `'threads' → 'Threads'`.

### 4.7 Đồng bộ đa biến thể frontend
VCreator có 3 biến thể FE: `frontend`, `frontend-vcreator`, `frontend-green`. Tính năng phải được áp dụng **nhất quán** cho cả ba (hoặc nêu rõ biến thể nào nằm trong phạm vi phát hành).

---

## 5. Luồng người dùng (User Flow)

```
[Trang Quản lý liên kết]
   └─ Mục "Threads" → bấm "➕ Thêm tài khoản"
        └─ [ThreadsModal]
             1. Đọc hướng dẫn → copy hashtag cá nhân
             2. Mở Threads, dán hashtag vào Bio
             3. Quay lại, dán link profile Threads
             4. Bấm "Đăng ký"
                 └─ FE: postLinkUserSocial({ source:'threads', linkSocial:url })
                      └─ BE: validate URL → ScrapeProfile → lưu user.Threads
                           └─ FE: đóng modal + refresh danh sách
   └─ Tài khoản Threads hiển thị (ảnh, tên, trạng thái)

[Nộp bài thử thách - Post Modal]  (FR-6)
   └─ Chọn nền tảng Threads → chọn tài khoản đã liên kết
        └─ Hiển thị chỉ hashtag chương trình
        └─ Dán URL bài đăng Threads (validate post URL)
        └─ Nộp bài (source='threads', accountId)
```

---

## 6. Yêu cầu phi chức năng (Non-Functional Requirements)

| Hạng mục | Yêu cầu |
|---|---|
| **Hiệu năng** | Scrape profile khi liên kết < 5s; có loading state trên modal; timeout & thông báo lỗi thân thiện khi external API chậm |
| **Độ tin cậy** | Xử lý lỗi external Threads API (profile riêng tư, không tồn tại, rate limit) với thông báo cụ thể; không lưu liên kết rác |
| **Bảo mật** | Lưu URL gốc; không lưu thông tin nhạy cảm; chống nhập URL độc hại bằng regex whitelist `threads.net`/`threads.com` |
| **Chống trùng** | Một tài khoản Threads (theo PK/username) không bị liên kết trùng cho nhiều user; cảnh báo nếu đã được liên kết |
| **i18n** | Toàn bộ text tiếng Việt (đồng bộ giọng văn hiện có); chuẩn bị khóa dịch nếu hệ thống đa ngôn ngữ |
| **Tương thích** | Web responsive; đồng bộ 3 biến thể FE |
| **Khả dụng** | Lỗi liên kết không làm hỏng trang quản lý; các kênh khác vẫn hoạt động bình thường |

---

## 7. Phương án thay thế đã cân nhắc

- **OAuth Threads Graph API (Meta):** chính danh hơn nhưng cần app review của Meta, cấu hình token/refresh, phức tạp và lệch khỏi hạ tầng hiện có (đang dùng scrape theo URL). **Không chọn cho phiên bản 1** để đảm bảo nhất quán với Ambassador và rút ngắn thời gian ra mắt. Có thể là hướng nâng cấp tương lai.

---

## 8. Phụ thuộc (Dependencies)
- **External Threads scraping API** (đã tích hợp ở backend VCreator – cần đảm bảo cấu hình endpoint/khóa cho môi trường staging & production).
- Cơ chế duyệt special source hiện hành (dùng chung với TikTok).
- Asset thiết kế: logo Threads, avatar mặc định Threads (`default-threads`, `default-avt-threads`).

---

## 9. Tiêu chí nghiệm thu (Acceptance Criteria)

- [ ] Mục **Threads** xuất hiện tại trang Quản lý liên kết với logo đúng.
- [ ] Bấm "Thêm tài khoản" mở modal "Đăng ký kênh Threads" đúng nội dung hướng dẫn.
- [ ] Hashtag cá nhân hiển thị và nút **Copy** hoạt động.
- [ ] Nhập link profile hợp lệ → liên kết thành công, scrape đúng tên/ảnh/follower.
- [ ] Nhập link sai định dạng → báo lỗi rõ ràng, không gọi backend lưu rác.
- [ ] Tài khoản Threads hiển thị trong danh sách kênh đã liên kết với trạng thái đúng.
- [ ] Có thể liên kết **nhiều** tài khoản Threads.
- [ ] (FR-6) Khi nộp bài chọn Threads: bắt buộc chọn tài khoản; chỉ hiển thị hashtag chương trình; validate đúng 2 định dạng URL bài đăng.
- [ ] TikTok và các nền tảng khác giữ nguyên hành vi (không hồi quy).
- [ ] Áp dụng nhất quán trên các biến thể FE trong phạm vi phát hành.
