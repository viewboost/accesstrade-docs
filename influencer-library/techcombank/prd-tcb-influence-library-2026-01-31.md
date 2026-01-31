# Product Requirements Document: TCB - Influence Library

**Document Version:** 1.0
**Date:** 2026-01-31
**Product Owner:** Techcombank
**Status:** Draft

---

## 1. Executive Summary

### 1.1 Product Vision
Xây dựng **TCB Influencer Library** - hệ thống quản lý influencer độc lập cho Techcombank, bao gồm Database, API, Admin UI và Sync Service. TCB sẽ sở hữu 100% source code và data, có khả năng:
- Thêm influencer riêng (private) qua crawl từ social platforms
- Request influencer từ AT Shared Pool (theo quota subscription)
- Tự động sync metrics hàng ngày
- Quản lý influencer với tags/notes riêng của TCB

### 1.2 Problem Statement
Techcombank cần influencer data để chạy campaigns marketing nhưng:
- Không muốn build hệ thống crawl/scoring từ đầu (tốn chi phí, thời gian)
- Cần sở hữu 100% data và source code (IP ownership)
- Cần kết hợp influencers riêng của TCB với influencers từ AT Pool
- Cần metrics cập nhật thường xuyên

### 1.3 Target Users
| User Type | Description |
|-----------|-------------|
| **TCB Marketing Team** | Sử dụng Admin UI để tìm kiếm, quản lý influencers cho campaigns |
| **TCB Campaign Managers** | Xem metrics, score để chọn influencer phù hợp |
| **TCB Developers** | Integrate với TCB API để build các ứng dụng internal |

### 1.4 Success Metrics
| Metric | Target |
|--------|--------|
| Influencer Library Size | 500+ influencers trong 6 tháng |
| Data Freshness | Metrics được update daily |
| System Availability | 99.5% uptime |
| User Adoption | 80% marketing team sử dụng |

---

## 2. Scope

### 2.1 In Scope (TCB Modules)
| Module | Description |
|--------|-------------|
| **M4. TCB Database** | Schema cho Influencer, SyncLog với source tracking |
| **M5. TCB API** | REST API cho influencer CRUD, AT integration, sync |
| **M6. TCB Admin** | Next.js UI cho quản lý influencers |
| **M7. TCB Sync Service** | Cron job daily sync + freeze logic |

### 2.2 Out of Scope
- AT Partner API (covered in AT Core PRD)
- Social platform crawling (handled by AT via Vendor)
- Score calculation algorithm (Vendor IP)
- Payment integration cho subscription
- Mobile application

### 2.3 Dependencies
| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| AT Partner API | External API | 🔄 In Development | M1 từ AT Core |
| AT Subscription | External | 🔄 In Development | Quota management |
| PostgreSQL | Infrastructure | ✅ Ready | TCB owns instance |
| Redis | Infrastructure | ✅ Ready | Caching |

### 2.4 Assumptions
- AT Partner API sẽ ready trước khi TCB bắt đầu AT integration
- TCB có quyền access AT Partner API với valid credentials (X-Partner-ID, X-API-Key)
- TCB subscription tier đã được setup bởi AT Admin

---

## 3. Functional Requirements

### 3.1 FR-001: Influencer Data Storage

**Priority:** Must Have

**Description:** Hệ thống phải lưu trữ influencer data với khả năng phân biệt nguồn (private vs AT shared).

**Acceptance Criteria:**
- [ ] Lưu trữ influencer từ 2 sources: `TCB_PRIVATE` và `AT_SHARED`
- [ ] Lưu trữ profile data: platform, username, displayName, avatarUrl, bio
- [ ] Lưu trữ metrics: followers, following, engagement rate, avg views
- [ ] Lưu trữ score và score breakdown
- [ ] Track sync status: `ACTIVE`, `FROZEN`, `DELETED`
- [ ] Support TCB-specific fields: tags, notes
- [ ] Unique constraint trên (platform, username)

**Data Model:**
```typescript
interface TCBInfluencer {
  id: string
  source: 'TCB_PRIVATE' | 'AT_SHARED'
  atInfluencerId?: string        // Reference to AT
  vendorProfileId?: string       // Reference to Vendor

  // Profile
  platform: 'tiktok' | 'youtube' | 'instagram' | 'facebook'
  username: string
  displayName?: string
  avatarUrl?: string
  bio?: string

  // Metrics
  followers: number
  following: number
  engagement: number
  avgViews: number

  // Score
  score: number
  scoreBreakdown?: ScoreBreakdown

  // Sync
  syncStatus: 'ACTIVE' | 'FROZEN' | 'DELETED'
  syncedAt?: Date
  frozenAt?: Date

  // TCB-specific
  tags: string[]
  notes?: string

  createdAt: Date
  updatedAt: Date
}
```

