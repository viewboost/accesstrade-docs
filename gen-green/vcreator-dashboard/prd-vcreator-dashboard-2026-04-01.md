# PRD: VCreator Dashboard — Analytics & Xuất dữ liệu

**Project:** Gen-Green (VCreator)
**Date:** 2026-04-01
**Author:** Product Manager
**Status:** Draft
**Version:** 1.0
**Source:** Clone từ `accesstrade-projects/techcombank/dashboard` (Next.js 16)

---

## 1. Executive Summary

Xây dựng dashboard mới cho VCreator bằng cách clone và adapt từ TCB Dashboard (Next.js 16). Dashboard chỉ bao gồm **2 chức năng chính**: **Analytics** (phân tích dữ liệu event/creator) và **Xuất dữ liệu** (quản lý export jobs). Kèm theo các chức năng phụ trợ: theme sáng/tối, hỗ trợ đa ngôn ngữ (ẩn, mặc định tiếng Việt), auth, sidebar navigation.

**Cách tiếp cận:** Clone toàn bộ codebase TCB Dashboard → adapt API layer + types cho VCreator backend → rebrand. Các chức năng ngoài scope được liệt kê tại [Section 13](#13-out-of-scope).

---

## 2. Business Objectives

| # | Objective | Success Metric |
|---|-----------|----------------|
| 1 | Dashboard analytics riêng cho VCreator, không phụ thuộc TCB | VCreator dashboard hoạt động độc lập với VCreator backend |
| 2 | Theo dõi hiệu quả event và creator real-time | Admin xem được KPIs, charts, creator performance |
| 3 | Xuất dữ liệu linh hoạt | Admin tạo export job, download file khi hoàn thành |
| 4 | Trải nghiệm UI hiện đại, thống nhất | Next.js 16 + Tailwind, thay thế admin UMI cũ cho phần analytics |
| 5 | Giảm thời gian phát triển bằng cách tái sử dụng code | Hoàn thành Phase 1 trong 2 tuần (vs 6 tuần nếu build from scratch) |

---

## 3. User Personas

| Persona | Vai trò | Nhu cầu |
|---------|---------|---------|
| **Admin/Staff VCreator** | Quản lý events, theo dõi hiệu quả | Xem KPIs tổng quan, so sánh hiệu quả theo thời gian, drill-down từng event, xuất dữ liệu analytics ra file |
| **Operations Manager** | Giám sát hoạt động creator | Xem top creators, segmentation, engagement rates |

---

## 4. Scope

### 4.1 Chức năng trong scope

| Chức năng | Route | Mức sửa | Mô tả |
|-----------|-------|---------|-------|
| **Analytics** | `/analytics` | Trung bình | Adapt KPIs, charts, filters cho VCreator domain |
| **Xuất dữ liệu** | `/exports` | Thấp | Đổi API endpoints |
| **Auth (code flow)** | N/A | Thấp | Giữ cơ chế OAuth2 code flow từ Admin, đổi endpoint |
| **Redirect** | `/` → `/vi/analytics` | Thấp | Entry point |

### 4.2 Chức năng phụ trợ

| Feature | Hành động | Chi tiết |
|---------|-----------|----------|
| **Theme sáng/tối** | Giữ nguyên | `next-themes`, toggle button trong sidebar |
| **Đa ngôn ngữ (i18n)** | Giữ infrastructure, ẩn UI | Giữ `next-intl`, default `vi`, ẩn toggle. Code vẫn hỗ trợ `en` nhưng UI không cho chuyển |
| **Sidebar** | Adapt | Chỉ còn 2 menu: Analytics, Xuất dữ liệu. Thêm link quay về VCreator Admin |
| **Error Boundary** | Giữ nguyên | React error boundary |
| **React Query** | Giữ nguyên | TanStack Query v5 với retry + cache |

---

## 5. Functional Requirements

### FR-001: Analytics Dashboard — KPI Grid

**Priority:** Must Have

**Description:**
Hiển thị 6 KPI cards tổng quan trên tab Overview, adapt cho VCreator domain.

**KPIs (adapted từ TCB):**

| # | KPI TCB | KPI VCreator | Data Source | Format |
|---|---------|-------------|-------------|--------|
| 1 | Total Videos | **Tổng nội dung** | `analytics/dashboard` → totalVideos | number |
| 2 | Total Views | **Tổng lượt xem** | `analytics/dashboard` → totalViews | number |
| 3 | Budget Used | **Ngân sách đã dùng** | `analytics/dashboard` → budgetUsed | percent |
| 4 | CPV | **CPV (chi phí/lượt xem)** | `analytics/dashboard` → cpv | currency (VND) |
| 5 | Avg Engagement | **Tương tác trung bình** | `analytics/dashboard` → avgEngagement | percent |
| 6 | Total Payment | **Tổng chi trả** | `analytics/dashboard` → totalPayment | currency (VND) |

**Acceptance Criteria:**
- [ ] 6 KPI cards hiển thị đúng data từ VCreator analytics API
- [ ] Mỗi KPI có trend indicator (so sánh với period trước)
- [ ] Loading skeleton khi đang fetch
- [ ] Format number: `1,234,567` (dấu phẩy ngàn), currency: `1,234,567đ`

---

### FR-002: Analytics Dashboard — Charts

**Priority:** Must Have

**Description:**
Hiển thị các biểu đồ phân tích trên tab Overview.

**Charts giữ lại:**

| Chart | Loại | Dữ liệu | Endpoint |
|-------|------|----------|----------|
| **Timeline Chart** | Line | Views, Videos, Engagement theo ngày | `GET /analytics/trends` |
| **Budget Widget** | Progress bar | Ngân sách đã dùng vs tổng | `GET /analytics/dashboard` |
| **Interaction Breakdown** | 4 metric cards | Views, Likes, Comments, Shares | `GET /analytics/dashboard` |
| **Approval Chart** | Donut | Approved%, Pending%, Rejected% | `GET /analytics/approval` |
| **Platform Charts** | Pie + Bar | Videos by platform, Views by platform | `GET /analytics/platforms` |

**Acceptance Criteria:**
- [ ] Tất cả charts render đúng với data từ VCreator API
- [ ] Charts responsive (1 cột mobile → 2-3 cột desktop)
- [ ] Chart colors adapt theo theme (light/dark)
- [ ] Timeline chart có toggle buttons cho từng metric

---

### FR-003: Analytics Dashboard — Filter System

**Priority:** Must Have

**Description:**
Hệ thống filter cho phép lọc data theo event, thời gian, creator.

**Filter Components:**

| Filter | Type | Options | Behavior |
|--------|------|---------|----------|
| **Event** | Multi-select | Events active từ VCreator | Empty = tất cả events |
| **Period** | Select | 7 ngày, 30 ngày, 90 ngày, Tùy chỉnh | Auto-update date range |
| **Date Range** | Date picker | Ngày bắt đầu / kết thúc | Chỉ enable khi period = Tùy chỉnh |
| **Creator** | Multi-select | Danh sách creators | Chỉ hiện ở tab Creator |

**Filter Workflow:**
```
User chọn filters → Hiện badge "Chưa áp dụng"
  → Click "Áp dụng" → URL update (?events=x&period=30d&start=...&end=...)
  → Data refetch
  → Click "Đặt lại" → Revert về filter đã áp dụng trước
```

**Acceptance Criteria:**
- [ ] Filters persist trong URL query params
- [ ] Validation: ngày bắt đầu < ngày kết thúc, events tồn tại
- [ ] Filter badge hiển thị khi có thay đổi chưa áp dụng
- [ ] Apply button disabled khi validation fail
- [ ] Khi load trang có URL params → auto-apply filters

---

### FR-004: Analytics Dashboard — Tab Creator

**Priority:** Must Have

**Description:**
Tab Creator hiển thị KPIs và bảng xếp hạng creators.

**Content:**
1. **Creator KPI Cards** (4 cards):
   - Tổng creators
   - Creators mới
   - Tỷ lệ hoạt động (active rate)
   - Tỷ lệ rời bỏ (churn rate)

2. **Creator Table** (bảng xếp hạng):
   - Columns: Hạng, Tên, Số nội dung, Lượt xem, Chi trả
   - Sortable by Lượt xem (mặc định)
   - Paginated (10 items/page ban đầu, rồi 100)
   - Filter theo creator khi chọn ở filter bar

**Acceptance Criteria:**
- [ ] 4 KPI cards hiển thị đúng
- [ ] Bảng sortable và paginated
- [ ] Click vào creator có thể filter dashboard theo creator đó
- [ ] Endpoint: `GET /analytics/creators`

---

### FR-005: Analytics Dashboard — Global Platform Overview

**Priority:** Should Have

**Description:**
Section hiển thị tổng quan metrics toàn platform, không phụ thuộc filter. Luôn hiển thị ở trên cùng.

**Content:**
- Bảng tổng hợp event portfolio (tên event, KPIs mỗi event)
- Click vào event → tự động chọn event đó trong filter và scroll xuống

**Acceptance Criteria:**
- [ ] Global overview luôn visible bất kể filter state
- [ ] Click event → filter apply + smooth scroll
- [ ] Endpoint: `GET /analytics/global/dashboard`

---

### FR-006: Xuất dữ liệu (Exports)

**Priority:** Must Have

**Description:**
Trang quản lý export jobs — liệt kê, theo dõi trạng thái, download file.

**Export Table Columns:**

| Column | Nội dung | Behavior |
|--------|----------|----------|
| Tên | Tên export job | Bold text |
| Loại | Loại dữ liệu export | Translated |
| Trạng thái | Badge màu | Chờ (xám), Đang xử lý (xanh dương + spinner), Hoàn thành (xanh lá), Thất bại (đỏ) |
| Người tạo | Tên user | From createdBy |
| Ngày tạo | `dd/MM/yyyy HH:mm` | Formatted |
| Hành động | Nút tải xuống | Chỉ enable khi Hoàn thành |

**Auto-Polling:**
- Khi có job đang Chờ hoặc Đang xử lý → auto-poll mỗi 5 giây
- Dừng poll khi tất cả jobs Hoàn thành hoặc Thất bại

**Download Flow:**
1. Click "Tải xuống"
2. Gọi `GET /data-exports/{id}/pre-sign` lấy pre-signed URL
3. Mở URL trong tab mới → browser auto-download
4. Hiện error toast nếu thất bại

**Acceptance Criteria:**
- [ ] Liệt kê export jobs với pagination (20 items/page)
- [ ] Status badges đúng màu và icon
- [ ] Auto-poll hoạt động đúng (start/stop)
- [ ] Download qua pre-signed URL thành công
- [ ] Hiện tooltip lý do khi job thất bại

---

### FR-007: Authentication (Clone OAuth2 Code Flow)

**Priority:** Must Have

**Description:**
Giữ nguyên cơ chế auth của TCB Dashboard: OAuth2 authorization code flow. Admin VCreator dẫn link sang dashboard kèm `?code=xxx`, dashboard đổi code lấy JWT token.

**Auth Flow VCreator (giống TCB):**
```
1. User đăng nhập vào VCreator Admin (UMI)
2. Admin có link/button mở Dashboard → redirect kèm ?code=xxx
3. Dashboard nhận code → gọi backend đổi code lấy JWT token
4. Token lưu localStorage
5. Mọi API request gắn Authorization: Bearer {token}
6. Response 401 → clear token → redirect về Admin login
```

**Acceptance Criteria:**
- [ ] Dashboard nhận `?code=xxx` từ URL → đổi code lấy token thành công
- [ ] Token lưu trong localStorage
- [ ] Không có token + không có code → redirect về VCreator Admin
- [ ] Auto-redirect khi token hết hạn (401)
- [ ] Logout clear token + redirect về VCreator Admin

**Thay đổi so với TCB:**
- Đổi API endpoint đổi code → VCreator backend
- Đổi redirect URL khi chưa auth → VCreator Admin URL (thay vì `/login`)

---

### FR-008: Sidebar Navigation (Modified)

**Priority:** Must Have

**Description:**
Sidebar chỉ giữ lại 2 menu chính + chức năng phụ trợ.

**Navigation Items:**

| Item | Icon | Route | Status |
|------|------|-------|--------|
| Analytics | BarChart2 | `/analytics` | Active |
| Xuất dữ liệu | FileDown | `/exports` | Active |
| --- separator --- | | | |
| Quay về Admin | ExternalLink | VCreator Admin URL | Link ngoài |
| Theme toggle | Sun/Moon | N/A | Toggle |
| Đăng xuất | LogOut | Redirect về VCreator Admin | Confirm dialog |

**Acceptance Criteria:**
- [ ] Chỉ hiển thị 2 menu chính + phụ trợ
- [ ] Active state highlighting đúng route
- [ ] Sidebar collapsible
- [ ] Link "Quay về Admin" mở đúng URL admin VCreator
- [ ] Logout có confirm dialog

---

### FR-009: Đa ngôn ngữ — Ẩn, mặc định tiếng Việt

**Priority:** Should Have

**Description:**
Giữ nguyên infrastructure `next-intl` nhưng ẩn language toggle. Mặc định locale = `vi`. Code vẫn support `en` để dễ mở lại sau.

**Thay đổi:**
- Default locale: `vi`
- Ẩn language toggle button trong sidebar
- Redirect `/` → `/vi/analytics` (không phải `/en/`)
- i18n message files: update nội dung tiếng Việt cho VCreator domain

**Acceptance Criteria:**
- [ ] Trang mặc định tiếng Việt
- [ ] Không hiển thị nút chuyển ngôn ngữ
- [ ] URL luôn có prefix `/vi/`
- [ ] Code vẫn hỗ trợ `en` locale (test bằng manual URL change)

---

## 6. Non-Functional Requirements

### NFR-001: API Compatibility

**Priority:** Must Have

**Description:**
Dashboard phải gọi đúng VCreator backend APIs. Cần mapping table và adapter layer.

**API Mapping (TCB → VCreator):**

| Feature | TCB Endpoint | VCreator Endpoint | Ghi chú |
|---------|-------------|-------------------|---------|
| Dashboard KPIs | `GET /analytics/dashboard` | `GET /analytics/dashboard` | Cần VCreator implement |
| Platform data | `GET /analytics/platforms` | `GET /analytics/platforms` | Cần VCreator implement |
| Approval data | `GET /analytics/approval` | `GET /analytics/approval` | Cần VCreator implement |
| Creator segments | `GET /analytics/creators/segments` | `GET /analytics/creators/segments` | Cần VCreator implement |
| Creator list | `GET /analytics/creators` | `GET /analytics/creators` | Cần VCreator implement |
| Timeline trends | `GET /analytics/trends` | `GET /analytics/trends` | Cần VCreator implement |
| Campaign stats | `GET /analytics/campaigns` | `GET /analytics/events` | Rename campaigns → events |
| Global dashboard | `GET /analytics/global/dashboard` | `GET /analytics/global/dashboard` | Cần VCreator implement |
| Events list | `GET /events` | `GET /events` | VCreator đã có |
| Export list | `GET /data-exports` | `GET /data-exports` | Cần VCreator implement |
| Export presign | `GET /data-exports/{id}/pre-sign` | `GET /data-exports/{id}/pre-sign` | Cần VCreator implement |
| Login | `POST /auth/login` | `POST /auth/login` | VCreator auth |

**Acceptance Criteria:**
- [ ] Tất cả API calls sử dụng VCreator base URL
- [ ] Response format tương thích: `{ code, data, message }`
- [ ] Error handling cho 401, 403, 500
- [ ] Retry strategy: 3 retries với exponential backoff

**Backend dependency:**
> VCreator backend cần implement analytics APIs. Nếu chưa có, dashboard hiển thị empty state với message "Chưa có dữ liệu".

---

### NFR-002: Branding

**Priority:** Must Have

**Description:**
Rebrand toàn bộ từ T-Fluencers sang VCreator.

**Thay đổi:**
- Logo: VCreator logo thay T-Fluencers
- Title: "VCreator Dashboard" thay "T-Fluencers Dashboard"
- Favicon: VCreator favicon
- Color scheme: Giữ nguyên hoặc adapt theo VCreator brand (nếu có brand guide)
- OG meta tags: VCreator

**Acceptance Criteria:**
- [ ] Không còn mention "T-Fluencers" hay "Techcombank" trong UI
- [ ] Logo hiển thị đúng trong sidebar
- [ ] Browser tab title: "VCreator Dashboard"

---

### NFR-003: Performance

**Priority:** Should Have

**Description:**
Dashboard phải load nhanh và responsive.

**Acceptance Criteria:**
- [ ] First Contentful Paint < 1.5s
- [ ] Time to Interactive < 3s
- [ ] React Query cache: staleTime 5 phút cho analytics, 10 phút cho filter dropdowns
- [ ] Charts render trong < 500ms sau khi có data

---

### NFR-004: Responsive Design

**Priority:** Should Have

**Description:**
Dashboard hoạt động tốt trên desktop và tablet.

**Acceptance Criteria:**
- [ ] Desktop (>1024px): Full layout, sidebar expanded
- [ ] Tablet (768-1024px): Sidebar collapsible, grid 2 columns
- [ ] Mobile (<768px): Sidebar overlay, grid 1 column

---

## 7. Epics

### EPIC-001: Project Setup & Branding

**Description:** Clone TCB dashboard, cleanup routes không cần, rebrand sang VCreator.

**Functional Requirements:** FR-008 (Sidebar), FR-009 (i18n)

**Tasks:**
1. Clone `techcombank/dashboard` → `vcreator/dashboard`
2. Xóa routes: profiles, campaigns, contents, performance, settings, accept-invite, forgot-password, reset-password
3. Xóa components liên quan đến routes đã xóa
4. Update branding (logo, title, favicon, meta)
5. Update sidebar navigation
6. Ẩn language toggle, default vi
7. Update i18n messages cho VCreator context

**Story Count Estimate:** 3

**Priority:** Must Have

---

### EPIC-002: Auth Adaptation (Code Flow)

**Description:** Adapt auth module — giữ nguyên cơ chế OAuth2 code flow, đổi endpoints sang VCreator backend.

**Functional Requirements:** FR-007

**Tasks:**
1. Update `lib/auth.ts` — đổi endpoint đổi code lấy token sang VCreator backend
2. Update `lib/api.ts` — đổi base URL
3. Xóa login page (`/login`) — chỉ dùng code flow từ Admin
4. Update `providers.tsx` — AuthInit redirect về VCreator Admin khi chưa auth
5. Xóa accept-invite, forgot/reset password routes
6. Config `ADMIN_URL` env var trỏ về VCreator Admin

**Story Count Estimate:** 2

**Priority:** Must Have

---

### EPIC-003: Analytics Dashboard Adaptation

**Description:** Adapt analytics dashboard cho VCreator data.

**Functional Requirements:** FR-001, FR-002, FR-003, FR-004, FR-005

**Tasks:**
1. Update TypeScript types/interfaces cho VCreator data models
2. Update analytics hooks — đổi endpoints, response parsing
3. Adapt KPI Grid — rename labels, adjust formats
4. Adapt charts — update data mapping
5. Adapt filter bar — events thay campaigns, VCreator creators
6. Adapt Creator tab — VCreator creator data model
7. Update Global Platform Overview
8. Update i18n messages (vi) cho tất cả analytics labels

**Story Count Estimate:** 5

**Priority:** Must Have

---

### EPIC-004: Exports Adaptation

**Description:** Adapt exports page cho VCreator backend.

**Functional Requirements:** FR-006

**Tasks:**
1. Update export hooks — đổi API endpoints
2. Update export types nếu VCreator có export types khác
3. Update i18n messages cho export labels
4. Test auto-polling + download flow

**Story Count Estimate:** 2

**Priority:** Must Have

---

## 8. Traceability Matrix

| Epic | FRs | NFRs | Story Est. | Priority |
|------|-----|------|------------|----------|
| EPIC-001: Project Setup & Branding | FR-008, FR-009 | NFR-002 | 3 | Must |
| EPIC-002: Auth Adaptation | FR-007 | NFR-001 | 2 | Must |
| EPIC-003: Analytics Adaptation | FR-001→005 | NFR-001, NFR-003, NFR-004 | 5 | Must |
| EPIC-004: Exports Adaptation | FR-006 | NFR-001 | 2 | Must |
| **Total** | **9 FRs** | **4 NFRs** | **~12 stories** | |

---

## 9. Prioritization Summary

| Priority | FRs | NFRs | Total |
|----------|-----|------|-------|
| Must Have | 8 (FR-001→008) | 2 (NFR-001, 002) | 10 |
| Should Have | 1 (FR-009) | 2 (NFR-003, 004) | 3 |
| Could Have | 0 | 0 | 0 |

---

## 10. Implementation Strategy

### Phase 1: Foundation (Week 1)
```
EPIC-001 (Setup + Branding) + EPIC-002 (Auth Adaptation)
→ Dashboard chạy được, auth code flow từ Admin hoạt động, sidebar đúng, branding đúng
→ Hiển thị empty states cho analytics/exports (chưa có API)
```

### Phase 2: Core Features (Week 2)
```
EPIC-003 (Analytics) + EPIC-004 (Exports)
→ Analytics dashboard hiển thị data từ VCreator
→ Exports hoạt động với VCreator backend
→ Tất cả filters, charts, KPIs hoạt động
```

### Backend Dependency
```
VCreator backend cần implement các analytics APIs (xem NFR-001).
Frontend và backend có thể phát triển song song:
- Frontend: mock data hoặc stub APIs
- Backend: implement endpoints theo contract trong PRD
```

---

## 11. Dependencies

**Internal:**
- VCreator backend (`accesstrade-projects/vcreator`) — cần implement analytics + exports APIs
- VCreator admin — cần link URL cho "Quay về Admin"

**External:**
- Không có — reuse toàn bộ từ TCB dashboard codebase

---

## 12. Assumptions

1. VCreator backend sẽ implement analytics APIs với response format tương tự TCB (`{ code, data, message }`)
2. VCreator backend đã có `/events` API (confirmed từ codebase exploration)
3. VCreator dùng OAuth2 code flow giống TCB — Admin dẫn link `?code=xxx` sang dashboard
4. Admin UMI vẫn là nơi quản lý events, contents, users — dashboard chỉ phục vụ analytics view
5. Branding VCreator sử dụng logo/colors hiện tại (không cần brand guide mới)
6. Export types VCreator tương tự hoặc subset của TCB export types

---

## 13. Out of Scope

### Routes TCB loại bỏ (không clone sang VCreator)

| Route TCB | Lý do |
|-----------|-------|
| `/profiles` + `/profiles/[id]` | VCreator quản lý user/creator trong admin UMI |
| `/campaigns` + sub-routes | VCreator quản lý events trong admin UMI |
| `/contents` + `/contents/[id]` | VCreator quản lý content trong admin UMI |
| `/performance` | VCreator crawl tự động, không cần CSV import thủ công |
| `/settings` | Auth qua code flow từ Admin, không cần change password |
| `/login` | Auth qua code flow từ Admin, không cần login page riêng |
| `/accept-invite` | TCB-specific flow |
| `/forgot-password` | Auth qua Admin, không cần |
| `/reset-password` | Auth qua Admin, không cần |

### Features TCB loại bỏ

- AT Core scoring / demographics card
- Campaign matching algorithm + matching history
- Content LLM summary / transcript scoring
- Influencer review & rating system
- Payment KPI widget
- Performance CSV import + batch management
- `x-device-id` header mechanism
- TCB feature flags (`NEXT_PUBLIC_FEATURE_CAMPAIGNS`)

### Chức năng tương lai (không nằm trong PRD này)

- Withdrawal dashboard tab
- Social account management (link/unlink TikTok, FB, IG, Threads)
- Creator onboarding wizard
- Notifications / real-time updates
- Creator self-registration flow

---

## 14. Files được Clone & Hành Động

### Giữ nguyên (không sửa hoặc sửa rất ít)

| File/Folder | Lý do |
|-------------|-------|
| `src/components/ui/*` | Radix UI primitives — reuse 100% |
| `src/components/charts/*` | Chart components — chỉ đổi data |
| `src/components/widgets/*` | KPI cards — đổi labels |
| `src/components/filters/filter-bar.tsx` | Filter container — giữ nguyên |
| `src/components/filters/date-range.tsx` | Date picker — giữ nguyên |
| `src/components/filters/period-select.tsx` | Period select — giữ nguyên |
| `src/components/layout/app-shell.tsx` | Layout wrapper — giữ nguyên |
| `src/components/providers.tsx` | Provider wrapper — sửa AuthInit |
| `src/lib/format.ts` | Number/date formatting — giữ nguyên |
| `src/lib/utils.ts` | Utilities — giữ nguyên |
| `next.config.ts` | Next.js config — giữ nguyên |
| `tailwind.config.ts` | Tailwind config — giữ nguyên |
| `tsconfig.json` | TypeScript config — giữ nguyên |

### Sửa đổi

| File | Thay đổi |
|------|----------|
| `src/components/layout/sidebar.tsx` | Chỉ giữ 2 menu, ẩn language toggle, thêm link Admin |
| `src/lib/auth.ts` | Đổi endpoint exchange code, redirect URL về VCreator Admin |
| `src/lib/api.ts` | Đổi base URL |
| `src/hooks/use-analytics.ts` | Đổi endpoints, response parsing |
| `src/hooks/use-exports.ts` | Đổi endpoints |
| `src/hooks/use-filters.ts` | Rename campaign → event terminology |
| `src/app/[locale]/analytics/page.tsx` | Adapt KPIs, labels |
| `src/app/[locale]/exports/page.tsx` | Đổi API calls |
| `src/messages/vi/*.json` | Update labels cho VCreator domain |
| `src/messages/en/*.json` | Update labels (giữ cho future use) |
| `.env` | Đổi API_URL, ADMIN_URL |
| `package.json` | Đổi name, description |
| `public/logo.svg` | VCreator logo |

---

## 15. Risk & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| VCreator backend chưa có analytics APIs | **Cao** | Frontend dùng mock data/stub APIs. Backend implement theo contract PRD. Phát triển song song. |
| Response format khác giữa TCB và VCreator | **Trung bình** | Tạo adapter layer trong hooks. Không sửa components, chỉ sửa data transformation. |
| Auth flow cần adapt | **Thấp** | Giữ nguyên cơ chế code flow, chỉ đổi endpoint + redirect URL. |
| Cleanup không sạch — import lỗi sau khi xóa files | **Thấp** | Chạy `tsc --noEmit` sau mỗi bước xóa. Fix broken imports ngay. |
| i18n keys conflict khi rename | **Thấp** | Dùng find-replace toàn bộ. Test từng page sau khi update. |

---

## Appendix A: VCreator Backend API Contract

Backend VCreator cần implement các endpoints sau với response format `{ code: number, data: T, message: string }`:

```
# Analytics
GET /analytics/dashboard?events=id1,id2&startDate=YYYY-MM-DD&endDate=YYYY-MM-DD
GET /analytics/platforms?events=id1,id2&startDate=&endDate=&withMetrics=true
GET /analytics/approval?events=id1,id2&startDate=&endDate=
GET /analytics/creators/segments?events=id1,id2&startDate=&endDate=
GET /analytics/creators?events=&startDate=&endDate=&page=1&limit=10&sortBy=views&sortOrder=desc
GET /analytics/trends?events=&startDate=&endDate=
GET /analytics/events?events=&startDate=&endDate=
GET /analytics/global/dashboard

# Events (đã có)
GET /events?status=active&limit=100

# Exports
GET /data-exports?filterByOwner=true&page=0&limit=20
GET /data-exports/:id
GET /data-exports/:id/pre-sign

# Auth (code flow từ Admin)
POST /auth/exchange-code  { code } → { token }
```

---

## Appendix B: Terminology Mapping

| TCB Term | VCreator Term | Context |
|----------|-------------|---------|
| Campaign | Event | Đơn vị campaign/event chính |
| T-Fluencers | VCreator | Brand name |
| Influencer | Creator | Người tạo nội dung |
| Profile | User/Creator | Thông tin người dùng |
| Staff | Admin/Staff | Người quản lý |

---

*Generated by BMAD Method v6 - Product Manager*
*Date: 2026-04-01*
