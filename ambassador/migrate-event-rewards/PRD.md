# Backfill Missing Event-Reward Migration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Thêm 1 API admin (POST, body validate, chạy nền) quét `content-analytic-daily` theo `event` + khoảng thời gian, với mỗi daily tái dùng **đúng luồng tạo reward thật** (`UpdateRewardTypeByStatisticContent`) để tạo event-reward còn thiếu (idempotent, có budget), và đánh dấu reward do migration tạo bằng flag `fromMigration`.

**Architecture:** KHÔNG tự build reward, KHÔNG dùng `event-reward-temps`. Migration chỉ điều phối: loop `content-analytic-daily` theo scope → với mỗi doc gọi `internalservice.EventSchema().UpdateRewardTypeByStatisticContent(ctx, content, doc, fromMigration=true)`. Hàm thật này đã idempotent (`findRewardPair` không lọc status: chưa có → insert, có rồi → update) và đã xử lý budget (BPE/BPU/BPC, primary/overflow) qua `processRewardForSchema`. Flag `fromMigration` được luồn qua `processRewardParams` và set **chỉ ở INSERT path** của `upsertPrimaryReward`/`upsertOverflowReward` (không đụng UPDATE path để không xóa flag cũ). 3 layer của API mới (router / handler / service) tách **file riêng** theo yêu cầu, không nhét vào `migration.go`.

**Tech Stack:** Go 1.24, Echo v4, MongoDB (mongo-go-driver), ozzo-validation v4, module path `viewboost`.

## Global Constraints

- Module import path `viewboost`.
- Collections: `event-rewards` (`databasemongodb.CollectionEventReward`), `content-analytic-daily` (`CollectionContentAnalyticDaily`).
- Reward do migration tạo phải đi qua **đúng luồng thật** `UpdateRewardTypeByStatisticContent` → `processRewardForSchema` (giữ budget/overflow), KHÔNG tự build, KHÔNG temp.
- Flag `fromMigration` set **chỉ khi INSERT reward mới**; UPDATE path giữ nguyên giá trị cũ.
- `dryRun=true` → chỉ đếm số `content-analytic-daily` trong scope + log, KHÔNG gọi `UpdateRewardTypeByStatisticContent`, KHÔNG ghi DB.
- 3 caller cũ của `UpdateRewardTypeByStatisticContent` phải truyền `fromMigration=false` (giữ nguyên hành vi production).
- Log bằng `github.com/logrusorgru/aurora`.
- Build sạch: `go build ./...`, `go vet ./...` từ thư mục `backend/`.
- API mới tách file riêng: `router/backfill_event_reward.go`, `handler/backfill_event_reward.go`, `service/backfill_event_reward.go`, `model/request/backfill_event_reward.go`, `routevalidation/backfill_event_reward.go`.

---

### Task 1: Thêm field `FromMigration` vào model EventRewardRaw

**Files:**
- Modify: `backend/internal/model/mg/event_reward.go:31`

**Interfaces:**
- Consumes: (none)
- Produces: field `EventRewardRaw.FromMigration bool` (bson/json `fromMigration`). Task 2 set khi INSERT reward từ migration.

- [ ] **Step 1: Thêm field**

Trong `backend/internal/model/mg/event_reward.go`, đổi block dòng 31-34:

```go
	FromSystem          bool                 `bson:"fromSystem" json:"fromSystem"`
	IsBudgetExceeded    bool                 `bson:"isBudgetExceeded" json:"isBudgetExceeded"`
	RecheckInProgress   bool                 `bson:"recheckInProgress,omitempty" json:"recheckInProgress,omitempty"`
	Note                string               `bson:"note" json:"note"`
```

thành:

```go
	FromSystem          bool                 `bson:"fromSystem" json:"fromSystem"`
	FromMigration       bool                 `bson:"fromMigration,omitempty" json:"fromMigration,omitempty"`
	IsBudgetExceeded    bool                 `bson:"isBudgetExceeded" json:"isBudgetExceeded"`
	RecheckInProgress   bool                 `bson:"recheckInProgress,omitempty" json:"recheckInProgress,omitempty"`
	Note                string               `bson:"note" json:"note"`
```

