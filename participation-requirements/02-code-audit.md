# Code Audit: Tính năng Điều kiện Tham gia Campaign

**Ngày:** 2026-02-07
**Mục đích:** Rà soát backend code để xác định các điểm cần lưu ý khi implement tính năng điều kiện tham gia campaign

---

## Executive Summary

Sau khi rà soát toàn bộ backend flow từ submit content → reconciliation, đã xác định được **7 điểm then chốt** cần xử lý khi implement tính năng điều kiện tham gia campaign.

**Kết luận chính:**
- ✅ Architecture hiện tại **HỖ TRỢ TỐT** cho việc thêm participation requirements
- ⚠️ Cần **mở rộng** 5 models chính
- 🔧 Cần **update** 8 service functions
- 📋 Cần **validation check** ở 3 điểm quan trọng trong flow

---

## 1. Models Cần Mở Rộng

### 1.1 EventRaw - Thêm Participation Requirements Config

**File:** `backend/internal/model/mg/event.go`

**Hiện tại:**
```go
type EventRaw struct {
    ID                   AppID
    Partner              AppID
    Options              *EventOpts
    AutoRejectConditions []*EventAutoRejectCondition
    // ... other fields
}

type EventOpts struct {
    MaxContentPerDay int
    ApplyForSources  []string
    Hashtags         []string
}
```

**Cần thêm:**
```go
type EventRaw struct {
    // ... existing fields
    ParticipationRequirements *EventParticipationRequirements `bson:"participationRequirements,omitempty" json:"participationRequirements,omitempty"`
}

type EventParticipationRequirements struct {
    Enabled      bool                          `json:"enabled" bson:"enabled"`
    Requirements []*ParticipationRequirement   `json:"requirements" bson:"requirements"`
}

type ParticipationRequirement struct {
    Type             string                           `json:"type" bson:"type"` // "facebook_account", "facebook_followers", "account_age", "invitation_code", "authentic_posts"
    Title            string                           `json:"title" bson:"title"`
    Description      string                           `json:"description" bson:"description"`
    ValidationLevel  string                           `json:"validationLevel" bson:"validationLevel"` // "auto", "manual", "hybrid"
    Validation       *ParticipationRequirementValidation `json:"validation,omitempty" bson:"validation,omitempty"`
    Required         bool                             `json:"required" bson:"required"`
    Order            int                              `json:"order" bson:"order"`
    HelpLink         string                           `json:"helpLink,omitempty" bson:"helpLink,omitempty"`
}

type ParticipationRequirementValidation struct {
    MinFollowers int    `json:"minFollowers,omitempty" bson:"minFollowers,omitempty"`
    MinMonths    int    `json:"minMonths,omitempty" bson:"minMonths,omitempty"`
    CodeRequired bool   `json:"codeRequired,omitempty" bson:"codeRequired,omitempty"`
}
```

**Lý do:**
- Event-level configuration cho phép mỗi campaign có requirements khác nhau
- Flexible validation rules per requirement type
- Support cho manual/auto/hybrid validation

---

### 1.2 UserEventRaw - Track Participation Status

**File:** `backend/internal/model/mg/user_event.go`

**Hiện tại:**
```go
type UserEventRaw struct {
    ID        AppID
    User      AppID
    Event     AppID
    Partner   AppID
    EventType string
    Statistic UserEventStatistic
    CreatedAt time.Time
    UpdatedAt time.Time
}
```

