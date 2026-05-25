# Techcombank — Feature Inventory

> Generated: 2026-05-07 (Evidence-based scan từ source code)

---

## 1. Backend Services (29 services)

Backend features được tổ chức trong `backend/internal/service/*.go`. Mỗi file = 1 domain service.

| Service | Mô tả | Loại | Path |
|---------|------|------|------|
| **audit** | Audit logging for user actions & changes | Core | `backend/internal/service/audit.go` |
| **budget** | Budget management & allocation for campaigns | **TCB-specific** | `backend/internal/service/budget.go` |
| **cashflow** | Cash flow tracking & transaction management | **TCB-specific** | `backend/internal/service/cashflow.go` |
| **check_rate_limit** | API rate limiting & throttling | Core | `backend/internal/service/check_rate_limit.go` |
| **content** | Content/post management | Core | `backend/internal/service/content.go` |
| **content_analytic_daily** | Daily analytics aggregation for content | Core | `backend/internal/service/content_analytic_daily.go` |
| **content_flow** | Content workflow/approval pipeline | Core | `backend/internal/service/content_flow.go` |
| **dashboard_analytics** | Dashboard metrics & KPIs | **TCB-specific** | `backend/internal/service/dashboard_analytics.go` |
| **event** | Campaign/event management | Core | `backend/internal/service/event.go` |
| **event_schema** | Event schema & tracking definitions | Core | `backend/internal/service/event_schema.go` |
| **filtered_campaigns** | Campaign filtering & search | Core | `backend/internal/service/filtered_campaigns.go` |
| **global_dashboard** | System-wide analytics dashboard | Core | `backend/internal/service/global_dashboard.go` |
| **influencer** | Influencer/creator profile management | Core | `backend/internal/service/influencer.go` |
| **load_data** | Data loading & initialization utilities | Core | `backend/internal/service/load_data.go` |
| **notification** | Notification system & messaging | Core | `backend/internal/service/notification.go` |
| **otp** | OTP generation & verification | Core | `backend/internal/service/otp.go` |
| **rating_aggregation** | Rating calculation & aggregation | Core | `backend/internal/service/rating_aggregation.go` |
| **reconciliation_checklist** | Reconciliation item evaluation & approval | **TCB-specific** | `backend/internal/service/reconciliation_checklist.go` |
| **reconciliation_snapshot** | Reconciliation data snapshots & versioning | **TCB-specific** | `backend/internal/service/reconciliation_snapshot.go` |
| **reconciliation_snapshot_job** | Async job for reconciliation snapshots | **TCB-specific** | `backend/internal/service/reconciliation_snapshot_job.go` |
| **review** | Content review & moderation | Core | `backend/internal/service/review.go` |
| **segment** | User segmentation & targeting | **TCB-specific** | `backend/internal/service/segment.go` |
| **tracking_request_crawl** | Web crawling for content tracking | Core | `backend/internal/service/tracking_request_crawl.go` |
| **upload_avatar_social** | Social media profile avatar upload | Core | `backend/internal/service/upload_avatar_social.go` |
| **user** | User account & profile management | Core | `backend/internal/service/user.go` |
| **user_social** | Social media account linking | Core | `backend/internal/service/user_social.go` |
| **user_social_partner** | Partner social account integration | Core | `backend/internal/service/user_social_partner.go` |
| **video** | Video management & streaming | Core | `backend/internal/service/video.go` |
| **withdraw** | Withdrawal/payout processing | Core | `backend/internal/service/withdraw.go` |

---

## 2. Backend Models (MongoDB Collections — 85 models)

MongoDB entity/collection definitions in `backend/internal/model/mg/`.

### Core Collections
- **user.go** - User account data
- **user_device.go** - Device registration & tracking
- **user_bank_card.go** - Bank account information
- **user_partner.go** - Partner-user relationships
- **user_publisher.go** - Publisher account data
- **user_social.go** - Social media linked accounts
- **user_social_partner.go** - Partner social accounts
- **session.go** - Authentication sessions
- **identification.go** - User identity verification
- **audit_login.go** - Login audit trail

### Campaign & Content Collections
- **campaign.go** - Campaign/event metadata
- **event.go** - Event data & settings
- **event_schema.go** - Event tracking schemas
- **event_categories.go** - Event category definitions
- **event_bonus.go** - Bonus reward structures
- **event_reward.go** - Reward configuration
- **event_reward_temp.go** - Temporary reward data
- **event_tracking_threshold.go** - Tracking thresholds
- **content.go** - Content/post data
- **content_flow.go** - Content approval workflow
- **content_flow_backup.go** - Workflow backup/history
- **content_manual_flow.go** - Manual content workflow
- **content_callback.go** - Content callback tracking
- **content_import_tracking.go** - Import history
- **content_crawl_history.go** - Web crawl logs
- **content_transcript.go** - Content transcription
- **content_analytic_daily.go** - Daily content analytics

