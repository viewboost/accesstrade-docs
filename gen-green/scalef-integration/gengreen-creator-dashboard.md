# Creator Dashboard — Gen-Green + Green Seller

> **Ngày:** 2026-04-01
> **Liên quan:** [Tích hợp Scalef Affiliate](./gengreen-scalef-affiliate-integration-proposal.md) · [Liên kết tài khoản](./gengreen-scalef-account-linking.md)

---

## 1. Vấn đề

Creator trên Gen-Green hiện chỉ thấy thu nhập từ nội dung. Sau khi tích hợp Scalef, creator có thêm thu nhập từ bán hàng affiliate. Cần 1 dashboard mới gộp cả 2 nguồn.

**2 nguồn thu nhập:**
- **Gen-Green** — tiền từ sáng tạo nội dung (lượt xem, thích, bình luận)
- **Green Seller** — hoa hồng từ bán hàng affiliate (click → đơn hàng → hoa hồng)

**Cùng 4 trạng thái tiền:**
Chờ duyệt → Đã duyệt → Đã đối soát → Đã thanh toán

---

## 2. Cấu trúc: 3 tầng

```
Tầng 1: Tổng quan             ← nhìn 1 cái biết tổng thu nhập
    │
    ├── Tầng 2: Gen-Green          ← thu nhập nội dung, nhóm theo đối tác
    │   ├── VinPearl
    │   │   ├── Mùa hè xanh 2026  ←── Tầng 3: drill-down chi tiết
    │   │   └── Du lịch xanh Q2
    │   ├── Vincom
    │   │   └── Vincom Shopping Fest
    │   └── VinHome
    │       └── Sống xanh cùng VinHome
    │
    └── Tầng 2: Green Seller       ← thu nhập bán hàng, nhóm theo đối tác
        ├── VinPearl
        │   └── VinPearl Booking  ←── Tầng 3: drill-down chi tiết
        ├── Vincom
        │   └── Vincom E-Shop
        └── VinHome
            └── VinHome Referral
```

---

## 3. Mockup

### Tầng 1: Tổng quan

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  THU NHẬP CỦA TÔI                                    Tháng 4, 2026 ▼  │
│                                                                          │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌──────────────┐ │
│  │ Chờ duyệt     │ │ Đã duyệt      │ │ Đã đối soát   │ │ Đã thanh toán│ │
│  │               │ │               │ │               │ │              │ │
│  │  2.500.000đ   │ │  1.800.000đ   │ │  5.200.000đ   │ │  4.100.000đ │ │
│  │               │ │               │ │               │ │              │ │
│  │ Gen-Green     │ │ Gen-Green     │ │ Gen-Green     │ │ Gen-Green    │ │
│  │   1.500.000   │ │   1.000.000   │ │   3.200.000   │ │   3.000.000  │ │
│  │ Green Seller  │ │ Green Seller  │ │ Green Seller  │ │ Green Seller │ │
│  │   1.000.000   │ │     800.000   │ │   2.000.000   │ │   1.100.000  │ │
│  └───────────────┘ └───────────────┘ └───────────────┘ └──────────────┘ │
│                                                                          │
│  Thu nhập 30 ngày gần nhất                                               │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │  5tr ┤                                                           │    │
│  │      ┤          ██                                               │    │
│  │  3tr ┤    ▓▓    ██▓▓          ██                                 │    │
│  │      ┤    ██▓▓  ████    ▓▓    ██▓▓                               │    │
│  │  1tr ┤  ▓▓████  ████  ▓▓██  ▓▓████                              │    │
│  │      └────────────────────────────────────────                   │    │
│  │       01/04  05/04  10/04  15/04  20/04  25/04  30/04           │    │
│  │                                                                  │    │
│  │  ██ Gen-Green   ▓▓ Green Seller                                  │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                          │
│  [ Gen-Green ]    [ Green Seller ]                                       │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

- 4 card: tổng gộp 2 nguồn, bên dưới mỗi card là breakdown nhỏ
- Biểu đồ cột chồng: Gen-Green + Green Seller theo ngày
- Chọn tháng bằng dropdown
- Bên dưới là 2 tab dẫn vào tầng 2

---

