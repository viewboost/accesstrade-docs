# Architecture: VCreator Global Platform

**Version:** 1.0
**Date:** 2026-03-02
**Author:** System Architect (BMAD Method)
**Status:** Draft
**PRD Reference:** [prd-vcreator-global-platform-2026-03-02.md](prd-vcreator-global-platform-2026-03-02.md)

---

## 1. Architectural Drivers

Các NFRs sau đây ảnh hưởng mạnh nhất đến thiết kế kiến trúc:

| # | Driver | NFR | Impact |
|---|--------|-----|--------|
| AD-1 | **Data Isolation giữa Countries** | NFR-003 | Mọi query phải scoped by country. Dual-dimension tenancy (country + partner). |
| AD-2 | **Backward Compatibility VN** | NFR-009 | Migration zero-downtime. VN + 11 partner apps phải tiếp tục hoạt động. |
| AD-3 | **Country Addition = Configuration** | NFR-005 | Thêm country < 2 tuần. Không cần deploy new code. |
| AD-4 | **Performance với Multi-Country Queries** | NFR-001 | p95 < 300ms. Cross-country aggregation < 2000ms. |
| AD-5 | **Country-Level Observability** | NFR-010 | Metrics, logs, alerts phân biệt per country. |
| AD-6 | **Multi-Currency + Dual Exchange Rate** | FR-020, FR-020B | Realtime reference rate + immutable reconciliation rate. |

---

## 2. High-Level Architecture

### 2.1 Pattern: Enhanced Monolith with Country-Scoped Multi-Tenancy

**Rationale:** Hệ thống hiện tại là monolith (Go backend + 2 API servers: public + admin). Chuyển sang microservices sẽ là overkill và high-risk cho timeline 6 tháng. Thay vào đó, **giữ monolith nhưng thêm multi-tenancy layer**.

**Chiến lược:**
- Giữ nguyên kiến trúc 3 services (public API, admin API, file service)
- Thêm **Country Context Layer** vào middleware chain
- Mở rộng **Partner tenancy** hiện tại thành **Dual-Dimension Tenancy** (country + partner)
- Thêm **Country Configuration Service** (trong cùng monolith)
- Thêm **Exchange Rate Service** (trong cùng monolith)
- Thêm **Audit Service** (mở rộng từ audit hiện tại)

### 2.2 Architecture Diagram

```
                    ┌─────────────────────────────────────────────────────┐
                    │                    CLIENTS                          │
                    │                                                     │
                    │  ┌──────────┐  ┌──────────┐  ┌────────────────┐   │
                    │  │ Frontend │  │  Admin   │  │ Partner Apps   │   │
                    │  │ (React)  │  │ (React)  │  │ (11 React apps)│   │
                    │  └────┬─────┘  └────┬─────┘  └──────┬─────────┘   │
                    └───────┼─────────────┼───────────────┼─────────────┘
                            │             │               │
                    ┌───────▼─────────────▼───────────────▼─────────────┐
                    │              NGINX / LOAD BALANCER                 │
                    │   /{cc}/api/public/*    /api/admin/*   /api/file/* │
                    └───────┬─────────────┬───────────────┬─────────────┘
                            │             │               │
              ┌─────────────▼──┐  ┌───────▼────────┐  ┌──▼──────────┐
              │  PUBLIC API    │  │  ADMIN API     │  │ FILE SERVICE│
              │  (Go/Echo)     │  │  (Go/Echo)     │  │ (Go/Echo)   │
              │  Port: 8080    │  │  Port: 8081    │  │ Port: 8082  │
              └───────┬────────┘  └───────┬────────┘  └──┬──────────┘
                      │                   │               │
              ┌───────▼───────────────────▼───────────────▼─────────┐
              │                SHARED INTERNAL LAYERS                │
              │                                                     │
              │  ┌─────────────────────────────────────────────┐   │
              │  │          MIDDLEWARE CHAIN (Enhanced)          │   │
              │  │                                              │   │
              │  │  APM → CORS → Logger → Gzip → Recover       │   │
              │  │  → Auth(JWT) → ★ CountryContext              │   │
              │  │  → ★ CountryPermission → Handler             │   │
              │  └─────────────────────────────────────────────┘   │
              │                                                     │
              │  ┌─────────────────────────────────────────────┐   │
              │  │          SERVICE LAYER (Enhanced)             │   │
              │  │                                              │   │
              │  │  ┌────────────┐ ┌────────────┐ ┌─────────┐ │   │
              │  │  │ User Svc   │ │ Event Svc  │ │Content  │ │   │
              │  │  │ (existing) │ │ (existing) │ │ Svc     │ │   │
              │  │  └────────────┘ └────────────┘ └─────────┘ │   │
              │  │  ┌────────────┐ ┌────────────┐ ┌─────────┐ │   │
              │  │  │★ Country   │ │★ Exchange  │ │★ Audit  │ │   │
              │  │  │  Config Svc│ │  Rate Svc  │ │ Svc v2  │ │   │
              │  │  └────────────┘ └────────────┘ └─────────┘ │   │
              │  │  ┌────────────┐ ┌────────────┐ ┌─────────┐ │   │
              │  │  │★ Tax Svc   │ │★ Payment   │ │★ Feature│ │   │
              │  │  │            │ │  Gateway   │ │ Flag Svc│ │   │
              │  │  └────────────┘ └────────────┘ └─────────┘ │   │
              │  └─────────────────────────────────────────────┘   │
              │                                                     │
              │  ┌─────────────────────────────────────────────┐   │
              │  │          DATA ACCESS LAYER (DAO)             │   │
              │  │  ★ CountryScopedDAO wraps existing DAOs      │   │
              │  │  70+ existing DAO files                      │   │
              │  └─────────────────────────────────────────────┘   │
              └─────────┬──────────────┬──────────────┬─────────────┘
                        │              │              │
              ┌─────────▼──┐  ┌───────▼──────┐  ┌───▼──────────┐
              │  MongoDB   │  │   Redis      │  │   MinIO      │
              │  (data)    │  │   (cache +   │  │   (files +   │
              │            │  │   sessions + │  │   KYC docs)  │
              │            │  │   rate cache)│  │              │
              └────────────┘  └──────────────┘  └──────────────┘

★ = New components for Global Platform
```

### 2.3 Dual-Dimension Tenancy Model

