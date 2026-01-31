# Sprint Plan: AT Core - Influence Library

**Date:** 2026-01-31
**Scrum Master:** Steve (BMAD Method)
**Project Level:** Level 1 (10 stories)
**Module Context:** Feature module trong hệ thống multi-tenant AT Influencer Service

---

## Executive Summary

Sprint plan cho **Influencer Library module** - một feature trong hệ thống multi-tenant của AccessTrade. Module này cung cấp Partner API cho phép các đối tác (Techcombank, Vinfast, Ambassador...) truy cập và sử dụng Influencer Pool với mô hình subscription-based và quota management.

**Key Metrics:**
| Metric | Value |
|--------|-------|
| Total Stories | 12 |
| Total Points | 52 |
| Planned Sprints | 4 |
| Team Size | 1 senior developer |
| Sprint Length | 2 weeks |
| Team Capacity | 15 points/sprint |
| Target Completion | Week 8 (2026-03-28) |

**Important Context:**
- Đây là **module/feature** trong hệ thống lớn hơn, KHÔNG phải standalone service
- Sẽ integrate với existing multi-tenant architecture (feature flags, shared DB)
- Partner/Subscription model sẽ là foundation cho các modules khác (TCB, Vinfast...)

---

## Story Inventory

### STORY-001: Database Schema & Migrations

**Epic:** Foundation
**Priority:** Must Have
**Points:** 5

**User Story:**
As a Developer
I want to have Partner, Subscription, PoolInfluencer, and Request tables
So that I can build Partner API features on top of it

**Acceptance Criteria:**
- [ ] Partner model với id, name, code, apiKeyHash, apiKeyPrefix, isActive, contactInfo, rateLimit
- [ ] PartnerSubscription model với tier, status, quota fields
- [ ] **PoolInfluencer model (NEW)** - AT Shared Pool storage:
  - [ ] id, vbProfileId (reference to ViewBoost)
  - [ ] platform, username, displayName, avatarUrl, bio
  - [ ] followers, following, engagement, avgViews, avgLikes, avgComments
  - [ ] score, scoreReach, scoreEngagement, scoreAuthenticity
  - [ ] category, tier, visibility (PUBLIC/PRIVATE)
  - [ ] contactEmail, contactPhone (encrypted)
  - [ ] addedBy, addedByPartnerId, source (MANUAL/PARTNER/BULK_IMPORT)
  - [ ] syncStatus (ACTIVE/PAUSED/FAILED/ARCHIVED), syncedAt, syncError
- [ ] InfluencerRequest model cho audit trail
- [ ] Enums: SubscriptionTier, SubscriptionStatus, ProfileVisibility, RequestStatus, InfluencerTier, InfluencerSource, SyncStatus
- [ ] Indexes trên frequently queried columns (code, apiKeyHash, visibility, platform, category, score)
- [ ] Migration scripts tested on staging
- [ ] Seed data cho test partner (techcombank) và sample pool influencers

**Technical Notes:**
- **QUAN TRỌNG:** AT lưu simplified profile trong PoolInfluencer table, KHÔNG phụ thuộc VB database
- PoolInfluencer là AT Shared Pool - cho phép search/request mà không cần gọi VB API
- Extend existing Prisma schema trong `influencer-meter-service`
- Schema phải compatible với multi-tenant architecture
- Consider soft delete cho Partner và PoolInfluencer

**Dependencies:** None (foundation)

---

### STORY-002: Partner Service (CRUD)

**Epic:** Foundation
**Priority:** Must Have
**Points:** 3

**User Story:**
As an AT Admin
I want to create and manage partners
So that they can access the Influencer API

**Acceptance Criteria:**
- [ ] Create partner với auto-generated API key
- [ ] API key format: `im_{env}_{partner_code}_{random32}`
- [ ] API key hashed (SHA-256) before storage, only show once
- [ ] Get partner by ID/code
- [ ] Update partner info (name, contact, rateLimit)
- [ ] Deactivate/reactivate partner
- [ ] Regenerate API key (invalidates old one)
- [ ] Unit tests với >80% coverage

