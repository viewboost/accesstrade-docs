# Product Requirements Document: AT Core - Influence Library

**Document Version:** 1.0
**Date:** 2026-01-31
**Product Owner:** AccessTrade
**Status:** Draft

---

## 1. Executive Summary

### 1.1 Product Vision
Xây dựng **AT Influencer Service** - một nền tảng Partner API cho phép các đối tác (Techcombank, Vinfast, Ambassador...) truy cập và sử dụng Influencer Library của AccessTrade với mô hình subscription-based và quota management.

### 1.2 Problem Statement
Hiện tại AccessTrade đã có cơ sở dữ liệu influencers từ Vendor Influence-Meter, nhưng thiếu:
- Cơ chế cho phép partners truy cập influencer pool
- Quota và subscription management
- Partner authentication và authorization
- Admin tools để quản lý partners

### 1.3 Target Users
| User Type | Description |
|-----------|-------------|
| **Partners** | Techcombank, Vinfast, Ambassador - cần truy cập influencer data qua API |
| **AT Admin** | Internal staff quản lý partners, quota, subscriptions |
| **Partner Systems** | Backend services của partners gọi AT API |

### 1.4 Success Metrics
| Metric | Target |
|--------|--------|
| API Response Time | < 200ms (p95) |
| API Uptime | 99.9% |
| Partner Onboarding Time | < 1 day |
| Quota Accuracy | 100% |

---

## 2. Scope

### 2.1 In Scope (AT Core Modules)
| Module | Description |
|--------|-------------|
| **M1. AT Partner API** | REST API endpoints cho partners |
| **M2. AT Database Extensions** | Schema mở rộng cho Partner, Subscription, Quota |
| **M3. AT Admin Enhancements** | UI quản lý partners và subscriptions |

### 2.2 Out of Scope
- TCB Database, API, Admin (separate PRD)
- TCB Sync Service (separate PRD)
- Vendor Influence-Meter modifications
- Mobile applications

### 2.3 Dependencies
| Dependency | Type | Status |
|------------|------|--------|
| `influencer-meter-adapter` | SDK | ✅ Ready |
| `influencer-meter-service` | REST API | ✅ Ready |
| Vendor Influence-Meter API | External | ✅ Production |
| PostgreSQL Database | Infrastructure | ✅ Ready |

---

## 3. Functional Requirements

### 3.1 FR-001: Partner Authentication

**Description:** Hệ thống phải xác thực partners qua API Key.

**Acceptance Criteria:**
- [ ] Partners được cấp unique `Partner ID` và `API Key`
- [ ] Mọi request phải có headers: `X-Partner-ID` và `X-API-Key`
- [ ] Invalid credentials trả về `401 Unauthorized`
- [ ] Rate limiting per partner: 100 requests/minute
- [ ] API keys có thể revoke/regenerate

**Data Model:**
```typescript
interface PartnerCredentials {
  partnerId: string      // 'techcombank'
  apiKey: string         // hashed, rotatable
  isActive: boolean
  rateLimit: number      // requests/minute
  lastUsedAt?: Date
}
```

---

### 3.2 FR-002: Influencer Pool Search

**Description:** Partners có thể tìm kiếm influencers trong AT Shared Pool.

**Endpoint:** `GET /api/v1/partners/pool/search`

**Acceptance Criteria:**
- [ ] Chỉ trả về influencers có `visibility: PUBLIC`
- [ ] Hỗ trợ filters: category, platform, followers range, engagement range
- [ ] Pagination với limit/offset
- [ ] Preview mode: không show contact info và detailed metrics
- [ ] Response time < 200ms với dataset 100K influencers

**Request:**
```yaml
GET /api/v1/partners/pool/search
Headers:
  X-Partner-ID: techcombank
  X-API-Key: tcb_api_key_xxx
Query:
  category: beauty | tech | lifestyle | food | travel | gaming
  platform: tiktok | youtube | instagram | facebook
  minFollowers: 10000
  maxFollowers: 1000000
  minEngagement: 3.0
  minScore: 60
  limit: 20 (default)
  offset: 0
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "at_inf_123",
      "platform": "tiktok",
      "username": "beauty_creator",
      "displayName": "Beauty Creator VN",
      "avatarUrl": "https://...",
      "followers": 250000,
      "category": "beauty",
      "tier": "premium",
      "score": 78,
      "previewOnly": true
    }
  ],
  "pagination": {
    "total": 1500,
    "limit": 20,
    "offset": 0,
    "hasMore": true
  }
}
```

