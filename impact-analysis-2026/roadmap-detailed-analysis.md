# Ambassador Influencer Platform - Roadmap Analysis (Impact.com Benchmark)

**Objective:**
1. Follow business timeline (library-first approach)
2. Achieve 90% parity với Impact.com Creator module
3. Support 10K → 20K KOC growth

**Timeline:** 11 tháng (Tháng 2 - Tháng 12, 2026)
**Team:** 7 FTE average

---

## Executive Summary

**Development Strategy:**
- **Business Priority**: Library → Booking → Growth (10K → 20K KOCs)
- **Impact.com Benchmark**: Learn from analytics, automation features
- **Key Addition**: Performance analytics and automation tools

**Rationale:**
- Business plan đã có market validation
- Learn from Impact.com's automation & analytics approach
- Manual tracking via discount codes (proven with TCB)

---

## Timeline Comparison

| Month | Business Plan | Impact.com Inspired Features | Ambassador Approach |
|-------|---------------|---------------------|-----------------|
| **T2** | Dashboard + Library cơ bản | + Basic booking system | Dashboard + Library + Booking |
| **T3** | Release Library + Affiliate | + Marketplace search | Public Library + Affiliate + Search |
| **T4** | Library 10K KOCs + Filters | + AI matching (Gemini) | Library 10K + Filters + AI recommendations |
| **T5** | Library 20K + Communication | + Auto-invite workflows | Library 20K + Chat + Auto-invite |
| **T6** | Booking optimization | + Payment automation | Booking + Auto-payment calculation |
| **T7** | Booking tự động | + Analytics dashboard | Smart booking + Performance analytics |
| **T8-12** | KOC sales tools | + Content mgmt + Fraud | Sales tools + Content workflow + Fraud detection |

---

## Detailed Development Timeline

### 🗓️ Tháng 2: Dashboard + Influencer Library + Booking System

#### Business Requirements:
- ✅ Dashboard mới (Admin/Brand view)
- ✅ Influencer library cơ bản (admin và pub tự nhập)
- ✅ Thu thập thông tin và store
- ✅ Hệ thống booking cơ bản
- ✅ Help negotiate budget, review

#### Impact.com Inspired Features:
- 🆕 Manual tracking via discount codes
- 🆕 Campaign performance dashboard

#### Implementation:

**Week 1-2: Admin Dashboard + Library Schema**
```
Admin Dashboard:
- Campaign overview
- Influencer list view
- Application review
- Negotiation notes

Library Schema (MongoDB):
{
  influencerId: "inf_xxx",
  name: "Nguyen Van A",
  platforms: [
    { platform: "tiktok", handle: "@nguyenvana", followers: 15000 }
  ],
  categories: ["beauty", "lifestyle"],
  priceRange: { min: 2000000, max: 5000000 },
  contactInfo: { email, phone },
  portfolio: [links],
  stats: { reach, engagement },
  addedBy: "admin" // manual input
}
```

**Week 3-4: Booking System**
```
Booking Flow:
1. Brand creates campaign with discount code
2. Admin/Brand manually adds influencers to campaign
3. System sends invite email
4. Influencer accepts → gets campaign details + discount code
5. Influencer posts with discount code
6. Manual tracking: Brand inputs sales/conversions per discount code
```

**Deliverables:**
- ✅ Admin dashboard (React)
- ✅ Influencer library (CRUD, manual input)
- ✅ Booking system (manual matching)
- ✅ Discount code generator
- ✅ Manual performance input

**Team:** 2 backend, 2 frontend, 1 PM

**Metrics:**
- Store 100+ influencer profiles (manual input)
- 5 campaigns with booking flow
- 5+ discount codes generated

---

### 🗓️ Tháng 3: Release Library + Affiliate Integration + Public Marketplace

#### Business Requirements:
- ✅ Release Influencer library (public view for brands)
- ✅ Tích hợp Affiliate system (existing)

#### Impact.com Inspired Features:
- 🆕 Public marketplace (influencers browse campaigns)
- 🆕 Search & filters (category, followers, price)
- 🆕 Application flow (influencers self-apply)

#### Implementation:

