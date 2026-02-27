# Architecture Document: Techcombank Influencer Library

**Project:** Influencer Library & Matching System
**Client:** Techcombank (TCB)
**Document Version:** 1.0
**Date:** 2026-02-13
**Status:** Draft for Review
**Architect:** System Architect

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-13 | System Architect | Initial architecture design |

---

## Table of Contents

1. [Architectural Drivers](#architectural-drivers)
2. [High-Level Architecture](#high-level-architecture)
3. [Technology Stack](#technology-stack)
4. [System Components](#system-components)
5. [Data Architecture](#data-architecture)
6. [API Design](#api-design)
7. [NFR Coverage](#nfr-coverage)
8. [Security Architecture](#security-architecture)
9. [Scalability & Performance](#scalability--performance)
10. [Reliability & Availability](#reliability--availability)
11. [Development & Deployment](#development--deployment)
12. [Traceability Matrix](#traceability-matrix)

---

## Architectural Drivers

Architectural drivers là các requirements ảnh hưởng lớn đến architectural decisions.

### Driver 1: Multi-Tenancy & Security

**NFRs:** NFR-003 (Encryption), NFR-004 (Authentication & Authorization)

**Requirements:**
- Data encryption at-rest và in-transit
- RBAC với roles: Influencer, Brand, Admin
- eKYC integration (National ID + selfie)
- Tenant isolation (TCB data ≠ Vinfast data)

**Architectural Impact:**
- **3-Tier Architecture REQUIRED:** TCB Portal → AT Core Middleware → Vendor Service
- AT Core provides tenant isolation, ID mapping, API key management
- TCB CANNOT call Vendor directly (security risk, no tenant control)

**Solution:**
- JWT-based authentication
- TLS 1.3 for all API calls
- Database encryption (PostgreSQL + MongoDB encryption at-rest)
- AT Core middleware enforces tenant_id filtering

---

### Driver 2: Performance (<2s page load, <300ms API)

**NFR:** NFR-001 (Performance)

**Requirements:**
- Influencer portal page load <2s
- API response time <300ms (p95)
- Mobile-first (80% mobile usage)

**Architectural Impact:**
- CDN for static assets
- Redis caching layer
- Database indexing strategy
- Connection pooling
- Image optimization (lazy loading, WebP format)

**Solution:**
- CloudFront CDN for React SPA
- Redis cache với TTL: 5 min (user data), 1 hour (static)
- PostgreSQL indexes on: email, national_id, social_account_handle
- Database connection pool: min 10, max 50

---

### Driver 3: Scalability (100K influencers, 10K concurrent)

**NFR:** NFR-005 (Scalability)

**Requirements:**
- Support 100K influencers long-term
- 10K concurrent users
- Grow from 200 (3 months) → 500 (6 months) → 100K

**Architectural Impact:**
- Horizontal scaling (add more API instances)
- Load balancer
- Database read replicas
- Async job processing (background jobs)

**Solution:**
- AWS ECS with auto-scaling (2-10 instances)
- Application Load Balancer (ALB)
- PostgreSQL primary + 2 read replicas
- Bull Queue (Redis-backed) for async jobs

---

### Driver 4: Multi-Profile Data Model

**FRs:** FR-002 (Multi-Profile Support), FR-003 (Tier 1/2/3 Data)

**Requirements:**
- 1 Influencer → Many Profiles (Instagram, TikTok, Facebook, etc.)
- Personal data asked ONCE (name, DOB, bank account)
- Profile-specific data per social account (handle, followers, pricing)

**Architectural Impact:**
- Normalized database schema: `influencers` table + `social_profiles` table
- API design: `/influencers/{id}/profiles` endpoints
- UI component architecture: Shared personal form + Per-profile forms

**Solution:**
```sql
-- influencers table (person-level, 1 record per person)
CREATE TABLE influencers (
  id UUID PRIMARY KEY,
  full_name VARCHAR(255),
  dob DATE,
  national_id VARCHAR(20) UNIQUE,
  bank_account VARCHAR(50),
  ekyc_status VARCHAR(50)
);

-- social_profiles table (account-level, many per influencer)
CREATE TABLE social_profiles (
  id UUID PRIMARY KEY,
  influencer_id UUID REFERENCES influencers(id),
  platform VARCHAR(20), -- 'instagram', 'tiktok', 'facebook'
  account_handle VARCHAR(255),
  follower_count BIGINT,
  engagement_rate DECIMAL(5,2),
  is_primary BOOLEAN DEFAULT false
);
```

---

### Driver 5: 4 Data Sources Integration

**FRs:** FR-016 (Vendor API Integration), FR-017 (AT Core Middleware), FR-018 (Data Push)

**Requirements:**
- **Source 1:** Influencer onboarding form (self-reported)
- **Source 2:** Social media crawl (Vendor auto-fetches)
- **Source 3:** Campaign performance (TCB pushes after campaign)
- **Source 4:** Brand ratings (TCB pushes after review)

**Architectural Impact:**
- AT Core middleware as integration layer
- ID mapping service (tcb_influencer_id ↔ vendor_influencer_id)
- Push API for TCB → AT Core → Vendor
- Pull API for TCB ← AT Core ← Vendor

**Solution:**
- AT Core exposes: POST `/tenants/tcb/influencers/performance`, POST `/tenants/tcb/influencers/ratings`
- Vendor receives data with tenant_id context
- Matching algorithm uses all 4 sources to calculate Overall Quality Score

---

## High-Level Architecture

### Architecture Pattern

**Pattern:** Modular Monolith với 3-Tier Integration Architecture

**Rationale:**
- **Modular Monolith** cho TCB Portal (simpler deployment, clear module boundaries, small team)
- **3-Tier Integration** cho cross-system communication (TCB → AT Core → Vendor)
- **NOT Microservices** (overkill cho Level 3 project, single tenant, small team)

---

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  TIER 1: TCB PORTAL                          │
│                                                              │
│  ┌─────────────────┐      ┌──────────────────┐             │
│  │ Influencer      │      │  Brand Portal    │             │
│  │ Portal (React)  │      │  (React)         │             │
│  └────────┬────────┘      └────────┬─────────┘             │
│           │                        │                        │
│           └───────────┬────────────┘                        │
│                       │                                     │
│           ┌───────────▼──────────┐                         │
│           │   API Gateway        │ (NestJS)                │
│           │   Auth, Rate Limit   │                         │
│           └───────────┬──────────┘                         │
│                       │                                     │
│     ┌─────────────────┼─────────────────┐                 │
│     │                 │                 │                  │
│ ┌───▼────────┐  ┌────▼────────┐  ┌────▼─────┐            │
│ │ Influencer │  │  Campaign   │  │  Admin   │            │
│ │  Module    │  │   Module    │  │  Module  │            │
│ └───┬────────┘  └────┬────────┘  └────┬─────┘            │
│     └─────────────────┼─────────────────┘                 │
│                       │                                     │
│           ┌───────────▼──────────┐                         │
│           │ Data Access Layer    │ (TypeORM)               │
│           └───────────┬──────────┘                         │
│                       │                                     │
│           ┌───────────▼──────────┐                         │
│           │   PostgreSQL DB      │                         │
│           │   + Redis Cache      │                         │
│           └──────────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                        │
                        │ HTTPS (TLS 1.3)
                        │
┌───────────────────────▼─────────────────────────────────────┐
│            TIER 2: AT CORE MIDDLEWARE                        │
│            (AccessTrade Multi-Tenant Platform)               │
│                                                              │
│  ┌──────────────────────────────────────────┐              │
│  │      AT Core API Layer (Node.js)         │              │
│  └──┬────────────────────────────────────┬──┘              │
│     │                                    │                  │
│ ┌───▼──────────┐           ┌────────────▼────┐            │
│ │ ID Mapping   │           │  Tenant Config  │            │
│ │   Service    │           │     Service     │            │
│ └───┬──────────┘           └────────────┬────┘            │
│     │                                    │                  │
│ ┌───▼────────────────────────────────┬──▼────┐            │
│ │   AT Core PostgreSQL               │ Redis │            │
│ │   (tenant_mappings, api_keys)      │ Cache │            │
│ └────────────────────────────────────┴───────┘            │
└─────────────────────────────────────────────────────────────┘
                        │
                        │ HTTPS (TLS 1.3)
                        │
┌───────────────────────▼─────────────────────────────────────┐
│     TIER 3: VENDOR SERVICE (External Influence-Meter)        │
│                                                              │
│  ┌──────────────────────────────────────────┐              │
│  │    Influence-Meter API (Node.js)         │              │
│  └──┬────────────────────────────────────┬──┘              │
│     │                                    │                  │
│ ┌───▼─────────┐  ┌──────────────┐  ┌───▼──────────┐       │
│ │  Matching   │  │    Social    │  │   Scoring    │       │
│ │   Engine    │  │   Crawler    │  │   Engine     │       │
│ └─────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
│  ┌──────────────────────────────────────────┐              │
│  │         MongoDB (multi-tenant)           │              │
│  │    (influencer_data, social_metrics)     │              │
│  └──────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

---

### Data Flow Examples

#### Flow 1: Influencer Registration (TCB → AT Core → Vendor)

```
1. Influencer submits Tier 1 form
   → TCB API Gateway receives POST /api/v1/influencers

2. TCB validates data + saves to TCB PostgreSQL
   → influencers table, social_profiles table

3. TCB calls AT Core
   → POST /tenants/tcb/influencers
   → Body: { full_name, dob, national_id, social_profiles: [...] }

4. AT Core creates ID mapping
   → tcb_influencer_id (UUID from TCB)
   → vendor_influencer_id (UUID from Vendor)
   → Saves to tenant_mappings table

5. AT Core calls Vendor API
   → POST /api/v1/influencers
   → Headers: { X-Tenant-ID: tcb }
   → Body: { influencer data }

6. Vendor saves to MongoDB with tenant_id=tcb
   → Returns vendor_influencer_id

7. Success response flows back
   → Vendor → AT Core → TCB → UI shows "Registration complete"
```

---

#### Flow 2: Social Metrics Auto-Fetch (Vendor crawl)

```
1. Influencer links Instagram account
   → TCB receives instagram_handle

2. TCB calls AT Core
   → POST /tenants/tcb/profiles/{profile_id}/crawl
   → Body: { platform: 'instagram', handle: '@beauty_queen' }

3. AT Core resolves vendor_profile_id from ID mapping

4. AT Core calls Vendor Social Crawler
   → POST /api/v1/crawl/instagram
   → Body: { handle: '@beauty_queen', tenant_id: 'tcb' }

5. Vendor crawls Instagram
   → Fetches: follower_count, engagement_rate, avg_likes, posts_per_week
   → Saves to MongoDB

6. Vendor returns metrics
   → { follower_count: 500000, engagement_rate: 3.5, ... }

7. AT Core → TCB → UI displays
   → "We detected 500K followers. Is this correct?"
```

---

#### Flow 3: Brand Search Influencers (Matching)

```
1. Brand searches influencers
   → TCB receives: { categories: ['finance'], age: '25-35', min_followers: 100000 }

2. TCB calls AT Core
   → GET /tenants/tcb/influencers/search?categories=finance&age=25-35&min_followers=100000

3. AT Core calls Vendor Matching Engine
   → POST /api/v1/match
   → Body: { tenant_id: 'tcb', filters: {...}, scoring_weights: {...} }

4. Vendor runs matching algorithm
   → Calculates Overall Quality Score from 4 sources:
     - Source 1: Onboarding data (finance affinity score)
     - Source 2: Social metrics (engagement rate, follower growth)
     - Source 3: Performance data (past campaign CTR/CVR)
     - Source 4: Brand ratings (avg rating from TCB marketers)
   → Returns top 50 matches sorted by score

5. AT Core maps vendor_ids → tcb_ids
   → Uses tenant_mappings table

6. TCB receives mapped results
   → UI displays influencer cards with scores
```

---

#### Flow 4: Performance Data Push (TCB → Vendor)

```
1. Campaign completes, TCB has performance data
   → CTR: 2.5%, CVR: 1.2%, Revenue: 500M VND

2. TCB calls AT Core
   → POST /tenants/tcb/influencers/{id}/performance
   → Body: { campaign_id, ctr, cvr, revenue, completion_date }

3. AT Core resolves vendor_influencer_id

4. AT Core pushes to Vendor
   → POST /api/v1/influencers/{vendor_id}/performance
   → Headers: { X-Tenant-ID: tcb }

5. Vendor updates MongoDB
   → Updates performance_history array
   → Recalculates Overall Quality Score

6. Success response → TCB
```

---

## Technology Stack

### Frontend (Influencer Portal + Brand Portal)

**Choice:** React 18 + TypeScript + Vite

**Rationale:**
- React: Component reusability, large ecosystem, team familiar
- TypeScript: Type safety reduces bugs (especially for complex forms)
- Vite: Fast dev server, faster builds than Webpack

**UI Library:** shadcn/ui + Radix UI + Tailwind CSS

**Rationale:**
- shadcn/ui: Production-ready components, accessible (WCAG 2.1 AA)
- Tailwind: Rapid UI development, consistent design system
- Addresses NFR-008 (Accessibility)

**State Management:** React Query (TanStack Query) + Zustand

**Rationale:**
- React Query: Server state management, caching, auto-refetch
- Zustand: Simple client state (UI state, form state)

**Form Handling:** React Hook Form + Zod validation

**Rationale:**
- React Hook Form: Performance (uncontrolled forms, minimal re-renders)
- Zod: Schema validation, type inference
- Critical for FR-003 (3-tier data collection with complex validation)

**Trade-offs:**
- ✅ Gain: Fast development, type-safe, good UX
- ❌ Lose: SPA SEO challenges (mitigated with React Helmet for meta tags)

---

### Backend (TCB Portal API)

**Choice:** NestJS (Node.js framework) + TypeScript

**Rationale:**
- NestJS: Modular architecture (aligns with Modular Monolith pattern)
- TypeScript: Type safety end-to-end (frontend + backend)
- Decorators: Clean API design (@Get, @Post, @UseGuards)
- Dependency Injection: Testable, maintainable

**ORM:** TypeORM

**Rationale:**
- TypeScript-first ORM
- Entity-based modeling (aligns with FR-002 multi-profile schema)
- Migration support

**Authentication:** Passport.js + JWT

**Rationale:**
- Passport.js: Proven, supports multiple strategies
- JWT: Stateless auth, scales horizontally
- Addresses NFR-004 (Authentication)

**Validation:** class-validator + class-transformer

**Rationale:**
- DTO-based validation
- Automatic type transformation
- Aligns with NestJS ecosystem

**Trade-offs:**
- ✅ Gain: Strong typing, modular, scalable
- ❌ Lose: Heavier than Express (but worth it for structure)

---

### Database (TCB Portal)

**Choice:** PostgreSQL 15

**Rationale:**
- Relational data model (influencers → social_profiles is 1:many)
- ACID transactions (critical for eKYC, payment data)
- JSON support (store flexible Tier 2/3 data as JSONB)
- Strong indexing (handles 100K influencers easily)

**Caching:** Redis 7

**Rationale:**
- In-memory cache (addresses NFR-001 <300ms API)
- Session storage (JWT blacklist for logout)
- Bull Queue backing (async jobs)

**Trade-offs:**
- ✅ Gain: Data integrity, ACID, powerful queries
- ❌ Lose: Less flexible than MongoDB (but not needed for TCB schema)

---

### AT Core Middleware

**Existing Stack:** Node.js + Express + PostgreSQL

**Our Integration:**
- Use existing AT Core APIs
- No architectural changes to AT Core
- TCB consumes AT Core as middleware

---

### Vendor Service (Influence-Meter)

**Existing Stack:** Node.js + MongoDB

**Our Integration:**
- Vendor API is external service
- TCB → AT Core → Vendor (never direct)
- Vendor handles multi-tenancy via tenant_id

---

### Infrastructure & DevOps

**Cloud Provider:** AWS

**Rationale:**
- TCB likely uses AWS (standard for banks)
- Mature services (ECS, RDS, ElastiCache, CloudFront)

**Compute:** AWS ECS (Elastic Container Service) + Fargate

**Rationale:**
- Containerized deployment (Docker)
- Serverless containers (no EC2 management)
- Auto-scaling (addresses NFR-005 scalability)

**Database:** AWS RDS PostgreSQL (Multi-AZ)

**Rationale:**
- Managed service (automated backups, patching)
- Multi-AZ for high availability (NFR-002: 99.5% uptime)

**Cache:** AWS ElastiCache Redis (Cluster mode)

**Rationale:**
- Managed Redis
- Automatic failover

**CDN:** AWS CloudFront

**Rationale:**
- Global edge locations (fast page load)
- Addresses NFR-001 (<2s page load)

**Load Balancer:** AWS Application Load Balancer (ALB)

**Rationale:**
- Layer 7 load balancing
- SSL termination
- Health checks

**CI/CD:** GitHub Actions

**Rationale:**
- Native GitHub integration
- YAML-based pipelines
- Free for private repos

**Monitoring:** AWS CloudWatch + Datadog

**Rationale:**
- CloudWatch: Infrastructure metrics (CPU, memory, disk)
- Datadog: APM (trace API calls, identify bottlenecks)

**Logging:** AWS CloudWatch Logs + ELK Stack (future)

**Rationale:**
- Centralized logging
- Structured logs (JSON format)
- Search/filter capabilities

---

## System Components

### Component 1: API Gateway

**Purpose:** Single entry point cho tất cả client requests

**Responsibilities:**
- Request routing đến modules (Influencer, Campaign, Admin)
- Authentication (JWT verification)
- Authorization (RBAC: check user roles)
- Rate limiting (prevent abuse)
- Request/response logging
- CORS handling

**Technology:** NestJS Guards + Interceptors

**Interfaces:**
- REST API (HTTPS, port 443)
- Endpoints: `/api/v1/*`

**Dependencies:**
- Redis (rate limit storage)
- PostgreSQL (user lookup for auth)

**FRs Addressed:** FR-001 (Account Creation), FR-007 (Search), FR-012 (Browse Campaigns)

---

### Component 2: Influencer Module

**Purpose:** Quản lý influencer registration, profiles, submissions

**Responsibilities:**
- Influencer registration (FR-001)
- Multi-profile management (FR-002)
- Tier 1/2/3 data collection (FR-003)
- Profile editing (FR-005)
- Submission management (FR-015)

**Sub-components:**
- InfluencerController: REST endpoints
- InfluencerService: Business logic
- InfluencerRepository: Database access (TypeORM)

**Database Tables:**
- `influencers` (person-level data)
- `social_profiles` (account-level data)
- `profile_tiers` (Tier 1/2/3 data as JSONB)
- `submissions` (campaign deliverables)

**Interfaces:**
- POST `/api/v1/influencers` - Register
- GET `/api/v1/influencers/{id}` - Get profile
- PATCH `/api/v1/influencers/{id}` - Update profile
- POST `/api/v1/influencers/{id}/profiles` - Add social profile
- GET `/api/v1/influencers/{id}/submissions` - List submissions

**Dependencies:**
- AT Core API (push data to Vendor)
- eKYC Service (National ID verification)
- Email Service (OTP)
- SMS Service (OTP)

**FRs Addressed:** FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-015

---

### Component 3: Campaign Module

**Purpose:** Brand portal campaign browsing, influencer discovery

**Responsibilities:**
- Campaign listing (FR-012)
- Influencer search/filter (FR-007, FR-008, FR-009)
- Influencer comparison (FR-010)
- Saved searches (FR-011)
- Campaign application (FR-013)
- Brief viewing (FR-014)

**Sub-components:**
- CampaignController
- CampaignService
- SearchService (integration với AT Core → Vendor Matching)

**Database Tables:**
- `campaigns` (campaign metadata)
- `campaign_applications` (influencer applications)
- `saved_searches` (brand saved filters)

**Interfaces:**
- GET `/api/v1/campaigns` - List campaigns
- GET `/api/v1/campaigns/{id}` - Get campaign detail
- POST `/api/v1/campaigns/{id}/apply` - Apply to campaign
- GET `/api/v1/search/influencers` - Search (calls AT Core)
- POST `/api/v1/search/save` - Save search

**Dependencies:**
- AT Core API (search/matching)
- Vendor API (via AT Core)

**FRs Addressed:** FR-007, FR-008, FR-009, FR-010, FR-011, FR-012, FR-013, FR-014

---

### Component 4: Admin Module

**Purpose:** System admin approvals, user management

**Responsibilities:**
- Influencer approval workflow (FR-020)
- eKYC verification (FR-021)
- Compliance checks (FR-022)
- User role management (RBAC)
- System monitoring

**Sub-components:**
- AdminController
- ApprovalService
- eKYCService

**Database Tables:**
- `users` (admin accounts)
- `roles` (role definitions)
- `permissions` (RBAC permissions)
- `approval_queue` (pending approvals)
- `audit_logs` (compliance trail)

**Interfaces:**
- GET `/api/v1/admin/approvals` - Approval queue
- POST `/api/v1/admin/approvals/{id}/approve` - Approve influencer
- POST `/api/v1/admin/approvals/{id}/reject` - Reject
- GET `/api/v1/admin/audit-logs` - Audit trail

**Dependencies:**
- eKYC Service (National ID verification API)
- Email Service (notification emails)

**FRs Addressed:** FR-020, FR-021, FR-022

---

### Component 5: Data Integration Layer

**Purpose:** Integrate với AT Core và Vendor services

**Responsibilities:**
- Push influencer data (Source 1: Onboarding)
- Trigger social crawl (Source 2: Metrics)
- Push performance data (Source 3: Campaign results)
- Push brand ratings (Source 4: Reviews)
- Pull matched influencers (search results)

**Sub-components:**
- ATCoreClient (HTTP client for AT Core API)
- DataSyncService (orchestrates push/pull)
- IDMappingCache (Redis cache cho ID mappings)

**Technology:**
- Axios (HTTP client)
- Bull Queue (async jobs for data push)

**Interfaces:**
- Internal service (no REST endpoints, called by other modules)

**Dependencies:**
- AT Core API
- Vendor API (via AT Core)
- Redis (caching)
- Bull Queue (job processing)

**FRs Addressed:** FR-016, FR-017, FR-018, FR-019

---

### Component 6: Authentication & Authorization Service

**Purpose:** User authentication, role-based access control

**Responsibilities:**
- User login (email + password)
- JWT token generation
- Token validation
- Role assignment (Influencer, Brand, Admin)
- Permission checks

**Sub-components:**
- AuthController
- AuthService
- JwtStrategy (Passport.js)
- RoleGuard (NestJS guard)

**Database Tables:**
- `users` (credentials, hashed passwords)
- `roles`
- `permissions`

**Interfaces:**
- POST `/api/v1/auth/register` - Register user
- POST `/api/v1/auth/login` - Login (returns JWT)
- POST `/api/v1/auth/logout` - Logout (blacklist JWT)
- POST `/api/v1/auth/refresh` - Refresh token

**Dependencies:**
- Redis (JWT blacklist for logout)
- bcrypt (password hashing)

**FRs Addressed:** FR-001 (Registration), NFR-004 (Authentication)

---

### Component 7: Notification Service

**Purpose:** Send emails, SMS notifications

**Responsibilities:**
- Email OTP (registration, email change)
- SMS OTP (phone verification)
- Campaign notifications (new campaign, application status)
- System notifications (approval status)

**Technology:**
- AWS SES (email)
- Twilio (SMS)
- Bull Queue (async job processing)

**Interfaces:**
- Internal service (no REST endpoints)

**Dependencies:**
- AWS SES API
- Twilio API
- Bull Queue

---

### Component 8: File Upload Service

**Purpose:** Handle file uploads (National ID, selfie, portfolio images)

**Responsibilities:**
- Upload validation (file type, size)
- Image compression (reduce storage cost)
- S3 storage
- CDN URL generation

**Technology:**
- AWS S3 (storage)
- Sharp (image processing)
- Multer (file upload middleware)

**Interfaces:**
- POST `/api/v1/upload/image` - Upload image
- POST `/api/v1/upload/document` - Upload document (National ID)

**Dependencies:**
- AWS S3
- CloudFront (CDN)

**FRs Addressed:** FR-001 (eKYC upload), FR-003 (Portfolio upload)

---

## Data Architecture

### Database Schema (TCB PostgreSQL)

#### Table: influencers (Person-level data)

```sql
CREATE TABLE influencers (
  -- Primary Key
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Personal Info (Tier 1)
  full_name VARCHAR(255) NOT NULL,
  display_name VARCHAR(255),
  dob DATE NOT NULL CHECK (dob <= CURRENT_DATE - INTERVAL '18 years'), -- Age 18+
  gender VARCHAR(20), -- 'male', 'female', 'other', 'prefer_not_to_say'

  -- Contact (Tier 1)
  email VARCHAR(255) NOT NULL UNIQUE,
  email_verified BOOLEAN DEFAULT false,
  phone VARCHAR(20) NOT NULL UNIQUE,
  phone_verified BOOLEAN DEFAULT false,

  -- Location (Tier 1)
  city VARCHAR(100),
  country VARCHAR(100) DEFAULT 'Vietnam',

  -- Identity & Compliance (Tier 1)
  national_id VARCHAR(20) NOT NULL UNIQUE,
  ekyc_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'verified', 'failed', 'expired'
  ekyc_verified_at TIMESTAMP,
  national_id_image_url TEXT, -- S3 URL
  selfie_image_url TEXT, -- S3 URL

  -- Financial (Tier 1)
  bank_account_number VARCHAR(50) NOT NULL,
  bank_name VARCHAR(100) NOT NULL,
  bank_branch VARCHAR(100),

  -- TCB Relationship (Tier 1)
  is_tcb_customer BOOLEAN DEFAULT false,
  interested_in_finance BOOLEAN DEFAULT false,

  -- Profile Completion
  profile_completion_pct INTEGER DEFAULT 0 CHECK (profile_completion_pct >= 0 AND profile_completion_pct <= 100),
  tier_1_completed BOOLEAN DEFAULT false,
  tier_2_completed BOOLEAN DEFAULT false,
  tier_3_completed BOOLEAN DEFAULT false,

  -- Status
  status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'active', 'suspended', 'deleted'
  approval_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
  approved_by UUID REFERENCES users(id),
  approved_at TIMESTAMP,
  rejection_reason TEXT,

  -- Metadata
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP, -- Soft delete

  -- Indexes
  CONSTRAINT age_check CHECK (EXTRACT(YEAR FROM AGE(dob)) >= 18)
);

CREATE INDEX idx_influencers_email ON influencers(email);
CREATE INDEX idx_influencers_national_id ON influencers(national_id);
CREATE INDEX idx_influencers_status ON influencers(status);
CREATE INDEX idx_influencers_approval_status ON influencers(approval_status);
```

---

#### Table: social_profiles (Account-level data)

```sql
CREATE TABLE social_profiles (
  -- Primary Key
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  influencer_id UUID NOT NULL REFERENCES influencers(id) ON DELETE CASCADE,

  -- Platform Info (Tier 1)
  platform VARCHAR(20) NOT NULL, -- 'instagram', 'facebook', 'tiktok', 'youtube', 'linkedin'
  account_handle VARCHAR(255) NOT NULL, -- '@beauty_queen' or full URL
  account_url TEXT,
  is_verified BOOLEAN DEFAULT false, -- Blue checkmark

  -- Verification
  verification_method VARCHAR(50), -- 'oauth', 'manual', 'pending'
  verified_at TIMESTAMP,

  -- Categories & Niche (Tier 1)
  primary_categories TEXT[], -- ['finance', 'beauty', 'lifestyle']
  niche_specialty VARCHAR(255), -- 'Credit card reviews', 'Personal finance for millennials'
  content_language VARCHAR(50) DEFAULT 'vietnamese', -- 'vietnamese', 'english', 'bilingual'

  -- Audience (Tier 1)
  target_audience_description TEXT, -- Free text

  -- Pricing (Tier 1)
  rate_min_vnd DECIMAL(15, 2), -- Min rate
  rate_max_vnd DECIMAL(15, 2), -- Max rate
  rate_negotiable BOOLEAN DEFAULT true,

  -- Portfolio (Tier 1)
  portfolio_links TEXT[], -- Array of URLs to best posts

  -- Social Metrics (Tier 2 - Auto-fetched from Vendor)
  follower_count BIGINT,
  following_count BIGINT,
  post_count INTEGER,
  engagement_rate DECIMAL(5, 2), -- 3.5 = 3.5%
  avg_likes INTEGER,
  avg_comments INTEGER,
  avg_shares INTEGER,
  posts_per_week DECIMAL(4, 1),
  account_created_date DATE,
  last_crawled_at TIMESTAMP, -- When Vendor last updated metrics

  -- Detailed Pricing (Tier 2)
  rate_per_post_vnd DECIMAL(15, 2),
  rate_per_story_vnd DECIMAL(15, 2),
  rate_per_video_vnd DECIMAL(15, 2),
  rate_per_reel_vnd DECIMAL(15, 2),

  -- Status
  is_primary BOOLEAN DEFAULT false, -- 1 primary profile per influencer
  status VARCHAR(50) DEFAULT 'active', -- 'active', 'paused', 'suspended', 'deleted'
  pause_reason VARCHAR(255),
  paused_until DATE,

  -- Metadata
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP, -- Soft delete

  -- Constraints
  CONSTRAINT unique_influencer_platform UNIQUE(influencer_id, platform, account_handle),
  CONSTRAINT one_primary_per_influencer UNIQUE(influencer_id, is_primary) WHERE is_primary = true
);

CREATE INDEX idx_social_profiles_influencer_id ON social_profiles(influencer_id);
CREATE INDEX idx_social_profiles_platform ON social_profiles(platform);
CREATE INDEX idx_social_profiles_handle ON social_profiles(account_handle);
CREATE INDEX idx_social_profiles_primary ON social_profiles(is_primary) WHERE is_primary = true;
```

---

#### Table: profile_tiers (JSONB for Tier 2/3 flexible data)

```sql
CREATE TABLE profile_tiers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id UUID NOT NULL REFERENCES social_profiles(id) ON DELETE CASCADE,
  tier_level INTEGER NOT NULL CHECK (tier_level IN (2, 3)), -- 2 or 3

  -- Flexible JSONB data
  data JSONB NOT NULL, -- Stores Tier 2/3 fields as JSON

  -- Metadata
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT unique_profile_tier UNIQUE(profile_id, tier_level)
);

CREATE INDEX idx_profile_tiers_profile_id ON profile_tiers(profile_id);
CREATE INDEX idx_profile_tiers_data_gin ON profile_tiers USING GIN(data); -- JSON index
```

**Example Tier 2 data:**
```json
{
  "audience_demographics": {
    "age_distribution": { "18-24": 30, "25-34": 45, "35-44": 20, "45+": 5 },
    "gender_distribution": { "male": 40, "female": 55, "other": 5 },
    "location_distribution": { "Hanoi": 35, "HCMC": 40, "Danang": 10, "Other": 15 }
  },
  "content_strategy": {
    "formats": ["photo", "video", "carousel"],
    "posting_frequency": "5-7 per week",
    "best_posting_time": "7-9 PM"
  },
  "finance_affinity": {
    "has_credit_card": true,
    "uses_banking_app": true,
    "investment_experience": "beginner",
    "financial_literacy_score": 75
  },
  "collaboration_preferences": {
    "min_lead_time_days": 7,
    "max_concurrent_campaigns": 3,
    "blackout_dates": ["2024-12-20 to 2024-12-31"]
  }
}
```

---

#### Table: campaigns

```sql
CREATE TABLE campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Campaign Info
  title VARCHAR(255) NOT NULL,
  description TEXT,
  brief_url TEXT, -- S3 URL to PDF brief

  -- TCB Product
  product_type VARCHAR(100), -- 'credit_card', 'savings_account', 'loan', 'investment'
  product_name VARCHAR(255),

  -- Targeting
  target_categories TEXT[], -- ['finance', 'lifestyle']
  min_followers BIGINT,
  target_age_range VARCHAR(50), -- '25-35'
  target_location TEXT[], -- ['Hanoi', 'HCMC']

  -- Timeline
  application_deadline DATE,
  content_submission_deadline DATE,
  campaign_start_date DATE,
  campaign_end_date DATE,

  -- Budget
  total_budget_vnd DECIMAL(15, 2),
  budget_per_influencer_vnd DECIMAL(15, 2),
  max_influencers INTEGER,

  -- Status
  status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'published', 'closed', 'completed'

  -- Metadata
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_deadline ON campaigns(application_deadline);
```

---

#### Table: campaign_applications

```sql
CREATE TABLE campaign_applications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id UUID NOT NULL REFERENCES campaigns(id),
  influencer_id UUID NOT NULL REFERENCES influencers(id),
  profile_id UUID NOT NULL REFERENCES social_profiles(id), -- Which profile applying

  -- Application Data
  cover_letter TEXT,
  proposed_content_plan TEXT,
  estimated_reach BIGINT,
  requested_rate_vnd DECIMAL(15, 2),

  -- Status
  status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'completed'
  reviewed_by UUID REFERENCES users(id),
  reviewed_at TIMESTAMP,
  rejection_reason TEXT,

  -- Metadata
  applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT unique_campaign_influencer UNIQUE(campaign_id, influencer_id)
);

CREATE INDEX idx_applications_campaign_id ON campaign_applications(campaign_id);
CREATE INDEX idx_applications_influencer_id ON campaign_applications(influencer_id);
CREATE INDEX idx_applications_status ON campaign_applications(status);
```

---

#### Table: submissions

```sql
CREATE TABLE submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  application_id UUID NOT NULL REFERENCES campaign_applications(id),

  -- Submission Data
  content_urls TEXT[], -- Array of post URLs
  screenshot_urls TEXT[], -- S3 URLs to screenshots
  analytics_report_url TEXT, -- S3 URL to PDF report
  notes TEXT,

  -- Performance Metrics (self-reported initially)
  impressions BIGINT,
  reach BIGINT,
  likes INTEGER,
  comments INTEGER,
  shares INTEGER,
  clicks INTEGER,

  -- Status
  status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'revision_needed'
  reviewed_by UUID REFERENCES users(id),
  reviewed_at TIMESTAMP,
  feedback TEXT,

  -- Metadata
  submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_submissions_application_id ON submissions(application_id);
CREATE INDEX idx_submissions_status ON submissions(status);
```

---

#### Table: performance_data (Source 3: Campaign Performance)

```sql
CREATE TABLE performance_data (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  influencer_id UUID NOT NULL REFERENCES influencers(id),
  campaign_id UUID NOT NULL REFERENCES campaigns(id),

  -- Performance Metrics (TCB pushes to Vendor after campaign)
  ctr DECIMAL(5, 2), -- Click-through rate %
  cvr DECIMAL(5, 2), -- Conversion rate %
  revenue_vnd DECIMAL(15, 2), -- Revenue generated
  roi DECIMAL(5, 2), -- Return on investment %

  -- Metadata
  completion_date DATE,
  pushed_to_vendor_at TIMESTAMP, -- When TCB pushed to AT Core → Vendor
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_performance_influencer_id ON performance_data(influencer_id);
CREATE INDEX idx_performance_campaign_id ON performance_data(campaign_id);
```

---

#### Table: brand_ratings (Source 4: Brand Ratings)

```sql
CREATE TABLE brand_ratings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  influencer_id UUID NOT NULL REFERENCES influencers(id),
  campaign_id UUID NOT NULL REFERENCES campaigns(id),

  -- Rating Data (TCB brand gives rating after campaign)
  rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5), -- 1-5 stars
  professionalism_score INTEGER CHECK (professionalism_score >= 1 AND professionalism_score <= 5),
  content_quality_score INTEGER CHECK (content_quality_score >= 1 AND content_quality_score <= 5),
  communication_score INTEGER CHECK (communication_score >= 1 AND communication_score <= 5),
  would_work_again BOOLEAN,

  -- Feedback
  review_text TEXT,

  -- Metadata
  rated_by UUID REFERENCES users(id), -- Brand user who rated
  rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  pushed_to_vendor_at TIMESTAMP -- When TCB pushed to AT Core → Vendor
);

CREATE INDEX idx_ratings_influencer_id ON brand_ratings(influencer_id);
CREATE INDEX idx_ratings_campaign_id ON brand_ratings(campaign_id);
```

---

### Data Flow Strategy

#### Write Path (Create/Update)

```
1. User action (e.g., Edit Profile)
   ↓
2. TCB API validates data
   ↓
3. Write to TCB PostgreSQL (primary source of truth for TCB)
   ↓
4. Push to AT Core via async job (Bull Queue)
   ↓
5. AT Core → Vendor API
   ↓
6. Vendor updates MongoDB
```

**Async Push:** Use Bull Queue to decouple write from external API calls
- Retry logic: Exponential backoff (3 retries max)
- If Vendor API fails → Log error, retry later
- TCB data remains consistent (PostgreSQL is source of truth)

---

#### Read Path (Search/Match)

```
1. Brand searches influencers
   ↓
2. TCB calls AT Core search API
   ↓
3. AT Core calls Vendor Matching Engine
   ↓
4. Vendor queries MongoDB (4 data sources) → Calculates scores
   ↓
5. Returns top matches → AT Core maps IDs
   ↓
6. TCB receives results → Cache in Redis (5 min TTL)
   ↓
7. Subsequent identical searches served from Redis cache
```

**Caching Strategy:**
- Cache key: `search:${hash(filters)}`
- TTL: 5 minutes (balance freshness vs performance)
- Cache invalidation: On influencer profile update

---

## API Design

### API Architecture

**Pattern:** RESTful API with versioning

**Versioning:** URL-based `/api/v1/*`

**Authentication:** JWT Bearer Token

**Request Format:** JSON

**Response Format:** JSON

**Error Format:** RFC 7807 Problem Details
```json
{
  "type": "https://tcb.influencer.vn/errors/validation-error",
  "title": "Validation Error",
  "status": 400,
  "detail": "Email already exists",
  "instance": "/api/v1/influencers",
  "errors": [
    { "field": "email", "message": "Email already registered" }
  ]
}
```

---

### Authentication Flow

#### Register
```
POST /api/v1/auth/register
Content-Type: application/json

Request:
{
  "email": "influencer@example.com",
  "password": "SecurePass123!",
  "phone": "+84901234567",
  "role": "influencer"
}

Response (201 Created):
{
  "user_id": "uuid-here",
  "email": "influencer@example.com",
  "email_verification_sent": true,
  "message": "Please check your email to verify your account"
}
```

#### Login
```
POST /api/v1/auth/login
Content-Type: application/json

Request:
{
  "email": "influencer@example.com",
  "password": "SecurePass123!"
}

Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "user": {
    "id": "uuid-here",
    "email": "influencer@example.com",
    "role": "influencer",
    "profile_completion": 45
  }
}
```

#### Refresh Token
```
POST /api/v1/auth/refresh
Content-Type: application/json

Request:
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600
}
```

---

### Influencer Endpoints

#### Create Influencer (Tier 1 Registration)
```
POST /api/v1/influencers
Authorization: Bearer {jwt_token}
Content-Type: application/json

Request:
{
  "full_name": "Nguyễn Văn Hoa",
  "display_name": "Beauty Queen",
  "dob": "1996-05-15",
  "gender": "female",
  "email": "hoa@example.com",
  "phone": "+84901234567",
  "city": "Hanoi",
  "national_id": "001096012345",
  "bank_account_number": "19038888888",
  "bank_name": "Techcombank",
  "is_tcb_customer": true,
  "interested_in_finance": true,
  "first_profile": {
    "platform": "instagram",
    "account_handle": "@beauty_queen",
    "primary_categories": ["beauty", "lifestyle", "finance"],
    "niche_specialty": "Beauty & Finance for Millennials",
    "content_language": "bilingual",
    "target_audience_description": "Women 25-35, urban, middle-income",
    "portfolio_links": [
      "https://instagram.com/p/abc123",
      "https://instagram.com/p/def456"
    ],
    "rate_min_vnd": 5000000,
    "rate_max_vnd": 15000000,
    "rate_negotiable": true
  }
}

Response (201 Created):
{
  "id": "uuid-influencer",
  "status": "pending_verification",
  "profile_completion_pct": 28,
  "next_steps": [
    "Verify email (OTP sent)",
    "Verify phone (OTP sent)",
    "Complete eKYC (upload National ID + selfie)",
    "Complete Tier 2 (optional, improves matching)"
  ],
  "first_profile_id": "uuid-profile"
}
```

#### Get Influencer Profile
```
GET /api/v1/influencers/{id}
Authorization: Bearer {jwt_token}

Response (200 OK):
{
  "id": "uuid-influencer",
  "full_name": "Nguyễn Văn Hoa",
  "display_name": "Beauty Queen",
  "email": "hoa@example.com",
  "profile_completion_pct": 75,
  "tier_1_completed": true,
  "tier_2_completed": true,
  "tier_3_completed": false,
  "status": "active",
  "approval_status": "approved",
  "ekyc_status": "verified",
  "profiles": [
    {
      "id": "uuid-profile-1",
      "platform": "instagram",
      "account_handle": "@beauty_queen",
      "follower_count": 500000,
      "engagement_rate": 3.5,
      "is_primary": true,
      "last_crawled_at": "2026-02-12T10:30:00Z"
    },
    {
      "id": "uuid-profile-2",
      "platform": "tiktok",
      "account_handle": "@beautyqueen_tiktok",
      "follower_count": 1000000,
      "engagement_rate": 5.2,
      "is_primary": false,
      "last_crawled_at": "2026-02-12T11:00:00Z"
    }
  ],
  "created_at": "2026-02-01T09:00:00Z",
  "updated_at": "2026-02-12T15:45:00Z"
}
```

#### Update Influencer Profile
```
PATCH /api/v1/influencers/{id}
Authorization: Bearer {jwt_token}
Content-Type: application/json

Request:
{
  "display_name": "Beauty Queen VN",
  "city": "Ho Chi Minh City",
  "interested_in_finance": true
}

Response (200 OK):
{
  "id": "uuid-influencer",
  "updated_fields": ["display_name", "city", "interested_in_finance"],
  "profile_completion_pct": 76,
  "message": "Profile updated successfully"
}
```

#### Add Social Profile
```
POST /api/v1/influencers/{influencer_id}/profiles
Authorization: Bearer {jwt_token}
Content-Type: application/json

Request:
{
  "platform": "tiktok",
  "account_handle": "@beautyqueen_tiktok",
  "account_url": "https://tiktok.com/@beautyqueen_tiktok",
  "primary_categories": ["beauty", "lifestyle"],
  "niche_specialty": "Short-form beauty tutorials",
  "portfolio_links": ["https://tiktok.com/@beautyqueen_tiktok/video/123"],
  "rate_min_vnd": 8000000,
  "rate_max_vnd": 20000000
}

Response (201 Created):
{
  "profile_id": "uuid-profile-2",
  "status": "pending_verification",
  "verification_method": "manual",
  "next_steps": [
    "We will crawl your TikTok metrics within 24 hours",
    "You can manually verify by uploading a screenshot"
  ]
}
```

#### Trigger Social Metrics Crawl
```
POST /api/v1/profiles/{profile_id}/crawl
Authorization: Bearer {jwt_token}

Response (202 Accepted):
{
  "job_id": "crawl-job-uuid",
  "status": "queued",
  "estimated_completion": "2026-02-13T10:00:00Z",
  "message": "Crawl job queued. Check back in 5-10 minutes."
}
```

---

### Campaign Endpoints

#### List Campaigns (Influencer View)
```
GET /api/v1/campaigns?status=published&page=1&limit=20
Authorization: Bearer {jwt_token}

Response (200 OK):
{
  "campaigns": [
    {
      "id": "uuid-campaign-1",
      "title": "TCB Credit Card Launch - Finance Influencers",
      "description": "Promote our new cashback credit card to young professionals",
      "product_type": "credit_card",
      "product_name": "TCB Cashback Platinum",
      "target_categories": ["finance", "lifestyle"],
      "min_followers": 100000,
      "budget_per_influencer_vnd": 10000000,
      "application_deadline": "2026-02-20",
      "content_submission_deadline": "2026-03-15",
      "match_score": 85,
      "match_reasons": [
        "Finance category match",
        "Follower count exceeds minimum",
        "High finance affinity score"
      ]
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "total_pages": 3
  }
}
```

#### Get Campaign Detail
```
GET /api/v1/campaigns/{id}
Authorization: Bearer {jwt_token}

Response (200 OK):
{
  "id": "uuid-campaign-1",
  "title": "TCB Credit Card Launch",
  "description": "...",
  "brief_url": "https://cdn.tcb.vn/briefs/campaign-1.pdf",
  "requirements": {
    "min_followers": 100000,
    "target_age_range": "25-35",
    "target_categories": ["finance", "lifestyle"],
    "content_types": ["instagram_post", "instagram_story"]
  },
  "deliverables": [
    "1 Instagram feed post",
    "3 Instagram stories",
    "Analytics report (impressions, clicks)"
  ],
  "budget_per_influencer_vnd": 10000000,
  "timeline": {
    "application_deadline": "2026-02-20",
    "content_submission_deadline": "2026-03-15",
    "campaign_start_date": "2026-03-01",
    "campaign_end_date": "2026-03-31"
  },
  "my_application_status": "not_applied"
}
```

#### Apply to Campaign
```
POST /api/v1/campaigns/{campaign_id}/apply
Authorization: Bearer {jwt_token}
Content-Type: application/json

Request:
{
  "profile_id": "uuid-profile-1",
  "cover_letter": "I am excited to promote TCB's credit card...",
  "proposed_content_plan": "I will create 1 feed post showcasing cashback benefits...",
  "estimated_reach": 450000,
  "requested_rate_vnd": 12000000
}

Response (201 Created):
{
  "application_id": "uuid-application",
  "status": "pending",
  "message": "Application submitted successfully. You will be notified within 3-5 business days."
}
```

---

### Search & Matching Endpoints (Brand View)

#### Search Influencers
```
GET /api/v1/search/influencers?categories=finance&min_followers=100000&age_range=25-35&location=Hanoi&page=1&limit=20
Authorization: Bearer {jwt_token}

Response (200 OK):
{
  "results": [
    {
      "influencer_id": "uuid-influencer-1",
      "display_name": "Finance Guru",
      "primary_profile": {
        "platform": "instagram",
        "account_handle": "@finance_guru",
        "follower_count": 300000,
        "engagement_rate": 4.2,
        "categories": ["finance", "investment"]
      },
      "match_score": 92,
      "score_breakdown": {
        "social_score": 28,
        "performance_score": 38,
        "ratings_score": 18,
        "completeness_score": 8
      },
      "finance_affinity_score": 88,
      "past_campaigns_count": 12,
      "avg_rating": 4.5
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 156,
    "total_pages": 8
  },
  "filters_applied": {
    "categories": ["finance"],
    "min_followers": 100000,
    "age_range": "25-35",
    "location": "Hanoi"
  }
}
```

**Note:** This endpoint calls AT Core → Vendor Matching Engine

---

### Admin Endpoints

#### Get Approval Queue
```
GET /api/v1/admin/approvals?status=pending&page=1&limit=20
Authorization: Bearer {jwt_token}
X-Role: admin

Response (200 OK):
{
  "approvals": [
    {
      "influencer_id": "uuid-influencer-1",
      "full_name": "Nguyễn Văn Hoa",
      "email": "hoa@example.com",
      "ekyc_status": "verified",
      "national_id": "001096012345",
      "national_id_image_url": "https://s3.../national-id.jpg",
      "selfie_image_url": "https://s3.../selfie.jpg",
      "submitted_at": "2026-02-12T10:00:00Z",
      "age": 28,
      "compliance_flags": []
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45
  }
}
```

#### Approve Influencer
```
POST /api/v1/admin/approvals/{influencer_id}/approve
Authorization: Bearer {jwt_token}
X-Role: admin

Response (200 OK):
{
  "influencer_id": "uuid-influencer-1",
  "approval_status": "approved",
  "message": "Influencer approved successfully. Email notification sent."
}
```

#### Reject Influencer
```
POST /api/v1/admin/approvals/{influencer_id}/reject
Authorization: Bearer {jwt_token}
X-Role: admin
Content-Type: application/json

Request:
{
  "reason": "eKYC verification failed - National ID does not match selfie"
}

Response (200 OK):
{
  "influencer_id": "uuid-influencer-1",
  "approval_status": "rejected",
  "message": "Influencer rejected. Email notification sent."
}
```

---

## NFR Coverage

Bây giờ tôi sẽ address từng NFR một cách systematic.

### NFR-001: Performance - Page Load Time

**Requirement:**
- Influencer portal page load <2s
- API response time <300ms (p95)

**Architecture Solution:**

**Frontend Performance:**
1. **Code Splitting:** React lazy loading cho routes
   ```typescript
   const InfluencerDashboard = lazy(() => import('./pages/InfluencerDashboard'));
   const CampaignList = lazy(() => import('./pages/CampaignList'));
   ```

2. **CDN:** AWS CloudFront serves static assets (JS, CSS, images)
   - Edge caching: TTL 1 year for versioned assets
   - Gzip/Brotli compression enabled

3. **Image Optimization:**
   - WebP format with JPEG fallback
   - Lazy loading với Intersection Observer
   - Responsive images: `srcset` for different screen sizes

4. **Bundle Size Optimization:**
   - Vite tree-shaking
   - Remove unused dependencies
   - Target bundle size: <300KB initial load

**Backend Performance:**

1. **Redis Caching:**
   - User profile cache: TTL 5 minutes
   - Search results cache: TTL 5 minutes
   - Campaign list cache: TTL 10 minutes

2. **Database Optimization:**
   - Indexes on frequently queried columns (email, national_id, platform+handle)
   - Connection pooling: min 10, max 50 connections
   - Read replicas for read-heavy operations (search, list campaigns)

3. **API Response Optimization:**
   - Pagination (limit 20 per page)
   - Field selection (only return requested fields)
   - Async operations (file upload, data push) → Background jobs

**Implementation Notes:**
- Monitor p95 response time with Datadog APM
- Set up CloudWatch alarms if p95 > 300ms
- Optimize slow queries identified in logs

**Validation:**
- Load testing: k6 or Artillery
- Target: 1000 RPS with <300ms p95
- Page load: Lighthouse score >90

---

### NFR-002: Availability - System Uptime

**Requirement:** 99.5% uptime (允許 43.8 hours downtime/year)

**Architecture Solution:**

**High Availability Design:**

1. **Multi-AZ Deployment:**
   - AWS ECS tasks across 2 AZs (ap-southeast-1a, ap-southeast-1b)
   - AWS RDS PostgreSQL Multi-AZ (automatic failover)
   - AWS ElastiCache Redis Cluster mode (multi-node)

2. **Load Balancer:**
   - AWS ALB health checks every 30 seconds
   - Unhealthy targets removed automatically
   - Cross-zone load balancing enabled

3. **Auto-Scaling:**
   - ECS auto-scaling: 2-10 tasks based on CPU (target 70%)
   - Scale-out: If CPU >70% for 2 minutes → Add 1 task
   - Scale-in: If CPU <30% for 5 minutes → Remove 1 task

4. **Database Redundancy:**
   - RDS Multi-AZ: Automatic failover <60 seconds
   - Read replicas (2) for read traffic
   - Automated backups: Daily snapshots, retained 7 days

**Monitoring & Alerting:**

1. **Health Checks:**
   - ALB health endpoint: `GET /health`
   - Returns 200 OK if database + Redis reachable
   - Timeout: 5 seconds

2. **Uptime Monitoring:**
   - AWS CloudWatch Synthetics (canary tests every 5 minutes)
   - PagerDuty alerts if downtime detected
   - Escalation: Dev team → Manager → CTO

**Disaster Recovery:**
- RTO (Recovery Time Objective): 1 hour
- RPO (Recovery Point Objective): 15 minutes (backup frequency)

**Implementation Notes:**
- Deploy during low-traffic windows (2-4 AM Vietnam time)
- Blue-green deployment strategy (zero downtime)
- Rollback plan if deployment fails

**Validation:**
- Monitor uptime with CloudWatch
- Monthly uptime report to stakeholders
- Post-mortem for any incidents >15 minutes downtime

---

### NFR-003: Security - Data Encryption

**Requirement:**
- Encryption at-rest (database, file storage)
- Encryption in-transit (TLS 1.3)
- Key management

**Architecture Solution:**

**Encryption at-rest:**

1. **Database:**
   - AWS RDS PostgreSQL encryption enabled (AES-256)
   - Managed by AWS KMS (Key Management Service)
   - Automatic key rotation annually

2. **File Storage:**
   - AWS S3 bucket encryption (SSE-S3)
   - National ID images, selfies, portfolio images encrypted
   - Bucket policy: Enforce encryption on upload

3. **Redis:**
   - ElastiCache encryption at-rest enabled
   - Encryption in-transit (TLS) enabled

**Encryption in-transit:**

1. **HTTPS Everywhere:**
   - ALB listens on port 443 only (HTTP 80 → 443 redirect)
   - TLS 1.3 (minimum TLS 1.2)
   - Certificate: AWS Certificate Manager (ACM)

2. **API Calls:**
   - TCB → AT Core: HTTPS (TLS 1.3)
   - AT Core → Vendor: HTTPS (TLS 1.3)
   - No plaintext HTTP allowed

**Key Management:**
- AWS KMS for encryption keys
- Separate keys per environment (dev, staging, prod)
- Key rotation: Annual automatic rotation
- Access: Only authorized IAM roles can use keys

**Implementation Notes:**
- Audit S3 bucket policies quarterly
- Monitor TLS versions with AWS Config
- Alert if TLS 1.0/1.1 detected (deprecated)

**Validation:**
- Security audit: Verify all data encrypted
- Penetration testing: Quarterly
- Compliance: GDPR, Vietnam Decree 13/2023

---

### NFR-004: Security - Authentication & Authorization

**Requirement:**
- JWT-based authentication
- RBAC (Role-Based Access Control)
- Secure password storage

**Architecture Solution:**

**Authentication:**

1. **JWT Tokens:**
   - Access token: 1 hour expiry
   - Refresh token: 7 days expiry
   - Algorithm: HS256 (HMAC SHA-256)
   - Secret: Stored in AWS Secrets Manager

2. **Token Storage:**
   - Access token: Frontend stores in memory (not localStorage)
   - Refresh token: HttpOnly cookie (prevents XSS)

3. **Password Security:**
   - bcrypt hashing (cost factor 12)
   - Salted hashes (unique per user)
   - Minimum password: 8 characters, 1 uppercase, 1 number, 1 special

**Authorization (RBAC):**

**Roles:**
- `influencer`: Access own profile, apply to campaigns
- `brand`: Search influencers, create campaigns, review submissions
- `admin`: Approve influencers, manage users, view audit logs

**Permissions:**
```typescript
const permissions = {
  influencer: [
    'profile:read:own',
    'profile:update:own',
    'campaigns:list',
    'campaigns:apply',
    'submissions:create:own'
  ],
  brand: [
    'influencers:search',
    'campaigns:create',
    'campaigns:update:own',
    'applications:review',
    'submissions:review'
  ],
  admin: [
    'influencers:approve',
    'users:manage',
    'audit-logs:read',
    '*:*' // All permissions
  ]
};
```

**Authorization Check:**
- NestJS Guards: `@UseGuards(JwtAuthGuard, RolesGuard)`
- Per-endpoint role check:
  ```typescript
  @Get('admin/approvals')
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles('admin')
  async getApprovals() { ... }
  ```

**Implementation Notes:**
- Logout: Blacklist JWT in Redis (TTL = token expiry)
- Token refresh: Automatic refresh 5 minutes before expiry
- MFA (Multi-Factor Auth): Future enhancement (not MVP)

**Validation:**
- Security testing: Attempt unauthorized access
- Audit: Review permissions quarterly
- Penetration testing: Annual

---

### NFR-005: Scalability - Concurrent Users

**Requirement:**
- Support 100K influencers (long-term)
- 10K concurrent users

**Architecture Solution:**

**Horizontal Scaling:**

1. **Application Layer:**
   - AWS ECS auto-scaling (2-10 tasks)
   - Stateless API (JWT auth, no server sessions)
   - Scale-out triggers:
     - CPU >70% for 2 minutes
     - Request count >1000/minute per task

2. **Database Layer:**
   - PostgreSQL read replicas (2)
   - Read traffic: Route to replicas
   - Write traffic: Route to primary
   - Connection pooling: TypeORM pool (max 50 connections per task)

3. **Caching Layer:**
   - Redis Cluster mode (3 shards, 6 nodes total)
   - Cache hit ratio target: >80%
   - Reduces database load

**Load Distribution:**
- AWS ALB distributes traffic across ECS tasks
- Sticky sessions: NOT used (stateless API)
- Health checks: Remove unhealthy tasks automatically

**Database Optimization:**
- Indexes on high-traffic queries
- Partitioning: Future enhancement if >1M influencers
- Query optimization: Avoid N+1 queries, use eager loading

**Implementation Notes:**
- Monitor concurrent users with CloudWatch metrics
- Load testing: Simulate 10K concurrent users
- Target: <300ms p95 response time under load

**Validation:**
- Load test: k6 script simulating 10K users
- Chaos engineering: Terminate random tasks, verify recovery
- Quarterly capacity planning

---

### NFR-006: Reliability - Error Handling & Graceful Degradation

**Requirement:**
- Graceful error handling
- Retry logic for external APIs
- Circuit breaker pattern

**Architecture Solution:**

**Error Handling:**

1. **API Error Responses:**
   - Consistent format (RFC 7807)
   - HTTP status codes: 400 (validation), 401 (auth), 403 (forbidden), 404 (not found), 500 (server error)
   - User-friendly messages (không expose stack traces)

2. **Logging:**
   - Structured JSON logs
   - Log levels: ERROR, WARN, INFO, DEBUG
   - Include: request_id, user_id, timestamp, error_stack

**Retry Logic:**

1. **External API Calls (AT Core, Vendor):**
   - Retry strategy: Exponential backoff
   - Max retries: 3
   - Backoff: 1s, 2s, 4s
   - Timeout: 10 seconds per request

2. **Bull Queue (Async Jobs):**
   - Job retry: 3 attempts
   - If failed after 3 attempts → Move to failed queue
   - Manual retry from admin panel

**Circuit Breaker:**
- Pattern: Prevent cascading failures
- Implementation: `opossum` library
- Thresholds:
  - Open circuit if 50% of requests fail in 1 minute
  - Half-open after 30 seconds
  - Close if 3 consecutive requests succeed

**Graceful Degradation:**

**Scenario 1: Vendor API down**
- Fallback: Serve cached search results (stale data OK for 30 minutes)
- User message: "Search results may not be up-to-date"

**Scenario 2: Redis cache down**
- Fallback: Direct database queries (slower but functional)
- Auto-scaling: Add more ECS tasks to handle load

**Scenario 3: Database read replica down**
- Fallback: Route reads to primary (performance degradation acceptable)
- Alert: PagerDuty notification to ops team

**Implementation Notes:**
- Monitor error rates with CloudWatch metrics
- Alert if error rate >1% for 5 minutes
- Post-mortem for all P0/P1 incidents

**Validation:**
- Chaos testing: Simulate Vendor API failures
- Verify circuit breaker opens/closes correctly
- Monitor retry success rate

---

### NFR-007: Maintainability - Code Quality & Documentation

**Requirement:**
- Code quality standards
- Comprehensive documentation
- Test coverage >80%

**Architecture Solution:**

**Code Quality:**

1. **Linting & Formatting:**
   - ESLint (TypeScript rules)
   - Prettier (code formatting)
   - Pre-commit hooks (Husky): Run lint + format before commit

2. **Code Review:**
   - All PRs require 1 approval
   - Automated checks: Lint, tests, build
   - PR template: Description, testing steps, screenshots (UI changes)

3. **Naming Conventions:**
   - Files: `kebab-case` (e.g., `influencer-service.ts`)
   - Classes: `PascalCase` (e.g., `InfluencerService`)
   - Functions: `camelCase` (e.g., `createInfluencer()`)
   - Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_ATTEMPTS`)

**Documentation:**

1. **API Documentation:**
   - OpenAPI (Swagger) spec auto-generated from NestJS decorators
   - Hosted at `/api/docs`
   - Examples for each endpoint

2. **Code Documentation:**
   - TSDoc comments for public methods
   - Explain WHY (not WHAT - code explains what)

3. **Architecture Documentation:**
   - This document (architecture-tcb-influencer-library-2026-02-13.md)
   - Database schema diagrams (dbdiagram.io)
   - Sequence diagrams for key flows (Mermaid)

**Testing:**

1. **Unit Tests:**
   - Framework: Jest
   - Coverage target: >80%
   - Test services, utilities, helpers

2. **Integration Tests:**
   - Test API endpoints (E2E)
   - Test database interactions
   - Framework: Supertest (NestJS)

3. **E2E Tests:**
   - Framework: Playwright
   - Test critical user flows (registration, campaign application)

**CI/CD Pipeline:**
```yaml
# GitHub Actions workflow
name: CI/CD
on: [push, pull_request]

jobs:
  test:
    - Run lint
    - Run unit tests
    - Run integration tests
    - Check coverage >80%

  build:
    - Build Docker image
    - Push to ECR

  deploy:
    - Deploy to ECS (staging)
    - Run smoke tests
    - Deploy to ECS (production) [manual approval]
```

**Implementation Notes:**
- Enforce test coverage with CI checks
- Quarterly code quality review
- Refactor technical debt regularly

**Validation:**
- SonarQube code quality metrics
- Test coverage reports
- Documentation review (quarterly)

---

### NFR-008: Usability - Accessibility (WCAG 2.1 AA)

**Requirement:** WCAG 2.1 AA compliance

**Architecture Solution:**

**Semantic HTML:**
- Use `<button>`, `<nav>`, `<main>`, `<article>` (not just `<div>`)
- Proper heading hierarchy (`<h1>` → `<h2>` → `<h3>`)

**Keyboard Navigation:**
- All interactive elements keyboard-accessible (Tab, Enter, Space)
- Focus indicators visible (blue outline)
- Skip to main content link

**Screen Reader Support:**
- ARIA labels for icon buttons
- Alt text for images
- Form labels associated with inputs

**Color Contrast:**
- Text contrast ratio ≥4.5:1 (normal text)
- Text contrast ratio ≥3:1 (large text >18pt)
- shadcn/ui components meet WCAG standards

**Form Accessibility:**
- Labels for all inputs
- Error messages associated with fields (aria-describedby)
- Required fields marked (aria-required)

**Implementation Notes:**
- Use axe DevTools for automated testing
- Manual testing with screen reader (NVDA, JAWS)
- Quarterly accessibility audit

**Validation:**
- axe-core automated tests in CI
- Lighthouse accessibility score >95
- Manual screen reader testing

---

### NFR-009: Compatibility - Browser & Device Support

**Requirement:**
- Modern browsers (Chrome, Safari, Firefox, Edge)
- Mobile-first (iOS, Android)
- Responsive design

**Architecture Solution:**

**Browser Support:**
- Chrome (last 2 versions)
- Safari (last 2 versions)
- Firefox (last 2 versions)
- Edge (last 2 versions)
- **NOT supported:** IE11 (deprecated)

**Responsive Design:**
- Mobile-first CSS (min-width media queries)
- Breakpoints: 640px (sm), 768px (md), 1024px (lg), 1280px (xl)
- Tailwind responsive utilities: `sm:`, `md:`, `lg:`

**Mobile Optimization:**
- Touch-friendly targets (min 44×44px)
- No hover-only interactions
- Optimized images for mobile (WebP, lazy loading)

**Progressive Enhancement:**
- Core functionality works without JavaScript (forms submit)
- Enhanced UX with JavaScript (client-side validation, auto-save)

**Testing:**
- BrowserStack for cross-browser testing
- Chrome DevTools device emulation
- Real device testing (iPhone, Android)

**Implementation Notes:**
- Polyfills for older browsers (if needed)
- Feature detection (not browser detection)

**Validation:**
- Cross-browser testing (quarterly)
- Mobile responsiveness check (every release)
- Lighthouse mobile score >90

---

### NFR-010: Data Retention & GDPR Compliance

**Requirement:**
- GDPR compliance
- Vietnam Decree 13/2023 (Personal Data Protection)
- Right to be forgotten

**Architecture Solution:**

**Data Retention Policy:**

1. **Active Users:**
   - Retain all data while account active
   - Quarterly reminder: "Update your profile"

2. **Inactive Users (>12 months no login):**
   - Email warning: "Your account will be deleted in 30 days"
   - After 30 days: Soft delete (set `deleted_at`)
   - After 90 days: Hard delete (anonymize personal data)

3. **Deleted Accounts:**
   - Anonymize PII: name → "Deleted User", email → "deleted-{uuid}@example.com"
   - Retain anonymized performance data (for analytics)

**GDPR Rights:**

1. **Right to Access:**
   - API endpoint: `GET /api/v1/influencers/{id}/data-export`
   - Returns JSON with all personal data

2. **Right to Rectification:**
   - Profile edit functionality (FR-005)

3. **Right to Erasure (Right to be Forgotten):**
   - API endpoint: `DELETE /api/v1/influencers/{id}`
   - Soft delete → Hard delete after 90 days
   - Email confirmation: "Your data will be permanently deleted in 90 days"

4. **Right to Data Portability:**
   - Export format: JSON
   - Includes: Profile data, submissions, performance data

**Data Processing Agreement:**
- TCB ↔ AT Core: DPA signed
- AT Core ↔ Vendor: DPA signed
- Vendor: GDPR-compliant data processing

**Audit Trail:**
- Log all data access (who, when, what)
- Retain audit logs: 7 years (compliance requirement)

**Implementation Notes:**
- Privacy policy: Clear, accessible
- Cookie consent banner (future enhancement)
- Annual GDPR compliance review

**Validation:**
- Data export: Verify all personal data included
- Right to erasure: Verify data deleted
- Audit logs: Review quarterly

---

## Security Architecture

### Defense in Depth

**Layer 1: Network Security**
- AWS VPC with private subnets
- Security groups: Whitelist only necessary ports (443, 5432, 6379)
- WAF (Web Application Firewall): Block common attacks (SQL injection, XSS)

**Layer 2: Application Security**
- Input validation (class-validator)
- Output encoding (prevent XSS)
- CSRF protection (SameSite cookies)
- Rate limiting (prevent DDoS)

**Layer 3: Data Security**
- Encryption at-rest (database, S3)
- Encryption in-transit (TLS 1.3)
- Key management (AWS KMS)

**Layer 4: Identity & Access**
- JWT authentication
- RBAC authorization
- MFA (future enhancement)

---

### Security Best Practices

**SQL Injection Prevention:**
- TypeORM parameterized queries (NO raw SQL)
- Example:
  ```typescript
  // ✅ SAFE
  await repo.findOne({ where: { email } });

  // ❌ UNSAFE (never do this)
  await repo.query(`SELECT * FROM users WHERE email = '${email}'`);
  ```

**XSS Prevention:**
- React auto-escapes output
- Sanitize user input on display (DOMPurify)
- CSP headers: `Content-Security-Policy: default-src 'self'`

**CSRF Protection:**
- SameSite cookies: `SameSite=Lax` (refresh tokens)
- Double-submit cookie pattern (future enhancement)

**Rate Limiting:**
- Express rate limit middleware
- Limits:
  - Login: 5 attempts per 15 minutes (per IP)
  - Registration: 3 attempts per hour (per IP)
  - API calls: 100 requests per minute (per user)

**Security Headers:**
```typescript
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https://cdn.tcb.vn"]
    }
  },
  hsts: { maxAge: 31536000 }, // HSTS 1 year
  noSniff: true,
  xssFilter: true
}));
```

---

## Scalability & Performance

### Caching Strategy

**Cache Hierarchy:**

**Level 1: CDN (CloudFront)**
- Static assets: JS, CSS, images
- TTL: 1 year (versioned assets)
- Cache hit ratio: >95%

**Level 2: Application Cache (Redis)**
- User profiles: TTL 5 minutes
- Search results: TTL 5 minutes
- Campaign list: TTL 10 minutes
- Cache invalidation: On data update

**Level 3: Database Cache (PostgreSQL shared_buffers)**
- Hot data in memory
- Query result cache

**Cache Key Strategy:**
```
profile:{influencer_id}
search:{hash(filters)}
campaigns:list:{page}:{limit}
```

**Cache Invalidation:**
- On profile update → Invalidate `profile:{id}`
- On campaign update → Invalidate `campaigns:*`
- On new influencer → Invalidate search caches

---

### Performance Optimization

**Database Query Optimization:**

1. **Use Indexes:**
   ```sql
   CREATE INDEX idx_influencers_email ON influencers(email);
   CREATE INDEX idx_social_profiles_platform_handle ON social_profiles(platform, account_handle);
   ```

2. **Avoid N+1 Queries:**
   ```typescript
   // ❌ BAD (N+1 query)
   const influencers = await repo.find();
   for (const inf of influencers) {
     const profiles = await profileRepo.find({ influencer_id: inf.id });
   }

   // ✅ GOOD (1 query)
   const influencers = await repo.find({
     relations: ['profiles']
   });
   ```

3. **Pagination:**
   - Always paginate lists (limit 20-50)
   - Use cursor-based pagination for large datasets (future)

**API Optimization:**

1. **Field Selection:**
   - Allow clients to select fields: `?fields=id,name,email`
   - Reduces response size

2. **Compression:**
   - Gzip/Brotli compression
   - Reduces bandwidth by 70-80%

3. **Async Operations:**
   - File uploads → Background job
   - Data push to Vendor → Background job
   - Email sending → Background job

---

## Reliability & Availability

### Monitoring & Alerting

**Metrics to Monitor:**

**Application Metrics:**
- Request rate (requests/second)
- Error rate (errors/total requests)
- Response time (p50, p95, p99)
- Success rate (2xx/total)

**Infrastructure Metrics:**
- CPU utilization (target <70%)
- Memory utilization (target <80%)
- Disk I/O
- Network I/O

**Business Metrics:**
- Influencer registrations/day
- Campaign applications/day
- Search requests/day
- Vendor API success rate

**Alerts:**

**P0 (Critical - Immediate Response):**
- System down (uptime <99.5%)
- Database connection failures
- Error rate >5%

**P1 (High - Response within 1 hour):**
- API response time p95 >500ms
- Error rate >1%
- Vendor API down

**P2 (Medium - Response within 4 hours):**
- Cache hit ratio <70%
- Disk usage >80%

**Alert Channels:**
- PagerDuty (on-call rotation)
- Slack (#alerts channel)
- Email (backup)

---

### Logging Strategy

**Log Levels:**
- **ERROR:** Application errors, exceptions
- **WARN:** Degraded performance, retry attempts
- **INFO:** Business events (user registration, campaign creation)
- **DEBUG:** Detailed debugging info (dev/staging only)

**Structured Logging (JSON):**
```json
{
  "timestamp": "2026-02-13T10:30:00Z",
  "level": "ERROR",
  "request_id": "uuid-123",
  "user_id": "uuid-456",
  "message": "Vendor API call failed",
  "error": {
    "name": "VendorAPIError",
    "message": "Connection timeout",
    "stack": "..."
  },
  "context": {
    "endpoint": "/api/v1/match",
    "retry_attempt": 3
  }
}
```

**Log Aggregation:**
- AWS CloudWatch Logs (short-term: 7 days)
- Future: ELK Stack (long-term: 90 days)

**Log Retention:**
- Application logs: 30 days
- Audit logs: 7 years (compliance)
- Access logs: 90 days

---

## Development & Deployment

### Development Workflow

**Branching Strategy (Git Flow):**
```
main (production)
  ├── develop (integration)
  │     ├── feature/influencer-registration
  │     ├── feature/campaign-search
  │     └── feature/admin-approval
  ├── hotfix/fix-login-bug
  └── release/v1.0.0
```

**Commit Message Format:**
```
type(scope): subject

feat(influencer): add multi-profile support
fix(auth): resolve JWT expiry issue
docs(api): update Swagger annotations
```

---

### CI/CD Pipeline

**GitHub Actions Workflow:**

**Step 1: Lint & Test (on every push)**
```yaml
- name: Lint
  run: npm run lint

- name: Unit Tests
  run: npm run test:unit

- name: Integration Tests
  run: npm run test:integration

- name: Check Coverage
  run: npm run test:coverage
  # Fail if coverage <80%
```

**Step 2: Build (on PR merge to develop)**
```yaml
- name: Build Docker Image
  run: docker build -t tcb-influencer-api:${{ github.sha }} .

- name: Push to ECR
  run: docker push {ecr_repo}/tcb-influencer-api:${{ github.sha }}
```

**Step 3: Deploy to Staging (on PR merge to develop)**
```yaml
- name: Deploy to ECS Staging
  run: |
    aws ecs update-service \
      --cluster tcb-influencer-staging \
      --service api \
      --force-new-deployment

- name: Run Smoke Tests
  run: npm run test:smoke -- --env=staging
```

**Step 4: Deploy to Production (on release tag)**
```yaml
- name: Deploy to ECS Production
  run: |
    aws ecs update-service \
      --cluster tcb-influencer-production \
      --service api \
      --force-new-deployment

- name: Health Check
  run: curl https://api.tcb.influencer.vn/health
```

---

### Deployment Strategy

**Blue-Green Deployment:**
- Deploy new version (Green) alongside old version (Blue)
- Run smoke tests on Green
- Switch ALB target group: Blue → Green
- Monitor for 30 minutes
- If errors → Rollback to Blue (1-click)
- If success → Terminate Blue

**Rollback Plan:**
- Keep previous Docker image tagged
- Rollback command: Update ECS task definition to previous image
- Target: <5 minutes rollback time

---

## Traceability Matrix

### Functional Requirements Coverage

| FR ID | FR Name | Components | API Endpoints | Database Tables |
|-------|---------|------------|---------------|-----------------|
| FR-001 | Account Creation | Influencer Module, Auth Service | POST /auth/register, POST /influencers | influencers, users |
| FR-002 | Multi-Profile Support | Influencer Module | POST /influencers/{id}/profiles | social_profiles |
| FR-003 | Tier 1/2/3 Data Collection | Influencer Module | PATCH /influencers/{id} | influencers, social_profiles, profile_tiers |
| FR-004 | Social Metrics Auto-Fetch | Data Integration Layer | POST /profiles/{id}/crawl | social_profiles |
| FR-005 | Profile Editing | Influencer Module | PATCH /influencers/{id} | influencers, social_profiles |
| FR-006 | Profile Status Management | Influencer Module | PATCH /profiles/{id}/status | social_profiles |
| FR-007 | Influencer Search | Campaign Module, Data Integration | GET /search/influencers | (Vendor via AT Core) |
| FR-008 | Advanced Filters | Campaign Module | GET /search/influencers?filters=... | (Vendor) |
| FR-009 | Sorting & Pagination | Campaign Module | GET /search/influencers?sort=...&page=... | (Vendor) |
| FR-010 | Compare Influencers | Campaign Module | GET /influencers/compare?ids=... | influencers, social_profiles |
| FR-011 | Save Searches | Campaign Module | POST /search/save | saved_searches |
| FR-012 | Browse Campaigns | Campaign Module | GET /campaigns | campaigns |
| FR-013 | Apply to Campaign | Campaign Module | POST /campaigns/{id}/apply | campaign_applications |
| FR-014 | View Campaign Brief | Campaign Module | GET /campaigns/{id} | campaigns |
| FR-015 | Submit Deliverables | Influencer Module | POST /submissions | submissions |
| FR-016 | Vendor API Integration | Data Integration Layer | Internal service | (External API) |
| FR-017 | AT Core Middleware | Data Integration Layer | Internal service | (External API) |
| FR-018 | Performance Data Push | Data Integration Layer | POST /influencers/{id}/performance | performance_data |
| FR-019 | Brand Ratings Push | Data Integration Layer | POST /influencers/{id}/ratings | brand_ratings |
| FR-020 | Influencer Approval | Admin Module | POST /admin/approvals/{id}/approve | influencers |
| FR-021 | eKYC Verification | Admin Module, File Upload Service | POST /upload/document | influencers |
| FR-022 | Compliance Checks | Admin Module | GET /admin/approvals | influencers |
| FR-023 | Responsive Design | Frontend | (UI components) | N/A |
| FR-024 | Vietnamese + English | Frontend, Backend | All endpoints (i18n) | N/A |
| FR-025 | Accessibility (WCAG 2.1 AA) | Frontend | (UI components) | N/A |

---

### Non-Functional Requirements Coverage

| NFR ID | NFR Name | Architectural Solution | Validation Method |
|--------|----------|------------------------|-------------------|
| NFR-001 | Performance (<2s page load, <300ms API) | CDN, Redis caching, database indexing, code splitting | Load testing (k6), Lighthouse, Datadog APM |
| NFR-002 | Availability (99.5% uptime) | Multi-AZ, ALB health checks, auto-scaling, RDS Multi-AZ | CloudWatch uptime monitoring, monthly report |
| NFR-003 | Data Encryption | RDS encryption (AES-256), S3 encryption (SSE-S3), TLS 1.3 | Security audit, AWS Config compliance |
| NFR-004 | Authentication & Authorization | JWT (HS256), RBAC, bcrypt password hashing | Penetration testing, security audit |
| NFR-005 | Scalability (100K influencers, 10K concurrent) | ECS auto-scaling, read replicas, Redis cluster | Load testing (10K concurrent users), capacity planning |
| NFR-006 | Error Handling & Graceful Degradation | Retry logic, circuit breaker, fallback to cache | Chaos testing, monitor error rates |
| NFR-007 | Code Quality & Documentation | ESLint, Prettier, Jest (>80% coverage), OpenAPI docs | SonarQube, test coverage reports |
| NFR-008 | Accessibility (WCAG 2.1 AA) | Semantic HTML, ARIA labels, keyboard navigation | axe-core tests, Lighthouse accessibility score |
| NFR-009 | Browser & Device Support | Responsive design, Tailwind, cross-browser testing | BrowserStack testing, Lighthouse mobile score |
| NFR-010 | GDPR Compliance | Data retention policy, right to erasure, audit logs | Data export test, compliance audit |

---

## Trade-offs & Decisions

### Decision 1: Modular Monolith vs Microservices

**Decision:** Modular Monolith

**Trade-off:**
- ✅ Gain: Simpler deployment, easier debugging, lower ops overhead
- ❌ Lose: Cannot independently scale modules, team boundaries less clear

**Rationale:**
- Level 3 project (59-87 stories) doesn't justify microservices complexity
- Single tenant (TCB only) → No need for multi-tenancy at module level
- Small team → Microservices coordination overhead too high

**Future:** If project grows to multi-tenant with 500+ stories, consider microservices migration

---

### Decision 2: PostgreSQL vs MongoDB (TCB Database)

**Decision:** PostgreSQL

**Trade-off:**
- ✅ Gain: ACID transactions, relational integrity, strong typing
- ❌ Lose: Less flexible for schema changes (but migrations handle this)

**Rationale:**
- Influencer → Profiles is clear 1:many relationship
- Financial data (bank accounts) requires ACID
- Tier 2/3 flexible data: Use JSONB columns (best of both worlds)

---

### Decision 3: JWT vs Session-based Auth

**Decision:** JWT (stateless)

**Trade-off:**
- ✅ Gain: Stateless (scales horizontally), no session storage needed
- ❌ Lose: Cannot revoke tokens (mitigated with Redis blacklist)

**Rationale:**
- Horizontal scaling requires stateless API
- Mobile apps: JWT easier to manage than cookies
- Logout: Use Redis blacklist (acceptable trade-off)

---

### Decision 4: Redis vs Memcached

**Decision:** Redis

**Trade-off:**
- ✅ Gain: Data structures (lists, sets), persistence, pub/sub
- ❌ Lose: Slightly higher memory usage than Memcached

**Rationale:**
- Need data structures for Bull Queue (job processing)
- Persistence: Can survive Redis restarts
- Ecosystem: Better NestJS integration

---

### Decision 5: REST vs GraphQL

**Decision:** REST

**Trade-off:**
- ✅ Gain: Simpler, standard, easier to cache
- ❌ Lose: Over-fetching (mitigated with field selection)

**Rationale:**
- Team familiar with REST
- Caching easier with REST (HTTP caching)
- GraphQL overkill for CRUD operations

---

## Appendix

### Glossary

- **AT Core:** AccessTrade Multi-Tenant Middleware Platform
- **Vendor:** External service provider (Influence-Meter API)
- **Tier 1/2/3:** Progressive data collection strategy (Essential/Recommended/Optional)
- **eKYC:** Electronic Know Your Customer (identity verification)
- **RBAC:** Role-Based Access Control
- **JWT:** JSON Web Token
- **WCAG:** Web Content Accessibility Guidelines
- **GDPR:** General Data Protection Regulation
- **SBV:** State Bank of Vietnam
- **CVR:** Conversion Rate
- **CTR:** Click-Through Rate
- **ROI:** Return on Investment

---

### References

- **PRD:** accesstrade-projects/techcombank/influencer-library/prd-tcb-influencer-library-2026-02-13.md
- **Brainstorming (4 Sources):** .bmad/influencer-library-4sources/brainstorming-influencer-library-4sources-2026-02-13.md
- **Brainstorming (Data Requirements):** .bmad/influencer-library-4sources/brainstorming-tcb-influencer-data-requirements-2026-02-13.md
- **Brainstorming (Multi-Profile):** .bmad/influencer-library-4sources/brainstorming-influencer-vs-profile-multi-account-2026-02-13.md
- **Implementation Plans:**
  - plans/20260212-1430-influencer-portal-week2/
  - plans/20260212-1234-brand-influencer-menu/

---

**Document Status:** Draft for Review
**Next Steps:**
1. Stakeholder review (Product Manager, Tech Lead, Security Team)
2. Finalize technology choices
3. Proceed to Sprint Planning (Phase 4)

**Last Updated:** 2026-02-13
