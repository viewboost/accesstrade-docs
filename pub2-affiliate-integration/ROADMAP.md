# 🚀 Pub2 Affiliate Integration - Lộ Trình Phát Triển

**Dự án:** Pub2 Affiliate Integration cho TCB/Ambassador/Vinfast
**Thời gian:** 6 tháng (Tháng 3 - Tháng 8, 2026)
**Cập nhật:** 2026-02-11

---

## 📊 Tổng Quan

- **Tổng số features:** 18 features chính
- **Timeline:** 6 tháng (3 tháng core + 3 tháng enhancements)
- **Partners:** TCB, Ambassador, Vinfast
- **Mục tiêu:** Tăng thu nhập influencer +40%, retention +15%

---

## CAMPAIGN ENHANCEMENTS

### 1. Social Media Schema Extension - Threads & Facebook Posts Support
**Timeline:** 1/3 → 15/3 | **Priority:** P1

**Lợi ích:**
- ✅ **Mở rộng nền tảng:** Influencer có thể chia sẻ affiliate links trên Threads và Facebook Posts (ngoài Instagram Stories/TikTok)
- ✅ **Tăng reach:** Threads đang viral tại VN (2M+ users), Facebook vẫn là platform #1
- ✅ **Linh hoạt content:** Mỗi platform có audience khác nhau → Maximize conversion
- ✅ **Tracking chính xác:** UTM parameters tự động cho từng platform → Biết platform nào convert tốt nhất

**Chi tiết kỹ thuật:**
- Extend database schema: `campaign_submissions` thêm fields `platform_type` (threads/facebook/instagram)
- API endpoints: `/api/campaigns/{id}/submit-threads-post`, `/api/campaigns/{id}/submit-facebook-post`
- Validation rules per platform (Threads: min 100 chars, Facebook: min 50 chars)

---

### 2. Pre-Submission Checklist System - Campaign Participation Requirements
**Timeline:** 15/3 → 31/3 | **Priority:** P0

**Lợi ích:**
- ✅ **Giảm rejection rate 40%:** Influencer tự check trước khi submit → Ít bị reject hơn
- ✅ **UX tốt hơn:** Biết rõ thiếu gì, cần làm gì (không bị "mù mờ")
- ✅ **Giảm support tickets 50%:** Không phải hỏi "Tại sao tôi bị reject?"
- ✅ **Admin workload giảm 30%:** Ít hồ sơ rác hơn → Focus vào review quality

**Hoạt động như thế nào:**
```
UI hiển thị checklist:
✅ Tài khoản ≥ 3 tháng tuổi
✅ Email đã xác thực
❌ Số follower: 800/1000 (thiếu 200)
❌ Chưa link Pub2 account

→ Button "Tham gia" bị disable
→ Hiển thị: "Hoàn thiện 2 yêu cầu còn lại để tham gia"
```

**Phân tích chi tiết:** Xem [Two-Tier Validation Brainstorming](/.bmad/brainstorming-participation-two-tier-validation-2026-02-07.md)

---

### 3. Bonus Reward System - Performance Incentives
**Timeline:** 15/3 → 31/3 | **Priority:** P1

**Lợi ích:**
- ✅ **Động lực cao hơn:** Top performers được thưởng thêm 10-30% → Push harder
- ✅ **Cạnh tranh lành mạnh:** Leaderboard public → Influencers cố gắng lên top
- ✅ **ROI cho brand:** Chỉ trả thưởng khi có kết quả thực tế (clicks, conversions)
- ✅ **Retention tăng:** Top performers gắn bó lâu dài với platform

**Cơ chế thưởng:**
```
🥇 Top 1-3: +30% base reward
🥈 Top 4-10: +20% base reward
🥉 Top 11-20: +10% base reward

Tiêu chí xếp hạng:
- 50%: Số conversions
- 30%: CTR (Click-through rate)
- 20%: Content quality score (admin rating)
```

**Example:**
- Base reward: 500k VND
- User đạt Top 5 → Bonus +20% = 100k
- Total: 600k VND

---

## PHÂN TÍCH PROFILE KOL/KOC

### 4. Influencer Library - Aggregated from 4 Data Sources
**Timeline:** 16/3 → 15/4 | **Priority:** P0

**4 nguồn dữ liệu:**
1. **Influencer onboarding:** Profile tự khai báo
2. **Data enrichment:** Crawl social media (followers, engagement)
3. **Campaign performance:** Lịch sử tham gia campaigns
4. **Brand feedback:** Rating từ brands (quality, attitude, delivery time)

