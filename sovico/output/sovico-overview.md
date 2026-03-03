# Sovico KOC Platform — Tổng Quan Giải Pháp

> **Tài liệu dành cho:** Business stakeholders, non-technical
> **Ngày:** 2026-03-03
> **Version:** 1.0 — Draft

---

## 1. Bối Cảnh & Mục Tiêu

### Bối cảnh
Tập đoàn Sovico muốn xây dựng một nền tảng **khuyến khích CBNV (Cán bộ nhân viên)** các công ty con (HDBank, Vikki, Vietjet,...) **tương tác tích cực** với nội dung trên kênh Facebook/TikTok/YouTube của thương hiệu — từ đó **tăng SOV (Share of Voice) và buzz** mỗi tháng.

### Mục tiêu cốt lõi
| # | Mục tiêu | Mô tả |
|---|----------|-------|
| 1 | **Tăng tương tác thương hiệu** | CBNV like, comment, share bài viết trên kênh chính thức |
| 2 | **Tracking & đo lường** | Biết chính xác ai tương tác gì, ở đâu, khi nào |
| 3 | **Trả thưởng tự động** | Quy đổi tương tác thành điểm, tích hợp hệ thống điểm Sovico |
| 4 | **Quản lý đa thương hiệu** | 1 platform phục vụ HDBank, Vikki, Vietjet,... cùng lúc |

---

## 2. Giải Pháp Đề Xuất

### Cách tiếp cận
Chúng tôi **tận dụng nền tảng Ambassador Platform đã vận hành production** (đang phục vụ 10+ thương hiệu lớn: TPBank, HDBank, MBBank, VNPay,...) và **customize theo đặc thù Sovico**:

- **KHÔNG xây từ đầu** → Giảm ~60-70% thời gian & chi phí so với build mới
- **Hệ thống đã proven** → Đã tracking hàng triệu tương tác, xử lý thanh toán cho hàng nghìn KOC
- **Sẵn sàng scale** → Kiến trúc microservices hỗ trợ mở rộng linh hoạt

### Điểm mạnh nền tảng hiện có
- ✅ Kết nối tài khoản MXH (Facebook, TikTok, YouTube, Threads,...)
- ✅ Dashboard analytics cho admin & user
- ✅ Hệ thống quản lý campaign/event linh hoạt
- ✅ Luồng duyệt nội dung (content moderation)
- ✅ Hệ thống tài chính: cashflow, withdraw, reconciliation
- ✅ Multi-brand support (đã chạy 10+ branded app)
- ✅ Customize giao diện theo nhận diện thương hiệu

### Cách thức tracking tương tác CBNV
Hệ thống sẽ **tracking từng hành động** của CBNV (ai like, ai comment, ai share) trên kênh chính thức của thương hiệu — KHÔNG phải chỉ đếm tổng số.

**Cơ chế:**
1. CBNV kết nối tài khoản MXH (Facebook/TikTok) vào hệ thống
2. Dịch vụ crawl (đã có sẵn) quét bài viết trên kênh thương hiệu → trả về danh sách ai đã like, comment, share
3. Hệ thống match social user ID → CBNV đã đăng ký
4. Ghi nhận từng tương tác: **CBNV nào** → **tương tác gì** → **bài viết nào** → **thời điểm nào**
5. Tự động tính điểm thưởng dựa trên quy tắc

---

## 3. Các Gói Dịch Vụ

### Gói 1: Onboard Cơ Bản ⭐ (Nền tảng)
**Timeline: D+15 (15 ngày làm việc ≈ 3 tuần)**

| Tính năng | Chi tiết |
|-----------|----------|
| Multi-company setup | Thiết lập nhiều công ty con (HDBank, Vikki, Vietjet) trên cùng 1 nền tảng |
| Luồng onboard CBNV | Đăng ký theo phòng ban/đơn vị, kết nối tài khoản MXH |
| Tracking từng CBNV | Biết chính xác **CBNV nào** đã like/comment/share **bài nào** — cập nhật theo ngày |
| Filter phòng ban | Lọc, xem dữ liệu theo phòng ban/đơn vị |
| Dashboard CBNV | Nhân viên tự xem kết quả bất cứ lúc nào |
| Dashboard tổng hợp | Tổng tương tác theo CBNV, theo phòng ban |
| Custom branding | Giao diện theo nhận diện thương hiệu từng brand |

