# Sprint Plan: Task Management & Workflow Automation System

**Date:** 2026-02-05
**Scrum Master:** Vinh Nguyen
**Project:** Operation Optimization - Task Management System
**Project Level:** Level 4 (Complex, Multi-Epic)
**Total Stories:** 72 stories
**Total Points:** ~288 SP
**Planned Sprints:** 14 sprints (28 tuần)
**Team Size:** 1 senior full-stack developer
**Sprint Capacity:** 20 SP/sprint

---

## Executive Summary

Dự án Task Management & Workflow Automation System là một **Level 4 project** với 8 epics lớn và 32 functional requirements. Với **1 senior full-stack developer**, timeline realistic là **28 tuần (7 tháng)** thay vì 18 tuần như ban đầu estimate.

**Key Adjustments:**
- ✅ **Notification Module First** (Sprint 0-1): Build standalone module, reusable cho 4 projects
- ✅ **Must Have Priority**: Focus vào 26 Must Have FRs trước
- ✅ **Phased Delivery**: MVP sau Sprint 7 (14 tuần), advanced features sau đó
- ✅ **Realistic Capacity**: 20 SP/sprint (1 senior dev, với buffer)

**Success Metrics:**
- Campaign cycle time: 10-16 days → 3-5 days (-65%)
- Reconciliation time: 2-4 days → 0.5 days (-83%)
- Admin workload: 100% manual → 50% manual (-50%)
- SLA compliance: Unknown → >85%
- Auto-match rate: 0% → >90%

---

## Team Capacity Analysis

### Team Configuration
- **Size:** 1 senior full-stack developer
- **Skills:** Go, React, MongoDB, Redis (expert level)
- **Sprint Length:** 2 tuần
- **Work Days:** 10 days/sprint
- **Productive Hours:** 6 hours/day (senior efficiency)

### Capacity Calculation
```
Total hours per sprint: 1 dev × 10 days × 6 hours = 60 hours
Senior velocity: 1 SP = 2-3 hours (average: 2.5h)
Raw capacity: 60h ÷ 2.5h = 24 SP/sprint

With 20% buffer (meetings, unknowns, bugs):
Safe capacity: 24 SP × 0.8 = ~20 SP/sprint
```

### Timeline Analysis
```
Total Story Points: ~288 SP
Capacity per sprint: 20 SP
Required sprints: 288 ÷ 20 = 14.4 sprints
Total weeks: 14 sprints × 2 weeks = 28 tuần (~7 tháng)
```

---

## Sprint Overview - TÓM TẮT

| Sprint | Weeks | Goal | Stories | SP | Cumulative SP |
|--------|-------|------|---------|----|--------------|
| **Sprint 0** | 1-2 | Notification Module (Standalone) | 5 | 20 | 20 |
| **Sprint 1** | 3-4 | Task Engine Core + Infra | 5 | 20 | 40 |
| **Sprint 2** | 5-6 | Task UI + Auto-Assignment | 5 | 20 | 60 |
| **Sprint 3** | 7-8 | SLA Tracking + Auto-Tasks | 5 | 20 | 80 |
| **Sprint 4** | 9-10 | Workflow Engine Foundation | 5 | 20 | 100 |
| **Sprint 5** | 11-12 | Budget Tracking + Controls | 5 | 20 | 120 |
| **Sprint 6** | 13-14 | Auto-Reconciliation System | 5 | 20 | 140 |
| **Sprint 7** | 15-16 | **MVP Integration + Testing** | 4 | 16 | 156 |
| **Sprint 8** | 17-18 | Fraud Detection (Rule-Based) | 5 | 20 | 176 |
| **Sprint 9** | 19-20 | Parallel Workflows + Templates | 5 | 20 | 196 |
| **Sprint 10** | 21-22 | Advanced Notifications + Preferences | 4 | 16 | 212 |
| **Sprint 11** | 23-24 | ML Models (Budget + Fraud) | 5 | 20 | 232 |
| **Sprint 12** | 25-26 | Monitoring + Alerting + Backups | 5 | 20 | 252 |
| **Sprint 13** | 27-28 | Documentation + UAT + Launch | 5 | 20 | 272 |
| **Sprint 14** | 29-30 | **Production Launch + Stabilization** | 4 | 16 | 288 |

**MVP Ready:** End of Sprint 7 (16 tuần)
**Full Launch:** End of Sprint 14 (30 tuần)

---

## Story Inventory - TẤT CẢ STORIES CHI TIẾT

### EPIC-003: Notification System (Module Độc Lập)

#### STORY-NOT-001: Notification Domain Model & Repository (Infrastructure)
**Priority:** Must Have
**Points:** 5
**Sprint:** Sprint 0

**User Story:**
As a system architect, I want a notification domain model với repository pattern, so that notification system có thể lưu trữ và query notifications efficiently.

**Acceptance Criteria:**
- [ ] Notification entity defined với fields: id, type, channel, recipient_id, content, status, sent_at, delivered_at, read_at, metadata
- [ ] NotificationPreferences entity: user_id, channels_enabled (telegram, email, inapp), event_types, quiet_hours, digest_mode
- [ ] NotificationRepository interface defined với methods: Create, FindByRecipient, MarkAsDelivered, MarkAsRead, CountUnread
- [ ] MongoDB implementation của repository
- [ ] Indexes created: recipient_id + status, sent_at, type
- [ ] Unit tests >80% coverage

**Technical Notes:**
- Location: `accesstrade-projects/shared-modules/notification-system/domain/`
- Database: MongoDB collection `notifications`, `notification_preferences`
- Indexes: Compound index (recipient_id, status, sent_at)

**Dependencies:** None

---

#### STORY-NOT-002: Telegram Bot Integration với Inline Buttons
**Priority:** Must Have
**Points:** 5
**Sprint:** Sprint 0

**User Story:**
As a reviewer, I want to receive Telegram notifications với inline buttons, so I can approve/reject tasks without opening admin portal.

**Acceptance Criteria:**
- [ ] Telegram Bot API integration working (send message, edit message)
- [ ] Inline keyboard buttons rendering correctly
- [ ] Button callbacks handled securely (verify callback authenticity)
- [ ] Message templates for 5 notification types (task assigned, due soon, overdue, completed, mention)
- [ ] Rate limiting implemented (30 messages/sec limit)
- [ ] Retry logic (3 attempts với exponential backoff)
- [ ] Error handling (bot blocked, invalid chat_id)
- [ ] Unit tests + integration tests với mock Telegram API

**Technical Notes:**
- Library: `github.com/go-telegram-bot-api/telegram-bot-api/v5`
- Bot token: Store in env var `TELEGRAM_BOT_TOKEN`
- Callback data format: `action:task_id:user_id`
- Security: Verify callback từ Telegram server (check secret token)

**Dependencies:** STORY-NOT-001

---

#### STORY-NOT-003: SendGrid Email Integration với Templates
**Priority:** Must Have
**Points:** 3
**Sprint:** Sprint 0

**User Story:**
As a user, I want to receive email notifications với professional templates, so I have detailed context và can review later.

**Acceptance Criteria:**
- [ ] SendGrid API integration working
- [ ] 5 email templates created (task assigned, due soon, overdue, completed, digest)
- [ ] HTML email templates responsive (desktop + mobile)
- [ ] Template variables working (task title, due date, assignee name, etc.)
- [ ] Delivery tracking (sent, delivered, bounced, opened)
- [ ] Retry logic (3 attempts)
- [ ] Error handling (invalid email, SendGrid quota exceeded)
- [ ] Integration tests với SendGrid sandbox

**Technical Notes:**
- Library: `github.com/sendgrid/sendgrid-go`
- API key: Store in env var `SENDGRID_API_KEY`
- Templates: Store in `templates/email/*.html`
- From email: `noreply@accesstrade.vn`

**Dependencies:** STORY-NOT-001

---

#### STORY-NOT-004: WebSocket In-App Notifications
**Priority:** Must Have
**Points:** 5
**Sprint:** Sprint 0

**User Story:**
As an admin, I want real-time in-app notifications, so I see updates immediately without refreshing page.

**Acceptance Criteria:**
- [ ] WebSocket server setup (Socket.io)
- [ ] Client connection authentication (JWT token)
- [ ] Real-time notification delivery (broadcast to specific user)
- [ ] Notification center UI component (dropdown bell icon)
- [ ] Unread count badge accurate
- [ ] Mark as read functionality
- [ ] Notification click → Navigate to task detail
- [ ] Persist to database (notifications collection)
- [ ] Handle reconnection automatically
- [ ] Load last 20 notifications on mount

**Technical Notes:**
- Backend: `github.com/googollee/go-socket.io`
- Frontend: `socket.io-client`
- Event names: `notification:new`, `notification:read`, `notification:count`
- Authentication: Verify JWT token on connection

**Dependencies:** STORY-NOT-001

---

#### STORY-NOT-005: Notification Service API + Testing
**Priority:** Must Have
**Points:** 2
**Sprint:** Sprint 0

**User Story:**
As a developer, I want a simple notification service API, so I can send notifications từ bất kỳ module nào without knowing implementation details.

**Acceptance Criteria:**
- [ ] NotificationService interface defined: Send(event NotificationEvent) error
- [ ] Implementation routes to correct channel (Telegram, Email, WebSocket)
- [ ] Respects user preferences (channels enabled, quiet hours)
- [ ] Delivery status tracking (sent, delivered, failed)
- [ ] Retry logic for failed deliveries
- [ ] Logging all notification events
- [ ] Standalone README với usage examples
- [ ] Unit tests (mock all channels) >90% coverage
- [ ] Integration tests với real channels (staging only)

**Technical Notes:**
- Location: `accesstrade-projects/shared-modules/notification-system/service/`
- Usage example:
  ```go
  notifier.Send(notification.Event{
      Type:      "task.assigned",
      Recipient: userID,
      Data:      map[string]interface{}{"task_id": taskID},
  })
  ```

**Dependencies:** STORY-NOT-002, STORY-NOT-003, STORY-NOT-004

---

### EPIC-001: Task Queue & Assignment System

#### STORY-TASK-001: Development Environment + Infrastructure Setup
**Priority:** Must Have
**Points:** 5
**Sprint:** Sprint 1

**User Story:**
As a developer, I want development environment fully configured, so I can start implementing features immediately.

**Acceptance Criteria:**
- [ ] Docker Compose file với MongoDB, Redis, API server
- [ ] MongoDB replica set configured (3 nodes)
- [ ] Redis configured (master + replica)
- [ ] Environment variables setup (.env.example)
- [ ] Database migration scripts (up/down)
- [ ] Seed data script (test users, sample tasks)
- [ ] Makefile với common commands (docker-up, docker-down, migrate, seed)
- [ ] CI/CD pipeline (GitHub Actions): build, test, lint
- [ ] Pre-commit hooks (go fmt, eslint, tests)
- [ ] README with setup instructions

