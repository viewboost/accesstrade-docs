# Brainstorming Session: Luồng Gửi Review vào Profile của Influencer

**Date:** 2026-02-13
**Objective:** Thiết kế luồng gửi review/rating vào profile của influencer sau khi campaign hoàn thành
**Context:** Phase 3 (Brand Portal - Campaign & Ratings) implementation
**Duration:** 60 minutes

---

## Executive Summary

**Problem Statement:**
Sau khi hoàn thành Brand Portal implementation (Phase 1-3), TCB cần luồng để brands gửi review/rating vào influencer profiles. System đã có:
- ✅ Danh sách influencers (person-level data)
- ✅ Danh sách profiles (social accounts: @beauty_ig, @beauty_fb, etc.)
- ✅ Multi-profile architecture (1 Influencer → Many Profiles)
- ❌ Chưa có: Review workflow, rating form, rating storage, rating display

**Solution:**
Thiết kế **Profile-Level Review System** với:
1. **5-Criteria Rating:** Content Quality, Professionalism, Communication, On-time Delivery, Performance
2. **Hybrid Auto+Manual:** Performance auto-calculated, others manual
3. **Two-Tier Privacy:** Public (community-shared) + Private (TCB-only)
4. **Influencer Response:** Allow dispute/clarify low ratings
5. **Time-Decay:** Recent ratings weigh more

**Key Insights:**
1. **Profile-Level Reviews (Critical):** Rate @beauty_ig, NOT Nguyễn Văn A
2. **Hybrid Rating:** Auto-calculate Performance từ metrics, brand rates 4/5 criteria
3. **Two-Tier Privacy:** Public + Private cho flexibility
4. **Mandatory + Reminders:** Ensure high completion rate (80%+)
5. **Quick Presets:** Excellent/Good/Average templates giảm friction
6. **Dispute Resolution:** Influencer can respond, admin mediates
7. **Time-Decay:** Recent reviews weigh more (favor current quality)

**Impact:**
- **Data-driven matching:** Future campaigns match dựa trên historical ratings
- **Quality improvement:** Influencers nhận feedback → Improve performance
- **Community value:** (Phase 3) Shared ratings benefit all AT Pool brands
- **Accountability:** Both brands và influencers accountable for quality

---

## Techniques Used

1. **Starbursting** - Ask Who/What/Where/When/Why/How cho review workflow
2. **User Journey Mapping** - Map toàn bộ workflow từ campaign complete → review display
3. **SCAMPER** - Creative variations (Substitute, Combine, Adapt, Modify, Put to other uses, Eliminate, Reverse)

---

## Context: Multi-Profile Architecture

### Critical Understanding

**Data Model:**
```
1 Influencer (Person) → Many Profiles (Social Accounts)

Example:
Influencer: Nguyễn Văn A
├─ @beauty_ig (Instagram, 500K followers)
├─ @beauty_fb (Facebook, 200K followers)
└─ @beauty_tiktok (TikTok, 1M followers)
```

**Why This Matters for Reviews:**

**✅ DO:**
- Rate PROFILE performance (@beauty_ig), NOT influencer (Nguyễn Văn A)
- Store reviews in `campaign_reviews` table linked to `profile_id`
- Display avg rating per profile: @beauty_ig (4.7/5), @beauty_fb (3.8/5)
- Allow different ratings per profile (same person, different performance)

**❌ DON'T:**
- Don't rate influencer as a whole
- Don't aggregate ratings across profiles
- Don't apply @beauty_ig rating to @beauty_fb

**Rationale:**
- Same person has different content strategies per platform
- @beauty_ig (visual, beauty) performs differently than @beauty_fb (community, lifestyle)
- Campaigns target specific profiles, not influencers

**Reference:** [Multi-Profile Data Model](./brainstorming-influencer-vs-profile-multi-account-2026-02-13.md)

---

## Ideas Generated (58 total)

### Category 1: Rating Form & Criteria (12 ideas)

#### Idea 1.1: 5-Criteria Rating System ⭐⭐⭐
**Source:** Starbursting (WHAT)
**Priority:** HIGH - MVP Core

**Criteria:**
1. **Content Quality** (1-5 stars): Creative, on-brand, visually appealing
2. **Professionalism** (1-5 stars): Attitude, responsiveness, collaboration
3. **Communication** (1-5 stars): Clarity, timeliness, proactive updates
4. **On-time Delivery** (1-5 stars): Met deadlines, no delays
5. **Performance** (1-5 stars): Reach, engagement, conversions vs targets

**Overall Rating:** Auto-calculated average of 5 criteria

**Why these 5?**
- Cover both **process** (Communication, On-time, Professional) and **results** (Content, Performance)
- Actionable feedback: Influencer knows what to improve
- Industry standard: Similar to Airbnb, Uber rating systems

---

#### Idea 1.2: Hybrid Auto+Manual Rating ⭐⭐⭐
**Source:** SCAMPER (Substitute)
**Priority:** HIGH - MVP Core

**Auto-Calculated (Objective):**
- **Performance Rating:** Auto từ campaign metrics
  ```typescript
  function calculatePerformanceRating(campaign) {
    const ctrScore = (actual_ctr / target_ctr) * 5;
    const reachScore = (actual_reach / target_reach) * 5;
    const conversionScore = (conversions / target_conversions) * 5;

    return Math.min(5, (ctrScore + reachScore + conversionScore) / 3);
  }
  ```
  - CTR 4% (target 3.5%) → 5/5 stars
  - Reach 480K (target 500K) → 4.8/5 stars

**Manual (Subjective):**
- Content Quality, Professionalism, Communication, On-time Delivery
- Brand rates based on qualitative assessment

**Benefit:**
- Reduce brand effort (only 4/5 criteria manual)
- Objective Performance rating → No bias
- Data-driven + Human judgment balance

---

#### Idea 1.3: Visual Score Cards
**Source:** Starbursting (HOW)
**Priority:** HIGH - MVP UI

**Design:**
```
┌─────────────────────────────────────────────────┐
│ Rate @beauty_ig Performance                     │
│ Campaign: Credit Card Q1 2026                   │
├─────────────────────────────────────────────────┤
│                                                 │
│ Content Quality        ⭐⭐⭐⭐⭐ 5/5          │
│ Professionalism        ⭐⭐⭐⭐⭐ 5/5          │
│ Communication          ⭐⭐⭐⭐☆ 4/5          │
│ On-time Delivery       ⭐⭐⭐⭐⭐ 5/5          │
│ Performance            ⭐⭐⭐⭐☆ 4/5 (Auto)  │
│                                                 │
│ Overall: 4.6/5 (auto-calculated)                │
│                                                 │
│ Review (Optional, max 500 chars):               │
│ ┌─────────────────────────────────────────────┐ │
│ │ Excellent content quality, delivered on     │ │
│ │ time. Engagement slightly below target      │ │
│ │ but overall great collaboration.            │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ Visibility:                                     │
│ ○ Public (visible to all brands)               │
│ ● Private (TCB internal only)                  │
│                                                 │
│ [Cancel] [Submit Review]                        │
└─────────────────────────────────────────────────┘
```

