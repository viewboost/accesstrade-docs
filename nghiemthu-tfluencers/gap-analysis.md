# BÁO CÁO ĐỐI CHIẾU YÊU CẦU — SRS v2.0

### Dự án: **Techcombank Influencer Platform (T-Fluencers)**

**Ngày:** 11/03/2026

**Mục đích:** Đối chiếu danh sách yêu cầu ban đầu (requirements.html) với đặc tả yêu cầu phần mềm (SRS v2.0) để xác định trạng thái triển khai và các hạng mục còn thiếu.

**Tài liệu liên quan:**
- Yêu cầu gốc: `requirements.html`
- Đặc tả phần mềm: `srs-v2.md`

---

## Bảng đối chiếu chi tiết

### Yêu cầu D+10 (Core)

| # | Req Row | Yêu cầu | SRS Mục | Trạng thái | Ghi chú |
|---|---------|---------|---------|-----------|---------|
| 1 | 5 | Đăng ký/Đăng nhập Google, TikTok | §1 | ✅ **ĐẠT** | Mở rộng thêm Facebook, Instagram |
| 2 | 6 | Profile (tạo, chỉnh sửa, avatar) | §2 | ✅ **ĐẠT** | |
| 3 | 7 | Thông số cá nhân | §11 | ✅ **ĐẠT** | Triển khai qua User Statistic API |
| 4 | 8 | Liên kết tài khoản (AT, Google, TikTok, FB) | §3, §8 | ✅ **ĐẠT** | Social linking + AT contract linking |
| 5 | 9 | Xếp hạng creator theo điểm số | §6 | ✅ **ĐẠT** | Leaderboard API per event |
| 6 | 10 | Xếp hạng content | §6 | ✅ **ĐẠT** | Content leaderboard API per event |
| 7 | 11 | Quản lý số dư & rút tiền | §7 | ⚠️ **ĐẠT MỘT PHẦN** | Xem số dư + lịch sử: có. Tạo lệnh rút tiền từ creator: **không triển khai** (xử lý qua admin) |
| 8 | 12 | Giao diện branding TCB | §VI.5 | ✅ **ĐẠT** | Branding đã áp dụng trên frontend |
| 9 | 13 | Quy tắc, hướng dẫn, thể lệ | §10 | ✅ **ĐẠT** | Articles + News CMS |
| 10 | 14 | Thông báo hệ thống | §9 | ✅ **ĐẠT** | In-app + FCM + Email + SMS |
| 11 | 15 | EKYC & ký hợp đồng | §8 | ✅ **ĐẠT** | OCR + eKYC + redirect AT TOS |
| 12 | 16 | Tài khoản thanh toán TCB bắt buộc | §7 | ✅ **ĐẠT** | Bank card management + backend validate chỉ chấp nhận tài khoản Techcombank |
| 13 | 17 | Admin Authentication | §12 | ✅ **ĐẠT** | Email/password + Google OAuth |
| 14 | 18 | Admin Dashboard tổng quan | §14 | ✅ **ĐẠT** | 2 dashboard: Admin + Next.js analytics |
| 15 | 19 | Danh sách content | §16 | ✅ **ĐẠT** | |
| 16 | 20 | Duyệt, hủy content | §16 | ✅ **ĐẠT** | Đơn lẻ + batch |
| 17 | 21 | Xem báo cáo sai phạm | §16 | ✅ **ĐẠT** | Warning tags + transcript review |
| 18 | 22 | Lấy thông tin content | §16, §32 | ✅ **ĐẠT** | Crawl metadata từ nền tảng |
| 19 | 23 | Lấy lượt view, comment, share | §32 | ✅ **ĐẠT** | Cron crawl + content analytic daily |
| 20 | 24 | Kiểm tra link content | §4, §16 | ✅ **ĐẠT** | |
| 21 | 25 | Kiểm tra nội dung content bằng API | §16, §38 | ✅ **ĐẠT** | Crawl + Vertex AI evaluation |
| 22 | 26 | Tạo/Quản lý chiến dịch | §15 | ✅ **ĐẠT** | Full CRUD + schema + category + bonus |
| 23 | 27 | Admin Creator management | §18 | ✅ **ĐẠT** | User + Influencer management |
| 24 | 28 | Admin User management | §18 | ✅ **ĐẠT** | CRUD + ban/unban |
| 25 | 29 | Thông số/Báo cáo chiến dịch | §14 | ✅ **ĐẠT** | Dashboard KPIs + analytics APIs |
| 26 | 30 | Quản lý lịch sử thanh toán | §21 | ✅ **ĐẠT** | Transfer management |
| 27 | 31 | Soạn thảo hướng dẫn/thể lệ | §24 | ✅ **ĐẠT** | Articles + News CMS |
| 28 | 32-37 | Server infrastructure | §VI.4 | ✅ **ĐẠT** | MongoDB, MinIO, monitoring, alerts |
| 29 | 38 | Xuất dữ liệu trên admin | §23 | ✅ **ĐẠT** | Background job + presigned URL |
| 30 | 39 | Phân quyền tài khoản admin | §13 | ✅ **ĐẠT** | RBAC: Root/Admin/Campaign Owner/Collaborator |

### Yêu cầu D+30 (Extended)