**Technical Notes:**
- Docker Compose: `docker-compose.yml`
- MongoDB: Port 27017, database `taskengine_dev`
- Redis: Port 6379
- API server: Port 8080

**Dependencies:** None

---

#### STORY-TASK-002: Authentication & Authorization (JWT + RBAC)
**Priority:** Must Have
**Points:** 5
**Sprint:** Sprint 1

**User Story:**
As a system, I want secure authentication và role-based authorization, so only authorized users can access resources.

**Acceptance Criteria:**
- [ ] JWT authentication implemented (RS256 signing)
- [ ] Login endpoint: POST /api/v1/auth/login (return JWT token)
- [ ] Token expiry: 24 hours
- [ ] Refresh token mechanism (optional, nice to have)
- [ ] RBAC middleware: Check user role before API calls
- [ ] Roles defined: Admin (full access), Reviewer (assigned tasks only), Creator (read-only)
- [ ] Unauthorized requests return 401/403
- [ ] HTTPS enforced (HTTPS-only cookies)
- [ ] Unit tests for auth logic >85%

**Technical Notes:**
- Library: `github.com/golang-jwt/jwt/v5`
- Private key: Store in `keys/jwt_private.pem`
- Public key: Store in `keys/jwt_public.pem`
- Middleware: Check `Authorization: Bearer <token>` header

**Dependencies:** STORY-TASK-001

---

#### STORY-TASK-003: Task Domain Model + State Machine
**Priority:** Must Have
**Points:** 3
**Sprint:** Sprint 1

**User Story:**
As a system, I want a robust task domain model với state machine, so task transitions are validated và tracked.

**Acceptance Criteria:**
- [ ] Task entity với 15+ fields (id, title, type, status, priority, assigned_to, dates, SLA, metadata, status_history)
- [ ] State machine defined với valid transitions:
  - draft → assigned
  - assigned → in_progress, cancelled
  - in_progress → completed, blocked, cancelled
  - blocked → in_progress
  - completed, cancelled (terminal states)
- [ ] Invalid transitions rejected with error
- [ ] Status history tracked automatically (from, to, changed_by, changed_at, reason)
- [ ] Validation rules enforced (due_date > created_at, assigned_to required if status=assigned)
- [ ] Unit tests cover all transitions >90%

**Technical Notes:**
- Location: `pkg/taskengine/domain/task.go`
- State machine: Use `github.com/looplab/fsm` or custom implementation
- Status history: Array field in MongoDB document

**Dependencies:** STORY-TASK-001

---

#### STORY-TASK-004: Task Repository + MongoDB Implementation
**Priority:** Must Have
**Points:** 3
**Sprint:** Sprint 1

**User Story:**
As a backend system, I want a task repository với MongoDB implementation, so I can store và query tasks efficiently.

**Acceptance Criteria:**
- [ ] TaskRepository interface defined: Create, FindByID, FindByFilters, Update, Delete, CountByStatus
- [ ] MongoDB implementation với 8 strategic indexes
- [ ] Pagination support (cursor-based, limit 50 items/page)
- [ ] Filter support: status (multiple), assigned_to, type, priority, due_date range
- [ ] Sort support: due_date, priority, created_at (asc/desc)
- [ ] Query performance <50ms for list queries
- [ ] Unit tests with in-memory repository >80%
- [ ] Integration tests with real MongoDB >70%

**Technical Notes:**
- Location: `pkg/taskengine/adapters/storage/mongodb/`
- Collection: `tasks`
- Indexes: See architecture doc (8 indexes)

**Dependencies:** STORY-TASK-003

---

#### STORY-TASK-005: Task CRUD API (RESTful Endpoints)
**Priority:** Must Have
**Points:** 4
**Sprint:** Sprint 1

**User Story:**
As a frontend developer, I want RESTful API endpoints để manage tasks, so I can build UI features.

**Acceptance Criteria:**
- [ ] POST /api/v1/tasks - Create task
- [ ] GET /api/v1/tasks - List tasks với filters, pagination, sort
- [ ] GET /api/v1/tasks/{id} - Get task detail
- [ ] PATCH /api/v1/tasks/{id} - Update task fields
- [ ] PATCH /api/v1/tasks/{id}/status - Transition status (với reason)
- [ ] DELETE /api/v1/tasks/{id} - Soft delete (set cancelled)
- [ ] All endpoints return JSON responses
- [ ] Error handling: 400 (validation), 401 (unauthorized), 404 (not found), 500 (server error)
- [ ] OpenAPI/Swagger documentation auto-generated
- [ ] Integration tests cover all endpoints >80%

**Technical Notes:**
- Framework: Gin
- Validation: `github.com/go-playground/validator`
- Swagger: `github.com/swaggo/gin-swagger`

**Dependencies:** STORY-TASK-004, STORY-TASK-002

---

#### STORY-TASK-006: Auto-Assignment Algorithm (Least-Loaded)
**Priority:** Must Have
**Points:** 5
**Sprint:** Sprint 2

**User Story:**
As a system, I want tasks auto-assigned to least-loaded reviewers, so workload is balanced across team.

**Acceptance Criteria:**
- [ ] Algorithm implemented:
  1. Get eligible reviewers for task type (skill matching)
  2. Count active tasks (status = assigned | in_progress) for each reviewer
  3. Filter out unavailable reviewers (on_leave, busy status)
  4. Assign to reviewer with lowest active count
  5. If tie → Round-robin based on last assignment time
- [ ] Can manually override auto-assignment
- [ ] Assignment logged in task history
- [ ] Notification sent to assigned reviewer
- [ ] Unit tests cover algorithm >90%
- [ ] Integration tests verify assignment logic

**Technical Notes:**
- Location: `pkg/taskengine/services/assignment_service.go`
- Reviewer availability: Check `users.status` field
- Skill matching: Map task type → reviewer roles (configurable)

**Dependencies:** STORY-TASK-005

---

#### STORY-TASK-007: My Tasks Dashboard (Frontend - List View)
**Priority:** Must Have
**Points:** 5
**Sprint:** Sprint 2

**User Story:**
As a reviewer, I want to see "My Tasks" dashboard sorted by priority, so I work on urgent items first.

**Acceptance Criteria:**
- [ ] Dashboard page `/tasks` với task list table
- [ ] Columns: Title, Type, Priority, Due Date, Status, Actions
- [ ] Filters working: Status (Assigned, In Progress, Completed), Type, Priority
- [ ] Sort working: Priority (urgent first), Due Date (soonest first)
- [ ] Visual priority indicators:
  - 🔴 Red badge: Overdue tasks
  - 🟡 Yellow badge: Due soon (<24h)
  - 🟢 Green: Normal
- [ ] Quick actions: Start Task, Complete Task, Escalate
- [ ] Click row → Navigate to task detail page
- [ ] Pagination working (50 items/page)
- [ ] Loading states + empty states
- [ ] Responsive design (desktop + mobile)

**Technical Notes:**
- Framework: React 18 + TypeScript
- UI library: shadcn/ui (Table, Badge, Button components)
- API client: TanStack Query (react-query)
- Routing: React Router v6

**Dependencies:** STORY-TASK-005

---

#### STORY-TASK-008: Task Detail Page (Frontend)
**Priority:** Must Have
**Points:** 3
**Sprint:** Sprint 2

**User Story:**
As a reviewer, I want to see full task details với context, so I can review và make informed decisions.

**Acceptance Criteria:**
- [ ] Task detail page `/tasks/:id`
- [ ] Display all task fields: title, description, type, priority, status, dates, assigned user
- [ ] Show metadata (content link, campaign info, creator info)
- [ ] Show status history timeline (who changed, when, why)
- [ ] Action buttons based on status:
  - draft → Assign button
  - assigned → Start Task button
  - in_progress → Complete, Block, Escalate buttons
  - blocked → Resume button
- [ ] Confirmation dialogs for critical actions (complete, reject)
- [ ] Loading state, error state
- [ ] Breadcrumb navigation (Dashboard > Tasks > Detail)

**Technical Notes:**
- Use shadcn/ui: Card, Timeline, Dialog components
- API call: GET /api/v1/tasks/{id}
- State management: Zustand (if needed)

**Dependencies:** STORY-TASK-007

---

#### STORY-TASK-009: Manual Task Creation Form (Frontend + Backend)
**Priority:** Must Have
**Points:** 3
**Sprint:** Sprint 2

**User Story:**
As an admin, I want to manually create tasks for ad-hoc work, so I can track non-automated workflows.

**Acceptance Criteria:**
- [ ] Create task form `/tasks/new`
- [ ] Form fields: Title, Type (dropdown), Priority (dropdown), Assigned To (user select), Due Date (date picker), Description (textarea)
- [ ] Validation working (all required fields, due date > today)
- [ ] Template selection dropdown (pre-fill common tasks)
- [ ] Submit → Call POST /api/v1/tasks API
- [ ] Success → Redirect to task detail page
- [ ] Error handling (show validation errors inline)
- [ ] Unit tests for form logic

**Technical Notes:**
- Form library: React Hook Form + Zod validation
- UI: shadcn/ui Form, Input, Select, Textarea
- Templates: Hardcoded array (can move to API later)

**Dependencies:** STORY-TASK-005

---

#### STORY-TASK-010: Bulk Task Creation (CSV Import)
**Priority:** Should Have
**Points:** 3
**Sprint:** Sprint 2

**User Story:**
As an admin, I want to bulk create tasks via CSV import, so I can efficiently create many tasks at once.

**Acceptance Criteria:**
- [ ] CSV upload form `/tasks/bulk-create`
- [ ] CSV format validation (columns: title, type, priority, assigned_to, due_date, description)
- [ ] Preview table showing parsed tasks (with validation errors highlighted)
- [ ] Bulk create API: POST /api/v1/tasks/bulk (accepts array of tasks)
- [ ] Progress indicator during creation
- [ ] Success summary (X tasks created, Y failed)
- [ ] Export failed tasks as CSV for retry
- [ ] Unit tests + integration tests

**Technical Notes:**
- CSV parsing: `papaparse` library (frontend)
- Backend: Process in batches (100 tasks/batch)
- Validation: Reuse single task validation logic

**Dependencies:** STORY-TASK-009

---

### EPIC-002: SLA Tracking & Escalation

#### STORY-SLA-001: SLA Configuration per Task Type
**Priority:** Must Have
**Points:** 3
**Sprint:** Sprint 3

**User Story:**
As an admin, I want to configure SLA targets cho mỗi task type, so system knows deadlines for each workflow.

**Acceptance Criteria:**
- [ ] SLA config stored in database (collection: `sla_policies`)
- [ ] Schema: task_type, target_minutes, warning_threshold (24h default), escalation_threshold (48h)
- [ ] Default configs for 5 task types:
  - content_review: 48 hours
  - reconciliation: 24 hours
  - bonus_approval: 12 hours
  - campaign_setup: 4 hours
  - dispute_resolution: 72 hours
