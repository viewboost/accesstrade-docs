# System Architecture: Pub2 Affiliate Integration — Ambassador

**Date:** 2026-03-25
**Architect:** vinhnguyen
**Version:** 1.0
**Project Type:** Feature Integration
**Project Level:** Level 3
**Status:** Draft

---

## Document Overview

Tài liệu này định nghĩa system architecture cho việc tích hợp Pub2 Affiliate vào Ambassador platform. Tất cả components được thêm vào hệ thống hiện tại (Go backend, React frontend, MongoDB) mà không ảnh hưởng đến chức năng đang chạy.

**Related Documents:**
- PRD: [prd-affiliate-integration-2026-03-25.md](./prd-affiliate-integration-2026-03-25.md)
- API Reference: [api-reference.md](./api-reference.md)

---

## Executive Summary

Tích hợp Pub2 Affiliate vào Ambassador bằng cách:

1. **Backend**: Thêm Go module `pub2` (HMAC client) + service/handler cho affiliate campaigns, links, reports
2. **Frontend**: Thêm section "Affiliate Campaign" vào trang chi tiết campaign hiện tại
3. **Admin**: Thêm trang quản lý affiliate campaigns + mapping với campaigns/events
4. **Database**: Thêm 3 MongoDB collections mới (không sửa collections hiện tại)

**Pattern**: Modular extension trên monolith hiện tại — thêm module mới, không thay đổi kiến trúc.

---

## Architectural Drivers

| # | NFR | Requirement | Impact |
|---|-----|-------------|--------|
| 1 | **NFR-002: Security** | HMAC auth, credential protection, sso_user_id inject từ backend | Quyết định toàn bộ Pub2 client design |
| 2 | **NFR-004: Reliability** | Pub2 là external dependency, cần retry + circuit breaker | Quyết định error handling pattern |
| 3 | **NFR-007: Compatibility** | Zero regression — không sửa schema/routes hiện tại | Quyết định cách tổ chức code (additive only) |
| 4 | **NFR-001: Performance** | Proxy API < 3s, dashboard aggregate < 5s | Quyết định parallel call strategy |
| 5 | **NFR-003: Tenant isolation** | sub2 parameter identify Ambassador | Quyết định tracking strategy |

---

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Pub2 (AccessTrade)                        │
│                   core-aff.dev.accesstrade.me                    │
│                                                                  │
│  API 2: Link  │  API 3.x: Reports  │  API 8: Orders            │
└───────────────────────────┬──────────────────────────────────────┘
                            │ HMAC-SHA256
                            │
┌───────────────────────────┴──────────────────────────────────────┐
│                    Ambassador Backend (Go)                        │
│                                                                  │
│  ┌──────────────────┐  ┌───────────────────┐  ┌──────────────┐  │
│  │ internal/module/  │  │ internal/service/  │  │ pkg/public/  │  │
│  │   pub2/           │  │   affiliate.go     │  │  handler/    │  │
│  │   ├── client.go   │  │                    │  │  router/     │  │
│  │   ├── hmac.go     │  │ pkg/admin/         │  │  service/    │  │
│  │   └── models.go   │  │   service/         │  │              │  │
│  │                    │  │   handler/         │  │              │  │
│  └──────────────────┘  └───────────────────┘  └──────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                    MongoDB                                │    │
│  │  affiliate_campaigns  │  affiliate_links  │  cam_aff_map │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
        │                                           │
        │ REST API                                  │ REST API
        ▼                                           ▼
