# at-core Architecture

> Kiến trúc kỹ thuật tổng thể của at-core Profile Hub.
>
> Cập nhật: 2026-03-11
>
> Tài liệu liên quan:
> - [business-overview.md](business-overview.md) - Tổng quan business (non-tech)
> - [architecture-gap-analysis.md](architecture-gap-analysis.md) - Gap analysis từ codebase hiện tại

---

## 1. System Overview

at-core là nền tảng quản lý influencer profile, đóng vai trò **Profile Hub** trung tâm kết nối giữa các Partner và Vendor phân tích.

```
┌──────────────────────────────────────────────────────────────────────┐
│                          at-core PROFILE HUB                         │
│                                                                      │
│  INGESTION          CORE                        OUTPUT               │
│                                                                      │
│  Partner ──┐    ┌──────────────┐            ┌──────────────┐         │
│  Submit    │    │  Ingestion   │            │  Partner API │──► TCB  │
│            ├───►│  Service     │            │  (scoped)    │──► VF   │
│  Creator ──┤    │              │    ┌───────│              │──► AMB  │
│  Self-Svc  │    │ - Validate   │    │       └──────────────┘         │
│            │    │ - Normalize  │    │                                 │
│  Admin ────┤    │ - Conflict   │    │       ┌──────────────┐         │
│  Import    │    │   Resolve    │    │       │  Pool Search │──► Any  │
│            │    └──────┬───────┘    │       │  (public)    │  Partner│
│  IM ───────┘           │            │       └──────────────┘         │
│  Webhook          ┌────▼────────┐   │                                │
│                   │  Profile    │   │       ┌──────────────┐         │
│                   │  Store      │───┘       │  Matching    │──► IM   │
│                   │             │           │  (proxy)     │  Vendor │
│                   │ - Base      │           └──────────────┘         │
│                   │ - Partner   │                                     │
│                   │   Data      │           ┌──────────────┐         │
│                   │ - Access    │           │  Admin API   │──► Ops  │
│                   │ - History   │───────────│  (full view) │──► Admin│
│                   └─────────────┘           └──────────────┘         │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### Các bên tương tác

| Bên | Vai trò | Giao tiếp |
|-----|---------|-----------|
| **Partner** (TCB, Vinfast, Ambassabor) | Đóng góp & tiêu thụ profile data | REST API (API Key / JWT) |
| **Vendor IM** (Influence Meter) | Phân tích, chấm điểm, matching influencer | REST API + Webhook |
| **Admin / Operations** | Quản trị hệ thống, xác minh dữ liệu | Admin API (JWT + RBAC) |

---

## 2. Architecture Pattern

**Clean / Hexagonal Architecture** với domain-driven design.

```
┌─────────────────────────────────────────────────────────┐
│                      API Layer                           │
│  Handlers (HTTP) + Middleware (Auth, Validation, CORS)   │
└────────────────────────┬────────────────────────────────┘
                         │ calls
┌────────────────────────▼────────────────────────────────┐
│                   Domain Layer                           │
│  Services (business logic) + Models + Interfaces         │
└────────────────────────┬────────────────────────────────┘
                         │ implements
┌────────────────────────▼────────────────────────────────┐
│                 Infrastructure Layer                     │
│  MongoDB repos + Redis cache + IM client + Webhook       │
└─────────────────────────────────────────────────────────┘
```

**Nguyên tắc:**
- Domain layer **không** phụ thuộc infrastructure (dùng interfaces)
- Handler **không** chứa business logic, chỉ parse request → gọi service → format response
- Infrastructure implement domain interfaces, inject qua DI trong `main.go`

---

## 3. Technology Stack

| Layer | Technology | Lý do |
|-------|-----------|-------|
| **Language** | Go 1.24+ | Performance, strong typing, concurrency |
| **Database** | MongoDB | Flexible schema cho profile data đa dạng |
| **Cache** | Redis | Rate limiting, caching, session |
| **HTTP Framework** | net/http + chi router | Lightweight, Go standard |
| **HTTP Client** | go-retryablehttp + gobreaker | Retry + circuit breaker cho vendor IM |
| **Auth** | JWT (golang-jwt/v5) | Stateless auth cho partner & admin |
| **Validation** | go-playground/validator | Request validation |
| **Password** | bcrypt (cost 12) | Password hashing |
| **Encryption** | AES-256 | Contact info encryption at rest |

---

## 4. Domain Architecture

### 4.1 Domain Map

```
internal/domain/
├── profile/          Profile Hub core: base profile + field-level tracking
├── partnerdata/      Partner-specific enrichment data (isolated per partner)
├── access/           Partner-profile relationship (ai thấy profile nào)
├── enrichment/       Ingestion pipeline + vendor IM enrichment
├── partner/          Partner account management + API key
├── pool/             Influencer pool search (public profiles)
├── admin/            Admin RBAC, session, security, audit
├── quota/            Monthly usage quota per partner
├── subscription/     Subscription tier & feature management
└── webhook/          Webhook event delivery to partners
```

### 4.2 Domain: `profile`

**Mục đích:** Core domain. Quản lý base profile (thông tin công khai) của influencer. Single source of truth.

**Model chính:**

```go
type UnifiedProfile struct {
    ID         primitive.ObjectID `bson:"_id,omitempty"`
    Platform   string             `bson:"platform"`    // tiktok, youtube, facebook, instagram
    ExternalID string             `bson:"externalId"`  // @handle hoặc platform user ID

    // Base profile data (shared, mọi partner đều thấy)
    ProfileData    ProfileData    `bson:"profileData"`
    ProfileMetrics ProfileMetrics `bson:"profileMetrics"`
    Content        []ContentItem  `bson:"content,omitempty"`

    // Scoring (từ vendor IM)
    Score          *ScoreData     `bson:"score,omitempty"`

    // Source tracking: mỗi field có nguồn + confidence
    FieldSources   map[string]FieldSource `bson:"fieldSources,omitempty"`

    // Quality indicators
    Visibility       Visibility `bson:"visibility"`        // PUBLIC | UNLISTED
    CompletenessScore float64   `bson:"completenessScore"` // 0-100
    VerifiedAt       *time.Time `bson:"verifiedAt,omitempty"`
    VerifiedBy       string     `bson:"verifiedBy,omitempty"`

    // Enrichment tracking
    LastEnrichedAt *time.Time `bson:"lastEnrichedAt,omitempty"`
    EnrichmentJobID string    `bson:"enrichmentJobId,omitempty"`

    // Timestamps
    CreatedAt time.Time `bson:"createdAt"`
    UpdatedAt time.Time `bson:"updatedAt"`
}

