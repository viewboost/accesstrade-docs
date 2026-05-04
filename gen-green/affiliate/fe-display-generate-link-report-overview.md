# Affiliate — FE Creator (Display + Generate Link + Report) — Overview

> **Ngày:** 2026-05-04
> **Trạng thái:** Đang thiết kế
> **PRD chi tiết:** chưa có (sẽ tạo sau khi spec stable)
> **Reference triển khai:** [`accesstrade-projects/ambassabor/frontend/src/pages/affiliate-*`](../../../ambassabor/frontend/src/pages/) — clone use case + UI từ Ambassador
> **Đối tượng:** Product, Operations, Stakeholders (non-tech)

---

## Đây là gì?

**FE Creator** là phần creator Gen-Green nhìn thấy: **browse chiến dịch affiliate, tham gia, tạo link để gắn vào nội dung, theo dõi hoa hồng**.

Hiểu đơn giản: nếu Admin Setup là "xếp hàng lên kệ", thì FE Creator là **cửa hàng đã mở cửa** — creator vào lấy sản phẩm (link affiliate) đem đi bán, cuối tháng đếm tiền.

---

## Tại sao cần?

Sau khi:
- ✅ Admin đã chuẩn bị catalog affiliate ([Admin Setup](admin-setup-overview.md))
- ✅ Creator đã liên kết tài khoản Scalef ([Account Linking](account-linking-overview.md))

→ Cần UI cho creator **dùng affiliate** để kiếm hoa hồng. Không có FE = data đã setup không ai dùng = không tạo doanh thu.

**Mục tiêu:** 40% creator active tạo affiliate link trong 3 tháng đầu (theo target Ambassador).

---

## Clone use case từ Ambassador

Toàn bộ chức năng + UI/UX **clone từ Ambassador frontend** (đã production, đã verified với 150K creators tương tự). Source: [`ambassabor/frontend/src/pages/`](../../../ambassabor/frontend/src/pages/).

| Chức năng | File reference Ambassador |
|-----------|---------------------------|
| Section affiliate trong Event detail | `affiliate-campaigns/index.tsx` |
| Trang chi tiết chiến dịch affiliate | `affiliate-campaign-detail/index.tsx` |
| Trang "Link affiliate của tôi" | `affiliate-links/index.tsx` |
| Trang "Hoa hồng của tôi" + báo cáo | `affiliate-commission/index.tsx` |
| Service layer (gọi BE proxy) | `services/affiliate.ts` |

→ Dev tham khảo trực tiếp source code, **không build từ đầu**. Tiết kiệm ~50% effort, giảm risk UX edge case.

---

## Creator làm gì?

### 1. Browse chiến dịch affiliate trong Event

Khi creator vào chi tiết Event (page hiện có) → thấy thêm **section "Chiến dịch Affiliate liên kết"**:

- Hiển thị card chiến dịch: banner, tên, hoa hồng, thưởng thêm, thời gian
- Grid 1 cột mobile, 2 cột desktop
- Click card → vào trang chi tiết affiliate
- Nếu Event không có affiliate liên kết → ẩn section luôn

### 2. Trang chi tiết chiến dịch affiliate

Layout 2 cột (desktop), stack dọc (mobile):

- **Cột trái:** Banner lớn + 3 badge (Hoa hồng / Thưởng thêm / Thời gian)
- **Cột phải:** Tên, mô tả ngắn, nút action chính, accordion sections (Thể lệ / Hướng dẫn — parse từ markdown)
- **Touchpoint AT linking:** Banner "Liên kết tài khoản Scalef" hiện trên đầu nếu chưa link

### 3. Tham gia chiến dịch

Trước khi tạo link, creator phải **tham gia** chiến dịch (BE gọi Scalef tạo contract):

- Nút "Tham gia chiến dịch" → BE proxy Scalef API
- Trạng thái contract:
  - **APPROVED** — duyệt ngay → hiện nút "Tạo link"
  - **PENDING** — banner vàng "Đang xử lý, thử lại sau X giờ" + countdown 24h
  - **REJECTED** — banner đỏ "Chưa đủ điều kiện, thử lại sau X ngày" + countdown 14 ngày

### 4. Tạo link affiliate

Sau khi APPROVED:

- Bấm "Tạo link" → modal nhập (optional) URL sản phẩm cụ thể
- BE gọi Scalef → trả `affiliate_link` (full) + `short_affiliate_link` (rút gọn)
- Hiển thị link với nút **Copy** + **Tạo link mới**
- Lưu vào danh sách "Link của tôi"

### 5. Xem danh sách link đã tạo

Trang riêng `/affiliate-links`:

- Group theo chiến dịch
- Tìm kiếm + filter
- Mỗi row: link rút gọn + link đầy đủ + nút Copy + ngày tạo
- (V2) Hiển thị số click + đơn hàng cho mỗi link

### 6. Xem báo cáo hoa hồng

Trang `/affiliate-commission`:

- **3 card tổng quan** ở đầu trang:
  - Hoa hồng **chờ duyệt** (pending)
  - Hoa hồng **tạm duyệt** (pre-approved)
  - Hoa hồng **đã xác nhận** (approved)
- **Filter thời gian** preset: 7 ngày / 1 tháng / 3 tháng / custom (max 3 tháng — limit Scalef)
- **Filter theo chiến dịch:** sidebar list các campaign đã tham gia
- **Danh sách đơn hàng:** table chi tiết đơn (order ID, sản phẩm, sale amount, commission, status, ngày)
- (V2) Chart chuyển đổi theo ngày, breakdown theo trạng thái

