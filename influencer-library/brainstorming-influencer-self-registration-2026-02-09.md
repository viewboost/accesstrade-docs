# Brainstorming Session: Influencer Self-Service Registration & Profile Enrichment

**Date:** 2026-02-09
**Objective:** Thiết kế flow cho influencer tự đăng ký và làm giàu profile data thông qua forms/questionnaires
**Context:** AT Core và TCB đang được develop, cần thêm tính năng cho influencers tự submit profile + enrichment data

---

## Executive Summary

**Problem:** Làm sao để influencers tự đăng ký, submit profile, và enrichment data một cách hiệu quả, đồng thời maintain data quality và sync giữa TCB và AT Core?

**Recommendation:** **Tiered Progressive Registration** với 3 levels (Quick → Standard → Premium), kết hợp automatic approval rules và post-approval Creator Portal.

**Key Insight:** Registration không phải endpoint, mà là starting point của long-term relationship với influencers.

**Data Flow:**
```
Influencer → TCB (full enrichment) → AT Core (simplified profile) → TCB (reference)
           Submit              If "Share to AT Pool"            atProfileId
```

---

## Techniques Used

1. **Starbursting** - Đặt câu hỏi Who/What/Where/When/Why/How để explore requirements
2. **Mind Mapping** - Visualize feature hierarchy, data models, flows
3. **SCAMPER** - Creative variations (Substitute, Combine, Adapt, Modify, Put to other uses, Eliminate, Reverse)

---

## Ideas Generated (51 Total)

### Category 1: Registration Flow & UX (13 ideas)

**Multi-step Wizard (Recommended)**
- 5-step progressive flow: Social → Demographics → Content → Collab → Review
- Progress bar (Step 1/5), save draft feature
- Mobile-optimized, responsive design

**Tiered Registration (HIGH IMPACT)**
```
Tier 1: QUICK REGISTER (2 minutes)
- Social URL + Name/Email/Phone
- Status: BASIC
- Can be approved fast, limited visibility

Tier 2: STANDARD REGISTER (6 minutes)
- + Demographics, Content info
- Status: VERIFIED
- Access to normal campaigns

Tier 3: PREMIUM REGISTER (15 minutes)
- + Full enrichment, portfolio, rate card
- Status: PREMIUM
- Exclusive campaigns, priority matching
```

**Social OAuth Integration**
- Login with TikTok/Instagram/YouTube
- Auto-fetch profile data
- 1-click registration
- Challenge: Need API approvals (2-3 months)

**Dynamic Forms**
- Conditional questions based on previous answers
- Example: If category = "Beauty" → Show "Do you do makeup tutorials?"
- Reduce cognitive load, show relevant fields only

**Conversational Bot Interface**
- Chat-like experience vs long form
- Bot asks 10 key questions
- More engaging, feels less like work

**Video Introduction**
- 30-second video vs written bio
- Show personality, voice, presentation style
- Harder to fake, differentiation factor

**Progress Gamification**
- "60% to go!", "Unlock priority review at 90%"
- Incentives per step
- Reduce drop-off rate

**LinkedIn-style Profile Structure**
- Headline: "Beauty & Lifestyle Creator | 250K TikTok"
- About, Experience (Brand Collabs), Skills
- Familiar structure, professional

**Draft Save Feature**
- Auto-save every 30s
- Resume anytime
- Expire after 30 days

**Mobile-First Design**
- Most influencers register on mobile
- Large tap targets, minimal typing
- Photo upload from camera roll

---

### Category 2: Data Enrichment (8 ideas)

**Enrichment Questionnaire Structure**
```
Step 2: Demographics (Required)
- Gender (radio)
- Age range (dropdown: 18-24, 25-34, 35-44, 45+)
- City/Location (autocomplete)
- Primary language (dropdown)

Step 3: Content Information (Required)
- Primary category (dropdown with icons)
  Options: Beauty, Tech, Lifestyle, Food, Travel, Gaming, Fashion, Fitness, Parenting, Education
- Secondary categories (multi-select, max 2)
- Content style (checkboxes)
  Options: Educational, Entertainment, Product Reviews, Lifestyle Vlogs, Tutorials, Behind-the-scenes
- Target audience demographics
  - Age range (checkboxes)
  - Gender (Male/Female/Both)
  - Interests (multi-select)
- Content frequency (slider)
  Options: 1-2/week, 3-5/week, Daily, Multiple/day

Step 4: Collaboration Information (Optional but encouraged)
- Previous brand collaborations (textarea, max 500 chars)
  Example: "Worked with L'Oreal, Maybelline, MAC Cosmetics"
- Preferred collaboration types (checkboxes)
  Options: Sponsored posts, Video reviews, Instagram stories, Live streams, Long-term ambassadorships
- Rate card (range selectors)
  - Per TikTok video: $50-$100, $100-$500, $500-$1000, $1000+
  - Per Instagram post: Similar ranges
  - Per YouTube video: Similar ranges
  - Per campaign (multiple posts): Similar ranges
- Sample work links (URL inputs, up to 5)
  Hint: "Paste links to your best performing content"
- Media kit upload (PDF, max 5MB)
  Hint: "Optional: Upload your media kit for faster review"

Step 5: Additional Information (Optional)
- Bio/Description (textarea, max 500 chars)
- Specializations (free text tags, max 5)
  Example: "Makeup tutorials, Product unboxing, Travel vlogs"
- Awards/Recognition (textarea)
- Why do you want to collaborate with brands? (textarea, max 250 chars)
```