---

### 3.2 FR-002: Add Private Influencer

**Priority:** Must Have

**Description:** TCB Admin có thể thêm influencer riêng bằng cách nhập social URL, hệ thống sẽ gọi AT API để crawl profile.

**Acceptance Criteria:**
- [ ] Input: Social URL (TikTok, YouTube, Instagram, Facebook)
- [ ] Validate URL format trước khi gọi API
- [ ] Gọi AT API `POST /profiles/enrich` để crawl
- [ ] Support async processing với callback URL
- [ ] Hiển thị loading state trong UI
- [ ] Lưu profile vào TCB DB với `source: TCB_PRIVATE`
- [ ] Handle errors: invalid URL, profile not found, crawl timeout
- [ ] Prevent duplicate (check existing platform + username)

**API Flow:**
```
TCB Admin → TCB API → AT API → Vendor → Social Platform
                                   ↓
TCB Admin ← TCB API ← AT API ← Vendor (profile data)
                ↓
            Save to TCB DB
```

---

### 3.3 FR-003: List Influencers

**Priority:** Must Have

**Description:** Hiển thị danh sách influencers với filters và pagination.

**Acceptance Criteria:**
- [ ] List tất cả influencers (cả private + shared)
- [ ] Filter by source: `all`, `tcb_private`, `at_shared`
- [ ] Filter by platform: `tiktok`, `youtube`, `instagram`, `facebook`
- [ ] Filter by sync status: `active`, `frozen`
- [ ] Search by name hoặc username (case-insensitive)
- [ ] Sort by: followers, engagement, score, createdAt
- [ ] Pagination với limit/offset
- [ ] Hiển thị: avatar, name, platform, followers, engagement, score, source badge, sync status

**API Endpoint:**
```yaml
GET /api/v1/influencers
Query:
  source: all | tcb_private | at_shared
  platform: tiktok | youtube | instagram | facebook
  syncStatus: active | frozen
  search: string
  sortBy: followers | engagement | score | createdAt
  sortOrder: asc | desc
  limit: 20 (default)
  offset: 0

Response:
  {
    "data": Influencer[],
    "pagination": {
      "total": number,
      "limit": number,
      "offset": number,
      "hasMore": boolean
    }
  }
```

---

### 3.4 FR-004: View Influencer Detail

**Priority:** Must Have

**Description:** Xem chi tiết influencer với full metrics và score breakdown.

**Acceptance Criteria:**
- [ ] Hiển thị profile header: avatar, name, platform icon, username
- [ ] Hiển thị metrics cards: followers, following, engagement, avg views
- [ ] Hiển thị score với breakdown (reach, engagement, authenticity)
- [ ] Hiển thị source badge và sync status
- [ ] Hiển thị TCB tags và notes (editable)
- [ ] Hiển thị last synced timestamp
- [ ] Nếu `FROZEN`: hiển thị warning banner

**API Endpoint:**
```yaml
GET /api/v1/influencers/:id

Response:
  {
    "data": {
      "id": "tcb_inf_001",
      "source": "at_shared",
      "platform": "tiktok",
      "username": "beauty_creator",
      "displayName": "Beauty Creator VN",
      "avatarUrl": "https://...",
      "followers": 250000,
      "engagement": 4.8,
      "score": 78,
      "scoreBreakdown": {
        "reach": 75,
        "engagement": 82,
        "authenticity": 80
      },
      "syncStatus": "active",
      "syncedAt": "2026-01-31T04:00:00Z",
      "tags": ["beauty", "tết-2026"],
      "notes": "Đã hợp tác campaign Q4 2025"
    }
  }
```

---

### 3.5 FR-005: Update TCB-Specific Fields

**Priority:** Must Have

**Description:** TCB Admin có thể cập nhật tags và notes cho influencer.

**Acceptance Criteria:**
- [ ] Update tags (array of strings)
- [ ] Update notes (free text)
- [ ] Validate tags: max 10 tags, max 50 chars mỗi tag
- [ ] Validate notes: max 1000 chars
- [ ] Chỉ update TCB fields, không thay đổi profile/metrics data

