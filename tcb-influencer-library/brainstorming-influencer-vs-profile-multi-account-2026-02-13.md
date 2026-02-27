# Brainstorming Session: Influencer vs Profile - Multi-Account Data Model

**Date:** 2026-02-13
**Objective:** Thiết kế data model và onboarding flow cho trường hợp 1 influencer có nhiều profiles (multiple social accounts)
**Duration:** 30 minutes
**Techniques:** Mind Mapping, SCAMPER, Six Thinking Hats

---

## Executive Summary

**Problem Statement:**
Current data model giả định **1 influencer = 1 profile** (1:1 relationship). Nhưng thực tế, **1 influencer có thể có nhiều social accounts** (@beauty_fb, @beauty_ig, @beauty_tiktok). Nếu mỗi profile là separate entity → influencer phải nhập lại personal info (name, DOB, bank account, compliance) nhiều lần → **BAD UX**.

**Solution:**
Tách thành **2 entities riêng biệt**:
1. **INFLUENCER** (Person) - Dữ liệu về con người (1 entity)
2. **PROFILE** (Social Account) - Dữ liệu về tài khoản mạng xã hội (nhiều entities)

**Key Decision:**
```
1 Influencer (Person)
  ├─ @beauty_fb (Facebook Profile)
  ├─ @beauty_ig (Instagram Profile)
  └─ @beauty_tiktok (TikTok Profile)
```

**Benefits:**
- ✅ Chỉ nhập personal info **1 lần** (name, DOB, bank account, compliance)
- ✅ Add profile mới chỉ mất **2-5 phút** (thay vì 15 phút)
- ✅ Data consistency (không có mâu thuẫn giữa profiles)
- ✅ Profile-specific matching (match đúng platform cho campaign)
- ✅ Cross-profile analytics (so sánh performance across platforms)

---

## Context

### Current State (1:1 Model)
```sql
CREATE TABLE influencer_profiles (
  id UUID PRIMARY KEY,
  -- Personal data
  full_name VARCHAR(255),
  dob DATE,
  national_id VARCHAR(20),
  bank_account VARCHAR(50),

  -- Social account
  instagram_handle VARCHAR(100),
  follower_count BIGINT,

  -- Mix of person + profile data
  ...
);
```

**Problems:**
1. If influencer has FB + IG + TikTok → Must register 3 times
2. Personal data (name, DOB, bank) entered 3 times → Redundancy
3. eKYC verification done 3 times → Waste of time
4. Compliance consents repeated 3 times → Confusion
5. No link between @beauty_fb and @beauty_ig → Brands don't know they're same person

### New Reality (1:Many Model)
```
Influencer: Nguyễn Văn A (1 person)
├─ Profile 1: @beauty_fb (Facebook, 200K followers, Finance + Lifestyle)
├─ Profile 2: @beauty_ig (Instagram, 500K followers, Beauty only)
└─ Profile 3: @beauty_tt (TikTok, 1M followers, Comedy + Beauty)
```

**Need:**
- Separate **Influencer data** (person) from **Profile data** (account)
- Ask influencer info once → Reuse for all profiles
- Allow adding multiple profiles easily
- Match campaigns at profile level (not influencer level)

---

## Data Model: Influencer vs Profile

### INFLUENCER Level (Person - Shared Across All Profiles)

**Categories:**

#### 1. Core Identity (18 fields)
*Ask once, shared across all profiles*

| Field | Type | Required | Example |
|-------|------|----------|---------|
| influencer_id | UUID | Yes | uuid-123 |
| full_name | VARCHAR(255) | Yes | Nguyễn Văn A |
| display_name | VARCHAR(255) | Yes | Beauty Queen |
| date_of_birth | DATE | Yes | 1995-05-15 |
| national_id | VARCHAR(20) | Yes | 079095001234 |
| gender | VARCHAR(20) | No | Female |
| citizenship | VARCHAR(50) | Yes | Vietnam |
| primary_phone | VARCHAR(20) | Yes | +84 901 234 567 |
| primary_email | VARCHAR(255) | Yes | nguyen.van.a@gmail.com |
| primary_location_city | VARCHAR(100) | Yes | Ho Chi Minh City |
| primary_location_region | VARCHAR(50) | Yes | South |
| profile_photo_url | TEXT | No | https://.../photo.jpg |
| bio | TEXT | No | Beauty & lifestyle creator... |
| languages | VARCHAR[] | No | [Vietnamese, English] |
| occupation | VARCHAR(100) | No | Content Creator |
| created_at | TIMESTAMP | Yes | 2026-01-15 10:30:00 |
| last_login | TIMESTAMP | No | 2026-02-13 14:22:00 |
| account_status | VARCHAR(50) | Yes | active |

**Rationale:** These are traits of the **PERSON**, not the social account.
- Same name across all platforms
- Same age (DOB)
- Same national ID (1 person = 1 ID)
- Same phone/email for login

---

#### 2. Financial Information (8 fields)
*1 person = 1 bank account for ALL payments*

| Field | Type | Required | Example |
|-------|------|----------|---------|
| bank_account_number | VARCHAR(50) | Yes | 1234567890 |
| bank_name | VARCHAR(100) | Yes | Techcombank |
| account_holder_name | VARCHAR(255) | Yes | NGUYEN VAN A |
| payment_method | VARCHAR(50) | Yes | bank_transfer |
| business_type | VARCHAR(50) | No | individual |
| tax_id | VARCHAR(50) | No | null (if individual) |
| invoice_entity | VARCHAR(255) | No | null |
| payment_terms | VARCHAR(100) | No | 50% upfront, 50% post |

**Rationale:** Payment goes to the person, not to individual social accounts.
- All campaigns → same bank account
- Simplifies accounting
- No confusion about which account to pay

**Example:**
```
Campaign 1: Use @beauty_ig → Pay to account 1234567890
Campaign 2: Use @beauty_fb → Pay to SAME account 1234567890
Campaign 3: Use @beauty_tt → Pay to SAME account 1234567890
```

---

#### 3. Compliance & Legal (8 fields)
*Consent is at person level, applies to ALL profiles*

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| age_18_confirmed | BOOLEAN | Yes | Must be true |
| right_to_work_confirmed | BOOLEAN | Yes | Must be true |
| no_conflict_confirmed | BOOLEAN | Yes | Must be true |
| competitor_exclusivity | VARCHAR(255) | No | null or bank name |
| exclusivity_expires | DATE | No | null if none |
| disclosure_agreed | BOOLEAN | Yes | #ad tags |
| privacy_consent | BOOLEAN | Yes | Data processing |
| terms_accepted | BOOLEAN | Yes | T&C version tracked |
| terms_version | VARCHAR(20) | Yes | v2.1 |
| marketing_opt_in | BOOLEAN | No | Email campaigns |
| ekyc_status | VARCHAR(50) | Yes | completed |
| ekyc_completed_at | TIMESTAMP | No | 2026-01-15 11:00:00 |

