# Architecture Decision Records — VCreator Global Platform Core

**Project:** VCreator Global Platform
**Date:** 2026-03-02
**Author:** System Architect
**Related:** [PRD](prd-vcreator-global-platform-2026-03-02.md) | [Architecture](architecture-vcreator-global-platform-2026-03-02.md) | [Brainstorming](../../.bmad/brainstorming-vcreator-global-2026-03-02.md)

---

## ADR-000: Foundational Decisions — Build New, Not Upgrade

### Status
**Accepted** (2026-03-02)

### Decisions

Ba quyết định nền tảng ảnh hưởng toàn bộ dự án:

#### Decision 1: Build mới hoàn toàn — KHÔNG nâng cấp từ source cũ

**Context:** Codebase `ambassabor` hiện tại chạy VN với React 16.x + UmiJS 3.x + Node 14.17.3 (EOL). Có 11 partner apps duplicate. Có thể refactor source cũ hoặc build mới.

**Quyết định: Build mới hoàn toàn (Greenfield).**

**Rationale:**
- Source cũ quá nhiều technical debt: React 16, Node 14 EOL, Socket.io v2, 11 partner apps duplicate
- Refactor source cũ vẫn phải rewrite ~70-80% code (thêm multi-tenancy, i18n, new auth model)
- Build mới cho phép chọn tech stack hiện đại ngay từ đầu
- Không bị ràng buộc bởi design decisions cũ (single-country assumptions)
- Source cũ (VN) tiếp tục chạy song song cho đến khi Global Platform stable → migrate VN sang

**Consequences:**
- (+) Tech stack hiện đại, clean architecture từ đầu
- (+) Không mang theo technical debt
- (+) Thiết kế multi-tenancy native (không phải bolt-on)
- (-) Effort lớn hơn (không reuse code cũ)
- (-) Phải maintain 2 systems song song trong giai đoạn chuyển tiếp
- (-) VN migration trở thành project riêng (chuyển data + users từ cũ sang mới)

**Impact lên báo giá:** Hours trong CSV là effort build mới, KHÔNG phải effort refactor. Không tính re-use savings từ source cũ.

#### Decision 2: Hierarchy — Country → Partner (giữ nguyên partner model)

**Context:** Hệ thống hiện tại có partner/brand model (Techcombank, HDBank, Anker...) — mỗi partner có branded app riêng. Global Platform vẫn cần concept này.

**Quyết định: Dual-dimension tenancy = Country + Partner.**

```
GLOBAL PLATFORM
  └── Country: Philippines (PH)
  │     ├── Partner: Brand A → branded app PH
  │     ├── Partner: Brand B → branded app PH
  │     └── Default: VCreator PH (no specific partner)
  │
  └── Country: Vietnam (VN)
        ├── Partner: Techcombank → branded app VN
        ├── Partner: HDBank → branded app VN
        └── Default: VCreator VN
```

**Data model:**
```
{ country_code: "ph", partner_code: "brand_a", ... }
{ country_code: "ph", partner_code: null, ... }  ← default VCreator PH
```

**Consequences:**
- Query filter: `country_code` (bắt buộc) + `partner_code` (optional)
- Campaign có thể gắn với partner cụ thể hoặc chung cho cả country
- Branded app per partner per country = matrix, cần partner app template system
- Admin: Local Admin scope = country. Partner manager scope = country + partner.

#### Decision 3: Mỗi country có đội ngũ operation riêng

**Context:** Ai vận hành platform ở mỗi country? Centralized từ VN hay local team?

**Quyết định: Local operation team per country.**

**Implications cho system design:**