type ProfileData struct {
    Name       string   `bson:"name"`
    Handle     string   `bson:"handle"`
    Avatar     string   `bson:"avatar,omitempty"`
    Bio        string   `bson:"bio,omitempty"`
    Followers  int64    `bson:"followers"`
    Verified   bool     `bson:"verified"`
    Country    string   `bson:"country,omitempty"`
    Categories []string `bson:"categories,omitempty"`
}

type ProfileMetrics struct {
    EngagementRate float64 `bson:"engagementRate"`
    AvgViews       int64   `bson:"avgViews,omitempty"`
    FollowerRatio  float64 `bson:"followerRatio,omitempty"`
}

type FieldSource struct {
    Source     string    `bson:"source"`     // crawl | partner_xxx | ops_verified | creator_self
    Confidence float64  `bson:"confidence"` // 0.0 - 1.0
    UpdatedAt  time.Time `bson:"updatedAt"`
    UpdatedBy  string    `bson:"updatedBy,omitempty"`
}

type Visibility string
const (
    VisibilityPublic   Visibility = "PUBLIC"
    VisibilityUnlisted Visibility = "UNLISTED"
)
```

**Source confidence hierarchy:**

```
1.0  platform_api      Direct từ TikTok/YouTube API (OAuth verified)
0.9  ops_verified       Operations team xác minh
0.8  partner_verified   Partner xác nhận data đúng
0.7  partner_submitted  Partner gửi vào (chưa verify)
0.6  crawl              Crawl từ vendor IM
0.5  creator_self       Influencer tự khai (qua Ambassabor)
0.3  ml_predicted       ML model predict
```

**Service interface:**

```go
type ProfileServicer interface {
    // CRUD
    GetByID(ctx context.Context, id primitive.ObjectID) (*UnifiedProfile, error)
    GetByPlatformID(ctx context.Context, platform, externalID string) (*UnifiedProfile, error)
    List(ctx context.Context, opts ListOptions) ([]UnifiedProfile, int64, error)

    // Ops override
    UpdateField(ctx context.Context, profileID primitive.ObjectID, field string,
        value interface{}, source FieldSource, reason string) error
    MarkVerified(ctx context.Context, profileID primitive.ObjectID, verifiedBy string) error
    GetChangeHistory(ctx context.Context, profileID primitive.ObjectID,
        opts PaginationOptions) ([]ChangeRecord, int64, error)

    // Quality
    RecalculateCompleteness(ctx context.Context, profileID primitive.ObjectID) (float64, error)
}
```

**MongoDB collection:** `profiles`

**Indexes:**
```
{ platform: 1, externalId: 1 }           unique
{ visibility: 1, completenessScore: -1 }  pool search
{ "profileData.categories": 1 }           category filter
{ createdAt: -1 }                          sorting
```

### 4.3 Domain: `partnerdata`

**Mục đích:** Lưu trữ dữ liệu riêng mà mỗi partner đóng góp cho 1 profile. **Chỉ partner đó mới thấy.**

```go
type PartnerProfileData struct {
    ID        primitive.ObjectID `bson:"_id,omitempty"`
    ProfileID primitive.ObjectID `bson:"profileId"`
    PartnerID primitive.ObjectID `bson:"partnerId"`
    DataKey   string             `bson:"dataKey"`   // "booking_price", "internal_rating"...
    DataValue interface{}        `bson:"dataValue"`
    DataType  DataType           `bson:"dataType"`  // STRING | NUMBER | BOOLEAN | JSON
    Source    string             `bson:"source"`     // "partner_submit" | "ops_override"
    Note      string             `bson:"note,omitempty"`
    CreatedAt time.Time          `bson:"createdAt"`
    UpdatedAt time.Time          `bson:"updatedAt"`
    UpdatedBy string             `bson:"updatedBy"`
}
```

**Service interface:**
```go
type PartnerDataServicer interface {
    Upsert(ctx context.Context, data *PartnerProfileData) error
    GetByProfile(ctx context.Context, profileID, partnerID primitive.ObjectID) ([]PartnerProfileData, error)
    DeleteByKey(ctx context.Context, profileID, partnerID primitive.ObjectID, key string) error
}
```

**MongoDB collection:** `partner_profile_data`

**Indexes:**
```
{ profileId: 1, partnerId: 1, dataKey: 1 }  unique compound
{ partnerId: 1 }                              list by partner
```

### 4.4 Domain: `access`

**Mục đích:** Track quan hệ partner ↔ profile. Xác định partner nào thấy profile nào trong danh sách "của tôi".

```go
type PartnerProfileAccess struct {
    ID           primitive.ObjectID `bson:"_id,omitempty"`
    PartnerID    primitive.ObjectID `bson:"partnerId"`
    ProfileID    primitive.ObjectID `bson:"profileId"`
    AccessType   AccessType         `bson:"accessType"`
    SourceAction string             `bson:"sourceAction"`
    CreatedAt    time.Time          `bson:"createdAt"`
    CreatedBy    string             `bson:"createdBy"`
}

