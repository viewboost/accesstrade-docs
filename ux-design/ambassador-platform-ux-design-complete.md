# Ambassador Influencer Platform - Complete UX Design

**Date:** 2026-02-06
**Designer:** UX Design Agent (BMAD Method v6)
**Version:** 1.0
**Status:** Ready for Implementation

---

## Executive Summary

Comprehensive UX design cho **Ambassador Influencer Platform** với 3 portals chính:
1. **Influencer Portal** - Cho KOCs/Influencers
2. **Brand Portal** - Cho Brands (Techcombank, Vinfast, etc.)
3. **Admin Portal** - Cho AT Admin và Partner Admin

### Design Scope

| Portal | Screens | User Flows | Components | Priority |
|--------|---------|------------|------------|----------|
| **Influencer Portal** | 12 | 6 | 18 | HIGH |
| **Brand Portal** | 18 | 8 | 25 | HIGHEST |
| **Admin Portal** | 15 | 7 | 22 | MEDIUM |
| **Total** | **45** | **21** | **40+** | - |

### Design Principles

✅ **AI-First** - Neural network visualizations, confidence indicators
✅ **Dark Mode Optimized** - Soft black (#1A1A1A), glassmorphism
✅ **Mobile-First Responsive** - 320px - 1400px+
✅ **WCAG AA Accessible** - 4.5:1+ contrast ratios
✅ **Data-Driven Interface** - Score cards, real-time metrics

### Design System

Uses existing design system:
- `/ambassabor/design-showcase/assets/css/design-system.css`
- `/ambassabor/design-showcase/assets/css/components.css`
- Colors: Electric Blue (#0066FF), Cyber Purple (#9D00FF), Deep Teal (#00A8A8)

---

## Table of Contents

1. [Requirements Analysis](#1-requirements-analysis)
2. [User Personas](#2-user-personas)
3. [Information Architecture](#3-information-architecture)
4. [User Journey Maps](#4-user-journey-maps)
5. [User Flow Diagrams](#5-user-flow-diagrams)
6. [Wireframes - Influencer Portal](#6-wireframes---influencer-portal)
7. [Wireframes - Brand Portal](#7-wireframes---brand-portal)
8. [Wireframes - Admin Portal](#8-wireframes---admin-portal)
9. [Interaction Patterns](#9-interaction-patterns)
10. [Component Specifications](#10-component-specifications)
11. [Accessibility Annotations](#11-accessibility-annotations)
12. [Responsive Strategy](#12-responsive-strategy)
13. [Developer Handoff](#13-developer-handoff)

---

## 1. Requirements Analysis

### 1.1. Functional Requirements Summary

**From PRDs và Roadmap:**

#### Influencer Portal (Clone + Enhance)
- ✅ Profile management (self-service)
- ✅ Campaign invitations (accept/decline/negotiate)
- ✅ Performance dashboard (personal metrics)
- ✅ Earnings & payments tracking
- ✅ Content upload & approval workflow
- ✅ Demographics submission (manual input + OCR)
- ✅ Communication hub (chat with brands)
- ✅ Campaign marketplace (browse, apply)

#### Brand Portal (NEW - Highest Priority)
- 🆕 Campaign creation & management
- 🆕 Influencer discovery & search (AI-powered)
- 🆕 AI-powered matching với scoring
- 🆕 Booking & collaboration tools
- 🆕 Performance analytics & ROI tracking
- 🆕 Payment management (MoMo, ZaloPay)
- 🆕 Communication hub (chat with influencers)
- 🆕 Contract management & e-signatures
- 🆕 TikTok Shop integration (GMV tracking)

#### Admin Portal (From PRD)
- ✅ AT Shared Pool management
- ✅ Partner management (tenants)
- ✅ Approval workflow (submissions)
- ✅ Sync management (with Vendor API)
- ✅ Tenant management (subscriptions)
- ✅ User & permissions
- ✅ Analytics dashboard

### 1.2. Non-Functional Requirements

| Category | Requirement | Impact on UX |
|----------|-------------|--------------|
| **Performance** | Page load < 2s | Loading states, skeleton UI |
| **Usability** | Intuitive navigation | Clear IA, breadcrumbs |
| **Accessibility** | WCAG 2.1 AA | Keyboard nav, screen readers |
| **Compatibility** | Desktop, Tablet, Mobile | Responsive design |
| **Security** | Role-based access | Permission-based UI |

### 1.3. User Roles

| Role | Portal Access | Key Tasks |
|------|---------------|-----------|
| **Influencer** | Influencer Portal | Profile setup, Accept campaigns, Upload content, Track earnings |
| **Brand Manager** | Brand Portal | Create campaigns, Find influencers, Manage bookings, Track ROI |
| **AT Admin** | Admin Portal | Manage pool, Approve submissions, Configure system |
| **Partner Admin** | Admin Portal (limited) | Manage own tenant, View analytics |

---

## 2. User Personas

### 2.1. Influencer Persona

**Name:** Minh Anh (Beauty Creator)
**Age:** 24
**Platform:** TikTok (250K followers)
**Location:** Ho Chi Minh City

**Goals:**
- Find brand collaborations that match her audience
- Manage multiple campaigns efficiently
- Track earnings and get paid quickly
- Build professional portfolio

**Pain Points:**
- Too many manual tasks (email back-and-forth)
- Hard to track which campaigns are profitable
- Delayed payments
- Unclear campaign requirements

**Tech Savvy:** High (uses phone 8+ hours/day)

**Quote:** "I want a platform where I can see all opportunities, accept campaigns with one click, and track everything in one place."

---

### 2.2. Brand Manager Persona

**Name:** Hương (Techcombank Marketing Manager)
**Age:** 32
**Platform:** Desktop (80%), Mobile (20%)
**Location:** Hanoi

**Goals:**
- Launch Tết campaign with 50 influencers quickly
- Find influencers who reach 25-35 age group
- Track ROI and engagement metrics
- Manage budget efficiently

**Pain Points:**
- Hard to find right influencers (manual search)
- Time-consuming negotiation process
- No way to track campaign performance
- Messy communication (email, Zalo, calls)

**Tech Savvy:** Medium (comfortable with web tools)

**Quote:** "I need to see which influencers will deliver the best ROI for my budget, and I need analytics to prove the campaign worked."

---

### 2.3. AT Admin Persona

**Name:** Tuấn (AccessTrade Operations)
**Age:** 28
**Platform:** Desktop (95%)
**Location:** Ho Chi Minh City

**Goals:**
- Maintain high-quality influencer pool
- Approve new influencer submissions quickly
- Monitor system health (sync status)
- Support partners (Techcombank, Vinfast)

**Pain Points:**
- Manual approval takes too long
- Hard to detect fake influencers
- System errors hard to debug
- Too many support requests

**Tech Savvy:** Very High (developer background)

**Quote:** "I need tools to automate approval, detect fraud, and keep the platform running smoothly."

---

## 3. Information Architecture

### 3.1. Portal Navigation Structure

```
INFLUENCER PORTAL
│
├── 🏠 Dashboard
│   ├── Overview metrics (campaigns, earnings)
│   ├── Recent activity feed
│   └── Quick actions
│
├── 👤 My Profile
│   ├── Basic Info (edit)
│   ├── Social Accounts (connect)
│   ├── Demographics (submit)
│   ├── Portfolio (past work)
│   └── Pricing (rate card)
│
├── 💼 Campaigns
│   ├── Invitations (pending, accepted, declined)
│   ├── Active Campaigns
│   ├── Completed Campaigns
│   └── Marketplace (browse available)
│
├── 📊 Performance
│   ├── My Analytics (reach, engagement)
│   ├── Top Performing Content
│   └── Audience Demographics
│
├── 💰 Earnings
│   ├── Overview (total, this month)
│   ├── Payment History
│   ├── Pending Payments
│   └── Payment Settings (bank, MoMo)
│
├── 📤 Content
│   ├── Upload Content
│   ├── Pending Approval
│   ├── Approved Content
│   └── Asset Library
│
└── 💬 Messages
    ├── Conversations (with brands)
    ├── Notifications
    └── Support Tickets
```

```
BRAND PORTAL (NEW)
│
├── 🏠 Dashboard
│   ├── Campaign Overview
│   ├── Performance Metrics
│   ├── Pending Tasks
│   └── Recent Activity
│
├── 🎯 Campaigns
│   ├── Active Campaigns
│   ├── Draft Campaigns
│   ├── Completed Campaigns
│   └── Create New Campaign (wizard)
│
├── 🔍 Discover Influencers
│   ├── Search & Filters (AI-powered)
│   ├── AI Matching (recommendations)
│   ├── Saved Searches
│   └── Influencer Collections
│
├── 📋 Bookings
│   ├── Pending Invitations
│   ├── Confirmed Bookings
│   ├── In Progress
│   └── Completed
│
├── 📊 Analytics
│   ├── Campaign Performance
│   ├── ROI Dashboard
│   ├── Influencer Rankings
│   ├── Content Performance
│   └── TikTok Shop GMV (if integrated)
│
├── 💳 Payments
│   ├── Budget Overview
│   ├── Payment Queue
│   ├── Payment History
│   └── Invoice Management
│
├── 📄 Contracts
│   ├── Contract Templates
│   ├── Pending Signatures
│   ├── Active Contracts
│   └── Contract Library
│
└── 💬 Messages
    ├── Influencer Conversations
    ├── Notifications
    └── Support
```

```
ADMIN PORTAL
│
├── 🏠 Dashboard
│   ├── System Overview
│   ├── Pool Statistics
│   ├── Partner Activity
│   └── Alerts
│
├── 👥 AT Shared Pool
│   ├── Influencer List (all)
│   ├── Add Influencer (URL / Manual)
│   ├── Bulk Import (CSV)
│   ├── Sync Management
│   └── Pool Analytics
│
├── ✅ Approval Workflow
│   ├── Pending Submissions
│   ├── Review Queue
│   ├── Approved/Rejected History
│   └── Auto-Approve Rules
│
├── 🏢 Partner Management
│   ├── Partner List (tenants)
│   ├── Create Partner
│   ├── Subscriptions & Quotas
│   ├── API Key Management
│   └── Usage Analytics
│
├── 🔄 Sync Management
│   ├── Sync Status Dashboard
│   ├── Failed Syncs
│   ├── Sync Schedule
│   └── Sync Logs
│
├── 👥 Users & Permissions
│   ├── User List
│   ├── Roles & Permissions
│   ├── Activity Logs
│   └── Invite Users
│
└── ⚙️ Settings
    ├── Platform Settings
    ├── Email Templates
    ├── Webhook Configuration
    └── System Logs
```

### 3.2. Portal Comparison Matrix

| Feature | Influencer | Brand | Admin |
|---------|------------|-------|-------|
| **Dashboard** | Personal metrics | Campaign overview | System overview |
| **Search** | Campaign marketplace | Influencer discovery | Pool management |
| **Create** | Upload content | Create campaign | Add influencer |
| **Manage** | Accept invitations | Manage bookings | Approve submissions |
| **Analytics** | Personal performance | Campaign ROI | Platform analytics |
| **Payments** | Track earnings | Manage budget | Monitor transactions |
| **Messages** | Chat with brands | Chat with influencers | Support tickets |

---

## 4. User Journey Maps

### 4.1. Influencer Journey: From Registration to First Payment

**Scenario:** Minh Anh discovers platform, signs up, completes first campaign, receives payment

**Stages:**

#### Stage 1: Awareness & Registration (Day 1)
**Touchpoint:** Landing page → Sign up
**Actions:**
- Sees platform advertised on Facebook
- Clicks "Join as Influencer"
- Fills sign-up form (name, email, phone, platform URLs)
- Verifies email

**Emotions:** 😊 Curious, hopeful
**Pain Points:** None (simple form)

#### Stage 2: Profile Setup (Day 1-2)
**Touchpoint:** Onboarding wizard
**Actions:**
- Connects TikTok account (OAuth)
- System auto-fetches followers, engagement
- Uploads profile photo, bio
- Sets pricing (per post, per story)
- Submits for approval

**Emotions:** 😊 Excited
**Pain Points:** ⚠️ Waiting for approval (24-48h)

#### Stage 3: Browse Campaigns (Day 3)
**Touchpoint:** Campaign Marketplace
**Actions:**
- Browses available campaigns
- Filters by category (Beauty)
- Clicks campaign: "Techcombank Tết 2026"
- Reads brief, budget, requirements
- Clicks "Apply"

**Emotions:** 😃 Motivated
**Pain Points:** None

#### Stage 4: Accept Invitation (Day 4)
**Touchpoint:** Email notification → Platform
**Actions:**
- Receives email: "You've been selected!"
- Logs in, sees invitation
- Reviews campaign details
- Accepts invitation
- Signs digital contract (one click)

**Emotions:** 🤩 Thrilled
**Pain Points:** None

#### Stage 5: Create Content (Day 5-7)
**Touchpoint:** Campaign dashboard → Content upload
**Actions:**
- Creates TikTok video (per brief)
- Uploads video to platform for approval
- Waits for brand approval
- Receives approval notification
- Posts on TikTok with campaign hashtag

**Emotions:** 😊 Productive
**Pain Points:** ⚠️ Video approval delay (1 day)

#### Stage 6: Track Performance (Day 8-14)
**Touchpoint:** Performance dashboard
**Actions:**
- Checks campaign dashboard daily
- Sees real-time metrics (views, likes, comments)
- Compares with other influencers (leaderboard)

**Emotions:** 😊 Engaged
**Pain Points:** None

#### Stage 7: Get Paid (Day 15)
**Touchpoint:** Earnings → Payment
**Actions:**
- Campaign marked "Completed"
- Sees payment pending (VND 5,000,000)
- Receives MoMo notification: "Payment received"
- Checks bank account

**Emotions:** 🤩 Satisfied, loyal
**Pain Points:** None (fast payment = happy influencer)

**Overall Sentiment:** ⭐⭐⭐⭐⭐ (5/5)

---

### 4.2. Brand Journey: From Campaign Creation to ROI Report

**Scenario:** Hương creates Tết campaign, books 50 influencers, tracks performance

**Stages:**

#### Stage 1: Awareness & Login (Day 1)
**Touchpoint:** AT sales team → Demo → Contract signed
**Actions:**
- AT sales shows platform demo
- Hương signs contract (Techcombank partnership)
- Receives login credentials
- Logs in to Brand Portal

**Emotions:** 😊 Curious
**Pain Points:** None

#### Stage 2: Create Campaign (Day 1)
**Touchpoint:** Campaign creation wizard
**Actions:**
- Clicks "Create New Campaign"
- Step 1: Basic Info (name, category, budget)
- Step 2: Target Audience (age 25-35, female 70%, location)
- Step 3: Deliverables (50 posts, 1 story each)
- Step 4: Timeline (Feb 1 - Feb 14)
- Step 5: Brand Guidelines (upload PDF)
- Saves as Draft

**Emotions:** 😊 Productive
**Pain Points:** ⚠️ Lots of fields to fill (30 min)

#### Stage 3: AI Matching (Day 1)
**Touchpoint:** Influencer discovery → AI recommendations
**Actions:**
- Clicks "Find Influencers" button
- AI generates 200 matches (ranked by score)
- Reviews top 50:
  - Match Score: 85/100
  - Audience Match: 90% (female 25-35)
  - Engagement: 6.8%
- Selects 50 influencers
- Clicks "Send Invitations" (bulk)

**Emotions:** 🤩 Impressed (AI works!)
**Pain Points:** None

#### Stage 4: Manage Responses (Day 2-3)
**Touchpoint:** Booking dashboard
**Actions:**
- Receives notifications: "20 influencers accepted"
- Reviews each acceptance
- Negotiates pricing with 5 influencers (chat)
- Confirms final 50 bookings
- Sends contracts (bulk e-signature)

**Emotions:** 😊 Efficient
**Pain Points:** ⚠️ Some influencers decline (backup needed)

#### Stage 5: Monitor Content (Day 4-10)
**Touchpoint:** Content approval workflow
**Actions:**
- Receives notifications: "New content submitted"
- Reviews videos (checks brand guidelines)
- Approves 45 videos
- Requests revisions for 5 videos (too short)
- All content approved by Day 10

**Emotions:** 😊 In control
**Pain Points:** ⚠️ Time-consuming review (2 hours/day)

#### Stage 6: Track Performance (Day 11-14)
**Touchpoint:** Analytics dashboard
**Actions:**
- Checks campaign dashboard daily
- Real-time metrics:
  - Total Reach: 4.2M
  - Total Engagement: 250K (likes + comments)
  - Avg Engagement Rate: 5.9%
  - Top Performer: Minh Anh (8.5%)
- Sees ROI calculator: 12% (spend VND 250M, reach VND 280M value)

**Emotions:** 🤩 Successful
**Pain Points:** None

#### Stage 7: Make Payments (Day 15)
**Touchpoint:** Payment queue
**Actions:**
- Reviews payment queue (50 influencers)
- Batch approves payments
- System processes via MoMo API
- All influencers paid within 5 minutes

**Emotions:** 😊 Satisfied
**Pain Points:** None (automated!)

#### Stage 8: Report to Leadership (Day 16)
**Touchpoint:** Analytics → Export report
**Actions:**
- Clicks "Export Campaign Report"
- Downloads PDF with charts
- Presents to CMO:
  - ROI: 12%
  - Cost per Reach: VND 60
  - Top 10 Influencers
- CMO approves next campaign

**Emotions:** 🤩 Career boost
**Pain Points:** None

**Overall Sentiment:** ⭐⭐⭐⭐⭐ (5/5)

---

### 4.3. Admin Journey: Pool Management & System Health

**Scenario:** Tuấn manages influencer pool, approves submissions, monitors sync

**Stages:**

#### Stage 1: Daily Check (Every Morning)
**Touchpoint:** Admin Dashboard
**Actions:**
- Logs in to Admin Portal
- Reviews dashboard:
  - Total Influencers: 20,500
  - Synced Today: 18,200
  - Failed Syncs: 15 (low!)
  - Pending Approvals: 35
- Sees alert: "3 profiles need manual review"

**Emotions:** 😊 Calm (system healthy)
**Pain Points:** None

#### Stage 2: Approve Submissions (9:00 AM)
**Touchpoint:** Approval Queue
**Actions:**
- Opens "Pending Submissions" (35 profiles)
- Reviews each profile:
  - Check followers (min 10K) ✓
  - Check engagement (min 3%) ✓
  - Check content quality (manual review)
- Approves 30 profiles (bulk action)
- Rejects 5 profiles (fake followers detected)
- Sends rejection emails with reason

**Emotions:** 😊 Productive
**Pain Points:** ⚠️ Manual review takes 30 min

#### Stage 3: Fix Failed Syncs (10:00 AM)
**Touchpoint:** Sync Management
**Actions:**
- Opens "Failed Syncs" (15 profiles)
- Reviews errors:
  - 10 profiles: "VB API timeout" → Retry
  - 5 profiles: "Profile deleted" → Mark as inactive
- Clicks "Retry Failed Syncs" (bulk)
- All 10 synced successfully

**Emotions:** 😊 Resolved
**Pain Points:** ⚠️ VB API sometimes slow

#### Stage 4: Partner Support (11:00 AM)
**Touchpoint:** Messages → Support ticket
**Actions:**
- Receives message from Techcombank admin:
  - "Need to add 100 influencers for Tết campaign"
- Opens "Bulk Import" tool
- Uploads CSV (100 profiles)
- System validates, enriches via VB API
- All profiles added to Techcombank's pool
- Replies to ticket: "Done! ✓"

**Emotions:** 😊 Helpful
**Pain Points:** None

#### Stage 5: Monitor System Health (Throughout Day)
**Touchpoint:** Sync dashboard
**Actions:**
- Checks sync status every 2 hours
- Sees daily sync completed: 98% success rate ✓
- Reviews performance metrics:
  - API Response Time: <200ms ✓
  - Database Query Time: <50ms ✓
- No issues

**Emotions:** 😊 Confident (system stable)
**Pain Points:** None

**Overall Sentiment:** ⭐⭐⭐⭐ (4/5) - Job is manageable with good tools

---

## 5. User Flow Diagrams

### 5.1. Influencer: Accept Campaign Invitation

```
[Start: Email Notification]
   │
   ▼
[1. Open Email]
   │
   ├─→ (Click "View Invitation") ─→ [2. Login to Platform]
   │                                    │
   │                                    ▼
   └──────────────────────────────→ [3. Campaign Invitation Page]
                                       │
                                       ├─→ Campaign Details
                                       ├─→ Budget & Deliverables
                                       ├─→ Timeline
                                       └─→ Brand Guidelines
                                       │
                                       ▼
                                    [Decision: Accept?]
                                       │
                ┌──────────────────────┼──────────────────────┐
                │                      │                      │
                ▼                      ▼                      ▼
          [Accept Button]      [Decline Button]      [Negotiate Button]
                │                      │                      │
                ▼                      ▼                      ▼
          [4a. Contract]        [4b. Decline]         [4c. Counter-Offer]
          [Review & Sign]       [Give Reason]         [Propose Rate]
                │                      │                      │
                ▼                      ▼                      ▼
          [Signature Modal]    [Confirmation]        [Send to Brand]
          [One-Click Sign]           │                      │
                │                    │                      │
                ▼                    │                      ▼
          [5. Success!]              │              [Wait for Response]
          [Campaign Added]           │                      │
                │                    │                      │
                ▼                    ▼                      ▼
          [6. Dashboard]       [6. Dashboard]       [6. Dashboard]
          [Active Campaigns]   [Declined List]      [Pending Negotiations]
                │
                ▼
          [End: Start Creating Content]

Error Cases:
- Contract signing fails → Show error → Retry button
- Network timeout → Show retry → Auto-save progress
```

---

### 5.2. Brand: Create Campaign & Find Influencers

```
[Start: Dashboard]
   │
   ▼
[1. Click "Create New Campaign"]
   │
   ▼
[2. Campaign Creation Wizard]
   │
   ├─→ Step 1: Basic Info
   │     ├─ Campaign Name (input)
   │     ├─ Category (select)
   │     ├─ Budget (input)
   │     └─ Next button
   │
   ├─→ Step 2: Target Audience
   │     ├─ Age Range (slider)
   │     ├─ Gender (checkboxes)
   │     ├─ Location (multi-select)
   │     ├─ Interests (tags)
   │     └─ Next button
   │
   ├─→ Step 3: Deliverables
   │     ├─ Content Type (posts, stories, reels)
   │     ├─ Quantity (50 posts)
   │     ├─ Platform (TikTok, Instagram)
   │     └─ Next button
   │
   ├─→ Step 4: Timeline
   │     ├─ Start Date (date picker)
   │     ├─ End Date (date picker)
   │     ├─ Content Deadline
   │     └─ Next button
   │
   └─→ Step 5: Brand Guidelines
         ├─ Upload PDF/Images
         ├─ Do's and Don'ts (textarea)
         ├─ Hashtags Required
         └─ Save as Draft / Create Campaign
         │
         ▼
[3. Campaign Created]
   │
   ▼
[4. Click "Find Influencers"]
   │
   ▼
[5. AI Matching Results]
   │
   ├─→ 200 Influencers Ranked by Score
   ├─→ Filter by Score, Followers, Engagement
   └─→ Sort by Match Score, Followers
   │
   ▼
[6. Select Influencers]
   │
   ├─→ Review Each Profile
   │     ├─ Match Score: 85/100
   │     ├─ Audience Demographics
   │     ├─ Past Performance
   │     └─ Pricing
   │
   ├─→ Add to Campaign (checkbox)
   └─→ Selected: 50 influencers
   │
   ▼
[7. Click "Send Invitations"]
   │
   ▼
[8. Invitation Confirmation Modal]
   │
   ├─→ Review Selected (50 influencers)
   ├─→ Total Budget Preview
   ├─→ Customize Invite Message (optional)
   └─→ Confirm Send button
   │
   ▼
[9. Invitations Sent]
   │
   ▼
[10. Redirect to Booking Dashboard]
   │
   ├─→ Pending Invitations (50)
   ├─→ Real-time Status Updates
   │     ├─ Accepted: 20
   │     ├─ Pending: 25
   │     ├─ Declined: 5
   │
   ▼
[11. Manage Responses]
   │
   ├─→ Accept Negotiations
   ├─→ Confirm Bookings
   └─→ Send Contracts
   │
   ▼
[End: Campaign In Progress]

Error Cases:
- AI matching timeout → Show retry → Use cached results
- Bulk invite fails → Show partial success → Retry failed
- Contract generation error → Show error → Generate manually
```

---

### 5.3. Admin: Approve Influencer Submission

```
[Start: Dashboard Alert]
   │
   ▼
[1. Click "35 Pending Approvals"]
   │
   ▼
[2. Approval Queue Page]
   │
   ├─→ Table: Pending Submissions
   │     ├─ Avatar, Name, Platform
   │     ├─ Followers, Engagement, Score
   │     ├─ Submitted Date
   │     └─ Actions: View Detail, Approve, Reject
   │
   ▼
[3. Click "View Detail" on Profile]
   │
   ▼
[4. Profile Review Modal]
   │
   ├─→ Left Panel: Enriched Profile Data
   │     ├─ Full Name, Platform URLs
   │     ├─ Followers, Engagement, Score
   │     ├─ Demographics (if available)
   │     ├─ Portfolio (past posts)
   │     └─ Eligibility Check Results
   │           ├─ Min Followers: 10K ✓
   │           ├─ Min Engagement: 3% ✓
   │           ├─ Min Score: 60 ✓
   │
   ├─→ Right Panel: Admin Actions
   │     ├─ Partner Info (who submitted)
   │     ├─ Submission Timestamp
   │     ├─ Notes/Comments (textarea)
   │     └─ Buttons: Approve, Reject
   │
   ▼
[Decision: Approve or Reject?]
   │
   ┌──────────────┼──────────────┐
   │              │              │
   ▼              ▼              ▼
[5a. Approve]  [5b. Reject]  [5c. Request Changes]
   │              │              │
   ▼              ▼              ▼
[Confirm]    [Enter Reason]  [Add Comments]
   │              │              │
   ▼              ▼              ▼
[6a. Success]  [6b. Rejected] [6c. Pending Changes]
   │              │              │
   ├─ Profile → PUBLIC    ├─ Rejection Email   └─ Notify Partner
   ├─ Notify Partner       │
   └─ Update Pool Stats    ▼
                      [Notify Submitter]
                           │
   ┌───────────────────────┴───────────────────────┐
   │                                               │
   ▼                                               ▼
[7. Next Profile]                            [7. Back to Queue]
   │                                               │
   └───────────────────┬───────────────────────────┘
                       │
                       ▼
              [All Profiles Reviewed?]
                       │
           ┌───────────┼───────────┐
           │                       │
           ▼                       ▼
        [Yes]                   [No]
           │                       │
           ▼                       │
    [8. Dashboard]                │
    [Updated Stats]               │
           │                      │
           ▼                      │
       [End]                     │
                                 │
                                 └─→ [Loop: Review Next]

Error Cases:
- VB API timeout during review → Show cached data → Retry sync button
- Approval fails → Show error → Retry button
- Webhook notification fails → Queue for retry → Show warning
```

---

## 6. Wireframes - Influencer Portal

### 6.1. Dashboard (Influencer)

**Purpose:** Central hub cho influencers xem overview của activities, earnings, và pending tasks

**Layout:**

```
Mobile (320-767px):
┌──────────────────────────────────┐
│ ☰  Ambassador    [?]  [👤]       │ ← Header (60px)
├──────────────────────────────────┤
│                                  │
│  👋 Xin chào, Minh Anh!         │ ← Greeting (32px)
│                                  │
│  ┌────────────────────────────┐ │
│  │ 💰 Earnings This Month     │ │ ← Metric Card
│  │ VND 12,500,000             │ │   (full-width)
│  │ +25% vs last month         │ │
│  └────────────────────────────┘ │
│                                  │
│  ┌────────────────────────────┐ │
│  │ 📊 Active Campaigns        │ │
│  │ 3 campaigns                 │ │
│  │ View All →                  │ │
│  └────────────────────────────┘ │
│                                  │
│  ┌────────────────────────────┐ │
│  │ ✉️ Pending Invitations     │ │
│  │ 2 new invitations          │ │
│  │ Review Now →               │ │
│  └────────────────────────────┘ │
│                                  │
│  ┌────────────────────────────┐ │
│  │ 📈 Total Reach             │ │
│  │ 1.2M                       │ │
│  │ Last 30 days               │ │
│  └────────────────────────────┘ │
│                                  │
│  Recent Activity               │ ← Section (24px)
│  ┌────────────────────────────┐ │
│  │ 🎉 Techcombank Tết        │ │ ← Activity Item
│  │ Campaign completed         │ │
│  │ 2 hours ago                │ │
│  └────────────────────────────┘ │
│  ┌────────────────────────────┐ │
│  │ 💸 Payment Received       │ │
│  │ VND 5,000,000             │ │
│  │ 1 day ago                 │ │
│  └────────────────────────────┘ │
│                                  │
│  Quick Actions                  │
│  ┌──────┐ ┌──────┐ ┌──────┐   │
│  │Upload│ │Browse│ │Profile│  │
│  │Post  │ │Camps │ │Edit  │  │
│  └──────┘ └──────┘ └──────┘   │
│                                  │
└──────────────────────────────────┘

Desktop (1024px+):
┌────────────────────────────────────────────────────────────┐
│ 🏠 Ambassador     Campaigns  Performance  Earnings  💬  👤 │ ← Header
├────────────────────────────────────────────────────────────┤
│                                                            │
│  👋 Xin chào, Minh Anh!                   [Upload Content]│
│                                                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│  │💰 Earnings  │ │📊 Campaigns │ │📈 Total Reach│        │ ← 3-col grid
│  │VND 12.5M    │ │3 active     │ │1.2M          │        │
│  │+25% ↑       │ │2 pending    │ │Last 30 days  │        │
│  └─────────────┘ └─────────────┘ └─────────────┘        │
│                                                            │
│  ┌──────────────────────────────┐ ┌──────────────────┐  │
│  │ Pending Invitations          │ │ Recent Activity  │  │
│  │                              │ │                  │  │
│  │ ┌─────────────────────────┐ │ │ Campaign Completed│
│  │ │ Techcombank Tết 2026    │ │ │ 2 hours ago      │  │
│  │ │ Budget: VND 5M          │ │ │                  │  │
│  │ │ Deadline: Feb 14        │ │ │ Payment Received │  │
│  │ │ [Accept] [Decline]      │ │ │ 1 day ago        │  │
│  │ └─────────────────────────┘ │ │                  │  │
│  │                              │ │ Content Approved │  │
│  │ ┌─────────────────────────┐ │ │ 3 days ago       │  │
│  │ │ Vinfast Summer Drive    │ │ │                  │  │
│  │ │ Budget: VND 8M          │ │ │ See All Activity →│
│  │ │ [Accept] [Decline]      │ │ │                  │  │
│  │ └─────────────────────────┘ │ │                  │  │
│  └──────────────────────────────┘ └──────────────────┘  │
│                                                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Performance Chart (Last 30 Days)                   │  │
│  │ [Reach] [Engagement] [Earnings]                    │  │ ← Tabs
│  │                                                     │  │
│  │    ╱╲                                              │  │
│  │   ╱  ╲      ╱╲                                    │  │ ← Line chart
│  │  ╱    ╲    ╱  ╲    ╱╲                            │  │
│  │ ╱      ╲╱╲╱    ╲  ╱  ╲╱                          │  │
│  │                  ╲╱                                │  │
│  │ Jan 1    Jan 10    Jan 20    Jan 30               │  │
│  └────────────────────────────────────────────────────┘  │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Components:**
- Header: Global nav, notifications, user menu
- Greeting: Personalized welcome message
- Metric Cards: Earnings, campaigns, reach (3-column grid desktop, stack mobile)
- Invitation Cards: Campaign invitations với Accept/Decline CTAs
- Activity Feed: Recent events (payment, approval, campaign updates)
- Quick Actions: Upload content, browse campaigns, edit profile
- Performance Chart: Line chart cho reach/engagement/earnings

**Interactions:**
- Metric Cards: Click → Navigate to detailed view
- Invitation Cards: Accept → Contract modal, Decline → Confirmation modal
- Activity Items: Click → Navigate to related page
- Quick Action Buttons: Click → Navigate to respective flow
- Chart: Hover → Show tooltips với exact values

**States:**
- Default: Show all metrics và activities
- Loading: Skeleton placeholders cho cards
- Empty State: "No pending invitations" với CTA "Browse Marketplace"
- Error State: Show error message với retry button

---

### 6.2. Campaign Invitation Detail (Influencer)

**Purpose:** Influencer xem chi tiết campaign invitation và quyết định accept/decline

**Layout:**

```
Desktop Modal (800px width):
┌──────────────────────────────────────────────────────────┐
│ ← Back to Invitations                              ✕    │ ← Header
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Techcombank Tết 2026 Campaign                         │ ← Title (32px)
│  💼 Financial Services • 📅 Jan 20 - Feb 14            │ ← Metadata
│                                                          │
│  ┌────────────────────────────────────────────────────┐│
│  │ 💰 Budget Offer                                    ││ ← Budget Card
│  │ VND 5,000,000 per post                            ││   (glassmorphism)
│  │ 1 TikTok post + 1 Instagram story                 ││
│  └────────────────────────────────────────────────────┘│
│                                                          │
│  Campaign Brief                                         │ ← Section
│  Create engaging content showcasing Techcombank's      │
│  Tết Lucky Draw promotion. Target audience: 25-35      │
│  age group, focus on family values and prosperity.     │
│                                                          │
│  Deliverables                                           │
│  ✓ 1 TikTok video (60-90 seconds)                     │ ← Checklist
│  ✓ 1 Instagram story (15 seconds)                     │
│  ✓ Include hashtags: #TechcombankTet #MayManDauNam    │
│  ✓ Tag @techcombank in posts                          │
│                                                          │
│  Timeline                                               │
│  • Content Submission: Feb 5, 2026                     │ ← Timeline items
│  • Brand Review: Feb 6-7, 2026                         │
│  • Go Live: Feb 8, 2026                                │
│  • Campaign End: Feb 14, 2026                          │
│  • Payment: Feb 15, 2026 (MoMo instant)               │
│                                                          │
│  Brand Guidelines                                       │
│  [📄 Brand Guidelines.pdf] [Download]                  │ ← File download
│  [🎨 Visual Assets.zip] [Download]                     │
│                                                          │
│  Do's and Don'ts                                        │
│  ✅ Do: Focus on family, prosperity, lucky draw        │ ← 2-col layout
│  ✅ Do: Show Techcombank app interface                 │
│  ❌ Don't: Compare with competitors                     │
│  ❌ Don't: Use inappropriate language                   │
│                                                          │
│  ┌────────────────────────────────────────────────────┐│
│  │ ⚠️ Campaign Requirements                          ││ ← Info box
│  │ • Minimum 50K followers (✓ You have 250K)        ││
│  │ • Minimum 3% engagement (✓ Your avg: 4.8%)       ││
│  │ • Must accept terms & conditions                  ││
│  └────────────────────────────────────────────────────┘│
│                                                          │
│  Actions                                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐     │
│  │ 💬 Ask       │ │ ✅ Accept    │ │ ❌ Decline   │     │ ← Action buttons
│  │ Questions    │ │ Invitation   │ │ Invitation   │     │
│  └─────────────┘ └─────────────┘ └─────────────┘     │
│                                                          │
└──────────────────────────────────────────────────────────┘

After clicking "Accept":
┌──────────────────────────────────────────────────────────┐
│ Contract Review & Signature                        ✕    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Please review and sign the contract below:            │
│                                                          │
│  ┌────────────────────────────────────────────────────┐│
│  │ INFLUENCER COLLABORATION AGREEMENT                 ││ ← Contract preview
│  │                                                     ││   (scrollable)
│  │ This agreement is between Techcombank ("Brand")   ││
│  │ and Minh Anh ("Influencer") for the campaign...   ││
│  │                                                     ││
│  │ [Full contract text here...]                       ││
│  │                                                     ││
│  │ Budget: VND 5,000,000                              ││
│  │ Deliverables: 1 TikTok post, 1 IG story          ││
│  │ Timeline: Feb 8-14, 2026                           ││
│  │ Payment Terms: Net 7 days after completion        ││
│  │                                                     ││
│  └────────────────────────────────────────────────────┘│
│                                                          │
│  ┌────────────────────────────────────────────────────┐│
│  │ ☐ I have read and agree to the terms above        ││ ← Checkbox
│  └────────────────────────────────────────────────────┘│
│                                                          │
│  [← Back]                    [Sign & Accept Campaign →]│ ← Actions
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Components:**
- Modal Header: Title, close button
- Campaign Info: Title, category, timeline
- Budget Card: Highlighted offer với deliverables
- Campaign Brief: Text description
- Deliverables: Checklist với checkmark icons
- Timeline: Vertical timeline với dates
- Brand Guidelines: Downloadable files
- Do's and Don'ts: Two-column layout
- Requirements Box: Info box với eligibility check
- Action Buttons: Ask, Accept, Decline
- Contract Modal: Scrollable contract preview với checkbox và sign button

**Interactions:**
- Download Files: Click → Opens file download
- Ask Questions: Click → Opens chat modal với brand
- Accept: Click → Shows contract modal
- Decline: Click → Shows confirmation modal với reason textarea
- Sign Contract: Checkbox required → Enable "Sign & Accept" button

**States:**
- Loading: Show skeleton while fetching campaign data
- Accept Flow: Show contract modal → Checkbox → Success message
- Decline Flow: Show confirmation modal → Reason textarea → Success message
- Error: Show error message nếu action fails

---

### 6.3. Upload Content (Influencer)

**Purpose:** Influencer uploads content cho campaign để brand review và approve

**Layout:**

```
Desktop (1200px):
┌────────────────────────────────────────────────────────────┐
│ 📤 Upload Content                                    ✕    │ ← Page title
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Select Campaign                                          │ ← Dropdown
│  ┌────────────────────────────────────────────────────┐  │
│  │ Techcombank Tết 2026 ▼                            │  │
│  └────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Campaign Requirements:                             │  │ ← Info box
│  │ • 1 TikTok video (60-90 seconds)                  │  │
│  │ • 1 Instagram story (15 seconds)                  │  │
│  │ • Include #TechcombankTet #MayManDauNam           │  │
│  │ • Content deadline: Feb 5, 2026 (3 days left)    │  │
│  └────────────────────────────────────────────────────┘  │
│                                                            │
│  Upload TikTok Video                                      │
│  ┌────────────────────────────────────────────────────┐  │
│  │                                                     │  │
│  │            [📹 Drag & Drop Video]                  │  │ ← Upload area
│  │                                                     │  │   (dashed border)
│  │         or click to browse files                   │  │
│  │                                                     │  │
│  │     Supported: MP4, MOV (max 500MB)               │  │
│  │                                                     │  │
│  └────────────────────────────────────────────────────┘  │
│                                                            │
│  After upload:                                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │ ┌─────────┐                                        │  │
│  │ │ [Video  │  techcombank-tet-2026.mp4              │  │ ← Uploaded file
│  │ │ Thumb]  │  1:23 minutes • 85MB                   │  │
│  │ │         │  [🗑️ Remove]                           │  │
│  │ └─────────┘                                        │  │
│  └────────────────────────────────────────────────────┘  │
│                                                            │
│  Video Details                                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Caption                                            │  │ ← Textarea
│  │ ┌──────────────────────────────────────────────┐  │  │
│  │ │ Chào mừng Tết 2026 cùng Techcombank! 🎉      │  │  │
│  │ │ Tham gia Lucky Draw để nhận quà may mắn...   │  │  │
│  │ │ #TechcombankTet #MayManDauNam                 │  │  │
│  │ └──────────────────────────────────────────────┘  │  │
│  │                                                     │  │
│  │ Hashtags Used                                      │  │ ← Chip list
│  │ [#TechcombankTet] [#MayManDauNam] [#Tet2026]     │  │
│  │                                                     │  │
│  │ Link to TikTok Post (after published)             │  │ ← Input
│  │ ┌──────────────────────────────────────────────┐  │  │
│  │ │ https://tiktok.com/@minh_anh/video/...       │  │  │
│  │ └──────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────┘  │
│                                                            │
│  Upload Instagram Story                                   │
│  [Similar upload area + details...]                      │
│                                                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │ ⚠️ Checklist Before Submitting                    │  │ ← Checklist
│  │ ✓ Video length: 60-90 seconds                     │  │
│  │ ✓ Hashtags included: #TechcombankTet              │  │
│  │ ✓ Brand name mentioned: Techcombank               │  │
│  │ ✗ Visual assets used (missing)                    │  │ ← Warning
│  └────────────────────────────────────────────────────┘  │
│                                                            │
│  [Save as Draft]              [Submit for Review →]      │ ← Actions
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Components:**
- Campaign Selector: Dropdown to choose active campaign
- Requirements Box: Campaign deliverables và deadline
- Upload Area: Drag & drop zone with file browser
- Uploaded File Preview: Thumbnail, filename, size, remove button
- Video Details Form: Caption, hashtags, TikTok link
- Checklist: Auto-check requirements before submit
- Action Buttons: Save draft, Submit for review

**Interactions:**
- Drag & Drop: Drag file → Show upload progress → Display preview
- Remove File: Click 🗑️ → Confirmation modal → Remove file
- Hashtag Detection: Auto-detect hashtags from caption → Show as chips
- Checklist: Auto-validate requirements → Show ✓ or ✗
- Submit: Click → Validation → Success modal → Redirect to content list

**States:**
- Empty: Show upload area với instructions
- Uploading: Show progress bar (0-100%)
- Uploaded: Show preview với details form
- Validation Error: Show error messages (missing hashtags, wrong duration)
- Success: Show success modal "Content submitted for review!"

---

## 7. Wireframes - Brand Portal

### 7.1. Dashboard (Brand)

**Purpose:** Central hub cho brands xem campaign overview, performance metrics, và pending tasks

**Layout:**

```
Desktop (1400px):
┌────────────────────────────────────────────────────────────────┐
│ 🏠 Brand Portal    Campaigns  Discover  Analytics  💬  👤     │ ← Header
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  👋 Welcome back, Hương!              [+ Create New Campaign] │
│                                                                │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐│
│  │📊 Active   │ │💰 Budget   │ │📈 Reach    │ │⭐ Avg ROI  ││ ← 4-col grid
│  │Campaigns   │ │Spent       │ │This Month  │ │This Month  ││
│  │            │ │            │ │            │ │            ││
│  │    12      │ │VND 250M    │ │  4.2M      │ │   12%      ││ ← Large numbers
│  │            │ │            │ │            │ │            ││
│  │+3 vs last  │ │70% of total│ │+15% ↑      │ │+2% ↑       ││
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘│
│                                                                │
│  ┌──────────────────────────────────┐ ┌──────────────────┐  │
│  │ Campaigns Overview               │ │ Pending Tasks    │  │
│  │ [All] [Active] [Draft] [Completed]│ │                  │  │ ← Tabs
│  │                                   │ │ ✉️ 15 Responses  │  │
│  │ ┌───────────────────────────────┐│ │ Review now →     │  │
│  │ │ Techcombank Tết 2026          ││ │                  │  │ ← Campaign card
│  │ │ Active • 50 influencers       ││ │ 📝 8 Content     │  │
│  │ │ Reach: 2.1M • ROI: 14%        ││ │ Needs Approval   │  │
│  │ │ [View Details →]              ││ │ Review now →     │  │
│  │ └───────────────────────────────┘│ │                  │  │
│  │                                   │ │ 💳 10 Payments   │  │
│  │ ┌───────────────────────────────┐│ │ Due This Week    │  │
│  │ │ Vinfast Summer Drive          ││ │ Process now →    │  │
│  │ │ Draft • 0 influencers         ││ │                  │  │
│  │ │ Budget: VND 180M              ││ │ 🎯 3 Campaigns   │  │
│  │ │ [Continue Editing →]          ││ │ Need Influencers │  │
│  │ └───────────────────────────────┘│ │ Find now →       │  │
│  │                                   │ │                  │  │
│  │ ┌───────────────────────────────┐│ └──────────────────┘  │
│  │ │ Brand Awareness Q1            ││                       │
│  │ │ Completed • 30 influencers    ││                       │
│  │ │ Reach: 1.8M • ROI: 9%         ││                       │
│  │ │ [View Report →]               ││                       │
│  │ └───────────────────────────────┘│                       │
│  └──────────────────────────────────┘                       │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ Performance Trends (Last 30 Days)                         ││
│  │ [Reach] [Engagement] [ROI] [Cost per Reach]              ││ ← Tab nav
│  │                                                           ││
│  │     ╱╲              ╱╲                                   ││
│  │    ╱  ╲            ╱  ╲        ╱╲                       ││ ← Multi-line
│  │   ╱    ╲    ╱╲    ╱    ╲      ╱  ╲      ╱╲             ││   chart
│  │  ╱      ╲  ╱  ╲  ╱      ╲    ╱    ╲    ╱  ╲            ││
│  │ ╱        ╲╱    ╲╱        ╲╱╲╱      ╲╱╲╱    ╲           ││
│  │ Jan 1    Jan 10   Jan 20        Jan 30                  ││
│  │                                                           ││
│  │ Legend: ─ Reach  ─ Engagement  ─ ROI                    ││
│  └──────────────────────────────────────────────────────────┘│
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Components:**
- Header: Global nav, notifications, user menu
- Greeting: Personalized welcome với CTA "Create New Campaign"
- Metric Cards: Active campaigns, budget spent, reach, ROI (4-column grid)
- Campaigns Overview: List of campaigns với status, metrics, CTAs
- Pending Tasks: Side widget với actionable items
- Performance Chart: Multi-line chart với tab navigation

**Interactions:**
- Metric Cards: Click → Navigate to filtered view
- Campaign Cards: Click "View Details" → Campaign dashboard
- Pending Tasks: Click arrow → Navigate to specific queue
- Chart: Hover → Show tooltips với exact values, toggle lines

**States:**
- Default: Show all data
- Loading: Skeleton placeholders
- Empty State (No Campaigns): Show "Create your first campaign" CTA
- Error State: Show error message với retry button

---

### 7.2. Create Campaign - Wizard (Brand)

**Purpose:** Multi-step wizard để create new campaign với AI matching setup

**Layout:**

```
Step 1/5: Basic Information

Desktop (1200px):
┌────────────────────────────────────────────────────────────────┐
│ Create New Campaign                                      ✕    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ● ○ ○ ○ ○  Basic Info → Target → Deliverables → Timeline →  │ ← Progress
│                                                        Review  │
│                                                                │
│  Campaign Name *                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Techcombank Tết 2026                                   │  │ ← Text input
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  Category *                                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Financial Services                                ▼    │  │ ← Dropdown
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  Campaign Objective *                                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ ○ Brand Awareness                                      │  │ ← Radio buttons
│  │ ● Conversion (Sales, Sign-ups)                         │  │
│  │ ○ Engagement (Likes, Comments)                         │  │
│  │ ○ Reach (Impressions, Views)                           │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  Total Budget *                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ VND │ 250,000,000                                      │  │ ← Currency input
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  Campaign Description                                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Promote Techcombank Tết Lucky Draw...                  │  │ ← Textarea
│  │                                                         │  │   (10 lines)
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  [Save as Draft]                              [Next: Target →]│
│                                                                │
└────────────────────────────────────────────────────────────────┘


Step 2/5: Target Audience

┌────────────────────────────────────────────────────────────────┐
│ Create New Campaign                                      ✕    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ● ● ○ ○ ○  Basic Info → Target → Deliverables → Timeline →  │
│                                                        Review  │
│                                                                │
│  Define Your Target Audience                                  │
│  This helps AI find the best-matching influencers             │
│                                                                │
│  Age Range *                                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ ├──────────●───────●──────────────────────┤           │  │ ← Range slider
│  │    13      25      35                    65+           │  │
│  │ Selected: 25-35 years old                              │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  Gender *                                                      │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ ☐ Male (30%)    ☑ Female (70%)    ☐ Other (0%)        │  │ ← Checkboxes
│  │ [Total must = 100%]                                    │  │   + validation
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  Location *                                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ [Search cities...]                                  ▼  │  │ ← Multi-select
│  │ ✓ Ho Chi Minh City (85%)                               │  │
│  │ ✓ Hanoi (70%)                                          │  │
│  │ ✓ Da Nang (60%)                                        │  │
│  │ [ ] Can Tho                                            │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  Interests (Optional)                                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ [Type to add interests...]                             │  │ ← Tag input
│  │ [Finance] [Banking] [Lifestyle] [Family] [+]          │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ 💡 AI Tip: Based on your target, we'll recommend      │  │ ← Info box
│  │ influencers whose audience matches 70%+ with your     │  │
│  │ demographics.                                          │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  [← Back]                         [Next: Deliverables →]    │
│                                                                │
└────────────────────────────────────────────────────────────────┘


Step 3/5: Deliverables

┌────────────────────────────────────────────────────────────────┐
│ Create New Campaign                                      ✕    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ● ● ● ○ ○  Basic Info → Target → Deliverables → Timeline →  │
│                                                        Review  │
│                                                                │
│  What content do you want influencers to create?              │
│                                                                │
│  Platforms *                                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ ☑ TikTok    ☑ Instagram    ☐ YouTube    ☐ Facebook    │  │ ← Checkboxes
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  Content Types & Quantity                                     │
│                                                                │
│  TikTok                                                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Content Type       Quantity    Budget per Post         │  │
│  │ ─────────────      ────────    ─────────────────       │  │
│  │ [Video Post ▼]     [50    ]    VND [5,000,000  ]      │  │ ← Inline form
│  │ [Story      ▼]     [0     ]    VND [2,000,000  ]      │  │
│  │ [+ Add Type]                                           │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  Instagram                                                     │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ [Story      ▼]     [50    ]    VND [2,000,000  ]      │  │
│  │ [+ Add Type]                                           │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  Total Influencers Needed: 50                                 │
│  Total Estimated Cost: VND 250,000,000                        │
│                                                                │
│  Content Requirements                                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Do's:                                                   │  │ ← Textarea
│  │ • Focus on family, prosperity, lucky draw               │  │
│  │ • Show Techcombank app interface                        │  │
│  │                                                         │  │
│  │ Don'ts:                                                 │  │
│  │ • No comparison with competitors                        │  │
│  │ • No inappropriate language                             │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  Required Hashtags                                            │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ [#TechcombankTet] [#MayManDauNam] [+]                 │  │ ← Tag input
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  [← Back]                           [Next: Timeline →]       │
│                                                                │
└────────────────────────────────────────────────────────────────┘


Step 4/5: Timeline

┌────────────────────────────────────────────────────────────────┐
│ Create New Campaign                                      ✕    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ● ● ● ● ○  Basic Info → Target → Deliverables → Timeline →  │
│                                                        Review  │
│                                                                │
│  Set Campaign Timeline                                        │
│                                                                │
│  Campaign Period *                                            │
│  ┌──────────────────────┐    ┌──────────────────────┐        │
│  │ Start Date           │    │ End Date             │        │
│  │ Feb 1, 2026     📅  │    │ Feb 14, 2026     📅  │        │ ← Date pickers
│  └──────────────────────┘    └──────────────────────┘        │
│  Campaign Duration: 14 days                                   │
│                                                                │
│  Key Milestones                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Booking Deadline        Feb 1, 2026   📅              │  │ ← Date inputs
│  │ Content Submission      Feb 5, 2026   📅              │  │
│  │ Content Approval        Feb 7, 2026   📅              │  │
│  │ Go Live Date            Feb 8, 2026   📅              │  │
│  │ Payment Release         Feb 15, 2026  📅              │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  Timeline Visualization                                       │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Jan 31    Feb 1     Feb 5    Feb 8     Feb 14  Feb 15 │  │
│  │    │        │         │        │          │       │    │  │
│  │    └───┬────┴────┬────┴───┬────┴────┬─────┴───┬───┘    │  │ ← Horizontal
│  │        │         │        │         │         │        │  │   timeline
│  │     Booking  Content  Go Live  Campaign  Payment       │  │
│  │     Opens   Deadline           Ends                     │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  [← Back]                           [Next: Review →]         │
│                                                                │
└────────────────────────────────────────────────────────────────┘


Step 5/5: Review & Create

┌────────────────────────────────────────────────────────────────┐
│ Create New Campaign                                      ✕    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ● ● ● ● ●  Basic Info → Target → Deliverables → Timeline →  │
│                                                        Review  │
│                                                                │
│  Review Your Campaign                                         │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Techcombank Tết 2026                         [Edit ✏️]│  │ ← Summary card
│  │ Financial Services • Conversion                        │  │
│  │ Budget: VND 250,000,000 • 50 influencers              │  │
│  │                                                         │  │
│  │ Target Audience                                [Edit ✏️]│  │
│  │ • Age: 25-35 years old                                 │  │
│  │ • Gender: 70% Female, 30% Male                         │  │
│  │ • Location: HCM (85%), Hanoi (70%), Da Nang (60%)     │  │
│  │                                                         │  │
│  │ Deliverables                                   [Edit ✏️]│  │
│  │ • 50 TikTok posts (VND 5M each)                        │  │
│  │ • 50 Instagram stories (VND 2M each)                   │  │
│  │ • Hashtags: #TechcombankTet #MayManDauNam              │  │
│  │                                                         │  │
│  │ Timeline                                       [Edit ✏️]│  │
│  │ • Campaign: Feb 1-14, 2026 (14 days)                  │  │
│  │ • Content Deadline: Feb 5                              │  │
│  │ • Go Live: Feb 8                                       │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  Next Steps                                                   │
│  After creating, you can:                                     │
│  1. Find influencers using AI matching                        │
│  2. Send bulk invitations                                     │
│  3. Track responses and manage bookings                       │
│                                                                │
│  [← Back]  [Save as Draft]     [Create Campaign & Find →]    │
│                                            Influencers        │
└────────────────────────────────────────────────────────────────┘
```

**Components:**
- Progress Indicator: Step 1/5 dots với labels
- Form Sections: Grouped inputs per step
- Input Types: Text, dropdown, radio, checkbox, range slider, date picker, textarea, tag input
- Validation: Real-time validation với error messages
- Info Boxes: Tips và guidance từ AI
- Timeline Visualization: Horizontal timeline với milestones
- Summary Cards: Editable review cards
- Action Buttons: Back, Save Draft, Next, Create Campaign

**Interactions:**
- Progress Dots: Click → Jump to step (if visited)
- Form Inputs: Type → Auto-save to draft → Show save indicator
- Range Slider: Drag → Update label với selected range
- Multi-select: Click checkbox → Update percentage (for gender)
- Tag Input: Type → Autocomplete suggestions → Add tag
- Date Pickers: Click → Calendar modal → Select date
- Edit Buttons: Click → Go back to specific step
- Create Campaign: Click → Validate all steps → Success → Redirect to AI matching

**States:**
- Step Navigation: Highlight current step, disable future steps
- Form Validation: Show errors inline (red border + message)
- Auto-save: Show "Saving..." indicator → "Saved" checkmark
- Loading: Show spinner khi processing
- Success: Show success modal → Redirect to influencer discovery

**Responsive:**
- Mobile: Stack form fields vertically, full-width inputs
- Tablet: 2-column layout cho checkboxes/radios
- Desktop: Maintain wizard width 1200px, centered

---

### 7.3. AI Influencer Matching (Brand)

**Purpose:** AI-powered influencer discovery với ranking scores, audience match, và bulk selection

**Layout:**

```
Desktop (1400px):
┌────────────────────────────────────────────────────────────────┐
│ ← Back to Campaign       Techcombank Tết 2026           ✕    │ ← Header
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  🤖 AI Matching Results for "Techcombank Tết 2026"           │ ← Title
│  Found 200 influencers • Showing top 50                       │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ 🎯 Matching Criteria                                    │  │ ← Info box
│  │ Target: Female 70%, Age 25-35, Location HCM/Hanoi      │  │   (collapsed)
│  │ Budget: VND 5M/post • Platform: TikTok                 │  │
│  │ [Show Full Criteria ▼]                                 │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌───────────────────┐  ┌─────────────────────────────────┐ │
│  │ Filters           │  │ Sort by: [Match Score ▼]        │ │
│  │                   │  │ Selected: 0 / 50 needed          │ │
│  │ Min Score         │  │                                  │ │
│  │ ├─●──────┤ 70+   │  │ ┌──────────────────────────────┐│ │
│  │                   │  │ │ #1 Match Score: 92/100       ││ │ ← Influencer
│  │ Followers Range   │  │ │ ┌──────┐                     ││ │   card
│  │ ├──●────●──┤      │  │ │ │[Img] │ Minh Anh           ││ │
│  │ 100K-500K         │  │ │ │      │ @beauty_creator    ││ │
│  │                   │  │ │ └──────┘ TikTok • Beauty     ││ │
│  │ Platform          │  │ │                               ││ │
│  │ ☑ TikTok          │  │ │ Followers: 250K              ││ │
│  │ ☐ Instagram       │  │ │ Engagement: 4.8%  ⭐⭐⭐⭐⭐ ││ │
│  │ ☐ YouTube         │  │ │                               ││ │
│  │ ☐ Facebook        │  │ │ Audience Match: 90%          ││ │
│  │                   │  │ │ ┌──────────────────────┐    ││ │
│  │ Category          │  │ │ │ Female: 82% (Target: 70%)││ │ ← Demographics
│  │ ☑ Beauty          │  │ │ │ Age 25-34: 75% ✓      ││ │   match
│  │ ☑ Lifestyle       │  │ │ │ HCM: 85% ✓            ││ │
│  │ ☐ Tech            │  │ │ └──────────────────────┘    ││ │
│  │                   │  │ │                               ││ │
│  │ Price Range       │  │ │ Pricing: VND 5M/post         ││ │
│  │ VND [2M - 8M]     │  │ │                               ││ │
│  │                   │  │ │ ☑ [Select] [View Profile]    ││ │ ← Actions
│  │ [Reset Filters]   │  │ └──────────────────────────────┘│ │
│  └───────────────────┘  │                                  │ │
│                         │ ┌──────────────────────────────┐│ │
│                         │ │ #2 Match Score: 88/100       ││ │
│                         │ │ [Similar card structure...]  ││ │
│                         │ └──────────────────────────────┘│ │
│                         │                                  │ │
│                         │ ┌──────────────────────────────┐│ │
│                         │ │ #3 Match Score: 85/100       ││ │
│                         │ │ [Similar card structure...]  ││ │
│                         │ └──────────────────────────────┘│ │
│                         │                                  │ │
│                         │ [Load More (showing 3 of 50)]   │ │
│                         └─────────────────────────────────┘ │
│                                                                │
│  [Select All Top 50]    [Review Selected (0) →]              │ ← Bulk actions
│                                                                │
└────────────────────────────────────────────────────────────────┘

After selecting influencers:

┌────────────────────────────────────────────────────────────────┐
│ Review Selected Influencers (50)                         ✕    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  You've selected 50 influencers for Techcombank Tết 2026     │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Budget Summary                                          │  │ ← Summary box
│  │ • Total Budget: VND 250,000,000                        │  │
│  │ • Per Influencer: VND 5,000,000 (50 posts)            │  │
│  │ • Est. Total Reach: 12.5M followers                   │  │
│  │ • Avg Match Score: 85/100                             │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  Selected Influencers (scrollable list)                       │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Minh Anh • @beauty_creator • TikTok • 250K   [Remove] │  │ ← List item
│  │ Match: 92/100 • Price: VND 5M                         │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ Hoa Nguyen • @lifestyle_daily • TikTok • 180K [Remove]│  │
│  │ Match: 88/100 • Price: VND 5M                         │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ [48 more influencers...]                               │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  Invitation Message (Optional)                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Hello! We'd love to collaborate with you for our       │  │ ← Textarea
│  │ Techcombank Tết 2026 campaign...                       │  │   (editable)
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  [← Back to Matching]            [Send Invitations (50) →]   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Components:**
- Matching Info Box: Target criteria summary (collapsible)
- Filter Sidebar: Range sliders, checkboxes, price range
- Sort Dropdown: Match score, followers, engagement, price
- Selection Counter: Shows X/50 selected
- Influencer Cards: Avatar, name, platform, metrics, demographics match, actions
- Match Score Badge: 0-100 với color coding (green 80+, yellow 60-79, red <60)
- Audience Match Bar: Horizontal bar chart showing demographics alignment
- Bulk Actions: Select all, review selected
- Review Modal: Selected list, budget summary, invitation message

**Interactions:**
- Filter Changes: Auto-refresh results (debounced)
- Sort Dropdown: Change order → Re-render list
- Select Checkbox: Add to selected → Update counter
- View Profile: Click → Open influencer detail modal
- Select All: Click → Add all visible to selected
- Review Selected: Click → Open review modal
- Send Invitations: Click → Validate → Bulk send → Success message

**States:**
- Loading: Show skeleton cards while AI processing
- Empty Results: Show "No matches found" với suggestions to adjust filters
- Partial Selection: Show counter "15/50 selected"
- Full Selection: Show "50/50 selected ✓" với green checkmark
- Sending: Show progress "Sending invitations... 25/50"
- Success: Show success modal "50 invitations sent!"

---

### 7.4. Campaign Dashboard (Brand)

**Purpose:** Monitor active campaign với real-time metrics, influencer status, content approval, và performance analytics

**Layout:**

```
Desktop (1400px):
┌────────────────────────────────────────────────────────────────┐
│ ← Back to Campaigns      Techcombank Tết 2026           ✕    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Techcombank Tết 2026                            [⚙️ Edit]    │ ← Title
│  Active • Feb 1-14, 2026 • 5 days remaining                   │
│                                                                │
│  [Overview] [Influencers] [Content] [Analytics] [Payments]   │ ← Tabs
│  ───────────                                                   │
│                                                                │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐│
│  │📊 Total    │ │✅ Confirmed│ │📈 Total    │ │⭐ Avg      ││ ← 4-col grid
│  │Influencers │ │Bookings    │ │Reach       │ │Engagement  ││
│  │            │ │            │ │            │ │            ││
│  │    50      │ │    45      │ │  2.1M      │ │   5.9%     ││
│  │            │ │            │ │            │ │            ││
│  │Target: 50  │ │90% accept  │ │Target: 2.5M│ │+0.5% ↑     ││
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘│
│                                                                │
│  Campaign Progress                                            │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ ────●─────────●──────────○──────────○──────────○       │  │ ← Progress bar
│  │     │         │          │          │          │       │  │   với stages
│  │   Setup   Booking    Content    Go Live     Completed  │  │
│  │   Feb 1    Feb 3     Feb 5-7    Feb 8       Feb 14     │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────┐ ┌──────────────────┐  │
│  │ Booking Status                   │ │ Action Items     │  │
│  │                                   │ │                  │  │
│  │ ┌─────────────────────────────┐ │ │ ⚠️ 5 Influencers │  │ ← Alerts
│  │ │ ● Confirmed: 45 (90%)       │ │ │ Need Response    │  │
│  │ │ ○ Pending: 3 (6%)           │ │ │ [Review →]       │  │
│  │ │ ✗ Declined: 2 (4%)          │ │ │                  │  │
│  │ └─────────────────────────────┘ │ │ 📝 15 Content    │  │
│  │                                   │ │ Pending Approval │  │
│  │ Top Performers (by match score) │ │ [Review →]       │  │
│  │ ┌───────────────────────────────┐│ │                  │  │
│  │ │ 1. Minh Anh (@beauty_creator) ││ │ 💳 10 Payments   │  │
│  │ │    TikTok • 250K • Match: 92% ││ │ Due This Week    │  │
│  │ │    Status: ✅ Confirmed       ││ │ [Process →]      │  │
│  │ ├───────────────────────────────┤│ │                  │  │
│  │ │ 2. Hoa Nguyen (@lifestyle)    ││ └──────────────────┘  │
│  │ │    TikTok • 180K • Match: 88% ││                       │
│  │ │    Status: ✅ Confirmed       ││                       │
│  │ ├───────────────────────────────┤│                       │
│  │ │ 3. [More influencers...]      ││                       │
│  │ └───────────────────────────────┘│                       │
│  │ [View All Influencers →]         │                       │
│  └──────────────────────────────────┘                       │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ Performance Trends (Real-time)                            ││
│  │ [Reach] [Engagement] [Content Posts] [Conversions]       ││ ← Tab nav
│  │                                                           ││
│  │     ╱╲                                                   ││
│  │    ╱  ╲          ╱╲                                     ││ ← Line chart
│  │   ╱    ╲   ╱╲   ╱  ╲      ╱╲                           ││   (animated)
│  │  ╱      ╲ ╱  ╲ ╱    ╲    ╱  ╲                          ││
│  │ ╱        ╲╱    ╲╱      ╲╱╲╱    ╲                        ││
│  │ Feb 8  Feb 9  Feb 10  Feb 11  Feb 12  Today (Feb 13)   ││
│  │                                                           ││
│  │ Total Reach: 2.1M views • Engagement: 125K interactions ││
│  └──────────────────────────────────────────────────────────┘│
│                                                                │
└────────────────────────────────────────────────────────────────┘


Tab: Content (Content Approval Queue)

┌────────────────────────────────────────────────────────────────┐
│ ← Back      Techcombank Tết 2026 • Content                    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  [Overview] [Influencers] [Content] [Analytics] [Payments]   │
│                            ────────                            │
│                                                                │
│  Content Approval Queue                                       │
│  Pending: 15 • Approved: 30 • Rejected: 5                     │
│                                                                │
│  Filter: [All] [Pending] [Approved] [Rejected] [Revisions]   │
│          ────────                                              │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ ┌──────┐                                               │  │ ← Content card
│  │ │[Video│  Minh Anh • @beauty_creator                   │  │
│  │ │Thumb]│  TikTok • Submitted: Feb 5, 2026 (2 days ago) │  │
│  │ │ ▶    │                                               │  │
│  │ └──────┘  Duration: 1:23 • 85MB                        │  │
│  │                                                         │  │
│  │ Caption:                                                │  │
│  │ "Chào mừng Tết 2026 cùng Techcombank! 🎉..."           │  │
│  │ #TechcombankTet #MayManDauNam ✓                        │  │
│  │                                                         │  │
│  │ Checklist:                                              │  │
│  │ ✓ Hashtags included                                    │  │
│  │ ✓ Brand mention: Techcombank                           │  │
│  │ ✓ Duration: 60-90 seconds                              │  │
│  │ ✗ Visual assets used (missing logo)                    │  │
│  │                                                         │  │
│  │ [▶ Play Video]  [✅ Approve]  [❌ Reject]  [📝 Request │  │ ← Actions
│  │                                            Revision]   │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ [Similar content cards for other submissions...]       │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  [Bulk Actions]  [Select All Pending] [Approve Selected (0)] │
│                                                                │
└────────────────────────────────────────────────────────────────┘


Tab: Analytics (Performance Deep Dive)

┌────────────────────────────────────────────────────────────────┐
│ ← Back      Techcombank Tết 2026 • Analytics                  │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  [Overview] [Influencers] [Content] [Analytics] [Payments]   │
│                                     ─────────                  │
│                                                                │
│  Campaign Performance Report                                  │
│  Feb 8-13, 2026 (5 days of data)                             │
│  [Export PDF] [Export CSV] [Share Report]                    │
│                                                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐│
│  │📈 Total     │ │👍 Total     │ │💬 Total     │ │🔄 Shares ││
│  │Reach        │ │Likes        │ │Comments     │ │          ││
│  │2.1M         │ │85K          │ │12K          │ │3.5K      ││
│  │+15% vs est. │ │4% eng rate  │ │0.6% rate    │ │0.2% rate ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘│
│                                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ ROI Analysis                                            │  │
│  │                                                         │  │
│  │ Budget Spent: VND 225,000,000 (45 influencers paid)   │  │
│  │ Total Reach Value: VND 280,000,000 (est.)             │  │
│  │ ROI: 24% profit                                        │  │
│  │ Cost per Reach: VND 107                                │  │
│  │ Cost per Engagement: VND 1,800                         │  │
│  │                                                         │  │
│  │ ┌────────────────────────────────────────────────┐    │  │
│  │ │ Budget: ████████████████░░░░░░░░  90% spent    │    │  │ ← Progress bar
│  │ │ Reach:  █████████████████████░░░  84% of target│    │  │
│  │ └────────────────────────────────────────────────┘    │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ Top Performing Content                                    ││
│  │                                                           ││
│  │ #1 Minh Anh • @beauty_creator • TikTok                   ││ ← Leaderboard
│  │    Reach: 480K • Engagement: 8.5% • Likes: 40K          ││
│  │    [View Content]                                        ││
│  │                                                           ││
│  │ #2 Hoa Nguyen • @lifestyle_daily • TikTok                ││
│  │    Reach: 350K • Engagement: 6.2% • Likes: 22K          ││
│  │    [View Content]                                        ││
│  │                                                           ││
│  │ #3 [More influencers...]                                 ││
│  └──────────────────────────────────────────────────────────┘│
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ Demographics Breakdown                                    ││
│  │                                                           ││
│  │ Age Distribution:                                         ││
│  │ 13-17: █░░░░░░░░░ 8%                                     ││ ← Horizontal
│  │ 18-24: ████░░░░░░ 22%                                    ││   bar chart
│  │ 25-34: ██████████ 45%  ← Target ✓                       ││
│  │ 35-44: ███░░░░░░░ 18%                                    ││
│  │ 45+:   █░░░░░░░░░ 7%                                     ││
│  │                                                           ││
│  │ Gender:                                                   ││
│  │ Female: ███████░░░ 68%  ← Target: 70% (close!)          ││
│  │ Male:   ███░░░░░░░ 30%                                   ││
│  │ Other:  ░░░░░░░░░░ 2%                                    ││
│  │                                                           ││
│  │ Location:                                                 ││
│  │ HCM:    ████████░░ 78%                                   ││
│  │ Hanoi:  ████░░░░░░ 15%                                   ││
│  │ Other:  █░░░░░░░░░ 7%                                    ││
│  └──────────────────────────────────────────────────────────┘│
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Components:**
- Tab Navigation: Overview, Influencers, Content, Analytics, Payments
- Metric Cards: Total influencers, bookings, reach, engagement (4-column grid)
- Campaign Progress: Visual timeline với completed/current/upcoming stages
- Booking Status: Pie chart hoặc progress bars với counts
- Top Performers: List of influencers ranked by match score
- Action Items: Alert widget với pending tasks
- Performance Chart: Line chart cho real-time metrics
- Content Cards: Video thumbnail, caption, checklist, approval actions
- Analytics Report: ROI calculator, top content leaderboard, demographics breakdown

**Interactions:**
- Tab Click: Switch view → Load tab content
- Metric Cards: Click → Filter view by metric
- Influencer Name: Click → Open influencer detail modal
- Action Items: Click arrow → Navigate to specific queue
- Content Video: Click ▶ Play → Play video in modal hoặc inline
- Approval Actions: Click Approve/Reject → Confirmation → Update status
- Export Report: Click → Generate PDF/CSV → Download
- Chart: Hover → Show tooltips với exact values

**States:**
- Tab Loading: Show skeleton for tab content
- Real-time Updates: WebSocket updates cho metrics (animated counters)
- Approval Success: Show toast "Content approved!" → Update queue
- Error State: Show error message nếu action fails (retry button)

---

## 8. Wireframes - Admin Portal

### 8.1. Admin Dashboard

**Purpose:** System overview cho AT Admin monitor pool health, approvals, partner activity

**Layout:**

```
Desktop (1400px):
┌────────────────────────────────────────────────────────────────┐
│ 🏠 Admin Portal    Pool  Approvals  Partners  Sync  ⚙️  👤   │ ← Header
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Admin Dashboard                           [Last updated: 9:00]│
│                                                                │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐│
│  │👥 Total    │ │✅ Synced   │ │⚠️ Pending  │ │🏢 Active   ││ ← 4-col grid
│  │Pool        │ │Today       │ │Approvals   │ │Partners    ││
│  │            │ │            │ │            │ │            ││
│  │  20,500    │ │  18,200    │ │     35     │ │     8      ││
│  │            │ │            │ │            │ │            ││
│  │+50 today   │ │89% success │ │Review →    │ │View →      ││
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘│
│                                                                │
│  System Health                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ API Response Time:     <200ms  ✓                       │  │ ← Status table
│  │ Database Query Time:   <50ms   ✓                       │  │
│  │ VB API Uptime:         99.2%   ✓                       │  │
│  │ Failed Syncs:          15      ⚠️ [View →]            │  │
│  │ Error Rate:            0.8%    ✓                       │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────┐ ┌──────────────────┐  │
│  │ Recent Activity                   │ │ Alerts           │  │
│  │                                   │ │                  │  │
│  │ ⏰ 9:05 AM                        │ │ ⚠️ 3 profiles    │  │
│  │ 15 profiles synced successfully  │ │ need manual      │  │
│  │                                   │ │ review (high     │  │
│  │ ⏰ 9:00 AM                        │ │ fraud risk)      │  │
│  │ Techcombank added 10 profiles    │ │ [Review →]       │  │
│  │                                   │ │                  │  │
│  │ ⏰ 8:45 AM                        │ │ 🔄 Daily sync    │  │
│  │ 5 submissions rejected (fake)    │ │ starting in      │  │
│  │                                   │ │ 3 hours          │  │
│  │ ⏰ 8:30 AM                        │ │                  │  │
│  │ Daily sync completed (98%)       │ │ ℹ️ VB API slow   │  │
│  │                                   │ │ response times   │  │
│  │ [View All Activity →]            │ │ detected         │  │
│  └──────────────────────────────────┘ └──────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ Pool Growth (Last 30 Days)                                ││
│  │                                                           ││
│  │     ╱                                                    ││
│  │    ╱                                                     ││ ← Area chart
│  │   ╱                              ╱                       ││
│  │  ╱    ╱╲      ╱╲    ╱╲         ╱                        ││
│  │ ╱    ╱  ╲    ╱  ╲  ╱  ╲  ╱╲   ╱                         ││
│  │╱────╱────╲╱╲╱────╲╱────╲╱──╲─╱──────────────────────────││
│  │ Jan 1    Jan 10   Jan 20         Jan 30                  ││
│  │                                                           ││
│  │ Total: 20,500 profiles • Added: 1,200 (6.2% growth)     ││
│  └──────────────────────────────────────────────────────────┘│
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Components:**
- Metric Cards: Total pool, synced today, pending approvals, active partners
- System Health Table: API performance, sync status, error rates
- Recent Activity Feed: Timestamped events
- Alerts Widget: Important notifications với CTAs
- Pool Growth Chart: Area chart showing growth trend

---

## 9. Interaction Patterns

### 9.1. Modal Patterns

**Usage:** For focused tasks, confirmations, details views

**Types:**

1. **Small Modal** (400px width)
   - Confirmations ("Are you sure?")
   - Simple forms (1-3 fields)
   - Alerts, success messages

2. **Medium Modal** (600px width)
   - Forms (5-10 fields)
   - Profile previews
   - Content details

3. **Large Modal** (800-1000px width)
   - Complex workflows (contract signing)
   - Rich content (video player + details)
   - Multi-step forms

**Interaction:**
- Open: Fade in + scale up (200ms)
- Close: Click ✕, click overlay, press Escape
- Scroll: Modal body scrollable, header/footer fixed
- Focus Trap: Tab cycles within modal

---

### 9.2. Toast Notifications

**Usage:** For feedback on actions (success, error, info)

**Position:** Top-right corner
**Duration:** 3-5 seconds (auto-dismiss)
**Types:**
- Success: Green background, checkmark icon
- Error: Red background, X icon
- Warning: Orange background, ! icon
- Info: Blue background, i icon

**Interactions:**
- Slide in from right (150ms)
- Hover → Pause auto-dismiss
- Click → Dismiss immediately

---

### 9.3. Loading States

**Skeleton Loading:**
- Use for initial page load
- Mimic actual content layout
- Animated shimmer effect
- Replace with real content (no flash)

**Spinner:**
- Use for in-progress actions (saving, submitting)
- Center of screen (fullscreen overlay) or inline (button)

**Progress Bar:**
- Use for file uploads, bulk operations
- Show percentage + estimated time

---

## 10. Component Specifications

[Continue with detailed component specs...]

**Due to length constraints, I'll create this as a separate file and save it.**