---

## Touchpoint liên kết Scalef trên Gen-Green

Khi creator **chưa liên kết** Scalef nhưng cố dùng affiliate, hệ thống chặn lại bằng touchpoint:

| Vị trí | Loại | Hành vi |
|--------|------|---------|
| Section affiliate trong Event | Banner | "Liên kết Scalef để kiếm hoa hồng" + CTA |
| Trang chi tiết affiliate | Banner | Hiển thị trên cùng cột phải |
| Bấm "Tham gia chiến dịch" | Popup chặn | "Cần liên kết Scalef trước" |
| Bấm "Tạo link affiliate" | Popup chặn | Tương tự |

CTA → redirect sang flow [account linking](account-linking-overview.md). Sau khi link xong → quay lại đúng trang trước đó.

---

## Trạng thái creator trên FE

| Trạng thái | UI hiển thị |
|------------|-------------|
| Chưa liên kết Scalef | Banner + popup chặn ở mọi action affiliate |
| Đã liên kết, chưa tham gia chiến dịch | Nút "Tham gia chiến dịch" |
| Đang chờ duyệt (PENDING) | Banner vàng + countdown 24h, disable "Tạo link" |
| Bị từ chối (REJECTED) | Banner đỏ + countdown 14 ngày |
| Đã duyệt, chưa tạo link | Nút "Tạo link" hoạt động |
| Đã có link | Hiển thị link + nút Copy + nút "Tạo link mới" |

---

## Vai trò trong hệ thống tổng

| Phase | Track | Trạng thái |
|-------|-------|-----------|
| Track độc lập | **[Admin Setup](admin-setup-overview.md)** — chuẩn bị catalog | Có thể start sớm nhất |
| 1 | **[Account Linking](account-linking-overview.md)** — liên kết Scalef | Cần spec SSO Scalef |
| 2 | **FE Creator** (track này) — Display + Generate + Report | Cần Phase 1 + Admin Setup xong |
| 3 | Hợp nhất tài khoản (Vin Creator Portal) | Future |

→ Track này **launch sau cùng**, vì cần data từ Admin Setup + identity từ Account Linking.

---

## Phân chia V1 / V2

### V1 (Must Have — launch initial)

- Section affiliate trong Event detail
- Trang chi tiết chiến dịch affiliate
- Tham gia + retry logic (PENDING/REJECTED)
- Tạo link + copy
- Trang "Link của tôi" (chưa có click/order count)
- Touchpoint liên kết Scalef (banner + popup)

### V2 (Should Have — launch sau)

- Trang "Hoa hồng của tôi" với 3 card + filter thời gian
- Danh sách đơn hàng chi tiết
- Click count + order count cho mỗi link
- Chart chuyển đổi theo ngày (nếu Scalef cung cấp data)
- Export CSV báo cáo

### Out of Scope

| Feature | Lý do |
|---------|-------|
| Withdraw hoa hồng affiliate | Phase 3 — gộp với cashflow Gen-Green |
| Affiliate dashboard real-time | Future — Scalef report API delay vài giờ |
| Recommend campaign theo content creator | Future — cần ML |
| Affiliate cho story / live | Future |

---

## Thời gian & nguồn lực

### V1
- **Effort:** ~7.5 ngày (~1.5 tuần) cho 1 BE + 1 FE
- **Output:**
  - 4 components mới: Section, Card, Banner Scalef, Popup chặn
  - 2 page mới: campaign detail, my-links
  - Service layer + interfaces

### V2 (Report)
- **Effort:** ~5 ngày (~1 tuần)
- **Output:**
  - Trang commission dashboard
  - Filter thời gian + campaign
  - Table đơn hàng

→ Tổng V1+V2 ~12.5 ngày (~2.5 tuần).

Effort thực tế thấp hơn estimate Ambassador build từ đầu (~24 ngày) vì **clone trực tiếp source code** — chỉ cần thay API endpoints + adapt cho Gen-Green design system.

---

## Phụ thuộc

### Cần data sẵn sàng (đã có khi Admin Setup + Account Linking xong)
- Affiliate campaigns active + mapping với Event ([Admin Setup](admin-setup-overview.md))
- `scalef_user_id` trên user Gen-Green ([Account Linking](account-linking-overview.md))

### Cần BE proxy
- BE Gen-Green proxy gọi Scalef APIs theo spec [`scalef-api.md`](scalef-api.md)
- Endpoints chính: `POST /campaigns/join`, `POST /campaigns/generate-link`, `POST /report/click`, `POST /report/overview`, `GET /publisher/conversion`

### Cần từ design
- Adapt UI Ambassador → Gen-Green design system (màu, typography, spacing)
- Logo + branding Gen-Green

---

## Liên quan

- [Admin Setup Overview](admin-setup-overview.md) — chuẩn bị data nguồn
- [Account Linking Overview](account-linking-overview.md) — Phase 1, cần xong trước
- [Scalef API Reference](scalef-api.md) — BE integration spec
- [Ambassador frontend source](../../../ambassabor/frontend/src/pages/) — clone reference
- [PRD admin setup](prd-admin-setup-2026-05-04.md) — track admin (nếu PRD FE viết sau, sẽ ở cùng folder)