---

### 3.3 FR-003: Request Influencers from Pool

**Description:** Partners có thể request access đến influencers từ AT Pool.

**Endpoint:** `POST /api/v1/partners/pool/request`

**Acceptance Criteria:**
- [ ] Auto-approve nếu partner còn quota
- [ ] Trừ quota ngay khi approved
- [ ] Trả về full influencer data sau khi approved
- [ ] Deny nếu hết quota với message rõ ràng
- [ ] Ghi log mọi requests (audit trail)
- [ ] Support batch request (tối đa 20 influencers/request)

**Request:**
```json
{
  "influencerIds": ["at_inf_123", "at_inf_456"],
  "reason": "Campaign Tết 2026"
}
```

**Response (Success):**
```json
{
  "success": true,
  "approved": [
    {
      "id": "at_inf_123",
      "platform": "tiktok",
      "username": "beauty_creator",
      "displayName": "Beauty Creator VN",
      "avatarUrl": "https://...",
      "followers": 250000,
      "engagement": 4.8,
      "score": 78,
      "contactInfo": {
        "email": "creator@email.com",
        "phone": "+84..."
      },
      "detailedMetrics": {
        "avgViews": 50000,
        "avgLikes": 5000,
        "avgComments": 200
      }
    }
  ],
  "denied": [],
  "quota": {
    "used": 7,
    "limit": 50,
    "remaining": 43,
    "resetsAt": "2026-02-01T00:00:00Z"
  }
}
```

**Response (Over Quota):**
```json
{
  "success": false,
  "error": {
    "code": "QUOTA_EXCEEDED",
    "message": "Monthly quota exceeded. Used: 50/50. Resets at 2026-02-01."
  },
  "approved": [],
  "denied": ["at_inf_123", "at_inf_456"],
  "quota": {
    "used": 50,
    "limit": 50,
    "remaining": 0,
    "resetsAt": "2026-02-01T00:00:00Z"
  }
}
```

---

### 3.4 FR-004: Quota Management

**Description:** Quản lý quota cho mỗi partner theo subscription tier.

**Endpoint:** `GET /api/v1/partners/quota`

**Acceptance Criteria:**
- [ ] Mỗi partner có monthly quota theo tier
- [ ] Quota reset vào ngày 1 hàng tháng (00:00 UTC+7)
- [ ] Real-time quota tracking
- [ ] Webhook notification khi quota đạt 80%, 100%

**Subscription Tiers:**
| Tier | Monthly Quota | Price |
|------|---------------|-------|
| FREE | 10 influencers | $0 |
| BASIC | 50 influencers | $199/month |
| PREMIUM | 200 influencers | $499/month |
| ENTERPRISE | Unlimited | Custom |

**Response:**
```json
{
  "partnerId": "techcombank",
  "tier": "premium",
  "quota": {
    "used": 45,
    "limit": 200,
    "remaining": 155,
    "resetsAt": "2026-02-01T00:00:00Z"
  },
  "usageHistory": [
    { "date": "2026-01-30", "count": 5 },
    { "date": "2026-01-29", "count": 10 }
  ]
}
```

---

### 3.5 FR-005: Subscription Status

**Description:** Partners có thể kiểm tra trạng thái subscription.

**Endpoint:** `GET /api/v1/partners/subscription`

**Acceptance Criteria:**
- [ ] Trả về tier, status, features, expiry date
- [ ] Alert khi subscription sắp hết hạn (7 days)
- [ ] Grace period: 7 days sau khi expired

**Response:**
```json
{
  "partnerId": "techcombank",
  "subscription": {
    "tier": "premium",
    "status": "active",
    "startDate": "2026-01-01T00:00:00Z",
    "endDate": "2026-12-31T23:59:59Z",
    "autoRenew": true,
    "daysRemaining": 335
  },
  "features": {
    "poolSearch": true,
    "poolRequest": true,
    "profileEnrich": true,
    "batchRefresh": true,
    "webhooks": true,
    "prioritySupport": true
  },
  "alerts": []
}
```