**Cần thêm:**
```go
type UserEventRaw struct {
    // ... existing fields
    ParticipationStatus *UserEventParticipationStatus `bson:"participationStatus,omitempty" json:"participationStatus,omitempty"`
    CanSubmitContent    bool                          `bson:"canSubmitContent" json:"canSubmitContent"`
}

type UserEventParticipationStatus struct {
    Status           string                                  `json:"status" bson:"status"` // "not_started", "pending_review", "approved", "rejected"
    Requirements     map[string]*RequirementStatus           `json:"requirements" bson:"requirements"`
    ApprovedAt       *time.Time                              `json:"approvedAt,omitempty" bson:"approvedAt,omitempty"`
    ApprovedBy       *AppID                                  `json:"approvedBy,omitempty" bson:"approvedBy,omitempty"` // Admin ID
    RejectedAt       *time.Time                              `json:"rejectedAt,omitempty" bson:"rejectedAt,omitempty"`
    RejectionReason  string                                  `json:"rejectionReason,omitempty" bson:"rejectionReason,omitempty"`
    SubmittedAt      *time.Time                              `json:"submittedAt,omitempty" bson:"submittedAt,omitempty"`
    ReviewNotes      string                                  `json:"reviewNotes,omitempty" bson:"reviewNotes,omitempty"`
}

type RequirementStatus struct {
    Type           string                   `json:"type" bson:"type"`
    Status         string                   `json:"status" bson:"status"` // "pending", "passed", "failed", "manual_override"
    CheckedAt      *time.Time               `json:"checkedAt,omitempty" bson:"checkedAt,omitempty"`
    AutoCheckResult *AutoCheckResult        `json:"autoCheckResult,omitempty" bson:"autoCheckResult,omitempty"`
    ManualCheckAt  *time.Time               `json:"manualCheckAt,omitempty" bson:"manualCheckAt,omitempty"`
    ManualCheckBy  *AppID                   `json:"manualCheckBy,omitempty" bson:"manualCheckBy,omitempty"`
    Value          interface{}              `json:"value,omitempty" bson:"value,omitempty"` // Current value (follower count, etc.)
    Required       interface{}              `json:"required,omitempty" bson:"required,omitempty"` // Required value
    Notes          string                   `json:"notes,omitempty" bson:"notes,omitempty"`
}

type AutoCheckResult struct {
    Success bool        `json:"success" bson:"success"`
    Data    interface{} `json:"data,omitempty" bson:"data,omitempty"`
    Error   string      `json:"error,omitempty" bson:"error,omitempty"`
}
```

**Lý do:**
- Track từng requirement status riêng biệt
- Support both auto và manual validation
- Audit trail (who approved, when, why rejected)

---

### 1.3 ContentRaw - Link to Participation Status

**File:** `backend/internal/model/mg/content.go`

**Hiện tại:**
```go
type ContentRaw struct {
    ID      AppID
    User    AppID
    Event   AppID
    Partner AppID
    Status  string
    // ... other fields
}
```

**Cần thêm (nếu cần validation at submit time):**
```go
type ContentRaw struct {
    // ... existing fields
    ParticipationValidatedAt *time.Time `bson:"participationValidatedAt,omitempty" json:"participationValidatedAt,omitempty"`
    // Timestamp khi validate participation requirements lần cuối
    // Dùng để check nếu requirements changed sau khi user đã submit
}
```

**Lý do:**
- Audit trail: Biết content được submit khi participation status ra sao
- Reconciliation có thể re-check based on this timestamp

---

### 1.4 ReconciliationItemRaw - Include Participation Check

**File:** `backend/internal/model/mg/reconciliation_item.go`

**Cần mở rộng (nếu chưa có):**
```go
type ReconciliationItemRaw struct {
    // ... existing fields
    ParticipationCheck *ReconciliationParticipationCheck `bson:"participationCheck,omitempty" json:"participationCheck,omitempty"`
}

type ReconciliationParticipationCheck struct {
    Checked           bool                   `json:"checked" bson:"checked"`
    Passed            bool                   `json:"passed" bson:"passed"`
    FailedRequirements []string              `json:"failedRequirements,omitempty" bson:"failedRequirements,omitempty"`
    CheckedAt         time.Time              `json:"checkedAt" bson:"checkedAt"`
    Details           map[string]interface{} `json:"details,omitempty" bson:"details,omitempty"`
}
```