**Lợi ích:**
- ✅ **360° view:** Brand thấy đầy đủ thông tin influencer (không chỉ followers)
- ✅ **Data-driven decisions:** Chọn influencer dựa trên data thực tế, không "đoán mò"
- ✅ **Trust & transparency:** Influencer có track record → Dễ được tin tưởng
- ✅ **Tiết kiệm thời gian:** Không phải research manual từng influencer

**Database schema:**
```sql
influencer_profiles (
  id, user_id, niche_categories, follower_count,
  engagement_rate, avg_views, campaigns_completed,
  quality_score, brand_rating_avg, last_enriched_at
)
```

---

### 5. Influencer Library - Discovery & Exploration
**Timeline:** 16/4 → 30/4 | **Priority:** P0

**Lợi ích:**
- ✅ **Tìm đúng người nhanh:** Brand search theo niche, location, follower range → Kết quả trong 3s
- ✅ **Advanced filters:** Lọc theo engagement rate, past performance, price range
- ✅ **Save time 80%:** Không phải scroll qua 1000 profiles, chỉ xem 10-20 matches
- ✅ **Smart suggestions:** AI suggest influencers tương tự với top performers

**UI Features:**
- Search bar với autocomplete (tìm theo name, niche, location)
- Filter sidebar: Niche, Followers (10k-50k, 50k-100k...), Engagement (>5%, >10%)
- Sort by: Relevance, Quality score, Price (low-high), Recent campaigns
- Save to "Favorites" list

---

### 6. Influencer Library - Scoring & Matching Engine
**Timeline:** 1/5 → 15/5 | **Priority:** P1

**Lợi ích:**
- ✅ **Chấm điểm tự động:** Mỗi influencer có score 0-100 → Dễ so sánh
- ✅ **Match tự động:** AI suggest top 10 influencers phù hợp nhất cho campaign
- ✅ **Giảm bias:** Quyết định dựa trên data, không "thiên vị cá nhân"
- ✅ **Predict success rate:** "85% khả năng campaign này sẽ thành công với influencer A"

**Scoring formula:**
```javascript
Quality Score (0-100) =
  Follower authenticity (30%) +
  Engagement rate (25%) +
  Campaign completion rate (25%) +
  Brand rating (20%)

Example:
- Follower authenticity: 90% real followers = 27/30
- Engagement rate: 8% = 20/25
- Completion rate: 95% = 24/25
- Brand rating: 4.5/5 = 18/20
→ Total: 89/100 (Excellent)
```

**Matching algorithm:**
- Campaign niche vs Influencer niche (exact match > partial match)
- Budget fit (influencer price ≤ campaign budget)
- Past performance in similar campaigns
- Availability (không overbooked)

---

### 7. Influencer Library - Booking & Reservation System
**Timeline:** 15/5 → 30/5 | **Priority:** P1

**Lợi ích:**
- ✅ **Tránh double booking:** Influencer không bị book 5 campaigns cùng lúc
- ✅ **Commitment rõ ràng:** Brand book → Influencer confirm → Deal chắc chắn
- ✅ **Calendar integration:** Influencer thấy schedule của mình (campaign A: 1-7/5, campaign B: 8-15/5)
- ✅ **Deposit system:** Brand trả deposit 30% → Influencer cam kết làm

**Workflow:**
```
1. Brand chọn influencer → Click "Book"
2. Chọn dates (start - end)
3. Gửi booking request + deposit 30%
4. Influencer nhận notification
5. Influencer: [Accept] / [Decline] / [Counter-offer dates]
6. Nếu Accept → Status = "Confirmed" → Block calendar
7. Campaign ends → Release remaining 70%
```

---

## AFFILIATE CENTER - UNIFIED CAMPAIGN & DUAL EARNING

### 8. Connect Affiliate Programs to Campaigns - Maximize Revenue per Content
**Timeline:** 1/4 → 30/4 | **Priority:** P0

**Lợi ích:**
- ✅ **Tăng thu nhập 2x:** 1 video vừa được trả view reward, vừa kiếm affiliate commission
- ✅ **Win-win:** Brand có thêm conversion, Influencer có thêm thu nhập → Đôi bên đều vui
- ✅ **Simplify workflow:** Không phải quản lý 2 platforms riêng (1 cho views, 1 cho affiliate)
- ✅ **Tracking thống nhất:** Dashboard duy nhất xem cả 2 loại thu nhập

