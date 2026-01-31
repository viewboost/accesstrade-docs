# Technical Specification: AT Core - Influence Library

**Date:** 2026-01-31
**Author:** AccessTrade Engineering
**Version:** 1.0
**Project Type:** Backend API + Admin UI
**Project Level:** Level 1 (10 stories)
**Status:** Draft

---

## Document Overview

This Technical Specification provides focused technical planning for AT Core Influence Library. It covers the Partner API, Database Extensions, and Admin Enhancements modules.

**Related Documents:**
- PRD: `docs/prd-at-core-influence-library-2026-01-31.md`
- Architecture: `docs/brainstorming-influence-library-2026-01-31.md`

---

## Problem & Solution

### Problem Statement

AccessTrade đã có cơ sở dữ liệu influencers từ Vendor Influence-Meter, nhưng thiếu:
- Cơ chế cho phép partners (Techcombank, Vinfast, Ambassador) truy cập influencer pool
- Quota và subscription management theo tier
- Partner authentication và authorization
- Admin tools để quản lý partners và subscriptions

### Proposed Solution

Xây dựng **AT Influencer Service** gồm 3 modules:
1. **Partner API** - REST endpoints cho partners truy cập influencer pool
2. **Database Extensions** - Schema mở rộng cho Partner, Subscription, Quota
3. **Admin Enhancements** - UI quản lý partners và visibility

---

## Requirements

### What Needs to Be Built

**Partner Authentication & Authorization:**
- Partner registration với unique `code` và `API Key`
- API Key authentication qua headers `X-Partner-ID` và `X-API-Key`
- Rate limiting per partner (default: 100 req/min)
- API key rotation và revocation

**Influencer Pool Access:**
- Search influencers với filters (category, platform, followers, engagement)
- Preview mode (không show contact info)
- Request influencers với auto-approval nếu còn quota
- Batch request tối đa 20 influencers/request

**Quota & Subscription Management:**
- 4 tiers: FREE (10/mo), BASIC (50/mo), PREMIUM (200/mo), ENTERPRISE (unlimited)
- Monthly quota reset vào ngày 1 hàng tháng
- Real-time quota tracking
- Subscription status với grace period 7 days

**Profile Enrichment:**
- Crawl profile mới từ social URLs (TikTok, YouTube, Instagram, Facebook)
- Async processing với callback URL
- Batch refresh cho multiple profiles

**Admin Functions:**
- Partner CRUD với API key management
- Subscription tier management
- Influencer visibility control (PUBLIC/PRIVATE)
- Usage analytics

### What This Does NOT Include

- TCB Database, API, Admin (separate project)
- TCB Sync Service (separate project)
- Vendor Influence-Meter core modifications
- Mobile applications
- Payment integration

---

## Technical Approach

### Technology Stack

- **Language/Framework:** TypeScript + NestJS
- **Database:** PostgreSQL 15 + Prisma ORM
- **Cache:** Redis (for rate limiting, quota tracking)
- **API Documentation:** OpenAPI 3.0 (Swagger)
- **Admin UI:** Next.js 16 (extend existing IM Admin)
- **Testing:** Jest + Supertest
- **Deployment:** Docker + Kubernetes

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           AT INFLUENCER SERVICE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐        │
│  │   Partner API  │    │  Admin API     │    │   Admin UI     │        │
│  │   (NestJS)     │    │  (NestJS)      │    │   (Next.js)    │        │
│  └───────┬────────┘    └───────┬────────┘    └───────┬────────┘        │
│          │                     │                     │                  │
│          └─────────────────────┼─────────────────────┘                  │
│                                │                                         │
│                    ┌───────────┴───────────┐                            │
│                    │      Core Services    │                            │
│                    │  ┌─────────────────┐  │                            │
│                    │  │ PartnerService  │  │                            │
│                    │  │ QuotaService    │  │                            │
│                    │  │ PoolService     │  │                            │
│                    │  │ SubscriptionSvc │  │                            │
│                    │  └─────────────────┘  │                            │
│                    └───────────┬───────────┘                            │
│                                │                                         │
│          ┌─────────────────────┼─────────────────────┐                  │
│          │                     │                     │                  │
│   ┌──────┴──────┐    ┌────────┴────────┐    ┌──────┴──────┐           │
│   │  PostgreSQL │    │     Redis       │    │   Vendor    │           │
│   │  (Prisma)   │    │  (Rate Limit)   │    │   Adapter   │           │
│   └─────────────┘    └─────────────────┘    └─────────────┘           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Request Flow:**

