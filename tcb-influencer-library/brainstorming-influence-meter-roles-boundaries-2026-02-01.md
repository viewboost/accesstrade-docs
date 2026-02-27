# Brainstorming Session: Vai Trò và Ranh Giới Trách Nhiệm của Influence-Meter

**Date:** 2026-02-01
**Objective:** Làm rõ vai trò của Influence-Meter trong hệ sinh thái, đặc biệt về việc ai sẽ cung cấp thông tin manual (demographics, profile enrichment)
**Context:** Demographics v1.1 implementation cần xác định rõ ranh giới giữa IM (API service), AT-Core (admin UI), và TCB Portal (influencer UI)

---

## Techniques Used

1. **Starbursting** - Đặt câu hỏi Who/What/Where/When/Why/How
2. **Six Thinking Hats** - Phân tích từ 6 góc độ (Facts, Emotions, Risks, Benefits, Creativity, Process)
3. **SWOT Analysis** - Đánh giá 3 phương án thiết kế

---

## Ideas Generated

### Category 1: Architecture & Responsibility Boundaries

**Nguyên tắc phân chia trách nhiệm:**

**IM (Influence-Meter) chịu trách nhiệm:**
- ✅ API endpoints (REST/GraphQL)
- ✅ Data storage (MongoDB - demographics, submissions, trust scores)
- ✅ Rule-based inference engine (category mappings, hashtag analysis, location inference)
- ✅ OCR processing (Google Cloud Vision API integration)
- ✅ Trust scoring algorithm (calculate trust based on history)
- ✅ Background jobs (daily refresh, cache invalidation)
- ✅ Automated validation checks (risk scoring, fraud detection)
- ✅ Multi-tenant data isolation

**AT (AccessTrade) chịu trách nhiệm:**
- ✅ All UI (influencer portal, admin dashboard)
- ✅ Business logic customization (eligibility rules, campaign matching)
- ✅ Verification decisions (approve/reject submissions)
- ✅ User authentication & authorization
- ✅ Notification system (email, in-app)
- ✅ Custom workflows (onboarding, gamification)

**TCB/Vinfast (End Customers) chịu trách nhiệm:**
- ✅ End-user experience
- ✅ Branding customization
- ✅ Local compliance (GDPR, data privacy laws)

**Ranh giới rõ ràng:**
- IM = **Data service** (API-only, no UI)
- AT = **Business logic + UI** (owns user experience)
- TCB/Vinfast = **End customer customization** (white-label on top of AT platform)

---

### Category 2: Data Flow & Integration Patterns

**Manual Input Flow (Influencer → IM → AT → IM):**

```
1. Influencer submits demographics
   Location: TCB Portal (AT owns UI)
   Action: Upload screenshot + manual form
   API Call: POST /api/v1/demographics/:profileId/submit
   Payload: {screenshot: File, manual_data: {age, gender, location}}

2. IM processes submission
   Actions:
   - OCR extraction (Google Cloud Vision)
   - Store submission in MongoDB
   - Calculate risk score (automated checks)
   - Return extracted data + submissionId
   Response: {submissionId, status: "pending", extracted_data, risk_score}

3. IM sends webhook to AT
   Trigger: New submission created
   API Call: POST https://at-core.com/webhooks/demographics-pending
   Payload: {submissionId, profileId, risk_score, extracted_data}

4. AT displays in admin queue
   Location: AT-Core Admin UI (AT owns)
   Data Source: GET /api/v1/admin/demographics/queue
   Display: Pending submissions sorted by risk score (high → low)

5. Admin verifies submission
   Location: AT-Core Admin UI
   Action: Review screenshot, compare with rule-based estimate
   API Call: POST /api/v1/admin/demographics/:submissionId/verify
   Payload: {action: "approve", trust_score_adjustment: +0.1, notes: "..."}

6. IM updates trust & marks verified
   Actions:
   - Update trust score (0.7 → 0.8)
   - Mark submission as verified
   - Invalidate cache for profileId
   - Send webhook to AT

7. AT notifies influencer
   Location: TCB Portal notification system
   Message: "Your demographics have been verified! ✓"
```

**Data Ownership Mapping:**