| Aspect | Impact |
|--------|--------|
| **Admin roles** | Mỗi country có Local Admin team riêng (admin, accountant, operations) |
| **Data isolation** | CRITICAL — Local team KHÔNG được xem data country khác |
| **Language** | Admin panel cần i18n (local team dùng ngôn ngữ local) |
| **Training** | Onboarding docs, guides per country per language |
| **Timezone** | Operations theo timezone local (audit log, scheduling) |
| **Reconciliation** | Local team tự đối soát — không centralized |
| **KYC review** | Local team review KYC (hiểu context local: ID types, naming conventions) |
| **Content moderation** | Local team duyệt content (hiểu ngôn ngữ, văn hóa local) |
| **Global Admin** | VN team oversight — "acting as local" khi cần, bắt buộc audit |

**Consequences:**
- (+) Operations quality cao hơn (local context understanding)
- (+) Timezone-appropriate response
- (+) Scalable: thêm country = hire local team
- (-) Cần training materials per country
- (-) Cần robust permission system (country-scoped)
- (-) Global Admin "acting as local" cần audit trail chặt

---

## ADR-001: Multi-Tenancy Strategy — Country-Scoped Data Partitioning

### Status
**Accepted** (2026-03-02)

### Context

Global Platform được **build mới hoàn toàn** (ADR-000), không nâng cấp từ source cũ. Cần thiết kế multi-tenancy native cho đa quốc gia (Philippines → Indonesia → CIS/EU) với yêu cầu:

- **Data isolation**: Mỗi country có local operation team riêng (ADR-000), KHÔNG được xem data country khác
- **Dual-dimension**: Country + Partner (ADR-000) — campaign/data scoped by cả hai
- **Compliance**: KYC, thuế, privacy rules khác nhau per country
- **Performance**: Queries không bị chậm khi thêm countries
- **VN migration**: Source cũ chạy song song, VN data migrate sang sau khi Global Platform stable

### Các phương án đã xem xét

| Phương án | Mô tả | Pros | Cons |
|-----------|-------|------|------|
| **A. Separate databases per country** | Mỗi country 1 MongoDB cluster riêng | Isolation hoàn toàn, performance tốt | Expensive, cross-country queries phức tạp, ops overhead lớn |
| **B. Separate collections per country** | Mỗi collection có suffix `_ph`, `_vn` | Isolation tốt | Code duplication cực cao, migration nightmare |
| **C. Country_code field partitioning** | Thêm `country_code` vào tất cả documents, middleware filter | Đơn giản, 1 codebase, cross-country queries dễ | Phải migrate VN data, middleware phải chặt |
| **D. Fork codebase per country** | Mỗi country 1 instance riêng | Nhanh deploy | Maintenance hell, mất shared improvements |

### Decision

**Chọn C: Country_code field partitioning** — Enhanced Monolith with Country-Scoped Multi-Tenancy.

```
┌──────────────────────────────────────────┐
│            MONGODB CLUSTER               │
│                                          │
│  users:      { ..., country_code: "vn" } │
│  campaigns:  { ..., country_code: "ph" } │
│  contents:   { ..., country_code: "vn" } │
│  earnings:   { ..., country_code: "ph" } │
│  kyc_data:   { ..., country_code: "vn" } │
│  ...                                     │
│                                          │
│  INDEX: { country_code: 1, ... }         │
└──────────────────────────────────────────┘
         ▲
         │ middleware auto-inject filter
         │
┌────────┴─────────────────────────────────┐
│         COUNTRY CONTEXT LAYER            │
│                                          │
│  Request → Extract country_code          │
│         → Inject vào query context       │
│         → Validate permission scope      │
│                                          │
│  Sources: URL path, JWT token, session   │
└──────────────────────────────────────────┘
```

### Implementation

**Country Context Middleware Chain:**
1. **Extract**: Lấy `country_code` từ URL path (`/ph/api/...`) hoặc JWT claim
2. **Validate**: Check country_code có trong danh sách active countries
3. **Inject**: Set `country_code` vào request context
4. **Enforce**: Tất cả DB queries tự động append `country_code` filter
5. **Audit**: Log country context cho mọi write operation