**Rationale:** Legal consents are from the **person**, not the account.
- 1 eKYC verification → Valid for ALL profiles
- If person is <18 → Cannot use ANY profile for finance campaigns
- If person has competitor exclusivity → Applies to ALL profiles

**Important:** If influencer revokes consent → ALL profiles become inactive (person-level decision).

---

#### 4. Professional Setup (6 fields)
*Applies to the influencer's career, not specific profile*

| Field | Type | Example |
|-------|------|---------|
| working_as | VARCHAR(50) | solo / agency / company |
| agency_mcn_name | VARCHAR(255) | ABC Talent Agency |
| team_size | VARCHAR(50) | 2-5 people |
| business_registered | BOOLEAN | false |
| years_as_influencer | INT | 5 |
| professional_affiliations | TEXT[] | [IAB Vietnam, ...] |

**Rationale:** Professional setup describes the **person's career**, not individual accounts.

---

#### 5. Finance Affinity (TCB-Specific, 10 fields)
*Personal banking experience, not account-specific*

| Field | Type | Example |
|-------|------|---------|
| is_tcb_customer | BOOLEAN | true |
| tcb_customer_tier | VARCHAR(20) | gold |
| tcb_products_used | VARCHAR[] | [credit_card, savings] |
| tcb_customer_since | DATE | 2020-03-15 |
| banking_relationships | VARCHAR[] | [techcombank, vietcombank] |
| credit_card_usage | VARCHAR(50) | regularly |
| investment_experience | VARCHAR(50) | intermediate |
| financial_literacy_score | INT | 8 (out of 10) |
| willing_finance_training | BOOLEAN | true |
| finance_affinity_score | INT | 82 (computed 0-100) |

**Rationale:** Banking experience is personal, not tied to social accounts.
- Same person uses credit card (personal experience)
- Same person is TCB customer
- Finance affinity score applies to the person

**Usage:** When matching finance campaigns, use person's finance affinity, not profile-level.

---

#### 6. System Metadata (5 fields)

| Field | Type | Notes |
|-------|------|-------|
| influencer_id | UUID | Primary key |
| created_at | TIMESTAMP | Registration date |
| updated_at | TIMESTAMP | Last profile update |
| last_login_at | TIMESTAMP | Last access |
| overall_reputation_score | INT | Cross-profile aggregation |

---

### PROFILE Level (Social Account - Specific to Each Platform)

**Categories:**

#### 1. Profile Identity (8 fields)
*Specific to THIS social account*

| Field | Type | Required | Example |
|-------|------|----------|---------|
| profile_id | UUID | Yes | uuid-456 |
| influencer_id | UUID | Yes | uuid-123 (FK) |
| platform | VARCHAR(20) | Yes | instagram |
| account_handle | VARCHAR(255) | Yes | @beauty_ig |
| account_url | TEXT | Yes | instagram.com/beauty_ig |
| display_name_on_platform | VARCHAR(255) | No | Beauty Queen IG |
| profile_bio | TEXT | No | Beauty tips & reviews... |
| is_primary_profile | BOOLEAN | No | true (1 primary per influencer) |

**Rationale:** Each social account has its own identity.
- @beauty_fb has different handle than @beauty_ig
- Bio can be customized per platform
- URL is platform-specific

**Primary Profile:**
- Influencer selects 1 profile as "primary" (default for matching)
- Usually their largest or most active account
- Can change anytime

---

#### 2. Social Metrics (Auto-Fetched by Diso Source 2, 10 fields)
*Platform-specific, varies widely*

| Field | Type | Example (IG) | Example (FB) | Example (TT) |
|-------|------|--------------|--------------|--------------|
| follower_count | BIGINT | 500,000 | 200,000 | 1,000,000 |
| following_count | BIGINT | 1,200 | 800 | 2,500 |
| post_count | INT | 1,450 | 3,200 | 890 |
| engagement_rate | DECIMAL(5,2) | 4.2% | 2.1% | 6.8% |
| avg_likes | BIGINT | 21,000 | 4,200 | 68,000 |
| avg_comments | BIGINT | 850 | 230 | 2,100 |
| posts_per_week | DECIMAL(4,1) | 7.0 | 3.5 | 14.0 |
| is_verified | BOOLEAN | true | true | false |
| account_created_date | DATE | 2018-06-10 | 2015-02-20 | 2020-10-05 |
| last_crawled_at | TIMESTAMP | 2026-02-13 12:00 | 2026-02-13 12:00 | 2026-02-13 12:00 |

**Rationale:** Metrics vary DRAMATICALLY per platform.
- Instagram: High engagement, visual content
- Facebook: Lower engagement, broader reach
- TikTok: Viral potential, younger audience

**Don't ask influencer for these** → Diso auto-fetches via API.

---

#### 3. Content Strategy (Platform-Specific, 8 fields)
*Different content approach per platform*

| Field | Type | Example (IG) | Example (LinkedIn) |
|-------|------|--------------|-------------------|
| primary_categories | VARCHAR[] | [beauty, lifestyle] | [finance, business] |
| content_formats | VARCHAR[] | [reels, photos] | [articles, videos] |
| content_language | VARCHAR(50) | Bilingual | Vietnamese |
| posting_frequency | VARCHAR(50) | Daily | 2x per week |
| content_style | VARCHAR(50) | Entertainment | Educational |
| niche_specialty | TEXT | Beauty product reviews | Personal finance tips |
| target_audience_desc | TEXT | Young women 25-35 | Professionals 30-45 |
| content_tone | VARCHAR(50) | Fun, inspirational | Professional, informative |

**Rationale:** Influencer often creates different content per platform.
- Instagram: Beauty (visual, fun)
- LinkedIn: Finance (professional, serious)
- TikTok: Comedy (viral, short-form)

**Example:**
```
Influencer: Nguyễn Văn A

@beauty_ig (Instagram):
- Categories: Beauty, Lifestyle
- Style: Entertainment, product reviews
- Audience: Young women 25-35

@finance_linkedin (LinkedIn):
- Categories: Finance, Business
- Style: Educational, professional
- Audience: Professionals 30-45

Same person, different content strategies per platform.
```

---

#### 4. Audience Demographics (Platform-Specific, 8 fields)
*Varies WIDELY per platform*