**Week 1-2: Public Library + Search**
```
Public Library Features:
- Brand can browse influencer profiles
- Filters: category, followers, engagement rate, price
- Influencer detail page (portfolio, stats, pricing)
- Contact button → open booking request

Search Implementation:
- Elasticsearch for fast search
- Filter by: category, followers range, price range, platform
- Sort by: followers, engagement, price

Public URL: app.viewboost.vn/influencers
```

**Week 2-3: Affiliate Integration**
```
Existing Affiliate System:
- AccessTrade affiliate platform
- Integration API available

Integration Points:
1. Unified dashboard (show affiliate + influencer campaigns)
2. Shared performance reporting
3. Unified payment system

Note: Affiliate system đã có → chỉ cần UI integration
```

**Week 3-4: Influencer Self-Application**
```
Marketplace for Influencers:
- URL: app.viewboost.vn/marketplace
- Influencers can browse open campaigns
- Apply with portfolio + pitch
- Track application status

Application Flow:
1. Influencer sees campaign
2. Click "Apply"
3. Submit portfolio + rate
4. Admin review → approve/reject
5. Approved → gets campaign details + discount code
```

**Deliverables:**
- ✅ Public influencer library
- ✅ Search & filters (Elasticsearch)
- ✅ Affiliate UI integration
- ✅ Campaign marketplace (influencer view)
- ✅ Self-application flow

**Team:** 2 frontend, 1 backend, 0.5 designer

**Metrics:**
- 500+ profiles publicly visible
- 10+ campaigns in marketplace
- 50+ applications from influencers

---

### 🗓️ Tháng 4: Library Growth 10K + AI Matching

#### Business Requirements:
- ✅ Phát triển Influencer Library → 10,000 KOCs
- ✅ Hoàn thiện tìm kiếm, lọc, xếp hạng

#### Impact.com Inspired Features:
- 🆕 AI-powered matching (Gemini API)
- 🆕 Smart recommendations
- 🆕 Auto-scoring based on Influence-Meter

#### Implementation:

**Week 1-2: Bulk Onboarding Tools**
```
Growth Strategy (Business side):
- Outreach team manually onboards KOCs
- Influencers self-register via marketplace
- Import from social platforms (scraping)

System Support:
- Bulk CSV import (admin upload 1000 profiles at once)
- Auto-profile enrichment (call Influence-Meter API)
- Duplicate detection
- Profile quality scoring

CSV Format:
name, tiktok_handle, instagram_handle, category, email
```

**Week 2-3: AI Matching System**
```
Gemini API Integration:

Input: Campaign brief + requirements
{
  campaignName: "TCB Credit Card Q1",
  category: ["finance", "lifestyle"],
  targetAudience: "Gen Z, urban",
  budget: 50000000,
  requirements: "Must have >10K followers, engagement >3%"
}

Gemini Processing:
- Semantic matching: campaign brief → influencer bios
- Category detection: infer categories from content
- Audience overlap: match target audience với influencer audience

Output: Ranked list of top 50 matching influencers
[
  { influencerId: "inf_123", matchScore: 0.92, reason: "Strong Gen Z audience, finance content" },
  { influencerId: "inf_456", matchScore: 0.85, reason: "Lifestyle content, urban audience" }
]
```

**Week 3-4: Advanced Search & Ranking**
```
Enhanced Search:
- Semantic search (Gemini): "Gen Z beauty influencers with high engagement"
- Auto-complete suggestions
- Saved searches

Ranking Algorithm:
1. Influence-Meter score (40%)
2. Engagement rate (30%)
3. Relevance to campaign (20%)
4. Price competitiveness (10%)

Leaderboard:
- Top influencers by category
- Rising stars (high engagement, low followers)
- Best ROI (historical performance)
```

**Deliverables:**
- ✅ Bulk onboarding tools (CSV import)
- ✅ AI matching system (Gemini API)
- ✅ Enhanced search & ranking
- ✅ Leaderboard & recommendations
- ✅ 10,000+ profiles in library

**Team:** 2 backend (AI + bulk import), 1 frontend, 1 PM (coordinate growth team)

**Metrics:**
- 10,000+ influencer profiles
- AI matching accuracy: >70%
- Search latency: <500ms
- Bulk import: 1000 profiles in 5 minutes

---

### 🗓️ Tháng 5: Library Growth 20K + Communication Tools