---

#### Idea 1.4: Quick Rating Presets ⭐⭐
**Source:** User Journey (Pain Point)
**Priority:** MEDIUM - UX Enhancement

**Problem:** Brand mất thời gian click 5 lần để rate 5 criteria

**Solution:** Quick templates
```
┌─────────────────────────────────────────────────┐
│ Quick Rate:                                     │
│                                                 │
│ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│ │ Excellent   │ │ Good        │ │ Average    │ │
│ │ ⭐⭐⭐⭐⭐│ │ ⭐⭐⭐⭐☆│ │ ⭐⭐⭐☆☆│ │
│ │ (All 5/5)   │ │ (All 4/5)   │ │ (All 3/5)  │ │
│ │ [Use]       │ │ [Use]       │ │ [Use]      │ │
│ └─────────────┘ └─────────────┘ └────────────┘ │
│                                                 │
│ Or customize manually below ↓                   │
└─────────────────────────────────────────────────┘
```

**Benefit:**
- 1 click vs 5 clicks → Faster submission
- Higher completion rate
- Can still customize if needed

---

#### Idea 1.5: Text Review (Optional, Mandatory if <3)
**Source:** Starbursting (WHAT)
**Priority:** HIGH - MVP Validation

**Rules:**
- Optional nếu rating ≥3 stars
- **Mandatory** nếu rating <3 stars (must explain why)
- Max 500 characters
- Character counter shows remaining

**Validation:**
```typescript
if (overallRating < 3 && !reviewText) {
  throw new Error("Low ratings (<3★) must include explanation");
}
```

**Benefit:**
- Low ratings have context → Influencer can improve
- Prevent unfair/lazy low ratings
- Optional for high ratings → Less friction

---

#### Idea 1.6: AI-Suggested Ratings
**Source:** SCAMPER (Substitute)
**Priority:** LOW - Phase 4 (ML required)

**Concept:** AI pre-fills ratings based on:
- Past brand ratings for this influencer
- Campaign performance vs benchmarks
- Communication logs analysis

**Brand reviews + adjusts** nếu cần

**Benefit:**
- Save time
- Consistency across campaigns
- Learn from patterns

---

#### Idea 1.7: Rating + Tags
**Source:** SCAMPER (Combine)
**Priority:** MEDIUM - Phase 3

**Tags Examples:**
- "credit-card-specialist"
- "great-visual-content"
- "slow-communication"
- "viral-potential"

**Use Case:**
- Brand searches: "credit-card-specialist" → Find profiles with that tag
- Niche categorization beyond generic categories

---

#### Idea 1.8: Rating + "Work Again?" Recommendation
**Source:** SCAMPER (Combine)
**Priority:** MEDIUM - Phase 3

**Question:** "Would you work with @beauty_ig again?"
- ○ Yes, definitely
- ○ Yes, for specific campaigns only (specify: __________)
- ○ Maybe
- ○ No

**Benefit:**
- Future matching signal
- Stronger than just star rating

---

#### Idea 1.9: Weighted Criteria by Campaign Type
**Source:** SCAMPER (Modify)
**Priority:** LOW - Phase 4

**Different campaign types → Different weights:**

**Awareness Campaign:**
- Content Quality: 40%
- Performance: 30%
- Professionalism: 15%
- Communication: 10%
- On-time: 5%

**Conversion Campaign:**
- Performance: 50%
- On-time: 30%
- Content Quality: 10%
- Communication: 5%
- Professionalism: 5%

**Benefit:** Context-aware ratings

---

#### Idea 1.10: Alternative Scales
**Source:** SCAMPER (Modify)
**Priority:** LOW - Future Consideration

**Options:**
- Current: 1-5 stars
- Option A: 1-10 scale (more granular)
- Option B: 3-tier (Below/Meets/Exceeds expectations)
- Option C: Thumbs up/down (simplest)

**Recommendation:** Keep 1-5 stars (industry standard)

---

#### Idea 1.11: Single Overall Rating (Simplified)
**Source:** SCAMPER (Eliminate)
**Priority:** LOW - Not Recommended

**Concept:** Remove 5-criteria breakdown, just 1 overall rating

**Benefit:** 10-second submission

**Trade-off:** Less actionable feedback

**Decision:** Keep 5-criteria (more valuable)

---

#### Idea 1.12: Rating + Performance Report Combined
**Source:** SCAMPER (Combine)
**Priority:** MEDIUM - Phase 3

**Combine in 1 view:**
- Star ratings (qualitative)
- Performance metrics (quantitative: reach, CTR, conversions)
- ROI calculation (revenue vs cost)

**Benefit:** Holistic view, data-backed ratings

---

### Category 2: Workflow & Triggers (8 ideas)

#### Idea 2.1: Trigger - Post-Campaign Complete ⭐⭐⭐
**Source:** Starbursting (WHEN)
**Priority:** HIGH - MVP Core

**Trigger Conditions:**
- Campaign status = 'completed'
- Deliverables submitted + approved
- Performance data available (7 days wait optional)

**Action:**
- "⭐ Rate Influencer" button appears in Campaign Dashboard
- Email notification: "Rate @beauty_ig performance"

---

#### Idea 2.2: Smart Reminders ⭐⭐
**Source:** User Journey (Pain Point)
**Priority:** HIGH - Ensure Completion

**Reminder Schedule:**
- **Day 3:** Email reminder "Don't forget to rate @beauty_ig"
- **Day 7:** Second reminder with escalation
- **Day 14:** Final reminder

**Implementation:**
```typescript
async function sendRatingReminders() {
  const campaigns = await db.query(`
    SELECT c.* FROM campaigns c
    LEFT JOIN campaign_reviews r ON c.id = r.campaign_id
    WHERE c.status = 'completed'
      AND r.id IS NULL
      AND c.completed_at < NOW() - INTERVAL '3 days'
  `);

  for (const campaign of campaigns) {
    await sendEmail({
      to: campaign.brand_user_email,
      subject: "⭐ Rate your influencer - Campaign completed",
      template: "rating_reminder",
      data: { campaign, profile }
    });
  }
}
```

---

#### Idea 2.3: Entry Points - Multiple Touchpoints
**Source:** Starbursting (WHERE)
**Priority:** HIGH - MVP UI