┌──────────────────┐                    ┌──────────────────┐
│ Ambassador       │                    │ Ambassador       │
│ Frontend (React) │                    │ Admin (React)    │
│                  │                    │                  │
│ Campaign Detail  │                    │ Affiliate CRUD   │
│  └─ Affiliate    │                    │ Campaign Mapping │
│     Section      │                    │                  │
└──────────────────┘                    └──────────────────┘
```

### Architectural Pattern

**Pattern:** Modular Extension on Existing Monolith

**Rationale:**
- Ambassador đã là monolith (Go + Echo + MongoDB). Thêm module mới vào hệ thống hiện tại là cách đơn giản và low-risk nhất.
- Không cần microservice vì đây là feature bổ sung, không phải hệ thống mới.
- Pub2 client được tách thành module riêng (`internal/module/pub2/`) để dễ maintain và reuse.

---

## Technology Stack

### Frontend

**Choice:** React + UmiJS (hiện tại)

Không thêm library mới. Sử dụng:
- UmiJS routing cho trang affiliate
- SCSS + Bootstrap cho styling
- Redux/UmiJS models cho state

### Backend

**Choice:** Go 1.24+ + Echo v4 (hiện tại)

Thêm:
- `crypto/hmac` + `crypto/sha256` (Go stdlib) cho HMAC signature
- `github.com/google/uuid` cho `client-trace-no` (đã có trong project)

### Database

**Choice:** MongoDB (hiện tại)

Thêm 3 collections mới. Không sửa collections hiện tại.

### Third-Party Services

| Service | Purpose | Protocol |
|---------|---------|----------|
| Pub2 API | Affiliate link, reports | REST + HMAC-SHA256 |
| AccessTrade SSO | Account linking (đã có) | OAuth2 |

---

## System Components

### Component 1: Pub2 API Client

**Location:** `backend/internal/module/pub2/`

**Purpose:** Go client gọi Pub2 APIs với HMAC-SHA256 authentication.

**Files:**
```
internal/module/pub2/
├── client.go        // Pub2Client struct, HTTP methods
├── hmac.go          // HMAC-SHA256 signature generation
├── models.go        // Request/Response structs
└── errors.go        // Error handling, Pub2 error codes
```

**Responsibilities:**
- Tạo HMAC signature per request
- Gọi Pub2 APIs (link, reports, orders)
- Parse response chuẩn (status/code/message)
- Retry logic (max 3, exponential backoff)
- Timeout handling (10s default)
- Logging request/response

**Interface:**
```go
type Pub2Client interface {
    GenerateAffiliateLink(ctx context.Context, req GenerateLinkRequest) (*GenerateLinkResponse, error)
    GetClickStats(ctx context.Context, req ReportRequest) (*ClickStatsResponse, error)
    GetConversionStats(ctx context.Context, req ReportRequest) (*ConversionStatsResponse, error)
    GetSaleAmountStats(ctx context.Context, req ReportRequest) (*SaleAmountStatsResponse, error)
    GetCommissionStats(ctx context.Context, req ReportRequest) (*CommissionStatsResponse, error)
    GetConversionsList(ctx context.Context, req ConversionsListRequest) (*ConversionsListResponse, error)
}
```

**Config:**

> **Lưu ý:** Đây là config riêng cho affiliate, KHÔNG dùng chung với `AccessTradePub2` (SSO). `AccessTradePub2` dùng cho liên kết tài khoản, `AffiliateConfig` dùng cho affiliate APIs.

```go
// internal/config/env.go — struct MỚI, thêm vào ENV chính
type AffiliateConfig struct {
    Endpoint     string `env:"AFFILIATE_ENDPOINT"`
    ClientID     string `env:"AFFILIATE_CLIENT_ID"`
    ClientSecret string `env:"AFFILIATE_CLIENT_SECRET"`
    PartnerCode  string `env:"AFFILIATE_PARTNER_CODE" envDefault:"PARTNER_1_POINT_5"`
    Timeout      int    `env:"AFFILIATE_TIMEOUT" envDefault:"10"`
    MaxRetries   int    `env:"AFFILIATE_MAX_RETRIES" envDefault:"3"`
}
```
```

**FRs Addressed:** FR-014

---

### Component 2: Affiliate Service (Internal)

**Location:** `backend/internal/service/affiliate.go`

**Purpose:** Business logic cho affiliate campaigns, links, reports.

**Responsibilities:**
- CRUD affiliate campaigns (MongoDB)
- Campaign-Event mapping (MongoDB)
- Generate affiliate link (delegate to Pub2Client)
- Lưu links vào DB
- Aggregate reports từ Pub2
- Validate user đã link AccessTrade

**Key Methods:**
```go
type AffiliateService interface {
    // Campaign CRUD
    CreateCampaign(ctx context.Context, campaign *AffiliateCampaign) error
    UpdateCampaign(ctx context.Context, id string, update *AffiliateCampaignUpdate) error
    GetCampaign(ctx context.Context, id string) (*AffiliateCampaign, error)
    ListCampaigns(ctx context.Context, filter CampaignFilter) (*CampaignListResult, error)
    UpdateCampaignStatus(ctx context.Context, id string, status string) error

    // Campaign-Event Mapping
    LinkCampaignToEvent(ctx context.Context, mapping *CampaignAffiliateMapping) error
    UnlinkCampaignFromEvent(ctx context.Context, mappingID string) error
    GetAffiliateCampaignsByEvent(ctx context.Context, eventID string) ([]*AffiliateCampaign, error)
    GetEventsByAffiliateCampaign(ctx context.Context, affCampaignID string) ([]string, error)

    // Affiliate Links
    GenerateLink(ctx context.Context, userID string, campaignID string) (*AffiliateLink, error)
    GetUserLinks(ctx context.Context, userID string, filter LinkFilter) (*LinkListResult, error)

    // Reports (proxy to Pub2)
    GetClickReport(ctx context.Context, userID string, req ReportRequest) (*ClickStatsResponse, error)
    GetConversionReport(ctx context.Context, userID string, req ReportRequest) (*ConversionStatsResponse, error)
    GetSaleAmountReport(ctx context.Context, userID string, req ReportRequest) (*SaleAmountStatsResponse, error)
    GetCommissionReport(ctx context.Context, userID string, req ReportRequest) (*CommissionStatsResponse, error)
    GetOrdersList(ctx context.Context, userID string, req OrdersListRequest) (*ConversionsListResponse, error)
}
```