**Country Configuration Service:**
```
country_config: {
  code: "ph",
  name: "Philippines",
  currency: { code: "PHP", symbol: "₱", position: "before" },
  languages: ["fil", "en"],
  tax_rules: { withholding_rate: 0.10, ... },
  kyc_requirements: { accepted_ids: [...], ... },
  payment_config: { gateways: ["gcash", "bank_transfer"], ... },
  oauth_providers: ["tiktok", "google"],
  social_platforms: ["tiktok", "facebook", "instagram"],
  feature_flags: { facebook_login: false, ... },
  active: true
}
```

**Dual-Dimension Tenancy** (country + partner):
```
Hiện tại:  { partner_code: "techcombank" }
Mới:       { country_code: "ph", partner_code: "brand_x" }
```

### Migration Strategy (VN Data)

Vì build mới hoàn toàn (ADR-000), VN migration là chuyển data từ **source cũ → Global Platform mới**:

1. **Phase 1-2**: Global Platform build mới, PH go-live trước (greenfield)
2. **Phase 3**: VN migration — export data từ source cũ → transform → import vào Global Platform
   - Users: map sang Shared Identity + Country Profile "vn" (ADR-002)
   - Campaigns, contents, earnings: import với `country_code = "vn"`
   - Partners (11 branded apps): import config vào dual-tenancy model
3. **Parallel run**: Source cũ + Global Platform chạy song song trong giai đoạn chuyển tiếp
4. **Cutover**: Khi Global Platform VN stable → redirect traffic → decommission source cũ

**Timing**: VN migration là Phase 3, SAU Philippines go-live, giảm risk

### Consequences

**Positive:**
- Build mới → multi-tenancy native từ đầu, không phải bolt-on
- 1 MongoDB cluster, đơn giản ops
- Cross-country queries dễ (Global Admin dashboard)
- 1 codebase, shared improvements across countries
- Country thêm mới = configuration, không cần deploy code mới
- Dual-dimension (country + partner) tích hợp sẵn

**Negative:**
- Middleware phải 100% chặt — 1 query thiếu filter = data leak (đặc biệt quan trọng vì local teams riêng per country)
- Compound indexes tăng storage
- VN migration từ source cũ là project riêng (transform data format)
- Performance có thể degrade nếu data lớn → cần monitoring per country

**Risks & Mitigations:**
| Risk | Mitigation |
|------|-----------|
| Data leak giữa countries | Middleware enforce + integration tests + audit log. Critical vì local teams KHÔNG được xem data country khác |
| VN migration data loss | Phase 3, parallel run, rollback = keep source cũ running |
| Query performance | Compound indexes, country-level monitoring, query explain plans |
| Middleware bypass | Code review checklist, linter rules, automated security tests |
| Partner × Country matrix explosion | Partner app template system, shared base config |

---

## ADR-002: Shared User Identity + Separate Country Profiles

### Status
**Accepted** (2026-03-02)

### Context

Creator có thể hoạt động ở nhiều quốc gia (VN Creator mở rộng sang PH). Cần quyết định: mỗi country là 1 account riêng, hay 1 account dùng chung?

Hệ thống hiện tại: 1 user = 1 account, login bằng TikTok/Google/Facebook + AT SSO. Không có khái niệm multi-country.

### Các phương án đã xem xét

| Phương án | Mô tả | Pros | Cons |
|-----------|-------|------|------|
| **A. Separate accounts per country** | Mỗi country 1 account riêng, OAuth credentials riêng | Isolation đơn giản, data clean | UX tệ (login lại khi switch country), OAuth app management phức tạp |
| **B. Shared identity + separate profiles** | 1 user account chung, mỗi country có profile riêng (KYC, bank, earnings) | UX tốt (login 1 lần, switch country), 1 bộ OAuth chung | Data model phức tạp hơn, cần country context switching |
| **C. Fully shared account** | 1 account, 1 profile, dùng chung KYC/bank across countries | Đơn giản nhất | Không thể — KYC/bank/tax PHẢI khác per country (legal requirement) |

