# TÀI LIỆU ĐẶC TẢ YÊU CẦU PHẦN MỀM

### Dự án: **Techcombank Influencer Platform (T-Fluencers)**

**Phiên bản:** 2.2

**Ngày phát hành:** 23/04/2026

---

## Lịch sử thay đổi

| Phiên bản | Ngày | Người thay đổi | Mô tả |
|---|---|---|---|
| 1.0 | — | AT Dev Team | Bản SRS gốc |
| 2.0 | 11/03/2026 | AT Dev Team | Cập nhật toàn bộ theo phạm vi đã triển khai |
| 2.1 | 12/03/2026 | AT Dev Team | Bổ sung Acceptance Criteria, NFR, State Diagram, Business Rules. Bỏ đăng nhập Facebook (Creator) và đăng nhập Google (Admin) |
| 2.2 | 23/04/2026 | AT Dev Team | Bổ sung mô tả **Snapshot đối soát (Reconciliation Snapshot)** — cơ chế tạo, dữ liệu ghi nhận và cách sử dụng trong quy trình đối soát |

## Bảng thuật ngữ

| Thuật ngữ | Định nghĩa |
|---|---|
| **Creator / Influencer** | Người dùng cuối — nhà sáng tạo nội dung tham gia chiến dịch |
| **Thử thách (Event)** | Một chiến dịch truyền thông mà Creator tham gia, đăng nội dung và nhận hoa hồng |
| **Content** | Bài tham gia của Creator (thường là video trên MXH) cho một thử thách |
| **Đối soát (Reconciliation)** | Quy trình kiểm tra, xác nhận hoa hồng phát sinh cho Creator |
| **Snapshot đối soát (Reconciliation Snapshot)** | Ảnh chụp số liệu hiệu suất content (view, like, comment, share) tại thời điểm cụ thể, dùng làm bằng chứng ghi nhận không thay đổi trong quá trình đối soát |
| **Thanh toán (Transfer)** | Đợt chi trả hoa hồng đã đối soát cho Creator |
| **Hồ sơ social (User Social)** | Tài khoản MXH đã đăng ký và xác thực trên hệ thống |
| **eKYC** | Xác minh danh tính điện tử bằng CCCD/CMND |
| **AT-Core** | Dịch vụ trung gian của AccessTrade, cung cấp dữ liệu enrichment cho influencer profile |
| **Service TOS** | Hệ thống cộng tác viên AccessTrade, xử lý ký hợp đồng và rút tiền |
| **Budget Cap** | Ngưỡng ngân sách tối đa cho một chiến dịch |
| **Mốc thưởng (Milestone)** | Ngưỡng hiệu suất (vd: 10.000 views) để Creator nhận hoa hồng tương ứng |
| **Segment** | Nhóm phân khúc Creator phục vụ lọc, gửi thông báo, quản lý chiến dịch |
| **RBAC** | Role-Based Access Control — phân quyền dựa trên vai trò |

## Giả định & Ràng buộc

### Giả định
1. Creator có thiết bị kết nối Internet và trình duyệt web hiện đại (Chrome, Safari, Firefox phiên bản gần nhất).
2. Creator đã có tài khoản MXH hợp lệ trước khi đăng ký hệ thống.
3. API của các nền tảng MXH (TikTok, YouTube, Instagram, Facebook, Threads) khả dụng và ổn định.
4. Dịch vụ AT-Core và Service TOS hoạt động liên tục; nếu gián đoạn, hệ thống sẽ retry theo cơ chế đã thiết kế.
5. Đội vận hành AT duyệt hồ sơ social và content trong vòng 1 ngày làm việc.

### Ràng buộc
1. Hệ thống chỉ hỗ trợ tiếng Việt trên Cổng Influencer và Cổng quản trị; Dashboard phân tích hỗ trợ thêm tiếng Anh.
2. Thanh toán hoa hồng phải qua Service TOS (AccessTrade), không chi trả trực tiếp.
3. Dữ liệu cá nhân tuân thủ Nghị định 13/2023/NĐ-CP (Việt Nam) về bảo vệ dữ liệu cá nhân.
4. Hệ thống triển khai trên hạ tầng do AT quản lý (Docker, MongoDB, Redis, MinIO).

## Phụ thuộc bên ngoài

| Dịch vụ | Mục đích | Ảnh hưởng khi không khả dụng |
|---|---|---|
| **TikTok OAuth API** | Đăng nhập + đăng ký kênh TikTok | Creator không đăng nhập/đăng ký kênh TikTok được |
| **Google OAuth API** | Đăng nhập Google | Creator không đăng nhập Google được |
| **YouTube Data API** | Xác thực kênh YouTube | Không xác thực kênh YouTube được |
| **AT-Core (influence-meter)** | Enrichment profile, thông số kênh | Dữ liệu influencer profile không cập nhật; hệ thống vẫn hoạt động với dữ liệu cache |
| **Service TOS (AccessTrade)** | eKYC, ký hợp đồng, rút tiền | Creator không ký hợp đồng và không nhận được tiền; retry tự động mỗi 30 phút |
| **Google Vertex AI** | Đánh giá nội dung AI | Admin đối soát thủ công thay vì có hỗ trợ AI; không ảnh hưởng chức năng chính |
| **SendGrid** | Gửi email | Thông báo email không gửi được; thông báo in-app vẫn hoạt động |
| **eSMS** | Gửi SMS/OTP | SMS không gửi được |
| **Firebase (FCM)** | Push notification | Push notification không gửi được; thông báo in-app vẫn hoạt động |

---

# MỤC LỤC

