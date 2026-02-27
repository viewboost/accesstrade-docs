# Brainstorming Session: Influencer Library Roadmap Strategy

**Date:** 2026-02-09
**Objective:** Lập roadmap implementation cho influencer-library, xác định thứ tự ưu tiên giữa AT Core và Techcombank
**Context:** Influence-Meter đã hoàn thành, AT Core và TCB đều có PRD/Tech Spec, cần quyết định execution strategy

---

## Executive Summary

**Problem:** Cần quyết định thứ tự implementation: AT Core first, TCB first, hay parallel development?

**Recommendation:** **PHASED PARALLEL** (nếu có 2 devs) hoặc **AT FIRST** (nếu 1 dev)

**Key Insight:** AT Core là foundation critical cho TCB AT integration (Stories 3-6), nhưng TCB có thể làm private features (60%) song song nếu resource cho phép.

**Timeline:**
- Phased Parallel: **11-12 weeks** (recommended với 2 devs)
- AT First: **15 weeks** (safe fallback với 1 dev)
- Full Parallel: **9 weeks** (high risk, only if urgent)

---

## Techniques Used

1. **Six Thinking Hats** - Đánh giá từ 6 góc nhìn (facts, emotions, risks, benefits, creativity, process)
2. **SWOT Analysis** - So sánh strengths/weaknesses/opportunities/threats của từng approach
3. **Decision Tree Analysis** - Map dependencies và decision paths dựa trên resource/risk tolerance

---

## Scenarios Evaluated

### Scenario A: AT Core First → TCB Second
- Timeline: 15 weeks
- Risk: LOW
- Best for: 1 dev, low risk tolerance
- Value: High stability, clean dependencies

### Scenario B: TCB First → AT Core → TCB Integration
- Timeline: 15-18 weeks (risk of overrun)
- Risk: HIGH (rework, integration hell)
- ❌ **NOT RECOMMENDED**
- Issues: Context switching, API contract mismatch, 40%+ rework

### Scenario C: Full Parallel Development
- Timeline: 9 weeks
- Risk: HIGH
- Best for: 2 senior devs, urgent deadline (<10 weeks)
- Requirements: Daily sync, mock server, locked API contract

### Scenario D: Phased Parallel (RECOMMENDED)
- Timeline: 11-12 weeks
- Risk: MEDIUM
- Best for: 2 devs, medium risk tolerance
- Balance: Speed + Safety

---

## Key Insights

### Insight 1: AT Core là Foundation Critical
**Source:** All techniques
**Impact:** HIGH

AT Core Stories 3-6 (Pool Search, Request, Quota) phải xong trước khi TCB làm AT integration. TCB không thể function fully mà không có AT Partner API.

**Implication:** Ít nhất cần AT Phase 1 (Stories 1-6) ready.

---

### Insight 2: TCB Private Features Độc Lập
**Source:** Decision Tree, Six Hats (Green Hat)
**Impact:** MEDIUM

TCB có thể làm 50-60% features độc lập:
- Database setup (Stories 1-3)
- Private influencer CRUD (Stories 8-10)
- Basic Admin UI
- Tags/notes management

**Opportunity:** Parallel work nếu scope đúng.

---

### Insight 3: Phased Parallel = Optimal Balance
**Source:** SWOT, Decision Tree
**Impact:** HIGH

Nếu có 2 devs, Phased Parallel cho:
- 25% faster than sequential (11w vs 15w)
- 50% safer than full parallel
- Clear integration point (Week 7)
- Acceptable risk level (MEDIUM)

**Recommended approach** với 2 devs available.

---

### Insight 4: Sequential Safe với 1 Dev
**Source:** Six Hats (Black Hat), SWOT
**Impact:** HIGH

If resource constraint (1 dev only):
- AT First là only viable option
- 15 weeks acceptable
- TCB team làm planning/design/frontend trong lúc đợi
- Lowest risk approach

---

### Insight 5: TCB First = Rework Hell
**Source:** Six Hats (Black Hat), SWOT threats
**Impact:** HIGH

Làm TCB trước → high probability of:
- API contract mismatch (TCB expectations ≠ AT reality)
- 40%+ code rework sau khi AT Core xong
- Context switching pain (TCB → AT → TCB)
- Timeline explosion (15w → 20w+)
- Team morale impact (rework is demoralizing)