- [ ] **Step 2: Verify compile**

Run: `cd backend && go build ./internal/model/mg/`
Expected: exit 0.

- [ ] **Step 3: Commit**

```bash
git add backend/internal/model/mg/event_reward.go
git commit -m "feat(event-reward): add fromMigration flag to EventRewardRaw"
```

---

### Task 2: Luồn flag `fromMigration` qua reward pipeline (đụng core — cẩn thận)

**Files:**
- Modify: `backend/internal/service/event_schema.go:50-59` (struct `processRewardParams`)
- Modify: `backend/internal/service/event_schema.go:313-335` (`upsertPrimaryReward` INSERT path)
- Modify: `backend/internal/service/event_schema.go:365-388` (`upsertOverflowReward` INSERT path)
- Modify: `backend/internal/service/event_schema.go:29` (interface `EventSchemaInterface`)
- Modify: `backend/internal/service/event_schema.go:718-797` (`UpdateRewardTypeByStatisticContent` signature + build params)
- Modify: `backend/internal/service/event_schema.go:843` (caller nội bộ)
- Modify: `backend/internal/service/content_analytic_daily.go:158,461` (2 caller)

**Interfaces:**
- Consumes: `EventRewardRaw.FromMigration` (Task 1).
- Produces: signature mới `UpdateRewardTypeByStatisticContent(ctx context.Context, content *modelmg.ContentRaw, doc *modelmg.ContentAnalyticDailyRaw, fromMigration bool)`. Task 5 gọi với `fromMigration=true`.

- [ ] **Step 1: Thêm field vào `processRewardParams`**

Trong `backend/internal/service/event_schema.go`, đổi struct (dòng 50-59):

```go
// processRewardParams holds all inputs for processRewardForSchema.
type processRewardParams struct {
	Event   *modelmg.EventRaw
	Content *modelmg.ContentRaw
	Schema  *modelmg.EventSchemaRaw
	Doc     *modelmg.ContentAnalyticDailyRaw
	Status  string // derived from content status (pending/waitingApproved/rejected)
	// Pre-computed full statistic for this content+schema+date
	FullStat modelmg.EventRewardStatistic
	FullCash float64
}
```

thành (thêm `FromMigration`):

```go
// processRewardParams holds all inputs for processRewardForSchema.
type processRewardParams struct {
	Event   *modelmg.EventRaw
	Content *modelmg.ContentRaw
	Schema  *modelmg.EventSchemaRaw
	Doc     *modelmg.ContentAnalyticDailyRaw
	Status  string // derived from content status (pending/waitingApproved/rejected)
	// Pre-computed full statistic for this content+schema+date
	FullStat modelmg.EventRewardStatistic
	FullCash float64
	// FromMigration đánh dấu reward MỚI được sinh bởi migration backfill. Chỉ set
	// khi INSERT (không đụng UPDATE path để giữ nguyên flag của reward đã tồn tại).
	FromMigration bool
}
```

- [ ] **Step 2: Set flag ở INSERT path của `upsertPrimaryReward`**

Trong `upsertPrimaryReward` (nhánh `else` — INSERT, dòng 314-335), đổi struct literal reward: thêm `FromMigration: p.FromMigration` ngay dưới `FromSystem: true,`:

```go
			EventOptions:     p.Event.Options,
			CreatedAt:        now,
			Statistic:        stat,
			UpdatedAt:        now,
			Options:          &modelmg.EventRewardOpts{ContentID: p.Content.ID, Source: p.Content.Source},
			FromSystem:       true,
			FromMigration:    p.FromMigration,
			IsBudgetExceeded: isBudgetExceeded,
		}
```

> Không sửa nhánh UPDATE (dòng 295-312) — reward đã tồn tại giữ nguyên `fromMigration` cũ.

- [ ] **Step 3: Set flag ở INSERT path của `upsertOverflowReward`**

Trong `upsertOverflowReward` (nhánh `else` — INSERT, dòng 366-388), thêm `FromMigration: p.FromMigration` ngay dưới `FromSystem: true,`:

```go
			EventOptions:     p.Event.Options,
			CreatedAt:        now,
			Statistic:        stat,
			UpdatedAt:        now,
			Options:          &modelmg.EventRewardOpts{ContentID: p.Content.ID, Source: p.Content.Source},
			FromSystem:       true,
			FromMigration:    p.FromMigration,
			IsBudgetExceeded: true,
		}
```

> Không sửa nhánh UPDATE (dòng 347-364).

- [ ] **Step 4: Đổi signature interface**

Trong `backend/internal/service/event_schema.go` dòng 29, đổi:

```go
	UpdateRewardTypeByStatisticContent(ctx context.Context, content *modelmg.ContentRaw, doc *modelmg.ContentAnalyticDailyRaw)
```

thành:

```go
	UpdateRewardTypeByStatisticContent(ctx context.Context, content *modelmg.ContentRaw, doc *modelmg.ContentAnalyticDailyRaw, fromMigration bool)
```

- [ ] **Step 5: Đổi signature impl + build params với flag**

Đổi dòng khai báo hàm (dòng 718):

```go
func (e eventSchemaImpl) UpdateRewardTypeByStatisticContent(ctx context.Context, c *modelmg.ContentRaw, doc *modelmg.ContentAnalyticDailyRaw) {
```

thành:

```go
func (e eventSchemaImpl) UpdateRewardTypeByStatisticContent(ctx context.Context, c *modelmg.ContentRaw, doc *modelmg.ContentAnalyticDailyRaw, fromMigration bool) {
```

Rồi trong thân hàm, tại chỗ build `processRewardParams` (dòng 789-797), thêm `FromMigration: fromMigration`:

```go
			processRewardForSchema(ctx, processRewardParams{
				Event:         event,
				Content:       content,
				Schema:        schema,
				Doc:           doc,
				Status:        status,
				FullStat:      fullStat,
				FullCash:      fullCash,
				FromMigration: fromMigration,
			})
```

- [ ] **Step 6: Sửa 3 caller cũ truyền `false`**

1. `backend/internal/service/event_schema.go:843` — trong `RecheckSchemaWithContentWhenChangeStatus`, đổi:
```go
			e.UpdateRewardTypeByStatisticContent(ctx, content, doc)
```
thành:
```go
			e.UpdateRewardTypeByStatisticContent(ctx, content, doc, false)
```

2. `backend/internal/service/content_analytic_daily.go:158`, đổi:
```go
		EventSchema().UpdateRewardTypeByStatisticContent(ctx, content, doc)
```
thành:
```go
		EventSchema().UpdateRewardTypeByStatisticContent(ctx, content, doc, false)
```

3. `backend/internal/service/content_analytic_daily.go:461`, đổi:
```go
		EventSchema().UpdateRewardTypeByStatisticContent(ctx, content, doc)
```
thành:
```go
		EventSchema().UpdateRewardTypeByStatisticContent(ctx, content, doc, false)
```

- [ ] **Step 7: Verify compile + vet toàn repo (bắt sót caller)**

Run: `cd backend && go build ./... && go vet ./internal/service/`
Expected: exit 0. Nếu còn caller nào chưa sửa, compile sẽ báo "not enough arguments" — sửa nốt.

- [ ] **Step 8: Commit**

```bash
git add backend/internal/service/event_schema.go backend/internal/service/content_analytic_daily.go
git commit -m "feat(event-reward): thread fromMigration flag through reward upsert pipeline"
```

---

### Task 3: Request body + Validate + unit test (TDD)

**Files:**
- Create: `backend/pkg/admin/model/request/backfill_event_reward.go`
- Test: `backend/pkg/admin/model/request/backfill_event_reward_test.go`

**Interfaces:**
- Consumes: `github.com/go-ozzo/ozzo-validation/v4`, `.../v4/is`.
- Produces: `type BackfillEventRewardBody struct { Event string; FromAt string; ToAt string; DryRun bool }` + `func (p BackfillEventRewardBody) Validate() error`. Task 4 bind, Task 6 consume.

- [ ] **Step 1: Viết test thất bại**

Tạo `backend/pkg/admin/model/request/backfill_event_reward_test.go`:

```go
package request

import "testing"

func TestBackfillEventRewardBody_Validate(t *testing.T) {
	tests := []struct {
		name  string
		body  BackfillEventRewardBody
		valid bool
	}{
		{
			name:  "valid_event_only",
			body:  BackfillEventRewardBody{Event: "665f1c2a3b4d5e6f7a8b9c0d"},
			valid: true,
		},
		{
			name: "valid_with_date_range",
			body: BackfillEventRewardBody{
				Event:  "665f1c2a3b4d5e6f7a8b9c0d",
				FromAt: "2026-06-01T00:00:00Z",
				ToAt:   "2026-06-30T00:00:00Z",
			},
			valid: true,
		},
		{
			name:  "missing_event",
			body:  BackfillEventRewardBody{Event: ""},
			valid: false,
		},
		{
			name:  "event_not_objectid",
			body:  BackfillEventRewardBody{Event: "not-a-hex"},
			valid: false,
		},
		{
			name: "fromAt_bad_format",
			body: BackfillEventRewardBody{
				Event:  "665f1c2a3b4d5e6f7a8b9c0d",
				FromAt: "01-06-2026",
			},
			valid: false,
		},
		{
			name: "toAt_bad_format",
			body: BackfillEventRewardBody{
				Event: "665f1c2a3b4d5e6f7a8b9c0d",
				ToAt:  "2026/06/30",
			},
			valid: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.body.Validate()
			if tt.valid && err != nil {
				t.Fatalf("expected valid, got: %v", err)
			}
			if !tt.valid && err == nil {
				t.Fatalf("expected invalid, got nil")
			}
		})
	}
}
```

- [ ] **Step 2: Chạy test — xác nhận FAIL**

Run: `cd backend && go test ./pkg/admin/model/request/ -run TestBackfillEventRewardBody_Validate -v`
Expected: FAIL — `undefined: BackfillEventRewardBody`.

- [ ] **Step 3: Tạo request body**

Tạo `backend/pkg/admin/model/request/backfill_event_reward.go`:

```go
package request

import (
	"time"

	validation "github.com/go-ozzo/ozzo-validation/v4"
	"github.com/go-ozzo/ozzo-validation/v4/is"
)

// BackfillEventRewardBody — body cho POST /migration/backfill-event-reward.
//
// Quét content-analytic-daily thuộc Event (bắt buộc) trong khoảng [FromAt, ToAt]
// (optional) và tạo event-reward còn thiếu qua đúng luồng thật
// (UpdateRewardTypeByStatisticContent, idempotent + có budget). Reward mới được
// đánh dấu fromMigration=true.
//
// DryRun=true → chỉ đếm daily trong scope + log, KHÔNG tạo reward.
type BackfillEventRewardBody struct {
	// Event bắt buộc: event._id hex 24-char.
	Event string `json:"event"`
	// FromAt optional (RFC3339, vd "2026-06-01T00:00:00Z"): chỉ xử lý daily có
	// date >= FromAt. Rỗng = không giới hạn cận dưới.
	FromAt string `json:"fromAt,omitempty"`
	// ToAt optional (RFC3339): chỉ xử lý daily có date <= ToAt. Rỗng = không
	// giới hạn cận trên.
	ToAt string `json:"toAt,omitempty"`
	// DryRun bắt buộc (middleware ép có mặt): true = chỉ đếm, KHÔNG ghi DB.
	DryRun bool `json:"dryRun"`
}

func (p BackfillEventRewardBody) Validate() error {
	return validation.ValidateStruct(&p,
		validation.Field(&p.Event, validation.Required, is.MongoID),
		validation.Field(&p.FromAt, validation.Date(time.RFC3339)),
		validation.Field(&p.ToAt, validation.Date(time.RFC3339)),
	)
}
```

> `validation.Date(layout)` bỏ qua chuỗi rỗng nên FromAt/ToAt vẫn optional.

- [ ] **Step 4: Chạy test — xác nhận PASS**

Run: `cd backend && go test ./pkg/admin/model/request/ -run TestBackfillEventRewardBody_Validate -v`
Expected: PASS toàn bộ 6 case.

- [ ] **Step 5: Commit**

```bash
git add backend/pkg/admin/model/request/backfill_event_reward.go backend/pkg/admin/model/request/backfill_event_reward_test.go
git commit -m "feat(backfill-event-reward): add request body + validation"
```

