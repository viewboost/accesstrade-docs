# System Architecture: Task Management & Workflow Automation System

**Date:** 2026-02-05
**Architect:** System Architect (BMAD Method)
**Version:** 1.0
**Project Type:** Task Management & Workflow Orchestration Platform
**Project Level:** Level 4 (Complex, Multi-Epic, 17-week implementation)
**Status:** Draft - Ready for Review

---

## Document Overview

This document defines the system architecture for the **Task Management & Workflow Automation System**. It provides the technical blueprint for implementation, addressing all 32 functional requirements and 12 non-functional requirements from the PRD.

**Critical Design Principle:** **Reusability-First Architecture** - System designed để tái sử dụng cho 4 projects (TCB, Ambassador, Influence Meter, Social Crawler) với 60-70% code reuse target.

**Related Documents:**
- Product Requirements Document: `/accesstrade-projects/docs/operation-optimize/prd-task-management-system.md`
- Brainstorming Session (Reusability): `/accesstrade-projects/techcombank/.bmad/brainstorming-task-management-reusability-20260205.md`

---

## Executive Summary

### Architecture Philosophy

Hệ thống được thiết kế theo **3-Layer Reusable Architecture Pattern**:
- 🟢 **Core Layer (70% - Fully Reusable)**: Domain models, business logic, interfaces
- 🟡 **Adapter Layer (20% - Pluggable)**: Storage, notifications, events - implement interfaces
- 🔴 **Specific Layer (10% - Per-Project)**: Custom task types, workflows, validation rules

### Key Architectural Decisions

1. **Modular Monolith** (not Microservices)
   - **Why**: Simpler deployment, faster iteration, adequate cho Level 4 project
   - **When to change**: Khi có ≥3 projects + need centralized monitoring

2. **Embedded Workflow Engine** (not Temporal/n8n)
   - **Why**: Full control, zero dependencies, adequate for requirements
   - **Future**: Can add Workflow-as-Code (YAML) layer sau

3. **MongoDB + Redis + Go + React**
   - **Why**: Match existing TCB stack, team expertise, proven performance
   - **Benefit**: No learning curve, reuse infrastructure

4. **Interface-Driven Design**
   - **Why**: Enable swapping implementations (MongoDB → Postgres, Telegram → Slack)
   - **Benefit**: Testability (mock everything), flexibility

5. **Phased Extraction Strategy**
   - **Phase 1 (Week 1-4)**: Build TCB-specific, structure cho reusability
   - **Phase 2 (Week 5-8)**: Extract to `pkg/taskengine` library
   - **Phase 3 (Week 9+)**: Scale to 3+ projects, evaluate microservice

### Architecture Highlights

- **Components**: 8 major components (Task Engine, SLA Monitor, Notification Hub, Workflow Orchestrator, Budget Controller, Fraud Detector, Reconciliation Engine, Support Integration)
- **APIs**: RESTful (primary), WebSocket (real-time), gRPC (future inter-service)
- **Database**: MongoDB (tasks, workflows), Redis (queue, cache), PostgreSQL (analytics - optional)
- **Deployment**: Docker containers, horizontal scaling, blue-green deployment
- **Monitoring**: Sentry (errors), Prometheus (metrics), Grafana (dashboards)

---

## Architectural Drivers

These NFRs heavily influence architectural decisions:

### 1. **Reusability (NEW - From Brainstorming)**
**Target**: 60-70% code reuse across 4 projects

**Architecture Solution**:
- 3-Layer separation (Core/Adapter/Specific)
- Interface-driven design (8 core interfaces)
- Phased extraction strategy
- Library-first approach (`pkg/taskengine`)

**Validation**: Measure code duplication % after extracting library

---

### 2. **NFR-001: API Response Time (P95 < 200ms)**
**Requirement**: API response times: P50 <100ms, P95 <200ms, P99 <500ms

**Architecture Solution**:
- **Caching layer**: Redis cho hot data (task lists, user info)
- **Database indexing**: 8 strategic indexes on tasks collection
- **Query optimization**: Pagination (limit 50), projection (select needed fields only)
- **Async processing**: Background jobs cho notifications, SLA checks

**Validation**: Load testing 1000 RPS, measure P95

---

### 3. **NFR-003: Concurrent Users (100 users)**
**Requirement**: Support 100 concurrent users without degradation

**Architecture Solution**:
- **Horizontal scaling**: Stateless API servers, scale to 3-5 instances
- **Connection pooling**: MongoDB pool size 100, Redis pool 50
- **Load balancer**: Nginx round-robin
- **Session management**: JWT tokens (stateless), no server-side sessions

**Validation**: Load test 100 concurrent users × 10 req/min

---

### 4. **NFR-005: Authentication & Authorization (JWT + RBAC)**
**Requirement**: JWT authentication, role-based access control

**Architecture Solution**:
- **JWT tokens**: 24h expiry, RS256 signing
- **RBAC middleware**: Check roles before API calls
- **Roles**: Admin (full), Reviewer (assigned tasks only), Creator (read-only)
- **API security**: HTTPS only, CORS enabled

**Validation**: Penetration testing, security audit

---

### 5. **NFR-007: Uptime SLA (99.5%)**
**Requirement**: 99.5% monthly uptime (max 3.6h downtime)

**Architecture Solution**:
- **High availability**: Multi-AZ deployment (2+ zones)
- **Health checks**: /health endpoint, Kubernetes liveness probes
- **Graceful degradation**: If Redis down, fallback to DB queries
- **Circuit breakers**: Prevent cascade failures

**Validation**: Uptime monitoring (UptimeRobot), monthly reports

---

### 6. **NFR-008: Disaster Recovery (RTO 1h, RPO 15min)**
**Requirement**: RTO 1 hour, RPO 15 minutes

**Architecture Solution**:
- **Automated backups**: MongoDB snapshots every 15 min
- **Backup storage**: AWS S3 (3 regions), retention 30 days
- **Restore procedure**: Documented runbook, tested monthly
- **Failover**: Automated MongoDB replica set failover

**Validation**: Monthly restore drill, measure RTO/RPO

---

### 7. **NFR-011: Code Quality (>80% test coverage)**
**Requirement**: >80% test coverage, clean code

**Architecture Solution**:
- **Layered testing**: Unit (85%), Integration (70%), E2E (50%)
- **Dependency injection**: All interfaces injected, mockable
- **CI enforcement**: Tests must pass before merge
- **Code review**: All PRs need 1 approval

**Validation**: Coverage reports, SonarQube quality gate

---

### 8. **NFR-002: Database Query Optimization**
**Requirement**: Fast queries (<50ms list, <5ms by ID)

**Architecture Solution**:
- **Strategic indexes**: 8 indexes on tasks collection
- **Query patterns**: Filter by status + assigned_to (compound index)
- **Pagination**: Cursor-based, limit 50 items/page
- **Explain plans**: Monitor slow queries, optimize

**Validation**: Query profiling, slow query logs

---

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TASK MANAGEMENT SYSTEM                            │
│                  (3-Layer Reusable Architecture)                     │
└─────────────────────────────────────────────────────────────────────┘

                   ┌─────────────────────────┐
                   │     CLIENT LAYER         │
                   ├──────────────────────────┤
                   │  Admin UI (React)        │
                   │  Creator Portal (React)  │
                   │  Mobile App (Future)     │
                   └───────────┬──────────────┘
                               │ HTTPS/WSS
                   ┌───────────▼──────────────┐
                   │   API GATEWAY            │
                   │  (Nginx + Auth)          │
                   └───────────┬──────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
┌───────▼──────┐      ┌────────▼───────┐    ┌────────▼────────┐
│ 🟢 CORE      │      │ 🟡 ADAPTER     │    │ 🔴 SPECIFIC    │
│ (Reusable)   │◄────►│ (Pluggable)    │◄───│ (Per-Project)  │
└───────┬──────┘      └────────┬───────┘    └────────┬────────┘
        │                      │                      │
        │                      │                      │
  ┌─────▼──────────────────────▼──────────────────────▼──────┐
  │              APPLICATION CORE LAYER                        │
  ├────────────────────────────────────────────────────────────┤
  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐ │
  │  │ Task Engine  │  │ Workflow     │  │ Budget          │ │
  │  │              │  │ Orchestrator │  │ Controller      │ │
  │  └──────────────┘  └──────────────┘  └─────────────────┘ │
  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐ │
  │  │ SLA Monitor  │  │ Notification │  │ Fraud           │ │
  │  │              │  │ Hub          │  │ Detector        │ │
  │  └──────────────┘  └──────────────┘  └─────────────────┘ │
  │  ┌──────────────┐  ┌──────────────┐                      │
  │  │Reconciliation│  │ Support      │                      │
  │  │ Engine       │  │ Integration  │                      │
  │  └──────────────┘  └──────────────┘                      │
  └─────────────────────────┬──────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼──────┐   ┌────────▼───────┐   ┌──────▼──────┐
│  MongoDB     │   │  Redis Queue   │   │  External   │
│  (Tasks DB)  │   │  (Asynq)       │   │  Services   │
└──────────────┘   └────────────────┘   └─────────────┘
                                         │ Telegram    │
                                         │ SendGrid    │
                                         │ Chatwoot    │
                                         └─────────────┘
```

### Architecture Diagram (3-Layer Detail)

```
pkg/taskengine/           ← 🟢 CORE (70% - Reusable)
├─ domain/
│   ├─ task.go            - Task entity, state machine
│   ├─ workflow.go        - Workflow definitions
│   ├─ sla.go             - SLA policies
│   ├─ assignment.go      - Assignment strategies
│   └─ events.go          - Domain events
├─ interfaces/
│   ├─ repository.go      - TaskRepository interface
│   ├─ notifier.go        - NotificationSender interface
│   ├─ publisher.go       - EventPublisher interface
│   ├─ assigner.go        - AssignmentStrategy interface
│   ├─ validator.go       - ValidationRule interface
│   └─ workflow.go        - WorkflowEngine interface
├─ statemachine/
│   ├─ transitions.go     - Valid state transitions
│   ├─ guards.go          - Transition guards
│   └─ hooks.go           - Lifecycle hooks
└─ services/
    ├─ task_service.go    - Core business logic
    ├─ sla_service.go     - SLA calculations
    └─ workflow_service.go- Workflow execution