**Technical Notes:**
- PartnerService class trong NestJS
- Use crypto.randomBytes cho API key generation
- Store apiKeyPrefix (first 8 chars) for display/identification

**Dependencies:** STORY-001

---

### STORY-003: API Key Authentication Guard

**Epic:** Foundation
**Priority:** Must Have
**Points:** 5

**User Story:**
As a Partner System
I want to authenticate API requests using API key
So that I can access protected endpoints

**Acceptance Criteria:**
- [ ] Request headers: `X-Partner-ID` và `X-API-Key`
- [ ] Valid credentials → attach partner context to request
- [ ] Missing headers → 401 Unauthorized
- [ ] Invalid key → 401 Unauthorized
- [ ] Inactive partner → 403 Forbidden
- [ ] Rate limiting per partner (default: 100 req/min)
- [ ] Exceed rate limit → 429 Too Many Requests
- [ ] Rate limit uses Redis sliding window
- [ ] Update `lastApiCallAt` on successful auth
- [ ] Unit + integration tests

**Technical Notes:**
- NestJS Guard: `PartnerAuthGuard`
- Redis for rate limiting (sliding window algorithm)
- Cache partner data in Redis (TTL: 5 min) to reduce DB queries
- Decorator: `@PartnerAuth()` để apply guard

**Dependencies:** STORY-001, STORY-002

---

### STORY-004: Quota Service

**Epic:** Core API
**Priority:** Must Have
**Points:** 5

**User Story:**
As the System
I want to track and enforce quota limits per partner
So that subscription tiers are respected

**Acceptance Criteria:**
- [ ] Get current quota status (used, limit, remaining, resetsAt)
- [ ] Check quota before allowing requests
- [ ] Decrement quota atomically (prevent race conditions)
- [ ] Monthly reset on day 1 (00:00 UTC+7)
- [ ] Tier limits: FREE=10, BASIC=50, PREMIUM=200, ENTERPRISE=unlimited
- [ ] Quota exceeded → clear error response với reset date
- [ ] Get usage history (last 30 days)
- [ ] Unit tests cho edge cases (month boundary, concurrent requests)

**Technical Notes:**
- QuotaService class
- Use Redis INCR cho atomic counter
- Cron job để reset quota monthly
- Consider Lua script cho atomic check-and-decrement

**Dependencies:** STORY-001, STORY-003

---

### STORY-005: Pool Search Endpoint

**Epic:** Core API
**Priority:** Must Have
**Points:** 5

**User Story:**
As a Partner
I want to search influencers in AT pool
So that I can find suitable creators for campaigns

**Acceptance Criteria:**
- [ ] `GET /api/v1/partners/pool/search`
- [ ] Filters: category, platform, minFollowers, maxFollowers, minEngagement, minScore
- [ ] Only return PUBLIC visibility influencers
- [ ] Preview mode: không show contactInfo và detailedMetrics
- [ ] Pagination: limit (default 20, max 100), offset
- [ ] Sort by: score (default), followers, engagement
- [ ] Response time < 200ms với 100K records
- [ ] OpenAPI documentation
- [ ] Integration tests

**Technical Notes:**
- Controller: PoolController
- Use database indexes cho performance
- Consider full-text search cho username/displayName
- Response DTO: InfluencerPreviewDto (no sensitive data)

**Dependencies:** STORY-003, STORY-004

---

### STORY-006: Pool Request Endpoint

**Epic:** Core API
**Priority:** Must Have
**Points:** 5

**User Story:**
As a Partner
I want to request access to influencers
So that I can get full data including contact info

**Acceptance Criteria:**
- [ ] `POST /api/v1/partners/pool/request`
- [ ] Body: `{ influencerIds: string[], reason?: string }`
- [ ] Batch request: tối đa 20 influencers per request
- [ ] Auto-approve nếu còn quota
- [ ] Decrement quota cho số approved
- [ ] Return full influencer data (including contactInfo, detailedMetrics)
- [ ] Deny với clear message nếu over quota
- [ ] Partial approval nếu quota < requested count
- [ ] Create InfluencerRequest record (audit trail)
- [ ] Response includes quota status
- [ ] Integration tests

