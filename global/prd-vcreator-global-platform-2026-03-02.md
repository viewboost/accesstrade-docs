# PRD: VCreator Global Platform

**Version:** 1.0
**Date:** 2026-03-02
**Author:** Product Manager (BMAD Method)
**Status:** Draft
**Project Level:** Level 4 (Enterprise-scale, 30+ stories)
**Related:** [Brainstorming Session](.../../.bmad/brainstorming-vcreator-global-2026-03-02.md) | [Bandung Plan](bandung/Plan.html) | [Bandung QnA](bandung/QnA.html)

---

## 1. Executive Summary

Dự án VCreator Global Platform mở rộng nền tảng KOC (Key Opinion Creator) management hiện tại — đang vận hành tại Việt Nam — thành một **Global Core Platform** hỗ trợ đa quốc gia, đa ngôn ngữ, đa tiền tệ. Bắt đầu với Philippines, sau đó tích hợp Indonesia và các thị trường khác (CIS, EU).

Hệ thống hiện tại (codebase `ambassabor`) gồm Go backend, React frontend, React admin panel, MongoDB, Redis, MinIO — đã chạy production với 11 partner brands. Dự án này sẽ refactor toàn bộ hệ thống sang kiến trúc **Country Pod** với data isolation, role-based access theo quốc gia, và compliance riêng cho từng thị trường.

---

## 2. Business Objectives

| # | Objective | Success Metric |
|---|-----------|---------------|
| BO-1 | Mở rộng nền tảng VCreator sang đa quốc gia, bắt đầu Philippines → Indonesia → CIS/EU | Philippines go-live trong 6 tháng, Indonesia trong 9 tháng |
| BO-2 | Xây dựng Global Core Platform tái sử dụng được, giảm effort setup mỗi country mới | Setup country mới < 2 tuần (sau Philippines) |
| BO-3 | Đảm bảo compliance (KYC, thuế, privacy) theo luật từng quốc gia | 100% compliance cho mỗi country trước go-live |

---

## 3. User Personas

### P1: Creator/KOC (End User)
- **Mô tả:** Content creator tham gia chiến dịch marketing cho brands
- **Quốc gia:** VN (hiện tại), Philippines, Indonesia (mở rộng)
- **Nhu cầu:** Tham gia campaign, submit content, nhận hoa hồng theo tiền tệ local
- **Pain points:** Giao diện không đúng ngôn ngữ, quy trình KYC phức tạp, không rõ thu nhập thực tế

### P2: Local Admin
- **Mô tả:** Nhân viên vận hành tại từng quốc gia
- **Vai trò:** Campaign management, content moderation, KYC review, reconciliation, payment
- **Nhu cầu:** Chỉ xem data của nước mình, báo cáo theo tiền tệ local
- **Pain points:** Không có tool phù hợp cho thị trường local, phải dùng spreadsheet

### P3: Global Admin
- **Mô tả:** Quản lý cấp cao xem tổng hợp đa quốc gia
- **Vai trò:** Dashboard tổng, "acting as local" khi cần, audit oversight
- **Nhu cầu:** Xem data cross-country, so sánh performance, intervention khi cần
- **Pain points:** Không có góc nhìn tổng thể, khó tracking across countries

### P4: Local Vendor/Operations
- **Mô tả:** Đối tác vận hành tại quốc gia mới
- **Nhu cầu:** Được training để vận hành platform, moderate content, onboard creators
- **Pain points:** Không quen platform, cần tài liệu bằng ngôn ngữ local

---

## 4. Key User Flows

### Flow 1: Creator tham gia campaign đa quốc gia
```
Truy cập Global Platform → Chọn quốc gia → Chọn ngôn ngữ → Đăng nhập TikTok/Google
→ Điền thông tin cá nhân & KYC → Truy cập chiến dịch → Nhận mã hashtag cá nhân
→ Nộp tác phẩm → Nhận hoa hồng (tiền tệ local)
```

### Flow 2: Local Admin vận hành campaign
```
Đăng nhập admin site (local scope) → Tạo campaign → Kiểm duyệt nội dung
→ Review KYC users → Xem báo cáo → Đối soát → Thanh toán
```

### Flow 3: Global Admin oversight
```
Đăng nhập admin (global scope) → Xem dashboard tổng hợp (USD)
→ So sánh cross-country → "Acting as local" (nếu cần, có audit)
→ Xem audit trail → Broadcast thông báo tới Local Admins
```

---

## 5. Functional Requirements

### 5.1 MULTI-TENANCY & DATA ISOLATION

#### FR-001: Country-Based Data Partitioning
**Priority:** Must Have

**Description:**
Hệ thống phải phân tách data theo quốc gia bằng `country_code` field trên tất cả MongoDB collections. Mỗi record phải gắn với 1 quốc gia cụ thể. Queries mặc định phải filter theo country context của user/admin đang đăng nhập.

**Acceptance Criteria:**
- [ ] Tất cả collections có field `country_code` (indexed)
- [ ] API middleware tự động inject country filter vào queries
- [ ] Local Admin chỉ query được data có `country_code` matching scope của mình
- [ ] Global Admin có thể query cross-country hoặc filter theo specific country
- [ ] Không có data leak giữa countries trong bất kỳ API endpoint nào

**Dependencies:** None (foundation requirement)

---

#### FR-002: Country Configuration Store
**Priority:** Must Have

**Description:**
Hệ thống cần một Country Configuration service lưu trữ và quản lý cấu hình riêng cho từng quốc gia: tiền tệ, ngôn ngữ hỗ trợ, thuế suất, quy định KYC, payment method, OAuth providers, social platforms.

**Acceptance Criteria:**
- [ ] CRUD API cho country configuration (Global Admin only)
- [ ] Mỗi country có: `code`, `name`, `currency`, `languages[]`, `tax_rules`, `kyc_requirements`, `payment_config`, `oauth_providers[]`, `social_platforms[]`
- [ ] Config được cache (Redis) để giảm DB reads
- [ ] Thay đổi config có audit log
- [ ] Feature flags per country để bật/tắt tính năng

**Dependencies:** None

---

#### FR-003: URL Routing theo Country Code
**Priority:** Must Have

**Description:**
URL sử dụng country code viết tắt (2 ký tự: `vn`, `ph`, `th`, `id`...) trong path, không dùng full country name. Platform phải có landing page cho phép user chọn quốc gia.

**Acceptance Criteria:**
- [ ] URL format: `/{country_code}/...` (vd: `/ph/campaign/123`)
- [ ] Country selector page tại root URL `/`
- [ ] Redirect user đến đúng country path sau khi chọn
- [ ] Country code validation (chỉ accept configured countries)
- [ ] 404 cho invalid country codes

**Dependencies:** FR-002

---