pkg/taskengine/adapters/  ← 🟡 ADAPTERS (20% - Pluggable)
├─ storage/
│   ├─ mongodb/
│   │   ├─ repository.go  - MongoDB implementation
│   │   └─ indexes.go     - Index definitions
│   ├─ postgres/
│   │   └─ repository.go  - Postgres implementation (future)
│   └─ inmemory/
│       └─ repository.go  - In-memory (testing)
├─ notifiers/
│   ├─ telegram.go        - Telegram Bot API
│   ├─ email.go           - SendGrid integration
│   ├─ inapp.go           - WebSocket notifications
│   └─ mock.go            - Mock notifier (testing)
├─ events/
│   ├─ redis.go           - Redis Pub/Sub
│   ├─ kafka.go           - Kafka (future)
│   └─ local.go           - Local event bus (testing)
└─ assignment/
    ├─ leastloaded.go     - Least-loaded algorithm
    ├─ roundrobin.go      - Round-robin
    └─ skillbased.go      - Skill-based matching

projects/tcb/tasks/       ← 🔴 SPECIFIC (10% - TCB Custom)
├─ types.go               - ContentReviewTask, ReconciliationTask
├─ workflows.go           - CampaignWorkflow, ReconciliationWorkflow
├─ validators.go          - TCB-specific validation
└─ handlers.go            - HTTP handlers

projects/ambassador/tasks/ ← 🔴 SPECIFIC (10% - Ambassador Custom)
├─ types.go               - CampaignApprovalTask, PayoutTask
├─ workflows.go           - PayoutWorkflow
└─ validators.go          - Ambassador validation
```

### Architectural Pattern

**Pattern:** Modular Monolith with 3-Layer Separation

**Rationale:**
- **Simplicity**: Monolith deployment = simple ops, no microservice complexity
- **Performance**: No network calls between layers = low latency
- **Reusability**: Clear layer separation = easy to extract library
- **Team size**: 2 engineers (backend + frontend) = monolith is appropriate
- **Future-proof**: Can split to microservices later if needed (≥3 projects)

**Main System Components:**

1. **API Gateway** (Nginx)
   - Entry point, auth, routing, rate limiting

2. **Application Core** (8 components)
   - Task Engine, SLA Monitor, Notification Hub, Workflow Orchestrator
   - Budget Controller, Fraud Detector, Reconciliation Engine, Support Integration

3. **Data Layer**
   - MongoDB (tasks, workflows, users)
   - Redis (queues, cache, pub/sub)

4. **External Integrations**
   - Telegram, SendGrid, Chatwoot, Firebase, Content Catcher API

**Interaction Flow:**
```
Client → API Gateway → Auth Middleware → Application Core → Adapters → Storage
                                    ↓
                          Background Jobs (Asynq) → Notifications
```

---

## Technology Stack

### Frontend

**Choice:** React 18 + TypeScript + Tailwind CSS + shadcn/ui

**Rationale:**
- **React 18**: Current TCB stack, team expertise, rich ecosystem
- **TypeScript**: Type safety, better DX, catch errors compile-time
- **Tailwind CSS**: Utility-first, fast styling, consistent design
- **shadcn/ui**: High-quality components, accessible, customizable

**Trade-offs:**
- ✅ Gain: Fast development, component reusability
- ❌ Lose: Bundle size larger than vanilla JS (acceptable cho admin tool)

**Key Libraries:**
- **State management**: Zustand (simpler than Redux)
- **Forms**: React Hook Form + Zod validation
- **API client**: TanStack Query (react-query)
- **Routing**: React Router v6
- **Real-time**: Socket.io-client (WebSocket)
- **Charts**: Recharts (SLA dashboard)

---

### Backend

**Choice:** Go 1.21 + Gin (HTTP) + Asynq (background jobs)

**Rationale:**
- **Go**: Current TCB stack, excellent performance, strong typing
- **Gin**: Lightweight HTTP framework, fast routing, middleware support
- **Asynq**: Reliable background jobs, Redis-based, retry logic

**Trade-offs:**
- ✅ Gain: High performance, strong concurrency, compiled binary
- ❌ Lose: Smaller ecosystem than Node.js (acceptable)

**Key Libraries:**
- **HTTP framework**: Gin
- **Validation**: go-playground/validator
- **JWT**: golang-jwt/jwt
- **MongoDB driver**: mongo-go-driver
- **Redis**: go-redis/redis
- **Testing**: testify, gomock

---

### Database

**Primary: MongoDB 6.0 (Document Database)**

**Rationale:**
- **Current TCB stack**: Already running, team expertise
- **Flexible schema**: Tasks have dynamic metadata (JSON)
- **Query capabilities**: Rich queries, aggregation pipelines
- **Performance**: Fast reads, good for task queries

**Schema Design:**
```javascript
// tasks collection
{
  _id: ObjectId,
  title: String,
  type: String,          // content_review, reconciliation, etc.
  status: String,        // draft, assigned, in_progress, completed
  priority: String,      // low, medium, high, urgent
  assigned_to: ObjectId, // User ID
  created_at: Date,
  updated_at: Date,
  due_date: Date,
  completed_at: Date,
  sla_target: Number,    // minutes
  is_breached: Boolean,
  warning_sent: Boolean,
  metadata: Object,      // Flexible JSON (content_id, campaign_id, etc.)
  status_history: [{
    from: String,
    to: String,
    changed_by: ObjectId,
    changed_at: Date,
    reason: String
  }]
}
```

**Indexes (8 strategic indexes):**
```javascript
db.tasks.createIndex({ status: 1, assigned_to: 1 })  // Main query
db.tasks.createIndex({ due_date: 1, status: 1 })     // SLA monitoring
db.tasks.createIndex({ type: 1, created_at: -1 })    // Task type filtering
db.tasks.createIndex({ priority: 1 })                // Priority sorting
db.tasks.createIndex({ "metadata.campaign_id": 1 })  // Campaign tasks
db.tasks.createIndex({ "metadata.content_id": 1 })   // Content tasks
db.tasks.createIndex({ is_breached: 1 })             // Breached tasks
db.tasks.createIndex({ created_at: -1 })             // Recent tasks
```

**Trade-offs:**
- ✅ Gain: Flexible schema, fast queries, team expertise
- ❌ Lose: No ACID transactions across documents (acceptable cho task system)

---

**Secondary: Redis 7.0 (Cache + Queue + Pub/Sub)**

**Rationale:**
- **Caching**: Hot data (task lists, user info) → reduce DB load
- **Queue**: Asynq background jobs (notifications, SLA checks)
- **Pub/Sub**: Real-time events (task updates → WebSocket clients)

**Usage:**
```
Cache Layer:
- task:list:{user_id}:{status} → TTL 5 min
- user:info:{user_id} → TTL 1 hour

Queue:
- asynq:default → Notifications, SLA checks
- asynq:critical → Budget alerts, fraud alerts

Pub/Sub:
- task:created:{campaign_id}
- task:updated:{task_id}
- notification:sent:{user_id}
```

---

### Infrastructure

**Choice:** Docker + Kubernetes (optional) / Docker Compose (simple)

**Rationale:**
- **Docker**: Consistent environments, easy deployment
- **Kubernetes**: IF need auto-scaling (100+ users) → Overkill cho start
- **Docker Compose**: Adequate cho 2-5 servers

**Deployment Architecture:**
```
┌─────────────────────────────────────────┐
│         Load Balancer (Nginx)            │
│         - HTTPS termination              │
│         - Round-robin routing            │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
┌──────▼──────┐ ┌──────▼──────┐
│ API Server 1│ │ API Server 2│ (Horizontal scaling)
│ (Docker)    │ │ (Docker)    │
└──────┬──────┘ └──────┬──────┘
       │               │
       └───────┬───────┘
               │
┌──────────────▼──────────────────┐
│      MongoDB Replica Set         │
│      - Primary (write)           │
│      - Secondary 1 (read)        │
│      - Secondary 2 (read)        │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│         Redis Cluster            │
│         - Master (write)         │
│         - Replica (read)         │
└──────────────────────────────────┘
```

**Cost Estimate (Monthly):**
- API servers (2× VPS 4GB): $40
- MongoDB replica set (3× VPS 4GB): $60
- Redis (1× VPS 2GB): $10
- Load balancer: $10
- **Total: $120/month**

---

### Third-Party Services

**1. Telegram Bot API** (Notifications)
- **Cost**: Free
- **Why**: Instant notifications, inline buttons, high engagement
- **Rate limit**: 30 msg/sec (adequate)

**2. SendGrid** (Email)
- **Cost**: $20/month (100K emails)
- **Why**: Reliable delivery, templates, analytics
- **Backup**: AWS SES ($1/10K emails)

**3. Chatwoot** (Help Center)
- **Cost**: $20/month (self-hosted VPS)
- **Why**: Open-source, multi-channel, knowledge base
- **Integration**: Webhook → Task Engine

**4. Sentry** (Error Tracking)
- **Cost**: Free tier (5K events/month)
- **Why**: Real-time error alerts, stack traces

**5. AWS S3** (Backups)
- **Cost**: $5/month (100GB)
- **Why**: Reliable, cheap, multi-region

**Total Third-Party Cost: ~$50/month**

---

### Development & Deployment

**Version Control:** Git + GitHub

**CI/CD Pipeline:** GitHub Actions
```yaml
Pipeline stages:
1. Lint → golangci-lint (Go), ESLint (React)
2. Test → Unit tests (80%+ coverage)
3. Build → Docker image
4. Deploy → Blue-green deployment
```

**Testing Strategy:**
- **Unit tests**: 85% coverage (Go services, React components)
- **Integration tests**: 70% coverage (API endpoints, DB operations)
- **E2E tests**: 50% coverage (Critical flows: create task, approve content)
- **Load tests**: 1000 RPS, 100 concurrent users

**Monitoring:**
- **Metrics**: Prometheus (API latency, error rate, queue depth)
- **Dashboards**: Grafana (system health, SLA metrics)
- **Logging**: Structured logs (JSON), centralized (Loki)
- **Alerting**: PagerDuty (critical), Telegram (warnings)

---

## System Components

### Component 1: Task Engine (Core)

**Purpose:** Central task management - CRUD operations, state machine, assignment

**Responsibilities:**
- Create, read, update, delete tasks
- Enforce state machine transitions
- Auto-assign tasks to reviewers
- Track status history

**Interfaces:**
```go
type TaskRepository interface {
    Create(ctx context.Context, task *Task) error
    FindByID(ctx context.Context, id string) (*Task, error)
    Query(ctx context.Context, filters QueryFilters) ([]*Task, int64, error)
    Update(ctx context.Context, id string, updates map[string]interface{}) error
    Delete(ctx context.Context, id string) error
}

