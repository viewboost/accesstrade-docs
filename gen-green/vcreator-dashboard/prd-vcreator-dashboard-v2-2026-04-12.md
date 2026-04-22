# PRD: VCreator Dashboard v2

**Project:** Gen-Green — VCreator Dashboard
**Date:** 2026-04-12
**Version:** 2.0
**Author:** Product Manager
**Status:** Draft
**Demo:** `demo-gen-green` → `/dashboard-moi`

---

## 1. Executive Summary

Xây dựng dashboard analytics mới cho VCreator (Gen-Green), thay thế hệ thống admin hiện tại. Dashboard gồm 4 module chính: **Thống kê** (analytics đa widget), **Nội dung** (quản lý video/content), **Creator** (quản lý creator + phân loại CBNV), **Xuất dữ liệu** (export jobs + chọn cột linh hoạt).

Hệ thống vận hành theo trục **Partner (ADV/Advertiser)** — tất cả data analytics, nội dung, creator đều filter theo partner. Bổ sung phân loại **CBNV/Bên ngoài** và filter **Cơ sở làm việc** để đáp ứng nhu cầu vận hành nội bộ.

---

## 2. Business Objectives

| # | Objective | Success Metric |
|---|-----------|----------------|
| 1 | Dashboard analytics hiện đại, thay thế admin cũ | Admin xem KPIs trực tiếp trên giao diện, không cần export Excel |
| 2 | Phân loại CBNV và creator bên ngoài | Trả lời nhanh "bao nhiêu CBNV cơ sở X tham gia chương trình Y?" trên dashboard |
| 3 | Filter theo Partner (ADV) — trục vận hành chính | Tất cả data filter được theo partner, cascade reset event/creator/tag |
| 4 | Export linh hoạt — user tự chọn cột | Không cần dev mỗi lần team vận hành thay đổi nhu cầu export |
| 5 | UI hiện đại, responsive | Next.js 16 + TailwindCSS, hỗ trợ theme sáng/tối, desktop + tablet |

---

## 3. User Personas

| Persona | Vai trò | Nhu cầu chính |
|---------|---------|---------------|
| **Operations Manager** | Vận hành hàng ngày | Filter CBNV/cơ sở, export chọn cột, xem phân loại creator trên table |
| **Business Lead** | Quản lý chiến lược | Xem quick stats trên giao diện, filter theo partner/cơ sở, đánh giá hiệu quả |
| **Admin VCreator** | Staff nội bộ | Xem KPIs tổng quan, duyệt nội dung, theo dõi thử thách |

---

## 4. Scope

### In Scope

| Route | Chức năng | Mô tả |
|-------|-----------|-------|
| `/analytics` | Thống kê | 13 widgets: KPIs, biểu đồ, bảng thử thách, ngân sách, tương tác, duyệt, nền tảng, đối soát |
| `/contents` | Nội dung | Table video/content + 10 filter + batch actions |
| `/creators` | Creator | Table creator + filter CBNV/cơ sở |
| `/exports` | Xuất dữ liệu | Export jobs + dialog chọn cột |
| `/login` | Đăng nhập | OAuth2 code flow |
| `/settings` | Cài đặt | Tài khoản, preferences |
| Layout | Shell | Sidebar, Header, Theme sáng/tối |

### Out of Scope

| Feature | Lý do |
|---------|-------|
| Quản lý Event CRUD | Xử lý ở admin hiện tại |
| Influencer Profiles chi tiết (demographics, reviews) | Không phù hợp domain Gen-Green |
| Affiliate dashboard (Scalef data) | Scope dự án riêng |
| Import data từ Excel | Không ưu tiên v2 |

---

## 5. Functional Requirements

### EPIC-001: Thống kê (Analytics)

#### FR-001: Filter Partner (ADV) — Trục chính

**Priority:** Must Have

**Description:**
Filter Partner (ADV/Advertiser) là trục filter chính trên toàn hệ thống. Searchable select, load dynamic từ API. Khi chọn partner → cascade reset: Event, Creator, Warning Tag.