**Lý do:**
- Reconciliation cần re-validate participation requirements
- Track lý do reject nếu không pass (follower drop, etc.)

---

### 1.5 New Model: ParticipationReview (Admin Review Queue)

**File:** `backend/internal/model/mg/participation_review.go` (NEW)

```go
package modelmg

import (
    "time"
    databasemongodb "viewboost/internal/module/database/mongodb"
)

type ParticipationReviewDAO interface {
    GetShare() databasemongodb.IDatabase
}

type ParticipationReviewRaw struct {
    ID          AppID     `bson:"_id"`
    UserEvent   AppID     `bson:"userEvent"` // Reference to user-events
    User        AppID     `bson:"user"`
    Event       AppID     `bson:"event"`
    Partner     AppID     `bson:"partner"`
    Status      string    `bson:"status"` // "pending", "approved", "rejected", "need_more_info"

    // Submission data
    FacebookProfileUrl string   `bson:"facebookProfileUrl,omitempty"`
    ProofScreenshots   []string `bson:"proofScreenshots,omitempty"` // URLs to screenshots
    InvitationCode     string   `bson:"invitationCode,omitempty"`

    // Review data
    ReviewedAt  *time.Time `bson:"reviewedAt,omitempty"`
    ReviewedBy  *AppID     `bson:"reviewedBy,omitempty"` // Admin ID
    ReviewNotes string     `bson:"reviewNotes,omitempty"`

    // Requirements status snapshot
    RequirementsSnapshot map[string]*RequirementStatus `bson:"requirementsSnapshot"`

    CreatedAt   time.Time `bson:"createdAt"`
    UpdatedAt   time.Time `bson:"updatedAt"`
}

func (s *ParticipationReviewRaw) DbModelName() string {
    return databasemongodb.CollectionParticipationReview
}
```

**Lý do:**
- Dedicated collection cho admin review queue
- Separate concern: Review process vs. UserEvent data
- Easier to query pending reviews for admin dashboard

---

## 2. Service Functions Cần Update

### 2.1 Content Service - Submit Content Flow

**File:** `backend/pkg/public/service/content.go`

**Function:** `Create()`

**Hiện tại (lines 83-118):**
```go
func (c contentImpl) Create(ctx context.Context, eventId, userId modelmg.AppID, body request.CreateContentBody) (err error) {
    // ... existing code

    // Check event available
    _ = daomongodb.EventDAO().GetShare().FindOne(ctx, event, bson.M{"_id": eventId})
    if event.ID.IsZero() {
        return errors.New(locale.EventKeyNotFound)
    }
    if !event.IsValid() {
        return errors.New(locale.EventNotYetStartOrFinished)
    }
    if event.Options != nil && !funk.Contains(event.Options.ApplyForSources, body.Source) {
        return errors.New(fmt.Sprintf("Chương trình chỉ chấp nhận bài đăng %s!", strings.Join(event.Options.ApplyForSources, ", ")))
    }

    // ... rest of content creation
}
```

**Cần thêm (sau line 108):**
```go
// Check participation requirements
if event.ParticipationRequirements != nil && event.ParticipationRequirements.Enabled {
    canSubmit, err := c.checkParticipationRequirements(ctx, event, userId)
    if err != nil {
        return err
    }
    if !canSubmit {
        return errors.New("Bạn chưa đủ điều kiện tham gia campaign này. Vui lòng hoàn thành các yêu cầu trước khi gửi bài viết.")
    }
}
```