type AccessType string
const (
    AccessContributed AccessType = "CONTRIBUTED"  // partner gửi profile vào
    AccessBookmarked  AccessType = "BOOKMARKED"   // partner lưu từ pool
    AccessBooked      AccessType = "BOOKED"       // partner đã booking
)

// SourceAction values:
// "creator_registered" | "partner_submitted" | "admin_assigned" | "pool_saved" | "campaign_booking"
```

**Service interface:**
```go
type AccessServicer interface {
    Grant(ctx context.Context, access *PartnerProfileAccess) error
    HasAccess(ctx context.Context, partnerID, profileID primitive.ObjectID) (bool, error)
    ListByPartner(ctx context.Context, partnerID primitive.ObjectID, opts ListOptions) ([]PartnerProfileAccess, int64, error)
    ListByProfile(ctx context.Context, profileID primitive.ObjectID) ([]PartnerProfileAccess, error)
    UpdateType(ctx context.Context, partnerID, profileID primitive.ObjectID, accessType AccessType) error
    Revoke(ctx context.Context, partnerID, profileID primitive.ObjectID) error
}
```

**MongoDB collection:** `partner_profile_access`

**Indexes:**
```
{ partnerId: 1, profileId: 1 }    unique compound
{ partnerId: 1, accessType: 1 }   list + filter
{ profileId: 1 }                   reverse lookup
```

### 4.5 Domain: `enrichment`

**Mục đích:** Ingestion pipeline (nhận profile từ nhiều nguồn) + orchestration với vendor IM (crawl & scoring).

**Ingestion model:**
```go
type IngestionRequest struct {
    Source   string           `json:"source" validate:"required"`
    Profiles []IngestProfile  `json:"profiles" validate:"required,min=1,max=100"`
    Options  IngestionOptions `json:"options"`
}

type IngestProfile struct {
    Platform   string                 `json:"platform" validate:"required"`
    ExternalID string                 `json:"externalId" validate:"required"`
    Data       map[string]interface{} `json:"data"`
    Contact    *ContactInfo           `json:"contact,omitempty"`
    Metadata   map[string]interface{} `json:"metadata,omitempty"`
}

type IngestionOptions struct {
    TriggerEnrichment bool   `json:"triggerEnrichment"`
    OverrideExisting  bool   `json:"overrideExisting"`
    Visibility        string `json:"visibility"`
}

type IngestionResult struct {
    Platform        string          `json:"platform"`
    ExternalID      string          `json:"externalId"`
    Action          string          `json:"action"`    // created | updated | skipped
    ProfileID       string          `json:"profileId"`
    Conflicts       []FieldConflict `json:"conflicts,omitempty"`
    EnrichmentJobID string          `json:"enrichmentJobId,omitempty"`
}
```

**Enrichment job model (vendor IM):**
```go
type EnrichmentJob struct {
    ID           primitive.ObjectID `bson:"_id,omitempty"`
    ProfileID    primitive.ObjectID `bson:"profileId,omitempty"`
    Platform     string             `bson:"platform"`
    ExternalID   string             `bson:"externalId"`
    URL          string             `bson:"url,omitempty"`
    Status       JobStatus          `bson:"status"`     // PENDING → SUBMITTED → PROCESSING → COMPLETED | FAILED
    IMJobID      string             `bson:"imJobId,omitempty"`
    RetryCount   int                `bson:"retryCount"`
    Error        string             `bson:"error,omitempty"`
    PartnerID    *primitive.ObjectID `bson:"partnerId,omitempty"`
    CreatedAt    time.Time          `bson:"createdAt"`
    UpdatedAt    time.Time          `bson:"updatedAt"`
}
```

**Service interface:**
```go
type EnrichmentServicer interface {
    // Multi-source ingestion
    IngestProfiles(ctx context.Context, partnerID primitive.ObjectID, req *IngestionRequest) ([]IngestionResult, error)

    // Vendor IM enrichment (URL-based)
    EnrichFromURL(ctx context.Context, platform, url string, opts EnrichOptions) (*EnrichResult, error)

    // Vendor IM webhook handlers
    OnWebhookReceived(ctx context.Context, payload *WebhookPayload) error
    OnWebhookFailed(ctx context.Context, payload *WebhookPayload) error

    // Job management
    GetJob(ctx context.Context, jobID primitive.ObjectID) (*EnrichmentJob, error)
    RetryJob(ctx context.Context, jobID primitive.ObjectID) error
}
```

### 4.6 Domain: `partner`

**Mục đích:** Quản lý partner accounts, API keys, subscriptions.

```go
type Partner struct {
    ID           primitive.ObjectID `bson:"_id,omitempty"`
    Name         string             `bson:"name"`
    Code         string             `bson:"code"`         // unique, e.g. "techcombank"
    APIKeyHash   string             `bson:"apiKeyHash"`
    APIKeyPrefix string             `bson:"apiKeyPrefix"` // "at_prod_t..."
    IsActive     bool               `bson:"isActive"`
    ContactName  string             `bson:"contactName,omitempty"`
    ContactEmail string             `bson:"contactEmail,omitempty"`
    RateLimit    int                `bson:"rateLimit"`    // req/min, default 100
    WebhookURL   string             `bson:"webhookUrl,omitempty"`
    WebhookSecret string            `bson:"webhookSecret,omitempty"`
    CreatedAt    time.Time          `bson:"createdAt"`
    UpdatedAt    time.Time          `bson:"updatedAt"`
}

