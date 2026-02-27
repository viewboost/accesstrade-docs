# Brainstorming: Brand Feedback Storage - Profile vs Influencer Level

**Date:** 2026-02-13
**Objective:** Xác định nơi lưu trữ tối ưu cho negative brand feedback (thái độ hợp tác, content quality)
**Context:** Multi-profile architecture (1 Influencer → Many Profiles), post-campaign brand ratings
**Methods:** SWOT Analysis, Six Thinking Hats, Starbursting
**Expert Perspective:** Industry best practices từ Upwork, Airbnb, Uber

---

## Executive Summary

**Kết luận:** Áp dụng **HYBRID STORAGE** - phân loại feedback theo bản chất:

| Feedback Type | Storage Level | Examples | Visibility |
|---------------|---------------|----------|------------|
| **Performance** | Profile-level (`social_profiles`) | Content quality, creativity, platform expertise, visual quality | Public (với consent) |
| **Behavior** | Person-level (`influencers`) | Cooperation attitude, communication, professionalism, reliability | Private (admin only) |

**Rationale:**
- "Content không sáng tạo" → Profile-specific (có thể content TikTok kém nhưng Instagram tốt)
- "Thái độ hợp tác không tốt" → Person characteristic (Nguyễn Văn A khó tính ở mọi platform)

---

## Brainstorming Context

### Multi-Profile Architecture

```
1 Influencer (PERSON) → N Social Profiles (ACCOUNTS)

Nguyễn Văn A (influencers table)
   ├── @beauty_ig (Instagram) → social_profiles
   ├── @beauty_fb (Facebook) → social_profiles
   └── @beauty_tiktok (TikTok) → social_profiles
```

**Brand Workflow:**
1. **Phase 2 (Discovery):** Brand searches & browses **PROFILES** (not influencers)
2. **Phase 3 (Campaign):** Brand works with **SPECIFIC PROFILE** (@beauty_ig)
3. **Post-Campaign:** Brand rates **BOTH** profile performance AND person behavior

---

## Technique 1: SWOT Analysis

### Option A: Profile-Level Only

**Strengths:**
- ✅ Granular ratings per platform
- ✅ Fair for influencers with multi-account (content quality khác nhau)
- ✅ Matches brand workflow (brand works with profiles)

**Weaknesses:**
- ❌ Behavioral attributes (cooperation, communication) không phải profile-specific
- ❌ Influencer có thể "profile-hop" để rửa sạch reputation
- ❌ Khó detect bad actors có nhiều accounts

**Opportunities:**
- Platform-specific content benchmarks
- A/B testing content strategies

**Threats:**
- Gaming the system (tạo profile mới khi bị rate thấp)

---

### Option B: Influencer-Level Only

**Strengths:**
- ✅ Prevent profile-hopping exploitation
- ✅ Hợp lý cho behavioral ratings (person-level traits)
- ✅ Easier aggregation across platforms

**Weaknesses:**
- ❌ Không công bằng khi content quality khác nhau giữa platforms
- ❌ Không match với brand workflow (brand chọn profile, không phải influencer)
- ❌ Mất đi granularity về platform expertise

**Opportunities:**
- Simplified data model
- Easier influencer reputation scoring

**Threats:**
- Influencer với 1 profile tốt + 1 profile kém → unfair averaging

---

### Option C: HYBRID (Recommended) ⭐⭐⭐

**Strengths:**
- ✅ Best of both worlds - granular + prevention
- ✅ Matches real-world: Performance varies by profile, behavior is consistent
- ✅ Follows industry best practices (Upwork + Airbnb model)
- ✅ Flexible filtering for brand discovery

**Weaknesses:**
- ⚠️ Slightly more complex data model
- ⚠️ Brand cần hiểu sự khác biệt (education needed)

**Opportunities:**
- Combined scoring algorithm (60% performance + 40% behavior)
- Smart brand-influencer matching
- Time-weighted behavior recovery path

**Threats:**
- Data quality depends on brand understanding the categorization

**Winner:** Option C (Hybrid) - minimizes weaknesses, maximizes opportunities

---

## Technique 2: Six Thinking Hats

### White Hat (Facts & Data)

**Industry benchmarks:**
- **Upwork:** Rates PEOPLE (freelancers) on communication, professionalism → Person-level
- **Airbnb:** Rates PROPERTIES (listings) on cleanliness, amenities → Property-level
- **Uber:** HYBRID - Driver behavior + Car comfort

**Our data model:**
- `influencers` table → Person-level attributes
- `social_profiles` table → Account-level attributes
- `campaign_performance` table → Campaign-specific results

**Fact:** Content quality CAN vary by platform. Behavioral traits typically DO NOT.

---

### Red Hat (Emotions & Intuition)

**Brand perspective:**
> "Tôi làm việc với @beauty_ig, không phải với Nguyễn Văn A. Tôi muốn rate profile mà tôi collaborate."

**Influencer perspective:**
> "Thái độ hợp tác không tốt là đánh giá về TÔI (người), không phải về @beauty_ig (account). Không công bằng nếu tạo account mới mà vẫn bị gán nhãn xấu."

**Platform perspective:**
> "Chúng tôi cần bảo vệ brands khỏi bad actors, nhưng cũng cần fair cho influencers improve."

**Insight:** Emotional fairness đòi hỏi phân biệt rõ Performance (profile) vs Behavior (person)

---

### Black Hat (Risks & Caution)

**Legal risks:**
- ❌ Public negative ratings về behavior → potential defamation lawsuits
- ❌ GDPR/PDPA compliance - personal data về behavior cần private
- ⚠️ Influencer có quyền kiểm soát reputation data

**Business risks:**
- ❌ Profile-only ratings → influencers game the system (tạo account mới)
- ❌ Influencer-only ratings → unfair penalization for multi-account users
- ❌ Lack of guidelines → brands rate incorrectly (mix performance + behavior)

**Recommendation:** Behavior ratings must be PRIVATE by default. Performance ratings can be public with consent.

---

### Yellow Hat (Benefits & Opportunities)

