# Feature Matrix - Ambassador Platform 3 Portals

**Date:** 2026-02-06
**Purpose:** Cross-portal feature comparison và implementation priority

---

## Feature Comparison Matrix

| Feature Category | Influencer Portal | Brand Portal | Admin Portal | Priority |
|------------------|-------------------|--------------|--------------|----------|
| **Dashboard** | Personal metrics | Campaign overview | System health | P0 |
| **Profile Management** | ✅ Self-service | ❌ N/A | ✅ Pool management | P0 |
| **Campaign Discovery** | ✅ Marketplace browse | ✅ AI-powered search | ❌ N/A | P0 |
| **Campaign Management** | ✅ View invitations | ✅ Full CRUD | ✅ Monitor all | P0 |
| **Content Upload** | ✅ Upload & track | ❌ Review only | ❌ N/A | P0 |
| **Content Approval** | ❌ N/A | ✅ Approve/reject | ✅ Monitor queue | P0 |
| **AI Matching** | ❌ N/A | ✅ Full access | ❌ View results | P0 |
| **Demographics** | ✅ Submit own | ✅ View all | ✅ Manage pool | P1 |
| **Earnings/Payments** | ✅ Track & receive | ✅ Process & track | ✅ Monitor all | P0 |
| **Analytics** | ✅ Personal perf | ✅ Campaign ROI | ✅ Platform stats | P1 |
| **Messaging** | ✅ Chat with brands | ✅ Chat with inf. | ❌ Support only | P1 |
| **Contracts** | ✅ Sign contracts | ✅ Manage templates | ✅ Monitor all | P1 |
| **Booking** | ✅ Accept/decline | ✅ Full management | ✅ Monitor all | P0 |
| **TikTok Shop** | ❌ N/A | ✅ GMV tracking | ❌ View metrics | P2 |
| **Approval Workflow** | ❌ N/A | ❌ N/A | ✅ Full control | P0 |
| **Partner Management** | ❌ N/A | ❌ N/A | ✅ Full control | P0 |
| **Sync Management** | ❌ N/A | ❌ N/A | ✅ Full control | P0 |

---

## Screen Count by Portal

### Influencer Portal (12 screens)

**Tier 1 - Core (P0):**
1. Dashboard - Overview metrics
2. My Profile - Edit profile
3. Campaign Invitations - List invitations
4. Invitation Detail - View & accept
5. Upload Content - Submit for approval
6. Campaign Marketplace - Browse available
7. Earnings Overview - Track payments

**Tier 2 - Important (P1):**
8. Performance Dashboard - Personal analytics
9. Payment History - Transaction list
10. Messages - Chat with brands
11. Content Library - Manage assets
12. Settings - Profile settings

**Total:** 12 screens

---

### Brand Portal (18 screens)

**Tier 1 - Core (P0):**
1. Dashboard - Campaign overview
2. Create Campaign - 5-step wizard
3. AI Matching - Find influencers
4. Campaign Dashboard - Monitor active
5. Influencer Discovery - Search & filter
6. Booking Dashboard - Manage bookings
7. Content Approval - Review queue
8. Payment Queue - Process payments

**Tier 2 - Important (P1):**
9. Analytics - ROI reports
10. Influencer Profile - Detailed view
11. Messages - Chat with influencers
12. Contract Templates - Manage contracts
13. Campaign List - All campaigns
14. Budget Management - Track spend

**Tier 3 - Nice-to-have (P2):**
15. TikTok Shop GMV - Track live-stream
16. Campaign Reports - Export reports
17. Saved Searches - Quick filters
18. Settings - Brand settings

**Total:** 18 screens

---

### Admin Portal (15 screens)

**Tier 1 - Core (P0):**
1. Dashboard - System overview
2. AT Pool List - All influencers
3. Add Influencer - By URL/manual
4. Approval Queue - Pending submissions
5. Review Submission - Approve/reject
6. Partner List - All tenants
7. Create Partner - New tenant

**Tier 2 - Important (P1):**
8. Sync Dashboard - Monitor sync
9. Failed Syncs - Retry queue
10. Partner Detail - Tenant detail
11. API Key Management - Manage keys
12. Usage Analytics - Per partner
13. Bulk Import - CSV upload

**Tier 3 - Nice-to-have (P2):**
14. Settings - Platform config
15. Audit Logs - Activity logs

