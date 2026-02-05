# Product Requirements Document: Task Management & Workflow Automation System

**Date:** 2026-02-05
**Author:** Product Manager (BMAD Method)
**Version:** 1.0
**Project Type:** Task Management & Workflow Orchestration Platform
**Project Level:** Level 4 (Complex, Multi-Epic, 17-week implementation)
**Status:** Draft - Awaiting Stakeholder Approval

---

## Document Overview

This Product Requirements Document (PRD) defines the functional and non-functional requirements for the **Task Management & Workflow Automation System** for TCB Creator Platform.

This system addresses critical operational bottlenecks identified in the gaps analysis and aims to reduce campaign cycle time from 10-16 days to 3-5 days (-65%) through automated task orchestration, intelligent assignment, SLA tracking, and process automation.

**Related Documents:**
- Gap Analysis: `/accesstrade-projects/techcombank/.bmad/brainstorming/system-operation-gaps-analysis-2026-02-05.md`
- Project Roadmap: `/accesstrade-projects/techcombank/.bmad/PROJECT-ROADMAP-toi-uu-van-hanh.md`
- System Operation Overview: `/accesstrade-projects/techcombank/.bmad/brainstorming/system-operation-overview-2026-02-05.md`

---

## Executive Summary

### Problem Statement

TCB Creator Platform hiện đang vận hành 100% manual với các bottlenecks nghiêm trọng:

**Current State (AS-IS):**
- Campaign cycle time: 10-16 ngày
- Admin workload: 100% manual tasks
- Reconciliation: 2-4 ngày (1000 items × 1 min/item manually)
- SLA compliance: Unknown (không track)
- Task visibility: Admin phải tự check, không có notifications
- Sequential processing: Các phases chạy tuần tự → lãng phí thời gian
- Risk exposure: Không fraud detection, no budget controls

**Business Impact:**
- Lost productivity: 4.8 FTE/month wasted
- Budget risk: Campaign viral có thể vượt budget 300%
- Fraud risk: 10-30% spend có thể là fake engagement (~50-100M VND/campaign)
- Creator churn risk: Slow approvals → Poor creator experience

### Solution Overview

Task Management & Workflow Automation System giải quyết bottlenecks thông qua 3 pillars:

**Pillar 1: Task Management (Foundation)**
- Auto-create tasks from business events
- Intelligent auto-assignment (least-loaded)
- Real-time notifications (Telegram, Email, In-app)
- SLA tracking & escalation

**Pillar 2: Process Automation**
- 90% auto-reconciliation (URL matching + ML)
- Budget tracking & controls
- Fraud detection (rule-based + ML)
- Parallel workflow execution

**Pillar 3: Intelligence & Monitoring**
- Real-time dashboard
- Predictive analytics
- Anomaly detection
- Business continuity & disaster recovery

### Success Criteria

**Primary Metrics:**
- Campaign cycle time: 10-16 days → 3-5 days (-65%)
- Reconciliation time: 2-4 days → 0.5 days (-83%)
- Admin workload: 100% manual → 50% manual (-50%)
- SLA compliance: Unknown → >85%
- Auto-match rate: 0% → >90%

**Financial Impact:**
- Time savings: $172,800/year
- Fraud prevention: $100,000/year
- Budget overrun prevention: $150,000/year
- Downtime prevention: $50,000/year
- **Total annual value: $472,800**

**Investment:**
- Development: $27,000
- Infrastructure: $1,200/year
- Training: $3,000
- **Total: $31,200** (ROI: 1,515%, Payback: 0.8 months)

---

## Product Goals

### Business Objectives

1. **Giảm 65% campaign cycle time** (10-16 ngày → 3-5 ngày)
   - Rationale: Faster campaigns = more campaigns/month = more revenue
   - Measurement: Average days từ campaign setup → report complete

2. **Giảm 50% admin workload** thông qua automation
   - Rationale: Free up team cho strategic work
   - Measurement: Hours spent on manual tasks/week

3. **Nâng SLA compliance lên >85%**
   - Rationale: Predictable operations, better stakeholder confidence
   - Measurement: % tasks completed within SLA deadline

4. **Prevent budget overrun & fraud** (save 100-250M VND/campaign)
   - Rationale: Financial risk mitigation
   - Measurement: Budget variance, fraud detection rate

### Success Metrics

**Operational Metrics:**
- Average cycle time: <5 days
- Reconciliation time: <4 hours
- SLA compliance: >85%
- Auto-reconciliation accuracy: >90%
- Notification response time: <2 hours
- Tasks stuck >48h: <5%

**Financial Metrics:**
- Time saved: 4.8 FTE/month
- Cost reduction: $172,800/year (time) + $300K/year (fraud + budget prevention)
- Campaign throughput: 10/month → 25/month (2.5x)
- Error rate: 5% → <1%

**User Satisfaction:**
- Admin satisfaction: >8/10
- Creator satisfaction: >4/5
- Stakeholder NPS: >50

---

## Functional Requirements

Functional Requirements (FRs) define **what** the system does - specific features and behaviors.

Organized by Epic (8 major epics), prioritized using MoSCoW method.

---

## EPIC 1: Task Queue & Assignment System

### FR-001: Task Domain Model

**Priority:** Must Have

**Description:**
System phải hỗ trợ comprehensive task entity với các properties:
- Basic info: ID, title, description
- Status: draft, assigned, in_progress, blocked, completed, cancelled
- Priority: low, medium, high, urgent
- Type: content_review, reconciliation, bonus_approval, campaign_setup, dispute_resolution
- Assignee: assigned_to user ID
- Dates: created_at, updated_at, due_date, completed_at
- SLA: target_completion, warning_sent, is_breached
- Metadata: content_id, campaign_id, creator_id (flexible JSON)
- Status history: track all transitions với timestamp + who

**Acceptance Criteria:**
- [ ] Task entity có đủ 15+ fields cần thiết
- [ ] Support flexible metadata (JSON object)
- [ ] Status history tracking automatic mỗi khi transition
- [ ] Validation rules enforce (e.g., due_date > created_at)
- [ ] Unit tests cover all validations

**Dependencies:** None

---

### FR-002: Task State Machine

**Priority:** Must Have

**Description:**
System enforce valid state transitions để prevent invalid workflows:
- draft → assigned
- assigned → in_progress, cancelled
- in_progress → completed, blocked, cancelled
- blocked → in_progress
- completed (terminal state)
- cancelled (terminal state)

Authorization checks: Chỉ assigned user hoặc admin mới transition được.

**Acceptance Criteria:**
- [ ] State machine defined với valid transitions map
- [ ] Invalid transitions rejected with error
- [ ] Authorization check before transition
- [ ] Status history recorded automatically
- [ ] Integration tests cover all transitions

**Dependencies:** FR-001

---

### FR-003: Task CRUD API

**Priority:** Must Have

