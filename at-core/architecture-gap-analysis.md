# at-core Gap Analysis: Hiện tại → Profile Hub

> Phân tích khoảng cách giữa codebase hiện tại và kiến trúc Profile Hub mục tiêu.
> Bao gồm: những gì giữ nguyên, cần mở rộng, cần thêm mới, và migration plan.
>
> Cập nhật: 2026-03-11

---

## 1. Tổng quan kiến trúc

### 1.1 Kiến trúc hiện tại

at-core hiện là **proxy/middleware** giữa partners và Influence Meter (IM):

```
Partner (TCB) ──► at-core (proxy) ──► Influence Meter (vendor)
```

**Điểm mạnh đã có:**
- Clean/Hexagonal Architecture với domain-driven design
- 8 domain modules (admin, enrichment, partner, pool, profile, quota, subscription, webhook)
- Partner authentication (API Key + JWT hybrid)
- Admin RBAC + audit trail
- Quota/Subscription management
- Rate limiting (Redis sliding window)
- Circuit breaker cho IM client
- Webhook dispatcher với retry + DLQ

### 1.2 Kiến trúc mục tiêu: Profile Hub

at-core phát triển từ proxy thành **Profile Hub** - nơi tập trung quản lý influencer profile từ nhiều nguồn:

```
                              ┌─────────────────────────────────────────┐
                              │            at-core PROFILE HUB          │
                              │                                         │
  ┌─────────┐  Ingestion API  │  ┌───────────┐    ┌──────────────────┐ │
  │   TCB   │────────────────►│  │ Ingestion │───►│  Profile Store   │ │
  └─────────┘                 │  │ Service   │    │                  │ │
  ┌─────────┐  Ingestion API  │  │           │    │ Base Profile     │ │
  │ Vinfast │────────────────►│  │ - Validate│    │ Partner Data     │ │
  └─────────┘                 │  │ - Normalize    │ Partner Access   │ │
  ┌──────────┐ Ingestion API  │  │ - Conflict│    │ Change History   │ │
  │Ambassador│───────────────►│  │   resolve │    └────────┬─────────┘ │
  └──────────┘                │  └───────────┘             │           │
  ┌─────────┐  Admin API      │                            │           │
  │  Admin  │────────────────►│  ┌───────────┐             │           │
  │  / Ops  │                 │  │   Ops     │─────────────┘           │
  └─────────┘                 │  │  Override │                         │
                              │  └───────────┘                         │
                              │                            │           │
                              │  ┌───────────┐    ┌────────▼─────────┐ │
                              │  │ Output    │    │ Vendor IM Client │ │
  ┌─────────┐  Partner API    │  │ Layer     │    │                  │ │
  │   TCB   │◄────────────────│  │           │    │ - Enrichment     │ │
  └─────────┘                 │  │ - Pool    │    │ - Scoring        │ │
  ┌──────────┐ Partner API    │  │ - My Prof │    │ - Matching       │ │
  │Ambassador│◄───────────────│  │ - Match   │    │                  │ │
  └──────────┘                │  └───────────┘    └──────────────────┘ │
                              └─────────────────────────────────────────┘
```

### 1.3 Nguyên tắc thiết kế

| # | Nguyên tắc | Mô tả |
|---|-----------|--------|
| P1 | **Profile Hub là single source of truth** | Tất cả profile data tập trung tại at-core. Partners contribute & consume |
| P2 | **Shared Base + Private Enrichment** | Base profile công khai, partner data cách ly hoàn toàn |
| P3 | **Field-level confidence** | Mỗi trường dữ liệu có source + confidence score, conflict resolution tự động |
| P4 | **Partner-scoped access** | Mọi request đều scoped theo partner_id, không có cross-partner data leak |
| P5 | **IM là vendor, không phải core** | at-core có thể hoạt động khi IM down (graceful degradation) |
| P6 | **Audit everything** | Mọi thay đổi profile đều có lịch sử: ai, khi nào, giá trị cũ/mới, lý do |

---

## 2. Technology Stack

### 2.1 Giữ nguyên (đã proven)

| Layer | Technology | Lý do giữ |
|-------|-----------|-----------|
| **Language** | Go 1.24+ | Performance, typing, team familiarity |
| **Database** | MongoDB | Flexible schema phù hợp profile data đa dạng |
| **Cache** | Redis | Rate limiting, caching, session management |
| **HTTP Client** | go-retryablehttp + gobreaker | Retry + circuit breaker cho vendor IM |
| **Auth** | JWT (golang-jwt/v5) | Stateless auth cho cả partner & admin |
| **Validation** | go-playground/validator | Request validation |

### 2.2 Không thay đổi stack

Không có lý do kỹ thuật để thay đổi stack hiện tại. Go + MongoDB + Redis đáp ứng tốt yêu cầu Profile Hub:
- MongoDB flexible schema → phù hợp cho profile data có nhiều optional fields
- Go performance → xử lý batch ingestion hiệu quả
- Redis → cache profile queries, rate limiting

---

## 3. Domain Architecture

### 3.1 Domain Map: Hiện tại → Mục tiêu

