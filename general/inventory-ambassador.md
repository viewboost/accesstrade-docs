# Ambassador — Feature Inventory

> Generated: 2026-05-07. Evidence-based scan từ source code. Multi-tenant white-label platform.

## 1. Backend Services

| Service | Mô tả | Loại | Path |
|---------|------|------|------|
| Affiliate | Quản lý affiliate campaigns, mapping event-campaign, commissions | Ambassador-specific | backend/internal/service/affiliate.go |
| Audit | Logging & audit trail cho các hành động admin | Core | backend/internal/service/audit.go |
| Cashflow | Quản lý dòng tiền: income, pending, rejected, completed | Core | backend/internal/service/cashflow.go |
| Content | Quản lý nội dung (article, video): CRUD, hashtag checking, status workflows | Core | backend/internal/service/content.go |
| Content Analytic Daily | Aggregation analytics hàng ngày cho content | Core | backend/internal/service/content_analytic_daily.go |
| Content Flow | Workflow & automation cho nội dung (review, approve, reject) | Core | backend/internal/service/content_flow.go |
| Event | Quản lý event: CRUD, reward calculation, analytics | Core | backend/internal/service/event.go |
| Event Schema | Tracking schema & event definitions | Core | backend/internal/service/event_schema.go |
| Load Data | Data import & migration utilities | Core | backend/internal/service/load_data.go |
| Notification | Push notification management (Firebase) | Core | backend/internal/service/notification.go |
| OTP | One-time password generation & verification | Core | backend/internal/service/otp.go |
| User | User profile, statistic, partner mapping | Core | backend/internal/service/user.go |
| User Social | Social media account linking (TikTok, YouTube, Instagram) | Core | backend/internal/service/user_social.go |
| User Social Partner | Partner-specific social config & linking | Ambassador-specific | backend/internal/service/user_social_partner.go |
| Video | Video CRUD & management | Core | backend/internal/service/video.go |
| Withdraw | Withdrawal requests & payment processing | Core | backend/internal/service/withdraw.go |

## 2. Backend Models (MongoDB Collections)

### User & Authentication (Core)
- User (profile, stats, KYC status)
- User Device (device tracking)
- User Bank Card (payment methods)
- User Event (user participation in events)
- User Event Analytic Daily (user event stats)
- User Event Schema Tracking (tracking info per user)
- User Income Month (monthly income summary)
- User Partner (user-partner association)
- User Publisher (publisher role)
- User Segment (segmentation tags)
- User Social (TikTok/YouTube/Instagram links)
- User Social Partner (partner-specific social setup)
- Session (authentication sessions)
- Identification (KYC documents)
- Tracking Identification (KYC tracking)
- Tracking Request OTP (OTP tracking)

### Partner & Multi-tenant Config (Ambassador-specific)
- Partner (client config: Anker, HDBank, TPBank, VNPay...)
- User Partner (user belongs to partner)
- Common Configs (partner-level configurations)
- Configurations (privacy, feature flags)

### Content & Publishing (Core)
- Article (news/articles)
- Article View (view analytics)
- Content (user-submitted content, status workflow)
- Content Analytic Daily (daily aggregation)
- Content Callback (webhook callbacks)
- Content Crawl History (crawl tracking)
- Content Flow (content workflow stages)
- Content Flow Backup (backups)
- Content Manual Flow (manual workflow entries)
- Content Transcript (transcription storage)
- Video (video metadata)
- Cover (cover images)
- File (file storage metadata)

### Event & Campaign (Core)
- Event (campaign events)
- Event Analytic Daily (daily event stats)
- Event Bonus (bonus rules)
- Event Reward (reward definitions)
- Event Reward Temp (temporary reward caching)
- Event Schema (event tracking schema)
- Event Tracking Threshold (threshold configs)

### Campaign & Affiliate (Ambassador-specific)
- Affiliate (affiliate program config) [Note: model not found but service exists]
- Tag (content tags)
- Category (content categories)
- Gift (reward gifts)
- Gift History (gift redemption)
- Mission (seasonal missions)
- Quick Action (quick task definitions)
- News (news feed)
- News Views (news analytics)

### Financial & Reconciliation (Core)
- Cashflow (transaction log)
- Withdraw (withdrawal requests)
- Transfer (internal transfers)
- Bank (bank list)
- Bank Branch (branch details)
- Reconciliation (reconciliation records)
- Reconciliation History (reconciliation audit)
- Reconciliation Item (line items)

### Notifications & Messaging (Core)
- Notification (push notifications)
- Admin Notification (admin-only notifications)

### Reference Data (Core)
- Role (access control roles)
- Staff (admin staff accounts)
- Province (Vietnamese provinces)
- Country (countries list)
- Segment (user segmentation)
- Audit (audit log)
- Export (export tracking)
- Referral (referral program) [Note: model not found but exists]

## 3. Backend HTTP Routes (High-level)

### Admin API (pkg/admin/handler)
- `/admin/affiliate` - Affiliate campaign management
- `/admin/article` - Article CRUD
- `/admin/audit` - Audit logs
- `/admin/category` - Content categories
- `/admin/common_configs` - Config management
- `/admin/content` - Content moderation & workflow
- `/admin/content-manual-flow` - Manual content workflows
- `/admin/event` - Event CRUD & management
- `/admin/event-bonus` - Bonus configuration
- `/admin/event-budget` - Budget allocation
- `/admin/event-requirements` - Event requirements
- `/admin/event-reward` - Reward rules
- `/admin/event-schema` - Event schema editor
- `/admin/export` - Data export
- `/admin/external_api` - External API integrations
- `/admin/gift` - Gift management
- `/admin/identification` - KYC verification
- `/admin/influencer-profiles` - Influencer profiles
- `/admin/migration` - Data migration tools
- `/admin/mission` - Mission management
- `/admin/news` - News feed
- `/admin/partner` - Partner/client config
- `/admin/quick-action` - Quick actions
- `/admin/reconciliation` - Reconciliation processing
- `/admin/role` - Role & permission management
- `/admin/segment` - User segmentation
- `/admin/staff` - Staff management
- `/admin/tag` - Tag management
- `/admin/transfer` - Internal transfers
- `/admin/user` - User management
- `/admin/user-segment` - User segmentation
- `/admin/admin-notification` - Admin notifications