**Total:** 15 screens

---

## User Flow Matrix

| User Flow | Influencer | Brand | Admin | Complexity |
|-----------|------------|-------|-------|------------|
| **Registration & Onboarding** | ✅ Sign up → Profile setup → Approval | ✅ Contract → Login → Setup | ✅ Admin invite → Setup | Medium |
| **Campaign Discovery** | ✅ Browse marketplace → Apply | ✅ Create → AI match → Invite | ❌ N/A | High |
| **Accept Campaign** | ✅ View invitation → Sign contract | ❌ N/A | ❌ N/A | Low |
| **Upload Content** | ✅ Upload → Submit for review | ❌ N/A | ❌ N/A | Medium |
| **Approve Content** | ❌ N/A | ✅ Review → Approve/reject | ✅ Monitor queue | Medium |
| **Track Performance** | ✅ View personal analytics | ✅ View campaign analytics | ✅ View platform analytics | Low |
| **Process Payment** | ✅ Track earnings → Receive | ✅ Approve payments → Send | ✅ Monitor transactions | Medium |
| **Manage Pool** | ❌ N/A | ❌ N/A | ✅ Add → Sync → Approve | High |

---

## Component Reusability Matrix

| Component | Influencer | Brand | Admin | Design System |
|-----------|------------|-------|-------|---------------|
| **Button** | ✅ 50+ uses | ✅ 80+ uses | ✅ 60+ uses | `/components.css` |
| **Card** | ✅ Metric, campaign | ✅ Metric, inf. | ✅ Metric, pool | `/components.css` |
| **Score Card** | ❌ N/A | ✅ Matching scores | ✅ Pool stats | `/components.css` |
| **Table** | ✅ Payments, content | ✅ Influencers, content | ✅ Pool, partners | `/components.css` |
| **Form Input** | ✅ Profile, upload | ✅ Campaign wizard | ✅ Add influencer | `/components.css` |
| **Modal** | ✅ Invitation, contract | ✅ Matching, review | ✅ Approval, sync | `/components.css` |
| **Badge** | ✅ Platform, status | ✅ Match score, tier | ✅ Sync status | `/components.css` |
| **Chart** | ✅ Performance trends | ✅ Campaign ROI | ✅ Pool growth | Chart.js (new) |
| **Avatar** | ✅ Profile display | ✅ Influencer cards | ✅ User display | `/components.css` |
| **Toast** | ✅ Success, error | ✅ Success, error | ✅ Success, error | Custom (new) |
| **Skeleton** | ✅ Loading states | ✅ Loading states | ✅ Loading states | Custom (new) |
| **Progress Bar** | ✅ Upload progress | ✅ Campaign progress | ✅ Sync progress | `/components.css` |

---

## Data Flow Matrix

| Data Entity | Influencer | Brand | Admin | Source of Truth |
|-------------|------------|-------|-------|-----------------|
| **Influencer Profile** | ✅ Edit own | ✅ View all | ✅ Manage pool | AT Database |
| **Campaign** | ✅ View assigned | ✅ Full CRUD | ✅ View all | AT Database |
| **Booking** | ✅ Accept/decline | ✅ Manage all | ✅ Monitor all | AT Database |
| **Content** | ✅ Upload | ✅ Approve | ✅ Monitor | AT Database |
| **Payment** | ✅ Track earnings | ✅ Process | ✅ Monitor | AT Database |
| **Demographics** | ✅ Submit own | ✅ View all | ✅ Manage | Influence-Meter API |
| **Match Score** | ❌ N/A | ✅ View results | ✅ View results | Influence-Meter API |
| **Pool Sync** | ❌ N/A | ❌ N/A | ✅ Manage | VB API → AT DB |
| **Partner/Tenant** | ❌ N/A | ❌ N/A | ✅ Full CRUD | AT Database |

---

## API Integration Matrix

| API/Service | Influencer | Brand | Admin | Integration Type |
|-------------|------------|-------|-------|------------------|
| **Influence-Meter API** | ✅ Demographics submit | ✅ Matching, demographics | ✅ Pool enrichment | REST API |
| **AT Core API** | ✅ All operations | ✅ All operations | ✅ All operations | REST API |
| **ViewBoost API** | ❌ N/A | ❌ N/A | ✅ Sync influencers | REST API (via adapter) |
| **MoMo API** | ✅ Receive payments | ✅ Send payments | ✅ Monitor | REST API |
| **ZaloPay API** | ✅ Receive payments | ✅ Send payments | ✅ Monitor | REST API |
| **TikTok Shop API** | ❌ N/A | ✅ GMV tracking | ❌ View metrics | REST API |
| **WebSocket** | ✅ Notifications | ✅ Real-time updates | ✅ Sync status | WebSocket |
| **Upload Service** | ✅ Content upload | ❌ N/A | ❌ N/A | REST API + S3 |