```
internal/domain/
├── admin/          ✅ GIỮ NGUYÊN    Admin RBAC, session, audit
├── partner/        ✅ GIỮ NGUYÊN    Partner management, API key, subscription
├── quota/          ✅ GIỮ NGUYÊN    Monthly quota tracking
├── subscription/   ✅ GIỮ NGUYÊN    Tier & feature management
├── webhook/        ✅ GIỮ NGUYÊN    Event delivery to partners
├── enrichment/     🔧 MỞ RỘNG      Thêm ingestion pipeline (không chỉ URL-based)
├── profile/        🔧 MỞ RỘNG      Thêm field-level source/confidence, ops edit
├── pool/           🔧 MỞ RỘNG      Tích hợp partner-profile access vào pool search
├── partnerdata/    🆕 MỚI          Partner-specific enrichment data (isolated)
└── access/         🆕 MỚI          Partner-profile relationship tracking
```

### 3.2 Domain mới: `partnerdata`

**Mục đích:** Lưu trữ và quản lý dữ liệu riêng mà mỗi partner đóng góp cho profile. Data này **chỉ partner đó** mới thấy.

**Model:**
```go
// partnerdata/model.go

type PartnerProfileData struct {
    ID        primitive.ObjectID `bson:"_id,omitempty"`
    ProfileID primitive.ObjectID `bson:"profileId"`
    PartnerID primitive.ObjectID `bson:"partnerId"`
    DataKey   string             `bson:"dataKey"`   // "booking_price", "internal_rating"...
    DataValue interface{}        `bson:"dataValue"`
    DataType  DataType           `bson:"dataType"`  // STRING, NUMBER, BOOLEAN, JSON
    Source    string             `bson:"source"`     // "partner_submit" | "ops_override"
    Note      string             `bson:"note,omitempty"`
    CreatedAt time.Time          `bson:"createdAt"`
    UpdatedAt time.Time          `bson:"updatedAt"`
    UpdatedBy string             `bson:"updatedBy"`  // admin email hoặc "system"
}

type DataType string
const (
    DataTypeString  DataType = "STRING"
    DataTypeNumber  DataType = "NUMBER"
    DataTypeBoolean DataType = "BOOLEAN"
    DataTypeJSON    DataType = "JSON"
)
```

**Repository interface:**
```go
type Repository interface {
    Upsert(ctx context.Context, data *PartnerProfileData) error
    GetByProfile(ctx context.Context, profileID, partnerID primitive.ObjectID) ([]PartnerProfileData, error)
    DeleteByKey(ctx context.Context, profileID, partnerID primitive.ObjectID, dataKey string) error
    ListByPartner(ctx context.Context, partnerID primitive.ObjectID, opts ListOptions) ([]PartnerProfileData, int64, error)
}
```

**MongoDB collection:** `partner_profile_data`

**Indexes:**
```
{ profileId: 1, partnerId: 1, dataKey: 1 }  // unique compound
{ partnerId: 1 }                              // list by partner
{ profileId: 1 }                              // list by profile
```

### 3.3 Domain mới: `access`

**Mục đích:** Track quan hệ giữa partner và profile. Xác định "partner nào thấy profile nào trong danh sách".

**Model:**
```go
// access/model.go

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
// "creator_registered"  - creator đăng ký qua ambassabor
// "partner_submitted"   - partner gửi qua ingestion API
// "admin_assigned"      - admin assign profile cho partner
// "pool_saved"          - partner lưu từ pool search
// "campaign_booking"    - partner booking cho campaign
```

**Repository interface:**
```go
type Repository interface {
    Upsert(ctx context.Context, access *PartnerProfileAccess) error
    HasAccess(ctx context.Context, partnerID, profileID primitive.ObjectID) (bool, error)
    ListByPartner(ctx context.Context, partnerID primitive.ObjectID, opts ListOptions) ([]PartnerProfileAccess, int64, error)
    ListByProfile(ctx context.Context, profileID primitive.ObjectID) ([]PartnerProfileAccess, error)
    UpdateAccessType(ctx context.Context, partnerID, profileID primitive.ObjectID, accessType AccessType) error
    Delete(ctx context.Context, partnerID, profileID primitive.ObjectID) error
}
```

**MongoDB collection:** `partner_profile_access`

**Indexes:**
```
{ partnerId: 1, profileId: 1 }  // unique compound
{ partnerId: 1, accessType: 1 } // list by partner + filter type
{ profileId: 1 }                 // list partners for a profile
```

### 3.4 Mở rộng domain `profile`

**Thay đổi trên UnifiedProfile:**

