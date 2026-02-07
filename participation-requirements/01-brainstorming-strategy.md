# Brainstorming Session: Đánh giá Phương án Event Registration Strategy

**Date:** 2026-02-07
**Objective:** Đánh giá phương án gộp "điều kiện tham gia" và "nhập mã yêu cầu" trong hệ thống event thưởng bài post Facebook
**Context:**
- Event schema: Thưởng theo số bài (1-3 bài x 150,000đ/bài)
- Điều kiện Facebook: Tài khoản cá nhân, fanpage >1,000, có bài đăng thật, tham gia ≥3 tháng
- Điều kiện mã mời: Tracking referral + whitelist/blacklist
- Hiện tại: Nhập mã ở bước "trước submit bài post"
- Dự định: Gộp vào bước "đăng ký tham gia event"

---

## Techniques Used

1. **SWOT Analysis** - Đánh giá toàn diện điểm mạnh/yếu của phương án
2. **Reverse Brainstorming** - Tìm các kịch bản thất bại để phòng tránh
3. **Starbursting** - Đặt câu hỏi sâu về Who/What/Where/When/Why/How

---

## Ideas Generated

### Category 1: Strengths (Điểm mạnh)

**1. Trải nghiệm người dùng tốt hơn**
- Rà soát tất cả điều kiện 1 lần duy nhất ở đầu
- Giảm friction trong luồng submit bài post
- User biết ngay từ đầu có đủ điều kiện hay không

**2. Kiểm soát chất lượng sớm**
- Lọc user không đủ điều kiện ngay từ bước đăng ký
- Tránh waste effort cho cả user và hệ thống
- Chỉ có qualified users mới được vào event

**3. Data tracking rõ ràng hơn**
- Tracking referral source ngay từ đầu
- Dễ phân tích conversion funnel (đăng ký → submit post → nhận thưởng)
- Attribution dễ dàng hơn

**4. Giảm complexity trong luồng submit**
- Submit bài post chỉ cần validate link Facebook
- Không cần check điều kiện lại ở nhiều điểm
- Code đơn giản hơn, ít bug hơn

### Category 2: Weaknesses (Điểm yếu)

**1. Barrier to entry cao hơn**
- User phải làm nhiều bước mới được bắt đầu
- Có thể mất user do onboarding phức tạp
- First-time user experience kém hơn

**2. Mất tính linh hoạt**
- Không cho phép "try before commit"
- User không thể xem event trước khi đăng ký
- Khó adjust điều kiện mid-campaign

**3. Risk của validation timing**
- Facebook data có thể thay đổi sau khi đăng ký (follower giảm, bài đăng bị xóa)
- Cần re-validate lúc submit post?
- Xử lý edge case phức tạp hơn

**4. Phụ thuộc vào Facebook OAuth sớm**
- Phải connect Facebook ngay từ đầu
- Nếu OAuth fail → lost user
- Privacy concern cao hơn ở bước đầu

### Category 3: Opportunities (Cơ hội)

**1. Gamification onboarding**
- Có thể tạo progress bar: Nhập mã → Connect FB → Validate → Approved
- Thêm email confirmation, welcome message
- Build expectation và commitment

**2. Whitelist management hiệu quả**
- Admin có thể pre-approve VIP users
- Partner có thể quản lý quota mã mời của họ
- A/B test với different referral sources

**3. Pre-campaign education**
- Onboarding screen có thể giáo dục về quy định
- Giảm spam/violation sau này
- Set expectations rõ ràng về payment timeline

**4. Multi-event management**
- User đăng ký 1 lần, tham gia nhiều campaign
- Profile reuse cho events khác
- Build long-term relationship

### Category 4: Threats (Rủi ro)

**1. Conversion funnel drop-off**
- Drop rate cao ở bước đăng ký phức tạp
- Competitor có onboarding đơn giản hơn → mất market share
- Mất organic growth do viral khó xảy ra

**2. User confusion**
- "Tại sao phải đăng ký mới xem được event?"
- "Mã mời ở đâu?" → support overhead
- Bad reviews nếu không communicate rõ

**3. Technical complexity**
- State management phức tạp hơn (pending approval, expired validation, etc.)
- Edge cases: User approved nhưng FB data changed
- Rollback khó nếu có bug ở onboarding

**4. Abuse vectors mới**
- Fake registration để "squat" slots
- Mã mời bị share public, mất kiểm soát
- Bot registration nếu không có CAPTCHA

### Category 5: Failure Scenarios (Kịch bản thất bại)

**1. Registration Hell**
- Onboarding có 10+ steps
- Mỗi step có thể fail (OAuth, validation, mã mời sai)
- Không có save progress → user phải làm lại từ đầu
- **→ Solution:** Progressive saving, maximum 3-4 steps, clear error messaging