| # | Req Row | Yêu cầu | SRS Mục | Trạng thái | Ghi chú |
|---|---------|---------|---------|-----------|---------|
| 31 | 41 | Import dữ liệu chiến dịch/creator | §16, §26, §29 | ✅ **ĐẠT** | Import content, user segments, performance, codes từ Excel |
| 32 | 42 | Doanh thu / Conversion rate | §29 | ❌ **CHƯA ĐẠT** | Chưa có chức năng nhập conversion rate và tính revenue estimation realtime |
| 33 | 43 | Budget management | §22 | ✅ **ĐẠT** | Tạo/giám sát/cảnh báo tự động |

### Yêu cầu D+50 (Advanced)

| # | Req Row | Yêu cầu | SRS Mục | Trạng thái | Ghi chú |
|---|---------|---------|---------|-----------|---------|
| 34 | 45 | Liên kết MXH nâng cao | §3 | ✅ **ĐẠT** | 5 nền tảng: TikTok/YouTube/Facebook/Instagram/Threads |
| 35 | 46 | Lấy thông tin kênh tự động | §32, §39 | ✅ **ĐẠT** | AT-Core enrichment + social crawling (TikTok/YouTube/Facebook) |
| 36 | 47 | Thư viện influencer (bộ lọc, xem) | §18.2, §18.3 | ✅ **ĐẠT** | Influencer list + profiles + conditions |
| 37 | 48 | Chấm điểm đánh giá creator (weighted) | §28 | ✅ **ĐẠT** | Review/Rating system + weighted scoring đã triển khai |

### Yêu cầu D+65 (AI)

| # | Req Row | Yêu cầu | SRS Mục | Trạng thái | Ghi chú |
|---|---------|---------|---------|-----------|---------|
| 38 | 50 | Auto scan & approval content bằng AI | §38 | ⚠️ **ĐẠT MỘT PHẦN** | Transcript extraction + Vertex AI evaluation có. Auto-approval tự động hoàn toàn: chưa |
| 39 | 51 | Quản lý nội dung (AI log, blacklist) | §16, §38 | ❌ **CHƯA ĐẠT** | AI evaluation log có. Upload/quản lý blacklist từ ngữ riêng: chưa có |

---

## Thống kê tổng hợp

| Phân loại | Số lượng | Tỷ lệ |
|-----------|---------|-------|
| ✅ **ĐẠT** | **33 / 39** | **84.6%** |
| ⚠️ **ĐẠT MỘT PHẦN** | **3 / 39** | **7.7%** |
| ❌ **CHƯA ĐẠT** | **3 / 39** | **7.7%** |

### Chi tiết các mục "Đạt một phần"

| # | Yêu cầu | Đã có | Còn thiếu |
|---|---------|-------|-----------|
| 7 | Quản lý số dư & rút tiền | Xem số dư, lịch sử dòng tiền, bank card | Tạo lệnh rút tiền từ giao diện creator — **không triển khai** (xử lý qua admin) |
| 38 | Auto scan content AI | Transcript extraction + Vertex AI evaluation | Luồng auto-approval hoàn toàn tự động — chưa hoàn thiện |
| — | (Ghi chú: #7 — quyết định không triển khai rút tiền phía creator) | | |

### Chi tiết các mục "Chưa đạt"

| # | Yêu cầu | Mô tả |
|---|---------|-------|
| 32 | Doanh thu / Conversion rate (D+30) | Chưa có chức năng nhập conversion rate theo chiến dịch/nhóm creator và tính revenue estimation realtime |
| 39 | Quản lý blacklist từ ngữ (D+65) | Chưa có giao diện upload và quản lý blacklist/keyword list cho kiểm duyệt AI |
| — | (Ghi chú: #32 thuộc D+30, #39 thuộc D+65 — đều ngoài scope core D+10) | |

---

## Tính năng MỞ RỘNG ngoài yêu cầu ban đầu

Hệ thống đã triển khai nhiều tính năng vượt yêu cầu gốc:

| # | Tính năng | Mô tả |
|---|-----------|-------|
| 1 | **Dashboard phân tích nâng cao** (Next.js) | 6+ KPIs, 7+ loại biểu đồ, đa ngôn ngữ vi/en |
| 2 | **Đối tác & Campaign Matching** | Quản lý partner, thuật toán matching influencer |
| 3 | **Đánh giá & Rating Influencer** | Review system cho Admin và Brand |
| 4 | **Phân khúc người dùng** (Segments) | Phân nhóm creator, import Excel |
| 5 | **Mã tham gia** (Code Management) | Promo code cho thử thách invite-only |
| 6 | **Hệ thống checklist đối soát** | Classification, quick approve/reject, override |
| 7 | **Vertex AI Content Evaluation** | Đánh giá nội dung bằng Gemini AI |
| 8 | **Multi-channel Notification** | In-app + FCM + Email + SMS + Telegram |
| 9 | **Influencer Profile Enrichment** | AT-Core integration cho nhân khẩu học |
| 10 | **Performance Data Import** | Import CSV dữ liệu hiệu suất |
| 11 | **Mã giới thiệu (Referral)** | Hệ thống referral code |
| 12 | **Event Bonus** | Thưởng bổ sung ngoài hoa hồng cơ bản |
| 13 | **Instagram & Threads support** | Mở rộng nền tảng MXH |
| 14 | **Staff invite system** | Mời nhân viên qua email + bulk invite |

---

*Báo cáo đối chiếu yêu cầu — SRS v2.0*
*Ngày: 11/03/2026*