type PartnerSubscription struct {
    ID           primitive.ObjectID `bson:"_id,omitempty"`
    PartnerID    primitive.ObjectID `bson:"partnerId"`
    Tier         SubscriptionTier   `bson:"tier"`     // FREE | BASIC | PREMIUM | ENTERPRISE
    Status       SubscriptionStatus `bson:"status"`   // ACTIVE | EXPIRED | SUSPENDED
    MonthlyQuota int                `bson:"monthlyQuota"`
    UsedThisMonth int               `bson:"usedThisMonth"`
    StartDate    time.Time          `bson:"startDate"`
    EndDate      *time.Time         `bson:"endDate,omitempty"`
    AutoRenew    bool               `bson:"autoRenew"`
}
```

### 4.7 Domain: `pool`

**Mục đích:** Search trên pool công khai (PUBLIC profiles). Chỉ trả base profile, không enrichment.

```go
type SearchFilter struct {
    Platform      string   `json:"platform,omitempty"`
    Categories    []string `json:"categories,omitempty"`
    MinFollowers  int64    `json:"minFollowers,omitempty"`
    MaxFollowers  int64    `json:"maxFollowers,omitempty"`
    MinEngagement float64  `json:"minEngagement,omitempty"`
    MinScore      float64  `json:"minScore,omitempty"`
    Country       string   `json:"country,omitempty"`
    Query         string   `json:"query,omitempty"`       // text search
    Sort          string   `json:"sort,omitempty"`         // completenessScore | followers | score
}
```

### 4.8 Domain: `admin`

**Mục đích:** Admin user management, RBAC, sessions, security, audit trail.

```go
type AdminUser struct {
    ID              primitive.ObjectID `bson:"_id,omitempty"`
    Email           string             `bson:"email"`
    PasswordHash    string             `bson:"passwordHash"`
    RoleID          primitive.ObjectID `bson:"roleId"`
    Status          string             `bson:"status"`        // active | suspended | deleted
    MustChangePassword bool            `bson:"mustChangePassword"`
    FailedAttempts  int                `bson:"failedAttempts"`
    LockedUntil     *time.Time         `bson:"lockedUntil,omitempty"`
    LastLoginAt     *time.Time         `bson:"lastLoginAt,omitempty"`
}

type Role struct {
    ID            primitive.ObjectID   `bson:"_id,omitempty"`
    Name          string               `bson:"name"`
    Slug          string               `bson:"slug"`          // super-admin | admin | moderator
    HierarchyLevel int                 `bson:"hierarchyLevel"` // 100 | 50 | 10
    PermissionIDs []primitive.ObjectID  `bson:"permissionIds"`
}

type Permission struct {
    ID       primitive.ObjectID `bson:"_id,omitempty"`
    Code     string             `bson:"code"`     // "profiles:write", "partner_data:read"
    Resource string             `bson:"resource"` // "profiles", "partners"
    Action   string             `bson:"action"`   // "read", "write", "verify"
}

