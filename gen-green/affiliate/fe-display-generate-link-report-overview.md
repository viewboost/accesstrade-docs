# Affiliate — FE Display + Generate Link + Report — Overview

> **Project:** Gen-Green × Affiliate Integration — Phase 2 (Affiliate trong Gen-Green)
> **Ngày:** 2026-05-04
> **Trạng thái:** Đang thiết kế
> **Phụ thuộc:** [Admin Setup](admin-setup-overview.md) + [API Integration](api-integration-overview.md) + [Scalef Linking Phase 1](../scalef-integration/overview.md)
> **Tham chiếu Ambassador V1:** [`prd-affiliate-v1-2026-03-31.md`](../../pub2-affiliate-integration/prd-affiliate-v1-2026-03-31.md) — FR-004, FR-005, FR-013, FR-017, FR-018

---

## 1. Bối cảnh

Đây là **lớp tiếp xúc với creator** — nơi affiliate biến từ concept thành thu nhập thật:

1. **Display:** Creator browse campaign affiliate ngay trong Event hiện có
2. **Join:** Tham gia chiến dịch (tạo contract với Pub2 qua sso_id Scalef)
3. **Generate Link:** Tạo affiliate link cá nhân để gắn vào nội dung
4. **Report (V2):** Theo dõi click, đơn hàng, hoa hồng, thu nhập

**Nguyên tắc UX:**
- Affiliate là **giá trị cộng thêm**, không thay đổi flow chính của creator
- Touchpoint liên kết Scalef đặt sát nơi creator có động lực (banner trong event detail)
- 1 click để copy link, không bắt creator hiểu thuật ngữ kỹ thuật
- Trạng thái phải minh bạch (PENDING/APPROVED/REJECTED + countdown retry)

---

## 2. Scope

### Phase 2a — Display + Join + Generate Link (V1)

- Hiển thị affiliate campaign trong Event Detail
- Trang chi tiết Affiliate Campaign
- Touchpoint liên kết Scalef (banner + popup)
- Join campaign + retry logic PENDING/REJECTED
- Generate affiliate link + copy
- Trang "Link affiliate của tôi"

### Phase 2b — Report (V2)

- Dashboard cá nhân (clicks / orders / commission / total income)
- Filter theo thời gian (3 tháng max — limit Pub2)
- Breakdown theo campaign / theo trạng thái đơn
- Export CSV
- Notification khi có đơn mới / hoa hồng được duyệt

### Out of Scope

| Feature | Phase |
|---------|-------|
| Withdraw hoa hồng affiliate | Phase 3 (gộp với cashflow) |
| Affiliate dashboard real-time | Future |
| Recommend campaign cho creator dựa trên content | Future |
| Affiliate cho story / live | Future |

---

## 3. User Flows

### 3.1 Happy path — đã link Scalef

```
Creator vào Event Detail
  → Thấy section "Chiến dịch Affiliate liên kết" (1-2 cột)
  → Click vào Affiliate Card
  → Trang chi tiết Affiliate Campaign (2-col desktop, stack mobile)
  → Bấm "Tham gia chiến dịch"
  → BE gọi Pub2 API 1.2 → contract APPROVED ngay
  → Hiện nút "Tạo link affiliate"
  → Bấm → BE gọi Pub2 API 2 → trả về affiliate_link + short_link
  → Creator copy link → paste vào video/bio
```

### 3.2 Chưa link Scalef

```
Creator vào Event Detail
  → Thấy banner "Liên kết tài khoản Scalef để kiếm hoa hồng"
  → Bấm CTA → redirect sang trang link Scalef (Phase 1 flow)
  → Hoàn tất linking → quay lại Event Detail
  → Banner ẩn, affiliate section hiển thị bình thường
```

Nếu creator click "Tham gia" / "Tạo link" mà chưa link → popup chặn:

```
"Bạn cần liên kết tài khoản Scalef trước khi tham gia chiến dịch affiliate"
[Liên kết ngay] [Để sau]
```

### 3.3 Contract PENDING