- [ ] Admin UI to view/edit SLA configs
- [ ] New tasks automatically inherit SLA from type
- [ ] Validation: target > 0, warning < escalation
- [ ] Unit tests >80%

**Technical Notes:**
- Location: `pkg/taskengine/domain/sla_policy.go`
- API: GET/PUT /api/v1/sla-policies
- UI: Simple form với task type dropdown

**Dependencies:** STORY-TASK-005

---

#### STORY-SLA-002: SLA Monitoring Background Job (Asynq)
**Priority:** Must Have
**Points:** 5
**Sprint:** Sprint 3

**User Story:**
As a system, I want background job monitoring SLA deadlines, so warnings và breach notifications are sent automatically.

**Acceptance Criteria:**
- [ ] Background worker runs every 5 minutes
- [ ] Find tasks approaching deadline (24h warning):
  - status = assigned | in_progress
  - due_date between (now, now+24h)
  - warning_sent = false
- [ ] Send warning notification (via notification module)
- [ ] Mark warning_sent = true
- [ ] Find overdue tasks:
  - status = assigned | in_progress
  - due_date < now
  - is_breached = false
- [ ] Send breach notification to assignee + admin
- [ ] Mark is_breached = true
- [ ] Log all SLA events
- [ ] Integration tests simulate time passing

**Technical Notes:**
- Queue: Asynq (Redis-based)
- Cron: `@every 5m`
- Notification: Use STORY-NOT-005 API

**Dependencies:** STORY-SLA-001, STORY-NOT-005

---

#### STORY-SLA-003: SLA Dashboard & Reports (Frontend + Backend)
**Priority:** Should Have
**Points:** 5
**Sprint:** Sprint 3

**User Story:**
As a manager, I want to see SLA compliance dashboard, so I can track team performance.

**Acceptance Criteria:**
- [ ] Dashboard page `/sla-dashboard`
- [ ] 5 key metrics displayed:
  - Current SLA compliance rate (% tasks completed within SLA)
  - Tasks by status (pie chart: assigned, in progress, overdue, completed)
  - Overdue tasks list (table với assignee, how long overdue)
  - SLA trends (line chart: compliance % over last 30 days)
  - Team performance (table: SLA compliance by reviewer)
- [ ] Export to Excel button
- [ ] Real-time updates (WebSocket)
- [ ] API endpoints:
  - GET /api/v1/sla/metrics
  - GET /api/v1/sla/trends?days=30
  - GET /api/v1/sla/team-performance
- [ ] Charts render correctly (Recharts)
- [ ] Responsive design

**Technical Notes:**
- Charts: Recharts library
- Export: `xlsx` library
- WebSocket: Reuse STORY-NOT-004 infrastructure

**Dependencies:** STORY-SLA-002

---

#### STORY-SLA-004: SLA Escalation Workflow
**Priority:** Should Have
**Points:** 3
**Sprint:** Sprint 3

**User Story:**
As a manager, I want overdue tasks auto-escalated to me, so blockers get resolved quickly.

**Acceptance Criteria:**
- [ ] Escalation triggers after 24h breach (configurable)
- [ ] Escalation logic:
  1. Find task's manager (user.manager_id)
  2. Reassign task to manager
  3. Send notification to both assignee + manager
  4. Log escalation event in task history
- [ ] Can disable auto-escalation via config
- [ ] Manual escalation button in UI
- [ ] Unit tests >85%

**Technical Notes:**
- Config: `AUTO_ESCALATION_ENABLED=true` (env var)
- Run in SLA monitoring background job

**Dependencies:** STORY-SLA-002

---

#### STORY-SLA-005: Auto-Task Creation from Business Events
**Priority:** Must Have
**Points:** 4
**Sprint:** Sprint 3

**User Story:**
As a system, I want tasks auto-created when business events occur, so reviewers know what to work on without manual creation.

**Acceptance Criteria:**
- [ ] Event hooks implemented for 3 business events:
  - ContentSubmitted → Create "Review Content" task
  - CampaignCreated → Create "Setup Campaign" + "Configure Metrics" tasks
  - ReconciliationStarted → Create "Review Reconciliation" task
- [ ] Task templates defined for each event type
- [ ] Auto-assignment triggered after creation
- [ ] Notification sent to assigned user
- [ ] Metadata linked correctly (content_id, campaign_id)
- [ ] Integration tests simulate events
- [ ] Event publisher interface (can swap Redis Pub/Sub, Kafka, etc.)

**Technical Notes:**
- Event bus: Redis Pub/Sub (initial), can add Kafka later
- Location: `pkg/taskengine/events/`
- Example event:
  ```go
  eventBus.Publish("content.submitted", ContentSubmittedEvent{
      ContentID: 123,
      CampaignID: 456,
      CreatorID: 789,
  })
  ```

**Dependencies:** STORY-TASK-006

---

### EPIC-004: Workflow Orchestration Engine

#### STORY-WORKFLOW-001: Workflow Engine Foundation (State Management)
**Priority:** Must Have
**Points:** 5
**Sprint:** Sprint 4

**User Story:**
As a system, I want a workflow engine managing multi-step processes, so complex workflows can execute automatically.

**Acceptance Criteria:**
- [ ] Workflow entity defined: id, name, steps, current_step, status, metadata
- [ ] WorkflowStep: id, name, type (task, parallel_gateway, join_gateway, end), next_steps
- [ ] Workflow state machine: draft → running → completed/failed
- [ ] Step execution engine: Execute step → Transition to next → Repeat until end
- [ ] Workflow repository (MongoDB collection: `workflows`)
- [ ] API: POST /api/v1/workflows (start workflow)
- [ ] API: GET /api/v1/workflows/{id} (get status)
- [ ] Unit tests >85%

**Technical Notes:**
- Location: `pkg/taskengine/workflow/`
- Simple implementation first (no Temporal/n8n)
- Can add YAML-based workflow definitions later

**Dependencies:** STORY-TASK-005

---

#### STORY-WORKFLOW-002: Parallel Workflow Execution (Parallel Gateway)
**Priority:** Must Have
**Points:** 5
**Sprint:** Sprint 4

**User Story:**
As a system, I want to execute tasks in parallel, so workflows complete faster.

**Acceptance Criteria:**
- [ ] Parallel gateway step type implemented
- [ ] Parallel gateway spawns multiple tasks simultaneously
- [ ] Join gateway waits for all parallel tasks to complete
- [ ] Example workflow:
  ```
  Setup Campaign (1 task)
      ↓
  [Parallel Gateway]
      ├─► Content Review 1
      ├─► Content Review 2
      ├─► Content Review 3
      └─► Tech Setup
      ↓
  [Join Gateway] - Wait for ALL
      ↓
  Reconciliation
  ```
- [ ] Workflow status tracks parallel progress
- [ ] Integration tests verify parallel execution
- [ ] Visual workflow diagram in UI (optional, nice to have)

**Technical Notes:**
- Use goroutines for parallel task creation
- Join gateway: Check if all parallel tasks completed

**Dependencies:** STORY-WORKFLOW-001

---

#### STORY-WORKFLOW-003: Conditional Workflow Routing (Decision Gateway)
**Priority:** Should Have
**Points:** 3
**Sprint:** Sprint 4

**User Story:**
As a system, I want workflows to branch based on conditions, so different paths execute based on data.

**Acceptance Criteria:**
- [ ] Decision gateway step type implemented
- [ ] Conditional expressions evaluated (simple if/else logic)
- [ ] Example conditions:
  - If content.rejected → Create dispute task
  - If reconciliation.discrepancy > 20% → Escalate to manager
  - If budget.utilization > 90% → Pause campaign
- [ ] Workflow logs decision rationale
- [ ] Unit tests cover all conditions

**Technical Notes:**
- Expression language: Simple Go conditionals (avoid complex DSL initially)
- Can add `github.com/antonmedv/expr` later for advanced expressions

**Dependencies:** STORY-WORKFLOW-002

---

#### STORY-WORKFLOW-004: Workflow Visual Builder (Frontend - Optional)
**Priority:** Could Have
**Points:** 8
**Sprint:** Sprint 9

**User Story:**
As an admin, I want to visually build workflows, so I can customize processes without coding.

**Acceptance Criteria:**
- [ ] Drag-and-drop workflow builder (React Flow library)
- [ ] Node types: Task, Parallel Gateway, Join Gateway, Decision Gateway, End
- [ ] Connect nodes with edges
- [ ] Configure each node (name, task type, conditions)
- [ ] Save workflow as JSON
- [ ] Load và visualize existing workflows
- [ ] Validation (no orphan nodes, valid connections)

**Technical Notes:**
- Library: `reactflow` (drag-and-drop workflow builder)
- Complex feature - defer to later sprint

**Dependencies:** STORY-WORKFLOW-003

---

### EPIC-005: Budget Tracking & Controls

#### STORY-BUDGET-001: Budget Dashboard (Real-Time Metrics)
**Priority:** Must Have
**Points:** 5
**Sprint:** Sprint 5

**User Story:**
As a finance manager, I want real-time budget dashboard, so I know campaign spend status.

**Acceptance Criteria:**
- [ ] Dashboard page `/budget-dashboard`
- [ ] 6 key metrics:
  - Allocated: Total budget (500M VND)
  - Committed: Approved content chưa paid (350M VND)
  - Spent: Paid out (200M VND)
  - Available: Allocated - Committed (150M VND)
  - Forecast: ML prediction of final spend (480M VND)
  - Utilization Rate: Committed/Allocated (70%)
- [ ] Visual progress bar color-coded:
  - 🟢 Green: <80%
  - 🟡 Yellow: 80-95%
  - 🔴 Red: >95%
- [ ] Real-time updates (WebSocket)
- [ ] Export to Excel
- [ ] API: GET /api/v1/budget/metrics?campaign_id=X

**Technical Notes:**
- Budget data: Aggregate from `event_rewards` collection
- Real-time: WebSocket updates on new approval

**Dependencies:** STORY-TASK-005

---

#### STORY-BUDGET-002: Budget Control Enforcement (Before Approval)
**Priority:** Must Have
**Points:** 5
**Sprint:** Sprint 5

**User Story:**
As a system, I want to block content approval if budget exceeded, so we don't overspend.

**Acceptance Criteria:**
- [ ] 3 budget checks before approval:
  - **Check 1:** Campaign budget (current + reward <= campaign budget)
  - **Check 2:** Creator cap (creator earnings + reward <= creator cap)
  - **Check 3:** Platform daily limit (platform spend today + reward <= daily limit)
- [ ] If any check fails → Block approval, return error message
- [ ] Can override với manager approval (optional flag)
- [ ] Log all check results
- [ ] Integration tests verify blocks
- [ ] API: POST /api/v1/content/{id}/approve (with budget checks)