// Audit log - append-only, immutable
type AdminActivityLog struct {
    ID        primitive.ObjectID `bson:"_id,omitempty"`
    AdminID   primitive.ObjectID `bson:"adminId"`
    Action    string             `bson:"action"`
    Resource  string             `bson:"resource"`
    ResourceID string            `bson:"resourceId,omitempty"`
    Changes   *ChangeSet         `bson:"changes,omitempty"` // before/after
    IP        string             `bson:"ip"`
    UserAgent string             `bson:"userAgent"`
    Result    string             `bson:"result"`    // success | failed
    CreatedAt time.Time          `bson:"createdAt"`
}
```

### 4.9 Domains: `quota`, `subscription`, `webhook`

| Domain | Collection | Mục đích |
|--------|-----------|----------|
| `quota` | (uses partner_subscriptions) | Check & decrement monthly quota per partner |
| `subscription` | `partner_subscriptions` | Tier management, feature gating, alerts |
| `webhook` | `webhook_events` | Event delivery to partner webhook URLs. Retry (1m, 5m, 15m) + DLQ |

---

## 5. Data Architecture

### 5.1 MongoDB Collections

```
at_core_db
│
│  CORE
├── profiles                     Base profile (shared, mọi partner thấy)
├── partner_profile_data         Partner enrichment (isolated per partner)
├── partner_profile_access       Partner-profile relationship
├── profile_changes              Audit trail cho profile edits
│
│  ENRICHMENT
├── enrichment_jobs              Job tracking cho vendor IM
│
│  PARTNER
├── partners                     Partner accounts
├── partner_subscriptions        Subscription tiers + quota
│
│  WEBHOOK
├── webhook_events               Event delivery to partners
│
│  ADMIN
├── admin_users                  Admin accounts
├── admin_roles                  RBAC roles
├── admin_permissions            RBAC permissions
├── admin_sessions               Session tracking
└── admin_activity_logs          Admin audit trail (append-only)
```

### 5.2 Profile Data Model (3 tầng)

```
┌────────────────────────────────────────────────────────┐
│ profiles collection                                     │
│ (Base Profile - PUBLIC, mọi partner thấy)              │
│                                                         │
│ { platform, externalId, profileData, profileMetrics,   │
│   score, visibility, completenessScore, fieldSources,  │
│   verifiedAt, verifiedBy }                              │
└────────────────────────┬───────────────────────────────┘
                         │ profileId
┌────────────────────────▼───────────────────────────────┐
│ partner_profile_data collection                         │
│ (Private Enrichment - CHỈ partner đó thấy)             │
│                                                         │
│ { profileId, partnerId, dataKey, dataValue, source }   │
│                                                         │
│ Ví dụ:                                                  │
│ TCB:  { dataKey: "booking_price", dataValue: 50000000 }│
│ AMB:  { dataKey: "self_rate", dataValue: 40000000 }    │
│ → TCB KHÔNG thấy data của AMB, ngược lại cũng vậy     │
└────────────────────────┬───────────────────────────────┘
                         │ profileId + partnerId
┌────────────────────────▼───────────────────────────────┐
│ partner_profile_access collection                       │
│ (Ai thấy profile nào trong danh sách)                  │
│                                                         │
│ { partnerId, profileId, accessType, sourceAction }     │
│                                                         │
│ Ví dụ:                                                  │
│ TCB + Profile_A:  CONTRIBUTED (partner_submitted)       │
│ AMB + Profile_A:  CONTRIBUTED (creator_registered)      │
│ TCB + Profile_B:  BOOKMARKED  (pool_saved)             │
└────────────────────────────────────────────────────────┘
```

### 5.3 Profile Change History

```go
// profile_changes collection
type ChangeRecord struct {
    ID        primitive.ObjectID `bson:"_id,omitempty"`
    ProfileID primitive.ObjectID `bson:"profileId"`
    Field     string             `bson:"field"`        // "profileData.categories"
    OldValue  interface{}        `bson:"oldValue,omitempty"`
    NewValue  interface{}        `bson:"newValue"`
    OldSource *FieldSource       `bson:"oldSource,omitempty"`
    NewSource FieldSource        `bson:"newSource"`
    Reason    string             `bson:"reason,omitempty"`
    ChangedBy string             `bson:"changedBy"`    // admin email | "system" | "partner_tcb"
    ChangedAt time.Time          `bson:"changedAt"`
}
```

### 5.4 Completeness Score

```
Required fields (60%):
  platform + externalId          10%
  name + handle                  10%
  followers count                10%
  engagement rate                10%
  categories                     10%
  avatar                         10%

Optional fields (30%):
  contact email                   5%
  contact phone                   5%
  country                         5%
  bio/description                 5%
  recent content                  5%
  demographics                    5%

Quality bonus (10%):
  has ops_verified fields          5%
  freshness < 7 days               5%
```

---

## 6. API Design

### 6.1 API Overview

| Group | Base Path | Auth | Mô tả |
|-------|-----------|------|--------|
| **Health** | `/health` | None | Liveness & readiness checks |
| **Partner Auth** | `/auth` | API Key | Exchange API key for JWT tokens |
| **Partner API** | `/v1` | API Key hoặc JWT | Profile queries, ingestion, matching |
| **Admin API** | `/admin` | Admin JWT + RBAC | System management, ops override |
| **Vendor Webhook** | `/v1/webhooks/im` | HMAC-SHA256 | Receive results from vendor IM |

### 6.2 Partner API

```
AUTH
POST   /auth/login                            Exchange API key → JWT tokens
POST   /auth/refresh                          Refresh token pair

PROFILES (scoped by partner)
GET    /v1/profiles                           List profiles
         ?scope=my_profiles                     Profiles có relationship với partner
         ?scope=pool                            Pool search (PUBLIC, base only)
         ?platform=tiktok
         ?categories=beauty
         ?minFollowers=10000
         ?sort=completenessScore:desc
         ?page=1&limit=20
GET    /v1/profiles/{id}                      Get profile (base + own enrichment)
GET    /v1/profiles/{platform}/{externalId}   Get by platform identity