**Cơ sở kỹ thuật:** Tận dụng nền tảng Ambassador + tích hợp dịch vụ crawl đã có sẵn:
- Module quản lý phòng ban/đơn vị (mới)
- Luồng onboard CBNV đơn giản hóa (thay vì KOC flow phức tạp)
- Tích hợp crawl service → nhận data tương tác cá nhân → matching CBNV (mới)
- Dashboard aggregation theo phòng ban (mới)

---

### Gói 2: Hệ Thống Tích Điểm
**Timeline: D+25 (25 ngày làm việc ≈ 5 tuần, song song với Gói 1)**

| Tính năng | Chi tiết |
|-----------|----------|
| Thay tiền bằng điểm | Toàn bộ reward quy về hệ thống tích điểm |
| Tích hợp API Sovico | Khi điểm được confirm → gọi API sang hệ thống điểm Sovico |
| Lịch sử điểm | CBNV xem lịch sử cộng/trừ điểm |
| Admin quản lý | Cấu hình quy đổi, duyệt điểm |

**Cơ sở kỹ thuật:** Refactor module cashflow/withdraw hiện có → point-based system. Tích hợp API outbound.

---

### Gói 3: "Tương Tác Cũng Được Tiền"
**Timeline: D+25 (25 ngày, bắt đầu sau Gói 1 hoàn thành)**

| Tính năng | Chi tiết |
|-----------|----------|
| Chương trình khuyến khích | Tạo campaign khuyến khích comment trên Own Channel |
| Đăng ký tham gia | CBNV chọn tham gia chương trình |
| Nhận data tương tác | Tích hợp crawl service → nhận data like, comment, share trên kênh thương hiệu |
| Đánh giá hợp lệ | Kiểm tra comment có nội dung, không spam |
| Tính thưởng | Tự động tính điểm thưởng theo quy tắc |

**Cơ sở kỹ thuật:** Tích hợp crawl service (đã có) cho campaign cụ thể. Bổ sung:
- Campaign-scoped crawl config (bài nào, kênh nào)
- Rule engine đánh giá comment hợp lệ (mới)
- Reuse matching engine CBNV từ Gói 1

---

### Gói 4: "Đánh Giá 5 Sao Được Tiền"
**Timeline: D+25 (25 ngày, có thể song song với Gói 3)**

| Tính năng | Chi tiết |
|-----------|----------|
| Rating trên App Store | CBNV đánh giá app trên Apple/Google Store |
| Hashtag cá nhân | Kèm hashtag để identify |
| Chụp bằng chứng | Upload ảnh screenshot làm bằng chứng |
| Verify tự động + thủ công | Hệ thống kiểm tra, admin duyệt |
| Thưởng tự động | Cộng điểm khi verify thành công |

**Cơ sở kỹ thuật:** Module mới, tận dụng:
- Upload/file management hiện có
- Content moderation flow hiện có
- Reward/cashflow engine hiện có

---

### Gói 5: "Check-in Được Tiền"
**Timeline: D+25 (25 ngày, có thể song song với Gói 4)**

| Tính năng | Chi tiết |
|-----------|----------|
| Check-in Google Maps | Rating/review trên Google Maps |
| Hashtag cá nhân | Kèm hashtag để identify |
| Chụp bằng chứng | Upload ảnh screenshot |
| Verify | Hệ thống + admin kiểm tra |
| Thưởng | Cộng điểm thưởng |

**Cơ sở kỹ thuật:** Tương tự Gói 4, cùng module proof-submission + verification.

**Phụ thuộc:** Gói "Phân tích tương tác"

---

## 4. Roadmap Triển Khai (Target: ~1 Tháng)

```
Tuần 1          Tuần 2          Tuần 3          Tuần 4          Tuần 5
│───────────────│───────────────│───────────────│───────────────│──────────>
│                                               │
│◄──── Gói 1: Onboard Cơ Bản (D+15) ─────────►│
│                                               │
│◄──────────── Gói 2: Tích Điểm (D+25, song song) ────────────────────►│
│                                                               │
│               │◄── Gói 3: Tương tác (D+25, sau Gói 1) ──────────────►│
│               │                                               │
│               │◄── Gói 4: Rating 5 sao (D+25, song song) ───────────►│
│               │                                               │
│               │◄── Gói 5: Check-in (D+25, song song) ───────────────►│
│               │                                               │
│───────────────│───────────────│───────────────│───────────────│──────────>
```

**Chiến lược:**
- **Tuần 1-3:** Gói 1 (onboard) + Gói 2 (tích điểm) chạy song song
- **Tuần 2-5:** Gói 3, 4, 5 bắt đầu khi foundation Gói 1 ổn
- **D+25 (~5 tuần):** Toàn bộ 5 gói hoàn thành