| Field | IG (Beauty) | FB (Lifestyle) | TT (Comedy) |
|-------|-------------|----------------|-------------|
| age_18_24_pct | 20% | 15% | 45% |
| age_25_34_pct | 50% ⭐ | 40% | 35% |
| age_35_44_pct | 25% | 30% | 15% |
| age_45_plus_pct | 5% | 15% | 5% |
| gender_female_pct | 80% | 65% | 55% |
| gender_male_pct | 20% | 35% | 45% |
| top_locations | [HCMC 40%, Hanoi 25%] | [Hanoi 35%, HCMC 30%] | [HCMC 30%, Hanoi 25%] |
| income_level | High | Medium | Medium-Low |
| audience_interests | [beauty, fashion, shopping] | [lifestyle, family, travel] | [entertainment, comedy] |

**Rationale:** Same influencer → Different audiences per platform.
- Instagram: Younger, female-dominated, high-income (beauty products)
- Facebook: Broader age, family-focused
- TikTok: Very young, comedy/entertainment

**Matching Impact:**
```
Campaign: Credit Card for Young Professionals (25-35, high income)
→ Match: @beauty_ig (50% in target age, high income) ✅
→ NOT Match: @comedy_tiktok (45% are 18-24, medium-low income) ❌
```

---

#### 5. Pricing (Per Profile, 8 fields)
*Rates vary per platform + follower count*

| Field | @beauty_ig (500K) | @beauty_fb (200K) | @beauty_tt (1M) |
|-------|-------------------|-------------------|-----------------|
| rate_per_post | 10M VND | 5M VND | 15M VND |
| rate_per_story | 3M VND | 2M VND | 4M VND |
| rate_per_video | 15M VND | 8M VND | 20M VND |
| rate_per_reel | 12M VND | - | 18M VND |
| package_deal | 3 posts + 5 stories = 25M | - | 1 video = 15M |
| rate_negotiability | Flexible | Fixed | Flexible |
| minimum_budget | 8M VND | 4M VND | 12M VND |
| exclusivity_premium | +20% | +15% | +25% |

**Rationale:** Pricing depends on platform reach and engagement.
- TikTok (1M followers) → Highest rate (viral potential)
- Instagram (500K) → Medium-high rate (high engagement)
- Facebook (200K) → Lower rate (lower engagement)

**Multi-Profile Bundles:**
```
Campaign wants multi-platform:
- @beauty_ig: 10M
- @beauty_tt: 15M
- Bundle discount: -3M
- Total: 22M VND
```

---

#### 6. Performance History (Per Profile, 8 fields)
*Campaign performance varies per platform*

| Field | Type | Example |
|-------|------|---------|
| campaigns_completed | INT | 25 (on THIS profile) |
| campaigns_last_12mo | INT | 12 |
| avg_ctr | DECIMAL(5,2) | 3.8% (platform-specific) |
| avg_cvr | DECIMAL(5,2) | 1.5% |
| best_performing_category | VARCHAR(50) | Beauty products |
| total_revenue_generated | DECIMAL(15,2) | 180M VND (on THIS profile) |
| avg_brand_rating | DECIMAL(3,2) | 4.7 / 5.0 |
| case_study_links | TEXT[] | [link1, link2] |

**Rationale:** Performance varies per platform.
- Instagram beauty campaigns → 3.8% CTR
- Facebook lifestyle campaigns → 2.1% CTR
- TikTok viral campaigns → 6.5% CTR

**Cross-Profile Analytics:**
```
Dashboard shows:
"Your Instagram performs 80% better than Facebook for beauty campaigns"
→ Recommendation: Use @beauty_ig for beauty, @beauty_fb for lifestyle
```

---

#### 7. Collaboration Preferences (May Vary Per Profile, 6 fields)

| Field | Example |
|-------|---------|
| preferred_campaign_types | [beauty, skincare, makeup] |
| creative_control_pref | Full creative freedom |
| content_approval_required | Yes (brand must approve) |
| max_concurrent_campaigns | 3 (per profile) |
| blackout_dates | [2026-06-01 to 2026-06-30] |
| platform_specific_notes | "No political content on IG" |

---

#### 8. Profile Metadata (7 fields)

| Field | Type | Notes |
|-------|------|-------|
| profile_id | UUID | Primary key |
| influencer_id | UUID | Foreign key |
| profile_status | VARCHAR(50) | active / paused / suspended |
| verification_status | VARCHAR(50) | verified / pending / failed |
| oauth_connected | BOOLEAN | true (can auto-post) |
| profile_completeness_pct | INT | 85% |
| profile_quality_score | INT | 92 / 100 |
| created_at | TIMESTAMP | When profile added |
| updated_at | TIMESTAMP | Last edit |

---

## Database Schema (Normalized)