**2. Validation Mismatch**
- User đăng ký lúc có 2,000 followers → Approved
- Submit bài post lúc còn 900 followers → Rejected
- **→ Solution:** Re-validation with grace period, communicate clearly, snapshot locking

**3. Invitation Code Chaos**
- Mã mời bị leak trên group Facebook/Telegram
- 10,000 người register với 1 mã
- **→ Solution:** Quota limits per code, rate limiting, admin dashboard monitoring

**4. Poor Communication**
- User không biết event có những campaign nào
- Đăng ký xong không biết làm gì tiếp
- **→ Solution:** Email/notification flow, clear dashboard showing status

**5. Technical Debt**
- State machine phức tạp với nhiều edge cases
- Bug fix ở 1 chỗ break 3 chỗ khác
- **→ Solution:** Simple state design, separate concerns, comprehensive tests

### Category 6: Critical Questions (Starbursting)

**WHO Questions:**
- Who validates điều kiện Facebook? → Backend via Graph API
- Who manages mã mời? → Admin + Partner self-service
- Who handles edge cases? → CS team + automated retry
- Who decides approval/rejection? → Automated with human escalation

**WHAT Questions:**
- What happens khi user fail validation? → Clear error + appeal process
- What data lưu ở registration? → FB snapshot + invite details + validation results
- What là success criteria? → Completion rate >60%, Time <5min, Support <5%
- What về privacy compliance? → GDPR-compliant retention, user deletion rights

**WHERE Questions:**
- Where trong user journey? → Dedicated onboarding flow
- Where lưu validation state? → Database + Redis cache
- Where validate lại? → Backend API at submit time
- Where user xem status? → Dedicated dashboard

**WHEN Questions:**
- When re-validate FB conditions? → Tiered approach (snapshot/periodic/per-submit)
- When expire invitation code? → Time + usage + event-based
- When notify approval status? → Real-time for critical events
- When allow update FB account? → Before first post only

**WHY Questions:**
- Why gộp validation vào registration? → Better UX, cleaner architecture, easier tracking
- Why cần mã mời? → Tracking, control, partnership enablement
- Why không free registration? → Quality, budget control, targeted growth
- Why validate FB conditions? → Fraud prevention, brand safety, ROI

**HOW Questions:**
- How implement registration? → Multi-step wizard with progressive disclosure
- How handle validation failures? → Soft rejection with waitlist option
- How manage invitation codes? → Branded codes with hierarchical tracking
- How prevent abuse? → Rate limiting, CAPTCHA, device fingerprinting, verification
- How optimize conversion? → Social proof, progress indicator, auto-save, reminder emails

### Category 7: Solution Approaches

**1. Hybrid 2-Tier Registration Model**
- **Tier 1: Quick Registration** (1 minute)
  - Nhập mã mời + email
  - Connect Facebook (OAuth only, no validation)
  - Status: "Registered, pending verification"
  - Can browse events and view rules

- **Tier 2: Full Verification** (before first submit)
  - Triggered when user wants to submit first post
  - Validate all FB conditions
  - Snapshot data at this point
  - Status: "Verified, can submit posts"

**Benefits:**
- ✅ Low barrier to entry (Tier 1)
- ✅ Quality control maintained (Tier 2)
- ✅ Flexibility for users to "try before buy"
- ✅ Reduced drop-off rate

**2. Invitation Code Management System**
```
Structure: {PARTNER_ID}-{CAMPAIGN_ID}-{RANDOM}
Example: TCB-EVENT01-A3X9K

Features:
- Quota per code: Max 100 registrations
- Quota per partner: Max 1,000 total
- Quota per campaign: Max 10,000 total
- Auto-disable when limit reached
- Real-time monitoring dashboard
- Fraud detection alerts
- Manual kill switch
- Expiration: 30 days or campaign end
```

**3. Re-Validation Strategy (Tiered)**
- **Tier 1: Snapshot Trust** (Default)
  - Save FB data at registration
  - Trust for entire campaign
  - Simple, low friction

- **Tier 2: Periodic Refresh** (High-value events)
  - Re-check every 7 days
  - 3-day grace period if fail
  - Proactive notifications

- **Tier 3: Per-Submission** (Maximum security)
  - Validate each post submission
  - Immediate rejection if fail
  - Only for very high-value campaigns

**4. UX Flow Design**
```
Registration Flow (< 2 minutes):
Step 1: Nhập mã mời → Validate code → Show event details
Step 2: Connect Facebook → OAuth → Preview profile data
Step 3: Confirm & Submit → Show validation results

Status Dashboard shows:
- Registration status: ✅ Verified / ⏳ Pending / ❌ Rejected
- Available events: [List]
- Posts submitted: 2/3 (next post: +150k VND)
- Total earnings: 300,000 VND
- Payment status: Pending

Notification Flow:
- Email: Registration confirmed
- Email: Verification complete (approved/rejected)
- Email: New campaign available
- Push: Post approved
- Push: Payment processed

Error Handling Example:
❌ Bad: "Validation failed"
✅ Good: "Your Facebook account doesn't meet requirements:
         ❌ Followers: 850 (need 1,000)
         ✅ Account age: 2 years
         ✅ Has posts: Yes

         [Appeal] [Try Different Account]"
```