**AI-Generated Suggestions (Phase 2)**
- Analyze recent 20 posts from social profile
- Extract: demographics (comments, followers), topics (hashtags)
- Suggest: "Your audience is 18-25 females interested in beauty, fashion"
- Influencer confirms or edits
- Result: 50% less time to complete

**Portfolio Builder Integration**
- Select best 5 posts/videos during registration
- Add description for each ("Why this is my best work")
- Showcase engagement stats
- Generate shareable portfolio URL: creator.techcombank.com/@username

**Skill Assessment Quiz (Optional)**
- "What's a good engagement rate for TikTok?" (educate + filter)
- "Have you disclosed sponsored content before?" (compliance check)
- "What brands align with your values?" (match quality)
- Optional section, +10% profile completeness

**Rich Media Upload**
- Profile photo (if different from social)
- Cover image (banner for profile page)
- Portfolio samples (images/videos, max 3, 50MB total)

---

### Category 3: Validation & Quality (7 ideas)

**Pre-submit Validation**
```
Required field checks:
✅ Social URL valid format (matches TikTok/IG/YouTube/FB pattern)
✅ Email valid + verified (6-digit code sent)
✅ Phone valid (optional SMS verification)
✅ Primary category selected
✅ Terms & Conditions accepted

Data quality checks:
⚠️ Rate card reasonable (flag if > $10,000/post)
⚠️ Sample work URLs accessible (test each link)
⚠️ Bio not spam (keyword detection)
```

**Quality Gates (Automatic)**
```
After social profile crawled:
❌ REJECT if:
   - Followers < 5,000 (too small)
   - Engagement < 1% (inactive audience)
   - Score < 40 (poor quality, from VB)
   - Account age < 3 months (too new)
   - Fake/bot detection flags (from VB)

⚠️ MANUAL REVIEW if:
   - Followers 5K-100K (moderate size)
   - Score 40-80 (middle range)
   - Profile completeness 60-89%

✅ AUTO-APPROVE if:
   - Followers > 100K (established)
   - Score > 80 (excellent, from VB)
   - Profile completeness > 90%
   - Previous brand collabs documented
```

**Duplicate Detection**
- Check existing influencers by social URL
- Check by email/phone
- Prevent re-submission within 30 days if rejected

**Email Verification Flow**
- After Step 1, send 6-digit code to email
- Influencer enters code
- Email confirmed, proceed to Step 2

**Phone Verification (Optional)**
- SMS code for additional trust signal
- Optional (not required) to reduce friction
- Useful for high-value influencers (Tier 3)

**Spam/Abuse Prevention**
- Rate limit: Max 3 submissions per IP per day
- CAPTCHA on submit
- Flag suspicious patterns (same name, different URLs)

**Content Moderation**
- Check for inappropriate content in recent posts (via VB API)
- Flag: Violence, adult content, hate speech
- Auto-reject or manual review based on severity

---

### Category 4: Approval Workflow (6 ideas)

**3-Tier Approval System**
```
TIER 1: AUTO-APPROVE (Instant) - ~15% of submissions
Criteria:
✅ Score > 80 (from VB)
✅ Followers > 100,000
✅ Profile completeness > 90%
✅ Previous brand collaborations documented
✅ All quality gates passed

Action:
- Status: APPROVED_AUTO
- Email: "Congratulations! Your profile is live."
- Redirect to Creator Portal

TIER 2: MANUAL REVIEW (48h SLA) - ~70% of submissions
Criteria:
⚠️ Score 40-80 (middle range)
⚠️ Followers 5K-100K (moderate)
⚠️ Needs human judgment for brand fit

TCB Reviewer Dashboard:
- View profile summary
- Watch sample content (if video links provided)
- Check brand alignment (Does content fit TCB brand values?)
- Rate: Good fit / Neutral / Poor fit
- Approve/Reject with notes

Action:
- If approved: Email notification, status APPROVED_MANUAL
- If rejected: Email with reason + "Reapply in 30 days"

TIER 3: AUTO-REJECT (Instant) - ~15% of submissions
Criteria:
❌ Score < 40 (poor quality)
❌ Followers < 5,000 (too small)
❌ Fake/bot flags detected
❌ Duplicate submission within 30 days
❌ Content moderation flags

Action:
- Status: REJECTED_AUTO
- Email: "Thank you for applying. Unfortunately..."
  - Clear rejection reason
  - Improvement suggestions
  - Reapply timeline (30 days or 90 days)
```

**Reviewer Dashboard Features**
- Queue view: List pending submissions
- Filters: Category, score range, follower range
- Sort: Submission date, score, followers
- Bulk actions: Approve selected, Reject selected
- Reviewer notes (internal, not visible to influencer)
- Review history (track reviewer decisions)

