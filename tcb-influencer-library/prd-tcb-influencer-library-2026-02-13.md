# Product Requirements Document: Influencer Library @ Techcombank

**Project:** Influencer Library & Matching System
**Client:** Techcombank (TCB)
**Document Version:** 1.0
**Date:** 2026-02-13
**Status:** Draft for Review
**Owner:** Product Manager

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-13 | Product Manager | Initial PRD creation |

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Business Objectives](#business-objectives)
3. [Success Metrics](#success-metrics)
4. [User Personas](#user-personas)
5. [Functional Requirements](#functional-requirements)
6. [Non-Functional Requirements](#non-functional-requirements)
7. [Epics](#epics)
8. [User Flows](#user-flows)
9. [Dependencies](#dependencies)
10. [Assumptions](#assumptions)
11. [Out of Scope](#out-of-scope)
12. [Open Questions](#open-questions)
13. [Stakeholders](#stakeholders)
14. [Appendices](#appendices)

---

## Executive Summary

Techcombank (TCB) cần một **Influencer Library** để quản lý influencers và tạo campaigns marketing cho các sản phẩm tài chính (credit cards, savings accounts, loans, investment products).

### Current State
- TCB hiện KHÔNG có hệ thống quản lý influencers
- Marketing teams phải quản lý influencers thủ công qua Excel/email
- Không có cách để match influencers phù hợp cho campaigns
- Không track được performance của influencer campaigns

### Proposed Solution
Xây dựng **Influencer Library System** với 3 portals:
1. **Influencer Portal:** Influencers tự đăng ký, quản lý profiles, view campaigns, submit deliverables
2. **Brand Portal:** TCB marketing team browse influencers, create campaigns, review submissions
3. **Admin Portal:** System admins approve influencers, manage system settings

### Key Features
- **Multi-Profile Support:** 1 influencer có thể có nhiều social accounts (Instagram, Facebook, TikTok, etc.)
- **4 Data Sources Integration:**
  - Source 1: Influencer onboarding form (self-reported data)
  - Source 2: Social media crawl (Diso Influence-Meter API)
  - Source 3: Campaign performance tracking
  - Source 4: Brand ratings & reviews
- **Intelligent Matching:** Match influencers to campaigns dựa trên audience demographics, content niche, finance affinity, past performance
- **3-Tier Architecture:** TCB → AT Core (middleware) → Diso (Influence-Meter API)

### Project Scope
- **Phase 1 (Current):** Influencer Portal (profile detail, profile list, submission)
- **Phase 2 (Current):** Brand Portal (influencer browsing, search, filters)
- **Phase 3 (Future PRD):** Brand Portal (campaign creation, review, ratings) - **Out of scope for this PRD**
- **Phase 4 (Future):** Admin Portal (approvals, system management)

### Timeline
- **Week 1-2 (Completed):** Influencer Portal foundation
- **Week 3-4 (In Progress):** Brand Portal influencer browsing
- **Week 5+:** Additional features per roadmap

---

## Business Objectives

### Primary Objectives

**OBJ-01: Reduce Campaign Setup Time**
- **Current:** 2-3 weeks to manually find and contact influencers
- **Target:** <3 days to create campaign and match influencers
- **Metric:** Average time from campaign idea to influencer outreach

**OBJ-02: Improve Influencer Match Quality**
- **Current:** 40% of campaigns use mismatched influencers (wrong audience)
- **Target:** 80% of campaigns have audience-product fit score >80/100
- **Metric:** Campaign ROI, conversion rate vs industry benchmarks

**OBJ-03: Centralize Influencer Data**
- **Current:** Influencer data scattered across Excel files, emails, personal contacts
- **Target:** 100% influencer data in centralized system
- **Metric:** Number of influencers registered, data completeness %

**OBJ-04: Enable Data-Driven Decisions**
- **Current:** Cannot compare influencer performance, no historical data
- **Target:** Track and compare influencer performance across campaigns
- **Metric:** % of campaigns with performance data tracked

### Secondary Objectives

**OBJ-05: Build Influencer Ecosystem for Finance Products**
- Attract influencers interested in promoting financial products
- Create TCB-certified finance influencer program
- **Metric:** Number of influencers with high finance affinity score (>75/100)

**OBJ-06: Improve Brand-Influencer Collaboration**
- Streamline communication between TCB marketing teams and influencers
- Transparent campaign brief → submission → review → payment workflow
- **Metric:** Influencer satisfaction score, repeat collaboration rate

**OBJ-07: Compliance & Brand Safety**
- Ensure all influencers comply with SBV regulations (age 18+, disclosure tags)
- Prevent inappropriate influencers from promoting financial products
- **Metric:** 100% compliance rate, zero regulatory violations

---

## Success Metrics

### Product Metrics

| Metric | Current | 3-Month Target | 6-Month Target | Measurement |
|--------|---------|----------------|----------------|-------------|
| **Influencers Registered** | 0 | 200 | 500 | System count |
| **Profile Completion Rate** | N/A | 70% (Tier 1+2) | 85% | Avg completion % |
| **Campaigns Created** | 0 | 20 | 50 | System count |
| **Influencer-Campaign Matches** | 0 | 100 | 300 | System count |
| **Campaign ROI** | Unknown | Baseline | +20% vs manual | Revenue/Cost |
| **Time to Match** | 2-3 weeks | <3 days | <1 day | Avg time |

### User Engagement Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Influencer Login Frequency** | >1x per week (active influencers) | Google Analytics |
| **Profile Update Frequency** | 90% updated quarterly | System logs |
| **Campaign Application Rate** | >30% of targeted influencers apply | System count |
| **Submission On-Time Rate** | >80% submitted by deadline | System count |

### Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **System Uptime** | 99.5% | Monitoring |
| **API Response Time** | <300ms (p95) | APM tools |
| **Page Load Time** | <2s (influencer portal) | Web Vitals |
| **Data Accuracy** | >95% (vs actual social metrics) | Diso crawl validation |

---

## User Personas

### Persona 1: Beauty Influencer (Primary User - Influencer Portal)

**Name:** Nguyễn Văn Hoa ("Beauty Queen")
**Age:** 28
**Occupation:** Full-time content creator
**Platforms:** Instagram (500K), Facebook (200K), TikTok (1M)
**Income:** 50-100M VND/month from influencer campaigns

**Goals:**
- Find legitimate brand partnerships (especially premium brands like TCB)
- Showcase her work to attract more campaigns
- Get paid fairly and on-time
- Build long-term relationships with brands

**Pain Points:**
- Too many scam "brand partnerships" → wastes time
- Complex onboarding forms → abandons if >15 minutes
- Unclear campaign requirements → delivers wrong content
- Payment delays → cash flow problems

**Tech Savvy:** High (uses social media all day, comfortable with apps)

**Behaviors:**
- Checks phone 50+ times/day
- Responds to DMs within 1 hour
- Prefers mobile over desktop (80% mobile usage)
- Visual person (screenshots > reading documentation)

**Needs from Influencer Library:**
- **Fast onboarding:** <10 minutes to register
- **Clear campaign briefs:** Know exactly what's expected
- **Easy submission:** Upload content with 1-click
- **Transparent payment:** See payment status anytime

---

### Persona 2: Marketing Manager (Primary User - Brand Portal)

**Name:** Trần Thị Lan
**Age:** 35
**Occupation:** Senior Marketing Manager @ TCB
**Department:** Digital Marketing
**Experience:** 8 years in marketing, 3 years at TCB

**Goals:**
- Launch 10+ influencer campaigns per quarter for TCB products
- Find influencers who genuinely resonate with TCB brand values
- Track campaign ROI to justify influencer marketing budget
- Scale influencer program from 20 → 200 influencers

**Pain Points:**
- Manually searching Instagram/Facebook for hours to find influencers
- No way to verify influencer audience demographics (rely on screenshots)
- Difficult to compare influencers (Excel spreadsheets)
- Cannot track which influencers perform best

**Tech Savvy:** Medium-high (uses Google Analytics, Meta Ads Manager, Excel)

**Behaviors:**
- Spends 60% time on campaign planning, 40% execution
- Data-driven (wants metrics for every decision)
- Busy (manages 5+ campaigns simultaneously)
- Prefers dashboards over raw data

**Needs from Influencer Library:**
- **Smart filters:** Find influencers by audience age, location, niche, finance affinity
- **Quick comparison:** Side-by-side comparison of 3-5 influencers
- **Performance data:** See past campaign results, engagement rates
- **Batch operations:** Select 10 influencers → send campaign invites with 1 click

---

### Persona 3: Finance-Focused Influencer (Secondary User - Influencer Portal)

**Name:** Lê Văn Minh ("Finance Guru")
**Age:** 32
**Occupation:** Part-time influencer + Full-time financial advisor
**Platforms:** LinkedIn (50K), Instagram (300K), YouTube (100K subscribers)
**Niche:** Personal finance education

**Goals:**
- Monetize finance expertise through influencer campaigns
- Partner with reputable financial institutions (banks, investment firms)
- Educate followers on smart money management
- Build credibility in finance industry

**Pain Points:**
- Most influencer platforms focus on beauty/fashion → no finance campaigns
- Brands don't understand his audience (professionals 30-45, high income)
- Long-form content (YouTube videos) not valued by brands who only want Instagram posts

**Finance Knowledge:** Advanced (certified financial advisor)

**Needs from Influencer Library:**
- **Finance-specific campaigns:** Credit cards, investment products, loans
- **Credibility building:** Showcase certifications, finance content portfolio
- **Multi-platform support:** Link LinkedIn + IG + YouTube (different audiences)
- **Educational content:** Brands allow him to educate (not just promote)

---

### Persona 4: System Administrator (Tertiary User - Admin Portal)

**Name:** Phạm Văn Nam
**Age:** 40
**Occupation:** IT Manager @ TCB
**Department:** IT Operations

**Goals:**
- Ensure system uptime (99.5% SLA)
- Manage user permissions (who can access what)
- Monitor system health, troubleshoot issues
- Approve influencer registrations (compliance check)

**Pain Points:**
- Limited time for manual approvals (500 influencers × 5 mins each = 40 hours)
- Need audit trails for compliance (SBV regulations)
- Security concerns (credential leaks, data breaches)

**Needs from Influencer Library:**
- **Automated approvals:** Auto-approve if eKYC passes + no red flags
- **Audit logs:** Track all user actions (GDPR compliance)
- **Role-based access:** Granular permissions per user role
- **Monitoring dashboard:** System health at a glance

---

## Functional Requirements

### EPIC-01: Influencer Registration & Profile Management

#### FR-001: Influencer Account Creation

**Priority:** Must Have

**Description:**
Influencers phải có khả năng tạo account mới thông qua influencer portal. System cần support 2 onboarding paths:
- **Path A (TCB Portal Direct):** Influencer đến trực tiếp `tcb.influencer.vn` → Full Tier 1 registration required
- **Path B (Marketplace):** Influencer browse campaigns trước → Minimal registration (name, email, 1 social account) → Complete profile when applying

**Acceptance Criteria:**
- [ ] Registration form có 3-step flow với auto-save mỗi step
- [ ] Tier 1 Essential fields (28 fields) bắt buộc cho Path A
- [ ] Minimal fields (4 fields: name, email, phone, 1 social) cho Path B
- [ ] Email verification via OTP (6-digit code, expires 10 minutes)
- [ ] Phone verification via SMS OTP
- [ ] eKYC integration (National ID upload + selfie + liveness detection)
- [ ] Age 18+ validation from DOB
- [ ] Duplicate email/phone detection (prevent multiple accounts)
- [ ] Progress saved automatically (can resume later)
- [ ] Compliance checkboxes (age 18+, right to work, data privacy, T&C)

**Dependencies:** None

**Related User Stories:**
- As an influencer, I want to create an account in <10 minutes so that I can start browsing campaigns quickly
- As an influencer, I want to save my progress and resume later so that I don't lose my data if I get interrupted

---

#### FR-002: Multi-Profile Support (1 Influencer → Many Social Accounts)

**Priority:** Must Have

**Description:**
System phải support 1 influencer có nhiều social profiles (Instagram, Facebook, TikTok, YouTube, LinkedIn). Personal data (name, DOB, bank account, compliance) chỉ nhập 1 lần, shared across all profiles. Profile-specific data (platform, handle, followers, content strategy, pricing) nhập riêng cho mỗi profile.

**Acceptance Criteria:**
- [ ] Database schema: `influencers` table (person-level) + `social_profiles` table (account-level)
- [ ] After Tier 1 registration → Influencer adds first profile (required)
- [ ] "Add New Profile" button in dashboard → 2-5 minutes to add additional profile
- [ ] Profile verification per platform:
  - OAuth connection (preferred): Instagram, Facebook, TikTok OAuth flow
  - Manual verification: Upload screenshot with verification code
- [ ] Personal data NOT asked again when adding 2nd, 3rd profile
- [ ] Each profile has own: Platform, handle, follower count, categories, pricing, audience demographics
- [ ] Primary profile selection (1 per influencer, default for matching)
- [ ] Profile status management: Active, Paused, Suspended, Deleted
- [ ] Cannot delete last profile (must have ≥1 active profile)

**Dependencies:** FR-001

**Related User Stories:**
- As an influencer with Instagram + TikTok, I want to add both accounts without re-entering my personal info so that I save time
- As an influencer, I want to set my Instagram as primary so that brands see it first when matching

---

#### FR-003: Profile Data Collection (Tier 1, 2, 3)

**Priority:** Must Have (Tier 1), Should Have (Tier 2), Could Have (Tier 3)

**Description:**
System thu thập influencer data theo 3 tiers:
- **Tier 1 Essential (28 fields):** Bắt buộc, 5-7 phút
- **Tier 2 Recommended (38 fields):** Suggested ngay sau Tier 1, improve matching quality
- **Tier 3 Optional (60 fields):** Thu thập dần, nice-to-have

**Tier 1 Essential Fields (Must Have):**
```
Influencer Level (13 fields - asked ONCE):
- Full name, Display name, DOB, National ID
- Gender, Phone, Email, Location (city)
- Bank account number, Bank name
- TCB customer status, Interest in finance campaigns
- Compliance (8 checkboxes)

Profile Level (15 fields - per social account):
- Platform, Account handle/URL
- Primary categories (1-3: finance, beauty, lifestyle, etc.)
- Content language (Vietnamese, English, Bilingual)
- Niche specialty
- Target audience description
- Portfolio links (3-5 best posts)
- Base rate range (min-max VND)
- Rate negotiability
```

**Tier 2 Recommended Fields (Should Have):**
```
Profile Level (38 fields):
- Audience demographics (age, gender, location distribution)
- Content strategy (formats, posting frequency, style)
- Finance affinity (banking relationships, credit card usage, investment experience, financial literacy score)
- Detailed pricing (rate per post/story/video per platform)
- Collaboration preferences (lead time, max concurrent campaigns, blackout dates)
- Performance history (campaigns completed, avg CTR/CVR)
- Professional setup (working solo vs agency, team size)
- Analytics capability (can provide reports, tracking tools used)
```

**Tier 3 Optional Fields (Could Have):**
```
Profile Level (60 fields):
- Advanced audience insights (income level, occupation types, interests)
- Platform-specific notes, content approval preferences
- Case studies, brand testimonials
- Certification/training completed
- Additional social platforms
```

**Acceptance Criteria:**
- [ ] Form wizard với progress bar (Step 1 of 3)
- [ ] Tier 1 form validates all required fields before submission
- [ ] Tier 2 form skippable (user can click "Skip for now")
- [ ] Tier 3 form accessible anytime from dashboard ("Complete your profile")
- [ ] Profile completion percentage displayed (0-100%)
- [ ] AI pre-fill where possible:
  - Location from phone area code
  - Pricing suggestion from follower count + category
  - Categories from Instagram bio analysis (if user pastes bio)
- [ ] Smart defaults:
  - Content language = Vietnamese (default)
  - Rate negotiability = Flexible (default)
- [ ] Field validation:
  - DOB → Age ≥18 (hard requirement)
  - Phone → Vietnam format (+84...)
  - Email → Valid format
  - Bank account → 10-14 digits
  - Portfolio links → Valid URLs

**Dependencies:** FR-001, FR-002

**Related User Stories:**
- As an influencer, I want to complete Tier 1 in <7 minutes so that I can start browsing campaigns quickly
- As an influencer, I want the system to suggest my pricing based on my follower count so that I don't undervalue myself
- As an influencer, I want to skip Tier 2 and come back later so that I'm not forced to spend 30 minutes upfront

---

#### FR-004: Social Metrics Auto-Fetch (Diso Integration - Source 2)

**Priority:** Must Have

**Description:**
System KHÔNG hỏi influencer về follower count, engagement rate, post frequency, content types. Instead, auto-fetch từ Diso Influence-Meter API (Source 2: Social Crawl). Influencer chỉ cần link social account → System tự động fetch metrics.

**Acceptance Criteria:**
- [ ] After influencer links social account → System calls Diso API to fetch:
  - Follower count, Following count, Post count
  - Engagement rate (likes + comments / followers)
  - Avg likes, avg comments, avg shares
  - Posts per week
  - Account verified status (blue check)
  - Account created date
- [ ] Display fetched data to influencer: "We detected 500K followers on Instagram. Is this correct?"
- [ ] Allow manual override if data incorrect (edge case: API failed)
- [ ] Auto-refresh metrics monthly (Diso crawls in background)
- [ ] Show "Last updated" timestamp for metrics
- [ ] Don't ask these fields in onboarding form (reduces 10-15 fields)
- [ ] If Diso API fails → Allow influencer to self-report temporarily → Flag for manual review

**Dependencies:** FR-002, Diso Influence-Meter API integration

**Related User Stories:**
- As an influencer, I don't want to manually enter my follower count because the system can see it from my Instagram
- As a brand, I want to trust that follower counts are accurate (not self-reported) so that I avoid inflated numbers

---

#### FR-005: Profile Editing & Updates

**Priority:** Must Have

**Description:**
Influencers phải có khả năng edit profile data anytime. Personal data (Tier 1) có thể edit nhưng một số fields locked after eKYC (name, DOB, National ID). Profile-specific data (pricing, categories, portfolio) có thể edit freely.

**Acceptance Criteria:**
- [ ] "Edit Profile" button in dashboard
- [ ] Edit form pre-fills existing data
- [ ] Locked fields after eKYC: Full name, DOB, National ID (show reason: "Verified via eKYC, contact support to change")
- [ ] Editable fields: Display name, bio, location, bank account, phone, email (with re-verification)
- [ ] Profile-specific fields always editable: Categories, pricing, portfolio, audience demographics
- [ ] Change tracking: Log what changed, when, by whom (audit trail)
- [ ] Email change → Requires email verification (send OTP to new email)
- [ ] Phone change → Requires SMS OTP to new number
- [ ] Bank account change → Flagged for admin review (fraud prevention)
- [ ] Auto-save draft every 30 seconds
- [ ] "Discard changes" button to revert
- [ ] Success message after save: "Profile updated successfully"
- [ ] Quarterly reminder email: "Update your profile for better matches" (90 days since last update)

**Dependencies:** FR-001, FR-002, FR-003

**Related User Stories:**
- As an influencer, I want to update my pricing when my follower count grows so that I get fair compensation
- As an influencer, I want to add new portfolio items after completing campaigns so that my profile stays current

---

#### FR-006: Profile Status Management

**Priority:** Should Have

**Description:**
Influencers có thể pause/resume profiles (VD: maternity leave, platform break). System phải support profile lifecycle states.

**Acceptance Criteria:**
- [ ] Profile states:
  - **Active:** Available for campaigns (default)
  - **Paused:** Temporarily unavailable (reason required: dropdown + optional text)
  - **Under Review:** Admin reviewing profile (system-managed)
  - **Suspended:** Violation detected (system/admin action)
  - **Deleted:** Soft delete (can restore within 30 days)
- [ ] "Pause Profile" button per profile (not influencer-level)
  - Example: Pause Instagram, keep Facebook + TikTok active
- [ ] Pause reasons (dropdown):
  - Maternity leave
  - Platform break
  - Traveling
  - Focusing on other platforms
  - Other (free text)
- [ ] Paused profiles:
  - NOT shown in brand search results
  - Cannot receive campaign invites
  - Can view existing campaigns
  - Can resume anytime
- [ ] "Resume Profile" button → Profile back to Active
- [ ] Suspended profiles:
  - Influencer sees reason (system message)
  - Cannot resume (must contact support)
  - Can appeal suspension
- [ ] Delete profile:
  - Confirmation modal: "Are you sure? This cannot be undone."
  - Soft delete (data retained 30 days)
  - "Restore deleted profile" option in settings (within 30 days)
  - Hard delete after 30 days (GDPR compliance)

**Dependencies:** FR-002

**Related User Stories:**
- As an influencer going on maternity leave, I want to pause my Instagram for 3 months so that I don't receive campaign invites
- As an influencer, I want to delete my TikTok profile because I'm no longer active there so that brands only see my active accounts

---

### EPIC-02: Brand Portal - Influencer Discovery & Browsing

#### FR-007: Influencer Search & Filters

**Priority:** Must Have

**Description:**
Brand marketing teams phải có khả năng search và filter influencers trong Influencer Library dựa trên multiple criteria để tìm influencers phù hợp cho campaigns.

**Acceptance Criteria:**
- [ ] Search bar: Free text search (searches: name, bio, niche specialty)
- [ ] Filter sidebar với categories:
  - **Platform:** Checkboxes (Instagram, Facebook, TikTok, YouTube, LinkedIn)
  - **Follower Range:** Slider (10K-50K, 50K-100K, 100K-500K, 500K-1M, 1M+)
  - **Engagement Rate:** Slider (1-2%, 2-4%, 4-6%, 6%+)
  - **Content Categories:** Multi-select (Finance, Beauty, Lifestyle, Travel, Food, Tech, etc.)
  - **Location:** Multi-select provinces/cities (HCMC, Hanoi, Da Nang, Can Tho, etc.)
  - **Audience Age:** Checkboxes (18-24, 25-34, 35-44, 45+)
  - **Audience Gender:** Checkboxes (Majority Female, Majority Male, Balanced)
  - **Finance Affinity Score:** Slider (0-100, default: no filter)
  - **TCB Customer:** Checkbox "TCB customers only"
  - **Rate Range:** Min-Max VND input
  - **Availability:** Checkbox "Available now" (excludes paused profiles)
- [ ] Filter combinations work with AND logic (all must match)
- [ ] "Clear all filters" button
- [ ] Active filter count badge: "Filters (5)" if 5 filters applied
- [ ] URL params for filters (sharable links)
- [ ] Save filter preset: "Save this search" → Name it → Reuse later
- [ ] Suggested filters based on campaign type (if coming from campaign creation flow):
  - Campaign = Credit Card → Auto-filter: Finance affinity >60, Age 25-44
- [ ] Filter performance: Results update in <300ms (paginated, lazy load)

**Dependencies:** FR-002 (profiles must exist to search)

**Related User Stories:**
- As a brand manager, I want to filter influencers by "Finance affinity >70" so that I find influencers genuinely interested in finance
- As a brand manager, I want to save my filter preset "Credit Card Millennials" so that I don't re-apply 5 filters every time

---

#### FR-008: Influencer List View with Sorting

**Priority:** Must Have

**Description:**
Brand marketing teams cần view danh sách influencers trong table/grid format với sorting options.

**Acceptance Criteria:**
- [ ] View toggle: Table view (default) / Grid view (cards)
- [ ] **Table View** columns:
  - Checkbox (multi-select)
  - Profile photo + Name (display name)
  - Platform badges (IG, FB, TT icons)
  - Follower count (formatted: 500K, 1.2M)
  - Engagement rate (% with color coding: green >4%, yellow 2-4%, red <2%)
  - Categories (chips, max 3 shown)
  - Finance Affinity Score (gauge: 0-100)
  - Rate range (min-max VND)
  - Actions (View Profile, Add to Campaign, Favorite)
- [ ] **Grid View** cards:
  - Profile photo (large)
  - Name + Primary platform
  - Follower count + Engagement rate
  - Categories (chips)
  - Finance Affinity Score
  - Rate range
  - Quick action buttons
- [ ] Sorting options (dropdown):
  - Relevance (default, based on filters + matching score)
  - Follower count (high to low / low to high)
  - Engagement rate (high to low)
  - Finance affinity score (high to low)
  - Rate (low to high / high to low)
  - Recently updated (newest first)
- [ ] Pagination: 20 results per page (configurable: 10/20/50/100)
- [ ] Infinite scroll option (toggle in settings)
- [ ] Bulk actions:
  - Select all (current page / all pages)
  - Add selected to campaign (bulk invite)
  - Add selected to favorites
  - Export selected to CSV
- [ ] Performance: List renders in <500ms for 20 items

**Dependencies:** FR-007

**Related User Stories:**
- As a brand manager, I want to sort by engagement rate (high to low) so that I prioritize high-performing influencers
- As a brand manager, I want to select 10 influencers and add them to my campaign with 1 click so that I save time

---

#### FR-009: Influencer Profile Detail Page

**Priority:** Must Have

**Description:**
Brand marketing teams cần xem chi tiết profile của 1 influencer để đánh giá suitability cho campaign trước khi invite.

**Acceptance Criteria:**
- [ ] URL format: `/brand/influencer-pool/[influencerId]`
- [ ] Profile sections:
  1. **Header:**
     - Profile photo (large)
     - Display name + Verified badge (if verified)
     - Primary platform + handle (clickable link)
     - Finance Affinity Score (prominent gauge)
     - TCB Customer badge (if applicable)
     - Action buttons: "Invite to Campaign", "Add to Favorites", "Send Message"
  2. **Social Profiles:**
     - Cards for each linked account (IG, FB, TT, YT, etc.)
     - Per profile: Platform, handle, follower count, engagement rate, verification status
     - "View Platform Insights" → Expands to show demographics, content types
  3. **About:**
     - Bio/description
     - Content categories (chips)
     - Niche specialty
     - Languages
     - Location (city)
  4. **Audience Demographics:**
     - Age distribution (bar chart)
     - Gender distribution (pie chart)
     - Top locations (list with %)
     - Income level
     - Audience interests
  5. **Content Portfolio:**
     - Grid of portfolio items (images/videos)
     - Lightbox on click
     - Link to original post
     - Performance metrics per post (if available)
  6. **Pricing:**
     - Rate card table:
       | Platform | Post Type | Rate (VND) |
       |----------|-----------|------------|
       | Instagram | Post | 10M |
       | Instagram | Reel | 12M |
       | Instagram | Story (5x) | 3M |
     - Package deals (if any)
     - Negotiability indicator
  7. **Performance History:**
     - Total campaigns completed
     - Campaigns last 12 months
     - Finance campaigns completed
     - Avg CTR / CVR (if available)
     - Case studies (links)
  8. **Finance Affinity Details:** (If score >50)
     - TCB customer info (products used, customer since)
     - Banking relationships
     - Investment experience level
     - Financial literacy score
     - Finance content examples
  9. **Collaboration Preferences:**
     - Lead time required
     - Max concurrent campaigns
     - Blackout dates (calendar view)
     - Creative control preference
     - Willing to travel
- [ ] Responsive design (mobile-friendly)
- [ ] Loading skeleton while fetching data
- [ ] Error state if profile not found / access denied
- [ ] Breadcrumb navigation: Home > Influencer Pool > [Name]
- [ ] "Back to search results" button (preserves filters)

**Dependencies:** FR-002, FR-003

**Related User Stories:**
- As a brand manager, I want to see the influencer's audience age distribution so that I can verify it matches my target demographic
- As a brand manager, I want to see past campaign performance so that I can assess if this influencer delivers results

---

#### FR-010: Influencer Comparison

**Priority:** Should Have

**Description:**
Brand marketing teams cần so sánh 2-5 influencers side-by-side để quyết định chọn ai.

**Acceptance Criteria:**
- [ ] "Add to Compare" button on list view + profile detail
- [ ] Compare tray at bottom of screen:
  - Shows mini cards of selected influencers (max 5)
  - "Compare Now" button (enabled when ≥2 selected)
  - "Clear All" button
- [ ] Comparison page: `/brand/influencer-pool/compare?ids=1,2,3`
- [ ] Side-by-side table:
  | Metric | Influencer A | Influencer B | Influencer C |
  |--------|--------------|--------------|--------------|
  | Photo | [img] | [img] | [img] |
  | Follower Count | 500K | 300K | 1M |
  | Engagement Rate | 4.2% ✅ Best | 3.1% | 6.8% ✅ Best |
  | Finance Affinity | 82 ✅ Best | 65 | 45 |
  | Rate per Post | 10M | 7M ✅ Lowest | 15M |
  | Audience 25-34 | 50% | 60% ✅ Best | 35% |
  | ...more rows... | | | |
- [ ] Highlight best value in each row (green background)
- [ ] Difference indicators: "↑25% higher", "↓15% lower"
- [ ] Export comparison to PDF
- [ ] "Invite All" button → Add all compared influencers to campaign
- [ ] Performance: Comparison loads in <1s

**Dependencies:** FR-008, FR-009

**Related User Stories:**
- As a brand manager, I want to compare 3 influencers side-by-side so that I can see who has the best engagement rate
- As a brand manager, I want to export the comparison to PDF so that I can share with my team for decision-making

---

#### FR-011: Favorite/Bookmark Influencers

**Priority:** Should Have

**Description:**
Brand marketing teams cần save influencers to favorites list để easily access later.

**Acceptance Criteria:**
- [ ] "Add to Favorites" button (heart icon) on:
  - List view (per row)
  - Profile detail page (header)
  - Comparison page
- [ ] Favorites toggle (filled heart = favorited, outline = not)
- [ ] Favorites page: `/brand/favorites`
- [ ] Favorites list:
  - Same view as influencer list (table/grid toggle)
  - All sorting/filtering options available
  - "Remove from Favorites" button
  - Organize by tags (optional): "Credit Card Campaign", "Beauty Influencers", etc.
- [ ] Favorites count badge in menu: "Favorites (12)"
- [ ] Favorites synced per user (not shared across team)
- [ ] Bulk operations: "Add all filtered results to Favorites"
- [ ] Performance: Add/remove from favorites in <200ms (optimistic UI update)

**Dependencies:** FR-008, FR-009

**Related User Stories:**
- As a brand manager, I want to favorite influencers I like so that I can quickly find them for future campaigns
- As a brand manager, I want to organize favorites by tags so that I can group influencers by campaign type

---

### EPIC-03: Influencer Profile Submission & Campaign Interaction

#### FR-012: Campaign Browsing (Influencer Portal)

**Priority:** Must Have

**Description:**
Influencers phải có khả năng browse available campaigns mà TCB đang active recruiting influencers.

**Acceptance Criteria:**
- [ ] Campaigns page: `/portal/campaigns`
- [ ] Campaign card view (grid, 3 columns):
  - Campaign banner image
  - Campaign title
  - Brand logo (TCB)
  - Product category (Credit Card, Investment, etc.)
  - Rate range (VND)
  - Duration (start - end date)
  - Deliverables summary (3 posts + 5 stories)
  - Required platforms (badges: IG, FB, TT)
  - Match score (if logged in): "92% Match" (based on influencer's profiles)
  - Status: "Open for Applications" / "Closing Soon" / "Filled"
  - "View Details" button
- [ ] Filter sidebar:
  - Platform required (IG, FB, TT, YT)
  - Product category (All, Credit Cards, Savings, Loans, Investment)
  - Rate range (min-max VND)
  - Duration (This week, This month, Next 3 months)
  - Application deadline (sorting)
- [ ] Sort options:
  - Match score (high to low) - default if logged in
  - Rate (high to low / low to high)
  - Application deadline (earliest first)
  - Posted date (newest first)
- [ ] Campaign detail page: `/portal/campaigns/[campaignId]`
  - Full brief (what, why, target audience, deliverables, timeline)
  - Requirements (follower count, engagement rate, audience demographics)
  - Rate & payment terms
  - Application deadline
  - Spots available (10 slots, 3 filled)
  - "Apply Now" button (disabled if doesn't meet requirements)
  - "Not eligible" message if profile doesn't match (with reasons)
- [ ] Recommended campaigns section: "Based on your profile"
- [ ] Performance: Campaign list loads in <500ms

**Dependencies:** Brand creates campaigns (Out of scope for this PRD - Phase 3)

**Related User Stories:**
- As an influencer, I want to see campaigns sorted by match score so that I apply to campaigns I'm most likely to get
- As an influencer, I want to see why I'm not eligible for a campaign so that I can improve my profile

---

#### FR-013: Campaign Application (Influencer Portal)

**Priority:** Must Have

**Description:**
Influencers phải có khả năng apply to campaigns với profile của họ.

**Acceptance Criteria:**
- [ ] "Apply Now" button on campaign detail page
- [ ] Application modal/page:
  - Select which profile to use (if multiple):
    - Radio buttons: @beauty_ig (500K, 92% match) ✅ Recommended
    - @beauty_fb (200K, 65% match)
    - @beauty_tiktok (1M, 45% match - doesn't meet requirements)
  - Pre-filled data from selected profile:
    - Platform, handle, follower count, engagement rate
    - Audience demographics (age, gender, location)
    - Rate expectation (editable)
  - Campaign-specific questions (if any):
    - "Have you promoted credit cards before?" (Yes/No)
    - "Can you create content in English?" (Yes/No)
    - Upload: Previous campaign examples (optional)
  - Application message (optional, 500 chars):
    - "Why are you a good fit for this campaign?"
  - Confirm deliverables checklist:
    - [ ] I can deliver 3 Instagram posts by [date]
    - [ ] I can deliver 5 Instagram stories by [date]
    - [ ] I agree to use #ad or #sponsored tags (compliance)
  - T&C checkbox: "I agree to campaign terms and TCB influencer agreement"
- [ ] Application preview before submit
- [ ] Submit button → Confirmation message: "Application submitted successfully"
- [ ] Post-submit actions:
  - Redirect to "My Applications" page
  - Show application status: "Under Review"
  - Email notification to influencer: "Your application was received"
  - Email notification to brand: "New application for [Campaign]"
- [ ] Cannot apply twice to same campaign (show "Already applied" status)
- [ ] Can withdraw application before brand reviews (status = "Submitted")
- [ ] Performance: Application submits in <1s

**Dependencies:** FR-012, FR-002 (needs profiles to apply)

**Related User Stories:**
- As an influencer, I want to apply to a campaign with my Instagram account so that I can get selected for the collaboration
- As an influencer, I want to see which of my profiles is recommended so that I use the best-fit account

---

#### FR-014: Application Status Tracking (Influencer Portal)

**Priority:** Must Have

**Description:**
Influencers phải có khả năng track status của applications họ đã submit.

**Acceptance Criteria:**
- [ ] "My Applications" page: `/portal/applications`
- [ ] Application list (table view):
  | Campaign | Profile Used | Applied Date | Status | Actions |
  |----------|--------------|--------------|--------|---------|
  | Credit Card Millennials | @beauty_ig | 2026-02-10 | Under Review | View, Withdraw |
  | Investment Fund | @finance_ig | 2026-02-08 | Accepted ✅ | View Contract, Upload Content |
  | Savings Account | @beauty_fb | 2026-02-05 | Rejected | View Feedback |
- [ ] Application statuses:
  - **Submitted:** Application received, waiting for brand review
  - **Under Review:** Brand is reviewing application
  - **Accepted:** Brand selected this influencer ✅
  - **Rejected:** Brand did not select this influencer
  - **Withdrawn:** Influencer withdrew application
  - **Contract Sent:** Brand sent contract, waiting for influencer signature
  - **Active:** Contract signed, campaign in progress
  - **Completed:** Campaign finished, payment processed
- [ ] Status timeline (per application):
  - Submitted: 2026-02-10 10:30 AM
  - Under Review: 2026-02-11 2:15 PM
  - Accepted: 2026-02-12 4:00 PM
  - Contract Sent: 2026-02-12 4:30 PM
  - (Next step: Sign contract)
- [ ] Filter by status (dropdown): All, Submitted, Accepted, Rejected, Active, Completed
- [ ] Sort by: Application date, Status, Campaign name
- [ ] Notification badges: "3 new updates" on Applications menu item
- [ ] In-app notifications:
  - "Your application for [Campaign] was accepted!"
  - "Your application for [Campaign] was rejected. Reason: [...]"
- [ ] Email notifications for status changes
- [ ] Performance: Applications page loads in <500ms

**Dependencies:** FR-013

**Related User Stories:**
- As an influencer, I want to see the status of my applications so that I know if I got selected
- As an influencer, I want to receive email notifications when my application status changes so that I don't miss important updates

---

#### FR-015: Content Submission (Influencer Portal)

**Priority:** Must Have

**Description:**
Sau khi được accept vào campaign, influencers phải submit deliverables (posts, stories, videos) để brand review.

**Acceptance Criteria:**
- [ ] Content submission page: `/portal/campaigns/[campaignId]/submit`
- [ ] Deliverables checklist:
  - [ ] Instagram Post 1 (Due: Feb 20, 2026)
    - Upload image/video (max 10MB per file)
    - Caption (copy-paste from Instagram)
    - Link to published post (Instagram URL)
    - Performance metrics (optional): Likes, Comments, Shares, Reach
    - Submit button
  - [ ] Instagram Post 2 (Due: Feb 22, 2026)
  - [ ] Instagram Stories (5 stories) (Due: Feb 25, 2026)
    - Upload screenshots of stories
    - Links to story highlights (if available)
- [ ] Submission statuses per deliverable:
  - **Pending:** Not submitted yet
  - **Submitted:** Uploaded, waiting for brand review
  - **Approved:** Brand approved ✅
  - **Revision Requested:** Brand wants changes (with feedback)
  - **Re-submitted:** Influencer uploaded revised version
- [ ] File upload:
  - Drag-and-drop area
  - File type validation (images: JPG, PNG, GIF / videos: MP4, MOV)
  - File size validation (max 10MB per file, max 50MB total)
  - Upload progress bar
  - "Remove file" option before submit
- [ ] Link validation:
  - Instagram URL format check
  - "Verify link" button → System checks if post exists (API call or manual check)
- [ ] Bulk upload: "Upload All" if multiple deliverables
- [ ] Submission confirmation:
  - Modal: "You are submitting [3 files]. Cannot undo. Continue?"
  - Success message: "Deliverables submitted for review"
  - Email to brand: "New deliverable submitted for [Campaign]"
- [ ] Re-submission flow (if revision requested):
  - View brand feedback
  - Upload new file (replaces old)
  - Add message: "Changes made: [...]"
  - Submit again
- [ ] Campaign timeline:
  - Shows deadlines for each deliverable
  - Overdue indicator (red) if past deadline
  - Warnings: "Due in 2 days" (yellow)
- [ ] Performance: File upload completes in <5s for 10MB file

**Dependencies:** FR-013 (must be accepted first), FR-014

**Related User Stories:**
- As an influencer, I want to upload my content and submit for review so that I can complete my campaign deliverables
- As an influencer, I want to see if my submission was approved so that I know if I need to make revisions

---

### EPIC-04: Data Integration & Synchronization

#### FR-016: Diso Influence-Meter API Integration (Source 2: Social Crawl)

**Priority:** Must Have

**Description:**
System phải integrate với Diso Influence-Meter API để tự động fetch social media metrics thay vì hỏi influencer.

**Acceptance Criteria:**
- [ ] API endpoints integrated:
  - `POST /api/profiles/verify` - Verify social account ownership
  - `GET /api/profiles/{profileId}/metrics` - Get follower count, engagement rate, etc.
  - `POST /api/profiles/crawl` - Trigger on-demand crawl
  - `GET /api/profiles/{profileId}/audience` - Get audience demographics
- [ ] 3-tier architecture flow:
  - TCB backend → AT Core API → Diso API
  - AT Core owns Diso API key (TCB never calls Diso directly)
  - AT Core maps TCB profile ID ↔ Diso profile ID
- [ ] Auto-fetch triggers:
  - On profile creation (after influencer links account)
  - On profile update (if influencer changes handle)
  - Monthly scheduled crawl (background job)
  - On-demand crawl (when brand views profile)
- [ ] Data fetched and stored:
  - Follower count, Following count, Post count
  - Engagement rate (%)
  - Avg likes, avg comments, avg shares
  - Posts per week
  - Account verified status
  - Account created date
  - Audience age distribution (% per bracket)
  - Audience gender distribution
  - Audience top locations (cities/provinces)
- [ ] Error handling:
  - If Diso API fails → Retry 3 times with exponential backoff
  - If still fails → Allow influencer self-report (flag for manual review)
  - If account not found → Error message: "Could not verify account. Check handle."
- [ ] Rate limiting:
  - Respect Diso API rate limits (100 req/min)
  - Queue requests if limit reached
  - Retry after rate limit reset
- [ ] Caching:
  - Cache metrics for 24 hours (reduce API calls)
  - Invalidate cache if influencer triggers manual refresh
- [ ] Monitoring:
  - Log all API calls (request, response, latency)
  - Alert if error rate >5%
  - Dashboard: Diso API health, call volume, avg latency
- [ ] Performance: API call completes in <2s (p95)

**Dependencies:** FR-002, FR-004, Diso API availability

**Related User Stories:**
- As a system, I want to auto-fetch follower count from Instagram so that influencers don't manually enter it
- As an admin, I want to see Diso API health metrics so that I can troubleshoot if integration fails

---

#### FR-017: AT Core Middleware (ID Mapping & Tenant Isolation)

**Priority:** Must Have

**Description:**
AT Core phải hoạt động như middleware giữa TCB và Diso để manage API keys, map IDs, và ensure tenant isolation.

**Acceptance Criteria:**
- [ ] AT Core database table: `influencer_mappings`
  ```sql
  CREATE TABLE influencer_mappings (
    id UUID PRIMARY KEY,
    tenant_id VARCHAR(50), -- 'techcombank'
    tenant_influencer_id VARCHAR(100), -- TCB's internal ID
    diso_profile_id VARCHAR(100), -- Diso's profile ID
    platform VARCHAR(20), -- facebook, instagram, tiktok
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(tenant_id, tenant_influencer_id)
  );
  ```
- [ ] AT Core API endpoints:
  - `POST /api/tenants/{tenantId}/profiles/sync` - Create/update profile, map to Diso
  - `GET /api/tenants/{tenantId}/profiles/{profileId}` - Get profile with mapped Diso data
  - `POST /api/tenants/{tenantId}/profiles/{profileId}/metrics` - Push performance data to Diso
- [ ] ID mapping flow:
  1. TCB creates profile → Sends to AT Core with TCB profile ID
  2. AT Core calls Diso API → Gets Diso profile ID
  3. AT Core stores mapping: TCB ID ↔ Diso ID
  4. AT Core returns mapped profile to TCB
  5. Future calls: TCB uses TCB ID → AT Core translates to Diso ID
- [ ] Tenant isolation:
  - All API calls include `tenant_id` (techcombank, vinfast, etc.)
  - AT Core filters: `WHERE tenant_id = 'techcombank'`
  - TCB cannot see Vinfast's influencers, vice versa
- [ ] API key management:
  - AT Core owns Diso API key (stored securely)
  - TCB never sees Diso API key
  - AT Core authenticates TCB via JWT
- [ ] Data transformation:
  - TCB sends data in TCB format
  - AT Core transforms to Diso format
  - Diso returns data → AT Core transforms back to TCB format
- [ ] Error handling:
  - If Diso API fails → AT Core returns error to TCB
  - If mapping not found → AT Core creates new mapping
- [ ] Performance: AT Core adds <50ms overhead per request

**Dependencies:** FR-016, AT Core infrastructure

**Related User Stories:**
- As AT Core, I want to map TCB profile IDs to Diso profile IDs so that TCB doesn't need to know Diso's ID scheme
- As AT Core, I want to ensure tenant isolation so that Techcombank cannot see Vinfast's influencer data

---

#### FR-018: Performance Data Push (Source 3: Campaign Metrics)

**Priority:** Should Have

**Description:**
Sau khi campaign complete, TCB phải push performance data (CTR, CVR, completion rate) to Diso để update influencer scores.

**Acceptance Criteria:**
- [ ] Push trigger: Campaign status changes to "Completed"
- [ ] Data pushed per influencer:
  - Campaign ID, Influencer profile ID
  - Completed (yes/no)
  - On-time delivery (yes/no)
  - CTR (click-through rate %)
  - CVR (conversion rate %)
  - Reach (impressions)
  - Engagement (likes + comments + shares)
  - Revenue generated (if trackable)
- [ ] Push flow:
  1. TCB backend → POST `/api/campaigns/{campaignId}/complete`
  2. AT Core receives → Maps TCB profile ID to Diso profile ID
  3. AT Core → POST to Diso `/api/performance/update`
  4. Diso updates Performance Score (Source 3)
  5. Diso recalculates Overall Quality Score
- [ ] Retry logic:
  - If push fails → Retry 3 times
  - If still fails → Queue for manual retry
  - Admin dashboard shows failed pushes
- [ ] Historical data:
  - Store all performance data (not just latest)
  - Diso calculates avg CTR/CVR across all campaigns
- [ ] Performance: Push completes in <1s

**Dependencies:** FR-016, FR-017, Campaign completion (Phase 3)

**Related User Stories:**
- As a system, I want to push campaign performance data to Diso so that influencer scores reflect real results
- As a brand, I want to see historical performance so that I can identify consistently high-performing influencers

---

#### FR-019: Brand Rating Push (Source 4: Brand Reviews)

**Priority:** Should Have

**Description:**
Sau khi campaign complete, TCB brand team phải rate influencer (collaboration quality, communication, professionalism). System pushes ratings to Diso.

**Acceptance Criteria:**
- [ ] Brand rating form:
  - Overall rating: 1-5 stars (required)
  - Collaboration quality: 1-5 stars (required)
  - Communication: 1-5 stars (required)
  - Professionalism: 1-5 stars (required)
  - Content quality: 1-5 stars (required)
  - Would recommend: Yes/No
  - Comments (optional, 500 chars)
- [ ] Rating submission: POST `/api/campaigns/{campaignId}/rate-influencer`
- [ ] Push flow:
  1. Brand submits rating → TCB backend
  2. TCB → AT Core → Diso
  3. Diso updates Brand Rating Score (Source 4)
  4. Diso recalculates Overall Quality Score
- [ ] Rating visibility:
  - Influencer can see ratings (transparency)
  - Brand can see own ratings
  - Other brands can see aggregated score only (not individual ratings)
- [ ] Performance: Rating push completes in <500ms

**Dependencies:** FR-016, FR-017, Campaign review (Phase 3 - Out of scope)

**Note:** Rating form UI is out of scope for this PRD (Phase 3: Brand Campaign Management)

---

### EPIC-05: System Administration & Compliance

#### FR-020: Influencer Approval Workflow

**Priority:** Must Have

**Description:**
Admin phải review và approve influencer registrations trước khi họ có thể browse/apply campaigns.

**Acceptance Criteria:**
- [ ] Admin dashboard: Pending approvals queue
- [ ] Approval checklist per influencer:
  - [ ] eKYC verification passed (auto-check)
  - [ ] Age 18+ confirmed (auto-check from DOB)
  - [ ] Social accounts verified (OAuth or manual)
  - [ ] No red flags (manual review: inappropriate content, fake followers)
  - [ ] Bank account valid format
  - [ ] No competitor exclusivity conflicts
- [ ] Auto-approval rules:
  - If all auto-checks pass + no manual review flags → Auto-approve after 24 hours
  - If any check fails → Flag for manual review
- [ ] Manual approval actions:
  - Approve → Influencer status = "Active", can browse campaigns
  - Reject → Influencer status = "Rejected", email with reason
  - Request Info → Influencer status = "Info Requested", email asking for clarification
- [ ] Rejection reasons (dropdown + free text):
  - Failed eKYC verification
  - Underage (<18)
  - Inappropriate content on social media
  - Suspected fake followers
  - Competitor exclusivity conflict
  - Incomplete information
  - Other (explain)
- [ ] Audit trail:
  - Log who approved/rejected, when, reason
  - Compliance report: All approvals in date range
- [ ] Performance: Approval queue loads in <1s

**Dependencies:** FR-001 (registration must complete first)

**Related User Stories:**
- As an admin, I want to auto-approve influencers who pass all checks so that I don't manually review every registration
- As an admin, I want to reject influencers with inappropriate content so that we maintain brand safety

---

#### FR-021: eKYC Integration (Identity Verification)

**Priority:** Must Have

**Description:**
System phải integrate với eKYC provider (VNPT, FPT, etc.) để verify influencer identity trước khi approve.

**Acceptance Criteria:**
- [ ] eKYC flow triggered after Tier 1 registration
- [ ] eKYC steps:
  1. Upload National ID (front + back photos)
  2. Take selfie (liveness detection - blink, turn head)
  3. OCR extracts: Name, DOB, ID number, Address
  4. Face matching: Selfie vs ID photo (similarity score >90%)
  5. Government database check: ID number valid
  6. Blacklist check: ID not on fraud list
- [ ] eKYC statuses:
  - Pending: Not started
  - In Progress: Influencer uploaded docs, processing
  - Completed: Verified ✅
  - Failed: Verification failed (reason: face mismatch, invalid ID, etc.)
- [ ] eKYC result stored:
  - Verification date, provider (VNPT/FPT), session ID
  - Extracted data (name, DOB, ID, address)
  - Similarity score (%)
  - Status (completed/failed)
- [ ] Retry policy:
  - If failed → Influencer can retry (max 3 attempts)
  - After 3 fails → Flag for manual review
- [ ] Personal data lock:
  - After eKYC completes → Lock fields: Full name, DOB, National ID
  - Show message: "Verified via eKYC. Contact support to change."
- [ ] Compliance:
  - Store eKYC proof for 5 years (SBV requirement)
  - Encrypted storage (GDPR compliance)
- [ ] Performance: eKYC completes in 2-3 minutes

**Dependencies:** FR-001, eKYC provider contract

**Related User Stories:**
- As an admin, I want eKYC to auto-verify influencer identity so that I don't manually check IDs
- As an influencer, I want eKYC to be fast (<5 mins) so that I'm not frustrated

---

#### FR-022: Audit Logs & Compliance Reporting

**Priority:** Must Have

**Description:**
System phải log all user actions để đáp ứng compliance requirements (SBV, GDPR, internal audit).

**Acceptance Criteria:**
- [ ] Events logged:
  - User actions: Login, logout, profile update, application submit, content upload
  - Admin actions: Approve/reject influencer, suspend account, delete data
  - System actions: eKYC verification, API calls to Diso, data sync
- [ ] Log fields:
  - Timestamp (ISO 8601)
  - User ID, User role (influencer/brand/admin)
  - Action type (login, profile_update, etc.)
  - Resource affected (profile ID, campaign ID, etc.)
  - IP address
  - User agent (browser/device)
  - Result (success/failure)
  - Error message (if failed)
  - Metadata (JSON: what changed, old value → new value)
- [ ] Audit log storage:
  - Database table: `audit_logs`
  - Retention: 5 years (SBV requirement)
  - Immutable (cannot edit/delete logs)
- [ ] Audit log viewer (admin only):
  - Filter by: Date range, user ID, action type, result
  - Search by: Resource ID (e.g., profile ID)
  - Export to CSV (for compliance reports)
- [ ] Compliance reports:
  - Monthly active users report
  - Approval/rejection report (count, reasons)
  - eKYC verification report (success rate, failure reasons)
  - Data access report (who accessed what data)
- [ ] Performance: Log write in <10ms (async, non-blocking)

**Dependencies:** All user-facing features (logs user actions)

**Related User Stories:**
- As a compliance officer, I want to see all actions taken by user X so that I can audit their activity
- As a compliance officer, I want to export audit logs to CSV so that I can submit to regulators

---

### EPIC-06: User Experience & Interface

#### FR-023: Responsive Design (Mobile-First)

**Priority:** Must Have

**Description:**
All portals (Influencer, Brand) phải responsive, mobile-friendly vì 80% influencers sử dụng mobile.

**Acceptance Criteria:**
- [ ] Breakpoints:
  - Mobile: <640px (single column, touch-optimized)
  - Tablet: 640-1024px (2 columns)
  - Desktop: >1024px (3 columns, full features)
- [ ] Mobile-specific optimizations:
  - Large touch targets (min 44px height)
  - Bottom navigation (thumbs can reach)
  - Collapsible filters (drawer)
  - Infinite scroll (instead of pagination)
  - Camera access for photo upload
  - Native select dropdowns (iOS/Android)
- [ ] Responsive components:
  - Forms: Single column on mobile, 2 columns on desktop
  - Tables: Horizontal scroll or card view on mobile
  - Modals: Full-screen on mobile, centered on desktop
  - Navigation: Hamburger menu on mobile, top nav on desktop
- [ ] Touch gestures:
  - Swipe to delete (mobile lists)
  - Pull to refresh (mobile pages)
  - Pinch to zoom (images)
- [ ] Performance targets:
  - Mobile page load: <3s on 3G
  - First Contentful Paint: <1.5s
  - Time to Interactive: <3.5s
  - Lighthouse score: >90 (mobile)
- [ ] Testing:
  - Test on iOS Safari, Chrome Android
  - Test on iPhone SE (small screen), iPhone 14 Pro Max (large screen)
  - Test on Android (Samsung, Xiaomi)

**Dependencies:** All frontend features

**Related User Stories:**
- As an influencer using my phone, I want the registration form to work smoothly on mobile so that I can sign up on the go
- As a brand manager using iPad, I want the influencer list to display nicely so that I can browse during meetings

---

#### FR-024: Multi-Language Support (i18n)

**Priority:** Could Have

**Description:**
System phải support Vietnamese (primary) và English (secondary) cho international influencers/brands.

**Acceptance Criteria:**
- [ ] Language toggle in header:
  - Vietnamese (VI) - default
  - English (EN)
- [ ] Translated content:
  - All UI labels, buttons, error messages
  - Form field labels, placeholders, validation messages
  - Email templates (confirmation, notifications)
  - Static pages (T&C, Privacy Policy, FAQs)
- [ ] NOT translated (user-generated):
  - Influencer bios, campaign briefs, comments (remains in original language)
  - But display language indicator: "This content is in Vietnamese"
- [ ] Language persistence:
  - Store user language preference (cookie or DB)
  - Remember choice across sessions
- [ ] Implementation:
  - React i18n library (next-i18next)
  - Translation files: `locales/vi.json`, `locales/en.json`
  - Date/number formatting per locale
- [ ] Performance: Language switch in <200ms (no page reload)

**Dependencies:** All frontend features

**Note:** English support is low priority for Phase 1 (TCB focuses on Vietnamese market)

---

#### FR-025: Accessibility (WCAG 2.1 AA)

**Priority:** Should Have

**Description:**
System phải accessible cho users với disabilities (screen readers, keyboard navigation, color contrast).

**Acceptance Criteria:**
- [ ] WCAG 2.1 Level AA compliance:
  - Color contrast ratio ≥4.5:1 (text/background)
  - All interactive elements keyboard accessible (Tab, Enter, Esc)
  - Focus indicators visible (outline on Tab)
  - ARIA labels for screen readers
  - Alt text for all images
  - Form labels associated with inputs
  - Error messages announced by screen readers
- [ ] Keyboard navigation:
  - Tab order logical (top to bottom, left to right)
  - Enter to submit forms
  - Esc to close modals
  - Arrow keys to navigate lists
  - Space to select checkboxes
- [ ] Screen reader support:
  - Semantic HTML (header, nav, main, footer)
  - ARIA landmarks (role="navigation", role="main")
  - ARIA live regions for dynamic content
  - Skip to main content link
- [ ] Testing:
  - Test with NVDA (Windows), VoiceOver (Mac/iOS)
  - Lighthouse accessibility score >90
  - Automated testing (axe-core)
- [ ] Performance: No accessibility features degrade performance

**Dependencies:** All frontend features

**Related User Stories:**
- As a visually impaired influencer using screen reader, I want to navigate the registration form so that I can sign up independently
- As a user who cannot use mouse, I want to browse influencers using only keyboard so that I can do my job

---

## Non-Functional Requirements

### NFR-001: Performance - Page Load Time

**Priority:** Must Have

**Description:**
All pages phải load nhanh để không làm users frustrated, especially trên mobile 3G/4G.

**Acceptance Criteria:**
- [ ] Page load targets:
  - Desktop (4G): First Contentful Paint <1s, Time to Interactive <2s
  - Mobile (4G): First Contentful Paint <1.5s, Time to Interactive <3s
  - Mobile (3G): Page load <5s
- [ ] API response time:
  - p50: <100ms
  - p95: <300ms
  - p99: <500ms
- [ ] Optimization techniques:
  - Code splitting (lazy load routes)
  - Image optimization (WebP format, lazy loading)
  - CDN for static assets
  - Gzip/Brotli compression
  - Browser caching (max-age: 1 year for assets)
- [ ] Monitoring: Real User Monitoring (RUM) via Google Analytics
- [ ] Performance budget:
  - JavaScript bundle: <200KB (gzipped)
  - CSS: <50KB
  - Images per page: <500KB total

**Rationale:** Influencers sử dụng mobile, often on slower connections. Slow pages = high bounce rate.

---

### NFR-002: Availability - System Uptime

**Priority:** Must Have

**Description:**
System phải available 99.5% trong business hours để brands có thể access anytime.

**Acceptance Criteria:**
- [ ] Uptime target: 99.5% (equivalent to ~3.6 hours downtime per month)
- [ ] Business hours: 24/7 (influencers work all hours)
- [ ] Maintenance windows:
  - Scheduled: 2 AM - 4 AM Vietnam time (lowest traffic)
  - Notify users 48 hours advance
  - Max 2 hours downtime per window
- [ ] High availability setup:
  - Load balancer (2+ app servers)
  - Database replication (primary + read replica)
  - Auto-scaling (scale up if CPU >70%)
- [ ] Health checks:
  - Ping every 30 seconds
  - Alert if 3 consecutive failures
  - Auto-restart unhealthy containers
- [ ] Monitoring: Uptime monitoring via UptimeRobot, PagerDuty alerts

**Rationale:** Campaigns có deadlines. If system down khi influencer cần submit → miss deadline → payment issues.

---

### NFR-003: Security - Data Encryption

**Priority:** Must Have

**Description:**
All sensitive data (personal info, bank accounts, eKYC docs) phải encrypted at rest và in transit.

**Acceptance Criteria:**
- [ ] Encryption in transit:
  - HTTPS/TLS 1.3 for all connections
  - Certificate from trusted CA (Let's Encrypt)
  - HSTS header (force HTTPS)
  - Certificate auto-renewal
- [ ] Encryption at rest:
  - Database: Encrypt sensitive fields (bank account, national ID, phone)
  - File storage: Encrypt uploaded files (eKYC photos, content submissions)
  - Backups: Encrypted before storage
- [ ] Key management:
  - Use AWS KMS or HashiCorp Vault
  - Rotate encryption keys annually
  - Separate keys per environment (prod, staging)
- [ ] Password hashing:
  - Bcrypt with salt (cost factor: 12)
  - Never store plaintext passwords
- [ ] Compliance: Meet PCI-DSS Level 1 (if handling payments), GDPR Article 32

**Rationale:** Banking data is highly sensitive. Data breach → huge fines + brand damage.

---

### NFR-004: Security - Authentication & Authorization

**Priority:** Must Have

**Description:**
System phải có strong authentication (login security) và authorization (access control).

**Acceptance Criteria:**
- [ ] Authentication:
  - JWT tokens (access token + refresh token)
  - Access token: 15 minutes expiry
  - Refresh token: 7 days expiry
  - Secure cookies (HttpOnly, Secure, SameSite)
  - Multi-factor authentication (MFA) for admins (optional for influencers)
- [ ] Password policy:
  - Min 8 characters
  - Must include: uppercase, lowercase, number, special char
  - Password strength meter
  - Prevent common passwords (check against leaked DB)
- [ ] Account security:
  - Rate limiting: Max 5 login attempts per 15 minutes
  - Account lockout after 5 failed attempts (unlock after 30 mins)
  - Email notification on new login from unknown device
  - Session timeout after 30 mins inactivity
- [ ] Authorization (RBAC - Role-Based Access Control):
  - Roles: Influencer, Brand, Admin
  - Permissions per role:
    - Influencer: Can view own profile, apply to campaigns, submit content
    - Brand: Can browse influencers, create campaigns, review submissions
    - Admin: Can approve influencers, view audit logs, manage system settings
  - API: Check permissions on every request
  - Frontend: Hide UI elements based on role (but still check backend)

**Rationale:** Prevent unauthorized access. If influencer account hacked → attacker could submit inappropriate content.

---

### NFR-005: Scalability - Concurrent Users

**Priority:** Should Have

**Description:**
System phải handle growth từ 200 influencers (Phase 1) đến 5,000 influencers (Year 2).

**Acceptance Criteria:**
- [ ] Concurrent users supported:
  - Phase 1: 100 concurrent users
  - Year 1: 500 concurrent users
  - Year 2: 2,000 concurrent users
- [ ] Database scalability:
  - PostgreSQL or MongoDB with indexing
  - Read replicas for heavy read queries
  - Connection pooling (max 100 connections)
- [ ] Application scalability:
  - Horizontal scaling (add more app servers)
  - Stateless app servers (no session state in memory)
  - Load balancer distributes traffic
- [ ] CDN for static assets:
  - Cloudflare or AWS CloudFront
  - Serve images, CSS, JS from edge locations
  - Reduce origin server load
- [ ] Performance testing:
  - Load test with 500 concurrent users (Year 1 target)
  - Stress test to find breaking point
  - Monitor: Response time, error rate, throughput

**Rationale:** If viral campaign → sudden traffic spike. System must not crash.

---

### NFR-006: Reliability - Error Handling & Graceful Degradation

**Priority:** Must Have

**Description:**
System phải handle errors gracefully, không crash, và provide helpful error messages.

**Acceptance Criteria:**
- [ ] Error handling:
  - All API errors caught, logged, and return user-friendly messages
  - Never expose stack traces or sensitive info to users
  - Error codes: 400 (bad request), 401 (unauthorized), 403 (forbidden), 404 (not found), 500 (server error)
- [ ] User-friendly error messages:
  - "We couldn't load your profile. Please try again." (instead of "500 Internal Server Error")
  - "This email is already registered." (instead of "Duplicate key violation")
  - Actionable: "Check your internet connection and try again"
- [ ] Graceful degradation:
  - If Diso API down → Allow influencer self-report metrics (flag for review)
  - If image upload fails → Retry automatically, then show error
  - If email service down → Queue emails, send when service recovers
- [ ] Retry logic:
  - Network requests: Retry 3 times with exponential backoff
  - Queue jobs: Retry failed jobs (max 5 attempts)
  - Show loading state during retries
- [ ] Offline support (nice-to-have):
  - Service worker caches app shell
  - Can view cached profiles offline
  - Show "You are offline" banner

**Rationale:** Errors happen. Users should not be stuck or frustrated.

---

### NFR-007: Maintainability - Code Quality & Documentation

**Priority:** Should Have

**Description:**
Codebase phải maintainable để developers mới có thể onboard nhanh và fix bugs efficiently.

**Acceptance Criteria:**
- [ ] Code quality:
  - Linting: ESLint (frontend), golangci-lint (backend)
  - Code formatting: Prettier (auto-format on save)
  - Type safety: TypeScript (frontend), Go (backend)
  - Code coverage: >70% (unit + integration tests)
- [ ] Documentation:
  - README per repository (setup instructions, architecture overview)
  - API documentation: OpenAPI/Swagger spec
  - Inline comments for complex logic
  - Architecture diagrams (C4 model)
- [ ] Code review:
  - All PRs require 1 approval
  - Automated checks: Linting, tests, build
  - Review checklist: Security, performance, tests, documentation
- [ ] Version control:
  - Git branching strategy: main (production), develop (staging), feature/* (dev)
  - Conventional commits: feat:, fix:, docs:, refactor:
  - Semantic versioning: v1.0.0, v1.1.0, v2.0.0
- [ ] Dependency management:
  - Lock files: package-lock.json, go.sum
  - Automated dependency updates: Dependabot
  - Security scanning: Snyk, npm audit

**Rationale:** TCB cần maintain hệ thống 5+ years. Clean code = lower maintenance cost.

---

### NFR-008: Usability - Accessibility (WCAG 2.1 AA)

**Priority:** Should Have

**Description:**
System phải accessible cho users với disabilities (chi tiết trong FR-025).

**Acceptance Criteria:**
- [ ] WCAG 2.1 Level AA compliance (see FR-025 for details)
- [ ] Lighthouse accessibility score >90
- [ ] Keyboard navigation support
- [ ] Screen reader support

**Rationale:** Inclusivity. Some influencers may have visual/motor impairments.

---

### NFR-009: Compatibility - Browser & Device Support

**Priority:** Must Have

**Description:**
System phải work trên all major browsers và devices mà users sử dụng.

**Acceptance Criteria:**
- [ ] Browser support:
  - Chrome (latest 2 versions)
  - Safari (latest 2 versions) - important for iOS
  - Firefox (latest 2 versions)
  - Edge (latest 2 versions)
- [ ] Device support:
  - iOS: iPhone (iOS 14+), iPad
  - Android: Samsung, Xiaomi, Oppo (Android 10+)
  - Desktop: Windows, macOS, Linux
- [ ] Screen sizes:
  - Mobile: 375px - 428px (iPhone SE to iPhone 14 Pro Max)
  - Tablet: 768px - 1024px (iPad, Android tablets)
  - Desktop: 1280px - 1920px (laptop to 4K monitor)
- [ ] Testing matrix:
  - Test on real devices (not just emulators)
  - BrowserStack for cross-browser testing
  - Minimum 5 device types tested per release

**Rationale:** Users có diverse devices. Cannot assume everyone has latest iPhone.

---

### NFR-010: Data Retention & GDPR Compliance

**Priority:** Must Have

**Description:**
System phải comply với GDPR và Vietnam Personal Data Protection Decree 13/2023.

**Acceptance Criteria:**
- [ ] Data retention policy:
  - Active user data: Retained indefinitely (while account active)
  - Inactive users (no login 2 years): Email reminder before deletion
  - Deleted accounts: Soft delete 30 days, then hard delete
  - Audit logs: Retained 5 years (SBV requirement)
  - eKYC documents: Retained 5 years, then auto-delete
- [ ] User rights (GDPR Article 15-20):
  - Right to access: Users can download their data (JSON export)
  - Right to rectification: Users can edit profile data
  - Right to erasure: Users can delete account (with confirmation)
  - Right to data portability: Export data in machine-readable format
  - Right to object: Users can opt-out of marketing emails
- [ ] Consent management:
  - Clear consent checkboxes (not pre-checked)
  - Granular: Consent for data processing, marketing, third-party sharing
  - Revocable: Users can withdraw consent anytime
  - Audit trail: Log when consent given, withdrawn
- [ ] Data minimization:
  - Only collect data necessary for service
  - Don't ask for data "just in case"
  - Regularly review if old data still needed
- [ ] Data breach response:
  - Detect breach within 24 hours (monitoring, alerts)
  - Notify authorities within 72 hours (GDPR Article 33)
  - Notify affected users within 72 hours (if high risk)
  - Incident response plan documented

**Rationale:** GDPR fines up to 4% of annual revenue. Vietnam Decree 13/2023 has similar penalties.

---

## Epics

### Epic Summary

| Epic ID | Epic Name | Priority | FRs Included | Story Estimate | Business Value |
|---------|-----------|----------|--------------|----------------|----------------|
| EPIC-01 | Influencer Registration & Profile Management | Must Have | FR-001 to FR-006 | 15-20 stories | Core functionality - without this, no influencers can join |
| EPIC-02 | Brand Portal - Influencer Discovery & Browsing | Must Have | FR-007 to FR-011 | 12-18 stories | Core functionality - brands need to find influencers |
| EPIC-03 | Influencer Profile Submission & Campaign Interaction | Must Have | FR-012 to FR-015 | 10-15 stories | Core workflow - influencers apply & submit content |
| EPIC-04 | Data Integration & Synchronization | Must Have | FR-016 to FR-019 | 8-12 stories | Backend infrastructure - ensures data accuracy |
| EPIC-05 | System Administration & Compliance | Must Have | FR-020 to FR-022 | 6-10 stories | Legal/compliance requirement - cannot launch without |
| EPIC-06 | User Experience & Interface | Should Have | FR-023 to FR-025 | 8-12 stories | Quality of life - improves adoption |

**Total Estimated Stories: 59-87 stories**

---

## User Flows

### Flow 1: Influencer Registration (TCB Portal Direct - Path A)

```
┌────────────────────────────────────────────────────────────┐
│  INFLUENCER REGISTRATION FLOW (TCB PORTAL DIRECT)          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1. Landing Page                                            │
│     User visits: tcb.influencer.vn                          │
│     Sees: Welcome message, benefits, "Get Started" button   │
│     ↓ Clicks "Get Started"                                  │
│                                                            │
│  2. Step 1/3: Personal Info (Tier 1 - 5 mins)              │
│     Form fields:                                            │
│     - Full name, Display name, DOB, Gender                  │
│     - Phone (+ OTP verification)                            │
│     - Email (+ email verification)                          │
│     - Location (city dropdown)                              │
│     - National ID (for eKYC later)                          │
│     ↓ Clicks "Continue to Step 2"                           │
│     ✅ Auto-save (can resume later)                         │
│                                                            │
│  3. Step 2/3: First Profile (5 mins)                        │
│     "Add Your Social Media Profile"                         │
│     - Select platform: ○ Instagram ○ Facebook ○ TikTok      │
│     - Enter handle: [@beauty_ig]                            │
│     - Click "Verify Account"                                │
│       → OAuth flow OR paste verification code               │
│     - Auto-fetch: 500K followers ✓ 4.2% engagement ✓        │
│     - Categories: [✓] Beauty [✓] Lifestyle                  │
│     - Niche: "Beauty product reviews for millennials"       │
│     - Portfolio: [Paste 3 best post links]                  │
│     - Rate range: 8M - 12M VND (suggested: 8-12M)           │
│     ↓ Clicks "Continue to Step 3"                           │
│     ✅ Auto-save                                             │
│                                                            │
│  4. Step 3/3: Compliance (2 mins)                           │
│     Required checkboxes:                                    │
│     [✓] I am 18 years or older                              │
│     [✓] I have the right to work in Vietnam                 │
│     [✓] I agree to use #ad/#sponsored tags                  │
│     [✓] I consent to data processing (Privacy Policy)       │
│     [✓] I agree to Terms & Conditions                       │
│     Finance questions:                                      │
│     - TCB customer? ○ Yes ○ No                              │
│     - Interest in finance campaigns? ○ Very ○ Moderate ○ Not│
│     ↓ Clicks "Complete Registration"                        │
│                                                            │
│  5. eKYC Verification (3 mins)                              │
│     "One more step: Verify your identity"                   │
│     - Upload National ID (front + back)                     │
│     - Take selfie (liveness: blink, turn head)              │
│     - System processes...                                   │
│     - Result: ✅ Verified OR ❌ Failed (retry)               │
│     ↓ eKYC completes                                        │
│                                                            │
│  6. Success! Dashboard                                      │
│     "Welcome, [Name]! Your profile is 28% complete"         │
│     Suggested actions:                                      │
│     1. Complete Tier 2 (audience demographics) → 66%        │
│     2. Browse available campaigns                           │
│     3. Add more social profiles                             │
│                                                            │
│  ═══════════════════════════════════════════════════════   │
│  Total Time: ~15 minutes                                    │
│  Profile Completion: 28% (Tier 1 done)                      │
│  Status: Pending Admin Approval (24-48 hours)               │
└────────────────────────────────────────────────────────────┘
```

---

### Flow 2: Brand Searches for Influencers

```
┌────────────────────────────────────────────────────────────┐
│  BRAND SEARCHES FOR INFLUENCERS                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1. Brand Portal: Influencer Pool                           │
│     User (Brand Manager) logged in                          │
│     Navigates to: /brand/influencer-pool                    │
│     Sees: List of influencers (default: all active)         │
│     ↓                                                       │
│                                                            │
│  2. Apply Filters                                           │
│     Opens filter sidebar                                    │
│     Selects:                                                │
│     - Platform: [✓] Instagram                               │
│     - Follower Range: 100K - 500K                           │
│     - Categories: [✓] Beauty [✓] Lifestyle                  │
│     - Finance Affinity: 60-100                              │
│     - Location: [✓] HCMC [✓] Hanoi                          │
│     - Audience Age: [✓] 25-34                               │
│     ↓ Clicks "Apply Filters"                                │
│     Results update: 42 influencers match                    │
│                                                            │
│  3. Sort & Browse Results                                   │
│     Sorts by: Engagement Rate (high to low)                 │
│     Views table:                                            │
│     ┌────────────────────────────────────────────────┐     │
│     │ Name      Platform  Followers  Engagement  Rate│     │
│     │ Beauty Q  IG        500K       4.2% ✅    10M  │     │
│     │ Lifestyle IG        300K       3.8%       7M   │     │
│     │ ...                                             │     │
│     └────────────────────────────────────────────────┘     │
│     ↓ Clicks on "Beauty Queen" row                          │
│                                                            │
│  4. View Profile Detail                                     │
│     Sees comprehensive profile:                             │
│     - Header: Photo, name, finance affinity: 82/100         │
│     - Social profiles: Instagram 500K, Facebook 200K        │
│     - Audience: 50% age 25-34, 80% female, 40% HCMC        │
│     - Portfolio: 5 beauty product posts                     │
│     - Pricing: IG post 10M, IG reel 12M                     │
│     ↓ Decides: Good fit for credit card campaign            │
│                                                            │
│  5. Save to Favorites                                       │
│     Clicks "Add to Favorites" ❤️                            │
│     Success: "Added to Favorites"                           │
│     ↓ Continues browsing...                                 │
│                                                            │
│  6. Compare Influencers                                     │
│     Clicks "Add to Compare" on 3 influencers                │
│     Compare tray shows: 3 mini cards                        │
│     ↓ Clicks "Compare Now"                                  │
│     Sees side-by-side comparison table                      │
│     Highlights: Best engagement, lowest rate, best fit      │
│     ↓ Decides on "Beauty Queen"                             │
│                                                            │
│  7. Invite to Campaign                                      │
│     (Out of scope - Phase 3: Campaign Management)           │
│     But button visible: "Invite to Campaign"                │
│                                                            │
│  ═══════════════════════════════════════════════════════   │
│  Total Time: ~10 minutes                                    │
│  Result: Found 3 suitable influencers, favorited 5          │
└────────────────────────────────────────────────────────────┘
```

---

### Flow 3: Influencer Applies to Campaign & Submits Content

```
┌────────────────────────────────────────────────────────────┐
│  INFLUENCER APPLIES TO CAMPAIGN & SUBMITS CONTENT          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1. Browse Campaigns                                        │
│     Influencer logged in → /portal/campaigns                │
│     Sees campaign cards:                                    │
│     ┌─────────────────────────────────┐                    │
│     │ Credit Card for Millennials     │                    │
│     │ Rate: 8-15M VND                 │                    │
│     │ Platform: Instagram             │                    │
│     │ Match: 92% ✅ (high match!)      │                    │
│     │ [View Details]                  │                    │
│     └─────────────────────────────────┘                    │
│     ↓ Clicks "View Details"                                 │
│                                                            │
│  2. Read Campaign Brief                                     │
│     Sees:                                                   │
│     - Campaign goal: Promote TCB Platinum Credit Card       │
│     - Target audience: Millennials 25-34, high income       │
│     - Deliverables: 3 IG posts + 5 IG stories              │
│     - Timeline: Feb 20-28, 2026                             │
│     - Rate: 10M VND                                         │
│     - Requirements: >100K followers, engagement >3%,        │
│       audience 25-34 >30%, willing to create finance content│
│     ↓ Checks: "I meet all requirements ✅"                  │
│     ↓ Clicks "Apply Now"                                    │
│                                                            │
│  3. Application Form                                        │
│     Modal opens:                                            │
│     - Select profile: ○ @beauty_ig (500K, 92% match) ✅     │
│                       ○ @beauty_fb (200K, 65% match)        │
│     - Pre-filled data displayed (followers, engagement, audience)│
│     - Rate expectation: 10M VND (editable)                  │
│     - Campaign questions:                                   │
│       Q: "Have you promoted credit cards before?"           │
│       A: ○ Yes ○ No → Selects "No"                          │
│     - Application message (optional):                       │
│       "I have 500K followers, 50% are millennials in HCMC.  │
│        I've created finance education content before..."    │
│     - [✓] I agree to campaign terms                         │
│     ↓ Clicks "Submit Application"                           │
│     ✅ Success: "Application submitted!"                    │
│                                                            │
│  4. Wait for Brand Review (24-48 hours)                     │
│     Influencer checks: /portal/applications                 │
│     Status: "Under Review"                                  │
│     ↓ Receives email: "Your application was ACCEPTED!"      │
│     Status updated: "Accepted ✅"                            │
│     ↓ Clicks "View Contract"                                │
│                                                            │
│  5. Sign Contract (Out of scope - Phase 3)                  │
│     Reviews contract, e-signs                               │
│     ↓ Contract signed                                       │
│     Status: "Active - Campaign in progress"                 │
│                                                            │
│  6. Create & Post Content (Influencer does this on Instagram)│
│     Influencer creates 3 posts + 5 stories                  │
│     Posts on Instagram with #ad tag                         │
│     ↓ Content live on Instagram                             │
│                                                            │
│  7. Submit Deliverables                                     │
│     Navigates to: /portal/campaigns/[id]/submit             │
│     Deliverable checklist:                                  │
│     - [✓] Instagram Post 1:                                 │
│       - Upload: [beauty-post-1.jpg]                         │
│       - Link: instagram.com/p/abc123                        │
│       - Metrics: 25K likes, 850 comments                    │
│       [Submit]                                              │
│     - [✓] Instagram Post 2: [Similar]                       │
│     - [✓] Instagram Post 3: [Similar]                       │
│     - [✓] Instagram Stories (5x): [Upload screenshots]      │
│     ↓ All submitted                                         │
│     Status: "Submitted - Waiting for Brand Review"          │
│                                                            │
│  8. Brand Reviews & Approves                                │
│     (Brand side - out of influencer's control)              │
│     ↓ Email: "Your deliverables were approved!"             │
│     Status: "Approved ✅"                                    │
│                                                            │
│  9. Payment Processed (Out of scope - Phase 3)              │
│     Status: "Completed - Payment sent"                      │
│     Influencer receives 10M VND to bank account             │
│                                                            │
│  ═══════════════════════════════════════════════════════   │
│  Total Time:                                                │
│  - Application: 10 minutes                                  │
│  - Content creation: 2-3 days                               │
│  - Submission: 15 minutes                                   │
│  Result: Campaign completed, paid 10M VND ✅                 │
└────────────────────────────────────────────────────────────┘
```

---

## Dependencies

### Internal Dependencies

| Dependency | Type | Owner | Status | Impact if Delayed |
|------------|------|-------|--------|-------------------|
| **at-core Backend API** | System | AT Core team | ✅ Active | Cannot integrate with campaigns, influencer approval |
| **at-core Database (MongoDB)** | System | AT Core team | ✅ Active | Cannot store influencer data |
| **influencer-portal (Next.js 16)** | System | Frontend team | ✅ Deployed | Influencer features blocked |
| **brand-portal (Next.js 16)** | System | Frontend team | ✅ Deployed | Brand features blocked |
| **User Authentication (JWT)** | Service | Auth team | ✅ Active | Cannot login users |
| **File Upload Service (S3/Cloudinary)** | Service | Infrastructure | ⏳ Pending setup | Cannot upload eKYC docs, content submissions |

### External Dependencies

| Dependency | Provider | Type | SLA | Fallback |
|------------|----------|------|-----|----------|
| **Diso Influence-Meter API** | Diso | API Service | 99.5% uptime | Allow influencer self-report (flagged for review) |
| **eKYC Service** | VNPT / FPT | API Service | 99% uptime | Manual admin review of ID uploads |
| **Email Service** | SendGrid / AWS SES | API Service | 99.9% uptime | Queue emails, retry when service recovers |
| **SMS OTP Service** | Twilio / VNPT | API Service | 99.5% uptime | Alternative: Email OTP |
| **CDN** | Cloudflare / AWS CloudFront | Infrastructure | 100% uptime (guaranteed) | Direct server delivery (slower) |
| **Payment Gateway** | TCB Internal | API Service | 99.9% uptime | Manual bank transfer processing |

### Infrastructure Dependencies

| Dependency | Environment | Owner | Status |
|------------|-------------|-------|--------|
| **Production MongoDB Cluster** | AWS / GCP | DevOps | ✅ Provisioned |
| **Staging MongoDB** | AWS / GCP | DevOps | ✅ Provisioned |
| **Production App Servers (2x)** | AWS EC2 / GCP Compute | DevOps | ✅ Running |
| **Load Balancer** | AWS ALB / GCP LB | DevOps | ✅ Configured |
| **SSL Certificate** | Let's Encrypt | DevOps | ✅ Auto-renewal setup |
| **CI/CD Pipeline** | GitHub Actions | DevOps | ✅ Active |
| **Monitoring (APM)** | DataDog / New Relic | DevOps | ⏳ Pending setup |

---

## Assumptions

1. **User Adoption:**
   - Assume 200 influencers register in first 3 months
   - Assume 70% profile completion rate (Tier 1 + Tier 2)
   - Assume 30% of invited influencers apply to campaigns

2. **Technical:**
   - Assume Diso Influence-Meter API is stable (99.5% uptime)
   - Assume AT Core middleware can handle 100 req/s
   - Assume MongoDB can scale to 10,000 influencers (Year 2)
   - Assume eKYC provider has 95% success rate (5% need manual review)

3. **Business:**
   - Assume TCB marketing team will create 5+ campaigns per month
   - Assume average campaign invites 10 influencers
   - Assume average influencer participates in 2 campaigns per quarter
   - Assume TCB budget for influencer payments: 100M+ VND per month

4. **Compliance:**
   - Assume all influencers are Vietnam-based (no international tax complications)
   - Assume SBV regulations remain stable (no major changes mid-project)
   - Assume GDPR/Decree 13/2023 compliance is sufficient (no additional privacy laws)

5. **Data Quality:**
   - Assume Diso social crawl data is 90% accurate
   - Assume influencers self-report audience demographics accurately (validated by brands over time)
   - Assume 10% of influencer registrations are fake/spam (filtered by admin approval)

---

## Out of Scope (Phase 3 - Future PRD)

The following features are **NOT included** in this PRD and will be addressed in a separate PRD for Phase 3:

### Brand Campaign Management
- ❌ Campaign creation UI (brand creates campaigns)
- ❌ Campaign brief editor (rich text, file uploads)
- ❌ Campaign invites (brand invites influencers)
- ❌ Contract generation & e-signature
- ❌ Content review workflow (brand reviews submitted content)
- ❌ Brand rating form (brand rates influencer after campaign)
- ❌ Payment processing (brand pays influencer)

### Advanced Features
- ❌ Messaging/Chat (brand ↔ influencer communication)
- ❌ In-app notifications (push notifications)
- ❌ Analytics dashboard (campaign ROI, influencer performance trends)
- ❌ Automated influencer recommendations (ML-based matching)
- ❌ Influencer tiers/badges (gold, platinum, certified)
- ❌ Referral program (influencer refers other influencers)
- ❌ Multi-language support (English) - Low priority for TCB Vietnam market

### Admin Portal
- ❌ System configuration UI (admin settings)
- ❌ User management (admin creates brand users)
- ❌ Reporting dashboard (business intelligence)
- ❌ Fraud detection (automated flagging)

### Integrations
- ❌ CRM integration (Salesforce, HubSpot)
- ❌ Accounting integration (QuickBooks, Xero)
- ❌ Social media scheduling (Buffer, Hootsuite)

**Note:** These features may be added in Phase 3 or later phases based on user feedback and business priorities.

---

## Open Questions

These questions need to be resolved before finalizing requirements:

### Technical Questions

1. **Q: Which eKYC provider should we use?**
   - Options: VNPT eKYC, FPT eKYC, VietGuys
   - Decision needed by: Week 1 of implementation
   - Owner: Tech Lead + Procurement

2. **Q: How will AT Core authenticate TCB API calls?**
   - Options: JWT, API Key, OAuth 2.0
   - Decision needed by: Before Phase 4 implementation
   - Owner: AT Core team

3. **Q: What is Diso API rate limit?**
   - Need to know: Max requests per minute, per day
   - Impact: Design queuing strategy
   - Owner: Diso team (external)

4. **Q: Where to store uploaded files (eKYC docs, content submissions)?**
   - Options: AWS S3, Google Cloud Storage, Cloudinary
   - Decision needed by: Before FR-015 implementation
   - Owner: DevOps team

### Business Questions

5. **Q: What is the minimum influencer follower count to be eligible?**
   - Current assumption: No minimum (even 1K followers can register)
   - Need confirmation from: Marketing team
   - Impact: Filter requirements

6. **Q: Should influencers be auto-approved or manual review required?**
   - Current assumption: Manual review (admin approves within 24-48 hours)
   - Need confirmation from: Compliance team
   - Impact: Onboarding time

7. **Q: What happens if influencer doesn't submit on time?**
   - Penalties? Warning system? Payment reduction?
   - Need confirmation from: Legal + Marketing
   - Impact: Contract terms, payment logic

### Compliance Questions

8. **Q: Does TCB need influencer data for 5 years (SBV requirement)?**
   - If yes: Cannot fully delete accounts (soft delete only)
   - Need confirmation from: Legal/Compliance
   - Impact: Data retention policy (NFR-010)

9. **Q: Are there restrictions on who can promote financial products?**
   - E.g., Age >21? Finance certification? No criminal record?
   - Need confirmation from: SBV liaison / Legal
   - Impact: Approval criteria (FR-020)

10. **Q: How to handle influencer tax reporting?**
    - Issue 1099 equivalent? Withholding tax?
    - Need confirmation from: Finance team
    - Impact: Payment processing (Phase 3)

**Action Items:**
- [ ] Schedule stakeholder meeting to resolve Questions 1-10
- [ ] Document decisions in this PRD (update version 1.1)
- [ ] Communicate decisions to development team

---

## Stakeholders

| Role | Name | Department | Responsibility | Contact |
|------|------|------------|----------------|---------|
| **Executive Sponsor** | [Name TBD] | Executive | Final approval, budget | [email] |
| **Product Owner** | [Name TBD] | Marketing | Define requirements, prioritization | [email] |
| **Project Manager** | [Name TBD] | IT/PMO | Timeline, resources, coordination | [email] |
| **Tech Lead** | [Name TBD] | Engineering | Architecture, technical decisions | [email] |
| **Frontend Lead** | [Name TBD] | Engineering | Influencer/Brand portal implementation | [email] |
| **Backend Lead** | [Name TBD] | Engineering | API, database, integrations | [email] |
| **UX Designer** | [Name TBD] | Design | User flows, wireframes, UI design | [email] |
| **QA Lead** | [Name TBD] | QA | Test planning, quality assurance | [email] |
| **DevOps Engineer** | [Name TBD] | Infrastructure | Deployment, monitoring, scaling | [email] |
| **Compliance Officer** | [Name TBD] | Legal/Compliance | GDPR, SBV regulations, eKYC | [email] |
| **Marketing Manager** | [Name TBD] | Marketing | Campaign requirements, brand needs | [email] |
| **Finance Manager** | [Name TBD] | Finance | Payment processing, tax reporting | [email] |
| **External: Diso** | [Name TBD] | Diso | Influence-Meter API support | [email] |
| **External: AT Core** | [Name TBD] | AT Core | Middleware, tenant management | [email] |

---

## Appendices

### Appendix A: Referenced Plans & Brainstorming Documents

This PRD consolidates requirements from the following existing documents:

**Implementation Plans:**
1. [plans/20260212-1430-influencer-portal-week2/plan.md](../plans/20260212-1430-influencer-portal-week2/plan.md)
   - Influencer Portal (profile detail, profile list, submission)
   - Phases 01-08 implementation (completed)

2. [plans/20260212-1234-brand-influencer-menu/plan.md](../plans/20260212-1234-brand-influencer-menu/plan.md)
   - Brand Portal influencer browsing
   - Search, filters, profile detail view

**Brainstorming Documents:**
3. [.bmad/influencer-library-4sources/brainstorming-influencer-library-4sources-2026-02-13.md](../.bmad/influencer-library-4sources/brainstorming-influencer-library-4sources-2026-02-13.md)
   - 4 Data Sources architecture
   - 3-Tier architecture (TCB → AT Core → Diso)
   - Overall Quality Score formula

4. [.bmad/influencer-library-4sources/brainstorming-tcb-influencer-data-requirements-2026-02-13.md](../.bmad/influencer-library-4sources/brainstorming-tcb-influencer-data-requirements-2026-02-13.md)
   - 138 data points (Tier 1, 2, 3)
   - Form UX design (3-step, auto-save, AI pre-fill)
   - Context-aware onboarding (TCB Portal vs Marketplace)

5. [.bmad/influencer-library-4sources/brainstorming-influencer-vs-profile-multi-account-2026-02-13.md](../.bmad/influencer-library-4sources/brainstorming-influencer-vs-profile-multi-account-2026-02-13.md)
   - Influencer (Person) vs Profile (Social Account) data model
   - Multi-profile support (1 influencer → many profiles)
   - Database schema (influencers + social_profiles tables)

---

### Appendix B: Traceability Matrix

Maps Functional Requirements → Epics → User Stories

| FR ID | FR Name | Epic | Story Count |
|-------|---------|------|-------------|
| FR-001 | Influencer Account Creation | EPIC-01 | 3-4 |
| FR-002 | Multi-Profile Support | EPIC-01 | 4-5 |
| FR-003 | Profile Data Collection (Tier 1, 2, 3) | EPIC-01 | 5-6 |
| FR-004 | Social Metrics Auto-Fetch | EPIC-01 | 2-3 |
| FR-005 | Profile Editing & Updates | EPIC-01 | 2-3 |
| FR-006 | Profile Status Management | EPIC-01 | 1-2 |
| FR-007 | Influencer Search & Filters | EPIC-02 | 3-4 |
| FR-008 | Influencer List View with Sorting | EPIC-02 | 2-3 |
| FR-009 | Influencer Profile Detail Page | EPIC-02 | 3-4 |
| FR-010 | Influencer Comparison | EPIC-02 | 2-3 |
| FR-011 | Favorite/Bookmark Influencers | EPIC-02 | 2-3 |
| FR-012 | Campaign Browsing (Influencer Portal) | EPIC-03 | 2-3 |
| FR-013 | Campaign Application | EPIC-03 | 3-4 |
| FR-014 | Application Status Tracking | EPIC-03 | 2-3 |
| FR-015 | Content Submission | EPIC-03 | 3-4 |
| FR-016 | Diso Influence-Meter API Integration | EPIC-04 | 3-4 |
| FR-017 | AT Core Middleware (ID Mapping) | EPIC-04 | 2-3 |
| FR-018 | Performance Data Push (Source 3) | EPIC-04 | 1-2 |
| FR-019 | Brand Rating Push (Source 4) | EPIC-04 | 1-2 |
| FR-020 | Influencer Approval Workflow | EPIC-05 | 2-3 |
| FR-021 | eKYC Integration | EPIC-05 | 3-4 |
| FR-022 | Audit Logs & Compliance Reporting | EPIC-05 | 2-3 |
| FR-023 | Responsive Design (Mobile-First) | EPIC-06 | 3-4 |
| FR-024 | Multi-Language Support (i18n) | EPIC-06 | 2-3 |
| FR-025 | Accessibility (WCAG 2.1 AA) | EPIC-06 | 3-4 |

**Total Stories: 59-87 stories**

---

### Appendix C: Prioritization Summary

**Must Have (MVP - Cannot launch without):**
- EPIC-01: Influencer Registration & Profile Management (15-20 stories)
- EPIC-02: Brand Portal - Influencer Discovery (12-18 stories)
- EPIC-03: Campaign Interaction (10-15 stories)
- EPIC-04: Data Integration (8-12 stories)
- EPIC-05: Compliance (6-10 stories)
- NFR-001 to NFR-010 (Performance, Security, Scalability, etc.)

**Should Have (High value, but workaround exists):**
- EPIC-06: UX/Accessibility improvements (8-12 stories)
- FR-010: Influencer Comparison (nice-to-have)
- FR-011: Favorites (nice-to-have)
- FR-018, FR-019: Data push flows (can be manual initially)

**Could Have (Nice-to-have, low priority):**
- FR-024: Multi-language (English) - TCB focuses on Vietnam market
- Advanced analytics, reporting (Phase 4)

---

### Appendix D: Glossary

| Term | Definition |
|------|------------|
| **Influencer** | Person who creates content on social media and has influence over their followers' purchasing decisions |
| **Profile** | Social media account (Instagram, Facebook, TikTok, etc.) belonging to an influencer |
| **Multi-Profile** | 1 influencer có nhiều social accounts (e.g., Instagram + TikTok) |
| **Campaign** | Marketing initiative where brands collaborate with influencers to promote products |
| **Deliverable** | Content that influencer must create (e.g., 3 Instagram posts, 5 stories) |
| **Finance Affinity Score** | 0-100 score measuring influencer's interest/experience with financial products |
| **Overall Quality Score** | Composite score from 4 sources: Social (30%) + Performance (40%) + Ratings (20%) + Completeness (10%) |
| **Source 1** | Onboarding data (influencer self-reported) |
| **Source 2** | Social crawl data (Diso auto-fetches) |
| **Source 3** | Campaign performance data (TCB pushes after campaign) |
| **Source 4** | Brand ratings (TCB rates influencer after campaign) |
| **eKYC** | Electronic Know Your Customer - identity verification via ID upload + selfie |
| **Tier 1, 2, 3** | Data collection tiers (Tier 1 = essential, Tier 2 = recommended, Tier 3 = optional) |
| **AT Core** | Middleware platform owned by AccessTrade, sits between TCB and Diso |
| **Diso** | Company that owns Influence-Meter API (social scoring, matching) |
| **Influence-Meter** | Diso's API service for influencer scoring and matching |
| **TCB** | Techcombank (client for this project) |
| **SBV** | State Bank of Vietnam (regulator) |
| **GDPR** | General Data Protection Regulation (EU privacy law) |
| **Decree 13/2023** | Vietnam Personal Data Protection Decree (Vietnam's GDPR equivalent) |

---

## Document Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | [Name] | _________ | _____ |
| Tech Lead | [Name] | _________ | _____ |
| Compliance Officer | [Name] | _________ | _____ |
| Executive Sponsor | [Name] | _________ | _____ |

---

**End of PRD**

*Document Generated: 2026-02-13*
*Next Update: After stakeholder review (Version 1.1)*