- [I. Giới thiệu](#i-giới-thiệu)
- [II. Yêu cầu chức năng — Phía Creator (Influencer)](#ii-yêu-cầu-chức-năng--phía-creator-influencer)
- [III. Yêu cầu chức năng — Phía Admin](#iii-yêu-cầu-chức-năng--phía-admin)
- [IV. Hệ thống nền & Tác vụ tự động](#iv-hệ-thống-nền--tác-vụ-tự-động)
- [V. Mô hình dữ liệu](#v-mô-hình-dữ-liệu)
- [VI. Bảo mật, hạ tầng & thiết kế](#vi-bảo-mật-hạ-tầng--thiết-kế)
- [VII. Yêu cầu phi chức năng (NFR)](#vii-yêu-cầu-phi-chức-năng-nfr)
- [VIII. Vòng đời trạng thái (State Diagrams)](#viii-vòng-đời-trạng-thái-state-diagrams)
- [IX. Quy tắc nghiệp vụ (Business Rules)](#ix-quy-tắc-nghiệp-vụ-business-rules)
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

## 1. Đăng nhập bằng Google / TikTok

### Mục tiêu
Cho phép người dùng đăng nhập bằng tài khoản mạng xã hội, không cần tạo tài khoản thủ công.

### Phạm vi
- Nền tảng: Cổng Influencer (web)
- Hỗ trợ: Google, TikTok

### Luồng nghiệp vụ
1. Người dùng chọn phương thức đăng nhập (Google / TikTok).
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
| `provider` | Hệ thống | DB | google / tiktok |
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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-1.1 | Đăng nhập Google thành công | Chọn Google → hoàn tất OAuth → redirect về trang chủ với trạng thái đã đăng nhập, hiển thị tên + avatar |
| AC-1.2 | Đăng nhập TikTok thành công | Chọn TikTok → hoàn tất OAuth → redirect về trang chủ với trạng thái đã đăng nhập |
| AC-1.3 | Tạo tài khoản mới tự động | Người dùng chưa tồn tại → hệ thống tạo tài khoản mới, lưu provider_user_id, email, display_name, avatar_url |
| AC-1.4 | Đăng nhập lại tài khoản đã tồn tại | Người dùng đã có tài khoản → đăng nhập trực tiếp, không tạo trùng |
| AC-1.5 | Từ chối cấp quyền | Người dùng từ chối trên trang OAuth → hiển thị thông báo lỗi, không tạo tài khoản |
| AC-1.6 | Access token không lưu | Sau đăng nhập thành công, access_token OAuth không tồn tại trong DB |
| AC-1.7 | JWT token hợp lệ | Response trả về JWT token, sử dụng được cho các API tiếp theo |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-2.1 | Hiển thị thông tin hiện tại | Truy cập trang → hiển thị đầy đủ: avatar, tên, giới tính, ngày sinh, email |
| AC-2.2 | Cập nhật tên hiển thị | Sửa tên → Lưu → tên mới hiển thị trên header và trang cá nhân |
| AC-2.3 | Upload avatar hợp lệ | Upload ảnh JPG/PNG ≤ 5MB → avatar cập nhật thành công |
| AC-2.4 | Từ chối avatar không hợp lệ | Upload file > 5MB hoặc không phải JPG/PNG → hiển thị lỗi, không lưu |
| AC-2.5 | Validate email | Nhập email sai định dạng → hiển thị lỗi validation, không lưu |
| AC-2.6 | Tên không được trống | Xóa trắng tên → nhấn Lưu → hiển thị lỗi "Tên không được để trống" |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-3.1 | Đăng ký TikTok qua OAuth | Chọn TikTok → OAuth thành công → hệ thống lấy tên, ID, avatar, followers → trả kết quả ngay (APPROVED nếu ≥ X followers, REJECTED nếu không đạt) |
| AC-3.2 | Đăng ký YouTube qua URL | Nhập URL kênh hợp lệ + thêm hashtag định danh → hệ thống verify qua YouTube API → trả kết quả ngay |
| AC-3.3 | Đăng ký Facebook/Instagram/Threads | Nhập URL + thêm hashtag → trạng thái PENDING → kết quả trả về trong 1 ngày làm việc |
| AC-3.4 | Hashtag định danh | Hệ thống sinh hashtag duy nhất cho mỗi user (vd: #TCB_xxxxx), user phải thêm vào mô tả kênh/profile |
| AC-3.5 | Từ chối URL không hợp lệ | Nhập URL sai định dạng hoặc không truy cập được → hiển thị lỗi |
| AC-3.6 | Không đăng ký trùng | User đã có hồ sơ APPROVED cho cùng nền tảng → không cho đăng ký lại |
| AC-3.7 | Kiểm tra điều kiện followers | Số followers < ngưỡng cấu hình → REJECTED kèm lý do |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-4.1 | Tham gia thành công | Chọn hồ sơ social đã duyệt + nhập link video hợp lệ + có hashtag bắt buộc → trạng thái PENDING |
| AC-4.2 | Chặn khi chưa có hồ sơ social | User không có hồ sơ APPROVED → nút "Tham gia" bị disable hoặc hiển thị yêu cầu đăng ký kênh |
| AC-4.3 | Chặn khi hết hạn thử thách | Thử thách đã kết thúc → không cho submit content mới |
| AC-4.4 | Validate link video | Link không truy cập được / nền tảng không khớp hồ sơ / thiếu hashtag → hiển thị lỗi cụ thể |
| AC-4.5 | Tham gia bằng mã code | Nhập mã hợp lệ → cho phép tham gia thử thách invite-only. Mã sai → hiển thị lỗi |
| AC-4.6 | Không submit trùng | User đã submit cùng link video cho cùng thử thách → từ chối, thông báo trùng |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-5.1 | Hiển thị danh sách thử thách | Trang "Thử thách của tôi" hiển thị tất cả thử thách đã tham gia, sắp xếp theo thời gian mới nhất |
| AC-5.2 | Hiển thị trạng thái video | Mỗi video hiển thị rõ trạng thái: PENDING / APPROVED / REJECTED |
| AC-5.3 | Hiển thị thông số | Video APPROVED hiển thị lượt xem, lượt tương tác, cập nhật theo kỳ crawl |
| AC-5.4 | Hiển thị mốc hoa hồng | Các mốc thưởng đã đạt hiển thị kèm số tiền |
| AC-5.5 | Phân quyền xem | User A không xem được thông tin thử thách của User B |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-6.1 | Hiển thị bảng xếp hạng creator | Trang thử thách hiển thị leaderboard creator: tên, avatar, số content, thông số tương tác |
| AC-6.2 | Hiển thị bảng xếp hạng content | Leaderboard content hiển thị: thumbnail, lượt xem, lượt tương tác, xếp theo thứ tự giảm dần |
| AC-6.3 | Dữ liệu cập nhật định kỳ | Dữ liệu leaderboard phản ánh đúng sau mỗi lần cron job chạy |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-7.1 | Hiển thị số dư | Trang "Ví" hiển thị 3 loại số dư: đã đối soát, chưa thanh toán, đã thanh toán — số liệu khớp với dữ liệu backend |
| AC-7.2 | Lịch sử dòng tiền | Danh sách giao dịch hiển thị: ngày, loại, số tiền, trạng thái — hỗ trợ phân trang |
| AC-7.3 | Thêm thẻ ngân hàng | Nhập thông tin thẻ hợp lệ → lưu thành công, hiển thị trong danh sách |
| AC-7.4 | Đặt thẻ mặc định | Chọn thẻ → đặt mặc định → thẻ cũ mất trạng thái mặc định, thẻ mới hiển thị "Mặc định" |
| AC-7.5 | Validate thẻ ngân hàng | Nhập thiếu thông tin bắt buộc → hiển thị lỗi validation |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-8.1 | Upload ảnh CCCD | Upload ảnh mặt trước/sau → OCR trích xuất: họ tên, số CCCD, ngày sinh, giới tính, địa chỉ |
| AC-8.2 | Xác nhận thông tin OCR | Hiển thị thông tin trích xuất → user xác nhận hoặc chỉnh sửa → gửi xác minh → trạng thái PENDING |
| AC-8.3 | eKYC được duyệt | Admin duyệt → trạng thái APPROVED → user có thể tiếp tục ký hợp đồng |
| AC-8.4 | eKYC bị từ chối | Admin từ chối → trạng thái REJECTED kèm lý do → user nhận thông báo và có thể gửi lại |
| AC-8.5 | Ký hợp đồng thành công | Sau eKYC duyệt → nhập thông tin thanh toán → redirect sang ctv.scalef.com → ký xong → T-Fluencers nhận callback |
| AC-8.6 | Tải hợp đồng | User đã ký → có thể tải hợp đồng PDF qua presigned URL |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-9.1 | Hiển thị danh sách thông báo | Trang thông báo hiển thị danh sách, sắp xếp mới nhất trước, hỗ trợ phân trang |
| AC-9.2 | Đánh dấu đã đọc | Nhấn vào thông báo → trạng thái chuyển "đã đọc", badge số thông báo chưa đọc giảm |
| AC-9.3 | Push notification | Khi có thông báo mới + user đã đăng ký device token → nhận push notification trên thiết bị |
| AC-9.4 | Gửi email | Thông báo quan trọng (duyệt content, hoa hồng) → email gửi đến email đã đăng ký |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-10.1 | Trang chủ hiển thị đúng | Banner, thông tin chương trình, danh sách thử thách hiển thị đúng nội dung từ CMS |
| AC-10.2 | Xem bài viết/thể lệ | Nhấn vào bài viết → hiển thị nội dung đầy đủ (rich text, hình ảnh) |
| AC-10.3 | Trang tin tức | Danh sách tin tức hiển thị, sắp xếp mới nhất trước, hỗ trợ phân trang |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-11.1 | Thống kê cá nhân | Hiển thị tổng content đã gửi, tổng lượt xem, tổng hoa hồng — số liệu khớp backend |
| AC-11.2 | Thống kê content | Danh sách content kèm thông số chi tiết, hỗ trợ phân trang |
| AC-11.3 | Danh sách người được giới thiệu | Hiển thị danh sách invitees: tên, ngày tham gia |
| AC-11.4 | Gửi mã giới thiệu | Nhập mã hợp lệ → liên kết thành công. Mã không tồn tại hoặc đã dùng → hiển thị lỗi |
| AC-11.5 | Không tự giới thiệu | User nhập mã giới thiệu của chính mình → từ chối |

---

# III. Yêu cầu chức năng — Phía Admin

## 12. Đăng nhập Admin

### Mục tiêu
Cho phép quản trị viên đăng nhập vào hệ thống quản trị.

### Phương thức đăng nhập
- **Email + Mật khẩu**: Đăng nhập thông thường

### Luồng nghiệp vụ
1. Admin truy cập trang đăng nhập.
2. Nhập email và mật khẩu.
3. Backend xác thực → tạo JWT token.
4. Chuyển hướng đến trang quản trị.

### Tính năng bổ sung
- Quên mật khẩu → gửi email reset
- Đổi mật khẩu
- Mời nhân viên mới (invite system)
- Xác minh invite token → chấp nhận lời mời

### API đã triển khai
- `POST /staffs/login` — Đăng nhập email/password
- `POST /staffs/forgot-password` — Quên mật khẩu
- `POST /staffs/reset-password` — Đặt lại mật khẩu
- `POST /staffs/invite` — Mời nhân viên
- `POST /staffs/bulk-invite` — Mời hàng loạt

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-12.1 | Đăng nhập thành công | Nhập email + mật khẩu đúng → redirect vào trang quản trị, hiển thị tên admin |
| AC-12.2 | Đăng nhập thất bại | Email/mật khẩu sai → hiển thị "Thông tin đăng nhập không đúng", không cho vào |
| AC-12.3 | Quên mật khẩu | Nhập email → nhận email reset → click link → đặt mật khẩu mới → đăng nhập bằng mật khẩu mới |
| AC-12.4 | Mời nhân viên | Nhập email → gửi invite → người được mời nhận email → click link → xác nhận → tạo tài khoản |
| AC-12.5 | Mời hàng loạt | Upload danh sách email → tất cả nhận được email invite |
| AC-12.6 | Invite token hết hạn | Click link invite sau thời hạn → hiển thị "Link đã hết hạn" |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-13.1 | Danh sách nhân viên | Hiển thị tên, email, vai trò, trạng thái, hỗ trợ tìm kiếm và phân trang |
| AC-13.2 | Tạo nhân viên | Nhập thông tin + gán vai trò → tạo thành công, hiển thị trong danh sách |
| AC-13.3 | Phân quyền RBAC | Collaborator không truy cập được trang đối soát/thanh toán. Campaign Owner chỉ thấy chiến dịch được gán |
| AC-13.4 | Vô hiệu hóa nhân viên | Đổi trạng thái inactive → nhân viên không đăng nhập được |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-14.1 | KPI tổng quan (Admin) | Dashboard hiển thị: tổng content, tổng view, tổng tiền các trạng thái — dữ liệu khớp DB |
| AC-14.2 | Bộ lọc hoạt động | Lọc theo chiến dịch / thời gian → dữ liệu cập nhật tương ứng |
| AC-14.3 | Dashboard phân tích (Next.js) | Hiển thị 6+ thẻ KPI, 7+ loại biểu đồ, 3 tab (Tổng quan/Nền tảng/Creator) |
| AC-14.4 | Bộ lọc nâng cao | Lọc theo nền tảng, khoảng thời gian (7/30/90 ngày, tùy chỉnh) → dữ liệu đúng |
| AC-14.5 | Đa ngôn ngữ | Chuyển ngôn ngữ vi↔en → toàn bộ giao diện dashboard chuyển đổi chính xác |
| AC-14.6 | Phân tích xu hướng | Hiển thị so sánh với kỳ trước, tỷ lệ tăng/giảm chính xác |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-15.1 | Tạo chiến dịch | Nhập đầy đủ thông tin → tạo thành công với trạng thái DRAFT |
| AC-15.2 | Cấu hình cơ cấu thưởng | Tạo reward BY_VIEW hoặc BY_TASK → mốc thưởng và số tiền lưu chính xác |
| AC-15.3 | Kích hoạt chiến dịch | Đổi trạng thái DRAFT → ACTIVE → Creator nhìn thấy trên Cổng Influencer |
| AC-15.4 | Kết thúc chiến dịch | Đổi ACTIVE → ENDED → Creator không submit content mới được |
| AC-15.5 | Chặn submit content | Bật chặn → Creator không gửi bài mới cho chiến dịch này |
| AC-15.6 | Thống kê & biểu đồ | Trang chi tiết hiển thị thống kê: tổng content, tổng view, biểu đồ phân bố |
| AC-15.7 | Validate thời gian | Thời gian kết thúc phải sau thời gian bắt đầu |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-16.1 | Danh sách content | Hiển thị đầy đủ: thumbnail, link, nền tảng, trạng thái, thông số — hỗ trợ lọc và phân trang |
| AC-16.2 | Duyệt content | Chọn content → Approve → trạng thái APPROVED, bắt đầu crawl thống kê, Creator nhận thông báo |
| AC-16.3 | Từ chối content | Chọn content → Reject + nhập lý do bắt buộc → trạng thái REJECTED, Creator nhận thông báo kèm lý do |
| AC-16.4 | Duyệt/Hủy hàng loạt | Chọn nhiều content → batch approve/reject → tất cả cập nhật đúng trạng thái |
| AC-16.5 | Reject không lý do | Nhấn Reject mà không nhập lý do → hiển thị lỗi, không cho phép |
| AC-16.6 | Import content | Upload Excel → hệ thống xử lý → hiển thị tiến độ import, báo lỗi dòng sai |
| AC-16.7 | Ghim content | Ghim content → hiển thị ưu tiên trên giao diện Influencer |
| AC-16.8 | Ghi log | Mọi thao tác duyệt/hủy ghi nhận trong audit log: ai, lúc nào, hành động gì |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-17.1 | Danh sách hồ sơ social | Trong trang User detail, hiển thị danh sách hồ sơ: nền tảng, tên, URL, followers, trạng thái |
| AC-17.2 | Duyệt hồ sơ | Approve → trạng thái APPROVED, Creator nhận thông báo, có thể tham gia thử thách |
| AC-17.3 | Từ chối hồ sơ | Reject + lý do bắt buộc → REJECTED, Creator nhận thông báo kèm lý do |
| AC-17.4 | Hủy duyệt (Revoke) | Hồ sơ đã APPROVED → Revoke → trạng thái thay đổi, Creator nhận thông báo |
| AC-17.5 | Admin tạo hồ sơ social | Admin nhập URL + nền tảng cho user → tạo thành công |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-18.1 | Danh sách user | Hiển thị tên, email, trạng thái, ngày tạo — hỗ trợ tìm kiếm, lọc, phân trang |
| AC-18.2 | Chi tiết user | Xem đầy đủ: thông tin cá nhân, hồ sơ social, thông tin thanh toán, lịch sử tham gia |
| AC-18.3 | Khóa tài khoản | Ban user → user không đăng nhập được, hiển thị thông báo "Tài khoản bị khóa" |
| AC-18.4 | Mở khóa | Unban user → user đăng nhập lại được bình thường |
| AC-18.5 | Tạo user từ admin | Nhập thông tin → tạo thành công, user có thể đăng nhập |
| AC-18.6 | Danh sách influencer | Hiển thị tên, nền tảng, followers, trạng thái — dữ liệu enriched từ AT-Core |
| AC-18.7 | Influencer profile | Xem dữ liệu enrichment: followers, engagement rate, content count, nhân khẩu học |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-19.1 | Danh sách yêu cầu | Hiển thị danh sách eKYC: tên user, ảnh CCCD, trạng thái — hỗ trợ lọc, phân trang |
| AC-19.2 | Xem chi tiết | Hiển thị ảnh CCCD mặt trước/sau, thông tin OCR trích xuất |
| AC-19.3 | Duyệt eKYC | Approve → trạng thái APPROVED, user nhận thông báo, có thể ký hợp đồng |
| AC-19.4 | Từ chối eKYC | Reject + lý do → REJECTED, user nhận thông báo kèm lý do, có thể gửi lại |
| AC-19.5 | Từ chối hợp đồng | Reject contract → user nhận thông báo, trạng thái hợp đồng cập nhật |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-20.1 | Tạo đợt đối soát | Chọn thử thách + loại hoa hồng + thời gian → tạo thành công, hiển thị tổng user/video/tiền |
| AC-20.2 | Xem chi tiết tabs | 4 tab hiển thị đúng: Nội dung, Mốc thưởng, Thưởng bổ sung, Tổng quan |
| AC-20.3 | Đánh giá checklist | Chạy evaluate → phân loại content tự động, hiển thị kết quả AI (nếu có) |
| AC-20.4 | Quick approve/reject | Duyệt/Từ chối nhanh từng content item → trạng thái cập nhật ngay |
| AC-20.5 | Xuất Excel | Nhấn xuất → tạo file Excel đúng cấu trúc (BY_VIEW hoặc BY_TASK), tải thành công |
| AC-20.6 | Kết thúc đợt | Khóa đợt → số dư user cập nhật chính xác, không thao tác thêm được trên đợt đã khóa |
| AC-20.7 | Tính toán chính xác | Tổng tiền đối soát = tổng các mốc thưởng đã đạt + thưởng bổ sung, khớp với Excel xuất ra |

---

## 20A. Snapshot đối soát (Reconciliation Snapshot)

### Mục tiêu
Ghi nhận lại số liệu hiệu suất content (view, like, comment, share) tại các thời điểm cụ thể dưới dạng **ảnh chụp (snapshot) không thể chỉnh sửa**, phục vụ làm bằng chứng trong quá trình đối soát hoa hồng giữa AT, TCB và Creator — đảm bảo tính minh bạch, truy vết và chống tranh chấp khi có khác biệt giữa số liệu đầu kỳ và cuối kỳ.

### Luồng nghiệp vụ

#### Phần 1 — Cơ chế tạo Snapshot

Hệ thống tạo snapshot theo **3 cơ chế độc lập**:

**1) Tạo theo crawl hàng ngày (Daily Crawl Snapshot)**
- Kích hoạt tự động mỗi lần hệ thống crawl content (theo lịch crawl định kỳ 15-30 phút/lần).
- Mỗi content được crawl → ngay sau đó tự động tạo một snapshot ghi lại số liệu hiện tại.
- Chạy song song, không chặn luồng crawl chính.
- Nguồn (`source`): `daily_crawl`.

**2) Tạo sau khi thử thách kết thúc (Post-Expiry Crawl)**
- Cron job tự động chạy lúc **02:00 sáng hàng ngày**.
- Hệ thống tìm tất cả thử thách đã kết thúc (`endAt < hiện tại`) nhưng chưa đóng đối soát.
- Crawl lại toàn bộ content của các reward hợp lệ (không bị từ chối) → tạo snapshot.
- Đảm bảo luôn có snapshot chốt sau khi thử thách kết thúc, kể cả khi crawl hàng ngày bị gián đoạn.
- Nguồn (`source`): `post_expiry_crawl`.

**3) Tạo bổ sung thủ công (Makeup Crawl)**
- Admin trigger thủ công qua nút "Crawl bổ sung" trên trang đối soát.
- Hệ thống tự động phát hiện các ngày thiếu snapshot trong khoảng từ `endAt` đến hiện tại (detect missing days).
- Có cơ chế **debounce 1 giờ** (trừ khi force) để tránh spam crawl.
- Dùng khi admin phát hiện thiếu dữ liệu hoặc cần lấy lại số liệu mới nhất trước khi đóng đối soát.
- Nguồn (`source`): `makeup_crawl`.

#### Phần 2 — Dữ liệu ghi nhận trong Snapshot

Mỗi snapshot ghi nhận đầy đủ thông tin sau (bất biến sau khi tạo):

| Trường | Mô tả |
|---|---|
| `user` | ID Creator sở hữu content |
| `event` | ID thử thách |
| `content` | ID content/bài đăng |
| `contentSource` | Nền tảng (tiktok / facebook / youtube / instagram) |
| `date` | Ngày tạo snapshot (theo múi giờ Việt Nam) |
| `viewCount` | Số lượt xem tại thời điểm snapshot |
| `likeCount` | Số lượt thích |
| `commentCount` | Số bình luận |
| `shareCount` | Số lượt chia sẻ |
| `hashtags` | Danh sách hashtag của content |
| `crawlSuccess` | Trạng thái crawl thành công hay thất bại |
| `statusCode` | Mã phản hồi từ dịch vụ crawl |
| `source` | Nguồn tạo snapshot (`daily_crawl` / `post_expiry_crawl` / `makeup_crawl`) |
| `crawledAt` | Thời điểm crawl |
| `createdAt` | Thời điểm ghi vào hệ thống |

**Đặc điểm quan trọng:**
- Snapshot là **immutable** — không cho phép sửa, xóa sau khi tạo.
- Mỗi content có thể có **nhiều snapshot theo thời gian** → tạo thành chuỗi lịch sử phục vụ phân tích xu hướng và đối chiếu.

#### Phần 3 — Sử dụng Snapshot trong quá trình đối soát

Snapshot được sử dụng tại 3 điểm chính trong luồng đối soát:

**1) Giai đoạn Chuẩn bị (DRAFT → IN_PROGRESS)**
- Khi tạo đợt đối soát, hệ thống lấy **snapshot gần nhất** của mỗi content (theo `crawledAt` giảm dần).
- Số liệu snapshot được dùng để tính **số tiền dự kiến** theo các mốc thưởng.
- Số liệu này được **"khóa"** như giá trị gốc, không thay đổi kể cả khi content có thêm lượt xem sau đó.

**2) Giai đoạn Đánh giá Checklist (IN_PROGRESS → REVIEWED)**
- Hệ thống tự động đánh giá các tiêu chí checklist dựa trên dữ liệu snapshot:
  - `video_accessible`: Content còn truy cập được không (dựa vào `crawlSuccess` + `statusCode`)
  - `hashtag_present`: Hashtag yêu cầu có xuất hiện trong `hashtags` không
  - `view_not_dropped`: So sánh view hiện tại với view snapshot → phát hiện sụt giảm bất thường
- Các content có cảnh báo → Admin xem chi tiết và override/confirm thủ công.

**3) Giai đoạn Công bố & Thanh toán (REVIEWED → CLOSED)**
- Số liệu snapshot là **bằng chứng cuối cùng** gửi đến Creator khi công bố kết quả đối soát.
- Nếu Creator có khiếu nại → Admin kiểm tra lại snapshot làm căn cứ.
- Khi đợt đối soát đóng (CLOSED) → snapshot liên quan vẫn giữ nguyên như bản ghi kiểm toán (audit trail).

### Quy tắc nghiệp vụ

| # | Quy tắc | Mô tả |
|---|---|---|
| BR-SS.1 | Snapshot bất biến | Không cho phép sửa, xóa snapshot sau khi tạo |
| BR-SS.2 | Nhiều snapshot/content | Một content có thể có nhiều snapshot theo thời gian; luôn dùng **snapshot gần nhất** khi tính toán đối soát |
| BR-SS.3 | Ưu tiên theo nguồn | Khi có nhiều snapshot cùng ngày, ưu tiên theo thứ tự: `makeup_crawl` > `post_expiry_crawl` > `daily_crawl` |
| BR-SS.4 | Debounce Makeup Crawl | Makeup crawl có cơ chế chống spam 1 giờ (trừ khi admin force) |
| BR-SS.5 | Timezone chuẩn | Ngày snapshot (`date`) tính theo múi giờ **Asia/Ho_Chi_Minh**, lấy đầu ngày (start of day) |
| BR-SS.6 | Bắt buộc có snapshot | Đợt đối soát chỉ có thể chuyển sang CLOSED khi tất cả content item đều có ít nhất 1 snapshot |

### API đã triển khai
- `POST /reconciliations/events/:eventId/makeup-crawl` — Trigger tạo snapshot bổ sung thủ công (hỗ trợ query `?force=true`)
- `GET /reconciliations/:id/content` — Danh sách content item (đã chứa dữ liệu snapshot mới nhất)
- `POST /reconciliations/:id/evaluate` — Đánh giá checklist sử dụng dữ liệu snapshot
- Cron job `post-expiry-crawl` — Tự động chạy 02:00 AM hàng ngày (không phải API)

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-20A.1 | Tạo snapshot khi crawl hàng ngày | Crawl content → tự động tạo snapshot với `source=daily_crawl`, ghi đúng các chỉ số view/like/comment/share |
| AC-20A.2 | Cron post-expiry crawl | Lúc 02:00 AM → tìm đúng event đã hết hạn chưa close, crawl và tạo snapshot với `source=post_expiry_crawl` |
| AC-20A.3 | Makeup crawl thủ công | Admin trigger API → hệ thống phát hiện các ngày thiếu, tạo snapshot với `source=makeup_crawl` |
| AC-20A.4 | Debounce makeup crawl | Trigger makeup crawl 2 lần trong 1 giờ → lần 2 bị chặn; gọi với `force=true` → cho phép chạy |
| AC-20A.5 | Snapshot bất biến | Không có API/chức năng sửa hoặc xóa snapshot đã tạo |
| AC-20A.6 | Dùng snapshot gần nhất | Mở đợt đối soát → số liệu view/like hiển thị khớp với snapshot mới nhất của content |
| AC-20A.7 | Đánh giá checklist theo snapshot | Chạy evaluate → các tiêu chí `video_accessible`, `hashtag_present`, `view_not_dropped` dùng đúng dữ liệu snapshot |
| AC-20A.8 | Phát hiện view giảm | Nếu view hiện tại < view snapshot → checklist `view_not_dropped` báo cảnh báo (warning) |
| AC-20A.9 | Số liệu đối soát không đổi | Sau khi đợt đối soát bắt đầu, view trong đối soát giữ nguyên kể cả content nhận thêm view mới |
| AC-20A.10 | Timezone | Ngày snapshot (`date`) khớp với đầu ngày theo múi giờ Việt Nam (Asia/Ho_Chi_Minh) |
| AC-20A.11 | Phân biệt nguồn snapshot | Query snapshot → phân biệt được nguồn (`daily_crawl` / `post_expiry_crawl` / `makeup_crawl`) |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-21.1 | Tạo đợt thanh toán | Tạo đợt → hệ thống tổng hợp user có hoa hồng đã đối soát chưa thanh toán |
| AC-21.2 | Xem chi tiết | Hiển thị danh sách user + số tiền + trạng thái — hỗ trợ phân trang |
| AC-21.3 | Xuất Excel | Tải file Excel chứa đầy đủ thông tin thanh toán |
| AC-21.4 | Xác nhận thanh toán | Confirm → đẩy lệnh rút tiền sang Service TOS, trạng thái cập nhật |
| AC-21.5 | Hủy thanh toán | Cancel + lý do → trạng thái hủy, số dư user không thay đổi |
| AC-21.6 | Kết thúc đợt | Khóa → cập nhật số dư user (đã thanh toán), ghi log giao dịch |
| AC-21.7 | Retry tự động | Push TOS thất bại → cron retry mỗi 30 phút → thành công sau retry |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-22.1 | Tạo ngân sách | Tạo budget cap cho chiến dịch → lưu thành công, hiển thị trong danh sách |
| AC-22.2 | Cảnh báo 75% | Hoa hồng phát sinh đạt 75% budget → Admin nhận email cảnh báo |
| AC-22.3 | Chặn submit 95% | Đạt 95% → tự động chặn Creator submit content mới cho chiến dịch |
| AC-22.4 | Ngừng tính hoa hồng 100% | Đạt 100% → hệ thống không lưu hoa hồng dự kiến mới |
| AC-22.5 | Thông báo Creator | Creator nhận thông báo khi chiến dịch bị chặn submit do vượt budget |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-23.1 | Tạo yêu cầu xuất | Nhấn "Xuất dữ liệu" → tạo request trạng thái "Đang tạo", hiển thị trong danh sách |
| AC-23.2 | Xử lý background | Background job chạy → tạo Excel → lưu MinIO → trạng thái "Thành công" |
| AC-23.3 | Tải file | Nhấn tải → presigned URL hiệu lực 30 giây → tải file thành công |
| AC-23.4 | Link hết hạn | Truy cập link sau 30 giây → lỗi access denied |
| AC-23.5 | Ghi log | Mỗi lần tải ghi log: user, thời điểm, IP |

---

## 24. Quản lý bài viết, tin tức & nội dung CMS

### Mục tiêu
Cho phép Admin soạn thảo hướng dẫn, thể lệ, bài viết, tin tức hiển thị trên Cổng Influencer.

### Luồng nghiệp vụ
1. Admin tạo/sửa bài viết (Article): rich text editor (Braft Editor).
2. Quản lý tin tức (News): tạo, sửa, đổi trạng thái, clone.
3. Quản lý tag: phân loại nội dung.
4. Quản lý Quick Action: các liên kết hành động nhanh (hỗ trợ, hướng dẫn).

### Ràng buộc dữ liệu
| Đối tượng | Trường | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|---|
| Article | Tiêu đề | Text | Có | |
| Article | Nội dung | Rich Text | Có | Hỗ trợ hình ảnh, link, bảng |
| Article | Trạng thái | Enum | Có | DRAFT / PUBLISHED |
| News | Tiêu đề | Text | Có | |
| News | Mô tả ngắn | Text | Không | Hiển thị ở danh sách |
| News | Nội dung | Rich Text | Có | |
| News | Ảnh bìa | File | Không | JPG/PNG |
| News | Trạng thái | Enum | Có | DRAFT / PUBLISHED |
| Tag | Tên | Text | Có | Không trùng |
| Quick Action | Tiêu đề | Text | Có | |
| Quick Action | URL | URL | Có | Link hành động |
| Quick Action | Icon | File/Text | Không | |

### API đã triển khai
- CRUD cho Articles, News, Tags, Quick Actions

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-24.1 | Tạo bài viết | Nhập tiêu đề + nội dung rich text → lưu DRAFT → hiển thị trong danh sách |
| AC-24.2 | Xuất bản bài viết | Đổi trạng thái PUBLISHED → hiển thị trên Cổng Influencer |
| AC-24.3 | Rich text editor | Editor hỗ trợ: bold, italic, heading, hình ảnh, link, bảng, danh sách |
| AC-24.4 | Quản lý tin tức | Tạo/sửa/clone/đổi trạng thái tin tức → hoạt động chính xác |
| AC-24.5 | Quản lý tag | Tạo/sửa/xóa tag → phân loại bài viết/tin tức chính xác |
| AC-24.6 | Quick Action | Tạo quick action → hiển thị trên Cổng Influencer, link hoạt động |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-25.1 | Tạo thông báo | Nhập tiêu đề + nội dung + chọn đối tượng nhận → lưu thành công |
| AC-25.2 | Gửi đa kênh | Gửi thông báo → Creator nhận qua: in-app + push (FCM) + email (SendGrid) tùy cấu hình |
| AC-25.3 | Gửi theo segment | Chọn segment → chỉ Creator trong segment nhận thông báo |
| AC-25.4 | Clone thông báo | Clone → tạo bản sao với nội dung giống, có thể chỉnh sửa trước khi gửi |
| AC-25.5 | Theo dõi trạng thái | Hiển thị trạng thái: Hoàn thành / Từ chối — Admin biết thông báo đã gửi thành công hay chưa |

---

## 26. Phân khúc người dùng (Segments)

### Mục tiêu
Cho phép Admin phân nhóm creator để phục vụ lọc, gửi thông báo, quản lý chiến dịch.

### Luồng nghiệp vụ
1. Admin tạo segment: đặt tên, mô tả mục đích.
2. Thêm user vào segment thủ công hoặc import từ Excel.
3. Xóa user khỏi segment.
4. Sử dụng segment để: lọc danh sách user, gửi thông báo, cấu hình điều kiện chiến dịch.

### Ràng buộc dữ liệu
| Trường | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|
| Tên segment | Text | Có | Không trùng |
| Mô tả | Text | Không | |
| Danh sách user | Array (User ID) | Có | Ít nhất 1 user |

### API đã triển khai
- CRUD cho Segments
- `POST /user-segments/import-excel` — Import từ Excel

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-26.1 | Tạo segment | Nhập tên + mô tả → tạo thành công |
| AC-26.2 | Thêm user | Thêm user vào segment → user xuất hiện trong danh sách thành viên |
| AC-26.3 | Import từ Excel | Upload file Excel chứa danh sách user → thêm hàng loạt, báo lỗi dòng sai (user không tồn tại) |
| AC-26.4 | Xóa user | Xóa user khỏi segment → user không còn trong danh sách |
| AC-26.5 | Tên không trùng | Tạo segment trùng tên → hiển thị lỗi |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-27.1 | Quản lý đối tác | CRUD partner: tạo/sửa/xem/xóa → hoạt động chính xác |
| AC-27.2 | Tạo chiến dịch | Tạo campaign cho partner → lưu thành công |
| AC-27.3 | Chạy matching | Chạy thuật toán → hiển thị danh sách influencer phù hợp, kèm điểm matching |
| AC-27.4 | Thêm/Xóa influencer | Thêm influencer vào campaign → hiển thị trong danh sách. Xóa → không còn |
| AC-27.5 | Lịch sử matching | Xem được các lần chạy matching trước đó, kết quả từng lần |

---

## 28. Đánh giá & Xếp hạng Influencer (Review/Rating)

### Mục tiêu
Cho phép Admin và Brand đánh giá influencer sau chiến dịch.

### Luồng nghiệp vụ
1. Admin hoặc Brand gửi review cho profile influencer.
2. Đánh giá theo nhiều tiêu chí, cho điểm từng tiêu chí.
3. Viết nhận xét (comment) kèm review.
4. Xem thống kê rating tổng hợp: điểm trung bình, phân bố theo tiêu chí.

### Tiêu chí đánh giá
| Tiêu chí | Mô tả | Thang điểm |
|---|---|---|
| Chất lượng nội dung | Chất lượng video/bài đăng | 1-5 |
| Đúng deadline | Gửi bài đúng thời hạn | 1-5 |
| Tuân thủ brief | Nội dung đúng yêu cầu chiến dịch | 1-5 |
| Thái độ hợp tác | Giao tiếp, phản hồi | 1-5 |
| Hiệu quả tương tác | Lượt view, engagement thực tế | 1-5 |

### API đã triển khai
- `POST /profiles/:profile_id/reviews` — Gửi review
- `GET /profiles/:profile_id/reviews` — Danh sách review
- `GET /profiles/:profile_id/ratings/stats` — Thống kê rating

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-28.1 | Gửi review | Chọn profile → chấm điểm từng tiêu chí + viết nhận xét → lưu thành công |
| AC-28.2 | Danh sách review | Xem tất cả review cho 1 profile: người đánh giá, ngày, điểm, nhận xét |
| AC-28.3 | Thống kê rating | Hiển thị điểm trung bình tổng và từng tiêu chí, số lượt đánh giá |
| AC-28.4 | Không đánh giá trùng | 1 reviewer chỉ đánh giá 1 lần cho 1 profile trong 1 chiến dịch |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-29.1 | Import CSV | Upload file CSV → xử lý batch → hiển thị kết quả: thành công/thất bại từng dòng |
| AC-29.2 | Danh sách dữ liệu | Xem danh sách đã import, hỗ trợ phân trang |
| AC-29.3 | Quản lý batch | Xem danh sách batch import: ngày, số dòng, trạng thái |
| AC-29.4 | Biểu đồ xu hướng | Dữ liệu import hiển thị trên biểu đồ xu hướng hiệu suất trên dashboard |

---

## 30. Quản lý mã (Code Management)

### Mục tiêu
Cho phép Admin tạo và quản lý mã tham gia thử thách (promo code / invite code).

### Luồng nghiệp vụ
1. Admin tạo mã mới: nhập mã hoặc sinh tự động, gán cho thử thách cụ thể.
2. Import hàng loạt từ Excel.
3. Xem danh sách mã: mã, thử thách liên kết, trạng thái (đã dùng / chưa dùng), ngày tạo.
4. Xóa mã chưa sử dụng.

### Ràng buộc dữ liệu
| Trường | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|
| Mã code | Text | Có | Duy nhất, không trùng |
| Thử thách | Ref (Event) | Có | Liên kết với chiến dịch |
| Trạng thái | Enum | Tự động | UNUSED / USED |
| Ngày tạo | DateTime | Tự động | |
| Người sử dụng | Ref (User) | Tự động | Ghi nhận khi mã được dùng |

### API đã triển khai
- `POST /manage-codes` — Tạo mã
- `GET /manage-codes` — Danh sách
- `POST /manage-codes/import-excel` — Import từ Excel
- `DELETE /manage-codes/:id` — Xóa mã

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-30.1 | Tạo mã | Tạo mã + gán thử thách → lưu thành công, hiển thị trong danh sách |
| AC-30.2 | Mã không trùng | Tạo mã đã tồn tại → hiển thị lỗi |
| AC-30.3 | Import Excel | Upload Excel → tạo hàng loạt, báo lỗi dòng trùng/sai |
| AC-30.4 | Xóa mã | Xóa mã chưa dùng → thành công. Xóa mã đã dùng → từ chối |
| AC-30.5 | Sử dụng mã | Creator nhập mã → tham gia thử thách invite-only, mã chuyển trạng thái USED |

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

### Tiêu chí chấp nhận (Acceptance Criteria)
| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| AC-31.1 | Ghi log tự động | Mọi thao tác quan trọng (duyệt/hủy content, đối soát, thanh toán, ban/unban) được ghi log tự động |
| AC-31.2 | Nội dung log | Mỗi dòng log chứa: người thao tác, thời gian, hành động, đối tượng bị tác động |
| AC-31.3 | Xem lịch sử | Admin xem danh sách audit log, hỗ trợ lọc theo thời gian, người thao tác, loại hành động |
| AC-31.4 | Ghi nhận đăng nhập | Mỗi lần admin đăng nhập ghi log: email, IP, thời gian, kết quả (thành công/thất bại) |
| AC-31.5 | Không thể xóa/sửa | Audit log chỉ đọc, không ai có thể sửa hoặc xóa |

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

---

# VII. Yêu cầu phi chức năng (NFR)

## 1. Hiệu năng (Performance)

| Chỉ số | Mục tiêu | Ghi chú |
|---|---|---|
| Response time (API) | ≤ 500ms (P95) | Cho các API đọc dữ liệu thông thường |
| Response time (API ghi) | ≤ 1000ms (P95) | Cho các API tạo/cập nhật dữ liệu |
| Response time (Dashboard) | ≤ 3000ms (P95) | Cho các truy vấn analytics phức tạp |
| Tải trang đầu tiên | ≤ 3 giây | Trên kết nối 4G (10 Mbps) |
| File upload | ≤ 30 giây | Cho file ≤ 50MB |
| Export Excel | ≤ 5 phút | Cho dataset ≤ 100.000 dòng |

## 2. Khả dụng (Availability)

| Chỉ số | Mục tiêu |
|---|---|
| Uptime | ≥ 99.5% (tương đương ≤ 3.65 giờ downtime/tháng) |
| Bảo trì định kỳ | Thông báo trước ≥ 24 giờ, thực hiện ngoài giờ cao điểm (22:00-06:00 GMT+7) |
| Recovery Time Objective (RTO) | ≤ 4 giờ |
| Recovery Point Objective (RPO) | ≤ 1 giờ (tối đa mất dữ liệu 1 giờ) |

## 3. Khả năng chịu tải (Scalability)

| Chỉ số | Mục tiêu |
|---|---|
| Concurrent users (Creator) | ≥ 1.000 người dùng đồng thời |
| Concurrent users (Admin) | ≥ 50 admin đồng thời |
| Tổng Creator đã đăng ký | ≥ 100.000 tài khoản |
| Tổng content | ≥ 500.000 bài tham gia |
| Cron job crawl | Xử lý ≥ 10.000 video/lần crawl |

## 4. Bảo mật (Security)

| Chỉ số | Mục tiêu |
|---|---|
| Mã hóa truyền tải | TLS 1.2+ cho mọi kết nối |
| Mã hóa lưu trữ | AES-256 cho dữ liệu PII nhạy cảm (CCCD, số tài khoản) |
| JWT expiry | Access token: 24 giờ. Refresh token: 7 ngày |
| Rate limiting | ≤ 100 requests/phút/IP cho API public. ≤ 300 requests/phút/IP cho API admin |
| Brute force protection | Khóa tạm sau 5 lần đăng nhập thất bại liên tiếp (15 phút) |
| Presigned URL TTL | 30 giây cho file download |
| Audit log retention | ≥ 12 tháng |

## 5. Sao lưu & Phục hồi (Backup & Recovery)

| Hạng mục | Chính sách |
|---|---|
| Database (MongoDB) | Backup tự động hàng ngày, lưu ≥ 30 ngày |
| File storage (MinIO) | Replicate cross-zone, backup weekly |
| Disaster recovery | Có quy trình phục hồi được kiểm tra định kỳ |

## 6. Tương thích (Compatibility)

| Hạng mục | Yêu cầu |
|---|---|
| Trình duyệt (Creator) | Chrome, Safari, Firefox — 2 phiên bản gần nhất |
| Trình duyệt (Admin) | Chrome — 2 phiên bản gần nhất |
| Thiết bị (Creator) | Responsive: mobile ≥ 375px, tablet ≥ 768px, desktop ≥ 1024px |
| Thiết bị (Admin) | Desktop ≥ 1024px |

---

# VIII. Vòng đời trạng thái (State Diagrams)

## 1. Content (Bài tham gia)

```
                    ┌──────────────┐
   Creator submit → │   PENDING    │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            │            ▼
     ┌────────────┐        │    ┌────────────┐
     │  APPROVED  │        │    │  REJECTED  │
     └────────────┘        │    └──────┬─────┘
              │            │           │
              │            │    Creator sửa & gửi lại
              │            │           │
              │            └───────────┘
              │
     Crawl thống kê bắt đầu
              │
     ┌────────┴────────────────┐
     │ Auto reject (not found) │
     └────────┬────────────────┘
              ▼
     ┌────────────┐
     │  REJECTED  │
     └────────────┘
```

**Quy tắc chuyển trạng thái:**

| Từ trạng thái | Đến trạng thái | Ai thực hiện | Điều kiện |
|---|---|---|---|
| — | PENDING | Creator | Submit link video hợp lệ |
| PENDING | APPROVED | Admin | Duyệt thủ công hoặc quick approve |
| PENDING | REJECTED | Admin | Từ chối + lý do bắt buộc |
| PENDING | REJECTED | Hệ thống | Auto reject: content không hợp lệ hoặc không tìm thấy trên nền tảng |
| APPROVED | REJECTED | Admin | Phát hiện vi phạm sau duyệt (revoke) |
| REJECTED | PENDING | Creator | Sửa và gửi lại (nếu thử thách còn mở) |

## 2. Hồ sơ Social (User Social)

```
                      ┌──────────────┐
   Creator đăng ký → │   PENDING    │
                      └──────┬───────┘
                             │
                ┌────────────┼────────────┐
                ▼                         ▼
       ┌────────────┐            ┌────────────┐
       │  APPROVED  │            │  REJECTED  │
       └──────┬─────┘            └──────┬─────┘
              │                         │
              │                  Creator gửi lại
         Phát hiện vi phạm              │
              │                         │
              ▼                         │
       ┌────────────┐                   │
       │  REVOKED   │                   │
       └────────────┘                   │
```

**Quy tắc chuyển trạng thái:**

| Từ trạng thái | Đến trạng thái | Ai thực hiện | Điều kiện |
|---|---|---|---|
| — | PENDING | Creator | Đăng ký kênh MXH |
| PENDING | APPROVED | Admin / Hệ thống | TikTok: tự động (OAuth). YouTube: tự động (API). FB/IG/Threads: Admin duyệt |
| PENDING | REJECTED | Admin / Hệ thống | Không đạt điều kiện followers hoặc hashtag không khớp |
| APPROVED | REVOKED | Admin | Phát hiện vi phạm |
| REJECTED | PENDING | Creator | Gửi lại hồ sơ |

## 3. Đối soát (Reconciliation)

```
   ┌──────────┐     ┌─────────────┐     ┌────────────┐     ┌──────────┐
   │  DRAFT   │ ──→ │ IN_PROGRESS │ ──→ │  REVIEWED  │ ──→ │  CLOSED  │
   └──────────┘     └──────┬──────┘     └────────────┘     └──────────┘
                           │
                           ▼
                    ┌────────────┐
                    │ CANCELLED  │
                    └────────────┘
```

**Quy tắc chuyển trạng thái:**

| Từ trạng thái | Đến trạng thái | Ai thực hiện | Điều kiện |
|---|---|---|---|
| — | DRAFT | Admin | Tạo đợt đối soát |
| DRAFT | IN_PROGRESS | Admin | Bắt đầu đối soát |
| IN_PROGRESS | REVIEWED | Admin | Hoàn tất đánh giá checklist tất cả content items |
| REVIEWED | CLOSED | Admin | Xác nhận kết thúc → khóa đợt, cập nhật số dư user |
| IN_PROGRESS | CANCELLED | Admin | Hủy đợt đối soát |
| CLOSED | — | — | Không thể thay đổi sau khi đóng |

## 4. Thanh toán (Transfer)

```
   ┌──────────┐     ┌─────────────┐     ┌────────────┐     ┌──────────┐
   │  DRAFT   │ ──→ │  CONFIRMED  │ ──→ │ PROCESSING │ ──→ │ COMPLETED│
   └──────────┘     └──────┬──────┘     └──────┬─────┘     └──────────┘
                           │                    │
                           ▼                    ▼
                    ┌────────────┐       ┌────────────┐
                    │ CANCELLED  │       │   FAILED   │
                    └────────────┘       └──────┬─────┘
                                                │
                                         Retry (auto)
                                                │
                                                ▼
                                        ┌────────────┐
                                        │ PROCESSING │
                                        └────────────┘
```

**Quy tắc chuyển trạng thái:**

| Từ trạng thái | Đến trạng thái | Ai thực hiện | Điều kiện |
|---|---|---|---|
| — | DRAFT | Admin | Tạo đợt thanh toán |
| DRAFT | CONFIRMED | Admin | Xác nhận danh sách thanh toán |
| CONFIRMED | PROCESSING | Hệ thống | Đẩy lệnh rút tiền sang Service TOS |
| PROCESSING | COMPLETED | Hệ thống | TOS xác nhận thanh toán thành công → cập nhật số dư user |
| PROCESSING | FAILED | Hệ thống | TOS trả lỗi |
| FAILED | PROCESSING | Hệ thống | Retry tự động (cron mỗi 30 phút, tối đa theo cấu hình) |
| DRAFT | CANCELLED | Admin | Hủy đợt thanh toán + lý do |
| COMPLETED | — | — | Không thể thay đổi sau khi hoàn tất |

## 5. Chiến dịch / Thử thách (Event)

```
   ┌──────────┐     ┌──────────┐     ┌──────────┐
   │  DRAFT   │ ──→ │  ACTIVE  │ ──→ │  ENDED   │
   └──────────┘     └────┬─────┘     └──────────┘
                         │
                         ▼
                  ┌────────────┐
                  │ CANCELLED  │
                  └────────────┘
```

| Từ trạng thái | Đến trạng thái | Ai thực hiện | Điều kiện |
|---|---|---|---|
| — | DRAFT | Admin | Tạo chiến dịch |
| DRAFT | ACTIVE | Admin | Kích hoạt → Creator nhìn thấy và tham gia được |
| ACTIVE | ENDED | Admin / Hệ thống | Kết thúc thủ công hoặc hết thời hạn |
| ACTIVE | CANCELLED | Admin | Hủy chiến dịch |
| ENDED | — | — | Không thể mở lại |

## 6. eKYC (Xác minh danh tính)

```
   ┌──────────┐     ┌────────────┐
   │ PENDING  │ ──→ │  APPROVED  │
   └────┬─────┘     └────────────┘
        │
        ▼
   ┌────────────┐
   │  REJECTED  │ ──→ Creator gửi lại → PENDING
   └────────────┘
```

| Từ trạng thái | Đến trạng thái | Ai thực hiện | Điều kiện |
|---|---|---|---|
| — | PENDING | Creator | Gửi ảnh CCCD + xác nhận thông tin |
| PENDING | APPROVED | Admin | Duyệt |
| PENDING | REJECTED | Admin | Từ chối + lý do |
| REJECTED | PENDING | Creator | Gửi lại thông tin mới |

---

# IX. Quy tắc nghiệp vụ (Business Rules)

## 1. Quy tắc hoa hồng

| # | Quy tắc | Mô tả |
|---|---|---|
| BR-1.1 | Chỉ content APPROVED mới tính hoa hồng | Content ở trạng thái PENDING hoặc REJECTED không phát sinh hoa hồng |
| BR-1.2 | Hoa hồng theo mốc (BY_VIEW) | Mỗi mốc view (vd: 10K, 50K, 100K views) có số tiền thưởng tương ứng, cấu hình trong Event Reward |
| BR-1.3 | Hoa hồng theo nhiệm vụ (BY_TASK) | Hoàn thành nhiệm vụ (vd: đăng video, đạt engagement) → nhận hoa hồng cố định |
| BR-1.4 | Mốc thưởng tích lũy | Creator đạt mốc 50K views → nhận thưởng mốc 10K + 50K (nếu chưa nhận mốc 10K trước đó) |
| BR-1.5 | Không tính trùng | 1 video chỉ tính hoa hồng 1 lần cho mỗi mốc. Đạt mốc rồi thì không tính lại |
| BR-1.6 | Hoa hồng dự kiến vs thực nhận | Hoa hồng tính tự động = **dự kiến**. Chỉ trở thành **thực nhận** sau khi đối soát (Reconciliation) xác nhận |
| BR-1.7 | Làm tròn | Số tiền hoa hồng làm tròn xuống đến đơn vị VNĐ (không có phần thập phân) |

## 2. Quy tắc ngân sách (Budget)

| # | Quy tắc | Mô tả |
|---|---|---|
| BR-2.1 | Budget cap là hard limit | Tổng hoa hồng thực nhận không được vượt budget cap của chiến dịch |
| BR-2.2 | Tính budget usage | `Budget usage = (Tổng hoa hồng đã đối soát + Tổng hoa hồng dự kiến) / Budget cap × 100%` |
| BR-2.3 | Ngưỡng 75% — Cảnh báo | Gửi email cảnh báo cho Admin. Không ảnh hưởng hoạt động |
| BR-2.4 | Ngưỡng 95% — Chặn submit | Tự động bật flag `block-user-submit-content` → Creator không gửi content mới |
| BR-2.5 | Ngưỡng 100% — Ngừng tính hoa hồng | Hệ thống không lưu hoa hồng dự kiến mới. Hoa hồng đã lưu trước đó vẫn giữ |
| BR-2.6 | Kiểm tra budget trước khi lưu hoa hồng | Mỗi lần cron tính hoa hồng → kiểm tra budget trước → nếu vượt 100% thì không lưu |
| BR-2.7 | Tần suất giám sát | Cron kiểm tra budget mỗi 30 phút |

## 3. Quy tắc đối soát (Reconciliation)

| # | Quy tắc | Mô tả |
|---|---|---|
| BR-3.1 | Chỉ đối soát content APPROVED | Content PENDING hoặc REJECTED không xuất hiện trong đợt đối soát |
| BR-3.2 | Đợt đã đóng không thể mở lại | Trạng thái CLOSED là terminal, đảm bảo tính toàn vẹn tài chính |
| BR-3.3 | Cập nhật số dư khi đóng đợt | Khi CLOSED → số dư "đã đối soát" của user tăng tương ứng |
| BR-3.4 | Snapshot kiểm toán | Khi đóng đợt → tạo snapshot dữ liệu tại thời điểm đó → không thay đổi sau |
| BR-3.5 | Excel = source of truth | Dữ liệu xuất Excel phải khớp 100% với dữ liệu hiển thị trên giao diện |

## 4. Quy tắc thanh toán (Transfer)

| # | Quy tắc | Mô tả |
|---|---|---|
| BR-4.1 | Chỉ thanh toán hoa hồng đã đối soát | Chỉ số dư "đã đối soát, chưa thanh toán" mới được đưa vào đợt thanh toán |
| BR-4.2 | Yêu cầu hợp đồng | Creator phải có hợp đồng đã ký (qua Service TOS) mới nhận thanh toán |
| BR-4.3 | Yêu cầu eKYC | Creator phải có eKYC APPROVED mới nhận thanh toán |
| BR-4.4 | Yêu cầu thẻ ngân hàng | Creator phải có ít nhất 1 thẻ ngân hàng đã đăng ký |
| BR-4.5 | Retry policy | Push TOS thất bại → retry mỗi 30 phút, tối đa theo cấu hình hệ thống |
| BR-4.6 | Cập nhật số dư khi hoàn tất | COMPLETED → số dư "đã thanh toán" tăng, "chưa thanh toán" giảm tương ứng |

## 5. Quy tắc hồ sơ social

| # | Quy tắc | Mô tả |
|---|---|---|
| BR-5.1 | Mỗi nền tảng 1 hồ sơ APPROVED | User không có 2 hồ sơ APPROVED cho cùng 1 nền tảng |
| BR-5.2 | Hashtag xác minh quyền sở hữu | Hệ thống sinh hashtag duy nhất → user phải thêm vào profile → hệ thống verify |
| BR-5.3 | Ngưỡng followers cấu hình | Ngưỡng tối thiểu followers cấu hình qua Admin (Conditions), khác nhau theo nền tảng và chiến dịch |
| BR-5.4 | TikTok xác thực tự động | OAuth → lấy data API → verify ngay. Không cần Admin duyệt thủ công |
| BR-5.5 | YouTube xác thực bán tự động | URL + hashtag + YouTube API → verify ngay |
| BR-5.6 | FB/IG/Threads duyệt thủ công | PENDING → Admin crawl + verify → kết quả trong 1 ngày làm việc |

## 6. Quy tắc content

| # | Quy tắc | Mô tả |
|---|---|---|
| BR-6.1 | Link video phải public | Video private hoặc restricted → không hợp lệ |
| BR-6.2 | Hashtag bắt buộc | Content phải chứa hashtag của chiến dịch, kiểm tra khi submit và khi crawl |
| BR-6.3 | Nền tảng phải khớp | Link TikTok chỉ submit cho hồ sơ TikTok, YouTube cho YouTube, v.v. |
| BR-6.4 | Auto reject | Content không tìm thấy trên nền tảng sau X ngày → tự động REJECTED (cron 04:30) |
| BR-6.5 | Warning tag | Content vi phạm (views bất thường, engagement giả) → gắn cờ cảnh báo tự động (cron 05:30) |
| BR-6.6 | Crawl thống kê | Content APPROVED → bắt đầu crawl views/engagement định kỳ (mỗi 4 giờ) |

---

*Tài liệu đặc tả yêu cầu phần mềm v2.1*
*Ngày: 01/11/2025*