type TaskService interface {
    CreateTask(ctx context.Context, config TaskConfig) (*Task, error)
    AssignTask(ctx context.Context, taskID string, assigneeID string) error
    TransitionStatus(ctx context.Context, taskID string, newStatus Status) error
    ListTasks(ctx context.Context, filters TaskFilters) ([]*Task, error)
}
```

**Dependencies:**
- MongoDB (storage)
- Redis (cache)
- Event Publisher (emit task.created, task.updated events)

**FRs Addressed:** FR-001, FR-002, FR-003, FR-004, FR-005, FR-006

---

### Component 2: SLA Monitor (Background Worker)

**Purpose:** Track SLA deadlines, send warnings, escalate overdue tasks

**Responsibilities:**
- Background job every 5 minutes
- Find tasks approaching deadline (<24h)
- Send warning notifications
- Find overdue tasks, mark breached
- Auto-escalate tasks overdue >24h

**Implementation:**
```go
// Asynq periodic task
func (m *SLAMonitor) CheckSLAs(ctx context.Context) error {
    // Find tasks due in <24h, warning_sent=false
    tasks, _ := m.repo.Query(ctx, QueryFilters{
        DueBefore: time.Now().Add(24 * time.Hour),
        WarningSent: false,
    })

    for _, task := range tasks {
        m.notifier.Send(ctx, Notification{
            Type: "sla_warning",
            User: task.AssignedTo,
            Data: task,
        })
        m.repo.Update(ctx, task.ID, map[string]interface{}{
            "warning_sent": true,
        })
    }

    // Find overdue tasks
    overdue, _ := m.repo.Query(ctx, QueryFilters{
        DueBefore: time.Now(),
        IsBreached: false,
    })

    for _, task := range overdue {
        m.notifier.Send(ctx, Notification{
            Type: "sla_breach",
            User: task.AssignedTo,
        })
        m.repo.Update(ctx, task.ID, map[string]interface{}{
            "is_breached": true,
        })
    }

    return nil
}
```

**Dependencies:**
- Task Repository (queries)
- Notification Hub (send alerts)

**FRs Addressed:** FR-007, FR-008, FR-009

---

### Component 3: Notification Hub (Multi-Channel)

**Purpose:** Send notifications via Telegram, Email, In-app

**Responsibilities:**
- Route notifications to appropriate channels
- Retry failed deliveries (3 attempts)
- Track delivery status
- Respect user preferences (quiet hours, digest mode)

**Interfaces:**
```go
type NotificationSender interface {
    Send(ctx context.Context, notification Notification) error
    SendBatch(ctx context.Context, notifications []Notification) error
}

type Notification struct {
    Type     string // task_assigned, sla_warning, sla_breach
    Channel  string // telegram, email, inapp
    User     User
    Template string
    Data     map[string]interface{}
}
```

**Implementation Strategy:**
- **Priority queue**: Critical notifications (SLA breach) → High priority
- **Batching**: Digest mode → Batch 1 email/day with all notifications
- **Retry logic**: Exponential backoff (1s, 5s, 25s)

**Dependencies:**
- Telegram Bot API
- SendGrid API
- WebSocket server (in-app)

**FRs Addressed:** FR-011, FR-012, FR-013, FR-014

---

### Component 4: Workflow Orchestrator (Embedded Engine)

**Purpose:** Execute workflows, auto-create tasks from events, parallel execution

**Responsibilities:**
- Listen to business events (content.submitted, campaign.created)
- Execute workflow steps
- Support parallel gateways
- Support conditional routing

**Workflow Definition (In-Code - Phase 1):**
```go
// Example: Content Review Workflow
type ContentReviewWorkflow struct {
    taskEngine *TaskEngine
    notifier   NotificationSender
}

func (w *ContentReviewWorkflow) Execute(ctx context.Context, event Event) error {
    content := event.Data.(*Content)

    // Step 1: Create review task
    task, err := w.taskEngine.CreateTask(ctx, TaskConfig{
        Type:     "content_review",
        Title:    fmt.Sprintf("Review Content #%s", content.ID),
        Priority: content.IsUrgent ? "high" : "medium",
        Metadata: map[string]interface{}{
            "content_id": content.ID,
            "creator_id": content.CreatorID,
        },
    })
    if err != nil {
        return err
    }

    // Step 2: Notify assignee
    w.notifier.Send(ctx, Notification{
        Type: "task_assigned",
        User: task.AssignedTo,
        Data: task,
    })

    // Step 3: Wait for completion (handled by Task Engine)
    // Step 4: Update content status (event handler)

    return nil
}
```

**Future Enhancement (Phase 2):** Workflow-as-Code (YAML)
```yaml
name: Content Review Workflow
triggers:
  - event: content.submitted
steps:
  - id: create_task
    type: task.create
    params:
      type: content_review
      title: "Review Content #{{content.id}}"
  - id: notify
    type: notification.send
    depends_on: [create_task]
```

**Dependencies:**
- Task Engine (create tasks)
- Event Bus (subscribe to events)

**FRs Addressed:** FR-015, FR-016, FR-017, FR-018

---

### Component 5: Budget Controller

**Purpose:** Track budget, enforce limits, auto-pause campaigns

**Responsibilities:**
- Real-time budget tracking
- Check budget before approvals
- Auto-pause at 100% utilization
- Forecast budget (ML model - Phase 3)

**Budget Check Logic:**
```go
func (b *BudgetController) CheckBudget(ctx context.Context, approval ContentApproval) error {
    campaign := b.getCampaign(approval.CampaignID)

    // Check 1: Campaign budget
    if campaign.Committed + approval.EstimatedReward > campaign.Budget {
        return errors.New("Campaign budget exceeded")
    }

    // Check 2: Creator cap
    creatorSpend := b.getCreatorSpend(approval.CreatorID, campaign.ID)
    if creatorSpend + approval.EstimatedReward > campaign.CreatorCap {
        return errors.New("Creator cap exceeded")
    }

    // Check 3: Daily platform limit
    todaySpend := b.getPlatformSpendToday()
    if todaySpend + approval.EstimatedReward > b.config.DailyLimit {
        return errors.New("Platform daily limit exceeded")
    }

    return nil
}
```

**Auto-Pause Logic:**
```go
func (b *BudgetController) MonitorBudgets(ctx context.Context) {
    campaigns := b.getActiveCampaigns()

    for _, campaign := range campaigns {
        utilization := campaign.Committed / campaign.Budget

        if utilization >= 1.0 {
            // Auto-pause
            b.pauseCampaign(campaign.ID, "BUDGET_EXHAUSTED")
            b.notifier.Send(ctx, Notification{
                Type: "budget_exhausted",
                Users: campaign.Stakeholders,
            })
        } else if utilization >= 0.95 {
            // Warning
            b.notifier.Send(ctx, Notification{
                Type: "budget_warning_95",
                Users: campaign.Stakeholders,
            })
        }
    }
}
```

**Dependencies:**
- Campaign service
- Notification Hub

**FRs Addressed:** FR-019, FR-020, FR-021, FR-022

---

### Component 6: Fraud Detector

**Purpose:** Detect fraudulent content submissions

**Responsibilities:**
- Rule-based checks (4 rules)
- Score fraud risk (0-3 flags)
- ML-based detection (Phase 3 - optional)
- Blacklist management

**Rule-Based Detection:**
```go
type FraudRule interface {
    Check(ctx context.Context, content *Content) (flagged bool, reason string)
}

// Rule 1: Abnormal view velocity
type ViewVelocityRule struct {
    Threshold int // 100,000 views/hour
}

func (r *ViewVelocityRule) Check(ctx context.Context, content *Content) (bool, string) {
    velocity := content.Views / content.HoursSincePosted
    if velocity > r.Threshold {
        return true, "SUSPICIOUS_VIEW_VELOCITY"
    }
    return false, ""
}

// Fraud scoring
func (f *FraudDetector) Score(ctx context.Context, content *Content) FraudScore {
    flags := []string{}

    for _, rule := range f.rules {
        if flagged, reason := rule.Check(ctx, content); flagged {
            flags = append(flags, reason)
        }
    }

    // Scoring logic
    score := FraudScore{
        Flags: flags,
        Count: len(flags),
    }

    if score.Count == 0 {
        score.Action = "auto_approve"
    } else if score.Count <= 2 {
        score.Action = "manual_review"
    } else {
        score.Action = "auto_reject"
    }

    return score
}
```

**Dependencies:**
- Content service (get content data)
- Blacklist repository

**FRs Addressed:** FR-023, FR-024, FR-025

---

### Component 7: Reconciliation Engine

**Purpose:** Auto-match submissions to crawled data, 90% automation

**Responsibilities:**
- URL matching algorithm
- Discrepancy calculation
- Auto-approve (<10% discrepancy)
- Flag for review (>10% discrepancy)

**Auto-Match Algorithm:**
```go
func (r *ReconciliationEngine) Reconcile(ctx context.Context, batch ReconciliationBatch) ReconciliationResult {
    result := ReconciliationResult{
        AutoApproved: 0,
        Flagged:      0,
    }

    for _, submission := range batch.Submissions {
        // Step 1: Find match in crawled data by URL
        crawled := r.findMatchByURL(submission.URL)

        if crawled == nil {
            // Flag: Not found
            r.flagSubmission(submission, "NOT_FOUND")
            result.Flagged++
            continue
        }

        // Step 2: Calculate discrepancy
        discrepancy := abs(submission.Views - crawled.Views) / float64(crawled.Views)

        if discrepancy < 0.10 {
            // Auto-approve
            r.approveSubmission(submission)
            result.AutoApproved++
        } else if discrepancy < 0.20 {
            // Flag for review
            r.flagSubmission(submission, "MEDIUM_DISCREPANCY")
            result.Flagged++
        } else {
            // Flag high discrepancy
            r.flagSubmission(submission, "HIGH_DISCREPANCY")
            result.Flagged++
        }
    }

    return result
}
```

**Performance Target:**
- 1000 items in <30 seconds
- 90% auto-match rate

**Dependencies:**
- Content Catcher API (crawled data)
- Submission repository

**FRs Addressed:** FR-026, FR-027, FR-028

---

### Component 8: Support Integration (Chatwoot)

**Purpose:** Integrate help center với task management

**Responsibilities:**
- Webhook handler (Chatwoot → Task Engine)
- Auto-create tasks from support tickets
- Update Chatwoot when task completed
- Track support metrics

**Webhook Handler:**
```go
func (h *ChatwootWebhook) HandleConversationUpdated(event ChatwootEvent) error {
    conv := event.Conversation

    // Check if labeled as "bug"
    if contains(conv.Labels, "bug") && !hasTask(conv) {
        // Create task
        task, err := h.taskEngine.CreateTask(ctx, TaskConfig{
            Type:     "bug_fix",
            Title:    conv.Subject,
            Priority: "high",
            Metadata: map[string]interface{}{
                "chatwoot_conversation_id": conv.ID,
                "user_email":               conv.Contact.Email,
            },
        })

        // Update Chatwoot
        h.chatwoot.UpdateConversation(conv.ID, map[string]interface{}{
            "custom_attributes": map[string]interface{}{
                "task_id": task.ID,
            },
        })

        // Notify user
        h.chatwoot.CreateMessage(conv.ID, &Message{
            Content: fmt.Sprintf("✅ Task #%s created!", task.ID),
        })
    }

    return nil
}
```

**Dependencies:**
- Chatwoot API
- Task Engine

**FRs Addressed:** Support & feedback loop (from brainstorming)

---

## Data Architecture

### Data Model

**Core Entities:**

1. **Task**
```go
type Task struct {
    ID            primitive.ObjectID `bson:"_id"`
    Title         string             `bson:"title"`
    Description   string             `bson:"description"`
    Type          string             `bson:"type"` // content_review, reconciliation, etc.
    Status        Status             `bson:"status"`
    Priority      Priority           `bson:"priority"`
    AssignedTo    primitive.ObjectID `bson:"assigned_to"`
    CreatedAt     time.Time          `bson:"created_at"`
    UpdatedAt     time.Time          `bson:"updated_at"`
    DueDate       time.Time          `bson:"due_date"`
    CompletedAt   *time.Time         `bson:"completed_at,omitempty"`
    SLATarget     int                `bson:"sla_target"` // minutes
    IsBreached    bool               `bson:"is_breached"`
    WarningSent   bool               `bson:"warning_sent"`
    Metadata      map[string]interface{} `bson:"metadata"` // Flexible
    StatusHistory []StatusChange     `bson:"status_history"`
}