### Tầng 2: Tab Gen-Green

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  [ Gen-Green ]    [ Green Seller ]                                       │
│  ━━━━━━━━━━━━                                                            │
│                                                                          │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌──────────────┐ │
│  │ Chờ duyệt     │ │ Đã duyệt      │ │ Đã đối soát   │ │ Đã thanh toán│ │
│  │  1.500.000đ   │ │  1.000.000đ   │ │  3.200.000đ   │ │  3.000.000đ │ │
│  └───────────────┘ └───────────────┘ └───────────────┘ └──────────────┘ │
│                                                                          │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐                  │
│  │ Lượt xem      │ │ Lượt thích    │ │ Bình luận     │                  │
│  │    125.400    │ │     8.900     │ │     2.340     │                  │
│  └───────────────┘ └───────────────┘ └───────────────┘                  │
│                                                                          │
│  ── VinPearl ──────────────────────────────────────────────────────────  │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │  Mùa hè xanh 2026                                               │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │    │
│  │  │ 500.000đ │ │ 12.400   │ │    890   │ │    234   │           │    │
│  │  │ Thu nhập  │ │ Lượt xem │ │ Thích    │ │ Bình luận│           │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │    │
│  │  Trạng thái: Chờ đối soát                          [Xem →]    │    │
│  ├──────────────────────────────────────────────────────────────────┤    │
│  │  Du lịch xanh Q2                                                │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │    │
│  │  │ 300.000đ │ │  8.100   │ │    520   │ │    112   │           │    │
│  │  │ Thu nhập  │ │ Lượt xem │ │ Thích    │ │ Bình luận│           │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │    │
│  │  Trạng thái: Chờ duyệt                             [Xem →]    │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ── Vincom ────────────────────────────────────────────────────────────  │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │  Vincom Shopping Fest                                            │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │    │
│  │  │ 400.000đ │ │ 22.300   │ │  1.800   │ │    456   │           │    │
│  │  │ Thu nhập  │ │ Lượt xem │ │ Thích    │ │ Bình luận│           │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │    │
│  │  Trạng thái: Đã thanh toán                         [Xem →]    │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ── VinHome ───────────────────────────────────────────────────────────  │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │  Sống xanh cùng VinHome                                         │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │    │
│  │  │ 300.000đ │ │ 15.600   │ │  1.200   │ │    321   │           │    │
│  │  │ Thu nhập  │ │ Lượt xem │ │ Thích    │ │ Bình luận│           │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │    │
│  │  Trạng thái: Đã đối soát                           [Xem →]    │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

- 4 card tiền: chỉ phần Gen-Green
- 3 card: tổng lượt xem, thích, bình luận
- Chiến dịch nhóm theo đối tác (VinPearl / Vincom / VinHome)
- Bấm [Xem →] vào tầng 3

---

### Tầng 2: Tab Green Seller

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  [ Gen-Green ]    [ Green Seller ]                                       │
│                    ━━━━━━━━━━━━━━                                        │
│                                                                          │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌──────────────┐ │
│  │ Chờ duyệt     │ │ Đã duyệt      │ │ Đã đối soát   │ │ Đã thanh toán│ │
│  │  1.000.000đ   │ │    800.000đ   │ │  2.000.000đ   │ │  1.100.000đ │ │
│  └───────────────┘ └───────────────┘ └───────────────┘ └──────────────┘ │
│                                                                          │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐                  │
│  │ Lượt click    │ │ Đơn hàng      │ │ Doanh số      │                  │
│  │     1.234     │ │        45     │ │  8.500.000đ   │                  │
│  └───────────────┘ └───────────────┘ └───────────────┘                  │
│                                                                          │
│  ── VinPearl ──────────────────────────────────────────────────────────  │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │  VinPearl Booking                                                │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │    │
│  │  │ 500.000đ │ │    450   │ │     18   │ │3.600.000đ│           │    │
│  │  │ Hoa hồng │ │ Click    │ │ Đơn hàng │ │ Doanh số │           │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │    │
│  │  Trạng thái: Chờ đối soát                          [Xem →]    │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ── Vincom ────────────────────────────────────────────────────────────  │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │  Vincom E-Shop                                                   │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │    │
│  │  │ 300.000đ │ │    540   │ │     20   │ │3.200.000đ│           │    │
│  │  │ Hoa hồng │ │ Click    │ │ Đơn hàng │ │ Doanh số │           │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │    │
│  │  Trạng thái: Đã duyệt                              [Xem →]    │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ── VinHome ───────────────────────────────────────────────────────────  │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │  VinHome Referral                                                │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │    │
│  │  │ 200.000đ │ │    244   │ │      7   │ │1.700.000đ│           │    │
│  │  │ Hoa hồng │ │ Click    │ │ Đơn hàng │ │ Doanh số │           │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │    │
│  │  Trạng thái: Chờ duyệt                             [Xem →]    │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