#### Business Requirements:
- ✅ Library → 20,000 KOCs
- ✅ Hoàn thiện giao tiếp, kết nối
- ✅ Hỗ trợ ký kết với KOC

#### Impact.com Inspired Features:
- 🆕 In-platform messaging
- 🆕 Contract templates
- 🆕 Auto-invite workflows
- 🆕 Conversion tracking (basic)

#### Implementation:

**Week 1-2: Communication System**
```
In-Platform Chat:
- Brand ↔ Influencer messaging
- Real-time notifications
- File sharing (contracts, briefs)
- Message history

Tech Stack:
- WebSocket for real-time
- MongoDB for message storage
- Notification service (email + in-app)

Chat UI:
- Inbox (threads per campaign)
- Quick replies (templates)
- @mentions
- Read receipts
```

**Week 2-3: Contract Management**
```
Contract Templates:
- Flat-fee contract
- CPA contract (% of sales)
- Hybrid contract (flat + commission)

Contract Flow:
1. Brand selects template
2. Fill campaign details (deliverables, timeline, payment)
3. Send to influencer
4. Influencer reviews → accepts/negotiates
5. Digital signature (simple checkbox for MVP)
6. Signed contract stored

Note: Full e-signature (DocuSign) is P2, start with simple accept button
```

**Week 3-4: Auto-Invite + Conversion Tracking**
```
Auto-Invite Workflows:
- Brand sets criteria (followers, engagement, category)
- System matches → sends bulk invites
- Track invite status (sent, opened, applied, accepted)

Example:
Criteria: TikTok, 10K-50K followers, Beauty category, engagement >5%
→ System finds 200 matches
→ Sends personalized email invites
→ 40 open, 15 apply, 5 accept

Conversion Tracking (Basic):
- Discount code tracking (integrate with Shopify/WooCommerce)
- Manual conversion input (brand uploads sales data)
- Auto-calculate conversions per influencer
- Update earnings dashboard
```

**Deliverables:**
- ✅ In-platform messaging (WebSocket)
- ✅ Contract templates & flow
- ✅ Auto-invite workflows
- ✅ Basic conversion tracking (discount codes)
- ✅ 20,000+ profiles in library

**Team:** 2 backend, 2 frontend, 0.5 designer

**Metrics:**
- 20,000+ influencer profiles
- 100+ brand-influencer conversations
- 50+ contracts signed
- Auto-invites: 30% open rate, 10% apply rate

---

### 🗓️ Tháng 6: Booking Optimization + Payment Automation

#### Business Requirements:
- ✅ Influencer booking optimization
- ✅ Tối ưu luồng booking KOC

#### Impact.com Inspired Features:
- 🆕 Auto-payment calculation
- 🆕 Earnings dashboard (influencer)
- 🆕 Payment scheduling
- 🆕 MoMo/ZaloPay integration

#### Implementation:

**Week 1-2: Smart Booking System**
```
Booking Optimization:

1. AI-Powered Suggestions:
   - When brand creates campaign → Gemini suggests top 20 matches
   - Show estimated ROI per influencer (based on historical data)
   - Bulk invite top matches (1-click)

2. Booking Calendar:
   - Influencers set availability calendar
   - Brands see availability when booking
   - Avoid double-booking

3. Booking Analytics:
   - Acceptance rate per influencer
   - Time to accept (avg)
   - Success rate (completed campaigns)

UI Improvements:
- Drag & drop influencers to campaign
- Kanban board (pending, accepted, in-progress, completed)
- Bulk actions (invite all, message all)
```

**Week 2-3: Payment Engine**
```
Auto-Payment Calculation:

Commission Types:
1. Flat-fee: Fixed ₫5,000,000 per post
2. CPA: ₫50,000 per sale
3. CPS: 10% of sale value
4. Hybrid: ₫2,000,000 flat + ₫20,000 per sale

Calculation Logic:
- Read contract terms
- Fetch conversion data (from discount code tracking or manual input)
- Calculate earnings = flat_fee + (conversions × cpa_rate) + (sales_value × cps_rate)
- Deduct platform fee (10%)
- Show net earnings

Payment Scheduling:
- Weekly payout (every Friday)
- Monthly payout (1st of month)
- Per-campaign payout (after campaign ends)
- Minimum payout: ₫500,000 (prevent micro-transactions)

Payment Status:
- Pending (calculation done, waiting payout date)
- Processing (payment initiated)
- Paid (completed)
- Failed (retry)
```