#### FR-004: Cross-Country Data Aggregation
**Priority:** Must Have

**Description:**
Global Admin cần xem báo cáo tổng hợp data từ nhiều quốc gia. Tất cả số liệu tổng hợp phải convert sang USD để so sánh.

**Acceptance Criteria:**
- [ ] Aggregation API cho: total creators, total campaigns, total revenue (USD), total content per country
- [ ] Dashboard hiển thị tổng hợp + breakdown theo country
- [ ] Currency conversion dùng exchange rate từ FR-020
- [ ] Filter theo date range, country, campaign type
- [ ] Export báo cáo tổng hợp (Excel, PDF)

**Dependencies:** FR-002, FR-020

---

### 5.2 AUTHENTICATION & USER MANAGEMENT

#### FR-005: Multi-Provider OAuth với Feature Flag per Country
**Priority:** Must Have

**Description:**
Hệ thống hỗ trợ đăng nhập qua TikTok, Google (Phase 1), Facebook (Phase 2). Mỗi quốc gia có thể bật/tắt provider qua feature flag. OAuth credentials quản lý riêng per country.

**Acceptance Criteria:**
- [ ] TikTok OAuth login (đã có, cần refactor cho multi-country)
- [ ] Google OAuth login (đã có, cần refactor cho multi-country)
- [ ] Facebook OAuth login (Phase 2)
- [ ] Feature flag bật/tắt provider per country (từ Country Config)
- [ ] OAuth credentials (client_id, client_secret) quản lý per country
- [ ] Login UI chỉ hiển thị providers đang active cho country đó

**Dependencies:** FR-002

---

#### FR-006: User Country Binding & Multi-Country Profile
**Priority:** Must Have

**Description:**
User chọn quốc gia khi đăng ký → bind với quốc gia đó. 1 user có thể tham gia nhiều quốc gia nhưng mỗi nơi có profile riêng (KYC, bank, tax riêng). User phải sử dụng tài khoản bank, KYC, MST theo luật quốc gia đã chọn.

**Acceptance Criteria:**
- [ ] User chọn country khi đăng ký lần đầu
- [ ] Profile data (KYC, bank, tax) gắn với specific country
- [ ] User có thể thêm profile cho country khác (separate flow)
- [ ] Hashtag cá nhân riêng cho mỗi country
- [ ] Hoa hồng tính và trả theo tiền tệ của country đã chọn

**Dependencies:** FR-001, FR-002

---

#### FR-007: Role & Permission System — Country-Scoped
**Priority:** Must Have

**Description:**
Hệ thống phân quyền phân theo quốc gia VÀ position (admin/accountant/operations). Local Admin chỉ thao tác được trên data nước mình. Global Admin có quyền mở rộng nhưng bắt buộc audit.

**Acceptance Criteria:**
- [ ] Roles: `global_admin`, `local_admin`, `local_accountant`, `local_operations`
- [ ] Mỗi role gắn với `country_code` scope (trừ global_admin)
- [ ] Permission check tại mọi API endpoint: verify role + country scope
- [ ] Local Admin: CRUD campaign, content moderation, KYC review, reconciliation, payment — CHỈ trong country scope
- [ ] Global Admin: xem tổng hợp + "acting as local" (xem FR-012)
- [ ] Local Admin KHÔNG thể xem data nước khác
- [ ] Role assignment CRUD (Global Admin only)

**Dependencies:** FR-001, FR-002

---

### 5.3 INTERNATIONALIZATION (i18n)

#### FR-008: Backend Multi-Language Support
**Priority:** Must Have

**Description:**
Backend API phải trả response (error messages, labels, notification text) theo ngôn ngữ được request. Mỗi quốc gia luôn có 2 ngôn ngữ: ngôn ngữ Local + English.

**Acceptance Criteria:**
- [ ] Accept-Language header hoặc user preference xác định ngôn ngữ
- [ ] Error messages đa ngôn ngữ (hiện có 17 locale dirs, cần audit + hoàn thiện)
- [ ] API response bao gồm translated labels khi cần
- [ ] Fallback: local language → English → default
- [ ] Locale files cho: Vietnamese, English, Filipino/Tagalog, Indonesian (Phase 1)

**Dependencies:** FR-002

---

#### FR-009: Frontend Language Switcher
**Priority:** Must Have

**Description:**
UI có language switcher rõ ràng cho phép user/admin chọn giữa ngôn ngữ Local và English. Preference lưu theo user/session.

**Acceptance Criteria:**
- [ ] Language switch UI trên header/navigation
- [ ] Hỗ trợ 2 ngôn ngữ per country: Local + English
- [ ] Preference lưu trong user profile (logged-in) hoặc session (guest)
- [ ] Toàn bộ UI labels, buttons, messages chuyển ngôn ngữ
- [ ] T&C, campaign content, KV thay đổi theo language

**Dependencies:** FR-008

---

#### FR-010: Content Management Đa Ngôn Ngữ (Admin Nhập)
**Priority:** Must Have

**Description:**
Admin panel hỗ trợ nhập content (T&C, campaign description, notifications, articles) theo nhiều ngôn ngữ. Mỗi content item có version cho mỗi ngôn ngữ của country đó.

**Acceptance Criteria:**
- [ ] Content editor có tab/switch cho mỗi ngôn ngữ
- [ ] Mỗi content item lưu: `{ language_code: content_body }` per version
- [ ] Preview content theo từng ngôn ngữ
- [ ] Validation: bắt buộc nhập ít nhất 1 ngôn ngữ (local hoặc EN)
- [ ] Warning nếu content chưa có bản dịch cho ngôn ngữ nào đó

**Dependencies:** FR-008, FR-009

---

#### FR-011: Auto-Language Detection & Fallback
**Priority:** Should Have (Phase 2)

**Description:**
Nếu user truy cập country khác quốc gia của mình → auto switch sang English. Thứ tự ưu tiên: (1) user manual choice, (2) market default language, (3) cross-market fallback English.

**Acceptance Criteria:**
- [ ] Detect user country: từ KYC info / IP geolocation / user setting
- [ ] So sánh user country vs URL country → nếu khác → suggest English
- [ ] User vẫn có thể manual override
- [ ] Priority chain: manual > market default > fallback EN
- [ ] Không force-change đã-saved preference

**Dependencies:** FR-009

---

### 5.4 ADMIN SYSTEM

#### FR-012: Global Admin "Acting as Local" Mode
**Priority:** Must Have

**Description:**
Global Admin có thể switch sang scope của một Local cụ thể để thao tác như Local Admin. BẮT BUỘC audit: actor, local scope, reason, thời gian, mọi hành động đã thực hiện. Tác vụ nhạy cảm (KYC access, payment) có thể yêu cầu approval.