### Decision

**Chọn B: Shared User Identity + Separate Country Profiles**

```
┌────────────────────────────────────────┐
│          USER IDENTITY (shared)         │
│                                         │
│  user_id: "usr_abc123" (global unique)  │
│  oauth: { tiktok: "...", google: "..." }│
│  display_name: "Nguyễn Văn A"          │
│  avatar: "https://..."                  │
│  language_pref: "vi"                    │
│  created_at, last_login                 │
│  active_country: "vn" (last used)       │
└────────┬──────────────┬────────────────┘
         │              │
   ┌─────▼─────┐  ┌────▼──────┐
   │ PROFILE VN │  │ PROFILE PH │
   │            │  │            │
   │ kyc_status │  │ kyc_status │
   │ cccd_data  │  │ gov_id     │
   │ mst        │  │ tin        │
   │ bank_vn    │  │ gcash/bank │
   │ contract   │  │ contract   │
   │ earnings₫  │  │ earnings₱  │
   │ campaigns  │  │ campaigns  │
   │ hashtags   │  │ hashtags   │
   │ referrals  │  │ referrals  │
   └────────────┘  └────────────┘
```

### Implementation

**Data Model:**
```
// Collection: users (shared identity)
{
  _id: ObjectId,
  oauth_providers: [
    { provider: "tiktok", provider_id: "...", ... },
    { provider: "google", provider_id: "...", ... }
  ],
  display_name: "...",
  avatar_url: "...",
  language_pref: "vi",
  active_country: "vn",
  country_profiles: ["vn", "ph"],  // list of activated countries
  created_at: Date,
  last_login: Date
}

// Collection: country_profiles
{
  _id: ObjectId,
  user_id: ObjectId,         // ref → users
  country_code: "ph",
  kyc_status: "approved",
  kyc_data: { encrypted },
  bank_accounts: [{ encrypted }],
  tax_id: { encrypted },
  contract_signed: true,
  contract_date: Date,
  referral_code: "PH_abc123",
  created_at: Date
}

// Earnings, campaigns, contents → vẫn dùng country_code (ADR-001)
// nhưng link via user_id (shared)
```

**OAuth Flow:**
```
Creator click "Login with TikTok"
  → OAuth redirect (1 bộ credentials chung)
  → Callback → match/create user identity
  → IF new user:
      → "Chọn quốc gia của bạn" screen
      → Create country_profile
      → Redirect to /{country_code}/dashboard
  → IF existing user:
      → Redirect to /{active_country}/dashboard
      → Country switcher available in header
```

**Country Switching:**
```
Creator click "Switch to Philippines" 🇵🇭
  → IF has PH profile: switch context → reload scoped data
  → IF no PH profile: "Thêm quốc gia" flow → create profile → switch
  → Update active_country in user identity
  → UI refresh: campaigns, earnings, content = PH scoped
```

### Consequences

**Positive:**
- 1 lần login → access tất cả countries
- 1 bộ OAuth app (TikTok, Google, FB) cho toàn hệ thống
- UX mượt: country switcher trong app
- Giảm friction cho Creator mở rộng cross-country

**Negative:**
- Data model phức tạp hơn (2-level: identity + profile)
- Country switching cần refresh toàn bộ scoped data
- Social account linking: cần quyết định shared vs per-country (xem Open Question)

**Open Question:**
- **Social links (TikTok, IG account) shared hay per country?** Creator PH có thể dùng cùng TikTok account cho cả VN và PH campaigns? → Cần chốt với Product.

---

## ADR-003: Internationalization (i18n) Strategy

### Status
**Accepted** (2026-03-02)

### Context

Platform cần hỗ trợ đa ngôn ngữ. Mỗi country có 2 ngôn ngữ: **local language + English**. Cần i18n cho:
1. **UI labels/buttons/messages** (frontend)
2. **API responses/error messages** (backend)
3. **Campaign content, T&C, notifications** (dynamic content)

