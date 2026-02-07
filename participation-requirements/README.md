# Participation Requirements Feature - Documentation

**Feature:** Điều kiện tham gia Campaign (Event Participation Requirements)

**Date:** 2026-02-07

**Status:** Planning Phase

---

## 📚 Document Index

### 1. [Brainstorming & Strategy Analysis](./01-brainstorming-strategy.md)
- **Purpose:** Đánh giá phương án thiết kế hệ thống điều kiện tham gia
- **Content:**
  - SWOT Analysis
  - Reverse Brainstorming (failure scenarios)
  - Starbursting (critical questions)
  - Hybrid 2-tier registration model
  - UX/UI recommendations
  - Success metrics

**Key Findings:**
- ✅ Phương án checklist-based requirements là tốt nhất
- ✅ Hybrid model: Quick registration → Full verification
- ⚠️ Cần balance giữa conversion rate và quality control
- 📊 Target metrics: >60% completion rate, <5% fraud rate

---

### 2. [Code Audit & Technical Analysis](./02-code-audit.md)
- **Purpose:** Rà soát backend code để xác định implementation requirements
- **Content:**
  - Models cần mở rộng (5 models)
  - Services cần update (4 services)
  - New services cần tạo (2 services)
  - Validation checkpoints (3 điểm)
  - API endpoints (12 endpoints)
  - Database indices (6 indices)
  - Critical edge cases & solutions
  - Implementation roadmap (5 phases)

**Key Findings:**
- ✅ Backend architecture sẵn sàng cho feature mới
- 🔧 Cần extend UserEvent, Event models
- 🆕 Cần tạo ParticipationReview collection mới
- ⚠️ 4 critical edge cases cần handle
- 📅 Estimate: 5 tuần development

---

### 3. [Configuration Examples](./03-requirements-config-examples.md)
- **Purpose:** Concrete examples của event configurations và UI mockups
- **Content:**
  - 4 event configuration examples (Techcombank, VinFast, Ambassador, VIP)
  - Database schema examples (Event, UserEvent, ParticipationReview)
  - Admin UI mockups
  - User checklist UI mockups
  - Validation level definitions

**Key Examples:**
- Techcombank: Strict requirements (followers, authentic posts, invitation code)
- VinFast: Moderate requirements (TikTok followers, optional code)
- Ambassador: Basic requirements (account age, email verified)
- VIP: Exclusive requirements (KYC, total followers, quality score)