```sql
-- ============================================
-- INFLUENCER TABLE (Person-Level Data)
-- ============================================
CREATE TABLE influencers (
  -- Identity
  id UUID PRIMARY KEY,
  full_name VARCHAR(255) NOT NULL,
  display_name VARCHAR(255) NOT NULL,
  date_of_birth DATE NOT NULL,
  national_id VARCHAR(20) NOT NULL UNIQUE,
  gender VARCHAR(20),
  citizenship VARCHAR(50) NOT NULL,
  primary_phone VARCHAR(20) NOT NULL UNIQUE,
  primary_email VARCHAR(255) NOT NULL UNIQUE,
  primary_location_city VARCHAR(100) NOT NULL,
  primary_location_region VARCHAR(50),
  profile_photo_url TEXT,
  bio TEXT,
  languages VARCHAR[],
  occupation VARCHAR(100),

  -- Financial (Shared across all profiles)
  bank_account_number VARCHAR(50) NOT NULL,
  bank_name VARCHAR(100) NOT NULL,
  account_holder_name VARCHAR(255) NOT NULL,
  payment_method VARCHAR(50) NOT NULL,
  business_type VARCHAR(50),
  tax_id VARCHAR(50),
  invoice_entity VARCHAR(255),
  payment_terms VARCHAR(100),

  -- Compliance (Person-level, applies to ALL profiles)
  age_18_confirmed BOOLEAN NOT NULL DEFAULT false,
  right_to_work_confirmed BOOLEAN NOT NULL DEFAULT false,
  no_conflict_confirmed BOOLEAN NOT NULL DEFAULT false,
  competitor_exclusivity VARCHAR(255),
  exclusivity_expires DATE,
  disclosure_agreed BOOLEAN NOT NULL DEFAULT false,
  privacy_consent BOOLEAN NOT NULL DEFAULT false,
  terms_accepted BOOLEAN NOT NULL DEFAULT false,
  terms_version VARCHAR(20),
  marketing_opt_in BOOLEAN DEFAULT false,
  ekyc_status VARCHAR(50) NOT NULL DEFAULT 'pending',
  ekyc_completed_at TIMESTAMP,

  -- Professional
  working_as VARCHAR(50),
  agency_mcn_name VARCHAR(255),
  team_size VARCHAR(50),
  business_registered BOOLEAN DEFAULT false,
  years_as_influencer INT,
  professional_affiliations TEXT[],

  -- Finance Affinity (TCB-specific, person-level)
  is_tcb_customer BOOLEAN DEFAULT false,
  tcb_customer_tier VARCHAR(20),
  tcb_products_used VARCHAR[],
  tcb_customer_since DATE,
  banking_relationships VARCHAR[],
  credit_card_usage VARCHAR(50),
  investment_experience VARCHAR(50),
  financial_literacy_score INT CHECK (financial_literacy_score BETWEEN 1 AND 10),
  willing_finance_training BOOLEAN,
  finance_affinity_score INT CHECK (finance_affinity_score BETWEEN 0 AND 100),

  -- System
  account_status VARCHAR(50) DEFAULT 'active',
  overall_reputation_score INT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_login_at TIMESTAMP,

  -- Constraints
  CONSTRAINT age_18_plus CHECK (DATE_PART('year', AGE(date_of_birth)) >= 18),
  CONSTRAINT valid_ekyc_status CHECK (ekyc_status IN ('pending', 'in_progress', 'completed', 'failed'))
);

-- ============================================
-- SOCIAL_PROFILES TABLE (Account-Level Data)
-- ============================================
CREATE TABLE social_profiles (
  -- Identity
  id UUID PRIMARY KEY,
  influencer_id UUID NOT NULL REFERENCES influencers(id) ON DELETE CASCADE,
  platform VARCHAR(20) NOT NULL, -- facebook, instagram, tiktok, youtube, linkedin
  account_handle VARCHAR(255) NOT NULL,
  account_url TEXT NOT NULL,
  display_name_on_platform VARCHAR(255),
  profile_bio TEXT,
  is_primary_profile BOOLEAN DEFAULT false,

  -- Social Metrics (Auto-fetched by Diso Source 2)
  follower_count BIGINT,
  following_count BIGINT,
  post_count INT,
  engagement_rate DECIMAL(5,2),
  avg_likes BIGINT,
  avg_comments BIGINT,
  posts_per_week DECIMAL(4,1),
  is_verified BOOLEAN DEFAULT false,
  account_created_date DATE,
  last_crawled_at TIMESTAMP,

  -- Content Strategy (Platform-specific)
  primary_categories VARCHAR[],
  content_formats VARCHAR[],
  content_language VARCHAR(50),
  posting_frequency VARCHAR(50),
  content_style VARCHAR(50),
  niche_specialty TEXT,
  target_audience_desc TEXT,
  content_tone VARCHAR(50),

  -- Audience Demographics (Platform-specific)
  age_18_24_pct INT CHECK (age_18_24_pct BETWEEN 0 AND 100),
  age_25_34_pct INT CHECK (age_25_34_pct BETWEEN 0 AND 100),
  age_35_44_pct INT CHECK (age_35_44_pct BETWEEN 0 AND 100),
  age_45_plus_pct INT CHECK (age_45_plus_pct BETWEEN 0 AND 100),
  gender_female_pct INT,
  gender_male_pct INT,
  top_locations JSONB, -- {hcmc: 40, hanoi: 25, ...}
  income_level VARCHAR(50),
  audience_interests TEXT[],

  -- Pricing (Per profile)
  rate_per_post DECIMAL(15,2),
  rate_per_story DECIMAL(15,2),
  rate_per_video DECIMAL(15,2),
  rate_per_reel DECIMAL(15,2),
  package_deal TEXT,
  rate_negotiability VARCHAR(50),
  minimum_budget DECIMAL(15,2),
  exclusivity_premium_pct INT,

  -- Performance (Per profile)
  campaigns_completed INT DEFAULT 0,
  campaigns_last_12mo INT DEFAULT 0,
  avg_ctr DECIMAL(5,2),
  avg_cvr DECIMAL(5,2),
  best_performing_category VARCHAR(50),
  total_revenue_generated DECIMAL(15,2),
  avg_brand_rating DECIMAL(3,2),
  case_study_links TEXT[],

  -- Collaboration Preferences (Per profile)
  preferred_campaign_types VARCHAR[],
  creative_control_pref VARCHAR(50),
  content_approval_required BOOLEAN,
  max_concurrent_campaigns INT,
  blackout_dates JSONB, -- [{start: '2026-06-01', end: '2026-06-30'}]
  platform_specific_notes TEXT,

  -- Profile Metadata
  profile_status VARCHAR(50) DEFAULT 'active', -- active, paused, suspended, deleted
  verification_status VARCHAR(50) DEFAULT 'pending',
  oauth_connected BOOLEAN DEFAULT false,
  oauth_token_encrypted TEXT,
  profile_completeness_pct INT DEFAULT 0,
  profile_quality_score INT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  -- Constraints
  UNIQUE(influencer_id, platform, account_handle),
  CONSTRAINT valid_platform CHECK (platform IN ('facebook', 'instagram', 'tiktok', 'youtube', 'linkedin', 'twitter')),
  CONSTRAINT valid_profile_status CHECK (profile_status IN ('active', 'paused', 'suspended', 'deleted')),
  CONSTRAINT one_primary_per_influencer EXCLUDE USING gist (influencer_id WITH =) WHERE (is_primary_profile = true)
);

-- ============================================
-- PROFILE_PORTFOLIO TABLE (Content Examples)
-- ============================================
CREATE TABLE profile_portfolio_items (
  id UUID PRIMARY KEY,
  profile_id UUID NOT NULL REFERENCES social_profiles(id) ON DELETE CASCADE,
  content_url TEXT NOT NULL,
  content_type VARCHAR(50), -- post, reel, video, story
  platform VARCHAR(20), -- facebook, instagram, tiktok
  description TEXT,
  is_sponsored BOOLEAN DEFAULT false,
  brand_name VARCHAR(255),
  campaign_id UUID, -- Optional link to campaign
  performance_metrics JSONB, -- {likes: 25000, comments: 850, shares: 120, views: 150000}
  created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================
CREATE INDEX idx_influencers_email ON influencers(primary_email);
CREATE INDEX idx_influencers_phone ON influencers(primary_phone);
CREATE INDEX idx_influencers_tcb_customer ON influencers(is_tcb_customer) WHERE is_tcb_customer = true;
CREATE INDEX idx_influencers_finance_affinity ON influencers(finance_affinity_score DESC);

CREATE INDEX idx_profiles_influencer ON social_profiles(influencer_id);
CREATE INDEX idx_profiles_platform ON social_profiles(platform);
CREATE INDEX idx_profiles_handle ON social_profiles(account_handle);
CREATE INDEX idx_profiles_primary ON social_profiles(influencer_id, is_primary_profile) WHERE is_primary_profile = true;
CREATE INDEX idx_profiles_categories ON social_profiles USING GIN(primary_categories);
CREATE INDEX idx_profiles_follower_count ON social_profiles(follower_count DESC);
CREATE INDEX idx_profiles_engagement ON social_profiles(engagement_rate DESC);
```