---

### Task 4: Validation middleware (file riêng)

**Files:**
- Create: `backend/pkg/admin/router/routevalidation/backfill_event_reward.go`

**Interfaces:**
- Consumes: `request.BackfillEventRewardBody` (Task 3), `constants.KeyPayload`.
- Produces: `type BackfillEventReward struct{}` + `func (m BackfillEventReward) Body(next echo.HandlerFunc) echo.HandlerFunc`. Task 7 dùng làm middleware route.

- [ ] **Step 1: Tạo middleware**

Tạo `backend/pkg/admin/router/routevalidation/backfill_event_reward.go`:

```go
package routevalidation

import (
	"bytes"
	"encoding/json"
	"io"
	"strings"

	"github.com/labstack/echo/v4"

	"viewboost/internal/constants"
	echocustom "viewboost/internal/echo"
	"viewboost/pkg/admin/model/request"
)

// BackfillEventReward — validation cho POST /migration/backfill-event-reward.
type BackfillEventReward struct {
}

// Body bind + validate body. Ép "dryRun" có mặt: endpoint tạo reward thật nên
// không được chạy nhầm bằng default zero-value (curl thiếu body).
func (m BackfillEventReward) Body(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		var (
			cc      = echocustom.EchoGetCustomCtx(c)
			payload request.BackfillEventRewardBody
		)

		raw, err := io.ReadAll(c.Request().Body)
		if err != nil {
			return cc.Response400(nil, "Không đọc được body")
		}
		c.Request().Body = io.NopCloser(bytes.NewBuffer(raw))

		if trimmed := strings.TrimSpace(string(raw)); trimmed == "" || trimmed == "{}" {
			return cc.Response400(nil, "Body bắt buộc, không được rỗng. Phải có ít nhất field event và dryRun.")
		}

		var rawMap map[string]json.RawMessage
		if err := json.Unmarshal(raw, &rawMap); err != nil {
			return cc.Response400(nil, "Body không phải JSON hợp lệ")
		}
		if _, ok := rawMap["dryRun"]; !ok {
			return cc.Response400(nil, "Field dryRun bắt buộc (true|false)")
		}

		if err := c.Bind(&payload); err != nil {
			return cc.Response400(nil, "")
		}
		if err := payload.Validate(); err != nil {
			return cc.ValidationError(err)
		}

		c.Set(constants.KeyPayload, payload)
		return next(c)
	}
}
```

- [ ] **Step 2: Verify compile**

Run: `cd backend && go build ./pkg/admin/router/routevalidation/`
Expected: exit 0.

- [ ] **Step 3: Commit**

```bash
git add backend/pkg/admin/router/routevalidation/backfill_event_reward.go
git commit -m "feat(backfill-event-reward): add validation middleware"
```

---

### Task 5: Service (file riêng) — điều phối backfill qua luồng reward thật

**Files:**
- Create: `backend/pkg/admin/service/backfill_event_reward.go`

**Interfaces:**
- Consumes: `internalservice.EventSchema().UpdateRewardTypeByStatisticContent(ctx, content, doc, fromMigration)` (Task 2); `util.GetAppIDFromHex`; `mgquery.CommonQuery`.
- Produces: accessor + interface:
  - `func BackfillEventReward() BackfillEventRewardInterface`
  - `type BackfillEventRewardInterface interface { Run(eventID string, fromAt, toAt time.Time, dryRun bool) }`
  Task 6 (handler) gọi `go service.BackfillEventReward().Run(...)`.

- [ ] **Step 1: Tạo service**

Tạo `backend/pkg/admin/service/backfill_event_reward.go`:

```go
package service

import (
	"context"
	"fmt"
	"time"

	"viewboost/internal/constants"
	modelmg "viewboost/internal/model/mg"
	daomongodb "viewboost/internal/module/database/mongodb/dao"
	internalservice "viewboost/internal/service"
	"viewboost/internal/util"
	"viewboost/internal/util/mgquery"

	"github.com/logrusorgru/aurora"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

// BackfillEventRewardInterface ...
type BackfillEventRewardInterface interface {
	// Run quét content-analytic-daily thuộc eventID trong [fromAt, toAt] (bỏ qua
	// nếu zero) và tạo event-reward còn thiếu qua đúng luồng thật
	// (UpdateRewardTypeByStatisticContent — idempotent + có budget), đánh dấu
	// fromMigration=true. dryRun=true chỉ đếm + log, không tạo reward.
	Run(eventID string, fromAt, toAt time.Time, dryRun bool)
}

// BackfillEventReward ...
func BackfillEventReward() BackfillEventRewardInterface {
	return &backfillEventRewardImpl{}
}

type backfillEventRewardImpl struct {
}

func (s backfillEventRewardImpl) Run(eventID string, fromAt, toAt time.Time, dryRun bool) {
	var (
		ctx  = context.Background()
		cond = bson.M{
			"event": util.GetAppIDFromHex(eventID),
		}
		q = mgquery.CommonQuery{
			Page:  0,
			Limit: 1000,
			SortInterface: bson.D{
				{"_id", 1},
			},
		}
		lastId       primitive.ObjectID
		totalDaily   int
		totalSkipped int
	)

	dateCond := bson.M{}
	if !fromAt.IsZero() {
		dateCond["$gte"] = fromAt
	}
	if !toAt.IsZero() {
		dateCond["$lte"] = toAt
	}
	if len(dateCond) > 0 {
		cond["date"] = dateCond
	}

	mode := ""
	if dryRun {
		mode = " (DRY-RUN)"
	}
	fmt.Println(aurora.Green("*** Start BackfillEventReward event=" + eventID + mode))

	for {
		if !lastId.IsZero() {
			cond["_id"] = bson.M{
				"$gt": lastId,
			}
		}
		var (
			data = make([]*modelmg.ContentAnalyticDailyRaw, 0)
		)
		_ = daomongodb.ContentAnalyticDailyDAO().GetShare().Find(ctx, new(modelmg.ContentAnalyticDailyRaw), cond, q.GetFindOptsUsingPage())(&data)
		if len(data) == 0 {
			break
		}
		for _, doc := range data {
			totalDaily++
			if dryRun {
				fmt.Println("[DRY-RUN] daily=", doc.ID.Hex(), " content=", doc.Content.Hex(), " date=", doc.Date.Format("2006-01-02"))
				continue
			}
			var (
				content = new(modelmg.ContentRaw)
			)
			_ = daomongodb.ContentDAO().GetShare().FindById(ctx, content, doc.Content)
			if content.ID.IsZero() {
				totalSkipped++
				continue
			}
			// Tái dùng đúng luồng tạo reward thật: idempotent (chưa có → insert,
			// có rồi → update), giữ budget/overflow, đánh dấu fromMigration=true.
			internalservice.EventSchema().UpdateRewardTypeByStatisticContent(ctx, content, doc, true)
		}
		lastId = data[len(data)-1].ID
		fmt.Println("LastId : ", lastId.Hex())
	}

	fmt.Println(aurora.Green(fmt.Sprintf("*** Finish BackfillEventReward%s — daily scanned: %d, skipped(content missing): %d", mode, totalDaily, totalSkipped)))
}

// đảm bảo constants được dùng (import không thừa) — dùng ở nơi khác nếu cần.
var _ = constants.StatusActive
```

> Ghi chú: nếu sau khi viết mà `constants` không được dùng ở đâu, xóa import `constants` và dòng `var _ = constants.StatusActive`. Giữ import gọn theo `go vet`.

- [ ] **Step 2: Verify compile + vet + gỡ import thừa**

Run: `cd backend && go build ./pkg/admin/service/ && go vet ./pkg/admin/service/`
Expected: exit 0. Nếu báo `constants imported and not used`, xóa dòng `var _ = constants.StatusActive` và import `"viewboost/internal/constants"`.

- [ ] **Step 3: Commit**

```bash
git add backend/pkg/admin/service/backfill_event_reward.go
git commit -m "feat(backfill-event-reward): service reuses real reward flow (idempotent, budget-aware)"
```

---

### Task 6: Handler (file riêng)

**Files:**
- Create: `backend/pkg/admin/handler/backfill_event_reward.go`