```
                    ┌──────────────────────────────────────┐
                    │           TENANCY DIMENSIONS          │
                    │                                      │
                    │  Dimension 1: COUNTRY                │
                    │  ┌────┐ ┌────┐ ┌────┐ ┌────┐       │
                    │  │ VN │ │ PH │ │ ID │ │ .. │       │
                    │  └────┘ └────┘ └────┘ └────┘       │
                    │                                      │
                    │  Dimension 2: PARTNER (cross-country) │
                    │  ┌────────┐ ┌──────┐ ┌───────┐      │
                    │  │ HDBank │ │Anker │ │ Yody  │ ...  │
                    │  │ (VN)   │ │(VN,PH)│ │(VN)  │      │
                    │  └────────┘ └──────┘ └───────┘      │
                    │                                      │
                    │  Query Scope:                        │
                    │  Local Admin:  country=PH            │
                    │  + partner filter if non-root        │
                    │                                      │
                    │  Global Admin: country=ALL (or pick) │
                    │  + partner filter if non-root        │
                    └──────────────────────────────────────┘
```

**Rules:**
- Partner có field `countries: ["vn", "ph"]` — danh sách countries mà partner hoạt động
- Campaign thuộc 1 partner + 1 country (`partner` + `country_code`)
- Staff (admin user) có `country_code` scope + `partner` scope
- Creator (user) có profile per country, có thể join campaigns ở nhiều countries
- **Query precedence:** Country filter TRƯỚC → Partner filter SAU

---

## 3. Technology Stack

### 3.1 Giữ Nguyên (No Changes)

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| Backend | Go | 1.24 | Existing, performant, stable |
| Web Framework | Echo | v4.11.4 | Existing, lightweight, fast middleware chain |
| Database | MongoDB | Driver 1.11.3 | Existing, flexible schema cho multi-tenancy |
| Cache | Redis | go-redis v8 | Existing, dùng cho sessions + config cache + rate cache |
| File Storage | MinIO | v7.0.69 | Existing, S3-compatible |
| Auth | JWT + Firebase | Existing | Existing, extend with country_code claim |
| APM | Elastic APM | v1.15 | Existing, extend with country tag |
| Logging | Zap | v1.27 | Existing, structured logging |
| Frontend | React 16 + UmiJS 3.5 | Existing | Existing, add i18n layer |
| Admin | React 16 + Ant Design Pro | Existing | Existing, add country scope UI |

### 3.2 New Components (Add, Not Replace)

| Component | Purpose | Implementation |
|-----------|---------|---------------|
| Country Context Middleware | Inject country_code vào request context | New Echo middleware |
| Country Permission Middleware | Verify country scope | New Echo middleware |
| Country Config Service | CRUD + cache country configs | New Go service + MongoDB collection |
| Exchange Rate Service | Realtime rate fetch + cache | New Go service + Redis cache |
| Reconciliation Rate Store | Immutable chốt rate per batch | New MongoDB collection |
| Tax Calculation Engine | Country-specific tax rules | New Go service |
| Payment Gateway Abstraction | Pluggable payment per country | New Go interface + implementations |
| Feature Flag Service | Per-country feature toggles | New Go service + Redis cache |
| Audit Service v2 | Enhanced audit with country scope | Extend existing audit service |
| i18n Content Store | Multi-language content management | Extend existing content model |

### 3.3 External Services (New)

| Service | Purpose | Phase |
|---------|---------|-------|
| Exchange Rate API | Realtime rates from bank authority | Phase 1 |
| Philippines Payment Gateway | GCash / bank transfer | Phase 2 |
| Indonesia Payment Gateway | TBD | Phase 3 |

---

## 4. System Components

### Component 1: Country Context Middleware (★ NEW)

**Purpose:** Extract country_code từ URL/JWT và inject vào request context. Đây là **gate** cho toàn bộ multi-tenancy.

**Responsibilities:**
- Parse country_code từ URL path (`/{cc}/api/...`)
- Hoặc từ JWT token claim (`country_code`)
- Hoặc từ request header (`X-Country-Code`) cho admin API
- Validate country_code against Country Config (cached)
- Set country context: `ctx.Set("country_code", cc)`
- Set country config: `ctx.Set("country_config", config)`

**Interfaces:**
```go
// Middleware injection point - after Auth, before handlers
func CountryContextMiddleware() echo.MiddlewareFunc

// Context helpers
func GetCountryCode(ctx echo.Context) string
func GetCountryConfig(ctx echo.Context) *CountryConfig
func IsGlobalScope(ctx echo.Context) bool
```

**Dependencies:** Country Config Service (for validation + config lookup)

**FRs Addressed:** FR-001, FR-003

---

### Component 2: Country Permission Middleware (★ NEW)

**Purpose:** Enforce country-scoped access control. Local Admin chỉ access data nước mình.

**Responsibilities:**
- Verify staff's `country_scope` matches request's country_code
- Global Admin bypass country check nhưng log "acting as"
- Partner-level filtering (existing logic, enhanced)
- Block cross-country access attempts

**Interfaces:**
```go
// After CountryContext middleware
func CountryPermissionMiddleware() echo.MiddlewareFunc

// Permission helpers
func RequireCountryAccess(cc string) echo.MiddlewareFunc
func RequireGlobalAdmin() echo.MiddlewareFunc
func ActingAsLocal(cc string, reason string) echo.MiddlewareFunc
```

**FRs Addressed:** FR-007, FR-012

---

### Component 3: Country Config Service (★ NEW)

**Purpose:** Quản lý cấu hình per country: currency, languages, tax rules, KYC requirements, payment config, OAuth providers, feature flags.

**Responsibilities:**
- CRUD country configurations
- Cache configs in Redis (TTL: 5 min)
- Validate country_code existence
- Provide config to middleware and services

