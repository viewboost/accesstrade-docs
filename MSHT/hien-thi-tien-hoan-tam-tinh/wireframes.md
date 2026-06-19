# Wireframes: Hiển thị mức tiền hoàn tạm tính tại MSHT

| | |
|---|---|
| **Phiên bản** | v1.0 |
| **Ngày tạo** | 2026-06-01 |
| **Trạng thái** | Draft |
| **Related docs** | [PRD](./PRD.md) |

---

## Mục lục

1. [Màn 1: Input Link (Idle State)](#1-màn-1-input-link-idle-state)
2. [Màn 2: Loading State](#2-màn-2-loading-state)
3. [Màn 3: Kết quả - Có hoàn tiền](#3-màn-3-kết-quả---có-hoàn-tiền-happy-path-)
4. [Màn 4: Kết quả - Không có hoàn tiền](#4-màn-4-kết-quả---không-có-hoàn-tiền-0đ-)
5. [Màn 5: Error States](#5-màn-5-error-states)
6. [Sơ đồ luồng tổng quan](#6-sơ-đồ-luồng-tổng-quan-flow-diagram)
7. [Components UI cần design](#7-components-ui-cần-design)
8. [Lưu ý cho Designer khi chuyển sang Hi-fi](#8-lưu-ý-cho-designer-khi-chuyển-sang-hi-fi)

---

## 1. Màn 1: Input Link (Idle State)

```
  Active
┌─────────────────────────────────────┐
│ [S] [TT] [Laz]          Hướng dẫn › │
│                                     │
│  TỐI ĐA TIỀN HOÀN TRÊN SHOPEE       │
│                                     │
│  Sao chép link sản phẩm từ Shopee,  │
│  Tiktok Shop, Lazada và dán vào ô   │
│  bên dưới.                          │
│                                     │
│  ┌──────────────────────┐ ┌───────┐ │
│  │ 🔗 https://s.shopee… │ │Mua ngay│ │
│  └──────────────────────┘ └───────┘ │
│                                     │
│  Mua đúng sản phẩm được chuyển      │
│  hướng đến                          │
│                                     │
└─────────────────────────────────────┘
```

**Ghi chú:**
- Logo các sàn hỗ trợ hiển thị đầu card: **Shopee, TikTok Shop, Lazada**
- Link **"Hướng dẫn ›"** (góc phải trên) → mở hướng dẫn cách sao chép link sản phẩm
- Tiêu đề: "TỐI ĐA TIỀN HOÀN TRÊN SHOPEE"
- Input field dán link + button **"Mua ngay"** (inline bên phải input)
- Button "Mua ngay" **disabled** khi input rỗng
- Footer note: "Mua đúng sản phẩm được chuyển hướng đến"

---

## 2. Màn 2: Loading State

```
┌─────────────────────────────────────┐
│  ←     Kiểm tra hoàn tiền      ⋮   │
├─────────────────────────────────────┤
│                                     │
│  ┌───────────────────────────────┐ │
│  │ 🔗 https://shopee.vn/prod...  │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ │
│  │ ░░░░░    [skeleton]    ░░░░ │ │
│  │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ │
│  │                              │ │
│  │ ░░░░░░░░░░░░░░░░░░           │ │
│  │ ░░░░░░░░░░░                  │ │
│  │                              │ │
│  │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ │
│  └───────────────────────────────┘ │
│                                     │
│        ⏳ Đang kiểm tra...          │
│                                     │
└─────────────────────────────────────┘
```

---

## 3. Màn 3: Kết quả - Có hoàn tiền (Happy Path) ⭐

```
┌─────────────────────────────────────┐
│  ←     Kết quả hoàn tiền       ⋮   │
├─────────────────────────────────────┤
│  ┌───────────────────────────────┐ │
│  │ ┌─────┐                       │ │
│  │ │     │ Áo thun unisex form   │ │
│  │ │ IMG │ rộng cotton 100%...   │ │
│  │ │     │                       │ │
│  │ └─────┘ 🛒 Shopee             │ │
│  │                               │ │
│  │ 💵 Giá: 250.000đ              │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  💰 TIỀN HOÀN DỰ KIẾN         │ │
│  │                               │ │
│  │      ┌─────────────────┐      │ │
│  │      │   25.000 đ      │      │ │
│  │      │   (10% hoàn)    │      │ │
│  │      └─────────────────┘      │ │
│  │                               │ │
│  │  ▾ Chi tiết:                  │ │
│  │   • Hoàn base: 15.000đ (6%)   │ │
│  │   • Bonus:     10.000đ (4%)🎁 │ │
│  └───────────────────────────────┘ │
│                                     │
│  ⚠️ Số tiền hoàn là dự kiến và có   │
│     thể thay đổi tùy chính sách     │
│     từng ngày                       │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  🛍️  Mua ngay & nhận hoàn     │ │
│  └───────────────────────────────┘ │
│                                     │
│       Kiểm tra link khác →          │
│                                     │
└─────────────────────────────────────┘
```

**Highlights:**
- Số tiền hoàn **nổi bật** ở giữa, font lớn
- Breakdown base + bonus rõ ràng (có thể collapse/expand)
- Disclaimer ngay dưới
- CTA chính **bold**, full-width

---

## 4. Màn 4: Kết quả - Không có hoàn tiền (0đ) ⚠️

```
┌─────────────────────────────────────┐
│  ←     Kết quả hoàn tiền       ⋮   │
├─────────────────────────────────────┤
│  ┌───────────────────────────────┐ │
│  │ ┌─────┐                       │ │
│  │ │ IMG │ Sách "Đắc Nhân Tâm"   │ │
│  │ │     │ 🛒 Shopee             │ │
│  │ └─────┘ 💵 Giá: 89.000đ       │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │         😔                    │ │
│  │                               │ │
│  │   Sản phẩm này hiện           │ │
│  │   KHÔNG CÓ HOÀN TIỀN          │ │
│  │                               │ │
│  │   Lý do: Ngành hàng "Sách"    │ │
│  │   không thuộc danh mục được   │ │
│  │   hoàn tiền của chương trình  │ │
│  └───────────────────────────────┘ │
│                                     │
│  💡 Gợi ý cho bạn:                  │
│  ┌───────────────────────────────┐ │
│  │ 🔥 Sản phẩm tương tự có hoàn  │ │
│  │                               │ │
│  │ [IMG] Sách KN... 5% hoàn  →  │ │
│  │ [IMG] Sách TC... 8% hoàn  →  │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │   Xem sản phẩm có hoàn tiền   │ │
│  └───────────────────────────────┘ │
│                                     │
│       Kiểm tra link khác →          │
│                                     │
└─────────────────────────────────────┘
```

**Lưu ý quan trọng:**
- Thông báo **0đ rõ ràng** ngay đầu để tránh kỳ vọng sai
- Giải thích **lý do** cụ thể
- Có gợi ý thay thế → giữ user trong app

---

## 5. Màn 5: Error States

> Chỉ dành cho **lỗi chặn** (không tạo được affiliate link). Lỗi API AT lấy tạm tính KHÔNG vào đây — xem Màn 3b (thông báo mềm + vẫn cho mua).

### 5b. Link không hợp lệ

```
┌─────────────────────────────────────┐
│  ←     Kiểm tra hoàn tiền      ⋮   │
├─────────────────────────────────────┤
│                                     │
│  ┌───────────────────────────────┐ │
│  │ 🔗 abc.xyz/some-random...     │ │
│  │                          [✕]  │ │
│  └───────────────────────────────┘ │
│  ❌ Link không hợp lệ               │
│                                     │
│  ┌───────────────────────────────┐ │
│  │         🔍                    │ │
│  │                               │ │
│  │   Không nhận diện được        │ │
│  │   sản phẩm từ link này        │ │
│  │                               │ │
│  │   Vui lòng kiểm tra lại link  │ │
│  │   hoặc copy lại từ ứng dụng   │ │
│  │   sàn TMĐT                    │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │       Thử lại                 │ │
│  └───────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

---

## 6. Sơ đồ luồng tổng quan (Flow Diagram)

```
┌──────────────┐
│  Entry Point │
│ (Home/Tab)   │
└──────┬───────┘
       ↓
┌──────────────┐
│  Màn 1:      │
│  Input Link  │
└──────┬───────┘
       ↓ [User dán link + tap CTA]
┌──────────────┐
│  Validate    │
│  link?       │
└──┬────────┬──┘
   │        │
   │ Invalid│ Valid
   ↓        ↓
┌─────┐  ┌─────────────┐
│ M5b │  │  Màn 2:     │
│Link │  │  Loading    │
│ lỗi │  │ (gen link + │
└─────┘  │  AT // song)│
         └──────┬──────┘
                ↓ [Call gen link + AT API song song]
         ┌──────────────┐
         │  API Result? │
         └──┬─────┬─────┴─┐
            │     │       │
       Success Zero    AT lỗi
            │     │       │
            ↓     ↓       ↓
         ┌────┐┌────┐ ┌──────┐
         │ M3 ││ M4 │ │ M3b  │
         └─┬──┘└─┬──┘ └──┬───┘
           │     │       │
   [CTA]   │     │[Gợi ý]│ [CTA vẫn hiện]
           ↓     ↓       ↓
      ┌────────────┐
      │ Redirect   │
      │ Affiliate  │
      └────────────┘
```

---

## 7. Components UI cần design

| Component | Mô tả | Reuse từ DS? |
|---|---|---|
| `LinkInput` | Input field + paste button | Có thể reuse |
| `LoadingSkeleton` | Skeleton placeholder | Có |
| `ProductCard` | Card hiển thị sản phẩm | Có |
| `CashbackHighlight` | Box hiển thị tiền hoàn nổi bật | **Mới** |
| `CashbackBreakdown` | Collapse list base + bonus | **Mới** |
| `EmptyState` | Trạng thái 0đ / error | Có |
| `RecommendationList` | List sản phẩm gợi ý | Có |
| `PrimaryCTA` | Button mua hàng | Có |

---

## 8. Lưu ý cho Designer khi chuyển sang Hi-fi

1. **Màu sắc tiền hoàn dự kiến**: dùng màu chủ đạo brand (vàng/cam) để gây chú ý
2. **Typography**: số tiền hoàn dùng font size lớn nhất (vd: 32-40pt)
3. **Animation**: micro-interaction khi reveal kết quả (số tiền đếm tăng dần)
4. **Empty state cho 0đ**: tránh dùng màu đỏ tiêu cực, dùng tone trung tính + có call-to-action thay thế
5. **Disclaimer**: cần đủ rõ nhưng không lấn át số tiền hoàn
6. **Accessibility**: contrast ratio ≥ 4.5:1, support dark mode

---

## 9. Lịch sử thay đổi

| Version | Ngày | Người thay đổi | Nội dung |
|---|---|---|---|
| v1.0 | 2026-06-01 | PM | Khởi tạo wireframe v1 |

---

**End of Document**