**Acceptance Criteria:**
- [ ] Dropdown searchable hiển thị danh sách partner từ API
- [ ] Chọn partner → Event dropdown chỉ hiện event thuộc partner đó
- [ ] Chọn partner → reset Creator filter và Tag filter
- [ ] Option "Tất cả partner" → hiện data toàn bộ
- [ ] Debounce search 500ms

**Dependencies:** API `GET /partners` (searchable)

---

#### FR-002: Filter Phân loại CBNV

**Priority:** Must Have

**Description:**
Filter phân loại creator trên trang Thống kê, Nội dung, Creator. Dropdown: Tất cả / CBNV / Bên ngoài.

**Acceptance Criteria:**
- [ ] Dropdown 3 options, có mặt trên cả 3 trang
- [ ] Chọn CBNV → data chỉ hiện creator có `account_type = staff`
- [ ] Chọn Bên ngoài → data chỉ hiện creator có `account_type = creator`
- [ ] KPIs và charts cập nhật theo filter

**Dependencies:** Backend field `account_type` trên user/content response

---

#### FR-003: Filter Cơ sở làm việc

**Priority:** Must Have

**Description:**
Filter cơ sở làm việc trên cả 3 trang. Grouped dropdown (6 nhóm, 57 cơ sở).

**Acceptance Criteria:**
- [ ] Grouped dropdown: VinPalace, Vinpearl, VinWonders, Vinpearl Golf, Green SM, Khác
- [ ] 57 cơ sở hiển thị đúng nhóm
- [ ] Có search/filter text trong dropdown
- [ ] Chọn cơ sở → data filter theo `workplace_name`

**Dependencies:** Backend field `workplace_name` trên user response

---

#### FR-004: Tổng quan Nền tảng (4 KPI cards)

**Priority:** Must Have

**Description:**
4 KPI cards hiển thị tổng quan nền tảng: Tổng Creator, Creator mới, Tỷ lệ hoạt động, Tỷ lệ nghỉ. Mỗi card có trend % so kỳ trước.

**Acceptance Criteria:**
- [ ] 4 cards hiển thị đúng giá trị từ API
- [ ] Trend badge xanh (tăng) / đỏ (giảm) với % chính xác
- [ ] Responsive: 4 cột desktop, 2 cột mobile
- [ ] Data phản ứng theo filter Partner + Date range

**Dependencies:** API `GET /analytics/platform-overview`

---

#### FR-005: 6 KPI chính (Tab Tổng quan)

**Priority:** Must Have

**Description:**
6 KPI cards: Tổng Video, Lượt xem, Ngân sách %, CPV trung bình, Engagement, Tổng phí quảng cáo.

**Acceptance Criteria:**
- [ ] 6 cards hiển thị đúng, format number/currency/percent
- [ ] Responsive: 3 cột desktop, 2 cột mobile
- [ ] Phản ứng theo tất cả filter (Partner, Event, Date, CBNV, Cơ sở)

**Dependencies:** API `GET /analytics/dashboard`

---

#### FR-006: Bảng Thử thách

**Priority:** Must Have

**Description:**
Table danh sách event/thử thách thuộc partner đang chọn: Tên, Trạng thái, Ngân sách (đã dùng/tổng), Videos, Views, CPV.

**Acceptance Criteria:**
- [ ] Table hiển thị event thuộc partner đang chọn
- [ ] Trạng thái: Active (xanh), Completed (xám), Draft (vàng)
- [ ] Ngân sách hiển thị "đã dùng / tổng (%)"
- [ ] Sortable theo Views, Videos

**Dependencies:** API `GET /analytics/events`, FR-001

---

#### FR-007: Biểu đồ theo thời gian

**Priority:** Must Have

**Description:**
Multi-line/bar chart với 4 series toggle: Lượt xem, Video, Tỷ lệ tương tác, Khách hàng mới. Switch Daily/Monthly.

**Acceptance Criteria:**
- [ ] Chart render đúng data từ API
- [ ] 4 checkbox toggle series on/off
- [ ] Daily/Monthly switch
- [ ] Tooltip hiển thị giá trị khi hover
- [ ] Responsive width

**Dependencies:** API `GET /analytics/timeline`

---

#### FR-008: Ngân sách thử thách

**Priority:** Should Have