**API Endpoint:**
```yaml
PATCH /api/v1/influencers/:id
Body:
  {
    "tags": ["beauty", "tết-2026", "premium"],
    "notes": "Đã hợp tác campaign Q4 2025. Contact: manager@email.com"
  }

Response:
  {
    "data": Influencer
  }
```

---

### 3.6 FR-006: Delete Private Influencer

**Priority:** Must Have

**Description:** TCB Admin có thể xóa influencer private (không thể xóa AT shared).

**Acceptance Criteria:**
- [ ] Chỉ cho phép delete influencer có `source: TCB_PRIVATE`
- [ ] AT_SHARED influencers không thể delete (return error)
- [ ] Soft delete: set `syncStatus: DELETED`
- [ ] Confirm dialog trước khi delete
- [ ] Không hiển thị deleted influencers trong list (trừ khi filter explicitly)

**API Endpoint:**
```yaml
DELETE /api/v1/influencers/:id

Response (success):
  { "success": true }

Response (error - AT_SHARED):
  {
    "success": false,
    "error": {
      "code": "CANNOT_DELETE_SHARED",
      "message": "Cannot delete influencer from AT Shared Pool"
    }
  }
```

---

### 3.7 FR-007: Search AT Pool

**Priority:** Must Have

**Description:** TCB Admin có thể search influencers từ AT Shared Pool để request về TCB.

**Acceptance Criteria:**
- [ ] Search với filters: category, platform, followers range, engagement range
- [ ] Hiển thị preview data (không có contact info)
- [ ] Hiển thị influencers đã có trong TCB DB (để tránh duplicate request)
- [ ] Pagination
- [ ] Cho phép select multiple influencers để request

**API Endpoint:**
```yaml
GET /api/v1/at-influencers/search
Query:
  category: beauty | tech | lifestyle | food | travel | gaming
  platform: tiktok | youtube | instagram | facebook
  minFollowers: number
  maxFollowers: number
  minEngagement: number
  minScore: number
  limit: 20
  offset: 0

Response:
  {
    "data": [
      {
        "atId": "at_inf_789",
        "platform": "tiktok",
        "username": "beauty_guru",
        "displayName": "Beauty Guru VN",
        "avatarUrl": "https://...",
        "followers": 500000,
        "category": "beauty",
        "score": 85,
        "previewOnly": true,
        "alreadyInTCB": false    // Check nếu đã có trong TCB DB
      }
    ],
    "pagination": {...}
  }
```

---

### 3.8 FR-008: Request Influencers from AT Pool

**Priority:** Must Have

**Description:** TCB Admin có thể request influencers từ AT Pool, auto-approve nếu còn quota.

**Acceptance Criteria:**
- [ ] Select 1-20 influencers per request
- [ ] Gọi AT API `POST /partners/pool/request`
- [ ] Auto-approve nếu còn quota
- [ ] Lưu approved influencers vào TCB DB với `source: AT_SHARED`
- [ ] Hiển thị full data (bao gồm contact info) sau khi approved
- [ ] Handle quota exceeded error
- [ ] Update quota display sau mỗi request

**API Endpoint:**
```yaml
POST /api/v1/at-influencers/request
Body:
  {
    "influencerIds": ["at_inf_789", "at_inf_790"],
    "reason": "Campaign Tết 2026"
  }

Response (success):
  {
    "success": true,
    "approved": [
      {
        "id": "tcb_inf_456",
        "atId": "at_inf_789",
        "source": "at_shared",
        "platform": "tiktok",
        "username": "beauty_guru",
        "followers": 500000,
        "engagement": 5.2,
        "score": 85,
        "contactInfo": {
          "email": "...",
          "phone": "..."
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

Response (over quota):
  {
    "success": false,
    "error": {
      "code": "QUOTA_EXCEEDED",
      "message": "Monthly quota exceeded"
    },
    "quota": { "used": 50, "limit": 50, "remaining": 0 }
  }
```

---

### 3.9 FR-009: View Quota Status

**Priority:** Must Have

**Description:** Hiển thị quota usage và subscription status.

**Acceptance Criteria:**
- [ ] Hiển thị current tier (FREE, BASIC, PREMIUM, ENTERPRISE)
- [ ] Hiển thị quota: used / limit
- [ ] Hiển thị remaining quota
- [ ] Hiển thị reset date (ngày 1 hàng tháng)
- [ ] Progress bar visualization
- [ ] Warning khi quota > 80%
- [ ] Critical alert khi quota = 100%

