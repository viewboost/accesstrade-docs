# Pub2 Affiliate Integration - Documentation Index

**Project:** Pub2 Affiliate Integration for TCB/Ambassador/Vinfast
**Date:** 2026-02-07
**Status:** Architecture & Design Phase
**Partners:** Techcombank (TCB_001), Ambassador (AMB_001), Vinfast (VF_001)

---

## 📚 Document Index

### 0. [Executive Summary](./00-executive-summary.md) ⭐ **START HERE**
**Date:** 2026-02-07
**Type:** Business Overview
**Audience:** Product Owners, Business Stakeholders, Management

**Nội dung:**
- 📋 **Business Model:** 3 partners độc lập (TCB/AMB/VF)
- 💡 **User Journey:** Influencer & Admin workflows (non-technical)
- 🎯 **Value Propositions:** Cho influencers, platforms, merchants
- 🔒 **Data Privacy:** Tenant isolation giải thích đơn giản
- 🚀 **Rollout Plan:** 4 phases, 10 weeks timeline
- 📊 **Success Metrics:** Targets & KPIs
- 💼 **Business Q&A:** 5 câu hỏi quan trọng nhất
- 🎁 **Competitive Advantages:** So sánh với competitors
- ⚠️ **Risks & Mitigations:** Risk management

**Đọc document này TRƯỚC để hiểu tổng quan business & product.**

---

### 1. [Brainstorming Session](./01-brainstorming-session.md)
**Date:** 2026-02-07
**Type:** Brainstorming (SWOT, Mind Mapping, Starbursting)
**Duration:** ~45 minutes

**Nội dung:**
- SWOT Analysis (Strengths, Weaknesses, Opportunities, Threats)
- 5 Integration Models (từ simple → complex)
- Architecture Components chi tiết
- Multi-tenant Strategy
- Data Flow diagrams
- User Experience Scenarios
- Technical Challenges & Solutions
- Security & Compliance
- Monitoring & Analytics
- 7 Key Insights (P0 và P1)

**Key Outputs:**
- **Recommended Model:** API Proxy Model (4-6 tuần MVP)
- **Critical Insights:** 7 insights (4 P0, 3 P1)
- **Total Ideas:** 85+
- **Categories:** 10

---

### 2. [Architecture Decisions](./02-architecture-decisions.md)
**Date:** 2026-02-07
**Type:** Architecture Decision Record (ADR)
**Based on:** Brainstorming session + 3 băn khoăn chính

**Nội dung:**

#### Decision 1: Pub2 Partner Structure
- **Question:** Pub2 nên biết 3 partners (TCB, AMB, VF) hay chỉ 1 (at-core)?
- **Chosen:** 3 Separate Pub2 Partners
- **Rationale:** Clean source handover, billing independence, exit strategy
- **Implementation:** Phase-by-phase setup guide

#### Decision 2: User Balance & Transactions
- **Question:** Influencer join multiple tenants → Balance riêng hay chung?
- **Chosen:** Separate Balance per Tenant
- **Rationale:** White-label isolation, clear billing, no data leakage
- **Payout:** Strategy 1 (Separate) for MVP, Strategy 2 (Consolidated) future

#### Decision 3: Influencer Portal Display
- **Question:** TCB portal nên hiển thị gì?
- **Chosen:** Tenant-Isolated UI với 5 core components
- **Components:**
  1. Dashboard Overview
  2. Campaign Browser
  3. My Affiliate Links
  4. Affiliate Analytics
  5. Payout History
- **Branding:** White-label theming per tenant

**Code Examples:**
- Database schema (SQL)
- Service layer (TypeScript)
- Filtering logic
- Webhook handlers

---

### 3. [Admin Campaign Management](./03-admin-campaign-management.md)
**Date:** 2026-02-07
**Type:** Feature Specification
**Focus:** Campaign curation & admin workflows

**Nội dung:**

#### Problem Addressed
- Pub2 có 1000+ campaigns → Không thể auto-sync tất cả
- Risk hiển thị competitor campaigns (Vietcombank, BIDV, etc.)
- TCB cần full control over campaigns visible to influencers

#### Solution: Manual Curation Model
- **Admin Browse Pub2:** Search & filter campaigns from Pub2 API
- **Selective Addition:** Admin manually adds relevant campaigns only
- **Full Customization:** TCB controls title, description, images (Vietnamese)
- **Pub2 Linking:** Chỉ lưu `pub2_campaign_id` để link affiliate tracking
- **Brand Safety:** Competitor detection, category relevance checking