**🎨 Live Mockup:**
- [View Event Detail Checklist Mockup](https://ambassador.diso.vn/mockup-event-detail-checklist.html) - Interactive HTML mockup cho UI checklist điều kiện tham gia

---

### 4. [PM Response to Requirements](./PM-RESPONSE-TO-REQUIREMENTS.md)
- **Purpose:** Product Manager phân tích 2 đề bài từ Product Owner/Business Operation
- **Content:**
  - Đề bài 1: Hỗ trợ Facebook Post cho creators (manual phase 1, auto phase 2)
  - Đề bài 2: Thu thập thông tin liên hệ (phone/email) từ creators upfront
  - Phân tích và đề xuất Unified Participation Requirements System
  - Database design (Event, UserEvent, ParticipationReview)
  - API specifications (12 endpoints)
  - Implementation plan (5 weeks)

**Key Solution:**
- ✅ Một hệ thống giải quyết CẢ HAI đề bài
- ✅ Pre-registration validation (check trước khi submit post)
- ✅ Phone/Email OTP verification integrated
- ✅ Auto + Manual + Hybrid validation levels
- ✅ Flexible per campaign

---

### 5. [Executive Summary (Vietnamese)](./EXECUTIVE-SUMMARY-VI.md)
- **Purpose:** Tóm tắt cho Product Owner và Business Operation (tiếng Việt)
- **Content:**
  - Business case với real-world examples
  - ROI calculation chi tiết (4.5 tháng payback, 73% ROI sau 1 năm)
  - Giải thích từng requirement với reasoning
  - UI mockups (ASCII art)
  - Timeline visualization

**Key Highlights:**
- 💰 Tiết kiệm 50M đ/tháng (giảm fraud từ 15% → 5%)
- 📈 Tăng ROI từ 150% → 200%+
- 🎯 Dễ hiểu cho non-technical stakeholders

---


## 🎯 Feature Overview

### Business Goal
Đảm bảo chất lượng influencers tham gia campaigns thông qua verification điều kiện trước khi cho phép submit content.

### User Flow

```
User discovers campaign
    ↓
View participation requirements checklist
    ↓
Submit for participation (FB profile, screenshots, invitation code)
    ↓
Admin reviews profile (1-2 days)
    ↓
Approved → Can submit posts
Rejected → Cannot participate
```

### Participation Requirements (Example)

1. ✅ **Account Age:** ≥3 tháng (Auto-validated)
2. ✅ **Invitation Code:** Valid code from partner (Auto-validated)
3. ⏳ **Facebook Profile:** Linked account (Manual review)
4. ⏳ **Facebook Followers:** ≥1,000 followers (Hybrid: Auto-check with manual override)
5. ⏳ **Authentic Posts:** Có bài đăng thật, không spam (Manual review)

---

## 🏗️ Technical Architecture

### Core Models

**1. Event (Extended)**
```typescript
interface Event {
  participationRequirements: {
    enabled: boolean
    requirements: ParticipationRequirement[]
  }
}
```

**2. UserEvent (Extended)**
```typescript
interface UserEvent {
  participationStatus: {
    status: 'pending_review' | 'approved' | 'rejected'
    requirements: Map<string, RequirementStatus>
    approvedAt?: Date
    approvedBy?: AdminId
  }
  canSubmitContent: boolean
}
```

**3. ParticipationReview (NEW)**
```typescript
interface ParticipationReview {
  userEvent: UserEventId
  status: 'pending' | 'approved' | 'rejected'
  facebookProfileUrl: string
  proofScreenshots: string[]
  reviewedBy?: AdminId
  reviewNotes?: string
}
```

### Key Services

- `internal/service/participation.go` - Core participation logic
- `admin/service/participation_review.go` - Admin review operations
- Extended: `content.go`, `user.go`, `event_schema.go`, `reconciliation.go`

### API Endpoints

**Public:**
- `GET /api/v1/events/{id}/participation/requirements` - Get checklist
- `POST /api/v1/events/{id}/participation/submit` - Submit for review
- `GET /api/v1/events/{id}/participation/status` - Check status

**Admin:**
- `GET /api/admin/v1/participation-reviews?status=pending` - Review queue
- `POST /api/admin/v1/participation-reviews/{id}/approve` - Approve
- `POST /api/admin/v1/participation-reviews/{id}/reject` - Reject
- `POST /api/admin/v1/participation-reviews/{id}/check-followers` - FB API check

---

## 🚨 Critical Edge Cases

### 1. Follower Drop After Approval
**Scenario:** User approved với 1,200 followers → drop xuống 900 → submit content

**Solution:**
- Allow submit (không block user experience)
- Re-validate at reconciliation
- Grace period: -10% acceptable
- Flag for manual review if drop >20%

---

### 2. Rejection After Content Submission
**Scenario:** User submit 2 posts → Admin reject profile → Xử lý content?

**Solution:**
- Auto-reject all pending/approved contents
- Notification to user with rejection reason
- No payment processed

---

### 3. Mid-Campaign Requirement Changes
**Scenario:** Requirements thay đổi từ ≥1,000 → ≥2,000 followers mid-campaign

**Solution:**
- Grandfather rule: Lock requirements snapshot at approval time
- New registrations use new requirements
- Existing approved users không bị ảnh hưởng

---

### 4. Facebook Graph API Failures
**Scenario:** API down/rate limited khi admin check followers

**Solution:**
- Queue retry mechanism (retry after 1 hour)
- Manual override option (admin nhập follower count từ screenshot)
- Graceful degradation (không block approval process)

---

## 📊 Success Metrics

### Registration Funnel
- Landing → Start Registration: **>70%**
- Start → Complete Registration: **>60%**
- Complete → First Submit: **>40%**

### Quality Metrics
- Fraud rate: **<5%**
- Support tickets: **<10%** of users
- Payment success rate: **>95%**

### Business Metrics
- Cost per qualified user: **<50k VND**
- ROI per campaign: **>200%**
- User retention (2nd campaign): **>30%**

---

## 🗓️ Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Create new models
- [ ] Database migrations
- [ ] Create indices
- [ ] Basic Participation service

### Phase 2: Public Flow (Week 2)
- [ ] Public APIs
- [ ] Update Content.Create() validation
- [ ] Frontend integration

### Phase 3: Admin Review (Week 3)
- [ ] Admin review queue APIs
- [ ] Admin dashboard UI
- [ ] Facebook Graph API integration
- [ ] Manual override flows

### Phase 4: Reconciliation Integration (Week 4)
- [ ] Update reconciliation flow
- [ ] Re-validation logic
- [ ] Edge case handling
- [ ] Testing

### Phase 5: Polish & Launch (Week 5)
- [ ] Scheduled jobs (follower re-check)
- [ ] Notifications
- [ ] Analytics
- [ ] Documentation
- [ ] Soft launch with 1 event

**Total Duration:** 5 weeks
**Team Size:** 1 backend dev + 1 frontend dev + 0.5 QA

---

## 🔗 Related Documents

- [Facebook Post Integration](../../backend/documents/facebook-post-integration.md)
- Business Context: `/BUSINESS-CONTEXT.md`
- BMAD Workflow Status: `/.bmad/bmad-workflow-status.yaml`

---

## 📝 Next Steps

1. **Review & Alignment**
   - [ ] Stakeholder review of strategy document
   - [ ] Product approval of UX flow
   - [ ] Tech lead approval of architecture

2. **Technical Specification**
   - [ ] Detailed database schema
   - [ ] API request/response specs
   - [ ] Error handling specifications
   - [ ] Security considerations

3. **Design**
   - [x] UI/UX mockup for participation checklist ([View Mockup](https://ambassador.diso.vn/mockup-event-detail-checklist.html))
   - [ ] Admin review dashboard mockups
   - [ ] Email notification templates

4. **Implementation**
   - [ ] Sprint planning
   - [ ] Task breakdown
   - [ ] Begin Phase 1 development

---

## 📞 Contact

**Product Owner:** TBD
**Tech Lead:** TBD
**Project Manager:** TBD

---

*Last Updated: 2026-02-07*
*Status: Planning Phase - Awaiting Approval*
