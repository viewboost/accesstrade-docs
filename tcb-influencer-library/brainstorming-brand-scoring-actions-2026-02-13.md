# Brainstorming Session: Brand Portal Actions trong Luồng Scoring Influencers

**Date:** 2026-02-13
**Objective:** Xác định các actions mà Brand Portal nên có để làm việc với influencer profiles trong luồng scoring
**Context:** Influencer đang tự nhập thông tin qua 3-tier onboarding (28 + 38 + 60 fields), Brand Portal cần actions để review, verify, rate profiles
**Related:**
- [plan.md](../../../plans/20260213-0711-influencer-profile-collection/plan.md)
- [prd-tcb-influencer-library-2026-02-13.md](prd-tcb-influencer-library-2026-02-13.md)
- [brainstorming-influencer-library-4sources-2026-02-13.md](brainstorming-influencer-library-4sources-2026-02-13.md)
- [brainstorming-influencer-vs-profile-multi-account-2026-02-13.md](brainstorming-influencer-vs-profile-multi-account-2026-02-13.md)

---

## Executive Summary

**Problem:** Brand Portal chưa có actions rõ ràng để làm việc với influencer profiles - cần thiết kế workflow từ discovery → review → scoring → campaign matching → rating

**Context Update (Feb 13, 2026):**
- ✅ eKYC deferred (Step 2 skipped in MVP onboarding)
- ✅ Profiles auto-visible after Tier 1 complete (no brand approval needed)
- ✅ Multi-profile support: 1 Influencer (person) → Many Profiles (social accounts)
- ✅ Brand works with PROFILES (not influencers directly)
- ✅ Focus: Discovery, filtering, scoring, flagging (NOT pre-approval)

**Recommendation:** **6-CATEGORY ACTION FRAMEWORK** - Auto-visible với quality indicators

**Key Insights:**
1. **Auto-Visible Profiles** - No approval bottleneck, all active profiles visible → Faster onboarding
2. **Transparent Scoring** - Show breakdown + freshness + audit trail → Build trust
3. **AI-Assisted Discovery** - Smart filters + recommendations → Reduce decision fatigue
4. **Context-Aware Scoring** - Adaptive weights theo campaign type → Better matching
5. **Two-Tier Ratings** - Public (shared) + Private (TCB-only) → Balance transparency + confidentiality
6. **Red Flags System** - Proactive warnings về performance drops → Prevent bad matches
7. **Comparison View** - Side-by-side 2-5 influencers + AI insights → Faster decisions

**Total Ideas Generated:** 61 ideas across 6 categories (updated to remove approval workflows)
**Timeline Impact:** Clear action framework → Faster Phase 2 (Brand Portal) implementation

---

## Techniques Used

1. **SCAMPER** - Creative variations (Substitute, Combine, Adapt, Modify, Put to other uses, Eliminate, Reverse)
2. **Starbursting** - Ask Who/What/Where/When/Why/How cho brand workflows
3. **Reverse Brainstorming** - "Làm thế nào để brand scoring FAIL thảm hại?" → Insights từ failure modes

---

## 🔑 Multi-Profile Context (Critical Understanding)

### Data Model: Influencer vs Profile

**Key Architecture Decision:**
```
1 Influencer (Person) → Many Profiles (Social Accounts)

Example:
Influencer: Nguyễn Văn A
├─ @beauty_ig (Instagram, 500K followers)
├─ @beauty_fb (Facebook, 200K followers)
└─ @beauty_tiktok (TikTok, 1M followers)
```

**Why this matters for Brand Portal:**

1. **Brand searches/browses PROFILES, not influencers**
   - Search results show: @beauty_ig, @beauty_fb, @beauty_tiktok (3 separate cards)
   - Each profile has own score, metrics, pricing, audience demographics
   - Influencer info (Nguyễn Văn A) shown as secondary context

2. **Campaign matching at PROFILE level**
   - Campaign needs Instagram → Match @beauty_ig only (not @beauty_fb)
   - Campaign needs finance audience → Match profiles with finance content (not all profiles from same person)
   - Different profiles = different audiences, content strategies, pricing

3. **Ratings/Feedback target PROFILES, not influencers**
   - Brand rates @beauty_ig performance: 4.7/5 (from 25 campaigns)
   - Brand rates @beauty_fb performance: 3.8/5 (from 8 campaigns)
   - Same person, different ratings per profile

**Data Separation:**

| Data Level | Stored Where | Examples |
|------------|--------------|----------|
| **Person-Level** (shared) | `influencers` table | Name, DOB, Bank account, eKYC, Finance affinity (82/100), Compliance |
| **Profile-Level** (specific) | `social_profiles` table | Platform, Handle, Followers (500K on IG vs 200K on FB), Engagement rate, Categories, Audience demographics, Pricing, Campaign performance |

**Brand Portal Implications:**

✅ **DO:**
- Show profile cards (@beauty_ig) as primary entity
- Show influencer info (Nguyễn Văn A) as secondary context
- Allow filtering by profile metrics (followers, engagement, platform)
- Enable comparison between profiles (even from same person)
- Support multi-profile bundles (book all 3 profiles at discount)

❌ **DON'T:**
- Don't conflate influencer data with profile data
- Don't show aggregate metrics across profiles (500K IG + 200K FB ≠ 700K total)
- Don't assume same content strategy across profiles (IG beauty ≠ FB lifestyle)
- Don't apply ratings from one profile to others

**Reference:** See [brainstorming-influencer-vs-profile-multi-account-2026-02-13.md](brainstorming-influencer-vs-profile-multi-account-2026-02-13.md) for full data model.

---

## 📋 Brand Workflow: Xem Profile + Gửi Feedback