**New helper function:**
```go
func (c contentImpl) checkParticipationRequirements(ctx context.Context, event *modelmg.EventRaw, userId modelmg.AppID) (bool, error) {
    // Find user-event
    var userEvent = new(modelmg.UserEventRaw)
    _ = daomongodb.UserEventDAO().GetShare().FindOne(ctx, userEvent, bson.M{
        "user": userId,
        "event": event.ID,
    })

    if userEvent.ID.IsZero() {
        // No user-event yet → need to register first
        return false, errors.New("Bạn cần đăng ký tham gia campaign trước.")
    }

    if userEvent.ParticipationStatus == nil {
        return false, errors.New("Vui lòng hoàn thành các điều kiện tham gia.")
    }

    if userEvent.ParticipationStatus.Status != "approved" {
        switch userEvent.ParticipationStatus.Status {
        case "pending_review":
            return false, errors.New("Hồ sơ của bạn đang chờ duyệt. Thời gian duyệt: 1-2 ngày làm việc.")
        case "rejected":
            reason := userEvent.ParticipationStatus.RejectionReason
            if reason == "" {
                reason = "Hồ sơ không đạt yêu cầu."
            }
            return false, errors.New(fmt.Sprintf("Hồ sơ bị từ chối: %s", reason))
        default:
            return false, errors.New("Vui lòng hoàn thành các điều kiện tham gia.")
        }
    }

    // Check if still eligible (not changed since approval)
    // This is optional - you can also defer this to reconciliation

    return true, nil
}
```

---

### 2.2 User Service - Link/Unlink Social

**File:** `backend/pkg/public/service/user.go`

**Functions affected:**
- `ProccessPendingWithLinkSocial()` (line 2498)
- `UnlinkUserSocial()` (line 2573)

**Cần thêm logic:**

Khi user link Facebook account, nếu có pending participation requirements → auto-check requirements mới có thể check được:

```go
// After successful link/unlink, trigger participation requirement check
func (u userImpl) AfterLinkSocial(ctx context.Context, userId AppID, source string) {
    // Find all user-events with pending participation for this user
    var userEvents = make([]*modelmg.UserEventRaw, 0)
    _ = daomongodb.UserEventDAO().GetShare().Find(ctx, new(modelmg.UserEventRaw), bson.M{
        "user": userId,
        "participationStatus.status": "pending_review",
    })(&userEvents)

    for _, ue := range userEvents {
        // Check if event has FB-related requirements
        event := new(modelmg.EventRaw)
        _ = daomongodb.EventDAO().GetShare().FindById(ctx, event, ue.Event)

        if event.ParticipationRequirements != nil {
            // Trigger requirement re-check
            go internalservice.Participation().RecheckRequirements(context.Background(), ue.ID)
        }
    }
}
```

---

### 2.3 Event Schema Service - Milestone Check

**File:** `backend/internal/service/event_schema.go`

**Function:** `CheckPassSchemaTypeByViewMilestoneWithListSchema()` (line 43)

**Hiện tại:**
- Không check participation requirements trước khi tạo milestone reward

**Cần thêm (line 91, trước khi create reward):**
```go
// Check participation requirements before creating milestone reward
if event.ParticipationRequirements != nil && event.ParticipationRequirements.Enabled {
    if userEvent.ParticipationStatus == nil || userEvent.ParticipationStatus.Status != "approved" {
        fmt.Println(aurora.Yellow(fmt.Sprintf("[Milestone] User %s not eligible (participation not approved)", userEvent.User.Hex())))
        return // Don't create reward
    }
}
```

**Lý do:**
- Chỉ user đã approved mới được nhận milestone reward
- Prevent exploit: User submit content trước khi bị reject participation

---

### 2.4 Reconciliation Service - Processing Content

**File:** `backend/pkg/admin/service/reconciliation_processing.go`

**Function:** `ProcessingContent()` - cần xác định location chính xác

**Cần thêm:**

Trong reconciliation flow, cần re-validate participation requirements:

```go
func (r reconciliationImpl) ProcessingContent(ctx context.Context, rc *modelmg.ReconciliationRaw, staffId modelmg.AppID) {
    // ... existing code to get contents

    for _, content := range contents {
        // Re-check participation requirements
        userEvent := new(modelmg.UserEventRaw)
        _ = daomongodb.UserEventDAO().GetShare().FindOne(ctx, userEvent, bson.M{
            "user": content.User,
            "event": content.Event,
        })

        participationCheck := &modelmg.ReconciliationParticipationCheck{
            Checked: true,
            CheckedAt: time.Now(),
        }

        if userEvent.ParticipationStatus == nil || userEvent.ParticipationStatus.Status != "approved" {
            participationCheck.Passed = false
            participationCheck.FailedRequirements = []string{"participation_not_approved"}

            // Reject content in reconciliation
            // ... update reconciliation item status
            continue
        }

        // Re-check specific requirements (e.g., follower count)
        event := new(modelmg.EventRaw)
        _ = daomongodb.EventDAO().GetShare().FindById(ctx, event, content.Event)

        if event.ParticipationRequirements != nil {
            failedReqs := r.recheckParticipationRequirements(ctx, event, userEvent)
            if len(failedReqs) > 0 {
                participationCheck.Passed = false
                participationCheck.FailedRequirements = failedReqs
                // Reject or flag for manual review
                continue
            }
        }

        participationCheck.Passed = true
        // ... proceed with normal reconciliation
    }
}

func (r reconciliationImpl) recheckParticipationRequirements(ctx context.Context, event *modelmg.EventRaw, userEvent *modelmg.UserEventRaw) []string {
    failedReqs := []string{}

    for _, req := range event.ParticipationRequirements.Requirements {
        switch req.Type {
        case "facebook_followers":
            // Re-check follower count
            reqStatus := userEvent.ParticipationStatus.Requirements["facebook_followers"]
            if reqStatus != nil && reqStatus.AutoCheckResult != nil {
                currentCount := reqStatus.Value.(int)
                required := req.Validation.MinFollowers

                if currentCount < required {
                    failedReqs = append(failedReqs, fmt.Sprintf("facebook_followers: %d < %d", currentCount, required))
                }
            }
        }
    }

    return failedReqs
}
```

---

## 3. Validation Checkpoints

### 3.1 ✅ Checkpoint 1: Event Creation/Update (Admin)

**Location:** Admin event service

**Validate:**
- ParticipationRequirements config hợp lệ
- Không có duplicate requirement types
- Validation rules consistent (minFollowers > 0, etc.)

---

### 3.2 ✅ Checkpoint 2: Submit Content (Public)

**Location:** `content.go:Create()` (đã note ở trên)

**Validate:**
- User có user-event record chưa?
- Participation status = "approved"?
- Nếu chưa approved → trả error rõ ràng

---

### 3.3 ✅ Checkpoint 3: Reconciliation

**Location:** `reconciliation_processing.go` (đã note ở trên)

**Validate:**
- Re-check participation requirements
- Đặc biệt: Facebook follower count có drop không?
- Flag cho manual review nếu có thay đổi suspicious

---

## 4. New Services Cần Tạo

### 4.1 Participation Service (NEW)

**File:** `backend/internal/service/participation.go` (NEW)

```go
package internalservice

import (
    "context"
    "viewboost/internal/model/mg"
)

type ParticipationInterface interface {
    // Check requirements for a user-event
    CheckRequirements(ctx context.Context, userEventId modelmg.AppID) (*ParticipationCheckResult, error)

    // Re-check requirements (e.g., after FB link, or periodic)
    RecheckRequirements(ctx context.Context, userEventId modelmg.AppID) error

    // Submit for participation (create user-event + participation review)
    SubmitParticipation(ctx context.Context, userId, eventId modelmg.AppID, data *SubmitParticipationData) error

    // Admin approve/reject
    ApproveParticipation(ctx context.Context, reviewId modelmg.AppID, adminId modelmg.AppID, notes string) error
    RejectParticipation(ctx context.Context, reviewId modelmg.AppID, adminId modelmg.AppID, reason string) error
}

func Participation() ParticipationInterface {
    return &participationImpl{}
}

type participationImpl struct {}

type ParticipationCheckResult struct {
    CanParticipate bool
    Status         string
    Requirements   map[string]*RequirementCheckResult
}

type RequirementCheckResult struct {
    Type    string
    Status  string // "passed", "failed", "pending"
    Message string
}

type SubmitParticipationData struct {
    FacebookProfileUrl string
    ProofScreenshots   []string
    InvitationCode     string
}
```