> **Lưu ý:** Timeline D+25 ≈ 5 tuần calendar. Nếu muốn giao nhanh hơn, có thể ưu tiên Gói 1+2 trước (D+15 ≈ 3 tuần), các gói còn lại phase 2.

---

## 5. Lợi Thế Cạnh Tranh

### So với build từ đầu

| Tiêu chí | Build từ đầu | Giải pháp của chúng tôi |
|-----------|-------------|------------------------|
| **Thời gian** | 3-4 tháng | ~1 tháng |
| **Chi phí** | Cao (full dev team 3-4 tháng) | Giảm 60-70% |
| **Rủi ro** | Cao (code mới chưa test) | Thấp (production-proven) |
| **Tracking MXH** | Phải tự xây crawler + tích hợp | Chỉ cần tích hợp crawl service (đã có) |
| **Multi-brand** | Phải thiết kế architecture | Đã hỗ trợ 10+ brand |
| **Scalability** | Chưa chứng minh | Đã chứng minh với data thực |

### Đã phục vụ thành công
TPBank, HDBank, MBBank, VPBank, VNPay, Anker, Flamingo, Yody, Turborg, WildRift

---

## 6. Nền Tảng Hỗ Trợ

| Nền tảng | OAuth (link account) | Tracking tương tác | Ghi chú |
|----------|---------------------|-------------------|---------|
| **Facebook** | ✅ Sẵn sàng | ✅ Qua crawl service | Link FB account → match ai like/comment/share |
| **TikTok** | ✅ Sẵn sàng | ✅ Qua crawl service | Link TikTok → match tương tác |
| **YouTube** | ✅ Sẵn sàng | ✅ Qua crawl service | Link YouTube → match comment |
| **Threads** | ✅ Sẵn sàng | ✅ Qua crawl service | Link Threads → match tương tác |
| **Google Maps** | — | 🔨 Proof-based | CBNV chụp screenshot → admin verify |
| **App Store** | — | 🔨 Proof-based | CBNV chụp screenshot → admin verify |

> **Lưu ý:** Dịch vụ crawl (lấy data ai like/comment/share trên kênh thương hiệu) đã có sẵn. Hệ thống chỉ cần **tích hợp nhận data** và **matching với CBNV**.

---

## 7. Yêu Cầu Từ Phía Sovico

Để triển khai nhanh, cần từ phía Sovico:

1. **API spec hệ thống tích điểm** — Endpoint, authentication, payload format
2. **Danh sách công ty con** tham gia ban đầu (HDBank, Vikki, Vietjet,...)
3. **Cấu trúc phòng ban** của từng công ty con (Excel)
4. **Bộ nhận diện thương hiệu** — Logo, màu sắc, font cho custom branding
5. **Danh sách kênh MXH chính thức** cần tracking (Facebook page ID, TikTok channel,...)
6. **Quy tắc tích điểm** — Bao nhiêu điểm cho 1 like, 1 comment, 1 share,...
7. **Spec crawl service** — API format trả data tương tác (ai like/comment/share bài nào)
8. **Người phụ trách** từ mỗi công ty con để UAT (User Acceptance Testing)

---

## 8. Rủi Ro & Giảm Thiểu

| Rủi ro | Mức độ | Giảm thiểu |
|--------|--------|-----------|
| API tích điểm Sovico chưa sẵn sàng | Trung bình | Mock API trước, tích hợp thật sau |
| Crawl service trả data không đủ/trễ | Trung bình | Thiết kế retry + reconciliation; fallback manual report |
| Matching CBNV sai (trùng tên, thiếu link MXH) | Trung bình | Bắt buộc link account MXH khi onboard; match bằng social ID (không bằng tên) |
| Số lượng CBNV lớn (hàng nghìn) | Thấp | Hệ thống đã scale với data thực |
| Yêu cầu thay đổi giữa chừng | Trung bình | Chia gói rõ ràng, UAT sau mỗi gói |
| Verify rating/check-in không chính xác 100% | Trung bình | Kết hợp auto-verify + admin review |

---

## 9. Liên Hệ

**Đơn vị triển khai:** [Tên công ty]
**Liên hệ:** [Thông tin liên hệ]
**Website:** [URL]

---

*Tài liệu này là bản draft v1.0. Cần review và xác nhận từ phía Sovico trước khi tiến hành báo giá chi tiết.*