**Primary:**
- **Campaign Dashboard:** "⭐ Rate Influencer" button (most common)

**Secondary:**
- **Profile Detail Page:** "Add Review" button (ad-hoc anytime)
- **Post-Campaign Completion Page:** Inline rating form

---

#### Idea 2.4: 24h Edit Window ⭐
**Source:** Starbursting (WHEN)
**Priority:** MEDIUM - Phase 2

**Rules:**
- Can edit review within 24h after submission
- After 24h: Locked (can only dispute via support)

**Rationale:**
- Allow fix mistakes
- Prevent constant revisions (abuse)

---

#### Idea 2.5: Mandatory Before Next Campaign
**Source:** SCAMPER (Adapt - Uber model)
**Priority:** LOW - Too Strict for MVP

**Concept:** Cannot start next campaign until rate previous one

**Benefit:** 100% completion rate

**Trade-off:** Too strict, may annoy brands

**Decision:** Use soft mandatory (reminders) for MVP

---

#### Idea 2.6: Time-Based Prompt (7 days for performance data)
**Source:** Starbursting (WHEN)
**Priority:** LOW - Optional Enhancement

**Concept:** Wait 7 days after campaign complete để có full performance data

**Use Case:** CTR, conversions take time to stabilize

**Implementation:** Configurable per campaign type

---

#### Idea 2.7: Rating Form - Modal vs Inline
**Source:** User Journey
**Priority:** HIGH - MVP UI Decision

**Option A: Modal (Recommended)**
- Click "Rate" → Modal opens
- Lightweight, doesn't navigate away
- Can cancel easily

**Option B: Inline (Campaign Page)**
- Form embedded in Campaign Detail page
- Always visible (may clutter)

**Decision:** Modal for MVP (cleaner UX)

---

#### Idea 2.8: Bulk Rating (Multiple Campaigns)
**Source:** SCAMPER (Combine)
**Priority:** LOW - Phase 4

**Use Case:** Brand has 10 campaigns to rate

**UI:** Select multiple → Rate all at once

**Benefit:** Efficiency for high-volume brands

---

### Category 3: Privacy & Visibility (5 ideas)

#### Idea 3.1: Two-Tier Privacy System ⭐⭐⭐
**Source:** Starbursting (WHO can see)
**Priority:** HIGH - MVP Core

**Public Reviews:**
- Visible to: All brands (if AT Pool enabled), Influencer
- Use case: High ratings (4-5★), help community
- Example: "Great content, professional collaboration"

**Private Reviews:**
- Visible to: TCB team only
- Use case: Low ratings (<3★), sensitive feedback, brand-specific notes
- Example: "Great for credit cards, weak for savings campaigns"

**Default:** Private (safer, simpler for MVP)

**Implementation:**
```typescript
// Display logic
function getVisibleReviews(profileId, currentBrandId) {
  return db.query(`
    SELECT * FROM campaign_reviews
    WHERE profile_id = $1
      AND (
        visibility = 'public'
        OR (visibility = 'private' AND brand_id = $2)
      )
    ORDER BY created_at DESC
  `, [profileId, currentBrandId]);
}
```

---

#### Idea 3.2: Default Private for MVP
**Source:** User Journey (Pain Point - Decision Fatigue)
**Priority:** HIGH - MVP Simplification

**Rationale:**
- Safer (no accidental public shame)
- Simpler (one less decision)
- Add Public option in Phase 2

**UI:**
```
Visibility: ● Private (TCB only) [Default]
            ○ Public (coming soon)
```

---

#### Idea 3.3: Eliminate Public (Phase 1 Only Private)
**Source:** SCAMPER (Eliminate)
**Priority:** MEDIUM - MVP Consideration

**Approach:** Phase 1 = Private only, Phase 2 = Add Public

**Benefit:**
- Simpler MVP
- Less legal/compliance concerns
- Faster launch

**Trade-off:** No community value yet

---

#### Idea 3.4: Verified Campaign Badge
**Source:** SCAMPER (Adapt - Amazon)
**Priority:** LOW - Phase 3

**Concept:** Only brands who actually worked with influencer can review

**Badge:** "✓ Verified Campaign" (vs fake/spam reviews)

**Implementation:** Check `campaign_reviews.campaign_id` exists in `campaigns` table

---

#### Idea 3.5: AT Pool Cross-Brand Sharing
**Source:** Starbursting (WHO can see)
**Priority:** LOW - Phase 4 (requires AT Core integration)

**Concept:**
- TCB opts into AT Pool
- Public reviews shared across all brands in pool
- Other brands (VietcomBank, BIDV, etc.) can see TCB's reviews

**Benefit:** Community value, collective intelligence

---

### Category 4: Data Storage & Aggregation (7 ideas)

#### Idea 4.1: Profile-Level Review Storage ⭐⭐⭐
**Source:** Starbursting (WHERE store)
**Priority:** CRITICAL - Foundation

**Schema:**
```typescript
// campaign_reviews table
{
  id: UUID,
  campaign_id: UUID,
  profile_id: UUID, // @beauty_ig (NOT influencer_id)
  brand_id: UUID,

  // Ratings (1-5)
  overall_rating: float, // Auto-calculated avg
  content_quality: int,
  professionalism: int,
  communication: int,
  on_time_delivery: int,
  performance_rating: int, // Auto from metrics

  // Text review
  review_text: string | null,

  // Privacy
  visibility: 'public' | 'private',

  // Metadata
  created_at: timestamp,
  updated_at: timestamp,
  reviewer_user_id: UUID, // Who submitted

  // Status
  status: 'active' | 'disputed' | 'removed'
}
```

**Why profile_id (NOT influencer_id)?**
- Multi-profile model: 1 influencer → many profiles
- @beauty_ig (4.7/5) vs @beauty_fb (3.8/5) different performance
- Ratings specific to profile used in campaign

---

#### Idea 4.2: Aggregate to Profile ⭐⭐⭐
**Source:** Starbursting (WHERE display)
**Priority:** HIGH - MVP Core

**Update after each review:**
```sql
UPDATE social_profiles
SET
  avg_brand_rating = (
    SELECT AVG(overall_rating)
    FROM campaign_reviews
    WHERE profile_id = $1 AND status = 'active'
  ),
  total_reviews = (
    SELECT COUNT(*)
    FROM campaign_reviews
    WHERE profile_id = $1 AND status = 'active'
  ),

  -- Breakdown averages
  avg_content_quality = (SELECT AVG(content_quality) FROM ...),
  avg_professionalism = (SELECT AVG(professionalism) FROM ...),
  avg_communication = (SELECT AVG(communication) FROM ...),
  avg_on_time = (SELECT AVG(on_time_delivery) FROM ...),
  avg_performance = (SELECT AVG(performance_rating) FROM ...)

WHERE id = $1;
```