**FRs Addressed:** FR-001, FR-002, FR-003, FR-005, FR-006, FR-007, FR-008, FR-009, FR-010, FR-011, FR-012

---

### Component 3: Affiliate Handlers (Public + Admin)

**Location:**
- `backend/pkg/public/handler/affiliate.go` — Influencer APIs
- `backend/pkg/public/router/affiliate.go` — Influencer routes
- `backend/pkg/admin/handler/affiliate.go` — Admin APIs
- `backend/pkg/admin/router/affiliate.go` — Admin routes

**Purpose:** HTTP handlers cho affiliate endpoints.

**FRs Addressed:** FR-015, FR-016

---

### Component 4: Frontend — Affiliate Section in Campaign Detail

**Location:** `frontend/src/pages/campaign-detail/components/affiliate-section/`

**Purpose:** Section hiển thị affiliate campaign(s) trong trang chi tiết campaign hiện tại.

**Files:**
```
frontend/src/pages/campaign-detail/components/affiliate-section/
├── index.tsx                    // Main section component
├── affiliate-campaign-card.tsx  // Card hiển thị 1 affiliate campaign
├── generate-link-modal.tsx      // Modal tạo link + copy
├── link-accesstrade-banner.tsx  // Banner yêu cầu liên kết AT
├── link-accesstrade-popup.tsx   // Popup khi action mà chưa link
└── styles.scss
```

**Behavior:**
1. Gọi API `GET /events/:id/affiliate-campaigns`
2. Nếu không có affiliate campaigns → không render section
3. Nếu có → hiển thị section với:
   - Banner "Liên kết AccessTrade" nếu chưa link (check `user.accesstrade.id`)
   - Danh sách affiliate campaign cards
   - CTA "Tạo link" → check AT linked → generate hoặc show popup

**FRs Addressed:** FR-004, FR-013

---

### Component 5: Frontend — Affiliate Reports Page

**Location:** `frontend/src/pages/affiliate-reports/`

**Purpose:** Trang báo cáo affiliate cho influencer (link từ campaign detail hoặc menu).

**Files:**
```
frontend/src/pages/affiliate-reports/
├── index.tsx              // Dashboard overview
├── components/
│   ├── summary-cards.tsx  // Cards: clicks, conversions, commission, sale amount
│   ├── click-chart.tsx    // Biểu đồ click theo ngày
│   ├── orders-table.tsx   // Bảng danh sách đơn hàng
│   └── date-filter.tsx    // Bộ lọc thời gian
└── styles.scss
```

**FRs Addressed:** FR-007, FR-008, FR-009, FR-010, FR-011, FR-012

---

### Component 6: Admin — Affiliate Campaign Management

**Location:** `admin/src/pages/affiliate-campaign/`

**Purpose:** Admin CRUD affiliate campaigns + mapping với events.

**Files:**
```
admin/src/pages/affiliate-campaign/
├── index.tsx                    // List view
├── detail/
│   ├── index.tsx                // Create/Edit form
│   └── components/
│       ├── basic-info-form.tsx  // Title, description, banner, category
│       ├── pub2-config-form.tsx // pub2_campaign_id, pub2_campaign_url, commission
│       └── linked-events.tsx    // Danh sách events đã liên kết + link/unlink
└── styles.scss
```

**Thêm vào Admin Event Detail:**
- `admin/src/pages/event/detail/components/tabs/affiliate-campaigns.tsx` — Tab hiển thị affiliate campaigns liên kết

**FRs Addressed:** FR-001, FR-002, FR-003

---

## Data Architecture

### Data Model

#### Collection: `affiliate_campaigns`

```javascript
{
    _id: ObjectId,
    title: String,                    // Tên campaign (do admin đặt)
    description: String,              // Mô tả (rich text)
    banner: String,                   // URL banner image
    category: String,                 // Danh mục (e.g., "credit_card", "insurance")
    commissionType: String,           // "CPA" | "CPL" | "CPI"
    commissionRate: String,           // "250,000đ / thẻ approved"
    pub2CampaignId: String,           // Pub2 campaign ID (unique, required)
    pub2CampaignUrl: String,          // Original URL cho tracking (required)
    status: String,                   // "draft" | "active" | "inactive"
    startAt: Date,                    // Ngày bắt đầu
    endAt: Date,                      // Ngày kết thúc (nullable)
    createdBy: ObjectId,              // Admin user ID
    createdAt: Date,
    updatedAt: Date
}

// Indexes
{ pub2CampaignId: 1 }               // unique
{ status: 1, createdAt: -1 }        // list active campaigns
{ category: 1 }                      // filter by category
```

