# Cam kết Dữ liệu Hồ sơ Creator

> **Vai trò tài liệu:** Cam kết với AccessTrade về phạm vi dữ liệu mà CRM at-core sẽ cung cấp cho mỗi creator, dựa trên influence-meter (Diso đã có sẵn) và các nền tảng social public.
> **Cập nhật:** 2026-05-04
> **Nguồn:** `influence-meter` backend (sản phẩm Diso đang vận hành cho Techcombank dashboard)

---

## Mục đích cam kết

Khi AccessTrade quyết định triển khai CRM at-core, đội Care và Đội Phát triển Kinh doanh cần biết chính xác **những trường dữ liệu nào sẽ thấy được trên trang chi tiết creator**, từ đó đánh giá creator hiệu quả mà không cần mở thêm công cụ ngoài.

Tài liệu này liệt kê **dữ liệu thực tế đang chạy production** trong influence-meter mà CRM at-core sẽ hiển thị cho mỗi creator.

**Lưu ý:** Dữ liệu chỉ được pull từ influence-meter **1 lần** (lúc creator đăng ký hoặc lúc Care mở trang chi tiết creator lần đầu). Sau đó cache lại trong DB. Chưa có cơ chế re-enrich định kỳ trong scope này.

---

## Tổng quan dữ liệu khả dụng

| Nền tảng | Profile cơ bản | Engagement | Recent content |
|---|---|---|---|
| **TikTok** | ✅ | ✅ | ✅ |
| **YouTube** | ✅ | ✅ | ✅ |
| **Facebook** | ✅ | ✅ | ✅ |
| **Instagram** | ✅ | ✅ | ✅ |

> **⚠️ Caveat quan trọng:** Một số trường mặc dù schema có support nhưng thực tế **influence-meter chưa lấy được chính xác / đầy đủ cho cả 4 platform**. Các trường sau KHÔNG đảm bảo cam kết và sẽ KHÔNG hiển thị:
> - **Verified badge** — không nhất quán giữa các platform
> - **Quốc gia** — không phải platform nào cũng public
> - **Ngôn ngữ** — chưa có detection ổn định
>
> Khi audit influence-meter API ở tuần 1 triển khai, nếu phát hiện thêm trường nào không cover đầy đủ, Diso sẽ cập nhật danh sách này và thông báo trước với AT.

---

## TikTok

### Profile cơ bản
- Tên creator, handle (@username)
- Avatar, bio, mô tả
- Số follower, số đang follow
- Tổng số video đã đăng
- Chuyên mục (category)
- Ngày tạo tài khoản, tuổi tài khoản (ngày)

### Engagement metrics
- **Engagement rate (%)** = (avg views + avg likes + avg comments + avg shares) / followers × 100
- Avg views per video
- Avg likes per post
- Tổng comments, tổng shares
- Tần suất đăng bài (posts/tuần)

### Recent content (top 10-20 video gần nhất)
- Content ID, link permalink
- View count, like count, comment count, share count, save count
- Ngày đăng
- Hashtags
- Music title (đặc trưng TikTok)

---

## YouTube

### Profile cơ bản
- Tên kênh, handle, custom URL
- Avatar, mô tả kênh
- Số subscriber
- Tổng số video
- Chuyên mục
- Ngày tạo kênh

### Engagement metrics
- **Engagement rate (%)** = (avg likes + avg comments) / subscribers × 100
- Avg views per video
- Avg likes per video
- Tần suất đăng (posts/tuần)
- Tuổi tài khoản

### Recent content (top 10-20 video gần nhất)
- Video ID, title, permalink
- View count, like count, comment count
- Duration (giây)
- Thumbnail URL
- Tags
- Ngày đăng

---

## Facebook

### Profile cơ bản
- Tên page, handle
- Avatar, banner, cover URL, mô tả
- Số follower (page likes)
- Tổng số bài đăng
- Chuyên mục
- Website
- Profile URL

### Engagement metrics
- **Engagement rate (%)** = (avg likes + avg comments + avg shares) / followers × 100
- Avg likes/comments/shares per post
- Tần suất đăng bài
- Tuổi tài khoản

### Recent content
- Post ID, caption, permalink
- View, like, comment, share count
- Ngày đăng
- **Reactions breakdown** (Like, Love, Haha, Wow, Sad, Angry)

---

## Instagram

### Profile cơ bản
- Tên, handle, mô tả
- Avatar, banner
- Số follower, số đang follow
- Tổng số bài
- Chuyên mục
- Website

### Engagement metrics
- **Engagement rate (%)** = (avg likes + avg comments) / followers × 100
- Avg views per video (reels/IGTV)
- Avg likes/comments per post
- Tần suất đăng bài
- Tuổi tài khoản

### Recent content (top 10-20 bài gần nhất)
- Content ID, caption, permalink
- View, like, comment count
- Thumbnail URL
- Hashtags
- Ngày đăng

---

## Dữ liệu liên nền tảng (Cross-platform)

### Trust signals
- Tuổi tài khoản trên mỗi platform
- Tần suất đăng nhất quán

### Performance score
- Điểm hiệu suất 0-100 dựa trên lịch sử campaign đã tracking
- Ngày cập nhật điểm gần nhất

---

## Cách dữ liệu được lấy

- Pull từ influence-meter **1 lần** lúc creator đăng ký (hoặc lúc Care mở trang chi tiết creator lần đầu)
- Lưu cache vào DB của CRM at-core
- Không có job re-enrich định kỳ — nếu cần data mới, Care bấm nút "Refresh" thủ công trên trang chi tiết creator
- Mỗi lần Refresh tốn 1 quota của influence-meter

---

## Giới hạn và điều kiện

### Public profile only
- Chỉ lấy data từ **public profile + public posts** trên 4 nền tảng.
- Creator KHÔNG cần đăng nhập platform để CRM lấy data.
- Bài đăng private, story 24h, DM, group kín — KHÔNG nằm trong scope.

### Rate limit
- Influence-meter có quota theo tenant — khi vượt quota, request bị queue và retry sau.
- Multi-region proxy rotation tránh IP bị block (đã proven trong Metric POC).

### Pháp lý và đạo đức
- Tuân thủ Terms of Service từng platform khi scrape.
- Không thu thập dữ liệu cá nhân nhạy cảm (PII) ngoài phạm vi public.

---

## Validation và minh chứng

Diso cam kết các dữ liệu REAL ở trên đang chạy production cho:
- **Techcombank dashboard** — hiển thị data creator cho team Marketing TCB từ Q1 2026
- **Metric POC** — thu thập data hơn 5.000 creator/tuần ổn định

AccessTrade có thể request demo live từ một creator cụ thể bất kỳ để verify dữ liệu trước khi ký hợp đồng.

---

## Tài liệu liên quan

- **Nguồn code:** `influencer-platform/influence-meter/` (Diso internal)
- **Production reference:** Techcombank dashboard (Diso đã ship)