**Technical Notes:**
- Transaction để ensure consistency (quota + request record)
- Response DTO: InfluencerFullDto (with sensitive data)
- Consider caching requested influencers per partner

**Dependencies:** STORY-004, STORY-005

---

### STORY-007: Subscription Service

**Epic:** Core API
**Priority:** Must Have
**Points:** 3

**User Story:**
As a Partner
I want to view my subscription status
So that I know my current plan and limits

**Acceptance Criteria:**
- [ ] `GET /api/v1/partners/subscription`
- [ ] Return: tier, status, startDate, endDate, daysRemaining, autoRenew
- [ ] Return features available for tier
- [ ] Alert khi subscription sắp hết hạn (< 7 days)
- [ ] Grace period: 7 days sau khi expired (status: GRACE_PERIOD)
- [ ] After grace period: status → SUSPENDED, deny all requests
- [ ] Unit tests

**Technical Notes:**
- SubscriptionService class
- Feature matrix per tier (store in config or DB)
- Cron job để check expiring subscriptions và send alerts

**Dependencies:** STORY-001, STORY-003

---

### STORY-008: Profile Enrichment Endpoint

**Epic:** Profile Enrichment
**Priority:** Must Have
**Points:** 5

**User Story:**
As a Partner
I want to crawl a new influencer profile
So that I can add influencers not in AT pool