**Acceptance Criteria:**
- [ ] UI cho Global Admin chọn "Act as [Country]"
- [ ] Session scope switch → tất cả actions filter theo country đã chọn
- [ ] Bắt buộc nhập reason khi activate mode
- [ ] Tất cả actions trong mode này ghi audit log: actor, scope, reason, timestamp, action
- [ ] Tác vụ nhạy cảm (access KYC/bank data) cần additional confirmation
- [ ] Có thể exit "Acting as Local" mode bất kỳ lúc nào
- [ ] Audit log viewer cho Global Admin review history

**Dependencies:** FR-007, FR-013

---

#### FR-013: Audit Trail System
**Priority:** Must Have

**Description:**
Lưu lịch sử "ai làm gì, lúc nào, ở đâu" cho tất cả thao tác quan trọng. Đặc biệt cho Global Admin acting as Local. Audit data phải searchable, filterable, exportable.

**Acceptance Criteria:**
- [ ] Log format: `{ actor, action, target, country_scope, timestamp, details, ip_address }`
- [ ] Auto-log cho: campaign CRUD, content moderation decisions, KYC approval/rejection, payment execution, role changes, config changes, "acting as local" sessions
- [ ] Audit log viewer UI (searchable, filterable by actor/action/country/date)
- [ ] Export audit logs (CSV, Excel)
- [ ] Retention policy configurable (default: 2 years)
- [ ] Immutable records (không thể edit/delete audit entries)

**Dependencies:** FR-007

---

#### FR-014: Local Admin — Campaign & Content Operations
**Priority:** Must Have

**Description:**
Local Admin có đầy đủ công cụ để vận hành campaign tại country mình: tạo/sửa campaign, kiểm duyệt nội dung, xem báo cáo, quản lý users.

**Acceptance Criteria:**
- [ ] Campaign CRUD (chỉ trong country scope)
- [ ] Content moderation queue (chỉ content của country mình)
- [ ] User list + search (chỉ users thuộc country mình)
- [ ] KYC review workflow (approve/reject + reason)
- [ ] Reporting dashboard (tiền tệ local + USD tham chiếu)
- [ ] Notification settings cho users trong country

**Dependencies:** FR-001, FR-007

---

#### FR-015: Local Admin — Reconciliation & Payment
**Priority:** Must Have

**Description:**
Local Admin thực hiện đối soát và thanh toán cho creators theo đơn vị tiền tệ và luật thuế của quốc gia đó.

**Acceptance Criteria:**
- [ ] Reconciliation workflow: review → approve → execute payment
- [ ] Tính toán theo tiền tệ local
- [ ] Áp dụng tax rules của country (từ Country Config)
- [ ] Net income calculation: gross - income tax (KHÔNG tính exchange fee)
- [ ] Export reconciliation reports (Excel, PDF)
- [ ] Payment execution integration (FR-021)

**Dependencies:** FR-007, FR-019, FR-020

---

#### FR-016: Global Admin Dashboard — Cross-Country
**Priority:** Must Have

**Description:**
Dashboard cho Global Admin xem tổng hợp data từ tất cả countries, convert sang USD, so sánh performance across countries.

**Acceptance Criteria:**
- [ ] Overview: total creators, campaigns, revenue (USD) across all countries
- [ ] Revenue USD chia 2 phần rõ ràng:
  - **Confirmed:** Dùng chốt rate từ reconciliation batches (FR-020B)
  - **Estimated:** Dùng realtime rate cho data chưa đối soát (FR-020)
  - Hiển thị: "Revenue: $125,000 confirmed + ~$23,000 estimated"
- [ ] Breakdown per country: creators, campaigns, revenue (confirmed + estimated), content count
- [ ] Comparison charts: country vs country performance
- [ ] Trend over time: growth per country
- [ ] Drill-down: click country → xem chi tiết (link sang Local Admin view)
- [ ] Sensitive data (KYC/bank) ẩn mặc định, phải click + log khi access

**Dependencies:** FR-004, FR-007, FR-020, FR-020B

---

#### FR-017: Global Admin → Local Admin Notifications
**Priority:** Should Have (Phase 2)

**Description:**
Global Admin có thể gửi thông báo tới Local Admin(s) theo country hoặc role. Phương thức: in-app notification và/hoặc email.

**Acceptance Criteria:**
- [ ] Compose notification: title, body, target (by country, by role, all)
- [ ] Delivery channels: in-app notification, email
- [ ] Notification history (sent, read status)
- [ ] Local Admin nhận và xem notifications trong admin panel
- [ ] Scheduled notifications (gửi theo thời gian hẹn)

**Dependencies:** FR-007

---

### 5.5 PAYMENT, CURRENCY & TAX

#### FR-018: Multi-Currency Display & Conversion
**Priority:** Must Have

**Description:**
Hệ thống hiển thị số tiền theo tiền tệ local (cho creators, Local Admin) và USD (cho Global Admin). Creator nhận hoa hồng theo tiền tệ local. Có 2 loại rate conversion rõ ràng: **realtime reference** (tham chiếu) và **reconciliation rate** (đã chốt).

**Acceptance Criteria:**
- [ ] Currency config per country (từ FR-002)
- [ ] Creator dashboard: hiển thị earnings bằng tiền tệ local + USD tham chiếu (realtime rate, label rõ)
- [ ] Local Admin: báo cáo bằng tiền tệ local + USD (realtime cho chưa đối soát, chốt rate cho đã đối soát)
- [ ] Global Admin: tổng hợp bằng USD — chia rõ "USD đã chốt" vs "USD ước tính"
- [ ] Format number theo locale (dấu phẩy, dấu chấm, symbol vị trí: ₱100 vs 100 ₫)
- [ ] UI phân biệt rõ ràng giữa "tỷ giá tham chiếu" và "tỷ giá đã chốt" (màu sắc/icon/label)

**Dependencies:** FR-002, FR-020, FR-020B

---

#### FR-019: Tax Calculation Engine per Country
**Priority:** Must Have

**Description:**
Hệ thống tính thuế theo quy định từng quốc gia. Công thức: Net income = Gross income - Income tax. KHÔNG tính exchange fee vào net income.

**Acceptance Criteria:**
- [ ] Tax rules configurable per country (tax rate, tax bands, withholding rules)
- [ ] Net income = gross - income tax (per country rules)
- [ ] Creator dashboard: hiển thị estimated net income
- [ ] Tax calculation transparent (hiển thị breakdown cho creator)
- [ ] Tax rules updatable bởi Global Admin (có audit log)

**Dependencies:** FR-002

---

#### FR-020: Exchange Rate — Realtime Reference Rate
**Priority:** Must Have