**Week 3-4: Vietnam Payment Integration**
```
MoMo Integration:
- MoMo API for instant transfer
- QR code payment
- Transaction fee: 1%

ZaloPay Integration:
- ZaloPay API
- Instant payout
- Transaction fee: 1%

Bank Transfer:
- Manual bank transfer (for large amounts)
- ACH batch processing
- 1-2 days settlement

Earnings Dashboard (Influencer):
- Total earnings (all-time, this month)
- Pending payments
- Payment history
- Payout method settings
- Tax withholding (if applicable)
```

**Deliverables:**
- ✅ Smart booking system (AI suggestions)
- ✅ Booking calendar & analytics
- ✅ Auto-payment calculation engine
- ✅ Payment scheduling
- ✅ MoMo/ZaloPay integration
- ✅ Earnings dashboard

**Team:** 2 backend (payment), 1 frontend, 1 DevOps (payment gateway)

**Metrics:**
- Booking time reduced: 50% faster (AI suggestions)
- Payment accuracy: 100%
- Instant payout: <5 minutes (MoMo/ZaloPay)
- 200+ influencers paid

---

### 🗓️ Tháng 7: Booking Tự Động + Analytics Dashboard

#### Business Requirements:
- ✅ Influencer booking tự động

#### Impact.com Inspired Features:
- 🆕 Real-time analytics dashboard
- 🆕 Campaign performance reports
- 🆕 ROI calculator
- 🆕 Multi-touch attribution (basic)

#### Implementation:

**Week 1-2: Auto-Booking System**
```
Fully Automated Booking:

Auto-Matching Flow:
1. Brand creates campaign with criteria
2. AI matches top 50 influencers (Gemini)
3. System auto-invites top 20 (configurable)
4. Influencers accept/reject via email (1-click)
5. Auto-accept if influencer pre-approves criteria
6. Contract auto-generated & sent
7. Influencer signs → booking confirmed
8. Tracking link auto-generated
9. Campaign starts

Pre-Approval Settings (Influencer):
- Auto-accept campaigns matching: category, min budget, max workload
- Example: "Auto-accept Beauty campaigns with >₫3M budget"

Smart Scheduling:
- AI optimizes posting schedule (best time for engagement)
- Avoid conflicts (multiple campaigns same week)
- Balance workload (don't overbook influencers)
```

**Week 2-3: Analytics Dashboard**
```
Brand Dashboard:

Campaign Performance:
- Live stats: impressions, clicks, conversions, revenue
- Funnel visualization: impressions → clicks → conversions
- Top performing influencers (leaderboard)
- ROI calculator: revenue / cost = ROAS

Charts:
- Time series: daily impressions, clicks, conversions
- Bar chart: performance by influencer
- Pie chart: traffic sources (TikTok, Instagram, YouTube)
- Heatmap: engagement by time of day

Export Reports:
- CSV export (all data)
- PDF report (branded, shareable)
- Scheduled reports (email weekly)
```

**Week 3-4: Multi-Touch Attribution**
```
Attribution Models:

1. Last-Click (current):
   - Credit last influencer before purchase

2. First-Click (new):
   - Credit first influencer who introduced customer

3. Linear (new):
   - Split credit equally among all touchpoints
   Example: User clicked 3 influencer links → each gets 33.3% credit

4. Time-Decay (new):
   - More recent touchpoints get more credit
   Example: Link 1 (30 days ago) = 20%, Link 2 (7 days ago) = 80%

Implementation:
- Track user journey (cookie-based)
- Store all influencer touchpoints
- Calculate credit per model
- Allow brand to switch models in dashboard
```

**Deliverables:**
- ✅ Auto-booking system (end-to-end automation)
- ✅ Real-time analytics dashboard
- ✅ ROI calculator
- ✅ Multi-touch attribution (4 models)
- ✅ Report builder & exports

**Team:** 2 backend (attribution), 2 frontend (dashboard), 1 PM