**Description:**
RESTful API cho task operations:
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks` - List tasks (với filters: status, assigned_to, type, priority)
- `GET /api/v1/tasks/{id}` - Get task detail
- `PATCH /api/v1/tasks/{id}` - Update task fields
- `PATCH /api/v1/tasks/{id}/status` - Transition status
- `DELETE /api/v1/tasks/{id}` - Soft delete (set cancelled)

Query parameters support:
- status (multiple): ?status=assigned,in_progress
- assigned_to: ?assigned_to={user_id}
- priority: ?priority=high,urgent
- type: ?type=content_review
- due_date range: ?due_from=...&due_to=...
- Pagination: ?page=1&limit=50
- Sort: ?sort=due_date:asc

**Acceptance Criteria:**
- [ ] All 6 endpoints working
- [ ] Filters work correctly (single + multiple values)
- [ ] Pagination working (limit 50 items/page)
- [ ] Sorting working (asc/desc)
- [ ] API returns JSON responses
- [ ] Error handling (400, 401, 404, 500)
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Integration tests cover all endpoints

**Dependencies:** FR-001, FR-002

---

### FR-004: Auto-Assignment Algorithm

**Priority:** Must Have

**Description:**
System tự động assign tasks cho reviewers based on:
1. **Skill matching**: Task type → Eligible reviewers (e.g., content_review → content reviewers)
2. **Load balancing**: Pick reviewer với ít active tasks nhất
3. **Availability**: Skip reviewers on leave/busy

Algorithm:
```
1. Get eligible reviewers for task type
2. Count active tasks for each reviewer
3. Filter out unavailable reviewers
4. Assign to reviewer with lowest active count
5. If tie → Round-robin
```

**Acceptance Criteria:**
- [ ] Skill matching works (content_review → content reviewers)
- [ ] Load balancing works (assigns to least-loaded)
- [ ] Respects reviewer availability status
- [ ] Round-robin on tie
- [ ] Can manually override auto-assignment
- [ ] Unit tests cover algorithm
- [ ] Integration tests verify assignment

**Dependencies:** FR-003

---

### FR-005: My Tasks Dashboard

**Priority:** Must Have

**Description:**
Reviewer UI để view & manage assigned tasks:
- **Filter by status**: Assigned, In Progress, Completed
- **Sort by**: Priority (urgent first), Due Date (soonest first)
- **Visual indicators**:
  - 🔴 Overdue tasks (red badge)
  - 🟡 Due soon (<24h) (yellow badge)
  - 🟢 Normal (green)
- **Quick actions**:
  - Start task (assigned → in_progress)
  - Complete task
  - Escalate task
- **Task details**: Click to see full context (content, campaign info)

**Acceptance Criteria:**
- [ ] Dashboard displays assigned tasks
- [ ] Filters working (status, priority, due date)
- [ ] Visual priority indicators (colors)
- [ ] Quick actions working (1-click status change)
- [ ] Task detail view có full context
- [ ] Responsive design (desktop + mobile)
- [ ] Loading states & empty states
- [ ] Unit tests for UI components

**Dependencies:** FR-003

---

### FR-006: Manual Task Creation

**Priority:** Must Have

**Description:**
Admin có thể manually create tasks khi cần:
- Form với fields: Title, Type, Priority, Assigned To, Due Date, Description
- Template selection (pre-fill common tasks)
- Bulk creation (e.g., create 10 review tasks for 10 contents)

**Acceptance Criteria:**
- [ ] Create task form working
- [ ] All fields validated
- [ ] Template dropdown working
- [ ] Bulk creation working (CSV import hoặc multi-select)
- [ ] Success notification
- [ ] Integration tests

**Dependencies:** FR-003

---

## EPIC 2: SLA Tracking & Escalation

### FR-007: SLA Configuration per Task Type

**Priority:** Must Have

**Description:**
System allow configure SLA targets cho mỗi task type:
- content_review: 48 hours
- reconciliation: 24 hours
- bonus_approval: 12 hours
- campaign_setup: 4 hours
- dispute_resolution: 72 hours

Configurable via admin UI hoặc config file.

**Acceptance Criteria:**
- [ ] SLA config stored in database hoặc config file
- [ ] Each task type có SLA target
- [ ] Can update SLA config via UI
- [ ] New tasks automatically inherit SLA from type
- [ ] Validation: SLA target > 0

**Dependencies:** FR-001

---

### FR-008: SLA Monitoring Background Job

**Priority:** Must Have

**Description:**
Background worker chạy every 5 minutes để:
1. **Find tasks approaching deadline** (24h warning):
   - Status = assigned | in_progress
   - due_date between (now, now+24h)
   - warning_sent = false
2. **Send warning notification** to assignee
3. **Mark warning_sent = true**
4. **Find overdue tasks**:
   - Status = assigned | in_progress
   - due_date < now
   - is_breached = false
5. **Send breach notification** to assignee + admin
6. **Mark is_breached = true**

**Acceptance Criteria:**
- [ ] Background job runs every 5 min
- [ ] Detects tasks <24h from deadline
- [ ] Sends warning notification (1 time only)
- [ ] Detects overdue tasks
- [ ] Sends breach notification
- [ ] Updates SLA flags in database
- [ ] Integration tests simulate time passing

**Dependencies:** FR-007

---

### FR-009: SLA Escalation Workflow

**Priority:** Should Have

**Description:**
Khi task overdue >24 hours:
- Auto-escalate to manager
- Reassign task to manager
- Notify both assignee + manager
- Log escalation event

**Acceptance Criteria:**
- [ ] Escalation triggers after 24h breach
- [ ] Manager automatically assigned
- [ ] Notifications sent
- [ ] Escalation logged in task history
- [ ] Can disable auto-escalation (config)

**Dependencies:** FR-008

---

### FR-010: SLA Dashboard & Reports

**Priority:** Should Have

**Description:**
Admin dashboard hiển thị SLA metrics:
- **Current SLA compliance rate**: X% tasks completed within SLA
- **Tasks by status**: Pie chart (assigned, in progress, overdue, completed)
- **Overdue tasks list**: Table với assignee, how long overdue
- **SLA trends**: Line chart showing compliance % over time (last 30 days)
- **Team performance**: Table showing SLA compliance by reviewer

Export report to Excel.

**Acceptance Criteria:**
- [ ] Dashboard displays 5 key metrics
- [ ] Charts render correctly
- [ ] Export to Excel working
- [ ] Real-time updates (WebSocket)
- [ ] Responsive design

**Dependencies:** FR-008

---

## EPIC 3: Notification System

### FR-011: Multi-Channel Notification Delivery

**Priority:** Must Have

**Description:**
System gửi notifications qua 3 channels:
1. **Telegram**: Instant, mobile-friendly, inline buttons
2. **Email**: Detailed, async, good for records
3. **In-app**: Notification center in admin UI

Notification types:
- Task assigned
- Task due soon (24h warning)
- Task overdue
- Task completed
- Mention in comments

**Acceptance Criteria:**
- [ ] Telegram notifications working
- [ ] Email notifications working
- [ ] In-app notifications working
- [ ] User can configure preferences (which channels)
- [ ] Delivery tracking (sent, delivered, read)
- [ ] Retry logic on failure (3 attempts)
- [ ] Integration tests for each channel

**Dependencies:** None

---

### FR-012: Telegram Bot Inline Actions

**Priority:** Must Have

**Description:**
Telegram notifications có inline buttons cho quick actions:
- Message: "Bạn có 1 task mới: Review Content #123"
- Buttons: [✅ Approve] [❌ Reject] [👀 View Details]

Clicking button:
- Calls API to transition task status
- Updates message với result
- No need mở admin portal

**Acceptance Criteria:**
- [ ] Inline buttons render correctly
- [ ] Button clicks trigger API calls
- [ ] Message updates after action
- [ ] Error handling (if API fails)
- [ ] Security: Verify callback authenticity
- [ ] Rate limiting: Max 5 actions/min

**Dependencies:** FR-011

---

### FR-013: In-App Notification Center

**Priority:** Must Have

**Description:**
Admin UI có notification dropdown (top-right bell icon):
- **Unread count badge**: Red circle với số
- **Dropdown list**: Last 20 notifications
- **Mark as read**: Click notification → Mark read
- **Mark all as read**: Button
- **Notification types**: Icon + color coding
  - 🔴 Urgent (overdue tasks)
  - 🟡 Warning (due soon)
  - 🟢 Info (task completed)
- **Click notification**: Navigate to task detail page

Real-time updates via WebSocket.

**Acceptance Criteria:**
- [ ] Notification center UI component
- [ ] Unread count badge accurate
- [ ] Dropdown shows last 20 notifications
- [ ] Mark as read working
- [ ] Click notification → Navigate to task
- [ ] Real-time updates (WebSocket)
- [ ] Persists to database
- [ ] Unit tests for UI logic

**Dependencies:** FR-011

---

### FR-014: Notification Preferences

**Priority:** Should Have

**Description:**
User có thể configure notification preferences:
- **Channels**: Enable/disable Telegram, Email, In-app
- **Event types**: Choose which events trigger notifications
  - Task assigned: ✅
  - Task due soon: ✅
  - Task overdue: ✅
  - Task completed: ❌ (don't care)
- **Quiet hours**: Don't send notifications 10pm-8am
- **Digest mode**: Batch notifications, send 1 summary email/day

**Acceptance Criteria:**
- [ ] Preferences UI working
- [ ] Save preferences to database
- [ ] Notification engine respects preferences
- [ ] Quiet hours working (timezone-aware)
- [ ] Digest mode working (daily summary email)

**Dependencies:** FR-011

---

## EPIC 4: Workflow Orchestration Engine

### FR-015: Auto-Task Creation from Business Events

**Priority:** Must Have

**Description:**
System auto-create tasks khi business events occur:

**Event: Content Submitted**
→ Create Task: "Review Content #123"
- Type: content_review
- Assigned to: Auto-assign to reviewer
- Due: created_at + 48h
- Metadata: { content_id, campaign_id, creator_id }

**Event: Campaign Created**
→ Create Tasks:
- "Setup Campaign #456" (assigned to admin)
- "Configure Metrics Tracking" (assigned to tech team)

**Event: Reconciliation Started**
→ Create Task: "Review Reconciliation #789"
- Due: created_at + 24h

**Acceptance Criteria:**
- [ ] Event hooks working for 3+ business events
- [ ] Tasks auto-created with correct template
- [ ] Auto-assignment triggered
- [ ] Notifications sent
- [ ] Metadata linked correctly
- [ ] Integration tests simulate events

**Dependencies:** FR-004

---

### FR-016: Parallel Workflow Execution

**Priority:** Must Have

**Description:**
System support parallel task execution:
- Campaign workflow có parallel gateway
- Example:
  ```
  Setup Campaign (1 task)
      ↓
  [Parallel Gateway]
      ├─► Content Review Tasks (multiple in parallel)
      └─► Tech Setup (1 task)
      ↓
  [Join Gateway] - Wait for ALL parallel tasks complete
      ↓
  Reconciliation (1 task)
  ```

**Acceptance Criteria:**
- [ ] Parallel gateway support
- [ ] Multiple tasks execute simultaneously
- [ ] Join gateway waits for all completions
- [ ] Workflow state tracking
- [ ] Visual workflow diagram in UI
- [ ] Integration tests verify parallel execution

**Dependencies:** FR-015

---

### FR-017: Conditional Workflow Routing

**Priority:** Should Have

**Description:**
Workflow có thể branch based on conditions:
- If content rejected → Create dispute task (optional)
- If reconciliation discrepancy >20% → Escalate to manager
- If budget >90% → Pause new content submissions

**Acceptance Criteria:**
- [ ] Conditional expressions evaluated
- [ ] Correct branch taken
- [ ] Workflow logs decision rationale
- [ ] Unit tests cover conditions

**Dependencies:** FR-016

---

### FR-018: Workflow Templates

**Priority:** Should Have

**Description:**
Pre-defined workflow templates cho common scenarios:
- **Campaign Approval Workflow**: 3-level approval
- **Content Review Workflow**: Submit → Review → Publish
- **Reconciliation Workflow**: Collect → Match → Approve
- **Dispute Resolution Workflow**: Submit → Investigate → Resolve

Admin có thể:
- Clone template
- Customize steps
- Save as new template

**Acceptance Criteria:**
- [ ] 4 pre-defined templates
- [ ] Can clone & customize
- [ ] Templates versioned
- [ ] Can activate/deactivate template
- [ ] UI for template management

**Dependencies:** FR-016

---

## EPIC 5: Budget Tracking & Controls

### FR-019: Real-Time Budget Dashboard

**Priority:** Must Have

**Description:**
Dashboard hiển thị campaign budget status:
- **Allocated**: Total budget (500M VND)
- **Committed**: Approved content chưa paid (350M VND)
- **Spent**: Paid out (200M VND)
- **Available**: Allocated - Committed (150M VND)
- **Forecast**: ML prediction of final spend (480M VND)
- **Utilization Rate**: Committed/Allocated (70%)

Visual progress bar:
- 🟢 Green: <80% utilization
- 🟡 Yellow: 80-95% utilization
- 🔴 Red: >95% utilization

**Acceptance Criteria:**
- [ ] Dashboard displays 6 budget metrics
- [ ] Real-time updates (WebSocket)
- [ ] Progress bar color-coded
- [ ] Alerts when >80% utilization
- [ ] Export budget report to Excel
- [ ] Responsive design

**Dependencies:** None

---

### FR-020: Budget Control Enforcement

**Priority:** Must Have

**Description:**
Before approving content, system check budget constraints:

**Check 1: Campaign Budget**
- Current spend + estimated reward <= Campaign budget
- If violated → Block approval, show error

**Check 2: Creator Cap**
- Creator total earnings (this campaign) + estimated reward <= Creator cap
- If violated → Block approval

**Check 3: Platform Daily Limit**
- Platform spend today + estimated reward <= Platform daily limit
- If violated → Block approval

**Acceptance Criteria:**
- [ ] All 3 checks enforced before approval
- [ ] Clear error messages
- [ ] Can override with manager approval
- [ ] Log all check results
- [ ] Integration tests verify blocks

**Dependencies:** FR-019

---

### FR-021: Auto-Pause Campaign on Budget Exhaustion

**Priority:** Must Have

**Description:**
Khi budget >= 100% utilized:
- Auto-pause campaign (status → PAUSED_BUDGET_EXHAUSTED)
- Block new content submissions
- Send notifications to stakeholders
- Log pause event

Can manually resume after budget increase approved.

**Acceptance Criteria:**
- [ ] Auto-pause triggers at 100% utilization
- [ ] New submissions blocked
- [ ] Notifications sent
- [ ] Can manually resume
- [ ] Integration tests

**Dependencies:** FR-020

---

### FR-022: Budget Forecast ML Model

**Priority:** Should Have

**Description:**
ML model predict final campaign spend based on early trends:
- Input features: submissions_per_day, approval_rate, avg_views, avg_reward
- Train on first 3 days data
- Predict total spend for remaining days
- Confidence score: 85%+

If forecast >120% budget → Alert stakeholders early.

**Acceptance Criteria:**
- [ ] ML model trained on historical data
- [ ] Predictions accurate >85%
- [ ] Forecast updates daily
- [ ] Alerts sent if forecast exceeds budget
- [ ] Model versioning & retraining

**Dependencies:** FR-019

---

## EPIC 6: Fraud Detection System

### FR-023: Rule-Based Fraud Detection

**Priority:** Must Have

**Description:**
Before approving content, run fraud checks:

**Rule 1: Abnormal View Velocity**
- If views_per_hour > 100,000 → Flag "SUSPICIOUS_VIEW_VELOCITY"

**Rule 2: Low Engagement Rate**
- If (likes / views) < 0.5% → Flag "LOW_ENGAGEMENT_RATE"

**Rule 3: New Account**
- If creator account age < 30 days → Flag "NEW_ACCOUNT"

**Rule 4: Follower Spike**
- If follower growth >20% in 1 day → Flag "FOLLOWER_SPIKE"

Scoring:
- 0 flags → Auto-approve
- 1-2 flags → Manual review (yellow flag)
- 3+ flags → Auto-reject (red flag)

**Acceptance Criteria:**
- [ ] 4 fraud rules implemented
- [ ] Scoring algorithm working
- [ ] Flags displayed in review UI
- [ ] Can override (with justification)
- [ ] False positive rate <5%
- [ ] Integration tests

**Dependencies:** None

---

### FR-024: ML-Based Fraud Detection

**Priority:** Could Have

**Description:**
ML model trained on historical fraud data:
- Features: views, likes, comments, shares, follower_count, account_age, etc.
- Model: Random Forest classifier
- Output: Fraud probability (0-1)

Decision thresholds:
- Prob > 0.8 → Auto-reject
- Prob 0.5-0.8 → Manual review
- Prob < 0.5 → Auto-approve

**Acceptance Criteria:**
- [ ] ML model trained (accuracy >90%)
- [ ] Predictions integrated into review flow
- [ ] Model monitoring & drift detection
- [ ] Retraining pipeline (monthly)
- [ ] A/B test vs rule-based

**Dependencies:** FR-023

---

### FR-025: Blacklist Management

**Priority:** Must Have

**Description:**
System maintain blacklist của fraud creators:
- **Permanent ban**: Proven fraud → Never allow again
- **Temporary ban**: Policy violation → Ban 3 months
- **Auto-block**: Blacklisted creator submit → Auto-reject với message

Blacklist operations:
- Add creator to blacklist (reason required)
- Remove from blacklist (appeal approved)
- Check if creator blacklisted (before approval)
- Export blacklist (CSV)

**Acceptance Criteria:**
- [ ] Blacklist CRUD operations
- [ ] Auto-block working
- [ ] Reason required for ban
- [ ] Appeal workflow
- [ ] Blacklist visible to admins only
- [ ] Integration tests

**Dependencies:** FR-023

---

## EPIC 7: Auto-Reconciliation System

### FR-026: Auto-Match Submissions to Crawled Data

**Priority:** Must Have

**Description:**
Reconciliation algorithm:
```
For each content submission:
  1. Find match in crawled data by URL
  2. If match found:
     - Compare views (submission vs crawled)
     - Calculate discrepancy %
     - If discrepancy < 10%:
       → Auto-approve
     - Else if discrepancy 10-20%:
       → Flag for review
     - Else (>20%):
       → Flag as "HIGH_DISCREPANCY"
  3. If no match found:
     → Flag as "NOT_FOUND"