| Data Type | Stored In | Accessed Via | Owner |
|-----------|-----------|--------------|-------|
| Demographics (age, gender, location) | IM MongoDB | IM API | IM |
| Submissions (screenshot, OCR results) | IM MongoDB | IM API | IM |
| Trust scores | IM MongoDB | IM API | IM |
| User profiles (name, email, social) | AT Database | AT API | AT |
| Campaign data | AT Database | AT API | AT |
| Verification decisions (approve/reject) | IM MongoDB (audit log) | IM API | IM stores, AT decides |

**No Data Duplication:**
- AT does NOT store demographics locally (calls IM API real-time)
- AT can cache IM responses (Redis TTL 7 days)
- Cache invalidation: IM webhook triggers AT to clear cache

---

### Category 3: User Roles & Access Patterns

**WHO does WHAT WHERE:**

| Actor | Action | Interface | API Endpoint | Owner |
|-------|--------|-----------|--------------|-------|
| **Influencer** | Submit demographics | TCB Portal (React UI) | `POST /demographics/:id/submit` | AT owns UI |
| **Influencer** | View own demographics | TCB Portal (Dashboard) | `GET /demographics/:id` | AT owns UI |
| **Influencer** | Update screenshot | TCB Portal (Settings) | `PUT /demographics/:id/update` | AT owns UI |
| **AT Admin** | Review queue | AT-Core Admin (Next.js) | `GET /admin/demographics/queue` | AT owns UI |
| **AT Admin** | Approve submission | AT-Core Admin (Verification page) | `POST /admin/demographics/:id/verify` | AT owns UI |
| **AT Admin** | Reject submission | AT-Core Admin (Verification page) | `POST /admin/demographics/:id/verify` | AT owns UI |
| **AT Admin** | Adjust trust manually | AT-Core Admin (Profile page) | `POST /admin/trust/:profileId/adjust` | AT owns UI |
| **AT Admin** | View analytics | AT-Core Admin (Analytics) | `GET /admin/analytics/demographics` | AT owns UI |
| **IM Operations** | Monitor system health | IM Internal Dashboard | `/internal/metrics` | IM owns (minimal) |
| **IM Operations** | Debug stuck jobs | IM Debug Console | `/internal/jobs/:jobId/retry` | IM owns (minimal) |
| **IM Operations** | View submission details | IM Debug Console | `/internal/debug/:submissionId` | IM owns (minimal) |
| **Automated System** | Refresh rule-based estimates | IM Cron Job | (internal scheduler) | IM owns |
| **Automated System** | Send verification webhooks | IM Webhook Service | (outbound HTTP) | IM owns |

**Key Principle:**
- **User-facing actions** → AT owns UI (full customization)
- **Internal operations** → IM owns minimal tools (read-only, debugging)
- **NO overlap**: IM internal tools do NOT have verify/approve actions (that's AT's job)

---

### Category 4: Technical Implementation Details

**API Endpoints (Recommended Structure):**