PROFILE ACTIONS
POST   /v1/profiles/{id}/save                Save từ pool → bookmarked
DELETE /v1/profiles/{id}/save                Remove bookmark

PARTNER DATA (own enrichment)
GET    /v1/profiles/{id}/data                Get own partner data
PUT    /v1/profiles/{id}/data                Upsert partner data
DELETE /v1/profiles/{id}/data/{key}          Delete data key

INGESTION (submit profiles)
POST   /v1/profiles/ingest                   Batch submit (max 100)

ENRICHMENT (trigger vendor IM)
POST   /v1/enrichment                        Enrich from URL
GET    /v1/enrichment/jobs/{id}              Get job status

MATCHING (proxy to vendor IM)
POST   /v1/matching/score                    Score single influencer
POST   /v1/matching/batch                    Score batch
GET    /v1/matching/jobs/{id}                Get batch job status

POOL
GET    /v1/pool/search                       Search public pool
POST   /v1/pool/request                      Request profiles (quota check)

QUOTA
GET    /v1/partners/quota                    Get quota status
```

### 6.3 Admin API

```
AUTH
POST   /admin/auth/login                     Email + password login
POST   /admin/auth/refresh                   Refresh tokens
POST   /admin/auth/logout                    Revoke session
POST   /admin/auth/change-password           Change password

PROFILES (full view, no partner scope)
GET    /admin/profiles                       List all profiles
GET    /admin/profiles/{id}                  Full profile (all sources, all partner data)
GET    /admin/profiles/{id}/history          Change history
PUT    /admin/profiles/{id}/fields           Ops override (edit fields + reason)
POST   /admin/profiles/{id}/verify           Mark as ops-verified
POST   /admin/profiles/import                Bulk import (CSV)

PROFILE-PARTNER ACCESS
GET    /admin/profiles/{id}/partners         Partners with access
POST   /admin/profiles/{id}/assign           Assign profile to partner

ENRICHMENT
POST   /admin/enrichment                     Enrich from URL
GET    /admin/enrichment/jobs                List recent jobs
GET    /admin/enrichment/jobs/{id}           Job detail
POST   /admin/enrichment/jobs/{id}/retry     Retry failed job

PARTNERS
POST   /admin/partners                       Create partner
GET    /admin/partners                       List partners
GET    /admin/partners/{id}                  Partner detail
PUT    /admin/partners/{id}                  Update partner
POST   /admin/partners/{id}/api-key/rotate   Rotate API key

USERS, ROLES, SESSIONS
CRUD   /admin/users
CRUD   /admin/roles
GET    /admin/sessions
DELETE /admin/sessions/{id}

WEBHOOKS
GET    /admin/webhooks                       List webhook events
POST   /admin/webhooks/{id}/retry            Manual retry

AUDIT
GET    /admin/activity-logs                  Paginated audit log
```

### 6.4 Vendor IM Webhook

```
POST   /v1/webhooks/im                       Receive crawl/scoring results
       Header: X-Api-Key: {im_api_key}
       Body: HMAC-SHA256 signed

       Events:
       - profile.created → update profile (source=crawl, confidence=0.6)
       - job.failed → mark job failed, schedule retry
```

### 6.5 Response Format

**Profile response (Partner-scoped):**
```json
{
  "id": "...",
  "platform": "tiktok",
  "externalId": "@handle",
  "base": {
    "name": "...",
    "handle": "@handle",
    "followers": 150000,
    "engagementRate": 3.2,
    "categories": ["beauty"],
    "country": "VN",
    "verified": true
  },
  "score": {
    "total": 78.5,
    "engagement": 72,
    "authenticity": 85,
    "growth": 65,
    "reach": 92
  },
  "enrichment": {
    "booking_price": { "value": 50000000, "updatedAt": "2026-03-01" }
  },
  "opsVerified": {
    "verifiedAt": "2026-03-05",
    "verifiedFields": ["categories", "country"]
  },
  "meta": {
    "completenessScore": 87.5,
    "visibility": "PUBLIC",
    "lastEnriched": "2026-03-10",
    "accessType": "CONTRIBUTED"
  }
}
```

**Ingestion response:**
```json
{
  "results": [
    {
      "platform": "tiktok",
      "externalId": "@handle",
      "action": "created",
      "profileId": "...",
      "conflicts": [],
      "enrichmentJobId": "..."
    }
  ],
  "summary": {
    "total": 10,
    "created": 6,
    "updated": 3,
    "skipped": 1
  }
}
```

**Error response:**
```json
{
  "code": "VALIDATION_ERROR",
  "message": "Invalid platform",
  "details": "platform must be one of: tiktok, youtube, facebook, instagram"
}
```

---

## 7. Authentication & Authorization

### 7.1 Partner Authentication

**Hai phương thức, cùng kết quả:**

| Method | Use case | Headers |
|--------|----------|---------|
| **API Key** | Server-to-server | `X-Partner-ID: tcb` + `X-API-Key: at_prod_xxx` |
| **JWT** | Web client, automation | `Authorization: Bearer {access_token}` hoặc cookie |

Cả hai đều set `Partner` vào request context. Handlers không cần biết auth method nào.

**JWT Token flow:**
```
POST /auth/login (API Key) → { accessToken (1h), refreshToken (7d) }
POST /auth/refresh (refreshToken) → { new accessToken, new refreshToken }
```

### 7.2 Admin Authentication

| Method | Headers |
|--------|---------|
| **Admin JWT** | `Authorization: Bearer {admin_token}` hoặc cookie `admin_access_token` |

**Security measures:**
- bcrypt password hashing (cost 12)
- Account lockout: 5 failed attempts → 15 min lock
- IP throttling: max 20 failed/hour/IP
- Progressive delay sau mỗi failed attempt
- Session tracking per device

### 7.3 Admin RBAC Permissions

```
# Profile Hub permissions
profiles:read              Xem profiles
profiles:write             Sửa profile fields (ops override)
profiles:verify            Đánh dấu ops-verified
profiles:import            Bulk import CSV
profiles:history           Xem change history
partner_data:read          Xem partner enrichment data (cross-partner, admin only)
access:read                Xem partner-profile relationships
access:write               Assign/remove partner access