### Phase 2 (Current): Discovery & Review - NO Feedback Yet

**Brand actions available:**

```
┌──────────────────────────────────────────────────────────┐
│  PHASE 2: BRAND PORTAL (Discovery Only)                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1. Browse/Search Profiles                               │
│     → See profile cards (platform, handle, metrics)     │
│     → Filter by: platform, niche, followers, score      │
│     → Sort by: score, engagement, completeness          │
│                                                          │
│  2. View Profile Detail Page                             │
│     ┌──────────────────────────────────────────────┐    │
│     │ LEFT: Profile Info                           │    │
│     │ - Platform: Instagram                        │    │
│     │ - Handle: @beauty_ig                         │    │
│     │ - Metrics: 500K followers, 4.2% ER           │    │
│     │ - Categories: Beauty, Lifestyle              │    │
│     │ - Audience: Women 25-35, High income         │    │
│     │ - Pricing: 10M/post, 3M/story               │    │
│     │ - Performance: 25 campaigns, 4.7★ rating    │    │
│     │                                              │    │
│     │ RIGHT: Influencer Context                    │    │
│     │ - Name: Nguyễn Văn A                         │    │
│     │ - Finance Affinity: 82/100 ✅               │    │
│     │ - Other Profiles:                            │    │
│     │   • @beauty_fb (200K, Facebook)             │    │
│     │   • @beauty_tiktok (1M, TikTok)             │    │
│     │                                              │    │
│     │ BOTTOM: Portfolio (THIS PROFILE)             │    │
│     │ - Best posts from @beauty_ig                │    │
│     │ - Performance metrics per post               │    │
│     └──────────────────────────────────────────────┘    │
│                                                          │
│  3. Private Actions (TCB Internal Only)                  │
│     ✓ Add private notes                                 │
│       "Great for credit cards, weak for savings"        │
│     ✓ Add to lists                                      │
│       - Shortlist Q1 2026                               │
│       - Watchlist: Credit Card Specialists              │
│       - Blacklist: Declined influencers                 │
│     ✓ Flag profile (→ Admin review queue)               │
│       Reasons: Fake followers, inappropriate content    │
│                                                          │
│  4. Export/Share                                         │
│     ✓ Export shortlist to Excel/PDF                     │
│     ✓ Compare 2-5 profiles side-by-side                 │
│                                                          │
│  ❌ NOT AVAILABLE IN PHASE 2:                            │
│     - Campaign invitations (Phase 3)                    │
│     - Performance ratings (Phase 3, post-campaign)      │
│     - Deliverable reviews (Phase 3)                     │
└──────────────────────────────────────────────────────────┘
```

---

### Phase 3 (Future): Campaign + Feedback Workflow

**When ratings/feedback happen:**

```
┌──────────────────────────────────────────────────────────┐
│  PHASE 3: CAMPAIGN WORKFLOW (Future)                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  STEP 1: Brand Invites Profile                           │
│  ─────────────────────────────                           │
│  Brand: "I want @beauty_ig for credit card campaign"    │
│  Action: Send invitation to THIS PROFILE                 │
│  (Not to influencer - specific to @beauty_ig)           │
│                                                          │
│  STEP 2: Influencer Accepts                              │
│  ─────────────────────────────                           │
│  Influencer: "I'll use @beauty_ig for this campaign"    │
│  Status: Campaign ACTIVE                                 │
│                                                          │
│  STEP 3: Influencer Submits Deliverables                 │
│  ─────────────────────────────                           │
│  Deliverables: 3 posts + 5 stories on @beauty_ig        │
│  Brand reviews: Content quality, messaging compliance    │
│                                                          │
│  STEP 4: Campaign Completes                              │
│  ─────────────────────────────                           │
│  Results: 480K reach, 3.2% CTR, 145 conversions         │
│                                                          │
│  STEP 5: ✅ Brand Rates PROFILE Performance              │
│  ─────────────────────────────                           │
│  ┌────────────────────────────────────────────────┐     │
│  │ Post-Campaign Review: @beauty_ig               │     │
│  │                                                │     │
│  │ Overall Rating: ⭐⭐⭐⭐⭐ 5/5                  │     │
│  │                                                │     │
│  │ Detailed Ratings:                              │     │
│  │ • Content Quality:    ⭐⭐⭐⭐⭐ 5/5           │     │
│  │ • Professionalism:    ⭐⭐⭐⭐⭐ 5/5           │     │
│  │ • Communication:      ⭐⭐⭐⭐☆ 4/5           │     │
│  │ • On-time Delivery:   ⭐⭐⭐⭐⭐ 5/5           │     │
│  │ • Performance:        ⭐⭐⭐⭐☆ 4/5           │     │
│  │                                                │     │
│  │ Review (Optional):                             │     │
│  │ "Excellent content quality, delivered on      │     │
│  │  time. Engagement slightly below target       │     │
│  │  but overall great collaboration."            │     │
│  │                                                │     │
│  │ Privacy: ○ Public ● Private (TCB only)         │     │
│  │                                                │     │
│  │ [Submit Rating]                                │     │
│  └────────────────────────────────────────────────┘     │
│                                                          │
│  RESULT: Profile rating updated                          │
│  ─────────────────────────────                           │
│  @beauty_ig: 26 campaigns, avg rating 4.7/5             │
│  (This rating does NOT affect @beauty_fb or @tiktok)    │
└──────────────────────────────────────────────────────────┘
```

---

### Data Storage: Profile-Level Ratings

**Stored in `social_profiles` table (NOT influencers):**