---

## Onboarding Flow: Influencer + Profiles

### Flow Overview

```
┌──────────────────────────────────────────────────────────────┐
│  NEW ONBOARDING FLOW (1 Influencer → Many Profiles)         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  PHASE 1: REGISTER INFLUENCER (One-Time, 10-15 mins)        │
│  ┌────────────────────────────────────┐                      │
│  │ Step 1: Personal Info              │                      │
│  │ - Name, DOB, ID, Phone, Email      │                      │
│  │ - Location, Photo                  │                      │
│  │                                    │                      │
│  │ Step 2: Financial Info             │                      │
│  │ - Bank account (for ALL payments)  │                      │
│  │ - Payment method                   │                      │
│  │                                    │                      │
│  │ Step 3: Compliance                 │                      │
│  │ - eKYC (verify once for all)       │                      │
│  │ - Consents (applies to all profiles)│                     │
│  │                                    │                      │
│  │ Step 4: Professional Setup         │                      │
│  │ - Working as, Agency, Team         │                      │
│  │                                    │                      │
│  │ Step 5: Finance Affinity ⭐         │                      │
│  │ - TCB customer? Banking experience │                      │
│  │                                    │                      │
│  │ ✅ INFLUENCER REGISTERED            │                      │
│  │    Profile: 20% complete           │                      │
│  └────────────────────────────────────┘                      │
│                                                              │
│  ↓                                                           │
│                                                              │
│  PHASE 2: ADD FIRST PROFILE (Required, 5-7 mins)            │
│  ┌────────────────────────────────────┐                      │
│  │ "Add Your Social Media Profile"    │                      │
│  │                                    │                      │
│  │ Step 1: Select Platform            │                      │
│  │ ○ Instagram  ○ Facebook  ○ TikTok  │                      │
│  │                                    │                      │
│  │ Step 2: Link Account               │                      │
│  │ [@beauty_ig] [Verify ✓]            │                      │
│  │ ↳ Auto-fetch: 500K followers       │                      │
│  │                                    │                      │
│  │ Step 3: Content Strategy           │                      │
│  │ - Categories, Niche, Style         │                      │
│  │ - Portfolio links                  │                      │
│  │                                    │                      │
│  │ Step 4: Audience (optional)        │                      │
│  │ - Age/Gender distribution          │                      │
│  │ - Location, Income level           │                      │
│  │ [Upload analytics screenshot]      │                      │
│  │                                    │                      │
│  │ Step 5: Pricing                    │                      │
│  │ - Rate per post/story/video        │                      │
│  │ - Suggested: 8-12M (based on 500K) │                      │
│  │                                    │                      │
│  │ ✅ FIRST PROFILE ADDED              │                      │
│  │    Overall: 60% complete           │                      │
│  └────────────────────────────────────┘                      │
│                                                              │
│  ↓                                                           │
│                                                              │
│  PHASE 3: ADD MORE PROFILES (Optional, Anytime, 2-5 mins each)│
│  ┌────────────────────────────────────┐                      │
│  │ Dashboard: "Manage Your Profiles"  │                      │
│  │                                    │                      │
│  │ ┌──────────┐ ┌──────────┐          │                      │
│  │ │@beauty_ig│ │@beauty_fb│          │                      │
│  │ │500K ✓    │ │200K ✓    │          │                      │
│  │ │Primary   │ │Active    │          │                      │
│  │ └──────────┘ └──────────┘          │                      │
│  │                                    │                      │
│  │ [+ Add New Profile]                │                      │
│  │                                    │                      │
│  │ ↓ (Click Add New)                  │                      │
│  │                                    │                      │
│  │ Quick Add Flow:                    │                      │
│  │ 1. Select Platform: TikTok         │                      │
│  │ 2. Link: @beauty_tiktok            │                      │
│  │ 3. Auto-fetch: 1M followers ✓      │                      │
│  │ 4. Content: Comedy + Beauty        │                      │
│  │ 5. Pricing: 15M per video          │                      │
│  │                                    │                      │
│  │ ✅ PROFILE ADDED (2 minutes!)       │                      │
│  │                                    │                      │
│  │ 💡 No need to re-enter:            │                      │
│  │    - Your name (already saved)     │                      │
│  │    - Bank account (shared)         │                      │
│  │    - eKYC (already verified)       │                      │
│  │    - Compliance (already consented)│                      │
│  └────────────────────────────────────┘                      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

### Form Comparison: OLD vs NEW

**OLD Model (1:1 - Each Profile Separate):**
```
Register Profile 1 (@beauty_ig):
├─ Name, DOB, ID, Bank → 15 fields
├─ eKYC → 3 minutes
├─ Compliance → 8 checkboxes
├─ Instagram data → 10 fields
└─ TOTAL: 15 minutes

Register Profile 2 (@beauty_fb):
├─ Name, DOB, ID, Bank → 15 fields (DUPLICATE!)
├─ eKYC → 3 minutes (DUPLICATE!)
├─ Compliance → 8 checkboxes (DUPLICATE!)
├─ Facebook data → 10 fields
└─ TOTAL: 15 minutes

Register Profile 3 (@beauty_tiktok):
├─ Name, DOB, ID, Bank → 15 fields (DUPLICATE!)
├─ eKYC → 3 minutes (DUPLICATE!)
├─ Compliance → 8 checkboxes (DUPLICATE!)
├─ TikTok data → 10 fields
└─ TOTAL: 15 minutes

GRAND TOTAL: 45 minutes for 3 profiles ❌
BAD UX: Entering same info 3 times
```

**NEW Model (1:Many - Influencer → Profiles):**
```
Register Influencer (One-Time):
├─ Name, DOB, ID, Bank → 15 fields
├─ eKYC → 3 minutes
├─ Compliance → 8 checkboxes
├─ Finance Affinity → 5 fields
└─ SUBTOTAL: 15 minutes (ONE TIME)