**SLA Monitoring**
- 48h SLA for manual reviews
- Alert if review queue > 50 submissions
- Daily digest email to reviewers

**Appeal Process**
- Rejected influencers can appeal (within 7 days)
- Appeals go to senior reviewer
- Influencer can update profile before appeal

**Review Analytics**
- Approval rate by reviewer
- Average review time
- Rejection reasons breakdown
- Quality of approved influencers (post-campaign performance)

**AT Pool Approval (If "Share to AT Pool" enabled)**
- After TCB approval → Call AT API
- AT Admin reviews (higher quality bar)
- AT approves → Visibility: PUBLIC in AT Pool
- AT rejects → Influencer stays in TCB only, not shared

---

### Category 5: Data Storage & Sync (5 ideas)

**Dual Storage Strategy (CRITICAL)**
```
TCB DATABASE (Full Ownership):
Table: influencer_submissions
- id (UUID)
- status (DRAFT/PENDING/APPROVED/REJECTED)
- socialProfiles (JSON array)
  [
    { platform: "tiktok", username: "@beauty_guru", url: "...", followers: 250000 }
  ]
- demographics (JSON)
  { gender: "female", ageRange: "25-34", city: "Ho Chi Minh", language: "vi" }
- contentInfo (JSON)
  { primaryCategory: "beauty", secondaryCategories: ["fashion", "lifestyle"], ... }
- collabInfo (JSON)
  { previousCollabs: "...", preferredTypes: [...], rateCard: {...}, sampleWork: [...] }
- enrichmentData (JSON) - All questionnaire responses
- crawledData (JSON) - Data from VB API (followers, engagement, score)
- atPoolStatus (ENUM: NOT_SYNCED, PENDING, SYNCED, REJECTED)
- atProfileId (UUID, nullable) - Reference to AT Pool profile
- tcbFields (JSON) - Tags, notes, campaigns participated
- createdAt, submittedAt, reviewedAt, approvedAt

AT CORE DATABASE (Simplified, Platform-level):
Table: pool_influencers
- id (UUID)
- vbProfileId (UUID) - ViewBoost profile ID
- platform, username, displayName, avatarUrl
- followers, engagement, score
- category, tier
- visibility (PUBLIC/PRIVATE)
- source (PARTNER_SUBMISSION)
- partnerUserId (TCB influencer ID) - CRITICAL for linking
- approvalStatus (PENDING/APPROVED/REJECTED)
- approvalReviewedBy, approvalReviewedAt
- syncedAt, syncStatus
```

**Data Flow Architecture**
```
Step 1: Influencer submits registration
        ↓
Step 2: TCB validates data
        ↓
Step 3: TCB calls VB API to crawl social profile
        - VB returns: followers, engagement, score, metrics
        ↓
Step 4: TCB saves FULL profile to TCB DB (status: PENDING_APPROVAL)
        - All enrichment data
        - Crawled social metrics
        - Questionnaire responses
        ↓
Step 5: TCB approval workflow
        - Auto-approve, Manual review, or Auto-reject
        - If approved: status = APPROVED
        ↓
Step 6: If "Share to AT Pool" checkbox enabled:
        - TCB calls AT Core API: POST /api/v1/partners/pool/submit
        - Body: {
            url: "https://tiktok.com/@beauty_guru",
            partnerUserId: "tcb_inf_123", // TCB influencer ID
            category: "beauty",
            tier: "premium",
            visibility: "PUBLIC"
          }
        ↓
Step 7: AT Core saves SIMPLIFIED profile to AT Pool DB
        - Platform-level data only (no enrichment)
        - approvalStatus: PENDING_APPROVAL
        - Links: partnerUserId → TCB influencer ID
        ↓
Step 8: AT Admin reviews (if needed)
        - Approve → visibility: PUBLIC, AT Pool active
        - Reject → webhook callback to TCB
        ↓
Step 9: Webhook callback to TCB
        - TCB updates: atPoolStatus = SYNCED, atProfileId = "at_prof_456"
        - Or: atPoolStatus = REJECTED (if AT rejected)
```

**Sync Strategy**
```
Daily Sync (TCB Sync Service):
- For influencers with atPoolStatus = SYNCED
- Call AT API: POST /api/v1/profiles/batch-refresh
- Update: followers, engagement, score (social metrics)
- TCB DB updated with latest metrics

Manual Update (Influencer-initiated):
- Influencer updates enrichment data (rate card, bio, portfolio)
- Saved to TCB DB only (enrichment not synced to AT)
- Monthly limit: Max 1 update per month

Re-approval Trigger:
- If influencer adds new social account → Re-review required
- Major changes (category change) → Flag for review
```

**Data Ownership Clarity**
```
AT Pool owns:
- Platform-level data (username, followers, score)
- Data crawled from VB API
- Visibility control (PUBLIC/PRIVATE)
- Source tracking

TCB owns:
- Enrichment data (demographics, rate card, portfolio)
- TCB-specific fields (tags, notes, campaigns)
- Full submission history
- Approval decisions (TCB level)

No duplication:
- TCB doesn't store score calculation (comes from AT)
- AT doesn't store rate card (stays in TCB)
```