**Metrics:**
- Auto-booking rate: 70% of campaigns
- Dashboard load time: <2s
- Attribution accuracy: 95%+
- 50+ campaigns with full analytics

---

### 🗓️ Tháng 8: Content Management System

#### Business Requirements:
- ✅ Các công cụ cho KOC bán hàng, làm content

#### Impact.com Inspired Features:
- 🆕 Content submission portal
- 🆕 Approval workflow
- 🆕 Asset library
- 🆕 Content performance tracking

#### Implementation:

**Week 1-2: Content Submission Portal**
```
Influencer Content Upload:
- Upload video (MP4, max 500MB)
- Upload images (JPG, PNG, max 10MB each)
- Submit social media post links (TikTok, Instagram, YouTube)
- Add caption/description
- Tag campaign

Content Metadata:
- Platform (TikTok, Instagram, YouTube, Facebook)
- Post type (video, image, carousel, story)
- Post date/time
- Public URL
- Performance data (views, likes, comments, shares)

Auto-Fetch Stats:
- If post URL provided → scrape stats automatically
- Update daily (views, engagement)
- Track growth over time
```

**Week 2-3: Approval Workflow**
```
Approval Process:

1. Influencer submits content (before or after posting)
2. Brand reviews content
3. Brand can:
   - Approve → payment triggered
   - Request changes → back to influencer
   - Reject → campaign cancelled (no payment)
4. Comments & feedback (inline comments on video/image)
5. Version history (if resubmitted)

Admin Review Dashboard:
- Queue of pending content
- Side-by-side: content + campaign brief
- Quick actions: approve, reject, comment
- Bulk approve (if multiple posts)

Notifications:
- Influencer: "Your content was approved!"
- Influencer: "Brand requested changes: [feedback]"
- Brand: "New content submitted by @influencer"
```

**Week 3-4: Asset Library & Content Tools**
```
Asset Library (Brand Side):
- Upload brand assets (logos, product images, guidelines)
- Share with influencers in campaign brief
- Download tracking (who downloaded what)

Content Templates:
- Pre-made caption templates
- Hashtag suggestions (trending, campaign-specific)
- Script templates (video scripts)

Content Performance:
- Track each post's performance (views, engagement, conversions)
- Compare: which post drove most sales?
- Best practices: learn from top-performing content

KOC Sales Tools:
- Affiliate link generator (for each post)
- QR code generator (for offline sharing)
- Bio link page (landing page with all campaign links)
- Example: bio.viewboost.vn/@nguyenvana
```

**Deliverables:**
- ✅ Content submission portal
- ✅ Approval workflow (review, comment, approve/reject)
- ✅ Asset library (brand assets)
- ✅ Content templates & tools
- ✅ Content performance tracking

**Team:** 2 frontend, 1 backend, 0.5 designer

**Metrics:**
- 500+ content pieces submitted
- 90%+ approval rate (within 24h)
- Content performance: track views, conversions per post

---

### 🗓️ Tháng 9: TikTok Shop Integration 🚀

#### Business Requirements:
- ✅ Các công cụ cho KOC bán hàng

#### Impact.com Inspired Features:
- 🆕 TikTok Shop API integration
- 🆕 Live-stream tracking
- 🆕 GMV tracking per influencer
- 🆕 TikTok-specific analytics

#### Implementation:

**Week 1-2: TikTok Shop API Integration**
```
TikTok Shop Setup:
- Apply for TikTok Shop Partner API access
- OAuth integration (brands connect TikTok Shop)
- Fetch product catalog
- Sync orders & sales data

Influencer TikTok Shop Flow:
1. Brand creates TikTok Shop campaign
2. Influencer applies
3. Brand approves → influencer gets affiliate link
4. Influencer promotes products in TikTok videos/live
5. Sales tracked automatically via TikTok Shop API
6. Earnings calculated based on GMV (Gross Merchandise Value)

Commission Structure:
- % of GMV (e.g., 10% of sales)
- Tiered: 0-100 sales = 5%, 100+ = 10%
- Bonus for hitting targets
```