---

### 3.6 FR-006: Profile Enrichment

**Description:** Partners có thể request crawl profile mới từ social platforms.

**Endpoint:** `POST /api/v1/profiles/enrich`

**Acceptance Criteria:**
- [ ] Support URLs: TikTok, YouTube, Instagram, Facebook
- [ ] Async processing với callback URL
- [ ] Trả về job ID để poll status
- [ ] Timeout: 30 seconds cho crawl
- [ ] Cache result: 24 hours

**Request:**
```json
{
  "url": "https://tiktok.com/@beauty_creator",
  "callbackUrl": "https://api.tcb.vn/webhooks/crawl-complete"
}
```

**Response (Immediate):**
```json
{
  "success": true,
  "jobId": "job_abc123",
  "status": "processing",
  "estimatedTime": 10
}
```

**Callback Payload:**
```json
{
  "jobId": "job_abc123",
  "status": "completed",
  "profile": {
    "id": "vb_prof_123",
    "platform": "tiktok",
    "username": "beauty_creator",
    "displayName": "Beauty Creator VN",
    "followers": 250000,
    "engagement": 4.8,
    "score": 78,
    "metrics": { ... },
    "crawledAt": "2026-01-31T10:00:00Z"
  }
}
```

---

### 3.7 FR-007: Batch Refresh Profiles

**Description:** Refresh metrics cho nhiều profiles cùng lúc.

**Endpoint:** `POST /api/v1/profiles/batch-refresh`

**Acceptance Criteria:**
- [ ] Tối đa 100 profiles per request
- [ ] Async processing
- [ ] Prioritize by partner tier
- [ ] Return partial results if some fail

**Request:**
```json
{
  "profileIds": ["vb_prof_123", "vb_prof_456", "vb_prof_789"]
}
```

**Response:**
```json
{
  "success": true,
  "refreshed": [
    {
      "id": "vb_prof_123",
      "status": "updated",
      "previousScore": 75,
      "newScore": 78,
      "updatedAt": "2026-01-31T10:00:00Z"
    }
  ],
  "failed": [
    {
      "id": "vb_prof_789",
      "error": "Profile not found or private"
    }
  ],
  "summary": {
    "total": 3,
    "success": 2,
    "failed": 1
  }
}
```

---

### 3.8 FR-008: Partner Management (Admin)

**Description:** AT Admin có thể quản lý partners.

**Acceptance Criteria:**
- [ ] List all partners với filters
- [ ] Create new partner với credentials
- [ ] Update partner info và subscription
- [ ] Deactivate/reactivate partner
- [ ] Regenerate API key
- [ ] View partner usage analytics

**Admin UI Pages:**
```
/admin/partners
├── List view (table)
│   ├── Partner name, code
│   ├── Subscription tier, status
│   ├── Quota used/limit
│   └── Actions: Edit, Deactivate
│
├── Create Partner form
│   ├── Name, Code (unique)
│   ├── Contact info
│   ├── Subscription tier
│   └── Generate API key
│
└── Partner Detail
    ├── Profile info
    ├── Subscription management
    ├── Quota usage chart
    ├── API key management
    └── Request history
```

---

### 3.9 FR-009: Influencer Visibility Control (Admin)

**Description:** AT Admin có thể control visibility của influencers.

**Acceptance Criteria:**
- [ ] Set visibility: PUBLIC (partners can see) or PRIVATE (AT only)
- [ ] Bulk update visibility
- [ ] Filter influencers by visibility
- [ ] Audit log khi change visibility

---

### 3.10 FR-010: Subscription Management (Admin)

**Description:** AT Admin có thể quản lý subscriptions.

**Acceptance Criteria:**
- [ ] View all subscriptions
- [ ] Change tier for partner
- [ ] Extend/shorten subscription period
- [ ] Manual quota adjustment
- [ ] Send notification to partner

---

## 4. Non-Functional Requirements

### 4.1 NFR-001: Performance

| Metric | Requirement |
|--------|-------------|
| API Response Time (p50) | < 100ms |
| API Response Time (p95) | < 200ms |
| API Response Time (p99) | < 500ms |
| Database Query Time | < 50ms |
| Throughput | 1000 requests/second |

### 4.2 NFR-002: Availability