#### Core Workflows
1. **Add Campaign:** Browse Pub2 → Customize → Submit for approval → Publish
2. **Edit Campaign:** Update info, re-approval for major changes
3. **Approval Workflow:** Draft → Pending → Approved/Rejected/Changes Requested
4. **Bulk Operations:** Activate/deactivate multiple campaigns
5. **Pub2 Sync:** Background job checks if campaigns ended on Pub2

#### Data Models
```sql
campaigns (TCB's curated list)
  - title, description (TCB controls)
  - pub2_campaign_id (link to Pub2)
  - pub2_campaign_status (synced hourly)
  - status (draft/active/inactive)
  - featured, display_order

campaign_approvals (workflow)
  - requester_id, approver_id
  - status (pending/approved/rejected)
  - notes, changes_requested

campaign_sync_logs (audit trail)
campaign_metrics (performance analytics)
```

#### Admin UI Components
1. **Campaign List:** Main dashboard với filtering, bulk actions
2. **Browse Pub2:** Search Pub2 campaigns, competitor warnings
3. **Campaign Form:** Add/edit with rich text, image upload
4. **Approval Dashboard:** Pending approvals, review queue
5. **Analytics:** Performance metrics, top influencers

#### Security & Permissions
- **Editor:** Create, edit own drafts
- **Manager:** Approve campaigns, edit active campaigns
- **Admin:** Full control, bulk operations

**Code Examples:**
- Service layer (CampaignManagementService)
- Approval workflow logic
- Pub2 sync background job
- Permission middleware
- Analytics queries

---

### 4. [Pub2 Questions Response](./04-pub2-questions-response.md)
**Date:** 2026-02-07
**Type:** Q&A Document / Technical Response
**Audience:** Pub2 Team (AccessTrade)

**Nội dung:**

Trả lời chi tiết các câu hỏi từ Pub2 về integration, với references đến các documents đã phân tích.

#### Phần I: UI/UX & Action Flows
- ⏳ **TODO:** Cần bổ sung Figma mockups (high-fidelity)
- ✅ **Current:** Wireframes (ASCII) đã có trong docs
- References: 5 influencer pages, 4 admin pages

#### Phần II: Account Linking (Matching Tài khoản)
1. **Cơ chế liên kết:**
   - OAuth 2.0 flow (recommended)
   - Email/Phone/CCCD matching (fallback)
   - Database: `influencer_pub2_accounts` table

2. **Tính hợp pháp & GDPR:**
   - Explicit user consent required
   - OAuth 2.0 = industry standard
   - Data Processing Agreement
   - Right to deletion support

3. **Auto Onboarding:**
   - Matching algorithm (priority: Email → Phone → CCCD)
   - Verification flows (email code, SMS)
   - Edge cases handling (multiple matches, no match)

4. **SSO Brand Protection:**
   - Ambassador không muốn show "AccessTrade" branding
   - Solution: Tenant-branded OAuth domains
   - Alternative: Silent linking (backend only)

#### Phần III: Campaign Distribution
1. **Campaign Management:**
   - Manual curation model (NOT auto-sync)
   - TCB admin browse Pub2 → Select relevant → Customize → Publish
   - Competitor detection & warnings
   - Approval workflow

2. **Join Campaign Flow:**
   - Influencer browse → Generate link = "Join"
   - Backend: Call Pub2 API, store in `pub2_affiliate_links`
   - Track performance per link

3. **Data Isolation:**
   - **Critical:** Separate balance per tenant (sub_id_2 filtering)
   - TCB portal KHÔNG show Ambassador data
   - Ambassador portal KHÔNG show TCB data
   - Audit logging for security

4. **Metrics & Conversion:**
   - Funnel tracking: Total users → Linked → Generated links → Conversions
   - Current Ambassador: 40% link rate (target 50%)
   - Activation rate: 70% (target 80%)

**Code Examples:**
- Account linking service (OAuth + Email matching)
- Filtering queries (tenant isolation)
- Auto-match algorithm
- Stats aggregation

**Action Items:**
- Pub2: Confirm OAuth support, API endpoints, custom branding
- ViewBoost: Create Figma mockups, implement account linking
- Timeline: 10 weeks to production

---

## 🎯 Quick Summary (For Developers)

### Problem Statement
Techcombank/Ambassador/Vinfast platforms hiện có view-based reward system. Cần tích hợp affiliate marketing từ Pub2 để:
- Tăng revenue stream cho influencers (dual income)
- Monetize video content beyond views
- Competitive differentiation