### Budget & Financial Collections (TCB-specific)
- **cash_flow.go** - Transaction history & ledger
- **budget_alert.go** - Budget alerts & thresholds
- **transfer.go** - Payment transfer data
- **withdraw.go** - Withdrawal/payout requests
- **user_income_month.go** - Monthly income summaries

### Reconciliation Collections (TCB-specific)
- **reconciliation.go** - Main reconciliation records
- **reconciliation_checklist.go** - Reconciliation items & status
- **reconciliation_item.go** - Individual reconciliation entries
- **reconciliation_snapshot.go** - Reconciliation versioning
- **reconciliation_history.go** - Reconciliation audit trail
- **reconciliation_event_config.go** - Reconciliation event settings

### Segmentation Collections (TCB-specific)
- **segment.go** - Audience segment definitions
- **user_segment.go** - User segment membership

### Analytics & Performance
- **event_analytic_daily.go** - Daily event metrics
- **user_event.go** - User event tracking
- **user_event_analytic_daily.go** - Daily user-event analytics
- **user_event_schema_tracking.go** - Schema tracking data
- **content_analytic_daily.go** - Content performance data
- **rating_cache.go** - Cached rating values
- **performance_data.go** - Performance metrics

### Influencer & Partner
- **influencer_profile.go** - Influencer profile data
- **partner.go** - Partner organization data
- **partner_influencer_config.go** - Partner-influencer settings
- **profile_review.go** - Profile review & status

### Article & News
- **article.go** - Blog article content
- **article_view.go** - Article view tracking
- **news.go** - News item data
- **news_views.go** - News view tracking

### Admin & Configuration
- **admin_notification.go** - Admin notifications
- **role.go** - User role definitions
- **staff.go** - Admin staff accounts
- **audit.go** - General audit logs
- **configurations.go** - System configuration

### Utility & System
- **contract.go** - Contract terms & agreements
- **cover.go** - Cover/banner images
- **file.go** - File upload metadata
- **export.go** - Data export records
- **import_batch.go** - Batch import operations
- **notification.go** - User notifications
- **otp.go** - OTP records
- **tag.go** - Tag definitions
- **quick_action.go** - Quick action shortcuts
- **manage_code.go** - Code management (promo, etc.)
- **blacklist_keyword.go** - Content filter keywords
- **auto_approve_rule.go** - Approval automation rules
- **bank.go** - Bank information
- **bank_branch.go** - Bank branch details
- **country.go** - Country/region data
- **province.go** - Province/state data
- **referral.go** - Referral program tracking
- **tracking_identification.go** - Tracking ID management
- **tracking_request_crawl.go** - Crawl request logs
- **tracking_request_otp.go** - OTP-based tracking requests
- **tracking_request_webhook.go** - Webhook tracking requests
- **transcript_tracking_request.go** - Transcript tracking

### Campaign Matching (TCB-specific)
- **campaign_matching.go** - Campaign matching rules

---

## 3. Backend HTTP Routes (high-level)

Backend API organized via Echo router in `backend/pkg/admin/router/router.go`. Route groups:

| Route Group | Purpose | Service Layer |
|-------------|---------|----------------|
| `/common/*` | Common utilities (auth, config, file upload) | Core |
| `/staff/*` | Admin staff management | Core |
| `/event/*` | Event/campaign management | Core |
| `/event-categories/*` | Event category CRUD | Core |
| `/event-bonus/*` | Bonus configuration | Core |
| `/content/*` | Content/post management | Core |
| `/user/*` | User account management | Core |
| `/article/*` | Article management | Core |
| `/event-schema/*` | Event schema configuration | Core |
| `/reconciliation/*` | **Reconciliation checklist & approval** | **TCB-specific** |
| `/export/*` | Data export operations | Core |
| `/identification/*` | KYC/identity verification | Core |
| `/transfers/*` | **Payment transfer management** | **TCB-specific** |
| `/news/*` | News management | Core |
| `/partner/*` | Partner organization management | Core |
| `/quick-action/*` | Quick action configuration | Core |
| `/role/*` | Role-based access control | Core |
| `/segment/*` | **User segment management** | **TCB-specific** |
| `/user-segment/*` | **User segment assignment** | **TCB-specific** |
| `/admin-notification/*` | Admin notification management | Core |
| `/content-manual-flow/*` | Manual content workflow | Core |
| `/audit/*` | Audit log queries | Core |
| `/tag/*` | Tag management | Core |
| `/migration/*` | Data migration utilities | Core |
| `/influencer/*` | Influencer profile management | Core |
| `/review/*` | Content review/moderation | Core |
| `/influencer-profiles/*` | Extended influencer data | Core |
| `/campaign/*` | Campaign setup & management | Core |
| `/campaign-matching/*` | **Campaign matching rules** | **TCB-specific** |
| `/budget/*` | **Budget allocation & management** | **TCB-specific** |
| `/manage-code/*` | Promo code management | Core |
| `/blacklist-keyword/*` | Content filter keywords | Core |
| `/auto-approve-rule/*` | Approval automation | Core |
| `/analytics/*` | System analytics/KPIs | **TCB-specific** |
| `/performance/*` | Performance metrics & reports | **TCB-specific** |

---

## 4. Admin Features (admin/) — 29 pages

Admin portal pages in `admin/src/pages/`. Each folder = 1 admin feature.

| Page | Purpose | Type |
|------|---------|------|
| **analytics-dashboard** | System-wide analytics & KPI dashboard | **TCB-specific** |
| **article** | Blog article management | Core |
| **blacklist-keyword** | Content filter keyword management | Core |
| **configuration** | System configuration settings | Core |
| **content** | Content/post moderation & approval | Core |
| **content-import** | Batch content import tool | Core |
| **dashboard** | Main admin dashboard | Core |
| **dashboard-external** | External dashboard view | Core |
| **data** | Data management utilities | Core |
| **event** | Campaign/event management | Core |
| **event-bonus** | Bonus reward configuration | Core |
| **event-category** | Event category CRUD | Core |
| **event-statistic** | Event performance statistics | Core |
| **identification** | KYC/identity verification | Core |
| **influencer** | Influencer profile management | Core |
| **influencer-management** | Advanced influencer management | Core |
| **login** | Admin login interface | Core |
| **manage-code** | Promo/coupon code management | Core |
| **news** | News/article publication | Core |
| **notification** | Notification management & sending | Core |
| **partner** | Partner organization management | Core |
| **quick-action** | Quick action shortcuts config | Core |
| **reconciliation** | **Reconciliation checklist & approval** | **TCB-specific** |
| **segment** | **User segmentation & targeting** | **TCB-specific** |
| **staff** | Admin staff account management | Core |
| **tag** | Content tag management | Core |
| **transfer** | **Payment transfer processing** | **TCB-specific** |
| **user** | User account management | Core |
| **user-partner** | User-partner relationship management | Core |

---

## 5. Frontend Features (frontend/) — 21 pages

Creator-facing pages in `frontend/src/pages/`.

| Page | Purpose | Audience |
|------|---------|----------|
| **404** | Error page | Creator |
| **account** | Account settings & profile | Creator |
| **article** | Article viewing | Creator |
| **bank** | Bank account linking | Creator |
| **common-article** | Shared article view | Creator |
| **connect-tiktok** | TikTok OAuth integration | Creator |
| **contact** | Contact form | Creator |
| **content** | Creator content management | Creator |
| **contract** | Contract viewing & signing | Creator |
| **creator-info** | Creator profile info | Creator |
| **events-by-category** | Campaign browsing by category | Creator |
| **guide** | How-to guides & tutorials | Creator |
| **home** | Home/landing page | Creator |
| **login-google** | Google OAuth login | Creator |
| **login-tiktok** | TikTok OAuth login | Creator |
| **main-home** | Main homepage | Creator |
| **notification** | Notification center | Creator |
| **partner-home** | Partner dashboard view | Partner |
| **profile** | User profile management | Creator |
| **qa** | Q&A/FAQ section | Creator |

---

## 6. Dashboard Features (dashboard/) — NEW, TCB-specific

Next.js App Router (v16) dashboard with internationalization (next-intl). **Completely new module** not in legacy admin/frontend.

### Routes & Pages