**API Endpoints**
```
TCB API (Internal):
POST   /api/v1/influencers/register        # Submit registration
GET    /api/v1/influencers/draft/:id       # Get draft
PATCH  /api/v1/influencers/draft/:id       # Update draft
POST   /api/v1/influencers/submit/:id      # Submit for review
GET    /api/v1/influencers/status/:id      # Check status

TCB Admin API:
GET    /api/v1/admin/submissions           # List pending submissions
POST   /api/v1/admin/submissions/:id/approve
POST   /api/v1/admin/submissions/:id/reject

AT Core API (External, called by TCB):
POST   /api/v1/partners/pool/submit        # Submit influencer to AT Pool
GET    /api/v1/partners/pool/submissions/:id # Check AT approval status

Webhooks (AT → TCB):
POST   /api/v1/webhooks/at-approval        # AT approval/rejection callback
```

---

### Category 6: Post-Approval Features (6 ideas)

**Creator Portal Architecture**
```
Dashboard:
├─ Welcome message: "Hi @beauty_guru! Your profile is 85% complete"
├─ Profile completeness progress bar
├─ Quick stats: Profile views, Campaign invitations
├─ Notifications: New campaign matches, Profile update reminders
└─ Call-to-action: "Complete your profile to unlock premium campaigns"

Profile Management:
├─ View Profile (as brands see it)
│   - Preview mode
│   - Public profile URL: creator.techcombank.com/@beauty_guru
│
├─ Edit Profile
│   ├─ Social accounts (add new, triggers re-review)
│   ├─ Demographics (update annually)
│   ├─ Content info (update monthly)
│   ├─ Rate card (update quarterly)
│   └─ Portfolio (upload new samples anytime)
│
├─ Profile Completeness Checklist
│   ✅ Social profile connected
│   ✅ Demographics filled
│   ✅ Rate card provided
│   ⚠️ Media kit missing (+15% completeness)
│   ⚠️ Video intro missing (+10% completeness)
│
└─ Settings
    - Email preferences
    - Privacy settings
    - "Share to AT Pool" toggle

Campaign Center (Phase 2):
├─ Browse Campaigns
│   ├─ Open campaigns list
│   ├─ Filter by category, budget, duration
│   ├─ Sort by deadline, budget
│   └─ "Apply" button
│
├─ My Applications
│   ├─ Pending (waiting for brand response)
│   ├─ Accepted (campaign details)
│   ├─ Rejected (feedback from brand)
│   └─ Completed (past collaborations)
│
└─ Collaboration History
    - List of past campaigns
    - Brands worked with
    - Total earnings
    - Performance ratings

Analytics & Insights (Phase 3):
├─ Profile Performance
│   - Profile views (last 30 days)
│   - Profile views by brands
│   - Top performing content (from portfolio)
│
├─ Campaign Performance
│   - Campaigns completed
│   - Average rating from brands
│   - Earnings trends
│
└─ Growth Tips
    - "Influencers with video intros get 3x more invites"
    - "Complete your media kit to increase profile views"
    - "Update your portfolio monthly for best results"
```

**Brand Matching Algorithm (Phase 2)**
```
Match Score Calculation:
├─ Category overlap (40% weight)
│   - Exact match: 100 points
│   - Secondary match: 50 points
│
├─ Audience alignment (30% weight)
│   - Age match: 40 points
│   - Gender match: 30 points
│   - Location match: 30 points
│
├─ Budget fit (20% weight)
│   - Influencer rate within campaign budget: 100 points
│   - Slightly above: 50 points
│
└─ Content style (10% weight)
    - Style matches campaign needs: 100 points

Output:
"You're 85% match for TCB Beauty Campaign"
- Category: Beauty ✅ (100%)
- Audience: 18-25 females ✅ (90%)
- Budget: $500/post ✅ (fits budget)
- Style: Product reviews ✅

Call-to-action: "Apply Now"
```

**Notification System**
```
Email notifications:
- Registration confirmed
- Profile approved/rejected
- New campaign match (85%+)
- Campaign invitation from brand
- Profile completeness reminder (weekly if <80%)
- Monthly performance report

In-app notifications:
- New campaign posted
- Application status update
- Profile viewed by brand
- Message from brand
```

**Profile Analytics**
```
Metrics tracked:
- Profile views (total, last 7/30/90 days)
- Profile views by brands (which brands viewed)
- Application conversion rate
- Campaign acceptance rate
- Average response time
- Profile completeness score

Benchmarking:
- "Your profile views are 25% above average for Beauty influencers"
- "Influencers with 90%+ completeness get 2x more invitations"
```

**Gamification Elements**
```
Achievements:
✅ "Quick Starter" - Completed registration in <5 minutes
✅ "Completionist" - 100% profile completeness
✅ "Rising Star" - 10,000+ profile views
✅ "Brand Favorite" - 5+ successful campaigns
✅ "Portfolio Master" - Uploaded 10+ portfolio samples

Badges display on profile (visible to brands)

Leaderboards (optional):
- Top viewed profiles (this month)
- Top earning influencers (this quarter)
- Most campaigns completed
```