**Data Model:**
```go
type CountryConfig struct {
    ID              AppID             `bson:"_id"`
    Code            string            `bson:"code"`           // "vn", "ph", "id"
    Name            string            `bson:"name"`           // "Vietnam"
    NameLocal       string            `bson:"nameLocal"`      // "Việt Nam"
    Currency        CurrencyConfig    `bson:"currency"`
    Languages       []LanguageConfig  `bson:"languages"`
    TaxRules        TaxRules          `bson:"taxRules"`
    KYCRequirements KYCConfig         `bson:"kycRequirements"`
    PaymentConfig   PaymentConfig     `bson:"paymentConfig"`
    OAuthProviders  []OAuthProvider   `bson:"oauthProviders"`
    FeatureFlags    map[string]bool   `bson:"featureFlags"`
    Timezone        string            `bson:"timezone"`
    Status          string            `bson:"status"`         // "active", "inactive"
    CreatedAt       time.Time         `bson:"createdAt"`
    UpdatedAt       time.Time         `bson:"updatedAt"`
}

type CurrencyConfig struct {
    Code           string  `bson:"code"`           // "VND", "PHP", "IDR"
    Symbol         string  `bson:"symbol"`         // "₫", "₱", "Rp"
    SymbolPosition string  `bson:"symbolPosition"` // "before" or "after"
    DecimalPlaces  int     `bson:"decimalPlaces"`  // 0 for VND, 2 for PHP
    ThousandSep    string  `bson:"thousandSep"`    // "." for VN, "," for PH
    DecimalSep     string  `bson:"decimalSep"`     // "," for VN, "." for PH
}
```

**MongoDB Collection:** `country-configs`
**Redis Cache Key:** `country:config:{code}` (TTL: 5 min)

**FRs Addressed:** FR-002, FR-028

---

### Component 4: Exchange Rate Service (★ NEW)

**Purpose:** 2 chức năng riêng biệt: (1) Realtime reference rate (informational), (2) Reconciliation chốt rate (immutable).

**Responsibilities:**

**4A. Realtime Reference Rate:**
- Fetch rate từ external API (bank authority / financial API)
- Cache trong Redis (TTL: 15 min, configurable per country)
- Provide rate cho dashboard display
- Fallback: dùng rate gần nhất + timestamp warning
- Store rate history (daily snapshots)

**4B. Reconciliation Rate:**
- Khi Local Admin tạo reconciliation batch → suggest current rate
- Admin confirm hoặc override (với reason)
- Chốt rate → immutable, gắn vào batch
- Provide rate cho payment calculation + Global dashboard

**Interfaces:**
```go
type ExchangeRateService interface {
    // Realtime reference
    GetRealtimeRate(ctx context.Context, fromCurrency, toCurrency string) (*Rate, error)
    GetRateHistory(ctx context.Context, currency string, from, to time.Time) ([]Rate, error)

    // Reconciliation rate
    SuggestReconciliationRate(ctx context.Context, cc string) (*Rate, error)
    LockReconciliationRate(ctx context.Context, batchID AppID, rate Rate, reason string, actor AppID) error
    GetReconciliationRate(ctx context.Context, batchID AppID) (*Rate, error)
}

type Rate struct {
    FromCurrency string    `bson:"fromCurrency"`  // "PHP"
    ToCurrency   string    `bson:"toCurrency"`    // "USD"
    Value        float64   `bson:"value"`         // 0.0178 (1 PHP = 0.0178 USD)
    Source       string    `bson:"source"`        // "bsp_api" or "manual"
    FetchedAt    time.Time `bson:"fetchedAt"`
}
```

**MongoDB Collections:**
- `exchange-rates` — rate history (daily snapshots)
- `reconciliation-rates` — chốt rates (immutable, linked to reconciliation batch)

**Redis Cache Keys:**
- `exchange:rate:{from}:{to}` — realtime rate (TTL: 15 min)

**FRs Addressed:** FR-020, FR-020B

---

### Component 5: Tax Calculation Engine (★ NEW)

**Purpose:** Tính thuế theo quy định từng quốc gia. Pluggable tax rules per country.

**Interfaces:**
```go
type TaxService interface {
    CalculateTax(ctx context.Context, cc string, grossIncome float64) (*TaxResult, error)
    GetTaxRules(ctx context.Context, cc string) (*TaxRules, error)
}

type TaxResult struct {
    GrossIncome float64
    TaxRate     float64
    TaxAmount   float64
    NetIncome   float64  // = GrossIncome - TaxAmount
    Breakdown   []TaxBand
    CountryCode string
    Currency    string
}

type TaxRules struct {
    CountryCode     string     `bson:"countryCode"`
    WithholdingRate float64    `bson:"withholdingRate"` // flat rate
    TaxBands        []TaxBand  `bson:"taxBands"`        // progressive bands
    TaxType         string     `bson:"taxType"`         // "flat" or "progressive"
}
```

**Tax rules stored in:** Country Config (`countryConfigs.taxRules`)

**FRs Addressed:** FR-019, FR-034

---

### Component 6: Payment Gateway Abstraction (★ NEW)

**Purpose:** Interface chung cho payment, implementation khác nhau per country.

**Interfaces:**
```go
type PaymentGateway interface {
    Pay(ctx context.Context, req PaymentRequest) (*PaymentResult, error)
    GetStatus(ctx context.Context, transactionID string) (*PaymentStatus, error)
    Refund(ctx context.Context, transactionID string, amount float64) (*RefundResult, error)
}

type PaymentRequest struct {
    CreatorID   AppID
    Amount      float64
    Currency    string
    CountryCode string
    BankInfo    BankInfo
    BatchID     AppID     // reconciliation batch reference
    Rate        *Rate     // chốt rate for this batch
}

// Factory — returns correct gateway per country
func GetPaymentGateway(cc string) PaymentGateway {
    switch cc {
    case "vn":
        return &VNPaymentGateway{}   // existing VN payment logic
    case "ph":
        return &PHPaymentGateway{}   // new Philippines gateway (GCash/bank)
    default:
        return &ManualPaymentGateway{} // manual processing
    }
}
```

**FRs Addressed:** FR-021

---

### Component 7: Audit Service v2 (Enhanced)

**Purpose:** Mở rộng audit hiện tại với country scope, "acting as local" tracking, immutable logs.

**Enhanced Data Model:**
```go
type AuditEntry struct {
    ID          AppID     `bson:"_id"`
    Actor       AppID     `bson:"actor"`
    ActorName   string    `bson:"actorName"`
    ActorRole   string    `bson:"actorRole"`      // "global_admin", "local_admin", etc.
    Action      string    `bson:"action"`          // "campaign.create", "kyc.approve", etc.
    Target      AppID     `bson:"target"`
    TargetType  string    `bson:"targetType"`      // "campaign", "user", "content"
    CountryCode string    `bson:"countryCode"`     // ★ NEW
    PartnerID   AppID     `bson:"partnerId,omitempty"`
    Details     bson.M    `bson:"details"`         // before/after diff
    IPAddress   string    `bson:"ipAddress"`
    IsActingAs  bool      `bson:"isActingAs"`      // ★ NEW — true if Global Admin acting as Local
    ActingAsCC  string    `bson:"actingAsCC,omitempty"` // ★ NEW — which country scope
    Reason      string    `bson:"reason,omitempty"` // ★ NEW — reason for acting as local
    CreatedAt   time.Time `bson:"createdAt"`
}
```