**API Endpoint:**
```yaml
GET /api/v1/at-influencers/quota

Response:
  {
    "partnerId": "techcombank",
    "tier": "premium",
    "quota": {
      "used": 45,
      "limit": 200,
      "remaining": 155,
      "percentUsed": 22.5,
      "resetsAt": "2026-02-01T00:00:00Z"
    },
    "subscription": {
      "status": "active",
      "startDate": "2026-01-01T00:00:00Z",
      "endDate": "2026-12-31T23:59:59Z"
    }
  }
```

---

### 3.10 FR-010: Daily Metrics Sync

**Priority:** Must Have

**Description:** Cron job tự động sync metrics từ AT hàng ngày.

**Acceptance Criteria:**
- [ ] Run daily lúc 4:00 AM (off-peak)
- [ ] Sync tất cả influencers có `syncStatus: ACTIVE`
- [ ] Gọi AT API `POST /profiles/batch-refresh` (50 profiles per batch)
- [ ] Update metrics trong TCB DB
- [ ] Log sync results: total, success, failed
- [ ] Retry failed profiles (max 3 retries)
- [ ] Alert nếu > 10% profiles fail

**Sync Flow:**
```
Cron Trigger (4:00 AM)
        ↓
Check subscription status
        ↓
    [active?]
    ↓ Yes              ↓ No
Get influencers      Freeze all AT_SHARED
        ↓
Batch refresh via AT API
        ↓
Update TCB DB
        ↓
Log results
```

---

### 3.11 FR-011: Freeze Logic

**Priority:** Must Have

**Description:** Khi subscription expired, AT_SHARED influencers bị freeze (data còn, không sync).

**Acceptance Criteria:**
- [ ] Check subscription status trước mỗi sync
- [ ] Nếu `expired` hoặc `suspended`: freeze tất cả AT_SHARED influencers
- [ ] Freeze = set `syncStatus: FROZEN`, `frozenAt: now()`
- [ ] Frozen influencers vẫn viewable trong Admin UI
- [ ] Hiển thị warning banner cho frozen influencers
- [ ] Không cho request thêm từ AT Pool khi expired
- [ ] TCB_PRIVATE không bị ảnh hưởng

**Freeze Rules:**
| Subscription Status | TCB_PRIVATE | AT_SHARED |
|---------------------|-------------|-----------|
| ACTIVE | ✅ Normal | ✅ Normal |
| GRACE_PERIOD | ✅ Normal | ⚠️ Warning, still sync |
| EXPIRED | ✅ Normal | 🧊 FROZEN |
| SUSPENDED | ✅ Normal | 🧊 FROZEN |

---

### 3.12 FR-012: Manual Sync Trigger

**Priority:** Should Have

**Description:** TCB Admin có thể trigger sync manually.

**Acceptance Criteria:**
- [ ] Button "Sync Now" trong Admin UI
- [ ] Confirm dialog
- [ ] Chỉ sync nếu subscription active
- [ ] Hiển thị progress/status
- [ ] Disable button khi sync đang chạy
- [ ] Show last sync timestamp

**API Endpoint:**
```yaml
POST /api/v1/sync/trigger

Response:
  {
    "jobId": "sync_job_001",
    "status": "started",
    "startedAt": "2026-01-31T10:00:00Z"
  }

GET /api/v1/sync/status

Response:
  {
    "lastSync": {
      "completedAt": "2026-01-31T04:00:00Z",
      "total": 150,
      "success": 148,
      "failed": 2
    },
    "nextSync": "2026-02-01T04:00:00Z",
    "currentJob": null | {
      "jobId": "...",
      "status": "running",
      "progress": 45
    }
  }
```

---

### 3.13 FR-013: Webhook Handlers

**Priority:** Should Have

**Description:** Handle webhooks từ AT để nhận updates real-time.

**Acceptance Criteria:**
- [ ] Endpoint cho crawl complete callback
- [ ] Validate webhook signature
- [ ] Update influencer data khi nhận callback
- [ ] Idempotent (handle duplicate webhooks)
- [ ] Log all webhooks