### Recommended Solution

**Integration Model:** API Proxy Model
- at-core proxy Pub2 APIs
- Native UX, no external redirects
- Time-to-market: 4-6 tuần
- Clean source code ownership

**Architecture Highlights:**
- **3 Separate Pub2 Partners:** TCB, Ambassador, Vinfast có own API keys
- **Tenant Isolation:** Filter data via `sub_id_2` parameter
- **Dual Revenue Display:** View rewards + Affiliate commission
- **White-label UI:** Brand-specific theming per tenant

### Business Value

**For Influencers:**
- Dual income stream (views + affiliate)
- Relevant campaigns (filtered by tenant)
- Unified dashboard (clear metrics)
- Single platform for all earnings

**For Tenants (TCB, Vinfast):**
- Full control post-handover (own Pub2 account)
- White-label branding
- Campaign filtering (brand safety)
- Independent billing & reporting

**For AccessTrade:**
- Product differentiation
- Network effects (cross-tenant)
- Scalable multi-tenant model
- Clean IP ownership for source sales

### Key Metrics (Projected)

**MVP Timeline:** 12 weeks
- Phase 1: Foundation (4 weeks)
- Phase 2: Frontend (4 weeks)
- Phase 3: Testing & Deployment (4 weeks)

**Expected Impact:**
- Influencer retention: +30% (dual income appeal)
- Conversion rate: 4-6% (industry benchmark)
- Revenue per influencer: +40% (affiliate adds to views)

---

## 🏗️ Architecture Overview

### High-Level Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Pub2 System                          │
├─────────────────────────────────────────────────────────┤
│  Partner: TCB (TCB_001)      API Key: tcb_xxx          │
│  Partner: Ambassador (AMB_001) API Key: amb_xxx        │
│  Partner: Vinfast (VF_001)   API Key: vf_xxx           │
└────────────┬────────────────────────────────────────────┘
             │
             │ REST API calls (tenant-specific keys)
             │
┌────────────┴────────────────────────────────────────────┐
│              at-core Platform (API Proxy)               │
├─────────────────────────────────────────────────────────┤
│  • Pub2ApiClient (API wrapper)                         │
│  • Campaign filtering (whitelist/blacklist)            │
│  • Attribution logic (sub_id_1, sub_id_2, sub_id_3)    │
│  • Webhook handlers (clicks, conversions)              │
│  • Data aggregation (views + affiliate metrics)        │
└────────────┬────────────────────────────────────────────┘
             │
       ┌─────┴─────┬──────────┬──────────┐
       │           │          │          │
┌──────▼────┐ ┌────▼────┐ ┌──▼────┐ ┌──▼────────┐
│ TCB       │ │ AMB     │ │ VF    │ │ Future... │
│ Portal    │ │ Portal  │ │ Portal│ │           │
│ (Blue)    │ │ (Red)   │ │ (Navy)│ │           │
└───────────┘ └─────────┘ └───────┘ └───────────┘
```

### Data Flow (Campaign Discovery → Conversion)

```
1. Campaign Discovery
   Influencer (TCB) → at-core UI → Pub2 API (tcb_xxx key)
   → Filter (banking only) → Display

2. Link Generation
   Select campaign → at-core backend → Pub2 createLink API
   → Store (sub_id_1=video_id, sub_id_2=tcb)
   → Return link to influencer

3. Click Tracking
   User clicks link → Pub2 tracks → Webhook → at-core
   → Update pub2_click_events → Dashboard refresh

4. Conversion Tracking
   Purchase → Pub2 detects → Webhook → at-core
   → Verify tenant match (sub_id_2)
   → Update pub2_conversions → Notify influencer

5. Payout
   Influencer requests → at-core validates → TCB approves
   → TCB pays influencer → Update status