**Week 2-3: Live-Stream Tracking**
```
TikTok Live-Stream Analytics:

Track Live Metrics:
- Concurrent viewers (peak, average)
- Total views
- Engagement (likes, comments, shares)
- Gifts/donations (TikTok coins)
- Product clicks during live
- Sales during live (GMV)

Live Dashboard (Real-Time):
- Brand can watch live stream performance
- See sales happening in real-time
- Top products sold during live
- Engagement spikes correlated with sales

Post-Live Report:
- Summary: total viewers, sales, GMV
- Timeline: sales peaks (which moments drove sales)
- Influencer performance grade (A-F)
```

**Week 3-4: TikTok-Specific Features**
```
TikTok Analytics:
- Video performance (views, watch time, completion rate)
- Product tag performance (clicks per tag)
- Audience demographics (age, gender, location)
- Trending sounds & hashtags used

TikTok Tools for KOCs:
- Best time to post (AI suggests optimal timing)
- Trending product recommendations
- Hashtag generator (trending + relevant)
- Video template library (proven formats)

TikTok Shop Dashboard:
- GMV leaderboard (top sellers)
- Product performance (best-selling products)
- Conversion rate (views → sales)
- Earnings forecast (projected monthly income)
```

**Deliverables:**
- ✅ TikTok Shop API integration
- ✅ Live-stream tracking & analytics
- ✅ GMV tracking per influencer
- ✅ TikTok-specific dashboard
- ✅ KOC tools (best time, hashtags, templates)

**Team:** 2 backend (TikTok API), 1 frontend

**Metrics:**
- 100+ TikTok Shop campaigns
- Track 1000+ products
- 50+ live-streams tracked
- GMV tracking: ₫500M+/month

---

### 🗓️ Tháng 10: Fraud Detection + Advanced Analytics

#### Business Requirements:
- ✅ Các công cụ cho KOC làm content

#### Impact.com Inspired Features:
- 🆕 Fraud detection (fake followers, bots)
- 🆕 ML fraud scoring
- 🆕 Admin moderation tools
- 🆕 Advanced analytics (cohort, LTV)

#### Implementation:

**Week 1-2: Fraud Detection System**
```
Fake Follower Detection:

Red Flags:
- Follower spike (gained 10K followers in 1 day)
- Low engagement vs followers (100K followers, 50 likes/post)
- Bot-like comments ("Nice post!", "🔥🔥🔥")
- Follower-to-following ratio (following 50K, 10K followers)

ML Model (Python):
- Train on known fake accounts
- Features: engagement rate, growth pattern, comment quality
- Output: Fraud risk score (0-100)

Actions:
- Score >70: Flag for review
- Score >90: Auto-reject
- Score <30: Trusted influencer (badge)

Admin Review:
- Review flagged profiles
- Manual approve/reject
- Whitelist trusted influencers
```

**Week 2-3: Click & Conversion Fraud**
```
Click Fraud Detection:

Suspicious Patterns:
- Same IP clicked 100 times
- Clicks from VPN/proxy
- Clicks but no conversions (ever)
- Clicks at unusual times (3am, all at once)

Bot Detection:
- Headless browser (no JavaScript)
- User agent spoofing
- Click velocity (10 clicks in 1 second)

Conversion Fraud:
- Same customer, multiple discount codes
- Returns (bought then returned)
- Fake orders (test credit cards)

Real-Time Blocking:
- Block suspicious IPs
- Require CAPTCHA for flagged users
- Delay payment until order confirmed (14 days)
```

**Week 3-4: Advanced Analytics**
```
Cohort Analysis:
- Group influencers by join date
- Track retention (still active after 3 months?)
- Track performance over time (improving or declining?)

Example Insight:
"Influencers who joined in Q1 2026 have 2x higher engagement than Q4 2025 cohort"

Customer LTV (Lifetime Value):
- Track customers acquired by influencer
- Measure repeat purchases
- Calculate LTV per influencer

Example:
Influencer A: acquired 100 customers, LTV ₫2,000,000 each → total value ₫200M
Influencer B: acquired 500 customers, LTV ₫500,000 each → total value ₫250M
→ Influencer B has higher total value despite lower LTV

Predictive Analytics:
- Forecast next month GMV per influencer
- Predict campaign success (before launch)
- Recommend budget allocation

Admin Moderation Dashboard:
- Fraud queue (flagged profiles)
- Content moderation (inappropriate content)
- User reports (brands/influencers report issues)
- Bulk actions (ban, suspend, verify)
```