---

### 4.2 Admin Participation Review Service (NEW)

**File:** `backend/pkg/admin/service/participation_review.go` (NEW)

Tương tự reconciliation review, cần:
- Get review queue
- Approve/reject with notes
- Auto-check follower count (call Facebook Graph API)
- Bulk operations

---

## 5. API Endpoints Cần Tạo

### 5.1 Public APIs

```
GET  /api/v1/events/{eventId}/participation/requirements
     → Get checklist for current user

POST /api/v1/events/{eventId}/participation/submit
     → Submit for participation (with FB URL, screenshots, code)

GET  /api/v1/events/{eventId}/participation/status
     → Get current participation status

POST /api/v1/events/{eventId}/participation/recheck
     → Trigger re-check (e.g., after linking FB)
```

### 5.2 Admin APIs

```
GET  /api/admin/v1/participation-reviews?status=pending
     → Get review queue

GET  /api/admin/v1/participation-reviews/{reviewId}
     → Get review details

POST /api/admin/v1/participation-reviews/{reviewId}/approve
     → Approve participation

POST /api/admin/v1/participation-reviews/{reviewId}/reject
     → Reject participation

POST /api/admin/v1/participation-reviews/{reviewId}/check-followers
     → Manually trigger FB follower count check

GET  /api/admin/v1/events/{eventId}/participation-stats
     → Stats: pending/approved/rejected counts
```

---

## 6. Database Indices Cần Tạo

```javascript
// user-events collection
db.userEvents.createIndex({
    "user": 1,
    "event": 1
}, { unique: true })

db.userEvents.createIndex({
    "participationStatus.status": 1
})

db.userEvents.createIndex({
    "event": 1,
    "participationStatus.status": 1
})

// participation-reviews collection (NEW)
db.participationReviews.createIndex({
    "status": 1,
    "createdAt": -1
})

db.participationReviews.createIndex({
    "userEvent": 1
})

db.participationReviews.createIndex({
    "user": 1,
    "event": 1
})

// contents collection - add index for participation validation timestamp
db.contents.createIndex({
    "user": 1,
    "event": 1,
    "participationValidatedAt": 1
})
```

---

## 7. Critical Edge Cases & Solutions

### 7.1 User approved → Follower count drops → Submit content

**Problem:**
- User có 1,200 followers lúc approved
- 1 tuần sau drop xuống 900 followers
- User submit bài post

**Solution Options:**

**Option 1: Validate at submit time (strict)**
```go
// In content.Create()
if event.ParticipationRequirements.Enabled {
    // Re-check follower count
    currentFollowers := getFacebookFollowers(user.FacebookId)
    required := event.ParticipationRequirements.GetRequirement("facebook_followers").MinFollowers

    if currentFollowers < required {
        return errors.New("Số followers của bạn đã giảm xuống dưới yêu cầu. Vui lòng cập nhật.")
    }
}
```

**Option 2: Allow submit, check at reconciliation (lenient - RECOMMENDED)**
```go
// In content.Create()
// Don't re-check, allow submit

// In reconciliation
// Re-check và reject nếu drop quá nhiều
// Hoặc flag for manual review với grace period
```

**Recommendation:** Option 2 với grace period
- User experience tốt hơn
- Follower count có thể fluctuate tạm thời
- Reconciliation có thể set grace period (e.g., -10% acceptable)

---

### 7.2 User submit content → Admin review participation → Reject