| Metric | Requirement |
|--------|-------------|
| Uptime SLA | 99.9% |
| Planned Downtime | Max 4 hours/month (off-peak) |
| Recovery Time Objective (RTO) | < 1 hour |
| Recovery Point Objective (RPO) | < 5 minutes |

### 4.3 NFR-003: Security

| Requirement | Implementation |
|-------------|----------------|
| API Authentication | API Key (hashed, rotatable) |
| Transport Security | TLS 1.3 mandatory |
| Rate Limiting | 100 req/min per partner |
| Input Validation | Strict schema validation |
| Audit Logging | All mutations logged |
| Data Encryption | AES-256 for sensitive data |

### 4.4 NFR-004: Scalability

| Metric | Requirement |
|--------|-------------|
| Partners | Support 100+ partners |
| Influencers | Support 500K+ profiles |
| Concurrent Users | 1000+ simultaneous |
| Data Growth | 20% YoY |

### 4.5 NFR-005: Maintainability

| Requirement | Implementation |
|-------------|----------------|
| Code Coverage | > 80% |
| Documentation | OpenAPI 3.0 spec |
| Monitoring | Prometheus + Grafana |
| Logging | Structured JSON logs |
| Error Tracking | Sentry integration |

---

## 5. Epics and User Stories

### Epic 1: Partner Authentication & Authorization

**E1-US01: Partner Registration**
```
AS an AT Admin
I WANT to register a new partner in the system
SO THAT they can access the Influencer API

Acceptance Criteria:
- Can create partner with name, code, contact info
- System generates unique API key
- Partner receives onboarding email
- Partner status is ACTIVE by default
```

**E1-US02: API Key Authentication**
```
AS a Partner System
I WANT to authenticate API requests using API key
SO THAT I can access protected endpoints

Acceptance Criteria:
- Request with valid X-Partner-ID + X-API-Key returns 200
- Request without headers returns 401
- Request with invalid key returns 401
- Request with revoked key returns 401
```

**E1-US03: Rate Limiting**
```
AS an AT System
I WANT to limit API requests per partner
SO THAT system remains stable

Acceptance Criteria:
- Each partner has rate limit (default 100/min)
- Exceeding limit returns 429 Too Many Requests
- Rate limit resets every minute
- Custom limit configurable per partner
```

---

### Epic 2: Influencer Pool Access

**E2-US01: Search Influencer Pool**
```
AS a Partner
I WANT to search influencers in AT pool
SO THAT I can find suitable creators for campaigns

Acceptance Criteria:
- Can filter by category, platform, followers, engagement
- Results show preview (no contact info)
- Pagination works correctly
- Only PUBLIC influencers shown
```

**E2-US02: Request Influencers**
```
AS a Partner
I WANT to request access to influencers
SO THAT I can get full data including contact info

Acceptance Criteria:
- Can request up to 20 influencers per call
- Auto-approved if quota available
- Quota decremented on approval
- Full data returned after approval
- Denied with clear message if over quota
```

**E2-US03: Check Quota**
```
AS a Partner
I WANT to check my remaining quota
SO THAT I can plan my campaigns

Acceptance Criteria:
- Shows used/limit/remaining
- Shows reset date
- Shows usage history
- Real-time accurate
```

---

### Epic 3: Profile Enrichment

**E3-US01: Crawl New Profile**
```
AS a Partner
I WANT to crawl a new influencer profile
SO THAT I can add private influencers

Acceptance Criteria:
- Submit social URL
- Get job ID for tracking
- Receive callback when done
- Get full profile data
```

**E3-US02: Batch Refresh Profiles**
```
AS a Partner
I WANT to refresh multiple profiles at once
SO THAT I have up-to-date metrics

Acceptance Criteria:
- Submit up to 100 profile IDs
- Get updated metrics for each
- Partial success handled gracefully
- Summary of success/failed
```

---

### Epic 4: Subscription Management

**E4-US01: View Subscription Status**
```
AS a Partner
I WANT to view my subscription status
SO THAT I know my current plan and limits

Acceptance Criteria:
- Shows tier, status, dates
- Shows features available
- Shows alerts (expiring soon)
- Shows days remaining
```