```

---

## 🔑 Key Design Decisions

### Decision Matrix

| Aspect | Options Considered | Chosen | Rationale |
|--------|-------------------|--------|-----------|
| **Pub2 Partner** | A) 3 separate<br>B) 1 shared | **A** | Clean handover, billing independence |
| **Balance Model** | A) Separate per tenant<br>B) Shared total | **A** | White-label, no data leak |
| **Payout** | A) Separate per tenant<br>B) Consolidated | **A (MVP)** | Simplicity, can evolve to B |
| **Integration** | Link-only, Widget, **API Proxy**, Deep, Blockchain | **API Proxy** | Balance effort/value |
| **Attribution** | Last-click, First-click, Multi-touch | **Last-click** | Standard, Pub2 default |

### Trade-offs Accepted

**✅ What we gained:**
- Clean source code ownership
- Tenant independence post-handover
- Data privacy compliance
- Flexible commercial terms

**⚠️ What we sacrificed:**
- Network effects across tenants (accepted for isolation)
- Single payout convenience (MVP only, can enhance)
- Setup simplicity (one-time cost, worth it)

---

## 📋 Implementation Checklist

### Phase 1: Foundation (Week 1-4)

- [ ] **Week 1-2: Pub2 Setup**
  - [ ] AT contacts Pub2 for 3 partner accounts
  - [ ] Pub2 provisions TCB_001, AMB_001, VF_001
  - [ ] API keys issued & tested in sandbox
  - [ ] Webhook endpoints configured

- [ ] **Week 3-4: Backend**
  - [ ] Database schema migration
  - [ ] Pub2ApiClient service
  - [ ] Tenant filtering logic (sub_id_2)
  - [ ] Webhook receivers (clicks, conversions)
  - [ ] Integration tests

**Deliverable:** Backend functional, tested in sandbox

---

### Phase 2: Frontend (Week 5-8)

- [ ] **Week 5-6: Core UI**
  - [ ] Dashboard overview component
  - [ ] Campaign browser (with filtering)
  - [ ] Affiliate link generator
  - [ ] White-label theming system

- [ ] **Week 7-8: Analytics & Payout**
  - [ ] Analytics dashboard (CTR, CVR, charts)
  - [ ] Payout request flow
  - [ ] Payout history view
  - [ ] Notification system

**Deliverable:** Full UI functional, ready for UAT

---

### Phase 3: Testing & Deployment (Week 9-12)

- [ ] **Week 9-10: UAT**
  - [ ] UAT with TCB stakeholders
  - [ ] UAT with Ambassador team
  - [ ] Bug fixes & refinements
  - [ ] Performance optimization (load testing)

- [ ] **Week 11: Production**
  - [ ] TCB production deployment
  - [ ] Ambassador production deployment
  - [ ] Monitoring dashboards (Datadog/NewRelic)
  - [ ] Alerting rules configured

- [ ] **Week 12: Handover (TCB)**
  - [ ] Source code transfer to TCB repo
  - [ ] Pub2 API credentials transfer
  - [ ] Training for TCB engineers (2 sessions)
  - [ ] Support SLA activation

**Deliverable:** TCB operates independently

---

### Phase 4: Enhancements (Month 4-6)

- [ ] AI campaign recommendations
- [ ] Advanced fraud detection (ML models)
- [ ] Consolidated payout (Strategy 2)
- [ ] A/B testing framework
- [ ] Mobile app integration

---

## 🔒 Security & Compliance

### API Key Management
- **Storage:** KMS encryption (AWS KMS, GCP Secret Manager)
- **Access:** Tenant-isolated credentials
- **Rotation:** Admin UI with 24h grace period
- **Audit:** All key accesses logged

### Fraud Prevention
1. **Rate Limiting:** 100 clicks/day per link
2. **Pattern Detection:** CTR > 50% → Flag
3. **IP Diversity:** < 30% unique IPs → Flag
4. **Self-Clicking:** > 5 clicks from influencer → Flag
5. **Manual Review:** Queue for flagged links
6. **Pub2 Detection:** Trust Pub2's fraud systems

### Compliance
- **Affiliate Disclosure:** Auto-insert FTC/ASA templates
- **Data Privacy:** GDPR/PDPA consent & retention
- **Tax Reporting:** W-9/1099 support (US), equivalent for Vietnam
- **Audit Trails:** All transactions logged immutably

---

## 📊 Monitoring & Alerts

### Key Metrics

**System Health:**
- Pub2 API uptime: Target 99%+
- Webhook delivery rate: Target 95%+
- Sync lag: Target < 30 min

**Business Metrics:**
- Total affiliate revenue (per tenant)
- Top influencers by commission
- Top campaigns by conversion rate
- Average CTR, CVR, AOV

**Alerts:**
```yaml
- Pub2 API down (Critical → PagerDuty)
- Webhook delivery < 90% (Warning → Slack)
- Sync lag > 2 hours (Warning → Email)
- Fraud pattern detected (Warning → Slack)
- Payout request pending > 7 days (Warning → Email)
```

---

## 🧪 Testing Strategy

### Test Coverage

1. **Unit Tests:**
   - Service layer (Pub2ApiClient)
   - Filtering logic (tenant isolation)
   - Attribution logic (sub_id extraction)
   - Coverage target: 80%+

2. **Integration Tests:**
   - Pub2 API calls (sandbox)
   - Webhook handling (end-to-end)
   - Database transactions
   - Coverage: All critical paths

3. **E2E Tests:**
   - Campaign discovery flow
   - Link generation → Click → Conversion
   - Payout request flow
   - Coverage: Happy paths + key edge cases

4. **Load Tests:**
   - 1000+ concurrent influencers
   - 10,000+ API calls/hour
   - Webhook burst (100 events/sec)

---

## 📚 Additional Resources

### External Documentation
- [Pub2 API Documentation](https://docs.pub2.vn) (assumed URL)
- [BUSINESS-CONTEXT.md](../../BUSINESS-CONTEXT.md) - Ownership model
- [at-core Architecture](../architecture/) - Platform overview

### Internal References
- Database Schema: See [02-architecture-decisions.md](./02-architecture-decisions.md#database-schema)
- Service Layer: See [02-architecture-decisions.md](./02-architecture-decisions.md#service-layer-example)
- UI Components: See [02-architecture-decisions.md](./02-architecture-decisions.md#ui-component-specifications)

### Runbooks
- [ ] Pub2 API Key Rotation (TODO)
- [ ] Webhook Failure Recovery (TODO)
- [ ] Data Reconciliation (TODO)
- [ ] Fraud Investigation (TODO)

---

## 🤝 Stakeholders

### Internal (ViewBoost)
- **Engineering:** Backend, Frontend, DevOps teams
- **QA:** UAT coordination, test execution
- **Product:** Requirements, prioritization

### External
- **AccessTrade:**
  - Leadership: Business alignment
  - Engineering: Technical coordination
  - Finance: Billing & invoicing setup

- **Techcombank:**
  - Stakeholders: UAT, requirements validation
  - Engineering: Training, handover acceptance

- **Pub2:**
  - Account Manager: Partner setup
  - Support: Technical integration support

---

## 📞 Support & Escalation

### Support Tiers

**Tier 1: Influencer Support**
- Channel: In-app chat, email
- SLA: 24h response
- Scope: Basic questions, payout status

**Tier 2: Tenant Support (TCB, AMB, VF)**
- Channel: Dedicated Slack, email
- SLA: 4h response (business hours)
- Scope: Configuration, reporting, troubleshooting

**Tier 3: Engineering Escalation**
- Channel: PagerDuty (critical), JIRA
- SLA: 1h response (critical), 24h (normal)
- Scope: Bugs, outages, data issues

**Tier 4: Pub2 Escalation**
- Channel: Via AT account manager
- SLA: Per Pub2 SLA
- Scope: API issues, billing disputes

---

## 🚀 Next Steps

### Immediate Actions (Week 1)

1. **Stakeholder Validation:**
   - [ ] Present architecture to AT leadership
   - [ ] Review with TCB stakeholders
   - [ ] Confirm Pub2's capability for 3 partners

2. **Project Kickoff:**
   - [ ] Form cross-functional team
   - [ ] Setup project tracking (JIRA)
   - [ ] Initialize GitHub repo branches

3. **Pub2 Coordination:**
   - [ ] AT initiates partner account requests
   - [ ] Collect business details (TCB, AMB, VF)
   - [ ] Schedule Pub2 onboarding calls

### Short-term (Month 1)

- Complete Phase 1 (Foundation)
- First UAT session with AT internal team
- Update documentation based on learnings

### Mid-term (Month 2-3)

- Complete Phase 2 (Frontend)
- UAT with TCB stakeholders
- Production deployment preparation

### Long-term (Month 4-6)

- TCB source code handover
- Phase 4 enhancements
- Ambassador/Vinfast rollout

---

## 📝 Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-02-07 | Initial brainstorming & architecture decisions | ViewBoost Team |
| 2026-02-07 | Documentation index created | ViewBoost Team |
| TBD | Stakeholder validation results | TBD |
| TBD | Phase 1 implementation start | TBD |

---

## 📄 Document Metadata

**Project:** AccessTrade at-core - Pub2 Affiliate Integration
**Phase:** Architecture & Design
**Status:** Awaiting Stakeholder Validation
**Owner:** ViewBoost Engineering
**Last Updated:** 2026-02-07
**Next Review:** After stakeholder sign-off

---

**For questions or feedback, contact:**
- Engineering Lead: [TBD]
- Product Owner: [TBD]
- AT Liaison: [TBD]
