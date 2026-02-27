# Brainstorming: Advanced Filters cho Matching System

**Date:** 2026-02-01
**Context:** UX Design feedback - cần bộ lọc để filter bớt nhiễu trước khi matching
**Problem:** Matching API v1.0 chỉ có basic criteria, chưa đủ để loại bỏ influencers không phù hợp

---

## Problem Statement

**Current State (v1.0):**
- Criteria chỉ có: categories, budgetTiers, minEngagement
- Brand search trong Pool → picks 20 influencers → score all 20
- **Issue:** 20 influencers có thể không phù hợp về:
  - Demographics (audience location, age, gender)
  - Content quality (posting frequency, content type)
  - Brand safety (controversial content, fake followers)
  - Collaboration history (đã từng làm việc với competitors?)

**Desired State:**
- Pre-filtering TRƯỚC KHI score để loại bỏ nhiễu
- Chỉ score những influencers có khả năng cao match
- Tăng quality của matching results

---

## Use Cases

### Use Case 1: Geographic Targeting

**Scenario:** Brand Techcombank muốn campaign chỉ target audience Việt Nam

**Current Problem:**
- Pool Search không filter theo audience location
- Brand phải manually review 100 influencers
- Có thể pick influencer có 80% audience từ Philippines

**Desired Filter:**
- Audience Location: Vietnam ≥70%
- Exclude influencers với majority audience ngoài VN

### Use Case 2: Audience Demographics

**Scenario:** Campaign beauty products cho phụ nữ 25-35 tuổi

**Current Problem:**
- Không biết audience demographics của influencer
- Có thể pick influencer có 90% audience nam giới
- Wasted budget on wrong target

**Desired Filters:**
- Audience Gender: Female ≥60%
- Audience Age: 25-35 ≥50%

### Use Case 3: Content Quality

**Scenario:** Brand cần influencer post regularly, engagement thật

**Current Problem:**
- Influencer có 100K followers nhưng post 1 lần/tháng
- Engagement rate cao nhưng có thể fake (bot comments)
- Không biết content type (video, image, carousel)

**Desired Filters:**
- Posting Frequency: ≥4 posts/month
- Audience Authenticity Score: ≥80% (detect fake followers)
- Content Type: Video preferred

### Use Case 4: Brand Safety

**Scenario:** Bank cần influencers "sạch", không controversial

**Current Problem:**
- Không check past controversies
- Influencer có thể có scandal gần đây
- Risk cho brand reputation

**Desired Filters:**
- Brand Safety Score: ≥90% (no controversial content)
- Exclude keywords: politics, gambling, adult content
- Verified account only

### Use Case 5: Exclusion List

**Scenario:** Brand đã làm việc với influencer, không muốn duplicate

**Current Problem:**
- Không biết influencer đã collaborate với brand trước đó
- Không biết influencer đang làm việc với competitors

**Desired Filters:**
- Exclude: Influencers đã hợp tác trong 6 tháng qua
- Exclude: Influencers đang promote competitor brands
- Whitelist/Blacklist capability

---

## Proposed Filter Categories

### Category 1: Audience Demographics

**Filters:**
1. **Audience Location (Top Countries)**
   - Vietnam: [0-100]% (slider)
   - Thailand: [0-100]%
   - Multi-select countries với threshold

2. **Audience Age Distribution**
   - 13-17: [0-100]%
   - 18-24: [0-100]%
   - 25-34: [0-100]% ← Target
   - 35-44: [0-100]%
   - 45+: [0-100]%

3. **Audience Gender**
   - Female: [0-100]%
   - Male: [0-100]%
   - Other: [0-100]%

4. **Audience Interests** (if available)
   - Beauty & Cosmetics
   - Technology
   - Fashion
   - Food & Dining
   - Travel

**Data Source:**
- influence-meter crawls demographics từ platform APIs
- Instagram Insights, YouTube Analytics, TikTok Creator Marketplace