# Partner management
partners:read              Xem partners
partners:write             Tạo/sửa partners
partners:api_key           Rotate API keys

# Enrichment
enrichment:read            Xem jobs
enrichment:write           Tạo/retry jobs

# Webhook
webhooks:read              Xem webhook events
webhooks:retry             Manual retry

# Admin management
users:read                 Xem admin users
users:write                Tạo/sửa admin users
roles:read                 Xem roles
roles:write                Tạo/sửa roles
activity_logs:read         Xem audit logs
```

### 7.4 Vendor IM Authentication

```
POST /v1/webhooks/im
Header: X-Api-Key: {configured_im_api_key}
Body: raw JSON
Signature: HMAC-SHA256(body, webhook_secret) verified against header
```

---

## 8. Middleware Stack

Thứ tự xử lý request:

```
Request
  │
  ├─ 1. Recovery          Panic recovery, log error
  ├─ 2. CORS              Cross-origin validation
  ├─ 3. RequestID         Generate X-Request-ID
  ├─ 4. Logging           Request/response logging
  ├─ 5. RequestMetadata   Extract IP, UserAgent → context
  │
  ├─ [Partner routes]
  │   ├─ 6a. JWTAuth / PartnerAuth    Validate token or API key
  │   └─ 7a. PartnerRateLimit         Per-partner rate limit (Redis)
  │
  ├─ [Admin routes]
  │   ├─ 6b. AdminAuth                Validate admin JWT
  │   ├─ 7b. PermissionGuard          Check RBAC permissions
  │   └─ 8b. IPAllowlist (optional)   Restrict admin by IP
  │
  └─ 9. Validation        Request body schema validation
  │
  Handler
```

---

## 9. Infrastructure Layer

### 9.1 Vendor IM Client (`infra/ipclient`)

HTTP client tới Influence Meter API:

```go
type IMClient interface {
    GetProfile(ctx context.Context, platform, externalID string) (*ProfileResponse, error)
    GetScore(ctx context.Context, platform, externalID string) (*ScoreResponse, error)
    SubmitEnrichment(ctx context.Context, platform, url, callbackURL string) (*EnrichResponse, error)
    GetJobStatus(ctx context.Context, jobID string) (*JobResponse, error)
    FetchEnrichedProfile(ctx context.Context, platform, externalID string) (*EnrichedProfileResponse, error)
}
```

**Resilience:**
- **Retry:** Exponential backoff (3 attempts)
- **Circuit breaker:** Open after 5 consecutive failures, half-open after 30s
- **Timeout:** 30s per request
- **Connection pooling:** Max 100 idle connections

**Graceful degradation:** Khi IM down:
- at-core vẫn serve cached profiles + partner data
- Enrichment & matching requests trả 503 với message rõ ràng
- Circuit breaker ngăn cascade failure

### 9.2 MongoDB (`infra/mongodb`)

- Connection pooling (max 100 connections)
- Read preference: secondaryPreferred cho read-heavy queries
- Write concern: majority cho profile writes
- Repository pattern: mỗi domain có implementation riêng

### 9.3 Redis (`infra/redis`)

| Use case | Pattern | TTL |
|----------|---------|-----|
| Rate limiting | Sliding window (ZSET) | 1 min |
| Profile cache | Key-value | 5 min |
| Score cache | Key-value | 1 hour |
| Session | Key-value | 7 days |
| IP throttle | Counter | 1 hour |

### 9.4 Webhook Dispatcher (`infra/webhook`)

- Gửi events tới partner webhook URLs
- Retry schedule: 1m → 5m → 15m (3 auto retries)
- Max 5 attempts (1 initial + 3 auto + 1 manual)
- Dead letter queue (DLQ) cho failed events
- HMAC-SHA256 signature cho mỗi delivery

---

## 10. Luồng xử lý chính

### 10.1 Ingestion: Partner gửi profile

```
POST /v1/profiles/ingest

1. PartnerAuth middleware → set Partner context
2. Validate request body (max 100 profiles)
3. For each profile:
   a. Find existing by platform + externalID
   b. Not found → create UnifiedProfile
   c. Found → conflict resolution:
      - Field có confidence mới > cũ → update
      - Field có confidence mới < cũ → skip (giữ nguyên)
      - Field có confidence bằng → flag conflict
   d. Update FieldSources cho mỗi field đã thay đổi
   e. Create PartnerProfileAccess (CONTRIBUTED)
   f. Save partner metadata → PartnerProfileData
   g. Record ChangeRecord(s)
   h. Recalculate completeness score
   i. If triggerEnrichment → submit job to IM