**Hybrid approach benefits:**
- ✅ **Better brand matching:** Filter by both performance AND behavior
- ✅ **Fair for influencers:** Content quality rated per profile, behavior rated as person
- ✅ **Platform integrity:** Prevent reputation laundering via new profiles
- ✅ **Data richness:** Detailed insights for both stakeholders
- ✅ **Scalable:** Works as influencer adds more profiles over time

**Revenue opportunities:**
- Premium influencers with high scores command higher rates
- Platform can offer "verified professional" badges for consistent high behavior scores
- Data insights for influencer training programs

---

### Green Hat (Creativity & Alternatives)

**Creative solutions:**
1. **Time-weighted behavior scoring** → Người có thể improve, gần đây quan trọng hơn
2. **Influencer improvement path** → Suggestions để tăng behavior score
3. **Anonymous aggregated feedback** → Show trends without exposing individual brands
4. **Peer feedback** → Influencers rate brands (2-way accountability)
5. **Dispute resolution** → Allow influencers to contest unfair ratings with evidence

**Novel idea:** "Behavior Score Recovery Missions"
```typescript
interface RecoveryMission {
  requirement: "Complete 3 campaigns with 5-star communication within 60 days",
  reward: "Remove 1 behavior_flag from your record",
  status: "in_progress" | "completed" | "failed",
}
```

---

### Blue Hat (Process & Control)

**Implementation phases:**
1. **Phase 1 (MVP):** Private behavior ratings only, no public display
2. **Phase 2:** Add performance ratings, allow influencer to opt-in for public display
3. **Phase 3:** Weighted scoring algorithms, recovery paths
4. **Phase 4:** Advanced analytics, predictive matching

**Quality control:**
- Brand feedback form with clear guidelines (tooltips, examples)
- Automated checks for suspicious rating patterns (all 1-star or all 5-star)
- Quarterly review of rating distributions
- Influencer can request rating review if unfair

---

## Technique 3: Starbursting (6W Questions)

### WHO?

**Who rates what?**
- Brands rate both Performance (profile) AND Behavior (person)

**Who sees the ratings?**
- Performance: Public (if influencer consents), or private
- Behavior: Private (admin only), influencer sees aggregated score without notes

**Who benefits?**
- Brands: Better discovery & risk mitigation
- Influencers: Fair ratings, improvement paths
- Platform: Trust, quality control

**Who is at risk?**
- Bad actors: Can't escape reputation via profile-hopping
- Good influencers: Protected from unfair public shaming

---

### WHAT?

**What is being rated?**

**Performance (Profile-level):**
- Content quality & creativity
- Platform expertise
- Visual quality
- Engagement delivery
- Deadline adherence (content delivery)

**Behavior (Person-level):**
- Cooperation attitude
- Communication responsiveness
- Professionalism
- Reliability
- Willingness to iterate on feedback

**What is NOT rated?**
- Personal characteristics (age, gender, ethnicity) → discrimination risk
- Follower count growth → not under influencer's full control

---

### WHERE?

**Where is data stored?**

```sql
-- Profile-Level Performance
campaign_performance_ratings (
  campaign_id,
  profile_id,        -- @beauty_ig
  influencer_id,
  content_quality_score,
  content_creativity_score,
  platform_expertise_score,
  visual_quality_score,
  engagement_delivery_score,
  performance_notes,
)

-- Person-Level Behavior
influencer_behavior_ratings (
  campaign_id,
  influencer_id,     -- Nguyễn Văn A
  profile_id,        -- Track which profile, but rating applies to PERSON
  cooperation_attitude_score,
  communication_score,
  professionalism_score,
  reliability_score,
  deadline_adherence_score,
  behavior_notes,
  visibility ENUM('private'),  -- Always private in MVP
)

-- Aggregated Scores
social_profiles.avg_performance_score    -- Average from all campaign_performance_ratings
influencers.avg_behavior_score           -- Average from all influencer_behavior_ratings
influencers.behavior_flag_count          -- Count of ratings < 3 stars
```

**Where is it displayed?**
- Brand portal: Campaign history page → both performance + behavior (if authorized)
- Influencer dashboard: Own scores + improvement suggestions
- Discovery page: Aggregated scores (with filters)

---

### WHEN?

**When are ratings collected?**
- Post-campaign completion (after influencer delivers final content)
- 7-day window for brand to submit feedback
- Optional: Mid-campaign check-in ratings

**When are scores recalculated?**
- Real-time for new ratings
- Monthly batch job for time-weighted behavior scores
- On-demand when influencer disputes a rating

**When can influencers see feedback?**
- Immediately after brand submits (for performance)
- Behavior notes: Never (only see aggregated score)

**When can ratings be disputed?**
- Within 30 days of submission
- Requires evidence (screenshots, chat logs)
- Platform mediates, can remove unfair ratings

---

### WHY?

**Why hybrid approach?**
- Performance varies by platform → Profile-level makes sense
- Behavior is consistent across platforms → Person-level makes sense
- Prevents gaming the system while maintaining fairness

**Why private behavior ratings?**
- Legal: GDPR compliance, defamation protection
- Ethical: People deserve second chances, avoid permanent labeling
- Practical: Reduces rating inflation (brands more honest when private)

**Why allow public performance ratings?**
- Low risk: Work quality is less sensitive than personal traits
- Benefits influencers: Social proof, portfolio building
- Controlled: Influencer must consent

---

### HOW?

**How to implement?**

**Backend:**
```typescript
// DTO for brand post-campaign feedback
class CreateCampaignFeedbackDto {
  @IsUUID()
  campaign_id: string;

  @IsUUID()
  profile_id: string;  // Auto-derive influencer_id from this

  @ValidateNested()
  performance: PerformanceRatingDto;  // 5 scores + notes

  @ValidateNested()
  behavior: BehaviorRatingDto;  // 5 scores + notes

  @IsBoolean()
  @IsOptional()
  allow_public_performance?: boolean;  // Influencer consent checkbox
}

// Service layer
async createCampaignFeedback(dto: CreateCampaignFeedbackDto) {
  const profile = await this.profileRepo.findOne(dto.profile_id);
  const influencer_id = profile.influencer_id;

  // Insert performance rating (profile-level)
  await this.performanceRepo.save({
    campaign_id: dto.campaign_id,
    profile_id: dto.profile_id,
    influencer_id,
    ...dto.performance,
  });

  // Insert behavior rating (person-level)
  await this.behaviorRepo.save({
    campaign_id: dto.campaign_id,
    influencer_id,  // Store at PERSON level
    profile_id: dto.profile_id,  // Track which profile was used
    ...dto.behavior,
    visibility: 'private',  // Always private in MVP
  });

  // Recalculate aggregated scores
  await this.recalculateProfileScore(dto.profile_id);
  await this.recalculateInfluencerScore(influencer_id);
}
```