```go
// profile/model.go - ADDITIONS to existing UnifiedProfile

// Thêm fields mới vào UnifiedProfile:
type UnifiedProfile struct {
    // ... existing fields giữ nguyên ...

    // === MỚI: Source tracking ===
    Visibility       Visibility `bson:"visibility" json:"visibility"`
    CompletenessScore float64   `bson:"completenessScore" json:"completenessScore"`
    VerifiedAt       *time.Time `bson:"verifiedAt,omitempty" json:"verifiedAt,omitempty"`
    VerifiedBy       string     `bson:"verifiedBy,omitempty" json:"verifiedBy,omitempty"`

    // === MỚI: Field-level source tracking ===
    FieldSources map[string]FieldSource `bson:"fieldSources,omitempty" json:"fieldSources,omitempty"`
}

type Visibility string
const (
    VisibilityPublic   Visibility = "PUBLIC"
    VisibilityUnlisted Visibility = "UNLISTED"
)

type FieldSource struct {
    Source     string    `bson:"source" json:"source"`         // "crawl" | "partner_tcb" | "ops_verified" | "creator_self"
    Confidence float64  `bson:"confidence" json:"confidence"` // 0.0 - 1.0
    UpdatedAt  time.Time `bson:"updatedAt" json:"updatedAt"`
    UpdatedBy  string    `bson:"updatedBy,omitempty" json:"updatedBy,omitempty"`
    PreviousValue interface{} `bson:"previousValue,omitempty" json:"-"` // cho audit
}

// Source confidence hierarchy
const (
    ConfidencePlatformAPI   = 1.0  // direct từ TikTok/YouTube API
    ConfidenceOpsVerified   = 0.9  // operations team xác minh
    ConfidencePartnerVerified = 0.8 // partner xác nhận
    ConfidencePartnerSubmit = 0.7  // partner gửi vào
    ConfidenceCrawl         = 0.6  // crawl từ IM
    ConfidenceCreatorSelf   = 0.5  // creator tự khai
    ConfidenceMLPredicted   = 0.3  // ML model predict
)
```

**Thêm vào ProfileServicer interface:**
```go
// profile/service_interface.go - ADDITIONS

type ProfileServicer interface {
    // ... existing methods giữ nguyên ...

    // MỚI: Operations override
    UpdateField(ctx context.Context, profileID primitive.ObjectID, field string, value interface{}, source FieldSource, reason string) error
    GetChangeHistory(ctx context.Context, profileID primitive.ObjectID, opts ListOptions) ([]ChangeRecord, int64, error)

    // MỚI: Completeness
    RecalculateCompleteness(ctx context.Context, profileID primitive.ObjectID) (float64, error)
}
```

**MongoDB collection mới:** `profile_changes` (audit trail)
```go
type ChangeRecord struct {
    ID        primitive.ObjectID `bson:"_id,omitempty"`
    ProfileID primitive.ObjectID `bson:"profileId"`
    Field     string             `bson:"field"`
    OldValue  interface{}        `bson:"oldValue,omitempty"`
    NewValue  interface{}        `bson:"newValue"`
    OldSource FieldSource        `bson:"oldSource,omitempty"`
    NewSource FieldSource        `bson:"newSource"`
    Reason    string             `bson:"reason,omitempty"`
    ChangedBy string             `bson:"changedBy"`
    ChangedAt time.Time          `bson:"changedAt"`
}
```

### 3.5 Mở rộng domain `enrichment` → Ingestion Pipeline

**Hiện tại:** Enrichment chỉ nhận URL → gửi IM crawl → nhận kết quả.

**Mở rộng:** Thêm ingestion pipeline nhận profile data trực tiếp từ nhiều nguồn.

```go
// enrichment/ingestion.go - NEW

type IngestionRequest struct {
    Source   string            `json:"source" validate:"required"`   // "partner_tcb" | "partner_vinfast" | "creator_self" | "admin_import"
    Profiles []IngestProfile   `json:"profiles" validate:"required,min=1,max=100"`
    Options  IngestionOptions  `json:"options"`
}

type IngestProfile struct {
    Platform   string                 `json:"platform" validate:"required"`
    ExternalID string                 `json:"externalId" validate:"required"`
    Data       map[string]interface{} `json:"data"`                          // name, handle, followers, categories...
    Contact    *ContactInfo           `json:"contact,omitempty"`             // email, phone (encrypted)
    Metadata   map[string]interface{} `json:"metadata,omitempty"`            // partner-specific metadata
}

type IngestionOptions struct {
    TriggerEnrichment bool   `json:"triggerEnrichment"` // gửi IM crawl sau khi ingest
    OverrideExisting  bool   `json:"overrideExisting"`  // ghi đè data có confidence thấp hơn
    Visibility        string `json:"visibility"`         // PUBLIC | UNLISTED
}

type IngestionResult struct {
    Platform     string           `json:"platform"`
    ExternalID   string           `json:"externalId"`
    Action       string           `json:"action"`       // "created" | "updated" | "merged" | "skipped"
    ProfileID    string           `json:"profileId"`
    Conflicts    []FieldConflict  `json:"conflicts,omitempty"`
    EnrichmentJobID string        `json:"enrichmentJobId,omitempty"`
}

type FieldConflict struct {
    Field    string      `json:"field"`
    Existing FieldSource `json:"existing"`
    Submitted FieldSource `json:"submitted"`
    Resolution string    `json:"resolution"` // "kept_existing" | "updated" | "flagged"
}
```