**Interfaces:**
- Consumes: `service.BackfillEventReward().Run(...)` (Task 5); `request.BackfillEventRewardBody` (Task 3); `constants.KeyPayload`.
- Produces: `type BackfillEventReward struct{}` + `func (h BackfillEventReward) Run(c echo.Context) error`. Task 7 dùng làm handler route.

- [ ] **Step 1: Tạo handler**

Tạo `backend/pkg/admin/handler/backfill_event_reward.go`:

```go
package handler

import (
	"time"

	"viewboost/internal/constants"
	echocustom "viewboost/internal/echo"
	"viewboost/pkg/admin/model/request"
	"viewboost/pkg/admin/service"

	"github.com/labstack/echo/v4"
)

// BackfillEventReward ...
type BackfillEventReward struct {
}

// Run quét content-analytic-daily theo event + khoảng thời gian, tạo event-reward
// còn thiếu qua luồng thật (đánh dấu fromMigration). Chạy nền, trả 200 ngay.
func (h BackfillEventReward) Run(c echo.Context) error {
	var (
		cc = echocustom.EchoGetCustomCtx(c)
		p  = cc.Get(constants.KeyPayload).(request.BackfillEventRewardBody)
	)

	var fromAt, toAt time.Time
	if p.FromAt != "" {
		fromAt, _ = time.Parse(time.RFC3339, p.FromAt)
	}
	if p.ToAt != "" {
		toAt, _ = time.Parse(time.RFC3339, p.ToAt)
	}

	go service.BackfillEventReward().Run(p.Event, fromAt, toAt, p.DryRun)
	return cc.Response200(echo.Map{
		"event":  p.Event,
		"fromAt": p.FromAt,
		"toAt":   p.ToAt,
		"dryRun": p.DryRun,
	}, "Backfill event-reward đã chạy nền")
}
```

- [ ] **Step 2: Verify compile**

Run: `cd backend && go build ./pkg/admin/handler/`
Expected: exit 0.

- [ ] **Step 3: Commit**

```bash
git add backend/pkg/admin/handler/backfill_event_reward.go
git commit -m "feat(backfill-event-reward): add handler"
```

---

### Task 7: Router (file riêng) + đăng ký

**Files:**
- Create: `backend/pkg/admin/router/backfill_event_reward.go`
- Modify: `backend/pkg/admin/router/router.go:44` (đăng ký group)

**Interfaces:**
- Consumes: `handler.BackfillEventReward` (Task 6), `routevalidation.BackfillEventReward` (Task 4), `routeauth.Auth()`.
- Produces: route `POST /api/admin/migration/backfill-event-reward`.

- [ ] **Step 1: Tạo file router**

Tạo `backend/pkg/admin/router/backfill_event_reward.go`:

```go
package router

import (
	"viewboost/pkg/admin/handler"
	"viewboost/pkg/admin/router/routeauth"
	"viewboost/pkg/admin/router/routevalidation"

	"github.com/labstack/echo/v4"
)

func backfillEventReward(e *echo.Group) {
	var (
		a = routeauth.Auth()
		g = e.Group("/migration/backfill-event-reward", a.RequiredLogin)
		h = handler.BackfillEventReward{}
		v = routevalidation.BackfillEventReward{}
	)

	g.POST("", h.Run, v.Body)
}
```

- [ ] **Step 2: Đăng ký group trong Init**

Trong `backend/pkg/admin/router/router.go`, thêm dòng ngay dưới `creatorProfile(adminGroup)` (dòng 44, trước `}`):

```go
	creatorProfile(adminGroup)
	backfillEventReward(adminGroup)
}
```

- [ ] **Step 3: Verify compile toàn repo + vet**

Run: `cd backend && go build ./... && go vet ./pkg/admin/...`
Expected: exit 0.

- [ ] **Step 4: Commit**

```bash
git add backend/pkg/admin/router/backfill_event_reward.go backend/pkg/admin/router/router.go
git commit -m "feat(backfill-event-reward): wire POST /migration/backfill-event-reward route"
```

---

### Task 8: Verify end-to-end (build + test + smoke)

**Files:** (không sửa)

- [ ] **Step 1: Build + vet + test toàn repo**

Run:
```bash
cd backend && go build ./... && go vet ./... && go test ./pkg/admin/model/request/ -run TestBackfillEventRewardBody_Validate -v
```
Expected: build & vet exit 0; test PASS.

