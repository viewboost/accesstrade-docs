# Mô hình Booking trên Ambassador — Đề bài gốc

> Tài liệu mô tả mô hình KOC Booking triển khai trên nền tảng **Ambassador**, bao gồm luồng nghiệp vụ, hành trình ADV chọn creator, kế hoạch migration từ hệ thống KOC Booking cũ, và so sánh với đối thủ.

> **Nguồn:** Chuyển thể trực tiếp từ request gốc — [Google Sheets](https://docs.google.com/spreadsheets/d/194bLxGmDumERIDkHy1tlzBtczyvSWSqy9lfKpQrHokI/edit?gid=0#gid=0).

## Mục lục

1. [Tổng quan 5 module](#tổng-quan-5-module)
2. [Sơ đồ ① — Luồng Booking 5 bước](#sơ-đồ--luồng-booking-5-bước)
3. [Sơ đồ ② — ADV Side: Chọn Creator](#sơ-đồ--adv-side-chọn-creator-trên-ambassador)
4. [Sơ đồ ③ — Tận dụng hệ thống KOC Booking cũ → Ambassador](#sơ-đồ--tận-dụng-hệ-thống-koc-booking-cũ--ambassador)
5. [Rollout — Thứ tự ưu tiên](#rollout--thứ-tự-ưu-tiên)
6. [So sánh với đối thủ](#so-sánh-với-đối-thủ) *(đã fact-check qua research)*
7. [Chi tiết 5 module cần build](#chi-tiết-5-module-cần-build)

---

## Tổng quan 5 module

| # | Module | Mô tả ngắn |
|---|--------|-----------|
| ① | **Job Listing** | Brand/Admin tạo job với brief, ngân sách, quota. KOC thấy feed job được filter theo tier và platform. |
| ② | **Tham gia Job** | KOC apply → Admin duyệt → tự gửi brief + hướng dẫn. Cần workflow approval và notification. |
| ③ | **Nộp bài Content** | KOC submit link + proof → Admin review (tối đa 2 lần revise) → track performance tự động. **Module phức tạp nhất về logic.** |
| ④ | **Ký HĐ điện tử** | Template HĐ tự động điền theo job, KOC ký bằng OTP/eSign, lưu PDF có timestamp. Tích hợp eSign provider. |
| ⑤ | **Thanh toán** | Triggered sau khi bài approved → Finance xác nhận → upload proof → KOC nhận notification và xác nhận. Gắn chặt với ④. |

---

## Sơ đồ ① — Luồng Booking 5 bước

```
        ┌─────────────────────────────────────────────────────────────────┐
        │                  MÔ HÌNH BOOKING TRÊN AMBASSADOR                  │
        └─────────────────────────────────────────────────────────────────┘

  Brand/Admin                                                      KOC/Creator
      │                                                                 ▲
      │            ┌──────────────────────────────────────────┐         │
      ├───────────▶│            ① DANH SÁCH JOBS               │────────▶│
      │            ├──────────────┬──────────────┬────────────┤         │
      │            │   Tạo Job     │ Điều kiện     │ Hiển thị    │         │
      │            │              │ tham gia      │ cho KOC     │         │
      │            │ • Tên, mô tả  │ • Tier /      │ • Feed job  │         │
      │            │   yêu cầu     │   follower min │   phù hợp   │         │
      │            │ • Ngân sách,  │ • Platform     │   profile   │         │
      │            │   timeline    │   yêu cầu      │ • Filter    │         │
      │            │ • Quota KOC   │ • Ngành/niche  │   platform/ │         │
      │            │              │               │   tier      │         │
      │            │              │               │ • Deadline  │         │
      │            │              │               │   đăng ký   │         │
      │            └──────────────┴───────┬───────┴────────────┘         │
      │                                   ▼                              │
      │            ┌──────────────────────────────────────────┐         │
      │            │            ② THAM GIA JOB                 │────────▶│
      │            ├──────────────┬──────────────┬────────────┤         │
      │            │  KOC apply    │ Admin duyệt   │ Gửi Brief   │         │
      │            │              │              │ + HD        │         │
      │  · · · · · │ • Chọn job →  │ • Review      │ • File brief│         │
      │            │   Apply       │   profile KOC │   tự động   │         │
      │            │ • Xem brief   │ • Approve /   │   gửi       │         │
      │            │   trước       │   Reject      │ • Hướng dẫn │         │
      │            │ • Status:     │ • Notify KOC  │   nộp bài   │         │
      │            │   Pending     │              │ • Deadline  │         │
      │            │              │              │   content   │         │
      │            └──────────────┴───────┬───────┴────────────┘         │
      │                                   ▼                              │
      │            ┌──────────────────────────────────────────┐         │
      │            │           ③ NỘP BÀI CONTENT              │────────▶│
      │            ├──────────────┬──────────────┬────────────┤         │
      │            │  KOC submit   │ Review bài    │ Track       │         │
      │            │              │              │ performance │         │
      │  · · · · · │ • Link post / │ • Admin check │ • View,like,│         │
      │            │   video       │   content     │   comment   │         │
      │            │ • Thời gian   │ • Pass / Yêu  │ • Đơn / GMV │         │
      │            │   đăng        │   cầu sửa     │   (nếu aff) │         │
      │            │ • Screenshot  │ • Max 2 lần   │ • Auto-     │         │
      │            │   proof       │   revise      │   update KPI│         │
      │            └──────────────┴───────┬───────┴────────────┘         │
      │                                   ▼                              │
      │            ┌──────────────────────────────────────────┐         │
      │            │           ④ KÝ HĐ ĐIỆN TỬ                │────────▶│
      │            ├──────────────┬──────────────┬────────────┤         │
      │            │ Tạo HĐ tự     │ KOC ký số     │ Lưu trữ +   │         │
      │            │ động          │              │ pháp lý     │         │
      │            ├──────────────┤ • OTP / eSign │ • HĐ 2 bên  │         │
      │            │ • Template    │ • Xác nhận    │   đã ký     │         │
      │            │   theo job    │   điều khoản  │ • Gắn với   │         │
      │            │   type        │ • Lưu PDF có  │   job ID    │         │
      │            │ • Fill tên,   │   timestamp   │ • Download  │         │
      │            │   số tiền     │              │   anytime   │         │
      │            │ • Điều khoản  │              │             │         │
      │            │   chuẩn       │              │             │         │
      │            └──────────────┴───────┬───────┴────────────┘         │
      │                                   ▼                              │
      │            ┌──────────────────────────────────────────┐         │
      ├───────────▶│         ⑤ THEO DÕI THANH TOÁN            │────────▶│
      │            ├──────────────┬──────────────┬────────────┤         │
      │            │ Xét duyệt TT  │ Thực hiện TT  │ KOC xem &   │         │
      │            │              │              │ xác nhận    │         │
      │            │ • Sau khi bài │ • Chuyển      │ • Lịch sử   │         │
      │            │   approved    │   khoản / ví  │   thanh toán│         │
      │            │ • Finance xác │ • Upload bill │ • Thông báo │         │
      │            │   nhận        │   proof       │   real-time │         │
      │            │ • Status:     │ • Status:     │ • Xác nhận  │         │
      │            │   Pending pay │   Paid        │   nhận tiền │         │
      │            └──────────────┴──────────────┴────────────┘         │
      │                                                                  │
      │            ┌──────────────────────────────────────────┐         │
      │            │                DATA LAYER                 │         │
      │            │  Job DB · KOC Profile · Contract Store ·   │         │
      │            │         Payment Log · Analytics            │         │
      │            └──────────────────────────────────────────┘         │

  Chú thích:
  ──────  Brand / Admin action      ──────  KOC action      · · · ·  Shared / review
```

---

## Sơ đồ ② — ADV Side: Chọn Creator trên Ambassador

Hành trình của Advertiser (ADV) khi chủ động chọn creator trên marketplace.

```
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│   ① KHÁM PHÁ      │──▶│   ② SHORTLIST     │──▶│   ③ GỬI BRIEF     │──▶│   ④ THEO DÕI      │
├──────────────────┤   ├──────────────────┤   ├──────────────────┤   ├──────────────────┤
│ Browse           │   │ Lưu vào wishlist │   │ Fill brief       │   │ Dashboard ADV    │
│ marketplace      │   │ So sánh nhiều     │   │ template         │   │ riêng            │
│ Filter: tier,    │   │ creator          │   │ Budget /         │   │ Status từng      │
│ platform, niche, │   │ Share list nội    │   │ timeline         │   │ creator          │
│ follower, giá    │   │ bộ               │   │ KPI kỳ vọng      │   │ View, đơn, GMV   │
│ Xem profile +    │   │ ADV confirm chọn  │   │ Sản phẩm /       │   │ Report tự động   │
│ portfolio        │   │                  │   │ yêu cầu          │   │                  │
└──────────────────┘   └──────────────────┘   └──────────────────┘   └──────────────────┘

┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│ Creator Profile  │   │ Shortlist board  │   │ Brief builder    │   │ ADV Dashboard    │
│ card             │   │                  │   │                  │   │                  │
│ • Follower +     │   │ • Compare side-  │   │ • Template theo  │   │ • Toàn bộ        │
│   engagement rate│   │   by-side        │   │   loại job       │   │   campaign của   │
│ • Past campaign  │   │ • Ghi note nội bộ│   │ • Auto-gửi       │   │   ADV            │
│   results        │   │ • Confirm list   │   │   creator khi    │   │ • Per-creator    │
│ • Audience demo +│   │   cuối           │   │   chốt           │   │   performance    │
│   platform       │   │ • Assign PIC nội │   │ • Negotiate /    │   │ • Payment status │
│ • Giá booking cơ │   │   bộ             │   │   counter offer  │   │ • Export báo cáo │
│   bản            │   │                  │   │ • Trigger e-     │   │   PDF            │
│                  │   │                  │   │   contract sau OK│   │                  │
└──────────────────┘   └──────────────────┘   └──────────────────┘   └──────────────────┘
```

---

## Sơ đồ ③ — Tận dụng hệ thống KOC Booking cũ → Ambassador

Kế hoạch migrate dữ liệu và quy trình từ hệ thống cũ sang nền tảng Ambassador.

```
┌────────────────────────┐      ┌────────────────────────┐      ┌────────────────────────┐
│      HỆ THỐNG CŨ       │      │   MIGRATION ACTION      │      │    TRÊN AMBASSADOR     │
└────────────────────────┘      └────────────────────────┘      └────────────────────────┘

┌────────────────────────┐      ┌────────────────────────┐      ┌────────────────────────┐
│ Database KOC profiles  │─────▶│  Import + enrich        │─────▶│ Creator Marketplace    │
│ • Tên, contact,        │      │ • Migrate sang          │      │ • ADV tự search,filter │
│   platform             │      │   Ambassador DB         │      │ • Profile card đầy đủ  │
│ • Follower, lịch sử    │      │ • Bổ sung: engagement   │      │ • Verified = có lịch   │
│   booking              │      │   rate, audience demo,  │      │   sử cũ                │
│ • Tier, giá cũ         │      │   portfolio             │      │                        │
└────────────────────────┘      └────────────────────────┘      └────────────────────────┘

┌────────────────────────┐      ┌────────────────────────┐      ┌────────────────────────┐
│ Booking request form   │─────▶│  Digitize → self-serve  │─────▶│ Brief Builder tích hợp │
│ • ADV gửi brief qua    │      │ • Đưa form lên platform │      │ • ADV tự làm, PIC      │
│   email                │      │ • ADV fill trực tiếp    │      │   review               │
│ • hoặc điền form thủ   │      │ • Auto-assign to PIC    │      │ • Không cần qua email  │
│   công                 │      │                         │      │ • Thời gian xử lý      │
│ • AM xử lý tay         │      │                         │      │   giảm 70%             │
└────────────────────────┘      └────────────────────────┘      └────────────────────────┘

┌────────────────────────┐      ┌────────────────────────┐      ┌────────────────────────┐
│ Hợp đồng               │─────▶│  Template hóa + eSign   │─────▶│ E-contract tự động     │
│ • Word/PDF soạn thủ    │      │ • Convert sang template │      │ • Auto-generate khi    │
│   công                 │      │   chuẩn                 │      │   chốt deal            │
│ • Ký tay hoặc scan     │      │ • Tích hợp eSign        │      │ • Cả 2 bên ký trên app │
│ • Lưu Google Drive rời │      │   provider              │      │ • Lưu tập trung, tìm   │
│   rạc                  │      │ • Link HĐ với job ID    │      │   được                 │
└────────────────────────┘      └────────────────────────┘      └────────────────────────┘

┌────────────────────────┐      ┌────────────────────────┐      ┌────────────────────────┐
│ Tracking performance   │─────▶│  Connect data source    │─────▶│ ADV Dashboard live     │
│ • Báo cáo thủ công     │      │ • Gắn tracking pixel /  │      │ • ADV tự xem realtime  │
│ • Excel / sheet rời    │      │   API                   │      │ • Auto báo cáo định kỳ │
│ • Gửi qua email cho ADV│      │ • Import lịch sử cũ từ  │      │ • Không cần chờ AM gửi │
│                        │      │   Excel                 │      │                        │
│                        │      │ • Chuẩn hóa format      │      │                        │
└────────────────────────┘      └────────────────────────┘      └────────────────────────┘

┌────────────────────────┐      ┌────────────────────────┐      ┌────────────────────────┐
│ Thanh toán             │─────▶│  Số hóa quy trình TT    │─────▶│ Payment tracking       │
│ • Finance xử lý thủ    │      │ • Map quy trình hiện    │      │ • Creator thấy status  │
│   công                 │      │   tại                   │      │ • ADV xác nhận release │
│ • Chuyển khoản rời rạc │      │ • Thêm trigger tự động  │      │ • Full audit trail     │
│ • Không có audit trail │      │ • Upload proof →        │      │                        │
│   rõ                   │      │   confirm               │      │                        │
└────────────────────────┘      └────────────────────────┘      └────────────────────────┘
```

### 💡 Lợi thế lớn nhất khi migration

> **Lịch sử booking cũ = social proof cho creator trên marketplace.**
> Creator có 20 booking thành công sẽ được hiển thị **"Verified"** → ADV tin tưởng hơn từ ngày đầu.

---

## Rollout — Thứ tự ưu tiên

```
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│ Phase 1 — Quick win │  │ Phase 2 — Core flow │  │ Phase 3 — Automation│  │ Phase 4 — Scale     │
├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤
│ • Import creator DB │  │ • Brief builder     │  │ • Payment tracking  │  │ • ADV self-serve    │
│   cũ                │  │ • Booking request   │  │ • ADV dashboard live│  │   hoàn toàn         │
│ • Creator           │  │   online            │  │ • Auto-report ADV   │  │ • AI match brand-   │
│   marketplace       │  │ • E-contract tự     │  │                     │  │   creator           │
│ • ADV browse +      │  │   động              │  │                     │  │ • Multi-ADV         │
│   shortlist         │  │                     │  │                     │  │   concurrently      │
│                     │  │                     │  │                     │  │                     │
│   ~2-3 sprint       │  │   ~3-4 sprint       │  │   ~3-4 sprint       │  │   ~4+ sprint        │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘
```

| Phase | Tên | Hạng mục | Ước lượng |
|-------|-----|----------|-----------|
| **1** | Quick win | Import creator DB cũ · Creator marketplace · ADV browse + shortlist | ~2-3 sprint |
| **2** | Core flow | Brief builder · Booking request online · E-contract tự động | ~3-4 sprint |
| **3** | Automation | Payment tracking · ADV dashboard live · Auto-report ADV | ~3-4 sprint |
| **4** | Scale | ADV self-serve hoàn toàn · AI match brand-creator · Multi-ADV concurrently | ~4+ sprint |

---

## So sánh với đối thủ

> **Cập nhật 2026-06-24** — Bảng so sánh đã được fact-check qua research đa nguồn (web search → deep-read trang chính thức → adversarial verify; 241 raw findings, 22 claim confirmed, 2 refuted). Phiên bản trước của bảng này có một số mô tả **chưa chính xác** (xem [Đính chính](#đính-chính-so-với-bản-trước) bên dưới). Hầu hết số liệu quy mô là **marketing tự báo, chưa kiểm toán độc lập**, thường mâu thuẫn ngay trong website đối thủ → đọc kèm [Caveats](#caveats--giới-hạn-độ-tin-cậy).

### Tổng quan bối cảnh

Thị trường influencer/KOC Việt Nam chia thành 2 mô hình vận hành: **self-service marketplace** (creator tự đăng ký, tự apply) và **managed/agency platform** (nhãn hàng brief, đội vận hành chạy chiến dịch qua database). **Cả 3 đối thủ phân tích đều là HYBRID** — không ai self-serve "thuần túy".

### Bảng so sánh (đã fact-check)

| Tiêu chí | Revu Vietnam | Hiip | KOLs.com.vn | **Ambassador (của bạn)** |
|----------|--------------|------|-------------|--------------------------|
| **Mô hình** | Hybrid rõ nét — 3 tier sản phẩm (self-service + full-service booking + CreatorAds). JV Hàn-Việt (REVU Corp × CleverGroup ~70%) | Hybrid nghiêng **managed/full-service**. Middleman matching bằng AI in-house, lo trọn gói thay brand | Marketplace self-apply *trên giấy* nhưng vận hành thực là **agency thủ công** (báo giá do "Á Châu" cập nhật) | Admin-curated + self-serve digital, automation pháp lý + thanh toán |
| **Job listing** | Niêm yết **MỞ** + đẩy qua trang chủ/email/thông báo. Creator tự ứng tuyển job còn hạn. Brand cũng chọn từ pool | **KHÔNG** browse-apply. Hệ thống **ĐẨY** chiến dịch phù hợp tới creator qua email; brand-initiated | Trang `/du-an/` công khai dạng card (ngân sách 💰, hạn 📅, "Xem & Apply"). Đăng dự án cần brand login | Admin tạo job, **push đến creator phù hợp** theo tier/platform |
| **Tham gia** | Free, 3 bước (tạo TK → kết nối MXH → apply). ĐK: 2.000 follow TikTok/FB/IG, 18+, có TK ngân hàng | Free qua **Facebook OAuth** (web + app iOS/Android). Sàn follower ~3.000 (khuyến nghị 5.000+). Không độc quyền | Free. Form: tên nghệ danh, SĐT/Zalo, 12 lĩnh vực, follower. **Apply 1-click + lời nhắn**, biết ngân sách trước | Creator apply trong app, **admin duyệt** |
| **Nộp bài** | **Có pre-publish review**: tạo nội dung → submit duyệt TRƯỚC khi đăng → đăng → nhận thưởng. Auto nhắc deadline | **Quote-and-confirm**: creator submit báo giá + đề xuất; brand confirm. Content review 1 bước. Không mô tả revision nhiều vòng | **KHÔNG công bố** quy trình submission/review. Chỉ nói chung "thực hiện nội dung" + "báo cáo". Trang quy trình trả 404 | Submit trên platform, **track KPI**, max 2 lần revise |
| **Hợp đồng** | Không tìm thấy e-contract công khai cho creator (quan hệ qua apply + email + cam kết TT) | Không yêu cầu độc quyền; **không mô tả e-contract** brand-influencer công khai | Có bước "ký hợp đồng" nhưng đường ký là **offline/thủ công qua Zalo + email** | **E-contract tự động, ký số (OTP/eSign), lưu PDF có timestamp** |
| **Thanh toán** | Tiền mặt / sản phẩm / voucher. Chuyển khoản sau khi review đăng theo thỏa thuận | Chuyển khoản **2-4 tuần** sau khi hoàn thành. Gắn điều kiện giữ bài live (xóa bài → mất tiền) | **Gần như không nêu chi tiết** (chỉ "thanh toán an toàn"). Không có escrow/timing/milestone công khai | Tracked trên platform, **creator xác nhận**, full audit trail |
| **Mô hình giá** | Bảng giá **tham khảo** công khai 5 tier (Nano 0–2M → Mega 50M+ VND). Phí phía brand không công khai | **Phí creator công khai: 15%** transaction fee (quote 1M → nhận 850K). Phí phía brand quote-on-consultation | Phí nền tảng/commission **không công bố** (trang 404). Có bảng giá celebrity tham khảo `/bang-gia/` (3M–85M VND) | (đề xuất) minh bạch take-rate + bảng giá theo tier |
| **Định vị** | "Nền tảng IM lớn nhất châu Á" + "Agency hàng đầu VN". Phủ 7 thị trường. *Số liệu quy mô mâu thuẫn 1,5-2x* | "#1 IM & ecom company in Asia". Phủ 6 nước SEA, HQ Singapore. Mạnh AI matching + live-selling | "Nền tảng KOL #1 VN". UX marketplace rõ nhưng quy mô tự báo **nhỏ + mâu thuẫn** (40+ KOL vs "500+ dự án/tháng"), data liên hệ dạng placeholder → uy tín đáng nghi nhất | KOC booking end-to-end tích hợp |

### Khoảng trống thị trường → cơ hội cho Ambassador

Research xác nhận **3 khoảng trống** mà không đối thủ nào lấp đầy:

1. **E-contract / hợp đồng điện tử in-platform** — *không đối thủ nào công bố có*. Hợp đồng chủ yếu offline hoặc qua email/Zalo. → Module ④ là **khác biệt rõ rệt nhất**.
2. **Minh bạch thanh toán / escrow** — Hiip có cadence (2-4 tuần, phí creator 15%) nhưng phía brand mù mờ; KOLs.com.vn gần như không có gì. → Module ⑤ (audit trail + creator xác nhận) là điểm mạnh thật.
3. **Pricing model rõ ràng** — đa số quote-on-consultation, chỉ có bảng giá "tham khảo". → Cơ hội định vị minh bạch.

**Định vị Ambassador:** Kết hợp ưu điểm cả 2 mô hình — vừa có **admin curation** (push job đúng creator như tier full-service của Revu) vừa có **self-serve digital** (creator apply trong app). Khác biệt cốt lõi nằm ở lớp **automation pháp lý (e-contract) + thanh toán minh bạch (audit trail)** — đúng 3 khoảng trống đối thủ đang để ngỏ.

### Hồ sơ chi tiết từng đối thủ

#### Revu Vietnam
- **Sở hữu/cấu trúc:** JV giữa REVU Corporation (Hàn Quốc, thành lập 2014) × CleverGroup VN (~70% cổ phần). JV ra mắt tại VN đầu 2019.
- **Sản phẩm:** REVU Platform (self-service) · REVU Premium (full-service booking + tư vấn) · REVU Media/CreatorAds (content + Digital Ads) · REVU SELECT (search-and-offer cho macro).
- **Creator:** REVUers gồm Nano/Micro/Social Seller/Mass Seeder/User — đều là KOC/Reviewer.
- **Điểm mạnh:** hậu thuẫn JV mạnh, phủ 7 thị trường (REVU Global), bảng giá tham khảo công khai (minh bạch hơn đối thủ), pre-publish content review.
- **Điểm yếu:** số liệu quy mô tự báo **mâu thuẫn nặng** (105K vs 155K influencer; 5 vs 8 năm; 1.500 vs 2.000 brand — footer boilerplate dùng lại không khớp body); không có e-contract công khai cho creator.

#### Hiip
- **Nguồn gốc:** Việt Nam, thành lập 2015 bởi CEO **Phi Nguyen** (hay bị viết nhầm "Phil"), CTO Elon Nguyen, chairman Eric Rosenkranz; sản phẩm launch 2016. Có office SEA tại Singapore + VN/MY/TH/ID/PH.
- **Mô hình:** middleman matching brand-influencer bằng AI in-house (*Hiip mô tả* ML + image recognition + NLP — self-description marketing, chưa kiểm chứng độc lập). Lo trọn gói "creator sourcing, contracting, content review, posting, ROI reporting" thay brand.
- **Quy mô:** đội ~110-120 người. Mạng lưới: 3M+ global / 1M SEA (2 scope khác nhau, nhất quán — đều là first-party copy).
- **Điểm mạnh:** công nghệ AI matching + e-commerce/live-selling, full-service end-to-end, **phí creator minh bạch (15%)**.
- **Điểm yếu:** creator phụ thuộc push email (không chủ động browse); brand-side pricing hoàn toàn mù mờ.

#### KOLs.com.vn
- **Mô hình:** **mâu thuẫn nội bộ** — marketing trình bày là two-sided marketplace self-apply, nhưng trang "Quy trình làm việc" của chính họ mô tả flow agency thủ công 3 bước; bảng giá do "Á Châu" (operator) cập nhật → thực chất agency-mediated.
- **Bảng giá công khai:** `/bang-gia/` ~60 cá nhân, flat per-booking 3M (dancer) → 85M VND (ca sĩ Đông Nhi), đa số 15–30M. Ngân sách dự án trên `/du-an/` khiêm tốn ~500K–15M/collab.
- **Điểm yếu lớn:** quy mô tự báo **nhỏ + mâu thuẫn** (40+ KOL, 27+ nhãn hàng vs "500+ dự án/tháng"); data liên hệ có dấu hiệu **placeholder/template** (hotline "0901 234 567", email lệch domain "contact@kol.com.vn", credit "dev.com.vn"); nhiều trang quy trình trả 404 → **độ trưởng thành/uy tín đáng nghi nhất** trong 3 đối thủ.

### Đính chính so với bản trước

Bảng so sánh phiên bản đầu (gộp Hiip/KOLs.com.vn 1 cột) có một số mô tả sai so với thực tế đã verify:

| Mục | Bản trước (❌) | Thực tế đã verify (✅) |
|-----|---------------|----------------------|
| Revu — Job listing | "AM đề xuất thủ công" | Niêm yết **mở**, creator **tự ứng tuyển** job còn hạn (mảng REVUers) |
| Revu — Tham gia | "Revu match & contact creator" | **Open self-application** (đăng ký → kết nối MXH → apply) |
| Revu — Nộp bài | "Qua email/zalo với AM" | Submit **trên platform**, có **pre-publish review** |
| Hiip — Tham gia | "Creator tự apply" | **Brand-initiated**: hệ thống đẩy job qua email, creator submit báo giá (không browse-apply) |
| Hiip/KOLs gộp chung | 1 cột chung | Tách riêng — 2 mô hình **rất khác** (Hiip managed-tech vs KOLs agency thủ công) |

### Caveats — giới hạn độ tin cậy

- Hầu hết **số liệu quy mô** (số influencer/brand/năm/chiến dịch) là marketing tự báo, **không kiểm toán độc lập**, thường mâu thuẫn ngay trong site đối thủ — chỉ nên xem là claim định vị.
- **Revu:** vắng mặt e-contract cho creator là "không có bằng chứng công khai", **không** đồng nghĩa chắc chắn không tồn tại nội bộ. Số liệu mâu thuẫn lan rộng ≥4 trang.
- **Hiip:** mô tả công nghệ "ML + image recognition + NLP" là self-description marketing, **không có corroboration độc lập**. Brand-side pricing (commission, min budget) hoàn toàn không công khai; min budget ~$1K là ước tính nguồn ngoài.
- **KOLs.com.vn:** mâu thuẫn giữa marketing self-apply và quy trình agency thủ công; data liên hệ dạng placeholder; nhiều trang (`/quy-trinh-kols/`, `/san-pham/`) trả **404** → không truy xuất được quy trình end-to-end.
- Ranh giới mô hình (self-serve vs agency vs hybrid) dựa trên cách đối thủ **tự trình bày công khai** + corroboration hạn chế; vận hành nội bộ thực tế có thể khác.

---

## Chi tiết 5 module cần build

> 5 module theo thứ tự ưu tiên triển khai.

### ① Job Listing
Brand/Admin tạo job với brief, ngân sách, quota. KOC thấy feed job được filter theo **tier** và **platform** của họ.

- Tạo job: tên, mô tả, yêu cầu, ngân sách, timeline, quota KOC
- Điều kiện tham gia: tier / follower min, platform, ngành/niche
- Hiển thị cho KOC: feed phù hợp profile, filter platform/tier, deadline đăng ký

### ② Tham gia Job
KOC apply → Admin duyệt → hệ thống tự gửi brief và hướng dẫn. Cần **workflow approval** và **notification**.

- KOC apply: chọn job → apply, xem brief trước, status `Pending`
- Admin duyệt: review profile KOC, approve/reject, notify KOC
- Gửi brief + HD: file brief tự động gửi, hướng dẫn nộp bài, deadline content

### ③ Nộp bài Content
KOC submit link + proof → Admin review (**tối đa 2 lần revise**) → track performance tự động (view, đơn, GMV).
**→ Đây là module phức tạp nhất về logic.**

- KOC submit: link post/video, thời gian đăng, screenshot proof
- Review bài: admin check content, pass / yêu cầu sửa, max 2 lần revise
- Track performance: view/like/comment, đơn/GMV (nếu affiliate), auto-update KPI

### ④ Ký HĐ điện tử
Template HĐ tự động điền theo job, KOC ký bằng **OTP/eSign**, lưu PDF có timestamp.
Cần tích hợp **eSign provider** (VD: VNPT eSign, Esign.vn, hoặc DocuSign).

- Tạo HĐ tự động: template theo job type, fill tên/số tiền, điều khoản chuẩn
- KOC ký số: OTP/eSign, xác nhận điều khoản, lưu PDF có timestamp
- Lưu trữ + pháp lý: HĐ 2 bên đã ký, gắn với job ID, download anytime

### ⑤ Thanh toán
Triggered sau khi bài approved → Finance xác nhận → upload proof → KOC nhận notification và xác nhận.
Cần gắn chặt với module ④ (**HĐ là điều kiện để TT**).

- Xét duyệt TT: sau khi bài approved, Finance xác nhận, status `Pending pay`
- Thực hiện TT: chuyển khoản/ví, upload bill proof, status `Paid`
- KOC xem & xác nhận: lịch sử thanh toán, thông báo real-time, xác nhận nhận tiền

---

*Tài liệu tạo từ sơ đồ thiết kế mô hình Booking trên Ambassador. Phần "So sánh với đối thủ" được fact-check qua research đa nguồn (2026-06-24): web search → deep-read trang chính thức Revu/Hiip/KOLs.com.vn → adversarial verify (241 findings, 22 confirmed, 2 refuted). Số liệu quy mô là marketing tự báo — đọc kèm Caveats.*