```
Creator bấm "Tham gia"
  → Pub2 trả PENDING
  → UI: banner vàng "Yêu cầu đang được xử lý. Thử lại sau X giờ"
  → Sau 24h: nút "Thử lại" enable
  → Bấm → BE gọi lại Pub2 → có thể APPROVED hoặc tiếp tục PENDING
```

### 3.4 Contract REJECTED

```
Creator bấm "Tham gia"
  → Pub2 trả REJECTED
  → UI: banner đỏ "Bạn chưa đủ điều kiện. Thử lại sau X ngày"
  → Sau 14 ngày: nút "Thử lại" enable
```

### 3.5 Generate link

```
Creator (đã APPROVED) bấm "Tạo link affiliate"
  → Modal nhập (optional) URL gốc cụ thể (deep-link sản phẩm)
  → Nếu để trống → dùng pub2_campaign_url default
  → BE gọi Pub2 API 2 với sub2='GENGREEN', sub3=campaign_id, sub4=event_id
  → Trả affiliate_link + short_affiliate_link
  → Lưu MongoDB local
  → Hiển thị link với nút Copy
  → Toast "Đã copy link"
```

### 3.6 Xem report (V2)

```
Creator vào "Thu nhập của tôi" → tab "Hoa hồng affiliate"
  → Default: 30 ngày gần nhất
  → Card: Tổng hoa hồng / Số đơn / Số click / Tỉ lệ chuyển đổi
  → Chart: theo ngày
  → Table breakdown: theo campaign
  → Filter: thời gian (max 3 tháng), campaign, trạng thái đơn
```

---

## 4. Pages & Components

### 4.1 `AffiliateCampaignsSection` (component nhúng vào Event Detail)

**Vị trí:** Trong page Event Detail của creator (Gen-Green frontend).

**Hiển thị:**
- Section title "Chiến dịch Affiliate liên kết"
- Banner liên kết Scalef (nếu chưa link) — **BẮT ĐẦU SECTION**
- Grid 1 cột mobile / 2 cột desktop
- Mỗi item = `AffiliateItemCard`
- Empty state: nếu không có affiliate link với event → ẩn cả section

**Logic:**
- Fetch `GET /events/:id/affiliate-campaigns` (Phase 2a API)
- Cache response với TanStack Query / DVA
- Auto-refresh khi user thay đổi link Scalef status

### 4.2 `AffiliateItemCard`

**Layout:**
```
┌─────────────────────────────────┐
│ [Banner image]                   │
├─────────────────────────────────┤
│ Title campaign                   │
│ Short description                │
│ [💰 Hoa hồng tới 8%]             │
│ [🎁 Thưởng +50K]                 │
│ [⏰ Đến 31/12/2026]               │
│                                  │
│ [Khám phá ngay →]                │
└─────────────────────────────────┘
```

**Click → navigate sang trang chi tiết.**

### 4.3 Page `affiliate-campaign-detail/:id`

**Layout desktop (2 cột):**
```
┌─────────────────────┬──────────────────────────┐
│ [Banner image]      │ Title                    │
│                     │ Description short        │
│ 💰 Hoa hồng         │                          │
│ 🎁 Thưởng           │ [Tham gia chiến dịch]    │
│ ⏰ Thời gian         │ (hoặc state khác)        │
│                     │                          │
│                     │ [AT Linking Banner]      │
│                     │ (nếu chưa link)          │
│                     │                          │
│                     │ Tabs:                    │
│                     │  [Thể lệ] [Hướng dẫn]    │
│                     │                          │
│                     │ Accordion sections từ    │
│                     │ markdown (## headings)   │
│                     │ — section đầu mặc định mở │
└─────────────────────┴──────────────────────────┘
```

**Mobile:** stack dọc, banner ở trên cùng.

**States chính:**

| State | UI |
|-------|-----|
| Chưa link Scalef | Nút "Tham gia" disable + AT Linking Banner |
| Chưa join | Nút "Tham gia chiến dịch" |
| Joining | Spinner, disable click |
| PENDING | Banner vàng + countdown + nút "Thử lại" (sau 24h) |
| REJECTED | Banner đỏ + countdown + nút "Thử lại" (sau 14 ngày) |
| APPROVED | Nút "Tạo link affiliate" |
| Đã có link | Hiển thị link đã tạo + Copy + nút "Tạo link mới" |