**Result:**
```
Profile: @beauty_ig
Overall Rating: ⭐ 4.7/5 (from 26 reviews)

Breakdown:
Content Quality:    4.8/5 ████████████░
Professionalism:    4.9/5 ████████████░
Communication:      4.5/5 ███████████░░
On-time Delivery:   4.8/5 ████████████░
Performance:        4.6/5 ████████████░
```

---

#### Idea 4.3: Real-Time Recalculation
**Source:** Starbursting (WHEN update)
**Priority:** HIGH - MVP Core

**Trigger:** After each review submission

**Implementation:**
```typescript
async function submitReview(review) {
  // 1. Save review
  await db.insert('campaign_reviews', review);

  // 2. Recalculate aggregate (immediate)
  await recalculateProfileRating(review.profile_id);

  // 3. Update Overall Score (includes rating component)
  await recalculateOverallScore(review.profile_id);

  // 4. Notify influencer
  await sendReviewNotification(review);
}
```

---

#### Idea 4.4: Time-Decay Weighted Average ⭐⭐
**Source:** SCAMPER (Modify)
**Priority:** MEDIUM - Phase 3

**Concept:** Recent ratings weigh more than old ratings

**Formula:**
```typescript
function calculateWeightedAvg(reviews) {
  const now = Date.now();

  const weighted = reviews.map(r => {
    const ageMonths = (now - r.created_at) / (30 * 24 * 60 * 60 * 1000);

    // Decay curve
    let weight = 1.0;
    if (ageMonths >= 6) weight = 0.8;
    if (ageMonths >= 12) weight = 0.5;
    if (ageMonths >= 24) weight = 0.3;

    return { rating: r.overall_rating, weight };
  });

  const sum = weighted.reduce((acc, w) => acc + (w.rating * w.weight), 0);
  const totalWeight = weighted.reduce((acc, w) => acc + w.weight, 0);

  return sum / totalWeight;
}
```

**Display:**
```
Profile: @beauty_ig
Overall Rating: ⭐ 4.7/5 (26 reviews, all time)

Last 6 months: ⭐ 4.9/5 (8 reviews) ↗️ Improving
Last 12 months: ⭐ 4.8/5 (15 reviews)
```

**Benefit:**
- Reflect current influencer quality
- Incentivize continuous improvement
- Identify rising stars vs declining

---

#### Idea 4.5: Rating Trends Chart
**Source:** User Journey (Learn & Improve)
**Priority:** MEDIUM - Phase 3

**Display:** 6-12 month trend chart

**Example:**
```
Rating Trend (Last 12 Months)

5.0 ┤                            ●
4.8 ┤              ●       ●  ●
4.6 ┤        ●  ●
4.4 ┤  ●  ●
4.2 ┤●
4.0 ┼────────────────────────────
    Jan  Feb  Mar  Apr  May  Jun
```

**Benefit:**
- See trajectory (rising/declining)
- Identify seasonal patterns

---

#### Idea 4.6: Performance Report Integration
**Source:** SCAMPER (Combine)
**Priority:** MEDIUM - Phase 3

**Combine ratings + metrics in 1 view:**

```
Campaign: Credit Card Q1 2026
Profile: @beauty_ig

┌─────────────────┬──────────────────┐
│ RATINGS         │ PERFORMANCE DATA │
├─────────────────┼──────────────────┤
│ Overall: 4.6/5  │ Reach: 480K      │
│ Content: 5/5    │ CTR: 3.2%        │
│ Professional: 5 │ Conversions: 145 │
│ Communication: 4│ ROI: 285%        │
│ On-time: 5/5    │ Revenue: 58M VND │
│ Performance: 4/5│ Cost: 20M VND    │
└─────────────────┴──────────────────┘
```

---

#### Idea 4.7: Review History Log (Audit Trail)
**Source:** User Journey (Dispute Resolution)
**Priority:** LOW - Phase 4

**Track changes:**
```typescript
review_history {
  review_id: UUID,
  changed_at: timestamp,
  changed_by: UUID,
  field: string, // 'overall_rating', 'review_text', etc.
  old_value: any,
  new_value: any,
  reason: string // 'influencer_dispute', 'brand_revision', etc.
}
```

**Use case:** Admin investigates dispute

---

### Category 5: Influencer Experience (9 ideas)

#### Idea 5.1: Multi-Channel Notifications ⭐⭐
**Source:** Starbursting (WHO notified)
**Priority:** HIGH - MVP Core

**Channels:**
1. **Email** (Primary)
   - Subject: "TCB rated your @beauty_ig: 4.6/5 ⭐"
   - Body: Summary + link to full review

2. **In-App** (Badge notification)
   - Header bell icon: "1 new review"

3. **Push Notification** (If mobile app)
   - "You received a new review from TCB"

**Email Template:**
```
Subject: TCB rated your @beauty_ig performance: 4.6/5 ⭐

Hi Nguyễn Văn A,

TCB has rated your @beauty_ig performance for the
"Credit Card Q1 2026" campaign:

Overall Rating: ⭐⭐⭐⭐⭐ 4.6/5

Breakdown:
• Content Quality:    5/5 ⭐⭐⭐⭐⭐
• Professionalism:    5/5 ⭐⭐⭐⭐⭐
• Communication:      4/5 ⭐⭐⭐⭐☆
• On-time Delivery:   5/5 ⭐⭐⭐⭐⭐
• Performance:        4/5 ⭐⭐⭐⭐☆

Review: "Excellent content quality, delivered on time.
Engagement slightly below target but overall great
collaboration."

[View Full Review] [Respond to Review]

Keep up the great work!
```

---

#### Idea 5.2: Reviews Tab in Influencer Portal ⭐⭐⭐
**Source:** User Journey (View Review)
**Priority:** HIGH - MVP Core

**Location:** Influencer Portal → @beauty_ig → Reviews tab