- 4 card hoa hồng: chỉ phần Green Seller
- 3 card: tổng click, đơn hàng, doanh số
- Danh sách chiến dịch affiliate, mỗi dòng: hoa hồng + click + đơn + doanh số
- Bấm [Xem →] vào tầng 3

**Nếu chưa liên kết Scalef** — tab Green Seller hiện:

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│   Bắt đầu kiếm tiền với Green Seller!                           │
│                                                                  │
│   Liên kết tài khoản Scalef để bán hàng affiliate               │
│   và nhận hoa hồng ngay trên Gen-Green.                         │
│                                                                  │
│                     [ Liên kết ngay ]                            │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

### Tầng 3: Chi tiết chiến dịch Gen-Green

Bấm [Xem →] trên 1 chiến dịch nội dung:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  ← Quay lại                                                             │
│                                                                          │
│  Mùa hè xanh 2026                                     Gen-Green         │
│  Đối tác: VinPearl  |  01/04 – 30/06/2026                               │
│                                                                          │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌──────────────┐ │
│  │ Thu nhập       │ │ Lượt xem      │ │ Lượt thích    │ │ Bình luận    │ │
│  │   500.000đ    │ │    12.400    │ │       890    │ │       234    │ │
│  └───────────────┘ └───────────────┘ └───────────────┘ └──────────────┘ │
│                                                                          │
│  Thu nhập theo trạng thái:                                               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ Chờ duyệt    │ │ Đã duyệt     │ │ Đã đối soát  │ │ Đã thanh toán│   │
│  │   100.000    │ │   150.000    │ │   250.000    │ │          0   │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
│                                                                          │
│  Theo nền tảng:                                                          │
│  ┌─────────────┬──────────┬──────────┬──────────┬──────────┐           │
│  │ Nền tảng    │ Lượt xem │ Thích    │ Bình luận│ Thu nhập  │           │
│  ├─────────────┼──────────┼──────────┼──────────┼──────────┤           │
│  │ TikTok      │    8.200 │      620 │      156 │  320.000 │           │
│  │ YouTube     │    3.100 │      180 │       52 │  130.000 │           │
│  │ Facebook    │    1.100 │       90 │       26 │   50.000 │           │
│  └─────────────┴──────────┴──────────┴──────────┴──────────┘           │
│                                                                          │
│  Bài đăng:                                                               │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │  TikTok  "Review sản phẩm xanh #muahexanh"                      │    │
│  │  Views: 5.200  Likes: 340  Comments: 89  |  Đã duyệt            │    │
│  │  Đăng lúc: 05/04/2026                                            │    │
│  ├──────────────────────────────────────────────────────────────────┤    │
│  │  TikTok  "Unbox quà tặng xanh"                                   │    │
│  │  Views: 3.000  Likes: 280  Comments: 67  |  Chờ duyệt           │    │
│  │  Đăng lúc: 12/04/2026                                            │    │
│  ├──────────────────────────────────────────────────────────────────┤    │
│  │  YouTube  "Vlog: 1 ngày sống xanh"                               │    │
│  │  Views: 3.100  Likes: 180  Comments: 52  |  Đã duyệt            │    │
│  │  Đăng lúc: 08/04/2026                                            │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

### Tầng 3: Chi tiết chiến dịch Green Seller