4. Return results
```

### 10.2 Enrichment: IM webhook callback

```
POST /v1/webhooks/im

1. Verify X-Api-Key header
2. Verify HMAC-SHA256 signature
3. Parse webhook payload
4. Event = "profile.created":
   a. Find EnrichmentJob by IM job ID
   b. Transform IM data → profile fields
   c. For each field:
      - Check existing FieldSource confidence
      - Crawl confidence = 0.6
      - If existing confidence > 0.6 (e.g., ops_verified 0.9) → skip field
      - Else → update field, set source=crawl
   d. Update profile
   e. Job status → COMPLETED
   f. Trigger webhook to partner (if configured)
5. Event = "job.failed":
   a. Job status → FAILED
   b. If retryCount < max → schedule retry
```

### 10.3 Ops Override: Admin sửa profile

```
PUT /admin/profiles/{id}/fields

1. AdminAuth middleware
2. PermissionGuard (profiles:write)
3. For each field to update:
   a. Get current field value + source
   b. Set new value
   c. Set source = ops_verified, confidence = 0.9
   d. Record ChangeRecord (old/new value, reason, admin email)
4. Log AdminActivityLog
5. Recalculate completeness
```

### 10.4 Partner query: Scoped profile list

```
GET /v1/profiles?scope=my_profiles

1. PartnerAuth middleware → get Partner
2. scope = "my_profiles":
   a. Query partner_profile_access WHERE partnerId = partner.ID
   b. Get profileIDs
   c. Query profiles WHERE _id IN profileIDs
   d. For each profile, attach own enrichment from partner_profile_data
   e. Return base + enrichment + meta
3. scope = "pool":
   a. Query profiles WHERE visibility = PUBLIC
   b. Apply filters (platform, categories, minFollowers...)
   c. Return base only (NO enrichment)
```

---

## 11. Configuration

```
# Server
SERVER_PORT                 HTTP server port (default: 8080)

# MongoDB
MONGODB_URI                 Connection string

# Redis
REDIS_URL                   Connection string

# JWT
JWT_SECRET                  Partner JWT signing secret (min 32 chars)
JWT_ISSUER                  Token issuer (default: "at-core")
ADMIN_JWT_SECRET            Admin JWT signing secret (separate)

# Vendor IM
IM_BASE_URL                 Influence Meter API base URL
IM_API_KEY                  API key for IM authentication
IM_TENANT_ID                Tenant ID for IM webhook routing
IM_WEBHOOK_SECRET           HMAC secret for webhook verification
IM_WEBHOOK_API_KEY          API key for webhook header validation

# Callbacks
CALLBACK_BASE_URL           Internal URL for IM callbacks
PUBLIC_BASE_URL             Public URL for partner-facing links

# Security
ENCRYPTION_KEY              64-char hex for contact info encryption (AES-256)

# Email
EMAIL_HOST                  SMTP host
EMAIL_PORT                  SMTP port
EMAIL_USERNAME              SMTP username
EMAIL_PASSWORD              SMTP password
```

---

## 12. Dependency Diagram

```
main.go (DI Container)
  │
  ├── API Layer
  │   ├── Handlers
  │   │   ├── ProfileHandler        → ProfileServicer, PartnerDataServicer, AccessServicer
  │   │   ├── IngestionHandler      → EnrichmentServicer, AccessServicer
  │   │   ├── PoolHandler           → PoolServicer
  │   │   ├── MatchingHandler       → IMClient (proxy)
  │   │   ├── AdminProfileHandler   → ProfileServicer, PartnerDataServicer, AccessServicer
  │   │   ├── AdminPartnerHandler   → PartnerServicer
  │   │   ├── AdminAuthHandler      → AdminServicer, SessionServicer
  │   │   ├── IMWebhookHandler      → EnrichmentServicer
  │   │   └── WebhookHandler        → WebhookServicer
  │   │
  │   └── Middleware
  │       ├── PartnerAuth           → PartnerServicer
  │       ├── AdminAuth             → JWTManager
  │       ├── PermissionGuard       → (reads claims from context)
  │       └── RateLimit             → Redis
  │
  ├── Domain Layer (interfaces)
  │   ├── ProfileServicer
  │   ├── PartnerDataServicer
  │   ├── AccessServicer
  │   ├── EnrichmentServicer
  │   ├── PartnerServicer
  │   ├── PoolServicer
  │   ├── QuotaServicer
  │   ├── AdminServicer
  │   ├── SessionServicer
  │   └── WebhookServicer
  │
  └── Infrastructure Layer (implementations)
      ├── MongoDB repositories (all domain repos)
      ├── Redis client (cache, rate limit)
      ├── IMClient (vendor IM HTTP client)
      ├── JWTManager (token generation/validation)
      ├── WebhookDispatcher (event delivery)
      └── EmailService (notifications)
```

---

*Tài liệu thuộc dự án at-core - AccessTrade Projects*
