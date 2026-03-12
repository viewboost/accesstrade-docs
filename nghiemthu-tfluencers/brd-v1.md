# TÀI LIỆU YÊU CẦU NGHIỆP VỤ (BRD)

### Dự án: **Techcombank Influencer Platform (T-Fluencers)**

**Phiên bản:** 1.0

**Ngày phát hành:** 01/11/2025

---

## Lịch sử thay đổi

| Phiên bản | Ngày | Người thay đổi | Mô tả |
|---|---|---|---|
| 1.0 | 12/03/2026 | AT Team | Bản BRD đầu tiên, rút gọn từ SRS v2.1 |

---

# MỤC LỤC

- [1. Tổng quan dự án](#1-tổng-quan-dự-án)
- [2. Bối cảnh kinh doanh](#2-bối-cảnh-kinh-doanh)
- [3. Các bên liên quan](#3-các-bên-liên-quan)
- [4. Phạm vi sản phẩm](#4-phạm-vi-sản-phẩm)
- [5. Yêu cầu nghiệp vụ — Phía Creator](#5-yêu-cầu-nghiệp-vụ--phía-creator)
- [6. Yêu cầu nghiệp vụ — Phía Quản trị (Admin)](#6-yêu-cầu-nghiệp-vụ--phía-quản-trị-admin)
- [7. Quy trình vận hành tự động](#7-quy-trình-vận-hành-tự-động)
- [8. Quy tắc nghiệp vụ](#8-quy-tắc-nghiệp-vụ)
- [9. Vòng đời trạng thái các đối tượng chính](#9-vòng-đời-trạng-thái-các-đối-tượng-chính)
- [10. Yêu cầu bảo mật & tuân thủ](#10-yêu-cầu-bảo-mật--tuân-thủ)
- [11. Giả định & Ràng buộc](#11-giả-định--ràng-buộc)
- [12. Tiêu chí chấp nhận tổng thể](#12-tiêu-chí-chấp-nhận-tổng-thể)
- [Phụ lục A: Bảng thuật ngữ](#phụ-lục-a-bảng-thuật-ngữ)

---

# 1. Tổng quan dự án

## 1.1. Mục tiêu kinh doanh

**Techcombank Influencer Platform (T-Fluencers)** là nền tảng quản lý chiến dịch Influencer Marketing, được xây dựng nhằm:

1. **Tối ưu hóa chiến dịch truyền thông** — Quản lý tập trung các chiến dịch thử thách, theo dõi nội dung Creator đăng tải, đo lường hiệu quả qua dữ liệu thực tế (views, engagement).
2. **Quản lý tài chính minh bạch** — Thiết lập ngân sách, đối soát hoa hồng, chi trả cho Creator theo quy trình rõ ràng, kiểm toán được.
3. **Mở rộng mạng lưới Creator** — Cho phép Creator tự đăng ký, liên kết kênh MXH, tham gia chiến dịch và nhận hoa hồng qua nền tảng.
4. **Cung cấp dữ liệu phân tích** — Dashboard báo cáo giúp Techcombank nắm bắt hiệu quả chiến dịch, so sánh xu hướng, đánh giá ROI.

## 1.2. Kết quả mong đợi

| Kết quả | Chỉ số đo lường |
|---|---|
| Quản lý chiến dịch tập trung | 100% chiến dịch được tạo, quản lý và đối soát trên nền tảng |
| Quy trình duyệt nội dung hiệu quả | Thời gian duyệt content trung bình ≤ 1 ngày làm việc |
| Đối soát & thanh toán chính xác | Sai lệch đối soát = 0%; thanh toán qua quy trình kiểm toán |
| Mạng lưới Creator mở rộng | Hỗ trợ ≥ 100.000 Creator đăng ký, 5 nền tảng MXH |
| Báo cáo kịp thời | Dashboard cập nhật dữ liệu tối đa mỗi 4 giờ |

---

# 2. Bối cảnh kinh doanh

Techcombank cần một nền tảng công nghệ để quản lý hoạt động Influencer Marketing, thay vì vận hành thủ công qua email/spreadsheet. Nền tảng do **AccessTrade (AT)** phát triển và vận hành, phục vụ 3 nhóm người dùng chính.

### Mô hình vận hành 3 bên

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   TECHCOMBANK   │         │   ACCESSTRADE    │         │    CREATOR      │
│   (Chủ sở hữu) │         │   (Vận hành)     │         │  (Người dùng)   │
├─────────────────┤         ├──────────────────┤         ├─────────────────┤
│ • Định hướng    │ ──────→ │ • Phát triển     │ ──────→ │ • Đăng ký       │
│   chiến lược    │         │   hệ thống       │         │ • Tham gia      │
│ • Giám sát      │         │ • Vận hành        │         │   thử thách     │
│   qua báo cáo   │         │   chiến dịch     │         │ • Đăng nội dung │
│ • Duyệt chi     │ ←────── │ • Duyệt content  │ ←────── │ • Nhận hoa hồng │
│   ngân sách     │         │ • Đối soát       │         │   (qua AT)      │
│                 │         │ • Chi trả hoa hồng│         │                 │
└─────────────────┘         └──────────────────┘         └─────────────────┘
```

**Lưu ý quan trọng:**
- TCB **không** trực tiếp thao tác trên hệ thống (trừ xem báo cáo dashboard).
- TCB **không** thanh toán trực tiếp cho Creator. TCB cấp ngân sách cho AT → AT đối soát & chi trả.
- AT chịu trách nhiệm toàn bộ vận hành: duyệt content, đối soát hoa hồng, thanh toán.

---

# 3. Các bên liên quan

| Bên liên quan | Vai trò | Nhu cầu chính |
|---|---|---|
| **Techcombank (TCB)** | Chủ sở hữu, định hướng chiến lược | Giám sát hiệu quả chiến dịch qua báo cáo; kiểm soát ngân sách |
| **AccessTrade (AT) — Vận hành** | Đội ngũ vận hành chiến dịch | Duyệt content nhanh chóng; đối soát chính xác; quản lý Creator hiệu quả |
| **AccessTrade (AT) — Kỹ thuật** | Đội ngũ phát triển & bảo trì | Hệ thống ổn định, dễ bảo trì, mở rộng |
| **Creator (Influencer)** | Nhà sáng tạo nội dung | Đăng ký dễ dàng; tham gia thử thách nhanh; nhận hoa hồng minh bạch |
| **Đối tác (Partner/Brand)** | Thương hiệu tham gia chiến dịch matching | Tìm được Creator phù hợp; đánh giá hiệu quả hợp tác |

---

# 4. Phạm vi sản phẩm

## 4.1. Trong phạm vi

| # | Nhóm chức năng | Mô tả |
|---|---|---|
| 1 | Quản lý Creator | Đăng ký, đăng nhập, hồ sơ cá nhân, liên kết kênh MXH, eKYC, ký hợp đồng |
| 2 | Quản lý chiến dịch | Tạo, cấu hình, kích hoạt, kết thúc chiến dịch/thử thách |
| 3 | Quản lý nội dung | Submit content, duyệt, từ chối, import, crawl thống kê |
| 4 | Tài chính | Cơ cấu thưởng, ngân sách, đối soát hoa hồng, thanh toán |
| 5 | Phân tích & Báo cáo | Dashboard KPI, biểu đồ, leaderboard, phân khúc Creator |
| 6 | Quản trị hệ thống | Quản lý nhân viên, phân quyền, CMS, thông báo, audit log |
| 7 | Hệ thống tự động | Crawl video, tính hoa hồng, giám sát budget, auto reject, AI content review |

## 4.2. Ngoài phạm vi

| # | Hạng mục | Lý do |
|---|---|---|
| 1 | Thanh toán trực tiếp TCB → Creator | Thanh toán qua Service TOS của AccessTrade |
| 2 | Ứng dụng mobile native | Hiện tại chỉ hỗ trợ responsive web |
| 3 | Tích hợp CRM của TCB | Không trong phạm vi hợp đồng hiện tại |
| 4 | Quản lý hợp đồng giữa TCB và AT | Xử lý ngoài hệ thống |

---

# 5. Yêu cầu nghiệp vụ — Phía Creator

## BRQ-01: Đăng nhập bằng tài khoản mạng xã hội

**Mô tả:** Creator đăng nhập hệ thống bằng tài khoản Google hoặc TikTok — không cần tạo tài khoản thủ công.

**Lý do:** Giảm rào cản đăng ký, tăng tỷ lệ chuyển đổi. Creator không cần nhớ thêm mật khẩu mới.

**Kết quả mong đợi:**
- Creator chọn nền tảng → xác thực → vào hệ thống trong < 30 giây
- Tài khoản mới tự động tạo khi đăng nhập lần đầu
- Không lưu trữ access token của bên thứ ba

**Tiêu chí chấp nhận:**
- [ ] Đăng nhập Google thành công, hiển thị tên + avatar
- [ ] Đăng nhập TikTok thành công
- [ ] Tài khoản mới tạo tự động khi chưa tồn tại
- [ ] Không tạo trùng khi đăng nhập lại
- [ ] Từ chối cấp quyền → hiển thị thông báo lỗi

---

## BRQ-02: Cập nhật hồ sơ cá nhân

**Mô tả:** Creator xem và chỉnh sửa thông tin cá nhân: avatar, tên, giới tính, ngày sinh, email.

**Lý do:** Đảm bảo thông tin chính xác cho mục đích liên lạc, đối soát và thanh toán.

**Tiêu chí chấp nhận:**
- [ ] Hiển thị đầy đủ thông tin hiện tại
- [ ] Cập nhật thành công, phản ánh ngay trên giao diện
- [ ] Validate: tên không trống, email đúng định dạng, ảnh JPG/PNG ≤ 5MB

---

## BRQ-03: Đăng ký kênh mạng xã hội

**Mô tả:** Creator đăng ký và xác thực kênh MXH (TikTok, YouTube, Facebook, Instagram, Threads) để tham gia chiến dịch.

**Lý do:** Xác minh quyền sở hữu kênh và kiểm tra điều kiện tham gia (số followers) trước khi cho phép Creator tham gia.

**Quy trình theo nền tảng:**

| Nền tảng | Phương thức xác thực | Thời gian trả kết quả |
|---|---|---|
| TikTok | OAuth 2.0 tự động | Ngay lập tức |
| YouTube | URL + hashtag + YouTube API | Ngay lập tức |
| Facebook / Instagram / Threads | URL + hashtag + kiểm duyệt | ≤ 1 ngày làm việc |

**Tiêu chí chấp nhận:**
- [ ] Mỗi nền tảng hoạt động đúng quy trình xác thực riêng
- [ ] Kiểm tra điều kiện followers (ngưỡng cấu hình)
- [ ] Không đăng ký trùng cùng nền tảng
- [ ] Hashtag định danh duy nhất cho mỗi Creator

---

## BRQ-04: Tham gia thử thách

**Mô tả:** Creator gửi link video để tham gia một thử thách cụ thể.

**Lý do:** Đây là hành động chính tạo ra nội dung cho chiến dịch. Cần đảm bảo nội dung hợp lệ trước khi vào quy trình duyệt.

**Điều kiện tiên quyết:** Đã đăng nhập + có hồ sơ social đã duyệt + thử thách còn mở.

**Tiêu chí chấp nhận:**
- [ ] Submit thành công với link video hợp lệ + hashtag bắt buộc
- [ ] Chặn khi chưa có hồ sơ social / thử thách đã kết thúc
- [ ] Validate: link truy cập được, nền tảng khớp hồ sơ, có hashtag
- [ ] Hỗ trợ tham gia bằng mã code (invite-only)
- [ ] Không submit trùng link video

---

## BRQ-05: Theo dõi thử thách đã tham gia

**Mô tả:** Creator xem lại toàn bộ thử thách đã tham gia, trạng thái video, thông số hiệu suất và mốc hoa hồng.

**Lý do:** Minh bạch thông tin, tạo động lực cho Creator theo dõi và cải thiện hiệu suất.

**Tiêu chí chấp nhận:**
- [ ] Hiển thị danh sách thử thách, video, trạng thái (PENDING/APPROVED/REJECTED)
- [ ] Hiển thị thông số: lượt xem, tương tác, mốc hoa hồng đã đạt
- [ ] Phân quyền: chỉ xem được thông tin của mình

---

## BRQ-06: Bảng xếp hạng (Leaderboard)

**Mô tả:** Hiển thị bảng xếp hạng Creator và Content trên trang thử thách.

**Lý do:** Tạo tính cạnh tranh, khuyến khích Creator tham gia tích cực hơn.

**Tiêu chí chấp nhận:**
- [ ] Leaderboard Creator: tên, avatar, thông số tương tác
- [ ] Leaderboard Content: thumbnail, views, engagement
- [ ] Dữ liệu cập nhật định kỳ

---

## BRQ-07: Quản lý số dư & Dòng tiền

**Mô tả:** Creator xem số dư hoa hồng, lịch sử giao dịch, và quản lý thẻ ngân hàng.

**Lý do:** Minh bạch tài chính. Creator cần biết mình đã nhận bao nhiêu, còn bao nhiêu chưa thanh toán.

**Tiêu chí chấp nhận:**
- [ ] Hiển thị 3 loại số dư: đã đối soát, chưa thanh toán, đã thanh toán
- [ ] Lịch sử dòng tiền đầy đủ, hỗ trợ phân trang
- [ ] Thêm/sửa thẻ ngân hàng, đặt thẻ mặc định

---

## BRQ-08: eKYC & Ký hợp đồng điện tử

**Mô tả:** Creator xác minh danh tính bằng CCCD và ký hợp đồng điện tử trước khi nhận hoa hồng.

**Lý do:** Yêu cầu pháp lý — cần xác minh danh tính và có hợp đồng trước khi chi trả.

**Quy trình:**
1. Upload ảnh CCCD → OCR trích xuất thông tin → xác nhận → gửi xác minh
2. Admin duyệt eKYC
3. Creator cung cấp thông tin thanh toán → ký hợp đồng trên AccessTrade (ctv.scalef.com)

**Tiêu chí chấp nhận:**
- [ ] OCR trích xuất chính xác từ ảnh CCCD
- [ ] Quy trình eKYC: PENDING → APPROVED/REJECTED
- [ ] Ký hợp đồng thành công qua redirect sang AccessTrade
- [ ] Tải hợp đồng PDF sau khi ký

---

## BRQ-09: Thông báo đa kênh

**Mô tả:** Creator nhận thông báo về kết quả duyệt content, hoa hồng, cập nhật chiến dịch qua nhiều kênh.

**Lý do:** Đảm bảo Creator không bỏ lỡ thông tin quan trọng.

**Kênh thông báo:** In-app, Push notification (FCM), Email (SendGrid), SMS (eSMS).

**Tiêu chí chấp nhận:**
- [ ] Thông báo in-app hiển thị đúng, đánh dấu đã đọc
- [ ] Push notification gửi đến thiết bị đã đăng ký
- [ ] Email gửi cho thông báo quan trọng

---

## BRQ-10: Trang giới thiệu & Nội dung

**Mô tả:** Hiển thị thông tin giới thiệu chương trình, thể lệ, tin tức — quản lý từ CMS.

**Tiêu chí chấp nhận:**
- [ ] Trang chủ hiển thị banner, thông tin chương trình, danh sách thử thách
- [ ] Bài viết/thể lệ hiển thị đầy đủ nội dung rich text
- [ ] Tin tức cập nhật, phân trang

---

## BRQ-11: Thống kê cá nhân & Mã giới thiệu

**Mô tả:** Creator xem thống kê hiệu suất cá nhân và quản lý chương trình giới thiệu.

**Tiêu chí chấp nhận:**
- [ ] Thống kê: tổng content, views, hoa hồng
- [ ] Danh sách người được giới thiệu
- [ ] Nhập mã giới thiệu hợp lệ → liên kết thành công

---

# 6. Yêu cầu nghiệp vụ — Phía Quản trị (Admin)

## BRQ-12: Đăng nhập & Quản lý nhân viên

**Mô tả:** Admin đăng nhập bằng email/mật khẩu. Hệ thống hỗ trợ mời nhân viên, quên mật khẩu, phân quyền RBAC.

**Vai trò phân quyền:**

| Vai trò | Quyền hạn |
|---|---|
| Root | Toàn quyền hệ thống |
| Admin | Quản lý chiến dịch, content, user, đối soát, thanh toán |
| Campaign Owner | Chỉ quản lý chiến dịch được gán |
| Collaborator | Quyền hạn giới hạn |

**Tiêu chí chấp nhận:**
- [ ] Đăng nhập email/password thành công
- [ ] Quên mật khẩu → reset qua email
- [ ] Mời nhân viên (đơn lẻ + hàng loạt)
- [ ] RBAC hoạt động: mỗi vai trò chỉ truy cập đúng phạm vi

---

## BRQ-13: Dashboard & Báo cáo

**Mô tả:** Cung cấp cái nhìn tổng quan về hiệu quả chiến dịch cho AT và TCB.

**2 giao diện dashboard:**
1. **Cổng quản trị (Admin)**: Tổng content, views, tiền, biểu đồ — lọc theo chiến dịch, thời gian
2. **Dashboard phân tích (Next.js)**: KPI nâng cao, 7+ loại biểu đồ, phân tích xu hướng, phân khúc Creator, đa ngôn ngữ (vi/en)

**Tiêu chí chấp nhận:**
- [ ] KPI tổng quan chính xác, khớp dữ liệu
- [ ] Bộ lọc nâng cao hoạt động (chiến dịch, nền tảng, thời gian)
- [ ] Biểu đồ hiển thị đúng
- [ ] Chuyển ngôn ngữ vi↔en chính xác

---

## BRQ-14: Quản lý chiến dịch / Thử thách

**Mô tả:** Admin tạo, cấu hình, kích hoạt và kết thúc chiến dịch truyền thông.

**Thông tin chiến dịch:** Tên, mô tả, ảnh bìa, thời gian, loại chiến dịch, điều kiện tham gia, hashtag bắt buộc.

**Cơ cấu thưởng:**
- **BY_VIEW**: Hoa hồng theo mốc lượt xem (vd: 10K views = 500.000đ)
- **BY_TASK**: Hoa hồng theo nhiệm vụ cố định

**Vòng đời:** DRAFT → ACTIVE → ENDED / CANCELLED

**Tiêu chí chấp nhận:**
- [ ] Tạo chiến dịch với đầy đủ thông tin + cơ cấu thưởng
- [ ] Kích hoạt → Creator nhìn thấy và tham gia được
- [ ] Kết thúc → Creator không submit content mới
- [ ] Chặn submit / chặn tạo thưởng khi cần

---

## BRQ-15: Duyệt nội dung (Content Moderation)

**Mô tả:** Admin xem, duyệt, từ chối nội dung của Creator. Hỗ trợ duyệt đơn lẻ, hàng loạt, import, ghim.

**Quy trình duyệt:**
1. Creator submit → PENDING
2. Admin duyệt → APPROVED (bắt đầu crawl thống kê) / REJECTED (kèm lý do bắt buộc)

**Tính năng bổ sung:** Import từ Excel, crawl thông tin, gắn cờ cảnh báo, quản lý transcript, đánh giá AI.

**Tiêu chí chấp nhận:**
- [ ] Duyệt/Từ chối đơn lẻ + hàng loạt
- [ ] Từ chối phải có lý do
- [ ] Import content từ Excel, báo lỗi dòng sai
- [ ] Mọi thao tác ghi audit log

---

## BRQ-16: Duyệt hồ sơ social & Quản lý Creator

**Mô tả:** Admin duyệt/từ chối hồ sơ MXH của Creator, quản lý thông tin user và influencer.

**Tiêu chí chấp nhận:**
- [ ] Duyệt/Từ chối/Hủy duyệt (Revoke) hồ sơ social — kèm lý do và thông báo
- [ ] Xem chi tiết user: thông tin cá nhân, hồ sơ social, lịch sử tham gia
- [ ] Khóa/Mở khóa tài khoản Creator
- [ ] Xem influencer profile enriched (followers, engagement, nhân khẩu học)

---

## BRQ-17: eKYC & Hợp đồng (phía Admin)

**Mô tả:** Admin duyệt/từ chối yêu cầu xác minh danh tính và hợp đồng của Creator.

**Tiêu chí chấp nhận:**
- [ ] Xem danh sách + chi tiết eKYC (ảnh CCCD, thông tin OCR)
- [ ] Duyệt/Từ chối eKYC + thông báo cho Creator
- [ ] Từ chối hợp đồng nếu cần

---

## BRQ-18: Đối soát hoa hồng (Reconciliation)

**Mô tả:** Admin thực hiện đối soát hoa hồng cho Creator theo từng chiến dịch, đảm bảo tính chính xác trước khi thanh toán.

**Quy trình:**
1. Tạo đợt đối soát → chọn thử thách, loại hoa hồng, thời gian
2. Hệ thống tổng hợp: tổng user, video, tiền
3. Đánh giá: checklist tự động + AI (tham khảo) + duyệt thủ công
4. Xuất Excel kiểm tra
5. Kết thúc đợt → khóa, cập nhật số dư Creator

**Vòng đời:** DRAFT → IN_PROGRESS → REVIEWED → CLOSED / CANCELLED

**Tiêu chí chấp nhận:**
- [ ] Tạo đợt, xem chi tiết 4 tab (Nội dung, Mốc thưởng, Thưởng bổ sung, Tổng quan)
- [ ] Đánh giá checklist + quick approve/reject
- [ ] Xuất Excel đúng cấu trúc
- [ ] Kết thúc đợt → số dư Creator cập nhật chính xác
- [ ] Tổng tiền đối soát khớp giữa giao diện và Excel

---

## BRQ-19: Thanh toán (Transfer)

**Mô tả:** Admin tạo đợt thanh toán cho Creator đã đối soát, đẩy lệnh rút tiền qua AccessTrade.

**Quy trình:**
1. Tạo đợt → tổng hợp Creator có hoa hồng chưa thanh toán
2. Xem chi tiết + xuất Excel
3. Xác nhận → đẩy lệnh rút tiền sang Service TOS
4. Kết thúc đợt → cập nhật số dư

**Vòng đời:** DRAFT → CONFIRMED → PROCESSING → COMPLETED / FAILED (retry tự động)

**Tiêu chí chấp nhận:**
- [ ] Tạo đợt, tổng hợp chính xác
- [ ] Xuất Excel
- [ ] Push sang TOS thành công / retry khi thất bại
- [ ] Kết thúc → số dư "đã thanh toán" cập nhật

---

## BRQ-20: Quản lý ngân sách chiến dịch

**Mô tả:** Admin cấu hình budget cap cho mỗi chiến dịch. Hệ thống tự động giám sát và hành động khi vượt ngưỡng.

**Ngưỡng tự động:**

| Ngưỡng | Hành động |
|---|---|
| 75% | Cảnh báo email cho Admin |
| 95% | Chặn Creator submit content mới |
| 100% | Ngừng tính hoa hồng dự kiến |

**Tiêu chí chấp nhận:**
- [ ] Tạo budget cap, hiển thị % sử dụng
- [ ] Cảnh báo gửi đúng ngưỡng
- [ ] Chặn submit tự động ở 95%
- [ ] Ngừng tính hoa hồng ở 100%

---

## BRQ-21: Quản lý nội dung CMS

**Mô tả:** Admin soạn thảo bài viết, tin tức, thể lệ, quick action — hiển thị trên Cổng Influencer.

**Tiêu chí chấp nhận:**
- [ ] Tạo/sửa bài viết bằng rich text editor
- [ ] Quản lý tin tức (tạo, sửa, clone, đổi trạng thái)
- [ ] Quản lý tag phân loại
- [ ] Quick Action hiển thị trên Cổng Influencer

---

## BRQ-22: Thông báo (Admin → Creator)

**Mô tả:** Admin tạo và gửi thông báo đến Creator qua nhiều kênh (in-app, push, email).

**Tiêu chí chấp nhận:**
- [ ] Tạo thông báo + chọn đối tượng nhận (segment hoặc toàn bộ)
- [ ] Gửi đa kênh
- [ ] Clone thông báo để tái sử dụng
- [ ] Theo dõi trạng thái gửi

---

## BRQ-23: Phân khúc Creator (Segments)

**Mô tả:** Admin phân nhóm Creator để lọc, gửi thông báo, cấu hình chiến dịch.

**Tiêu chí chấp nhận:**
- [ ] Tạo segment, thêm/xóa user
- [ ] Import danh sách từ Excel
- [ ] Sử dụng segment khi gửi thông báo / lọc user

---

## BRQ-24: Đối tác & Matching Influencer

**Mô tả:** Quản lý đối tác (Partner) và chạy thuật toán matching tìm Creator phù hợp cho chiến dịch.

**Tiêu chí chấp nhận:**
- [ ] CRUD đối tác
- [ ] Tạo campaign cho đối tác
- [ ] Chạy matching → danh sách Creator phù hợp
- [ ] Thêm/Xóa Creator khỏi campaign

---

## BRQ-25: Đánh giá & Xếp hạng Creator

**Mô tả:** Admin/Brand đánh giá Creator sau chiến dịch theo nhiều tiêu chí.

**Tiêu chí đánh giá:** Chất lượng nội dung, Đúng deadline, Tuân thủ brief, Thái độ hợp tác, Hiệu quả tương tác (thang 1-5).

**Tiêu chí chấp nhận:**
- [ ] Chấm điểm từng tiêu chí + nhận xét
- [ ] Xem thống kê rating tổng hợp
- [ ] Không đánh giá trùng (1 reviewer/profile/campaign)

---

## BRQ-26: Các chức năng hỗ trợ

| Chức năng | Mô tả | Tiêu chí chấp nhận |
|---|---|---|
| **Import hiệu suất** | Upload CSV dữ liệu hiệu suất → hiển thị xu hướng trên dashboard | Import thành công, biểu đồ cập nhật |
| **Quản lý mã (Code)** | Tạo/import mã tham gia thử thách (invite code) | Tạo mã, Creator dùng mã tham gia, mã không trùng |
| **Xuất dữ liệu** | Xuất Excel (đối soát, thanh toán, analytics) qua background job | Tạo file → presigned URL 30s → tải thành công |
| **Nhật ký kiểm toán** | Ghi log mọi thao tác quan trọng | Log chỉ đọc, lọc theo thời gian/người/hành động |

---

# 7. Quy trình vận hành tự động

| # | Quy trình | Tần suất | Mô tả |
|---|---|---|---|
| 1 | **Crawl thống kê video** | Mỗi 4 giờ | Thu thập views, engagement từ TikTok, YouTube, Facebook |
| 2 | **Tính hoa hồng** | Định kỳ (cấu hình) | So khớp video APPROVED với cơ cấu thưởng → tính hoa hồng dự kiến |
| 3 | **Giám sát ngân sách** | Mỗi 30 phút | Kiểm tra % budget → cảnh báo/chặn/ngừng tương ứng |
| 4 | **Auto reject content** | Hàng ngày 03:45 | Tự động từ chối content không hợp lệ |
| 5 | **Auto reject not found** | Hàng ngày 04:30 | Từ chối content không tìm thấy trên nền tảng |
| 6 | **Warning tag** | Hàng ngày 05:30 | Gắn cờ cảnh báo content vi phạm |
| 7 | **Retry thanh toán** | Mỗi 30 phút | Retry đẩy lệnh rút tiền sang TOS khi thất bại |
| 8 | **Kiểm tra hồ sơ social** | Mỗi giờ | Kiểm tra trạng thái kênh MXH |
| 9 | **Đánh giá AI** | Khi có transcript | Vertex AI đánh giá chất lượng content (tham khảo, không tự động duyệt) |

---

# 8. Quy tắc nghiệp vụ

## 8.1. Hoa hồng

| # | Quy tắc |
|---|---|
| BR-1 | Chỉ content **APPROVED** mới tính hoa hồng |
| BR-2 | Hoa hồng **BY_VIEW**: mỗi mốc views có số tiền tương ứng (cấu hình trong Event Reward) |
| BR-3 | Hoa hồng **BY_TASK**: hoàn thành nhiệm vụ → nhận hoa hồng cố định |
| BR-4 | Mốc thưởng **tích lũy**: đạt mốc cao → nhận hết các mốc thấp hơn chưa nhận |
| BR-5 | **Không tính trùng**: 1 video chỉ tính 1 lần cho mỗi mốc |
| BR-6 | Hoa hồng tính tự động = **dự kiến**. Chỉ thành **thực nhận** sau đối soát xác nhận |
| BR-7 | Số tiền **làm tròn xuống** đến đơn vị VNĐ |

## 8.2. Ngân sách

| # | Quy tắc |
|---|---|
| BR-8 | `Budget usage = (Đã đối soát + Dự kiến) / Budget cap × 100%` |
| BR-9 | **75%** → Cảnh báo email Admin |
| BR-10 | **95%** → Chặn submit content mới |
| BR-11 | **100%** → Ngừng lưu hoa hồng dự kiến mới |
| BR-12 | Kiểm tra budget **trước** khi lưu hoa hồng (mỗi lần cron chạy) |

## 8.3. Đối soát & Thanh toán

| # | Quy tắc |
|---|---|
| BR-13 | Chỉ đối soát content **APPROVED** |
| BR-14 | Đợt đối soát **CLOSED** không thể mở lại |
| BR-15 | Khi đóng đợt → snapshot dữ liệu, cập nhật số dư Creator |
| BR-16 | Chỉ thanh toán hoa hồng **đã đối soát** |
| BR-17 | Creator phải có **eKYC + hợp đồng + thẻ ngân hàng** mới nhận thanh toán |
| BR-18 | Push TOS thất bại → retry mỗi 30 phút |

## 8.4. Hồ sơ social & Content

| # | Quy tắc |
|---|---|
| BR-19 | Mỗi nền tảng tối đa **1 hồ sơ APPROVED** |
| BR-20 | Hashtag xác minh quyền sở hữu (hệ thống sinh duy nhất) |
| BR-21 | Ngưỡng followers cấu hình theo nền tảng/chiến dịch |
| BR-22 | Video phải **public**, chứa hashtag bắt buộc, nền tảng khớp hồ sơ |
| BR-23 | Content không tìm thấy trên nền tảng → auto reject |
| BR-24 | Content APPROVED → bắt đầu crawl thống kê mỗi 4 giờ |

---

# 9. Vòng đời trạng thái các đối tượng chính

## 9.1. Content (Bài tham gia)

```
Creator submit → [PENDING] → Admin duyệt → [APPROVED] → Crawl thống kê
                     ↓                            ↓
              Admin từ chối               Phát hiện vi phạm
                     ↓                            ↓
                [REJECTED] ← ─ ─ ─ ─ ─ ─ ─ [REJECTED]
                     ↓
           Creator sửa & gửi lại → [PENDING]
```

- Hệ thống tự động reject: content không hợp lệ hoặc không tìm thấy trên nền tảng
- REJECTED → Creator có thể sửa và gửi lại nếu thử thách còn mở

## 9.2. Đối soát (Reconciliation)

```
[DRAFT] → [IN_PROGRESS] → [REVIEWED] → [CLOSED] (terminal — không mở lại)
               ↓
          [CANCELLED]
```

## 9.3. Thanh toán (Transfer)

```
[DRAFT] → [CONFIRMED] → [PROCESSING] → [COMPLETED] (terminal)
               ↓                ↓
          [CANCELLED]       [FAILED] → retry → [PROCESSING]
```

## 9.4. Chiến dịch (Event)

```
[DRAFT] → [ACTIVE] → [ENDED] (terminal)
               ↓
          [CANCELLED]
```

## 9.5. Hồ sơ Social

```
[PENDING] → [APPROVED] → [REVOKED] (khi vi phạm)
     ↓
[REJECTED] → Creator gửi lại → [PENDING]
```

## 9.6. eKYC

```
[PENDING] → [APPROVED]
     ↓
[REJECTED] → Creator gửi lại → [PENDING]
```

---

# 10. Yêu cầu bảo mật & tuân thủ

## 10.1. Phân loại dữ liệu

| Mức | Ví dụ | Biện pháp bảo vệ |
|---|---|---|
| **Public** | Banner, tin tức, marketing | Kiểm soát chỉnh sửa |
| **Internal** | Cấu hình, quy tắc hoa hồng | Giới hạn truy cập nội bộ, log thay đổi |
| **Confidential** | Họ tên, email, phone, hoa hồng | Phân quyền RBAC, audit log |
| **Restricted** | CCCD, hợp đồng, số tài khoản | Mã hóa lưu trữ + truyền tải, hạn chế truy cập |

## 10.2. Tuân thủ pháp luật

- **Nghị định 13/2023/NĐ-CP** (Việt Nam): Bảo vệ dữ liệu cá nhân
- **Không lưu** access token OAuth của bên thứ ba
- **Mã hóa** dữ liệu nhạy cảm (CCCD, số tài khoản): AES-256
- **Presigned URL** cho file download: hiệu lực 30 giây
- **Audit log**: Ghi nhận mọi thao tác quan trọng, không thể xóa/sửa

## 10.3. Phân quyền

- RBAC 4 cấp: Root / Admin / Campaign Owner / Collaborator
- Mọi API yêu cầu JWT authentication
- Creator chỉ xem được thông tin của mình

---

# 11. Giả định & Ràng buộc

## 11.1. Giả định

1. Creator có thiết bị kết nối Internet và trình duyệt web hiện đại.
2. Creator đã có tài khoản MXH hợp lệ trước khi đăng ký.
3. API các nền tảng MXH khả dụng và ổn định.
4. Dịch vụ AT-Core và Service TOS hoạt động liên tục; nếu gián đoạn, hệ thống retry tự động.
5. Đội vận hành AT duyệt hồ sơ social và content trong vòng 1 ngày làm việc.

## 11.2. Ràng buộc

1. Hệ thống web responsive, chưa có ứng dụng mobile native.
2. Ngôn ngữ: Tiếng Việt (Cổng Influencer, Admin); Tiếng Anh bổ sung trên Dashboard phân tích.
3. Thanh toán hoa hồng phải qua Service TOS (AccessTrade), không chi trả trực tiếp.
4. Tuân thủ Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân.

---

# 12. Tiêu chí chấp nhận tổng thể

Dự án được nghiệm thu khi đáp ứng đầy đủ các tiêu chí sau:

| # | Tiêu chí | Điều kiện đạt |
|---|---|---|
| 1 | **Chức năng Creator** | 11 nhóm chức năng (BRQ-01 → BRQ-11) hoạt động đúng theo tiêu chí chấp nhận |
| 2 | **Chức năng Admin** | 15 nhóm chức năng (BRQ-12 → BRQ-26) hoạt động đúng theo tiêu chí chấp nhận |
| 3 | **Quy trình tự động** | 9 cron job / background job chạy đúng tần suất và xử lý chính xác |
| 4 | **Quy tắc nghiệp vụ** | 24 quy tắc (BR-1 → BR-24) được kiểm chứng |
| 5 | **Vòng đời trạng thái** | 6 state diagram hoạt động đúng: Content, Reconciliation, Transfer, Event, Social, eKYC |
| 6 | **Bảo mật** | Dữ liệu nhạy cảm mã hóa, RBAC phân quyền đúng, audit log hoạt động |
| 7 | **Báo cáo** | Dashboard hiển thị chính xác, bộ lọc hoạt động, xuất Excel khớp dữ liệu |
| 8 | **Tích hợp bên ngoài** | TikTok, Google OAuth hoạt động. Service TOS: eKYC + thanh toán hoạt động |

---

# Phụ lục A: Bảng thuật ngữ

| Thuật ngữ | Định nghĩa |
|---|---|
| **Creator / Influencer** | Người dùng cuối — nhà sáng tạo nội dung tham gia chiến dịch |
| **Thử thách (Event)** | Một chiến dịch truyền thông mà Creator tham gia, đăng nội dung và nhận hoa hồng |
| **Content** | Bài tham gia của Creator (thường là video trên MXH) cho một thử thách |
| **Đối soát (Reconciliation)** | Quy trình kiểm tra, xác nhận hoa hồng phát sinh cho Creator |
| **Thanh toán (Transfer)** | Đợt chi trả hoa hồng đã đối soát cho Creator |
| **Hồ sơ social (User Social)** | Tài khoản MXH đã đăng ký và xác thực trên hệ thống |
| **eKYC** | Xác minh danh tính điện tử bằng CCCD/CMND |
| **AT-Core** | Dịch vụ trung gian của AccessTrade, cung cấp dữ liệu enrichment cho influencer profile |
| **Service TOS** | Hệ thống cộng tác viên AccessTrade, xử lý ký hợp đồng và rút tiền |
| **Budget Cap** | Ngưỡng ngân sách tối đa cho một chiến dịch |
| **Mốc thưởng (Milestone)** | Ngưỡng hiệu suất (vd: 10.000 views) để Creator nhận hoa hồng tương ứng |
| **Segment** | Nhóm phân khúc Creator phục vụ lọc, gửi thông báo, quản lý chiến dịch |
| **RBAC** | Role-Based Access Control — phân quyền dựa trên vai trò |
| **BY_VIEW** | Loại hoa hồng tính theo mốc lượt xem video |
| **BY_TASK** | Loại hoa hồng tính theo nhiệm vụ hoàn thành |
| **Presigned URL** | Link tải file có thời hạn (30 giây), bảo mật truy cập |

---

*Tài liệu yêu cầu nghiệp vụ (BRD) v1.0*
*Ngày: 01/11/2025*