**Description:**
Hệ thống cung cấp tỷ giá tham chiếu realtime (USD ↔ local currency) để Creator và Admin xem tương đương USD. Đây là tỷ giá **informational**, KHÔNG dùng để thanh toán. Lấy từ bank authority local hoặc financial API, cập nhật liên tục.

**Acceptance Criteria:**
- [ ] API lấy realtime exchange rate từ data source (bank authority / financial API)
- [ ] Cache rate trong Redis với TTL configurable (default: 15 phút)
- [ ] Creator dashboard: hiển thị "Thu nhập ₱50,000 ≈ $890 (tỷ giá tham chiếu)"
- [ ] Label rõ ràng: "Tỷ giá tham chiếu — không dùng cho thanh toán"
- [ ] Local Admin dashboard: hiển thị cột USD tham chiếu bên cạnh tiền tệ local
- [ ] Global Admin dashboard: dùng realtime rate cho data CHƯA đối soát
- [ ] Rate refresh interval configurable per country (từ Country Config)
- [ ] Fallback: nếu API fail → dùng rate gần nhất + hiển thị timestamp "cập nhật lúc..."
- [ ] Rate history lưu lại (lịch sử tỷ giá theo ngày)

**Dependencies:** FR-002

---

#### FR-020B: Exchange Rate — Chốt Rate khi Đối soát (Reconciliation Rate)
**Priority:** Must Have

**Description:**
Khi Local Admin thực hiện đối soát (reconciliation), hệ thống **chốt tỷ giá tại thời điểm đó**. Rate này trở thành **immutable** cho toàn bộ batch đối soát — dùng để tính toán payment, convert sang USD cho báo cáo Global. Đây là tỷ giá **pháp lý**.

**Acceptance Criteria:**
- [ ] Khi Local Admin tạo reconciliation batch → hệ thống suggest rate hiện tại (từ FR-020)
- [ ] Local Admin có thể: (a) chấp nhận rate suggest, hoặc (b) nhập rate manual (với reason)
- [ ] Sau khi confirm → rate được **chốt (snapshot)** và gắn vào reconciliation batch
- [ ] Rate đã chốt: KHÔNG thể sửa đổi (immutable) — nếu sai phải tạo batch adjustment mới
- [ ] Tất cả payment trong batch dùng cùng 1 chốt rate
- [ ] Global Admin dashboard: dùng chốt rate cho data ĐÃ đối soát
- [ ] Reconciliation report hiển thị rõ: "Tỷ giá chốt: 1 USD = ₱56.2 (ngày 15/03/2026, chốt bởi admin@ph)"
- [ ] Audit log: ai chốt, lúc nào, rate bao nhiêu, rate source (realtime hay manual)
- [ ] History: danh sách tất cả reconciliation rates đã chốt (filterable by country, date range)

**Flow:**
```
Local Admin mở đối soát
  → Hệ thống hiển thị: "Tỷ giá hiện tại: 1 USD = ₱56.2 (cập nhật 10:30 AM)"
  → Admin chọn: [Dùng tỷ giá này] hoặc [Nhập tỷ giá khác]
  → Nếu nhập khác → bắt buộc nhập lý do
  → Confirm → Rate chốt → Gắn vào batch → Tất cả tính toán dùng rate này
  → Payment execute theo rate đã chốt
  → Không thể thay đổi sau khi confirm
```

**Dependencies:** FR-002, FR-020, FR-015

---

#### FR-021: Payment Gateway Abstraction per Country
**Priority:** Must Have

**Description:**
Abstraction layer cho payment integration. Mỗi country có payment gateway riêng. VN giữ nguyên hệ thống hiện tại. Philippines cần tích hợp vendor local mới.

**Acceptance Criteria:**
- [ ] Payment abstraction interface: `pay(creator_id, amount, currency, country)`
- [ ] VN: giữ payment flow hiện tại
- [ ] Philippines: tích hợp payment vendor local (GCash, bank transfer, etc.)
- [ ] Payment status tracking (pending, processing, completed, failed)
- [ ] Payment history per creator per country
- [ ] Retry mechanism cho failed payments

**Dependencies:** FR-002, FR-019

---

### 5.6 KYC & COMPLIANCE

#### FR-022: Country-Specific KYC Requirements
**Priority:** Must Have

**Description:**
Mỗi quốc gia có quy định KYC riêng. Hệ thống phải hỗ trợ custom KYC form fields, validation rules, document types per country.

**Acceptance Criteria:**
- [ ] KYC form configurable per country (required fields, document types)
- [ ] VN: CCCD/CMND, tax code (hiện tại)
- [ ] Philippines: valid government ID (cần research cụ thể)
- [ ] Upload & store KYC documents (encrypted, MinIO)
- [ ] KYC review workflow: pending → under_review → approved/rejected
- [ ] Local Admin review KYC (chỉ users của country mình)

**Dependencies:** FR-002, FR-006

---

#### FR-023: Bank Account Management per Country
**Priority:** Must Have

**Description:**
Bank list và validation rules khác nhau per country. Sensitive data (account number, etc.) phải encrypted.

**Acceptance Criteria:**
- [ ] Bank list configurable per country
- [ ] Account validation rules per country (format, length, etc.)
- [ ] Sensitive data encrypted at rest (AES-256)
- [ ] Bank info chỉ accessible bởi: owner (creator), Local Admin (khi review), Global Admin (khi "acting as local" + audit log)
- [ ] CRUD bank account per creator per country

**Dependencies:** FR-002, FR-006

---

#### FR-024: Tax ID / Registration per Country
**Priority:** Must Have

**Description:**
Tax registration format khác nhau per country. Validation rules apply theo country-specific format.

**Acceptance Criteria:**
- [ ] Tax ID format configurable per country
- [ ] VN: MST format (hiện tại)
- [ ] Philippines: TIN format
- [ ] Validation: format check, uniqueness check per country
- [ ] Tax ID stored securely (encrypted)

**Dependencies:** FR-002, FR-006

---

### 5.7 CAMPAIGN & CONTENT

#### FR-025: Country-Scoped Campaign Management
**Priority:** Must Have

**Description:**
Campaign gắn với quốc gia cụ thể. Creator tham gia campaign theo country đã chọn. Hashtag cá nhân riêng cho mỗi country.

**Acceptance Criteria:**
- [ ] Campaign gắn `country_code` (mandatory)
- [ ] Creator chỉ thấy campaigns của country mình
- [ ] Mỗi creator nhận hashtag cá nhân RIÊNG per country
- [ ] Campaign content (description, rules, T&C) theo ngôn ngữ (FR-010)
- [ ] Campaign analytics scoped by country

**Dependencies:** FR-001, FR-006, FR-010

---

#### FR-026: Content Moderation per Country
**Priority:** Must Have

**Description:**
Local Admin kiểm duyệt content của creators trong country mình. Moderation rules có thể khác nhau per country.

