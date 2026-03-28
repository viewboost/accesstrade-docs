# Product Requirements Document: Pub2 Affiliate Integration — Ambassador

**Date:** 2026-03-25
**Author:** vinhnguyen
**Version:** 1.2
**Project Type:** Feature Integration
**Project Level:** Level 3
**Status:** Draft
**Platform:** Ambassador (`accesstrade-projects/ambassabor/`)

---

## Document Overview

PRD này định nghĩa requirements cho việc tích hợp hệ thống affiliate marketing của Pub2 (AccessTrade) vào platform Ambassador. Cho phép influencer tạo affiliate link, theo dõi hiệu suất, và kiếm commission từ các chiến dịch affiliate.

**Related Documents:**
- [Executive Summary](./00-executive-summary.md)
- [Architecture Decisions](./02-architecture-decisions.md)
- [API Reference](./api-reference.md)
- [Minimize API Spec](./minimize-api.md)

---

## Executive Summary

Ambassador hiện có hệ thống campaign nội bộ (event-based). Chức năng mới này bổ sung **affiliate campaigns** — một đối tượng mới được **liên kết (mapping) với campaign/event hiện tại**, không phải đứng riêng lẻ.

**Concept chính:** Affiliate campaign được gắn vào campaign hiện tại. Influencer vào chi tiết campaign → thấy phần affiliate campaign bên trong → tạo link, xem báo cáo.

Influencer sẽ:
1. Vào chi tiết campaign hiện tại → thấy affiliate campaign được liên kết
2. **Tham gia chiến dịch** (join campaign) → hệ thống tạo contract với Pub2
3. Tạo affiliate link cho campaign
4. Chia sẻ link → thu commission khi có conversion
5. Xem báo cáo hiệu suất (click, conversion, sale amount, commission)
6. Xem chi tiết danh sách đơn hàng

**Điểm quan trọng:**
- **Affiliate campaign gắn vào campaign hiện tại** qua bảng quan hệ mapping (campaign ↔ affiliate campaign)
- Feature chính: influencer xem affiliate campaign **bên trong chi tiết campaign**, chưa phải standalone listing
- Chức năng **liên kết tài khoản AccessTrade** đã có sẵn trên Ambassador (SSO OAuth2)
- Cần thêm **điểm chạm** (touchpoint): banner trên đầu trang + popup khi thực hiện action
- Backend Ambassador (Go) sẽ proxy gọi Pub2 APIs với HMAC authentication
- Admin tự tạo affiliate campaigns và **liên kết** chúng với campaign/event hiện tại

---

## Product Goals

### Business Objectives

1. **Tăng thu nhập influencer**: Dual revenue stream (views + affiliate commissions)
2. **Tăng engagement**: Incentive mạnh hơn để tạo nội dung chất lượng
3. **Tăng retention**: Influencer gắn bó lâu hơn nhờ thu nhập cao hơn
4. **Mở rộng giá trị platform**: Kết nối influencer với merchants qua affiliate

### Success Metrics

| Metric | Target | Timeframe |
|--------|--------|-----------|
| Tỷ lệ influencer tạo affiliate link | 40% active users | 3 tháng sau launch |
| Activation rate (linked → generated link) | 60% | 3 tháng |
| Avg. influencer income tăng | +40% | 6 tháng |
| Influencer retention | +15% | 6 tháng |

---

## Functional Requirements

Functional Requirements (FRs) define **what** the system does - specific features and behaviors.

---

### FR-001: Admin tạo Affiliate Campaign

**Priority:** Must Have

**Description:**
Admin tạo affiliate campaign mới trên Ambassador Admin panel. Campaign bao gồm thông tin nội bộ (title, description, banner, category, commission info) và liên kết với Pub2 qua `pub2_campaign_id`.

**Acceptance Criteria:**
- [ ] Admin có thể tạo affiliate campaign với các trường: partner (required), title, description, short_desc (mô tả ngắn, hiển thị trên card listing và trang chi tiết thay cho desc), banner image (required), category, commission info (required), bonus_info, pub2_campaign_id, pub2_campaign_url (required), start_date, end_date
- [ ] **Partner là required khi tạo và immutable sau khi tạo** (giống event). Root staff chọn partner, non-root staff tự động gán partner của mình
- [ ] **Status mặc định là `draft` khi tạo** — admin không chọn status lúc tạo, chỉ thay đổi sau khi tạo
- [ ] Admin có thể chỉnh sửa và cập nhật campaign (trừ partner)
- [ ] Admin có thể thay đổi status: draft / active / inactive
- [ ] Validate `pub2_campaign_id` là required và không trùng lặp
- [ ] Campaign chỉ hiển thị cho influencer khi status = active

**Dependencies:** None

---

### FR-002: Admin quản lý danh sách Affiliate Campaigns

**Priority:** Must Have

**Description:**
Admin xem, tìm kiếm, lọc và quản lý danh sách affiliate campaigns đã tạo.

**Acceptance Criteria:**
- [ ] Hiển thị danh sách campaigns với: title, status, category, commission, ngày tạo
- [ ] Lọc theo status (draft/active/inactive), category
- [ ] Tìm kiếm theo title
- [ ] Sắp xếp theo ngày tạo, title
- [ ] Bulk actions: activate / deactivate nhiều campaigns

**Dependencies:** FR-001

---

### FR-003: Admin liên kết Affiliate Campaign với Campaign/Event

**Priority:** Must Have

**Description:**
Admin liên kết (mapping) một affiliate campaign với một hoặc nhiều campaign/event hiện tại của Ambassador. Đây là bảng quan hệ giữa 2 đối tượng: campaign (event) ↔ affiliate campaign.