**Strongly NOT RECOMMENDED** except extreme business pressure.

---

### Insight 6: Full Parallel Cần Discipline
**Source:** Six Hats (Blue Hat), SWOT weaknesses
**Impact:** MEDIUM-HIGH

Full parallel có thể deliver 9 weeks NHƯNG yêu cầu:
- 2 senior backend devs (5+ years exp)
- Daily sync meetings (mandatory, 15min)
- API contract locked Week 1 (no changes)
- Mock server ready Week 1
- Strong PM coordination
- Team có experience với parallel work

**Only do if timeline CRITICAL (<10 weeks).**

---

### Insight 7: Early Demo vs Complete Value
**Source:** Six Hats (Yellow, Red Hat)
**Impact:** MEDIUM

TCB private features có thể demo sớm (Week 6 if TCB first):
- ✅ Business happy, sees progress
- ❌ Incomplete value (no AT Pool access)
- ❌ Limited use case

AT First → TCB sau:
- ⚠️ No demo cho đến Week 12
- ✅ Complete features when delivered
- ✅ Higher long-term value

**Trade-off:** Perception vs Reality

---

### Insight 8: AT Core Enables Scale
**Source:** SWOT opportunities
**Impact:** HIGH

AT Core xong = platform foundation cho multiple partners:
- Techcombank (first customer)
- Vinfast
- Ambassador
- Multi-tenant instance
- Future partners

**Platform thinking:** Build foundation right = scales better long-term.

---

### Insight 9: Mock-First Enables Decoupling
**Source:** Six Hats (Green Hat - Creative)
**Impact:** HIGH (nếu parallel)

Strategy:
1. Week 1: AT creates OpenAPI spec
2. Week 1: Setup mock server (Prism/Mockoon)
3. Week 1-6: TCB develops against mock
4. Week 7: Swap mock → real AT API
5. Integration testing

**Key enabler** cho parallel development success. Decouples teams.

---

### Insight 10: Vertical Slice Alternative
**Source:** Six Hats (Green Hat)
**Impact:** MEDIUM

Alternative approach:
- Week 1-4: AT Minimal (5 core stories: auth, search, request)
- Week 5-8: TCB Minimal (8 core stories: CRUD + AT integration)
- → **End-to-end working by Week 8**
- Week 9-12: AT Polish (subscription, admin)
- Week 13-15: TCB Polish (sync service, admin)

**Benefits:**
- Working system early (stakeholder confidence)
- Real integration testing from Week 8
- Can pivot based on feedback

**Trade-off:** More context switching, less deep focus.

---

## Decision Framework

