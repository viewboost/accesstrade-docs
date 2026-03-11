# TÀI LIỆU ĐẶC TẢ YÊU CẦU PHẦN MỀM

### Dự án: **Techcombank Influencer Platform (T-Fluencers)**

**Phiên bản:** 2.0

**Ngày phát hành:** 11/03/2026

**Ghi chú:** Tài liệu này mô tả chi tiết các yêu cầu chức năng của hệ thống Techcombank Influencer Platform dựa trên phạm vi đã triển khai. Bảng đối chiếu trạng thái yêu cầu xem tại `gap-analysis.md`.

---

# MỤC LỤC

- [I. Giới thiệu](#i-giới-thiệu)
- [II. Yêu cầu chức năng — Phía Creator (Influencer)](#ii-yêu-cầu-chức-năng--phía-creator-influencer)
- [III. Yêu cầu chức năng — Phía Admin](#iii-yêu-cầu-chức-năng--phía-admin)
- [IV. Hệ thống nền & Tác vụ tự động](#iv-hệ-thống-nền--tác-vụ-tự-động)
- [V. Mô hình dữ liệu](#v-mô-hình-dữ-liệu)
- [VI. Bảo mật, hạ tầng & thiết kế](#vi-bảo-mật-hạ-tầng--thiết-kế)
---

# I. Giới thiệu

## 1. Mục tiêu

Tài liệu này mô tả chi tiết yêu cầu nghiệp vụ, yêu cầu chức năng và mô hình vận hành của **hệ thống Techcombank Influencer Platform (T-Fluencers)**, bao gồm:

- Quản lý chiến dịch truyền thông (thử thách)
- Quản lý nhà sáng tạo nội dung (Influencer/Creator)
- Quản lý ngân sách chiến dịch
- Cơ chế đối soát và chi trả hoa hồng
- Quy trình duyệt nội dung
- Phân tích dữ liệu và báo cáo

## 2. Mô tả hệ thống

**Techcombank Influencer Platform** là nền tảng công nghệ được **AccessTrade (AT)** phát triển và vận hành theo yêu cầu của **Techcombank (TCB)**.

### Mô hình vận hành

| Bên tham gia | Vai trò | Phạm vi trách nhiệm |
|---|---|---|
| **Techcombank (TCB)** | Chủ sở hữu và định hướng | Xây dựng yêu cầu, giám sát qua báo cáo, duyệt chi ngân sách cho AT. Không trực tiếp thao tác hoặc thanh toán cho Influencer. |
| **AccessTrade (AT)** | Phát triển và vận hành | Phát triển hệ thống, vận hành chiến dịch, phê duyệt nội dung, tính hoa hồng, đối soát, báo cáo định kỳ cho TCB, chi trả hoa hồng cho Influencer. |
| **Influencer** | Người dùng cuối | Đăng ký, liên kết mạng xã hội, tham gia chiến dịch, đăng nội dung, nhận hoa hồng từ AT. |
| **3rd Party Provider** | Hỗ trợ kỹ thuật | Cung cấp API phân tích dữ liệu MXH, CDN, eKYC, cloud. Không truy cập trực tiếp giao diện hoặc dữ liệu người dùng. |

### Kiến trúc kỹ thuật

Hệ thống gồm 3 ứng dụng frontend và 3 dịch vụ backend:

**Frontend:**
1. **Cổng Influencer (frontend)** — Umi.js + React: nơi Influencer đăng ký, tham gia chiến dịch, theo dõi hoa hồng
2. **Cổng quản trị (admin)** — Umi.js + Ant Design Pro: dành cho đội vận hành AT quản lý chiến dịch, duyệt nội dung, đối soát
3. **Bảng phân tích (dashboard)** — Next.js 16 + React 19: dashboard phân tích dữ liệu, báo cáo nâng cao, đa ngôn ngữ

**Backend:**
1. **Public API** — Go + Echo: API dành cho Influencer
2. **Admin API** — Go + Echo: API dành cho quản trị viên
3. **File API** — Go + Echo + FFmpeg: xử lý upload/download tệp tin

**Hạ tầng:** MongoDB, Redis, MinIO (S3), Asynq (hàng đợi), Elasticsearch (APM)

---

# II. Yêu cầu chức năng — Phía Creator (Influencer)

## 1. Đăng nhập bằng Google / TikTok / Facebook / Instagram

### Mục tiêu
Cho phép người dùng đăng nhập bằng tài khoản mạng xã hội, không cần tạo tài khoản thủ công.

### Phạm vi
- Nền tảng: Cổng Influencer (web)
- Hỗ trợ: Google, TikTok, Facebook, Instagram

### Luồng nghiệp vụ
1. Người dùng chọn phương thức đăng nhập (Google / TikTok / Facebook / Instagram).
2. Ứng dụng chuyển hướng đến trang xác thực OAuth 2.0 của nền tảng tương ứng.
3. Người dùng đăng nhập và cấp quyền truy cập thông tin: email, tên hiển thị, ảnh đại diện.
4. Nền tảng trả về Authorization Code → Frontend gửi đến Backend.
5. Backend đổi mã lấy Access Token → lấy thông tin người dùng.
6. Kiểm tra: nếu người dùng đã tồn tại → đăng nhập; chưa tồn tại → tạo tài khoản mới.
7. Backend tạo JWT token, trả phản hồi đăng nhập thành công.

### Dữ liệu
| Trường | Nguồn | Lưu trữ | Ghi chú |
|---|---|---|---|
| `provider_user_id` | OAuth | DB (hash) | Định danh duy nhất |
| `provider` | Hệ thống | DB | google / tiktok / facebook / instagram |
| `email` | OAuth | DB | Không chia sẻ bên thứ ba |
| `display_name` | OAuth | DB | Cho phép chỉnh sửa |
| `avatar_url` | OAuth | DB | Có thể cập nhật |
| `access_token` | OAuth | **Không lưu** | Dùng 1 lần rồi hủy |

### Bảo mật
- Không lưu access_token sau khi đăng nhập thành công.
- Tuân thủ Nghị định 13/2023 (VN) và GDPR (EU).
- Mã hóa AES-256 cho OAuth token tạm thời.

### Kịch bản lỗi
| Tình huống | Hành động |
|---|---|
| Từ chối cấp quyền | Hiển thị thông báo, dừng tiến trình |
| Token hết hạn / không hợp lệ | Thông báo "Phiên đăng nhập thất bại" |
| Backend không kết nối OAuth server | Retry tối đa 3 lần → thông báo lỗi |

---

## 2. Cập nhật hồ sơ cá nhân

### Mục tiêu
Cho phép người dùng xem và chỉnh sửa thông tin cá nhân sau khi đăng nhập.

### Luồng nghiệp vụ
1. Người dùng truy cập trang "Thông tin tài khoản".
2. Hệ thống hiển thị: ảnh đại diện, tên hiển thị, giới tính, ngày sinh, email.
3. Người dùng chỉnh sửa và nhấn "Lưu thay đổi".
4. Backend kiểm tra: tên và email không trống, email hợp lệ, ảnh JPG/PNG ≤ 5MB.
5. Lưu thông tin và trả phản hồi thành công.

### Ràng buộc dữ liệu
| Trường | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|
| Ảnh đại diện | File (JPG, PNG) | Không | ≤ 5MB |
| Tên hiển thị | Text | Có | Không để trống |
| Giới tính | Enum (Nam, Nữ, Khác) | Không | |
| Ngày sinh | Date | Không | |
| Email | Text | Có | Định dạng email hợp lệ |

---

## 3. Đăng ký kênh mạng xã hội

### Mục tiêu
Cho phép người dùng đăng ký và xác thực hồ sơ mạng xã hội trước khi tham gia thử thách.

### Phạm vi
- Hỗ trợ 5 nền tảng: **TikTok, YouTube, Facebook, Instagram, Threads**
- Mỗi nền tảng có quy trình xác thực riêng

### 3.1. TikTok (OAuth 2.0)
1. Người dùng chọn TikTok → chuyển hướng OAuth 2.0.
2. Cấp quyền → Backend lấy: tên kênh, ID, avatar, số followers.
3. Kiểm tra điều kiện (≥ X followers): đạt → APPROVED; không đạt → REJECTED.

### 3.2. YouTube (URL + API)
1. Người dùng nhập URL kênh YouTube.
2. Yêu cầu thêm hashtag định danh (vd: `#TCB_xxxxx`) vào mô tả kênh.
3. Backend lấy metadata từ YouTube API: tên, ID, avatar, followers.
4. Kiểm tra điều kiện → trả kết quả **ngay lập tức**.

### 3.3. Facebook / Instagram / Threads (URL + Kiểm duyệt)
1. Người dùng nhập URL hồ sơ cá nhân.
2. Bắt buộc thêm hashtag định danh vào mô tả hồ sơ.
3. Backend lưu trạng thái PENDING.
4. Kiểm duyệt thủ công/bán tự động: crawl hồ sơ, kiểm tra hashtag + followers.
5. Kết quả cập nhật **chậm nhất 01 ngày làm việc**.

### Ràng buộc dữ liệu
| Trường | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|
| Nền tảng | Enum | Có | TIKTOK / YOUTUBE / FACEBOOK / INSTAGRAM / THREADS |
| URL hồ sơ | URL | Có (trừ TikTok) | |
| Hashtag định danh | Text | Có (trừ TikTok) | Xác minh quyền sở hữu |
| Số followers | Number | Tự động | ≥ X (cấu hình) |
| Trạng thái | Enum | Có | PENDING / APPROVED / REJECTED |

---

## 4. Tham gia thử thách

### Mục tiêu
Cho phép người dùng gửi bài dự thi (video/nội dung) cho một thử thách cụ thể.

### Điều kiện tiên quyết
- Đã đăng nhập
- Có ít nhất một hồ sơ social đã duyệt (APPROVED)
- Thử thách còn trong thời gian đăng ký

### Luồng nghiệp vụ
1. Người dùng truy cập trang chi tiết thử thách → xem mô tả, thể lệ, hashtag bắt buộc.
2. Nhấn "Tham gia thử thách" → chọn hồ sơ social đã duyệt.
3. Nhập link video tương ứng với hồ sơ đã chọn.
4. Hệ thống kiểm tra:
   - Link hợp lệ, truy cập được
   - Nền tảng video khớp với hồ sơ
   - Có chứa hashtag bắt buộc
5. Hợp lệ → lưu trạng thái PENDING → chờ kiểm duyệt.
6. Sau duyệt: APPROVED (bắt đầu tính thống kê) hoặc REJECTED (kèm lý do).

### Hỗ trợ tham gia bằng mã code
- Ngoài cách tham gia thông thường, người dùng có thể nhập **mã code** để tham gia thử thách đặc biệt (invite-only).

---

## 5. Theo dõi thử thách đã tham gia

### Mục tiêu
Cho phép người dùng xem lại toàn bộ thử thách đã tham gia, video đã gửi, trạng thái và mốc hoa hồng.

### Luồng nghiệp vụ
1. Người dùng truy cập "Thử thách của tôi".
2. Hệ thống hiển thị:
   - Danh sách thử thách đã tham gia
   - Video đã gửi + trạng thái (PENDING / APPROVED / REJECTED)
   - Thông số: lượt xem, lượt tương tác
   - Mốc hoa hồng đã đạt được

### Bảo mật
- Chỉ người dùng đăng nhập mới xem được thông tin của chính họ.

---

## 6. Xếp hạng Creator & Content (Bảng xếp hạng)

### Mục tiêu
Hiển thị bảng xếp hạng creator và content trên giao diện Influencer, tạo động lực tham gia.

### Luồng nghiệp vụ
1. Trang thử thách hiển thị **bảng xếp hạng (leaderboard)** theo thử thách.
2. Xếp hạng creator theo: số content, số chiến dịch tham gia, thông số tương tác.
3. Xếp hạng content theo: lượt xem, lượt tương tác.
4. Dữ liệu cập nhật định kỳ qua cron job.

### API đã triển khai
- `GET /events/:id/leaderboards` — Bảng xếp hạng creator theo thử thách
- `GET /events/:id/content/leaderboards` — Bảng xếp hạng content theo thử thách

---

## 7. Quản lý số dư & Dòng tiền

### Mục tiêu
Cho phép creator xem số dư hoa hồng, lịch sử giao dịch và thông tin tài chính.

### Luồng nghiệp vụ
1. Người dùng truy cập trang "Ví / Tài chính".
2. Hệ thống hiển thị:
   - Số dư hiện tại (đã đối soát, chưa thanh toán, đã thanh toán)
   - Lịch sử dòng tiền (cash flow)
   - Thông tin thẻ ngân hàng đã liên kết
3. Người dùng có thể:
   - Thêm / sửa thẻ ngân hàng
   - Đặt thẻ mặc định

### API đã triển khai
- `GET /users/cash-flow` — Lịch sử dòng tiền
- `GET /users/bank-cards` — Danh sách thẻ ngân hàng
- `POST /users/bank-cards` — Thêm thẻ ngân hàng
- `PUT /users/bank-cards/:id` — Cập nhật thẻ
- `PUT /users/bank-cards/:id/set-default` — Đặt thẻ mặc định

### Phạm vi
- Giao diện creator hỗ trợ xem số dư, lịch sử dòng tiền và quản lý thẻ ngân hàng.
- Việc tạo lệnh rút tiền và chi trả được xử lý qua luồng Admin (xem §20, §21).

---

## 8. eKYC & Ký hợp đồng điện tử

### Mục tiêu
Cho phép creator xác minh danh tính (CCCD) và ký hợp đồng điện tử để nhận hoa hồng.

### Luồng nghiệp vụ

#### 8.1. Xác minh danh tính (eKYC)
1. Người dùng truy cập trang "Hợp đồng".
2. Tải ảnh CCCD/CMND.
3. Hệ thống trích xuất thông tin từ ảnh bằng **OCR** (API nội bộ).
4. Người dùng xác nhận thông tin → gửi yêu cầu xác minh.
5. Trạng thái: PENDING → APPROVED / REJECTED.

#### 8.2. Ký hợp đồng
1. Sau khi eKYC được duyệt, người dùng cung cấp thông tin thanh toán.
2. Hệ thống tạo hợp đồng → chuyển hướng đến **trang cộng tác viên AccessTrade** (ctv.scalef.com).
3. Ký hợp đồng trên AccessTrade (cung cấp thông tin, xác thực, xem/tải hợp đồng).
4. T-Fluencers lưu mã định danh để nhận diện user tương ứng.
5. Kết quả ký được thông báo lại cho T-Fluencers.

### API đã triển khai
- `POST /users/identification` — Gửi thông tin xác minh
- `POST /users/identification/image` — Trích xuất OCR từ ảnh CCCD
- `POST /users/contract/info` — Lưu thông tin hợp đồng
- `POST /users/contract/estimate` — Ước tính hợp đồng
- `GET /users/contract/pre-signed` — Lấy link tải hợp đồng
- `GET /users/service-tos/redirect-url` — Chuyển hướng trang AccessTrade

---

## 9. Thông báo

### Mục tiêu
Hiển thị thông báo hệ thống cho người dùng: kết quả duyệt content, hoa hồng, cập nhật chiến dịch.

### Luồng nghiệp vụ
1. Hệ thống gửi thông báo qua nhiều kênh:
   - **In-app**: Danh sách thông báo trên giao diện
   - **Push notification**: Firebase Cloud Messaging (FCM)
   - **Email**: SendGrid
   - **SMS**: eSMS
2. Người dùng xem danh sách thông báo → nhấn để đánh dấu đã đọc.

### API đã triển khai
- `GET /notifications` — Danh sách thông báo
- `GET /notifications/:id` — Đánh dấu đã đọc
- `POST /users/device` — Đăng ký device token cho push notification

---

## 10. Trang giới thiệu, Thể lệ & Bài viết

### Mục tiêu
Hiển thị thông tin giới thiệu chương trình, quy tắc, hướng dẫn, thể lệ, tin tức.

### Luồng nghiệp vụ
1. Trang chủ hiển thị banner, thông tin chương trình, danh sách thử thách.
2. Người dùng xem bài viết/thể lệ → nội dung được quản lý từ Admin CMS.
3. Trang tin tức cập nhật thông tin mới nhất.

### API đã triển khai
- `GET /articles/:id` — Chi tiết bài viết
- `GET /news` — Danh sách tin tức
- `GET /quick-actions` — Danh sách hành động nhanh (hỗ trợ)

---

## 11. Thống kê cá nhân & Mã giới thiệu

### Mục tiêu
Cho phép creator xem thống kê cá nhân và quản lý mã giới thiệu.

### Luồng nghiệp vụ
1. Xem tổng quan: số content đã gửi, lượt xem, hoa hồng.
2. Xem danh sách người được giới thiệu (invitees).
3. Nhập/chia sẻ mã giới thiệu.

### API đã triển khai
- `GET /user-statistic` — Thống kê cá nhân
- `GET /user-statistic/contents` — Thống kê content
- `GET /user-statistic/invitees` — Danh sách người được giới thiệu
- `POST /users/referral` — Gửi mã giới thiệu

---

# III. Yêu cầu chức năng — Phía Admin

## 12. Đăng nhập Admin

### Mục tiêu
Cho phép quản trị viên đăng nhập vào hệ thống quản trị.

### Phương thức đăng nhập
- **Email + Mật khẩu**: Đăng nhập thông thường
- **Google OAuth**: Đăng nhập nhanh qua Google

### Luồng nghiệp vụ
1. Admin truy cập trang đăng nhập.
2. Nhập email/mật khẩu hoặc chọn "Đăng nhập bằng Google".
3. Backend xác thực → tạo JWT token.
4. Chuyển hướng đến trang quản trị.

### Tính năng bổ sung
- Quên mật khẩu → gửi email reset
- Đổi mật khẩu
- Mời nhân viên mới (invite system)
- Xác minh invite token → chấp nhận lời mời

### API đã triển khai
- `POST /staffs/login` — Đăng nhập email/password
- `POST /staffs/login-with-google` — Đăng nhập Google
- `POST /staffs/forgot-password` — Quên mật khẩu
- `POST /staffs/reset-password` — Đặt lại mật khẩu
- `POST /staffs/invite` — Mời nhân viên
- `POST /staffs/bulk-invite` — Mời hàng loạt

---

## 13. Quản lý nhân viên & Phân quyền

### Mục tiêu
Quản lý tài khoản nhân viên quản trị và phân quyền truy cập.

### Luồng nghiệp vụ
1. Admin xem danh sách nhân viên.
2. Tạo mới / cập nhật thông tin / thay đổi trạng thái (active/inactive).
3. Gán vai trò cho nhân viên.

### Hệ thống vai trò (RBAC)
| Vai trò | Mô tả |
|---|---|
| **Root** | Toàn quyền hệ thống |
| **Admin** | Quản lý chiến dịch, nội dung, người dùng, đối soát, thanh toán |
| **Campaign Owner** | Quản lý chiến dịch được giao |
| **Collaborator** | Cộng tác viên với quyền hạn giới hạn |

### API đã triển khai
- `GET /staffs` — Danh sách nhân viên
- `POST /staffs/register` — Tạo nhân viên
- `PUT /staffs/:id/update-info` — Cập nhật thông tin
- `PATCH /staffs/:id/status` — Thay đổi trạng thái
- `GET /roles` — Danh sách vai trò

---

## 14. Dashboard tổng quan

### Mục tiêu
Cung cấp cái nhìn tổng quan về hiệu quả chiến dịch cho AT và TCB.

### Luồng nghiệp vụ (Cổng quản trị - Admin)
1. Admin truy cập trang Dashboard.
2. Hệ thống hiển thị:
   - Tổng content (phân theo YouTube / TikTok)
   - Tổng lượt xem
   - Tổng tiền ở các trạng thái
   - Biểu đồ phân bố content
   - Bộ lọc theo chiến dịch, thời gian

### Luồng nghiệp vụ (Dashboard phân tích — Next.js)
1. Truy cập dashboard phân tích nâng cao.
2. Hệ thống hiển thị:
   - **6+ thẻ KPI**: Tổng video, tổng creator, tổng tương tác, ngân sách, tỷ lệ tương tác
   - **Phân tích xu hướng**: So sánh với kỳ trước
   - **3 tab**: Tổng quan / Nền tảng / Creator
   - **Bộ lọc nâng cao**: Chiến dịch, nền tảng (Facebook/YouTube/TikTok/Instagram), khoảng thời gian (7/30/90 ngày hoặc tùy chỉnh)
   - **7+ loại biểu đồ**: Bar, Line, Pie, Doughnut...
   - **Bảng xếp hạng creator**: Top influencers theo hiệu quả
   - **Phân khúc creator**: Segments theo nhóm
3. Hỗ trợ đa ngôn ngữ (Tiếng Việt / Tiếng Anh).

### API đã triển khai
- `GET /analytics/global/dashboard` — KPI tổng quan
- `GET /analytics/dashboard` — KPI chi tiết
- `GET /analytics/platforms` — Phân tích theo nền tảng
- `GET /analytics/creators` — Bảng xếp hạng creator
- `GET /analytics/creators/segments` — Phân khúc creator
- `GET /analytics/approval` — Phân tích duyệt content
- `GET /analytics/trends` — Xu hướng timeline
- `GET /analytics/creator-kpis` — KPI creator
- `GET /analytics/transfers` — Phân tích thanh toán
- `GET /analytics/performance/trends` — Xu hướng hiệu suất

---

## 15. Quản lý chiến dịch / Thử thách (Event)

### Mục tiêu
Cho phép Admin tạo, cấu hình và quản lý các chiến dịch/thử thách truyền thông.

### Luồng nghiệp vụ
1. Admin truy cập "Quản lý chiến dịch".
2. **Tạo mới** chiến dịch với thông tin:
   - Tên, mô tả, ảnh bìa
   - Thời gian bắt đầu – kết thúc
   - Loại chiến dịch (ViewBased, Other)
   - Điều kiện tham gia
   - Hashtag bắt buộc
3. **Cấu hình cơ cấu thưởng** (Event Reward):
   - Loại: BY_VIEW (theo lượt xem) / BY_TASK (theo nhiệm vụ)
   - Mốc thưởng, số tiền tương ứng
   - Quy tắc tính (RewardRule — JSON)
4. **Quản lý Event Schema**: Tạo các template cấu trúc cho chiến dịch.
5. **Quản lý Event Category**: Phân loại chiến dịch theo danh mục.
6. **Thay đổi trạng thái**: DRAFT → ACTIVE → ENDED / CANCELLED.
7. **Chặn bài đăng mới** / **Chặn tạo thưởng** khi cần.
8. **Xem thống kê** và **biểu đồ** chiến dịch.

### API đã triển khai
- `POST /events` — Tạo chiến dịch
- `GET /events` — Danh sách
- `GET /events/:id` — Chi tiết
- `PUT /events/:id` — Cập nhật
- `PATCH /events/:id/status` — Đổi trạng thái
- `GET /events/:id/statistic` — Thống kê
- `GET /events/:id/chart` — Biểu đồ
- `PATCH /events/:id/block-user-submit-content` — Chặn submit
- `PATCH /events/:id/block-create-reward` — Chặn tạo thưởng
- `GET /events/report-statistic` — Báo cáo thống kê
- CRUD cho Event Schema, Event Category, Event Bonus

---

## 16. Quản lý nội dung (Content)

### Mục tiêu
Cho phép Admin xem danh sách, duyệt, hủy, và quản lý nội dung (video) của Influencer.

### Luồng nghiệp vụ
1. Admin truy cập "Danh sách nội dung".
2. Lọc theo: trạng thái, thời gian, nền tảng, thông số.
3. Xem chi tiết: link video, thumbnail, mô tả, transcript, thông số tương tác.
4. Thao tác:
   - **Duyệt** (Approve): chuyển APPROVED
   - **Hủy** (Reject): nhập lý do bắt buộc → REJECTED
   - **Duyệt/Hủy hàng loạt** (batch)
   - **Ghim** (pin) nội dung nổi bật
5. Xem biểu đồ thống kê nội dung.
6. Ghi log hành động.

### Tính năng bổ sung
- **Import nội dung**: Upload Excel để import content hàng loạt
- **Theo dõi tiến độ import**: Xem trạng thái batch import
- **Crawl thông tin content**: Thu thập metadata từ nền tảng
- **Gắn cờ cảnh báo**: Tự động gắn warning tag cho content vi phạm
- **Transcript management**: Xem và quản lý bản ghi âm (transcript) của video

### API đã triển khai
- `GET /contents` — Danh sách
- `GET /contents/:id` — Chi tiết
- `PATCH /contents/:id/status` — Duyệt/Hủy
- `PATCH /contents/batch-status` — Duyệt/Hủy hàng loạt
- `POST /contents/import` — Import content
- `POST /contents/:id/crawl-info` — Crawl thông tin
- `PATCH /contents/:id/pin` — Ghim content
- `GET /contents/statistic-chart` — Biểu đồ thống kê

---

## 17. Duyệt / Hủy hồ sơ social

### Mục tiêu
Cho phép Admin duyệt hoặc từ chối hồ sơ mạng xã hội của Influencer.

### Luồng nghiệp vụ
1. Admin truy cập "Quản lý hồ sơ social" (trong trang User detail).
2. Xem danh sách hồ sơ: nền tảng, tên, URL, hashtag, followers, trạng thái.
3. Lọc theo: nền tảng, trạng thái, thời gian, người dùng.
4. Thao tác:
   - **Duyệt** (Approve)
   - **Từ chối** (Reject) — nhập lý do bắt buộc
   - **Hủy duyệt** (Revoke) — khi phát hiện vi phạm
5. Gửi thông báo kết quả cho người dùng.
6. Ghi log toàn bộ thao tác.

### API đã triển khai
- `GET /users/:id/socials` — Danh sách hồ sơ social của user
- `POST /users/create-user-social` — Tạo hồ sơ social (admin nhập liệu)

---

## 18. Quản lý người dùng & Creator

### Mục tiêu
Cho phép Admin xem, tìm kiếm, quản lý thông tin người dùng và Influencer.

### Luồng nghiệp vụ

#### 18.1. Quản lý người dùng (User)
1. Admin xem danh sách người dùng: tên, email, trạng thái, ngày tạo.
2. Xem chi tiết: thông tin cá nhân, hồ sơ social, thông tin thanh toán, lịch sử tham gia.
3. Thao tác: **Khóa (ban)** / **Mở khóa (unban)** tài khoản.
4. Tạo user mới từ admin.

#### 18.2. Quản lý Influencer
1. Admin xem danh sách influencer: tên, nền tảng, số followers, trạng thái.
2. Xem chi tiết: hồ sơ enriched từ AT-Core, thông số tương tác, nhân khẩu học.
3. Thay đổi trạng thái influencer.
4. Cập nhật thống kê thủ công.
5. Cấu hình điều kiện tham gia (Conditions).

#### 18.3. Quản lý Influencer Profile
1. Xem profile chi tiết: dữ liệu enrichment từ AT-Core (followers, engagement, content count).
2. Duyệt hồ sơ phân loại.

### API đã triển khai
- `GET /users` — Danh sách user
- `POST /users` — Tạo user
- `GET /users/:id` — Chi tiết
- `PATCH /users/:id/ban` / `un-ban` — Khóa/Mở khóa
- `GET /influencers` — Danh sách influencer
- `PATCH /influencers/:id/change-status` — Đổi trạng thái
- `PUT /influencers/:id/update-stats` — Cập nhật thống kê
- `GET /profiles` — Danh sách profile
- `GET /profiles/:id` — Chi tiết profile

---

## 19. Xác minh danh tính (eKYC — phía Admin)

### Mục tiêu
Cho phép Admin duyệt / từ chối yêu cầu xác minh danh tính của người dùng.

### Luồng nghiệp vụ
1. Admin xem danh sách yêu cầu xác minh.
2. Xem chi tiết: ảnh CCCD, thông tin trích xuất.
3. Duyệt / Từ chối kèm lý do.
4. Từ chối hợp đồng nếu cần.

### API đã triển khai
- `GET /identifications` — Danh sách
- `GET /identifications/:id` — Chi tiết
- `PATCH /identifications/:id/status` — Duyệt/Từ chối
- `PATCH /users/:id/reject-contract` — Từ chối hợp đồng

---

## 20. Đối soát hoa hồng

### Mục tiêu
Cho phép Admin thực hiện đối soát hoa hồng cho Influencer theo chiến dịch.

### Luồng nghiệp vụ
1. Admin truy cập "Đối soát hoa hồng".
2. Xem danh sách đợt đối soát / tạo mới.
3. Khi tạo mới: chọn thử thách, loại hoa hồng, thời gian.
4. Hệ thống tổng hợp: tổng user, tổng video, tổng tiền.
5. Admin xem chi tiết:
   - **Tab nội dung**: Danh sách content cần đối soát
   - **Tab mốc thưởng**: Milestone tracking
   - **Tab thưởng bổ sung**: Event bonus
   - **Tab tổng quan**: Overview
6. Hệ thống đánh giá tự động bằng **checklist**:
   - Phân loại content (classification)
   - Quick approve / Quick reject
   - Override phân loại nếu cần
   - Reset checklist
7. **Xuất Excel** để kiểm tra thủ công.
8. Xác nhận / Hủy từng khoản.
9. **Kết thúc đợt**: khóa, tự động cập nhật số dư người dùng.

### Cấu trúc Excel xuất
- **BY_VIEW**: ID user, tên, ID video, link, view đầu kỳ/trong kỳ/cuối kỳ, mốc, số tiền, trạng thái, ghi chú
- **BY_TASK**: ID user, tên, số tiền, trạng thái, ghi chú

### API đã triển khai
- `GET /reconciliations` — Danh sách
- `POST /reconciliations` — Tạo mới
- `GET /reconciliations/:id` — Chi tiết
- `GET /reconciliations/:id/content` — Content items
- `GET /reconciliations/:id/milestone` — Milestone items
- `GET /reconciliations/:id/bonus` — Bonus items
- `PATCH /reconciliations/:id/change-status` — Đổi trạng thái
- `POST /reconciliations/:id/evaluate` — Đánh giá checklist
- `POST /reconciliations/:id/apply-classification` — Phân loại
- `POST /reconciliations/:id/content/:itemId/quick-approve` — Duyệt nhanh
- `POST /reconciliations/:id/content/:itemId/quick-reject` — Từ chối nhanh
- `PATCH /reconciliations/events/:eventId/close` — Kết thúc đợt

---

## 21. Thanh toán cho người dùng (Transfer)

### Mục tiêu
Cho phép Admin tạo và quản lý đợt thanh toán cho Influencer.

### Luồng nghiệp vụ
1. Admin truy cập "Thanh toán".
2. Xem danh sách đợt thanh toán / tạo mới.
3. Hệ thống tổng hợp: người dùng có hoa hồng chưa thanh toán (đã đối soát).
4. Admin xem chi tiết / **xuất Excel**.
5. Xác nhận / Hủy thanh toán (kèm lý do).
6. Kết thúc đợt: khóa, cập nhật số dư, ghi log giao dịch.

### Tích hợp
- Tích hợp với **Service TOS** (AccessTrade) để đẩy lệnh rút tiền.
- Retry tự động khi push thất bại (cron mỗi 30 phút).

### API đã triển khai
- `GET /transfers` — Danh sách
- `POST /transfers` — Tạo đợt
- `GET /transfers/:id` — Chi tiết
- `PUT /transfers/:id` — Cập nhật
- `PUT /transfers/:id/change-status` — Đổi trạng thái
- `PATCH /transfers/:id/change-declined` — Đánh dấu từ chối
- `GET /transfers/:id/withdraw-cashes` — Danh sách giao dịch rút tiền

---

## 22. Quản lý ngân sách chiến dịch (Budget)

### Mục tiêu
Cho phép Admin cấu hình và theo dõi ngân sách chiến dịch.

### Luồng nghiệp vụ
1. Admin tạo ngân sách cho chiến dịch: số tiền giới hạn (budget cap).
2. Hệ thống tự động giám sát (cron mỗi 30 phút):
   - Tính tổng hoa hồng phát sinh + dự kiến
   - **75%** → Cảnh báo (warning)
   - **95%** → Chặn bài đăng mới
   - **100%** → Ngừng tính hoa hồng (không lưu hoa hồng dự kiến)
3. Gửi cảnh báo qua email (Admin) và giao diện/email (Influencer).

### API đã triển khai
- `POST /budget-campaigns` — Tạo ngân sách
- `GET /budget-campaigns` — Danh sách
- `GET /budget-campaigns/:id` — Chi tiết
- `PUT /budget-campaigns/:id` — Cập nhật
- `PATCH /budget-campaigns/:id/status` — Đổi trạng thái

---

## 23. Quản lý file dữ liệu & Xuất dữ liệu

### Mục tiêu
Cho phép Admin tải xuống file dữ liệu (đối soát, thanh toán, analytics) dạng Excel.

### Luồng nghiệp vụ
1. Admin thao tác "Xuất dữ liệu".
2. Hệ thống tạo request với trạng thái "Đang tạo".
3. Background job: truy vấn → tạo Excel → lưu MinIO → cập nhật "Thành công".
4. Admin tải file qua **link bảo mật** (presigned URL, hiệu lực 30 giây).
5. Ghi log: user, thời điểm, IP.

### API đã triển khai
- `POST /data-exports` — Tạo yêu cầu xuất
- `GET /data-exports` — Danh sách
- `GET /data-exports/:id/pre-sign` — Lấy link tải

---

## 24. Quản lý bài viết, tin tức & nội dung CMS

### Mục tiêu
Cho phép Admin soạn thảo hướng dẫn, thể lệ, bài viết, tin tức hiển thị trên Cổng Influencer.

### Luồng nghiệp vụ
1. Admin tạo/sửa bài viết (Article): rich text editor (Braft Editor).
2. Quản lý tin tức (News): tạo, sửa, đổi trạng thái, clone.
3. Quản lý tag: phân loại nội dung.
4. Quản lý Quick Action: các liên kết hành động nhanh (hỗ trợ, hướng dẫn).

### API đã triển khai
- CRUD cho Articles, News, Tags, Quick Actions

---

## 25. Quản lý thông báo (Admin → Influencer)

### Mục tiêu
Cho phép Admin tạo và gửi thông báo đến Influencer.

### Luồng nghiệp vụ
1. Admin tạo thông báo: tiêu đề, nội dung, đối tượng nhận.
2. Gửi qua: in-app, push notification (FCM), email (SendGrid).
3. Theo dõi trạng thái: Hoàn thành / Từ chối.
4. Clone thông báo để tái sử dụng.

### API đã triển khai
- `POST /admin-notifications` — Tạo thông báo
- `GET /admin-notifications` — Danh sách
- `PUT /admin-notifications/:id` — Cập nhật
- `POST /admin-notifications/:id/clone` — Clone
- `PATCH /admin-notifications/:id/completed` / `rejected` — Đổi trạng thái

---

## 26. Phân khúc người dùng (Segments)

### Mục tiêu
Cho phép Admin phân nhóm creator để phục vụ lọc, gửi thông báo, quản lý chiến dịch.

### Luồng nghiệp vụ
1. Tạo segment (nhóm).
2. Thêm/Xóa user vào segment.
3. Import danh sách từ Excel.

### API đã triển khai
- CRUD cho Segments
- `POST /user-segments/import-excel` — Import từ Excel

---

## 27. Đối tác & Chiến dịch matching (Campaign)

### Mục tiêu
Quản lý đối tác (partner) và matching influencer vào chiến dịch.

### Luồng nghiệp vụ
1. Quản lý danh sách đối tác (Partner): CRUD.
2. Tạo chiến dịch (Campaign) cho đối tác.
3. **Chạy thuật toán matching**: tìm influencer phù hợp cho chiến dịch.
4. Thêm/Xóa influencer khỏi chiến dịch.
5. Xem lịch sử matching.

### API đã triển khai
- CRUD cho Partners, Campaigns
- `POST /campaigns/:id/matching/run` — Chạy matching
- `POST /campaigns/:id/influencers` — Thêm influencer

---

## 28. Đánh giá & Xếp hạng Influencer (Review/Rating)

### Mục tiêu
Cho phép Admin và Brand đánh giá influencer sau chiến dịch.

### Luồng nghiệp vụ
1. Admin hoặc Brand gửi review cho profile influencer.
2. Đánh giá theo tiêu chí, cho điểm.
3. Xem thống kê rating tổng hợp.

### API đã triển khai
- `POST /profiles/:profile_id/reviews` — Gửi review
- `GET /profiles/:profile_id/reviews` — Danh sách review
- `GET /profiles/:profile_id/ratings/stats` — Thống kê rating

---

## 29. Import dữ liệu hiệu suất (Performance)

### Mục tiêu
Cho phép Admin import dữ liệu hiệu suất từ file CSV và xem biểu đồ xu hướng trên dashboard phân tích.

### Luồng nghiệp vụ
1. Admin upload file CSV chứa dữ liệu hiệu suất trên **Dashboard phân tích (Next.js)**.
2. Hệ thống xử lý batch import.
3. Xem danh sách dữ liệu đã import, quản lý batch.
4. Xem xu hướng hiệu suất trên biểu đồ dashboard.

### API đã triển khai
- `POST /performance/import` — Import CSV
- `GET /performance/list` — Danh sách
- `GET /performance/batches` — Danh sách batch
- `GET /analytics/performance/trends` — Xu hướng

---

## 30. Quản lý mã (Code Management)

### Mục tiêu
Cho phép Admin tạo và quản lý mã tham gia thử thách (promo code).

### API đã triển khai
- `POST /manage-codes` — Tạo mã
- `GET /manage-codes` — Danh sách
- `POST /manage-codes/import-excel` — Import từ Excel
- `DELETE /manage-codes/:id` — Xóa mã

---

## 31. Nhật ký kiểm toán (Audit Log)

### Mục tiêu
Ghi nhận toàn bộ hành động của Admin và User trong hệ thống.

### Luồng nghiệp vụ
1. Mọi thao tác quan trọng được ghi log: người thao tác, thời gian, hành động, đối tượng.
2. Admin xem lịch sử audit.
3. Ghi nhận đăng nhập (audit login).

### API đã triển khai
- `GET /audits` — Danh sách audit log

---

# IV. Hệ thống nền & Tác vụ tự động

## 32. Cập nhật thông số video định kỳ

### Mục tiêu
Tự động thu thập và cập nhật lượt xem, tương tác cho video đã gửi.

### Cơ chế
- **Cron job** crawl thông số video từ các nền tảng:
  - Crawl YouTube: `crawl-content-youtube`
  - Crawl TikTok: `crawl-content-tiktok` + `crawl-content-tiktok-self`
  - Crawl Facebook: `crawl-content-facebook`
- Gọi **Social Profile Service** (AT-Core) để lấy metadata.
- Lưu kết quả vào `content-analytic-daily`.
- Cập nhật báo cáo: daily, weekly, monthly.
- Ghi log mỗi lượt crawl vào `content-crawl-histories`.

### Cron đã triển khai
- Xóa lịch sử crawl cũ: mỗi 2 ngày
- Kiểm tra lại analytics: mỗi 4 giờ
- Audit content analytic: hàng ngày 04:00

---

## 33. Tính hoa hồng định kỳ

### Mục tiêu
Tự động tính toán hoa hồng dựa trên hiệu suất video và cơ cấu thưởng.

### Cơ chế
1. Backend lấy danh sách thử thách có cơ cấu hoa hồng (CampaignReward).
2. Lấy video hợp lệ (APPROVED) thuộc các thử thách đó.
3. So khớp video với reward structure → tính hoa hồng.
4. Kiểm tra ngân sách trước khi lưu (xem mục 22).
5. Nếu vượt 100% budget → không lưu hoa hồng.
6. Ghi log kết quả.

### Cron đã triển khai
- Cập nhật event analytics daily: qua API trigger
- Rerun reward theo cấu hình

---

## 34. Giám sát ngân sách tự động

### Cơ chế
- **Cron mỗi 30 phút**: kiểm tra ngưỡng budget cho mỗi chiến dịch.
- Gửi cảnh báo email (SendGrid) khi vượt mốc 75%, 95%, 100%.
- Tự động chặn submit content khi vượt 95%.
- Tự động ngừng tính hoa hồng khi vượt 100%.

---

## 35. Xử lý nội dung tự động

### Cơ chế
- **Auto reject content**: Tự động từ chối content không hợp lệ (hàng ngày 03:45)
- **Auto reject content not found**: Từ chối content không tìm thấy trên nền tảng (hàng ngày 04:30)
- **Warning tag**: Tự động gắn cờ cảnh báo cho content vi phạm (hàng ngày 05:30)
- **Content callback queue**: Xử lý callback từ nền tảng qua Asynq queue

---

## 36. Hàng đợi xử lý bất đồng bộ (Asynq)

### Tác vụ đã triển khai
1. **action_after_admin_change_status_content** — Xử lý hậu cần khi admin đổi trạng thái content
2. **action_submit_content** — Xử lý khi content được submit

### Cấu hình
- Priority queues: Critical (10), Default (3), Schedule (3)
- Max retry: 5-10 lần
- Task timeout: 30 phút
- Task retention: 24 giờ

---

## 37. Retry thanh toán & Kiểm tra trạng thái

### Cơ chế
- **Retry push withdraws to TOS**: Mỗi 30 phút, retry đẩy lệnh rút tiền sang AccessTrade TOS
- **Check campaign invoice status**: Mỗi 15 phút (prod), kiểm tra trạng thái hóa đơn chiến dịch
- **Check user social status**: Mỗi giờ, kiểm tra trạng thái hồ sơ social
- **Check Facebook status**: Hàng ngày 01:00, kiểm tra trạng thái Facebook

---

## 38. Đánh giá nội dung bằng AI (Vertex AI)

### Mục tiêu
Sử dụng AI để đánh giá chất lượng nội dung video dựa trên transcript.

### Cơ chế
1. Video được trích xuất transcript (qua webhook transcript).
2. Hệ thống gọi **Google Vertex AI (Gemini API)** để đánh giá transcript.
3. Đối chiếu nội dung với tiêu chí chiến dịch.
4. Kết quả: điểm số, độ phù hợp, vấn đề phát hiện, khuyến nghị.
5. Kết quả AI được lưu phục vụ đối soát (reconciliation checklist).

### Phạm vi
- Tính năng hiện tại hỗ trợ đánh giá chất lượng nội dung phục vụ quy trình đối soát. Kết quả AI là dữ liệu tham chiếu cho admin, không tự động phê duyệt.

---

## 39. Webhook & Tích hợp bên ngoài

### Webhook đã triển khai
| Webhook | Mô tả |
|---|---|
| `POST /content-callback` | Callback khi content được cập nhật từ nền tảng |
| `POST /content-callback/tos` | Callback từ AccessTrade TOS |
| `POST /content-callback/transcript` | Callback khi transcript sẵn sàng |
| `POST /social-profiles/webhook` | Cập nhật hồ sơ social |
| `POST /influencer-profiles/webhook/enrichment` | Enrichment profile từ AT-Core |
| `POST /transcripts/webhook` | Callback transcript |

### Tích hợp bên ngoài
| Dịch vụ | Mục đích |
|---|---|
| **AT-Core** (influence-meter) | Enrichment profile, thông số kênh, nhân khẩu học |
| **Service TOS** (AccessTrade) | eKYC, ký hợp đồng, rút tiền |
| **Google Vertex AI** | Đánh giá nội dung AI |
| **SendGrid** | Gửi email thông báo, cảnh báo |
| **eSMS** | Gửi SMS/OTP |
| **Firebase (FCM)** | Push notification mobile |
| **Telegram** | Alert cho admin |
| **MinIO** | Lưu trữ file (avatar, CCCD, export) |
| **Google Drive** | Lưu trữ hợp đồng |
| **Elasticsearch** | APM monitoring |

---

# V. Mô hình dữ liệu

## Entities chính (84+ collections MongoDB)

### Nhóm người dùng
| Entity | Mô tả |
|---|---|
| `users` | Tài khoản người dùng (influencer) |
| `staffs` | Tài khoản quản trị viên |
| `roles` | Vai trò và phân quyền |
| `sessions` | Phiên đăng nhập |
| `identifications` | Thông tin xác minh danh tính (eKYC) |
| `user-contracts` | Hợp đồng điện tử |
| `user-publishers` | Thông tin publisher |
| `user-bank-cards` | Thẻ ngân hàng |
| `user-devices` | Thiết bị (FCM token) |
| `user-socials` | Hồ sơ mạng xã hội |
| `user-partners` | Quan hệ với đối tác |
| `user-segments` | Phân khúc người dùng |
| `otp-codes` | Mã OTP |

### Nhóm chiến dịch
| Entity | Mô tả |
|---|---|
| `events` | Chiến dịch / Thử thách |
| `event-schemas` | Template cấu trúc |
| `event-rewards` | Cơ cấu thưởng |
| `event-categories` | Danh mục chiến dịch |
| `event-bonuses` | Thưởng bổ sung |
| `event-analytic-daily` | Analytics hàng ngày |
| `event-tracking-thresholds` | Ngưỡng theo dõi |

### Nhóm nội dung
| Entity | Mô tả |
|---|---|
| `contents` | Bài tham gia (video/link) |
| `content-transcripts` | Bản ghi âm video |
| `content-analytic-daily` | Analytics content hàng ngày |
| `content-crawl-histories` | Lịch sử crawl |
| `content-callbacks` | Webhook callback |
| `content-manual-follows` | Theo dõi thủ công |
| `videos` | Tài nguyên video |

### Nhóm tài chính
| Entity | Mô tả |
|---|---|
| `reconciliation` | Đợt đối soát |
| `reconciliation-items` | Dòng đối soát |
| `reconciliation-histories` | Lịch sử đối soát |
| `reconciliation-snapshots` | Snapshot kiểm toán |
| `reconciliation-checklist-results` | Kết quả checklist |
| `transfers` | Đợt thanh toán |
| `cash-flows` | Dòng tiền |
| `budget-campaigns` | Ngân sách chiến dịch |
| `user-income-month` | Thu nhập hàng tháng |

### Nhóm hỗ trợ
| Entity | Mô tả |
|---|---|
| `notifications` | Thông báo người dùng |
| `admin-notifications` | Thông báo admin |
| `articles` | Bài viết/Thể lệ |
| `news` | Tin tức |
| `tags` | Nhãn phân loại |
| `segments` | Phân khúc |
| `quick-actions` | Hành động nhanh |
| `partners` | Đối tác |
| `campaigns` | Chiến dịch matching |
| `manage-codes` | Mã tham gia |
| `referrals` | Giới thiệu |
| `configurations` | Cấu hình hệ thống |
| `data-exports` | Yêu cầu xuất dữ liệu |
| `audit-logins` | Log đăng nhập |
| `influencer-profiles` | Profile enriched |
| `profile-reviews` | Đánh giá profile |
| `performance-data` | Dữ liệu hiệu suất |

---

# VI. Bảo mật, hạ tầng & thiết kế

## 1. Phân loại dữ liệu

| Mức | Ví dụ | Biện pháp |
|---|---|---|
| **Public** | Banner, tin tức, marketing | WAF, CDN, kiểm soát chỉnh sửa |
| **Internal** | Cấu hình, rule hoa hồng | Giới hạn truy cập nội bộ, log thay đổi |
| **Confidential** | Họ tên, email, phone, hoa hồng | RBAC, audit log, DSAR 30 ngày |
| **Restricted** | CCCD, hợp đồng, số tài khoản | Mã hóa at-rest + in-transit, hạn chế truy cập |

## 2. Mã hóa & Bảo mật
- **Truyền tải**: TLS 1.2+
- **Lưu trữ**: AES-256 cho cột PII nhạy cảm
- **Token/Secret**: JWT với expiry, không lưu OAuth access_token
- **Mật khẩu**: Hash (bcrypt/argon2)
- **File**: MinIO private bucket, presigned URL TTL 30 giây

## 3. Phân quyền
- **RBAC**: Root / Admin / Campaign Owner / Collaborator
- **Middleware**: JWT authentication trên mọi API
- **Audit**: Ghi log toàn bộ thao tác quan trọng

## 4. Hạ tầng đã triển khai
| Thành phần | Công nghệ |
|---|---|
| Database | MongoDB |
| Cache & Queue broker | Redis |
| File storage | MinIO (S3-compatible) |
| Queue system | Asynq + Asynqmon dashboard |
| Email | SendGrid |
| SMS | eSMS |
| Push notification | Firebase Cloud Messaging |
| Monitoring | Elasticsearch APM |
| Alert | Telegram bot |
| Container | Docker (Alpine) |
| PDF generation | wkhtmltopdf |
| Video processing | FFmpeg |

## 5. Yêu cầu thiết kế (UI/UX)
- Tuân thủ branding Techcombank (bảng màu, font, logo)
- Responsive: ≥375px (mobile) + 1024/1440px (desktop)
- WCAG 2.1 AA (≥4.5:1 contrast)
- Dashboard phân tích hỗ trợ đa ngôn ngữ (vi/en)

---

*Tài liệu đặc tả yêu cầu phần mềm v2.0*
*Ngày: 11/03/2026*