**API Endpoints:**
```yaml
POST /api/v1/webhooks/crawl-complete
Body:
  {
    "jobId": "job_abc123",
    "status": "completed",
    "profile": {...}
  }

POST /api/v1/webhooks/at-sync
Body:
  {
    "influencerId": "at_inf_789",
    "data": {...}
  }
```

---

### 3.14 FR-014: Sync Log History

**Priority:** Could Have

**Description:** Xem history của sync jobs.

**Acceptance Criteria:**
- [ ] List sync logs với pagination
- [ ] Filter by type: DAILY_FULL, MANUAL, WEBHOOK
- [ ] Filter by status: RUNNING, COMPLETED, FAILED
- [ ] Show: timestamp, type, total, success, failed, duration
- [ ] Drill down to see failed profiles

---

## 4. Non-Functional Requirements

### 4.1 NFR-001: Performance

| Metric | Requirement |
|--------|-------------|
| API Response Time (p95) | < 200ms |
| List page load | < 1s (100 influencers) |
| Search response | < 300ms |
| Sync throughput | 500 profiles / 5 minutes |
| Database query time | < 50ms |

### 4.2 NFR-002: Availability

| Metric | Requirement |
|--------|-------------|
| Uptime SLA | 99.5% |
| Sync job success rate | > 95% |
| Recovery Time Objective (RTO) | < 2 hours |
| Recovery Point Objective (RPO) | < 24 hours (sync frequency) |

### 4.3 NFR-003: Security

| Requirement | Implementation |
|-------------|----------------|
| Authentication | TCB internal SSO |
| Authorization | Role-based (Admin, Viewer) |
| AT API Credentials | Stored in secrets manager |
| Webhook Validation | HMAC signature |
| Audit Logging | All mutations logged |
| Data Encryption | At rest (AES-256), in transit (TLS 1.3) |

### 4.4 NFR-004: Scalability

| Metric | Requirement |
|--------|-------------|
| Influencers | Support 10,000+ profiles |
| Concurrent Users | 50+ simultaneous |
| Sync batch size | 50 profiles per batch |
| Data retention | 2 years |

### 4.5 NFR-005: Maintainability

| Requirement | Implementation |
|-------------|----------------|
| Code Coverage | > 80% |
| Documentation | OpenAPI spec, README |
| Logging | Structured JSON, correlation IDs |
| Monitoring | Health checks, metrics |
| Error Tracking | Sentry integration |

---

## 5. Epics and User Stories

### Epic 1: Database Setup (M4)

**Description:** Setup TCB Database schema và infrastructure.

**Functional Requirements:** FR-001

**Story Count Estimate:** 3 stories

**Priority:** Must Have

**User Stories:**

**E1-US01: Database Schema Design**
```
AS a Developer
I WANT to have a well-designed database schema
SO THAT I can store influencer data efficiently

Acceptance Criteria:
- Influencer table with all required fields
- SyncLog table for tracking sync history
- Proper indexes on frequently queried columns
- Enum types for source, syncStatus, platform
```

**E1-US02: Database Migration**
```
AS a Developer
I WANT to run database migrations
SO THAT the schema is created in all environments

Acceptance Criteria:
- Migration scripts created
- Can run on local, staging, production
- Rollback script available
```

**E1-US03: Seed Data**
```
AS a Developer
I WANT to have test data
SO THAT I can develop and test features

Acceptance Criteria:
- 10 sample influencers (mix private + shared)
- Sample sync logs
- Data realistic enough for testing
```

---

### Epic 2: Influencer CRUD (M5)

**Description:** API endpoints cho basic influencer management.

**Functional Requirements:** FR-002, FR-003, FR-004, FR-005, FR-006

**Story Count Estimate:** 5 stories

**Priority:** Must Have

**User Stories:**

**E2-US01: List Influencers API**
```
AS TCB Admin
I WANT to see all influencers in a list
SO THAT I can browse and find influencers

Acceptance Criteria:
- Pagination works correctly
- Filters work (source, platform, syncStatus)
- Search by name/username
- Sort by different fields
```

**E2-US02: Get Influencer Detail API**
```
AS TCB Admin
I WANT to see full details of an influencer
SO THAT I can understand their profile and metrics

Acceptance Criteria:
- Returns all fields including score breakdown
- Returns TCB-specific fields (tags, notes)
- Returns sync status
```

**E2-US03: Add Private Influencer API**
```
AS TCB Admin
I WANT to add an influencer from social URL
SO THAT I can build my private influencer library

Acceptance Criteria:
- Validates URL format
- Calls AT API for crawl
- Saves to DB on success
- Handles errors gracefully
```