#### Collection: `campaign_affiliate_mappings`

```javascript
{
    _id: ObjectId,
    eventId: ObjectId,                // Campaign/Event ID (ref: events)
    affiliateCampaignId: ObjectId,    // Affiliate Campaign ID (ref: affiliate_campaigns)
    createdBy: ObjectId,              // Admin user ID
    createdAt: Date
}

// Indexes
{ eventId: 1, affiliateCampaignId: 1 }   // unique compound — tránh duplicate mapping
{ eventId: 1 }                             // query by event
{ affiliateCampaignId: 1 }                // query by affiliate campaign
```

#### Collection: `affiliate_links`

```javascript
{
    _id: ObjectId,
    userId: ObjectId,                 // Influencer user ID (ref: users)
    affiliateCampaignId: ObjectId,    // Affiliate Campaign ID
    ssoUserId: Number,                // AccessTrade SSO user ID (từ user data)
    affiliateLink: String,            // Link dài từ Pub2
    shortAffiliateLink: String,       // Link ngắn từ Pub2
    sub1: String,                     // Tracking: sso_user_id
    sub2: String,                     // Tracking: platform identifier
    sub3: String,                     // Tracking: reserved
    sub4: String,                     // Tracking: reserved
    createdAt: Date
}

// Indexes
{ userId: 1, affiliateCampaignId: 1 }    // query user's links per campaign
{ userId: 1, createdAt: -1 }              // list user's all links
```

### Entity Relationships

```
users (existing)
  │
  ├── 1:N ──→ affiliate_links
  │             │
  │             └── N:1 ──→ affiliate_campaigns
  │
  events (existing)
  │
  └── M:N ──→ affiliate_campaigns
        via campaign_affiliate_mappings
```

### Data Flow

```
1. ADMIN: Tạo affiliate campaign
   Admin → POST /admin/affiliate-campaigns → MongoDB:affiliate_campaigns

2. ADMIN: Liên kết với event
   Admin → POST /admin/campaign-affiliate-mappings → MongoDB:campaign_affiliate_mappings

3. INFLUENCER: Xem affiliate trong campaign detail
   Frontend → GET /events/:id/affiliate-campaigns
   Backend → MongoDB:campaign_affiliate_mappings (lookup eventId)
           → MongoDB:affiliate_campaigns (get details, filter status=active)
           → Return to frontend

4. INFLUENCER: Tạo affiliate link
   Frontend → POST /affiliate-campaigns/:id/generate-link
   Backend → Validate user.accesstrade.id exists
           → Get campaign.pub2CampaignId, campaign.pub2CampaignUrl
           → Pub2Client.GenerateAffiliateLink()
           → Save to MongoDB:affiliate_links
           → Return link to frontend

5. INFLUENCER: Xem reports
   Frontend → POST /affiliate-reports/clicks
   Backend → Get user.accesstrade.id (sso_user_id)
           → Pub2Client.GetClickStats(sso_user_id, ...)
           → Return Pub2 response to frontend (passthrough)
```

---

## API Design

### API Architecture

- **Protocol:** REST (JSON)
- **Auth:** JWT Bearer token (hệ thống hiện tại)
- **Versioning:** Không version riêng — dùng prefix path
- **Rate limiting:** Dùng middleware hiện tại

### Admin Endpoints

| Method | Path | Description | FR |
|--------|------|-------------|-----|
| POST | `/admin/affiliate-campaigns` | Tạo affiliate campaign | FR-001 |
| GET | `/admin/affiliate-campaigns` | Danh sách campaigns (filter, search, pagination) | FR-002 |
| GET | `/admin/affiliate-campaigns/:id` | Chi tiết campaign | FR-002 |
| PUT | `/admin/affiliate-campaigns/:id` | Cập nhật campaign | FR-001 |
| PATCH | `/admin/affiliate-campaigns/:id/status` | Thay đổi status | FR-001 |
| POST | `/admin/campaign-affiliate-mappings` | Liên kết affiliate campaign ↔ event | FR-003 |
| DELETE | `/admin/campaign-affiliate-mappings/:id` | Gỡ liên kết | FR-003 |
| GET | `/admin/events/:id/affiliate-campaigns` | Danh sách affiliate campaigns liên kết với event | FR-003 |
| GET | `/admin/affiliate-campaigns/:id/events` | Danh sách events liên kết với affiliate campaign | FR-003 |

### Public (Influencer) Endpoints