**Acceptance Criteria:**
- [ ] Moderation queue scoped by country
- [ ] Moderation actions: approve, reject (with reason), request revision
- [ ] Moderation rules configurable per country (optional)
- [ ] Content submission workflow: submitted → under_review → approved/rejected
- [ ] Moderation analytics (approval rate, avg review time per country)

**Dependencies:** FR-001, FR-007, FR-025

---

#### FR-027: Social Platform Coverage per Country
**Priority:** Must Have (core platforms), Should Have (additional platforms)

**Description:**
Social platforms (TikTok, Facebook, Instagram, Threads) đã tích hợp. Mỗi country có thể bật/tắt specific platforms qua Country Config.

**Acceptance Criteria:**
- [ ] Social platform list configurable per country (từ FR-002)
- [ ] TikTok: global (tất cả countries)
- [ ] Facebook, Instagram, Threads: global (tất cả countries)
- [ ] Country-specific platforms: configurable, pluggable
- [ ] Content submission validate: chỉ accept links từ enabled platforms

**Dependencies:** FR-002

---

### 5.8 INFRASTRUCTURE & OPERATIONS

#### FR-028: Feature Flag System per Country
**Priority:** Must Have

**Description:**
Feature flags cho phép bật/tắt tính năng per country. Dùng để rollout incremental, A/B testing, và disable features chưa sẵn sàng ở country mới.

**Acceptance Criteria:**
- [ ] Feature flag CRUD (Global Admin only)
- [ ] Flag scope: global, per-country
- [ ] Backend check: `isFeatureEnabled(feature_name, country_code)`
- [ ] Frontend check: flags available via API cho conditional rendering
- [ ] Flag states: enabled, disabled, percentage rollout
- [ ] Flag audit log

**Dependencies:** FR-002

---

#### FR-029: Database Migration — VN Data to Global Structure
**Priority:** Must Have (Phase 1 — scripts ready), Should Have (Phase 2/3 — execution)

**Description:**
Migration scripts để add `country_code = "vn"` vào tất cả existing VN data. Script phải idempotent, reversible, zero-downtime.

**Acceptance Criteria:**
- [ ] Migration scripts cho tất cả collections
- [ ] Add `country_code = "vn"` to all existing records
- [ ] Indexes cho `country_code` field
- [ ] Idempotent (chạy nhiều lần không sai)
- [ ] Reversible (rollback plan)
- [ ] Zero-downtime (background migration)
- [ ] Validation report (kiểm tra data integrity sau migration)

**Dependencies:** FR-001

---

#### FR-030: Philippines Country Pod Setup
**Priority:** Must Have (Phase 2)

**Description:**
Setup đầy đủ Country Pod cho Philippines: configuration, locale files, KYC integration, payment gateway, bank list, tax rules.

**Acceptance Criteria:**
- [ ] Philippines country config created (currency: PHP, languages: fil, en)
- [ ] Filipino/Tagalog + English locale files hoàn thiện
- [ ] Philippines KYC integration (government ID types)
- [ ] Philippines payment gateway integrated
- [ ] Philippines bank list + validation rules
- [ ] Philippines tax rules (withholding tax, etc.)
- [ ] UAT passed
- [ ] First campaign successfully onboarded

**Dependencies:** FR-002, FR-005, FR-008, FR-019, FR-021, FR-022, FR-023, FR-024

---

#### FR-031: Indonesia Country Pod Setup
**Priority:** Should Have (Phase 3)

**Description:**
Setup Country Pod cho Indonesia theo cùng pattern đã validate với Philippines.

**Acceptance Criteria:**
- [ ] Indonesia country config (currency: IDR, languages: id, en)
- [ ] Indonesian + English locale files
- [ ] Indonesia KYC integration
- [ ] Indonesia payment gateway integrated
- [ ] Indonesia bank list + validation rules
- [ ] Indonesia tax rules
- [ ] UAT passed

**Dependencies:** FR-030 (learnings), FR-002

---

#### FR-032: Facebook Login Integration
**Priority:** Should Have (Phase 2)

**Description:**
Thêm Facebook OAuth login, bật theo feature flag per country. Chuẩn bị phương án Meta app review.

**Acceptance Criteria:**
- [ ] Facebook OAuth integration
- [ ] Feature flag per country (FR-028)
- [ ] Meta app review preparation & submission
- [ ] Login UI hiển thị Facebook button khi enabled
- [ ] Account linking (Facebook ↔ existing user)

**Dependencies:** FR-005, FR-028

---

#### FR-033: Cross-Country Comparison Reports
**Priority:** Should Have (Phase 3)

**Description:**
Global Admin xem báo cáo so sánh performance giữa các countries: creators, campaigns, revenue, content quality.

**Acceptance Criteria:**
- [ ] Comparison dashboard: chọn 2+ countries để so sánh
- [ ] Metrics: creator count, active rate, campaign count, revenue (USD), avg content quality score
- [ ] Trend charts: performance over time per country
- [ ] Export comparison reports

**Dependencies:** FR-004, FR-016

---

#### FR-034: Creator Net Income Dashboard
**Priority:** Must Have

**Description:**
Creator xem estimated net income: gross income - income tax. Hiển thị breakdown rõ ràng theo tiền tệ local. Dashboard phân biệt rõ: số tiền ĐÃ đối soát (chính xác, dùng chốt rate) vs CHƯA đối soát (ước tính, dùng realtime rate).

**Acceptance Criteria:**
- [ ] Dashboard hiển thị: gross income, tax deduction, net income (tiền tệ local)
- [ ] Tính toán theo tax rules của country (FR-019)
- [ ] Phân biệt 2 trạng thái rõ ràng:
  - **Đã đối soát:** Số chính xác, USD convert theo chốt rate, label "Đã xác nhận"
  - **Chưa đối soát:** Số ước tính, USD convert theo realtime rate, label "Ước tính — có thể thay đổi"