**5. Implementation Phasing**

**Phase 1: MVP (2 weeks)**
- Basic registration flow (Tier 1 Quick Reg)
- Invitation code with quota
- Manual FB validation (admin review)
- Goal: Test with 100 users

**Phase 2: Automation (3 weeks)**
- Automated FB validation via Graph API
- Full verification flow (Tier 2)
- Email notifications
- Status dashboard
- Goal: Scale to 1,000 users, measure conversion

**Phase 3: Optimization (4 weeks)**
- A/B test different flows
- Advanced fraud detection
- Re-validation strategy
- Partner management dashboard
- Goal: Production-ready, 10k+ users

---

## Key Insights

### Insight 1: ✅ Phương án hợp lý - nhưng cần cải tiến

**Description:** Gộp validation vào registration là quyết định đúng về mặt kiến trúc và UX, nhưng cần implement theo mô hình Hybrid để tránh drop-off rate cao.

**Source:** SWOT Analysis + Reverse Brainstorming + Starbursting

**Impact:** High | **Effort:** Medium

**Why it matters:**
- Tách biệt rõ ràng giữa "đủ điều kiện tham gia" vs "submit bài post"
- Giảm complexity trong submit flow
- Better data tracking và attribution
- Cleaner architecture

**Cải tiến cần thiết:**
1. Progressive validation thay vì "all-or-nothing"
2. Re-validation strategy cho FB conditions
3. Grace period cho edge cases

---

### Insight 2: ⚠️ Rủi ro lớn nhất - Conversion Funnel Drop-off

**Description:** Onboarding phức tạp có thể mất 60-80% users. Cần A/B test và optimize aggressively.

**Source:** SWOT (Threats) + Reverse Brainstorming

**Impact:** High | **Effort:** High to mitigate

**Why it matters:**
- Competitor có thể có "free registration → submit → validate" đơn giản hơn
- Drop-off trực tiếp impact revenue và growth
- First impression rất quan trọng cho retention

**Giải pháp:**
1. A/B test phương án hiện tại vs phương án mới
2. Optimize onboarding: Maximum 3 steps, save progress, clear indicators
3. Lazy validation option: Quick reg → hard check khi submit

---

### Insight 3: 🎯 Chiến lược Hybrid - Best of Both Worlds

**Description:** Mô hình 2-tier registration cân bằng giữa low barrier entry và quality control.

**Source:** Starbursting (How questions) + SWOT Analysis

**Impact:** High | **Effort:** Medium

**Why it matters:**
- Tier 1 (Quick Reg) giảm friction, cho phép users explore
- Tier 2 (Full Verify) đảm bảo quality khi users commit
- Balance giữa conversion rate và fraud prevention

**Implementation:**
- Tier 1: Mã mời + OAuth only (1 minute)
- Tier 2: Full validation before first submit
- Clear communication về 2 tiers

---

### Insight 4: 🔐 Invitation Code Management - Critical Success Factor

**Description:** Hệ thống quản lý mã mời phải robust với quota limits, monitoring, và fraud detection.

**Source:** Starbursting (Who/What/When/How) + SWOT (Threats)

**Impact:** High | **Effort:** Medium

**Why it matters:**
- Mã mời là defensive line đầu tiên chống abuse
- Enable partnership tracking và attribution
- Budget control phụ thuộc vào quota management

**Must-have features:**
- Structured format: {PARTNER}-{CAMPAIGN}-{RANDOM}
- Quota limits: Per code, per partner, per campaign
- Real-time monitoring dashboard
- Auto-disable + manual kill switch
- Expiration policies

---

### Insight 5: 📊 Re-Validation Strategy - Balance Trust & Accuracy

**Description:** Cần tiered approach cho re-validation: Snapshot trust (default), Periodic refresh (high-value), Per-submission (maximum security).

**Source:** Reverse Brainstorming (Validation Mismatch) + Starbursting (When)

**Impact:** Medium | **Effort:** Low

**Why it matters:**
- Facebook data có thể thay đổi sau registration
- Balance giữa UX friction và data accuracy
- Edge case handling phải được plan trước

**Recommendation:**
- Bắt đầu với Tier 1 (Snapshot Trust)
- Upgrade based on fraud rate metrics
- Clear communication về expectations

---

### Insight 6: 🎨 UX Critical Points - Make or Break

**Description:** UX của registration flow và status dashboard trực tiếp quyết định success hay failure của phương án.