**Acceptance Criteria:**
- [ ] `POST /api/v1/profiles/enrich`
- [ ] Body: `{ url: string, callbackUrl?: string }`
- [ ] Support URLs: TikTok, YouTube, Instagram, Facebook
- [ ] Validate URL format
- [ ] Async processing với job queue
- [ ] Return jobId immediately
- [ ] Callback to partner when complete (if callbackUrl provided)
- [ ] Poll endpoint: `GET /api/v1/profiles/jobs/:jobId`
- [ ] Timeout: 30 seconds for crawl
- [ ] Cache result: 24 hours (don't re-crawl same URL)
- [ ] Use existing `influencer-meter-adapter` SDK
- [ ] Integration tests

**Technical Notes:**
- Use Bull queue cho async jobs
- Call `influencer-meter-adapter.getProfileByUrl()`
- Store job status in Redis
- Webhook callback với retry (3 attempts)

**Dependencies:** STORY-003

---

### STORY-009: Admin Partner Management UI

**Epic:** Admin UI
**Priority:** Must Have
**Points:** 5

**User Story:**
As an AT Admin
I want a UI to manage partners
So that I can onboard and support partners efficiently

**Acceptance Criteria:**
- [ ] `/admin/partners` - List view (table)
  - [ ] Columns: Name, Code, Tier, Status, Quota (used/limit), Last API Call
  - [ ] Filter by: status, tier
  - [ ] Search by: name, code
  - [ ] Sort by any column
- [ ] Create Partner form
  - [ ] Fields: name, code (unique), contactName, contactEmail, contactPhone, tier
  - [ ] Auto-generate và display API key (once only)
  - [ ] Copy to clipboard button
- [ ] Partner Detail page
  - [ ] Profile info (editable)
  - [ ] Subscription management (change tier, extend period)
  - [ ] Quota usage chart (last 30 days)
  - [ ] API key management (regenerate, show prefix)
  - [ ] Request history (recent 50)
  - [ ] Deactivate/Reactivate button
- [ ] Responsive design
- [ ] Loading states, error handling

**Technical Notes:**
- Extend existing Admin UI (Next.js)
- Use existing UI components (shadcn/ui)
- API calls to Admin endpoints
- Feature flag: `features.influencerLibrary.adminPartners`

**Dependencies:** STORY-002, STORY-004, STORY-007

---

### STORY-010: Admin Influencer Visibility Control

**Epic:** Admin UI
**Priority:** Must Have
**Points:** 3

**User Story:**
As an AT Admin
I want to control influencer visibility
So that I can manage what partners can see in the pool

**Acceptance Criteria:**
- [ ] Extend existing Influencer list với visibility column
- [ ] Toggle visibility: PUBLIC ↔ PRIVATE (single influencer)
- [ ] Bulk update visibility (select multiple → change visibility)
- [ ] Filter by visibility
- [ ] Confirmation dialog for bulk changes
- [ ] Audit log khi change visibility (who, when, what)
- [ ] Loading states, error handling

**Technical Notes:**
- Add visibility column to existing influencer table
- Backend: `PATCH /api/v1/admin/influencers/:id/visibility`
- Backend: `POST /api/v1/admin/influencers/bulk-visibility`
- Feature flag: `features.influencerLibrary.adminVisibility`

**Dependencies:** STORY-001, STORY-005

---

### STORY-011: Admin Pool Influencer Management (NEW)

**Epic:** Pool Management
**Priority:** Must Have
**Points:** 5

**User Story:**
As an AT Admin
I want to add, edit, and remove influencers in AT Shared Pool
So that partners can discover and request them

**Acceptance Criteria:**
- [ ] `POST /api/v1/admin/pool/influencers` - Add influencer by social URL
  - [ ] Call VB API to enrich profile
  - [ ] Save simplified profile to PoolInfluencer table
  - [ ] Set category, tier, visibility
- [ ] `GET /api/v1/admin/pool/influencers` - List pool với filters
  - [ ] Filter by: visibility, category, platform, syncStatus
  - [ ] Search by: username, displayName
  - [ ] Sort by: score, followers, createdAt
  - [ ] Pagination
- [ ] `GET /api/v1/admin/pool/influencers/:id` - Get detail
- [ ] `PATCH /api/v1/admin/pool/influencers/:id` - Update AT-specific fields
- [ ] `DELETE /api/v1/admin/pool/influencers/:id` - Soft delete
- [ ] `POST /api/v1/admin/pool/influencers/:id/sync` - Trigger sync for one
- [ ] `POST /api/v1/admin/pool/import` - Bulk import từ CSV
- [ ] Admin UI: `/admin/pool` page với list, add form, detail view
- [ ] Unit + integration tests

**Technical Notes:**
- PoolInfluencerService class
- Use Bull queue cho bulk import và async enrichment
- Call `influencer-meter-adapter.getProfileByUrl()` for enrichment
- Store job status for bulk operations

**Dependencies:** STORY-001, STORY-008

---

### STORY-012: Pool Sync Management (NEW)

**Epic:** Pool Management
**Priority:** Should Have
**Points:** 5

**User Story:**
As an AT Admin
I want to manage sync between AT Pool and ViewBoost
So that pool data stays fresh

**Acceptance Criteria:**
- [ ] `GET /api/v1/admin/sync/status` - Sync dashboard
  - [ ] Last sync time, total count, success/fail count
  - [ ] Next scheduled sync
- [ ] `POST /api/v1/admin/sync/trigger` - Trigger full sync
- [ ] `GET /api/v1/admin/sync/errors` - List failed syncs
- [ ] `POST /api/v1/admin/sync/retry` - Retry failed syncs
- [ ] `PATCH /api/v1/admin/sync/settings` - Update sync config
- [ ] Cron job: Daily sync at 4 AM (configurable)
- [ ] Batch processing: 100 influencers per batch
- [ ] Update PoolInfluencer.syncedAt, syncStatus, syncError
- [ ] Admin UI: `/admin/pool/sync` dashboard
- [ ] Unit tests

**Technical Notes:**
- SyncService class
- Use node-cron for scheduling
- Use Bull queue for batch processing
- Circuit breaker for VB API calls
- Store sync history for debugging

**Dependencies:** STORY-001, STORY-011

---

## Sprint Allocation

### Sprint 1: Foundation (Week 1-2)

**Goal:** Complete database foundation (bao gồm PoolInfluencer) và partner authentication system

**Capacity:** 15 points
**Committed:** 13 points (87% utilization)

| Story | Title | Points | Priority |
|-------|-------|--------|----------|
| STORY-001 | Database Schema & Migrations (incl. PoolInfluencer) | 5 | Must Have |
| STORY-002 | Partner Service (CRUD) | 3 | Must Have |
| STORY-003 | API Key Authentication Guard | 5 | Must Have |

**Deliverable:** Partner có thể được tạo và authenticate qua API key với rate limiting. PoolInfluencer table ready cho AT Shared Pool.

**Risks:**
- Schema design issues → Review kỹ trước khi implement
- Redis setup for rate limiting → Verify Redis available in environment

**Sprint 1 Definition of Done:**
- [ ] All stories pass acceptance criteria
- [ ] Unit tests >80% coverage
- [ ] Integration tests passing
- [ ] Code reviewed
- [ ] Deployed to staging
- [ ] Demo: Partner authentication working

---

### Sprint 2: Core API (Week 3-4)

**Goal:** Complete core Partner API - Pool Search, Request, và Quota Management

**Capacity:** 15 points
**Committed:** 15 points (100% utilization)

| Story | Title | Points | Priority |
|-------|-------|--------|----------|
| STORY-004 | Quota Service | 5 | Must Have |
| STORY-005 | Pool Search Endpoint | 5 | Must Have |
| STORY-006 | Pool Request Endpoint | 5 | Must Have |

**Deliverable:** Partners có thể search pool, request influencers với quota enforcement

**Risks:**
- Performance với large dataset → Early performance testing
- Quota race conditions → Use Redis atomic operations
- Complex request logic → Thorough integration testing

**Sprint 2 Definition of Done:**
- [ ] All stories pass acceptance criteria
- [ ] API response time < 200ms (p95)
- [ ] Quota tracking 100% accurate
- [ ] OpenAPI spec updated
- [ ] Deployed to staging
- [ ] Demo: Full search → request flow working

---

### Sprint 3: Enrichment & Admin Partner (Week 5-6)

**Goal:** Complete Profile Enrichment, Subscription service, và Admin Partner UI

**Capacity:** 15 points
**Committed:** 13 points (87% utilization)

| Story | Title | Points | Priority |
|-------|-------|--------|----------|
| STORY-007 | Subscription Service | 3 | Must Have |
| STORY-008 | Profile Enrichment Endpoint | 5 | Must Have |
| STORY-009 | Admin Partner Management UI | 5 | Must Have |

**Deliverable:** Partner có thể enrich profiles, subscription management working, Admin Partner UI ready

**Risks:**
- Admin UI complexity → May need to simplify some features
- Async job handling → Use existing Bull queue setup

**Sprint 3 Definition of Done:**
- [ ] All stories pass acceptance criteria
- [ ] Profile enrichment working end-to-end
- [ ] Admin Partner UI functional
- [ ] Deployed to staging
- [ ] Demo: Enrichment flow + Admin Partner management

---

### Sprint 4: Pool Management & Completion (Week 7-8)

**Goal:** Complete AT Shared Pool Management - Admin có thể add/manage influencers trong pool

**Capacity:** 15 points
**Committed:** 13 points (87% utilization)

| Story | Title | Points | Priority |
|-------|-------|--------|----------|
| STORY-010 | Admin Influencer Visibility Control | 3 | Must Have |
| STORY-011 | Admin Pool Influencer Management | 5 | Must Have |
| STORY-012 | Pool Sync Management | 5 | Should Have |

**Deliverable:** AT Admin có thể add influencers vào pool, manage visibility, và sync với VB

**Risks:**
- Bulk import complexity → Start với single add, add bulk later
- Sync reliability → Implement retry mechanism
- STORY-012 có thể simplified version nếu thiếu time

**Sprint 4 Definition of Done:**
- [ ] All stories pass acceptance criteria
- [ ] Full E2E testing (Partner search → request → Admin manage pool)
- [ ] Documentation complete
- [ ] Deployed to staging
- [ ] Production readiness review
- [ ] Demo: Complete flow từ Admin add to pool → Partner search → Partner request

---

## Timeline Summary

```
Week 1-2 (Sprint 1): Foundation
├── STORY-001: Database Schema + PoolInfluencer  [██████████] 5 pts
├── STORY-002: Partner Service                   [████████░░] 3 pts
└── STORY-003: Auth Guard + Rate Limit           [██████████] 5 pts
    └── Milestone: Partner Auth Working + Pool DB Ready

Week 3-4 (Sprint 2): Core API
├── STORY-004: Quota Service             [██████████] 5 pts
├── STORY-005: Pool Search               [██████████] 5 pts
└── STORY-006: Pool Request              [██████████] 5 pts
    └── Milestone: Partners Can Search & Request from AT Pool

Week 5-6 (Sprint 3): Enrichment & Admin Partner
├── STORY-007: Subscription Service      [████████░░] 3 pts
├── STORY-008: Profile Enrichment        [██████████] 5 pts
└── STORY-009: Admin Partner UI          [██████████] 5 pts
    └── Milestone: Enrichment + Admin Partner Ready

Week 7-8 (Sprint 4): Pool Management & Completion
├── STORY-010: Admin Visibility Control  [████████░░] 3 pts
├── STORY-011: Admin Pool Management     [██████████] 5 pts  ← NEW
└── STORY-012: Pool Sync Management      [██████████] 5 pts  ← NEW
    └── Milestone: Production Ready - Full Pool Management
```

---

## Epic Traceability

| Epic | Stories | Total Points | Sprint |
|------|---------|--------------|--------|
| Foundation | STORY-001, 002, 003 | 13 points | Sprint 1 |
| Core API | STORY-004, 005, 006, 007 | 18 points | Sprint 2-3 |
| Profile Enrichment | STORY-008 | 5 points | Sprint 3 |
| Admin Partner | STORY-009 | 5 points | Sprint 3 |
| Pool Management (NEW) | STORY-010, 011, 012 | 13 points | Sprint 4 |

---

## Functional Requirements Coverage

| FR ID | FR Name | Story | Sprint |
|-------|---------|-------|--------|
| FR-001 | Partner Authentication | STORY-002, 003 | 1 |
| FR-002 | Influencer Pool Search | STORY-005 | 2 |
| FR-003 | Request Influencers from Pool | STORY-006 | 2 |
| FR-004 | Quota Management | STORY-004 | 2 |
| FR-005 | Subscription Status | STORY-007 | 3 |
| FR-006 | Profile Enrichment | STORY-008 | 3 |
| FR-007 | Batch Refresh Profiles | STORY-008 (partial), STORY-012 | 3, 4 |
| FR-008 | Partner Management (Admin) | STORY-009 | 3 |
| FR-009 | Influencer Visibility Control | STORY-010 | 4 |
| FR-010 | Subscription Management (Admin) | STORY-009 (partial) | 3 |
| **FR-011** | **Pool Influencer Management (Admin)** | **STORY-011** | **4** |
| **FR-012** | **Pool Sync Management (Admin)** | **STORY-012** | **4** |

---

## Risks and Mitigation

### High Risk

| Risk | Impact | Mitigation |
|------|--------|------------|
| API contract changes break downstream | High | Version API (`/v1/`), maintain backwards compatibility |
| Quota calculation race conditions | High | Use Redis atomic operations, implement distributed lock |
| Performance với 100K+ influencers | High | Database indexes, query optimization, caching |

### Medium Risk

| Risk | Impact | Mitigation |
|------|--------|------------|
| Schema migration issues | Medium | Test on staging, backup before deploy |
| Rate limit bypass attempts | Medium | Multiple enforcement points, monitoring alerts |
| Admin UI complexity | Medium | Prioritize core features, iterate on UX |

### Low Risk

| Risk | Impact | Mitigation |
|------|--------|------------|
| Vendor API downtime | Low | Circuit breaker already in adapter |
| Redis unavailable | Low | Fallback to database, monitor Redis health |

---

## Dependencies

### External Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| `influencer-meter-adapter` | Internal SDK | ✅ Ready | For profile enrichment |
| `influencer-meter-service` | Internal API | ✅ Ready | Existing backend to extend |
| Vendor Influencer Platform API | External | ✅ Production | Via adapter |
| PostgreSQL | Infrastructure | ✅ Ready | Existing database |
| Redis | Infrastructure | ✅ Ready | For rate limiting, caching, job queue |
| Existing Admin UI | Frontend | ✅ Ready | Next.js app to extend |

### Internal Dependencies (Story Level)

```
STORY-001 (DB Schema + PoolInfluencer)
    │
    ├── STORY-002 (Partner Service)
    │       │
    │       └── STORY-003 (Auth Guard)
    │               │
    │               ├── STORY-004 (Quota Service)
    │               │       │
    │               │       ├── STORY-005 (Pool Search) ← queries PoolInfluencer
    │               │       │       │
    │               │       │       └── STORY-006 (Pool Request)
    │               │       │
    │               │       └── STORY-007 (Subscription)
    │               │
    │               └── STORY-008 (Profile Enrichment)
    │                       │
    │                       └── STORY-011 (Admin Pool Management) ← uses enrichment
    │                               │
    │                               └── STORY-012 (Pool Sync Management)
    │
    └── STORY-009 (Admin Partner UI) ← depends on 002, 004, 007

STORY-001 + STORY-005 → STORY-010 (Admin Visibility)
```

---

## Definition of Done

For a story to be considered complete:

- [ ] Code implemented and committed
- [ ] Unit tests written and passing (≥80% coverage)
- [ ] Integration tests passing
- [ ] Code reviewed and approved
- [ ] OpenAPI spec updated (for API endpoints)
- [ ] Feature flag added (for new features)
- [ ] Documentation updated
- [ ] Deployed to staging environment
- [ ] Acceptance criteria validated
- [ ] No critical/high bugs open

---

## Multi-Tenant Considerations

Vì đây là module trong hệ thống multi-tenant:

1. **Feature Flags:** Mọi features mới đều wrap trong feature flag
   ```yaml
   features:
     influencerLibrary:
       enabled: true
       adminPartners: true
       adminVisibility: true
       poolSearch: true
       poolRequest: true
       profileEnrich: true
   ```

2. **Tenant Isolation:** Partner data isolated by partnerId
3. **Shared Pool:** Influencer pool là shared resource, visibility controls access
4. **Extensibility:** Design APIs để có thể reuse cho future partners (Vinfast, etc.)

---

## Next Steps

**Immediate:** Begin Sprint 1

```
✓ Sprint plan complete (4 sprints, 8 weeks)

Ready for implementation!

Options:
1. /bmad:create-story STORY-001 - Create detailed story document
2. /bmad:dev-story STORY-001 - Start implementing immediately
3. /bmad:sprint-status - Check current sprint status

Recommended: Start with /bmad:dev-story STORY-001 (Database Schema + PoolInfluencer)
```

**Sprint Cadence:**
- Sprint length: 2 weeks
- Sprint planning: Monday Week 1
- Daily standup: Async (status update in TODO)
- Sprint review: Friday Week 2
- Sprint retrospective: Friday Week 2

---

## Key Architecture Note: AT Shared Pool

**QUAN TRỌNG:** AT **PHẢI** lưu profile riêng trong `PoolInfluencer` table để:

1. **Cho phép Partners search** - Không thể search nếu không có data
2. **Control visibility** - Quyết định influencer nào PUBLIC/PRIVATE
3. **Giảm latency** - Trả về data từ AT DB thay vì gọi VB mỗi lần
4. **Quản lý độc lập** - AT có thể add/remove influencer khỏi pool

```
VB (Vendor) → crawl/score → AT Pool (simplified) → Partners search/request
                              ↑
                    AT Admin add/manage
```

Xem thêm chi tiết tại: [PRD Section 2.4 - AT Shared Pool Architecture](prd-at-core-influence-library-2026-01-31.md#24-at-shared-pool-architecture)

---

**This plan was created using BMAD Method v6 - Phase 4 (Implementation Planning)**
**Module: AT Core - Influence Library (Multi-tenant Feature)**
**Updated:** 2026-01-31 (Added FR-011, FR-012 for Pool Management)