**Example scenario:**
```
Campaign: Review Techcombank Credit Card
- View reward: 50k VND (guaranteed)
- Affiliate commission: 5% per approval (variable)

Influencer posts video:
- 100k views → Earn 50k (guaranteed)
- Video có 50 clicks → 5 conversions
- 5 conversions × 500k commission = 2,500k VND
→ Total: 2,550k VND (50x base reward!)
```

**UI/UX:**
- Dashboard hiển thị 2 columns: "View Rewards" | "Affiliate Commissions"
- Campaign card show: "Base: 50k + Up to 3,000k từ affiliate"
- Single "Generate Link" button → Tạo link tracking cả views + affiliate

---

## SYSTEM IMPROVE

### 9. Fraud Detection - Enhancement & Optimization
**Timeline:** 16/4 → 15/5 | **Priority:** P0

**Lợi ích:**
- ✅ **Bảo vệ ngân sách brand:** Phát hiện 80%+ fake clicks/conversions → Tiết kiệm hàng trăm triệu
- ✅ **Fair play:** Influencers trung thực không bị ảnh hưởng, chỉ catch cheaters
- ✅ **ML-powered:** Machine learning học patterns → Ngày càng thông minh hơn
- ✅ **Real-time blocking:** Phát hiện fraud trong vòng 5 phút → Block ngay

**Fraud detection methods:**

**Phase 1 (Basic - Already implemented):**
- Rate limiting: 100 clicks/day
- CTR threshold: >50% → Flag
- IP diversity: <30% unique IPs → Flag
- Self-clicking: >5 clicks from influencer → Flag