**Description:**
Widget ngân sách: progress bar % đã sử dụng + 3 metrics (Đã dùng, Tổng, Còn lại VND).

**Acceptance Criteria:**
- [ ] Progress bar gradient, % chính xác
- [ ] 3 metrics format VND
- [ ] Phản ứng theo filter Partner + Event

**Dependencies:** API `GET /analytics/budget`

---

#### FR-009: Tương tác

**Priority:** Should Have

**Description:**
Widget tương tác: Lượt xem, Thích, Bình luận (với icon + tỷ lệ %). Tổng tỷ lệ tương tác.

**Acceptance Criteria:**
- [ ] 3 metrics format số lớn (M/K)
- [ ] % tính đúng (Thích/Lượt xem, Bình luận/Lượt xem)
- [ ] Tỷ lệ tương tác tổng hợp

**Dependencies:** API `GET /analytics/interactions`

---

#### FR-010: Trạng thái duyệt

**Priority:** Should Have

**Description:**
Stacked bar (Đã duyệt/Chờ/Từ chối) + 3 stats (% + count) + Top 5 lý do từ chối.

**Acceptance Criteria:**
- [ ] Stacked bar 3 màu: xanh/vàng/đỏ
- [ ] 3 stats: % + số video
- [ ] Top 5 lý do từ chối, sort giảm dần

**Dependencies:** API `GET /analytics/approval-status`

---

#### FR-011: Phân bố nền tảng + Lượt xem theo nền tảng

**Priority:** Should Have

**Description:**
Pie chart phân bố content theo platform + Horizontal bar chart lượt xem theo platform.

**Acceptance Criteria:**
- [ ] Pie chart hiển thị % + count
- [ ] Bar chart horizontal, mỗi platform 1 bar
- [ ] Legend rõ ràng

**Dependencies:** API `GET /analytics/platforms`

---

#### FR-012: Đối soát thanh toán

**Priority:** Should Have

**Description:**
3 KPI (Tổng đợt, Yêu cầu thành công, Đã thanh toán VND) + Table đợt chuyển.

**Acceptance Criteria:**
- [ ] 3 KPI cards format đúng
- [ ] Table: Tên đợt, Trạng thái, Yêu cầu, Thành công, Tỷ lệ, Tổng tiền, Đã TT, Ngày
- [ ] Trạng thái badge: Hoàn thành (xanh), Đang xử lý (vàng)

**Dependencies:** API `GET /analytics/reconciliation`

---

### EPIC-002: Nội dung (Contents)

#### FR-013: Table nội dung

**Priority:** Must Have

**Description:**
Table nội dung 12 cột: Thumbnail, Tiêu đề, Creator, **Phân loại**, **Cơ sở làm việc**, **Hashtag cá nhân**, Nguồn, Sự kiện, Lượt xem, Trạng thái, Warning Tags, Ngày đăng.

**Acceptance Criteria:**
- [ ] 12 cột hiển thị đúng
- [ ] Phân loại: Badge "CBNV" (xanh) / "Bên ngoài" (xám)
- [ ] Cơ sở: tên cơ sở hoặc "—"
- [ ] Hashtag: hiển thị hashtag cá nhân
- [ ] Sortable theo Lượt xem
- [ ] Pagination 20 items/page

**Dependencies:** Backend fields `account_type`, `workplace_name`, `hashtag` trên content response

---

#### FR-014: Filter nội dung

**Priority:** Must Have

**Description:**
10 filter: **Partner (ADV)**, Search, Date Range, Source, Event, Status, Created By, Warning Tag, **Phân loại**, **Cơ sở làm việc**.

**Acceptance Criteria:**
- [ ] Partner filter đứng đầu, cascade reset Event + Created By + Tag
- [ ] 10 filter hoạt động đúng
- [ ] Debounce search 500ms
- [ ] Reset pagination khi thay đổi filter

**Dependencies:** FR-001, FR-002, FR-003

---

#### FR-015: Batch actions nội dung

**Priority:** Should Have

**Description:**
Batch actions: Duyệt, Chờ duyệt, Từ chối (với lý do), Cập nhật Tags, Xóa Tags.