**E4-US02: Manage Partner Subscription (Admin)**
```
AS an AT Admin
I WANT to manage partner subscriptions
SO THAT I can upgrade/downgrade partners

Acceptance Criteria:
- Can change tier
- Can extend/shorten period
- Can adjust quota manually
- Partner notified of changes
```

---

### Epic 5: Admin Dashboard

**E5-US01: Partner List View**
```
AS an AT Admin
I WANT to see all partners
SO THAT I can manage them

Acceptance Criteria:
- Table with name, tier, status, quota
- Filter by status, tier
- Search by name
- Sort by any column
```

**E5-US02: Partner Detail View**
```
AS an AT Admin
I WANT to see partner details
SO THAT I can understand their usage

Acceptance Criteria:
- Profile information
- Subscription details
- Quota usage chart
- Request history
- API key management
```

**E5-US03: Influencer Visibility Control**
```
AS an AT Admin
I WANT to control influencer visibility
SO THAT I can manage what partners can see

Acceptance Criteria:
- Toggle PUBLIC/PRIVATE
- Bulk update
- Filter by visibility
- Audit log
```

---

## 6. Data Models

### 6.1 Partner

```prisma
model Partner {
  id          String   @id @default(cuid())
  name        String   // "Techcombank"
  code        String   @unique // "techcombank"

  // Credentials
  apiKey      String   @unique // hashed
  apiKeyHash  String   // for verification
  isActive    Boolean  @default(true)

  // Contact
  contactName  String?
  contactEmail String?
  contactPhone String?

  // Settings
  rateLimit   Int      @default(100) // req/min

  // Relations
  subscription PartnerSubscription?
  requests    InfluencerRequest[]

  // Timestamps
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  lastApiCallAt DateTime?
}
```

### 6.2 Partner Subscription

```prisma
model PartnerSubscription {
  id          String   @id @default(cuid())
  partnerId   String   @unique
  partner     Partner  @relation(fields: [partnerId], references: [id])

  // Plan
  tier        SubscriptionTier @default(FREE)
  status      SubscriptionStatus @default(ACTIVE)

  // Quota
  monthlyQuota    Int    @default(10)
  usedThisMonth   Int    @default(0)
  quotaResetAt    DateTime

  // Period
  startDate   DateTime
  endDate     DateTime?
  autoRenew   Boolean  @default(false)

  // Timestamps
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
}

enum SubscriptionTier {
  FREE        // 10/month
  BASIC       // 50/month
  PREMIUM     // 200/month
  ENTERPRISE  // unlimited
}

enum SubscriptionStatus {
  ACTIVE
  EXPIRED
  SUSPENDED
  GRACE_PERIOD
}
```

### 6.3 Influencer Request

```prisma
model InfluencerRequest {
  id          String   @id @default(cuid())
  partnerId   String
  partner     Partner  @relation(fields: [partnerId], references: [id])

  // Request details
  influencerIds String[]
  reason      String?
  status      RequestStatus @default(APPROVED)

  // Results
  approvedCount Int @default(0)
  deniedCount   Int @default(0)

  // Timestamps
  createdAt   DateTime @default(now())
}

enum RequestStatus {
  PENDING
  APPROVED
  DENIED
  PARTIAL
}
```

### 6.4 Profile Extension (Existing Model)

```prisma
// Extend existing Profile model
model Profile {
  // ... existing fields ...

  // New: Visibility control
  visibility  ProfileVisibility @default(PUBLIC)

  // New: Track who added
  addedByPartnerId String?

  // New: Category
  category    String?
}

enum ProfileVisibility {
  PUBLIC    // Partners can see
  PRIVATE   // AT internal only
}
```

---

## 7. API Specification Summary

### 7.1 Partner Pool Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/partners/pool/search` | Search influencer pool |
| POST | `/api/v1/partners/pool/request` | Request influencers |
| GET | `/api/v1/partners/quota` | Get quota status |
| GET | `/api/v1/partners/subscription` | Get subscription status |

### 7.2 Profile Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/profiles/enrich` | Crawl new profile |
| POST | `/api/v1/profiles/batch-refresh` | Refresh multiple profiles |