**Technical Notes:**
- Budget service: Calculate current spend in real-time
- Override: Require admin role + reason

**Dependencies:** STORY-BUDGET-001

---

#### STORY-BUDGET-003: Auto-Pause Campaign on Budget Exhaustion
**Priority:** Must Have
**Points:** 3
**Sprint:** Sprint 5

**User Story:**
As a system, I want campaigns auto-paused when budget 100% utilized, so no overspend occurs.

**Acceptance Criteria:**
- [ ] Background job monitors budget utilization
- [ ] When utilization >= 100%:
  - Set campaign.status = PAUSED_BUDGET_EXHAUSTED
  - Block new content submissions
  - Send notifications to stakeholders (campaign manager, finance)
  - Log pause event
- [ ] Can manually resume after budget increase
- [ ] Resume workflow: Update budget → Click Resume button → Confirm
- [ ] Integration tests simulate budget exhaustion

**Technical Notes:**
- Run in same job as SLA monitoring (every 5 min)
- Notification: Use STORY-NOT-005 API

**Dependencies:** STORY-BUDGET-002

---

#### STORY-BUDGET-004: Budget Alerts (80%, 95% Thresholds)
**Priority:** Must Have
**Points:** 2
**Sprint:** Sprint 5

**User Story:**
As a campaign manager, I want budget alerts at 80% và 95%, so I can request increase early.

**Acceptance Criteria:**
- [ ] Alert rules configured:
  - 🟡 Warning at 80% utilization → Notify campaign manager
  - 🔴 Critical at 95% utilization → Notify campaign manager + finance