**Thêm vào EnrichmentServicer:**
```go
type EnrichmentServicer interface {
    // ... existing methods giữ nguyên ...

    // MỚI: Multi-source ingestion
    IngestProfiles(ctx context.Context, partnerID primitive.ObjectID, req *IngestionRequest) ([]IngestionResult, error)
}
```

**Ingestion flow:**
```
IngestProfiles()
  ├─ Validate input
  ├─ For each profile:
  │   ├─ Find existing by platform + externalID
  │   ├─ If not found → create new UnifiedProfile
  │   ├─ If found → conflict resolution:
  │   │   ├─ Compare confidence: new > existing → update
  │   │   ├─ new == existing → flag for ops
  │   │   └─ new < existing → skip (keep existing)
  │   ├─ Save FieldSources for each updated field
  │   ├─ Create PartnerProfileAccess (CONTRIBUTED)
  │   ├─ Save partner-specific metadata to PartnerProfileData
  │   ├─ Record ChangeRecord for audit
  │   ├─ Recalculate completeness score
  │   └─ If triggerEnrichment → submit to IM
  └─ Return results
```

---

## 4. Data Architecture

### 4.1 MongoDB Collections

```
at-core database
│
├── profiles                    🔧 MỞ RỘNG   Base profile (shared)
│   Indexes:
│   - { platform, externalId }  unique
│   - { visibility, completenessScore }
│   - { "profileData.categories" }
│   - { createdAt }
│
├── partner_profile_data        🆕 MỚI       Partner enrichment (isolated)
│   Indexes:
│   - { profileId, partnerId, dataKey }  unique
│   - { partnerId }
│
├── partner_profile_access      🆕 MỚI       Partner-profile relationship
│   Indexes:
│   - { partnerId, profileId }  unique
│   - { partnerId, accessType }
│   - { profileId }
│
├── profile_changes             🆕 MỚI       Audit trail for profile edits
│   Indexes:
│   - { profileId, changedAt }
│   - { changedBy }
│
├── enrichment_jobs             ✅ GIỮ NGUYÊN Job tracking
├── partners                    ✅ GIỮ NGUYÊN Partner accounts
├── partner_subscriptions       ✅ GIỮ NGUYÊN Subscription tiers
├── webhook_events              ✅ GIỮ NGUYÊN Webhook delivery
├── admin_users                 ✅ GIỮ NGUYÊN Admin accounts
├── admin_roles                 ✅ GIỮ NGUYÊN RBAC roles
├── admin_permissions           ✅ GIỮ NGUYÊN RBAC permissions
├── admin_sessions              ✅ GIỮ NGUYÊN Admin sessions
└── admin_activity_logs         ✅ GIỮ NGUYÊN Admin audit trail
```

### 4.2 Data Flow Diagram

```
                    INGESTION                          STORAGE                          OUTPUT
                    ─────────                          ───────                          ──────

Partner submit ─┐                              ┌─ profiles ──────────────┐
                │   ┌─────────────────┐        │  (base, shared)         │
Creator self ───┤──►│ Ingestion       │───────►│                         ├──► Partner API (scoped)
                │   │ Service         │        ├─ partner_profile_data   │      GET /v1/profiles
Admin import ───┤   │                 │        │  (private, per partner) │      base + own enrichment
                │   │ - validate      │        │                         │
IM webhook ─────┘   │ - normalize     │───────►├─ partner_profile_access │──► Pool Search
                    │ - conflict res  │        │  (who sees what)        │      GET /v1/pool/search
                    │ - confidence    │        │                         │      base only, PUBLIC
                    └────────┬────────┘        ├─ profile_changes       │
                             │                 │  (audit trail)         │──► Admin Dashboard
                    ┌────────▼────────┐        │                         │      all data + history
                    │ Vendor IM       │        └─────────────────────────┘
                    │ (enrichment,    │
                    │  scoring,       │──► Matching API proxy
                    │  matching)      │      POST /v1/matching/score
                    └─────────────────┘
```

### 4.3 Completeness Score Formula

```
Required fields (60%):
  platform + externalId         10%
  name + handle                 10%
  followers count               10%
  engagement rate               10%
  categories                    10%
  avatar                        10%

Optional fields (30%):
  contact email                  5%
  contact phone                  5%
  country                        5%
  description/bio                5%
  recent content                 5%
  demographics data              5%

Quality bonus (10%):
  has ops_verified fields        5%
  freshness < 7 days             5%
```

---

## 5. API Design

### 5.1 API Groups Overview

| Group | Base Path | Auth | Mô tả |
|-------|-----------|------|--------|
| **Partner API** | `/v1/` | API Key hoặc JWT | Partner truy cập profiles, pool, matching |
| **Ingestion API** | `/v1/profiles/ingest` | API Key hoặc JWT | Partner/system gửi profile data vào |
| **Admin API** | `/admin/` | Admin JWT | Quản trị hệ thống, ops override |
| **Vendor Webhook** | `/v1/webhooks/im` | HMAC signature | Nhận kết quả từ IM |
| **Health** | `/health` | None | Liveness & readiness |

### 5.2 Partner API (Mở rộng)