**Referral Program (Phase 3)**
```
"Invite fellow creators, earn rewards"
- Each influencer gets unique referral link
- Referred influencer signs up + gets approved → Referrer earns points
- Points can be redeemed for:
  - Priority review (skip queue)
  - Featured profile (highlighted to brands)
  - Premium support

Viral loop:
More influencers → More campaigns → More influencers
```

---

### Category 7: Alternative Approaches (7 ideas)

**Approach 1: Reverse Flow - Brand Invites First**
```
Instead of: Influencer applies → Wait approval → Maybe get campaign

Reverse flow:
1. TCB scouts influencers (via VB search or social media)
2. TCB sends email invite: "We'd love to work with you!"
   - Unique registration link (pre-filled data)
   - Influencer status: INVITED
3. Influencer registers (fast-track, simplified form)
   - Basic info already filled (from social profile)
   - Influencer confirms + adds enrichment
4. Auto-approved (since curated)
5. Immediate campaign invitation

Benefits:
✅ Higher quality (curated, not random applicants)
✅ Influencer more motivated (invited vs cold apply)
✅ Faster conversion (pre-vetted)
✅ Better brand fit (TCB already screened)

Use case: Premium influencers (100K+ followers)
```

**Approach 2: Enrichment AFTER Approval**
```
Instead of: Full enrichment before approval

Staged flow:
Stage 1: Quick Registration (2 min)
- Social URL + Email + Phone
- Submit → Auto-crawl → Fast approval (24h)

Stage 2: Post-Approval Enrichment
- Email: "Welcome! Complete your profile to unlock campaigns"
- Influencer logs in to Creator Portal
- Fills enrichment data (demographics, rate card, portfolio)
- Profile completeness: 40% → 100%

Benefits:
✅ Lower barrier to entry (2-min registration)
✅ Faster approval (less data to review)
✅ Influencer more motivated post-approval

Trade-off:
❌ Less data for initial matching
❌ Influencer might not complete enrichment
```

**Approach 3: Mutual Opt-in (Brand & Influencer)**
```
Instead of: Only brand approves influencer

Mutual approval:
1. Influencer registers
2. Reviews TCB brand profile:
   - Brand values: "Sustainability, Innovation, Quality"
   - Past campaigns: Beauty, Tech, Lifestyle
   - Collaboration style: Long-term partnerships
3. Checkbox: "I'm interested in TCB collaborations"
4. TCB reviews interested influencers only

Benefits:
✅ Better culture fit (influencer already aligned with brand)
✅ Higher engagement (willing participants)
✅ Reduced rejection rate (self-filtering)

Implementation:
- TCB brand profile page (public)
- Influencer reviews before registering
- "Apply to TCB" button (after review)
```

**Approach 4: Registration as Lead Gen for Creator Academy**
```
After registration:
"Want to improve your content?"
- Join TCB Creator Academy (free courses)
- Weekly webinars with top influencers
- Resource library (templates, guides)

Monetization:
- Free tier: Basic courses
- Premium tier ($99/year): Advanced courses, 1-on-1 coaching

Benefits:
✅ Additional revenue stream
✅ Higher engagement (influencers return for courses)
✅ Brand loyalty (TCB invests in influencer growth)
✅ Better content quality (educated influencers)
```

**Approach 5: Data for Market Research**
```
Aggregate registration data for insights:
- Influencer market trends report
  - "Beauty influencers in Vietnam: 45% increase in 2026"
  - "Average rate for TikTok video: $250 (up 15% YoY)"
- Category saturation analysis
  - "Gaming category: High competition, 500 influencers"
  - "Parenting category: Low competition, 50 influencers"
- Rate card benchmarking
  - "Your rate is 20% above market average"

Output:
- TCB Marketing Insights Dashboard
- Public report (attract more influencers)
```

**Approach 6: White-label Solution for Other Brands**
```
If TCB registration system works well:
- Package as white-label product
- Sell to other brands (Vinfast, Samsung, etc.)
- Revenue model: $5K setup + $500/month per brand

Benefits:
✅ Monetize investment in registration system
✅ Scale AT Partner Network faster
✅ Standardized registration across brands
```

**Approach 7: Blockchain-based Verified Credentials**
```
Phase 3 idea (future):
- Influencer profile → NFT-based credential
- Verified on-chain (followers, engagement, past collabs)
- Portable across platforms (TCB, AT Partners, OpenSea)

Benefits:
✅ Tamper-proof reputation
✅ Portable identity (use across brands)
✅ Innovative differentiator

Challenge: Complexity, blockchain adoption
```

---

### Category 8: Technical Implementation (5 ideas)

**Async Crawl Processing (CRITICAL)**
```
Flow:
1. Influencer submits social URL
2. TCB API validates URL format
3. Queue job: "Crawl social profile"
   - Job ID: job_abc123
   - Status: QUEUED
4. Respond immediately: "Thank you! We're processing..."
5. Background worker picks up job
6. Call VB API: GET /profiles/enrich
   - May take 10-30 seconds
7. VB returns: followers, engagement, score
8. Save to TCB DB: crawledData field
9. Email notification: "Your profile is ready for review"

Benefits:
✅ Non-blocking (influencer doesn't wait)
✅ Scalable (handle 100+ concurrent submissions)
✅ Resilient (retry failed crawls)

Implementation:
- Redis queue (Bull/BullMQ)
- Background workers (separate process)
- Webhook callback (optional, for immediate notification)
```