| Method | Path | Description | FR |
|--------|------|-------------|-----|
| GET | `/events/:id/affiliate-campaigns` | Affiliate campaigns active liên kết với event | FR-004 |
| GET | `/affiliate-campaigns/:id` | Chi tiết affiliate campaign | FR-004 |
| POST | `/affiliate-campaigns/:id/generate-link` | Tạo affiliate link | FR-005 |
| GET | `/affiliate-links` | Danh sách links đã tạo (pagination) | FR-006 |
| POST | `/affiliate-reports/clicks` | Báo cáo click | FR-007 |
| POST | `/affiliate-reports/conversions` | Báo cáo conversion | FR-008 |
| POST | `/affiliate-reports/sale-amount` | Báo cáo sale amount | FR-009 |
| POST | `/affiliate-reports/commission` | Báo cáo commission | FR-010 |
| POST | `/affiliate-reports/orders` | Danh sách đơn hàng | FR-011 |

### Key API Contracts

#### POST `/affiliate-campaigns/:id/generate-link`

**Request:** (no body — campaign ID from URL, user from JWT)

**Response:**
```json
{
    "data": {
        "_id": "link_id",
        "affiliateLink": "https://me-tracking.dev.accesstrade.me/deep_link/...",
        "shortAffiliateLink": "https://me-slink.vpbank.com/taYj3UJV",
        "affiliateCampaignId": "campaign_id",
        "createdAt": "2026-03-25T10:00:00Z"
    }
}
```

**Logic:**
1. Get user from JWT → check `user.accesstrade.id` exists → 403 if not
2. Get affiliate campaign → check status = active → 404 if not
3. Check existing link (userId + campaignId) → return existing if found (idempotent)
4. Call Pub2Client.GenerateAffiliateLink:
   - `partner_code`: from config
   - `original_url`: campaign.pub2CampaignUrl
   - `partner_ref_campaign_id`: campaign.pub2CampaignId
   - `sso_user_id`: user.accesstrade.id
   - `sub1`: fmt.Sprintf("%d", user.accesstrade.id)
   - `sub2`: "ambassador"
5. Save link to `affiliate_links`
6. Return link

#### POST `/affiliate-reports/clicks`

**Request:**
```json
{
    "fromDate": "2026-01-01T00:00:00+0700",
    "toDate": "2026-03-25T23:59:59+0700",
    "campaignIds": ["pub2_campaign_id_1"]
}
```

**Response:** Passthrough từ Pub2 response (statistics + meta)

**Logic:**
1. Get user.accesstrade.id → inject `sso_user_id`
2. Validate date range ≤ 3 tháng
3. Map campaignIds từ affiliate_campaign IDs → pub2CampaignIds
4. Call Pub2Client.GetClickStats
5. Return response

### Authentication & Authorization

- **Influencer APIs** (`/events/...`, `/affiliate-campaigns/...`, `/affiliate-links`, `/affiliate-reports/...`): JWT Bearer token (auth middleware hiện tại)
- **Admin APIs** (`/admin/affiliate-campaigns/...`, `/admin/campaign-affiliate-mappings/...`): JWT + admin role check (admin middleware hiện tại)
- **Pub2 APIs**: HMAC-SHA256 (handled by Pub2Client internally, transparent to handlers)

---

## Non-Functional Requirements Coverage

### NFR-001: Performance — API Response Time

**Requirement:** Internal APIs < 200ms, proxy APIs < 3s, dashboard aggregate < 5s

**Architecture Solution:**
- Internal APIs (CRUD, list): Direct MongoDB queries với proper indexes → < 200ms
- Proxy APIs: Single Pub2 call + overhead → bounded by Pub2 latency + ~100ms
- Dashboard aggregate (FR-012): Gọi 4 Pub2 APIs **parallel** bằng Go goroutines + errgroup

**Implementation:**
```go
// Dashboard: parallel calls
g, ctx := errgroup.WithContext(ctx)
var clicks, conversions, saleAmount, commission interface{}

g.Go(func() error { clicks, err = pub2.GetClickStats(ctx, req); return err })
g.Go(func() error { conversions, err = pub2.GetConversionStats(ctx, req); return err })
g.Go(func() error { saleAmount, err = pub2.GetSaleAmountStats(ctx, req); return err })
g.Go(func() error { commission, err = pub2.GetCommissionStats(ctx, req); return err })

if err := g.Wait(); err != nil { /* handle partial failure */ }
```

---

### NFR-002: Security — HMAC & Data Protection

**Requirement:** Credentials in env, unique signature per request, sso_user_id from backend

**Architecture Solution:**
- Pub2Config loaded from environment variables at startup
- `client-trace-no` = UUID v4 per request (unique)
- `sso_user_id` extracted from `user.accesstrade.id` in service layer, never from frontend input
- Pub2 credentials never exposed to frontend