**API Extension:**
```json
POST /v1/influencers/search
{
  "platform": "instagram",
  "filters": {
    "audienceDemographics": {
      "location": {
        "VN": {"min": 70, "max": 100}
      },
      "age": {
        "25-34": {"min": 40}
      },
      "gender": {
        "female": {"min": 60}
      }
    }
  }
}
```

---

### Category 2: Content Quality

**Filters:**
1. **Posting Frequency**
   - Posts per month: [1-30] (slider)
   - Last post within: [7/14/30] days

2. **Content Type**
   - Video: Yes/No
   - Image: Yes/No
   - Carousel: Yes/No
   - Reels/Shorts: Yes/No

3. **Average Performance**
   - Avg views per post: [min-max]
   - Avg likes per post: [min-max]
   - Avg comments per post: [min-max]

4. **Engagement Quality**
   - Comment-to-like ratio: [0-1] (high ratio = real engagement)
   - Reply rate to comments: [0-100]%

**Data Source:**
- influence-meter analyzes recent posts (last 30 days)
- Calculate metrics từ post history

**API Extension:**
```json
POST /v1/influencers/search
{
  "filters": {
    "contentQuality": {
      "postingFrequency": {"min": 4, "period": "month"},
      "lastPostWithin": 14,
      "contentTypes": ["video", "reels"],
      "avgViews": {"min": 10000}
    }
  }
}
```

---

### Category 3: Brand Safety

**Filters:**
1. **Brand Safety Score**
   - Overall score: [0-100] (influence-meter calculates)
   - Based on: controversial content detection, toxic language, fake followers

2. **Content Moderation**
   - Exclude keywords: [politics, gambling, adult]
   - Must be verified account: Yes/No

3. **Authenticity**
   - Fake followers percentage: [0-100]% (lower is better)
   - Suspicious engagement: Yes/No (detect bot comments)

4. **Past Controversies**
   - Scandal-free period: [3/6/12] months
   - Negative sentiment score: [0-100]% (lower is better)

**Data Source:**
- influence-meter uses ML models:
  - Text classification for controversial content
  - Fake follower detection algorithms
  - Sentiment analysis on comments

**API Extension:**
```json
POST /v1/influencers/search
{
  "filters": {
    "brandSafety": {
      "score": {"min": 90},
      "verified": true,
      "excludeKeywords": ["politics", "gambling"],
      "fakeFollowers": {"max": 10}
    }
  }
}
```

---

### Category 4: Collaboration History

**Filters:**
1. **Past Collaborations**
   - Exclude: Worked with THIS brand in last [3/6/12] months
   - Exclude: Currently promoting competitor brands
   - Whitelist: Preferred influencers only

2. **Campaign Performance**
   - Past campaign ROI: [min] %
   - Past campaign engagement: [min] %

3. **Availability**
   - Not currently in exclusive contract
   - Available for collaboration start date

**Data Source:**
- at-core stores collaboration history
- influence-meter tracks brand mentions (competitor analysis)

**API Extension:**
```json
POST /v1/influencers/search
{
  "filters": {
    "collaboration": {
      "excludeRecentPartners": true,
      "excludePeriod": 6,
      "excludeCompetitors": ["Brand A", "Brand B"],
      "whitelist": ["influencer_id_1", "influencer_id_2"]
    }
  }
}
```

---

### Category 5: Platform-Specific

**Instagram:**
- Story engagement rate
- Reel performance
- IGTV usage

**YouTube:**
- Video length preference
- Upload frequency
- Subscriber retention rate

**TikTok:**
- Viral video count (>1M views)
- Sound usage trends
- Hashtag performance

**Facebook:**
- Page vs Profile
- Group engagement
- Live stream frequency

**API Extension:**
```json
POST /v1/influencers/search
{
  "platform": "instagram",
  "filters": {
    "platformSpecific": {
      "storyEngagement": {"min": 5},
      "reelPerformance": {"min": 10000}
    }
  }
}
```