**Acceptance Criteria:**
- [ ] Checkbox chọn nhiều rows
- [ ] Toolbar batch actions hiện khi có selection
- [ ] Từ chối yêu cầu nhập lý do (modal)
- [ ] Cập nhật realtime sau action

**Dependencies:** API `POST /contents/batch-action`

---

### EPIC-003: Creator

#### FR-016: Table Creator

**Priority:** Must Have

**Description:**
Table 10 cột: Avatar, Tên, **Hashtag cá nhân**, **Phân loại**, **Nơi làm việc**, Tổng view, Tổng tiền, Đã rút, Số video, Ngày tham gia.

**Acceptance Criteria:**
- [ ] 10 cột hiển thị đúng
- [ ] Format: view (M/K), tiền (VND), ngày (dd/mm/yyyy)
- [ ] Sortable theo Tổng view, Tổng tiền, Số video
- [ ] Pagination 20 items/page

**Dependencies:** API `GET /creators`

---

#### FR-017: Filter Creator

**Priority:** Must Have

**Description:**
Filter bar: Partner (ADV), Search, Phân loại (CBNV/Bên ngoài), Cơ sở làm việc.

**Acceptance Criteria:**
- [ ] 4 filter hoạt động đúng
- [ ] Partner cascade reset
- [ ] Cơ sở grouped dropdown

**Dependencies:** FR-001, FR-002, FR-003

---

### EPIC-004: Xuất dữ liệu

#### FR-018: Export chọn cột

**Priority:** Must Have

**Description:**
Dialog checkbox list cho user chọn cột muốn xuất. Default preset bỏ tick cột thừa. Áp dụng cho Nội dung, Creator, Thống kê.

**Acceptance Criteria:**
- [ ] Dialog hiển thị tất cả cột (checkbox)
- [ ] Default: tick cột hiển thị, bỏ tick cột thừa (ID video, Thumbnail, Sentiment, Đối tác, Ngày tạo)
- [ ] Nút "Chọn tất cả" / "Mặc định"
- [ ] Bấm "Xuất" → tạo export job với `columns[]` param

**Dependencies:** API `POST /exports` hỗ trợ `columns[]`

---

#### FR-019: Quản lý export jobs

**Priority:** Must Have

**Description:**
Trang danh sách export jobs: Tên, Loại, Trạng thái, Số dòng, Số cột, Kích thước, Thời gian, Download.

**Acceptance Criteria:**
- [ ] Table lịch sử export jobs
- [ ] Trạng thái: Hoàn tất (download), Đang xử lý, Thất bại (retry)
- [ ] Download qua pre-signed URL
- [ ] Polling status cho jobs đang xử lý

**Dependencies:** API `GET /exports`, `GET /exports/:id/presign`

---

### EPIC-005: Layout & Auth

#### FR-020: Sidebar navigation

**Priority:** Must Have

**Description:**
Sidebar: Thống kê, Nội dung, Creator, Hiệu suất, Xuất dữ liệu, Cài đặt, Theme toggle, Link về Admin.

**Acceptance Criteria:**
- [ ] 5 menu items chính + 2 phụ
- [ ] Active state highlight
- [ ] Responsive: collapse trên mobile

---

#### FR-021: Auth OAuth2 code flow

**Priority:** Must Have

**Description:**
Đăng nhập qua VCreator Admin OAuth2: redirect → login → callback code → exchange token.

**Acceptance Criteria:**
- [ ] Redirect sang VCreator Admin khi chưa login
- [ ] Callback xử lý authorization code
- [ ] Token inject vào mọi API request
- [ ] 401 → clear token + redirect login

**Dependencies:** VCreator Admin OAuth2 endpoint

---

#### FR-022: Theme sáng/tối

**Priority:** Could Have

**Description:**
Toggle theme sáng/tối trong sidebar. Persist vào localStorage.

**Acceptance Criteria:**
- [ ] Toggle hoạt động
- [ ] Persist preference

---

## 6. Non-Functional Requirements

### NFR-001: Performance — Response Time

**Priority:** Must Have

Dashboard load < 3s (first meaningful paint). API filter/pagination < 500ms. Chart render < 1s.

---

### NFR-002: Performance — Caching

**Priority:** Must Have