| Route | Feature | Type | Purpose |
|-------|---------|------|---------|
| **[locale]/login** | Login page | Auth | Creator authentication |
| **[locale]/forgot-password** | Password reset | Auth | Forgot password flow |
| **[locale]/reset-password** | Password recovery | Auth | Reset password execution |
| **[locale]/accept-invite** | Invitation acceptance | Auth | Accept campaign invite |
| **[locale]/analytics** | Main analytics tab | **Dashboard** | Overview metrics & KPIs |
| **[locale]/campaigns** | Campaign management | **Dashboard** | List campaigns |
| **[locale]/campaigns/create** | Campaign creation | **Dashboard** | Create new campaign |
| **[locale]/campaigns/[id]** | Campaign detail | **Dashboard** | View/edit campaign |
| **[locale]/contents** | Content management | **Dashboard** | List content/posts |
| **[locale]/contents/[id]** | Content detail | **Dashboard** | View/edit content |
| **[locale]/influencers** | Influencer list | **Dashboard** | Browse influencers |
| **[locale]/influencers/[id]** | Influencer detail | **Dashboard** | View influencer profile |
| **[locale]/profiles** | Profile management | **Dashboard** | Manage user profile |
| **[locale]/profiles/[id]** | Profile detail | **Dashboard** | View/edit profile |
| **[locale]/performance** | Performance analytics | **Dashboard** | Performance metrics |
| **[locale]/exports** | Data export | **Dashboard** | Export analytics data |
| **[locale]/settings** | System settings | **Dashboard** | Dashboard settings |

### Dashboard Components (Next.js/React)

#### Layout & Navigation
- **Header** - Top navigation & user menu
- **Sidebar** - Main navigation menu
- **Layout wrapper** - Page structure

#### Analytics & Filters (Smart Auto-Hide Pattern)
- **FilterBar** - Campaign/Creator/Period/DateRange filters (with auto-hide for Creator filter on non-creator tab)
- **CampaignSelect** - Campaign dropdown selector
- **PlatformFilter** - Platform/network filter
- **PeriodSelect** - Time period selection
- **DateRange** - Custom date range picker
- **DashboardTabs** - Tab navigation (Overview/Creators/Contents/Performance)

#### Metrics & Visualization (Phase 3 KPI Cards)
- **KPICard** - Single metric card widget (icon, label, value, trend)
- **KPIGrid** - Responsive 6-card grid (3-col desktop, 2-col tablet, 1-col mobile)
- **TrendBadge** - Trend indicator (up/down/neutral with percentage)
- **useAnalytics** - React Query hook for metrics data

#### Tab Content Implementations
- **OverviewTabContent** - KPI metrics + TrendBadges
- **CreatorTabContent** - Influencer metrics & table
- **ContentTabContent** - Content/post metrics
- **PerformanceTabContent** - Performance analytics

#### Advanced Features
- **Smart Auto-Hide Filter Pattern** - Conditionally render CreatorFilter (Feb 2026)
- **Framer Motion animations** - Smooth filter appearance/disappearance
- **URL-based state management** - Tab & filter state in query params
- **Suspense boundaries** - Async content loading
- **next-intl i18n** - Vietnamese + English localization (REQUIRED)

### Documentation Resources
- **README.md** - Main project documentation
- **DOCUMENTATION_SUMMARY.md** - Phase breakdown (Phase 0-3 KPI complete, Phase 4+ planned)
- **docs/README.md** - Documentation index
- **docs/architecture.md** - System design & component hierarchy
- **docs/filter-bar-components.md** - Filter API reference
- **docs/development-guide.md** - Step-by-step dev guide
- **docs/filter-patterns.md** - Smart Auto-Hide pattern (Feb 2026)
- **docs/filter-design.md** - Filter bar design rationale

### Tech Stack
- **Next.js 16** (App Router, Turbopack)
- **React 19** (React Compiler enabled)
- **TypeScript** (strict mode)
- **Tailwind CSS** + **shadcn/ui** + **Radix UI**
- **TanStack Query v5** + **TanStack Table v8**
- **Zustand** (filter state)
- **Framer Motion** (animations)
- **next-intl v4+** (i18n)
- **Recharts** (charts)
- **date-fns** (date utilities)

---

## 7. Key TCB-specific Modules (Baseline Features)

Features that distinguish TCB from vCreator/Ambassador:

### 1. Budget Management System
- **Service**: `budget.go`
- **Models**: `cash_flow.go`, `budget_alert.go`
- **Admin Pages**: reconciliation, transfer
- **Purpose**: Campaign budget allocation, spending limits, alerts
- **Evidence**: Budget service with campaign spending tracking, email alerts