type Status string
const (
    StatusDraft      Status = "draft"
    StatusAssigned   Status = "assigned"
    StatusInProgress Status = "in_progress"
    StatusBlocked    Status = "blocked"
    StatusCompleted  Status = "completed"
    StatusCancelled  Status = "cancelled"
)

type Priority string
const (
    PriorityLow    Priority = "low"
    PriorityMedium Priority = "medium"
    PriorityHigh   Priority = "high"
    PriorityUrgent Priority = "urgent"
)
```

2. **Workflow**
```go
type Workflow struct {
    ID        primitive.ObjectID `bson:"_id"`
    Name      string             `bson:"name"`
    Version   string             `bson:"version"`
    Triggers  []Trigger          `bson:"triggers"`
    Steps     []WorkflowStep     `bson:"steps"`
    Active    bool               `bson:"active"`
    CreatedAt time.Time          `bson:"created_at"`
}

type Trigger struct {
    EventType string            `bson:"event_type"` // content.submitted
    Filters   map[string]interface{} `bson:"filters"`
}

type WorkflowStep struct {
    ID         string                 `bson:"id"`
    Type       string                 `bson:"type"` // task.create, notification.send
    DependsOn  []string               `bson:"depends_on"`
    Params     map[string]interface{} `bson:"params"`
}
```

3. **Notification**
```go
type Notification struct {
    ID        primitive.ObjectID `bson:"_id"`
    Type      string             `bson:"type"` // task_assigned, sla_warning
    Channel   string             `bson:"channel"` // telegram, email, inapp
    UserID    primitive.ObjectID `bson:"user_id"`
    Status    string             `bson:"status"` // sent, delivered, failed
    Data      map[string]interface{} `bson:"data"`
    SentAt    *time.Time         `bson:"sent_at,omitempty"`
    CreatedAt time.Time          `bson:"created_at"`
}
```

4. **User** (existing in TCB)
```go
type User struct {
    ID    primitive.ObjectID `bson:"_id"`
    Email string             `bson:"email"`
    Name  string             `bson:"name"`
    Role  string             `bson:"role"` // admin, reviewer, creator
    // ... other fields
}
```

**Relationships:**
- Task ← (many-to-one) → User (assigned_to)
- Task ← (many-to-many) → Campaign (via metadata.campaign_id)
- Notification ← (many-to-one) → User
- Workflow ← (many-to-many) → Task (via metadata.workflow_id)

---

### Database Design

**MongoDB Collections:**

1. **tasks** (Primary collection)
   - Documents: ~1M tasks (10K campaigns × 100 tasks/campaign)
   - Avg doc size: 2KB
   - Total size: ~2GB

2. **workflows**
   - Documents: ~50 workflows
   - Size: <1MB

3. **notifications**
   - Documents: ~10M notifications (1M tasks × 10 notifications/task)
   - Avg doc size: 0.5KB
   - Total size: ~5GB

4. **users** (existing)
   - Documents: ~100K users
   - Size: ~50MB

**Capacity Planning (2 years):**
- Total data: ~10GB
- Indexes: ~3GB
- Working set: ~5GB (hot data)
- **Recommended MongoDB server**: 8GB RAM, 50GB SSD

---

### Data Flow

**Flow 1: Task Creation**
```
Client → API → Task Service → Validate → Repository → MongoDB
                    ↓
            Event Publisher → Redis Pub/Sub → Subscribers:
                                              - Notification Hub → Send notification
                                              - Workflow Engine → Trigger workflow
                                              - Audit Logger → Log event
```

**Flow 2: SLA Monitoring**
```
Asynq Scheduler (every 5min) → SLA Monitor → Repository → Query tasks
                                     ↓
                              Find due tasks → Notification Hub → Telegram/Email
                                     ↓
                              Update task (warning_sent=true) → MongoDB
```

**Flow 3: Real-Time Updates**
```
Task Updated → Event Publisher → Redis Pub/Sub → WebSocket Server
                                                      ↓
                                                  Connected Clients (Admin UI)
                                                      ↓
                                                  UI Auto-Refresh
```

---

## API Design

### API Architecture

**Style:** RESTful API (primary) + WebSocket (real-time)

**Versioning:** URL-based versioning (`/api/v1/...`)

**Authentication:** JWT tokens (Bearer)

**Response Format:** JSON

**Error Handling:** Standard HTTP status codes + error object
```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task with ID 123 not found",
    "details": {}
  }
}
```

---

### API Endpoints

**Base URL:** `https://tcb.accesstrade.com/api/v1`

#### Task Management

**POST /tasks**
Create new task
```json
Request:
{
  "title": "Review Content #123",
  "type": "content_review",
  "priority": "high",
  "metadata": {
    "content_id": "123",
    "campaign_id": "456"
  }
}

Response: 201 Created
{
  "id": "507f1f77bcf86cd799439011",
  "title": "Review Content #123",
  "status": "assigned",
  "assigned_to": "507f191e810c19729de860ea",
  "due_date": "2026-02-07T10:00:00Z",
  "created_at": "2026-02-05T10:00:00Z"
}
```

**GET /tasks**
List tasks (with filters, pagination, sorting)
```
Query parameters:
- status: assigned,in_progress (comma-separated)
- assigned_to: user_id
- priority: high,urgent
- type: content_review
- due_from: 2026-02-01
- due_to: 2026-02-28
- page: 1
- limit: 50 (max 100)
- sort: due_date:asc | priority:desc | created_at:desc

Response: 200 OK
{
  "tasks": [...],
  "total": 150,
  "page": 1,
  "limit": 50,
  "total_pages": 3
}
```

**GET /tasks/:id**
Get task detail

**PATCH /tasks/:id**
Update task fields
```json
Request:
{
  "priority": "urgent",
  "due_date": "2026-02-06T10:00:00Z"
}
```

**PATCH /tasks/:id/status**
Transition task status
```json
Request:
{
  "status": "completed",
  "result": "approved",
  "feedback": "Good content!"
}
```

**DELETE /tasks/:id**
Soft delete (set status=cancelled)

---

#### SLA & Reports

**GET /tasks/sla/dashboard**
Get SLA metrics
```json
Response:
{
  "compliance_rate": 0.87,
  "total_tasks": 1000,
  "completed_on_time": 870,
  "overdue": 30,
  "tasks_by_status": {
    "assigned": 50,
    "in_progress": 80,
    "completed": 870
  },
  "trends": [
    {"date": "2026-02-01", "compliance": 0.85},
    {"date": "2026-02-02", "compliance": 0.88}
  ]
}
```

**GET /tasks/reports/export**
Export task report (Excel)
```
Query: ?from=2026-02-01&to=2026-02-28&format=xlsx
Response: Excel file download
```

---

#### Notifications

**GET /notifications**
List notifications (last 20)

**PATCH /notifications/:id/read**
Mark notification as read

**PATCH /notifications/read-all**
Mark all as read

**GET /notifications/unread-count**
Get unread count

---

#### Workflows

**GET /workflows**
List workflows

**POST /workflows**
Create workflow (admin only)

**PATCH /workflows/:id**
Update workflow

**POST /workflows/:id/activate**
Activate workflow

---

### Authentication & Authorization

**Authentication Method:** JWT (JSON Web Tokens)

**Token Lifetime:** 24 hours (configurable)

**Token Format:**
```
Header: Authorization: Bearer <token>

Token payload:
{
  "user_id": "507f191e810c19729de860ea",
  "email": "reviewer@accesstrade.com",
  "role": "reviewer",
  "exp": 1738761600,
  "iat": 1738675200
}
```

**Authorization (RBAC):**

| Role     | Permissions                                      |
|----------|--------------------------------------------------|
| Admin    | Full access (all endpoints)                      |
| Reviewer | - View assigned tasks<br>- Update assigned tasks only<br>- Cannot create/delete tasks<br>- Cannot modify SLA settings |
| Creator  | - Read-only access<br>- View own content status only |

**API Security:**
- HTTPS only (TLS 1.2+)
- CORS enabled (whitelist domains)
- Rate limiting: 1000 req/hour per user
- API key for external integrations (Chatwoot, Content Catcher)

---

## Non-Functional Requirements Coverage

### NFR-001: API Response Time (P95 < 200ms)

**Requirement:** P50 <100ms, P95 <200ms, P99 <500ms

**Architecture Solution:**
1. **Redis caching layer**
   - Cache hot data: task lists (TTL 5 min), user info (TTL 1h)
   - Cache key pattern: `task:list:{user_id}:{status}`

2. **Database indexing**
   - 8 strategic indexes on tasks collection
   - Compound index on (status, assigned_to) for main query

3. **Query optimization**
   - Pagination (limit 50 items/page)
   - Projection (select only needed fields)
   - No N+1 queries (use aggregation pipelines)

4. **Async processing**
   - Notifications sent asynchronously (Asynq)
   - SLA checks in background job
   - No blocking operations in API handlers