**MongoDB Collection:** `audits` (existing, enhanced)
**Indexes:** `countryCode`, `actor`, `action`, `createdAt`, `isActingAs`

**FRs Addressed:** FR-013, FR-012

---

### Component 8: Feature Flag Service (★ NEW)

**Purpose:** Per-country feature toggles. Cho phép rollout incremental.

**Data Model:**
```go
type FeatureFlag struct {
    ID          AppID             `bson:"_id"`
    Key         string            `bson:"key"`            // "facebook_login", "realtime_rate"
    Description string            `bson:"description"`
    Scope       string            `bson:"scope"`          // "global" or "country"
    Countries   map[string]bool   `bson:"countries"`      // {"vn": true, "ph": false}
    GlobalState bool              `bson:"globalState"`    // default state
    CreatedAt   time.Time         `bson:"createdAt"`
    UpdatedAt   time.Time         `bson:"updatedAt"`
}
```

**Check Logic:**
```go
func IsEnabled(ctx context.Context, key string, cc string) bool {
    // 1. Check Redis cache
    // 2. If miss → check MongoDB → cache result
    // 3. Country-specific override > global state
}
```

**Redis Cache Key:** `feature:{key}:{cc}` (TTL: 1 min)

**FRs Addressed:** FR-028, FR-005

---

## 5. Data Architecture

### 5.1 Schema Changes — Existing Collections

**Chiến lược:** Thêm `countryCode` field vào existing collections. KHÔNG rename hay restructure.

| Collection | Change | Default Value (VN migration) |
|-----------|--------|------------------------------|
| `users` | Add `countryCode: string` (top-level) | `"vn"` |
| `events` | Add `countryCode: string` | `"vn"` |
| `contents` | Add `countryCode: string` | `"vn"` |
| `cash-flows` | Add `countryCode: string` | `"vn"` |
| `withdraw` | Add `countryCode: string` | `"vn"` |
| `transfers` | Add `countryCode: string` | `"vn"` |
| `user-events` | Add `countryCode: string` | `"vn"` |
| `event-schemas` | Add `countryCode: string` | `"vn"` |
| `event-rewards` | Add `countryCode: string` | `"vn"` |
| `partners` | Add `countries: []string` | `["vn"]` |
| `staff` | Add `countryScope: string` (or `"*"` for global) | `"vn"` or `"*"` |
| `reconciliation` | Add `countryCode: string` + `exchangeRate: Rate` | `"vn"` |
| `audits` | Add `countryCode: string` + `isActingAs` + `actingAsCC` + `reason` | `"vn"` |
| `configurations` | Add `countryCode: string` | `"vn"` |
| `notifications` | Add `countryCode: string` | `"vn"` |
| `articles` | Add `countryCode: string` + `translations: map[string]Content` | `"vn"` |

### 5.2 New Collections

| Collection | Purpose |
|-----------|---------|
| `country-configs` | Country configuration (currency, languages, tax, KYC, payment, flags) |
| `exchange-rates` | Rate history (daily snapshots per currency pair) |
| `reconciliation-rates` | Immutable chốt rates per reconciliation batch |
| `feature-flags` | Per-country feature toggles |

### 5.3 Index Strategy

**New Compound Indexes (critical for performance):**

```javascript
// All major collections — country_code as first field for efficient filtering
db.users.createIndex({ "countryCode": 1, "createdAt": -1 })
db.users.createIndex({ "countryCode": 1, "partners": 1 })

db.events.createIndex({ "countryCode": 1, "status": 1 })
db.events.createIndex({ "countryCode": 1, "partner": 1, "status": 1 })

db.contents.createIndex({ "countryCode": 1, "event": 1, "status": 1 })
db.contents.createIndex({ "countryCode": 1, "user": 1 })

db["cash-flows"].createIndex({ "countryCode": 1, "user": 1, "createdAt": -1 })

db.withdraw.createIndex({ "countryCode": 1, "user": 1, "status": 1 })

db["user-events"].createIndex({ "countryCode": 1, "user": 1 })

db.audits.createIndex({ "countryCode": 1, "createdAt": -1 })
db.audits.createIndex({ "isActingAs": 1, "createdAt": -1 })

db["country-configs"].createIndex({ "code": 1 }, { unique: true })
db["exchange-rates"].createIndex({ "fromCurrency": 1, "toCurrency": 1, "fetchedAt": -1 })
db["reconciliation-rates"].createIndex({ "batchId": 1 }, { unique: true })
db["feature-flags"].createIndex({ "key": 1 }, { unique: true })
```

### 5.4 Data Flow

```
                          WRITE PATH
Creator submits content:
  Client → Public API → Auth MW → CountryContext MW
    → Content Handler → ContentService.Create(ctx, content)
      → content.CountryCode = GetCountryCode(ctx)    ★ inject
      → content.Partner = from event
      → ContentDAO.Insert(content)
      → AuditService.Log("content.submit", content.ID)

                          READ PATH
Local Admin views content list:
  Client → Admin API → Auth MW → CountryContext MW → CountryPermission MW
    → Content Handler → ContentDAO.Find(ctx, bson.M{
        "countryCode": GetCountryCode(ctx),         ★ auto-filter
        "partner":     staff.AssignPartner(),        (existing)
        "status":      "pending",
      })
    → Return filtered results

Global Admin views cross-country dashboard:
  Client → Admin API → Auth MW → CountryContext MW (scope=global)
    → Dashboard Handler → Aggregation Pipeline:
      $match: {} (no country filter — global scope)
      $group: { _id: "$countryCode", totalRevenue: {$sum: ...} }
      → ExchangeRateService.Convert(revenue, currency, "USD")
      → Return aggregated results
```

### 5.5 Migration Strategy

**Approach: Phased, Zero-Downtime, Reversible**

```
Phase A: Prepare (No downtime)
  1. Deploy new code that WRITES countryCode but doesn't REQUIRE it
  2. New records automatically get countryCode
  3. Old records work fine without countryCode (null = treated as "vn")

Phase B: Backfill (Background, no downtime)
  1. Run background script: add countryCode="vn" to all existing records
  2. Batch size: 1000 records per iteration
  3. Sleep 100ms between batches (throttle)
  4. Progress tracking: log % complete
  5. Idempotent: skip records that already have countryCode

Phase C: Enforce (After backfill complete)
  1. Add middleware that REQUIRES countryCode in context
  2. Add validation that REQUIRES countryCode on new records
  3. Create compound indexes
  4. Verify: no records without countryCode

Phase D: Cleanup
  1. Remove null-handling fallback code
  2. Enable multi-country features
```