**Frontend:**
```typescript
// Brand Post-Campaign Feedback Form
<Form>
  <Section title="Performance Rating" subtitle="Đánh giá chất lượng công việc trên platform này">
    <Tooltip>Chỉ đánh giá content quality, không phải thái độ cá nhân</Tooltip>

    <StarRating label="Content Quality" name="performance.content_quality" />
    <StarRating label="Content Creativity" name="performance.content_creativity" />
    <StarRating label="Platform Expertise" name="performance.platform_expertise" />
    <StarRating label="Visual Quality" name="performance.visual_quality" />
    <StarRating label="Engagement Delivery" name="performance.engagement_delivery" />
    <TextArea label="Notes" name="performance.notes" placeholder="Content rất sáng tạo, engagement tốt" />
  </Section>

  <Section title="Behavior Rating" subtitle="Đánh giá phẩm chất làm việc (private)">
    <Tooltip>Đánh giá thái độ hợp tác, communication - áp dụng cho NGƯỜI, không phải account</Tooltip>

    <StarRating label="Cooperation Attitude" name="behavior.cooperation_attitude" />
    <StarRating label="Communication" name="behavior.communication" />
    <StarRating label="Professionalism" name="behavior.professionalism" />
    <StarRating label="Reliability" name="behavior.reliability" />
    <StarRating label="Deadline Adherence" name="behavior.deadline_adherence" />
    <TextArea label="Notes (private)" name="behavior.notes" placeholder="Thái độ hợp tác tốt, phản hồi nhanh" />

    <Alert variant="info">
      Behavior ratings are private and only visible to platform admin. This encourages honest feedback.
    </Alert>
  </Section>

  <Checkbox label="Allow public display of performance rating (influencer will see this)"
            name="allow_public_performance" />

  <Button type="submit">Submit Feedback</Button>
</Form>

// Example bad rating education
<ExampleCard variant="error">
  <Icon name="x" />
  <Text>❌ SAI: Rate "Cooperation = 1 sao" vì "Content không đẹp"</Text>
</ExampleCard>

<ExampleCard variant="success">
  <Icon name="check" />
  <Text>✅ ĐÚNG: Rate "Content Quality = 1 sao" (performance) + "Cooperation = 5 sao" (behavior)</Text>
</ExampleCard>
```

**How to display to influencers?**
```typescript
// Influencer Dashboard - My Ratings View
interface InfluencerRatingsView {
  performance_ratings: {
    profile: "@beauty_ig",
    campaign: "Sephora x Lancôme",
    brand: "Sephora",
    date: "2026-02-01",
    avg_score: 4.5,
    breakdown: {
      content_quality: 5,
      content_creativity: 5,
      platform_expertise: 4,
      visual_quality: 5,
      engagement_delivery: 4,
    },
    brand_notes: "Content rất sáng tạo, engagement delivery tốt",
    visibility: "public",
  }[],

  behavior_summary: {
    overall_score: 4.2,
    total_campaigns: 26,
    trend: "improving",  // "stable" | "declining"
    breakdown: {
      cooperation_attitude: 4.5,
      communication: 4.3,
      professionalism: 4.0,
      reliability: 4.1,
      deadline_adherence: 4.2,
    },
    message: "Detailed feedback notes are private. Focus on improving these areas:",
    suggestions: [
      "✅ Phản hồi brand trong 24h để cải thiện communication_score",
      "✅ Hoàn thành đúng deadline 3 campaign liên tiếp để tăng reliability_score",
    ],
  },
}
```

**How to use in brand discovery?**
```sql
-- Brand searches for Instagram beauty influencers with high scores
SELECT
  sp.id,
  sp.username,
  sp.platform,
  sp.followers_count,
  sp.avg_performance_score,
  i.full_name,
  i.avg_behavior_score,
  i.behavior_flag_count,
  (sp.avg_performance_score * 0.6 + i.avg_behavior_score * 0.4) as combined_score
FROM social_profiles sp
JOIN influencers i ON sp.influencer_id = i.id
WHERE
  sp.platform = 'instagram'
  AND sp.category = 'beauty'
  AND sp.followers_count BETWEEN 10000 AND 100000
  AND sp.avg_performance_score >= 4.0  -- Good content quality on Instagram
  AND i.avg_behavior_score >= 4.0      -- Good cooperation attitude (person-level)
  AND i.behavior_flag_count <= 1       -- Max 1 bad behavior incident
ORDER BY combined_score DESC
LIMIT 20;
```

---

## Key Insights

### Insight 1: Hybrid Storage - Phân loại theo Bản chất Feedback ⭐⭐⭐

**Description:** Lưu feedback dựa trên bản chất - Performance (Profile-level) vs Behavior (Person-level)

**Source:** Cả 3 techniques (SWOT, Six Thinking Hats, Starbursting)

**Impact:** 🔴 High | **Effort:** 🟡 Medium

**Rationale:**
```
"Thái độ hợp tác không tốt" → Person characteristic (INFLUENCER level)
   ↳ Nguyễn Văn A luôn khó tính dù dùng @beauty_ig hay @beauty_fb

"Content không sáng tạo" → Profile/Platform specific (PROFILE level)
   ↳ @beauty_ig có content tốt nhưng @beauty_tiktok nhàm chán
```

---

### Insight 2: Private by Default - Bảo vệ Reputation ⭐⭐

**Description:** Behavior ratings should be private. Performance ratings can be public with consent.

**Source:** Six Thinking Hats (Red Hat - emotions, Black Hat - legal risks)

**Impact:** 🔴 High (Compliance + Trust) | **Effort:** 🟢 Low