### Public API (pkg/public/handler)
- `/api/event` - Event details & listing
- `/api/user` - User profile & auth
- `/api/user/social` - Social account linking
- `/api/user/statistic` - User statistics
- `/api/content` - Content submission & management
- `/api/article` - Article listing
- `/api/category` - Category listing
- `/api/bank` - Bank & account info
- `/api/partner` - Partner information
- `/api/notification` - Notifications
- `/api/common_configs` - Config retrieval
- `/api/common_demographics` - Demographics data
- `/api/gift` - Gift listing & redemption
- `/api/mission` - Mission listing
- `/api/transcript` - Content transcription
- `/api/opshub_webhook` - OpshubHub webhook integration
- `/api/influencer-profile` - Creator profiles
- `/api/common` - Common utilities

### File Upload API (pkg/file/handler)
- `/file/upload` - File upload
- `/file/video` - Video upload & processing

## 4. Admin Features

- **affiliate-campaign** - Affiliate campaign CRUD & tracking
- **article** - Article/news management
- **bonus** - Event bonus configuration
- **category** - Content category management
- **common_configs** - System-wide configuration editor
- **configuration** - Feature toggles & privacy settings
- **content** - Content moderation, approval workflow
- **dashboard** - Admin overview & metrics
- **data** - Data management tools
- **event-statistic** - Event performance analytics
- **event** - Event CRUD & configuration
- **gifts** - Reward gift management
- **identification** - KYC verification & review
- **login** - Admin authentication
- **mission** - Seasonal mission management
- **news** - News feed administration
- **notification** - Admin notification center
- **partner** - Multi-tenant client configuration
- **quick-action** - Quick task templates
- **reconciliation** - Financial reconciliation
- **segment** - User segmentation & targeting
- **staff** - Staff account management
- **tag** - Content tag management
- **transfer** - Internal transfer management
- **user-partner** - User-partner associations
- **user** - User account management & KYC

## 5. Frontend Features (Creator-facing)

- **account** - Account management & settings
- **affiliate-campaign-detail** - Individual campaign details
- **affiliate-campaigns** - Affiliate campaign marketplace
- **affiliate-commission** - Commission tracking & history
- **affiliate-links** - Affiliate link generation
- **article** - Article browsing
- **bank** - Bank account linking
- **campaigns** - Event/campaign discovery
- **common-article** - General content articles
- **connect-tiktok** - TikTok OAuth connection
- **content** - Content submission & management
- **contract** - Contract viewing & signing
- **ekyc** - e-KYC verification flow
- **guide** - Onboarding & help guides
- **home** - Creator home/dashboard
- **identity-info** - Identity information management
- **login-tiktok** - TikTok login
- **main-home** - Main home page
- **notification** - Notification center
- **partner-home** - Partner-specific home
- **profile** - Creator profile
- **statistic** - Performance analytics
- **support** - Support & help resources
- **tax-code** - Tax ID management

## 6. Multi-tenant Architecture Notes

Ambassador là white-label platform cho nhiều client:

- **Partner routing**: Mỗi user có `partner` field (AppID) trong JWT token & database. Request được route dựa trên partner context.
- **Partner configuration**: `Partner` model chứa branding (logo, covers, slug), domain whitelist (`allowDomains`), budget allocation (BPP), leaderboard settings.
- **User-Partner association**: Model `UserPartner` + `User.partner` field cho multi-platform membership.
- **Tenant isolation**: `CommonConfigs` model có `partner` field để per-tenant settings. `Configurations` model cho global privacy settings.
- **Shared collections**: Một số collections (User, Content, Event) shared across partners, filtered bằng `partner` field. Khác Partner models như `Partner`, `UserPartner` là dedicated.

## 7. Key Ambassador-specific Features

- **Affiliate Program**: Full affiliate campaign management (campaign CRUD, link generation, commission tracking, bonus rules). Unique đến Ambassador.
- **Multi-tenant white-label**: Support nhiều client (Anker, HDBank, TPBank, VNPay...) với isolated configuration & branding (logo, domain, budget per partner).
- **Social Media Integration**: TikTok, YouTube, Instagram account linking (`UserSocial`, `UserSocialPartner`). Creator-facing feature.
- **Content Workflow**: Sophisticated content submission → review → approval/rejection cycle với hashtag checking, tag validation, manual flow override.
- **Event-Driven Rewards**: Events với complex reward rules (bonuses, thresholds, daily analytics). Có affiliate campaign mapping.
- **Financial Management**: Cashflow tracking (pending/rejected/completed), withdrawal processing, reconciliation, internal transfers, multi-bank support.
- **Creator KYC**: e-KYC verification (EKYC handler), identification documents, tracking OTP workflows.
- **Advanced Analytics**: Daily aggregation cho content, events, user events. Leaderboard support per partner.
- **Notification System**: Firebase push notifications với localization, app response formatting, custom options per notification type.
- **Mission/Seasonal Campaigns**: Seasonal missions & quick actions.
- **Gift Redemption**: User can redeem gifts từ earned points/cashflow.