**Social OAuth Setup (Phase 2)**
```
APIs needed:
├─ TikTok Business API
│   - Approval: 4-6 weeks
│   - OAuth scopes: user.info.basic, video.list
│   - Rate limit: 100 req/min
│
├─ Instagram Graph API
│   - Approval: 2-4 weeks (if business account)
│   - OAuth scopes: instagram_basic, instagram_manage_insights
│   - Rate limit: 200 req/hour
│
├─ YouTube Data API v3
│   - Approval: Instant (Google Cloud project)
│   - OAuth scopes: youtube.readonly
│   - Rate limit: 10,000 units/day
│
└─ Facebook Graph API
    - Approval: 1-2 weeks
    - OAuth scopes: pages_show_list, pages_read_engagement
    - Rate limit: 200 req/hour

Implementation:
- NextAuth.js for OAuth flows
- Store: accessToken, refreshToken (encrypted)
- Auto-refresh tokens before expiry
```

**Video Upload Infrastructure (Phase 2)**
```
Technical requirements:
├─ File upload
│   - Max size: 50MB
│   - Allowed formats: MP4, MOV, AVI
│   - Validation: Check duration (max 60 seconds)
│
├─ Storage
│   - AWS S3 or Cloudflare R2
│   - Bucket: tcb-creator-videos
│   - CDN: CloudFront for fast playback
│
├─ Processing
│   - FFmpeg: Convert to web-optimized format (H.264)
│   - Generate thumbnail (frame at 2 seconds)
│   - Compress if > 20MB
│
└─ Transcription (optional)
    - AWS Transcribe or Deepgram
    - Auto-generate captions
    - Make video searchable

Implementation:
- Presigned URL upload (direct to S3)
- Lambda function for processing
- Queue job for transcription
```

**Webhook Integration**
```
Webhooks needed:
├─ VB Crawl Complete
│   - Endpoint: POST /api/v1/webhooks/vb-crawl-complete
│   - Body: { jobId, status, profileData }
│   - Validation: HMAC signature
│
├─ AT Approval Callback
│   - Endpoint: POST /api/v1/webhooks/at-approval
│   - Body: { submissionId, status: "APPROVED/REJECTED", atProfileId }
│   - Update TCB DB: atPoolStatus
│
└─ Email Delivery Status
    - SendGrid webhook
    - Track: Delivered, Opened, Clicked

Security:
- HMAC signature validation
- IP whitelist (if possible)
- Replay attack prevention (timestamp check)
- Idempotency (handle duplicate webhooks)
```

**Database Schema (TCB)**
```sql
-- Influencer Submissions (Main table)
CREATE TABLE influencer_submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  status VARCHAR(50) NOT NULL, -- DRAFT, PENDING, APPROVED, REJECTED

  -- Social profiles (JSON array)
  social_profiles JSONB NOT NULL,

  -- Demographics (JSON)
  demographics JSONB,

  -- Content info (JSON)
  content_info JSONB,

  -- Collaboration info (JSON)
  collab_info JSONB,

  -- Enrichment data (all questionnaire responses)
  enrichment_data JSONB,

  -- Crawled data from VB API
  crawled_data JSONB,

  -- AT Pool sync
  at_pool_status VARCHAR(50) DEFAULT 'NOT_SYNCED', -- NOT_SYNCED, PENDING, SYNCED, REJECTED
  at_profile_id UUID, -- Reference to AT Pool profile

  -- TCB-specific
  tcb_tags TEXT[],
  tcb_notes TEXT,

  -- Approval tracking
  reviewed_by UUID, -- Admin user ID
  reviewed_at TIMESTAMP,
  rejection_reason TEXT,

  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  submitted_at TIMESTAMP,
  approved_at TIMESTAMP,

  -- Indexes
  INDEX idx_status (status),
  INDEX idx_at_pool_status (at_pool_status),
  INDEX idx_created_at (created_at),
  INDEX idx_social_profiles ((social_profiles->>'platform'))
);

-- Draft save (for resume functionality)
CREATE TABLE registration_drafts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id VARCHAR(255), -- Browser session or user ID
  draft_data JSONB, -- Partial submission data
  step_completed INT DEFAULT 1, -- Last completed step (1-5)
  expires_at TIMESTAMP, -- 30 days from last update
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Approval queue (for reviewer workflow)
CREATE TABLE approval_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  submission_id UUID REFERENCES influencer_submissions(id),
  priority INT DEFAULT 0, -- Higher = higher priority
  assigned_to UUID, -- Reviewer user ID
  assigned_at TIMESTAMP,

  INDEX idx_priority (priority DESC),
  INDEX idx_assigned_to (assigned_to)
);
```

---

## Key Insights

### Insight 1: Tiered Progressive Registration là Optimal UX
**Source:** Starbursting (How), Mind Mapping, SCAMPER (Modify)
**Impact:** HIGH
**Effort:** MEDIUM