### 2. Reconciliation Engine (Core TCB Differentiator)
- **Services**: `reconciliation_checklist.go`, `reconciliation_snapshot.go`, `reconciliation_snapshot_job.go`
- **Models**: `reconciliation.go`, `reconciliation_checklist.go`, `reconciliation_item.go`, `reconciliation_snapshot.go`, `reconciliation_event_config.go`, `reconciliation_history.go`
- **Admin Pages**: reconciliation
- **Routes**: `/reconciliation/*`
- **Purpose**: Multi-step data validation, automatic evaluation, manual override, approval workflow
- **Evidence**: 30+ methods for evaluation, classification, approval, reset

### 3. Cashflow & Transfer System
- **Service**: `cashflow.go`
- **Models**: `cash_flow.go`, `transfer.go`, `withdraw.go`, `user_income_month.go`
- **Admin Pages**: transfer
- **Routes**: `/transfers/*`
- **Purpose**: Real-time transaction ledger, payout processing
- **Evidence**: Add/get/track cash flows, manage transaction history

### 4. Segmentation & Targeting
- **Service**: `segment.go`
- **Models**: `segment.go`, `user_segment.go`
- **Admin Pages**: segment, user-segment
- **Routes**: `/segment/*`, `/user-segment/*`
- **Purpose**: User audience segmentation, automatic/manual targeting, referral conditions
- **Evidence**: Segment type (automatic/manual), apply types (referral codes, rules)

### 5. Campaign Matching Engine
- **Service**: N/A (model-only)
- **Models**: `campaign_matching.go`
- **Routes**: `/campaign-matching/*`
- **Purpose**: Match rules between campaigns & influencers/content

### 6. Analytics & Performance Dashboard
- **Service**: `dashboard_analytics.go`, `global_dashboard.go`
- **Admin Pages**: analytics-dashboard
- **Dashboard Pages**: /analytics, /performance
- **Routes**: `/analytics/*`, `/performance/*`
- **Purpose**: System-wide KPI aggregation, trend analysis
- **Evidence**: Dashboard metrics service for TCB-specific analytics

### 7. Vertex AI Integration (Mentioned in context)
- **Likely Purpose**: Smart content analysis, recommendations
- **Note**: Found reference in infrastructure (vertex_ai module) but not yet in feature services

---

## 8. Summary by Audience

### For Features to Sync Across AccessTrade Products

**CORE (shared with vCreator/Ambassador):**
- User management
- Content/post management
- Campaign/event setup
- Content moderation & review
- Social media integration (TikTok, etc.)
- Influencer/creator profiles
- Notifications
- Article/news management
- Quick actions & shortcuts

**TCB-SPECIFIC (do NOT expect in vCreator/Ambassador):**
- Budget allocation & management
- Reconciliation workflow (6 models, complex evaluation logic)
- Cash flow tracking & transfers
- User segmentation & targeting
- Campaign matching rules
- Advanced analytics dashboard
- Performance reporting

---

## File Statistics

| Component | Count | Notes |
|-----------|-------|-------|
| Backend Services | 29 | `backend/internal/service/*.go` |
| MongoDB Models | 85 | `backend/internal/model/mg/*.go` |
| API Route Groups | 32 | From `backend/pkg/admin/router/router.go` |
| Admin Pages | 29 | `admin/src/pages/*/` folders |
| Frontend Pages | 21 | `frontend/src/pages/*/` folders |
| Dashboard Routes | 17 | Next.js `[locale]/*` paths |
| Dashboard Components | 20+ | Filter, KPI, tabs, layout |

---

## Evidence Paths (for verification)

- **Backend services** → `/Users/vinhnguyen/workspaces/diso/accesstrade-projects/techcombank/backend/internal/service/`
- **Backend models** → `/Users/vinhnguyen/workspaces/diso/accesstrade-projects/techcombank/backend/internal/model/mg/`
- **Backend routes** → `/Users/vinhnguyen/workspaces/diso/accesstrade-projects/techcombank/backend/pkg/admin/router/router.go`
- **Admin pages** → `/Users/vinhnguyen/workspaces/diso/accesstrade-projects/techcombank/admin/src/pages/`
- **Frontend pages** → `/Users/vinhnguyen/workspaces/diso/accesstrade-projects/techcombank/frontend/src/pages/`
- **Dashboard app** → `/Users/vinhnguyen/workspaces/diso/accesstrade-projects/techcombank/dashboard/src/app/[locale]/`
- **Dashboard docs** → `/Users/vinhnguyen/workspaces/diso/accesstrade-projects/techcombank/dashboard/DOCUMENTATION_SUMMARY.md`

---

Generated: 2026-05-07 | Updated: Evidence-based source code scan