### 4.4 Modal `GenerateLinkModal`

**Input:**
- (Optional) URL cụ thể trong campaign (VD: link sản phẩm cụ thể trên Shopee)
- Nếu để trống → dùng `pub2_campaign_url`

**Output:**
- `affiliate_link` (full)
- `short_affiliate_link` (rút gọn — ưu tiên hiển thị)
- Nút Copy + nút "Tạo thêm"

### 4.5 Page `account/my-affiliate-links`

Danh sách link đã tạo của creator:

```
┌────────────────────────────────────────────────┐
│ Filter: [campaign] [date range] [search]        │
├────────────────────────────────────────────────┤
│ Campaign │ Link │ Tạo lúc │ Click │ Đơn │ Action │
├────────────────────────────────────────────────┤
│ Shopee   │ s.io/abc │ 1/5  │ 12 │ 2 │ Copy/Del │
│ Lazada   │ s.io/xyz │ 2/5  │ 5  │ 0 │ Copy/Del │
└────────────────────────────────────────────────┘
```

Click count + đơn hàng = Phase Report (V2). V1 hiển thị `—`.

### 4.6 Page `account/affiliate-income` (V2)

Dashboard hoa hồng — thiết kế chi tiết ở doc Report riêng (sẽ tạo sau khi V1 launch).

### 4.7 `ScalefLinkingBanner` (touchpoint)

**Vị trí:** Trong AffiliateCampaignsSection + đầu trang affiliate-campaign-detail.

**Visibility:** chỉ khi `user.scalef_user_id == null`.

**Layout:**
```
┌──────────────────────────────────────────────┐
│ 🔗 Liên kết tài khoản Scalef để kiếm hoa hồng │
│    affiliate trên các đơn hàng                 │
│                                                │
│ [Liên kết ngay →]              [Tìm hiểu thêm] │
└──────────────────────────────────────────────┘
```

### 4.8 `ScalefLinkingPopup` (chặn action)

Trigger khi user chưa link mà bấm "Tham gia" / "Tạo link":

```
┌──────────────────────────────────┐
│ Liên kết Scalef trước khi tham gia│
│                                   │
│ Để tham gia chiến dịch affiliate  │
│ và kiếm hoa hồng, bạn cần liên    │
│ kết tài khoản Scalef.             │
│                                   │
│ [Liên kết ngay] [Để sau]          │
└──────────────────────────────────┘
```

---

## 5. State Management

### Local state (UI)
- Modal open/close
- Form inputs

### Server state (cache via TanStack Query / DVA)
- `affiliate-campaigns-by-event/:eventId` — TTL 5'
- `affiliate-campaign-detail/:id` — TTL 10'
- `my-contract/:campaignId` — TTL 1' (vì có retry timer)
- `my-affiliate-links` — TTL 1'
- `me` (user info, để check `scalef_user_id`) — invalidate sau linking

### Persistent (LocalStorage)
- Không lưu nhạy cảm. Chỉ lưu UI preferences (đã đóng banner X).

---

## 6. Responsive

| Breakpoint | Layout |
|-----------|--------|
| ≥ 1024px | 2-col grid + 2-col detail page |
| 768-1024px | 2-col grid + stack detail |
| < 768px | 1-col grid + stack detail, banner full-width |
| ≥ 320px | Đảm bảo mọi action (copy, join, retry) hoạt động |

---

## 7. Accessibility

- All buttons có `aria-label`
- Modal có focus trap + ESC to close
- Color contrast ≥ 4.5:1 (banner vàng/đỏ vẫn đọc được)
- Keyboard navigation cho list + tabs
- Screen reader announce trạng thái contract change

---

## 8. Tracking events (Analytics)