**HMAC Implementation:**
```go
func GenerateSignature(clientID, traceNo, requestTime, secret string) string {
    message := clientID + "|" + traceNo + "|" + requestTime
    mac := hmac.New(sha256.New, []byte(secret))
    mac.Write([]byte(message))
    return hex.EncodeToString(mac.Sum(nil))
}
```

---

### NFR-003: Tenant Isolation

**Requirement:** sub2 identifies Ambassador, reports filtered by sso_user_id

**Architecture Solution:**
- `sub2` parameter hardcoded = `"ambassador"` trong config
- Tất cả report API calls đều inject `sso_user_id` từ user data — không cho frontend chỉ định
- Affiliate links trong DB có `userId` → query scoped by user

---

### NFR-004: Reliability — Error Handling

**Requirement:** Retry, circuit breaker, graceful degradation

**Architecture Solution:**
- **Retry**: Max 3 retries, exponential backoff (1s, 2s, 4s), chỉ retry network errors (timeout, connection refused)
- **Circuit breaker**: Nếu Pub2 fail > 5 lần liên tiếp → open circuit 30s → return "service unavailable"
- **Error mapping**: Parse Pub2 `code` + `message` → map thành user-friendly error
- **Partial failure** (dashboard): Nếu 1 trong 4 API calls fail → return partial data + error flag

**Implementation:**
```go
type Pub2Client struct {
    httpClient   *http.Client
    config       Pub2Config
    circuitState struct {
        failCount  int
        openUntil  time.Time
    }
}
```

---

### NFR-005: Usability — Mobile Responsive

**Architecture Solution:**
- Frontend components sử dụng Bootstrap grid (đã có) → responsive by default
- Chart library sử dụng responsive mode
- Copy button sử dụng Clipboard API (works on mobile)

---

### NFR-006: Maintainability — Module Structure

**Architecture Solution:**
- Pub2 client tách riêng tại `internal/module/pub2/` với interface
- Service layer tại `internal/service/affiliate.go`
- Handlers tách public/admin
- Models tại `internal/model/mg/affiliate.go`

---

### NFR-007: Compatibility — Zero Regression

**Architecture Solution:**
- **3 collections mới** — không sửa bất kỳ collection hiện tại nào
- **Routes mới** với prefix riêng — không conflict:
  - Public: `/events/:id/affiliate-campaigns`, `/affiliate-campaigns/*`, `/affiliate-links`, `/affiliate-reports/*`
  - Admin: `/admin/affiliate-campaigns/*`, `/admin/campaign-affiliate-mappings/*`
- **Frontend**: Thêm component mới vào campaign detail page, không sửa component hiện tại
- **Admin**: Thêm page mới + tab mới trong event detail

---

## Security Architecture

### Authentication

- **User → Ambassador**: JWT Bearer token (hiện tại, không thay đổi)
- **Ambassador → Pub2**: HMAC-SHA256 signature per request

### Authorization

| Role | Allowed Actions |
|------|----------------|
| Influencer (authenticated) | Xem affiliate campaigns, tạo link, xem reports |
| Influencer (authenticated + AT linked) | Tất cả trên + thực hiện generate link, reports |
| Admin | CRUD affiliate campaigns, mapping, xem tất cả |

**Middleware check:**
```go
func RequireAccessTradeLinked(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        user := getUserFromContext(c)
        if user.Accesstrade.ID == 0 {
            return c.JSON(403, map[string]string{
                "error": "accesstrade_not_linked",
                "message": "Vui lòng liên kết tài khoản AccessTrade trước",
            })
        }
        return next(c)
    }
}
```

### Data Protection

- Pub2 `client_id` + `client_secret`: Environment variables only
- `sso_user_id`: Extracted from DB, never from client input
- Affiliate links: Scoped by `userId`, users chỉ thấy links của mình

---

## Scalability & Performance

### Performance Optimization

1. **MongoDB indexes** trên tất cả query fields (đã định nghĩa ở Data Model)
2. **Pub2 parallel calls** cho dashboard (Go errgroup)
3. **Idempotent link generation**: Check existing link trước khi gọi Pub2 → avoid duplicate calls
4. **Connection reuse**: `http.Client` với connection pooling cho Pub2 calls

### Caching Strategy (Phase sau)

MVP không cache — tất cả on-demand. Phase sau có thể thêm:
- Redis cache cho Pub2 report responses (TTL 5-15 phút)
- Cache affiliate campaigns list (TTL 1 giờ, invalidate on CRUD)

---

## Development Architecture

### Code Organization