Backend hiện tại đã có 17 locale directories — foundation có sẵn nhưng chưa hoàn thiện.

### Các phương án đã xem xét

| Layer | Phương án A | Phương án B |
|-------|-------------|-------------|
| **Dynamic content (campaign, T&C)** | Admin nhập manual per language | AI auto-translate |
| **UI labels** | i18n library (react-intl / next-intl) | No alternative |
| **Backend messages** | Locale files (có sẵn) | No alternative |

**Về dynamic content:**

| Tiêu chí | Admin nhập manual | AI auto-translate |
|-----------|-------------------|-------------------|
| Chất lượng | Cao — human curated | Trung bình — cần review |
| Effort Admin | Cao — nhập 2+ versions | Thấp — nhập 1 → AI dịch |
| Dev effort | Thấp — chỉ cần multi-lang editor | Cao — integrate AI API, review flow |
| Legal content (T&C) | Bắt buộc manual (legal requirement) | Không chấp nhận được |
| Campaign content | Acceptable | Acceptable nếu có review |
| Cost | 0 (admin labor) | AI API cost per content |

### Decision

**Hybrid approach:**
- **UI labels + backend messages**: Locale files + i18n library (standard)
- **Legal content (T&C, contracts)**: Admin nhập manual per language (bắt buộc)
- **Campaign content**: Admin nhập manual Phase 1, xem xét AI-assist Phase 3

### Implementation

**Backend i18n:**
```
/locales/
  /vi/        ← Vietnamese (existing, cần audit)
  /en/        ← English (existing, cần hoàn thiện)
  /fil/       ← Filipino/Tagalog (mới)
  /id/        ← Indonesian (Phase 3)

Mỗi locale:
  errors.json       ← error messages
  notifications.json ← notification templates
  labels.json       ← API response labels
```

**Language resolution chain:**
```
1. User manual choice (saved in profile)    ← highest priority
2. Market default (country_config.languages[0])
3. Cross-market fallback: English
4. System default: English
```

**Frontend i18n:**
```
- react-intl hoặc tương đương (phù hợp với React + UmiJS stack hiện tại)
- Locale files loaded async (code splitting per language)
- Language switcher: header component, persist to user profile
- Number/currency format per locale:
    VN: 1.000.000 ₫
    PH: ₱1,000,000
    EN: $1,000,000
```

**Dynamic content model:**
```
// Campaign content
{
  campaign_id: ObjectId,
  country_code: "ph",
  content: {
    "fil": {
      title: "...",
      description: "...",
      rules: "...",
      terms: "..."
    },
    "en": {
      title: "...",
      description: "...",
      rules: "...",
      terms: "..."
    }
  }
}
```

**Admin CMS UI:**
```
┌─────────────────────────────────┐
│  Campaign: Summer Sale 2026     │
│                                 │
│  [Filipino] [English]  ← tabs  │
│  ─────────────────────────      │
│  Title: ___________________     │
│  Description: _____________     │
│  Rules: ___________________     │
│  T&C: _____________________    │
│                                 │
│  ⚠️ English version missing    │
│  [Preview] [Save]               │
└─────────────────────────────────┘
```

### Consequences

**Positive:**
- Foundation đã có (17 locale dirs) → build on top
- Standard approach, well-documented tooling
- Legal content quality assured (manual)
- Flexible: thêm language = thêm locale files

**Negative:**
- Admin effort cao cho manual content input (mỗi content × mỗi language)
- Locale files cần audit và hoàn thiện (technical debt)
- Currency/number formatting phải test kỹ per locale

---

## ADR-004: Multi-Currency & Dual Exchange Rate

### Status
**Accepted** (2026-03-02)

### Context