Bấm [Xem →] trên 1 chiến dịch affiliate:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  ← Quay lại                                                             │
│                                                                          │
│  VinPearl Booking                                     Green Seller       │
│  Đối tác: VinPearl  |  Hoa hồng: 25.000đ/đơn  |  01/04 – 30/06/2026   │
│                                                                          │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌──────────────┐ │
│  │ Hoa hồng      │ │ Lượt click    │ │ Đơn hàng      │ │ Doanh số     │ │
│  │   800.000đ    │ │       890    │ │        32    │ │  6.400.000đ │ │
│  └───────────────┘ └───────────────┘ └───────────────┘ └──────────────┘ │
│                                                                          │
│  Hoa hồng theo trạng thái:                                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ Chờ duyệt    │ │ Đã duyệt     │ │ Đã đối soát  │ │ Đã thanh toán│   │
│  │   200.000    │ │   150.000    │ │   350.000    │ │   100.000    │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
│                                                                          │
│  Click + đơn hàng (30 ngày):                                            │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │  50 ┤                                                            │    │
│  │     ┤  ██        ██                                              │    │
│  │  30 ┤  ██  ██    ████    ██                                      │    │
│  │     ┤  ████████  ██████  ████                                    │    │
│  │  10 ┤  ████████  ██████  ██████                                  │    │
│  │     └──────────────────────────────                              │    │
│  │  ██ Click   ▓▓ Đơn hàng                                         │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  Link affiliate:                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │  https://shorten.scalef.vn/taYj3UJV                    [Copy]   │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  Danh sách đơn hàng:                                                     │
│  ┌──────┬─────────────────┬────────────┬──────────┬───────────────┐     │
│  │  #   │ Mã đơn          │ Giá trị    │ Hoa hồng │ Trạng thái    │     │
│  ├──────┼─────────────────┼────────────┼──────────┼───────────────┤     │
│  │  1   │ AT_SP_001...    │   200.000  │   25.000 │ Đã duyệt      │     │
│  │  2   │ AT_SP_002...    │   350.000  │   25.000 │ Đã đối soát   │     │
│  │  3   │ AT_SP_003...    │   180.000  │   25.000 │ Chờ duyệt     │     │
│  │  4   │ AT_SP_004...    │   120.000  │   25.000 │ Đã thanh toán │     │
│  │ ...  │                 │            │          │               │     │
│  ├──────┴─────────────────┴────────────┴──────────┴───────────────┤     │
│  │                    1  2  3  ... 5  →                            │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Các tình huống đặc biệt

| Tình huống | Hiển thị |
|-----------|----------|
| Chưa liên kết Scalef | Tab Green Seller → onboarding card "Liên kết Scalef để bán hàng" |
| Dữ liệu Green Seller đang tải | Phần Gen-Green hiện bình thường, Green Seller hiện loading riêng |
| Creator chỉ làm nội dung | Tổng quan: breakdown Green Seller = 0, vẫn hiện |
| Creator chỉ bán hàng | Tổng quan: breakdown Gen-Green = 0, vẫn hiện |
| Không có dữ liệu tháng đó | "Chưa có dữ liệu cho tháng này" |

---

## 5. Thông số hiển thị

### Gen-Green (nội dung)

| Thông số | Ý nghĩa | Có ở tầng |
|----------|---------|----------|
| Thu nhập (4 trạng thái) | Tiền chờ duyệt / đã duyệt / đã đối soát / đã thanh toán | 1, 2, 3 |
| Lượt xem | Tổng view tất cả bài đăng | 2, 3 |
| Lượt thích | Tổng like | 2, 3 |
| Bình luận | Tổng comment | 2, 3 |
| Nền tảng | TikTok, YouTube, YouTube Shorts, Facebook, Facebook Reels, Instagram, Instagram Reels | 3 |
| Bài đăng | Tiêu đề, link, nền tảng, view/like/comment, trạng thái duyệt, ngày đăng | 3 |

### Green Seller (bán hàng)

| Thông số | Ý nghĩa | Có ở tầng |
|----------|---------|----------|
| Hoa hồng (4 trạng thái) | Commission chờ duyệt / đã duyệt / đã đối soát / đã thanh toán | 1, 2, 3 |
| Lượt click | Số lần click vào link affiliate | 2, 3 |
| Đơn hàng | Số đơn hàng phát sinh | 2, 3 |
| Doanh số | Tổng giá trị đơn hàng | 2, 3 |
| Link affiliate | Link rút gọn + nút Copy | 3 |
| Biểu đồ click/đơn | Theo ngày, 30 ngày gần nhất | 3 |
| Danh sách đơn hàng | Mã đơn, giá trị, hoa hồng, trạng thái, phân trang | 3 |

### Mapping trạng thái tiền