```
backend/
├── internal/
│   ├── module/
│   │   └── pub2/                     # [NEW] Pub2 API client
│   │       ├── client.go             # HTTP client, retry, circuit breaker
│   │       ├── hmac.go               # HMAC-SHA256 signature
│   │       ├── models.go             # Request/Response types
│   │       └── errors.go             # Error handling
│   ├── model/mg/
│   │   └── affiliate.go              # [NEW] MongoDB models
│   └── service/
│       └── affiliate.go              # [NEW] Business logic
├── pkg/
│   ├── public/
│   │   ├── handler/
│   │   │   └── affiliate.go          # [NEW] Influencer endpoints
│   │   ├── router/
│   │   │   └── affiliate.go          # [NEW] Influencer routes
│   │   └── service/
│   │       └── affiliate.go          # [NEW] Public service layer
│   └── admin/
│       ├── handler/
│       │   └── affiliate.go          # [NEW] Admin endpoints
│       └── router/
│           └── affiliate.go          # [NEW] Admin routes

frontend/
├── src/
│   ├── pages/
│   │   ├── campaign-detail/components/  # [EXISTING]
│   │   │   └── affiliate-section/       # [NEW] Affiliate section
│   │   └── affiliate-reports/           # [NEW] Reports page
│   ├── services/
│   │   └── affiliate.ts                 # [NEW] API client
│   └── interfaces/
│       └── affiliate.ts                 # [NEW] TypeScript types

admin/
├── src/
│   ├── pages/
│   │   ├── affiliate-campaign/          # [NEW] CRUD pages
│   │   └── event/detail/components/tabs/
│   │       └── affiliate-campaigns.tsx  # [NEW] Tab in event detail
│   └── services/
│       └── affiliate.ts                 # [NEW] API client
```

### Testing Strategy

| Layer | Tool | Coverage |
|-------|------|----------|
| Pub2 Client | Go unit tests + httptest mock server | HMAC signature, retry, error handling |
| Service | Go unit tests + MongoDB mock | Business logic, validation |
| Handler | Go integration tests | API contracts, auth checks |
| Frontend | Jest + React Testing Library | Component rendering, user interactions |

**Priority tests:**
1. HMAC signature generation (correctness)
2. Generate link flow (happy path + AT not linked)
3. Report API passthrough (correct sso_user_id injection)
4. Campaign-event mapping CRUD

---

## Requirements Traceability

### Functional Requirements Coverage

| FR ID | FR Name | Backend | Frontend | Admin |
|-------|---------|---------|----------|-------|
| FR-001 | Admin tạo Affiliate Campaign | service/affiliate.go, handler (admin) | — | affiliate-campaign/detail |
| FR-002 | Admin quản lý danh sách | service/affiliate.go, handler (admin) | — | affiliate-campaign/index |
| FR-003 | Admin liên kết campaign ↔ event | service/affiliate.go, handler (admin) | — | linked-events.tsx, affiliate-campaigns tab |
| FR-004 | Influencer xem affiliate trong campaign detail | handler (public), GET /events/:id/affiliate-campaigns | affiliate-section/ | — |
| FR-005 | Influencer tạo link | handler (public), pub2/client.go | generate-link-modal.tsx | — |
| FR-006 | Influencer xem links | handler (public), service/affiliate.go | affiliate-links page hoặc section | — |
| FR-007 | Báo cáo Click | handler (public), pub2/client.go | click-chart.tsx | — |
| FR-008 | Báo cáo Conversion | handler (public), pub2/client.go | summary-cards.tsx | — |
| FR-009 | Báo cáo Sale Amount | handler (public), pub2/client.go | summary-cards.tsx | — |
| FR-010 | Báo cáo Commission | handler (public), pub2/client.go | summary-cards.tsx | — |
| FR-011 | Danh sách đơn | handler (public), pub2/client.go | orders-table.tsx | — |
| FR-012 | Dashboard tổng hợp | handler (public), parallel calls | affiliate-reports/index.tsx | — |
| FR-013 | Điểm chạm liên kết AT | RequireAccessTradeLinked middleware | link-accesstrade-banner/popup | — |
| FR-014 | Pub2 API Client | internal/module/pub2/ | — | — |
| FR-015 | Backend CRUD + Mapping APIs | handlers + service | — | — |
| FR-016 | Backend Link & Report APIs | handlers + service + pub2 client | — | — |

### Non-Functional Requirements Coverage

| NFR ID | NFR Name | Solution | Validation |
|--------|----------|----------|------------|
| NFR-001 | Performance | MongoDB indexes, parallel Pub2 calls | p95 response time monitoring |
| NFR-002 | Security | HMAC, env vars, sso_user_id injection | Security review, penetration test |
| NFR-003 | Tenant isolation | sub2="ambassador", user-scoped queries | Manual verification |
| NFR-004 | Reliability | Retry 3x, circuit breaker 30s | Pub2 downtime simulation test |
| NFR-005 | Mobile responsive | Bootstrap grid, Clipboard API | Manual mobile testing |
| NFR-006 | Maintainability | Separate pub2 module with interface | Code review |
| NFR-007 | Compatibility | New collections/routes only, no changes to existing | Regression test suite |