**E2-US04: Update Influencer Tags/Notes API**
```
AS TCB Admin
I WANT to add tags and notes to influencers
SO THAT I can organize and annotate them

Acceptance Criteria:
- Can update tags (max 10)
- Can update notes (max 1000 chars)
- Validates input
```

**E2-US05: Delete Private Influencer API**
```
AS TCB Admin
I WANT to remove a private influencer
SO THAT I can clean up my library

Acceptance Criteria:
- Only deletes TCB_PRIVATE
- Returns error for AT_SHARED
- Soft delete (syncStatus: DELETED)
```

---

### Epic 3: AT Pool Integration (M5)

**Description:** Integration với AT Partner API để search và request influencers.

**Functional Requirements:** FR-007, FR-008, FR-009

**Story Count Estimate:** 4 stories

**Priority:** Must Have

**User Stories:**

**E3-US01: AT API Client**
```
AS a Developer
I WANT to have a client for AT Partner API
SO THAT I can make API calls reliably

Acceptance Criteria:
- Configured with credentials
- Handles authentication headers
- Retry logic for transient errors
- Timeout handling
```

**E3-US02: Search AT Pool API**
```
AS TCB Admin
I WANT to search influencers in AT Pool
SO THAT I can find suitable creators for campaigns

Acceptance Criteria:
- Proxies to AT API
- Returns preview data
- Marks influencers already in TCB
- Pagination works
```

**E3-US03: Request Influencers API**
```
AS TCB Admin
I WANT to request influencers from AT Pool
SO THAT I can add them to my library

Acceptance Criteria:
- Sends request to AT API
- Saves approved influencers to DB
- Returns quota status
- Handles quota exceeded
```

**E3-US04: Get Quota Status API**
```
AS TCB Admin
I WANT to see my quota status
SO THAT I can plan my requests

Acceptance Criteria:
- Shows used/limit/remaining
- Shows subscription status
- Shows reset date
```

---

### Epic 4: Sync Service (M7)

**Description:** Background service để sync metrics.

**Functional Requirements:** FR-010, FR-011, FR-012, FR-013, FR-014

**Story Count Estimate:** 5 stories

**Priority:** Must Have

**User Stories:**

**E4-US01: Daily Sync Job**
```
AS TCB System
I WANT to sync metrics daily
SO THAT influencer data stays fresh

Acceptance Criteria:
- Runs at 4:00 AM
- Syncs all ACTIVE influencers
- Batches (50 per request)
- Logs results
```

**E4-US02: Freeze Logic**
```
AS TCB System
I WANT to freeze AT_SHARED when subscription expires
SO THAT we respect quota limits

Acceptance Criteria:
- Checks subscription before sync
- Freezes all AT_SHARED if expired
- Updates syncStatus and frozenAt
- TCB_PRIVATE unaffected
```

**E4-US03: Manual Sync Trigger**
```
AS TCB Admin
I WANT to trigger sync manually
SO THAT I can get fresh data immediately

Acceptance Criteria:
- API endpoint to trigger
- Returns job status
- Blocks if sync already running
```

**E4-US04: Webhook Handlers**
```
AS TCB System
I WANT to handle webhooks from AT
SO THAT I can receive real-time updates

Acceptance Criteria:
- Crawl complete webhook
- Validates signature
- Updates DB
- Idempotent
```

**E4-US05: Sync Log History**
```
AS TCB Admin
I WANT to see sync history
SO THAT I can monitor sync health

Acceptance Criteria:
- Lists past syncs
- Shows success/fail counts
- Can filter by type/status
```

---

### Epic 5: Admin UI (M6)

**Description:** Next.js Admin UI cho quản lý influencers.

**Functional Requirements:** FR-003, FR-004, FR-005, FR-007, FR-008, FR-009, FR-012

**Story Count Estimate:** 6 stories

**Priority:** Must Have

**User Stories:**

**E5-US01: Influencer List Page**
```
AS TCB Admin
I WANT to see a list of influencers
SO THAT I can browse my library

Acceptance Criteria:
- Table with key columns
- Filters sidebar
- Search input
- Pagination
- Responsive design
```

**E5-US02: Influencer Detail Page**
```
AS TCB Admin
I WANT to see influencer details
SO THAT I can review their profile

Acceptance Criteria:
- Profile header
- Metrics cards
- Score visualization
- Edit tags/notes
- Sync status indicator
```

