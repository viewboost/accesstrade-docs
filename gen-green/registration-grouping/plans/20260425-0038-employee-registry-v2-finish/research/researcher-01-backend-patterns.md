# Backend Patterns Research — vcreator (Gen-Green Employee Registry v2)

**Date:** 2026-04-24  
**For:** FR-009 (registry lookup on register), FR-013 (auto staff removal), FR-014 (notifications)

---

## 1. Scheduled Job / Cron Pattern

**Files đã đọc:**
- `go.mod` (line 28): `github.com/robfig/cron/v3 v3.0.1`
- `pkg/public/schedule/schedule.go` (lines 1–48)
- `pkg/admin/schedule/init.go` (referenced)
- `pkg/file/schedule/schedule.go` (referenced)

**Findings:**
- vcreator đã dùng **robfig/cron/v3** framework (init: `cron.New(cron.WithLocation(l), cron.WithSeconds())`)
- Cron spec format: **standard 6-field** (includes seconds), timezone-aware (Asia/Ho_Chi_Minh)
- 10+ scheduled tasks đang chạy: RunCheckPassSchemaStatisticAfterDay, CrawlDataContentTiktok, CrawlDataContent, ProcessContentCallback, UpdateContractStatus, SyncOpsHubContents, v.v.
- Entry point: `schedule.Init()` gọi `c.Start()` — chạy chung với main API process (not separate daemon)
- Pattern: define `AddFunc(cronExpr, serviceMethod)` → framework handles timing/execution
- Error handling: các scheduled tasks bên trong service layer (`service.Schedule().Method()`)

**Code snippet:**
```go
// pkg/public/schedule/schedule.go
func Init() {
	l, _ := time.LoadLocation("Asia/Ho_Chi_Minh")
	c := cron.New(cron.WithLocation(l), cron.WithSeconds())
	
	// Daily check at 00:30
	c.AddFunc("0 30 0 * * *", service.Schedule().RunCheckPassSchemaStatisticAfterDay)
	// Every 15 min
	c.AddFunc("0 */15 * * * *", service.Schedule().UpdateContractStatus)
	
	c.Start()
}
```

**Implications cho đợt 2+3:**
- FR-013 cron: `"0 0 0 * * *"` (daily 00:00) để check `staffRemovalScheduledAt < now()` và remove staff tag
- Thêm `schedule.Init()` call vào `cmd/public/main.go` nếu chưa có
- Scheduled task method phải implement retry logic & error logging (zap logger)

---

## 2. Notification Service API Signature

**Files đã đọc:**
- `internal/service/notification.go` (lines 1–60)
- `internal/constants/notification.go` (lines 1–56)

**Findings:**
- Interface `NotificationInterface.Push(ctx context.Context, n []*modelmg.NotificationRaw) error`
- Payload: `*modelmg.NotificationRaw` struct (MongoDB document, FirebaseCloud Messaging sink)
- Existing types: `NotificationTypeStaffVerifySuccess`, `NotificationTypeStaffVerifyFailed` (line 15–16)
- No types yet cho: `auto_verified`, `cancelled_mismatch`, `workplace_updated`, `staff_removed_scheduled`, `staff_removed`
- Notification categories: Event, Other, Bonus (line 20–22)
- Push flow: insert many → broadcast to Firebase (async batched, line 55, with `wg.Add()`)

**Code snippet:**
```go
// internal/constants/notification.go
const (
	NotificationTypeStaffVerifySuccess = "staff_verify_success"
	NotificationTypeStaffVerifyFailed  = "staff_verify_failed"
	// TODO: Add for FR-014
	// NotificationTypeAutoVerified = "auto_verified"
	// NotificationTypeStaffRemovedScheduled = "staff_removed_scheduled"
)

// internal/service/notification.go
func (ns notificationImpl) Push(ctx context.Context, n []*modelmg.NotificationRaw) error {
	notiInterface := make([]interface{}, 0)
	for _, no := range n {
		if no.Partner.IsZero() {
			no.IsAllPartner = true
		}
		notiInterface = append(notiInterface, no)
	}
	
	err := daomongodb.NotificationDAO().GetShare().InsertMany(ctx, new(modelmg.NotificationRaw), notiInterface)
	// ... async Firebase push
}
```

**Implications cho đợt 2+3:**
- Define 5 new constants cho FR-014 notification types (trong `internal/constants/notification.go`)
- Call `internalservice.Notification().Push()` từ FR-009 (CompleteProfile), FR-013 (scheduled removal), FR-014 UI handlers
- Check `modelmg.NotificationRaw` struct để hiểu payload fields (title, content, deeplink, user_id, partner_id, etc.)

---

## 3. User Register Flow (Public)

**Files đã đọc:**
- `pkg/public/handler/user.go` (interface lines 20–78, CompleteProfile line 1015–1028)
- `pkg/public/service/user.go` (CompleteProfile service impl lines 2801–2860)

**Findings:**
- Endpoint: **`POST /users/complete-profile`** (handler `CompleteProfile(c echo.Context) error`)
- Flow: user completed phone verification → call CompleteProfile → set `profileCompletedAt`, `staffStatus=pending`, `employeeCode` (if submitted)
- Current logic (line 2925–2926): if `body.EmployeeCode` provided → auto-set `staffStatus = StaffStatusPending`
- Check validation: phone unique, email unique, email verified (auto-verified if Google login)
- No registry lookup YET in this flow — placeholder for FR-009

**Code snippet:**
```go
// pkg/public/service/user.go:2801
func (u userImpl) CompleteProfile(ctx context.Context, userId primitive.ObjectID, body request.CompleteProfileBody) error {
	user := new(modelmg.UserRaw)
	daomongodb.UserDAO().GetShare().FindById(ctx, user, userId)
	
	// ... validations (phone/email unique, verified)
	
	now := time.Now()
	set := bson.M{
		"name":  body.Name,
		"email": body.Email,
		"phone": modelmg.Phone{...},
		"profileCompletedAt": now,
		"updatedAt": now,
	}
	if body.EmployeeCode != "" {
		set["employeeCode"] = body.EmployeeCode
		set["staffStatus"] = constants.StaffStatusPending  // line 2926
	}
	// ... update user in DB
}
```

**Implications cho đợt 2+3:**
- FR-009 hook: after `body.EmployeeCode` set, call `registryService.LookupStaff(ctx, employeeCode)` → auto-verify if match (set `staffStatus = StaffStatusAutoVerified`, `staffVerifiedAt`)
- Notification push: `NotificationTypeAutoVerified` when lookup succeeds
- Error path: `staffStatus = StaffStatusMismatch` → user sees rejection reason, can retry
- Response: return lookup result to frontend (auto_verified, mismatch_details, pending_manual_review)

---

## Unresolved Questions

1. **modelmg.NotificationRaw structure**: phần nào là required fields (user_id, type, title, content, deeplink)?
2. **Registry service integration**: endpoint URL, auth header, payload schema từ external registry API?
3. **Scheduled removal timing**: sau 7 ngày từ `staffRemovalScheduledAt`, hay từ `staffVerifiedAt` lỗi → xóa ngay?
