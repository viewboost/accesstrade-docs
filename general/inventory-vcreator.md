# vCreator — Feature Inventory

> Generated: 2026-05-07. Evidence-based scan từ source code.

## 1. Backend Services

| Service | Mô tả | Loại | Path |
|---------|------|------|------|
| audit | Audit log tracking cho admin actions | Core | backend/internal/service/audit.go |
| cashflow | Quản lý dòng tiền (cash flow) trong hệ thống | Core | backend/internal/service/cashflow.go |
| content | Xử lý nội dung, status change, hash tag check, image upload | vCreator-specific | backend/internal/service/content.go |
| content_analytic_daily | Analytics hàng ngày cho nội dung | vCreator-specific | backend/internal/service/content_analytic_daily.go |
| content_flow | Luồng xử lý nội dung (approval workflow) | vCreator-specific | backend/internal/service/content_flow.go |
| event | Quản lý sự kiện, reward, thống kê | Core | backend/internal/service/event.go |
| event_schema | Schema cho tracking events, tag định nghĩa | vCreator-specific | backend/internal/service/event_schema.go |
| notification | Gửi/quản lý thông báo cho users | Core | backend/internal/service/notification.go |
| otp | Xác thực OTP (2FA) | Core | backend/internal/service/otp.go |
| registry_match | Match engine cho admin import V2, single lookup hook | vCreator-specific | backend/internal/service/registry_match.go |
| staff | Helper methods cho staff system (root account) | vCreator-specific | backend/internal/service/staff.go |
| user | User management, registration, profile | Core | backend/internal/service/user.go |
| user_social | Quản lý social accounts (TikTok, etc.) | vCreator-specific | backend/internal/service/user_social.go |
| video | Xử lý video, transcoding, analytics | vCreator-specific | backend/internal/service/video.go |
| withdraw | Quản lý rút tiền (withdrawal) | Core | backend/internal/service/withdraw.go |

**Tổng: 15 services (8 vCreator-specific, 7 Core)**

---

## 2. Backend Models (MongoDB Collections)

### Financial & Banking
- bank.go — Danh sách ngân hàng
- bank_branch.go — Chi nhánh ngân hàng
- cash_flow.go — Lịch sử dòng tiền
- transfer.go — Transfers giữa các parties
- user_bank_card.go — Thẻ ngân hàng của user
- withdraw.go — Lịch sử rút tiền
- reconciliation.go, reconciliation_history.go, reconciliation_item.go — Đối chiếu tài khoản

### Campaign & Events (vCreator-specific)
- event.go — Sự kiện (campaign)
- event_bonus.go — Bonus structure của event
- event_reward.go, event_reward_temp.go — Phần thưởng
- event_analytic_daily.go — Thống kê daily của event
- event_schema.go — Schema cho tracking events

### Content (vCreator-specific)
- content.go — Bài viết/video content
- content_analytic_daily.go — Analytics daily cho content
- content_callback.go — Webhook callbacks
- content_crawl_history.go — Lịch sử crawl nội dung
- content_flow.go — Workflow approval
- content_flow_backup.go — Backup của flow
- content_manual_flow.go — Manual flow override
- content_transcript.go — Transcript/metadata của content
- video.go — Video-specific metadata
- article.go — Article/news content
- cover.go — Cover images

### User Management
- user.go — User core data
- user_device.go — Thiết bị của user
- user_social.go — Social accounts (TikTok, etc.)
- user_event.go — User participation trong event
- user_event_analytic_daily.go — User-event analytics
- user_event_schema_tracking.go — User event tracking schema
- user_partner.go — User-partner relationships
- user_publisher.go — Publisher/creator info
- user_segment.go — User segmentation
- user_income_month.go — Monthly income tracking

### Admin & Operations
- staff.go — Admin staff accounts
- role.go — Role-based access control
- employee_registry.go — Employee registry
- audit.go — Audit logs
- admin_notification.go — Admin notifications
- notification.go — General notifications

### Identification & Verification
- identification.go — ID verification (KYC)
- tracking_identification.go — Tracking ID verification
- tracking_request_otp.go — OTP request tracking

### Tags & Metadata
- tag.go — Tags cho content/events
- segment.go — User segments
- quick_action.go — Quick actions

### System & Configuration
- configurations.go — System configurations
- session.go — User sessions
- otp.go — OTP records
- file.go — File metadata
- common.go — Common fields/enums

### Content Platform Specific
- news.go — News/blog articles
- news_views.go — News view counts
- article_view.go — Article view counts
- partner.go — Partner/brand info
- country.go, province.go — Location data

### Workplace (Multi-tenant)
- workplace_brand.go — Brand workspace
- workplace_company.go — Company workspace
- workplace_unit.go — Unit workspace

### Import & Export
- import_history.go — Import batch history
- export.go — Export jobs

**Tổng: 68 models**

---

## 3. Backend HTTP Routes (high-level)

**Route Groups (Admin)** — from `/pkg/admin/router/router.go`:

| Group | Path Prefix (inferred) | Purpose |
|-------|------------------------|---------|
| common | `/api/admin/common/*` | Common endpoints (auth, config) |
| staff | `/api/admin/staff/*` | Staff/admin account management |
| event | `/api/admin/event/*` | Event creation, management, analytics |
| content | `/api/admin/content/*` | Content moderation, status change |
| user | `/api/admin/user/*` | User management, profiles |
| article | `/api/admin/article/*` | Article/news management |
| eventSchema | `/api/admin/event-schema/*` | Event tracking schema config |
| reconciliation | `/api/admin/reconciliation/*` | Financial reconciliation |
| export | `/api/admin/export/*` | Data export jobs |
| identification | `/api/admin/identification/*` | KYC verification |
| transfers | `/api/admin/transfer/*` | Transfer management |
| news | `/api/admin/news/*` | News publishing |
| partner | `/api/admin/partner/*` | Partner/brand management |
| workplace | `/api/admin/workplace/*` | Workplace (brand/company/unit) |
| quickAction | `/api/admin/quick-action/*` | Quick action templates |
| role | `/api/admin/role/*` | Role & permission config |
| segment | `/api/admin/segment/*` | User segment management |
| userSegment | `/api/admin/user-segment/*` | User-segment assignment |
| adminNotification | `/api/admin/notification/*` | Admin notifications |
| contentManualFlow | `/api/admin/content-manual-flow/*` | Manual content flow override |
| audit | `/api/admin/audit/*` | Audit log queries |
| tag | `/api/admin/tag/*` | Tag management |
| migration | `/api/admin/migration/*` | Data migration tools |
| eventReward | `/api/admin/event-reward/*` | Reward structure config |
| eventBonus | `/api/admin/event-bonus/*` | Bonus structure config |
| employeeRegistry | `/api/admin/employee-registry/*` | Employee registry management |

**Other Servers**:
- `/public/*` — Public API (creator-facing, registration, social auth)
- `/file/*` — File upload/download service

**Tổng: 24 route groups**

---

## 4. Admin Features (pages)

| Page | Mô tả |
|------|------|
| article | Article/news management và publication |
| bonus | Event bonus structure configuration |
| configuration | System configuration & settings |
| content | Content moderation, status change, analytics |
| dashboard | Admin dashboard & overview |
| data | Data management & import/export |
| department | Department/organizational structure |
| employee-registry | Employee registry & staff registry |
| event-statistic | Event statistics & analytics |
| event | Event creation, management, rewards |
| identification | KYC verification & identification |
| login | Admin login page |
| news | News publishing & management |
| notification | Notification management |
| partner | Partner/brand management |
| quick-action | Quick action templates |
| reconciliation | Financial reconciliation |
| segment | User segment management |
| staff | Staff/admin account management |
| tag | Tag management |
| transfer | Transfer management |
| user-partner | User-partner relationship management |
| user | User management & profile editing |

**Tổng: 23 admin pages**

---

## 5. Frontend Features (frontend-green/)

| Page | Mô tả |
|------|------|
| 404 | Not found error page |
| account | Tài khoản settings & profile |
| article | Article/blog reading & browsing |
| bank | Ngân hàng/thanh toán settings |
| bonus | Bonus & reward viewing |
| common-article | Shared article components/layouts |
| connect-tiktok | TikTok account connection flow |
| content | Creator's content management dashboard |
| contract | Contract viewing & management |
| guide | Help/guide/tutorial content |
| home | Creator home page |
| login-tiktok | TikTok login/authentication |
| main-home | Main landing page |
| notification | Notification center & inbox |
| partner-home | Partner/brand collaboration page |
| profile | Creator profile viewing & editing |
| statistic | Content & earnings statistics |

**Tổng: 17 creator-facing pages**

---

## 6. Key vCreator-specific Modules

Những feature ĐẶC TRƯNG vCreator (không có ở TCB/Ambassador):

- **Content Management & Workflow** — Full content moderation pipeline (content.go, content_flow.go, content_flow_backup.go) với status tracking, hash tag validation, image upload. Admin interface cho content approval/rejection.

- **TikTok Social Integration** — user_social.go + connect-tiktok/login-tiktok pages cho phép creators link TikTok accounts và import content từ platform.

- **Video Processing & Analytics** — video.go service + video-related models (content_transcript.go, video analytics) cho transcoding, metadata extraction, performance tracking.

- **Creator Dashboard & Statistics** — Real-time statistic pages (frontend-green/src/pages/statistic/, event_analytic_daily, content_analytic_daily, user_event_analytic_daily) theo dõi views, engagement, earnings.

- **Registry Match Engine** — registry_match.go specialized service cho admin import V2 (bulk user matching by code/phone) + single lookup hook cho public registration. Core algorithm không tìm thấy ở TCB/Ambassador.

- **Event-driven Reward System** — Sophisticated event schema (event_schema.go) + event tracking (user_event_schema_tracking.go) cho flexible event configuration, bonus tiers (event_bonus.go), dynamic reward calculation.

- **Staff System** — staff.go service + root account model (StaffRaw) cho system automation tasks, audit trail integration (audit.go, admin_notification.go).

- **Content Analytics & Insights** — Dedicated daily analytics services (content_analytic_daily.go, event_analytic_daily.go, user_event_analytic_daily.go) với granular tracking.

- **Partner/Brand Collaboration** — partner.go model + dedicated admin page/routes cho brand partnerships, likely sponsor relationships.

- **Multi-tenant Workplace** — workplace_brand.go, workplace_company.go, workplace_unit.go models + admin routes cho organizational hierarchy, workspace isolation.

---

## Evidence Map

- Backend services: `/Users/vinhnguyen/workspaces/diso/accesstrade-projects/vcreator/backend/internal/service/`
- Models: `/Users/vinhnguyen/workspaces/diso/accesstrade-projects/vcreator/backend/internal/model/mg/`
- Admin routes: `/Users/vinhnguyen/workspaces/diso/accesstrade-projects/vcreator/backend/pkg/admin/router/router.go`
- Admin pages: `/Users/vinhnguyen/workspaces/diso/accesstrade-projects/vcreator/admin/src/pages/`
- Frontend pages: `/Users/vinhnguyen/workspaces/diso/accesstrade-projects/vcreator/frontend-green/src/pages/`