**Rationale:**
- Behavioral feedback ("thái độ hợp tác không tốt") có thể harm reputation
- GDPR/PDPA compliance cho personal data
- Influencer có quyền kiểm soát personal information
- Private ratings encourage honest brand feedback (no rating inflation)

---

### Insight 3: Industry Benchmark - Học từ Upwork & Airbnb ⭐⭐⭐

**Description:** Upwork rates PEOPLE, Airbnb rates PROPERTIES. We need both.

**Source:** SWOT (Opportunities), Starbursting (Why - best practices)

**Impact:** 🔴 High (Product-market fit) | **Effort:** 🟢 Low

**Comparison:**
| Platform | Entity | What's Rated | Our Mapping |
|----------|--------|--------------|-------------|
| Upwork | Freelancer (PERSON) | Communication, professionalism | Influencer (behavior) |
| Airbnb | Listing (PROPERTY) | Cleanliness, amenities | Profile (performance) |
| Uber | Driver + Car (HYBRID) | Attitude + comfort | Influencer + Profile |

---

### Insight 4: Prevent Profile-Hopping Exploitation ⭐⭐

**Description:** Nếu chỉ rate Profile, influencer có behavior xấu có thể tạo profile mới để "rửa sạch" reputation

**Source:** Six Thinking Hats (Black Hat - risk identification)

**Impact:** 🔴 High (Platform integrity) | **Effort:** 🟢 Low

**Scenario:**
```
Nguyễn Văn A bị rate "cooperation_attitude = 1 sao" nhiều lần

Profile-only storage:
  @beauty_ig → avg_rating = 2.1 (bị đánh giá xấu)
  ❌ Solution: Tạo @beauty_newaccount → avg_rating = null (fresh start!)

Person-level storage:
  Nguyễn Văn A → avg_behavior_score = 2.1
  ✅ Dù tạo @beauty_newaccount, behavior score vẫn theo PERSON
```

---

### Insight 5: Smart Brand Matching - Use Both Signals ⭐⭐⭐

**Description:** Brand Discovery cần filter theo CẢ performance (Profile) VÀ behavior (Person)

**Source:** Starbursting (How), Six Thinking Hats (Yellow Hat - benefits)

**Impact:** 🔴 High (Match quality) | **Effort:** 🟡 Medium

**Combined Scoring:**
```typescript
function calculateCombinedScore(profile, influencer) {
  return profile.avg_performance_score * 0.6 + influencer.avg_behavior_score * 0.4;
}

// Why 60-40 weighting?
// - Content quality (performance) slightly more important for ROI
// - But cooperation (behavior) critical for campaign success
```

---

### Insight 6: Influencer Reputation Recovery Path ⭐

**Description:** Cho phép influencer cải thiện behavior score qua thời gian (time-weighted scoring)

**Source:** Six Thinking Hats (Green Hat - creativity, Yellow Hat - fairness)

**Impact:** 🟡 Medium (Fairness + Retention) | **Effort:** 🟡 Medium

**Implementation:**
```sql
-- Time-weighted scoring (gần đây quan trọng hơn)
-- Decay 5% mỗi tháng → Rating 6 tháng trước còn ~74% weight
SELECT
  SUM(avg_rating * POWER(0.95, months_ago)) / SUM(POWER(0.95, months_ago))
FROM influencer_behavior_ratings
WHERE influencer_id = 'uuid';
```

---

### Insight 7: Feedback Loop - Brand Education ⭐⭐

**Description:** Brand cần guidelines rõ ràng để phân biệt Performance vs Behavior

**Source:** Starbursting (Who - stakeholder education)

**Impact:** 🟡 Medium (Data quality) | **Effort:** 🟢 Low

**Implementation:**
- In-form tooltips explaining each rating category
- Example "bad ratings" vs "good ratings"
- Visual separation between Performance section and Behavior section
- Automated validation (e.g., flag if all ratings are same score)

---

## Implementation Recommendations

### Phase 1: Database Schema (Week 1)