---

## Filter UI/UX Design

### Option 1: Sidebar Filters (Desktop)

```
┌────────────────────────────────────────────────┐
│ Search Influencers                             │
├────────────┬───────────────────────────────────┤
│ FILTERS    │ RESULTS (245 influencers)         │
│            │                                   │
│ 📍 Location│ ┌───────────┐ ┌───────────┐     │
│ ☑️ Vietnam │ │ @beauty   │ │ @tech     │     │
│   70-100%  │ │ 125K      │ │ 215K      │     │
│            │ │ Score: 85 │ │ Score: 82 │     │
│ 👥 Age     │ └───────────┘ └───────────┘     │
│ ☑️ 25-34   │                                   │
│   40%+     │ ┌───────────┐ ┌───────────┐     │
│            │ │ @fashion  │ │ @lifestyle│     │
│ 👤 Gender  │ └───────────┘ └───────────┘     │
│ ☑️ Female  │                                   │
│   60%+     │ [...more results...]             │
│            │                                   │
│ 📊 Content │                                   │
│ Posts/mo:  │ [Load More]                       │
│ ━━●━━━ 4+  │                                   │
│            │                                   │
│ ✓ Safety   │                                   │
│ Score 90+  │                                   │
│ ☑️ Verified│                                   │
│            │                                   │
│ [Reset]    │                                   │
│ [Apply]    │                                   │
└────────────┴───────────────────────────────────┘
```

### Option 2: Expandable Sections (Mobile)

```
┌─────────────────────┐
│ Search Influencers  │
├─────────────────────┤
│ 📍 Audience Location▼│ Collapsed
│                     │
│ 👥 Age Distribution▼│
│                     │
│ 👤 Gender ▼         │
│                     │
│ 📊 Content Quality ▶│ Expanded
│ ┌─────────────────┐ │
│ │ Posts/month:    │ │
│ │ ━━●━━━ 4+       │ │
│ │                 │ │
│ │ Last post:      │ │
│ │ ☑️ Within 14d   │ │
│ │                 │ │
│ │ Content type:   │ │
│ │ ☑️ Video        │ │
│ │ ☑️ Reels        │ │
│ └─────────────────┘ │
│                     │
│ ✓ Brand Safety ▶    │
│                     │
│ 🚫 Exclusions ▶     │
│                     │
├─────────────────────┤
│ [Reset] [Apply]     │
└─────────────────────┘
```

### Option 3: Multi-Step Wizard

```
Step 1: Basic Criteria
┌─────────────────────────────┐
│ What are you looking for?   │
│                             │
│ Categories:                 │
│ ☑️ Beauty  ☑️ Fashion       │
│ □ Tech    □ Lifestyle       │
│                             │
│ Budget Tier:                │
│ ☑️ Micro   ☑️ Mid           │
│ □ Macro   □ Mega            │
│                             │
│ [Next: Audience →]          │
└─────────────────────────────┘

Step 2: Audience Targeting
┌─────────────────────────────┐
│ Who is your target audience?│
│                             │
│ Location: Vietnam 70%+      │
│ Age: 25-34 (40%+)           │
│ Gender: Female (60%+)       │
│                             │
│ [← Back]  [Next: Quality →] │
└─────────────────────────────┘

Step 3: Quality & Safety
┌─────────────────────────────┐
│ Quality requirements        │
│                             │
│ Posting: 4+ per month       │
│ Brand Safety: 90+           │
│ Verified: Yes               │
│                             │
│ [← Back]  [Search →]        │
└─────────────────────────────┘
```

---

## Implementation Strategy

### Phase 1: Backend Data (Week 1-2)