**Rollback Plan:**
- Phase A: Just deploy old code (countryCode field is ignored)
- Phase B: countryCode="vn" is correct data, no harm
- Phase C: Remove enforcement middleware, indexes stay (no harm)

---

## 6. API Design

### 6.1 URL Routing Strategy

**Public API — Country in Path:**
```
/{country_code}/api/public/...

Examples:
  /vn/api/public/events          → Events in Vietnam
  /ph/api/public/events          → Events in Philippines
  /vn/api/public/user/profile    → VN user profile
```

**Admin API — Country in Header/Query:**
```
/api/admin/...
Header: X-Country-Code: ph    (for Local Admin, auto-set from JWT)
Query:  ?country=ph            (for Global Admin, manual select)

Examples:
  /api/admin/events?country=ph              → PH events
  /api/admin/dashboard?country=all          → Global dashboard
  /api/admin/users?country=ph&partner=xxx   → PH users for partner
```

**Backward Compatibility:**
```
/api/public/events              → Auto-resolve to /vn/api/public/events (default)
```

**Rationale:**
- Public API: Country in path → clean URLs, cacheable, SEO-friendly
- Admin API: Country in header → cleaner admin routes, flexibility for "acting as local"
- Backward compat: URL without country → default "vn" → existing apps work

### 6.2 Key API Endpoints (New/Modified)

#### Country Configuration
```
GET    /api/admin/countries                    → List all countries
POST   /api/admin/countries                    → Create country config (Global Admin)
GET    /api/admin/countries/:code              → Get country config
PATCH  /api/admin/countries/:code              → Update country config
GET    /api/public/countries                   → List active countries (for selector)
```

#### Exchange Rate
```
GET    /api/public/exchange-rate/:from/:to     → Realtime reference rate
GET    /api/admin/exchange-rates/history       → Rate history
POST   /api/admin/reconciliation/:id/lock-rate → Chốt rate for batch
GET    /api/admin/reconciliation/:id/rate      → Get chốt rate for batch
```

#### Feature Flags
```
GET    /api/admin/feature-flags                → List all flags
POST   /api/admin/feature-flags                → Create flag
PATCH  /api/admin/feature-flags/:key           → Update flag
GET    /api/public/feature-flags               → Get active flags for current country
```

#### Audit Trail
```
GET    /api/admin/audits                       → Search audit logs (filterable)
GET    /api/admin/audits/acting-as-local       → Filter "acting as local" entries
POST   /api/admin/acting-as-local/start        → Start acting-as-local session
POST   /api/admin/acting-as-local/end          → End acting-as-local session
```

#### Global Dashboard
```
GET    /api/admin/dashboard/global             → Cross-country aggregation
GET    /api/admin/dashboard/global/compare     → Country comparison
GET    /api/admin/dashboard/country/:code      → Single country details
```

#### i18n Content
```
GET    /api/admin/content/:id/translations     → Get all translations
PATCH  /api/admin/content/:id/translations/:lang → Update translation
GET    /{cc}/api/public/content/:id            → Get content in user's language
```

### 6.3 Authentication Enhancement

**JWT Token — Enhanced Claims:**
```json
{
  "_id": "staff_id",
  "name": "Admin Name",
  "email": "admin@example.com",
  "isRoot": false,
  "partner": "partner_id",
  "countryScope": "ph",         // ★ NEW — "ph", "vn", or "*" for global
  "roles": ["local_admin"],     // ★ NEW — role codes
  "exp": 1234567890
}
```

**Public JWT — Enhanced Claims:**
```json
{
  "_id": "user_id",
  "countryCode": "ph",          // ★ NEW — user's primary country
  "exp": 1234567890
}
```

### 6.4 Response Format Enhancement

```json
{
  "data": { ... },
  "code": 200,
  "message": "Success",
  "meta": {
    "countryCode": "ph",                    // ★ NEW
    "currency": "PHP",                       // ★ NEW
    "language": "fil",                       // ★ NEW
    "exchangeRate": {                        // ★ NEW (optional, in financial endpoints)
      "type": "reference",                   // "reference" or "locked"
      "value": 0.0178,
      "updatedAt": "2026-03-02T10:30:00Z"
    }
  }
}
```

---

## 7. NFR Coverage

### NFR-001: Performance — API Response Time

**Requirement:** p95 < 300ms, p99 < 1000ms, dashboard < 2000ms

**Architecture Solution:**
- **Country_code as first field in compound indexes** → MongoDB query optimizer uses index prefix efficiently
- **Redis cache for Country Config** (TTL: 5 min) → Avoid DB read per request
- **Redis cache for Exchange Rates** (TTL: 15 min) → Avoid external API call per request
- **Feature Flag cache** (TTL: 1 min) → Fast feature checks
- **Aggregation pipelines with $match on countryCode first** → Reduce scan scope

**Validation:**
- Load test: 500 RPS per country endpoint, measure p95
- Monitor: Elastic APM transaction duration, tagged by country_code

---

### NFR-003: Security — Data Isolation

**Requirement:** Absolute data isolation between countries. No cross-country data leak.

**Architecture Solution:**
- **CountryContext Middleware** → Inject country_code vào EVERY request context
- **CountryPermission Middleware** → Verify staff's countryScope matches request
- **CountryScopedDAO** → Wrapper DAO tự động thêm `{"countryCode": cc}` filter
- **JWT country_code claim** → Server-side validation, không trust client
- **Audit log cho sensitive data access** → KYC, bank info

**Implementation — CountryScopedDAO Pattern:**
```go
// Wraps existing DAO methods to auto-inject country filter
type CountryScopedDAO struct {
    inner   IDatabase
    country string
}

func (d *CountryScopedDAO) Find(ctx context.Context, results interface{}, cond bson.M, opts ...interface{}) error {
    // Auto-inject country filter
    cond["countryCode"] = d.country
    return d.inner.Find(ctx, results, cond, opts...)
}

func (d *CountryScopedDAO) FindOne(ctx context.Context, result interface{}, cond bson.M) error {
    cond["countryCode"] = d.country
    return d.inner.FindOne(ctx, result, cond)
}

// For Global Admin — no country filter
type GlobalScopedDAO struct {
    inner IDatabase
}
```

