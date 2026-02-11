# System Operation Gaps Analysis

**Date:** 2026-02-11
**Analysis By:** ViewBoost Team
**Purpose:** Align business presentation & technical spec with actual implementation scope

---

## ❌ GAPS: Current Documents vs Reality

### 1. Budget & Timeline Gap

**Documents say:**
- Development cost: **$27,000 one-time**
- Timeline: 4 weeks with 2 backend + 1 frontend dev

**Reality:**
- ✅ Budget: **66 giờ/tháng total team** (~$3,300/tháng max)
- ✅ Timeline: Phải fit trong 1 tháng với constraint 66h

**Impact:** Documents hiện tại over-promise về resources

---

### 2. AI Integration Gap

**Documents say:**
- Phase 1 includes AI:
  - Google Vision API (logo detection)
  - Google Speech-to-Text (brand mention)
  - OpenAI Moderation API
  - Cost: $10/month AI APIs

**Reality:**
- ✅ **AI = Phase 2** (future enhancement)
- ✅ Phase 1: **100% manual tickboxes only**
- ✅ Cost Phase 1: $0 AI (chỉ development time)

**Impact:** Cần remove AI khỏi Phase 1 scope & cost

---

### 3. Checklist Focus Gap

**Documents say:**
- 4 checklists:
  1. Campaign Participation (13 items, auto + manual)
  2. Pre-Submission (14 items, self-check)
  3. Validation (15 items, **AI-heavy auto-check**)
  4. Admin Review (17 items, **AI assist**)

**Reality:**
- ✅ 4 checklists YES, nhưng simple manual tickboxes:
  1. **Video Idea Check** - Influencer self-check hướng dẫn tạo video
  2. **Campaign Participation** - Influencer must tick trước join
  3. **Content Submission** - Influencer must tick trước submit
  4. **Admin Review** - Admin must tick khi duyệt (AI Phase 2)

**Impact:** Overselling AI automation, underselling manual process

---

### 4. Existing Validation Gap

**Documents say:**
- "Không có validation system hiện tại"
- "Manual review 100%"

**Reality:**
- ✅ **Existing validation đã có:**
  - Link validation (platform, valid URL)
  - Hashtag detection (CheckHashTag function)
  - Metrics check (views, engagement, submission time)
  - Auto-reject conditions (EventAutoRejectCondition)

**Impact:** Documents ignore existing code, làm như build from scratch

---

### 5. Brand Involvement Gap

**Documents say:**
- Admin define checklist templates
- Centralized checklist management

**Reality:**
- ✅ **Brand tham gia define checklist**
  - Khi tạo campaign (đi kèm thể lệ)
  - Brand có thể customize checklist per campaign
  - AI có thể generate & review (Phase 2)

**Impact:** Missing critical stakeholder (Brand) trong process

---

## ✅ WHAT TO KEEP (Đúng hướng)

### Correct Concepts

1. ✅ **4 checklist types** - Concept đúng, chỉ cần simplify
2. ✅ **3-layer architecture** (Influencer/System/Admin) - Đúng
3. ✅ **Progressive micro-checklists** - Đúng insight
4. ✅ **Smart failure reports** - Đúng, keep
5. ✅ **Context-aware checklists** - Đúng (platform, tier, campaign)
6. ✅ **Checklist versioning** - Đúng
7. ✅ **Analytics & metrics** - Đúng

### Correct Impact Metrics

| Metric | Target | Keep? |
|--------|--------|-------|
| First-time approval: 40% → 70% | ✅ Realistic |
| Admin review time: 5min → 2min | ✅ Realistic |
| Reject due to hashtag: 35% → <5% | ✅ Realistic |
| Repeat submission: 40% → 15% | ✅ Realistic |

---

## 🔧 WHAT TO FIX

### Fix #1: Scope Reduction

**Remove from Phase 1:**
- ❌ AI Vision API integration
- ❌ AI Speech-to-Text
- ❌ AI Moderation
- ❌ Asynq worker for AI processing
- ❌ ML-based fraud detection
- ❌ Video quality analysis AI

**Keep in Phase 1:**
- ✅ Manual tickbox checklists (4 types)
- ✅ Leverage existing validation (link, hashtag, metrics)
- ✅ Smart failure messages
- ✅ Context-aware checklist selection
- ✅ Analytics dashboard

---

### Fix #2: Budget Realignment

