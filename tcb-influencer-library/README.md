# Techcombank Influencer Library

**Project:** Influencer Library cho Techcombank
**Date Created:** 2026-02-13
**Status:** Planning Phase

---

## 📁 Project Documents

### Core Documents
- **[prd-tcb-influencer-library-2026-02-13.md](prd-tcb-influencer-library-2026-02-13.md)** ⭐ **MAIN PRD**
  - 25 Functional Requirements
  - 10 Non-Functional Requirements
  - 6 Epics (59-87 stories estimated)
  - User personas, flows, dependencies

### Brainstorming Sessions
1. **[brainstorming-influencer-library-4sources-2026-02-13.md](brainstorming-influencer-library-4sources-2026-02-13.md)**
   - 4 data sources architecture
   - 3-tier system design (TCB → AT Core → Diso)
   - Scoring formula: Social 30% + Performance 40% + Ratings 20% + Completeness 10%

2. **[brainstorming-tcb-influencer-data-requirements-2026-02-13.md](brainstorming-tcb-influencer-data-requirements-2026-02-13.md)**
   - 138 data points across 12 categories
   - 3-tier data collection strategy (Tier 1: 28 fields, Tier 2: 38 fields, Tier 3: 60 fields)
   - Context-aware onboarding (TCB Portal vs Marketplace paths)

3. **[brainstorming-influencer-vs-profile-multi-account-2026-02-13.md](brainstorming-influencer-vs-profile-multi-account-2026-02-13.md)**
   - Multi-profile architecture (1 Influencer → Many Profiles)
   - Normalized database schema
   - 44% reduction in onboarding time

---

## 🎯 Project Overview

**Objective:** Xây dựng hệ thống Influencer Library cho phép Techcombank quản lý và kết nối với influencers trong chiến dịch marketing.

**Key Features:**
- ✅ Multi-profile support (1 influencer có nhiều social accounts)
- ✅ Progressive profiling (3-tier data collection)
- ✅ Context-aware onboarding (TCB Portal vs Marketplace)
- ✅ 4 data sources integration (Onboarding + Social Crawl + Performance + Brand Ratings)
- ✅ 3-tier architecture (TCB → AT Core → Diso Influence-Meter)

---

## 🏗️ Architecture Overview

```
┌─────────────────┐
│   Techcombank   │  Tenant-specific portal
│     Portal      │  (Brand + Influencer interfaces)
└────────┬────────┘
         │
         ├─ Push: Performance data (after campaign)
         ├─ Push: Brand ratings (after review)
         └─ Pull: Matched profiles (on-demand)
         │
┌────────▼────────┐
│    AT Core      │  Multi-tenant middleware
│   Middleware    │  (ID mapping, tenant isolation)
└────────┬────────┘
         │
         ├─ Push: TCB data → Diso
         └─ Pull: Matched profiles ← Diso
         │
┌────────▼────────┐
│  Diso Platform  │  Shared services
│ Influence-Meter │  (Matching engine, scoring, crawl)
└─────────────────┘
```

---

## 👥 User Personas

1. **Beauty Influencer** (Mai, 28 tuổi)
   - 150K followers Instagram
   - Làm content về beauty, skincare
   - Muốn hợp tác với thương hiệu finance

2. **Marketing Manager** (Lan, 35 tuổi)
   - Techcombank Marketing Department
   - Quản lý influencer campaigns
   - Tìm kiếm influencers phù hợp

3. **Finance Influencer** (Minh, 32 tuổi)
   - 80K followers YouTube
   - Chuyên về đầu tư, tài chính cá nhân
   - Muốn hợp tác với ngân hàng

4. **System Admin** (Hùng, 40 tuổi)
   - IT Administrator
   - Quản lý users, approve eKYC
   - Monitor system health

---

## 📊 Key Metrics

**Functional Requirements:**
- Must Have: 20 FRs
- Should Have: 5 FRs

**Epics Breakdown:**
- EPIC-01: Registration & Profile (15-20 stories)
- EPIC-02: Brand Discovery (12-18 stories)
- EPIC-03: Campaign Interaction (10-15 stories)
- EPIC-04: Data Integration (8-12 stories)
- EPIC-05: Admin & Compliance (6-10 stories)
- EPIC-06: UX & Interface (8-12 stories)

**Total Estimated Stories:** 59-87 stories

---

## 🚀 Implementation Plans

### Completed Plans
- ✅ [plans/20260212-1430-influencer-portal-week2](../../plans/20260212-1430-influencer-portal-week2/)
- ✅ [plans/20260212-1234-brand-influencer-menu](../../plans/20260212-1234-brand-influencer-menu/)

### Next Steps
1. **Architecture Design** ← YOU ARE HERE
2. **Sprint Planning** - Break epics into user stories
3. **Development** - Implement features by sprint
4. **Testing & QA**
5. **Deployment**

---

## 🔗 Related Systems

**Diso Platform:**
- `influencer-platform/influence-meter` - Matching engine, scoring
- `influencer-platform/social-crawler-profile` - Auto-fetch social metrics

**AT Core:**
- `accesstrade-projects/at-core` - Multi-tenant middleware, ID mapping

---

## 📝 Out of Scope (Phase 3)

Các tính năng này sẽ được implement ở phase sau:
- ❌ Brand campaign creation UI
- ❌ Brand review/rating UI
- ❌ Contract generation
- ❌ Payment processing
- ❌ Messaging/chat system
- ❌ Analytics dashboard
- ❌ Admin portal (full-featured)

---

## 📚 Reference Documents

**Architecture & Data:**
- [.bmad/influencer-library-4sources/ARCHITECTURE-SUMMARY.md](../../.bmad/influencer-library-4sources/ARCHITECTURE-SUMMARY.md)
- [.bmad/influencer-library-4sources/INDEX.md](../../.bmad/influencer-library-4sources/INDEX.md)

**Business Context:**
- [BUSINESS-CONTEXT.md](../../BUSINESS-CONTEXT.md)
- [ARCHITECTURE.md](../../ARCHITECTURE.md)

---

**Last Updated:** 2026-02-13
**Project Status:** PRD Complete → Architecture Design In Progress