**Deliverables:**
- ✅ Fraud detection (fake followers, click fraud)
- ✅ ML fraud scoring model
- ✅ Admin moderation dashboard
- ✅ Cohort analysis
- ✅ LTV tracking
- ✅ Predictive analytics

**Team:** 1 backend (fraud detection), 1 ML engineer, 1 frontend

**Metrics:**
- Fraud detection accuracy: >80%
- Caught 50+ fake profiles
- Prevented ₫10M+ fraud losses

---

### 🗓️ Tháng 11-12: Polish, Scale, Advanced Tools

#### Business Requirements:
- ✅ Các công cụ cho KOC bán hàng, làm content (continue)

#### Impact.com Inspired Features:
- 🆕 Mobile app (influencer)
- 🆕 Webhooks & API for integrations
- 🆕 White-label option (enterprise)
- 🆕 Advanced reporting

#### Implementation:

**Tháng 11: Mobile App + Webhooks**
```
Mobile App (React Native):

Features:
- Campaign browse & apply
- Push notifications (new campaign, payment received)
- Quick stats (earnings, clicks)
- Upload content from phone
- Chat with brands

Platform: iOS + Android

Webhook System:
- Brands can subscribe to events
- Events: new_application, content_submitted, campaign_completed, payment_processed
- POST to brand's URL with event data
- Retry logic (if webhook fails)

Example Use Case:
Brand has CRM → when influencer applies, auto-create lead in CRM
```

**Tháng 12: Scale & Enterprise Features**
```
Performance Optimization:
- Database indexing & query optimization
- CDN for assets (images, videos)
- Caching layer (Redis)
- Load balancing (handle 10K concurrent users)

White-Label (Enterprise):
- Custom domain (campaigns.techcombank.com.vn)
- Custom branding (logo, colors)
- Custom email templates
- Dedicated support

Advanced Reporting:
- Custom SQL query builder (for power users)
- Scheduled reports (daily, weekly, monthly)
- Data export to BI tools (Google Data Studio, Tableau)
- API for custom integrations

Security Audit:
- Penetration testing
- OWASP compliance
- Data encryption (at rest, in transit)
- GDPR compliance (data privacy)
```

**Deliverables:**
- ✅ Mobile app (iOS + Android)
- ✅ Webhook system
- ✅ White-label option
- ✅ Advanced reporting
- ✅ Performance optimization
- ✅ Security audit

**Team:** 1 mobile dev, 1 backend, 1 DevOps, 0.5 QA

**Metrics:**
- Mobile app: 1000+ downloads
- API uptime: 99.5%
- Page load: <2s (95th percentile)

---

## Feature Matrix: Business vs Impact.com

| Feature Category | Business Plan | Impact.com Requirement | Status |
|------------------|---------------|----------------------|--------|
| **Influencer Library** | ✅ 20K profiles, manual + bulk import | Public marketplace | ✅ Implemented (T2-5) |
| **Booking System** | ✅ Manual + auto booking | Campaign management | ✅ Implemented (T2, T6-7) |
| **Communication** | ✅ Chat, contracts | In-platform messaging | ✅ Implemented (T5) |
| **Tracking** | ❌ Not in business plan | ✅ Performance tracking (critical) | 🆕 Added (T2, T7) |
| **Payments** | ⚠️ Implicit (negotiate) | ✅ Automated payments | 🆕 Added (T6) |
| **Analytics** | ❌ Not in business plan | ✅ Real-time dashboard | 🆕 Added (T7, T10) |
| **AI Matching** | ⚠️ Implicit (filters) | ✅ AI-powered discovery | 🆕 Added (T4) |
| **Content Mgmt** | ✅ KOC tools | Content submission & approval | ✅ Implemented (T8) |
| **TikTok Shop** | ✅ Sales tools | TikTok Shop integration | ✅ Implemented (T9) |
| **Fraud Detection** | ❌ Not in business plan | ✅ Trust & safety | 🆕 Added (T10) |

---

## Impact.com Parity Assessment