```typescript
// ============================================
// INFLUENCER-FACING APIs (called by AT Portal)
// ============================================

// Submit new demographics (screenshot + manual)
POST /api/v1/demographics/:profileId/submit
Request: {
  screenshot?: File,
  manual_data: {
    age_distribution: {13_17: 10, 18_24: 40, 25_34: 30, 35_44: 15, 45_plus: 5},
    gender_distribution: {male: 30, female: 65, other: 5},
    location_distribution: [{country: "VN", percentage: 85}, ...]
  },
  data_source: "TikTok Analytics" | "Instagram Insights" | "Manual Estimate",
  data_date: "2026-01-15"
}
Response: {
  submissionId: "sub_abc123",
  status: "pending" | "verified" | "rejected",
  extracted_data: {...}, // OCR results if screenshot provided
  risk_score: 0.3,
  estimated_review_time: "2-4 hours"
}

// Get current demographics for profile
GET /api/v1/demographics/:profileId
Response: {
  age_distribution: {...},
  gender_distribution: {...},
  location_distribution: [...],
  confidence_score: 0.75,
  data_source: "manual_verified" | "rule_based" | "hybrid",
  last_updated: "2026-01-20T10:00:00Z",
  trust_score: 0.85
}

// Update existing demographics
PUT /api/v1/demographics/:profileId/update
Request: {screenshot?, manual_data?, data_source?, data_date?}
Response: {submissionId, status, ...}

// ============================================
// ADMIN-FACING APIs (called by AT Admin UI)
// ============================================

// Get pending submissions queue
GET /api/v1/admin/demographics/queue?tenant=AT.TCB&sort=risk_score&limit=20
Response: {
  submissions: [
    {
      submissionId: "sub_abc123",
      profileId: "prof_xyz",
      influencer_name: "Mai Beauty",
      submitted_at: "2026-02-01T09:00:00Z",
      risk_score: 0.7,
      screenshot_url: "https://...",
      extracted_data: {...},
      rule_based_estimate: {...}
    },
    ...
  ],
  total_count: 45,
  page: 1
}

// Get submission details
GET /api/v1/admin/demographics/:submissionId
Response: {
  submissionId,
  profileId,
  screenshot_url,
  extracted_data,
  manual_data,
  rule_based_estimate,
  automated_checks: {
    percentage_sum_valid: true,
    category_alignment: "warning", // female% lower than expected for beauty
    data_freshness: "pass",
    screenshot_format: "pass"
  },
  risk_score: 0.7,
  trust_score_current: 0.5
}

// Verify submission (approve/reject)
POST /api/v1/admin/demographics/:submissionId/verify
Request: {
  action: "approve" | "reject" | "request_clarification",
  reason?: "Fake screenshot" | "Unrealistic data" | "...",
  trust_score_adjustment?: +0.1 | -0.4,
  notes?: "Manual notes from admin"
}
Response: {
  status: "verified" | "rejected",
  new_trust_score: 0.8,
  demographics_updated: true
}

// Manually adjust trust score (rare)
POST /api/v1/admin/trust/:profileId/adjust
Request: {
  adjustment: +0.1 | -0.2,
  reason: "Correcting error" | "Penalty for fraud"
}
Response: {new_trust_score: 0.75}

// Get analytics dashboard data
GET /api/v1/admin/analytics/demographics?tenant=AT.TCB
Response: {
  coverage_percentage: 58,
  high_confidence_percentage: 45,
  pending_verifications: 12,
  avg_verification_time_hours: 3.5,
  auto_approve_rate: 32,
  fraud_alerts: 2,
  confidence_distribution: {low: 20, medium: 35, high: 45},
  data_source_breakdown: {rule_based: 40, manual_verified: 35, hybrid: 25}
}

// ============================================
// TENANT CONFIG APIs (called by AT system)
// ============================================

// Get tenant configuration
GET /api/v1/tenants/:tenantId/config
Response: {
  tenantId: "AT.TCB",
  trust: {
    auto_approve_threshold: 0.85,
    low_confidence_threshold: 0.65,
    decay_rate_days: 90
  },
  confidence: {
    hard_hide_threshold: 0.60,
    medium_tier_min: 0.60,
    high_tier_min: 0.75
  },
  webhooks: {
    submission_created: "https://at-core.com/webhooks/demographics-pending",
    submission_verified: "https://at-core.com/webhooks/demographics-verified",
    trust_score_changed: "https://at-core.com/webhooks/trust-changed"
  },
  category_mappings: {...}, // custom overrides
  rate_limits: {
    submissions_per_influencer_per_day: 3,
    api_requests_per_hour: 1000
  }
}

// Update tenant configuration
PUT /api/v1/tenants/:tenantId/config
Request: {trust?, confidence?, webhooks?, category_mappings?, rate_limits?}
Response: {updated: true, config: {...}}

// ============================================
// INTERNAL IM OPERATIONS APIs (NOT exposed to AT)
// ============================================

// System health metrics
GET /internal/metrics
Response: {
  api_performance_p95: 450, // ms
  ocr_success_rate: 87,
  queue_depth: 12,
  cache_hit_rate: 82,
  error_rate_last_hour: 0.02
}

// Job queue monitor
GET /internal/jobs?status=failed&limit=50
Response: {
  jobs: [
    {jobId, type: "refresh_demographics", status: "failed", error, created_at, attempts},
    ...
  ]
}

// Retry failed job
POST /internal/jobs/:jobId/retry
Response: {status: "queued", retry_attempt: 2}

// Debug submission details (extended info)
GET /internal/debug/:submissionId
Response: {
  submissionId,
  raw_ocr_output: {...},
  processing_timeline: [...],
  error_logs: [...],
  webhook_delivery_attempts: [...]
}
```

**Webhook Events (IM → AT):**