Add Profile 1 (@beauty_ig):
├─ Platform selection → 1 field
├─ Link Instagram → 1 field
├─ Auto-fetch metrics → 0 fields (Diso does it)
├─ Content strategy → 5 fields
├─ Pricing → 3 fields
└─ SUBTOTAL: 5 minutes

Add Profile 2 (@beauty_fb):
├─ Platform selection → 1 field
├─ Link Facebook → 1 field
├─ Content strategy → 5 fields
├─ Pricing → 3 fields
└─ SUBTOTAL: 3 minutes (faster, knows the flow)

Add Profile 3 (@beauty_tiktok):
├─ Platform selection → 1 field
├─ Link TikTok → 1 field
├─ Content strategy → 5 fields
├─ Pricing → 3 fields
└─ SUBTOTAL: 2 minutes (very fast!)

GRAND TOTAL: 25 minutes for 3 profiles ✅
SAVINGS: 20 minutes (44% faster)
GREAT UX: No duplicate data entry
```

---

## Campaign Matching: Profile-Level

### Matching Algorithm Changes

**OLD (Influencer-Level Matching):**
```typescript
// Match campaign to influencer (no platform specificity)
function matchCampaign(campaign: Campaign): Influencer[] {
  return db.query(`
    SELECT * FROM influencer_profiles
    WHERE categories && $1
      AND follower_count >= $2
    ORDER BY engagement_rate DESC
  `, [campaign.categories, campaign.min_followers])
}

// Problem: Cannot specify platform
// If campaign needs Instagram → might match Facebook profile
```

**NEW (Profile-Level Matching):**
```typescript
// Match campaign to specific profiles
interface ProfileMatch {
  influencer: Influencer
  profile: SocialProfile
  matchScore: number
}

function matchCampaign(campaign: Campaign): ProfileMatch[] {
  // Step 1: Filter profiles by platform requirement
  const platformFilter = campaign.platform_required
    ? `AND sp.platform = '${campaign.platform_required}'`
    : ''

  // Step 2: Query profiles (not influencers)
  const results = await db.query(`
    SELECT
      i.*,
      sp.*,
      -- Calculate match score
      (
        CASE WHEN sp.primary_categories && $1 THEN 30 ELSE 0 END +
        CASE WHEN sp.follower_count >= $2 THEN 20 ELSE 0 END +
        CASE WHEN sp.engagement_rate >= $3 THEN 20 ELSE 0 END +
        CASE WHEN i.finance_affinity_score >= $4 THEN 20 ELSE 0 END +
        CASE WHEN sp.age_25_34_pct >= $5 THEN 10 ELSE 0 END
      ) AS match_score
    FROM social_profiles sp
    JOIN influencers i ON sp.influencer_id = i.id
    WHERE sp.profile_status = 'active'
      ${platformFilter}
      AND sp.primary_categories && $1
      AND sp.follower_count >= $2
    ORDER BY match_score DESC, sp.engagement_rate DESC
    LIMIT 20
  `, [
    campaign.categories,
    campaign.min_followers,
    campaign.min_engagement_rate,
    campaign.min_finance_affinity,
    campaign.min_target_age_pct
  ])

  return results.map(row => ({
    influencer: extractInfluencerData(row),
    profile: extractProfileData(row),
    matchScore: row.match_score
  }))
}
```

**Example Matching:**
```
Campaign: "Credit Card for Millennials"
Requirements:
- Platform: Instagram
- Min followers: 100K
- Categories: [finance, lifestyle]
- Audience: 25-34 years old (>30%)
- Finance affinity: >60

Results:
1. Influencer: Nguyễn Văn A
   Profile: @beauty_ig (Instagram, 500K followers)
   Categories: [beauty, lifestyle] ✓
   Audience 25-34: 50% ✓
   Finance Affinity: 82 ✓
   Match Score: 92/100 ✅

   (Not matched: @beauty_fb - wrong platform)
   (Not matched: @beauty_tiktok - wrong audience age)

2. Influencer: Trần Thị B
   Profile: @finance_ig (Instagram, 300K followers)
   Categories: [finance, business] ✓
   Audience 25-34: 60% ✓
   Finance Affinity: 95 ✓
   Match Score: 98/100 ✅

Brand sees:
- 2 influencers matched
- Each with their best-fitting Instagram profile
- Can choose 1 or both
```

---

## Multi-Profile Scenarios

### Scenario 1: Same Niche, Multiple Platforms

**Influencer:** Beauty Creator
```
@beauty_ig (Instagram, 500K)
├─ Categories: Beauty, Skincare
├─ Audience: Women 25-35, high income
├─ Rate: 10M VND per post
└─ Best for: Visual product reviews

@beauty_fb (Facebook, 200K)
├─ Categories: Beauty, Lifestyle
├─ Audience: Women 30-45, medium income
├─ Rate: 5M VND per post
└─ Best for: Community engagement, Q&A

@beauty_tiktok (TikTok, 1M)
├─ Categories: Beauty, Comedy
├─ Audience: Women 18-30, mixed income
├─ Rate: 15M VND per video
└─ Best for: Viral trends, product demos
```

**Campaign Matching:**
```
Campaign 1: "High-end Skincare for Professionals"
→ Match: @beauty_ig (high income audience, visual) ✅
→ Skip: @beauty_tiktok (too young, comedy tone) ❌

Campaign 2: "Budget Beauty Products for Gen Z"
→ Match: @beauty_tiktok (young audience, viral) ✅
→ Skip: @beauty_ig (too premium audience) ❌

Campaign 3: "Multi-Platform Beauty Launch"
→ Match: ALL 3 PROFILES (bundle deal)
   @beauty_ig: 10M
   @beauty_fb: 5M
   @beauty_tiktok: 15M
   Bundle: 27M (3M discount) ✅
```

---

### Scenario 2: Different Niches, Different Platforms

**Influencer:** Multi-Niche Creator
```
@finance_linkedin (LinkedIn, 50K)
├─ Categories: Finance, Investment
├─ Audience: Professionals 30-50, high income
├─ Content: Educational articles, long-form
├─ Rate: 8M VND per article
└─ Best for: B2B finance, professional services

@lifestyle_ig (Instagram, 300K)
├─ Categories: Lifestyle, Travel, Food
├─ Audience: Millennials 25-35, medium-high income
├─ Content: Visual storytelling, inspirational
├─ Rate: 7M VND per post
└─ Best for: Lifestyle brands, consumer products