**Problem:**
- User đã submit 2 bài posts
- Admin review hồ sơ → reject
- Content đã submit xử lý thế nào?

**Solution:**
```go
// When admin reject participation
func (p participationImpl) RejectParticipation(ctx context.Context, reviewId, adminId modelmg.AppID, reason string) error {
    // ... update participation status to rejected

    // Find all contents from this user for this event
    contents := make([]*modelmg.ContentRaw, 0)
    _ = daomongodb.ContentDAO().GetShare().Find(ctx, new(modelmg.ContentRaw), bson.M{
        "user": userEvent.User,
        "event": userEvent.Event,
        "status": bson.M{"$in": []string{"waiting_approved", "approved"}},
    })(&contents)

    // Reject all contents
    for _, content := range contents {
        _ = daomongodb.ContentDAO().GetShare().UpdateOne(ctx, new(modelmg.ContentRaw), bson.M{
            "_id": content.ID,
        }, bson.M{
            "$set": bson.M{
                "status": "rejected",
                "note": fmt.Sprintf("Hồ sơ tham gia không đạt yêu cầu: %s", reason),
            },
        })
    }

    // Send notification to user
    // ...
}
```

---

### 7.3 Event requirements change mid-campaign

**Problem:**
- Campaign bắt đầu với requirement: ≥1,000 followers
- 1 tuần sau admin change thành ≥2,000 followers
- User đã approved với 1,200 followers bị ảnh hưởng?

**Solution: Grandfather Rule**
```go
type UserEventParticipationStatus struct {
    // ... existing fields
    RequirementsVersion int       `json:"requirementsVersion" bson:"requirementsVersion"`
    LockedRequirements  []*ParticipationRequirement `json:"lockedRequirements" bson:"lockedRequirements"`
}

// When approve participation
func ApproveParticipation() {
    // Lock current requirements snapshot
    userEvent.ParticipationStatus.RequirementsVersion = event.ParticipationRequirements.Version
    userEvent.ParticipationStatus.LockedRequirements = event.ParticipationRequirements.Requirements

    // Later validation uses LockedRequirements, not current event requirements
}
```

---

### 7.4 Facebook Graph API rate limit / outage

**Problem:**
- Admin review 100 profiles
- Click "Check Followers" button
- Graph API hit rate limit or down

**Solution: Graceful degradation + Queue**
```go
func (p participationImpl) CheckFacebookFollowers(ctx context.Context, reviewId modelmg.AppID) error {
    // Try API first
    count, err := callFacebookGraphAPI(facebookUserId)

    if err != nil {
        // Check error type
        if isRateLimitError(err) {
            // Queue for retry later
            _ = queueFacebookCheck(reviewId, time.Now().Add(1 * time.Hour))
            return errors.New("Facebook API rate limit. Sẽ tự động kiểm tra lại sau 1 giờ.")
        }

        if isAPIDownError(err) {
            // Flag for manual check
            _ = updateReview(reviewId, bson.M{
                "$set": bson.M{
                    "requirements.facebook_followers.status": "manual_required",
                    "requirements.facebook_followers.notes": "Facebook API tạm thời không khả dụng. Vui lòng kiểm tra thủ công bằng screenshot.",
                },
            })
            return errors.New("Facebook API không khả dụng. Đã chuyển sang kiểm tra thủ công.")
        }

        return err
    }

    // Success
    _ = updateReview(reviewId, bson.M{
        "$set": bson.M{
            "requirements.facebook_followers.status": "passed",
            "requirements.facebook_followers.autoCheckResult": map[string]interface{}{
                "success": true,
                "count": count,
            },
        },
    })

    return nil
}
```

---

## 8. Implementation Roadmap

### Phase 1: Foundation (Week 1)
- ✅ Create new models (ParticipationReview, extend UserEvent, Event)
- ✅ Database migrations
- ✅ Create indices
- ✅ Basic Participation service