**E5-US03: Add Private Influencer Form**
```
AS TCB Admin
I WANT to add an influencer by URL
SO THAT I can grow my library

Acceptance Criteria:
- URL input with validation
- Platform auto-detect
- Loading state
- Success/error feedback
```

**E5-US04: AT Pool Search Page**
```
AS TCB Admin
I WANT to search AT Pool
SO THAT I can find influencers to request

Acceptance Criteria:
- Search form with filters
- Results grid/table
- Select multiple
- Show quota status
```

**E5-US05: Request Confirmation Modal**
```
AS TCB Admin
I WANT to confirm before requesting
SO THAT I don't accidentally use quota

Acceptance Criteria:
- Shows selected influencers
- Shows quota impact
- Confirm/cancel buttons
- Success feedback
```

**E5-US06: Subscription Dashboard**
```
AS TCB Admin
I WANT to see my subscription status
SO THAT I can track usage

Acceptance Criteria:
- Tier display
- Quota progress bar
- Reset date
- Warning at 80%/100%
```

---

## 6. Data Models

### 6.1 Influencer

```prisma
model Influencer {
  id              String   @id @default(cuid())

  // Source tracking
  source          InfluencerSource
  atInfluencerId  String?  @unique
  vendorProfileId String?

  // Profile
  platform        Platform
  username        String
  displayName     String?
  avatarUrl       String?
  bio             String?

  // Metrics
  followers       Int      @default(0)
  following       Int      @default(0)
  engagement      Float    @default(0)
  avgViews        Int      @default(0)

  // Score
  score           Int      @default(0)
  scoreBreakdown  Json?

  // Contact (only for approved AT_SHARED)
  contactInfo     Json?

  // Sync
  syncStatus      SyncStatus @default(ACTIVE)
  syncedAt        DateTime?
  frozenAt        DateTime?

  // TCB-specific
  tags            String[]
  notes           String?

  // Timestamps
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  @@unique([platform, username])
  @@index([source])
  @@index([syncStatus])
  @@index([platform])
  @@index([score])
}

enum InfluencerSource {
  TCB_PRIVATE
  AT_SHARED
}

enum Platform {
  TIKTOK
  YOUTUBE
  INSTAGRAM
  FACEBOOK
}

enum SyncStatus {
  ACTIVE
  FROZEN
  DELETED
}
```

### 6.2 SyncLog

```prisma
model SyncLog {
  id            String        @id @default(cuid())
  type          SyncType
  status        SyncLogStatus

  // Stats
  totalCount    Int           @default(0)
  successCount  Int           @default(0)
  failedCount   Int           @default(0)

  // Timing
  startedAt     DateTime
  completedAt   DateTime?
  durationMs    Int?

  // Error
  error         String?
  failedIds     String[]

  @@index([type])
  @@index([status])
  @@index([startedAt])
}

enum SyncType {
  DAILY_FULL
  MANUAL
  WEBHOOK
}

enum SyncLogStatus {
  RUNNING
  COMPLETED
  FAILED
}
```

---

## 7. API Specification Summary

### 7.1 Influencer Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/influencers` | List influencers |
| GET | `/api/v1/influencers/:id` | Get influencer detail |
| POST | `/api/v1/influencers` | Add private influencer |
| PATCH | `/api/v1/influencers/:id` | Update tags/notes |
| DELETE | `/api/v1/influencers/:id` | Delete private influencer |

### 7.2 AT Pool Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/at-influencers/search` | Search AT Pool |
| POST | `/api/v1/at-influencers/request` | Request influencers |
| GET | `/api/v1/at-influencers/quota` | Get quota status |

### 7.3 Sync Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/sync/trigger` | Trigger manual sync |
| GET | `/api/v1/sync/status` | Get sync status |
| GET | `/api/v1/sync/logs` | Get sync history |

### 7.4 Webhook Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/webhooks/crawl-complete` | Crawl complete callback |
| POST | `/api/v1/webhooks/at-sync` | AT sync update |

---

## 8. Integration Points

### 8.1 Upstream Dependencies

```
TCB API
    │
    ├── AT Partner API (via HTTPS)
    │   ├── POST /profiles/enrich
    │   ├── POST /profiles/batch-refresh
    │   ├── GET /partners/pool/search
    │   ├── POST /partners/pool/request
    │   ├── GET /partners/quota
    │   └── GET /partners/subscription
    │
    └── TCB Internal Systems
        ├── SSO (Authentication)
        └── Secrets Manager (API credentials)
```