@comedy_tiktok (TikTok, 800K)
├─ Categories: Comedy, Entertainment
├─ Audience: Gen Z 18-25, mixed income
├─ Content: Short skits, memes
├─ Rate: 12M VND per video
└─ Best for: Viral campaigns, youth brands
```

**Campaign Matching:**
```
Campaign A: "Investment App for Professionals"
→ Match: @finance_linkedin (perfect fit) ✅
→ Skip: @lifestyle_ig, @comedy_tiktok (wrong niche) ❌

Campaign B: "Travel Insurance for Millennials"
→ Match: @lifestyle_ig (travel + millennials) ✅
→ Skip: @finance_linkedin (too serious), @comedy_tiktok (too young) ❌

Campaign C: "Viral Challenge for Soft Drink Brand"
→ Match: @comedy_tiktok (viral potential) ✅
→ Skip: @finance_linkedin, @lifestyle_ig (not comedy) ❌
```

**Key Insight:** Same person, completely different profiles → Separate matching.

---

## Key Insights

### Insight 1: Normalize Data - Eliminate Redundancy ⭐⭐⭐
**Impact:** Very High | **Effort:** Medium

**Problem:**
Current 1:1 model forces influencers to re-enter personal data (name, DOB, bank account, eKYC) for each profile → 40% duplicate data.

**Solution:**
Split into 2 tables:
- `influencers` table: Person-level data (shared)
- `social_profiles` table: Account-level data (profile-specific)

**Benefits:**
- ✅ Enter personal info ONCE → Reused for all profiles
- ✅ Data consistency (no conflicts between profiles)
- ✅ Faster profile addition (2-5 mins vs 15 mins)
- ✅ Better UX (influencers love it)

**Implementation:**
```sql
-- Before (Denormalized)
influencer_profiles:
  name, dob, bank_account, instagram_handle, follower_count, ...

-- After (Normalized)
influencers:
  name, dob, bank_account, ekyc_status, ...

social_profiles:
  influencer_id (FK), platform, handle, follower_count, ...
```

---

### Insight 2: Profile-Level Matching (Not Influencer-Level) ⭐⭐
**Impact:** High | **Effort:** Medium

**Rationale:**
Campaigns care about **specific platform + audience**, not just the influencer.
- Campaign needs Instagram → Match Instagram profiles only
- Campaign needs finance audience → Match finance-focused profiles

**Old Way:**
```
Campaign → Match Influencer → Hope they have right platform
```

**New Way:**
```
Campaign → Match Profile (platform-specific) → Return influencer + their matching profile
```

**Example:**
```
Campaign: "Credit Card for Instagram"
Platform Required: Instagram

OLD: Might match influencer with Facebook profile ❌
NEW: Only matches Instagram profiles ✅

Result:
- Influencer: Nguyễn Văn A
- Profile: @beauty_ig (Instagram, 500K)
- Match Score: 92/100
```

---

### Insight 3: Cross-Profile Analytics & Recommendations ⭐
**Impact:** Medium | **Effort:** Low

**Opportunity:**
Since we have multiple profiles per influencer, we can compare performance across platforms.

**Dashboard Insights:**
```
"Your Instagram performs 2x better than Facebook for beauty campaigns"

Stats:
- @beauty_ig: Avg CTR 4.2%, Avg CVR 1.8%, Revenue 180M
- @beauty_fb: Avg CTR 2.1%, Avg CVR 0.9%, Revenue 60M

Recommendation:
"Focus on Instagram for beauty. Use Facebook for lifestyle/community."
```

**AI Suggestions:**
```
When influencer applies for campaign:

System: "Based on your performance history, we recommend using @beauty_ig for this campaign"
Reason:
- Similar campaigns on IG averaged 4.2% CTR
- Your FB averaged only 2.1% CTR for beauty
- IG audience is 80% female (better match)
```

---

### Insight 4: Multi-Profile Bundle Campaigns ⭐
**Impact:** Medium | **Effort:** Medium

**Use Case:**
Brands want multi-platform presence → Book influencer's 2+ profiles at once.

**Bundle Pricing:**
```
Campaign: "Multi-Platform Beauty Launch"

Individual Rates:
- @beauty_ig: 10M VND
- @beauty_fb: 5M VND
- @beauty_tiktok: 15M VND
Total: 30M VND

Bundle Discount: -3M (10%)
Final Price: 27M VND

Deliverables:
- 3 IG posts + 5 stories
- 2 FB posts + community Q&A
- 1 TikTok viral challenge video
```

**Benefits:**
- Brand: Consistent messaging across platforms
- Influencer: Higher revenue, easier coordination
- Platform: Higher average order value

---

### Insight 5: Profile Lifecycle Management ⭐
**Impact:** Medium | **Effort:** Low

**Need:** Influencers need granular control per profile.

**Profile States:**
```
Active: Available for campaigns
Paused: Temporarily unavailable (reason: maternity leave, platform break)
Under Review: Compliance check or verification pending
Suspended: Violation detected (admin action)
Deleted: Permanently removed
```

**Use Cases:**
```
Scenario 1: Maternity Leave
- Influencer pauses @beauty_ig for 3 months
- @beauty_fb and @beauty_tiktok remain active
- Returns → Reactivate @beauty_ig

Scenario 2: Platform Pivot
- Influencer focuses on TikTok growth
- Pauses @beauty_fb (low performance)
- Keeps @beauty_ig + @beauty_tiktok active

Scenario 3: Compliance Issue
- @beauty_ig flagged for disclosure violation
- Admin suspends @beauty_ig temporarily
- Other profiles unaffected
- After training → Reactivate
```

---

### Insight 6: Fraud Prevention - Profile Verification ⭐⭐
**Impact:** High | **Effort:** Medium

**Risk:**
Influencer A could claim celebrity's account (fraud).

**Solution:**
Require verification per profile (even if same influencer):

**Verification Methods:**

**Option 1: OAuth Connection (Best)**
```
1. Influencer clicks "Link Instagram"
2. Redirects to Instagram OAuth
3. Influencer logs into their Instagram
4. Grants permission
5. System receives access token ✓
6. Profile verified (cannot fake this)
```

**Option 2: Verification Code (Manual)**
```
1. System generates random code: "TCB-VERIFY-8273"
2. Influencer posts code to Instagram story
3. Influencer submits screenshot
4. System auto-detects code in screenshot (OCR)
5. Profile verified ✓
```

**Option 3: DM Verification**
```
1. System sends DM to @beauty_ig: "Reply with code 8273"
2. Influencer receives DM, replies
3. Influencer screenshots reply
4. Submits to platform
5. Manual review → Verified ✓
```

**Best Practice:** OAuth > DM > Manual screenshot

---

### Insight 7: Compliance at Person-Level, Not Profile-Level ⭐⭐
**Impact:** High | **Effort:** Low

**Key Decision:**
Compliance consents (age 18+, eKYC, data privacy, T&C) are from the **PERSON**, not the account.

**Rationale:**
- 1 person = 1 eKYC verification (valid for ALL profiles)
- If person is <18 → CANNOT use ANY profile for finance campaigns
- If person revokes consent → ALL profiles become inactive
- Consent audit trail: Track at influencer level, applies to all profiles

**Implementation:**
```sql
-- Compliance in influencers table (person-level)
influencers:
  age_18_confirmed: true (applies to ALL profiles)
  ekyc_status: 'completed' (done ONCE)
  privacy_consent: true (covers ALL profiles)
  terms_accepted: true (version 2.1, all profiles bound)