```
┌─────────────────────────────────────────────────────────────┐
│                 DECISION FLOWCHART                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Q1] Resource Availability?                                │
│         │                                                   │
│         ├─ 1 Backend Dev                                    │
│         │   └─→ AT FIRST (15 weeks, LOW risk) ✅           │
│         │                                                   │
│         └─ 2+ Backend Devs                                  │
│             └─ [Q2] Risk Tolerance?                         │
│                 │                                           │
│                 ├─ LOW → AT FIRST (same as 1 dev)           │
│                 │                                           │
│                 ├─ MEDIUM → PHASED PARALLEL ✅✅             │
│                 │            (11-12w, MEDIUM risk)          │
│                 │                                           │
│                 └─ HIGH                                     │
│                     └─ [Q3] Timeline Critical (<10w)?      │
│                         │                                   │
│                         ├─ YES → FULL PARALLEL ⚡           │
│                         │        (9w, HIGH risk)            │
│                         │        Requirements:              │
│                         │        - Daily sync               │
│                         │        - Mock server              │
│                         │        - Senior devs              │
│                         │                                   │
│                         └─ NO → PHASED PARALLEL             │
│                                 (better safety)             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Recommended Approach: PHASED PARALLEL

**Conditions:**
- ✅ 2 backend developers available
- ✅ Medium risk tolerance
- ✅ 11-12 weeks acceptable
- ✅ Team có khả năng sync daily

**Timeline: 11-12 weeks**

### Phase 1: AT Foundation (Weeks 1-3)

**Focus:** AT Core lays foundation

**Stories:**
- AT-1: Database Schema (Partner, Subscription, Request tables)
- AT-2: Partner Service (CRUD operations)
- AT-3: API Key Auth Guard (authentication + rate limiting)
- AT-4: Quota Service (tracking, monthly reset, tier limits)

**Deliverables:**
- Partner registration working
- API key authentication working
- Quota tracking working
- Database ready

**Goal:** TCB có thể register as partner, get API key

**Resource:** 1 backend dev full-time

**Risk:** LOW (no dependencies)

---

### Phase 2: Parallel Development (Weeks 4-6)

**Focus:** AT builds core API + TCB builds private features [PARALLEL]

**AT Stories:**
- AT-5: Pool Search Endpoint (filters, pagination, visibility)
- AT-6: Pool Request Endpoint (auto-approval, quota deduction)
- AT-7: Subscription Service (status, features, grace period)

**TCB Stories (PARALLEL):**
- TCB-1 to TCB-3: Database Schema (Influencer, SyncLog)
- TCB-4 to TCB-7: Influencer CRUD (List, Detail, Update, Delete)
- TCB-8 to TCB-10: Private Influencer Features (Add by URL via AT /profiles/enrich)
- TCB-11 to TCB-12: Admin UI basics (List page, Detail page)

**Coordination:**
- Daily sync meeting (15min standup)
- API contract review (Wed/Fri)
- Integration test setup (mock server or staging)

**Deliverables:**
- AT Pool API working (search, request, quota)
- TCB private features working (CRUD, tags/notes)
- TCB Admin UI showing private influencers

**Goal:** Both teams productive, AT API testable, TCB có demo value

**Resource:** 2 backend devs (1 AT, 1 TCB)

**Risk:** MEDIUM (need coordination, but phases decoupled)

---

### Phase 3: TCB AT Integration (Weeks 7-9)

**Focus:** Connect TCB to real AT Partner API

**TCB Stories:**
- TCB-13 to TCB-14: AT API Client (credentials, retry, timeout)
- TCB-15: AT Pool Search Integration
- TCB-16: AT Pool Request Integration
- TCB-17: Quota Display Integration
- TCB-18: Admin UI for AT Pool (search page, request flow)

**AT Support:**
- Bug fixes for AT API
- Support TCB integration issues
- Performance optimization

**Deliverables:**
- TCB có thể search AT Pool
- TCB có thể request influencers từ AT
- Quota working end-to-end
- Integration tests pass

**Goal:** End-to-end flow working (TCB search → request → influencer added to TCB DB)

**Resource:** 1 backend dev (TCB), 0.5 backend dev (AT support)

**Risk:** MEDIUM (integration issues expected, but manageable)

---

### Phase 4: Polish & Launch (Weeks 10-12)

**Focus:** Production readiness

**AT Stories:**
- AT-8: Profile Enrichment (async crawl, callback)
- AT-9: Admin Partner UI (partner list, create, API key mgmt)
- AT-10: Admin Visibility UI (influencer visibility controls)

**TCB Stories:**
- TCB-19 to TCB-21: Sync Service (daily cron, freeze logic, manual trigger)
- TCB-22: Webhook Handlers (crawl complete, AT sync)
- TCB-23: Admin UI Polish (sync status, quota display, filters)

**Testing:**
- End-to-end testing
- Load testing
- Security review
- Documentation

**Deliverables:**
- AT Core production-ready (all 10 stories done)
- TCB production-ready (all 23 stories done)
- Documentation complete
- Deployment to production

**Goal:** Launch 🚀

**Resource:** 2 backend devs + frontend + QA

**Risk:** LOW (mostly polish, buffer for issues)

---

## Fallback Plan: AT FIRST (1 Dev)

**If resource constraint (only 1 backend dev):**

### Phase 1: AT Core Complete (Weeks 1-6)
- All 10 AT stories
- Partner API production-ready
- Can onboard test partners

### Phase 2: TCB Complete (Weeks 7-15)
- All 23 TCB stories
- Uses working AT Partner API
- No integration surprises

**Timeline:** 15 weeks
**Risk:** LOW
**TCB team during Phase 1:** Design, planning, frontend, testing setup

---

## Dependencies Analysis

### AT Core Dependencies
```
✅ Influence-Meter Adapter (ready)
✅ Influence-Meter Service (ready)
✅ PostgreSQL (ready)
✅ Redis (ready)
❌ NONE blocking → Can start immediately
```

### TCB Dependencies
```
For PRIVATE features (60% of TCB):
✅ Profile Enrichment API (via AT or direct VB)
✅ PostgreSQL
✅ TCB Auth/SSO
❌ NO AT Core dependency