```typescript
// Profile-specific performance data
social_profiles {
  id: "uuid-@beauty_ig",
  influencer_id: "uuid-nguyen-van-a",
  platform: "instagram",
  account_handle: "@beauty_ig",

  // Performance History (THIS PROFILE ONLY)
  campaigns_completed: 26,
  campaigns_last_12mo: 12,
  avg_brand_rating: 4.7, // Average from 26 campaigns
  avg_ctr: 3.8,
  avg_cvr: 1.5,
  total_revenue_generated: 195000000, // 195M VND

  // Last updated: After each campaign completion
}

// Campaign-specific rating
campaign_performance {
  campaign_id: "uuid-campaign-123",
  profile_id: "uuid-@beauty_ig", // Linked to PROFILE
  influencer_id: "uuid-nguyen-van-a",

  // Auto-tracked metrics
  reach: 480000,
  engagement: 21000,
  ctr: 3.2,
  conversions: 145,

  // Brand rating (manual input)
  brand_rating_overall: 4.5,
  brand_rating_breakdown: {
    content_quality: 5,
    professionalism: 5,
    communication: 4,
    on_time: 5,
    performance: 4
  },
  brand_review_text: "Excellent content...",
  rating_visibility: "private", // or "public"

  created_at: "2026-02-13"
}

// Brand private notes (per brand, per profile)
brand_profile_notes {
  brand_id: "uuid-tcb",
  profile_id: "uuid-@beauty_ig", // NOT influencer_id
  note: "Great for credit cards, weak for savings",
  tags: ["credit-card-specialist"],
  created_at: "2026-02-13"
}
```

---

### Multi-Profile Feedback Example

**Same influencer, different ratings per profile:**

```
Influencer: Nguyễn Văn A
Finance Affinity: 82/100 (person-level, shared)

├─ @beauty_ig (Instagram, 500K)
│  └─ Brand Rating: 4.7/5 ⭐⭐⭐⭐⭐ (from 26 campaigns)
│  └─ TCB Note: "Great for credit cards, young audience"
│  └─ Best for: Visual product reviews, high-income audience
│
├─ @beauty_fb (Facebook, 200K)
│  └─ Brand Rating: 3.8/5 ⭐⭐⭐⭐ (from 8 campaigns)
│  └─ TCB Note: "Lower engagement, older audience"
│  └─ Best for: Community engagement, broader reach
│
└─ @beauty_tiktok (TikTok, 1M)
   └─ Brand Rating: 4.9/5 ⭐⭐⭐⭐⭐ (from 12 campaigns)
   └─ TCB Note: "Viral potential, Gen Z audience"
   └─ Best for: Viral trends, young demographics
```

**Brand Portal Display:**

When brand searches "beauty influencers 100K+":
- Shows 3 SEPARATE profile cards (not 1 influencer card)
- Each card shows profile-specific rating + metrics
- Brand can see "Same person" indicator but rates separately

---

## Ideas Generated

### Category 1: Discovery & Browsing (13 ideas)

**⚠️ MULTI-PROFILE CONTEXT:**
- Brand searches/browses PROFILES (not influencers)
- Each profile (@beauty_ig, @beauty_fb) shown as separate card
- Influencer info (Nguyễn Văn A) shown as secondary context
- Filters/sorts apply to PROFILE metrics (not aggregated)

#### Idea 1.4: Browse + Filter + Score Preview trong 1 screen
**Description:** Unified view - Sidebar filters, Main grid influencer cards, Right panel score breakdown
**Source:** SCAMPER (Combine)
**Benefit:** Faster discovery, context-rich decisions
**Priority:** HIGH - Phase 2 core feature

#### Idea 2.7: Multi-channel Discovery Touchpoints
**Description:**
- Browse Library page (search + filters)
- Campaign Match Suggestions page (AI-powered)
- Email digest (weekly new profiles)
**Source:** Starbursting (WHERE)
**Benefit:** Reach brand users at different touchpoints
**Priority:** MEDIUM - Phase 2-3

#### Idea 3.1: Smart Filters với Saved Presets
**Description:** Pre-configured filters like "Finance influencers 100K+", "Beauty nano 10-50K"
**Source:** Reverse Brainstorming (Failure Mode 1)
**Benefit:** Faster search, reusable workflows
**Priority:** HIGH - Phase 2

#### Idea 3.2: AI-Powered Recommendations
**Description:** "Top 10 matches for this campaign" based on campaign brief + influencer scores
**Source:** Reverse Brainstorming
**Benefit:** Less effort, AI-driven matching
**Priority:** MEDIUM - Phase 3 (requires ML)

#### Idea 3.3: Default Sort by Highest Score
**Description:** Landing page shows best matches first (not random)
**Source:** Reverse Brainstorming
**Benefit:** Immediate value, reduce scroll fatigue
**Priority:** HIGH - Phase 2

#### Idea 3.10: Minimum Score Threshold Filter
**Description:** Hide profiles <40 Overall Score (configurable by brand)
**Source:** Reverse Brainstorming (Failure Mode 4)
**Benefit:** Reduce noise, focus on quality
**Priority:** MEDIUM - Phase 2

#### Idea 3.11: Completeness Filter
**Description:** Only show profiles ≥70% complete (or custom threshold)
**Source:** Reverse Brainstorming
**Benefit:** Ensure usable data
**Priority:** MEDIUM - Phase 2

#### Idea 3.19: Custom Tag System
**Description:** Brand adds custom tags: "credit-card-specialist", "millennial-savers"
**Source:** Reverse Brainstorming (Failure Mode 7)
**Benefit:** Niche targeting beyond generic categories
**Priority:** MEDIUM - Phase 3