- [ ] USD tham chiếu kèm label "Tỷ giá tham chiếu, không dùng cho thanh toán"
- [ ] History: monthly/campaign-level breakdown
- [ ] Transparent formula: hiển thị rõ `Gross ₱50,000 − Tax 10% ₱5,000 = Net ₱45,000 (≈ $801*)`
- [ ] KHÔNG hiển thị exchange fee (theo QnA #10)

**Dependencies:** FR-018, FR-019, FR-020, FR-020B

---

## 6. Non-Functional Requirements

### NFR-001: Performance — API Response Time
**Priority:** Must Have

**Description:**
API response time phải đảm bảo trải nghiệm mượt cho users across countries (có latency mạng khác nhau).

**Acceptance Criteria:**
- [ ] API response < 300ms cho 95% requests (p95)
- [ ] API response < 1000ms cho 99% requests (p99)
- [ ] Dashboard/report APIs < 2000ms (heavy aggregation queries)
- [ ] Multi-country queries không chậm hơn > 50% so với single-country

**Rationale:** Hiện tại single-country. Multi-country queries + country_code filter có thể impact performance.

---

### NFR-002: Performance — Concurrent Users
**Priority:** Must Have

**Description:**
Hệ thống phải support concurrent users từ nhiều countries cùng lúc.

**Acceptance Criteria:**
- [ ] Support 1000+ concurrent creators (Phase 1: VN + PH)
- [ ] Support 50+ concurrent admin users
- [ ] Horizontal scaling capability (thêm countries không cần redesign)

**Rationale:** Multi-country = multiply user base. Architecture phải scale.

---

### NFR-003: Security — Data Isolation
**Priority:** Must Have

**Description:**
Data isolation giữa countries phải absolute. Không có path nào để Local Admin hoặc Creator access data nước khác.

**Acceptance Criteria:**
- [ ] All API endpoints enforce country-scope check
- [ ] Penetration test: no cross-country data leak
- [ ] SQL/NoSQL injection protection (existing)
- [ ] Sensitive data (KYC, bank) encrypted at rest (AES-256)
- [ ] Sensitive data access logged (audit trail)

**Rationale:** Multi-country compliance yêu cầu strict data isolation.

---

### NFR-004: Security — Authentication & Authorization
**Priority:** Must Have

**Description:**
Authentication multi-provider, authorization country-scoped, session management secure.

**Acceptance Criteria:**
- [ ] OAuth 2.0 for social logins (existing, extend per country)
- [ ] JWT tokens with country_code claim
- [ ] Token refresh mechanism
- [ ] Session invalidation khi role/permission thay đổi
- [ ] Rate limiting per IP/user
- [ ] CORS configured per country domain

**Rationale:** Multi-country = more attack surface. Auth phải solid.

---

### NFR-005: Scalability — Country Addition
**Priority:** Must Have

**Description:**
Thêm country mới phải là configuration task, không phải code change.

**Acceptance Criteria:**
- [ ] New country setup < 2 tuần (sau Philippines)
- [ ] Setup qua: Country Config + locale files + KYC config + payment config
- [ ] Không cần deploy new code cho country mới
- [ ] Country-specific features via feature flags

**Rationale:** Business objective BO-2. Scale nhanh sang nhiều nước.

---

### NFR-006: Reliability — Uptime
**Priority:** Must Have

**Description:**
Platform phải available cho tất cả countries. Downtime ở 1 country không ảnh hưởng countries khác.

**Acceptance Criteria:**
- [ ] 99.5% uptime (monthly)
- [ ] Country-level health monitoring
- [ ] Graceful degradation: 1 country's payment gateway down → không ảnh hưởng countries khác
- [ ] Backup strategy: daily automated backups
- [ ] Disaster recovery plan: RPO < 24h, RTO < 4h

**Rationale:** Multi-country = multi-timezone = cần uptime cao hơn.

---

### NFR-007: Usability — Internationalization
**Priority:** Must Have

**Description:**
UI/UX phải tự nhiên cho users từ different countries. Không chỉ translate text mà phải localize experience.

**Acceptance Criteria:**
- [ ] RTL support (nếu mở rộng Arab/Middle East — future)
- [ ] Date format theo locale (DD/MM/YYYY vs MM/DD/YYYY)
- [ ] Number format theo locale (1,000.00 vs 1.000,00)
- [ ] Currency symbol placement (₱100 vs 100 ₫)
- [ ] Browser/device: Chrome, Safari, Firefox (latest 2 versions), iOS Safari, Android Chrome
- [ ] Mobile responsive (existing, maintain)

**Rationale:** Localization quality ảnh hưởng trực tiếp user adoption.

---

### NFR-008: Maintainability — Code Quality
**Priority:** Should Have

**Description:**
Codebase phải maintainable khi scale thêm countries và features.

**Acceptance Criteria:**
- [ ] Country-specific logic isolated (Country Config, not hardcoded)
- [ ] No VN-specific hardcoded values in shared code
- [ ] API documentation (Swagger — existing, maintain)
- [ ] Testing: unit tests cho critical business logic (tax calculation, permission check, data isolation)
- [ ] Code review mandatory cho multi-tenancy related changes

**Rationale:** Technical debt ở multi-tenancy code = exponential cost.

---

### NFR-009: Compatibility — Backward Compatibility
**Priority:** Must Have

**Description:**
VN platform phải tiếp tục hoạt động bình thường trong và sau migration. Zero downtime migration.

**Acceptance Criteria:**
- [ ] VN users không bị interrupt trong quá trình migration
- [ ] Existing VN API contracts maintained (backward compatible)
- [ ] VN partner apps (11 apps) tiếp tục hoạt động
- [ ] Migration rollback plan tested

**Rationale:** VN là production revenue. Không được break.

---

### NFR-010: Monitoring — Multi-Country Observability
**Priority:** Must Have

**Description:**
Monitoring và alerting phải phân biệt được issues per country.

**Acceptance Criteria:**
- [ ] Metrics tagged by `country_code`
- [ ] Alerts configurable per country (Elastic APM — existing, extend)
- [ ] Dashboard: error rate per country, latency per country
- [ ] Log correlation: request → country → user

**Rationale:** Country-specific issues cần identify và resolve nhanh.

---

## 7. Epics

### EPIC-001: Multi-Tenancy Foundation
**Description:** Xây dựng nền tảng multi-tenancy: data partitioning, country configuration, URL routing, data aggregation.

**Functional Requirements:**
- FR-001: Country-Based Data Partitioning
- FR-002: Country Configuration Store
- FR-003: URL Routing theo Country Code
- FR-004: Cross-Country Data Aggregation
- FR-029: Database Migration — VN Data

**Story Count Estimate:** 8-10 stories

**Priority:** Must Have (Phase 1 — làm TRƯỚC)

**Business Value:** Foundation cho toàn bộ dự án. Không có epic này = không có Global Platform.

---

### EPIC-002: Authentication & User Management
**Description:** Mở rộng auth system cho multi-country: multi-provider OAuth per country, user country binding, country-scoped permissions.

**Functional Requirements:**
- FR-005: Multi-Provider OAuth với Feature Flag
- FR-006: User Country Binding & Multi-Country Profile
- FR-007: Role & Permission System — Country-Scoped

**Story Count Estimate:** 6-8 stories

**Priority:** Must Have (Phase 1)

**Business Value:** User onboarding per country. Không có = không thể register/login theo country.

---

### EPIC-003: Internationalization (i18n)
**Description:** Hệ thống đa ngôn ngữ end-to-end: backend locale, frontend language switcher, content management, auto-detection.

**Functional Requirements:**
- FR-008: Backend Multi-Language Support
- FR-009: Frontend Language Switcher
- FR-010: Content Management Đa Ngôn Ngữ
- FR-011: Auto-Language Detection & Fallback (Phase 2)

**Story Count Estimate:** 6-8 stories

**Priority:** Must Have (Phase 1 core), Should Have (Phase 2 auto-detection)

**Business Value:** UX cho users non-Vietnamese. Critical cho mở rộng quốc tế.

---

### EPIC-004: Admin System — Local & Global
**Description:** Admin panel cho cả Local Admin (country-scoped operations) và Global Admin (cross-country oversight, acting-as-local).

**Functional Requirements:**
- FR-012: Global Admin "Acting as Local" Mode
- FR-013: Audit Trail System
- FR-014: Local Admin — Campaign & Content Operations
- FR-015: Local Admin — Reconciliation & Payment
- FR-016: Global Admin Dashboard — Cross-Country
- FR-017: Global Admin → Local Admin Notifications (Phase 2)

**Story Count Estimate:** 10-12 stories

**Priority:** Must Have (Phase 1 core), Should Have (Phase 2 notifications)

**Business Value:** Operational capability cho mỗi country + global oversight.

---

### EPIC-005: Payment, Currency & Tax
**Description:** Multi-currency display, tax calculation engine, exchange rate management (realtime reference + chốt rate đối soát), payment gateway abstraction.

**Functional Requirements:**
- FR-018: Multi-Currency Display & Conversion
- FR-019: Tax Calculation Engine per Country
- FR-020: Exchange Rate — Realtime Reference Rate
- FR-020B: Exchange Rate — Chốt Rate khi Đối soát (Reconciliation Rate)
- FR-021: Payment Gateway Abstraction
- FR-034: Creator Net Income Dashboard

**Story Count Estimate:** 10-12 stories

**Priority:** Must Have (Phase 1)

**Business Value:** Revenue flow. Creators phải nhận đúng tiền, đúng thuế, đúng tiền tệ. Tách biệt rõ ràng tỷ giá tham chiếu vs tỷ giá pháp lý cho đối soát.

---

### EPIC-006: KYC & Compliance
**Description:** KYC, bank account, tax ID management per country. Compliance với luật từng quốc gia.

**Functional Requirements:**
- FR-022: Country-Specific KYC Requirements
- FR-023: Bank Account Management per Country
- FR-024: Tax ID / Registration per Country

**Story Count Estimate:** 5-7 stories

**Priority:** Must Have (Phase 1)

**Business Value:** Legal compliance. Không có = không thể vận hành hợp pháp ở country mới.

---

### EPIC-007: Campaign & Content per Country
**Description:** Campaign management scoped by country, content moderation per country, social platform configuration.

**Functional Requirements:**
- FR-025: Country-Scoped Campaign Management
- FR-026: Content Moderation per Country
- FR-027: Social Platform Coverage per Country

**Story Count Estimate:** 5-7 stories

**Priority:** Must Have (Phase 1)

**Business Value:** Core business flow. Campaign = product chính của platform.

---

### EPIC-008: Infrastructure & Feature Flags
**Description:** Feature flag system, CI/CD updates, monitoring expansion cho multi-country.

**Functional Requirements:**
- FR-028: Feature Flag System per Country

**NFR Coverage:**
- NFR-005, NFR-006, NFR-010

**Story Count Estimate:** 4-5 stories

**Priority:** Must Have (Phase 1)

**Business Value:** Enable incremental rollout, reduce risk, enable country-specific configuration.

---

### EPIC-009: Philippines Country Launch
**Description:** Trọn bộ setup cho Philippines: config, locale, KYC, payment, bank, tax, vendor training, UAT.

**Functional Requirements:**
- FR-030: Philippines Country Pod Setup

**Story Count Estimate:** 6-8 stories

**Priority:** Must Have (Phase 2)

**Business Value:** Milestone chính. First international market = validate Global Platform.

---

### EPIC-010: Phase 3 Enhancements
**Description:** Indonesia setup, Facebook login, auto-language detection, realtime exchange rate, cross-country reports.

**Functional Requirements:**
- FR-031: Indonesia Country Pod Setup
- FR-032: Facebook Login Integration
- FR-033: Cross-Country Comparison Reports
- FR-011: Auto-Language Detection (from EPIC-003)

**Story Count Estimate:** 8-10 stories

**Priority:** Should Have / Could Have (Phase 3)

**Business Value:** Mở rộng thêm market (Indonesia), nâng cao UX và reporting.

---

## 8. Traceability Matrix

| Epic ID | Epic Name | FRs | NFRs | Phase | Priority | Story Estimate |
|---------|-----------|-----|------|-------|----------|---------------|
| EPIC-001 | Multi-Tenancy Foundation | FR-001, FR-002, FR-003, FR-004, FR-029 | NFR-003, NFR-005, NFR-009 | Phase 1 | Must | 8-10 |
| EPIC-002 | Auth & User Management | FR-005, FR-006, FR-007 | NFR-004 | Phase 1 | Must | 6-8 |
| EPIC-003 | Internationalization | FR-008, FR-009, FR-010, FR-011 | NFR-007 | Phase 1+2 | Must/Should | 6-8 |
| EPIC-004 | Admin System | FR-012, FR-013, FR-014, FR-015, FR-016, FR-017 | NFR-010 | Phase 1+2 | Must/Should | 10-12 |
| EPIC-005 | Payment, Currency & Tax | FR-018, FR-019, FR-020, FR-020B, FR-021, FR-034 | NFR-001 | Phase 1 | Must | 10-12 |
| EPIC-006 | KYC & Compliance | FR-022, FR-023, FR-024 | NFR-003 | Phase 1 | Must | 5-7 |
| EPIC-007 | Campaign & Content | FR-025, FR-026, FR-027 | NFR-002 | Phase 1 | Must | 5-7 |
| EPIC-008 | Infrastructure & Feature Flags | FR-028 | NFR-005, NFR-006, NFR-010 | Phase 1 | Must | 4-5 |
| EPIC-009 | Philippines Launch | FR-030 | NFR-006 | Phase 2 | Must | 6-8 |
| EPIC-010 | Phase 3 Enhancements | FR-031, FR-032, FR-033, FR-011 | NFR-005 | Phase 3 | Should/Could | 8-10 |

**Total Estimated Stories: 68-89**

---

## 9. Prioritization Summary

### Functional Requirements
| Priority | Count | FRs |
|----------|-------|-----|
| **Must Have** | 28 | FR-001→FR-010, FR-012→FR-016, FR-018→FR-021, FR-020B, FR-022→FR-030, FR-034 |
| **Should Have** | 6 | FR-011, FR-017, FR-031, FR-032, FR-033 |
| **Could Have** | 1 | (additional country pods beyond Indonesia) |
| **Total** | 35 | |

### Non-Functional Requirements
| Priority | Count |
|----------|-------|
| **Must Have** | 8 |
| **Should Have** | 2 |
| **Total** | 10 |

---

## 10. Dependencies

### Internal Dependencies
- **ambassabor backend (Go):** Core refactoring target — multi-tenancy, permissions, i18n
- **ambassabor frontend (React/UmiJS):** UI refactoring — country selector, language switcher, i18n
- **ambassabor admin (React/Ant Design Pro):** Admin refactoring — Local/Global split, audit trail
- **MongoDB:** Schema migration, new indexes
- **Redis:** Country config cache, feature flags cache
- **MinIO:** KYC document storage (existing, extend per country)
- **Firebase Auth:** Multi-country auth configuration

### External Dependencies
- **Philippines compliance research:** KYC requirements, tax laws, payment regulations
- **Philippines payment vendor:** GCash, bank transfer — cần scout & integrate
- **Philippines local vendor:** Operations partner — cần recruit & train
- **OAuth providers:** TikTok, Google, Facebook (Meta app review for Phase 2)
- **Exchange rate data source:** Bank authority API (Phase 2)
- **Social platform APIs:** TikTok, Facebook, Instagram, Threads (existing, maintain)

---

## 11. Assumptions

1. **Philippines là country đầu tiên** mở rộng — sẽ validate trước Indonesia
2. **Tech stack giữ nguyên** (Go, React, MongoDB, Redis, MinIO) — không migrate tech
3. **VN platform tiếp tục chạy** song song trong quá trình migration
4. **11 partner apps giữ riêng** (Phase 1-2) — quyết định unify sau Phase 3
5. **Content i18n bằng admin nhập manual** — không dùng AI translation (Phase 1)
6. **Exchange rate Phase 1 bằng manual input** — realtime API ở Phase 2
7. **Single MongoDB cluster** với country_code partitioning — không separate clusters per country
8. **Team ATVN chịu trách nhiệm development** — vendor chỉ operations
9. **Node 14 giữ nguyên Phase 1-2** — upgrade Phase 3 (FR không liệt kê vì là tech task)

---

## 12. Out of Scope

1. **Mobile native app** (iOS/Android) — chỉ responsive web
2. **AI-powered content moderation** — manual moderation only
3. **AI translation** — admin nhập manual per language
4. **EU/CIS country launch** — chỉ planning, không implementation trong 6 tháng
5. **Partner apps unification** (11 apps → 1 app) — evaluate sau Phase 3
6. **GDPR full compliance** — chỉ cần thiết khi thực sự mở EU
7. **Real-time collaboration features** (multi-admin editing)
8. **Advanced analytics / BI integration** — basic reporting chỉ
9. **Blockchain-based payment / crypto**
10. **White-label platform** cho third parties

---

## 13. Open Questions

| # | Question | Owner | Status | Impact |
|---|----------|-------|--------|--------|
| OQ-1 | Philippines KYC: Cụ thể cần những loại government ID nào? Validation rules? | ATVN + PH Legal | Open | FR-022, FR-030 |
| OQ-2 | Philippines payment: GCash, bank transfer, hay vendor nào? API integration docs? | ATVN + PH Vendor | Open | FR-021, FR-030 |
| OQ-3 | Philippines tax: Withholding tax rate? Tax bands? Reporting requirements? | ATVN + PH Accountant | Open | FR-019, FR-030 |
| OQ-4 | ~~Exchange rate "chốt rate" timing~~ **RESOLVED:** Chốt rate tại thời điểm Local Admin tạo reconciliation batch. Xem FR-020B. | GSM VN | **Resolved** | FR-020B |
| OQ-5 | Auto-language detection: Source xác định "quốc gia user" — KYC info, IP geolocation, hay user setting? | Product | Open | FR-011 |
| OQ-6 | Net income formula: Có cần hiển thị international transfer fee reference không? | GSM VN | Open | FR-034 |
| OQ-7 | Server deployment: Centralized VN hay multi-region (SEA)? Latency acceptable? | Engineering | Open | NFR-001, NFR-006 |
| OQ-8 | Partner apps (11): Khi mở rộng multi-country, partner apps có cần multi-country không? | Product | Open | EPIC-010 |

---

## 14. Stakeholders

| Role | Responsibility | Involvement |
|------|---------------|-------------|
| GSM VN | Business requirements, approval, exchange rate decisions | High — approval required |
| GSM Local (PH) | Philippines market requirements, compliance, operations | High — Phase 2 |
| ATVN Engineering | System development, architecture, deployment | High — all phases |
| ATVN Product | Requirements, prioritization, UAT | High — all phases |
| AT Local (PH) | Philippines operations, vendor coordination | Medium — Phase 2+ |
| Local Vendor (PH) | Content moderation, creator support at Philippines | Medium — Phase 2+ |
| Legal/Compliance | KYC, tax, privacy requirements per country | Medium — Phase 0+ |

---

## 15. Timeline Overview

| Phase | Timeline | Focus | Key Deliverable |
|-------|----------|-------|-----------------|
| **Phase 0** | Tuần 1-2 | Foundation & Planning | Architecture doc, compliance research started, vendor scouting |
| **Phase 1** | Tuần 3-12 | Global Core Platform | Multi-tenancy, auth, i18n, admin, payment, KYC — all "Must Have" FRs |
| **Phase 2** | Tuần 10-16 | Philippines Launch | Country Pod setup, vendor training, UAT, first campaign |
| **Phase 3** | Tuần 14-24 | Enhancements | Indonesia, Facebook login, auto-language, realtime exchange rate |

**Note:** Phase 1 & 2 overlap (tuần 10-12). Phase 2 & 3 overlap (tuần 14-16).

---

## PRD Validation Checklist

- [x] Tất cả Must-Have FRs được define rõ ràng (26 FRs)
- [x] Mỗi FR có testable acceptance criteria
- [x] NFRs cover: performance, security, scalability, reliability, usability, maintainability, compatibility, monitoring (10 NFRs)
- [x] NFRs có measurable targets (response time, uptime %, concurrent users)
- [x] Epics group FRs logically (10 epics)
- [x] Tất cả FRs assigned to epics
- [x] Priorities realistic: 26 Must / 7 Should / 1 Could
- [x] Requirements trace to business objectives (BO-1, BO-2, BO-3)
- [x] Out of scope clearly stated (10 items)
- [x] Open questions documented (8 items)
- [x] Dependencies identified (internal + external)

---

*Generated by BMAD Method v6 - Product Manager*
*Date: 2026-03-02*