---

## Permission Matrix

| Permission | Influencer | Brand | Admin | Partner Admin |
|------------|------------|-------|-------|---------------|
| **View Own Profile** | ✅ Full | ❌ N/A | ✅ All | ✅ Own tenant |
| **Edit Profile** | ✅ Own only | ❌ N/A | ✅ Pool profiles | ❌ Read-only |
| **Create Campaign** | ❌ No | ✅ Yes | ✅ Monitor | ✅ Own tenant |
| **View All Influencers** | ❌ No | ✅ Public pool | ✅ All | ✅ Own pool |
| **Approve Content** | ❌ No | ✅ Own campaigns | ✅ All campaigns | ✅ Own campaigns |
| **Process Payments** | ❌ No | ✅ Own campaigns | ✅ All | ✅ Own campaigns |
| **Manage Pool** | ❌ No | ❌ No | ✅ Full control | ❌ View only |
| **Approve Submissions** | ❌ No | ❌ No | ✅ Full control | ✅ Own submissions |
| **Manage Partners** | ❌ No | ❌ No | ✅ Full control | ❌ No |
| **View Analytics** | ✅ Personal | ✅ Own campaigns | ✅ Platform-wide | ✅ Own tenant |

---

## Implementation Priority

### Phase 1 - MVP (Month 2-3)

**Influencer Portal (P0):**
1. Dashboard
2. Profile Management
3. Campaign Invitations
4. Upload Content
5. Earnings Tracking

**Brand Portal (P0):**
1. Dashboard
2. Create Campaign Wizard
3. AI Matching
4. Campaign Dashboard
5. Content Approval
6. Payment Queue

**Admin Portal (P0):**
1. Dashboard
2. Pool Management
3. Approval Queue
4. Partner Management

**Estimated:** 20 screens, 8 weeks

---

### Phase 2 - Enhanced (Month 4-5)

**All Portals (P1):**
- Messaging system (WebSocket)
- Analytics dashboards
- Contract management
- Demographics submission
- Performance tracking

**Estimated:** 15 screens, 6 weeks

---

### Phase 3 - Advanced (Month 6+)

**Brand Portal (P2):**
- TikTok Shop integration
- Advanced analytics
- Saved searches
- Export reports

**Admin Portal (P2):**
- Audit logs
- Advanced settings
- Fraud detection

**Estimated:** 10 screens, 4 weeks

---

## Development Estimates

| Portal | Screens | Components | API Endpoints | Est. Time (weeks) |
|--------|---------|------------|---------------|-------------------|
| **Influencer Portal** | 12 | 18 | 15 | 6-8 weeks |
| **Brand Portal** | 18 | 25 | 25 | 10-12 weeks |
| **Admin Portal** | 15 | 22 | 20 | 8-10 weeks |
| **Shared Components** | - | 40+ | - | 2-3 weeks |
| **Total** | 45 | 65+ | 60+ | **20-25 weeks** |

**Team Recommendation:**
- 2 Backend developers
- 2 Frontend developers
- 1 UI/UX Designer
- 1 Product Manager
- 1 QA Engineer

---

## Success Metrics

### Influencer Portal
- Registration completion rate: >80%
- Time to first campaign accepted: <7 days
- Content upload success rate: >95%
- Payment processing time: <24 hours
- User satisfaction: >4.5/5

### Brand Portal
- Campaign creation time: <30 minutes
- AI matching acceptance rate: >70%
- Content approval time: <24 hours
- Campaign ROI: >10%
- Platform NPS: >50

### Admin Portal
- Approval queue processing time: <1 hour
- Sync success rate: >95%
- System uptime: >99.5%
- Support ticket resolution: <24 hours
- Admin efficiency: >100 profiles/day managed

---

**Document Owner:** UX Design Team
**Last Updated:** 2026-02-06
**Status:** Ready for Development Planning