#### Idea 3.20: AI Content Analysis for Niche Detection
**Description:** Auto-detect niche from past posts (không chỉ self-declaration)
**Source:** Reverse Brainstorming
**Benefit:** Accurate niche classification
**Priority:** LOW - Phase 4 (requires NLP)

#### Idea 3.21: Negative Filters
**Description:** "Exclude beauty influencers" when looking for finance-only
**Source:** Reverse Brainstorming
**Benefit:** Precision targeting
**Priority:** LOW - Phase 3

#### Idea 2.16: Faceted Search UI
**Description:**
- Quick filters: Niche, Followers range, Score threshold, Finance affinity
- Advanced filters: Audience demographics, past campaign types, geography
**Source:** Starbursting (HOW)
**Benefit:** Professional search experience
**Priority:** HIGH - Phase 2

#### Idea 1.20: Wishlist → System Suggests Matches
**Description:** Brand creates wishlist (target audience, budget, goals) → AI suggests profiles
**Source:** SCAMPER (Reverse)
**Benefit:** Proactive matching vs passive browsing
**Priority:** MEDIUM - Phase 3

#### Idea 1.21: Multi-Profile Bundle Discovery
**Description:** When viewing profile detail, show "Other Profiles from Same Person":
- @beauty_ig (primary) + @beauty_fb + @beauty_tiktok
- "Bundle all 3 profiles: 27M (save 3M, 10% off)"
- "Multi-platform reach: Instagram + Facebook + TikTok"
**Source:** Multi-profile architecture
**Benefit:** Upsell multi-platform campaigns, higher AOV
**Priority:** MEDIUM - Phase 3

---

### Category 2: Profile Quality & Flagging (8 ideas)

**⚠️ IMPORTANT CONTEXT UPDATE:**
- eKYC deferred (Step 2 skipped in MVP)
- No "brand approval" needed for profiles to be visible
- All active profiles auto-visible in Brand Portal
- Brand can FLAG problematic profiles → Admin reviews

#### Idea 1.2: AI-Powered OCR Demographics Validation
**Description:** OCR extract demographics từ screenshots → Auto-validate percentages sum = 100%
**Source:** SCAMPER (Substitute)
**Benefit:** Instant validation, catch errors early
**Context:** Tier 2 demographics screenshots (optional upload)
**Priority:** MEDIUM - Phase 3

#### Idea 2.1: Role-Based Permissions
**Description:**
- Marketing Manager: Strategic decisions (campaign fit, brand alignment)
- Junior Associate: Search/filter operations
**Source:** Starbursting (WHO)
**Benefit:** Efficient task allocation
**Priority:** MEDIUM - Phase 3

#### Idea 3.12: Trust Badge System (Auto-Generated)
**Description:** System auto-generates badges based on data:
- "✓ Crawl Verified" (social metrics confirmed by vendor)
- "✓✓ Email Verified" (optional email verification completed)
- "✓✓✓ Tier 2 Complete" (66% profile completeness)
**Source:** Reverse Brainstorming (Failure Mode 4)
**Benefit:** Quick trust signals, no manual approval needed
**Priority:** MEDIUM - Phase 2

#### Idea 2.10: Flag Profile System
**Description:** Brand can flag inappropriate profiles:
- Reasons: Fake followers, inappropriate content, competitor brand
- Action: Flagged → Admin Portal review queue
- Admin actions: Investigate, Suspend, or Dismiss flag
**Source:** Starbursting (WHEN)
**Benefit:** Community moderation, brand safety
**Priority:** MEDIUM - Phase 3

#### Idea 2.12: Profile Freshness Indicators
**Description:** Auto-detect stale profiles:
- Last active >90 days → Show "⚠️ Inactive profile"
- Social metrics >30 days old → Show "⏱️ Metrics may be outdated"
**Source:** Starbursting (WHEN)
**Benefit:** Data quality awareness
**Priority:** LOW - Phase 3

#### Idea 2.13: Quality Score Breakdown (Transparent)
**Description:** Show HOW quality score calculated:
- Profile Completeness: 30% (66/100 = Tier 1+2 complete)
- Social Metrics Quality: 40% (verified by vendor, fresh <7 days)
- Engagement Quality: 20% (ER >3%, not fake)
- Portfolio Quality: 10% (has best posts uploaded)
**Source:** Starbursting (WHY)
**Benefit:** Transparent scoring, build trust
**Priority:** HIGH - Phase 2

#### Idea 1.16: Eliminate Manual Follower Count Entry
**Description:** Crawl tự động lấy → Influencer không cần nhập
**Source:** SCAMPER (Eliminate)
**Benefit:** Less friction, higher accuracy
**Priority:** HIGH - Phase 1 (already planned)

#### Idea 2.14: Watchlist for Brand Safety
**Description:** Brand maintains private watchlist:
- Blacklist: Never show these influencers (competitor brands, controversy)
- Whitelist: Priority/favorite influencers (past good performance)
**Source:** Brand safety requirements
**Benefit:** Custom content filtering
**Priority:** MEDIUM - Phase 3

---

### Category 3: Scoring & Insights (15 ideas)

#### Idea 1.7: Adaptive Scoring Weights theo Campaign Type
**Description:**
- Awareness: Reach (40%), Engagement (30%), Finance Affinity (20%), Conversion (10%)
- Conversion: Finance Affinity (30%), Conversion (50%), Reach (10%), Engagement (10%)
**Source:** SCAMPER (Adapt)
**Benefit:** Campaign-specific matching accuracy
**Priority:** HIGH - Phase 2

#### Idea 1.9: Time-Based Score Decay
**Description:**
- No activity >6 months → Score × 0.8
- No activity >12 months → Flagged for re-verification
**Source:** SCAMPER (Adapt)
**Benefit:** Accurate, fresh scores
**Priority:** MEDIUM - Phase 3

