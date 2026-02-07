# Participation Requirements Feature - Executive Summary

**Date:** 2026-02-07
**Status:** ✅ Planning Complete - Ready for Review
**Priority:** High

---

## 🎯 Mục tiêu

Xây dựng hệ thống **điều kiện tham gia campaign** để đảm bảo chất lượng influencers trước khi cho phép submit content và nhận thưởng.

**Business Goal:**
- Giảm fraud rate từ ~15% xuống <5%
- Tăng ROI campaign từ ~150% lên >200%
- Cải thiện brand safety cho partners (Techcombank, VinFast)

---

## 📋 Deliverables

### ✅ Completed (Planning Phase)
1. ✅ [Brainstorming & Strategy Analysis](./01-brainstorming-strategy.md)
   - SWOT analysis
   - 3 brainstorming techniques (SWOT, Reverse Brainstorming, Starbursting)
   - 7 key insights
   - UX/UI recommendations
   - Success metrics definition

2. ✅ [Code Audit & Technical Analysis](./02-code-audit.md)
   - 5 models cần mở rộng
   - 4 services cần update
   - 2 new services
   - 12 API endpoints
   - 6 database indices
   - 4 critical edge cases + solutions
   - 5-phase implementation roadmap

3. ✅ [Configuration Examples](./03-requirements-config-examples.md)
   - 4 event configuration examples (Techcombank, VinFast, Ambassador, VIP)
   - Database schema examples
   - Admin UI mockups
   - User checklist UI mockups


### 🔜 Next Steps (Implementation Phase)
1. ⏳ Technical Specification (Week 1)
   - Detailed API request/response specs
   - Database migration scripts
   - Error handling specifications

2. ⏳ UI/UX Design (Week 1)
   - High-fidelity wireframes
   - User flow diagrams
   - Admin dashboard designs

3. ⏳ Implementation (Weeks 2-5)
   - Phase 1: Foundation
   - Phase 2: Public flow
   - Phase 3: Admin review
   - Phase 4: Reconciliation
   - Phase 5: Polish & launch

---

## 💡 Key Decisions

### ✅ Decision 1: Checklist-based Requirements (APPROVED)
**Instead of:** All-or-nothing validation upfront

**We chose:** Progressive checklist approach
- User sees requirements list với visual feedback (✅/❌/⏳)
- Can "window shop" campaign trước khi commit
- Self-service CTAs để fulfill từng requirement

**Rationale:**
- Better UX (lower drop-off rate: 30-40% vs 60-80%)
- Transparent (user biết exactly thiếu gì)
- Scalable (dễ add/remove requirements per campaign)

---

### ✅ Decision 2: Hybrid 2-Tier Validation (APPROVED)
**Tier 1 - Auto Validation:**
- Account age ≥3 months → Instant check
- Invitation code → Instant check
- Email verified → Instant check

**Tier 2 - Manual Review:**
- Facebook profile quality → Admin review
- Authentic posts check → Admin review
- Edge cases → Admin override

**Tier 3 - Hybrid (Auto + Manual):**
- Facebook follower count → Try Graph API first, manual if fail
- TikTok follower count → Try TikTok API first, manual if fail

**Rationale:**
- Balance automation và quality control
- Facebook API không 100% reliable → cần manual fallback
- Optimize admin workload (chỉ review high-risk items)

---

### ✅ Decision 3: Reconciliation Re-Validation (APPROVED)
**When:** At payment reconciliation time

**What:** Re-check critical requirements
- Follower count (có drop không?)
- Account status (có bị banned không?)

**How:**
- Grace period: -10% acceptable (1,000 → 900 OK)
- Flag for manual review if drop >20%
- Automatic reject if drop >30%

**Rationale:**
- Prevent exploitation (gain followers → get approved → lose followers → still get paid)
- Fair với users (allow natural fluctuation)
- Protect partner budget

---

### ✅ Decision 4: Grandfather Rule for Mid-Campaign Changes (APPROVED)
**Problem:** Campaign requirements thay đổi giữa chừng

**Solution:** Lock requirements snapshot khi approve
- User approved với v1 requirements → vẫn dùng v1
- New registrations dùng v2 requirements
- Không retroactively apply changes

**Rationale:**
- Fair với users đã committed
- Avoid legal issues
- Maintain trust

---

## 🏗️ Architecture Highlights

### Core Components