```sql
-- Profile-Level Performance Ratings
CREATE TABLE campaign_performance_ratings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id UUID NOT NULL REFERENCES campaigns(id),
  profile_id UUID NOT NULL REFERENCES social_profiles(id),
  influencer_id UUID NOT NULL REFERENCES influencers(id),

  -- Performance metrics (1-5 scale)
  content_quality_score INT CHECK (content_quality_score BETWEEN 1 AND 5),
  content_creativity_score INT CHECK (content_creativity_score BETWEEN 1 AND 5),
  platform_expertise_score INT CHECK (platform_expertise_score BETWEEN 1 AND 5),
  visual_quality_score INT CHECK (visual_quality_score BETWEEN 1 AND 5),
  engagement_delivery_score INT CHECK (engagement_delivery_score BETWEEN 1 AND 5),

  performance_notes TEXT,
  visibility ENUM('public', 'private') DEFAULT 'private',

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  UNIQUE(campaign_id, profile_id)  -- One rating per campaign-profile pair
);

-- Person-Level Behavior Ratings
CREATE TABLE influencer_behavior_ratings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id UUID NOT NULL REFERENCES campaigns(id),
  influencer_id UUID NOT NULL REFERENCES influencers(id),
  profile_id UUID NOT NULL REFERENCES social_profiles(id),  -- Track which profile was used

  -- Behavioral metrics (1-5 scale)
  cooperation_attitude_score INT CHECK (cooperation_attitude_score BETWEEN 1 AND 5),
  communication_score INT CHECK (communication_score BETWEEN 1 AND 5),
  professionalism_score INT CHECK (professionalism_score BETWEEN 1 AND 5),
  reliability_score INT CHECK (reliability_score BETWEEN 1 AND 5),
  deadline_adherence_score INT CHECK (deadline_adherence_score BETWEEN 1 AND 5),

  behavior_notes TEXT,
  visibility ENUM('private') DEFAULT 'private',  -- Always private in MVP

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  UNIQUE(campaign_id, influencer_id)  -- One rating per campaign-influencer pair
);

-- Aggregated scores
ALTER TABLE social_profiles
  ADD COLUMN avg_performance_score DECIMAL(3,2),
  ADD COLUMN total_campaigns_rated INT DEFAULT 0;

ALTER TABLE influencers
  ADD COLUMN avg_behavior_score DECIMAL(3,2),
  ADD COLUMN behavior_flag_count INT DEFAULT 0;  -- Count of ratings < 3 stars

-- Indexes
CREATE INDEX idx_performance_profile ON campaign_performance_ratings(profile_id);
CREATE INDEX idx_behavior_influencer ON influencer_behavior_ratings(influencer_id);
CREATE INDEX idx_performance_campaign ON campaign_performance_ratings(campaign_id);
CREATE INDEX idx_behavior_campaign ON influencer_behavior_ratings(campaign_id);

-- Trigger to recalculate aggregated scores
CREATE OR REPLACE FUNCTION update_aggregated_scores()
RETURNS TRIGGER AS $$
BEGIN
  -- Recalculate profile performance score
  UPDATE social_profiles
  SET
    avg_performance_score = (
      SELECT AVG((content_quality_score + content_creativity_score +
                  platform_expertise_score + visual_quality_score +
                  engagement_delivery_score) / 5.0)
      FROM campaign_performance_ratings
      WHERE profile_id = NEW.profile_id
    ),
    total_campaigns_rated = (
      SELECT COUNT(*) FROM campaign_performance_ratings WHERE profile_id = NEW.profile_id
    )
  WHERE id = NEW.profile_id;

  -- Recalculate influencer behavior score
  UPDATE influencers
  SET
    avg_behavior_score = (
      SELECT AVG((cooperation_attitude_score + communication_score +
                  professionalism_score + reliability_score +
                  deadline_adherence_score) / 5.0)
      FROM influencer_behavior_ratings
      WHERE influencer_id = NEW.influencer_id
    ),
    behavior_flag_count = (
      SELECT COUNT(*)
      FROM influencer_behavior_ratings
      WHERE influencer_id = NEW.influencer_id
        AND (cooperation_attitude_score + communication_score +
             professionalism_score + reliability_score +
             deadline_adherence_score) / 5.0 < 3.0
    )
  WHERE id = NEW.influencer_id;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER performance_rating_update
AFTER INSERT OR UPDATE ON campaign_performance_ratings
FOR EACH ROW EXECUTE FUNCTION update_aggregated_scores();

CREATE TRIGGER behavior_rating_update
AFTER INSERT OR UPDATE ON influencer_behavior_ratings
FOR EACH ROW EXECUTE FUNCTION update_aggregated_scores();
```

---

### Phase 2: Backend API (Week 2)

**DTOs:**
```typescript
// dto/create-campaign-feedback.dto.ts
export class PerformanceRatingDto {
  @IsInt()
  @Min(1)
  @Max(5)
  content_quality_score: number;

  @IsInt()
  @Min(1)
  @Max(5)
  content_creativity_score: number;

  @IsInt()
  @Min(1)
  @Max(5)
  platform_expertise_score: number;

  @IsInt()
  @Min(1)
  @Max(5)
  visual_quality_score: number;

  @IsInt()
  @Min(1)
  @Max(5)
  engagement_delivery_score: number;

  @IsString()
  @IsOptional()
  performance_notes?: string;
}

export class BehaviorRatingDto {
  @IsInt()
  @Min(1)
  @Max(5)
  cooperation_attitude_score: number;

  @IsInt()
  @Min(1)
  @Max(5)
  communication_score: number;

  @IsInt()
  @Min(1)
  @Max(5)
  professionalism_score: number;

  @IsInt()
  @Min(1)
  @Max(5)
  reliability_score: number;

  @IsInt()
  @Min(1)
  @Max(5)
  deadline_adherence_score: number;

  @IsString()
  @IsOptional()
  behavior_notes?: string;
}

export class CreateCampaignFeedbackDto {
  @IsUUID()
  campaign_id: string;

  @IsUUID()
  profile_id: string;

  @ValidateNested()
  @Type(() => PerformanceRatingDto)
  performance: PerformanceRatingDto;

  @ValidateNested()
  @Type(() => BehaviorRatingDto)
  behavior: BehaviorRatingDto;

  @IsBoolean()
  @IsOptional()
  allow_public_performance?: boolean;
}
```