**Old (Documents):**
```
Development: $27,000 one-time
AI APIs: $10/month
Total Year 1: $28,320
```

**New (Reality):**
```
Development: 66 giờ × $50/giờ = $3,300 (1 tháng)
AI APIs: $0 (Phase 2)
Infrastructure: Existing (no new cost)
Total Year 1: $3,300
```

**ROI Recalculation:**
```
Cost: $3,300
Savings Year 1: $120,000 (admin time) + $24,000 (rework) = $144,000
ROI: 4,264% (instead of 508%)
Payback: 0.27 months (instead of 2.4 months)
```

---

### Fix #3: Checklist Simplification

**From (Complex AI-heavy):**
```yaml
ITEM-205:
  question: "Logo Techcombank visible?"
  checkType: system
  automationLevel: ai
  aiService: Google Vision API
  aiConfidence: 0.92
  requiresHumanReview: if < 0.95
```

**To (Simple Manual):**
```yaml
ITEM-205:
  question: "Logo Techcombank hiển thị rõ ràng trong video?"
  checkType: influencer_tick  # Must tick before submit
  required: true
  helpText: "Logo phải xuất hiện ít nhất 3 giây, rõ nét"
  exampleGood: "https://example.com/good-logo.mp4"

  # Future Phase 2: AI auto-check
  futureAI: {
    service: "Google Vision API",
    autoTick: "if confidence > 95%"
  }
```

---

### Fix #4: Leverage Existing Code

**Current Documents:**
- Build new validation from scratch
- New MongoDB collections
- New Go services

**Better Approach:**
```javascript
// EXTEND existing EventAutoRejectCondition
db.events.update({
  autoRejectConditions: [
    // EXISTING
    { type: "min_views", value: 1000 },
    { type: "hashtag_required", value: "#TCB" },

    // NEW: Add checklist requirement
    {
      type: "checklist_required",
      checklistType: "pre_submission",
      mustPass: true
    }
  ]
});

// EXTEND existing Contents collection
db.contents.update({
  // EXISTING fields: Link, Title, Desc, EventID, Status...

  // NEW: Add checklist tracking
  checklists: {
    preSubmission: {
      completed: true,
      instanceId: ObjectId("..."),
      score: 85,
      passedAt: ISODate("...")
    },
    adminReview: {
      completed: false,
      instanceId: null
    }
  }
});
```

**Impact:** Faster implementation, less breaking changes

---

### Fix #5: Brand-Driven Checklist

**Add to Campaign Creation Flow:**

```javascript
// When Brand creates campaign
db.events.insert({
  // ... existing fields

  // NEW: Brand-defined checklist
  brandChecklist: {
    enabled: true,
    customItems: [
      {
        id: "brand_item_1",
        question: "Video phải nhắc đến 'Mở thẻ online 5 phút'?",
        required: true,
        checkType: "influencer_tick"
      },
      {
        id: "brand_item_2",
        question: "Không so sánh với ngân hàng khác?",
        required: true,
        checkType: "admin_verify"
      }
    ],

    // AI generate checklist (Phase 2)
    aiGenerated: false,
    aiReviewed: false
  }
});
```

---

## 📋 REVISED SCOPE: Phase 1 (66 giờ)

### What We Build

**Week 1 (16h): Database & Backend**
- [ ] Extend `events` collection: add `brandChecklist` field
- [ ] Extend `contents` collection: add `checklists` tracking
- [ ] Create `checklist_instances` collection (minimal schema)
- [ ] API: POST `/api/checklist/execute/:type`
- [ ] API: GET `/api/checklist/instance/:id`

**Week 2 (16h): Frontend - Influencer**
- [ ] Video Idea Checklist modal (self-check guide)
- [ ] Participation Checklist modal (must tick before join)
- [ ] Pre-Submission Checklist modal (must tick before submit)
- [ ] Checklist failure report UI

**Week 3 (16h): Frontend - Admin**
- [ ] Admin Review Checklist (must tick when reviewing)
- [ ] Brand Checklist Builder (when creating campaign)
- [ ] Checklist analytics dashboard (simple metrics)

**Week 4 (18h): Integration & Testing**
- [ ] Integrate with existing validation logic
- [ ] E2E testing: Creator flow
- [ ] E2E testing: Admin flow
- [ ] E2E testing: Brand flow
- [ ] Performance testing
- [ ] Bug fixes & polish