**1. Event Configuration**
```
Event.participationRequirements: {
  enabled: true
  requirements: [
    { type, title, validationLevel, validation, required, order }
  ]
}
```

**2. User Participation Tracking**
```
UserEvent.participationStatus: {
  status: 'approved' | 'pending_review' | 'rejected'
  requirements: Map<type, RequirementStatus>
  approvedAt, approvedBy
}
```

**3. Admin Review Queue**
```
ParticipationReview {
  userEvent, status
  facebookProfileUrl, proofScreenshots
  reviewedBy, reviewNotes
}
```

### Key Flows

**Submission Flow:**
```
User → View requirements checklist
     → Submit participation (FB URL + screenshots + code)
     → Admin review (1-2 days)
     → Approved/Rejected
     → Can submit posts / Cannot participate
```

**Content Submit Flow:**
```
User submit post
  → Check participationStatus = 'approved'?
  → YES: Create content
  → NO: Error "Chưa đủ điều kiện tham gia"
```

**Reconciliation Flow:**
```
Payment processing
  → Re-validate follower count
  → Check within grace period?
  → YES: Proceed payment
  → NO: Reject + flag for review
```

---

## 📊 Success Metrics

### Registration Funnel
- **Landing → Start Registration:** >70%
- **Start → Complete Registration:** >60%
- **Complete → First Submit:** >40%

### Quality Metrics
- **Fraud rate:** <5% (currently ~15%)
- **Support tickets:** <10% of users
- **Payment success rate:** >95%

### Business Metrics
- **Cost per qualified user:** <50k VND
- **ROI per campaign:** >200% (currently ~150%)
- **User retention (2nd campaign):** >30%

---

## ⚠️ Risks & Mitigations

### Risk 1: Facebook Graph API Dependency
**Likelihood:** High
**Impact:** Medium

**Mitigation:**
- Manual override option (admin nhập follower count từ screenshot)
- Queue retry mechanism (auto retry sau 1 hour nếu API fail)
- Graceful degradation (không block approval process)

---

### Risk 2: Admin Review Bottleneck
**Likelihood:** Medium
**Impact:** High (user wait time 1-2 days)

**Mitigation:**
- Auto-validate càng nhiều càng tốt (account age, invitation code, email)
- Batch approval tools for admin
- Priority queue (VIP users, high-value campaigns first)
- SLA monitoring (alert if queue >100 pending >24h)

---

### Risk 3: User Drop-off at Registration
**Likelihood:** Medium
**Impact:** High (lose potential good users)

**Mitigation:**
- Progressive disclosure (không overwhelm user với tất cả requirements upfront)
- Clear communication (explain WHY each requirement exists)
- Self-service CTAs (guide user to fulfill requirements)
- Save progress (user có thể quay lại complete sau)

---

### Risk 4: Reconciliation Performance Impact
**Likelihood:** Low
**Impact:** Medium

**Mitigation:**
- Cache participation status (không query mỗi lần)
- Async re-validation (không block payment flow)
- Grace period rules (giảm số lượng cần manual review)

---

## 💰 Budget Estimate

### Development Cost
- **Backend Developer:** 5 weeks × 40h/week × 500k VND/h = **100M VND**
- **Frontend Developer:** 5 weeks × 40h/week × 400k VND/h = **80M VND**
- **QA Engineer:** 5 weeks × 20h/week × 300k VND/h = **30M VND**
- **PM/Designer:** 2 weeks × 20h/week × 400k VND/h = **16M VND**

**Total Development:** ~226M VND

### Operational Cost (Monthly)
- **Facebook Graph API:** Free (within rate limits)
- **Admin review labor:** 2h/day × 20 days × 200k VND/h = **8M VND/month**
- **Server cost increase:** ~5% = **2M VND/month**

**Total Monthly:** ~10M VND

### ROI Projection
**Assumptions:**
- 1,000 users/month participate
- Current fraud rate: 15% → New fraud rate: 5%
- Average loss per fraud case: 500k VND
- Fraud reduction saves: 1,000 × 10% × 500k = **50M VND/month**

**Payback Period:** 226M / 50M = **~4.5 months**

---

## 🗓️ Timeline

### Phase 1: Foundation (Week 1)
**Feb 10 - Feb 16**
- [ ] Database migrations
- [ ] Create models (Event, UserEvent, ParticipationReview)
- [ ] Create indices
- [ ] Basic Participation service