**Service:**
```typescript
// services/campaign-feedback.service.ts
@Injectable()
export class CampaignFeedbackService {
  constructor(
    @InjectRepository(CampaignPerformanceRating)
    private performanceRepo: Repository<CampaignPerformanceRating>,

    @InjectRepository(InfluencerBehaviorRating)
    private behaviorRepo: Repository<InfluencerBehaviorRating>,

    @InjectRepository(SocialProfile)
    private profileRepo: Repository<SocialProfile>,
  ) {}

  async createCampaignFeedback(dto: CreateCampaignFeedbackDto, brand_id: string) {
    // Verify campaign belongs to brand
    const campaign = await this.campaignRepo.findOne({
      where: { id: dto.campaign_id, brand_id },
    });
    if (!campaign) throw new NotFoundException('Campaign not found');

    // Get influencer_id from profile
    const profile = await this.profileRepo.findOne({
      where: { id: dto.profile_id },
      relations: ['influencer'],
    });
    if (!profile) throw new NotFoundException('Profile not found');

    const influencer_id = profile.influencer.id;

    // Create performance rating (profile-level)
    const performanceRating = this.performanceRepo.create({
      campaign_id: dto.campaign_id,
      profile_id: dto.profile_id,
      influencer_id,
      ...dto.performance,
      visibility: dto.allow_public_performance ? 'public' : 'private',
    });
    await this.performanceRepo.save(performanceRating);

    // Create behavior rating (person-level)
    const behaviorRating = this.behaviorRepo.create({
      campaign_id: dto.campaign_id,
      influencer_id,  // Store at PERSON level
      profile_id: dto.profile_id,  // Track which profile was used
      ...dto.behavior,
      visibility: 'private',  // Always private
    });
    await this.behaviorRepo.save(behaviorRating);

    // Aggregated scores are auto-updated by triggers

    return {
      performance_rating: performanceRating,
      behavior_rating: behaviorRating,
    };
  }

  async getInfluencerRatings(influencer_id: string) {
    // For influencer dashboard
    const performanceRatings = await this.performanceRepo.find({
      where: { influencer_id },
      relations: ['campaign', 'profile'],
      order: { created_at: 'DESC' },
    });

    const behaviorSummary = await this.behaviorRepo
      .createQueryBuilder('br')
      .select('AVG(br.cooperation_attitude_score)', 'avg_cooperation')
      .addSelect('AVG(br.communication_score)', 'avg_communication')
      .addSelect('AVG(br.professionalism_score)', 'avg_professionalism')
      .addSelect('AVG(br.reliability_score)', 'avg_reliability')
      .addSelect('AVG(br.deadline_adherence_score)', 'avg_deadline')
      .addSelect('COUNT(*)', 'total_campaigns')
      .where('br.influencer_id = :influencer_id', { influencer_id })
      .getRawOne();

    return {
      performance_ratings: performanceRatings.map(r => ({
        profile: r.profile.username,
        campaign: r.campaign.name,
        date: r.created_at,
        avg_score: (
          r.content_quality_score + r.content_creativity_score +
          r.platform_expertise_score + r.visual_quality_score +
          r.engagement_delivery_score
        ) / 5.0,
        breakdown: {
          content_quality: r.content_quality_score,
          content_creativity: r.content_creativity_score,
          platform_expertise: r.platform_expertise_score,
          visual_quality: r.visual_quality_score,
          engagement_delivery: r.engagement_delivery_score,
        },
        notes: r.performance_notes,
        visibility: r.visibility,
      })),
      behavior_summary: {
        overall_score: (
          parseFloat(behaviorSummary.avg_cooperation) +
          parseFloat(behaviorSummary.avg_communication) +
          parseFloat(behaviorSummary.avg_professionalism) +
          parseFloat(behaviorSummary.avg_reliability) +
          parseFloat(behaviorSummary.avg_deadline)
        ) / 5.0,
        total_campaigns: parseInt(behaviorSummary.total_campaigns),
        breakdown: {
          cooperation_attitude: parseFloat(behaviorSummary.avg_cooperation),
          communication: parseFloat(behaviorSummary.avg_communication),
          professionalism: parseFloat(behaviorSummary.avg_professionalism),
          reliability: parseFloat(behaviorSummary.avg_reliability),
          deadline_adherence: parseFloat(behaviorSummary.avg_deadline),
        },
        // Notes are NOT exposed to influencer
      },
    };
  }
}
```

**Controller:**
```typescript
// controllers/campaign-feedback.controller.ts
@Controller('campaigns/:campaign_id/feedback')
@UseGuards(JwtAuthGuard, RoleGuard)
export class CampaignFeedbackController {
  constructor(private feedbackService: CampaignFeedbackService) {}

  @Post()
  @Roles('brand')
  async createFeedback(
    @Param('campaign_id') campaign_id: string,
    @Body() dto: CreateCampaignFeedbackDto,
    @Req() req,
  ) {
    return this.feedbackService.createCampaignFeedback(
      { ...dto, campaign_id },
      req.user.id,
    );
  }

  @Get('my-ratings')
  @Roles('influencer')
  async getMyRatings(@Req() req) {
    return this.feedbackService.getInfluencerRatings(req.user.influencer_id);
  }
}
```

---

### Phase 3: Frontend Forms (Week 3)