Mỗi country có tiền tệ riêng (VNĐ, PHP, IDR...). Cần:
1. Creator xem earnings bằng **tiền local** (primary)
2. Global Admin xem tổng hợp bằng **USD** (comparison)
3. Khi đối soát (reconciliation), cần **chốt tỷ giá** cố định cho batch đó
4. Ngoài reconciliation, hiển thị **tỷ giá tham chiếu realtime** cho informational

### Các phương án đã xem xét

| Phương án | Mô tả | Pros | Cons |
|-----------|-------|------|------|
| **A. Single rate** | 1 loại tỷ giá duy nhất | Đơn giản | Không phân biệt được reference vs chốt |
| **B. Dual rate** | Realtime reference + Reconciliation chốt rate | Rõ ràng, đúng nghiệp vụ | Phức tạp hơn, cần manage 2 rate streams |
| **C. No USD** | Chỉ hiển thị local currency | Đơn giản nhất | Global Admin không so sánh được cross-country |

### Decision

**Chọn B: Dual Exchange Rate System**

```
┌─────────────────────────────────────────────────────┐
│                  EXCHANGE RATES                       │
│                                                       │
│  ┌─────────────────────┐  ┌────────────────────────┐ │
│  │  REALTIME REFERENCE  │  │  RECONCILIATION RATE   │ │
│  │                      │  │                        │ │
│  │  Source: bank API     │  │  Source: snapshot at   │ │
│  │  Update: every 15min  │  │  reconciliation time  │ │
│  │  Cache: Redis + TTL   │  │  Storage: immutable    │ │
│  │  Use: informational   │  │  record per batch      │ │
│  │  Label: "≈ $X (ref)"  │  │  Use: payment calc,   │ │
│  │                      │  │  official reporting    │ │
│  │  Mutable: yes (auto)  │  │  Mutable: NO          │ │
│  └─────────────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Implementation

**Realtime Reference Rate:**
```
// Service: exchange_rate_service
{
  country_code: "ph",
  base: "USD",
  target: "PHP",
  rate: 56.2,
  source: "bangko_sentral",       // bank authority per country
  fetched_at: "2026-03-02T10:30:00Z",
  cache_ttl: 900                   // 15 min, configurable per country
}

// API: GET /api/exchange-rate?country=ph
// Fallback: if API fail → last known rate + "cập nhật lúc..." label
```

**Reconciliation Rate (chốt):**
```
// Khi Local Admin tạo reconciliation batch:
{
  batch_id: ObjectId,
  country_code: "ph",
  reconciliation_rate: {
    base: "USD",
    target: "PHP",
    rate: 56.2,
    source: "realtime",             // hoặc "manual"
    manual_reason: null,            // bắt buộc nếu source = "manual"
    locked_by: "admin@ph",
    locked_at: "2026-03-15T14:00:00Z"
  },
  // IMMUTABLE sau khi confirm
  // Tất cả payment trong batch dùng rate này
  // Nếu sai → tạo adjustment batch mới (không sửa batch cũ)
}
```

**Display Rules:**

| Ai xem | Hiển thị | Rate source |
|--------|----------|-------------|
| **Creator** | Earnings ₱50,000 ≈ $890 (tham chiếu) | Realtime reference |
| **Local Admin** | Chưa đối soát: ₱ + USD (realtime). Đã đối soát: ₱ + USD (chốt rate) | Mixed |
| **Global Admin** | Revenue: $125,000 confirmed + ~$23,000 estimated | Chốt for confirmed, realtime for estimated |

**UI phân biệt:**
- **Realtime**: text nhỏ, màu xám, icon ≈, label "tỷ giá tham chiếu"
- **Chốt**: text bình thường, màu đen, label "tỷ giá chốt [date]"

### Consequences

**Positive:**
- Nghiệp vụ rõ ràng: tham chiếu ≠ thanh toán
- Reconciliation rate immutable → audit-safe, legal-safe
- Creator hiểu rõ "con số này là ước tính, không phải thực tế"
- Global Admin dashboard phân biệt confirmed vs estimated revenue

**Negative:**
- Phức tạp hơn single rate
- Cần maintain exchange rate API integration per country
- UI cần thiết kế cẩn thận để Creator không confuse 2 loại rate

---

## ADR-005: Feature Flag System per Country

### Status
**Accepted** (2026-03-02)

### Context

Không phải feature nào cũng sẵn sàng cho tất cả countries cùng lúc. VD: Facebook login Phase 2, GCash chỉ PH, eKYC flow khác per country. Cần cơ chế bật/tắt feature per country mà không cần deploy code mới.

### Decision

**Feature Flag Service tích hợp vào Country Config.**

```
// Country Config bao gồm feature_flags:
{
  country_code: "ph",
  feature_flags: {
    "facebook_login":     { enabled: false, phase: 2 },
    "gcash_payment":      { enabled: true },
    "deferred_kyc":       { enabled: true },
    "ai_content_scan":    { enabled: false, phase: 4 },
    "creator_badge":      { enabled: false, phase: 3 }
  }
}