```typescript
// Event 1: New submission created
POST https://at-core.com/webhooks/demographics-pending
Payload: {
  event: "demographics.submission.created",
  submissionId: "sub_abc123",
  profileId: "prof_xyz",
  tenantId: "AT.TCB",
  risk_score: 0.7,
  timestamp: "2026-02-01T10:00:00Z"
}

// Event 2: Submission verified
POST https://at-core.com/webhooks/demographics-verified
Payload: {
  event: "demographics.submission.verified",
  submissionId: "sub_abc123",
  profileId: "prof_xyz",
  action: "approved" | "rejected",
  new_trust_score: 0.8,
  timestamp: "2026-02-01T11:00:00Z"
}

// Event 3: Rule-based estimate updated
POST https://at-core.com/webhooks/demographics-updated
Payload: {
  event: "demographics.estimate.updated",
  profileId: "prof_xyz",
  old_confidence: 0.65,
  new_confidence: 0.70,
  reason: "New content crawled",
  timestamp: "2026-02-01T12:00:00Z"
}

// Event 4: Trust score changed
POST https://at-core.com/webhooks/trust-changed
Payload: {
  event: "trust.score.changed",
  profileId: "prof_xyz",
  old_trust: 0.7,
  new_trust: 0.8,
  reason: "Submission approved",
  timestamp: "2026-02-01T11:00:00Z"
}

// Event 5: Eligibility status changed (optional)
POST https://at-core.com/webhooks/eligibility-changed
Payload: {
  event: "eligibility.status.changed",
  profileId: "prof_xyz",
  old_status: "eligible",
  new_status: "not_eligible",
  reason: "Demographics updated, no longer meets criteria",
  timestamp: "2026-02-01T12:30:00Z"
}
```

**Webhook Delivery Guarantees:**
- At-least-once delivery (IM retries up to 3 times)
- Exponential backoff: 1s, 4s, 16s
- AT must respond with 2xx status (200-299) to acknowledge
- IM stores delivery attempts for debugging

---

### Category 5: Risk Mitigation Strategies

**Risk 1: Confusion về ranh giới trách nhiệm**

**Symptoms:**
- AT team hỏi: "Tại sao IM không có UI để verify?"
- IM team hỏi: "Tại sao AT không dùng IM admin tools?"
- Duplicate work: Both teams build similar features

**Mitigation:**
- ✅ **Clear documentation**: Architecture diagram showing boundaries
- ✅ **Decision framework**: "Is this data or business logic?" (see Blue Hat section)
- ✅ **Weekly sync**: AT + IM teams review integration points
- ✅ **Reference implementation**: IM provides Figma designs + code examples (AT copies, not imports)

---

**Risk 2: IM API không đủ flexible cho AT customization**

**Symptoms:**
- AT requests frequent IM API changes
- AT forks IM code to add custom logic
- Slow iteration speed (waiting for IM releases)

**Mitigation:**
- ✅ **Config-driven API**: Thresholds, rules, mappings → sent via `/tenants/:id/config`
- ✅ **Webhook architecture**: Custom logic in AT webhooks (not IM code)
- ✅ **Feature flags**: IM API supports `?features=ocr,auto_approve` to enable/disable
- ✅ **Versioned API**: `/v1/`, `/v2/` for backwards compatibility

---

**Risk 3: Data sync issues (AT cache stale data)**

**Symptoms:**
- Influencer sees updated demographics in TCB Portal
- Brand sees old demographics in campaign matching
- Eligibility flips unexpectedly

**Mitigation:**
- ✅ **Cache invalidation webhooks**: IM sends `demographics.updated` → AT clears cache
- ✅ **Short TTL**: AT caches IM responses for max 7 days (configurable)
- ✅ **Audit trail**: All data changes logged with timestamp
- ✅ **Fallback**: If cache inconsistent, AT can force refresh via `?force_refresh=true`

---

**Risk 4: Trust score gaming (influencers submit fake data repeatedly)**

**Symptoms:**
- Influencer submits fake screenshot → rejected → trust -0.4
- Submits again with different fake data → rejected → trust -0.4
- Repeats 5 times → trust = 0.0 → banned
- But then creates new account → starts fresh

**Mitigation:**
- ✅ **Rate limiting**: Max 3 submissions per influencer per day
- ✅ **Device fingerprinting**: Detect same device creating multiple accounts
- ✅ **Screenshot similarity**: Flag duplicate/edited screenshots (FR-012 advanced checks in v1.2)
- ✅ **Admin alerts**: High-risk patterns flagged for manual review