| Event | Khi nào |
|-------|---------|
| `affiliate_section_viewed` | Section hiển thị trong event detail |
| `affiliate_campaign_clicked` | Click vào card |
| `at_linking_banner_clicked` | Click banner Scalef |
| `at_linking_popup_shown` | Popup chặn hiển thị |
| `affiliate_join_clicked` | Bấm "Tham gia" |
| `affiliate_join_result` | Kèm status APPROVED/PENDING/REJECTED |
| `affiliate_link_generated` | Tạo link thành công |
| `affiliate_link_copied` | Bấm copy |
| `affiliate_retry_clicked` | Bấm "Thử lại" |

Mục đích: đo conversion funnel `view → click → join → generate → copy`.

---

## 9. Error Handling

| Lỗi | UI |
|-----|-----|
| BE timeout | Toast "Có lỗi, vui lòng thử lại" + retry button |
| Pub2 timeout | Như trên (BE đã handle) |
| Pub2 reject với code lạ | Hiển thị message từ BE + ticket support |
| Network offline | Banner "Mất kết nối" |
| User chưa login | Redirect login |
| User chưa link Scalef | Popup linking |

Không bao giờ hiển thị raw error message từ Pub2.

---

## 10. Performance

| Yêu cầu | Target |
|---------|--------|
| Affiliate section render | < 500ms (cache hit) / < 2s (cache miss) |
| Detail page first paint | < 1.5s |
| Generate link API | < 3s (BE proxy Pub2) |
| Copy link | Instant |
| Mobile bundle size | < 50KB gzipped tăng thêm |

Lazy-load detail page + `my-affiliate-links` page (route-level code split).

---

## 11. Phụ thuộc

### Có sẵn
- Gen-Green frontend (creator-facing)
- User session + me API trả về `scalef_user_id`
- Event Detail page

### Cần build
- 4 components mới (Section, Card, Banner, Popup)
- 2 pages mới (campaign-detail, my-affiliate-links)
- Service layer (`services/affiliate.ts`) + interfaces
- Markdown parser cho description (reuse từ news/article nếu có)
- Toast / Modal (reuse component lib)

### Cần từ BE (xem [API Integration](api-integration-overview.md))
- Public APIs join/contract/generate-link/list-links/list-by-event
- `me` endpoint trả `scalef_user_id`

---

## 12. Estimate

### Phase 2a — V1

| Module | Effort |
|--------|--------|
| Service layer + interfaces | 0.5d |
| AffiliateCampaignsSection + Card | 1.5d |
| Affiliate campaign detail page | 1.5d |
| Join + retry logic + states | 1d |
| Generate link modal + copy | 0.5d |
| `my-affiliate-links` page | 0.5d |
| ScalefLinkingBanner + Popup | 0.5d |
| Responsive + accessibility | 0.5d |
| QA + bug fix | 1d |
| **Tổng V1** | **~7.5d (~1.5 tuần)** |

### Phase 2b — V2 Report

| Module | Effort |
|--------|--------|
| Service + interfaces | 0.5d |
| Income dashboard (cards + chart + filter) | 2d |
| Breakdown table | 1d |
| Export CSV | 0.5d |
| QA | 1d |
| **Tổng V2** | **~5d (~1 tuần)** |

---

## 13. Edge Cases

| Case | Xử lý |
|------|-------|
| User link Scalef giữa flow | Re-fetch user + ẩn banner ngay |
| Campaign deactivate khi user đang xem | Banner "Campaign đã ngừng" + disable action |
| Creator đã có link, sau đó admin xóa campaign | Link cũ vẫn hoạt động (Pub2 side), nhưng FE ẩn campaign |
| Generate link nhiều lần với cùng URL | Cho phép, mỗi lần tạo bản ghi mới |
| Mobile copy fail (browser old) | Fallback: hiển thị input + select all + manual copy |
| User dùng 2 device | State PENDING/APPROVED sync qua server, mỗi device fetch lại |

---

## 14. Liên quan

- [Admin Setup Overview](admin-setup-overview.md)
- [API Integration Overview](api-integration-overview.md)
- [Scalef Linking Phase 1](../scalef-integration/overview.md)
- Ambassador reference UI: `frontend/src/pages/affiliate-campaign-detail/`, `frontend/src/pages/home/components/affiliate-campaigns-section/`, `frontend/src/pages/home/components/affiliate-item-card/`