```
# Profile - danh sách & chi tiết
GET    /v1/profiles                          List profiles (scoped by partner)
       ?scope=my_profiles                      Chỉ profiles có relationship
       ?scope=pool                             Pool search (PUBLIC, base only)
       ?platform=tiktok
       ?categories=beauty
       ?minFollowers=10000
       ?sort=completenessScore:desc
GET    /v1/profiles/{id}                     Get profile detail (base + own enrichment)
GET    /v1/profiles/{platform}/{externalId}  Get by platform identity

# Profile actions
POST   /v1/profiles/{id}/save               Save profile từ pool → bookmarked
DELETE /v1/profiles/{id}/save               Remove from my list

# Partner enrichment data
GET    /v1/profiles/{id}/data               Get own partner data for profile
PUT    /v1/profiles/{id}/data               Upsert partner data (key-value)
DELETE /v1/profiles/{id}/data/{key}         Delete a partner data key

# Ingestion
POST   /v1/profiles/ingest                  Submit profiles (batch, max 100)

# Enrichment (existing, giữ nguyên)
POST   /v1/enrichment                       Enrich from URL (trigger IM)
GET    /v1/enrichment/jobs/{id}             Get job status

# Matching (existing, proxy to IM)
POST   /v1/matching/score                   Score single influencer
POST   /v1/matching/batch                   Score batch influencers
GET    /v1/matching/jobs/{id}               Get batch job status

# Pool (existing, giữ nguyên)
GET    /v1/pool/search                      Search influencer pool
POST   /v1/pool/request                     Request influencer profiles (quota check)

# Quota (existing, giữ nguyên)
GET    /v1/partners/quota                   Get quota status
```

### 5.3 Admin API (Mở rộng)

```
# Profile management (MỚI)
GET    /admin/profiles                       List all profiles (no partner scope)
GET    /admin/profiles/{id}                  Get full profile (all sources, all partner data)
GET    /admin/profiles/{id}/history          Get change history
PUT    /admin/profiles/{id}/fields           Ops override: edit field(s) with reason
POST   /admin/profiles/{id}/verify           Mark profile as ops-verified
POST   /admin/profiles/import               Bulk import from CSV

# Partner-profile access (MỚI)
GET    /admin/profiles/{id}/partners         List partners with access to profile
POST   /admin/profiles/{id}/assign           Assign profile to partner (admin_assigned)

# Existing admin endpoints (giữ nguyên)
POST   /admin/auth/login
POST   /admin/auth/refresh
POST   /admin/auth/logout
CRUD   /admin/users
CRUD   /admin/roles
GET    /admin/activity-logs
CRUD   /admin/partners
CRUD   /admin/webhooks
POST   /admin/enrichment
```

### 5.4 Response Format - Profile với Partner Scope

**Partner gọi `GET /v1/profiles/{id}` (ví dụ TCB):**

```json
{
  "id": "...",
  "platform": "tiktok",
  "externalId": "@ngoctrinhfashion",

  "base": {
    "name": "Ngọc Trinh",
    "handle": "@ngoctrinhfashion",
    "followers": 1200000,
    "engagementRate": 3.2,
    "categories": ["fashion", "lifestyle"],
    "country": "VN",
    "avatar": "https://...",
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
    "booking_price": { "value": 50000000, "updatedAt": "2026-03-01" },
    "campaigns_done": { "value": 3, "updatedAt": "2026-02-15" },
    "internal_rating": { "value": 4.5, "updatedAt": "2026-03-10" }
  },

  "opsVerified": {
    "verifiedAt": "2026-03-05",
    "verifiedBy": "ops@accesstrade.vn",
    "verifiedFields": ["categories", "country", "verified"]
  },

  "meta": {
    "completenessScore": 87.5,
    "visibility": "PUBLIC",
    "lastEnriched": "2026-03-10",
    "accessType": "CONTRIBUTED"
  }
}
```

**Lưu ý:** Field `enrichment` chỉ chứa data của partner đang gọi. TCB không thấy enrichment của Ambassabor.

**Admin gọi `GET /admin/profiles/{id}`:**

```json
{
  "id": "...",
  "base": { "..." },
  "score": { "..." },
  "fieldSources": {
    "categories": { "source": "ops_verified", "confidence": 0.9, "updatedAt": "..." },
    "followers": { "source": "crawl", "confidence": 0.6, "updatedAt": "..." }
  },
  "partnerData": {
    "tcb": {
      "booking_price": 50000000,
      "campaigns_done": 3
    },
    "ambassabor": {
      "self_declared_rate": 40000000
    }
  },
  "partnerAccess": [
    { "partnerId": "tcb", "accessType": "CONTRIBUTED" },
    { "partnerId": "ambassabor", "accessType": "CONTRIBUTED" }
  ],
  "changeHistory": [
    { "field": "categories", "oldValue": ["lifestyle"], "newValue": ["fashion"], "changedBy": "ops@at.vn", "reason": "Verified from content analysis" }
  ]
}
```

### 5.5 Authentication & Authorization

**Không thay đổi** so với hiện tại. Giữ nguyên hệ thống đã có:

| Method | Dùng cho | Headers |
|--------|----------|---------|
| **API Key** | Partner server-to-server | `X-Partner-ID` + `X-API-Key` |
| **JWT (Partner)** | Partner web client | `Authorization: Bearer {token}` hoặc cookie `access_token` |
| **JWT (Admin)** | Admin dashboard | `Authorization: Bearer {token}` hoặc cookie `admin_access_token` |
| **HMAC-SHA256** | IM webhook | `X-Api-Key` + HMAC signature trên body |

**Thêm permissions mới cho Admin RBAC:**

```
profiles:read           # Xem profiles
profiles:write          # Sửa profile fields (ops override)
profiles:verify         # Đánh dấu ops-verified
profiles:import         # Bulk import
profiles:history        # Xem change history
partner_data:read       # Xem partner enrichment data (admin only)
access:read             # Xem partner-profile relationships
access:write            # Assign/remove partner access
```

---

## 6. Luồng xử lý chính

### 6.1 Partner gửi Influencer mới (Ingestion)

```
POST /v1/profiles/ingest
Header: X-Partner-ID: tcb

┌──────────┐     ┌──────────────┐     ┌───────────────┐     ┌──────────────┐
│ Partner  │────►│ PartnerAuth  │────►│ Ingestion     │────►│ Profile      │
│ (TCB)    │     │ Middleware   │     │ Handler       │     │ Store        │
└──────────┘     └──────────────┘     └───────┬───────┘     └──────────────┘
                                              │
                                    ┌─────────▼──────────┐
                                    │ EnrichmentService   │
                                    │ .IngestProfiles()   │
                                    │                     │
                                    │ For each profile:   │
                                    │ 1. Find existing    │
                                    │ 2. Conflict resolve │
                                    │ 3. Save/update      │
                                    │ 4. Create access    │──► access collection
                                    │ 5. Save partner data│──► partnerdata collection
                                    │ 6. Record changes   │──► profile_changes collection
                                    │ 7. Calc completeness│
                                    │ 8. Trigger IM?      │──► Vendor IM (async)
                                    └─────────────────────┘
```

### 6.2 Operations Override (Ops sửa profile)

```
PUT /admin/profiles/{id}/fields
Header: Admin JWT

┌──────────┐     ┌──────────────┐     ┌───────────────┐
│ Ops User │────►│ AdminAuth    │────►│ Admin Profile │
│          │     │ + Permission │     │ Handler       │
└──────────┘     │ (profiles:   │     └───────┬───────┘
                 │  write)      │             │
                 └──────────────┘    ┌────────▼─────────┐
                                     │ ProfileService    │
                                     │ .UpdateField()    │
                                     │                   │
                                     │ 1. Get current    │
                                     │ 2. Check: new     │
                                     │    confidence >   │
                                     │    existing?      │
                                     │ 3. Update field   │
                                     │ 4. Set source=    │
                                     │    ops_verified   │
                                     │ 5. Record change  │──► profile_changes
                                     │ 6. Log activity   │──► admin_activity_logs
                                     │ 7. Recalc         │
                                     │    completeness   │
                                     └───────────────────┘
```

### 6.3 Partner truy vấn Profile (Scoped)

```
GET /v1/profiles?scope=my_profiles
Header: X-Partner-ID: tcb

┌──────────┐     ┌──────────────┐     ┌───────────────┐
│ Partner  │────►│ PartnerAuth  │────►│ Profile       │
│ (TCB)    │     │ Middleware   │     │ Handler       │
└──────────┘     └──────────────┘     └───────┬───────┘
                                              │
                  ┌───────────────────────────▼──────────────────────────┐
                  │ scope == "my_profiles"?                              │
                  │                                                      │
                  │ YES:                          NO (scope == "pool"):  │
                  │ 1. Query access collection    1. Query profiles      │
                  │    WHERE partnerId = tcb         WHERE visibility    │
                  │ 2. Get profileIDs                = PUBLIC            │
                  │ 3. Query profiles by IDs      2. Return base only   │
                  │ 4. Attach own partner data       (no enrichment)    │
                  │    from partnerdata                                  │
                  │ 5. Return base + enrichment                         │
                  └─────────────────────────────────────────────────────┘
```

### 6.4 IM Webhook (Giữ nguyên, refine)

```
POST /v1/webhooks/im
Vendor IM gửi kết quả crawl/scoring

┌──────────┐     ┌──────────────┐     ┌───────────────┐
│ Vendor   │────►│ HMAC Verify  │────►│ IM Webhook    │
│ IM       │     │ + API Key    │     │ Handler       │
└──────────┘     └──────────────┘     └───────┬───────┘
                                              │
                                    ┌─────────▼──────────┐
                                    │ EnrichmentService   │
                                    │                     │
                                    │ profile.created:    │
                                    │ 1. Find job         │
                                    │ 2. Transform data   │
                                    │ 3. Update profile   │
                                    │    (source=crawl,   │
                                    │     confidence=0.6) │
                                    │ 4. Conflict resolve │
                                    │    (giữ ops_verified│
                                    │     nếu có)        │
                                    │ 5. Job → COMPLETED  │
                                    │ 6. Webhook → partner│
                                    │                     │
                                    │ job.failed:         │
                                    │ 1. Job → FAILED     │
                                    │ 2. Schedule retry   │
                                    └─────────────────────┘
```