-- If influencer revokes privacy_consent:
UPDATE influencers SET privacy_consent = false WHERE id = 'uuid-123';

-- Effect: ALL profiles for this influencer become unavailable
UPDATE social_profiles
SET profile_status = 'suspended'
WHERE influencer_id = 'uuid-123';
```

---

## Migration Strategy (Existing Data)

**Challenge:** Current system has 1000 influencers registered in 1:1 model.

**Migration Steps:**

### Step 1: Data Analysis
```sql
-- Identify potential duplicates (same person, multiple "profiles")
SELECT email, phone, COUNT(*)
FROM influencer_profiles
GROUP BY email, phone
HAVING COUNT(*) > 1;

-- Result: 150 influencers have 2+ entries (same email/phone)
-- → These are actually 1 person with multiple accounts
```

### Step 2: Create New Tables
```sql
-- Create influencers table
CREATE TABLE influencers (...);

-- Create social_profiles table
CREATE TABLE social_profiles (...);
```

### Step 3: Migrate Data
```sql
-- Script to migrate each profile
FOR EACH profile IN influencer_profiles:
  -- Check if influencer already exists (by email/phone)
  influencer = SELECT * FROM influencers WHERE email = profile.email;

  IF influencer NOT EXISTS:
    -- Create new influencer record
    influencer_id = INSERT INTO influencers (
      full_name = profile.full_name,
      dob = profile.dob,
      email = profile.email,
      phone = profile.phone,
      bank_account = profile.bank_account,
      ekyc_status = profile.ekyc_status,
      ...
    ) RETURNING id;
  ELSE:
    -- Use existing influencer (de-duplication)
    influencer_id = influencer.id;
  END IF;

  -- Create profile record
  INSERT INTO social_profiles (
    influencer_id = influencer_id,
    platform = detect_platform(profile.instagram_handle, profile.facebook_url, ...),
    account_handle = profile.instagram_handle OR profile.facebook_handle,
    follower_count = profile.follower_count,
    ...
  );
END FOR;
```

### Step 4: De-Duplication
```
Before Migration:
- influencer_profiles table: 1000 records
  - Same person with Instagram + Facebook = 2 records

After Migration:
- influencers table: 850 unique persons (de-duplicated)
- social_profiles table: 1000 profiles
  - 850 persons have 1 profile
  - 150 persons have 2+ profiles
```

### Step 5: Verification
```
-- Email influencers with multiple profiles:
"We detected you have 2 accounts registered:
- @beauty_ig (Instagram)
- @beauty_fb (Facebook)

We've linked them to your account. Please verify."

[Yes, both are mine] → Merge complete
[No, only @beauty_ig] → Unlink @beauty_fb, ask to re-verify
```

---

## Next Steps & Recommendations

### Immediate (P0 - MVP)
1. ✅ Design database schema (influencers + social_profiles tables)
2. ✅ Create migration script for existing data
3. ✅ Update onboarding flow:
   - Phase 1: Register Influencer
   - Phase 2: Add First Profile
   - Phase 3: Add More Profiles (optional)
4. ✅ Update matching algorithm (profile-level, not influencer-level)
5. ✅ Build "Manage Profiles" dashboard

### Short-Term (P1 - 3 months)
6. Profile verification system (OAuth connection)
7. Cross-profile analytics dashboard
8. Multi-profile bundle pricing
9. Profile lifecycle states (active, paused, suspended)
10. Campaign-specific profile suggestions

### Long-Term (P2 - 6 months)
11. AI-powered profile recommendations ("Use @beauty_ig for this campaign")
12. Automated profile performance comparison
13. Profile specialization tags (#finance, #beauty, #viral)
14. Shared content library (photos/videos accessible to all profiles)
15. Profile quality scores (completeness, engagement, revenue)

---

## Technical Considerations

### Performance
- **Index strategy:** Profile lookups must be fast (campaign matching)
- **Caching:** Cache influencer data (rarely changes), invalidate on update
- **Pagination:** Profile lists can be large (influencer with 5+ profiles)

### Security
- **OAuth tokens:** Encrypt access tokens for social profiles
- **Verification:** Require proof of ownership per profile (prevent fraud)
- **Consent tracking:** Audit trail for compliance (person-level, affects all profiles)

### Scalability
- **Database size:** 850 influencers × avg 1.5 profiles = 1,275 profiles (manageable)
- **Matching queries:** Profile-level queries need proper indexes
- **Data sync:** Diso crawls profiles regularly (Source 2) → Update metrics

---

## Conclusion

Splitting **Influencer (Person)** from **Profile (Social Account)** is a **critical architectural decision** that:

✅ **Eliminates 40% data redundancy** (personal info entered once)
✅ **Improves UX dramatically** (add profile in 2-5 mins vs 15 mins)
✅ **Enables profile-specific matching** (right platform for right campaign)
✅ **Unlocks cross-profile analytics** (compare performance, recommendations)
✅ **Supports multi-profile campaigns** (bundle deals, multi-platform)
✅ **Ensures compliance** (person-level consents, single eKYC)

**Key Insight:**
```
1 Person ≠ 1 Social Account
1 Person = 1 Identity + Many Social Accounts

Therefore:
Ask personal info ONCE → Reuse for all accounts
Match campaigns to PROFILES (not persons)
Track compliance at PERSON level (applies to all profiles)
```

**Recommendation:**
Implement this **BEFORE launch** to avoid painful migration later. The longer we wait, the more data to migrate.

---

*Generated by BMAD Method v6 - Creative Intelligence*
*Techniques: Mind Mapping, SCAMPER, Six Thinking Hats*
*Session duration: 30 minutes*
*Total insights: 7 actionable recommendations*