---

## Trade-offs & Decision Log

### Decision 1: On-demand reports vs. Scheduled sync

**Choice:** On-demand (gọi Pub2 API real-time khi user request)

**Trade-off:**
- ✓ Gain: Đơn giản, data luôn fresh, không cần cron job
- ✗ Lose: Phụ thuộc Pub2 uptime, latency cao hơn cached data

**Rationale:** MVP simplicity. Thêm caching/sync ở phase sau nếu performance là issue.

### Decision 2: Affiliate campaign gắn vào campaign detail vs. standalone page

**Choice:** Gắn vào campaign detail (FR-004)

**Trade-off:**
- ✓ Gain: Natural UX — influencer khám phá affiliate trong context campaign đang xem
- ✗ Lose: Phức tạp hơn standalone page, cần mapping table

**Rationale:** User feedback — affiliate campaign có ý nghĩa trong context campaign, không phải standalone.

### Decision 3: Many-to-many mapping vs. 1:1

**Choice:** Many-to-many (campaign_affiliate_mappings)

**Trade-off:**
- ✓ Gain: Flexible — 1 affiliate campaign có thể dùng cho nhiều events, ngược lại
- ✗ Lose: Thêm 1 collection, query phức tạp hơn

**Rationale:** Business cần: 1 Pub2 campaign (e.g., "Shopee") có thể liên kết với nhiều events khác nhau.

### Decision 4: Idempotent link generation

**Choice:** Check existing link trước khi gọi Pub2

**Trade-off:**
- ✓ Gain: Tiết kiệm Pub2 API calls, user luôn thấy consistent link
- ✗ Lose: Extra DB query mỗi lần generate

**Rationale:** Pub2 API call tốn ~1-3s, DB query ~5ms. Check trước là win rõ ràng.

---

## Open Issues & Risks

| # | Issue | Impact | Mitigation |
|---|-------|--------|------------|
| 1 | Pub2 API rate limit chưa rõ | Có thể bị throttle khi nhiều user request cùng lúc | Hỏi Pub2 team, implement rate limiter nội bộ nếu cần |
| 2 | `sso_user_id` mapping chưa confirm 100% | Link generation có thể fail nếu ID không match | Test kỹ với dev environment, hỏi AT team confirm |
| 3 | Pub2 dev endpoint có thể không stable | Development bị block | Implement mock mode cho Pub2 client (testing) |
| 4 | Campaign trên Pub2 có thể expire | Link generation fail cho expired campaign | Phase sau: thêm sync job kiểm tra campaign status |

---

## Assumptions & Constraints

1. Ambassador backend structure (Go + Echo + MongoDB) giữ nguyên
2. Auth middleware hiện tại (JWT) hoạt động đúng cho routes mới
3. Admin middleware hiện tại phân quyền đúng
4. Pub2 dev environment available cho testing
5. `user.accesstrade.id` đã populated đúng sau SSO linking flow
6. MongoDB instance hiện tại đủ capacity cho 3 collections mới

---

## Future Considerations

1. **Caching layer**: Redis cache cho Pub2 responses khi user base tăng
2. **Scheduled sync**: Cron job sync conversion data để giảm Pub2 dependency
3. **Webhook integration**: Khi Pub2 cung cấp API 7 → real-time conversion updates
4. **Standalone affiliate page**: Nếu số lượng affiliate campaigns tăng → cần listing page riêng
5. **Multi-tenant reuse**: Pub2 client module có thể reuse cho TCB, Vinfast
6. **Analytics**: Track conversion funnel (view campaign → generate link → click → conversion)

---

## Approval & Sign-off

**Review Status:**
- [ ] Technical Lead
- [ ] Product Owner
- [ ] Pub2 Team (API confirmation)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-25 | vinhnguyen | Initial architecture |

---

## Next Steps

### Phase 4: Sprint Planning & Implementation

Run `/sprint-planning` to:
- Break epics into detailed user stories
- Estimate story complexity
- Plan sprint iterations
- Begin implementation following this architectural blueprint

**Implementation Order gợi ý:**
1. **Sprint 1**: Pub2 Client module + Admin CRUD affiliate campaigns
2. **Sprint 2**: Campaign-Event mapping + Frontend affiliate section trong campaign detail
3. **Sprint 3**: Link generation + Reports APIs
4. **Sprint 4**: Frontend reports page + testing + polish

---

**This document was created using BMAD Method v6 - Phase 3 (Solutioning)**