For AT POOL features (40% of TCB):
❌ AT Partner API (needs AT Stories 3-6)
❌ AT API Credentials (needs AT Story 2)
→ BLOCKED until AT Core Phase 1 done
```

**Conclusion:** TCB private features (Stories 1-12) CAN be done parallel với AT Core (Stories 1-7).

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **API Contract Mismatch** | MEDIUM | HIGH | Lock contract Week 3, daily sync, versioned API (/v1/) |
| **Timeline Overrun (AT)** | MEDIUM | HIGH | 20% buffer, weekly checkpoints, descope AT-8 if needed |
| **Timeline Overrun (TCB)** | LOW | MEDIUM | Sync service (TCB-19-21) can be delayed post-launch |
| **Resource Shortage** | MEDIUM | HIGH | Frontend helps Admin UI, outsource design, reuse components |
| **Integration Issues** | MEDIUM | MEDIUM | Mock server Week 1, integration tests Week 4, staging env |
| **Quota Calculation Bug** | LOW | HIGH | Unit tests, Redis atomic ops, audit logging |
| **Security Vulnerabilities** | LOW | CRITICAL | Security review, penetration testing, OWASP compliance |

---

## Statistics

- **Total Ideas Generated:** 47
- **Categories:** 5 (Technical, Resource, Risk, Business, Execution)
- **Key Insights:** 10
- **Techniques Applied:** 3 (Six Hats, SWOT, Decision Tree)
- **Scenarios Evaluated:** 4 (A, B, C, D)
- **Recommended Path:** Phased Parallel (D)

---

## Immediate Action Items

### Week 0 (Preparation)

**Action 1: Resource Confirmation**
```
Owner: PM / Tech Lead
Deadline: THIS WEEK
Task: Confirm resource availability
Questions:
- Có 1 hay 2 backend devs?
- Frontend dev availability?
- QA resource?

Decision:
- If 2 devs → Execute Phased Parallel
- If 1 dev → Execute AT First
```

**Action 2: API Contract Definition**
```
Owner: AT Backend Dev
Deadline: Week 1 Day 1-2
Task: Create OpenAPI 3.0 spec for AT Partner API
Endpoints:
- POST /api/v1/partners/pool/search
- POST /api/v1/partners/pool/request
- GET /api/v1/partners/quota
- GET /api/v1/partners/subscription
- POST /api/v1/profiles/enrich