// Backend check:
isFeatureEnabled("facebook_login", ctx.country_code) → bool

// Frontend: flags fetched via API → conditional rendering
```

### Consequences

**Positive:**
- Rollout incremental per country
- Disable feature nhanh nếu có issue (kill switch)
- Không cần deploy code khi thay đổi feature availability
- A/B testing per country possible

**Negative:**
- Feature flag debt: cần cleanup khi feature mature (tất cả countries đều bật)
- Code phải handle cả 2 states (enabled/disabled) cho mỗi feature

---

## Summary — All ADRs

| ADR | Decision | Impact |
|-----|----------|--------|
| **ADR-000** | Build mới (greenfield), Country → Partner hierarchy, Local ops team per country | Foundation — ảnh hưởng toàn bộ approach |
| **ADR-001** | Country_code field partitioning + Dual-dimension tenancy (country + partner) | Data layer — ảnh hưởng toàn bộ queries |
| **ADR-002** | Shared User Identity + Separate Country Profiles | User model — ảnh hưởng auth, onboarding, UX |
| **ADR-003** | Hybrid i18n: locale files + manual CMS content | i18n layer — ảnh hưởng FE, BE, admin |
| **ADR-004** | Dual Exchange Rate (realtime reference + reconciliation chốt) | Financial layer — ảnh hưởng earnings, payout, reporting |
| **ADR-005** | Feature Flags per Country (integrated with Country Config) | Deployment — ảnh hưởng rollout strategy |

### Dependencies

```
ADR-000 (Foundational) ← Tất cả ADR khác build on top of this
    ↓
ADR-001 (Multi-Tenancy) ← Foundation layer, phải làm trước
    ↓
ADR-002 (User Identity) ← Depends on country_code + partner model
ADR-003 (i18n)          ← Depends on country_code + local ops team
ADR-004 (Currency)      ← Depends on country_code
ADR-005 (Feature Flags) ← Depends on Country Config (ADR-001)
```

### Open Questions (cần chốt)

| # | Question | ADR | Impact |
|---|----------|-----|--------|
| 1 | Social links shared hay per country? | ADR-002 | Data model |
| 2 | KYC deferred được không? (legal per country) | ADR-001, 002 | Onboarding flow |
| 3 | Exchange rate data source per country? | ADR-004 | Integration |
| 4 | Feature flag cleanup policy? | ADR-005 | Tech debt |
| 5 | Tech stack cho build mới? (Go tiếp hay chuyển?) | ADR-000 | Toàn bộ dev effort |
| 6 | Partner app template strategy? (shared base hay separate builds) | ADR-000, 001 | Partner onboarding effort |
| 7 | VN cutover timeline? (parallel run bao lâu) | ADR-000 | Ops cost |

---

*Generated by BMAD Method v6 — System Architect*
*Date: 2026-03-02*