**Acceptance Criteria:**
- [ ] Admin có thể liên kết 1 affiliate campaign với 1 hoặc nhiều campaigns/events
- [ ] Admin có thể liên kết 1 campaign/event với 1 hoặc nhiều affiliate campaigns
- [ ] **Chỉ hiển thị events cùng partner** khi liên kết — event search được filter theo partner của affiliate campaign
- [ ] Quan hệ many-to-many: bảng mapping `campaign_affiliate_mappings` với `event_id` + `affiliate_campaign_id`
- [ ] Admin có thể gỡ liên kết (unlink)
- [ ] Hiển thị danh sách events đã liên kết trong trang chi tiết affiliate campaign (admin) — bao gồm tên event, trạng thái, ngày liên kết
- [ ] Hiển thị danh sách affiliate campaigns đã liên kết trong trang chi tiết campaign (admin)
- [ ] Event search autocomplete với debounce khi liên kết

**Dependencies:** FR-001

---

### FR-004: Influencer xem Affiliate Campaign trong chi tiết Campaign

**Priority:** Must Have

**Description:**
Influencer vào chi tiết campaign/event hiện tại → thấy section affiliate campaign(s) được liên kết bên trong. Đây là **feature chính** — affiliate campaign hiển thị trong context của campaign, không phải standalone listing.

**Acceptance Criteria:**
- [ ] Trong trang chi tiết campaign hiện tại, hiển thị section "Chiến Dịch Affiliate Liên Kết" nếu campaign có liên kết affiliate
- [ ] Nếu campaign không có affiliate campaign liên kết → không hiển thị section
- [ ] Nếu có nhiều affiliate campaigns liên kết → hiển thị danh sách dạng grid (1 cột mobile, 2 cột desktop)
- [ ] Hiển thị banner trên đầu section nếu chưa liên kết AccessTrade, kèm CTA "Liên kết tài khoản"

**UI Design — Affiliate Item Card:**

Mỗi affiliate campaign hiển thị dưới dạng card theo thiết kế Figma:

| Thành phần | Mô tả | Required fields |
|------------|--------|-----------------|
| **Banner image** | Ảnh banner campaign, aspect ratio ~5:2, rounded top corners, object-fit cover | `banner.url` (required) |
| **Title** | Tên campaign, font 18px/semibold, color #101828, 1 line ellipsis | `title` (required) |
| **URL link** | Link URL xanh (#1570EF), clickable mở tab mới, fallback hiển thị category | `pub2_campaign_url` (required) |
| **CTA button** | "Khám phá ngay", gradient purple-pink (radial-gradient #7A5AF8 → #FF5FAC), pill shape, nằm bên phải header | Luôn hiển thị |
| **Divider** | Đường kẻ ngang 1px #EAECF0 | — |
| **Description** | Mô tả campaign, font 14px/regular, color #475467, max 3 dòng ellipsis | `desc` |
| **Info badges** | 3 badges nằm ngang (stack dọc trên mobile <576px) | — |

**Info Badges chi tiết:**

| Badge | Icon | Label | Value field | Ví dụ |
|-------|------|-------|-------------|-------|
| Hoa hồng | Dollar/coin icon (#475467) | "Hoa hồng" | `commission_info` (required) | "100.000/đơn" |
| Thưởng thêm | Gift icon (#7A5AF8) | "Thưởng thêm" | `bonus_info` | "+1.000.000 đ", "+10%" |
| Thời gian | Calendar icon (#475467) | "Thời gian" | `start_date` + `end_date` | "15 - 20/02/2026", "Đến 20/02/2026" |

- Badge container: border 1px solid #D5D7DA, border-radius 10px, padding 16px 12px
- Label: 14px/medium, color #475467
- Value: 14px/semibold, color #344054
- Nếu `bonus_info` không có → hiển thị "—"
- Thời gian format: "dd/mm/yyyy - dd/mm/yyyy" hoặc "Đến dd/mm/yyyy" nếu chỉ có end date

**Card container:**
- Background: #FFFFFF, border-radius: 16px
- Box shadow: 0 1px 3px rgba(16,24,40,0.1)
- Max-width: 592px
- Hover: shadow tăng nhẹ

**CTA behavior:**
- Click "Khám phá ngay" → navigate đến trang chi tiết affiliate campaign
- Nếu chưa link AccessTrade → show popup yêu cầu liên kết trước
- Nếu đã link → navigate bình thường

**Dependencies:** FR-001, FR-003

---

### FR-017: Influencer tham gia chiến dịch (Join Campaign)

**Priority:** Must Have

**Description:**
Influencer phải tham gia (join) chiến dịch affiliate trước khi có thể tạo link. Backend gọi Pub2 API 1.2 (POST `/campaign-service/api/v1/contracts`) để tạo contract giữa publisher và campaign.

**Acceptance Criteria:**
- [ ] Chỉ cho phép tham gia khi đã liên kết tài khoản AccessTrade
- [ ] Backend gọi Pub2 API 1.2 với: `partner_code`, `sso_id` (từ user AccessTrade data), `partner_ref_campaign_id` (pub2_campaign_id)
- [ ] Xử lý response: lưu `contract_no` và `contract_status` vào database Ambassador
- [ ] Hiển thị trạng thái tham gia cho influencer:
  - `PENDING`: "Đang chờ duyệt" — disable nút tạo link
  - `APPROVED`: "Đã được duyệt" — enable nút tạo link
  - `REJECTED`: "Bị từ chối" — hiển thị thông báo, disable nút tạo link
- [ ] Nếu đã tham gia (affiliation already exist, error_code=0) → cập nhật trạng thái từ response
- [ ] Xử lý error codes từ Pub2 API 1.2:
  - `1`: Publisher không tồn tại → thông báo lỗi
  - `2`: Campaign không tồn tại → thông báo lỗi
  - `5`: Ekyc thất bại → hướng dẫn user
  - `7`: Chưa đăng ký campaign cha → thông báo lỗi
  - `10`: Không đủ điều kiện tham gia → thông báo lỗi
  - Khác: Lỗi hệ thống → thông báo chung
- [ ] Nút "Tham gia chiến dịch" hiển thị trong affiliate campaign card khi chưa join
- [ ] Sau khi join thành công (APPROVED) → tự động hiện nút "Tạo link affiliate"

**Dependencies:** FR-004, FR-013, FR-014

---

### FR-018: Trang chi tiết Affiliate Campaign (Campaign Detail Page)

**Priority:** Must Have

**Description:**
Trang chi tiết affiliate campaign hiển thị đầy đủ thông tin campaign cho influencer. Layout 2 cột trên desktop, stack dọc trên mobile. Bao gồm thông tin campaign, tabs nội dung, và các accordion sections.

**Acceptance Criteria:**

**Layout tổng quan (Desktop):**
- [ ] 2 cột ngang, gap 20px, max-width 1280px, padding 0 112px
- [ ] Cột trái (598px): Banner image + 3 info badges
- [ ] Cột phải (flex-grow): Title, description, tabs, AT linking banner
- [ ] Background: #FAFAFA
- [ ] Border-radius: 20px cho mỗi cột (white background)
- [ ] Mobile: stack dọc, single column

**Cột trái — Banner + Info badges:**

| Thành phần | Mô tả |
|------------|--------|
| Banner image | Ảnh campaign, aspect ratio tự nhiên, rounded top (20px), width 100% |
| Info badges | 3 badges ngang dưới banner, padding 0 20px, gap 16px |

- Info badges giống FR-004 (Hoa hồng, Thưởng thêm, Thời gian)
- Border: 1px solid #E9EAEB (hơi khác card listing)
- Value font-weight: 700 (bold, thay vì 600 ở card listing)

**Cột phải — Nội dung campaign:**

| Thành phần | Mô tả | Specs |
|------------|--------|-------|
| Title | Tên campaign | 20px/semibold, color #101828 |
| Description | Mô tả chi tiết | 16px/regular, color #181D27, line-height 24px |
| Tabs | "Thể lệ" / "Hướng dẫn" | 2 tabs ngang, border 1px solid #E9EAEB, rounded 12px, 14px/semibold |
| AT Linking Banner | Banner liên kết AccessTrade (nếu chưa link) | Background #FEF6FB (Pink/25), rounded 12px, padding 20px |

**Tabs chi tiết:**
- Container: border 1px solid #E9EAEB, border-radius 12px
- 2 tabs: "Thể lệ" | "Hướng dẫn", phân cách bằng divider 1px #D9D9D9
- Tab text: 14px/semibold, color #181D27, text-align center
- Active tab có thể highlight (TBD)

**AT Linking Banner (chưa liên kết):**
- Background: #FEF6FB (Pink/25), border-radius 12px, padding 20px
- Icon: AT logo trong circle button (white bg, skeuomorphic shadow)
- Text: "Để tham gia chương trình bạn cần liên kết với **tài khoản ACCESSTRADE**", 14px/medium, color #181D27
- CTA: "Liên kết ngay" button, gradient purple-pink, rounded 8px, padding 10px 16px
- Icon link-05 trước text, color white

**Accordion Sections (phía dưới, full width):**

Nội dung accordion được parse từ field `desc` (markdown). Mỗi heading `##` trong markdown tạo thành 1 accordion section.

Ví dụ markdown `desc`:
```markdown
## Giới thiệu chung
Lorem ipsum dolor sit amet...

## Chính sách hoa hồng
Chi tiết commission...

## Điều kiện ghi nhận
...
```

- Container: white background, border-radius 12px
- Mỗi section: padding 20px 24px, divider 1px #F2F4F7 giữa các section
- Title: 16px/bold, color #101828
- Content: 14px/regular, color #475467
- Toggle icon: chevron-up (mở) / chevron-down (đóng), 24px, border 2px solid #000
- Section đầu tiên mặc định mở, các section còn lại mặc định đóng
- Không cần thêm fields riêng — tất cả nội dung nằm trong `desc`

**Dependencies:** FR-004, FR-017

---

### FR-005: Influencer tạo Affiliate Link

**Priority:** Must Have

**Description:**
Influencer tạo affiliate link cho một campaign. **Yêu cầu đã tham gia chiến dịch (contract_status = APPROVED) trước khi tạo link.** Backend gọi Pub2 API 2 (POST `/publisher/affiliate/link`) với HMAC authentication.

**Acceptance Criteria:**
- [ ] **Chỉ cho phép tạo link khi đã tham gia chiến dịch (contract_status = APPROVED)**
- [ ] Chỉ cho phép tạo link khi đã liên kết tài khoản AccessTrade
- [ ] Backend gọi Pub2 API với: `partner_code`, `original_url` (từ campaign), `partner_ref_campaign_id` (pub2_campaign_id), `sso_user_id` (từ user AccessTrade data)
- [ ] Sử dụng sub parameters cho tracking: `sub1` = sso_user_id, `sub2` = ambassador platform identifier
- [ ] Trả về `affiliate_link` (dài) và `short_affiliate_link` (ngắn)
- [ ] Influencer có thể copy link (cả dài và ngắn)
- [ ] Lưu lại link đã tạo trong database Ambassador để hiển thị lại
- [ ] Xử lý lỗi: Pub2 API fail → hiện thông báo lỗi rõ ràng

**Dependencies:** FR-003, FR-004, **FR-017**

---

### FR-006: Influencer xem danh sách Link đã tạo

**Priority:** Must Have

**Description:**
Influencer xem lại tất cả affiliate links đã tạo, grouped theo campaign.

**Acceptance Criteria:**
- [ ] Hiển thị danh sách links: campaign name, short link, ngày tạo
- [ ] Copy link nhanh
- [ ] Link đến campaign detail
- [ ] Phân trang

**Dependencies:** FR-005

---

### FR-007: Báo cáo Click

**Priority:** Must Have

**Description:**
Influencer xem báo cáo số lượt click affiliate links. Backend gọi Pub2 API 3.1.

**Acceptance Criteria:**
- [ ] Hiển thị tổng click trong khoảng thời gian chọn
- [ ] Biểu đồ click theo ngày (dữ liệu epoch time từ Pub2 → convert sang ngày)
- [ ] Lọc theo khoảng thời gian (max 3 tháng)
- [ ] Lọc theo campaign (optional)
- [ ] Gọi Pub2 API on-demand khi user request

**Dependencies:** FR-005

---

### FR-008: Báo cáo Conversion

**Priority:** Must Have

**Description:**
Influencer xem báo cáo số đơn hàng (conversions). Backend gọi Pub2 API 3.2.

**Acceptance Criteria:**
- [ ] Hiển thị tổng conversion trong khoảng thời gian
- [ ] Biểu đồ conversion theo ngày
- [ ] Lọc theo thời gian (max 3 tháng) và campaign
- [ ] Gọi Pub2 API on-demand

**Dependencies:** FR-005

---

### FR-009: Báo cáo Sale Amount

**Priority:** Should Have

**Description:**
Influencer xem báo cáo giá trị đơn hàng (sale amount), phân theo trạng thái. Backend gọi Pub2 API 3.3.

**Acceptance Criteria:**
- [ ] Hiển thị tổng sale amount
- [ ] Phân theo trạng thái: REJECTED, WAITING_FOR_APPROVED, APPROVED, TEMPORARY_APPROVED
- [ ] Biểu đồ theo ngày
- [ ] Lọc theo thời gian (max 3 tháng) và campaign

**Dependencies:** FR-005

---

### FR-010: Báo cáo Commission (Hoa hồng)

**Priority:** Must Have

**Description:**
Influencer xem báo cáo hoa hồng (commission), phân theo trạng thái. Backend gọi Pub2 API 3.4.

**Acceptance Criteria:**
- [ ] Hiển thị tổng commission
- [ ] Phân theo trạng thái: REJECTED, WAITING_FOR_APPROVED, APPROVED, TEMPORARY_APPROVED
- [ ] Biểu đồ theo ngày
- [ ] Lọc theo thời gian (max 3 tháng) và campaign

**Dependencies:** FR-005

---

### FR-011: Danh sách đơn hàng chi tiết

**Priority:** Must Have

**Description:**
Influencer xem danh sách đơn hàng chi tiết (conversions list) với đầy đủ thông tin. Backend gọi Pub2 API 8.

**Acceptance Criteria:**
- [ ] Hiển thị danh sách đơn: campaign name, conversion_id, sale amount, commission, trạng thái, ngày phát sinh
- [ ] Phân trang (page, page_size)
- [ ] Lọc theo thời gian, campaign, trạng thái
- [ ] Lọc theo campaign_invoice_ids (khi có)
- [ ] Hiển thị trạng thái đơn: REJECTED / WAITING_FOR_APPROVED / APPROVED / TEMPORARY_APPROVED / CALCULATED

**Dependencies:** FR-005

---

### FR-012: Affiliate Dashboard tổng hợp

**Priority:** Should Have

**Description:**
Influencer xem dashboard tổng hợp hiệu suất affiliate, aggregate từ nhiều API reports (vì Pub2 chưa có API overview tổng hợp).

**Acceptance Criteria:**
- [ ] Hiển thị summary cards: tổng clicks, tổng conversions, tổng commission (approved), tổng sale amount
- [ ] Gọi parallel 4 APIs (click, conversion, sale-amount, commission) để build dashboard
- [ ] Mặc định hiển thị dữ liệu 30 ngày gần nhất
- [ ] Cho phép thay đổi khoảng thời gian

**Dependencies:** FR-007, FR-008, FR-009, FR-010

---

### FR-013: Điểm chạm liên kết AccessTrade tại Campaign Detail

**Priority:** Must Have

**Description:**
Thêm touchpoint tại section affiliate campaign trong trang chi tiết campaign/event để hướng dẫn influencer liên kết tài khoản AccessTrade (chức năng linking đã có sẵn).

**Acceptance Criteria:**
- [ ] **Banner trên đầu section** affiliate campaign trong campaign detail: hiển thị khi user chưa liên kết AccessTrade, kèm CTA "Liên kết tài khoản"
- [ ] **Popup khi thực hiện action**: khi bấm "Tạo link", "Xem báo cáo" mà chưa link → show popup yêu cầu liên kết trước
- [ ] Popup có nút redirect đến trang liên kết AccessTrade (flow SSO hiện tại)
- [ ] Sau khi liên kết thành công → redirect về trang campaign detail đang xem
- [ ] Banner tự ẩn khi đã liên kết thành công

**Dependencies:** FR-004, chức năng liên kết AccessTrade hiện có

---

### FR-014: Backend Pub2 API Client (HMAC Authentication)

**Priority:** Must Have

**Description:**
Backend Go service gọi Pub2 APIs với HMAC signature authentication. Đây là service dùng chung cho tất cả Pub2 API calls.

**Acceptance Criteria:**
- [ ] Implement HMAC-SHA256 signature: `HMACSHA256(clientId + "|" + clientTraceNo + "|" + clientRequestTime, clientSecret)`
- [ ] Headers: `client-id`, `client-trace-no` (UUID unique), `client-request-time`, `client-signature`
- [ ] Config từ environment: `PUB2_ENDPOINT`, `PUB2_CLIENT_ID`, `PUB2_CLIENT_SECRET`
- [ ] Xử lý response chuẩn: check `status` (success/fail/error), `code` (PX00000 = OK), `message`
- [ ] Retry logic khi gặp network error (max 3 retries)
- [ ] Logging request/response cho debugging
- [ ] Timeout configuration (default 10s)

**Dependencies:** None

---

### FR-015: Backend Affiliate Campaign CRUD APIs

**Priority:** Must Have

**Description:**
Backend APIs cho Admin CRUD affiliate campaigns, lưu trong MongoDB.

**Acceptance Criteria:**
- [ ] `POST /admin/affiliate-campaigns` — Tạo campaign (partner field required, immutable after creation)
- [ ] `GET /admin/affiliate-campaigns` — Danh sách campaigns (filter, search, pagination; scoped by staff's partner)
- [ ] `GET /admin/affiliate-campaigns/:id` — Chi tiết campaign
- [ ] `PUT /admin/affiliate-campaigns/:id` — Cập nhật campaign (partner field ignored if provided)
- [ ] `PATCH /admin/affiliate-campaigns/:id/status` — Thay đổi status
- [ ] Validate: pub2_campaign_id unique, required fields, partner required on creation
- [ ] Mapping APIs (campaign ↔ affiliate campaign):
  - `POST /admin/campaign-affiliate-mappings` — Liên kết affiliate campaign với campaign/event
  - `DELETE /admin/campaign-affiliate-mappings/:id` — Gỡ liên kết
  - `GET /admin/campaigns/:id/affiliate-campaigns` — Danh sách affiliate campaigns liên kết với campaign
  - `GET /admin/affiliate-campaigns/:id/campaigns` — Danh sách campaigns liên kết với affiliate campaign
- [ ] Public APIs cho influencer:
  - `GET /events/:id/affiliate-campaigns` — Danh sách affiliate campaigns active liên kết với campaign
  - `GET /affiliate-campaigns/:id` — Chi tiết affiliate campaign

**Dependencies:** FR-014

---

### FR-016: Backend Affiliate Link & Report APIs

**Priority:** Must Have

**Description:**
Backend APIs cho influencer tạo link và xem báo cáo, proxy qua Pub2 APIs.

**Acceptance Criteria:**
- [ ] `POST /affiliate-campaigns/:id/join` — Tham gia chiến dịch (proxy Pub2 API 1.2)
- [ ] `GET /affiliate-campaigns/:id/contract` — Lấy trạng thái tham gia chiến dịch
- [ ] `POST /affiliate-campaigns/:id/generate-link` — Tạo affiliate link (proxy Pub2 API 2, yêu cầu contract APPROVED)
- [ ] `GET /affiliate-links` — Danh sách links đã tạo (từ DB Ambassador)
- [ ] `POST /affiliate-reports/clicks` — Báo cáo click (proxy Pub2 API 3.1)
- [ ] `POST /affiliate-reports/conversions` — Báo cáo conversion (proxy Pub2 API 3.2)
- [ ] `POST /affiliate-reports/sale-amount` — Báo cáo sale amount (proxy Pub2 API 3.3)
- [ ] `POST /affiliate-reports/commission` — Báo cáo commission (proxy Pub2 API 3.4)
- [ ] `POST /affiliate-reports/orders` — Danh sách đơn (proxy Pub2 API 8)
- [ ] Tất cả APIs yêu cầu authentication + đã link AccessTrade
- [ ] Tự động inject `sso_user_id` từ user data, không cho frontend truyền

**Dependencies:** FR-014, FR-015

---

## Non-Functional Requirements

---

### NFR-001: Performance — API Response Time

**Priority:** Must Have

**Description:**
API response time phải nhanh, đặc biệt các API proxy qua Pub2.

**Acceptance Criteria:**
- [ ] Internal APIs (CRUD campaigns, list links): < 200ms cho 95% requests
- [ ] Proxy APIs (Pub2 reports): < 3s cho 95% requests (phụ thuộc Pub2 latency)
- [ ] Dashboard aggregate (4 parallel API calls): < 5s

**Rationale:** User experience — influencer không chờ lâu khi xem báo cáo

---

### NFR-002: Security — HMAC & Data Protection

**Priority:** Must Have

**Description:**
Bảo mật trong giao tiếp với Pub2 và bảo vệ dữ liệu người dùng.

**Acceptance Criteria:**
- [ ] Pub2 credentials (client_id, client_secret) lưu trong environment variables, KHÔNG hardcode
- [ ] HMAC signature unique per request (client-trace-no = UUID)
- [ ] `sso_user_id` inject từ backend, frontend không thể spoof
- [ ] Affiliate links lưu trong DB chỉ thuộc về user đã tạo
- [ ] Admin APIs yêu cầu admin role

**Rationale:** Tránh data leak, unauthorized access, credential exposure

---

### NFR-003: Security — Tenant Isolation

**Priority:** Must Have

**Description:**
Dữ liệu affiliate thuộc về Ambassador platform, không leak sang tenant khác (TCB, Vinfast) khi scale.

**Acceptance Criteria:**
- [ ] `sub2` parameter trong Pub2 API calls phải identify Ambassador platform
- [ ] Report APIs chỉ trả dữ liệu của user hiện tại (filter by sso_user_id)
- [ ] Không expose pub2 credentials ra frontend

**Rationale:** Multi-tenant isolation, competitive data protection

---

### NFR-004: Reliability — Error Handling

**Priority:** Must Have

**Description:**
Xử lý graceful khi Pub2 API down hoặc trả lỗi.

**Acceptance Criteria:**
- [ ] Pub2 API timeout: hiển thị thông báo "Hệ thống đang bận, vui lòng thử lại"
- [ ] Pub2 error response (code != PX00000): parse message và hiển thị cho user
- [ ] Retry logic: max 3 retries với exponential backoff cho network errors
- [ ] Circuit breaker: nếu Pub2 fail liên tục > 5 lần → short-circuit 30s

**Rationale:** Pub2 là external dependency, cần graceful degradation

---

### NFR-005: Usability — Mobile Responsive

**Priority:** Should Have

**Description:**
Tất cả UI affiliate campaigns phải responsive trên mobile.

**Acceptance Criteria:**
- [ ] Campaign list, detail, dashboard hiển thị tốt trên mobile (≥ 320px width)
- [ ] Copy link hoạt động trên mobile
- [ ] Biểu đồ báo cáo responsive

**Rationale:** Nhiều influencer sử dụng mobile

---

### NFR-006: Maintainability — Pub2 Client Module

**Priority:** Should Have

**Description:**
Pub2 API client phải được tách thành module riêng, dễ maintain và reuse.

**Acceptance Criteria:**
- [ ] Pub2 client là Go package riêng trong `internal/module/pub2/`
- [ ] Interface-based design để dễ mock trong tests
- [ ] Config externalized (endpoint, credentials, timeout)

**Rationale:** Clean architecture, reusable cho các tenant khác nếu cần

---

### NFR-007: Compatibility — Existing System

**Priority:** Must Have

**Description:**
Tích hợp mới không ảnh hưởng đến hệ thống hiện tại của Ambassador.

**Acceptance Criteria:**
- [ ] Affiliate campaigns là collection riêng trong MongoDB, không sửa schema event/campaign hiện tại
- [ ] Routing mới không conflict với routes hiện có
- [ ] Chức năng liên kết AccessTrade hiện tại không bị ảnh hưởng

**Rationale:** Zero regression risk

---

## Epics

---

### EPIC-001: Admin Affiliate Campaign Management

**Description:**
Admin tạo, chỉnh sửa, quản lý affiliate campaigns, và liên kết chúng với campaigns/events hiện tại trên Ambassador Admin panel.

**Functional Requirements:**
- FR-001: Admin tạo Affiliate Campaign
- FR-002: Admin quản lý danh sách Affiliate Campaigns
- FR-003: Admin liên kết Affiliate Campaign với Campaign/Event
- FR-015: Backend Affiliate Campaign CRUD + Mapping APIs

**Story Count Estimate:** 6-8

**Priority:** Must Have

**Business Value:** Foundation — không có campaigns thì không có gì để hiển thị cho influencer

---

### EPIC-002: Pub2 API Integration (Backend)

**Description:**
Backend Go service tích hợp Pub2 APIs: HMAC client, link generation, reports proxy.

**Functional Requirements:**
- FR-014: Backend Pub2 API Client (HMAC Authentication)
- FR-016: Backend Affiliate Link & Report APIs

**Story Count Estimate:** 5-7

**Priority:** Must Have

**Business Value:** Core integration — backend phải hoạt động trước khi frontend có thể consume

---

### EPIC-003: Influencer Affiliate Campaign Experience

**Description:**
Influencer browse campaigns, tham gia chiến dịch, tạo link, và quản lý links đã tạo.

**Functional Requirements:**
- FR-004: Influencer xem Affiliate Campaign trong chi tiết Campaign
- FR-017: Influencer tham gia chiến dịch (Join Campaign)
- FR-005: Influencer tạo Affiliate Link
- FR-006: Influencer xem danh sách Link đã tạo
- FR-013: Điểm chạm liên kết AccessTrade tại Campaign Detail

**Story Count Estimate:** 7-9

**Priority:** Must Have

**Business Value:** Core user experience — đây là touchpoint chính của influencer

---

### EPIC-004: Affiliate Reports & Dashboard

**Description:**
Influencer xem báo cáo hiệu suất affiliate: clicks, conversions, sale amount, commission, danh sách đơn.

**Functional Requirements:**
- FR-007: Báo cáo Click
- FR-008: Báo cáo Conversion
- FR-009: Báo cáo Sale Amount
- FR-010: Báo cáo Commission
- FR-011: Danh sách đơn hàng chi tiết
- FR-012: Affiliate Dashboard tổng hợp

**Story Count Estimate:** 6-8

**Priority:** Must Have (FR-007,008,010,011), Should Have (FR-009,012)

**Business Value:** Transparency — influencer cần thấy hiệu suất để tiếp tục sử dụng

---

## User Stories (High-Level)

### EPIC-001: Admin Campaign Management
- As an **Admin**, I want to create an affiliate campaign with Pub2 campaign ID so that influencers can generate affiliate links.
- As an **Admin**, I want to manage (edit, activate, deactivate) affiliate campaigns so that I control what influencers see.
- As an **Admin**, I want to link an affiliate campaign to one or more existing campaigns/events so that influencers see affiliate options within campaign detail.
- As an **Admin**, I want to search and filter affiliate campaigns so that I can quickly find and manage them.

### EPIC-002: Pub2 API Integration
- As a **Backend service**, I want to authenticate with Pub2 using HMAC-SHA256 so that API calls are secure.
- As a **Backend service**, I want to proxy Pub2 report APIs so that frontend can display data without exposing Pub2 credentials.
- As a **Backend service**, I want to generate affiliate links via Pub2 API so that influencers get tracking links.

### EPIC-003: Influencer Campaign Experience
- As an **Influencer**, I want to see affiliate campaigns inside a campaign detail page so that I can discover affiliate opportunities within campaigns I'm already participating in.
- As an **Influencer**, I want to join an affiliate campaign so that I can get approved to generate affiliate links.
- As an **Influencer**, I want to see my campaign join status (pending/approved/rejected) so that I know when I can start generating links.
- As an **Influencer**, I want to see a prompt to link my AccessTrade account when I try to join or create a link so that I know what's required.
- As an **Influencer**, I want to generate and copy an affiliate link (after being approved) so that I can share it with my audience.
- As an **Influencer**, I want to see all my generated links so that I can reuse them.

### EPIC-004: Reports & Dashboard
- As an **Influencer**, I want to see click statistics over time so that I know how my links perform.
- As an **Influencer**, I want to see my commission earnings by status so that I know my pending and approved income.
- As an **Influencer**, I want to see a list of my orders so that I can track individual conversions.
- As an **Influencer**, I want a dashboard overview so that I get a quick summary of my affiliate performance.

---

## User Personas

### 1. Influencer (Primary User)
- **Mô tả:** Content creator đã đăng ký trên Ambassador, có/chưa có tài khoản AccessTrade
- **Mục tiêu:** Kiếm thêm thu nhập từ affiliate commission bên cạnh view rewards
- **Hành vi:** Browse campaigns → tạo link → chia sẻ → theo dõi hiệu suất
- **Pain points:** Không biết campaign nào phù hợp, quá trình liên kết phức tạp

### 2. Admin (Secondary User)
- **Mô tả:** Nhân viên AccessTrade/Ambassador quản lý platform
- **Mục tiêu:** Curate affiliate campaigns phù hợp, quản lý chất lượng
- **Hành vi:** Chọn lọc campaigns từ Pub2 → tạo trên admin → monitor hiệu suất
- **Pain points:** Tránh hiện competitor campaigns, đảm bảo brand safety

---

## User Flows

### Flow 1: Influencer tạo Affiliate Link (Happy Path)

```
Influencer đã liên kết AccessTrade
  → Vào chi tiết campaign/event hiện tại
  → Scroll đến section "Affiliate Campaigns"
  → Thấy affiliate campaign(s) được liên kết
  → Xem chi tiết: commission, mô tả, điều kiện
  → Click "Tham gia chiến dịch"
  → Hệ thống gọi Pub2 API 1.2 → tạo contract
  → Contract status = APPROVED → nút "Tạo link" được enable
  → Click "Tạo link affiliate"
  → Hệ thống gọi Pub2 API 2 → trả về link
  → Copy link (ngắn hoặc dài)
  → Chia sẻ link trên social media / video
```

### Flow 2: Influencer chưa liên kết AccessTrade

```
Influencer chưa liên kết
  → Vào chi tiết campaign/event hiện tại
  → Scroll đến section "Affiliate Campaigns"
  → Thấy banner: "Liên kết tài khoản AccessTrade để bắt đầu"
  → Click "Tham gia chiến dịch" hoặc "Tạo link affiliate"
  → Popup hiện: "Bạn cần liên kết tài khoản AccessTrade trước"
  → Click "Liên kết ngay" → redirect tới trang liên kết (SSO flow hiện tại)
  → Liên kết thành công → redirect về campaign detail đang xem
  → Tham gia chiến dịch → Tạo link thành công
```

### Flow 2b: Influencer tham gia chiến dịch — chờ duyệt

```
Influencer đã liên kết AccessTrade
  → Vào chi tiết campaign/event → section "Affiliate Campaigns"
  → Click "Tham gia chiến dịch"
  → Hệ thống gọi Pub2 API 1.2 → contract_status = PENDING
  → Hiển thị: "Đang chờ duyệt tham gia chiến dịch"
  → Nút "Tạo link" bị disable
  → (Quay lại sau khi được duyệt → contract_status = APPROVED → tạo link bình thường)
```

### Flow 3: Admin tạo và liên kết Affiliate Campaign

```
Admin login Ambassador Admin
  → Vào "Affiliate Campaigns" → "Tạo mới"
  → Điền thông tin: title, description, banner, category
  → Nhập pub2_campaign_id (lấy từ Pub2 dashboard)
  → Nhập pub2_campaign_url (original_url cho tracking)
  → Nhập commission info
  → Save (status = draft)
  → Review → Activate (status = active)
  → Vào chi tiết campaign/event hiện tại (admin)
  → Click "Liên kết Affiliate Campaign"
  → Chọn affiliate campaign(s) từ danh sách
  → Confirm → Mapping được tạo
  → Influencer vào campaign detail sẽ thấy affiliate section
```

---

## Dependencies

### Internal Dependencies

| Dependency | Mô tả | Status |
|-----------|--------|--------|
| Liên kết AccessTrade (SSO) | OAuth2 flow đã có sẵn, lưu `sso_user_id` trong user data | ✅ Có sẵn |
| Ambassador Backend (Go + Echo) | Framework, auth middleware, MongoDB connection | ✅ Có sẵn |
| Ambassador Frontend (React + UmiJS) | UI framework, routing, state management | ✅ Có sẵn |
| Ambassador Admin (React + UmiJS + Ant Design) | Admin panel framework | ✅ Có sẵn |

### External Dependencies

| Dependency | Mô tả | Status |
|-----------|--------|--------|
| Pub2 API (AccessTrade) | 7 APIs đã cung cấp (join campaign, link, click, conversion, sale-amount, commission, orders) | ✅ Sẵn sàng (dev env) |
| Pub2 Credentials | `client_id` + `client_secret` cho HMAC authentication | ✅ Có (dev) |
| Pub2 API — Campaign Info (API 1) | Chưa cung cấp | ⏳ Chưa có |
| Pub2 API — Webhook (API 7) | Chưa cung cấp | ⏳ Chưa có |
| Pub2 API — Overview (API 6) | Chưa cung cấp (dùng API 3.x thay thế) | ❌ Không có |

---

## Assumptions

1. **Pub2 dev environment** (`core-aff.dev.accesstrade.me`) ổn định và available cho development
2. **`sso_user_id`** từ AccessTrade SSO mapping chính xác với Pub2 publisher ID
3. **`partner_code`** mặc định `"PARTNER_1_POINT_5"` cho Ambassador
4. **Pub2 API rate limit** đủ cho lượng influencer Ambassador (chưa có thông tin cụ thể)
5. **Admin** sẽ tự lấy `pub2_campaign_id` từ Pub2 dashboard (manual flow)
6. **Influencer** chỉ cần liên kết AccessTrade 1 lần, không cần re-authenticate cho mỗi API call
7. **Report data** từ Pub2 API là on-demand (real-time), chưa cần scheduled sync ở phase đầu
8. **MongoDB** hiện tại đủ capacity cho thêm collections affiliate campaigns và links

---

## Out of Scope

1. **OAuth2 flow mới cho Pub2** — dùng HMAC authentication hiện có, không implement OAuth riêng với Pub2
2. **Auto-sync campaigns từ Pub2** — Admin tạo thủ công, không auto-import
3. **Webhook real-time** (Pub2 API 7 chưa có) — dùng on-demand reports
4. **Scheduled sync / caching reports** — Phase sau, MVP dùng on-demand
5. **Payout / rút tiền commission** — Quy trình riêng, không nằm trong scope này
6. **Multi-tenant** (TCB, Vinfast) — PRD này chỉ cho Ambassador
7. **AI campaign recommendations** — Phase sau
8. **Fraud detection** — Phase sau
9. **Consolidated payout across platforms** — Phase sau

---

## Open Questions

| # | Question | Owner | Status |
|---|----------|-------|--------|
| 1 | `partner_code` cho Ambassador production là gì? Vẫn là `PARTNER_1_POINT_5`? | Pub2 team | Open |
| 2 | Pub2 API rate limit là bao nhiêu? | Pub2 team | Open |
| 3 | `sso_user_id` từ AccessTrade SSO có chắc chắn match với Pub2 publisher ID? | AT team | Open |
| 4 | Pub2 production endpoint là gì? (hiện chỉ có dev: `core-aff.dev.accesstrade.me`) | Pub2 team | Open |
| 5 | Sub parameters nên dùng thế nào cho Ambassador? `sub1`=user_id, `sub2`=platform, `sub3`=?, `sub4`=? | AT team | Open |
| 6 | Khi nào Pub2 cung cấp Webhook API (API 7)? | Pub2 team | Open |
| 7 | Campaign trên Pub2 có expire/thay đổi status không? Cần sync không? | Pub2 team | Open |

---

## Approval & Sign-off

### Stakeholders

| Role | Name | Responsibility |
|------|------|---------------|
| Product Owner | TBD | Requirements approval |
| Engineering Lead | vinhnguyen | Technical feasibility, implementation |
| Pub2 Liaison | TBD | API support, credentials |
| Ambassador Admin | TBD | UAT, campaign curation |

### Approval Status

- [ ] Product Owner
- [ ] Engineering Lead
- [ ] Pub2 Team (API confirmation)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-25 | vinhnguyen | Initial PRD |
| 1.1 | 2026-03-25 | vinhnguyen | Thêm FR-003 mapping campaign ↔ affiliate campaign. Sửa FR-004: affiliate hiển thị trong campaign detail (không standalone). Cập nhật Epics, User Flows, Traceability Matrix. |
| 1.2 | 2026-03-26 | vinhnguyen | Thêm FR-017: Tham gia chiến dịch (Join Campaign) — influencer phải join campaign (Pub2 API 1.2) trước khi tạo link. Cập nhật FR-005 dependency, FR-016 endpoints, User Flows (thêm Flow 2b), EPIC-003, User Stories, Traceability Matrix. |

---

## Next Steps

### Phase 3: Architecture

Run `/architecture` to create system architecture based on these requirements.

The architecture will address:
- MongoDB schema cho affiliate campaigns, links
- Go backend module structure (pub2 client, services, handlers)
- Frontend component structure
- Admin panel pages
- API endpoint design
- HMAC authentication flow

### Phase 4: Sprint Planning

After architecture is complete, run `/sprint-planning` to:
- Break epics into detailed user stories
- Estimate story complexity
- Plan sprint iterations
- Begin implementation

---

**This document was created using BMAD Method v6 - Phase 2 (Planning)**

---

## Appendix A: Requirements Traceability Matrix

| Epic ID | Epic Name | Functional Requirements | Story Count (Est.) |
|---------|-----------|-------------------------|-------------------|
| EPIC-001 | Admin Campaign Management | FR-001, FR-002, FR-003, FR-015 | 6-8 |
| EPIC-002 | Pub2 API Integration | FR-014, FR-016 | 5-7 |
| EPIC-003 | Influencer Campaign Experience | FR-004, FR-017, FR-005, FR-006, FR-013 | 7-9 |
| EPIC-004 | Reports & Dashboard | FR-007, FR-008, FR-009, FR-010, FR-011, FR-012 | 6-8 |

**Total Estimated Stories:** 24-32

---

## Appendix B: Prioritization Details

### Functional Requirements

| Priority | Count | FRs |
|----------|-------|-----|
| **Must Have** | 15 | FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-010, FR-011, FR-013, FR-014, FR-015, FR-016, FR-017 |
| **Should Have** | 2 | FR-009, FR-012 |
| **Could Have** | 0 | — |

### Non-Functional Requirements

| Priority | Count | NFRs |
|----------|-------|------|
| **Must Have** | 5 | NFR-001, NFR-002, NFR-003, NFR-004, NFR-007 |
| **Should Have** | 2 | NFR-005, NFR-006 |

---

## Appendix C: Pub2 API Reference (Quick)

| API | Method | Path | Status |
|-----|--------|------|--------|
| API 1: Campaign Info | - | - | ❌ Chưa có |
| API 1.2: Tham gia chiến dịch | POST | `/pgw-api/campaign-service/api/v1/contracts` | ✅ |
| API 2: Affiliate Link | POST | `/pgw-api/tracking-service/api/v1.0/publisher/affiliate/link` | ✅ |
| API 3.1: Click Stats | POST | `/pgw-api/tracking-service/api/v1.0/publisher/affiliate/statistics/click` | ✅ |
| API 3.2: Conversion Stats | POST | `/pgw-api/conversion-service/api/v1.0/publisher/affiliate/statistics/conversion` | ✅ |
| API 3.3: Sale Amount | POST | `/pgw-api/conversion-service/api/v1.0/publisher/affiliate/statistics/sale-amount` | ✅ |
| API 3.4: Commission | POST | `/pgw-api/conversion-service/api/v1.0/publisher/affiliate/statistics/commission` | ✅ |
| API 6: Overview | - | - | ❌ Chưa có |
| API 7: Webhook | - | - | ❌ Chưa có |
| API 8: Orders List | POST | `/pgw-api/conversion-service/api/v1.0/publisher/affiliate/conversions` | ✅ |