**Phase 4 (Enhanced - ML-powered):**
- **Click farm detection:** ML model nhận diện patterns của click farms (timing, devices, IPs)
- **Bot detection:** User-agent analysis, mouse movement patterns
- **Fake follower check:** Re-validate follower count tại reconciliation (xem feature #13)
- **Network analysis:** Phát hiện fraud rings (nhóm influencers collude)

**Success metrics:**
- Fraud detection rate: +30%
- False positive: <5%
- Cost savings: 200M+ VND/year

---

### 10. Setup Editor - AI Agent Assistant
**Timeline:** 1/4 → 15/4 | **Priority:** P1

**Lợi ích:**
- ✅ **Tạo campaign nhanh 5x:** AI suggest title, description, requirements dựa trên past campaigns
- ✅ **Consistency:** AI đảm bảo không miss required fields (budget, timeline, T&C)
- ✅ **Smart defaults:** AI fill sẵn common settings (followers ≥1000, engagement ≥3%)
- ✅ **Learning từ best practices:** AI học từ top-performing campaigns → Suggest winning formula

**AI features:**
```
Brand nhập: "Campaign review thẻ tín dụng Techcombank"

AI suggest:
✨ Title: "Trải nghiệm thẻ tín dụng Techcombank - Ưu đãi 2026"
✨ Description: [AI viết 200 words về benefits, target audience]
✨ Requirements:
   - Followers ≥ 1000
   - Niche: Finance, Lifestyle
   - Age: 22-35
   - Content: 1 video review 60s
✨ Budget suggestion: 50M VND (dựa trên 100 influencers × 500k)
✨ Timeline: 30 ngày (industry standard cho financial campaigns)

Brand review → Edit nếu cần → Approve → Publish
```

**Technical:**
- GPT-4 integration
- Train on 200+ past campaigns
- Template library (banking, lifestyle, tech, food...)

---

### 11. Operations Manager - Task Management & Performance Scoring
**Timeline:** 1/5 → 30/5 | **Priority:** P1

**Lợi ích:**
- ✅ **Quản lý task hiệu quả:** Admin assign tasks (review submissions, approve payouts) → Track progress real-time
- ✅ **SLA tracking:** Đảm bảo tasks được xử lý đúng hạn (review trong 24h, payout trong 3 ngày)
- ✅ **Performance scoring:** Admin có score → Reward top performers, coach underperformers
- ✅ **Workload balancing:** Hệ thống tự động distribute tasks đều cho team

**Features:**

**Task Dashboard:**
```
📋 My Tasks (12 pending)
┌─────────────────────────────────────────┐
│ ⚡ URGENT (SLA < 2h)                     │
│ • Review submission #1234 (1h left)     │
│ • Approve payout #5678 (30m left)       │
│                                         │
│ 📅 TODAY (SLA < 24h)                    │
│ • Review 8 campaign submissions         │
│ • Process 3 payout requests             │
│                                         │
│ 📆 THIS WEEK                            │
│ • Monthly report generation             │
└─────────────────────────────────────────┘
```

**Performance Scoring:**
```javascript
Admin Score (0-100) =
  SLA compliance (40%) +        // Xử lý đúng hạn
  Quality (30%) +                // Ít complaints từ users
  Volume (20%) +                 // Số tasks hoàn thành
  User satisfaction (10%)        // Rating từ users

Example:
Admin A: 95 points → Top performer → Bonus 20%
Admin B: 65 points → Average → Training needed
```

---

### 12. Brand Portal - Dashboard Modernization
**Timeline:** 15/3 → 31/3 | **Priority:** P1

**Lợi ích:**
- ✅ **Real-time insights:** Dashboard update real-time (không phải F5 liên tục)
- ✅ **Beautiful UI:** Modern design (shadcn/ui components) → Professional look
- ✅ **Mobile-friendly:** Brand managers xem dashboard trên điện thoại
- ✅ **Custom views:** Mỗi brand customize dashboard theo nhu cầu (TCB quan tâm ROI, Ambassador quan tâm reach)

**Dashboard widgets:**
- **Campaign Overview:** Active/Completed/Draft campaigns
- **Performance Charts:**
  - Views over time (line chart)
  - Conversion funnel (bar chart)
  - Top influencers (table)
- **Budget Tracking:** Spent/Remaining/Projected
- **Real-time Feed:** Recent submissions, approvals, payouts
- **Quick Actions:** Create campaign, Browse influencers, View reports

**Tech stack:**
- React + TypeScript
- shadcn/ui components
- Chart.js / Recharts
- Real-time: WebSocket connections

---

### 13. Re-validation at Reconciliation - Prevent Fake Follower Exploitation
**Timeline:** 16/4 → 30/4 | **Priority:** P0 🔴 CRITICAL

**Lợi ích:**
- ✅ **Chặn exploitation:** Users không thể mua fake followers → Submit → Xóa fake → Nhận tiền
- ✅ **Bảo vệ ngân sách:** Chỉ trả tiền cho influencers có real followers
- ✅ **Fair play:** Influencers trung thực không bị thiệt
- ✅ **10% grace period:** Cho phép natural fluctuation (unfollows tự nhiên)

**Vấn đề cần giải quyết:**
```
❌ Exploitation scenario:
T1: User có 1000 followers → Approved ✅
T2: Mua 500 fake → 1500 followers → Submit posts
T3: Xóa 500 fake → Về lại 1000
T4: Payment → User nhận tiền (system bị lừa)
```

**Giải pháp - Multi-checkpoint validation:**
```
✅ Checkpoint 1: Participation approval
   → Validate requirements
   → Save baseline follower count (1000)

✅ Checkpoint 2: Content submission
   → Spot check 20% random submissions
   → Flag nếu follower drop >10%

✅ Checkpoint 3: Payment reconciliation
   → Re-validate follower count
   → Compare with baseline
   → Grace period: -10% OK (900-1000 OK)
   → Reject nếu drop >30% (< 700 = REJECT)
```

**Implementation:**
```javascript
async function validateAtReconciliation(userEvent) {
  const original = 1000;  // Saved at approval
  const current = 700;    // Current count
  const drop = 30%;       // Dropped 30%

  if (drop <= 10%)  return 'PASS';     // Natural fluctuation
  if (drop <= 30%)  return 'WARNING';  // Manual review
  return 'REJECT';  // Likely fake follower removal
}
```

**Phân tích chi tiết:** [Two-Tier Validation - Insight 7](/.bmad/brainstorming-participation-two-tier-validation-2026-02-07.md#insight-7-re-validation-at-reconciliation-prevents-exploitation-)

---

### 14. Automated Campaign Lifecycle: Brief → Discovery → Budgeting → Approval → Execution
**Timeline:** 15/5 → 30/5 | **Priority:** P1

**Lợi ích:**
- ✅ **Tự động hóa 70% workflow:** Giảm manual work từ 10h → 3h per campaign
- ✅ **Không bỏ sót steps:** System enforce đúng trình tự (không thể skip budgeting)
- ✅ **Audit trail:** Track được ai làm gì, khi nào → Transparency
- ✅ **Notification tự động:** Stakeholders được notify đúng lúc (không phải remind manual)

**Lifecycle workflow:**

```
1️⃣ BRIEF (Brand)
   → Input: Campaign goals, target audience, budget range
   → Output: Campaign brief document
   → Auto-notification: Send to Marketing Manager

2️⃣ DISCOVERY (Marketing Manager)
   → Use AI Agent Assistant (feature #10)
   → Browse Influencer Library (feature #5)
   → Select 20-50 potential influencers
   → Output: Influencer shortlist

3️⃣ BUDGETING (Finance)
   → Review shortlist + estimated costs
   → Approve/Adjust budget
   → Output: Approved budget
   → Auto-notification: Send back to Marketing Manager

4️⃣ APPROVAL (Director/VP)
   → Review full campaign plan
   → Approve/Reject/Request changes
   → Output: Final approval
   → Auto-notification: Send to Operations team

5️⃣ EXECUTION (Operations)
   → Book influencers (feature #7)
   → Launch campaign
   → Monitor performance
   → Process payouts
   → Output: Campaign completion report
```

**Timeline tracking:**
- Each stage có SLA (Brief: 2 days, Discovery: 3 days, Budgeting: 1 day...)
- Dashboard hiển thị: "Campaign đang ở stage Discovery, còn 1 ngày trước deadline"

---

### 15. Influencer Portal - UX/UI Modernization
**Timeline:** 15/5 → 30/5 | **Priority:** P1

**Lợi ích:**
- ✅ **Trải nghiệm tốt hơn:** Modern UI → Influencers cảm thấy professional, muốn quay lại
- ✅ **Navigation dễ hơn:** Đi từ A → B chỉ cần 1-2 clicks (thay vì 5-6 clicks)
- ✅ **Mobile-first:** 80% influencers dùng điện thoại → Phải optimize cho mobile
- ✅ **Onboarding smooth:** New users hiểu cách dùng trong 2 phút (không cần training)

**UI Improvements:**

**Before (Old UI):**
- Desktop-only design
- Complex navigation (3-level menus)
- Slow loading (5-7s)
- Outdated design (2015 style)

**After (Modern UI):**
- **Mobile-first responsive:** Works perfect on iPhone/Android
- **Simple navigation:**
  - Bottom tab bar: Home | Campaigns | Links | Earnings | Profile
  - Max 2 clicks to any feature
- **Fast loading:** <1s page transitions (Next.js App Router)
- **Modern design:**
  - Tailwind CSS styling
  - shadcn/ui components
  - Dark mode support
  - Smooth animations

**Onboarding flow:**
```
Welcome Screen → Link Pub2 Account (1-click OAuth)
→ Complete Profile (2 mins)
→ Browse First Campaign
→ Generate First Link
→ Done! 🎉

Total time: 5 minutes
```

**Tech stack:**
- Next.js 15 (App Router + Server Components)
- React 19 + TypeScript
- Tailwind CSS + shadcn/ui
- Framer Motion (animations)

---

## VERIFIED CREATOR SYSTEM

### 16. Verified Creator Badge - Fast-track Approval for Trusted Creators
**Timeline:** 1/5 → 15/5 | **Priority:** P1

**Lợi ích:**
- ✅ **Reward loyalty:** Influencers trung thực được thưởng bằng instant approval
- ✅ **Admin focus đúng chỗ:** Focus 80% effort vào new/risky creators, chỉ 20% cho verified
- ✅ **Scalability:** Khi platform lớn (10k influencers), không cần hire thêm 50 admins
- ✅ **Retention +15-20%:** Top creators gắn bó lâu dài vì được đối xử VIP

**Badge tiers:**

```
🥉 BRONZE (1-2 campaigns completed)
   → Standard review: 1-2 days
   → No benefits yet

🥈 SILVER (3-5 campaigns completed, 70%+ quality score)
   → Fast-track review: 4-8 hours
   → Priority support

🥇 GOLD (6+ campaigns, 90%+ quality score)
   → Instant approval (auto-approve)
   → Dedicated account manager
   → Higher commission rates

💎 DIAMOND (Partner-nominated VIPs)
   → Whitelist (always auto-approve)
   → Exclusive campaigns
   → Premium payouts
```

**Quality Score formula:**
```javascript
Quality Score (0-100) =
  Approval rate (30%) +           // Được approve bao nhiêu %
  Completion rate (25%) +         // Hoàn thành campaign bao nhiêu %
  Avg engagement (25%) +          // Engagement trung bình
  Partner ratings (20%)           // Rating từ brands

Example - Gold Creator:
- Approval rate: 95% (28.5/30)
- Completion rate: 100% (25/25)
- Avg engagement: 8.5% (21.25/25)
- Partner rating: 4.7/5 (18.8/20)
→ Total: 93.55/100 → GOLD ✅
```

**Automation logic:**
```javascript
function determineReviewPath(user, campaign) {
  if (user.badge === 'diamond')
    return 'instant_approve';

  if (user.badge === 'gold' && user.qualityScore >= 90)
    return 'instant_approve';

  if (user.badge === 'silver')
    return 'fast_track_4_8h';

  return 'standard_review_1_2days';
}
```

**Risk mitigation:**
- Spot check random 10% gold submissions
- Auto-downgrade nếu quality score < 70%
- Manual review nếu fraud detection flag

**Phân tích chi tiết:** [Two-Tier Validation - Insight 5](/.bmad/brainstorming-participation-two-tier-validation-2026-02-07.md#insight-5-verified-creator-badge-enables-fast-pass-)

---

### 17. Partial Approval System - Tiered Approvals (Optional)
**Timeline:** 15/5 → 30/5 | **Priority:** P2 (Nice to have)

**Lợi ích:**
- ✅ **Giảm rejection rate 40%:** Thay vì reject hoàn toàn, cho phép tham gia giới hạn
- ✅ **Tăng participation:** Users "gần đủ điều kiện" vẫn được tham gia → Motivation
- ✅ **Progressive unlocking:** Bronze → Silver → Gold (giống game progression)
- ✅ **Risk control:** Brand vẫn có quality control (Bronze = max 1 post, 70% reward)

**Tiered approval:**

```
🥉 BRONZE (60-79% requirements met)
   → Max 1 post
   → 70% reward
   Example: 800 followers (yêu cầu 1000) → Still OK

🥈 SILVER (80-99% requirements met)
   → Max 2 posts
   → 85% reward
   Example: 950 followers, email verified

🥇 GOLD (100% requirements met)
   → Max 3 posts
   → 100% reward
   Full benefits
```

**Example scenario:**
```
Campaign requirement: 1000 followers, email verified, phone verified

User A: 800 followers, email ✅, phone ✅
→ Current system: REJECT ❌
→ Proposed: Bronze approval (1 post, 70% reward) ✅

User B: 950 followers, email ✅, phone ✅
→ Current: REJECT ❌
→ Proposed: Silver approval (2 posts, 85% reward) ✅
```

**Implementation:**
```javascript
function calculateApprovalTier(requirements, userStatus) {
  const score = requirements.filter(r =>
    userStatus[r.type].passed
  ).length / requirements.length;

  if (score >= 1.0)  return { tier: 'gold', maxPosts: 3, reward: 1.0 };
  if (score >= 0.8)  return { tier: 'silver', maxPosts: 2, reward: 0.85 };
  if (score >= 0.6)  return { tier: 'bronze', maxPosts: 1, reward: 0.7 };

  return { tier: 'rejected', maxPosts: 0 };
}
```

**Trade-offs:**
- ⚠️ Complexity tăng (UI/logic phức tạp hơn)
- ⚠️ Brand có thể lo về bronze quality
- ⚠️ Cần pilot test với 1 campaign trước

**Recommendation:** Pilot test với TCB trong 1 tháng → Measure rejection rate, quality, satisfaction → Decide scale or not

**Phân tích chi tiết:** [Two-Tier Validation - Insight 6](/.bmad/brainstorming-participation-two-tier-validation-2026-02-07.md#insight-6-partial-approval-gi%E1%BA%A3m-rejection-rate-40-)

---

### 18. AI Campaign Recommendations - Auto-suggest Relevant Campaigns
**Timeline:** 1/5 → 15/5 | **Priority:** P1

**Lợi ích:**
- ✅ **Tăng participation +25%:** Influencers thấy campaigns phù hợp → Tham gia nhiều hơn
- ✅ **Tăng conversion +20%:** Match đúng niche → Performance tốt hơn
- ✅ **Save time:** Không phải scroll 100 campaigns, AI suggest top 5 best matches
- ✅ **Learn from data:** AI càng dùng càng thông minh (học từ past performance)

**Recommendation engine:**

**Input factors:**
1. **Influencer niche:** Beauty, Tech, Food, Finance...
2. **Past performance:** Campaigns nào user đã tham gia, convert tốt
3. **Follower demographics:** Age, gender, location of followers
4. **Engagement patterns:** User tương tác nhiều với content type nào
5. **Availability:** User có busy không (đang làm 5 campaigns → Đừng suggest thêm)

**ML Model:**
```javascript
function recommendCampaigns(influencer, allCampaigns) {
  // Score mỗi campaign (0-100)
  const scored = allCampaigns.map(campaign => ({
    campaign,
    score: calculateMatchScore(influencer, campaign)
  }));

  // Sort by score
  scored.sort((a, b) => b.score - a.score);

  // Return top 10
  return scored.slice(0, 10);
}

function calculateMatchScore(influencer, campaign) {
  return (
    nicheMatch(influencer.niche, campaign.niche) * 0.4 +
    pastPerformance(influencer, campaign.category) * 0.3 +
    demographicsMatch(influencer.followers, campaign.targetAudience) * 0.2 +
    availabilityScore(influencer.schedule) * 0.1
  ) * 100;
}
```

**UI Display:**
```
🎯 Được đề xuất cho bạn

┌────────────────────────────────────┐
│ ⭐ 95% match                        │
│ Review thẻ tín dụng Techcombank    │
│ 500k VND + Up to 5M từ affiliate   │
│                                    │
│ Lý do đề xuất:                     │
│ ✓ Bạn đã làm 3 campaigns Finance   │
│ ✓ Followers của bạn: 25-35 tuổi   │
│ ✓ Past CTR: 8.5% (cao hơn avg)    │
└────────────────────────────────────┘
```

**A/B Testing:**
- Group A: Random campaigns
- Group B: AI recommendations
- Measure: Click rate, participation rate, conversion rate

**Target metrics:**
- Recommendation accuracy: ≥70%
- CTR on recommended campaigns: +20% vs non-recommended
- User satisfaction: ≥4.5/5

---

## 📊 Timeline Overview

```
THÁNG 3 (March)
├─ Week 1-2: Social Media Schema Extension
├─ Week 3-4: Pre-Submission Checklist + Bonus Reward
└─ Week 3-4: Brand Portal Modernization

THÁNG 4 (April)
├─ Week 1-2: Influencer Library - Data Aggregation
├─ Week 2-4: Setup Editor AI Assistant
├─ Week 3-4: Discovery & Exploration
├─ Week 3-4: Re-validation at Reconciliation
└─ Week 1-4: Connect Affiliate Programs

THÁNG 5 (May)
├─ Week 1-2: Scoring & Matching Engine
├─ Week 1-2: Fraud Detection Enhancement
├─ Week 1-2: AI Campaign Recommendations
├─ Week 1-2: Verified Creator Badge
├─ Week 1-4: Operations Manager
├─ Week 3-4: Booking & Reservation
├─ Week 3-4: Automated Campaign Lifecycle
├─ Week 3-4: Influencer Portal Modernization
└─ Week 3-4: Partial Approval (Optional)
```

---

## 🎯 Success Metrics

### Business Impact
| Metric | Baseline | Target (6 months) |
|--------|----------|-------------------|
| Influencer retention | 70% | 85% (+15%) |
| Avg revenue per influencer | View rewards only | +40% (dual earning) |
| Campaign participation rate | 30% | 45% (+15%) |
| Monthly payout requests | 100 | 300+ |

### Operational Efficiency
| Metric | Baseline | Target |
|--------|----------|--------|
| Admin workload per campaign | 10h | 3h (-70%) |
| Campaign setup time | 2 days | 4h (-75%) |
| Support tickets | 200/month | 100/month (-50%) |
| Fraud detection rate | 50% | 80%+ (+30%) |

### User Experience
| Metric | Baseline | Target |
|--------|----------|--------|
| Rejection rate | 30% | 18% (-40%) |
| Time to first payment | 15 days | 7 days |
| Influencer satisfaction | 3.5/5 | 4.5/5 |
| Brand satisfaction | 3.8/5 | 4.7/5 |

---

## 📚 Phụ Lục - Giải Thích Thuật Ngữ

### A
- **Affiliate Commission:** Hoa hồng bán hàng. VD: Bán 1 thẻ tín dụng được 500k
- **Affiliate Link:** Link tracking để biết ai bán được hàng
- **AI Agent Assistant:** Trợ lý AI giúp setup campaign tự động
- **Auto-approve:** Duyệt tự động không cần admin review

### B
- **Badge System:** Hệ thống huy hiệu (Bronze, Silver, Gold, Diamond)
- **Baseline:** Giá trị ban đầu để so sánh
- **Booking System:** Hệ thống đặt lịch influencer
- **Bonus Reward:** Tiền thưởng thêm cho top performers

### C
- **CTR (Click-Through Rate):** Tỷ lệ click. VD: 100 người xem, 5 click = 5% CTR
- **CVR (Conversion Rate):** Tỷ lệ chuyển đổi. VD: 100 clicks, 2 mua = 2% CVR
- **Campaign Lifecycle:** Vòng đời campaign từ lúc tạo đến kết thúc
- **Checkpoint Validation:** Kiểm tra tại nhiều điểm khác nhau

### D
- **Dashboard:** Trang tổng quan hiển thị metrics
- **Data Enrichment:** Bổ sung dữ liệu từ nguồn external (crawl social media)
- **Dual Earning:** Thu nhập kép (views + affiliate)
- **Discovery:** Tìm kiếm, khám phá

### E
- **Engagement Rate:** Tỷ lệ tương tác (likes + comments) / followers
- **Exploitation:** Lợi dụng lỗ hổng hệ thống

### F
- **Fake Followers:** Followers giả (mua về)
- **Fast-track:** Ưu tiên xử lý nhanh
- **Fraud Detection:** Phát hiện gian lận

### G
- **Grace Period:** Khoảng thời gian cho phép sai số. VD: -10% followers là OK
- **Gold Creator:** Influencer hạng vàng (chất lượng cao)

### L
- **Leaderboard:** Bảng xếp hạng

### M
- **ML (Machine Learning):** Học máy, AI tự học từ data
- **Matching Engine:** Công cụ ghép đôi (campaign - influencer)

### O
- **OAuth:** Phương thức đăng nhập an toàn (đăng nhập bằng Google/Facebook)
- **Onboarding:** Quy trình đưa user mới vào hệ thống

### P
- **Partial Approval:** Duyệt một phần (thay vì reject hoàn toàn)
- **Pub2:** Affiliate network partner của AccessTrade
- **Progressive Unlocking:** Mở khóa dần (Bronze → Silver → Gold)

### Q
- **Quality Score:** Điểm chất lượng (0-100)

### R
- **Re-validation:** Kiểm tra lại (ở thời điểm sau)
- **Reconciliation:** Đối soát thanh toán
- **Retention:** Giữ chân users (% users quay lại)
- **ROI (Return on Investment):** Lợi nhuận trên đầu tư

### S
- **SLA (Service Level Agreement):** Cam kết mức độ dịch vụ. VD: Xử lý trong 24h
- **Scoring Engine:** Công cụ chấm điểm
- **Spot Check:** Kiểm tra ngẫu nhiên (sample)

### T
- **Tier:** Cấp độ (Bronze, Silver, Gold)
- **Two-Tier Validation:** Kiểm tra 2 lớp (auto + manual)
- **Tracking:** Theo dõi, đo lường

### U
- **UAT (User Acceptance Testing):** Test chấp nhận từ users
- **UX/UI:** Trải nghiệm người dùng / Giao diện

### V
- **Verified Creator:** Influencer đã được xác minh
- **View Reward:** Tiền thưởng dựa trên lượt xem

### W
- **Webhook:** Hệ thống thông báo tự động (từ Pub2 → Platform)
- **White-label:** Tùy biến thương hiệu (mỗi brand có màu sắc riêng)
- **Workflow:** Quy trình làm việc

---

## 🔗 Tài Liệu Liên Quan

1. [Executive Summary](./00-executive-summary.md) - Tổng quan dự án
2. [Brainstorming Session](./01-brainstorming-session.md) - Phiên brainstorming ban đầu
3. [Architecture Decisions](./02-architecture-decisions.md) - Quyết định kiến trúc
4. [Two-Tier Validation Brainstorming](/.bmad/brainstorming-participation-two-tier-validation-2026-02-07.md) - Phân tích chi tiết hệ thống validation
5. [Design Mockups](./DESIGN-MOCKUPS-SUMMARY.md) - Thiết kế UI/UX

---

**Cập nhật:** 2026-02-11
**Version:** 2.0
**Người tạo:** ViewBoost Team + Claude (BMAD Method)