#### Idea 1.10: Visual Score Cards
**Description:**
```
Overall Score: 87/100 ⭐⭐⭐⭐

🎯 Reach: 92/100 ████████████░
💬 Engagement: 85/100 ███████████░░
💰 Finance Affinity: 78/100 ██████████░░░
✓ Completeness: 95/100 ████████████░
```
**Source:** SCAMPER (Modify)
**Benefit:** Easier to scan, faster decisions
**Priority:** HIGH - Phase 2

#### Idea 1.11: Comparison View (Side-by-Side)
**Description:** Select 2-5 influencers → Compare scores, audience, past campaigns
**Source:** SCAMPER (Modify)
**Benefit:** Better selection decisions
**Priority:** MEDIUM - Phase 2

#### Idea 1.12: Trend Indicators
**Description:**
- Follower count: 500K (↗️ +15% vs 30d ago)
- Engagement rate: 3.2% (↘️ -0.5% vs 30d ago)
**Source:** SCAMPER (Modify)
**Benefit:** Forward-looking decisions
**Priority:** MEDIUM - Phase 2

#### Idea 2.6: Expandable Score Breakdown UI
**Description:** Click Overall Score → Expand to show sub-scores + weights
**Source:** Starbursting (WHAT)
**Benefit:** Transparency
**Priority:** HIGH - Phase 2

#### Idea 2.11: Real-Time Score Recalculation Engine
**Description:**
- Social metrics: Daily auto-update
- Performance: After campaign completes
- Ratings: Immediately after submission
**Source:** Starbursting (WHEN)
**Benefit:** Always fresh data
**Priority:** MEDIUM - Phase 2

#### Idea 2.15: Finance Affinity Score (Separate Metric)
**Description:** Finance Affinity tracked separately từ Overall Score
**Source:** Starbursting (WHY)
**Benefit:** Niche-specific matching
**Priority:** HIGH - Phase 2

#### Idea 3.4: Score Breakdown Always Visible
**Description:** Không hide sub-scores, always show chi tiết
**Source:** Reverse Brainstorming (Failure Mode 2)
**Benefit:** Informed decisions
**Priority:** HIGH - Phase 2

#### Idea 3.5: Red Flags Highlighting
**Description:** "⚠️ Engagement rate dropped 40% last 3 months"
**Source:** Reverse Brainstorming (Failure Mode 2)
**Benefit:** Prevent bad matches
**Priority:** HIGH - Phase 2

#### Idea 3.6: Past Campaign Performance Preview
**Description:** "3/5 TCB campaigns completed on-time"
**Source:** Reverse Brainstorming (Failure Mode 2)
**Benefit:** Historical context
**Priority:** MEDIUM - Phase 2

#### Idea 3.7: Transparent Scoring Explanation
**Description:** "Score based on: Crawl (30%), Performance (40%), Ratings (20%), Completeness (10%)"
**Source:** Reverse Brainstorming (Failure Mode 3)
**Benefit:** Build trust
**Priority:** HIGH - Phase 2

#### Idea 3.8: Data Freshness Indicators
**Description:** "Followers updated 2h ago, Engagement rate updated daily"
**Source:** Reverse Brainstorming (Failure Mode 3)
**Benefit:** Trust in data quality
**Priority:** MEDIUM - Phase 2

#### Idea 3.9: Audit Trail for Score Changes
**Description:** "Score changed 82 → 87 on Feb 10 due to campaign completion"
**Source:** Reverse Brainstorming (Failure Mode 3)
**Benefit:** Transparency, debugging
**Priority:** LOW - Phase 3

#### Idea 2.17: AI Insights in Comparison
**Description:** "Influencer A: Better reach (+25%), Influencer B: Better engagement (+15%)"
**Source:** Starbursting (HOW)
**Benefit:** Guided decisions
**Priority:** MEDIUM - Phase 3 (requires ML)

---

### Category 4: Campaign Management (5 ideas)

#### Idea 1.5: Profile Review + Invitation Combined Flow
**Description:** Review profile → Immediately invite to campaign (1-click)
**Source:** SCAMPER (Combine)
**Benefit:** Reduce friction
**Priority:** HIGH - Phase 3 (depends on Campaign features)

#### Idea 1.21: Influencer Applies to Campaign
**Description:** Brand posts campaign → Influencers discover & apply → Brand reviews applicants
**Source:** SCAMPER (Reverse)
**Benefit:** Self-selection, serious applicants
**Priority:** MEDIUM - Phase 4

#### Idea 2.18: Campaign Dashboard
**Description:** Campaigns → Invitations → Status (Pending, Accepted, Declined)
**Source:** Starbursting (HOW)
**Benefit:** Track interactions
**Priority:** HIGH - Phase 3

#### Idea 3.22: Invitation Status Badges
**Description:** "✓ Invited to 2 campaigns", "❌ Declined last campaign"
**Source:** Reverse Brainstorming (Failure Mode 8)
**Benefit:** Prevent duplicate invites
**Priority:** MEDIUM - Phase 3

#### Idea 3.23: Interaction History
**Description:** "Last contacted: Jan 15, Campaign: CNY Promo"
**Source:** Reverse Brainstorming (Failure Mode 8)
**Benefit:** Context for decisions
**Priority:** MEDIUM - Phase 3

---

### Category 5: Ratings & Feedback (11 ideas)

#### Idea 1.3: Peer Ratings from Other Brands
**Description:** "3/5 brands rated this influencer 4.5★" → Social proof
**Source:** SCAMPER (Substitute)
**Benefit:** More data points
**Priority:** MEDIUM - Phase 3 (if AT Pool shared ratings)