**Thay đổi quan trọng ở bước 4:** Khi IM webhook trả về data, conflict resolution phải kiểm tra: nếu field đã có ops_verified (confidence 0.9), crawl data (confidence 0.6) **không được ghi đè**.

---

## 7. NFR & Security

### 7.1 Data Isolation (Critical)

| Measure | Implementation |
|---------|---------------|
| **Partner data isolation** | `partner_profile_data` collection scoped bởi `partnerId`. Mọi query PHẢI có partnerId filter |
| **Access control** | `partner_profile_access` xác định partner nào thấy profile nào. Middleware inject partnerId vào context |
| **Response filtering** | Handler PHẢI filter enrichment data theo partnerId trước khi trả response |
| **Admin bypass** | Admin API trả về tất cả data (cho ops), nhưng cần permission `partner_data:read` |

**Validation rule:** Không có query nào tới `partner_profile_data` mà không có `partnerId` trong WHERE clause. Code review phải enforce.

### 7.2 Audit Trail

| Event | Collection | Fields |
|-------|-----------|--------|
| Profile field changed | `profile_changes` | profileId, field, oldValue, newValue, source, changedBy, reason |
| Admin action | `admin_activity_logs` | adminId, action, resource, result, IP, timestamp |
| Partner ingestion | `profile_changes` | profileId, source="partner_xxx", batch reference |
| IM crawl update | `profile_changes` | profileId, source="crawl", jobId |

### 7.3 Performance

| Concern | Solution | Target |
|---------|----------|--------|
| Profile query latency | Redis cache cho frequently accessed profiles | < 100ms p95 |
| Pool search | MongoDB compound indexes + text search | < 500ms p95 |
| Batch ingestion | Bulk write operations, async IM trigger | 100 profiles < 5s |
| Completeness recalc | Computed on write, cached on read | < 10ms |

### 7.4 Availability

Giữ nguyên approach hiện tại:
- Circuit breaker cho IM client (gobreaker)
- Retry với exponential backoff
- **Mới:** IM down → at-core vẫn serve cached profiles + partner data. Chỉ enrichment/matching bị ảnh hưởng

### 7.5 Security (Giữ nguyên + mở rộng)

Giữ nguyên tất cả security measures hiện có:
- Password hashing (bcrypt cost 12)
- Account lockout (5 failed → 15min lock)
- IP throttling (20 failed/hour/IP)
- HMAC-SHA256 webhook validation
- API key hashing
- Contact info encryption (AES-256)
- HttpOnly + Secure + SameSite cookies
- CORS

**Thêm:**
- Encrypt partner data values có tag `sensitive` (giá booking, contact riêng)
- Rate limit ingestion API riêng (10 req/min/partner) để tránh abuse

---

## 8. Migration Strategy

### 8.1 Backward Compatibility

Tất cả thay đổi phải **backward compatible**. Existing partners (TCB) không cần thay đổi code.

| API hiện tại | Sau migration | Breaking change? |
|-------------|--------------|-------------------|
| `GET /v1/profiles` | Thêm `?scope=` param, default = hiện tại | Không |
| `GET /v1/profiles/{platform}/{externalId}` | Giữ nguyên, thêm enrichment nếu có | Không |
| `POST /admin/enrichment` | Giữ nguyên | Không |
| `GET /v1/pool/search` | Giữ nguyên, dùng visibility filter | Không |
| `POST /v1/matching/*` | Giữ nguyên (proxy IM) | Không |

### 8.2 Phased Rollout

**Phase 1: Foundation (2-3 tuần)**
1. Thêm collections: `partner_profile_access`, `partner_profile_data`, `profile_changes`
2. Thêm fields vào `UnifiedProfile`: `visibility`, `completenessScore`, `fieldSources`
3. Migration script: tạo `partner_profile_access` cho TCB existing profiles
4. Build `POST /v1/profiles/ingest` API
5. Build `PUT /admin/profiles/{id}/fields` (ops override)

**Phase 2: Partner Integration (1-2 tuần)**
6. Thêm `?scope=` parameter cho `GET /v1/profiles`
7. Build partner data CRUD: `GET/PUT/DELETE /v1/profiles/{id}/data`
8. Build `POST /admin/profiles/import` (CSV bulk)
9. Completeness score calculation

**Phase 3: Quality & Scale (2-3 tuần)**
10. Admin dashboard: conflict resolution UI
11. Freshness tracking + auto re-crawl trigger
12. Onboard Ambassabor: creator self-service flow
13. Onboard Vinfast: new partner setup

---

## 9. Dependency Diagram