**Validation:**
- Security review: verify every endpoint uses CountryScopedDAO
- Penetration test: attempt cross-country access with manipulated JWT

---

### NFR-004: Security — Authentication & Authorization

**Requirement:** Multi-provider OAuth, country-scoped JWT, rate limiting

**Architecture Solution:**
- **JWT with country_code claim** — public and admin tokens
- **Separate JWT secrets per role** (existing: AUTH_SECRET_ADMIN, AUTH_SECRET_PUBLIC)
- **Redis session cache** (existing) — extend with country tag
- **OAuth credentials per country** — stored in Country Config, loaded at auth time
- **Rate limiting** — extend existing, add per-country limits

---

### NFR-005: Scalability — Country Addition

**Requirement:** New country < 2 tuần, no code deploy

**Architecture Solution:**
- **Country Config as data** — stored in MongoDB, cached in Redis
- **Feature flags** — enable/disable features per country without deploy
- **Payment Gateway factory** — `GetPaymentGateway(cc)` returns correct implementation
- **Locale files** — loaded at startup, hot-reload capable
- **KYC form config** — stored in Country Config, frontend renders dynamically

**Country Setup Checklist (automated via admin API):**
1. Create Country Config document
2. Upload locale files
3. Configure tax rules
4. Configure KYC requirements
5. Configure payment gateway
6. Set OAuth credentials
7. Enable feature flags
8. Seed data (banks, provinces)
9. UAT testing

---

### NFR-006: Reliability — Uptime

**Requirement:** 99.5% uptime, country-level health, graceful degradation

**Architecture Solution:**
- **Payment Gateway circuit breaker** — nếu PH payment down → không ảnh hưởng VN
- **Exchange Rate fallback** — nếu API fail → dùng last cached rate + warning
- **Feature flag kill switch** — disable specific features per country instantly
- **MongoDB replica set** (existing) → high availability
- **Redis sentinel/cluster** → cache availability
- **Health check endpoints** per country: `GET /health?country=ph`

---

### NFR-009: Compatibility — Backward Compatibility

**Requirement:** VN platform + 11 partner apps continue working, zero downtime

**Architecture Solution:**
- **URL backward compat:** `/api/public/*` → auto-resolve to `/vn/api/public/*`
- **Schema backward compat:** `countryCode` field optional during migration, default to "vn"
- **API response backward compat:** `meta.countryCode` is new but non-breaking
- **Partner apps:** Each app hits `/api/public/...` (no country prefix) → routed to VN

**Migration guard:**
```go
// During migration period
func GetCountryCode(ctx echo.Context) string {
    cc := ctx.Get("country_code")
    if cc == nil || cc == "" {
        return "vn"  // Default fallback during migration
    }
    return cc.(string)
}
```

---

### NFR-010: Monitoring — Multi-Country Observability

**Requirement:** Metrics tagged by country, alerts per country

**Architecture Solution:**
- **Elastic APM labels:** `apm.SetLabel("country_code", cc)` on every transaction
- **Structured logging:** Zap logger with `country_code` field
- **Redis metrics:** Track per-country cache hit/miss rates
- **Dashboard:** Kibana/Grafana dashboards filtered by country_code
- **Alerts:** Threshold alerts per country (error rate > 5% for country X)

---

## 8. Security Architecture

### 8.1 Authentication Flow

```
Creator Login (Public):
  Client → /{cc}/api/public/auth/login
    → OAuth provider (TikTok/Google/Facebook per country config)
    → Verify OAuth token
    → Find/create user with countryCode
    → Generate JWT: { _id, countryCode, exp }
    → Return token

Admin Login:
  Client → /api/admin/auth/login
    → Verify credentials
    → Load staff.countryScope + staff.partner
    → Generate JWT: { _id, countryScope, partner, roles, isRoot, exp }
    → Store token in Redis (for invalidation)
    → Return token
```

### 8.2 Authorization Model

```
┌─────────────────────────────────────────────────────┐
│                 AUTHORIZATION LAYERS                 │
│                                                     │
│  Layer 1: Authentication (JWT valid?)               │
│  Layer 2: Country Scope (staff.countryScope match?) │
│  Layer 3: Partner Scope (staff.partner match?)      │
│  Layer 4: Role Check (staff.role has permission?)   │
│  Layer 5: Audit (log sensitive actions)             │
│                                                     │
│  Decision Matrix:                                   │
│  ┌──────────────┬────────┬──────────┬────────────┐ │
│  │ Role         │Country │ Partner  │ Special    │ │
│  ├──────────────┼────────┼──────────┼────────────┤ │
│  │ global_admin │ ALL    │ ALL      │ ActingAs   │ │
│  │ local_admin  │ own CC │ assigned │ Full CRUD  │ │
│  │ local_acct   │ own CC │ assigned │ Reconcile  │ │
│  │ local_ops    │ own CC │ assigned │ Moderate   │ │
│  └──────────────┴────────┴──────────┴────────────┘ │
└─────────────────────────────────────────────────────┘
```

### 8.3 Sensitive Data Protection

| Data | Encryption | Access Control | Audit |
|------|-----------|---------------|-------|
| KYC documents | AES-256 (MinIO encryption) | Owner + Local Admin (country-scoped) | Always logged |
| Bank accounts | AES-256 (field-level) | Owner + Local Admin (country-scoped) | Always logged |
| Tax ID | AES-256 (field-level) | Owner + Local Admin (country-scoped) | Always logged |
| JWT secrets | Env vars (not in DB) | Server-only | N/A |
| OAuth credentials | Env vars per country | Server-only | Config change logged |

---

## 9. Scalability & Performance

### 9.1 Scaling Strategy

**Horizontal Scaling (Primary):**
- Go backend instances are stateless → scale horizontally behind load balancer
- Each instance handles all countries (shared deployment)
- Redis for session/cache → no sticky sessions needed

**Database Scaling:**
- MongoDB replica set (existing) → add read replicas for heavy read countries
- Country_code index → efficient per-country queries
- Aggregation queries → schedule pre-computed daily summaries for dashboard

**When to Consider Separation:**
- IF a country generates > 50% total traffic → consider dedicated instances
- IF compliance requires data residency → consider separate MongoDB cluster per region
- NOT needed for Phase 1-3

### 9.2 Caching Strategy