- [ ] Alerts sent once (don't spam)
- [ ] Alert includes: Current utilization, forecast, recommended action
- [ ] Alerts logged in database
- [ ] Can configure thresholds (80%, 95% are defaults)

**Technical Notes:**
- Store last alert level to avoid duplicates
- Notification channels: Telegram + Email

**Dependencies:** STORY-BUDGET-001

---

#### STORY-BUDGET-005: Budget Forecast ML Model (Basic Linear)
**Priority:** Should Have
**Points:** 5
**Sprint:** Sprint 11

**User Story:**
As a finance manager, I want ML forecast of final spend, so I can plan budget adjustments.

**Acceptance Criteria:**
- [ ] ML model trained on historical campaign data
- [ ] Input features: submissions_per_day, approval_rate, avg_views, avg_reward, days_elapsed
- [ ] Output: Predicted final spend
- [ ] Model: Simple linear regression (MVP) or Random Forest (advanced)
- [ ] Accuracy: Mean Absolute Error <10%
- [ ] Forecast updates daily
- [ ] If forecast >120% budget → Send early warning
- [ ] API: GET /api/v1/budget/forecast?campaign_id=X
- [ ] Model versioning (store model version)

**Technical Notes:**
- ML library: `gonum.org/v1/gonum` (Go) or Python microservice
- Training data: Last 10 campaigns
- Retrain monthly

**Dependencies:** STORY-BUDGET-001

---

### EPIC-007: Auto-Reconciliation System

#### STORY-RECON-001: Auto-Match Algorithm (URL Matching + Discrepancy)
**Priority:** Must Have
**Points:** 8
**Sprint:** Sprint 6

**User Story:**
As a reconciliation admin, I want 90% auto-matching, so I only review exceptions.

**Acceptance Criteria:**
- [ ] Algorithm implemented:
  ```
  For each content submission:
    1. Find match in crawled data by URL
    2. If match found:
       - Compare views (submission vs crawled)
       - Calculate discrepancy % = |submission - crawled| / crawled
       - If discrepancy < 10%:
         → Auto-approve, mark matched
       - Else if discrepancy 10-20%:
         → Flag "MEDIUM_DISCREPANCY"
       - Else (>20%):
         → Flag "HIGH_DISCREPANCY"
    3. If no match found:
       → Flag "NOT_FOUND"
  ```
- [ ] Target: >90% auto-approve rate
- [ ] Match accuracy >95%
- [ ] Performance: 1000 items in <30 seconds
- [ ] Flags stored in database
- [ ] Integration tests với sample data

**Technical Notes:**
- URL normalization: Remove query params, trailing slash
- Fuzzy matching: Levenshtein distance for similar URLs
- Parallel processing: Use goroutines

**Dependencies:** None (standalone logic)

---

#### STORY-RECON-002: Flagged Items Review Dashboard (Frontend)
**Priority:** Must Have
**Points:** 5
**Sprint:** Sprint 6

**User Story:**
As an admin, I want dashboard chỉ showing flagged items, so I focus on exceptions only.

**Acceptance Criteria:**
- [ ] Dashboard page `/reconciliation/flagged`
- [ ] Filters: NOT_FOUND, MEDIUM_DISCREPANCY, HIGH_DISCREPANCY, DUPLICATE
- [ ] Sort: By discrepancy % (highest first)
- [ ] Table columns: Content ID, Submitted Views, Crawled Views, Discrepancy %, Flag, Actions
- [ ] Comparison view: Side-by-side submission vs crawled data
- [ ] Quick actions:
  - Approve anyway (with note)
  - Reject with reason
  - Bulk approve (select multiple)
- [ ] Pagination (50 items/page)
- [ ] Export flagged items to Excel

**Technical Notes:**
- API: GET /api/v1/reconciliation/flagged
- Bulk actions: POST /api/v1/reconciliation/bulk-approve

**Dependencies:** STORY-RECON-001

---

#### STORY-RECON-003: Reconciliation Audit Trail
**Priority:** Should Have
**Points:** 3
**Sprint:** Sprint 6

**User Story:**
As a compliance officer, I want full audit trail, so I can verify all reconciliation decisions.

**Acceptance Criteria:**
- [ ] All decisions logged:
  - Auto-approved: Log match score, discrepancy %
  - Manual approved: Log admin, reason, timestamp
  - Rejected: Log reason
- [ ] Audit trail stored in `reconciliation_audit` collection
- [ ] Audit trail immutable (no updates, only inserts)
- [ ] Export audit trail to Excel
- [ ] Search & filter audit logs (by date, admin, decision)
- [ ] Retention policy: 2 years (configurable)

**Technical Notes:**
- Append-only collection
- Index: content_id, created_at

**Dependencies:** STORY-RECON-002

---

#### STORY-RECON-004: Reconciliation Background Job (Daily Batch)
**Priority:** Must Have
**Points:** 4
**Sprint:** Sprint 6

**User Story:**
As a system, I want daily reconciliation job running automatically, so admins don't manually trigger.

**Acceptance Criteria:**
- [ ] Background job runs daily at 2am
- [ ] Fetch new submissions from last 24h
- [ ] Fetch crawled data from Content Catcher API
- [ ] Run auto-match algorithm (STORY-RECON-001)
- [ ] Send summary notification (X matched, Y flagged)
- [ ] Log job execution (start time, end time, results)
- [ ] Error handling (retry 3 times if Content Catcher fails)
- [ ] Integration tests

**Technical Notes:**
- Asynq scheduled task: `@daily 02:00`
- Content Catcher API: GET /api/crawled-data?start_date=...

**Dependencies:** STORY-RECON-001

---

### EPIC-006: Fraud Detection System

#### STORY-FRAUD-001: Rule-Based Fraud Detection (4 Rules)
**Priority:** Must Have
**Points:** 5
**Sprint:** Sprint 8

**User Story:**
As a reviewer, I want fraud flags displayed during review, so I can spot suspicious content.

**Acceptance Criteria:**
- [ ] 4 fraud detection rules implemented:
  - **Rule 1:** Abnormal view velocity (views/hour > 100,000) → Flag "SUSPICIOUS_VIEW_VELOCITY"
  - **Rule 2:** Low engagement rate (likes/views < 0.5%) → Flag "LOW_ENGAGEMENT_RATE"
  - **Rule 3:** New account (account age < 30 days) → Flag "NEW_ACCOUNT"
  - **Rule 4:** Follower spike (follower growth >20% in 1 day) → Flag "FOLLOWER_SPIKE"
- [ ] Scoring algorithm:
  - 0 flags → Auto-approve (safe)
  - 1-2 flags → Manual review (yellow flag)
  - 3+ flags → Auto-reject recommendation (red flag)
- [ ] Flags displayed in review UI
- [ ] Can override (with justification required)
- [ ] False positive rate <5%
- [ ] Integration tests

**Technical Notes:**
- Run before approval decision
- Store fraud score in task metadata

**Dependencies:** STORY-TASK-005

---

#### STORY-FRAUD-002: Blacklist Management (CRUD + Auto-Block)
**Priority:** Must Have
**Points:** 3
**Sprint:** Sprint 8

**User Story:**
As an admin, I want to blacklist fraud creators, so they can't submit again.

**Acceptance Criteria:**
- [ ] Blacklist CRUD operations:
  - Add creator to blacklist (reason required)
  - Remove from blacklist (appeal approved)
  - List blacklisted creators
  - Export blacklist (CSV)
- [ ] Ban types: Permanent, Temporary (with expiry date)
- [ ] Auto-block: If blacklisted creator submits → Auto-reject with message
- [ ] Check blacklist before creating review task
- [ ] Appeal workflow (creator can request unban)
- [ ] Blacklist visible to admins only (not public)
- [ ] Integration tests

**Technical Notes:**
- Collection: `blacklist`
- Check: Before task creation, lookup creator_id in blacklist

**Dependencies:** STORY-FRAUD-001

---

#### STORY-FRAUD-003: Fraud Detection Dashboard (Analytics)
**Priority:** Should Have
**Points:** 3
**Sprint:** Sprint 8

**User Story:**
As a fraud analyst, I want dashboard showing fraud trends, so I can improve detection rules.

**Acceptance Criteria:**
- [ ] Dashboard page `/fraud-dashboard`
- [ ] Metrics:
  - Total fraud cases detected
  - Fraud rate (fraud / total submissions)
  - Top fraud patterns (which rules trigger most)
  - False positive rate
- [ ] Charts:
  - Fraud trend over time (line chart)
  - Fraud by rule (bar chart)
- [ ] Export fraud report to Excel
- [ ] API: GET /api/v1/fraud/analytics

**Technical Notes:**
- Aggregate fraud flags from tasks metadata

**Dependencies:** STORY-FRAUD-002

---

#### STORY-FRAUD-004: ML-Based Fraud Detection (Random Forest)
**Priority:** Could Have
**Points:** 8
**Sprint:** Sprint 11

**User Story:**
As a system, I want ML fraud detection catching sophisticated patterns, so we prevent advanced fraud.

**Acceptance Criteria:**
- [ ] ML model trained on historical fraud data (labeled dataset)
- [ ] Features: views, likes, comments, shares, follower_count, account_age, engagement_rate, view_velocity, etc.
- [ ] Model: Random Forest classifier
- [ ] Output: Fraud probability (0-1)
- [ ] Decision thresholds:
  - Prob > 0.8 → Auto-reject
  - Prob 0.5-0.8 → Manual review
  - Prob < 0.5 → Auto-approve
- [ ] Model accuracy >90%
- [ ] Predictions integrated into review flow
- [ ] Model monitoring (drift detection)
- [ ] Retraining pipeline (monthly)
- [ ] A/B test ML vs rule-based

**Technical Notes:**
- ML library: Python microservice (scikit-learn) or Go (`gonum`)
- Training data: Need labeled fraud cases (at least 1000 samples)
- Feature engineering: Add domain-specific features

**Dependencies:** STORY-FRAUD-001

---

#### STORY-FRAUD-005: Fraud Alerts (High-Risk Submissions)
**Priority:** Must Have
**Points:** 2
**Sprint:** Sprint 8

**User Story:**
As a fraud manager, I want immediate alerts for high-risk submissions, so I can investigate quickly.

**Acceptance Criteria:**
- [ ] Alert rule: If fraud score >= 3 flags → Send critical alert
- [ ] Alert channels: Telegram + Email to fraud team
- [ ] Alert includes: Creator info, content link, fraud flags, recommended action
- [ ] Alert deduplication (don't spam for same creator)
- [ ] Can configure alert threshold (default: 3 flags)

**Technical Notes:**
- Use STORY-NOT-005 notification API
- Store last alert time to avoid duplicates

**Dependencies:** STORY-FRAUD-001

---

### EPIC-008: Monitoring, Alerting & Business Continuity

#### STORY-MONITOR-001: System Health Dashboard (Backend + Frontend)
**Priority:** Must Have
**Points:** 5
**Sprint:** Sprint 12

**User Story:**
As an ops engineer, I want system health dashboard, so I know if services are down.

**Acceptance Criteria:**
- [ ] Dashboard page `/system-health`
- [ ] 15+ metrics displayed:
  - **Service Status:** API (UP/DOWN), DB (UP/DOWN), Redis (UP/DOWN), MinIO (UP/DOWN)
  - **Resource Usage:** CPU %, Memory %, Disk %
  - **Error Rates:** 5xx errors/min, exceptions/min
  - **Response Times:** P50, P95, P99 latency
  - **Queue Depths:** Asynq pending jobs count
- [ ] Color coding: 🟢 Green (healthy), 🟡 Yellow (warning), 🔴 Red (critical)
- [ ] Historical charts (last 24h)
- [ ] Real-time updates (5s refresh)
- [ ] Mobile-friendly
- [ ] API: GET /api/v1/system/health

**Technical Notes:**
- Metrics collection: Prometheus (optional) or custom
- Health checks: Ping DB, Redis, etc.

**Dependencies:** None

---

#### STORY-MONITOR-002: Alert Rules & Notifications (PagerDuty + Telegram)
**Priority:** Must Have
**Points:** 5
**Sprint:** Sprint 12

**User Story:**
As an on-call engineer, I want critical alerts via PagerDuty, so I respond to outages immediately.

**Acceptance Criteria:**
- [ ] Alert rules configured:
  - 🔴 **CRITICAL** (Page on-call):
    - API down >5 min
    - Database primary down
    - Error rate >10%
    - Payment processing stopped
  - 🟡 **WARNING** (Notify Slack/Telegram):
    - CPU >80%
    - Disk >90%
    - Queue depth >1000
    - Response time >2s
- [ ] Alert channels:
  - PagerDuty (critical only)
  - Telegram #ops-alerts (all alerts)
  - Slack (warnings)
- [ ] Alert deduplication (don't spam)
- [ ] Alert resolution tracking
- [ ] False alarm rate <5%

**Technical Notes:**
- Alerting: Prometheus Alertmanager (if using Prometheus) or custom
- PagerDuty API: `github.com/PagerDuty/go-pagerduty`

**Dependencies:** STORY-MONITOR-001

---

#### STORY-MONITOR-003: Automated Backup & Restore (MongoDB + MinIO)
**Priority:** Must Have
**Points:** 5
**Sprint:** Sprint 12

**User Story:**
As a business owner, I want automated backups tested monthly, so I trust disaster recovery.

**Acceptance Criteria:**
- [ ] Automated backup strategy:
  - **MongoDB:** Full backup daily (retained 30 days), incremental every 6h
  - **MinIO files:** Sync to S3 hourly, versioning enabled, retention 90 days
  - **Config:** Infrastructure as Code (Terraform), env vars in vault
- [ ] Backups uploaded to AWS S3 (or alternative)
- [ ] Restore procedure documented (runbook)
- [ ] Monthly restore test passed (in staging)
- [ ] RTO (Recovery Time Objective): 1 hour
- [ ] RPO (Recovery Point Objective): 15 minutes
- [ ] Monitoring backup success (alert if backup fails)

**Technical Notes:**
- MongoDB backup: `mongodump` or MongoDB Atlas backups
- S3 sync: AWS CLI or `rclone`
- Restore runbook: Step-by-step instructions

**Dependencies:** None

---

#### STORY-MONITOR-004: Operational Runbooks (5 Runbooks)
**Priority:** Must Have
**Points:** 3
**Sprint:** Sprint 12

**User Story:**
As an on-call engineer, I want runbooks for common failures, so I can recover quickly.

**Acceptance Criteria:**
- [ ] 5 runbooks documented:
  1. **Database Failure Recovery:** MongoDB failover steps
  2. **Redis Failure Recovery:** Restart Redis, drain queue
  3. **Content Catcher API Outage:** Enable manual metric entry
  4. **Payment Processing Failure:** Retry logic, notify creators
  5. **Full Disaster Recovery:** Restore from backups
- [ ] Each runbook includes:
  - Symptom description
  - Diagnosis steps
  - Recovery steps (copy-paste commands)
  - Estimated time
  - Validation checklist
  - Communication plan (who to notify)
- [ ] Runbooks tested in staging
- [ ] Accessible to on-call team (wiki or docs)
- [ ] Updated quarterly

**Technical Notes:**
- Format: Markdown files in `/docs/runbooks/`
- Review quarterly or after incidents

**Dependencies:** STORY-MONITOR-003

---

#### STORY-MONITOR-005: Error Tracking (Sentry Integration)
**Priority:** Must Have
**Points:** 2
**Sprint:** Sprint 12

**User Story:**
As a developer, I want all errors tracked in Sentry, so I can debug issues quickly.

**Acceptance Criteria:**
- [ ] Sentry SDK integrated (backend + frontend)
- [ ] All exceptions captured automatically
- [ ] Context included: User ID, request ID, stack trace
- [ ] Error grouping working (similar errors grouped)
- [ ] Email alerts for critical errors
- [ ] Breadcrumbs tracking (actions before error)
- [ ] Release tracking (tag errors by deploy version)

**Technical Notes:**
- Sentry DSN: Store in env var
- Backend: `github.com/getsentry/sentry-go`
- Frontend: `@sentry/react`

**Dependencies:** None

---

### EPIC-003 (Continued): Advanced Notification Features

#### STORY-NOT-006: Notification Preferences UI (User Settings)
**Priority:** Should Have
**Points:** 3
**Sprint:** Sprint 10

**User Story:**
As a user, I want to configure notification preferences, so I only get alerts I care about.

**Acceptance Criteria:**
- [ ] Settings page `/settings/notifications`
- [ ] Configure channels: Enable/disable Telegram, Email, In-app
- [ ] Configure event types: Which events trigger notifications (task assigned, due soon, completed, etc.)
- [ ] Quiet hours: Don't send notifications 10pm-8am (timezone-aware)
- [ ] Digest mode: Batch notifications, send 1 summary email/day
- [ ] Save preferences to database
- [ ] Notification engine respects preferences
- [ ] Unit tests for preferences logic

**Technical Notes:**
- API: GET/PUT /api/v1/users/{id}/notification-preferences
- Quiet hours: Use user's timezone

**Dependencies:** STORY-NOT-005

---

#### STORY-NOT-007: Notification Digest (Daily Summary Email)
**Priority:** Should Have
**Points:** 3
**Sprint:** Sprint 10

**User Story:**
As a user, I want daily digest email, so I get 1 summary instead of many individual notifications.

**Acceptance Criteria:**
- [ ] Digest mode option in preferences
- [ ] Daily job aggregates notifications (last 24h)
- [ ] Digest email template with sections:
  - Tasks assigned to you (count + list)
  - Tasks due soon (count + list)
  - Overdue tasks (count + list)
- [ ] Send at configured time (default: 8am user timezone)
- [ ] Skip if no notifications
- [ ] Integration tests

**Technical Notes:**
- Asynq scheduled task: `@daily` per user timezone
- Template: HTML email with sections

**Dependencies:** STORY-NOT-006

---

#### STORY-NOT-008: Notification Delivery Analytics (Dashboard)
**Priority:** Could Have
**Points:** 2
**Sprint:** Sprint 10

**User Story:**
As a product manager, I want notification analytics, so I know which channels users prefer.

**Acceptance Criteria:**
- [ ] Dashboard `/notifications/analytics`
- [ ] Metrics:
  - Notifications sent by channel (Telegram, Email, In-app)
  - Delivery rate by channel
  - Read rate (in-app notifications)
  - Click-through rate (Telegram inline buttons)
- [ ] Charts: Line chart (notifications over time), Pie chart (by channel)
- [ ] Export analytics to CSV

**Technical Notes:**
- Aggregate from `notifications` collection

**Dependencies:** STORY-NOT-006

---

#### STORY-NOT-009: Notification Templates Editor (Admin UI)
**Priority:** Could Have
**Points:** 3
**Sprint:** Sprint 10

**User Story:**
As an admin, I want to edit notification templates, so I can customize messages without code changes.

**Acceptance Criteria:**
- [ ] Template editor UI `/admin/notification-templates`
- [ ] List all templates (task assigned, due soon, etc.)
- [ ] Edit template with variables preview (e.g., {{task_title}}, {{due_date}})
- [ ] Preview rendering (show example notification)
- [ ] Save template to database
- [ ] Template versioning (rollback to previous version)
- [ ] Validation (required variables present)

**Technical Notes:**
- Template engine: Go `html/template` or custom
- Store templates in database (collection: `notification_templates`)

**Dependencies:** STORY-NOT-005

---

### EPIC-004 (Continued): Workflow Templates

#### STORY-WORKFLOW-005: 4 Pre-Defined Workflow Templates
**Priority:** Should Have
**Points:** 5
**Sprint:** Sprint 9

**User Story:**
As an admin, I want pre-defined workflow templates, so I can reuse proven processes.

**Acceptance Criteria:**
- [ ] 4 workflow templates defined:
  1. **Campaign Approval Workflow:** 3-level approval (Reviewer → Manager → Finance)
  2. **Content Review Workflow:** Submit → Review → Publish
  3. **Reconciliation Workflow:** Collect → Match → Approve
  4. **Dispute Resolution Workflow:** Submit → Investigate → Resolve
- [ ] Templates stored in database
- [ ] Can activate template for a campaign
- [ ] Templates versioned (v1, v2, etc.)
- [ ] API: GET /api/v1/workflow-templates, POST /api/v1/workflows/from-template

**Technical Notes:**
- Store as JSON in `workflow_templates` collection
- Include step definitions, transitions, task templates

**Dependencies:** STORY-WORKFLOW-003

---

#### STORY-WORKFLOW-006: Clone & Customize Workflow Template (UI)
**Priority:** Should Have
**Points:** 3
**Sprint:** Sprint 9

**User Story:**
As an admin, I want to clone và customize templates, so I can adapt workflows to specific needs.

**Acceptance Criteria:**
- [ ] Clone template button
- [ ] Edit workflow steps (add, remove, reorder)
- [ ] Edit step properties (name, task type, conditions)
- [ ] Save as new template (with new name)
- [ ] Validate workflow (no orphan steps, valid connections)
- [ ] Preview workflow before saving

**Technical Notes:**
- UI: Form với step editor (simple JSON editor initially)
- Can add visual builder later (STORY-WORKFLOW-004)

**Dependencies:** STORY-WORKFLOW-005

---

#### STORY-WORKFLOW-007: Workflow Execution Logs & Debugging
**Priority:** Should Have
**Points:** 2
**Sprint:** Sprint 9

**User Story:**
As a developer, I want workflow execution logs, so I can debug failed workflows.

**Acceptance Criteria:**
- [ ] Log all workflow events:
  - Workflow started
  - Step executed (which step, result)
  - Step failed (error message)
  - Workflow completed/failed
- [ ] Logs stored in `workflow_logs` collection
- [ ] UI to view logs for a workflow instance
- [ ] Search logs by workflow_id, date
- [ ] Log retention: 90 days

**Technical Notes:**
- Structured logging with step details
- Index: workflow_id, created_at

**Dependencies:** STORY-WORKFLOW-005

---

### Sprint 13-14: Documentation, UAT, Launch

#### STORY-DOCS-001: API Documentation (OpenAPI/Swagger)
**Priority:** Must Have
**Points:** 3
**Sprint:** Sprint 13

**User Story:**
As a frontend developer, I want API documentation, so I can integrate với backend easily.

**Acceptance Criteria:**
- [ ] OpenAPI spec auto-generated từ code
- [ ] All API endpoints documented (100+ endpoints)
- [ ] Request/response schemas defined
- [ ] Example requests/responses included
- [ ] Swagger UI hosted at `/api/docs`
- [ ] Postman collection exported

**Technical Notes:**
- Library: `github.com/swaggo/gin-swagger`
- Annotations: Add Swagger comments to handlers

**Dependencies:** All API stories

---

#### STORY-DOCS-002: User Guide với Screenshots
**Priority:** Must Have
**Points:** 3
**Sprint:** Sprint 13

**User Story:**
As a new admin, I want user guide với screenshots, so I can learn how to use the system.

**Acceptance Criteria:**
- [ ] User guide document (Markdown or PDF)
- [ ] 10+ sections:
  - Login & Authentication
  - My Tasks Dashboard
  - Task Detail & Actions
  - Creating Tasks Manually
  - SLA Dashboard
  - Budget Dashboard
  - Reconciliation Review
  - Notification Settings
  - Workflow Management
  - System Health Monitoring
- [ ] Screenshots for each feature
- [ ] Step-by-step instructions
- [ ] FAQ section

**Technical Notes:**
- Format: Markdown in `/docs/user-guide.md`
- Screenshots: Use staging environment

**Dependencies:** All UI stories

---

#### STORY-DOCS-003: Architecture & Deployment Guide
**Priority:** Must Have
**Points:** 3
**Sprint:** Sprint 13

**User Story:**
As an ops engineer, I want deployment guide, so I can deploy to production confidently.

**Acceptance Criteria:**
- [ ] Architecture diagram (updated from architecture doc)
- [ ] System components overview
- [ ] Deployment guide:
  - Infrastructure setup (MongoDB, Redis)
  - Docker deployment steps
  - Environment variables configuration
  - Database migration steps
  - Backup/restore procedures
- [ ] Monitoring setup (Sentry, health checks)
- [ ] Troubleshooting section

**Technical Notes:**
- Format: Markdown in `/docs/deployment-guide.md`
- Include all env vars needed

**Dependencies:** All infrastructure stories

---

#### STORY-UAT-001: UAT với Pilot Campaign (Testing)
**Priority:** Must Have
**Points:** 5
**Sprint:** Sprint 13

**User Story:**
As a QA lead, I want to run UAT với real pilot campaign, so we validate system works end-to-end.

**Acceptance Criteria:**
- [ ] Pilot campaign created (small scale: 10 creators, 100K budget)
- [ ] Test all workflows:
  - Content submission → Review → Approval
  - SLA tracking (warnings, escalation)
  - Budget tracking (alerts, auto-pause)
  - Reconciliation (auto-match, flagged review)
  - Fraud detection (simulate fraud case)
  - Notifications (Telegram, Email, In-app)
- [ ] UAT test cases (50+ scenarios)
- [ ] Bug tracking (log all issues)
- [ ] UAT sign-off (stakeholders approve)

**Technical Notes:**
- Use staging environment
- Invite 3-5 users for UAT

**Dependencies:** All MVP stories (Sprint 1-7)

---

#### STORY-UAT-002: Performance Testing (Load + Stress)
**Priority:** Must Have
**Points:** 3
**Sprint:** Sprint 13

**User Story:**
As an ops engineer, I want performance testing results, so I know system handles production load.

**Acceptance Criteria:**
- [ ] Load testing: 100 concurrent users × 10 req/min = 1000 req/min
- [ ] Stress testing: Gradually increase to 200 users (find breaking point)
- [ ] Metrics measured:
  - P50, P95, P99 latency
  - Error rate
  - Throughput (req/sec)
- [ ] Performance targets met:
  - P95 <200ms
  - Error rate <1%
  - No crashes under load
- [ ] Performance report generated

**Technical Notes:**
- Tool: `k6` (load testing tool)
- Test scenarios: Task CRUD, notifications, reconciliation

**Dependencies:** STORY-UAT-001

---

#### STORY-UAT-003: Security Audit & Penetration Testing
**Priority:** Must Have
**Points:** 3
**Sprint:** Sprint 13

**User Story:**
As a security officer, I want security audit passed, so we deploy safely to production.

**Acceptance Criteria:**
- [ ] Security audit checklist:
  - Authentication (JWT validation)
  - Authorization (RBAC enforcement)
  - Input validation (SQL injection, XSS)
  - HTTPS enforced
  - Secrets management (no hardcoded keys)
- [ ] Penetration testing (automated + manual)
- [ ] Vulnerabilities fixed (all critical + high severity)
- [ ] Security report generated

**Technical Notes:**
- Tools: OWASP ZAP, Burp Suite (manual testing)
- Fix all vulnerabilities before launch

**Dependencies:** STORY-UAT-001

---

#### STORY-LAUNCH-001: Training Sessions (3 Sessions)
**Priority:** Must Have
**Points:** 2
**Sprint:** Sprint 13

**User Story:**
As an admin user, I want training sessions, so I know how to use the system effectively.

**Acceptance Criteria:**
- [ ] 3 training sessions scheduled:
  - Session 1: Admin features (tasks, workflows, budget)
  - Session 2: Reviewer features (My Tasks, SLA, fraud detection)
  - Session 3: Advanced features (reconciliation, monitoring)
- [ ] Training materials (slides, demo videos)
- [ ] Q&A session
- [ ] Feedback collected

**Technical Notes:**
- Duration: 1-2 hours each
- Record sessions for future reference

**Dependencies:** STORY-DOCS-002

---

#### STORY-LAUNCH-002: Production Deployment (Blue-Green)
**Priority:** Must Have
**Points:** 5
**Sprint:** Sprint 14

**User Story:**
As an ops engineer, I want blue-green deployment, so we can rollback quickly if issues occur.

**Acceptance Criteria:**
- [ ] Blue-green deployment strategy:
  - Deploy to "green" environment (new version)
  - Run smoke tests on green
  - Switch traffic to green (via load balancer)
  - Keep blue running (old version) for 24h
  - If issues → Rollback to blue
  - If stable → Decommission blue
- [ ] Database migration executed (with rollback plan)
- [ ] Health checks passing
- [ ] Smoke tests passing (critical paths)
- [ ] Monitoring enabled (Sentry, health dashboard)

**Technical Notes:**
- Load balancer: Nginx (switch upstream)
- Rollback time: <5 minutes

**Dependencies:** All stories

---

#### STORY-LAUNCH-003: Production Launch + Stabilization (Week 1)
**Priority:** Must Have
**Points:** 5
**Sprint:** Sprint 14

**User Story:**
As a product owner, I want stable production launch, so users can start using the system confidently.

**Acceptance Criteria:**
- [ ] Production launch communication (email to users)
- [ ] Real campaign launched (not pilot)
- [ ] Monitor metrics for 1 week:
  - Uptime (target: >99.5%)
  - Error rate (target: <1%)
  - Performance (P95 <200ms)
  - User adoption (tasks created, notifications sent)
- [ ] Hotfix process ready (if critical bugs found)
- [ ] On-call rotation setup
- [ ] Incident response plan activated

**Technical Notes:**
- Monitor 24/7 for first week
- Quick response to user feedback

**Dependencies:** STORY-LAUNCH-002

---

#### STORY-LAUNCH-004: Post-Launch Retrospective + Optimization
**Priority:** Must Have
**Points:** 2
**Sprint:** Sprint 14

**User Story:**
As a team, we want retrospective session, so we learn what went well và what to improve.

**Acceptance Criteria:**
- [ ] Retrospective meeting (2 hours)
- [ ] Topics discussed:
  - What went well?
  - What could be improved?
  - Action items for next phase
- [ ] Collect success metrics:
  - Campaign cycle time (actual vs target)
  - SLA compliance rate
  - Auto-reconciliation rate
  - User satisfaction (survey)
- [ ] Optimization backlog created (for Phase 2)

**Technical Notes:**
- Document learnings in `/docs/retrospective.md`

**Dependencies:** STORY-LAUNCH-003

---

#### STORY-LAUNCH-005: Handoff to Maintenance Team
**Priority:** Must Have
**Points:** 2
**Sprint:** Sprint 14

**User Story:**
As a developer, I want smooth handoff to maintenance team, so they can support the system long-term.

**Acceptance Criteria:**
- [ ] Knowledge transfer sessions (2 sessions):
  - Session 1: Architecture & codebase walkthrough
  - Session 2: Operations & troubleshooting
- [ ] All documentation updated and accessible
- [ ] Runbooks tested by maintenance team
- [ ] On-call rotation handed over
- [ ] Support Slack channel setup

**Technical Notes:**
- Maintenance team: TCB ops team or AT team

**Dependencies:** All documentation stories

---

## Sprint Allocation - CHI TIẾT

### Sprint 0 (Week 1-2): Notification System Module (Standalone)
**Goal:** Build notification system như một module độc lập, reusable cho 4 projects

**Stories:**
- STORY-NOT-001: Notification Domain Model & Repository (5 SP)
- STORY-NOT-002: Telegram Bot Integration với Inline Buttons (5 SP)
- STORY-NOT-003: SendGrid Email Integration với Templates (3 SP)
- STORY-NOT-004: WebSocket In-App Notifications (5 SP)
- STORY-NOT-005: Notification Service API + Testing (2 SP)

**Total:** 20 SP / 20 capacity (100% utilization)

**Risks:**
- External service dependencies (Telegram, SendGrid) → Use mocks in tests
- WebSocket complexity → Reuse existing Socket.io knowledge

**Dependencies:** None (standalone module)

---

### Sprint 1 (Week 3-4): Task Engine Core + Infrastructure
**Goal:** Task management foundation + integrate notification module

**Stories:**
- STORY-TASK-001: Development Environment + Infrastructure Setup (5 SP)
- STORY-TASK-002: Authentication & Authorization (JWT + RBAC) (5 SP)
- STORY-TASK-003: Task Domain Model + State Machine (3 SP)
- STORY-TASK-004: Task Repository + MongoDB Implementation (3 SP)
- STORY-TASK-005: Task CRUD API (RESTful Endpoints) (4 SP)

**Total:** 20 SP / 20 capacity (100% utilization)

**Outcome:**
- Development environment ready
- Task CRUD working end-to-end
- Authentication secured
- Foundation for Sprint 2

**Dependencies:** Sprint 0 (notification module ready to integrate)

---

### Sprint 2 (Week 5-6): Task UI + Auto-Assignment
**Goal:** Complete task management MVP với UI và auto-assignment

**Stories:**
- STORY-TASK-006: Auto-Assignment Algorithm (Least-Loaded) (5 SP)
- STORY-TASK-007: My Tasks Dashboard (Frontend - List View) (5 SP)
- STORY-TASK-008: Task Detail Page (Frontend) (3 SP)
- STORY-TASK-009: Manual Task Creation Form (Frontend + Backend) (3 SP)
- STORY-TASK-010: Bulk Task Creation (CSV Import) (3 SP) - Defer to backlog if time runs out

**Total:** 19 SP / 20 capacity (95% utilization)

**Outcome:**
- Reviewers can see assigned tasks
- Tasks auto-assigned fairly
- Manual task creation working
- **First usable MVP** (basic task management)

**Dependencies:** Sprint 1

---

### Sprint 3 (Week 7-8): SLA Tracking + Auto-Task Creation
**Goal:** SLA monitoring, escalation, workflow foundation

**Stories:**
- STORY-SLA-001: SLA Configuration per Task Type (3 SP)
- STORY-SLA-002: SLA Monitoring Background Job (Asynq) (5 SP)
- STORY-SLA-003: SLA Dashboard & Reports (Frontend + Backend) (5 SP)
- STORY-SLA-004: SLA Escalation Workflow (3 SP)
- STORY-SLA-005: Auto-Task Creation from Business Events (4 SP)

**Total:** 20 SP / 20 capacity (100% utilization)

**Outcome:**
- SLA compliance tracking live
- Warnings sent before deadlines
- Tasks auto-created from events
- **Key automation milestone**

**Dependencies:** Sprint 2

---

### Sprint 4 (Week 9-10): Workflow Engine Foundation
**Goal:** Workflow orchestration với parallel execution

**Stories:**
- STORY-WORKFLOW-001: Workflow Engine Foundation (State Management) (5 SP)
- STORY-WORKFLOW-002: Parallel Workflow Execution (Parallel Gateway) (5 SP)
- STORY-WORKFLOW-003: Conditional Workflow Routing (Decision Gateway) (3 SP)

**Total:** 13 SP / 20 capacity (65% utilization)
**Buffer:** 7 SP for bug fixes, tech debt, or pull forward Sprint 5 stories

**Outcome:**
- Workflow engine working
- Parallel tasks execute simultaneously
- Foundation for complex workflows

**Dependencies:** Sprint 3

---

### Sprint 5 (Week 11-12): Budget Tracking & Controls
**Goal:** Budget dashboard + controls + auto-pause

**Stories:**
- STORY-BUDGET-001: Budget Dashboard (Real-Time Metrics) (5 SP)
- STORY-BUDGET-002: Budget Control Enforcement (Before Approval) (5 SP)
- STORY-BUDGET-003: Auto-Pause Campaign on Budget Exhaustion (3 SP)
- STORY-BUDGET-004: Budget Alerts (80%, 95% Thresholds) (2 SP)

**Total:** 15 SP / 20 capacity (75% utilization)
**Buffer:** 5 SP for testing, polish

**Outcome:**
- Budget tracking real-time
- Overspend prevention automated
- Finance team visibility

**Dependencies:** Sprint 2 (Task system), Sprint 0 (Notifications)

---

### Sprint 6 (Week 13-14): Auto-Reconciliation System
**Goal:** 90% auto-reconciliation + flagged review UI

**Stories:**
- STORY-RECON-001: Auto-Match Algorithm (URL Matching + Discrepancy) (8 SP)
- STORY-RECON-002: Flagged Items Review Dashboard (Frontend) (5 SP)
- STORY-RECON-003: Reconciliation Audit Trail (3 SP)
- STORY-RECON-004: Reconciliation Background Job (Daily Batch) (4 SP)

**Total:** 20 SP / 20 capacity (100% utilization)

**Outcome:**
- Reconciliation time 2-4 days → 4 hours
- 90% auto-approved
- Admins review only 10% exceptions
- **Biggest time saver delivered**

**Dependencies:** Sprint 3 (Auto-task creation)

---

### Sprint 7 (Week 15-16): MVP Integration Testing + Bug Fixes
**Goal:** Integration testing, polish, prepare for pilot launch

**Stories:**
- Integration testing all features (Sprint 0-6)
- Bug fixes from testing
- Performance optimization
- UX polish

**Total:** ~16 SP (bug fixes, testing, polish)

**Outcome:**
- **MVP READY for pilot campaign**
- All critical bugs fixed
- Performance targets met
- User-facing features polished

**Milestone:** 🎯 **MVP Launch Ready** (Week 16)

---

### Sprint 8 (Week 17-18): Fraud Detection (Rule-Based)
**Goal:** Rule-based fraud detection + blacklist management

**Stories:**
- STORY-FRAUD-001: Rule-Based Fraud Detection (4 Rules) (5 SP)
- STORY-FRAUD-002: Blacklist Management (CRUD + Auto-Block) (3 SP)
- STORY-FRAUD-003: Fraud Detection Dashboard (Analytics) (3 SP)
- STORY-FRAUD-005: Fraud Alerts (High-Risk Submissions) (2 SP)

**Total:** 13 SP / 20 capacity (65% utilization)
**Buffer:** 7 SP for UAT support, bug fixes

**Outcome:**
- Fraud detection live
- Blacklist preventing repeat offenders
- Fraud analytics dashboard

**Dependencies:** Sprint 2 (Task system)

---

### Sprint 9 (Week 19-20): Parallel Workflows + Templates
**Goal:** Workflow templates + visual workflow management

**Stories:**
- STORY-WORKFLOW-005: 4 Pre-Defined Workflow Templates (5 SP)
- STORY-WORKFLOW-006: Clone & Customize Workflow Template (UI) (3 SP)
- STORY-WORKFLOW-007: Workflow Execution Logs & Debugging (2 SP)

**Total:** 10 SP / 20 capacity (50% utilization)
**Buffer:** 10 SP for advanced features or defer to backlog

**Outcome:**
- Workflow templates reusable
- Admins can customize workflows
- Workflow debugging easier

**Dependencies:** Sprint 4 (Workflow engine)

---

### Sprint 10 (Week 21-22): Advanced Notifications + Preferences
**Goal:** Notification preferences, digest mode, analytics

**Stories:**
- STORY-NOT-006: Notification Preferences UI (User Settings) (3 SP)
- STORY-NOT-007: Notification Digest (Daily Summary Email) (3 SP)
- STORY-NOT-008: Notification Delivery Analytics (Dashboard) (2 SP)
- STORY-NOT-009: Notification Templates Editor (Admin UI) (3 SP)

**Total:** 11 SP / 20 capacity (55% utilization)
**Buffer:** 9 SP for polish, UX improvements

**Outcome:**
- Users control notification preferences
- Digest mode reduces notification fatigue
- Notification analytics for PM

**Dependencies:** Sprint 0 (Notification module)

---

### Sprint 11 (Week 23-24): ML Models (Budget Forecast + Fraud)
**Goal:** ML-based budget forecast + ML fraud detection

**Stories:**
- STORY-BUDGET-005: Budget Forecast ML Model (Basic Linear) (5 SP)
- STORY-FRAUD-004: ML-Based Fraud Detection (Random Forest) (8 SP)

**Total:** 13 SP / 20 capacity (65% utilization)
**Buffer:** 7 SP (ML models often take longer)

**Outcome:**
- Budget forecast predicts overspend early
- ML fraud detection catches sophisticated fraud
- **AI-powered features live**

**Dependencies:** Sprint 5 (Budget), Sprint 8 (Fraud)

**Note:** ML models require labeled training data (may defer if data not ready)

---

### Sprint 12 (Week 25-26): Monitoring + Alerting + Backups
**Goal:** Production-ready monitoring, alerting, disaster recovery

**Stories:**
- STORY-MONITOR-001: System Health Dashboard (Backend + Frontend) (5 SP)
- STORY-MONITOR-002: Alert Rules & Notifications (PagerDuty + Telegram) (5 SP)
- STORY-MONITOR-003: Automated Backup & Restore (MongoDB + MinIO) (5 SP)
- STORY-MONITOR-004: Operational Runbooks (5 Runbooks) (3 SP)
- STORY-MONITOR-005: Error Tracking (Sentry Integration) (2 SP)

**Total:** 20 SP / 20 capacity (100% utilization)

**Outcome:**
- Monitoring dashboard live
- Critical alerts to PagerDuty
- Backups automated + tested
- Runbooks ready for on-call
- **Production operations ready**

**Dependencies:** All previous sprints (monitoring needs all features)

---

### Sprint 13 (Week 27-28): Documentation + UAT + Training
**Goal:** Documentation, UAT, training, prepare for production launch

**Stories:**
- STORY-DOCS-001: API Documentation (OpenAPI/Swagger) (3 SP)
- STORY-DOCS-002: User Guide với Screenshots (3 SP)
- STORY-DOCS-003: Architecture & Deployment Guide (3 SP)
- STORY-UAT-001: UAT với Pilot Campaign (Testing) (5 SP)
- STORY-UAT-002: Performance Testing (Load + Stress) (3 SP)
- STORY-UAT-003: Security Audit & Penetration Testing (3 SP)
- STORY-LAUNCH-001: Training Sessions (3 Sessions) (2 SP)

**Total:** 22 SP / 20 capacity (110% over)
**Adjustment:** Defer STORY-UAT-003 to Sprint 14 if needed

**Outcome:**
- Documentation complete
- UAT passed
- Security audit passed
- Training completed
- **Launch-ready checklist completed**

**Dependencies:** All features complete

---

### Sprint 14 (Week 29-30): Production Launch + Stabilization
**Goal:** Production deployment, stabilization, handoff

**Stories:**
- STORY-UAT-003: Security Audit & Penetration Testing (3 SP) - If deferred from Sprint 13
- STORY-LAUNCH-002: Production Deployment (Blue-Green) (5 SP)
- STORY-LAUNCH-003: Production Launch + Stabilization (Week 1) (5 SP)
- STORY-LAUNCH-004: Post-Launch Retrospective + Optimization (2 SP)
- STORY-LAUNCH-005: Handoff to Maintenance Team (2 SP)

**Total:** 17 SP / 20 capacity (85% utilization)

**Outcome:**
- 🚀 **PRODUCTION LAUNCH**
- System stable after 1 week
- Retrospective completed
- Handoff to maintenance team
- **Project complete!**

**Milestone:** 🎉 **FULL LAUNCH** (Week 30)

---

## Epic Traceability

| Epic ID | Epic Name | Stories | Total SP | Sprints |
|---------|-----------|---------|----------|---------|
| EPIC-003 | Notification System | NOT-001 to NOT-009 | 29 SP | Sprint 0, 10 |
| EPIC-001 | Task Queue & Assignment | TASK-001 to TASK-010 | 39 SP | Sprint 1-2 |
| EPIC-002 | SLA Tracking & Escalation | SLA-001 to SLA-005 | 20 SP | Sprint 3 |
| EPIC-004 | Workflow Orchestration | WORKFLOW-001 to WORKFLOW-007 | 23 SP | Sprint 4, 9 |
| EPIC-005 | Budget Tracking & Controls | BUDGET-001 to BUDGET-005 | 20 SP | Sprint 5, 11 |
| EPIC-007 | Auto-Reconciliation | RECON-001 to RECON-004 | 20 SP | Sprint 6 |
| EPIC-006 | Fraud Detection | FRAUD-001 to FRAUD-005 | 21 SP | Sprint 8, 11 |
| EPIC-008 | Monitoring & BC | MONITOR-001 to MONITOR-005 | 20 SP | Sprint 12 |
| Documentation & Launch | DOCS, UAT, LAUNCH | 32 SP | Sprint 13-14 |
| Testing & Polish | Integration, bug fixes | 16 SP | Sprint 7 |
| **TOTALS** | **8 Epics + Docs** | **72 stories** | **288 SP** | **14 sprints** |

---

## Requirements Coverage

All 32 Functional Requirements covered:

**EPIC-001 (Task Management):**
- ✅ FR-001: Task Domain Model (STORY-TASK-003)
- ✅ FR-002: Task State Machine (STORY-TASK-003)
- ✅ FR-003: Task CRUD API (STORY-TASK-005)
- ✅ FR-004: Auto-Assignment (STORY-TASK-006)
- ✅ FR-005: My Tasks Dashboard (STORY-TASK-007, 008)
- ✅ FR-006: Manual Task Creation (STORY-TASK-009, 010)

**EPIC-002 (SLA):**
- ✅ FR-007: SLA Configuration (STORY-SLA-001)
- ✅ FR-008: SLA Monitoring (STORY-SLA-002)
- ✅ FR-009: SLA Escalation (STORY-SLA-004)
- ✅ FR-010: SLA Dashboard (STORY-SLA-003)

**EPIC-003 (Notifications):**
- ✅ FR-011: Multi-Channel Delivery (STORY-NOT-002, 003, 004)
- ✅ FR-012: Telegram Inline Actions (STORY-NOT-002)
- ✅ FR-013: In-App Notification Center (STORY-NOT-004)
- ✅ FR-014: Notification Preferences (STORY-NOT-006, 007)

**EPIC-004 (Workflow):**
- ✅ FR-015: Auto-Task Creation (STORY-SLA-005)
- ✅ FR-016: Parallel Execution (STORY-WORKFLOW-002)
- ✅ FR-017: Conditional Routing (STORY-WORKFLOW-003)
- ✅ FR-018: Workflow Templates (STORY-WORKFLOW-005, 006)

**EPIC-005 (Budget):**
- ✅ FR-019: Budget Dashboard (STORY-BUDGET-001)
- ✅ FR-020: Budget Controls (STORY-BUDGET-002)
- ✅ FR-021: Auto-Pause (STORY-BUDGET-003)
- ✅ FR-022: Budget Forecast ML (STORY-BUDGET-005)

**EPIC-006 (Fraud):**
- ✅ FR-023: Rule-Based Fraud (STORY-FRAUD-001)
- ✅ FR-024: ML Fraud (STORY-FRAUD-004)
- ✅ FR-025: Blacklist (STORY-FRAUD-002)

**EPIC-007 (Reconciliation):**
- ✅ FR-026: Auto-Match (STORY-RECON-001)
- ✅ FR-027: Flagged Dashboard (STORY-RECON-002)
- ✅ FR-028: Audit Trail (STORY-RECON-003)

**EPIC-008 (Monitoring):**
- ✅ FR-029: Health Dashboard (STORY-MONITOR-001)
- ✅ FR-030: Alert Rules (STORY-MONITOR-002)
- ✅ FR-031: Backup/Restore (STORY-MONITOR-003)
- ✅ FR-032: Runbooks (STORY-MONITOR-004)

---

## Risks & Mitigation

### High Risks

**1. Single Developer Resource**
- **Risk:** If developer unavailable (sick, vacation) → Timeline delays
- **Mitigation:** Build 20% buffer into sprints, document everything for easy handoff
- **Impact:** High (could add 2-4 weeks)

**2. ML Models Complexity**
- **Risk:** Budget forecast + Fraud ML may take longer than estimated (8+5=13 SP)
- **Mitigation:** Use simple models first (linear regression), defer advanced models
- **Impact:** Medium (could defer to post-MVP)

**3. External API Dependencies**
- **Risk:** Content Catcher API, Telegram, SendGrid outages during development
- **Mitigation:** Mock all external services, integration tests only in staging
- **Impact:** Low (mocks prevent blocking)

**4. Scope Creep**
- **Risk:** Stakeholders request new features mid-development
- **Mitigation:** Strict change control, defer to backlog unless critical
- **Impact:** Medium (could add 1-2 sprints)

### Medium Risks

**5. Performance Bottlenecks**
- **Risk:** Auto-reconciliation 1000 items might be slow
- **Mitigation:** Performance testing in Sprint 6, optimize before MVP
- **Impact:** Medium (optimization time)

**6. MongoDB Indexing Issues**
- **Risk:** Queries slow as data grows
- **Mitigation:** Create all 8 indexes upfront, monitor slow queries
- **Impact:** Low (indexes solve most issues)

### Low Risks

**7. Notification Delivery Failures**
- **Risk:** Telegram/SendGrid rate limits or quota exceeded
- **Mitigation:** Retry logic, rate limiting, queue batching
- **Impact:** Low (handled by design)

---

## Definition of Done

For a story to be considered **complete**:

- [ ] Code implemented and committed to main branch
- [ ] Unit tests written and passing (≥80% coverage for that story)
- [ ] Integration tests passing (if applicable)
- [ ] Code reviewed (self-review checklist for solo dev)
- [ ] Documentation updated (API docs, code comments)
- [ ] Deployed to staging environment
- [ ] Manual testing completed (happy path + edge cases)
- [ ] No critical bugs
- [ ] Acceptance criteria validated (all checkboxes checked)

---

## Next Steps

### Immediate Actions (This Week)

1. **Review & Approve Sprint Plan**
   - Stakeholder review (Product Owner, Finance, Ops)
   - Confirm team capacity assumptions
   - Adjust if needed

2. **Prepare Sprint 0 (Notification Module)**
   - Setup project structure: `accesstrade-projects/shared-modules/notification-system/`
   - Create Telegram Bot (get token from @BotFather)
   - Setup SendGrid account (free tier: 100 emails/day)
   - Setup MongoDB + Redis for notification storage

3. **Kick Off Sprint 0 (Week 1-2)**
   - Daily stand-ups (self-check-in for solo dev)
   - Build STORY-NOT-001 (Domain model) first
   - Parallelize Telegram + Email + WebSocket (can work sequentially)

### Recommended Next Workflow

**After completing Sprint 0-1:**
- Run `/bmad:dev-story STORY-NOT-001` to start implementing first story
- Or run `/watzup` to review progress and get recommendations

### Sprint Cadence

- **Sprint length:** 2 tuần
- **Sprint planning:** Monday Week 1 (review plan, prioritize)
- **Daily check-in:** 15 min self-reflection (what done, what next, blockers)
- **Sprint review:** Friday Week 2 (demo features, update status)
- **Sprint retro:** Friday Week 2 (what went well, what to improve)

---

## Success Metrics Tracking

Track these metrics throughout implementation:

**Development Velocity:**
- Story Points completed per sprint (target: 20 SP)
- Sprint goal achievement rate (target: >80%)
- Bug rate (bugs found per sprint, target: <5)

**Quality Metrics:**
- Code coverage (target: >80%)
- Production bugs (target: <2 per month after launch)
- Performance (P95 latency, target: <200ms)

**Business Metrics (Post-Launch):**
- Campaign cycle time (target: <5 days)
- SLA compliance (target: >85%)
- Auto-reconciliation rate (target: >90%)
- User satisfaction (survey, target: >8/10)

---

## Appendix: Story Point Reference Guide

**1 SP (1-2 hours):**
- Config change, text update, simple validation

**2 SP (2-4 hours):**
- Basic CRUD endpoint, simple component, add index

**3 SP (4-8 hours):**
- Complex component with state, business logic, integration test

**5 SP (1-2 days):**
- Feature với frontend + backend, complex logic, full testing

**8 SP (2-3 days):**
- Complete user flow, multiple components, external integration

**13 SP (3-5 days):**
- TOO BIG - Break it down!

---

**This Sprint Plan was created using BMAD Method v6 - Phase 4 (Sprint Planning)**

*To continue: Run `/bmad:dev-story STORY-NOT-001` to start implementing, or `/bmad:workflow-status` to check progress.*

---

**END OF SPRINT PLAN**