**Implementation Notes:**
```go
// Caching example
func (s *TaskService) ListTasks(ctx context.Context, filters TaskFilters) ([]*Task, error) {
    cacheKey := fmt.Sprintf("task:list:%s:%s", filters.UserID, filters.Status)

    // Try cache first
    if cached, err := s.cache.Get(ctx, cacheKey); err == nil {
        return cached, nil
    }

    // Cache miss → Query DB
    tasks, err := s.repo.Query(ctx, filters)
    if err != nil {
        return nil, err
    }

    // Cache for 5 minutes
    s.cache.Set(ctx, cacheKey, tasks, 5*time.Minute)

    return tasks, nil
}
```

**Validation:**
- Load test: 1000 RPS, measure P95 latency
- Monitoring: Prometheus histogram, alert if P95 >200ms

---

### NFR-002: Database Query Optimization

**Requirement:** List tasks <50ms, Find by ID <5ms

**Architecture Solution:**
1. **Strategic indexes** (8 indexes)
   ```javascript
   db.tasks.createIndex({ status: 1, assigned_to: 1 })  // Main query (most used)
   db.tasks.createIndex({ due_date: 1, status: 1 })     // SLA monitoring
   db.tasks.createIndex({ type: 1, created_at: -1 })    // Task type filtering
   db.tasks.createIndex({ priority: 1 })                // Priority sorting
   db.tasks.createIndex({ "metadata.campaign_id": 1 })  // Campaign tasks
   db.tasks.createIndex({ "metadata.content_id": 1 })   // Content tasks
   db.tasks.createIndex({ is_breached: 1 })             // Breached tasks
   db.tasks.createIndex({ created_at: -1 })             // Recent tasks
   ```

2. **Query patterns**
   - Use compound indexes for common filter combinations
   - Projection to reduce document size returned
   - Pagination with cursor-based (better than offset)

3. **Explain plan analysis**
   - Monitor slow queries (>100ms)
   - Use explain() to verify index usage
   - No collection scans (COLLSCAN)

**Implementation Notes:**
```javascript
// Good query (uses index)
db.tasks.find({
  status: { $in: ["assigned", "in_progress"] },
  assigned_to: ObjectId("...")
}).sort({ priority: -1, due_date: 1 }).limit(50)

// Index used: { status: 1, assigned_to: 1 }
```

**Validation:**
- Explain plan shows IXSCAN (index scan)
- Query time <50ms
- Monitoring: Slow query log

---

### NFR-003: Concurrent Users (100 users)

**Requirement:** Support 100 concurrent users, 1000 req/min

**Architecture Solution:**
1. **Horizontal scaling**
   - Stateless API servers (no session state)
   - Scale to 2-5 instances based on load
   - Load balancer (Nginx) round-robin

2. **Connection pooling**
   - MongoDB pool size: 100 connections
   - Redis pool size: 50 connections
   - Reuse connections (no new connection per request)

3. **Session management**
   - JWT tokens (stateless)
   - No server-side sessions
   - No sticky sessions needed

4. **Resource limits**
   - Max request body size: 10MB
   - Request timeout: 30 seconds
   - Rate limiting: 1000 req/hour per user

**Implementation Notes:**
```go
// MongoDB connection pool
client, err := mongo.Connect(ctx, options.Client().
    ApplyURI(mongoURI).
    SetMaxPoolSize(100).
    SetMinPoolSize(10))

// Redis connection pool
redis.NewClient(&redis.Options{
    Addr:         redisAddr,
    PoolSize:     50,
    MinIdleConns: 10,
})
```

**Validation:**
- Load test: 100 concurrent users × 10 req/min = 1000 req/min
- Monitor: Connection pool usage, response time under load

---

### NFR-005: Authentication & Authorization (JWT + RBAC)

**Requirement:** Secure auth, role-based permissions

**Architecture Solution:**
1. **JWT authentication**
   - Algorithm: RS256 (asymmetric)
   - Token lifetime: 24 hours
   - Refresh tokens: 30 days

2. **RBAC middleware**
   ```go
   func RequireRole(requiredRole string) gin.HandlerFunc {
       return func(c *gin.Context) {
           user := c.MustGet("user").(*User)
           if user.Role != requiredRole && user.Role != "admin" {
               c.JSON(403, gin.H{"error": "Forbidden"})
               c.Abort()
               return
           }
           c.Next()
       }
   }

   // Usage
   router.PATCH("/tasks/:id/status",
       authMiddleware,
       RequireRole("reviewer"),
       handleUpdateTaskStatus)
   ```

3. **Authorization checks**
   - Admin: Full access
   - Reviewer: Can only update assigned tasks
   - Creator: Read-only

4. **API security**
   - HTTPS only (redirect HTTP to HTTPS)
   - CORS whitelist
   - Rate limiting (1000 req/hour)

**Validation:**
- Penetration testing
- Security audit (OWASP Top 10)

---

### NFR-007: Uptime SLA (99.5%)

**Requirement:** 99.5% monthly uptime (max 3.6h downtime)

**Architecture Solution:**
1. **High availability**
   - Multi-AZ deployment (2 availability zones)
   - MongoDB replica set (1 primary + 2 secondaries)
   - Redis sentinel (auto-failover)

2. **Health checks**
   ```go
   // Health endpoint
   router.GET("/health", func(c *gin.Context) {
       status := "ok"

       // Check MongoDB
       if err := mongoClient.Ping(ctx, nil); err != nil {
           status = "degraded"
       }

       // Check Redis
       if err := redisClient.Ping(ctx).Err(); err != nil {
           status = "degraded"
       }

       c.JSON(200, gin.H{
           "status": status,
           "timestamp": time.Now(),
       })
   })
   ```

3. **Graceful degradation**
   - If Redis down → Fallback to DB queries (slower but works)
   - If MongoDB secondary down → Use primary only
   - If notification service down → Queue for retry

4. **Circuit breakers**
   - Prevent cascade failures
   - Timeout external API calls (5s timeout)

**Validation:**
- Uptime monitoring (UptimeRobot)
- Monthly uptime reports
- Incident response time <15 min

---

### NFR-008: Disaster Recovery (RTO 1h, RPO 15min)

**Requirement:** RTO 1 hour, RPO 15 minutes

**Architecture Solution:**
1. **Automated backups**
   - MongoDB snapshots every 15 minutes
   - Incremental backups (only changes)
   - Full backup daily (retained 30 days)

2. **Backup storage**
   - AWS S3 (3 regions: Singapore, Tokyo, Oregon)
   - Versioning enabled
   - Lifecycle policy: Delete after 30 days

3. **Restore procedure**
   ```bash
   # Documented runbook
   1. Stop API servers
   2. Restore MongoDB from snapshot
      mongorestore --uri="mongodb://..." --archive=backup.gz
   3. Verify data integrity (check counts)
   4. Start API servers
   5. Smoke test (create task, list tasks)
   Total estimated time: 45 minutes ✅ (within RTO 1h)
   ```

4. **Failover**
   - MongoDB replica set auto-failover (30 seconds)
   - API servers stateless → Any instance can handle requests

**Validation:**
- Monthly restore drill (test in staging)
- Measure RTO (target <1 hour)
- Measure RPO (verify data loss <15 min)

---

### NFR-011: Code Quality (>80% test coverage)

**Requirement:** >80% test coverage, clean code

**Architecture Solution:**
1. **Layered testing**
   - **Unit tests**: 85% coverage (Go services, React components)
     - Test all business logic
     - Mock all dependencies
     - Fast execution (<5s)

   - **Integration tests**: 70% coverage (API endpoints, DB operations)
     - Test with real MongoDB (testcontainers)
     - Test API contracts
     - Medium execution (<30s)

   - **E2E tests**: 50% coverage (Critical user flows)
     - Create task → Assign → Complete
     - Content review workflow
     - SLA warning flow
     - Slow execution (<5min)

2. **Dependency injection**
   ```go
   // All dependencies injected via constructor
   type TaskService struct {
       repo      TaskRepository
       notifier  NotificationSender
       publisher EventPublisher
   }

   func NewTaskService(
       repo TaskRepository,
       notifier NotificationSender,
       publisher EventPublisher,
   ) *TaskService {
       return &TaskService{
           repo:      repo,
           notifier:  notifier,
           publisher: publisher,
       }
   }

   // Testing: Inject mocks
   service := NewTaskService(
       mocks.NewMockRepository(),
       mocks.NewMockNotifier(),
       mocks.NewMockPublisher(),
   )
   ```

3. **CI enforcement**
   ```yaml
   # GitHub Actions
   - name: Run tests
     run: go test ./... -coverprofile=coverage.out

   - name: Check coverage
     run: |
       coverage=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | sed 's/%//')
       if (( $(echo "$coverage < 80" | bc -l) )); then
         echo "Coverage $coverage% is below 80%"
         exit 1
       fi
   ```

4. **Code review process**
   - All PRs need 1 approval
   - Automated checks (linting, tests)
   - Review checklist (security, performance, tests)

**Validation:**
- Coverage reports (Codecov)
- SonarQube quality gate
- CI pipeline passes

---

## Security Architecture

### Authentication

**Method:** JWT (JSON Web Tokens) with RS256 (asymmetric encryption)

**Token Flow:**
```
1. User login (email + password) → API
2. Verify credentials → Database
3. Generate JWT token (24h expiry)
   - Signed with private key (RS256)
   - Payload: user_id, email, role, exp, iat
4. Return token to client
5. Client stores token (localStorage or secure cookie)
6. Client includes token in all requests (Authorization: Bearer <token>)
7. API verifies token with public key
8. Extract user info from token → Proceed
```

**Token Structure:**
```json
{
  "alg": "RS256",
  "typ": "JWT"
}
{
  "user_id": "507f191e810c19729de860ea",
  "email": "reviewer@accesstrade.com",
  "role": "reviewer",
  "exp": 1738761600,
  "iat": 1738675200
}
```

**Refresh Tokens:**
- Refresh token: 30 days lifetime
- Stored in httpOnly cookie (XSS protection)
- Used to get new access token without re-login

---

### Authorization

**Model:** Role-Based Access Control (RBAC)

**Roles & Permissions:**

| Role     | Permissions                                                                 |
|----------|-----------------------------------------------------------------------------|
| **Admin** | - Full access to all endpoints<br>- Create/update/delete tasks<br>- Manage workflows<br>- View all reports<br>- Manage users |
| **Reviewer** | - View assigned tasks<br>- Update assigned tasks only<br>- Transition status (assigned tasks)<br>- Add comments<br>- Cannot create/delete tasks |
| **Creator** | - Read-only access<br>- View own content status<br>- Cannot modify tasks |