```

Target: 90% auto-match rate.

**Acceptance Criteria:**
- [ ] URL matching algorithm working
- [ ] Discrepancy calculation accurate
- [ ] Auto-approve working (90% of cases)
- [ ] Flagging working (10% of cases)
- [ ] Match accuracy >95%
- [ ] Performance: 1000 items in <30 seconds
- [ ] Integration tests

**Dependencies:** None

---

### FR-027: Flagged Items Review Dashboard

**Priority:** Must Have

**Description:**
Admin UI chỉ show 10% flagged items cần manual review:
- **Filters**: NOT_FOUND, HIGH_DISCREPANCY, DUPLICATE
- **Sort**: By discrepancy % (highest first)
- **Quick actions**:
  - Approve anyway (với note)
  - Reject with reason
  - Bulk approve (select multiple)
- **Comparison view**: Side-by-side submission vs crawled data

**Acceptance Criteria:**
- [ ] Dashboard shows only flagged items
- [ ] Filters & sort working
- [ ] Quick actions working
- [ ] Bulk operations working
- [ ] Comparison view helpful
- [ ] Responsive design

**Dependencies:** FR-026

---

### FR-028: Reconciliation Audit Trail

**Priority:** Should Have

**Description:**
Full audit trail cho mọi reconciliation decision:
- Auto-approved: Log match score, discrepancy
- Manual approved: Log admin, reason, timestamp
- Rejected: Log reason
- Export audit trail to Excel for compliance

**Acceptance Criteria:**
- [ ] All decisions logged
- [ ] Audit trail immutable
- [ ] Export to Excel working
- [ ] Search & filter audit logs
- [ ] Retention policy: 2 years

**Dependencies:** FR-026

---

## EPIC 8: Monitoring, Alerting & Business Continuity

### FR-029: System Health Dashboard

**Priority:** Must Have

**Description:**
Real-time monitoring dashboard:
- **Service Status**: API (UP/DOWN), DB (UP/DOWN), Redis (UP/DOWN), MinIO (UP/DOWN)
- **Resource Usage**: CPU %, Memory %, Disk %
- **Error Rates**: 5xx errors/min, exceptions/min
- **Response Times**: P50, P95, P99 latency
- **Queue Depths**: Asynq pending jobs count

Color coding: 🟢 Green (healthy), 🟡 Yellow (warning), 🔴 Red (critical)

**Acceptance Criteria:**
- [ ] Dashboard displays 15+ metrics
- [ ] Real-time updates (5s refresh)
- [ ] Color-coded health status
- [ ] Historical charts (last 24h)
- [ ] Mobile-friendly

**Dependencies:** None

---

### FR-030: Alert Rules & Notifications

**Priority:** Must Have

**Description:**
Alert rules:
- 🔴 **CRITICAL** (Page on-call immediately):
  - API down >5 min
  - Database primary down
  - Error rate >10%
  - Payment processing stopped
- 🟡 **WARNING** (Notify Slack):
  - CPU >80%
  - Disk >90%
  - Queue depth >1000
  - Response time >2s

Alert channels:
- PagerDuty (critical only)
- Telegram (all alerts)
- Slack #ops-alerts (warnings)

**Acceptance Criteria:**
- [ ] Alert rules configured
- [ ] Alerts sent to correct channels
- [ ] No false alarms (<5%)
- [ ] Alert deduplication (don't spam)
- [ ] Alert resolution tracking

**Dependencies:** FR-029

---

### FR-031: Automated Backup & Restore

**Priority:** Must Have

**Description:**
Automated backup strategy:
- **MongoDB**: Full backup daily (retained 30 days), incremental every 6h
- **Files (MinIO)**: Sync to S3 hourly, versioning enabled, retention 90 days
- **Config**: Infrastructure as Code (Terraform), env vars in vault

Backup testing:
- Monthly restore drill (test in staging)
- RTO (Recovery Time Objective): 1 hour
- RPO (Recovery Point Objective): 15 minutes

**Acceptance Criteria:**
- [ ] Automated backups running
- [ ] Backups uploaded to S3
- [ ] Restore procedure documented
- [ ] Monthly restore test passed
- [ ] Monitoring backup success

**Dependencies:** None

---

### FR-032: Operational Runbooks

**Priority:** Must Have

**Description:**
Runbooks cho common failure scenarios:
1. **Database Failure Recovery**: Step-by-step MongoDB failover
2. **Redis Failure Recovery**: Restart Redis, drain queue
3. **Content Catcher API Outage**: Enable manual metric entry
4. **Payment Processing Failure**: Retry logic, notify creators
5. **Full Disaster Recovery**: Restore from backups

Each runbook:
- Symptom description
- Diagnosis steps
- Recovery steps
- Estimated time
- Validation checklist
- Communication plan

**Acceptance Criteria:**
- [ ] 5 runbooks documented
- [ ] Runbooks tested in staging
- [ ] Accessible to on-call team
- [ ] Updated quarterly

**Dependencies:** FR-031

---

## Non-Functional Requirements

Non-Functional Requirements (NFRs) define **how** the system performs - quality attributes and constraints.

---

### NFR-001: Performance - API Response Time

**Priority:** Must Have

**Description:**
API response times phải đáp ứng:
- P50 (median): <100ms
- P95: <200ms
- P99: <500ms

Measured for:
- GET /api/v1/tasks (list)
- POST /api/v1/tasks (create)
- PATCH /api/v1/tasks/{id}/status (update)

**Acceptance Criteria:**
- [ ] Performance testing passed (1000 requests)
- [ ] Metrics monitored in production
- [ ] Alert if P95 >200ms

**Rationale:**
Fast response times = better UX for admins. Slow APIs frustrate users.

---

### NFR-002: Performance - Database Query Optimization

**Priority:** Must Have

**Description:**
Database queries optimized với indexes:
- Index on tasks.status
- Index on tasks.assigned_to + status (compound)
- Index on tasks.due_date
- Index on tasks.created_at

Query performance targets:
- List tasks: <50ms
- Count tasks: <20ms
- Find by ID: <5ms

**Acceptance Criteria:**
- [ ] All indexes created
- [ ] Query performance tested
- [ ] Explain plan shows index usage
- [ ] No full collection scans

**Rationale:**
Fast queries = scalable system. Without indexes, queries slow down as data grows.

---

### NFR-003: Performance - Concurrent User Capacity

**Priority:** Must Have

**Description:**
System support 100 concurrent users without degradation:
- 50 admins browsing dashboards
- 30 reviewers viewing tasks
- 20 creators submitting content

Load testing scenarios:
- Scenario 1: 100 users × 10 requests/min = 1000 req/min
- Scenario 2: Spike test (100 → 200 users in 1 min)

**Acceptance Criteria:**
- [ ] Load testing passed
- [ ] Response time stable under load
- [ ] No errors under load
- [ ] Auto-scaling tested (if applicable)

**Rationale:**
Peak usage times (campaign launch) require handling concurrent users.

---

### NFR-004: Scalability - Data Volume

**Priority:** Should Have

**Description:**
System handle 1M+ tasks without performance degradation:
- 10K campaigns
- 100K contents
- 1M tasks
- 10M notifications

Database sharding strategy (if needed):
- Shard by campaign_id

**Acceptance Criteria:**
- [ ] Performance tested with 1M tasks
- [ ] Query performance maintained
- [ ] Pagination working efficiently
- [ ] Indexes tuned for scale

**Rationale:**
System needs to grow với business. Plan for 2-3 years growth.

---

### NFR-005: Security - Authentication & Authorization

**Priority:** Must Have

**Description:**
Security requirements:
- **Authentication**: JWT tokens (expire 24h)
- **Authorization**: Role-based access control (RBAC)
  - Admin: Full access
  - Reviewer: View tasks, update assigned tasks only
  - Creator: View own content status only
- **API Security**: API keys for external integrations
- **Encryption**: HTTPS only, TLS 1.2+

**Acceptance Criteria:**
- [ ] JWT authentication working
- [ ] RBAC enforced on all endpoints
- [ ] Unauthorized requests rejected (401, 403)
- [ ] HTTPS enforced
- [ ] Security audit passed

**Rationale:**
Protect sensitive data (creator info, financial data). Prevent unauthorized access.

---

### NFR-006: Security - Data Privacy & GDPR

**Priority:** Must Have

**Description:**
GDPR compliance:
- **Data retention**: Delete creator data after 2 years (if inactive)
- **Right to be forgotten**: API to delete creator data on request
- **Data export**: API to export creator data (JSON format)
- **Audit logging**: Log all data access

**Acceptance Criteria:**
- [ ] Data retention policy implemented
- [ ] Delete API working
- [ ] Export API working
- [ ] Audit logs stored (retention 5 years)
- [ ] GDPR compliance checklist completed

**Rationale:**
Legal requirement. Avoid fines (up to 4% revenue).

---

### NFR-007: Reliability - Uptime SLA

**Priority:** Must Have

**Description:**
System uptime target: **99.5%** monthly
- Allowed downtime: 3.6 hours/month
- Planned maintenance: Max 2 hours/month (announced 1 week advance)
- Unplanned downtime: <1.6 hours/month

Uptime calculation excludes:
- Scheduled maintenance (with notice)
- Upstream service outages (TikTok API, Facebook API)

**Acceptance Criteria:**
- [ ] Uptime monitoring active (UptimeRobot)
- [ ] Monthly uptime report generated
- [ ] SLA met for 3 consecutive months
- [ ] Incident response time <15 min

**Rationale:**
Downtime = lost revenue. Campaigns cannot pause midway.

---

### NFR-008: Reliability - Disaster Recovery

**Priority:** Must Have

**Description:**
Disaster recovery targets:
- **RTO (Recovery Time Objective)**: 1 hour
  - Within 1 hour, system back online
- **RPO (Recovery Point Objective)**: 15 minutes
  - Max 15 minutes data loss acceptable

Disaster recovery plan tested:
- Monthly restore drill
- Failover to backup region (optional)

**Acceptance Criteria:**
- [ ] DR plan documented
- [ ] Restore tested monthly (passed)
- [ ] RTO met in tests (<1 hour)
- [ ] RPO met (backups every 15 min)

**Rationale:**
Catastrophic failures (data center fire) must be recoverable.

---

### NFR-009: Usability - Browser Support

**Priority:** Must Have

**Description:**
Frontend hỗ trợ browsers:
- Chrome 100+ (primary)
- Firefox 100+
- Safari 15+
- Edge 100+

Mobile browsers:
- iOS Safari 15+
- Chrome Android 100+

**Acceptance Criteria:**
- [ ] Cross-browser testing passed
- [ ] Responsive design working (mobile, tablet, desktop)
- [ ] No major visual bugs

**Rationale:**
Admins dùng different devices. Must work everywhere.

---

### NFR-010: Usability - Accessibility (WCAG 2.1 Level AA)

**Priority:** Should Have

**Description:**
Accessibility requirements:
- Keyboard navigation (no mouse required)
- Screen reader support (ARIA labels)
- Color contrast ratio >4.5:1
- Alt text for images
- Focus indicators visible

**Acceptance Criteria:**
- [ ] WCAG 2.1 AA audit passed
- [ ] Automated testing (axe-core)
- [ ] Manual testing with screen reader

**Rationale:**
Inclusive design. Support users with disabilities.

---

### NFR-011: Maintainability - Code Quality

**Priority:** Must Have

**Description:**
Code quality standards:
- **Test coverage**: >80% (unit + integration)
- **Code review**: All PRs require 1 approval
- **Linting**: ESLint (frontend), golangci-lint (backend)
- **Code complexity**: Cyclomatic complexity <10

**Acceptance Criteria:**
- [ ] Test coverage >80%
- [ ] CI enforces linting
- [ ] Code review process documented
- [ ] Complexity checks pass

**Rationale:**
High-quality code = fewer bugs, easier maintenance.

---

### NFR-012: Maintainability - Documentation

**Priority:** Must Have

**Description:**
Documentation requirements:
- **API documentation**: OpenAPI/Swagger (auto-generated)
- **Architecture diagram**: System components, data flow
- **Deployment guide**: Step-by-step production deployment
- **User guide**: How to use task management (screenshots)
- **Runbooks**: Operational procedures

**Acceptance Criteria:**
- [ ] All 5 docs types complete
- [ ] Docs reviewed & approved
- [ ] Docs published & accessible
- [ ] Docs updated within 1 week of changes

**Rationale:**
Good docs = faster onboarding, less support burden.

---

## Epics

Epics are logical groupings of related functionality that will be broken down into user stories during sprint planning (Phase 4).

Each epic maps to multiple functional requirements and will generate 2-10 stories.

---

### EPIC-001: Task Queue & Assignment System

**Description:**
Core task management foundation - create, assign, track, complete tasks với intelligent auto-assignment và status workflows.

**Functional Requirements:**
- FR-001: Task Domain Model
- FR-002: Task State Machine
- FR-003: Task CRUD API
- FR-004: Auto-Assignment Algorithm
- FR-005: My Tasks Dashboard
- FR-006: Manual Task Creation

**Story Count Estimate:** 8-10 stories

**Priority:** Must Have

**Business Value:**
Foundation cho toàn bộ system. Không có task management = không có automation.

**Implementation:** Week 1-4 (Phase 1)

---

### EPIC-002: SLA Tracking & Escalation

**Description:**
Track task deadlines, warn before breach, escalate overdue tasks, report SLA compliance metrics.

**Functional Requirements:**
- FR-007: SLA Configuration per Task Type
- FR-008: SLA Monitoring Background Job
- FR-009: SLA Escalation Workflow
- FR-010: SLA Dashboard & Reports

**Story Count Estimate:** 5-7 stories

**Priority:** Must Have

**Business Value:**
SLA compliance >85% là key success metric. Without tracking, no accountability.

**Implementation:** Week 3-6 (Phase 1-2)

---

### EPIC-003: Notification System

**Description:**
Multi-channel notifications (Telegram, Email, In-app) với inline actions, preferences, real-time delivery.

**Functional Requirements:**
- FR-011: Multi-Channel Notification Delivery
- FR-012: Telegram Bot Inline Actions
- FR-013: In-App Notification Center
- FR-014: Notification Preferences

**Story Count Estimate:** 6-8 stories

**Priority:** Must Have

**Business Value:**
Notifications = awareness. Without notifications, admins không biết có tasks → delays.

**Implementation:** Week 3-4 (Phase 1)

---

### EPIC-004: Workflow Orchestration Engine

**Description:**
Auto-create tasks from business events, support parallel execution, conditional routing, workflow templates.

**Functional Requirements:**
- FR-015: Auto-Task Creation from Business Events
- FR-016: Parallel Workflow Execution
- FR-017: Conditional Workflow Routing
- FR-018: Workflow Templates

**Story Count Estimate:** 7-9 stories

**Priority:** Must Have

**Business Value:**
Workflow automation = 65% time reduction. Parallel execution = even faster.

**Implementation:** Week 5-11 (Phase 2-3)

---

### EPIC-005: Budget Tracking & Controls

**Description:**
Real-time budget dashboard, enforce budget limits, auto-pause on exhaustion, ML forecasting.

**Functional Requirements:**
- FR-019: Real-Time Budget Dashboard
- FR-020: Budget Control Enforcement
- FR-021: Auto-Pause Campaign on Budget Exhaustion
- FR-022: Budget Forecast ML Model

**Story Count Estimate:** 6-8 stories

**Priority:** Must Have

**Business Value:**
Prevent budget overrun (save 150M VND/year). Critical financial control.

**Implementation:** Week 1-10 (Parallel với other epics)

---

### EPIC-006: Fraud Detection System

**Description:**
Rule-based fraud detection, ML model, blacklist management để prevent fake engagement.

**Functional Requirements:**
- FR-023: Rule-Based Fraud Detection
- FR-024: ML-Based Fraud Detection
- FR-025: Blacklist Management

**Story Count Estimate:** 5-7 stories

**Priority:** Must Have (FR-023, FR-025), Could Have (FR-024)

**Business Value:**
Prevent fraud losses (save 100M VND/year). Protect brand reputation.

**Implementation:** Week 1-2 (basic), Week 11-12 (ML)

---

### EPIC-007: Auto-Reconciliation System

**Description:**
90% auto-reconciliation through URL matching, discrepancy detection, flagged item review dashboard.

**Functional Requirements:**
- FR-026: Auto-Match Submissions to Crawled Data
- FR-027: Flagged Items Review Dashboard
- FR-028: Reconciliation Audit Trail

**Story Count Estimate:** 5-7 stories

**Priority:** Must Have

**Business Value:**
Reconciliation time: 2-4 days → 0.5 days (-83%). Biggest time saver.

**Implementation:** Week 7-8 (Phase 2)

---

### EPIC-008: Monitoring, Alerting & Business Continuity

**Description:**
System health monitoring, alert rules, automated backups, disaster recovery, operational runbooks.

**Functional Requirements:**
- FR-029: System Health Dashboard
- FR-030: Alert Rules & Notifications
- FR-031: Automated Backup & Restore
- FR-032: Operational Runbooks

**Story Count Estimate:** 6-8 stories

**Priority:** Must Have

**Business Value:**
Prevent downtime (save 50K/year). Ensure business continuity.

**Implementation:** Week 1-4 (foundational), ongoing (runbooks)

---

## User Stories (High-Level)

User stories follow the format: "As a [user type], I want [goal] so that [benefit]."

These are preliminary stories. Detailed stories will be created in Phase 4 (Sprint Planning).

---

### EPIC-001: Task Queue & Assignment

**Story 1.1:** As an admin, I want tasks to auto-create when content is submitted, so I don't have to manually track submissions.

**Story 1.2:** As a reviewer, I want tasks auto-assigned to me based on my availability, so I have balanced workload.

**Story 1.3:** As a reviewer, I want to see "My Tasks" dashboard sorted by priority, so I work on urgent items first.

**Story 1.4:** As an admin, I want to manually create tasks for ad-hoc work, so I can track non-automated workflows.

---

### EPIC-002: SLA Tracking

**Story 2.1:** As a reviewer, I want to receive warnings 24h before task deadline, so I don't miss SLAs.

**Story 2.2:** As a manager, I want to see SLA compliance dashboard, so I can track team performance.

**Story 2.3:** As an admin, I want overdue tasks auto-escalated to managers, so blockers get resolved quickly.

---

### EPIC-003: Notifications

**Story 3.1:** As a reviewer, I want Telegram notifications with inline buttons, so I can approve tasks without opening admin portal.

**Story 3.2:** As an admin, I want in-app notification center, so I see all updates in one place.

**Story 3.3:** As a user, I want to configure notification preferences, so I only get alerts I care about.

---

### EPIC-004: Workflow Orchestration

**Story 4.1:** As a system, I want to auto-create review tasks when content submitted, so reviewers know what to work on.

**Story 4.2:** As a campaign manager, I want parallel task execution, so setup and review happen simultaneously.

**Story 4.3:** As an admin, I want workflow templates for common scenarios, so I can reuse proven processes.

---

### EPIC-005: Budget Tracking

**Story 5.1:** As a finance manager, I want real-time budget dashboard, so I know campaign spend status.

**Story 5.2:** As a system, I want to block content approval if budget exceeded, so we don't overspend.

**Story 5.3:** As a campaign manager, I want budget forecast alerts, so I can request budget increase early.

---

### EPIC-006: Fraud Detection

**Story 6.1:** As a reviewer, I want fraud flags displayed during review, so I can spot suspicious content.

**Story 6.2:** As an admin, I want to blacklist fraud creators, so they can't submit again.

**Story 6.3:** As a system, I want ML fraud detection, so I catch sophisticated fraud patterns.

---

### EPIC-007: Auto-Reconciliation

**Story 7.1:** As a reconciliation admin, I want 90% auto-matching, so I only review exceptions.

**Story 7.2:** As an admin, I want flagged items dashboard, so I focus on discrepancies.

**Story 7.3:** As a compliance officer, I want reconciliation audit trail, so I can verify decisions.

---

### EPIC-008: Monitoring & BC

**Story 8.1:** As an ops engineer, I want system health dashboard, so I know if services are down.

**Story 8.2:** As an on-call engineer, I want critical alerts via PagerDuty, so I respond to outages immediately.

**Story 8.3:** As a business owner, I want automated backups tested monthly, so I trust disaster recovery.

---

## User Personas

### Persona 1: Content Reviewer (Primary User)

**Name:** Nguyễn Thị Lan
**Role:** Content Reviewer (AT Operation Team)
**Age:** 25
**Experience:** 1 year reviewing creator content

**Goals:**
- Review content quickly & accurately
- Meet SLA deadlines (48h)
- Avoid missing tasks
- Balance workload

**Pain Points (Current):**
- Doesn't know what needs review (phải tự check UI)
- No prioritization (treats all tasks equally)
- Manual reconciliation takes 2-4 days (boring, error-prone)
- Overdue tasks không ai notice → Stakeholder complaints

**Needs from System:**
- Auto-assigned tasks (balanced workload)
- Clear priority indicators (urgent first)
- Notifications (Telegram, Email)
- Quick actions (approve/reject from notification)
- SLA warnings (don't miss deadlines)

---

### Persona 2: Campaign Manager (Admin)

**Name:** Trần Văn Minh
**Role:** Campaign Manager (AT Team)
**Age:** 30
**Experience:** 3 years managing influencer campaigns

**Goals:**
- Launch campaigns quickly
- Track campaign progress
- Ensure budget compliance
- Report to stakeholders

**Pain Points (Current):**
- Campaign setup manual (2 days)
- No visibility into task status (ai đang làm gì?)
- Budget tracking manual (Excel spreadsheets)
- Risk of budget overrun (no alerts)
- Reporting manual (copy-paste từ nhiều sources)

**Needs from System:**
- Auto-task creation (campaign launched → Tasks created)
- Real-time dashboard (campaign progress)
- Budget tracking (know spend status)
- Budget alerts (prevent overrun)
- 1-click reporting (PDF export)

---

### Persona 3: Finance Manager (Stakeholder)

**Name:** Lê Thị Hương
**Role:** Finance Manager (Techcombank)
**Age:** 35
**Experience:** 5 years financial operations

**Goals:**
- Control campaign budgets
- Prevent overspend
- Ensure payment accuracy
- Audit reconciliation

**Pain Points (Current):**
- No real-time budget visibility
- Discover budget overrun too late (after campaign ends)
- Reconciliation errors (manual mistakes)
- Audit trail incomplete

**Needs from System:**
- Real-time budget dashboard
- Budget alerts (80%, 95%, 100%)
- Auto-pause on budget exhaustion
- Reconciliation audit trail
- Financial reports (Excel export)

---

### Persona 4: On-Call Engineer (Operations)

**Name:** Phạm Văn Hùng
**Role:** DevOps Engineer
**Age:** 28
**Experience:** 2 years system operations

**Goals:**
- Maintain system uptime (99.5%)
- Respond to incidents quickly
- Prevent data loss
- Minimize downtime

**Pain Points (Current):**
- No monitoring dashboard (manual checks)
- Discover outages từ user complaints (too late)
- No runbooks (guess solutions)
- Backup restore untested (risky)

**Needs from System:**
- System health dashboard
- Critical alerts (PagerDuty)
- Automated backups (tested monthly)
- Runbooks (step-by-step recovery)
- Incident tracking

---

## Key User Flows

### User Flow 1: Content Review (Happy Path)

**Actors:** Creator, System, Reviewer

**Steps:**
1. **Creator submits content** (TikTok URL) via Creator Portal
2. **System auto-creates review task**
   - Type: content_review
   - Auto-assign to least-loaded reviewer (Lan)
   - Due: created_at + 48h
3. **System sends Telegram notification** to Lan
   - Message: "Bạn có 1 task mới: Review Content #123"
   - Buttons: [✅ Approve] [❌ Reject] [👀 View]
4. **Lan clicks [👀 View]** → Opens task detail page
5. **Lan reviews content** (video quality, brand guidelines)
6. **Fraud check runs** automatically
   - Rule-based: No flags
   - Decision: Safe to approve
7. **Budget check runs** automatically
   - Current spend + reward <= Campaign budget ✅
8. **Lan clicks [✅ Approve]**
9. **System transitions status** (in_progress → completed)
10. **System creates EventReward** record
11. **System sends notification** to creator: "Content approved!"
12. **Task completed**, SLA met

**Expected Duration:** 30 minutes (vs 2-3 days currently)

---

### User Flow 2: Budget Overrun Prevention

**Actors:** Campaign Manager (Minh), System, Finance Manager (Hương)

**Steps:**
1. **Campaign running**, budget 80% utilized
2. **System sends warning alert** to Minh & Hương
   - Telegram: "🟡 Campaign #456 budget 80% utilized"
   - Email: Budget summary
3. **Minh reviews budget dashboard**
   - Allocated: 500M
   - Committed: 400M (80%)
   - Forecast: 480M (within budget) ✅
4. **Campaign continues**, budget reaches 95%
5. **System sends critical alert**
   - Telegram: "🔴 Campaign #456 budget 95% utilized"
6. **Minh checks forecast**: 520M (exceeds budget by 20M)
7. **Minh requests budget increase** (manual process)
8. **Hương approves +50M** → Budget now 550M
9. **Campaign continues**, reaches 100% of original budget (500M)
10. **System auto-pauses campaign** (PAUSED_BUDGET_EXHAUSTED)
11. **Minh manually resumes** với new budget (550M)
12. **Campaign completes** at 520M (within new budget) ✅

**Outcome:** Budget overrun prevented, stakeholders informed early.

---

### User Flow 3: Fraud Detection & Blacklist

**Actors:** Creator (Fraudster), System, Reviewer (Lan)

**Steps:**
1. **Creator submits content** (suspicious high views)
2. **System auto-creates review task**
3. **Fraud detection runs** automatically
   - Rule 1: views_per_hour = 150,000 (threshold: 100K) → Flag "SUSPICIOUS_VIEW_VELOCITY" 🚩
   - Rule 2: engagement_rate = 0.2% (threshold: 0.5%) → Flag "LOW_ENGAGEMENT_RATE" 🚩
   - Rule 3: account_age = 15 days (threshold: 30 days) → Flag "NEW_ACCOUNT" 🚩
   - **Total flags: 3** → Risk score: HIGH
4. **System recommendation**: Auto-reject
5. **Lan reviews task**, sees 3 red flags
6. **Lan investigates**: Checks creator profile, spots bot followers
7. **Lan confirms fraud**, clicks [❌ Reject]
8. **Lan adds creator to blacklist**
   - Reason: "Fake views + bot followers"
   - Ban type: Permanent
9. **System blocks future submissions** from this creator
10. **System sends notification** to creator: "Content rejected (policy violation)"
11. **Creator attempts to submit again** (new content)
12. **System auto-blocks** với message: "You are blacklisted"

**Outcome:** Fraud detected, creator blacklisted, prevented loss (~5M VND).

---

## Dependencies

### Internal Dependencies

**Existing TCB Systems:**
- **Content Management System**: Task system integrates via API hooks
- **MongoDB Replica Set**: Task data stored here
- **Redis Queue (Asynq)**: Background jobs for notifications, SLA monitoring
- **Firebase**: Push notifications
- **SendGrid**: Email notifications
- **Telegram Bot API**: Inline action notifications
- **Content Catcher API**: Crawled metrics for reconciliation
- **TikTok/Facebook APIs**: Social platform data

**Assumptions:**
- All existing systems remain stable
- APIs well-documented & accessible
- Database performance adequate for task volume

---

### External Dependencies

**Third-Party Services:**
- **Telegram Bot API**: For inline notifications (Free, 99.9% uptime)
- **SendGrid**: Email delivery (100K emails/month, $20/month)
- **Monitoring (Sentry)**: Error tracking (Free tier sufficient)
- **Cloud Storage (S3)**: Backup storage ($5/month)

**Risks:**
- Telegram API rate limits (30 msg/sec) → Batch notifications
- SendGrid quota exceeded → Upgrade plan
- S3 outage → Backups delayed

---

## Assumptions

1. **Team Availability**
   - 1 Backend engineer (Go) full-time for 12 weeks
   - 1 Frontend engineer (React) full-time for 12 weeks
   - Product owner available for decisions (4h/week)

2. **Technical Environment**
   - MongoDB replica set already configured
   - Redis already running
   - Development environment setup complete
   - Access to production infrastructure

3. **Business Commitment**
   - Stakeholders approve $31.2K budget
   - Team committed to 12-week timeline
   - Pilot campaign available for testing (Week 8)
   - Training sessions scheduled (Week 12)

4. **Data Quality**
   - Historical campaign data available (for ML training)
   - Fraud labels available (for fraud detection training)
   - Content Catcher API reliable (>99% uptime)

5. **Regulatory**
   - GDPR compliance requirements understood
   - Legal team reviewed data retention policy
   - No additional compliance requirements

---

## Out of Scope

**Explicitly NOT included in this project:**

1. **Creator Portal Redesign**
   - Creator portal remains as-is
   - Only backend integrations affected

2. **Payment Processing System**
   - Payment workflows remain manual
   - Future phase: Automate payment batching

3. **CRM System for Creators**
   - Creator segmentation (Platinum/Gold/Silver) deferred
   - Future phase: Full CRM implementation

4. **Advanced Analytics & BI**
   - Basic dashboards only
   - Advanced analytics (cohort analysis, etc.) deferred

5. **Mobile Native Apps**
   - Web-based only (responsive design)
   - Native iOS/Android apps deferred

6. **Multi-Language Support**
   - Vietnamese only
   - Internationalization (i18n) deferred

7. **White-Label Platform**
   - TCB-specific only
   - Multi-tenant platform deferred

8. **Blockchain/NFT Integration**
   - Not relevant for this use case

---

## Open Questions

**Questions needing stakeholder input:**

1. **Budget Approval Workflow**
   - Q: Who approves budget increases >20%? (Finance Manager? CFO?)
   - Impact: Affects FR-020 implementation
   - Decision needed by: Week 2

2. **Fraud Detection Thresholds**
   - Q: What's acceptable false positive rate? (5%? 10%?)
   - Impact: Affects ML model tuning
   - Decision needed by: Week 10

3. **SLA Escalation Rules**
   - Q: Escalate after how many hours breach? (24h? 48h?)
   - Impact: Affects FR-009 logic
   - Decision needed by: Week 4

4. **Blacklist Sharing**
   - Q: Share blacklist with other brands (VPBank, VIB)?
   - Impact: Requires legal review, data sharing agreements
   - Decision needed by: Week 8

5. **Notification Volume**
   - Q: Max notifications per user per day? (To avoid spam)
   - Impact: Affects FR-014 digest mode logic
   - Decision needed by: Week 3

6. **Disaster Recovery Region**
   - Q: Deploy backup region (Singapore? Tokyo?)? (Cost: +$50/month)
   - Impact: Affects NFR-008 implementation
   - Decision needed by: Week 1

---

## Approval & Sign-off

### Stakeholders

**Product Owner:** [Name], AT Operations Lead
**Engineering Lead:** [Name], Backend Team Lead
**Finance Stakeholder:** [Name], TCB Finance Manager
**Legal/Compliance:** [Name], Legal Team
**QA Lead:** [Name], QA Team Lead

### Approval Status

- [ ] Product Owner: Approved requirements alignment với business goals
- [ ] Engineering Lead: Approved technical feasibility
- [ ] Finance: Approved budget ($31.2K)
- [ ] Legal: Approved data privacy & compliance approach
- [ ] QA Lead: Approved NFRs testable

**Target Approval Date:** 2026-02-10 (5 days)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-05 | Product Manager (BMAD) | Initial PRD based on gaps analysis |

---

## Next Steps

### Phase 3: Architecture

Run `/bmad:architecture` to create system architecture based on these requirements.

The architecture will address:
- All 32 functional requirements (FRs)
- All 12 non-functional requirements (NFRs)
- Technical stack decisions (workflow engine: n8n vs Temporal)
- Data models (MongoDB schemas, indexes)
- API design (RESTful endpoints)
- System components (Backend, Frontend, Workers, Monitoring)
- Integration points (existing TCB systems)
- Deployment architecture (infrastructure)

### Phase 4: Sprint Planning

After architecture is complete, run `/bmad:sprint-planning` to:
- Break 8 epics into detailed user stories (80-100 stories)
- Estimate story complexity (story points)
- Plan sprint iterations (12 weeks = 6 sprints)
- Assign stories to sprints
- Begin implementation

---

**This document was created using BMAD Method v6 - Phase 2 (Planning)**

*To continue: Run `/bmad:workflow-status` to see your progress and next recommended workflow.*

---

## Appendix A: Requirements Traceability Matrix

| Epic ID | Epic Name | Functional Requirements | Story Count (Est.) | Implementation Phase |
|---------|-----------|-------------------------|-------------------|----------------------|
| EPIC-001 | Task Queue & Assignment System | FR-001, FR-002, FR-003, FR-004, FR-005, FR-006 | 8-10 stories | Week 1-4 (Phase 1) |
| EPIC-002 | SLA Tracking & Escalation | FR-007, FR-008, FR-009, FR-010 | 5-7 stories | Week 3-6 (Phase 1-2) |
| EPIC-003 | Notification System | FR-011, FR-012, FR-013, FR-014 | 6-8 stories | Week 3-4 (Phase 1) |
| EPIC-004 | Workflow Orchestration Engine | FR-015, FR-016, FR-017, FR-018 | 7-9 stories | Week 5-11 (Phase 2-3) |
| EPIC-005 | Budget Tracking & Controls | FR-019, FR-020, FR-021, FR-022 | 6-8 stories | Week 1-10 (Parallel) |
| EPIC-006 | Fraud Detection System | FR-023, FR-024, FR-025 | 5-7 stories | Week 1-2, 11-12 |
| EPIC-007 | Auto-Reconciliation System | FR-026, FR-027, FR-028 | 5-7 stories | Week 7-8 (Phase 2) |
| EPIC-008 | Monitoring & Business Continuity | FR-029, FR-030, FR-031, FR-032 | 6-8 stories | Week 1-4, ongoing |
| **TOTALS** | **8 Epics** | **32 Functional Requirements** | **48-64 stories** | **12 weeks** |

---

## Appendix B: Prioritization Details

### Functional Requirements Breakdown

**Must Have (Critical for MVP):** 26 FRs
- EPIC-001: 6 FRs (Task management core)
- EPIC-002: 3 FRs (SLA tracking, exclude advanced reporting)
- EPIC-003: 3 FRs (Notifications, exclude preferences)
- EPIC-004: 2 FRs (Auto-task creation, parallel execution)
- EPIC-005: 3 FRs (Budget dashboard, controls, auto-pause)
- EPIC-006: 2 FRs (Rule-based fraud, blacklist)
- EPIC-007: 2 FRs (Auto-reconciliation, review dashboard)
- EPIC-008: 3 FRs (Health monitoring, alerts, backups)

**Should Have (High value, include if time permits):** 5 FRs
- FR-009: SLA Escalation Workflow
- FR-010: SLA Dashboard & Reports
- FR-014: Notification Preferences
- FR-017: Conditional Workflow Routing
- FR-018: Workflow Templates
- FR-028: Reconciliation Audit Trail

**Could Have (Nice to have, defer if needed):** 1 FR
- FR-024: ML-Based Fraud Detection (defer to Week 11-12)

**Won't Have (Out of scope):** 0 FRs
- All defined FRs are in scope

### Non-Functional Requirements Breakdown

**Must Have:** 10 NFRs
- NFR-001 to NFR-008 (Performance, Security, Reliability)
- NFR-011: Code Quality
- NFR-012: Documentation

**Should Have:** 2 NFRs
- NFR-004: Data Volume Scalability (test with 1M tasks)
- NFR-010: Accessibility (WCAG 2.1 AA)

**Could Have:** 0 NFRs

---

## Appendix C: Success Metrics Dashboard (Target State)

```
┌─────────────────────────────────────────────────────────────────┐
│          TASK MANAGEMENT SYSTEM - SUCCESS METRICS               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PRIMARY METRICS (Business Objectives)                         │
│  ══════════════════════════════════════                        │
│                                                                 │
│  Average Campaign Cycle Time:                                  │
│  Baseline: ████████████████ 12 days                           │
│  Current:  ████░░░░░░░░░░░ 4 days (-67%) ✅ Target: <5 days   │
│                                                                 │
│  Reconciliation Time:                                          │
│  Baseline: ████████████████ 3 days                            │
│  Current:  █░░░░░░░░░░░░░░ 0.4 days (-87%) ✅ Target: <4h    │
│                                                                 │
│  Admin Workload Reduction:                                     │
│  Baseline: ████████████████ 100% manual                       │
│  Current:  ████████░░░░░░░ 48% manual (-52%) ✅ Target: <50% │
│                                                                 │
│  SLA Compliance Rate:                                          │
│  Baseline: ░░░░░░░░░░░░░░░ Unknown                            │
│  Current:  ██████████████░ 87% ✅ Target: >85%                │
│                                                                 │
│  Auto-Reconciliation Match Rate:                               │
│  Baseline: ░░░░░░░░░░░░░░░ 0%                                 │
│  Current:  ██████████████░ 92% ✅ Target: >90%                │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  OPERATIONAL METRICS                                            │
│  ══════════════════                                             │
│                                                                 │
│  - Tasks stuck >48h: 3% ✅ (Target: <5%)                       │
│  - Notification response time: 1.2h ✅ (Target: <2h)           │
│  - Report generation time: 3 min ✅ (Target: <5 min)           │
│  - System uptime: 99.7% ✅ (Target: >99.5%)                    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  FINANCIAL IMPACT                                               │
│  ═════════════════                                              │
│                                                                 │
│  Annual Savings Realized:                                       │
│  - Time saved: $172,800 ✅                                     │
│  - Fraud prevention: $105,000 ✅                               │
│  - Budget control: $160,000 ✅                                 │
│  - Downtime prevention: $52,000 ✅                             │
│  ────────────────────────────────                              │
│  Total: $489,800/year                                          │
│                                                                 │
│  ROI: 1,570% ✅                                                 │
│  Payback: 0.8 months ✅                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

**END OF PRD**

**Document Status:** Draft - Ready for Stakeholder Review
**Next Action:** Schedule stakeholder review meeting (target: 2026-02-10)
**Questions?** Contact Product Manager or refer to gaps analysis document.