**Description:**
Thay vì single long form, sử dụng **3-tier registration**:
- Tier 1: QUICK (2min) - Social + Contact
- Tier 2: STANDARD (6min) - + Demographics, Content info
- Tier 3: PREMIUM (15min) - + Full enrichment

**Benefits:**
- Lower barrier to entry (2-min quick form)
- Higher completion rate (~70% vs 20% for long form)
- Progressive value (approved Tier 1, incentivized to complete more)
- Flexibility (campaigns can require tier levels)

**Implementation:** 5-step wizard, progress bar, save draft, mobile-optimized

---

### Insight 2: Social OAuth > Manual URL Input
**Source:** SCAMPER (Substitute), Starbursting (How)
**Impact:** HIGH
**Effort:** HIGH (API approvals 2-3 months)

**Description:**
Login with TikTok/Instagram/YouTube > typing URL manually

**Benefits:**
- Verified identity (no fake URLs)
- 1-click registration (faster)
- Auto-populated data (accurate)
- 30-50% higher completion rate

**Challenge:** Need API approvals (2-3 months)

**Recommendation:** Launch MVP with manual URL, add OAuth in Phase 2

---

### Insight 3: Dual Storage Strategy Cần Định Nghĩa Rõ
**Source:** All techniques, Mind Mapping (Data Models)
**Impact:** CRITICAL
**Effort:** MEDIUM

**Description:**
AT Pool và TCB lưu **complementary data**, không duplicate:

```
AT POOL: Platform-level data
- Social metrics (followers, engagement, score)
- Visibility (PUBLIC/PRIVATE)
- Source tracking

TCB: Enrichment + TCB-specific
- Demographics, rate card, portfolio
- TCB campaigns, tags, notes
- Full submission history
```

**Data flow:**
```
Influencer → TCB (full) → AT Core (simplified) → TCB (reference)
```

**Why it matters:**
- Clarity on ownership (AT owns platform data, TCB owns enrichment)
- No duplication (metrics from AT, enrichment from TCB)
- Sync strategy (social metrics sync daily, enrichment stays TCB)

---

### Insight 4: Automatic Approval Rules Cần Được Balanced
**Source:** Starbursting (How), Mind Mapping (Quality Gates)
**Impact:** HIGH
**Effort:** LOW

**Description:**
3-tier approval system:
- AUTO-APPROVE (15%): Score >80, Followers >100K, Profile >90%
- MANUAL REVIEW (70%): Score 40-80, needs human judgment
- AUTO-REJECT (15%): Score <40, Followers <5K, fake/bot

**Why it matters:**
- Speed (15% instant approval)
- Quality (filter low-quality automatically)
- Scalability (only 70% need manual review)
- Transparency (clear rejection reasons)

**Tuning:** Start conservative (score >85 auto-approve), adjust based on data

---

### Insight 5: Post-Approval Creator Portal là Retention Driver
**Source:** Mind Mapping (Post-Approval), SCAMPER (Combine)
**Impact:** MEDIUM-HIGH
**Effort:** MEDIUM

**Description:**
Registration không phải endpoint, mà là **starting point** của relationship.

Creator Portal features:
- Profile management (update enrichment monthly)
- Campaign center (browse, apply, track)
- Analytics (profile views, earnings, performance)

**Why it matters:**
- Engagement (influencers login regularly)
- Data freshness (influencers update profile when needed)
- Retention (portal creates stickiness)
- Network effects (more influencers = more campaigns)

**Phase approach:**
- MVP: Basic profile update
- Phase 2: Campaign browsing
- Phase 3: Analytics + growth tools

---

### Insight 6: AI-Suggested Enrichment Giảm Effort 50%
**Source:** SCAMPER (Substitute - AI), Starbursting (How)
**Impact:** MEDIUM
**Effort:** HIGH (AI integration)

**Description:**
AI suggests enrichment data based on crawled content:
- Analyze recent 20 posts
- Extract demographics (comments, followers), topics (hashtags)
- Suggest: "Your audience is 18-25 females interested in beauty"
- Influencer confirms or edits

**Benefits:**
- 50% less time to complete enrichment
- More accurate than self-reported
- Standardized format → better matching
- Educates influencers about their audience

**Recommendation:** Phase 2 feature (after MVP proven)

---

### Insight 7: "Share to AT Pool" Nên Là Optional với Clear Benefits
**Source:** Mind Mapping (AT Integration), Starbursting (Why)
**Impact:** HIGH
**Effort:** LOW

**Description:**
Checkbox "Share my profile to AT Partner Network" with clear benefits:
- ✅ "Get discovered by multiple brands (not just TCB)"
- ✅ "3x more campaign opportunities"
- ⚠️ "Your profile will be visible to AT partners"

**Default:** UNCHECKED (opt-in)

**Why it matters:**
- Consent (influencers choose visibility)
- Quality (only willing influencers opt-in to AT Pool)
- TCB exclusive (TCB can keep influencers private)
- AT quality (AT Pool has committed influencers)

**Workflow:**
- TCB approves → `atPoolStatus: NOT_SYNCED`
- If "Share to AT Pool" → TCB calls AT API → AT approves → `atPoolStatus: SYNCED`

---