**Authorization Middleware:**
```go
// Check if user owns the task (for reviewers)
func RequireTaskOwnership() gin.HandlerFunc {
    return func(c *gin.Context) {
        user := c.MustGet("user").(*User)
        taskID := c.Param("id")

        if user.Role == "admin" {
            c.Next()
            return
        }

        task, err := taskRepo.FindByID(c.Request.Context(), taskID)
        if err != nil {
            c.JSON(404, gin.H{"error": "Task not found"})
            c.Abort()
            return
        }

        if task.AssignedTo.Hex() != user.ID.Hex() {
            c.JSON(403, gin.H{"error": "You can only modify assigned tasks"})
            c.Abort()
            return
        }

        c.Next()
    }
}

// Usage
router.PATCH("/tasks/:id/status",
    authMiddleware,
    RequireRole("reviewer"),
    RequireTaskOwnership(),
    handleUpdateTaskStatus)
```

---

### Data Encryption

**At Rest:**
- **MongoDB encryption**: Enabled (WiredTiger encryption)
- **Backup encryption**: AES-256 before upload to S3
- **Secrets**: Stored in environment variables (not in code)

**In Transit:**
- **HTTPS only**: TLS 1.3 (prefer) or TLS 1.2 (fallback)
- **Certificate**: Let's Encrypt (auto-renewal)
- **MongoDB connection**: TLS enabled
- **Redis connection**: TLS enabled

**Sensitive Data:**
- **Passwords**: Bcrypt hashing (cost 12)
- **API keys**: Stored encrypted in DB
- **JWT signing key**: Stored securely (AWS Secrets Manager or env var)

---

### Security Best Practices

1. **Input Validation**
   - Validate all inputs (go-playground/validator)
   - Sanitize HTML/SQL (prevent injection)
   - Max request body size: 10MB

2. **SQL/NoSQL Injection Prevention**
   - Use parameterized queries (MongoDB driver handles this)
   - No string concatenation in queries

3. **XSS Prevention**
   - Sanitize output (escape HTML)
   - CSP headers: `Content-Security-Policy: default-src 'self'`

4. **CSRF Protection**
   - SameSite cookie attribute
   - CSRF tokens for state-changing operations

5. **Rate Limiting**
   - 1000 requests/hour per user
   - 100 requests/minute per IP (DDoS protection)

6. **Security Headers**
   ```
   Strict-Transport-Security: max-age=31536000; includeSubDomains
   X-Content-Type-Options: nosniff
   X-Frame-Options: DENY
   X-XSS-Protection: 1; mode=block
   Content-Security-Policy: default-src 'self'
   ```

7. **Secrets Management**
   - No secrets in code (use env vars)
   - Rotate JWT signing keys every 90 days
   - API keys: Hash before storing

8. **Logging & Monitoring**
   - Log all auth failures
   - Alert on suspicious patterns (100 failed logins)
   - GDPR compliance: Anonymize PII in logs

---

## Scalability & Performance

### Scaling Strategy

**Horizontal Scaling (Preferred):**
- Stateless API servers → Easy to scale
- Add instances based on load (2 → 5 instances)
- Load balancer distributes requests (round-robin)

**Vertical Scaling (Temporary):**
- Increase server resources (2 CPU → 4 CPU)
- Use for MongoDB (better for writes)

**Auto-Scaling Triggers:**
- CPU >70% for 5 minutes → Scale up
- Request queue depth >100 → Scale up
- CPU <30% for 10 minutes → Scale down
- Min instances: 2 (HA)
- Max instances: 5 (cost control)

**Database Scaling:**
- **MongoDB replica set**: 1 primary (writes) + 2 secondaries (reads)
- **Read replicas**: Direct read queries to secondaries
- **Sharding**: IF data >100GB → Shard by campaign_id (not needed now)

---

### Performance Optimization

**1. Caching Strategy (Redis)**
```
Cache Layers:
- L1 (In-memory): Task objects (LRU, max 10K items)
- L2 (Redis): Task lists (TTL 5 min)
- L3 (MongoDB): Source of truth

Cache Hit Ratio Target: >80%
```

**2. Query Optimization**
- Indexes on all query fields
- Projection (select only needed fields)
- Pagination (limit 50 items/page)
- No N+1 queries (use aggregation pipelines)

**3. Lazy Loading**
- Load task details on demand (not in list view)
- Load status history only when needed

**4. Compression**
- Gzip compression for API responses (reduce bandwidth 70%)
- MongoDB compression: Snappy (fast) or Zstd (better ratio)

**5. Async Processing**
- Notifications sent asynchronously (Asynq)
- SLA checks in background job (no blocking)
- Email sending (queue, retry on failure)

---

### Caching Strategy

**Cache Hierarchy:**
```
┌──────────────────────────────────────┐
│  L1: In-Memory (LRU Cache)           │
│  - Task objects (10K items)          │
│  - Hit: <1ms                         │
│  - Eviction: LRU                     │
└─────────────┬────────────────────────┘
              │ Miss
┌─────────────▼────────────────────────┐
│  L2: Redis Cache                     │
│  - Task lists (TTL 5 min)            │
│  - User info (TTL 1 hour)            │
│  - Hit: <5ms                         │
└─────────────┬────────────────────────┘
              │ Miss
┌─────────────▼────────────────────────┐
│  L3: MongoDB (Source of Truth)       │
│  - All tasks                         │
│  - Hit: 10-50ms                      │
└──────────────────────────────────────┘
```

**Cache Keys:**
```
task:list:{user_id}:{status}         → TTL 5 min
task:detail:{task_id}                → TTL 10 min
user:info:{user_id}                  → TTL 1 hour
campaign:budget:{campaign_id}        → TTL 1 min (critical data)
```

**Cache Invalidation:**
```go
// When task updated → Invalidate cache
func (s *TaskService) UpdateTask(ctx context.Context, id string, updates map[string]interface{}) error {
    // Update DB
    err := s.repo.Update(ctx, id, updates)
    if err != nil {
        return err
    }

    // Invalidate cache
    task, _ := s.repo.FindByID(ctx, id)
    s.cache.Delete(ctx, fmt.Sprintf("task:detail:%s", id))
    s.cache.Delete(ctx, fmt.Sprintf("task:list:%s:%s", task.AssignedTo, task.Status))

    return nil
}
```

---

### Load Balancing

**Load Balancer:** Nginx

**Algorithm:** Round-robin (default)
- Request 1 → Server 1
- Request 2 → Server 2
- Request 3 → Server 1
- ...

**Health Checks:**
```nginx
upstream api_servers {
    server api1:8080 max_fails=3 fail_timeout=30s;
    server api2:8080 max_fails=3 fail_timeout=30s;
}

server {
    listen 443 ssl http2;
    server_name tcb.accesstrade.com;

    location /api/ {
        proxy_pass http://api_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        # Health check
        health_check interval=10s fails=3 passes=2;
    }
}
```

**Sticky Sessions:** Not needed (stateless JWT)

**SSL Termination:** At load balancer (offload SSL from API servers)

---

## Reliability & Availability

### High Availability Design

**Target:** 99.5% uptime (max 3.6h downtime/month)

**Architecture:**
```
┌────────────────────────────────────────┐
│       Load Balancer (Nginx)            │
│       - Auto-failover                  │
│       - Health checks                  │
└───────────┬────────────────────────────┘
            │
    ┌───────┴───────┐
    │               │
┌───▼───┐       ┌───▼───┐
│ API 1 │       │ API 2 │  (Multi-AZ)
│ AZ-1  │       │ AZ-2  │
└───┬───┘       └───┬───┘
    │               │
    └───────┬───────┘
            │
┌───────────▼────────────────────────────┐
│    MongoDB Replica Set                 │
│    - Primary (AZ-1)                    │
│    - Secondary 1 (AZ-2)                │
│    - Secondary 2 (AZ-3)                │
│    - Auto-failover (<30s)              │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│    Redis Sentinel                      │
│    - Master (AZ-1)                     │
│    - Replica (AZ-2)                    │
│    - Sentinel monitors failover        │
└────────────────────────────────────────┘
```

**No Single Points of Failure:**
- ✅ Load balancer: 2 instances (keepalived)
- ✅ API servers: 2+ instances
- ✅ MongoDB: Replica set (auto-failover)
- ✅ Redis: Sentinel (auto-failover)

**Failover Mechanisms:**
- MongoDB primary fails → Secondary promoted (30s)
- Redis master fails → Replica promoted (10s)
- API server fails → Health check detects → Route to healthy servers

---

### Disaster Recovery

**RTO (Recovery Time Objective):** 1 hour
**RPO (Recovery Point Objective):** 15 minutes

**Backup Strategy:**

**MongoDB Backups:**
```
Schedule:
- Incremental backup: Every 15 minutes
- Full backup: Daily at 2am UTC
- Retention: 30 days

Storage:
- AWS S3 (3 regions: Singapore, Tokyo, Oregon)
- Encryption: AES-256
- Versioning: Enabled
```

**Backup Script:**
```bash
#!/bin/bash
# Automated MongoDB backup

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="mongodb_backup_${TIMESTAMP}.gz"

# Create backup
mongodump --uri="mongodb://primary:27017" \
          --gzip \
          --archive=${BACKUP_FILE}

# Encrypt
openssl enc -aes-256-cbc -salt -in ${BACKUP_FILE} -out ${BACKUP_FILE}.enc -k ${BACKUP_KEY}

# Upload to S3
aws s3 cp ${BACKUP_FILE}.enc s3://tcb-backups/mongodb/${BACKUP_FILE}.enc

# Cleanup local
rm ${BACKUP_FILE} ${BACKUP_FILE}.enc
```

**Restore Procedure (Runbook):**
```
1. Declare incident (notify stakeholders)
2. Stop API servers (prevent writes during restore)
3. Download backup from S3
   aws s3 cp s3://tcb-backups/mongodb/latest.gz.enc .
4. Decrypt backup
   openssl enc -aes-256-cbc -d -in latest.gz.enc -out latest.gz -k ${KEY}
5. Restore MongoDB
   mongorestore --uri="mongodb://primary:27017" --gzip --archive=latest.gz
6. Verify data integrity
   mongo --eval "db.tasks.count()"  // Check counts
7. Start API servers
8. Smoke test (create task, list tasks)
9. Monitor for errors
10. Declare incident resolved

Estimated time: 45 minutes ✅ (within RTO 1h)
```

---

### Backup Strategy

**What to Backup:**
1. MongoDB (tasks, workflows, notifications)
2. Redis persistence files (AOF/RDB)
3. Configuration files (env vars, nginx configs)
4. Application code (Git repository)

**Backup Testing:**
- Monthly restore drill (test in staging environment)
- Verify data integrity (check counts, sample records)
- Measure RTO (target <1 hour)

**Backup Monitoring:**
- Alert if backup fails
- Alert if backup size anomaly (>20% change)
- Daily backup success report

---

### Monitoring & Alerting