**Display:**
```
┌────────────────────────────────────────────────┐
│ Reviews for @beauty_ig                         │
│ Overall: ⭐ 4.7/5 (26 reviews)                 │
├────────────────────────────────────────────────┤
│                                                │
│ ┌──────────────────────────────────────────┐  │
│ │ Review #26 from TCB                      │  │
│ │ Campaign: Credit Card Q1 2026            │  │
│ │ Date: Feb 13, 2026                       │  │
│ │                                          │  │
│ │ Overall: ⭐⭐⭐⭐⭐ 4.6/5              │  │
│ │                                          │  │
│ │ Breakdown:                               │  │
│ │ • Content Quality:    5/5 ⭐⭐⭐⭐⭐  │  │
│ │ • Professionalism:    5/5 ⭐⭐⭐⭐⭐  │  │
│ │ • Communication:      4/5 ⭐⭐⭐⭐☆  │  │
│ │ • On-time Delivery:   5/5 ⭐⭐⭐⭐⭐  │  │
│ │ • Performance:        4/5 ⭐⭐⭐⭐☆  │  │
│ │                                          │  │
│ │ Review:                                  │  │
│ │ "Excellent content quality, delivered on │  │
│ │  time. Engagement slightly below target  │  │
│ │  but overall great collaboration."       │  │
│ │                                          │  │
│ │ [Respond]                                │  │
│ └──────────────────────────────────────────┘  │
│                                                │
│ [Load More Reviews...]                         │
└────────────────────────────────────────────────┘
```

---

#### Idea 5.3: Influencer Response System ⭐⭐
**Source:** User Journey (Dispute)
**Priority:** MEDIUM - Phase 3

**Use Cases:**

**Scenario 1: Clarification**
```
Brand Rating: Communication 2/5
Review: "Slow to respond"

[Respond] →

Response Form:
┌─────────────────────────────────────────────┐
│ Response to TCB (max 300 chars)             │
│ ┌─────────────────────────────────────────┐ │
│ │ I responded within 24h to all messages  │ │
│ │ as per SLA. The delay on Feb 5 was due │ │
│ │ to platform outage. Screenshot attached.│ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ Supporting Evidence (optional):             │
│ [Upload Screenshots]                        │
│                                             │
│ [Cancel] [Submit Response]                  │
└─────────────────────────────────────────────┘
```

**Scenario 2: Dispute**
```
Brand Rating: On-time 1/5
Review: "Missed deadline by 5 days"

Response:
"Original deadline was Feb 10. Brand requested
major revisions on Feb 9, extending timeline to
Feb 15. Deliverables submitted Feb 14. Email
trail attached."
```

**Workflow:**
1. Influencer submits response
2. Brand receives notification
3. Brand can revise rating (if valid)
4. If no resolution → Escalate to Admin
5. Admin reviews both sides → Final decision

**Schema:**
```typescript
review_responses {
  id: UUID,
  review_id: UUID,
  influencer_id: UUID,
  response_text: string,
  evidence_urls: string[],
  created_at: timestamp,

  // Admin resolution
  admin_reviewed: boolean,
  admin_decision: 'upheld' | 'revised' | 'removed',
  admin_notes: string,
  revised_rating: float | null
}
```

---

#### Idea 5.4: Insights Dashboard ⭐
**Source:** User Journey (Learn & Improve)
**Priority:** MEDIUM - Phase 3

**Display strengths + areas to improve:**

```
┌────────────────────────────────────────────────┐
│ Your Rating Insights (@beauty_ig)              │
├────────────────────────────────────────────────┤
│ Overall: ⭐ 4.7/5 (26 reviews)                 │
│                                                │
│ STRENGTHS ✅                                   │
│ • Content Quality:    4.9/5 (Top 10%)         │
│ • Professionalism:    4.8/5 (Excellent)       │
│ • On-time Delivery:   4.8/5 (Reliable)        │
│                                                │
│ AREAS TO IMPROVE ⚠️                            │
│ • Communication:      4.3/5 (-10% vs top)     │
│   💡 Tip: Respond within 12h, confirm         │
│      deliverables upfront, use professional   │
│      tone in all messages.                    │
│                                                │
│ • Performance:        4.5/5 (-5% vs avg)      │
│   💡 Tip: Analyze audience demographics,      │
│      optimize posting times, A/B test content │
│                                                │
│ TREND 📈                                       │
│ Last 6 months: 4.9/5 ↗️ +4% improvement       │
│ Keep it up!                                    │
└────────────────────────────────────────────────┘
```

---

#### Idea 5.5: Training Resources Auto-Send
**Source:** SCAMPER (Put to other uses)
**Priority:** LOW - Phase 4

**Concept:** Low-rated influencers → Auto-send training

**Example:**
```
Email: "Improve Your Communication Rating"

Your Communication rating is 3.2/5, below the
platform average of 4.0/5.

Here are some tips to improve:

1. Respond within 24h to all brand messages
2. Use professional tone (avoid slang)
3. Confirm deliverables upfront
4. Proactive updates on progress
5. Set clear expectations

[Download Communication Best Practices Guide]
```

---

#### Idea 5.6: Progress Tracking (Gamification)
**Source:** User Journey (Motivation)
**Priority:** LOW - Phase 4

**Display:**
```
Your Rating Journey

Feb 2025: 4.3/5 ⭐⭐⭐⭐☆
Jun 2025: 4.6/5 ⭐⭐⭐⭐⭐ ↗️ +7%
Dec 2025: 4.7/5 ⭐⭐⭐⭐⭐ ↗️ +2%

Next Milestone: 4.8/5 to unlock "Premium" badge 🏆
```

---

#### Idea 5.7: Leaderboard (Opt-in)
**Source:** SCAMPER (Put to other uses)
**Priority:** LOW - Phase 4

**Public leaderboard:** "Top 100 Finance Influencers"

**Gamification:**
- Gold Tier: 4.8+ avg rating
- Silver Tier: 4.5-4.7
- Bronze Tier: 4.0-4.4

**Benefit:** Motivation, competition

---

#### Idea 5.8: Review Visibility Toggle
**Source:** User Journey (Privacy)
**Priority:** LOW - Phase 3

**Allow influencer to hide low reviews from public profile?**

**Options:**
- Show all reviews (transparency)
- Hide reviews <3 stars (protect reputation)

**Trade-off:** Less transparency vs reputation protection

**Decision:** Show all (transparency wins)

---

#### Idea 5.9: Badge Notifications in Portal
**Source:** Starbursting (WHERE notify)
**Priority:** HIGH - MVP Core

**Header bell icon:**
```
🔔 (1)

Dropdown:
┌────────────────────────────────────┐
│ New review from TCB                │
│ @beauty_ig rated 4.6/5 ⭐          │
│ 2 hours ago                        │
│ [View Review]                      │
└────────────────────────────────────┘
```

---

### Category 6: Two-Way Rating (Reverse) (4 ideas)

#### Idea 6.1: Influencer Rates Brand ⭐
**Source:** SCAMPER (Reverse, Adapt - Airbnb)
**Priority:** LOW - Phase 4

**Concept:** Influencer also rates brand

**Criteria:**
1. **Brief Clarity** (1-5): Clear requirements, realistic expectations
2. **Payment Timeliness** (1-5): Paid on-time as agreed
3. **Collaboration** (1-5): Easy to work with, responsive, professional
4. **Creative Freedom** (1-5): Allowed creative input
5. **Overall** (1-5): Would work again

