# PRD: Hiển thị mức tiền hoàn tạm tính khi user dán link tại MSHT

## Mục lục

1. [Tổng quan](#1-tổng-quan-overview)
2. [Bối cảnh & Vấn đề](#2-bối-cảnh--vấn-đề-problem-statement)
3. [Mục tiêu & Success Metrics](#3-mục-tiêu--success-metrics)
4. [Đối tượng người dùng](#4-đối-tượng-người-dùng-target-users)
5. [User Stories](#5-user-stories)
6. [Yêu cầu chức năng](#6-yêu-cầu-chức-năng-functional-requirements)
7. [Yêu cầu kỹ thuật](#7-yêu-cầu-kỹ-thuật-technical-requirements)
8. [Edge Cases](#8-edge-cases)
9. [Non-Goals](#9-non-goals-out-of-scope-mvp)
10. [Rủi ro & Giải pháp](#10-rủi-ro--giải-pháp)
11. [Tracking & Analytics](#11-tracking--analytics)
12. [Timeline & Milestones](#12-timeline--milestones-đề-xuất)
13. [Open Questions](#13-open-questions)
14. [Phụ lục](#14-phụ-lục)

---

## 1. Tổng quan (Overview)

Tính năng cho phép user dán link sản phẩm từ các sàn TMĐT (Shopee, Lazada, Tiki...) vào MSHT để **xem trước mức tiền hoàn dự kiến** trước khi quyết định mua, giúp user ra quyết định nhanh và chính xác hơn, đồng thời giảm tỉ lệ thất vọng sau khi đặt hàng.

> 📐 **Thiết kế UX/UI chi tiết**: xem file [wireframes.md](./wireframes.md)

---

## 2. Bối cảnh & Vấn đề (Problem Statement)

### 2.1 Vấn đề hiện tại

- User **không biết** sản phẩm mình định mua có được hoàn tiền hay không, hoàn nhiều hay ít → khó ra quyết định mua.
- Thời gian chờ kết quả hoàn tiền: **nhanh nhất 48h, trung bình 70 ngày**.
- Khi nhận kết quả, một bộ phận user **thất vọng** vì:
  - Tiền hoàn = 0đ (sản phẩm thuộc ngành hàng không hoàn tiền)
  - Tiền hoàn thấp hơn kỳ vọng
- → **Rủi ro mất user mới** nếu trải nghiệm đầu tiên rơi vào tình huống thất vọng.

### 2.2 Cơ hội

- Đối thủ Shopback đã triển khai tính năng tương tự (có showcase tham khảo).
- AT (AccessTrade) đã cung cấp sẵn API để lấy giá và % hoàn tiền của sản phẩm → giảm chi phí phát triển.

### 2.3 Công thức tính tiền hoàn dự kiến

```
Tiền hoàn dự kiến = Transaction × % hoàn tiền
Tiền hoàn dự kiến = Tiền hoàn base + Tiền hoàn bonus
```

> **Lưu ý:** Tiền hoàn dự kiến có thể thay đổi so với thực tế vì tỉ lệ hoàn tiền có thể điều chỉnh theo từng ngày.

---

## 3. Mục tiêu & Success Metrics

### 3.1 Mục tiêu kinh doanh

| Mục tiêu | Mô tả |
|---|---|
| **Tăng conversion rate** | User paste link → click CTA mua hàng |
| **Giảm churn user mới** | Giảm tỉ lệ user mới rời bỏ sau trải nghiệm hoàn 0đ |
| **Tăng GMV** | Tăng tổng giá trị đơn hàng qua MSHT |

### 3.2 Success Metrics

| Metric | Mục tiêu MVP | Cách đo |
|---|---|---|
| **CTR** (Paste link → CTA mua hàng) | ≥ 60% | Tracking event |
| **Conversion rate** (Paste link → đơn hàng thành công) | Tăng ≥ 20% so với baseline | Data team |
| **Tỉ lệ complaint hoàn 0đ** | Giảm ≥ 30% | CS ticket |
| **Retention D30 user mới** | Tăng ≥ 10% | Analytics |
| **API response time** | < 2s (p95) | APM |

---

## 4. Đối tượng người dùng (Target Users)

### 4.1 Primary
- User đã đăng nhập MSHT, có nhu cầu mua hàng qua link affiliate.

### 4.2 Use cases điển hình
- User thấy sản phẩm trên Facebook/TikTok → copy link → mở MSHT → paste → check tiền hoàn → quyết định mua.
- User đang lưỡng lự giữa 2 sản phẩm → so sánh tiền hoàn → chọn cái có hoàn cao hơn.

---

## 5. User Stories

| ID | User Story | Priority |
|---|---|---|
| US-01 | Là user, tôi muốn **dán link sản phẩm** và xem được **số tiền hoàn dự kiến** trước khi mua, để quyết định có nên mua hay không. | P0 |
| US-02 | Là user, tôi muốn biết **rõ ràng** khi sản phẩm **không có hoàn tiền** để không kỳ vọng sai. | P0 |
| US-03 | Là user, tôi muốn **click trực tiếp CTA** để được redirect đến sản phẩm và mua hàng. | P0 |
| US-04 | Là user, tôi muốn hiểu rằng số tiền hoàn là **dự kiến** và có thể thay đổi. | P1 |
| US-05 | Là user, tôi muốn được gợi ý sản phẩm tương tự có hoàn tiền cao nếu sản phẩm hiện tại không có hoàn. | P2 |

---

## 6. Yêu cầu chức năng (Functional Requirements)

### 6.1 Luồng UX chính

**Nguyên tắc thiết kế:** Việc hiển thị tiền hoàn tạm tính là phần **enhancement (best-effort)** được thêm vào luồng mua hàng đã có sẵn. Nó **không được phép chặn** luồng CTA mua hàng. CTA mua hàng chỉ phụ thuộc vào việc tạo được affiliate link (API gen link), **không phụ thuộc** vào việc lấy được thông tin sản phẩm (API AT).

Sau khi parse link thành công, FE gọi **2 API song song (parallel)**:

| API | Vai trò | Mức độ quan trọng |
|---|---|---|
| **API gen link** (luồng cũ) | Tạo affiliate link để redirect mua hàng | **Bắt buộc** — lỗi thì chặn |
| **API AT lấy thông tin sản phẩm** (mới) | Lấy giá + % hoàn để hiển thị tiền hoàn tạm tính | **Best-effort** — lỗi thì bỏ qua, không chặn |

```
[User paste link]
      ↓
[Validate & Parse link]
      ↓
[Gọi SONG SONG 2 API]
   ├── API gen link (bắt buộc)
   └── API AT lấy thông tin sản phẩm (best-effort)
      ↓
   ┌──────────────────────────────────────────────────────────┐
   │ Ma trận kết quả                                          │
   ├──────────────┬─────────────┬─────────────────────────────┤
   │ Gen link     │ API AT      │ Kết quả hiển thị            │
   ├──────────────┼─────────────┼─────────────────────────────┤
   │ ❌ Lỗi       │ (bất kỳ)    │ Báo lỗi (luồng cũ).         │
   │              │             │ KHÔNG hiện tiền hoàn,       │
   │              │             │ KHÔNG có CTA mua hàng.      │
   ├──────────────┼─────────────┼─────────────────────────────┤
   │ ✅ OK        │ ❌ Lỗi      │ Ẩn tiền hoàn tạm tính.      │
   │              │             │ Hiện thông báo mềm +        │
   │              │             │ CTA mua hàng (vẫn đi tiếp). │
   ├──────────────┼─────────────┼─────────────────────────────┤
   │ ✅ OK        │ ✅ OK       │ Happy case: hiện đầy đủ     │
   │              │             │ tiền hoàn tạm tính + CTA.   │
   └──────────────┴─────────────┴─────────────────────────────┘
      ↓
[CTA mua hàng → Redirect qua affiliate link]
```

### 6.2 Chi tiết các màn hình

> 📐 **Xem chi tiết wireframes**: [wireframes.md](./wireframes.md)

#### Màn 1: Input link

> 🖼️ Tham khảo giao diện màn nhập link (ảnh thiết kế).

Bố cục card (trạng thái **Active**):
- **Logo các sàn hỗ trợ** hiển thị ngay đầu card: **Shopee**, **TikTok Shop**, **Lazada**
- Link **"Hướng dẫn ›"** (góc phải trên) → mở hướng dẫn cách sao chép link sản phẩm
- **Tiêu đề**: "TỐI ĐA TIỀN HOÀN TRÊN SHOPEE"
- **Mô tả**: "Sao chép link sản phẩm từ Shopee, TikTok Shop, Lazada và dán vào ô bên dưới."
- **Input field** cho user dán link (icon 🔗) + **button "Mua ngay"** (inline bên phải input)
  - Button disabled khi input rỗng
- **Footer note**: "Mua đúng sản phẩm được chuyển hướng đến"
- Hỗ trợ sàn: **Shopee, TikTok Shop, Lazada** (MVP)

#### Màn 2: Loading
- Skeleton/spinner trong khi gọi **2 API song song** (gen link + API AT)
- Điều kiện thoát loading: khi **cả 2 API đã có kết quả** (thành công hoặc lỗi/timeout)
- Timeout 5s áp dụng độc lập cho từng API:
  - API gen link timeout/lỗi → báo lỗi theo luồng cũ (không có CTA mua hàng vì chưa tạo được affiliate link)
  - API AT timeout/lỗi (gen link OK) → đi nhánh thông báo mềm (Màn 3b)

#### Màn 3: Kết quả – Có hoàn tiền (Happy path — TH#3: gen link OK + API AT OK)
Hiển thị:
- Ảnh + tên sản phẩm
- **Giá sản phẩm** (VND)
- **% hoàn tiền** (base + bonus, breakdown nếu có)
- **Tiền hoàn dự kiến** (VND) – nổi bật, font lớn
- **Disclaimer**: "Số tiền hoàn có thể thay đổi tùy theo chính sách từng ngày"
- CTA chính: **"Mua ngay & nhận hoàn tiền"**

#### Màn 3b: Kết quả – Không lấy được tạm tính (TH#2: gen link OK + API AT lỗi/timeout)
Trường hợp này affiliate link đã tạo được nên **vẫn cho user mua hàng**, chỉ thiếu phần tạm tính.
- **Ẩn hoàn toàn** phần thông tin sản phẩm + tiền hoàn tạm tính (không hiện số, không hiện skeleton lỗi)
- **Thông báo mềm** (trấn an, không phải báo lỗi): *"Hiện chưa tạm tính được hoàn tiền, nhưng bạn vẫn được hoàn tiền như bình thường khi mua qua đây 🎁"*
- (Tùy chọn) Link/nút phụ **"Thử lại"** để gọi lại API AT (chỉ gọi lại API AT, không gọi lại gen link)
- CTA chính **vẫn nổi bật, không thay đổi**: **"Mua ngay & nhận hoàn tiền"**
- > ⚠️ Lưu ý design: màn này **bắt buộc có CTA mua hàng**. Không được biến thành error state chặn user.

#### Màn 4: Kết quả – Không có hoàn tiền (0đ)
- Thông báo rõ ràng: "Sản phẩm này hiện **không có hoàn tiền**"
- Lý do: ngành hàng không thuộc danh mục hoàn tiền
- (Phase 2) Gợi ý sản phẩm/danh mục tương tự có hoàn tiền
- CTA phụ: "Xem sản phẩm khác có hoàn tiền"

#### Màn 5: Error state (chỉ dành cho lỗi chặn — không tạo được affiliate link)
Đây là các lỗi khiến **không có gì để mua** nên chặn là đúng. Phân biệt rõ với TH#2 (API AT lỗi) ở Màn 3b — TH#2 KHÔNG phải error state.

- **Màn 5b — Link không hợp lệ**: "Link không hợp lệ, vui lòng kiểm tra lại"

> **Quan trọng:** Lỗi của **API AT lấy thông tin sản phẩm KHÔNG đi vào Màn 5** — nó đi vào **Màn 3b** (thông báo mềm + CTA mua hàng) vì affiliate link vẫn tạo được.

---

## 7. Yêu cầu kỹ thuật (Technical Requirements)

### 7.1 APIs sử dụng

| API | Mục đích | Doc |
|---|---|---|
| AT Document API | Lấy thông tin sản phẩm + % hoàn base | [Postman](https://documenter.getpostman.com/view/28946819/2sB2qaj2UM) |
| AT Brand Bonus Shopee API | Lấy % bonus theo brand | [AccessTrade Dev](https://developers.accesstrade.vn/api-publisher-vietnamese/lay-danh-sach-giao-dich) |

### 7.2 Backend
- Endpoint mới: `POST /api/v1/cashback/estimate`
  - Input: `{ link: string }`
  - Output: `{ product_info, cashback_amount, cashback_rate, breakdown, affiliate_link }`
- Logic:
  - Parse link → extract platform + product ID
  - Call AT API (parallel: product info + brand bonus)
  - Calculate cashback amount
  - Generate affiliate link
- **Caching**: Cache response 5-15 phút theo product ID để giảm tải API AT.
- **Rate limiting**: 30 req/min/user.
- **Error handling**: timeout 5s, retry 1 lần.

### 7.3 Frontend
- Component mới: `CashbackEstimator`
- States: idle, loading, success, no-cashback, error
- Responsive: mobile-first

### 7.4 Non-functional
- API response time p95 < 2s
- Availability ≥ 99.5%
- Support latest 2 versions của iOS/Android

---

## 8. Edge Cases

| Case | Xử lý |
|---|---|
| Link rút gọn (bit.ly, shope.ee) | Resolve link trước khi parse |
| Link sản phẩm hết hàng | Vẫn hiển thị thông tin + cảnh báo "Sản phẩm có thể hết hàng" |
| Link sản phẩm khuyến mãi (flash sale) | Hiển thị giá hiện tại, lưu ý giá có thể thay đổi |
| User paste cùng link nhiều lần | Dùng cache, không gọi API lặp |
| Link không phải sàn TMĐT | Báo lỗi rõ ràng |
| API AT trả về data không đầy đủ | Fallback hiển thị phần khả dụng + báo "Không thể lấy đầy đủ thông tin" |
| **Gen link OK + API AT lỗi/timeout** | Đi Màn 3b: ẩn tạm tính + thông báo mềm, **vẫn hiện CTA mua hàng** (không chặn) |
| **Gen link lỗi** | Báo lỗi theo luồng cũ + "Thử lại", **không** hiện tạm tính, **không** CTA mua hàng (chưa có affiliate link) |
| **1 API trả về trước, 1 API còn đang chờ** | Chờ cả 2 API có kết quả mới render màn cuối (tránh nhấp nháy UI giữa các state) |
| **API AT chậm hơn timeout nhưng vẫn trả về sau** | Bỏ qua response trễ (đã render Màn 3b), không update ngược lại UI để tránh giật |

---

## 9. Non-Goals (Out of Scope MVP)

- Hiển thị review/rating sản phẩm
- So sánh giá giữa các sàn
- Thông báo khi % hoàn tiền thay đổi
- Hỗ trợ tất cả sàn ngoài Shopee (Phase 2)
- Tính năng cho user chưa đăng nhập
- Recommendation sản phẩm tương tự (Phase 2)

---

## 10. Rủi ro & Giải pháp

| Rủi ro | Mức độ | Giải pháp |
|---|---|---|
| API AT chậm/không ổn định | Cao | Caching, timeout, **fallback Màn 3b: ẩn tạm tính + thông báo mềm + vẫn cho mua hàng** (không chặn conversion) |
| Tính năng tạm tính (mới) vô tình chặn luồng mua hàng (cũ) | Cao | Tách 2 API song song; CTA chỉ phụ thuộc gen link, độc lập với API AT |
| Tỉ lệ hoàn thay đổi giữa lúc xem và lúc mua | Cao | Disclaimer rõ ràng, log lại snapshot |
| User vẫn thất vọng dù đã có dự kiến | Trung bình | UX rõ ràng phần "dự kiến", có FAQ |
| Tỉ lệ parse link sai do format mới | Trung bình | Monitor + alert, update parser |
| Lạm dụng API (spam) | Thấp | Rate limit |
| User chia sẻ link không phải sản phẩm | Thấp | Validation chặt chẽ |

---

## 11. Tracking & Analytics

### 11.1 Events cần track

| Event | Properties |
|---|---|
| `cashback_estimator_opened` | source (home, deeplink...) |
| `link_pasted` | platform (shopee/lazada...), link_valid |
| `cashback_estimated_shown` | cashback_amount, cashback_rate, has_bonus |
| `cashback_zero_shown` | reason |
| `cashback_unavailable_shown` | reason (api_at_error/api_at_timeout) — TH#2: Màn 3b, đã hiện CTA |
| `cta_buy_clicked` | cashback_amount (nullable), product_id (nullable), estimate_status (ok/unavailable) |
| `error_shown` | error_type (gen_link_error theo luồng cũ / invalid_link ở Màn 5b) |

### 11.2 Dashboard
- Conversion funnel: open → paste → see result → click CTA → order
- Phân tích theo platform, ngành hàng, mức % hoàn

---

## 12. Timeline & Milestones (Đề xuất)

| Tuần | Hoạt động | Owner |
|---|---|---|
| Tuần 1 | Finalize PRD + Design wireframe | PM, Design |
| Tuần 2 | High-fidelity design + Tech spec | Design, Tech Lead |
| Tuần 3-4 | Development (BE + FE) | Tech |
| Tuần 5 | QA + Internal UAT | QA |
| Tuần 6 | A/B test 50/50 release | PM, Data |
| Tuần 7-8 | Monitor + Iterate → Full rollout | PM |

---

## 13. Open Questions

- [ ] MVP có làm Shopee only hay bao gồm cả Lazada/Tiki?
- [ ] SLA của API AT là bao nhiêu? Cần ký thỏa thuận riêng không?
- [ ] Có A/B test không hay rollout 100% luôn?
- [ ] Có cần áp dụng cho user chưa đăng nhập (để acquire user mới)?
- [ ] Có cần làm push notification khi user có link trong clipboard không?

---

## 14. Phụ lục

### 14.1 Tài liệu tham khảo
- **Showcase tham khảo**: Video "Hiển thị hoàn tiền tạm tính - show case.mp4" (Shopback)
- **API Doc**:
  - Document API: https://documenter.getpostman.com/view/28946819/2sB2qaj2UM
  - Brand Bonus Shopee: https://developers.accesstrade.vn/api-publisher-vietnamese/lay-danh-sach-giao-dich
- **Source request**: "Hiển thị mức tiền hoàn tạm tính cho user khi dán link tại MSHT"

### 14.2 Lịch sử thay đổi

| Version | Ngày | Người thay đổi | Nội dung |
|---|---|---|---|
| v1.0 | 2026-06-01 | PM | Khởi tạo PRD |
| v1.1 | 2026-06-11 | PM | Tách phụ thuộc: FE gọi 2 API song song (gen link + API AT). Khi API AT lỗi/timeout vẫn cho mua hàng (Màn 3b: thông báo mềm + CTA). Tính năng tạm tính không còn chặn luồng mua hàng cũ. |

---

**End of Document**