Client-side cache (stale time 5 phút). Retry 3 lần với exponential backoff. Invalidate on mutation.

---

### NFR-003: Compatibility — Browser

**Priority:** Must Have

Chrome 90+, Safari 15+, Firefox 90+, Edge 90+. Responsive desktop (1024px+) + tablet (768px+).

---

### NFR-004: Security — Auth Token

**Priority:** Must Have

Access token inject via HTTP interceptor. 401 auto-redirect login. Token không expose qua URL.

---

### NFR-005: Maintainability — Code Quality

**Priority:** Should Have

TypeScript strict mode. Hooks pattern cho API calls. Translation keys cho tất cả UI text.

---

### NFR-006: Deployment

**Priority:** Must Have

Standalone build output, Docker-ready. ENV config: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_ADMIN_URL`.

---

## 7. Epics & Traceability

| Epic | FRs | Stories (est.) | Priority |
|------|-----|----------------|----------|
| EPIC-001: Thống kê | FR-001 → FR-012 | 12-15 | Must Have |
| EPIC-002: Nội dung | FR-013 → FR-015 | 4-6 | Must Have |
| EPIC-003: Creator | FR-016 → FR-017 | 3-4 | Must Have |
| EPIC-004: Xuất dữ liệu | FR-018 → FR-019 | 3-4 | Must Have |
| EPIC-005: Layout & Auth | FR-020 → FR-022 | 3-4 | Must Have |

**Tổng:** 5 epics · 22 FRs · 6 NFRs · 25-33 stories

---

## 8. Prioritization

| Priority | FRs | NFRs |
|----------|-----|------|
| Must Have | 16 | 5 |
| Should Have | 5 | 1 |
| Could Have | 1 | 0 |

---

## 9. Dependencies

### Có sẵn

| Dependency | Status |
|-----------|--------|
| VCreator Admin (OAuth2 endpoint) | ✅ |
| VCreator Backend API (analytics, contents, exports) | ✅ |

### Cần bổ sung

| Dependency | Status | Owner |
|-----------|--------|-------|
| Backend field `account_type`, `workplace_name` trên user/content | Cần bổ sung | Backend |
| API `GET /creators` với fields phân loại | Cần bổ sung | Backend |
| API `POST /exports` hỗ trợ `columns[]` param | Cần bổ sung | Backend |
| Data CBNV/Cơ sở (từ form đăng ký) | Đang thiết kế | Product |

---

## 10. Assumptions

1. Backend API giữ nguyên contract hiện tại, chỉ thêm fields mới
2. Data phân loại CBNV/Cơ sở đã có trước khi dashboard go-live
3. Admin cũ vẫn hoạt động song song trong giai đoạn chuyển đổi

---

## 11. Open Questions

1. Performance page: giữ hay bỏ ở v2?
2. Export format: chỉ Excel (.xlsx) hay thêm CSV?
3. Filter persistence: URL params hay localStorage?
4. Default theme: sáng hay tối?

---

## 12. Timeline

| Phase | Thời gian | Nội dung |
|-------|-----------|----------|
| Phase 1: Foundation | 1 ngày | Layout, Auth, Sidebar, API layer |
| Phase 2: Analytics | 1.5 ngày | Filter Partner/CBNV/Cơ sở + 13 widgets |
| Phase 3: Tables | 1 ngày | Nội dung (table + filter + batch) + Creator (table + filter) |
| Phase 4: Export | 0.5 ngày | Dialog chọn cột + Export jobs |
| Phase 5: Polish | 0.5 ngày | Test, responsive, translation |
| **Tổng** | **~4.5 ngày** | |

**Target:** Đầu tháng 5/2026 (align mùa cao điểm hè)

---

## 13. Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 16 (App Router) |
| UI | TailwindCSS 4 + shadcn/ui + Radix UI |
| Data | TanStack Query v5 + TanStack Table v8 |
| HTTP | Axios + interceptors |
| Charts | Chart.js + react-chartjs-2 |
| i18n | next-intl (vi default, en available) |
| Theme | next-themes |
| Icons | lucide-react |
| Auth | OAuth2 code flow |
| Build | Standalone output, Docker-ready |