**Benefit:**
- Accountability for brands
- Attract better brands (high-rated brands get more applicants)
- Two-way transparency

---

#### Idea 6.2: Both Submit Before Reveal (Airbnb Model)
**Source:** SCAMPER (Adapt)
**Priority:** MEDIUM - Phase 4

**Workflow:**
1. Campaign completes
2. Both brand AND influencer submit ratings
3. Ratings hidden until BOTH submit
4. After both submit → Reveal to each other

**Benefit:** Prevent bias (brand fears low influencer rating → Inflates their rating)

---

#### Idea 6.3: Brand Rating Display in Brand Portal
**Source:** SCAMPER (Reverse)
**Priority:** LOW - Phase 4

**Display brand ratings in Brand Portal:**
```
TCB Marketing Team
Overall Rating: ⭐ 4.8/5 (from 45 influencers)

Breakdown:
• Brief Clarity:      4.9/5 ✅
• Payment Timeliness: 4.7/5 ✅
• Collaboration:      4.8/5 ✅
• Creative Freedom:   4.7/5 ✅

Top Review: "Best brand to work with. Clear briefs,
on-time payments, professional team."
```

**Benefit:** Attract top influencers

---

#### Idea 6.4: High-Rated Brands Get Priority
**Source:** SCAMPER (Reverse)
**Priority:** LOW - Phase 4

**Concept:** Brands with 4.5+ rating → Influencers prioritize their campaigns

**Gamification:** "Premium Brand" badge

---

### Category 7: Quality Control (6 ideas)

#### Idea 7.1: Validation Rules ⭐⭐⭐
**Source:** Starbursting (HOW validate)
**Priority:** HIGH - MVP Core

**Rules:**
1. At least 3/5 criteria must be rated
2. If overall rating <3 → Must provide review_text
3. No duplicate reviews (1 review per campaign)
4. Review text max 500 chars

**Implementation:**
```typescript
function validateReview(review) {
  // Rule 1: Min 3 criteria
  const ratedCount = [
    review.content_quality,
    review.professionalism,
    review.communication,
    review.on_time_delivery,
    review.performance_rating
  ].filter(r => r !== null).length;

  if (ratedCount < 3) {
    throw new Error("Must rate at least 3 criteria");
  }

  // Rule 2: Low rating needs explanation
  if (review.overall_rating < 3 && !review.review_text) {
    throw new Error("Low ratings (<3★) must include explanation");
  }

  // Rule 3: No duplicates
  const existing = await db.findOne('campaign_reviews', {
    campaign_id: review.campaign_id,
    brand_id: review.brand_id
  });

  if (existing) {
    throw new Error("You already rated this campaign");
  }

  // Rule 4: Text length
  if (review.review_text && review.review_text.length > 500) {
    throw new Error("Review text max 500 characters");
  }
}
```

---

#### Idea 7.2: Admin Review Outliers ⭐
**Source:** SCAMPER (Reverse)
**Priority:** MEDIUM - Phase 3

**Auto-flag suspicious ratings:**

**Outlier Detection:**
```typescript
async function flagOutliers(review) {
  // Get other reviews for same profile
  const otherReviews = await db.query(`
    SELECT AVG(overall_rating) as avg_rating
    FROM campaign_reviews
    WHERE profile_id = $1
      AND brand_id != $2
  `, [review.profile_id, review.brand_id]);

  const avgRating = otherReviews.avg_rating;
  const diff = Math.abs(review.overall_rating - avgRating);

  // If >2 stars difference → Flag for review
  if (diff > 2.0) {
    await db.insert('flagged_reviews', {
      review_id: review.id,
      reason: 'outlier',
      avg_rating: avgRating,
      this_rating: review.overall_rating,
      difference: diff
    });
  }
}
```

**Admin Portal:**
```
Flagged Reviews

Review #1234
Brand: TCB → Profile: @beauty_ig
Rating: 1/5 (Avg from others: 4.7/5) ⚠️ -3.7 difference
Reason: Possible bias or retaliation

[Investigate] [Approve] [Remove]
```

---

#### Idea 7.3: Upvote Helpful Reviews
**Source:** SCAMPER (Adapt - Amazon)
**Priority:** LOW - Phase 4

**Concept:** Other brands upvote helpful reviews

```
Review from TCB:
"Excellent content, delivered on time. Great for
credit card campaigns specifically."

👍 18 brands found this helpful
```

**Benefit:** Surface most useful reviews

---

#### Idea 7.4: Rating Prediction (Pre-Campaign)
**Source:** SCAMPER (Reverse)
**Priority:** LOW - Phase 4

**Concept:** Before campaign starts, predict likely rating

**Factors:**
- Influencer past avg: 4.7/5
- Brand strictness: TCB avg rates 4.2/5 (strict)
- Campaign difficulty: High (conversion campaign)

**Prediction:** 4.3/5 ± 0.5

**Benefit:** Set expectations, prevent mismatches

---

#### Idea 7.5: Anomaly Detection
**Source:** User Journey (Red Flags)
**Priority:** MEDIUM - Phase 3

**Auto-detect unusual patterns:**

**Examples:**
- Brand rates ALL influencers 1/5 (too harsh)
- Brand rates ALL influencers 5/5 (too lenient)
- Sudden rating drop for influencer (4.7 → 2.0)

**Action:** Flag for admin review

---

#### Idea 7.6: No Self-Reviews
**Source:** Quality Control
**Priority:** HIGH - MVP Core

**Rule:** Brand cannot review their own influencer accounts

**Validation:**
```typescript
if (review.brand_id === profile.influencer.brand_id) {
  throw new Error("Cannot review your own account");
}
```

---

### Category 8: Display & UI (7 ideas)

#### Idea 8.1: Avg Rating Badge in Profile Card ⭐⭐⭐
**Source:** Starbursting (WHERE display)
**Priority:** HIGH - MVP Core

**Search Results:**
```
┌────────────────────────────────────┐
│ @beauty_ig                         │
│ Instagram • 500K followers         │
│                                    │
│ ⭐ 4.7/5 (26 reviews)              │
│                                    │
│ Beauty, Lifestyle                  │
│ Engagement: 4.2%                   │
│ Rate: 10M VND/post                 │
│                                    │
│ [View Profile]                     │
└────────────────────────────────────┘
```

---

#### Idea 8.2: Reviews Section in Profile Detail ⭐⭐⭐
**Source:** Starbursting (WHERE display)
**Priority:** HIGH - MVP Core

**Profile Detail Page → Reviews Tab:**