```
Partner Request → API Gateway → Rate Limiter → Auth Guard → Controller → Service → DB/Cache
                                    │
                                    └─→ 429 if exceeded
```

### Data Model

#### Partner

```prisma
model Partner {
  id            String   @id @default(cuid())
  name          String   // "Techcombank"
  code          String   @unique // "techcombank"

  // API Key (hashed)
  apiKeyHash    String   @unique
  apiKeyPrefix  String   // First 8 chars for display: "im_prod_t..."

  // Status
  isActive      Boolean  @default(true)

  // Contact
  contactName   String?
  contactEmail  String?
  contactPhone  String?

  // Settings
  rateLimit     Int      @default(100) // req/min

  // Relations
  subscription  PartnerSubscription?
  requests      InfluencerRequest[]

  // Timestamps
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt
  lastApiCallAt DateTime?

  @@index([code])
  @@index([apiKeyHash])
}
```

#### PartnerSubscription

```prisma
model PartnerSubscription {
  id              String   @id @default(cuid())
  partnerId       String   @unique
  partner         Partner  @relation(fields: [partnerId], references: [id])

  // Plan
  tier            SubscriptionTier @default(FREE)
  status          SubscriptionStatus @default(ACTIVE)

  // Quota (monthly influencer requests)
  monthlyQuota    Int      @default(10)
  usedThisMonth   Int      @default(0)
  quotaResetAt    DateTime

  // Period
  startDate       DateTime
  endDate         DateTime?
  autoRenew       Boolean  @default(false)

  // Timestamps
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  @@index([partnerId])
  @@index([status])
}

enum SubscriptionTier {
  FREE        // 10 influencers/month
  BASIC       // 50 influencers/month
  PREMIUM     // 200 influencers/month
  ENTERPRISE  // Unlimited
}

enum SubscriptionStatus {
  ACTIVE
  EXPIRED
  SUSPENDED
  GRACE_PERIOD
}
```

#### InfluencerRequest

```prisma
model InfluencerRequest {
  id              String   @id @default(cuid())
  partnerId       String
  partner         Partner  @relation(fields: [partnerId], references: [id])

  // Request details
  influencerIds   String[]
  reason          String?
  status          RequestStatus @default(APPROVED)

  // Results
  approvedCount   Int      @default(0)
  deniedCount     Int      @default(0)

  // Timestamps
  createdAt       DateTime @default(now())

  @@index([partnerId])
  @@index([createdAt])
}

enum RequestStatus {
  PENDING
  APPROVED
  DENIED
  PARTIAL
}
```

#### Profile Extension

```prisma
// Extend existing Profile model
model Profile {
  // ... existing fields ...

  // New: Visibility control
  visibility      ProfileVisibility @default(PUBLIC)

  // New: Category for filtering
  category        String?

  @@index([visibility])
  @@index([category])
}

enum ProfileVisibility {
  PUBLIC    // Partners can see and request
  PRIVATE   // AT internal only
}
```

### API Design

#### Partner API Endpoints

```yaml
# Authentication: X-Partner-ID + X-API-Key headers required

# Pool Search
GET /api/v1/partners/pool/search
  Query: category, platform, minFollowers, maxFollowers, minEngagement, minScore, limit, offset
  Response: { data: InfluencerPreview[], pagination }

# Request Influencers
POST /api/v1/partners/pool/request
  Body: { influencerIds: string[], reason?: string }
  Response: { approved: Influencer[], denied: string[], quota: QuotaStatus }

# Quota Status
GET /api/v1/partners/quota
  Response: { used, limit, remaining, resetsAt, usageHistory }

# Subscription Status
GET /api/v1/partners/subscription
  Response: { tier, status, features, startDate, endDate, daysRemaining, alerts }

# Profile Enrichment
POST /api/v1/profiles/enrich
  Body: { url: string, callbackUrl?: string }
  Response: { jobId, status: "processing", estimatedTime }

# Batch Refresh
POST /api/v1/profiles/batch-refresh
  Body: { profileIds: string[] }
  Response: { refreshed: Profile[], failed: FailedProfile[], summary }
```

#### Admin API Endpoints