```
                                 ┌──────────────────────┐
                                 │       main.go         │
                                 │   (DI Container)      │
                                 └──────────┬───────────┘
                                            │ wires
                    ┌───────────────────────┼───────────────────────┐
                    │                       │                       │
          ┌─────────▼──────────┐  ┌─────────▼──────────┐  ┌───────▼────────┐
          │   API Handlers     │  │   Middleware        │  │   Infra        │
          │                    │  │                     │  │                │
          │ - ProfileHandler   │  │ - PartnerAuth       │  │ - MongoDB      │
          │ - IngestionHandler │  │ - AdminAuth         │  │ - Redis        │
          │ - PoolHandler      │  │ - PermissionGuard   │  │ - IMClient     │
          │ - MatchingHandler  │  │ - RateLimit         │  │ - Email        │
          │ - AdminProfile     │  │ - CORS, Logging     │  │ - Webhook      │
          │   Handler          │  │                     │  │   Dispatcher   │
          └─────────┬──────────┘  └─────────────────────┘  └───────┬────────┘
                    │ depends on                                    │
          ┌─────────▼─────────────────────────────────────────────▼─┐
          │                    Domain Services                       │
          │                                                          │
          │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
          │  │ Profile      │  │ Enrichment   │  │ Partner      │   │
          │  │ Service      │  │ Service      │  │ Service      │   │
          │  │              │  │              │  │              │   │
          │  │ - GetProfile │  │ - Ingest     │  │ - Validate   │   │
          │  │ - UpdateField│  │ - EnrichURL  │  │   APIKey     │   │
          │  │ - CalcScore  │  │ - Webhook    │  │ - GetPartner │   │
          │  └──────┬───────┘  └──────┬───────┘  └──────────────┘   │
          │         │                 │                               │
          │  ┌──────▼───────┐  ┌──────▼───────┐                     │
          │  │ PartnerData  │  │ Access       │                     │
          │  │ Service      │  │ Service      │                     │
          │  │              │  │              │                     │
          │  │ - Upsert     │  │ - Grant      │                     │
          │  │ - GetByProf  │  │ - HasAccess  │                     │
          │  │ - Delete     │  │ - ListByPart │                     │
          │  └──────────────┘  └──────────────┘                     │
          │                                                          │
          │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
          │  │ Pool         │  │ Quota        │  │ Webhook      │   │
          │  │ Service      │  │ Service      │  │ Service      │   │
          │  └──────────────┘  └──────────────┘  └──────────────┘   │
          │                                                          │
          │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
          │  │ Admin        │  │ Subscription │  │ (Session,    │   │
          │  │ Service      │  │ Service      │  │  Security)   │   │
          │  └──────────────┘  └──────────────┘  └──────────────┘   │
          └──────────────────────────────────────────────────────────┘
                    │ depends on (interfaces)
          ┌─────────▼──────────────────────────────────────────────────┐
          │                Repository Interfaces                        │
          │  (defined in each domain, implemented in infra/mongodb)     │
          └─────────────────────────────────────────────────────────────┘
```

---

## 10. Trade-offs & Decisions

### Decision 1: MongoDB flexible document vs. strict relational

**Chọn:** Giữ MongoDB (đã có)

**Được:**
- Profile data có nhiều optional fields → flexible schema phù hợp
- `fieldSources` map dễ embed trong document
- Partner data key-value → schema-less tự nhiên

**Mất:**
- Không có foreign key enforcement → phải enforce ở application layer
- Cross-collection joins phải dùng aggregation pipeline

**Rationale:** Đã proven với codebase hiện tại, không có lý do migrate.

### Decision 2: Partner data riêng collection vs. embed trong profile

**Chọn:** Collection riêng (`partner_profile_data`)

**Được:**
- Isolation rõ ràng: không thể vô tình leak data qua profile query
- Scale: mỗi partner có thể có nhiều data keys
- Permission dễ enforce: query riêng, không cần filter trong profile

**Mất:**
- Thêm 1 query khi lấy profile + enrichment (2 queries thay vì 1)
- Phải join ở application layer

**Rationale:** Data isolation là requirement critical. 1 query thêm (< 5ms từ MongoDB) chấp nhận được.

### Decision 3: Ingestion API chung vs. API riêng cho mỗi source

**Chọn:** API chung `POST /v1/profiles/ingest` với `source` field

**Được:**
- 1 API, mọi partner dùng chung → ít code maintain
- Thêm partner mới không cần thêm endpoint
- Conflict resolution logic tập trung

**Mất:**
- Validation phải handle nhiều source types trong 1 handler
- Partner-specific logic (nếu có) phải dùng adapter pattern

**Rationale:** Simplicity. Partner-specific logic hiện tại không phức tạp đến mức cần API riêng.

---

## Checklist

- [x] Tất cả domains hiện tại được giữ nguyên hoặc mở rộng (không break)
- [x] 2 domain mới (partnerdata, access) có model + repository + indexes
- [x] Data isolation enforced ở mọi layer (middleware → service → repository)
- [x] Field-level source tracking + confidence scoring
- [x] Ops override với audit trail
- [x] Backward compatible API changes
- [x] Phased migration plan
- [x] Security không giảm (chỉ thêm)
- [x] Trade-offs documented

---

*Tài liệu thuộc dự án at-core - AccessTrade Projects*
*Dựa trên: business-overview.md + codebase analysis + brainstorming insights*