```
┌────────────────────────────────────────────────┐
│ Reviews for @beauty_ig                         │
├────────────────────────────────────────────────┤
│ Overall: ⭐ 4.7/5 (26 reviews)                 │
│                                                │
│ Breakdown:                                     │
│ Content Quality:    4.9/5 ████████████░       │
│ Professionalism:    4.8/5 ████████████░       │
│ Communication:      4.5/5 ███████████░░       │
│ On-time Delivery:   4.8/5 ████████████░       │
│ Performance:        4.6/5 ████████████░       │
│                                                │
│ Recent Reviews (3 latest public):              │
│ ┌──────────────────────────────────────────┐  │
│ │ ⭐⭐⭐⭐⭐ 5/5 from Brand X           │  │
│ │ "Excellent collaboration!"                │  │
│ │ Jan 15, 2026                              │  │
│ └──────────────────────────────────────────┘  │
│                                                │
│ [View All 26 Reviews]                          │
└────────────────────────────────────────────────┘
```

---

#### Idea 8.3: Visual Progress Bars
**Source:** Starbursting (HOW display)
**Priority:** HIGH - MVP UI

**Use progress bars for visual clarity:**

```
Content Quality:    ⭐ 4.9/5 ████████████░  (Excellent)
Professionalism:    ⭐ 4.8/5 ████████████░  (Excellent)
Communication:      ⭐ 4.5/5 ███████████░░  (Good)
On-time Delivery:   ⭐ 4.8/5 ████████████░  (Excellent)
Performance:        ⭐ 4.6/5 ████████████░  (Good)
```

---

#### Idea 8.4: Side-by-Side Comparison View
**Source:** User Journey (Decision Making)
**Priority:** MEDIUM - Phase 2

**Compare 2-5 profiles:**

```
┌───────────────┬───────────────┬───────────────┐
│ @beauty_ig    │ @fashion_ig   │ @lifestyle_fb │
├───────────────┼───────────────┼───────────────┤
│ ⭐ 4.7/5      │ ⭐ 4.5/5      │ ⭐ 4.2/5      │
│ (26 reviews)  │ (18 reviews)  │ (12 reviews)  │
│               │               │               │
│ Content: 4.9  │ Content: 4.7  │ Content: 4.3  │
│ Prof: 4.8     │ Prof: 4.6     │ Prof: 4.1     │
│ Comm: 4.5     │ Comm: 4.8 ✅  │ Comm: 4.0     │
│ On-time: 4.8  │ On-time: 4.2  │ On-time: 4.5  │
│ Perf: 4.6     │ Perf: 4.1     │ Perf: 4.0     │
│               │               │               │
│ 500K followers│ 350K followers│ 200K followers│
│ 4.2% ER       │ 5.1% ER ✅    │ 2.8% ER       │
│ 10M VND/post  │ 8M VND/post ✅│ 5M VND/post ✅│
└───────────────┴───────────────┴───────────────┘

💡 Recommendation: @beauty_ig for content quality,
   @fashion_ig for communication & engagement
```

---

#### Idea 8.5: AI Insights in Comparison
**Source:** User Journey
**Priority:** LOW - Phase 4 (ML required)

**AI analysis:**
```
Comparing @beauty_ig vs @fashion_ig:

• @beauty_ig: Better content quality (+0.2★),
  higher professionalism (+0.2★), larger reach (+43%)

• @fashion_ig: Better communication (+0.3★),
  higher engagement rate (+22%), lower cost (-20%)

💡 For your Awareness Campaign:
   → @beauty_ig is 15% better match
   → Higher content quality aligns with campaign needs
   → Larger reach covers target audience better
```

---

#### Idea 8.6: Public Leaderboard
**Source:** SCAMPER (Put to other uses)
**Priority:** LOW - Phase 4

**Display:** "Top 100 Finance Influencers"

**Filters:**
- By niche (Finance, Beauty, Lifestyle)
- By platform (Instagram, Facebook, TikTok)
- By tier (Gold/Silver/Bronze)

---

#### Idea 8.7: Rating Badge in Campaign Dashboard
**Source:** Starburting (WHERE display)
**Priority:** HIGH - MVP Core

**Campaign List:**
```
Campaign: Credit Card Q1 2026
Profile: @beauty_ig
Status: Completed ✅
Rating: ⭐ 4.6/5 [View Review]
```

**Before rating:**
```
Campaign: Credit Card Q1 2026
Profile: @beauty_ig
Status: Completed ✅
[⭐ Rate Influencer] ← CTA
```

---

## Key Insights

### Insight 1: Profile-Level Reviews (NOT Person-Level) ⭐⭐⭐
**Impact:** CRITICAL | **Effort:** LOW

**Description:**
Reviews phải target PROFILE (@beauty_ig), không phải INFLUENCER (Nguyễn Văn A)

**Rationale:**
- Multi-profile architecture: 1 person có nhiều profiles với different performance
- @beauty_ig (IG) có thể excellent (4.8/5), @beauty_fb (FB) có thể average (3.5/5)
- Mixing ratings → Không fair, không accurate

**Implementation:**
```typescript
// Store in campaign_reviews
{
  profile_id: UUID, // @beauty_ig (NOT influencer_id)
  campaign_id: UUID,
  brand_id: UUID,
  overall_rating: float,
  // ...
}

// Aggregate to profile
UPDATE social_profiles
SET avg_brand_rating = AVG(reviews)
WHERE id = profile_id;
```

**Why it matters:**
- Foundation cho entire rating system
- Nếu sai từ đầu → Toàn bộ data bị pollute
- Matching accuracy phụ thuộc vào profile-specific ratings

---

### Insight 2: Hybrid Rating System (Auto + Manual) ⭐⭐⭐
**Impact:** HIGH | **Effort:** MEDIUM

**Description:**
Combine auto-calculated metrics với manual brand ratings

**Auto-Calculated (Objective):**
- **Performance Rating:** Auto từ campaign metrics (CTR, CVR, reach vs targets)
- Formula: `Performance = (actual / target) * 5`
- Example: CTR 4% (target 3.5%) → 5/5 stars

**Manual (Subjective):**
- Content Quality, Professionalism, Communication, On-time Delivery

**Benefit:**
- Objective + Subjective balance
- Reduce brand effort (only 4/5 criteria)
- Data-driven Performance → No bias

**Implementation:**
```typescript
// Auto-calculate Performance
function calculatePerformanceRating(campaign) {
  const ctrScore = (campaign.actual_ctr / campaign.target_ctr) * 5;
  const reachScore = (campaign.actual_reach / campaign.target_reach) * 5;
  const conversionScore = (campaign.conversions / campaign.target_conversions) * 5;

  return Math.min(5, (ctrScore + reachScore + conversionScore) / 3);
}

// Pre-fill in form
ratingForm.performance_rating = calculatePerformanceRating(campaign);
```