```yaml
# Authentication: Admin session required

# Partner Management
GET    /api/v1/admin/partners              # List partners
POST   /api/v1/admin/partners              # Create partner
GET    /api/v1/admin/partners/:id          # Get partner detail
PATCH  /api/v1/admin/partners/:id          # Update partner
DELETE /api/v1/admin/partners/:id          # Deactivate partner

# API Key Management
POST   /api/v1/admin/partners/:id/regenerate-key  # Regenerate API key

# Subscription Management
PATCH  /api/v1/admin/partners/:id/subscription    # Update subscription
POST   /api/v1/admin/partners/:id/quota/adjust    # Manual quota adjustment

# Influencer Visibility
PATCH  /api/v1/admin/influencers/:id/visibility   # Update single
POST   /api/v1/admin/influencers/bulk-visibility  # Bulk update
```

---

## Implementation Plan

### Stories

| # | Story | Description | Points |
|---|-------|-------------|--------|
| 1 | **Database Schema** | Create Partner, Subscription, Request tables + migrations | 3 |
| 2 | **Partner Service** | CRUD operations cho Partner entity | 3 |
| 3 | **API Key Auth Guard** | Authentication middleware với rate limiting | 5 |
| 4 | **Quota Service** | Quota tracking, monthly reset, tier limits | 5 |
| 5 | **Pool Search Endpoint** | Search với filters, visibility, pagination | 5 |
| 6 | **Pool Request Endpoint** | Request influencers với auto-approval | 5 |
| 7 | **Subscription Service** | Status, features, alerts, grace period | 3 |
| 8 | **Profile Enrichment** | Async crawl với callback integration | 5 |
| 9 | **Admin Partner UI** | List, create, edit, API key management | 5 |
| 10 | **Admin Visibility UI** | Influencer visibility controls | 3 |

**Total:** 42 story points

### Development Phases

```
PHASE 1: Foundation (Week 1-2)
├── Story 1: Database Schema
├── Story 2: Partner Service
└── Story 3: API Key Auth Guard
    └── Milestone: Partner authentication working

PHASE 2: Core API (Week 3-4)
├── Story 4: Quota Service
├── Story 5: Pool Search Endpoint
├── Story 6: Pool Request Endpoint
└── Story 7: Subscription Service
    └── Milestone: Partners can search & request influencers

PHASE 3: Enrichment & Admin (Week 5-6)
├── Story 8: Profile Enrichment
├── Story 9: Admin Partner UI
└── Story 10: Admin Visibility UI
    └── Milestone: Production ready
```

---

## Acceptance Criteria

How we'll know it's done:

- [ ] Partner can authenticate with API key and get 200 response
- [ ] Partner can search influencers with filters (category, platform, followers)
- [ ] Partner can request influencers and receive full data if quota available
- [ ] Quota decrements correctly and resets monthly
- [ ] Rate limiting returns 429 when exceeded
- [ ] Admin can create partner and generate API key
- [ ] Admin can update subscription tier
- [ ] Admin can toggle influencer visibility
- [ ] All tests pass (>80% coverage)
- [ ] OpenAPI spec generated and accurate
- [ ] Deployed to staging environment

---

## Non-Functional Requirements

### Performance

| Metric | Target |
|--------|--------|
| API Response Time (p95) | < 200ms |
| Database Query Time | < 50ms |
| Throughput | 1000 req/sec |
| Pool Search (100K records) | < 200ms |

**Implementation:**
- Database indexes on frequently queried columns
- Redis caching for quota counters
- Connection pooling (Prisma)
- Query optimization với `explain analyze`

### Security

| Requirement | Implementation |
|-------------|----------------|
| API Key Storage | SHA-256 hash, never store plaintext |
| Transport | TLS 1.3 mandatory |
| Rate Limiting | Sliding window, Redis-backed |
| Input Validation | Zod schemas, strict typing |
| Audit Logging | All mutations logged với actor |
| CORS | Whitelist partner domains |