---

**Risk 5: IM Operations blind spots (cannot debug AT issues)**

**Symptoms:**
- AT admin reports: "Verification stuck, cannot approve"
- IM team asks: "What's the submissionId? What error did you see?"
- AT team doesn't know (UI doesn't show technical details)
- Slow incident response

**Mitigation:**
- ✅ **IM Internal Dashboard**: Read-only view of all submissions (including AT's)
- ✅ **Audit logs**: IM logs all API calls (AT admin ID, action, timestamp)
- ✅ **Debug console**: IM team can view submission timeline, webhook delivery status
- ✅ **Shared metrics**: Both teams see same health metrics (API latency, error rate)

---

### Category 6: Future Extensibility

**V2 Features (Phase 2 - After v1.1 Launch):**

1. **GraphQL API for real-time updates**
   - Replace polling with subscriptions: `subscription { queueUpdated(tenantId: "AT.TCB") }`
   - Better for admin UI (live updates when new submission arrives)

2. **ML-based inference engine**
   - Train model using v1.1 verified data as ground truth
   - Improve accuracy from 60-65% (rule-based) to 75-80% (ML)
   - Hybrid approach: ML + rules

3. **Advanced fraud detection**
   - Image similarity (detect duplicate screenshots)
   - EXIF metadata analysis (detect tampering)
   - Behavioral signals (submission patterns, timing)

4. **Multi-language support**
   - i18n for error messages
   - Support Thai, Indonesian demographics (not just Vietnamese)

5. **Audience lookalike matching**
   - "Find influencers with similar audiences to this profile"
   - Vector similarity search (demographics embeddings)

**Integration Opportunities:**

1. **Other AT products**
   - Ambassador platform can use same IM API
   - AT multi-tenant instance → each tenant isolated in IM

2. **Non-AT customers**
   - IM can serve other platforms (not just AT)
   - White-label IM with different tenant configs

3. **Third-party data enrichment**
   - Partner with HypeAuditor for cross-validation
   - Integrate with Social Blade for historical trends

---

## Key Insights

### Insight 1: "API-Only IM" là giải pháp duy nhất phù hợp với business model

**Description:**
Influence-Meter KHÔNG nên build UI (kể cả internal admin tools cho verification workflow), vì:
- Business model: AT sells source code to TCB/Vinfast → cannot have IM components
- Separation of concerns: IM = data service, AT = business logic + UI
- Flexibility: AT customizes UI for different customers

**Source:** Starbursting (WHO/WHAT/WHERE questions), SWOT Analysis (Option C rejected)

**Impact:** HIGH
**Effort:** LOW (this is current plan, just confirms it)

**Why it matters:**
Đây là foundation principle cho tất cả design decisions. Nếu vi phạm nguyên tắc này (build IM UI), sẽ tạo ra ownership conflicts và business model breakdown.

**Actionable Decision:**
- ✅ IM provides **API only** (no UI components, no embeddable SDK)
- ✅ AT builds all user-facing UI (influencer portal, admin dashboard)
- ✅ IM can have minimal internal tools (metrics dashboard, debug console) - read-only, not for verification

---

### Insight 2: Manual data input flow cần 3 actors rõ ràng - không phải 2

**Description:**
Demographics v1.1 PRD hiện tại thiếu làm rõ vai trò của **3 actors**:
1. **Influencer** (via TCB Portal - AT owns UI) → Submit data
2. **AT Operations** (via AT-Core Admin - AT owns UI) → Verify submissions
3. **IM Operations** (via minimal internal tools - IM owns) → Monitor system health, debug stuck jobs

**Current PRD chỉ focus vào #1 và #2**, thiếu #3 → IM team không có tools để debug khi có issues.

**Source:** Starbursting (WHO questions), Six Thinking Hats (Black Hat - IM Operations blind spots)

**Impact:** MEDIUM
**Effort:** LOW

**Why it matters:**
- Nếu không có IM internal tools → IM team cannot troubleshoot issues independently
- But nếu build full admin UI → confusing với AT admin UI
- **Solution**: IM builds **minimal read-only dashboard** (metrics, job queue status, debug console) - NOT full verification UI

**Recommended Action:**
Update PRD/Architecture to include:
- **FR-020**: IM Internal Operations Dashboard (Could Have)
  - Metrics: API performance, OCR success rate, queue depth
  - Job monitor: View stuck jobs, retry failed jobs
  - Debug: View submission details, raw OCR output
  - **NOT included**: Verify/Approve actions (that's AT responsibility)

---

### Insight 3: Webhook architecture cần đảo ngược - IM gọi AT, không phải AT poll IM

**Description:**
Current PRD suggests AT polls queue (`GET /admin/demographics/queue`). This is inefficient:
- Polling wastes resources (AT checks every 30s, even when no new submissions)
- Delayed notifications (up to 30s latency)
- Scalability issue (100 AT instances polling → high load)

**Better approach: Event-driven webhooks**
- IM sends webhook to AT when event occurs: `POST https://at-core.com/webhooks/demographics-pending`
- AT immediately knows about new submission → can show real-time notification to admin
- Reduces IM API load (no polling)

**Source:** Six Thinking Hats (Green Hat - Creative solutions), Starbursting (HOW questions)

**Impact:** HIGH
**Effort:** MEDIUM

**Why it matters:**
- Real-time notifications improve admin UX (faster verification)
- Reduces infrastructure cost (no polling traffic)
- Scalable to multiple tenants (each tenant registers own webhook URL)

**Recommended Action:**
Update Architecture/PRD:
- Add webhook system to IM API design
- AT implements webhook handlers: `/webhooks/demographics-pending`, `/webhooks/demographics-verified`
- Fallback: If webhook fails, AT can still poll queue (backwards compatibility)

---

### Insight 4: Trust scoring logic phải ở IM, nhưng threshold phải configurable bởi AT

**Description:**
PRD defines trust scoring system (FR-013), nhưng không rõ **WHO controls trust thresholds**:
- Example: Auto-approve if trust ≥0.85
- Question: AT có thể set threshold = 0.90 (more conservative) hay 0.70 (more aggressive)?

**Current PRD assumes fixed threshold** → không flexible cho different AT customers.

**Recommended approach:**
- **Trust calculation algorithm**: IM owns (consistent across tenants)
- **Trust thresholds**: Configurable per tenant via API
  ```json
  POST /api/v1/tenants/AT.TCB/config
  {
    "trust": {
      "auto_approve_threshold": 0.90,
      "low_confidence_threshold": 0.65,
      "decay_rate_days": 90
    }
  }
  ```

**Source:** Starbursting (WHY/WHAT questions), Six Thinking Hats (Yellow Hat - flexibility benefits)

**Impact:** MEDIUM
**Effort:** LOW (just make thresholds configurable)

**Why it matters:**
- TCB may be conservative (high threshold) → less auto-approvals, more manual review
- Vinfast may be aggressive (low threshold) → faster onboarding, accept more risk
- AT can A/B test different thresholds to optimize conversion vs quality

**Recommended Action:**
Update Architecture:
- Add tenant config API endpoint
- Store tenant-specific thresholds in IM database
- Document default values in PRD

---

### Insight 5: Eligibility flip rate KPI cần tracking ở IM level, không chỉ AT level

**Description:**
PRD defines critical KPI: "Eligibility Flip Rate <15%" (when demographics data updates, profile changes from eligible → not eligible).

**Current assumption**: AT tracks this metric (since AT defines eligibility rules).

**Problem**: IM không visibility vào flip rate → cannot optimize inference algorithm to reduce flips.

**Better approach: Shared metric**
- AT sends eligibility criteria to IM: `POST /api/v1/eligibility/check`
- IM logs when profile switches eligibility (eligible → not eligible)
- IM exposes metric: `GET /api/v1/metrics/eligibility-flip-rate`
- AT monitors metric in dashboard

**Source:** Six Thinking Hats (White Hat - facts), Starbursting (WHAT/WHERE questions)

**Impact:** MEDIUM
**Effort:** MEDIUM

**Why it matters:**
- Flip rate is joint responsibility (IM's inference quality + AT's eligibility rules)
- If IM cannot measure flip rate → cannot improve algorithm
- Transparency: Both teams see same metric → better collaboration

**Recommended Action:**
Update PRD NFR-006 (Accuracy):
- Add eligibility flip rate as measured metric in IM API
- AT sends eligibility check requests to IM (so IM can track)
- IM provides `/metrics/eligibility-flip-rate` endpoint

---

### Insight 6: IM nên cung cấp Reference Implementation để AT không phải "reinvent the wheel"

**Description:**
Option A (API-Only IM) có weakness: "AT team needs to build verification UI from scratch (more work)".

**Creative solution (không conflict với business model):**
IM provides **Reference Implementation** (không ship as package):
- **Figma Designs**: Complete admin verification UI design (free to AT)
- **Code Examples**: Sample React components (MIT licensed, AT can copy)
- **Implementation Guide**: Step-by-step tutorial "How to build verification UI using IM API"
- **Demo App**: Running demo at `demo.influence-meter.com` (AT can test before building)

**This is NOT an SDK** (AT doesn't install package):
- AT copies code to their repo → owns 100%
- AT customizes freely (colors, branding, logic)
- No dependency on IM package versions

**Source:** Six Thinking Hats (Green Hat - creative solutions), SWOT Analysis (Option A opportunities)

**Impact:** HIGH
**Effort:** MEDIUM (design work upfront, saves AT months of development)

**Why it matters:**
- Reduces AT time-to-market (copy reference vs build from scratch)
- Ensures best practices (IM team knows API better than AT)
- Still maintains clean ownership (AT owns copied code)
- IM can update reference implementation → AT can adopt new patterns

**Recommended Action:**
Create deliverable (parallel to v1.1 implementation):
- **Deliverable**: IM Reference Implementation Package
  - Figma design file (export to AT)
  - React component examples (GitHub repo, MIT license)
  - Integration guide (Markdown docs with screenshots)
  - Demo deployment (Vercel/Netlify hosted)
- **Timeline**: Deliver before AT starts UI development (Sprint 2)
- **Maintenance**: IM updates reference when API changes

---

### Insight 7: Category mappings và confidence thresholds cần được research-backed, không phải "best guess"

**Description:**
PRD Appendix C proposes category demographics (Beauty → 82% female, Gaming → 30% female), nhưng **source không rõ ràng**.

**Risk**: Nếu mappings không accurate → rule-based inference fails → low confidence → more manual input needed → defeats purpose.

**Recommended approach:**
- **Sprint 0 (Pre-development)**: Research phase
  - Collect industry reports (Nielsen, Pew Research, Statista)
  - Analyze existing IM database (sample 500 profiles with known demographics)
  - Validate assumptions (is Beauty really 82% female in Vietnam?)
- **Document sources**: Each category mapping cites source
- **Confidence scores based on data quality**:
  - Strong research (n>100 samples) → 0.75 confidence
  - Weak research (n<50 samples) → 0.55 confidence

**Source:** Six Thinking Hats (Black Hat - risks), Starbursting (WHY questions)

**Impact:** HIGH
**Effort:** MEDIUM (research upfront, prevents rework)

**Why it matters:**
- Accuracy targets (60-65% rule-based) depend on good category mappings
- If mappings are wrong → cannot hit KPI targets → project fails
- Research-backed data → easier to defend to stakeholders

**Recommended Action:**
Add to Sprint Plan:
- **Sprint 0 Task**: Category Demographics Research (1 week)
  - Assign to Data/ML Lead
  - Deliverable: Populated mapping table with sources cited
  - Acceptance: PM approves accuracy of mappings (validated against sample data)
- **Documentation**: Add "Research Methodology" section to PRD Appendix
  - Source 1: Nielsen Social Media Demographics Report 2025
  - Source 2: IM database analysis (500 verified profiles)
  - Source 3: Pew Research Vietnam Social Media Study

---

## Statistics

- **Total ideas generated**: 78 ideas across 6 categories
- **Categories**: 6 (Architecture, Data Flow, User Roles, Technical Details, Risk Mitigation, Future)
- **Key insights**: 7
- **Techniques applied**: 3 (Starbursting, Six Thinking Hats, SWOT)
- **Session duration**: ~45 minutes

---

## Recommended Next Steps

### Immediate Actions (Sprint 0 - Before Implementation)

1. **Update PRD with insights**
   - Add FR-020: IM Internal Operations Dashboard (Could Have)
   - Add webhook architecture to integration section
   - Add tenant config API to technical design
   - Add eligibility flip rate tracking to NFRs
   - Add category research phase to Sprint 0

2. **Create Architecture Document**
   - Run `/architecture` to formalize system design
   - Include boundary diagrams (IM vs AT vs TCB)
   - Document webhook flow
   - Design tenant config schema

3. **Research Category Mappings**
   - Assign to Data/ML Lead (1 week)
   - Collect industry reports
   - Analyze IM database samples
   - Validate assumptions

4. **Design Reference Implementation**
   - Assign to IM Design Lead (2 weeks)
   - Create Figma designs for admin verification UI
   - Build demo app (React + IM API integration)
   - Write implementation guide

### Phase Transition (After Sprint 0)

5. **Sprint Planning**
   - Run `/sprint-planning` to break down updated PRD
   - Include reference implementation delivery in Sprint 2
   - Add category research validation in Sprint 1

6. **Stakeholder Alignment**
   - Share this brainstorming doc with AT team
   - Review architecture boundaries
   - Confirm webhook integration approach
   - Agree on reference implementation deliverables

---

## Decision Framework (Blue Hat Synthesis)

**When designing a feature, ask:**

### Question 1: Is this DATA or BUSINESS LOGIC?
- **Data** → IM responsibility (API, storage, inference)
- **Business Logic** → AT responsibility (configurable via IM API)

**Examples:**
- Demographics storage → DATA → IM stores in MongoDB
- Eligibility rules → BUSINESS LOGIC → AT defines, IM executes via config
- Trust scoring algorithm → DATA → IM calculates
- Auto-approve threshold → BUSINESS LOGIC → AT configures

### Question 2: Is this USER-FACING or INTERNAL?
- **User-facing** → AT builds UI (full customization)
- **Internal** → IM builds minimal tools (if needed for operations)

**Examples:**
- Verification queue UI → USER-FACING → AT builds
- Metrics dashboard → INTERNAL → IM builds (minimal)
- Influencer onboarding flow → USER-FACING → AT builds
- Job queue monitor → INTERNAL → IM builds

### Question 3: Who needs to CUSTOMIZE this?
- **If AT/TCB need to customize** → API-driven with config
- **If IM needs to standardize** → Hard-coded in IM

**Examples:**
- Confidence thresholds → AT customizes → API config
- OCR processing → IM standardizes → Hard-coded
- Verification UI → AT customizes → AT builds from scratch (or copies reference)
- Fraud detection rules → IM standardizes → Hard-coded (with feature flags)

### Question 4: Who OWNS the data after contract ends?
- **IM data** → Demographics, submissions, trust scores (service data)
- **AT data** → User profiles, campaigns, notifications (business data)
- **No duplication** → AT calls IM API real-time

**Examples:**
- Demographics history → IM owns (stored in IM MongoDB)
- User authentication tokens → AT owns (stored in AT database)
- Verification decisions → IM stores audit log, AT made decision

---

## Appendix: SWOT Comparison Summary

| Aspect | Option A: API-Only IM | Option B: IM Minimal Tools | Option C: IM SDK/Components |
|--------|----------------------|---------------------------|----------------------------|
| **Strengths** | ✅ Clean ownership<br>✅ AT flexibility<br>✅ IM focus on API | ✅ IM can debug independently<br>✅ Better visibility | ✅ AT faster development<br>✅ Consistent UI |
| **Weaknesses** | ⚠️ AT builds from scratch<br>⚠️ More AT effort | ⚠️ Risk of confusion<br>⚠️ Duplicate effort | ❌ Violates ownership model<br>❌ TCB/Vinfast will reject |
| **Opportunities** | 💡 Reference implementation<br>💡 AT differentiation | 💡 PoC for AT to copy<br>💡 Advanced debugging | (None - not viable) |
| **Threats** | 🔴 AT lacks UI expertise<br>🔴 Longer timeline | 🔴 Scope creep<br>🔴 IM becomes UI team | 🔴 BLOCKER: Business model conflict<br>🔴 Legal issues |
| **Decision** | ✅ **RECOMMENDED**<br>With reference implementation | ✅ **ACCEPTABLE**<br>Minimal tools only | ❌ **REJECTED**<br>Business model violation |

**Final Recommendation:**
**Hybrid of A + B**:
- IM provides **API-only** (no embeddable components)
- IM provides **Reference Implementation** (Figma + code examples for AT to copy)
- IM builds **Minimal Internal Tools** (metrics dashboard, debug console - read-only)
- AT builds **All User-Facing UI** (verification, onboarding, analytics)

---

*Generated by BMAD Method v6 - Creative Intelligence*
*Brainstorming session: 2026-02-01*
*Techniques: Starbursting, Six Thinking Hats, SWOT Analysis*