**Total:** 66 giờ

---

## 📊 REVISED SUCCESS METRICS

### Phase 1 (Manual Checklists)

| Metric | Baseline | Target 3mo | How Measured |
|--------|----------|------------|--------------|
| First-time approval | 40% | 60% | contents.status = approved on first submit |
| Admin review time | 5min | 3min | Avg time: review_started → approved/rejected |
| Missing hashtag rejection | 35% | 10% | Reject reason = "hashtag_missing" |
| Repeat submission | 40% | 25% | contents.submitCount > 1 |
| Creator satisfaction | 3.2/5 | 4.0/5 | Survey: "Checklist giúp tôi hiểu yêu cầu rõ hơn" |

### Phase 2 (AI Automation) - Future

| Metric | Phase 1 | Target Phase 2 | How |
|--------|---------|----------------|-----|
| Auto-approval rate | 0% | 30% | AI confidence > 95% → auto approve |
| Admin review time | 3min | 1.5min | AI pre-fill checklist items |
| AI accuracy | N/A | >90% | AI decision vs human decision match rate |

---

## 🎯 RECOMMENDED ACTIONS

### 1. Update BUSINESS-PRESENTATION-CHECKLIST-SYSTEM.md

**Changes needed:**
- ✅ Reduce budget: $28,320 → $3,300 (Year 1)
- ✅ Remove AI from Phase 1 scope
- ✅ Emphasize manual tickboxes
- ✅ Add Brand involvement section
- ✅ Lower Phase 1 targets (40% → 60% approval, not 70%)
- ✅ Recalculate ROI: 4,264% (higher!)
- ✅ Add Phase 2 roadmap for AI

### 2. Update CHECKLIST-PRODUCTION-READY.md

**Changes needed:**
- ✅ Remove AI service implementation sections
- ✅ Simplify checklist items: manual tickboxes only
- ✅ Add "futureAI" fields for Phase 2 planning
- ✅ Extend existing collections instead of new ones
- ✅ Reduce API count: 15 → 5 essential APIs
- ✅ Remove Asynq worker, AI validation logic
- ✅ Add Brand Checklist Builder spec
- ✅ Update deployment to 66h timeline

### 3. Update brainstorming-influencer-checklist-system-2026-02-11.md

**Changes needed:**
- ✅ Update addendum: clarify Phase 1 = manual, Phase 2 = AI
- ✅ Revise ROI: 4,264% (even better!)
- ✅ Add note: "Leveraging existing validation system"

---

## 📈 WHY PHASE 1 IS STILL POWERFUL

**Even without AI, manual checklists deliver HUGE value:**

1. **Creator Education** ✅
   - Video Idea Checklist: Teaches best practices BEFORE creating
   - Pre-Submission Checklist: Catches 80% of issues BEFORE admin sees

2. **Consistent Reviews** ✅
   - Admin Checklist: Forces systematic review (no more ad-hoc)
   - Reduces "forgot to check X" errors

3. **Clear Failure Feedback** ✅
   - "Missing hashtag #TCB" → Link to tutorial
   - "Logo not visible" → Example good video

4. **Brand Control** ✅
   - Brand defines what matters per campaign
   - Not one-size-fits-all checklist

5. **Data for Phase 2** ✅
   - Collect which items fail most → Train AI on those
   - Creator behavior data → Predictive checklists

**Bottom line:** Phase 1 gets 70% of value at 10% of cost. Perfect MVP.

---

## ✅ APPROVAL CHECKLIST

**Before presenting to stakeholders:**

- [ ] Business doc reflects 66h budget, $3,300 cost
- [ ] Technical spec removes AI sections, adds "Phase 2" markers
- [ ] ROI updated: 4,264% (higher than before!)
- [ ] Phase 1 targets realistic: 60% approval (not 70%)
- [ ] Brand involvement clearly explained
- [ ] Existing validation leverage highlighted
- [ ] Phase 2 roadmap included (AI, ML, advanced features)
- [ ] All 3 documents aligned on scope

---

**Conclusion:** Current documents are 80% correct but over-promise on AI and under-leverage existing code. Simple fixes make this a MORE compelling pitch (higher ROI, faster delivery, realistic scope).

**Next Step:** Update 3 documents → Present to AccessTrade + Techcombank → Get approval → Start 66h sprint.