---

### Insight 3: Two-Tier Privacy (Public + Private) ⭐⭐
**Impact:** HIGH | **Effort:** LOW

**Description:**
Support both Public (community-shared) và Private (TCB-only) reviews

**Public Reviews:**
- High ratings (4-5★) → Help community
- Generic feedback
- Visible to: All brands (AT Pool), Influencer

**Private Reviews:**
- Low ratings (<3★) → Sensitive
- TCB-specific context
- Visible to: TCB team only

**Phase Approach:**
- **Phase 1 (MVP):** Private only (safer)
- **Phase 2:** Add Public option
- **Phase 3:** AT Pool integration

---

### Insight 4: Mandatory Rating + Smart Reminders ⭐⭐
**Impact:** MEDIUM | **Effort:** LOW

**Description:**
Make rating mandatory để ensure data completeness

**Soft Mandatory (Recommended):**
- "⭐ Rate Influencer" button after campaign complete
- Reminder emails: Day 3, Day 7, Day 14
- Can skip but persistent reminders

**Benefit:**
- High completion rate (80%+)
- Rich dataset for matching
- Consistent influencer feedback

**Implementation:**
```typescript
// Cron job: Daily reminder check
async function sendRatingReminders() {
  const campaigns = await db.query(`
    SELECT c.* FROM campaigns c
    LEFT JOIN campaign_reviews r ON c.id = r.campaign_id
    WHERE c.status = 'completed'
      AND r.id IS NULL
      AND c.completed_at < NOW() - INTERVAL '3 days'
  `);

  for (const campaign of campaigns) {
    await sendEmail({
      to: campaign.brand_user_email,
      subject: "⭐ Rate your influencer",
      template: "rating_reminder"
    });
  }
}
```

---

### Insight 5: Quick Presets giảm Friction ⭐⭐
**Impact:** MEDIUM | **Effort:** LOW

**Description:**
Provide quick templates: Excellent (5-5-5-5-5), Good (4-4-4-4-4), Average (3-3-3-3-3)

**Benefit:**
- 1 click vs 5 clicks → Faster
- Higher completion rate
- Can still customize

**UI:**
```
Quick Rate Templates:

[Excellent ⭐⭐⭐⭐⭐] [Good ⭐⭐⭐⭐☆] [Average ⭐⭐⭐☆☆]

Or customize manually ↓
```

---

### Insight 6: Influencer Response & Dispute Resolution ⭐
**Impact:** MEDIUM | **Effort:** MEDIUM

**Description:**
Allow influencers to respond to reviews, especially low ratings

**Use Cases:**
- **Clarification:** "I responded within 24h, here's proof"
- **Dispute:** "Deadline was extended per email trail"

**Workflow:**
1. Influencer submits response (300 chars + evidence)
2. Brand receives notification → Can revise rating
3. If no resolution → Admin mediates
4. Admin decision: Upheld / Revised / Removed

**Benefit:**
- Fair hearing
- Prevent unfair ratings
- Build trust

---

### Insight 7: Time-Decay Ratings favor Recent Performance ⭐
**Impact:** MEDIUM | **Effort:** MEDIUM

**Description:**
Weight recent ratings higher than old ratings

**Formula:**
```typescript
Age < 6 months  → 100% weight
Age 6-12 months → 80% weight
Age 12-24 months → 50% weight
Age > 24 months → 30% weight
```

**Display:**
```
Overall: ⭐ 4.7/5 (26 reviews, all time)
Last 6 months: ⭐ 4.9/5 ↗️ Improving
```

**Benefit:**
- Reflect current quality
- Incentivize continuous improvement
- Identify rising stars

---

## Statistics

- **Total ideas generated:** 58 ideas
- **Categories:** 8 categories
- **Key insights:** 7 insights
- **Techniques applied:** 3 (Starbursting, User Journey Mapping, SCAMPER)
- **Session duration:** 60 minutes

---

## Recommended Next Steps

### Immediate Actions (This Week)

1. **Review with Team:**
   - Share với Product Manager + Design team
   - Validate 5-criteria rating approach
   - Confirm privacy model (Private first, Public later)

2. **Technical Planning:**
   - Design `campaign_reviews` table schema
   - Design aggregate calculation logic
   - Design auto-calculate Performance rating algorithm

3. **UI/UX Design:**
   - Wireframe: Rating modal form
   - Wireframe: Reviews tab in Profile Detail
   - Wireframe: Reviews tab in Influencer Portal

### Phase 1 MVP Scope (Week 5-6)

**Must-Have Features:**
1. ✅ 5-Criteria rating form (Content, Professional, Communication, On-time, Performance)
2. ✅ Hybrid auto+manual (Performance auto-calculated)
3. ✅ Private reviews only (no Public yet)
4. ✅ Profile-level storage (NOT person-level)
5. ✅ Real-time aggregate updates
6. ✅ Multi-channel notifications (Email + In-app)
7. ✅ Reviews tab in Profile Detail + Influencer Portal
8. ✅ Validation rules (min 3 criteria, <3★ needs text)
9. ✅ Smart reminders (Day 3, 7, 14)
10. ✅ Visual score cards + progress bars

**Total:** 10 MVP features

### Phase 2 Enhancements (Week 7-8)

11. Quick rating presets (Excellent/Good/Average)
12. 24h edit window
13. Rating trends chart (6-month)
14. Side-by-side comparison view
15. Campaign Dashboard rating badge

### Phase 3 Advanced (Week 9+)

16. Public reviews (Two-tier privacy)
17. Influencer response system (dispute resolution)
18. Time-decay weighted average
19. Insights dashboard (strengths/weaknesses)
20. Training resources auto-send

### Phase 4 Future (Post-Launch)

21. Two-way rating (Influencer rates Brand)
22. AI-suggested ratings
23. Admin outlier detection
24. Public leaderboard
25. AT Pool cross-brand sharing

---

## Next Workflow

**Recommended:** Run `/bmad:create-story` to create Sprint stories

Break down 10 MVP features into user stories:
- Story 1: As a Brand, I can rate influencer profiles with 5 criteria
- Story 2: As a Brand, I can view aggregate ratings on profile cards
- Story 3: As an Influencer, I can view my profile ratings
- ...

Or run `/plan:parallel` to create implementation plan với parallel phases.

---

*Generated by BMAD Method v6 - Creative Intelligence*
*Techniques: Starbursting, User Journey Mapping, SCAMPER*
*Session duration: 60 minutes*
*Total ideas: 58 ideas across 8 categories*
*Key insights: 7 actionable recommendations*