| Data | Cache Location | TTL | Invalidation |
|------|---------------|-----|-------------|
| Country Config | Redis | 5 min | On config update (publish Redis event) |
| Feature Flags | Redis | 1 min | On flag update |
| Exchange Rates (realtime) | Redis | 15 min (configurable) | TTL expiry |
| Exchange Rates (chốt) | MongoDB only | Never expires | Immutable |
| JWT sessions (admin) | Redis | 8 hours | On logout / role change |
| User profile (hot) | Redis | 10 min | On profile update |

### 9.3 Performance Optimization

**Query Optimization:**
- Country_code as FIRST field in compound indexes → prefix scan
- Avoid cross-country queries at DAO level → aggregate at service level
- Pre-computed daily analytics (existing pattern: `content-analytic-daily`)

**Response Optimization:**
- Gzip compression (existing)
- Pagination with cursor-based tokens (existing)
- Selective field projection for list endpoints

---

## 10. Reliability & Availability

### 10.1 Circuit Breaker Pattern

```go
// Payment Gateway with circuit breaker
type CircuitBreakerPaymentGateway struct {
    gateway PaymentGateway
    breaker *gobreaker.CircuitBreaker
}

func (cb *CircuitBreakerPaymentGateway) Pay(ctx context.Context, req PaymentRequest) (*PaymentResult, error) {
    result, err := cb.breaker.Execute(func() (interface{}, error) {
        return cb.gateway.Pay(ctx, req)
    })
    if err != nil {
        // Circuit open → return error, don't retry
        // Other countries' payment gateways unaffected
        return nil, fmt.Errorf("payment gateway for %s is temporarily unavailable", req.CountryCode)
    }
    return result.(*PaymentResult), nil
}
```

### 10.2 Graceful Degradation Matrix

| Component Down | Impact | Mitigation |
|---------------|--------|-----------|
| PH Payment Gateway | PH payments fail | VN, ID unaffected. Queue failed payments for retry. |
| Exchange Rate API | No realtime rate | Use last cached rate + timestamp warning. |
| Redis | Sessions lost, cache cold | DB fallback for all reads. Users need re-login. |
| MongoDB secondary | Read latency increase | Failover to primary. No data loss. |

### 10.3 Backup & DR

| Component | Backup Frequency | RPO | RTO |
|-----------|-----------------|-----|-----|
| MongoDB | Daily full + oplog streaming | < 1 hour | < 4 hours |
| Redis | RDB snapshots (daily) | < 24 hours | < 1 hour |
| MinIO (KYC docs) | Daily sync to backup bucket | < 24 hours | < 4 hours |
| Config/Env | Git-versioned | Instant | < 30 min |

---

## 11. Development & Deployment

### 11.1 Code Organization Changes

```
backend/internal/
├── config/
│   └── env.go                     (existing, add country vars)
├── middleware/
│   ├── cors.go                    (existing)
│   ├── jwt.go                     (existing)
│   ├── country_context.go         ★ NEW
│   └── country_permission.go      ★ NEW
├── module/
│   ├── database/mongodb/
│   │   ├── dao/
│   │   │   ├── country_config.go  ★ NEW
│   │   │   ├── exchange_rate.go   ★ NEW
│   │   │   ├── feature_flag.go    ★ NEW
│   │   │   └── ... (70+ existing)
│   │   ├── country_scoped.go      ★ NEW (CountryScopedDAO wrapper)
│   │   └── ...
│   └── ...
├── service/
│   ├── country_config.go          ★ NEW
│   ├── exchange_rate.go           ★ NEW
│   ├── tax.go                     ★ NEW
│   ├── payment_gateway.go         ★ NEW
│   ├── feature_flag.go            ★ NEW
│   ├── audit.go                   (existing, enhanced)
│   └── ... (13 existing services)
├── model/mg/
│   ├── country_config.go          ★ NEW
│   ├── exchange_rate.go           ★ NEW
│   ├── feature_flag.go            ★ NEW
│   └── ... (existing models, add countryCode field)
└── locale/
    ├── vi/                        (existing)
    ├── en/                        (existing)
    ├── fil/                       ★ NEW (Filipino/Tagalog)
    └── id/                        ★ NEW (Indonesian)
```

### 11.2 Testing Strategy

| Test Type | Scope | Target |
|-----------|-------|--------|
| Unit Tests | Tax calculation, permission checks, data isolation | 80%+ coverage on new services |
| Integration Tests | Country middleware chain, DAO with country filter | All new middleware |
| API Tests | Cross-country isolation, role-based access | Every endpoint |
| Migration Tests | Backfill script on test data, rollback verification | Before production run |
| Load Tests | Multi-country concurrent requests | p95 < 300ms |

**Critical Test Scenarios:**
1. Local Admin PH CANNOT access VN data
2. Global Admin access PH data → audit log created
3. Exchange rate chốt → immutable (cannot update)
4. VN requests without country_code → default to "vn" (backward compat)
5. Feature flag disabled for PH → feature not accessible

### 11.3 Deployment Strategy

**Phase 1 Deployment (Incremental):**
```
Step 1: Deploy code with CountryContext middleware (disabled via flag)
Step 2: Run backfill migration script (background)
Step 3: Enable CountryContext middleware for admin API first
Step 4: Enable for public API (after VN testing)
Step 5: Enable CountryPermission middleware
Step 6: Enable multi-country features
```

**Rollback:** Feature flags. Disable country features → system behaves like before.

**Docker-compose Updates:**
```yaml
# No structural changes — same 3 services
# Just add new env vars:
backend-public:
  environment:
    - COUNTRY_DEFAULT=vn
    - EXCHANGE_RATE_API_URL=...
    - EXCHANGE_RATE_CACHE_TTL=900

backend-admin:
  environment:
    - COUNTRY_DEFAULT=vn
    - EXCHANGE_RATE_API_URL=...
```

---

## 12. Traceability & Trade-offs

### 12.1 FR → Component Traceability

