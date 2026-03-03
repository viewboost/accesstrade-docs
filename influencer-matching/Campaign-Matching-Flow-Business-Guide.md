# HƯỚNG DẪN CHỨC NĂNG: TẠO CHIẾN DỊCH & TÌM INFLUENCER PHÙ HỢP

**Ngày:** 2026-03-03
**Người viết:** Product Manager - Diso
**Dành cho:** Accesstrade Business Team, Techcombank Marketing Team
**Mục đích:** Giải thích cách hoạt động của chức năng tạo chiến dịch, chọn influencer, và chấm điểm matching trên nền tảng at-core

---

## MỤC LỤC

1. [Tổng Quan Chức Năng](#1-tổng-quan-chức-năng)
2. [Quy Trình Từng Bước](#2-quy-trình-từng-bước)
3. [Cách Hệ Thống Chấm Điểm](#3-cách-hệ-thống-chấm-điểm)
4. [Vai Trò Của Vendor](#4-vai-trò-của-vendor)
5. [Ví Dụ Thực Tế](#5-ví-dụ-thực-tế)
6. [Câu Hỏi Thường Gặp](#6-câu-hỏi-thường-gặp)
7. [Trạng Thái Triển Khai](#7-trạng-thái-triển-khai)

---

## 1. TỔNG QUAN CHỨC NĂNG

### Vấn Đề Hiện Tại

Khi brand (ví dụ Techcombank) muốn chạy chiến dịch influencer marketing, đội marketing phải:

- Tự tìm influencer trên mạng xã hội (mất **2-3 giờ**)
- Đánh giá thủ công từng influencer (ngành hàng có phù hợp không? followers bao nhiêu? tương tác tốt không?)
- Không có tiêu chí rõ ràng → chọn theo cảm tính
- Khó giải thích cho sếp tại sao chọn influencer này mà không chọn người kia

### Giải Pháp

Nền tảng at-core sẽ hỗ trợ **tự động hóa** quy trình này:

```
Trước khi có hệ thống               Sau khi có hệ thống
══════════════════════               ══════════════════════
Tìm influencer thủ công (2-3h)  →   Lọc từ thư viện influencer (5 phút)
Đánh giá bằng cảm tính          →   Chấm điểm tự động (3 tiêu chí)
Không có lý do rõ ràng           →   Giải thích chi tiết tại sao chọn
Mất thời gian so sánh            →   Xếp hạng từ cao → thấp tự động
```

---

## 2. QUY TRÌNH TỪNG BƯỚC

### Bước 1: Tạo Chiến Dịch

Brand tạo chiến dịch mới và nhập các thông tin cơ bản:

| Thông tin | Ví dụ | Giải thích |
|-----------|-------|------------|
| **Tên chiến dịch** | "TCB Summer Beauty 2026" | Đặt tên dễ nhận biết |
| **Ngành hàng** | Làm đẹp, Thời trang | Influencer cần thuộc ngành nào? |
| **Quy mô influencer** | Micro (10K-100K), Mid (100K-500K) | Budget phù hợp với tier nào? |
| **Tương tác tối thiểu** | 3% | Engagement rate tối thiểu chấp nhận được |
| **Ngân sách** | 50 triệu VND | Tổng ngân sách chiến dịch |
| **Thời gian** | 01/04 → 30/04/2026 | Khi nào chạy? |

> **Lưu ý:** Các thông tin "Ngành hàng", "Quy mô influencer", và "Tương tác tối thiểu" chính là **tiêu chí matching** - hệ thống sẽ dùng để chấm điểm influencer ở bước sau.

---

### Bước 2: Chọn Influencer Để Chấm Điểm

Sau khi tạo chiến dịch, brand vào **Thư viện Influencer** để tìm và chọn ứng viên:

```
┌──────────────────────────────────────────────────────────┐
│  Thư Viện Influencer                    [Lọc] [Tìm kiếm]│
│                                                          │
│  Nền tảng: [TikTok ✓] [YouTube ✓] [Instagram]           │
│  Ngành:    [Làm đẹp ✓] [Thời trang ✓]                   │
│  Followers: [10K] → [500K]                               │
│                                                          │
│  ──────────────────────────────────────────────────────   │
│                                                          │
│  ☑ Ngọc Trinh Beauty    TikTok    85K followers   4.5%   │
│  ☑ Fashion Queen VN     YouTube   120K followers  3.8%   │
│  ☑ Skincare Tips Daily  Instagram 45K followers   6.2%   │
│  ☐ Gaming Pro VN        TikTok    200K followers  2.1%   │
│  ☑ Beauty Blogger HN    TikTok    95K followers   5.1%   │
│  ...                                                     │
│                                                          │
│  Đã chọn: 20 influencer          [Chấm Điểm Matching →] │
└──────────────────────────────────────────────────────────┘
```

Brand chọn tối đa **100 influencer** rồi bấm **"Chấm Điểm Matching"**.

---

### Bước 3: Hệ Thống Chấm Điểm (Tự Động)

Khi brand bấm "Chấm Điểm Matching", hệ thống at-core sẽ:

```
at-core (nền tảng của AT)                      Vendor (bên chấm điểm)
═══════════════════════════                     ═══════════════════════

1. Lấy tiêu chí từ chiến dịch
   • Ngành: Làm đẹp, Thời trang
   • Quy mô: Micro, Mid
   • Tương tác tối thiểu: 3%

2. Gửi danh sách 20 influencer ──────────►  3. Nhận danh sách + tiêu chí
   kèm tiêu chí của chiến dịch
                                                4. Tra dữ liệu từng influencer
                                                   (đã có sẵn từ hệ thống crawl)

                                                5. Chấm điểm 3 tiêu chí:
                                                   • Ngành hàng phù hợp? → /100
                                                   • Quy mô phù hợp?     → /100
                                                   • Tương tác đủ tốt?    → /100

                                                6. Tính điểm tổng (0-100)

7. Nhận kết quả  ◄──────────────────────────  8. Trả kết quả chấm điểm

9. Lưu lịch sử matching
10. Hiển thị kết quả cho brand
```

> **Thời gian xử lý:** Dưới 5 giây cho 100 influencer.

---

### Bước 4: Xem Kết Quả & Chọn Influencer

Kết quả hiển thị dưới dạng **danh sách xếp hạng từ cao → thấp**:

```
┌──────────────────────────────────────────────────────────────┐
│  Kết Quả Matching          19/20 chấm điểm thành công       │
│                                                              │
│  Điểm │ Influencer              │ Ngành  │ Quy mô │ T.Tác  │
│  ─────┼─────────────────────────┼────────┼────────┼──────── │
│  88 ✓ │ Skincare Tips Daily     │ 100    │ 50     │ 100    │
│  85 ✓ │ Ngọc Trinh Beauty       │ 100    │ 100    │ 80     │
│  78 ✓ │ Fashion Queen VN        │ 100    │ 100    │ 50     │
│  72 ✓ │ Beauty Blogger HN       │ 100    │ 100    │ 50     │
│  ...  │ ...                     │ ...    │ ...    │ ...    │
│  35 ✗ │ Gaming Pro VN           │ 0      │ 100    │ 20     │
│                                                              │
│  ✓ = Phù hợp (≥60 điểm)    ✗ = Chưa phù hợp (<60 điểm)    │
│                                                              │
│  ☑ Chọn top 5              [Thêm vào chiến dịch →]          │
└──────────────────────────────────────────────────────────────┘
```

Brand có thể bấm vào từng influencer để xem **giải thích chi tiết**:

```
┌──────────────────────────────────────────────────────────┐
│  Chi Tiết Điểm: Skincare Tips Daily                      │
│                                                          │
│  ĐIỂM TỔNG: 88/100  ✓ Phù hợp                           │
│  ████████████████████████████░░░░                         │
│                                                          │
│  ── Ngành hàng (chiếm 40% điểm tổng) ────────────────   │
│  100/100  ██████████████████████████████                  │
│  "Ngành 'Làm đẹp' khớp hoàn toàn với chiến dịch"        │
│                                                          │
│  ── Quy mô influencer (chiếm 30% điểm tổng) ─────────   │
│  50/100   ███████████████░░░░░░░░░░░░░░░                 │
│  "Tier 'Nano' (45K followers) gần với tier Micro"        │
│                                                          │
│  ── Tương tác (chiếm 30% điểm tổng) ─────────────────   │
│  100/100  ██████████████████████████████                  │
│  "Engagement rate 6.2% rất tốt (≥5%)"                   │
│                                                          │
│                                           [Đóng]         │
└──────────────────────────────────────────────────────────┘
```

### Bước 5: Hoàn Tất

Brand chọn những influencer phù hợp nhất → thêm vào chiến dịch → bắt đầu liên hệ và booking.

---

## 3. CÁCH HỆ THỐNG CHẤM ĐIỂM

Mỗi influencer được chấm điểm trên **3 tiêu chí**, mỗi tiêu chí có **trọng số** khác nhau:

### 3.1. Ngành Hàng Phù Hợp (40% trọng số)

Hệ thống kiểm tra: **Nội dung của influencer có thuộc ngành mà chiến dịch nhắm tới không?**

| Kết quả | Điểm | Ví dụ |
|---------|------|-------|
| Khớp hoàn toàn | **100** | Chiến dịch "Làm đẹp" + Influencer ngành "Làm đẹp" |
| Không khớp | **0** | Chiến dịch "Làm đẹp" + Influencer ngành "Gaming" |

> Đây là tiêu chí quan trọng nhất (40%) vì nếu ngành hàng không khớp, influencer sẽ không thể truyền tải thông điệp hiệu quả.

### 3.2. Quy Mô Influencer (30% trọng số)

Hệ thống kiểm tra: **Số followers của influencer có nằm trong tier mà chiến dịch mong muốn không?**

**Bảng phân tier:**

| Tier | Followers | Ví dụ |
|------|-----------|-------|
| Nano | 1K - 10K | Beauty blogger mới |
| Micro | 10K - 100K | Reviewer sản phẩm |
| Mid | 100K - 500K | Content creator nổi tiếng |
| Macro | 500K - 1M | KOL có ảnh hưởng lớn |
| Mega | 1M+ | Celebrity, ngôi sao |

| Kết quả | Điểm | Ví dụ |
|---------|------|-------|
| Đúng tier | **100** | Cần Micro + Influencer 85K followers (= Micro) |
| Tier liền kề | **50** | Cần Micro + Influencer 5K followers (= Nano, gần Micro) |
| Khác xa | **0** | Cần Nano + Influencer 2M followers (= Mega) |

### 3.3. Chất Lượng Tương Tác (30% trọng số)

Hệ thống kiểm tra: **Engagement rate (tỷ lệ tương tác) của influencer có đủ tốt không?**

| Engagement Rate | Điểm | Đánh giá |
|-----------------|------|----------|
| ≥ 5% | **100** | Xuất sắc |
| ≥ 3% | **80** | Tốt |
| ≥ 1% | **50** | Trung bình |
| < 1% | **20** | Thấp |

### 3.4. Cách Tính Điểm Tổng

```
Điểm tổng = (Ngành hàng × 40%) + (Quy mô × 30%) + (Tương tác × 30%)
```

**Ví dụ:** Influencer "Skincare Tips Daily"
- Ngành hàng: 100 × 40% = **40.0**
- Quy mô: 50 × 30% = **15.0**
- Tương tác: 100 × 30% = **30.0**
- **Tổng: 85.0 điểm → ✓ Phù hợp**

**Ngưỡng phù hợp:** Influencer có điểm **≥ 60** được đánh dấu "Phù hợp" (✓).

### 3.5. Tùy Chỉnh Trọng Số (Nâng Cao)

Brand có thể điều chỉnh trọng số nếu muốn ưu tiên tiêu chí khác:

| Trường hợp | Ngành | Quy mô | Tương tác |
|-------------|-------|--------|-----------|
| **Mặc định** | 40% | 30% | 30% |
| Ưu tiên tương tác | 30% | 20% | **50%** |
| Ưu tiên đúng tier | 20% | **50%** | 30% |

> Tổng trọng số luôn phải = 100%.

---

## 4. VAI TRÒ CỦA VENDOR

### Vendor Là Gì?

Vendor là **bên thứ ba cung cấp dịch vụ chấm điểm influencer** thông qua API (giao diện lập trình). Tương tự như cách Techcombank dùng dịch vụ SMS OTP của bên thứ ba - at-core gọi tới Vendor để lấy kết quả chấm điểm.

### Vendor Làm Gì?

```
┌─────────────────────────────────────────────────────────┐
│  VENDOR (Bên Chấm Điểm)                                 │
│                                                          │
│  Thu thập dữ liệu         Phân tích & chấm điểm        │
│  ─────────────────         ──────────────────────        │
│  • Crawl TikTok            • Chấm điểm ngành hàng      │
│  • Crawl Instagram         • Chấm điểm quy mô          │
│  • Crawl YouTube           • Chấm điểm tương tác       │
│  • Crawl Facebook          • Tính điểm tổng            │
│                            • Giải thích kết quả        │
│                                                          │
│  Chỉ cung cấp: KẾT QUẢ (qua API)                       │
│  Không cung cấp: Giao diện, ứng dụng                    │
└─────────────────────────────────────────────────────────┘
```

### at-core Làm Gì Thêm? (Không Chỉ Chuyển Tiếp)

at-core **không chỉ đơn thuần chuyển tiếp** yêu cầu tới Vendor. Nền tảng xử lý thêm nhiều việc quan trọng:

| Việc at-core làm | Lý do |
|-------------------|-------|
| **Xác thực người dùng** | Chỉ brand/partner được phép mới gọi được |
| **Kiểm soát tần suất** | Tối đa 10 lần/giây, 1000 lần/ngày - tránh quá tải |
| **Lưu lịch sử** | Mỗi lần chấm điểm đều được ghi lại để xem lại sau |
| **Bộ nhớ đệm** | Nếu cùng tiêu chí, trả kết quả cũ (nhanh hơn, tiết kiệm chi phí) |
| **Xử lý lỗi** | Nếu Vendor tạm ngưng, vẫn trả kết quả từ bộ nhớ đệm |
| **Bổ sung thông tin** | Thêm avatar, thông tin liên hệ từ dữ liệu nội bộ |

### Khi Nào Vendor Không Hoạt Động?

```
Bình thường:
  Brand bấm "Chấm điểm" → at-core → Vendor → Kết quả mới (< 5 giây)

Vendor tạm ngưng:
  Brand bấm "Chấm điểm" → at-core → Vendor ✗ → Trả kết quả từ bộ nhớ đệm
                                                   + Thông báo: "Dữ liệu từ 1 giờ trước"
```

> Brand vẫn sử dụng được, chỉ là kết quả có thể chưa phải mới nhất.

---

## 5. VÍ DỤ THỰC TẾ

### Chiến dịch: "TCB Summer Beauty 2026"

**Bước 1 - Tạo chiến dịch:**
- Ngành hàng: Làm đẹp, Skincare
- Quy mô: Micro (10K-100K), Mid (100K-500K)
- Tương tác tối thiểu: 3%
- Ngân sách: 50 triệu VND

**Bước 2 - Chọn 5 influencer để chấm điểm:**

| Influencer | Nền tảng | Followers | ER | Ngành |
|------------|----------|-----------|-----|-------|
| Skincare Tips Daily | Instagram | 45K | 6.2% | Skincare |
| Beauty Guru VN | TikTok | 85K | 4.5% | Làm đẹp |
| Fashion Queen | YouTube | 120K | 3.8% | Thời trang |
| Travel Vlogger | TikTok | 200K | 2.5% | Du lịch |
| Gaming Pro | YouTube | 300K | 1.2% | Gaming |

**Bước 3 - Kết quả chấm điểm:**

| # | Influencer | Ngành (40%) | Quy mô (30%) | Tương tác (30%) | Tổng | Kết quả |
|---|------------|-------------|---------------|-----------------|------|---------|
| 1 | Beauty Guru VN | 100 → 40.0 | 100 → 30.0 | 80 → 24.0 | **94** | ✓ Phù hợp |
| 2 | Skincare Tips Daily | 100 → 40.0 | 50 → 15.0 | 100 → 30.0 | **85** | ✓ Phù hợp |
| 3 | Fashion Queen | 100 → 40.0 | 100 → 30.0 | 80 → 24.0 | **94** | ✓ Phù hợp |
| 4 | Travel Vlogger | 0 → 0.0 | 100 → 30.0 | 50 → 15.0 | **45** | ✗ Chưa phù hợp |
| 5 | Gaming Pro | 0 → 0.0 | 100 → 30.0 | 50 → 15.0 | **45** | ✗ Chưa phù hợp |

**Phân tích kết quả:**
- **Beauty Guru VN** (94 điểm): Đúng ngành (Làm đẹp ✓), đúng tier Micro (85K ✓), ER tốt (4.5% ✓)
- **Skincare Tips Daily** (85 điểm): Đúng ngành (Skincare ✓), nhưng tier Nano thay vì Micro (45K, chỉ được 50 điểm quy mô), ER xuất sắc (6.2% ✓)
- **Travel Vlogger** (45 điểm): Sai ngành (Du lịch ≠ Làm đẹp → 0 điểm ngành hàng). Dù quy mô và tương tác ổn, sai ngành hàng là lý do chính bị điểm thấp.

**Bước 4 - Brand chọn top 3** (Beauty Guru VN, Fashion Queen, Skincare Tips Daily) → Thêm vào chiến dịch.

---

## 6. CÂU HỎI THƯỜNG GẶP

### Q: Dữ liệu influencer từ đâu?
**A:** Vendor thu thập dữ liệu từ các nền tảng mạng xã hội (TikTok, Instagram, YouTube, Facebook) thông qua hệ thống crawl tự động. Dữ liệu được cập nhật định kỳ.

### Q: Có thể chấm điểm bao nhiêu influencer cùng lúc?
**A:** Tối đa **100 influencer** mỗi lần. Nếu cần nhiều hơn, brand có thể chấm điểm nhiều lần.

### Q: Điểm số có thay đổi theo thời gian không?
**A:** Có. Khi dữ liệu influencer được cập nhật (followers tăng, ER thay đổi, đổi ngành nội dung), điểm matching sẽ thay đổi theo.

### Q: Brand có thể tùy chỉnh trọng số không?
**A:** Có. Mặc định là 40/30/30 (ngành/quy mô/tương tác), nhưng brand có thể điều chỉnh theo nhu cầu. Tổng luôn phải bằng 100%.

### Q: Nếu influencer không có trong hệ thống thì sao?
**A:** Hệ thống sẽ báo lỗi cho influencer đó và bỏ qua. Các influencer khác vẫn được chấm điểm bình thường. Kết quả sẽ ghi rõ "19/20 chấm điểm thành công, 1 không tìm thấy".

### Q: Dữ liệu matching có được lưu lại không?
**A:** Có. Mỗi lần chấm điểm đều được lưu thành một **phiên matching** (matching session). Brand có thể xem lại lịch sử matching của từng chiến dịch bất cứ lúc nào.

### Q: Chi phí Vendor tính như thế nào?
**A:** Vendor tính phí theo lượt gọi API. at-core có cơ chế bộ nhớ đệm (cache) để giảm số lần gọi, tiết kiệm chi phí cho brand.

---

## 7. TRẠNG THÁI TRIỂN KHAI

### Đã Hoàn Thành

| Hạng mục | Phía | Trạng thái |
|----------|------|------------|
| Hệ thống chấm điểm matching (Vendor API) | Vendor | ✅ Xong |
| Hệ thống enrichment influencer | at-core + Vendor | ✅ Xong |
| Kết nối API cơ bản (lấy profile, lấy điểm) | at-core | ✅ Xong |
| Xử lý lỗi, bộ nhớ đệm, circuit breaker | at-core | ✅ Xong |
| Quản lý tenant (multi-brand) | at-core | ✅ Xong |

### Chưa Triển Khai

| Hạng mục | Phía | Ghi chú |
|----------|------|---------|
| Quản lý chiến dịch (Campaign CRUD) | at-core | Cần xây mới |
| Gọi API chấm điểm matching (/matching/batch) | at-core | API Vendor sẵn sàng, at-core chưa gọi |
| Lưu lịch sử matching sessions | at-core | Collection MongoDB chưa tạo |
| Giao diện danh sách điểm (Scored Influencer List) | at-core | Chưa có |
| Giao diện chi tiết điểm (Score Breakdown Modal) | at-core | Có component cơ bản, cần enhance |
| Giao diện lịch sử matching | at-core | Chưa có |

### Tóm Tắt

```
Vendor (bên chấm điểm):       ██████████████████████  100% sẵn sàng
at-core nền tảng (cơ sở hạ tầng): ██████████████████████  95% sẵn sàng
at-core chức năng matching:    ███░░░░░░░░░░░░░░░░░░  ~15% (cần xây thêm)
```

> **Nền móng đã vững** (kết nối API, xử lý lỗi, cache). Cần xây thêm phần **Campaign + Matching UI** để brand có thể sử dụng end-to-end.

---

**Tài liệu này được tạo bởi:** Diso Product Team
**Ngày:** 2026-03-03
**Phiên bản:** 1.0