Deliverable: /docs/api/partner-api.yaml
Review: TCB team reviews and approves
```

**Action 3: Mock Server Setup (if parallel)**
```
Owner: AT Backend Dev
Deadline: Week 1 Day 3
Task: Setup mock server using OpenAPI spec
Tool: Prism (https://stoplight.io/prism) or Mockoon
Config: Mock responses for happy path + error cases
URL: http://localhost:4010 or staging-mock.accesstrade.vn

Purpose: TCB develops against mock during Phase 1-2
```

**Action 4: Kickoff Meetings**
```
AT Core Kickoff:
Date: Week 1 Day 1
Attendees: AT dev, PM, Tech Lead
Agenda:
- Review PRD + Tech Spec
- Sprint planning (Stories 1-4)
- Setup dev environment
- Create tasks in Jira/Linear

TCB Kickoff (if parallel):
Date: Week 1 Day 1
Attendees: TCB dev, PM, Tech Lead
Agenda:
- Review PRD
- Sprint planning (Stories 1-6)
- Setup dev environment + mock AT API
- Create tasks
```

---

### Weekly Cadence (Weeks 1-12)

**Mon:**
- Sprint planning (if new sprint)
- Team sync (both projects if parallel)

**Wed:**
- API contract review (Phase 2 only)
- Mid-week checkpoint

**Fri:**
- Demo internal progress
- Retrospective (if sprint ends)
- Risk review

**Daily (Phase 2 only):**
- 15min standup (AT + TCB devs together)
- Sync on API changes, blockers

---

## Alternative Approaches Considered

### Vertical Slice Approach
```
Week 1-4: AT Minimal (5 stories: auth, search, request)
Week 5-8: TCB Minimal (8 stories: CRUD + AT integration)
→ End-to-end working by Week 8
Week 9-12: AT Polish (subscription, admin)
Week 13-15: TCB Polish (sync service, admin)

Pros: Working system early, stakeholder confidence
Cons: More context switching, less deep focus
Verdict: Good alternative if early demo critical
```

### Outsource Frontend Approach
```
AT + TCB backend sequential (Weeks 1-12)
Admin UI outsourced to agency (parallel)

Pros: Backend focus, faster Admin UI
Cons: Cost, quality control, integration overhead
Verdict: Consider if frontend resource scarce
```

### Infrastructure-First Approach
```
Week 1-2: Setup infra (DB, Redis, CI/CD, monitoring)
Week 3-8: AT Core
Week 9-15: TCB

Pros: Solid foundation, less tech debt
Cons: Delayed business value
Verdict: Overkill, infra can be setup parallel
```

---

## Success Criteria

### AT Core Success (Week 6)
- [ ] Partner can register and get API key
- [ ] Partner can authenticate with API key
- [ ] Partner can search AT Pool with filters
- [ ] Partner can request influencers (auto-approve if quota)
- [ ] Quota tracking accurate, resets monthly
- [ ] Rate limiting returns 429 when exceeded
- [ ] Admin can create partner
- [ ] Admin can toggle influencer visibility
- [ ] API tests pass (>80% coverage)
- [ ] OpenAPI spec accurate

### TCB Success (Week 12)
- [ ] TCB can add private influencer by URL
- [ ] TCB can list influencers with filters
- [ ] TCB can view influencer detail
- [ ] TCB can update tags/notes
- [ ] TCB can search AT Pool
- [ ] TCB can request influencers from AT
- [ ] Quota display accurate
- [ ] Daily sync working
- [ ] Freeze logic working when expired
- [ ] Admin UI functional (list, detail, search, request)
- [ ] Tests pass (>80% coverage)

### Integration Success (Week 9)
- [ ] TCB → AT API calls working
- [ ] Quota deducted correctly on request
- [ ] Influencers synced from AT to TCB DB
- [ ] Error handling graceful
- [ ] No data inconsistencies
- [ ] Performance acceptable (<200ms p95)

---

## Recommended Next Workflows

### Phase 0: Planning (THIS WEEK)
```
1. Resource confirmation
2. /bmad:sprint-planning for AT Core
   - Break Stories 1-4 into tasks
   - Estimate capacity
3. /bmad:sprint-planning for TCB (if parallel)
   - Break Stories 1-6 into tasks
```

### Phase 1: Implementation (Week 1)
```
1. /bmad:dev-story for AT-1 (Database Schema)
2. /bmad:dev-story for AT-2 (Partner Service)
3. If parallel: /bmad:dev-story for TCB-1 (Database Schema)
```

### Phase 2: Continuous Development (Weeks 2-9)
```
Repeat: /bmad:dev-story for each story
Track: /bmad:workflow-status to monitor progress
```

### Phase 3: Integration Testing (Week 7-9)
```
1. /test for integration test suite
2. /fix:test if issues found
3. Performance testing
```

### Phase 4: Launch Prep (Week 10-12)
```
1. /docs:update to finalize documentation
2. Security review
3. Deployment planning
4. /watzup to review all changes before launch
```

---

## Conclusion

**Primary Recommendation: PHASED PARALLEL (11-12 weeks với 2 devs)**

Phased Parallel cân bằng tốt nhất giữa:
- ✅ Speed (25% faster than sequential)
- ✅ Safety (50% safer than full parallel)
- ✅ Resource efficiency (2 devs productive)
- ✅ Business value (cả AT và TCB progress visible)

**Fallback: AT FIRST (15 weeks với 1 dev)**

Nếu resource constraint, AT First vẫn là lựa chọn solid:
- ✅ Lowest risk
- ✅ Clean dependencies
- ✅ Platform foundation cho future partners

**NOT Recommended: TCB First**

Strongly avoid TCB First do high risk of:
- ❌ Rework (40%+ code changes)
- ❌ Integration hell
- ❌ Timeline explosion

---

**Next Step:** Clarify resource availability → Execute recommended approach → Win 🚀

---

*Generated by BMAD Method v6 - Creative Intelligence*
*Session duration: 60 minutes*
*Techniques: Six Thinking Hats, SWOT Analysis, Decision Tree*