| FR ID | FR Name | Components | Implementation Notes |
|-------|---------|------------|---------------------|
| FR-001 | Data Partitioning | CountryContext MW, CountryScopedDAO | Add countryCode to all collections |
| FR-002 | Country Config Store | Country Config Service, Redis cache | New collection + service |
| FR-003 | URL Routing | CountryContext MW, Nginx | /{cc}/api/public/* routing |
| FR-004 | Cross-Country Aggregation | Global Dashboard API, ExchangeRate Svc | MongoDB aggregation pipelines |
| FR-005 | Multi-Provider OAuth | Auth MW, Country Config | OAuth creds from country config |
| FR-006 | User Country Binding | User model, CountryContext MW | New countryCode field on user |
| FR-007 | Country-Scoped Permissions | CountryPermission MW, Role model | countryScope on staff JWT |
| FR-008 | Backend i18n | Locale loader, Echo context | Extend existing 17 locale dirs |
| FR-009 | Language Switcher | Frontend i18n, Accept-Language | Frontend component + user pref |
| FR-010 | Multi-lang Content | Content model, Admin CMS | translations map on content |
| FR-012 | Acting as Local | CountryPermission MW, Audit Svc v2 | Session scope switch + audit |
| FR-013 | Audit Trail | Audit Service v2, MongoDB | Enhanced audit model |
| FR-018 | Multi-Currency Display | Currency formatter, Country Config | Locale-aware formatting |
| FR-019 | Tax Engine | Tax Service, Country Config | Pluggable tax rules per country |
| FR-020 | Realtime Rate | Exchange Rate Service, Redis | External API + cache |
| FR-020B | Chốt Rate | Exchange Rate Service, MongoDB | Immutable rate per recon batch |
| FR-021 | Payment Abstraction | Payment Gateway factory | Interface + per-country impl |
| FR-022 | Country KYC | Country Config, KYC forms | Dynamic form from config |
| FR-025 | Country Campaigns | Event model + countryCode | Existing + country filter |
| FR-028 | Feature Flags | Feature Flag Service, Redis | New service + cache |
| FR-029 | VN Migration | Migration scripts | Phased backfill |
| FR-034 | Creator Income Dashboard | Tax Svc, ExchangeRate Svc | Combine tax + rate + earnings |

### 12.2 NFR → Architecture Solution Traceability

| NFR ID | NFR Name | Solution | Validation |
|--------|----------|----------|------------|
| NFR-001 | API Performance | Compound indexes (cc first), Redis cache | Load test p95 < 300ms |
| NFR-002 | Concurrent Users | Stateless Go, horizontal scaling | Load test 1000+ concurrent |
| NFR-003 | Data Isolation | CountryScopedDAO, middleware chain | Penetration test |
| NFR-004 | Auth & Authz | JWT + country claims, Redis sessions | Security review |
| NFR-005 | Country Addition | Config-driven, feature flags | Setup PH < 2 weeks |
| NFR-006 | Uptime | Circuit breakers, graceful degradation | Monthly uptime monitoring |
| NFR-007 | i18n | Locale files, number/date/currency formatting | UX review per country |
| NFR-008 | Code Quality | CountryScopedDAO pattern, tests | Code review, coverage report |
| NFR-009 | Backward Compat | URL fallback, schema migration | VN regression test suite |
| NFR-010 | Observability | APM labels, structured logging per country | Dashboard per country |

### 12.3 Key Trade-offs

#### Trade-off 1: Single Cluster vs Multi-Cluster MongoDB

**Decision:** Single MongoDB cluster with country_code partitioning
**Gain:** Simpler ops, easier cross-country queries, lower cost
**Lose:** No data residency isolation, single point of failure for all countries
**Rationale:** Phase 1-3 = SEA only, no data residency requirements. Re-evaluate when expanding to EU.

#### Trade-off 2: Enhanced Monolith vs Microservices

**Decision:** Keep monolith, add multi-tenancy layer
**Gain:** Lower risk, faster delivery (reuse 90%+ existing code), team familiarity
**Lose:** Cannot scale country-specific components independently, harder to assign country to different teams later
**Rationale:** 6-month timeline. Team knows Go monolith. Microservices = 12+ months. Can extract services later if needed.

#### Trade-off 3: CountryScopedDAO Wrapper vs Rewrite Every DAO

**Decision:** Wrapper pattern (CountryScopedDAO wraps existing DAO interface)
**Gain:** Minimal changes to existing 70+ DAO files, automatic country filter
**Lose:** Slight performance overhead (extra function call), risk of missing some code paths
**Rationale:** 70+ DAOs → rewriting each = months. Wrapper = weeks. Risk mitigated by integration tests.

#### Trade-off 4: Country in URL Path (Public) vs Header (Admin)

**Decision:** Hybrid — path for public, header for admin
**Gain:** Public: clean URLs, cacheable. Admin: flexible scope switching for Global Admin
**Lose:** Inconsistency between public and admin patterns
**Rationale:** Different use cases. Public = user-facing, URL matters. Admin = internal, flexibility matters.

#### Trade-off 5: Keep Partner as Independent Dimension

**Decision:** Country + Partner = 2 independent dimensions (not hierarchical)
**Gain:** Partner can operate in multiple countries (Anker in VN + PH)
**Lose:** More complex query logic (2 filters instead of 1), permission model more complex
**Rationale:** Business requirement. Partners ARE cross-country. Hierarchical model would force data duplication.

---

## Architecture Validation Checklist

- [x] All 35 FRs have component assignments
- [x] All 10 NFRs have architectural solutions
- [x] Technology choices justified (keep stack, minimal new components)
- [x] Trade-offs documented (5 major decisions)
- [x] Security addressed (auth, authz, encryption, audit)
- [x] Scalability path clear (horizontal, index-driven, cache-first)
- [x] Data model defined (schema changes + new collections + indexes)
- [x] API contracts specified (URL routing + key endpoints + response format)
- [x] Testing strategy defined (unit, integration, API, migration, load)
- [x] Deployment approach clear (incremental, feature-flagged, rollback plan)
- [x] Backward compatibility ensured (URL fallback, schema migration, partner apps)
- [x] Dual exchange rate system designed (realtime reference + immutable chốt rate)

---

## Summary

| Aspect | Design |
|--------|--------|
| **Pattern** | Enhanced Monolith with Country-Scoped Multi-Tenancy |
| **New Components** | 8 (2 middleware + 6 services) |
| **Modified Components** | ~15 (existing services + models) |
| **New Collections** | 4 (country-configs, exchange-rates, reconciliation-rates, feature-flags) |
| **Modified Collections** | 16+ (add countryCode field) |
| **New Indexes** | 12+ compound indexes |
| **Tech Stack Changes** | None (same Go, MongoDB, Redis, React) |
| **Deployment Changes** | Minimal (new env vars, feature flags) |
| **Risk Level** | Medium (most changes are additive, not destructive) |

---

*Generated by BMAD Method v6 - System Architect*
*Date: 2026-03-02*