#### Idea 1.6: Rating + Testimonial Combined Submission
**Description:** 1 form: Star rating + short review (100 chars)
**Source:** SCAMPER (Combine)
**Benefit:** Richer feedback
**Priority:** MEDIUM - Phase 3

#### Idea 2.3: Two-Tier Rating System
**Description:**
- Public: Star rating + review (visible to all brands)
- Private: Internal notes + tags (TCB only)
**Source:** Starbursting (WHO)
**Benefit:** Balance transparency + confidentiality
**Priority:** HIGH - Phase 3

#### Idea 2.8: Contextual Rating Forms
**Description:**
- Post-campaign review page (mandatory after campaign)
- Influencer profile page (ad-hoc ratings anytime)
**Source:** Starbursting (WHERE)
**Benefit:** Flexibility
**Priority:** MEDIUM - Phase 3

#### Idea 2.14: Mandatory Post-Campaign Rating Flow
**Description:** Campaign completes → Brand MUST rate before closing
**Source:** Starbursting (WHY)
**Benefit:** Consistent data collection
**Priority:** HIGH - Phase 3

#### Idea 2.19: Multi-Level Feedback System
**Description:**
- Level 1: Private message to influencer (constructive feedback)
- Level 2: Rating submission (visible to brands)
- Level 3: Flag profile (admin review if severe)
**Source:** Starbursting (HOW)
**Benefit:** Graduated responses
**Priority:** MEDIUM - Phase 3

#### Idea 1.19: Influencer Reviews Brands (Reverse)
**Description:** Influencers rate brands: "TCB pays on-time 5★", "Clear briefs 4.5★"
**Source:** SCAMPER (Reverse)
**Benefit:** Accountability, attract better influencers
**Priority:** LOW - Phase 4

#### Idea 3.13: Warning Banners
**Description:** "⚠️ 2 brands reported late deliveries"
**Source:** Reverse Brainstorming (Failure Mode 5)
**Benefit:** Prevent bad matches
**Priority:** HIGH - Phase 2

#### Idea 3.16: Mandatory Rating Justification
**Description:** Low rating (<3★) → Must explain why
**Source:** Reverse Brainstorming (Failure Mode 6)
**Benefit:** Fair, actionable feedback
**Priority:** MEDIUM - Phase 3

#### Idea 3.17: Rating Review by Admin
**Description:** Outlier ratings flagged (TCB gives 1★, others give 5★)
**Source:** Reverse Brainstorming (Failure Mode 6)
**Benefit:** Prevent unfair bias
**Priority:** LOW - Phase 4

#### Idea 3.18: Influencer Response to Ratings
**Description:** Influencer can reply to low ratings with context
**Source:** Reverse Brainstorming (Failure Mode 6)
**Benefit:** Fair hearing, dispute resolution
**Priority:** LOW - Phase 4

---

### Category 6: Data Management & Tracking (8 ideas)

#### Idea 1.13: Export Shortlist to Excel/PDF
**Description:** Brand selects influencers → Export với scores, contact info
**Source:** SCAMPER (Put to other uses)
**Benefit:** Workflow compatibility (get management approval)
**Priority:** MEDIUM - Phase 2

#### Idea 1.14: Score History Chart
**Description:** 6-12 month trend chart for Overall Score
**Source:** SCAMPER (Put to other uses)
**Benefit:** See trajectory (rising stars vs declining)
**Priority:** MEDIUM - Phase 2

#### Idea 1.15: Public Leaderboard
**Description:** "Top 100 Finance Influencers" (opt-in by influencers)
**Source:** SCAMPER (Put to other uses)
**Benefit:** Gamification, motivation
**Priority:** LOW - Phase 4

#### Idea 2.2: Configurable Notifications
**Description:**
- Slack channel: Real-time new profile submissions
- Email digest: Daily/Weekly summary
**Source:** Starbursting (WHO)
**Benefit:** Stay informed
**Priority:** MEDIUM - Phase 2

#### Idea 2.9: Data Residency Settings
**Description:**
- TCB internal: All data stays in TCB database
- Shared: Opt-in to AT Pool (anonymous ratings visible to other brands)
**Source:** Starbursting (WHERE)
**Benefit:** Compliance, flexibility
**Priority:** LOW - Phase 3

#### Idea 3.14: Performance History Chart
**Description:** Completion rate trend over 12 months
**Source:** Reverse Brainstorming (Failure Mode 5)
**Benefit:** Predict future reliability
**Priority:** MEDIUM - Phase 3

#### Idea 3.15: Brand Community Notes
**Description:** Anonymized feedback from other brands: "Great for awareness campaigns, weak on sales"
**Source:** Reverse Brainstorming (Failure Mode 5)
**Benefit:** Collective intelligence
**Priority:** LOW - Phase 4 (requires AT Pool integration)

#### Idea 3.24: Lists/Collections
**Description:** Brand creates custom lists: "Shortlist Q1 2026", "Declined influencers", "Top performers"
**Source:** Reverse Brainstorming (Failure Mode 8)
**Benefit:** Organize workflow
**Priority:** MEDIUM - Phase 3

---

## Key Insights

### Insight 1: Auto-Visible Profiles + Quality Indicators (No Approval Needed)
**Description:** All active profiles auto-visible, Brand relies on quality scores + badges để filter
**Source:** SCAMPER (Adapt), Reverse Brainstorming, Updated MVP scope (eKYC deferred)
**Impact:** HIGH | **Effort:** LOW
**Why it matters:**
- **No bottleneck:** Influencers visible immediately after Tier 1 complete (20 fields, no eKYC)
- **Quality signals:** Trust badges auto-generated (Crawl Verified, Email Verified, Tier 2 Complete)
- **Brand filters:** Filter by completeness %, score threshold, verification status
- **Flagging system:** Brand flags problematic profiles → Admin reviews (not pre-approval)