**Brand Feedback Form:**
```typescript
// pages/brand/campaigns/[id]/feedback.tsx
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';

const FeedbackSchema = Yup.object({
  performance: Yup.object({
    content_quality_score: Yup.number().min(1).max(5).required(),
    content_creativity_score: Yup.number().min(1).max(5).required(),
    platform_expertise_score: Yup.number().min(1).max(5).required(),
    visual_quality_score: Yup.number().min(1).max(5).required(),
    engagement_delivery_score: Yup.number().min(1).max(5).required(),
    performance_notes: Yup.string().max(500),
  }),
  behavior: Yup.object({
    cooperation_attitude_score: Yup.number().min(1).max(5).required(),
    communication_score: Yup.number().min(1).max(5).required(),
    professionalism_score: Yup.number().min(1).max(5).required(),
    reliability_score: Yup.number().min(1).max(5).required(),
    deadline_adherence_score: Yup.number().min(1).max(5).required(),
    behavior_notes: Yup.string().max(500),
  }),
  allow_public_performance: Yup.boolean(),
});

export default function CampaignFeedbackPage({ campaign, profile }) {
  return (
    <Container>
      <PageHeader>
        <Title>Campaign Feedback - {campaign.name}</Title>
        <Subtitle>Profile: @{profile.username} ({profile.platform})</Subtitle>
      </PageHeader>

      <Formik
        initialValues={{
          performance: {
            content_quality_score: 5,
            content_creativity_score: 5,
            platform_expertise_score: 5,
            visual_quality_score: 5,
            engagement_delivery_score: 5,
            performance_notes: '',
          },
          behavior: {
            cooperation_attitude_score: 5,
            communication_score: 5,
            professionalism_score: 5,
            reliability_score: 5,
            deadline_adherence_score: 5,
            behavior_notes: '',
          },
          allow_public_performance: false,
        }}
        validationSchema={FeedbackSchema}
        onSubmit={async (values) => {
          await api.post(`/campaigns/${campaign.id}/feedback`, {
            profile_id: profile.id,
            ...values,
          });
          toast.success('Feedback submitted successfully');
          router.push(`/brand/campaigns/${campaign.id}`);
        }}
      >
        {({ values, setFieldValue }) => (
          <Form>
            {/* Performance Section */}
            <Card>
              <CardHeader>
                <CardTitle>Performance Rating (Public with consent)</CardTitle>
                <Tooltip>
                  Đánh giá chất lượng công việc cụ thể trên platform này.
                  VD: Content quality, creativity, engagement metrics.
                </Tooltip>
              </CardHeader>

              <CardBody>
                <StarRatingField
                  label="Content Quality"
                  description="Chất lượng nội dung (copy, hashtags, call-to-action)"
                  name="performance.content_quality_score"
                />

                <StarRatingField
                  label="Content Creativity"
                  description="Độ sáng tạo, unique, không copy template"
                  name="performance.content_creativity_score"
                />

                <StarRatingField
                  label="Platform Expertise"
                  description="Hiểu rõ platform (Instagram Reels trends, TikTok sounds, etc.)"
                  name="performance.platform_expertise_score"
                />

                <StarRatingField
                  label="Visual Quality"
                  description="Chất lượng hình ảnh/video (lighting, editing, composition)"
                  name="performance.visual_quality_score"
                />

                <StarRatingField
                  label="Engagement Delivery"
                  description="Đạt hoặc vượt engagement KPIs (likes, comments, shares)"
                  name="performance.engagement_delivery_score"
                />

                <TextAreaField
                  label="Performance Notes"
                  placeholder="Content rất sáng tạo, engagement tốt hơn kỳ vọng..."
                  name="performance.performance_notes"
                  maxLength={500}
                />
              </CardBody>
            </Card>

            {/* Behavior Section */}
            <Card>
              <CardHeader>
                <CardTitle>Behavior Rating (Private)</CardTitle>
                <Tooltip>
                  Đánh giá phẩm chất làm việc của NGƯỜI (không phụ thuộc platform).
                  VD: Communication, professionalism, deadline adherence.
                </Tooltip>
              </CardHeader>

              <CardBody>
                <Alert variant="info">
                  <Icon name="lock" />
                  Behavior ratings are private and only visible to platform admin.
                  This encourages honest feedback without harming influencer reputation.
                </Alert>

                <StarRatingField
                  label="Cooperation Attitude"
                  description="Thái độ hợp tác, sẵn sàng nhận feedback và chỉnh sửa"
                  name="behavior.cooperation_attitude_score"
                />

                <StarRatingField
                  label="Communication"
                  description="Phản hồi nhanh, rõ ràng, professional"
                  name="behavior.communication_score"
                />

                <StarRatingField
                  label="Professionalism"
                  description="Chuyên nghiệp trong mọi tương tác"
                  name="behavior.professionalism_score"
                />

                <StarRatingField
                  label="Reliability"
                  description="Đáng tin cậy, giữ lời hứa"
                  name="behavior.reliability_score"
                />

                <StarRatingField
                  label="Deadline Adherence"
                  description="Hoàn thành đúng deadline, không trễ hạn"
                  name="behavior.deadline_adherence_score"
                />

                <TextAreaField
                  label="Behavior Notes (Private)"
                  placeholder="Thái độ hợp tác tốt, phản hồi nhanh, hoàn thành đúng deadline..."
                  name="behavior.behavior_notes"
                  maxLength={500}
                />
              </CardBody>
            </Card>

            {/* Education Section */}
            <Card variant="warning">
              <CardHeader>
                <Icon name="info" />
                <CardTitle>How to Rate Correctly</CardTitle>
              </CardHeader>

              <CardBody>
                <ExampleBadRating>
                  ❌ <strong>SAI:</strong> Rate "Cooperation Attitude = 1 sao" vì "Content không đẹp"
                </ExampleBadRating>

                <ExampleGoodRating>
                  ✅ <strong>ĐÚNG:</strong> Rate "Content Quality = 1 sao" (Performance) +
                  "Cooperation Attitude = 5 sao" (Behavior) nếu influencer dễ hợp tác nhưng content kém
                </ExampleGoodRating>

                <Divider />

                <h4>Remember:</h4>
                <ul>
                  <li><strong>Performance</strong> = Work quality (content, engagement) → Có thể khác nhau giữa platforms</li>
                  <li><strong>Behavior</strong> = Personal traits (cooperation, communication) → Nhất quán ở mọi platforms</li>
                </ul>
              </CardBody>
            </Card>

            {/* Consent Checkbox */}
            <CheckboxField
              label="Allow public display of performance rating"
              description="Influencer sẽ thấy performance rating này trên profile. Behavior rating luôn private."
              name="allow_public_performance"
            />

            <ButtonGroup>
              <Button type="button" variant="secondary" onClick={() => router.back()}>
                Cancel
              </Button>
              <Button type="submit" variant="primary">
                Submit Feedback
              </Button>
            </ButtonGroup>
          </Form>
        )}
      </Formik>
    </Container>
  );
}
```

**Influencer Ratings Dashboard:**
```typescript
// pages/influencer/my-ratings.tsx
export default function MyRatingsPage({ data }) {
  return (
    <Container>
      <PageHeader>
        <Title>My Ratings & Feedback</Title>
      </PageHeader>

      {/* Behavior Summary (Private aggregated view) */}
      <Card>
        <CardHeader>
          <CardTitle>Behavior Score Summary</CardTitle>
          <Badge variant={data.behavior_summary.overall_score >= 4 ? 'success' : 'warning'}>
            {data.behavior_summary.overall_score.toFixed(1)} / 5.0
          </Badge>
        </CardHeader>

        <CardBody>
          <Alert variant="info">
            Detailed feedback notes are private and only visible to platform admin.
            Focus on improving these key areas:
          </Alert>

          <ProgressBar
            label="Cooperation Attitude"
            value={data.behavior_summary.breakdown.cooperation_attitude}
            max={5}
          />
          <ProgressBar
            label="Communication"
            value={data.behavior_summary.breakdown.communication}
            max={5}
          />
          <ProgressBar
            label="Professionalism"
            value={data.behavior_summary.breakdown.professionalism}
            max={5}
          />
          <ProgressBar
            label="Reliability"
            value={data.behavior_summary.breakdown.reliability}
            max={5}
          />
          <ProgressBar
            label="Deadline Adherence"
            value={data.behavior_summary.breakdown.deadline_adherence}
            max={5}
          />

          <Divider />

          <h4>Improvement Suggestions:</h4>
          <SuggestionList>
            <Suggestion>✅ Phản hồi brand trong 24h để cải thiện communication_score</Suggestion>
            <Suggestion>✅ Hoàn thành đúng deadline 3 campaign liên tiếp</Suggestion>
          </SuggestionList>
        </CardBody>
      </Card>

      {/* Performance Ratings by Profile */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Ratings by Campaign</CardTitle>
        </CardHeader>

        <CardBody>
          <Table>
            <thead>
              <tr>
                <th>Profile</th>
                <th>Campaign</th>
                <th>Date</th>
                <th>Avg Score</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {data.performance_ratings.map((rating) => (
                <tr key={rating.id}>
                  <td>@{rating.profile}</td>
                  <td>{rating.campaign}</td>
                  <td>{formatDate(rating.date)}</td>
                  <td>
                    <Badge variant={rating.avg_score >= 4 ? 'success' : 'warning'}>
                      {rating.avg_score.toFixed(1)} / 5.0
                    </Badge>
                  </td>
                  <td>
                    <ExpandableRow>
                      <div>Content Quality: {rating.breakdown.content_quality} ⭐</div>
                      <div>Content Creativity: {rating.breakdown.content_creativity} ⭐</div>
                      <div>Platform Expertise: {rating.breakdown.platform_expertise} ⭐</div>
                      <div>Visual Quality: {rating.breakdown.visual_quality} ⭐</div>
                      <div>Engagement Delivery: {rating.breakdown.engagement_delivery} ⭐</div>
                      {rating.notes && (
                        <div className="mt-2">
                          <strong>Brand Notes:</strong> {rating.notes}
                        </div>
                      )}
                    </ExpandableRow>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </CardBody>
      </Card>
    </Container>
  );
}
```