### Insight 8: Video Introduction là Differentiation Factor
**Source:** SCAMPER (Substitute), Starbursting (What)
**Impact:** MEDIUM (high value, not MVP)
**Effort:** MEDIUM

**Description:**
Optional 30-second video introduction vs text bio:
- Show personality, voice, presentation style
- Upload video (max 50MB) or record via webcam
- Auto-transcription for searchability

**Why it matters:**
- Differentiation (brands prefer video profiles)
- Authenticity (harder to fake)
- Engagement (video profiles get 2-3x more views)
- Selection (brands assess presentation before inviting)

**Recommendation:** Phase 2 feature, promoted as "Premium" add-on

---

## Statistics

- **Total Ideas:** 51
- **Categories:** 8
- **Key Insights:** 8
- **Techniques Applied:** 3 (Starbursting, Mind Mapping, SCAMPER)

---

## Recommended Implementation Roadmap

### MVP (Phase 1) - 6-8 weeks
**Goal:** Basic registration working, manual approval

**Features:**
- ✅ Multi-step wizard (5 steps)
- ✅ Tiered registration (Quick/Standard/Premium)
- ✅ Social profile crawl (async, via VB API)
- ✅ Email verification
- ✅ Enrichment questionnaire (demographics, content, collab)
- ✅ Automatic quality gates (min followers, score)
- ✅ 3-tier approval (auto-approve, manual, auto-reject)
- ✅ TCB database (full storage)
- ✅ AT Core integration (POST /partners/pool/submit)
- ✅ Basic Creator Portal (view status, update profile)

**Out of scope (MVP):**
- ❌ Social OAuth (Phase 2)
- ❌ Video introduction (Phase 2)
- ❌ AI-suggested enrichment (Phase 2)
- ❌ Campaign center (Phase 2)
- ❌ Analytics dashboard (Phase 3)

---

### Phase 2 - 4-6 weeks (after MVP proven)
**Goal:** Enhanced UX, social OAuth, video intro

**Features:**
- ✅ Social OAuth (TikTok, Instagram, YouTube login)
- ✅ Video introduction upload + recording
- ✅ AI-suggested enrichment (audience analysis)
- ✅ Campaign center (browse, apply)
- ✅ Portfolio builder (select best content)
- ✅ Reviewer dashboard (improved workflow)

---

### Phase 3 - 4-6 weeks (scale & retention)
**Goal:** Analytics, gamification, referrals

**Features:**
- ✅ Analytics dashboard (profile views, earnings)
- ✅ Gamification (achievements, badges)
- ✅ Referral program (invite creators, earn rewards)
- ✅ Market research insights (aggregate data)
- ✅ Brand matching algorithm (show match score)

---

## Recommended Next Steps

### Immediate (This Week):
1. **Align on approach:** Review this document with stakeholders
2. **Prioritize features:** Confirm MVP scope (what's in/out)
3. **Resource planning:** 1 backend dev, 1 frontend dev, 1 designer?

### Week 1-2:
1. **PRD Creation:** Run `/bmad:prd` based on this brainstorming
   - Include: MVP features, tiered registration, dual storage
   - Exclude: OAuth, video, AI (Phase 2)

2. **Tech Spec:** Run `/bmad:tech-spec` for implementation details
   - API endpoints (TCB internal + AT Core integration)
   - Database schema (influencer_submissions table)
   - Async crawl processing (Redis queue)

3. **Design mockups:** Wireframes for 5-step registration wizard

### Week 3+:
1. **Sprint planning:** `/bmad:sprint-planning`
2. **Development:** `/bmad:dev-story` for each epic
3. **Testing:** `/test` for quality assurance

---

## Traceability to AT Core & TCB PRDs

**This feature relates to existing PRDs:**

**AT Core PRD (already planned):**
- ✅ FR-013: Partner Profile Submission → TCB will use this API
- ✅ FR-015: Approval Workflow Management → AT Admin reviews submissions
- ✅ FR-014: Eligibility Check API → Optional, TCB can use to pre-validate

**TCB PRD (needs update):**
- 🆕 NEW EPIC: Influencer Self-Registration
  - Stories: Registration wizard, enrichment forms, approval workflow
- 🆕 NEW EPIC: Creator Portal
  - Stories: Dashboard, profile management, campaign center (Phase 2)

**Integration point:**
```
TCB Registration Flow → POST /api/v1/partners/pool/submit (AT Core API)
                      ← Webhook callback on AT approval
```

---

## Conclusion

**Primary Recommendation:** Implement **Tiered Progressive Registration** (Quick/Standard/Premium) với **3-tier approval system** (auto-approve, manual, auto-reject).

**Key Success Factors:**
1. Low barrier to entry (2-minute Quick registration)
2. Clear value proposition at each tier
3. Fast approval turnaround (auto for 15%, manual 48h SLA)
4. Post-approval Creator Portal for retention
5. Clean dual storage strategy (TCB enrichment, AT platform data)

**Next Step:** Create PRD based on this brainstorming, focusing on MVP features.

---

*Generated by BMAD Method v6 - Creative Intelligence*
*Session duration: 90 minutes*
*Techniques: Starbursting, Mind Mapping, SCAMPER*