### 8.2 AT API Client Configuration

```typescript
interface ATClientConfig {
  baseUrl: string           // https://api.accesstrade.vn/influencer-service
  partnerId: string         // 'techcombank'
  apiKey: string            // From secrets manager
  timeout: number           // 30000ms
  retries: number           // 3
}
```

---

## 9. Acceptance Criteria Summary

### 9.1 Must Have (P0)
- [ ] Add private influencer via URL
- [ ] List influencers with filters
- [ ] View influencer detail
- [ ] Search AT Pool
- [ ] Request influencers from AT Pool
- [ ] View quota status
- [ ] Daily metrics sync
- [ ] Freeze logic when expired

### 9.2 Should Have (P1)
- [ ] Update tags/notes
- [ ] Delete private influencer
- [ ] Manual sync trigger
- [ ] Webhook handlers
- [ ] Sync status display

### 9.3 Could Have (P2)
- [ ] Sync log history
- [ ] Export influencer list
- [ ] Bulk tag update
- [ ] Usage analytics

---

## 10. Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| AT API không ready | High | Medium | Mock AT API, parallel development |
| Sync race conditions | High | Medium | Idempotent design, distributed locks |
| Quota calculation mismatch | Medium | Low | Verify với AT response, audit logging |
| Data inconsistency | High | Low | Transactional operations, sync logs |
| Subscription status stale | Medium | Medium | Check before every AT call |

---

## 11. Timeline & Milestones

### Phase 1: Foundation (Week 3-4)
- [ ] M4: TCB Database schema + migrations
- [ ] M5: Basic influencer CRUD endpoints
- [ ] M5: AT API client setup

### Phase 2: AT Integration (Week 5-6)
- [ ] M5: AT Pool search/request endpoints
- [ ] M5: Quota integration
- [ ] M7: Daily sync job

### Phase 3: Admin UI (Week 7-8)
- [ ] M6: Influencer list page
- [ ] M6: Add private form
- [ ] M6: AT Pool search/request flow
- [ ] M6: Subscription dashboard

### Phase 4: Polish (Week 9)
- [ ] M7: Freeze logic
- [ ] M7: Manual sync trigger
- [ ] Integration testing
- [ ] Documentation

---

## 12. Appendix

### A. Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_URL` | 400 | Invalid social platform URL |
| `DUPLICATE_INFLUENCER` | 409 | Influencer already exists |
| `CANNOT_DELETE_SHARED` | 403 | Cannot delete AT_SHARED |
| `QUOTA_EXCEEDED` | 403 | Monthly quota exceeded |
| `SUBSCRIPTION_EXPIRED` | 403 | Subscription expired |
| `AT_API_ERROR` | 502 | AT API returned error |
| `CRAWL_FAILED` | 502 | Profile crawl failed |
| `SYNC_IN_PROGRESS` | 409 | Sync already running |

### B. Subscription Tier Features

| Feature | FREE | BASIC | PREMIUM | ENTERPRISE |
|---------|------|-------|---------|------------|
| Monthly Quota | 10 | 50 | 200 | Unlimited |
| Add Private | ✅ | ✅ | ✅ | ✅ |
| Daily Sync | ✅ | ✅ | ✅ | ✅ |
| Manual Sync | ❌ | ✅ | ✅ | ✅ |
| Webhooks | ❌ | ✅ | ✅ | ✅ |
| Priority Support | ❌ | ❌ | ✅ | ✅ |

### C. Traceability Matrix

| Epic | FRs | Story Estimate |
|------|-----|----------------|
| E1: Database Setup | FR-001 | 3 stories |
| E2: Influencer CRUD | FR-002, FR-003, FR-004, FR-005, FR-006 | 5 stories |
| E3: AT Pool Integration | FR-007, FR-008, FR-009 | 4 stories |
| E4: Sync Service | FR-010, FR-011, FR-012, FR-013, FR-014 | 5 stories |
| E5: Admin UI | FR-003, FR-004, FR-005, FR-007, FR-008, FR-009, FR-012 | 6 stories |

**Total: 5 Epics, 23 Stories**

---

**Document Status:** Draft
**Next Review Date:** TBD
**Approved By:** Pending

---

*Generated by BMAD Method v6 - Product Manager Workflow*
