# Brainstorming Session: Pub2 Affiliate Integration vào at-core

**Date:** 2026-02-07
**Objective:** Thiết kế kiến trúc tích hợp hệ thống affiliate Pub2 vào Techcombank và at-core (TCB, Ambassador, Vinfast)
**Context:** Techcombank hiện có booking system với view-based rewards. Pub2 (AccessTrade) cung cấp full affiliate platform (campaigns, link generation, tracking, commission). Influencer accounts đã được liên kết giữa 2 hệ thống.

---

## Executive Summary

**Recommended Approach:** API Proxy Model (Insight #1)
- at-core proxy Pub2 APIs để cung cấp native UX
- Influencer browse campaigns, generate links, track performance in-app
- Không cần deep data sync (giảm complexity)
- Time-to-market: 4-6 tuần cho MVP

**Critical Design Decisions:**
1. **Multi-tenant config layer** (Insight #2) - P0 blocking requirement
2. **Attribution via sub_id parameters** (Insight #3) - Foundation cho analytics
3. **Webhook + Polling hybrid** (Insight #4) - Production-grade reliability
4. **Fraud prevention từ đầu** (Insight #7) - Protect platform integrity

**Expected Value:**
- Dual income stream cho influencers (view rewards + affiliate commission)
- Competitive differentiation (unique value prop)
- Rich data insights (content-to-commerce correlation)
- Network effects qua multi-tenant platform

---

## Techniques Used

1. **SWOT Analysis** - Đánh giá strategic fit
2. **Mind Mapping** - Cấu trúc architecture options
3. **Starbursting** - Khám phá requirements chi tiết (Who/What/Where/When/Why/How)

---

## SWOT Analysis

### Strengths
- **S1. Liên kết tài khoản sẵn có** - TCB influencer ↔ Pub2 user SSO đã hoạt động
- **S2. Pub2 API đầy đủ chức năng** - Mature system với campaign management, tracking, payout
- **S3. Architecture phân tách rõ ràng** - View rewards (at-core) vs Affiliate (Pub2) = separate concerns
- **S4. Multi-tenant foundation đã có** - at-core thiết kế cho TCB, Ambassador, Vinfast
- **S5. ViewBoost không maintain affiliate logic** - Pub2 handle complexity, ViewBoost chỉ integrate

### Weaknesses
- **W1. Dual reward system phức tạp** - Risk user confusion, báo cáo tổng hợp challenging
- **W2. Dependency vào Pub2 API** - Downtime/changes ảnh hưởng feature, no roadmap control
- **W3. Data synchronization challenge** - Video data (TCB) vs Campaign/Order (Pub2) cần sync
- **W4. Attribution complexity** - View tracking vs Click tracking, multi-touch attribution unclear
- **W5. Source code ownership constraint** - AT bán source → tenant-specific Pub2 config tricky

### Opportunities
- **O1. Tăng revenue cho influencer** - Dual income stream → platform retention
- **O2. Expand use cases** - Product reviews, tutorials, unboxing → mở rộng verticals
- **O3. Data insights mới** - View ↔ conversion correlation, high-converting profiles, ML opportunities
- **O4. Competitive advantage** - Unique dual-reward model → market differentiation
- **O5. Cross-sell opportunities** - Network effects giữa Ambassador/Vinfast/TCB influencers
- **O6. White-label cho clients** - Tenants tự config campaigns → client autonomy

### Threats
- **T1. Pub2 API breaking changes** - Version incompatibility, deprecated endpoints
- **T2. Regulatory compliance** - Affiliate disclosure laws, tax reporting, GDPR/PDPA
- **T3. User confusion** - Quá nhiều reward types, complicated payout schedules
- **T4. Fraud risks** - Fake clicks, self-clicking, view + click manipulation
- **T5. Technical complexity** - Integration bugs, performance degradation, maintenance overhead
- **T6. Business relationship risks** - Pub2 pricing changes, service termination, contract disputes
- **T7. Competitor response** - Model được copy, price wars, feature parity

---

## Integration Models (5 Options)

### 1.1 Link-Only Model (Simplest)
**Approach:** Influencer tự tạo link trên Pub2, paste vào video description
**Pros:** Zero development cost
**Cons:** Không tracking, không automation, poor UX
**Verdict:** ❌ Không đủ value

### 1.2 Widget Embed Model
**Approach:** Iframe embed Pub2 campaign widget vào at-core UI
**Pros:** Low dev effort (1-2 tuần)
**Cons:** UX disconnect, external redirect, branding inconsistency
**Verdict:** ⚠️ Acceptable cho proof-of-concept

### 1.3 API Proxy Model ⭐ RECOMMENDED MVP
**Approach:** at-core proxy Pub2 APIs, native UX cho campaign browsing & link generation
**Pros:**
- Native UX, no external redirects
- Full UI/branding control
- Moderate complexity (4-6 tuần)
- Can evolve to Deep Integration later
- 100% clean source code ownership

**Cons:**
- Moderate effort vs Widget Embed
- Dependency on Pub2 API stability

**Verdict:** ✅ Best balance cho MVP

### 1.4 Deep Integration Model
**Approach:** Sync Pub2 campaigns vào at-core DB, webhook listeners, unified dashboard
**Pros:** Best UX, full analytics control, offline capability
**Cons:** High complexity (3+ tháng), sync overhead, data consistency challenges
**Verdict:** 🔮 Future enhancement sau khi validate MVP

### 1.5 Hybrid Revenue Share Model
**Approach:** Smart contract/blockchain cho dual payout, transparent audit trail
**Pros:** Future-proof, transparent, decentralized
**Cons:** Very complex, overkill, no proven demand
**Verdict:** ❌ Không phù hợp hiện tại

---

## Architecture Components (API Proxy Model)

### Backend Services

```typescript
// Pub2 API Client
class Pub2ApiClient {
  async getCampaigns(apiKey: string): Promise<Campaign[]>
  async createAffiliateLink(params: LinkParams): Promise<string>
  async getClickStats(linkId: string): Promise<ClickStats>
  async getConversions(params: ConversionQuery): Promise<Conversion[]>
}

// Campaign Sync Service (optional caching layer)
class CampaignSyncService {
  // Background job: Sync campaigns hourly
  async syncCampaigns(tenantId: string): Promise<void>
  // Invalidate cache on webhook "campaign_ended"
  async invalidateCampaign(campaignId: string): Promise<void>
}

// Webhook Handler
class WebhookHandler {
  async handleClickEvent(payload: ClickWebhook): Promise<void>
  async handleConversionEvent(payload: ConversionWebhook): Promise<void>
  async handleCommissionUpdate(payload: CommissionWebhook): Promise<void>
}

// Attribution Service
class AttributionService {
  // Extract video_id from sub_id_1
  async attributeConversionToVideo(conversion: Conversion): Promise<void>
  // Calculate combined earnings (view + affiliate)
  async calculateTotalEarnings(videoId: string): Promise<Earnings>
}
```

### Data Models

```sql
-- Tenant-specific Pub2 configuration
CREATE TABLE tenant_pub2_config (
  tenant_id VARCHAR(50) PRIMARY KEY,
  pub2_api_key VARCHAR(255) ENCRYPTED,  -- KMS encrypted
  pub2_account_id VARCHAR(100),
  enabled BOOLEAN DEFAULT false,
  campaign_whitelist JSONB,  -- Allowed category IDs
  campaign_blacklist JSONB,  -- Blocked campaign IDs
  commission_share_pct DECIMAL(5,2),  -- Platform fee if applicable
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Influencer ↔ Pub2 account linking
CREATE TABLE influencer_pub2_accounts (
  id UUID PRIMARY KEY,
  influencer_id UUID REFERENCES influencers(id),
  pub2_user_id VARCHAR(100),
  link_status VARCHAR(20),  -- 'active' | 'inactive' | 'pending'
  linked_at TIMESTAMP,
  updated_at TIMESTAMP,
  UNIQUE(influencer_id, pub2_user_id)
);

-- Generated affiliate links (cached for reference)
CREATE TABLE pub2_affiliate_links (
  id UUID PRIMARY KEY,
  influencer_id UUID REFERENCES influencers(id),
  video_id UUID REFERENCES videos(id),
  campaign_id VARCHAR(100),  -- Pub2 campaign ID
  affiliate_url TEXT,
  sub_id_1 VARCHAR(100),  -- video_id (for attribution)
  sub_id_2 VARCHAR(100),  -- tenant_id (for isolation)
  created_at TIMESTAMP,
  status VARCHAR(20) DEFAULT 'active'  -- 'active' | 'inactive' | 'flagged'
);

-- Click events (synced from Pub2 via webhook/polling)
CREATE TABLE pub2_click_events (
  id UUID PRIMARY KEY,
  link_id UUID REFERENCES pub2_affiliate_links(id),
  event_id VARCHAR(100) UNIQUE,  -- Pub2's event ID (for idempotency)
  clicked_at TIMESTAMP,
  ip_address INET,  -- For fraud detection
  user_agent TEXT,
  created_at TIMESTAMP
);

-- Conversions (purchases)
CREATE TABLE pub2_conversions (
  id UUID PRIMARY KEY,
  link_id UUID REFERENCES pub2_affiliate_links(id),
  event_id VARCHAR(100) UNIQUE,  -- Pub2's conversion ID
  order_id VARCHAR(100),
  order_value DECIMAL(10,2),
  commission DECIMAL(10,2),
  commission_status VARCHAR(20),  -- 'pending' | 'confirmed' | 'paid'
  purchased_at TIMESTAMP,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Webhook audit logs
CREATE TABLE pub2_webhook_logs (
  id UUID PRIMARY KEY,
  webhook_type VARCHAR(50),  -- 'click' | 'conversion' | 'commission_update'
  payload JSONB,
  processed BOOLEAN DEFAULT false,
  error TEXT,
  received_at TIMESTAMP,
  processed_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_links_video ON pub2_affiliate_links(video_id);
CREATE INDEX idx_links_influencer ON pub2_affiliate_links(influencer_id);
CREATE INDEX idx_clicks_link ON pub2_click_events(link_id);
CREATE INDEX idx_conversions_link ON pub2_conversions(link_id);
CREATE INDEX idx_conversions_status ON pub2_conversions(commission_status);
```

### Frontend Components

```typescript
// Campaign Browser
<CampaignBrowser>
  - List campaigns filtered by tenant
  - Search, filter by category, commission rate
  - Campaign details modal
  - "Generate Link" CTA

// Affiliate Link Generator
<AffiliateLinkGenerator>
  - Select campaign
  - Select video (for attribution)
  - Generate link → Copy to clipboard
  - Auto-suggest relevant campaigns for video

// Unified Dashboard
<UnifiedDashboard>
  - Total earnings (view + affiliate)
  - Breakdown by revenue type
  - Top performing videos by total earnings
  - Metrics: CTR, CVR, avg order value

// Affiliate Performance Table
<AffiliatePerformanceTable>
  - List all affiliate links
  - Metrics per link: clicks, conversions, commission
  - Actions: Deactivate link, view analytics
```

---

## Multi-Tenant Strategy

### Tenant-Level Configuration

**Database Schema:** (see `tenant_pub2_config` above)

**Admin UI:**
```
Tenant Settings → Integrations → Pub2 Affiliate

[ ] Enable Pub2 Integration

API Configuration:
  Pub2 API Key: *********************** [Show] [Rotate]
  Pub2 Account ID: AT123456

Campaign Filtering:
  Allowed Categories: [Banking] [Finance] [Insurance]
  Blocked Campaigns: [Add Campaign ID]

Commission Settings:
  Platform Fee: 0% (optional)
  Min Commission Rate: 5.0%

[Save Configuration]
```

**Example Configs:**

```typescript
// Techcombank
const tcbConfig = {
  allowedCategories: ['banking', 'finance', 'insurance'],
  blockedCampaigns: [],  // Specific competitor campaigns
  minCommissionRate: 5.0
};

// Vinfast
const vinfastConfig = {
  allowedCategories: ['automotive', 'ev', 'accessories', 'insurance'],
  blockedCampaigns: [],
  minCommissionRate: 3.0
};

// Ambassador (generic, all campaigns)
const ambassadorConfig = {
  allowedCategories: [],  // Empty = all categories
  blockedCampaigns: [],
  minCommissionRate: 2.0
};
```

### Campaign Filtering Logic

```typescript
async function getAvailableCampaigns(tenantId: string, influencerId: string) {
  // Layer 1: Fetch from Pub2 (or cache)
  const config = await getTenantPub2Config(tenantId);
  const allCampaigns = await pub2Client.getCampaigns(config.pub2ApiKey);

  // Layer 2: Tenant whitelist/blacklist
  const tenantFiltered = allCampaigns.filter(campaign => {
    // If whitelist exists, only show whitelisted categories
    if (config.allowedCategories.length > 0) {
      if (!config.allowedCategories.includes(campaign.category)) {
        return false;
      }
    }

    // Blacklist specific campaigns
    if (config.blockedCampaigns.includes(campaign.id)) {
      return false;
    }

    // Min commission rate
    if (campaign.commissionRate < config.minCommissionRate) {
      return false;
    }

    return true;
  });

  // Layer 3: Influencer eligibility (future enhancement)
  // e.g., Premium influencers get exclusive high-commission campaigns

  return tenantFiltered;
}
```

---

## Data Flow

### 1. Campaign Discovery Flow

```
┌─────────────┐       ┌──────────────┐       ┌─────────┐       ┌───────────┐
│ Influencer  │──────▶│  at-core UI  │──────▶│ Backend │──────▶│  Pub2 API │
│   (User)    │       │              │       │         │       │           │
└─────────────┘       └──────────────┘       └─────────┘       └───────────┘
                                                    │
                                                    ▼
                                          [Tenant Filtering]
                                                    │
                                                    ▼
                                          [Cache in Redis]
                                                    │
                                                    ▼
                                          [Return to Frontend]
```

### 2. Link Generation Flow

```
┌─────────────┐       ┌──────────────┐       ┌─────────┐       ┌───────────┐
│ Select      │──────▶│ POST /api/   │──────▶│ Fetch   │──────▶│ Pub2 API  │
│ Campaign    │       │ affiliate-   │       │ Tenant  │       │ POST      │
│             │       │ links        │       │ API Key │       │ /create-  │
│             │       │              │       │         │       │ link      │
└─────────────┘       └──────────────┘       └─────────┘       └───────────┘
                                                                      │
                      ┌───────────────────────────────────────────────┘
                      ▼
              [Store in pub2_affiliate_links table]
                      │
                      ▼
              [Return link to frontend]
```

**Link Parameters:**
```json
{
  "campaign_id": "camp_12345",
  "publisher_id": "pub2_user_789",
  "sub_id_1": "vid_abc123",       // video_id for attribution
  "sub_id_2": "tcb",               // tenant_id for isolation
  "sub_id_3": "banking"            // campaign category
}
```

### 3. Click Tracking Flow

```
┌──────────┐       ┌───────────┐       ┌─────────┐       ┌──────────────┐
│ End User │──────▶│ Affiliate │──────▶│  Pub2   │──────▶│   Merchant   │
│          │       │   Link    │       │ Tracks  │       │   Website    │
└──────────┘       └───────────┘       └─────────┘       └──────────────┘
                                              │
                                              ▼
                                    [Webhook to at-core]
                                              │
                                              ▼
                                    POST /webhooks/pub2/clicks
                                              │
                                              ▼
                                    [Store in pub2_click_events]
                                              │
                                              ▼
                                    [Update dashboard cache]
```

### 4. Conversion Tracking Flow

```
┌──────────┐       ┌──────────────┐       ┌─────────┐       ┌──────────────┐
│ End User │──────▶│   Purchase   │──────▶│  Pub2   │──────▶│   at-core    │
│          │       │   Product    │       │ Detects │       │   Webhook    │
└──────────┘       └──────────────┘       └─────────┘       └──────────────┘
                                                                    │
                                                                    ▼
                                                          [Verify event_id]
                                                          [Check duplicates]
                                                                    │
                                                                    ▼
                                                        [Store in pub2_conversions]
                                                                    │
                                                                    ▼
                                                        [Attribute to video via sub_id_1]
                                                                    │
                                                                    ▼
                                                        [Update video.affiliate_earnings]
                                                                    │
                                                                    ▼
                                                        [Notify influencer]
```

### 5. Payout Flow (Combined)

```
┌─────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│   at-core       │──────▶│  Calculate Total │──────▶│  Generate       │
│   Payout Job    │       │  (View + Affil)  │       │  Payout Report  │
└─────────────────┘       └──────────────────┘       └─────────────────┘
                                                              │
                                                              ▼
                                                    ┌──────────────────┐
                                                    │ Influencer Payout│
                                                    │ - View: $800     │
                                                    │ - Affil: $450    │
                                                    │ Total: $1,250    │
                                                    └──────────────────┘
```

---

## User Experience Scenarios

### Scenario 1: Product Review Video

**Flow:**
1. Influencer tạo review video cho "TCB Credit Card"
2. Trong video creation flow → Click "Add Affiliate Links"
3. at-core suggests relevant campaigns:
   - "TCB Platinum Credit Card - 8% commission"
   - "Travel Insurance Bundle - 5% commission"
4. Influencer selects campaign → Generate link
5. Link auto-copied to clipboard
6. Influencer pastes vào video description
7. Publish video
8. Dashboard shows:
   - Views: 5,200 → View reward: $260
   - Clicks: 234 → Conversions: 12 → Commission: $120
   - **Total earnings: $380**

**UX Highlights:**
- AI suggests campaigns based on video content/title
- One-click link generation
- Unified metrics dashboard

---

### Scenario 2: Campaign-First Approach

**Flow:**
1. Influencer browses "High Commission Campaigns"
2. Finds "New EV Charging Station - 15% commission"
3. Click "Create Video for This Campaign"
4. at-core opens video creator with campaign pre-selected
5. Influencer shoots video về charging station
6. Link auto-generated on publish
7. Track performance

**UX Highlights:**
- Reverse workflow (campaign → video instead of video → campaign)
- Gamification: Leaderboard by commission earnings
- Campaign deadlines visible (urgency)

---

### Scenario 3: Bulk Link Management

**Flow:**
1. Influencer có 20 evergreen banking videos
2. Navigate to "My Affiliate Links" page
3. Table shows all links with performance metrics
4. Bulk action: "Update all banking videos with new campaign"
5. Select new campaign → Bulk generate links
6. Export link list → Update video descriptions

**UX Highlights:**
- Bulk operations for power users
- Performance comparison (old vs new campaign)
- Export to CSV for external tools

---

## Technical Challenges & Solutions

### Challenge 1: API Rate Limits

**Problem:** Pub2 API có rate limits (e.g., 1000 req/hour)

**Solutions:**
1. **Aggressive caching:**
   - Campaign list: Cache 1 hour in Redis
   - Campaign details: Cache 6 hours
   - Invalidate on webhook "campaign_ended"

2. **Background sync jobs:**
   - Scheduled sync thay vì on-demand
   - Predictable load, avoid spikes

3. **Request batching:**
   - Fetch multiple campaigns in one API call
   - Batch link generation if Pub2 supports

4. **Graceful degradation:**
   - Show cached data if API quota exceeded
   - "Data may be up to 1 hour old" warning

---

### Challenge 2: Data Consistency

**Problem:** Pub2 data thay đổi (campaign ends, commission updates) nhưng at-core có cached data

**Solutions:**
1. **Webhooks cho urgent updates:**
   - Campaign ended → Immediate cache invalidation
   - Commission rate changed → Update cached data

2. **TTL-based expiry:**
   - All cached data có TTL
   - Auto-refresh sau expiry

3. **Reconciliation jobs:**
   - Daily job: Compare at-core vs Pub2 data
   - Flag discrepancies for review
   - Auto-fix if diff < threshold

4. **Manual refresh button:**
   - Influencer có thể force refresh
   - Rate-limited (max 1x per 5 minutes)

---

### Challenge 3: Attribution Window

**Problem:** User clicks link today, mua hàng 25 ngày sau. Làm sao track?

**Solutions:**
1. **Rely on Pub2's attribution:**
   - Pub2 tracks cookies/fingerprints
   - Standard 30-day window
   - Webhook fires khi conversion xảy ra

2. **sub_id parameters persist:**
   - video_id, tenant_id embedded trong link
   - Pub2 returns khi webhook

3. **Retroactive updates:**
   - Conversion webhook → Update video earnings
   - Even if video đã published weeks ago

4. **Clear communication:**
   - Dashboard shows "Pending conversions (30-day window)"
   - Estimated earnings vs confirmed earnings

---

### Challenge 4: Multi-Touch Attribution

**Problem:** User clicks Influencer A's link, sau đó clicks Influencer B's link, rồi mua. Ai nhận commission?

**Solutions:**
1. **Last-click wins (RECOMMENDED for MVP):**
   - Influencer B nhận 100% commission
   - Simple, industry standard
   - Pub2 likely uses this model

2. **First-click wins (alternative):**
   - Influencer A nhận credit
   - Rare in affiliate marketing

3. **Split commission (complex, future):**
   - A nhận 40%, B nhận 60%
   - Requires custom logic, not standard Pub2

**Decision:** Accept Pub2's attribution model (likely last-click)

---

### Challenge 5: Cross-Platform Tracking

**Problem:** User clicks link trên mobile, mua trên desktop. Cookie không sync.

**Solutions:**
1. **Rely on Pub2's tracking tech:**
   - Device fingerprinting
   - Cross-device tracking (if Pub2 supports)
   - Email matching (advanced)

2. **Accept limitation:**
   - Some conversions không tracked → Acceptable loss
   - Industry standard problem

3. **Educate influencers:**
   - Explain why conversion rate < 100%
   - Set realistic expectations

---

## Security & Compliance

### API Key Security

**Storage:**
```typescript
// Use KMS encryption
import { KMS } from 'aws-sdk';

async function storeApiKey(tenantId: string, apiKey: string) {
  const kms = new KMS();

  // Encrypt API key
  const encrypted = await kms.encrypt({
    KeyId: process.env.KMS_KEY_ID,
    Plaintext: apiKey
  });

  // Store encrypted value
  await db.query(
    'UPDATE tenant_pub2_config SET pub2_api_key = $1 WHERE tenant_id = $2',
    [encrypted.CiphertextBlob, tenantId]
  );
}

async function getApiKey(tenantId: string): Promise<string> {
  const result = await db.query(
    'SELECT pub2_api_key FROM tenant_pub2_config WHERE tenant_id = $1',
    [tenantId]
  );

  // Decrypt only when needed
  const kms = new KMS();
  const decrypted = await kms.decrypt({
    CiphertextBlob: result.rows[0].pub2_api_key
  });

  return decrypted.Plaintext.toString();
}
```

**Access Control:**
- Admin UI: Only tenant owner can view/edit API key
- API: Middleware validates tenant context
- Logs: Redact API keys from all logs

**Rotation Policy:**
- Tenant can rotate key anytime
- 24-hour grace period for inflight requests
- Notify influencers if key rotation affects links

---

### Fraud Prevention

**Multi-Layer Defense:**

```typescript
// Layer 1: Rate limiting
const CLICK_RATE_LIMIT = 100; // Max 100 clicks/day per link
const CONVERSION_RATE_LIMIT = 10; // Max 10 conversions/day

// Layer 2: Pattern detection
async function detectFraudPatterns(linkId: string) {
  const stats = await getAffiliateStats(linkId);
  const warnings = [];

  // Red flag: Very high CTR (>50% suspicious)
  if (stats.ctr > 0.5) {
    warnings.push('Abnormally high CTR');
  }

  // Red flag: Low IP diversity
  const uniqueIps = await getUniqueClickIps(linkId);
  if (uniqueIps.length < stats.clicks * 0.3) {
    warnings.push('Low IP diversity - possible bot traffic');
  }

  // Red flag: Self-clicking
  const influencerClicks = await getInfluencerSelfClicks(linkId);
  if (influencerClicks > 5) {
    warnings.push('Self-clicking detected');
  }

  // Red flag: High clicks, zero conversions
  if (stats.clicks > 100 && stats.conversions === 0) {
    warnings.push('Low conversion despite high clicks');
  }

  return warnings;
}

// Layer 3: Auto-flagging
if (warnings.length > 0) {
  await db.query(
    'UPDATE pub2_affiliate_links SET status = $1 WHERE id = $2',
    ['flagged', linkId]
  );
  await notifyAdmin({
    linkId,
    influencerId,
    warnings,
    autoActions: ['Link disabled', 'Pending review']
  });
}

// Layer 4: Pub2's fraud detection (external)
// Trust Pub2's built-in systems for device fingerprinting, VPN detection, etc.
```

**Policy Recommendations:**
- Terms of Service: Explicit ban on self-clicking, fraud
- Consequences: First offense = warning, repeat = account suspension
- Manual review: Admin dashboard for flagged links
- Cooldown: New influencers limited to 5 links/day for first month

---

### Disclosure Requirements

**Compliance:**
- FTC guidelines (US): Affiliate links must be disclosed
- ASA guidelines (UK): "Ad" or "#ad" required
- Local regulations: Vietnam, Thailand, etc.

**Implementation:**

```typescript
// Auto-insert disclosure template
const DISCLOSURE_TEMPLATE = `
⚠️ Affiliate Disclosure: Các link trong video này là affiliate links.
Khi bạn mua hàng qua link, tôi có thể nhận hoa hồng mà không làm tăng giá cho bạn.
Cảm ơn bạn đã ủng hộ!
`;

// Video creation flow
async function publishVideo(videoData) {
  // Check if video has affiliate links
  const hasAffiliateLinks = videoData.affiliateLinks.length > 0;

  if (hasAffiliateLinks && !videoData.description.includes('Affiliate Disclosure')) {
    // Auto-prepend disclosure
    videoData.description = DISCLOSURE_TEMPLATE + '\n\n' + videoData.description;

    // Warn user
    await showWarning('Affiliate disclosure added to your video description');
  }

  await saveVideo(videoData);
}
```

**Compliance Checker:**
- Admin dashboard: Report videos với affiliate links nhưng thiếu disclosure
- Auto-reminder: Email influencer nếu published video thiếu disclosure
- Legal review: Quarterly audit of disclosure compliance

---

### Data Privacy

**GDPR/PDPA Compliance:**

```typescript
// Click tracking consent
async function trackClick(linkId: string, userId: string) {
  // Check user consent
  const consent = await getUserConsent(userId);

  if (!consent.analytics) {
    // Don't store IP, user agent if no consent
    await db.query(
      'INSERT INTO pub2_click_events (link_id, clicked_at) VALUES ($1, $2)',
      [linkId, new Date()]
    );
  } else {
    // Store full data
    await db.query(
      'INSERT INTO pub2_click_events (link_id, ip_address, user_agent, clicked_at) VALUES ($1, $2, $3, $4)',
      [linkId, req.ip, req.headers['user-agent'], new Date()]
    );
  }
}

// Data retention
// Auto-delete click events older than 2 years
// Keep aggregated stats only
```

**User Rights:**
- Right to access: API endpoint to export all user data
- Right to deletion: Delete click history, anonymize conversions
- Right to portability: Export data in JSON format

---

## Monitoring & Analytics

### Health Monitoring

**Metrics to Track:**

```typescript
// Pub2 API Health
metrics.gauge('pub2.api.uptime', uptimePercentage);
metrics.gauge('pub2.api.latency_p95', latency);
metrics.counter('pub2.api.errors', { error_type: '500' });

// Webhook Delivery
metrics.gauge('pub2.webhook.delivery_rate', deliveryRate);
metrics.counter('pub2.webhook.failed', { webhook_type: 'click' });

// Sync Jobs
metrics.gauge('pub2.sync.lag_minutes', lagTime);
metrics.counter('pub2.sync.discrepancies', { severity: 'high' });

// Business Metrics
metrics.counter('pub2.links.generated', { tenant_id: 'tcb' });
metrics.counter('pub2.conversions.total', { tenant_id: 'tcb' });
metrics.gauge('pub2.revenue.total_usd', totalRevenue);
```

**Alerting Rules:**
```yaml
alerts:
  - name: Pub2APIDown
    condition: pub2.api.uptime < 95%
    severity: critical
    notify: pagerduty

  - name: WebhookDeliveryLow
    condition: pub2.webhook.delivery_rate < 90%
    severity: warning
    notify: slack

  - name: HighSyncLag
    condition: pub2.sync.lag_minutes > 120
    severity: warning
    notify: email

  - name: ReconciliationDiscrepancy
    condition: pub2.sync.discrepancies > 10
    severity: warning
    notify: slack
```

---

### Business Analytics Dashboard

**Influencer-Facing Metrics:**

```
┌──────────────────────────────────────────────────┐
│  MY PERFORMANCE THIS MONTH                       │
├──────────────────────────────────────────────────┤
│  TOTAL EARNINGS: $1,250  ⬆ +15%                 │
│                                                  │
│  📹 View Rewards:        $800 (64%)             │
│     10 videos • 45K views                        │
│                                                  │
│  🔗 Affiliate Commission: $450 (36%)            │
│     23 conversions • $9,800 sales                │
│                                                  │
│  KEY METRICS                                     │
│  CTR (Click-Through):     4.5%                   │
│  CVR (Conversion):        9.8%                   │
│  Avg Order Value:         $426                   │
│  Commission per View:     $0.01                  │
│                                                  │
│  TOP VIDEOS BY TOTAL EARNINGS                    │
│  1. TCB Credit Card Review  - $380              │
│  2. Best Savings Account    - $285              │
│  3. Investment Tips         - $210              │
└──────────────────────────────────────────────────┘
```

**Admin-Facing Metrics:**

```
┌──────────────────────────────────────────────────┐
│  PLATFORM AFFILIATE PERFORMANCE                  │
├──────────────────────────────────────────────────┤
│  Total Revenue (All Tenants): $45,230           │
│  - TCB:        $28,500 (63%)                     │
│  - Ambassador: $12,100 (27%)                     │
│  - Vinfast:    $4,630 (10%)                      │
│                                                  │
│  TOP INFLUENCERS BY COMMISSION                   │
│  1. Alice Nguyen (TCB)      - $2,340            │
│  2. Bob Tran (Ambassador)   - $1,890            │
│  3. Carol Le (TCB)          - $1,650            │
│                                                  │
│  TOP CAMPAIGNS BY CONVERSION                     │
│  1. TCB Platinum Card       - 12.3% CVR         │
│  2. VinFast VF8 Test Drive  - 8.7% CVR          │
│  3. Travel Insurance        - 6.5% CVR          │
│                                                  │
│  SYSTEM HEALTH                                   │
│  Pub2 API Uptime:      99.2%                     │
│  Webhook Delivery:     97.8%                     │
│  Sync Lag:             12 min (avg)              │
└──────────────────────────────────────────────────┘
```

---

## Key Insights

### Insight 1: API Proxy Model là Sweet Spot cho MVP ⭐
**Impact:** High | **Effort:** Medium | **Priority:** P0

**Description:**
Integration qua API Proxy cung cấp balance tốt nhất giữa effort và value. Native UX, full control, moderate complexity (4-6 tuần vs 3+ tháng cho Deep Integration).

**Why it matters:**
- Time-to-market nhanh
- Không embed Pub2 components (source ownership clean)
- Có thể evolve sang Deep Integration sau validation
- Tenant flexibility (enable/disable per tenant)

---

### Insight 2: Multi-Tenant Config Layer là Critical Requirement ⭐
**Impact:** High | **Effort:** Medium | **Priority:** P0

**Description:**
Mỗi tenant (TCB, Ambassador, Vinfast) PHẢI có isolated Pub2 credentials, campaign filtering, và revenue tracking. Không phải optional mà là foundational architecture.

**Why it matters:**
- Business model: AT bán source → tenants tự quản lý
- Security: API keys isolation
- Relevance: Campaign filtering by vertical
- Compliance: Separate legal entities
- White-label: Tenant autonomy

**Schema:**
```sql
tenant_pub2_config:
  - tenant_id
  - pub2_api_key (encrypted)
  - campaign_whitelist/blacklist
  - commission_share_pct
```

---

### Insight 3: Attribution via sub_id Parameters ⭐
**Impact:** High | **Effort:** Low | **Priority:** P0

**Description:**
Encode video_id và tenant_id vào Pub2's sub_id_1, sub_id_2 parameters. Đây là foundation cho tất cả analytics và revenue attribution.

**Why it matters:**
- Video performance tracking (video nào drive sales?)
- Influencer insights (optimize content strategy)
- Revenue attribution (chính xác per video, per tenant)
- Fraud detection (unusual patterns)
- Multi-tenant isolation

**Implementation:**
```typescript
pub2.createLink({
  sub_id_1: video.id,    // "vid_abc123"
  sub_id_2: tenant.id,   // "tcb"
  sub_id_3: campaign.category
});
```

---

### Insight 4: Webhook + Polling Hybrid = Reliability ⭐
**Impact:** High | **Effort:** Medium | **Priority:** P0

**Description:**
Webhooks cho real-time updates, polling reconciliation jobs như safety net. Single point of failure không acceptable cho financial data.

**Why it matters:**
- Webhook failures happen (network, downtime, bugs)
- Financial accuracy critical (commission must be 100% correct)
- Influencer trust phụ thuộc accurate reporting
- Tax compliance requires perfect data
- Debugging: Reconciliation reveals systematic issues

**Pattern:**
- Primary: Webhooks (fast UX)
- Backup: Daily reconciliation jobs
- Monitoring: Alert if webhook delivery < 95%

---

### Insight 5: Unified Dashboard Design Drives Adoption
**Impact:** High | **Effort:** Low | **Priority:** P1

**Description:**
Hiển thị "Total Earnings" (view + affiliate) prominently, breakdown rõ ràng, actionable metrics (CTR, CVR).

**Why it matters:**
- User psychology: Total number motivates
- Transparency builds trust
- Actionable insights help optimize
- Gamification opportunities
- Reduce support tickets

**Key metrics:**
- Total earnings (headline)
- Breakdown (view vs affiliate)
- Performance (CTR, CVR, AOV)
- Trends (week-over-week)

---

### Insight 6: Campaign Filtering = Competitive Moat
**Impact:** Medium | **Effort:** Low | **Priority:** P1

**Description:**
Tenant-specific filtering (banking cho TCB, automotive cho Vinfast) không chỉ technical requirement mà là business differentiation.

**Why it matters:**
- Conversion rate: Relevant campaigns convert 3-5x better
- Brand safety: No competitor campaigns
- UX: Không waste time với irrelevant campaigns
- Compliance: Regulated industries cần approval
- White-label: Tenant control

---

### Insight 7: Fraud Prevention PHẢI từ đầu
**Impact:** High | **Effort:** Medium | **Priority:** P1

**Description:**
Affiliate fraud (self-clicking, fake conversions) là existential threat. Pub2 có detection nhưng at-core cần thêm safeguards.

**Why it matters:**
- Financial loss từ fake commissions
- Merchant trust (high fraud → merchants leave)
- Platform reputation
- Legal risk
- Platform ban risk (Pub2 terminates high-fraud accounts)

**Defense layers:**
1. Rate limiting (100 clicks/day per link)
2. Pattern detection (high CTR, low IP diversity)
3. Manual review queue
4. Pub2's fraud detection (device fingerprints)

---

## Statistics

- **Total Ideas Generated:** 85+
- **Categories:** 10
- **Key Insights:** 7
- **Techniques Applied:** 3 (SWOT, Mind Mapping, Starbursting)
- **Recommended Model:** API Proxy Model
- **Estimated MVP Timeline:** 4-6 weeks
- **P0 Insights:** 4 (blocking cho MVP)
- **P1 Insights:** 3 (essential cho production)

---

## Recommended Next Steps

### Immediate (Next Workflow)

**Option 1: Technical Spec (RECOMMENDED)**
```bash
/bmad:tech-spec
```
**Rationale:** Architecture đã clear từ brainstorming. Tech spec sẽ detail DB schema, API contracts, implementation plan.

**Option 2: Product Requirements Document**
```bash
/bmad:prd
```
**Rationale:** Nếu cần alignment với stakeholders (AccessTrade, Techcombank) trước khi technical dive.

---

### Short-term (Phase 1: MVP - 4-6 weeks)

**Sprint 1: Foundation (Week 1-2)**
- Database schema (tenant_pub2_config, affiliate_links, etc.)
- Pub2ApiClient service
- Tenant config Admin UI
- Multi-tenant filtering logic

**Sprint 2: Core Features (Week 3-4)**
- Campaign browser UI
- Affiliate link generator
- Attribution logic (sub_id parameters)
- Webhook receiver + polling fallback

**Sprint 3: Analytics & Polish (Week 5-6)**
- Unified dashboard
- Fraud detection (basic patterns)
- Monitoring & alerting
- Testing & deployment

---

### Mid-term (Phase 2: Production Hardening - 2-3 months)

**Enhancements:**
- Advanced fraud detection
- Reconciliation jobs automation
- Influencer onboarding flow (link Pub2 account)
- Campaign recommendation AI
- A/B testing (campaign performance)
- Export/reporting tools

**Scale:**
- Redis caching layer
- Background job optimization (Bullmq)
- Database indexing & query optimization
- Load testing (1000+ concurrent influencers)

---

### Long-term (Phase 3: Deep Integration - 6+ months)

**Advanced Features:**
- Sync campaigns to at-core DB (offline capability)
- Real-time websocket updates
- Multi-touch attribution
- Split commission models
- White-label campaign management UI
- Integration với payment systems (combined payout)

**Platform Evolution:**
- Support multiple affiliate networks (beyond Pub2)
- Influencer marketplace (brands post campaigns)
- Automated campaign matching (AI)
- Predictive analytics (expected commission per video)

---

## Appendix: Pub2 API Reference (Assumed)

**Note:** Actual Pub2 API cần confirm với AccessTrade. Đây là assumptions based on standard affiliate APIs.

### Essential Endpoints

```typescript
// Get campaigns
GET /api/v1/campaigns
Headers: { Authorization: 'Bearer {api_key}' }
Query: {
  category?: string,
  status?: 'active' | 'paused',
  updated_since?: timestamp
}
Response: {
  campaigns: [
    {
      id: 'camp_123',
      title: 'TCB Platinum Card',
      category: 'banking',
      commission_rate: 8.5,
      commission_type: 'percentage' | 'fixed',
      start_date: '2026-01-01',
      end_date: '2026-12-31',
      status: 'active',
      merchant: { id: 'merch_456', name: 'Techcombank' }
    }
  ]
}

// Create affiliate link
POST /api/v1/affiliate-links
Headers: { Authorization: 'Bearer {api_key}' }
Body: {
  campaign_id: 'camp_123',
  publisher_id: 'pub_789',
  sub_id_1?: 'vid_abc123',  // Custom tracking param
  sub_id_2?: 'tcb',          // Custom tracking param
  sub_id_3?: 'banking'       // Custom tracking param
}
Response: {
  link_id: 'link_xyz',
  url: 'https://pub2.com/track/xyz?campaign=123&pub=789&sub1=vid_abc123',
  created_at: '2026-02-07T10:00:00Z'
}

// Get click stats
GET /api/v1/clicks
Headers: { Authorization: 'Bearer {api_key}' }
Query: {
  link_id?: 'link_xyz',
  date_from?: '2026-02-01',
  date_to?: '2026-02-07'
}
Response: {
  clicks: [
    {
      event_id: 'click_111',
      link_id: 'link_xyz',
      clicked_at: '2026-02-07T11:30:00Z',
      ip_address: '123.45.67.89',
      user_agent: 'Mozilla/5.0...'
    }
  ],
  total: 234
}

// Get conversions
GET /api/v1/conversions
Headers: { Authorization: 'Bearer {api_key}' }
Query: {
  link_id?: 'link_xyz',
  status?: 'pending' | 'confirmed' | 'paid',
  date_from?: '2026-02-01'
}
Response: {
  conversions: [
    {
      event_id: 'conv_222',
      link_id: 'link_xyz',
      order_id: 'order_333',
      order_value: 500.00,
      commission: 42.50,
      commission_status: 'pending',
      purchased_at: '2026-02-07T12:00:00Z',
      sub_id_1: 'vid_abc123',
      sub_id_2: 'tcb'
    }
  ],
  total_commission: 42.50
}
```

### Webhook Payloads

```typescript
// Click event webhook
POST {at-core}/webhooks/pub2/clicks
Headers: {
  'X-Pub2-Signature': 'sha256=...',
  'X-Pub2-Event': 'click'
}
Body: {
  event_id: 'click_111',
  event_type: 'click',
  link_id: 'link_xyz',
  campaign_id: 'camp_123',
  publisher_id: 'pub_789',
  sub_id_1: 'vid_abc123',
  sub_id_2: 'tcb',
  clicked_at: '2026-02-07T11:30:00Z',
  ip_address: '123.45.67.89',
  user_agent: 'Mozilla/5.0...'
}

// Conversion event webhook
POST {at-core}/webhooks/pub2/conversions
Headers: {
  'X-Pub2-Signature': 'sha256=...',
  'X-Pub2-Event': 'conversion'
}
Body: {
  event_id: 'conv_222',
  event_type: 'conversion',
  link_id: 'link_xyz',
  campaign_id: 'camp_123',
  publisher_id: 'pub_789',
  sub_id_1: 'vid_abc123',
  sub_id_2: 'tcb',
  order_id: 'order_333',
  order_value: 500.00,
  commission: 42.50,
  commission_status: 'pending',
  purchased_at: '2026-02-07T12:00:00Z'
}

// Commission update webhook
POST {at-core}/webhooks/pub2/commission-updates
Headers: {
  'X-Pub2-Signature': 'sha256=...',
  'X-Pub2-Event': 'commission_update'
}
Body: {
  event_id: 'conv_222',
  commission_status: 'confirmed',  // 'pending' → 'confirmed' → 'paid'
  updated_at: '2026-02-14T10:00:00Z'
}
```

---

**Generated by BMAD Method v6 - Creative Intelligence**
**Session Duration:** ~45 minutes
**Workflow:** Brainstorm
**Next Recommended:** Tech Spec (`/bmad:tech-spec`) or PRD (`/bmad:prd`)