### Phase 2: Public Flow (Week 2)
- ✅ Public APIs (get requirements, submit participation)
- ✅ Update Content.Create() with participation check
- ✅ Frontend integration

### Phase 3: Admin Review (Week 3)
- ✅ Admin review queue APIs
- ✅ Admin dashboard UI
- ✅ Facebook Graph API integration
- ✅ Manual override flows

### Phase 4: Reconciliation Integration (Week 4)
- ✅ Update reconciliation flow
- ✅ Re-validation logic
- ✅ Edge case handling
- ✅ Testing

### Phase 5: Polish & Launch (Week 5)
- ✅ Scheduled jobs (follower re-check)
- ✅ Notifications
- ✅ Analytics
- ✅ Documentation
- ✅ Soft launch với 1 event

---

## 9. Testing Checklist

### Unit Tests
- [ ] Participation requirement validation
- [ ] Auto-check logic (account age, invitation code)
- [ ] Follower count check (with mocked FB API)

### Integration Tests
- [ ] Submit participation flow (end-to-end)
- [ ] Admin approve/reject flow
- [ ] Content submit with participation check
- [ ] Reconciliation re-validation

### Edge Case Tests
- [ ] Follower drop scenario
- [ ] Mid-campaign requirement change
- [ ] Facebook API failure handling
- [ ] Concurrent submissions

### Performance Tests
- [ ] Admin review queue with 10,000 pending reviews
- [ ] Reconciliation with 100,000 contents
- [ ] Bulk follower checks (rate limit handling)

---

## 10. Monitoring & Alerts

### Metrics to Track
```
participation.submissions.total (counter)
participation.submissions.approved (counter)
participation.submissions.rejected (counter)
participation.review_duration (histogram) // Time from submit to approve/reject

participation.facebook_api.success (counter)
participation.facebook_api.failures (counter)
participation.facebook_api.rate_limits (counter)

reconciliation.participation_rejects (counter)
reconciliation.participation_follower_drops (counter)
```

### Alerts
- [ ] Participation review queue > 100 pending for >24h
- [ ] Facebook API error rate > 10%
- [ ] Reconciliation rejection rate > 20% (investigate requirements)

---

## 11. Documentation Needs

### For Developers
- [ ] API documentation (Swagger)
- [ ] Architecture diagram (flow chart)
- [ ] Database schema documentation
- [ ] Testing guide

### For Admins
- [ ] How to configure participation requirements
- [ ] Review queue workflow
- [ ] Manual override procedures
- [ ] Troubleshooting guide

### For Users
- [ ] How to submit participation
- [ ] Requirements explanation
- [ ] FAQ (Why rejected? How long review takes?)
- [ ] Screenshot guidelines

---

## 12. Summary: Critical Action Items

### Must Do Before Launch:
1. ✅ **Extend 5 models:** Event, UserEvent, Content, ReconciliationItem, new ParticipationReview
2. ✅ **Update 4 services:** Content, User, EventSchema, Reconciliation
3. ✅ **Create 2 new services:** Participation, Admin ParticipationReview
4. ✅ **Add validation at 3 checkpoints:** Event config, Content submit, Reconciliation
5. ✅ **Create 12 API endpoints:** 4 public + 8 admin
6. ✅ **Database indices:** 6 new indices
7. ✅ **Handle 4 critical edge cases:** Follower drop, reject after submit, mid-campaign change, API failure

### Nice to Have (Post-MVP):
- Automated follower re-check (daily cron)
- Advanced analytics dashboard
- Bulk approval tools
- ML-based fraud detection
- Multi-language support for requirements

---

**Conclusion:**
Backend architecture hiện tại **sẵn sàng** cho tính năng participation requirements. Cần ~5 tuần development với team size: 1 backend dev + 1 frontend dev + 0.5 QA.

Risk level: **MEDIUM** (phụ thuộc vào Facebook Graph API stability)

---

*Generated: 2026-02-07*
*Author: Code Audit Tool*
