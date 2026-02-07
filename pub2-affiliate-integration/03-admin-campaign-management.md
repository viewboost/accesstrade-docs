# Admin Campaign Management - Pub2 Integration

**Date:** 2026-02-07
**Status:** Architecture Design
**Related Documents:**
- [01-brainstorming-session.md](./01-brainstorming-session.md)
- [02-architecture-decisions.md](./02-architecture-decisions.md)

---

## Executive Summary

Tài liệu này mô tả **Campaign Management System** cho TCB Admin, giải quyết vấn đề:

**Problem:**
- Pub2 có hàng nghìn campaigns
- Không thể auto-sync tất cả vì risk show competitor campaigns
- TCB cần full control over campaigns hiển thị cho influencers

**Solution:**
- **Manual Curation Model:** TCB admin tự tạo campaigns trong hệ thống
- **Pub2 Linking:** Chỉ lưu `pub2_campaign_id` để link tới Pub2
- **Full Customization:** TCB control title, description, images, visibility
- **Brand Safety:** Zero risk hiển thị competitor campaigns

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Data Model](#data-model)
3. [Admin Workflows](#admin-workflows)
4. [UI/UX Design](#uiux-design)
5. [Implementation Code](#implementation-code)
6. [Background Jobs](#background-jobs)
7. [Security & Permissions](#security--permissions)
8. [Analytics & Reporting](#analytics--reporting)

---

## Architecture Overview

### Manual Curation Model

```
┌─────────────────────────────────────────────────────────┐
│              Pub2 System (1000+ campaigns)              │
│  • Banking campaigns: 200+                              │
│  • Finance campaigns: 300+                              │
│  • Insurance: 150+                                      │
│  • Competitor campaigns: 100+ (Vietcombank, BIDV, etc) │
│  • Irrelevant campaigns: 250+                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ TCB Admin BROWSES (not auto-sync)
                     │ Manual selection only
                     ▼
┌─────────────────────────────────────────────────────────┐
│           TCB Admin Panel - Campaign Management         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  STEP 1: Browse Pub2                                    │
│  ┌───────────────────────────────────────────────┐     │
│  │ Search: [credit card] 🔍                      │     │
│  │                                               │     │
│  │ Results:                                      │     │
│  │ ✓ Platinum Card (TCB) - camp_123            │     │
│  │ ✓ Travel Insurance - camp_456               │     │
│  │ ⚠️ Vietcombank Card (COMPETITOR) - camp_999 │     │
│  │                                               │     │
│  │ [Add Selected to TCB]                         │     │
│  └───────────────────────────────────────────────┘     │
│                                                         │
│  STEP 2: Customize Campaign                             │
│  ┌───────────────────────────────────────────────┐     │
│  │ Pub2 ID: camp_123 (locked)                    │     │
│  │ Title: [Thẻ Platinum TCB_______________]     │     │
│  │ Description: [Lãi suất 0%...____________]    │     │
│  │ Image: [Upload TCB branded image]            │     │
│  │ Category: [Credit Card ▼]                    │     │
│  │ Status: [Draft ▼] → Active after approval    │     │
│  │                                               │     │
│  │ [Save] [Submit for Approval]                  │     │
│  └───────────────────────────────────────────────┘     │
│                                                         │
│  STEP 3: Approval (Optional)                            │
│  Manager approves → Campaign goes live                  │
│                                                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Only approved campaigns visible
                     ▼
┌─────────────────────────────────────────────────────────┐
│         TCB Influencer Portal - Campaign Browser        │
├─────────────────────────────────────────────────────────┤
│  ✅ Campaigns (15 active, curated by admin):           │
│  • Platinum Credit Card (TCB)                           │
│  • Travel Insurance                                     │
│  • Savings Account                                      │
│  • Personal Loan                                        │
│  • ...                                                  │
│                                                         │
│  ❌ NOT VISIBLE:                                        │
│  • Vietcombank campaigns (competitor)                   │
│  • BIDV campaigns (competitor)                          │
│  • Random campaigns from Pub2                           │
│  • Unapproved campaigns                                 │
└─────────────────────────────────────────────────────────┘
```

---

### Key Principles

1. **TCB Owns Campaign Data**
   - Title, description, images stored in TCB database
   - Not dependent on Pub2's data structure
   - Can customize for Vietnamese audience

2. **Pub2 as Commission Engine**
   - Link via `pub2_campaign_id`
   - Pub2 handles click tracking, conversions, payouts
   - TCB doesn't need to replicate Pub2's affiliate logic

3. **Manual Curation = Brand Safety**
   - Admin explicitly approves each campaign
   - Zero risk of competitor campaigns leaking through
   - Legal/compliance review before publish

4. **Sync Only Status**
   - Background job checks if Pub2 campaign still active
   - Auto-update `pub2_campaign_status` field
   - Notify admin if campaign ends on Pub2

---

## Data Model

### Database Schema

```sql
-- TCB's curated campaigns
CREATE TABLE campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id VARCHAR(50) NOT NULL,  -- 'tcb', 'ambassador', 'vinfast'

  -- Campaign metadata (TCB controls)
  title VARCHAR(255) NOT NULL,
  short_description VARCHAR(500),
  full_description TEXT,

  -- Media assets
  banner_image_url TEXT,
  thumbnail_url TEXT,
  gallery_images JSONB DEFAULT '[]',  -- Array of image URLs

  -- Categorization
  category VARCHAR(100) NOT NULL,  -- 'credit-card', 'insurance', 'loan', etc.
  tags JSONB DEFAULT '[]',  -- ['platinum', 'cashback', 'travel']

  -- Commission info
  commission_rate DECIMAL(5,2),
  commission_type VARCHAR(20) CHECK (commission_type IN ('percentage', 'fixed')),
  commission_amount DECIMAL(10,2),  -- For fixed type
  commission_note TEXT,  -- Internal notes

  -- Pub2 linking (CRITICAL FIELD)
  pub2_campaign_id VARCHAR(100) UNIQUE NOT NULL,  -- Link to Pub2
  pub2_merchant_name VARCHAR(255),  -- Cached from Pub2
  pub2_campaign_status VARCHAR(20),  -- 'active' | 'paused' | 'ended' (synced)
  pub2_last_synced TIMESTAMP,  -- Last sync time

  -- Visibility & lifecycle
  status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'inactive', 'archived')),
  featured BOOLEAN DEFAULT false,  -- Show on homepage
  display_order INT DEFAULT 0,  -- Sort order (lower = higher priority)

  -- Date range
  start_date DATE,
  end_date DATE,

  -- Audit trail
  created_by UUID NOT NULL,  -- Admin user who created
  approved_by UUID,  -- Manager who approved
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  published_at TIMESTAMP,  -- When status → active

  -- Constraints
  FOREIGN KEY (tenant_id) REFERENCES tenants(id),
  FOREIGN KEY (created_by) REFERENCES users(id),
  FOREIGN KEY (approved_by) REFERENCES users(id)
);

-- Campaign approval workflow
CREATE TABLE campaign_approvals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,

  -- Workflow
  requester_id UUID NOT NULL REFERENCES users(id),  -- Who created/edited
  approver_id UUID REFERENCES users(id),  -- Who approved/rejected
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'changes_requested')),

  -- Feedback
  notes TEXT,  -- Approval notes from manager
  changes_requested TEXT,  -- What needs to change

  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  reviewed_at TIMESTAMP,

  FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
);

-- Sync logs (track Pub2 status changes)
CREATE TABLE campaign_sync_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  pub2_campaign_id VARCHAR(100) NOT NULL,

  -- Sync details
  sync_type VARCHAR(50) NOT NULL,  -- 'status_check' | 'commission_update' | 'merchant_update'
  old_value JSONB,  -- Previous state
  new_value JSONB,  -- New state

  -- Result
  sync_status VARCHAR(20),  -- 'success' | 'failed' | 'no_change'
  error_message TEXT,

  synced_at TIMESTAMP DEFAULT NOW()
);

-- Campaign performance metrics (aggregated)
CREATE TABLE campaign_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,

  -- Date range
  date DATE NOT NULL,  -- Metrics for this date

  -- Engagement metrics
  views INT DEFAULT 0,  -- How many influencers viewed
  link_generations INT DEFAULT 0,  -- How many links created

  -- Affiliate metrics (synced from pub2_conversions)
  total_clicks INT DEFAULT 0,
  total_conversions INT DEFAULT 0,
  total_commission DECIMAL(10,2) DEFAULT 0,

  -- Calculated metrics
  ctr DECIMAL(5,2),  -- Click-through rate
  cvr DECIMAL(5,2),  -- Conversion rate

  created_at TIMESTAMP DEFAULT NOW(),

  UNIQUE(campaign_id, date)
);

-- Indexes for performance
CREATE INDEX idx_campaigns_tenant ON campaigns(tenant_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_pub2_id ON campaigns(pub2_campaign_id);
CREATE INDEX idx_campaigns_category ON campaigns(category);
CREATE INDEX idx_campaigns_featured ON campaigns(featured) WHERE featured = true;
CREATE INDEX idx_campaign_approvals_status ON campaign_approvals(status) WHERE status = 'pending';
CREATE INDEX idx_campaign_sync_logs_date ON campaign_sync_logs(synced_at);
CREATE INDEX idx_campaign_metrics_date ON campaign_metrics(date);

-- Full-text search on campaigns
CREATE INDEX idx_campaigns_title_search ON campaigns USING GIN (to_tsvector('english', title));
CREATE INDEX idx_campaigns_desc_search ON campaigns USING GIN (to_tsvector('english', full_description));
```

---

### Entity Relationships

```
┌─────────────┐       ┌──────────────────┐       ┌─────────────┐
│   Tenants   │──────<│    Campaigns     │>──────│    Users    │
│             │       │                  │       │  (created)  │
└─────────────┘       │  - title         │       └─────────────┘
                      │  - description   │
                      │  - pub2_id ◄─────┼──► Pub2 System
                      │  - status        │
                      └────────┬─────────┘
                               │
                 ┌─────────────┼──────────────┐
                 │             │              │
                 ▼             ▼              ▼
       ┌─────────────────┐ ┌──────────┐ ┌─────────────┐
       │ Campaign        │ │ Sync     │ │ Campaign    │
       │ Approvals       │ │ Logs     │ │ Metrics     │
       │                 │ │          │ │             │
       │ - requester     │ │ - old    │ │ - clicks    │
       │ - approver      │ │ - new    │ │ - convs     │
       │ - status        │ │ - type   │ │ - commission│
       └─────────────────┘ └──────────┘ └─────────────┘
```

---

## Admin Workflows

### Workflow 1: Add New Campaign

```
┌──────────────────────────────────────────────────────────┐
│  PHASE 1: Discover Campaign on Pub2                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Admin navigates to: "Campaign Management" → "+ Add"    │
│                                                          │
│  UI displays "Browse Pub2 Campaigns" page                │
│  ┌────────────────────────────────────────────────┐     │
│  │ Search Pub2: [credit card____________] 🔍     │     │
│  │ Category Filter: [Banking ▼] [Finance] [All]  │     │
│  │                                                │     │
│  │ Sorting: [Newest ▼] [Highest Commission]      │     │
│  │                                                │     │
│  │ Results (fetched from Pub2 API):               │     │
│  │ ┌──────────────────────────────────────────┐  │     │
│  │ │ 🏦 Platinum Credit Card                  │  │     │
│  │ │                                          │  │     │
│  │ │ Pub2 ID: camp_12345                      │  │     │
│  │ │ Merchant: Techcombank                    │  │     │
│  │ │ Commission: 8.5% per approved app        │  │     │
│  │ │ Status: Active until Dec 31, 2026        │  │     │
│  │ │                                          │  │     │
│  │ │ ✅ Matches tenant: Techcombank           │  │     │
│  │ │ ✅ Not yet added to TCB                  │  │     │
│  │ │                                          │  │     │
│  │ │ [Add to TCB] [View on Pub2]              │  │     │
│  │ └──────────────────────────────────────────┘  │     │
│  │                                                │     │
│  │ ┌──────────────────────────────────────────┐  │     │
│  │ │ 💳 Vietcombank Platinum Card             │  │     │
│  │ │                                          │  │     │
│  │ │ Pub2 ID: camp_99999                      │  │     │
│  │ │ Merchant: Vietcombank                    │  │     │
│  │ │ Commission: 10%                          │  │     │
│  │ │                                          │  │     │
│  │ │ ⚠️ WARNING: Competitor Campaign          │  │     │
│  │ │ This merchant competes with Techcombank  │  │     │
│  │ │                                          │  │     │
│  │ │ [Add Anyway] (requires approval)         │  │     │
│  │ └──────────────────────────────────────────┘  │     │
│  │                                                │     │
│  │ ┌──────────────────────────────────────────┐  │     │
│  │ │ 🍕 Pizza Delivery Service                │  │     │
│  │ │                                          │  │     │
│  │ │ Pub2 ID: camp_88888                      │  │     │
│  │ │ Category: Food & Beverage                │  │     │
│  │ │                                          │  │     │
│  │ │ ⓘ Irrelevant category for TCB            │  │     │
│  │ │ Not recommended                          │  │     │
│  │ └──────────────────────────────────────────┘  │     │
│  └────────────────────────────────────────────────┘     │
│                                                          │
│  Backend Logic:                                          │
│  1. Call Pub2 API with search query                     │
│  2. Fetch existing TCB campaigns (pub2_campaign_id)     │
│  3. Filter out already-added campaigns                  │
│  4. Flag competitors (keyword matching)                 │
│  5. Sort by relevance                                   │
│                                                          │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  PHASE 2: Customize Campaign Details                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Admin clicks "Add to TCB" → Form opens                 │
│                                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │ Add Campaign: Platinum Credit Card             │     │
│  ├────────────────────────────────────────────────┤     │
│  │                                                │     │
│  │ PUB2 CAMPAIGN INFO (read-only)                 │     │
│  │ ────────────────────────────────               │     │
│  │ Pub2 Campaign ID: camp_12345                   │     │
│  │ Merchant: Techcombank                          │     │
│  │ Original Commission: 8.5%                      │     │
│  │ Pub2 Status: Active                            │     │
│  │                                                │     │
│  │ ─────────────────────────────────              │     │
│  │                                                │     │
│  │ CAMPAIGN DETAILS (customizable)                │     │
│  │ ────────────────────────────────               │     │
│  │                                                │     │
│  │ Title (Vietnamese): *                          │     │
│  │ [Thẻ Tín Dụng Techcombank Platinum________]   │     │
│  │                                                │     │
│  │ Short Description (max 500 chars):             │     │
│  │ [Lãi suất 0% trong 12 tháng đầu tiên_____]   │     │
│  │                                                │     │
│  │ Full Description (rich text editor):           │     │
│  │ ┌────────────────────────────────────────┐    │     │
│  │ │ [B] [I] [U] [Link] [Image]             │    │     │
│  │ │                                        │    │     │
│  │ │ ✨ Ưu đãi đặc biệt:                    │    │     │
│  │ │ • Lãi suất 0% trong 12 tháng đầu       │    │     │
│  │ │ • Hoàn tiền 8% cho chi tiêu nước ngoài │    │     │
│  │ │ • Miễn phí thường niên năm đầu         │    │     │
│  │ │ • Tích điểm đổi quà hấp dẫn            │    │     │
│  │ │                                        │    │     │
│  │ │ 📋 Điều kiện:                          │    │     │
│  │ │ • Thu nhập tối thiểu 10 triệu/tháng   │    │     │
│  │ │ • Độ tuổi từ 22-65                     │    │     │
│  │ └────────────────────────────────────────┘    │     │
│  │                                                │     │
│  │ Category: *                                    │     │
│  │ [Credit Card ▼]                                │     │
│  │ Options: Credit Card, Loan, Insurance, etc.    │     │
│  │                                                │     │
│  │ Tags (optional):                               │     │
│  │ [platinum] [cashback] [travel] [+Add Tag]      │     │
│  │                                                │     │
│  │ ─────────────────────────────────              │     │
│  │                                                │     │
│  │ COMMISSION SETTINGS                            │     │
│  │ ────────────────────────────────               │     │
│  │                                                │     │
│  │ Commission Type: [Percentage ▼]                │     │
│  │ Commission Rate: [8.5]%                        │     │
│  │                                                │     │
│  │ [ ] Override Pub2 commission                   │     │
│  │     (Check if TCB wants to offer different)    │     │
│  │                                                │     │
│  │ Internal Notes (not visible to influencers):   │     │
│  │ [High priority campaign, promote heavily___]   │     │
│  │                                                │     │
│  │ ─────────────────────────────────              │     │
│  │                                                │     │
│  │ MEDIA ASSETS                                   │     │
│  │ ────────────────────────────────               │     │
│  │                                                │     │
│  │ Banner Image (1200x400px): *                   │     │
│  │ [Upload File] or [Enter URL]                   │     │
│  │ [████████████████] platinum-banner.jpg         │     │
│  │                                                │     │
│  │ Thumbnail (400x300px):                         │     │
│  │ [Upload File]                                  │     │
│  │ [████████] platinum-thumb.jpg                  │     │
│  │                                                │     │
│  │ Gallery Images (optional):                     │     │
│  │ [img1.jpg] [img2.jpg] [+ Add Image]            │     │
│  │                                                │     │
│  │ ─────────────────────────────────              │     │
│  │                                                │     │
│  │ VISIBILITY & SCHEDULING                        │     │
│  │ ────────────────────────────────               │     │
│  │                                                │     │
│  │ Status: [Draft ▼]                              │     │
│  │ Options:                                       │     │
│  │ • Draft (not visible to influencers)           │     │
│  │ • Active (visible, requires approval)          │     │
│  │ • Inactive (hidden)                            │     │
│  │                                                │     │
│  │ [ ] Featured Campaign                          │     │
│  │     (Show on homepage & top of campaign list)  │     │
│  │                                                │     │
│  │ Display Order: [10]                            │     │
│  │ (Lower numbers appear first)                   │     │
│  │                                                │     │
│  │ Start Date: [2026-02-08] (optional)            │     │
│  │ End Date: [2026-12-31] (optional)              │     │
│  │                                                │     │
│  │ ─────────────────────────────────              │     │
│  │                                                │     │
│  │ [Save as Draft] [Submit for Approval]          │     │
│  │                                                │     │
│  └────────────────────────────────────────────────┘     │
│                                                          │
│  * = Required fields                                     │
│                                                          │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  PHASE 3: Approval Workflow (if Submit for Approval)    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  System creates campaign_approvals record:               │
│  - campaign_id: [new campaign ID]                        │
│  - requester_id: [current admin user]                    │
│  - status: 'pending'                                     │
│                                                          │
│  Notification sent to managers:                          │
│  ┌────────────────────────────────────────────────┐     │
│  │ 🔔 New Campaign Pending Approval               │     │
│  │                                                │     │
│  │ Campaign: Platinum Credit Card                 │     │
│  │ Created by: admin@techcombank.com              │     │
│  │ Date: 2026-02-07 14:30                         │     │
│  │                                                │     │
│  │ [Review Now]                                   │     │
│  └────────────────────────────────────────────────┘     │
│                                                          │
│  Manager navigates to "Pending Approvals" page           │
│  ┌────────────────────────────────────────────────┐     │
│  │ Review Campaign: Platinum Credit Card          │     │
│  ├────────────────────────────────────────────────┤     │
│  │                                                │     │
│  │ [Preview as Influencer would see]              │     │
│  │ ┌──────────────────────────────────────────┐  │     │
│  │ │ 🏦 Thẻ Tín Dụng Techcombank Platinum    │  │     │
│  │ │                                          │  │     │
│  │ │ [Banner Image]                           │  │     │
│  │ │                                          │  │     │
│  │ │ Lãi suất 0% trong 12 tháng đầu tiên     │  │     │
│  │ │                                          │  │     │
│  │ │ Commission: 8.5%                         │  │     │
│  │ │ [Generate Affiliate Link]               │  │     │
│  │ └──────────────────────────────────────────┘  │     │
│  │                                                │     │
│  │ Campaign Details:                              │     │
│  │ • Pub2 ID: camp_12345                          │     │
│  │ • Category: Credit Card                        │     │
│  │ • Status will be: Active                       │     │
│  │ • Featured: No                                 │     │
│  │                                                │     │
│  │ Approval Decision:                             │     │
│  │ ○ Approve                                      │     │
│  │ ○ Request Changes                              │     │
│  │ ○ Reject                                       │     │
│  │                                                │     │
│  │ Notes (required if rejecting):                 │     │
│  │ [_________________________________________]    │     │
│  │                                                │     │
│  │ [Submit Decision]                              │     │
│  └────────────────────────────────────────────────┘     │
│                                                          │
│  If APPROVED:                                            │
│  - campaign.status → 'active'                            │
│  - campaign.approved_by → [manager user ID]             │
│  - campaign.published_at → NOW()                        │
│  - Notify creator: "Campaign approved!"                 │
│  - Campaign now visible to influencers                  │
│                                                          │
│  If REQUEST CHANGES:                                     │
│  - campaign.status remains 'draft'                       │
│  - approval.status → 'changes_requested'                │
│  - Notify creator with manager's notes                  │
│  - Creator can edit & re-submit                         │
│                                                          │
│  If REJECTED:                                            │
│  - campaign.status → 'inactive'                          │
│  - approval.status → 'rejected'                         │
│  - Notify creator with reason                           │
│                                                          │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  PHASE 4: Campaign Goes Live                            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  After approval, campaign appears in:                    │
│                                                          │
│  1. Admin Panel → Campaign List (status: Active)         │
│  2. Influencer Portal → Campaign Browser                 │
│                                                          │
│  Influencers can now:                                    │
│  - Browse campaign                                       │
│  - Generate affiliate links                              │
│  - Track performance                                     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

### Workflow 2: Edit Existing Campaign

```
┌──────────────────────────────────────────────────────────┐
│  Edit Campaign Workflow                                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Admin navigates to: Campaign List → [Edit]             │
│                                                          │
│  Form pre-filled with existing data                      │
│  ┌────────────────────────────────────────────────┐     │
│  │ Edit Campaign: Platinum Credit Card            │     │
│  ├────────────────────────────────────────────────┤     │
│  │                                                │     │
│  │ [All fields from Add form, pre-filled]         │     │
│  │                                                │     │
│  │ Changes:                                       │     │
│  │ • Can edit all fields EXCEPT pub2_campaign_id  │     │
│  │ • If campaign is 'active', changes may require │     │
│  │   re-approval (configurable)                   │     │
│  │                                                │     │
│  │ [Save Changes] [Preview] [Cancel]              │     │
│  └────────────────────────────────────────────────┘     │
│                                                          │
│  Business Rules:                                         │
│  • Draft campaigns: Edit freely, no approval needed      │
│  • Active campaigns:                                     │
│    - Minor edits (typos, images): Auto-save             │
│    - Major edits (commission, description): Re-approve  │
│  • Inactive/Archived: Cannot edit (must duplicate)      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

### Workflow 3: Bulk Operations

```
┌──────────────────────────────────────────────────────────┐
│  Bulk Campaign Operations                                │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Campaign List page with checkboxes:                     │
│  ┌────────────────────────────────────────────────┐     │
│  │ ☑ Select All (15 campaigns)                    │     │
│  │                                                │     │
│  │ [☑] Platinum Credit Card (Active)              │     │
│  │ [☑] Travel Insurance (Active)                  │     │
│  │ [☑] Personal Loan (Active)                     │     │
│  │ [ ] Old Campaign (Ended)                       │     │
│  │ ...                                            │     │
│  │                                                │     │
│  │ Bulk Actions: [Choose Action ▼] [Apply]        │     │
│  │ Options:                                       │     │
│  │ • Activate Selected                            │     │
│  │ • Deactivate Selected                          │     │
│  │ • Mark as Featured                             │     │
│  │ • Unmark Featured                              │     │
│  │ • Archive Selected                             │     │
│  │ • Export to CSV                                │     │
│  │ • Delete (requires confirmation)               │     │
│  └────────────────────────────────────────────────┘     │
│                                                          │
│  Use Cases:                                              │
│  • End of year: Deactivate all expired campaigns        │
│  • Promotion: Mark top 5 campaigns as featured          │
│  • Cleanup: Archive campaigns from Pub2 that ended      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

### Workflow 4: Campaign Performance Review

```
┌──────────────────────────────────────────────────────────┐
│  View Campaign Performance                               │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Admin clicks [Stats] on campaign list                   │
│                                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │ Campaign Performance: Platinum Credit Card     │     │
│  ├────────────────────────────────────────────────┤     │
│  │                                                │     │
│  │ Date Range: [Last 30 Days ▼]                   │     │
│  │                                                │     │
│  │ KEY METRICS                                    │     │
│  │ ┌──────────┐ ┌──────────┐ ┌──────────┐       │     │
│  │ │ Views    │ │ Links    │ │ Clicks   │       │     │
│  │ │  1,234   │ │   234    │ │  5,678   │       │     │
│  │ └──────────┘ └──────────┘ └──────────┘       │     │
│  │                                                │     │
│  │ ┌──────────┐ ┌──────────┐ ┌──────────┐       │     │
│  │ │ Convs    │ │ Revenue  │ │   CVR    │       │     │
│  │ │    89    │ │ $3,765   │ │  1.57%   │       │     │
│  │ └──────────┘ └──────────┘ └──────────┘       │     │
│  │                                                │     │
│  │ 📊 CONVERSION TREND                           │     │
│  │ [Line chart showing daily conversions]         │     │
│  │                                                │     │
│  │ TOP PERFORMING INFLUENCERS                     │     │
│  │ 1. Alice Nguyen - 23 conversions - $966       │     │
│  │ 2. Bob Tran - 18 conversions - $756           │     │
│  │ 3. Carol Le - 14 conversions - $588           │     │
│  │                                                │     │
│  │ RECOMMENDATIONS                                │     │
│  │ ✓ High CTR (4.6%) - Campaign is attractive    │     │
│  │ ✓ CVR above average - Good landing page       │     │
│  │ ⚠️ Consider increasing display_order to top 3  │     │
│  │                                                │     │
│  │ [Export Report] [Share with Team]              │     │
│  └────────────────────────────────────────────────┘     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## UI/UX Design

### Page 1: Campaign List (Main Dashboard)

```
┌───────────────────────────────────────────────────────────┐
│  CAMPAIGNS                      [+ Add Campaign] [Import] │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Filter:  [All (45)] [Active (15)] [Draft (8)]           │
│          [Inactive (12)] [Archived (10)]                 │
│                                                           │
│  Search: [_________________________] 🔍                   │
│  Category: [All ▼]  Sort: [Display Order ▼]              │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ [ ] Status   Campaign Info           Pub2   Actions │ │
│  ├─────────────────────────────────────────────────────┤ │
│  │ [☑] 🟢 Active                                       │ │
│  │     ┌─────┐  Thẻ Tín Dụng Platinum                 │ │
│  │     │ IMG │  Commission: 8.5%                       │ │
│  │     └─────┘  camp_123                               │ │
│  │     Featured • Credit Card                          │ │
│  │     234 links • 89 conversions                      │ │
│  │     Created: Feb 1 by admin@tcb.com                 │ │
│  │                                                     │ │
│  │     [Edit] [Stats] [Duplicate] [Deactivate]        │ │
│  │                                                     │ │
│  ├─────────────────────────────────────────────────────┤ │
│  │ [ ] 🟢 Active                                       │ │
│  │     ┌─────┐  Travel Insurance                       │ │
│  │     │ IMG │  Commission: $15 fixed                  │ │
│  │     └─────┘  camp_456                               │ │
│  │     Insurance                                       │ │
│  │     89 links • 34 conversions                       │ │
│  │                                                     │ │
│  │     [Edit] [Stats] [Deactivate]                     │ │
│  │                                                     │ │
│  ├─────────────────────────────────────────────────────┤ │
│  │ [ ] 🟡 Draft (Pending Approval)                     │ │
│  │     ┌─────┐  Savings Account Premium                │ │
│  │     │ IMG │  Commission: 5%                         │ │
│  │     └─────┘  camp_789                               │ │
│  │     Banking                                         │ │
│  │     Submitted by: editor@tcb.com                    │ │
│  │     Waiting for: manager@tcb.com                    │ │
│  │                                                     │ │
│  │     [Review] [Edit] [Withdraw]                      │ │
│  │                                                     │ │
│  ├─────────────────────────────────────────────────────┤ │
│  │ [ ] 🔴 Ended (Pub2 campaign ended)                  │ │
│  │     ┌─────┐  Old Promotion                          │ │
│  │     │ IMG │  Ended on Pub2: Jan 31, 2026            │ │
│  │     └─────┘  camp_111                               │ │
│  │     Had 45 links, 12 conversions                    │ │
│  │                                                     │ │
│  │     [Archive] [View Report]                         │ │
│  │                                                     │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  Bulk Actions:                                            │
│  2 selected  [Activate] [Deactivate] [Delete] [Export]   │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ SUMMARY                                             │ │
│  │ • Total Campaigns: 45                               │ │
│  │ • Active & Visible: 15                              │ │
│  │ • Total Affiliate Links: 1,234                      │ │
│  │ • This Month Revenue: $12,340                       │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  Pagination: [< Prev] Page 1 of 3 [Next >]               │
└───────────────────────────────────────────────────────────┘
```

---

### Page 2: Browse Pub2 Campaigns

```
┌───────────────────────────────────────────────────────────┐
│  BROWSE PUB2 CAMPAIGNS                     [Back to List] │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Search Pub2: [credit card_______________] 🔍            │
│  Category: [Banking ▼] [Finance] [Insurance] [All]       │
│  Sort by: [Newest ▼] [Highest Commission] [Trending]     │
│                                                           │
│  ℹ️ Showing campaigns from Pub2 not yet added to TCB     │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ 🏦 Platinum Credit Card                             │ │
│  │                                                     │ │
│  │ Pub2 ID: camp_12345                                 │ │
│  │ Merchant: Techcombank                               │ │
│  │ Commission: 8.5% per approved application           │ │
│  │ Status: Active until Dec 31, 2026                   │ │
│  │ Description: Premium credit card with 0% intro...   │ │
│  │                                                     │ │
│  │ ✅ Matches your tenant (Techcombank)                │ │
│  │ ✅ Not yet added to TCB                             │ │
│  │ ✅ High conversion rate (12.3% average)             │ │
│  │                                                     │ │
│  │ [Add to TCB] [Preview on Pub2 →]                    │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ 💳 Vietcombank Premier Credit Card                  │ │
│  │                                                     │ │
│  │ Pub2 ID: camp_99999                                 │ │
│  │ Merchant: Vietcombank                               │ │
│  │ Commission: 10% per approval                        │ │
│  │ Status: Active                                      │ │
│  │                                                     │ │
│  │ ⚠️ WARNING: COMPETITOR CAMPAIGN                     │ │
│  │ Vietcombank competes with Techcombank               │ │
│  │ Adding this may confuse influencers or violate      │ │
│  │ brand guidelines.                                   │ │
│  │                                                     │ │
│  │ [Add Anyway] (Requires manager approval)            │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ 🍕 Pizza Hut Delivery - 20% Off                     │ │
│  │                                                     │ │
│  │ Pub2 ID: camp_88888                                 │ │
│  │ Category: Food & Beverage                           │ │
│  │ Commission: $5 per order                            │ │
│  │                                                     │ │
│  │ ⓘ IRRELEVANT CATEGORY                               │ │
│  │ This campaign doesn't match Techcombank's focus     │ │
│  │ (Banking/Finance/Insurance).                        │ │
│  │                                                     │ │
│  │ [Add Anyway]                                        │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ 📱 Samsung Galaxy S26 Pre-Order                     │ │
│  │                                                     │ │
│  │ Pub2 ID: camp_77777                                 │ │
│  │ Commission: 3%                                      │ │
│  │                                                     │ │
│  │ ✅ Already added to TCB                             │ │
│  │ Added on: Feb 5, 2026                               │ │
│  │                                                     │ │
│  │ [View in TCB] [Edit]                                │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  Pagination: [< Prev] Page 1 of 24 [Next >]              │
│                                                           │
│  💡 TIP: Use category filters to find relevant campaigns │
│  quickly. Banking/Finance/Insurance match TCB best.      │
└───────────────────────────────────────────────────────────┘
```

---

### Page 3: Campaign Form (Add/Edit)

(Already detailed in Workflow 1 above - see PHASE 2)

---

### Page 4: Approval Dashboard

```
┌───────────────────────────────────────────────────────────┐
│  PENDING APPROVALS                                        │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Filter: [All (12)] [My Requests (3)] [Awaiting Me (5)]  │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ 🟡 Pending Approval                                  │ │
│  │                                                     │ │
│  │ Campaign: Savings Account Premium                   │ │
│  │ Pub2 ID: camp_789                                   │ │
│  │                                                     │ │
│  │ Requested by: editor@tcb.com                        │ │
│  │ Date: Feb 7, 2026 10:30 AM (2 hours ago)            │ │
│  │                                                     │ │
│  │ Changes:                                            │ │
│  │ • New campaign (not edit)                           │ │
│  │ • Commission: 5% percentage                         │ │
│  │ • Category: Banking                                 │ │
│  │ • Will be: Active, Featured                         │ │
│  │                                                     │ │
│  │ [Review Now] [Preview]                              │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ 🟠 Changes Requested                                │ │
│  │                                                     │ │
│  │ Campaign: Personal Loan                             │ │
│  │ Pub2 ID: camp_555                                   │ │
│  │                                                     │ │
│  │ Requested by: editor@tcb.com                        │ │
│  │ Manager notes: "Please update description to        │ │
│  │ include eligibility criteria clearly."             │ │
│  │                                                     │ │
│  │ Status: Awaiting editor to re-submit               │ │
│  │                                                     │ │
│  │ [View Campaign]                                     │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ ✅ Recently Approved                                │ │
│  │                                                     │ │
│  │ Campaign: Travel Insurance                          │ │
│  │ Approved by: manager@tcb.com                        │ │
│  │ Date: Feb 6, 2026 3:45 PM                           │ │
│  │                                                     │ │
│  │ Now live and visible to influencers                 │ │
│  │                                                     │ │
│  │ [View Live Campaign]                                │ │
│  └─────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

---

## Implementation Code

### Service Layer

```typescript
// services/CampaignManagement.service.ts

import { Pub2ApiClient } from './Pub2ApiClient';
import db from '../db';
import { notificationService } from './Notification.service';

interface CampaignCreateData {
  tenantId: string;
  title: string;
  shortDescription?: string;
  fullDescription?: string;
  category: string;
  tags?: string[];
  commissionRate: number;
  commissionType: 'percentage' | 'fixed';
  commissionAmount?: number;
  pub2CampaignId: string;
  bannerImageUrl?: string;
  thumbnailUrl?: string;
  galleryImages?: string[];
  status: 'draft' | 'active' | 'inactive';
  featured?: boolean;
  displayOrder?: number;
  startDate?: string;
  endDate?: string;
  createdBy: string;
}

interface Pub2Campaign {
  id: string;
  title: string;
  merchant: string;
  category: string;
  commissionRate: number;
  commissionType: string;
  status: 'active' | 'paused' | 'ended';
  description?: string;
}

class CampaignManagementService {
  private pub2Client: Pub2ApiClient;

  constructor() {
    this.pub2Client = new Pub2ApiClient();
  }

  /**
   * Browse available Pub2 campaigns (not yet added to TCB)
   */
  async browsePub2Campaigns(
    tenantId: string,
    options: {
      search?: string;
      category?: string;
      sortBy?: 'newest' | 'commission' | 'trending';
      page?: number;
      limit?: number;
    } = {}
  ) {
    const { search, category, sortBy = 'newest', page = 1, limit = 20 } = options;

    // Get tenant Pub2 config
    const tenantConfig = await this.getTenantPub2Config(tenantId);

    // Fetch campaigns from Pub2
    const pub2Campaigns = await this.pub2Client.getCampaigns(
      tenantConfig.pub2ApiKey,
      {
        search,
        category,
        status: 'active',
        page,
        limit: limit * 2  // Fetch more to filter
      }
    );

    // Get already-added campaign IDs
    const existingPub2Ids = await db.campaigns
      .where('tenant_id', tenantId)
      .pluck('pub2_campaign_id');

    // Filter out already-added
    let availableCampaigns = pub2Campaigns.filter(
      c => !existingPub2Ids.includes(c.id)
    );

    // Enrich with warnings
    availableCampaigns = availableCampaigns.map(campaign => {
      const isCompetitor = this.isCompetitorCampaign(
        campaign.merchant,
        tenantId
      );
      const isRelevant = this.isCategoryRelevant(
        campaign.category,
        tenantId
      );

      return {
        ...campaign,
        warnings: {
          isCompetitor,
          isIrrelevant: !isRelevant
        },
        recommended: !isCompetitor && isRelevant,
        alreadyAdded: false
      };
    });

    // Sort
    if (sortBy === 'commission') {
      availableCampaigns.sort((a, b) => b.commissionRate - a.commissionRate);
    } else if (sortBy === 'trending') {
      // Would need trending data from Pub2 or own analytics
      // Placeholder: sort by commission for now
      availableCampaigns.sort((a, b) => b.commissionRate - a.commissionRate);
    }

    // Paginate
    const startIdx = (page - 1) * limit;
    const endIdx = startIdx + limit;
    const paginatedCampaigns = availableCampaigns.slice(startIdx, endIdx);

    return {
      campaigns: paginatedCampaigns,
      pagination: {
        page,
        limit,
        total: availableCampaigns.length,
        hasMore: endIdx < availableCampaigns.length
      }
    };
  }

  /**
   * Add campaign to TCB
   */
  async createCampaign(data: CampaignCreateData) {
    const { tenantId, pub2CampaignId, createdBy, status } = data;

    // Verify Pub2 campaign exists
    const tenantConfig = await this.getTenantPub2Config(tenantId);
    const pub2Campaign = await this.pub2Client.getCampaignById(
      pub2CampaignId,
      tenantConfig.pub2ApiKey
    );

    if (!pub2Campaign) {
      throw new Error(`Pub2 campaign not found: ${pub2CampaignId}`);
    }

    if (pub2Campaign.status !== 'active') {
      throw new Error(`Pub2 campaign is not active: ${pub2Campaign.status}`);
    }

    // Check if already added
    const existing = await db.campaigns.findOne({
      tenant_id: tenantId,
      pub2_campaign_id: pub2CampaignId
    });

    if (existing) {
      throw new Error('Campaign already added to this tenant');
    }

    // Create campaign
    const campaign = await db.campaigns.create({
      tenant_id: tenantId,
      title: data.title,
      short_description: data.shortDescription,
      full_description: data.fullDescription,
      category: data.category,
      tags: data.tags || [],
      commission_rate: data.commissionRate,
      commission_type: data.commissionType,
      commission_amount: data.commissionAmount,
      pub2_campaign_id: pub2CampaignId,
      pub2_merchant_name: pub2Campaign.merchant,
      pub2_campaign_status: pub2Campaign.status,
      pub2_last_synced: new Date(),
      banner_image_url: data.bannerImageUrl,
      thumbnail_url: data.thumbnailUrl,
      gallery_images: data.galleryImages || [],
      status: data.status || 'draft',
      featured: data.featured || false,
      display_order: data.displayOrder || 0,
      start_date: data.startDate,
      end_date: data.endDate,
      created_by: createdBy
    });

    // If submitting for approval
    if (status === 'active') {
      await this.createApprovalRequest(campaign.id, createdBy);
    }

    return campaign;
  }

  /**
   * Update existing campaign
   */
  async updateCampaign(
    campaignId: string,
    updates: Partial<CampaignCreateData>,
    userId: string
  ) {
    const campaign = await db.campaigns.findOne({ id: campaignId });

    if (!campaign) {
      throw new Error('Campaign not found');
    }

    // Check if major changes require re-approval
    const majorChanges = this.hasMajorChanges(campaign, updates);

    // Update campaign
    const updated = await db.campaigns.update(
      { id: campaignId },
      {
        ...updates,
        updated_at: new Date()
      }
    );

    // If active campaign has major changes, request re-approval
    if (campaign.status === 'active' && majorChanges) {
      await db.campaigns.update(
        { id: campaignId },
        { status: 'draft' }
      );
      await this.createApprovalRequest(campaignId, userId);
    }

    return updated;
  }

  /**
   * Create approval request
   */
  private async createApprovalRequest(campaignId: string, requesterId: string) {
    const approval = await db.campaign_approvals.create({
      campaign_id: campaignId,
      requester_id: requesterId,
      status: 'pending'
    });

    // Notify managers
    await this.notifyManagers(campaignId, requesterId);

    return approval;
  }

  /**
   * Approve campaign
   */
  async approveCampaign(
    approvalId: string,
    approverId: string,
    notes?: string
  ) {
    const approval = await db.campaign_approvals.findOne({ id: approvalId });

    if (!approval) {
      throw new Error('Approval request not found');
    }

    if (approval.status !== 'pending') {
      throw new Error('Approval already processed');
    }

    // Update approval
    await db.campaign_approvals.update(
      { id: approvalId },
      {
        status: 'approved',
        approver_id: approverId,
        notes,
        reviewed_at: new Date()
      }
    );

    // Activate campaign
    await db.campaigns.update(
      { id: approval.campaign_id },
      {
        status: 'active',
        approved_by: approverId,
        published_at: new Date()
      }
    );

    // Notify requester
    await notificationService.send({
      user_id: approval.requester_id,
      type: 'campaign_approved',
      title: 'Campaign Approved',
      message: `Your campaign has been approved and is now live!`,
      data: { campaign_id: approval.campaign_id }
    });

    return { success: true };
  }

  /**
   * Reject campaign
   */
  async rejectCampaign(
    approvalId: string,
    approverId: string,
    notes: string
  ) {
    const approval = await db.campaign_approvals.findOne({ id: approvalId });

    if (!approval) {
      throw new Error('Approval request not found');
    }

    // Update approval
    await db.campaign_approvals.update(
      { id: approvalId },
      {
        status: 'rejected',
        approver_id: approverId,
        notes,
        reviewed_at: new Date()
      }
    );

    // Mark campaign inactive
    await db.campaigns.update(
      { id: approval.campaign_id },
      { status: 'inactive' }
    );

    // Notify requester
    await notificationService.send({
      user_id: approval.requester_id,
      type: 'campaign_rejected',
      title: 'Campaign Rejected',
      message: `Your campaign was rejected. Reason: ${notes}`,
      data: { campaign_id: approval.campaign_id }
    });

    return { success: true };
  }

  /**
   * Request changes
   */
  async requestChanges(
    approvalId: string,
    approverId: string,
    changesRequested: string
  ) {
    const approval = await db.campaign_approvals.findOne({ id: approvalId });

    if (!approval) {
      throw new Error('Approval request not found');
    }

    // Update approval
    await db.campaign_approvals.update(
      { id: approvalId },
      {
        status: 'changes_requested',
        approver_id: approverId,
        changes_requested: changesRequested,
        reviewed_at: new Date()
      }
    );

    // Notify requester
    await notificationService.send({
      user_id: approval.requester_id,
      type: 'campaign_changes_requested',
      title: 'Changes Requested',
      message: `Please update your campaign: ${changesRequested}`,
      data: { campaign_id: approval.campaign_id }
    });

    return { success: true };
  }

  /**
   * Sync Pub2 campaign status (background job)
   */
  async syncCampaignStatus(campaignId: string) {
    const campaign = await db.campaigns.findOne({ id: campaignId });

    if (!campaign) {
      throw new Error('Campaign not found');
    }

    const tenantConfig = await this.getTenantPub2Config(campaign.tenant_id);

    try {
      // Fetch latest from Pub2
      const pub2Campaign = await this.pub2Client.getCampaignById(
        campaign.pub2_campaign_id,
        tenantConfig.pub2ApiKey
      );

      if (!pub2Campaign) {
        // Campaign deleted on Pub2
        await this.handlePub2CampaignDeleted(campaign);
        return;
      }

      const oldStatus = campaign.pub2_campaign_status;
      const newStatus = pub2Campaign.status;

      // Check if status changed
      if (oldStatus !== newStatus) {
        // Update campaign
        await db.campaigns.update(
          { id: campaignId },
          {
            pub2_campaign_status: newStatus,
            pub2_last_synced: new Date()
          }
        );

        // Log sync
        await db.campaign_sync_logs.create({
          campaign_id: campaignId,
          pub2_campaign_id: campaign.pub2_campaign_id,
          sync_type: 'status_check',
          old_value: { status: oldStatus },
          new_value: { status: newStatus },
          sync_status: 'success'
        });

        // Notify admin if ended
        if (newStatus === 'ended') {
          await this.notifyAdminCampaignEnded(campaign);
        }
      } else {
        // No change, just update sync time
        await db.campaigns.update(
          { id: campaignId },
          { pub2_last_synced: new Date() }
        );
      }

    } catch (error) {
      console.error(`Sync failed for campaign ${campaignId}:`, error);

      // Log failed sync
      await db.campaign_sync_logs.create({
        campaign_id: campaignId,
        pub2_campaign_id: campaign.pub2_campaign_id,
        sync_type: 'status_check',
        sync_status: 'failed',
        error_message: error.message
      });
    }
  }

  /**
   * Bulk sync all active campaigns (cron job)
   */
  async syncAllCampaigns(tenantId: string) {
    const campaigns = await db.campaigns
      .where('tenant_id', tenantId)
      .whereIn('status', ['active', 'draft'])
      .select('id');

    console.log(`Syncing ${campaigns.length} campaigns for tenant ${tenantId}`);

    for (const campaign of campaigns) {
      await this.syncCampaignStatus(campaign.id);

      // Rate limiting: Wait 100ms between API calls
      await new Promise(resolve => setTimeout(resolve, 100));
    }
  }

  /**
   * Check if merchant is competitor
   */
  private isCompetitorCampaign(merchantName: string, tenantId: string): boolean {
    const competitorKeywords = {
      'tcb': ['vietcombank', 'bidv', 'vietinbank', 'agribank', 'mb bank', 'acb'],
      'vinfast': ['toyota', 'honda', 'hyundai', 'kia', 'mazda', 'mitsubishi'],
      'ambassador': []  // No specific competitors, general platform
    };

    const keywords = competitorKeywords[tenantId] || [];
    const merchantLower = merchantName.toLowerCase();

    return keywords.some(keyword => merchantLower.includes(keyword));
  }

  /**
   * Check if category is relevant to tenant
   */
  private isCategoryRelevant(category: string, tenantId: string): boolean {
    const relevantCategories = {
      'tcb': ['banking', 'finance', 'insurance', 'investment', 'credit'],
      'vinfast': ['automotive', 'ev', 'car', 'vehicle', 'insurance', 'finance'],
      'ambassador': []  // All categories OK
    };

    const categories = relevantCategories[tenantId];
    if (!categories || categories.length === 0) return true;  // No restriction

    const categoryLower = category.toLowerCase();
    return categories.some(rel => categoryLower.includes(rel));
  }

  /**
   * Check if updates contain major changes requiring re-approval
   */
  private hasMajorChanges(
    original: any,
    updates: Partial<CampaignCreateData>
  ): boolean {
    const majorFields = [
      'commission_rate',
      'commission_type',
      'commission_amount',
      'full_description'
    ];

    return majorFields.some(field => {
      return updates[field] !== undefined && updates[field] !== original[field];
    });
  }

  /**
   * Notify managers about new approval request
   */
  private async notifyManagers(campaignId: string, requesterId: string) {
    const campaign = await db.campaigns.findOne({ id: campaignId });
    const managers = await db.users
      .where('tenant_id', campaign.tenant_id)
      .where('role', 'manager')
      .select('id');

    for (const manager of managers) {
      await notificationService.send({
        user_id: manager.id,
        type: 'campaign_pending_approval',
        title: 'New Campaign Pending Approval',
        message: `${campaign.title} requires your review`,
        data: { campaign_id: campaignId, requester_id: requesterId }
      });
    }
  }

  /**
   * Notify admin when Pub2 campaign ends
   */
  private async notifyAdminCampaignEnded(campaign: any) {
    const admins = await db.users
      .where('tenant_id', campaign.tenant_id)
      .whereIn('role', ['admin', 'manager'])
      .select('id');

    for (const admin of admins) {
      await notificationService.send({
        user_id: admin.id,
        type: 'campaign_ended',
        title: 'Campaign Ended on Pub2',
        message: `"${campaign.title}" has ended on Pub2. Please review and update status.`,
        data: { campaign_id: campaign.id }
      });
    }
  }

  /**
   * Handle Pub2 campaign deletion
   */
  private async handlePub2CampaignDeleted(campaign: any) {
    await db.campaigns.update(
      { id: campaign.id },
      {
        pub2_campaign_status: 'deleted',
        status: 'archived'
      }
    );

    await db.campaign_sync_logs.create({
      campaign_id: campaign.id,
      pub2_campaign_id: campaign.pub2_campaign_id,
      sync_type: 'status_check',
      old_value: { status: campaign.pub2_campaign_status },
      new_value: { status: 'deleted' },
      sync_status: 'success'
    });

    await this.notifyAdminCampaignEnded(campaign);
  }

  /**
   * Get tenant Pub2 config
   */
  private async getTenantPub2Config(tenantId: string) {
    const config = await db.tenant_pub2_config.findOne({
      tenant_id: tenantId,
      enabled: true
    });

    if (!config) {
      throw new Error(`Pub2 integration not enabled for tenant: ${tenantId}`);
    }

    return config;
  }
}

export default new CampaignManagementService();
```

---

## Background Jobs

### Cron Job: Sync Pub2 Campaign Status

```typescript
// jobs/syncPub2Campaigns.job.ts

import cron from 'node-cron';
import campaignManagementService from '../services/CampaignManagement.service';
import db from '../db';

/**
 * Sync Pub2 campaign status for all tenants
 * Runs every hour
 */
export function startPub2SyncJob() {
  // Every hour at :00
  cron.schedule('0 * * * *', async () => {
    console.log('[Pub2 Sync] Starting hourly sync...');

    try {
      // Get all tenants with Pub2 enabled
      const tenants = await db.tenant_pub2_config
        .where('enabled', true)
        .select('tenant_id');

      for (const tenant of tenants) {
        console.log(`[Pub2 Sync] Syncing campaigns for tenant: ${tenant.tenant_id}`);

        await campaignManagementService.syncAllCampaigns(tenant.tenant_id);
      }

      console.log('[Pub2 Sync] Hourly sync completed');
    } catch (error) {
      console.error('[Pub2 Sync] Error during sync:', error);
    }
  });

  console.log('[Pub2 Sync] Job scheduled (runs every hour)');
}
```

---

## Security & Permissions

### Role-Based Access Control

```typescript
// middleware/campaignPermissions.middleware.ts

export const campaignPermissions = {
  // Who can browse Pub2 campaigns
  browsePub2: ['admin', 'editor', 'manager'],

  // Who can create campaigns
  create: ['admin', 'editor'],

  // Who can edit campaigns
  edit: {
    draft: ['admin', 'editor', 'manager'],  // Own drafts
    active: ['admin', 'manager'],  // Active campaigns need higher permission
    inactive: ['admin']
  },

  // Who can approve
  approve: ['manager', 'admin'],

  // Who can delete
  delete: ['admin'],

  // Who can view analytics
  viewAnalytics: ['admin', 'editor', 'manager']
};

/**
 * Check if user can perform action on campaign
 */
export async function checkCampaignPermission(
  userId: string,
  action: string,
  campaign?: any
): Promise<boolean> {
  const user = await db.users.findOne({ id: userId });

  if (!user) return false;

  // Super admin bypass
  if (user.role === 'super_admin') return true;

  // Check action permission
  switch (action) {
    case 'browse_pub2':
      return campaignPermissions.browsePub2.includes(user.role);

    case 'create':
      return campaignPermissions.create.includes(user.role);

    case 'edit':
      if (!campaign) return false;
      const editRoles = campaignPermissions.edit[campaign.status];
      if (!editRoles) return false;

      // If editor, can only edit own campaigns
      if (user.role === 'editor') {
        return campaign.created_by === userId;
      }

      return editRoles.includes(user.role);

    case 'approve':
      return campaignPermissions.approve.includes(user.role);

    case 'delete':
      return campaignPermissions.delete.includes(user.role);

    case 'view_analytics':
      return campaignPermissions.viewAnalytics.includes(user.role);

    default:
      return false;
  }
}
```

---

## Analytics & Reporting

### Campaign Performance Query

```typescript
// services/CampaignAnalytics.service.ts

interface CampaignPerformanceMetrics {
  views: number;
  linkGenerations: number;
  totalClicks: number;
  totalConversions: number;
  totalCommission: number;
  ctr: number;  // Click-through rate
  cvr: number;  // Conversion rate
  topInfluencers: Array<{
    id: string;
    name: string;
    conversions: number;
    commission: number;
  }>;
}

class CampaignAnalyticsService {

  /**
   * Get campaign performance metrics
   */
  async getCampaignPerformance(
    campaignId: string,
    dateRange: { start: Date; end: Date }
  ): Promise<CampaignPerformanceMetrics> {
    const { start, end } = dateRange;

    // Aggregate from campaign_metrics table
    const metrics = await db.campaign_metrics
      .where('campaign_id', campaignId)
      .whereBetween('date', [start, end])
      .select(
        db.raw('SUM(views) as total_views'),
        db.raw('SUM(link_generations) as total_link_generations'),
        db.raw('SUM(total_clicks) as total_clicks'),
        db.raw('SUM(total_conversions) as total_conversions'),
        db.raw('SUM(total_commission) as total_commission')
      )
      .first();

    // Calculate rates
    const ctr = metrics.total_link_generations > 0
      ? (metrics.total_clicks / metrics.total_link_generations) * 100
      : 0;

    const cvr = metrics.total_clicks > 0
      ? (metrics.total_conversions / metrics.total_clicks) * 100
      : 0;

    // Get top influencers
    const topInfluencers = await this.getTopInfluencers(
      campaignId,
      dateRange,
      5  // Top 5
    );

    return {
      views: metrics.total_views || 0,
      linkGenerations: metrics.total_link_generations || 0,
      totalClicks: metrics.total_clicks || 0,
      totalConversions: metrics.total_conversions || 0,
      totalCommission: parseFloat(metrics.total_commission) || 0,
      ctr: parseFloat(ctr.toFixed(2)),
      cvr: parseFloat(cvr.toFixed(2)),
      topInfluencers
    };
  }

  /**
   * Get top performing influencers for campaign
   */
  private async getTopInfluencers(
    campaignId: string,
    dateRange: { start: Date; end: Date },
    limit: number = 5
  ) {
    const topInfluencers = await db.pub2_conversions
      .join('pub2_affiliate_links', 'pub2_conversions.link_id', 'pub2_affiliate_links.id')
      .join('campaigns', 'pub2_affiliate_links.campaign_id', 'campaigns.id')
      .join('influencers', 'pub2_affiliate_links.influencer_id', 'influencers.id')
      .where('campaigns.id', campaignId)
      .whereBetween('pub2_conversions.purchased_at', [dateRange.start, dateRange.end])
      .groupBy('influencers.id', 'influencers.name')
      .select(
        'influencers.id',
        'influencers.name',
        db.raw('COUNT(*) as conversions'),
        db.raw('SUM(pub2_conversions.commission) as commission')
      )
      .orderBy('commission', 'desc')
      .limit(limit);

    return topInfluencers.map(inf => ({
      id: inf.id,
      name: inf.name,
      conversions: inf.conversions,
      commission: parseFloat(inf.commission)
    }));
  }
}

export default new CampaignAnalyticsService();
```

---

## Summary

### Key Features

✅ **Manual Curation**
- Admin browses Pub2 campaigns
- Selects relevant campaigns only
- Full customization before publish

✅ **Brand Safety**
- Competitor detection (Vietcombank, BIDV, etc.)
- Category relevance checking
- Zero auto-sync risk

✅ **Approval Workflow**
- Draft → Pending → Approved → Active
- Multi-level review (editor → manager)
- Changes requested feedback loop

✅ **Pub2 Sync**
- Background jobs check campaign status
- Notify admin if campaign ends on Pub2
- Log all sync activities

✅ **Analytics**
- Performance metrics per campaign
- Top influencers ranking
- CTR, CVR calculations

---

### Next Steps

1. **UI Implementation:**
   - Build React components for admin panel
   - Implement approval workflow UI
   - Create analytics dashboards

2. **Testing:**
   - Unit tests for service layer
   - Integration tests with Pub2 API (sandbox)
   - E2E tests for approval workflow

3. **Documentation:**
   - Admin user guide
   - API documentation
   - Troubleshooting runbook

4. **Deployment:**
   - Database migration
   - Cron job setup
   - Permission configuration

---

**Document Status:** Architecture Complete
**Last Updated:** 2026-02-07
**Next Review:** After stakeholder feedback