---

### Phase 4: Discovery Filters (Week 4)

**Brand Discovery with Combined Scoring:**
```typescript
// api/discovery/search-influencers
interface DiscoveryFilters {
  platform: 'instagram' | 'facebook' | 'tiktok';
  category?: string;
  min_followers?: number;
  max_followers?: number;

  // Performance filters (Profile-level)
  min_performance_score?: number;

  // Behavior filters (Person-level)
  min_behavior_score?: number;
  max_behavior_flags?: number;

  // Sorting
  sort_by: 'performance_score' | 'behavior_score' | 'combined_score' | 'followers_count';
}

async function searchInfluencers(filters: DiscoveryFilters) {
  const query = this.profileRepo
    .createQueryBuilder('sp')
    .innerJoin('sp.influencer', 'i')
    .select([
      'sp.id',
      'sp.username',
      'sp.platform',
      'sp.followers_count',
      'sp.avg_performance_score',
      'i.full_name',
      'i.avg_behavior_score',
      'i.behavior_flag_count',
    ])
    .where('sp.platform = :platform', { platform: filters.platform });

  // Performance filters
  if (filters.min_performance_score) {
    query.andWhere('sp.avg_performance_score >= :min_perf', {
      min_perf: filters.min_performance_score,
    });
  }

  // Behavior filters
  if (filters.min_behavior_score) {
    query.andWhere('i.avg_behavior_score >= :min_behavior', {
      min_behavior: filters.min_behavior_score,
    });
  }

  if (filters.max_behavior_flags !== undefined) {
    query.andWhere('i.behavior_flag_count <= :max_flags', {
      max_flags: filters.max_behavior_flags,
    });
  }

  // Combined scoring
  if (filters.sort_by === 'combined_score') {
    query.addSelect(
      '(sp.avg_performance_score * 0.6 + i.avg_behavior_score * 0.4)',
      'combined_score'
    );
    query.orderBy('combined_score', 'DESC');
  } else if (filters.sort_by === 'performance_score') {
    query.orderBy('sp.avg_performance_score', 'DESC');
  } else if (filters.sort_by === 'behavior_score') {
    query.orderBy('i.avg_behavior_score', 'DESC');
  }

  return query.limit(20).getMany();
}
```

---

## Statistics

- **Total Ideas Generated:** 47
- **Categories:** 8 (Storage strategy, Privacy, Industry benchmarks, Platform protection, Discovery, Recovery paths, Education, Implementation)
- **Key Insights:** 7
- **Techniques Applied:** 3 (SWOT, Six Thinking Hats, Starbursting)
- **Impact Distribution:**
  - 🔴 High Impact: 5 insights
  - 🟡 Medium Impact: 2 insights
- **Effort Distribution:**
  - 🟢 Low Effort: 4 insights
  - 🟡 Medium Effort: 3 insights

---

## Recommended Next Steps

### Immediate (Next Sprint)
1. **Implement database schema** (Phase 1) - Estimated 1 day
2. **Create backend DTOs and validation** (Phase 2) - Estimated 1 day
3. **Write unit tests** for rating services

### Short-term (Next 2 Sprints)
4. **Build brand feedback form** with education tooltips (Phase 3)
5. **Create influencer ratings dashboard** (Phase 3)
6. **Add discovery filters** for combined scoring (Phase 4)

### Medium-term (Quarter)
7. **Implement time-weighted behavior scoring** (Insight 6)
8. **Add influencer improvement suggestions** (Gamification)
9. **Build admin dashboard** for monitoring rating patterns
10. **Create dispute resolution workflow**

### Long-term (Next Quarter+)
11. **Peer ratings** (Influencers rate brands)
12. **Predictive matching** (ML-based brand-influencer pairing)
13. **Reputation recovery missions** (Gamified improvement)

---

## Appendix: Industry Research

### Upwork Freelancer Ratings
- **Entity:** Freelancer (PERSON)
- **Attributes:** Skills, availability, communication, quality of work, adherence to schedule
- **Visibility:** Public, displayed on freelancer profile
- **Impact:** Directly affects job success score (JSS) and search ranking

### Airbnb Listing Ratings
- **Entity:** Property (LISTING)
- **Attributes:** Cleanliness, accuracy, check-in, communication, location, value
- **Visibility:** Public, displayed on listing page
- **Impact:** Superhost status, search ranking, booking conversion

### Uber Driver+Trip Ratings
- **Entity:** HYBRID (Driver + Trip)
- **Driver ratings:** Friendliness, driving skill, professionalism
- **Trip ratings:** Car cleanliness, temperature, music
- **Visibility:** Private (only driver sees aggregated score)
- **Impact:** Low ratings → deactivation

---

*Generated by BMAD Method v6 - Creative Intelligence*
*Brainstorming Session Duration: ~45 minutes*
*Document Version: 1.0*
*Date: 2026-02-13*