**Monitoring Stack:**
- **Metrics**: Prometheus (collect), Grafana (visualize)
- **Logging**: Structured logs (JSON), Loki (aggregation)
- **Errors**: Sentry (real-time error tracking)
- **Uptime**: UptimeRobot (external monitoring)

**Key Metrics to Track:**

**1. Application Metrics:**
```
- API latency (P50, P95, P99)
- Request rate (req/sec)
- Error rate (errors/min)
- Active users (concurrent)
```

**2. System Metrics:**
```
- CPU usage (%)
- Memory usage (%)
- Disk usage (%)
- Network I/O (MB/s)
```

**3. Database Metrics:**
```
- MongoDB connections (active/available)
- Query latency (ms)
- Slow queries (>100ms)
- Replication lag (seconds)
```

**4. Queue Metrics:**
```
- Asynq queue depth (pending jobs)
- Job processing time (ms)
- Failed jobs (count)
```

**5. Business Metrics:**
```
- Tasks created/hour
- Tasks completed/hour
- SLA compliance rate (%)
- Notification delivery rate (%)
```

**Alert Rules:**

**CRITICAL (Page on-call):**
```
- API down >5 min
- Database primary down
- Error rate >10%
- Disk usage >95%
```

**WARNING (Notify Slack):**
```
- CPU >80% for 5 min
- Memory >80%
- P95 latency >200ms
- Queue depth >1000
```

**Grafana Dashboard:**
```
┌─────────────────────────────────────────┐
│  TASK MANAGEMENT SYSTEM - MONITORING    │
├─────────────────────────────────────────┤
│  System Health: 🟢 All systems operational
│  Uptime: 99.7% (this month)
│
│  ┌─────────┐ ┌─────────┐ ┌─────────┐
│  │ API     │ │ MongoDB │ │ Redis   │
│  │ 🟢 UP   │ │ 🟢 UP   │ │ 🟢 UP   │
│  └─────────┘ └─────────┘ └─────────┘
│
│  API Latency (P95): 145ms ✅
│  ████████░░ (target <200ms)
│
│  Error Rate: 0.3% ✅
│  █░░░░░░░░░ (target <1%)
│
│  Queue Depth: 45 ✅
│  ██░░░░░░░░ (alert if >1000)
│
│  SLA Compliance: 87% ✅
│  ████████░░ (target >85%)
└─────────────────────────────────────────┘
```

---

## Requirements Traceability

### Functional Requirements Coverage

| FR ID | FR Name | Components | Implementation |
|-------|---------|-----------|----------------|
| FR-001 | Task Domain Model | Task Engine | MongoDB schema, Go struct |
| FR-002 | Task State Machine | Task Engine | State transition logic, guards |
| FR-003 | Task CRUD API | Task Engine, API Layer | 6 RESTful endpoints |
| FR-004 | Auto-Assignment Algorithm | Task Engine | Least-loaded strategy |
| FR-005 | My Tasks Dashboard | Frontend | React component, filters, sort |
| FR-006 | Manual Task Creation | Task Engine, Frontend | API + UI form |
| FR-007 | SLA Configuration | SLA Monitor | Config-driven SLA policies |
| FR-008 | SLA Monitoring Background Job | SLA Monitor | Asynq periodic task (5 min) |
| FR-009 | SLA Escalation Workflow | SLA Monitor | Auto-escalate after 24h breach |
| FR-010 | SLA Dashboard & Reports | SLA Monitor, Frontend | Metrics API + React charts |
| FR-011 | Multi-Channel Notification Delivery | Notification Hub | Telegram, Email, In-app |
| FR-012 | Telegram Bot Inline Actions | Notification Hub | Inline buttons, callback handler |
| FR-013 | In-App Notification Center | Frontend | WebSocket + React component |
| FR-014 | Notification Preferences | Notification Hub | User preferences, quiet hours |
| FR-015 | Auto-Task Creation from Events | Workflow Orchestrator | Event subscribers |
| FR-016 | Parallel Workflow Execution | Workflow Orchestrator | Parallel gateway support |
| FR-017 | Conditional Workflow Routing | Workflow Orchestrator | If/else logic |
| FR-018 | Workflow Templates | Workflow Orchestrator | Pre-defined workflows |
| FR-019 | Real-Time Budget Dashboard | Budget Controller, Frontend | WebSocket + React charts |
| FR-020 | Budget Control Enforcement | Budget Controller | 3 budget checks before approval |
| FR-021 | Auto-Pause Campaign on Budget Exhaustion | Budget Controller | Monitor + auto-pause logic |
| FR-022 | Budget Forecast ML Model | Budget Controller | ML predictor (Phase 3 - optional) |
| FR-023 | Rule-Based Fraud Detection | Fraud Detector | 4 fraud rules, scoring |
| FR-024 | ML-Based Fraud Detection | Fraud Detector | ML model (Phase 3 - optional) |
| FR-025 | Blacklist Management | Fraud Detector | Blacklist CRUD, auto-block |
| FR-026 | Auto-Match Submissions to Crawled Data | Reconciliation Engine | URL matching, discrepancy calc |
| FR-027 | Flagged Items Review Dashboard | Reconciliation Engine, Frontend | Review UI for 10% flagged |
| FR-028 | Reconciliation Audit Trail | Reconciliation Engine | Immutable audit log |
| FR-029 | System Health Dashboard | Monitoring | Prometheus + Grafana |
| FR-030 | Alert Rules & Notifications | Monitoring | PagerDuty, Telegram, Slack |
| FR-031 | Automated Backup & Restore | Infrastructure | MongoDB snapshots (15 min) |
| FR-032 | Operational Runbooks | Documentation | 5 runbooks documented |

**Coverage:** 32/32 FRs addressed (100%)

---

### Non-Functional Requirements Coverage

| NFR ID | NFR Name | Solution | Validation |
|--------|----------|----------|------------|
| NFR-001 | API Response Time (P95 <200ms) | Redis caching, indexes, async | Load test 1000 RPS |
| NFR-002 | Database Query Optimization | 8 strategic indexes, pagination | Explain plans, <50ms |
| NFR-003 | Concurrent Users (100 users) | Horizontal scaling, pooling | Load test 100 users |
| NFR-004 | Data Volume Scalability (1M tasks) | Indexes, pagination, sharding plan | Perf test 1M tasks |
| NFR-005 | Authentication & Authorization | JWT + RBAC | Penetration test |
| NFR-006 | Data Privacy & GDPR | Retention policy, delete API | Compliance audit |
| NFR-007 | Uptime SLA (99.5%) | Multi-AZ, health checks, HA | Uptime monitoring |
| NFR-008 | Disaster Recovery (RTO 1h, RPO 15min) | Automated backups, restore drill | Monthly drill |
| NFR-009 | Browser Support | Chrome 100+, Firefox, Safari, Edge | Cross-browser test |
| NFR-010 | Accessibility (WCAG 2.1 AA) | Keyboard nav, ARIA labels | axe-core audit |
| NFR-011 | Code Quality (>80% coverage) | Unit/integration/E2E tests | Coverage report |
| NFR-012 | Documentation | API docs, architecture, runbooks | Review & publish |

**Coverage:** 12/12 NFRs addressed (100%)

---

## Trade-offs & Decision Log

### Decision 1: Modular Monolith vs Microservices

**Choice:** Modular Monolith

**Rationale:**
- **Team size**: 2 engineers → Monolith simpler to manage
- **Deployment**: Simpler ops, no service mesh complexity
- **Performance**: No network calls between components
- **Cost**: Lower infrastructure cost

**Trade-off:**
- ✅ Gain: Simplicity, faster development, lower cost
- ❌ Lose: Harder to scale individual components (acceptable now)

**When to revisit:** If ≥3 projects using task engine + need centralized monitoring → Consider microservice

---

### Decision 2: Embedded Workflow vs Temporal/n8n

**Choice:** Embedded Workflow Engine (in-code)

**Rationale:**
- **Simplicity**: No external dependencies
- **Full control**: Can customize exactly for needs
- **Performance**: No network calls to workflow service
- **Team expertise**: Go code (familiar), no new tools

**Trade-off:**
- ✅ Gain: Simplicity, full control, performance
- ❌ Lose: Less powerful than Temporal, no visual editor

**Future enhancement:** Add Workflow-as-Code (YAML) layer in Phase 2

---

### Decision 3: MongoDB vs PostgreSQL

**Choice:** MongoDB

**Rationale:**
- **Current stack**: TCB already uses MongoDB
- **Flexible schema**: Tasks have dynamic metadata (JSON)
- **Team expertise**: No learning curve
- **Query capabilities**: Aggregation pipelines adequate

**Trade-off:**
- ✅ Gain: Team expertise, flexible schema, fast queries
- ❌ Lose: No ACID transactions across documents

**Alternative considered:** PostgreSQL with JSONB
- **Why rejected**: Team not familiar, migration effort high

---

### Decision 4: Library Extraction Strategy (Phased vs Immediate)

**Choice:** Phased Extraction (Week 1-4 TCB → Week 5-8 Extract → Week 9+ Scale)

**Rationale:**
- **Avoid premature abstraction**: Learn from real use cases first
- **Deliver value faster**: TCB working by week 4
- **Better abstractions**: Extract based on actual duplication
- **Lower risk**: Incremental approach, can adjust

**Trade-off:**
- ✅ Gain: Faster delivery, better abstractions, lower risk
- ❌ Lose: Some duplicate code initially (temporary)

**Validation metric:** Code duplication % after extraction (target <20%)

---

### Decision 5: Self-Hosted Chatwoot vs Cloud

**Choice:** Self-Hosted Chatwoot

**Rationale:**
- **Cost**: $20/month (VPS) vs $99/month (cloud) → Save $948/year
- **Control**: Full data ownership, can customize
- **Integration**: Same network as task engine → faster

**Trade-off:**
- ✅ Gain: Lower cost, full control, faster integration
- ❌ Lose: Need to maintain infrastructure (acceptable)

---

## Deployment Architecture

### Environments

**1. Development (Local)**
- Developer laptops
- Docker Compose
- In-memory storage (testing)
- Hot reload enabled

**2. Staging**
- Mirrors production
- Same infrastructure (scaled down)
- Used for: QA testing, UAT, restore drills
- Data: Synthetic data + anonymized production data

**3. Production**
- Live environment
- Multi-AZ deployment
- Auto-scaling enabled
- Monitored 24/7

**Environment Parity:**
- Same Docker images (different configs)
- Same tech stack
- Config via environment variables

---

### Deployment Strategy

**Strategy:** Blue-Green Deployment