**Source:** Reverse Brainstorming (Poor Communication) + Starbursting (Where)

**Impact:** High | **Effort:** Medium

**Why it matters:**
- User confusion → support tickets → cost tăng
- Poor onboarding → drop-off → revenue loss
- Good UX → word of mouth → organic growth

**Must-have elements:**
- Registration flow <2 minutes với clear progress
- Status dashboard với real-time updates
- Proactive notifications (email + push)
- Helpful error messages với action items

---

### Insight 7: 🏗️ Implementation Phasing - Minimize Risk

**Description:** Rollout theo 3 phases (MVP → Automation → Optimization) để minimize risk và maximize learning.

**Source:** All techniques synthesis

**Impact:** High | **Effort:** Proper planning

**Why it matters:**
- Big bang rollout rủi ro cao
- Phased approach cho phép learn và adjust
- Early user feedback invaluable cho optimization

**Roadmap:**
- Phase 1 (2 weeks): MVP với 100 users, manual validation
- Phase 2 (3 weeks): Automation với 1,000 users, measure conversion
- Phase 3 (4 weeks): Production-ready với 10k+ users

---

## Tổng hợp & Khuyến nghị

### ✅ ĐỒNG Ý với phương án - với 3 điều kiện:

**1. Áp dụng mô hình HYBRID 2-tier registration**
- Tier 1: Quick reg (mã mời + OAuth) → Low friction
- Tier 2: Full verify (khi submit post đầu) → Quality control
- → Best of both worlds

**2. Implement PROGRESSIVE từng phase**
- Phase 1: MVP với manual validation
- Phase 2: Automation
- Phase 3: Optimization based on data
- → Minimize risk, maximize learning

**3. Đầu tư vào UX & COMMUNICATION**
- Clear onboarding flow (<2 minutes)
- Transparent status dashboard
- Proactive notifications
- Helpful error messages
- → Retain users, reduce support cost

---

### ⚠️ KHÔNG ĐỒNG Ý nếu:

**1. All-or-nothing validation ở đầu**
- → Drop-off rate sẽ quá cao
- → Mất competitive advantage

**2. Không có A/B testing**
- → Flying blind, không biết impact thật
- → Có thể làm hỏng toàn bộ funnel

**3. Bỏ qua re-validation strategy**
- → Edge cases sẽ explode
- → Support ticket tăng vọt
- → User frustration cao

---

### 📈 Success Metrics

**Registration Funnel:**
- Landing → Start Reg: >70%
- Start Reg → Complete Reg: >60%
- Complete Reg → First Submit: >40%

**Quality Metrics:**
- Fraud rate: <5%
- Support tickets: <10% of users
- Payment success rate: >95%

**Business Metrics:**
- Cost per qualified user: <50k VND
- ROI per campaign: >200%
- User retention (2nd campaign): >30%

---

## Statistics

- **Total ideas:** 45+
- **Categories:** 7
- **Key insights:** 7
- **Techniques applied:** 3

---

## Recommended Next Steps

### Immediate (This week):
1. **Validate phương án với stakeholders** - Present brainstorming findings
2. **Create detailed tech spec** cho Hybrid 2-tier model
3. **Design UX wireframes** cho registration flow và dashboard

### Short-term (Next 2 weeks):
1. **Build Phase 1 MVP:**
   - Basic registration form
   - Invitation code system với quota
   - Manual admin review process
2. **Setup monitoring:**
   - Conversion funnel tracking
   - Drop-off rate analysis
   - User feedback collection

### Medium-term (Next 1-2 months):
1. **Implement Phase 2 Automation:**
   - Facebook Graph API integration
   - Automated validation logic
   - Email notification system
2. **A/B testing framework:**
   - Test different onboarding flows
   - Measure impact on conversion
   - Iterate based on data

### Long-term (Next 3 months):
1. **Scale to Phase 3:**
   - Advanced fraud detection
   - Partner management dashboard
   - Re-validation strategies
2. **Continuous optimization:**
   - User research & testing
   - Performance monitoring
   - Feature enhancements

---

### Suggested Next BMAD Workflow:

**Option 1: Technical Specification** `/bmad:tech-spec`
- Detail out the Hybrid 2-tier registration model
- Database schema for user states, invitation codes
- API specifications for validation endpoints
- Integration points với Facebook Graph API

**Option 2: Create UX Design** `/bmad:create-ux-design`
- Registration flow wireframes
- Status dashboard mockups
- Email notification templates
- Error message copy

**Option 3: Sprint Planning** `/bmad:sprint-planning`
- Break down Phase 1 MVP into stories
- Estimate effort for each component
- Plan 2-week sprint execution
- Assign tasks to team

---

*Generated by BMAD Method v6 - Creative Intelligence*
*Session duration: 45 minutes*
*Techniques: SWOT Analysis, Reverse Brainstorming, Starbursting*