| Module | Impact.com Feature | Ambassador Plan | Parity % |
|--------|-------------------|-------------|----------|
| **Influencer Discovery** | Marketplace, AI matching | ✅ T3-4 | **90%** ✅ |
| **Campaign Management** | Booking, workflows | ✅ T2, T6-7 | **90%** ✅ |
| **Content Management** | Upload, approval, library | ✅ T8 | **85%** ✅ |
| **Performance Tracking** | Links, attribution | ✅ T2, T7 | **85%** ✅ |
| **Payment & Compensation** | Auto-calc, MoMo/ZaloPay | ✅ T6 | **90%** ✅ |
| **Analytics & Reporting** | Dashboard, ROI, cohort | ✅ T7, T10 | **90%** ✅ |
| **Influencer Portal** | Marketplace, earnings | ✅ T3, T6 | **85%** ✅ |

**Overall Parity: ~88%** (Close to 90% target) ✅

---

## Team Summary

| Month | Backend | Frontend | ML/AI | Mobile | PM | Designer | DevOps | QA | Total FTE |
|-------|---------|----------|-------|--------|----|---------|---------|----|-----------|
| T2 | 2 | 2 | 0 | 0 | 1 | 0 | 1 | 0 | 6 |
| T3 | 1 | 2 | 0 | 0 | 1 | 0.5 | 0 | 0 | 4.5 |
| T4 | 2 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 4 |
| T5 | 2 | 2 | 0 | 0 | 1 | 0.5 | 0 | 0 | 5.5 |
| T6 | 2 | 1 | 0 | 0 | 1 | 0 | 1 | 0 | 5 |
| T7 | 2 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 5 |
| T8 | 1 | 2 | 0 | 0 | 1 | 0.5 | 0 | 0 | 4.5 |
| T9 | 2 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 4 |
| T10 | 1 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 4 |
| T11 | 1 | 1 | 0 | 1 | 1 | 0 | 1 | 0 | 5 |
| T12 | 1 | 0 | 0 | 1 | 1 | 0 | 1 | 0.5 | 4.5 |

**Average: 7 FTE**

---

## Success Metrics

### Month 6 Gate:
- ✅ 10,000+ influencer profiles
- ✅ 50+ active campaigns
- ✅ Auto-booking working
- ✅ Payment automation live
- ✅ 20+ paying customers

### Month 12 Gate (90% Parity):
- ✅ 20,000+ influencer profiles
- ✅ 200+ campaigns completed
- ✅ TikTok Shop tracking live
- ✅ ₫500M+ GMV tracked
- ✅ 100+ paying customers
- ✅ 99.5% API uptime
- ✅ Mobile app launched
- ✅ **88-90% Impact.com parity achieved** ✅

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **20K KOC growth target** | Bulk onboarding tools (T4), referral program, partnerships with influencer agencies |
| **TikTok API restrictions** | Apply for partner access early (T7), fallback to manual tracking |
| **Payment fraud** | Fraud detection (T10), 14-day hold period, manual review for large amounts |
| **Performance at scale** | Optimization in T12, load testing, CDN, caching |
| **Business plan changes** | Agile approach, monthly check-ins, adjust roadmap as needed |

---

## Next Steps

### Week 1: Alignment
- [ ] Review merged roadmap with business team
- [ ] Confirm: Does this meet both business goals + Impact.com parity?
- [ ] Adjust priorities if needed

### Week 2-4: Sprint 1 Prep
- [ ] Finalize Month 2 scope (Dashboard + Library + Tracking)
- [ ] Hire 2 backend, 2 frontend engineers
- [ ] Setup infrastructure (AWS, MongoDB, Elasticsearch)
- [ ] Create Sprint 1 tickets

### Month 2: Execute & Validate
- [ ] Build admin dashboard + library
- [ ] Implement booking system
- [ ] Add discount code system
- [ ] Onboard 100 influencers (manual)
- [ ] Launch 5 pilot campaigns

---

**Key Insight:** Ambassador roadmap satisfies both:
1. ✅ Business requirements (library-first, 20K growth, booking automation)
2. ✅ Impact.com parity (tracking, analytics, automation, 88-90%)

**Timeline:**
- 11 months (vs 10 months influencer-only)
- **Benefit:** Achieves business goals + competitive feature parity

---

*Created: 2026-02-05*
*Version: 1.0 - Business Plan with Impact.com Benchmark Analysis*
