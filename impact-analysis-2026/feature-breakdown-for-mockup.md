# PHÂN TÍCH CHỨC NĂNG CHO MOCKUP - AMBASSADOR INFLUENCER PLATFORM 2026

**Ngày:** 2026-02-06
**Mục đích:** Phân tích chi tiết các chức năng để vẽ mockup UI/UX
**Dựa trên:**
- [Influencer Library](../influencer-library/core/prd-at-core-influence-library-2026-01-31.md)
- [Influencer Matching](../influencer-matching/Influencer-Library-Matching-System-Roadmap.md)
- [Ambassador Roadmap 2026](../ambassador-influencer-roadmap-2026.md)

---

## TỔNG QUAN HỆ THỐNG

### Kiến Trúc 3 Tầng

```
┌─────────────────────────────────────────────────────────────────┐
│                   VENDOR (Influence-Meter API)                  │
│  • Profile Scoring & Demographics                               │
│  • Social Crawler (TikTok, Instagram, YouTube, Facebook)        │
│  • Matching Engine API                                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │ API Integration
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              AT CORE (AccessTrade Platform)                     │
│  • AT Shared Pool (Influencer Library)                          │
│  • Partner API (for Techcombank, Vinfast, etc.)                 │
│  • Admin Dashboard                                              │
│  • Campaign Management (future)                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │ Source Code Sale
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│           PARTNER INSTANCES (Techcombank, Vinfast...)           │
│  • Own 100% source code                                         │
│  • Custom branding & features                                   │
│  • Self-hosted infrastructure                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## MODULE 1: INFLUENCER LIBRARY (Đã chi tiết)

> Chi tiết đầy đủ tại: [PRD AT Core Influence Library](../influencer-library/core/prd-at-core-influence-library-2026-01-31.md)

### 1.1. AT Shared Pool Management (Admin)

#### Trang: `/admin/pool`

**Chức năng chính:**
- ✅ **List Pool Influencers** - Danh sách tất cả influencers trong AT Pool
- ✅ **Add Influencer** - Thêm influencer mới (by URL hoặc manual)
- ✅ **Edit Influencer** - Sửa category, tier, visibility
- ✅ **Remove Influencer** - Xóa khỏi pool (soft delete)
- ✅ **Bulk Import** - Import từ CSV
- ✅ **Sync Management** - Quản lý đồng bộ với Vendor API

**UI Components cần thiết:**

1. **Pool Influencer List Table**
   ```
   Columns:
   - Avatar & Name
   - Platform badge
   - Username
   - Followers count
   - Engagement rate
   - Score (0-100) with color coding
   - Tier badge (Standard/Premium/VIP)
   - Category tag
   - Visibility toggle (Public/Private)
   - Sync status indicator
   - Last synced timestamp
   - Actions: Edit, Sync, Remove
   ```

2. **Filters Panel**
   ```
   - Platform (TikTok, YouTube, Instagram, Facebook)
   - Category (Beauty, Tech, Lifestyle, Food, Travel, Gaming)
   - Tier (Standard, Premium, VIP)
   - Visibility (Public, Private)
   - Sync Status (Active, Paused, Failed, Pending Approval)
   - Score range slider
   - Followers range slider
   - Search by username/name
   ```

3. **Add Influencer Modal**
   ```
   Tab 1: By URL
   - Social URL input
   - Platform auto-detect
   - Category dropdown
   - Tier dropdown
   - Visibility toggle
   - "Crawl & Add" button

   Tab 2: Manual Entry
   - Platform select
   - Username input
   - Display name
   - Basic info form
   - "Add Without Crawl" button
   ```

4. **Bulk Import Modal**
   ```
   - CSV upload dropzone
   - CSV template download link
   - Column mapping interface
   - Import preview table
   - Progress bar
   - Success/failure report
   ```

5. **Sync Management Dashboard**
   ```
   Overview Cards:
   - Last sync time
   - Total influencers
   - Synced successfully
   - Failed syncs
   - Next scheduled sync

   Failed Syncs Table:
   - Influencer info
   - Error message
   - Retry button

   Sync Settings Form:
   - Schedule (cron expression)
   - Batch size
   - Timeout settings
   ```

### 1.2. Partner Pool Access (Partner API Consumer)

#### Trang: `/partners/pool`

**Chức năng chính:**
- ✅ **Search Pool** - Tìm kiếm influencers trong public pool
- ✅ **Request Influencers** - Request access để nhận full data
- ✅ **View Quota** - Xem quota còn lại
- ✅ **Submission Tracking** - Theo dõi submissions đã gửi

**UI Components cần thiết:**

1. **Pool Search Interface**
   ```
   Search Bar:
   - Keyword search
   - Advanced filters button

   Filter Sidebar:
   - Category chips
   - Platform checkboxes
   - Followers range slider
   - Engagement range slider
   - Min score slider

   Results Grid:
   - Avatar, name, username
   - Platform badge
   - Followers, engagement
   - Score badge
   - "Preview Only" watermark
   - "Request Access" button
   ```

2. **Quota Dashboard Widget**
   ```
   - Used / Limit progress bar
   - Remaining count (large number)
   - Resets at date
   - Tier badge
   - "Upgrade Plan" CTA (if applicable)
   ```

3. **Request Influencers Modal**
   ```
   - Selected influencers list (max 20)
   - Reason textarea
   - Quota impact preview
   - "Submit Request" button
   - Auto-approve notification
   ```

4. **Influencer Detail Modal (Preview)**
   ```
   Preview Mode (before request):
   - Basic info only
   - Metrics summary
   - Contact info HIDDEN
   - "Request to see contact info" CTA

   Full Mode (after approved):
   - Complete profile
   - Contact info (email, phone)
   - Detailed metrics
   - Download vCard button
   ```

### 1.3. Partner Submission Flow

#### Trang: `/partners/pool/submit`

**Chức năng chính:**
- ✅ **Submit URL** - Gửi URL để thêm influencer vào pool
- ✅ **Track Submissions** - Theo dõi trạng thái approval
- ✅ **View Submission Detail** - Chi tiết influencer đã submit

**UI Components cần thiết:**

1. **Submit URL Form**
   ```
   - Social URL input (with validation)
   - Platform auto-detect badge
   - "Submit for Approval" button
   - Callback URL (optional)
   - Estimated review time notice
   ```

2. **Submissions List**
   ```
   Columns:
   - Submitted date
   - Profile preview (avatar, username)
   - Platform
   - Status badge (Pending, Enriching, Ready for Review, Approved, Rejected)
   - Review time (if approved/rejected)
   - Actions: View Detail
   ```

3. **Submission Detail Modal**
   ```
   Status: PENDING
   - Profile preview
   - "Waiting for admin review"
   - Estimated review time

   Status: APPROVED
   - Full profile data
   - Approved by (admin name)
   - Approved at (timestamp)
   - "Add to Campaign" button

   Status: REJECTED
   - Profile preview
   - Rejection reason
   - Rejected by (admin name)
   - "Submit Another" button
   ```

### 1.4. Approval Workflow (Admin)

#### Trang: `/admin/pool/submissions`

**Chức năng chính:**
- ✅ **List Pending Submissions** - Danh sách chờ duyệt
- ✅ **Review Submission** - Xem chi tiết và approve/reject
- ✅ **Auto-Approve Configuration** - Cấu hình rules tự động approve

**UI Components cần thiết:**

1. **Pending Submissions Table**
   ```
   Columns:
   - Submitted date
   - Partner name
   - Profile preview (avatar, username, platform)
   - Followers count
   - Score
   - Eligibility check result (badge)
   - Actions: Approve, Reject, View Detail
   ```

2. **Submission Review Modal**
   ```
   Left Panel:
   - Full enriched profile
   - Score breakdown
   - Eligibility check detail

   Right Panel:
   - Partner info
   - Submission timestamp
   - Callback URL (if any)
   - Approve button
   - Reject button (with reason textarea)
   ```

3. **Auto-Approve Settings**
   ```
   Enable/Disable Toggle

   Rules Configuration:
   - Min followers threshold
   - Min score threshold
   - Allowed platforms checkboxes
   - Auto-approve only verified accounts toggle

   Rule History Table:
   - Rule change log
   - Changed by (admin)
   - Changed at (timestamp)
   ```

---

## MODULE 2: INFLUENCER MATCHING (Đã chi tiết)

> Chi tiết đầy đủ tại: [Influencer Matching Roadmap](../influencer-matching/Influencer-Library-Matching-System-Roadmap.md)

### 2.1. Campaign-Based Matching

#### Trang: `/campaigns/:id/matching`

**Chức năng chính:**
- ✅ **Advanced Search** - Tìm kiếm với filters phức tạp
- ✅ **Multi-Dimensional Scoring** - Hiển thị điểm matching
- ✅ **Matching History** - Lịch sử matching sessions

**UI Components cần thiết:**

1. **Campaign Target Audience Form**
   ```
   Demographics:
   - Age range slider
   - Gender checkboxes
   - Location multi-select
   - Interests tags input

   Campaign Info:
   - Category select
   - Budget tier select
   - Brand safety requirements
   ```

2. **Matching Results Table**
   ```
   Columns:
   - Rank (#1, #2, ...)
   - Influencer (avatar, name, username)
   - Platform badge
   - Match Score (0-100) with color
   - Score Breakdown button
   - Category match badge
   - Tier match badge
   - Engagement rate
   - Add to Campaign button
   ```

3. **Score Breakdown Modal**
   ```
   Overall Score: 85/100

   Breakdown:
   - Category Match: 95/100 (Beauty ↔ Beauty)
   - Budget Tier Match: 80/100 (Premium tier)
   - Engagement Rate: 90/100 (4.8%)
   - Audience Match: 75/100 (demographics alignment)
   - Brand Safety: 100/100 (verified, no controversy)

   Recommendation: "Highly Recommended"
   ```

4. **Matching History Tab**
   ```
   Session Cards:
   - Timestamp
   - Filters used
   - Number of results
   - Top 3 influencers preview
   - "View Full Results" button
   - "Export Report" button
   ```

### 2.2. Demographics Integration

#### Component: **Influencer Profile Card**

**Chức năng chính:**
- ✅ **Display Demographics** - Hiển thị audience demographics
- ✅ **Reliability Badge** - Hiển thị độ tin cậy data
- ✅ **Data Source Transparency** - Nguồn gốc data

**UI Components cần thiết:**

1. **Demographics Section**
   ```
   Header: "Audience Demographics" + Reliability Badge

   Age Distribution Chart:
   - 13-17: 15%
   - 18-24: 45%
   - 25-34: 30%
   - 35-44: 8%
   - 45+: 2%

   Gender Distribution Chart:
   - Female: 82%
   - Male: 16%
   - Other: 2%

   Location Distribution:
   - Vietnam: 85%
   - Thailand: 8%
   - Other SEA: 7%
   ```

2. **Reliability Badge**
   ```
   HIGH (✓✓ Verified):
   - Green badge
   - Tooltip: "Manual verified via Instagram Insights"

   MEDIUM (✓ Trusted):
   - Blue badge
   - Tooltip: "Estimated with high confidence (OCR)"

   LOW (~ Estimated):
   - Yellow badge
   - Tooltip: "Estimated via rule-based inference"
   - Warning: "May not be accurate for this campaign"
   ```

3. **Data Source Transparency Card**
   ```
   Source: Manual Verified
   Submitted: 2026-01-25
   Verified by: Admin name
   Confidence: 85%
   Last updated: 3 days ago

   "Request Refresh" button (if partner tier allows)
   ```

---

## MODULE 3: CAMPAIGN MANAGEMENT (Cần bổ sung)

> **Trạng thái:** Chưa có PRD chi tiết
> **Độ ưu tiên:** HIGH (Cần cho roadmap Month 2)

### 3.1. Campaign Creation & Setup

#### Trang: `/campaigns/new`

**Chức năng chính:**
- ⚠️ **Campaign Basic Info** - Tên, mô tả, timeline
- ⚠️ **Target Audience Setup** - Demographics, interests
- ⚠️ **Budget & Tier Selection** - Budget allocation, influencer tiers
- ⚠️ **Brand Safety Settings** - Content guidelines, exclusions
- ⚠️ **Discount Code Generation** - Manual tracking codes

**UI Components cần thiết:**

1. **Campaign Info Form**
   ```
   Step 1: Basic Information
   - Campaign name input
   - Description textarea
   - Category select (Beauty, Tech, Lifestyle, etc.)
   - Start date picker
   - End date picker
   - Campaign objective select (Awareness, Conversion, Engagement)
   ```

2. **Target Audience Builder**
   ```
   Demographics:
   - Age range slider (13-17, 18-24, 25-34, 35-44, 45+)
   - Gender checkboxes (Female, Male, Other)
   - Location tree select (Vietnam cities)
   - Interests tag input (autocomplete)

   Preview Widget:
   - Estimated reach
   - Matched influencers count
   - "Find Influencers" button → redirect to matching
   ```

3. **Budget Allocation**
   ```
   Total Budget: Input (VND)

   Tier Distribution:
   - Nano (1K-10K): Budget % slider
   - Micro (10K-100K): Budget % slider
   - Mid (100K-500K): Budget % slider
   - Macro (500K-1M): Budget % slider
   - Mega (1M+): Budget % slider

   Total: 100% validation

   Estimated Influencer Count per Tier
   ```

4. **Brand Safety Settings**
   ```
   Content Guidelines:
   - Do's and Don'ts textarea
   - Hashtags required (input)
   - Mentions required (input)
   - Link required (URL input)

   Exclusions:
   - Controversial topics tags
   - Competitor mentions tags
   - NSFW content toggle
   ```

5. **Tracking Setup**
   ```
   Tracking Method: Manual (Discount Codes)

   Code Generation:
   - Prefix input (e.g., "TCB2026")
   - Auto-generate toggle
   - Custom codes textarea (bulk input)
   - "Generate Codes" button

   Code Assignment Preview:
   - Influencer name → Code
   - Export CSV button
   ```

### 3.2. Campaign Dashboard

#### Trang: `/campaigns/:id`

**Chức năng chính:**
- ⚠️ **Campaign Overview** - Tổng quan metrics
- ⚠️ **Influencer List** - Danh sách influencers đã chọn
- ⚠️ **Performance Tracking** - Metrics theo dõi
- ⚠️ **Content Management** - Quản lý nội dung posts
- ⚠️ **Payment Tracking** - Theo dõi thanh toán

**UI Components cần thiết:**

1. **Campaign Header**
   ```
   - Campaign name (editable)
   - Status badge (Draft, Active, Paused, Completed)
   - Timeline (Start - End dates)
   - Actions: Edit, Pause/Resume, Archive
   ```

2. **Overview Metrics Cards**
   ```
   Card 1: Total Influencers
   - Count (large number)
   - By tier breakdown

   Card 2: Total Reach
   - Estimated reach (followers sum)
   - Actual reach (posts viewed)

   Card 3: Engagement
   - Total likes, comments, shares
   - Engagement rate

   Card 4: Budget Tracking
   - Spent / Total budget
   - Progress bar
   - Remaining budget
   ```

3. **Influencer List Table**
   ```
   Columns:
   - Influencer (avatar, name, username)
   - Platform badge
   - Tier badge
   - Status (Invited, Accepted, Posted, Completed)
   - Discount code assigned
   - Posts count
   - Reach
   - Engagement
   - Payment status
   - Actions: View Profile, Contact, Remove
   ```

4. **Content Posts Table**
   ```
   Columns:
   - Thumbnail (post image/video)
   - Influencer name
   - Platform badge
   - Post type (Photo, Video, Story, Reel)
   - Posted date
   - Link to post (external)
   - Views, Likes, Comments, Shares
   - Discount code used count
   - Approve/Reject buttons (if moderation)
   ```

5. **Payment Tracking Table**
   ```
   Columns:
   - Influencer name
   - Tier
   - Agreed amount (VND)
   - Payment method (Bank Transfer, MoMo, ZaloPay)
   - Status (Pending, Paid, Failed)
   - Invoice link
   - Paid date
   - Actions: Mark as Paid, Download Invoice
   ```

### 3.3. Campaign Analytics

#### Trang: `/campaigns/:id/analytics`

**Chức năng chính:**
- ⚠️ **Performance Overview** - Tổng quan hiệu suất
- ⚠️ **Influencer Ranking** - Xếp hạng influencers
- ⚠️ **Content Performance** - Hiệu suất từng post
- ⚠️ **ROI Calculation** - Tính toán ROI

**UI Components cần thiết:**

1. **Performance Timeline Chart**
   ```
   Line Chart:
   - X: Date
   - Y: Reach, Engagement, Conversions
   - Multiple series (selectable)
   - Date range picker
   ```

2. **Top Performers Leaderboard**
   ```
   Rankings:
   1. Influencer A - 1.2M reach - 8.5% engagement
   2. Influencer B - 980K reach - 7.8% engagement
   3. Influencer C - 750K reach - 9.2% engagement

   Sorting options:
   - By reach
   - By engagement
   - By conversions (discount code usage)
   ```

3. **Content Type Breakdown**
   ```
   Pie Chart:
   - Photos: 40%
   - Videos: 35%
   - Stories: 15%
   - Reels: 10%

   Bar Chart (Performance by Type):
   - Avg engagement per type
   ```

4. **ROI Calculator**
   ```
   Input:
   - Total budget spent
   - Revenue generated (from discount codes)

   Output:
   - ROI percentage
   - Cost per reach (CPR)
   - Cost per engagement (CPE)
   - Cost per conversion (CPC)

   Comparison to Industry Benchmark
   ```

---

## MODULE 4: BOOKING & COLLABORATION (Cần bổ sung)

> **Trạng thái:** Chưa có PRD chi tiết
> **Độ ưu tiên:** HIGH (Roadmap Month 2, 5, 6, 7)

### 4.1. Influencer Booking Flow

#### Trang: `/campaigns/:id/booking`

**Chức năng chính:**
- ⚠️ **Send Invitations** - Gửi lời mời influencers
- ⚠️ **Track Responses** - Theo dõi responses (Accept/Decline)
- ⚠️ **Contract Generation** - Tạo hợp đồng tự động
- ⚠️ **Booking Calendar** - Lịch booking timeline

**UI Components cần thiết:**

1. **Invite Influencers Modal**
   ```
   Selected Influencers List:
   - Avatar, name, tier
   - Estimated cost (auto-calculate by tier)
   - Remove button

   Invitation Template:
   - Email template editor
   - Merge fields (influencer name, campaign name, etc.)
   - "Send Invitations" button
   ```

2. **Booking Responses Table**
   ```
   Columns:
   - Influencer (avatar, name)
   - Invited date
   - Response status (Pending, Accepted, Declined, Negotiating)
   - Proposed rate (if negotiating)
   - Contract status (Pending, Signed)
   - Actions: Accept Rate, Decline, Send Contract
   ```

3. **Contract Generator**
   ```
   Template Selection:
   - Standard contract
   - Custom template upload

   Contract Fields (auto-filled):
   - Brand info
   - Influencer info
   - Campaign details
   - Deliverables (posts count, type)
   - Payment terms
   - Deadline

   E-Signature Integration:
   - DocuSign / local solution
   - "Send for Signature" button
   ```

4. **Booking Calendar**
   ```
   Timeline View:
   - X: Dates
   - Y: Influencers
   - Blocks: Booking periods
   - Color coding: Status (Invited, Booked, Posted, Completed)

   Conflict Detection:
   - Warning if influencer double-booked
   ```

### 4.2. Communication Hub

#### Trang: `/campaigns/:id/messages`

**Chức năng chính:**
- ⚠️ **In-App Messaging** - Chat với influencers
- ⚠️ **Email Integration** - Sync emails
- ⚠️ **Broadcast Messages** - Gửi tin nhắn hàng loạt
- ⚠️ **Notification Center** - Thông báo sự kiện

**UI Components cần thiết:**

1. **Messenger Interface**
   ```
   Left Sidebar: Conversations List
   - Search influencers
   - Filter by status (Unread, All, Archived)
   - Conversation item:
     - Avatar, name
     - Last message preview
     - Unread badge

   Main Panel: Chat Window
   - Message thread
   - Text input + attachments
   - Quick replies templates
   - "Mark as Resolved" button
   ```

2. **Broadcast Message Modal**
   ```
   Recipient Selection:
   - All influencers checkbox
   - Filter by tier, status
   - Selected count preview

   Message Composer:
   - Subject input
   - Rich text editor
   - Attachments upload
   - Schedule send (optional)
   - "Send Broadcast" button
   ```

3. **Notification Center**
   ```
   Notification List:
   - Icon (type: booking, message, post, payment)
   - Title
   - Description
   - Timestamp
   - Actions: View, Dismiss, Mark as Read

   Filter by:
   - Type
   - Read/Unread
   - Date range
   ```

---

## MODULE 5: ADMIN & SETTINGS (Cần bổ sung)

> **Trạng thái:** Một phần đã có (Partner Management trong Library PRD)
> **Độ ưu tiên:** MEDIUM (Hỗ trợ modules khác)

### 5.1. Tenant Management (AT Admin)

#### Trang: `/admin/tenants`

**Chức năng chính:**
- ⚠️ **List Tenants** - Danh sách partners (Techcombank, Vinfast...)
- ⚠️ **Create Tenant** - Tạo tenant mới
- ⚠️ **Manage Subscriptions** - Quản lý gói subscription
- ⚠️ **API Key Management** - Quản lý API keys
- ⚠️ **Usage Analytics** - Theo dõi usage per tenant

**UI Components cần thiết:**

1. **Tenants List Table**
   ```
   Columns:
   - Tenant name (logo, name)
   - Code (unique ID)
   - Subscription tier (Free, Basic, Premium, Enterprise)
   - Status (Active, Expired, Suspended)
   - Quota used/limit
   - Last API call
   - Actions: Edit, View Usage, Manage Keys
   ```

2. **Create Tenant Form**
   ```
   Basic Info:
   - Tenant name
   - Unique code
   - Logo upload
   - Contact name, email, phone

   Subscription:
   - Tier select
   - Start date, End date
   - Auto-renew toggle
   - Monthly quota input

   Features:
   - Features checkboxes (Pool Search, Request, Enrich, etc.)

   "Generate API Key" button
   ```

3. **API Key Management Modal**
   ```
   Current Key:
   - Key (masked, copy button)
   - Created date
   - Last used date
   - Usage count
   - "Regenerate Key" button (warning)

   Key History:
   - Previous keys table
   - Revoked date
   ```

4. **Tenant Usage Dashboard**
   ```
   Time Range Selector: Last 7/30/90 days

   Metrics Cards:
   - Total API Calls
   - Pool Searches
   - Influencer Requests
   - Profiles Enriched

   Usage Chart:
   - Line chart: API calls over time
   - Bar chart: Calls by endpoint

   Quota Status:
   - Used / Limit progress bar
   - Projected usage (next month)
   - "Adjust Quota" button
   ```

### 5.2. User & Permissions Management

#### Trang: `/admin/users`

**Chức năng chính:**
- ⚠️ **List Users** - Danh sách users trong tenant
- ⚠️ **Invite Users** - Mời users mới
- ⚠️ **Role Management** - Phân quyền roles
- ⚠️ **Activity Logs** - Logs hoạt động

**UI Components cần thiết:**

1. **Users List Table**
   ```
   Columns:
   - Avatar, Name
   - Email
   - Role badge (Admin, Manager, Viewer)
   - Status (Active, Pending, Suspended)
   - Last login
   - Actions: Edit, Suspend, Delete
   ```

2. **Invite User Modal**
   ```
   Email input (multiple)
   Role select
   Permissions checkboxes:
   - Manage campaigns
   - Manage influencers
   - View analytics
   - Manage billing
   - etc.

   "Send Invitations" button
   ```

3. **Role Permissions Matrix**
   ```
   Table:
   Rows: Permissions
   Columns: Roles (Admin, Manager, Viewer, Custom)
   Cells: Checkboxes (editable for Custom role)

   "Save Custom Role" button
   ```

4. **Activity Logs Table**
   ```
   Columns:
   - Timestamp
   - User (avatar, name)
   - Action (Created campaign, Invited influencer, etc.)
   - Resource (resource ID)
   - IP address
   - Export CSV button

   Filters:
   - User select
   - Action type select
   - Date range picker
   ```

### 5.3. Platform Settings

#### Trang: `/settings`

**Chức năng chính:**
- ⚠️ **Branding Settings** - Logo, colors, custom domain
- ⚠️ **Email Templates** - Customize email templates
- ⚠️ **Payment Integration** - MoMo, ZaloPay config
- ⚠️ **Webhook Configuration** - Outgoing webhooks

**UI Components cần thiết:**

1. **Branding Settings**
   ```
   Logo Upload:
   - Primary logo (light bg)
   - Secondary logo (dark bg)
   - Favicon

   Color Scheme:
   - Primary color picker
   - Secondary color picker
   - Preview panel

   Custom Domain:
   - Domain input
   - DNS instructions
   - Verification status
   ```

2. **Email Templates Editor**
   ```
   Template List Sidebar:
   - Invitation email
   - Acceptance confirmation
   - Payment notification
   - etc.

   Template Editor:
   - Subject input
   - Rich text editor (with merge fields)
   - Preview button
   - Send test email
   - "Save Template" button
   ```

3. **Payment Integration Config**
   ```
   MoMo Settings:
   - API Key input
   - Secret Key input
   - Endpoint URL
   - Test Connection button

   ZaloPay Settings:
   - Similar fields

   Bank Transfer:
   - Bank name, account number
   - QR code upload
   ```

4. **Webhook Configuration**
   ```
   Webhooks List:
   - URL
   - Events subscribed
   - Status (Active/Inactive)
   - Last triggered
   - Actions: Edit, Delete, Test

   Add Webhook Modal:
   - URL input
   - Events checkboxes (campaign created, influencer accepted, etc.)
   - Secret key (for signature)
   - "Add Webhook" button
   ```

---

## MODULE 6: MARKETPLACE & PUBLIC PAGES (Cần bổ sung)

> **Trạng thái:** Chưa có PRD
> **Độ ưu tiên:** MEDIUM (Roadmap Month 3)

### 6.1. Public Influencer Marketplace

#### Trang: `/marketplace` (Public)

**Chức năng chính:**
- ⚠️ **Browse Influencers** - Duyệt influencers công khai
- ⚠️ **Search & Filter** - Tìm kiếm và lọc
- ⚠️ **Influencer Public Profile** - Trang profile công khai
- ⚠️ **Contact Form** - Form liên hệ booking

**UI Components cần thiết:**

1. **Marketplace Landing Page**
   ```
   Hero Section:
   - Title: "Find Your Perfect Influencer"
   - Search bar (keyword)
   - Popular categories chips

   Featured Influencers Carousel:
   - Top-rated influencers
   - Auto-scroll

   Categories Grid:
   - Beauty, Tech, Lifestyle, etc.
   - Category cards with thumbnail
   ```

2. **Browse & Search Interface**
   ```
   Filter Sidebar:
   - Platform
   - Category
   - Followers range
   - Engagement range
   - Location
   - Price range (if public)

   Results Grid:
   - Influencer cards (3-4 per row)
   - Avatar, name, username
   - Platform badge
   - Followers, engagement
   - Tier badge
   - "View Profile" button

   Sorting:
   - Relevance, Followers, Engagement, Price
   ```

3. **Public Influencer Profile**
   ```
   Header:
   - Cover photo
   - Avatar
   - Name, username
   - Platform links
   - Followers, engagement stats
   - "Contact for Booking" CTA

   About Section:
   - Bio
   - Categories
   - Languages

   Portfolio Section:
   - Recent posts grid (embed or thumbnails)
   - Past collaborations logos

   Statistics Section:
   - Audience demographics charts
   - Engagement breakdown

   Contact Form:
   - Brand name
   - Email
   - Campaign brief
   - Budget range
   - "Send Inquiry" button
   ```

### 6.2. Influencer Self-Service Portal

#### Trang: `/influencers` (Influencer login)

**Chức năng chính:**
- ⚠️ **Profile Management** - Quản lý profile riêng
- ⚠️ **Campaign Invitations** - Nhận và phản hồi invitations
- ⚠️ **Performance Dashboard** - Xem metrics cá nhân
- ⚠️ **Earnings & Payments** - Theo dõi thu nhập

**UI Components cần thiết:**

1. **Influencer Dashboard**
   ```
   Metrics Cards:
   - Active campaigns count
   - Pending invitations count
   - Total earnings (this month)
   - Avg engagement rate

   Recent Activity Feed:
   - New invitation
   - Campaign accepted
   - Payment received
   - etc.
   ```

2. **Profile Editor**
   ```
   Basic Info:
   - Avatar upload
   - Cover photo upload
   - Bio textarea
   - Categories multi-select
   - Languages multi-select

   Social Accounts:
   - TikTok URL
   - Instagram URL
   - YouTube URL
   - Facebook URL
   - "Verify Account" buttons (OAuth)

   Portfolio:
   - Upload past work images/videos
   - Add brand collaboration logos

   Pricing (optional):
   - Rate per post input
   - Rate per story input
   - Custom package descriptions
   ```

3. **Campaign Invitations**
   ```
   Invitations List:
   - Brand logo, name
   - Campaign name
   - Invitation date
   - Offered rate
   - Deliverables (posts count, type)
   - Deadline
   - Actions: Accept, Decline, Counter-Offer

   Invitation Detail Modal:
   - Full campaign brief
   - Brand guidelines
   - Contract preview
   - "Accept & Sign" button
   ```

4. **Earnings & Payments**
   ```
   Earnings Overview:
   - Total earnings (all time)
   - This month earnings
   - Pending payments
   - Paid amount

   Payments Table:
   - Campaign name
   - Brand name
   - Amount
   - Status (Pending, Paid, Failed)
   - Payment method
   - Paid date
   - Invoice download

   Payment Settings:
   - Bank account info
   - MoMo number
   - ZaloPay number
   - "Verify Account" buttons
   ```

---

## MODULE 7: TIKTOK SHOP INTEGRATION (Cần bổ sung)

> **Trạng thái:** Chưa có PRD
> **Độ ưu tiên:** HIGH (Roadmap Month 9, Killer Feature)

### 7.1. TikTok Shop Tracking

#### Trang: `/campaigns/:id/tiktok-shop`

**Chức năng chính:**
- ⚠️ **Link TikTok Shop** - Liên kết TikTok Shop của brand
- ⚠️ **Live-stream Tracking** - Theo dõi live-stream sales
- ⚠️ **GMV Tracking** - Gross Merchandise Value tracking
- ⚠️ **Affiliate Links** - Tạo và tracking affiliate links

**UI Components cần thiết:**

1. **TikTok Shop Integration Setup**
   ```
   Step 1: Connect TikTok Shop Account
   - TikTok Shop URL input
   - OAuth authorization button
   - Connection status indicator

   Step 2: Product Selection
   - Products list (from TikTok Shop API)
   - Checkboxes to select products for campaign
   - Product preview (image, name, price)

   Step 3: Affiliate Links
   - Auto-generate affiliate links per influencer
   - Copy links button
   - Send links to influencers button
   ```

2. **Live-stream Monitoring**
   ```
   Active Live-streams List:
   - Influencer name
   - Live-stream title
   - Start time
   - Current viewers count
   - Real-time sales count
   - "Watch Live" button (embed or external)

   Live-stream Detail Modal:
   - Embedded player (if possible)
   - Real-time metrics:
     - Viewers
     - Likes
     - Comments
     - Products showcased
     - Sales count
     - GMV
   ```

3. **GMV Dashboard**
   ```
   Overview Cards:
   - Total GMV (campaign lifetime)
   - GMV this month
   - Orders count
   - Avg order value

   GMV by Influencer Table:
   - Influencer name
   - Live-streams count
   - Total GMV
   - Orders count
   - Commission earned
   - ROI

   GMV Timeline Chart:
   - Line chart: GMV over time
   - Annotations: Live-stream events
   ```

4. **Affiliate Link Performance**
   ```
   Links Table:
   - Influencer name
   - Product name
   - Affiliate link (copy button)
   - Clicks count
   - Conversions count
   - Conversion rate
   - GMV generated
   - Commission

   Top Performing Links Leaderboard:
   - Rank
   - Link/Product
   - GMV
   - Commission
   ```

---

## MODULE 8: ANALYTICS & REPORTING (Cần bổ sung)

> **Trạng thái:** Một phần trong Campaign Analytics
> **Độ ưu tiên:** MEDIUM (Roadmap Month 7)

### 8.1. Cross-Campaign Analytics

#### Trang: `/analytics`

**Chức năng chính:**
- ⚠️ **Portfolio Overview** - Tổng quan tất cả campaigns
- ⚠️ **Trend Analysis** - Phân tích xu hướng
- ⚠️ **Benchmark Comparison** - So sánh với industry benchmarks
- ⚠️ **Custom Reports** - Tạo báo cáo tùy chỉnh

**UI Components cần thiết:**

1. **Portfolio Overview Dashboard**
   ```
   Summary Cards:
   - Total campaigns (All time, Active, Completed)
   - Total influencers collaborated
   - Total reach
   - Total engagement
   - Total budget spent
   - Avg ROI

   Recent Campaigns Table:
   - Campaign name
   - Status
   - Influencers count
   - Reach
   - Engagement
   - ROI
   - Actions: View Details
   ```

2. **Trend Analysis Charts**
   ```
   Chart 1: Campaign Performance Over Time
   - Line chart: Reach, Engagement, ROI
   - Trend lines
   - Date range picker

   Chart 2: Platform Distribution
   - Pie chart: TikTok, Instagram, YouTube, Facebook
   - Over time changes (animated)

   Chart 3: Category Performance
   - Bar chart: Categories (Beauty, Tech, etc.)
   - Metrics: Reach, Engagement, ROI
   ```

3. **Benchmark Comparison**
   ```
   Industry Benchmarks Table:
   - Metric (Engagement Rate, CPM, ROI)
   - Your Performance
   - Industry Average
   - Difference (% above/below)
   - Color coding (green/red)

   Top Performers (Industry):
   - Anonymized competitor data
   - Percentile ranking
   ```

4. **Custom Report Builder**
   ```
   Step 1: Select Metrics
   - Checkboxes: Reach, Engagement, GMV, ROI, etc.

   Step 2: Filters
   - Date range
   - Campaigns select
   - Platforms select
   - Categories select

   Step 3: Visualization
   - Chart type select (Line, Bar, Pie, Table)

   Step 4: Export
   - Format select (PDF, Excel, CSV)
   - Schedule report (daily, weekly, monthly)
   - "Generate Report" button
   ```

---

## MODULE 9: MOBILE APP (Cần bổ sung)

> **Trạng thái:** Chưa có PRD
> **Độ ưu tiên:** LOW (Roadmap Month 11-12)

### 9.1. Brand Mobile App

**Chức năng chính:**
- ⚠️ **Campaign Monitoring** - Theo dõi campaigns on-the-go
- ⚠️ **Approve Content** - Duyệt posts từ mobile
- ⚠️ **Messaging** - Chat với influencers
- ⚠️ **Push Notifications** - Thông báo real-time

**UI Components cần thiết:**

1. **Mobile Dashboard**
   ```
   Top Cards (horizontal scroll):
   - Active campaigns
   - Pending approvals
   - Unread messages

   Campaign List:
   - Campaign cards (vertical scroll)
   - Thumbnail, name, status
   - Quick stats
   - "View Details" tap
   ```

2. **Content Approval Flow**
   ```
   Posts Queue:
   - Post cards (swipe to approve/reject)
   - Thumbnail, influencer name
   - Caption preview

   Post Detail:
   - Full image/video
   - Caption
   - Hashtags, mentions
   - Metrics preview
   - Approve / Reject buttons
   - Leave comment textarea
   ```

3. **Mobile Messenger**
   ```
   Conversations List:
   - Similar to web interface
   - Unread badges
   - Last message preview

   Chat Interface:
   - Message bubbles
   - Image/video attachments
   - Quick replies
   - Voice messages (optional)
   ```

### 9.2. Influencer Mobile App

**Chức năng chính:**
- ⚠️ **Invitations Management** - Nhận và phản hồi invitations
- ⚠️ **Upload Content** - Upload posts từ phone
- ⚠️ **Performance Tracking** - Xem metrics cá nhân
- ⚠️ **Earnings** - Theo dõi earnings

**UI Components cần thiết:**

1. **Influencer Home**
   ```
   Top Section:
   - Earnings this month (large number)
   - Active campaigns count

   Invitations List:
   - Invitation cards
   - Brand logo, campaign name
   - Offered rate
   - Quick actions: Accept / Decline
   ```

2. **Content Upload Flow**
   ```
   Step 1: Select Campaign
   - Campaign cards list

   Step 2: Upload Media
   - Camera integration
   - Gallery picker
   - Multiple images/videos

   Step 3: Add Details
   - Caption textarea
   - Hashtags input
   - Post type select (Feed, Story, Reel)
   - Platform select (TikTok, Instagram)

   Step 4: Submit
   - "Submit for Approval" button
   - Status notification
   ```

3. **Performance Dashboard**
   ```
   Metrics Cards:
   - Total reach
   - Avg engagement rate
   - Top post (thumbnail)

   Recent Posts List:
   - Post thumbnail
   - Campaign name
   - Platform badge
   - Views, Likes, Comments
   ```

---

## TÓM TẮT CHO MOCKUP DESIGN

### Độ Ưu Tiên Modules (cho vẽ mockup)

#### ✅ **Đã chi tiết đầy đủ (có thể vẽ mockup ngay):**
1. **Influencer Library** (Module 1) - 100% ready
2. **Influencer Matching** (Module 2) - 100% ready

#### ⚠️ **Cần bổ sung chi tiết (ưu tiên HIGH):**
3. **Campaign Management** (Module 3) - 70% complete
   - Thiếu: Content moderation workflow, advanced payment tracking
4. **Booking & Collaboration** (Module 4) - 60% complete
   - Thiếu: Contract templates, negotiation flow details
5. **TikTok Shop Integration** (Module 7) - 50% complete
   - Thiếu: API integration specs, real-time data sync
6. **Admin & Settings** (Module 5) - 80% complete
   - Thiếu: Advanced permissions, audit logs details

#### 🔵 **Cần nghiên cứu thêm (ưu tiên MEDIUM):**
7. **Marketplace & Public Pages** (Module 6) - 40% complete
8. **Analytics & Reporting** (Module 8) - 50% complete

#### 🟡 **Có thể skip trong v1.0 (ưu tiên LOW):**
9. **Mobile App** (Module 9) - 30% complete

---

## NEXT STEPS

### Để hoàn thiện mockup:

1. **Xác nhận scope cho mockup:**
   - Chỉ vẽ Module 1, 2? (đã đủ chi tiết)
   - Hay bao gồm Module 3, 4? (cần bổ sung một số details)

2. **Tạo PRD cho các modules còn thiếu:**
   - Campaign Management (Module 3) - HIGH priority
   - Booking & Collaboration (Module 4) - HIGH priority
   - TikTok Shop Integration (Module 7) - MEDIUM priority

3. **User Flow Diagrams:**
   - Vẽ user flow cho từng module
   - Xác định navigation structure

4. **Design System:**
   - Color palette, typography
   - Component library (buttons, cards, forms)
   - Iconography

5. **Mockup Phases:**
   - Phase 1: Wireframes (low-fidelity)
   - Phase 2: High-fidelity mockups
   - Phase 3: Interactive prototype (Figma)

---

**Document Owner:** Diso Product Team
**Last Updated:** 2026-02-06
**Status:** Draft - Ready for Mockup Design