**influence-meter tasks:**
1. Crawl audience demographics từ platform APIs
2. Calculate brand safety score (ML model)
3. Detect fake followers (algorithm)
4. Store in profile schema:
```javascript
{
  demographics: {
    location: {VN: 75, TH: 15, SG: 10},
    age: {"18-24": 30, "25-34": 50, "35-44": 20},
    gender: {female: 70, male: 30}
  },
  contentQuality: {
    postingFrequency: 8, // per month
    lastPostDate: "2026-02-01",
    avgViews: 15000,
    commentLikeRatio: 0.12
  },
  brandSafety: {
    score: 95,
    fakeFollowers: 5,
    controversialContent: false
  }
}
```

**at-core tasks:**
1. Add collaboration history tracking
2. Store whitelist/blacklist per partner
3. Track competitor brand mentions

### Phase 2: Search API Enhancement (Week 3)

**New endpoint:**
```
POST /v1/influencers/search
{
  "platform": "instagram",
  "basicCriteria": {
    "categories": ["beauty", "fashion"],
    "minFollowers": 10000,
    "maxFollowers": 500000
  },
  "advancedFilters": {
    "demographics": {...},
    "contentQuality": {...},
    "brandSafety": {...},
    "collaboration": {...}
  },
  "sort": "relevance",
  "limit": 100
}
```

**Response:**
```json
{
  "results": [
    {
      "platform": "instagram",
      "externalId": "beauty_guru_123",
      "name": "Beauty Guru",
      "relevanceScore": 92,
      "matchedFilters": {
        "demographics": "✓",
        "quality": "✓",
        "safety": "✓"
      }
    }
  ],
  "meta": {
    "total": 245,
    "filtered": 245,
    "excluded": 755
  }
}
```

### Phase 3: UI Integration (Week 4)

**at-core UI:**
1. Add filter sidebar/panel
2. Implement filter components:
   - Range sliders (age %, location %)
   - Checkboxes (verified, content types)
   - Dropdowns (posting frequency)
3. Real-time filter count ("245 results")
4. "Applied filters" chips with [X] to remove

### Phase 4: Matching API Update (Week 5)

**v1.1 Enhancement:**
- Accept `appliedFilters` in request
- Use filters for score adjustment:
  - Perfect demographic match → +10 bonus points
  - High brand safety → +5 bonus points
  - Good content quality → +5 bonus points

**Request:**
```json
POST /v1/matching/score
{
  "profile": {...},
  "criteria": {
    "categories": ["beauty"],
    "budgetTiers": ["micro"]
  },
  "appliedFilters": {
    "demographics": {
      "location": {"VN": {"min": 70}}
    },
    "brandSafety": {
      "score": {"min": 90}
    }
  }
}
```

**Response with bonus:**
```json
{
  "scores": {
    "finalScore": 90.5, // 85.5 base + 5 bonus
    "categoryScore": 90,
    "tierScore": 85,
    "engagementScore": 82,
    "bonusPoints": {
      "demographics": 3,
      "brandSafety": 2
    }
  }
}
```

---

## Data Requirements Analysis

### What influence-meter ALREADY HAS:
- ✅ Basic profile: name, handle, followers, engagement
- ✅ Platform data: posts, views, likes, comments
- ✅ Category classification (from bio/content)

### What influence-meter NEEDS TO ADD:

**Critical (Must Have):**
1. **Audience Location** - From platform APIs
   - Instagram Insights: Audience top countries
   - YouTube Analytics: Geography
   - TikTok: Audience territories
   - **Effort:** Medium (API integration)

2. **Audience Age & Gender** - From platform APIs
   - Available in creator analytics
   - **Effort:** Medium (API integration)

3. **Posting Frequency** - Calculate from post history
   - Already have post data, just aggregate
   - **Effort:** Low (calculation)

4. **Verified Status** - From platform API
   - Simple boolean field
   - **Effort:** Low (already crawling)

**Important (Should Have):**
1. **Brand Safety Score** - ML model
   - Text classification for controversial content
   - **Effort:** High (ML model training)