### 7.3 Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/partners` | List partners |
| POST | `/api/v1/admin/partners` | Create partner |
| GET | `/api/v1/admin/partners/:id` | Get partner detail |
| PATCH | `/api/v1/admin/partners/:id` | Update partner |
| POST | `/api/v1/admin/partners/:id/regenerate-key` | Regenerate API key |
| PATCH | `/api/v1/admin/partners/:id/subscription` | Update subscription |
| GET | `/api/v1/admin/influencers` | List influencers |
| PATCH | `/api/v1/admin/influencers/:id/visibility` | Update visibility |
| POST | `/api/v1/admin/influencers/bulk-visibility` | Bulk update visibility |

---

## 8. Integration Points

### 8.1 Upstream Dependencies

```
AT Partner API
    │
    ├── influencer-meter-service (REST wrapper)
    │       │
    │       └── influencer-meter-adapter (TypeScript SDK)
    │               │
    │               └── Vendor Influence-Meter API
    │
    └── PostgreSQL Database
```

### 8.2 Downstream Consumers

```
Partners (TCB, Vinfast, Ambassador...)
    │
    └── AT Partner API
            │
            ├── Pool Search
            ├── Request Influencers
            ├── Profile Enrichment
            └── Batch Refresh
```

---

## 9. Acceptance Criteria Summary

### 9.1 Must Have (P0)
- [ ] Partner authentication with API key
- [ ] Pool search with filters
- [ ] Request influencers with auto-approval
- [ ] Quota management with monthly reset
- [ ] Profile enrichment endpoint
- [ ] Basic admin: create/view partners

### 9.2 Should Have (P1)
- [ ] Subscription status endpoint
- [ ] Batch refresh endpoint
- [ ] Admin: update partner subscription
- [ ] Admin: influencer visibility control
- [ ] Rate limiting
- [ ] Webhook notifications

### 9.3 Could Have (P2)
- [ ] Admin: usage analytics dashboard
- [ ] Admin: request history view
- [ ] Quota warning notifications
- [ ] API key expiration

---

## 10. Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| API contract changes break partners | High | Medium | Version API, deprecation policy |
| Quota calculation bugs | High | Low | Comprehensive testing, monitoring |
| Vendor API downtime | High | Low | Circuit breaker in adapter |
| Database migration issues | Medium | Medium | Test migrations, backup strategy |
| Security vulnerabilities | High | Low | Security review, penetration testing |

---

## 11. Timeline & Milestones

### Phase 1: Foundation (Week 1-2)
- [ ] M2: Database schema design & migration
- [ ] M1: Partner authentication middleware
- [ ] M1: Profile enrichment endpoint (partial)

### Phase 2: Core API (Week 3-4)
- [ ] M1: Pool search endpoint
- [ ] M1: Request influencers endpoint
- [ ] M1: Quota management

### Phase 3: Admin & Polish (Week 5-6)
- [ ] M3: Partner management UI
- [ ] M3: Influencer visibility UI
- [ ] M1: Batch refresh, subscription endpoints
- [ ] Integration testing

---

## 12. Appendix

### A. Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Invalid or missing API key |
| `FORBIDDEN` | 403 | Partner inactive or suspended |
| `QUOTA_EXCEEDED` | 403 | Monthly quota exceeded |
| `RATE_LIMITED` | 429 | Too many requests |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 400 | Invalid request payload |
| `INTERNAL_ERROR` | 500 | Server error |

### B. Subscription Tier Features

| Feature | FREE | BASIC | PREMIUM | ENTERPRISE |
|---------|------|-------|---------|------------|
| Monthly Quota | 10 | 50 | 200 | Unlimited |
| Pool Search | ✅ | ✅ | ✅ | ✅ |
| Pool Request | ✅ | ✅ | ✅ | ✅ |
| Profile Enrich | ✅ | ✅ | ✅ | ✅ |
| Batch Refresh | ❌ | ✅ | ✅ | ✅ |
| Webhooks | ❌ | ✅ | ✅ | ✅ |
| Priority Support | ❌ | ❌ | ✅ | ✅ |
| Custom Integration | ❌ | ❌ | ❌ | ✅ |

### C. OpenAPI Spec Location

Full OpenAPI 3.0 specification will be generated at:
`/api-docs/partner-api.yaml`

---

**Document Status:** Draft
**Next Review Date:** TBD
**Approved By:** Pending

---

*Generated by BMAD Method v6 - Product Manager Workflow*