| Cột trên dashboard | Gen-Green | Green Seller (Scalef) |
|-------------------|----------|----------------------|
| Chờ duyệt | pending | WAITING_FOR_APPROVED + TEMPORARY_APPROVED |
| Đã duyệt | approved | APPROVED |
| Đã đối soát | cashback | Có campaign_invoice_id |
| Đã thanh toán | transfer | calculate_status = CALCULATED |

---

<details>
<summary><strong>Phụ lục kỹ thuật (dành cho dev)</strong></summary>

## A. Dữ liệu Gen-Green hiện có

Từ API `/user-statistic`, cấu trúc `UserStats`:

```typescript
type Stats = {
  total: number;
  pending: number;     // chờ duyệt
  approved: number;    // đã duyệt
  cashback: number;    // đã đối soát
  transfer: number;    // đã thanh toán
}

type UserStats = {
  totalInvitee: number;
  cash: Stats;
  view: Stats;
  like: Stats;
  comment: Stats;
}
```

Chi tiết theo event có thêm breakdown platform:
- tiktok, youtube, youtube_shorts, facebook, facebook_reels, instagram, instagram_reels
- Mỗi platform: `{point, view, like, comment, cash}` với `Point = {total, pending, rejected, completed}`

Chi tiết content: source, title, link, view/like/comment totals, status, publishedAt.

## B. Dữ liệu Green Seller từ Scalef API

| API | Dữ liệu |
|-----|---------|
| API 3.1 Click | Tổng click theo ngày. `meta.total`, `statistics` (epoch → count) |
| API 3.2 Conversion | Tổng đơn hàng theo ngày. `meta.total`, `statistics` |
| API 3.3 Sale Amount | Doanh số theo trạng thái. `statistic_details`: REJECTED, WAITING_FOR_APPROVED, APPROVED, TEMPORARY_APPROVED |
| API 3.4 Commission | Hoa hồng theo trạng thái. Cấu trúc giống Sale Amount |
| API 8 Conversions | Danh sách đơn chi tiết. campaign_name, total_pub_com, total_sale_amount, conversion_sale_time, calculate_status |

Chi tiết: [API Reference Pub2](../pub2-affiliate-integration/api-reference.md)

## C. API gộp đề xuất

Frontend gọi 1 endpoint, backend gộp 2 nguồn:

```
GET /api/creator/dashboard?month=2026-04
Authorization: Bearer {token}
```

Response:
```json
{
  "summary": {
    "pending":    { "total": 2500000, "gen_green": 1500000, "green_seller": 1000000 },
    "approved":   { "total": 1800000, "gen_green": 1000000, "green_seller": 800000 },
    "reconciled": { "total": 5200000, "gen_green": 3200000, "green_seller": 2000000 },
    "paid":       { "total": 4100000, "gen_green": 3000000, "green_seller": 1100000 }
  },
  "chart_30d": {
    "labels": ["2026-04-01", "2026-04-02"],
    "gen_green": [50000, 120000],
    "green_seller": [0, 80000]
  },
  "gen_green": {
    "cash":    { "pending": 1500000, "approved": 1000000, "cashback": 3200000, "transfer": 3000000 },
    "view":    { "total": 125400 },
    "like":    { "total": 8900 },
    "comment": { "total": 2340 },
    "campaigns": [
      {
        "id": "evt_001", "name": "Mùa hè xanh 2026", "partner": "VinGroup",
        "cash": 500000, "view": 12400, "like": 890, "comment": 234,
        "status": "reconciling"
      }
    ]
  },
  "green_seller": {
    "linked": true,
    "commission": { "pending": 1000000, "approved": 800000, "reconciled": 2000000, "paid": 1100000 },
    "click": { "total": 1234 },
    "conversion": { "total": 45 },
    "sale_amount": { "total": 8500000 },
    "campaigns": [
      {
        "id": "camp_001", "name": "Shopee Smartlink",
        "commission_rate": "25.000đ/đơn",
        "commission": 800000, "click": 890, "conversion": 32, "sale_amount": 6400000,
        "status": "reconciling"
      }
    ]
  }
}
```

`green_seller.linked = false` → frontend hiện onboarding card.

Chi tiết chiến dịch: `GET /api/creator/dashboard/campaign/:id`

</details>

---

*Tham chiếu: [Tích hợp Scalef Affiliate](./gengreen-scalef-affiliate-integration-proposal.md) · [API Reference Pub2](../pub2-affiliate-integration/api-reference.md)*