2. **Fake Follower Detection** - Algorithm
   - Analyze follower growth patterns
   - Comment quality analysis
   - **Effort:** High (algorithm development)

3. **Content Type Distribution** - Analyze posts
   - Classify: video, image, carousel, reels
   - **Effort:** Medium (classification)

**Nice to Have:**
1. **Audience Interests** - Platform APIs (limited availability)
2. **Sentiment Analysis** - ML model
3. **Competitor Tracking** - Brand mention detection

---

## PRD Gap Analysis

### Current PRD Coverage:

**v1.0 PRD includes:**
- ✅ Basic matching criteria (categories, tiers, engagement)
- ✅ Scoring algorithm (3 dimensions)
- ✅ Batch processing

**v1.0 PRD MISSING:**
- ❌ Audience demographics filtering
- ❌ Content quality requirements
- ❌ Brand safety considerations
- ❌ Exclusion lists
- ❌ Advanced search filters

### Recommendation: Create v1.1 PRD

**Focus areas for v1.1:**
1. **Advanced Filtering System**
   - Audience demographics (location, age, gender)
   - Content quality metrics
   - Brand safety scoring
   - Collaboration history

2. **Enhanced Matching Algorithm**
   - Include demographic fit in scoring
   - Adjust scores based on filter match
   - Bonus points for perfect matches

3. **Search API Overhaul**
   - Replace simple Pool Search với advanced filter engine
   - Real-time filter result counts
   - Saved filter presets

**Effort Estimate:**
- Research & PRD: 1 week
- Backend data collection: 2 weeks
- Search API enhancement: 1 week
- Matching algorithm update: 1 week
- UI implementation: 2 weeks
- Testing: 1 week
- **Total: 8 weeks (2 months)**

---

## Immediate Next Steps

### Option 1: Quick Win - Basic Filters First (Recommended)

**Week 1-2: Implement "must have" filters only**
- Audience Location (từ platform API)
- Verified status (already available)
- Posting frequency (calculate from posts)

**Week 3: Integrate vào UI**
- Simple filter sidebar
- 3 filters above

**Week 4: Test & Release v1.1**

**Benefits:**
- Fast delivery (1 month)
- Immediate value for users
- Foundation for advanced filters later

### Option 2: Comprehensive Approach

**Month 1-2: Full v1.1 implementation**
- All filters (demographics, quality, safety)
- ML models for brand safety
- Enhanced matching algorithm
- Complete UI overhaul

**Benefits:**
- Complete solution
- Better long-term architecture

**Risks:**
- Longer time to market
- More complex, higher risk

---

## Recommendation

**Phased Approach:**

**v1.1 (Quick Win - 1 month):**
- Audience Location filter (VN ≥70%)
- Posting Frequency filter (≥4/month)
- Verified status filter
- Basic exclusion list (manual)

**v1.2 (Enhanced - 2 months):**
- Audience Age & Gender
- Content Quality metrics
- Brand Safety Score (basic)

**v2.0 (Advanced - 3 months):**
- ML-based Brand Safety
- Fake Follower Detection
- Competitor Tracking
- Audience Interests

---

## Conclusion

**Yes, PRD chưa đủ mạnh!**

Current v1.0 PRD focuses on **scoring** but missing **pre-filtering**.

**Action Items:**
1. ✅ Create v1.1 PRD với advanced filters
2. ✅ Update UX design với filter UI
3. ✅ Update Tech Spec với data requirements
4. ✅ Plan phased rollout (v1.1 → v1.2 → v2.0)

**Recommended immediate workflow:**
```bash
/bmad:prd  # Create PRD v1.1 - Advanced Filtering System
```

**Follow-up:**
```bash
/bmad:tech-spec  # Tech spec cho filter implementation
/bmad:sprint-planning  # Plan sprints cho v1.1
```

---

*Document created: 2026-02-01*
*Follow-up: Create PRD v1.1 với advanced filtering requirements*