**Process:**
```
1. Deploy to Green (inactive) environment
2. Run health checks on Green
3. Run smoke tests on Green
4. If all pass → Switch traffic to Green (via load balancer)
5. Monitor for errors (15 min)
6. If errors → Instant rollback to Blue
7. If stable → Blue becomes next Green

Rollback time: <30 seconds ✅
Zero downtime: Yes ✅
```

**Release Schedule:**
- Production deploys: Tuesday & Thursday (2x/week)
- Staging deploys: Daily (after CI passes)
- Hotfix deploys: Anytime (for critical bugs)

**Deployment Checklist:**
```
Pre-deploy:
- [ ] All tests pass (CI green)
- [ ] Code review approved
- [ ] Security scan passed
- [ ] Backup created
- [ ] Rollback plan ready

Post-deploy:
- [ ] Health checks pass
- [ ] Smoke tests pass
- [ ] Monitor errors (15 min)
- [ ] Stakeholders notified
- [ ] Deployment logged
```

---

### Infrastructure as Code

**Tool:** Terraform (optional) or Docker Compose (simple)

**For Simplicity (Recommended for Start):**
```yaml
# docker-compose.yml
version: '3.8'

services:
  api-1:
    image: tcb/task-api:latest
    environment:
      - MONGO_URL=${MONGO_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET=${JWT_SECRET}
    ports:
      - "8080:8080"
    deploy:
      replicas: 2

  mongodb:
    image: mongo:6.0
    volumes:
      - mongo_data:/data/db
    command: --replSet rs0

  redis:
    image: redis:7.0
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:latest
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

**For Scale (Future):**
- Kubernetes manifests (Deployments, Services, Ingress)
- Helm charts (templating, versioning)
- Terraform (provision infrastructure)

---

## Open Issues & Risks

### Open Issues

**1. Budget Approval Workflow**
- **Question**: Who approves budget increases >20%? Finance Manager or CFO?
- **Impact**: Affects FR-020 implementation
- **Action**: Schedule meeting with Finance team (Week 2)
- **Decision needed by**: Week 2

**2. Fraud Detection Thresholds**
- **Question**: Acceptable false positive rate? (5% or 10%?)
- **Impact**: ML model tuning, review workload
- **Action**: Analyze historical data, propose thresholds
- **Decision needed by**: Week 10 (ML model phase)

**3. SLA Escalation Rules**
- **Question**: Escalate after how many hours breach? (24h or 48h?)
- **Impact**: FR-009 logic, manager workload
- **Action**: Review current escalation patterns
- **Decision needed by**: Week 4

**4. Blacklist Sharing**
- **Question**: Share blacklist with other brands (VPBank, VIB)?
- **Impact**: Legal review, data sharing agreements, API design
- **Action**: Consult legal team
- **Decision needed by**: Week 8

---

### Risks

**1. MongoDB Performance Degradation (Medium Risk)**
- **Risk**: Queries slow down as data grows to 1M+ tasks
- **Mitigation**: Strategic indexes, query optimization, monitoring
- **Contingency**: Add read replicas, implement sharding

**2. External API Dependencies (High Risk)**
- **Risk**: Telegram API rate limit hit, SendGrid quota exceeded
- **Mitigation**: Batch notifications, fallback channels
- **Contingency**: Implement retry logic, upgrade plans

**3. Team Bandwidth (Medium Risk)**
- **Risk**: 2 engineers may be insufficient for 12-week timeline
- **Mitigation**: Prioritize Must-Have features, defer Could-Have
- **Contingency**: Extend timeline or add contractor

**4. Scope Creep (High Risk)**
- **Risk**: Stakeholders request additional features mid-project
- **Mitigation**: Lock scope after PRD approval, change control process
- **Contingency**: Push new features to Phase 2

**5. Library Extraction Complexity (Low Risk)**
- **Risk**: Extracting library harder than expected
- **Mitigation**: Phased approach, measure duplication first
- **Contingency**: Keep TCB-specific, revisit extraction later

---

## Assumptions & Constraints

### Assumptions

**1. Team Availability**
- 1 Backend engineer (Go) full-time for 12 weeks
- 1 Frontend engineer (React) full-time for 12 weeks
- Product owner available 4h/week for decisions

**2. Technical Environment**
- MongoDB replica set already configured
- Redis already running
- Development environment setup complete
- Access to production infrastructure

**3. Business Commitment**
- Stakeholders approve $31.2K budget
- Team committed to 12-week timeline
- Pilot campaign available for testing (Week 8)
- Training sessions scheduled (Week 12)

**4. Data Quality**
- Historical campaign data available (for ML training - optional)
- Content Catcher API reliable (>99% uptime)
- Fraud labels available (if doing ML fraud detection)

**5. Infrastructure**
- Cloud hosting available (AWS, DigitalOcean, or similar)
- CI/CD pipeline (GitHub Actions) already setup
- Monitoring tools (Sentry, Prometheus) accounts ready

---

### Constraints

**1. Timeline**
- Must deliver in 12 weeks (hard deadline)
- Week 8: Pilot campaign testing
- Week 12: Production launch

**2. Budget**
- Total budget: $31.2K (development + infrastructure + training)
- Monthly infrastructure: <$150

**3. Team Size**
- 2 engineers (cannot hire more)
- No dedicated QA engineer (devs do testing)

**4. Technology Stack**
- Must use Go + React (current stack)
- Must use MongoDB (existing database)
- Cannot introduce new languages

**5. Compliance**
- GDPR compliance required
- Data retention: 2 years
- No PII in logs

---

## Future Considerations

### Phase 2 Enhancements (Week 13+)

**1. Workflow-as-Code (YAML)**
- Define workflows in YAML files
- Visual workflow editor
- Version control workflows

**2. Advanced Analytics**
- Predictive SLA breach (ML model)
- Task duration predictions
- Team performance analytics

**3. Mobile Native Apps**
- React Native app for reviewers
- Push notifications
- Offline mode

**4. Multi-Language Support**
- i18n framework (react-intl)
- Translate to English
- Vietnamese (default) + English

---

### Phase 3: Microservice Migration (If Needed)

**Criteria to migrate:**
- ≥3 projects using task engine
- Team size >5 engineers
- Need centralized monitoring
- Need independent scaling

**Migration Strategy:**
```
1. Extract Task Service (microservice)
2. Keep existing projects using library (no disruption)
3. New projects can choose: Library or Service
4. Gradual migration over 6 months
```

---

### SaaS Productization (Future)

**Potential:** Package task engine as SaaS product

**Features:**
- Multi-tenant architecture
- White-label UI
- API-first design
- Self-service onboarding

**Market:** Vietnamese enterprises needing task management

**Revenue:** $50-200/month per company (SaaS pricing)

---

## Approval & Sign-off

### Review Status

**Technical Lead:** [ ] Approved architecture, tech stack, component design

**Product Owner:** [ ] Approved requirements coverage, business logic

**Security Architect:** [ ] Approved security architecture, auth/authz design

**DevOps Lead:** [ ] Approved deployment strategy, infrastructure plan

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-05 | System Architect (BMAD) | Initial architecture design |

---

## Next Steps

### Immediate Actions (This Week)

**1. Architecture Review Meeting**
- Schedule review with stakeholders
- Present architecture document
- Get approvals & sign-offs
- Address open questions

**2. Development Environment Setup**
- Setup local Docker Compose
- Configure MongoDB replica set
- Setup Redis
- Create initial project structure

**3. Phase 1 Kickoff (Week 1)**
- Sprint planning (break epics into stories)
- Create task management board (Jira/GitHub Projects)
- Setup CI/CD pipeline
- Begin implementation (Task Engine core)

---

### Phase 4: Sprint Planning

After architecture approval, run `/bmad:sprint-planning` to:

**1. Break Epics into User Stories (80-100 stories)**
- Detailed acceptance criteria
- Effort estimation (story points)
- Dependencies mapping

**2. Plan Sprint Iterations (12 weeks = 6 sprints)**
- Sprint 1-2: Task Engine, SLA, Notifications
- Sprint 3: Workflows, Budget Controls
- Sprint 4: Fraud Detection, Reconciliation
- Sprint 5: Monitoring, Support Integration
- Sprint 6: Testing, Documentation, Launch

**3. Team Capacity Planning**
- 2 engineers × 8h/day × 10 days/sprint = 160 hours/sprint
- Story points per sprint: ~20-25 SP

**4. Begin Implementation**
- Follow architectural blueprint
- Implement component by component
- Test continuously (unit → integration → E2E)

---

## Summary

**Architecture Type:** 3-Layer Reusable Modular Monolith

**Key Highlights:**
- ✅ **Reusability-first**: 60-70% code reuse target across 4 projects
- ✅ **Performance**: P95 <200ms, Redis caching, 8 strategic indexes
- ✅ **Reliability**: 99.5% uptime, multi-AZ, auto-failover
- ✅ **Security**: JWT + RBAC, encryption at rest/transit
- ✅ **Scalability**: Horizontal scaling, 100 concurrent users
- ✅ **Maintainability**: >80% test coverage, clean architecture

**Technology Stack:**
- Frontend: React 18 + TypeScript + Tailwind
- Backend: Go 1.21 + Gin + Asynq
- Database: MongoDB 6.0 + Redis 7.0
- Infrastructure: Docker + Nginx + AWS S3

**Components (8 major):**
1. Task Engine (CRUD, state machine, assignment)
2. SLA Monitor (deadlines, warnings, escalation)
3. Notification Hub (Telegram, Email, In-app)
4. Workflow Orchestrator (auto-create, parallel, conditional)
5. Budget Controller (tracking, limits, auto-pause)
6. Fraud Detector (rule-based, ML-optional, blacklist)
7. Reconciliation Engine (90% auto-match)
8. Support Integration (Chatwoot webhook)

**Requirements Coverage:**
- Functional: 32/32 (100%)
- Non-Functional: 12/12 (100%)

**Implementation Approach:**
- Phase 1 (Week 1-4): Build TCB-specific (structure for reusability)
- Phase 2 (Week 5-8): Extract library `pkg/taskengine`
- Phase 3 (Week 9+): Scale to 3+ projects, evaluate microservice

**Cost (Monthly):**
- Infrastructure: $120 (VPS, MongoDB, Redis, LB)
- Third-party: $50 (SendGrid, S3, Chatwoot, Sentry)
- **Total: $170/month**

**ROI:**
- Annual value: $472,800 (time saved + fraud prevention + budget control)
- Investment: $31,200
- **ROI: 1,515% | Payback: 0.8 months**

---

**This architecture is ready for implementation. All 32 FRs and 12 NFRs are addressed with concrete solutions.**

**Next workflow:** `/bmad:sprint-planning` to create detailed user stories and sprint plan.

---

*This document was created using BMAD Method v6 - Phase 3 (Solutioning)*

*Generated: 2026-02-05*