### Phase 2: Public Flow (Week 2)
**Feb 17 - Feb 23**
- [ ] Public APIs (4 endpoints)
- [ ] Update Content.Create() validation
- [ ] Frontend: Requirements checklist page
- [ ] Frontend: Submission form

### Phase 3: Admin Review (Week 3)
**Feb 24 - Mar 2**
- [ ] Admin APIs (8 endpoints)
- [ ] Admin dashboard: Review queue
- [ ] Facebook Graph API integration
- [ ] Manual override flows

### Phase 4: Reconciliation (Week 4)
**Mar 3 - Mar 9**
- [ ] Update reconciliation flow
- [ ] Re-validation logic
- [ ] Edge case handling
- [ ] Integration testing

### Phase 5: Polish & Launch (Week 5)
**Mar 10 - Mar 16**
- [ ] Scheduled jobs (follower re-check)
- [ ] Email notifications
- [ ] Analytics dashboard
- [ ] User documentation
- [ ] Soft launch với Techcombank event

**Total Duration:** 5 weeks
**Launch Date:** Mid-March 2026

---

## 👥 Team & Roles

### Development Team
- **Backend Developer:** 1 FTE (5 weeks)
  - Models, services, APIs
  - Database migrations
  - Reconciliation integration

- **Frontend Developer:** 1 FTE (5 weeks)
  - User checklist UI
  - Submission flow
  - Admin dashboard

- **QA Engineer:** 0.5 FTE (5 weeks)
  - Test planning
  - Integration testing
  - Edge case testing

### Supporting Roles
- **Product Manager:** 0.5 FTE (2 weeks)
  - Requirements clarification
  - Stakeholder communication
  - Success metrics tracking

- **UI/UX Designer:** 0.5 FTE (1 week)
  - High-fidelity wireframes
  - User flow diagrams
  - Design system integration

- **Tech Lead:** 0.25 FTE (5 weeks)
  - Code review
  - Architecture decisions
  - Technical guidance

---

## 📚 Documentation

### Planning Documents (Completed)
1. ✅ [README](./README.md) - Overview và index
2. ✅ [Brainstorming & Strategy](./01-brainstorming-strategy.md) - SWOT, insights
3. ✅ [Code Audit](./02-code-audit.md) - Technical analysis
4. ✅ [Config Examples](./03-requirements-config-examples.md) - Database schemas, UI mockups

### Technical Documents (To be created)
1. ⏳ API Specification - Request/response formats
2. ⏳ Database Migration Guide - Step-by-step migration
3. ⏳ Admin Manual - How to review profiles
4. ⏳ User Guide - How to submit participation

### Operational Documents (To be created)
1. ⏳ Deployment Runbook - Production deployment steps
2. ⏳ Monitoring Setup - Alerts và metrics
3. ⏳ Troubleshooting Guide - Common issues và fixes

---

## ✅ Approval Checklist

### Stakeholder Sign-off
- [ ] **Product Owner:** Strategy và UX approach
- [ ] **Tech Lead:** Architecture và implementation plan
- [ ] **Business Owner:** ROI projection và timeline
- [ ] **Partner (Techcombank):** Requirements definition
- [ ] **Legal/Compliance:** Data privacy và GDPR

### Pre-Implementation Checklist
- [ ] All planning documents reviewed
- [ ] Budget approved
- [ ] Team allocated
- [ ] Timeline confirmed
- [ ] Success metrics agreed
- [ ] Risk mitigation plans in place

### Ready for Implementation When:
- [ ] All approvals received
- [ ] Technical spec completed
- [ ] UI/UX designs finalized
- [ ] Development environment ready
- [ ] Test data prepared

---

## 📞 Contact & Escalation

**Project Lead:** TBD
**Tech Lead:** TBD
**Product Owner:** TBD

**Escalation Path:**
1. Project Lead (day-to-day issues)
2. Tech Lead (technical blockers)
3. Product Owner (requirement changes)
4. CTO (strategic decisions)

---

## 🔗 Quick Links

- [README](./README.md)
- [Brainstorming](./01-brainstorming-strategy.md)
- [Code Audit](./02-code-audit.md)
- [Config Examples](./03-requirements-config-examples.md)
- [Main Docs](/docs/README.md)

---

**Next Action:** Schedule stakeholder review meeting to present findings và get approval to proceed.

---

*Last Updated: 2026-02-07*
*Document Version: 1.0*
*Status: Ready for Review*