**Implementation Path:**
1. **Phase 2:** Quality Score calculation (Completeness 30% + Social Metrics 40% + Engagement 20% + Portfolio 10%)
2. **Phase 2:** Auto-generated trust badges (no manual approval)
3. **Phase 3:** Flag profile system (brand → admin moderation queue)

---

### Insight 2: Transparent Scoring builds Trust
**Description:** Brand Portal PHẢI show score breakdown + data freshness + audit trail
**Source:** Reverse Brainstorming (Failure Mode 3), Starbursting (WHY)
**Impact:** HIGH | **Effort:** LOW
**Why it matters:**
- Black-box scores → Brand không trust → Fallback to manual hunting
- Transparent breakdown → Brand understand WHY influencer scored 87/100
- Audit trail → Brand see score evolution, not just snapshot

**Implementation Path:**
1. **Phase 2:** Visual score cards với sub-scores (Reach, Engagement, Finance Affinity, Completeness)
2. **Phase 2:** Data freshness indicators: "Followers updated 2h ago"
3. **Phase 3:** Score history chart + audit trail

---

### Insight 3: Discovery cần AI-Assisted Filtering
**Description:** Smart filters + AI recommendations + saved presets giảm decision fatigue
**Source:** SCAMPER (Combine), Reverse Brainstorming (Failure Mode 1)
**Impact:** HIGH | **Effort:** HIGH
**Why it matters:**
- 1000+ influencer library → Brand overwhelmed without smart filters
- Generic filters (followers range) không đủ → Need Finance Affinity, Niche tags
- AI recommendations → "Top 10 matches for your campaign"

**Implementation Path:**
1. **Phase 2:** Faceted search (Quick filters: Niche, Followers, Score + Advanced filters: Demographics, Geography)
2. **Phase 2:** Saved filter presets ("Finance influencers 100K+")
3. **Phase 3:** AI-powered recommendations engine (requires ML model)

---

### Insight 4: Campaign Context-Aware Scoring
**Description:** Overall Score không đủ - cần adaptive weights theo campaign type
**Source:** SCAMPER (Adapt), Starbursting (WHAT)
**Impact:** MEDIUM | **Effort:** MEDIUM
**Why it matters:**
- Awareness campaign: Reach quan trọng hơn Conversion
- Sales campaign: Finance Affinity + Conversion rate quan trọng nhất
- Generic scoring → Mismatched influencers → Poor ROI

**Implementation Path:**
1. **Phase 2:** Campaign type selection dropdown (Awareness / Consideration / Conversion)
2. **Phase 2:** Dynamic weight adjustment:
   - Awareness: `Reach (40%) + Engagement (30%) + Finance (20%) + Conversion (10%)`
   - Conversion: `Finance (30%) + Conversion (50%) + Reach (10%) + Engagement (10%)`
3. **Phase 3:** Machine learning model learns optimal weights from past campaign ROI

---

### Insight 5: Two-Tier Rating System cần thiết
**Description:** Public ratings (shared) + Private notes (TCB internal only)
**Source:** Starbursting (WHO, WHERE), SCAMPER (Combine)
**Impact:** MEDIUM | **Effort:** LOW
**Why it matters:**
- Public ratings → Community benefit (if AT Pool shared), influencer accountability
- Private notes → TCB-specific context (e.g., "Great for credit cards, poor for savings")
- Balance: Transparency + Confidentiality

**Implementation Path:**
1. **Phase 3:** Public rating system (star rating 1-5 + 100-char review)
2. **Phase 3:** Private notes system (internal tags + freeform notes, TCB team only)
3. **Phase 4:** Optional: Share public ratings with AT Pool (tenant opt-in)

---

### Insight 6: Red Flags & Warning System prevent bad matches
**Description:** Proactive warnings về performance drops, late deliveries, complaints
**Source:** Reverse Brainstorming (Failure Mode 5), Starbursting (HOW)
**Impact:** HIGH | **Effort:** MEDIUM
**Why it matters:**
- Brand chọn influencer score 92 → Later discovers 2 late deliveries
- Prevent costly mistakes BEFORE campaign starts
- Auto-detect anomalies: Engagement drop 40%, multiple brand complaints

**Implementation Path:**
1. **Phase 2:** Warning banners in profile cards:
   - "⚠️ Engagement rate dropped 40% last 3 months"
   - "⚠️ 2 brands reported late deliveries"
2. **Phase 2:** Trend indicators: ↗️↘️ for all dynamic metrics
3. **Phase 3:** Anomaly detection algorithm (auto-flag unusual changes)

---

### Insight 7: Comparison View accelerates decision-making
**Description:** Side-by-side comparison của 2-5 influencers với AI insights
**Source:** SCAMPER (Modify), Starbursting (HOW)
**Impact:** MEDIUM | **Effort:** MEDIUM
**Why it matters:**
- Brand shortlists 3-5 candidates → Needs easy comparison
- Manual comparison (open multiple tabs) → Tedious, error-prone
- AI insights: "Influencer A: Better reach (+25%), Influencer B: Better engagement (+15%)"

**Implementation Path:**
1. **Phase 2:** Comparison modal: Select 2-5 influencers → Side-by-side table
2. **Phase 2:** Show all key metrics: Scores, audience demographics, past campaign performance
3. **Phase 3:** AI recommendation: "For your Awareness campaign, Influencer A is better match (+12% expected reach)"