**API Key Format:**
```
im_{env}_{partner_code}_{random32}
Example: im_prod_techcombank_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

### Other

- **Observability:** Prometheus metrics, structured JSON logs
- **Error Tracking:** Sentry integration
- **Documentation:** OpenAPI 3.0 auto-generated
- **Testing:** Unit (Jest), Integration (Supertest), E2E

---

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| `influencer-meter-adapter` | Internal SDK | ✅ Ready | Profile enrichment |
| `influencer-meter-service` | Internal API | ✅ Ready | REST wrapper |
| Vendor Influence-Meter API | External | ✅ Production | Crawling service |
| PostgreSQL 15 | Infrastructure | ✅ Ready | Existing database |
| Redis | Infrastructure | ✅ Ready | Rate limiting, caching |
| Existing Profile table | Database | ✅ Ready | Extend với visibility |

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **API contract breaks partners** | High | Medium | Version API (`/v1/`), deprecation policy, SDK cho partners |
| **Quota calculation race condition** | High | Medium | Redis atomic operations, distributed lock |
| **Vendor API downtime** | High | Low | Circuit breaker pattern, graceful degradation |
| **Database migration issues** | Medium | Medium | Test on staging, backup before deploy |
| **Rate limit bypass** | Medium | Low | Multiple enforcement points, monitoring alerts |

---

## Timeline

**Target Completion:** 6 weeks (42 working days)

**Milestones:**

| Week | Milestone | Deliverables |
|------|-----------|--------------|
| 2 | Foundation Complete | Schema, Partner CRUD, Auth working |
| 4 | Core API Complete | Search, Request, Quota all working |
| 6 | Production Ready | Admin UI, testing, documentation |

**Resource Allocation:**
- 1 Backend Developer (full-time)
- 1 Frontend Developer (50% time for Admin UI)
- Code review by Tech Lead

---

## Approval

**Reviewed By:**
- [ ] Engineering Lead
- [ ] Product Owner
- [ ] Security Review

---

## Next Steps

### Phase 4: Implementation

This is a Level 1 project with 10 stories:

1. Run `/bmad:sprint-planning` to organize sprints
2. Create stories with `/bmad:create-story`
3. Implement with `/bmad:dev-story`

**Recommended Sprint Structure:**
- Sprint 1 (Week 1-2): Stories 1-3 (Foundation)
- Sprint 2 (Week 3-4): Stories 4-7 (Core API)
- Sprint 3 (Week 5-6): Stories 8-10 (Enrichment & Admin)

---

## Appendix

### A. API Key Authentication Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │     │  Guard   │     │  Redis   │     │   DB     │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │ Request +      │                │                │
     │ X-API-Key      │                │                │
     │───────────────▶│                │                │
     │                │                │                │
     │                │ Check rate     │                │
     │                │ limit          │                │
     │                │───────────────▶│                │
     │                │                │                │
     │                │◀───────────────│                │
     │                │ (ok/exceeded)  │                │
     │                │                │                │
     │    429 if      │                │                │
     │◀───exceeded────│                │                │
     │                │                │                │
     │                │ Validate key   │                │
     │                │ (hash + lookup)│                │
     │                │───────────────────────────────▶│
     │                │                │                │
     │                │◀───────────────────────────────│
     │                │ Partner data   │                │
     │                │                │                │
     │    401 if      │                │                │
     │◀───invalid─────│                │                │
     │                │                │                │
     │                │ Attach context │                │
     │                │ to request     │                │
     │                │                │                │
     │    Continue    │                │                │
     │◀───to handler──│                │                │
     ▼                ▼                ▼                ▼
```

### B. Quota Management Logic

```typescript
// Pseudo-code for quota check
async function checkAndDecrementQuota(partnerId: string, count: number): Promise<QuotaResult> {
  // 1. Get current subscription
  const subscription = await getSubscription(partnerId);

  // 2. Check status
  if (subscription.status === 'EXPIRED') {
    throw new QuotaError('Subscription expired');
  }

  // 3. Check if reset needed
  if (isNewMonth(subscription.quotaResetAt)) {
    await resetQuota(subscription);
  }

  // 4. Check quota
  const remaining = subscription.monthlyQuota - subscription.usedThisMonth;
  if (remaining < count) {
    return { success: false, error: 'QUOTA_EXCEEDED', remaining };
  }

  // 5. Decrement (atomic)
  await incrementUsed(subscription.id, count);

  return { success: true, remaining: remaining - count };
}
```

### C. Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "QUOTA_EXCEEDED",
    "message": "Monthly quota exceeded. Used: 50/50. Resets at 2026-02-01.",
    "details": {
      "used": 50,
      "limit": 50,
      "resetsAt": "2026-02-01T00:00:00Z"
    }
  },
  "timestamp": "2026-01-31T10:00:00Z",
  "requestId": "req_abc123"
}
```

---

**This document was created using BMAD Method v6 - Phase 2 (Planning)**

*To continue: Run `/bmad:sprint-planning` to plan your sprints.*