- [ ] **Step 2: Smoke dry-run (môi trường có DB)**

Chạy admin service local, login lấy token:

```bash
curl -X POST "$ADMIN_HOST/api/admin/migration/backfill-event-reward" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"event":"<EVENT_ID_HEX>","fromAt":"2026-06-01T00:00:00Z","toAt":"2026-06-30T00:00:00Z","dryRun":true}'
```

Expected:
- HTTP 200, message "Backfill event-reward đã chạy nền".
- Log: `*** Start BackfillEventReward event=... (DRY-RUN)`, các dòng `[DRY-RUN] daily=...`, kết thúc `*** Finish ... — daily scanned: N, skipped...`.
- `event-rewards`: KHÔNG có document mới (dry-run).

- [ ] **Step 3: Kiểm chứng nhánh lỗi validate**

```bash
# thiếu body → 400 "Body bắt buộc..."
curl -X POST "$ADMIN_HOST/api/admin/migration/backfill-event-reward" -H "Authorization: Bearer $TOKEN"

# thiếu dryRun → 400 "Field dryRun bắt buộc..."
curl -X POST "$ADMIN_HOST/api/admin/migration/backfill-event-reward" -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"event":"665f1c2a3b4d5e6f7a8b9c0d"}'

# event sai định dạng → 400 validation (is.MongoID)
curl -X POST "$ADMIN_HOST/api/admin/migration/backfill-event-reward" -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"event":"abc","dryRun":true}'
```

- [ ] **Step 4: Chạy thật scope hẹp + kiểm idempotent**

Chạy `dryRun:false` trên 1 khoảng ngày hẹp:
```bash
curl -X POST "$ADMIN_HOST/api/admin/migration/backfill-event-reward" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"event":"<EVENT_ID_HEX>","fromAt":"2026-06-01T00:00:00Z","toAt":"2026-06-02T00:00:00Z","dryRun":false}'
```
Verify:
- `event-rewards` xuất hiện document mới của các content trong scope có `fromMigration:true`, `fromSystem:true`, cash/statistic đúng theo budget.
- Reward đã tồn tại từ trước KHÔNG bị đổi `fromMigration` (giữ nguyên, vì chỉ set ở INSERT).
- Chạy lại lần 2 cùng payload → không nhân bản reward (idempotent nhờ `findRewardPair`); reward hiện có chỉ được update statistic/cash nếu view thay đổi.

---

## Ghi chú review (self-review)

- **Spec coverage:** 1 API admin ✓ (Task 3-7, tách file riêng router/handler/service/validation/request); payload `{event, fromAt, toAt, dryRun}` ✓ (Task 3); check content-analytic-daily vs event-rewards + tạo cái thiếu ✓ — tái dùng luồng thật `UpdateRewardTypeByStatisticContent` đã idempotent qua `findRewardPair` (Task 5); flag đánh dấu từ migration ✓ (Task 1 + 2, set fromMigration ở INSERT). "tạo docs" = tạo **document** event_reward (đã xác nhận), không phải file tài liệu.
- **KHÔNG dùng temp:** bỏ hoàn toàn `event-reward-temps` — khác hẳn `CheckMissView`.
- **KHÔNG tự build reward:** dùng đúng pipeline production (budget BPE/BPU/BPC, primary/overflow) → không lệch logic tính tiền.
- **An toàn với luồng cũ:** flag chỉ luồn thêm 1 param; 3 caller cũ truyền `false`; UPDATE path không đụng field `fromMigration`.
- **Điểm review kỹ:** Task 2 đụng core reward — xác nhận `go build ./...` bắt hết caller `UpdateRewardTypeByStatisticContent` (đã liệt kê 3: event_schema.go:843, content_analytic_daily.go:158/461); xác nhận không set `fromMigration` ở UPDATE path (Step 2/3 chỉ sửa nhánh INSERT).
- **Rủi ro còn lại:** `WithBudgetLock` chạy tuần tự từng doc — migration scope rộng sẽ chậm; đó là lý do có `dryRun` để ước lượng khối lượng + nên chạy scope hẹp trước.
```