---

## Recommended Implementation Phases

### **Phase 2: Brand Portal Core (Current - Week 3-4)**
**Priority: HIGH**
**Effort: 2 weeks**

**Features to implement:**
1. **Discovery & Browsing (6 features):**
   - ✓ Browse + Filter + Score Preview UI (Idea 1.4)
   - ✓ Faceted search (Quick + Advanced filters) (Idea 2.16)
   - ✓ Smart filter presets (Idea 3.1)
   - ✓ Default sort by score (Idea 3.3)
   - ✓ Minimum score threshold filter (Idea 3.10)
   - ✓ Completeness % filter (Idea 3.11)

2. **Scoring & Insights (7 features):**
   - ✓ Visual score cards (Idea 1.10)
   - ✓ Expandable score breakdown (Idea 2.6)
   - ✓ Transparent scoring explanation (Idea 3.7)
   - ✓ Data freshness indicators (Idea 3.8)
   - ✓ Red flags highlighting (Idea 3.5)
   - ✓ Finance Affinity Score (Idea 2.15)
   - ✓ Adaptive weights by campaign type (Idea 1.7)

3. **Profile Quality (4 features):**
   - ✓ Auto-generated trust badges (Idea 3.12) - "✓ Crawl Verified", "✓✓ Email Verified", "✓✓✓ Tier 2 Complete"
   - ✓ Quality Score breakdown (Idea 2.13) - Completeness + Social Metrics + Engagement + Portfolio
   - ✓ Profile freshness warnings (Idea 2.12) - "⚠️ Inactive >90 days"
   - ✓ Transparent score calculation (Idea 2.13)

4. **Data Management (4 features):**
   - ✓ Export shortlist to Excel/PDF (Idea 1.13)
   - ✓ Score history chart (Idea 1.14)
   - ✓ Configurable notifications (Idea 2.2)
   - ✓ Comparison view (Idea 1.11)

**Total: 21 features in Phase 2** (removed 3 approval-related features)

---

### **Phase 3: Advanced Features (Week 5-6)**
**Priority: MEDIUM**
**Effort: 2 weeks**

**Features to implement:**
1. **Campaign Management:**
   - Campaign Dashboard (Idea 2.18)
   - Profile + Invitation combined flow (Idea 1.5)
   - Invitation status badges (Idea 3.22)
   - Interaction history (Idea 3.23)

2. **Ratings & Feedback:**
   - Two-tier rating system (Idea 2.3)
   - Rating + Testimonial form (Idea 1.6)
   - Mandatory post-campaign rating (Idea 2.14)
   - Multi-level feedback system (Idea 2.19)
   - Rating justification (Idea 3.16)

3. **Advanced Filters:**
   - Custom tag system (Idea 3.19)
   - Lists/Collections (Idea 3.24)
   - Multi-channel discovery (Idea 2.7)

4. **Insights:**
   - Comparison view (Idea 1.11)
   - Trend indicators (Idea 1.12)
   - Performance history chart (Idea 3.14)
   - Time-based score decay (Idea 1.9)

**Total: 16 features in Phase 3**

---

### **Phase 4: AI & Community Features (Week 7+)**
**Priority: LOW**
**Effort: 3+ weeks**

**Features to implement:**
1. **AI-Powered:**
   - AI recommendations engine (Idea 3.2)
   - AI content analysis (Idea 3.20)
   - AI insights in comparison (Idea 2.17)

2. **Community & Gamification:**
   - Public leaderboard (Idea 1.15)
   - Influencer reviews brands (Idea 1.19)
   - Brand community notes (Idea 3.15)
   - Influencer response to ratings (Idea 3.18)

3. **Advanced Review:**
   - AI-powered OCR validation (Idea 1.2)
   - Role-based permissions (Idea 2.1)
   - Audit trail (Idea 3.9)
   - Rating review by admin (Idea 3.17)

4. **Discovery:**
   - Wishlist matching (Idea 1.20)
   - Influencer applies to campaign (Idea 1.21)
   - Negative filters (Idea 3.21)

**Total: 14 features in Phase 4**

---

## Statistics

- **Total ideas generated:** 61 ideas
- **Categories:** 6 categories
- **Key insights:** 7 insights
- **Techniques applied:** 3 (SCAMPER, Starbursting, Reverse Brainstorming)
- **Session duration:** 45 minutes

---

## Recommended Next Steps

### Immediate Actions (This Week)

1. **Review with Team:**
   - Share brainstorming với Product Manager + Design team
   - Prioritize Phase 2 features (24 features)
   - Cut scope if timeline tight (focus on top 15 HIGH priority)

2. **Technical Planning:**
   - Design score calculation engine (4 sources: Onboarding, Crawl, Performance, Ratings)
   - Design Trust Score formula for progressive automation
   - Design adaptive scoring weights (campaign type → weight adjustments)

3. **UI/UX Design:**
   - Wireframe: Browse Library page (filters + cards + score breakdown)
   - Wireframe: Score card component (visual bars, sub-scores)
   - Wireframe: Comparison view modal

### Next Workflow

**Run `/bmad:architecture` to design technical implementation:**
- Score calculation service architecture
- Real-time score recalculation triggers
- Filtering & search optimization (PostgreSQL indexes, Redis cache)
- Warning system (anomaly detection algorithm)

**Or run `/bmad:create-story` to create Sprint stories:**
- Break down 24 Phase 2 features into user stories
- Estimate story points
- Create acceptance criteria

---

*Generated by BMAD Method v6 - Creative Intelligence*
*Session duration: 45 minutes*
*Techniques: SCAMPER, Starbursting, Reverse Brainstorming*
